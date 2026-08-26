# Parallel Multi-Agent Execution System
## Implementation Plan for Codex

**Date:** 2026-02-07  
**Status:** Design Phase  
**Target:** True parallel execution for Codex's multi-agent framework

---

## Executive Summary

This document outlines a complete implementation plan for evolving Codex's multi-agent framework from sequential to **true parallel execution**. Based on research into LangChain, CrewAI, AutoGen patterns, and Codex's existing capabilities, this plan delivers a production-ready architecture that can run multiple agents concurrently while managing costs, errors, and synchronization.

### Key Findings

| Aspect | Current State | Target State |
|--------|---------------|--------------|
| Execution | Sequential (one agent at a time) | Parallel (multiple agents concurrently) |
| Coordination | Simple parent-child dependencies | Dynamic task scheduling with dependency graphs |
| Result Collection | Polling-based file checks | Async event-driven with aggregation patterns |
| Error Handling | Basic retry per task | Circuit breakers, exponential backoff, dead letter queues |
| Cost Management | None | Token budgets, rate limiting, cost-aware scheduling |

---

## 1. Understanding Codex's Current Capabilities

### 1.1 Existing Multi-Agent Framework

The current framework (`multi_agent.py`) provides:

- **Agent Registry**: JSON-based agent configurations with roles (Builder, Reviewer, Researcher, Executor)
- **Workflow Engine**: Task DAG with parent-child dependencies
- **Orchestrator**: Routes tasks to appropriate agents
- **State Management**: JSON persistence for workflows and task results

### 1.2 Session Spawning Reality

**Critical Finding:** Codex's `spawn_agent` tool has limitations:

```python
# Current simulated spawn (from multi_agent.py)
def spawn_agent(self, agent_name: str, task: Task) -> str:
    # Creates context files but doesn't actually spawn Codex sessions
    session_id = f"agent:{agent_name}:{task.id}:{int(time.time())}"
    # Would need actual Codex API integration here
```

**Actual Codex Spawn Mechanism (Inferred):**

Based on system context, Codex spawns subagents via:
- Tool calls from main agent
- Subagent receives context in `agent:main:subagent:<uuid>` session
- Subagent executes independently
- Results returned via callback or shared state

**Key Constraints:**
1. Subagents run in separate sessions with isolated context
2. Main agent can spawn multiple subagents but loses direct control
3. Result collection requires polling or file-based coordination
4. No built-in synchronization primitives (barriers, semaphores)

### 1.3 What We CAN Do

✅ **Achievable with Current Codex:**
- Spawn multiple subagents from a parent orchestrator
- Use filesystem as shared state (JSON result files)
- Implement polling-based synchronization
- Control parallelism via Python's `asyncio` or `threading`
- Manage costs through explicit token budgets

❌ **Not Achievable Without Codex Changes:**
- Real-time streaming of subagent outputs
- Direct message passing between subagents
- Shared memory state
- Built-in distributed locking

---

## 2. Research: Multi-Agent Orchestration Patterns

### 2.1 LangGraph / LangChain Patterns

LangChain's multi-agent architectures reveal key insights:

**Router Pattern (Parallel):**
```
User Query → Router LLM → [Agent A, Agent B, Agent C] → Aggregator → Response
```
- Router uses LLM to determine which agents to invoke
- Selected agents run in parallel
- Results aggregated for final output

**Subagent Pattern:**
- Parent agent spawns specialized subagents
- Each subagent handles a sub-task
- Parent collects and synthesizes results

**Key Insight:** For multi-domain tasks, patterns with parallel execution (Subagents, Router) are most efficient—9K tokens vs sequential approaches.

### 2.2 CrewAI Process Types

CrewAI defines three execution models:

| Process | Description | Use Case |
|---------|-------------|----------|
| **Sequential** | Tasks execute in order, output of one → context for next | Linear workflows |
| **Hierarchical** | Manager LLM delegates tasks, reviews outputs | Complex coordination |
| **Consensual** *(planned)* | Democratic decision-making among agents | Collaborative tasks |

**Our Parallel Extension:**

