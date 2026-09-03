import sys
import json
import os
import urllib.request

API = "https://api.agnes-ai.com/v1/chat/completions"
TOKEN = os.environ.get("AGNES_API_KEY", "")
MODEL = "agnes.2.0-flash"


def stream_chat(message):
    if not TOKEN:
        print("Error: AGNES_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": message}],
        "stream": True
    }).encode("utf-8")
    req = urllib.request.Request(API,
        data=payload,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    response = urllib.request.urlopen(req)
    for line in response:
        line = line.decode("utf-8").strip()
        if line.startswith("data: "):
            data = line[6:]
            try:
                json_data = json.loads(data)
                if "choices" in json_data:
                    delta = json_data["choices"][0].get("delta", {})
                    if "content" in delta:
                        print(delta["content"], end="", flush=True)
                if json_data.get("finish_reason") == "stop":
                    print("")
                    break
            except:
                pass


if __name__ == "__main__":
    msg = sys.stdin.read().strip()
    print("-" * 40)
    print("FreeAI Chat")
    print("-" * 40)
    stream_chat(msg)
