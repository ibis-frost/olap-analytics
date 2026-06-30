#!/usr/bin/env python3
"""Run the full ETL pipeline: generate data, seed Postgres, build DuckDB warehouse."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ETL = ROOT / "etl"


def run(script: str) -> None:
    print(f"\n=== Running {script} ===")
    subprocess.run([sys.executable, str(ETL / script)], check=True, cwd=ROOT)


def main() -> None:
    run("generate_data.py")

    try:
        run("seed_postgres.py")
        run("build_warehouse.py")
    except subprocess.CalledProcessError:
        print("\nPostgres unavailable; building warehouse directly from CSV...")
        run("build_warehouse_from_csv.py")

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
