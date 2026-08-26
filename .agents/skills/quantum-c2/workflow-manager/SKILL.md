---
name: quantum-c2-workflow-manager
description: >
  Quantum C2 workflow management skill. Use when the user asks about workflows, automation, pipeline creation, or operational workflows. Triggers on: "workflow", "automation", "pipeline", "kill chain", "incident response", "compliance assessment", "red team", "blue team", "purple team", "vulnerability scan", "threat intel".
---

# Quantum C2 Workflow Manager

Create, manage, and execute operational workflows across the Quantum C2 platform.

## Workflow Architecture

### Workflow Object Model
```json
{
  "id": "wf-abc123",
  "name": "Full Kill Chain",
  "description": "Complete offensive security workflow",
  "type": "offensive",
  "status": "active",
  "version": "1.0.0",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "stages": [
    {
      "id": "stage-1",
      "name": "Reconnaissance",
      "tool": "recon",
      "order": 1,
      "config": {"scan_type": "quick"},
      "on_success": "stage-2",
      "on_failure": "retry|abort"
    },
    {
      "id": "stage-2",
      "name": "Exploitation",
      "tool": "exploit",
      "order": 2,
      "config": {"exploit_name": "force_entry"},
      "on_success": "stage-3",
      "on_failure": "retry|abort"
    }
  ],
  "scheduling": {
    "type": "manual|cron|event",
    "cron": "0 2 * * *",
    "trigger_event": "scan_complete"
  },
  "notifications": {
    "on_start": true,
    "on_success": true,
    "on_failure": true,
    "channels": ["webhook", "email", "websocket"]
  },
  "ai_integration": {
    "enabled": true,
    "model": "claude-sonnet-4-20250514",
    "decision_points": ["stage-1", "stage-3"]
  }
}
```

## API Endpoints

### List Workflows
```bash
GET /api/workflows
GET /api/workflows?status=active
GET /api/workflows?type=offensive
```

### Get Workflow Details
```bash
GET /api/workflows/{workflow_id}
```

### Create Workflow
```bash
POST /api/workflows
{
  "name": "Custom Workflow",
  "description": "Custom operational workflow",
  "type": "offensive",
  "stages": [
    {"tool": "recon", "config": {"scan_type": "quick"}, "next": "stage-2"},
    {"tool": "exploit", "config": {"exploit_name": "force_entry"}, "next": null}
  ]
}
```

### Update Workflow
```bash
PUT /api/workflows/{workflow_id}
```

### Delete Workflow
```bash
DELETE /api/workflows/{workflow_id}
```

### Execute Workflow
```bash
POST /api/workflows/{workflow_id}/execute
{
  "target": "192.168.1.100",
  "params": {"scan_type": "quick", "exploit": "force_entry"}
}
```

### Get Execution Status
```bash
GET /api/workflows/{workflow_id}/executions/{execution_id}
GET /api/workflows/{workflow_id}/executions/{execution_id}/stages/{stage_id}
```

### Schedule Workflow
```bash
POST /api/workflows/{workflow_id}/schedule
{
  "type": "cron",
  "cron": "0 2 * * *",
  "timezone": "UTC"
}
```

### Get Execution History
```bash
GET /api/workflows/{workflow_id}/executions
GET /api/workflows/{workflow_id}/executions?limit=50
```

## Workflow Templates

### Full Kill Chain
```bash
GET /api/workflows/templates/kill_chain
```
**Stages:**
1. Reconnaissance (nmap scan)
2. Vulnerability Analysis (CVE matching)
3. Weaponization (payload generation)
4. Delivery (stager deployment)
5. Exploitation (exploit execution)
6. Installation (persistence)
7. Command & Control (listener setup)
8. Actions on Objectives (data staging)
9. Exfiltration (data extraction)
10. Cleanup (log wiping)

**Execution:**
```bash
# Create from template
curl -X POST http://localhost:8000/api/workflows/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "kill_chain", "name": "Operation Nightfall"}'

# Execute
curl -X POST http://localhost:8000/api/workflows/kill_chain_wf/execute \
  -H "Content-Type: application/json" \
  -d '{"target": "192.168.1.100"}'
```

### Compliance Assessment
```bash
GET /api/workflows/templates/compliance_assessment
```
**Stages:**
1. Asset Discovery (inventory)
2. Policy Validation (compliance check)
3. Gap Analysis (find discrepancies)
4. Remediation Planning (fix recommendations)
5. Verification (re-scan)
6. Report Generation (PDF output)

**Execution:**
```bash
curl -X POST http://localhost:8000/api/workflows/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "compliance_assessment", "name": "Q1 Compliance Review"}'
```

