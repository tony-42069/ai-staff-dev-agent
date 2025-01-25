from sqlalchemy import Column, String, DateTime, JSON, func
from sqlalchemy.orm import relationship
import uuid
from typing import Dict, Any
from app.core.database import Base
from app.models.database.project_agent_association import project_agent_association

class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="active")
    project_metadata = Column(JSON, default=dict, nullable=False)
    agent_metadata = Column(JSON, nullable=False, default=lambda: {
        "assigned_agents": [],
        "capability_requirements": [],
        "operation_history": []
    })
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Many-to-many relationship with agents
    agents = relationship(
        "AgentModel",
        secondary=project_agent_association,
        back_populates="projects"
    )

    def add_agent(self, agent_id: str, capabilities: list[str]) -> None:
        """Add an agent with specific capabilities to the project"""
        if agent_id not in self.agent_metadata["assigned_agents"]:
            self.agent_metadata["assigned_agents"].append(agent_id)
            self.agent_metadata["capability_requirements"].extend(capabilities)

    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the project"""
        if agent_id in self.agent_metadata["assigned_agents"]:
            self.agent_metadata["assigned_agents"].remove(agent_id)

    def add_operation(self, agent_id: str, capability: str, result: Dict[str, Any]) -> None:
        """Record an agent operation in the project history"""
        operation = {
            "agent_id": agent_id,
            "capability": capability,
            "timestamp": func.now(),
            "status": "completed",
            "result": result
        }
        self.agent_metadata["operation_history"].append(operation)

    def add_failed_operation(self, agent_id: str, capability: str, error: str) -> None:
        """Record a failed agent operation in the project history"""
        operation = {
            "agent_id": agent_id,
            "capability": capability,
            "timestamp": func.now(),
            "status": "failed",
            "error": error
        }
        self.agent_metadata["operation_history"].append(operation)
