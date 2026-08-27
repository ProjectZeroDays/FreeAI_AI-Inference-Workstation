#!/usr/bin/env python3
"""CLI health checker for FreeAI Unified AI Stack.

Reads config/services.json and probes every registered service port.
Reports status, latency, dependency health, GPU, disk, and memory.

Usage:
    python scripts/check_health.py                 # full check
    python scripts/check_health.py --json           # machine-readable output
    python scripts/check_health.py --service proxy  # single service
    python scripts/check_health.py --watch          # continuous monitoring (30s interval)
    python scripts/check_health.py --summary        # one-line pass/fail
    python scripts/check_health.py --deps           # show dependency graph
"""
import argparse
import json
import os
import socket
import subprocess
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
ALERTS_CFG = CONFIG_DIR / "alerts.json"
DISK_WARN_PCT = 85.0
MEM_WARN_PCT = 85.0


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
        "dependencies": svc.get("dependencies", []),
    }


def get_gpu_info():
    """Query nvidia-smi for GPU health data."""
    result = {
        "available": False,
        "devices": [],
        "total_vram_mb": 0,
        "used_vram_mb": 0,
        "utilization_pct": 0,
        "temperature_c": 0,
        "power_w": 0,
        "clocks": {},
    }
    try:
        r = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=name,memory.total,memory.used,memory.free,"
             "utilization.gpu,temperature.cores,power.draw,power.limit,"
             "clocks.current.graphics,clocks.max.graphics",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode != 0:
            return result
        devices = []
        for line in r.stdout.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 10:
                continue
            total_mb = int(parts[1]) * 1024 if parts[1] else 0
            used_mb = int(parts[2]) * 1024 if parts[2] else 0
            free_mb = int(parts[3]) * 1024 if parts[3] else 0
            util = int(parts[4].replace("%", "")) if parts[4] else 0
            temp = int(parts[5]) if parts[5] else 0
            power = float(parts[6]) if parts[6] else 0
            power_limit = float(parts[7]) if parts[7] else 0
            cur_clock = parts[8].strip() if len(parts) > 8 else "—"
            max_clock = parts[9].strip() if len(parts) > 9 else "—"
            devices.append({
                "name": parts[0],
                "total_vram_mb": total_mb,
                "used_vram_mb": used_mb,
                "free_vram_mb": free_mb,
                "utilization_pct": util,
                "temperature_c": temp,
                "power_w": power,
                "power_limit_w": power_limit,
                "clock_current_mhz": cur_clock,
                "clock_max_mhz": max_clock,
            })
        if devices:
            result.update({
                "available": True,
                "devices": devices,
                "total_vram_mb": sum(d["total_vram_mb"] for d in devices),
                "used_vram_mb": sum(d["used_vram_mb"] for d in devices),
                "utilization_pct": max(d["utilization_pct"] for d in devices),
                "temperature_c": max(d["temperature_c"] for d in devices),
                "power_w": sum(d["power_w"] for d in devices),
                "clocks": {
                    "current": devices[0].get("clock_current_mhz", "—"),
                    "max": devices[0].get("clock_max_mhz", "—"),
                },
            })
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return result


def get_disk_info():
    """Return disk usage for the main partition as a dict."""
    try:
        if sys.platform == "win32":
            import psutil
            c = psutil.disk_usage("C:\\")
            return {
                "total_gb": round(c.total / 1e9, 1),
                "used_gb": round(c.used / 1e9, 1),
                "free_gb": round(c.free / 1e9, 1),
                "percent": c.percent,
                "warning": c.percent >= DISK_WARN_PCT,
            }
        else:
            r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
            lines = r.stdout.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                return {
                    "total_gb": parts[1],
                    "used_gb": parts[2],
                    "free_gb": parts[3],
                    "percent": int(parts[4].replace("%", "")),
                    "warning": int(parts[4].replace("%", "")) >= DISK_WARN_PCT,
                }
    except Exception:
        pass
    return {"error": "unavailable"}


