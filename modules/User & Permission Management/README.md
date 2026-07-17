# User & Permission Management — Python Automation Scripts

This folder contains **9 standalone Python scripts**, each automating a single, specific user or permission management task (creating/deleting/modifying users, passwords, groups, file permissions, ownership, and ACLs).

Every script:
- Is completely **independent** — you only need the one file for the task you want.
- Can be run directly from the command line.
- Uses `argparse`, so running it with `-h` shows help and usage.
- Prints clear success/error messages so you always know what happened.

> **Repository:** https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/User%20%26%20Permission%20Management/scripts

---

## ⚠️ Important Cautions Before You Start

1. **Most scripts here require root/sudo (Linux/macOS) or Administrator (Windows)** because they modify real system accounts, groups, and file ownership. Run them with `sudo python3 script.py ...` on Linux/macOS.
2. **These scripts modify real system state** — user accounts, passwords, group memberships, file permissions, and ownership. There's no "undo." Test on a disposable VM, container, or throwaway test account/file **before** running against production systems or real user accounts.
3. **`delete_user.py --remove-home` permanently deletes the user's entire home directory.** Double-check the username before confirming — there is no recovery.
4. **`change_password.py`** will overwrite an existing password immediately. If run without `--password`, it prompts securely (hidden input) — never pass real passwords as plain command-line arguments on a shared or logged system if you can avoid it.
5. **`modify_file_permissions.py --recursive` and `change_file_ownership.py --recursive`** apply to every file and subdirectory under the given path. Double-check the path — running this on the wrong directory (e.g. `/` or `/home`) could make a system unusable or expose sensitive files.
6. **`manage_acl.py` requires the `acl` package installed at the OS level** (provides `setfacl`/`getfacl`) — this is a system package, not a Python package. See installation notes below.
7. **`modify_user.py` is Linux-only.** Windows account modification (shell/groups/expiry equivalents) varies too much to wrap generically — use `net user <name> /expires:date` and similar commands directly for Windows.
8. **`change_file_ownership.py` and `manage_acl.py` are Linux/macOS (POSIX) only** — `os.chown` and POSIX ACLs don't exist in the same form on Windows.

---

## 📦 Requirements

- **Python 3.9+** installed on your system.
- Check your version:
  ```bash
  python3 --version
  ```
