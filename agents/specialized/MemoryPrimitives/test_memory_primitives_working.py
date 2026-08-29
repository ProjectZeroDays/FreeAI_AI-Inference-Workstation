"""
Working test suite for Memory Corruption Primitives Agent
Run with: python test_memory_primitives_working.py
"""

import pytest
import asyncio
import sys
import os
import pytest_asyncio

# Import the agent directly
sys.path.insert(0, os.path.dirname(__file__))

from memory_primitives import MemoryPrimitivesAgent

@pytest_asyncio.fixture
async def agent():
    """Create agent instance for tests"""
    return MemoryPrimitivesAgent()

class TestPrimitiveList:
    """Test listing primitives"""

    @pytest.mark.asyncio
    async def test_list_primitives(self, agent):
        """Test listing all primitives"""
        result = await agent.list_primitives()

        assert "primitives" in result
        assert "total_primitives" in result
        assert "classification" in result
        assert result["total_primitives"] == 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])