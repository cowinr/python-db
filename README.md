# python-db

A collection of Python database connectivity demos, from local SQLite through to cloud-authenticated Azure SQL Managed Instance. Each demo is self-contained and can be run independently.

## Structure

```
python-db/
├── demos/
│   ├── sqlite_local/        — stdlib sqlite3, no dependencies, no server
│   ├── sqlalchemy_core/     — SQLAlchemy Core 2.0, backend-agnostic (SQLite / Postgres / MySQL / MSSQL)
│   └── azure_sql_mi/        — pyodbc + Microsoft Entra / SQL auth against Azure SQL MI
├── shared/
│   └── runner.py            — shared output utilities (print_table, report_result)
└── pyproject.toml           — project metadata, dependencies, ruff config
```

## Setup

Install [uv](https://docs.astral.sh/uv/) once if you haven't already:

```bash
echo "ssl-no-revoke" >> ~/.curlrc
curl -LsSf --ssl-no-revoke https://astral.sh/uv/install.sh | sh
```

Then resolve and install the project's dependencies into a local virtual environment:

```bash
uv sync
```

`uv sync` reads `pyproject.toml` and `uv.lock`, creates `.venv/`, and installs everything needed for the SQLAlchemy and Azure SQL MI demos. The SQLite demo has no third-party dependencies of its own and will run under any Python 3.13+.

## Demos

### SQLite (local)

Path: `demos/sqlite_local/`

No install beyond Python itself. Creates a local `.db` file, defines a schema, inserts rows, and queries them back. The simplest possible baseline.

```bash
uv run demos/sqlite_local/sqlite_demo.py
uv run demos/sqlite_local/sqlite_demo.py --db-path :memory:
```

See `demos/sqlite_local/README.md` for full details.

### SQLAlchemy Core (backend-agnostic)

Path: `demos/sqlalchemy_core/`

Demonstrates the same operations as the SQLite demo, but through SQLAlchemy Core 2.0. The same Python code can target SQLite, PostgreSQL, MySQL/MariaDB, or Microsoft SQL Server by changing only the connection URL.

```bash
uv run demos/sqlalchemy_core/sqlalchemy_demo.py
uv run demos/sqlalchemy_core/sqlalchemy_demo.py --backend sqlite --memory
uv run demos/sqlalchemy_core/sqlalchemy_demo.py --echo

export DATABASE_URL="postgresql+psycopg2://user:pw@host/db"
uv run demos/sqlalchemy_core/sqlalchemy_demo.py --backend postgres
```

See `demos/sqlalchemy_core/README.md` for full details.

### Azure SQL Managed Instance

Path: `demos/azure_sql_mi/`

Connects to an Azure SQL MI using Microsoft Entra Integrated auth (default) or SQL username/password, then runs a version check and a ping query.

```bash
uv run demos/azure_sql_mi/azure_sql_mi_demo.py
uv run demos/azure_sql_mi/azure_sql_mi_demo.py --auth sql
```

Requires `config.py` in the demo directory (copy from `config.example.py`). See `demos/azure_sql_mi/` for full setup notes.

## Shared Utilities

`shared/runner.py` provides two functions used by all demos:

- `print_table(rows, headers)` formats query results as a plain-text table.
- `report_result(label, passed, detail)` logs a standardised PASSED / FAILED line.

Each demo adds the repo root to `sys.path` so the import resolves regardless of which directory you run from.

## Dependencies

All third-party deps are declared in `pyproject.toml` with explicit upper-version pins, and a resolved `uv.lock` is checked in for reproducibility:

- `sqlalchemy` (Core 2.0 demo)
- `pyodbc` (Azure SQL MI demo and the `mssql` backend of the SQLAlchemy demo)
- `psycopg2-binary` (PostgreSQL backend of the SQLAlchemy demo)
- `pymysql` (MySQL/MariaDB backend of the SQLAlchemy demo)
- `typer` (CLI framework for the SQLAlchemy and Azure SQL MI demos)

The Azure SQL MI demo and the `mssql` backend of the SQLAlchemy demo also require the Microsoft ODBC Driver for SQL Server (17 or 18) installed on the host.
