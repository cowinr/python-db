# SQLAlchemy Core Demo

Demonstrates SQLAlchemy Core (2.0 style) as a backend-agnostic abstraction over a relational database. The same Python code runs against SQLite, PostgreSQL, MySQL/MariaDB, or Microsoft SQL Server (including Azure SQL Managed Instance and Azure SQL Database). Only the connection URL changes.

This is the headline argument for SQLAlchemy over a raw driver: portable, pooled, parameterised access with a Pythonic query language. Compare it with `demos/sqlite_local/` (raw stdlib `sqlite3`) to see the contrast.

## What it does

1. Builds a SQLAlchemy `Engine` for the chosen backend
2. Creates a `products` table if it does not already exist (using SQLAlchemy's schema model)
3. Inserts sample rows (parameterised, batched)
4. Runs two queries built with the SQLAlchemy expression language (no raw SQL strings)
5. Prints results via the shared runner

## Prerequisites

Python 3.9 or later, plus SQLAlchemy and the optional backend drivers:

```bash
pip install -r ../../requirements.txt
```

The root `requirements.txt` includes `psycopg2-binary` (PostgreSQL), `pymysql` (MySQL / MariaDB), and `pyodbc` (SQL Server / Azure SQL MI), so all four backends work out of the box. The `pyodbc` install also requires the Microsoft ODBC Driver for SQL Server (17 or 18) on the host.

## Setting up a test database

The SQLite backend works out of the box and needs no setup. PostgreSQL and MySQL each need a running server. This directory ships start/stop scripts for both that run an ephemeral Docker container and write the generated credentials to a gitignored env file (permissions 0600). Sourcing that file before the demo run mimics the real-world pattern where passwords live in environment variables, not source.

### PostgreSQL via Docker (recommended)

```bash
./start-postgres.sh
source .demo-postgres.env
python sqlalchemy_demo.py --backend postgres
./stop-postgres.sh
```

`start-postgres.sh` runs `postgres:16` as `python-db-postgres` on port 5432, generates a random password, writes the URL to `.demo-postgres.env`. `stop-postgres.sh` stops and removes the container (`--rm`) and deletes the env file.

If port 5432 is already in use (for example by a Homebrew Postgres on the same machine), stop that first or edit `HOST_PORT` in the start script.

### PostgreSQL via Homebrew (persistent alternative)

If you have Postgres installed via Homebrew and want a long-lived local server:

```bash
brew services start postgresql@17

export DATABASE_URL="postgresql+psycopg2://$USER@localhost:5432/postgres"
python sqlalchemy_demo.py --backend postgres

brew services stop postgresql@17
```

If the default `postgres` database does not exist, create one with `createdb demo` and adjust the URL to end in `/demo`.

### MySQL via Docker (recommended)

```bash
./start-mysql.sh
source .demo-mysql.env
python sqlalchemy_demo.py --backend mysql
./stop-mysql.sh
```

`start-mysql.sh` runs `mysql:8.4` (current LTS) as `python-db-mysql` on port 3306, generates a random root password, auto-creates a database called `demo`, and writes the URL to `.demo-mysql.env`. First-run startup takes 15 to 30 seconds while MySQL initialises its data directory. `stop-mysql.sh` stops and removes the container and deletes the env file.

If port 3306 is already in use, stop the conflicting service first or edit `HOST_PORT` in the start script.

### Azure SQL Managed Instance (or Azure SQL DB / on-prem SQL Server)

There is no Docker test-server script for SQL Server here. Point the demo at an existing Azure SQL Managed Instance (or any SQL Server reachable from your machine) by setting `DATABASE_URL` to a `mssql+pyodbc` URL.

The connection requires the Microsoft ODBC Driver for SQL Server (17 or 18) on the host. On macOS:

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install msodbcsql18
```

Then build a URL with one of the two common auth shapes.

**Microsoft Entra integrated auth** (uses your existing Entra session, **dummy** credentials in the URL):

> [!important]
> You must use **dummy** credentials in the URL to prevent SQLAlchemy from appending `Integrated Security=SSPI` when the URL has no username/password. When `DATABASE_URL` also contains `Authentication=ActiveDirectoryIntegrated`, ODBC gets both and refuses.

```bash
export DATABASE_URL="mssql+pyodbc://dummy@your-instance.xxxxxxxx.database.windows.net/your_db?driver=ODBC+Driver+18+for+SQL+Server&Authentication=ActiveDirectoryIntegrated&Encrypt=yes&TrustServerCertificate=no"
python sqlalchemy_demo.py --backend mssql --probe
```

**SQL authentication** (username and password in the URL — be careful with shell history):

```bash
export DATABASE_URL="mssql+pyodbc://USER:PASSWORD@your-instance.xxxxxxxx.database.windows.net/your_db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
python sqlalchemy_demo.py --backend mssql
```

Notes:

- URL-encode any special characters in the password (`@` becomes `%40`, `:` becomes `%3A`, and so on).
- The driver name in the query string must match an installed ODBC driver exactly. Spaces become `+` in the URL.
- For Entra Integrated to work on macOS, your machine must already be signed in via the Microsoft Entra tooling. If you want token-based auth (e.g. service principal, managed identity, interactive device code) instead, see the dedicated `demos/azure_sql_mi/` demo, which uses raw `pyodbc` and is easier to extend in that direction.
- Re-running the demo will append rows to the `products` table on a real database. Either pre-create a throwaway database, or drop the table between runs.
- Sanity-check the connection first with `--probe` (see below). It runs `SELECT 1` and reports the server version without creating tables or inserting rows. Recommended for any shared database.

## Usage

Default (SQLite, file-backed):

```bash
python sqlalchemy_demo.py
```

In-memory SQLite (transient, no file written):

```bash
python sqlalchemy_demo.py --backend sqlite --memory
```

PostgreSQL, MySQL, or SQL Server / Azure SQL MI (set DATABASE_URL first):

```bash
export DATABASE_URL="postgresql+psycopg2://user:pw@host:5432/dbname"
python sqlalchemy_demo.py --backend postgres

export DATABASE_URL="mysql+pymysql://user:pw@host:3306/dbname"
python sqlalchemy_demo.py --backend mysql

export DATABASE_URL="mssql+pyodbc://@host/dbname?driver=ODBC+Driver+18+for+SQL+Server&Authentication=ActiveDirectoryIntegrated"
python sqlalchemy_demo.py --backend mssql
```

Override the URL directly (any SQLAlchemy-supported backend):

```bash
python sqlalchemy_demo.py --url sqlite:///custom.db
```

Show the SQL that SQLAlchemy generates from the Python expressions:

```bash
python sqlalchemy_demo.py --echo
```

Non-invasive connectivity check (no DDL, no inserts):

```bash
python sqlalchemy_demo.py --backend mssql --probe
```

`--probe` connects, runs `SELECT 1`, and prints the dialect, driver, and server version. The full demo creates a `products` table and inserts four rows on every run, which is fine for SQLite and the Docker test servers but not what you want when first pointing the demo at a shared database like Azure SQL MI. Use `--probe` to confirm the URL, auth, and network path are working before letting the full flow touch the schema.

Sample probe output (against in-memory SQLite):

```log
2026-04-30 10:00:00,000 [INFO] Backend: sqlite
2026-04-30 10:00:00,000 [INFO] Driver: sqlite
2026-04-30 10:00:00,001 [INFO] Probing connection (no DDL, no inserts)…

  dialect                 driver                  server_version          ping
  ----------------------  ----------------------  ----------------------  ----------------------
  sqlite                  pysqlite                3.51.0                  1

2026-04-30 10:00:00,002 [INFO] SQLAlchemy probe: PASSED
```

## SQLAlchemy URL format

```
<dialect>+<driver>://<user>:<password>@<host>:<port>/<database>
```

Examples:

- `sqlite:///./local.db` (file)
- `sqlite:///:memory:` (in-memory)
- `postgresql+psycopg2://alice:secret@db.example.com:5432/orders`
- `mysql+pymysql://alice:secret@db.example.com:3306/orders`
- `mssql+pyodbc://alice:secret@server/dbname?driver=ODBC+Driver+17+for+SQL+Server`

The dialect (`postgresql`, `mysql`, `mssql`, `sqlite`) tells SQLAlchemy which SQL dialect to emit. The driver (`psycopg2`, `pymysql`, `pyodbc`) tells it which Python package to use to talk to the database.

## What this demo highlights

Things SQLAlchemy gives you for free that the raw `sqlite3` demo does not:

- **Backend portability.** Swap the URL, the same code runs.
- **Connection pooling.** `create_engine` returns an engine with a pool already configured. No per-call connect overhead.
- **Schema in Python.** `Table`, `Column`, and `MetaData` describe the schema once and emit the right DDL for whichever backend you're using.
- **Expression language.** `select(products).where(products.c.price_gbp <= 25.00)` is parameterised by construction. There is no string formatting path to SQL injection.
- **Type-aware results.** `Result.all()` returns row objects with named column access on every backend.

Things this demo does not show but you should know about:

- **Sessions and the ORM.** SQLAlchemy ORM sits on top of Core and adds object-relational mapping. A separate demo would cover that.
- **Migrations.** `Alembic` is the standard migration tool for SQLAlchemy projects.
- **Async.** SQLAlchemy 2.0 supports async with `create_async_engine` and `asyncpg` / `aiosqlite` drivers. A separate async demo would cover that.

## Output

```log
2026-04-30 10:00:00,000 [INFO] Backend: sqlite
2026-04-30 10:00:00,000 [INFO] Driver: sqlite
2026-04-30 10:00:00,001 [INFO] Schema ready.
2026-04-30 10:00:00,002 [INFO] Inserted 4 sample rows.
2026-04-30 10:00:00,003 [INFO] Querying all products…

  id                      name                    price_gbp               created_at
  ----------------------  ----------------------  ----------------------  ----------------------
  1                       Widget A                9.99                    2026-04-30 09:00:00
  2                       Widget B                14.5                    2026-04-30 09:00:00
  3                       Gadget Pro              49.95                   2026-04-30 09:00:00
  4                       Gadget Lite             24.99                   2026-04-30 09:00:00

2026-04-30 10:00:00,004 [INFO] Querying products at £25.00 or under…

  id                      name                    price_gbp
  ----------------------  ----------------------  ----------------------
  1                       Widget A                9.99
  2                       Widget B                14.5
  4                       Gadget Lite             24.99

2026-04-30 10:00:00,005 [INFO] SQLAlchemy demo: PASSED
```

## Notes

- Re-running the script appends rows if the table already exists. Use `--memory` for a clean slate, or delete `sqlalchemy_demo.db`.
- The `*.db` pattern is gitignored at the repo root.
- Generated SQLite, Postgres, and MySQL DDL all differ slightly (autoincrement syntax, default value handling). SQLAlchemy emits the right form for whichever backend you connect to. Use `--echo` to see it.
