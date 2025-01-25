from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel


class OperationStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OperationPriority(str, Enum):
    HIGH = "high"
    NORMAL = "normal" 
    LOW = "low"


class Operation(BaseModel):
    id: str
    project_id: str
    agent_id: str
    capability: str
    status: OperationStatus
    priority: OperationPriority = OperationPriority.NORMAL
    progress: Optional[float] = 0
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class OperationMessage(BaseModel):
    type: str  # status, error, complete
    operation_id: str
    data: Dict[str, Any]


class OperationUpdate(BaseModel):
    operation_id: str
    status: Optional[OperationStatus] = None
    progress: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
