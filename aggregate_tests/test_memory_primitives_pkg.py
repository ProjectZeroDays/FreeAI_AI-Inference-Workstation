"""
Test suite for Memory Corruption Primitives Agent (aggregate tests).
Tests the package-level API: agents.specialized.memory_primitives
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from agents.specialized.memory_primitives import MemoryPrimitivesAgent, PRIMITIVES, CVE_MAPPINGS


class TestPrimitiveList:
    """Test listing primitives."""

    def test_list_primitives(self):
        agent = MemoryPrimitivesAgent()
        result = agent.list_primitives()

        assert "primitives" in result
        assert "count" in result
        assert result["count"] >= 10
        assert len(result["primitives"]) == len(PRIMITIVES)

    def test_primitives_count_matches_constants(self):
        agent = MemoryPrimitivesAgent()
        result = agent.list_primitives()
        assert result["count"] == len(PRIMITIVES)
        assert result["count"] == len(CVE_MAPPINGS)


class TestPrimitiveDetails:
    """Test getting primitive details."""

    def test_get_primitive(self):
        agent = MemoryPrimitivesAgent()
        details = agent.get_primitive("buffer_overflow")

        assert "name" in details
        assert "description" in details
        assert "difficulty" in details
        assert "impact" in details
        assert "real_world_cves" in details
        assert "mitigations" in details

    def test_get_primitive_not_found(self):
        agent = MemoryPrimitivesAgent()
        details = agent.get_primitive("nonexistent_primitive")
        assert "error" in details
        assert "status" in details

    def test_all_primitives_have_details(self):
        agent = MemoryPrimitivesAgent()
        for name in PRIMITIVES:
            details = agent.get_primitive(name)
            assert "name" in details, f"Missing details for {name}"


class TestPrimitiveSimulation:
    """Test primitive simulation."""

    def test_simulate_primitive(self):
        agent = MemoryPrimitivesAgent()
        result = agent.simulate_primitive("buffer_overflow", {
            "target": "192.168.1.100",
            "architecture": "x86_64",
        })

        assert "primitive" in result
        assert "status" in result
        assert result["status"] == "simulated"
        assert "details" in result

    def test_simulate_unknown_primitive(self):
        agent = MemoryPrimitivesAgent()
        result = agent.simulate_primitive("nonexistent")
        assert "error" in result

    def test_simulation_history(self):
        agent = MemoryPrimitivesAgent()
        agent.simulate_primitive("buffer_overflow")
        agent.simulate_primitive("use_after_free")
        history = agent.get_simulations()
        assert history["count"] == 2


class TestExploitMapping:
    """Test exploit mapping."""

    def test_map_to_exploit(self):
        agent = MemoryPrimitivesAgent()
        mapping = agent.map_to_exploit("use_after_free")

        assert "primitive" in mapping
        assert "techniques" in mapping
        assert len(mapping["techniques"]) > 0
        assert "reliability" in mapping

    def test_map_all_primitives(self):
        agent = MemoryPrimitivesAgent()
        result = agent.list_primitives()
        for prim in result["primitives"]:
            name = prim["name"]
            mapping = agent.map_to_exploit(name)
            assert mapping["primitive"] == name
            assert name in CVE_MAPPINGS


class TestMitigationDetection:
    """Test mitigation detection."""

    def test_find_mitigations(self):
        agent = MemoryPrimitivesAgent()
        result = agent.find_mitigations("buffer_overflow")

        assert "primitive" in result
        assert "mitigations" in result
        assert len(result["mitigations"]) > 0
        assert "count" in result

    def test_all_primitives_have_mitigations(self):
        agent = MemoryPrimitivesAgent()
        result = agent.list_primitives()
        for prim in result["primitives"]:
            name = prim["name"]
            mit_result = agent.find_mitigations(name)
            assert len(mit_result["mitigations"]) > 0, f"No mitigations for {name}"


class TestCVEAccess:
    """Test CVE database access."""

    def test_get_cves_all(self):
        agent = MemoryPrimitivesAgent()
        result = agent.get_cves()

        assert "cves_by_primitive" in result
        assert "total_cves" in result
        assert "status" in result
        assert result["total_cves"] > 0

    def test_each_primitive_has_cves(self):
        agent = MemoryPrimitivesAgent()
        result = agent.get_cves()
        for prim_name in PRIMITIVES:
            assert prim_name in result["cves_by_primitive"]
            assert len(result["cves_by_primitive"][prim_name]) > 0


class TestDescribe:
    """Test agent description."""

    def test_describe(self):
        agent = MemoryPrimitivesAgent()
        result = agent.describe()

        assert result["name"] == "memory_primitives"
        assert "capabilities" in result
        assert "primitive_count" in result
        assert result["primitive_count"] == 10


class TestConstants:
    """Test module-level constants."""

    def test_primitives_is_dict(self):
        assert hasattr(PRIMITIVES, 'keys')
        assert len(PRIMITIVES) == 10

    def test_cve_mappings_is_dict(self):
        assert hasattr(CVE_MAPPINGS, 'keys')
        assert len(CVE_MAPPINGS) == 10

    def test_primitives_keys_match_constants(self):
        agent = MemoryPrimitivesAgent()
        result = agent.list_primitives()
        prim_names = {p["name"] for p in result["primitives"]}
        assert prim_names == set(PRIMITIVES.keys())
        assert prim_names == set(CVE_MAPPINGS.keys())


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
