# System Information Scripts

This document explains, script by script, exactly how to run each tool
and what output it produces. Each script is independent and produces
a different kind of output, so each one is documented separately below.

All commands assume you are inside the scripts folder:

```bash
cd "Python-System-Administration/modules/System Information/scripts"
```

and that dependencies are already installed:

```bash
pip install -r requirements.txt
```

---

## 1. cpu_info.py

### What it does

Reads CPU details using `psutil` and `platform`: processor name,
architecture, physical core count, logical thread count, current/min/max
clock frequency, overall CPU usage, and per-core usage.

### How to run

```bash
python3 cpu_info.py
```

No arguments or flags.

### Sample output

```
==================================================
 CPU INFORMATION
==================================================
Processor                   : x86_64
Architecture                : x86_64
Physical cores               : 1
Logical threads              : 1
Current frequency (MHz)      : 2800.0
Min frequency (MHz)          : N/A
Max frequency (MHz)          : N/A
Overall CPU usage (%)        : 0.0

Per-core usage (%):
  Core 0: 2.0%
==================================================
```

### Notes on output

- `Physical cores` and `Logical threads` will differ on machines with
  hyperthreading enabled (logical threads is higher).
- `Min/Max frequency` shows `N/A` on systems where the kernel does not
  expose frequency scaling limits (common in virtual machines and
  containers, as in the sample above).
- The per-core usage list has one line for every logical thread
  detected, so this section grows on multi-core machines.

---

## 2. memory_info.py

### What it does

Reads total, available, used, and free RAM, plus swap statistics,
using `psutil.virtual_memory()` and `psutil.swap_memory()`.

### How to run

```bash
python3 memory_info.py
```

No arguments or flags.

### Sample output

```
==================================================
 MEMORY INFORMATION
==================================================
Total RAM (GB)               : 3.9
Available RAM (GB)           : 3.64
Used RAM (GB)                : 0.26
Free RAM (GB)                : 3.71
RAM usage (%)                : 6.7

Swap:
  Total swap (GB)            : 0.0
  Used swap (GB)             : 0.0
  Free swap (GB)             : 0.0
  Swap usage (%)             : 0.0
```

### Notes on output

- All values are converted to gigabytes and rounded to two decimal
  places.
- If the machine has no swap configured (common on some cloud or
  container instances, as above), all swap values show as `0.0`.
- `Available RAM` is not the same as `Free RAM` — available accounts
  for memory the kernel could reclaim (caches/buffers) and is the more
  reliable figure for "how much can a new process actually use."

---

## 3. disk_info.py

### What it does

Iterates over every mounted partition with `psutil.disk_partitions()`
and reports device name, mount point, filesystem type, mount options,
and usage (total/used/free/percent) for each one.

### How to run

```bash
python3 disk_info.py
```

No arguments or flags.

### Sample output

```
======================================================================
 DISK INFORMATION
======================================================================

Device        : /dev/vda
Mount point   : /
Filesystem    : ext4
Options       : rw,relatime,resv_strict,resuid=65534,resgid=65534
Total size    : 251.97 GB
Used          : 8.55 GB
Free          : 9.98 GB
Usage         : 46.1%

Device        : /dev/vdb
Mount point   : /opt/rclone
Filesystem    : squashfs
Options       : ro,relatime,errors=continue
Total size    : 0.01 GB
Used          : 0.01 GB
Free          : 0.0 GB
Usage         : 100.0%

======================================================================
```

### Notes on output

- One block is printed per partition. A machine with more drives or
  more mounted filesystems (USB drives, network shares, read-only
  system mounts, etc.) will produce more blocks.
- Read-only mounts (`ro` in Options, e.g. `squashfs` images) usually
  show `Usage : 100.0%` because the used space equals the total size.
- If a mount point cannot be read due to permissions, the script prints
  `Usage : Permission denied` instead of crashing.

---

## 4. network_interfaces.py

### What it does

Lists every network interface on the machine with `psutil.net_if_addrs()`
and `psutil.net_if_stats()`: link status (up/down), speed, MTU, MAC
address, and IPv4/IPv6 addresses with netmask and broadcast address.

### How to run

```bash
python3 network_interfaces.py
```

No arguments or flags.

### Sample output

