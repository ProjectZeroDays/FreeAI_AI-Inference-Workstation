"""AgentBrain — Three-tier intelligent routing (from guaardvark).

Decides how much compute a request deserves before any tools fire.
  Tier 1 (Reflex):  <100ms, 0 LLM calls — deterministic tool actions
  Tier 2 (Instinct): 1-3s, 1 LLM call — social/chat, direct answers
  Tier 3 (Deliberation): 5-30s, 3-10 LLM calls — multi-step ReACT loops

Usage:
    from brain import AgentBrain
    brain = AgentBrain()
    result = brain.route("Write a Python function to sort an array")
"""
import json
import os
import re
import threading
import time
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "agent_brain.json"
DEFAULT_CONFIG = {
    "enabled": True,
    "reflex_patterns": [
        {"pattern": r"\b(status|health)\b", "tier": "reflex", "action": "health_check"},
        {"pattern": r"\b(list|show)\s+(models|agents|plugins|providers)\b", "tier": "reflex", "action": "list_resources"},
        {"pattern": r"\b(clear|reset)\s*(memory|session|cache)\b", "tier": "reflex", "action": "clear_state"},
        {"pattern": r"\b(turn|toggle)\s+(off|on)\b", "tier": "reflex", "action": "toggle_feature"},
        {"pattern": r"\b(time|date)\b", "tier": "reflex", "action": "clock"},
        {"pattern": r"\b(ls|dir|pwd|whoami|echo)\b", "tier": "reflex", "action": "shell"},
        {"pattern": r"\b(help|what can you do)\b", "tier": "reflex", "action": "help"},
    ],
    "instinct_keywords": [
        "hello", "hi", "hey", "thanks", "thank you", "bye", "goodbye",
        "ok", "okay", "sure", "yes", "no", "please", "what", "how",
        "when", "where", "why", "explain", "tell me", "describe",
    ],
    "deliberation_keywords": [
        "implement", "build", "create", "design", "plan", "architect",
        "analyze", "debug", "fix", "optimize", "refactor", "review",
        "compare", "evaluate", "assess", "research", "investigate",
        "multi-step", "complex", "involves", "requires",
    ],
    "default_tier": "instinct",
    "max_deliberation_steps": 10,
    "deliberation_timeout_s": 120,
}


def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_CONFIG.copy()


class TierResult:
    """Base class for tier results."""
    def __init__(self, tier, action, result, latency_ms=0):
        self.tier = tier
        self.action = action
        self.result = result
        self.latency_ms = latency_ms
        self.timestamp = time.time()


