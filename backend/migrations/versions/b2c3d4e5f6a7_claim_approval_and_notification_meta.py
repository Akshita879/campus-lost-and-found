"""Add claim approval statuses and notification metadata

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-11-16 17:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Expand claim status values (native_enum=False uses VARCHAR)
    op.add_column("notifications", sa.Column("kind", sa.String(length=50), nullable=True))
    op.add_column("notifications", sa.Column("claim_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_notifications_claim_id"), "notifications", ["claim_id"], unique=False)
    op.create_foreign_key(
        "fk_notifications_claim_id",
        "notifications",
        "claims",
        ["claim_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_notifications_claim_id", "notifications", type_="foreignkey")
    op.drop_index(op.f("ix_notifications_claim_id"), table_name="notifications")
    op.drop_column("notifications", "claim_id")
    op.drop_column("notifications", "kind")
