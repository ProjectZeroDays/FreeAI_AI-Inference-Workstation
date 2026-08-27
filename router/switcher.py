from models import MODEL_REGISTRY, FALLBACK_CHAIN, FallbackChain


def select_model(task_type: str) -> dict:
    """Primary model for a task type (kept for backward compatibility)."""
    chain = FALLBACK_CHAIN.get(task_type, FALLBACK_CHAIN["general_code"])
    return MODEL_REGISTRY[chain[0]]


def select_chain(task_type: str, agent: str = None) -> list:
    """Ordered candidate list for fallback routing (returns model keys).

    Per-agent overrides (config router.model_overrides / env
    AGENT_MODEL_OVERRIDES JSON) put the overridden model first.
    """
    return [entry["key"] for entry in FallbackChain(task_type, agent).build()]


def get_chain_summary(task_type: str, agent: str = None) -> list:
    """Return the fallback chain with confidence scores for API consumers."""
    return FallbackChain(task_type, agent).build()
