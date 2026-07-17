#!/usr/bin/env python3
"""
convert_cert_format.py - Convert certificates/keys between PEM, DER, and PKCS#12 (PFX) formats.

Usage examples:
    # PEM -> DER
    python3 convert_cert_format.py --in cert.pem --in-form PEM --out cert.der --out-form DER

    # PEM -> PFX (bundling cert + key, optional chain)
    python3 convert_cert_format.py --in cert.pem --in-form PEM --out bundle.pfx --out-form PFX \
        --key key.pem --ca-chain chain.pem --pfx-password mypassword

    # PFX -> PEM
    python3 convert_cert_format.py --in bundle.pfx --in-form PFX --out cert.pem --out-form PEM \
        --pfx-password mypassword --out-key key.pem

Output:
    Certificate/key file(s) in the requested target format.
"""
import argparse
import sys

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12


def read_cert_any(path, form, password=None):
    with open(path, "rb") as f:
        data = f.read()
    if form == "PEM":
        return x509.load_pem_x509_certificate(data), None, []
    elif form == "DER":
        return x509.load_der_x509_certificate(data), None, []
    elif form == "PFX":
        key, cert, chain = pkcs12.load_key_and_certificates(
            data, password.encode() if password else None
        )
        return cert, key, chain or []
    raise ValueError(f"Unsupported input format: {form}")


def main():
    parser = argparse.ArgumentParser(description="Convert certificate formats (PEM/DER/PFX).")
    parser.add_argument("--in", dest="infile", required=True)
    parser.add_argument("--in-form", choices=["PEM", "DER", "PFX"], required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-form", choices=["PEM", "DER", "PFX"], required=True)
    parser.add_argument("--key", help="Private key file (PEM), needed to build a PFX")
    parser.add_argument("--ca-chain", help="PEM file with intermediate/root certs to include in PFX")
    parser.add_argument("--pfx-password", default=None, help="Password for reading/writing PFX")
    parser.add_argument("--out-key", help="Where to write extracted private key (PFX -> PEM/DER)")
    parser.add_argument("--friendly-name", default="cert", help="Friendly name for PFX bundle")
    args = parser.parse_args()

    try:
        cert, key, chain = read_cert_any(args.infile, args.in_form, args.pfx_password)

        if args.out_form == "PEM":
            with open(args.out, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            if key and args.out_key:
                with open(args.out_key, "wb") as f:
                    f.write(key.private_bytes(
                        serialization.Encoding.PEM,
                        serialization.PrivateFormat.TraditionalOpenSSL,
                        serialization.NoEncryption(),
                    ))

        elif args.out_form == "DER":
            with open(args.out, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.DER))
            if key and args.out_key:
                with open(args.out_key, "wb") as f:
                    f.write(key.private_bytes(
                        serialization.Encoding.DER,
                        serialization.PrivateFormat.PKCS8,
                        serialization.NoEncryption(),
                    ))

        elif args.out_form == "PFX":
            if not args.key:
                raise ValueError("--key is required when converting to PFX")
            with open(args.key, "rb") as f:
                priv_key = serialization.load_pem_private_key(f.read(), password=None)

            extra_certs = []
            if args.ca_chain:
                with open(args.ca_chain, "rb") as f:
                    chain_data = f.read()
                if hasattr(x509, "load_pem_x509_certificates"):
                    extra_certs = x509.load_pem_x509_certificates(chain_data)

            enc = (
                serialization.BestAvailableEncryption(args.pfx_password.encode())
                if args.pfx_password else serialization.NoEncryption()
            )
            pfx_bytes = pkcs12.serialize_key_and_certificates(
                name=args.friendly_name.encode(),
                key=priv_key,
                cert=cert,
                cas=extra_certs or None,
                encryption_algorithm=enc,
            )
            with open(args.out, "wb") as f:
                f.write(pfx_bytes)

        print(f"[+] Converted {args.in_form} -> {args.out_form}: {args.out}")

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
