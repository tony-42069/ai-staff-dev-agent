from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="active", pattern=r"^(active|completed|archived)$")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    agent_id: Optional[str] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, pattern=r"^(active|completed|archived)$")

class Project(ProjectBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "AI Development Project",
                "description": "Building an AI-powered development assistant",
                "status": "active",
                "metadata": {
                    "priority": "high",
                    "tags": ["ai", "development"]
                },
                "agent_id": "987fcdeb-51a2-4bc1-9e3d-14af6324a326",
                "created_at": "2024-01-23T20:51:00",
                "updated_at": "2024-01-23T20:51:00"
            }
        }
    )
