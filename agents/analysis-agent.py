#!/usr/bin/env python3
import os

import requests

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")


def analyze(context: str, question: str):
    prompt = f"""
You are an analysis agent.

Context:
{context}

Question:
{question}

Think step by step, then answer clearly.
"""
    r = requests.post(ROUTER_URL, json={"prompt": prompt, "max_tokens": 2048})
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    ctx = ("We have a microservice architecture with 5 services "
           "and a shared database.")
    q = "What are the main risks and how should we mitigate them?"
    print(analyze(ctx, q))
