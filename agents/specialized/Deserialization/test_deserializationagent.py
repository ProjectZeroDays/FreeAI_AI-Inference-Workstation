#!/usr/bin/env python3
"""Tests for DeserializationAgent agent."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from deserializationagent import DeserializationAgent


def test_describe():
    agent = DeserializationAgent()
    result = agent.describe()
    assert result["name"] == "deserialization"
    assert "description" in result
    assert result["category"] == "red_teaming"


def test_capabilities():
    agent = DeserializationAgent()
    desc = agent.describe()
    assert "capabilities" in desc
    assert len(desc["capabilities"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])