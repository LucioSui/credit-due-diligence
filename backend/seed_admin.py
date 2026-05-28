"""Seed script: create an initial admin user and all tables."""
import asyncio
import sys
import uuid
from datetime import datetime, timezone

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, ".")

from sqlalchemy import select, text

from auth.utils import hash_password
from config import settings
from database import AsyncSessionLocal, create_tables
from models.user import User, UserRole


async def main():
    # 1. Create all tables
    print("[1/3] Creating tables...")
    await create_tables()
    print("[OK] Tables created.")

    async with AsyncSessionLocal() as db:
        # 2. Check existing users
        result = await db.execute(text("SELECT id, username, role FROM users"))
        existing = result.fetchall()
        print(f"[2/3] Existing users: {len(existing)}")

        if existing:
            for row in existing:
                print(f"      {row[0]}  {row[1]}  {row[2]}")

        # 3. Create admin user if not exists
        check = await db.execute(
            select(User).where(User.username == "admin")
        )
        if check.scalar_one_or_none():
            print("[OK] Admin user already exists.")
        else:
            admin = User(
                id=uuid.uuid4(),
                username="admin",
                email="admin@diligence.com",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
                real_name="系统管理员",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            )
            db.add(admin)
            await db.commit()
            print("[OK] Created admin user: admin / admin123")

        # Final check
        result = await db.execute(text("SELECT id, username, role, is_active FROM users"))
        rows = result.fetchall()
        print(f"\n[Summary] Total users: {len(rows)}")
        for row in rows:
            print(f"  ID={row[0]}, username={row[1]}, role={row[2]}, active={row[3]}")


if __name__ == "__main__":
    asyncio.run(main())
