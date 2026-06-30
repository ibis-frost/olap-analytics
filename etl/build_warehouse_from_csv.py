"""Build DuckDB star schema directly from raw CSV files (no Postgres required)."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DUCKDB_PATH, RAW_DATA_DIR


def build_warehouse_from_csv() -> None:
    orders = pd.read_csv(RAW_DATA_DIR / "raw_orders.csv")
    products = pd.read_csv(RAW_DATA_DIR / "raw_products.csv")
    stores = pd.read_csv(RAW_DATA_DIR / "raw_stores.csv")
    orders["order_date"] = pd.to_datetime(orders["order_date"]).dt.date

    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DUCKDB_PATH.exists():
        DUCKDB_PATH.unlink()

    con = duckdb.connect(str(DUCKDB_PATH))
    con.register("orders_df", orders)
    con.register("products_df", products)
    con.register("stores_df", stores)

    con.execute(
        """
        CREATE TABLE dim_date AS
        SELECT
            CAST(STRFTIME(d, '%Y%m%d') AS INTEGER) AS date_key,
            d AS full_date,
            EXTRACT(YEAR FROM d)::INTEGER AS year,
            EXTRACT(QUARTER FROM d)::INTEGER AS quarter,
            EXTRACT(MONTH FROM d)::INTEGER AS month,
            STRFTIME(d, '%B') AS month_name,
            STRFTIME(d, '%A') AS day_of_week
        FROM (
            SELECT UNNEST(GENERATE_SERIES(
                DATE '2023-01-01',
                DATE '2025-06-30',
                INTERVAL 1 DAY
            )) AS d
        );
        """
    )

    con.execute(
        """
        CREATE TABLE dim_product AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY product_id) AS product_key,
            product_id,
            product_name,
            category,
            brand,
            unit_cost
        FROM products_df;
        """
    )

    con.execute(
        """
        CREATE TABLE dim_store AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY store_id) AS store_key,
            store_id,
            store_name,
            city,
            state,
            region
        FROM stores_df;
        """
    )

    con.execute(
        """
        CREATE TABLE dim_customer AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_key,
            customer_id,
            customer_name
        FROM (
            SELECT DISTINCT customer_id, customer_name
            FROM orders_df
        );
        """
    )

    con.execute(
        """
        CREATE TABLE fact_sales AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY o.order_id) AS sales_key,
            dd.date_key,
            dp.product_key,
            ds.store_key,
            dc.customer_key,
            o.order_id,
            o.quantity,
            o.unit_price,
            ROUND(o.quantity * o.unit_price, 2) AS amount
        FROM orders_df o
        JOIN dim_date dd ON dd.full_date = o.order_date
        JOIN dim_product dp ON dp.product_id = o.product_id
        JOIN dim_store ds ON ds.store_id = o.store_id
        JOIN dim_customer dc ON dc.customer_id = o.customer_id;
        """
    )

    fact_count = con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    print(f"Built warehouse from CSV at {DUCKDB_PATH} with {fact_count:,} fact rows")
    con.close()


if __name__ == "__main__":
    build_warehouse_from_csv()
