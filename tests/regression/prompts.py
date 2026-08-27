"""Prompt regression suite: 50 golden prompts across 5 categories.

Run: pytest tests/regression/prompts.py -v
"""
import json
import os
import statistics
import sys

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "router"))

import router as router_mod  # noqa: E402

# ── golden prompts ──────────────────────────────────────────────────────

GOLDEN_PROMPTS = [
    # ── coding (10) ──────────────────────────────────────────────────
    {"id": "c01", "cat": "coding", "prompt": "Build a production REST API with FastAPI and SQLAlchemy",
     "expect_type": "full_project", "min_tokens": 100},
    {"id": "c02", "cat": "coding", "prompt": "Refactor this function to use type hints and async/await",
     "expect_type": "refactor", "min_tokens": 64},
    {"id": "c03", "cat": "coding", "prompt": "Write unit tests for the authentication module",
     "expect_type": "full_project", "min_tokens": 100},
    {"id": "c04", "cat": "coding", "prompt": "Create a Dockerfile for a Python Flask microservice",
     "expect_type": "full_project", "min_tokens": 80},
    {"id": "c05", "cat": "coding", "prompt": "Debug the memory leak in this WebSocket server",
     "expect_type": "refactor", "min_tokens": 64},
    {"id": "c06", "cat": "coding", "prompt": "Implement a rate limiter middleware for an HTTP server",
     "expect_type": "full_project", "min_tokens": 100},
    {"id": "c07", "cat": "coding", "prompt": "Optimize this SQL query for a PostgreSQL database with millions of rows",
     "expect_type": "refactor", "min_tokens": 64},
    {"id": "c08", "cat": "coding", "prompt": "Set up a CI/CD pipeline using GitHub Actions for a monorepo",
     "expect_type": "full_project", "min_tokens": 100},
    {"id": "c09", "cat": "coding", "prompt": "Rewrite this bash script in Python with proper error handling",
     "expect_type": "refactor", "min_tokens": 64},
    {"id": "c10", "cat": "coding", "prompt": "Scaffold a Next.js 14 app with TypeScript and Tailwind CSS",
     "expect_type": "full_project", "min_tokens": 100},

    # ── math (10) ────────────────────────────────────────────────────
    {"id": "m01", "cat": "math", "prompt": "Calculate the eigenvalues of a 3x3 matrix",
     "expect_type": "analysis", "min_tokens": 64},
    {"id": "m02", "cat": "math", "prompt": "Solve the differential equation y'' + 4y' + 4y = 0",
     "expect_type": "analysis", "min_tokens": 64},
    {"id": "m03", "cat": "math", "prompt": "Compute the Fourier transform of a Gaussian function step by step",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "m04", "cat": "math", "prompt": "Prove that the sum of angles in a triangle is 180 degrees",
     "expect_type": "analysis", "min_tokens": 64},
    {"id": "m05", "cat": "math", "prompt": "Find the determinant of a 4x4 matrix using cofactor expansion",
     "expect_type": "analysis", "min_tokens": 64},
    {"id": "m06", "cat": "math", "prompt": "Explain the central limit theorem with a numerical example",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "m07", "cat": "math", "prompt": "Derive the quadratic formula from completing the square",
     "expect_type": "analysis", "min_tokens": 64},
    {"id": "m08", "cat": "math", "prompt": "Calculate the probability of getting exactly 3 heads in 5 coin flips",
     "expect_type": "analysis", "min_tokens": 64},
    {"id": "m09", "cat": "math", "prompt": "Solve for x: log₂(x) + log₂(x-2) = 3",
     "expect_type": "analysis", "min_tokens": 64},
    {"id": "m10", "cat": "math", "prompt": "Compute the integral of x²·e^x using integration by parts",
     "expect_type": "analysis", "min_tokens": 64},

    # ── reasoning (10) ───────────────────────────────────────────────
    {"id": "r01", "cat": "reasoning", "prompt": "Think step by step: why does DNS use UDP instead of TCP?",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "r02", "cat": "reasoning", "prompt": "Analyze the trade-offs between SQL and NoSQL for a social media platform",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "r03", "cat": "reasoning", "prompt": "Reason through the CAP theorem and when to prioritize each property",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "r04", "cat": "reasoning", "prompt": "Break down how a blockchain consensus mechanism works",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "r05", "cat": "reasoning", "prompt": "Explain why HTTPS is preferred over HTTP for authentication flows",
     "expect_type": "analysis", "min_tokens": 64},
    {"id": "r06", "cat": "reasoning", "prompt": "Analyze the security implications of storing passwords in plaintext",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "r07", "cat": "reasoning", "prompt": "Think through the implications of microservices for team organization",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "r08", "cat": "reasoning", "prompt": "Reason about the best caching strategy for a high-traffic e-commerce site",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "r09", "cat": "reasoning", "prompt": "Explain how Rust's ownership model prevents use-after-free bugs",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "r10", "cat": "reasoning", "prompt": "Analyze the trade-offs between gRPC and REST for internal service communication",
     "expect_type": "analysis", "min_tokens": 80},

    # ── creative (10) ────────────────────────────────────────────────
    {"id": "k01", "cat": "creative", "prompt": "Write a short sci-fi story about an AI discovering emotions",
     "expect_type": "general_code", "min_tokens": 200},
    {"id": "k02", "cat": "creative", "prompt": "Create a naming convention for a fantasy RPG character classes",
     "expect_type": "general_code", "min_tokens": 100},
    {"id": "k03", "cat": "creative", "prompt": "Generate a poem about the ocean at midnight in the style of Neruda",
     "expect_type": "general_code", "min_tokens": 80},
    {"id": "k04", "cat": "creative", "prompt": "Design a fictional language with 10 basic words and grammar rules",
     "expect_type": "general_code", "min_tokens": 150},
    {"id": "k05", "cat": "creative", "prompt": "Write a dialogue between Shakespeare and a modern programmer",
     "expect_type": "general_code", "min_tokens": 200},
    {"id": "k06", "cat": "creative", "prompt": "Create a plot outline for a mystery novel set in a space station",
     "expect_type": "general_code", "min_tokens": 150},
    {"id": "k07", "cat": "creative", "prompt": "Generate a bedtime story about a robot who learns to dream",
     "expect_type": "general_code", "min_tokens": 200},
    {"id": "k08", "cat": "creative", "prompt": "Write a haiku about debugging production code on a Friday evening",
     "expect_type": "general_code", "min_tokens": 30},
    {"id": "k09", "cat": "creative", "prompt": "Create a branding name and tagline for a coffee-powered coding tool",
     "expect_type": "general_code", "min_tokens": 64},
    {"id": "k10", "cat": "creative", "prompt": "Design a fictional world where gravity is optional and explain its physics",
     "expect_type": "general_code", "min_tokens": 150},

    # ── knowledge (10) ───────────────────────────────────────────────
    {"id": "z01", "cat": "knowledge", "prompt": "Explain how Docker containers differ from virtual machines",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "z02", "cat": "knowledge", "prompt": "Describe the difference between JWT authentication and session-based auth",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "z03", "cat": "knowledge", "prompt": "What is the Byzantine Generals Problem and how does it relate to consensus?",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "z04", "cat": "knowledge", "prompt": "Explain the concept of idempotency in distributed systems",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "z05", "cat": "knowledge", "prompt": "What are the seven layers of the OSI model and what does each do?",
     "expect_type": "analysis", "min_tokens": 100},
    {"id": "z06", "cat": "knowledge", "prompt": "Describe how B-trees enable efficient database indexing",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "z07", "cat": "knowledge", "prompt": "Explain the concept of eventual consistency in distributed databases",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "z08", "cat": "knowledge", "prompt": "What is the difference between OAuth 2.0 and OpenID Connect?",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "z09", "cat": "knowledge", "prompt": "Describe how GraphQL resolvers work and when to use them",
     "expect_type": "analysis", "min_tokens": 80},
    {"id": "z10", "cat": "knowledge", "prompt": "Explain the concept of a service mesh and its role in microservices",
     "expect_type": "analysis", "min_tokens": 80},
]


# ── fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture()
def client():
    router_mod.app.config["TESTING"] = True
    with router_mod.app.test_client() as c:
        yield c


# ── scoring helpers ──────────────────────────────────────────────────────

def score_format_compliance(response):
    """Response must be a dict with required keys."""
    if not isinstance(response, dict):
        return 0
    has_model = "model_used" in response
    has_type = "task_type" in response
    has_resp = "response" in response
    return (has_model + has_type + has_resp) / 3


def score_response_length(response, min_tokens):
    """Normalize response text length against the minimum threshold."""
    content = response.get("response", {})
    if isinstance(content, dict):
        text = content.get("content", "")
    else:
        text = str(content)
    length = len(text)
    if length >= min_tokens * 3:   # rough char estimate
        return 1.0
    if length >= min_tokens:
        return 0.5
    return 0.0


def score_task_type_accuracy(predicted, expected):
    """1.0 if exact match, 0.5 if related category."""
    if predicted == expected:
        return 1.0
    # analysis-related: math and reasoning both map to analysis
    map_ = {"math": "analysis", "reasoning": "analysis",
            "knowledge": "analysis", "coding": "full_project",
            "creative": "general_code"}
    if map_.get(predicted) == map_.get(expected):
        return 0.5
    return 0.0


# ── test suite ───────────────────────────────────────────────────────────

