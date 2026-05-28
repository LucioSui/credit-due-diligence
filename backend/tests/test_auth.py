"""Integration tests for authentication endpoints."""

import pytest

from auth.utils import hash_password

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def seeded_admin(client):
    """Create a seed admin user before each test that needs login."""
    from sqlalchemy import select
    from models.user import User, UserRole
    import database

    async with database.AsyncSessionLocal() as session:
        existing = await session.execute(select(User).where(User.username == "admin"))
        if existing.scalar_one_or_none() is None:
            session.add(
                User(
                    username="admin",
                    email="admin@example.com",
                    password_hash=hash_password("admin123"),
                    role=UserRole.ADMIN,
                    real_name="测试管理员",
                )
            )
            await session.commit()


@pytest.fixture
async def seeded_approver(client):
    """Create a seed approver user."""
    from sqlalchemy import select
    from models.user import User, UserRole
    import database

    async with database.AsyncSessionLocal() as session:
        existing = await session.execute(select(User).where(User.username == "approver"))
        if existing.scalar_one_or_none() is None:
            session.add(
                User(
                    username="approver",
                    email="approver@example.com",
                    password_hash=hash_password("approver123"),
                    role=UserRole.APPROVER,
                    real_name="审批员",
                )
            )
            await session.commit()


class TestLogin:
    async def test_login_success(self, client, seeded_admin):
        resp = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["username"] == "admin"

    async def test_login_wrong_password(self, client, seeded_admin):
        resp = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong"},
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client):
        resp = await client.post(
            "/api/auth/login",
            json={"username": "ghost", "password": "xxx"},
        )
        assert resp.status_code == 401


class TestRefresh:
    async def test_refresh_success(self, client, seeded_admin):
        login = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        refresh_token = login.json()["data"]["refresh_token"]

        resp = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]

    async def test_refresh_invalid_token(self, client):
        resp = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        assert resp.status_code == 401


class TestMe:
    async def test_me_returns_user_info(self, client, seeded_admin):
        login = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        token = login.json()["data"]["access_token"]

        resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["username"] == "admin"

    async def test_me_without_token(self, client):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401


class TestLogout:
    async def test_logout_success(self, client, seeded_admin):
        login = await client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        token = login.json()["data"]["access_token"]

        resp = await client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["code"] == 0
