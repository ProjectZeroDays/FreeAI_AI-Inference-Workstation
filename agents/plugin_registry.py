#!/usr/bin/env python3
"""Plugin Registry + Skills Integration System.

Manages:
- Plugin registry (awesome-opencode style) with discovery and metadata
- Skill loading from directory structure (agent-toolkit style)
- Plugin installation/uninstallation
- Skill-to-agent mapping
- Runtime skill activation
"""
import json
import os
import re
import shutil
import hashlib
import time
import threading
from pathlib import Path
from typing import Optional


REGISTRY_PATH = Path(__file__).parent.parent / "registry" / "plugins.json"
SKILLS_DIR = Path(__file__).parent.parent / "skills"
REMOTE_REGISTRY_URL = (
    "https://raw.githubusercontent.com/awesome-opencode/"
    "awesome-opencode/main/dist/registry.json"
)

_lock = threading.Lock()


class PluginRegistry:
    """Manages plugin catalog and metadata."""

    def __init__(self, registry_path: Path = REGISTRY_PATH):
        self._path = registry_path
        self._plugins: dict = {}
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                self._plugins = json.loads(self._path.read_text())
            except (json.JSONDecodeError, IOError):
                self._plugins = {}

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._plugins, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def fetch_remote(self) -> dict:
        """Fetch the latest registry from the remote URL."""
        import urllib.request
        try:
            with urllib.request.urlopen(REMOTE_REGISTRY_URL, timeout=30) as r:
                data = json.loads(r.read())
            with _lock:
                self._plugins = data
            self._save()
            return data
        except Exception as exc:
            return {"error": str(exc), "plugins": self._plugins}

    def list_plugins(self, category: str = None, enabled: bool = None) -> list:
        with _lock:
            plugins = list(self._plugins.values())
        if category:
            plugins = [p for p in plugins if p.get("category") == category]
        if enabled is not None:
            plugins = [p for p in plugins if p.get("enabled", True) == enabled]
        return plugins

    def get_plugin(self, name: str) -> Optional[dict]:
        with _lock:
            return self._plugins.get(name)

    def install_plugin(self, name: str, source: str = None) -> dict:
        """Mark a plugin as installed locally."""
        plugin = self.get_plugin(name)
        if not plugin:
            return {"error": f"plugin '{name}' not found in registry"}
        plugin["installed"] = True
        plugin["installed_at"] = int(time.time())
        if source:
            plugin["source"] = source
        self._save()
        return {"status": "installed", "plugin": name}

    def uninstall_plugin(self, name: str) -> dict:
        plugin = self.get_plugin(name)
        if not plugin:
            return {"error": f"plugin '{name}' not found"}
        plugin.pop("installed", None)
        plugin.pop("installed_at", None)
        self._save()
        return {"status": "uninstalled", "plugin": name}

    def stats(self) -> dict:
        with _lock:
            plugins = list(self._plugins.values())
        installed = sum(1 for p in plugins if p.get("installed"))
        categories = set(p.get("category", "uncategorized") for p in plugins)
        return {
            "total": len(plugins),
            "installed": installed,
            "categories": list(categories),
        }


class SkillLoader:
    """Loads and manages skills from directory structure."""

    SKILL_FILE = "SKILL.md"

    def __init__(self, skills_dirs: list[Path] = None):
        self._dirs = skills_dirs or [
            Path(__file__).parent.parent / "skills",
            Path(os.environ.get("AGENT_TOOLKIT_SKILLS", "")),
        ]
        self._skills: dict[str, dict] = {}
        self._loaded = False

    def _parse_frontmatter(self, content: str) -> tuple[dict, str]:
        """Extract YAML frontmatter from a skill file."""
        fm_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
        match = fm_pattern.match(content)
        if not match:
            return {}, content
        fm_text = match.group(1)
        body = content[match.end():]
        # Simple YAML-like parsing (no full parser dependency)
        fm = {}
        for line in fm_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                fm[key] = val
        return fm, body

    def discover(self) -> dict:
        """Scan all skill directories and index skills."""
        skills = {}
        for sd in self._dirs:
            if not sd.exists():
                continue
            for skill_root in sd.iterdir():
                if not skill_root.is_dir():
                    continue
                skill_file = skill_root / self.SKILL_FILE
                if not skill_file.exists():
                    continue
                try:
                    content = skill_file.read_text(encoding="utf-8")
                    fm, body = self._parse_frontmatter(content)
                    name = fm.get("name", skill_root.name)
                    skills[name] = {
                        "name": name,
                        "path": str(skill_file),
                        "dir": str(skill_root),
                        "description": fm.get("description", "")[:500],
                        "triggers": [t.strip() for t in fm.get("triggers", "").split(",") if t.strip()],
                        "metadata": fm.get("metadata", {}),
                        "body_preview": body[:200],
                    }
                except Exception:
                    continue
        with _lock:
            self._skills = skills
        self._loaded = True
        return skills

    def get_skill(self, name: str) -> Optional[dict]:
        return self._skills.get(name)

    def match_skills(self, query: str, limit: int = 5) -> list[dict]:
        """Find skills matching a query by description and triggers."""
        self.discover()  # ensure loaded
        query_lower = query.lower()
        scored = []
        for name, info in self._skills.items():
            score = 0
            desc = info.get("description", "").lower()
            triggers = [t.lower().strip() for t in info.get("triggers", [])]
            if query_lower in desc:
                score += len(query_lower)
            for trigger in triggers:
                if trigger in query_lower:
                    score += 10
            if score > 0:
                scored.append((score, name, info))
        scored.sort(reverse=True)
        return [info for _, _, info in scored[:limit]]

    def list_skills(self, category: str = None) -> list[dict]:
        if not self._loaded:
            self.discover()
        skills = list(self._skills.values())
        if category:
            skills = [s for s in skills
                      if category.lower() in s.get("path", "").lower()]
        return skills

    def stats(self) -> dict:
        if not self._loaded:
            self.discover()
        dirs_found = [str(d) for d in self._dirs if d.exists()]
        return {
            "total": len(self._skills),
            "dirs_scanned": len(dirs_found),
            "dirs": dirs_found,
        }


# ------------------------------------------------------------------ singleton instances
_registry = None
_loader = None


def get_registry() -> PluginRegistry:
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry


def get_loader() -> SkillLoader:
    global _loader
    if _loader is None:
        _loader = SkillLoader()
    return _loader


# ------------------------------------------------------------------ CLI interface
if __name__ == "__main__":
    import sys
    registry = get_registry()
    loader = get_loader()

    if len(sys.argv) < 2:
        print("Usage: plugin_registry.py [list|discover|fetch|stats|search <q>]")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "list":
        cat = sys.argv[2] if len(sys.argv) > 2 else None
        plugins = registry.list_plugins(category=cat)
        for p in plugins[:20]:
            status = "✓" if p.get("installed") else " "
            print(f"  {status} {p.get('name', '?')} [{p.get('category', '?')}]")
    elif cmd == "discover":
        info = loader.discover()
        print(f"Discovered {len(info)} skills")
        for name in list(info.keys())[:10]:
            print(f"  - {name}")
    elif cmd == "fetch":
        result = registry.fetch_remote()
        print(json.dumps(result, indent=2))
    elif cmd == "stats":
        print(json.dumps({
            "registry": registry.stats(),
            "skills": loader.stats(),
        }, indent=2))
    elif cmd == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        matches = loader.match_skills(query)
        for m in matches[:5]:
            print(f"  {m['name']}: {m['description'][:80]}")
    else:
        print(f"Unknown command: {cmd}")
