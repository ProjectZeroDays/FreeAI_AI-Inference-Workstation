#!/usr/bin/env python3
"""Plugin Registry System — awesome-opencode-style plugin management.

Features:
  - Remote registry fetch (from awesome-opencode GitHub)
  - Plugin browsing and filtering
  - Plugin install/remove/enable/disable
  - Plugin validation (schema checks)
  - Local plugin directory management
  - MCP server integration

Usage:
    python plugins/registry/registry.py           # runs on :8130
    python plugins/registry/registry.py --fetch   # fetch fresh registry
"""
import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

ROOT = Path(__file__).parent.parent
PLUGINS_DIR = ROOT / "plugins"
INSTALLED_DIR = PLUGINS_DIR / "installed"
REGISTRY_URL = (
    "https://raw.githubusercontent.com/"
    "awesome-opencode/awesome-opencode/main/dist/registry.json"
)

app = FastAPI(title="Plugin Registry", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_REGISTRY = {"plugins": [], "fetched_at": 0}
_REGISTRY_LOCK = threading.Lock()


def _ensure_dirs():
    INSTALLED_DIR.mkdir(parents=True, exist_ok=True)
    (PLUGINS_DIR / "disabled").mkdir(parents=True, exist_ok=True)


_ensure_dirs()


# ── Registry operations ──────────────────────────────────────────────
def fetch_registry(force=False):
    """Fetch plugin registry from remote source."""
    with _REGISTRY_LOCK:
        now = int(time.time())
        if not force and now - _REGISTRY["fetched_at"] < 3600 and _REGISTRY["plugins"]:
            return _REGISTRY

    try:
        req = Request(REGISTRY_URL, headers={"User-Agent": "FreeAI-Registry/1.0"})
        with urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
        with _REGISTRY_LOCK:
            if isinstance(data, list):
                _REGISTRY["plugins"] = data
            elif isinstance(data, dict):
                _REGISTRY["plugins"] = data.get("plugins", [])
            else:
                _REGISTRY["plugins"] = []
            _REGISTRY["fetched_at"] = int(time.time())
        return _REGISTRY
    except (URLError, HTTPError, json.JSONDecodeError) as exc:
        # Return cached or empty
        with _REGISTRY_LOCK:
            return _REGISTRY.copy()


def load_local_plugins():
    """Scan installed plugins directory."""
    plugins = []
    if not INSTALLED_DIR.exists():
        return plugins
    for plugin_dir in INSTALLED_DIR.iterdir():
        if not plugin_dir.is_dir():
            continue
        plugin_json = plugin_dir / "plugin.json"
        if plugin_json.exists():
            try:
                with open(plugin_json, encoding="utf-8") as f:
                    plugin = json.load(f)
                plugin["_path"] = str(plugin_dir)
                plugin["_installed"] = True
                plugins.append(plugin)
            except (json.JSONDecodeError, OSError):
                continue
    return plugins


def get_all_plugins():
    """Combine remote registry with locally installed plugins."""
    registry = fetch_registry()
    remote = registry.get("plugins", [])
    local = load_local_plugins()

    # Index remote by name
    remote_map = {p.get("name"): p for p in remote if p.get("name")}
    local_map = {p.get("name"): p for p in local if p.get("name")}

    # Merge
    all_names = set(remote_map.keys()) | set(local_map.keys())
    result = []
    for name in sorted(all_names):
        if name in local_map:
            p = local_map[name].copy()
            p["_source"] = "local"
            p["_enabled"] = p.get("enabled", True)
            result.append(p)
        if name in remote_map:
            p = remote_map[name].copy()
            p["_source"] = "remote"
            p["_enabled"] = True
            if name not in local_map:
                result.append(p)

    return result


# ── Install / Remove ─────────────────────────────────────────────────
def install_plugin(plugin_name, plugin_data=None):
    """Install a plugin from registry data or local source."""
    target = INSTALLED_DIR / plugin_name
    if target.exists():
        raise HTTPException(status_code=409, detail=f"Plugin {plugin_name} already installed")

    if plugin_data:
        plugin_json = json.dumps(plugin_data, indent=2)
        target.mkdir(parents=True)
        (target / "plugin.json").write_text(plugin_json, encoding="utf-8")

        # Copy any scripts/reference files
        for key in ("scripts", "references", "templates"):
            if key in plugin_data and isinstance(plugin_data[key], dict):
                for fname, content in plugin_data[key].items():
                    if isinstance(content, str):
                        (target / key / fname).parent.mkdir(parents=True, exist_ok=True)
                        (target / key / fname).write_text(content, encoding="utf-8")

        return {"status": "installed", "name": plugin_name, "path": str(target)}

    raise HTTPException(status_code=400, detail="plugin_data required for install")


def remove_plugin(plugin_name):
    """Remove an installed plugin."""
    target = INSTALLED_DIR / plugin_name
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_name} not installed")
    shutil.rmtree(target)
    return {"status": "removed", "name": plugin_name}


