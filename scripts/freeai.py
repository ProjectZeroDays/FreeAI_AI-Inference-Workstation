#!/usr/bin/env python3
"""freeai-cli - control the FreeAI unified service stack from a shell.

Usage:
    freeai status                # show all service health
    freeai models                # list available models from the router
    freeai route "<prompt>"      # send a prompt through the router
    freeai workflows             # list registered workflows
    freeai run <workflow_id>     # execute a workflow
    freeai start                 # start all services via launch.py
    freeai stop                  # stop all services
    freeai logs <service>        # tail logs for a service

Environment:
    MOCK_LLM=1                  # local dev mode: route returns canned responses
    FREEAI_HOST                 # override base host (default: localhost)
"""
import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "services.json"
LAUNCH_PY = ROOT / "launch.py"
LOGS_DIR = ROOT / "logs"
RUNS_DIR = ROOT / ".runs"

BASE_HOST = os.environ.get("FREEAI_HOST", "localhost")
MOCK_MODE = os.environ.get("MOCK_LLM", "").lower() in ("1", "true", "yes")

# Canned responses for MOCK_LLM mode
MOCK_RESPONSES = {
    "default": "This is a mock response in MOCK_LLM dev mode. The router is not running.",
    "code": "Here is a Python implementation:\n\n```python\ndef hello():\n    return 'world'\n```\n\nThis satisfies the request in mock mode.",
    "analysis": "Mock analysis result: the request has been classified as a general task. In production this would return a real LLM analysis.",
    "full_project": "Mock full_project response: a complete project structure has been generated with architecture, code, and tests.",
}

MOCK_MODELS = {
    "qwen3.6-12b": {"name": "Qwen3.6 12B (mock)", "role": "primary_coder", "strengths": ["architecture", "full_project"], "endpoint": "mock"},
    "moe-13b":     {"name": "L3.1 MOE 2x8B (mock)", "role": "fast_coder", "strengths": ["refactor", "debug"], "endpoint": "mock"},
    "claude-code-9b": {"name": "CodeClawd 9B (mock)", "role": "code_specialist", "strengths": ["coding_agent", "refactor"], "endpoint": "mock"},
}


def load_services():
    """Load service definitions from config/services.json."""
    if not CONFIG_PATH.exists():
        print(f"error: config/services.json not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def _http(method, url, body=None, timeout=10):
    """Make an HTTP request and return (status_code, parsed_json_or_None)."""
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read().decode() or "{}")
        except Exception:
            return exc.code, None
    except urllib.error.URLError as exc:
        return 0, {"error": str(exc.reason)}
    except Exception as exc:
        return 0, {"error": "request failed"}


def _url(port, path="/"):
    return f"http://{BASE_HOST}:{port}{path}"


def cmd_status(args):
    """Show health of every service defined in config/services.json."""
    cfg = load_services()
    services = cfg.get("services", {})
    rows = sorted(services.items(), key=lambda kv: kv[1].get("port", 0))

    print()
    print("=" * 68)
    print("  FreeAI Service Health")
    print("=" * 68)
    print(f"  {'Service':<22s} {'Port':>6s}  {'Health':>8s}  Status")
    print("-" * 68)

    all_up = True
    for name, svc in rows:
        port = svc.get("port")
        health_path = svc.get("health_path", "/health")
        if port is None:
            state, detail = "N/A", "no port"
        else:
            code, body = _http("GET", _url(port, health_path))
            if code == 200:
                state = "healthy"
                extra = body.get("status", "") if isinstance(body, dict) else ""
                detail = f"  {extra}".strip()
            elif code == 0:
                state = "unreachable"
                detail = ""
                all_up = False
            else:
                state = f"http-{code}"
                detail = ""
                all_up = False
        icon = "UP" if state == "healthy" else "DOWN"
        if state != "healthy":
            all_up = False
        port_str = str(port) if port else "---"
        print(f"  {name:<22s} {port_str:>6s}  {icon:>8s}  {state}{f'  {detail}' if detail else ''}")

    print("=" * 68)
    print(f"  {'All services healthy!' if all_up else 'Some services are DOWN'}")
    print("=" * 68)
    print()


