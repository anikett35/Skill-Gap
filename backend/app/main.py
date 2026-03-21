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

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — connecting to MongoDB...")
    await connect_to_mongo()
    yield
    logger.info("Shutting down...")
    await close_mongo_connection()


app = FastAPI(
    title="AI Adaptive Onboarding Engine v3",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter()-start)*1000:.2f}"
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": str(exc)})

# Import routers
from app.api import auth, analyze, progress, chat, export

app.include_router(auth.router,     prefix="/api/auth",     tags=["Auth"])
app.include_router(analyze.router,  prefix="/api/analyze",  tags=["Analysis"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(chat.router,     prefix="/api/chat",     tags=["Chat"])
app.include_router(export.router,   prefix="/api/export",   tags=["Export"])

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "3.0.0"}

@app.get("/")
async def root():
    return {"message": "AI Adaptive Onboarding Engine v3", "status": "running"}