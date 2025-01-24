from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class AgentBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    capabilities: list[str] = Field(default_factory=list)
    status: str = Field(default="idle", pattern=r"^(idle|busy|error)$")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, pattern=r"^(idle|busy|error)$")

class Agent(AgentBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Development Agent",
                "description": "Handles development tasks",
                "capabilities": ["code_review", "testing"],
                "status": "idle",
                "created_at": "2024-01-23T20:43:00",
                "updated_at": "2024-01-23T20:43:00"
            }
        }
    )
