#!/usr/bin/env python3
"""
convert_ssh_key_format.py - Convert SSH private keys between OpenSSH and PEM
(PKCS8) formats. PPK conversion (PuTTY format) requires the external
`puttygen` tool; this script will call it via subprocess if available.

Usage:
    # OpenSSH -> PEM
    python3 convert_ssh_key_format.py --in id_ed25519 --in-form OpenSSH \
        --out id_ed25519.pem --out-form PEM

    # PEM -> OpenSSH
    python3 convert_ssh_key_format.py --in key.pem --in-form PEM \
        --out id_key --out-form OpenSSH

    # OpenSSH -> PPK (requires puttygen installed)
    python3 convert_ssh_key_format.py --in id_rsa --in-form OpenSSH \
        --out id_rsa.ppk --out-form PPK

Output:
    Converted private key file in the requested format.
"""
import argparse
import shutil
import subprocess
import sys

from cryptography.hazmat.primitives import serialization


def load_key(path, passphrase):
    with open(path, "rb") as f:
        data = f.read()
    if data.strip().startswith(b"-----BEGIN OPENSSH"):
        return serialization.load_ssh_private_key(
            data, password=passphrase.encode() if passphrase else None
        )
    return serialization.load_pem_private_key(
        data, password=passphrase.encode() if passphrase else None
    )


def main():
    parser = argparse.ArgumentParser(description="Convert SSH key formats (OpenSSH / PEM / PPK).")
    parser.add_argument("--in", dest="infile", required=True)
    parser.add_argument("--in-form", choices=["OpenSSH", "PEM"], required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-form", choices=["OpenSSH", "PEM", "PPK"], required=True)
    parser.add_argument("--passphrase", default=None, help="Passphrase for reading an encrypted key")
    parser.add_argument("--out-passphrase", default=None, help="Passphrase to encrypt the output key")
    args = parser.parse_args()

    try:
        if args.out_form == "PPK":
            if shutil.which("puttygen") is None:
                print(
                    "[!] PPK conversion requires `puttygen` to be installed and on PATH.\n"
                    "    Ubuntu/Debian: sudo apt install putty-tools\n"
                    "    macOS (brew) : brew install putty",
                    file=sys.stderr,
                )
                sys.exit(1)
            cmd = ["puttygen", args.infile, "-o", args.out]
            print(f"[*] Running: {' '.join(cmd)}")
            result = subprocess.run(cmd)
            sys.exit(result.returncode)

        key = load_key(args.infile, args.passphrase)
        encryption = (
            serialization.BestAvailableEncryption(args.out_passphrase.encode())
            if args.out_passphrase else serialization.NoEncryption()
        )

        if args.out_form == "OpenSSH":
            out_bytes = key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.OpenSSH,
                encryption_algorithm=encryption,
            )
        else:  # PEM
            out_bytes = key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption,
            )

        with open(args.out, "wb") as f:
            f.write(out_bytes)

        print(f"[+] Converted {args.in_form} -> {args.out_form}: {args.out}")

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
