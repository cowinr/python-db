"""
db_connect_test.py
==================
Verifies connectivity to the Azure SQL Managed Instance.

Connects using one of two authentication modes, runs ``SELECT @@VERSION``
and ``SELECT 1 AS ping``, then prints the results to confirm the connection
is working.

Authentication modes
--------------------
  integrated (default)
      Microsoft Entra Integrated / Active Directory Integrated.  No
      credentials are stored; the current user's Entra session is used.

  sql
      SQL Server username and password, prompted at runtime and never
      persisted.

Prerequisites
-------------
  - ODBC Driver for SQL Server installed on the host (default: ODBC Driver 17;
    override via ``ODBC_DRIVER`` in config.py).
  - ``config.py`` present in the same directory (copy config.example.py and
    fill in SERVER and DATABASE).
  - For integrated auth: the signed-in Entra account must have at least
    ``db_datareader`` or ``CONNECT`` permission on the target database.

Usage
-----
  python db_connect_test.py
  python db_connect_test.py --auth sql
"""

from __future__ import annotations

import argparse
import getpass
import sys

import pyodbc

from defaults import *  # noqa: F401,F403 — intentional wildcard import for config layering
from config import *    # noqa: F401,F403


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

    print(f"Connecting to {SERVER} / {DATABASE} using {args.auth} auth…")

    try:
        with pyodbc.connect(conn_str, timeout=15) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT @@VERSION AS server_version;")
            row = cursor.fetchone()
            print("\nServer version:")
            print(f"  {row.server_version}\n")

            cursor.execute("SELECT 1 AS ping;")
            row = cursor.fetchone()
            print(f"Ping result: {row.ping}")

        print("\nConnection test PASSED.")

    except pyodbc.Error as exc:
        print(f"\nConnection test FAILED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
