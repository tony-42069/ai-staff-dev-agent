"""Models for agent operations and project integration"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class AssignToProjectRequest(BaseModel):
    """Request model for assigning an agent to a project"""
    project_id: str
    capabilities: List[str]

class ExecuteCapabilityRequest(BaseModel):
    """Request model for executing an agent capability"""
    project_id: str
    capability: str
    parameters: Optional[Dict[str, Any]] = None

class OperationResponse(BaseModel):
    """Response model for agent operations"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class AgentOperation(BaseModel):
    """Model for an agent operation record"""
    agent_id: str
    capability: str
    timestamp: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
