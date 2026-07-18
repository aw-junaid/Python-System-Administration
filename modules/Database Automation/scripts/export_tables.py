#!/usr/bin/env python3
"""
export_tables.py
==================
Stream a database table (or arbitrary query result) out to a CSV or
Parquet file, fetching rows in batches rather than loading the whole
table into memory at once.

Usage
-----
    # SQLite -> CSV (works immediately, no server needed)
    python export_tables.py --db-type sqlite --db sample.db --table employees --format csv --output employees.csv

    # SQLite -> Parquet
    python export_tables.py --db-type sqlite --db sample.db --table employees --format parquet --output employees.parquet

    # MySQL -> CSV
    python export_tables.py --db-type mysql --host localhost --user root --password secret \
        --database testdb --table employees --format csv --output employees.csv

    # PostgreSQL -> Parquet
    python export_tables.py --db-type postgres --host localhost --user postgres --password secret \
        --database testdb --table employees --format parquet --output employees.parquet

If --db is omitted for sqlite, a sample database + "employees" table
is created first.

Expected output
----------------
A CSV or Parquet file (--output) containing every row of --table (or
the result of --query if given), with a header row / schema matching
the source column names. The script prints how many rows were
streamed and in how many batches.

Requirements
------------
    pip install pymysql psycopg2-binary pyarrow
    (sqlite3 is built in; pyarrow is only needed for --format parquet)
"""

import argparse
import csv
import os
import sqlite3
import sys

BATCH_SIZE = 500


def create_sample_sqlite_db(path: str) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, department TEXT, salary REAL)"
    )
    conn.execute("INSERT INTO employees (name, department, salary) VALUES ('Alice Khan', 'Engineering', 95000)")
    conn.execute("INSERT INTO employees (name, department, salary) VALUES ('Bilal Ahmed', 'Sales', 62000)")
    conn.execute("INSERT INTO employees (name, department, salary) VALUES ('Sara Malik', 'Marketing', 71000)")
    conn.commit()
    conn.close()
    print(f"[info] No --db given, created a sample SQLite database at: {path}")


def get_sqlite_cursor(db_path, query):
    conn = sqlite3.connect(db_path)
    cur = conn.execute(query)
    columns = [d[0] for d in cur.description]
    return conn, cur, columns


def get_mysql_cursor(host, port, user, password, database, query):
    import pymysql
    conn = pymysql.connect(host=host, port=port, user=user, password=password,
                            database=database, connect_timeout=5)
    cur = conn.cursor()
    cur.execute(query)
    columns = [d[0] for d in cur.description]
    return conn, cur, columns


def get_postgres_cursor(host, port, user, password, database, query):
    import psycopg2
    conn = psycopg2.connect(host=host, port=port, user=user, password=password,
                             dbname=database, connect_timeout=5)
    cur = conn.cursor()
    cur.execute(query)
    columns = [d.name for d in cur.description]
    return conn, cur, columns


def stream_to_csv(cur, columns, output) -> int:
    total = 0
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        while True:
            batch = cur.fetchmany(BATCH_SIZE)
            if not batch:
                break
            writer.writerows(batch)
            total += len(batch)
            print(f"[info] Wrote batch of {len(batch)} row(s), total so far: {total}")
    return total


def stream_to_parquet(cur, columns, output) -> int:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("[error] pyarrow is not installed. Run: pip install pyarrow")
        sys.exit(1)

    total = 0
    writer = None
    try:
        while True:
            batch = cur.fetchmany(BATCH_SIZE)
            if not batch:
                break
            columns_data = list(zip(*batch)) if batch else [[] for _ in columns]
            table = pa.table({col: list(vals) for col, vals in zip(columns, columns_data)})
            if writer is None:
                writer = pq.ParquetWriter(output, table.schema)
            writer.write_table(table)
            total += len(batch)
            print(f"[info] Wrote batch of {len(batch)} row(s), total so far: {total}")
    finally:
        if writer is not None:
            writer.close()
    return total


def main():
    parser = argparse.ArgumentParser(description="Stream a database table to CSV or Parquet.")
    parser.add_argument("--db-type", choices=["sqlite", "mysql", "postgres"], default="sqlite")
    parser.add_argument("--db", default=None, help="SQLite database file path (sqlite only)")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default=None, help="Database name (mysql/postgres)")
    parser.add_argument("--table", default="employees", help="Table to export")
    parser.add_argument("--query", default=None, help="Custom query to export instead of a whole table")
    parser.add_argument("--format", choices=["csv", "parquet"], default="csv")
    parser.add_argument("--output", default=None, help="Output file path")
    args = parser.parse_args()

    query = args.query or f"SELECT * FROM {args.table}"
    output = args.output or f"{args.table}.{args.format}"

    if args.db_type == "sqlite":
        db_path = args.db
        if db_path is None:
            db_path = "sample.db"
            create_sample_sqlite_db(db_path)
        conn, cur, columns = get_sqlite_cursor(db_path, query)

    elif args.db_type == "mysql":
        if not args.database:
            print("[error] --database is required for --db-type mysql")
            sys.exit(1)
        conn, cur, columns = get_mysql_cursor(args.host, args.port or 3306, args.user or "root",
                                               args.password, args.database, query)

    else:
        if not args.database:
            print("[error] --database is required for --db-type postgres")
            sys.exit(1)
        conn, cur, columns = get_postgres_cursor(args.host, args.port or 5432, args.user or "postgres",
                                                  args.password, args.database, query)

    print(f"[info] Exporting query result to {args.format.upper()}: {query}")

    if args.format == "csv":
        total = stream_to_csv(cur, columns, output)
    else:
        total = stream_to_parquet(cur, columns, output)

    cur.close()
    conn.close()

    print(f"[success] Exported {total} row(s) to: {output}")


if __name__ == "__main__":
    main()
