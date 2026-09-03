"""Unified service launcher for the AI development environment.

Starts all integrated services with a single command.
Services:
  - proxy            (:8100)  Unified LLM proxy (opencodex-style)
  - memory           (:8110)  Agent Zero persistent memory
  - agents           (:8120)  7 specialized agents (oh-my-opencode-slim)
  - registry         (:8130)  Plugin registry (awesome-opencode)
  - rag              (:8140)  RAG retrieval service
  - brain            (:8150)  AgentBrain three-tier router
  - skills           (:8160)  Skills API & auto-skill creation
  - pipeline         (:8170)  Workflow pipeline service
  - dashboard        (:8080)  Web UI (dashboard + skills manager)
  - autonomous       (:8050)  Autonomous operations engine
  - knightshade      (:8180)  Browser automation (Knight-Shade)
  - mcp_catalog      (:8190)  MCP server catalog API
  - unified_catalog  (:8195)  Skills+Plugins+MCPs+Providers catalog API
  - godmode          (:8196)  GODMODE uncensored agent mode + campaign

Usage:
    python launch.py                  # start all services
    python launch.py proxy           # start only proxy
    python launch.py --stop all      # stop all services
    python launch.py --status        # check running services
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
CONFIG_DIR = ROOT / "config"
PID_DIR = ROOT / ".runs"
PID_DIR.mkdir(exist_ok=True)

SERVICES = {
    "proxy":      {"port": 8100, "module": "proxy.proxy",                    "cmd": "python"},
    "memory":     {"port": 8110, "module": "memory.memory_api",              "cmd": "python"},
    "agents":     {"port": 8120, "module": "agents.specialized.agents_api",  "cmd": "python"},
    "registry":   {"port": 8130, "module": "plugins.registry.registry_api",  "cmd": "python"},
    "rag":        {"port": 8140, "module": "rag.service",                    "cmd": "python"},
    "brain":      {"port": 8150, "module": "brain.brain",                    "cmd": "python"},
    "skills":     {"port": 8160, "module": "skills.skills_api",              "cmd": "python"},
    "pipeline":   {"port": 8170, "module": "pipeline.api",                   "cmd": "python"},
    "dashboard":  {"port": 8080, "module": "dashboard.backend",              "cmd": "python"},
    "autonomous": {"port": 8050, "module": "autonomous.api", "launcher": "start_autonomous.py"},
    "knightshade": {"port": 8180, "module": "browser.api", "launcher": "start_browser.py"},
    "mcp_catalog": {"port": 8190, "module": "mcp.catalog_api",               "cmd": "python"},
    "unified_catalog": {"port": 8195, "module": "skills.catalog_api",        "cmd": "python"},
    "godmode":    {"port": 8196, "module": "agents.godmode",                  "cmd": "python"},
    "campaign":   {"port": 8192, "module": "agents.campaign_manager",         "cmd": "python"},
}


def get_pid(name):
    pid_file = PID_DIR / f"{name}.pid"
    if pid_file.exists():
        try:
            return int(pid_file.read_text().strip())
        except (ValueError, OSError):
            return None
    return None


def is_running(pid):
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def start_service(name):
    """Start a service by name."""
    svc = SERVICES.get(name)
    if not svc:
        print(f"[launch] Unknown service: {name}")
        return False

    pid = get_pid(name)
    if is_running(pid):
        print(f"[launch] {name} already running (PID {pid})")
        return True

    module_path = ROOT / (svc["module"].replace(".", "/") + ".py")
    if not module_path.exists():
        print(f"[launch] Module not found: {module_path}")
        return False

    env = os.environ.copy()
    env["PROXY_PORT"] = str(svc["port"])
    env["MEMORY_PORT"] = str(SERVICES.get("memory", {}).get("port", 8110))
    env["AGENTS_PORT"] = str(SERVICES.get("agents", {}).get("port", 8120))
    env["REGISTRY_PORT"] = str(SERVICES.get("registry", {}).get("port", 8130))
    env["RAG_PORT"] = str(svc["port"])
    env["GODMODE_PORT"] = str(SERVICES.get("godmode", {}).get("port", 8196))
    env["CAMPAIGN_PORT"] = str(SERVICES.get("campaign", {}).get("port", 8192))

    print(f"[launch] Starting {name} on :{svc['port']}...")
    try:
        # Use a launcher script for uvicorn-based services to avoid
        # the subprocess path-resolution issues on Windows
        if svc.get("launcher"):
            launcher = ROOT / svc["launcher"]
            cmd = [sys.executable, str(launcher)]
        else:
            module_path = ROOT / (svc["module"].replace(".", "/") + ".py")
            cmd = [sys.executable, str(module_path)]
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        pid_file = PID_DIR / f"{name}.pid"
        pid_file.write_text(str(proc.pid))
        # Wait for port to open
        import socket
        for _ in range(20):
            time.sleep(0.5)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if s.connect_ex(("127.0.0.1", svc["port"])) == 0:
                s.close()
                print(f"[launch] {name} ready on :{svc['port']} (PID {proc.pid})")
                return True
            s.close()
        print(f"[launch] {name} started but port not yet open")
        return True
    except Exception as exc:
        print(f"[launch] Failed to start {name}: {exc}")
        return False


def stop_service(name):
    """Stop a service by name."""
    pid = get_pid(name)
    if not is_running(pid):
        print(f"[launch] {name} not running")
        return True
    try:
        os.kill(pid, signal.SIGTERM)
        (PID_DIR / f"{name}.pid").unlink(missing_ok=True)
        print(f"[launch] Stopped {name} (PID {pid})")
        return True
    except Exception as exc:
        print(f"[launch] Failed to stop {name}: {exc}")
        return False


def status_all():
    """Show status of all services."""
    print("\n" + "=" * 55)
    print("  FreeAI Environment — Service Status")
    print("=" * 55)
    all_up = True
    for name, svc in SERVICES.items():
        pid = get_pid(name)
        running = is_running(pid)
        icon = "\u2713" if running else " "
        port_status = "UP" if running else "DOWN"
        print(f"  [{icon}] {name:10s} :{svc['port']}  {port_status}"
              + (f"  PID {pid}" if running else ""))
        if not running:
            all_up = False
    print("=" * 55)
    print(f"  {'All services running!' if all_up else 'Some services are down'}")
    print("=" * 55 + "\n")
    return all_up


def run_startup_gpu_warmup():
    """Run GPU warmup once after dashboard is up, if enabled in config."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gw_backend", ROOT / "dashboard" / "backend.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        result = mod.run_warmup_on_startup()
        if result and not result.get("skipped"):
            print(f"[launch] GPU warmup: {result.get('gpu_count', 0)} device(s) warmed")
        else:
            print(f"[launch] GPU warmup skipped: {result.get('reason', 'no GPU')}")
    except Exception as e:
        print(f"[launch] GPU warmup error (non-fatal): {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="FreeAI Service Launcher")
    parser.add_argument("service", nargs="?",
                        help="Service to start (proxy|memory|agents|registry|rag|brain|skills|pipeline|knightshade|godmode|campaign|all)")
    parser.add_argument("--stop", nargs="?", const="all",
                        help="Stop a service or all services")
    parser.add_argument("--status", action="store_true",
                        help="Show status of all services")
    parser.add_argument("--bg", action="store_true",
                        help="Start in background (daemon mode)")
    parser.add_argument("--no-warmup", action="store_true",
                        help="Skip GPU warmup on startup")
    args = parser.parse_args()

    if args.status:
        status_all()
        return

    if args.stop:
        targets = [args.stop] if args.stop != "all" else list(SERVICES.keys())
        for name in targets:
            stop_service(name)
        return

    # Start mode
    targets = [args.service] if args.service and args.service != "all" else list(SERVICES.keys())
    for name in targets:
        start_service(name)

    # GPU warmup (after dashboard is up)
    if not args.no_warmup and not args.bg:
        import time as _t
        _t.sleep(3)  # wait for dashboard to be ready
        run_startup_gpu_warmup()

    if not args.bg:
        print("\n[launch] All services started. Use --status to check.")
        print("[launch] Press Ctrl+C to stop all services.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[launch] Stopping all services...")
            for name in SERVICES:
                stop_service(name)
            print("[launch] Done.")


if __name__ == "__main__":
    main()
