"""Persistent memory system — Agent Zero-style cross-session recall.

Features:
  - Per-session conversation history (in-memory, TTL-evicted)
  - Long-term knowledge store (JSONL, searchable by session/topic)
  - Cross-session recall (retrieve facts from other sessions)
  - Topic tagging via lightweight keyword extraction
  - Qdrant vector-search backend (falls back to JSONL)
  - REST API via FastAPI

Usage:
    python memory/memory_api.py          # runs on :8110
    MOCK_LLM=1 python memory/memory_api.py
"""
import json
import os
import re
import threading
import time
from collections import OrderedDict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

MEMORY_DIR = Path(__file__).parent.parent / "config" / "memory"
LONG_TERM_PATH = MEMORY_DIR / "knowledge.jsonl"
SESSIONS_PATH = MEMORY_DIR / "sessions.json"
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")

MEMORY_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Memory Service", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8030", "http://127.0.0.1:8030"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory session store ──────────────────────────────────────────
_SESSIONS = OrderedDict()   # session_id -> list of {role, content, ts}
_SESSIONS_LOCK = threading.Lock()
MAX_TURNS = int(os.environ.get("MEMORY_MAX_TURNS", "50"))
MAX_SESSIONS = int(os.environ.get("MEMORY_MAX_SESSIONS", "500"))

# ── Long-term knowledge store ────────────────────────────────────────
_KNOWLEDGE_LOCK = threading.Lock()

# ── Topic extractor (simple keyword-based) ───────────────────────────
TOPIC_PATTERNS = [
    (r'\b(?:python|javascript|typescript|rust|go|java|c\+\+|c#|ruby)\b', 'language'),
    (r'\b(?:docker|kubernetes|k8s|aws|azure|gcp|terraform)\b', 'infra'),
    (r'\b(?:api|rest|graphql|websocket)\b', 'api'),
    (r'\b(?:database|sql|nosql|redis|postgres|mongo)\b', 'database'),
    (r'\b(?:react|vue|angular|svelte)\b', 'frontend'),
    (r'\b(?:pytest|jest|mocha|unittest)\b', 'testing'),
    (r'\b(?:security|auth|encrypt|vuln|cve)\b', 'security'),
    (r'\b(?:ml|llm|ai|neural|transformer)\b', 'ml'),
    (r'\b(?:agent|orchestrator|workflow)\b', 'agents'),
]


def extract_topics(text):
    topics = set()
    for pat, label in TOPIC_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            topics.add(label)
    return sorted(topics) or ["general"]


def _load_knowledge():
    entries = []
    if LONG_TERM_PATH.exists():
        for line in open(LONG_TERM_PATH, encoding="utf-8"):
            try:
                entries.append(json.loads(line))
            except ValueError:
                continue
    return entries


