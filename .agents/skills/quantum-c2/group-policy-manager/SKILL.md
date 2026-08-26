---
name: quantum-c2-group-policy-manager
description: >
  Quantum C2 group policy management skill. Use when the user asks about group policies, policy management, compliance configuration, operator access controls, or wire harness management. Triggers on: "group policy", "policy", "compliance configuration", "access control", "operator policy", "allowed tools", "blocked tools", "policy validation", "RBAC", "wire harness", "agency configuration".
---

# Quantum C2 Group Policy Manager

Manage operator access controls, group policies, and compliance configurations across Quantum C2.

## Policy Structure

### Policy Object Model
```json
{
  "id": "pol-abc123",
  "name": "Operator Policy Template",
  "description": "Default policy for standard operators",
  "operator_type": "operator",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "allowed_tools": ["recon", "exploit", "postex"],
  "blocked_tools": ["botnet", "rootkit"],
  "network_config": {
    "allowed_ranges": ["192.168.0.0/16", "10.0.0.0/8"],
    "blocked_ranges": ["0.0.0.0/0"],
    "dns_over_https": false,
    "tor_routing": false
  },
  "compliance": {
    "require_approval": true,
    "max_session_duration": 3600,
    "log_level": "verbose",
    "data_retention_days": 90,
    "encryption_required": true
  },
  "audit": {
    "enabled": true,
    "log_all_commands": true,
    "screenshot_capture": false
  }
}
```

### Operator Types
| Type | Description | Default Tool Access |
|------|-------------|---------------------|
| `operator` | Standard field operator | recon, exploit, postex |
| `analyst` | Intelligence analyst | recon, intel, reports |
| `admin` | System administrator | all tools |
| `compliance_officer` | Compliance reviewer | audit, reports, policies |
| `ai_agent` | AI agent operator | workflow, automation |
| `wire_harness` | Agency-specific operator | agency-configured tools |

## Policy Management

### List Policies
```bash
GET /api/admin/policies
```

**Response:**
```json
{
  "policies": [
    {
      "id": "pol-abc123",
      "name": "Standard Operator",
      "operator_type": "operator",
      "status": "active",
      "assigned_operators": 12,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### Create Policy
```bash
POST /api/admin/policies
```

**Request Body:**
```json
{
  "name": "Custom Operator Policy",
  "description": "Policy for custom operator role",
  "operator_type": "operator",
  "allowed_tools": ["recon", "exploit", "postex", "intel"],
  "blocked_tools": ["botnet", "rootkit"],
  "network_config": {
    "allowed_ranges": ["192.168.0.0/16"],
    "blocked_ranges": ["10.0.0.0/8"],
    "dns_over_https": true,
    "tor_routing": true
  },
  "compliance": {
    "require_approval": false,
    "max_session_duration": 7200,
    "log_level": "standard",
    "data_retention_days": 30,
    "encryption_required": true
  }
}
```

### Update Policy
```bash
PUT /api/admin/policies/{id}
```

**Request Body:** Same as create, all fields optional.

### Delete Policy
```bash
DELETE /api/admin/policies/{id}
```

**Response:**
```json
{
  "deleted": true,
  "policy_id": "pol-abc123",
  "affected_operators": 5
}
```

### Validate Policy
```bash
POST /api/admin/policies/validate
```

**Request Body:**
```json
{
  "policy": {
    "name": "Test Policy",
    "allowed_tools": ["recon", "invalid_tool"],
    "network_config": {
      "allowed_ranges": ["invalid_cidr"]
    }
  }
}
```

**Response:**
```json
{
  "valid": false,
  "errors": [
    {
      "field": "allowed_tools",
      "value": "invalid_tool",
      "message": "Tool not found in allowed list"
    },
    {
      "field": "network_config.allowed_ranges",
      "value": "invalid_cidr",
      "message": "Invalid CIDR notation"
    }
  ],
  "warnings": [
    {
      "field": "compliance.max_session_duration",
      "message": "Session duration exceeds recommended maximum (86400s)"
    }
  ]
}
```

### Preview Policy Application
```bash
GET /api/admin/policies/{id}/apply
```

**Response:**
```json
{
  "policy_id": "pol-abc123",
  "effective_permissions": {
    "tools": {
      "recon": true,
      "exploit": true,
      "postex": true,
      "botnet": false,
      "rootkit": false
    },
    "network": {
      "allowed_ranges": ["192.168.0.0/16"],
      "blocked_ranges": ["10.0.0.0/8"]
    }
  },
  "compliance_requirements": [
    "Session duration: 3600s max",
    "All commands logged",
    "Encryption required"
  ],
  "audit_trail": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "action": "created",
      "operator": "admin"
    }
  ]
}
```

## Per-Operator-Type Templates

### Standard Operator Template
```bash
POST /api/admin/policies/template
{
  "operator_type": "operator"
}
```

### Administrator Template
```bash
POST /api/admin/policies/template
{
  "operator_type": "admin"
}
```

### Analyst Template
```bash
POST /api/admin/policies/template
{
  "operator_type": "analyst"
}
```

### Compliance Officer Template
```bash
POST /api/admin/policies/template
{
  "operator_type": "compliance_officer"
}
```

## RBAC Integration

### Map Policy to Role
```bash
POST /api/admin/policies/{id}/roles
{
  "role": "operator_team_alpha"
}
```

### Assign Operator to Policy
```bash
POST /api/admin/operators/{operator_id}/policy
{
  "policy_id": "pol-abc123"
}
```

### Get Operator Effective Policy
```bash
GET /api/admin/operators/{operator_id}/effective-policy
```

## Policy Export/Import

### Export Policy
```bash
GET /api/admin/policies/{id}/export
```

**Response:**
```json
{
  "format": "json",
  "exported_at": "2024-01-15T10:30:00Z",
  "policy": { ... }
}
```

### Import Policy
```bash
POST /api/admin/policies/import
{
  "policy": { ... },
  "mode": "create|update|merge"
}
```

### Export All Policies
```bash
GET /api/admin/policies/export
```

### Import Bulk Policies
```bash
POST /api/admin/policies/bulk-import
{
  "policies": [{ ... }, { ... }],
  "mode": "create|update|merge"
}
```

## Policy Synchronization

### Sync Across Operator Groups
```bash
POST /api/admin/policies/sync
{
  "policy_id": "pol-abc123",
  "target_groups": ["team_alpha", "team_bravo", "team_charlie"]
}
```

### Check Sync Status
```bash
GET /api/admin/policies/{id}/sync-status
```

**Response:**
```json
{
  "policy_id": "pol-abc123",
  "synced_groups": ["team_alpha"],
  "pending_sync": ["team_bravo", "team_charlie"],
  "last_sync": "2024-01-15T10:30:00Z"
}
```

### Sync All Active Policies
```bash
POST /api/admin/policies/sync-all
```

## Compliance Checking

### Check Policy Compliance
```bash
GET /api/admin/compliance/check
```

### Generate Compliance Report
```bash
GET /api/admin/compliance/report
{
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  }
}
```

### Violation Alert Configuration
```bash
POST /api/admin/compliance/alerts
{
  "type": "unauthorized_tool_usage",
  "severity": "high",
  "notify": ["admin", "compliance_officer"],
  "action": "log_and_alert"
}
```

## Policy Hierarchy

### Policy Precedence
1. **System-level policy** — Applies to all operators
2. **Group-level policy** — Applies to operator group
3. **Individual-level policy** — Applies to specific operator
4. **Wire harness policy** — Agency-specific overrides

### Conflict Resolution
```bash
GET /api/admin/policies/conflicts
```

**Response:**
```json
{
  "conflicts": [
    {
      "operator_id": "op-123",
      "policy_level": "individual",
      "field": "allowed_tools",
      "conflicting_value": ["botnet"],
      "group_policy_value": ["recon", "exploit"],
      "resolution": "individual_overrides_group"
    }
  ]
}
```

## Version Control

### List Policy Versions
```bash
GET /api/admin/policies/{id}/versions
```

### Rollback to Version
```bash
POST /api/admin/policies/{id}/rollback
{
  "version": "v2"
}
```

## Workflows

### Create Policy from Template
```bash
# 1. List available templates
curl http://localhost:8000/api/admin/policies/templates

