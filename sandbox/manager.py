"""
NovaOS V2 Sandbox Manager
Isolated workspace for non-production experiments and prototyping
"""

import sqlite3
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid

from core.agent_factory import AgentFactory
from core.memory import NovaMemory
from config.settings import MODELS, DEFAULT_MODELS, EXECUTION_AGENT_BUDGET


class SandboxMemory(NovaMemory):
    """Isolated memory for sandbox - separate from production"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize sandbox database with same schema as production"""
        super()._initialize_db()

        # Add sandbox-specific tables
        cursor = self.conn.cursor()

        # Sandbox projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sandbox_projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                workspace_path TEXT,
                deployed_agents TEXT,
                results TEXT,
                evaluation TEXT,
                promoted_at TEXT
            )
        """)

        # Sandbox experiments table (for tracking specific experiments within projects)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sandbox_experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                hypothesis TEXT,
                config TEXT,
                results TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                success BOOLEAN,
                FOREIGN KEY (project_id) REFERENCES sandbox_projects(id)
            )
        """)

        self.conn.commit()


class SandboxProject:
    """Represents a single sandbox project with isolated workspace"""

    def __init__(self, project_id: str, name: str, description: str,
                 workspace_path: Path, memory: SandboxMemory):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.workspace_path = workspace_path
        self.memory = memory
        self.deployed_agents = []

    def get_metrics(self) -> Dict[str, Any]:
        """Get project metrics"""
        # Get all agents for this project
        agents = self.memory.get_all_agents(status=None)
        project_agents = [a for a in agents if a.get('id', '').startswith(f"sandbox_{self.project_id}")]

        total_cost = sum(a.get('total_cost', 0) for a in project_agents)
        total_revenue = sum(a.get('revenue_generated', 0) for a in project_agents)

        return {
            'project_id': self.project_id,
            'name': self.name,
            'total_agents': len(project_agents),
            'active_agents': len([a for a in project_agents if a.get('status') == 'active']),
            'total_cost': total_cost,
            'total_revenue': total_revenue,
            'profit': total_revenue - total_cost,
            'roi': ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
        }

    def deploy_agent(self, agent_type: str, name: str, config: Dict = None) -> str:
        """Deploy an agent in this sandbox project"""
        # Create unique agent ID for sandbox
        agent_id = f"sandbox_{self.project_id}_{agent_type}_{uuid.uuid4().hex[:6]}"

        # No budget constraints in sandbox (within reason)
        token_budget = config.get('token_budget', EXECUTION_AGENT_BUDGET * 10)  # 10x normal budget

        if config is None:
            config = {}

        # Add sandbox metadata
        config['sandbox_project'] = self.project_id
        config['sandbox_mode'] = True

        # Register in sandbox memory
        success = self.memory.register_agent(
            agent_id=agent_id,
            name=name,
            agent_type=agent_type,
            department="sandbox",  # All sandbox agents in "sandbox" department
            token_budget=token_budget,
            config=config
        )

        if not success:
            raise Exception(f"Failed to register sandbox agent {agent_id}")

        self.deployed_agents.append(agent_id)

        # Update project
        self._update_project_agents()

        return agent_id

    def _update_project_agents(self):
        """Update project's deployed agents list"""
        cursor = self.memory.conn.cursor()
        cursor.execute("""
            UPDATE sandbox_projects
            SET deployed_agents = ?
            WHERE id = ?
        """, (json.dumps(self.deployed_agents), self.project_id))
        self.memory.conn.commit()

    def list_agents(self) -> List[Dict]:
        """List all agents in this project"""
        agents = self.memory.get_all_agents(status=None)
        return [a for a in agents if a.get('id', '').startswith(f"sandbox_{self.project_id}")]

    def get_results(self) -> Dict[str, Any]:
        """Get project results for evaluation"""
        metrics = self.get_metrics()
        agents = self.list_agents()

        # Get all experiments
        cursor = self.memory.conn.cursor()
        cursor.execute("""
            SELECT * FROM sandbox_experiments
            WHERE project_id = ?
            ORDER BY started_at DESC
        """, (self.project_id,))
        experiments = [dict(row) for row in cursor.fetchall()]

        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'metrics': metrics,
            'agents': agents,
            'experiments': experiments,
            'workspace': str(self.workspace_path)
        }


