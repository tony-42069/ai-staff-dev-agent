"""Create agent-related database tables.

Revision ID: create_agent_tables
Revises: add_agent_metadata_to_projects
Create Date: 2025-02-06 17:18:26.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'create_agent_tables'
down_revision = 'add_agent_metadata_to_projects'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default="inactive"),
        sa.Column('registered_at', sa.DateTime(), nullable=False),
        sa.Column('last_heartbeat', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=False),
        sa.Column('version', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, default=dict),
        sa.PrimaryKeyConstraint('id')
    )

    # Create capabilities table
    op.create_table(
        'capabilities',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=False, default=dict),
        sa.Column('required_resources', sa.JSON(), nullable=False, default=dict),
        sa.Column('metadata', sa.JSON(), nullable=False, default=dict),
        sa.PrimaryKeyConstraint('name')
    )

    # Create agent_capability_association table
    op.create_table(
        'agent_capability_association',
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('capability_name', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['capability_name'],
            ['capabilities.name'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('agent_id', 'capability_name')
    )

    # Create agent_metrics table
    op.create_table(
        'agent_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('metric_type', sa.String(), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False, default=dict),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create agent_events table
    op.create_table(
        'agent_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False, default="info"),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False, default=dict),
        sa.Column('metadata', sa.JSON(), nullable=False, default=dict),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create agent_maintenance_windows table
    op.create_table(
        'agent_maintenance_windows',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default="scheduled"),
        sa.Column('impact', sa.String(), nullable=False, default="none"),
        sa.Column('metadata', sa.JSON(), nullable=False, default=dict),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create agent_resources table
    op.create_table(
        'agent_resources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('total', sa.Integer(), nullable=False),
        sa.Column('available', sa.Integer(), nullable=False),
        sa.Column('reserved', sa.Integer(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False, default=dict),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(
        'ix_agents_status',
        'agents',
        ['status']
    )
    op.create_index(
        'ix_agents_is_active',
        'agents',
        ['is_active']
    )
    op.create_index(
        'ix_agent_metrics_timestamp',
        'agent_metrics',
        ['timestamp']
    )
    op.create_index(
        'ix_agent_events_timestamp',
        'agent_events',
        ['timestamp']
    )
    op.create_index(
        'ix_agent_maintenance_windows_start_time',
        'agent_maintenance_windows',
        ['start_time']
    )
    op.create_index(
        'ix_agent_maintenance_windows_end_time',
        'agent_maintenance_windows',
        ['end_time']
    )

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_agent_maintenance_windows_end_time')
    op.drop_index('ix_agent_maintenance_windows_start_time')
    op.drop_index('ix_agent_events_timestamp')
    op.drop_index('ix_agent_metrics_timestamp')
    op.drop_index('ix_agents_is_active')
    op.drop_index('ix_agents_status')

    # Drop tables
    op.drop_table('agent_resources')
    op.drop_table('agent_maintenance_windows')
    op.drop_table('agent_events')
    op.drop_table('agent_metrics')
    op.drop_table('agent_capability_association')
    op.drop_table('capabilities')
    op.drop_table('agents')
