# File & Directory Operations — Python Automation Scripts

This folder contains **33 standalone Python scripts**, each automating a single, specific file or directory operation (listing, creating, deleting, copying, moving, archiving, hashing, encrypting, organizing, and more).

Every script:
- Is completely **independent** — you only need the one file for the task you want.
- Can be run directly from the command line.
- Uses `argparse`, so running it with `-h` shows help and usage.
- Prints clear success/error messages so you always know what happened.

> **Repository:** https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/File%20%26%20Directory%20Operations/scripts

---

## ⚠️ Important Cautions Before You Start

1. **These scripts modify your real files.** Operations like delete, move, rename, and "clean temporary files" are **destructive and mostly irreversible**. There is no Recycle Bin/Trash — deleted files are gone.
2. **Always test on a throwaway folder first.** Create a dummy test directory with sample files before running any script on real data.
3. **Read the confirmation prompts.** Scripts that delete things (`delete_files.py`, `delete_directories.py`, `clean_temporary_files.py`) ask `[y/N]` before doing anything, unless you pass `--force`. Don't use `--force` until you're confident.
4. **Back up important data** before running `encrypt_files.py`, `split_large_files.py`, or `organize_files.py` on folders you care about.
5. **Remember your password.** `encrypt_files.py` has no password-recovery option. If you forget the password, the encrypted file **cannot** be decrypted.
6. Scripts that watch/monitor (`watch_directories.py`, `monitor_file_changes.py`) run in an infinite loop — stop them with `Ctrl+C`.

---

## 📦 Requirements

- **Python 3.7+** installed on your system.
- Check your version:
  ```bash
  python3 --version
  ```
- Most scripts use **only the Python standard library** — nothing extra to install.
- Two scripts (`encrypt_files.py`, `decrypt_files.py`) need the `cryptography` package, listed in `requirements.txt`.

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aw-junaid/Python-System-Administration.git
   cd "Python-System-Administration/modules/File & Directory Operations/scripts"
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
   > If you don't plan to use `encrypt_files.py` / `decrypt_files.py`, you can skip this step — every other script works with zero installs.

4. **Run any script:**
   ```bash
   python3 script_name.py --help
   ```
   This shows the exact arguments each script expects.

---

## 🗂 Full List of Scripts, Usage & Expected Output

Below, `python3` is used for Linux/macOS. On Windows, use `python` instead.

### 1. `list_directory.py` — List Directory Contents
```bash
python3 list_directory.py .
python3 list_directory.py /home/user/Documents --long
```
**Expected output:** A list of files/folders in the target directory, tagged `[DIR]` or `[FILE]`. With `--long`, also shows size and last-modified time.

---

### 2. `create_files.py` — Create Files
```bash
python3 create_files.py notes.txt
python3 create_files.py a.txt b.txt --content "Hello World"
```
**Expected output:** `Created: notes.txt` for each new file. Existing files are skipped, not overwritten.

---

### 3. `delete_files.py` — Delete Files
```bash
python3 delete_files.py old.txt
python3 delete_files.py a.txt b.txt --force
```
**Expected output:** Confirmation prompt per file (unless `--force`), then `Deleted: old.txt`.
**Caution:** Permanent deletion — no recovery.

---

### 4. `rename_files.py` — Rename Files
```bash
python3 rename_files.py report.txt final_report.txt
```
**Expected output:** `Renamed: 'report.txt' -> 'final_report.txt'`. Fails if the target name already exists.

---

### 5. `move_files.py` — Move Files
```bash
python3 move_files.py /home/user/Archive report.txt notes.txt
```
**Expected output:** Each file moved into the destination folder; destination is created automatically if missing.

---

### 6. `copy_files.py` — Copy Files
```bash
python3 copy_files.py /home/user/Backup report.txt notes.txt
```
**Expected output:** Each file copied (original stays in place) into the destination folder.

---

### 7. `copy_directories.py` — Copy Directories
```bash
python3 copy_directories.py /home/user/Project /home/user/Project_backup
```
**Expected output:** The entire folder tree is duplicated at the destination. Fails if destination already exists (to avoid overwriting).