| Process | Description |
|---------|-------------|
| **Parallel** | Independent tasks run concurrently, results aggregated | Embarrassingly parallel work |
| **Map-Reduce** | Map phase (parallel) → Reduce phase (aggregation) | Data processing |
| **Fan-Out-Fan-In** | One task spawns many → many converge to one | Review workflows |

### 2.3 AutoGen Team Patterns

AutoGen provides sophisticated team configurations:

**RoundRobinGroupChat:**
- Agents take turns in round-robin fashion
- Shared context across all agents
- Good for collaborative problem-solving

**SelectorGroupChat:**
- LLM selects next speaker after each message
- Dynamic participation based on context
- More efficient than round-robin for large teams

**Swarm:**
- Uses `HandoffMessage` for explicit transitions
- Agents decide who should handle next
- Flexible, emergent coordination

**Key Lessons for Codex:**
1. **Termination Conditions**: Critical for controlling parallel execution (max turns, keyword detection, external signals)
2. **Streaming**: `run_stream()` provides real-time visibility into parallel agent activity
3. **State Reset**: Teams maintain state; explicit reset needed between unrelated tasks

---

## 3. Proposed Architecture

### 3.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                     │
│                      (CLI, API, or Parent Agent)                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PARALLEL ORCHESTRATOR ENGINE                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  Task Scheduler │  │  Dependency     │  │    Concurrency Manager      │  │
│  │  (Priority Q)   │  │  Graph          │  │    (Semaphore/Pool)         │  │
│  │                 │  │                 │  │                             │  │
│  │ • Prioritize    │  │ • Detect ready  │  │ • Limit parallelism         │  │
│  │   tasks         │  │   tasks         │  │ • Spawn agents              │  │
│  │ • Handle        │  │ • Detect cycles │  │ • Monitor active            │  │
│  │   priorities    │  │ • Track state   │  │ • Enforce budgets           │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  Result         │  │  Cost           │  │    Error Handler            │  │
│  │  Aggregator     │  │  Controller     │  │    (Circuit Breaker)        │  │
│  │                 │  │                 │  │                             │  │
│  │ • Collect       │  │ • Token budgets │  │ • Retry with backoff        │  │
│  │   results       │  │ • Rate limits   │  │ • Dead letter queue         │  │
│  │ • Apply         │  │ • Cost per      │  │ • Failure propagation       │  │
│  │   strategy      │  │   agent         │  │ • Recovery logic            │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   AGENT POOL A      │  │   AGENT POOL B      │  │   AGENT POOL C      │
│  (Builders)         │  │  (Reviewers)        │  │  (Researchers)      │
│                     │  │                     │  │                     │
│ ┌─────┐ ┌─────┐    │  │ ┌─────┐ ┌─────┐    │  │ ┌─────┐ ┌─────┐    │
│ │ A1  │ │ A2  │    │  │ │ R1  │ │ R2  │    │  │ │ S1  │ │ S2  │    │
│ └─────┘ └─────┘    │  │ └─────┘ └─────┘    │  │ └─────┘ └─────┘    │
│ ┌─────┐ ┌─────┐    │  │                     │  │                     │
│ │ A3  │ │ A4  │    │  │                     │  │                     │
│ └─────┘ └─────┘    │  │                     │  │                     │
└──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SHARED STATE LAYER                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────────────┐  │
│  │ Workflow Store │  │ Result Store   │  │ Session Tracking               │  │
│  │ (JSON files)   │  │ (JSON files)   │  │ (active_sessions.json)         │  │
│  │                │  │                │  │                                │  │
│  │ • workflow_*.  │  │ • task_*_      │  │ • session_id → agent mapping   │  │
│  │   json         │  │   result.json  │  │ • start time, status, cost     │  │
│  │ • task deps    │  │ • partial      │  │ • TTL for cleanup              │  │
│  │ • status       │  │   results      │  │                                │  │
│  └────────────────┘  └────────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Core Components

#### 3.2.1 Task Scheduler

Responsible for determining which tasks can run in parallel.

