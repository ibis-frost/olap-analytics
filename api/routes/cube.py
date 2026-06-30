"""OLAP cube slice/dice and drill-down endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.db import fetch_all, get_connection

router = APIRouter(prefix="/api/cube", tags=["cube"])

ALLOWED_DIMENSIONS = {
    "region": ("s.region", "dim_store s ON f.store_key = s.store_key"),
    "category": ("p.category", "dim_product p ON f.product_key = p.product_key"),
    "store": ("s.store_name", "dim_store s ON f.store_key = s.store_key"),
    "brand": ("p.brand", "dim_product p ON f.product_key = p.product_key"),
}

MEASURES = {
    "revenue": "ROUND(SUM(f.amount), 2)",
    "orders": "COUNT(DISTINCT f.order_id)",
    "units": "SUM(f.quantity)",
}

FILTER_JOINS = """
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_product p ON f.product_key = p.product_key
    JOIN dim_store s ON f.store_key = s.store_key
"""


@router.get("")
def cube_query(
    dimensions: str = Query("region,category"),
    measure: str = Query("revenue"),
    start: str = Query("2023-01-01"),
    end: str = Query("2025-06-30"),
    region: str = Query("all"),
    category: str = Query("all"),
) -> list[dict]:
    dim_names = [d.strip() for d in dimensions.split(",") if d.strip()]
    invalid = [d for d in dim_names if d not in ALLOWED_DIMENSIONS]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid dimensions: {invalid}")
    if measure not in MEASURES:
        raise HTTPException(status_code=400, detail=f"Invalid measure: {measure}")

    select_parts = [f"{ALLOWED_DIMENSIONS[d][0]} AS {d}" for d in dim_names]
    group_parts = ", ".join(str(i + 1) for i in range(len(dim_names)))

    conn = get_connection()
    try:
        return fetch_all(
            conn,
            f"""
            SELECT
                {", ".join(select_parts)},
                {MEASURES[measure]} AS value
            FROM fact_sales f
            {FILTER_JOINS}
            WHERE d.full_date BETWEEN ? AND ?
              AND (? = 'all' OR s.region = ?)
              AND (? = 'all' OR p.category = ?)
            GROUP BY {group_parts}
            ORDER BY value DESC
            LIMIT 100
            """,
            [start, end, region, region, category, category],
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        conn.close()


@router.get("/drill")
def drill_down(
    dimension: str = Query("date"),
    level: str = Query("year"),
    start: str = Query("2023-01-01"),
    end: str = Query("2025-06-30"),
    region: str = Query("all"),
    category: str = Query("all"),
) -> list[dict]:
    if dimension != "date":
        raise HTTPException(status_code=400, detail="Only date drill-down is supported in v1")

    level_map = {
        "year": ("CAST(d.year AS VARCHAR)", "d.year"),
        "quarter": ("d.year || '-Q' || d.quarter", "d.year, d.quarter"),
        "month": ("STRFTIME(d.full_date, '%Y-%m')", "d.year, d.month"),
    }
    if level not in level_map:
        raise HTTPException(status_code=400, detail=f"Invalid level: {level}")

    label_expr, group_expr = level_map[level]

    conn = get_connection()
    try:
        return fetch_all(
            conn,
            f"""
            SELECT
                {label_expr} AS period,
                ROUND(SUM(f.amount), 2) AS revenue,
                COUNT(DISTINCT f.order_id) AS orders
            FROM fact_sales f
            {FILTER_JOINS}
            WHERE d.full_date BETWEEN ? AND ?
              AND (? = 'all' OR s.region = ?)
              AND (? = 'all' OR p.category = ?)
            GROUP BY {group_expr}
            ORDER BY {group_expr}
            """,
            [start, end, region, region, category, category],
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        conn.close()
