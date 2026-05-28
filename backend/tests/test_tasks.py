"""Integration tests for task management endpoints."""

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


# ── TestCreateTask ─────────────────────────────────────────────────────────


class TestCreateTask:
    async def test_create_task_success(self, admin_client):
        payload = {
            "company_name": "腾讯科技(深圳)有限公司",
            "unified_credit_code": "91440300708460290H",
        }
        resp = await admin_client.post("/api/tasks", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        task_data = data["data"]
        assert task_data["company_name"] == "腾讯科技(深圳)有限公司"
        assert task_data["unified_credit_code"] == "91440300708460290H"
        assert task_data["status"] == "PENDING"
        assert task_data["progress"] == 0.0
        assert "task_id" in task_data
        assert task_data["task_no"].startswith("DD-")

    async def test_create_task_without_credit_code(self, admin_client):
        payload = {"company_name": "阿里巴巴集团"}
        resp = await admin_client.post("/api/tasks", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["company_name"] == "阿里巴巴集团"

    async def test_create_task_without_auth(self, client):
        resp = await client.post(
            "/api/tasks",
            json={"company_name": "某某公司"},
        )
        assert resp.status_code == 401


# ── TestListTasks ──────────────────────────────────────────────────────────


class TestListTasks:
    async def test_list_tasks_empty(self, admin_client):
        resp = await admin_client.get("/api/tasks")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []

    async def test_list_tasks_with_data(self, admin_client):
        # Create two tasks
        await admin_client.post(
            "/api/tasks",
            json={"company_name": "腾讯科技"},
        )
        await admin_client.post(
            "/api/tasks",
            json={"company_name": "阿里巴巴"},
        )

        resp = await admin_client.get("/api/tasks")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 2
        assert len(data["data"]["items"]) == 2

    async def test_list_tasks_filter_by_status(self, admin_client):
        await admin_client.post(
            "/api/tasks",
            json={"company_name": "腾讯科技"},
        )

        resp = await admin_client.get("/api/tasks?status=pending")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] == 1

        # Filter by non-existent status
        resp2 = await admin_client.get("/api/tasks?status=completed")
        assert resp2.status_code == 200
        assert resp2.json()["data"]["total"] == 0

    async def test_list_tasks_pagination(self, admin_client):
        resp = await admin_client.get("/api/tasks?page=1&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 10

    async def test_list_tasks_without_auth(self, client):
        resp = await client.get("/api/tasks")
        assert resp.status_code == 401


# ── TestGetTask ────────────────────────────────────────────────────────────


class TestGetTask:
    async def test_get_task_success(self, admin_client):
        create_resp = await admin_client.post(
            "/api/tasks",
            json={"company_name": "华为技术"},
        )
        task_id = create_resp.json()["data"]["task_id"]

        resp = await admin_client.get(f"/api/tasks/{task_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["task_id"] == task_id
        assert data["data"]["company_name"] == "华为技术"

    async def test_get_task_not_found(self, admin_client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await admin_client.get(f"/api/tasks/{fake_id}")
        assert resp.status_code == 404

    async def test_get_task_without_auth(self, client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.get(f"/api/tasks/{fake_id}")
        assert resp.status_code == 401


# ── TestStartScan ──────────────────────────────────────────────────────────


class TestStartScan:
    async def test_start_scan_success(self, admin_client):
        create_resp = await admin_client.post(
            "/api/tasks",
            json={"company_name": "百度科技"},
        )
        task_id = create_resp.json()["data"]["task_id"]

        resp = await admin_client.post(f"/api/tasks/{task_id}/scan")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "SCANNING"

    async def test_start_scan_not_found(self, admin_client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await admin_client.post(f"/api/tasks/{fake_id}/scan")
        assert resp.status_code == 404

    async def test_start_scan_without_auth(self, client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.post(f"/api/tasks/{fake_id}/scan")
        assert resp.status_code == 401


# ── TestScanProgress ───────────────────────────────────────────────────────


class TestScanProgress:
    async def test_get_scan_progress(self, admin_client):
        create_resp = await admin_client.post(
            "/api/tasks",
            json={"company_name": "字节跳动"},
        )
        task_id = create_resp.json()["data"]["task_id"]

        resp = await admin_client.get(f"/api/tasks/{task_id}/progress")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["task_id"] == task_id
        assert data["data"]["status"] == "PENDING"
        assert data["data"]["progress"] == 0.0
        assert "steps" in data["data"]
        # All steps should be undone at 0% progress
        assert all(not step["done"] for step in data["data"]["steps"])

    async def test_get_scan_progress_after_scan(self, admin_client):
        create_resp = await admin_client.post(
            "/api/tasks",
            json={"company_name": "美团"},
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Start scan (sets status to SCANNING, progress to 0)
        await admin_client.post(f"/api/tasks/{task_id}/scan")

        resp = await admin_client.get(f"/api/tasks/{task_id}/progress")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["status"] == "SCANNING"

    async def test_get_scan_progress_not_found(self, admin_client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await admin_client.get(f"/api/tasks/{fake_id}/progress")
        assert resp.status_code == 404

    async def test_get_scan_progress_without_auth(self, client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.get(f"/api/tasks/{fake_id}/progress")
        assert resp.status_code == 401
