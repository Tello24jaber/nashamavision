"""
FastAPI Application Entry Point
Main application configuration and setup
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

from app.core.config import settings
from app.api.routers import matches, videos, tracks, processing, replay, assistant, simple_processing
from app.api.routers.analytics import metrics_router, tactics_router, xt_router, events_router
from app.api.routers.analytics.player_analytics import router as player_analytics_router
from app.db.session import init_db

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    Runs on startup and shutdown
    """
    # Startup
    logger.info("Starting Nashama Vision API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize database (skip during testing)
    import os
    if os.getenv("TESTING") != "1":
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            logger.warning("⚠️ Application starting without database connection")
            logger.warning("⚠️ API endpoints will return errors until database is accessible")
    else:
        logger.info("Skipping database initialization (testing mode)")
    
    # Create storage directories
    if settings.storage_type == "local":
        storage_path = Path(settings.local_storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)
        (storage_path / "videos" / "raw").mkdir(parents=True, exist_ok=True)
        (storage_path / "videos" / "processed").mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage initialized at: {storage_path}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Nashama Vision API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Advanced Football Analytics Platform with Computer Vision",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# Add CORS middleware - Allow all localhost origins for development
# Explicitly list localhost variations to avoid CORS issues
cors_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if not settings.is_production else settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add TrustedHost middleware (for production)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure this properly in production
    )


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type"),
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": errors,
            "status_code": 422,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
            "status_code": 500,
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "docs": "/api/docs",
    }


# Include routers
app.include_router(matches.router, prefix="/api/v1/matches", tags=["Matches"])
app.include_router(videos.router, prefix="/api/v1/videos", tags=["Videos"])
app.include_router(tracks.router, prefix="/api/v1/tracks", tags=["Tracks"])
app.include_router(processing.router, prefix="/api/v1/processing", tags=["Processing"])
app.include_router(simple_processing.router, prefix="/api/v1/simple-processing", tags=["Simple Processing"])

# Analytics routers (Phase 2)
app.include_router(metrics_router, tags=["Analytics"])
app.include_router(player_analytics_router, tags=["Player Analytics"])

# Phase 3 routers
app.include_router(tactics_router, tags=["Tactical Analysis"])
app.include_router(xt_router, tags=["Expected Threat"])
app.include_router(events_router, tags=["Events"])

# Phase 4 routers
app.include_router(replay.router, tags=["Replay"])

# Phase 5 routers
app.include_router(assistant.router, tags=["AI Assistant"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
