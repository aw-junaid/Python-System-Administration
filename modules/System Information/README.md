# System Information — Python Scripts

Standalone Python automation scripts that collect and display system
information: CPU, memory, disk, network, installed software,
environment variables, BIOS, motherboard, OS/kernel version, boot
time, logged-in users, and GPU details.

Part of: [Python-System-Administration](https://github.com/aw-junaid/Python-System-Administration) → `modules/System Information/`

---

## ⚠️ Caution Before You Run These Scripts

- **Source of these scripts:** these files are meant to be added to the
  `modules/System Information/scripts` folder of the
  [Python-System-Administration](https://github.com/aw-junaid/Python-System-Administration)
  repository. If you cloned that repo, these scripts belong at:
  `modules/System Information/scripts/*.py`
- **Read before running.** Every script only *reads* system data — none
  of them modify, delete, or reconfigure anything on your machine.
  Still, always review a script's source before running it, especially
  with elevated privileges.
- **Some scripts need `sudo`/Administrator** to see certain fields
  (e.g. BIOS/motherboard serial numbers on Linux). Without elevated
  privileges they will simply print `Permission denied` for those
  specific fields — the rest of the output still works.
- **Platform support varies per script.** Most scripts work on Linux,
  Windows, and macOS via `psutil`. A few (`installed_software.py`,
  `bios_info.py`, `motherboard_info.py`) rely on OS-specific tools
  (`dpkg`/`rpm`, `/sys/class/dmi/id`, or `wmi` on Windows) — see each
  script's own docstring and the table below for exact support.
- **`gpu_info.py`** depends on vendor tools (`nvidia-smi` for NVIDIA,
  `rocm-smi` for AMD) already being installed by your GPU driver. It
  does not install drivers for you.
- **Do not run scripts as root/Administrator by default.** Only elevate
  when a script specifically tells you a field needs it.
- **Sensitive output.** BIOS/motherboard serial numbers, MAC addresses,
  and installed package lists can be sensitive. Don't paste raw output
  into public issues/chats without reviewing it first.

---

## 📁 Files in This Module

| Script | Purpose |
|---|---|
| `cpu_info.py` | Physical cores, logical threads, current/min/max frequency, per-core usage |
| `memory_info.py` | Total, available, used, and free RAM + swap statistics |
| `disk_info.py` | Partition sizes, mount points, filesystem types, usage per partition |
| `network_interfaces.py` | MAC addresses and IPv4/IPv6 configuration per network interface |
| `installed_software.py` | Lists installed packages by querying `dpkg` (Debian/Ubuntu) or `rpm` (RHEL/Fedora) |
| `environment_variables.py` | Prints environment variables visible to the current session, including `PATH` |
| `bios_info.py` | BIOS vendor, version, release date, (serial number needs elevated privileges) |
| `motherboard_info.py` | Baseboard manufacturer, product name, version, serial number |
| `os_version.py` | OS release name, version, and distribution details (Linux) |
| `kernel_version.py` | Exact kernel release, equivalent to `uname -r` |
| `boot_time.py` | Precise system boot timestamp and current uptime |
| `logged_in_users.py` | Currently active user sessions: user, terminal, host, login time |
| `gpu_info.py` | Detects NVIDIA/AMD GPUs and reports VRAM usage |

---

## 🖥️ Platform Support

| Script | Linux | Windows | macOS |
|---|:---:|:---:|:---:|
| `cpu_info.py` | ✅ | ✅ | ✅ |
| `memory_info.py` | ✅ | ✅ | ✅ |
| `disk_info.py` | ✅ | ✅ | ✅ |
| `network_interfaces.py` | ✅ | ✅ | ✅ |
| `installed_software.py` | ✅ (dpkg/rpm only) | ❌ | ❌ |
| `environment_variables.py` | ✅ | ✅ | ✅ |
| `bios_info.py` | ✅ (needs root for serial) | ✅ (needs `wmi`) | ❌ |
| `motherboard_info.py` | ✅ (needs root for serial) | ✅ (needs `wmi`) | ❌ |
| `os_version.py` | ✅ | ✅ | ✅ |
| `kernel_version.py` | ✅ | ✅ (reports Windows build) | ✅ |
| `boot_time.py` | ✅ | ✅ | ✅ |
| `logged_in_users.py` | ✅ | ✅ | ✅ |
| `gpu_info.py` | ✅ (needs `nvidia-smi`/`rocm-smi`) | ✅ (needs `nvidia-smi`) | ⚠️ limited |

---

## 🔧 Installation

1. Clone the repository (or copy these files into your existing clone):

   ```bash
   git clone https://github.com/aw-junaid/Python-System-Administration.git
   cd "Python-System-Administration/modules/System Information/scripts"
   ```

2. (Recommended) create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   > On Linux, `wmi` is skipped automatically (it's Windows-only).
   > On Windows, `distro` is skipped automatically (it's Linux-only).

---

## ▶️ How to Run

Each script is standalone — run any one individually:

```bash
python3 cpu_info.py
python3 memory_info.py
python3 disk_info.py
python3 network_interfaces.py
python3 installed_software.py
python3 environment_variables.py
python3 bios_info.py
python3 motherboard_info.py
python3 os_version.py
python3 kernel_version.py
python3 boot_time.py
python3 logged_in_users.py
python3 gpu_info.py
```

Some scripts accept optional flags:

```bash
python3 installed_software.py --limit 50     # show only first 50 packages
python3 environment_variables.py --key PATH  # show a single variable
```

For fields that need elevated privileges (BIOS/motherboard serial numbers on Linux):

```bash
sudo python3 bios_info.py
sudo python3 motherboard_info.py
```

---

## ✅ Expected Output

Every script prints a bordered, human-readable text block to the
terminal — no files are written and no GUI is opened. For example:

```
==================================================
 CPU INFORMATION
==================================================
Processor                   : x86_64
Architecture                 : x86_64
Physical cores               : 4
Logical threads              : 8
Current frequency (MHz)      : 2100.0
...
```

If a piece of data isn't available (e.g. no GPU present, or a
permission was denied), the script prints a clear message instead of
crashing, such as:

```
Permission denied (try running with sudo)
```

or

```
[!] No GPU devices found via lspci.
```

---

## 🧩 Adding These Scripts to the Repo

If you're contributing these to
`aw-junaid/Python-System-Administration`, place the `.py` files in:

```
modules/System Information/scripts/
```

and this `README.md` + `requirements.txt` in:

```
modules/System Information/
```

alongside the existing `scripts/` folder referenced here:
https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/System%20Information/scripts

---

## 📜 License

Follows the license of the parent repository
([Python-System-Administration](https://github.com/aw-junaid/Python-System-Administration)).
