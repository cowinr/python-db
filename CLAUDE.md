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

A single root `requirements.txt` lists deps grouped by demo with comments. All declared deps are real installs (no commented-out hints) so a fresh `pip install -r requirements.txt` leaves every backend usable.

### Test-server scripts

Backends that need a running server (currently Postgres and MySQL in `demos/sqlalchemy_core/`) ship a `start-<backend>.sh` / `stop-<backend>.sh` pair in the demo directory. The convention:

- Run an ephemeral `--rm` Docker container with a fixed name (`python-db-<backend>`)
- Generate a random password with `openssl rand -hex 16`
- Write the resulting `DATABASE_URL` into a gitignored `.demo-<backend>.env` file (`umask 077`, perms 0600)
- User sources that file before invoking the demo
- Stop script removes the container and the env file
- Both scripts gate on `docker info > /dev/null 2>&1` so they fail with a clean message when Docker Desktop isn't running

The `*.env` and `*.db` patterns are gitignored at the repo root.

### Demo invariants

When adding a new demo, preserve these:

- Default to a configuration that works without setup (in-memory database, default backend, etc.) so smoke-testing requires zero external state
- Surface backend or auth choices via CLI flags, not edits to source
- Use the shared runner for all tabular output
- Pull credentials from environment variables or a gitignored `config.py`, never hardcode
- Use parameterised queries everywhere (driver-level `?` for raw drivers, expression language for SQLAlchemy)

## Security checks

Before sharing any demo, run the four-check pre-share gate prescribed by the `dev-standards:hansard-python` skill:

```bash
uvx ruff check .
uvx bandit -r demos/<name>/
uvx detect-secrets scan --baseline .secrets.baseline
uvx pip-audit
```

Repo-specific notes:

- `.secrets.baseline` at the repo root records known false-positive Basic Auth Credentials hits (illustrative URL placeholders like `user:pw@host` in the demo READMEs and docstrings). Always scan with `--baseline .secrets.baseline` so the baseline suppresses these. New secret-shaped strings still raise alerts. To re-baseline after adding more known placeholders, run `uvx detect-secrets scan > .secrets.baseline`.
- `pip-audit` will not run against `requirements.txt` directly because the deps use `>=` constraints rather than exact pins or hashes. Run it without arguments (`uvx pip-audit`) to audit the active Python environment instead — that's where the deps are actually installed via `pip install -r requirements.txt`.

## Project memory

Project-scoped notes (e.g. planned demos roadmap) live in `~/.claude/projects/-Users-richard-projects-python-db/memory/`. Read `MEMORY.md` there for context on what's planned next.
