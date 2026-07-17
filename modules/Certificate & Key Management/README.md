# Certificate & Key Management Scripts

Automation scripts for X.509 certificate lifecycle management, SSH/GPG key
handling, and PKI operations. Each topic is implemented as its own
standalone Python script — no shared modules, no numbered filenames.


---

## ⚠️ Read This Before You Run Anything

- **This is real cryptographic tooling, not a toy.** Scripts that generate
  CAs, sign certificates, revoke certificates, or rotate encryption keys
  operate on files that your systems may come to trust. A mistake here can
  lock you out of a server, invalidate a production certificate chain, or
  expose a private key.
- **Test in a scratch directory / VM first.** Every example below uses
  throwaway filenames (`cert.pem`, `key.pem`, `pki/`, etc.) — run them in an
  empty folder you don't mind cleaning up until you're comfortable with the
  output.
- **Self-signed certificates (`self_signed_cert.py`) are not trusted by
  browsers or OSes.** They're for internal/dev/test use only. For a
  publicly trusted certificate, use `generate_csr.py` + a real CA, or
  `letsencrypt_manager.py`.
- **Private keys are sensitive.** Scripts write key files with `chmod 600`
  where possible, but you are responsible for where those files end up
  (don't commit them to git, don't email them, don't leave them in
  world-readable directories).