# 2. Create from operator template
curl -X POST http://localhost:8000/api/admin/policies/template \
  -H "Content-Type: application/json" \
  -d '{"operator_type": "operator"}'

# 3. Validate the policy
curl -X POST http://localhost:8000/api/admin/policies/validate \
  -H "Content-Type: application/json" \
  -d '{"policy": {"name": "My Policy", "allowed_tools": ["recon", "exploit"], "operator_type": "operator"}}'

# 4. Create the policy
curl -X POST http://localhost:8000/api/admin/policies \
  -H "Content-Type: application/json" \
  -d '{"name": "My Policy", "operator_type": "operator", "allowed_tools": ["recon", "exploit"]}'

# 5. Assign to operators
curl -X POST http://localhost:8000/api/admin/policies/{id}/assign \
  -H "Content-Type: application/json" \
  -d '{"operator_ids": ["op-123", "op-456"]}'
```

### Sync Policy to Teams
```bash
# 1. Sync to specific groups
curl -X POST http://localhost:8000/api/admin/policies/{id}/sync \
  -H "Content-Type: application/json" \
  -d '{"target_groups": ["team_alpha", "team_bravo"]}'

# 2. Check sync status
curl http://localhost:8000/api/admin/policies/{id}/sync-status
```

## Best Practices

1. **Start with templates** — Use built-in templates as base
2. **Validate before applying** — Always run validate endpoint
3. **Use least privilege** — Default deny, grant explicitly
4. **Document policy changes** — Include description and rationale
5. **Review compliance regularly** — Schedule periodic audits
6. **Version control** — Keep policy versions for rollback
7. **Test in staging** — Validate effects before production
8. **Sync after updates** — Ensure all groups get updates

## Troubleshooting

### Policy Not Applied
```bash
# Check effective policy
curl http://localhost:8000/api/admin/operators/{id}/effective-policy

# Check for conflicts
curl http://localhost:8000/api/admin/policies/conflicts
```

### Validation Failing
```bash
# Get detailed validation errors
curl -X POST http://localhost:8000/api/admin/policies/validate \
  -H "Content-Type: application/json" \
  -d '{"policy": {...}}'
```

### Sync Not Working
```bash
# Check sync status
curl http://localhost:8000/api/admin/policies/{id}/sync-status

# Force sync
curl -X POST http://localhost:8000/api/admin/policies/{id}/sync \
  -H "Content-Type: application/json" \
  -d '{"target_groups": ["team_alpha"]}'
```
