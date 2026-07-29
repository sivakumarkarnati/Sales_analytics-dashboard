"""
generate_data.py
Generates realistic synthetic sales data and inserts it into MySQL.
Run this once after creating the schema (schema.sql) to populate the database.

Usage:
    python generate_data.py
"""

import random
from datetime import date, timedelta

import mysql.connector
from faker import Faker

from db_config import get_connection

fake = Faker()
random.seed(42)

REGIONS = ["North", "South", "East", "West", "Central"]
SEGMENTS = ["Consumer", "Corporate", "SMB"]
CATEGORIES = {
    "Electronics": ["Wireless Mouse", "USB-C Hub", "Bluetooth Speaker", "Laptop Stand", "Webcam"],
    "Office Supplies": ["Notebook", "Desk Organizer", "Stapler", "Sticky Notes", "Whiteboard"],
    "Furniture": ["Office Chair", "Standing Desk", "Bookshelf", "Filing Cabinet", "Monitor Arm"],
    "Apparel": ["T-Shirt", "Hoodie", "Cap", "Tote Bag", "Water Bottle"],
}
ORDER_STATUSES = ["Completed"] * 85 + ["Returned"] * 10 + ["Cancelled"] * 5  # weighted

N_CUSTOMERS = 300
N_PRODUCTS_PER_CATEGORY = 5
N_ORDERS = 4000
DATE_START = date.today() - timedelta(days=730)  # 2 years of history
DATE_END = date.today()


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def seed_customers(cursor):
    print(f"Inserting {N_CUSTOMERS} customers...")
    rows = []
    for _ in range(N_CUSTOMERS):
        rows.append((
            fake.company() if random.random() < 0.3 else fake.name(),
            random.choice(REGIONS),
            random.choice(SEGMENTS),
            random_date(DATE_START, DATE_END),
        ))
    cursor.executemany(
        "INSERT INTO customers (customer_name, region, segment, signup_date) VALUES (%s, %s, %s, %s)",
        rows,
    )


def seed_products(cursor):
    print("Inserting products...")
    rows = []
    for category, names in CATEGORIES.items():
        for name in names:
            price = round(random.uniform(8, 250), 2)
            rows.append((name, category, price))
    cursor.executemany(
        "INSERT INTO products (product_name, category, unit_price) VALUES (%s, %s, %s)",
        rows,
    )


def seed_orders_and_items(cursor, conn):
    print(f"Inserting {N_ORDERS} orders with line items...")
    cursor.execute("SELECT customer_id, region FROM customers")
    customers = cursor.fetchall()

    cursor.execute("SELECT product_id, unit_price FROM products")
    products = cursor.fetchall()

    order_insert = "INSERT INTO orders (customer_id, order_date, region, status) VALUES (%s, %s, %s, %s)"
    item_insert = (
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)"
    )

    batch_size = 200
    for batch_start in range(0, N_ORDERS, batch_size):
        for _ in range(min(batch_size, N_ORDERS - batch_start)):
            customer_id, region = random.choice(customers)
            order_date = random_date(DATE_START, DATE_END)
            status = random.choice(ORDER_STATUSES)

            cursor.execute(order_insert, (customer_id, order_date, region, status))
            order_id = cursor.lastrowid

            n_items = random.randint(1, 4)
            chosen_products = random.sample(products, k=min(n_items, len(products)))
            for product_id, unit_price in chosen_products:
                quantity = random.randint(1, 5)
                cursor.execute(item_insert, (order_id, product_id, quantity, unit_price))
        conn.commit()
        print(f"  ...{min(batch_start + batch_size, N_ORDERS)}/{N_ORDERS} orders committed")


def main():
    conn = get_connection()
    cursor = conn.cursor()

    seed_customers(cursor)
    conn.commit()

    seed_products(cursor)
    conn.commit()

    seed_orders_and_items(cursor, conn)

    cursor.close()
    conn.close()
    print("Done. Database seeded successfully.")


if __name__ == "__main__":
    main()
