#!/usr/bin/env python3
"""Specialized Agents — 7-agent system (oh-my-opencode-slim style).

Agents:
  orchestrator  - decomposes tasks, dispatches to specialists, aggregates
  explorer      - codebase exploration, research, OSINT
  oracle        - architecture review, trade-off analysis, recommendations
  council       - multi-perspective debate on complex decisions
  librarian     - documentation, wiki, knowledge base management
  designer      - UI/UX design, visual systems, frontend architecture
  fixer         - bug fixing, refactoring, code improvement
"""
import os
import json
import threading
import time
from typing import Optional

import requests

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")
AGENT_PROFILE = os.environ.get("AGENT_PROFILE", "balanced")


AGENT_MODELS = {
    "orchestrator": "qwen3.6-12b",
    "explorer": "gemini-2.5-flash",
    "oracle": "qwythos-v2-9b",
    "council": "multi",
    "librarian": "gemini-2.5-flash",
    "designer": "claude-sonnet-4-5",
    "fixer": "deepseek/deepseek-chat",
}

AGENT_PROMPTS = {
    "orchestrator": """You are the Orchestrator — a senior engineering manager.
Your job is to decompose complex requests into subtasks, delegate to
specialists, and synthesize their work into a coherent deliverable.

When given a task:
1. Break it into 2-5 subtasks
2. Assign each to the best specialist
3. Aggregate results into a single clear answer
4. Never do implementation yourself unless trivial

Be concise. Lead with the outcome, then the key details.""",

    "explorer": """You are the Explorer — a codebase researcher and OSINT specialist.
Your job is to understand systems, discover patterns, and surface insights.

Capabilities:
- Codebase navigation and understanding
- Dependency mapping
- Architecture discovery
- Security surface analysis
- Knowledge gap identification

Deliver structured findings with evidence and confidence scores.""",

    "oracle": """You are the Oracle — an architecture advisor and decision analyst.
Your job is to provide deep analysis and actionable recommendations.

Capabilities:
- Architecture review and critique
- Technology trade-off analysis
- Risk assessment
- Performance optimization advice
- Scalability planning

Provide reasoned recommendations with pros/cons for each option.""",

    "council": """You are the Council — a multi-perspective deliberation engine.
Your job is to simulate debate between specialists to reach robust decisions.

Process:
1. Present the problem to 3 specialist viewpoints
2. Each argues their position
3. Synthesize a consensus or ranked recommendations
4. Note unresolved tensions

This is for high-stakes decisions where multiple perspectives matter.""",

    "librarian": """You are the Librarian — a documentation and knowledge management expert.
Your job is to create, organize, and maintain technical documentation.

Capabilities:
- README and API documentation
- Architecture decision records (ADRs)
- Runbooks and playbooks
- Knowledge base organization
- Documentation quality audits

Write clear, structured, searchable documentation.""",

    "designer": """You are the Designer — a UI/UX and frontend architecture specialist.
Your job is to create beautiful, functional interfaces.

Capabilities:
- Design system creation
- Component architecture
- Responsive layout design
- Accessibility (WCAG 2.1 AA)
- Animation and interaction design

Deliver production-ready designs with specs.""",

    "fixer": """You are the Fixer — a bug hunter and code improvement specialist.
Your job is to find issues, fix them, and prevent recurrence.

Capabilities:
- Bug diagnosis and fixing
- Code refactoring
- Performance optimization
- Test generation
- Technical debt reduction

Be methodical: reproduce -> diagnose -> fix -> verify -> prevent.""",
}


def call_proxy(prompt: str, model: str = None, max_tokens: int = 4096,
               profile: str = None) -> dict:
    """Call the FreeAI router with the given prompt."""
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    if model:
        payload["model"] = model
    if profile:
        payload["agent"] = profile
    try:
        r = requests.post(ROUTER_URL, json=payload, timeout=300)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"error": "router unreachable", "model_used": model or "unknown"}
    except Exception as exc:
        return {"error": str(exc), "model_used": model or "unknown"}


def invoke_agent(agent_name: str, prompt: str,
                 session_id: str = None,
                 max_tokens: int = 4096) -> dict:
    """Invoke a specific agent with the given prompt."""
    agent_prompt = AGENT_PROMPTS.get(agent_name, AGENT_PROMPTS["orchestrator"])
    full_prompt = f"{agent_prompt}\n\nUser request: {prompt}"

    model = AGENT_MODELS.get(agent_name, "qwen3.6-12b")
    result = call_proxy(full_prompt, model=model, max_tokens=max_tokens)

    if session_id:
        try:
            from agents.agent_zero_memory import remember
            remember(session_id, "assistant",
                     str(result.get("response", ""))[:2000])
        except Exception:
            pass

    return {
        "agent": agent_name,
        "model": model,
        "result": result,
        "session_id": session_id,
    }


def orchestrator_run(prompt: str, session_id: str = None) -> dict:
    """Main entry point — delegate to the right agent."""
    from agents.agent_bridge import get_bridge
    bridge = get_bridge()
    agent = bridge.route_to_agent(prompt)
    return invoke_agent(agent, prompt, session_id=session_id)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: specialized_agents.py <agent> <prompt>")
        sys.exit(1)
    agent = sys.argv[1]
    prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "hello"
    result = invoke_agent(agent, prompt)
    print(json.dumps(result, indent=2)[:2000])
