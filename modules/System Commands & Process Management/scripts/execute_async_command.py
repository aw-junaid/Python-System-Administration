#!/usr/bin/env python3
"""
execute_async_command.py

Purpose:
    Execute a command asynchronously using Python's asyncio, so the
    script can perform other work while the command runs in parallel.

Usage:
    python execute_async_command.py "sleep 2 && echo done1" "sleep 1 && echo done2"

    If no commands are given, two safe built-in demo commands run
    concurrently.

Expected Output:
    Started: sleep 2 && echo done1
    Started: sleep 1 && echo done2
    Finished: sleep 1 && echo done2 -> exit 0
    Finished: sleep 2 && echo done1 -> exit 0
    (Note faster commands can finish before slower ones, proving true
    concurrency.)

Caution:
    - All given commands run at the same time; make sure they don't
      compete destructively for the same resource/file if run together.
    - This script waits for ALL commands to finish before exiting
      (asyncio.gather); it does not "fire and forget".
"""

import asyncio
import sys


async def run_command_async(command: str) -> None:
    print(f"Started: {command}")
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    print(f"Finished: {command} -> exit {process.returncode}")
    if stdout:
        print(f"  stdout: {stdout.decode().strip()}")
    if stderr:
        print(f"  stderr: {stderr.decode().strip()}")


async def main_async(commands):
    await asyncio.gather(*(run_command_async(cmd) for cmd in commands))


def main():
    if len(sys.argv) > 1:
        commands = sys.argv[1:]
    else:
        commands = [
            "sleep 2 && echo done1",
            "sleep 1 && echo done2"
        ]
    asyncio.run(main_async(commands))


if __name__ == "__main__":
    main()
