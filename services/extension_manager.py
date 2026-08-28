"""Extension Manager — manages browser extensions with lifecycle control.

Wraps the browser extensions manager and provides REST API endpoints
for listing, installing, enabling/disabling, and managing browser
extensions. Integrates with the Knight-Shade browser engine.

Usage:
    from services.extension_manager import ExtensionManagerService
    mgr = ExtensionManagerService()
    mgr.install_extension({"name": "my-ext", ...})
"""
import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
EXTENSIONS_STATE_PATH = CONFIG_DIR / "extensions_state.json"


class ExtensionState:
    """Tracks the state of a browser extension."""

    def __init__(self, name: str, manifest: dict, source: str = "user"):
        self.name = name
        self.manifest = manifest
        self.source = source  # "builtin", "user", "remote"
        self.enabled = manifest.get("enabled", True)
        self.install_time = time.time()
        self.last_active = time.time()
        self.injection_count = 0
        self.errors: List[str] = []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "manifest": self.manifest,
            "source": self.source,
            "enabled": self.enabled,
            "install_time": self.install_time,
            "last_active": self.last_active,
            "injection_count": self.injection_count,
            "errors": self.errors[-5:],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExtensionState":
        ext = cls(
            name=data.get("name", ""),
            manifest=data.get("manifest", {}),
            source=data.get("source", "user"),
        )
        ext.enabled = data.get("enabled", True)
        ext.install_time = data.get("install_time", time.time())
        ext.last_active = data.get("last_active", time.time())
        ext.injection_count = data.get("injection_count", 0)
        ext.errors = data.get("errors", [])
        return ext


class ExtensionManagerService:
    """Manages browser extensions with persistence and dashboard support."""

    def __init__(self, config_path: Optional[Path] = None):
        self._config_path = config_path or EXTENSIONS_STATE_PATH
        self._extensions: Dict[str, ExtensionState] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        if not self._config_path.exists():
            return
        try:
            data = json.loads(self._config_path.read_text(encoding="utf-8"))
            for ed in data.get("extensions", []):
                ext = ExtensionState.from_dict(ed)
                self._extensions[ext.name] = ext
        except (json.JSONDecodeError, OSError):
            pass

    def _save(self):
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "extensions": [e.to_dict() for e in self._extensions.values()],
            "settings": self._get_settings(),
        }
        self._config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _get_settings(self) -> dict:
        return {
            "auto_inject": True,
            "inject_on_navigation": True,
            "max_extensions": 50,
            "allow_remote": False,
        }

    def install(self, manifest: dict, source: str = "user") -> dict:
        name = manifest.get("name", "")
        if not name:
            return {"error": "Extension manifest missing 'name' field"}
        if len(self._extensions) >= self._get_settings().get("max_extensions", 50):
            return {"error": "Maximum extension limit reached"}
        ext = ExtensionState(name=name, manifest=manifest, source=source)
        with self._lock:
            self._extensions[name] = ext
        self._save()
        return {"ok": True, "extension": ext.to_dict()}

    def uninstall(self, name: str) -> dict:
        with self._lock:
            if name not in self._extensions:
                return {"error": f"Extension not found: {name}"}
            del self._extensions[name]
        self._save()
        return {"ok": True, "name": name}

    def list_extensions(self, enabled_only: bool = False) -> List[dict]:
        with self._lock:
            exts = list(self._extensions.values())
        if enabled_only:
            exts = [e for e in exts if e.enabled]
        return [e.to_dict() for e in sorted(exts, key=lambda e: e.name)]

    def get_extension(self, name: str) -> Optional[dict]:
        with self._lock:
            ext = self._extensions.get(name)
        return ext.to_dict() if ext else None

    def toggle_extension(self, name: str, enabled: bool) -> dict:
        with self._lock:
            if name not in self._extensions:
                return {"error": f"Extension not found: {name}"}
            self._extensions[name].enabled = enabled
            self._extensions[name].last_active = time.time()
        self._save()
        return {"ok": True, "name": name, "enabled": enabled}

    def get_settings(self) -> dict:
        return self._get_settings()

    def update_settings(self, settings: dict) -> dict:
        current = self._get_settings()
        current.update(settings)
        self._save()
        return {"ok": True, "settings": current}

    def get_stats(self) -> dict:
        with self._lock:
            total = len(self._extensions)
            enabled = sum(1 for e in self._extensions.values() if e.enabled)
            by_source = {}
            for e in self._extensions.values():
                by_source[e.source] = by_source.get(e.source, 0) + 1
        return {
            "total": total,
            "enabled": enabled,
            "disabled": total - enabled,
            "by_source": by_source,
            "settings": self._get_settings(),
        }

    def inject_for_page(self, name: str, page_url: str) -> dict:
        with self._lock:
            ext = self._extensions.get(name)
            if not ext:
                return {"error": f"Extension not found: {name}"}
            if not ext.enabled:
                return {"error": f"Extension disabled: {name}"}
            ext.last_active = time.time()
            ext.injection_count += 1
        self._save()
        return {"ok": True, "name": name, "url": page_url, "count": ext.injection_count}

    def reset(self):
        with self._lock:
            self._extensions.clear()
        self._save()


_service: Optional[ExtensionManagerService] = None
_service_lock = threading.Lock()


def get_service() -> ExtensionManagerService:
    global _service
    if _service is None:
        with _service_lock:
            if _service is None:
                _service = ExtensionManagerService()
    return _service


def reset_service():
    global _service
    with _service_lock:
        _service = ExtensionManagerService()
