#!/usr/bin/env python3
"""
connect_mysql.py
=================
Establish a connection to a MySQL/MariaDB server using pymysql and run
a test query.

Usage
-----
    python connect_mysql.py --host localhost --port 3306 --user root \
        --password secret --database testdb

    # Or via environment variables (safer than passing --password on the CLI)
    export DB_HOST=localhost DB_PORT=3306 DB_USER=root DB_PASSWORD=secret DB_NAME=testdb
    python connect_mysql.py

Expected output
----------------
- On success: server version, a list of tables in the target database,
  and the result of --query if one was given.
- On failure: a clear, actionable error message (this script does NOT
  crash with a raw traceback for common connection problems).

CAUTION
-------
This script requires a REAL, RUNNING MySQL/MariaDB server that you can
reach with the given host/port/credentials. It will not create one for
you. Double check you are pointing at a test/development database, not
production, especially if you plan to try DDL/DML statements with
--query.

Requirements
------------
    pip install pymysql
"""

import argparse
import os
import sys

try:
    import pymysql
except ImportError:
    print("[error] pymysql is not installed. Run: pip install pymysql")
    sys.exit(1)


def get_connection(host, port, user, password, database):
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        connect_timeout=5,
        cursorclass=pymysql.cursors.DictCursor,
    )


def main():
    parser = argparse.ArgumentParser(description="Connect to a MySQL/MariaDB server and run a test query.")
    parser.add_argument("--host", default=os.environ.get("DB_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("DB_PORT", 3306)))
    parser.add_argument("--user", default=os.environ.get("DB_USER", "root"))
    parser.add_argument("--password", default=os.environ.get("DB_PASSWORD", ""))
    parser.add_argument("--database", default=os.environ.get("DB_NAME", ""))
    parser.add_argument("--query", default=None, help="Optional SQL query to run after connecting")
    args = parser.parse_args()

    print(f"[info] Attempting connection to mysql://{args.user}@{args.host}:{args.port}/{args.database}")

    try:
        conn = get_connection(args.host, args.port, args.user, args.password, args.database or None)
    except pymysql.err.OperationalError as e:
        print(f"[error] Could not connect to MySQL server: {e}")
        print("        Check that: the server is running, host/port are correct, "
              "the user/password are valid, and the user has access to the database.")
        sys.exit(1)

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION() AS version")
            version = cur.fetchone()["version"]
            print(f"[success] Connected. MySQL/MariaDB server version: {version}")

            if args.database:
                cur.execute("SHOW TABLES")
                tables = [list(row.values())[0] for row in cur.fetchall()]
                print(f"[info] Tables in '{args.database}': {tables if tables else '(none found)'}")

            if args.query:
                print(f"\n[info] Running query: {args.query}")
                cur.execute(args.query)
                if cur.description:
                    rows = cur.fetchall()
                    for row in rows:
                        print(row)
                    print(f"[info] {len(rows)} row(s) returned")
                else:
                    conn.commit()
                    print(f"[info] Statement executed, {cur.rowcount} row(s) affected")
    finally:
        conn.close()
        print("[info] Connection closed")


if __name__ == "__main__":
    main()
