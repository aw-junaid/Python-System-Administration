#!/usr/bin/env python3
"""
audit_log.py
----------------
Generates structured audit log entries (who did what, when) in JSON
Lines format - one JSON object per line, easy to parse or feed into
log analysis tools like the ELK stack or Splunk.

Usage:
    python3 audit_log.py
"""

import json
import logging
import os
from datetime import datetime, timezone

LOG_DIR = "logs"
AUDIT_FILE = os.path.join(LOG_DIR, "audit.log")

os.makedirs(LOG_DIR, exist_ok=True)


class JsonLineFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "event": getattr(record, "event", "unspecified"),
            "user": getattr(record, "user", "unknown"),
            "details": record.getMessage(),
        }
        return json.dumps(entry)


logger = logging.getLogger("audit_log_demo")
logger.setLevel(logging.INFO)

handler = logging.FileHandler(AUDIT_FILE)
handler.setFormatter(JsonLineFormatter())
logger.addHandler(handler)


def audit(event, user, details=""):
    logger.info(details, extra={"event": event, "user": user})


def main():
    # Example audit trail entries
    audit(event="login", user="ahmad", details="User logged in from 192.168.1.10")
    audit(event="file_access", user="ahmad", details="Accessed /etc/passwd")
    audit(event="config_change", user="admin", details="Changed firewall rule: allow 443/tcp")
    audit(event="logout", user="ahmad", details="User logged out")

    print(f"Audit log entries written to: {AUDIT_FILE}")
    print("Each line is a standalone JSON object (JSON Lines format).")


if __name__ == "__main__":
    main()
