#!/usr/bin/env python3
"""Qdrant ingest — chunks docs/ + README, embeds via local MiniLM, upserts."""
import argparse
import hashlib
import os
import pathlib
import time

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    QdrantClient = None

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = "tokugawa_docs"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    out = []
    i = 0
    while i < len(text):
        out.append(text[i:i+size])
        i += size - overlap
    return out

def embed(texts):
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return model.encode(texts).tolist()
    except Exception:
        # fallback: hash-based toy vectors for CI without model download
        import hashlib, struct
        vecs = []
        for t in texts:
            h = hashlib.sha256(t.encode()).digest()
            vecs.append([struct.unpack("f", h[i:i+4])[0] for i in range(0, 32, 4)])
        return vecs

def ensure_collection(client):
    try:
        client.get_collection(COLLECTION)
    except Exception:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

def ingest_once(docs_root):
    if QdrantClient is None:
        print("qdrant-client not installed, skipping")
        return 0
    client = QdrantClient(url=QDRANT_URL, timeout=10)
    ensure_collection(client)
    count = 0
    for path in pathlib.Path(docs_root).rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for idx, chunk in enumerate(chunk_text(text)):
            vec = embed([chunk])[0]
            pid = int(hashlib.sha256(f"{path}:{idx}".encode()).hexdigest()[:12], 16)
            client.upsert(collection_name=COLLECTION,
                          points=[PointStruct(id=pid, vector=vec,
                                              payload={"path": str(path), "text": chunk[:2000]})])
            count += 1
    print(f"ingested {count} chunks into {COLLECTION}")
    return count

def query(q, top_k=5):
    client = QdrantClient(url=QDRANT_URL, timeout=10)
    vec = embed([q])[0]
    return client.query_points(collection_name=COLLECTION, query=vec, limit=top_k).points

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true", help="loop every 60s")
    ap.add_argument("--query", help="one-off query")
    args = ap.parse_args()
    if args.query:
        for p in query(args.query):
            print(p.payload["path"], p.score)
    elif args.watch:
        while True:
            try:
                ingest_once("/app/docs")
            except Exception as e:
                print("ingest error", e)
            time.sleep(60)
    else:
        ingest_once("/app/docs")
