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

logger = logging.getLogger(__name__)

class RetryStrategies:
    """Handles retry strategies and calculations"""
    
    # Base delay for exponential backoff (in seconds)
    BASE_DELAY = 1.0
    
    # Maximum delay between retries (in seconds)
    MAX_DELAY = 60.0
    
    # Delay increment for linear backoff (in seconds)
    LINEAR_INCREMENT = 5.0

    @classmethod
    def calculate_delay(cls, strategy: RetryStrategy, attempt: int) -> Optional[float]:
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
    def prepare_operation_for_retry(
        cls,
        operation: Operation,
        error: OperationError,
        attempt: int
    ) -> None:
        """Update operation metadata for retry"""
        operation.status = OperationStatus.QUEUED
        operation.metadata.update({
            "retry_count": attempt,
            "last_error": error.to_dict(),
            "next_retry": datetime.utcnow().isoformat()
        })
