# Task Scheduling — Python Automation Scripts

This folder contains **7 standalone Python scripts**, each automating a single, specific task-scheduling need (in-process scheduling, cron, Windows Task Scheduler, periodic execution, one-off timed execution, retry-on-failure, and a background job queue).

Every script:
- Is completely **independent** — you only need the one file for the task you want.
- Can be run directly from the command line.
- Uses `argparse`, so running it with `-h` shows help and usage.
- Prints clear success/error messages so you always know what happened.

> **Repository:** https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/Task%20Scheduling/scripts

---

## ⚠️ Important Cautions Before You Start

1. **`schedule_with_library.py`, `execute_periodically.py`, and `execute_at_specific_time.py` only run while the script itself is running.** Close the terminal or lose the process and the schedule stops. For jobs that must survive reboots/logouts, use `schedule_with_cron.py` (Linux/macOS) or `windows_task_scheduler.py` (Windows) instead — those register with the OS.
2. **`schedule_with_cron.py` modifies your real crontab** (the current user's). Run `crontab -l` before and after to see what changed, and always give jobs a `--comment` label so you can find and remove them later with the `remove` action.
3. **`windows_task_scheduler.py` modifies real Windows Task Scheduler entries** and may require running your terminal **as Administrator** for some schedule types or system-level tasks.
4. **Commands you schedule run with the same permissions as the user/script that scheduled them.** Don't schedule commands from untrusted sources.
5. **`queue_background_jobs.py`'s worker actually executes every command in the queue** — only add commands you trust, and check `job_queue.json`/`job_queue.log` if something unexpected runs.
6. **Always test your command manually first** (run it directly in the terminal) before scheduling it, so you know it works and know what "success" (exit code 0) looks like.
7. Long-running loops (`execute_periodically.py` without `--count`, `schedule_with_library.py`, `queue_background_jobs.py worker` without `--once`) run until you press `Ctrl+C` — know how to stop them.

---

## 📦 Requirements

- **Python 3.9+** installed on your system.
- Check your version:
  ```bash
  python3 --version
  ```
- Some scripts use **only the Python standard library** — nothing to install.
- Others need small external packages, listed in `requirements.txt`.
- `schedule_with_cron.py` requires a working `cron`/`crontab` installation and is **Linux/macOS only**.
- `windows_task_scheduler.py` wraps the built-in `schtasks` command and is **Windows only**.

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aw-junaid/Python-System-Administration.git
   cd "Python-System-Administration/modules/Task Scheduling/scripts"
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
   > `windows_task_scheduler.py`, `execute_periodically.py`, `execute_at_specific_time.py`, `retry_failed_task.py`, and `queue_background_jobs.py` work with zero installs. `schedule_with_library.py` needs `schedule`; `schedule_with_cron.py` needs `python-crontab` and `croniter`.

4. **Run any script:**
   ```bash
   python3 script_name.py --help
   ```
   This shows the exact arguments each script expects.

---

## 🗂 Full List of Scripts, Usage & Expected Output

Below, `python3` is used for Linux/macOS. On Windows, use `python` instead.

### 1. `schedule_with_library.py` — Schedule Jobs Using `schedule`
**Requires:** `pip install -r requirements.txt`
```bash
python3 schedule_with_library.py "echo Hello" --every 10 --unit seconds
python3 schedule_with_library.py "python3 backup.py" --every 1 --unit hours
```
**Expected output:** Confirms the schedule, then runs the command every `N` `--unit` (seconds/minutes/hours/days), printing a timestamp and output each time it fires. Runs until `Ctrl+C` — the script itself must stay running.

---

### 2. `schedule_with_cron.py` — Schedule Jobs Using cron
**Requires:** `pip install -r requirements.txt` · **Platform:** Linux/macOS only
```bash
python3 schedule_with_cron.py add "0 2 * * *" "python3 /home/user/backup.py" --comment "daily-backup"
python3 schedule_with_cron.py list
python3 schedule_with_cron.py remove --comment "daily-backup"
```
**Expected output:**
- `add`: confirms the job was added to your crontab and shows its next run time.
- `list`: shows every cron job for your user, with enabled/disabled status.
- `remove`: confirms how many jobs with that comment/label were deleted.

Verify directly with the standard `crontab -l` command at any time.

---

### 3. `windows_task_scheduler.py` — Windows Task Scheduler Automation
**Platform:** Windows only
```bash
python windows_task_scheduler.py add "DailyBackup" "C:\Python312\python.exe C:\scripts\backup.py" --schedule DAILY --time 02:00
python windows_task_scheduler.py list
python windows_task_scheduler.py remove "DailyBackup"
```
**Expected output:**
- `add`: `Task 'DailyBackup' created successfully.` (uses `schtasks /Create` under the hood).
- `list`: full output of `schtasks /Query`, showing all scheduled tasks on the system.
- `remove`: `Task 'DailyBackup' removed successfully.`

**Caution:** Some schedule types or system-wide tasks require running your terminal **as Administrator**.

---

### 4. `execute_periodically.py` — Execute Tasks Periodically
```bash
python3 execute_periodically.py "echo Hello" --interval 5
python3 execute_periodically.py "python3 healthcheck.py" --interval 60 --count 10
```
**Expected output:** Runs the command every `--interval` seconds, printing a timestamp and output each time. With `--count`, stops automatically after that many runs; without it, runs forever until `Ctrl+C`.

---

### 5. `execute_at_specific_time.py` — Execute Tasks at Specific Times
```bash
python3 execute_at_specific_time.py "python3 backup.py" --time 23:30
python3 execute_at_specific_time.py "python3 report.py" --datetime "2026-08-01 09:00:00"
```
**Expected output:** Prints the target time and how long it will wait, then blocks until that moment and runs the command once. `--time HH:MM` schedules for today (or tomorrow if that time already passed); `--datetime` targets an exact date and time. `Ctrl+C` cancels before it fires.

---

### 6. `retry_failed_task.py` — Retry Failed Tasks
```bash
python3 retry_failed_task.py "curl -f https://example.com/api/ping"
python3 retry_failed_task.py "python3 upload.py" --max-retries 8 --base-delay 3
```
**Expected output:** Runs the command; if it exits non-zero, retries with **exponential backoff** (delay doubles each attempt, capped at `--max-delay`, default 60s) up to `--max-retries` times (default 5). Prints `Success on attempt N` and exits 0 as soon as it succeeds, or gives up and exits 1 after the final attempt.

---

### 7. `queue_background_jobs.py` — Queue Background Jobs
```bash
python3 queue_background_jobs.py add "python3 convert.py file1.csv"
python3 queue_background_jobs.py add "python3 convert.py file2.csv"
python3 queue_background_jobs.py list
python3 queue_background_jobs.py worker
```
**Expected output:**
- `add`: `Job #N added to queue: <command>`, stored in `job_queue.json`.
- `list`: every job with its status (`pending`, `completed`, `failed`).
- `worker`: processes pending jobs **in order, one at a time**, logging each start/output/result to `job_queue.log`. Use `worker --once` to drain the current queue and exit; without `--once`, it keeps polling for new jobs every `--interval` seconds (default 5) until `Ctrl+C`.

---

## 🧪 Quick Test Workflow

To safely try these scripts without touching real schedules or system state:

```bash
mkdir test_area && cd test_area
python3 ../execute_periodically.py "echo tick" --interval 2 --count 3
python3 ../retry_failed_task.py "python3 -c \"import sys; sys.exit(0)\"" --max-retries 2
python3 ../queue_background_jobs.py add "echo queued job"
python3 ../queue_background_jobs.py worker --once
```

---

## 📄 License / Usage Notes

- These scripts are provided for educational and administrative automation purposes.
- Always review a script's code before scheduling it to run automatically or unattended.
- The author is not responsible for issues caused by scheduled commands, including unintended crontab/Task Scheduler changes, runaway loops, or commands run with incorrect permissions.
