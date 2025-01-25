"""create project agent association table

Revision ID: create_project_agent_association
Revises: add_agent_metadata_to_projects
Create Date: 2025-01-24 20:36:41.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_project_agent_association'
down_revision = 'add_agent_metadata_to_projects'
branch_labels = None
depends_on = None

def upgrade():
    # Create project_agent_association table
    op.create_table(
        'project_agent_association',
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('agent_id', sa.String(36), sa.ForeignKey('agents.id', ondelete='CASCADE'), primary_key=True)
    )

    # Create indexes for better query performance
    op.create_index(
        'ix_project_agent_project_id',
        'project_agent_association',
        ['project_id']
    )
    op.create_index(
        'ix_project_agent_agent_id',
        'project_agent_association',
        ['agent_id']
    )

def downgrade():
    # Drop indexes first
    op.drop_index('ix_project_agent_agent_id')
    op.drop_index('ix_project_agent_project_id')
    
    # Drop the table
    op.drop_table('project_agent_association')
