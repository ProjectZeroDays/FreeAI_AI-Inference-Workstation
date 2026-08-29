#!/usr/bin/env python3
"""API Transaction Sniffer Agent — reverse-engineers API transactions and maps app schemes."""
import json
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent


class ApiSniffer:
    """Intercepts and analyzes API transactions via CDP Network domain."""

    def __init__(self, browser_engine=None):
        self.engine = browser_engine
        self.transactions = []
        self.mappings = {}

    def describe(self):
        return {
            "name": "api_sniffer",
            "description": "Reverse-engineers API transactions, maps app schemes via CDP Network domain",
            "category": "red_teaming",
            "capabilities": ["network_intercept", "scheme_mapping", "transaction_log"],
        }

    async def start_capture(self, target_url, headers=None):
        """Begin capturing API transactions from a target URL."""
        if not self.engine:
            return {"error": "No browser engine attached"}
        self.transactions = []
        self.mappings = {}
        result = await self.engine.navigate(target_url, extra_headers=headers)
        if result.get("ok"):
            return {"ok": True, "url": target_url, "transactions_captured": 0}
        return {"error": result.get("error", "navigation failed")}

    def get_transactions(self):
        """Return all captured API transactions."""
        return self.transactions

    def get_mappings(self):
        """Return API scheme mappings."""
        return self.mappings

    def add_transaction(self, method, url, status, timing_ms, size_bytes):
        """Record a single API transaction."""
        entry = {
            "ts": time.time(),
            "method": method,
            "url": url,
            "status": status,
            "timing_ms": timing_ms,
            "size_bytes": size_bytes,
        }
        self.transactions.append(entry)
        # Build scheme mapping
        parsed = _parse_url(url)
        if parsed:
            key = f"{method} {parsed['path']}"
            if key not in self.mappings:
                self.mappings[key] = {"auth_required": False, "params": [], "body_schema": None}
        return entry

    def stop_capture(self):
        """Stop capturing and return summary."""
        by_method = {}
        for t in self.transactions:
            by_method.setdefault(t["method"], []).append(t)
        summary = {
            "total": len(self.transactions),
            "by_method": {m: len(v) for m, v in by_method.items()},
            "mappings": self.mappings,
            "transactions": self.transactions[-100:],
        }
        self.transactions = []
        return summary


def _parse_url(url):
    try:
        from urllib.parse import urlparse
        p = urlparse(url)
        return {"scheme": p.scheme, "host": p.hostname, "path": p.path, "query": p.query}
    except Exception:
        return None


if __name__ == "__main__":
    agent = ApiSniffer()
    print(json.dumps(agent.describe(), indent=2))