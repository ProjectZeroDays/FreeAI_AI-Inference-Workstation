#!/usr/bin/env python3
import os

import requests

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")


def call_router(prompt: str, max_tokens: int = 2048,
                temperature: float = 0.2):
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    r = requests.post(ROUTER_URL, json=payload)
    r.raise_for_status()
    return r.json()


def project_scaffolding_agent(spec: str):
    prompt = f"""
You are a senior production engineer.

Task: Turn this spec into a production-ready project.

Spec:
{spec}

Deliver:
- Architecture overview
- Tech stack
- Directory structure
- Key services/modules
- Data models
- API contracts
- CI/CD outline
- Infra notes (Docker/K8s if relevant)
"""
    return call_router(prompt)


def refactor_agent(code: str, goals: str = "clean, idiomatic, maintainable"):
    prompt = f"""
You are a refactoring specialist.

Task: Refactor the following code.

Goals: {goals}

Code:
```code
{code}
```

Deliver:
- Refactored code
- Brief explanation of changes
"""
    return call_router(prompt)


def debug_agent(code: str, error: str):
    prompt = f"""
You are a debugging specialist.

Task: Find and fix the bug.

Code:
```code
{code}
```

Error:
{error}

Deliver:
- Root cause explanation
- Fixed code
- Notes on prevention
"""
    return call_router(prompt)


def analysis_agent(context: str, question: str):
    prompt = f"""
You are a reasoning specialist.

Context:
{context}

Question:
{question}

Think step by step, then answer.
"""
    return call_router(prompt)


if __name__ == "__main__":
    print("[orchestrator] Example run: project scaffolding")
    spec = ("Build a REST API for a rideshare app with auth, "
            "trips, payments, and admin dashboard.")
    result = project_scaffolding_agent(spec)
    print(result["model_used"])
    print(result["response"])
