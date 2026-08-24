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

    args = parser.parse_args()
    {
        "status": cmd_status,
        "models": cmd_models,
        "route": cmd_route,
        "workflows": cmd_workflows,
        "run": cmd_run,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
