from __future__ import annotations

import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "ecommerce.db"
SCHEMA_PATH = DB_DIR / "schema.sql"


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    """Open a connection with Row factory """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Path | str = DB_PATH, schema_path: Path | str = SCHEMA_PATH) -> None:
    """Create the database from schema.sql."""
    sql = Path(schema_path).read_text(encoding="utf-8")
    conn = get_connection(db_path)
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


def query(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Run a SELECT and return all rows."""
    return conn.execute(sql, params).fetchall()


def execute(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> int:
    """Run one INSERT/UPDATE/DELETE, commit, and return the affected row count."""
    cur = conn.execute(sql, params)
    conn.commit()
    return cur.rowcount


def table_counts(conn: sqlite3.Connection) -> dict[str, int]:
    tables = ("Customer", "Staff", "CreditCard", "Product", "Purchase", "PurchaseItem")
    return {t: query(conn, f"SELECT COUNT(*) AS n FROM {t}")[0]["n"] for t in tables}