def get_memory_info():
    """Return system memory usage."""
    try:
        import psutil
        m = psutil.virtual_memory()
        return {
            "total_gb": round(m.total / 1e9, 1),
            "used_gb": round(m.used / 1e9, 1),
            "free_gb": round(m.free / 1e9, 1),
            "available_gb": round(m.available / 1e9, 1),
            "percent": m.percent,
            "warning": m.percent >= MEM_WARN_PCT,
        }
    except Exception:
        pass
    return {"error": "unavailable (install psutil)"}


def build_dep_graph(services_cfg):
    """Build a dependency map: {service: [deps]} plus reverse deps."""
    svcs = services_cfg.get("services", {})
    forward = {}
    reverse = {}
    for name, svc in svcs.items():
        deps = svc.get("dependencies", [])
        forward[name] = deps
        if name not in reverse:
            reverse[name] = []
        for dep in deps:
            reverse.setdefault(dep, []).append(name)
    return {"forward": forward, "reverse": reverse}


def render_table(results, gpu, disk, memory, compact=False):
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

    # GPU section
    lines.append("")
    lines.append("  GPU")
    lines.append("  " + "─" * 40)
    if gpu.get("available"):
        for d in gpu["devices"]:
            lines.append(f"  {d['name']:<28s} Temp: {d['temperature_c']}°C  "
                         f"Power: {d['power_w']:.0f}W/{d['power_limit_w']:.0f}W  "
                         f"Clock: {d['clock_current_mhz']}  "
                         f"VRAM: {d['used_vram_mb']//1024}/{d['total_vram_mb']//1024}GB")
        lines.append(f"  {'Overall':<28s} Util: {gpu['utilization_pct']}%  "
                     f"Temp: {gpu['temperature_c']}°C  Power: {gpu['power_w']:.0f}W")
    else:
        lines.append("  nvidia-smi not available")

    # System resources
    lines.append("")
    lines.append("  System Resources")
    lines.append("  " + "─" * 40)
    if "error" not in memory:
        lines.append(f"  Memory: {memory['used_gb']}GB / {memory['total_gb']}GB  "
                     f"({memory['percent']}%)  {'⚠ HIGH' if memory['warning'] else '✓'}")
    else:
        lines.append(f"  Memory: unavailable")
    if "error" not in disk:
        lines.append(f"  Disk:   {disk['used_gb']}GB / {disk['total_gb']}GB  "
                     f"({disk['percent']}%)  {'⚠ HIGH' if disk['warning'] else '✓'}")
    else:
        lines.append(f"  Disk: unavailable")
    lines.append("")
    return "\n".join(lines)


def render_json(results, gpu, disk, memory, dep_graph):
    print(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "up": sum(1 for r in results if r["status"] == "UP"),
            "down": sum(1 for r in results if r["status"] == "DOWN"),
            "status": "ok" if all(r["status"] == "UP" for r in results) else "degraded",
        },
        "services": results,
        "gpu": gpu,
        "disk": disk,
        "memory": memory,
        "dependencies": dep_graph,
    }, indent=2))


def render_deps(dep_graph):
    lines = ["", "  Service Dependency Graph", "  " + "─" * 50, ""]
    for svc, deps in sorted(dep_graph["forward"].items()):
        if deps:
            lines.append(f"  {svc}  →  {', '.join(deps)}")
        else:
            lines.append(f"  {svc}  →  (none)")
    lines.append("")
    lines.append("  Reverse (who depends on me):")
    lines.append("  " + "─" * 50)
    for svc, rev in sorted(dep_graph["reverse"].items()):
        if rev:
            lines.append(f"  {svc}  ←  {', '.join(rev)}")
        else:
            lines.append(f"  {svc}  ←  (nobody)")
    lines.append("")
    return "\n".join(lines)


