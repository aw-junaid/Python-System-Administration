# Automation Utilities Scripts

Python automation building blocks: retries, timeouts, progress/spinner
indicators, rate limiting, concurrency (threads/processes/async), job
queues, caching, config validation, and cleanup context managers. Each
script is standalone, importable as a library, and directly runnable as
a demo with `python3 <script>.py`.

---

## ⚠️ Caution before you run anything

- Most scripts here are pure standard library and safe to run as-is —
  read the top of each file for what it actually does before wiring it
  into anything important.
- **`job_queue.py`** and the Redis path in **`cache_results.py`** will
  try to talk to a Redis server. If `redis` isn't installed or no
  server is reachable at `redis://localhost:6379/0`, they print a clear
  warning and fall back to an in-process/in-memory version so the demo
  still runs — but that fallback is single-process only and **not**
  a substitute for real Redis (no persistence, not shared across
  processes/workers). Don't assume the fallback behaves like production
  Redis.
- **`multiprocessing_utils.py`** spins up real OS child processes. On a
  single-core machine you will see little or no speedup versus
  sequential execution — that's expected, not a bug; the benefit shows
  up on multi-core machines.
- **`timeout_execution.py`** cannot force-kill an arbitrary running
  thread (Python has no safe API for that). If the wrapped function
  exceeds its timeout, `TimeoutError_` is raised in your calling code,
  but the original background thread keeps running until it finishes
  naturally. For work that truly needs to be killable, run it in a
  separate process instead.
- **`spinner_animation.py`** and **`progress_indicator.py`** write
  carriage-return (`\r`) animated output — this looks correct in a
  normal terminal but may look odd if you redirect stdout to a file or
  run in a non-interactive CI log.
- If you're pulling this code from the repo
  (`https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/Automation%20Utilities/scripts`),
  read each script before running it, the same as you should with any
  code you didn't write yourself.

---

## Setup

```bash
git clone https://github.com/aw-junaid/Python-System-Administration.git
cd "Python-System-Administration/modules/Automation Utilities/scripts"

# Optional — only needed for job_queue.py and the Redis path in cache_results.py
pip install redis
docker run -p 6379:6379 redis   # or install Redis locally
```

All scripts run standalone with no arguments: `python3 <script>.py`

---

## Scripts

### 1. `retry_failed_operations.py`
Basic `@retry` decorator: catches specified exceptions and retries N
times with a fixed delay.

```bash
python3 retry_failed_operations.py
```
**Expected output:** two `[retry] Attempt X/4 ... failed` lines (the
demo function fails twice), then `Final result: success` and
`Total calls made: 3`.

---

### 2. `timeout_execution.py`
`@timeout(seconds)` decorator that races a function against a timer and
raises `TimeoutError_` in the caller if it runs too long.

```bash
python3 timeout_execution.py
```
**Expected output:** Demo 1 prints `fast task finished` (completes in
time). Demo 2 prints a caught `TimeoutError_` message for a task that
takes 3s against a 1s timeout.

---

### 3. `progress_indicator.py`
Dependency-free iterable wrapper printing a live `%` progress bar.

```bash
python3 progress_indicator.py
```
**Expected output:** a single line that updates in place from
`Working [#-----...] 5.0% (1/20)` up to `100.0% (20/20)`, then `Done.`

---

