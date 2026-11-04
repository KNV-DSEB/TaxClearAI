"""Add partner classifications and consultation data snapshots."""

import sqlalchemy as sa
from alembic import op

revision = "20261104_01"
down_revision = "20261101_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "experts",
        sa.Column(
            "partner_type",
            sa.String(50),
            server_default="tax_consultant",
            nullable=False,
        ),
    )
    op.add_column(
        "experts",
        sa.Column("services_offered", sa.String(500), server_default="", nullable=False),
    )
    op.create_index("ix_experts_partner_type", "experts", ["partner_type"])
    op.add_column("consultation_requests", sa.Column("service_needed", sa.String(100)))
    op.add_column(
        "consultation_requests",
        sa.Column("share_data_consent", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.add_column("consultation_requests", sa.Column("data_snapshot", sa.Text()))


def downgrade() -> None:
    op.drop_column("consultation_requests", "data_snapshot")
    op.drop_column("consultation_requests", "share_data_consent")
    op.drop_column("consultation_requests", "service_needed")
    op.drop_index("ix_experts_partner_type", table_name="experts")
    op.drop_column("experts", "services_offered")
    op.drop_column("experts", "partner_type")
