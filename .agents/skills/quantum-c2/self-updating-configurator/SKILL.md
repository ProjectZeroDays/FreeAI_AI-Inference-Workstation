---
name: quantum-c2-self-updating-configurator
description: >
  Quantum C2 self-updating configurator skill. Use when the user asks about self-updating, auto-update, or version management. Triggers on: "self-updating", "auto-update", "version management", "update channel", "update schedule", "rollback", "changelog", "dependency management".
---

# Quantum C2 Self-Updating Configurator

Configure automated updates and version management for Quantum C2.

## Update Channel Configuration

### Available Channels
```bash
GET /api/self-updating/channels
```

**Response:**
```json
{
  "channels": [
    {"id": "stable", "name": "Stable", "description": "Production-ready releases", "current_version": "2.5.0"},
    {"id": "beta", "name": "Beta", "description": "Pre-release testing", "current_version": "2.6.0-beta.3"},
    {"id": "nightly", "name": "Nightly", "description": "Daily development builds", "current_version": "2.7.0-nightly.20240115"}
  ]
}
```

### Set Update Channel
```bash
POST /api/self-updating/channel
{
  "channel": "stable"
}
```

### Get Current Channel
```bash
GET /api/self-updating/channel
```

## Update Scheduling

### Configure Schedule
```bash
POST /api/self-updating/schedule
{
  "enabled": true,
  "type": "cron",
  "cron": "0 3 * * *",
  "timezone": "UTC",
  "window_start": "02:00",
  "window_end": "06:00"
}
```

### Schedule Types
```bash
# Daily at 3 AM
POST /api/self-updating/schedule
{"type": "cron", "cron": "0 3 * * *"}

# Weekly on Sunday
POST /api/self-updating/schedule
{"type": "cron", "cron": "0 3 * * 0"}

# Monthly on 1st
POST /api/self-updating/schedule
{"type": "cron", "cron": "0 3 1 * *"}

# Manual only
POST /api/self-updating/schedule
{"type": "manual"}
```

### Get Schedule
```bash
GET /api/self-updating/schedule
```

## Update Validation

### Pre-Update Validation
```bash
POST /api/self-updating/validate/pre
{
  "version": "2.6.0"
}
```

**Response:**
```json
{
  "valid": true,
  "checks": [
    {"name": "dependency_compatibility", "status": "pass"},
    {"name": "database_schema", "status": "pass"},
    {"name": "config_compatibility", "status": "warning", "message": "New config keys added"},
    {"name": "breaking_changes", "status": "pass"}
  ],
  "warnings": ["New config key: ai.model.fallback.enabled"],
  "requires_manual_action": false
}
```

### Post-Update Validation
```bash
POST /api/self-updating/validate/post
```

## Rollback Procedures

### Current Version Info
```bash
GET /api/self-updating/version/current
```

**Response:**
```json
{
  "version": "2.5.0",
  "build": "20240110",
  "channel": "stable",
  "installed_at": "2024-01-10T03:00:00Z",
  "commit_hash": "abc1234def5678"
}
```

### Rollback to Previous Version
```bash
POST /api/self-updating/rollback
{
  "target_version": "2.4.0",
  "dry_run": false
}
```

### Rollback History
```bash
GET /api/self-updating/rollback/history
```

**Response:**
```json
{
  "rollbacks": [
    {
      "from_version": "2.5.0",
      "to_version": "2.4.0",
      "reason": "Critical bug in 2.5.0",
      "timestamp": "2024-01-12T08:00:00Z",
      "initiated_by": "auto"
    }
  ]
}
```

### Create Backup Before Update
```bash
POST /api/self-updating/backup/create
{
  "name": "Pre-update backup 2.5.0",
  "include_config": true,
  "include_database": true,
  "include_data": true
}
```

### Get Backups
```bash
GET /api/self-updating/backup/list
```

## Changelog Management

### Get Changelog
```bash
GET /api/self-updating/changelog
GET /api/self-updating/changelog?from_version=2.4.0
GET /api/self-updating/changelog?to_version=2.6.0
```

