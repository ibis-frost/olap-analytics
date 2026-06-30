"""Database connection helpers."""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env.example")

_raw_path = Path(os.getenv("DUCKDB_PATH", "data/warehouse.duckdb"))
DUCKDB_PATH = _raw_path if _raw_path.is_absolute() else REPO_ROOT / _raw_path


def get_connection() -> duckdb.DuckDBPyConnection:
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"Warehouse not found at {DUCKDB_PATH}. Run etl/build_warehouse.py first."
        )
    return duckdb.connect(str(DUCKDB_PATH), read_only=True)


def fetch_all(conn: duckdb.DuckDBPyConnection, query: str, params: list | None = None) -> list[dict]:
    if params:
        result = conn.execute(query, params)
    else:
        result = conn.execute(query)
    columns = [col[0] for col in result.description]
    return [dict(zip(columns, row)) for row in result.fetchall()]
