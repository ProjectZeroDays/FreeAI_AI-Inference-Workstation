#!/usr/bin/env python3
"""Tests for SecurityScanner agent."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from securityscanneragent import SecurityScanner


def test_describe():
    agent = SecurityScanner()
    result = agent.describe()
    assert result["name"] == "security_scanner"
    assert "description" in result
    assert result["category"] == "security"


def test_capabilities():
    agent = SecurityScanner()
    desc = agent.describe()
    assert "capabilities" in desc
    assert len(desc["capabilities"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])