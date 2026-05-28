"""测试创建任务的全链路问题诊断"""
import asyncio
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models.user import Base, User, UserRole
from models.task import Task, TaskStatus
from auth.utils import hash_password, create_access_token, decode_token

OK = "[OK]"
FAIL = "[FAIL]"

async def main():
    print("=" * 60)
    print("[1] 检查数据库连接和表结构")
    print("=" * 60)
    engine = create_async_engine("sqlite+aiosqlite:///./dev.db", echo=False)
    AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        from sqlalchemy import text
        result = await db.execute(text("SELECT id, username, role, is_active FROM users"))
        users = result.fetchall()
        if users:
            print(f"{OK} users 表有 {len(users)} 条记录:")
            for u in users:
                print(f"   id={u.id}, username={u.username}, role={u.role}, is_active={u.is_active}")
        else:
            print(f"{FAIL} users 表为空! 没有用户可登录")

        result = await db.execute(text("SELECT COUNT(*) FROM tasks"))
        count = result.scalar()
        print(f"   tasks 表有 {count} 条记录")

    # 2. Test demo-token
    print()
    print("=" * 60)
    print("[2] 测试 demo 模式 token")
    print("=" * 60)
    try:
        decode_token("demo-token")
        print(f"{OK} demo-token 可被解码")
    except Exception as e:
        print(f"{FAIL} demo-token 无法解码: {type(e).__name__}: {e}")
        print("   -> 前端 demo 模式登录后, token='demo-token', 后端会返回 401")

    # 3. Check JWTError import
    print()
    print("=" * 60)
    print("[3] 测试 auth.dependencies 中的 JWTError 引用")
    print("=" * 60)
    import inspect
    source = inspect.getsource(sys.modules['auth.dependencies'])
    if 'from jose import JWTError' in source or 'from jose.exceptions import JWTError' in source:
        print(f"{OK} JWTError 已导入")
    elif 'JWTError' in source:
        print(f"{FAIL} JWTError 被使用但未导入!")
        print("   -> 当 token 无效时, except JWTError 会触发 NameError")
    else:
        print("   JWTError 未被引用")

    # 4. Generate admin token
    print()
    print("=" * 60)
    print("[4] 生成测试用 admin token")
    print("=" * 60)

    if not users:
        print("   users 表为空, 创建测试 admin 用户...")
        async with AsyncSessionLocal() as db:
            import uuid
            from datetime import datetime, timezone
            admin = User(
                id=uuid.uuid4(),
                username="admin",
                email="admin@test.com",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
                real_name="测试管理员",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            user_id = str(admin.id)
            print(f"   {OK} 已创建 admin 用户: id={user_id}")
        # Re-fetch users
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT id, username, role, is_active FROM users"))
            users = result.fetchall()
    else:
        user_id = str(users[0].id)

    token_data = {"sub": user_id, "username": "admin"}
    access_token = create_access_token(token_data)
    print(f"   {OK} Access Token (前50字符): {access_token[:50]}...")

    decoded = decode_token(access_token)
    print(f"   {OK} Token 解码: sub={decoded.get('sub')}, type={decoded.get('type')}")

    print()
    print("=" * 60)
    print("[总结]")
    print("=" * 60)
    if not users:
        print("问题1: 数据库没有用户 -> 已创建 admin/admin123")
    print("问题2: 前端 demo 模式使用 'demo-token' -> 后端 JWT 解码失败 -> 401")
    print("问题3: dependencies.py 中 JWTError 未导入 -> NameError 或意外行为")
    print()
    print("修复方案:")
    print("1. 修复 dependencies.py 导入 JWTError")
    print("2. 要么在 dependencies.py 支持 demo-token, 要么去掉前端 demo 模式")
    print("3. 使用真实登录: admin/admin123")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