### Incident Response
```bash
GET /api/workflows/templates/incident_response
```
**Stages:**
1. Detection (SIEM alert)
2. Triage (severity assessment)
3. Containment (isolate affected systems)
4. Eradication (remove threat)
5. Recovery (restore operations)
6. Lessons Learned (post-mortem)

**Execution:**
```bash
curl -X POST http://localhost:8000/api/workflows/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "incident_response", "name": "IR-2024-001"}'
```

### Red Team Exercise
```bash
GET /api/workflows/templates/red_team
```
**Stages:**
1. Rules of Engagement (ROE validation)
2. Target Selection (authorized targets)
3. Reconnaissance (broad scanning)
4. Initial Access (entry point identification)
5. Persistence (maintain access)
6. Lateral Movement (internal pivot)
7. Privilege Escalation (highest access)
8. Objective Achievement (data/objective)
9. Reporting (comprehensive report)

**Execution:**
```bash
curl -X POST http://localhost:8000/api/workflows/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "red_team", "name": "Exercise Crimson"}'
```

### Blue Team Defense
```bash
GET /api/workflows/templates/blue_team
```
**Stages:**
1. Baseline Establishment (normal state)
2. Monitoring Configuration (alert rules)
3. Detection Tuning (reduce false positives)
4. Response Playbook (automated response)
5. Validation (test detection)
6. Optimization (improve coverage)

**Execution:**
```bash
curl -X POST http://localhost:8000/api/workflows/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "blue_team", "name": "Defense Baseline"}'
```

### Purple Team Collaboration
```bash
GET /api/workflows/templates/purple_team
```
**Stages:**
1. Attack Planning (red team)
2. Detection Planning (blue team)
3. Attack Execution (controlled)
4. Detection Validation (blue team)
5. Gap Analysis (what was missed)
6. Control Improvement (tuning)
7. Re-attack (validation)
8. Final Report (findings)

**Execution:**
```bash
curl -X POST http://localhost:8000/api/workflows/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "purple_team", "name": "Purple Exercise 01"}'
```

### Automated Vulnerability Scan
```bash
GET /api/workflows/templates/vuln_scan
```
**Stages:**
1. Asset Discovery (scope definition)
2. Port Scanning (service enumeration)
3. Vulnerability Scanning (CVE matching)
4. Risk Assessment (CVSS scoring)
5. Report Generation (findings)
6. Remediation Tracking (fix tracking)

**Execution:**
```bash
curl -X POST http://localhost:8000/api/workflows/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "vuln_scan", "name": "Weekly Vuln Scan"}'
```

### Threat Intelligence Collection
```bash
GET /api/workflows/templates/threat_intel
```
**Stages:**
1. Feed Subscription (IOC sources)
2. Collection (automated pull)
3. Enrichment (correlation)
4. Analysis (pattern detection)
5. Dissemination (sharing)
6. Integration (SOC update)

**Execution:**
```bash
curl -X POST http://localhost:8000/api/workflows/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "threat_intel", "name": "Daily Intel Sweep"}'
```

## Workflow Execution

### Real-time Monitoring
```bash
# WebSocket for live updates
ws://localhost:8000/api/workflows/{id}/executions/{exec_id}/ws

# WebSocket message types
{
  "type": "stage_start|stage_complete|stage_fail|workflow_complete",
  "stage": "stage-1",
  "result": {...},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Stage Control
```bash
# Pause workflow
POST /api/workflows/{id}/executions/{exec_id}/pause

# Resume workflow
POST /api/workflows/{id}/executions/{exec_id}/resume

# Skip stage
POST /api/workflows/{id}/executions/{exec_id}/skip-stage
{"stage_id": "stage-2"}