def check_and_alert(results):
    """Log alerts for any DOWN services to config/alerts.json."""
    down = [r for r in results if r["status"] == "DOWN"]
    if not down:
        return
    alerts = []
    if ALERTS_CFG.exists():
        try:
            alerts = json.loads(ALERTS_CFG.read_text())
        except (json.JSONDecodeError, OSError):
            alerts = []
    now = datetime.now().isoformat()
    for s in down:
        entry = {
            "ts": now,
            "service": s["name"],
            "port": s["port"],
            "level": "critical" if s["priority"] == "critical" else "warning",
            "message": f"Service '{s['name']}' on port {s['port']} is DOWN",
        }
        # Avoid duplicate alerts for the same service within 60s
        existing_keys = [(a.get("service"), a.get("ts")) for a in alerts]
        if not any(k[0] == s["name"] and abs(datetime.fromisoformat(k[1]).timestamp() - time.time()) < 60
                   for k in existing_keys if isinstance(k[1], str)):
            alerts.append(entry)
    # Keep only last 50 alerts
    alerts = alerts[-50:]
    ALERTS_CFG.parent.mkdir(parents=True, exist_ok=True)
    ALERTS_CFG.write_text(json.dumps(alerts, indent=2))
    for s in down:
        print(f"  ⚠ ALERT: {s['name']} (port {s['port']}) is DOWN — written to alerts.json")


def main():
    parser = argparse.ArgumentParser(description="FreeAI Health Checker")
    parser.add_argument("--json", action="store_true", dest="json_out", help="JSON output")
    parser.add_argument("--service", metavar="NAME", help="Check single service")
    parser.add_argument("--watch", action="store_true", help="Continuous monitor (30s)")
    parser.add_argument("--summary", action="store_true", help="One-line summary")
    parser.add_argument("--deps", action="store_true", help="Show dependency graph")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval in seconds")
    args = parser.parse_args()

    cfg = load_services()
    services = cfg["services"]
    dep_graph = build_dep_graph(cfg)

    if args.service:
        if args.service not in services:
            print(f"Unknown service: {args.service}")
            print(f"Available: {', '.join(sorted(services.keys()))}")
            sys.exit(1)
        results = [check_service(args.service, services[args.service])]
    else:
        results = [check_service(name, svc) for name, svc in services.items()]

    gpu = get_gpu_info()
    disk = get_disk_info()
    memory = get_memory_info()

    if args.summary:
        up = sum(1 for r in results if r["status"] == "UP")
        down = [r["name"] for r in results if r["status"] == "DOWN"]
        warnings = []
        if disk.get("warning"):
            warnings.append(f"disk {disk['percent']}%")
        if memory.get("warning"):
            warnings.append(f"memory {memory['percent']}%")
        if gpu.get("available") and gpu["temperature_c"] >= 85:
            warnings.append(f"gpu temp {gpu['temperature_c']}°C")
        parts = [f"{up}/{len(results)} services UP"]
        if down:
            parts.append(f"down: {', '.join(down)}")
        if warnings:
            parts.append(f"⚠ {', '.join(warnings)}")
        status = "ALL CLEAR" if not down and not warnings else "DEGRADED"
        print(f"{status} — {'; '.join(parts)}")
        sys.exit(0 if status == "ALL CLEAR" else 1)

    if args.deps:
        print(render_deps(dep_graph))
        return

    if args.json_out:
        render_json(results, gpu, disk, memory, dep_graph)
    else:
        print(render_table(results, gpu, disk, memory))
        check_and_alert(results)

    down = [r for r in results if r["status"] == "DOWN"]
    if down and not args.watch and not args.json_out:
        print("Tip: python scripts/startup.py --priority critical  # restart downed critical services")

    if args.watch:
        try:
            while True:
                time.sleep(args.interval)
                if args.service:
                    results = [check_service(args.service, services[args.service])]
                else:
                    results = [check_service(name, svc) for name, svc in services.items()]
                gpu = get_gpu_info()
                disk = get_disk_info()
                memory = get_memory_info()
                print("\033[H\033[J", end="")  # clear screen
                print(render_table(results, gpu, disk, memory))
        except KeyboardInterrupt:
            print("\n[watch] Stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()
