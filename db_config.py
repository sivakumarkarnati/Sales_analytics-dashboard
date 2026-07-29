"""
db_config.py
Centralized MySQL connection handling. Reads credentials from a .env file
so nothing is hardcoded in the codebase.

Create a `.env` file (see .env.example) before running any script.
"""

import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Returns a live MySQL connection using credentials from .env"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "sales_analytics"),
    )
