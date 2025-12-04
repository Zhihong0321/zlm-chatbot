"""Redundant migration - columns already added in 002_add_mcp_schema

This migration is now deprecated as the MCP columns were properly added 
in the 002_add_mcp_schema migration. This file exists for migration
history compatibility but performs no operations.

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
    # NO OP - MCP columns were already added in 002_add_mcp_schema
    # This migration is kept for history but performs no operations
    pass


def downgrade() -> None:
    # NO OP - MCP columns are managed by 002_add_mcp_schema
    pass
