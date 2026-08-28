"""MCP Catalog API — REST endpoints for MCP server management.

Endpoints:
  GET  /api/catalog/mcps             - List all cataloged MCPs
  GET  /api/catalog/mcps/{id}        - Get MCP details
  POST /api/catalog/mcps/{id}/enable - Enable an MCP
  POST /api/catalog/mcps/{id}/disable - Disable an MCP
  POST /api/catalog/mcps/install     - Install an MCP from catalog
  GET  /api/catalog/mcps/installed   - List installed MCPs
  GET  /api/catalog/mcps/categories  - Get MCP categories
  POST /api/catalog/mcps/test/{id}   - Test MCP connectivity
"""
import json
import os
import subprocess
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
CATALOG_PATH = ROOT / "mcp" / "catalog.json"
INSTALLED_PATH = ROOT / "config" / "mcp_installed.json"
_MCP_LOCK = threading.Lock()


def _load_catalog() -> dict:
    if CATALOG_PATH.exists():
        try:
            return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"version": "2.0", "mcp_servers": [], "categories": [], "tool_counts": {}}


def _load_installed() -> dict:
    if INSTALLED_PATH.exists():
        try:
            return json.loads(INSTALLED_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"installed": {}, "enabled": [], "configured_at": 0}


def _save_installed(data: dict):
    INSTALLED_PATH.parent.mkdir(parents=True, exist_ok=True)
    INSTALLED_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def list_mcps(category: str = None) -> list:
    catalog = _load_catalog()
    mcps = catalog.get("mcp_servers", [])
    if category:
        mcps = [m for m in mcps if m.get("category") == category]
    installed = _load_installed()
    installed_ids = set(installed.get("enabled", []))
    for m in mcps:
        m["_installed"] = m["id"] in installed_ids
        m["_enabled"] = m.get("id", "") in installed.get("enabled", [])
    return mcps


def get_mcp(mcp_id: str) -> dict | None:
    for m in _load_catalog().get("mcp_servers", []):
        if m["id"] == mcp_id:
            installed = _load_installed()
            m["_installed"] = m["id"] in installed.get("enabled", [])
            m["_enabled"] = m["id"] in installed.get("enabled", [])
            return m
    return None


def enable_mcp(mcp_id: str) -> dict:
    with _MCP_LOCK:
        data = _load_installed()
        if mcp_id not in [m["id"] for m in _load_catalog().get("mcp_servers", [])]:
            raise HTTPException(status_code=404, detail=f"MCP {mcp_id} not in catalog")
        if mcp_id not in data["enabled"]:
            data["enabled"].append(mcp_id)
        data["configured_at"] = int(time.time())
        _save_installed(data)
        return {"status": "enabled", "id": mcp_id}


def disable_mcp(mcp_id: str) -> dict:
    with _MCP_LOCK:
        data = _load_installed()
        if mcp_id in data["enabled"]:
            data["enabled"].remove(mcp_id)
        data["configured_at"] = int(time.time())
        _save_installed(data)
        return {"status": "disabled", "id": mcp_id}


def install_mcp(mcp_id: str, config: dict = None) -> dict:
    mcp = get_mcp(mcp_id)
    if not mcp:
        raise HTTPException(status_code=404, detail=f"MCP {mcp_id} not found")

    with _MCP_LOCK:
        data = _load_installed()
        data["installed"][mcp_id] = {
            "config": config or {},
            "installed_at": int(time.time()),
        }
        if mcp_id not in data["enabled"]:
            data["enabled"].append(mcp_id)
        data["configured_at"] = int(time.time())
        _save_installed(data)
    return {"status": "installed", "id": mcp_id, "path": str(INSTALLED_PATH)}


