from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from app.core.database import get_db
from app.models.project import Project, ProjectCreate, ProjectUpdate
from app.models.database.project import ProjectModel
from app.models.database.agent import AgentModel

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=Project)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify agent exists if agent_id is provided
    if project.agent_id:
        agent_query = select(AgentModel).where(AgentModel.id == project.agent_id)
        agent = await db.execute(agent_query)
        if not agent.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Agent not found")

    db_project = ProjectModel(**project.model_dump())
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

@router.get("", response_model=List[Project])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(active|completed|archived)$"),
    agent_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(ProjectModel)
    if status:
        query = query.where(ProjectModel.status == status)
    if agent_id:
        query = query.where(ProjectModel.agent_id == agent_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    query = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    # Verify project exists
    query = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify agent exists if agent_id is being updated
    if project_update.agent_id:
        agent_query = select(AgentModel).where(AgentModel.id == project_update.agent_id)
        agent = await db.execute(agent_query)
        if not agent.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Agent not found")

    # Update project
    update_data = project_update.model_dump(exclude_unset=True)
    update_query = (
        update(ProjectModel)
        .where(ProjectModel.id == project_id)
        .values(**update_data)
    )
    await db.execute(update_query)
    await db.commit()
    
    # Fetch updated project
    query = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await db.execute(query)
    return result.scalar_one()

@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Verify project exists
    query = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await db.execute(query)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete project
    delete_query = delete(ProjectModel).where(ProjectModel.id == project_id)
    await db.execute(delete_query)
    await db.commit()
