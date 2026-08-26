---
name: quantum-c2-ai-agent-manager
description: >
  Quantum C2 AI agent management skill. Use when the user asks about AI agents, agent orchestration, agent configuration, or agent management. Triggers on: "AI agent", "agent orchestration", "agent configuration", "agent team", "ORCH", "RECON agent", "EXPLOIT agent", "POSTEX agent", "DEFENSE agent", "COMPLIANCE agent", "INTEL agent", "agent fallback", "model selection".
---

# Quantum C2 AI Agent Manager

Configure and manage AI agents for automated operations across Quantum C2.

## Agent Types

### 7 Agent Types
| Type | Abbreviation | Role | Primary Tools |
|------|--------------|------|---------------|
| Orchestration | ORCH | Coordinates multi-agent workflows | workflow, sessions, policies |
| Reconnaissance | RECON | Performs reconnaissance operations | recon, network, osint |
| Exploitation | EXPLOIT | Deploys exploits and generates payloads | exploit, payloads, brute_force |
| Post-Exploitation | POSTEX | Manages compromised sessions | postex, sessions, persistence |
| Defense | DEFENSE | Monitors and defends systems | defense, detection, hardening |
| Compliance | COMPLIANCE | Ensures policy adherence | compliance, audit, reporting |
| Intelligence | INTEL | Collects and analyzes threat intel | intel, threat_intel, analysis |

## Agent Configuration