### 4. `spinner_animation.py`
Animated spinner (`| / - \`) for indeterminate-length waits, usable as
a context manager.

```bash
python3 spinner_animation.py
```
**Expected output:** a spinning character animation in place for ~2
seconds, ending with `Waiting for indeterminate task... done`.

---

### 5. `retry_decorator.py`
Configurable `@retry` supporting both sync and async functions, a
result-acceptance predicate, and an `on_failure` callback per attempt.

```bash
python3 retry_decorator.py
```
**Expected output:** Demo 1 (sync, polling until a "ready" result)
prints two `did not succeed` log lines then `Result: ready`. Demo 2
(async, exception-based) prints one failed attempt then
`Result: async success`.

---

### 6. `rate_limiting.py`
Token-bucket rate limiter / `@rate_limited` decorator to throttle calls
to N per time window while allowing short bursts.

```bash
python3 rate_limiting.py
```
**Expected output:** the first 3 calls fire immediately (t≈0.00s), then
calls 4–8 are spaced out roughly every 0.33s as the bucket refills.

---

### 7. `parallel_execution.py`
`parallel_map()` helper using `ThreadPoolExecutor` — best for I/O-bound
work (network/file I/O).

```bash
python3 parallel_execution.py
```
**Expected output:** squares of 1–8 computed in parallel; elapsed time
around 0.3s total instead of ~2.4s sequential, since each simulated
call sleeps 0.3s.

---

### 8. `threading_utils.py`
Thread-safe `SafeCounter` (Lock-protected) plus a producer/consumer
worker-pool pattern using `queue.Queue`.

```bash
python3 threading_utils.py
```
**Expected output:** Demo 1 shows `Expected: 10000, Actual: 10000
(correct -- no race condition)`. Demo 2 shows 10 items processed by 3
worker threads, interleaved.

---

### 9. `multiprocessing_utils.py`
`parallel_map_processes()` using `multiprocessing.Pool` to bypass the
GIL for CPU-bound work.

```bash
python3 multiprocessing_utils.py
```
**Expected output:** sequential vs. multiprocessing timing for 8
CPU-heavy tasks, plus a speedup ratio. On a single-core machine the
speedup will be ~1x or worse (process overhead) — that's expected, not
a bug; multi-core machines will show a real speedup.

---

### 10. `async_utils.py`
`gather_limited()` — run coroutines concurrently but capped at N at
once — plus a `with_timeout()` wrapper around `asyncio.wait_for`.

```bash
python3 async_utils.py
```
**Expected output:** Demo 1 shows 10 simulated network calls completing
in ~2.0s with concurrency capped at 3 (rather than ~0.5s uncapped or
~5.0s sequential). Demo 2 shows a caught `asyncio.TimeoutError`.

---

### 11. `job_queue.py`
Redis-backed FIFO job queue helpers (enqueue/dequeue), with an
in-memory fallback if `redis` isn't installed or no server is reachable.

```bash
python3 job_queue.py
```
**Expected output:** if Redis/`redis` isn't available, a warning is
printed and an in-memory queue is used instead; either way, you'll see
5 jobs enqueued and then processed one by one, ending with
`Queue length now: 0`.

---

### 12. `cache_results.py`
Memoization via `functools.lru_cache` (in-process) and an optional
Redis-backed cache decorator with TTL (falls back to an in-process TTL
cache if Redis isn't available).

```bash
python3 cache_results.py
```
**Expected output:** for each demo, the first call shows the function
body actually ran (`ran 1x`), and the second call with the same
arguments returns instantly from cache (`ran 1x -- cached`, i.e. the
counter did not increase).

---

### 13. `config_validation.py`
`@validated_config` class decorator enforcing type + custom validator
checks on plain dataclasses — no external dependency required.

```bash
python3 config_validation.py
```
**Expected output:** Demo 1 constructs a valid config successfully.
Demo 2 raises and catches a `TypeError` for a wrong-typed field. Demo 3
raises and catches a `ValueError` for a field that fails its validator.

---

### 14. `auto_cleanup.py`
Context managers guaranteeing cleanup via `__exit__`, even when the
`with` block raises — a generic `ManagedResource` wrapper plus a
ready-made `temp_directory` example.

```bash
python3 auto_cleanup.py
```
**Expected output:** Demo 1 shows the fake resource being released even
though the block raised an exception. Demo 2 creates a temp directory,
writes a file into it, and confirms it's removed
(`Directory still exists after the block? False`).

---

### 15. `retry_backoff.py`
`@retry_with_backoff` — retries with exponentially increasing delay
(and optional jitter) to avoid a thundering-herd retry storm.

```bash
python3 retry_backoff.py
```
**Expected output:** failed-attempt log lines showing delays roughly
doubling (0.20s, 0.40s, 0.80s...), then `Final result: connected` after
4 total calls.

---

## Design notes that apply across scripts

- **Retry family** (`retry_failed_operations.py`, `retry_decorator.py`,
  `retry_backoff.py`) are three different levels of the same idea:
  fixed-delay, fully configurable (sync+async), and exponential
  backoff, respectively. Pick the simplest one that covers your case.
- **Concurrency family** (`parallel_execution.py`, `threading_utils.py`,
  `multiprocessing_utils.py`, `async_utils.py`) — use threads/async for
  I/O-bound work, and multiprocessing for CPU-bound work, since threads
  can't run Python bytecode in parallel due to the GIL.
- Every script can be imported (`from <name> import <thing>`) instead of
  run directly — the `if __name__ == "__main__":` block only contains
  the demo.
