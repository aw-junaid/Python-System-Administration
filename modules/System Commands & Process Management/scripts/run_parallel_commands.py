#!/usr/bin/env python3
"""
run_parallel_commands.py

Purpose:
    Run multiple independent commands at the same time using a thread
    pool, and collect all of their results once they finish.

Usage:
    python run_parallel_commands.py "sleep 2 && echo A" "sleep 1 && echo B" "echo C"

    If no commands are given, three safe built-in demo commands run
    in parallel.

Expected Output:
    Results (order may vary based on which finishes first):
    [echo C] exit=0 output=C
    [sleep 1 && echo B] exit=0 output=B
    [sleep 2 && echo A] exit=0 output=A

Caution:
    - Commands run truly in parallel (separate OS processes), so if
      they write to the same file or resource, you may get race
      conditions or corrupted output. Keep each command's side effects
      isolated.
    - This script waits for every command to finish before printing
      results; it is not meant for long-lived background services (see
      launch_background_process.py for that use case).
"""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_one(command: str):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return command, result.returncode, result.stdout.strip(), result.stderr.strip()


def run_parallel(commands):
    print(f"Running {len(commands)} commands in parallel...\n")
    results = []
    with ThreadPoolExecutor(max_workers=len(commands)) as executor:
        futures = {executor.submit(run_one, cmd): cmd for cmd in commands}
        for future in as_completed(futures):
            results.append(future.result())

    print("Results (order may vary based on which finishes first):")
    for command, exit_code, output, error in results:
        print(f"[{command}] exit={exit_code} output={output}", end="")
        if error:
            print(f" error={error}")
        else:
            print()


def main():
    if len(sys.argv) > 1:
        commands = sys.argv[1:]
    else:
        commands = [
            "sleep 2 && echo A",
            "sleep 1 && echo B",
            "echo C"
        ]
    run_parallel(commands)


if __name__ == "__main__":
    main()
