import asyncio
import logging
from typing import Optional, Dict, Any

from ..models.errors import (
    OperationError,
    ExecutionError
)
from ..models.operations import Operation, OperationStatus
from .retry_strategies import RetryStrategies

logger = logging.getLogger(__name__)

class RetryHandler:
    """Handles retry logic for failed operations"""

    @classmethod
    async def handle_retry(
        cls,
        operation: Operation,
        error: OperationError,
        attempt: int = 1,
        queue = None  # Queue will be injected at runtime
    ) -> bool:
        """
        Handle retry logic for a failed operation
        Returns True if operation should be retried, False otherwise
        """
        if not isinstance(error, OperationError):
            error = ExecutionError(str(error))

        if attempt > error.max_retries:
            logger.warning(
                f"Operation {operation.id} exceeded max retries ({error.max_retries})"
            )
            return False

        delay = RetryStrategies.calculate_delay(error.retry_strategy, attempt)
        if delay is None:
            return False

        # Update operation status for retry
        RetryStrategies.prepare_operation_for_retry(operation, error, attempt)

        # Wait before retry
        await asyncio.sleep(delay)

        if queue is None:
            logger.error("Queue not provided for retry")
            return False

        try:
            # Re-queue the operation
            await queue.add_operation(operation)
            logger.info(
                f"Operation {operation.id} queued for retry {attempt}/{error.max_retries}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to queue retry for operation {operation.id}: {e}")
            return False

    @classmethod
    async def handle_operation_failure(
        cls,
        operation: Operation,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        queue = None  # Queue will be injected at runtime
    ) -> None:
        """Handle operation failure and manage retry process"""
        if not RetryStrategies.should_retry(error):
            logger.info(f"Operation {operation.id} failed with non-retryable error: {error}")
            operation.status = OperationStatus.FAILED
            operation.error = str(error)
            return

        retry_count = operation.metadata.get("retry_count", 0) + 1
        if await cls.handle_retry(operation, error, retry_count, queue):
            logger.info(
                f"Operation {operation.id} scheduled for retry {retry_count} "
                f"with strategy {error.retry_strategy}"
            )
        else:
            logger.error(f"Operation {operation.id} failed after {retry_count} retries")
            operation.status = OperationStatus.FAILED
            operation.error = str(error)
            operation.metadata["final_error"] = {
                "message": str(error),
                "retry_count": retry_count,
                "context": context
            }
