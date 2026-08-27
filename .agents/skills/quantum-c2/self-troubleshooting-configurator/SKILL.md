---
name: quantum-c2-self-troubleshooting-configurator
description: >
  Quantum C2 self-troubleshooting configurator skill. Use when the user asks about troubleshooting, diagnostics, or issue resolution. Triggers on: "troubleshooting", "diagnostics", "issue resolution", "error diagnosis", "log analysis", "system health", "auto-diagnosis", "escalation".
---

# Quantum C2 Self-Troubleshooting Configurator

Automated diagnostics, log analysis, and issue resolution for Quantum C2.

## Diagnostic Collection

### System Diagnostics
```bash
POST /api/troubleshoot/diagnostics/system
{
  "scope": "full",
  "components": ["cpu", "memory", "disk", "network", "database", "redis"]
}
```

**Response:**
```json
{
  "diagnostic_id": "diag-001",
  "timestamp": "2024-01-15T10:30:00Z",
  "system": {
    "cpu": {"usage_percent": 45, "load_avg": [1.2, 1.5, 1.8]},
    "memory": {"total_gb": 16, "used_gb": 8, "free_gb": 8, "cached_gb": 2},
    "disk": {"total_gb": 500, "used_gb": 200, "free_gb": 300, "iostat": "normal"},
    "network": {"interfaces": ["eth0", "lo"], "errors": 0, "drops": 0}
  }
}
```

### Service Diagnostics
```bash
POST /api/troubleshoot/diagnostics/services
{
  "services": ["flask", "redis", "postgres", "nginx", "websocket"]
}
```

### Application Diagnostics
```bash
POST /api/troubleshoot/diagnostics/application
{
  "scope": "full"
}
```

**Response:**
```json
{
  "sessions": {"active": 45, "idle": 12, "closed": 1200},
  "workers": {"available": 8, "busy": 3, "idle": 5},
  "queue": {"pending": 5, "processing": 2, "failed": 0},
  "errors_24h": 12,
  "performance": {"avg_response_ms": 45, "p99_ms": 250}
}
```

## Log Analysis

### Log Collection
```bash
GET /api/troubleshoot/logs
GET /api/troubleshoot/logs?service=flask
GET /api/troubleshoot/logs?level=error
GET /api/troubleshoot/logs?hours=24
```

### Log Analysis
```bash
POST /api/troubleshoot/logs/analyze
{
  "period": "24h",
  "service": "all",
  "pattern_type": "all"
}
```

**Response:**
```json
{
  "summary": {
    "total_logs": 15420,
    "errors": 45,
    "warnings": 230,
    "info": 15145
  },
  "error_patterns": [
    {
      "pattern": "Connection refused to Redis",
      "count": 12,
      "first_seen": "2024-01-15T08:00:00Z",
      "last_seen": "2024-01-15T10:00:00Z",
      "severity": "high"
    },
    {
      "pattern": "Slow query detected",
      "count": 8,
      "first_seen": "2024-01-15T09:30:00Z",
      "last_seen": "2024-01-15T10:15:00Z",
      "severity": "medium"
    }
  ]
}
```

### Real-time Log Streaming
```bash
# WebSocket for live logs
ws://localhost:8000/api/troubleshoot/logs/stream
```

