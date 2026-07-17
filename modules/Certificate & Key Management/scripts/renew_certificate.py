#!/usr/bin/env python3
"""
renew_certificate.py - Check a certificate's remaining validity and, if it is
within a renewal threshold, generate a fresh self-signed certificate (reusing
the existing private key) or a new CSR for re-submission to a CA.

Usage:
    # Renew a self-signed cert in place if it expires within 30 days
    python3 renew_certificate.py --cert cert.pem --key key.pem --mode self-signed \
        --renew-days 30 --valid-days 365

    # Generate a fresh CSR for CA renewal if within threshold
    python3 renew_certificate.py --cert cert.pem --key key.pem --mode csr \
        --renew-days 30 --out-csr renewed.csr

Output:
    A renewed certificate (or CSR) only if the existing certificate is within
    the renewal window; otherwise reports that renewal is not yet needed.
"""
import argparse
import datetime
import sys

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization


def load_cert(path):
    with open(path, "rb") as f:
        return x509.load_pem_x509_certificate(f.read())


def load_key(path, password=None):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=password.encode() if password else None)


def days_remaining(cert):
    not_after = cert.not_valid_after_utc if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after
    now = datetime.datetime.now(datetime.timezone.utc) if hasattr(cert, "not_valid_after_utc") \
        else datetime.datetime.utcnow()
    return (not_after - now).days


def renew_self_signed(cert, key, valid_days, out_cert):
    now = datetime.datetime.utcnow()
    new_cert = (
        x509.CertificateBuilder()
        .subject_name(cert.subject)
        .issuer_name(cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=valid_days))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    with open(out_cert, "wb") as f:
        f.write(new_cert.public_bytes(serialization.Encoding.PEM))
    print(f"[+] Renewed self-signed certificate written to: {out_cert}")
    print(f"[+] New expiry: {now + datetime.timedelta(days=valid_days)}")


def renew_csr(cert, key, out_csr):
    builder = x509.CertificateSigningRequestBuilder().subject_name(cert.subject)
    csr = builder.sign(key, hashes.SHA256())
    with open(out_csr, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))
    print(f"[+] New CSR written to: {out_csr}")
    print("[*] Submit this CSR to your CA to obtain the renewed certificate.")


def main():
    parser = argparse.ArgumentParser(description="Renew a certificate before it expires.")
    parser.add_argument("--cert", required=True, help="Existing certificate file")
    parser.add_argument("--key", required=True, help="Existing private key file")
    parser.add_argument("--key-password", default=None)
    parser.add_argument("--mode", choices=["self-signed", "csr"], required=True)
    parser.add_argument("--renew-days", type=int, default=30, help="Renew if expiry is within N days")
    parser.add_argument("--valid-days", type=int, default=365, help="Validity period for the renewed cert")
    parser.add_argument("--out-cert", default="renewed_cert.pem")
    parser.add_argument("--out-csr", default="renewed.csr")
    parser.add_argument("--force", action="store_true", help="Renew regardless of remaining validity")
    args = parser.parse_args()

    try:
        cert = load_cert(args.cert)
        key = load_key(args.key, args.key_password)
        remaining = days_remaining(cert)
        print(f"[*] Current certificate expires in {remaining} days.")

        if remaining > args.renew_days and not args.force:
            print("[*] Renewal not needed yet. Use --force to renew anyway.")
            return

        if args.mode == "self-signed":
            renew_self_signed(cert, key, args.valid_days, args.out_cert)
        else:
            renew_csr(cert, key, args.out_csr)

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
