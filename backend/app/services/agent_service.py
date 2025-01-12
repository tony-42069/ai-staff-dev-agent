from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.agent import Agent, AgentCreate, AgentUpdate
from app.models.database.agent import AgentModel

class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Agent]:
        result = await self.db.execute(select(AgentModel))
        agents = result.scalars().all()
        return [Agent.model_validate(agent) for agent in agents]

    async def get_by_id(self, agent_id: UUID) -> Optional[Agent]:
        result = await self.db.execute(select(AgentModel).filter(AgentModel.id == agent_id))
        agent = result.scalar_one_or_none()
        return Agent.model_validate(agent) if agent else None

    async def create(self, agent_create: AgentCreate) -> Agent:
        agent = AgentModel(**agent_create.model_dump())
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return Agent.model_validate(agent)

    async def update(self, agent_id: UUID, agent_update: AgentUpdate) -> Optional[Agent]:
        result = await self.db.execute(select(AgentModel).filter(AgentModel.id == agent_id))
        agent = result.scalar_one_or_none()
        if not agent:
            return None

        update_data = agent_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)

        await self.db.commit()
        await self.db.refresh(agent)
        return Agent.model_validate(agent)

    async def delete(self, agent_id: UUID) -> bool:
        result = await self.db.execute(select(AgentModel).filter(AgentModel.id == agent_id))
        agent = result.scalar_one_or_none()
        if not agent:
            return False

        await self.db.delete(agent)
        await self.db.commit()
        return True 