**WebSocket Message:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "error",
  "service": "flask",
  "message": "Database connection timeout"
}
```

## Error Pattern Detection

### Pattern Analysis
```bash
GET /api/troubleshoot/patterns
GET /api/troubleshoot/patterns?severity=high
GET /api/troubleshoot/patterns?hours=24
```

**Response:**
```json
{
  "patterns": [
    {
      "id": "pat-001",
      "name": "Redis Connection Failure",
      "description": "Redis connections failing intermittently",
      "severity": "high",
      "occurrence_count": 12,
      "first_occurrence": "2024-01-15T08:00:00Z",
      "trend": "increasing",
      "related_errors": ["ECONNREFUSED", "RedisTimeoutError"]
    }
  ]
}
```

### Pattern Resolution
```bash
POST /api/troubleshoot/patterns/{pattern_id}/resolve
{
  "resolution": "Increased Redis connection pool size",
  "action_taken": "config_update"
}
```

## Automated Diagnosis

### Trigger Diagnosis
```bash
POST /api/troubleshoot/diagnose
{
  "issue": "High response times",
  "scope": "full"
}
```

**Response:**
```json
{
  "diagnosis_id": "diag-002",
  "status": "completed",
  "timestamp": "2024-01-15T10:35:00Z",
  "findings": [
    {
      "severity": "high",
      "component": "database",
      "issue": "Slow queries detected",
      "evidence": "Avg query time: 2.5s (threshold: 500ms)",
      "recommendation": "Add indexes to users table"
    },
    {
      "severity": "medium",
      "component": "redis",
      "issue": "Connection pool exhaustion",
      "evidence": "Pool utilization: 95%",
      "recommendation": "Increase max_connections"
    }
  ],
  "confidence": 0.87,
  "suggested_actions": [
    "Run database query optimization",
    "Increase Redis max connections to 200"
  ]
}
```

### AI-Powered Diagnosis
```bash
POST /api/troubleshoot/diagnose/ai
{
  "context": "Web interface is slow after update to 2.6.0",
  "include_logs": true,
  "include_metrics": true,
  "include_changes": true
}
```

**Response:**
```json
{
  "diagnosis_id": "ai-diag-001",
  "ai_summary": "The performance degradation is likely caused by a database query regression introduced in version 2.6.0. The new compliance reporting feature added an unoptimized JOIN operation on the audit_logs table.",
  "root_cause": {
    "component": "database",
    "issue": "Missing index on audit_logs.completed_at",
    "introduced_in": "2.6.0",
    "confidence": 0.92
  },
  "recommended_fix": {
    "sql": "CREATE INDEX idx_audit_logs_completed ON audit_logs(completed_at);",
    "migration": "Run migration 042_add_audit_logs_index"
  },
  "alternative_fixes": [
    {
      "description": "Disable compliance reporting feature",
      "risk": "low",
      "reversibility": "high"
    }
  ]
}
```

## Resolution Recommendations

### Get Recommendations
```bash
GET /api/troubleshoot/recommendations/{issue_id}
```

**Response:**
```json
{
  "issue_id": "issue-001",
  "recommendations": [
    {
      "id": "rec-001",
      "title": "Increase Redis Connection Pool",
      "description": "Current pool size is insufficient for load",
      "severity": "medium",
      "effort": "low",
      "steps": [
        "Edit Redis configuration: max_connections = 200",
        "Restart Redis service",
        "Verify connection pool metrics"
      ],
      "risk": "low",
      "estimated_impact": "Reduce connection timeout errors by 90%"
    },
    {
      "id": "rec-002",
      "title": "Add Database Index",
      "description": "Missing index causing slow queries",
      "severity": "high",
      "effort": "medium",
      "steps": [
        "Run: CREATE INDEX idx_audit_logs_completed ON audit_logs(completed_at)",
        "Monitor query performance",
        "Verify using EXPLAIN ANALYZE"
      ],
      "risk": "medium",
      "estimated_impact": "Reduce query time from 2.5s to 50ms"
    }
  ]
}
```

### Apply Recommendation
```bash
POST /api/troubleshoot/recommendations/{rec_id}/apply
{
  "dry_run": false
}
```

## Manual Intervention Triggers

### Escalation Rules
```bash
POST /api/troubleshoot/escalation/rules
{
  "condition": "diagnosis_confidence < 0.7 AND severity = 'high'",
  "action": "notify_admin",
  "channels": ["email", "slack"]
}
```

### Trigger Manual Review
```bash
POST /api/troubleshoot/escalate
{
  "diagnosis_id": "diag-002",
  "reason": "Low confidence diagnosis",
  "priority": "high"
}
```

### Get Pending Reviews
```bash
GET /api/troubleshoot/escalations/pending
```

## Escalation Procedures

### Escalation History
```bash
GET /api/troubleshoot/escalations
GET /api/troubleshoot/escalations?status=pending
```

**Response:**
```json
{
  "escalations": [
    {
      "id": "esc-001",
      "diagnosis_id": "diag-001",
      "status": "open",
      "severity": "high",
      "created_at": "2024-01-15T10:30:00Z",
      "assigned_to": "admin@example.com",
      "reason": "Database performance degradation",
      "auto_resolution_attempted": true,
      "auto_resolution_failed": true
    }
  ]
}
```

### Acknowledge Escalation
```bash
POST /api/troubleshoot/escalations/{id}/acknowledge
```

### Resolve Escalation
```bash
POST /api/troubleshoot/escalations/{id}/resolve
{
  "resolution": "Added missing database index",
  "notes": "Query performance restored to normal"
}
```

## Knowledge Base Integration

### Knowledge Base Search
```bash
GET /api/troubleshoot/kb/search?q=database+slow+query
```

**Response:**
```json
{
  "results": [
    {
      "id": "kb-001",
      "title": "Database Query Performance Issues",
      "category": "database",
      "severity": "medium",
      "symptoms": ["Slow API responses", "High query times", "Database lock contention"],
      "solutions": [
        {"title": "Add missing indexes", "steps": ["Analyze slow query log", "Create appropriate indexes"]},
        {"title": "Optimize query structure", "steps": ["Review JOIN operations", "Use covering indexes"]}
      ],
      "related_issues": ["issue-001", "issue-045"]
    }
  ]
}
```

### Add Knowledge Entry
```bash
POST /api/troubleshoot/kb
{
  "title": "Redis Connection Pool Exhaustion",
  "category": "redis",
  "symptoms": ["Connection timeout errors", "Redis maxmemory reached"],
  "solution": "Increase max connections or implement connection pooling",
  "applicable_issues": ["issue-002"]
}
```

## Health Dashboard

### Overall Health
```bash
GET /api/troubleshoot/health
```

**Response:**
```json
{
  "status": "degraded",
  "score": 72,
  "issues": 3,
  "critical": 1,
  "warning": 2,
  "resolved_24h": 5,
  "trending": "improving"
}
```

### Component Health
```bash
GET /api/troubleshoot/health/components
```

### Issue Timeline
```bash
GET /api/troubleshoot/issues/timeline?hours=24
```

## API Reference

### Diagnostics
```
POST   /api/troubleshoot/diagnostics/system
POST   /api/troubleshoot/diagnostics/services
POST   /api/troubleshoot/diagnostics/application
```

### Logs
```
GET    /api/troubleshoot/logs
POST   /api/troubleshoot/logs/analyze
```

### Patterns
```
GET    /api/troubleshoot/patterns
POST   /api/troubleshoot/patterns/{id}/resolve
```

### Diagnosis
```
POST   /api/troubleshoot/diagnose
POST   /api/troubleshoot/diagnose/ai
```

### Recommendations
```
GET    /api/troubleshoot/recommendations/{issue_id}
POST   /api/troubleshoot/recommendations/{rec_id}/apply
```

### Escalation
```
POST   /api/troubleshoot/escalation/rules
POST   /api/troubleshoot/escalate
GET    /api/troubleshoot/escalations/pending
GET    /api/troubleshoot/escalations
POST   /api/troubleshoot/escalations/{id}/acknowledge
POST   /api/troubleshoot/escalations/{id}/resolve
```

### Knowledge Base
```
GET    /api/troubleshoot/kb/search
POST   /api/troubleshoot/kb
```

### Health
```
GET    /api/troubleshoot/health
GET    /api/troubleshoot/health/components
GET    /api/troubleshoot/issues/timeline
```

## Workflows

### Automated Troubleshooting
```bash
# 1. Trigger system diagnostics
curl -X POST http://localhost:8000/api/troubleshoot/diagnostics/system \
  -H "Content-Type: application/json" \
  -d '{"scope": "full"}'

