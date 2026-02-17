"""
Autonomous Decision Engine - AI-driven agent management

Makes autonomous decisions about:
- Deploying new agents
- Scaling successful agents
- Killing underperforming agents
- Budget allocation
- ROI optimization
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)


logger = logging.getLogger(__name__)


@dataclass
class AutonDecision:
    """Represents an autonomous decision"""
    timestamp: datetime
    decision_type: str  # deploy, scale, kill, pause, optimize
    target: str  # worker_id or worker_type
    reason: str
    expected_roi: float
    cost_impact: float
    confidence: float  # 0.0 - 1.0
    requires_approval: bool
    metadata: Dict


class AutonomousEngine:
    """
    Autonomous decision-making engine for NovaOS

    Features:
    - ROI-based decision making
    - Auto-deploy profitable agents
    - Auto-kill unprofitable agents
    - Auto-scale successful agents
    - Budget management
    - Risk assessment
    """

    def __init__(
        self,
        enabled: bool = False,
        max_daily_budget: float = 100.0,
        min_roi_threshold: float = 150.0,  # 150% ROI minimum
        scale_roi_threshold: float = 300.0,  # 300% ROI to trigger scaling
        kill_roi_threshold: float = 0.0,  # Negative ROI triggers kill
        require_approval_above: float = 50.0,  # Require approval for decisions > $50
        min_data_points: int = 20  # Minimum runs before making decisions
    ):
        """
        Initialize autonomous engine

        Args:
            enabled: Enable autonomous mode
            max_daily_budget: Maximum daily spend
            min_roi_threshold: Minimum ROI to keep agents alive
            scale_roi_threshold: ROI threshold to trigger scaling
            kill_roi_threshold: ROI threshold to trigger killing
            require_approval_above: Cost threshold requiring human approval
            min_data_points: Minimum data points before decisions
        """
        self.enabled = enabled
        self.max_daily_budget = max_daily_budget
        self.min_roi_threshold = min_roi_threshold
        self.scale_roi_threshold = scale_roi_threshold
        self.kill_roi_threshold = kill_roi_threshold
        self.require_approval_above = require_approval_above
        self.min_data_points = min_data_points

        self.decisions: List[AutonDecision] = []
        self.pending_approvals: List[AutonDecision] = []
        self.budget_spent_today = 0.0
        self.last_budget_reset = safe_datetime_now().date()

        logger.info(f"AutonomousEngine initialized (enabled: {enabled})")

    def enable(self):
        """Enable autonomous mode"""
        self.enabled = True
        logger.info("Autonomous mode ENABLED")

    def disable(self):
        """Disable autonomous mode"""
        self.enabled = False
        logger.info("Autonomous mode DISABLED")

    def _reset_daily_budget_if_needed(self):
        """Reset daily budget at midnight"""
        today = safe_datetime_now().date()
        if today > self.last_budget_reset:
            logger.info(f"Resetting daily budget (spent: ${self.budget_spent_today:.2f})")
            self.budget_spent_today = 0.0
            self.last_budget_reset = today

    def _has_budget_available(self, amount: float) -> bool:
        """Check if budget is available for decision"""
        self._reset_daily_budget_if_needed()
        return (self.budget_spent_today + amount) <= self.max_daily_budget

    def _record_decision(self, decision: AutonDecision):
        """Record a decision"""
        self.decisions.append(decision)

        if decision.requires_approval:
            self.pending_approvals.append(decision)
            logger.info(f"Decision requires approval: {decision.decision_type} {decision.target}")
        else:
            logger.info(f"Autonomous decision: {decision.decision_type} {decision.target}")

    def analyze_worker(self, worker, worker_monitor) -> Dict:
        """
        Analyze a worker and generate recommendations

        Args:
            worker: Worker instance
            worker_monitor: WorkerMonitor instance

        Returns:
            Analysis with recommendations
        """
        metrics = worker.metrics

        # Need minimum data
        if metrics.total_runs < self.min_data_points:
            return {
                'worker_id': worker.worker_id,
                'status': 'insufficient_data',
                'recommendation': 'collect_more_data',
                'roi': metrics.roi,
                'runs': metrics.total_runs,
                'min_required': self.min_data_points
            }

        roi = metrics.roi
        profit = metrics.profit
        success_rate = metrics.success_rate

        # Determine status
        if roi >= self.scale_roi_threshold and success_rate >= 80:
            status = 'excellent'
            recommendation = 'scale_up'
        elif roi >= self.min_roi_threshold and success_rate >= 70:
            status = 'good'
            recommendation = 'maintain'
        elif roi >= self.kill_roi_threshold:
            status = 'poor'
            recommendation = 'optimize_or_pause'
        else:
            status = 'failing'
            recommendation = 'kill'

        # Check if scaling makes sense
        can_scale = worker_monitor.should_scale_up(worker)
        should_kill = worker_monitor.should_scale_down(worker) or roi < self.kill_roi_threshold

        if should_kill:
            recommendation = 'kill'
        elif can_scale:
            recommendation = 'scale_up'

        return {
            'worker_id': worker.worker_id,
            'name': worker.name,
            'status': status,
            'recommendation': recommendation,
            'metrics': {
                'roi': roi,
                'profit': profit,
                'revenue': metrics.total_revenue,
                'cost': metrics.total_cost,
                'runs': metrics.total_runs,
                'success_rate': success_rate
            },
            'can_scale': can_scale,
            'should_kill': should_kill
        }

    def decide_scale_up(
        self,
        worker,
        analysis: Dict,
        multiplier: int = 2
    ) -> Optional[AutonDecision]:
        """
        Decide whether to scale up a worker

        Args:
            worker: Worker instance
            analysis: Worker analysis
            multiplier: Scale multiplier

        Returns:
            Decision or None
        """
        if not self.enabled:
            return None

        if analysis['recommendation'] != 'scale_up':
            return None

        # Estimate cost impact
        avg_cost_per_run = worker.metrics.total_cost / worker.metrics.total_runs
        estimated_daily_runs = (24 * 3600) / worker.run_interval
        estimated_daily_cost = avg_cost_per_run * estimated_daily_runs * (multiplier - 1)

        # Check budget
        if not self._has_budget_available(estimated_daily_cost):
            logger.warning(f"Insufficient budget to scale {worker.worker_id}")
            return None

        # Calculate confidence based on data quality
        confidence = min(worker.metrics.total_runs / 100, 1.0)  # Max confidence at 100 runs

        requires_approval = estimated_daily_cost > self.require_approval_above

        decision = AutonDecision(
            timestamp=safe_datetime_now(),
            decision_type='scale_up',
            target=worker.worker_id,
            reason=f"High ROI ({analysis['metrics']['roi']:.1f}%) and success rate ({analysis['metrics']['success_rate']:.1f}%)",
            expected_roi=analysis['metrics']['roi'],
            cost_impact=estimated_daily_cost,
            confidence=confidence,
            requires_approval=requires_approval,
            metadata={
                'multiplier': multiplier,
                'current_instances': 1,
                'new_instances': multiplier
            }
        )

        self._record_decision(decision)
        return decision

    def decide_kill(
        self,
        worker,
        analysis: Dict
    ) -> Optional[AutonDecision]:
        """
        Decide whether to kill a worker

        Args:
            worker: Worker instance
            analysis: Worker analysis

        Returns:
            Decision or None
        """
        if not self.enabled:
            return None

        if analysis['recommendation'] != 'kill':
            return None

        # Calculate potential savings
        avg_cost_per_run = worker.metrics.total_cost / worker.metrics.total_runs
        estimated_daily_runs = (24 * 3600) / worker.run_interval
        estimated_daily_savings = avg_cost_per_run * estimated_daily_runs

        confidence = min(worker.metrics.total_runs / 100, 1.0)

        # Killing negative ROI doesn't require approval
        requires_approval = analysis['metrics']['roi'] > 0

        decision = AutonDecision(
            timestamp=safe_datetime_now(),
            decision_type='kill',
            target=worker.worker_id,
            reason=f"Low ROI ({analysis['metrics']['roi']:.1f}%) - unprofitable",
            expected_roi=analysis['metrics']['roi'],
            cost_impact=-estimated_daily_savings,  # Negative = savings
            confidence=confidence,
            requires_approval=requires_approval,
            metadata={
                'current_profit': analysis['metrics']['profit'],
                'total_cost': analysis['metrics']['cost']
            }
        )

        self._record_decision(decision)
        return decision

    def decide_deploy_new(
        self,
        worker_type: str,
        expected_roi: float,
        estimated_daily_cost: float,
        reason: str
    ) -> Optional[AutonDecision]:
        """
        Decide whether to deploy a new agent type

        Args:
            worker_type: Type of worker to deploy
            expected_roi: Expected ROI
            estimated_daily_cost: Estimated daily cost
            reason: Reason for deployment

        Returns:
            Decision or None
        """
        if not self.enabled:
            return None

        # Check if ROI meets threshold
        if expected_roi < self.min_roi_threshold:
            logger.info(f"Expected ROI ({expected_roi:.1f}%) below threshold ({self.min_roi_threshold:.1f}%)")
            return None

        # Check budget
        if not self._has_budget_available(estimated_daily_cost):
            logger.warning(f"Insufficient budget to deploy {worker_type}")
            return None

        requires_approval = estimated_daily_cost > self.require_approval_above

        decision = AutonDecision(
            timestamp=safe_datetime_now(),
            decision_type='deploy',
            target=worker_type,
            reason=reason,
            expected_roi=expected_roi,
            cost_impact=estimated_daily_cost,
            confidence=0.5,  # Lower confidence for new deployments
            requires_approval=requires_approval,
            metadata={
                'worker_type': worker_type
            }
        )

        self._record_decision(decision)
        return decision

    def execute_decision(
        self,
        decision: AutonDecision,
        worker_manager
    ) -> bool:
        """
        Execute an autonomous decision

        Args:
            decision: Decision to execute
            worker_manager: WorkerManager instance

        Returns:
            True if executed successfully
        """
        if not self.enabled:
            logger.warning("Cannot execute decision: autonomous mode disabled")
            return False

        if decision.requires_approval and decision in self.pending_approvals:
            logger.warning("Cannot execute decision: requires approval")
            return False

        try:
            if decision.decision_type == 'scale_up':
                worker_manager.scale_worker(
                    decision.target,
                    decision.metadata['multiplier']
                )
                logger.info(f"Executed scale_up for {decision.target}")

            elif decision.decision_type == 'kill':
                worker_manager.kill_worker(decision.target)
                logger.info(f"Executed kill for {decision.target}")

            elif decision.decision_type == 'deploy':
                # Would need to implement deployment logic
                logger.info(f"Executed deploy for {decision.target}")

            elif decision.decision_type == 'pause':
                worker_manager.pause_worker(decision.target)
                logger.info(f"Executed pause for {decision.target}")

            # Update budget
            if decision.cost_impact > 0:
                self.budget_spent_today += decision.cost_impact

            # Remove from pending approvals
            if decision in self.pending_approvals:
                self.pending_approvals.remove(decision)

            return True

        except Exception as e:
            logger.error(f"Error executing decision: {e}")
            return False

    def approve_decision(self, decision: AutonDecision) -> bool:
        """
        Approve a pending decision

        Args:
            decision: Decision to approve

        Returns:
            True if approved
        """
        if decision in self.pending_approvals:
            self.pending_approvals.remove(decision)
            decision.requires_approval = False
            logger.info(f"Approved decision: {decision.decision_type} {decision.target}")
            return True

        return False

    def run_analysis_cycle(self, worker_manager, worker_monitor) -> Dict:
        """
        Run complete analysis cycle on all workers

        Args:
            worker_manager: WorkerManager instance
            worker_monitor: WorkerMonitor instance

        Returns:
            Analysis summary
        """
        logger.info("Running autonomous analysis cycle")

        analyses = []
        decisions_made = []

        for worker in worker_manager.workers.values():
            # Analyze worker
            analysis = self.analyze_worker(worker, worker_monitor)
            analyses.append(analysis)

            if not self.enabled:
                continue  # Just analyze, don't make decisions

            # Make decisions based on analysis
            if analysis.get('recommendation') == 'scale_up':
                decision = self.decide_scale_up(worker, analysis)
                if decision:
                    decisions_made.append(decision)

                    # Auto-execute if no approval needed
                    if not decision.requires_approval:
                        self.execute_decision(decision, worker_manager)

            elif analysis.get('recommendation') == 'kill':
                decision = self.decide_kill(worker, analysis)
                if decision:
                    decisions_made.append(decision)

                    # Auto-execute if no approval needed
                    if not decision.requires_approval:
                        self.execute_decision(decision, worker_manager)

        return {
            'timestamp': safe_datetime_now().isoformat(),
            'enabled': self.enabled,
            'analyses': analyses,
            'decisions_made': len(decisions_made),
            'pending_approvals': len(self.pending_approvals),
            'budget_spent_today': self.budget_spent_today,
            'budget_remaining': self.max_daily_budget - self.budget_spent_today,
            'decisions': [
                {
                    'type': d.decision_type,
                    'target': d.target,
                    'reason': d.reason,
                    'expected_roi': d.expected_roi,
                    'cost_impact': d.cost_impact,
                    'requires_approval': d.requires_approval
                }
                for d in decisions_made
            ]
        }

    def get_status(self) -> Dict:
        """Get autonomous engine status"""
        return {
            'enabled': self.enabled,
            'config': {
                'max_daily_budget': self.max_daily_budget,
                'min_roi_threshold': self.min_roi_threshold,
                'scale_roi_threshold': self.scale_roi_threshold,
                'kill_roi_threshold': self.kill_roi_threshold,
                'require_approval_above': self.require_approval_above
            },
            'budget': {
                'spent_today': self.budget_spent_today,
                'remaining': self.max_daily_budget - self.budget_spent_today,
                'percent_used': (self.budget_spent_today / self.max_daily_budget * 100) if self.max_daily_budget > 0 else 0
            },
            'decisions': {
                'total': len(self.decisions),
                'today': len([d for d in self.decisions if d.timestamp.date() == safe_datetime_now().date()]),
                'pending_approvals': len(self.pending_approvals)
            },
            'pending_approvals': [
                {
                    'type': d.decision_type,
                    'target': d.target,
                    'reason': d.reason,
                    'expected_roi': d.expected_roi,
                    'cost_impact': d.cost_impact,
                    'timestamp': d.timestamp.isoformat()
                }
                for d in self.pending_approvals
            ]
        }


# Global singleton
_autonomous_instance = None


def get_autonomous_engine() -> AutonomousEngine:
    """Get global autonomous engine instance"""
    global _autonomous_instance
    if _autonomous_instance is None:
        _autonomous_instance = AutonomousEngine()
    return _autonomous_instance
