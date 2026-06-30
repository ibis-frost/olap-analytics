"""FastAPI application entry point."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.db import DUCKDB_PATH
from api.routes import cube, metrics

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_DIST = REPO_ROOT / "web" / "dist"
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env.example")

default_origins = "http://localhost:5173,http://127.0.0.1:5173"
cors_env = os.getenv("CORS_ORIGINS", default_origins)
if cors_env.strip() == "*":
    cors_origins = ["*"]
else:
    cors_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]

app = FastAPI(
    title="OLAP Analytics API",
    description="Slice-and-dice retail analytics powered by DuckDB star schema.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router)
app.include_router(cube.router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "warehouse_ready": DUCKDB_PATH.exists(),
    }


if WEB_DIST.exists():
    assets_dir = WEB_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def dashboard_home() -> FileResponse:
        return FileResponse(WEB_DIST / "index.html")

    @app.get("/{full_path:path}")
    def dashboard_fallback(full_path: str) -> FileResponse:
        reserved = ("api", "health", "docs", "openapi.json", "redoc", "assets")
        if full_path.startswith(reserved):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(WEB_DIST / "index.html")
