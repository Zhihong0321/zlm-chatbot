"""Add missing MCP columns to chat_messages

Revision ID: 003_add_mcp_message_columns
Revises: fix_metadata_rename
Create Date: 2025-12-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_mcp_message_columns'
down_revision = 'fix_metadata_rename'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing MCP columns to chat_messages table
    conn = op.get_bind()
    
    # Check if tools_used column exists, if not add it
    try:
        conn.execute(sa.text("SELECT tools_used FROM chat_messages LIMIT 1"))
        print("tools_used column already exists")
    except:
        print("Adding tools_used column")
        op.add_column('chat_messages', sa.Column('tools_used', sa.JSON(), nullable=True, comment='List of MCP tools used in this message'))
    
    # Check if mcp_server_responses column exists, if not add it
    try:
        conn.execute(sa.text("SELECT mcp_server_responses FROM chat_messages LIMIT 1"))
        print("mcp_server_responses column already exists")
    except:
        print("Adding mcp_server_responses column")
        op.add_column('chat_messages', sa.Column('mcp_server_responses', sa.JSON(), nullable=True, comment='MCP server responses associated with this message'))


def downgrade() -> None:
    # Remove the MCP columns (optional)
    op.drop_column('chat_messages', 'tools_used')
    op.drop_column('chat_messages', 'mcp_server_responses')
