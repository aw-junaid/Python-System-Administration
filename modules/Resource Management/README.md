# Resource Management — Python Automation Scripts

This folder contains **8 standalone Python scripts**, each automating a single, specific resource-management task (CPU/memory/disk limits, execution timeouts, process priority, system monitoring, exhaustion detection, and auto-restart of failed processes).

Every script:
- Is completely **independent** — you only need the one file for the task you want.
- Can be run directly from the command line.
- Uses `argparse`, so running it with `-h` shows help and usage.
- Prints clear success/error messages so you always know what happened.

> **Repository:** https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/Resource%20Management/scripts

---

## ⚠️ Important Cautions Before You Start

1. **These scripts can kill processes, throttle resources, or terminate work in progress.** Test on a throwaway command first (e.g. `sleep 10`, a small test script) before pointing them at anything important.
2. **`set_cpu_limit.py` and `limit_memory_usage.py` only enforce hard OS-level limits on Linux/macOS** (via the `resource` module's `RLIMIT_CPU`/`RLIMIT_AS`). On Windows, the OS does not support these the same way — the scripts detect this and run the command *without* a hard limit rather than silently failing.
3. **`set_process_priority.py` with negative priority values (higher priority) usually requires root/sudo (Linux/macOS) or Administrator (Windows).** Without elevated privileges, you'll get a permission error — this is expected OS behavior, not a bug.
4. **`limit_disk_usage.py` cannot enforce a hard OS-level disk quota** — Python has no cross-platform way to do that without root tools like `setquota`. It monitors and reports/exits non-zero when the limit is crossed; you (or your own script) decide what to do about it (e.g. stop writing, alert, clean up).
5. **`restart_failed_process.py` will keep restarting a crashing process** up to `--max-retries` (default 5) with a delay between attempts (default 3s) to avoid restart storms. Setting `--max-retries 0` means unlimited restarts — use with care, and always know how to stop it (`Ctrl+C`).
6. **Monitoring scripts (`monitor_system_resources.py`, `detect_resource_exhaustion.py`) with `--watch`/continuous mode run until you press `Ctrl+C`.**
7. When passing a command to run (`set_cpu_limit.py`, `limit_memory_usage.py`, `limit_execution_time.py`, `set_process_priority.py`, `restart_failed_process.py`), always put your own script's flags **before** the command, and separate the target command with `--` to avoid ambiguity — see examples below.

---

## 📦 Requirements

- **Python 3.9+** installed on your system.
- Check your version:
  ```bash
  python3 --version
  ```
- Some scripts use **only the Python standard library** (`resource`, `subprocess`, `os`, `time`) — nothing to install.
- Scripts that inspect processes/system stats cross-platform require the `psutil` package, listed in `requirements.txt`.
- `set_cpu_limit.py` and `limit_memory_usage.py` rely on the `resource` module, which is **Linux/macOS only** (part of the Python standard library there, not available on Windows).

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aw-junaid/Python-System-Administration.git
   cd "Python-System-Administration/modules/Resource Management/scripts"
   ```

2. **(Recommended) Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   > `limit_disk_usage.py`, `limit_execution_time.py`, and `restart_failed_process.py` work with zero installs. `set_cpu_limit.py` and `limit_memory_usage.py` need no installs either (Linux/macOS), but won't hard-limit on Windows. Install `psutil` for the other three scripts.

4. **Run any script:**
   ```bash
   python3 script_name.py --help
   ```
   This shows the exact arguments each script expects.

---

## 🗂 Full List of Scripts, Usage & Expected Output

Below, `python3` is used for Linux/macOS. On Windows, use `python` instead.

### 1. `set_cpu_limit.py` — Set CPU Usage Limits
**Platform:** Linux/macOS for hard enforcement (Windows runs without a limit).
```bash
python3 set_cpu_limit.py 5 -- python3 -c "while True: pass"
```
**Expected output:** The command runs, then is killed once it accumulates 5 seconds of **CPU time** (not wall-clock time). Output shows `Command finished with exit code: -9` and explains the process was terminated by a signal.

---

### 2. `limit_memory_usage.py` — Limit Memory Usage
**Platform:** Linux/macOS for hard enforcement (Windows runs without a limit).
```bash
python3 limit_memory_usage.py 200 -- python3 -c "x = bytearray(500*1024*1024)"
```
**Expected output:** The process fails with a `MemoryError` (or is killed) once it tries to exceed 200 MB of virtual memory. Non-zero exit code confirms the limit was hit.

---

### 3. `limit_disk_usage.py` — Limit Disk Usage
```bash
python3 limit_disk_usage.py /home/user/uploads 500
python3 limit_disk_usage.py /home/user/uploads 500 --watch --interval 10
```
**Expected output:** Current directory size vs. the limit, and a status: `OK`, `WARNING` (90%+), or `LIMIT EXCEEDED` (exits with code 1 in single-check mode). `--watch` repeats the check on an interval until `Ctrl+C`.

---

### 4. `limit_execution_time.py` — Limit Execution Time
```bash
python3 limit_execution_time.py 10 -- ping -c 100 example.com
```
**Expected output:** The command runs normally if it finishes in time. If it exceeds the timeout, it's terminated and the script exits with code `124` (the conventional timeout exit code, same as the GNU `timeout` command).

---

### 5. `set_process_priority.py` — Set Process Priority
**Requires:** `pip install -r requirements.txt`
```bash
python3 set_process_priority.py --pid 1234 --priority 10
python3 set_process_priority.py --priority -5 -- python3 my_script.py
```
**Expected output:** Confirmation that the process's niceness/priority was changed. On Linux/macOS, priority ranges from `-20` (highest) to `19` (lowest); negative values typically need root/sudo. On Windows, the closest matching priority class is applied automatically.

---

### 6. `monitor_system_resources.py` — Monitor System Resources
**Requires:** `pip install -r requirements.txt`
```bash
python3 monitor_system_resources.py
python3 monitor_system_resources.py --watch --interval 5
```
**Expected output:** A snapshot of CPU usage (overall + per core), memory, swap, disk usage for `/`, and network bytes sent/received. `--watch` refreshes continuously until `Ctrl+C`.

---

### 7. `detect_resource_exhaustion.py` — Detect Resource Exhaustion
**Requires:** `pip install -r requirements.txt`
```bash
python3 detect_resource_exhaustion.py
python3 detect_resource_exhaustion.py --cpu 80 --memory 85 --disk 95 --interval 10
python3 detect_resource_exhaustion.py --once
```
**Expected output:** Continuously prints `OK` or `ALERT — resource exhaustion detected` with details on which resource(s) crossed their threshold (default 90% for CPU/memory/disk). Use `--once` for a single check suitable for scripting/cron (exits with code 1 if any threshold is exceeded).

---

### 8. `restart_failed_process.py` — Automatically Restart Failed Processes
```bash
python3 restart_failed_process.py python3 my_server.py
python3 restart_failed_process.py python3 my_server.py --max-retries 10 --delay 5
python3 restart_failed_process.py python3 flaky_job.py --timeout 30
```
**Expected output:** The command runs; if it exits with a non-zero code, it's automatically restarted after `--delay` seconds (default 3), up to `--max-retries` times (default 5, `0` = unlimited). Stops immediately once the process exits with code 0. Use `--timeout` to also treat a hang (running too long) as a failure worth restarting.
**Note:** Put this script's own flags (`--max-retries`, `--delay`, `--timeout`) before your target command, e.g. `restart_failed_process.py --max-retries 10 -- python3 my_server.py`.

---

## 🧪 Quick Test Workflow

To safely try these scripts without touching anything important:

```bash
mkdir test_area && cd test_area
python3 ../monitor_system_resources.py
python3 ../limit_execution_time.py 3 -- sleep 10
python3 ../detect_resource_exhaustion.py --once
python3 ../restart_failed_process.py --max-retries 2 --delay 1 -- python3 -c "import sys; sys.exit(1)"
```

---

## 📄 License / Usage Notes

- These scripts are provided for educational and administrative automation purposes.
- Always review a script's code before running it against production processes or servers.
- The author is not responsible for service interruptions caused by aggressive resource limits, killed processes, or restart loops resulting from misuse.
