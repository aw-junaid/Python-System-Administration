#!/usr/bin/env python3
"""
backup_database.py
====================
Dump a database's schema and data into a portable .sql file.

- SQLite: uses Python's built-in sqlite3 `iterdump()` — no external
  tools needed.
- MySQL/MariaDB: shells out to the `mysqldump` command-line tool.
- PostgreSQL: shells out to the `pg_dump` command-line tool.

Usage
-----
    # SQLite (works immediately, no server needed)
    python backup_database.py --db-type sqlite --db sample.db --output backup.sql

    # MySQL (requires the `mysqldump` CLI tool installed and on PATH)
    python backup_database.py --db-type mysql --host localhost --user root \
        --password secret --database testdb --output backup.sql

    # PostgreSQL (requires the `pg_dump` CLI tool installed and on PATH)
    python backup_database.py --db-type postgres --host localhost --user postgres \
        --password secret --database testdb --output backup.sql

If --db is omitted for sqlite, a sample database is created first so
you can see a full backup run immediately.

Expected output
----------------
A single .sql file (--output) containing CREATE TABLE statements and
INSERT statements that fully reproduce the database. The script prints
the output path and file size on success.

CAUTION
-------
- Backups can contain sensitive data. Store --output files securely
  and don't commit them to public version control.
- MySQL/PostgreSQL modes require `mysqldump`/`pg_dump` to already be
  installed on this machine (they ship with the respective database's
  client tools, not with this script or with pip).
- This script does NOT encrypt backups. Encrypt sensitive dumps
  yourself (e.g. `gpg -c backup.sql`) before storing/transmitting them.

Requirements
------------
No Python packages required for SQLite mode. MySQL/PostgreSQL modes
require the `mysqldump` / `pg_dump` command-line tools respectively
(install via your OS package manager, e.g. `apt install mysql-client`
or `apt install postgresql-client`).
"""

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys


def create_sample_sqlite_db(path: str) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, department TEXT, salary REAL)"
    )
    conn.execute("INSERT INTO employees (name, department, salary) VALUES ('Alice Khan', 'Engineering', 95000)")
    conn.execute("INSERT INTO employees (name, department, salary) VALUES ('Bilal Ahmed', 'Sales', 62000)")
    conn.commit()
    conn.close()
    print(f"[info] No --db given, created a sample SQLite database at: {path}")


def backup_sqlite(db_path: str, output: str) -> None:
    if not os.path.exists(db_path):
        print(f"[error] Database file not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    with open(output, "w", encoding="utf-8") as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    conn.close()

    size = os.path.getsize(output)
    print(f"[success] SQLite backup written to: {output} ({size} bytes)")


def backup_mysql(host, port, user, password, database, output) -> None:
    if shutil.which("mysqldump") is None:
        print("[error] 'mysqldump' command not found on PATH. Install MySQL client tools first.")
        sys.exit(1)

    cmd = ["mysqldump", "-h", host, "-P", str(port), "-u", user]
    if password:
        cmd.append(f"-p{password}")
    cmd.append(database)

    print(f"[info] Running: mysqldump -h {host} -P {port} -u {user} -p*** {database} > {output}")
    with open(output, "w", encoding="utf-8") as out_f:
        result = subprocess.run(cmd, stdout=out_f, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"[error] mysqldump failed: {result.stderr}")
        sys.exit(1)

    size = os.path.getsize(output)
    print(f"[success] MySQL backup written to: {output} ({size} bytes)")


def backup_postgres(host, port, user, password, database, output) -> None:
    if shutil.which("pg_dump") is None:
        print("[error] 'pg_dump' command not found on PATH. Install PostgreSQL client tools first.")
        sys.exit(1)

    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password

    cmd = ["pg_dump", "-h", host, "-p", str(port), "-U", user, "-f", output, database]
    print(f"[info] Running: pg_dump -h {host} -p {port} -U {user} -f {output} {database}")
    result = subprocess.run(cmd, env=env, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"[error] pg_dump failed: {result.stderr}")
        sys.exit(1)

    size = os.path.getsize(output)
    print(f"[success] PostgreSQL backup written to: {output} ({size} bytes)")


def main():
    parser = argparse.ArgumentParser(description="Backup a database's schema and data to a portable SQL file.")
    parser.add_argument("--db-type", choices=["sqlite", "mysql", "postgres"], default="sqlite")
    parser.add_argument("--db", default=None, help="SQLite database file path (sqlite only)")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default=None, help="Database name (mysql/postgres)")
    parser.add_argument("--output", default="backup.sql", help="Path for the output .sql backup file")
    args = parser.parse_args()

    if args.db_type == "sqlite":
        db_path = args.db
        if db_path is None:
            db_path = "sample.db"
            create_sample_sqlite_db(db_path)
        backup_sqlite(db_path, args.output)

    elif args.db_type == "mysql":
        if not args.database:
            print("[error] --database is required for --db-type mysql")
            sys.exit(1)
        backup_mysql(args.host, args.port or 3306, args.user or "root", args.password, args.database, args.output)

    elif args.db_type == "postgres":
        if not args.database:
            print("[error] --database is required for --db-type postgres")
            sys.exit(1)
        backup_postgres(args.host, args.port or 5432, args.user or "postgres", args.password, args.database, args.output)


if __name__ == "__main__":
    main()
