"""Unified Catalog API — combines skills, plugins, MCPs, providers, and agents.

Endpoints:
  GET  /api/catalog                    - Unified catalog summary
  GET  /api/catalog/skills             - List all skills
  GET  /api/catalog/plugins            - List all plugins
  GET  /api/catalog/mcps               - List all MCPs
  GET  /api/catalog/providers          - List all providers
  GET  /api/catalog/agents             - List all agents
  GET  /api/catalog/themes             - List available themes
  POST /api/catalog/auto-install       - Auto-install missing catalog items
  GET  /api/catalog/stats              - Catalog statistics
  GET  /api/catalog/dropdowns          - Dropdown-ready data for dashboard
"""
import json
import os
import threading
import time
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
SKILLS_CATALOG = ROOT / "skills" / "catalog.json"
MCP_CATALOG = ROOT / "mcp" / "catalog.json"
PROVIDERS_PATH = CONFIG_DIR / "providers-merged.json"
AGENT_DEFS_PATH = ROOT / "agents" / "agent.json"
THEMES_PATH = CONFIG_DIR / "themes.json"
AUTO_INSTALL_LOG = CONFIG_DIR / "auto_install_log.jsonl"

_lock = threading.Lock()


def _load_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _load_list(path: Path) -> list:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return []


def get_skills() -> list:
    catalog = _load_json(SKILLS_CATALOG)
    return catalog.get("skills", [])


def get_plugins() -> list:
    """Load plugins from registry and local installations."""
    plugins = []
    # From registry
    reg_path = ROOT / "registry" / "plugins.json"
    if reg_path.exists():
        try:
            plugins.extend(_load_list(reg_path))
        except (json.JSONDecodeError, OSError):
            pass
    # From installed plugins
    installed = ROOT / "plugins" / "installed"
    if installed.exists():
        for d in installed.iterdir():
            pj = d / "plugin.json"
            if pj.exists():
                try:
                    plugins.append({**json.loads(pj.read_text()), "_source": "local"})
                except (json.JSONDecodeError, OSError):
                    pass
    return plugins


def get_mcps() -> list:
    catalog = _load_json(MCP_CATALOG)
    return catalog.get("mcp_servers", [])


def get_providers() -> list:
    data = _load_json(PROVIDERS_PATH)
    if isinstance(data, list):
        return data
    providers = data.get("providers", data) if isinstance(data, dict) else {}
    return [{"id": k, **v} for k, v in providers.items()]


def get_agents() -> list:
    data = _load_json(AGENT_DEFS_PATH)
    if isinstance(data, list):
        return data
    agents = data.get("agents", data) if isinstance(data, dict) else []
    return agents if isinstance(agents, list) else []


def get_themes() -> list:
    data = _load_json(THEMES_PATH)
    if isinstance(data, list):
        return data
    themes = data.get("themes", data) if isinstance(data, dict) else []
    return themes if isinstance(themes, list) else []


def auto_install(missing_only: bool = True) -> dict:
    """Auto-install skills, plugins, or MCPs missing from local config."""
    log = []
    now = int(time.time())

    # Auto-install MCPs that are cataloged but not enabled
    mcp_catalog = _load_json(MCP_CATALOG)
    mcp_installed_path = CONFIG_DIR / "mcp_installed.json"
    mcp_installed = _load_json(mcp_installed_path) if mcp_installed_path.exists() else {"enabled": []}
    enabled_mcps = set(mcp_installed.get("enabled", []))

    for mcp in mcp_catalog.get("mcp_servers", []):
        mid = mcp["id"]
        if mid not in enabled_mcps:
            if not missing_only or mid not in mcp_installed.get("installed", {}):
                if mid not in mcp_installed.get("installed", {}):
                    mcp_installed.setdefault("installed", {})[mid] = {
                        "config": {},
                        "installed_at": now,
                    }
                if mid not in mcp_installed.get("enabled", []):
                    mcp_installed["enabled"].append(mid)
                mcp_installed["configured_at"] = now
                log.append({"item": mid, "type": "mcp", "action": "installed"})

    # Auto-install skills from catalog that aren't local
    skills_catalog = _load_json(SKILLS_CATALOG)
    local_skills_dir = ROOT / "skills"
    for skill in skills_catalog.get("skills", []):
        if skill.get("local"):
            continue
        skill_id = skill.get("id", "")
        skill_dir = local_skills_dir / skill_id
        if not skill_dir.exists() and not missing_only:
            # Create placeholder
            skill_dir.mkdir(parents=True, exist_ok=True)
            log.append({"item": skill_id, "type": "skill", "action": "placeholder_created"})

    # Save updated MCP config
    if log:
        _save_json(mcp_installed_path, mcp_installed)
        with open(AUTO_INSTALL_LOG, "a", encoding="utf-8") as f:
            for entry in log:
                f.write(json.dumps({"ts": now, **entry}) + "\n")

    return {"installed": log, "total": len(log), "timestamp": now}


