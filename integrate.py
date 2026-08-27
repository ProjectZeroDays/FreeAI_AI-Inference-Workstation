"""Integration script — wires all components together.

Creates unified config, registers services, and sets up the
coordinator entry point.

Usage:
    python integrate.py              # generate configs
    python integrate.py --verify     # verify all services reachable
    python integrate.py --status     # show integrated system status
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CONFIG_DIR = ROOT / "config"
PROXY_PORT = int(os.environ.get("PROXY_PORT", "8100"))
MEMORY_PORT = int(os.environ.get("MEMORY_PORT", "8110"))
AGENTS_PORT = int(os.environ.get("AGENTS_PORT", "8120"))
REGISTRY_PORT = int(os.environ.get("REGISTRY_PORT", "8130"))
RAG_PORT = int(os.environ.get("RAG_PORT", "8140"))
BRAIN_PORT = int(os.environ.get("BRAIN_PORT", "8150"))
SKILL_PORT = int(os.environ.get("SKILL_PORT", "8160"))


def generate_configs():
    """Generate all integration config files."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Unified proxy config (opencodex-style)
    proxy_config = {
        "version": "1.0",
        "default_provider": "anthropic",
        "default_model": "claude-sonnet-4-5",
        "proxy_port": PROXY_PORT,
        "providers": {
            "anthropic": {
                "enabled": True,
                "base_url": "https://api.anthropic.com",
                "key_env": "ANTHROPIC_API_KEY",
                "models": ["claude-opus-4-6", "claude-sonnet-4-5",
                           "claude-haiku-4-5"],
                "task_profiles": {
                    "coding": "claude-opus-4-6",
                    "reasoning": "claude-opus-4-6",
                    "quick": "claude-haiku-4-5",
                    "creative": "claude-sonnet-4-5",
                },
            },
            "openai": {
                "enabled": True,
                "base_url": "https://api.openai.com/v1",
                "key_env": "OPENAI_API_KEY",
                "models": ["gpt-4o", "gpt-4o-mini", "o3-mini"],
                "task_profiles": {
                    "coding": "gpt-4o",
                    "reasoning": "o3-mini",
                    "quick": "gpt-4o-mini",
                },
            },
            "google": {
                "enabled": True,
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "key_env": "GOOGLE_API_KEY",
                "models": ["gemini-2.5-pro", "gemini-2.5-flash"],
                "task_profiles": {
                    "coding": "gemini-2.5-pro",
                    "quick": "gemini-2.5-flash",
                },
            },
            "deepseek": {
                "enabled": True,
                "base_url": "https://api.deepseek.com/v1",
                "key_env": "DEEPSEEK_API_KEY",
                "models": ["deepseek-chat", "deepseek-reasoner",
                           "deepseek-coder"],
                "task_profiles": {
                    "coding": "deepseek-coder",
                    "reasoning": "deepseek-reasoner",
                    "quick": "deepseek-chat",
                },
            },
            "groq": {
                "enabled": True,
                "base_url": "https://api.groq.com/openai/v1",
                "key_env": "GROQ_API_KEY",
                "models": ["llama-3.3-70b-versatile", "qwen/qwen3-32b",
                           "llama-3.1-8b-instant"],
                "task_profiles": {
                    "coding": "llama-3.3-70b-versatile",
                    "quick": "llama-3.1-8b-instant",
                },
            },
            "ollama": {
                "enabled": False,
                "base_url": "http://localhost:11434/v1",
                "key_env": None,
                "models": ["qwen2.5-coder", "llama3.2", "deepseek-coder"],
            },
        },
        "routing": {
            "coding": ["anthropic/claude-opus-4-6", "openai/gpt-4o",
                        "deepseek/deepseek-coder", "groq/llama-3.3-70b-versatile"],
            "reasoning": ["anthropic/claude-opus-4-6", "openai/o3-mini",
                          "google/gemini-2.5-pro", "deepseek/deepseek-reasoner"],
            "quick": ["google/gemini-2.5-flash", "openai/gpt-4o-mini",
                      "groq/llama-3.1-8b-instant"],
            "creative": ["anthropic/claude-sonnet-4-5", "openai/gpt-4o"],
        },
        "rate_limit": {"capacity": 60, "refill_per_min": 60},
        "timeout_s": 300,
    }

    (CONFIG_DIR / "proxy.json").write_text(
        json.dumps(proxy_config, indent=2), encoding="utf-8")

    # 2. Agent brain config
    brain_config = {
        "enabled": True,
        "tier_defaults": {
            "reflex": {"max_latency_ms": 100, "llm_calls": 0},
            "instinct": {"max_latency_ms": 3000, "llm_calls": 1},
            "deliberation": {"max_latency_ms": 30000, "llm_calls": 10},
        },
        "reflex_patterns": [
            {"pattern": r"\b(status|health)\b", "tier": "reflex"},
            {"pattern": r"\b(list|show)\s+(models|agents|plugins)\b", "tier": "reflex"},
            {"pattern": r"\b(time|date)\b", "tier": "reflex"},
            {"pattern": r"\b(help|what can you do)\b", "tier": "reflex"},
        ],
        "instinct_keywords": ["hello", "hi", "thanks", "ok", "explain", "what is"],
        "deliberation_keywords": [
            "implement", "build", "create", "analyze", "debug",
            "optimize", "refactor", "compare", "research",
        ],
    }
    (CONFIG_DIR / "agent_brain.json").write_text(
        json.dumps(brain_config, indent=2), encoding="utf-8")

    # 3. Swarm config
    swarm_config = {
        "max_agents": 5,
        "worktree_base": ".swarm/worktrees",
        "merge_strategy": "dependency_ordered",
        "poll_interval_s": 5,
        "timeout_s": 1800,
        "memory_guard": {"min_ram_gb": 4.0, "max_swap_gb": 1.0},
    }
    (CONFIG_DIR / "swarm.json").write_text(
        json.dumps(swarm_config, indent=2), encoding="utf-8")

    # 4. Service registry (all internal services)
    services = {
        "proxy": {"port": PROXY_PORT, "module": "proxy.proxy", "url": f"http://localhost:{PROXY_PORT}"},
        "memory": {"port": MEMORY_PORT, "module": "memory.memory_api", "url": f"http://localhost:{MEMORY_PORT}"},
        "agents": {"port": AGENTS_PORT, "module": "agents.specialized.agents_api", "url": f"http://localhost:{AGENTS_PORT}"},
        "registry": {"port": REGISTRY_PORT, "module": "plugins.registry.registry_api", "url": f"http://localhost:{REGISTRY_PORT}"},
        "rag": {"port": RAG_PORT, "module": "rag.service", "url": f"http://localhost:{RAG_PORT}"},
        "brain": {"port": BRAIN_PORT, "module": "brain.brain", "url": f"http://localhost:{BRAIN_PORT}"},
        "skills": {"port": SKILL_PORT, "module": "skills.skill_api", "url": f"http://localhost:{SKILL_PORT}"},
        "pipeline": {"port": 8170, "module": "pipeline.api", "url": "http://localhost:8170"},
        "dashboard": {"port": 8080, "module": "dashboard.backend", "url": "http://localhost:8080"},
        "autonomous": {"port": 8050, "module": "autonomous.api", "url": "http://localhost:8050"},
    }
    (CONFIG_DIR / "services.json").write_text(
        json.dumps(services, indent=2), encoding="utf-8")

    # 5. Skills mapping
    skills_config = {
        "paths": [
            str(ROOT / "skills"),
            str(ROOT / ".opencode" / "skill"),
        ],
        "auto_load": ["orchestrate", "rate-limit-retry", "self-heal",
                      "repo-maintenance", "research", "code-review"],
        "categories": {
            "coding": ["binary-patching-for-ai-providers", "debugging-hermes-tui-commands",
                       "gui-component-integration", "python-debugpy",
                       "systematic-debugging", "test-driven-development",
                       "writing-plans"],
            "agents": ["agent-autonomy-kit", "agent-team-orchestration",
                       "self-improving-agent"],
            "creative": ["ascii-art", "comfyui", "design-md", "manim-video",
                         "pixel-art"],
            "devops": ["kanban-orchestrator", "kanban-worker", "webhook-subscriptions"],
            "github": ["github-code-review", "github-issues", "github-pr-workflow"],
            "productivity": ["notion", "linear", "obsidian"],
            "mlops": ["llama-cpp", "vllm", "dspy"],
        },
    }
    (CONFIG_DIR / "skills.json").write_text(
        json.dumps(skills_config, indent=2), encoding="utf-8")

    print(f"[integrate] Generated {len(list(CONFIG_DIR.glob('*.json')))} config files")
    services["skills"] = {"port": SKILL_PORT, "module": "skills.skill_api",
                          "url": f"http://localhost:{SKILL_PORT}",
                          "dashboard": str(ROOT / "skills" / "dashboard.html")}
    return services