```
============================================================
 NETWORK INTERFACES
============================================================

Interface: lo
  Status     : UP
  Speed      : N/A
  MTU        : 65536
  IPv4 Address: 127.0.0.1
    Netmask   : 255.0.0.0
  MAC Address: 00:00:00:00:00:00

Interface: eth0
  Status     : UP
  Speed      : N/A
  MTU        : 1400
  IPv4 Address: 192.0.2.2
    Netmask   : 255.255.255.0
    Broadcast : 192.0.2.255
  MAC Address: 02:fc:00:00:00:01

============================================================
```

### Notes on output

- `lo` is the loopback interface and is present on every machine; its
  MAC address is always all zeros.
- `Speed : N/A` appears when the driver does not report a negotiated
  link speed (common for virtual NICs, as above); on physical Ethernet
  or Wi-Fi adapters this typically shows a number in Mbps.
- Interfaces that are down (disconnected, disabled) still appear in
  the list with `Status : DOWN` and usually no IP address.
- IPv6 addresses print the same way as IPv4, just under an
  `IPv6 Address` line, when present.

---

## 5. installed_software.py

### What it does

Queries the OS package manager directly — `dpkg-query` on
Debian/Ubuntu systems or `rpm` on RHEL/Fedora/CentOS systems — and
lists installed package names and versions. This script does not work
on Windows or macOS because neither package manager exists there.

### How to run

```bash
python3 installed_software.py
```

Optional flag to limit output length:

```bash
python3 installed_software.py --limit 50
```

### Sample output (with --limit 5)

```
============================================================
 INSTALLED SOFTWARE
============================================================
[*] Detected dpkg (Debian/Ubuntu based system)

adduser 3.137ubuntu1
adwaita-icon-theme 46.0-1
apt 2.8.3
apt-transport-https 2.8.3
at-spi2-common 2.52.0-1build1

Total packages shown: 5
============================================================
```

### Notes on output

- Without `--limit`, this script prints every installed package —
  on a typical desktop or server this can be several hundred to a few
  thousand lines, so redirect to a file if you want to review it:

  ```bash
  python3 installed_software.py > packages.txt
  ```

- The first line always tells you which package manager was detected
  (`dpkg` or `rpm`) before the list starts.
- On a system with neither `dpkg` nor `rpm` (Windows, macOS, or a
  minimal Linux distribution without either tool), the script exits
  with an explanatory message instead of a package list.

---

## 6. environment_variables.py

### What it does

Reads the current process's environment using Python's `os.environ`
and prints all variables, or a single variable if requested. Also
breaks down `PATH` into its individual entries.

### How to run

Print every environment variable:

```bash
python3 environment_variables.py
```

Print only one variable:

```bash
python3 environment_variables.py --key PATH
```

### Sample output (--key PATH)

```
============================================================
 ENVIRONMENT VARIABLES
============================================================
PATH=/home/claude/.npm-global/bin:/home/claude/.local/bin:/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
============================================================
```

### Sample output (no flag — abbreviated)

```
============================================================
 ENVIRONMENT VARIABLES
============================================================
HOME=/home/claude
LANG=en_US.UTF-8
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
SHELL=/bin/bash
...
Total variables: 24

PATH entries:
  - /usr/local/sbin
  - /usr/local/bin
  - /usr/sbin
  - /usr/bin
  - /sbin
  - /bin
```

### Notes on output

- Without `--key`, output length depends entirely on how many
  variables your shell session has set — it can be a handful or
  several dozen lines.
- This script can only see the environment of the process it runs
  in (and whatever the parent shell passed down). It cannot read
  another user's session environment — that would require elevated
  privileges and OS-specific APIs outside what this script does.
- The `PATH entries` section splits on `:` on Linux/macOS and on `;`
  on Windows automatically.

---

## 7. bios_info.py

### What it does

On Linux, reads BIOS vendor, version, release date, and revision
directly from `/sys/class/dmi/id/`. On Windows, uses the `wmi` package
to query `Win32_BIOS`. Some fields (notably serial numbers) require
root/Administrator privileges to read.

### How to run

Standard run:

```bash
python3 bios_info.py
```

With elevated privileges on Linux (needed for restricted fields):

```bash
sudo python3 bios_info.py
```

### Sample output (without sudo, inside a restricted/virtual environment)

```
==================================================
 BIOS INFORMATION
==================================================
Vendor         : Not available
Version        : Not available
Release date   : Not available
BIOS revision  : Not available
==================================================
```

### Sample output (on a typical physical machine with sudo)

