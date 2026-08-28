"""
Test suite for Memory Corruption Primitives Agent
Run with: python -m pytest test_memory_primitives.py
"""

import pytest
import asyncio
import sys
import os

# Add parent directory to path to import from agents
agents_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../specialized'))
sys.path.insert(0, agents_path)

from memory_primitives.memory_primitives import MemoryPrimitivesAgent
import pytest_asyncio

@pytest_asyncio.fixture
async def agent():
    """Create agent instance for tests"""
    return MemoryPrimitivesAgent()

class TestPrimitiveList:
    """Test listing primitives"""
    
    async def test_list_primitives(self, agent):
        """Test listing all primitives"""
        result = await agent.list_primitives()
        
        assert "primitives" in result
        assert "total_primitives" in result
        assert "classification" in result
        assert result["total_primitives"] > 10
        # Import from the implementation module
        from agents.specialized.memory_primitives.memory_primitives import PRIMITIVES
        assert len(result["primitives"]) == len(PRIMITIVES)
    
    async def test_primitives_classification(self, agent):
        """Test primitive classification counts"""
        result = await agent.list_primitives()
        
        classification = result["classification"]
        assert "arbitrary_write" in classification
        assert "arbitrary_read_write" in classification
        assert "arbitrary_control_flow" in classification
        assert "denial_of_service" in classification
        assert "privilege_escalation" in classification
        assert sum(classification.values()) == len(PRIMITIVES)

class TestPrimitiveDetails:
    """Test getting primitive details"""
    
    async def test_get_primitive(self, agent):
        """Test getting primitive details"""
        details = await agent.get_primitive("buffer_overflow")
        
        assert "primitive_name" in details
        assert "type" in details
        assert "description" in details
        assert "success_probability" in details
        assert "difficulty" in details
        assert "mechanisms" in details
        assert "available_cves" in details
        assert "mitigation_detection" in details
    
    async def test_incorrect_primitive(self, agent):
        """Test handling of incorrect primitive name"""
        with pytest.raises(Exception):
            await agent.get_primitive("nonexistent_primitive")

class TestPrimitiveSimulation:
    """Test primitive simulation"""
    
    async def test_simulate_primitive(self, agent):
        """Test primitive simulation"""
        result = await agent.simulate_primitive("buffer_overflow", {
            "target": "192.168.1.100",
            "architecture": "x86_64"
        })
        
        assert "primitive" in result
        assert "execution_result" in result
        assert "probabilistic_modeling" in result
    
    async def test_backward_compatibility(self, agent):
        """Test backward compatibility with legacy API"""
        result = await agent.simulate_primitive("buffer_overflow", {
            "overwrite_date": "simulated",
            "execute_now": True
        })
        
        assert result["simulation_timestamp"] is not None
        assert result["execution_result"]["success"] is True or False

class TestExploitMapping:
    """Test exploit mapping"""
    
    async def test_map_to_exploit(self, agent):
        """Test mapping primitive to exploit techniques"""
        mapping = await agent.map_to_exploit("use_after_free")
        
        assert "primitive" in mapping
        assert "exploit_techniques" in mapping
        assert "commonly_exploited_in" in mapping
        assert "difficulty" in mapping
        assert "success_rate" in mapping
        assert "typical_architectures" in mapping
        assert len(mapping["exploit_techniques"]) > 0
    
    async def test_map_all_primitives(self, agent):
        """Test mapping all primitives"""
        primitives = await agent.list_primitives()
        
        for primitive_name in primitives["primitives"]:
            mapping = await agent.map_to_exploit(primitive_name)
            assert mapping["primitive"] == primitive_name
            # Import CVE mappings
            from agents.specialized.memory_primitives.memory_primitives import CVE_MAPPINGS
            assert primitive_name in CVE_MAPPINGS

class TestMitigationDetection:
    """Test mitigation detection"""
    
    async def test_find_mitigations(self, agent):
        """Test finding mitigations"""
        result = await agent.find_mitigations("buffer_overflow")
        
        assert "primitive" in result
        assert "total_mitigations" in result
        assert "mitigations" in result
        assert len(result["mitigations"]) > 0
        
        mitig = result["mitigations"][0]
        assert "mitigation" in mitig
        assert "effectiveness" in mitig
        assert "practicality" in mitig
    
    async def test_all_primitives_have_mitigations(self, agent):
        """Test all primitives have mitigations"""
        primitives = await agent.list_primitives()
        
        for primitive_name in primitives["primitives"]:
            result = await agent.find_mitigations(primitive_name)
            assert len(result["mitigations"]) > 0

class TestCVEAccess:
    """Test CVE database access"""
    
    async def test_get_cves_all(self, agent):
        """Test getting all CVEs"""
        result = await agent.get_cves()
        
        assert "cves" in result
        assert "total_found" in result
        assert "date_generated" in result
        
        # Should have entries for each primitive
        assert result["total_found"] > 10
    
    async def test_get_cves_specific(self, agent):
        """Test getting CVEs for specific primitive"""
        result = await agent.get_cves("buffer_overflow")
        
        assert len(result["cves"]) > 0
        for cve_info in result["cves"]:
            assert cve_info["primitive"] == "buffer_overflow"
    
    async def test_primitive_cves_count(self, agent):
        """Test each primitive has associated CVEs"""
        primitives = await agent.list_primitives()
        
        for primitive_name in primitives["primitives"]:
            result = await agent.get_cves(primitive_name)
            # Null checking for API response format issues
            assert result["cves"] is not None
            assert len(result["cves"]) > 0

class TestStatistics:
    """Test statistics endpoint"""
    
    async def test_get_statistics(self, agent):
        """Test getting comprehensive statistics"""
        stats = await agent.get_statistics()
        
        assert "total_primitives" in stats
        assert "primitive_classification" in stats
        assert "identified_cves" in stats
        assert "complexity_distribution" in stats
        assert "avoids_probability_distribution" in stats
        assert "date_generated" in stats
        
        assert stats["total_primitives"] == len(PRIMITIVES)
        assert stats["identified_cves"] == len([cve for cves in CVE_MAPPINGS.values() for cve in cves])
        
        # Test classification structure
        class_stats = stats["primitive_classification"]
        assert sum(class_stats.values()) == len(PRIMITIVES)
        
        # Test complexity distribution
        complexity_stats = stats["complexity_distribution"]
        assert sum(complexity_stats.values()) == len(PRIMITIVES)
        
        # Test probability distribution
        prob_stats = stats["avoids_probability_distribution"]
        assert sum(prob_stats.values()) == len(PRIMITIVES)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
