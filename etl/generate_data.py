"""Generate synthetic retail CSV files for the OLAP demo."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

from config import RAW_DATA_DIR

fake = Faker()
Faker.seed(42)
random.seed(42)

REGIONS = ["North", "South", "East", "West", "Central"]
STATES_BY_REGION = {
    "North": ["NY", "MA", "IL"],
    "South": ["TX", "FL", "GA"],
    "East": ["PA", "NJ", "VA"],
    "West": ["CA", "WA", "CO"],
    "Central": ["OH", "MI", "MN"],
}
CATEGORIES = {
    "Electronics": ["Laptop", "Phone", "Tablet", "Headphones", "Monitor"],
    "Apparel": ["Jacket", "Jeans", "Sneakers", "T-Shirt", "Dress"],
    "Home": ["Blender", "Vacuum", "Lamp", "Chair", "Bedding"],
    "Sports": ["Yoga Mat", "Dumbbells", "Bike", "Tennis Racket", "Running Shoes"],
    "Grocery": ["Coffee", "Snacks", "Pasta", "Juice", "Cereal"],
}
BRANDS = ["Acme", "Nova", "Peak", "Summit", "Zenith", "Pulse", "Orbit"]


def generate_products(count: int = 120) -> pd.DataFrame:
    rows = []
    product_id = 1
    for category, items in CATEGORIES.items():
        for item in items:
            if product_id > count:
                break
            unit_price = round(random.uniform(9.99, 899.99), 2)
            rows.append(
                {
                    "product_id": product_id,
                    "product_name": item,
                    "category": category,
                    "brand": random.choice(BRANDS),
                    "unit_cost": round(unit_price * random.uniform(0.45, 0.75), 2),
                }
            )
            product_id += 1
    while product_id <= count:
        category = random.choice(list(CATEGORIES.keys()))
        rows.append(
            {
                "product_id": product_id,
                "product_name": fake.word().title(),
                "category": category,
                "brand": random.choice(BRANDS),
                "unit_cost": round(random.uniform(5, 400) * 0.6, 2),
            }
        )
        product_id += 1
    return pd.DataFrame(rows)


def generate_stores(count: int = 40) -> pd.DataFrame:
    rows = []
    for store_id in range(1, count + 1):
        region = REGIONS[(store_id - 1) % len(REGIONS)]
        state = random.choice(STATES_BY_REGION[region])
        rows.append(
            {
                "store_id": store_id,
                "store_name": f"{fake.company()} Store",
                "city": fake.city(),
                "state": state,
                "region": region,
            }
        )
    return pd.DataFrame(rows)


def generate_orders(
    products: pd.DataFrame,
    stores: pd.DataFrame,
    row_count: int = 60000,
) -> pd.DataFrame:
    start = date(2023, 1, 1)
    end = date(2025, 6, 30)
    span = (end - start).days

    product_ids = products["product_id"].tolist()
    store_ids = stores["store_id"].tolist()
    price_lookup = products.set_index("product_id")["unit_cost"].to_dict()
    # Use a markup for selling price
    sell_prices = {
        pid: round(price_lookup[pid] / random.uniform(0.45, 0.75), 2)
        for pid in product_ids
    }

    customers = [fake.unique.name() for _ in range(8000)]
    rows = []
    for order_id in range(1, row_count + 1):
        order_date = start + timedelta(days=random.randint(0, span))
        customer_id = random.randint(1, len(customers))
        product_id = random.choice(product_ids)
        store_id = random.choice(store_ids)
        quantity = random.randint(1, 5)
        rows.append(
            {
                "order_id": order_id,
                "order_date": order_date.isoformat(),
                "customer_id": customer_id,
                "customer_name": customers[customer_id - 1],
                "store_id": store_id,
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": sell_prices[product_id],
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    products = generate_products()
    stores = generate_stores()
    orders = generate_orders(products, stores)

    products.to_csv(RAW_DATA_DIR / "raw_products.csv", index=False)
    stores.to_csv(RAW_DATA_DIR / "raw_stores.csv", index=False)
    orders.to_csv(RAW_DATA_DIR / "raw_orders.csv", index=False)

    print(f"Wrote {len(products)} products, {len(stores)} stores, {len(orders)} orders to {RAW_DATA_DIR}")


if __name__ == "__main__":
    main()