**Response:**
```json
{
  "version": "2.6.0",
  "release_date": "2024-01-15",
  "changes": {
    "features": [
      "Added AI agent orchestration",
      "New compliance reporting module",
      "Enhanced network scanning"
    ],
    "fixes": [
      "Fixed WebSocket reconnection bug",
      "Fixed database connection leak",
      "Fixed permission check in admin panel"
    ],
    "breaking": [],
    "security": [
      "Updated dependencies to patch CVE-2024-1234",
      "Hardened API authentication"
    ]
  }
}
```

### Subscribe to Changelog
```bash
POST /api/self-updating/changelog/subscribe
{
  "channel": "email",
  "recipients": ["admin@example.com"]
}
```

## Version Tracking

### Version History
```bash
GET /api/self-updating/version/history
```

**Response:**
```json
{
  "versions": [
    {"version": "2.6.0", "date": "2024-01-15", "channel": "beta", "status": "current"},
    {"version": "2.5.0", "date": "2024-01-10", "channel": "stable", "status": "installed"},
    {"version": "2.4.0", "date": "2023-12-15", "channel": "stable", "status": "rolled_back"}
  ]
}
```

### Check for Updates
```bash
POST /api/self-updating/check
{
  "channel": "stable"
}
```

**Response:**
```json
{
  "current_version": "2.5.0",
  "available_version": "2.6.0",
  "update_available": true,
  "channel": "stable",
  "requires_manual_update": false,
  "estimated_update_time_seconds": 300
}
```

## Dependency Management

### Current Dependencies
```bash
GET /api/self-updating/dependencies
```

### Check Dependency Updates
```bash
POST /api/self-updating/dependencies/check
```

### Update Dependencies
```bash
POST /api/self-updating/dependencies/update
{
  "scope": "security",
  "dry_run": false
}
```

## CI/CD Integration

### Webhook Configuration
```bash
POST /api/self-updating/webhook
{
  "url": "https://ci.example.com/webhook",
  "events": ["update_available", "update_started", "update_completed", "rollback_triggered"],
  "secret": "webhook_secret_123"
}
```

### CI Pipeline Trigger
```bash
POST /api/self-updating/ci/trigger
{
  "pipeline": "test_and_deploy",
  "version": "2.6.0"
}
```

### Build Status
```bash
GET /api/self-updating/ci/builds
GET /api/self-updating/ci/builds/{build_id}
```

### Deployment Status
```bash
GET /api/self-updating/deploy/status
GET /api/self-updating/deploy/history
```

## Update Policies

### Configure Policy
```bash
POST /api/self-updating/policy
{
  "auto_update": true,
  "auto_rollback": true,
  "max_concurrent_updates": 1,
  "maintenance_window": {
    "start": "02:00",
    "end": "06:00",
    "timezone": "UTC"
  },
  "notification": {
    "before_update": true,
    "after_update": true,
    "on_rollback": true,
    "channels": ["email", "slack"]
  },
  "approval": {
    "required": false,
    "approvers": ["admin1", "admin2"],
    "timeout_hours": 24
  }
}
```

### Get Policy
```bash
GET /api/self-updating/policy
```

## Update Logs

### Update Logs
```bash
GET /api/self-updating/logs
GET /api/self-updating/logs?level=info
GET /api/self-updating/logs?level=error
```

**Response:**
```json
{
  "logs": [
    {"timestamp": "2024-01-15T03:00:00Z", "level": "info", "message": "Starting update to 2.6.0"},
    {"timestamp": "2024-01-15T03:02:00Z", "level": "info", "message": "Downloading update package"},
    {"timestamp": "2024-01-15T03:03:00Z", "level": "info", "message": "Validating update"},
    {"timestamp": "2024-01-15T03:04:00Z", "level": "info", "message": "Applying update"},
    {"timestamp": "2024-01-15T03:05:00Z", "level": "info", "message": "Update completed successfully"}
  ]
}
```

