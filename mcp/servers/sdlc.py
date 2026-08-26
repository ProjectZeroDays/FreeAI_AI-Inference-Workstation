#!/usr/bin/env python3
import os, sys, json, requests
AUTO_API = os.environ.get("AUTO_API", "http://localhost:8050")
ROUTER_API = os.environ.get("AGENT_API", "http://localhost:8020")
def reply(id, result):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"result":result})+"\n"); sys.stdout.flush()
def error(id, code, msg):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"error":{"code":code,"message":msg}})+"\n"); sys.stdout.flush()
TOOLS = [
  {"name":"sdlc_start","description":"Start autonomous SDLC run","inputSchema":{"type":"object","properties":{"spec":{"type":"string"},"profile":{"type":"string"}},"required":["spec"]}},
  {"name":"sdlc_status","description":"Get run status","inputSchema":{"type":"object","properties":{"run_id":{"type":"string"}},"required":["run_id"]}},
  {"name":"sdlc_fetch","description":"Fetch artifact","inputSchema":{"type":"object","properties":{"run_id":{"type":"string"}},"required":["run_id"]}},
  {"name":"sdlc_security_gate","description":"Run red/blue/purple gate on workspace","inputSchema":{"type":"object","properties":{"run_id":{"type":"string"}},"required":["run_id"]}},
]
def handle(req):
    id=req.get("id"); m=req.get("method"); p=req.get("params",{})
    if m=="initialize": reply(id, {"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"sdlc-apex","version":"2.0.0"}})
    elif m=="tools/list": reply(id, {"tools": TOOLS})
    elif m=="tools/call":
        n=p.get("name"); a=p.get("arguments",{})
        try:
            if n=="sdlc_start":
                r=requests.post(f"{AUTO_API}/auto/start", json={"spec":a["spec"],"profile":a.get("profile","balanced"),"enable_shell":True}, timeout=30); r.raise_for_status(); res=r.json()
            elif n=="sdlc_status":
                r=requests.get(f"{AUTO_API}/auto/runs/{a['run_id']}", timeout=15); r.raise_for_status(); res=r.json()
            elif n=="sdlc_fetch": res={"artifact_url": f"{AUTO_API}/auto/runs/{a['run_id']}/artifact"}
            elif n=="sdlc_security_gate":
                r=requests.post(f"{ROUTER_API}/agent/red", json={"operation":"chain","target":a["run_id"]}, timeout=660); red=r.json()
                b=requests.post(f"{ROUTER_API}/agent/blue", json={"operation":"harden","target":a["run_id"]}, timeout=660); blue=b.json()
                res={"red":red,"blue":blue,"gate":"security gate executed"}
            else: return error(id,-32601,f"unknown {n}")
            reply(id, {"content":[{"type":"text","text": json.dumps(res, indent=2)}]})
        except Exception as e: error(id,-32603,str(e))
    elif m=="notifications/initialized": pass
    else: error(id,-32601,f"unknown {m}")
def main():
    for line in sys.stdin:
        line=line.strip()
        if not line: continue
        try: handle(json.loads(line))
        except Exception as e: sys.stderr.write(f"err {e}\n")
if __name__=="__main__": main()
