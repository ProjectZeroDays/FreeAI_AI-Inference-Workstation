---
name: quantum-c2-ai-agent
description: >
  Quantum C2 AI agent orchestration skill. Use when the user needs to create, configure, and deploy AI agents for autonomous Quantum C2 operations. Covers agent configuration, team orchestration, parallel task execution, model selection, and agent-to-agent communication. Triggers on: "create AI agent", "deploy agent team", "autonomous operation", "agent orchestration", "parallel tasks", "AI operator", "agent configuration", "multi-agent system", "automated C2".
---

# Quantum C2 AI Agent Skill

Configure and deploy AI agents for autonomous Quantum C2 operations.

## Agent Architecture

### Agent Types
| Agent | Role | Model | Capabilities |
|-------|------|-------|--------------|
| **Orchestrator** | Routes tasks, tracks state, makes priority calls | High-reasoning | Decision making, task assignment |
| **Recon Agent** | Network scanning, OSINT, vulnerability assessment | Balanced | Reconnaissance, data collection |
| **Exploit Agent** | Exploit selection, payload generation, deployment | Balanced | Exploitation, payload creation |
| **Postex Agent** | Session management, privilege escalation, persistence | Balanced | Post-exploitation, lateral movement |
| **Deception Agent** | Honeypot deployment, evasion, trigger management | Balanced | Deception ops, anti-detection |
| **Analysis Agent** | Log analysis, reporting, threat assessment | Balanced | Analysis, reporting |
| **Ops Agent** | Routine health checks, monitoring, alerting | Lightweight | Monitoring, maintenance |

### Communication Patterns
- **Async messaging** — Agents communicate via task queue
- **Artifact sharing** — Common workspace for results
- **Handoff protocol** — Structured output for next agent
- **Status reporting** — Real-time progress updates

## Agent Configuration

### Agent Template
```yaml
agent:
  id: "recon-001"
  name: "Reconnaissance Agent"
  type: "recon"
  model: "agnes-pro"
  capabilities:
    - network_scan
    - domain_recon
    - osint_search
    - vuln_assessment
  api_base: "http://localhost:8000"
  auth:
    type: "jwt"
    token_env: "C2_API_TOKEN"
  rate_limit:
    requests_per_minute: 30
    concurrent: 3
  output:
    format: "json"
    save_to: "/shared/artifacts/{agent_id}/{timestamp}"
```

### Model Selection
| Model | Best For | Cost |
|-------|----------|------|
| `agnes-pro` | Complex reasoning, multi-step ops | $$ |
| `agnes-standard` | Balanced operations | $ |
| `agnes-lite` | Simple queries, monitoring | ¢ |
| `gpt-4o` | High-quality analysis | $$ |
| `deepseek-r1-671b` | Reasoning tasks | $ |
| `llama-3.3-70b` | General operations | ¢ |
| Local models | Offline, air-gapped | Free |

## Team Deployment

### 1. Minimal Team (2 Agents)
```
Orchestrator → Recon Agent
Orchestrator → Exploit Agent
```

### 2. Standard Team (4 Agents)
```
Orchestrator
  ├── Recon Agent
  ├── Exploit Agent
  ├── Postex Agent
  └── Deception Agent
```

### 3. Full Team (7 Agents)
```
Orchestrator
  ├── Recon Agent
  ├── Exploit Agent
  ├── Postex Agent
  ├── Deception Agent
  ├── Analysis Agent
  └── Ops Agent
```

### Deployment Command
```bash
# Deploy standard team
POST /api/agents/deploy
{
  "team_size": "standard",
  "model": "agnes-pro",
  "target": "192.168.1.0/24",
  "objectives": ["recon", "exploit", "postex"]
}
```

## Agent Tasks

### Recon Task
```json
{
  "agent_id": "recon-001",
  "task": "full_recon",
  "parameters": {
    "target": "192.168.1.0/24",
    "scan_type": "quick",
    "osint_sources": ["shodan", "censys", "virustotal"],
    "output_format": "json"
  },
  "timeout_seconds": 300
}
```

### Exploit Task
```json
{
  "agent_id": "exploit-001",
  "task": "exploit_deployment",
  "parameters": {
    "target": "192.168.1.100",
    "exploit_name": "force_entry",
    "payload_type": "python",
    "platform": "linux",
    "listener_id": "listen-001"
  },
  "timeout_seconds": 600
}
```

