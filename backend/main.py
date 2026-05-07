"""
AutoCinema Backend Server
FastAPI application with CORS, static files, and database initialization.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from backend.database import init_db
from backend.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    # Create storage directories
    base_dir = os.path.dirname(__file__)
    os.makedirs(os.path.join(base_dir, "storage", "outputs"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "storage", "projects"), exist_ok=True)
    await init_db()
    print("[OK] AutoCinema backend ready")
    yield


app = FastAPI(
    title="AutoCinema API",
    description="Cloud-driven video production platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated assets
storage_path = os.path.join(os.path.dirname(__file__), "storage")
os.makedirs(os.path.join(storage_path, "outputs"), exist_ok=True)
app.mount("/static", StaticFiles(directory=storage_path), name="static")

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    return {"message": "AutoCinema API is running", "docs": "/docs"}
