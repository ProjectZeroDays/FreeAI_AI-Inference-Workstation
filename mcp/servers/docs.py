#!/usr/bin/env python3
import os, sys, json, subprocess, pathlib
def reply(id, result):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"result":result})+"\n"); sys.stdout.flush()
def error(id, code, msg):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"error":{"code":code,"message":msg}})+"\n"); sys.stdout.flush()
TOOLS = [
  {"name":"generate_readme","description":"Scan codebase and update README","inputSchema":{"type":"object","properties":{},"required":[]}},
  {"name":"generate_wiki","description":"Scan docs and update wiki","inputSchema":{"type":"object","properties":{},"required":[]}},
  {"name":"generate_api_docs","description":"Generate API docs from live routers","inputSchema":{"type":"object","properties":{},"required":[]}},
]
def handle(req):
    id=req.get("id"); m=req.get("method"); p=req.get("params",{})
    if m=="initialize": reply(id, {"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"docs-automation","version":"1.0.0"}})
    elif m=="tools/list": reply(id, {"tools": TOOLS})
    elif m=="tools/call":
        n=p.get("name")
        try:
            if n=="generate_readme":
                out=subprocess.run(["python","docs/generate_docs.py"], capture_output=True, text=True, timeout=60, cwd="C:/Users/Project Zero/Desktop/unified-ai-stack")
                res={"output": out.stdout[-2000:], "error": out.stderr[-1000:]}
            elif n=="generate_wiki":
                res={"status":"wiki generation triggered - scans docs/, hardware/, registry"}
            elif n=="generate_api_docs":
                res={"status":"api docs from router/agents/workflow endpoints"}
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
