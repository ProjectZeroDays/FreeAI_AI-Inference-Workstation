---
name: quantum-c2-reporting
description: >
  Reporting and analytics for Quantum C2. Use when the user needs to generate reports, view analytics, check audit logs, or export operational data. Triggers on: "report", "analytics", "audit log", "export data", "generate report", "statistics", "operations report", "trend analysis".
---

# Quantum C2 Reporting & Analytics Skill

Generate reports and analyze operational data.

## Report Generation

### Generate Operations Report
```bash
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"operations","format":"json"}'
```

### List Reports
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/reports/
```

### Get Report
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/reports/{id}
```

## Audit Log

### Get Audit Log
```bash
curl -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/audit/?limit=100"
```

### Filter by User
```bash
curl -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/audit/?user_id=1&limit=50"
```

### Filter by Action
```bash
curl -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/audit/?action=exploit_deploy&limit=50"
```

## System Logs

### Get Logs
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/logs/
```

### Log Levels
| Level | Description |
|-------|-------------|
| `debug` | Detailed diagnostic info |
| `info` | Normal operations |
| `warning` | Potential issues |
| `error` | Errors requiring attention |
| `critical` | Critical system failures |

## Telemetry

### System Stats
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/telemetry/stats
```

### Process List
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/telemetry/processes
```

### Network Stats
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/telemetry/network
```

### Disk Info
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/telemetry/disk
```

### Real-Time Stream
```
ws://localhost:8000/api/telemetry/ws
```

## Dashboard Stats

```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/dashboard/
```

## Status Endpoints

```bash
# System health
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/health

# Service status
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/status

# System info
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/system/info
```

## Self-Optimization

### Status
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/self-optimization/status
```

### Metrics
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/self-optimization/metrics
```

### Recommendations
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/self-optimization/recommendations
```

### Trigger Optimization
```bash
curl -X POST http://localhost:8000/api/self-optimization/optimize \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Daily Report
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/self-optimization/daily-report
```

## Chain of Custody

```bash
# List chain of custody items
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/chain-of-custody/

# Add evidence
curl -X POST http://localhost:8000/api/chain-of-custody/ \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"evidence_type":"file","source":"session_abc","description":"Captured document"}'
```

## Export Functions

### Export All Data
```bash
curl -X POST http://localhost:8000/api/reports/export \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format":"json","scope":"all"}'
```

### Export Sessions
```bash
curl -X POST http://localhost:8000/api/reports/export \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format":"csv","scope":"sessions"}'
```

### Export Credentials
```bash
curl -X POST http://localhost:8000/api/reports/export \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format":"json","scope":"credentials"}'
```

## Alert Center

```bash
# Get alerts
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/notifications/

# Mark read
curl -X POST http://localhost:8000/api/notifications/mark-read \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notification_ids":["id1","id2"]}'
```
