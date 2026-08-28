"""Skill catalog scraper — fetches and normalizes skills from external sources.

Usage:
    python scripts/scrape_skills.py              # run scraper, write catalog.json
    python scripts/scrape_skills.py --dry-run    # print results without writing

Outputs: skills/catalog.json
"""
import json
import re
import sys
import time
from pathlib import Path

try:
    import urllib.request
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

ROOT = Path(__file__).parent.parent
CATALOG_PATH = ROOT / "skills" / "catalog.json"

EXTERNAL_SKILL_URLS = [
    ("ohmyopencodeslim", "https://ohmyopencodeslim.com/skills"),
]

# Curated fallback skills used when external sources are unreachable.
FALLBACK_SKILLS = [
    {"id": "accessibility-audit", "name": "Accessibility Audit", "description": "WCAG compliance, accessibility testing, ARIA patterns, screen reader optimization, and keyboard navigation.", "category": "development", "triggers": ["accessibility", "a11y", "WCAG", "ARIA", "screen reader", "keyboard navigation"]},
    {"id": "ace-music", "name": "ACE Music", "description": "Generate AI music using ACE-Step 1.5 via ACE Music's free API. Supports lyrics, style prompts, covers, and repainting.", "category": "creative", "triggers": ["music", "generate music", "compose", "song", "ACE music"]},
    {"id": "advanced-intel", "name": "Advanced Intel", "description": "High-fidelity intelligence gathering and data assimilation. Focuses on synthesizing fragmented data into a comprehensive target operational picture.", "category": "red-teaming", "triggers": ["intel", "intelligence", "gathering", "target analysis", "OSINT"]},
    {"id": "api-design", "name": "API Design", "description": "REST and GraphQL API design patterns, OpenAPI specs, versioning, pagination, rate limiting, authentication, and error handling.", "category": "development", "triggers": ["API design", "REST", "GraphQL", "OpenAPI", "swagger", "endpoint"]},
    {"id": "autonomous-red-teaming", "name": "Autonomous Red Teaming", "description": "AI-driven autonomous red teaming. Automates the cycle of target discovery, vulnerability research, exploit generation, and verification.", "category": "red-teaming", "triggers": ["red team", "pentest", "vulnerability", "exploit", "autonomous red team"]},
    {"id": "backend-architecture", "name": "Backend Architecture", "description": "Backend architecture patterns, service design, microservices, event-driven architecture, CQRS, and system design.", "category": "development", "triggers": ["backend", "architecture", "microservices", "CQRS", "event-driven", "system design"]},
    {"id": "binary-patching-for-ai-providers", "name": "Binary Patching for AI Providers", "description": "Modify AI provider settings in applications through direct binary patching for seamless integration.", "category": "red-teaming", "triggers": ["binary patch", "patching", "AI provider", "integration"]},
    {"id": "browser-automation", "name": "Browser Automation", "description": "Drive a browser from the CLI to navigate pages, extract data, take screenshots, fill forms, click controls, or inspect web apps.", "category": "development", "triggers": ["browser automation", "web scraping", "screenshots", "forms", "playwright", "selenium"]},
    {"id": "build-game", "name": "Build Game", "description": "Generate and iteratively develop polished 3D browser games from natural language. Outputs a single playable HTML file using Three.js.", "category": "creative", "triggers": ["game", "3D game", "Three.js", "browser game", "build game"]},
    {"id": "code-review", "name": "Code Review", "description": "Review code changes for correctness, security, performance, and code quality. Accepts diffs, commit hashes, or git ranges.", "category": "development", "triggers": ["code review", "review", "diff", "PR review", "pull request"]},
    {"id": "comfyui", "name": "ComfyUI", "description": "Generate images, video, and audio with ComfyUI. Install, launch, manage nodes/models, and run workflows with parameter injection.", "category": "creative", "triggers": ["comfyui", "comfy UI", "image generation", "workflow", "nodes"]},
    {"id": "data-pipeline", "name": "Data Pipeline", "description": "Data pipeline design, ETL processes, stream processing, data validation, and workflow orchestration.", "category": "data-science", "triggers": ["data pipeline", "ETL", "stream processing", "Airflow", "Dagster", "data workflow"]},
    {"id": "docker-compose", "name": "Docker Compose", "description": "Docker Compose service orchestration for multi-container applications. Sets up local dev environments, volumes, networks, and health checks.", "category": "devops", "triggers": ["docker compose", "docker-compose", "containers", "multi-container", "dev environment"]},
    {"id": "debug-pro", "name": "Debug Pro", "description": "Reproduce, isolate, instrument, and fix bugs across common programming languages and runtimes.", "category": "development", "triggers": ["debug", "fix bug", "reproduce", "isolate", "instrument"]},
    {"id": "error-handling", "name": "Error Handling", "description": "Error handling patterns, custom exceptions, error boundaries, retry strategies, and graceful degradation.", "category": "development", "triggers": ["error handling", "exceptions", "retry", "graceful degradation", "error boundary"]},
    {"id": "forensic-analysis", "name": "Forensic Analysis", "description": "Professional forensic analysis of logs, memory dumps, and file metadata. Extracts actionable intelligence from compromised systems.", "category": "red-teaming", "triggers": ["forensic", "analysis", "logs", "memory dump", "IOC", "compromised"]},
    {"id": "game-ai", "name": "Game AI", "description": "Game AI development guide covering behavior trees, state machines, pathfinding, and decision-making systems.", "category": "creative", "triggers": ["game AI", "behavior tree", "pathfinding", "state machine", "NPC", "AI behavior"]},
    {"id": "git-workflow", "name": "Git Workflow", "description": "Advanced git workflows including branching strategies, interactive rebase, bisect debugging, stash management, and cherry-pick.", "category": "development", "triggers": ["git", "branching", "rebase", "bisect", "stash", "cherry-pick"]},
    {"id": "infrastructure-as-code", "name": "Infrastructure as Code", "description": "Infrastructure as Code with Terraform, Pulumi, and Ansible. Provision cloud infrastructure, manage state, and automate server configuration.", "category": "devops", "triggers": ["Terraform", "Pulumi", "Ansible", "IaC", "infrastructure", "provisioning"]},
    {"id": "llama-cpp", "name": "llama.cpp", "description": "llama.cpp local GGUF inference and HuggingFace Hub model discovery.", "category": "data-science", "triggers": ["llama.cpp", "GGUF", "local LLM", "inference", "HuggingFace", "model"]},
    {"id": "performance-profiling", "name": "Performance Profiling", "description": "Performance optimization, profiling tools, memory analysis, CPU profiling, query optimization, and benchmarking.", "category": "development", "triggers": ["performance", "profiling", "optimization", "memory", "CPU", "benchmark"]},
    {"id": "pixel-art", "name": "Pixel Art", "description": "Pixel art with era palettes (NES, Game Boy, PICO-8).", "category": "creative", "triggers": ["pixel art", "NES", "Game Boy", "PICO-8", "retro", "pixel"]},
    {"id": "playwright", "name": "Playwright", "description": "Browser automation with Playwright. Test websites, take screenshots, check responsive design, and automate any browser task.", "category": "development", "triggers": ["playwright", "browser test", "E2E test", "screenshots", "automated test"]},
    {"id": "python-debugpy", "name": "Python Debugpy", "description": "Debug Python via pdb REPL and debugpy remote (DAP).", "category": "development", "triggers": ["python debug", "debugpy", "pdb", "DAP", "debugger"]},
    {"id": "regex-mastery", "name": "Regex Mastery", "description": "Regular expression patterns, common use cases, and debugging. Writing regex, parsing text patterns, and validating input.", "category": "development", "triggers": ["regex", "regular expression", "pattern matching", "parsing"]},
    {"id": "security-audit", "name": "Security Audit", "description": "Security audit patterns, vulnerability detection, OWASP Top 10, secure coding practices, and dependency scanning.", "category": "red-teaming", "triggers": ["security audit", "OWASP", "vulnerability", "secure coding", "dependency scan"]},
    {"id": "shell-scripting", "name": "Shell Scripting", "description": "Shell scripting for automation, Bash/PowerShell one-liners, file manipulation, text processing, and system administration.", "category": "devops", "triggers": ["shell", "bash", "scripting", "automation", "PowerShell", "CLI"]},
    {"id": "tdd-restoration", "name": "TDD Restoration", "description": "Restores missing framework components using a strict Test-Driven Development loop: Fail -> Implement -> Pass.", "category": "development", "triggers": ["TDD", "test-driven development", "red-green-refactor", "test first"]},
    {"id": "webhook-subscriptions", "name": "Webhook Subscriptions", "description": "Event-driven agent runs via webhook subscriptions.", "category": "devops", "triggers": ["webhook", "event-driven", "subscription", "trigger"]},
    {"id": "writing-clearly-and-concisely", "name": "Writing Clearly and Concisely", "description": "Write prose humans will read — documentation, commit messages, error messages, explanations, reports, or UI text. Applies Strunk's timeless rules.", "category": "productivity", "triggers": ["write clearly", "concise", "documentation", "prose", "editing"]},
    {"id": "memory-pipeline", "name": "Memory Pipeline", "description": "Two-phase memory pipeline for AI CLI agents. Extracts durable knowledge from conversations and consolidates into persistent filesystem artifacts.", "category": "productivity", "triggers": ["memory", "knowledge base", "persistent memory", "knowledge extraction"]},
    {"id": "fullstack-developer", "name": "Fullstack Developer", "description": "World-class fullstack development covering frontend (React, Next.js, Vue), backend (Node.js, Python/FastAPI, Django), databases, APIs, and DevOps.", "category": "development", "triggers": ["fullstack", "frontend", "backend", "React", "Next.js", "Vue", "FastAPI", "Django"]},
    {"id": "database-patterns", "name": "Database Patterns", "description": "Database design patterns, SQL optimization, migrations, indexing strategies, connection pooling, and ORM best practices.", "category": "development", "triggers": ["database", "SQL", "migration", "indexing", "ORM", "connection pooling"]},
    {"id": "monitoring-logging", "name": "Monitoring & Logging", "description": "Application monitoring, structured logging, distributed tracing, alerting, and observability patterns.", "category": "devops", "triggers": ["monitoring", "logging", "tracing", "observability", "Prometheus", "Grafana"]},
    {"id": "frontend-design", "name": "Frontend Design", "description": "Frontend UI/UX patterns, responsive design, component architecture, CSS strategies, accessibility, and design systems.", "category": "development", "triggers": ["frontend", "UI", "UX", "responsive", "CSS", "design system", "components"]},
    {"id": "devops-kanban-orchestrator", "name": "DevOps Kanban Orchestrator", "description": "Decomposition playbook and anti-temptation rules for an orchestrator profile routing work through Kanban.", "category": "devops", "triggers": ["kanban", "orchestrator", "workflow", "task decomposition", "project management"]},
]


