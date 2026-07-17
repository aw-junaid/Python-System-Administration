#!/usr/bin/env python3
"""
spinner_animation.py
--------------------
An animated spinner for tasks with an unknown duration (as opposed to
progress_indicator.py, which needs a known total). Runs on a background
thread so it can animate while your main code does its work, and can
also be used as a context manager.

Usage as a library:
    from spinner_animation import Spinner
    import time

    with Spinner("Waiting for server"):
        time.sleep(3)

    # or manually:
    s = Spinner("Working")
    s.start()
    do_slow_thing()
    s.stop()

Run directly for a demo:
    python spinner_animation.py
"""

import itertools
import sys
import threading
import time


class Spinner:
    FRAMES = ["|", "/", "-", "\\"]

    def __init__(self, message="Working", interval=0.1, stream=sys.stdout):
        self.message = message
        self.interval = interval
        self.stream = stream
        self._stop_event = threading.Event()
        self._thread = None

    def _spin(self):
        for frame in itertools.cycle(self.FRAMES):
            if self._stop_event.is_set():
                break
            self.stream.write(f"\r{self.message}... {frame}")
            self.stream.flush()
            time.sleep(self.interval)

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def stop(self, final_message="done"):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        clear_len = len(self.message) + len(final_message) + 8
        self.stream.write("\r" + " " * clear_len + "\r")
        self.stream.write(f"{self.message}... {final_message}\n")
        self.stream.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop("failed" if exc_type else "done")
        return False  # don't suppress exceptions


if __name__ == "__main__":
    print("Demo: spinner running for 2 seconds via context manager\n")
    with Spinner("Waiting for indeterminate task"):
        time.sleep(2)
    print("Demo finished.")
