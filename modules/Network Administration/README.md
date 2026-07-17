# Network Administration — Python Automation Scripts

This folder contains **14 standalone Python scripts**, each covering one
network-administration topic. Every script is independent — use only
the ones you need, and each can be run directly with `python3`.


> ⚠️ **Caution before you install/run anything from that repository (or this folder):**
> - **Only scan, probe, or run commands against hosts and networks you own or have explicit written permission to test.** `scan_ports.py`, `test_connectivity.py`, `check_host_availability.py`, `ssh_automation.py`, and `configure_firewall.py` interact directly with network hosts — running them against systems you don't control/own may violate that system's acceptable-use policy or local law.
> - **`configure_firewall.py` can lock you out of a remote machine** if you block the very port you're connected through (e.g. SSH/22, RDP/3389). Test on a machine with local/console access first, or double-check the port/protocol before running `--action block` remotely.
> - **Never pass passwords on the command line in shared/logged environments** (`--password` is visible in shell history and process lists). Every script that needs a password lets you omit `--password`/`--key` and will prompt you securely instead.
> - **Plain FTP (`ftp_download.py` / `ftp_upload.py` without `--tls`) sends credentials and data unencrypted.** Prefer `--tls` (FTPS) or, better, use `sftp_automation.py`/`scp_transfer.py` (SSH-based, encrypted) whenever the server supports it.
> - This is third-party, community-maintained code from a public GitHub repo, not an official or audited product — treat it the same as any script you download from the internet: review it, understand it, then run it.
> - Rules added by `configure_firewall.py` on Linux via `iptables` are typically **not persisted across reboots** unless you also save them with your distro's mechanism (e.g. `iptables-save`, `netfilter-persistent`).

---

## Contents

| Script | Topic # | What it does |
|---|---|---|
| `ping_hosts.py` | 204 | ICMP ping to verify Layer-3 connectivity |
| `scan_ports.py` | 205 | TCP connect scan to enumerate open ports |
| `check_host_availability.py` | 206 | Combined ping + TCP probe health check |
| `resolve_dns.py` | 207 | Look up A, AAAA, MX, TXT, NS, CNAME, SOA records via `dnspython` |
| `whois_lookup.py` | 208 | Query domain registration/expiration data (raw WHOIS protocol) |
| `get_public_ip.py` | 209 | Determine your network's public/NAT IP via an external API |
| `get_local_ip.py` | 210 | Identify this machine's private LAN IP address(es) |
| `test_connectivity.py` | 211 | Socket-based TCP connectivity tests to specific endpoints |
| `ftp_download.py` | 212 | Download files from an FTP/FTPS server via `ftplib` |
| `ftp_upload.py` | 213 | Upload/deploy files to an FTP/FTPS server via `ftplib` |
| `ssh_automation.py` | 214 | Execute remote commands over SSH via `paramiko` |
| `scp_transfer.py` | 215 | Securely copy a single file to/from a server over SSH |
| `sftp_automation.py` | 216 | Browse remote filesystems and transfer files/directories via SFTP |
| `configure_firewall.py` | 217 | Manage `iptables` (Linux) / Windows Firewall rules |

---

## Installation

1. Clone or download this folder (or the referenced GitHub repo).
2. (Recommended) create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Only `resolve_dns.py` (needs `dnspython`) and `ssh_automation.py` /
   `scp_transfer.py` / `sftp_automation.py` (need `paramiko`) require
   extra packages. Every other script uses just the Python standard
   library.
4. Make sure the system `ping` command is installed (needed by
   `ping_hosts.py` and `check_host_availability.py`). It ships by
   default with Windows/macOS/most Linux desktops; on minimal Linux
   images: `sudo apt install iputils-ping`.
5. `configure_firewall.py` needs `iptables` (standard on Linux) or
   `netsh` (built into Windows) — no extra install needed, but it must
   be run with root/sudo (Linux) or an Administrator/elevated terminal
   (Windows).
6. Confirm Python 3.9+ is installed: `python3 --version`

