#!/usr/bin/env python3
"""
sign_file_gpg.py - Digitally sign a file using a GPG key (detached or clearsign).

Requires: GnuPG installed on the system and a secret key already available
in your keyring (see manage_gpg_keys.py to generate one).

Usage:
    python3 sign_file_gpg.py --file report.txt --fingerprint ABCD1234 \
        --passphrase mypassphrase --detach --out report.txt.sig

    python3 sign_file_gpg.py --file report.txt --fingerprint ABCD1234 \
        --passphrase mypassphrase --clearsign --out report.txt.asc

Output:
    A detached signature (.sig) or clear-signed file (.asc).
"""
import argparse
import sys

import gnupg


def main():
    parser = argparse.ArgumentParser(description="Sign a file with GPG.")
    parser.add_argument("--file", required=True, help="File to sign")
    parser.add_argument("--fingerprint", required=True, help="Signing key fingerprint or key ID")
    parser.add_argument("--passphrase", required=True)
    parser.add_argument("--gnupghome", default=None)
    parser.add_argument("--out", required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--detach", action="store_true", help="Create a detached signature (default)")
    mode.add_argument("--clearsign", action="store_true", help="Create a clear-signed document")
    args = parser.parse_args()

    gpg = gnupg.GPG(gnupghome=args.gnupghome) if args.gnupghome else gnupg.GPG()

    try:
        with open(args.file, "rb") as f:
            if args.clearsign:
                signed = gpg.sign_file(
                    f, keyid=args.fingerprint, passphrase=args.passphrase, clearsign=True
                )
            else:
                signed = gpg.sign_file(
                    f, keyid=args.fingerprint, passphrase=args.passphrase, detach=True
                )

        if not signed.data:
            print("[!] Signing failed. Check the fingerprint/passphrase and that the key is present.",
                  file=sys.stderr)
            sys.exit(1)

        with open(args.out, "wb") as f:
            f.write(signed.data)

        print(f"[+] Signature written to: {args.out}")

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
