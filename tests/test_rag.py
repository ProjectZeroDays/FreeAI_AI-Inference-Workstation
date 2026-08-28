"""Tests for rag/vector_store.py and rag/embeddings.py batch operations."""
import os
import sys
import time

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from rag.embeddings import batch_embed  # noqa: E402
from rag.vector_store import (  # noqa: E402
    LRUCache,
    VectorStore,
    CACHE_MAX_SIZE,
    CACHE_TTL_SECONDS,
)


# ── helpers ──────────────────────────────────────────────────────────

def _make_store(tmp_path) -> VectorStore:
    """Return a VectorStore backed by *tmp_path* so indexes don't leak."""
    return VectorStore(index_name="test", index_dir=tmp_path)


# ── test_batch_insert ────────────────────────────────────────────────

def test_batch_insert_fills_store(tmp_path):
    store = _make_store(tmp_path)
    entries = [
        {"doc_id": "a", "text": "alpha"},
        {"doc_id": "b", "text": "beta"},
        {"doc_id": "c", "text": "gamma"},
    ]
    n = store.batch_insert(entries)
    assert n == 3
    assert store.count() == 3


def test_batch_insert_accepts_payloads(tmp_path):
    store = _make_store(tmp_path)
    entries = [
        {"doc_id": "x", "text": "hello", "payload": {"path": "/f.py", "line": 1}},
        {"doc_id": "y", "text": "world", "payload": {"path": "/g.py", "line": 2}},
    ]
    store.batch_insert(entries)
    results = store.query("hello", top_k=2)
    assert results[0]["payload"]["path"] == "/f.py"
    assert results[0]["payload"]["line"] == 1


def test_batch_insert_empty_list(tmp_path):
    store = _make_store(tmp_path)
    n = store.batch_insert([])
    assert n == 0
    assert store.count() == 0


def test_batch_insert_persists_to_disk(tmp_path):
    store = _make_store(tmp_path)
    store.batch_insert([
        {"doc_id": "p1", "text": "persistence test"},
    ])
    # Reconstruct from disk using same index_dir
    store2 = VectorStore(index_name="test", index_dir=tmp_path)
    assert store2.count() == 1
    assert store2.query("persistence test")


# ── test_batch_query ─────────────────────────────────────────────────

def test_batch_query_returns_matching_order(tmp_path):
    store = _make_store(tmp_path)
    store.batch_insert([
        {"doc_id": "a", "text": "machine learning basics deep neural networks overview"},
        {"doc_id": "b", "text": "deep neural networks convolutional recurrent architectures"},
        {"doc_id": "c", "text": "cooking pasta italian al dente sauce recipe"},
    ])
    queries = [
        {"text": "machine learning", "top_k": 3, "threshold": -1.0},
        {"text": "cooking pasta", "top_k": 1, "threshold": -1.0},
    ]
    results = store.batch_query(queries)
    assert len(results) == 2
    # Results should be sorted by score descending
    assert results[0][0]["score"] >= results[0][1]["score"] >= results[0][2]["score"]
    assert len(results[1]) == 1


def test_batch_query_empty_queries(tmp_path):
    store = _make_store(tmp_path)
    store.batch_insert([{"doc_id": "z", "text": "only doc"}])
    results = store.batch_query([])
    assert results == []


def test_batch_query_threshold_filter(tmp_path):
    store = _make_store(tmp_path)
    store.batch_insert([
        {"doc_id": "similar", "text": "python programming language code development software engineering"},
        {"doc_id": "unrelated", "text": "banana smoothie recipe tropical fruit breakfast drink"},
    ])
    queries = [{"text": "python programming", "threshold": 0.9999}]
    results = store.batch_query(queries)
    # With very high threshold, unrelated doc should be excluded
    doc_ids = {r["doc_id"] for r in results[0]}
    assert len(doc_ids) <= 1


# ── test_result_cache ────────────────────────────────────────────────

def test_cache_hits_return_stored_result(tmp_path):
    store = _make_store(tmp_path)
    store.batch_insert([{"doc_id": "k1", "text": "cached document content here"}])
    store.query("cached document content here", top_k=5)
    first_stats = store.cache_stats
    store.query("cached document content here", top_k=5)
    second_stats = store.cache_stats
    assert second_stats["hits"] > first_stats["hits"]
    assert second_stats["misses"] >= 1


