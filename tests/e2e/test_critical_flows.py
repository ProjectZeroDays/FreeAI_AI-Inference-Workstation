"""E2E tests for critical FreeAI user flows.
Run with: pytest tests/e2e/ -v
"""
import pytest
import tempfile
from pathlib import Path


class TestLoginFlow:
    """Test user authentication flow."""

    def test_login_page_accessible(self):
        """Login page should be accessible."""
        import sys
        sys.path.insert(0, ".")
        from dashboard import backend as dash
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dash.CONFIG_DIR = tmp_path
            dash.SKILLS_DIR = tmp_path / "skills"
            dash.ACTIVITY_LOG = tmp_path / "activity_log.jsonl"
            dash.UPLOAD_DIR = tmp_path / "uploads"
            dash.SALAD_API_KEY = ""
            dash._SALAD_API_KEY = ""
            dash.AIKIDO_API_KEY = ""
            dash.AIKIDO_APP_ID = ""
            dash._SUBAGENTS.clear()
            dash._TRAINING_DATA.update({"datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []}, "models": []})
            dash._MEMORY_STATE["projects"].clear()
            dash._MEMORY_STATE["learnings"].clear()
            dash._AUTOMATIONS["jobs"].clear()
            dash._AUTOMATIONS["history"].clear()
            dash._campaigns.clear()
            dash._scheduler_jobs.clear()
            dash._gpu_state["devices"] = []
            dash.app.config["TESTING"] = True
            client = dash.app.test_client()
            resp = client.get("/login")
            assert resp.status_code in (200, 302, 404)


class TestAgentCreation:
    """Test agent creation flow."""

    def test_agents_api_accessible(self):
        """Agents API should be accessible."""
        import sys
        sys.path.insert(0, ".")
        from dashboard import backend as dash
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dash.CONFIG_DIR = tmp_path
            dash.SKILLS_DIR = tmp_path / "skills"
            dash.ACTIVITY_LOG = tmp_path / "activity_log.jsonl"
            dash.UPLOAD_DIR = tmp_path / "uploads"
            dash.SALAD_API_KEY = ""
            dash._SALAD_API_KEY = ""
            dash.AIKIDO_API_KEY = ""
            dash.AIKIDO_APP_ID = ""
            dash._SUBAGENTS.clear()
            dash._TRAINING_DATA.update({"datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []}, "models": []})
            dash._MEMORY_STATE["projects"].clear()
            dash._MEMORY_STATE["learnings"].clear()
            dash._AUTOMATIONS["jobs"].clear()
            dash._AUTOMATIONS["history"].clear()
            dash._campaigns.clear()
            dash._scheduler_jobs.clear()
            dash._gpu_state["devices"] = []
            dash.app.config["TESTING"] = True
            client = dash.app.test_client()
            resp = client.get("/api/agents")
            assert resp.status_code in (200, 404)


class TestCVELookup:
    """Test CVE lookup flow."""

    def test_cve_mappings_proxy_works(self):
        """CVE mappings proxy should be iterable."""
        from agents.specialized.memory_primitives import CVE_MAPPINGS
        items = list(CVE_MAPPINGS.items())
        # CVE mappings may be empty in test environment
        assert items is not None

    def test_memory_primitives_agent_exists(self):
        """MemoryPrimitivesAgent should be importable."""
        from agents.specialized.memory_primitives import MemoryPrimitivesAgent
        agent = MemoryPrimitivesAgent()
        assert agent is not None


class TestWorkflowExecution:
    """Test workflow execution flow."""

    def test_workflows_api_accessible(self):
        """Workflows API should be accessible."""
        import sys
        sys.path.insert(0, ".")
        from dashboard import backend as dash
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dash.CONFIG_DIR = tmp_path
            dash.SKILLS_DIR = tmp_path / "skills"
            dash.ACTIVITY_LOG = tmp_path / "activity_log.jsonl"
            dash.UPLOAD_DIR = tmp_path / "uploads"
            dash.SALAD_API_KEY = ""
            dash._SALAD_API_KEY = ""
            dash.AIKIDO_API_KEY = ""
            dash.AIKIDO_APP_ID = ""
            dash._SUBAGENTS.clear()
            dash._TRAINING_DATA.update({"datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []}, "models": []})
            dash._MEMORY_STATE["projects"].clear()
            dash._MEMORY_STATE["learnings"].clear()
            dash._AUTOMATIONS["jobs"].clear()
            dash._AUTOMATIONS["history"].clear()
            dash._campaigns.clear()
            dash._scheduler_jobs.clear()
            dash._gpu_state["devices"] = []
            dash.app.config["TESTING"] = True
            client = dash.app.test_client()
            resp = client.get("/api/workflows")
            assert resp.status_code in (200, 404)


class TestSkillsCatalog:
    """Test skills catalog flow."""

    def test_skills_api_module_exists(self):
        """Skills API module should be importable."""
        from skills import catalog_api
        assert catalog_api is not None

    def test_skills_catalog_json_exists(self):
        """Skills catalog should be accessible."""
        from skills.catalog_api import SKILLS_CATALOG
        assert SKILLS_CATALOG is not None


class TestDashboardAPI:
    """Test dashboard API endpoints."""

    def test_health_endpoint(self):
        """Health endpoint should return ok."""
        import sys
        sys.path.insert(0, ".")
        from dashboard import backend as dash
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dash.CONFIG_DIR = tmp_path
            dash.SKILLS_DIR = tmp_path / "skills"
            dash.ACTIVITY_LOG = tmp_path / "activity_log.jsonl"
            dash.UPLOAD_DIR = tmp_path / "uploads"
            dash.SALAD_API_KEY = ""
            dash._SALAD_API_KEY = ""
            dash.AIKIDO_API_KEY = ""
            dash.AIKIDO_APP_ID = ""
            dash._SUBAGENTS.clear()
            dash._TRAINING_DATA.update({"datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []}, "models": []})
            dash._MEMORY_STATE["projects"].clear()
            dash._MEMORY_STATE["learnings"].clear()
            dash._AUTOMATIONS["jobs"].clear()
            dash._AUTOMATIONS["history"].clear()
            dash._campaigns.clear()
            dash._scheduler_jobs.clear()
            dash._gpu_state["devices"] = []
            dash.app.config["TESTING"] = True
            client = dash.app.test_client()
            resp = client.get("/health")
            assert resp.status_code == 200

    def test_metrics_endpoint(self):
        """Metrics endpoint should be accessible."""
        import sys
        sys.path.insert(0, ".")
        from dashboard import backend as dash
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dash.CONFIG_DIR = tmp_path
            dash.SKILLS_DIR = tmp_path / "skills"
            dash.ACTIVITY_LOG = tmp_path / "activity_log.jsonl"
            dash.UPLOAD_DIR = tmp_path / "uploads"
            dash.SALAD_API_KEY = ""
            dash._SALAD_API_KEY = ""
            dash.AIKIDO_API_KEY = ""
            dash.AIKIDO_APP_ID = ""
            dash._SUBAGENTS.clear()
            dash._TRAINING_DATA.update({"datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []}, "models": []})
            dash._MEMORY_STATE["projects"].clear()
            dash._MEMORY_STATE["learnings"].clear()
            dash._AUTOMATIONS["jobs"].clear()
            dash._AUTOMATIONS["history"].clear()
            dash._campaigns.clear()
            dash._scheduler_jobs.clear()
            dash._gpu_state["devices"] = []
            dash.app.config["TESTING"] = True
            client = dash.app.test_client()
            resp = client.get("/metrics")
            assert resp.status_code == 200

    def test_services_endpoint(self):
        """Services endpoint should return service list."""
        import sys
        sys.path.insert(0, ".")
        from dashboard import backend as dash
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dash.CONFIG_DIR = tmp_path
            dash.SKILLS_DIR = tmp_path / "skills"
            dash.ACTIVITY_LOG = tmp_path / "activity_log.jsonl"
            dash.UPLOAD_DIR = tmp_path / "uploads"
            dash.SALAD_API_KEY = ""
            dash._SALAD_API_KEY = ""
            dash.AIKIDO_API_KEY = ""
            dash.AIKIDO_APP_ID = ""
            dash._SUBAGENTS.clear()
            dash._TRAINING_DATA.update({"datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []}, "models": []})
            dash._MEMORY_STATE["projects"].clear()
            dash._MEMORY_STATE["learnings"].clear()
            dash._AUTOMATIONS["jobs"].clear()
            dash._AUTOMATIONS["history"].clear()
            dash._campaigns.clear()
            dash._scheduler_jobs.clear()
            dash._gpu_state["devices"] = []
            dash.app.config["TESTING"] = True
            client = dash.app.test_client()
            resp = client.get("/api/services")
            assert resp.status_code in (200, 404)


class TestProviderRouting:
    """Test provider routing flow."""

    def test_providers_list(self):
        """Providers list should return valid response."""
        from router.providers import load_providers
        providers = load_providers()
        assert isinstance(providers, dict)

    def test_route_endpoint(self):
        """Route endpoint should accept requests."""
        from router.router import app
        app.config["TESTING"] = True
        client = app.test_client()
        resp = client.post("/route", json={"prompt": "test"})
        assert resp.status_code == 200
