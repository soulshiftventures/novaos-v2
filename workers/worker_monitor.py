"""
Worker Monitor - Resource tracking and cost monitoring
"""

import psutil
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


def safe_datetime_now() -> datetime:
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        return datetime(2025, 1, 1, 0, 0, 0)


@dataclass
class ResourceSnapshot:
    """Resource usage snapshot"""
    timestamp: datetime = field(default_factory=safe_datetime_now)
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    thread_count: int = 0


class WorkerMonitor:
    """
    Monitor worker resources and costs

    Features:
    - CPU/memory tracking
    - Cost monitoring per worker
    - ROI tracking
    - Alert generation
    """

    def __init__(self):
        """Initialize worker monitor"""
        self.resource_history: Dict[str, List[ResourceSnapshot]] = {}
        self.cost_alerts: List[Dict] = []
        self.max_history = 1000  # Keep last 1000 snapshots
        logger.info("WorkerMonitor initialized")

    def capture_resources(self, worker_id: str):
        """Capture resource snapshot for a worker"""
        try:
            process = psutil.Process()

            snapshot = ResourceSnapshot(
                timestamp=safe_datetime_now(),
                cpu_percent=process.cpu_percent(interval=0.1),
                memory_mb=process.memory_info().rss / 1024 / 1024,
                memory_percent=process.memory_percent(),
                thread_count=process.num_threads()
            )

            if worker_id not in self.resource_history:
                self.resource_history[worker_id] = []

            self.resource_history[worker_id].append(snapshot)

            # Trim history
            if len(self.resource_history[worker_id]) > self.max_history:
                self.resource_history[worker_id] = self.resource_history[worker_id][-self.max_history:]

        except Exception as e:
            logger.error(f"Error capturing resources for {worker_id}: {e}")

    def get_resource_stats(self, worker_id: str, period: timedelta = timedelta(hours=1)) -> Dict:
        """Get resource statistics for a worker"""
        if worker_id not in self.resource_history:
            return {
                'worker_id': worker_id,
                'period': str(period),
                'samples': 0,
                'cpu': {'avg': 0, 'max': 0, 'min': 0},
                'memory': {'avg': 0, 'max': 0, 'min': 0}
            }

        history = self.resource_history[worker_id]
        cutoff = safe_datetime_now() - period
        recent = [s for s in history if s.timestamp >= cutoff]

        if not recent:
            return {
                'worker_id': worker_id,
                'period': str(period),
                'samples': 0,
                'cpu': {'avg': 0, 'max': 0, 'min': 0},
                'memory': {'avg': 0, 'max': 0, 'min': 0}
            }

        cpu_values = [s.cpu_percent for s in recent]
        mem_values = [s.memory_mb for s in recent]

        return {
            'worker_id': worker_id,
            'period': str(period),
            'samples': len(recent),
            'cpu': {
                'avg': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'avg': sum(mem_values) / len(mem_values),
                'max': max(mem_values),
                'min': min(mem_values)
            }
        }

    def check_worker_costs(self, worker) -> List[Dict]:
        """Check if worker costs are concerning"""
        alerts = []

        # Check ROI
        if worker.metrics.total_runs > 10:  # Need some data
            roi = worker.metrics.roi

            if roi < 0:
                alerts.append({
                    'severity': 'CRITICAL',
                    'worker_id': worker.worker_id,
                    'type': 'negative_roi',
                    'message': f"Worker {worker.name} has negative ROI: {roi:.1f}%",
                    'recommendation': 'Consider pausing or killing this worker'
                })
            elif roi < 100:
                alerts.append({
                    'severity': 'WARNING',
                    'worker_id': worker.worker_id,
                    'type': 'low_roi',
                    'message': f"Worker {worker.name} has low ROI: {roi:.1f}%",
                    'recommendation': 'Monitor closely or optimize'
                })

        # Check budget limit
        if worker.budget_limit:
            percent_used = (worker.metrics.total_cost / worker.budget_limit) * 100

            if percent_used >= 100:
                alerts.append({
                    'severity': 'CRITICAL',
                    'worker_id': worker.worker_id,
                    'type': 'budget_exceeded',
                    'message': f"Worker {worker.name} exceeded budget limit",
                    'recommendation': 'Worker should be auto-paused'
                })
            elif percent_used >= 80:
                alerts.append({
                    'severity': 'WARNING',
                    'worker_id': worker.worker_id,
                    'type': 'budget_warning',
                    'message': f"Worker {worker.name} at {percent_used:.1f}% of budget",
                    'recommendation': 'Monitor spending'
                })

        # Check crash rate
        if worker.metrics.total_runs > 10:
            crash_rate = (worker.metrics.crash_count / worker.metrics.total_runs) * 100

            if crash_rate > 20:
                alerts.append({
                    'severity': 'CRITICAL',
                    'worker_id': worker.worker_id,
                    'type': 'high_crash_rate',
                    'message': f"Worker {worker.name} crash rate: {crash_rate:.1f}%",
                    'recommendation': 'Investigate and fix issues'
                })

        return alerts

    def check_all_workers(self, worker_manager) -> Dict:
        """Check all workers for cost/performance issues"""
        from .manager import get_worker_manager

        all_alerts = []

        for worker in worker_manager.workers.values():
            alerts = self.check_worker_costs(worker)
            all_alerts.extend(alerts)

        # Store alerts
        self.cost_alerts = all_alerts

        # Categorize by severity
        critical = [a for a in all_alerts if a['severity'] == 'CRITICAL']
        warnings = [a for a in all_alerts if a['severity'] == 'WARNING']

        return {
            'timestamp': safe_datetime_now().isoformat(),
            'total_alerts': len(all_alerts),
            'critical': len(critical),
            'warnings': len(warnings),
            'alerts': all_alerts
        }

    def get_cost_breakdown(self, worker_manager) -> Dict:
        """Get cost breakdown across all workers"""
        workers = worker_manager.workers.values()

        total_cost = sum(w.metrics.total_cost for w in workers)
        total_revenue = sum(w.metrics.total_revenue for w in workers)

        # Sort by cost
        by_cost = sorted(workers, key=lambda w: w.metrics.total_cost, reverse=True)

        breakdown = []
        for worker in by_cost:
            if worker.metrics.total_cost > 0:
                breakdown.append({
                    'worker_id': worker.worker_id,
                    'name': worker.name,
                    'cost': worker.metrics.total_cost,
                    'revenue': worker.metrics.total_revenue,
                    'profit': worker.metrics.profit,
                    'roi': worker.metrics.roi,
                    'percent_of_total': (worker.metrics.total_cost / total_cost * 100) if total_cost > 0 else 0
                })

        return {
            'timestamp': safe_datetime_now().isoformat(),
            'total_cost': total_cost,
            'total_revenue': total_revenue,
            'total_profit': total_revenue - total_cost,
            'overall_roi': ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0,
            'breakdown': breakdown
        }

    def get_top_performers(self, worker_manager, limit: int = 5) -> List[Dict]:
        """Get top performing workers by ROI"""
        workers = [w for w in worker_manager.workers.values() if w.metrics.total_runs > 5]

        # Sort by ROI
        sorted_workers = sorted(workers, key=lambda w: w.metrics.roi, reverse=True)

        return [{
            'worker_id': w.worker_id,
            'name': w.name,
            'roi': w.metrics.roi,
            'profit': w.metrics.profit,
            'revenue': w.metrics.total_revenue,
            'cost': w.metrics.total_cost,
            'runs': w.metrics.total_runs
        } for w in sorted_workers[:limit]]

    def get_bottom_performers(self, worker_manager, limit: int = 5) -> List[Dict]:
        """Get bottom performing workers by ROI"""
        workers = [w for w in worker_manager.workers.values() if w.metrics.total_runs > 5]

        # Sort by ROI ascending
        sorted_workers = sorted(workers, key=lambda w: w.metrics.roi)

        return [{
            'worker_id': w.worker_id,
            'name': w.name,
            'roi': w.metrics.roi,
            'profit': w.metrics.profit,
            'revenue': w.metrics.total_revenue,
            'cost': w.metrics.total_cost,
            'runs': w.metrics.total_runs
        } for w in sorted_workers[:limit]]

    def should_scale_up(self, worker) -> bool:
        """Determine if worker should be scaled up"""
        # Must have enough data
        if worker.metrics.total_runs < 20:
            return False

        # Must be healthy
        if not worker.is_healthy():
            return False

        # Must have high ROI
        if worker.metrics.roi < 300:  # 300% ROI threshold
            return False

        # Must have high success rate
        if worker.metrics.success_rate < 80:
            return False

        return True

    def should_scale_down(self, worker) -> bool:
        """Determine if worker should be scaled down"""
        # Must have enough data
        if worker.metrics.total_runs < 20:
            return False

        # Low ROI
        if worker.metrics.roi < 100:
            return True

        # High crash rate
        if worker.metrics.total_runs > 10:
            crash_rate = (worker.metrics.crash_count / worker.metrics.total_runs) * 100
            if crash_rate > 15:
                return True

        return False


# Global singleton
_monitor_instance = None


def get_worker_monitor() -> WorkerMonitor:
    """Get global worker monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = WorkerMonitor()
    return _monitor_instance
