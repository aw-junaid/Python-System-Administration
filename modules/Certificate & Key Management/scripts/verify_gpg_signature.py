#!/usr/bin/env python3
"""
verify_gpg_signature.py - Verify a GPG signature (detached or clearsigned)
against the original file to confirm authenticity and integrity.

Usage:
    # Detached signature
    python3 verify_gpg_signature.py --file report.txt --sig report.txt.sig

    # Clearsigned file (signature + content combined)
    python3 verify_gpg_signature.py --clearsigned report.txt.asc

Output:
    Prints whether the signature is valid, the signer's key ID, and trust level.
    Exit code 0 = valid signature, 1 = invalid/unverifiable.
"""
import argparse
import sys

import gnupg


def main():
    parser = argparse.ArgumentParser(description="Verify a GPG signature.")
    parser.add_argument("--file", help="Original file (required for detached signatures)")
    parser.add_argument("--sig", help="Detached signature file")
    parser.add_argument("--clearsigned", help="Clear-signed file containing both content and signature")
    parser.add_argument("--gnupghome", default=None)
    args = parser.parse_args()

    if not args.clearsigned and not (args.file and args.sig):
        print("[!] Provide either --clearsigned FILE, or both --file and --sig", file=sys.stderr)
        sys.exit(1)

    gpg = gnupg.GPG(gnupghome=args.gnupghome) if args.gnupghome else gnupg.GPG()

    try:
        if args.clearsigned:
            with open(args.clearsigned, "rb") as f:
                verified = gpg.verify_file(f)
        else:
            with open(args.sig, "rb") as f:
                verified = gpg.verify_file(f, args.file)

        if verified.valid:
            print("[+] Signature is VALID")
            print(f"    Signed by  : {verified.username}")
            print(f"    Key ID     : {verified.key_id}")
            print(f"    Fingerprint: {verified.fingerprint}")
            print(f"    Trust level: {verified.trust_text}")
            sys.exit(0)
        else:
            print("[!] Signature is INVALID or could not be verified.", file=sys.stderr)
            print(f"    Status: {verified.status}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
