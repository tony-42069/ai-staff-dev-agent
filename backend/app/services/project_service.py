from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.project import Project, ProjectCreate, ProjectUpdate
from app.models.database.project import ProjectModel

class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Project]:
        result = await self.db.execute(select(ProjectModel))
        projects = result.scalars().all()
        return [Project.model_validate(project) for project in projects]

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        result = await self.db.execute(select(ProjectModel).filter(ProjectModel.id == project_id))
        project = result.scalar_one_or_none()
        return Project.model_validate(project) if project else None

    async def create(self, project_create: ProjectCreate) -> Project:
        project = ProjectModel(**project_create.model_dump())
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return Project.model_validate(project)

    async def update(self, project_id: UUID, project_update: ProjectUpdate) -> Optional[Project]:
        result = await self.db.execute(select(ProjectModel).filter(ProjectModel.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return None

        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        await self.db.commit()
        await self.db.refresh(project)
        return Project.model_validate(project)

    async def delete(self, project_id: UUID) -> bool:
        result = await self.db.execute(select(ProjectModel).filter(ProjectModel.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return False

        await self.db.delete(project)
        await self.db.commit()
        return True 