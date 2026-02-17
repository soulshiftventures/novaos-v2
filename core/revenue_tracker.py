"""
Revenue Tracker - Real-time revenue attribution and tracking

Tracks revenue from multiple sources and attributes it to specific agents
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


@dataclass
class RevenueEvent:
    """Single revenue event"""
    event_id: str
    timestamp: datetime
    amount: float
    source: str  # stripe, gumroad, manual, etc.
    agent_id: Optional[str] = None
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class RevenueTracker:
    """
    Revenue tracking and attribution system

    Features:
    - Track revenue from multiple sources
    - Attribute revenue to specific agents
    - Calculate per-agent profitability
    - Real-time cash flow tracking
    - Auto-reinvestment logic
    """

    def __init__(self):
        """Initialize revenue tracker"""
        self.events: List[RevenueEvent] = []
        self.agent_revenue: Dict[str, float] = {}
        self.source_revenue: Dict[str, float] = {}
        self.total_revenue = 0.0
        self.total_costs = 0.0
        self.reinvestment_rate = 0.7  # Reinvest 70% of profits

        logger.info("RevenueTracker initialized")

    def track_event(
        self,
        amount: float,
        source: str,
        agent_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        product_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> RevenueEvent:
        """
        Track a revenue event

        Args:
            amount: Revenue amount
            source: Revenue source (stripe, gumroad, etc.)
            agent_id: Agent responsible for revenue
            customer_id: Customer identifier
            product_id: Product identifier
            metadata: Additional metadata

        Returns:
            Created revenue event
        """
        event_id = f"rev_{datetime.now().timestamp()}_{len(self.events)}"

        event = RevenueEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            amount=amount,
            source=source,
            agent_id=agent_id,
            customer_id=customer_id,
            product_id=product_id,
            metadata=metadata or {}
        )

        self.events.append(event)
        self.total_revenue += amount

        # Update agent attribution
        if agent_id:
            if agent_id not in self.agent_revenue:
                self.agent_revenue[agent_id] = 0.0
            self.agent_revenue[agent_id] += amount

        # Update source tracking
        if source not in self.source_revenue:
            self.source_revenue[source] = 0.0
        self.source_revenue[source] += amount

        logger.info(f"Revenue tracked: ${amount:.2f} from {source} (agent: {agent_id})")
        return event

    def track_cost(
        self,
        amount: float,
        agent_id: Optional[str] = None,
        category: str = "ai_cost"
    ):
        """
        Track a cost

        Args:
            amount: Cost amount
            agent_id: Agent incurring cost
            category: Cost category
        """
        self.total_costs += amount
        logger.debug(f"Cost tracked: ${amount:.2f} ({category}, agent: {agent_id})")

    def get_agent_attribution(self, agent_id: str) -> Dict:
        """
        Get revenue attribution for an agent

        Args:
            agent_id: Agent ID

        Returns:
            Revenue attribution summary
        """
        revenue = self.agent_revenue.get(agent_id, 0.0)

        # Get all events for this agent
        agent_events = [e for e in self.events if e.agent_id == agent_id]

        # Calculate by source
        by_source = {}
        for event in agent_events:
            if event.source not in by_source:
                by_source[event.source] = 0.0
            by_source[event.source] += event.amount

        return {
            'agent_id': agent_id,
            'total_revenue': revenue,
            'event_count': len(agent_events),
            'by_source': by_source,
            'first_revenue': agent_events[0].timestamp.isoformat() if agent_events else None,
            'last_revenue': agent_events[-1].timestamp.isoformat() if agent_events else None
        }

    def get_source_breakdown(self) -> Dict:
        """Get revenue breakdown by source"""
        sources = []

        for source, amount in self.source_revenue.items():
            events = [e for e in self.events if e.source == source]

            sources.append({
                'source': source,
                'total_revenue': amount,
                'event_count': len(events),
                'percent_of_total': (amount / self.total_revenue * 100) if self.total_revenue > 0 else 0
            })

        # Sort by revenue
        sources.sort(key=lambda x: x['total_revenue'], reverse=True)

        return {
            'total_revenue': self.total_revenue,
            'sources': sources
        }

    def get_profitability(self, agent_id: Optional[str] = None) -> Dict:
        """
        Calculate profitability

        Args:
            agent_id: Specific agent (or None for overall)

        Returns:
            Profitability metrics
        """
        if agent_id:
            revenue = self.agent_revenue.get(agent_id, 0.0)
            # Would need to track per-agent costs separately
            cost = 0.0  # Placeholder
        else:
            revenue = self.total_revenue
            cost = self.total_costs

        profit = revenue - cost
        roi = ((revenue - cost) / cost * 100) if cost > 0 else 0

        return {
            'revenue': revenue,
            'cost': cost,
            'profit': profit,
            'roi': roi,
            'margin': (profit / revenue * 100) if revenue > 0 else 0
        }

    def get_cash_flow(self, period: timedelta = timedelta(days=30)) -> Dict:
        """
        Get cash flow for period

        Args:
            period: Time period to analyze

        Returns:
            Cash flow summary
        """
        cutoff = datetime.now() - period
        recent_events = [e for e in self.events if e.timestamp >= cutoff]

        # Group by day
        daily_revenue = {}
        for event in recent_events:
            day = event.timestamp.date()
            if day not in daily_revenue:
                daily_revenue[day] = 0.0
            daily_revenue[day] += event.amount

        # Calculate metrics
        total_period_revenue = sum(daily_revenue.values())
        days_with_revenue = len(daily_revenue)
        avg_daily_revenue = total_period_revenue / days_with_revenue if days_with_revenue > 0 else 0

        return {
            'period_days': period.days,
            'total_revenue': total_period_revenue,
            'days_with_revenue': days_with_revenue,
            'avg_daily_revenue': avg_daily_revenue,
            'daily_breakdown': {
                str(day): amount
                for day, amount in sorted(daily_revenue.items())
            }
        }

    def calculate_reinvestment(self) -> Dict:
        """
        Calculate available budget for reinvestment

        Returns:
            Reinvestment calculations
        """
        profit = self.total_revenue - self.total_costs
        reinvestment_amount = profit * self.reinvestment_rate

        return {
            'total_profit': profit,
            'reinvestment_rate': self.reinvestment_rate,
            'available_for_reinvestment': reinvestment_amount,
            'reserved_for_withdraw': profit - reinvestment_amount
        }

    def get_top_performers(self, limit: int = 5) -> List[Dict]:
        """
        Get top revenue-generating agents

        Args:
            limit: Number of agents to return

        Returns:
            List of top performers
        """
        performers = [
            {
                'agent_id': agent_id,
                'revenue': revenue,
                'percent_of_total': (revenue / self.total_revenue * 100) if self.total_revenue > 0 else 0
            }
            for agent_id, revenue in self.agent_revenue.items()
        ]

        performers.sort(key=lambda x: x['revenue'], reverse=True)
        return performers[:limit]

    def get_revenue_timeline(self, hours: int = 24) -> List[Dict]:
        """
        Get revenue timeline for last N hours

        Args:
            hours: Number of hours to look back

        Returns:
            Hourly revenue data
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_events = [e for e in self.events if e.timestamp >= cutoff]

        # Group by hour
        hourly_revenue = {}
        for event in recent_events:
            hour = event.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour not in hourly_revenue:
                hourly_revenue[hour] = {
                    'timestamp': hour.isoformat(),
                    'revenue': 0.0,
                    'events': 0
                }
            hourly_revenue[hour]['revenue'] += event.amount
            hourly_revenue[hour]['events'] += 1

        return sorted(hourly_revenue.values(), key=lambda x: x['timestamp'])

    def export_data(self, filepath: str):
        """
        Export revenue data to JSON file

        Args:
            filepath: Path to output file
        """
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_revenue': self.total_revenue,
            'total_costs': self.total_costs,
            'total_profit': self.total_revenue - self.total_costs,
            'events': [
                {
                    'event_id': e.event_id,
                    'timestamp': e.timestamp.isoformat(),
                    'amount': e.amount,
                    'source': e.source,
                    'agent_id': e.agent_id,
                    'customer_id': e.customer_id,
                    'product_id': e.product_id,
                    'metadata': e.metadata
                }
                for e in self.events
            ],
            'agent_revenue': self.agent_revenue,
            'source_revenue': self.source_revenue
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Revenue data exported to {filepath}")

    def get_summary(self) -> Dict:
        """Get complete revenue summary"""
        profitability = self.get_profitability()
        reinvestment = self.calculate_reinvestment()
        cash_flow = self.get_cash_flow(timedelta(days=30))

        return {
            'timestamp': datetime.now().isoformat(),
            'totals': {
                'revenue': self.total_revenue,
                'costs': self.total_costs,
                'profit': profitability['profit'],
                'roi': profitability['roi']
            },
            'events': {
                'total': len(self.events),
                'by_source': self.source_revenue,
                'by_agent': len(self.agent_revenue)
            },
            'cash_flow': cash_flow,
            'reinvestment': reinvestment,
            'top_performers': self.get_top_performers(5)
        }


# Global singleton
_tracker_instance = None


def get_revenue_tracker() -> RevenueTracker:
    """Get global revenue tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = RevenueTracker()
    return _tracker_instance
