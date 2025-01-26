from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.agent import Agent, AgentCreate, AgentUpdate
from app.models.database.agent import AgentModel
from app.models.database.project import ProjectModel
from app.core.intelligence import CoreIntelligence
from app.models.operations import Operation, OperationPriority, OperationStatus
from app.services.operation_queue import queue as operation_queue

class AgentServiceError(Exception):
    """Base exception for agent service errors"""
    pass

class AgentNotFoundError(AgentServiceError):
    """Raised when an agent is not found"""
    pass

class DuplicateAgentError(AgentServiceError):
    """Raised when attempting to create an agent with a duplicate name"""
    pass

class AgentService:
    VALID_CAPABILITIES = {
        "code_review",
        "testing",
        "development",
        "documentation",
        "deployment"
    }

    def __init__(self, db: AsyncSession, core: Optional[CoreIntelligence] = None):
        self.db = db
        self.core = core

    def _validate_capabilities(self, capabilities: List[str]) -> None:
        """Validate that all capabilities are recognized"""
        invalid_capabilities = set(capabilities) - self.VALID_CAPABILITIES
        if invalid_capabilities:
            raise ValueError(f"Invalid capabilities: {', '.join(invalid_capabilities)}")

    async def get_all(self) -> List[Agent]:
        """Get all agents"""
        result = await self.db.execute(select(AgentModel))
        agents = result.scalars().all()
        return [Agent.model_validate(agent) for agent in agents]

    async def get_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        try:
            UUID(agent_id)  # Validate UUID format
        except ValueError:
            raise ValueError(f"Invalid UUID format: {agent_id}")

        result = await self.db.execute(
            select(AgentModel).filter(AgentModel.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise AgentNotFoundError(f"Agent with id {agent_id} not found")
        
        return Agent.model_validate(agent)

    async def create(self, agent_create: AgentCreate) -> Agent:
        """Create a new agent"""
        # Validate capabilities
        self._validate_capabilities(agent_create.capabilities)

        # Check for duplicate name
        existing = await self.db.execute(
            select(AgentModel).filter(AgentModel.name == agent_create.name)
        )
        if existing.scalar_one_or_none():
            raise DuplicateAgentError(f"Agent with name '{agent_create.name}' already exists")

        try:
            agent = AgentModel(**agent_create.model_dump())
            self.db.add(agent)
            await self.db.commit()
            await self.db.refresh(agent)
            return Agent.model_validate(agent)
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateAgentError(f"Agent with name '{agent_create.name}' already exists")

    async def update(self, agent_id: str, agent_update: AgentUpdate) -> Agent:
        """Update an agent"""
        try:
            UUID(agent_id)  # Validate UUID format
        except ValueError:
            raise ValueError(f"Invalid UUID format: {agent_id}")

        # Start transaction
        async with self.db.begin():
            result = await self.db.execute(
                select(AgentModel).filter(AgentModel.id == agent_id)
            )
            agent = result.scalar_one_or_none()
            
            if not agent:
                raise AgentNotFoundError(f"Agent with id {agent_id} not found")

            # Prepare update data
            update_data = agent_update.model_dump(exclude_unset=True)
            
            # Validate capabilities if they're being updated
            if "capabilities" in update_data:
                self._validate_capabilities(update_data["capabilities"])

            # Check name uniqueness if name is being updated
            if "name" in update_data:
                name_check = await self.db.execute(
                    select(AgentModel).filter(
                        AgentModel.name == update_data["name"],
                        AgentModel.id != agent_id
                    )
                )
                if name_check.scalar_one_or_none():
                    raise DuplicateAgentError(f"Agent with name '{update_data['name']}' already exists")

            # Update fields
            for field, value in update_data.items():
                setattr(agent, field, value)
            
            # Update timestamp
            agent.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(agent)
            return Agent.model_validate(agent)

    async def assign_to_project(
        self,
        agent_id: str,
        project_id: str,
        capabilities: List[str]
    ) -> Dict[str, Any]:
        """Assign an agent to a project with specific capabilities"""
        async with self.db.begin():
            # Get agent and project
            agent = await self._get_agent(agent_id)
            project = await self._get_project(project_id)
            
            # Validate capabilities
            self._validate_capabilities(capabilities)
            for capability in capabilities:
                if not agent.has_capability(capability):
                    raise ValueError(f"Agent {agent_id} does not have capability: {capability}")
            
            # Add agent to project
            if project not in agent.projects:
                agent.projects.append(project)
            project.add_agent(agent_id, capabilities)
            
            await self.db.commit()
            return {
                "status": "success",
                "message": f"Agent {agent_id} assigned to project {project_id}"
            }

    async def execute_capability(
        self,
        agent_id: str,
        project_id: str,
        capability: str,
        params: Dict[str, Any] = None,
        priority: OperationPriority = OperationPriority.NORMAL
    ) -> str:
        """Queue an agent capability execution as an operation"""
        if not self.core:
            raise ValueError("CoreIntelligence not initialized")
            
        async with self.db.begin():
            # Get agent and project
            agent = await self._get_agent(agent_id)
            project = await self._get_project(project_id)
            
            # Validate capability
            if not agent.has_capability(capability):
                raise ValueError(f"Agent {agent_id} does not have capability: {capability}")
            
            # Validate assignment
            if project not in agent.projects:
                raise ValueError(f"Agent {agent_id} not assigned to project {project_id}")
            
            # Create operation
            operation = Operation(
                id=str(uuid4()),
                project_id=project_id,
                agent_id=agent_id,
                capability=capability,
                status=OperationStatus.QUEUED,
                priority=priority,
                metadata={
                    "parameters": params or {},
                    "agent_name": agent.name,
                    "project_name": project.name
                }
            )
            
            # Add to queue
            operation_id = await operation_queue.add_operation(operation)
            
            # Record operation in project
            project.add_operation(agent_id, capability, {"operation_id": operation_id})
            await self.db.commit()
            
            return operation_id

    async def _execute_operation(self, operation: Operation) -> Dict[str, Any]:
        """Internal method to execute an operation via core intelligence"""
        try:
            result = await self.core.execute_capability(
                operation.capability,
                {
                    "agent_id": operation.agent_id,
                    "project_id": operation.project_id,
                    "parameters": operation.metadata.get("parameters", {})
                }
            )
            return result
        except Exception as e:
            raise ValueError(f"Operation execution failed: {str(e)}")

    async def get_project_operations(
        self,
        agent_id: str,
        project_id: str
    ) -> List[Dict[str, Any]]:
        """Get all operations performed by an agent on a project"""
        agent = await self._get_agent(agent_id)
        operations = agent.get_project_operations(project_id)
        
        # Enrich with current operation status if available
        for op in operations:
            if "operation_id" in op:
                status = await operation_queue.get_operation_status(op["operation_id"])
                if status:
                    op["status"] = status.status
                    op["progress"] = status.progress
        
        return operations

    async def _get_agent(self, agent_id: str) -> AgentModel:
        """Get agent by ID or raise error"""
        try:
            UUID(agent_id)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {agent_id}")
            
        result = await self.db.execute(
            select(AgentModel).filter(AgentModel.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise AgentNotFoundError(f"Agent with id {agent_id} not found")
        return agent

    async def _get_project(self, project_id: str) -> ProjectModel:
        """Get project by ID or raise error"""
        try:
            UUID(project_id)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {project_id}")
            
        result = await self.db.execute(
            select(ProjectModel).filter(ProjectModel.id == project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project with id {project_id} not found")
        return project

    async def delete(self, agent_id: str) -> bool:
        """Delete an agent"""
        agent = await self._get_agent(agent_id)
        await self.db.delete(agent)
        await self.db.commit()
        return True
