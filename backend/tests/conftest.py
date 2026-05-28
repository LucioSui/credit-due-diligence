"""Shared pytest fixtures for integration testing.

Uses an in-memory SQLite database and httpx AsyncClient against the FastAPI app.
"""

import asyncio
import sys
import tempfile
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── Test database engine ──────────────────────────────────────────────────

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, echo=False, future=True)
TestSession = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    """Create all tables before each test and tear them down afterwards."""
    from models import Base  # noqa: F401
    from models.user import User, UserRole
    from models.task import Task, TaskStatus
    from models.company import Company, CompanyShareholder, CompanyExecutive, CompanyInvestment
    from models.company_risk import CompanyRisk, RiskType, RiskLevel
    from models.company_financial import CompanyFinancial
    from models.financial_report import UploadedFinancialReport, ReportType, FileSource, ParseStatus
    from models.bank_statement import BankStatement, StatementSource, BankStatementParseStatus
    from models.credit import LegalPersonCredit, EnterpriseCredit, PersonIdType, CreditSource, CreditRating
    from models.equity import EquityChain, ChainType
    from models.rating import RatingRecord, Grade
    from models.report import ReportSnapshot

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── Override FastAPI dependencies for testing ──────────────────────────────

from database import get_db as real_get_db


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Test database dependency override — uses in-memory SQLite."""
    async with TestSession() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(autouse=True)
def _override_db_dependency():
    """Automatically override the DB dependency for all tests."""
    import database

    original_get_db = database.get_db
    original_session = database.AsyncSessionLocal
    database.get_db = override_get_db
    database.AsyncSessionLocal = TestSession
    yield
    database.get_db = original_get_db
    database.AsyncSessionLocal = original_session


# ── FastAPI ASGI app ──────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provides an httpx AsyncClient connected to the test FastAPI app."""
    # Must import *after* db override is in place (handled by autouse fixture)
    from main import app

    # Override lifespan to skip production startup
    @asynccontextmanager
    async def test_lifespan(_app):
        import os
        os.makedirs("uploads", exist_ok=True)
        yield

    app.lifespan = test_lifespan

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ── Auth helper ───────────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="function")
async def admin_token(client: AsyncClient) -> str:
    """Login as admin and return the access token."""
    resp = await client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    return data["data"]["access_token"]


@pytest_asyncio.fixture(scope="function")
async def admin_client(client: AsyncClient, admin_token: str) -> AsyncClient:
    """Client pre-authenticated as admin."""
    client.headers["Authorization"] = f"Bearer {admin_token}"
    return client