def cmd_models(args):
    """List available models from the router /models endpoint."""
    if MOCK_MODE:
        print("\n  [MOCK_LLM=1] Using local canned model registry\n")
        print(f"  {'Key':<18s} {'Role':<22s} Name")
        print("  " + "-" * 68)
        for key, info in MOCK_MODELS.items():
            print(f"  {key:<18s} {info['role']:<22s} {info['name']}")
        print()
        return

    cfg = load_services()
    router_svc = cfg.get("services", {}).get("router", {})
    port = router_svc.get("port", 8010)
    code, body = _http("GET", _url(port, "/models"))
    if code == 0:
        print(f"error: router at :{port} is unreachable", file=sys.stderr)
        sys.exit(1)
    if not isinstance(body, dict) or "error" in body:
        print(f"error: /models returned {code}: {body}", file=sys.stderr)
        sys.exit(1)

    print(f"\n  Models from router :{port}\n")
    print(f"  {'Key':<18s} {'Role':<22s} Name")
    print("  " + "-" * 68)
    for key, info in body.items():
        name = info.get("name", "")
        role = info.get("role", "")
        print(f"  {key:<18s} {role:<22s} {name}")
    print()


def cmd_route(args):
    """Send a prompt to the router and print the response."""
    if MOCK_MODE:
        task = args.task if args.task else "default"
        response = MOCK_RESPONSES.get(task, MOCK_RESPONSES["default"])
        print(f"[mock | {task} | 0ms]")
        print(response)
        print()
        return

    cfg = load_services()
    router_svc = cfg.get("services", {}).get("router", {})
    port = router_svc.get("port", 8010)

    payload = {"prompt": args.prompt}
    if args.max_tokens:
        payload["max_tokens"] = args.max_tokens
    if args.profile:
        payload["profile"] = args.profile
    if args.task:
        payload["task"] = args.task

    code, body = _http("POST", _url(port, "/route"), payload)
    if code == 0:
        print(f"error: router at :{port} is unreachable", file=sys.stderr)
        sys.exit(1)
    if not isinstance(body, dict):
        print(f"error: unexpected response from /route: {body}", file=sys.stderr)
        sys.exit(1)

    model_used = body.get("model_used", "?")
    task_type = body.get("task_type", "?")
    elapsed = body.get("elapsed_ms", "?")
    resp = body.get("response", {})

    if isinstance(resp, dict):
        text = (resp.get("content")
                or (resp.get("choices") or [{}])[0].get("message", {}).get("content", ""))
    elif isinstance(resp, str):
        text = resp
    else:
        text = json.dumps(resp) if resp else ""

    print(f"[{model_used} | {task_type} | {elapsed}ms]")
    print(text if text else json.dumps(body, indent=2))
    print()


def cmd_workflows(args):
    """List registered workflows from the workflow engine."""
    cfg = load_services()
    wf_svc = cfg.get("services", {}).get("workflow_engine", {})
    port = wf_svc.get("port", 8040)
    code, body = _http("GET", _url(port, "/workflows"))
    if code == 0:
        print(f"error: workflow engine at :{port} is unreachable", file=sys.stderr)
        sys.exit(1)
    workflows = body.get("workflows", []) if isinstance(body, dict) else []
    print(f"\n  Registered workflows ({len(workflows)}):\n")
    for wf in workflows:
        print(f"  - {wf}")
    print()


def cmd_run(args):
    """Execute a workflow by ID."""
    cfg = load_services()
    wf_svc = cfg.get("services", {}).get("workflow_engine", {})
    port = wf_svc.get("port", 8040)

    payload = {"workflow": args.workflow_id}
    if args.context:
        try:
            payload["context"] = json.loads(args.context)
        except ValueError as exc:
            print(f"error: --context is not valid JSON: {exc}", file=sys.stderr)
            sys.exit(1)

    code, body = _http("POST", _url(port, "/workflow/run"), payload)
    if code == 0:
        print(f"error: workflow engine at :{port} is unreachable", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(body, indent=2))
    print()


