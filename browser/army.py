"""Omni-Agent-Army — Hierarchical multi-agent orchestration.

Ranks: E-1 (Grunt) through O-7 (General) — 14 ranks
Divisions: Recon, Operations, Engineering, Security, SpecialOps, Command
Each agent has isolated browser session, anonymity config, telemetry stream.
Scales to 1000+ concurrent agents.
"""
import asyncio
import json
import os
import random
import threading
import time
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Optional

ROOT = Path(__file__).parent.parent
ARMY_CONFIG_PATH = ROOT / "config" / "army.json"


# ── Ranks & Divisions ─────────────────────────────────────────────
RANKS = {
    "E-1": {"title": "Grunt", "max_agents": 50, "tier": 1},
    "E-2": {"title": "Private", "max_agents": 50, "tier": 1},
    "E-3": {"title": "Specialist", "max_agents": 50, "tier": 2},
    "E-4": {"title": "Corporal", "max_agents": 40, "tier": 2},
    "E-5": {"title": "Sergeant", "max_agents": 30, "tier": 3},
    "E-6": {"title": "Staff Sergeant", "max_agents": 20, "tier": 3},
    "E-7": {"title": "Sergeant First Class", "max_agents": 15, "tier": 4},
    "O-1": {"title": "Second Lieutenant", "max_agents": 10, "tier": 4},
    "O-2": {"title": "First Lieutenant", "max_agents": 8, "tier": 4},
    "O-3": {"title": "Captain", "max_agents": 5, "tier": 5},
    "O-4": {"title": "Major", "max_agents": 3, "tier": 5},
    "O-5": {"title": "Lieutenant Colonel", "max_agents": 2, "tier": 5},
    "O-6": {"title": "Colonel", "max_agents": 1, "tier": 6},
    "O-7": {"title": "Brigadier General", "max_agents": 1, "tier": 6},
}

DIVISIONS = {
    "recon": {"description": "Web reconnaissance & scraping", "extensions": ["scrapling", "proxycrawl"]},
    "operations": {"description": "Browser automation & interaction", "extensions": ["manifest-x", "cdp-full"]},
    "engineering": {"description": "Code analysis & binary reverse engineering", "extensions": ["ghidra", "frida"]},
    "security": {"description": "Penetration testing & vulnerability scanning", "extensions": ["burp", "zaproxy", "mitmproxy"]},
    "specialops": {"description": "Stealth operations & cloaked browsing", "extensions": ["cloakbrowser", "manifest-x-god"]},
    "command": {"description": "Orchestration & fleet coordination", "extensions": ["swarm-coord", "health-monitor"]},
}

# Map divisions to browser engine config overrides
DIVISION_ENGINE_CONFIG = {
    "recon": {"stealth": {"enable": True}, "anonymity": {"mode": "none"}},
    "operations": {"stealth": {"enable": True}, "manifestx": {"enabled": True}},
    "security": {"stealth": {"enable": True}, "anonymity": {"mode": "tor"}, "cdp": {"enabled": True}},
    "specialops": {"stealth": {"enable": True}, "anonymity": {"mode": "shadowsocks"}, "manifestx": {"enabled": True, "god_mode": True}},
    "engineering": {"stealth": {"enable": False}},
    "command": {"stealth": {"enable": True}},
}


class ArmyAgent:
    """Individual army operator with isolated resources."""

    def __init__(self, agent_id, rank, division, config=None):
        self.agent_id = agent_id
        self.rank = rank
        self.division = division
        self.config = config or {}
        self.status = "standby"  # standby, active, busy, failed, retired
        self.session_id = None
        self.browser_engine = None
        self.anonymity_mode = config.get("anonymity_mode", "none")
        self.telemetry = []
        self.created_at = time.time()
        self.last_active = self.created_at
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.extensions = DIVISIONS.get(division, {}).get("extensions", [])

    def describe(self):
        return {
            "agent_id": self.agent_id,
            "rank": self.rank,
            "division": self.division,
            "status": self.status,
            "session_id": self.session_id,
            "extensions": self.extensions,
            "anonymity_mode": self.anonymity_mode,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "created_at": self.created_at,
        }


