import os

LLAMA_BASE = os.environ.get("LLAMA_BASE", "http://localhost:9001")
LLAMA_COMPLETION = f"{LLAMA_BASE}/completion"

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
}
