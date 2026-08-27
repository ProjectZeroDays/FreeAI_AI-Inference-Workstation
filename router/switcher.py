from models import MODEL_REGISTRY, FALLBACK_CHAIN


def select_model(task_type: str) -> dict:
    """Primary model for a task type (kept for backward compatibility)."""
    chain = FALLBACK_CHAIN.get(task_type, FALLBACK_CHAIN["general_code"])
    return MODEL_REGISTRY[chain[0]]


def select_chain(task_type: str, agent: str = None) -> list:
    """Ordered candidate list for fallback routing.

    Per-agent overrides (config router.model_overrides / env
    AGENT_MODEL_OVERRIDES JSON) put the overridden model first.
    """
    chain = list(FALLBACK_CHAIN.get(task_type, FALLBACK_CHAIN["general_code"]))

    override = None
    if agent:
        cfg = _load_overrides()
        override = cfg.get(agent)
    if override and override in MODEL_REGISTRY:
        if override in chain:
            chain.remove(override)
        chain.insert(0, override)
    return chain


def _load_overrides() -> dict:
    try:
        from settings import load_config
        return load_config().get("router", {}).get("model_overrides", {}) or {}
    except Exception:
        return {}
