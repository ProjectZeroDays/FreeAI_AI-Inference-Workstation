---
name: quantum-c2-self-healing-configurator
description: >
  Quantum C2 self-healing configurator skill. Use when the user asks about self-healing, self-repair, or autonomous recovery. Triggers on: "self-healing", "self-repair", "autonomous recovery", "health check", "auto-restart", "failover", "self-diagnosis", "recovery procedures".
---

# Quantum C2 Self-Healing Configurator

Configure autonomous self-healing and recovery for Quantum C2 infrastructure.

## Health Check Configuration

### Global Health Checks
```bash
POST /api/self-healing/health/global/config
{
  "enabled": true,
  "interval_seconds": 30,
  "checks": [
    {"name": "flask_backend", "endpoint": "/api/health", "expected_status": 200},
    {"name": "database", "endpoint": "/api/health/db", "expected_status": 200},
    {"name": "redis", "endpoint": "/api/health/redis", "expected_status": 200},
    {"name": "websocket_server", "endpoint": "/api/health/ws", "expected_status": 200}
  ]
}
```

### Component Health Checks
```bash
POST /api/self-healing/health/component/{component}
{
  "interval_seconds": 60,
  "timeout_seconds": 10,
  "healthy_threshold": 3,
  "unhealthy_threshold": 2
}
```

### Get Health Status
```bash
GET /api/self-healing/health/status
```

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "overall": "healthy",
  "components": {
    "flask_backend": {"status": "healthy", "response_time_ms": 5, "uptime": "72h"},
    "database": {"status": "healthy", "response_time_ms": 2, "connections": 15},
    "redis": {"status": "healthy", "response_time_ms": 1, "memory_usage": "45%"},
    "websocket_server": {"status": "degraded", "response_time_ms": 150, "active_connections": 45}
  }
}
```

## Auto-Restart Policies

### Service Restart Policies
```bash
POST /api/self-healing/policies/auto-restart
{
  "service": "flask_backend",
  "enabled": true,
  "conditions": [
    {"condition": "unhealthy", "action": "restart"},
    {"condition": "high_cpu", "threshold": 90, "action": "restart"},
    {"condition": "high_memory", "threshold": 85, "action": "restart"},
    {"condition": "timeout", "threshold_seconds": 30, "action": "restart"}
  ],
  "cooldown_seconds": 300,
  "max_restarts_per_hour": 5,
  "notify_on_restart": true
}
```

### Restart History
```bash
GET /api/self-healing/policies/auto-restart/history
```

**Response:**
```json
{
  "restarts": [
    {
      "timestamp": "2024-01-15T08:00:00Z",
      "service": "flask_backend",
      "reason": "unhealthy",
      "duration_seconds": 5,
      "success": true
    }
  ],
  "count_24h": 3,
  "avg_duration_seconds": 4.5
}
```

## Failover Configuration

### Primary-Secondary Setup
```bash
POST /api/self-healing/failover/config
{
  "service": "database",
  "primary": {"host": "db-primary", "port": 5432},
  "secondary": {"host": "db-secondary", "port": 5432},
  "health_check": {"interval_seconds": 10, "timeout_seconds": 5},
  "failover_action": "automatic",
  "auto_revert": true,
  "revert_delay_seconds": 3600
}
```

### Get Failover Status
```bash
GET /api/self-healing/failover/status
```

### Manual Failover
```bash
POST /api/self-healing/failover/trigger
{
  "service": "database",
  "target": "secondary"
}
```

## Self-Diagnosis Workflows

### Trigger Diagnosis
```bash
POST /api/self-healing/diagnose/trigger
{
  "scope": "all",
  "depth": "full"
}
```

### Diagnosis Results
```bash
GET /api/self-healing/diagnose/results/{diagnosis_id}
```

**Response:**
```json
{
  "diagnosis_id": "diag-001",
  "started_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:02:00Z",
  "status": "completed",
  "issues_found": 2,
  "findings": [
    {
      "severity": "high",
      "component": "websocket_server",
      "issue": "High connection latency",
      "root_cause": "Memory leak detected",
      "recommendation": "Restart service and apply memory limit"
    },
    {
      "severity": "medium",
      "component": "redis",
      "issue": "Memory usage above threshold",
      "root_cause": "Key expiration not configured",
      "recommendation": "Configure TTL for cache keys"
    }
  ],
  "actions_taken": [
    {"action": "restart", "component": "websocket_server", "success": true}
  ]
}
```

### Scheduled Diagnosis
```bash
POST /api/self-healing/diagnose/schedule
{
  "type": "cron",
  "cron": "0 */6 * * *",
  "scope": "all",
  "notify_on_issues": true
}
```

## Recovery Procedures

### Define Recovery Procedure
```bash
POST /api/self-healing/recovery/procedures
{
  "name": "Database Recovery",
  "trigger": "database_unhealthy",
  "steps": [
    {"step": 1, "action": "verify_connectivity", "timeout_seconds": 30},
    {"step": 2, "action": "restart_service", "timeout_seconds": 60},
    {"step": 3, "action": "run_health_check", "timeout_seconds": 30},
    {"step": 4, "action": "verify_data_integrity", "timeout_seconds": 120}
  ],
  "on_failure": "escalate_to_admin"
}
```

### Execute Recovery
```bash
POST /api/self-healing/recovery/execute
{
  "procedure_name": "Database Recovery",
  "dry_run": false
}
```

### Recovery History
```bash
GET /api/self-healing/recovery/history
```

## Alert Configuration

### Alert Rules
```bash
POST /api/self-healing/alerts/rules
{
  "name": "Service Down Alert",
  "condition": "service_status = 'unhealthy' AND duration > 60s",
  "severity": "critical",
  "actions": [
    {"type": "restart_service"},
    {"type": "notify", "channel": "slack", "webhook": "https://hooks.slack.com/..."},
    {"type": "notify", "channel": "email", "recipients": ["admin@example.com"]}
  ]
}
```

### Alert Channels
```bash
POST /api/self-healing/alerts/channels
{
  "type": "slack",
  "webhook_url": "https://hooks.slack.com/..."
}

