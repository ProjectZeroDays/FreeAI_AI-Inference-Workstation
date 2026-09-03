import os
from typing import Dict, List, Optional

try:
    from .settings import load_config
except ImportError:
    from settings import load_config

_CFG = load_config()
LLAMA_BASE = _CFG.get("router", {}).get(
    "llama_base", os.environ.get("LLAMA_BASE", "http://localhost:9001"))
LLAMA2_BASE = os.environ.get("LLAMA2_BASE", "http://localhost:9003")
_llama_bases = [b.rstrip("/") for b in os.environ.get(
    "LLAMA_BASES", f"{LLAMA_BASE},{LLAMA2_BASE}").split(",") if b.strip()]
LLAMA_COMPLETION = f"{LLAMA_BASE}/completion"
LLAMA2_COMPLETION = f"{LLAMA2_BASE}/completion"

# Strength-to-category mapping for confidence scoring
_STRENGTH_DOMAINS = {
    "architecture": "code",
    "full_project": "code",
    "production_code": "code",
    "multi_file": "code",
    "api_design": "code",
    "microservices": "code",
    "ci_cd": "code",
    "infrastructure": "code",
    "refactor": "code",
    "debug": "code",
    "fix_code": "code",
    "patch": "code",
    "optimize": "code",
    "incremental": "code",
    "fast_completion": "code",
    "coding_agent": "code",
    "tool_calling": "code",
    "coding": "code",
    "analysis": "analysis",
    "explain": "analysis",
    "think_step_by_step": "analysis",
    "planning": "analysis",
    "decomposition": "analysis",
    "logic": "analysis",
    "deep_reasoning": "analysis",
    "long_context": "analysis",
    "function_calling": "analysis",
    "math": "analysis",
    "vision": "creative",
    "creative": "creative",
    "general": "creative",
    "terminal_agent": "creative",
    "chat": "creative",
}

# Task-type to domain label
_TASK_DOMAIN = {
    "full_project": "code",
    "refactor": "code",
    "analysis": "analysis",
    "general_code": "code",
}


class ConfidenceScorer:
    """Rate each model's suitability per task type based on strength overlap.

    Returns a dict of {model_key: score} where score is 0.0-1.0.
    A model with no matching strengths scores 0.0; a model whose
    strengths fully align with the task domain scores up to 1.0.
    """

    def score(self, model_key: str, task_type: str) -> float:
        model = MODEL_REGISTRY.get(model_key)
        if not model:
            return 0.0
        strengths = model.get("strengths", [])
        if not strengths:
            return 0.0
        domain = _TASK_DOMAIN.get(task_type, "code")
        domain_hits = sum(
            1 for s in strengths if _STRENGTH_DOMAINS.get(s) == domain
        )
        # Bonus for exact-match strength keywords (up to +0.15)
        exact_hits = sum(
            1 for s in strengths if s in (
                "full_project", "refactor", "analysis", "general_code",
                "deep_reasoning", "production_code", "coding_agent",
            )
        )
        base = domain_hits / max(len(strengths), 1)
        bonus = min(0.15, 0.03 * exact_hits)
        return round(min(1.0, base + bonus), 2)

    def scores_for_task(self, task_type: str) -> Dict[str, float]:
        """Return {model_key: confidence_score} sorted descending."""
        scores = {
            key: self.score(key, task_type)
            for key in MODEL_REGISTRY
        }
        return dict(sorted(scores.items(), key=lambda kv: -kv[1]))


class FallbackChain:
    """Ordered list of models to try in sequence for a given task type.

    Uses FALLBACK_CHAIN as the base order, optionally prepends a
    per-agent override, and annotates each entry with its confidence
    score for the task type.
    """

    def __init__(self, task_type: str, agent: Optional[str] = None):
        self.task_type = task_type
        self.agent = agent
        self.scorer = ConfidenceScorer()

    def build(self) -> List[Dict]:
        """Return list of {key, confidence} sorted by confidence desc,
        with agent override forced to the front if configured."""
        override = self._load_override()
        chain = list(FALLBACK_CHAIN.get(
            self.task_type, FALLBACK_CHAIN["general_code"]))
        if override and override in MODEL_REGISTRY:
            if override in chain:
                chain.remove(override)
            chain.insert(0, override)
        out = []
        for key in chain:
            if key in MODEL_REGISTRY:
                out.append({
                    "key": key,
                    "confidence": self.scorer.score(key, self.task_type),
                })
        return out

    def _load_override(self) -> Optional[str]:
        try:
            cfg = load_config().get("router", {}).get("model_overrides", {})
            if self.agent and self.agent in cfg:
                return cfg[self.agent]
        except Exception:
            pass
        return None


