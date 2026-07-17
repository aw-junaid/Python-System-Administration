# System Commands & Process Management — Python Scripts

Companion scripts for the **System Commands & Process Management** module of
[Python-System-Administration](https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/System%20Commands%20%26%20Process%20Management).

Every script can be run directly and includes a safe built-in demo mode, so you can
try it immediately without needing to supply a real PID or command.

---

## ⚠️ Read This Before Running Anything

- These scripts interact with **real processes and real system commands** on the machine you
  run them on. Some (`kill_process.py`, `restart_process.py`, `suspend_resume_process.py`,
  `send_signal_to_process.py`, `manage_system_service.py`) can **stop, pause, or restart
  processes/services** — including ones you didn't intend to touch if you pass the wrong PID or
  name.
- **Always verify a PID first** with `monitor_processes.py` or `get_process_info.py` before using
  a script that terminates, suspends, restarts, or signals a process.
- Some scripts (managing services, killing processes owned by other users, daemonizing) may
  require **elevated/root privileges** (`sudo` on Linux/macOS, Administrator on Windows).
- `daemonize_process.py` is **POSIX-only** (Linux/macOS) — it uses `os.fork()`, which does not
  exist on Windows.
- Run everything in a **test/VM environment first** if you are not confident about the effect of
  a command, especially anything under "Process Control" below.
- No script here modifies files, installs software, or changes configuration outside of the
  process/command it's explicitly named for.

---

## Requirements

