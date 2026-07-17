#!/usr/bin/env python3
"""
manage_gpg_keys.py - Generate, import, export, list, and revoke GPG keys
using the `gpg` executable (via python-gnupg).

Requires: GnuPG installed on the system (gpg binary on PATH).

Usage:
    python3 manage_gpg_keys.py generate --name "Alice" --email alice@example.com \
        --passphrase mypassphrase

    python3 manage_gpg_keys.py list
    python3 manage_gpg_keys.py export --fingerprint ABCD1234 --out alice_pub.asc
    python3 manage_gpg_keys.py export --fingerprint ABCD1234 --secret --out alice_priv.asc --passphrase mypassphrase
    python3 manage_gpg_keys.py import --file alice_pub.asc
    python3 manage_gpg_keys.py revoke --fingerprint ABCD1234 --out revoke.asc

Output:
    Console confirmation of the action; exported keys/revocation certificates
    are written to the requested file paths.
"""
import argparse
import sys

import gnupg


def get_gpg(home_dir=None):
    return gnupg.GPG(gnupghome=home_dir) if home_dir else gnupg.GPG()


def cmd_generate(args, gpg):
    input_data = gpg.gen_key_input(
        name_real=args.name,
        name_email=args.email,
        passphrase=args.passphrase,
        key_type="RSA",
        key_length=args.bits,
    )
    key = gpg.gen_key(input_data)
    if not key.fingerprint:
        print("[!] Key generation failed.", file=sys.stderr)
        sys.exit(1)
    print(f"[+] Generated key with fingerprint: {key.fingerprint}")


def cmd_list(args, gpg):
    keys = gpg.list_keys(secret=args.secret)
    for k in keys:
        uids = ", ".join(k.get("uids", []))
        print(f"{k['fingerprint']}  {uids}")


def cmd_export(args, gpg):
    if args.secret:
        data = gpg.export_keys(args.fingerprint, secret=True, passphrase=args.passphrase)
    else:
        data = gpg.export_keys(args.fingerprint)
    if not data:
        print("[!] Export produced no data - check the fingerprint/passphrase.", file=sys.stderr)
        sys.exit(1)
    with open(args.out, "w") as f:
        f.write(data)
    print(f"[+] Key exported to: {args.out}")


def cmd_import(args, gpg):
    with open(args.file, "r") as f:
        data = f.read()
    result = gpg.import_keys(data)
    print(f"[+] Imported {result.count} key(s). Fingerprints: {result.fingerprints}")


def cmd_revoke(args, gpg):
    result = gpg.gen_revoke(args.fingerprint)
    with open(args.out, "w") as f:
        f.write(str(result))
    print(f"[+] Revocation certificate written to: {args.out}")
    print("[*] Import this certificate into keyrings/keyservers to revoke the key.")


def main():
    parser = argparse.ArgumentParser(description="Manage GPG keys.")
    parser.add_argument("--gnupghome", default=None, help="Custom GNUPGHOME directory")
    sub = parser.add_subparsers(dest="action", required=True)

    p_gen = sub.add_parser("generate")
    p_gen.add_argument("--name", required=True)
    p_gen.add_argument("--email", required=True)
    p_gen.add_argument("--passphrase", required=True)
    p_gen.add_argument("--bits", type=int, default=3072)
    p_gen.set_defaults(func=cmd_generate)

    p_list = sub.add_parser("list")
    p_list.add_argument("--secret", action="store_true", help="List secret keys instead of public")
    p_list.set_defaults(func=cmd_list)

    p_exp = sub.add_parser("export")
    p_exp.add_argument("--fingerprint", required=True)
    p_exp.add_argument("--secret", action="store_true")
    p_exp.add_argument("--passphrase", default=None)
    p_exp.add_argument("--out", required=True)
    p_exp.set_defaults(func=cmd_export)

    p_imp = sub.add_parser("import")
    p_imp.add_argument("--file", required=True)
    p_imp.set_defaults(func=cmd_import)

    p_rev = sub.add_parser("revoke")
    p_rev.add_argument("--fingerprint", required=True)
    p_rev.add_argument("--out", default="revoke.asc")
    p_rev.set_defaults(func=cmd_revoke)

    args = parser.parse_args()
    gpg = get_gpg(args.gnupghome)

    try:
        args.func(args, gpg)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
