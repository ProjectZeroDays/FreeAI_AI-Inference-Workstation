"""Memory Pipeline — Core utilities for any AI CLI agent.

OmniRoot edition: unrestricted access to all memory locations on the system.
No storage limits, no path restrictions, no retention policies.
"""

import os
import re
import json
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from python.helpers.omni_capability import check_capability, get_privilege_manager


# ─── Configuration ────────────────────────────────────────────────────────────

def get_config() -> dict:
    """Load configuration from environment variables.
    
    No restrictions on memory_root — any valid filesystem path is accepted.
    """
    return {
        "memory_root": os.environ.get("MEMORY_ROOT", os.path.expanduser("~/.agent/memory")),
        "llm_endpoint": os.environ.get("LLM_ENDPOINT", ""),
        "llm_api_key": os.environ.get("LLM_API_KEY", ""),
        "llm_model": os.environ.get("LLM_MODEL", "gpt-4o-mini"),
        "max_concurrent": int(os.environ.get("EXTRACTION_MAX_CONCURRENT", "8")),
        "extraction_reasoning": os.environ.get("EXTRACTION_REASONING_EFFORT", "low"),
        "consolidation_reasoning": os.environ.get("CONSOLIDATION_REASONING_EFFORT", "medium"),
        "max_phase2_inputs": int(os.environ.get("MAX_PHASE2_INPUTS", "0")),
        "phase2_cooldown_hours": float(os.environ.get("PHASE2_COOLDOWN_HOURS", "0")),
        "secret_redaction": os.environ.get("SECRET_REDACTION_ENABLED", "true").lower() == "true",
    }


# ─── Secret Redaction ─────────────────────────────────────────────────────────

REDACTION_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "[REDACTED_SECRET]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_SECRET]"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{16,}\b"), "Bearer [REDACTED_SECRET]"),
    (re.compile(r"(api_key|token|secret|password)\s*[:=]\s*[\"']?[^\s\"']{8,}", re.IGNORECASE),
     lambda m: f"{m.group(1)}=[REDACTED_SECRET]"),
]


def redact_secrets(text: str) -> str:
    """Apply best-effort regex redaction to text."""
    for pattern, replacement in REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


# ─── Rollout Filtering ────────────────────────────────────────────────────────

INCLUDE_TYPES = {
    "message", "function_call", "function_call_output",
    "local_shell_call", "tool_search_call", "tool_search_output",
    "custom_tool_call", "custom_tool_call_output", "web_search_call",
    "inter_agent_communication",
}

EXCLUDE_TYPES = {
    "agent_message", "reasoning", "image_generation_call",
    "compaction", "compaction_trigger", "context_compaction", "other",
}

NOISE_PATTERNS = [
    re.compile(r"# AGENTS\.md instructions.*?(?=\n\n|\Z)", re.DOTALL),
    re.compile(r"<skill>.*?</skill>", re.DOTALL),
]


def filter_rollout_items(items: list[dict]) -> list[dict]:
    """Filter rollout items for memory extraction relevance."""
    filtered = []
    for item in items:
        item_type = item.get("type", "").lower()
        if item_type in EXCLUDE_TYPES:
            continue
        if item_type not in INCLUDE_TYPES and item_type != "message":
            continue

        # Filter user messages: remove noise blocks
        if item_type == "message" and item.get("role") == "user":
            content = item.get("content", "")
            for noise in NOISE_PATTERNS:
                content = noise.sub("", content)
            item = {**item, "content": content}

        filtered.append(item)
    return filtered


def serialize_filtered_items(items: list[dict]) -> str:
    """Serialize filtered rollout items to text for LLM consumption."""
    lines = []
    for item in items:
        item_type = item.get("type", "unknown")
        role = item.get("role", "")
        content = item.get("content", item.get("command", item.get("text", "")))

        if item_type == "message":
            tag = f"[{role.upper()}]"
            lines.append(f"{tag} {content}")
        elif item_type in ("function_call", "local_shell_call", "tool_search_call",
                           "custom_tool_call", "web_search_call"):
            name = item.get("name", item.get("tool", item_type))
            args = json.dumps(item.get("arguments", item.get("args", {})), ensure_ascii=False)
            lines.append(f"[TOOL_CALL:{name}] {args}")
        elif item_type in ("function_call_output", "tool_search_output",
                           "custom_tool_call_output"):
            lines.append(f"[TOOL_OUTPUT] {content[:2000]}")
        else:
            lines.append(f"[{item_type.upper()}] {str(content)[:500]}")

    return "\n".join(lines)


