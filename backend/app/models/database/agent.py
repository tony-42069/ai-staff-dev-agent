from sqlalchemy import Column, String, DateTime, JSON, func
from sqlalchemy.orm import relationship
import uuid
from typing import List, Dict, Any
from app.core.database import Base
from app.models.database.project_agent_association import project_agent_association

class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    capabilities = Column(JSON, default=list, nullable=False)
    status = Column(String, default="idle")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Many-to-many relationship with projects
    projects = relationship(
        "ProjectModel",
        secondary=project_agent_association,
        back_populates="agents"
    )

    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities

    def add_capability(self, capability: str, metadata: Dict[str, Any] = None) -> None:
        """Add a new capability to the agent"""
        if not self.capabilities:
            self.capabilities = []
        if capability not in self.capabilities:
            if metadata:
                self.capabilities.append({"name": capability, "metadata": metadata})
            else:
                self.capabilities.append(capability)

    def remove_capability(self, capability: str) -> None:
        """Remove a capability from the agent"""
        if isinstance(self.capabilities[0], dict):
            self.capabilities = [cap for cap in self.capabilities if cap["name"] != capability]
        else:
            self.capabilities = [cap for cap in self.capabilities if cap != capability]

    def get_project_operations(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all operations performed by this agent on a specific project"""
        for project in self.projects:
            if project.id == project_id:
                return [
                    op for op in project.agent_metadata["operation_history"]
                    if op["agent_id"] == self.id
                ]
        return []
