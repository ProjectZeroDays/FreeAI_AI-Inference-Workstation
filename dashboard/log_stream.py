"""WebSocket log streaming service for the FreeAI dashboard.

Runs a separate asyncio WebSocket server on port 8766 alongside the
Flask dashboard. Flask threads call push_log() to push entries;
connected clients receive them in real time. Supports HTTP fallback
via get_log_buffer().
"""
import asyncio
import json
import logging
import threading
from typing import Dict, List, Optional, Set

try:
    import websockets
except ImportError:
    websockets = None

logger = logging.getLogger("log_stream")

MAX_BUFFER = 1000

# ── State ──────────────────────────────────────────────────────────
_log_buffers: Dict[str, List[dict]] = {}
_lock = threading.Lock()
_connected_clients: Set[any] = set()
_loop: asyncio.AbstractEventLoop | None = None
_queue: asyncio.Queue | None = None
_server: any = None


def _get_buffer(service: str) -> List[dict]:
    with _lock:
        return list(_log_buffers.get(service, []))


def _push_to_buffer(service: str, entry: dict) -> None:
    with _lock:
        buf = _log_buffers.get(service)
        if buf is None:
            buf = []
            _log_buffers[service] = buf
        buf.append(entry)
        if len(buf) > MAX_BUFFER:
            _log_buffers[service] = buf[-MAX_BUFFER:]


def push_log(service: str, level: str, message: str, **kwargs) -> None:
    """Push a log entry from any thread."""
    import time as _time
    entry = {
        "ts": _time.time(),
        "service": service,
        "level": level,
        "message": message,
        **kwargs,
    }
    _push_to_buffer(service, entry)
    if _queue is not None:
        try:
            _queue.put_nowait(entry)
        except asyncio.QueueFull:
            pass


def get_log_buffer(service: Optional[str] = None, limit: int = 100) -> List[dict]:
    """Return recent log entries, optionally filtered by service."""
    with _lock:
        if service:
            buf = list(_log_buffers.get(service, []))
        else:
            buf = []
            for svc_buf in _log_buffers.values():
                buf.extend(svc_buf)
    buf.sort(key=lambda e: e.get("ts", 0))
    return buf[-limit:]


def clear_log_buffer(service: Optional[str] = None) -> None:
    with _lock:
        if service:
            _log_buffers.pop(service, None)
        else:
            _log_buffers.clear()


async def _ws_handler(websocket) -> None:
    """Handle a single WebSocket client connection."""
    filters = {}
    with _lock:
        _connected_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if isinstance(data, dict) and "filter" in data:
                    filters = data["filter"]
                    if not isinstance(filters, dict):
                        filters = {}
                    await _send_initial(websocket, filters)
            except (json.JSONDecodeError, KeyError):
                pass
    finally:
        with _lock:
            _connected_clients.discard(websocket)


async def _send_initial(websocket, filters: dict) -> None:
    service = filters.get("service")
    level = filters.get("level")
    keyword = filters.get("keyword", "").lower()
    buf = get_log_buffer(service=service, limit=MAX_BUFFER)
    for entry in buf:
        if level and entry.get("level") != level:
            continue
        if keyword and keyword not in entry.get("message", "").lower():
            continue
        try:
            await websocket.send(json.dumps(entry))
        except Exception:
            break


async def _broadcast_loop() -> None:
    global _queue
    _queue = asyncio.Queue()
    while True:
        try:
            entry = await asyncio.wait_for(_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        payload = json.dumps(entry)
        svc = entry.get("service")
        lvl = entry.get("level")
        msg = entry.get("message", "")
        with _lock:
            clients = list(_connected_clients)
        for ws in clients:
            try:
                f: dict = getattr(ws, "filters", {})
                if not isinstance(f, dict):
                    f = {}
                if svc and f.get("service") and f["service"] != svc:
                    continue
                if lvl and f.get("level") and f["level"] != lvl:
                    continue
                kw = f.get("keyword", "")
                if kw and kw.lower() not in msg.lower():
                    continue
                await ws.send(payload)
            except Exception:
                pass


async def _ws_server_coroutine(host: str, port: int) -> None:
    global _server
    if websockets is None:
        logger.error("websockets package not installed")
        return
    _server = await websockets.serve(_ws_handler, host, port)
    logger.info("log stream ws server started on ws://%s:%d", host, port)
    await _server.wait_closed()


def start(host: str = "127.0.0.1", port: int = 8766) -> threading.Thread:
    """Start the WebSocket log stream server in a background thread."""

    async def _main() -> None:
        bg = asyncio.create_task(_broadcast_loop())
        srv = await websockets.serve(_ws_handler, host, port)
        logger.info("log stream ws server on ws://%s:%d", host, port)
        await asyncio.gather(bg, srv.wait_closed())

    global _loop
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

    def _run() -> None:
        _loop.run_until_complete(_main())

    t = threading.Thread(target=_run, daemon=True, name="log-ws")
    t.start()
    return t