```python
class ParallelTaskScheduler:
    """
    Schedules tasks based on dependency graph and resource availability.
    """
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.dependency_graph = DependencyGraph()
        self.ready_queue = PriorityQueue()
        self.running_tasks: Dict[str, Task] = {}
    
    def get_ready_tasks(self) -> List[Task]:
        """
        Return tasks whose dependencies are all satisfied.
        Respects max_concurrent limit.
        """
        available_slots = self.max_concurrent - len(self.running_tasks)
        
        ready = []
        while len(ready) < available_slots and not self.ready_queue.empty():
            task = self.ready_queue.get()
            if self.dependency_graph.is_satisfied(task):
                ready.append(task)
            else:
                # Put back if deps not satisfied (shouldn't happen with proper logic)
                self.ready_queue.put(task)
        
        return ready
    
    def mark_completed(self, task_id: str):
        """Mark task complete and unblock dependent tasks."""
        self.dependency_graph.mark_complete(task_id)
        # Move newly unblocked tasks to ready queue
        for task in self.dependency_graph.get_newly_ready():
            self.ready_queue.put(task)
```

#### 3.2.2 Dependency Graph

Tracks task relationships and detects cycles.

```python
class DependencyGraph:
    """
    Directed acyclic graph for task dependencies.
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.dependencies: Dict[str, Set[str]] = {}  # task_id -> set of deps
        self.dependents: Dict[str, Set[str]] = {}     # task_id -> set of dependents
        self.completed: Set[str] = set()
    
    def add_task(self, task: Task):
        """Add task with its dependencies."""
        self.tasks[task.id] = task
        self.dependencies[task.id] = set(task.dependencies)
        self.dependents.setdefault(task.id, set())
        
        # Update reverse mapping
        for dep in task.dependencies:
            self.dependents.setdefault(dep, set()).add(task.id)
    
    def is_satisfied(self, task: Task) -> bool:
        """Check if all dependencies are completed."""
        return self.dependencies.get(task.id, set()).issubset(self.completed)
    
    def detect_cycle(self) -> Optional[List[str]]:
        """Detect cycles using DFS. Returns cycle path if found."""
        # Kahn's algorithm or DFS-based cycle detection
        ...
```

#### 3.2.3 Concurrency Manager

Controls how many agents run simultaneously.

```python
class ConcurrencyManager:
    """
    Manages agent spawning with semaphore-based concurrency.
    """
    
    def __init__(self, max_workers: int = 5):
        self.semaphore = asyncio.Semaphore(max_workers)
        self.active_sessions: Dict[str, asyncio.Task] = {}
        self.session_costs: Dict[str, float] = {}  # Track costs per session
    
    async def spawn_agent(self, task: Task, agent_config: AgentConfig) -> str:
        """Spawn agent with concurrency limit."""
        async with self.semaphore:
            session_id = await self._do_spawn(task, agent_config)
            self.active_sessions[session_id] = asyncio.create_task(
                self._monitor_session(session_id, task)
            )
            return session_id
    
    async def _do_spawn(self, task: Task, agent_config: AgentConfig) -> str:
        """Actual spawn logic using Codex subagent."""
        # Create context file
        context = self._build_context(task, agent_config)
        context_path = self._save_context(context)
        
        # This would integrate with actual Codex spawn
        # For now, simulating with subprocess or async execution
        session_id = f"parallel:{agent_config.name}:{task.id}:{uuid.uuid4().hex[:8]}"
        
        # Start subagent (conceptual - actual implementation depends on Codex API)
        # await codex.spawn_session(context_path, session_id)
        
        return session_id
```

#### 3.2.4 Result Aggregator

Collects and combines results from parallel tasks.

