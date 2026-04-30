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
    uv run demos/azure_sql_mi/azure_sql_mi_demo.py
    uv run demos/azure_sql_mi/azure_sql_mi_demo.py --auth sql
"""

from __future__ import annotations

import getpass
import logging
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import config
import defaults
import pyodbc
import typer

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from shared.runner import print_table, report_result  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


class AuthMode(StrEnum):
    integrated = "integrated"
    sql = "sql"


@dataclass(frozen=True)
class DemoConfig:
    server: str
    database: str
    odbc_driver: str


def load_config() -> DemoConfig:
    """Layer config.py over defaults.py without importing names into the module namespace."""
    return DemoConfig(
        server=config.SERVER,
        database=config.DATABASE,
        odbc_driver=getattr(config, "ODBC_DRIVER", defaults.ODBC_DRIVER),
    )


def _build_conn_str(
    cfg: DemoConfig, auth: AuthMode, username: str | None, password: str | None
) -> str:
    base = (
        f"Driver={{{cfg.odbc_driver}}};"
        f"Server={cfg.server};"
        f"Database={cfg.database};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )
    if auth is AuthMode.sql:
        return base + f"UID={username};PWD={password};"
    return base + "Authentication=ActiveDirectoryIntegrated;"


def main(
    auth: Annotated[
        AuthMode, typer.Option(help="Authentication mode.")
    ] = AuthMode.integrated,
) -> None:
    """Test Azure SQL Managed Instance connectivity."""
    cfg = load_config()

    username: str | None = None
    password: str | None = None

    if auth is AuthMode.sql:
        username = input("SQL username: ").strip()
        password = getpass.getpass("SQL password: ")

    conn_str = _build_conn_str(cfg, auth, username, password)
    log.info("Connecting to %s / %s using %s auth…", cfg.server, cfg.database, auth.value)

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
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    typer.run(main)
