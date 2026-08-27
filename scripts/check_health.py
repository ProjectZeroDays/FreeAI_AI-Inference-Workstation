#!/usr/bin/env python3
"""CLI health checker for FreeAI Unified AI Stack.

Reads config/services.json and probes every registered service port.
Reports status, latency, and dependency health in a compact table.

Usage:
    python scripts/check_health.py                 # full check
    python scripts/check_health.py --json           # machine-readable output
    python scripts/check_health.py --service proxy  # single service
    python scripts/check_health.py --watch          # continuous monitoring (30s interval)
    python scripts/check_health.py --summary        # one-line pass/fail
"""
import argparse
import json
import socket
import sys
import time
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding for UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
SERVICES_CFG = CONFIG_DIR / "services.json"


def load_services():
    with open(SERVICES_CFG) as f:
        return json.load(f)


def probe_port(host, port, timeout=2.0):
    """Return (reachable: bool, latency_ms: float|None)."""
    start = time.monotonic()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        latency = (time.monotonic() - start) * 1000
        s.close()
        return result == 0, latency
    except Exception:
        return False, None


def probe_http(url, timeout=3.0):
    """Simple HTTP health probe (no external deps)."""
    start = time.monotonic()
    try:
        import http.client
        conn = http.client.HTTPConnection(url.hostname, url.path.lstrip("/").split("/")[0] if "/" in url.path else 80, timeout=timeout)
        # Use raw socket approach instead
        import urllib.request
        req = urllib.request.Request(url, method="GET")
        resp = urllib.request.urlopen(req, timeout=timeout)
        latency = (time.monotonic() - start) * 1000
        return True, latency, resp.status
    except Exception:
        return False, None, None


def parse_url(url_str):
    try:
        from urllib.parse import urlparse
        return urlparse(url_str)
    except Exception:
        return None


def check_service(name, svc):
    port = svc["port"]
    host = "127.0.0.1"
    reachable, latency = probe_port(host, port)
    health_path = svc.get("health_path")
    http_ok = None
    http_status = None

    if reachable and health_path:
        url = f"http://{host}:{port}{health_path}"
        http_ok, _, http_status = probe_http(url)

    status = "UP" if reachable else "DOWN"
    detail = f"{latency:.0f}ms" if latency is not None else "—"
    if http_ok:
        detail += f" HTTP {http_status}"

    return {
        "name": name,
        "port": port,
        "status": status,
        "latency_ms": latency,
        "http_ok": http_ok,
        "http_status": http_status,
        "detail": detail,
        "priority": svc.get("priority", "unknown"),
    }


def render_table(results, compact=False):
    sep = "─" * 62
    lines = [
        "",
        f"  FreeAI Health Check  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        sep,
        f"  {'Service':<22s} {'Port':>6s} {'Prior':<8s} {'Status':>6s}  Detail",
        sep,
    ]
    up_count = sum(1 for r in results if r["status"] == "UP")
    total = len(results)

    # Sort: UP first, then by priority order
    prio_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    results_sorted = sorted(results, key=lambda r: (prio_order.get(r["priority"], 9), r["name"]))

    for r in results_sorted:
        icon = "✓" if r["status"] == "UP" else "✗"
        name_display = f"{icon} {r['name']}" if not compact else r["name"]
        lines.append(
            f"  {name_display:<22s} :{r['port']:>5d}  {r['priority']:<8s} {r['status']:>6s}  {r['detail']}"
        )

    lines.append(sep)
    lines.append(f"  {up_count}/{total} services UP"
                 + (f"  ● {'ALL CLEAR' if up_count == total else '⚠ DEGRADED'}"
                    if not compact else ""))
    lines.append("")
    return "\n".join(lines)


def render_json(results):
    print(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "up": sum(1 for r in results if r["status"] == "UP"),
        "down": sum(1 for r in results if r["status"] == "DOWN"),
        "services": results,
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(description="FreeAI Health Checker")
    parser.add_argument("--json", action="store_true", dest="json_out", help="JSON output")
    parser.add_argument("--service", metavar="NAME", help="Check single service")
    parser.add_argument("--watch", action="store_true", help="Continuous monitor (30s)")
    parser.add_argument("--summary", action="store_true", help="One-line summary")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval in seconds")
    args = parser.parse_args()

    cfg = load_services()
    services = cfg["services"]

    if args.service:
        if args.service not in services:
            print(f"Unknown service: {args.service}")
            print(f"Available: {', '.join(sorted(services.keys()))}")
            sys.exit(1)
        results = [check_service(args.service, services[args.service])]
    else:
        results = [check_service(name, svc) for name, svc in services.items()]

    if args.summary:
        up = sum(1 for r in results if r["status"] == "UP")
        down = [r["name"] for r in results if r["status"] == "DOWN"]
        if down:
            print(f"DEGRADED — {up}/{len(results)} UP, down: {', '.join(down)}")
            sys.exit(1)
        else:
            print(f"ALL CLEAR — {up}/{len(results)} services UP")
            sys.exit(0)

    if args.json_out:
        render_json(results)
    else:
        print(render_table(results))

    down = [r for r in results if r["status"] == "DOWN"]
    if down and not args.watch:
        print("Tip: python scripts/startup.py --priority critical  # restart downed critical services")

    if args.watch:
        try:
            while True:
                time.sleep(args.interval)
                if args.service:
                    results = [check_service(args.service, services[args.service])]
                else:
                    results = [check_service(name, svc) for name, svc in services.items()]
                print("\033[H\033[J", end="")  # clear screen
                print(render_table(results))
        except KeyboardInterrupt:
            print("\n[watch] Stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()