class SandboxManager:
    """
    Sandbox Environment Manager

    Provides isolated workspace for:
    - Testing wild ideas without production impact
    - Personal passion projects
    - Learning new AI capabilities
    - Prototyping before committing resources

    Key Features:
    - Separate SQLite database (no production data contamination)
    - No budget constraints (within reason)
    - Project-based organization
    - Easy promotion to production
    """

    def __init__(self, sandbox_dir: str = "/Users/krissanders/novaos-v2/sandbox"):
        self.sandbox_dir = Path(sandbox_dir)
        self.projects_dir = self.sandbox_dir / "projects"
        self.db_path = self.sandbox_dir / "sandbox.db"

        # Ensure directories exist
        self.sandbox_dir.mkdir(exist_ok=True)
        self.projects_dir.mkdir(exist_ok=True)

        # Initialize sandbox memory
        self.memory = SandboxMemory(str(self.db_path))

    def create_project(self, name: str, description: str = None) -> str:
        """
        Create a new sandbox project

        Args:
            name: Project name
            description: Project description

        Returns:
            project_id: Unique project identifier
        """
        project_id = f"prj_{uuid.uuid4().hex[:8]}"
        workspace_path = self.projects_dir / project_id
        workspace_path.mkdir(exist_ok=True)

        # Create project record
        cursor = self.memory.conn.cursor()
        cursor.execute("""
            INSERT INTO sandbox_projects (id, name, description, status, created_at, workspace_path)
            VALUES (?, ?, ?, 'active', ?, ?)
        """, (project_id, name, description, safe_datetime_now().isoformat(), str(workspace_path)))
        self.memory.conn.commit()

        print(f"✓ Created sandbox project: {name}")
        print(f"  Project ID: {project_id}")
        print(f"  Workspace: {workspace_path}")

        return project_id

    def get_project(self, project_id: str) -> Optional[SandboxProject]:
        """Get a sandbox project"""
        cursor = self.memory.conn.cursor()
        cursor.execute("SELECT * FROM sandbox_projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()

        if not row:
            return None

        project_data = dict(row)

        # Load deployed agents
        deployed_agents_str = project_data.get('deployed_agents', '[]')
        if deployed_agents_str is None:
            deployed_agents = []
        else:
            deployed_agents = json.loads(deployed_agents_str)

        project = SandboxProject(
            project_id=project_data['id'],
            name=project_data['name'],
            description=project_data['description'],
            workspace_path=Path(project_data['workspace_path']),
            memory=self.memory
        )
        project.deployed_agents = deployed_agents

        return project

    def list_projects(self) -> List[Dict]:
        """List all sandbox projects"""
        cursor = self.memory.conn.cursor()
        cursor.execute("""
            SELECT id, name, description, status, created_at
            FROM sandbox_projects
            ORDER BY created_at DESC
        """)

        projects = []
        for row in cursor.fetchall():
            project_data = dict(row)

            # Get project metrics
            project = self.get_project(project_data['id'])
            if project:
                metrics = project.get_metrics()
                project_data['metrics'] = metrics

            projects.append(project_data)

        return projects

    def deploy_agent(self, project_id: str, agent_type: str, config: Dict = None) -> str:
        """
        Deploy an agent in a sandbox project

        Args:
            project_id: Project to deploy to
            agent_type: Type of agent
            config: Agent configuration

        Returns:
            agent_id: Deployed agent ID
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        name = config.get('name', f"{agent_type}-sandbox")
        agent_id = project.deploy_agent(agent_type, name, config)

        print(f"✓ Deployed {agent_type} agent in sandbox project: {project.name}")
        print(f"  Agent ID: {agent_id}")
        print(f"  Note: This is a sandbox agent (no production impact)")

        return agent_id

    def log_experiment(self, project_id: str, name: str, hypothesis: str,
                      config: Dict = None) -> int:
        """Log an experiment within a project"""
        cursor = self.memory.conn.cursor()
        cursor.execute("""
            INSERT INTO sandbox_experiments (project_id, name, hypothesis, config, started_at)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, name, hypothesis, json.dumps(config) if config else None,
              safe_datetime_now().isoformat()))
        self.memory.conn.commit()

        experiment_id = cursor.lastrowid

        print(f"✓ Started experiment: {name}")
        print(f"  Experiment ID: {experiment_id}")
        print(f"  Hypothesis: {hypothesis}")

        return experiment_id

    def complete_experiment(self, experiment_id: int, results: Dict, success: bool):
        """Mark experiment as complete with results"""
        cursor = self.memory.conn.cursor()
        cursor.execute("""
            UPDATE sandbox_experiments
            SET results = ?, completed_at = ?, success = ?
            WHERE id = ?
        """, (json.dumps(results), safe_datetime_now().isoformat(), success, experiment_id))
        self.memory.conn.commit()

        print(f"✓ Experiment {experiment_id} completed")
        print(f"  Success: {success}")

    def evaluate_project(self, project_id: str, use_council: bool = False) -> Dict[str, Any]:
        """
        Evaluate if a sandbox project should be promoted to production

        Args:
            project_id: Project to evaluate
            use_council: If True, use R&D Council for deep analysis (costs ~$0.50)
                        If False, use quick metrics-based evaluation (free)

        Returns evaluation with recommendation
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        results = project.get_results()
        metrics = results['metrics']

        # Evaluation criteria
        basic_evaluation = {
            'project_id': project_id,
            'project_name': project.name,
            'evaluated_at': safe_datetime_now().isoformat(),
            'metrics': metrics,
            'criteria': {}
        }

        # Check if has positive ROI
        has_positive_roi = metrics['roi'] > 0
        basic_evaluation['criteria']['positive_roi'] = {
            'pass': has_positive_roi,
            'value': metrics['roi'],
            'threshold': 0
        }

        # Check if profitable
        is_profitable = metrics['profit'] > 0
        basic_evaluation['criteria']['profitable'] = {
            'pass': is_profitable,
            'value': metrics['profit'],
            'threshold': 0
        }

        # Check if has active agents
        has_active_agents = metrics['active_agents'] > 0
        basic_evaluation['criteria']['has_active_agents'] = {
            'pass': has_active_agents,
            'value': metrics['active_agents'],
            'threshold': 1
        }

        # Check if has sufficient data (at least some cost incurred = testing happened)
        has_data = metrics['total_cost'] > 0
        basic_evaluation['criteria']['has_sufficient_data'] = {
            'pass': has_data,
            'value': metrics['total_cost'],
            'threshold': 0
        }

        # Overall recommendation
        all_pass = all(c['pass'] for c in basic_evaluation['criteria'].values())

        if all_pass and metrics['roi'] > 300:
            recommendation = "STRONGLY_RECOMMEND"
            reason = f"Excellent ROI ({metrics['roi']:.1f}%) and all criteria passed"
        elif all_pass:
            recommendation = "RECOMMEND"
            reason = f"Positive ROI ({metrics['roi']:.1f}%) and all criteria passed"
        elif has_positive_roi and has_data:
            recommendation = "CONSIDER"
            reason = "Positive results but some criteria not met"
        else:
            recommendation = "NOT_READY"
            reason = "Not meeting promotion criteria"

        basic_evaluation['recommendation'] = recommendation
        basic_evaluation['reason'] = reason

        # Use R&D Council for enhanced evaluation if requested
        if use_council:
            from sandbox.evaluator import get_evaluator
            evaluator = get_evaluator()
            evaluation = evaluator.evaluate_project(project, basic_evaluation)
        else:
            from sandbox.evaluator import get_evaluator
            evaluator = get_evaluator()
            evaluation = evaluator.quick_evaluate(project, basic_evaluation)

        # Save evaluation to project
        cursor = self.memory.conn.cursor()
        cursor.execute("""
            UPDATE sandbox_projects
            SET evaluation = ?, results = ?
            WHERE id = ?
        """, (json.dumps(evaluation), json.dumps(results), project_id))
        self.memory.conn.commit()

        return evaluation

    def promote_project(self, project_id: str, production_memory_path: str = None) -> Dict[str, Any]:
        """
        Promote a sandbox project to production

        This migrates successful agents and configurations to production NovaOS

        Args:
            project_id: Project to promote
            production_memory_path: Path to production database (default: novaos.db)

        Returns:
            Migration results
        """
        if production_memory_path is None:
            production_memory_path = "/Users/krissanders/novaos-v2/data/novaos.db"

        # Evaluate first
        evaluation = self.evaluate_project(project_id)

        if evaluation['recommendation'] == 'NOT_READY':
            print("⚠ Warning: Project evaluation recommends NOT promoting")
            print(f"  Reason: {evaluation['reason']}")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                return {'status': 'cancelled', 'reason': 'User cancelled'}

        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        print(f"\n=== Promoting Project to Production ===")
        print(f"Project: {project.name}")
        print(f"ID: {project_id}")

        # Get production memory
        from core.memory import NovaMemory


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return datetime.now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)

        prod_memory = NovaMemory(production_memory_path)

        # Migrate agents
        agents = project.list_agents()
        migrated_agents = []

        for agent in agents:
            # Only migrate active/successful agents
            if agent.get('status') not in ['active', 'paused']:
                continue

            # Only migrate profitable agents
            if agent.get('roi', 0) < 0:
                continue

            # Create new production agent ID (remove sandbox prefix)
            original_type = agent['type']
            prod_agent_id = f"{original_type}_{uuid.uuid4().hex[:8]}"

            # Parse config
            config = json.loads(agent.get('config', '{}')) if agent.get('config') else {}

            # Remove sandbox metadata
            config.pop('sandbox_project', None)
            config.pop('sandbox_mode', None)

            # Determine department from config or default to operations
            department = config.get('department', 'operations')

            # Register in production
            success = prod_memory.register_agent(
                agent_id=prod_agent_id,
                name=agent['name'].replace('-sandbox', ''),
                agent_type=original_type,
                department=department,
                token_budget=agent.get('token_budget'),
                config=config
            )

            if success:
                migrated_agents.append({
                    'sandbox_id': agent['id'],
                    'production_id': prod_agent_id,
                    'name': agent['name'],
                    'type': original_type,
                    'roi': agent.get('roi', 0)
                })
                print(f"✓ Migrated: {agent['name']}")
                print(f"  Sandbox ID: {agent['id']}")
                print(f"  Production ID: {prod_agent_id}")

        # Mark project as promoted
        cursor = self.memory.conn.cursor()
        cursor.execute("""
            UPDATE sandbox_projects
            SET status = 'promoted', promoted_at = ?
            WHERE id = ?
        """, (safe_datetime_now().isoformat(), project_id))
        self.memory.conn.commit()

        result = {
            'status': 'success',
            'project_id': project_id,
            'project_name': project.name,
            'agents_migrated': len(migrated_agents),
            'migrated_agents': migrated_agents,
            'evaluation': evaluation
        }

        print(f"\n✓ Project promoted to production")
        print(f"  Agents migrated: {len(migrated_agents)}")

        return result

    def kill_project(self, project_id: str, delete_workspace: bool = False) -> bool:
        """
        Delete a sandbox project

        Args:
            project_id: Project to delete
            delete_workspace: If True, delete workspace directory

        Returns:
            Success status
        """
        project = self.get_project(project_id)
        if not project:
            print(f"Project {project_id} not found")
            return False

        print(f"Killing sandbox project: {project.name}")

        # Kill all agents in project
        agents = project.list_agents()
        for agent in agents:
            self.memory.update_agent_status(agent['id'], 'killed')
            print(f"  ✓ Killed agent: {agent['name']}")

        # Delete workspace if requested
        if delete_workspace and project.workspace_path.exists():
            shutil.rmtree(project.workspace_path)
            print(f"  ✓ Deleted workspace: {project.workspace_path}")

        # Mark project as deleted
        cursor = self.memory.conn.cursor()
        cursor.execute("""
            UPDATE sandbox_projects
            SET status = 'deleted'
            WHERE id = ?
        """, (project_id,))
        self.memory.conn.commit()

        print(f"✓ Project {project.name} killed")

        return True

    def get_summary(self) -> Dict[str, Any]:
        """Get sandbox environment summary"""
        projects = self.list_projects()

        active_projects = [p for p in projects if p['status'] == 'active']
        promoted_projects = [p for p in projects if p['status'] == 'promoted']

        total_cost = sum(p.get('metrics', {}).get('total_cost', 0) for p in projects)
        total_agents = sum(p.get('metrics', {}).get('total_agents', 0) for p in active_projects)

        return {
            'total_projects': len(projects),
            'active_projects': len(active_projects),
            'promoted_projects': len(promoted_projects),
            'total_agents': total_agents,
            'total_cost': total_cost,
            'projects': projects
        }


# Singleton instance
_sandbox_instance = None

def get_sandbox() -> SandboxManager:
    """Get or create sandbox manager instance"""
    global _sandbox_instance
    if _sandbox_instance is None:
        _sandbox_instance = SandboxManager()
    return _sandbox_instance
