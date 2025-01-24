from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="active")
    project_metadata = Column(JSON, default=dict)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship with Agent
    agent = relationship("AgentModel", back_populates="projects")
