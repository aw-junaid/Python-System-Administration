#!/usr/bin/env python3
"""
connection_pooling.py
========================
Manage a pool of database connections gracefully under concurrent load
using SQLAlchemy's connection pool, instead of opening a brand-new
connection per request (which is slow and can exhaust the database's
max-connections limit).

Usage
-----
    # SQLite demo (works immediately, no server needed): simulates 20
    # "requests" from 8 concurrent worker threads sharing a pool of 5
    # connections.
    python connection_pooling.py --db-url sqlite:///sample.db --workers 8 --requests 20 --pool-size 5

    # MySQL
    python connection_pooling.py --db-url "mysql+pymysql://root:secret@localhost/testdb" \
        --workers 20 --requests 100 --pool-size 10

    # PostgreSQL
    python connection_pooling.py --db-url "postgresql+psycopg2://postgres:secret@localhost/testdb" \
        --workers 20 --requests 100 --pool-size 10

Expected output
----------------
Per-request log lines showing which worker ran a query and how long it
waited to obtain a connection from the pool, followed by a summary:
total requests completed, pool size used, and total elapsed time. This
demonstrates that connections are reused/queued rather than opened
fresh for every request.

CAUTION
-------
--pool-size controls how many real connections are kept open at once.
Setting this too high against a shared/production database can exhaust
its max_connections limit and affect other applications; setting it
too low under heavy concurrency will make requests queue and slow
down. Size it based on your database server's configured limits.

Requirements
------------
    pip install sqlalchemy pymysql psycopg2-binary
    (pymysql/psycopg2 only needed if --db-url targets MySQL/PostgreSQL;
    SQLite works with SQLAlchemy out of the box)
"""

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import QueuePool
except ImportError:
    print("[error] SQLAlchemy is not installed. Run: pip install sqlalchemy")
    sys.exit(1)


def build_engine(db_url: str, pool_size: int, max_overflow: int):
    is_sqlite = db_url.startswith("sqlite")
    if is_sqlite:
        # SQLite is file/memory based and doesn't benefit from a real
        # multi-connection pool the way a network database does, but we
        # still demonstrate the pooling API and its wait/timeout behavior.
        engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=10,
            connect_args={"check_same_thread": False},
        )
    else:
        engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=10,
            pool_pre_ping=True,  # detect and replace dropped connections
        )
    return engine


def ensure_sample_table(engine):
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS pool_demo (id INTEGER PRIMARY KEY, worker TEXT, ts REAL)"
        ))
        conn.commit()


def run_request(engine, worker_id: int, request_id: int):
    start = time.perf_counter()
    with engine.connect() as conn:
        acquired = time.perf_counter()
        conn.execute(
            text("INSERT INTO pool_demo (worker, ts) VALUES (:w, :t)"),
            {"w": f"worker-{worker_id}", "t": time.time()},
        )
        conn.commit()
    finished = time.perf_counter()

    wait_ms = (acquired - start) * 1000
    query_ms = (finished - acquired) * 1000
    print(f"[worker-{worker_id}] request {request_id}: waited {wait_ms:.1f} ms for a connection, "
          f"query took {query_ms:.1f} ms")


def main():
    parser = argparse.ArgumentParser(description="Demonstrate graceful connection pooling under concurrent load.")
    parser.add_argument("--db-url", default="sqlite:///sample.db",
                         help="SQLAlchemy database URL, e.g. sqlite:///file.db, "
                              "mysql+pymysql://user:pass@host/db, postgresql+psycopg2://user:pass@host/db")
    parser.add_argument("--workers", type=int, default=8, help="Number of concurrent worker threads")
    parser.add_argument("--requests", type=int, default=20, help="Total number of simulated requests")
    parser.add_argument("--pool-size", type=int, default=5, help="Number of persistent pooled connections")
    parser.add_argument("--max-overflow", type=int, default=5, help="Extra temporary connections allowed beyond pool-size")
    args = parser.parse_args()

    print(f"[info] Building engine for {args.db_url} (pool_size={args.pool_size}, max_overflow={args.max_overflow})")
    engine = build_engine(args.db_url, args.pool_size, args.max_overflow)
    ensure_sample_table(engine)

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(run_request, engine, i % args.workers, i)
            for i in range(args.requests)
        ]
        for f in as_completed(futures):
            f.result()  # re-raise any exception from a worker
    elapsed = time.perf_counter() - start

    engine.dispose()
    print(f"\n[success] Completed {args.requests} request(s) using {args.workers} worker(s) "
          f"against a pool of {args.pool_size} connection(s) in {elapsed:.2f}s total")


if __name__ == "__main__":
    main()
