"""WebSocket notification push server for the FreeAI dashboard.

Runs a separate asyncio WebSocket server alongside the Flask app.
Flask calls notify() to push events; connected clients receive them
in real time.
"""
import asyncio
import json
import logging
import threading
from pathlib import Path
from typing import Any, Dict, Set

try:
    import websockets
except ImportError:
    websockets = None

logger = logging.getLogger("notifications_ws")

CONFIG_DIR = Path(__file__).parent.parent / "config"
NOTIFICATIONS_PATH = CONFIG_DIR / "notifications.json"
MAX_LOG = 50

# ── State ──────────────────────────────────────────────────────────
_connected: Set[any] = set()
_lock = threading.Lock()
_loop: asyncio.AbstractEventLoop | None = None
_queue: asyncio.Queue | None = None
_server: websockets.WebSocketServer | None = None

# ── Settings (persisted) ───────────────────────────────────────────
_settings: Dict[str, Any] = {
    "enabled_types": ["error", "warning", "info", "success"],
    "sound": True,
}


def _load_settings() -> Dict[str, Any]:
    try:
        if NOTIFICATIONS_PATH.exists():
            data = json.loads(NOTIFICATIONS_PATH.read_text())
            global _settings
            _settings.update(data.get("settings", {}))
    except (json.JSONDecodeError, OSError):
        pass
    return _settings


def _save_settings() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {"settings": _settings}
    NOTIFICATIONS_PATH.write_text(json.dumps(data, indent=2))


def _load_log() -> list:
    try:
        if NOTIFICATIONS_PATH.exists():
            data = json.loads(NOTIFICATIONS_PATH.read_text())
            return data.get("log", [])
    except (json.JSONDecodeError, OSError):
        pass
    return []


def _save_log(log: list) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {"settings": _settings, "log": log}
    NOTIFICATIONS_PATH.write_text(json.dumps(data, indent=2))


# ── Public API (called from Flask threads) ─────────────────────────
def notify(title: str, message: str, level: str = "info", source: str = "") -> None:
    """Push a notification to all connected WebSocket clients and persist."""
    if level not in ("error", "warning", "info", "success"):
        level = "info"
    entry = {
        "id": f"{level}-{int(asyncio.get_event_loop().time() * 1000) if _loop else 0}",
        "ts": __import__("time").time(),
        "title": title,
        "message": message,
        "level": level,
        "source": source,
        "read": False,
    }
    log = _load_log()
    log.insert(0, entry)
    _save_log(log[:MAX_LOG])
    if _queue is not None:
        try:
            _queue.put_nowait(entry)
        except asyncio.QueueFull:
            pass


async def _ws_handler(websocket) -> None:
    """Handle a single WebSocket client connection."""
    with _lock:
        _connected.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("action") == "mark_read":
                    nid = data.get("id", "")
                    log = _load_log()
                    for item in log:
                        if item.get("id") == nid:
                            item["read"] = True
                    _save_log(log)
            except (json.JSONDecodeError, KeyError):
                pass
    finally:
        with _lock:
            _connected.discard(websocket)


async def _broadcast_loop() -> None:
    """Drain the queue and push to all connected clients."""
    global _queue
    _queue = asyncio.Queue()
    while True:
        try:
            entry = await asyncio.wait_for(_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        payload = json.dumps(entry)
        with _lock:
            clients = list(_connected)
        for ws in clients:
            try:
                await ws.send(payload)
            except Exception:
                pass


async def _ws_server_coroutine(host: str, port: int) -> None:
    global _server
    if websockets is None:
        logger.error("websockets package not installed")
        return
    _server = await websockets.serve(_ws_handler, host, port)
    logger.info("notification ws server started on ws://%s:%d", host, port)
    await _server.wait_closed()


def start(host: str = "127.0.0.1", port: int = 8765) -> threading.Thread:
    """Start the WebSocket notification server in a background thread."""
    _load_settings()

    async def _main() -> None:
        bg = asyncio.create_task(_broadcast_loop())
        srv = await websockets.serve(_ws_handler, host, port)
        logger.info("notification ws server on ws://%s:%d", host, port)
        await asyncio.gather(bg, srv.wait_closed())

    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

    def _run() -> None:
        _loop.run_until_complete(_main())

    t = threading.Thread(target=_run, daemon=True, name="notif-ws")
    t.start()
    return t


def get_settings() -> Dict[str, Any]:
    return dict(_settings)


def update_settings(updates: Dict[str, Any]) -> Dict[str, Any]:
    global _settings
    for k, v in updates.items():
        if k in _settings:
            _settings[k] = v
    _save_settings()
    return dict(_settings)


def get_log() -> list:
    return _load_log()


def clear_log() -> None:
    _save_log([])


def get_unread_count() -> int:
    return sum(1 for item in _load_log() if not item.get("read", False))
