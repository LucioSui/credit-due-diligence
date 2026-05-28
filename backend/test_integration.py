"""Integration test: login -> create task (runs server inline)."""
import asyncio
import json
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, ".")

from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from main import app as fastapi_app
from auth.utils import hash_password, create_access_token
from database import AsyncSessionLocal
from models.user import User, UserRole
from models.task import Task


async def main():
    print("=" * 60)
    print("授信尽调系统 - 集成测试")
    print("=" * 60)

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # --- Test 1: Health check ---
        print("\n[测试 1] 健康检查...")
        r = await client.get("/api/health")
        assert r.status_code == 200, f"Health check failed: {r.status_code}"
        print(f"  [OK] 健康检查通过: {r.json()}")

        # --- Test 2: Login ---
        print("\n[测试 2] 登录...")
        r = await client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        if r.status_code == 200:
            data = r.json()
            token = data["data"]["access_token"]
            print(f"  [OK] 登录成功, token 长度: {len(token)}")
        else:
            print(f"  [FAIL] 登录失败: {r.status_code} - {r.text[:200]}")
            token = None

        # --- Test 3: Get current user ---
        if token:
            print("\n[测试 3] 获取当前用户...")
            r = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            if r.status_code == 200:
                user = r.json()["data"]
                print(f"  [OK] 用户: {user['username']} ({user['role']})")
            else:
                print(f"  [FAIL] 获取用户失败: {r.status_code} - {r.text[:200]}")

        # --- Test 4: Create task (with real JWT token) ---
        if token:
            print("\n[测试 4] 创建任务 (真实 JWT token)...")
            r = await client.post(
                "/api/tasks",
                json={"company_name": "测试科技有限公司", "unified_social_credit_code": "91110000MA0XXXXX1A"},
                headers={"Authorization": f"Bearer {token}"},
            )
            if r.status_code == 200:
                task = r.json()
                print(f"  [OK] 任务创建成功: {task['data']['company_name']} (ID: {task['data']['id']})")
            else:
                print(f"  [FAIL] 创建任务失败: {r.status_code} - {r.text[:300]}")

        # --- Test 5: Create task (with demo-token) ---
        print("\n[测试 5] 创建任务 (demo-token)...")
        r = await client.post(
            "/api/tasks",
            json={"company_name": "演示公司有限公司"},
            headers={"Authorization": "Bearer demo-token"},
        )
        if r.status_code == 200:
            task = r.json()
            print(f"  [OK] 任务创建成功: {task['data']['company_name']} (ID: {task['data']['id']})")
        else:
            print(f"  [FAIL] 创建任务失败: {r.status_code} - {r.text[:300]}")

        # --- Test 6: List tasks ---
        print("\n[测试 6] 获取任务列表...")
        r = await client.get("/api/tasks", headers={"Authorization": "Bearer demo-token"})
        if r.status_code == 200:
            result = r.json()
            tasks = result.get("data", {}).get("items", result.get("data", []))
            if isinstance(tasks, list):
                print(f"  [OK] 任务列表获取成功, 共 {len(tasks)} 条")
            else:
                print(f"  [OK] 任务列表响应: {json.dumps(result, ensure_ascii=False)[:200]}")
        else:
            print(f"  [FAIL] 获取任务列表失败: {r.status_code} - {r.text[:300]}")

        # --- Test 7: 401 without token ---
        print("\n[测试 7] 无 token 访问 (应返回 401)...")
        r = await client.get("/api/tasks")
        if r.status_code == 401:
            print(f"  [OK] 正确返回 401")
        else:
            print(f"  [WARN] 期望 401 但返回 {r.status_code}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
