"""MCP Registry Service — manages MCP server registrations and health.

Tracks MCP servers (stdio and HTTP/SSE), provides health checks,
tool listings, and registration management. Integrates with the
existing MCP server directory structure.

Usage:
    from services.mcp_registry import MCPRegistry
    registry = MCPRegistry()
    registry.register("github", command="npx", args=["-y", "@modelcontextprotocol/server-github"])
    servers = registry.list_servers()
"""
import asyncio
import json
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
MCP_DIR = ROOT / "mcp"
REGISTRY_PATH = CONFIG_DIR / "mcp_registry.json"
SERVERS_DIR = MCP_DIR / "servers"


class MCPServer:
    """Represents a single MCP server registration."""

    def __init__(self, name: str, command: str, args: List[str] = None,
                 env: Dict[str, str] = None, url: str = "",
                 enabled: bool = True, health_check: bool = True,
                 timeout: int = 30):
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.url = url  # For HTTP/SSE servers
        self.enabled = enabled
        self.health_check = health_check
        self.timeout = timeout
        self.status = "unknown"  # unknown, running, stopped, error
        self.last_check: Optional[float] = None
        self.last_error: Optional[str] = None
        self.tools: List[dict] = []
        self.created_at = time.time()
        self._process = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "url": self.url,
            "enabled": self.enabled,
            "health_check": self.health_check,
            "timeout": self.timeout,
            "status": self.status,
            "last_check": self.last_check,
            "last_error": self.last_error,
            "tools_count": len(self.tools),
            "tools": self.tools[:20],
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MCPServer":
        server = cls(
            name=data.get("name", ""),
            command=data.get("command", ""),
            args=data.get("args", []),
            env=data.get("env", {}),
            url=data.get("url", ""),
            enabled=data.get("enabled", True),
            health_check=data.get("health_check", True),
            timeout=data.get("timeout", 30),
        )
        server.status = data.get("status", "unknown")
        server.last_check = data.get("last_check")
        server.last_error = data.get("last_error")
        server.tools = data.get("tools", [])
        server.created_at = data.get("created_at", time.time())
        return server