---

### 8. `delete_directories.py` — Delete Directories
```bash
python3 delete_directories.py old_project --force
```
**Expected output:** The folder and everything inside it is deleted.
**Caution:** Permanent — deletes all nested files/folders at once.

---

### 9. `create_nested_directories.py` — Create Nested Directories
```bash
python3 create_nested_directories.py projects/2026/january/reports
```
**Expected output:** All intermediate folders are created in one go (like `mkdir -p`).

---

### 10. `traverse_directories.py` — Traverse Directories Recursively
```bash
python3 traverse_directories.py /home/user/Documents
```
**Expected output:** An indented tree view of every subfolder and file, plus a total file/folder count.

---

### 11. `find_files_by_extension.py` — Find Files by Extension
```bash
python3 find_files_by_extension.py /home/user/Documents .pdf
```
**Expected output:** Full paths of every file with that extension found anywhere in the tree.

---

### 12. `find_duplicate_files.py` — Find Duplicate Files
```bash
python3 find_duplicate_files.py /home/user/Downloads
```
**Expected output:** Groups of files that are byte-for-byte identical (compared via SHA-256 hash), so you can see and manually clean up duplicates.

---

### 13. `search_file_contents.py` — Search File Contents
```bash
python3 search_file_contents.py /home/user/Project "TODO"
python3 search_file_contents.py /home/user/Project "import os" --extension .py
```
**Expected output:** `file_path:line_number: matching line` for every match, like a simple `grep -r`.

---

### 14. `calculate_file_hashes.py` — Calculate File Hashes
```bash
python3 calculate_file_hashes.py document.pdf
python3 calculate_file_hashes.py a.txt b.txt --algo md5
```
**Expected output:** `ALGO  hexdigest  filepath` for each file — useful for verifying file integrity.

---

### 15. `compare_two_files.py` — Compare Two Files
```bash
python3 compare_two_files.py old_version.txt new_version.txt
```
**Expected output:** Either `Files are IDENTICAL` or a unified line-by-line diff showing what changed.

---

### 16. `compare_directories.py` — Compare Directories
```bash
python3 compare_directories.py /home/user/ProjectA /home/user/ProjectB
```
**Expected output:** Lists of files only in A, only in B, files that differ, and a count of identical files — recursively through subfolders.

---

### 17. `get_file_metadata.py` — Get File Metadata
```bash
python3 get_file_metadata.py report.pdf
```
**Expected output:** Size, created/modified/accessed timestamps, permissions, and path info for the file.

---

### 18. `monitor_file_changes.py` — Monitor File Changes
```bash
python3 monitor_file_changes.py config.json --interval 5
```
**Expected output:** Runs continuously, printing a timestamped message whenever the file's size or modified time changes. Stop with `Ctrl+C`.

---

### 19. `create_temporary_files.py` — Create Temporary Files
```bash
python3 create_temporary_files.py --content "scratch data" --keep
```
**Expected output:** Path to a newly created temp file. Without `--keep`, the file is auto-deleted the moment the script exits (useful for testing the concept).

---

### 20. `create_temporary_directories.py` — Create Temporary Directories
```bash
python3 create_temporary_directories.py --keep
```
**Expected output:** Path to a new temp directory, kept on disk only if `--keep` is passed.

---

### 21. `compress_files.py` — Compress Files (ZIP)
```bash
python3 compress_files.py backup.zip file1.txt file2.txt
python3 compress_files.py project.zip my_project_folder
```
**Expected output:** `backup.zip` created containing the given files/folders.

---

### 22. `extract_zip_archives.py` — Extract ZIP Archives
```bash
python3 extract_zip_archives.py backup.zip ./extracted
```
**Expected output:** Archive contents extracted into the destination folder; count of extracted items shown.

---

### 23. `create_tar_archives.py` — Create TAR Archives
```bash
python3 create_tar_archives.py backup.tar file1.txt folder1
python3 create_tar_archives.py backup.tar.gz file1.txt folder1 --gzip
```
**Expected output:** A `.tar` (or `.tar.gz` with `--gzip`) archive containing the specified items.