---

## General usage pattern

Every script uses `argparse`, so you can always run:
```bash
python3 <script_name>.py --help
```
to see all options, defaults, and short flags.

---

## 1. `ping_hosts.py` — Ping Hosts

```bash
python3 ping_hosts.py --host 8.8.8.8
python3 ping_hosts.py --host google.com --host 1.1.1.1 --count 4
```

**Expected output:** REACHABLE/UNREACHABLE per host with average round-trip time, plus a summary table. Exit code 0 if all hosts responded, 1 otherwise.

---

## 2. `scan_ports.py` — Scan Open Ports

```bash
python3 scan_ports.py --host 192.168.1.10 --ports 1-1024
python3 scan_ports.py --host example.com --ports 22,80,443,3306
```

**Expected output:** one `[OPEN]` line per open port found (with common service name when recognized), then a summary of ports scanned, ports open, and elapsed time.

⚠️ Only scan hosts/networks you own or are authorized to test.

---

## 3. `check_host_availability.py` — Combined Health Check

```bash
python3 check_host_availability.py --host example.com --port 80 --port 443
python3 check_host_availability.py --host 10.0.0.5 --port 22 --no-ping
```

**Expected output:** ping result, per-port OPEN/CLOSED status with latency, and an overall UP/DOWN verdict. Exit code 0 if UP, 1 if DOWN.

---

## 4. `resolve_dns.py` — Resolve DNS Records

```bash
python3 resolve_dns.py --domain example.com --type A
python3 resolve_dns.py --domain example.com --type A --type MX --type TXT
python3 resolve_dns.py --domain example.com --type A --resolver 1.1.1.1
```

**Expected output:** every matching record per requested type, with TTL, plus a summary of total records found. Requires `dnspython`.

---

## 5. `whois_lookup.py` — WHOIS Lookups

```bash
python3 whois_lookup.py --domain example.com
python3 whois_lookup.py --domain example.com --raw
```

**Expected output:** parsed summary of Registrar, Creation/Expiration/Updated dates, Domain Status, and Name Servers (field availability varies by TLD). `--raw` shows the complete unparsed WHOIS response. No extra package needed — talks directly to WHOIS servers on port 43.

---

## 6. `get_public_ip.py` — Retrieve Public IP

```bash
python3 get_public_ip.py
python3 get_public_ip.py --provider ifconfig.me
python3 get_public_ip.py --ipv6
```

**Expected output:** your public IPv4 (or IPv6) address and which provider returned it. Requires outbound internet access (HTTPS).

---

## 7. `get_local_ip.py` — Retrieve Local IP

```bash
python3 get_local_ip.py
python3 get_local_ip.py --all-interfaces
```

**Expected output:** hostname plus the primary local/LAN IP address; with `--all-interfaces`, every local IP found across interfaces/aliases.

---

## 8. `test_connectivity.py` — Test Network Connectivity

```bash
python3 test_connectivity.py --endpoint 8.8.8.8:53
python3 test_connectivity.py --endpoint db.internal:5432 --endpoint api.example.com:443
python3 test_connectivity.py --endpoint smtp.example.com:587 --timeout 5 --retries 3
```

**Expected output:** CONNECTED (with latency) or FAILED (with specific error) per endpoint, plus a summary table. Exit code 0 if all connected, 1 if any failed.

---

## 9. `ftp_download.py` — Download Files via FTP

```bash
python3 ftp_download.py --host ftp.example.com --user myuser --password mypass \
    --remote-path /pub/data.zip --local-path ./data.zip

python3 ftp_download.py --host ftp.example.com --anonymous \
    --remote-path /pub/readme.txt --local-path ./readme.txt
```

**Expected output:** connection/login confirmation, per-file download confirmation, and a summary (files downloaded, total size, elapsed time). Add `--tls` to use FTPS.

---

## 10. `ftp_upload.py` — Upload Files via FTP

