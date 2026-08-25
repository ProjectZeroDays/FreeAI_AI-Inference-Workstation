#!/usr/bin/env python3
"""tokugawa-cli — control the Unified GPU Inference Stack from a shell."""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010")
AGENT_API = os.environ.get("AGENT_API", "http://localhost:8020")
WORKFLOW_API = os.environ.get("WORKFLOW_API", "http://localhost:8040")
AUTONOMOUS_API = os.environ.get("AUTONOMOUS_API", "http://localhost:8050")
DASH_API = os.environ.get("DASH_API", "http://localhost:8030")


def _req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=660) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode() or "{}")
    except urllib.error.URLError as exc:
        return 0, {"error": str(exc.reason)}


def _print(obj):
    print(json.dumps(obj, indent=2))


def cmd_status(_):
    for name, base in (("router", ROUTER_URL), ("agents", AGENT_API),
                       ("workflow", WORKFLOW_API)):
        code, body = _req("GET", f"{base}/health")
        state = "UP" if code == 200 else "DOWN"
        print(f"{name:10s} {state}")
    code, body = _req("GET", f"{ROUTER_URL}/metrics")
    if code == 200:
        _print(body)


def cmd_models(_):
    _, models = _req("GET", f"{ROUTER_URL}/models")
    for key, info in models.items():
        print(f"{key:14s} {info['role']:22s} {info['name']}")


def cmd_route(args):
    payload = {"prompt": args.prompt}
    if args.max_tokens:
        payload["max_tokens"] = args.max_tokens
    if args.profile:
        payload["profile"] = args.profile
    _, body = _req("POST", f"{ROUTER_URL}/route", payload)
    text = ""
    resp = body.get("response", {})
    if isinstance(resp, dict):
        text = (resp.get("content")
                or (resp.get("choices") or [{}])[0].get(
                    "message", {}).get("content", ""))
    print(f"[{body.get('model_used')} | {body.get('task_type')} "
          f"| {body.get('elapsed_ms', '?')}ms]")
    print(text or _print(body))


def cmd_workflows(_):
    _, body = _req("GET", f"{WORKFLOW_API}/workflows")
    for wf in body.get("workflows", []):
        print(wf)


def cmd_run(args):
    context = json.loads(args.context) if args.context else {}
    _, body = _req("POST", f"{WORKFLOW_API}/workflow/run",
                   {"workflow": args.name, "context": context})
    _print(body)


def cmd_auto_start(args):
    _, body = _req("POST", f"{AUTONOMOUS_API}/auto/start",
                   {"spec": args.spec,
                    "profile": args.profile,
                    "max_tasks": args.max_tasks,
                    "enable_shell": args.shell})
    print(f"run_id: {body.get('run_id')}")
    print("poll: tokugawa.py auto-status " + body.get("run_id", ""))


def _auto_poll(run_id):
    code, body = _req("GET", f"{AUTONOMOUS_API}/auto/runs/{run_id}")
    if code != 200:
        _print(body)
        return None
    print(f"[{body['status']}] tasks={len(body.get('tasks', []))} "
          f"files={len(body.get('files', []))} "
          f"fixes={body.get('fix_rounds', 0)}")
    for t in body.get("tasks", []):
        print(f"  {t['status']:8s} {t['id']}: {t['title']}")
    if body.get("report"):
        _print(body["report"])
    return body


def cmd_auto_status(args):
    import time as _time
    for i in range(max(1, args.watch)):
        body = _auto_poll(args.run_id)
        if body is None or body.get("status") in (
                "done", "failed", "cancelled"):
            break
        if args.watch > 1:
            _time.sleep(5)
    if body and body.get("artifact"):
        print(f"artifact: tokugawa.py auto-fetch {args.run_id}")


def cmd_auto_runs(_):
    _, body = _req("GET", f"{AUTONOMOUS_API}/auto/runs")
    for r in body.get("runs", []):
        print(f"{r['run_id']}  {r['status']:10s}  "
              f"{r['spec'][:60]}")


def cmd_auto_cancel(args):
    _, body = _req("POST",
                   f"{AUTONOMOUS_API}/auto/runs/{args.run_id}/cancel")
    _print(body)


