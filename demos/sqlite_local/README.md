# SQLite Local Demo

Demonstrates local SQLite database access using only the Python standard library. No driver to install, no server to run, no credentials to manage.

This is the baseline demo — the simplest possible database interaction in Python. Compare it with `db_connect_test.py` at the repo root to see the full range from local stdlib to cloud-authenticated Azure SQL Managed Instance.

## What it does

1. Opens (or creates) a local `.db` file
2. Creates a `products` table if it does not already exist
3. Inserts four sample rows using parameterised queries
4. Queries all rows back and prints them
5. Runs a filtered query (products at or under a given price)

## Prerequisites

Python 3.13 or later. No third-party packages required — `sqlite3` is part of the standard library, and this demo deliberately uses stdlib `argparse` to avoid pulling in any other dependencies.

## Usage

Run from this directory with plain `python`, or from the repo root via `uv run`:

```bash
python sqlite_demo.py
uv run demos/sqlite_local/sqlite_demo.py
```

Use a custom database file path:

```bash
python sqlite_demo.py --db-path /tmp/my_test.db
```

Use an in-memory database (discarded on exit — useful for testing):

```bash
python sqlite_demo.py --db-path :memory:
```

## Output

```
2026-04-30 09:00:00,000 [INFO] Using database: /path/to/demo.db
2026-04-30 09:00:00,001 [INFO] Schema ready.
2026-04-30 09:00:00,002 [INFO] Inserted 4 sample rows.
2026-04-30 09:00:00,003 [INFO] Querying all products…

  id                    name                  price_gbp             created_at
  --------------------  --------------------  --------------------  --------------------
  1                     Widget A              9.99                  2026-04-30 09:00:00
  2                     Widget B              14.5                  2026-04-30 09:00:00
  3                     Gadget Pro            49.95                 2026-04-30 09:00:00
  4                     Gadget Lite           24.99                 2026-04-30 09:00:00

2026-04-30 09:00:00,004 [INFO] Querying products at £25.00 or under…

  id                    name                  price_gbp
  --------------------  --------------------  --------------------
  1                     Widget A              9.99
  2                     Widget B              14.5
  4                     Gadget Lite           24.99

2026-04-30 09:00:00,005 [INFO] Demo complete.
```

## Notes

- Re-running the script appends rows to the table if `demo.db` already exists. Use `--db-path :memory:` or delete `demo.db` between runs for a clean slate.
- All queries use parameterised placeholders (`?`) rather than string formatting — this prevents SQL injection and is the correct pattern to follow in production code.
- The `demo.db` file is gitignored at the repo root.