# Category inference mapping from directory name substrings.
_CATEGORY_MAP = {
    "red": "red-teaming",
    "dev": "development",
    "creative": "creative",
    "data": "data-science",
    "ops": "devops",
    "product": "productivity",
}


def _infer_category(dir_name: str) -> str:
    lower = dir_name.lower()
    for key, cat in _CATEGORY_MAP.items():
        if key in lower:
            return cat
    return "general"


def _parse_fm_key(lines: list[str], key: str) -> str:
    for i, line in enumerate(lines):
        if line.startswith(key + ":"):
            val = line.split(":", 1)[1].strip().strip('"').strip("'")
            if val in (">", "|"):
                parts = []
                for j in range(i + 1, len(lines)):
                    nxt = lines[j]
                    if nxt and nxt[0] in (" ", "\t"):
                        parts.append(nxt.strip())
                    else:
                        break
                return "\n".join(parts)
            return val
    return ""


def _extract_triggers_from_desc(desc: str) -> list[str]:
    if not desc:
        return []
    triggers: list[str] = []
    seen: set[str] = set()
    # Look for explicit trigger phrases first
    patterns = [
        r"Triggers?\s*on:\s*([^\n]+)",
        r"When\s+the\s+user\s+asks\s+(?:to|about|for|with|how|where|what|when|why|who|if)\s+([^\n.]{5,120})",
        r"Use\s+when\s+(?:the\s+)?(?:user\s+)?([^\n.]{5,120})",
    ]
    for pat in patterns:
        m = re.search(pat, desc, re.I)
        if m:
            raw = m.group(1).strip()
            # Split on common delimiters
            for part in re.split(r"[,;]+\s*", raw):
                part = part.strip()
                if not part:
                    continue
                cleaned = re.sub(r"[^a-zA-Z0-9\s-]", "", part).strip()
                if cleaned and len(cleaned) <= 30 and cleaned.lower() not in seen:
                    seen.add(cleaned.lower())
                    triggers.append(cleaned)
                    if len(triggers) >= 5:
                        return triggers
    # Fallback: look for common trigger keywords embedded in description
    for phrase in re.findall(r"\b(?:use|when|triggers?|for|about|with)\b\s+(?:the\s+)?[a-zA-Z][a-zA-Z0-9\s]{3,27}(?=[.,;:\n]|$)", desc, re.I):
        cleaned = re.sub(r"[^a-zA-Z0-9\s-]", "", phrase).strip()
        if cleaned and len(cleaned) <= 30 and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            triggers.append(cleaned)
            if len(triggers) >= 5:
                break
    return triggers


