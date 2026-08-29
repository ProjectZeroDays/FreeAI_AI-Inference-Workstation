"""Qdrant RAG sidecar — vector index with filesystem watcher.

Connects to a local or remote Qdrant instance, embeds documents via
MiniLM (384-dim), and falls back to SHA256 hash-based embeddings when
sentence-transformers is unavailable.

Usage:
    python -m rag.qdrant_sidecar          # runs API on :8141
    python scripts/ingest.py --watch      # filesystem watcher mode
"""
import hashlib
import json
import os
import pathlib
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        FieldCondition,
        Filter,
        FilterSelector,
        HasIdentifierCondition,
        PointStruct,
        VectorParams,
        ScrollResult,
    )
    HAS_QDRANT = True
except ImportError:
    QdrantClient = None
    HAS_QDRANT = False

ROOT = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = ROOT / "config" / "rag.json"
DEFAULT_DOCS_DIR = ROOT / "config" / "documents"

# ---------------------------------------------------------------- config
def load_rag_config(path: pathlib.Path = None) -> Dict[str, Any]:
    cfg_path = path or DEFAULT_CONFIG_PATH
    if cfg_path.exists():
        return json.loads(cfg_path.read_text())
    return {
        "qdrant": {
            "url": os.environ.get("QDRANT_URL", "http://localhost:6333"),
            "api_key": os.environ.get("QDRANT_API_KEY", ""),
            "default_collection": "freeai_docs",
            "vector_size": 384,
            "distance": "COSINE",
        },
        "watch": {
            "docs_dir": str(ROOT / "config" / "documents"),
            "poll_interval_s": 30,
            "chunk_size": 800,
            "chunk_overlap": 120,
        },
        "embedding": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "fallback": "hash",
        },
    }


