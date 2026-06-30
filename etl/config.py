"""Shared configuration for ETL scripts."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = REPO_ROOT / "data" / "raw"
_raw_path = Path(os.getenv("DUCKDB_PATH", "data/warehouse.duckdb"))
DUCKDB_PATH = _raw_path if _raw_path.is_absolute() else REPO_ROOT / _raw_path

load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env.example")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://olap:olap@localhost:5432/olap_staging",
)
