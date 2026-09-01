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

from agents.specialized.chained_zero_day import ChainedZeroDayAgent
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

        result = await agent.build_chain(stages)

        assert result["status"] == "created"
        assert result["chain_id"] is not None
        assert result["stages"] == 2

    async def test_chain_probability_calculation(self, agent):
        """Test probability calculation via analyze"""
        stages = [
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641", "success_prob": 0.95},
            {"stage": 2, "type": "privilege_escalation", "cve": "CVE-2019-8646", "success_prob": 0.90}
        ]

        result = await agent.build_chain(stages)
        chain_id = result["chain_id"]

        analysis = await agent.analyze_chain(chain_id)
        assert analysis["total_stages"] == 2
        assert analysis["viability_score"] > 0  # Both high probabilities

    async def test_chain_success_probability_stages(self, agent):
        """Test probability calculation per stage"""
        stages = [
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.50},
            {"stage": 2, "type": "privilege_escalation", "success_prob": 0.95}
        ]

        result = await agent.build_chain(stages)
        chain_id = result["chain_id"]

        analysis = await agent.analyze_chain(chain_id)
        assert analysis["total_stages"] == 2
        assert "stage_analysis" in analysis
        assert len(analysis["stage_analysis"]) == 2

class TestChainAnalysis:
    """Test chain analysis functionality"""

    async def test_analyze_chain(self, agent):
        """Test chain analysis"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])

        analysis = await agent.analyze_chain(result["chain_id"])

        assert "chain_id" in analysis
        assert "total_stages" in analysis
        assert "stage_analysis" in analysis
        assert "risk_level" in analysis
        assert "viability_score" in analysis
        assert len(analysis["stage_analysis"]) == 1

    async def test_risk_assessment(self, agent):
        """Test risk assessment"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.50}
        ])

        analysis = await agent.analyze_chain(result["chain_id"])

        assert analysis["risk_level"] in ["high", "medium", "low"]
        assert isinstance(analysis["viability_score"], (int, float))

class TestChainSimulation:
    """Test chain simulation functionality"""

    async def test_simulate_chain(self, agent):
        """Test chain simulation"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])

        sim = await agent.simulate_chain(result["chain_id"])

        assert "chain_id" in sim
        assert "status" in sim
        assert "success" in sim
        assert "stages_completed" in sim
        assert sim["status"] == "simulated"
        assert sim["stages_completed"] == 1

    async def test_simulate_high_probability(self, agent):
        """Test simulation with high probability"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.95}
        ])

        sim = await agent.simulate_chain(result["chain_id"])

        assert sim["success"] is True
        assert sim["success_probability"] > 0.8

    async def test_simulate_low_probability(self, agent):
        """Test simulation with low probability"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "success_prob": 0.30}
        ])

        sim = await agent.simulate_chain(result["chain_id"])

        assert sim["status"] == "simulated"
        assert sim["stages_completed"] == 1

class TestChainOptimization:
    """Test chain optimization functionality"""

    async def test_optimize_chain(self, agent):
        """Test chain optimization"""
        result = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])

        optimization = await agent.optimize_chain(result["chain_id"])

        assert "chain_id" in optimization
        assert "optimization" in optimization
        opt = optimization["optimization"]
        assert "suggested_modifications" in opt
        assert "weaknesses" in opt
        assert "improvements" in opt
        assert len(opt["improvements"]) > 0

class TestCVEAccess:
    """Test CVE database access"""

    async def test_get_cves(self, agent):
        """Test CVE database access"""
        cves = await agent.get_cves()

        assert isinstance(cves, list)
        assert len(cves) > 0
        assert "id" in cves[0]
        assert "name" in cves[0]

    async def test_get_specific_cve(self, agent):
        """Test specific CVE lookup"""
        cves = await agent.get_cves("CVE-2019-8641")

        assert isinstance(cves, list)
        assert len(cves) > 0
        assert cves[0]["id"] == "CVE-2019-8641"
        assert "name" in cves[0]
        assert "type" in cves[0]

class TestRealWorldChains:
    """Test real-world chains functionality"""

    async def test_list_chains(self, agent):
        """Test listing real-world chains"""
        chains = await agent.list_chains()

        assert isinstance(chains, list)
        assert len(chains) > 0
        assert "id" in chains[0]
        assert "name" in chains[0]

    async def test_specific_real_world_chain(self, agent):
        """Test accessing specific real-world chain"""
        chains = await agent.list_chains()

        # Find Pegasus chain
        pegasus_chain = next((c for c in chains if c.get("name") == "Pegasus"), None)

        if pegasus_chain:
            assert "stages" in pegasus_chain
            assert len(pegasus_chain["stages"]) == 3
            assert pegasus_chain["stages"][0]["type"] == "initial_access"
            assert pegasus_chain.get("total_success_prob") is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
