"""Long-term memory store (ROADMAP 3) � Qdrant-backed with fallback to JSONL."""
import os, json, pathlib, time

STORE = pathlib.Path(__file__).parent.parent / "config" / "memory.jsonl"
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")

def remember_long(session_id, role, content, embed=None):
    entry = {"ts": int(time.time()), "session": session_id, "role": role, "content": content}
    # Try Qdrant if available
    try:
        import requests
        # Use hash embedding fallback if no embed model
        vec = embed or [hash(content) % 100 / 100.0] * 8
        requests.post(f"{QDRANT_URL}/collections/memory/points", json={"points": [{"id": hash(str(entry)), "vector": vec, "payload": entry}]}, timeout=2)
        return
    except: pass
    STORE.parent.mkdir(parents=True, exist_ok=True)
    with open(STORE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def recall_long(session_id, limit=20):
    try:
        import requests
        r = requests.post(f"{QDRANT_URL}/collections/memory/points/scroll", json={"filter": {"must": [{"key": "session", "match": {"value": session_id}}]}, "limit": limit}, timeout=2)
        if r.ok:
            return [p["payload"] for p in r.json().get("result", {}).get("points", [])]
    except: pass
    if not STORE.exists(): return []
    out=[]
    for line in open(STORE, encoding="utf-8"):
        try:
            e=json.loads(line)
            if e.get("session")==session_id: out.append(e)
        except: pass
    return out[-limit:]
