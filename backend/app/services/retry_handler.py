import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ..models.errors import (
    OperationError,
    RetryStrategy,
    ExecutionError,
    TimeoutError,
    ResourceError,
    NetworkError,
    QueueError
)
from ..models.operations import Operation, OperationStatus
from .operation_queue import queue as operation_queue

logger = logging.getLogger(__name__)

class RetryHandler:
    """Handles retry logic for failed operations"""
    
    # Base delay for exponential backoff (in seconds)
    BASE_DELAY = 1.0
    
    # Maximum delay between retries (in seconds)
    MAX_DELAY = 60.0
    
    # Delay increment for linear backoff (in seconds)
    LINEAR_INCREMENT = 5.0

    @classmethod
    async def handle_retry(
        cls,
        operation: Operation,
        error: OperationError,
        attempt: int = 1
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

        delay = cls._calculate_delay(error.retry_strategy, attempt)
        if delay is None:
            return False

        # Update operation status for retry
        operation.status = OperationStatus.QUEUED
        operation.metadata.update({
            "retry_count": attempt,
            "last_error": error.to_dict(),
            "next_retry": datetime.utcnow().isoformat()
        })

        # Wait before retry
        await asyncio.sleep(delay)

        try:
            # Re-queue the operation
            await operation_queue.add_operation(operation)
            logger.info(
                f"Operation {operation.id} queued for retry {attempt}/{error.max_retries}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to queue retry for operation {operation.id}: {e}")
            return False

    @classmethod
    def _calculate_delay(cls, strategy: RetryStrategy, attempt: int) -> Optional[float]:
        """Calculate delay before next retry based on strategy and attempt number"""
        if strategy == RetryStrategy.NO_RETRY:
            return None
            
        if strategy == RetryStrategy.IMMEDIATE:
            return 0
            
        if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = min(
                cls.BASE_DELAY * (2 ** (attempt - 1)),
                cls.MAX_DELAY
            )
            # Add small random jitter to prevent thundering herd
            jitter = asyncio.get_event_loop().time() * 0.1
            return delay + jitter
            
        if strategy == RetryStrategy.LINEAR_BACKOFF:
            return min(
                cls.LINEAR_INCREMENT * attempt,
                cls.MAX_DELAY
            )
            
        return None

    @classmethod
    def should_retry(cls, error: Exception) -> bool:
        """Determine if an error type is retryable"""
        RETRYABLE_ERRORS = (
            ExecutionError,
            TimeoutError,
            ResourceError,
            NetworkError,
            QueueError
        )
        return isinstance(error, RETRYABLE_ERRORS)

    @classmethod
    async def handle_operation_failure(
        cls,
        operation: Operation,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle operation failure and manage retry process"""
        if not cls.should_retry(error):
            logger.info(f"Operation {operation.id} failed with non-retryable error: {error}")
            operation.status = OperationStatus.FAILED
            operation.error = str(error)
            return

        retry_count = operation.metadata.get("retry_count", 0) + 1
        if await cls.handle_retry(operation, error, retry_count):
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
