# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

A collection of self-contained Python database connectivity demos, ranging from local SQLite (no install) through SQLAlchemy Core (backend-agnostic) to cloud-authenticated Azure SQL Managed Instance. Each demo is a learning artefact, not a production component.

## Commands

```bash
pip install -r requirements.txt

python demos/sqlite_local/sqlite_demo.py
python demos/sqlite_local/sqlite_demo.py --db-path :memory:

python demos/sqlalchemy_core/sqlalchemy_demo.py
python demos/sqlalchemy_core/sqlalchemy_demo.py --backend sqlite --memory
python demos/sqlalchemy_core/sqlalchemy_demo.py --echo
DATABASE_URL=postgresql+psycopg2://... python demos/sqlalchemy_core/sqlalchemy_demo.py --backend postgres

python demos/azure_sql_mi/azure_sql_mi_demo.py
python demos/azure_sql_mi/azure_sql_mi_demo.py --auth sql
```

The Azure SQL MI demo also requires `demos/azure_sql_mi/config.py` (copy from `config.example.py`); it is gitignored.

There is no test suite, no build step, no deploy. Smoke-testing is done by running each demo and inspecting output.

## Architecture

### Demo structure

Every demo lives in `demos/<name>/` and contains:

- A single executable Python file named `<name>_demo.py` (or close)
- A `README.md` covering purpose, usage, sample output
- Any per-demo config (e.g. `config.example.py`, `defaults.py`)
- No `__init__.py` — demos are scripts, not packages

### Shared runner

`shared/runner.py` provides two utilities used by every demo:

- `print_table(rows, headers, col_width=22)` — fixed-width plain-text table output
- `report_result(label, passed, detail="")` — standardised PASSED/FAILED log line

Every demo imports the runner via this idiom at the top of the script:

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from shared.runner import print_table, report_result
```

`parents[2]` resolves the repo root regardless of where the demo is invoked from. This is intentional rather than a packaging shortcut: the demos are deliberately runnable as standalone scripts (`python demos/.../demo.py`) without `pip install -e .`.

### Dependencies

A single root `requirements.txt` lists deps grouped by demo with comments. Optional drivers (e.g. `psycopg2-binary`, `pymysql` for the SQLAlchemy demo's non-SQLite backends) are listed as commented-out hints, installed manually only when needed.

### Demo invariants

When adding a new demo, preserve these:

- Default to a configuration that works without setup (in-memory database, default backend, etc.) so smoke-testing requires zero external state
- Surface backend or auth choices via CLI flags, not edits to source
- Use the shared runner for all tabular output
- Pull credentials from environment variables or a gitignored `config.py`, never hardcode
- Use parameterised queries everywhere (driver-level `?` for raw drivers, expression language for SQLAlchemy)

## Project memory

Project-scoped notes (e.g. planned demos roadmap) live in `~/.claude/projects/-Users-richard-projects-python-db/memory/`. Read `MEMORY.md` there for context on what's planned next.
