def classify_task(prompt: str):
    """Classify a prompt and return (task_type, confidence).

    Confidence is a rough 0..1 score based on how many signals matched.
    """
    p = prompt.lower()

    project_hits = [x for x in [
        "build", "create project", "scaffold", "production",
        "microservice", "api", "full codebase", "ci/cd",
        "docker", "kubernetes", "infrastructure"
    ] if x in p]
    if project_hits:
        conf = min(1.0, 0.4 + 0.15 * len(project_hits))
        return "full_project", round(conf, 2)

    refactor_hits = [x for x in [
        "fix", "refactor", "debug", "patch", "optimize",
        "clean up", "improve", "rewrite"
    ] if x in p]
    if refactor_hits:
        conf = min(1.0, 0.4 + 0.15 * len(refactor_hits))
        return "refactor", round(conf, 2)

    analysis_hits = [x for x in [
        "explain", "why", "how does", "analyze",
        "think step by step", "reason", "break down"
    ] if x in p]
    if analysis_hits:
        conf = min(1.0, 0.4 + 0.15 * len(analysis_hits))
        return "analysis", round(conf, 2)

    return "general_code", 0.5
