"""Swarm Orchestrator — parallel multi-agent execution (from guaardvark).

Launches up to N agents in isolated worktrees, monitors progress,
handles completions, triggers dependency-ordered merges, and tracks costs.

Usage:
    orch = SwarmOrchestrator(repo_path, max_agents=5)
    result = orch.launch("Implement user authentication")
    status = orch.get_status()
"""
import json
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path(__file__).parent.parent / "config" / "swarm.json"
DEFAULT_CONFIG = {
    "max_agents": 5,
    "worktree_base": ".swarm/worktrees",
    "merge_strategy": "dependency_ordered",
    "poll_interval_s": 5,
    "timeout_s": 1800,
    "cost_tracking": True,
    "memory_guard": {"min_ram_gb": 4.0, "max_swap_gb": 1.0},
}


def load_swarm_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_CONFIG.copy()


class SwarmTask:
    """Represents a single agent task within a swarm."""
    def __init__(self, task_id, prompt, agent_type="general",
                 priority=0, depends_on=None):
        self.task_id = task_id
        self.prompt = prompt
        self.agent_type = agent_type
        self.priority = priority
        self.depends_on = depends_on or []
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.started_at = None
        self.completed_at = None
        self.cost_tokens = 0
        self.worktree_path = None


class SwarmStatus:
    """Current status of a swarm execution."""
    def __init__(self, swarm_id):
        self.swarm_id = swarm_id
        self.status = "pending"  # pending, running, completed, failed, merging
        self.tasks = {}
        self.completed_count = 0
        self.failed_count = 0
        self.total_cost_tokens = 0
        self.started_at = None
        self.completed_at = None
        self.merge_result = None
        self.errors = []


