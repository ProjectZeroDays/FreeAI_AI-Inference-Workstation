#!/usr/bin/env python3
import os

import requests

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")


def scaffold_project(spec: str):
    prompt = f"""
You are a production-grade project scaffolding agent.

Spec:
{spec}

Deliver:
- High-level architecture
- Tech stack choice
- Directory layout
- Core modules/services
- Data models
- API endpoints
- CI/CD pipeline outline
- Testing strategy
"""
    r = requests.post(ROUTER_URL,
                      json={"prompt": prompt, "max_tokens": 4096})
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    spec = ("Monorepo with backend (FastAPI), frontend (Next.js), "
            "PostgreSQL, and Docker-based deployment.")
    print(scaffold_project(spec))
