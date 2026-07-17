# Security & Authentication — Python Automation Scripts

This folder contains **16 standalone Python scripts**, each automating a single, specific security/authentication task (secure password input, hashing, encryption, SSH keys, API key management, certificate validation, file integrity, and more).

Every script:
- Is completely **independent** — you only need the one file for the task you want.
- Can be run directly from the command line.
- Uses `argparse`, so running it with `-h` shows help and usage.
- Prints clear success/error messages so you always know what happened.

> **Repository:** https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/Security%20%26%20Authentication/scripts

---

## ⚠️ Important Security Cautions Before You Start

1. **This is educational/utility tooling, not a production security product.** Review the code before using it to protect anything sensitive in a real environment.
2. **Never pass real passwords as plain command-line arguments** where avoidable (they can leak into shell history, process lists, and logs). Scripts that need a password to *read* prefer interactive `getpass` prompts; scripts that need a password as a *flag* (`--password`) do so because the workflow requires it (e.g. vault tools) — use with care, and consider clearing your shell history afterward (`history -c`) on shared machines.
3. **There is no "forgot password" option.** If you forget a vault master password or an encryption password, the data **cannot be recovered**. Anywhere.
4. **Vault files (`*.vault`, `*.salt`) and private SSH keys are sensitive.** Treat them like passwords themselves — don't commit them to git, don't share them, back them up securely.
5. **`generate_random_password.py` and `generate_secure_token.py` output values directly to your terminal.** Anyone who can see your screen or terminal history/logging can see them.
6. **Test on throwaway data first.** Especially for `encrypt_sensitive_data.py`/`decrypt_sensitive_data.py` and the vault scripts — make sure round-tripping works before relying on them for anything important.
7. These scripts are **not a replacement** for established, audited tools like a real password manager (Bitwarden, 1Password), `ssh-keygen`, `openssl`, or your OS's certificate store — they're for learning, automation, and small personal/admin use cases.

---

## 📦 Requirements

- **Python 3.9+** installed on your system.
- Check your version:
  ```bash
  python3 --version
  ```
- Some scripts use **only the Python standard library** (`getpass`, `hashlib`, `hmac`, `secrets`, `base64`, `json`, `os`) — nothing to install.
- Scripts that work with encryption, SSH keys, or certificates require the `cryptography` package, listed in `requirements.txt`.

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aw-junaid/Python-System-Administration.git
   cd "Python-System-Administration/modules/Security & Authentication/scripts"
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
   > Scripts 1–3, 4–7, 14–15 (see list below) work with zero installs. Install `cryptography` only if you plan to use the encryption/SSH/certificate/vault scripts.

4. **Run any script:**
   ```bash
   python3 script_name.py --help
   ```
   This shows the exact arguments each script expects.

---

## 🗂 Full List of Scripts, Usage & Expected Output

Below, `python3` is used for Linux/macOS. On Windows, use `python` instead.

### 1. `handle_password_input.py` — Handle Password Input Securely
```bash
python3 handle_password_input.py
```
**Expected output:** Prompts `Enter your password:` with input hidden from the terminal, then confirms `Password received successfully (N characters).` Nothing is stored or logged.

---

### 2. `use_getpass.py` — Use getpass
```bash
python3 use_getpass.py
```
**Expected output:** A visible `Username:` prompt and a hidden `Password:` prompt (via the `getpass` module), then a summary confirming the password length only.

---

### 3. `reprompt_password.py` — Reprompt for Password Input
```bash
python3 reprompt_password.py
python3 reprompt_password.py --confirm --min-length 10
```
**Expected output:** Repeatedly prompts until the password meets the rules (length, uppercase, digit) and, with `--confirm`, matches a second entry. Gives up after `--max-attempts` (default 3).

---

### 4. `hash_passwords.py` — Hash Passwords
```bash
python3 hash_passwords.py
```
**Expected output:** Prompts for a password (hidden), then prints a self-contained hash string:
```
pbkdf2_sha256$390000$<salt_base64>$<hash_base64>
```
Save this string — it's what you should store instead of the plain password.

---

### 5. `verify_password_hash.py` — Verify Password Hashes
```bash
python3 verify_password_hash.py "pbkdf2_sha256$390000$abc...$def..."
```
**Expected output:** Prompts for a password, then prints `Password is VALID` or `Password is INVALID` (exits with code 1 if invalid).

---

### 6. `generate_random_password.py` — Generate Random Passwords
```bash
python3 generate_random_password.py
python3 generate_random_password.py --length 20 --count 5
python3 generate_random_password.py --length 12 --no-symbols
```
**Expected output:** A numbered list of cryptographically secure random passwords, guaranteed to include lowercase, uppercase, and digits (and symbols unless `--no-symbols`).

---

### 7. `generate_secure_token.py` — Generate Secure Tokens
```bash
python3 generate_secure_token.py
python3 generate_secure_token.py --bytes 48 --format urlsafe
```
**Expected output:** A single random token string, useful for API keys, session tokens, or CSRF tokens. Format options: `hex`, `urlsafe`, `base64`.