### Agent Object Model
```json
{
  "id": "agent-abc123",
  "name": "Alpha Recon Agent",
  "type": "RECON",
  "status": "active",
  "model_config": {
    "model": "claude-sonnet-4-20250514",
    "temperature": 0.3,
    "max_tokens": 4096,
    "top_p": 0.9
  },
  "system_prompt": "You are a reconnaissance specialist...",
  "fallback_chain": [
    {"model": "claude-opus-4-20250514", "priority": 1},
    {"model": "gpt-4o", "priority": 2},
    {"model": "ollama/llama3", "priority": 3},
    {"model": "local", "priority": 4}
  ],
  "tool_permissions": {
    "allowed": ["recon", "network", "osint", "intel"],
    "blocked": ["exploit", "postex", "botnet"]
  },
  "resource_limits": {
    "max_concurrent_tasks": 5,
    "max_execution_time": 3600,
    "max_memory_mb": 2048
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## API Endpoints

### List Agents
```bash
GET /api/agents
GET /api/agents?type=RECON
GET /api/agents?status=active
```

### Get Agent Details
```bash
GET /api/agents/{agent_id}
```

### Create Agent
```bash
POST /api/agents
{
  "name": "Bravo Exploit Agent",
  "type": "EXPLOIT",
  "model_config": {
    "model": "claude-sonnet-4-20250514",
    "temperature": 0.2,
    "max_tokens": 4096
  },
  "system_prompt": "You are an exploitation specialist...",
  "tool_permissions": {
    "allowed": ["exploit", "payloads", "brute_force"],
    "blocked": []
  }
}
```

### Update Agent
```bash
PUT /api/agents/{agent_id}
```

### Delete Agent
```bash
DELETE /api/agents/{agent_id}
```

### Activate Agent
```bash
POST /api/agents/{agent_id}/activate
```

### Deactivate Agent
```bash
POST /api/agents/{agent_id}/deactivate
```

### Reset Agent Context
```bash
POST /api/agents/{agent_id}/reset
```

## Agent Team Management

### Create Agent Team
```bash
POST /api/agent-teams
{
  "name": "Alpha Team",
  "description": "Full-spectrum operations team",
  "agents": [
    {"type": "ORCH", "count": 1},
    {"type": "RECON", "count": 2},
    {"type": "EXPLOIT", "count": 1},
    {"type": "POSTEX", "count": 1}
  ],
  "coordination": {
    "task_queue": true,
    "result_aggregation": true,
    "handoff_strategy": "sequential"
  }
}
```

### Get Team Details
```bash
GET /api/agent-teams/{team_id}
```

### Add Agent to Team
```bash
POST /api/agent-teams/{team_id}/agents
{
  "agent_id": "agent-abc123"
}
```

### Remove Agent from Team
```bash
DELETE /api/agent-teams/{team_id}/agents/{agent_id}
```

### Get Team Status
```bash
GET /api/agent-teams/{team_id}/status
```

**Response:**
```json
{
  "team_id": "team-abc123",
  "agents": [
    {
      "id": "agent-001",
      "type": "RECON",
      "status": "idle",
      "current_task": null,
      "tasks_completed": 42,
      "avg_response_time_ms": 1200
    }
  ],
  "metrics": {
    "total_agents": 5,
    "active_agents": 3,
    "idle_agents": 2,
    "avg_task_completion_time": "4.2m",
    "success_rate": 0.94
  }
}
```

## Task Submission

### Submit Task to Agent
```bash
POST /api/agents/{agent_id}/tasks
{
  "task_type": "recon_scan",
  "description": "Scan target network",
  "params": {
    "target": "192.168.1.0/24",
    "scan_type": "quick"
  },
  "priority": "normal",
  "timeout_seconds": 3600
}
```

### Submit Task to Team
```bash
POST /api/agent-teams/{team_id}/tasks
{
  "description": "Full kill chain operation",
  "phases": [
    {"type": "recon", "params": {"target": "192.168.1.100"}},
    {"type": "exploit", "params": {"exploit": "force_entry"}},
    {"type": "postex", "params": {"persistence": true}}
  ]
}
```

### Get Task Status
```bash
GET /api/agents/{agent_id}/tasks/{task_id}
GET /api/agents/{agent_id}/tasks?status=pending|running|completed|failed
```

### Cancel Task
```bash
POST /api/agents/{agent_id}/tasks/{task_id}/cancel
```

## Agent Result Aggregation

### Get Task Result
```bash
GET /api/agents/{agent_id}/tasks/{task_id}/result
```

### Aggregate Results
```bash
POST /api/agent-teams/{team_id}/aggregate
{
  "task_ids": ["task-001", "task-002", "task-003"],
  "aggregation": "summary|detailed"
}
```

**Response:**
```json
{
  "team_id": "team-abc123",
  "tasks": 3,
  "aggregate_result": {
    "total_hosts_found": 15,
    "total_vulnerabilities": 23,
    "critical_vulns": 3,
    "exploits_successful": 2,
    "sessions_established": 1
  },
  "individual_results": [...]
}
```

### Export Results
```bash
GET /api/agents/{agent_id}/tasks/{task_id}/export?format=json
GET /api/agents/{agent_id}/tasks/{task_id}/export?format=pdf
```

## Agent Fallback Chain

### Configure Fallback
```bash
PUT /api/agents/{agent_id}/model-config
{
  "fallback_chain": [
    {"model": "claude-opus-4-20250514", "priority": 1, "max_retries": 3},
    {"model": "gpt-4o", "priority": 2, "max_retries": 3},
    {"model": "ollama/llama3", "priority": 3, "max_retries": 2},
    {"model": "local", "priority": 4, "max_retries": 1}
  ]
}
```

### Monitor Fallback
```bash
GET /api/agents/{agent_id}/fallback-status
```

**Response:**
```json
{
  "current_model": "claude-sonnet-4-20250514",
  "fallback_active": false,
  "last_fallback": null,
  "fallback_count_24h": 2,
  "model_health": {
    "claude-sonnet-4-20250514": {"status": "healthy", "latency_ms": 450},
    "claude-opus-4-20250514": {"status": "healthy", "latency_ms": 800},
    "gpt-4o": {"status": "degraded", "latency_ms": 1200},
    "ollama/llama3": {"status": "healthy", "latency_ms": 2000}
  }
}
```

### Force Model Switch
```bash
POST /api/agents/{agent_id}/force-model
{
  "model": "claude-opus-4-20250514"
}
```

## Agent Skill Integration

### Assign Skill to Agent
```bash
POST /api/agents/{agent_id}/skills
{
  "skill": "reconnaissance",
  "level": "expert"
}
```

### Get Agent Skills
```bash
GET /api/agents/{agent_id}/skills
```

### Bulk Skill Assignment
```bash
POST /api/agent-teams/{team_id}/assign-skills
{
  "skills": [
    {"type": "RECON", "skill": "network_scanning", "level": "expert"},
    {"type": "EXPLOIT", "skill": "payload_generation", "level": "advanced"}
  ]
}
```

## Agent Performance Monitoring

### Get Agent Metrics
```bash
GET /api/agents/{agent_id}/metrics
GET /api/agents/{agent_id}/metrics?range=24h
```

**Response:**
```json
{
  "agent_id": "agent-abc123",
  "period": "24h",
  "tasks_submitted": 45,
  "tasks_completed": 42,
  "tasks_failed": 3,
  "avg_response_time_ms": 1250,
  "p99_response_time_ms": 3500,
  "tokens_used": 125000,
  "cost_usd": 2.50,
  "model_switches": 2,
  "fallback_activations": 1
}
```

### Get Team Metrics
```bash
GET /api/agent-teams/{team_id}/metrics
```

### Performance Alerts
```bash
POST /api/agents/alerts
{
  "type": "performance",
  "condition": "avg_response_time > 2000ms",
  "action": "notify",
  "recipients": ["admin"]
}
```

## Agent Templates

### Pre-built Agent Templates
```bash
GET /api/agents/templates
```

**Available Templates:**
| Template | Type | Description |
|----------|------|-------------|
| `recon_specialist` | RECON | Optimized for network reconnaissance |
| `exploit_specialist` | EXPLOIT | Focused on exploitation |
| `postex_operator` | POSTEX | Post-exploitation expert |
| `defense_analyst` | DEFENSE | Defensive operations |
| `compliance_auditor` | COMPLIANCE | Policy and compliance |
| `intel_analyst` | INTEL | Threat intelligence |
| `team_leader` | ORCH | Orchestration and coordination |

### Create from Template
```bash
POST /api/agents/from-template
{
  "template": "recon_specialist",
  "name": "Custom Recon Agent"
}
```

## Workflows

### Create and Configure Agent
```bash
# 1. Create from template
curl -X POST http://localhost:8000/api/agents/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "recon_specialist", "name": "Alpha Recon"}'

