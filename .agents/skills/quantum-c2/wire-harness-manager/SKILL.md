---
name: quantum-c2-wire-harness-manager
description: >
  Quantum C2 wire harness management skill. Use when the user asks about wire harnesses, agency configurations, agency-specific setups, or government operator configurations. Triggers on: "wire harness", "agency config", "NSA", "CIA", "DIA", "FBI", "DHS", "DOJ", "military config", "government operator", "agency-specific setup".
---

# Quantum C2 Wire Harness Manager

Manage agency-specific wire harness configurations for all 17 supported agencies.

## Agency Wire Harnesses

### Military Agencies
| Agency | Harness ID | Focus Area |
|--------|------------|------------|
| **NSA** | `nsa_wire_harness` | Signals intelligence, cyber operations |
| **DIA** | `dia_wire_harness` | Defense intelligence, target analysis |
| **Army** | `army_wire_harness` | Army Cyber Command, tactical operations |
| **Navy** | `navy_wire_harness` | Naval Network Warfare, fleet operations |
| **Air Force** | `airforce_wire_harness` | Air Force Cyber, space operations |
| **Space Force** | `spaceforce_wire_harness` | Space domain awareness, satellite ops |
| **Marines** | `marines_wire_harness` | Marine Corps Cyberspace Operations |
| **Coast Guard** | `coastguard_wire_harness` | Maritime security, port operations |

### Civilian Agencies
| Agency | Harness ID | Focus Area |
|--------|------------|------------|
| **CIA** | `cia_wire_harness` | Covert operations, human intel |
| **FBI** | `fbi_wire_harness` | Counterintelligence, domestic ops |
| **DHS** | `dhs_wire_harness` | Border security, critical infrastructure |
| **DOJ** | `doj_wire_harness` | Federal prosecution, legal ops |
| **DOE** | `doe_wire_harness` | Energy security, nuclear facilities |
| **Treasury** | `treasury_wire_harness` | Financial crimes, sanctions |
| **EPA** | `epa_wire_harness` | Environmental enforcement |
| **VA** | `va_wire_harness` | Veterans affairs, personnel |
| **State Dept** | `state_wire_harness` | Diplomatic security, embassies |

## Wire Harness Structure

### Harness Object Model
```json
{
  "id": "nsa_wire_harness",
  "agency": "NSA",
  "version": "2.1.0",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:00:00Z",
  "name": "NSA Cyber Operations Harness",
  "description": "Full-spectrum cyber operations configuration for NSA",
  "tool_access": {
    "allowed": ["recon", "exploit", "postex", "intel", "ai_agent", "deception"],
    "blocked": [],
    "require_approval": ["botnet", "rootkit", "forced_entry"]
  },
  "network_config": {
    "allowed_ranges": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
    "blocked_ranges": ["0.0.0.0/0"],
    "tor_routing": true,
    "dns_over_https": true,
    "encryption_standard": "AES-256-GCM",
    "max_beacon_interval": 60,
    "min_beacon_interval": 15
  },
  "operator_config": {
    "max_sessions": 50,
    "session_timeout": 3600,
    "require_multifactor": true,
    "audit_level": "maximum",
    "data_retention_days": 365
  },
  "compliance": {
    "framework": "DI19-003",
    "certification_required": true,
    "approval_workflow": "multi_level",
    "legal_review": true
  },
  "ai_config": {
    "default_model": "claude-sonnet-4-20250514",
    "fallback_chain": ["claude-sonnet", "claude-opus", "gpt-4o", "ollama"],
    "max_tokens": 4096,
    "temperature": 0.3
  }
}
```

## API Endpoints

### List Harnesses
```bash
GET /api/admin/harnesses
```

**Response:**
```json
{
  "harnesses": [
    {
      "id": "nsa_wire_harness",
      "agency": "NSA",
      "version": "2.1.0",
      "status": "active",
      "operators_count": 12,
      "last_updated": "2024-01-20T14:00:00Z"
    }
  ],
  "total": 17
}
```