```
==================================================
 BIOS INFORMATION
==================================================
Vendor         : American Megatrends Inc.
Version        : F.20
Release date   : 03/14/2024
BIOS revision  : 5.17
==================================================
```

### Notes on output

- `Not available` means the corresponding file under
  `/sys/class/dmi/id/` does not exist on this machine — this is
  expected inside many virtual machines, containers, and cloud
  instances that don't expose full DMI tables (as in the first sample
  above, captured on a sandboxed VM).
- `Permission denied (try running with sudo)` appears instead when the
  file exists but your user lacks read access — re-run with `sudo` to
  see the value.
- On Windows, output field names are the same but values come from WMI
  instead of DMI files.

---

## 8. motherboard_info.py

### What it does

Same approach as `bios_info.py`, but reads baseboard fields instead:
manufacturer, product name, version, and serial number. Linux reads
`/sys/class/dmi/id/`; Windows uses `wmi` to query `Win32_BaseBoard`.

### How to run

```bash
python3 motherboard_info.py
```

With elevated privileges on Linux:

```bash
sudo python3 motherboard_info.py
```

### Sample output (without sudo, inside a restricted/virtual environment)

```
==================================================
 MOTHERBOARD INFORMATION
==================================================
Manufacturer   : Not available
Product name   : Not available
Version        : Not available
Serial number  : Not available
==================================================
```

### Sample output (on a typical physical machine with sudo)

```
==================================================
 MOTHERBOARD INFORMATION
==================================================
Manufacturer   : ASUSTeK COMPUTER INC.
Product name   : ROG STRIX B650E-F GAMING WIFI
Version        : Rev 1.xx
Serial number  : NA1234567890
==================================================
```

### Notes on output

- Behaves identically to `bios_info.py` in terms of permission
  handling — `Not available` means the field doesn't exist on this
  hardware/virtualization layer, `Permission denied` means it exists
  but needs `sudo` to read.
- Many virtual machines report `Not available` or generic placeholder
  values (e.g. "QEMU Virtual Machine") for every field since there is
  no physical baseboard.

---

## 9. os_version.py

### What it does

Prints the OS name, kernel release, and version/build using
`platform`, then on Linux adds distribution-specific detail (name,
version, codename) using the `distro` package, falling back to
parsing `/etc/os-release` manually if `distro` is not installed.

### How to run

```bash
python3 os_version.py
```

No arguments or flags.

### Sample output

```
==================================================
 OPERATING SYSTEM VERSION
==================================================
System         : Linux
Release        : 6.18.5-fc-v20
Version/Build  : #1 SMP PREEMPT_DYNAMIC @0
Machine        : x86_64

Distribution details:
  Distribution : Ubuntu 24.04.4 LTS
  Version      : 24.04
  Codename     : noble
==================================================
```

### Notes on output

- The `Distribution details` block only appears on Linux. On Windows
  or macOS, only the top section (System/Release/Version/Machine)
  prints.
- `Release` here reflects the kernel release string, while
  `Distribution` reflects the userland distribution built on top of
  it — the two are independent (e.g. Ubuntu 24.04 can run on several
  different kernel release numbers depending on updates).

---

## 10. kernel_version.py

### What it does

Prints the exact kernel version, equivalent to running `uname -r`,
along with the rest of the fields from `platform.uname()`.

### How to run

```bash
python3 kernel_version.py
```

No arguments or flags.

### Sample output

```
==================================================
 KERNEL VERSION
==================================================
Kernel release (uname -r)    : 6.18.5-fc-v20
Kernel version                : #1 SMP PREEMPT_DYNAMIC @0
System name                   : Linux
Node name                     : vm
Machine                       : x86_64
Processor                     : x86_64
==================================================
```

### Notes on output

- `Kernel release (uname -r)` is the single field most people are
  looking for when they ask "what kernel am I running" — it matches
  the output of running `uname -r` directly in a terminal.
- `Node name` is the machine's hostname, not a network identifier —
  it will match whatever `hostname` returns locally.
- On Windows, this script still runs, but `Kernel release` reports the
  Windows build number instead of a Linux-style kernel string, since
  `platform.uname()` maps to the closest equivalent field on each OS.

---

## 11. boot_time.py

### What it does

Reads the system boot timestamp with `psutil.boot_time()`, converts it
to a readable date/time, and calculates uptime by comparing it to the
current time.

### How to run

```bash
python3 boot_time.py
```

No arguments or flags.

### Sample output