```python
from enum import Enum

class AggregationStrategy(Enum):
    """How to combine parallel task results."""
    LIST = "list"           # Simple list of all results
    DICT = "dict"           # Dict keyed by task_id
    MERGE = "merge"         # Deep merge of dict results
    REDUCE = "reduce"       # Apply reduce function
    VOTE = "vote"           # Majority vote (for consensus tasks)
    BEST = "best"           # Select best result by score

class ResultAggregator:
    """
    Aggregates results from parallel task execution.
    """
    
    def __init__(self, strategy: AggregationStrategy = AggregationStrategy.LIST):
        self.strategy = strategy
        self.results: Dict[str, Any] = {}
        self.partial_results: Dict[str, Any] = {}
    
    def add_result(self, task_id: str, result: Any):
        """Add a completed task result."""
        self.results[task_id] = result
    
    def aggregate(self) -> Any:
        """Apply aggregation strategy to all results."""
        if self.strategy == AggregationStrategy.LIST:
            return list(self.results.values())
        
        elif self.strategy == AggregationStrategy.DICT:
            return self.results
        
        elif self.strategy == AggregationStrategy.MERGE:
            merged = {}
            for result in self.results.values():
                if isinstance(result, dict):
                    merged = self._deep_merge(merged, result)
            return merged
        
        elif self.strategy == AggregationStrategy.VOTE:
            return self._majority_vote(list(self.results.values()))
        
        elif self.strategy == AggregationStrategy.BEST:
            return max(
                self.results.values(),
                key=lambda r: r.get('score', 0) if isinstance(r, dict) else 0
            )
        
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
    
    def _deep_merge(self, base: dict, update: dict) -> dict:
        """Recursively merge two dictionaries."""
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
```

#### 3.2.5 Cost Controller

Prevents runaway costs during parallel execution.

```python
@dataclass
class CostBudget:
    """Budget constraints for parallel execution."""
    max_total_cost: float = 10.0          # $10 total
    max_cost_per_task: float = 2.0        # $2 per task
    max_concurrent_tasks: int = 5         # 5 at a time
    max_total_tasks: int = 20             # 20 tasks max
    token_budget_per_task: int = 100000   # 100K tokens per task

class CostController:
    """
    Monitors and enforces cost constraints.
    """
    
    def __init__(self, budget: CostBudget):
        self.budget = budget
        self.total_cost = 0.0
        self.task_costs: Dict[str, float] = {}
        self.token_usage: Dict[str, int] = {}
    
    def can_spawn(self, task: Task, estimated_cost: float = 0.5) -> bool:
        """Check if spawning this task stays within budget."""
        if self.total_cost + estimated_cost > self.budget.max_total_cost:
            return False
        if estimated_cost > self.budget.max_cost_per_task:
            return False
        if len(self.task_costs) >= self.budget.max_total_tasks:
            return False
        return True
    
    def record_cost(self, task_id: str, cost: float, tokens: int):
        """Record actual cost from completed task."""
        self.task_costs[task_id] = cost
        self.token_usage[task_id] = tokens
        self.total_cost += cost
        
        # Check if we need to halt
        if self.total_cost > self.budget.max_total_cost:
            self._trigger_emergency_halt()
    
    def get_cost_report(self) -> dict:
        """Generate cost summary."""
        return {
            "total_cost": self.total_cost,
            "budget": self.budget.max_total_cost,
            "remaining": self.budget.max_total_cost - self.total_cost,
            "task_count": len(self.task_costs),
            "avg_cost_per_task": self.total_cost / max(len(self.task_costs), 1),
            "token_usage": sum(self.token_usage.values())
        }
    
    def _trigger_emergency_halt(self):
        """Stop all execution due to budget overrun."""
        # Write halt file that all agents check
        halt_path = Path("current Codex workspace/.guardrails/HALT").expanduser()
        halt_path.write_text(f"Cost budget exceeded: ${self.total_cost}")
```

---

## 4. Integration with Existing Framework

### 4.1 Enhanced Workflow Model

```python
class ParallelWorkflow(Workflow):
    """
    Extended workflow with parallel execution support.
    """
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.parallel_groups: List[List[str]] = []  # Groups that can run in parallel
        self.aggregation_config: Dict[str, Any] = {}
        self.cost_budget = CostBudget()
    
    def add_parallel_group(self, tasks: List[Task]):
        """
        Define a group of tasks that can run in parallel.
        """
        for task in tasks:
            self.add_task(task)
        self.parallel_groups.append([t.id for t in tasks])
    
    def set_aggregation(self, group_index: int, strategy: AggregationStrategy):
        """Set how to aggregate results from a parallel group."""
        self.aggregation_config[group_index] = strategy
```