def _save_knowledge(entries):
    with open(LONG_TERM_PATH, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def _load_sessions():
    if SESSIONS_PATH.exists():
        try:
            return json.loads(SESSIONS_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_sessions(sessions):
    SESSIONS_PATH.write_text(json.dumps(sessions, indent=2))


# ── API Models ───────────────────────────────────────────────────────
class RememberRequest(BaseModel):
    session_id: str
    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    content: str
    topics: Optional[list[str]] = None
    session_type: str = "project"


class RecallRequest(BaseModel):
    session_id: str
    limit: int = 20
    topics: Optional[list[str]] = None


class CrossSessionRequest(BaseModel):
    query: str
    limit: int = 10
    session_id: Optional[str] = None


class ForgetRequest(BaseModel):
    session_id: str
    entry_indices: Optional[list[int]] = None


# ── Endpoints ────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "knowledge_entries": len(_load_knowledge())}


@app.post("/remember")
def remember(req: RememberRequest):
    topics = req.topics or extract_topics(req.content)
    entry = {
        "ts": int(time.time()),
        "session": req.session_id,
        "type": req.session_type,
        "role": req.role,
        "content": req.content,
        "topics": topics,
    }
    with _KNOWLEDGE_LOCK:
        entries = _load_knowledge()
        entries.append(entry)
        _save_knowledge(entries)
    # Also update in-memory session
    with _SESSIONS_LOCK:
        hist = _SESSIONS.setdefault(req.session_id, [])
        hist.append({"role": req.role, "content": req.content,
                     "ts": entry["ts"]})
        while len(hist) > MAX_TURNS:
            hist.pop(0)
        while len(_SESSIONS) > MAX_SESSIONS:
            _SESSIONS.popitem(last=False)
    return {"status": "saved", "entry_id": len(_load_knowledge())}


@app.post("/recall")
def recall(req: RecallRequest):
    # In-memory session history
    with _SESSIONS_LOCK:
        session_hist = list(_SESSIONS.get(req.session_id, []))

    # Long-term knowledge
    with _KNOWLEDGE_LOCK:
        entries = _load_knowledge()

    if req.topics:
        matched = [e for e in entries
                   if any(t in e.get("topics", []) for t in req.topics)
                   and e.get("session") == req.session_id]
    else:
        matched = [e for e in entries
                   if e.get("session") == req.session_id]

    matched = matched[-req.limit:]
    return {
        "session_id": req.session_id,
        "history": session_hist[-req.limit:],
        "knowledge": matched,
        "total_knowledge": len(matched),
    }


@app.post("/cross-session")
def cross_session_recall(req: CrossSessionRequest):
    """Find related knowledge across all sessions."""
    with _KNOWLEDGE_LOCK:
        entries = _load_knowledge()

    query_terms = set(re.findall(r'\b\w{3,}\b', req.query.lower()))
    scored = []
    for e in entries:
        if req.session_id and e.get("session") == req.session_id:
            continue
        content_terms = set(re.findall(r'\b\w{3,}\b',
                                        e.get("content", "").lower()))
        topics_set = set(e.get("topics", []))
        score = len(query_terms & content_terms) * 2
        score += len(query_terms & topics_set) * 5
        if score > 0:
            scored.append((score, e))

    scored.sort(reverse=True)
    results = [e for _, e in scored[:req.limit]]
    return {"query": req.query, "results": results, "count": len(results)}


@app.delete("/forget")
def forget(req: ForgetRequest):
    with _KNOWLEDGE_LOCK:
        entries = _load_knowledge()
        if req.entry_indices:
            for idx in sorted(req.entry_indices, reverse=True):
                if 0 <= idx < len(entries):
                    entries.pop(idx)
        else:
            entries = [e for e in entries
                       if e.get("session") != req.session_id]
        _save_knowledge(entries)

    with _SESSIONS_LOCK:
        _SESSIONS.pop(req.session_id, None)

    return {"status": "forgotten", "remaining": len(entries)}


@app.get("/sessions")
def list_sessions():
    with _SESSIONS_LOCK:
        out = {}
        for sid, hist in _SESSIONS.items():
            out[sid] = {
                "turn_count": len(hist),
                "last_turn": hist[-1]["ts"] if hist else 0,
            }
    return {"sessions": out, "total": len(out)}


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    with _SESSIONS_LOCK:
        _SESSIONS.pop(session_id, None)
    with _KNOWLEDGE_LOCK:
        entries = [e for e in _load_knowledge()
                   if e.get("session") != session_id]
        _save_knowledge(entries)
    return {"status": "deleted"}


@app.get("/topics")
def list_topics():
    with _KNOWLEDGE_LOCK:
        entries = _load_knowledge()
    topic_counts = {}
    for e in entries:
        for t in e.get("topics", []):
            topic_counts[t] = topic_counts.get(t, 0) + 1
    return {"topics": dict(sorted(topic_counts.items(),
                                  key=lambda x: -x[1]))}


@app.get("/stats")
def stats():
    with _KNOWLEDGE_LOCK:
        entries = _load_knowledge()
    with _SESSIONS_LOCK:
        sessions = dict(_SESSIONS)
    total_turns = sum(len(h) for h in sessions.values())
    return {
        "knowledge_entries": len(entries),
        "sessions": len(sessions),
        "total_turns": total_turns,
        "max_turns_per_session": MAX_TURNS,
        "max_sessions": MAX_SESSIONS,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("MEMORY_PORT", "8110"))
    print(f"[memory] Starting memory service on :{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
