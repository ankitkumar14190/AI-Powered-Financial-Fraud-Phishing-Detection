"""
SQLite persistence layer.

Fixes vs the original version:
  * BUG: the original module computed its own DATABASE_PATH = Path("database")/"fraud.db",
    which is a path *relative to the current working directory*. src/config/config.py
    already defines an absolute DATABASE_PATH anchored to the project root. Depending on
    where `streamlit run` was launched from, the app could silently read/write two
    different database files. Fixed by importing the single source of truth from config.
  * Connections are now opened/closed with a context manager so a crash mid-query can't
    leak an open sqlite3 connection.
  * Added a `phishing_scans` table -- previously phishing results were never persisted,
    so the Dashboard could only ever show fraud transactions even though phishing
    detection is a core advertised feature.
  * All operations are wrapped in try/except with logging instead of failing silently
    or crashing the Streamlit app with an unhandled traceback.
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Tuple

from src.config.config import DATABASE_PATH
from src.utils.helpers import get_logger

logger = get_logger(__name__)


@contextmanager
def get_connection():
    """Yield a sqlite3 connection and guarantee it is always closed."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
    finally:
        conn.close()


def create_tables() -> None:
    """Create all tables if they do not already exist. Safe to call on every app start."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction INTEGER NOT NULL,
                    confidence REAL NOT NULL,
                    risk TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS phishing_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    risk TEXT NOT NULL,
                    reasons TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
        logger.info("Database tables verified/created successfully.")
    except sqlite3.Error:
        logger.exception("Failed to create database tables.")
        raise


def save_prediction(prediction: int, confidence: float, risk: str) -> None:
    """Persist a single fraud-model prediction."""
    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO transactions (prediction, confidence, risk)
                VALUES (?, ?, ?)
                """,
                (prediction, confidence, risk),
            )
            conn.commit()
    except sqlite3.Error:
        logger.exception("Failed to save fraud prediction.")
        raise


def get_all_predictions() -> List[Tuple]:
    """Return all fraud predictions, most recent first."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM transactions ORDER BY timestamp DESC"
            )
            return cursor.fetchall()
    except sqlite3.Error:
        logger.exception("Failed to fetch fraud predictions.")
        return []


def save_phishing_scan(url: str, score: int, risk: str, reasons: List[str]) -> None:
    """Persist a single phishing URL scan."""
    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO phishing_scans (url, score, risk, reasons)
                VALUES (?, ?, ?, ?)
                """,
                (url, score, risk, "; ".join(reasons)),
            )
            conn.commit()
    except sqlite3.Error:
        logger.exception("Failed to save phishing scan.")
        raise


def get_all_phishing_scans() -> List[Tuple]:
    """Return all phishing scans, most recent first."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM phishing_scans ORDER BY timestamp DESC"
            )
            return cursor.fetchall()
    except sqlite3.Error:
        logger.exception("Failed to fetch phishing scans.")
        return []
