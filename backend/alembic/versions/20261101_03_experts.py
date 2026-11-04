"""Tạo bảng chuyên gia và yêu cầu tư vấn."""

import sqlalchemy as sa
from alembic import op

revision = "20261101_03"
down_revision = "20261101_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "experts",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("organization", sa.String(200), nullable=False),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("bio", sa.Text(), nullable=False),
        sa.Column("specializations", sa.String(255), nullable=False),
        sa.Column("location", sa.String(100), nullable=False),
        sa.Column("experience_years", sa.Integer(), nullable=False),
        sa.Column("consultation_fee_text", sa.String(150), nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.create_index("ix_experts_is_verified", "experts", ["is_verified"])
    op.create_index("ix_experts_is_active", "experts", ["is_active"])
    op.create_table(
        "consultation_requests",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "expert_id",
            sa.UUID(),
            sa.ForeignKey("experts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column(
            "assessment_id",
            sa.UUID(),
            sa.ForeignKey("assessments.id", ondelete="SET NULL"),
        ),
        sa.Column("contact_name", sa.String(150), nullable=False),
        sa.Column("contact_phone", sa.String(50), nullable=False),
        sa.Column("contact_email", sa.String(150)),
        sa.Column("business_type", sa.String(100)),
        sa.Column("consultation_method", sa.String(50), server_default="online", nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), server_default="pending", nullable=False),
    )
    op.create_index("ix_consultation_requests_expert_id", "consultation_requests", ["expert_id"])
    op.create_index("ix_consultation_requests_user_id", "consultation_requests", ["user_id"])


def downgrade() -> None:
    op.drop_table("consultation_requests")
    op.drop_index("ix_experts_is_verified", table_name="experts")
    op.drop_index("ix_experts_is_active", table_name="experts")
    op.drop_table("experts")
