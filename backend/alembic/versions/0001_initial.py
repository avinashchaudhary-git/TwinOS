"""Initial migration creating all TwinOS relational schema tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-06 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "organization_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("firebase_uid", sa.String(255), nullable=True, unique=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_org", "users", ["organization_id"])

    # employee_aliases
    op.create_table(
        "employee_aliases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.UniqueConstraint("platform", "external_id", name="uq_platform_external_id"),
    )

    # platform_connections
    op.create_table(
        "platform_connections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "organization_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("oauth_token_ref", sa.Text(), nullable=True),
        sa.Column("scopes", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(50), server_default="connected"),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "platform", name="uq_user_platform"),
    )

    # sync_runs
    op.create_table(
        "sync_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "connection_id",
            sa.String(36),
            sa.ForeignKey("platform_connections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), server_default="running"),
        sa.Column("records_pulled", sa.Integer(), server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
    )

    # staging_records
    op.create_table(
        "staging_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint(
            "platform", "entity_type", "external_id", "content_hash", name="uq_staging_record"
        ),
    )
    op.create_index("idx_staging_status", "staging_records", ["status"])
    op.create_index("idx_staging_org", "staging_records", ["organization_id"])

    # risk_scores
    op.create_table(
        "risk_scores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("entity_type", sa.String(20), nullable=False),
        sa.Column("entity_id", sa.String(255), nullable=False),
        sa.Column("score", sa.Numeric(4, 3), nullable=False),
        sa.Column("band", sa.String(20), nullable=False),
        sa.Column("confidence", sa.String(20), server_default="normal"),
        sa.Column("top_factors", sa.JSON(), nullable=True),
        sa.Column("model_version", sa.String(50), server_default="1.0.0"),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "idx_risk_entity_computed", "risk_scores", ["entity_type", "entity_id", "computed_at"]
    )

    # risk_config
    op.create_table(
        "risk_config",
        sa.Column("organization_id", sa.String(36), primary_key=True),
        sa.Column("medium_threshold", sa.Numeric(4, 3), server_default="0.35"),
        sa.Column("high_threshold", sa.Numeric(4, 3), server_default="0.60"),
        sa.Column("critical_threshold", sa.Numeric(4, 3), server_default="0.80"),
        sa.Column("min_history_days", sa.Integer(), server_default="14"),
        sa.Column("sync_interval_minutes", sa.Integer(), server_default="15"),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column(
            "recipient_user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(255), nullable=False),
        sa.Column("from_band", sa.String(20), nullable=True),
        sa.Column("to_band", sa.String(20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_alerts_recipient", "alerts", ["recipient_user_id"])

    # audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("actor_id", sa.String(36), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_entity", sa.String(100), nullable=True),
        sa.Column("target_id", sa.String(255), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_audit_actor", "audit_log", ["actor_id"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("alerts")
    op.drop_table("risk_config")
    op.drop_table("risk_scores")
    op.drop_table("staging_records")
    op.drop_table("sync_runs")
    op.drop_table("platform_connections")
    op.drop_table("employee_aliases")
    op.drop_table("users")
    op.drop_table("organizations")
