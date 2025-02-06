"""Database models for agent data."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Boolean,
    JSON,
    ForeignKey,
    Table,
    Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...core.database import Base

agent_capability_association = Table(
    'agent_capability_association',
    Base.metadata,
    Column('agent_id', String, ForeignKey('agents.id')),
    Column('capability_name', String, ForeignKey('capabilities.name')),
)

class Agent(Base):
    """Database model for agent data."""
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String, default="inactive")
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_heartbeat = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False)
    version = Column(String, nullable=True)
    metadata = Column(JSON, default=dict)

    # Relationships
    capabilities = relationship(
        "Capability",
        secondary=agent_capability_association,
        back_populates="agents"
    )
    operations = relationship("Operation", back_populates="agent")
    metrics = relationship("AgentMetric", back_populates="agent")
    events = relationship("AgentEvent", back_populates="agent")
    maintenance_windows = relationship(
        "AgentMaintenanceWindow",
        back_populates="agent"
    )

    @hybrid_property
    def is_available(self) -> bool:
        """Check if agent is available for operations."""
        if not self.is_active:
            return False
        if not self.last_heartbeat:
            return False
        return (
            datetime.utcnow() - self.last_heartbeat
        ).total_seconds() < 60

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "registered_at": self.registered_at.isoformat(),
            "last_heartbeat": (
                self.last_heartbeat.isoformat()
                if self.last_heartbeat
                else None
            ),
            "is_active": self.is_active,
            "is_available": self.is_available,
            "version": self.version,
            "metadata": self.metadata,
            "capabilities": [cap.name for cap in self.capabilities]
        }

class Capability(Base):
    """Database model for agent capabilities."""
    __tablename__ = "capabilities"

    name = Column(String, primary_key=True)
    description = Column(Text, nullable=True)
    version = Column(String, nullable=True)
    parameters = Column(JSON, default=dict)
    required_resources = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)

    # Relationships
    agents = relationship(
        "Agent",
        secondary=agent_capability_association,
        back_populates="capabilities"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert capability to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "parameters": self.parameters,
            "required_resources": self.required_resources,
            "metadata": self.metadata
        }

class AgentMetric(Base):
    """Database model for agent metrics."""
    __tablename__ = "agent_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, ForeignKey("agents.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_type = Column(String)
    value = Column(JSON)
    metadata = Column(JSON, default=dict)

    # Relationships
    agent = relationship("Agent", back_populates="metrics")

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "metric_type": self.metric_type,
            "value": self.value,
            "metadata": self.metadata
        }

class AgentEvent(Base):
    """Database model for agent events."""
    __tablename__ = "agent_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, ForeignKey("agents.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)
    severity = Column(String, default="info")
    message = Column(Text)
    details = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)

    # Relationships
    agent = relationship("Agent", back_populates="events")

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
            "metadata": self.metadata
        }

class AgentMaintenanceWindow(Base):
    """Database model for agent maintenance windows."""
    __tablename__ = "agent_maintenance_windows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, ForeignKey("agents.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    type = Column(String)  # scheduled, emergency, update
    status = Column(String, default="scheduled")
    impact = Column(String, default="none")
    metadata = Column(JSON, default=dict)

    # Relationships
    agent = relationship("Agent", back_populates="maintenance_windows")

    def to_dict(self) -> Dict[str, Any]:
        """Convert maintenance window to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "type": self.type,
            "status": self.status,
            "impact": self.impact,
            "metadata": self.metadata
        }

class AgentResource(Base):
    """Database model for agent resources."""
    __tablename__ = "agent_resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, ForeignKey("agents.id"))
    name = Column(String)
    type = Column(String)  # cpu, memory, gpu, etc.
    total = Column(Integer)
    available = Column(Integer)
    reserved = Column(Integer)
    metadata = Column(JSON, default=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.type,
            "total": self.total,
            "available": self.available,
            "reserved": self.reserved,
            "metadata": self.metadata
        }
