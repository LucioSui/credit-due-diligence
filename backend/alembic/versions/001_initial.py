"""initial tables

Revision ID: 001
Revises:
Create Date: 2026-05-28

"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("email", sa.String(128), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("role", sa.Enum("admin", "approver", "supervisor", "viewer", name="userrole"), nullable=False, server_default="viewer"),
        sa.Column("real_name", sa.String(64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # tasks
    op.create_table(
        "tasks",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("task_no", sa.String(32), nullable=False),
        sa.Column("company_name", sa.String(256), nullable=False),
        sa.Column("unified_credit_code", sa.String(20), nullable=True),
        sa.Column("status", sa.Enum("pending", "scanning", "completed", "expired", name="taskstatus"), nullable=False, server_default="pending"),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_no"),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_tasks_task_no"), "tasks", ["task_no"], unique=True)
    op.create_index(op.f("ix_tasks_unified_credit_code"), "tasks", ["unified_credit_code"], unique=False)

    # companies
    op.create_table(
        "companies",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_name", sa.String(256), nullable=False),
        sa.Column("unified_credit_code", sa.String(20), nullable=True),
        sa.Column("registration_no", sa.String(64), nullable=True),
        sa.Column("legal_rep", sa.String(64), nullable=True),
        sa.Column("registered_capital", sa.String(128), nullable=True),
        sa.Column("est_date", sa.DateTime(), nullable=True),
        sa.Column("company_status", sa.String(64), nullable=True),
        sa.Column("business_scope", sa.String(2048), nullable=True),
        sa.Column("address", sa.String(512), nullable=True),
        sa.Column("industry_info", sa.JSON(), nullable=True),
        sa.Column("cached_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_name"),
        sa.UniqueConstraint("unified_credit_code"),
    )
    op.create_index(op.f("ix_companies_company_name"), "companies", ["company_name"], unique=True)
    op.create_index(op.f("ix_companies_unified_credit_code"), "companies", ["unified_credit_code"], unique=True)

    # company_shareholders
    op.create_table(
        "company_shareholders",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("shareholder_name", sa.String(256), nullable=False),
        sa.Column("shareholder_type", sa.String(64), nullable=True),
        sa.Column("share_ratio", sa.Float(), nullable=True),
        sa.Column("subscribe_capital", sa.String(128), nullable=True),
        sa.Column("paid_in_capital", sa.String(128), nullable=True),
        sa.Column("pledge_ratio", sa.Float(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
    )

    # company_executives
    op.create_table(
        "company_executives",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("position", sa.String(128), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
    )

    # company_investments
    op.create_table(
        "company_investments",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("invested_company", sa.String(256), nullable=False),
        sa.Column("invest_ratio", sa.Float(), nullable=True),
        sa.Column("invest_amount", sa.String(128), nullable=True),
        sa.Column("invest_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(64), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
    )

    # company_risks
    op.create_table(
        "company_risks",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("risk_type", sa.Enum("lawsuit", "dishonest", "restriction", "penalty", "abnormal", "tax_abnormal", "bankruptcy", "pledge", "freeze", "other", name="risktype"), nullable=False),
        sa.Column("risk_level", sa.Enum("high", "medium", "low", name="risklevel"), nullable=False),
        sa.Column("risk_detail", sa.JSON(), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
    )

    # equity_chains
    op.create_table(
        "equity_chains",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("chain_type", sa.Enum("upward", "downward", "ubo", name="chaintype"), nullable=False),
        sa.Column("chain_depth", sa.Integer(), nullable=False),
        sa.Column("chain_data", sa.JSON(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
    )

    # rating_records
    op.create_table(
        "rating_records",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("grade", sa.Enum("A", "B", "C", "D", name="grade"), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("judicial_score", sa.Float(), nullable=False),
        sa.Column("financial_score", sa.Float(), nullable=False),
        sa.Column("credit_score", sa.Float(), nullable=False),
        sa.Column("operation_score", sa.Float(), nullable=False),
        sa.Column("equity_score", sa.Float(), nullable=False),
        sa.Column("compliance_score", sa.Float(), nullable=False),
        sa.Column("detail_breakdown", sa.JSON(), nullable=True),
        sa.Column("rated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
    )

    # report_snapshots
    op.create_table(
        "report_snapshots",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("report_content", sa.Text(), nullable=False),
        sa.Column("report_version", sa.String(32), nullable=True),
        sa.Column("pdf_url", sa.String(512), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
    )


def downgrade() -> None:
    op.drop_table("report_snapshots")
    op.drop_table("rating_records")
    op.drop_table("equity_chains")
    op.drop_table("company_risks")
    op.drop_table("company_investments")
    op.drop_table("company_executives")
    op.drop_table("company_shareholders")
    op.drop_table("companies")
    op.drop_table("tasks")
    op.drop_table("users")
