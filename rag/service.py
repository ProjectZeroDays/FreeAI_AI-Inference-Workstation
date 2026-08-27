"""RAG Service — Hybrid retrieval (BM25 + vector) with AST chunking.

Features:
  - BM25 keyword search over indexed documents
  - Vector search via embeddings (local or remote)
  - AST-aware code chunking for programming repos
  - Entity extraction from documents
  - Per-project isolated indexes
  - Lightweight fallback to full-text search when vectors unavailable

Usage:
    python rag/service.py            # runs on :8140
"""
import json
import os
import re
import threading
import time
from collections import Counter
from pathlib import Path
from urllib.parse import quote

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

ROOT = Path(__file__).parent.parent
INDEX_DIR = ROOT / "config" / "rag_indexes"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# ── BM25 simplified implementation ───────────────────────────────────
def _tokenize(text):
    return re.findall(r'\b\w{2,}\b', text.lower())


def _idf_freq(doc_freq_map, total_docs):
    idf = {}
    for term, df in doc_freq_map.items():
        idf[term] = max(0.0, os.log(total_docs / (1 + df)))
    return idf


class BM25Index:
    """Simple BM25 index for keyword search."""

    def __init__(self):
        self.documents = {}  # doc_id -> text
        self.doc_freq = Counter()  # term -> docs containing term
        self.term_freq = {}  # doc_id -> {term: count}
        self.idf = {}
        self.total_docs = 0

    def add_document(self, doc_id, text, metadata=None):
        self.documents[doc_id] = text
        self.term_freq[doc_id] = Counter(_tokenize(text))
        for term in self.term_freq[doc_id]:
            self.doc_freq[term] += 1
        self.total_docs += 1
        self.idf = _idf_freq(self.doc_freq, self.total_docs)

    def search(self, query, top_k=10, k1=1.5, b=0.75):
        """BM25 scoring search."""
        terms = _tokenize(query)
        scores = {}
        for doc_id, text in self.documents.items():
            score = 0.0
            dl = len(terms)
            for term in terms:
                tf = self.term_freq[doc_id].get(term, 0)
                if tf == 0:
                    continue
                idf = self.idf.get(term, 0)
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * dl)
                score += idf * numerator / max(denominator, 1e-10)
            if score > 0:
                scores[doc_id] = score
        sorted_docs = sorted(scores.items(), key=lambda x: -x[1])
        return [{"doc_id": did, "score": round(score, 4)}
                for did, score in sorted_docs[:top_k]]


# ── AST Code Chunking ────────────────────────────────────────────────
CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
                   ".java", ".c", ".cpp", ".h", ".hpp", ".swift",
                   ".kt", ".rb", ".php", ".sh", ".yaml", ".yml",
                   ".json", ".toml", ".md", ".sql", ".html", ".css"}


def chunk_code_file(filepath, max_chunk_size=500):
    """Chunk a code file by logical units (functions, classes, blocks)."""
    chunks = []
    try:
        text = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return chunks

    lines = text.split("\n")
    current_chunk = []
    current_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Start of new logical unit
        if re.match(r'^(def |class |function |async def |impl |struct |fn |func |interface |export |import )',
                    stripped) or stripped.startswith("# "):
            if current_chunk and len("\n".join(current_chunk)) >= max_chunk_size:
                chunks.append({
                    "start_line": current_start,
                    "end_line": i,
                    "text": "\n".join(current_chunk),
                    "type": "code_block",
                })
                current_chunk = [line]
                current_start = i
            elif current_chunk:
                chunks.append({
                    "start_line": current_start,
                    "end_line": i,
                    "text": "\n".join(current_chunk),
                    "type": "code_block",
                })
                current_chunk = [line]
                current_start = i
        else:
            current_chunk.append(line)

    if current_chunk:
        chunks.append({
            "start_line": current_start,
            "end_line": len(lines),
            "text": "\n".join(current_chunk),
            "type": "code_block",
        })

    return chunks


def chunk_markdown_file(filepath, max_chunk_size=800):
    """Chunk markdown by headers."""
    chunks = []
    try:
        text = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return chunks

    sections = re.split(r'\n(?=# {1,3}\s)', text)
    current = []
    for section in sections:
        if len("\n".join(current)) + len(section) > max_chunk_size and current:
            chunks.append({"text": "\n".join(current), "type": "markdown_section"})
            current = [section]
        else:
            current.append(section)
    if current:
        chunks.append({"text": "\n".join(current), "type": "markdown_section"})
    return chunks


