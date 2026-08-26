---
name: agent-orchestration
description: Coordinate AI agents for Quantum C2 operations. Use when managing agent teams, delegating tasks, or orchestrating autonomous operations.
trigger_keywords: agent, orchestrate, autonomous, multi-agent, team, delegate, coordinate, AI agent
---

## Purpose
Orchestrates AI agent teams for parallel operations, task delegation, and autonomous execution within the Quantum C2 framework.

## When to Use
- When user asks to "deploy agents" or "orchestrate agents"
- For parallel task execution
- When autonomous operations are needed
- For multi-agent coordination

## Workflow
1. Define agent team composition
2. Submit tasks to agent queue
3. Monitor agent execution
4. Collect and synthesize results
5. Generate operation report

## Commands
```bash
# Check agent health
curl http://localhost:8000/api/agents/health

# Submit task to agent team
curl -X POST http://localhost:8000/api/agents/tasks \
  -H "Content-Type: application/json" \
  -d '{"task": "recon task", "priority": "high"}'

# List active agents
curl http://localhost:8000/api/agents/

# Check task queue
curl http://localhost:8000/api/agents/queue

# Get agent status
curl http://localhost:8000/api/agents/status

# Run autonomous operation
python -c "from offense_agent import OffenseAgent; a = OffenseAgent(); print(a.status())"
```

## Agent Types
| Agent | Module | Purpose |
|-------|--------|---------|
| OffenseAgent | `offense_agent.py` | Offensive operations |
| BotnetHandler | `botnet_handler.py` | Device coordination |
| DHSOrchestrator | `dhs_orchestrator.py` | Homeland defense ops |
| APTLogic | `apt_logic.py` | APT simulation |

## Task Queue Patterns
```python
# Submit parallel tasks
tasks = [
    {"type": "recon", "target": "example.com"},
    {"type": "scan", "target": "192.168.1.0/24"},
    {"type": "osint", "target": "example.com"}
]

# Process with agent team
for task in tasks:
    agent.submit(task)
```

## Agent Team Commands
```bash
# Start agent team
python -c "from agents import AgentTeam; t = AgentTeam(); t.start()"

# Check team status
python -c "from agents import AgentTeam; t = AgentTeam(); print(t.status())"

# Get team results
python -c "from agents import AgentTeam; t = AgentTeam(); print(t.get_results())"
```

## Notes
- Agents communicate via shared message queue
- Task priority: critical > high > medium > low
- Results aggregated and deduplicated
- See `.learnings/FEATURE_REQUESTS.md` for autonomous completion feature
