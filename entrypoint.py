"""
entrypoint.py
Container startup script:
  1. Waits for MySQL to be ready
  2. Seeds sample data if the database is empty (idempotent — safe on restarts)
  3. Launches the Streamlit dashboard
"""

import subprocess
import sys
import time

import mysql.connector

from db_config import get_connection


def wait_for_db(max_attempts=30, delay=2):
    for attempt in range(1, max_attempts + 1):
        try:
            conn = get_connection()
            conn.close()
            print("Database is ready.")
            return
        except mysql.connector.Error as e:
            print(f"Waiting for database... (attempt {attempt}/{max_attempts}) — {e}")
            time.sleep(delay)
    print("Database never became ready. Exiting.")
    sys.exit(1)


def needs_seeding() -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count == 0


def main():
    wait_for_db()

    if needs_seeding():
        print("No data found — seeding database with sample data...")
        subprocess.run([sys.executable, "generate_data.py"], check=True)
    else:
        print("Database already has data — skipping seed step.")

    print("Launching Streamlit dashboard...")
    subprocess.run([
        "streamlit", "run", "app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
    ], check=True)


if __name__ == "__main__":
    main()