### Postex Task
```json
{
  "agent_id": "postex-001",
  "task": "full_lifecycle",
  "parameters": {
    "session_id": "sess-abc123",
    "objectives": ["priv_esc", "cred_dump", "persistence", "exfil"],
    "exfil_method": "https"
  },
  "timeout_seconds": 1800
}
```

### Deception Task
```json
{
  "agent_id": "deception-001",
  "task": "deploy_deception",
  "parameters": {
    "asset_count": 10,
    "types": ["honeypot", "honeytoken", "canary"],
    "network": "10.0.0.0/24",
    "triggers": ["brute_force", "port_scan"]
  },
  "timeout_seconds": 120
}
```

## Parallel Execution

### Concurrent Task Pattern
```bash
# All agents run simultaneously
POST /api/agents/batch
{
  "tasks": [
    {"agent": "recon-001", "task": "scan_network", "target": "192.168.1.0/24"},
    {"agent": "deception-001", "task": "deploy_honeypots", "count": 5},
    {"agent": "recon-002", "task": "osint_search", "query": "target_company"}
  ],
  "max_concurrent": 3
}
```

### Sequential with Dependencies
```bash
POST /api/agents/chain
{
  "steps": [
    {"agent": "recon-001", "task": "scan"},
    {"agent": "exploit-001", "task": "exploit", "depends_on": ["recon-001"]},
    {"agent": "postex-001", "task": "postex", "depends_on": ["exploit-001"]}
  ]
}
```

## Agent Monitoring

### Status Check
```bash
GET /api/agents/status
GET /api/agents/{agent_id}/status
GET /api/agents/{agent_id}/logs
```

### Results Retrieval
```bash
GET /api/agents/{agent_id}/results
GET /api/agents/{agent_id}/artifacts
```

### Agent Control
```bash
POST /api/agents/{agent_id}/pause
POST /api/agents/{agent_id}/resume
POST /api/agents/{agent_id}/stop
POST /api/agents/{agent_id}/restart
```

## AI Chatbot Integration

The chatbot serves as the primary interface for agent operations:

```
User: "Scan 192.168.1.0/24 and find vulnerabilities"
→ Orchestrator delegates to Recon Agent
→ Recon Agent executes nmap + vuln scan
→ Results returned via chatbot
```

### Chat Commands
```
/scan <target> [scan_type]          → Network scan
/recon <target>                     → Full recon
/exploit <target> <exploit>         → Deploy exploit
/postex <session> [objectives]      → Post-exploitation
/deploy-deception [count]           → Deploy honeypots
/status                             → Check agent status
/stop-all                           → Stop all agents
```

## Autonomous Operation Modes

### 1. Passive Monitoring
- Continuous network monitoring
- Automatic deception response
- Alert on suspicious activity
- No active exploitation

### 2. Assisted Operations
- Human approves each phase
- Agent prepares, human executes
- Full audit trail
- Reversible actions

### 3. Autonomous Execution
- Agent executes full lifecycle
- AI makes tactical decisions
- Human monitors via dashboard
- Emergency stop available

### 4. Scheduled Operations
- Recurring scan schedules
- Automated report generation
- Scheduled deception refresh
- Automatic threat hunting

## Best Practices

### Security
1. Always use JWT authentication
2. Enable audit logging
3. Set rate limits per agent
4. Use separate API keys per agent
5. Monitor agent resource usage

### Performance
1. Batch independent tasks
2. Set appropriate timeouts
3. Use lightweight models for simple tasks
4. Cache recon results
5. Stagger agent startups

### Operations
1. Start with minimal team, scale up
2. Document all agent configurations
3. Maintain operation logs
4. Regular agent health checks
5. Rotate API keys periodically

## Troubleshooting

### Agent Not Responding
```bash
# Check agent status
GET /api/agents/{id}/status

# Restart agent
POST /api/agents/{id}/restart

# Check logs
GET /api/agents/{id}/logs
```

### Task Timeout
```bash
# Increase timeout
POST /api/agents/{id}/tasks
{
  "task": "...",
  "timeout_seconds": 600
}
```

### Rate Limit Exceeded
```bash
# Check rate limits
GET /api/agents/rate-limits

# Reduce concurrent tasks
POST /api/agents/config
{"max_concurrent": 2}
```
