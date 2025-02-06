"""Models for agent-specific operations and capabilities."""
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from pydantic import BaseModel, Field

from .operations import (
    Operation,
    OperationStatus,
    OperationType,
    OperationPriority
)

class AgentCapability(BaseModel):
    """Model for agent capability definition."""
    name: str
    description: str
    version: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required_resources: Dict[str, float] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentOperation(Operation):
    """Model for agent-specific operation details."""
    capability_name: str
    capability_version: str
    resource_allocation: Dict[str, float] = Field(default_factory=dict)
    execution_stats: Dict[str, Any] = Field(default_factory=dict)
    dependencies_met: bool = True
    retry_count: int = 0
    last_error: Optional[str] = None
    checkpoints: List[Dict[str, Any]] = Field(default_factory=list)

class AgentStatus(BaseModel):
    """Model for agent status information."""
    agent_id: str
    status: str  # active, busy, unavailable, error
    last_heartbeat: datetime
    current_operations: List[str] = Field(default_factory=list)
    capabilities: Set[str] = Field(default_factory=set)
    resource_usage: Dict[str, float] = Field(default_factory=dict)
    error_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentResource(BaseModel):
    """Model for agent resource tracking."""
    name: str
    type: str  # cpu, memory, gpu, etc.
    total: float
    available: float
    reserved: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentMetrics(BaseModel):
    """Model for agent performance metrics."""
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    operations_completed: int = 0
    operations_failed: int = 0
    average_response_time: float = 0.0
    error_rate: float = 0.0
    resource_utilization: Dict[str, float] = Field(default_factory=dict)
    capability_metrics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

class AgentWorkload(BaseModel):
    """Model for agent workload tracking."""
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    active_operations: int = 0
    queued_operations: int = 0
    completed_operations: int = 0
    failed_operations: int = 0
    average_queue_time: float = 0.0
    average_processing_time: float = 0.0

class AgentCapabilityMetrics(BaseModel):
    """Model for capability-specific metrics."""
    capability_name: str
    invocations: int = 0
    successful_invocations: int = 0
    failed_invocations: int = 0
    average_execution_time: float = 0.0
    error_rate: float = 0.0
    resource_usage: Dict[str, float] = Field(default_factory=dict)
    last_execution: Optional[datetime] = None
    performance_stats: Dict[str, Any] = Field(default_factory=dict)

class AgentDependency(BaseModel):
    """Model for agent dependencies."""
    source_agent: str
    target_agent: str
    dependency_type: str
    required: bool = True
    status: str = "pending"  # pending, satisfied, failed
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentResourceRequest(BaseModel):
    """Model for resource allocation requests."""
    agent_id: str
    operation_id: str
    resources: Dict[str, float]
    priority: OperationPriority
    duration: Optional[float] = None
    flexible: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentResourceAllocation(BaseModel):
    """Model for resource allocation results."""
    request_id: str
    agent_id: str
    operation_id: str
    allocated_resources: Dict[str, float]
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "active"  # active, released, failed
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentCheckpoint(BaseModel):
    """Model for operation checkpoints."""
    operation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    step: str
    status: str
    progress: float
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentEvent(BaseModel):
    """Model for agent events."""
    agent_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: str = "info"  # info, warning, error, critical
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentLog(BaseModel):
    """Model for agent logs."""
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    message: str
    operation_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentSchedule(BaseModel):
    """Model for agent scheduling."""
    agent_id: str
    operation_id: str
    scheduled_start: datetime
    scheduled_end: Optional[datetime] = None
    priority: OperationPriority
    resources: Dict[str, float] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentMaintenanceWindow(BaseModel):
    """Model for agent maintenance windows."""
    agent_id: str
    start_time: datetime
    end_time: datetime
    type: str  # scheduled, emergency, update
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    impact: str = "none"  # none, low, medium, high
    metadata: Dict[str, Any] = Field(default_factory=dict)
