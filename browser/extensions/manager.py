"""Knight-Shade Browser Extension Manager.

Handles loading, injecting, and managing Manifest-X browser extensions.
Supports content scripts, background scripts, permissions, and per-domain
enabling/disabling.
"""
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional

BROWSER_DIR = Path(__file__).parent
EXTENSIONS_DIR = BROWSER_DIR / "extensions"
SAMPLES_DIR = EXTENSIONS_DIR / "samples"
CONFIG_PATH = BROWSER_DIR.parent / "config" / "extensions.json"


class Extension:
    """Represents a single Manifest-X browser extension."""

    def __init__(self, name: str, manifest: dict, source_dir: Optional[Path] = None):
        self.name = name
        self.manifest = manifest
        self.source_dir = source_dir or (SAMPLES_DIR / name)
        self.enabled = manifest.get("enabled", True)
        self.enabled_domains: list[str] = manifest.get("enabled_domains", [])
        self.disabled_domains: list[str] = manifest.get("disabled_domains", [])
        self.installed_at = manifest.get("installed_at", time.time())
        self._content_scripts = manifest.get("content_scripts", [])
        self._background_scripts = manifest.get("background", {}).get("scripts", [])

    @property
    def version(self) -> str:
        return self.manifest.get("version", "1.0.0")

    @property
    def description(self) -> str:
        return self.manifest.get("description", "")

    @property
    def permissions(self) -> list[str]:
        return self.manifest.get("permissions", [])

    @property
    def icon_url(self) -> Optional[str]:
        return self.manifest.get("icons", {}).get("48", "")

    def is_domain_allowed(self, domain: str) -> bool:
        if not self.enabled:
            return False
        if domain in self.disabled_domains:
            return False
        if self.enabled_domains and domain not in self.enabled_domains:
            return False
        return True

    def generate_crx_manifest(self) -> dict:
        manifest = {
            "manifest_version": 4,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "permissions": self.permissions,
            "host_permissions": ["*://*/*"],
            "manifest_x": {
                "god_mode": True,
                "bypass_csp": True,
                "access_cdp": True,
                "access_browser_apis": True,
                "telemetry_encrypted": True,
                "extension_id": hashlib.sha256(self.name.encode()).hexdigest()[:16],
            },
        }
        if self._background_scripts:
            manifest["background"] = {
                "service_worker": "bg.js",
                "scripts": self._background_scripts,
            }
        if self._content_scripts:
            manifest["content_scripts"] = self._content_scripts
        return manifest

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled,
            "enabled_domains": self.enabled_domains,
            "disabled_domains": self.disabled_domains,
            "permissions": self.permissions,
            "installed_at": self.installed_at,
            "source_dir": str(self.source_dir),
            "content_scripts_count": len(self._content_scripts),
            "crx_manifest": self.generate_crx_manifest(),
        }


