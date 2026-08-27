---
name: quantum-c2-agents
description: >
  AI Agent Team orchestration for Quantum C2. Use when the user wants to create, manage, and deploy AI agent teams for parallel operations. Covers team creation, task submission, template execution, and agent monitoring. Triggers on: "agent team", "deploy agents", "parallel operations", "AI agents", "autonomous agents", "agent orchestration", "multi-agent", "agent team management", "task queue".
---

# Quantum C2 Agent Team Skill

Deploy and manage AI agent teams for parallel Quantum C2 operations.

## Team Management

### List Teams
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/agents/teams
```

### Create Team (Standard — 4 agents)
```bash
curl -X POST http://localhost:8000/api/agents/teams \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "team_size": "standard",
    "model": "agnes-pro"
  }'
```

### Team Sizes
| Size | Agents | Composition |
|------|--------|-------------|
| `mini` | 2 | Orchestrator + Recon |
| `standard` | 4 | + Exploit, Postex |
| `full` | 7 | + Deception, Analysis, Ops |

### Get Team Status
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/agents/teams/{team_id}
```

### Delete Team
```bash
curl -X DELETE http://localhost:8000/api/agents/teams/{team_id} \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Agent Management

### List Agents
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/agents/teams/{team_id}/agents
```

### Switch Agent Model
```bash
curl -X POST http://localhost:8000/api/agents/teams/{team_id}/agents/{agent_id}/switch-model \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "agnes-standard"}'
```

## Task Submission

### Submit Task
```bash
curl -X POST http://localhost:8000/api/agents/teams/{team_id}/tasks \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "network_scan",
    "parameters": {
      "target": "192.168.1.0/24",
      "scan_type": "quick"
    },
    "timeout_seconds": 300
  }'
```

### Task Types by Agent
| Agent Type | Task Types |
|------------|------------|
| Recon | `network_scan`, `domain_recon`, `osint_search`, `simulate_attack` |
| Exploit | `exploit_deploy`, `payload_generate` |
| Postex | `session_command`, `postex_full_lifecycle` |
| Deception | `deception_seed`, `trigger_seed` |
| Ops | `health_check`, `get_sessions`, `get_listeners` |

### List Tasks
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/agents/teams/{team_id}/tasks
```

### Execute All Tasks
```bash
curl -X POST http://localhost:8000/api/agents/teams/{team_id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["task-id-1", "task-id-2"]'
```

## Operation Templates

### List Templates
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/agents/templates
```

### Run Template
```bash
curl -X POST http://localhost:8000/api/agents/teams/{team_id}/run-template \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "full_recon",
    "params": {
      "target": "192.168.1.0/24",
      "domain": "target.com"
    }
  }'
```

### Available Templates
| Template | Tasks | Description |
|----------|-------|-------------|
| `full_recon` | 3 | Network + domain + OSINT scan |
| `exploit_deployment` | 2 | Deploy exploit + generate payload |
| `postex_chain` | 1 | Full post-exploitation chain |
| `deception_deploy` | 2 | Deploy honeypots + triggers |
| `attack_simulation` | 1 | Simulate attack |

## System Status

### Health Check
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/agents/health
```

### Statistics
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/agents/stats
```

## Team Control

### Pause Team
```bash
curl -X POST http://localhost:8000/api/agents/teams/{team_id}/pause \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Resume Team
```bash
curl -X POST http://localhost:8000/api/agents/teams/{team_id}/resume \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Stop Team
```bash
curl -X POST http://localhost:8000/api/agents/teams/{team_id}/stop \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Agent Types

| Type | Role | Capability |
|------|------|------------|
| `orchestrator` | Routes tasks, makes decisions | All |
| `recon` | Network/domain/OSINT | Scan, search, analyze |
| `exploit` | Exploit deployment | Deploy, generate payloads |
| `postex` | Post-exploitation | Commands, persistence, exfil |
| `deception` | Deception ops | Honeypots, evasion, triggers |
| `analysis` | Log analysis | Reports, threat assessment |
| `ops` | Maintenance | Health checks, monitoring |

## Quick Start

```bash
# 1. Create team
TEAM=$(curl -s -X POST http://localhost:8000/api/agents/teams \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"team_size":"standard","model":"agnes-pro"}')
TEAM_ID=$(echo $TEAM | python -c "import sys,json; print(json.load(sys.stdin)['team_id'])")

# 2. Run recon template
curl -s -X POST http://localhost:8000/api/agents/teams/$TEAM_ID/run-template \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template":"full_recon","params":{"target":"192.168.1.0/24"}}'

# 3. Check status
curl -s -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/agents/teams/$TEAM_ID

# 4. Get results
curl -s -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/agents/teams/$TEAM_ID/tasks
```