class SwarmCoordinator:
    """Coordinates agent swarms with hierarchical/mesh/hybrid topologies."""

    TOPOLOGIES = ["hierarchical", "mesh", "hybrid"]

    def __init__(self, topology="hierarchical"):
        self.topology = topology
        self._agents = {}
        self._sessions = {}
        self._lock = threading.Lock()
        self._running = False
        self._engine_configs = {}  # agent_id -> BrowserEngine config

    def add_agent(self, agent: ArmyAgent):
        with self._lock:
            self._agents[agent.agent_id] = agent

    def remove_agent(self, agent_id):
        with self._lock:
            self._agents.pop(agent_id, None)
            self._sessions.pop(agent_id, None)
            self._engine_configs.pop(agent_id, None)

    def get_agent(self, agent_id):
        return self._agents.get(agent_id)

    def list_agents(self, rank=None, division=None, status=None):
        agents = list(self._agents.values())
        if rank:
            agents = [a for a in agents if a.rank == rank]
        if division:
            agents = [a for a in agents if a.division == division]
        if status:
            agents = [a for a in agents if a.status == status]
        return agents

    def get_roster(self):
        with self._lock:
            return {a.agent_id: a.describe() for a in self._agents.values()}

    def deploy_swarms(self, count, rank="E-1", division="operations", config=None):
        """Deploy N agents of given rank/division."""
        deployed = []
        with self._lock:
            for i in range(count):
                aid = f"agent_{uuid.uuid4().hex[:6]}"
                agent = ArmyAgent(aid, rank, division, config or {})
                self._agents[aid] = agent
                # Merge division-specific engine config
                base_cfg = DIVISION_ENGINE_CONFIG.get(division, {})
                merged = {**base_cfg, **(config or {})}
                self._engine_configs[aid] = merged
                deployed.append(aid)
        return deployed

    async def execute_task(self, agent_id, task):
        """Execute a task on a specific agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        agent.status = "active"
        agent.last_active = time.time()
        try:
            result = await self._run_task(agent, task)
            agent.tasks_completed += 1
            agent.status = "standby"
            return {"agent_id": agent_id, "result": result}
        except Exception as exc:
            agent.tasks_failed += 1
            agent.status = "failed"
            return {"agent_id": agent_id, "error": str(exc)}

    async def _run_task(self, agent, task):
        """Run a task against the agent's BrowserEngine."""
        if not isinstance(task, dict):
            return {"error": "Task must be a dict"}

        task_type = task.get("type", "").lower()
        engine = await self._get_or_create_engine(agent)

        if task_type == "navigate":
            url = task.get("url", "")
            if not url:
                return {"error": "navigate requires 'url'"}
            await engine.open(url, task.get("wait_until", "networkidle"), task.get("timeout", 15000))
            # Inject extensions into the loaded page
            if hasattr(engine, '_ext_mgr') and engine._ext_mgr:
                injected = await engine._ext_mgr.inject_on_navigation(engine._page)
                return {"url": await engine.get_url(), "title": await engine.get_title(), "extensions_injected": injected}
            return {"url": await engine.get_url(), "title": await engine.get_title()}

        elif task_type == "extract":
            selector = task.get("selector", "")
            if not selector:
                return {"error": "extract requires 'selector'"}
            result = await engine.extract(selector, task.get("attribute", "text"))
            return {"selector": selector, "results": result}

        elif task_type == "extract_all":
            selector = task.get("selector", "")
            fields = task.get("fields", {})
            if not selector or not fields:
                return {"error": "extract_all requires 'selector' and 'fields'"}
            return {"items": await engine.extract_all(selector, fields)}

        elif task_type == "screenshot":
            path = task.get("path", f"screenshot_{uuid.uuid4().hex[:8]}.png")
            await engine.screenshot(path)
            return {"screenshot": path}

        elif task_type == "click":
            selector = task.get("selector", "")
            if not selector:
                return {"error": "click requires 'selector'"}
            await engine.click(selector, task.get("timeout", 5000))
            return {"clicked": selector}

        elif task_type == "fill":
            selector = task.get("selector", "")
            value = task.get("value", "")
            if not selector:
                return {"error": "fill requires 'selector'"}
            await engine.fill(selector, value, task.get("timeout", 5000))
            return {"filled": selector, "value": value}

        elif task_type == "source":
            return {"source": await engine.get_source()}

        elif task_type == "js":
            code = task.get("code", "")
            if not code:
                return {"error": "js requires 'code'"}
            return {"result": await engine.get_javascript(code)}

        elif task_type == "cookies":
            urls = task.get("urls")
            return {"cookies": await engine.get_cookies(urls)}

        elif task_type == "go_back":
            await engine.go_back()
            return {"url": await engine.get_url()}

        elif task_type == "go_forward":
            await engine.go_forward()
            return {"url": await engine.get_url()}

        elif task_type == "reload":
            await engine.reload()
            return {"url": await engine.get_url(), "title": await engine.get_title()}

        elif task_type == "close":
            await engine.close()
            agent.browser_engine = None
            return {"status": "closed"}

        elif task_type == "state":
            return await engine.get_state()

        elif task_type == "page_type":
            """Generate a PDF of the current page."""
            page_type = task.get("format", "pdf")
            path = task.get("path", f"output_{uuid.uuid4().hex[:8]}.{page_type}")
            if page_type == "pdf":
                result = await engine.cdp_send("Page.printToPDF", {
                    "scale": task.get("scale", 1),
                    "paperWidth": task.get("paper_width", 8.5),
                    "paperHeight": task.get("paper_height", 11),
                })
                if result and isinstance(result, dict) and result.get("data"):
                    import base64
                    pdf_bytes = base64.b64decode(result["data"])
                    Path(path).parent.mkdir(parents=True, exist_ok=True)
                    Path(path).write_bytes(pdf_bytes)
                    return {"pdf": path, "size": len(pdf_bytes)}
                return {"error": "PDF generation failed", "result": result}
            elif page_type == "screenshot":
                await engine.screenshot(path, full_page=task.get("full_page", False))
                return {"screenshot": path}
            return {"error": f"Unknown page_type: {page_type}"}

        elif task_type == "wait_for":
            selector = task.get("selector", "")
            state = task.get("state", "visible")
            timeout = task.get("timeout", 30000)
            if not selector:
                return {"error": "wait_for requires 'selector'"}
            return await engine.wait_for(selector, state, timeout)

        elif task_type == "evaluate":
            code = task.get("code", "")
            if not code:
                return {"error": "evaluate requires 'code'"}
            return {"result": await engine.get_javascript(code)}

        elif task_type == "history":
            action = task.get("action", "back")
            if action == "back":
                await engine.go_back()
                return {"url": await engine.get_url(), "action": "back"}
            elif action == "forward":
                await engine.go_forward()
                return {"url": await engine.get_url(), "action": "forward"}
            else:
                return {"error": f"Unknown history action: {action}"}

        elif task_type == "element_count":
            selector = task.get("selector", "")
            if not selector:
                return {"error": "element_count requires 'selector'"}
            if engine._page:
                count = await engine._page.locator(selector).count()
                return {"selector": selector, "count": count}
            return {"error": "No active page"}

        elif task_type == "wait_for_url":
            pattern = task.get("pattern", "")
            timeout = task.get("timeout", 30000)
            if not pattern:
                return {"error": "wait_for_url requires 'pattern'"}
            return await engine.wait_for_url(pattern, timeout)

        elif task_type == "screenshot_base64":
            full_page = task.get("full_page", False)
            fmt = task.get("format", "png")
            b64 = await engine.screenshot_base64(full_page=full_page, format=fmt)
            return {"screenshot_base64": b64, "format": fmt}

        elif task_type == "new_tab":
            url = task.get("url")
            return await engine.new_tab(url)

        elif task_type == "install_extension":
            manifest = task.get("manifest", {})
            return engine._ext_mgr.install_from_manifest(manifest)

        elif task_type == "list_extensions":
            return engine._ext_mgr.describe()

        elif task_type == "toggle_extension":
            name = task.get("name", "")
            enabled = task.get("enabled", True)
            return engine._ext_mgr.toggle(name, enabled)

        elif task_type == "switch_tab":
            tab_id = task.get("tab_id", "")
            if not tab_id:
                return {"error": "switch_tab requires 'tab_id'"}
            return await engine.switch_tab(tab_id)

        elif task_type == "close_tab":
            tab_id = task.get("tab_id")
            return await engine.close_tab(tab_id)

        elif task_type == "list_tabs":
            return await engine.list_tabs()

        elif task_type == "set_download_path":
            path = task.get("path", "")
            if not path:
                return {"error": "set_download_path requires 'path'"}
            return await engine.set_download_path(path)

        elif task_type == "list_downloads":
            return await engine.list_downloads()

        elif task_type == "set_proxy":
            host = task.get("host", "")
            port = task.get("port", 0)
            if not host or not port:
                return {"error": "set_proxy requires 'host' and 'port'"}
            return await engine.set_proxy(host, port,
                                          task.get("scheme", "http"),
                                          task.get("username"),
                                          task.get("password"))

        else:
            return {"error": f"Unknown task type: {task_type}"}

    async def _get_or_create_engine(self, agent):
        """Get or lazily create a BrowserEngine for the agent."""
        if agent.browser_engine is not None:
            return agent.browser_engine

        from browser.engine import create_engine
        cfg = self._engine_configs.get(agent.agent_id, {})
        cfg = {**cfg, "anonymity_mode": agent.anonymity_mode}
        engine = create_engine(cfg)
        await engine.start()
        agent.browser_engine = engine
        agent.session_id = engine._session_id
        return engine

    async def close_agent(self, agent_id):
        """Close an agent's browser engine and remove it."""
        agent = self._agents.get(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        if agent.browser_engine:
            try:
                await agent.browser_engine.close()
            except Exception:
                pass
            agent.browser_engine = None
        self.remove_agent(agent_id)
        return {"closed": agent_id}

    async def close_all(self):
        """Close all agent browser engines."""
        results = []
        with self._lock:
            agent_ids = list(self._agents.keys())
        for aid in agent_ids:
            r = await self.close_agent(aid)
            results.append(r)
        return {"closed_all": len(results), "results": results}

    def get_stats(self):
        with self._lock:
            agents = list(self._agents.values())
        by_rank = defaultdict(int)
        by_division = defaultdict(int)
        for a in agents:
            by_rank[a.rank] += 1
            by_division[a.division] += 1
        return {
            "total": len(agents),
            "active": sum(1 for a in agents if a.status == "active"),
            "standby": sum(1 for a in agents if a.status == "standby"),
            "failed": sum(1 for a in agents if a.status == "failed"),
            "by_rank": dict(by_rank),
            "by_division": dict(by_division),
        }


class FleetCoordinator:
    """Multi-stage operation coordination for large fleets."""

    def __init__(self, config=None):
        self.config = config or {}
        self._swarm = SwarmCoordinator(
            self.config.get("topology", "hierarchical"))
        self._operations = []

    def create_operation(self, name, agents=None, tasks=None):
        op = {
            "id": f"op_{uuid.uuid4().hex[:8]}",
            "name": name,
            "agents": agents or [],
            "tasks": tasks or [],
            "status": "planned",
            "created_at": time.time(),
        }
        self._operations.append(op)
        return op

    async def execute_operation(self, op_id):
        op = next((o for o in self._operations if o["id"] == op_id), None)
        if not op:
            return {"error": "Operation not found"}
        op["status"] = "running"
        results = []
        for task in op.get("tasks", []):
            for agent_id in op.get("agents", []):
                result = await self._swarm.execute_task(agent_id, task)
                results.append(result)
        op["status"] = "completed"
        op["results"] = results
        return op

    def get_operations(self):
        return self._operations


# ── Singleton ──────────────────────────────────────────────────────
_army_instance = None
_army_lock = threading.Lock()


def get_army():
    global _army_instance
    if _army_instance is None:
        with _army_lock:
            if _army_instance is None:
                _army_instance = FleetCoordinator()
    return _army_instance


if __name__ == "__main__":
    async def main():
        army = get_army()
        ids = army._swarm.deploy_swarms(3, rank="E-1", division="operations")
        print(f"Deployed: {ids}")
        print(f"Stats: {json.dumps(army._swarm.get_stats(), indent=2)}")

        # Test: navigate + extract
        r = await army._swarm.execute_task(ids[0], {"type": "navigate", "url": "https://example.com"})
        print(f"Task result: {json.dumps(r, indent=2)}")

        # Test: screenshot
        r2 = await army._swarm.execute_task(ids[0], {"type": "screenshot", "path": "agent_screenshot.png"})
        print(f"Screenshot: {r2}")

        # Cleanup
        await army._swarm.close_all()
        print("All agents closed.")

    asyncio.run(main())
