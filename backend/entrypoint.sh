#!/bin/bash
set -e

# Default to SQLite for local dev
: "${DATABASE_URL:=sqlite+aiosqlite:///./dev.db}"
export DATABASE_URL

# Check if using PostgreSQL (needs Alembic migrations) or SQLite (auto-create tables)
if echo "$DATABASE_URL" | grep -q "^sqlite"; then
    echo "SQLite detected — skipping Alembic migrations (tables auto-created by SQLAlchemy)."
else
    echo "PostgreSQL detected — waiting for database to be ready..."
    while ! python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from config import settings
async def check():
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            await conn.execute('SELECT 1')
        print('PostgreSQL is ready!')
    except Exception as e:
        print(f'Waiting... ({e})')
        raise
asyncio.run(check())
" 2>/dev/null; do
        sleep 2
    done

    echo "Running Alembic migrations..."
    alembic -c alembic.ini upgrade head
fi

echo "Starting Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
