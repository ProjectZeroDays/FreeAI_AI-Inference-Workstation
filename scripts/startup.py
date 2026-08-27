#!/usr/bin/env python3
"""Startup orchestrator for FreeAI Unified AI Stack.

Loads config/services.json and starts all services marked auto_start=true,
respecting dependency order. On Windows uses subprocess; on Linux also
wires up systemd-compatible behavior.

Usage:
    python scripts/startup.py              # start all critical+high services
    python scripts/startup.py --all        # start every service
    python scripts/startup.py --priority high  # start high-priority only
    python scripts/startup.py --stop all   # stop all managed services
    python scripts/startup.py --dry-run    # show what would start
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
SERVICES_CFG = CONFIG_DIR / "services.json"
RUNS_DIR = ROOT / ".runs"
RUNS_DIR.mkdir(exist_ok=True)
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def load_services():
    with open(SERVICES_CFG) as f:
        return json.load(f)


def pid_file(name):
    return RUNS_DIR / f"{name}.pid"


def get_pid(name):
    pf = pid_file(name)
    if not pf.exists():
        return None
    try:
        return int(pf.read_text().strip())
    except (ValueError, OSError):
        return None


def is_running(pid):
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def resolve_module_path(svc, cfg):
    mod = svc.get("module")
    if not mod:
        return None
    parts = mod.split(".")
    # Walk up from ROOT to find the top-level package
    candidates = [
        ROOT / Path(*parts) / (parts[-1] + ".py"),  # exact path from root
        ROOT / (mod.replace(".", "/") + ".py"),       # flat replacement
    ]
    # Also try dashboard/backend style
    flat = ROOT / mod.replace(".", "/") / (parts[-1] + ".py")
    candidates.append(flat)
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def start_service(name, svc, cfg, wait=True):
    port = svc["port"]
    pid = get_pid(name)
    if is_running(pid):
        print(f"  [already] {name} (:{port}) PID={pid}")
        return True

    module_path = resolve_module_path(svc, cfg)
    launcher = svc.get("launcher")

    env = os.environ.copy()
    env["FREEAI_SERVICE"] = name
    env["FREEAI_PORT"] = str(port)

    if launcher:
        cmd = [sys.executable, str(ROOT / launcher)]
    elif module_path:
        cmd = [sys.executable, module_path]
    else:
        print(f"  [skip]   {name} (:{port}) — no module or launcher found")
        return False

    log_path = LOGS_DIR / f"{name}.log"
    print(f"  [start]  {name} (:{port}) → {log_path}")
    try:
        with open(log_path, "a") as lf:
            proc = subprocess.Popen(
                cmd,
                cwd=str(ROOT),
                env=env,
                stdout=lf,
                stderr=subprocess.STDOUT,
            )
        pid_file(name).write_text(str(proc.pid))
        if wait:
            for _ in range(30):
                time.sleep(0.5)
                s = None
                try:
                    import socket
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    if s.connect_ex(("127.0.0.1", port)) == 0:
                        print(f"  [ready]  {name} (:{port}) PID={proc.pid}")
                        return True
                finally:
                    if s:
                        s.close()
            print(f"  [warn]   {name} started (PID {proc.pid}) but port not open yet")
            return True
        return True
    except Exception as exc:
        print(f"  [fail]   {name} (:{port}): {exc}")
        return False


def stop_service(name, svc, force=False):
    pid = get_pid(name)
    if not is_running(pid):
        print(f"  [stop]   {name} — not running")
        pid_file(name).unlink(missing_ok=True)
        return True
    try:
        sig = signal.SIGKILL if force else signal.SIGTERM
        os.kill(pid, sig)
        pid_file(name).unlink(missing_ok=True)
        print(f"  [stop]   {name} (:{svc['port']}) PID={pid}")
        return True
    except Exception as exc:
        print(f"  [fail]   {name}: {exc}")
        return False


def dependency_order(services_cfg):
    """Topological sort so dependencies start before dependents."""
    by_name = {n: s for n, s in services_cfg["services"].items()}
    visited = set()
    order = []

    def dfs(name):
        if name in visited:
            return
        visited.add(name)
        for dep in by_name[name].get("dependencies", []):
            if dep in by_name:
                dfs(dep)
        order.append(name)

    for name in by_name:
        dfs(name)
    return order


def main():
    parser = argparse.ArgumentParser(description="FreeAI Startup Orchestrator")
    parser.add_argument("--all", action="store_true", help="Start every service")
    parser.add_argument("--priority", choices=["critical", "high", "medium", "low"],
                        help="Start only services of given priority")
    parser.add_argument("--stop", nargs="?", const="all",
                        help="Stop a service or all services")
    parser.add_argument("--force", action="store_true", help="Force-kill on stop")
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for port open")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--service", nargs="?", help="Start a single service by name")
    args = parser.parse_args()

    cfg = load_services()
    services = cfg["services"]

    if args.stop:
        targets = [args.stop] if args.stop != "all" else list(services.keys())
        for name in targets:
            if name in services:
                stop_service(name, services[name], force=args.force)
        return

    if args.dry_run:
        print("=== Dry Run ===")
        for name in dependency_order(cfg):
            svc = services[name]
            gate = svc.get("env_gate")
            if gate and not os.environ.get(gate):
                print(f"  [skip]   {name} (:{svc['port']}) env gate '{gate}' not set")
                continue
            module = resolve_module_path(svc, cfg)
            launcher = svc.get("launcher")
            status = "module" if module else ("launcher" if launcher else "MISSING")
            auto = "auto" if svc.get("auto_start") or args.all else "manual"
            print(f"  [{auto:5s}] {name} (:{svc['port']}) [{svc['priority']}] status={status}")
        return

    if args.service:
        name = args.service
        if name not in services:
            print(f"Unknown service: {name}")
            sys.exit(1)
        svc = services[name]
        gate = svc.get("env_gate")
        if gate and not os.environ.get(gate):
            print(f"Service {name} requires env var {gate}=1")
            sys.exit(1)
        ok = start_service(name, svc, cfg, wait=not args.no_wait)
        sys.exit(0 if ok else 1)

    # Determine which services to start
    if args.priority:
        targets = [n for n, s in services.items() if s.get("priority") == args.priority]
    elif args.all:
        targets = list(services.keys())
    else:
        targets = [n for n, s in services.items()
                   if s.get("auto_start") and s.get("priority") in ("critical", "high")]

    # Filter out env-gated services missing their gate
    filtered = []
    for name in dependency_order(cfg):
        if name not in targets:
            continue
        svc = services[name]
        gate = svc.get("env_gate")
        if gate and not os.environ.get(gate):
            print(f"  [skip]   {name} (:{svc['port']}) env gate '{gate}' not set")
            continue
        filtered.append(name)

    print(f"\nStarting {len(filtered)} services...\n")
    failures = []
    for name in filtered:
        svc = services[name]
        ok = start_service(name, svc, cfg, wait=not args.no_wait)
        if not ok:
            failures.append(name)

    print(f"\n{'='*50}")
    if failures:
        print(f"FAILED: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("All requested services started.")
    print(f"{'='*50}\n")
    print("Tip: python scripts/startup.py --stop all   # stop everything")
    print("     python scripts/check_health.py          # full health report")


if __name__ == "__main__":
    main()
