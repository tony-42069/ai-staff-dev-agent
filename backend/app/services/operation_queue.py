"""Service for managing operation queues and execution."""
import asyncio
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import heapq

from ..models.operations import (
    Operation,
    OperationStatus,
    OperationPriority,
    OperationQueue,
    OperationStats
)
from ..models.errors import (
    OperationError,
    QueueError,
    TimeoutError,
    RetryStrategy
)

logger = logging.getLogger(__name__)

class PriorityQueue:
    """Priority queue implementation for operations."""
    def __init__(self):
        self.queue: List[tuple[int, datetime, Operation]] = []
        self.entry_count = 0

    def push(self, operation: Operation) -> None:
        """Push operation to queue with priority."""
        priority = self._get_priority_value(operation.priority)
        heapq.heappush(
            self.queue,
            (priority, operation.created_at, operation)
        )
        self.entry_count += 1

    def pop(self) -> Optional[Operation]:
        """Pop highest priority operation from queue."""
        if not self.queue:
            return None
        return heapq.heappop(self.queue)[2]

    def peek(self) -> Optional[Operation]:
        """View next operation without removing it."""
        if not self.queue:
            return None
        return self.queue[0][2]

    def remove(self, operation_id: str) -> Optional[Operation]:
        """Remove specific operation from queue."""
        for i, (_, _, op) in enumerate(self.queue):
            if op.id == operation_id:
                return heapq.heappop(self.queue[i])[2]
        return None

    def _get_priority_value(self, priority: OperationPriority) -> int:
        """Convert priority enum to numeric value."""
        priority_values = {
            OperationPriority.HIGH: 0,
            OperationPriority.NORMAL: 1,
            OperationPriority.LOW: 2
        }
        return priority_values.get(priority, 1)

