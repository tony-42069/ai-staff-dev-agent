"""update datetime fields

Revision ID: update_datetime_fields
Revises: rename_metadata
Create Date: 2024-01-24 18:27:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = 'update_datetime_fields'
down_revision = 'rename_metadata'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # SQLite doesn't support altering columns directly, so we need to:
    # 1. Create new table with desired schema
    # 2. Copy data
    # 3. Drop old table
    # 4. Rename new table
    
    op.execute('''
        CREATE TABLE projects_new (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR NOT NULL,
            description VARCHAR,
            status VARCHAR DEFAULT 'active',
            project_metadata JSON DEFAULT '{}',
            agent_id VARCHAR(36) REFERENCES agents(id) ON DELETE SET NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    ''')
    
    # Copy data, ensuring datetime fields are set
    op.execute('''
        INSERT INTO projects_new (
            id, name, description, status, project_metadata, 
            agent_id, created_at, updated_at
        )
        SELECT 
            id, name, description, status, project_metadata,
            agent_id, 
            COALESCE(created_at, CURRENT_TIMESTAMP),
            COALESCE(updated_at, CURRENT_TIMESTAMP)
        FROM projects
    ''')
    
    # Drop old table
    op.drop_table('projects')
    
    # Rename new table to original name
    op.execute('ALTER TABLE projects_new RENAME TO projects')

def downgrade() -> None:
    # Create old table structure
    op.execute('''
        CREATE TABLE projects_old (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR NOT NULL,
            description VARCHAR,
            status VARCHAR DEFAULT 'active',
            project_metadata JSON DEFAULT '{}',
            agent_id VARCHAR(36) REFERENCES agents(id) ON DELETE SET NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
    ''')
    
    # Copy data back
    op.execute('''
        INSERT INTO projects_old (
            id, name, description, status, project_metadata,
            agent_id, created_at, updated_at
        )
        SELECT 
            id, name, description, status, project_metadata,
            agent_id, created_at, updated_at
        FROM projects
    ''')
    
    # Drop new table
    op.drop_table('projects')
    
    # Rename old table back
    op.execute('ALTER TABLE projects_old RENAME TO projects')
