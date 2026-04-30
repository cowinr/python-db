# Python Database Access Options

A survey of state-of-the-art mechanisms for accessing databases from Python, covering the driver tier, abstraction layers, async patterns, and connection pooling. Written as context for extending this repo with additional demos.

## The Three Layers

```
Your code
────────────────────────
ORM / query builder       ← SQLAlchemy ORM, Peewee, Tortoise
SQL abstraction layer     ← SQLAlchemy Core, "databases" library
Raw DB-API 2.0 driver     ← pyodbc, psycopg3, pymysql, etc.
────────────────────────
Database wire protocol
```

Most real projects live at the middle layer (SQLAlchemy Core) or ORM layer, with the raw driver underneath as a dependency.

## Driver Tier

| Database | Sync driver | Async driver |
|---|---|---|
| SQL Server / Azure SQL MI | `pyodbc` (what you have), `pymssql` | no native async; wrap via `aioodbc` |
| PostgreSQL | `psycopg2` (C binding, ubiquitous), `psycopg3` (modern, async-native) | `asyncpg` (fastest), `psycopg3` |
| MySQL | `mysqlclient` (C, fast), `PyMySQL` (pure Python) | `aiomysql`, `asyncmy` |
| MariaDB | `mariadb` (official C connector) or any MySQL driver | `aiomysql` works |
| SQLite | stdlib `sqlite3` | `aiosqlite` |
| MongoDB | `pymongo` | `motor` |
| Redis | `redis-py` (has async mode built in) | same |

## SQLAlchemy

SQLAlchemy is effectively the standard for anything beyond a one-off script. Two distinct APIs in one library.

**Core** — SQL expression language, no ORM magic:

```python
from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://user:pw@host/db")
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1 AS ping"))
```

**ORM** — full Active Record / Data Mapper pattern. Worth knowing but not what you need for connectivity demos.

SQLAlchemy's `create_engine` connection strings are the lingua franca:

```
mssql+pyodbc://...
postgresql+psycopg2://...
mysql+mysqlconnector://...
sqlite:///local.db
```

One abstraction layer, swap the dialect underneath.

## Async

If you're building anything with FastAPI, async workers, or high-concurrency pipelines, async drivers matter. `asyncpg` (Postgres) is the fastest Python DB driver that exists. `psycopg3` supports both sync and async with the same API, which is elegant.

`databases` library (by Encode, who make Starlette/FastAPI) wraps async drivers behind a single interface:

```python
import databases
db = databases.Database("postgresql://...")
await db.fetch_all("SELECT * FROM foo")
```

## Connection Pooling

Raw `pyodbc.connect()` creates a new connection each time — fine for a test script, bad for any real workload. SQLAlchemy's engine has a built-in pool (configurable size, overflow, recycle). For async, `asyncpg` has its own pool. This is one of the strongest arguments for using SQLAlchemy Core even when you don't need the ORM.

## Suggested Demo Structure

```
python-db/
├── demos/
│   ├── azure_sql_mi/          ← what you have now (pyodbc, Entra auth)
│   ├── sqlite_local/          ← stdlib only, no install; good "hello world" baseline
│   ├── postgres_sqlalchemy/   ← SQLAlchemy Core over psycopg2, shows pooling + dialect swap
│   ├── mysql_mariadb/         ← mysql-connector or PyMySQL; covers both flavours
│   ├── postgres_async/        ← asyncpg + asyncio; shows the async pattern
│   └── sqlalchemy_orm/        ← optional: shows ORM mapping over the SQLite demo
├── shared/
│   └── runner.py              ← common "run these queries, print results" harness
└── requirements.txt           ← all deps, grouped by demo
```

The SQLite demo is worth doing first — it needs nothing installed, runs anywhere, and makes a clean "simplest possible case" to contrast against the Entra-authenticated Azure MI demo at the other end of the complexity spectrum.

The recommendation is to use SQLAlchemy Core as the abstraction for new demos rather than raw drivers. The API is consistent across all dialects, it handles pooling automatically, and swapping the connection string is a good illustration of the portability story. Pair that with one raw-driver demo (the SQLite stdlib one) to show what's under the hood.
