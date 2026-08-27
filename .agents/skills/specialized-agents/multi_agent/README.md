# Multi-Agent Orchestration Framework

A modular system for coordinating specialized AI agents using Codex's "Dream Team" pattern. Agents collaborate on complex tasks through structured workflows with clear handoffs.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Router    │  │   State     │  │  Session Manager    │  │
│  │             │  │  Manager    │  │  (Codex spawn)   │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘  │
└─────────┼───────────────────────────────────────────────────┘
          │
    ┌─────┴─────┬─────────────┬─────────────┐
    │           │             │             │
┌───▼───┐  ┌────▼────┐  ┌────▼────┐  ┌─────▼─────┐
│BUILDER│  │ REVIEWER│  │RESEARCHER│  │  EXECUTOR  │
│       │  │         │  │          │  │            │
│• Code │  │• Quality│  │• Web     │  │• Commands  │
│• Scripts│ │• Security│ │• Search  │  │• Scripts   │
│• Solve│  │• Review │  │• Docs    │  │• System    │
└───────┘  └─────────┘  └──────────┘  └────────────┘
```

## 🚀 New: Parallel Execution System

The framework now includes a powerful **Parallel Execution System** for running multiple tasks concurrently with advanced orchestration features:

```
┌─────────────────────────────────────────────────────────────┐
│               PARALLEL ORCHESTRATOR                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Parallel    │  │  Dependency │  │ Result              │  │
│  │   Engine    │  │    Graph    │  │ Aggregator          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Cost      │  │   Circuit   │  │ Concurrency         │  │
│  │ Controller  │  │  Breaker    │  │   Manager           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Parallel Features

- **🔄 Parallel Engine**: Execute multiple tasks concurrently with configurable limits
- **📊 Dependency Graph**: Define task dependencies for complex workflows
- **🔀 Result Aggregation**: 6 strategies (LIST, DICT, MERGE, REDUCE, VOTE, BEST)
- **💰 Cost Control**: Budget enforcement, token tracking, cost reporting
- **⚡ Circuit Breaker**: Fault tolerance and cascade failure prevention
- **🎯 Concurrency Management**: Control resource usage and rate limiting

### Quick Example

```python
from parallel.orchestrator import ParallelOrchestrator
from parallel.aggregator import AggregationStrategy
from multi_agent import Task, AgentRole

# Create orchestrator
orchestrator = ParallelOrchestrator(max_concurrent=5)

# Create workflow
workflow = orchestrator.create_workflow("Parallel Analysis", budget=5.0)

# Add parallel review tasks
orchestrator.add_parallel_group(
    workflow,
    tasks=[
        Task(description="Security review", role=AgentRole.REVIEWER),
        Task(description="Code quality review", role=AgentRole.REVIEWER),
        Task(description="Logic review", role=AgentRole.REVIEWER),
    ],
    strategy=AggregationStrategy.VOTE
)

# Execute with full parallel orchestration
results = await orchestrator.execute_parallel(workflow)
```

See [PARALLEL_GUIDE.md](PARALLEL_GUIDE.md) for comprehensive documentation.

## The Dream Team

| Agent | Role | Capabilities |
|-------|------|--------------|
| **Builder** | Implements solutions | Write code, create scripts, build tools |
| **Reviewer** | Validates quality | Code review, security audit, best practices |
| **Researcher** | Gathers information | Web search, documentation, API exploration |
| **Executor** | Runs commands | Shell execution, system operations (safe mode) |

## Quick Start

### 1. List Available Agents

```bash
cd current Codex workspace/multi_agent
python3 maestro.py list-agents
```

### 2. Create a Workflow

```bash
# Create a Builder + Reviewer workflow
python3 maestro.py create-workflow "Build a script to check SSL certificate expiration"
```

### 3. Check Workflow Status

```bash
python3 maestro.py status <workflow-id>
```

### 4. Run Examples

```bash
# Sequential workflow demo
python3 examples/builder_reviewer_demo.py

# Parallel execution demos
python3 examples/parallel_examples/basic_parallel.py
python3 examples/parallel_examples/map_reduce_demo.py
python3 examples/parallel_examples/voting_consensus.py
python3 examples/parallel_examples/cost_managed_workflow.py
python3 examples/parallel_examples/circuit_breaker_demo.py
python3 examples/parallel_examples/builder_reviewer_parallel.py
```

## File Structure

