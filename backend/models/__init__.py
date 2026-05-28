"""Models package - imports all model classes for Alembic autodetection."""

from .user import Base, User, UserRole
from .task import Task, TaskStatus
from .company import (
    Company,
    CompanyShareholder,
    CompanyExecutive,
    CompanyInvestment,
)
from .company_risk import CompanyRisk, RiskType, RiskLevel
from .company_financial import CompanyFinancial
from .financial_report import (
    UploadedFinancialReport,
    ReportType,
    FileSource,
    ParseStatus,
)
from .bank_statement import BankStatement, StatementSource, BankStatementParseStatus
from .credit import (
    LegalPersonCredit,
    EnterpriseCredit,
    PersonIdType,
    CreditSource,
    CreditRating,
)
from .equity import EquityChain, ChainType
from .rating import RatingRecord, Grade
from .report import ReportSnapshot

__all__ = [
    # Base
    "Base",
    # Enums
    "UserRole",
    "TaskStatus",
    "RiskType",
    "RiskLevel",
    "ReportType",
    "FileSource",
    "ParseStatus",
    "StatementSource",
    "BankStatementParseStatus",
    "PersonIdType",
    "CreditSource",
    "CreditRating",
    "ChainType",
    "Grade",
    # Models
    "User",
    "Task",
    "Company",
    "CompanyShareholder",
    "CompanyExecutive",
    "CompanyInvestment",
    "CompanyRisk",
    "CompanyFinancial",
    "UploadedFinancialReport",
    "BankStatement",
    "LegalPersonCredit",
    "EnterpriseCredit",
    "EquityChain",
    "RatingRecord",
    "ReportSnapshot",
]
