"""add agent metadata to projects

Revision ID: add_agent_metadata_to_projects
Revises: update_datetime_fields
Create Date: 2025-01-24 20:27:31.000000

"""
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
revision = 'add_agent_metadata_to_projects'
down_revision = 'update_datetime_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Add agent_metadata column with default structure
    op.add_column('projects', sa.Column('agent_metadata', sa.JSON, nullable=False, server_default=sa.text("""
    '{"assigned_agents": [], "capability_requirements": [], "operation_history": []}'
    """)))
    
    # SQLite doesn't support triggers for validation, we'll handle this in the application layer

def downgrade():
    op.drop_column('projects', 'agent_metadata')
