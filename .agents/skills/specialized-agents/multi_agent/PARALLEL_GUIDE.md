# Parallel Execution Guide

Comprehensive guide for the Parallel Multi-Agent Execution System.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
  - [ParallelEngine](#parallelengine)
  - [DependencyGraph](#dependencygraph)
  - [ResultAggregator](#resultaggregator)
  - [CostController](#costcontroller)
  - [CircuitBreaker](#circuitbreaker)
- [Aggregation Strategies](#aggregation-strategies)
- [Workflow Patterns](#workflow-patterns)
- [Configuration](#configuration)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## Overview

The Parallel Execution System enables running multiple AI agent tasks concurrently with:

- **Dependency Management**: Define complex task dependencies
- **Result Aggregation**: 6 strategies for combining results
- **Cost Control**: Budget enforcement and tracking
- **Fault Tolerance**: Circuit breaker pattern for resilience
- **Concurrency Control**: Configurable resource limits

### When to Use Parallel Execution

✅ **Good candidates:**
- Independent tasks (e.g., multiple reviews, parallel research)
- Map-reduce patterns (process chunks, then aggregate)
- Voting/consensus scenarios (multiple opinions)
- Batch processing (many similar tasks)

❌ **Not recommended:**
- Highly sequential workflows (no parallelism to exploit)
- Tasks requiring strict ordering
- Resource-constrained environments

## Architecture

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

### Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Tasks     │────▶│   Parallel  │────▶│   Results   │
│  (Input)    │     │   Engine    │     │  (Raw)      │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Final     │◀────│ Aggregator  │◀────│  Results    │
│   Output    │     │  (Strategy) │     │ (Filtered)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Quick Start

### Basic Parallel Execution

```python
import asyncio
from parallel.parallel_engine import ParallelEngine, Task

async def main():
    # Create engine with max 5 concurrent tasks
    engine = ParallelEngine(max_concurrent=5)
    
    # Define task coroutines
    async def task1():
        await asyncio.sleep(1)
        return "Result 1"
    
    async def task2():
        await asyncio.sleep(1)
        return "Result 2"
    
    # Submit tasks
    engine.submit(Task(task_id="t1", coro=task1))
    engine.submit(Task(task_id="t2", coro=task2))
    
    # Run and get results
    results = await engine.run()
    
    print(results["t1"].result)  # "Result 1"
    print(results["t2"].result)  # "Result 2"

asyncio.run(main())
```

### Using the ParallelOrchestrator

```python
from parallel.orchestrator import ParallelOrchestrator
from parallel.aggregator import AggregationStrategy
from multi_agent import Task, AgentRole

async def main():
    # Create orchestrator
    orch = ParallelOrchestrator(max_concurrent=5)
    
    # Create workflow with budget
    workflow = orch.create_workflow("Analysis", budget=10.0)
    
    # Add parallel tasks
    orch.add_parallel_group(
        workflow,
        tasks=[
            Task(description="Research A", role=AgentRole.RESEARCHER),
            Task(description="Research B", role=AgentRole.RESEARCHER),
        ],
        strategy=AggregationStrategy.LIST
    )
    
    # Execute
    results = await orch.execute_parallel(workflow)
    print(results)

asyncio.run(main())
```

## Core Components

### ParallelEngine

The core execution engine for running tasks concurrently.

```python
from parallel.parallel_engine import ParallelEngine, Task, TaskStatus

# Initialize
engine = ParallelEngine(max_concurrent=5)

# Submit tasks
engine.submit(Task(
    task_id="my_task",
    coro=my_coroutine,
    priority=1,
    depends_on=["other_task"]
))

# Run all tasks
results = await engine.run()

# Check results
for task_id, result in results.items():
    if result.status == TaskStatus.COMPLETED:
        print(f"{task_id}: {result.result}")
    elif result.status == TaskStatus.FAILED:
        print(f"{task_id} failed: {result.error}")
```

**Key Features:**
- Priority-based scheduling
- Dependency resolution
- Concurrent execution limiting
- Task status tracking
- Error handling

### DependencyGraph

Manages task dependencies to ensure correct execution order.

```python
from parallel.dependency_graph import DependencyGraph

graph = DependencyGraph()

# Add tasks with dependencies
graph.add_task("A")           # No dependencies
graph.add_task("B", ["A"])    # Depends on A
graph.add_task("C", ["A"])    # Depends on A
graph.add_task("D", ["B", "C"])  # Depends on B and C

# Get tasks ready to execute
ready = graph.get_ready_tasks()

# Mark task complete
graph.mark_complete("A")

# Check for cycles
has_cycles = graph.has_cycles()
```

**Dependency Patterns:**

```
# Parallel (no dependencies)
A     B     C
│     │     │
▼     ▼     ▼

# Sequential
A ──▶ B ──▶ C

# Fan-out
    ┌──▶ B
A ──┼──▶ C
    └──▶ D

# Fan-in
A ──┐
B ──┼──▶ E
C ──┘

# Diamond
    ┌──▶ B ──┐
A ──┤        ├──▶ D
    └──▶ C ──┘
```

### ResultAggregator

Combines results from multiple tasks using various strategies.

```python
from parallel.aggregator import (
    ResultAggregator,
    AggregationStrategy,
    MapReduceAggregator,
    ConsensusAggregator
)

# Basic aggregation
aggregator = ResultAggregator(strategy=AggregationStrategy.LIST)
results = {'t1': 10, 't2': 20, 't3': 30}
aggregated = aggregator.aggregate(results)
# Result: [10, 20, 30]

# Map-reduce
mr_agg = MapReduceAggregator(reduce_func=lambda a, b: a + b)
result = mr_agg.aggregate({'c1': 10, 'c2': 20, 'c3': 30})
# Result: 60

# Consensus voting
consensus = ConsensusAggregator(min_agreement=0.6)
result = consensus.aggregate({
    'agent1': 'approve',
    'agent2': 'approve',
    'agent3': 'reject'
})
# Result: {'decision': 'approve', 'agreement': 0.67, ...}
```

### CostController

Tracks and enforces budget limits.

```python
from parallel.cost_controller import (
    CostController,
    CostConfig,
    BudgetPolicy
)

# Configure
config = CostConfig(
    max_budget=10.0,
    warning_threshold=0.8,
    policy=BudgetPolicy.HALT_WORKFLOW
)

controller = CostController(config=config)

# Record API calls
controller.record_api_call('codex', estimated_cost=0.03)
controller.record_api_call('openai', tokens_used=1000)

# Check budget
try:
    controller.check_budget()
except BudgetExceeded:
    print("Budget exceeded!")

# Get report
report = controller.get_report()
print(f"Total cost: ${report.total_cost}")
print(f"Budget used: {report.budget_percent}%")
```

### CircuitBreaker

Prevents cascade failures by temporarily blocking requests to failing services.

```python
from parallel.circuit_breaker import CircuitBreaker, CircuitState

# Initialize
cb = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30.0,
    success_threshold=2
)

# Check if request should proceed
if cb.can_execute():
    try:
        result = await call_external_service()
        cb.record_success()
    except Exception:
        cb.record_failure()
        # Circuit may open if threshold reached
else:
    # Circuit is open, use fallback
    result = fallback_response()

# Check state
print(cb.state)  # CLOSED, OPEN, or HALF_OPEN

# Get stats
stats = cb.get_stats()
print(f"Failures: {stats.failures}")
print(f"Rejected: {stats.rejected_calls}")
```

## Aggregation Strategies

### LIST

Returns results as a list in completion order.

```python
aggregator = ResultAggregator(strategy=AggregationStrategy.LIST)
result = aggregator.aggregate({'t1': 10, 't2': 20})
# Result: [10, 20]
```

**Use case:** When order matters and you want all results.

### DICT

Returns results as a dictionary keyed by task ID.

```python
aggregator = ResultAggregator(strategy=AggregationStrategy.DICT)
result = aggregator.aggregate({'agent1': 'yes', 'agent2': 'no'})
# Result: {'agent1': 'yes', 'agent2': 'no'}
```

**Use case:** When you need to track which result came from which task.

### MERGE

Deep merges dictionary results with conflict resolution.

```python
aggregator = ResultAggregator(strategy=AggregationStrategy.MERGE)
result = aggregator.aggregate({
    't1': {'a': 1, 'b': {'c': 2}},
    't2': {'b': {'d': 3}, 'e': 4}
})
# Result: {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}
```

**Use case:** Combining configuration or data objects.

### REDUCE

Applies a reduce function to combine results.

```python
aggregator = ResultAggregator(
    strategy=AggregationStrategy.REDUCE,
    reduce_func=lambda acc, val: acc + val
)
result = aggregator.aggregate({'c1': 10, 'c2': 20, 'c3': 30})
# Result: 60
```

**Use case:** Map-reduce patterns, summing values.

### VOTE

Takes majority vote for categorical results.

```python
aggregator = ResultAggregator(strategy=AggregationStrategy.VOTE)
result = aggregator.aggregate({
    'agent1': 'approve',
    'agent2': 'approve',
    'agent3': 'reject'
})
# Result: 'approve'
```

**Use case:** Consensus-based decisions, multiple reviewers.

### BEST

Selects best result using a scoring function.

```python
aggregator = ResultAggregator(
    strategy=AggregationStrategy.BEST,
    score_func=lambda x: x['confidence']
)
result = aggregator.aggregate({
    't1': {'answer': 'A', 'confidence': 0.7},
    't2': {'answer': 'B', 'confidence': 0.9}
})
# Result: {'answer': 'B', 'confidence': 0.9}
```

**Use case:** Selecting highest confidence answer, best result.

## Workflow Patterns

### Pattern 1: Parallel Map

```
Input ──┬──▶ Task 1 ──┐
        ├──▶ Task 2 ──┼──▶ Results
        └──▶ Task 3 ──┘
```

```python
orchestrator.add_parallel_group(
    workflow,
    tasks=[Task(f"Process {i}") for i in range(5)],
    strategy=AggregationStrategy.LIST
)
```

### Pattern 2: Map-Reduce

```
Data ──┬──▶ Process 1 ──┐
       ├──▶ Process 2 ──┼──▶ Aggregate ──▶ Result
       └──▶ Process 3 ──┘
```

```python
# Map phase
orch.add_parallel_group(workflow, map_tasks, group_id="map")

# Reduce phase
orch.add_parallel_group(
    workflow,
    [reduce_task],
    dependencies=["map"],
    strategy=AggregationStrategy.REDUCE
)
```

### Pattern 3: Fan-Out / Fan-In

```
        ┌──▶ Reviewer 1 ──┐
Build ──┼──▶ Reviewer 2 ──┼──▶ Aggregate
        └──▶ Reviewer 3 ──┘
```

```python
orch.add_parallel_group(workflow, [build_task], group_id="build")
orth.add_parallel_group(
    workflow,
    [reviewer1, reviewer2, reviewer3],
    dependencies=["build"],
    strategy=AggregationStrategy.VOTE
)
```

### Pattern 4: Pipeline

```
A ──▶ B ──▶ C ──▶ D
```

```python
orch.add_parallel_group(workflow, [task_a], group_id="a")
orth.add_parallel_group(workflow, [task_b], dependencies=["a"], group_id="b")
orth.add_parallel_group(workflow, [task_c], dependencies=["b"], group_id="c")
orth.add_parallel_group(workflow, [task_d], dependencies=["c"])
```

## Configuration

### ParallelOrchestrator

```python
orchestrator = ParallelOrchestrator(
    registry=None,              # Custom agent registry
    workspace_dir=None,         # Custom workspace path
    max_concurrent=5,           # Max concurrent tasks
    default_budget=10.0,        # Default budget in $
    circuit_breaker_config=None # Circuit breaker settings
)
```

### CostController

```python
config = CostConfig(
    max_budget=10.0,            # Maximum budget ($)
    warning_threshold=0.8,      # Warn at 80% of budget
    policy=BudgetPolicy.HALT_WORKFLOW,  # Action on breach
    track_api_calls=True,       # Track API call counts
    track_tokens=True,          # Track token usage
    default_api_cost=0.01,      # Default cost per call
    api_costs={                 # Per-API costs
        'codex': 0.03,
        'openai': 0.02,
        'gemini': 0.005
    }
)
```

### CircuitBreaker

```python
cb = CircuitBreaker(
    failure_threshold=5,        # Failures before opening
    recovery_timeout=30.0,      # Seconds before half-open
    half_open_max_calls=3,      # Max calls in half-open
    success_threshold=2,        # Successes to close
    name="service_name",        # Identifier
    on_state_change=callback    # State change callback
)
```

## Examples

### Example 1: Basic Parallel Tasks

See `examples/parallel_examples/basic_parallel.py`

```python
import asyncio
from parallel.parallel_engine import ParallelEngine, Task

async def main():
    engine = ParallelEngine(max_concurrent=3)
    
    async def work(name):
        await asyncio.sleep(0.5)
        return f"{name} done"
    
    for i in range(3):
        engine.submit(Task(
            task_id=f"task_{i}",
            coro=lambda n=i: work(f"Task-{n}")
        ))
    
    results = await engine.run()
    
    for task_id, result in results.items():
        print(f"{task_id}: {result.result}")

asyncio.run(main())
```

### Example 2: Map-Reduce

See `examples/parallel_examples/map_reduce_demo.py`

```python
from parallel.aggregator import MapReduceAggregator

# Process chunks in parallel
chunks = split_data(data, num_chunks)
for i, chunk in enumerate(chunks):
    engine.submit(Task(
        task_id=f"chunk_{i}",
        coro=lambda c=chunk: process_chunk(c)
    ))

results = await engine.run()

# Reduce
aggregator = MapReduceAggregator(reduce_func=lambda a, b: a + b)
total = aggregator.aggregate({k: v.result for k, v in results.items()})
```

### Example 3: Voting Consensus

See `examples/parallel_examples/voting_consensus.py`

```python
from parallel.aggregator import ConsensusAggregator

# Multiple agents vote
for i in range(5):
    engine.submit(Task(
        task_id=f"agent_{i}",
        coro=lambda n=i: agent_vote(f"Agent-{n}", code)
    ))

results = await engine.run()
decisions = {k: v.result['decision'] for k, v in results.items()}

# Aggregate with consensus
aggregator = ConsensusAggregator(min_agreement=0.6)
consensus = aggregator.aggregate(decisions)
print(f"Decision: {consensus['decision']}")
print(f"Agreement: {consensus['agreement']}")
```

### Example 4: Cost Management

See `examples/parallel_examples/cost_managed_workflow.py`

```python
from parallel.cost_controller import CostController, CostConfig

config = CostConfig(max_budget=5.0, policy=BudgetPolicy.HALT_WORKFLOW)
controller = CostController(config=config)

# Check budget before expensive operation
if controller.can_afford(estimated_cost):
    result = await expensive_operation()
    controller.record_api_call('api_name', estimated_cost)
else:
    print("Insufficient budget")
```

### Example 5: Circuit Breaker

See `examples/parallel_examples/circuit_breaker_demo.py`

```python
from parallel.circuit_breaker import CircuitBreaker

cb = CircuitBreaker(failure_threshold=3)

if cb.can_execute():
    try:
        result = await call_external_api()
        cb.record_success()
    except Exception:
        cb.record_failure()
else:
    # Circuit is open
    result = use_fallback()
```

## API Reference

### ParallelEngine

| Method | Description |
|--------|-------------|
| `submit(task)` | Submit a task for execution |
| `run()` | Execute all submitted tasks |
| `shutdown()` | Clean up resources |

### ResultAggregator

| Method | Description |
|--------|-------------|
| `aggregate(results, context)` | Aggregate results using strategy |
| `create_aggregator(strategy, **kwargs)` | Factory function |

### CostController

| Method | Description |
|--------|-------------|
| `record_api_call(api, cost, tokens)` | Record an API call |
| `check_budget()` | Check if budget exceeded |
| `can_afford(cost)` | Check if operation affordable |
| `get_report()` | Get detailed cost report |
| `get_stats()` | Get quick statistics |

### CircuitBreaker

| Method | Description |
|--------|-------------|
| `can_execute()` | Check if request allowed |
| `record_success()` | Record successful call |
| `record_failure()` | Record failed call |
| `call(func, *args, **kwargs)` | Execute with protection |
| `get_stats()` | Get statistics |
| `reset()` | Reset to CLOSED state |

## Troubleshooting

### Common Issues

**Tasks not running in parallel:**
- Check `max_concurrent` setting
- Verify tasks don't have dependencies blocking them
- Ensure tasks are async functions

**Circuit breaker stuck open:**
- Check `recovery_timeout` setting
- Verify `record_success()` is called on success
- Manually reset with `cb.reset()` if needed

**Budget exceeded too early:**
- Check `estimated_cost` values
- Verify per-API costs in config
- Use `can_afford()` to pre-check

**High memory usage:**
- Reduce `max_concurrent`
- Process results incrementally
- Use streaming for large datasets

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Tips

1. **Set appropriate concurrency limits** based on your API rate limits
2. **Use dependency graphs** to maximize parallelism
3. **Choose aggregation strategy** based on your use case
4. **Monitor costs** with CostController reports
5. **Use circuit breakers** for external service calls

## Best Practices

1. **Start Simple**: Use basic parallel execution before complex patterns
2. **Set Budgets**: Always set budget limits for production workflows
3. **Handle Errors**: Use circuit breakers for external dependencies
4. **Monitor**: Track costs and performance metrics
5. **Test**: Test failure scenarios and edge cases

## Further Reading

- [parallel/](parallel/) - Source code
- [tests/](tests/) - Comprehensive tests
- [examples/parallel_examples/](examples/parallel_examples/) - Working examples