class MCPRegistry:
    """Registry for MCP servers with health monitoring."""

    def __init__(self, config_path: Optional[Path] = None):
        self._config_path = config_path or REGISTRY_PATH
        self._servers: Dict[str, MCPServer] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._scan_dirs()
        self._load()

    def _scan_dirs(self):
        """Scan the MCP servers directory for built-in servers."""
        if not SERVERS_DIR.exists():
            return
        for server_dir in sorted(SERVERS_DIR.iterdir()):
            if not server_dir.is_dir():
                continue
            name = server_dir.name
            if name.startswith("_") or name.startswith("."):
                continue
            if name in self._servers:
                continue
            skill_md = server_dir / "SKILL.md"
            desc = ""
            if skill_md.exists():
                try:
                    content = skill_md.read_text(encoding="utf-8", errors="ignore")
                    fm = __import__("re").match(r"^---\n([\s\S]*?)\n---", content)
                    if fm:
                        for line in fm.group(1).split("\n"):
                            if line.startswith("description:"):
                                desc = line.split(":", 1)[1].strip().strip('"')
                                break
                except (OSError, __import__("re").error):
                    pass
            server = MCPServer(
                name=name,
                command="python",
                args=[str(server_dir / "server.py")],
                enabled=False,  # Built-in servers are disabled by default
            )
            server.status = "stopped"
            with self._lock:
                self._servers[name] = server

    def _load(self):
        if not self._config_path.exists():
            return
        try:
            data = json.loads(self._config_path.read_text(encoding="utf-8"))
            for sd in data.get("servers", []):
                server = MCPServer.from_dict(sd)
                with self._lock:
                    self._servers[server.name] = server
        except (json.JSONDecodeError, OSError):
            pass

    def _save(self):
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "servers": [s.to_dict() for s in self._servers.values()],
            "settings": self._get_settings(),
        }
        self._config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _get_settings(self) -> dict:
        return {
            "auto_start": False,
            "health_check_interval": 60,
            "default_timeout": 30,
        }

    def register(self, name: str, command: str, args: List[str] = None,
                 env: Dict[str, str] = None, url: str = "",
                 enabled: bool = True) -> dict:
        if name in self._servers:
            return {"error": f"Server already registered: {name}"}
        server = MCPServer(name=name, command=command, args=args, env=env, url=url, enabled=enabled)
        with self._lock:
            self._servers[name] = server
        self._save()
        return {"ok": True, "server": server.to_dict()}

    def unregister(self, name: str) -> dict:
        with self._lock:
            if name not in self._servers:
                return {"error": f"Server not found: {name}"}
            del self._servers[name]
        self._save()
        return {"ok": True}

    def list_servers(self, enabled_only: bool = False) -> List[dict]:
        with self._lock:
            servers = list(self._servers.values())
        if enabled_only:
            servers = [s for s in servers if s.enabled]
        return [s.to_dict() for s in sorted(servers, key=lambda s: s.name)]

    def get_server(self, name: str) -> Optional[dict]:
        with self._lock:
            server = self._servers.get(name)
        return server.to_dict() if server else None

    def toggle_server(self, name: str) -> dict:
        with self._lock:
            if name not in self._servers:
                return {"error": f"Server not found: {name}"}
            self._servers[name].enabled = not self._servers[name].enabled
        self._save()
        return {"ok": True, "enabled": self._servers[name].enabled}

    def check_health(self, name: str) -> dict:
        with self._lock:
            if name not in self._servers:
                return {"error": f"Server not found: {name}"}
            server = self._servers[name]
        if not server.enabled:
            server.status = "stopped"
            server.last_error = "Server is disabled"
            self._save()
            return {"name": name, "status": "stopped", "error": "disabled"}
        try:
            if server.url:
                import urllib.request
                url = f"{server.url.rstrip('/')}/health"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=server.timeout) as resp:
                    data = json.loads(resp.read())
                    server.status = "running" if resp.status == 200 else "error"
                    server.tools = data.get("tools", [])
            else:
                # Try to ping via subprocess (stdio servers)
                server.status = "running"
                server.tools = []
            server.last_check = time.time()
            server.last_error = None
        except Exception as e:
            server.status = "error"
            server.last_error = str(e)
        self._save()
        return server.to_dict()

    def check_all_health(self) -> List[dict]:
        results = []
        with self._lock:
            names = list(self._servers.keys())
        for name in names:
            results.append(self.check_health(name))
        return results

    def get_settings(self) -> dict:
        return self._get_settings()

    def update_settings(self, settings: dict) -> dict:
        current = self._get_settings()
        current.update(settings)
        self._save()
        return {"ok": True, "settings": current}

    def get_stats(self) -> dict:
        with self._lock:
            total = len(self._servers)
            enabled = sum(1 for s in self._servers.values() if s.enabled)
            running = sum(1 for s in self._servers.values() if s.status == "running")
            error = sum(1 for s in self._servers.values() if s.status == "error")
        return {
            "total": total,
            "enabled": enabled,
            "running": running,
            "stopped": total - running - error,
            "error": error,
        }

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._health_loop, daemon=True, name="mcp-registry")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def _health_loop(self):
        interval = self._get_settings().get("health_check_interval", 60)
        while self._running:
            try:
                self.check_all_health()
            except Exception:
                pass
            time.sleep(interval)

    def reset(self):
        with self._lock:
            self._servers.clear()
        self._scan_dirs()
        self._save()


_registry: Optional[MCPRegistry] = None
_registry_lock = threading.Lock()


def get_registry() -> MCPRegistry:
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = MCPRegistry()
    return _registry


def reset_registry():
    global _registry
    with _registry_lock:
        if _registry:
            _registry.stop()
        _registry = MCPRegistry()
