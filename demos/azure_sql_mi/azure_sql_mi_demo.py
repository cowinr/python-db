"""
azure_sql_mi_demo.py
====================
Verifies connectivity to an Azure SQL Managed Instance.

Connects using one of two authentication modes, runs ``SELECT @@VERSION``
and ``SELECT 1 AS ping``, then prints the results to confirm the connection
is working.

Authentication modes
--------------------
  integrated (default)
      Microsoft Entra Integrated / Active Directory Integrated. No
      credentials are stored; the current user's Entra session is used.

  sql
      SQL Server username and password, prompted at runtime and never
      persisted.

Prerequisites
-------------
  - ODBC Driver for SQL Server installed on the host (default: ODBC Driver 17;
    override via ``ODBC_DRIVER`` in config.py).
  - ``config.py`` present in this directory (copy config.example.py and
    fill in SERVER and DATABASE).
  - For integrated auth: the signed-in Entra account must have at least
    ``db_datareader`` or ``CONNECT`` permission on the target database.

Usage
-----
    python azure_sql_mi_demo.py
    python azure_sql_mi_demo.py --auth sql
"""

from __future__ import annotations

import argparse
import getpass
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from shared.runner import print_table, report_result

import pyodbc

from defaults import *  # noqa: F401,F403 — intentional wildcard import for config layering
from config import *    # noqa: F401,F403

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def _build_conn_str(auth: str, username: str | None, password: str | None) -> str:
    base = (
        f"Driver={{{ODBC_DRIVER}}};"
        f"Server={SERVER};"
        f"Database={DATABASE};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )
    if auth == "sql":
        return base + f"UID={username};PWD={password};"
    return base + "Authentication=ActiveDirectoryIntegrated;"


def main() -> None:
    parser = argparse.ArgumentParser(description="Test Azure SQL Managed Instance connectivity.")
    parser.add_argument(
        "--auth",
        choices=["integrated", "sql"],
        default="integrated",
        help="Authentication mode (default: integrated).",
    )
    args = parser.parse_args()

    username: str | None = None
    password: str | None = None

    if args.auth == "sql":
        username = input("SQL username: ").strip()
        password = getpass.getpass("SQL password: ")

    conn_str = _build_conn_str(args.auth, username, password)
    log.info("Connecting to %s / %s using %s auth…", SERVER, DATABASE, args.auth)

    try:
        with pyodbc.connect(conn_str, timeout=15) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT @@VERSION AS server_version;")
            version_rows = cursor.fetchall()
            print_table(version_rows, ["server_version"], col_width=60)

            cursor.execute("SELECT 1 AS ping;")
            ping_rows = cursor.fetchall()
            print_table(ping_rows, ["ping"])

        report_result("Connection test", passed=True)

    except pyodbc.Error as exc:
        report_result("Connection test", passed=False, detail=str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