### Get Harness Details
```bash
GET /api/admin/harnesses/{harness_id}
```

### Create Custom Harness
```bash
POST /api/admin/harnesses
{
  "agency": "CUSTOM",
  "name": "Custom Operations Harness",
  "description": "Custom harness for specialized operations",
  "tool_access": {
    "allowed": ["recon", "exploit"],
    "blocked": ["botnet", "rootkit"]
  },
  "network_config": {
    "allowed_ranges": ["10.0.0.0/8"],
    "tor_routing": true
  }
}
```

### Update Harness
```bash
PUT /api/admin/harnesses/{harness_id}
```

### Delete Harness
```bash
DELETE /api/admin/harnesses/{harness_id}
```

### Validate Harness
```bash
POST /api/admin/harnesses/validate
{
  "harness": {
    "agency": "CUSTOM",
    "tool_access": {
      "allowed": ["invalid_tool"],
      "blocked": ["recon"]
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
      "field": "tool_access.allowed",
      "value": "invalid_tool",
      "message": "Tool not in allowed catalog"
    }
  ],
  "warnings": []
}
```

### Export Harness
```bash
GET /api/admin/harnesses/{harness_id}/export?format=json
GET /api/admin/harnesses/{harness_id}/export?format=yaml
GET /api/admin/harnesses/{harness_id}/export?format=pdf
```

**JSON Export:**
```json
{
  "export_format": "json",
  "harness": { ... },
  "exported_at": "2024-01-15T10:30:00Z",
  "signature": "sha256:abc123..."
}
```

### Import Harness
```bash
POST /api/admin/harnesses/import
{
  "format": "json",
  "harness": { ... },
  "mode": "create|update|merge"
}
```

### Compare Harnesses
```bash
POST /api/admin/harnesses/compare
{
  "harness_ids": ["nsa_wire_harness", "cia_wire_harness"],
  "fields": ["tool_access", "network_config", "compliance"]
}
```

**Response:**
```json
{
  "differences": [
    {
      "field": "tool_access.allowed",
      "nsa_wire_harness": ["recon", "exploit", "botnet"],
      "cia_wire_harness": ["recon", "exploit", "intel"]
    },
    {
      "field": "compliance.framework",
      "nsa_wire_harness": "DI19-003",
      "cia_wire_harness": "ICA-6"
    }
  ],
  "similarities": ["network_config.tor_routing", "operator_config.max_sessions"]
}
```

### Agency-Specific Harnesses

#### NSA Harness
```bash
GET /api/admin/harnesses/nsa_wire_harness
```
**Key Features:**
- Full cyber operations toolkit
- Maximum AI agent integration
- Multi-level approval workflow
- DI-19-003 compliance framework
- Advanced deception tools enabled

#### CIA Harness
```bash
GET /api/admin/harnesses/cia_wire_harness
```
**Key Features:**
- Covert operations focus
- Human intelligence integration
- Deep cover persistence mechanisms
- ICA-6 compliance framework
- OpSec maximized

#### DIA Harness
```bash
GET /api/admin/harnesses/dia_wire_harness
```
**Key Features:**
- Defense intelligence focus
- Target analysis tools
- Open-source intelligence integration
- Multi-source analysis pipelines
- DIU compliance framework

#### FBI Harness
```bash
GET /api/admin/harnesses/fbi_wire_harness
```
**Key Features:**
- Counterintelligence focus
- Domestic operations compliance
- Joint Terrorism Task Force integration
- Attorney General approval workflow
- CJIS compliance framework

#### DHS Harness
```bash
GET /api/admin/harnesses/dhs_wire_harness
```
**Key Features:**
- Critical infrastructure protection
- Border security integration
- CISA coordination
- ICS/SCADA tool access
- NIST CSF compliance framework

## Agency Tool Access Matrix