---

### 8. `encrypt_sensitive_data.py` — Encrypt Sensitive Data
**Requires:** `pip install -r requirements.txt`
```bash
python3 encrypt_sensitive_data.py --text "my secret data" --password MyPass123
python3 encrypt_sensitive_data.py --file secrets.txt --password MyPass123
```
**Expected output:** Encrypted base64 text printed to screen, or (for `--file`) a new `secrets.txt.enc` file. Uses password-derived AES (Fernet) encryption.

---

### 9. `decrypt_sensitive_data.py` — Decrypt Sensitive Data
**Requires:** `pip install -r requirements.txt`
```bash
python3 decrypt_sensitive_data.py --file secrets.txt.enc --password MyPass123
```
**Expected output:** The original plaintext, either printed or written to a file. Wrong password → `Error: decryption failed.`

---

### 10. `generate_ssh_keys.py` — Generate SSH Keys
**Requires:** `pip install -r requirements.txt`
```bash
python3 generate_ssh_keys.py my_key
python3 generate_ssh_keys.py my_key --type rsa --bits 4096
```
**Expected output:** Two files: `my_key` (private, permissions set to `600`) and `my_key.pub` (public, in standard OpenSSH format ready for `authorized_keys`).
**Caution:** Never share or commit the private key file.

---

### 11. `read_ssh_keys.py` — Read SSH Keys
**Requires:** `pip install -r requirements.txt`
```bash
python3 read_ssh_keys.py my_key.pub
python3 read_ssh_keys.py my_key
```
**Expected output:** Key type (RSA/Ed25519), size (for RSA), and a SHA256 fingerprint. Private key material itself is **never printed**.

---

### 12. `manage_api_keys.py` — Manage API Keys
**Requires:** `pip install -r requirements.txt`
```bash
python3 manage_api_keys.py add openai sk-abc123 --password MyVaultPass
python3 manage_api_keys.py list --password MyVaultPass
python3 manage_api_keys.py get openai --password MyVaultPass
python3 manage_api_keys.py remove openai --password MyVaultPass
```
**Expected output:** Keys stored encrypted in a local `api_keys.vault` file (plus `api_keys.salt`) in the current directory. `list` shows names only; `get` reveals a value. Wrong password → error, vault does not open.
**Caution:** Back up `api_keys.vault` + `api_keys.salt` together — losing either makes the vault unrecoverable.

---

### 13. `validate_certificate.py` — Validate Certificates
**Requires:** `pip install -r requirements.txt`
```bash
python3 validate_certificate.py server.pem
```
**Expected output:** Subject, issuer, serial number, validity window, and a status line: `VALID (N days remaining)`, `EXPIRED`, or `NOT YET VALID`. Warns if expiring within 30 days.

---

### 14. `verify_file_integrity.py` — Verify File Integrity
```bash
python3 verify_file_integrity.py installer.exe a1b2c3...  --algo sha256
```
**Expected output:** Prints expected vs. actual hash, then `MATCH — file integrity verified.` or `MISMATCH — file may be corrupted or tampered with!` (exits with code 1 on mismatch).

---

### 15. `generate_checksums.py` — Generate Checksums
```bash
python3 generate_checksums.py installer.exe
python3 generate_checksums.py *.iso --algo sha512 --output checksums.txt
```
**Expected output:** A checksum per file printed to screen, and optionally saved to a checksum file (`--output`) for later verification.

---

### 16. `secure_credential_storage.py` — Secure Credential Storage
**Requires:** `pip install -r requirements.txt`
```bash
python3 secure_credential_storage.py add gmail myuser@gmail.com --password MyMasterPass
# (you'll be prompted to enter the credential's password securely)
python3 secure_credential_storage.py get gmail --password MyMasterPass
python3 secure_credential_storage.py list --password MyMasterPass
python3 secure_credential_storage.py remove gmail --password MyMasterPass
```
**Expected output:** Username/password pairs stored encrypted in a local `credentials.vault` file (plus `credentials.salt`). Same caution as `manage_api_keys.py` — back up both files together.

---

## 🧪 Quick Test Workflow

To safely try these scripts without touching real accounts or data:

```bash
mkdir test_area && cd test_area
python3 ../generate_random_password.py --length 16 --count 3
python3 ../generate_secure_token.py --bytes 24
echo "test data" > sample.txt
python3 ../generate_checksums.py sample.txt --algo sha256
python3 ../encrypt_sensitive_data.py --text "hello vault" --password TestPass1
python3 ../generate_ssh_keys.py test_key --type ed25519
python3 ../read_ssh_keys.py test_key.pub
```

---

## 📄 License / Usage Notes

- These scripts are provided for educational and administrative automation purposes.
- Always review a script's code before running it on important credentials, keys, or production data.
- The author is not responsible for data loss or exposure resulting from misuse — especially around lost passwords/keys, or of encrypted files without backups.
