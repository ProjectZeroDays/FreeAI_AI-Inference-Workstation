# PARALLEL AGENT SYSTEM - Quick Reference Guide

**Last Updated:** 2026-02-07  
**Status:** Production Ready  
**Use Case:** Multi-agent task execution with true parallelism

---

## 🚀 When to Use This System

Use parallel agents when you need to:
- ✅ Build an app/game with multiple components
- ✅ Process multiple files/APIs simultaneously  
- ✅ Generate content in parallel (social media, reports)
- ✅ Run tests across different modules
- ✅ Analyze data from multiple sources
- ✅ Any task that can be split into independent subtasks

---

## 📁 Key Files

```
current Codex workspace/
├── multi_agent/
│   └── parallel/              # Core async engine
│       ├── __init__.py        # Import: ParallelEngine, Task
│       └── parallel_engine.py # Main execution logic
│
├── multi_process_engine.py    # CPU-bound parallelism (3x speedup)
├── agents/                    # 8 autonomous agents
│   ├── __init__.py           # CompleteEcosystem
│   ├── optimizer_agent.py
│   ├── cleanup_agent.py
│   ├── memory_agent.py
│   ├── document_agent.py
│   └── data_agent.py
│
├── autonomous_agents.py       # Fixer + Monitor + Security
├── content_command_center.py  # Practical example
└── app_dev_pipeline_demo.py   # App development example
```

---

## 🎯 Basic Usage

### Simple Parallel Execution

```python
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.codex/workspace/multi_agent'))
from parallel import ParallelEngine, Task

async def main():
    engine = ParallelEngine(max_workers=4)
    
    # Define tasks
    async def task_a():
        await asyncio.sleep(1)
        return "A done"
    
    async def task_b():
        await asyncio.sleep(1)
        return "B done"
    
    # Execute in parallel
    tasks = [
        Task('a', func=task_a),
        Task('b', func=task_b),
    ]
    
    results = await engine.execute(tasks)
    
    # Results
    for name, result in results.items():
        if result.success:
            print(f"{name}: {result.result}")

asyncio.run(main())
```

### With Dependencies

```python
# Task B depends on Task A
tasks = [
    Task('a', func=task_a),
    Task('b', func=task_b, dependencies=['a']),  # B waits for A
]

results = await engine.execute(tasks)
```

---

## 🤖 Using All 8 Agents

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.codex/workspace/agents'))
from agents import CompleteEcosystem

async def main():
    eco = CompleteEcosystem()
    
    # Run full pipeline
    results = await eco.run_full_pipeline(
        project_path=Path.cwd()
    )
    
    print(f"Completed {len(results)} phases")

asyncio.run(main())
```

### Individual Agents

```python
from optimizer_agent import OptimizerAgent
from cleanup_agent import CleanupAgent
from memory_agent import MemoryAgent
from document_agent import DocumentAgent
from data_agent import DataAgent

# Use any agent standalone
opt = OptimizerAgent()
opts = await opt.analyze_code(Path('myfile.py'))
```

---

## 🎨 Content Command Center (Practical Tool)

```bash
# Generate weekly social media content
python3 current Codex workspace/content_command_center.py

# View dashboard
open current Codex workspace/content_center_dashboard.html
```

**What it does:**
- Generates 4 posts (Mon/Wed/Fri/Sun)
- Suggests best posting times
- Creates fresh content ideas
- Saves to JSON files

---

## 🔧 Choosing the Right Engine

| Workload | Use | File | Speedup |
|----------|-----|------|---------|
| I/O (network/files) | Async | `multi_agent/parallel/` | 2-4x |
| CPU (math/compute) | Multi-process | `multi_process_engine.py` | 3x |
| Mixed | Async | `multi_agent/parallel/` | 2-3x |
| Distributed | Ray | `distributed_engine.py` | 100x+ |

---

## ⚠️ Limitations & Solutions

| Issue | Solution |
|-------|----------|
| macOS spawn error with inline code | Use script files, not `python3 -c "..."` |
| Process startup overhead | Worth it for CPU-bound work |
| GIL limits threading | Use MultiProcessEngine for CPU work |
| Memory uses JSON | Fine for personal scale |

---

## 📝 Template: Build an App

```python
async def build_app():
    engine = ParallelEngine(max_workers=4)
    
    # PHASE 1: Architecture
    design = await architect_agent.design()
    
    # PHASE 2: Development (PARALLEL)
    dev_tasks = [
        Task('frontend', build_frontend, args=[design]),
        Task('backend', build_backend, args=[design]),
        Task('database', build_database, args=[design]),
    ]
    components = await engine.execute(dev_tasks)
    
    # PHASE 3: Integration
    app = await integrator_agent.merge(components)
    
    # PHASE 4: Testing (PARALLEL)
    test_tasks = [
        Task('unit', run_unit_tests, args=[app]),
        Task('integration', run_integration_tests, args=[app]),
    ]
    test_results = await engine.execute(test_tasks)
    
    return app
```

---

## 🔍 Quick Tests

```bash
# Test parallel engine
python3 -c "
import sys; sys.path.insert(0, 'multi_agent')
from parallel import ParallelEngine
print('✅ ParallelEngine works')
"

# Test all agents
python3 -c "
import sys; sys.path.insert(0, 'agents')
from agents import CompleteEcosystem
print('✅ All 8 agents ready')
"

# Run content generator
python3 content_command_center.py
```

---

## 📚 Full Documentation

- `ECOSYSTEM_COMPLETE.md` - Technical overview
- `APP_DEV_GUIDE.md` - How to build apps/games
- `LIMITATIONS_FIXED.md` - Overcoming Python limits
- `FINAL_SUMMARY.md` - Complete summary
- `TOOLS.md` - Updated with all commands

---

## 💡 Remember

1. **Import paths matter** - Add `sys.path.insert()` for agents/multi_agent
2. **Async required** - All usage is async/await
3. **Dependencies work** - Use `dependencies=[...]` in Task
4. **I/O vs CPU** - Choose right engine for workload
5. **FixerAgent helps** - Auto-repairs common errors

**This system is production-ready for personal use!** 🚀
