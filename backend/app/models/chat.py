from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from datetime import datetime

class ChatMessage(BaseModel):
    type: Literal["message", "command", "status"] = Field(...)
    content: str = Field(min_length=1)
    sender: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "message",
                "content": "Hello, how can I help?",
                "sender": "agent",
                "timestamp": "2024-01-23T20:44:00"
            }
        }
    )

class ChatRequest(BaseModel):
    type: Literal["message", "command"] = Field(...)
    content: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "message",
                "content": "Can you help me with a task?"
            }
        }
    )
