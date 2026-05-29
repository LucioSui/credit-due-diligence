#!/bin/bash
set -e

# Resolve project root (parent of .devcontainer)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "========================================="
echo "  Credit Due Diligence - Codespaces Setup"
echo "  Project root: $PROJECT_ROOT"
echo "========================================="

# Install frontend dependencies
echo ""
echo "[1/2] Installing frontend dependencies..."
cd "$PROJECT_ROOT/frontend"
npm ci --legacy-peer-deps || npm install --legacy-peer-deps
echo "✓ Frontend dependencies installed"

# Setup backend environment
echo ""
echo "[2/2] Configuring backend environment..."
cd "$PROJECT_ROOT/backend"

# Create .env if not present (will be ignored by .gitignore)
if [ ! -f .env ]; then
    echo "Creating .env for development..."
    SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(48))")
    FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

    cat > .env << ENVEOF
# === Security ===
SECRET_KEY=${SECRET_KEY}
FERNET_KEY=${FERNET_KEY}

# === Database ===
DATABASE_URL=sqlite+aiosqlite:///./dev.db

# === Redis ===
REDIS_URL=redis://localhost:6379/0

# === JWT ===
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# === QCC API ===
QCC_API_KEY=
QCC_API_BASE_URL=https://api.qcc.com

# === App ===
DEBUG=true
ENABLE_DEMO_MODE=true

# === CORS ===
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# === File Upload ===
MAX_FILE_SIZE=52428800
UPLOAD_DIR=uploads

# === Celery ===
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
ENVEOF
    echo "✓ .env created with generated keys"
else
    echo "✓ .env already exists, skipping"
fi

# Create uploads directory
mkdir -p uploads

# Create database tables if not exists
if [ ! -f dev.db ]; then
    echo "Initializing database..."
    python -c "
import asyncio
from database import create_tables
asyncio.run(create_tables())
print('Database tables created')
" 2>&1 || echo "Warning: Database initialization skipped (will be created on first API call)"
else
    echo "✓ Database already exists"
fi

echo "✓ Backend configured"
echo ""
echo "========================================="
echo "  Setup finished! Services will start..."
echo "========================================="
