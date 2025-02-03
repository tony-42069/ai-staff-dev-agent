import asyncio
import logging
import time
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime, timedelta

from ..models.operations import Operation, OperationStatus, OperationPriority
from .operation_queue import queue as operation_queue

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and manages system metrics for operations and queue health"""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval  # seconds
        self.metrics: Dict[str, Any] = defaultdict(dict)
        self.running = False
        self.collection_task: asyncio.Task = None
        
        # Initialize metrics structure
        self._init_metrics()

    def _init_metrics(self):
        """Initialize metrics structure with default values"""
        self.metrics.update({
            "operations": {
                "total": 0,
                "active": 0,
                "completed": 0,
                "failed": 0,
                "queued": 0,
                "cancelled": 0,
                "by_priority": {
                    "high": 0,
                    "normal": 0,
                    "low": 0
                },
                "success_rate": 0.0,
                "average_duration": 0.0
            },
            "queues": {
                "high": {"size": 0, "wait_time": 0.0},
                "normal": {"size": 0, "wait_time": 0.0},
                "low": {"size": 0, "wait_time": 0.0}
            },
            "system": {
                "worker_utilization": 0.0,
                "error_rate": 0.0,
                "retry_rate": 0.0
            },
            "history": {
                "last_hour": [],
                "last_day": []
            }
        })

    async def start(self):
        """Start metrics collection"""
        if self.running:
            return
            
        self.running = True
        self.collection_task = asyncio.create_task(self._collect_metrics_loop())
        logger.info("Metrics collection started")

    async def stop(self):
        """Stop metrics collection"""
        self.running = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics collection stopped")

    async def _collect_metrics_loop(self):
        """Main metrics collection loop"""
        while self.running:
            try:
                await self._collect_metrics()
                await self._update_history()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(5)  # Short delay on error

    async def _collect_metrics(self):
        """Collect current system metrics"""
        # Get all operations
        operations = list(operation_queue.active_operations.values())
        
        # Reset counters
        status_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        durations = []
        
        # Calculate metrics
        for op in operations:
            status_counts[op.status] += 1
            priority_counts[op.priority] += 1
            
            if "start_time" in op.metadata:
                start_time = datetime.fromisoformat(op.metadata["start_time"])
                if op.status in [OperationStatus.COMPLETED, OperationStatus.FAILED]:
                    duration = (datetime.utcnow() - start_time).total_seconds()
                    durations.append(duration)
        
        # Update operation metrics
        self.metrics["operations"].update({
            "total": len(operations),
            "active": status_counts[OperationStatus.RUNNING],
            "completed": status_counts[OperationStatus.COMPLETED],
            "failed": status_counts[OperationStatus.FAILED],
            "queued": status_counts[OperationStatus.QUEUED],
            "cancelled": status_counts[OperationStatus.CANCELLED],
            "by_priority": {
                "high": priority_counts[OperationPriority.HIGH],
                "normal": priority_counts[OperationPriority.NORMAL],
                "low": priority_counts[OperationPriority.LOW]
            }
        })
        
        # Calculate success rate
        total_completed = (status_counts[OperationStatus.COMPLETED] + 
                         status_counts[OperationStatus.FAILED])
        if total_completed > 0:
            self.metrics["operations"]["success_rate"] = (
                status_counts[OperationStatus.COMPLETED] / total_completed * 100
            )
        
        # Calculate average duration
        if durations:
            self.metrics["operations"]["average_duration"] = sum(durations) / len(durations)
        
        # Update queue metrics
        for priority in OperationPriority:
            queue = operation_queue.queues[priority]
            # Skip queue size metrics for now since we can't await in this context
            self.metrics["queues"][priority.value].update({
                "size": 0,  # Temporarily set to 0 to avoid qsize() issues
                "wait_time": 0.0
            })
        
        # Update system metrics
        total_workers = sum(len(workers) for workers in operation_queue.workers.values())
        if total_workers > 0:
            self.metrics["system"]["worker_utilization"] = (
                len(operation_queue.active_operations) / total_workers * 100
            )
        
        # Calculate error and retry rates
        total_ops = len(operations)
        if total_ops > 0:
            retry_count = sum(
                1 for op in operations 
                if op.metadata.get("retry_count", 0) > 0
            )
            self.metrics["system"].update({
                "error_rate": status_counts[OperationStatus.FAILED] / total_ops * 100,
                "retry_rate": retry_count / total_ops * 100
            })

    def _estimate_queue_wait_time(self, queue_size: int) -> float:
        """Estimate average wait time for operations in queue"""
        if queue_size == 0:
            return 0.0
        # Simple estimation based on average operation duration and queue size
        avg_duration = self.metrics["operations"]["average_duration"]
        return avg_duration * queue_size / operation_queue.max_workers

    async def _update_history(self):
        """Update historical metrics"""
        current_metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "operations": self.metrics["operations"].copy(),
            "queues": self.metrics["queues"].copy(),
            "system": self.metrics["system"].copy()
        }
        
        # Update hourly metrics
        self.metrics["history"]["last_hour"].append(current_metrics)
        self.metrics["history"]["last_hour"] = self._trim_history(
            self.metrics["history"]["last_hour"],
            timedelta(hours=1)
        )
        
        # Update daily metrics (sampled every hour)
        if len(self.metrics["history"]["last_hour"]) % 60 == 0:
            self.metrics["history"]["last_day"].append(current_metrics)
            self.metrics["history"]["last_day"] = self._trim_history(
                self.metrics["history"]["last_day"],
                timedelta(days=1)
            )

    def _trim_history(
        self,
        history: List[Dict[str, Any]],
        max_age: timedelta
    ) -> List[Dict[str, Any]]:
        """Trim historical metrics older than max_age"""
        cutoff = datetime.utcnow() - max_age
        return [
            m for m in history
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        return self.metrics.copy()

    def get_historical_metrics(
        self,
        timeframe: str = "hour"
    ) -> List[Dict[str, Any]]:
        """Get historical metrics for specified timeframe"""
        if timeframe == "hour":
            return self.metrics["history"]["last_hour"]
        elif timeframe == "day":
            return self.metrics["history"]["last_day"]
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")


# Global metrics collector instance
collector = MetricsCollector()
