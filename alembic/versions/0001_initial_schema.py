"""Initial schema — users_master, teacher_master (with user_id FK), teacher_notes

Revision ID: 0001
Revises:
Create Date: 2026-04-30

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users_master ──────────────────────────────────────────────────────────
    op.create_table(
        "users_master",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("teacher", "student", "parent", "admin", name="userrole"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index("ix_users_master_username", "users_master", ["username"], unique=True)
    op.create_index("ix_users_master_email", "users_master", ["email"], unique=True)

    # ── teacher_master (with user_id FK) ──────────────────────────────────────
    op.create_table(
        "teacher_master",
        sa.Column("teacher_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("avatar_initials", sa.String(5), nullable=True),
        sa.Column("subject", sa.String(100), nullable=True),
        sa.Column("class_assigned", sa.String(10), nullable=True),
        sa.Column("section", sa.String(10), nullable=True),
        sa.Column("school_name", sa.String(255), nullable=True),
        sa.Column("employee_code", sa.String(50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users_master.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("teacher_id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_teacher_master_user_id", "teacher_master", ["user_id"], unique=True)

    # ── teacher_notes (new table) ──────────────────────────────────────────────
    op.create_table(
        "teacher_notes",
        sa.Column("note_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("chapter", sa.String(255), nullable=False),
        sa.Column(
            "content_type",
            sa.Enum("typed", "voice", "handwritten", name="contenttype"),
            nullable=False,
            server_default="typed",
        ),
        sa.Column("canvas_image_url", sa.Text(), nullable=True),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="[]",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["teacher_id"], ["teacher_master.teacher_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("note_id"),
    )
    op.create_index("ix_teacher_notes_teacher_id", "teacher_notes", ["teacher_id"])


def downgrade() -> None:
    op.drop_index("ix_teacher_notes_teacher_id", table_name="teacher_notes")
    op.drop_table("teacher_notes")
    op.execute("DROP TYPE IF EXISTS contenttype")

    op.drop_index("ix_teacher_master_user_id", table_name="teacher_master")
    op.drop_table("teacher_master")

    op.drop_index("ix_users_master_email", table_name="users_master")
    op.drop_index("ix_users_master_username", table_name="users_master")
    op.drop_table("users_master")
    op.execute("DROP TYPE IF EXISTS userrole")
