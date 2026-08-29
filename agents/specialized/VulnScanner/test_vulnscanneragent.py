#!/usr/bin/env python3
"""Tests for VulnScanner agent."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vulnscanneragent import VulnScanner


def test_describe():
    agent = VulnScanner()
    result = agent.describe()
    assert result["name"] == "vuln_scanner"
    assert "description" in result
    assert result["category"] == "red_teaming"


def test_capabilities():
    agent = VulnScanner()
    desc = agent.describe()
    assert "capabilities" in desc
    assert len(desc["capabilities"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])