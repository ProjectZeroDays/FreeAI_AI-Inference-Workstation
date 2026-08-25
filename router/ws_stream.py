#!/usr/bin/env python3
"""WebSocket token streaming adapter for router + agents.

Run alongside Flask routes via uvicorn: ws://localhost:8011/ws/route
Clients send JSON {prompt, max_tokens?, temperature?} and receive token
frames {"content": "..."} until {"done": true}.
"""
import asyncio
import json
import os
import threading

try:
    import websockets
except ImportError:
    websockets = None

from router import app as flask_app  # noqa: reuse metrics/helpers

# Bridge: reuse existing streaming generators via asyncio.to_thread
async def ws_route(websocket):
    async for raw in websocket:
        try:
            data = json.loads(raw)
            prompt = data.get("prompt", "")
            if not prompt:
                await websocket.send(json.dumps({"error": "prompt required"}))
                continue
            # stream via existing SSE generator in thread
            from router.router import stream_route, classify_task
            task, _ = classify_task(prompt)
            gen = stream_route(prompt, task, data.get("agent"), payload_base=data)
            for chunk in gen:
                # chunk is 'data: {...}\n\n' — extract JSON payload
                if "content" in chunk:
                    try:
                        obj = json.loads(chunk[len("data: "):].strip())
                        if "content" in obj:
                            await websocket.send(json.dumps({"content": obj["content"]}))
                    except Exception:
                        continue
            await websocket.send(json.dumps({"done": True}))
        except Exception as e:
            await websocket.send(json.dumps({"error": str(e)}))

def start_ws(port=8011):
    if websockets is None:
        print("websockets not installed")
        return
    import asyncio
    async def main():
        async with websockets.serve(ws_route, "0.0.0.0", port):
            await asyncio.Future()
    asyncio.run(main())

if __name__ == "__main__":
    start_ws(int(os.environ.get("WS_PORT", "8011")))
