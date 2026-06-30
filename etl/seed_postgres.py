"""Load raw CSV files into Postgres staging tables."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DATABASE_URL, RAW_DATA_DIR


STAGING_TABLES = {
    "raw_products": RAW_DATA_DIR / "raw_products.csv",
    "raw_stores": RAW_DATA_DIR / "raw_stores.csv",
    "raw_orders": RAW_DATA_DIR / "raw_orders.csv",
}


def ensure_csvs() -> None:
    missing = [name for name, path in STAGING_TABLES.items() if not path.exists()]
    if missing:
        from generate_data import main as generate_main

        print(f"Missing CSVs ({', '.join(missing)}); generating synthetic data...")
        generate_main()


def seed_postgres() -> None:
    ensure_csvs()
    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        for table_name, csv_path in STAGING_TABLES.items():
            df = pd.read_csv(csv_path)
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
            df.to_sql(table_name, conn, index=False, if_exists="replace")
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"Loaded {count:,} rows into {table_name}")


if __name__ == "__main__":
    seed_postgres()