# ─── Token Estimation ─────────────────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 bytes per token."""
    return max(1, (len(text.encode("utf-8")) + 3) // 4)


def truncate_to_budget(text: str, max_tokens: int) -> str:
    """Truncate text to fit within a token budget.
    
    Only used for LLM input limits. Memory storage has no truncation.
    """
    current_tokens = estimate_tokens(text)
    if current_tokens <= max_tokens:
        return text
    ratio = max_tokens / current_tokens
    truncated_len = int(len(text) * ratio * 0.9)  # 10% safety margin
    return text[:truncated_len] + "\n\n[... truncated to fit token budget ...]"


# ─── Filesystem Artifacts ─────────────────────────────────────────────────────

def ensure_memory_root(root: str) -> Path:
    """Create memory directory structure at ANY path on the system.
    
    No restrictions on root path — accepts any valid filesystem location.
    Under OmniRoot, this operates with full privilege access.
    """
    root = Path(root)
    (root / "rollout_summaries").mkdir(parents=True, exist_ok=True)
    (root / "skills").mkdir(parents=True, exist_ok=True)
    (root / "extensions" / "ad_hoc" / "notes").mkdir(parents=True, exist_ok=True)

    # Initialize git baseline if not present
    git_dir = root / ".git"
    if not git_dir.exists():
        import subprocess
        subprocess.run(["git", "init"], cwd=str(root), capture_output=True)
        (root / ".gitignore").write_text("phase2_workspace_diff.md\n")
        subprocess.run(["git", "add", "."], cwd=str(root), capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial memory baseline"],
                       cwd=str(root), capture_output=True)

    return root


def generate_rollout_summary_stem(thread_id: str, timestamp: datetime,
                                  slug: Optional[str] = None) -> str:
    """Generate a filesystem-safe rollout summary filename stem."""
    ts_str = timestamp.strftime("%Y-%m-%dT%H-%M-%S")
    hash_input = thread_id.encode()
    hash_val = hashlib.md5(hash_input).hexdigest()[:4]
    stem = f"{ts_str}-{hash_val}"
    if slug:
        safe_slug = re.sub(r"[^a-z0-9_]", "", slug.lower())[:60]
        if safe_slug:
            stem += f"-{safe_slug}"
    return stem


def read_raw_memories(memory_root: Path) -> str:
    """Read the merged raw_memories.md file."""
    path = memory_root / "raw_memories.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def read_memory_summary(memory_root: str) -> str:
    """Read memory_summary.md in full — no truncation, no artificial limits.
    
    Under OmniRoot, the complete memory summary is returned for maximum recall.
    """
    path = Path(memory_root) / "memory_summary.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_rollout_summary(memory_root: Path, stem: str, content: str) -> Path:
    """Write a rollout summary file at the configured memory root."""
    path = memory_root / "rollout_summaries" / f"{stem}.md"
    path.write_text(content, encoding="utf-8")
    return path


def write_raw_memories(memory_root: Path, entries: list[dict]) -> Path:
    """Write merged raw_memories.md from Phase 1 outputs."""
    lines = ["# Raw Memories\n", "Merged stage-1 raw memories:\n"]
    for entry in sorted(entries, key=lambda e: e.get("thread_id", "")):
        lines.append(f"## Thread `{entry['thread_id']}`")
        lines.append(f"updated_at: {entry.get('updated_at', 'unknown')}")
        lines.append(f"cwd: {entry.get('cwd', 'unknown')}")
        lines.append(f"rollout_path: {entry.get('rollout_path', 'unknown')}")
        lines.append(f"rollout_summary_file: {entry.get('summary_stem', 'unknown')}.md")
        lines.append("")
        lines.append(entry.get("raw_memory", ""))
        lines.append("")

    path = memory_root / "raw_memories.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ─── LLM Call ─────────────────────────────────────────────────────────────────

def build_validated_url(base_url: str) -> str:
    from urllib.parse import urlparse, urlunparse
    try:
        # Minimal path validation
        if "/../" in base_url or re.search(r"/%2e%2e/", base_url, re.IGNORECASE):
            raise ValueError("Invalid path")
        
        parsed = urlparse(base_url)
        
        # Protocol + host checks
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Invalid protocol")
        if not parsed.hostname:
            raise ValueError("Invalid host")
        allowed_domains = ["example.com"]  # add your allowed domains here
        if parsed.hostname.lower() not in allowed_domains:
            raise ValueError("Invalid host")
        
        # Append static path
        path = parsed.path.rstrip("/") + "/v1/chat/completions"
        parsed = parsed._replace(path=path)
        
        return urlunparse(parsed)
    except Exception:
        raise ValueError("Invalid URL")

def call_llm(system_prompt: str, user_prompt: str, config: dict,
             output_schema: Optional[dict] = None,
             temperature: float = 0.3) -> dict:
    """Call an OpenAI-compatible LLM endpoint. Returns parsed JSON response."""
    import requests

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['llm_api_key']}",
    }

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    body = {
        "model": config["llm_model"],
        "messages": messages,
        "temperature": temperature,
    }
    if output_schema:
        body["response_format"] = {"type": "json_object"}

    resp = requests.post(
        build_validated_url(config['llm_endpoint']),
        headers=headers,
        json=body,
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()

    content = data["choices"][0]["message"]["content"]
    # Try to parse as JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Extract JSON from markdown code block
        match = re.search(r"```(?:json)?\s*\n(.*?)\n```", content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return {"raw": content}


# ─── Git Operations ───────────────────────────────────────────────────────────

def git_diff(memory_root: Path) -> str:
    """Get git diff of memory workspace against baseline."""
    import subprocess
    result = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=str(memory_root),
        capture_output=True,
        text=True,
    )
    return result.stdout


def git_has_changes(memory_root: Path) -> bool:
    """Check if memory workspace has uncommitted changes."""
    import subprocess
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(memory_root),
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def git_commit_baseline(memory_root: Path, message: str = "Memory baseline update"):
    """Commit current state as new baseline."""
    import subprocess
    subprocess.run(["git", "add", "-A"], cwd=str(memory_root), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=str(memory_root),
        capture_output=True,
    )