def test_mcp(mcp_id: str) -> dict:
    mcp = get_mcp(mcp_id)
    if not mcp:
        raise HTTPException(status_code=404, detail=f"MCP {mcp_id} not found")

    result = {"id": mcp_id, "type": mcp.get("type"), "healthy": False, "error": None}
    try:
        if mcp.get("type") == "stdio":
            import shlex
            cmd = mcp.get("command", mcp_id)
            # Validate command is a simple executable name/path, not user-controlled shell input
            if not re.match(r'^[a-zA-Z0-9_\-./]+$', cmd):
                result["error"] = f"Invalid MCP command format: {cmd}"
                return result
            health_args = ["--health"] if "--health" not in mcp.get("args", []) else []
            all_args = health_args + (mcp.get("args", []) if "--health" not in health_args else [])
            try:
                safe_cmd = shlex.split(cmd + " " + " ".join(all_args))
            except ValueError:
                safe_cmd = [cmd] + all_args
            proc = subprocess.run(
                safe_cmd,
                capture_output=True, text=True, timeout=10
            )
            result["healthy"] = proc.returncode == 0
            if proc.stdout:
                result["output"] = proc.stdout[:500]
        elif mcp.get("type") == "http":
            import urllib.request
            url = mcp.get("url", "http://localhost:8080") + "/health"
            with urllib.request.urlopen(url, timeout=5) as r:
                result["healthy"] = r.status == 200
                result["output"] = r.read().decode()[:500]
    except Exception as exc:
        result["error"] = str(exc)
    return result


def get_categories() -> list:
    catalog = _load_catalog()
    return catalog.get("categories", [])


def get_stats() -> dict:
    catalog = _load_catalog()
    installed = _load_installed()
    mcps = catalog.get("mcp_servers", [])
    total_tools = sum(catalog.get("tool_counts", {}).values())
    enabled = len(installed.get("enabled", []))
    cats = {}
    for m in mcps:
        c = m.get("category", "uncategorized")
        cats[c] = cats.get(c, 0) + 1
    return {
        "total_mcps": len(mcps),
        "enabled": enabled,
        "total_tools": total_tools,
        "categories": cats,
        "last_configured": installed.get("configured_at", 0),
    }


# ── FastAPI app ────────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="MCP Catalog API", version="2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/catalog/mcps")
    def list_mcps_endpoint(category: str = None):
        return {"mcps": list_mcps(category), "total": len(list_mcps(category))}

    @app.get("/api/catalog/mcps/{mcp_id}")
    def get_mcp_endpoint(mcp_id: str):
        mcp = get_mcp(mcp_id)
        if not mcp:
            raise HTTPException(status_code=404, detail=f"MCP {mcp_id} not found")
        return mcp

    @app.post("/api/catalog/mcps/{mcp_id}/enable")
    def enable_mcp_endpoint(mcp_id: str):
        return enable_mcp(mcp_id)

    @app.post("/api/catalog/mcps/{mcp_id}/disable")
    def disable_mcp_endpoint(mcp_id: str):
        return disable_mcp(mcp_id)

    @app.post("/api/catalog/mcps/install")
    def install_mcp_endpoint(req: dict):
        mcp_id = req.get("id")
        if not mcp_id:
            raise HTTPException(status_code=400, detail="id required")
        return install_mcp(mcp_id, req.get("config"))

    @app.get("/api/catalog/mcps/installed")
    def list_installed():
        return _load_installed()

    @app.get("/api/catalog/mcps/categories")
    def categories_endpoint():
        return {"categories": get_categories()}

    @app.post("/api/catalog/mcps/test/{mcp_id}")
    def test_mcp_endpoint(mcp_id: str):
        return test_mcp(mcp_id)

    @app.get("/api/catalog/mcps/stats")
    def stats_endpoint():
        return get_stats()

    @app.get("/health")
    def health():
        return {"status": "ok", "mcps": len(_load_catalog().get("mcp_servers", []))}


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("MCP_CATALOG_PORT", "8190"))
        print(f"[mcp-catalog] Starting MCP Catalog API on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[mcp-catalog] FastAPI not available. Install fastapi+uvicorn.")
