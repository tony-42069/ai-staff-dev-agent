from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.agent import Agent, AgentCreate, AgentUpdate
from app.models.agent_operations import (
    AssignToProjectRequest,
    ExecuteCapabilityRequest,
    OperationResponse,
    AgentOperation
)
from app.services.agent_service import AgentService, AgentNotFoundError, DuplicateAgentError
from app.core.database import get_db
from app.core.intelligence import get_core_intelligence

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/", response_model=List[Agent])
async def get_agents(db: AsyncSession = Depends(get_db)):
    """Get all agents"""
    service = AgentService(db)
    try:
        return await service.get_all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch agents: {str(e)}"
        )

@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new agent"""
    service = AgentService(db)
    try:
        return await service.create(agent)
    except DuplicateAgentError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get agent by ID"""
    service = AgentService(db)
    try:
        agent = await service.get_by_id(agent_id)
        if not agent:
            raise AgentNotFoundError(f"Agent with id {agent_id} not found")
        return agent
    except AgentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch agent: {str(e)}"
        )

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent: AgentUpdate, db: AsyncSession = Depends(get_db)):
    """Update an agent"""
    service = AgentService(db)
    try:
        updated_agent = await service.update(agent_id, agent)
        if not updated_agent:
            raise AgentNotFoundError(f"Agent with id {agent_id} not found")
        return updated_agent
    except AgentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicateAgentError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}"
        )

@router.post("/{agent_id}/assign", response_model=OperationResponse)
async def assign_to_project(
    agent_id: str,
    request: AssignToProjectRequest,
    db: AsyncSession = Depends(get_db)
):
    """Assign an agent to a project with specific capabilities"""
    service = AgentService(db)
    try:
        result = await service.assign_to_project(
            agent_id,
            request.project_id,
            request.capabilities
        )
        return OperationResponse(
            status="success",
            message=f"Agent {agent_id} assigned to project {request.project_id}",
            data=result
        )
    except AgentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign agent: {str(e)}"
        )

@router.post("/{agent_id}/execute", response_model=OperationResponse)
async def execute_capability(
    agent_id: str,
    request: ExecuteCapabilityRequest,
    db: AsyncSession = Depends(get_db),
    core = Depends(get_core_intelligence)
):
    """Execute an agent capability on a project"""
    service = AgentService(db, core)
    try:
        result = await service.execute_capability(
            agent_id,
            request.project_id,
            request.capability,
            request.parameters
        )
        return OperationResponse(
            status="success",
            message=f"Capability {request.capability} executed successfully",
            data=result
        )
    except AgentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute capability: {str(e)}"
        )

@router.get("/{agent_id}/operations/{project_id}", response_model=List[AgentOperation])
async def get_project_operations(
    agent_id: str,
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all operations performed by an agent on a project"""
    service = AgentService(db)
    try:
        return await service.get_project_operations(agent_id, project_id)
    except AgentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get operations: {str(e)}"
        )

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an agent"""
    service = AgentService(db)
    try:
        success = await service.delete(agent_id)
        if not success:
            raise AgentNotFoundError(f"Agent with id {agent_id} not found")
        return None
    except AgentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )
