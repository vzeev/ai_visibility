"""Add created_at to config model registry."""

from __future__ import annotations

from alembic import op

revision = "20260616_2018"
down_revision = "20260616_0924"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE config.model_registry
        ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now()
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE config.model_registry DROP COLUMN IF EXISTS created_at")
