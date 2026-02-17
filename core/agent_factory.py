"""
NovaOS V2 Agent Factory
Dynamic agent deployment and management
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from core.memory import get_memory
from config.settings import (
    EXECUTION_AGENT_BUDGET, DEFAULT_AGENT_CONFIG,
    AUTO_OPTIMIZE_TRIGGERS
)


class AgentFactory:
    """Factory for deploying and managing execution agents"""

    def __init__(self):
        self.memory = get_memory()

    def deploy_agent(self, agent_type: str, name: str, department: str,
                    config: Dict = None, token_budget: int = None) -> str:
        """Deploy a new execution agent"""

        # Generate unique agent ID
        agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"

        # Set defaults
        if token_budget is None:
            token_budget = EXECUTION_AGENT_BUDGET

        if config is None:
            config = {}

        # Merge with defaults
        agent_config = {**DEFAULT_AGENT_CONFIG, **config}

        # Register agent in memory
        success = self.memory.register_agent(
            agent_id=agent_id,
            name=name,
            agent_type=agent_type,
            department=department,
            token_budget=token_budget,
            config=agent_config
        )

        if not success:
            raise Exception(f"Failed to register agent {agent_id}")

        print(f"✓ Deployed {name} ({agent_type}) in {department} department")
        print(f"  Agent ID: {agent_id}")
        print(f"  Token Budget: {token_budget}")

        return agent_id

    def pause_agent(self, agent_id: str) -> bool:
        """Pause an agent"""
        self.memory.update_agent_status(agent_id, "paused")
        agent = self.memory.get_agent(agent_id)
        if agent:
            print(f"⏸ Paused agent: {agent['name']} ({agent_id})")
            return True
        return False

    def resume_agent(self, agent_id: str) -> bool:
        """Resume a paused agent"""
        self.memory.update_agent_status(agent_id, "active")
        agent = self.memory.get_agent(agent_id)
        if agent:
            print(f"▶ Resumed agent: {agent['name']} ({agent_id})")
            return True
        return False

    def kill_agent(self, agent_id: str) -> bool:
        """Kill (permanently stop) an agent"""
        self.memory.update_agent_status(agent_id, "killed")
        agent = self.memory.get_agent(agent_id)
        if agent:
            print(f"⨯ Killed agent: {agent['name']} ({agent_id})")
            print(f"  Final stats: Cost ${agent.get('total_cost', 0):.2f}, "
                  f"Revenue ${agent.get('revenue_generated', 0):.2f}, "
                  f"ROI {agent.get('roi', 0):.1f}%")
            return True
        return False

    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Get detailed agent status"""
        agent = self.memory.get_agent(agent_id)

        if not agent:
            return None

        # Calculate performance metrics
        roi = agent.get('roi', 0)
        profit = agent.get('revenue_generated', 0) - agent.get('total_cost', 0)

        # Performance rating
        if roi >= 500:
            performance = "EXCELLENT"
        elif roi >= 300:
            performance = "GOOD"
        elif roi >= 100:
            performance = "FAIR"
        elif roi >= 0:
            performance = "POOR"
        else:
            performance = "NEGATIVE"

        return {
            "agent_id": agent['id'],
            "name": agent['name'],
            "type": agent['type'],
            "department": agent['department'],
            "status": agent['status'],
            "deployed_at": agent['deployed_at'],
            "last_active": agent.get('last_active'),
            "metrics": {
                "tokens_used": agent.get('tokens_used', 0),
                "token_budget": agent.get('token_budget', 0),
                "budget_used_percent": (agent.get('tokens_used', 0) / agent.get('token_budget', 1) * 100),
                "total_cost": agent.get('total_cost', 0),
                "revenue_generated": agent.get('revenue_generated', 0),
                "profit": profit,
                "roi": roi,
                "performance": performance
            },
            "config": json.loads(agent.get('config', '{}')) if agent.get('config') else {}
        }

    def list_agents(self, status: str = None, department: str = None) -> List[Dict]:
        """List all agents with optional filters"""
        agents = self.memory.get_all_agents(status=status, department=department)

        return [{
            "agent_id": a['id'],
            "name": a['name'],
            "type": a['type'],
            "department": a['department'],
            "status": a['status'],
            "cost": a.get('total_cost', 0),
            "revenue": a.get('revenue_generated', 0),
            "roi": a.get('roi', 0)
        } for a in agents]

    def auto_optimize_agents(self) -> Dict[str, Any]:
        """Automatically optimize agents based on performance"""

        actions_taken = []
        cost_saved = 0.0

        # Get all active agents
        active_agents = self.memory.get_all_agents(status="active")

        for agent in active_agents:
            agent_id = agent['id']
            roi = agent.get('roi', 0)
            cost = agent.get('total_cost', 0)

            # Check if agent should be paused (negative ROI trigger)
            if roi < -10:  # Less than -10% ROI
                # Check how long it's been negative
                # For now, pause immediately if very negative
                if roi < -50:
                    self.pause_agent(agent_id)
                    actions_taken.append({
                        "agent_id": agent_id,
                        "agent_name": agent['name'],
                        "action": "PAUSED",
                        "reason": f"Very negative ROI: {roi:.1f}%",
                        "cost_saved": cost * 0.5  # Estimate 50% cost savings
                    })
                    cost_saved += cost * 0.5

        # Get cost breakdown
        memory = get_memory()
        total_revenue = memory.get_total_revenue()
        total_costs = memory.get_total_costs()

        # Check if AI costs exceed threshold
        if total_revenue > 0:
            cost_percent = (total_costs / total_revenue) * 100

            if cost_percent > AUTO_OPTIMIZE_TRIGGERS["cost_percent_exceeded"]:
                # Find most expensive agents to review
                expensive = sorted(active_agents, key=lambda x: x.get('total_cost', 0), reverse=True)[:3]

                for agent in expensive:
                    if agent.get('roi', 0) < 200:  # Less than 200% ROI
                        actions_taken.append({
                            "agent_id": agent['id'],
                            "agent_name": agent['name'],
                            "action": "REVIEW_RECOMMENDED",
                            "reason": f"High cost ${agent.get('total_cost', 0):.2f}, low ROI {agent.get('roi', 0):.1f}%"
                        })

        return {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": len(actions_taken),
            "details": actions_taken,
            "estimated_cost_saved": cost_saved,
            "current_cost_percent": (total_costs / total_revenue * 100) if total_revenue > 0 else 0
        }


