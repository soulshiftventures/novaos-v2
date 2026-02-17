"""
Base Worker - Foundation for 24/7 background agents
"""

import time
import threading
import logging
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import traceback

logger = logging.getLogger(__name__)


def safe_datetime_now() -> datetime:
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        # Fallback to fixed date if system time causes overflow
        return datetime(2025, 1, 1, 0, 0, 0)


class WorkerStatus(Enum):
    """Worker lifecycle states"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    CRASHED = "crashed"


@dataclass
class WorkerMetrics:
    """Runtime metrics for a worker"""
    start_time: datetime = field(default_factory=safe_datetime_now)
    last_heartbeat: datetime = field(default_factory=safe_datetime_now)
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_revenue: float = 0.0
    total_cost: float = 0.0
    crash_count: int = 0
    restart_count: int = 0

    @property
    def uptime(self) -> timedelta:
        """Calculate uptime"""
        return safe_datetime_now() - self.start_time

    @property
    def roi(self) -> float:
        """Calculate ROI percentage"""
        if self.total_cost == 0:
            return 0.0
        return ((self.total_revenue - self.total_cost) / self.total_cost) * 100

    @property
    def profit(self) -> float:
        """Calculate profit"""
        return self.total_revenue - self.total_cost

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_runs == 0:
            return 0.0
        return (self.successful_runs / self.total_runs) * 100


class BaseWorker:
    """
    Base worker for 24/7 background agent execution

    Features:
    - Auto-restart on failure
    - Resource monitoring
    - Cost tracking
    - ROI calculation
    - Heartbeat monitoring
    - Configurable run intervals
    """

    def __init__(
        self,
        worker_id: str,
        name: str,
        run_interval: int = 60,
        max_crash_count: int = 5,
        crash_cooldown: int = 300,
        budget_limit: Optional[float] = None,
        auto_restart: bool = True
    ):
        """
        Initialize worker

        Args:
            worker_id: Unique worker identifier
            name: Human-readable name
            run_interval: Seconds between runs (default: 60)
            max_crash_count: Max crashes before stopping (default: 5)
            crash_cooldown: Seconds to wait after crash (default: 300)
            budget_limit: Max cost before auto-pause
            auto_restart: Auto-restart on failure
        """
        self.worker_id = worker_id
        self.name = name
        self.run_interval = run_interval
        self.max_crash_count = max_crash_count
        self.crash_cooldown = crash_cooldown
        self.budget_limit = budget_limit
        self.auto_restart = auto_restart

        self.status = WorkerStatus.INITIALIZING
        self.metrics = WorkerMetrics()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

        self.config: Dict[str, Any] = {}
        self.last_error: Optional[str] = None

        logger.info(f"Worker {self.worker_id} initialized: {self.name}")

    def start(self):
        """Start the worker in background thread"""
        if self._thread and self._thread.is_alive():
            logger.warning(f"Worker {self.worker_id} already running")
            return

        self._stop_event.clear()
        self._pause_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        self.status = WorkerStatus.RUNNING
        logger.info(f"Worker {self.worker_id} started")

    def stop(self):
        """Stop the worker gracefully"""
        logger.info(f"Stopping worker {self.worker_id}")
        self.status = WorkerStatus.STOPPING
        self._stop_event.set()

        if self._thread:
            self._thread.join(timeout=10)

        self.status = WorkerStatus.STOPPED
        logger.info(f"Worker {self.worker_id} stopped")

    def pause(self):
        """Pause worker execution"""
        logger.info(f"Pausing worker {self.worker_id}")
        self._pause_event.set()
        self.status = WorkerStatus.PAUSED

    def resume(self):
        """Resume worker execution"""
        logger.info(f"Resuming worker {self.worker_id}")
        self._pause_event.clear()
        self.status = WorkerStatus.RUNNING

    def _run_loop(self):
        """Main worker execution loop"""
        logger.info(f"Worker {self.worker_id} entering run loop")

        while not self._stop_event.is_set():
            try:
                # Wait if paused
                while self._pause_event.is_set() and not self._stop_event.is_set():
                    time.sleep(1)

                if self._stop_event.is_set():
                    break

                # Check budget limit
                if self.budget_limit and self.metrics.total_cost >= self.budget_limit:
                    logger.warning(f"Worker {self.worker_id} reached budget limit")
                    self.pause()
                    continue

                # Execute work
                self._execute_with_recovery()

                # Update heartbeat
                self.metrics.last_heartbeat = safe_datetime_now()

                # Wait for next run
                self._stop_event.wait(self.run_interval)

            except Exception as e:
                logger.error(f"Unexpected error in worker {self.worker_id}: {e}")
                self.last_error = str(e)
                self.status = WorkerStatus.ERROR

                if not self.auto_restart:
                    break

                time.sleep(self.crash_cooldown)

        logger.info(f"Worker {self.worker_id} exited run loop")

    def _execute_with_recovery(self):
        """Execute work with crash recovery"""
        try:
            self.metrics.total_runs += 1

            # Run the actual work
            result = self.run()

            # Track results
            if result:
                self.metrics.successful_runs += 1

                # Track revenue/cost if provided
                if isinstance(result, dict):
                    revenue = result.get('revenue', 0.0)
                    cost = result.get('cost', 0.0)

                    self.metrics.total_revenue += revenue
                    self.metrics.total_cost += cost
            else:
                self.metrics.failed_runs += 1

        except Exception as e:
            logger.error(f"Worker {self.worker_id} crashed: {e}")
            logger.error(traceback.format_exc())

            self.metrics.failed_runs += 1
            self.metrics.crash_count += 1
            self.last_error = str(e)

            # Check crash limit
            if self.metrics.crash_count >= self.max_crash_count:
                logger.critical(f"Worker {self.worker_id} exceeded crash limit")
                self.status = WorkerStatus.CRASHED
                self._stop_event.set()
                return

            # Restart with cooldown
            if self.auto_restart:
                logger.info(f"Worker {self.worker_id} auto-restarting after {self.crash_cooldown}s")
                self.metrics.restart_count += 1
                time.sleep(self.crash_cooldown)

    def run(self) -> Optional[Dict[str, Any]]:
        """
        Main work execution method - override in subclasses

        Returns:
            Dict with 'revenue' and 'cost' keys, or None
        """
        raise NotImplementedError("Subclasses must implement run()")

    def get_status(self) -> Dict[str, Any]:
        """Get worker status snapshot"""
        return {
            'worker_id': self.worker_id,
            'name': self.name,
            'status': self.status.value,
            'uptime': str(self.metrics.uptime),
            'uptime_seconds': self.metrics.uptime.total_seconds(),
            'last_heartbeat': self.metrics.last_heartbeat.isoformat(),
            'metrics': {
                'total_runs': self.metrics.total_runs,
                'successful_runs': self.metrics.successful_runs,
                'failed_runs': self.metrics.failed_runs,
                'success_rate': self.metrics.success_rate,
                'total_revenue': self.metrics.total_revenue,
                'total_cost': self.metrics.total_cost,
                'profit': self.metrics.profit,
                'roi': self.metrics.roi,
                'crash_count': self.metrics.crash_count,
                'restart_count': self.metrics.restart_count
            },
            'config': {
                'run_interval': self.run_interval,
                'budget_limit': self.budget_limit,
                'auto_restart': self.auto_restart
            },
            'last_error': self.last_error
        }

    def is_healthy(self) -> bool:
        """Check if worker is healthy"""
        # Check heartbeat (should be within 2x run interval)
        heartbeat_threshold = timedelta(seconds=self.run_interval * 2)
        time_since_heartbeat = safe_datetime_now() - self.metrics.last_heartbeat

        if time_since_heartbeat > heartbeat_threshold:
            return False

        # Check if crashed
        if self.status == WorkerStatus.CRASHED:
            return False

        # Check crash rate
        if self.metrics.crash_count >= self.max_crash_count:
            return False

        return True