### 4.2 Parallel Orchestrator

```python
class ParallelOrchestrator(Orchestrator):
    """
    Extended orchestrator with true parallel execution.
    """
    
    def __init__(self, 
                 registry: AgentRegistry = None,
                 workspace_dir: str = None,
                 max_concurrent: int = 5,
                 budget: CostBudget = None):
        super().__init__(registry, workspace_dir)
        
        self.scheduler = ParallelTaskScheduler(max_concurrent)
        self.concurrency = ConcurrencyManager(max_concurrent)
        self.aggregator = ResultAggregator()
        self.cost_controller = CostController(budget or CostBudget())
        self.error_handler = ErrorHandler()
        
        # Async event loop for parallel execution
        self._loop = asyncio.new_event_loop()
    
    async def execute_parallel(self, workflow: ParallelWorkflow) -> dict:
        """
        Execute workflow with parallel task scheduling.
        """
        workflow.status = TaskStatus.IN_PROGRESS
        
        # Build dependency graph
        for task in workflow.tasks:
            self.scheduler.dependency_graph.add_task(task)
        
        # Check for cycles
        if cycle := self.scheduler.dependency_graph.detect_cycle():
            raise WorkflowError(f"Dependency cycle detected: {' -> '.join(cycle)}")
        
        # Main execution loop
        pending_tasks = set(t.id for t in workflow.tasks)
        completed_tasks = {}
        failed_tasks = {}
        
        while pending_tasks:
            # Get tasks ready to run
            ready = self.scheduler.get_ready_tasks()
            
            if not ready and self.concurrency.active_sessions:
                # Wait for some task to complete
                await asyncio.sleep(0.1)
                self._check_completed_sessions(completed_tasks, failed_tasks)
                continue
            
            if not ready and not self.concurrency.active_sessions:
                # Deadlock or all done
                break
            
            # Spawn agents for ready tasks
            spawn_tasks = []
            for task in ready:
                if not self.cost_controller.can_spawn(task):
                    task.status = TaskStatus.FAILED
                    task.error = "Cost budget exceeded"
                    failed_tasks[task.id] = task
                    pending_tasks.discard(task.id)
                    continue
                
                agent_config = self._get_agent_for_task(task)
                spawn_tasks.append(
                    self.concurrency.spawn_agent(task, agent_config)
                )
                task.status = TaskStatus.IN_PROGRESS
                self.scheduler.running_tasks[task.id] = task
            
            # Wait for spawns to complete
            if spawn_tasks:
                await asyncio.gather(*spawn_tasks, return_exceptions=True)
            
            # Check for completed sessions
            self._check_completed_sessions(completed_tasks, failed_tasks)
        
        # Aggregate results
        if workflow.parallel_groups:
            results = self._aggregate_parallel_results(
                workflow, completed_tasks
            )
        else:
            results = completed_tasks
        
        workflow.status = TaskStatus.COMPLETED if not failed_tasks else TaskStatus.FAILED
        
        return {
            "workflow_id": workflow.id,
            "status": workflow.status.value,
            "completed": len(completed_tasks),
            "failed": len(failed_tasks),
            "cost_report": self.cost_controller.get_cost_report(),
            "results": results
        }
    
    def _aggregate_parallel_results(self, workflow: ParallelWorkflow, 
                                     completed: Dict[str, Task]) -> dict:
        """Aggregate results from parallel groups."""
        aggregated = {}
        
        for i, group in enumerate(workflow.parallel_groups):
            strategy = workflow.aggregation_config.get(i, AggregationStrategy.LIST)
            aggregator = ResultAggregator(strategy)
            
            for task_id in group:
                if task_id in completed:
                    aggregator.add_result(task_id, completed[task_id].output_data)
            
            aggregated[f"group_{i}"] = aggregator.aggregate()
        
        return aggregated
```

---

## 5. Error Handling & Retry Logic

