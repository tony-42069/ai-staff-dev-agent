"""Models for tracking operations and their status."""
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class OperationStatus(str, Enum):
    """Status of an operation."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    SUSPENDED = "suspended"

class OperationPriority(str, Enum):
    """Priority levels for operations."""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class OperationType(str, Enum):
    """Types of operations."""
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DEVELOPMENT = "development"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    PROJECT_GENERATION = "project_generation"
    AGENT_CREATION = "agent_creation"
    AGENT_ASSIGNMENT = "agent_assignment"
    RESOURCE_MANAGEMENT = "resource_management"
    SYSTEM_MAINTENANCE = "system_maintenance"

class Operation(BaseModel):
    """Model for tracking operations."""
    id: str
    project_id: str
    agent_id: str
    type: Optional[OperationType] = None
    capability: str
    status: OperationStatus
    priority: OperationPriority
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True

class OperationUpdate(BaseModel):
    """Model for updating operation status."""
    status: Optional[OperationStatus] = None
    progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class OperationFilter(BaseModel):
    """Model for filtering operations."""
    project_id: Optional[str] = None
    agent_id: Optional[str] = None
    type: Optional[OperationType] = None
    capability: Optional[str] = None
    status: Optional[OperationStatus] = None
    priority: Optional[OperationPriority] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class OperationMetrics(BaseModel):
    """Model for operation metrics."""
    total_operations: int = 0
    completed_operations: int = 0
    failed_operations: int = 0
    average_duration: float = 0.0
    success_rate: float = 0.0
    error_rate: float = 0.0
    average_progress: float = 0.0
    operations_by_status: Dict[str, int] = Field(default_factory=dict)
    operations_by_type: Dict[str, int] = Field(default_factory=dict)
    operations_by_priority: Dict[str, int] = Field(default_factory=dict)

class OperationDependency(BaseModel):
    """Model for operation dependencies."""
    operation_id: str
    dependent_id: str
    type: str
    required: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OperationStep(BaseModel):
    """Model for operation steps."""
    operation_id: str
    step_number: int
    name: str
    status: OperationStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OperationLog(BaseModel):
    """Model for operation logs."""
    operation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OperationResource(BaseModel):
    """Model for operation resource usage."""
    operation_id: str
    resource_type: str
    allocated: float
    used: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OperationSchedule(BaseModel):
    """Model for operation scheduling."""
    operation_id: str
    scheduled_start: datetime
    scheduled_end: Optional[datetime] = None
    recurrence: Optional[str] = None
    priority_override: Optional[OperationPriority] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OperationNotification(BaseModel):
    """Model for operation notifications."""
    operation_id: str
    type: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OperationStats(BaseModel):
    """Model for operation statistics."""
    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_duration: float = 0.0
    min_duration: float = 0.0
    max_duration: float = 0.0
    percentile_95_duration: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OperationQueue(BaseModel):
    """Model for operation queue status."""
    queue_name: str
    total_operations: int = 0
    active_operations: int = 0
    waiting_operations: int = 0
    completed_operations: int = 0
    failed_operations: int = 0
    average_wait_time: float = 0.0
    average_processing_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