class AgentBrain:
    """Three-tier routing engine."""

    def __init__(self, config=None):
        self.config = config or load_config()
        self._lock = threading.Lock()
        self._telemetry = []
        self._initialized = False

    def refresh(self):
        """Reload config and rebuild state."""
        self.config = load_config()
        self._initialized = True

    @property
    def is_ready(self):
        return self._initialized or True  # ready even before explicit init

    def route(self, prompt, context=None, session_id=None):
        """Route a prompt through the appropriate tier.

        Returns a dict with: tier, action, result, latency_ms, model_used
        """
        started = time.monotonic()
        tier = self._classify(prompt)

        if tier == "reflex":
            result = self._reflex_action(prompt, context)
        elif tier == "instinct":
            result = self._instinct_action(prompt, context, session_id)
        else:
            result = self._deliberation_action(prompt, context, session_id)

        latency_ms = int((time.monotonic() - started) * 1000)
        entry = {
            "ts": time.time(),
            "prompt_len": len(prompt),
            "tier": tier,
            "latency_ms": latency_ms,
        }
        with _TELEMETRY_LOCK:
            _TELEMETRY.append(entry)
            while len(_TELEMETRY) > 1000:
                _TELEMETRY.pop(0)
        return {**result, "tier": tier, "latency_ms": latency_ms}

    def _classify(self, prompt):
        """Classify prompt into tier."""
        p = prompt.lower().strip()

        # Reflex: pattern match
        for rule in self.config.get("reflex_patterns", []):
            if re.search(rule["pattern"], p):
                return "reflex"

        # Instinct: social/quick
        for kw in self.config.get("instinct_keywords", []):
            if kw in p:
                return "instinct"

        # Deliberation: complex/technical
        for kw in self.config.get("deliberation_keywords", []):
            if kw in p:
                return "deliberation"

        # Heuristic: long prompts or questions needing depth
        if len(p) > 200 or "?" in p and any(w in p for w in
                ["how to", "why", "what is", "explain", "compare"]):
            return "deliberation"

        return self.config.get("default_tier", "instinct")

    def _reflex_action(self, prompt, context=None):
        """Handle reflex-tier (deterministic) actions."""
        p = prompt.lower()
        if any(w in p for w in ["status", "health"]):
            return {"action": "health_check",
                    "result": "System operational. Check /health endpoint."}
        elif any(w in p for w in ["list models", "show models"]):
            return {"action": "list_models",
                    "result": "Use GET /proxy/models or GET /router/models"}
        elif any(w in p for w in ["list agents", "show agents"]):
            return {"action": "list_agents",
                    "result": "Use GET /agents/specialized/agents"}
        elif any(w in p for w in ["clear", "reset"]):
            return {"action": "clear_state",
                    "result": "State cleared. Use session-specific clear endpoints."}
        elif any(w in p for w in ["time", "date"]):
            return {"action": "clock",
                    "result": time.strftime("%Y-%m-%d %H:%M:%S")}
        elif "help" in p:
            return {"action": "help",
                    "result": (" tiers: reflex (<100ms), instinct (1-3s), "
                               "deliberation (5-30s)") }
        return {"action": "unknown_reflex", "result": "No reflex action matched"}

    def _instinct_action(self, prompt, context=None, session_id=None):
        """Handle instinct-tier (single LLM call)."""
        return {
            "action": "single_call",
            "result": " routed to single LLM call via proxy/router",
            "model_hint": "quick",
        }

    def _deliberation_action(self, prompt, context=None, session_id=None):
        """Handle deliberation-tier (multi-step ReACT)."""
        return {
            "action": "react_loop",
            "result": " routed to deliberation loop",
            "max_steps": self.config.get("max_deliberation_steps", 10),
            "timeout_s": self.config.get("deliberation_timeout_s", 120),
        }

    def get_telemetry(self, limit=100):
        with _TELEMETRY_LOCK:
            return list(_TELEMETRY[-limit:])

    def get_stats(self):
        with _TELEMETRY_LOCK:
            entries = list(_TELEMETRY)
        if not entries:
            return {"total": 0, "by_tier": {}}
        by_tier = {}
        total_latency = 0
        for e in entries:
            t = e.get("tier", "unknown")
            by_tier[t] = by_tier.get(t, 0) + 1
            total_latency += e.get("latency_ms", 0)
        return {
            "total": len(entries),
            "by_tier": by_tier,
            "avg_latency_ms": total_latency / len(entries) if entries else 0,
        }


_TELEMETRY = []
_TELEMETRY_LOCK = threading.Lock()
_BRAIN = None


def get_brain():
    global _BRAIN
    if _BRAIN is None:
        _BRAIN = AgentBrain()
        _BRAIN.refresh()
    return _BRAIN


def route(prompt, context=None, session_id=None):
    return get_brain().route(prompt, context, session_id)


if __name__ == "__main__":
    brain = AgentBrain()
    print("[brain] AgentBrain initialized")
    print(f"[brain] Config: {json.dumps(brain.config, indent=2)}")
    test_prompts = [
        "Hello, how are you?",
        "Write a Python function to implement quicksort",
        "What's the time?",
        "Compare React vs Vue for a SaaS dashboard",
        "List all available models",
    ]
    for p in test_prompts:
        result = brain.route(p)
        print(f"  [{result['tier']:12s}] {p[:50]}... -> {result['action']} ({result['latency_ms']}ms)")