# 2. Analyze logs
curl -X POST http://localhost:8000/api/troubleshoot/logs/analyze \
  -H "Content-Type: application/json" \
  -d '{"period": "24h"}'

# 3. Run AI diagnosis
curl -X POST http://localhost:8000/api/troubleshoot/diagnose/ai \
  -H "Content-Type: application/json" \
  -d '{"context": "System slow after update"}'

# 4. Get recommendations
curl http://localhost:8000/api/troubleshoot/recommendations/issue-001

# 5. Apply fix
curl -X POST http://localhost:8000/api/troubleshoot/recommendations/rec-001/apply \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'
```

### Manual Diagnosis
```bash
# 1. Describe the issue
curl -X POST http://localhost:8000/api/troubleshoot/diagnose \
  -H "Content-Type: application/json" \
  -d '{"issue": "Cannot connect to database", "scope": "full"}'

# 2. Search knowledge base
curl "http://localhost:8000/api/troubleshoot/kb/search?q=database+connection+failed"

# 3. Get recommendations
curl http://localhost:8000/api/troubleshoot/recommendations/{issue_id}
```

## Best Practices

1. **Regular diagnostics** — Schedule periodic health checks
2. **Monitor logs** — Set up log analysis alerts
3. **Build knowledge base** — Document solutions
4. **Test fixes first** — Validate in staging
5. **Escalate appropriately** — Know when to involve humans
6. **Track trends** — Monitor for recurring issues
7. **Document everything** — Maintain clear records

## Troubleshooting

### Diagnosis Timing Out
```bash
# Check diagnostic status
curl http://localhost:8000/api/troubleshoot/diagnose/status/{id}

# Reduce scope
curl -X POST http://localhost:8000/api/troubleshoot/diagnose \
  -d '{"scope": "critical", "issue": "high CPU"}'
```

### No Recommendations Found
```bash
# Search knowledge base
curl "http://localhost:8000/api/troubleshoot/kb/search?q=issue+keywords"

# Add knowledge entry
curl -X POST http://localhost:8000/api/troubleshoot/kb \
  -d '{"title": "New Issue", "solution": "Fix steps"}'
```

### Manual Intervention Required
```bash
# Escalate issue
curl -X POST http://localhost:8000/api/troubleshoot/escalate \
  -d '{"diagnosis_id": "diag-001", "reason": "Auto-fix failed"}'
```