def verify_services(services):
    """Check all services are reachable."""
    import requests
    import re
    from urllib.parse import urlparse, urlunparse
    
    def build_validated_url(base_url: str) -> str:
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
            
            # Rebuild path with fixed /health endpoint
            parsed = parsed._replace(path=f"{parsed.path.rstrip('/')}/health")
            
            return urlunparse(parsed)
        except Exception:
            raise ValueError("Invalid URL")
    
    results = {}
    for name, svc in services.items():
        try:
            r = requests.get(build_validated_url(svc['url']), timeout=3)
            results[name] = {"status": r.status_code, "healthy": r.ok}
        except Exception as exc:
            results[name] = {"status": 0, "healthy": False, "error": str(exc)}
    return results


def print_status(services, verify=True):
    """Print integrated system status."""
    print("\n" + "=" * 60)
    print("  FreeAI AI Development Environment — Integration Status")
    print("=" * 60)

    for name, svc in services.items():
        status = "RUNNING" if verify and verify_services({name: svc})[name]["healthy"] else "STOPPED"
        icon = "\u2713" if status == "RUNNING" else " "
        print(f"  [{icon}] {name:12s} :{svc['port']}  {status}")

    print("-" * 60)
    print("  Components:")
    print("    - Unified LLM Proxy (40+ providers)")
    print("    - Agent Brain (3-tier routing: Reflex/Instinct/Deliberation)")
    print("    - Agent Zero Memory (persistent, cross-session)")
    print("    - 7 Specialized Agents (Orchestrator, Explorer, Oracle, etc.)")
    print("    - Plugin Registry (awesome-opencode compatible)")
    print("    - RAG Service (BM25 + vector hybrid)")
    print("    - Swarm Orchestrator (parallel agents, worktree isolation)")
    print("    - Skills System (agent-toolkit, 100+ skills)")
    print("    - AutoSkill Monitor (pattern detection, auto SKILL.md creation)")
    print("    - Custom Pipeline API (scaffold/refactor/debug/analyze/review/document)")
    print("    - Autonomous SDLC (7-phase lifecycle: Plan→Code→Test→Fix→Review→Doc→Package)")
    print("    - Skills Manager Dashboard (browse, edit, manage skills)")
    print("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="FreeAI Integration")
    parser.add_argument("--verify", action="store_true",
                        help="Verify all services are running")
    parser.add_argument("--status", action="store_true",
                        help="Show system status")
    parser.add_argument("--generate", action="store_true",
                        help="Generate config files only")
    args = parser.parse_args()

    services = generate_configs()

    if args.generate:
        print("[integrate] Config generation complete.")
        return

    if args.verify:
        results = verify_services(services)
        all_healthy = all(r["healthy"] for r in results.values())
        for name, r in results.items():
            icon = "\u2713" if r["healthy"] else "\u2717"
            print(f"  [{icon}] {name}: {'healthy' if r['healthy'] else 'unreachable'}")
        sys.exit(0 if all_healthy else 1)

    if args.status:
        print_status(services, verify=False)
        return

    # Default: generate + show status
    print_status(services, verify=True)


if __name__ == "__main__":
    main()
