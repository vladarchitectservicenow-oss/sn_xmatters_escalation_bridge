#!/usr/bin/env python3
# Copyright (C) 2026 Vladimir Kapustin
# SPDX-License-Identifier: AGPL-3.0-only
"""ServiceNow xMatters Escalation Bridge — CLI entry point."""
import argparse, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.engine import Engine

def resolve_password(raw: str) -> str:
    """Resolve password from env: prefix or literal value."""
    if raw.startswith("env:"):
        var = raw[4:]
        val = os.environ.get(var, "")
        if not val:
            print(f"Warning: environment variable {var} is empty or not set", file=sys.stderr)
        return val
    return raw

def main():
    p = argparse.ArgumentParser(
        description="ServiceNow xMatters Escalation Bridge — fetch ServiceNow table data and generate reports",
        epilog="""Examples:
  python3 src/cli.py --sn-url https://dev12345.service-now.com --sn-user admin --sn-pass env:SN_PASS
  python3 src/cli.py --sn-url https://dev12345.service-now.com --sn-user admin --sn-pass env:SN_PASS --table change_request
  python3 src/cli.py --sn-url https://dev12345.service-now.com --sn-user admin --sn-pass env:SN_PASS --output /tmp/escalation_report"""
    )
    p.add_argument("--sn-url", required=True, help="ServiceNow instance URL (e.g., https://dev12345.service-now.com)")
    p.add_argument("--sn-user", required=True, help="ServiceNow username for basic auth")
    p.add_argument("--sn-pass", required=True, help="ServiceNow password. Use env:VAR_NAME to read from environment variable")
    p.add_argument("--table", default="incident", help="ServiceNow table to fetch (default: incident)")
    p.add_argument("--output", default="report", help="Output file prefix for .json and .md reports (default: report)")
    args = p.parse_args()
    password = resolve_password(args.sn_pass)
    if not password:
        print("Error: no password provided (env variable empty or not set)", file=sys.stderr)
        return 1
    Engine(args.sn_url, args.sn_user, password).run(args.table, args.output)
    print("Report generated.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
