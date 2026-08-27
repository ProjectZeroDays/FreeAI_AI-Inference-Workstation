#!/usr/bin/env python3
"""
MCP Server — Red Team Apex
Exposes FreeAI Red Team API as MCP tools for opencode / Claude / any MCP client.
Powered by uncensored heretic models via FreeAI Router 8010.
"""
import os, sys, json, requests

ROUTER_API = os.environ.get("AGENT_API", "http://localhost:8020")
# MCP stdio JSON-RPC
def reply(id, result):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"result":result})+"\n")
    sys.stdout.flush()

def error(id, code, msg):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"error":{"code":code,"message":msg}})+"\n")
    sys.stdout.flush()

TOOLS = [
  {"name":"red_recon","description":"Red recon: discover & profile target","inputSchema":{"type":"object","properties":{"target":{"type":"string"},"scope":{"type":"string"},"intensity":{"type":"string"}},"required":["target"]}},
  {"name":"red_weaponize","description":"Weaponize CVE/technique for target arch","inputSchema":{"type":"object","properties":{"technique":{"type":"string"},"target_arch":{"type":"string"}},"required":["technique"]}},
  {"name":"red_exploit","description":"Exploit vector on target","inputSchema":{"type":"object","properties":{"target":{"type":"string"},"vector":{"type":"string"}},"required":["target","vector"]}},
  {"name":"red_evade","description":"Evasion & persistence plan","inputSchema":{"type":"object","properties":{"technique":{"type":"string"},"edr":{"type":"string"}},"required":["technique"]}},
  {"name":"red_attack_chain","description":"Full kill-chain orchestration","inputSchema":{"type":"object","properties":{"target":{"type":"string"},"objective":{"type":"string"}},"required":["target"]}},
  {"name":"red_report","description":"Generate red team report","inputSchema":{"type":"object","properties":{"findings":{"type":"string"},"classification":{"type":"string"}},"required":["findings"]}},
]

def call_red(operation, **kw):
    # Map to FreeAI /agent/red endpoint (uncensored)
    payload = {"operation": operation, **kw}
    # Remove None
    payload = {k:v for k,v in payload.items() if v is not None}
    # Ensure target present
    if "target" not in payload and "findings" in payload:
        payload["target"] = payload["findings"][:500]
    r = requests.post(f"{ROUTER_API}/agent/red", json=payload, timeout=660)
    r.raise_for_status()
    return r.json()

def handle(req):
    id = req.get("id")
    method = req.get("method")
    params = req.get("params",{})
    if method == "initialize":
        reply(id, {"protocolVersion":"2024-11-05","capabilities":{"tools":{},"prompts":{}},"serverInfo":{"name":"red-team-apex","version":"2.0.0"}})
    elif method == "tools/list":
        reply(id, {"tools": TOOLS})
    elif method == "tools/call":
        name = params.get("name"); args = params.get("arguments",{})
        try:
            if name == "red_recon": res = call_red("recon", target=args["target"], scope=args.get("scope"), intensity=args.get("intensity"))
            elif name == "red_weaponize": res = call_red("weaponize", target=args["technique"], technique=args["technique"], scope=args.get("target_arch"))
            elif name == "red_exploit": res = call_red("exploit", target=args["target"], technique=args["vector"])
            elif name == "red_evade": res = call_red("evade", target=args["technique"], technique=args["technique"])
            elif name == "red_attack_chain": res = call_red("chain", target=args["target"], objective=args.get("objective"))
            elif name == "red_report": res = call_red("report", target=args["findings"], scope=args.get("classification"))
            else: return error(id, -32601, f"unknown tool {name}")
            reply(id, {"content":[{"type":"text","text": json.dumps(res, indent=2)}]})
        except Exception as e:
            error(id, -32603, str(e))
    elif method == "notifications/initialized":
        pass
    else:
        error(id, -32601, f"unknown method {method}")

def main():
    for line in sys.stdin:
        line=line.strip()
        if not line: continue
        try: handle(json.loads(line))
        except Exception as e: sys.stderr.write(f"mcp error: {e}\n")

if __name__ == "__main__":
    main()