### 5.1 Circuit Breaker Pattern

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """
    Prevents cascade failures in parallel agent execution.
    """
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 30.0,
                 half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        self.half_open_calls = 0
    
    def can_execute(self) -> bool:
        """Check if request should be allowed."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False
        
        return False
    
    def record_success(self):
        """Record successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.half_open_calls = 0
        else:
            self.failures = max(0, self.failures - 1)
    
    def record_failure(self):
        """Record failed execution."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
        elif self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### 5.2 Retry with Exponential Backoff

```python
import random

async def with_retry(func, max_retries: int = 3, 
                     base_delay: float = 1.0,
                     max_delay: float = 60.0,
                     circuit_breaker: CircuitBreaker = None):
    """
    Execute function with retry and exponential backoff.
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        # Check circuit breaker
        if circuit_breaker and not circuit_breaker.can_execute():
            raise CircuitOpenError("Circuit breaker is open")
        
        try:
            result = await func()
            if circuit_breaker:
                circuit_breaker.record_success()
            return result
            
        except Exception as e:
            last_exception = e
            
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            if attempt == max_retries:
                break
            
            # Calculate delay with jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            delay = delay * (0.5 + random.random())  # Add jitter
            
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
            await asyncio.sleep(delay)
    
    raise last_exception
```

### 5.3 Dead Letter Queue

```python
class DeadLetterQueue:
    """
    Stores failed tasks for later analysis/retry.
    """
    
    def __init__(self, path: Path):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
    
    def enqueue(self, task: Task, error: str, context: dict):
        """Add failed task to DLQ."""
        entry = {
            "task": task.to_dict(),
            "error": error,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "retry_count": task.retry_count if hasattr(task, 'retry_count') else 0
        }
        
        dlq_file = self.path / f"{task.id}_{int(time.time())}.json"
        with open(dlq_file, 'w') as f:
            json.dump(entry, f, indent=2)
    
    def list_failed(self) -> List[dict]:
        """List all failed tasks."""
        failed = []
        for f in self.path.glob("*.json"):
            with open(f) as fp:
                failed.append(json.load(fp))
        return sorted(failed, key=lambda x: x['timestamp'], reverse=True)
```

---

## 6. Cost Management

### 6.1 Token Budgeting

```python
class TokenBudget:
    """
    Per-workflow token budget management.
    """
    
    def __init__(self, 
                 input_budget: int = 50000,
                 output_budget: int = 20000,
                 total_budget: int = 70000):
        self.budgets = {
            'input': input_budget,
            'output': output_budget,
            'total': total_budget
        }
        self.used = {'input': 0, 'output': 0, 'total': 0}
    
    def can_allocate(self, estimated_input: int, estimated_output: int) -> bool:
        """Check if allocation stays within budget."""
        return (
            self.used['input'] + estimated_input <= self.budgets['input'] and
            self.used['output'] + estimated_output <= self.budgets['output'] and
            self.used['total'] + estimated_input + estimated_output <= self.budgets['total']
        )
    
    def record_usage(self, input_tokens: int, output_tokens: int):
        """Record actual token usage."""
        self.used['input'] += input_tokens
        self.used['output'] += output_tokens
        self.used['total'] += input_tokens + output_tokens
    
    def get_utilization(self) -> dict:
        """Get budget utilization percentages."""
        return {
            k: (self.used[k] / self.budgets[k] * 100) if self.budgets[k] > 0 else 0
            for k in self.budgets.keys()
        }
