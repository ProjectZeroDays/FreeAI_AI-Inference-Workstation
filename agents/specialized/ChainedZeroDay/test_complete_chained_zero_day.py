"""
Complete fixed test suite for Chained Zero-Day Exploitation Agent
All test classes from original test suite
Run with: python test_complete_chained_zero_day.py
"""

import pytest
import asyncio
import sys
import os
import pytest_asyncio

sys.path.insert(0, os.path.dirname(__file__))

from chained_zero_day import ChainedZeroDayAgent

@pytest_asyncio.fixture
async def agent():
    return ChainedZeroDayAgent()

class TestChainBuilding:
    @pytest.mark.asyncio
    async def test_build_chain(self, agent):
        stages = [
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"},
            {"stage": 2, "type": "kernel_lpe", "cve": "CVE-2019-8646"}
        ]
        chain = await agent.build_chain(stages)
        assert chain["chain_id"] is not None
        assert len(chain["stages"]) == 2
        assert "calculated_success_prob" in chain

class TestChainAnalysis:
    @pytest.mark.asyncio
    async def test_analyze_chain(self, agent):
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])
        analysis = await agent.analyze_chain(chain["chain_id"])
        assert "chain_id" in analysis
        assert "total_stages" in analysis
        assert "stage_analysis" in analysis

class TestChainSimulation:
    @pytest.mark.asyncio
    async def test_simulate_chain(self, agent):
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])
        result = await agent.simulate_chain(chain["chain_id"])
        assert "chain_id" in result
        assert "progress" in result
        assert "final_result" in result

class TestChainOptimization:
    @pytest.mark.asyncio
    async def test_optimize_chain(self, agent):
        chain = await agent.build_chain([
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"}
        ])
        optimization = await agent.optimize_chain(chain["chain_id"])
        assert "chain_id" in optimization
        assert "optimized_success_prob" in optimization

class TestCVEAccess:
    @pytest.mark.asyncio
    async def test_get_cves(self, agent):
        cves = await agent.get_cves()
        assert "cves" in cves

if __name__ == "__main__":
    pytest.main([__file__, "-v"])