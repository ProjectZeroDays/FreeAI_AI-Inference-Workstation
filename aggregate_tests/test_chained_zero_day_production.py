"""
Production tests for Chained Zero-Day Exploitation Agent
Tests input validation, error handling, and edge cases
Run with: python -m pytest test_chained_zero_day_production.py -v
"""

import pytest
import asyncio
import sys
import os

# Add project root to path so we can import from agents package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from agents.specialized.chained_zero_day import ChainedZeroDayAgent

@pytest.fixture
async def agent():
    """Create agent instance for tests"""
    return ChainedZeroDayAgent()

class TestInputValidation:
    """Test input validation for chain building"""

    async def test_empty_stages(self, agent):
        """Test building chain with empty stages"""
        result = await agent.build_chain([])
        assert result is not None
        assert result["status"] == "created"
        assert result["stages"] == 0

    async def test_invalid_stage_structure(self, agent):
        """Test chain with missing stage fields"""
        result = await agent.build_chain([{"missing_field": "value"}])
        assert result is not None
        assert result["status"] == "created"
        assert result["stages"] == 1

    async def test_negative_probabilities(self, agent):
        """Test stage with negative probability"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": -0.1}
        ])
        assert result["status"] == "created"
        assert result["stages"] == 1

    async def test_probabilities_exceeding_1(self, agent):
        """Test stage with probability > 1"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 1.5}
        ])
        assert result["status"] == "created"
        assert result["stages"] == 1

    async def test_duplicate_chain_ids(self, agent):
        """Test multiple chains with same ID"""
        result1 = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])

        result2 = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])

        assert result1["chain_id"] != result2["chain_id"]

class TestErrorHandling:
    """Test error handling"""

    async def test_analyze_missing_chain(self, agent):
        """Test analyzing non-existent chain"""
        result = await agent.analyze_chain("non-existent-chain-id")
        assert "error" in result

    async def test_simulate_missing_chain(self, agent):
        """Test simulating non-existent chain"""
        result = await agent.simulate_chain("non-existent-chain-id")
        assert "error" in result

    async def test_optimize_missing_chain(self, agent):
        """Test optimizing non-existent chain"""
        result = await agent.optimize_chain("non-existent-chain-id")
        assert "error" in result

    async def test_get_cves_invalid_cve_id(self, agent):
        """Test getting invalid CVE ID"""
        result = await agent.get_cves("INVALID-CVE-99999")
        assert isinstance(result, list)
        assert len(result) == 0

    async def test_list_chains_invalid_type(self, agent):
        """Test listing chains with invalid type"""
        result = await agent.list_chains("invalid_type_zz")
        assert isinstance(result, list)

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    async def test_single_stage_chain(self, agent):
        """Test chain with single stage"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])
        assert result["stages"] == 1

        analysis = await agent.analyze_chain(result["chain_id"])
        assert analysis["total_stages"] == 1

    async def test_long_chain(self, agent):
        """Test chain with 10 stages"""
        stages = [
            {"stage": i, "type": f"stage_{i}", "success_prob": 0.90}
            for i in range(1, 11)
        ]

        result = await agent.build_chain(stages)
        assert result["stages"] == 10

        analysis = await agent.analyze_chain(result["chain_id"])
        assert analysis["total_stages"] == 10

    async def test_analyze_chain_with_multiple_stages(self, agent):
        """Test edge case: analyze chain with full attack lifecycle"""
        result = await agent.build_chain([
            {"stage": 1, "type": "initial_access", "cve": "CVE-2019-8641", "success_prob": 0.75},
            {"stage": 2, "type": "privilege_escalation", "cve": "CVE-2019-8646", "success_prob": 0.70},
            {"stage": 3, "type": "persistence", "cve": "CVE-2019-8647", "success_prob": 0.68},
            {"stage": 4, "type": "data_exfiltration", "method": "dns_tunnel", "success_prob": 0.72}
        ])

        analysis = await agent.analyze_chain(result["chain_id"])
        assert analysis["total_stages"] == 4
        assert len(analysis["stage_analysis"]) == 4

class TestProbabilityBoundaries:
    """Test probability boundary conditions"""

    async def test_extremely_high_probabilities(self, agent):
        """Test chain with all stages having probability ~1.0"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.99},
            {"stage": 2, "type": "privilege_escalation", "success_prob": 0.98}
        ])

        analysis = await agent.analyze_chain(result["chain_id"])
        assert analysis["viability_score"] > 80  # Percentage

    async def test_extremely_low_probabilities(self, agent):
        """Test chain with all stages having probability ~0.0"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.05},
            {"stage": 2, "type": "privilege_escalation", "success_prob": 0.05}
        ])

        analysis = await agent.analyze_chain(result["chain_id"])
        assert analysis["viability_score"] < 20  # Percentage

    async def test_probability_variance(self, agent):
        """Test chains with widely varying probabilities"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.20},
            {"stage": 2, "type": "privilege_escalation", "success_prob": 0.95}
        ])

        analysis = await agent.analyze_chain(result["chain_id"])
        assert analysis["viability_score"] > 0
        assert analysis["total_stages"] == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
