from typing import Dict, Optional
from enum import Enum


class ErrorCode(str, Enum):
    """Error codes for operation failures"""
    VALIDATION_ERROR = "validation_error"
    EXECUTION_ERROR = "execution_error"
    TIMEOUT_ERROR = "timeout_error"
    RESOURCE_ERROR = "resource_error"
    PERMISSION_ERROR = "permission_error"
    SYSTEM_ERROR = "system_error"
    NETWORK_ERROR = "network_error"
    QUEUE_ERROR = "queue_error"


class RetryStrategy(str, Enum):
    """Retry strategies for failed operations"""
    NO_RETRY = "no_retry"
    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"


class OperationError(Exception):
    """Base exception for operation-related errors"""
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[Dict] = None,
        retry_strategy: RetryStrategy = RetryStrategy.NO_RETRY,
        max_retries: int = 0
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.retry_strategy = retry_strategy
        self.max_retries = max_retries
        super().__init__(message)

    def to_dict(self) -> Dict:
        """Convert error to dictionary format"""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "retry_strategy": self.retry_strategy,
            "max_retries": self.max_retries
        }


class ValidationError(OperationError):
    """Raised when operation parameters are invalid"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            retry_strategy=RetryStrategy.NO_RETRY
        )


class ExecutionError(OperationError):
    """Raised when operation execution fails"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            code=ErrorCode.EXECUTION_ERROR,
            message=message,
            details=details,
            retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            max_retries=3
        )


class TimeoutError(OperationError):
    """Raised when operation times out"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            code=ErrorCode.TIMEOUT_ERROR,
            message=message,
            details=details,
            retry_strategy=RetryStrategy.LINEAR_BACKOFF,
            max_retries=2
        )


class ResourceError(OperationError):
    """Raised when required resources are unavailable"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            code=ErrorCode.RESOURCE_ERROR,
            message=message,
            details=details,
            retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            max_retries=5
        )


class PermissionError(OperationError):
    """Raised when operation lacks required permissions"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            code=ErrorCode.PERMISSION_ERROR,
            message=message,
            details=details,
            retry_strategy=RetryStrategy.NO_RETRY
        )


class SystemError(OperationError):
    """Raised when system-level errors occur"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            code=ErrorCode.SYSTEM_ERROR,
            message=message,
            details=details,
            retry_strategy=RetryStrategy.IMMEDIATE,
            max_retries=1
        )


class NetworkError(OperationError):
    """Raised when network-related errors occur"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            code=ErrorCode.NETWORK_ERROR,
            message=message,
            details=details,
            retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            max_retries=3
        )


class QueueError(OperationError):
    """Raised when queue-related errors occur"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            code=ErrorCode.QUEUE_ERROR,
            message=message,
            details=details,
            retry_strategy=RetryStrategy.LINEAR_BACKOFF,
            max_retries=2
        )
