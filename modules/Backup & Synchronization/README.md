# Backup & Synchronization — Python Automation Scripts

This folder contains **10 standalone Python scripts**, each covering one
backup/sync topic. Every script is independent — you only need the ones
you actually want to use, and each can be run directly with `python3`.

These scripts are written to accompany the module here:
**https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/Backup%20&%20Synchronization/scripts**


> ⚠️ **Caution before you install/run anything from that repository (or this folder):**
> - **Read the code before running it**, especially `mirror_folders.py` (deletes files in the destination) and `rotate_backups.py` (deletes old backups). Both scripts support `--dry-run` — always test with `--dry-run` first on real data.
> - **Never run backup/sync/deletion scripts as root/admin** unless you fully understand what paths they will touch. A typo in `--dest` or `--dir` can affect the wrong folder.
> - **Test on sample/throwaway data first**, not on your only copy of anything important.
> - This is third-party, community-maintained code from a public GitHub repo, not an official or audited product — treat it the same as any script you download from the internet: review it, understand it, then run it.
> - `encrypt_backup.py`: if you forget your password, the data is **unrecoverable**. There is no backdoor or reset.
> - `remote_backup.py` requires you to separately install and configure `rsync` and/or `rclone` on your own system — this repo does not install or configure those tools for you.

---

## Contents

| Script | Topic # | What it does |
|---|---|---|
| `create_backup.py` | 194 | Full snapshot backup of one or more source directories |
| `incremental_backup.py` | 195 | Copies only files changed since the last run of this script |
| `differential_backup.py` | 196 | Copies files changed since the last **full** backup |
| `sync_directories.py` | 197 | Bi-directional sync so two directories match |
| `mirror_folders.py` | 198 | One-way replication (source → destination, deletes extras) |
| `verify_backup.py` | 199 | SHA-256 hash manifest generation & verification |
| `compress_backup.py` | 200 | Compress a directory into `.tar.gz` or `.zip` |
| `encrypt_backup.py` | 201 | Encrypt/decrypt a backup file with a password (AES/Fernet) |
| `rotate_backups.py` | 202 | Delete old backups per a retention policy |
| `remote_backup.py` | 203 | Push a backup to remote storage via `rsync` or `rclone` |

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
   Only `encrypt_backup.py` needs an extra package (`cryptography`); every
   other script uses just the Python standard library.
4. For `remote_backup.py` only, also install the external tool you plan
   to use (these are system tools, not `pip` packages):
   - **rsync** — usually preinstalled on Linux/macOS.
     - Debian/Ubuntu: `sudo apt install rsync`
     - macOS (Homebrew): `brew install rsync`
   - **rclone** — install from https://rclone.org/install/, then run
     `rclone config` once to set up your cloud remote (e.g. S3, Google
     Drive, Backblaze B2) before using this script.
5. Confirm Python 3.9+ is installed: `python3 --version`

---

## General usage pattern

Every script uses `argparse`, so you can always run:
```bash
python3 <script_name>.py --help
```
to see all options, defaults, and short flags.

---

## 1. `create_backup.py` — Full Backup

Creates a complete, timestamped copy of one or more source directories.

```bash
python3 create_backup.py --source /path/to/data --dest /path/to/backups
python3 create_backup.py --source /data1 --source /data2 --dest /backups --name nightly
```

**Expected output:**
- New folder: `<dest>/<name>_full_<YYYYMMDD_HHMMSS>/` with every file copied in.
- Marker file `<dest>/.last_full_backup.json` (used later by `differential_backup.py`).
- Console log of each file copied + a summary (file count, total size, elapsed time).

---

## 2. `incremental_backup.py` — Incremental Backup

Copies only files modified since the **last time this script ran** (full or incremental).

```bash
python3 incremental_backup.py --source /path/to/data --dest /path/to/backups
```

**Expected output:**
- New folder `<dest>/incremental_<timestamp>/` containing only changed files.
- State file `<dest>/.incremental_state.json` updated after each run.
- If nothing changed: prints "No changes detected" and creates no folder.
- Note: the very first run has no prior state, so it will copy everything once — this is expected.

---

## 3. `differential_backup.py` — Differential Backup

Copies every file changed since the **last full backup** (does not reset after each differential run). Requires `create_backup.py` to have been run at least once first.

```bash
python3 differential_backup.py --source /path/to/data --dest /path/to/backups
```

**Expected output:**
- New folder `<dest>/differential_<timestamp>/` with all files changed since the last full backup.
- Errors out with a clear message if `.last_full_backup.json` doesn't exist yet.

---

## 4. `sync_directories.py` — Bi-Directional Sync

Makes two directories match by copying newer/missing files in both directions.

```bash
python3 sync_directories.py --dir-a /path/A --dir-b /path/B
python3 sync_directories.py --dir-a /path/A --dir-b /path/B --dry-run
```

**Expected output:**
- Console log: `[COPY A->B]`, `[COPY B->A]`, or skip messages for identical files.
- Summary of files copied each direction and files skipped.
- **Note:** does not propagate deletions (a file removed from one side reappears from the other on next sync) — this is intentional to prevent accidental data loss.

---

## 5. `mirror_folders.py` — One-Way Mirror ⚠️ Destructive

Makes destination an **exact** copy of source, deleting anything in destination not present in source.

```bash
python3 mirror_folders.py --source /path/to/source --dest /path/to/mirror --dry-run
python3 mirror_folders.py --source /path/to/source --dest /path/to/mirror
```

**Expected output:**
- Console log: `[COPY]`, `[UPDATE]`, `[DELETE]` for each affected file.
- Summary counts + elapsed time.
- **Always run with `--dry-run` first** — files only in the destination are permanently deleted.

