"""Association table for the many-to-many relationship between projects and agents"""
from sqlalchemy import Column, String, ForeignKey, Table
from app.core.database import Base

project_agent_association = Table(
    'project_agent_association',
    Base.metadata,
    Column('project_id', String(36), ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
    Column('agent_id', String(36), ForeignKey('agents.id', ondelete='CASCADE'), primary_key=True)
)
