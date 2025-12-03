"""Rename metadata to file_metadata

Revision ID: fix_metadata_rename
Revises: add_session_fields
Create Date: 2025-12-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fix_metadata_rename'
down_revision = 'add_session_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Check if table exists first (to handle SQLite/Postgres differences or missing tables)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'agent_knowledge_files' in tables:
        columns = [c['name'] for c in inspector.get_columns('agent_knowledge_files')]
        
        if 'metadata' in columns and 'file_metadata' not in columns:
            print("Renaming metadata column to file_metadata")
            # For Postgres/SQLite that supports it
            with op.batch_alter_table('agent_knowledge_files') as batch_op:
                batch_op.alter_column('metadata', new_column_name='file_metadata')
        elif 'file_metadata' not in columns:
            print("Adding file_metadata column")
            op.add_column('agent_knowledge_files', sa.Column('file_metadata', sa.JSON(), nullable=True))
            
    else:
        print("Table agent_knowledge_files does not exist, creating it")
        # Create the table if it doesn't exist
        op.create_table('agent_knowledge_files',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('agent_id', sa.Integer(), nullable=False),
            sa.Column('zai_file_id', sa.String(length=255), nullable=False),
            sa.Column('filename', sa.String(length=255), nullable=False),
            sa.Column('original_filename', sa.String(length=255), nullable=False),
            sa.Column('file_size', sa.Integer(), nullable=True),
            sa.Column('file_type', sa.String(length=10), nullable=True),
            sa.Column('purpose', sa.String(length=20), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=True),
            sa.Column('file_metadata', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('zai_file_id')
        )
        op.create_index(op.f('ix_agent_knowledge_files_id'), 'agent_knowledge_files', ['id'], unique=False)


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'agent_knowledge_files' in tables:
        columns = [c['name'] for c in inspector.get_columns('agent_knowledge_files')]
        
        if 'file_metadata' in columns:
            with op.batch_alter_table('agent_knowledge_files') as batch_op:
                batch_op.alter_column('file_metadata', new_column_name='metadata')
