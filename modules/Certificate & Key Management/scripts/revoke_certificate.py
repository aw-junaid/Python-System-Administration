#!/usr/bin/env python3
"""
revoke_certificate.py - Maintain a Certificate Revocation List (CRL) for an
internal CA: add a certificate's serial number to the revoked set and issue
an updated, signed CRL.

Usage:
    python3 revoke_certificate.py --ca-cert ca.pem --ca-key ca.key \
        --revoke-cert compromised_cert.pem --crl-in crl.pem --crl-out crl.pem \
        --reason keyCompromise --next-update-days 7

    # First CRL for a CA (no existing --crl-in)
    python3 revoke_certificate.py --ca-cert ca.pem --ca-key ca.key \
        --revoke-serial 123456789 --crl-out crl.pem

Output:
    An updated PEM-encoded CRL listing all previously revoked certificates
    plus the newly revoked one.
"""
import argparse
import datetime
import sys

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization

REASON_MAP = {
    "unspecified": x509.ReasonFlags.unspecified,
    "keyCompromise": x509.ReasonFlags.key_compromise,
    "caCompromise": x509.ReasonFlags.ca_compromise,
    "affiliationChanged": x509.ReasonFlags.affiliation_changed,
    "superseded": x509.ReasonFlags.superseded,
    "cessationOfOperation": x509.ReasonFlags.cessation_of_operation,
    "certificateHold": x509.ReasonFlags.certificate_hold,
}


def main():
    parser = argparse.ArgumentParser(description="Revoke a certificate and issue an updated CRL.")
    parser.add_argument("--ca-cert", required=True)
    parser.add_argument("--ca-key", required=True)
    parser.add_argument("--ca-key-password", default=None)
    parser.add_argument("--revoke-cert", default=None, help="Certificate file to revoke")
    parser.add_argument("--revoke-serial", type=int, default=None, help="Serial number to revoke directly")
    parser.add_argument("--reason", choices=list(REASON_MAP.keys()), default="unspecified")
    parser.add_argument("--crl-in", default=None, help="Existing CRL to extend (optional)")
    parser.add_argument("--crl-out", required=True)
    parser.add_argument("--next-update-days", type=int, default=7)
    args = parser.parse_args()

    if not args.revoke_cert and not args.revoke_serial:
        print("[!] Provide either --revoke-cert or --revoke-serial", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.ca_cert, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
        with open(args.ca_key, "rb") as f:
            ca_key = serialization.load_pem_private_key(
                f.read(), password=args.ca_key_password.encode() if args.ca_key_password else None
            )

        if args.revoke_cert:
            with open(args.revoke_cert, "rb") as f:
                target_cert = x509.load_pem_x509_certificate(f.read())
            serial = target_cert.serial_number
        else:
            serial = args.revoke_serial

        now = datetime.datetime.utcnow()
        builder = x509.CertificateRevocationListBuilder().issuer_name(ca_cert.subject)
        builder = builder.last_update(now).next_update(now + datetime.timedelta(days=args.next_update_days))

        # Re-add existing revoked entries
        if args.crl_in:
            with open(args.crl_in, "rb") as f:
                existing_crl = x509.load_pem_x509_crl(f.read())
            for entry in existing_crl:
                builder = builder.add_revoked_certificate(entry)

        revoked = (
            x509.RevokedCertificateBuilder()
            .serial_number(serial)
            .revocation_date(now)
            .add_extension(
                x509.CRLReason(REASON_MAP[args.reason]), critical=False
            )
            .build()
        )
        builder = builder.add_revoked_certificate(revoked)

        crl = builder.sign(private_key=ca_key, algorithm=hashes.SHA256())

        with open(args.crl_out, "wb") as f:
            f.write(crl.public_bytes(serialization.Encoding.PEM))

        print(f"[+] Certificate with serial {serial} added to CRL")
        print(f"[+] Updated CRL written to: {args.crl_out}")
        print(f"[+] Next update due: {now + datetime.timedelta(days=args.next_update_days)}")

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
