"""add agent metadata to projects

Revision ID: add_agent_metadata_to_projects
Revises: update_datetime_fields
Create Date: 2025-01-24 20:27:31.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'add_agent_metadata_to_projects'
down_revision = 'update_datetime_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Add agent_metadata column with default structure
    op.add_column('projects', sa.Column('agent_metadata', JSONB, nullable=False, server_default=sa.text("""
    '{
        "assigned_agents": [],
        "capability_requirements": [],
        "operation_history": []
    }'::jsonb
    """)))
    
    # Add validation trigger
    op.execute("""
    CREATE OR REPLACE FUNCTION validate_agent_metadata()
    RETURNS trigger AS $$
    BEGIN
        IF NOT (
            NEW.agent_metadata ? 'assigned_agents' AND
            NEW.agent_metadata ? 'capability_requirements' AND
            NEW.agent_metadata ? 'operation_history'
        ) THEN
            RAISE EXCEPTION 'Invalid agent_metadata structure';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER ensure_valid_agent_metadata
    BEFORE INSERT OR UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION validate_agent_metadata();
    """)

def downgrade():
    op.execute("DROP TRIGGER IF EXISTS ensure_valid_agent_metadata ON projects")
    op.execute("DROP FUNCTION IF EXISTS validate_agent_metadata")
    op.drop_column('projects', 'agent_metadata')