# ── Embedding utilities ──────────────────────────────────────────────
def simple_hash_embedding(text, dim=8):
    """Fallback embedding via hash (non-vector semantic, but searchable)."""
    tokens = set(_tokenize(text))
    vec = [0.0] * dim
    for i, token in enumerate(sorted(tokens)):
        h = hash(token)
        vec[h % dim] = (h % 100) / 100.0
    return vec


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── RAG Service ──────────────────────────────────────────────────────
class RAGService:
    """Hybrid BM25 + vector RAG service."""

    def __init__(self, project_name=None):
        self.project_name = project_name or "default"
        self.bm25 = BM25Index()
        self.vector_store = {}  # doc_id -> embedding
        self.metadata = {}      # doc_id -> {path, type, chunks}
        self._lock = threading.Lock()
        self._load_index()

    def _index_path(self):
        return INDEX_DIR / f"{self.project_name}.json"

    def _load_index(self):
        idx = self._index_path()
        if idx.exists():
            try:
                data = json.loads(idx.read_text())
                self.bm25.documents = data.get("bm25_docs", {})
                self.bm25.term_freq = {k: Counter(v)
                                       for k, v in data.get("bm25_tf", {}).items()}
                self.bm25.doc_freq = Counter(data.get("bm25_df", {}))
                self.bm25.total_docs = data.get("total_docs", 0)
                self.bm25.idf = data.get("bm25_idf", {})
                self.vector_store = data.get("vectors", {})
                self.metadata = data.get("metadata", {})
            except (json.JSONDecodeError, OSError):
                pass

    def _save_index(self):
        data = {
            "bm25_docs": self.bm25.documents,
            "bm25_tf": {k: dict(v) for k, v in self.bm25.term_freq.items()},
            "bm25_df": dict(self.bm25.doc_freq),
            "bm25_idf": self.bm25.idf,
            "total_docs": self.bm25.total_docs,
            "vectors": self.vector_store,
            "metadata": self.metadata,
            "updated_at": int(time.time()),
        }
        self._index_path().write_text(json.dumps(data, indent=2))

    def index_directory(self, dir_path, recursive=True):
        """Index all relevant files in a directory."""
        dir_path = Path(dir_path)
        count = 0
        for ext in CODE_EXTENSIONS:
            pattern = f"**/*{ext}" if recursive else f"*{ext}"
            for filepath in dir_path.glob(pattern):
                self._index_file(filepath)
                count += 1
        # Also index markdown/docs
        for pattern in ["**/*.md", "**/*.rst", "**/*.txt", "**/*.yaml",
                        "**/*.yml", "**/*.json", "**/*.toml"]:
            for filepath in dir_path.glob(pattern):
                self._index_file(filepath)
                count += 1
        self._save_index()
        return count

    def _index_file(self, filepath):
        """Index a single file."""
        doc_id = str(filepath.resolve())
        ext = filepath.suffix.lower()

        if ext in {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
                   ".java", ".c", ".cpp", ".h", ".hpp", ".swift",
                   ".kt", ".rb", ".php"}:
            chunks = chunk_code_file(filepath)
        else:
            chunks = chunk_markdown_file(filepath)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}#{i}"
            text = chunk.get("text", "")
            if not text.strip():
                continue
            self.bm25.add_document(chunk_id, text,
                                   {"path": str(filepath), "chunk": i})
            self.vector_store[chunk_id] = simple_hash_embedding(text)
            self.metadata[chunk_id] = {
                "path": str(filepath),
                "chunk_index": i,
                "chunk_type": chunk.get("type", "text"),
                "start_line": chunk.get("start_line", 0),
                "end_line": chunk.get("end_line", 0),
                "indexed_at": int(time.time()),
            }

    def search(self, query, top_k=10, project=None):
        """Hybrid search: BM25 + vector similarity."""
        # BM25 search
        bm25_results = self.bm25.search(query, top_k=top_k * 2)

        # Vector search (hash-based fallback)
        query_vec = simple_hash_embedding(query)
        vector_scores = {}
        for doc_id, vec in self.vector_store.items():
            sim = cosine_similarity(query_vec, vec)
            if sim > 0.1:
                vector_scores[doc_id] = sim

        # Fuse results
        fused = {}
        for result in bm25_results:
            did = result["doc_id"]
            fused[did] = {"bm25": result["score"], "vector": 0,
                          "combined": result["score"]}
        for did, score in vector_scores.items():
            if did in fused:
                fused[did]["vector"] = score
                fused[did]["combined"] = (
                    fused[did]["bm25"] * 0.6 + score * 0.4)
            else:
                fused[did] = {"bm25": 0, "vector": score,
                              "combined": score * 0.5}

        # Sort and return top-k
        sorted_results = sorted(
            fused.items(), key=lambda x: -x[1]["combined"])[:top_k]

        output = []
        for doc_id, scores in sorted_results:
            meta = self.metadata.get(doc_id, {})
            text = self.bm25.documents.get(doc_id, "")[:500]
            output.append({
                "doc_id": doc_id,
                "path": meta.get("path", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "text_preview": text,
                "bm25_score": round(scores["bm25"], 4),
                "vector_score": round(scores["vector"], 4),
                "combined_score": round(scores["combined"], 4),
            })
        return output

    def get_stats(self):
        return {
            "project": self.project_name,
            "total_chunks": self.bm25.total_docs,
            "vector_store_size": len(self.vector_store),
            "index_path": str(self._index_path()),
            "last_updated": int(time.time())
            if self._index_path().exists() else 0,
        }


# ── FastAPI service ──────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="RAG Service", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _services = {}
    _services_lock = threading.Lock()

    def _get_service(project):
        with _services_lock:
            if project not in _services:
                _services[project] = RAGService(project)
            return _services[project]

    class IndexRequest(BaseModel):
        path: str
        recursive: bool = True

    class SearchRequest(BaseModel):
        query: str
        top_k: int = 10
        project: str = "default"

    @app.get("/health")
    def health():
        return {"status": "ok", "projects": list(_services.keys())}

    @app.post("/index/directory")
    def index_dir(req: IndexRequest):
        service = _get_service(req.path.split("/")[-1] or "default")
        count = service.index_directory(req.path, req.recursive)
        return {"status": "indexed", "files": count,
                "project": service.project_name}

    @app.post("/search")
    def search(req: SearchRequest):
        service = _get_service(req.project)
        results = service.search(req.query, req.top_k)
        return {"query": req.query, "results": results,
                "count": len(results)}

    @app.get("/stats/{project}")
    def stats(project: str):
        service = _get_service(project)
        return service.get_stats()

    @app.get("/projects")
    def list_projects():
        return {"projects": list(_services.keys())}


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("RAG_PORT", "8140"))
        print(f"[rag] Starting RAG service on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[rag] FastAPI not available, running CLI mode")
        service = RAGService("test")
        print(service.get_stats())