```bash
python3 ftp_upload.py --host ftp.example.com --user myuser --password mypass \
    --local-path ./dist/index.html --remote-path /public_html/index.html

python3 ftp_upload.py --host ftp.example.com --user myuser --password mypass \
    --local-dir ./dist --remote-dir /public_html
```

**Expected output:** connection/login confirmation, per-file upload confirmation, and a summary. Add `--tls` to use FTPS.

---

## 11. `ssh_automation.py` — SSH Automation

```bash
python3 ssh_automation.py --host 10.0.0.5 --user admin --password mypass --command "df -h"

python3 ssh_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
    --command "cd /srv/app && git pull" --command "sudo systemctl restart app"

python3 ssh_automation.py --host web1.example.com --host web2.example.com \
    --user admin --key ~/.ssh/id_rsa --command "uptime"
```

**Expected output:** per host, connection confirmation then STDOUT/STDERR and exit status for each command; a final per-host SUCCESS/FAILED summary. Requires `paramiko`.

---

## 12. `scp_transfer.py` — SCP File Transfers

```bash
python3 scp_transfer.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
    --direction upload --local ./app.tar.gz --remote /srv/releases/app.tar.gz

python3 scp_transfer.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
    --direction download --remote /var/log/app.log --local ./app.log
```

**Expected output:** connection confirmation, a live progress line (bytes transferred/total, % complete, speed), then a summary (direction, paths, size, elapsed time, avg speed). Requires `paramiko`.

---

## 13. `sftp_automation.py` — SFTP Automation

```bash
python3 sftp_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
    --action list --remote-path /var/www

python3 sftp_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
    --action upload-dir --local-path ./dist --remote-path /var/www/html

python3 sftp_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
    --action download-dir --remote-path /var/log/app --local-path ./logs
```

**Expected output:** `list` prints a directory listing (type/size/permissions/name); upload-dir/download-dir print one line per file transferred plus a summary; upload-file/download-file confirm a single transfer. Requires `paramiko`.

---

## 14. `configure_firewall.py` — Configure Firewall Rules

```bash
# Linux (needs sudo)
sudo python3 configure_firewall.py --action allow --port 22 --protocol tcp
sudo python3 configure_firewall.py --action block --port 8080 --protocol tcp
sudo python3 configure_firewall.py --action list
sudo python3 configure_firewall.py --action remove --port 8080 --protocol tcp --direction block

# Windows (needs an elevated/Administrator terminal)
python configure_firewall.py --action allow --port 3389 --protocol tcp
python configure_firewall.py --action block --port 445 --protocol tcp
python configure_firewall.py --action list
```

**Expected output:** the exact `iptables`/`netsh` command being run, its output, and a SUCCESS/FAILED result. `list` shows the current rule set.

⚠️ Double-check `--port`/`--protocol` before using `--action block`, especially on a machine you're remotely connected to — you can lock yourself out.

---

## Suggested combined workflow

```bash
# 1. Confirm a remote server is reachable
python3 ping_hosts.py --host server.example.com
python3 check_host_availability.py --host server.example.com --port 22 --port 443

# 2. Check DNS is pointing where you expect
python3 resolve_dns.py --domain example.com --type A --type MX

# 3. Confirm your own public IP (e.g. to whitelist it on a firewall)
python3 get_public_ip.py

# 4. Deploy a new build over SFTP
python3 sftp_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
    --action upload-dir --local-path ./dist --remote-path /var/www/html

# 5. Restart the service remotely
python3 ssh_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
    --command "sudo systemctl restart app"

# 6. Verify the app port is now open
python3 test_connectivity.py --endpoint server.example.com:443
```

---

## Tested environment

- Python 3.9+ (standard library only, except `resolve_dns.py` which needs `dnspython`, and `ssh_automation.py`/`scp_transfer.py`/`sftp_automation.py` which need `paramiko`)
- Linux / macOS / Windows (Windows-specific notes given for `configure_firewall.py`)
- Core logic of all 14 scripts was smoke-tested (DNS resolution, port scanning, TCP connectivity checks, local IP detection, argument validation, and connection-failure handling) before publishing.