# ---------------------------------------------------------------- embedding
class Embedder:
    """MiniLM embeddings with hash fallback."""

    def __init__(self, config: Dict[str, Any]):
        self._model_name = config.get("embedding", {}).get(
            "model", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self._fallback = config.get("embedding", {}).get("fallback", "hash")
        self._use_hash = False
        self._model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        except Exception:
            self._use_hash = True
            self._model = None

    def encode(self, texts: List[str]) -> List[List[float]]:
        if self._use_hash or self._model is None:
            return self._hash_embed(texts)
        import numpy as np
        vecs = self._model.encode(texts, convert_to_numpy=True)
        if vecs.ndim == 1:
            return [vecs.tolist()]
        return vecs.tolist()

    @staticmethod
    def _hash_embed(texts: List[str], dim: int = 384) -> List[List[float]]:
        """SHA256-based fallback: produces deterministic pseudo-vectors."""
        vecs = []
        for text in texts:
            h = hashlib.sha256(text.encode("utf-8")).digest()
            vec = []
            for i in range(0, min(len(h) * 4, dim * 4), 4):
                if i + 4 <= len(h) * 4:
                    chunk = h[(i // 4) % len(h):(i // 4) % len(h) + 1]
                    val = int.from_bytes(chunk, "big", signed=True) / (2**31)
                    vec.append(float(val))
            # Pad or trim to dim
            while len(vec) < dim:
                vec.append(0.0)
            vecs.append(vec[:dim])
        return vecs


# ---------------------------------------------------------------- sidecar
class QdrantSidecar:
    """Manages a Qdrant collection for RAG document storage."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or load_rag_config()
        self.qdrant_cfg = self.config.get("qdrant", {})
        self.watch_cfg = self.config.get("watch", {})
        self._client: Optional[QdrantClient] = None
        self._embedder = Embedder(self.config)
        self._lock = threading.Lock()
        self._watcher_thread: Optional[threading.Thread] = None
        self._watching = False
        self._seen_hashes: set = set()
        if HAS_QDRANT:
            self._connect()

    def _connect(self):
        url = self.qdrant_cfg.get("url", "http://localhost:6333")
        api_key = self.qdrant_cfg.get("api_key", "")
        kwargs = {"url": url, "timeout": 10}
        if api_key:
            kwargs["api_key"] = api_key
        self._client = QdrantClient(**kwargs)
        self._ensure_collection()

    def _ensure_collection(self):
        if self._client is None:
            return
        name = self.qdrant_cfg.get("default_collection", "freeai_docs")
        try:
            self._client.get_collection(name)
            return
        except Exception:
            pass
        dim = int(self.qdrant_cfg.get("vector_size", 384))
        dist = self.qdrant_cfg.get("distance", "COSINE")
        dist_map = {"COSINE": Distance.COSINE, "EUCLID": Distance.EUCLID,
                    "DOT": Distance.DOT}
        self._client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=dist_map.get(dist, Distance.COSINE)),
        )

    @property
    def collection_name(self) -> str:
        return self.qdrant_cfg.get("default_collection", "freeai_docs")

    @property
    def client(self) -> Optional[QdrantClient]:
        return self._client

    def _point_id(self, path: str, chunk_idx: int) -> int:
        h = hashlib.sha256(f"{path}:{chunk_idx}".encode()).hexdigest()
        return int(h[:16], 16)

    def _chunk_hash(self, path: str, text: str) -> str:
        return hashlib.sha256(f"{path}:{text}".encode()).hexdigest()[:16]

    def ingest_file(self, filepath: str, recursive: bool = True) -> int:
        """Ingest a single file, returns number of chunks added."""
        if self._client is None:
            raise RuntimeError("Qdrant not available — install qdrant-client")
        fp = pathlib.Path(filepath)
        if not fp.exists():
            raise FileNotFoundError(fp)
        text = fp.read_text(encoding="utf-8", errors="ignore")
        chunks = self._chunk_text(text)
        added = 0
        with self._lock:
            for i, chunk in enumerate(chunks):
                pid = self._point_id(str(fp.resolve()), i)
                chash = self._chunk_hash(str(fp.resolve()), chunk)
                if chash in self._seen_hashes:
                    continue
                self._seen_hashes.add(chash)
                vec = self._embedder.encode([chunk])[0]
                self._client.upsert(
                    collection_name=self.collection_name,
                    points=[PointStruct(
                        id=pid,
                        vector=vec,
                        payload={
                            "path": str(fp.resolve()),
                            "text": chunk,
                            "chunk_index": i,
                            "chunk_hash": chash,
                            "ingested_at": datetime.utcnow().isoformat(),
                        },
                    )],
                )
                added += 1
        return added

    def ingest_directory(self, dirpath: str, recursive: bool = True) -> int:
        """Ingest all text/markdown/code files in a directory."""
        total = 0
        fp = pathlib.Path(dirpath)
        exts = {".md", ".txt", ".rst", ".py", ".js", ".ts", ".go", ".rs",
                ".java", ".c", ".cpp", ".h", ".json", ".yaml", ".yml",
                ".toml", ".html", ".css", ".sql", ".sh"}
        pattern = "**/*" if recursive else "*"
        for ext in exts:
            for path in fp.glob(f"{pattern}{ext}"):
                total += self.ingest_file(str(path), recursive=False)
        return total

    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
    ) -> List[Dict]:
        """Similarity search returning scored hits."""
        if self._client is None:
            raise RuntimeError("Qdrant not available")
        vec = self._embedder.encode([query])[0]
        f = None
        if filter_dict:
            conditions = []
            for k, v in filter_dict.items():
                if isinstance(v, list):
                    conditions.append(
                        FieldCondition(key=k, match=None, values=v)
                    )
                else:
                    conditions.append(
                        FieldCondition(key=k, match=None, values=[v])
                    )
            f = Filter(must=conditions)
        results = self._client.query_points(
            collection_name=self.collection_name,
            query=vec,
            limit=top_k,
            query_filter=f,
        ).points
        return [
            {
                "id": p.id,
                "path": p.payload.get("path", ""),
                "text": p.payload.get("text", ""),
                "chunk_index": p.payload.get("chunk_index", 0),
                "score": round(p.score, 4) if p.score else 0.0,
                "ingested_at": p.payload.get("ingested_at", ""),
            }
            for p in results
        ]

    def list_collections(self) -> List[Dict]:
        """List all Qdrant collections with metadata."""
        if self._client is None:
            return []
        cols = self._client.get_collections().collections
        return [{"name": c.name, "points_count": c.points_count} for c in cols]

    def delete_collection(self, name: str) -> bool:
        """Delete a collection entirely."""
        if self._client is None:
            return False
        try:
            self._client.delete_collection(collection_name=name)
            return True
        except Exception:
            raise HTTPException(status_code=404, detail=f"Collection '{name}' not found")

    def _chunk_text(self, text: str) -> List[str]:
        size = int(self.watch_cfg.get("chunk_size", 800))
        overlap = int(self.watch_cfg.get("chunk_overlap", 120))
        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

    # ── filesystem watcher ─────────────────────────────────────────
    def start_watcher(self, docs_dir: Optional[str] = None):
        """Start a background thread watching docs_dir for new/changed files."""
        if self._watcher_thread and self._watching:
            return
        self._docs_dir = pathlib.Path(docs_dir or self.watch_cfg.get("docs_dir", str(DEFAULT_DOCS_DIR)))
        self._docs_dir.mkdir(parents=True, exist_ok=True)
        self._watching = True
        self._watcher_thread = threading.Thread(
            target=self._watch_loop, daemon=True
        )
        self._watcher_thread.start()

    def stop_watcher(self):
        self._watching = False

    def _watch_loop(self):
        interval = float(self.watch_cfg.get("poll_interval_s", 30))
        exts = {".md", ".txt", ".rst", ".py", ".js", ".ts", ".go", ".rs",
                ".java", ".c", ".cpp", ".h", ".json", ".yaml", ".yml",
                ".toml", ".html", ".css", ".sql", ".sh"}
        while self._watching:
            try:
                count = 0
                for ext in exts:
                    for fp in self._docs_dir.rglob(f"*{ext}"):
                        mtime = fp.stat().st_mtime
                        key = f"{fp}:{mtime}"
                        if key not in self._seen_hashes:
                            self._seen_hashes.add(key)
                            self.ingest_file(str(fp), recursive=False)
                            count += 1
                if count:
                    print(f"[rag-sidecar] ingested {count} new/changed file(s)")
            except Exception as e:
                print(f"[rag-sidecar] watch error: {e}")
            time.sleep(interval)


# ── FastAPI app ──────────────────────────────────────────────────────
_sidecar: Optional[QdrantSidecar] = None
_sidecar_lock = threading.Lock()


def get_sidecar(config: Optional[Dict] = None) -> QdrantSidecar:
    global _sidecar
    with _sidecar_lock:
        if _sidecar is None:
            _sidecar = QdrantSidecar(config)
        return _sidecar


if HAS_FASTAPI:
    _app = FastAPI(title="Qdrant RAG Sidecar", version="1.0")
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8030", "http://127.0.0.1:8030"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class IngestRequest(BaseModel):
        path: str
        recursive: bool = True

    class SearchRequest(BaseModel):
        query: str
        top_k: int = 10
        filter: Optional[Dict[str, Any]] = None

    class WatchStartRequest(BaseModel):
        docs_dir: Optional[str] = None

    @_app.get("/health")
    def health():
        sc = get_sidecar()
        return {
            "status": "ok",
            "qdrant_connected": sc.client is not None,
            "collection": sc.collection_name,
        }

    @_app.post("/rag/ingest")
    def ingest(req: IngestRequest):
        sc = get_sidecar()
        count = sc.ingest_file(req.path, recursive=req.recursive)
        return {"status": "ingested", "chunks": count, "path": req.path}

    @_app.post("/rag/ingest/dir")
    def ingest_dir(req: IngestRequest):
        sc = get_sidecar()
        count = sc.ingest_directory(req.path, recursive=req.recursive)
        return {"status": "ingested", "chunks": count, "path": req.path}

    @_app.get("/rag/search")
    def search(req: SearchRequest = None, query: str = None, top_k: int = 10, filter: str = None):
        # Support both JSON body and query params
        q = req.query if req else (query or "")
        fk = None
        if req and req.filter:
            fk = req.filter
        elif filter:
            try:
                fk = json.loads(filter)
            except ValueError:
                fk = {"path": filter}
        if not q:
            raise HTTPException(status_code=400, detail="query is required")
        sc = get_sidecar()
        results = sc.search(q, top_k=top_k, filter_dict=fk)
        return {"query": q, "results": results, "count": len(results)}

    @_app.post("/rag/search")
    def search_post(req: SearchRequest):
        sc = get_sidecar()
        results = sc.search(req.query, top_k=req.top_k, filter_dict=req.filter)
        return {"query": req.query, "results": results, "count": len(results)}

    @_app.get("/rag/collections")
    def list_collections():
        sc = get_sidecar()
        return {"collections": sc.list_collections()}

    @_app.delete("/rag/collection/{name}")
    def delete_collection(name: str):
        sc = get_sidecar()
        sc.delete_collection(name)
        return {"status": "deleted", "collection": name}

    @_app.post("/rag/watch/start")
    def start_watch(req: WatchStartRequest = None):
        sc = get_sidecar()
        sc.start_watcher(req.docs_dir if req else None)
        return {"status": "watching", "dir": sc._docs_dir}

    @_app.post("/rag/watch/stop")
    def stop_watch():
        sc = get_sidecar()
        sc.stop_watcher()
        return {"status": "stopped"}

    app = _app
else:
    app = None


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("RAG_SIDECAR_PORT", "8141"))
    cfg = load_rag_config()
    sc = QdrantSidecar(cfg)
    docs_dir = cfg.get("watch", {}).get("docs_dir", str(DEFAULT_DOCS_DIR))
    pathlib.Path(docs_dir).mkdir(parents=True, exist_ok=True)
    print(f"[rag-sidecar] Qdrant URL: {sc.qdrant_cfg.get('url')}")
    print(f"[rag-sidecar] Collection: {sc.collection_name}")
    print(f"[rag-sidecar] Embedding: {'MiniLM' if not sc._embedder._use_hash else 'hash (fallback)'}")
    if HAS_FASTAPI and app is not None:
        print(f"[rag-sidecar] Starting API on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
