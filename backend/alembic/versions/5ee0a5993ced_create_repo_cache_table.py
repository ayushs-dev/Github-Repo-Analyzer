"""create repo_cache table

Revision ID: 5ee0a5993ced
Revises:
Create Date: 2026-03-22 00:59:21.944494

This is the very first migration — it creates the repo_cache table from scratch.
Alembic auto-generated this by comparing our SQLAlchemy model (RepoCache)
to an empty database and figuring out what SQL was needed.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Alembic uses these IDs to track which migrations have been applied.
# revision = this migration's unique ID
# down_revision = the ID of the migration that must run before this one (None = first migration)
revision: str = '5ee0a5993ced'
down_revision: Union[str, None] = None   # no previous migration — this is the first one
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Runs when you apply this migration (e.g. `alembic upgrade head`).
    Creates the repo_cache table with all its columns.
    """
    op.create_table(
        'repo_cache',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),   # auto-incrementing primary key
        sa.Column('full_name', sa.String(), nullable=False),                  # e.g. "torvalds/linux"
        sa.Column('data', sa.JSON(), nullable=False),                         # the full GitHub API response
        sa.Column('fetched_at', sa.DateTime(), nullable=False),               # when the cache entry was created/updated
        sa.PrimaryKeyConstraint('id')
    )
    # Create a unique index on full_name for fast lookups.
    # unique=True also enforces that no two rows can have the same repo name.
    op.create_index(op.f('ix_repo_cache_full_name'), 'repo_cache', ['full_name'], unique=True)


def downgrade() -> None:
    """
    Runs when you roll back this migration (e.g. `alembic downgrade -1`).
    Undoes everything upgrade() did — drops the index first, then the table.
    (You must drop the index before the table, otherwise it throws an error.)
    """
    op.drop_index(op.f('ix_repo_cache_full_name'), table_name='repo_cache')
    op.drop_table('repo_cache')