def _try_fetch(url: str, timeout: int = 5) -> str | None:
    if not HAS_URLLIB:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FreeAI-SkillScraper/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def _parse_ohmyopencodeslim(html: str) -> list[dict]:
    """Try to extract skills from ohmyopencodeslim.com HTML response."""
    skills = []
    # Look for JSON-LD or embedded skill data
    json_matches = re.findall(r'<script[^>]*type=["\']application\/ld\+json["\'][^>]*>([\s\S]*?)<\/script>', html)
    if json_matches:
        for block in json_matches:
            try:
                data = json.loads(block)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "name" in item:
                            skills.append(_normalize_skill(item, "ohmyopencodeslim"))
                elif isinstance(data, dict) and "name" in data:
                    skills.append(_normalize_skill(data, "ohmyopencodeslim"))
            except (json.JSONDecodeError, KeyError):
                pass
    # Fallback: look for skill-like patterns in HTML
    for match in re.finditer(r'name["\s:]+([^"<>]+?)["\s:,]*\s*description["\s:]+["\']?([^"<\']{10,200})', html, re.I):
        name = match.group(1).strip()
        desc = match.group(2).strip()
        if len(name) > 2 and len(desc) > 10:
            skills.append({
                "id": re.sub(r"[^a-z0-9]", "-", name.lower()).strip("-"),
                "name": name,
                "description": desc,
                "source": "ohmyopencodeslim",
                "category": "general",
                "triggers": [],
                "path": None,
                "local": False,
            })
    return skills


