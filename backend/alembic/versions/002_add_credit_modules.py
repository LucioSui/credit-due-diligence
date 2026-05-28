"""add credit module tables

Revision ID: 002
Revises: 001
Create Date: 2026-05-28

"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # company_financials
    op.create_table(
        "company_financials",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("balance_sheet", sa.JSON(), nullable=True),
        sa.Column("income_statement", sa.JSON(), nullable=True),
        sa.Column("cash_flow", sa.JSON(), nullable=True),
        sa.Column("key_indicators", sa.JSON(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
    )

    # uploaded_financial_reports
    op.create_table(
        "uploaded_financial_reports",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("report_type", sa.Enum("audit", "tax", "quarterly", name="reporttype"), nullable=False),
        sa.Column("report_period", sa.String(64), nullable=True),
        sa.Column("file_name", sa.String(256), nullable=False),
        sa.Column("file_path", sa.String(512), nullable=False),
        sa.Column("file_source", sa.Enum("pdf", "excel", name="filesource"), nullable=False),
        sa.Column("total_assets", sa.Float(), nullable=True),
        sa.Column("total_liabilities", sa.Float(), nullable=True),
        sa.Column("revenue", sa.Float(), nullable=True),
        sa.Column("net_profit", sa.Float(), nullable=True),
        sa.Column("operating_cash_flow", sa.Float(), nullable=True),
        sa.Column("parsed_data", sa.JSON(), nullable=True),
        sa.Column("parse_status", sa.Enum("pending", "parsed", "failed", name="parsestatus"), nullable=False, server_default="pending"),
        sa.Column("parse_error", sa.Text(), nullable=True),
        sa.Column("uploaded_by", sa.UUID(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
    )

    # bank_statements
    op.create_table(
        "bank_statements",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("account_no", sa.String(64), nullable=True),
        sa.Column("bank_name", sa.String(128), nullable=True),
        sa.Column("statement_source", sa.Enum("internal", "uploaded", name="statementsource"), nullable=False),
        sa.Column("file_name", sa.String(256), nullable=True),
        sa.Column("file_path", sa.String(512), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("total_inflow", sa.Float(), nullable=True),
        sa.Column("total_outflow", sa.Float(), nullable=True),
        sa.Column("avg_daily_balance", sa.Float(), nullable=True),
        sa.Column("ending_balance", sa.Float(), nullable=True),
        sa.Column("transaction_count", sa.Integer(), nullable=True),
        sa.Column("transaction_summary", sa.JSON(), nullable=True),
        sa.Column("anomaly_flags", sa.JSON(), nullable=True),
        sa.Column("parse_status", sa.Enum("pending", "parsed", "failed", name="bankstatementparsetatus"), nullable=False, server_default="pending"),
        sa.Column("uploaded_by", sa.UUID(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
    )

    # legal_person_credit
    op.create_table(
        "legal_person_credit",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("person_name", sa.String(128), nullable=False),
        sa.Column("person_id_type", sa.Enum("id_card", "unified_social_code", name="personidtype"), nullable=False),
        sa.Column("person_id_no", sa.String(64), nullable=False),
        sa.Column("credit_source", sa.Enum("uploaded", "manual", name="creditsource"), nullable=False),
        sa.Column("credit_rating", sa.Enum("good", "fair", "poor", name="creditrating"), nullable=True),
        sa.Column("loan_accounts", sa.JSON(), nullable=True),
        sa.Column("credit_card_accounts", sa.JSON(), nullable=True),
        sa.Column("guarantee_info", sa.JSON(), nullable=True),
        sa.Column("overdue_records", sa.JSON(), nullable=True),
        sa.Column("default_records", sa.JSON(), nullable=True),
        sa.Column("report_snapshot", sa.JSON(), nullable=True),
        sa.Column("report_file_path", sa.String(512), nullable=True),
        sa.Column("entered_by", sa.UUID(), nullable=False),
        sa.Column("entered_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["entered_by"], ["users.id"]),
    )

    # enterprise_credit
    op.create_table(
        "enterprise_credit",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("credit_source", sa.Enum("uploaded", "manual", name="creditsource"), nullable=False),
        sa.Column("total_credit_line", sa.Float(), nullable=True),
        sa.Column("used_credit_line", sa.Float(), nullable=True),
        sa.Column("remaining_credit_line", sa.Float(), nullable=True),
        sa.Column("loan_details", sa.JSON(), nullable=True),
        sa.Column("guarantee_out", sa.JSON(), nullable=True),
        sa.Column("guarantee_in", sa.JSON(), nullable=True),
        sa.Column("overdue_info", sa.JSON(), nullable=True),
        sa.Column("attention_list", sa.JSON(), nullable=True),
        sa.Column("multi_lending_flag", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("lender_count", sa.Integer(), nullable=True),
        sa.Column("report_snapshot", sa.JSON(), nullable=True),
        sa.Column("report_file_path", sa.String(512), nullable=True),
        sa.Column("entered_by", sa.UUID(), nullable=False),
        sa.Column("entered_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["entered_by"], ["users.id"]),
    )


def downgrade() -> None:
    op.drop_table("enterprise_credit")
    op.drop_table("legal_person_credit")
    op.drop_table("bank_statements")
    op.drop_table("uploaded_financial_reports")
    op.drop_table("company_financials")