- **All scripts use only Python's standard library** — there is nothing to `pip install` for the Python side. `requirements.txt` is included for consistency with the rest of the repository but installs no packages.
- Several scripts wrap **OS-level command-line tools** that must already exist on your system:
  - `useradd`, `userdel`, `usermod`, `chpasswd`, `chage`, `groupadd`, `groupdel`, `gpasswd` — pre-installed on virtually all Linux distributions.
  - `setfacl` / `getfacl` — **not** installed by default on most systems; install via:
    ```bash
    # Debian/Ubuntu
    sudo apt install acl

    # RHEL/CentOS/Fedora
    sudo yum install acl
    ```
  - On Windows: the built-in `net user` command (no install needed).

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aw-junaid/Python-System-Administration.git
   cd "Python-System-Administration/modules/User & Permission Management/scripts"
   ```

2. **(Optional) Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   > This installs nothing (no external Python packages are needed) but confirms your environment is set up correctly.

4. **Run any script** (most need `sudo` on Linux/macOS):
   ```bash
   sudo python3 script_name.py --help
   ```
   This shows the exact arguments each script expects.

---

## 🗂 Full List of Scripts, Usage & Expected Output

Below, `python3` is used for Linux/macOS. On Windows, use `python` instead (and run as Administrator where noted).

### 231. `create_user.py` — Create Users
**Platform:** Linux (`useradd`) and Windows (`net user`) · **Requires:** root/sudo or Administrator
```bash
sudo python3 create_user.py johndoe --create-home --shell /bin/bash
sudo python3 create_user.py johndoe --create-home --password MyPass123
```
**Expected output:** `User 'johndoe' created successfully.` (and `Password set successfully.` if `--password` was given). Verify with `id johndoe` (Linux) or `net user johndoe` (Windows).

---

### 232. `delete_user.py` — Delete Users
**Platform:** Linux (`userdel`) and Windows (`net user /delete`) · **Requires:** root/sudo or Administrator
```bash
sudo python3 delete_user.py johndoe --remove-home
sudo python3 delete_user.py johndoe --remove-home --force
```
**Expected output:** Confirmation prompt (unless `--force`), then `User 'johndoe' deleted successfully.` plus `Home directory removed.` if `--remove-home` was used.
**Caution:** On Windows, the user's profile folder is **not** automatically removed — delete `C:\Users\<username>` manually if needed.

---

### 233. `modify_user.py` — Modify Users
**Platform:** Linux only (`usermod`) · **Requires:** root/sudo
```bash
sudo python3 modify_user.py johndoe --shell /bin/zsh
sudo python3 modify_user.py johndoe --groups sudo,docker --append-groups
sudo python3 modify_user.py johndoe --expiry 2027-01-01
```
**Expected output:** `User 'johndoe' modified successfully.` Verify shell/groups with `getent passwd johndoe` / `groups johndoe`, and expiry with `chage -l johndoe`.

---

### 234. `change_password.py` — Change Passwords
**Platform:** Linux (`chpasswd`) and Windows (`net user`) · **Requires:** root/sudo or Administrator
```bash
sudo python3 change_password.py johndoe --password NewSecurePass123
sudo python3 change_password.py johndoe --force-change-at-login
```
**Expected output:** `Password for 'johndoe' changed successfully.` If `--password` is omitted, you're prompted securely (hidden input, with confirmation). `--force-change-at-login` (Linux only) also requires the user to set a new password on their next login.

---

### 235. `manage_groups.py` — Manage Groups
**Platform:** Linux only · **Requires:** root/sudo for create/delete/add-user/remove-user
```bash
sudo python3 manage_groups.py create developers
sudo python3 manage_groups.py add-user johndoe developers
sudo python3 manage_groups.py remove-user johndoe developers
sudo python3 manage_groups.py delete developers
python3 manage_groups.py list --user johndoe
python3 manage_groups.py list
```
**Expected output:** Confirmation message per action (e.g. `Group 'developers' created successfully.`). `list --user` shows one user's groups; `list` alone shows every group on the system with its members (no root needed to view).

---

### 236. `check_file_permissions.py` — Check File Permissions
**Platform:** Linux/macOS (full owner/group name resolution); works on Windows with limited owner/group info
```bash
python3 check_file_permissions.py /etc/passwd
python3 check_file_permissions.py ./myscript.sh
```
**Expected output:** Octal mode (e.g. `0755`), symbolic form (e.g. `-rwxr-xr-x`), owner/group names and IDs, size, and a readable breakdown of owner/group/other read-write-execute bits. No root required — read-only.

---

### 237. `modify_file_permissions.py` — Modify File Permissions
**Platform:** Linux/macOS (full support); Windows has a much smaller effective permission model
```bash
python3 modify_file_permissions.py myscript.sh 755
python3 modify_file_permissions.py ./project 644 --recursive
```
**Expected output:** `Permissions set to 0755 on N item(s).` Applies to a single file/directory, or recursively to every file and subdirectory with `--recursive`.
**Caution:** Double-check the path before using `--recursive` — it touches everything underneath.

---

### 238. `change_file_ownership.py` — Change File Ownership
**Platform:** Linux/macOS only (`os.chown`) · **Requires:** root/sudo to assign ownership to another user
```bash
sudo python3 change_file_ownership.py /var/www/html --owner www-data --group www-data --recursive
sudo python3 change_file_ownership.py myfile.txt --owner 1000
```
**Expected output:** `Ownership updated on N item(s).` Accepts either usernames/group names or numeric UID/GID. Verify with `ls -l` or `check_file_permissions.py`.

---

### 239. `manage_acl.py` — Manage Access Control Lists (ACLs)
**Platform:** Linux only (POSIX ACLs, via `setfacl`/`getfacl`) · **Requires:** the `acl` OS package installed; root/sudo for files you don't own
```bash
python3 manage_acl.py view myfile.txt
sudo python3 manage_acl.py set myfile.txt --entity user:johndoe:rw-
sudo python3 manage_acl.py set /shared/project --entity group:developers:rwx --recursive
sudo python3 manage_acl.py remove myfile.txt --entity user:johndoe
sudo python3 manage_acl.py remove-all myfile.txt
```
**Expected output:**
- `view`: full `getfacl`-style listing of every ACL entry on the path.
- `set`: confirms the entry was added, then re-displays the ACL so you can verify.
- `remove`: removes one specific entry (format: `user:NAME` or `group:NAME`, no permission suffix).
- `remove-all`: strips all extended ACL entries, leaving standard Unix owner/group/other permissions untouched.

If you see `command not found: setfacl`, install the `acl` package first (see Requirements above).

---

## 🧪 Quick Test Workflow

To safely try these scripts without touching real accounts (run in a disposable VM/container as root):

```bash
sudo python3 create_user.py testuser --create-home
sudo python3 change_password.py testuser --password TempPass123
sudo python3 manage_groups.py create testgroup
sudo python3 manage_groups.py add-user testuser testgroup
python3 manage_groups.py list --user testuser
echo "sample" > /tmp/sample.txt
python3 check_file_permissions.py /tmp/sample.txt
python3 modify_file_permissions.py /tmp/sample.txt 640
sudo python3 change_file_ownership.py /tmp/sample.txt --owner testuser --group testgroup
sudo python3 delete_user.py testuser --remove-home --force
sudo python3 manage_groups.py delete testgroup
```

---

## 📄 License / Usage Notes

- These scripts are provided for educational and administrative automation purposes.
- Always review a script's code before running it against real user accounts, production servers, or shared systems.
- The author is not responsible for data loss, account lockouts, or permission issues resulting from misuse — especially with `--remove-home`, `--recursive`, and password-reset operations.