def test_cache_same_query_returns_hit(tmp_path):
    store = _make_store(tmp_path)
    store.batch_insert([{"doc_id": "d1", "text": "repeated query test"}])
    store.query("repeated query test")
    store.query("repeated query test")  # second call should hit cache
    stats = store.cache_stats
    assert stats["hits"] >= 1
    assert stats["hit_rate"] > 0


def test_cache_different_queries_differ(tmp_path):
    store = _make_store(tmp_path)
    store.batch_insert([
        {"doc_id": "a", "text": "alpha text"},
        {"doc_id": "b", "text": "beta text"},
    ])
    store.query("alpha")
    store.query("beta")
    stats = store.cache_stats
    # Two distinct queries → two cache entries, one miss per query
    assert stats["size"] == 2


def test_cache_respects_threshold_topk_in_key(tmp_path):
    store = _make_store(tmp_path)
    store.batch_insert([{"doc_id": "x", "text": "threshold test"}])
    store.query("threshold test", top_k=1)
    store.query("threshold test", top_k=5)
    stats = store.cache_stats
    # Different top_k → different cache keys
    assert stats["size"] == 2


# ── test_cache_eviction ──────────────────────────────────────────────

def test_cache_evicts_lru_when_full(tmp_path):
    store = _make_store(tmp_path)
    store.batch_insert([{"doc_id": f"d{i}", "text": f"doc number {i}"} for i in range(10)])
    cache = store._cache
    # Fill cache beyond max size
    for i in range(CACHE_MAX_SIZE + 5):
        store.query(f"doc number {i}", top_k=1)
    assert cache.size <= CACHE_MAX_SIZE
    assert cache.evictions > 0


def test_cache_eviction_removes_oldest(tmp_path):
    store = _make_store(tmp_path)
    cache = store._cache
    cache.clear()
    # Insert entries 0..CACHE_MAX_SIZE-1
    for i in range(CACHE_MAX_SIZE):
        cache.put(f"key{i}", f"value{i}")
    assert cache.size == CACHE_MAX_SIZE
    # Add one more → should evict key0 (oldest)
    cache.put(f"key{CACHE_MAX_SIZE}", "newest")
    assert cache.size == CACHE_MAX_SIZE
    assert cache.get("key0") is None
    assert cache.get(f"key{CACHE_MAX_SIZE - 1}") is not None


def test_cache_ttl_expires_entries(tmp_path):
    store = _make_store(tmp_path)
    cache = store._cache
    cache.clear()
    cache.put("ttl_key", "ttl_value")
    assert cache.get("ttl_key") == "ttl_value"
    # Manually age the entry past TTL
    import rag.vector_store as vs_mod
    # Access internal dict to shift timestamp
    key_hash = "ttl_key"
    with cache._lock:
        val, ts = cache._cache[key_hash]
        cache._cache[key_hash] = (val, ts - vs_mod.CACHE_TTL_SECONDS - 1)
    assert cache.get("ttl_key") is None
    assert cache.evictions >= 1


def test_cache_access_refreshes_ttl(tmp_path):
    store = _make_store(tmp_path)
    cache = store._cache
    cache.clear()
    cache.put("refresh_key", "refresh_value")
    # Access → refreshes internal timestamp
    cache.get("refresh_key")
    import rag.vector_store as vs_mod
    with cache._lock:
        val, ts = cache._cache["refresh_key"]
        assert time.monotonic() - ts < vs_mod.CACHE_TTL_SECONDS
    assert cache.get("refresh_key") == "refresh_value"


# ── batch_embed ──────────────────────────────────────────────────────

def test_batch_embed_returns_one_vector_per_text():
    texts = ["hello", "world", "foo"]
    vecs = batch_embed(texts)
    assert len(vecs) == 3
    assert all(len(v) == 64 for v in vecs)


def test_batch_embed_empty_input():
    assert batch_embed([]) == []


def test_batch_embed_deterministic_hash():
    texts = ["same text", "same text", "different"]
    vecs = batch_embed(texts)
    assert vecs[0] == vecs[1]  # same text → same vector
    assert vecs[0] != vecs[2]  # different text → different vector


def test_batch_embed_custom_dim():
    vecs = batch_embed(["a", "b"], dim=32)
    assert all(len(v) == 32 for v in vecs)
