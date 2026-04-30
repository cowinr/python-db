# python-db

A collection of Python database connectivity demos, from local SQLite through to cloud-authenticated Azure SQL Managed Instance. Each demo is self-contained and can be run independently.

## Structure

```
python-db/
├── demos/
│   ├── sqlite_local/        — stdlib sqlite3, no dependencies, no server
│   └── azure_sql_mi/        — pyodbc + Microsoft Entra / SQL auth against Azure SQL MI
├── shared/
│   └── runner.py            — shared output utilities (print_table, report_result)
└── requirements.txt         — top-level dependency list
```

## Demos

### SQLite (local)

Path: `demos/sqlite_local/`

No install beyond Python itself. Creates a local `.db` file, defines a schema, inserts rows, and queries them back. The simplest possible baseline.

```bash
python demos/sqlite_local/sqlite_demo.py
python demos/sqlite_local/sqlite_demo.py --db-path :memory:
```

See `demos/sqlite_local/README.md` for full details.

### Azure SQL Managed Instance

Path: `demos/azure_sql_mi/`

Connects to an Azure SQL MI using Microsoft Entra Integrated auth (default) or SQL username/password, then runs a version check and a ping query.

```bash
python demos/azure_sql_mi/azure_sql_mi_demo.py
python demos/azure_sql_mi/azure_sql_mi_demo.py --auth sql
```

Requires `config.py` in the demo directory (copy from `config.example.py`). See `demos/azure_sql_mi/` for full setup notes.

## Shared Utilities

`shared/runner.py` provides two functions used by all demos:

- `print_table(rows, headers)` — formats query results as a plain-text table
- `report_result(label, passed, detail)` — logs a standardised PASSED / FAILED line

Each demo adds the repo root to `sys.path` so the import resolves regardless of which directory you run from.

## Dependencies

```bash
pip install -r requirements.txt
```

The SQLite demo has no third-party dependencies. `requirements.txt` covers the Azure SQL MI demo.
