"""In-memory vector store with batch operations and LRU result cache."""
import hashlib
import json
import time
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

INDEX_DIR = Path(__file__).parent.parent / "config" / "rag_indexes"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

CACHE_MAX_SIZE = 256
CACHE_TTL_SECONDS = 300


class LRUCache:
    """LRU cache with TTL per entry. Tracks evictions for observability."""

    def __init__(self, max_size: int = CACHE_MAX_SIZE, ttl: int = CACHE_TTL_SECONDS):
        self._max_size = max_size
        self._ttl = ttl
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            value, ts = self._cache[key]
            if time.monotonic() - ts > self._ttl:
                del self._cache[key]
                self.evictions += 1
                self.misses += 1
                return None
            self._cache.move_to_end(key)
            self.hits += 1
            return value

    def put(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self._cache:
                self._cache[key] = (value, time.monotonic())
                self._cache.move_to_end(key)
                return
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
                self.evictions += 1
            self._cache[key] = (value, time.monotonic())

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    @property
    def stats(self) -> Dict[str, int]:
        with self._lock:
            return {
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "size": len(self._cache),
                "hit_rate": round(self.hits / max(1, self.hits + self.misses), 4),
            }


class VectorStore:
    """Simple in-memory vector store with persistence and batch operations."""

    def __init__(self, index_name: str = "default", index_dir: Optional[Path] = None):
        self.index_name = index_name
        self._index_dir = index_dir or INDEX_DIR
        self._vectors: Dict[str, List[float]] = {}
        self._payloads: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._cache = LRUCache(max_size=CACHE_MAX_SIZE, ttl=CACHE_TTL_SECONDS)
        self._load()

    def _path(self) -> Path:
        return self._index_dir / f"{self.index_name}.json"

    def _load(self) -> None:
        p = self._path()
        if not p.exists():
            return
        try:
            data = json.loads(p.read_text())
            self._vectors = {k: v for k, v in data.get("vectors", {}).items()}
            self._payloads = data.get("payloads", {})
        except (json.JSONDecodeError, OSError):
            self._vectors = {}
            self._payloads = {}

    def _save(self) -> None:
        data = {
            "vectors": self._vectors,
            "payloads": self._payloads,
            "updated_at": int(time.time()),
        }
        self._path().write_text(json.dumps(data, indent=2))

    @staticmethod
    def _hash_embed(text: str, dim: int = 64) -> List[float]:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = []
        for i in range(0, min(len(h) * 4, dim * 4), 4):
            chunk = h[(i // 4) % len(h):(i // 4) % len(h) + 1]
            val = int.from_bytes(chunk, "big", signed=True) / (2 ** 31)
            vec.append(float(val))
        while len(vec) < dim:
            vec.append(0.0)
        return vec[:dim]

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(y * y for y in b) ** 0.5
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def insert(self, doc_id: str, text: str, payload: Optional[Dict[str, Any]] = None) -> None:
        with self._lock:
            self._vectors[doc_id] = self._hash_embed(text)
            self._payloads[doc_id] = payload or {}
        self._save()

    def batch_insert(self, entries: List[Dict[str, Any]]) -> int:
        """Insert multiple (doc_id, text, payload) entries atomically.

        Each entry is a dict with keys: doc_id (str), text (str),
        and optionally payload (dict). Returns count inserted.
        """
        count = 0
        with self._lock:
            for entry in entries:
                doc_id = entry["doc_id"]
                text = entry["text"]
                payload = entry.get("payload")
                self._vectors[doc_id] = self._hash_embed(text)
                self._payloads[doc_id] = payload or {}
                count += 1
            self._save()
        return count

    def query(self, text: str, top_k: int = 10, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Single-text similarity search with LRU result cache."""
        cache_key = hashlib.sha256(f"{text}:{top_k}:{threshold}".encode()).hexdigest()
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        query_vec = self._hash_embed(text)
        results = []
        with self._lock:
            for doc_id, vec in self._vectors.items():
                sim = self._cosine(query_vec, vec)
                if sim >= threshold:
                    results.append({
                        "doc_id": doc_id,
                        "score": round(sim, 4),
                        "payload": dict(self._payloads.get(doc_id, {})),
                    })
        results.sort(key=lambda r: -r["score"])
        results = results[:top_k]
        self._cache.put(cache_key, results)
        return results

    def batch_query(self, queries: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Batch query multiple texts. Each query is a dict with keys:

        - text (str): query string
        - top_k (int, optional): number of results
        - threshold (float, optional): minimum cosine similarity

        Returns a list of result lists, same order as input.
        """
        all_results: List[List[Dict[str, Any]]] = []
        for q in queries:
            results = self.query(
                text=q["text"],
                top_k=q.get("top_k", 10),
                threshold=q.get("threshold", 0.0),
            )
            all_results.append(results)
        return all_results

    def delete(self, doc_id: str) -> bool:
        with self._lock:
            if doc_id in self._vectors:
                del self._vectors[doc_id]
                del self._payloads[doc_id]
                self._save()
                return True
        return False

    def count(self) -> int:
        with self._lock:
            return len(self._vectors)

    @property
    def cache_stats(self) -> Dict[str, Any]:
        return self._cache.stats
