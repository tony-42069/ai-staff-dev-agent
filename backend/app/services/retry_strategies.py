"""Retry strategies for handling operation failures."""
import asyncio
import random
from typing import Optional, Callable, Any, Awaitable
from datetime import datetime, timedelta
import logging
from functools import wraps

from ..models.errors import (
    OperationError,
    RetryStrategy,
    ErrorCode
)

logger = logging.getLogger(__name__)

class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(
        self,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        timeout: Optional[float] = None
    ):
        self.strategy = strategy
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.timeout = timeout

class RetryState:
    """State tracking for retries."""
    def __init__(self):
        self.attempts = 0
        self.start_time: Optional[datetime] = None
        self.last_attempt: Optional[datetime] = None
        self.errors: list[Exception] = []
        self.total_delay = 0.0

    def record_attempt(self, error: Optional[Exception] = None) -> None:
        """Record an attempt and optionally an error."""
        self.attempts += 1
        self.last_attempt = datetime.utcnow()
        if error:
            self.errors.append(error)

    def should_retry(self, config: RetryConfig) -> bool:
        """Determine if another retry should be attempted."""
        if self.attempts >= config.max_retries:
            return False
            
        if config.timeout and self.start_time:
            elapsed = (datetime.utcnow() - self.start_time).total_seconds()
            if elapsed >= config.timeout:
                return False
                
        return True

def calculate_delay(
    state: RetryState,
    config: RetryConfig
) -> float:
    """Calculate delay before next retry."""
    if config.strategy == RetryStrategy.IMMEDIATE:
        delay = 0.0
    elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
        delay = config.base_delay * state.attempts
    elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
        delay = config.base_delay * (2 ** (state.attempts - 1))
    else:
        delay = config.base_delay

    # Apply maximum delay limit
    delay = min(delay, config.max_delay)

    # Add jitter if enabled
    if config.jitter:
        jitter = random.uniform(-0.1, 0.1) * delay
        delay += jitter

    return delay

async def retry_operation(
    operation: Callable[..., Awaitable[Any]],
    config: RetryConfig,
    *args,
    **kwargs
) -> Any:
    """Retry an async operation with configured strategy."""
    state = RetryState()
    state.start_time = datetime.utcnow()

    while True:
        try:
            return await operation(*args, **kwargs)

        except Exception as e:
            state.record_attempt(e)
            
            if not state.should_retry(config):
                if isinstance(e, OperationError):
                    raise
                raise OperationError(
                    str(e),
                    code=ErrorCode.OPERATION_FAILED,
                    retry_strategy=config.strategy,
                    max_retries=config.max_retries,
                    context={
                        "attempts": state.attempts,
                        "total_delay": state.total_delay,
                        "errors": [str(err) for err in state.errors]
                    }
                )

            delay = calculate_delay(state, config)
            state.total_delay += delay

            logger.warning(
                "Operation failed (attempt %d/%d). Retrying in %.2f seconds. Error: %s",
                state.attempts,
                config.max_retries,
                delay,
                str(e)
            )

            await asyncio.sleep(delay)

def with_retry(
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    timeout: Optional[float] = None
):
    """Decorator for adding retry behavior to async functions."""
    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            config = RetryConfig(
                strategy=strategy,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                jitter=jitter,
                timeout=timeout
            )
            return await retry_operation(func, config, *args, **kwargs)
        return wrapper
    return decorator

class CircuitBreaker:
    """Circuit breaker for preventing cascading failures."""
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        half_open_timeout: float = 5.0
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, or half-open
        self._lock = asyncio.Lock()

    async def call(
        self,
        operation: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ) -> Any:
        """Execute operation with circuit breaker protection."""
        async with self._lock:
            await self._check_state()

            if self.state == "open":
                raise OperationError(
                    "Circuit breaker is open",
                    code=ErrorCode.RESOURCE_BUSY,
                    retry_strategy=RetryStrategy.LINEAR_BACKOFF,
                    max_retries=3
                )

            try:
                result = await operation(*args, **kwargs)
                if self.state == "half-open":
                    await self._close()
                return result

            except Exception as e:
                await self._record_failure()
                raise

    async def _check_state(self) -> None:
        """Check and update circuit breaker state."""
        if self.state == "open" and self.last_failure_time:
            elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
            if elapsed >= self.reset_timeout:
                self.state = "half-open"
                logger.info("Circuit breaker transitioning to half-open state")

    async def _record_failure(self) -> None:
        """Record a failure and potentially open the circuit."""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()

        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning("Circuit breaker opened after %d failures", self.failures)

    async def _close(self) -> None:
        """Close the circuit breaker."""
        self.state = "closed"
        self.failures = 0
        self.last_failure_time = None
        logger.info("Circuit breaker closed")

def with_circuit_breaker(
    failure_threshold: int = 5,
    reset_timeout: float = 60.0,
    half_open_timeout: float = 5.0
):
    """Decorator for adding circuit breaker protection."""
    circuit_breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        reset_timeout=reset_timeout,
        half_open_timeout=half_open_timeout
    )

    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
