"""Tạo bảng cho bản thử chuẩn bị hồ sơ; không chứa dữ liệu khách."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20261030_01"
down_revision = None
branch_labels = None
depends_on = None


def columns():
    return [sa.Column("id", sa.UUID(), primary_key=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)]


def upgrade():
    op.create_table("users", *columns(),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False))
    op.create_table("refresh_sessions", *columns(),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)))
    op.create_table("assessments", *columns(),
        sa.Column("owner_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("answers", postgresql.JSONB(), nullable=False),
        sa.Column("content_version", sa.String(80), nullable=False),
        sa.Column("summary_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("checklist_items", *columns(),
        sa.Column("assessment_id", sa.UUID(), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_code", sa.String(80), nullable=False),
        sa.Column("label_snapshot", sa.String(300), nullable=False),
        sa.Column("review_status", sa.String(20), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.UniqueConstraint("assessment_id", "item_code"),
        sa.CheckConstraint("status IN ('available','missing','needs_verification')",
                           name="checklist_items_status_check"),
        sa.CheckConstraint("review_status IN ('draft','approved')",
                           name="checklist_items_review_status_check"))
    for table, column in [("refresh_sessions", "user_id"), ("refresh_sessions", "expires_at"),
                          ("assessments", "owner_id"), ("assessments", "expires_at"),
                          ("checklist_items", "assessment_id")]:
        op.create_index(f"ix_{table}_{column}", table, [column])


def downgrade():
    for table in ("checklist_items", "assessments", "refresh_sessions", "users"):
        op.drop_table(table)