POST /api/self-healing/alerts/channels
{
  "type": "email",
  "smtp_host": "smtp.example.com",
  "recipients": ["admin@example.com"]
}

POST /api/self-healing/alerts/channels
{
  "type": "webhook",
  "url": "https://api.example.com/alerts"
}
```

### Alert History
```bash
GET /api/self-healing/alerts/history
GET /api/self-healing/alerts/history?severity=critical
```

## Self-Healing Schedule

### Create Schedule
```bash
POST /api/self-healing/schedule
{
  "name": "Daily Health Check",
  "type": "cron",
  "cron": "0 3 * * *",
  "actions": [
    {"type": "health_check", "scope": "all"},
    {"type": "diagnose", "scope": "all"},
    {"type": "cleanup", "max_age_days": 7}
  ],
  "notify": true
}
```

### Get Schedules
```bash
GET /api/self-healing/schedules
```

### Schedule Control
```bash
POST /api/self-healing/schedules/{id}/enable
POST /api/self-healing/schedules/{id}/disable
DELETE /api/self-healing/schedules/{id}
```

## Integration with Agnes AI

### AI-Driven Diagnosis
```bash
POST /api/self-healing/ai/diagnose
{
  "context": "Database connection pool exhausted",
  "include_logs": true,
  "include_metrics": true
}
```

### AI Recovery Suggestions
```bash
POST /api/self-healing/ai/recovery
{
  "issue": "High CPU on web server",
  "options": ["restart", "scale_up", "optimize"]
}
```

### AI Health Prediction
```bash
GET /api/self-healing/ai/predict
{
  "lookahead_hours": 24,
  "metrics": ["cpu", "memory", "disk", "connections"]
}
```

**Response:**
```json
{
  "prediction": {
    "database": {"risk": "medium", "issue": "Connection pool exhaustion in 6h"},
    "web_server": {"risk": "low", "issue": null},
    "redis": {"risk": "high", "issue": "Memory threshold breach in 2h"}
  },
  "recommendations": [
    "Increase Redis maxmemory",
    "Add database connection pool monitoring"
  ]
}
```

## Dashboard Endpoints

### Dashboard Data
```bash
GET /api/self-healing/dashboard
```

**Response:**
```json
{
  "uptime_24h": 99.95,
  "uptime_7d": 99.9,
  "uptime_30d": 99.8,
  "incidents_24h": 2,
  "auto_recovered": 3,
  "manual_interventions": 0,
  "avg_recovery_time_seconds": 45,
  "health_trend": "improving"
}
```

### Metrics
```bash
GET /api/self-healing/metrics
GET /api/self-healing/metrics?hours=24
```

## API Reference

### Health
```
POST   /api/self-healing/health/global/config
POST   /api/self-healing/health/component/{component}
GET    /api/self-healing/health/status
```

### Auto-Restart
```
POST   /api/self-healing/policies/auto-restart
GET    /api/self-healing/policies/auto-restart/history
```

### Failover
```
POST   /api/self-healing/failover/config
GET    /api/self-healing/failover/status
POST   /api/self-healing/failover/trigger
```

### Diagnosis
```
POST   /api/self-healing/diagnose/trigger
GET    /api/self-healing/diagnose/results/{id}
POST   /api/self-healing/diagnose/schedule
```

### Recovery
```
POST   /api/self-healing/recovery/procedures
POST   /api/self-healing/recovery/execute
GET    /api/self-healing/recovery/history
```

### Alerts
```
POST   /api/self-healing/alerts/rules
POST   /api/self-healing/alerts/channels
GET    /api/self-healing/alerts/history
```

### Schedule
```
POST   /api/self-healing/schedule
GET    /api/self-healing/schedules
POST   /api/self-healing/schedules/{id}/enable
POST   /api/self-healing/schedules/{id}/disable
DELETE /api/self-healing/schedules/{id}
```

### AI
```
POST   /api/self-healing/ai/diagnose
POST   /api/self-healing/ai/recovery
GET    /api/self-healing/ai/predict
```

### Dashboard
```
GET    /api/self-healing/dashboard
GET    /api/self-healing/metrics
```

## Workflows

### Configure Self-Healing
```bash
# 1. Set up health checks
curl -X POST http://localhost:8000/api/self-healing/health/global/config \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "interval_seconds": 30}'