```
==================================================
 BOOT TIME
==================================================
Boot time      : 2026-08-13 11:52:19
Current time   : 2026-08-13 11:53:09
Uptime         : 0:00:50
==================================================
```

### Notes on output

- `Boot time` is a fixed point in time and only changes when the
  machine is actually restarted.
- `Uptime` is formatted as `H:MM:SS` for short uptimes, and expands to
  include days automatically for machines that have been running a
  long time, e.g. `4 days, 3:12:47`.
- On a freshly started VM, container, or cloud instance, uptime will
  naturally be very small, as in the sample above.

---

## 12. logged_in_users.py

### What it does

Enumerates active login sessions using `psutil.users()`: username,
terminal, originating host, and login timestamp.

### How to run

```bash
python3 logged_in_users.py
```

No arguments or flags.

### Sample output (no active sessions, e.g. running inside a container/CI job)

```
============================================================
 LOGGED-IN USERS
============================================================
No active user sessions found.
```

### Sample output (typical interactive machine)

```
============================================================
 LOGGED-IN USERS
============================================================

User       : ahmad
Terminal   : pts/0
Host       : 192.168.1.14
Login time : 2026-08-13 09:15:02
PID        : 4821

Total active sessions: 1
============================================================
```

### Notes on output

- `No active user sessions found.` is expected and correct behavior
  when the script runs somewhere with no interactive login sessions —
  containers, CI runners, and some remote sandboxes commonly report
  this, as in the first sample above.
- `Host` shows `local` instead of an IP address for sessions that
  originated on the machine itself (a local terminal, not SSH).
- On a shared server with multiple people logged in via SSH, this list
  grows to one block per session, including multiple sessions from the
  same user if they have more than one terminal open.

---

## 13. gpu_info.py

### What it does

Tries `nvidia-smi` first (NVIDIA GPUs), then `rocm-smi` (AMD GPUs). If
neither tool is present, it falls back to scanning `lspci` output on
Linux for VGA/3D controller entries, though that fallback cannot
report VRAM usage — only that a GPU device exists.

### How to run

```bash
python3 gpu_info.py
```

No arguments or flags.

### Sample output (no GPU tools available, e.g. inside a sandboxed VM)

```
============================================================
 GPU INFORMATION
============================================================
[!] No NVIDIA/AMD tool found, and 'lspci' is unavailable.
    Cannot detect GPU on this system.
============================================================
```

### Sample output (typical machine with an NVIDIA GPU)

```
============================================================
 GPU INFORMATION
============================================================
[*] NVIDIA GPU(s) detected:

GPU 0: NVIDIA GeForce RTX 4070
  Total VRAM   : 12282 MB
  Used VRAM    : 1904 MB
  Free VRAM    : 10378 MB
  GPU Utilization: 7%

============================================================
```

### Notes on output

- The message differs completely depending on what is detected —
  NVIDIA output includes full VRAM usage figures; AMD output (via
  `rocm-smi`) is formatted differently since it comes straight from
  that tool's own text output; the `lspci` fallback only lists device
  names with no memory figures at all.
- `No NVIDIA/AMD tool found...` does not necessarily mean there is no
  GPU — it means neither vendor's command-line tool is installed, or
  `lspci` itself is missing (both true on the sandboxed environment
  used for the sample above).
- On a machine with more than one GPU, `nvidia-smi` output repeats the
  `GPU 0`, `GPU 1`, etc. block for each card detected.

---

## Summary Table: Run Command per Script

| Script | Default run command | Optional flags |
|---|---|---|
| cpu_info.py | `python3 cpu_info.py` | none |
| memory_info.py | `python3 memory_info.py` | none |
| disk_info.py | `python3 disk_info.py` | none |
| network_interfaces.py | `python3 network_interfaces.py` | none |
| installed_software.py | `python3 installed_software.py` | `--limit N` |
| environment_variables.py | `python3 environment_variables.py` | `--key NAME` |
| bios_info.py | `python3 bios_info.py` | run with `sudo` for full fields on Linux |
| motherboard_info.py | `python3 motherboard_info.py` | run with `sudo` for full fields on Linux |
| os_version.py | `python3 os_version.py` | none |
| kernel_version.py | `python3 kernel_version.py` | none |
| boot_time.py | `python3 boot_time.py` | none |
| logged_in_users.py | `python3 logged_in_users.py` | none |
| gpu_info.py | `python3 gpu_info.py` | none |