MODEL_REGISTRY = {
    "qwen3.6-12b": {
        "id": "qwen3.6-12b-iq-ultra-heretic-uncensored-thinking",
        "name": "Qwen3.6 12B IQ Ultra Heretic Uncensored Thinking",
        "role": "primary_coder",
        "strengths": [
            "architecture", "full_project", "production_code",
            "multi_file", "api_design", "microservices",
            "ci_cd", "infrastructure", "deep_reasoning"
        ],
        "endpoint": LLAMA_COMPLETION,
    },
    "moe-13b": {
        "id": "l3.1-moe-2x8b-deepseek-deephermes-e32-uncensored-abliterated",
        "name": "L3.1 MOE 2x8B DeepSeek DeepHermes e32 Abliterated",
        "role": "fast_coder",
        "strengths": [
            "refactor", "debug", "fix_code",
            "patch", "optimize", "incremental",
            "fast_completion"
        ],
        "endpoint": LLAMA_COMPLETION,
    },
    "qwen3.5-9b": {
        "id": "qwen3.5-9b-claude-highiq-heretic-uncensored",
        "name": "Qwen3.5 9B Claude HighIQ Heretic Uncensored",
        "role": "reasoning_specialist",
        "strengths": [
            "analysis", "explain", "think_step_by_step",
            "planning", "decomposition", "logic"
        ],
        "endpoint": LLAMA_COMPLETION,
    },
    "qwythos-9b": {
        "id": "qwythos-9b-claude-mythos-5-1m",
        "name": "Qwythos 9B Claude Mythos 5 1M (empero-ai)",
        "role": "reasoning_specialist",
        "strengths": [
            "deep_reasoning", "analysis", "planning",
            "long_context", "function_calling", "vision",
            "math", "logic"
        ],
        "endpoint": LLAMA_COMPLETION,
        # reasoning model: <think> blocks; temp <= 0.3 causes repetition
        "min_temperature": 0.6,
        "context": 1048576,
    },
    "qwythos-v2": {
        "id": "qwythos-9b-v2",
        "name": "Qwythos 9B v2 (empero-ai, FTPO loop-fix)",
        "role": "reasoning_specialist",
        "strengths": [
            "deep_reasoning", "analysis", "planning",
            "long_context", "function_calling", "vision",
            "math", "logic"
        ],
        "endpoint": LLAMA_COMPLETION,
        "min_temperature": 0.6,
        "context": 1048576,
    },
    "claude-code-9b": {
        "id": "qwen3.5-9b-claude-code",
        "name": "CodeClawd - Qwen3.5 9B Claude Code (empero-ai)",
        "role": "code_specialist",
        "strengths": [
            "coding_agent", "tool_calling", "multi_file",
            "refactor", "debug", "production_code"
        ],
        "endpoint": LLAMA_COMPLETION,
        "min_temperature": 0.6,
    },
    "qwable-9b": {
        "id": "qwable-9b-claude-fable-5",
        "name": "Qwable 9B Claude Fable 5 (empero-ai, multimodal)",
        "role": "general_assistant",
        "strengths": [
            "general", "vision", "coding", "creative",
            "terminal_agent", "chat"
        ],
        "endpoint": LLAMA_COMPLETION,
        "min_temperature": 0.6,
    },
    "qwen3.5-thinking": {
        "id": "qwen3.5-9b-claude-4.6-highiq-thinking-heretic",
        "name": "Qwen3.5 9B Claude 4.6 HighIQ THINKING Heretic (i1)",
        "role": "reasoning_fallback",
        "strengths": [
            "analysis", "think_step_by_step", "planning", "logic"
        ],
        "endpoint": LLAMA_COMPLETION,
        "min_temperature": 0.6,
    },
}

# Fallback order per task: primary first, then alternates.
FALLBACK_CHAIN = {
    "full_project": ["qwen3.6-12b", "claude-code-9b", "qwythos-v2", "moe-13b"],
    "refactor": ["claude-code-9b", "moe-13b", "qwen3.6-12b", "qwythos-v2"],
    "analysis": ["qwythos-v2", "qwythos-9b", "qwen3.5-thinking",
                 "qwen3.5-9b"],
    "general_code": ["qwen3.6-12b", "qwable-9b", "claude-code-9b",
                     "moe-13b"],
}
