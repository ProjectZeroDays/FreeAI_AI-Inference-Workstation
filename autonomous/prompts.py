"""System prompts, parsers, and verifiers for the autonomous SDLC loop."""

PLAN_PROMPT = """You are an autonomous software planner.

Task: decompose the SPEC into a minimal ordered list of implementation
tasks that together produce a complete, working project.

Respond with ONLY a JSON array, no prose, no markdown fences:
[
  {{"id": "task_1", "title": "...", "detail": "what to build",
    "files": ["relative/path.py"]}}
]

Rules:
- 1 to {max_tasks} tasks, each independently implementable.
- First task creates the project skeleton/entrypoint.
- Include a final task for README + tests where sensible.

SPEC:
{spec}"""

CODE_PROMPT = """You are an autonomous coding agent. Write COMPLETE files.

Project spec:
{spec}

Existing workspace files:
{tree}

Implement this task:
- id: {task_id}
- title: {title}
- detail: {detail}

Output format — repeat this block per file, nothing else:
=== FILE: relative/path ===
<entire file content>
=== END ===

Rules:
- Emit every file you create or modify in full; never use placeholders
  like "..." or "TODO: implement".
- Only write files for this task plus imports you must add.
- Keep code runnable and dependency-light (stdlib first)."""

FIX_PROMPT = """You are an autonomous fixing agent.

Spec:
{spec}

Current files:
{tree}

Verification findings (real command output / static analysis):
{issues}

Fix every finding. Output only blocks:
=== FILE: relative/path ===
<entire corrected file content>
=== END ==="""

DOC_PROMPT = """You are a technical writer finishing a generated project.

Spec:
{spec}

Final file tree:
{tree}

Key file excerpts:
{sample}

Write project documentation. Output only blocks:
=== FILE: README.md ===
<overview, setup, usage, architecture>
=== END ===
=== FILE: docs/API.md ===
<endpoints or module reference if applicable>
=== END ===

Omit docs/API.md block if the project has no API surface."""

REVIEW_PROMPT = """You are a strict code reviewer.

Spec:
{spec}

Generated files:
{tree}

Sample of generated code:
{sample}

First line MUST be exactly one of:
VERDICT: PASS
VERDICT: FIX

If FIX, list concrete issues after it, one per line, prefixed "- ".
"""

FILE_BLOCK_RE = r"===\s*FILE:\s*(.+?)\s*===\s*\n(.*?)\n?===\s*END\s*==="

_PLACEHOLDER_RE = None  # compiled lazily


def strip_outer_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        first_nl = t.find("\n")
        if first_nl != -1:
            t = t[first_nl + 1:]
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    return t.strip()


def parse_plan(raw: str):
    import json
    import re

    cleaned = strip_outer_fences(raw)
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if not match:
        return []
    try:
        plan = json.loads(match.group(0))
    except ValueError:
        return []
    if not isinstance(plan, list):
        return []
    tasks = []
    for i, item in enumerate(plan[:64], start=1):
        if not isinstance(item, dict) or not item.get("title"):
            continue
        tasks.append({
            "id": str(item.get("id") or f"task_{i}"),
            "title": str(item["title"]),
            "detail": str(item.get("detail", "")),
            "files": [str(f) for f in item.get("files", [])][:20],
        })
    return tasks


def parse_file_blocks(raw: str):
    import re

    cleaned = strip_outer_fences(raw)
    out = []
    seen = set()
    for m in re.finditer(FILE_BLOCK_RE, cleaned, re.DOTALL):
        path = m.group(1).strip().replace("\\", "/").lstrip("/")
        content = m.group(2)
        if path and path not in seen:
            seen.add(path)
            out.append((path, content))
    return out


def parse_verdict(raw: str):
    cleaned = strip_outer_fences(raw)
    lines = cleaned.splitlines()
    verdict = "pass"
    if lines and lines[0].strip().upper().startswith("VERDICT:"):
        verdict = "fix" if "FIX" in lines[0].upper() else "pass"
        lines = lines[1:]
    elif "VERDICT:" in cleaned.upper():
        idx = cleaned.upper().index("VERDICT:")
        head = cleaned[idx:].splitlines()[0]
        verdict = "fix" if "FIX" in head.upper() else "pass"
    issues = [ln.lstrip("- ").strip()
              for ln in lines if ln.strip().startswith("-")]
    return verdict, issues


# ---------------------------------------------------------------------
# Static verification fallback (used when shell tools are disabled)
# ---------------------------------------------------------------------

def static_issues(files, read_fn) -> list:
    """Scan generated text files for placeholders/emptiness.
    read_fn(path) -> str must be provided by caller."""
    global _PLACEHOLDER_RE
    import re

    if _PLACEHOLDER_RE is None:
        _PLACEHOLDER_RE = re.compile(
            r"^\s*(#|//|--)?\s*(TODO|FIXME|PLACEHOLDER|NOT IMPLEMENTED)\b"
            r"|^\s*(\.\.\.|<implement[^>]*>)\s*$",
            re.IGNORECASE)

    issues = []
    for f in files:
        path, size = f["path"], f["bytes"]
        if size == 0:
            issues.append(f"{path}: file is empty")
            continue
        if size > 200_000:
            continue
        try:
            body = read_fn(path)
        except OSError:
            continue
        for lineno, line in enumerate(body.splitlines(), start=1):
            if _PLACEHOLDER_RE.search(line):
                issues.append(f"{path}:{lineno}: placeholder found: "
                              f"{line.strip()[:80]}")
                if len(issues) >= 40:
                    return issues
        if body.strip() in ("", "..."):
            issues.append(f"{path}: file has no real content")
    return issues


# ---------------------------------------------------------------------
# Shell verification (real compiler/test runs inside the workspace)
# ---------------------------------------------------------------------

def detect_commands(paths) -> list:
    """Build (label, command) pairs suited to the detected stack."""
    cmds = []
    py = [p for p in paths if p.endswith(".py")]
    js = [p for p in paths if p.endswith((".js", ".mjs", ".cjs"))]

    if any(p == "package.json" for p in paths):
        pass  # npm install is networked; node --check below still applies

    if py:
        cmds.append(("python:syntax", "python3 -m compileall -q ."))
        has_tests = any(
            p.endswith(".py") and (
                p.startswith("test_")
                or "_test.py" in p
                or p.startswith(("tests/", "test/")))
            for p in paths)
        if has_tests:
            cmds.append(("python:pytest", "python3 -m pytest -q"))
            cmds.append(("python:unittest",
                         "python3 -m unittest discover -q"))

    for path in js[:10]:
        cmds.append((f"node:check:{path}", f'node --check "{path}"'))
    return cmds
