"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from config import settings
from database import AsyncSessionLocal, create_tables
from limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # Startup: create tables for dev environments using SQLite
    if settings.DATABASE_URL.startswith("sqlite"):
        await create_tables()

    # Ensure uploads directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    yield


app = FastAPI(
    title="银行授信尽调系统",
    description="Bank Credit Due Diligence System",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate Limiter — prevents brute-force login attacks (imported from limiter module)
limiter.init_app(app)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"code": 4290, "message": "请求过于频繁，请稍后再试", "data": None},
    )


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Register routers
from auth.router import router as auth_router
from routers.admin import router as admin_router
from routers.companies import router as companies_router
from routers.risks import router as risks_router
from routers.equity import router as equity_router
from routers import financial_reports as financial_reports_router
from routers import bank_statements as bank_statements_router
from routers import credit as credit_router
from fastapi import APIRouter

app.include_router(auth_router, tags=["auth"])  # already has /api/auth prefix
app.include_router(admin_router, prefix="/api", tags=["admin"])
app.include_router(companies_router, prefix="/api", tags=["companies"])
app.include_router(risks_router, prefix="/api", tags=["risks"])
app.include_router(equity_router, prefix="/api", tags=["equity"])

# T04 routers — mounted under /api/companies/{company_id}
company_sub_router = APIRouter(prefix="/api/companies/{company_id}")
company_sub_router.include_router(financial_reports_router.router)
company_sub_router.include_router(bank_statements_router.router)
company_sub_router.include_router(credit_router.router)
app.include_router(company_sub_router, tags=["financial-reports", "bank-statements", "credit"])

# T05 routers — task management, rating engine, report generation
from routers import tasks as tasks_router
from routers import rating as rating_router
from routers import reports as reports_router

app.include_router(tasks_router.router, prefix="/api", tags=["tasks"])
app.include_router(rating_router.router, prefix="/api", tags=["rating"])
app.include_router(reports_router.router, prefix="/api", tags=["reports"])

# Serve frontend SPA directly from FastAPI
# 1. Mount assets/ for JS/CSS bundles
# 2. Explicit catch-all route for SPA (serves index.html for any non-API path)
_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="frontend-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve index.html for SPA client-side routing."""
        return FileResponse(str(_FRONTEND_DIST / "index.html"))

    @app.get("/")
    async def serve_root():
        """Serve index.html for root path."""
        return FileResponse(str(_FRONTEND_DIST / "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
