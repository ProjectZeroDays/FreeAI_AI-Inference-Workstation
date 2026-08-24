def classify_task(prompt: str) -> str:
    p = prompt.lower()

    # Full project / production tasks
    if any(x in p for x in [
        "build", "create project", "scaffold", "production",
        "microservice", "api", "full codebase", "ci/cd",
        "docker", "kubernetes", "infrastructure"
    ]):
        return "full_project"

    # Debugging / refactoring / patching
    if any(x in p for x in [
        "fix", "refactor", "debug", "patch", "optimize",
        "clean up", "improve", "rewrite"
    ]):
        return "refactor"

    # Deep reasoning / explanation
    if any(x in p for x in [
        "explain", "why", "how does", "analyze",
        "think step by step", "reason", "break down"
    ]):
        return "analysis"

    # Default -> coding
    return "general_code"