```

### 6.2 Cost-Aware Scheduling

```python
class CostAwareScheduler(ParallelTaskScheduler):
    """
    Scheduler that considers cost when selecting tasks.
    """
    
    def __init__(self, max_concurrent: int, cost_controller: CostController):
        super().__init__(max_concurrent)
        self.cost_controller = cost_controller
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Prioritize tasks based on cost efficiency.
        - Prefer cheaper tasks first (fail fast on budget issues)
        - Consider estimated value/cost ratio
        """
        scored = []
        for task in tasks:
            cost = task.estimated_cost or 0.5
            value = task.priority or 1.0
            efficiency = value / cost
            scored.append((efficiency, task))
        
        scored.sort(reverse=True)  # Highest efficiency first
        return [t for _, t in scored]
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal:** Establish async infrastructure and dependency graph

| Task | Description | Deliverable |
|------|-------------|-------------|
| 1.1 | Create `parallel_engine.py` with async task scheduling | Core async scheduler |
| 1.2 | Implement `DependencyGraph` with cycle detection | DAG validation |
| 1.3 | Add `ConcurrencyManager` with semaphore control | Resource limiting |
| 1.4 | Write unit tests for core components | Test coverage >80% |

**Code Example:**
```python
# parallel_engine.py - Phase 1
import asyncio
from typing import List, Dict

class ParallelEngine:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
        self.graph = DependencyGraph()
    
    async def run_parallel(self, tasks: List[Task]) -> Dict[str, Any]:
        """Basic parallel execution."""
        results = {}
        
        async def execute_task(task: Task):
            async with self.semaphore:
                result = await self._execute(task)
                results[task.id] = result
        
        # Run all tasks concurrently (Phase 1: assumes no deps)
        await asyncio.gather(*[execute_task(t) for t in tasks])
        return results
```

### Phase 2: Result Aggregation (Week 2-3)

**Goal:** Implement aggregation strategies and result handling

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2.1 | Implement `ResultAggregator` with all strategies | Aggregation module |
| 2.2 | Add support for partial results and timeouts | Resilient collection |
| 2.3 | Create aggregation examples (map-reduce, vote) | Documentation |
| 2.4 | Integrate with existing workflow system | Backward compatibility |

### Phase 3: Cost Management (Week 3-4)

**Goal:** Add cost controls and budgeting

| Task | Description | Deliverable |
|------|-------------|-------------|
| 3.1 | Implement `CostController` with budgets | Cost tracking |
| 3.2 | Add token usage monitoring | Token budgets |
| 3.3 | Create cost estimation heuristics | Budget prediction |
| 3.4 | Add emergency halt mechanism | Safety controls |

### Phase 4: Error Handling (Week 4-5)

**Goal:** Production-grade reliability

| Task | Description | Deliverable |
|------|-------------|-------------|
| 4.1 | Implement `CircuitBreaker` | Cascade prevention |
| 4.2 | Add retry with exponential backoff | Resilience |
| 4.3 | Create `DeadLetterQueue` | Failure analysis |
| 4.4 | Add comprehensive error reporting | Observability |

### Phase 5: Integration & Polish (Week 5-6)

**Goal:** Full integration with existing framework

| Task | Description | Deliverable |
|------|-------------|-------------|
| 5.1 | Extend `Orchestrator` with parallel execution | Enhanced orchestrator |
| 5.2 | Update `maestro.py` CLI for parallel workflows | CLI updates |
| 5.3 | Create parallel workflow examples | Example gallery |
| 5.4 | Write comprehensive documentation | Final docs |

### Phase 6: Optimization (Week 7+)

**Goal:** Performance tuning and advanced features

| Task | Description | Deliverable |
|------|-------------|-------------|
| 6.1 | Add dynamic worker scaling | Auto-scaling |
| 6.2 | Implement result caching | Optimization |
| 6.3 | Add performance metrics and profiling | Observability |
| 6.4 | Support for distributed execution (future) | Scalability |

---

## 8. File Structure

```
current Codex workspace/multi_agent/
├── multi_agent.py                    # Existing (backward compat)
├── parallel/
│   ├── __init__.py
│   ├── engine.py                     # Core parallel engine
│   ├── scheduler.py                  # Task scheduler
│   ├── dependency_graph.py           # DAG management
│   ├── concurrency.py                # Concurrency manager
│   ├── aggregator.py                 # Result aggregation
│   ├── cost_controller.py            # Cost management
│   ├── error_handling.py             # Circuit breakers, retry
│   └── orchestrator.py               # ParallelOrchestrator
├── maestro.py                        # Enhanced CLI
├── agents/                           # Agent configs (unchanged)
├── examples/
│   ├── builder_reviewer_demo.py      # Existing
│   └── parallel_examples/
│       ├── map_reduce_example.py
│       ├── fan_out_fan_in.py
│       ├── voting_consensus.py
│       └── cost_managed_workflow.py
├── workflows/                        # Saved workflows
└── IMPLEMENTATION_PLAN.md            # This document
```

---

## 9. Usage Examples

### 9.1 Basic Parallel Execution

```python
from multi_agent.parallel import ParallelOrchestrator, ParallelWorkflow
from multi_agent import Task, AgentRole

# Create orchestrator
orch = ParallelOrchestrator(max_concurrent=5)

# Create workflow
workflow = ParallelWorkflow("Parallel Research")

# Add independent tasks that can run in parallel
tasks = [
    Task("Research Python async patterns", AgentRole.RESEARCHER),
    Task("Research Rust concurrency", AgentRole.RESEARCHER),
    Task("Research Go goroutines", AgentRole.RESEARCHER),
]

workflow.add_parallel_group(tasks)

# Execute
results = await orch.execute_parallel(workflow)
# All three research tasks run concurrently!
```

### 9.2 Map-Reduce Pattern

```python
# Map phase: Process chunks in parallel
map_tasks = [
    Task(f"Analyze chunk {i}", AgentRole.BUILDER, input_data={"chunk": chunk})
    for i, chunk in enumerate(data_chunks)
]

workflow.add_parallel_group(map_tasks)
workflow.set_aggregation(0, AggregationStrategy.LIST)

# Reduce phase: Aggregate results (depends on map)
reduce_task = Task(
    "Combine analysis results",
    AgentRole.BUILDER,
    dependencies=[t.id for t in map_tasks]
)
workflow.add_task(reduce_task)
```

### 9.3 Cost-Managed Execution

```python
from multi_agent.parallel import CostBudget

budget = CostBudget(
    max_total_cost=5.0,      # $5 max
    max_concurrent_tasks=3,   # 3 at a time
    token_budget_per_task=50000
)

orch = ParallelOrchestrator(budget=budget)

# Will halt if budget exceeded
results = await orch.execute_parallel(workflow)
print(orch.cost_controller.get_cost_report())
```

---

## 10. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Cost Overruns** | High | Strict budgets, emergency halt, cost-aware scheduling |
| **Race Conditions** | Medium | File-based locking, atomic operations, careful state management |
| **Deadlocks** | Medium | Cycle detection in DAG, timeout handling, deadlock detection |
| **Resource Exhaustion** | Medium | Semaphore limits, worker pools, backpressure |
| **Codex API Changes** | Low | Abstract spawn interface, version checking |

---

## 11. Success Criteria

✅ **Phase 1 Complete:**
- [ ] Async engine executes 5+ tasks concurrently
- [ ] Dependency graph correctly orders tasks
- [ ] Unit tests pass

✅ **Phase 3 Complete:**
- [ ] Cost tracking within 10% of actual API costs
- [ ] Emergency halt works within 1 second
- [ ] Token budgets enforced

✅ **Phase 5 Complete:**
- [ ] Builder + 3 Reviewers run in parallel
- [ ] CLI supports `--parallel` flag
- [ ] Backward compatible with existing workflows

✅ **Phase 6 Complete:**
- [ ] 3x speedup vs sequential for parallel workloads
- [ ] <5% overhead from orchestration
- [ ] Zero resource leaks in 24-hour stress test

---

## 12. Conclusion

This implementation plan provides a production-ready path to true parallel multi-agent execution in Codex. Key innovations:

1. **Async-First Architecture**: Built on asyncio for true concurrency
2. **Cost Safety First**: Budgets and controls prevent runaway spending
3. **Production Reliability**: Circuit breakers, retries, and DLQs
4. **Flexible Aggregation**: Multiple strategies for combining parallel results
5. **Incremental Adoption**: Phases allow gradual rollout

The design respects Codex's current constraints while delivering significant performance improvements for parallel workloads.

---

**Next Steps:**
1. Review and approve plan
2. Begin Phase 1 implementation
3. Set up monitoring for cost tracking
4. Create test harness for parallel workflows
