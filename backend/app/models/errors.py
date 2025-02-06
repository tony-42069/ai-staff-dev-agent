"""Error models and handling for the application."""
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class ErrorCode(str, Enum):
    """Enumeration of error codes."""
    # General errors
    UNKNOWN = "UNKNOWN"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # Operation errors
    OPERATION_FAILED = "OPERATION_FAILED"
    OPERATION_TIMEOUT = "OPERATION_TIMEOUT"
    OPERATION_CANCELLED = "OPERATION_CANCELLED"
    OPERATION_NOT_SUPPORTED = "OPERATION_NOT_SUPPORTED"
    
    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_EXISTS = "RESOURCE_EXISTS"
    RESOURCE_BUSY = "RESOURCE_BUSY"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    
    # Agent errors
    AGENT_NOT_FOUND = "AGENT_NOT_FOUND"
    AGENT_UNAVAILABLE = "AGENT_UNAVAILABLE"
    AGENT_ERROR = "AGENT_ERROR"
    CAPABILITY_NOT_FOUND = "CAPABILITY_NOT_FOUND"
    
    # Project errors
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    PROJECT_EXISTS = "PROJECT_EXISTS"
    PROJECT_ERROR = "PROJECT_ERROR"
    
    # System errors
    SYSTEM_ERROR = "SYSTEM_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    FILE_SYSTEM_ERROR = "FILE_SYSTEM_ERROR"

class RetryStrategy(str, Enum):
    """Enumeration of retry strategies."""
    NO_RETRY = "NO_RETRY"
    IMMEDIATE = "IMMEDIATE"
    LINEAR_BACKOFF = "LINEAR_BACKOFF"
    EXPONENTIAL_BACKOFF = "EXPONENTIAL_BACKOFF"

class ErrorContext(BaseModel):
    """Context information for errors."""
    timestamp: datetime
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    details: Dict[str, Any] = {}

class OperationError(Exception):
    """Base class for operation errors."""
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.UNKNOWN,
        retry_strategy: RetryStrategy = RetryStrategy.NO_RETRY,
        max_retries: int = 0,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.retry_strategy = retry_strategy
        self.max_retries = max_retries
        self.context = ErrorContext(
            timestamp=datetime.utcnow(),
            details=context or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "retry_strategy": self.retry_strategy,
            "max_retries": self.max_retries,
            "context": self.context.dict()
        }

class ExecutionError(OperationError):
    """Error during operation execution."""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        max_retries: int = 3
    ):
        super().__init__(
            message,
            code=ErrorCode.OPERATION_FAILED,
            retry_strategy=retry_strategy,
            max_retries=max_retries,
            context={"details": details or {}}
        )

class TimeoutError(OperationError):
    """Operation timeout error."""
    def __init__(
        self,
        message: str,
        timeout: float,
        retry_strategy: RetryStrategy = RetryStrategy.LINEAR_BACKOFF,
        max_retries: int = 3
    ):
        super().__init__(
            message,
            code=ErrorCode.OPERATION_TIMEOUT,
            retry_strategy=retry_strategy,
            max_retries=max_retries,
            context={"timeout": timeout}
        )

class ResourceError(OperationError):
    """Resource-related error."""
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: str,
        retry_strategy: RetryStrategy = RetryStrategy.LINEAR_BACKOFF,
        max_retries: int = 3
    ):
        super().__init__(
            message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
            retry_strategy=retry_strategy,
            max_retries=max_retries,
            context={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )

class NetworkError(OperationError):
    """Network-related error."""
    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        max_retries: int = 5
    ):
        super().__init__(
            message,
            code=ErrorCode.NETWORK_ERROR,
            retry_strategy=retry_strategy,
            max_retries=max_retries,
            context={"endpoint": endpoint}
        )

class QueueError(OperationError):
    """Queue-related error."""
    def __init__(
        self,
        message: str,
        queue_name: str,
        retry_strategy: RetryStrategy = RetryStrategy.IMMEDIATE,
        max_retries: int = 3
    ):
        super().__init__(
            message,
            code=ErrorCode.RESOURCE_BUSY,
            retry_strategy=retry_strategy,
            max_retries=max_retries,
            context={"queue_name": queue_name}
        )

class ValidationError(OperationError):
    """Validation error."""
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        super().__init__(
            message,
            code=ErrorCode.VALIDATION_ERROR,
            retry_strategy=RetryStrategy.NO_RETRY,
            max_retries=0,
            context={
                "field": field,
                "value": value
            }
        )

class AgentError(OperationError):
    """Agent-related error."""
    def __init__(
        self,
        message: str,
        agent_id: str,
        capability: Optional[str] = None,
        retry_strategy: RetryStrategy = RetryStrategy.LINEAR_BACKOFF,
        max_retries: int = 3
    ):
        super().__init__(
            message,
            code=ErrorCode.AGENT_ERROR,
            retry_strategy=retry_strategy,
            max_retries=max_retries,
            context={
                "agent_id": agent_id,
                "capability": capability
            }
        )

class ProjectError(OperationError):
    """Project-related error."""
    def __init__(
        self,
        message: str,
        project_id: str,
        operation: Optional[str] = None,
        retry_strategy: RetryStrategy = RetryStrategy.LINEAR_BACKOFF,
        max_retries: int = 3
    ):
        super().__init__(
            message,
            code=ErrorCode.PROJECT_ERROR,
            retry_strategy=retry_strategy,
            max_retries=max_retries,
            context={
                "project_id": project_id,
                "operation": operation
            }
        )
