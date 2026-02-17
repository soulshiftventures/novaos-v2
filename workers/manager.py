"""
Worker Manager - Orchestrates background workers
"""

import logging
from typing import Dict, List, Optional, Type
from datetime import datetime
from .base_worker import BaseWorker, WorkerStatus


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)


logger = logging.getLogger(__name__)


class WorkerManager:
    """
    Manages lifecycle of all background workers

    Features:
    - Start/stop all workers
    - Scale workers up/down
    - Monitor worker health
    - Aggregate metrics
    """

    _instance = None

    def __init__(self):
        """Initialize worker manager"""
        self.workers: Dict[str, BaseWorker] = {}
        self.worker_classes: Dict[str, Type[BaseWorker]] = {}
        logger.info("WorkerManager initialized")

    def register_worker_class(self, worker_type: str, worker_class: Type[BaseWorker]):
        """Register a worker class for deployment"""
        self.worker_classes[worker_type] = worker_class
        logger.info(f"Registered worker type: {worker_type}")

    def deploy_worker(
        self,
        worker_type: str,
        worker_id: str,
        name: str,
        config: Optional[Dict] = None,
        auto_start: bool = True
    ) -> BaseWorker:
        """
        Deploy a new worker instance

        Args:
            worker_type: Type of worker to deploy
            worker_id: Unique worker ID
            name: Human-readable name
            config: Worker configuration
            auto_start: Start immediately

        Returns:
            Deployed worker instance
        """
        if worker_type not in self.worker_classes:
            raise ValueError(f"Unknown worker type: {worker_type}")

        if worker_id in self.workers:
            raise ValueError(f"Worker {worker_id} already exists")

        worker_class = self.worker_classes[worker_type]
        worker = worker_class(worker_id=worker_id, name=name)

        # Apply config
        if config:
            worker.config.update(config)

        self.workers[worker_id] = worker
        logger.info(f"Deployed worker {worker_id}: {name}")

        if auto_start:
            worker.start()

        return worker

    def start_worker(self, worker_id: str):
        """Start a specific worker"""
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found")

        self.workers[worker_id].start()

    def stop_worker(self, worker_id: str):
        """Stop a specific worker"""
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found")

        self.workers[worker_id].stop()

    def pause_worker(self, worker_id: str):
        """Pause a specific worker"""
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found")

        self.workers[worker_id].pause()

    def resume_worker(self, worker_id: str):
        """Resume a specific worker"""
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found")

        self.workers[worker_id].resume()

    def kill_worker(self, worker_id: str):
        """Kill and remove a worker"""
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found")

        worker = self.workers[worker_id]
        worker.stop()
        del self.workers[worker_id]
        logger.info(f"Killed worker {worker_id}")

    def start_all(self):
        """Start all workers"""
        logger.info(f"Starting all {len(self.workers)} workers")
        for worker in self.workers.values():
            if worker.status == WorkerStatus.STOPPED:
                worker.start()

    def stop_all(self):
        """Stop all workers gracefully"""
        logger.info(f"Stopping all {len(self.workers)} workers")
        for worker in self.workers.values():
            if worker.status == WorkerStatus.RUNNING:
                worker.stop()

    def pause_all(self):
        """Pause all workers"""
        logger.info(f"Pausing all {len(self.workers)} workers")
        for worker in self.workers.values():
            if worker.status == WorkerStatus.RUNNING:
                worker.pause()

    def resume_all(self):
        """Resume all workers"""
        logger.info(f"Resuming all {len(self.workers)} workers")
        for worker in self.workers.values():
            if worker.status == WorkerStatus.PAUSED:
                worker.resume()

    def scale_worker(self, worker_id: str, multiplier: int):
        """
        Scale a worker by creating multiple instances

        Args:
            worker_id: Base worker ID
            multiplier: Number of instances to create
        """
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found")

        base_worker = self.workers[worker_id]

        # Create additional instances
        for i in range(1, multiplier):
            new_id = f"{worker_id}_scaled_{i}"
            new_name = f"{base_worker.name} (scaled {i})"

            # Find worker type
            worker_type = None
            for wtype, wclass in self.worker_classes.items():
                if isinstance(base_worker, wclass):
                    worker_type = wtype
                    break

            if worker_type:
                self.deploy_worker(
                    worker_type=worker_type,
                    worker_id=new_id,
                    name=new_name,
                    config=base_worker.config.copy()
                )
                logger.info(f"Scaled worker {worker_id} to {new_id}")

    def get_worker(self, worker_id: str) -> Optional[BaseWorker]:
        """Get worker by ID"""
        return self.workers.get(worker_id)

    def list_workers(
        self,
        status: Optional[WorkerStatus] = None,
        worker_type: Optional[str] = None
    ) -> List[BaseWorker]:
        """
        List workers with optional filters

        Args:
            status: Filter by status
            worker_type: Filter by type

        Returns:
            List of matching workers
        """
        workers = list(self.workers.values())

        if status:
            workers = [w for w in workers if w.status == status]

        if worker_type and worker_type in self.worker_classes:
            worker_class = self.worker_classes[worker_type]
            workers = [w for w in workers if isinstance(w, worker_class)]

        return workers

    def get_status(self) -> Dict:
        """Get aggregate status of all workers"""
        total_workers = len(self.workers)
        running = sum(1 for w in self.workers.values() if w.status == WorkerStatus.RUNNING)
        paused = sum(1 for w in self.workers.values() if w.status == WorkerStatus.PAUSED)
        stopped = sum(1 for w in self.workers.values() if w.status == WorkerStatus.STOPPED)
        crashed = sum(1 for w in self.workers.values() if w.status == WorkerStatus.CRASHED)
        error = sum(1 for w in self.workers.values() if w.status == WorkerStatus.ERROR)

        # Aggregate metrics
        total_revenue = sum(w.metrics.total_revenue for w in self.workers.values())
        total_cost = sum(w.metrics.total_cost for w in self.workers.values())
        total_runs = sum(w.metrics.total_runs for w in self.workers.values())
        successful_runs = sum(w.metrics.successful_runs for w in self.workers.values())

        # Calculate aggregate ROI
        roi = 0.0
        if total_cost > 0:
            roi = ((total_revenue - total_cost) / total_cost) * 100

        return {
            'timestamp': safe_datetime_now().isoformat(),
            'workers': {
                'total': total_workers,
                'running': running,
                'paused': paused,
                'stopped': stopped,
                'crashed': crashed,
                'error': error
            },
            'metrics': {
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'profit': total_revenue - total_cost,
                'roi': roi,
                'total_runs': total_runs,
                'successful_runs': successful_runs,
                'success_rate': (successful_runs / total_runs * 100) if total_runs > 0 else 0
            },
            'workers_detail': [w.get_status() for w in self.workers.values()]
        }

    def health_check(self) -> Dict:
        """Check health of all workers"""
        unhealthy = []
        needs_restart = []

        for worker_id, worker in self.workers.items():
            if not worker.is_healthy():
                unhealthy.append(worker_id)

                # Check if should restart
                if worker.status == WorkerStatus.CRASHED and worker.auto_restart:
                    needs_restart.append(worker_id)

        return {
            'timestamp': safe_datetime_now().isoformat(),
            'healthy': len(self.workers) - len(unhealthy),
            'unhealthy': len(unhealthy),
            'unhealthy_workers': unhealthy,
            'needs_restart': needs_restart
        }

    def auto_heal(self):
        """Auto-restart crashed workers"""
        health = self.health_check()

        for worker_id in health['needs_restart']:
            logger.info(f"Auto-healing worker {worker_id}")
            worker = self.workers[worker_id]

            # Reset crash count
            worker.metrics.crash_count = 0
            worker.status = WorkerStatus.STOPPED

            # Restart
            worker.start()


# Global singleton
_manager_instance = None


def get_worker_manager() -> WorkerManager:
    """Get global worker manager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = WorkerManager()
    return _manager_instance