class OperationQueueManager:
    """Manages operation queues and execution."""
    def __init__(self):
        self.queues: Dict[str, PriorityQueue] = defaultdict(PriorityQueue)
        self.active_operations: Dict[str, Operation] = {}
        self.operation_handlers: Dict[str, Callable[[Operation], Awaitable[Any]]] = {}
        self.stats: Dict[str, OperationStats] = defaultdict(OperationStats)
        self.max_concurrent = 10
        self.default_timeout = 300  # 5 minutes

    async def enqueue_operation(
        self,
        operation: Operation,
        queue_name: str = "default"
    ) -> None:
        """Add operation to queue."""
        try:
            operation.status = OperationStatus.QUEUED
            self.queues[queue_name].push(operation)
            logger.info(
                "Operation %s added to queue %s",
                operation.id,
                queue_name
            )
        except Exception as e:
            logger.error("Failed to enqueue operation: %s", e)
            raise QueueError(
                f"Failed to enqueue operation: {str(e)}",
                queue_name=queue_name
            )

    async def start_processing(self) -> None:
        """Start processing operations from queues."""
        while True:
            try:
                if len(self.active_operations) < self.max_concurrent:
                    for queue_name, queue in self.queues.items():
                        operation = queue.peek()
                        if operation and operation.id not in self.active_operations:
                            await self._process_operation(operation, queue_name)
                await asyncio.sleep(0.1)  # Prevent CPU spinning
            except Exception as e:
                logger.error("Error in queue processing: %s", e)
                await asyncio.sleep(1)  # Back off on error

    async def _process_operation(
        self,
        operation: Operation,
        queue_name: str
    ) -> None:
        """Process a single operation."""
        try:
            # Remove from queue and mark as running
            self.queues[queue_name].pop()
            operation.status = OperationStatus.RUNNING
            operation.started_at = datetime.utcnow()
            self.active_operations[operation.id] = operation

            # Get handler for operation type
            handler = self.operation_handlers.get(operation.capability)
            if not handler:
                raise OperationError(
                    f"No handler found for capability: {operation.capability}"
                )

            # Execute with timeout
            try:
                async with asyncio.timeout(self.default_timeout):
                    result = await handler(operation)
                    operation.result = result
                    operation.status = OperationStatus.COMPLETED
            except asyncio.TimeoutError:
                raise TimeoutError(
                    "Operation timed out",
                    timeout=self.default_timeout
                )

        except Exception as e:
            logger.error(
                "Operation %s failed: %s",
                operation.id,
                str(e)
            )
            operation.status = OperationStatus.FAILED
            operation.error = str(e)
            await self._handle_operation_error(operation, e)

        finally:
            operation.completed_at = datetime.utcnow()
            self.active_operations.pop(operation.id, None)
            await self._update_stats(operation, queue_name)

    async def _handle_operation_error(
        self,
        operation: Operation,
        error: Exception
    ) -> None:
        """Handle operation errors and retries."""
        if isinstance(error, OperationError):
            if error.retry_strategy != RetryStrategy.NO_RETRY:
                await self._retry_operation(operation, error)
        else:
            # Default retry strategy for unknown errors
            await self._retry_operation(
                operation,
                OperationError(
                    str(error),
                    retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                    max_retries=3
                )
            )

    async def _retry_operation(
        self,
        operation: Operation,
        error: OperationError
    ) -> None:
        """Retry failed operation based on strategy."""
        retry_count = operation.metadata.get("retry_count", 0)
        if retry_count >= error.max_retries:
            logger.warning(
                "Operation %s exceeded max retries",
                operation.id
            )
            return

        retry_count += 1
        operation.metadata["retry_count"] = retry_count
        operation.status = OperationStatus.RETRYING

        # Calculate delay based on strategy
        delay = self._calculate_retry_delay(
            error.retry_strategy,
            retry_count
        )

        logger.info(
            "Retrying operation %s in %.2f seconds (attempt %d/%d)",
            operation.id,
            delay,
            retry_count,
            error.max_retries
        )

        await asyncio.sleep(delay)
        await self.enqueue_operation(operation)

    def _calculate_retry_delay(
        self,
        strategy: RetryStrategy,
        retry_count: int,
        base_delay: float = 1.0
    ) -> float:
        """Calculate delay for retry based on strategy."""
        if strategy == RetryStrategy.IMMEDIATE:
            return 0
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            return base_delay * retry_count
        elif strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return base_delay * (2 ** (retry_count - 1))
        return base_delay

    async def _update_stats(
        self,
        operation: Operation,
        queue_name: str
    ) -> None:
        """Update operation statistics."""
        stats = self.stats[queue_name]
        stats.total_count += 1

        if operation.status == OperationStatus.COMPLETED:
            stats.success_count += 1
        elif operation.status == OperationStatus.FAILED:
            stats.failure_count += 1

        if operation.completed_at and operation.started_at:
            duration = (
                operation.completed_at - operation.started_at
            ).total_seconds()
            
            # Update duration stats
            if stats.total_count == 1:
                stats.min_duration = duration
                stats.max_duration = duration
            else:
                stats.min_duration = min(stats.min_duration, duration)
                stats.max_duration = max(stats.max_duration, duration)
            
            # Update moving average
            stats.average_duration = (
                (stats.average_duration * (stats.total_count - 1) + duration)
                / stats.total_count
            )

        # Update error rate
        stats.error_rate = (
            stats.failure_count / stats.total_count
            if stats.total_count > 0
            else 0.0
        )

        # Calculate throughput (operations per minute)
        window = timedelta(minutes=5)
        recent_count = sum(
            1 for op in self.active_operations.values()
            if op.completed_at
            and op.completed_at > datetime.utcnow() - window
        )
        stats.throughput = recent_count / 5.0  # ops/minute

    def get_queue_status(self, queue_name: str) -> OperationQueue:
        """Get current status of a queue."""
        queue = self.queues.get(queue_name)
        if not queue:
            return OperationQueue(queue_name=queue_name)

        active_count = sum(
            1 for op in self.active_operations.values()
            if op.metadata.get("queue_name") == queue_name
        )

        stats = self.stats.get(queue_name, OperationStats())

        return OperationQueue(
            queue_name=queue_name,
            total_operations=queue.entry_count,
            active_operations=active_count,
            waiting_operations=len(queue.queue),
            completed_operations=stats.success_count,
            failed_operations=stats.failure_count,
            average_wait_time=stats.average_duration,
            average_processing_time=stats.average_duration,
            metadata={
                "error_rate": stats.error_rate,
                "throughput": stats.throughput
            }
        )

    def register_handler(
        self,
        capability: str,
        handler: Callable[[Operation], Awaitable[Any]]
    ) -> None:
        """Register handler for operation type."""
        self.operation_handlers[capability] = handler
        logger.info("Registered handler for capability: %s", capability)

# Global queue manager instance
queue_manager = OperationQueueManager()
