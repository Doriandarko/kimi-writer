"""
FastAPI application entry point for the Kimi Novel Writing System.

This module sets up the web server with REST API, WebSocket support,
and serves the frontend in production mode.
"""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from backend.api import routes
from backend.api.websocket import websocket_endpoint
from backend.websocket_manager import get_ws_manager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting Kimi Novel Writing System...")

    # Initialize WebSocket manager
    ws_manager = get_ws_manager()
    logger.info("WebSocket manager initialized")

    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    logger.info(f"Output directory: {output_dir.absolute()}")

    # Log configuration
    logger.info(f"API Base URL: {os.getenv('MOONSHOT_API_BASE_URL', 'https://api.moonshot.cn/v1')}")
    logger.info(f"Model: {os.getenv('MOONSHOT_MODEL', 'kimi-k2-thinking')}")
    logger.info(f"CORS Enabled: {os.getenv('ENABLE_CORS', 'true')}")

    yield

    # Shutdown
    logger.info("Shutting down Kimi Novel Writing System...")


# Create FastAPI app
app = FastAPI(
    title="Kimi Novel Writing System",
    description="Multi-agent autonomous novel generation system powered by Moonshot AI",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration for development
if os.getenv("ENABLE_CORS", "true").lower() == "true":
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_url, "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for: {frontend_url}")

# Mount API routes
app.include_router(routes.router, prefix="/api")

# WebSocket endpoint
app.add_websocket_route("/ws/{project_id}", websocket_endpoint)


# Serve frontend static files in production
frontend_build_dir = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_build_dir.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=frontend_build_dir / "assets"), name="assets")

    # Serve index.html for all frontend routes
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend for all non-API routes."""
        # If requesting a file that exists, serve it
        file_path = frontend_build_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        # Otherwise serve index.html (SPA routing)
        return FileResponse(frontend_build_dir / "index.html")

    logger.info(f"Serving frontend from: {frontend_build_dir}")
else:
    logger.warning("Frontend build directory not found. Run 'npm run build' in frontend/")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "kimi-novel-writer",
        "version": "2.0.0"
    }


# Root endpoint (development mode without frontend)
@app.get("/")
async def root():
    """Root endpoint when frontend is not built."""
    if not frontend_build_dir.exists():
        return {
            "message": "Kimi Novel Writing System API",
            "version": "2.0.0",
            "docs": "/docs",
            "api": "/api",
            "websocket": "/ws/{project_id}",
            "note": "Frontend not built. Run 'npm run build' in frontend/ to serve the UI."
        }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "8000"))

    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"API documentation: http://localhost:{port}/docs")
    logger.info(f"WebSocket endpoint: ws://localhost:{port}/ws/{{project_id}}")

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
