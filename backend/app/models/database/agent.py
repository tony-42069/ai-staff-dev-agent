from sqlalchemy import Column, String, DateTime, func, JSON
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    capabilities = Column(JSON, default=list)
    status = Column(String, default="idle")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with projects
    projects = relationship("ProjectModel", back_populates="agent", cascade="all, delete-orphan")
