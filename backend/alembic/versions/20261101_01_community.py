"""Create community topics and questions."""

from alembic import op
import sqlalchemy as sa

revision = "20261101_01"
down_revision = "20261030_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "community_topics",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_community_topics_slug", "community_topics", ["slug"])
    op.create_table(
        "community_questions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("topic_id", sa.UUID(), sa.ForeignKey("community_topics.id"), nullable=False),
        sa.Column("author_name", sa.String(120), nullable=False),
        sa.Column("author_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("question_content", sa.Text(), nullable=False),
        sa.Column("answer_content", sa.Text()),
        sa.Column("answered_by", sa.String(120)),
        sa.Column("answered_at", sa.DateTime(timezone=True)),
        sa.Column("is_published", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_community_questions_topic_id", "community_questions", ["topic_id"])
    op.create_index("ix_community_questions_author_id", "community_questions", ["author_id"])
    op.create_index("ix_community_questions_is_published", "community_questions", ["is_published"])


def downgrade() -> None:
    op.drop_table("community_questions")
    op.drop_index("ix_community_topics_slug", table_name="community_topics")
    op.drop_table("community_topics")
