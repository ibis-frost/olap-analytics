"""KPI and trend analytics endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.db import fetch_all, get_connection

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

FILTER_CLAUSE = """
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_product p ON f.product_key = p.product_key
    JOIN dim_store s ON f.store_key = s.store_key
    WHERE d.full_date BETWEEN ? AND ?
      AND (? = 'all' OR s.region = ?)
      AND (? = 'all' OR p.category = ?)
"""


def _filters(start: str, end: str, region: str, category: str) -> list:
    return [start, end, region, region, category, category]


@router.get("/summary")
def summary(
    start: str = Query("2023-01-01"),
    end: str = Query("2025-06-30"),
    region: str = Query("all"),
    category: str = Query("all"),
) -> dict:
    conn = get_connection()
    try:
        params = _filters(start, end, region, category)
        row = fetch_all(
            conn,
            f"""
            SELECT
                ROUND(SUM(f.amount), 2) AS total_revenue,
                COUNT(DISTINCT f.order_id) AS total_orders,
                ROUND(SUM(f.quantity), 0) AS total_units,
                ROUND(SUM(f.amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_order_value
            {FILTER_CLAUSE}
            """,
            params,
        )[0]
        return row
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        conn.close()


@router.get("/revenue-trend")
def revenue_trend(
    grain: str = Query("month", pattern="^(month|quarter|year)$"),
    start: str = Query("2023-01-01"),
    end: str = Query("2025-06-30"),
    region: str = Query("all"),
    category: str = Query("all"),
) -> list[dict]:
    period_expr = {
        "month": "STRFTIME(d.full_date, '%Y-%m')",
        "quarter": "d.year || '-Q' || d.quarter",
        "year": "CAST(d.year AS VARCHAR)",
    }[grain]

    conn = get_connection()
    try:
        params = _filters(start, end, region, category)
        return fetch_all(
            conn,
            f"""
            SELECT
                {period_expr} AS period,
                ROUND(SUM(f.amount), 2) AS revenue,
                COUNT(DISTINCT f.order_id) AS orders
            {FILTER_CLAUSE}
            GROUP BY 1
            ORDER BY 1
            """,
            params,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        conn.close()


@router.get("/by-category")
def by_category(
    start: str = Query("2023-01-01"),
    end: str = Query("2025-06-30"),
    region: str = Query("all"),
    category: str = Query("all"),
) -> list[dict]:
    conn = get_connection()
    try:
        params = _filters(start, end, region, category)
        return fetch_all(
            conn,
            f"""
            SELECT
                p.category,
                ROUND(SUM(f.amount), 2) AS revenue,
                SUM(f.quantity) AS units
            {FILTER_CLAUSE}
            GROUP BY p.category
            ORDER BY revenue DESC
            """,
            params,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        conn.close()


@router.get("/filters")
def filter_options() -> dict:
    conn = get_connection()
    try:
        regions = fetch_all(conn, "SELECT DISTINCT region FROM dim_store ORDER BY region")
        categories = fetch_all(conn, "SELECT DISTINCT category FROM dim_product ORDER BY category")
        return {
            "regions": [row["region"] for row in regions],
            "categories": [row["category"] for row in categories],
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        conn.close()
