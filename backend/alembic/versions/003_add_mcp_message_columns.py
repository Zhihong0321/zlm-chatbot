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
    
    # Add tools_used column if it doesn't exist
    try:
        op.add_column('chat_messages', sa.Column('tools_used', sa.JSON(), nullable=True, comment='List of MCP tools used in this message'))
        print("✅ Added tools_used column to chat_messages")
    except sa.exc.ProgrammingError as e:
        if "already exists" in str(e):
            print("✅ tools_used column already exists in chat_messages")
        else:
            raise
    
    # Add mcp_server_responses column if it doesn't exist
    try:
        op.add_column('chat_messages', sa.Column('mcp_server_responses', sa.JSON(), nullable=True, comment='MCP server responses associated with this message'))
        print("✅ Added mcp_server_responses column to chat_messages")
    except sa.exc.ProgrammingError as e:
        if "already exists" in str(e):
            print("✅ mcp_server_responses column already exists in chat_messages")
        else:
            raise


def downgrade() -> None:
    # Remove the MCP columns (optional)
    op.drop_column('chat_messages', 'tools_used')
    op.drop_column('chat_messages', 'mcp_server_responses')
