"""Load balancing across parallel model instances (ROADMAP 2)."""
import random, os
from models import MODEL_REGISTRY, _llama_bases

STRATEGY = os.environ.get("LB_STRATEGY", "round_robin")
_rr_idx = 0

def pick_backend(task_type, agent=None):
    from switcher import select_chain
    chain = select_chain(task_type, agent)
    # If multiple llama shards healthy, spread across them
    if STRATEGY == "round_robin" and len(_llama_bases) > 1:
        global _rr_idx
        _rr_idx = (_rr_idx + 1) % len(_llama_bases)
        # annotate chosen base for caller
        return chain, _llama_bases[_rr_idx]
    if STRATEGY == "least_latency":
        # placeholder: pick first (metrics-driven selection lives in router metrics)
        return chain, _llama_bases[0]
    if STRATEGY == "random":
        return chain, random.choice(_llama_bases)
    return chain, _llama_bases[0]