# 2. Configure auto-restart
curl -X POST http://localhost:8000/api/self-healing/policies/auto-restart \
  -H "Content-Type: application/json" \
  -d '{"service": "flask_backend", "enabled": true}'

# 3. Set up alerts
curl -X POST http://localhost:8000/api/self-healing/alerts/rules \
  -H "Content-Type: application/json" \
  -d '{"name": "Critical Alert", "severity": "critical", "actions": [{"type": "notify", "channel": "slack"}]}'

# 4. Enable AI diagnosis
curl -X POST http://localhost:8000/api/self-healing/ai/diagnose \
  -H "Content-Type: application/json" \
  -d '{"context": "Check system health"}'
```

### Scheduled Recovery
```bash
# Create daily diagnosis schedule
curl -X POST http://localhost:8000/api/self-healing/schedule \
  -H "Content-Type: application/json" \
  -d '{"name": "Daily Check", "type": "cron", "cron": "0 3 * * *", "actions": [{"type": "diagnose", "scope": "all"}]}'
```

## Best Practices

1. **Start with health checks** — Establish baseline before auto-recovery
2. **Set appropriate thresholds** — Avoid unnecessary restarts
3. **Use cooldown periods** — Prevent restart loops
4. **Enable notifications** — Stay informed of issues
5. **Test recovery procedures** — Validate before production
6. **Monitor AI predictions** — Proactive issue prevention
7. **Document procedures** — Clear runbooks for manual intervention
8. **Review logs regularly** — Learn from incidents

## Troubleshooting

### Recovery Not Triggering
```bash
# Check health status
curl http://localhost:8000/api/self-healing/health/status

# Check policy
curl http://localhost:8000/api/self-healing/policies/auto-restart
```

### Restart Loop Detected
```bash
# Check restart history
curl http://localhost:8000/api/self-healing/policies/auto-restart/history

# Disable auto-restart temporarily
curl -X POST http://localhost:8000/api/self-healing/policies/auto-restart \
  -d '{"service": "flask_backend", "enabled": false}'
```

### Diagnosis Failing
```bash
# Check diagnosis status
curl http://localhost:8000/api/self-healing/diagnose/results/{id}

# Trigger manual diagnosis
curl -X POST http://localhost:8000/api/self-healing/diagnose/trigger \
  -d '{"scope": "all", "depth": "full"}'
```