- Python 3.8+
- Some scripts depend on the third-party [`psutil`](https://pypi.org/project/psutil/) library.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aw-junaid/Python-System-Administration.git
cd "Python-System-Administration/modules/System Commands & Process Management/scripts"

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## How to Run Any Script

All scripts follow the same pattern:

```bash
python3 <script_name>.py [arguments]
```

If you run a script **with no arguments**, it will execute a safe, built-in demo so you can see
expected output immediately. Scripts that need input (like a PID) will tell you so and show you
how to supply it.

---

## Script Reference

| # | Script | Topic | Run Example |
|---|--------|-------|-------------|
| 1 | `execute_external_command.py` | Execute External System Commands | `python3 execute_external_command.py "echo hi"` |
| 2 | `execute_shell_secure.py` | Execute Shell Commands Securely | `python3 execute_shell_secure.py ls -la` |
| 3 | `run_without_prompts.py` | Run Scripts Without User Prompts | `python3 run_without_prompts.py "echo hi"` |
| 4 | `run_with_prompts.py` | Run Scripts With User Prompts | `python3 run_with_prompts.py` |
| 5 | `launch_background_process.py` | Launch Background Processes | `python3 launch_background_process.py "sleep 30"` |
| 6 | `monitor_processes.py` | Monitor Running Processes | `python3 monitor_processes.py --filter python` |
| 7 | `kill_process.py` | Kill a Process | `python3 kill_process.py <PID>` |
| 8 | `restart_process.py` | Restart a Process | `python3 restart_process.py --pid <PID> --command "python app.py"` |
| 9 | `suspend_resume_process.py` | Suspend and Resume Processes | `python3 suspend_resume_process.py --suspend <PID>` |
| 10 | `get_process_info.py` | Retrieve Process Information | `python3 get_process_info.py <PID>` |
| 11 | `get_exit_status.py` | Get Exit Status of Commands | `python3 get_exit_status.py "ls /tmp"` |
| 12 | `execute_async_command.py` | Execute Commands Asynchronously | `python3 execute_async_command.py "sleep 2" "echo hi"` |
| 13 | `run_parallel_commands.py` | Run Multiple Commands in Parallel | `python3 run_parallel_commands.py "echo A" "echo B"` |
| 14 | `schedule_delayed_execution.py` | Schedule Delayed Execution | `python3 schedule_delayed_execution.py --delay 10 --command "echo hi"` |
| 15 | `run_scheduled_jobs.py` | Run Scheduled Jobs | `python3 run_scheduled_jobs.py --interval 5 --repeats 3 --command "echo tick"` |
| 16 | `execute_startup_script.py` | Execute Startup Scripts | `python3 execute_startup_script.py` |
| 17 | `manage_system_service.py` | Manage System Services | `python3 manage_system_service.py status ssh` |
| 18 | `detect_os.py` | Detect Operating System | `python3 detect_os.py` |
| 19 | `detect_current_user.py` | Detect Current User | `python3 detect_current_user.py` |
| 20 | `get_hostname.py` | Get Hostname | `python3 get_hostname.py` |
| 21 | `get_system_uptime.py` | Get System Uptime | `python3 get_system_uptime.py` |
| 22 | `run_command_with_timeout.py` | Run Commands with Timeout | `python3 run_command_with_timeout.py --timeout 3 --command "sleep 10"` |
| 23 | `set_cpu_affinity.py` | Set Process CPU Affinity | `python3 set_cpu_affinity.py --pid <PID> --cpus 0,1` |
| 24 | `daemonize_process.py` | Daemonize a Process | `python3 daemonize_process.py` |
| 25 | `get_parent_pid.py` | Get Parent Process ID | `python3 get_parent_pid.py <PID>` |
| 26 | `wait_for_process.py` | Wait for Process Completion | `python3 wait_for_process.py --pid <PID>` |
| 27 | `send_signal_to_process.py` | Send Signals to Processes | `python3 send_signal_to_process.py --pid <PID> --signal SIGTERM` |

---

## Detailed Usage & Expected Output

### 1. `execute_external_command.py`
Runs a command string via the shell and prints stdout/stderr/exit code.
```bash
python3 execute_external_command.py "echo Hello World"
```
**Expected output:** `STDOUT: Hello World`, `STDERR: (no errors)`, `Exit Code: 0`.
**Caution:** Uses `shell=True`. Never pass untrusted/user-supplied strings directly.

### 2. `execute_shell_secure.py`
Same as above but passes arguments as a list (`shell=False`) to avoid shell injection.
```bash
python3 execute_shell_secure.py ls -la
```
**Expected output:** directory listing, exit code 0.
**Caution:** shell features like pipes/wildcards won't work here by design.

### 3. `run_without_prompts.py`
Runs a command non-interactively by feeding blank stdin so it can't hang waiting for input.
```bash
python3 run_without_prompts.py "echo hi"
```
**Caution:** blank input can auto-accept a command's default answer (e.g. "yes" on empty input)
— only use on trusted commands.

### 4. `run_with_prompts.py`
Opposite of #3 — lets a command (or the built-in demo) prompt you and read real keyboard input.
```bash
python3 run_with_prompts.py
```
**Expected output:** you'll be asked to type your name and confirm.

### 5. `launch_background_process.py`
Starts a command in the background (non-blocking) and prints its PID.
```bash
python3 launch_background_process.py "sleep 30"
```
**Caution:** the process keeps running after the script exits — track the PID to manage it later.

### 6. `monitor_processes.py`
Lists running processes with PID, name, CPU%, and memory%.
```bash
python3 monitor_processes.py --filter python
```
**Requires:** `psutil`.

### 7. `kill_process.py`
Terminates a process by PID. Without a PID, lists sample processes so you can pick one.
```bash
python3 kill_process.py <PID>
```
**⚠️ Destructive.** Double-check the PID with `monitor_processes.py` first.

### 8. `restart_process.py`
Stops a process (by `--pid` or `--name`) and relaunches a `--command` in its place.
```bash
python3 restart_process.py --pid 1234 --command "python my_server.py"
```
**Caution:** force-stops the old process; no state is preserved. `--name` matching stops ALL
processes whose name contains that string.

### 9. `suspend_resume_process.py`
Pauses (`SIGSTOP`) and resumes (`SIGCONT`) a process by PID.
```bash
python3 suspend_resume_process.py --suspend 1234
python3 suspend_resume_process.py --resume 1234
```
**Caution:** POSIX concept; behavior may vary on Windows. Don't suspend critical system processes.

### 10. `get_process_info.py`
Shows detailed info for a PID: name, status, CPU%, memory, executable path, start time, cmdline.
```bash
python3 get_process_info.py 1234
```

### 11. `get_exit_status.py`
Runs a command and reports its exit code with a plain-English success/failure verdict.
```bash
python3 get_exit_status.py "ls /nonexistent"
```

### 12. `execute_async_command.py`
Runs multiple commands concurrently using `asyncio` and waits for all to finish.
```bash
python3 execute_async_command.py "sleep 2 && echo done1" "sleep 1 && echo done2"
```
**Note:** faster commands can finish before slower ones — that's expected concurrency.

### 13. `run_parallel_commands.py`
Runs multiple commands in parallel using a thread pool and collects all results.
```bash
python3 run_parallel_commands.py "sleep 2 && echo A" "sleep 1 && echo B" "echo C"
```
**Caution:** avoid commands that write to the same file/resource simultaneously.

### 14. `schedule_delayed_execution.py`
Waits N seconds, then runs a command (blocking, one-shot — like a simple `at`).
```bash
python3 schedule_delayed_execution.py --delay 10 --command "echo Done waiting"
```

### 15. `run_scheduled_jobs.py`
Runs a command repeatedly on a fixed interval, for a limited number of repeats (blocking).
```bash
python3 run_scheduled_jobs.py --interval 5 --repeats 3 --command "echo tick"
```
**Caution:** blocks for the full duration; for real production scheduling use `cron` /
Task Scheduler instead.

### 16. `execute_startup_script.py`
Runs a sequence of startup commands in order, stopping at the first failure. Edit the
`STARTUP_COMMANDS` list inside the script to customize.
```bash
python3 execute_startup_script.py
```

### 17. `manage_system_service.py`
Starts/stops/restarts/checks status of a system service using `systemctl` (Linux),
`launchctl` (macOS), or `sc` (Windows).
```bash
python3 manage_system_service.py status ssh
sudo python3 manage_system_service.py restart nginx
```
**⚠️ Can affect real system services.** Verify the service name before `start`/`stop`/`restart`.
Typically requires `sudo`/Administrator privileges.

### 18. `detect_os.py`
Prints OS name, release, version, architecture, and Python version. Read-only, always safe.
```bash
python3 detect_os.py
```

### 19. `detect_current_user.py`
Prints the username running the script. Read-only, always safe.
```bash
python3 detect_current_user.py
```

### 20. `get_hostname.py`
Prints the machine's hostname. Read-only, always safe.
```bash
python3 get_hostname.py
```

### 21. `get_system_uptime.py`
Prints system boot time and uptime in a human-readable format.
```bash
python3 get_system_uptime.py
```
**Requires:** `psutil`.

### 22. `run_command_with_timeout.py`
Runs a command but stops waiting (and terminates it) if it exceeds a timeout.
```bash
python3 run_command_with_timeout.py --timeout 3 --command "sleep 10"
```
**Caution:** a timed-out process is terminated for you; any partial work is lost.

### 23. `set_cpu_affinity.py`
Views and optionally sets which CPU cores a process may run on.
```bash
python3 set_cpu_affinity.py --pid 1234 --cpus 0,1
```
**Caution:** not supported on macOS via `psutil`. May require elevated privileges for other
users' processes.

### 24. `daemonize_process.py`
Demonstrates the classic double-fork technique to detach a process from its terminal (a "daemon").
```bash
python3 daemonize_process.py
```
**⚠️ POSIX-only (Linux/macOS).** Writes ticks to `/tmp/daemonize_process_demo.log`. You cannot
`Ctrl+C` it — use `kill_process.py` with the PID logged inside the file to stop it early.

### 25. `get_parent_pid.py`
Prints the Parent Process ID (PPID) of a given PID, and its parent's name.
```bash
python3 get_parent_pid.py 1234
```

### 26. `wait_for_process.py`
Blocks until a given PID finishes, then reports elapsed time and exit status.
```bash
python3 wait_for_process.py --pid 1234 --timeout 30
```
**Caution:** without `--timeout`, waits indefinitely. For processes not started by this script,
the exit code may be unavailable (OS limitation for non-child processes).

### 27. `send_signal_to_process.py`
Sends a POSIX signal (`SIGTERM`, `SIGKILL`, `SIGINT`, `SIGHUP`) to a process by PID.
```bash
python3 send_signal_to_process.py --pid 1234 --signal SIGTERM
```
**⚠️ `SIGKILL` cannot be caught or ignored** — the process dies immediately with no cleanup.
Try `SIGTERM` first.

---

## General Notes

- Every script can be run standalone — none depend on each other at import time.
- Scripts that accept no arguments always fall back to a **safe demo mode** rather than failing.
- Where a script could realistically be destructive, its docstring at the top contains an
  explicit **Caution** section — read it before running against a real PID/service.
- Tested on Linux (Ubuntu). Most scripts also work on macOS; a few (`daemonize_process.py`,
  parts of `set_cpu_affinity.py` and `manage_system_service.py`) have OS-specific limitations
  noted in their docstrings.