- **`letsencrypt_manager.py` talks to Let's Encrypt's real infrastructure**
  (or its staging environment with `--dry-run`). Let's Encrypt enforces
  [rate limits](https://letsencrypt.org/docs/rate-limits/) — always use
  `--dry-run` while testing so you don't get temporarily blocked from
  issuing real certificates for your domain.
- **`build_internal_pki.py` creates a Root CA key.** In a real deployment,
  the Root CA key should be generated offline, on an air-gapped machine,
  and stored offline/in an HSM — not left on a general-purpose server. This
  script is meant to teach/prototype the PKI hierarchy, not to replace
  proper offline root CA ceremony practices.
- **You must have explicit authorization** to generate certificates for any
  domain you don't own, to run a CA for infrastructure you don't control,
  or to manage keys on any system you don't administer.

---

## Prerequisites

### 1. Python

Python 3.9+ is recommended (the `cryptography` library's certificate APIs
and `datetime` timezone-aware attributes used here work best on modern
Python 3 versions).

### 2. Python packages

From inside the `Certificate & Key Management` folder:

```bash
pip install -r requirements.txt
```

This installs:

| Package | Used by |
|---|---|
| `cryptography` | Nearly every script — X.509, CSR, CRL, SSH keys, Fernet encryption |
| `python-gnupg` | `manage_gpg_keys.py`, `sign_file_gpg.py`, `verify_gpg_signature.py`, `distribute_public_keys.py` (gpg-keyserver mode) |
| `requests` | `monitor_cert_expiry.py` (webhook alerts), `distribute_public_keys.py` (http mode) |
| `hvac` | `secure_key_storage.py` (Vault backend only — optional) |

### 3. System (non-Python) binaries

A few scripts wrap external command-line tools that **pip cannot install**.
Install these separately, only if you plan to use the corresponding script:

| Script | Needs | Install (Ubuntu/Debian) | Install (macOS) |
|---|---|---|---|
| `manage_gpg_keys.py`, `sign_file_gpg.py`, `verify_gpg_signature.py`, `distribute_public_keys.py` (gpg mode) | `gpg` (GnuPG) | `sudo apt install gnupg` | `brew install gnupg` |
| `letsencrypt_manager.py` | `certbot` | `sudo apt install certbot` | `brew install certbot` |
| `convert_ssh_key_format.py` (PPK output only) | `puttygen` | `sudo apt install putty-tools` | `brew install putty` |

If a required binary is missing, each script detects this and prints an
install hint instead of crashing with a confusing traceback.

---

## Directory Layout

```
Certificate & Key Management/
├── README.md
├── requirements.txt
└── scripts/
    ├── self_signed_cert.py
    ├── generate_csr.py
    ├── sign_certificate.py
    ├── convert_cert_format.py
    ├── extract_cert_info.py
    ├── check_cert_expiration.py
    ├── monitor_cert_expiry.py
    ├── renew_certificate.py
    ├── letsencrypt_manager.py
    ├── generate_ssh_keypair.py
    ├── convert_ssh_key_format.py
    ├── manage_gpg_keys.py
    ├── sign_file_gpg.py
    ├── verify_gpg_signature.py
    ├── rotate_encryption_keys.py
    ├── secure_key_storage.py
    ├── revoke_certificate.py
    ├── build_internal_pki.py
    └── distribute_public_keys.py
```

All scripts are standalone — you can copy any single one out of `scripts/`
and run it on its own (aside from the shared pip packages above). Run any
script with `-h` / `--help` to see its full option list.

---

## Script Reference

### `self_signed_cert.py` — Generate Self-Signed Certificates
Creates an X.509 certificate signed with its own private key. For internal
testing/dev environments only.

```bash
python3 scripts/self_signed_cert.py --cn dev.local --days 365 --out-cert cert.pem --out-key key.pem
```
**Expected output:** `cert.pem` and `key.pem` written to disk; console
confirms the validity window. Browsers will show this as "not trusted" —
that's expected for a self-signed cert.

---

### `generate_csr.py` — Create Certificate Signing Requests (CSR)
Generates a private key and a CSR to submit to a public or internal CA.

```bash
python3 scripts/generate_csr.py --cn www.example.com --san www.example.com --san example.com \
    --out-csr request.csr --out-key request.key
```
**Expected output:** `request.key` (keep private) and `request.csr` (send
to your CA). Nothing is trusted yet — the CSR only becomes a usable
certificate once a CA signs it.

---

### `sign_certificate.py` — Sign Certificates with a CA
Acts as an internal CA: signs a CSR using a CA cert/key pair (see
`build_internal_pki.py` to create one) and issues a signed certificate.

```bash
python3 scripts/sign_certificate.py --csr request.csr --ca-cert pki/intermediate_ca.pem \
    --ca-key pki/intermediate_ca.key --days 365 --out signed_cert.pem
```
**Expected output:** `signed_cert.pem`, trusted only by systems that already
trust your CA chain (`pki/chain.pem`).

---

### `convert_cert_format.py` — Convert Certificate Formats (PEM, DER, PFX)
Converts between PEM, DER, and PKCS#12 (PFX/P12).

```bash
python3 scripts/convert_cert_format.py --in cert.pem --in-form PEM --out cert.der --out-form DER
python3 scripts/convert_cert_format.py --in cert.pem --in-form PEM --out bundle.pfx --out-form PFX \
    --key key.pem --pfx-password changeit
```
**Expected output:** A converted file in the target format. PFX output
requires `--key`; reading a PFX requires `--pfx-password` if it's
encrypted.

---

### `extract_cert_info.py` — Extract Certificate Information
Parses a cert and prints subject, issuer, validity window, and
fingerprints.

```bash
python3 scripts/extract_cert_info.py --cert cert.pem --json
```
**Expected output:** Either a human-readable summary or a JSON object with
`subject`, `issuer`, `serial_number`, `not_valid_before/after`, and SHA1/256
fingerprints.

---

### `check_cert_expiration.py` — Check Certificate Expiration Dates
One-shot check of a local cert file or a live TLS endpoint's certificate.
Designed for cron/monitoring pipelines via its exit codes.

```bash
python3 scripts/check_cert_expiration.py --host example.com --port 443 --warn-days 30
```
**Expected output:** Console summary of days remaining. Exit code `0`
(fine), `1` (within warning window), `2` (expired), `3` (couldn't check).

---

### `monitor_cert_expiry.py` — Monitor Certificates for Expiry
Extends the check above across multiple certs/hosts, optionally on a
repeating interval, with webhook or email notification when something is
close to expiring.

```bash
python3 scripts/monitor_cert_expiry.py --host example.com:443 --host example.org:443 \
    --warn-days 14 --interval 3600 --webhook https://hooks.example.com/notify
```
**Expected output:** Continuous console log every `--interval` seconds; a
webhook POST or email is sent only when a cert crosses into the warning or
expired state. Omit `--interval` (or leave it 0) for a single run, e.g. from
cron.

---

### `renew_certificate.py` — Automate Certificate Renewal
Checks remaining validity on an existing cert and, if within the renewal
threshold, either re-signs a fresh self-signed cert (same key) or produces
a new CSR for CA renewal.

```bash
python3 scripts/renew_certificate.py --cert cert.pem --key key.pem --mode self-signed \
    --renew-days 30 --valid-days 365
```
**Expected output:** If the cert has more than 30 days left, the script
reports "renewal not needed yet" and does nothing (use `--force` to
override). Otherwise it writes a renewed cert (or CSR).

---

### `letsencrypt_manager.py` — Manage Let's Encrypt Certificates
Wraps the `certbot` CLI to obtain/renew free, publicly trusted certificates
via ACME. **Requires `certbot` installed separately** (see Prerequisites) —
this script does not reimplement ACME.

```bash
# Always test with --dry-run first to avoid hitting real rate limits
python3 scripts/letsencrypt_manager.py obtain --domain example.com \
    --email admin@example.com --method standalone --dry-run

python3 scripts/letsencrypt_manager.py renew
```
**Expected output:** Real certbot output streamed to your console. On
success (non-dry-run), certificates land under
`/etc/letsencrypt/live/<domain>/` (standard certbot location) — this
requires root/sudo and port 80/443 availability for the `standalone`
method.

---

### `generate_ssh_keypair.py` — Generate SSH Key Pairs
Creates RSA, ECDSA, or Ed25519 SSH key pairs in OpenSSH format.

```bash
python3 scripts/generate_ssh_keypair.py --type ed25519 --out-private id_ed25519 \
    --out-public id_ed25519.pub --comment "you@yourhost"
```
**Expected output:** `id_ed25519` (chmod 600) and `id_ed25519.pub`, ready to
add to a server's `~/.ssh/authorized_keys` or your Git hosting provider.

---

### `convert_ssh_key_format.py` — Convert SSH Key Formats
Converts SSH private keys between OpenSSH and PEM (PKCS8); PPK (PuTTY)
output requires the external `puttygen` tool.

```bash
python3 scripts/convert_ssh_key_format.py --in id_ed25519 --in-form OpenSSH \
    --out id_ed25519.pem --out-form PEM
```
**Expected output:** A converted private key file. If you request `PPK`
output without `puttygen` installed, the script tells you exactly what to
install instead of failing silently.

---

### `manage_gpg_keys.py` — Manage GPG Keys
Generate, list, export, import, and revoke GPG keys. **Requires GnuPG
(`gpg`) installed on the system.**

```bash
python3 scripts/manage_gpg_keys.py generate --name "Alice" --email alice@example.com --passphrase "changeit"
python3 scripts/manage_gpg_keys.py list
python3 scripts/manage_gpg_keys.py export --fingerprint <FPR> --out alice_pub.asc
```
**Expected output:** Console-printed fingerprint on generation; an
ASCII-armored `.asc` key file on export; a revocation certificate on
`revoke`.

---

### `sign_file_gpg.py` — Sign Files with GPG
Creates a detached signature or a clearsigned document for a file, proving
authorship/integrity. Requires a secret key already in your keyring.

```bash
python3 scripts/sign_file_gpg.py --file report.txt --fingerprint <FPR> \
    --passphrase "changeit" --detach --out report.txt.sig
```
**Expected output:** `report.txt.sig` (or a clearsigned `.asc` file), which
recipients can check with `verify_gpg_signature.py`.

---

### `verify_gpg_signature.py` — Verify GPG Signatures
Confirms a signed file hasn't been tampered with and matches a trusted key.

```bash
python3 scripts/verify_gpg_signature.py --file report.txt --sig report.txt.sig
```
**Expected output:** "Signature is VALID" plus signer/key details, exit
code 0; or "INVALID/could not be verified" with exit code 1 if the
signature doesn't match or the signer's key isn't in your keyring.

---

### `rotate_encryption_keys.py` — Rotate Encryption Keys
Manages a symmetric (Fernet) key-rotation policy: generate an initial key,
then periodically rotate it, re-encrypting any files under `--data-dir` and
archiving the previous key.

```bash
python3 scripts/rotate_encryption_keys.py init --keystore keys/
python3 scripts/rotate_encryption_keys.py rotate --keystore keys/ --data-dir encrypted_data/
```
**Expected output:** `keys/current.key` (active key) and
`keys/archive/<timestamp>.key` (previous key retained for recovery); files
in `--data-dir` are re-encrypted in place under the new key.

---

### `secure_key_storage.py` — Secure Private Key Storage
Stores/retrieves private keys either in a password-protected local
encrypted keystore, or in HashiCorp Vault (if `hvac` is installed and a
Vault server is reachable).

```bash
python3 scripts/secure_key_storage.py store --backend local --keystore store.enc \
    --key-file id_rsa --password "changeit" --name my-server-key

python3 scripts/secure_key_storage.py retrieve --backend local --keystore store.enc \
    --password "changeit" --name my-server-key --out id_rsa_recovered
```
**Expected output:** `store.enc`, an encrypted file you can safely back up;
`retrieve` decrypts and writes the named key back out (chmod 600). The
Vault backend instead writes/reads secrets from a running Vault instance —
you must supply `--vault-addr`/`--vault-token` or set `VAULT_ADDR`/
`VAULT_TOKEN`.

---

### `revoke_certificate.py` — Revoke Compromised Certificates
Builds/extends a signed Certificate Revocation List (CRL) for your internal
CA.

```bash
python3 scripts/revoke_certificate.py --ca-cert pki/intermediate_ca.pem \
    --ca-key pki/intermediate_ca.key --revoke-cert compromised_cert.pem \
    --reason keyCompromise --crl-out crl.pem
```
**Expected output:** `crl.pem`, listing the revoked serial number plus any
previously revoked certs (pass the old CRL via `--crl-in` to extend it).
Distribute this CRL to anything that validates certs issued by this CA.

---

### `build_internal_pki.py` — Build Internal PKI Infrastructure
Creates a two-tier PKI: a self-signed Root CA and an Intermediate CA signed
by the Root — the standard structure for enterprise internal PKI.

```bash
python3 scripts/build_internal_pki.py --org "My Company" \
    --root-cn "My Company Root CA" --intermediate-cn "My Company Intermediate CA" \
    --out-dir pki/
```
**Expected output:** `pki/root_ca.{key,pem}`, `pki/intermediate_ca.{key,pem}`,
and `pki/chain.pem`. Use the intermediate with `sign_certificate.py` to
issue end-entity certs; keep `root_ca.key` offline in any real deployment.

---

### `distribute_public_keys.py` — Distribute Public Keys Securely
Publishes a public key (SSH `.pub`, GPG, or a certificate) to a shared
trusted directory, an internal HTTP endpoint, or a public GPG keyserver.

```bash
python3 scripts/distribute_public_keys.py local --file id_ed25519.pub --dest-dir /shared/trusted_keys/
python3 scripts/distribute_public_keys.py gpg-keyserver --fingerprint <FPR> --keyserver hkps://keys.openpgp.org
```
**Expected output:** Confirmation of where the key was published, plus a
SHA256 hash for the `local` mode so recipients can verify it out-of-band
before trusting it.

---

## General Notes

- Every script uses `argparse`; run any of them with `-h` to see the full,
  authoritative option list — this README shows the common cases, not
  every flag.
- Every script exits non-zero on failure and prints a `[!] Error: ...`
  message to stderr, so they chain cleanly into cron jobs or CI pipelines.
- None of these scripts phone home or transmit your keys/certs anywhere
  except where you explicitly point them (a webhook URL, an HTTP upload
  endpoint, a keyserver, or a Vault instance you configure).
