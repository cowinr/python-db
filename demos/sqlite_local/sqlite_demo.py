"""
sqlite_demo.py
==============
Demonstrates local SQLite database access using the Python standard library.

Creates a local .db file, defines a simple schema, inserts sample rows,
and queries them back — no third-party dependencies, no server, no credentials.

This is the "simplest possible case" baseline. Compare it with the Azure SQL MI
demo (db_connect_test.py) to see the full range from local stdlib to
cloud-authenticated managed instance.

Usage
-----
    python sqlite_demo.py
    python sqlite_demo.py --db-path /tmp/demo.db
    python sqlite_demo.py --db-path :memory:

Parameters
----------
  --db-path   Path to the SQLite database file.
              Default: ./demo.db in the current working directory.
              Pass ':memory:' for a transient in-memory database that is
              discarded when the script exits.
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from shared.runner import print_table

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

SAMPLE_PRODUCTS: list[tuple[str, float]] = [
    ("Widget A", 9.99),
    ("Widget B", 14.50),
    ("Gadget Pro", 49.95),
    ("Gadget Lite", 24.99),
]


def resolve_db_path(raw: str) -> str:
    """Return the path string to pass to sqlite3.connect.

    Passes ':memory:' through unchanged; converts everything else to an
    absolute path string so the .db file lands where the user expects.
    """
    if raw == ":memory:":
        return raw
    return str(Path(raw).resolve())


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            price_gbp  REAL    NOT NULL CHECK (price_gbp >= 0),
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    log.info("Schema ready.")


def insert_sample_data(conn: sqlite3.Connection) -> None:
    conn.executemany(
        "INSERT INTO products (name, price_gbp) VALUES (?, ?)",
        SAMPLE_PRODUCTS,
    )
    conn.commit()
    log.info("Inserted %d sample rows.", len(SAMPLE_PRODUCTS))


def query_all(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    cursor = conn.execute(
        "SELECT id, name, price_gbp, created_at FROM products ORDER BY id"
    )
    return cursor.fetchall()


def query_by_max_price(conn: sqlite3.Connection, max_price: float) -> list[sqlite3.Row]:
    cursor = conn.execute(
        "SELECT id, name, price_gbp FROM products WHERE price_gbp <= ? ORDER BY price_gbp",
        (max_price,),
    )
    return cursor.fetchall()


def main() -> None:
    parser = argparse.ArgumentParser(description="SQLite local database demo.")
    parser.add_argument(
        "--db-path",
        default="demo.db",
        help="Path to the SQLite .db file, or ':memory:' for a transient database (default: ./demo.db).",
    )
    args = parser.parse_args()

    db_path = resolve_db_path(args.db_path)
    log.info("Using database: %s", db_path)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        create_schema(conn)
        insert_sample_data(conn)

        log.info("Querying all products…")
        rows = query_all(conn)
        print_table(rows, ["id", "name", "price_gbp", "created_at"])

        price_filter = 25.00
        log.info("Querying products at £%.2f or under…", price_filter)
        cheap = query_by_max_price(conn, price_filter)
        print_table(cheap, ["id", "name", "price_gbp"])

    log.info("Demo complete.")


if __name__ == "__main__":
    main()