class AgentTemplates:
    """Pre-configured agent templates for common tasks"""

    @staticmethod
    def dds_prospecting(vertical: str, location: str, count: int = 50, budget: float = 50) -> Dict:
        """DDS prospecting agent config"""
        return {
            "agent_type": "dds_prospecting",
            "name": f"DDS-{vertical}-{location}",
            "department": "sales",
            "config": {
                "vertical": vertical,
                "location": location,
                "prospect_count": count,
                "budget": budget,
                "integration_path": "/Users/krissanders/prospecting_agent"
            }
        }

    @staticmethod
    def content_creator(platform: str, topic: str, frequency: str = "daily") -> Dict:
        """Content creation agent config"""
        return {
            "agent_type": "content_creator",
            "name": f"Content-{platform}-{topic}",
            "department": "marketing",
            "config": {
                "platform": platform,
                "topic": topic,
                "frequency": frequency,
                "auto_post": False
            }
        }

    @staticmethod
    def trend_monitor(topic: str, sources: List[str] = None) -> Dict:
        """Trend monitoring agent config"""
        if sources is None:
            sources = ["twitter", "reddit", "news"]

        return {
            "agent_type": "trend_monitor",
            "name": f"TrendMonitor-{topic}",
            "department": "research",
            "config": {
                "topic": topic,
                "sources": sources,
                "check_interval": 3600,  # 1 hour
                "alert_threshold": 0.7  # Alert on 70% confidence
            }
        }

    @staticmethod
    def seo_optimizer(website: str, keywords: List[str]) -> Dict:
        """SEO optimization agent config"""
        return {
            "agent_type": "seo_optimizer",
            "name": f"SEO-{website}",
            "department": "marketing",
            "config": {
                "website": website,
                "keywords": keywords,
                "check_interval": 86400,  # Daily
                "auto_optimize": True
            }
        }

    @staticmethod
    def system_monitor(target: str = "all") -> Dict:
        """System monitoring agent config"""
        return {
            "agent_type": "system_monitor",
            "name": f"Monitor-{target}",
            "department": "operations",
            "config": {
                "target": target,
                "check_interval": 300,  # 5 minutes
                "alert_on_issues": True
            }
        }


# Singleton instance
_factory_instance = None

def get_factory() -> AgentFactory:
    """Get or create factory instance"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = AgentFactory()
    return _factory_instance
