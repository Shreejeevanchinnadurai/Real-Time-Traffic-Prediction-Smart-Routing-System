"""
Database Connection Manager
===========================
Provides a context-managed SQLite connection with automatic initialization.
Designed to be swappable — change Config.DB_TYPE to switch backends.

Usage:
    from database.db_connection import get_connection, initialize_database

    initialize_database()  # Run once at startup

    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM locations")
        rows = cursor.fetchall()
"""

import sqlite3
from pathlib import Path
from typing import Optional

# Use relative import-safe approach
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

# Path to the SQL schema file
_SCHEMA_FILE = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """
    Create and return a new SQLite database connection.

    Returns:
        sqlite3.Connection configured with row_factory for dict-like access.

    Raises:
        sqlite3.Error: If connection fails.
    """
    try:
        # Ensure the database directory exists
        Config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(Config.DB_PATH))
        conn.row_factory = sqlite3.Row  # Access columns by name
        conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent reads
        conn.execute("PRAGMA foreign_keys=ON")    # Enforce FK constraints
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise


def initialize_database() -> None:
    """
    Initialize the database by executing the schema.sql script.
    Creates all tables if they don't already exist.
    Safe to call multiple times (uses CREATE IF NOT EXISTS).
    """
    if not _SCHEMA_FILE.exists():
        logger.error(f"Schema file not found: {_SCHEMA_FILE}")
        raise FileNotFoundError(f"Schema file not found: {_SCHEMA_FILE}")

    schema_sql = _SCHEMA_FILE.read_text(encoding="utf-8")

    try:
        with get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()
        logger.info(f"Database initialized at: {Config.DB_PATH}")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def check_connection() -> bool:
    """
    Test the database connection and return True if successful.

    Returns:
        True if connection is alive, False otherwise.
    """
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Connection check failed: {e}")
        return False


def get_table_counts() -> dict:
    """
    Get row counts for all tables.

    Returns:
        Dictionary mapping table name to row count.
    """
    tables = ["locations", "traffic_data", "predictions", "routes", "route_history"]
    counts = {}
    try:
        with get_connection() as conn:
            for table in tables:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f"Failed to get table counts: {e}")
        for table in tables:
            counts[table] = 0
    return counts
