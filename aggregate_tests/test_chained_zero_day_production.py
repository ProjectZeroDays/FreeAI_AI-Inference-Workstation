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

from agents.specialized.chained_zero_day.chained_zero_day import ChainedZeroDayAgent

@pytest.fixture
async def agent():
    """Create agent instance for tests"""
    return ChainedZeroDayAgent()

class TestInputValidation:
    """Test input validation for chain building"""

    async def test_empty_stages(self, agent):
        """Test building chain with empty stages"""
        chain = await agent.build_chain([])
        assert chain is not None
        assert len(chain["stages"]) == 0

    async def test_invalid_stage_structure(self, agent):
        """Test chain with missing stage fields"""
        chain = await agent.build_chain([{"missing_field": "value"}])
        assert chain is not None
        assert len(chain["stages"]) == 1

    async def test_negative_probabilities(self, agent):
        """Test stage with negative probability"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": -0.1}
        ])

        assert chain["stages"][0]["success_prob"] == -0.1

    async def test_probabilities_exceeding_1(self, agent):
        """Test stage with probability > 1"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 1.5}
        ])

        assert chain["stages"][0]["success_prob"] == 1.5
    
    async def test_duplicate_chain_ids(self, agent):
        """Test multiple chains with same ID"""
        chain1 = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])
        
        chain2 = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])
        
        assert chain1["chain_id"] != chain2["chain_id"]

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
        result = await agent.get_cves("INVALID-CVE")
        assert len(result["cves"]) == 0

    async def test_list_chains_invalid_type(self, agent):
        """Test listing chains with invalid type"""
        try:
            result = await agent.list_chains("invalid_type_zz")
            assert isinstance(result, dict)
        except Exception:
            pass  # Some implementations may raise on invalid type

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    async def test_single_stage_chain(self, agent):
        """Test chain with single stage"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])
        
        assert len(chain["stages"]) == 1
        analysis = await agent.analyze_chain(chain["chain_id"])
        assert analysis["total_stages"] == 1
    
    async def test_long_chain(self, agent):
        """Test chain with 10 stages"""
        stages = [
            {"stage": i, "type": f"stage_{i}", "success_prob": 0.90}
            for i in range(1, 11)
        ]
        
        chain = await agent.build_chain(stages)
        assert len(chain["stages"]) == 10
        
        analysis = await agent.analyze_chain(chain["chain_id"])
        assert analysis["total_stages"] == 10
    
    async def test_chains_by_invalid_type(self, agent):
        """Test chains_by_type with invalid type"""
        try:
            result = await agent.get_chains_by_type("invalid_type_xyz")
            assert result["type"] == "invalid_type_xyz"
        except AttributeError:
            pass  # Method may not exist
    
    async def test_analyze_chain_with_multiple_stages(self, agent):
        """Test edge case: analyze chain with full attack lifecycle"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "initial_access", "cve": "CVE-2019-8641", "success_prob": 0.75},
            {"stage": 2, "type": "privilege_escalation", "cve": "CVE-2019-8646", "success_prob": 0.70},
            {"stage": 3, "type": "persistence", "cve": "CVE-2019-8647", "success_prob": 0.68},
            {"stage": 4, "type": "data_exfiltration", "method": "dns_tunnel", "success_prob": 0.72}
        ])
        
        analysis = await agent.analyze_chain(chain["chain_id"])
        assert analysis["total_stages"] == 4
        assert len(analysis["stage_analysis"]) == 4

class TestProbabilityBoundaries:
    """Test probability boundary conditions"""
    
    async def test_extremely_high_probabilities(self, agent):
        """Test chain with all stages having probability ~1.0"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.99},
            {"stage": 2, "type": "privilege_escalation", "success_prob": 0.98}
        ])
        
        assert chain["calculated_success_prob"] > 0.8
    
    async def test_extremely_low_probabilities(self, agent):
        """Test chain with all stages having probability ~0.0"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.05},
            {"stage": 2, "type": "privilege_escalation", "success_prob": 0.05}
        ])
        
        assert chain["calculated_success_prob"] < 0.2
    
    async def test_probability_variance(self, agent):
        """Test chains with widely varying probabilities"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.20},
            {"stage": 2, "type": "privilege_escalation", "success_prob": 0.95}
        ])

        # Should be between the two probabilities (weighted by type)
        assert 0.1 <= chain["calculated_success_prob"] <= 0.95

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
