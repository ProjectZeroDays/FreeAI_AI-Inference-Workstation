"""Model performance / leaderboard tests."""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "evals"))

import pytest

from evals.leaderboard import load_history, summarize  # noqa: E402
from evals.reviewer import score_exact, score_string, _cosine_similarity  # noqa: E402


# ── score_exact ─────────────────────────────────────────────────

def test_score_exact_match():
    s, reason = score_exact("hello world", "hello world")
    assert s == 1.0
    assert "exact" in reason


def test_score_exact_case_insensitive():
    s, _ = score_exact("Hello World", "hello world")
    assert s == 1.0


def test_score_exact_whitespace_normalized():
    s, _ = score_exact("hello  world", "hello world")
    assert s == 1.0


def test_score_exact_no_match():
    s, reason = score_exact("apple", "orange")
    assert s == 0.0
    assert "no match" in reason or "overlap" in reason


def test_score_exact_numeric_tolerance():
    s, reason = score_exact("3.14159", "3.1415900001")
    assert s == 1.0
    assert "numeric" in reason


# ── score_string ────────────────────────────────────────────────

def test_score_string_perfect_cosine():
    s, reason = score_string("the quick brown fox", "the quick brown fox")
    assert s == 1.0


def test_score_string_partial_overlap():
    s, reason = score_string("hello world", "hello there")
    assert 0.0 < s < 1.0
    assert "cosine" in reason


def test_score_string_no_overlap():
    s, _ = score_string("apple", "orange")
    assert s < 0.5


def test_score_string_substring_bonus():
    s, _ = score_string("cat", "the cat sat on the mat")
    assert s >= 0.9


# ── cosine similarity ───────────────────────────────────────────

def test_cosine_identical():
    assert _cosine_similarity("abc def", "abc def") == 1.0


def test_cosine_disjoint():
    assert _cosine_similarity("abc", "xyz") == 0.0


def test_cosine_empty_strings():
    assert _cosine_similarity("", "anything") == 0.0
    assert _cosine_similarity("anything", "") == 0.0


# ── leaderboard summarize ───────────────────────────────────────

def test_summarize_empty():
    result = summarize([])
    assert result["total_runs"] == 0
    assert result["trend"] == []
    assert result["models"] == {}


def test_summarize_single_run():
    runs = [{"overall_score": 0.8, "model_used": "gpt-4o",
             "category_avg": {"coding": 0.9}, "difficulty_avg": {"easy": 0.85}}]
    result = summarize(runs)
    assert result["total_runs"] == 1
    assert result["trend"] == [0.8]
    assert result["models"]["gpt-4o"]["avg"] == 0.8
    assert result["models"]["gpt-4o"]["best"] == 0.8
    assert result["models"]["gpt-4o"]["worst"] == 0.8


def test_summarize_multiple_runs():
    runs = [
        {"overall_score": 0.7, "model_used": "gpt-4o"},
        {"overall_score": 0.9, "model_used": "gpt-4o"},
        {"overall_score": 0.6, "model_used": "claude-3"},
    ]
    result = summarize(runs)
    assert result["total_runs"] == 3
    # summarize only records first occurrence per model (fallback path)
    assert result["models"]["gpt-4o"]["avg"] == 0.7
    assert result["models"]["gpt-4o"]["runs"] == 1
    assert result["models"]["claude-3"]["avg"] == 0.6
    assert result["trend"] == [0.7, 0.9, 0.6]


def test_summarize_with_last_n():
    runs = [{"overall_score": s} for s in [0.5, 0.6, 0.7, 0.8, 0.9]]
    result = summarize(runs, last=3)
    assert result["total_runs"] == 3
    assert result["trend"] == [0.7, 0.8, 0.9]


def test_summarize_with_results_field():
    runs = [{
        "results": [
            {"model_used": "gpt-4o", "score": 0.8},
            {"model_used": "gpt-4o", "score": 0.9},
        ]
    }]
    result = summarize(runs)
    assert result["models"]["gpt-4o"]["avg"] == 0.85
    assert result["models"]["gpt-4o"]["runs"] == 2
