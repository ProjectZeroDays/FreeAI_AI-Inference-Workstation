#!/usr/bin/env python3
import os, sys, json, requests
ROUTER_API = os.environ.get("AGENT_API", "http://localhost:8020")
def reply(id, result):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"result":result})+"\n"); sys.stdout.flush()
def error(id, code, msg):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"error":{"code":code,"message":msg}})+"\n"); sys.stdout.flush()
TOOLS = [
  {"name":"blue_hunt","description":"Hunt APT/threat","inputSchema":{"type":"object","properties":{"telemetry":{"type":"string"},"hypothesis":{"type":"string"}},"required":["telemetry"]}},
  {"name":"blue_harden","description":"Harden system/network","inputSchema":{"type":"object","properties":{"target":{"type":"string"},"profile":{"type":"string"}},"required":["target"]}},
  {"name":"blue_triage","description":"Triage alert","inputSchema":{"type":"object","properties":{"alert":{"type":"string"}},"required":["alert"]}},
  {"name":"blue_forensics","description":"Forensic analysis","inputSchema":{"type":"object","properties":{"artifact":{"type":"string"}},"required":["artifact"]}},
  {"name":"blue_compliance","description":"Compliance check","inputSchema":{"type":"object","properties":{"framework":{"type":"string"}},"required":["framework"]}},
]
def call_blue(op, **kw):
    r=requests.post(f"{ROUTER_API}/agent/blue", json={"operation":op, **kw}, timeout=660); r.raise_for_status(); return r.json()
def handle(req):
    id=req.get("id"); m=req.get("method"); p=req.get("params",{})
    if m=="initialize": reply(id, {"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"blue-team-apex","version":"2.0.0"}})
    elif m=="tools/list": reply(id, {"tools": TOOLS})
    elif m=="tools/call":
        n=p.get("name"); a=p.get("arguments",{})
        try:
            if n=="blue_hunt": res=call_blue("hunt", telemetry=a["telemetry"], technique=a.get("hypothesis"))
            elif n=="blue_harden": res=call_blue("harden", target=a["target"], framework=a.get("profile"))
            elif n=="blue_triage": res=call_blue("triage", telemetry=a["alert"])
            elif n=="blue_forensics": res=call_blue("forensics", target=a["artifact"])
            elif n=="blue_compliance": res=call_blue("compliance", framework=a["framework"])
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
