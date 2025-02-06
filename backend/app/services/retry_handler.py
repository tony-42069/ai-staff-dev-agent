"""Service for handling operation retries."""
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime, timedelta
import logging

from .retry_strategies import (
    RetryConfig,
    retry_operation,
    with_retry,
    with_circuit_breaker
)
from ..models.errors import (
    OperationError,
    RetryStrategy,
    ErrorCode
)
from ..models.operations import Operation, OperationStatus

logger = logging.getLogger(__name__)

class RetryHandler:
    """Handles operation retries with different strategies."""
    def __init__(self):
        self.default_config = RetryConfig()
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.retry_counts: Dict[str, Dict[str, int]] = {}

    def get_retry_config(
        self,
        operation: Operation,
        error: Optional[Exception] = None
    ) -> RetryConfig:
        """Get retry configuration for operation."""
        # Default configuration
        config = RetryConfig()

        # Adjust based on operation type
        if operation.type:
            if operation.type.value in ["deployment", "system_maintenance"]:
                config.max_retries = 5
                config.strategy = RetryStrategy.EXPONENTIAL_BACKOFF
                config.base_delay = 2.0
            elif operation.type.value in ["testing", "documentation"]:
                config.max_retries = 2
                config.strategy = RetryStrategy.LINEAR_BACKOFF
                config.base_delay = 1.0

        # Adjust based on error type
        if isinstance(error, OperationError):
            if error.code in [
                ErrorCode.NETWORK_ERROR,
                ErrorCode.DATABASE_ERROR
            ]:
                config.strategy = RetryStrategy.EXPONENTIAL_BACKOFF
                config.max_retries = 5
            elif error.code == ErrorCode.RESOURCE_BUSY:
                config.strategy = RetryStrategy.LINEAR_BACKOFF
                config.base_delay = 5.0
            elif error.code == ErrorCode.VALIDATION_ERROR:
                config.strategy = RetryStrategy.NO_RETRY

        # Adjust based on previous retry history
        operation_key = f"{operation.project_id}:{operation.id}"
        if operation_key in self.retry_counts:
            previous_retries = self.retry_counts[operation_key]
            if previous_retries.get("total", 0) > 10:
                config.max_retries = 1  # Reduce retries for frequently failing operations
            if previous_retries.get("consecutive_failures", 0) > 3:
                config.base_delay *= 2  # Increase delay for consistently failing operations

        return config

    async def execute_with_retry(
        self,
        operation: Operation,
        handler: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ) -> Any:
        """Execute operation with retry handling."""
        operation_key = f"{operation.project_id}:{operation.id}"
        
        try:
            # Initialize retry tracking if needed
            if operation_key not in self.retry_counts:
                self.retry_counts[operation_key] = {
                    "total": 0,
                    "consecutive_failures": 0,
                    "last_status": None,
                    "last_attempt": None
                }

            # Get retry configuration
            config = self.get_retry_config(operation)

            # Execute with retry
            result = await retry_operation(
                handler,
                config,
                *args,
                **kwargs
            )

            # Update success metrics
            self.retry_counts[operation_key]["consecutive_failures"] = 0
            self.retry_counts[operation_key]["last_status"] = "success"
            self.retry_counts[operation_key]["last_attempt"] = datetime.utcnow()

            return result

        except Exception as e:
            # Update failure metrics
            self.retry_counts[operation_key]["total"] += 1
            self.retry_counts[operation_key]["consecutive_failures"] += 1
            self.retry_counts[operation_key]["last_status"] = "failure"
            self.retry_counts[operation_key]["last_attempt"] = datetime.utcnow()

            # Check if we should apply circuit breaker
            if self._should_apply_circuit_breaker(operation_key):
                await self._create_circuit_breaker(operation_key)

            raise

    def _should_apply_circuit_breaker(self, operation_key: str) -> bool:
        """Determine if circuit breaker should be applied."""
        if operation_key not in self.retry_counts:
            return False

        counts = self.retry_counts[operation_key]
        consecutive_failures = counts.get("consecutive_failures", 0)
        total_failures = counts.get("total", 0)
        last_attempt = counts.get("last_attempt")

        # Apply if many consecutive failures
        if consecutive_failures >= 5:
            return True

        # Apply if high failure rate in short time
        if (
            total_failures >= 10
            and last_attempt
            and (datetime.utcnow() - last_attempt) <= timedelta(minutes=5)
        ):
            return True

        return False

    async def _create_circuit_breaker(self, operation_key: str) -> None:
        """Create and configure circuit breaker."""
        if operation_key in self.circuit_breakers:
            return

        self.circuit_breakers[operation_key] = {
            "created_at": datetime.utcnow(),
            "failure_count": self.retry_counts[operation_key].get("total", 0),
            "reset_timeout": 60.0,  # 1 minute default
            "status": "open"
        }

        logger.warning(
            "Circuit breaker created for operation key: %s",
            operation_key
        )

    async def check_circuit_breaker(self, operation_key: str) -> None:
        """Check if operation is allowed by circuit breaker."""
        if operation_key not in self.circuit_breakers:
            return

        breaker = self.circuit_breakers[operation_key]
        if breaker["status"] == "open":
            elapsed = (
                datetime.utcnow() - breaker["created_at"]
            ).total_seconds()

            if elapsed >= breaker["reset_timeout"]:
                breaker["status"] = "half-open"
                logger.info(
                    "Circuit breaker transitioning to half-open: %s",
                    operation_key
                )
            else:
                raise OperationError(
                    "Operation blocked by circuit breaker",
                    code=ErrorCode.RESOURCE_BUSY,
                    retry_strategy=RetryStrategy.LINEAR_BACKOFF,
                    max_retries=3
                )

    async def cleanup_old_data(self) -> None:
        """Clean up old retry and circuit breaker data."""
        while True:
            try:
                current_time = datetime.utcnow()

                # Clean up old retry counts
                for key in list(self.retry_counts.keys()):
                    last_attempt = self.retry_counts[key].get("last_attempt")
                    if (
                        last_attempt
                        and (current_time - last_attempt) > timedelta(hours=1)
                    ):
                        del self.retry_counts[key]

                # Clean up old circuit breakers
                for key in list(self.circuit_breakers.keys()):
                    created_at = self.circuit_breakers[key]["created_at"]
                    if (
                        current_time - created_at
                    ) > timedelta(minutes=30):
                        del self.circuit_breakers[key]

                await asyncio.sleep(300)  # Clean up every 5 minutes

            except Exception as e:
                logger.error("Error in retry handler cleanup: %s", e)
                await asyncio.sleep(60)

# Global retry handler instance
retry_handler = RetryHandler()
