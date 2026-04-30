"""
sqlalchemy_demo.py
==================
Demonstrates SQLAlchemy Core (2.0 style) as a backend-agnostic abstraction
over a relational database.

The same Python code runs against SQLite, PostgreSQL, MySQL/MariaDB, or
Microsoft SQL Server (including Azure SQL Managed Instance and Azure SQL
Database). Only the connection URL changes. This is the headline benefit
of using SQLAlchemy over a raw driver: portable, pooled, parameterised
access with a Pythonic query language.

Usage
-----
    python sqlalchemy_demo.py
    python sqlalchemy_demo.py --backend sqlite --memory
    python sqlalchemy_demo.py --backend postgres
    python sqlalchemy_demo.py --backend mysql
    python sqlalchemy_demo.py --backend mssql
    python sqlalchemy_demo.py --url <full-sqlalchemy-url>
    python sqlalchemy_demo.py --echo

Parameters
----------
  --backend {sqlite,postgres,mysql,mssql}
        Which backend to connect to (default: sqlite).
        For sqlite, a local file ./sqlalchemy_demo.db is used unless
        --memory is also passed.
        For postgres, mysql, or mssql, the DATABASE_URL environment
        variable must be set to a full SQLAlchemy URL. The mssql
        backend covers on-prem SQL Server, Azure SQL Database, and
        Azure SQL Managed Instance — the dialect is the same; only
        the host and auth bits in the URL differ.

  --memory
        Use an in-memory SQLite database (only valid with --backend sqlite).

  --url URL
        Override the connection URL entirely. Takes precedence over
        --backend and --memory. Useful for one-off experiments.

  --echo
        Print the generated SQL to stderr. Helpful for understanding what
        SQLAlchemy compiles your Python expressions into.

Environment
-----------
  DATABASE_URL    Full SQLAlchemy URL for postgres / mysql / mssql backends, e.g.
                  postgresql+psycopg2://user:pw@host:5432/dbname
                  mysql+pymysql://user:pw@host:3306/dbname
                  mssql+pyodbc://user:pw@host/dbname?driver=ODBC+Driver+18+for+SQL+Server
                  mssql+pyodbc://@host/dbname?driver=ODBC+Driver+18+for+SQL+Server&Authentication=ActiveDirectoryIntegrated

Optional dependencies
---------------------
  Postgres backend:  pip install psycopg2-binary
  MySQL backend:     pip install pymysql
  MSSQL  backend:    pip install pyodbc, plus the Microsoft ODBC Driver
                     for SQL Server (17 or 18) installed on the host.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from shared.runner import print_table, report_result

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    func,
    insert,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

SAMPLE_PRODUCTS: list[dict] = [
    {"name": "Widget A", "price_gbp": 9.99},
    {"name": "Widget B", "price_gbp": 14.50},
    {"name": "Gadget Pro", "price_gbp": 49.95},
    {"name": "Gadget Lite", "price_gbp": 24.99},
]

metadata = MetaData()

products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("price_gbp", Float, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)


def build_url(backend: str, memory: bool, url_override: str | None) -> str:
    """Resolve the SQLAlchemy connection URL from CLI flags and environment."""
    if url_override:
        return url_override

    if backend == "sqlite":
        if memory:
            return "sqlite:///:memory:"
        db_file = Path.cwd() / "sqlalchemy_demo.db"
        return f"sqlite:///{db_file}"

    if backend in ("postgres", "mysql", "mssql"):
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise SystemExit(
                f"Backend '{backend}' requires the DATABASE_URL environment "
                f"variable to be set to a full SQLAlchemy URL."
            )
        return url

    raise ValueError(f"Unknown backend: {backend}")


def setup_schema(engine: Engine) -> None:
    metadata.create_all(engine)
    log.info("Schema ready.")


def insert_sample_data(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(insert(products), SAMPLE_PRODUCTS)
    log.info("Inserted %d sample rows.", len(SAMPLE_PRODUCTS))


def query_all(engine: Engine) -> list:
    with engine.connect() as conn:
        result = conn.execute(select(products).order_by(products.c.id))
        return result.all()


def query_by_max_price(engine: Engine, max_price: float) -> list:
    statement = (
        select(products.c.id, products.c.name, products.c.price_gbp)
        .where(products.c.price_gbp <= max_price)
        .order_by(products.c.price_gbp)
    )
    with engine.connect() as conn:
        return conn.execute(statement).all()


def main() -> None:
    parser = argparse.ArgumentParser(description="SQLAlchemy Core backend-agnostic demo.")
    parser.add_argument(
        "--backend",
        choices=["sqlite", "postgres", "mysql", "mssql"],
        default="sqlite",
        help="Which backend to connect to (default: sqlite).",
    )
    parser.add_argument(
        "--memory",
        action="store_true",
        help="Use an in-memory SQLite database (only valid with --backend sqlite).",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Override the connection URL entirely (takes precedence over --backend).",
    )
    parser.add_argument(
        "--echo",
        action="store_true",
        help="Print generated SQL to stderr.",
    )
    args = parser.parse_args()

    url = build_url(args.backend, args.memory, args.url)
    log.info("Backend: %s", args.backend if not args.url else "custom")
    log.info("Driver: %s", url.split(":", 1)[0])

    if args.echo:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    try:
        engine = create_engine(url, future=True)
        setup_schema(engine)
        insert_sample_data(engine)

        log.info("Querying all products…")
        all_rows = query_all(engine)
        print_table(all_rows, ["id", "name", "price_gbp", "created_at"])

        price_filter = 25.00
        log.info("Querying products at £%.2f or under…", price_filter)
        cheap = query_by_max_price(engine, price_filter)
        print_table(cheap, ["id", "name", "price_gbp"])

        report_result("SQLAlchemy demo", passed=True)

    except SQLAlchemyError as exc:
        report_result("SQLAlchemy demo", passed=False, detail=str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
