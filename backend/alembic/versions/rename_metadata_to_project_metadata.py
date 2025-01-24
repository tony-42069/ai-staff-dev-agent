"""rename metadata to project_metadata

Revision ID: rename_metadata
Revises: initial_migration
Create Date: 2024-01-24 18:14:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'rename_metadata'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create new table with desired schema
    op.execute('''
        CREATE TABLE projects_new (
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
    
    # Copy data from old table to new table
    op.execute('''
        INSERT INTO projects_new (
            id, name, description, status, project_metadata, 
            agent_id, created_at, updated_at
        )
        SELECT 
            id, name, description, status, metadata,
            agent_id, created_at, updated_at
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
            metadata JSON DEFAULT '{}',
            agent_id VARCHAR(36) REFERENCES agents(id) ON DELETE SET NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        )
    ''')
    
    # Copy data back
    op.execute('''
        INSERT INTO projects_old (
            id, name, description, status, metadata,
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