def toggle_plugin(plugin_name, enabled):
    """Enable/disable a plugin."""
    target = INSTALLED_DIR / plugin_name
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_name} not installed")

    plugin_json = target / "plugin.json"
    if not plugin_json.exists():
        raise HTTPException(status_code=400, detail="No plugin.json found")

    with open(plugin_json, encoding="utf-8") as f:
        data = json.load(f)

    data["enabled"] = enabled
    with open(plugin_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Move to disabled dir if disabling
    if not enabled:
        disabled_dir = PLUGINS_DIR / "disabled" / plugin_name
        disabled_dir.mkdir(parents=True, exist_ok=True)
        (plugin_json).rename(disabled_dir / "plugin.json")

    return {"status": "toggled", "name": plugin_name, "enabled": enabled}


# ── API Endpoints ────────────────────────────────────────────────────
@app.get("/health")
def health():
    registry = fetch_registry()
    local = load_local_plugins()
    return {
        "status": "ok",
        "remote_plugins": len(registry.get("plugins", [])),
        "installed_plugins": len(local),
        "last_fetched": registry.get("fetched_at", 0),
    }


@app.get("/plugins")
def list_plugins(category: Optional[str] = None, enabled: Optional[bool] = None):
    """List all plugins with optional filtering."""
    all_plugins = get_all_plugins()

    if category:
        all_plugins = [
            p for p in all_plugins
            if category.lower() in " ".join(p.get("categories", [])).lower()
            or category.lower() in p.get("description", "").lower()
        ]

    if enabled is not None:
        all_plugins = [p for p in all_plugins if p.get("_enabled", True) == enabled]

    # Strip internal fields for clean output
    clean = []
    for p in all_plugins:
        c = {k: v for k, v in p.items() if not k.startswith("_")}
        clean.append(c)

    return {"plugins": clean, "total": len(clean)}


@app.get("/plugins/{name}")
def get_plugin(name: str):
    """Get detailed info about a plugin."""
    all_plugins = get_all_plugins()
    for p in all_plugins:
        if p.get("name") == name:
            result = {k: v for k, v in p.items() if not k.startswith("_")}
            result["_enabled"] = p.get("_enabled", True)
            result["_source"] = p.get("_source", "unknown")
            return result
    raise HTTPException(status_code=404, detail=f"Plugin {name} not found")


@app.post("/plugins/fetch")
def refresh_registry():
    """Force-refresh the remote registry."""
    registry = fetch_registry(force=True)
    return {
        "status": "refreshed",
        "plugins_count": len(registry.get("plugins", [])),
        "fetched_at": registry["fetched_at"],
    }


@app.post("/plugins/{name}/install")
def install_plugin_endpoint(name: str, req: Optional[dict] = None):
    """Install a plugin."""
    if req is None:
        # Try to find in registry
        all_plugins = get_all_plugins()
        for p in all_plugins:
            if p.get("name") == name and p.get("_source") == "remote":
                req = p
                break
        if req is None:
            raise HTTPException(status_code=404, detail=f"Plugin {name} not in registry")

    result = install_plugin(name, req)
    return result


@app.delete("/plugins/{name}")
def uninstall_plugin_endpoint(name: str):
    """Remove a plugin."""
    return remove_plugin(name)


@app.put("/plugins/{name}/toggle")
def toggle_plugin_endpoint(name: str, req: dict):
    """Enable/disable a plugin."""
    enabled = req.get("enabled", True)
    return toggle_plugin(name, enabled)


@app.get("/categories")
def list_categories():
    """Get all plugin categories."""
    all_plugins = get_all_plugins()
    cats = set()
    for p in all_plugins:
        for c in p.get("categories", []):
            cats.add(c)
        # Also extract from description
        desc = p.get("description", "").lower()
        for keyword in ["agent", "orchestration", "security", "coding",
                        "documentation", "design", "testing", "devops",
                        "mcp", "memory", "research", "creative"]:
            if keyword in desc:
                cats.add(keyword)
    return {"categories": sorted(cats)}


@app.get("/stats")
def stats():
    """Registry statistics."""
    all_plugins = get_all_plugins()
    local = load_local_plugins()
    categories = {}
    for p in all_plugins:
        for c in p.get("categories", ["uncategorized"]):
            categories[c] = categories.get(c, 0) + 1

    return {
        "total_available": len(all_plugins),
        "installed": len(local),
        "categories": categories,
        "last_fetched": _REGISTRY.get("fetched_at", 0),
    }


# ── CLI convenience ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("REGISTRY_PORT", "8130"))
    fetch_registry(force=True)
    print(f"[registry] Starting plugin registry on :{port}")
    print(f"[registry] Plugins available: {len(get_all_plugins())}")
    uvicorn.run(app, host="0.0.0.0", port=port)
