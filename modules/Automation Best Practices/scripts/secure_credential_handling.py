#!/usr/bin/env python3
"""
secure_credential_handling.py

Demonstrates SECURE credential handling: never hardcoding secrets in
source code, loading them from environment variables (optionally via
a local, git-ignored .env file for development), masking secrets in
any logged/printed output, and failing fast with a clear error if a
required secret is missing — instead of silently using a fallback
that hides a misconfiguration.

Usage:
    python secure_credential_handling.py
    # or, with a real value set in your shell:
    export API_TOKEN="s3cr3t-value-123"
    python secure_credential_handling.py

Expected output:
    If no .env file and no environment variables are set, the script
    prints a clear, actionable error explaining exactly which
    environment variable to set, and exits non-zero (it does NOT fall
    back to a hardcoded secret). If a .env.example-based .env file (or
    real env vars) are present, it prints a masked version of the
    credential (e.g. "s3cr...123") to prove it loaded correctly,
    never the raw value.
"""

import os
import sys

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False


REQUIRED_SECRETS = ["API_TOKEN", "DB_PASSWORD"]


# ---------------------------------------------------------------------------
# ANTI-PATTERN (never do this):
#
#   API_TOKEN = "sk_live_51Hxxxxxxxxxxxxxxxxxxxxxxxx"   # <-- hardcoded secret,
#                                                          leaks via git history,
#                                                          screen shares, logs.
#
# GOOD PATTERN: load from the environment (itself populated by a real
# secrets manager / vault in production, or a local .env file that is
# in .gitignore for development).
# ---------------------------------------------------------------------------


def mask_secret(value: str, keep=4) -> str:
    """Return a masked version of a secret, safe to print/log."""
    if value is None:
        return "<not set>"
    if len(value) <= keep * 2:
        return "*" * len(value)
    return f"{value[:keep]}{'*' * (len(value) - keep * 2)}{value[-keep:]}"


def load_environment():
    """Load a local .env file for development, if python-dotenv is available."""
    if HAS_DOTENV:
        loaded = load_dotenv()  # loads variables from ./.env into os.environ, if present
        if loaded:
            print("Loaded local .env file for development.")
    else:
        print("(Tip: install python-dotenv to auto-load a local .env file: pip install python-dotenv)")


def get_required_secret(name: str) -> str:
    """
    Fetch a required secret from the environment. Fails fast and loudly
    if it's missing, rather than silently defaulting to a placeholder
    or an insecure fallback value.
    """
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(
            f"Required secret '{name}' is not set. "
            f"Set it as an environment variable (or in a local .env file "
            f"that is listed in .gitignore) before running this script. "
            f"In production, this should come from your secrets manager "
            f"or vault (e.g. AWS Secrets Manager, HashiCorp Vault, Azure Key Vault)."
        )
    return value


def connect_to_service(api_token: str, db_password: str):
    """Simulates using credentials, logging only masked versions."""
    print(f"Connecting with API_TOKEN={mask_secret(api_token)}  DB_PASSWORD={mask_secret(db_password)}")
    print("(In a real script, the raw values would be used here to authenticate, "
          "but NEVER printed, logged, or committed to source control.)")


def main():
    load_environment()

    print()
    print("Secure Credential Handling Demo")
    print("=" * 45)

    missing = [name for name in REQUIRED_SECRETS if not os.environ.get(name)]
    if missing:
        print(f"ERROR: missing required secret(s): {', '.join(missing)}")
        print()
        print("To try this script with real values, either:")
        print("  1) Export them in your shell:")
        for name in missing:
            print(f'       export {name}="your-value-here"')
        print("  2) Or create a local '.env' file (add it to .gitignore!) containing:")
        for name in missing:
            print(f"       {name}=your-value-here")
        sys.exit(1)

    api_token = get_required_secret("API_TOKEN")
    db_password = get_required_secret("DB_PASSWORD")

    connect_to_service(api_token, db_password)
    print()
    print("Done. Notice the raw secret values were never printed above — only masked previews.")


if __name__ == "__main__":
    main()