---

### 24. `extract_tar_archives.py` — Extract TAR Archives
```bash
python3 extract_tar_archives.py backup.tar.gz ./extracted
```
**Expected output:** Archive contents extracted into the destination folder (handles both `.tar` and `.tar.gz`).

---

### 25. `encrypt_files.py` — Encrypt Files
**Requires:** `pip install -r requirements.txt`
```bash
python3 encrypt_files.py secret.txt MyStrongPassword123
```
**Expected output:** A new `secret.txt.enc` file (AES-based encryption via Fernet). The password is **not stored anywhere** — remember it.
**Caution:** Passing passwords on the command line can be seen in shell history; use in a private/test environment.

---

### 26. `decrypt_files.py` — Decrypt Files
**Requires:** `pip install -r requirements.txt`
```bash
python3 decrypt_files.py secret.txt.enc MyStrongPassword123
```
**Expected output:** The original file restored (e.g. `secret.txt`). Wrong password → `Error: decryption failed.`

---

### 27. `split_large_files.py` — Split Large Files
```bash
python3 split_large_files.py bigvideo.mp4 100
```
**Expected output:** Multiple files `bigvideo.mp4.part0`, `.part1`, etc., each ≤100 MB.

---

### 28. `merge_split_files.py` — Merge Split Files
```bash
python3 merge_split_files.py bigvideo.mp4
```
**Expected output:** Reassembles `bigvideo.mp4.part0`, `.part1`, ... back into the original `bigvideo.mp4` (or a custom name with `--output`).

---

### 29. `watch_directories.py` — Watch Directories for Changes
```bash
python3 watch_directories.py /home/user/Downloads --interval 5
```
**Expected output:** Runs continuously, printing `ADDED`, `REMOVED`, or `MODIFIED` with timestamps as files change in the folder. Stop with `Ctrl+C`.

---

### 30. `clean_temporary_files.py` — Clean Temporary Files
```bash
python3 clean_temporary_files.py /home/user/Project --force
```
**Expected output:** Deletes common junk files (`.tmp`, `.bak`, `.log`, `.cache`, `.swp`) and folders (`__pycache__`, `.pytest_cache`) found in the tree.
**Caution:** Review the preview list before confirming — deletion is permanent.

---

### 31. `organize_files.py` — Automatically Organize Files
```bash
python3 organize_files.py /home/user/Downloads
```
**Expected output:** Files sorted into subfolders — `Images/`, `Documents/`, `Videos/`, `Music/`, `Archives/`, `Code/`, `Others/` — based on extension.

---

### 32. `batch_rename_files.py` — Batch Rename Files
```bash
python3 batch_rename_files.py /home/user/Photos vacation_
python3 batch_rename_files.py /home/user/Photos photo_ --start 100 --extension .png
```
**Expected output:** Files renamed sequentially, e.g. `vacation_001.jpg`, `vacation_002.jpg`, ...

---

### 33. `change_file_timestamps.py` — Change File Timestamps
```bash
python3 change_file_timestamps.py report.txt
python3 change_file_timestamps.py report.txt --date "2025-01-15 10:30:00"
```
**Expected output:** Updates the file's access/modified time to now (or the given date). Creates the file if it doesn't exist, like `touch`.

---

## 🧪 Quick Test Workflow

To safely try these scripts without touching real data:

```bash
mkdir test_area && cd test_area
python3 ../create_files.py sample1.txt sample2.txt --content "test data"
python3 ../list_directory.py . --long
python3 ../calculate_file_hashes.py sample1.txt
python3 ../compress_files.py backup.zip sample1.txt sample2.txt
python3 ../delete_files.py sample1.txt sample2.txt --force
```

---

## 📄 License / Usage Notes

- These scripts are provided for educational and administrative automation purposes.
- Always review a script's code before running it on important or production data.
- The author is not responsible for data loss resulting from misuse of destructive operations (delete, clean, split/merge, encrypt).
