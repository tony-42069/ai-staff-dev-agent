"""SQLAlchemy models for agent metrics."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship

from ...core.database import Base

class AgentMetric(Base):
    """SQLAlchemy model for agent metrics."""
    __tablename__ = "agent_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    metric_type = Column(String, nullable=False)
    value = Column(JSON, nullable=False)
    metric_metadata = Column(JSON, nullable=False, default=dict)

    # Relationships
    agent = relationship("Agent", back_populates="metrics")
