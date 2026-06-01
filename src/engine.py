#!/usr/bin/env python3
"""ServiceNow xMatters Escalation Bridge — core engine for ServiceNow REST API interaction and report generation.

Copyright (C) 2026  Vladimir Kapustin
SPDX-License-Identifier: AGPL-3.0-only
"""
import json, sys, requests
from typing import List, Dict

class Engine:
    """Core engine that fetches ServiceNow table data, processes records, and generates reports."""

    def __init__(self, sn_url: str, sn_user: str, sn_pass: str):
        self.sn_url = sn_url.rstrip("/")
        self.sn_auth = (sn_user, sn_pass)

    def fetch(self, table: str, limit: int = 100) -> List[Dict]:
        """Fetch records from a ServiceNow table via REST API.

        Args:
            table: ServiceNow table name (e.g., 'incident', 'change_request')
            limit: Maximum records to fetch (sysparm_limit parameter)

        Returns:
            List of record dicts. Returns empty list on any error.
        """
        url = f"{self.sn_url}/api/now/table/{table}"
        try:
            r = requests.get(url, params={"sysparm_limit": limit}, auth=self.sn_auth,
                           headers={"Accept": "application/json"}, timeout=30)
            r.raise_for_status()
            return r.json().get("result", [])
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error fetching {table}: {e.response.status_code}", file=sys.stderr)
            return []
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching {table}: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Unexpected error fetching {table}: {e}", file=sys.stderr)
            return []

    def process(self, records: List[Dict]) -> Dict:
        """Process fetched records into a summary dict.

        Args:
            records: List of record dicts from ServiceNow API

        Returns:
            Dict with 'total' (full count) and 'items' (capped at 50)
        """
        return {"total": len(records), "items": records[:50]}

    def report(self, data: Dict, prefix: str) -> Dict:
        """Generate JSON and Markdown reports from processed data.

        Args:
            data: Processed data dict from process()
            prefix: File path prefix for output files

        Returns:
            The input data dict (for chaining)
        """
        with open(f"{prefix}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        items = data.get("items", [])
        lines = [
            "# ServiceNow xMatters Escalation Report",
            f"**Total records:** {data['total']}",
            f"**Shown:** {len(items)}",
            "",
            "## Items",
        ]
        for idx, item in enumerate(items):
            label = item.get("name") or item.get("sys_id") or item.get("number") or f"Record {idx + 1}"
            lines.append(f"- {label}")
        with open(f"{prefix}.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return data

    def run(self, table: str, prefix: str) -> Dict:
        """Full pipeline: fetch → process → report.

        Args:
            table: ServiceNow table name
            prefix: Output file prefix

        Returns:
            Processed data dict
        """
        recs = self.fetch(table)
        data = self.process(recs)
        return self.report(data, prefix)