```
multi_agent/
├── multi_agent.py              # Core framework
├── maestro.py                  # CLI tool
├── parallel/                   # Parallel execution system
│   ├── parallel_engine.py      # Core parallel engine
│   ├── orchestrator.py         # Parallel orchestrator
│   ├── aggregator.py           # Result aggregation (6 strategies)
│   ├── cost_controller.py      # Budget enforcement
│   ├── circuit_breaker.py      # Fault tolerance
│   ├── dependency_graph.py     # Task dependencies
│   ├── examples/               # Parallel examples
│   └── tests/                  # Comprehensive test suite
├── agents/                     # Agent configurations
├── examples/                   # Example workflows
├── tests/                      # Test suite
└── workflows/                  # Saved workflow states
```

## Core Concepts

### Workflow

A workflow is a collection of tasks with dependencies. Workflows can be executed sequentially or in parallel.

```python
from multi_agent import Orchestrator, Workflow, Task, AgentRole

orchestrator = Orchestrator()
workflow = orchestrator.create_workflow("My Workflow")

# Add tasks
task1 = Task(description="Build something", role=AgentRole.BUILDER)
workflow.add_task(task1)

task2 = Task(
    description="Review it", 
    role=AgentRole.REVIEWER,
    parent_task_id=task1.id  # Depends on task1
)
workflow.add_task(task2)
```

### Parallel Workflow

For parallel execution, use the ParallelOrchestrator:

```python
from parallel.orchestrator import ParallelOrchestrator
from parallel.aggregator import AggregationStrategy

orchestrator = ParallelOrchestrator(max_concurrent=5)
workflow = orchestrator.create_workflow("Parallel Workflow", budget=10.0)

# Add independent tasks that can run in parallel
group1 = orchestrator.add_parallel_group(
    workflow,
    tasks=[
        Task(description="Research A", role=AgentRole.RESEARCHER),
        Task(description="Research B", role=AgentRole.RESEARCHER),
    ],
    strategy=AggregationStrategy.LIST
)

# Add dependent tasks
group2 = orchestrator.add_parallel_group(
    workflow,
    tasks=[Task(description="Build", role=AgentRole.BUILDER)],
    dependencies=[group1.group_id],
    strategy=AggregationStrategy.DICT
)

# Execute
results = await orchestrator.execute_parallel(workflow)
```

### Task

The unit of work. Each task has:
- **Role**: Which type of agent should handle it
- **Status**: Pending → Assigned → In Progress → Completed/Failed
- **Input/Output**: Data passed to and from the agent
- **Parent Task**: Optional dependency on another task

### Agent Configuration

Agents are defined via JSON configuration files:

```json
{
  "name": "builder",
  "role": "builder",
  "description": "Implements code and solutions",
  "system_prompt": "You are a Builder agent...",
  "capabilities": ["write_code", "create_scripts"],
  "max_retries": 2
}
```

## Builder + Reviewer Workflow Pattern

The simplest and most common pattern:

```
┌─────────┐     ┌──────────┐     ┌──────────┐
│  USER   │────▶│ BUILDER  │────▶│ REVIEWER │
│ Request │     │  (Build) │     │ (Review) │
└─────────┘     └────┬─────┘     └────┬─────┘
                     │                │
                     ▼                ▼
              ┌──────────┐      ┌──────────┐
              │  Code    │      │  Review  │
              │ Artifact │      │  Report  │
              └──────────┘      └──────────┘
```

**Example Task Flow:**

1. **User** submits: "Create a script to monitor disk usage"
2. **Orchestrator** creates workflow with 2 tasks
3. **Builder** spawns → writes `disk_usage.py` → completes
4. **Orchestrator** detects completion → spawns Reviewer
5. **Reviewer** analyzes → outputs review report → completes
6. **Orchestrator** marks workflow complete

## Parallel Builder + 3 Reviewers Pattern

Advanced pattern with parallel reviews:

```
┌─────────┐     ┌──────────┐
│  USER   │────▶│ BUILDER  │
│ Request │     │  (Build) │
└─────────┘     └────┬─────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   PARALLEL REVIEWS     │
        │  ┌────┐ ┌────┐ ┌────┐  │
        │  │Sec │ │Code│ │Logic│  │
        │  └────┘ └────┘ └────┘  │
        └────────────────────────┘
                     │
                     ▼
              ┌────────────┐
              │  CONSENSUS  │
              └────────────┘
```

## Running Tests

```bash
# Run all tests
cd current Codex workspace/multi_agent
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_aggregator.py -v
python3 -m pytest tests/test_circuit_breaker.py -v
python3 -m pytest tests/test_cost_controller.py -v
python3 -m pytest tests/test_orchestrator.py -v
python3 -m pytest tests/test_integration.py -v

# Run with coverage
python3 -m pytest tests/ --cov=parallel --cov-report=html
```

## Integration with Codex

The framework is designed to integrate with Codex's `spawn_agent` capability:

