#!/usr/bin/env python3
import asyncio
import json
import os
import time
import threading

try:
    import websockets
except ImportError:
    websockets = None

from router import stream_route, classify_task, API_KEY as ROUTER_API_KEY

WEBSOCKET_PORT = int(os.environ.get('WS_PORT', '8011'))
KEEP_ALIVE_INTERVAL_S = 30
MAX_CONCURRENT_PER_IP = 10

_connections = {}
_lock = threading.Lock()


def _auth_ok(ws):
    if not ROUTER_API_KEY:
        return True
    key = ws.request.get('key', [''])[0] if hasattr(ws, 'request') else ''
    header = getattr(ws, 'headers', {}).get('X-API-Key', '')
    return bool(key == ROUTER_API_KEY or header == ROUTER_API_KEY)


async def _send(ws, payload):
    await ws.send(json.dumps(payload))


async def _handle(websocket):
    client_ip = websocket.remote_address[0] if websocket.remote_address else 'unknown'
    async with _lock:
        count = sum(1 for v in _connections.values() if v['ip'] == client_ip)
        if count >= MAX_CONCURRENT_PER_IP:
            await _send(websocket, {'event': 'error', 'message': 'rate limited'})
            return
        _connections[id(websocket)] = {'ip': client_ip, 'connected_at': time.monotonic()}
    try:
        if not _auth_ok(websocket):
            await _send(websocket, {'event': 'error', 'message': 'unauthorized'})
            return
        ping_task = asyncio.get_event_loop().create_task(_ping_loop(websocket))
        try:
            async for raw in websocket:
                await _handle_message(websocket, raw)
        finally:
            ping_task.cancel()
    finally:
        async with _lock:
            _connections.pop(id(websocket), None)


async def _handle_message(websocket, raw):
    try:
        data = json.loads(raw)
    except Exception:
        await _send(websocket, {'event': 'error', 'message': 'invalid json'})
        return
    prompt = data.get('prompt', '').strip()
    if not prompt:
        await _send(websocket, {'event': 'error', 'message': 'prompt required'})
        return
    task_type, _ = classify_task(prompt)
    gen = stream_route(prompt, task_type, data.get('agent'), payload_base=data)
    for chunk in gen:
        line = chunk.strip()
        if not line.startswith('data: '):
            continue
        try:
            obj = json.loads(line[6:])
        except Exception:
            continue
        if obj.get('error'):
            await _send(websocket, {'event': 'error', 'message': obj['error']})
            break
        if 'content' in obj:
            await _send(websocket, {'event': 'token', 'content': obj['content']})
        elif 'model' in obj:
            await _send(websocket, {
                'event': 'model',
                'model': obj.get('model'),
                'task_type': obj.get('task_type', task_type),
            })
    else:
        await _send(websocket, {'event': 'done'})


async def _ping_loop(websocket):
    while True:
        await asyncio.sleep(KEEP_ALIVE_INTERVAL_S)
        try:
            await websocket.ping()
        except Exception:
            break


def start_ws(port=WEBSOCKET_PORT):
    if websockets is None:
        print('websockets not installed')
        return
    async def main():
        async with websockets.serve(_handle, '0.0.0.0', port):
            await asyncio.Future()
    asyncio.run(main())


if __name__ == '__main__':
    start_ws()
