#!/usr/bin/env python3
"""
import_csv.py
===============
Bulk load data from a CSV file into a relational table efficiently,
using batched executemany() calls instead of one INSERT per row.

Usage
-----
    # SQLite (works immediately, no server needed; creates the table
    # automatically from the CSV header if it doesn't exist)
    python import_csv.py --db-type sqlite --db sample.db --file data.csv --table employees

    # MySQL
    python import_csv.py --db-type mysql --host localhost --user root --password secret \
        --database testdb --file data.csv --table employees

    # PostgreSQL
    python import_csv.py --db-type postgres --host localhost --user postgres --password secret \
        --database testdb --file data.csv --table employees

If --file is omitted, a sample CSV is generated first.

Expected output
----------------
Rows from the CSV inserted into --table in batches of --batch-size,
with progress printed after each batch and a final row count. For
SQLite, the target table is auto-created (all TEXT columns) if it
doesn't already exist; for MySQL/PostgreSQL the table must already
exist (bulk-loading into a table implies the schema is already known).

CAUTION
-------
This script uses parameterized executemany() (never string
interpolation) so CSV content cannot be used for SQL injection.
However it does NOT validate/sanitize business data — check your CSV
for duplicate keys or bad types before a large import, and consider
importing into a staging table first for production use.

Requirements
------------
    pip install pymysql psycopg2-binary
    (sqlite3 is part of the Python standard library)
"""

import argparse
import csv
import sqlite3
import sys

BATCH_SIZE_DEFAULT = 500


def create_sample_csv(path: str) -> None:
    content = (
        "name,department,salary\n"
        "Hassan Raza,Engineering,88000\n"
        "Ayesha Noor,Marketing,64000\n"
        "Bilal Farooq,Sales,59000\n"
        "Noor Fatima,Finance,72000\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[info] No --file given, created a sample CSV at: {path}")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    return header, rows


def import_sqlite(db_path, table, header, rows, batch_size) -> None:
    conn = sqlite3.connect(db_path)
    columns_sql = ", ".join(f'"{c}" TEXT' for c in header)
    conn.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({columns_sql})')

    placeholders = ", ".join(["?"] * len(header))
    columns_list = ", ".join(f'"{c}"' for c in header)
    insert_sql = f'INSERT INTO "{table}" ({columns_list}) VALUES ({placeholders})'

    total = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        conn.executemany(insert_sql, batch)
        conn.commit()
        total += len(batch)
        print(f"[info] Inserted batch of {len(batch)} row(s), total so far: {total}")

    conn.close()
    print(f"[success] Imported {total} row(s) into SQLite table '{table}' in '{db_path}'")


def import_mysql(host, port, user, password, database, table, header, rows, batch_size) -> None:
    import pymysql
    conn = pymysql.connect(host=host, port=port, user=user, password=password,
                            database=database, connect_timeout=5)
    placeholders = ", ".join(["%s"] * len(header))
    columns_list = ", ".join(f"`{c}`" for c in header)
    insert_sql = f"INSERT INTO `{table}` ({columns_list}) VALUES ({placeholders})"

    total = 0
    with conn.cursor() as cur:
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            cur.executemany(insert_sql, batch)
            conn.commit()
            total += len(batch)
            print(f"[info] Inserted batch of {len(batch)} row(s), total so far: {total}")
    conn.close()
    print(f"[success] Imported {total} row(s) into MySQL table '{table}' in database '{database}'")


def import_postgres(host, port, user, password, database, table, header, rows, batch_size) -> None:
    import psycopg2
    import psycopg2.extras
    conn = psycopg2.connect(host=host, port=port, user=user, password=password,
                             dbname=database, connect_timeout=5)
    columns_list = ", ".join(f'"{c}"' for c in header)
    insert_sql = f'INSERT INTO "{table}" ({columns_list}) VALUES %s'

    total = 0
    with conn.cursor() as cur:
        for i in range(0, len(rows), batch_size):
            batch = [tuple(r) for r in rows[i:i + batch_size]]
            psycopg2.extras.execute_values(cur, insert_sql, batch)
            conn.commit()
            total += len(batch)
            print(f"[info] Inserted batch of {len(batch)} row(s), total so far: {total}")
    conn.close()
    print(f"[success] Imported {total} row(s) into PostgreSQL table '{table}' in database '{database}'")


def main():
    parser = argparse.ArgumentParser(description="Bulk load a CSV file into a relational database table.")
    parser.add_argument("--db-type", choices=["sqlite", "mysql", "postgres"], default="sqlite")
    parser.add_argument("--db", default="sample.db", help="SQLite database file path (sqlite only)")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default=None, help="Database name (mysql/postgres)")
    parser.add_argument("--file", default=None, help="Path to the CSV file to import")
    parser.add_argument("--table", default="employees", help="Target table name")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE_DEFAULT)
    args = parser.parse_args()

    csv_path = args.file
    if csv_path is None:
        csv_path = "sample_import.csv"
        create_sample_csv(csv_path)

    header, rows = read_csv(csv_path)
    print(f"[info] Read {len(rows)} row(s) from '{csv_path}' with columns: {header}")

    if args.db_type == "sqlite":
        import_sqlite(args.db, args.table, header, rows, args.batch_size)

    elif args.db_type == "mysql":
        if not args.database:
            print("[error] --database is required for --db-type mysql")
            sys.exit(1)
        import_mysql(args.host, args.port or 3306, args.user or "root", args.password,
                     args.database, args.table, header, rows, args.batch_size)

    elif args.db_type == "postgres":
        if not args.database:
            print("[error] --database is required for --db-type postgres")
            sys.exit(1)
        import_postgres(args.host, args.port or 5432, args.user or "postgres", args.password,
                         args.database, args.table, header, rows, args.batch_size)


if __name__ == "__main__":
    main()