def cmd_start(args):
    """Start all services via launch.py in background mode."""
    if not LAUNCH_PY.exists():
        print(f"error: launch.py not found at {LAUNCH_PY}", file=sys.stderr)
        sys.exit(1)
    print("[freeai] Starting all services via launch.py (background) ...")
    subprocess.Popen(
        [sys.executable, str(LAUNCH_PY), "--bg"],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("[freeai] Services starting. Use 'freeai status' to check readiness.")


def cmd_stop(args):
    """Stop all services via launch.py."""
    if not LAUNCH_PY.exists():
        print(f"error: launch.py not found at {LAUNCH_PY}", file=sys.stderr)
        sys.exit(1)
    print("[freeai] Stopping all services via launch.py ...")
    result = subprocess.run(
        [sys.executable, str(LAUNCH_PY), "--stop", "all"],
        cwd=str(ROOT),
    )
    sys.exit(result.returncode)


def cmd_logs(args):
    """Tail logs for a service."""
    service = args.service
    log_candidates = []

    # Check logs/ directory for service-specific log files
    if LOGS_DIR.exists():
        for f in LOGS_DIR.iterdir():
            fname = f.name.lower()
            if fname.startswith(service.lower()) or f"{service}.log" == fname:
                log_candidates.append(f)
        # Also match services with hyphens/underscores
        alt = service.replace("_", "-")
        for f in LOGS_DIR.iterdir():
            if f.name.lower() == f"{alt}.log" and f not in log_candidates:
                log_candidates.append(f)

    # Check .runs/ for service-specific log files (not .pid files)
    if RUNS_DIR.exists():
        for f in RUNS_DIR.iterdir():
            if f.suffix != ".log":
                continue
            fname = f.name.lower()
            if fname.startswith(service.lower()):
                log_candidates.append(f)

    if not log_candidates:
        print(f"error: no log files found for service '{service}'", file=sys.stderr)
        print(f"  looked in: {LOGS_DIR}, {RUNS_DIR}", file=sys.stderr)
        sys.exit(1)

    # Use the most recently modified log file
    log_file = max(log_candidates, key=lambda p: p.stat().st_mtime)

    if args.lines:
        # Show last N lines and exit
        with open(log_file, "r", errors="replace") as f:
            lines = f.readlines()
        start = max(0, len(lines) - args.lines)
        for line in lines[start:]:
            print(line, end="")
        print()
        return

    print(f"[freeai] Tailing {log_file} (Ctrl+C to stop)\n")
    try:
        with open(log_file, "r", errors="replace") as f:
            f.seek(0, 2)  # seek to end
            tail_lines = []
            while True:
                line = f.readline()
                if line:
                    if not line.endswith("\n"):
                        tail_lines.append(line)
                        line += "\n"
                    else:
                        if tail_lines:
                            print("".join(tail_lines), end="")
                            tail_lines = []
                        print(line, end="")
                else:
                    time.sleep(0.2)
    except KeyboardInterrupt:
        print()


def main():
    parser = argparse.ArgumentParser(
        prog="freeai",
        description=__doc__.strip().split("\n")[0],
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="show all service health (ports from services.json)")

    sub.add_parser("models", help="list available models from /models endpoint")

    p_route = sub.add_parser("route", help="send prompt to router and print response")
    p_route.add_argument("prompt", help="the prompt to send")
    p_route.add_argument("--max-tokens", type=int, default=None, help="max tokens in response")
    p_route.add_argument("--profile", choices=["strict", "balanced", "creative", "verbose", "minimal"],
                         help="agent profile")
    p_route.add_argument("--task", choices=["default", "code", "analysis", "full_project"],
                         default=None, help="task type hint (used in MOCK_LLM mode)")

    sub.add_parser("workflows", help="list workflows from /workflows endpoint")

    p_run = sub.add_parser("run", help="execute a workflow")
    p_run.add_argument("workflow_id", help="workflow ID to run")
    p_run.add_argument("--context", default=None, help="JSON object string for workflow context")

    sub.add_parser("start", help="start all services via launch.py")
    sub.add_parser("stop", help="stop all services")

    p_logs = sub.add_parser("logs", help="tail logs for a service")
    p_logs.add_argument("service", help="service name (e.g. router, dashboard, agents)")
    p_logs.add_argument("-n", "--lines", type=int, default=0,
                        help="show last N lines and exit (default: tail -f)")

    args = parser.parse_args()
    dispatch = {
        "status": cmd_status,
        "models": cmd_models,
        "route": cmd_route,
        "workflows": cmd_workflows,
        "run": cmd_run,
        "start": cmd_start,
        "stop": cmd_stop,
        "logs": cmd_logs,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    import urllib.request
    import urllib.error
    main()
