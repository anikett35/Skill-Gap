"""
AI Adaptive Onboarding Engine v3 — Production FastAPI Backend
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api import auth, analyze, progress, chat, export, debug

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — connecting to MongoDB...")
    await connect_to_mongo()
    yield
    logger.info("Shutting down — closing MongoDB connection...")
    await close_mongo_connection()


app = FastAPI(
    title="AI Adaptive Onboarding Engine v3",
    version="3.0.0",
    description="Production-grade AI skill gap analysis and learning platform",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
)

# ── Middleware ──────────────────────────────────────────────────────────────

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response


# ── Global exception handler ────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


# ── Routers ─────────────────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Mentor"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(debug.router, prefix="/api/debug", tags=["Debug"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}
