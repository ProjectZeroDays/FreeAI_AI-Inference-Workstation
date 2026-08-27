"""In-memory session conversation store.

Each agent gets its own conversation history keyed by session_id.
History is capped at MEMORY_MAX_TURNS (default 20) and the store
is capped at 200 active sessions to limit memory pressure.
"""
from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Any

MEMORY_MAX_TURNS = 20
MEMORY_MAX_SESSIONS = 200

_MEMORY: OrderedDict[str, list[dict]] = OrderedDict()
_LOCK = threading.Lock()


def remember(session_id: str, role: str, content: str) -> None:
    """Append a single turn to the given session."""
    if not session_id:
        return
    with _LOCK:
        hist = _MEMORY.setdefault(session_id, [])
        hist.append({"role": role, "content": content})
        while len(hist) > MEMORY_MAX_TURNS:
            hist.pop(0)
        _MEMORY.move_to_end(session_id)
        while len(_MEMORY) > MEMORY_MAX_SESSIONS:
            _MEMORY.popitem(last=False)


def recall(session_id: str) -> list[dict]:
    """Return the full conversation history for a session."""
    with _LOCK:
        return list(_MEMORY.get(session_id, []))


def clear(session_id: str) -> bool:
    """Remove a session's history. Returns True if it existed."""
    with _LOCK:
        if session_id in _MEMORY:
            del _MEMORY[session_id]
            return True
        return False


def stats() -> dict:
    with _LOCK:
        total_turns = sum(len(v) for v in _MEMORY.values())
        return {
            "sessions": len(_MEMORY),
            "total_turns": total_turns,
            "max_turns_per_session": MEMORY_MAX_TURNS,
            "max_sessions": MEMORY_MAX_SESSIONS,
        }