---

## 6. `verify_backup.py` — Integrity Verification

Generates or checks a SHA-256 manifest for a directory or `.zip`/`.tar.gz` archive.

```bash
# Generate baseline manifest right after making a backup
python3 verify_backup.py --mode generate --path /path/to/backup_folder --manifest manifest.json

# Later, verify nothing has silently corrupted/changed
python3 verify_backup.py --mode verify --path /path/to/backup_folder --manifest manifest.json
```

**Expected output:**
- `generate`: writes `manifest.json`, prints number of files hashed.
- `verify`: prints `[OK]`, `[MODIFIED]`, `[MISSING]`, `[NEW]` per file, then a summary.
- Exit code `0` if everything matches, `1` if something failed — safe to use in scripts/cron.

---

## 7. `compress_backup.py` — Compress Backups

Compresses a directory into a single `.tar.gz` or `.zip` archive.

```bash
python3 compress_backup.py --source /path/to/backup_folder --format tar.gz
python3 compress_backup.py --source /path/to/backup_folder --format zip --output /path/to/archive.zip
```

**Expected output:**
- One archive file (auto-named with a timestamp if `--output` isn't given).
- Console log of files added + summary: original size, compressed size, % space saved.
- Note: very small/already-compressed test folders may show a *negative* saving percentage due to archive overhead — this is normal and only relevant for small demo data, not real backups.

---

## 8. `encrypt_backup.py` — Encrypt/Decrypt Backups

Encrypts or decrypts a file using a password-derived symmetric key (PBKDF2 + Fernet/AES). Requires `cryptography` (see `requirements.txt`).

```bash
python3 encrypt_backup.py --mode encrypt --input backup.tar.gz --output backup.tar.gz.enc --password "MyStrongPassword"
python3 encrypt_backup.py --mode decrypt --input backup.tar.gz.enc --output backup.tar.gz --password "MyStrongPassword"
```

Omit `--password` to be prompted securely (input hidden) instead of typing it on the command line (recommended, since command-line arguments can be visible in your shell history / process list).

**Expected output:**
- `encrypt`: creates the encrypted `--output` file (safe to upload anywhere, e.g. cloud storage).
- `decrypt`: recreates the original file. Wrong password → clear error, no corrupted file written.
- **Caution:** there is no password recovery. Losing the password means losing the data permanently.

---

## 9. `rotate_backups.py` — Backup Rotation / Retention

Deletes old backups by age and/or keeps only the N most recent.

```bash
python3 rotate_backups.py --dir /path/to/backups --max-age-days 30
python3 rotate_backups.py --dir /path/to/backups --keep-last 5
python3 rotate_backups.py --dir /path/to/backups --max-age-days 30 --keep-last 10 --dry-run
```

**Expected output:**
- Console log: `[KEEP]` / `[DELETE]` per backup item with age and size.
- Summary: scanned / kept / deleted counts and total space freed.
- Marker/state files (names starting with `.`, e.g. `.last_full_backup.json`) are always preserved.
- **Always test with `--dry-run` first** — deletions are permanent.

---

## 10. `remote_backup.py` — Remote Push via rsync/rclone

Thin wrapper that calls your system's installed `rsync` or `rclone` to push a backup to remote storage. Does not reimplement transfer logic itself.

```bash
# rsync over SSH
python3 remote_backup.py --tool rsync --source /path/to/backup --dest user@server:/remote/backups/

# rsync to a locally mounted drive
python3 remote_backup.py --tool rsync --source /path/to/backup --dest /mnt/external_drive/backups/

# rclone to a configured cloud remote
python3 remote_backup.py --tool rclone --source /path/to/backup --dest mys3:backups/

# dry run (nothing transferred)
python3 remote_backup.py --tool rclone --source /path/to/backup --dest mys3:backups/ --dry-run
```

**Expected output:**
- Prints the exact `rsync`/`rclone` command being run, then streams that tool's own live progress output.
- Exits with the same exit code as the underlying tool.
- Clear error + install instructions if `rsync`/`rclone` isn't found on your `PATH`.
- **Prerequisite:** `rclone` remotes must already be configured via `rclone config` before this script can use them; this script does not set up cloud credentials for you.

---

## Suggested combined workflow

```bash
# 1. Full backup
python3 create_backup.py --source /data --dest /backups

# 2. Nightly differentials in between full backups
python3 differential_backup.py --source /data --dest /backups

# 3. Verify integrity
python3 verify_backup.py --mode generate --path /backups/data_full_20260101_020000 --manifest /backups/manifest.json

# 4. Compress
python3 compress_backup.py --source /backups/data_full_20260101_020000 --format tar.gz

# 5. Encrypt before sending off-site
python3 encrypt_backup.py --mode encrypt --input /backups/data_full_20260101_020000.tar.gz --output /backups/data_full_20260101_020000.tar.gz.enc --password "..."

# 6. Push to the cloud
python3 remote_backup.py --tool rclone --source /backups/data_full_20260101_020000.tar.gz.enc --dest mys3:offsite-backups/

# 7. Clean up old local backups
python3 rotate_backups.py --dir /backups --keep-last 7 --dry-run   # check first
python3 rotate_backups.py --dir /backups --keep-last 7             # then actually delete
```

---

## Tested environment

- Python 3.9+ (standard library only, except `encrypt_backup.py` which needs `cryptography`)
- Linux / macOS (paths and shell examples above use `/`; Windows users should adjust paths and use `venv\Scripts\activate`)
- All 10 scripts were smoke-tested end-to-end (create → incremental → differential → sync → mirror → compress → verify → encrypt/decrypt → rotate) before publishing.
