#!/usr/bin/env python3
"""
connect_sqlite.py
==================
Connect to a local file-based SQLite database, create a sample table
if the database is new, and demonstrate basic insert/select operations.

Usage
-----
    python connect_sqlite.py --db mydata.db
    python connect_sqlite.py --db mydata.db --query "SELECT * FROM employees"

If --db is omitted, a sample database (sample.db) is created/used in
the current directory with a small "employees" table pre-populated.

Expected output
----------------
- Connection confirmation and SQLite version.
- If the target table doesn't exist yet, it is created and seeded
  with sample rows.
- The result of --query (or a default "SELECT * FROM employees") is
  printed as a table.

Requirements
------------
No third-party packages required (sqlite3 is part of the Python
standard library).
"""

import argparse
import os
import sqlite3


def ensure_sample_table(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            salary REAL
        )
        """
    )
    cur.execute("SELECT COUNT(*) FROM employees")
    count = cur.fetchone()[0]
    if count == 0:
        cur.executemany(
            "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)",
            [
                ("Alice Khan", "Engineering", 95000),
                ("Bilal Ahmed", "Sales", 62000),
                ("Sara Malik", "Marketing", 71000),
            ],
        )
        conn.commit()
        print("[info] Seeded 'employees' table with sample rows")


def print_results(cur: sqlite3.Cursor) -> None:
    columns = [desc[0] for desc in cur.description] if cur.description else []
    rows = cur.fetchall()
    if columns:
        print(" | ".join(columns))
        print("-" * (len(" | ".join(columns))))
    for row in rows:
        print(" | ".join(str(v) for v in row))
    print(f"\n[info] {len(rows)} row(s) returned")


def main():
    parser = argparse.ArgumentParser(description="Connect to a SQLite database and run a query.")
    parser.add_argument("--db", default=None, help="Path to the SQLite database file")
    parser.add_argument("--query", default=None, help="SQL query to run (defaults to selecting sample data)")
    args = parser.parse_args()

    db_path = args.db
    new_db = db_path is None or not os.path.exists(db_path)
    if db_path is None:
        db_path = "sample.db"

    conn = sqlite3.connect(db_path)
    print(f"[success] Connected to SQLite database: {db_path}")
    print(f"          SQLite library version: {sqlite3.sqlite_version}")

    if new_db:
        ensure_sample_table(conn)

    query = args.query or "SELECT * FROM employees"
    try:
        cur = conn.execute(query)
        print(f"\n[info] Running query: {query}")
        print_results(cur)
    except sqlite3.Error as e:
        print(f"[error] Query failed: {e}")
    finally:
        conn.close()
        print("[info] Connection closed")


if __name__ == "__main__":
    main()
