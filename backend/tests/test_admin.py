"""Integration tests for admin user management endpoints."""

import pytest

from auth.utils import hash_password

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def seeded_admin(client):
    """Ensure an admin user exists for login."""
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
    """Ensure an approver user exists for auth tests."""
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


@pytest.fixture
async def admin_client(client, seeded_admin):
    """Authenticated client with admin token."""
    resp = await client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


# ── TestListUsers ──────────────────────────────────────────────────────────


class TestListUsers:
    async def test_list_users_empty(self, admin_client):
        resp = await admin_client.get("/api/admin/users")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        # seeded_admin creates 1 user, so total >= 1
        assert data["data"]["total"] >= 1

    async def test_list_users_with_data(self, admin_client, seeded_admin):
        # Create an extra user
        await admin_client.post(
            "/api/admin/users",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "test123",
                "role": "approver",
                "real_name": "测试用户",
            },
        )

        resp = await admin_client.get("/api/admin/users")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 2  # admin + testuser
        assert len(data["data"]["items"]) == 2

    async def test_list_users_pagination(self, admin_client):
        resp = await admin_client.get("/api/admin/users?page=1&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 10

    async def test_list_users_without_auth(self, client):
        resp = await client.get("/api/admin/users")
        assert resp.status_code == 401


# ── TestCreateUser ─────────────────────────────────────────────────────────


class TestCreateUser:
    async def test_create_user_success(self, admin_client):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "pass123",
            "role": "approver",
            "real_name": "新用户",
        }
        resp = await admin_client.post("/api/admin/users", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "newuser"
        assert data["data"]["email"] == "new@example.com"
        assert data["data"]["role"] == "approver"
        assert data["data"]["is_active"] is True
        assert "id" in data["data"]

    async def test_create_user_default_role(self, admin_client):
        payload = {
            "username": "viewer1",
            "email": "viewer1@example.com",
            "password": "pass123",
        }
        resp = await admin_client.post("/api/admin/users", json=payload)
        assert resp.status_code == 200
        assert resp.json()["data"]["role"] == "viewer"

    async def test_create_user_duplicate_username(self, admin_client, seeded_admin):
        # admin user already exists
        resp = await admin_client.post(
            "/api/admin/users",
            json={
                "username": "admin",
                "email": "different@example.com",
                "password": "pass123",
            },
        )
        assert resp.status_code == 400

    async def test_create_user_duplicate_email(self, admin_client, seeded_admin):
        resp = await admin_client.post(
            "/api/admin/users",
            json={
                "username": "different",
                "email": "admin@example.com",
                "password": "pass123",
            },
        )
        assert resp.status_code == 400

    async def test_create_user_without_auth(self, client):
        resp = await client.post(
            "/api/admin/users",
            json={"username": "x", "email": "x@x.com", "password": "x"},
        )
        assert resp.status_code == 401


# ── TestUpdateUser ─────────────────────────────────────────────────────────


class TestUpdateUser:
    async def test_update_user_real_name(self, admin_client, seeded_admin):
        login = await admin_client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        user_id = login.json()["data"]["user"]["id"]

        resp = await admin_client.put(
            f"/api/admin/users/{user_id}",
            json={"real_name": "更新后的名字"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["real_name"] == "更新后的名字"

    async def test_update_user_role(self, admin_client, seeded_admin):
        login = await admin_client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        user_id = login.json()["data"]["user"]["id"]

        resp = await admin_client.put(
            f"/api/admin/users/{user_id}",
            json={"role": "supervisor"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["role"] == "supervisor"

    async def test_update_user_password(self, admin_client, seeded_approver):
        # Create a new user, change password, then login with new password
        create_resp = await admin_client.post(
            "/api/admin/users",
            json={
                "username": "pwtest",
                "email": "pwtest@example.com",
                "password": "oldpass",
            },
        )
        user_id = create_resp.json()["data"]["id"]

        # Update password
        await admin_client.put(
            f"/api/admin/users/{user_id}",
            json={"password": "newpass123"},
        )

        # Login with new password
        login_resp = await admin_client.post(
            "/api/auth/login",
            json={"username": "pwtest", "password": "newpass123"},
        )
        assert login_resp.status_code == 200

    async def test_update_user_not_found(self, admin_client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await admin_client.put(
            f"/api/admin/users/{fake_id}",
            json={"real_name": "xxx"},
        )
        assert resp.status_code == 404

    async def test_update_user_duplicate_email(self, admin_client, seeded_admin, seeded_approver):
        # Get admin user id
        login = await admin_client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        admin_id = login.json()["data"]["user"]["id"]

        # Try to change admin's email to approver's email
        resp = await admin_client.put(
            f"/api/admin/users/{admin_id}",
            json={"email": "approver@example.com"},
        )
        assert resp.status_code == 400


# ── TestDeleteUser ─────────────────────────────────────────────────────────


class TestDeleteUser:
    async def test_delete_user_success(self, admin_client):
        # Create a user first
        create_resp = await admin_client.post(
            "/api/admin/users",
            json={
                "username": "todelete",
                "email": "delete@example.com",
                "password": "pass123",
            },
        )
        user_id = create_resp.json()["data"]["id"]

        resp = await admin_client.delete(f"/api/admin/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

        # Verify user is deactivated (soft delete) by listing all users
        get_resp = await admin_client.get("/api/admin/users")
        assert get_resp.status_code == 200
        items = get_resp.json()["data"]["items"]
        deleted_user = next(u for u in items if u["id"] == user_id)
        assert deleted_user["is_active"] is False

    async def test_delete_user_not_found(self, admin_client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await admin_client.delete(f"/api/admin/users/{fake_id}")
        assert resp.status_code == 404

    async def test_delete_user_without_auth(self, client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.delete(f"/api/admin/users/{fake_id}")
        assert resp.status_code == 401