# 2. Configure model
curl -X PUT http://localhost:8000/api/agents/agent-001/model-config \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-sonnet-4-20250514", "temperature": 0.2, "fallback_chain": [{"model": "claude-opus-4-20250514"}, {"model": "gpt-4o"}]}'

# 3. Assign skills
curl -X POST http://localhost:8000/api/agents/agent-001/skills \
  -H "Content-Type: application/json" \
  -d '{"skill": "network_scanning", "level": "expert"}'
```

### Create and Manage Team
```bash
# 1. Create team
curl -X POST http://localhost:8000/api/agent-teams \
  -H "Content-Type: application/json" \
  -d '{"name": "Task Force Alpha", "agents": [{"type": "RECON", "count": 2}, {"type": "EXPLOIT", "count": 1}]}'

# 2. Submit task to team
curl -X POST http://localhost:8000/api/agent-teams/team-001/tasks \
  -H "Content-Type: application/json" \
  -d '{"description": "Network assessment", "phases": [{"type": "recon", "params": {"target": "10.0.0.0/24"}}]}'

# 3. Monitor team
curl http://localhost:8000/api/agent-teams/team-001/status
```

## Best Practices

1. **Use templates** — Start from pre-built templates
2. **Configure fallback chains** — Ensure reliability
3. **Set appropriate limits** — Prevent resource exhaustion
4. **Monitor performance** — Track metrics regularly
5. **Use least privilege** — Restrict tool access
6. **Version agent configs** — Track changes
7. **Test before production** — Validate in staging

## Troubleshooting

### Agent Not Responding
```bash
# Check agent status
curl http://localhost:8000/api/agents/agent-001

# Check fallback status
curl http://localhost:8000/api/agents/agent-001/fallback-status

# Reset agent
curl -X POST http://localhost:8000/api/agents/agent-001/reset
```

### Task Stuck
```bash
# Check task status
curl http://localhost:8000/api/agents/agent-001/tasks/task-001

# Cancel stuck task
curl -X POST http://localhost:8000/api/agents/agent-001/tasks/task-001/cancel
```

### Model Failing
```bash
# Check model health
curl http://localhost:8000/api/agents/agent-001/fallback-status

# Force switch model
curl -X POST http://localhost:8000/api/agents/agent-001/force-model \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-opus-4-20250514"}'
```
