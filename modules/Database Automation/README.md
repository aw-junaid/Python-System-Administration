# Database Automation

A collection of standalone Python scripts for automating common
database tasks across SQLite, MySQL/MariaDB, and PostgreSQL: connecting,
running parameterized queries, backing up/restoring, exporting/importing
data, versioning schema changes with Alembic, and pooling connections
for concurrent workloads.

Every script is independent — you only need to run the ones you
actually want to use.

> **⚠️ Caution before you run anything**
> - Scripts that write output (`--output`, `--db`, `--file`, backup/
>   restore files, etc.) will **overwrite existing files** of the same
>   name without asking for confirmation. Double-check paths first.
> - **MySQL and PostgreSQL scripts require a real, running server**
>   that you can reach with the host/port/credentials you provide.
>   These scripts do not install or start a database server for you.
>   Point them at a **test/development** database, never production,
>   until you're confident in what a script does.
> - `execute_queries.py`, `import_csv.py`, `restore_database.py`, and
>   `migration_scripts.py` can all **modify or overwrite data and
>   schema**. Take a backup first (`backup_database.py`) before running
>   any of these against a database you care about.
> - `backup_database.py` / `restore_database.py` in MySQL/PostgreSQL
>   mode shell out to the official `mysqldump`/`mysql` and
>   `pg_dump`/`psql` command-line tools. These must already be
>   installed on your machine — `pip install -r requirements.txt` does
>   **not** install them (see "System dependencies" below).
> - Backup files (`.sql`) are plain text and can contain sensitive
>   data. Store them securely; consider encrypting with
>   `gpg -c backup.sql` before sharing or archiving them.
> - Every script accepts credentials via both `--password`-style flags
>   and environment variables (`DB_HOST`, `DB_PORT`, `DB_USER`,
>   `DB_PASSWORD`, `DB_NAME`). Prefer environment variables over typing
>   passwords on the command line, since CLI arguments can be visible
>   in your shell history and process list.

---

## Installation

1. Clone this repository (or download this folder).
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # on Windows: venv\Scripts\activate
   ```
3. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Confirm your Python version is 3.8 or newer:
   ```bash
   python3 --version
   ```

### System dependencies (only needed for MySQL/PostgreSQL backup & restore)

- **MySQL/MariaDB:** install client tools so `mysqldump` and `mysql`
  are on your PATH, e.g. `sudo apt install mysql-client` (Debian/
  Ubuntu) or `brew install mysql-client` (macOS).
- **PostgreSQL:** install client tools so `pg_dump` and `psql` are on
  your PATH, e.g. `sudo apt install postgresql-client` (Debian/
  Ubuntu) or `brew install postgresql` (macOS).

SQLite requires no server and no extra system tools — it's built into
Python's standard library.

---

## Scripts overview

| # | Script | What it does |
|---|--------|---------------|
| 184 | `connect_sqlite.py` | Connect to a local SQLite file and run a query |
| 185 | `connect_mysql.py` | Connect to a MySQL/MariaDB server via `pymysql` and run a query |
| 186 | `connect_postgres.py` | Connect to a PostgreSQL server via `psycopg2` and run a query |
| 187 | `execute_queries.py` | Run parameterized DDL/DML statements safely (SQL-injection-safe) |
| 188 | `backup_database.py` | Dump schema + data into a portable `.sql` file |
| 189 | `restore_database.py` | Reconstruct a database from a `.sql` backup dump |
| 190 | `export_tables.py` | Stream a table/query result out to CSV or Parquet |
| 191 | `import_csv.py` | Bulk-load a CSV file into a relational table in batches |
| 192 | `migration_scripts.py` | Version-control schema changes with Alembic (init/revision/upgrade/downgrade) |
| 193 | `connection_pooling.py` | Demonstrate graceful connection pooling under concurrent load |

---

## Usage & expected output

### 184. `connect_sqlite.py`
```bash
python3 connect_sqlite.py --db sample.db --query "SELECT * FROM employees"
```
Prints the SQLite version and the query results as a simple table. Run
with no arguments to auto-create `sample.db` with a seeded `employees`
table.

### 185. `connect_mysql.py`
```bash
python3 connect_mysql.py --host localhost --port 3306 --user root --password secret --database testdb
```
Prints the server version and the tables in `--database`. **Requires a
running MySQL/MariaDB server** — fails with a clear error message
(not a crash) if it can't connect.

### 186. `connect_postgres.py`
```bash
python3 connect_postgres.py --host localhost --port 5432 --user postgres --password secret --database testdb
```
Prints the server version and the tables in the `public` schema.
**Requires a running PostgreSQL server** — fails with a clear error
message if it can't connect.

### 187. `execute_queries.py`
```bash
python3 execute_queries.py --db-type sqlite --db sample.db \
  --sql "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)" \
  --params "Zara Ahmed" "Finance" 68000
