"""Add verification fields, related lost link, and notifications

Revision ID: a1b2c3d4e5f6
Revises: 93d0c13b4efc
Create Date: 2026-11-16 17:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "93d0c13b4efc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("reports", sa.Column("verification_question", sa.Text(), nullable=True))
    op.add_column("reports", sa.Column("verification_answer", sa.Text(), nullable=True))
    op.add_column("reports", sa.Column("related_lost_report_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_reports_related_lost_report_id"),
        "reports",
        ["related_lost_report_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_reports_related_lost_report_id",
        "reports",
        "reports",
        ["related_lost_report_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_constraint("fk_reports_related_lost_report_id", "reports", type_="foreignkey")
    op.drop_index(op.f("ix_reports_related_lost_report_id"), table_name="reports")
    op.drop_column("reports", "related_lost_report_id")
    op.drop_column("reports", "verification_answer")
    op.drop_column("reports", "verification_question")
