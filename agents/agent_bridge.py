#!/usr/bin/env python3
"""Agent Bridge — connects all integration components.

Provides intelligent routing between:
- Specialized agents (orchestrator, explorer, oracle, etc.)
- Memory system (agent-zero style)
- Plugin registry (awesome-opencode style)
- LLM proxy (opencodex-style)
"""
import json
import os
import time
import threading
from typing import Optional

from agents.llm_proxy import get_store as get_memory_store
from agents.plugin_registry import get_registry, get_loader
from agents.specialized_agents import AGENT_MODELS, AGENT_PROMPTS, call_proxy


class AgentBridge:
    """Central hub for agent coordination and routing."""

    def __init__(self):
        self._registry = get_registry()
        self._loader = get_loader()
        self._memory = get_memory_store()
        self._active_agents: dict[str, str] = {}  # session -> agent
        self._lock = threading.Lock()

    def route_to_agent(self, request: str) -> str:
        """Intelligently route a request to the best agent."""
        lower = request.lower()
        # Keyword-based routing with fallback to orchestrator
        routes = {
            "implement|write code|build|create|develop|function|class|api": "fixer",
            "research|explore|investigate|find|discover|search": "explorer",
            "architecture|design|review|analyze|trade.?off|recommend": "oracle",
            "document|readme|wiki|manual|guide|how.to": "librarian",
            "ui|ux|design|interface|layout|color|typography": "designer",
            "debate|discuss|pros|cons|perspective|multiple views": "council",
            "coordinate|plan|orchestrate|manage|delegate": "orchestrator",
        }
        for pattern, agent in routes.items():
            if re.search(pattern, lower):
                return agent
        return "orchestrator"  # default

    def get_model_for_task(self, task_type: str) -> str:
        """Get recommended model for a task type."""
        model_map = {
            "coding": AGENT_MODELS.get("fixer", "qwen3.6-12b"),
            "research": AGENT_MODELS.get("explorer", "gemini-2.5-flash"),
            "analysis": AGENT_MODELS.get("oracle", "qwythos-v2-9b"),
            "documentation": AGENT_MODELS.get("librarian", "gemini-2.5-flash"),
            "design": AGENT_MODELS.get("designer", "claude-sonnet-4-5"),
        }
        return model_map.get(task_type, AGENT_MODELS.get("orchestrator", "qwen3.6-12b"))

    def execute_with_model(self, prompt: str, model: str = None,
                           session_id: str = None) -> dict:
        """Execute a prompt with the specified model."""
        started = time.monotonic()
        result = call_proxy(prompt, model=model)
        elapsed = int((time.monotonic() - started) * 1000)
        if session_id:
            self._memory.remember(session_id, "assistant",
                                  result.get("response", {}).get("content", ""))
        return {**result, "elapsed_ms": elapsed}

    def execute_with_agent(self, prompt: str, agent: str = None,
                           session_id: str = None) -> dict:
        """Execute through a specific agent."""
        if not agent:
            agent = self.route_to_agent(prompt)
        with _lock:
            if session_id:
                self._active_agents[session_id] = agent
        # Import here to avoid circular imports at module level
        from agents.specialized_agents import invoke_agent
        return invoke_agent(agent, prompt, session_id=session_id)

    def get_context(self, session_id: str) -> str:
        """Get memory context for a session."""
        return self._memory.recall_context(session_id)

    def list_plugins(self, category: str = None) -> list:
        return self._registry.list_plugins(category=category)

    def find_skills(self, query: str, limit: int = 5) -> list:
        return self._loader.match_skills(query, limit)

    def stats(self) -> dict:
        return {
            "agents": list(AGENT_MODELS.keys()),
            "plugins": self._registry.stats(),
            "skills": self._loader.stats(),
            "memory": self._memory.stats(),
            "active_sessions": len(self._active_agents),
        }


_bridge = None
_lock = threading.Lock()


def get_bridge() -> AgentBridge:
    global _bridge
    if _bridge is None:
        _bridge = AgentBridge()
    return _bridge


if __name__ == "__main__":
    import re
    bridge = get_bridge()
    print(json.dumps(bridge.stats(), indent=2))
    print(f"\nRoute test: 'write a function' -> {bridge.route_to_agent('write a function')}")
    print(f"Route test: 'research this codebase' -> {bridge.route_to_agent('research this codebase')}")
    print(f"Route test: 'design the UI' -> {bridge.route_to_agent('design the UI')}")
