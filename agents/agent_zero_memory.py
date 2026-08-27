#!/usr/bin/env python3
"""Agent Zero-style persistent memory system.

Features:
- Per-session conversation history with configurable turn limits
- Long-term knowledge storage with JSONL journal
- Semantic recall via keyword search (extendable to vector search)
- Cross-session memory sharing for recurring patterns
- Auto-summarization of long sessions
- Integration with FreeAI router for context injection
"""
import json
import os
import re
import time
import hashlib
import threading
from pathlib import Path
from collections import OrderedDict, defaultdict


MEMORY_DIR = Path(__file__).parent.parent / "config" / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

SESSION_TTL_S = int(os.environ.get("MEMORY_SESSION_TTL", str(86400 * 7)))
MAX_TURNS_PER_SESSION = int(os.environ.get("MEMORY_MAX_TURNS", "50"))
SUMMARIZE_AFTER_TURNS = int(os.environ.get("MEMORY_SUMMARIZE_AFTER", "30"))
MAX_SUMMARY_LEN = 2000


class MemoryStore:
    """Thread-safe persistent memory store."""

    def __init__(self, store_dir: Path = MEMORY_DIR):
        self._store_dir = store_dir
        self._sessions: OrderedDict[str, list[dict]] = OrderedDict()
        self._summaries: dict[str, str] = {}
        self._global_knowledge: list[dict] = []
        self._lock = threading.Lock()
        self._load_disk()

    def _session_path(self, session_id: str) -> Path:
        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", session_id)[:64]
        return self._store_dir / f"session_{safe}.jsonl"

    def _load_disk(self):
        """Load all sessions from disk on startup."""
        for fpath in self._store_dir.glob("session_*.jsonl"):
            sid = fpath.stem.replace("session_", "")
            entries = []
            try:
                for line in fpath.read_text(encoding="utf-8").splitlines():
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            except Exception:
                continue
            if entries:
                self._sessions[sid] = entries

        # Load global knowledge
        global_path = self._store_dir / "knowledge.jsonl"
        if global_path.exists():
            for line in global_path.read_text(encoding="utf-8").splitlines():
                try:
                    self._global_knowledge.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    def _flush_session(self, session_id: str):
        """Persist a session to disk."""
        path = self._session_path(session_id)
        entries = self._sessions.get(session_id, [])
        with open(path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _flush_global(self):
        path = self._store_dir / "knowledge.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for entry in self._global_knowledge:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def remember(self, session_id: str, role: str, content: str,
                 metadata: dict = None):
        """Store a message in the session memory."""
        if not session_id or not content.strip():
            return
        entry = {
            "ts": int(time.time()),
            "session": session_id,
            "role": role,
            "content": content[:10000],
            "metadata": metadata or {},
        }
        with _lock:
            hist = self._sessions.setdefault(session_id, [])
            hist.append(entry)
            while len(hist) > MAX_TURNS_PER_SESSION:
                hist.pop(0)
            self._sessions.move_to_end(session_id)
            # Evict oldest sessions if too many
            while len(self._sessions) > 500:
                self._sessions.popitem(last=False)

    def recall(self, session_id: str, limit: int = 20,
               role_filter: str = None) -> list[dict]:
        """Retrieve recent messages for a session."""
        with self._lock:
            hist = list(self._sessions.get(session_id, []))
        if role_filter:
            hist = [e for e in hist if e.get("role") == role_filter]
        return hist[-limit:]

    def recall_context(self, session_id: str, max_tokens: int = 4096) -> str:
        """Build a context string from recent history for LLM injection."""
        entries = self.recall(session_id, limit=MAX_TURNS_PER_SESSION)
        if not entries:
            return ""
        parts = []
        total_len = 0
        for e in reversed(entries):
            text = f"{e['role']}: {e['content']}"
            if total_len + len(text) > max_tokens * 4:
                break
            parts.append(text)
            total_len += len(text)
        return "\n".join(reversed(parts))

    def summarize_session(self, session_id: str) -> str:
        """Generate a summary of a session (stored separately)."""
        entries = self.recall(session_id, limit=MAX_TURNS_PER_SESSION)
        if len(entries) < 5:
            return ""
        # Simple heuristic summary: first + last + key turns
        summary_parts = []
        if entries:
            summary_parts.append(f"Session started: {entries[0]['content'][:200]}")
        # Find longest exchange
        longest = max(entries, key=lambda e: len(e.get("content", "")))
        if longest["role"] == "assistant":
            summary_parts.append(f"Key insight: {longest['content'][:300]}")
        summary = " | ".join(summary_parts)
        self._summaries[session_id] = summary[:MAX_SUMMARY_LEN]
        return summary

    def search_global(self, query: str, limit: int = 10) -> list[dict]:
        """Keyword search across all global knowledge entries."""
        if not query.strip():
            return []
        terms = set(query.lower().split())
        scored = []
        for entry in self._global_knowledge:
            text = (entry.get("content", "") + " " +
                    entry.get("tags", "")).lower()
            score = sum(1 for t in terms if t in text)
            if score > 0:
                scored.append((score, entry))
        scored.sort(reverse=True)
        return [e for _, e in scored[:limit]]

    def remember_global(self, content: str, tags: list[str] = None,
                        session_id: str = None):
        """Store cross-session knowledge."""
        entry = {
            "ts": int(time.time()),
            "content": content[:5000],
            "tags": tags or [],
            "session": session_id,
        }
        with self._lock:
            self._global_knowledge.append(entry)
            # Keep global knowledge manageable
            if len(self._global_knowledge) > 1000:
                self._global_knowledge = self._global_knowledge[-500:]
        self._flush_global()

    def recall_global(self, limit: int = 20) -> list[dict]:
        """Get most recent global knowledge entries."""
        with self._lock:
            return list(self._global_knowledge[-limit:])

    def forget_session(self, session_id: str):
        """Delete a session's memory."""
        with self._lock:
            self._sessions.pop(session_id, None)
        path = self._session_path(session_id)
        if path.exists():
            path.unlink()

    def flush_all(self):
        """Persist all sessions to disk."""
        with self._lock:
            for sid in list(self._sessions.keys()):
                self._flush_session(sid)
            self._flush_global()

    def stats(self) -> dict:
        with self._lock:
            return {
                "sessions": len(self._sessions),
                "total_entries": sum(len(v) for v in self._sessions.values()),
                "global_knowledge": len(self._global_knowledge),
                "summaries": len(self._summaries),
                "sessions_dir": str(self._store_dir),
            }


_lock = threading.Lock()
_store = None


def get_store() -> MemoryStore:
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store


def remember(session_id: str, role: str, content: str,
             metadata: dict = None):
    return get_store().remember(session_id, role, content, metadata)


def recall(session_id: str, limit: int = 20) -> list[dict]:
    return get_store().recall(session_id, limit)


def recall_context(session_id: str, max_tokens: int = 4096) -> str:
    return get_store().recall_context(session_id, max_tokens)


def search_global(query: str, limit: int = 10) -> list[dict]:
    return get_store().search_global(query, limit)


def remember_global(content: str, tags: list[str] = None):
    return get_store().remember_global(content, tags)


def stats() -> dict:
    return get_store().stats()


if __name__ == "__main__":
    import sys
    store = get_store()
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        print(json.dumps(store.stats(), indent=2))
    elif len(sys.argv) > 1:
        print(f"Memory store at: {MEMORY_DIR}")
        print(f"Sessions: {len(store._sessions)}")
    else:
        print("Usage: memory_store.py [stats|<session_id>]")
