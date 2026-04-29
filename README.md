# DB Connectivity Test

A minimal script to verify connectivity to the Azure SQL Managed Instance before running the full extract pipeline.

## What it does

Connects to the target database and runs two queries:

- `SELECT @@VERSION` — confirms the server is reachable and returns its version string
- `SELECT 1 AS ping` — confirms a result set can be returned

Exits with code `0` on success, `1` on failure.

## Prerequisites

- ODBC Driver for SQL Server installed on the host machine (default: ODBC Driver 17)
- `config.py` present in this directory (see setup below)
- For integrated auth: your Entra account must have at least `CONNECT` permission on the target database

## Setup

1. Copy the example config and fill in your details:

   ```
   cp config.example.py config.py
   ```

2. Edit `config.py` with the correct `SERVER` and `DATABASE` values. This file is gitignored and must never be committed.

3. Install the dependency:

   ```
   python -m pip install -r requirements.txt
   ```

## Usage

**Integrated (Entra) authentication — default:**

```
python db_connect_test.py
```

**SQL Server username/password:**

```
python db_connect_test.py --auth sql
```

You will be prompted for credentials at runtime; nothing is stored.

## Output

```
Connecting to your-instance.xxx.database.windows.net / your_db using integrated auth…

Server version:
  Microsoft SQL Server 2019 (RTM-CU…) …

Ping result: 1

Connection test PASSED.
```