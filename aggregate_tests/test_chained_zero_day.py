"""
Test suite for Chained Zero-Day Exploitation Agent
Run with: python -m pytest test_chained_zero_day.py
"""

import pytest
import asyncio
import sys
import os

# Add project root to path so we can import from agents package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from agents.specialized.chained_zero_day.chained_zero_day import ChainedZeroDayAgent
import pytest_asyncio

@pytest_asyncio.fixture
async def agent():
    """Create agent instance for tests"""
    return ChainedZeroDayAgent()

class TestChainBuilding:
    """Test chain building functionality"""
    
    async def test_build_chain(self, agent):
        """Test building a simple chain"""
        stages = [
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"},
            {"stage": 2, "type": "kernel_lpe", "cve": "CVE-2019-8646"}
        ]
        
        chain = await agent.build_chain(stages)
        
        assert chain["chain_id"] is not None
        assert chain["created_at"] is not None
        assert len(chain["stages"]) == 2
        assert "calculated_success_prob" in chain
        assert 0 <= chain["calculated_success_prob"] <= 0.95
    
    async def test_chain_probability_calculation(self, agent):
        """Test probability calculation"""
        stages = [
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641", "success_prob": 0.95},
            {"stage": 2, "type": "privilege_escalation", "cve": "CVE-2019-8646", "success_prob": 0.90}
        ]
        
        chain = await agent.build_chain(stages)
        
        assert chain["calculated_success_prob"] > 0.6  # Both high probabilities
        
    async def test_chain_success_probability_stages(self, agent):
        """Test probability calculation per stage"""
        stages = [
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.50},  # Low
            {"stage": 2, "type": "privilege_escalation", "success_prob": 0.95}  # High
        ]
        
        chain = await agent.build_chain(stages)
        
        # Middle stage should pull probability up
        assert chain["calculated_success_prob"] > 0.6

class TestChainAnalysis:
    """Test chain analysis functionality"""
    
    async def test_analyze_chain(self, agent):
        """Test chain analysis"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])
        
        analysis = await agent.analyze_chain(chain["chain_id"])
        
        assert "chain_id" in analysis
        assert "total_stages" in analysis
        assert "stage_analysis" in analysis
        assert "dependency_graph" in analysis
        assert "risk_assessment" in analysis
        assert len(analysis["stage_analysis"]) == 1
    
    async def test_risk_assessment(self, agent):
        """Test risk assessment"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.50}
        ])
        
        analysis = await agent.analyze_chain(chain["chain_id"])
        
        assert "overall_detection_probability" in analysis["risk_assessment"]
        assert "critical_failure_points" in analysis["risk_assessment"]
        assert analysis["risk_assessment"]["critical_failure_points"] >= 0

class TestChainSimulation:
    """Test chain simulation functionality"""
    
    async def test_simulate_chain(self, agent):
        """Test chain simulation"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])
        
        result = await agent.simulate_chain(chain["chain_id"])
        
        assert "chain_id" in result
        assert "progress" in result
        assert "final_result" in result
        assert len(result["progress"]) == 1
        
        # Progress should have realistic structure
        stage_result = result["progress"][0]
        assert "stage_id" in stage_result
        assert "result" in stage_result
        assert stage_result["result"] in ["success", "failed"]
    
    async def test_create_final_result_success(self, agent):
        """Test final result calculation for mostly successful chain"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.95}
        ])
        
        result = await agent.simulate_chain(chain["chain_id"])
        
        # With high probability, should succeed
        assert result["final_result"]["exploit_established"] is True
        assert result["final_result"]["overall_status"] in ["success", "partial_failure"]
    
    async def test_final_result_partial_failure(self, agent):
        """Test final result for partially successful chain"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.30}  # Low probability
        ])
        
        result = await agent.simulate_chain(chain["chain_id"])
        
        # With low probability, might fail
        assert result["final_result"]["exploit_established"] is True or False

class TestChainOptimization:
    """Test chain optimization functionality"""
    
    async def test_optimize_chain(self, agent):
        """Test chain optimization"""
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])
        
        optimization = await agent.optimize_chain(chain["chain_id"])
        
        assert "chain_id" in optimization
        assert "optimized_success_prob" in optimization
        assert "weaknesses" in optimization
        assert "improvements" in optimization
        assert "solutions" in optimization
        assert len(optimization["weaknesses"]) >= 0
        assert len(optimization["improvements"]) > 0

class TestCVEAccess:
    """Test CVE database access"""
    
    async def test_get_cves(self, agent):
        """Test CVE database access"""
        cves = await agent.get_cves()
        
        assert "cves" in cves
        assert "total_found" in cves
    
    async def test_get_specific_cve(self, agent):
        """Test specific CVE lookup"""
        cves = await agent.get_cves("CVE-2019-8641")
        
        assert len(cves["cves"]) > 0
        any_cve = cves["cves"][0]
        assert "name" in any_cve
        assert "type" in any_cve

class TestRealWorldChains:
    """Test real-world chains functionality"""
    
    async def test_list_chains(self, agent):
        """Test listing real-world chains"""
        chains = await agent.list_chains()
        
        assert "chains" in chains
        assert "total_chains" in chains
        assert "chain_types" in chains
        assert len(chains["chains"]) > 0
    
    async def test_specific_real_world_chain(self, agent):
        """Test accessing specific real-world chain"""
        chains = await agent.list_chains()
        
        # Find Pegasus chain
        pegasus_chain = next((c for c in chains["chains"] if c.get("name") == "Pegasus"), None)
        
        if pegasus_chain:
            assert "stages" in pegasus_chain
            assert len(pegasus_chain["stages"]) == 3
            assert pegasus_chain["stages"][0]["type"] == "initial_access"
            assert pegasus_chain["total_success_prob"] is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