```
Runs the given SQL with values bound through driver placeholders
(`?` for SQLite, `%s` for MySQL/PostgreSQL) — never via string
interpolation, so untrusted input can't be used for SQL injection.
Prints returned rows for SELECTs or the affected-row count for
INSERT/UPDATE/DELETE/DDL. Run with no `--sql` to see a sample
parameterized SELECT against SQLite.

### 188. `backup_database.py`
```bash
python3 backup_database.py --db-type sqlite --db sample.db --output backup.sql
```
Writes a portable `.sql` dump. For MySQL/PostgreSQL, add `--host
--user --password --database` (requires `mysqldump`/`pg_dump`
installed — see "System dependencies").

### 189. `restore_database.py`
```bash
python3 restore_database.py --db-type sqlite --input backup.sql --db restored.db
```
Replays a `.sql` dump into a target database. For MySQL/PostgreSQL,
add `--host --user --password --database` (requires `mysql`/`psql`
installed). **Overwrites data in the target database.**

### 190. `export_tables.py`
```bash
python3 export_tables.py --db-type sqlite --db sample.db --table employees --format csv --output employees.csv
python3 export_tables.py --db-type sqlite --db sample.db --table employees --format parquet --output employees.parquet
```
Streams query results in batches (default 500 rows) to CSV or Parquet
rather than loading the whole table into memory. Works against
SQLite/MySQL/PostgreSQL via `--db-type`.

### 191. `import_csv.py`
```bash
python3 import_csv.py --db-type sqlite --db sample.db --file data.csv --table employees
```
Bulk-inserts CSV rows in batches (default 500 rows) using
`executemany()`. For SQLite, the target table is auto-created (all
TEXT columns) if missing; for MySQL/PostgreSQL the table must already
exist.

### 192. `migration_scripts.py`
```bash
python3 migration_scripts.py --action init --db-url sqlite:///sample.db
python3 migration_scripts.py --action revision --message "create employees table"
python3 migration_scripts.py --action upgrade
python3 migration_scripts.py --action downgrade
python3 migration_scripts.py --action history
python3 migration_scripts.py --action current
```
Wraps the Alembic CLI: `init` scaffolds a `migrations/` folder and
`alembic.ini` wired to `--db-url`, plus an example `models.py`;
`revision --autogenerate` detects schema changes from those models;
`upgrade`/`downgrade` apply/revert them. Run with **no arguments** to
see the full init → revision → upgrade workflow against a local
`sample.db`. Always review an autogenerated revision file before
applying it.

### 193. `connection_pooling.py`
```bash
python3 connection_pooling.py --db-url sqlite:///sample.db --workers 8 --requests 20 --pool-size 5
```
Simulates concurrent requests from multiple worker threads sharing a
SQLAlchemy connection pool, logging how long each request waited for a
pooled connection. Works with any SQLAlchemy URL, e.g.
`mysql+pymysql://user:pass@host/db` or
`postgresql+psycopg2://user:pass@host/db`.

---

## General notes

- Every script uses `argparse` — run `python3 <script>.py --help` at
  any time to see its full list of options.
- SQLite-based scripts (and modes) are safe to run with **zero
  arguments**: they auto-generate a small sample database/CSV so you
  can see expected output immediately.
- MySQL/PostgreSQL modes cannot auto-generate a server for you — you
  must have one running and reachable first.
- Scripts are independent of each other; you don't need to install or
  run all of them just to use one.
- Tested with Python 3.10+ on Linux; should work unmodified on macOS
  and Windows with the same `pip install -r requirements.txt` step
  (plus the system dependencies noted above for MySQL/PostgreSQL
  backup & restore).
