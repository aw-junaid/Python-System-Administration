#!/usr/bin/env python3
"""
auto_cleanup.py
--------------------
Context managers that guarantee resource cleanup via __exit__, even if
the code inside the `with` block raises an exception. Includes a
generic ManagedResource wrapper plus a ready-made temp-directory
example.

Usage as a library:
    from auto_cleanup import ManagedResource, temp_directory

    with ManagedResource(open_conn, close_conn) as conn:
        use(conn)   # close_conn(conn) runs even if this raises

    with temp_directory() as path:
        write_files(path)   # directory is removed afterwards regardless

Run directly for a demo:
    python auto_cleanup.py
"""

import shutil
import tempfile


class ManagedResource:
    """
    Generic context manager: calls `acquire()` on entry and
    `release(resource)` on exit -- exception or not.

    acquire  -- callable() -> resource
    release  -- callable(resource) -> None
    """

    def __init__(self, acquire, release):
        self.acquire = acquire
        self.release = release
        self.resource = None

    def __enter__(self):
        self.resource = self.acquire()
        return self.resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[auto_cleanup] Releasing resource "
              f"({'after exception' if exc_type else 'normally'})...")
        self.release(self.resource)
        return False  # never suppress the exception


class temp_directory:
    """Context manager that creates a temp directory and guarantees its
    removal on exit, exception or not."""

    def __enter__(self):
        self.path = tempfile.mkdtemp(prefix="auto_cleanup_demo_")
        print(f"[auto_cleanup] Created temp directory: {self.path}")
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[auto_cleanup] Removing temp directory: {self.path}")
        shutil.rmtree(self.path, ignore_errors=True)
        return False


if __name__ == "__main__":
    print("Demo 1: ManagedResource cleans up even when the block raises\n")

    class FakeConnection:
        def __init__(self):
            self.open = True

    def acquire_conn():
        print("  acquiring fake connection")
        return FakeConnection()

    def release_conn(conn):
        conn.open = False
        print("  fake connection closed:", not conn.open)

    try:
        with ManagedResource(acquire_conn, release_conn) as conn:
            print("  using connection...")
            raise RuntimeError("simulated failure while using the resource")
    except RuntimeError as e:
        print(f"  caught expected exception: {e}")

    print("\nDemo 2: temp_directory is removed automatically\n")
    with temp_directory() as path:
        import os
        with open(os.path.join(path, "example.txt"), "w") as f:
            f.write("hello")
        print("  wrote a file inside:", os.listdir(path))

    import os
    print(f"\nDirectory still exists after the block? {os.path.exists(path)}")
