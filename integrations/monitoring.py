"""
NovaOS V2 Monitoring & Cost Tracking
Real-time cost tracking, performance monitoring, and optimization alerts
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from core.memory import get_memory
from config.financial_targets import (
    get_current_target, is_on_track, calculate_roi,
    ALERT_THRESHOLDS, get_current_month
)
from config.settings import MAX_AI_COST_PERCENT, ALERT_AI_COST_PERCENT


class CostMonitor:
    """Real-time AI cost monitoring and optimization"""

    def __init__(self):
        self.memory = get_memory()

    def get_cost_dashboard(self, period: str = "today") -> Dict[str, Any]:
        """Get comprehensive cost dashboard"""

        # Get financial data
        total_revenue = self.memory.get_total_revenue()
        total_costs = self.memory.get_total_costs()
        cost_breakdown = self.memory.get_cost_breakdown(period)
        roi_by_dept = self.memory.get_roi_by_department()

        # Get targets
        targets = get_current_target()

        # Calculate metrics
        ai_cost_percent = (total_costs / total_revenue * 100) if total_revenue > 0 else 0
        net_profit = total_revenue - total_costs
        overall_roi = calculate_roi(total_revenue, total_costs)

        # Check status
        status = self._determine_cost_status(ai_cost_percent)

        # Get most expensive agents
        agents = self.memory.get_all_agents(status="active")
        expensive_agents = sorted(
            agents,
            key=lambda x: x.get('total_cost', 0),
            reverse=True
        )[:5]

        return {
            "timestamp": datetime.now().isoformat(),
            "period": period,
            "summary": {
                "total_revenue": total_revenue,
                "total_ai_costs": total_costs,
                "net_profit": net_profit,
                "ai_cost_percent": ai_cost_percent,
                "overall_roi": overall_roi,
                "status": status
            },
            "targets": {
                "revenue_target": targets['revenue_target'],
                "ai_budget": targets['ai_budget'],
                "daily_revenue_target": targets['daily_revenue_target'],
                "daily_ai_budget": targets['daily_ai_budget']
            },
            "cost_breakdown": cost_breakdown,
            "department_roi": roi_by_dept,
            "most_expensive_agents": [{
                "id": a['id'],
                "name": a['name'],
                "department": a['department'],
                "cost": a.get('total_cost', 0),
                "revenue": a.get('revenue_generated', 0),
                "roi": a.get('roi', 0)
            } for a in expensive_agents],
            "alerts": self._generate_cost_alerts(ai_cost_percent, total_revenue, total_costs)
        }

    def _determine_cost_status(self, ai_cost_percent: float) -> str:
        """Determine cost health status"""
        if ai_cost_percent <= MAX_AI_COST_PERCENT:
            return "HEALTHY"
        elif ai_cost_percent <= ALERT_AI_COST_PERCENT:
            return "WARNING"
        else:
            return "CRITICAL"

    def _generate_cost_alerts(self, ai_cost_percent: float,
                            total_revenue: float, total_costs: float) -> List[Dict]:
        """Generate cost-related alerts"""
        alerts = []

        # AI cost percentage alerts
        if ai_cost_percent > ALERT_AI_COST_PERCENT:
            alerts.append({
                "severity": "CRITICAL",
                "type": "cost_percent_exceeded",
                "message": f"AI costs at {ai_cost_percent:.1f}% of revenue (target: <{MAX_AI_COST_PERCENT}%)",
                "action": "Immediately optimize agent usage"
            })
        elif ai_cost_percent > MAX_AI_COST_PERCENT:
            alerts.append({
                "severity": "WARNING",
                "type": "cost_percent_high",
                "message": f"AI costs at {ai_cost_percent:.1f}% of revenue (target: <{MAX_AI_COST_PERCENT}%)",
                "action": "Review and optimize agent deployment"
            })

        # Negative ROI alert
        if total_revenue > 0 and (total_revenue - total_costs) < 0:
            alerts.append({
                "severity": "CRITICAL",
                "type": "negative_profit",
                "message": f"Negative profit: ${total_revenue - total_costs:.2f}",
                "action": "Reduce costs or accelerate revenue"
            })

        # Check for negative ROI agents
        agents = self.memory.get_all_agents(status="active")
        negative_agents = [a for a in agents if a.get('roi', 0) < -10]

        if negative_agents:
            alerts.append({
                "severity": "WARNING",
                "type": "negative_roi_agents",
                "message": f"{len(negative_agents)} agents have negative ROI",
                "action": "Review and pause underperforming agents",
                "agents": [a['id'] for a in negative_agents]
            })

        return alerts

    def track_api_call(self, agent_id: str, model: str, operation: str,
                      input_tokens: int, output_tokens: int, cost: float) -> int:
        """Track a single API call (called by agents)"""
        agent = self.memory.get_agent(agent_id)

        return self.memory.log_api_cost(
            model=model,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            agent_id=agent_id,
            agent_name=agent.get('name') if agent else None,
            department=agent.get('department') if agent else None
        )

    def get_cost_projection(self, days: int = 30) -> Dict[str, Any]:
        """Project costs based on current usage patterns"""

        # Get recent costs (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_costs = self.memory.get_total_costs(start_date=week_ago)

        # Calculate daily average
        daily_avg = recent_costs / 7

        # Project
        projected_costs = daily_avg * days

        # Get revenue
        recent_revenue = self.memory.get_total_revenue(start_date=week_ago)
        daily_revenue_avg = recent_revenue / 7
        projected_revenue = daily_revenue_avg * days

        # Calculate projected metrics
        projected_profit = projected_revenue - projected_costs
        projected_cost_percent = (projected_costs / projected_revenue * 100) if projected_revenue > 0 else 0

        # Determine if sustainable
        sustainable = projected_cost_percent <= MAX_AI_COST_PERCENT

        return {
            "period_days": days,
            "current_daily_cost": daily_avg,
            "current_daily_revenue": daily_revenue_avg,
            "projected_costs": projected_costs,
            "projected_revenue": projected_revenue,
            "projected_profit": projected_profit,
            "projected_cost_percent": projected_cost_percent,
            "sustainable": sustainable,
            "warning": "Unsustainable cost trajectory" if not sustainable else None
        }


class PerformanceMonitor:
    """Agent and system performance monitoring"""

    def __init__(self):
        self.memory = get_memory()

    def get_system_overview(self) -> Dict[str, Any]:
        """Get complete system performance overview"""

        # Get all agents
        all_agents = self.memory.get_all_agents()
        active_agents = [a for a in all_agents if a['status'] == 'active']

        # Calculate performance metrics
        high_performers = [a for a in active_agents if a.get('roi', 0) >= 300]
        low_performers = [a for a in active_agents if a.get('roi', 0) < 100 and a.get('roi', 0) >= 0]
        negative_performers = [a for a in active_agents if a.get('roi', 0) < 0]

        # Financial metrics
        total_revenue = self.memory.get_total_revenue()
        total_costs = self.memory.get_total_costs()

        # Targets
        month = get_current_month()
        day = datetime.now().day
        tracking = is_on_track(total_revenue, month, day)

        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": self._calculate_system_health(
                len(high_performers),
                len(low_performers),
                len(negative_performers),
                tracking['on_track']
            ),
            "agents": {
                "total": len(all_agents),
                "active": len(active_agents),
                "paused": len([a for a in all_agents if a['status'] == 'paused']),
                "killed": len([a for a in all_agents if a['status'] == 'killed']),
                "high_performers": len(high_performers),
                "low_performers": len(low_performers),
                "negative_performers": len(negative_performers)
            },
            "financials": {
                "total_revenue": total_revenue,
                "total_costs": total_costs,
                "profit": total_revenue - total_costs,
                "roi": calculate_roi(total_revenue, total_costs),
                "ai_cost_percent": (total_costs / total_revenue * 100) if total_revenue > 0 else 0
            },
            "targets": {
                "on_track": tracking['on_track'],
                "status": tracking['status'],
                "monthly_target": tracking['monthly_target'],
                "current_revenue": total_revenue,
                "percent_of_expected": tracking['percent_of_expected']
            },
            "recommendations": self._generate_system_recommendations(
                high_performers, low_performers, negative_performers, tracking
            )
        }

    def _calculate_system_health(self, high: int, low: int, negative: int,
                                on_track: bool) -> str:
        """Calculate overall system health"""
        total = high + low + negative

        if total == 0:
            return "NO_AGENTS"

        high_percent = (high / total) * 100

        if high_percent >= 60 and on_track:
            return "EXCELLENT"
        elif high_percent >= 40 and on_track:
            return "GOOD"
        elif high_percent >= 20:
            return "FAIR"
        else:
            return "POOR"

    def _generate_system_recommendations(self, high_performers: List,
                                       low_performers: List,
                                       negative_performers: List,
                                       tracking: Dict) -> List[str]:
        """Generate system-level recommendations"""
        recommendations = []

        # Revenue tracking
        if not tracking['on_track']:
            if tracking['status'] == 'behind':
                recommendations.append(
                    f"Behind revenue target - accelerate deployment or optimize conversion"
                )
            recommendations.append(
                f"Need ${tracking['monthly_target'] - tracking['current_revenue']:.0f} "
                f"more to hit monthly target"
            )

        # Agent performance
        if negative_performers:
            recommendations.append(
                f"Pause or kill {len(negative_performers)} negative ROI agents"
            )

        if low_performers and len(low_performers) > len(high_performers):
            recommendations.append(
                "Majority of agents underperforming - review deployment strategy"
            )

        if not high_performers:
            recommendations.append(
                "No high-performing agents - urgent optimization needed"
            )

        # Scaling recommendations
        if high_performers and len(high_performers) >= 3:
            recommendations.append(
                f"Scale successful patterns from {len(high_performers)} high performers"
            )

        return recommendations


class RevenueTracker:
    """Revenue tracking and optimization"""

    def __init__(self):
        self.memory = get_memory()

    def get_revenue_dashboard(self) -> Dict[str, Any]:
        """Get revenue tracking dashboard"""

        # Get revenue data
        total_revenue = self.memory.get_total_revenue()

        # Get by department
        roi_by_dept = self.memory.get_roi_by_department()

        # Get targets
        month = get_current_month()
        day = datetime.now().day
        tracking = is_on_track(total_revenue, month, day)
        targets = get_current_target()

        # Calculate runway
        total_costs = self.memory.get_total_costs()
        net_profit = total_revenue - total_costs

        return {
            "timestamp": datetime.now().isoformat(),
            "total_revenue": total_revenue,
            "monthly_target": targets['revenue_target'],
            "daily_target": targets['daily_revenue_target'],
            "tracking": tracking,
            "department_breakdown": {
                dept: data['revenue']
                for dept, data in roi_by_dept.items()
            },
            "top_revenue_generators": self._get_top_agents_by_revenue(),
            "profit": net_profit,
            "burn_rate": total_costs,
            "recommendations": self._generate_revenue_recommendations(tracking, roi_by_dept)
        }

    def _get_top_agents_by_revenue(self, limit: int = 5) -> List[Dict]:
        """Get top revenue-generating agents"""
        agents = self.memory.get_all_agents(status="active")
        sorted_agents = sorted(
            agents,
            key=lambda x: x.get('revenue_generated', 0),
            reverse=True
        )[:limit]

        return [{
            "id": a['id'],
            "name": a['name'],
            "department": a['department'],
            "revenue": a.get('revenue_generated', 0),
            "cost": a.get('total_cost', 0),
            "roi": a.get('roi', 0)
        } for a in sorted_agents]

    def _generate_revenue_recommendations(self, tracking: Dict,
                                         roi_by_dept: Dict) -> List[str]:
        """Generate revenue optimization recommendations"""
        recommendations = []

        # Check tracking
        if tracking['status'] == 'behind':
            recommendations.append(
                f"Urgently need ${tracking['expected_revenue'] - tracking['current_revenue']:.0f} "
                f"to get back on track"
            )

        # Check department performance
        for dept, data in roi_by_dept.items():
            if data['revenue'] < 100 and dept != 'operations':  # Operations is cost center
                recommendations.append(
                    f"{dept.title()} department generating low revenue (${data['revenue']:.2f}) "
                    f"- deploy more agents or optimize"
                )

        return recommendations


# === MONITORING FACADE ===

class Monitor:
    """Unified monitoring interface"""

    def __init__(self):
        self.cost_monitor = CostMonitor()
        self.performance_monitor = PerformanceMonitor()
        self.revenue_tracker = RevenueTracker()

    def status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "system": self.performance_monitor.get_system_overview(),
            "costs": self.cost_monitor.get_cost_dashboard("today"),
            "revenue": self.revenue_tracker.get_revenue_dashboard()
        }

    def costs(self, period: str = "today") -> Dict[str, Any]:
        """Get cost dashboard"""
        return self.cost_monitor.get_cost_dashboard(period)

    def revenue(self) -> Dict[str, Any]:
        """Get revenue dashboard"""
        return self.revenue_tracker.get_revenue_dashboard()

    def project_costs(self, days: int = 30) -> Dict[str, Any]:
        """Project costs"""
        return self.cost_monitor.get_cost_projection(days)


# Singleton
_monitor_instance = None

def get_monitor() -> Monitor:
    """Get or create monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = Monitor()
    return _monitor_instance
