from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.agent import Agent, AgentCreate, AgentUpdate
from app.models.database.agent import AgentModel

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

    def __init__(self, db: AsyncSession):
        self.db = db

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

    async def delete(self, agent_id: str) -> bool:
        """Delete an agent"""
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

            await self.db.delete(agent)
            await self.db.commit()
            return True