# Abort workflow
POST /api/workflows/{id}/executions/{exec_id}/abort
```

### Stage Execution Override
```bash
# Override stage config
POST /api/workflows/{id}/executions/{exec_id}/stage/{stage_id}/override
{
  "config": {"scan_type": "stealth"}
}
```

## Workflow Scheduling

### Manual Schedule
```bash
POST /api/workflows/{id}/schedule
{
  "type": "cron",
  "cron": "0 2 * * *",
  "params": {"target": "192.168.1.0/24"}
}
```

### Event-Based Trigger
```bash
POST /api/workflows/{id}/schedule
{
  "type": "event",
  "event": "vulnerability_detected",
  "filter": {"severity": "critical"}
}
```

### Interval Schedule
```bash
POST /api/workflows/{id}/schedule
{
  "type": "interval",
  "interval_seconds": 3600,
  "max_concurrent": 1
}
```

### Get Schedule Status
```bash
GET /api/workflows/{id}/schedule
GET /api/workflows/{id}/schedules
```

## Workflow Results Aggregation

### Stage Results
```bash
GET /api/workflows/{id}/executions/{exec_id}/results
```

**Response:**
```json
{
  "execution_id": "exec-abc123",
  "workflow_id": "wf-kill-chain",
  "status": "completed",
  "started_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:45:00Z",
  "stages": [
    {
      "id": "stage-1",
      "name": "Reconnaissance",
      "status": "completed",
      "started_at": "2024-01-15T10:00:00Z",
      "completed_at": "2024-01-15T10:10:00Z",
      "result": {"hosts_found": 5, "open_ports": 12}
    }
  ],
  "summary": {
    "total_time": "45m",
    "hosts_scanned": 5,
    "vulnerabilities_found": 3,
    "exploits_successful": 1
  }
}
```

### Aggregate Reports
```bash
GET /api/workflows/{id}/executions/{exec_id}/report
GET /api/workflows/{id}/executions/{exec_id}/report?format=pdf
GET /api/workflows/{id}/executions/{exec_id}/report?format=json
```

### Historical Aggregation
```bash
GET /api/workflows/{id}/executions?limit=100&date_from=2024-01-01&date_to=2024-01-31
```

## AI Agent Integration

### AI-Driven Workflows
```bash
# Enable AI decision points
POST /api/workflows/{id}/ai-config
{
  "enabled": true,
  "model": "claude-sonnet-4-20250514",
  "decision_points": ["stage-1_complete", "stage-3_complete"],
  "fallback": "manual_review"
}
```

### AI-Powered Workflow Generation
```bash
# Describe workflow in natural language
POST /api/workflows/from-natural-language
{
  "description": "Scan the internal network, find vulnerabilities, and generate a report",
  "type": "offensive"
}
```

### AI Workflow Optimization
```bash
# Analyze and optimize workflow
POST /api/workflows/{id}/optimize
{
  "analysis_type": "performance",
  "target": "reduce_execution_time"
}
```

## Workflow Versioning

### List Versions
```bash
GET /api/workflows/{id}/versions
```

### Create Version
```bash
POST /api/workflows/{id}/versions
{
  "version": "2.0.0",
  "changes": "Added AI decision points",
  "created_by": "admin"
}
```

### Rollback
```bash
POST /api/workflows/{id}/rollback
{
  "version": "1.5.0"
}
```

## Workflows

### Create and Execute Kill Chain
```bash
# 1. Create from template
curl -X POST http://localhost:8000/api/workflows/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "kill_chain", "name": "Op Nightfall"}'

# 2. Execute
curl -X POST http://localhost:8000/api/workflows/nf_wf/execute \
  -H "Content-Type: application/json" \
  -d '{"target": "192.168.1.100", "params": {"scan_type": "quick"}}'

# 3. Monitor
curl http://localhost:8000/api/workflows/nf_wf/executions/exec-001
```

### Schedule Regular Scan
```bash
# 1. Create workflow
curl -X POST http://localhost:8000/api/workflows/from-template \
  -H "Content-Type: application/json" \
  -d '{"template": "vuln_scan", "name": "Weekly Scan"}'

# 2. Schedule weekly
curl -X POST http://localhost:8000/api/workflows/ws_wf/schedule \
  -H "Content-Type: application/json" \
  -d '{"type": "cron", "cron": "0 2 * * 1"}'
```

## Best Practices

1. **Use templates as starting points** — Customize rather than build from scratch
2. **Validate before execution** — Test workflow structure
3. **Enable notifications** — Stay informed of progress
4. **Use AI for decision points** — Leverage AI for complex branching
5. **Version control workflows** — Track changes over time
6. **Schedule regular runs** — Automate recurring tasks
7. **Aggregate results** — Build historical analysis
8. **Review execution logs** — Identify bottlenecks

## Troubleshooting

### Workflow Stalled
```bash
# Check execution status
curl http://localhost:8000/api/workflows/{id}/executions/{exec_id}

# Check stage status
curl http://localhost:8000/api/workflows/{id}/executions/{exec_id}/stages
```

### Stage Failing
```bash
# Get stage error
curl http://localhost:8000/api/workflows/{id}/executions/{exec_id}/stages/{stage_id}

# Retry stage
curl -X POST http://localhost:8000/api/workflows/{id}/executions/{exec_id}/retry-stage \
  -d '{"stage_id": "stage-2"}'
```

### Workflow Not Starting
```bash
# Check schedule
curl http://localhost:8000/api/workflows/{id}/schedule

# Check dependencies
curl http://localhost:8000/api/workflows/{id}/dependencies
```