def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_stats() -> dict:
    skills = get_skills()
    plugins = get_plugins()
    mcps = get_mcps()
    providers = get_providers()
    agents = get_agents()
    themes = get_themes()

    return {
        "skills": len(skills),
        "plugins": len(plugins),
        "mcps": len(mcps),
        "providers": len(providers),
        "agents": len(agents),
        "themes": len(themes),
        "total_items": len(skills) + len(plugins) + len(mcps) + len(providers) + len(agents),
    }


def get_dropdowns() -> dict:
    """Return dropdown-ready data for the dashboard."""
    skills = get_skills()
    mcps = get_mcps()
    providers = get_providers()
    agents = get_agents()
    themes = get_themes()

    return {
        "skills": [
            {"value": s.get("id", s.get("name", "")), "label": s.get("name", ""), "category": s.get("category", "general")}
            for s in skills
        ],
        "mcps": [
            {"value": m["id"], "label": m["name"], "category": m.get("category", "uncategorized")}
            for m in mcps
        ],
        "providers": [
            {"value": p.get("id", k), "label": p.get("description", p.get("id", k))}
            for k, p in {**{i.get("id", i): i for i in providers}}.items()
        ],
        "agents": [
            {"value": a.get("id", a.get("name", "")), "label": a.get("name", a.get("id", "")), "role": a.get("role", "")}
            for a in agents
        ],
        "themes": [
            {"value": t.get("id", t.get("name", "")), "label": t.get("name", t.get("id", "")), "dark": t.get("dark", False)}
            for t in themes
        ],
    }


# ── FastAPI app ────────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="Unified Catalog API", version="2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/catalog")
    def catalog_summary():
        return {
            "summary": get_stats(),
            "timestamp": int(time.time()),
        }

    @app.get("/api/catalog/skills")
    def list_skills():
        return {"skills": get_skills(), "total": len(get_skills())}

    @app.get("/api/catalog/plugins")
    def list_plugins():
        return {"plugins": get_plugins(), "total": len(get_plugins())}

    @app.get("/api/catalog/mcps")
    def list_mcps():
        return {"mcps": get_mcps(), "total": len(get_mcps())}

    @app.get("/api/catalog/providers")
    def list_providers():
        return {"providers": get_providers(), "total": len(get_providers())}

    @app.get("/api/catalog/agents")
    def list_agents():
        return {"agents": get_agents(), "total": len(get_agents())}

    @app.get("/api/catalog/themes")
    def list_themes():
        return {"themes": get_themes(), "total": len(get_themes())}

    @app.post("/api/catalog/auto-install")
    def auto_install_endpoint(req: dict = None):
        missing_only = (req or {}).get("missing_only", True)
        return auto_install(missing_only=missing_only)

    @app.get("/api/catalog/stats")
    def stats_endpoint():
        return get_stats()

    @app.get("/api/catalog/dropdowns")
    def dropdowns_endpoint():
        return get_dropdowns()

    @app.get("/health")
    def health():
        return {"status": "ok", "items": get_stats()}


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("CATALOG_PORT", "8195"))
        print(f"[catalog] Starting Unified Catalog API on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[catalog] FastAPI not available. Install fastapi+uvicorn.")
