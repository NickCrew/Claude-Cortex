"""FastAPI server for Cortex dashboard."""

from pathlib import Path
import os

try:
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    raise ImportError("The 'dashboard' extra is required. Install with 'pip install claude-cortex[dashboard]'")

from .api import router as api_router

app = FastAPI(
    title="Cortex Dashboard",
    description="Web interface for Claude Cortex",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix="/api")

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    # Fallback for development if static dir isn't bundled yet
    print(f"Warning: Static directory not found at {static_dir}")