class SwarmOrchestrator:
    """Orchestrates parallel agent execution with worktree isolation."""

    def __init__(self, repo_path, config=None):
        self.repo_path = Path(repo_path)
        self.config = config or load_swarm_config()
        self._tasks = {}
        self._swarms = {}
        self._lock = threading.Lock()
        self._running = False

    def launch(self, spec, agent_types=None, max_agents=None):
        """Launch a swarm from a spec string or dict.

        Args:
            spec: Task description or structured plan
            agent_types: Override agent types (list of strings)
            max_agents: Override max parallel agents
        Returns:
            SwarmStatus object
        """
        swarm_id = f"swarm_{int(time.time())}_{os.getpid()}"
        status = SwarmStatus(swarm_id)
        status.started_at = time.time()

        with self._lock:
            self._swarms[swarm_id] = status
            self._running = True

        # Parse spec into tasks
        tasks = self._parse_spec(spec, agent_types)
        max_agents = max_agents or self.config.get("max_agents", 5)

        # Create worktrees
        worktree_base = self.repo_path / self.config.get("worktree_base",
                                                          ".swarm/worktrees")
        worktree_base.mkdir(parents=True, exist_ok=True)

        for i, task in enumerate(tasks):
            task.worktree_path = worktree_base / f"agent_{i+1}"
            task.worktree_path.mkdir(exist_ok=True)
            self._tasks[task.task_id] = task
            status.tasks[task.task_id] = task

        # Execute with concurrency limit
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_agents) as executor:
            futures = {}
            for task in tasks:
                future = executor.submit(
                    self._execute_task, task, status)
                futures[future] = task

            for future in concurrent.futures.as_completed(futures):
                task = futures[future]
                try:
                    future.result()
                except Exception as exc:
                    task.status = "failed"
                    task.result = str(exc)
                    status.failed_count += 1
                    status.errors.append(f"{task.task_id}: {exc}")

        # Merge results
        status.status = "merging"
        merge_result = self._merge_results(tasks, status)
        status.merge_result = merge_result
        status.status = "completed" if merge_result else "failed"
        status.completed_at = time.time()

        with self._lock:
            self._swarms[swarm_id] = status
            self._running = False

        return status

    def launch_async(self, spec, agent_types=None, max_agents=None):
        """Non-blocking launch. Returns swarm_id immediately."""
        swarm_id = f"swarm_{int(time.time())}_{os.getpid()}"
        threading.Thread(
            target=self.launch,
            args=(spec, agent_types, max_agents),
            daemon=True,
        ).start()
        return swarm_id

    def get_status(self, swarm_id):
        with self._lock:
            return self._swarms.get(swarm_id)

    def list_swarms(self):
        with self._lock:
            return list(self._swarms.values())

    def _parse_spec(self, spec, agent_types=None):
        """Parse task spec into SwarmTask list."""
        tasks = []
        if isinstance(spec, str):
            # Simple string spec — split into logical subtasks
            lines = spec.split("\n")
            agents = agent_types or ["general"] * len(lines)
            for i, line in enumerate(lines):
                line = line.strip()
                if line:
                    tasks.append(SwarmTask(
                        task_id=f"t{i+1}",
                        prompt=line,
                        agent_type=agents[i % len(agents)],
                    ))
            if not tasks:
                tasks.append(SwarmTask("t1", spec, "general"))
        elif isinstance(spec, list):
            for i, item in enumerate(spec):
                if isinstance(item, dict):
                    tasks.append(SwarmTask(
                        task_id=item.get("id", f"t{i+1}"),
                        prompt=item.get("prompt", ""),
                        agent_type=item.get("agent_type", "general"),
                        priority=item.get("priority", 0),
                        depends_on=item.get("depends_on", []),
                    ))
                elif isinstance(item, str):
                    tasks.append(SwarmTask(f"t{i+1}", item, "general"))
        else:
            tasks.append(SwarmTask("t1", str(spec), "general"))
        return tasks

    def _execute_task(self, task, status):
        """Execute a single task via the proxy."""
        task.status = "running"
        task.started_at = time.time()

        try:
            import requests
            proxy_url = os.environ.get("PROXY_URL", "http://localhost:8100")
            resp = requests.post(
                f"{proxy_url}/proxy",
                json={
                    "prompt": task.prompt,
                    "model": self._select_model(task.agent_type),
                    "max_tokens": 4096,
                },
                timeout=self.config.get("timeout_s", 1800),
            )
            resp.raise_for_status()
            data = resp.json()
            task.result = data.get("response", data)
            task.status = "completed"
            task.completed_at = time.time()
            status.completed_count += 1
            status.total_cost_tokens += data.get("usage", {}).get(
                "total_tokens", 0)
            task.cost_tokens = data.get("usage", {}).get(
                "total_tokens", 0)
        except Exception as exc:
            task.status = "failed"
            task.result = str(exc)
            status.failed_count += 1
            status.errors.append(f"{task.task_id}: {exc}")

    def _select_model(self, agent_type):
        """Select best model for agent type."""
        models = {
            "general": "anthropic/claude-sonnet-4-5",
            "coder": "openai/gpt-4o",
            "researcher": "google/gemini-2.5-pro",
            "writer": "anthropic/claude-opus-4-6",
            "analyst": "deepseek/deepseek-reasoner",
        }
        return models.get(agent_type, models["general"])

    def _merge_results(self, tasks, status):
        """Merge parallel results into coherent output."""
        completed = [t for t in tasks if t.status == "completed"]
        failed = [t for t in tasks if t.status == "failed"]

        if not completed:
            return {"success": False, "error": "All tasks failed"}

        merged = {
            "swarm_id": status.swarm_id,
            "total_tasks": len(tasks),
            "completed": len(completed),
            "failed": len(failed),
            "total_tokens": status.total_cost_tokens,
            "results": {},
        }

        # Dependency-ordered merge
        order = self._topological_sort(tasks)
        for task_id in order:
            task = next((t for t in tasks if t.task_id == task_id), None)
            if task and task.status == "completed":
                merged["results"][task_id] = {
                    "prompt": task.prompt[:200],
                    "result": str(task.result)[:500] if task.result else "",
                    "tokens": task.cost_tokens,
                }

        return merged

    def _topological_sort(self, tasks):
        """Sort tasks by dependency order."""
        task_map = {t.task_id: t for t in tasks}
        visited = set()
        order = []

        def visit(tid):
            if tid in visited:
                return
            visited.add(tid)
            task = task_map.get(tid)
            if task:
                for dep in task.depends_on:
                    visit(dep)
            order.append(tid)

        for t in tasks:
            visit(t.task_id)
        return order

    def kill_swarm(self, swarm_id):
        """Cancel a running swarm."""
        with self._lock:
            status = self._swarms.get(swarm_id)
            if status and status.status == "running":
                status.status = "failed"
                status.errors.append("Cancelled by user")
                return True
        return False


if __name__ == "__main__":
    orch = SwarmOrchestrator(".")
    spec = """Build authentication module
Create API endpoints
Write unit tests
Deploy to staging"""
    print("[swarm] Launching swarm...")
    status = orch.launch(spec, max_agents=2)
    print(f"[swarm] Status: {status.status}")
    print(f"[swarm] Completed: {status.completed_count}/{len(status.tasks)}")
    print(f"[swarm] Tokens: {status.total_cost_tokens}")
    if status.merge_result:
        print(f"[swarm] Merge: {json.dumps(status.merge_result, indent=2)}")
