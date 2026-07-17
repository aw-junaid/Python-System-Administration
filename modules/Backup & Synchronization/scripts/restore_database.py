#!/usr/bin/env python3
"""
restore_database.py
======================
Reconstruct a database from a .sql backup dump (as produced by
backup_database.py or the native mysqldump/pg_dump tools).

- SQLite: executes the dump's SQL statements against a (new or
  existing) database file using Python's built-in sqlite3.
- MySQL/MariaDB: pipes the dump into the `mysql` command-line client.
- PostgreSQL: pipes the dump into the `psql` command-line client.

Usage
-----
    # SQLite (works immediately, no server needed)
    python restore_database.py --db-type sqlite --input backup.sql --db restored.db

    # MySQL (requires the `mysql` CLI tool installed and on PATH)
    python restore_database.py --db-type mysql --input backup.sql --host localhost \
        --user root --password secret --database testdb

    # PostgreSQL (requires the `psql` CLI tool installed and on PATH)
    python restore_database.py --db-type postgres --input backup.sql --host localhost \
        --user postgres --password secret --database testdb

If --input is omitted, this script first creates a sample backup file
(via the same logic as backup_database.py) and immediately restores it
into --db, so you can see the full round trip.

Expected output
----------------
- SQLite: a new/updated .db file containing every table and row from
  the dump. Prints the tables found after restore.
- MySQL/PostgreSQL: prints the CLI tool's output; on success the
  target database will contain the restored schema and data.

CAUTION
-------
- Restoring OVERWRITES data: for MySQL/PostgreSQL this runs the dump's
  statements directly against --database, which can DROP and recreate
  tables if the dump contains DROP TABLE / CREATE TABLE statements.
  Never point this at a production database without a fresh backup
  and a maintenance window.
- MySQL/PostgreSQL modes require the `mysql` / `psql` command-line
  clients to already be installed on this machine.

Requirements
------------
No Python packages required for SQLite mode. MySQL/PostgreSQL modes
require the `mysql` / `psql` command-line tools respectively (install
via your OS package manager, e.g. `apt install mysql-client` or
`apt install postgresql-client`).
"""

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys


def create_sample_backup(path: str) -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, department TEXT, salary REAL)"
    )
    conn.execute("INSERT INTO employees (name, department, salary) VALUES ('Alice Khan', 'Engineering', 95000)")
    conn.execute("INSERT INTO employees (name, department, salary) VALUES ('Bilal Ahmed', 'Sales', 62000)")
    conn.commit()
    with open(path, "w", encoding="utf-8") as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    conn.close()
    print(f"[info] No --input given, created a sample backup file at: {path}")


def restore_sqlite(input_path: str, db_path: str) -> None:
    if not os.path.exists(input_path):
        print(f"[error] Backup file not found: {input_path}")
        sys.exit(1)

    if os.path.exists(db_path):
        print(f"[warning] '{db_path}' already exists — statements will be applied on top of it.")

    conn = sqlite3.connect(db_path)
    with open(input_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    conn.executescript(sql_script)
    conn.commit()

    tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    conn.close()

    print(f"[success] Restored '{input_path}' into '{db_path}'")
    print(f"          Tables present after restore: {tables}")


def restore_mysql(input_path, host, port, user, password, database) -> None:
    if not os.path.exists(input_path):
        print(f"[error] Backup file not found: {input_path}")
        sys.exit(1)
    if shutil.which("mysql") is None:
        print("[error] 'mysql' command not found on PATH. Install MySQL client tools first.")
        sys.exit(1)

    cmd = ["mysql", "-h", host, "-P", str(port), "-u", user]
    if password:
        cmd.append(f"-p{password}")
    cmd.append(database)

    print(f"[info] Restoring '{input_path}' into MySQL database '{database}' on {host}:{port}")
    with open(input_path, "r", encoding="utf-8") as in_f:
        result = subprocess.run(cmd, stdin=in_f, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"[error] Restore failed: {result.stderr}")
        sys.exit(1)

    print(f"[success] Restore completed into database '{database}'")


def restore_postgres(input_path, host, port, user, password, database) -> None:
    if not os.path.exists(input_path):
        print(f"[error] Backup file not found: {input_path}")
        sys.exit(1)
    if shutil.which("psql") is None:
        print("[error] 'psql' command not found on PATH. Install PostgreSQL client tools first.")
        sys.exit(1)

    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password

    cmd = ["psql", "-h", host, "-p", str(port), "-U", user, "-d", database, "-f", input_path]
    print(f"[info] Restoring '{input_path}' into PostgreSQL database '{database}' on {host}:{port}")
    result = subprocess.run(cmd, env=env, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"[error] Restore failed: {result.stderr}")
        sys.exit(1)

    print(f"[success] Restore completed into database '{database}'")


def main():
    parser = argparse.ArgumentParser(description="Restore a database from a .sql backup dump.")
    parser.add_argument("--db-type", choices=["sqlite", "mysql", "postgres"], default="sqlite")
    parser.add_argument("--input", default=None, help="Path to the .sql backup file to restore")
    parser.add_argument("--db", default="restored.db", help="Target SQLite database file (sqlite only)")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default=None, help="Target database name (mysql/postgres)")
    args = parser.parse_args()

    input_path = args.input
    if args.db_type == "sqlite" and input_path is None:
        input_path = "sample_backup.sql"
        create_sample_backup(input_path)

    if args.db_type == "sqlite":
        restore_sqlite(input_path, args.db)

    elif args.db_type == "mysql":
        if not input_path or not args.database:
            print("[error] --input and --database are required for --db-type mysql")
            sys.exit(1)
        restore_mysql(input_path, args.host, args.port or 3306, args.user or "root", args.password, args.database)

    elif args.db_type == "postgres":
        if not input_path or not args.database:
            print("[error] --input and --database are required for --db-type postgres")
            sys.exit(1)
        restore_postgres(input_path, args.host, args.port or 5432, args.user or "postgres", args.password, args.database)


if __name__ == "__main__":
    main()