def test_all_golden_prompts_route(client):
    """Run every golden prompt through /route and collect scores."""
    results = []
    for prompt in GOLDEN_PROMPTS:
        pid = prompt["id"]
        resp = client.post("/route", json={
            "prompt": prompt["prompt"],
            "max_tokens": prompt.get("min_tokens", 64) * 4,
        })
        assert resp.status_code == 200, f"{pid}: got {resp.status_code}"
        body = resp.get_json()
        predicted = body.get("task_type", "unknown")
        format_score = score_format_compliance(body)
        length_score = score_response_length(body, prompt["min_tokens"])
        type_score = score_task_type_accuracy(predicted, prompt["expect_type"])
        overall = (format_score + length_score + type_score) / 3
        results.append({
            "id": pid,
            "cat": prompt["cat"],
            "prompt": prompt["prompt"][:80],
            "predicted": predicted,
            "expected": prompt["expect_type"],
            "format": round(format_score, 2),
            "length": round(length_score, 2),
            "type": round(type_score, 2),
            "overall": round(overall, 2),
        })

    _print_report(results)

    # All prompts must produce a valid response
    assert all(r["format"] > 0 for r in results), "Some prompts returned malformed responses"

    # At least 80% of prompts must pass overall score >= 0.5
    passing = [r for r in results if r["overall"] >= 0.5]
    pct = len(passing) / len(results)
    print(f"Pass rate: {len(passing)}/{len(results)} ({pct*100:.0f}%)")
    assert pct >= 0.8, f"Only {pct*100:.0f}% prompts passed"


def _print_report(results):
    """Print a human-readable regression report."""
    print("\n=== PROMPT REGRESSION REPORT ===")
    cat_scores = {}
    for r in results:
        cat_scores.setdefault(r["cat"], []).append(r["overall"])

    for cat, scores in cat_scores.items():
        avg = round(statistics.mean(scores), 2)
        status = "PASS" if avg >= 0.5 else "FAIL"
        print(f"  [{status}] {cat}: avg={avg}  n={len(scores)}")

    print(f"\n  Total: {len(results)} prompts")
    print(f"  Overall avg: {round(statistics.mean(r['overall'] for r in results), 2)}")
    print("=== END REPORT ===\n")
