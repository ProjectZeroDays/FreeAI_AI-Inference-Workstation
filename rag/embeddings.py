"""Embedding utilities with batch support.

Provides both a real-path through sentence-transformers (when available)
and a deterministic SHA256 hash fallback for offline / CI environments.
"""
import hashlib
from typing import List, Optional


def _hash_embed_single(text: str, dim: int = 64) -> List[float]:
    """Produce a deterministic pseudo-vector from a single text string."""
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vec: List[float] = []
    for i in range(0, min(len(h) * 4, dim * 4), 4):
        chunk = h[(i // 4) % len(h):(i // 4) % len(h) + 1]
        val = int.from_bytes(chunk, "big", signed=True) / (2 ** 31)
        vec.append(float(val))
    while len(vec) < dim:
        vec.append(0.0)
    return vec[:dim]


def batch_embed(texts: List[str], dim: int = 64,
                model_name: Optional[str] = None) -> List[List[float]]:
    """Embed a batch of texts into fixed-dimension vectors.

    Tries sentence-transformers first for semantic embeddings, then
    falls back to deterministic SHA256-based vectors so tests pass
    without GPU or network access.

    Parameters
    ----------
    texts : list[str]
        Texts to embed. Empty list returns empty list.
    dim : int
        Output vector dimension (default 64).
    model_name : str or None
        Optional sentence-transformers model name. Passed through when
        the library is installed; ignored when the hash fallback is used.

    Returns
    -------
    list[list[float]]
        One vector per input text, each of length *dim*.
    """
    if not texts:
        return []

    use_hash = False
    model = None
    if model_name is not None:
        try:
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415
            model = SentenceTransformer(model_name)
        except ImportError:
            use_hash = True
    else:
        use_hash = True

    if use_hash or model is None:
        return [_hash_embed_single(t, dim=dim) for t in texts]

    import numpy as np  # noqa: PLC0415
    vecs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    if vecs.ndim == 1:
        vecs = vecs.reshape(1, -1)
    result = vecs.tolist()
    # Ensure uniform dimension
    if len(result) and len(result[0]) != dim:
        trimmed = [v[:dim] if len(v) > dim else v + [0.0] * (dim - len(v))
                   for v in result]
        return trimmed
    return result
