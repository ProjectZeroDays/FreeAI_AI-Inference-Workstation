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