class ExtensionManager:
    """Manages loading, injecting, and lifecycle of browser extensions."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self._extensions: dict[str, Extension] = {}
        self._domain_overrides: dict[str, dict[str, bool]] = {}
        self._log: list[dict] = []

    def _log_event(self, event: str, name: str, detail: str = ""):
        self._log.append({
            "ts": time.time(),
            "event": event,
            "extension": name,
            "detail": detail,
        })
        if len(self._log) > 500:
            self._log = self._log[-250:]

    def load_from_config(self, config_path: Optional[Path] = None) -> list[str]:
        path = config_path or CONFIG_PATH
        if not path.exists():
            return self.load_builtin_samples()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            extensions = data.get("extensions", [])
            self._domain_overrides = data.get("domain_overrides", {})
            for ext_cfg in extensions:
                name = ext_cfg.get("name", "")
                if name:
                    self._extensions[name] = Extension(name, ext_cfg)
                    self._log_event("loaded", name, f"from {path}")
            return list(self._extensions.keys())
        except (json.JSONDecodeError, OSError) as exc:
            self._log_event("load_error", "", str(exc))
            return []

    def load_builtin_samples(self) -> list[str]:
        loaded = []
        if not SAMPLES_DIR.exists():
            return loaded
        for sample_dir in sorted(SAMPLES_DIR.iterdir()):
            if not sample_dir.is_dir():
                continue
            manifest_path = sample_dir / "manifest.json"
            if not manifest_path.exists():
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                name = manifest.get("name", sample_dir.stem)
                manifest["source_dir"] = str(sample_dir)
                manifest["builtin"] = True
                self._extensions[name] = Extension(name, manifest, sample_dir)
                loaded.append(name)
                self._log_event("loaded", name, "builtin sample")
            except (json.JSONDecodeError, OSError):
                continue
        return loaded

    def install_from_manifest(self, manifest: dict) -> dict:
        name = manifest.get("name", "")
        if not name:
            return {"error": "Extension manifest missing 'name' field"}
        manifest["installed_at"] = time.time()
        manifest["builtin"] = False
        self._extensions[name] = Extension(name, manifest)
        self._log_event("installed", name)
        return {"ok": True, "name": name, "manifest": self._extensions[name].to_dict()}

    def uninstall(self, name: str) -> dict:
        if name not in self._extensions:
            return {"error": f"Extension not found: {name}"}
        ext = self._extensions.pop(name)
        self._log_event("uninstalled", name)
        return {"ok": True, "name": name}

    def get(self, name: str) -> Optional[Extension]:
        return self._extensions.get(name)

    def list_all(self) -> list[dict]:
        return [ext.to_dict() for ext in self._extensions.values()]

    def toggle(self, name: str, enabled: bool) -> dict:
        ext = self._extensions.get(name)
        if not ext:
            return {"error": f"Extension not found: {name}"}
        ext.enabled = enabled
        self._log_event("toggled", name, f"enabled={enabled}")
        return {"ok": True, "name": name, "enabled": enabled}

    def set_domain_override(self, name: str, domain: str, enabled: bool) -> dict:
        ext = self._extensions.get(name)
        if not ext:
            return {"error": f"Extension not found: {name}"}
        if name not in self._domain_overrides:
            self._domain_overrides[name] = {}
        self._domain_overrides[name][domain] = enabled
        self._log_event("domain_override", name, f"{domain}={enabled}")
        return {"ok": True, "name": name, "domain": domain, "enabled": enabled}

    def is_domain_enabled(self, name: str, domain: str) -> bool:
        ext = self._extensions.get(name)
        if not ext:
            return False
        overrides = self._domain_overrides.get(name, {})
        if domain in overrides:
            return overrides[domain]
        return ext.is_domain_allowed(domain)

    async def inject_into_page(self, page) -> list[str]:
        injected = []
        for ext in self._extensions.values():
            if not ext.enabled:
                continue
            script = self._build_injection_script(ext)
            if script:
                try:
                    await page.add_init_script(script)
                    injected.append(ext.name)
                except Exception:
                    pass
        return injected

    async def inject_on_navigation(self, page) -> list[str]:
        injected = []
        current_url = await page.url if page else ""
        for ext in self._extensions.values():
            if not ext.enabled:
                continue
            domain = self._extract_domain(current_url)
            if not ext.is_domain_allowed(domain):
                continue
            overrides = self._domain_overrides.get(ext.name, {})
            if overrides and domain in overrides and not overrides[domain]:
                continue
            script = self._build_injection_script(ext)
            if script:
                try:
                    await page.add_init_script(script)
                    injected.append(ext.name)
                except Exception:
                    pass
        return injected

    def _build_injection_script(self, ext: Extension) -> Optional[str]:
        parts = []
        for cs in ext._content_scripts:
            js_files = cs.get("js", [])
            for js_file in js_files:
                js_path = ext.source_dir / js_file
                if js_path.exists():
                    try:
                        code = js_path.read_text(encoding="utf-8")
                        wrapped = f"// ==Extension== {ext.name} ==Version== {ext.version}\n{code}"
                        parts.append(wrapped)
                    except OSError:
                        pass
        bg_code = self._load_background_code(ext)
        if bg_code:
            parts.append(bg_code)
        if not parts:
            return None
        return "\n".join(parts)

    def _load_background_code(self, ext: Extension) -> str:
        bg = ext.manifest.get("background", {})
        scripts = bg.get("scripts", [])
        if not scripts:
            return ""
        parts = []
        for s in scripts:
            p = ext.source_dir / s
            if p.exists():
                try:
                    parts.append(p.read_text(encoding="utf-8"))
                except OSError:
                    pass
        return f"// ==Background== {ext.name}\n" + "\n".join(parts)

    def _extract_domain(self, url: str) -> str:
        try:
            without_schema = url.split("://", 1)[-1]
            domain = without_schema.split("/")[0].split(":")[0]
            return domain
        except Exception:
            return ""

    def get_injection_log(self, limit: int = 50) -> list[dict]:
        return self._log[-limit:]

    def describe(self) -> dict:
        return {
            "total": len(self._extensions),
            "enabled": sum(1 for e in self._extensions.values() if e.enabled),
            "extensions": self.list_all(),
            "log": self._log[-20:],
        }


def get_manager(config: Optional[dict] = None) -> ExtensionManager:
    mgr = ExtensionManager(config)
    mgr.load_from_config()
    return mgr