| Tool | NSA | CIA | DIA | FBI | DHS | DOJ | Army | Navy | AF | Space | Marines | CG | DOE | Treasury | EPA | VA | State |
|------|-----|-----|-----|-----|-----|-----|------|------|----|-------|---------|----|-----|----------|-----|-----|-------|
| recon | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| exploit | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | no | yes | yes |
| postex | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | no | yes | yes |
| botnet | yes | yes | yes | no | no | no | yes | yes | yes | yes | yes | no | yes | no | no | no | no |
| rootkit | yes | yes | yes | no | no | no | yes | yes | yes | yes | yes | no | yes | no | no | no | no |
| intel | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| ai_agent | yes | yes | yes | no | no | no | yes | yes | yes | yes | yes | no | no | no | no | no | no |
| deception | yes | yes | yes | no | no | no | yes | yes | yes | yes | yes | no | no | no | no | no | no |
| compliance | no | no | no | yes | yes | yes | no | no | no | no | no | no | no | no | no | no | yes |

## Harness Versioning

### List Versions
```bash
GET /api/admin/harnesses/{harness_id}/versions
```

### Create New Version
```bash
POST /api/admin/harnesses/{harness_id}/versions
{
  "version": "3.0.0",
  "changes": "Added support for AI agent orchestration",
  "updated_by": "admin"
}
```

### Rollback to Version
```bash
POST /api/admin/harnesses/{harness_id}/rollback
{
  "version": "2.1.0"
}
```

### Version Diff
```bash
GET /api/admin/harnesses/{harness_id}/versions/{v1}/diff/{v2}
```

## Operational Workflows

### Deploy Agency Harness
```bash
# 1. Select agency harness
curl http://localhost:8000/api/admin/harnesses/nsa_wire_harness

# 2. Validate for current environment
curl -X POST http://localhost:8000/api/admin/harnesses/validate \
  -H "Content-Type: application/json" \
  -d '{"harness_id": "nsa_wire_harness"}'

# 3. Assign to operators
curl -X POST http://localhost:8000/api/admin/harnesses/nsa_wire_harness/assign \
  -H "Content-Type: application/json" \
  -d '{"operator_ids": ["op-123", "op-456"]}'

# 4. Verify deployment
curl http://localhost:8000/api/admin/harnesses/nsa_wire_harness/deployment-status
```

### Create Custom Agency Harness
```bash
# 1. Start from template
curl -X POST http://localhost:8000/api/admin/harnesses/template \
  -H "Content-Type: application/json" \
  -d '{"agency": "CUSTOM", "base": "fbi_wire_harness"}'

# 2. Customize
curl -X PUT http://localhost:8000/api/admin/harnesses/custom_001 \
  -H "Content-Type: application/json" \
  -d '{"tool_access": {"allowed": ["recon", "postex"], "blocked": ["exploit"]}}'

# 3. Validate
curl -X POST http://localhost:8000/api/admin/harnesses/validate \
  -H "Content-Type: application/json" \
  -d '{"harness_id": "custom_001"}'
```

## Best Practices

1. **Use agency-specific harnesses** — Leverage pre-configured settings
2. **Validate before deploying** — Always run validation
3. **Version control** — Track all changes
4. **Export regularly** — Maintain backup exports
5. **Compare before modifying** — Use comparison tool
6. **Review compliance** — Ensure framework alignment
7. **Limit custom changes** — Modify only what is necessary
8. **Test in staging** — Validate in isolated environment

## Troubleshooting

### Harness Not Applying
```bash
# Check assignment status
curl http://localhost:8000/api/admin/harnesses/{id}/assignment-status

# Check for conflicts
curl http://localhost:8000/api/admin/harnesses/{id}/conflicts
```

### Validation Failing
```bash
# Get detailed errors
curl -X POST http://localhost:8000/api/admin/harnesses/validate \
  -H "Content-Type: application/json" \
  -d '{"harness_id": "custom_001"}'
```

### Cross-Agency Comparison
```bash
# Compare all military agencies
curl -X POST http://localhost:8000/api/admin/harnesses/compare \
  -H "Content-Type: application/json" \
  -d '{"harness_ids": ["army_wire_harness", "navy_wire_harness", "airforce_wire_harness"]}'
```
