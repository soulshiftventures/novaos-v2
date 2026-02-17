"""
NovaOS V2 Departments
Tactical department managers that deploy and manage execution agents
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from core.memory import get_memory
from config.settings import DEPARTMENT_CONFIGS, DEPARTMENT_BUDGETS
from config.financial_targets import get_department_target, get_current_month


class Department:
    """Base class for department managers"""

    def __init__(self, name: str):
        self.name = name
        self.config = DEPARTMENT_CONFIGS.get(name, {})
        self.token_budget = DEPARTMENT_BUDGETS.get(name, 1000)
        self.memory = get_memory()
        self.department_id = f"dept_{name.lower()}"

    def get_agents(self) -> List[Dict]:
        """Get all agents in this department"""
        return self.memory.get_all_agents(department=self.name)

    def get_metrics(self) -> Dict[str, Any]:
        """Get department metrics"""
        agents = self.get_agents()

        total_cost = sum(a.get('total_cost', 0) for a in agents)
        total_revenue = sum(a.get('revenue_generated', 0) for a in agents)
        total_tokens = sum(a.get('tokens_used', 0) for a in agents)

        roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0

        month = get_current_month()
        target = get_department_target(month, self.name)

        return {
            "department": self.name,
            "active_agents": len([a for a in agents if a['status'] == 'active']),
            "total_agents": len(agents),
            "total_cost": total_cost,
            "total_revenue": total_revenue,
            "total_tokens": total_tokens,
            "roi": roi,
            "monthly_target": target,
            "target_progress": (total_revenue / target * 100) if target > 0 else 0
        }

    def get_status(self) -> Dict[str, Any]:
        """Get department status"""
        metrics = self.get_metrics()
        agents = self.get_agents()

        # Identify problem agents
        negative_roi_agents = [a for a in agents if a.get('roi', 0) < 0 and a['status'] == 'active']

        return {
            "department": self.name,
            "status": "active",
            "metrics": metrics,
            "problem_agents": len(negative_roi_agents),
            "recommendations": self._get_recommendations(metrics, negative_roi_agents)
        }

    def _get_recommendations(self, metrics: Dict, problem_agents: List) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []

        # Check ROI
        if metrics['roi'] < 100:
            recommendations.append(f"ROI below 100% - optimize or reduce agent deployment")

        # Check problem agents
        if problem_agents:
            recommendations.append(f"Review {len(problem_agents)} negative ROI agents for pause/kill")

        # Check target progress
        if metrics['target_progress'] < 50:
            recommendations.append(f"Behind revenue target - need acceleration")

        return recommendations


class SalesDepartment(Department):
    """Sales Department - Owns DDS prospecting system"""

    def __init__(self):
        super().__init__("sales")

    def deploy_dds(self, config: Dict) -> Dict[str, Any]:
        """Deploy DDS prospecting agents"""
        from core.agent_factory import get_factory

        factory = get_factory()

        # Deploy DDS agents
        agent_id = factory.deploy_agent(
            agent_type="dds_prospecting",
            name=f"DDS-{config.get('vertical', 'default')}",
            department="sales",
            config=config
        )

        return {
            "status": "deployed",
            "agent_id": agent_id,
            "department": "sales",
            "config": config
        }

    def get_dds_status(self) -> Dict[str, Any]:
        """Get DDS agent statuses"""
        agents = [a for a in self.get_agents() if 'dds' in a['type'].lower()]

        return {
            "total_dds_agents": len(agents),
            "active": len([a for a in agents if a['status'] == 'active']),
            "total_cost": sum(a.get('total_cost', 0) for a in agents),
            "total_revenue": sum(a.get('revenue_generated', 0) for a in agents),
            "agents": agents
        }


class MarketingDepartment(Department):
    """Marketing Department - Content, SEO, social media"""

    def __init__(self):
        super().__init__("marketing")

    def deploy_content_agent(self, config: Dict) -> Dict[str, Any]:
        """Deploy content creation agent"""
        from core.agent_factory import get_factory

        factory = get_factory()

        agent_id = factory.deploy_agent(
            agent_type="content_creator",
            name=f"Content-{config.get('platform', 'default')}",
            department="marketing",
            config=config
        )

        return {
            "status": "deployed",
            "agent_id": agent_id,
            "department": "marketing",
            "config": config
        }

    def deploy_seo_agent(self, config: Dict) -> Dict[str, Any]:
        """Deploy SEO optimization agent"""
        from core.agent_factory import get_factory

        factory = get_factory()

        agent_id = factory.deploy_agent(
            agent_type="seo_optimizer",
            name=f"SEO-{config.get('focus', 'default')}",
            department="marketing",
            config=config
        )

        return {
            "status": "deployed",
            "agent_id": agent_id,
            "department": "marketing",
            "config": config
        }


class ProductDepartment(Department):
    """Product Department - Digital product creation, SaaS building"""

    def __init__(self):
        super().__init__("product")

    def deploy_builder_agent(self, config: Dict) -> Dict[str, Any]:
        """Deploy product builder agent"""
        from core.agent_factory import get_factory

        factory = get_factory()

        agent_id = factory.deploy_agent(
            agent_type="product_builder",
            name=f"Builder-{config.get('product_type', 'default')}",
            department="product",
            config=config
        )

        return {
            "status": "deployed",
            "agent_id": agent_id,
            "department": "product",
            "config": config
        }


class OperationsDepartment(Department):
    """Operations Department - Infrastructure, monitoring, optimization"""

    def __init__(self):
        super().__init__("operations")

    def deploy_monitor_agent(self, config: Dict) -> Dict[str, Any]:
        """Deploy monitoring agent"""
        from core.agent_factory import get_factory

        factory = get_factory()

        agent_id = factory.deploy_agent(
            agent_type="system_monitor",
            name=f"Monitor-{config.get('target', 'default')}",
            department="operations",
            config=config
        )

        return {
            "status": "deployed",
            "agent_id": agent_id,
            "department": "operations",
            "config": config
        }

    def run_optimization(self) -> Dict[str, Any]:
        """Run system-wide optimization"""

        # Get all agents across all departments
        all_agents = self.memory.get_all_agents()

        optimizations = []

        # Find negative ROI agents
        negative_roi = [a for a in all_agents if a.get('roi', 0) < -10 and a['status'] == 'active']

        for agent in negative_roi:
            # Recommend pause
            optimizations.append({
                "agent_id": agent['id'],
                "agent_name": agent['name'],
                "action": "PAUSE",
                "reason": f"Negative ROI: {agent.get('roi', 0):.1f}%",
                "cost_saved": agent.get('total_cost', 0)
            })

        # Find high-cost, low-return agents
        high_cost = sorted([a for a in all_agents if a['status'] == 'active'],
                          key=lambda x: x.get('total_cost', 0), reverse=True)[:5]

        for agent in high_cost:
            if agent.get('roi', 0) < 200:  # Less than 200% ROI
                optimizations.append({
                    "agent_id": agent['id'],
                    "agent_name": agent['name'],
                    "action": "REVIEW",
                    "reason": f"High cost (${agent.get('total_cost', 0):.2f}), low ROI ({agent.get('roi', 0):.1f}%)",
                    "potential_savings": agent.get('total_cost', 0) * 0.5
                })

        return {
            "timestamp": safe_datetime_now().isoformat(),
            "optimizations_found": len(optimizations),
            "recommendations": optimizations,
            "potential_cost_savings": sum(o.get('cost_saved', 0) + o.get('potential_savings', 0)
                                        for o in optimizations)
        }


class ResearchDepartment(Department):
    """Research Department - R&D Expert Council, opportunity analysis"""

    def __init__(self):
        super().__init__("research")

    def deploy_analyst_agent(self, config: Dict) -> Dict[str, Any]:
        """Deploy research analyst agent"""
        from core.agent_factory import get_factory

        factory = get_factory()

        agent_id = factory.deploy_agent(
            agent_type="research_analyst",
            name=f"Analyst-{config.get('focus', 'default')}",
            department="research",
            config=config
        )

        return {
            "status": "deployed",
            "agent_id": agent_id,
            "department": "research",
            "config": config
        }

    def deploy_trend_monitor(self, config: Dict) -> Dict[str, Any]:
        """Deploy trend monitoring agent"""
        from core.agent_factory import get_factory

        factory = get_factory()

        agent_id = factory.deploy_agent(
            agent_type="trend_monitor",
            name=f"TrendMonitor-{config.get('topic', 'default')}",
            department="research",
            config=config
        )

        return {
            "status": "deployed",
            "agent_id": agent_id,
            "department": "research",
            "config": config
        }

    def run_council_session(self, question: str) -> Dict[str, Any]:
        """Run R&D Expert Council session"""
        from agents.council.expert_council import get_council


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return datetime.now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)


        council = get_council()
        result = council.analyze(question)

        return result


# === DEPARTMENT REGISTRY ===

class DepartmentRegistry:
    """Central registry for all departments"""

    def __init__(self):
        self.sales = SalesDepartment()
        self.marketing = MarketingDepartment()
        self.product = ProductDepartment()
        self.operations = OperationsDepartment()
        self.research = ResearchDepartment()

        self.departments = {
            "sales": self.sales,
            "marketing": self.marketing,
            "product": self.product,
            "operations": self.operations,
            "research": self.research
        }

    def get_department(self, name: str) -> Optional[Department]:
        """Get department by name"""
        return self.departments.get(name.lower())

    def get_all_statuses(self) -> Dict[str, Any]:
        """Get status of all departments"""
        return {
            name: dept.get_status()
            for name, dept in self.departments.items()
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all departments"""
        return {
            name: dept.get_metrics()
            for name, dept in self.departments.items()
        }


# Singleton instance
_registry_instance = None

def get_departments() -> DepartmentRegistry:
    """Get or create department registry"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = DepartmentRegistry()
    return _registry_instance
