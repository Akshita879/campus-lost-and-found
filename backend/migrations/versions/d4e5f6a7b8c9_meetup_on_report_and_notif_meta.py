"""Add meetup on found reports and report_id on notifications

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-11-16 18:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("reports", sa.Column("meetup_message", sa.Text(), nullable=True))
    op.add_column("notifications", sa.Column("report_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_notifications_report_id"), "notifications", ["report_id"], unique=False)
    op.create_foreign_key(
        "fk_notifications_report_id",
        "notifications",
        "reports",
        ["report_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_notifications_report_id", "notifications", type_="foreignkey")
    op.drop_index(op.f("ix_notifications_report_id"), table_name="notifications")
    op.drop_column("notifications", "report_id")
    op.drop_column("reports", "meetup_message")
