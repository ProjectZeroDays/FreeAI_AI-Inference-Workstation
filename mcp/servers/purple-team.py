#!/usr/bin/env python3
import os, sys, json, requests
ROUTER_API = os.environ.get("AGENT_API", "http://localhost:8020")
def reply(id, result):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"result":result})+"\n"); sys.stdout.flush()
def error(id, code, msg):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"error":{"code":code,"message":msg}})+"\n"); sys.stdout.flush()
TOOLS = [
  {"name":"purple_design","description":"Design purple exercise","inputSchema":{"type":"object","properties":{"threat_actor":{"type":"string"},"objective":{"type":"string"}},"required":["threat_actor","objective"]}},
  {"name":"purple_orchestrate","description":"Orchestrate live","inputSchema":{"type":"object","properties":{"exercise_id":{"type":"string"}},"required":["exercise_id"]}},
  {"name":"purple_validate","description":"Validate control","inputSchema":{"type":"object","properties":{"control_id":{"type":"string"},"technique":{"type":"string"}},"required":["control_id","technique"]}},
  {"name":"purple_bridge","description":"Bridge red->blue","inputSchema":{"type":"object","properties":{"red_finding":{"type":"string"},"blue_gap":{"type":"string"}},"required":["red_finding","blue_gap"]}},
  {"name":"purple_score","description":"Score exercise","inputSchema":{"type":"object","properties":{"exercise_log":{"type":"string"}},"required":["exercise_log"]}},
]
def call_purple(op, **kw):
    r=requests.post(f"{ROUTER_API}/agent/purple", json={"operation":op, **kw}, timeout=660); r.raise_for_status(); return r.json()
def handle(req):
    id=req.get("id"); m=req.get("method"); p=req.get("params",{})
    if m=="initialize": reply(id, {"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"purple-team-apex","version":"2.0.0"}})
    elif m=="tools/list": reply(id, {"tools": TOOLS})
    elif m=="tools/call":
        n=p.get("name"); a=p.get("arguments",{})
        try:
            if n=="purple_design": res=call_purple("design", threat_actor=a["threat_actor"], objective=a["objective"])
            elif n=="purple_orchestrate": res=call_purple("orchestrate", exercise_id=a["exercise_id"])
            elif n=="purple_validate": res=call_purple("validate", control_id=a["control_id"], technique=a["technique"])
            elif n=="purple_bridge": res=call_purple("bridge", findings=a["red_finding"], technique=a["blue_gap"])
            elif n=="purple_score": res=call_purple("score", findings=a["exercise_log"])
            else: return error(id,-32601,f"unknown {n}")
            reply(id, {"content":[{"type":"text","text": json.dumps(res, indent=2)}]})
        except Exception as e: error(id,-32603,"An error occurred")
    elif m=="notifications/initialized": pass
    else: error(id,-32601,f"unknown {m}")
def main():
    for line in sys.stdin:
        line=line.strip()
        if not line: continue
        try: handle(json.loads(line))
        except Exception as e: sys.stderr.write(f"err {e}\n")
if __name__=="__main__": main()
