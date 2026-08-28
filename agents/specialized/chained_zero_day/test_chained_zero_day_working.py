"""
Working test suite for Chained Zero-Day Exploitation Agent
Run with: python test_chained_zero_day_working.py
"""

import pytest
import asyncio
import sys
import os
import pytest_asyncio

# Import the agent directly
sys.path.insert(0, os.path.dirname(__file__))

from chained_zero_day import ChainedZeroDayAgent

@pytest_asyncio.fixture
async def agent():
    """Create agent instance for tests"""
    return ChainedZeroDayAgent()

class TestChainBuilding:
    """Test chain building functionality"""

    @pytest.mark.asyncio
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

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
