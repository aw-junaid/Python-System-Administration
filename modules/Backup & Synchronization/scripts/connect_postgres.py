#!/usr/bin/env python3
"""
connect_postgres.py
=====================
Establish a connection to a PostgreSQL server using psycopg2 and run a
test query.

Usage
-----
    python connect_postgres.py --host localhost --port 5432 --user postgres \
        --password secret --database testdb

    # Or via environment variables (safer than passing --password on the CLI)
    export DB_HOST=localhost DB_PORT=5432 DB_USER=postgres DB_PASSWORD=secret DB_NAME=testdb
    python connect_postgres.py

Expected output
----------------
- On success: server version, a list of tables in the "public" schema,
  and the result of --query if one was given.
- On failure: a clear, actionable error message (no raw traceback for
  common connection problems).

CAUTION
-------
This script requires a REAL, RUNNING PostgreSQL server that you can
reach with the given host/port/credentials. It will not create one for
you. Double check you are pointing at a test/development database, not
production, especially if you plan to try DDL/DML statements with
--query.

Requirements
------------
    pip install psycopg2-binary
"""

import argparse
import os
import sys

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("[error] psycopg2 is not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


def get_connection(host, port, user, password, database):
    return psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=database,
        connect_timeout=5,
    )


def main():
    parser = argparse.ArgumentParser(description="Connect to a PostgreSQL server and run a test query.")
    parser.add_argument("--host", default=os.environ.get("DB_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("DB_PORT", 5432)))
    parser.add_argument("--user", default=os.environ.get("DB_USER", "postgres"))
    parser.add_argument("--password", default=os.environ.get("DB_PASSWORD", ""))
    parser.add_argument("--database", default=os.environ.get("DB_NAME", "postgres"))
    parser.add_argument("--query", default=None, help="Optional SQL query to run after connecting")
    args = parser.parse_args()

    print(f"[info] Attempting connection to postgresql://{args.user}@{args.host}:{args.port}/{args.database}")

    try:
        conn = get_connection(args.host, args.port, args.user, args.password, args.database)
    except psycopg2.OperationalError as e:
        print(f"[error] Could not connect to PostgreSQL server: {e}")
        print("        Check that: the server is running, host/port are correct, "
              "the user/password are valid, and the database exists.")
        sys.exit(1)

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()["version"]
            print(f"[success] Connected. {version}")

            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
            tables = [row["table_name"] for row in cur.fetchall()]
            print(f"[info] Tables in schema 'public': {tables if tables else '(none found)'}")

            if args.query:
                print(f"\n[info] Running query: {args.query}")
                cur.execute(args.query)
                if cur.description:
                    rows = cur.fetchall()
                    for row in rows:
                        print(dict(row))
                    print(f"[info] {len(rows)} row(s) returned")
                else:
                    conn.commit()
                    print(f"[info] Statement executed, {cur.rowcount} row(s) affected")
    finally:
        conn.close()
        print("[info] Connection closed")


if __name__ == "__main__":
    main()