```python
# In a real implementation with Codex:
session_id = orchestrator.spawn_agent("builder", task)
# This would:
# 1. Create a context file with task details
# 2. Call Codex's session spawn API
# 3. Track the session ID for status monitoring
# 4. Handle completion callbacks
```

The current implementation creates the scaffolding for this integration:
- Context files for each spawned agent
- Session tracking in `active_sessions.json`
- Result files for agent outputs

## Creating Custom Agents

Add a new agent by creating a JSON file in `agents/`:

```bash
cat > agents/custom_analyzer.json << 'EOF'
{
  "name": "custom_analyzer",
  "role": "researcher",
  "description": "Analyzes Python code complexity",
  "system_prompt": "You are a code complexity analyzer...",
  "capabilities": ["analyze_code", "complexity_metrics"]
}
EOF
```

## Programmatic Usage

### Sequential Workflows

```python
from multi_agent import (
    Orchestrator, AgentRegistry, create_default_agents,
    Workflow, Task, AgentRole
)

# Setup
registry = AgentRegistry()
create_default_agents(registry)
orchestrator = Orchestrator(registry=registry)

# Create workflow
workflow = orchestrator.create_workflow("My Task")

# Add builder task
build_task = Task(
    description="Create a REST API client",
    role=AgentRole.BUILDER,
    input_data={"language": "python", "framework": "requests"}
)
workflow.add_task(build_task)

# Add reviewer task
review_task = Task(
    description="Review the API client",
    role=AgentRole.REVIEWER,
    parent_task_id=build_task.id
)
workflow.add_task(review_task)

# Execute
results = orchestrator.execute_workflow(workflow)
```

### Parallel Workflows

```python
from parallel.orchestrator import ParallelOrchestrator
from parallel.aggregator import AggregationStrategy, MapReduceAggregator
from multi_agent import Task, AgentRole

# Setup
orchestrator = ParallelOrchestrator(max_concurrent=5, default_budget=10.0)

# Create parallel workflow
workflow = orchestrator.create_workflow(
    "Map-Reduce Analysis",
    description="Process data in parallel",
    budget=5.0
)

# Map phase: multiple agents work in parallel
orchestrator.add_parallel_group(
    workflow,
    tasks=[
        Task(description=f"Analyze chunk {i}", role=AgentRole.RESEARCHER)
        for i in range(5)
    ],
    group_id="map_phase",
    strategy=AggregationStrategy.LIST
)

# Reduce phase: aggregate results
orchestrator.add_parallel_group(
    workflow,
    tasks=[Task(description="Aggregate results", role=AgentRole.BUILDER)],
    dependencies=["map_phase"],
    group_id="reduce_phase",
    strategy=AggregationStrategy.REDUCE
)

# Execute with full orchestration
results = await orchestrator.execute_parallel(workflow)
```

## Configuration Options

### ParallelOrchestrator Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_concurrent` | int | 5 | Maximum concurrent tasks |
| `default_budget` | float | 10.0 | Default budget per workflow ($) |
| `workspace_dir` | Path | current Codex workspace/multi_agent | Working directory |

### CostController Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_budget` | float | 10.0 | Maximum budget ($) |
| `warning_threshold` | float | 0.8 | Warn at % of budget |
| `policy` | BudgetPolicy | HALT_WORKFLOW | Action on budget exceeded |

### CircuitBreaker Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `failure_threshold` | int | 5 | Failures before opening |
| `recovery_timeout` | float | 30.0 | Seconds before retry |
| `success_threshold` | int | 2 | Successes to close |

## CLI Commands

```bash
# List available agents
python3 maestro.py list-agents

# Create a workflow
python3 maestro.py create-workflow "Description"

# Check workflow status
python3 maestro.py status <workflow-id>

# Run demo
python3 maestro.py demo

# Run parallel examples
python3 examples/parallel_examples/basic_parallel.py
python3 examples/parallel_examples/map_reduce_demo.py
python3 examples/parallel_examples/voting_consensus.py
```

## Design Principles

1. **Simplicity First**: Start with 2-agent workflows, expand as needed
2. **Clear Handoffs**: Explicit task dependencies and state management
3. **Artifact Preservation**: All outputs saved for inspection
4. **Fault Tolerance**: Retry logic, circuit breakers, error recovery
5. **Transparency**: Full visibility into workflow state and costs
6. **Parallel Efficiency**: Execute independent tasks concurrently
7. **Resource Control**: Budget limits, concurrency caps, timeouts

## Documentation

- [PARALLEL_GUIDE.md](PARALLEL_GUIDE.md) - Comprehensive parallel execution guide
- [parallel/](parallel/) - Parallel system implementation
- [examples/parallel_examples/](examples/parallel_examples/) - Working examples
- [tests/](tests/) - Test suite with >80% coverage

## License

MIT License - See LICENSE file for details
