from models import MODEL_REGISTRY


def select_model(task_type: str) -> dict:
    if task_type == "full_project":
        return MODEL_REGISTRY["qwen3.6-12b"]

    if task_type == "refactor":
        return MODEL_REGISTRY["moe-13b"]

    if task_type == "analysis":
        return MODEL_REGISTRY["qwen3.5-9b"]

    # Default -> strongest coder
    return MODEL_REGISTRY["qwen3.6-12b"]
