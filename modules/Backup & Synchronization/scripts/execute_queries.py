#!/usr/bin/env python3
"""
execute_queries.py
====================
Run parameterized DDL/DML SQL statements safely (never using raw
string interpolation, which prevents SQL injection) against SQLite,
MySQL, or PostgreSQL.

Usage
-----
    # SQLite (default, no server needed)
    python execute_queries.py --db-type sqlite --db sample.db \
        --sql "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)" \
        --params "Zara Ahmed" "Finance" 68000

    # MySQL
    python execute_queries.py --db-type mysql --host localhost --user root \
        --password secret --database testdb \
        --sql "INSERT INTO employees (name, department) VALUES (%s, %s)" \
        --params "Hamza Iqbal" "Sales"

    # PostgreSQL
    python execute_queries.py --db-type postgres --host localhost --user postgres \
        --password secret --database testdb \
        --sql "INSERT INTO employees (name, department) VALUES (%s, %s)" \
        --params "Noor Fatima" "Marketing"

If --sql is omitted, the script runs against a local sample SQLite
database (creating/seeding a small "employees" table) to demonstrate
parameterized SELECT/INSERT/UPDATE statements end-to-end.

Expected output
----------------
- The SQL statement being executed (with parameters shown separately,
  never interpolated into the string).
- For SELECT-like statements: the returned rows.
- For INSERT/UPDATE/DELETE/DDL: number of rows affected and a commit
  confirmation.

CAUTION
-------
Parameter placeholders differ by driver: SQLite uses "?", MySQL/Postgres
use "%s". Always pass values through --params (or the run_query()
function's `params` argument) — never build SQL strings with f-strings
or .format() using untrusted input, as that reintroduces SQL injection
risk that this script is specifically designed to avoid.

Requirements
------------
    pip install pymysql psycopg2-binary
    (sqlite3 is part of the Python standard library; only install the
    driver for the --db-type you actually plan to use)
"""

import argparse
import sqlite3
import sys


def run_query_sqlite(db_path, sql, params):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _ensure_sample_schema_sqlite(conn)
    try:
        cur = conn.execute(sql, params)
        _print_result_generic(cur, params, conn, driver="sqlite3")
    finally:
        conn.close()


def _ensure_sample_schema_sqlite(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            salary REAL
        )
        """
    )
    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)",
            [("Alice Khan", "Engineering", 95000), ("Bilal Ahmed", "Sales", 62000)],
        )
        conn.commit()


def run_query_mysql(host, port, user, password, database, sql, params):
    try:
        import pymysql
    except ImportError:
        print("[error] pymysql is not installed. Run: pip install pymysql")
        sys.exit(1)

    conn = pymysql.connect(host=host, port=port, user=user, password=password,
                            database=database, cursorclass=pymysql.cursors.DictCursor,
                            connect_timeout=5)
    try:
        with conn.cursor() as cur:
            _print_result_generic(cur, params, conn, driver="pymysql", sql=sql)
    finally:
        conn.close()


def run_query_postgres(host, port, user, password, database, sql, params):
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        print("[error] psycopg2 is not installed. Run: pip install psycopg2-binary")
        sys.exit(1)

    conn = psycopg2.connect(host=host, port=port, user=user, password=password,
                             dbname=database, connect_timeout=5)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            _print_result_generic(cur, params, conn, driver="psycopg2", sql=sql)
    finally:
        conn.close()


def _print_result_generic(cur, params, conn, driver, sql=None):
    if driver == "sqlite3":
        print(f"[info] Executed via sqlite3. Params: {params}")
    else:
        cur.execute(sql, params)
        print(f"[info] Executed via {driver}. SQL: {sql}  Params: {params}")

    if cur.description:
        rows = cur.fetchall()
        for row in rows:
            print(dict(row) if driver != "sqlite3" else tuple(row))
        print(f"[info] {len(rows)} row(s) returned")
    else:
        conn.commit()
        print(f"[success] Statement committed. Rows affected: {cur.rowcount}")


def main():
    parser = argparse.ArgumentParser(description="Safely run parameterized SQL against SQLite/MySQL/PostgreSQL.")
    parser.add_argument("--db-type", choices=["sqlite", "mysql", "postgres"], default="sqlite")
    parser.add_argument("--db", default="sample.db", help="SQLite database file path (sqlite only)")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default=None)
    parser.add_argument("--sql", default=None, help="SQL statement with placeholders (? for sqlite, %s for mysql/postgres)")
    parser.add_argument("--params", nargs="*", default=[], help="Values to bind to the SQL placeholders, in order")
    args = parser.parse_args()

    sql = args.sql or "SELECT * FROM employees WHERE department = ?"
    params = tuple(args.params) if args.params else ("Engineering",)

    if args.db_type == "sqlite":
        if not args.sql:
            print("[info] No --sql given, running a sample parameterized SELECT against sample.db")
        run_query_sqlite(args.db, sql, params)

    elif args.db_type == "mysql":
        if not args.sql:
            print("[error] --sql is required for --db-type mysql (a running server is needed)")
            sys.exit(1)
        run_query_mysql(args.host, args.port or 3306, args.user or "root", args.password,
                         args.database, sql, params)

    elif args.db_type == "postgres":
        if not args.sql:
            print("[error] --sql is required for --db-type postgres (a running server is needed)")
            sys.exit(1)
        run_query_postgres(args.host, args.port or 5432, args.user or "postgres", args.password,
                            args.database, sql, params)


if __name__ == "__main__":
    main()