## API Reference

### Channel
```
GET    /api/self-updating/channels
POST   /api/self-updating/channel
```

### Schedule
```
POST   /api/self-updating/schedule
GET    /api/self-updating/schedule
```

### Validation
```
POST   /api/self-updating/validate/pre
POST   /api/self-updating/validate/post
```

### Rollback
```
GET    /api/self-updating/version/current
POST   /api/self-updating/rollback
GET    /api/self-updating/rollback/history
POST   /api/self-updating/backup/create
GET    /api/self-updating/backup/list
```

### Changelog
```
GET    /api/self-updating/changelog
POST   /api/self-updating/changelog/subscribe
```

### Version
```
GET    /api/self-updating/version/history
POST   /api/self-updating/check
```

### Dependencies
```
GET    /api/self-updating/dependencies
POST   /api/self-updating/dependencies/check
POST   /api/self-updating/dependencies/update
```

### CI/CD
```
POST   /api/self-updating/webhook
POST   /api/self-updating/ci/trigger
GET    /api/self-updating/ci/builds
GET    /api/self-updating/deploy/status
GET    /api/self-updating/deploy/history
```

### Policy
```
POST   /api/self-updating/policy
GET    /api/self-updating/policy
```

### Logs
```
GET    /api/self-updating/logs
```

## Workflows

### Configure Auto-Updates
```bash
# 1. Set channel
curl -X POST http://localhost:8000/api/self-updating/channel \
  -H "Content-Type: application/json" \
  -d '{"channel": "stable"}'

# 2. Configure schedule
curl -X POST http://localhost:8000/api/self-updating/schedule \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "type": "cron", "cron": "0 3 * * *"}'

# 3. Set policy
curl -X POST http://localhost:8000/api/self-updating/policy \
  -H "Content-Type: application/json" \
  -d '{"auto_update": true, "auto_rollback": true}'
```

### Manual Update
```bash
# 1. Check for updates
curl -X POST http://localhost:8000/api/self-updating/check \
  -H "Content-Type: application/json" \
  -d '{"channel": "stable"}'

# 2. Validate pre-update
curl -X POST http://localhost:8000/api/self-updating/validate/pre \
  -H "Content-Type: application/json" \
  -d '{"version": "2.6.0"}'

# 3. Create backup
curl -X POST http://localhost:8000/api/self-updating/backup/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Pre-2.6.0 update"}'

# 4. Apply update
curl -X POST http://localhost:8000/api/self-updating/update/apply \
  -H "Content-Type: application/json" \
  -d '{"version": "2.6.0"}'

# 5. Validate post-update
curl -X POST http://localhost:8000/api/self-updating/validate/post
```

## Best Practices

1. **Use stable channel** — For production environments
2. **Schedule during maintenance** — Avoid peak hours
3. **Always backup first** — Create rollback point
4. **Test before production** — Use beta channel first
5. **Monitor update logs** — Track issues
6. **Enable auto-rollback** — Automatic recovery
7. **Notify stakeholders** — Keep team informed
8. **Review changelog** — Understand changes

## Troubleshooting

### Update Failing
```bash
# Check logs
curl http://localhost:8000/api/self-updating/logs

# Check validation
curl -X POST http://localhost:8000/api/self-updating/validate/pre \
  -H "Content-Type: application/json" \
  -d '{"version": "2.6.0"}'
```

### Rollback Needed
```bash
# Check current version
curl http://localhost:8000/api/self-updating/version/current

# List backups
curl http://localhost:8000/api/self-updating/backup/list

# Rollback
curl -X POST http://localhost:8000/api/self-updating/rollback \
  -H "Content-Type: application/json" \
  -d '{"target_version": "2.5.0"}'
```

### Stuck in Update
```bash
# Check update status
curl http://localhost:8000/api/self-updating/update/status

# Force cancel
curl -X POST http://localhost:8000/api/self-updating/update/cancel
```