def cmd_auto_fetch(args):
    import urllib.request
    url = f"{AUTONOMOUS_API}/auto/runs/{args.run_id}/artifact"
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        print(f"error: HTTP {exc.code} — artifact not ready?")
        return
    out = args.out or f"{args.run_id}.tar.gz"
    with open(out, "wb") as f:
        f.write(data)
    print(f"saved {out} ({len(data)} bytes)")


def cmd_presets(_):
    _, body = _req("GET", f"{DASH_API}/api/presets")
    for p in body.get("builtins", []):
        star = " (timed)" if p.get("idle_default_minutes") else ""
        print(f"* {p['name']}{star} — {p.get('description','')}")
    for p in body.get("customs", []):
        print(f"  {p['name']} — custom")


def cmd_preset(args):
    body = {}
    if args.idle:
        body["duration_min"] = args.idle
    code, out = _req(
        "POST", f"{DASH_API}/api/presets/{args.name}/apply", body)
    _print(out) if code != 200 else print(f"[preset] applied: {args.name}")


def cmd_settings(args):
    if args.action == "get":
        _, body = _req("GET", f"{DASH_API}/api/settings")
        s = body["settings"]
        if args.key:
            print(json.dumps({args.key: s.get(args.key)}))
        else:
            _print(s)
    elif args.action == "set":
        if not args.key or args.value is None:
            print("settings set KEY VALUE required", file=sys.stderr)
            raise SystemExit(2)
        try:
            val = json.loads(args.value)
        except ValueError:
            val = args.value
        code, body = _req("POST", f"{DASH_API}/api/settings",
                          {args.key: val})
        _print(body) if code != 200 else print("[settings] saved")


def main():
    parser = argparse.ArgumentParser(prog="tokugawa",
                                     description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="service health + router metrics")

    sub.add_parser("models", help="list registered models")

    p_route = sub.add_parser("route", help="send one prompt via the router")
    p_route.add_argument("prompt")
    p_route.add_argument("--max-tokens", type=int)
    p_route.add_argument("--profile",
                         choices=["strict", "balanced", "creative",
                                  "verbose", "minimal"])

    sub.add_parser("workflows", help="list registered workflows")

    p_run = sub.add_parser("run", help="run a workflow by name")
    p_run.add_argument("name")
    p_run.add_argument("--context", help="JSON object string")

    p_auto = sub.add_parser("auto-start",
                            help="launch an autonomous SDLC run")
    p_auto.add_argument("spec")
    p_auto.add_argument("--profile",
                        choices=["strict", "balanced", "creative",
                                 "verbose", "minimal"],
                        default="balanced")
    p_auto.add_argument("--max-tasks", type=int, default=8)
    p_auto.add_argument("--shell", action="store_true",
                        help="request shell verification "
                             "(server must enable it)")

    p_status = sub.add_parser("auto-status", help="poll an autonomous run")
    p_status.add_argument("run_id")
    p_status.add_argument("--watch", type=int, default=1,
                          help="poll N times (5s apart)")

    sub.add_parser("auto-runs", help="list autonomous runs")

    p_cancel = sub.add_parser("auto-cancel", help="cancel an autonomous run")
    p_cancel.add_argument("run_id")

    p_fetch = sub.add_parser("auto-fetch",
                             help="download the run's artifact tarball")
    p_fetch.add_argument("run_id")
    p_fetch.add_argument("-o", "--out")

    sub.add_parser("presets", help="list recommended + custom presets")

    p_pre = sub.add_parser("preset", help="apply a preset by name")
    p_pre.add_argument("name")
    p_pre.add_argument("--idle", type=int, default=None,
                       help="treat as timed-idle for N minutes")

    p_set = sub.add_parser("settings",
                           help="get/set shared runtime settings")
    p_set.add_argument("action", choices=["get", "set"])
    p_set.add_argument("key", nargs="?")
    p_set.add_argument("value", nargs="?")

    args = parser.parse_args()
    {
        "status": cmd_status,
        "models": cmd_models,
        "route": cmd_route,
        "workflows": cmd_workflows,
        "run": cmd_run,
        "auto-start": cmd_auto_start,
        "auto-status": cmd_auto_status,
        "auto-runs": cmd_auto_runs,
        "auto-cancel": cmd_auto_cancel,
        "auto-fetch": cmd_auto_fetch,
        "presets": cmd_presets,
        "preset": cmd_preset,
        "settings": cmd_settings,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