def _normalize_skill(raw: dict, source: str) -> dict:
    return {
        "id": raw.get("id", re.sub(r"[^a-z0-9]", "-", raw.get("name", "unknown").lower()).strip("-")),
        "name": raw.get("name", "Untitled"),
        "description": raw.get("description", "")[:500] + ("..." if len(raw.get("description", "")) > 500 else ""),
        "source": source,
        "category": raw.get("category", raw.get("type", "general")).lower().replace(" ", "-"),
        "triggers": raw.get("triggers", []),
        "path": None,
        "local": False,
    }


def fetch_external_skills() -> tuple[list[dict], list[dict]]:
    """Fetch skills from external sources. Returns (fetched, errors)."""
    fetched = []
    errors = []
    for source_name, url in EXTERNAL_SKILL_URLS:
        html = _try_fetch(url)
        if html is None:
            errors.append({"source": source_name, "url": url, "error": "unreachable"})
            continue
        try:
            skills = _parse_ohmyopencodeslim(html)
            fetched.extend(skills)
        except Exception as e:
            errors.append({"source": source_name, "url": url, "error": str(e)})
    return fetched, errors


def build_catalog(dry_run: bool = False) -> dict:
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    sources = [
        {"name": "ohmyopencodeslim", "url": "https://ohmyopencodeslim.com/skills", "fetched_at": now_iso},
        {"name": "mimocode", "url": "local", "fetched_at": now_iso},
    ]

    # Fetch external skills
    external_skills, fetch_errors = fetch_external_skills()

    # Combine: external + fallback
    all_skills = []
    seen_ids = set()

    for skill in external_skills:
        sid = skill.get("id", "")
        if sid and sid not in seen_ids:
            seen_ids.add(sid)
            all_skills.append(skill)

    # Add fallback skills (only those not already present)
    for skill in FALLBACK_SKILLS:
        sid = skill["id"]
        if sid not in seen_ids:
            seen_ids.add(sid)
            all_skills.append({
                "id": skill["id"],
                "name": skill["name"],
                "description": skill["description"],
                "source": "fallback" if not external_skills else "mimocode-curated",
                "category": skill["category"],
                "triggers": skill["triggers"],
                "path": None,
                "local": False,
            })

    # Add local skills from filesystem
    local_skill_dirs = [
        ROOT / "skills",
        ROOT / ".opencode" / "skills",
        ROOT / ".agents" / "skills",
    ]
    local_ids = set(s["id"] for s in all_skills)
    for base_dir in local_skill_dirs:
        if not base_dir.exists():
            continue
        for d in sorted(base_dir.iterdir()):
            if not d.is_dir():
                continue
            skill_md = d / "SKILL.md"
            if not skill_md.exists():
                continue
            sid = d.name
            if sid in local_ids:
                continue
            local_ids.add(sid)
            try:
                content = skill_md.read_text(encoding="utf-8", errors="ignore")
                name = sid
                desc = ""
                category = _infer_category(sid)
                triggers = []
                fm = re.match(r"^---\n([\s\S]*?)\n---", content)
                if fm:
                    fm_lines = fm.group(1).split("\n")
                    name = _parse_fm_key(fm_lines, "name") or name
                    desc = _parse_fm_key(fm_lines, "description") or desc
                    cat_from_fm = _parse_fm_key(fm_lines, "category")
                    if cat_from_fm:
                        category = cat_from_fm
                    for li, line in enumerate(fm_lines):
                        if line.startswith("triggers:"):
                            for lj in range(li + 1, len(fm_lines)):
                                nl = fm_lines[lj]
                                if nl.strip().startswith("- "):
                                    triggers.append(nl.strip()[2:].strip().strip('"'))
                                elif nl and not nl[0] in (" ", "\t"):
                                    break
                if not triggers and desc:
                    triggers = _extract_triggers_from_desc(desc)
                desc_trunc = desc[:500] + ("..." if len(desc) > 500 else "")
                all_skills.append({
                    "id": sid,
                    "name": name,
                    "description": desc_trunc,
                    "source": "local",
                    "category": category,
                    "triggers": triggers,
                    "path": str(skill_md),
                    "local": True,
                })
            except OSError:
                continue

    catalog = {
        "version": "1.0",
        "generated_at": now_iso,
        "sources": sources,
        "fetch_errors": fetch_errors,
        "skills": all_skills,
        "total": len(all_skills),
    }

    if not dry_run:
        CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[scrape] Wrote {len(all_skills)} skills to {CATALOG_PATH}")
        if fetch_errors:
            print(f"[scrape] {len(fetch_errors)} source(s) had errors: {[e['source'] for e in fetch_errors]}")
        else:
            print("[scrape] All sources fetched successfully.")
    else:
        print(f"[scrape] Dry run: would write {len(all_skills)} skills")
        if fetch_errors:
            print(f"[scrape] Fetch errors: {[e['source'] for e in fetch_errors]}")

    return catalog


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    build_catalog(dry_run=dry_run)
