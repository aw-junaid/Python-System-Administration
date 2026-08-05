#!/usr/bin/env python3
"""
restart_process.py

Purpose:
    "Restart" a process by terminating an existing one (matched by PID
    or by name) and relaunching a given command in its place.

Usage:
    python restart_process.py --pid 1234 --command "python my_server.py"
    python restart_process.py --name "my_server.py" --command "python my_server.py"

    If no arguments are given, a safe built-in demo runs: it launches a
    dummy process, then restarts it.

Expected Output:
    Stopping old process (if found)...
    Old process stopped.
    Starting new process...
    New process started with PID: <number>

Caution:
    - This does NOT gracefully drain connections or save state for you;
      it force-stops the old process before starting the new one. Any
      unsaved work in the old process will be lost.
    - If matching by --name, ALL processes whose name contains that
      string will be stopped, so use a specific/unique identifier to
      avoid killing the wrong thing.
"""

import subprocess
import sys
import time

try:
    import psutil
except ImportError:
    print("Error: this script requires 'psutil'. Install with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def stop_by_pid(pid: int) -> None:
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=5)
        print(f"Old process (PID {pid}) stopped.")
    except psutil.NoSuchProcess:
        print(f"No process with PID {pid} found; nothing to stop.")
    except psutil.AccessDenied:
        print(f"Access denied stopping PID {pid}.")


def stop_by_name(name: str) -> None:
    stopped_any = False
    for proc in psutil.process_iter(['pid', 'name']):
        if name.lower() in (proc.info['name'] or "").lower():
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"Stopped process {proc.info['pid']} ({proc.info['name']}).")
                stopped_any = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    if not stopped_any:
        print(f"No running process matched name '{name}'.")


def start_new(command: str) -> int:
    process = subprocess.Popen(command, shell=True)
    print(f"New process started with PID: {process.pid}")
    return process.pid


def parse_args():
    args = sys.argv[1:]
    pid = None
    name = None
    command = None
    i = 0
    while i < len(args):
        if args[i] == "--pid" and i + 1 < len(args):
            pid = int(args[i + 1]); i += 2
        elif args[i] == "--name" and i + 1 < len(args):
            name = args[i + 1]; i += 2
        elif args[i] == "--command" and i + 1 < len(args):
            command = args[i + 1]; i += 2
        else:
            i += 1
    return pid, name, command


def main():
    pid, name, command = parse_args()

    if not command:
        # Demo mode: launch a dummy sleep process, then restart it
        print("No --command given, running demo mode.")
        demo_command = "sleep 20"
        proc = subprocess.Popen(demo_command, shell=True)
        print(f"Launched demo process PID: {proc.pid}")
        time.sleep(1)
        print("Stopping old process...")
        stop_by_pid(proc.pid)
        print("Starting new process...")
        start_new(demo_command)
        return

    print("Stopping old process (if found)...")
    if pid:
        stop_by_pid(pid)
    elif name:
        stop_by_name(name)
    else:
        print("No --pid or --name given; skipping stop step.")

    print("Starting new process...")
    start_new(command)


if __name__ == "__main__":
    main()
