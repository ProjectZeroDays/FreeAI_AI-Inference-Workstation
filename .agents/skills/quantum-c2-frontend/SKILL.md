---
name: quantum-c2-frontend
description: >
  Frontend dashboard management for Quantum C2. Covers dashboard navigation, web card configuration, settings management, and RBAC visibility controls. Use when the user needs to navigate the React dashboard, configure web cards, manage UI settings, or adjust role-based visibility. Triggers on: "frontend", "dashboard", "web card", "UI settings", "dashboard navigation", "configure cards", "RBAC visibility", "frontend config", "dashboard layout".
---

# Quantum C2 Frontend Management

Manage the React dashboard interface including navigation, web cards, settings, and RBAC visibility.

## Overview

The Quantum C2 frontend is a React 18 + Vite application running on port 3000. It provides a tactical dashboard for all C2 operations with role-based access controls.

| Aspect | Detail |
|--------|--------|
| **Framework** | React 18 + Vite |
| **Port** | 3000 |
| **URL** | http://localhost:3000 |
| **Build** | `cd frontend && npm run build` |
| **Dev Server** | `cd frontend && npm run dev` |
| **Source** | `frontend/src/` |

## Dashboard Navigation

### Page Structure

| Page | Route | Clearance | Description |
|------|-------|-----------|-------------|
| Dashboard | `/` | L1+ | Overview metrics and status |
| Sessions | `/sessions` | L3+ | C2 session management |
| Reconnaissance | `/recon` | L2+ | Network and domain scanning |
| Exploitation | `/exploits` | L3+ | Exploit catalog and deployment |
| Post-Ex | `/postex` | L4+ | Post-exploitation toolkit |
| Agents | `/agents` | L4+ | AI agent team orchestration |
| Deception | `/deception` | L4+ | Honeypots, honeytokens, triggers |
| Devices | `/devices` | L3+ | Device control and monitoring |
| Vault | `/vault` | L3+ | Credential management |
| Infrastructure | `/infrastructure` | L5+ | TOR bridges, packet dispersal |
| Ubiquity | `/ubiquity` | L3+ | Message forging, document fuzzing |
| Reports | `/reports` | L1+ | Analytics and audit logs |
| Settings | `/settings` | L5+ | System configuration |
| Forced Entry | `/forced-entry` | L4+ | Full lifecycle operations |
| Listeners | `/listeners` | L3+ | C2 channel management |

### Navigation API

```bash
# Get available pages for current user
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/frontend/navigation

# Response (filtered by RBAC):
{
  "user_clearance": "L3",
  "pages": [
    {"id": "dashboard", "path": "/", "label": "Dashboard", "visible": true},
    {"id": "sessions", "path": "/sessions", "label": "Sessions", "visible": true},
    {"id": "recon", "path": "/recon", "label": "Reconnaissance", "visible": true},
    {"id": "exploits", "path": "/exploits", "label": "Exploitation", "visible": true},
    {"id": "postex", "path": "/postex", "label": "Post-Ex", "visible": false},
    {"id": "agents", "path": "/agents", "label": "Agents", "visible": false},
    {"id": "infrastructure", "path": "/infrastructure", "label": "Infrastructure", "visible": false}
  ]
}
```

## Web Card Configuration

### Card Types

| Card Type | Description | Data Source |
|-----------|-------------|-------------|
| `metric` | Single KPI display | `/api/dashboard/metrics` |
| `chart` | Time-series visualization | `/api/telemetry/` |
| `table` | Data table with sorting/filtering | Various API endpoints |
| `status` | Component health indicator | `/api/health` |
| `alert` | Active alerts display | `/api/alerts/` |
| `session_list` | Active C2 sessions | `/api/sessions/` |
| `bridge_pool` | TOR bridge status | `/api/infrastructure/tor/bridges` |
| `agent_status` | AI agent team status | `/api/agents/teams` |

### Card Configuration API

```bash
# Get current card layout
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/frontend/cards

# Configure card
curl -X PUT http://localhost:8000/api/frontend/cards/{card_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Active Sessions",
    "type": "session_list",
    "refresh_interval_seconds": 10,
    "visible": true,
    "position": {"row": 1, "col": 1, "width": 6, "height": 4},
    "filters": {"status": "active"},
    "columns": ["id", "target", "os", "user", "last_seen"]
  }'
```

### Dashboard Layouts

| Layout | Description | Best For |
|--------|-------------|----------|
| `operations` | Session-focused, real-time | Active C2 operations |
| `recon` | Scan results, vulnerability data | Reconnaissance phase |
| `infrastructure` | Bridge pool, dispersal, nodes | Infrastructure management |
| `analytics` | Charts, trends, reports | Post-operation analysis |
| `minimal` | Essential metrics only | Low-bandwidth environments |

```bash
# Switch dashboard layout
curl -X POST http://localhost:8000/api/frontend/layout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"layout": "operations"}'

# Save custom layout
curl -X POST http://localhost:8000/api/frontend/layout/save \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom Layout",
    "cards": [...],
    "is_default": false
  }'
```

## Settings Management

### System Settings

```bash
# Get current settings
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/settings/

# Update settings
curl -X PUT http://localhost:8000/api/settings/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "frontend": {
      "theme": "dark",
      "refresh_interval_seconds": 15,
      "websocket_enabled": true,
      "notifications_enabled": true,
      "compact_mode": false,
      "high_contrast": false
    },
    "backend": {
      "max_sessions": 1000,
      "session_timeout_minutes": 60,
      "log_level": "INFO",
      "audit_enabled": true
    },
    "security": {
      "token_expiry_hours": 24,
      "max_login_attempts": 5,
      "lockout_duration_minutes": 30,
      "require_2fa": false
    }
  }'
```

### UI Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `theme` | string | `"dark"` | UI theme: dark, light, tactical |
| `refresh_interval_seconds` | number | 15 | Dashboard auto-refresh rate |
| `websocket_enabled` | boolean | true | Real-time updates via WebSocket |
| `notifications_enabled` | boolean | true | Browser notification alerts |
| `compact_mode` | boolean | false | Reduced spacing for more data |
| `high_contrast` | boolean | false | SCIF-compatible high contrast |
| `language` | string | `"en"` | UI language |
| `timezone` | string | `"UTC"` | Timestamp display timezone |

### Theme Configuration

```bash
# Update theme
curl -X PUT http://localhost:8000/api/settings/theme \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "tactical",
    "custom_colors": {
      "bg_primary": "#0a0a0a",
      "bg_secondary": "#1a1a1a",
      "accent": "#00ff88",
      "text_primary": "#e0e0e0"
    }
  }'
```

### Available Themes

| Theme | Description | Use Case |
|-------|-------------|----------|
| `dark` | Dark background, standard contrast | Default operations |
| `light` | Light background, standard contrast | Office environments |
| `tactical` | High contrast, muted colors | Field operations, low light |
| `high_contrast` | Maximum contrast, accessibility | SCIF environments, accessibility |

## RBAC Visibility Controls

### Clearance-Based Page Access

| Clearance | Visible Pages |
|-----------|--------------|
| **L1 — Observer** | Dashboard, Reports, Audit Logs |
| **L2 — Analyst** | L1 + Reconnaissance, Vulnerabilities |
| **L3 — Operator** | L2 + Sessions, Exploitation, Devices, Vault, Listeners, Ubiquity |
| **L4 — Commander** | L3 + Post-Ex, Agents, Deception, Forced Entry |
| **L5 — Architect** | All pages + Infrastructure, Settings |

### Visibility API

```bash
# Get visibility matrix
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/frontend/visibility

# Response:
{
  "user_clearance": "L3",
  "pages": {
    "dashboard": {"visible": true, "read_only": false},
    "sessions": {"visible": true, "read_only": false},
    "recon": {"visible": true, "read_only": false},
    "exploits": {"visible": true, "read_only": false},
    "postex": {"visible": false, "read_only": false},
    "agents": {"visible": false, "read_only": false},
    "infrastructure": {"visible": false, "read_only": false},
    "settings": {"visible": false, "read_only": false}
  },
  "features": {
    "execute_commands": true,
    "generate_payloads": true,
    "manage_bridges": false,
    "configure_system": false,
    "manage_users": false
  }
}
```

### Feature-Level Controls

Beyond page visibility, individual features are gated:

| Feature | Minimum Clearance |
|---------|------------------|
| View dashboard | L1 |
| Run scans | L2 |
| Execute commands on sessions | L3 |
| Generate payloads | L3 |
| Deploy exploits | L3 |
| Privilege escalation | L4 |
| Manage agent teams | L4 |
| Deploy deception assets | L4 |
| Manage TOR bridges | L5 |
| Configure system settings | L5 |
| Manage users and roles | L5 |

### Override Visibility (L5 Only)

```bash
# Temporarily grant L4 access to L3 user
curl -X POST http://localhost:8000/api/frontend/visibility/override \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-abc123",
    "temporary_clearance": "L4",
    "duration_minutes": 60,
    "reason": "Emergency operation"
  }'
```

## WebSocket Real-Time Updates

### Connection

```javascript
// Frontend WebSocket connection
const ws = new WebSocket('ws://localhost:8000/api/ws/dashboard');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case 'session_update':
      updateSessionList(data.sessions);
      break;
    case 'alert':
      showNotification(data.alert);
      break;
    case 'telemetry':
      updateCharts(data.metrics);
      break;
    case 'bridge_status':
      updateBridgePool(data.bridges);
      break;
  }
};
```

### WebSocket Events

| Event | Data | Frequency |
|-------|------|-----------|
| `session_update` | Active sessions list | On change |
| `alert` | New alert notification | On event |
| `telemetry` | System metrics | Every 5s |
| `bridge_status` | TOR bridge health | Every 30s |
| `dispersal_progress` | Shard delivery progress | On change |
| `agent_status` | Agent team updates | On change |

## Responsive Design

### Breakpoints

| Mode | Width | Layout |
|------|-------|--------|
| `minimal` | < 640px | Single column, essential cards only |
| `tablet` | 640-1023px | Two columns, compact cards |
| `full` | >= 1024px | Full layout, all cards |

### Tactical Mode

For low-bandwidth or field deployments:

```bash
# Enable tactical mode
curl -X POST http://localhost:8000/api/frontend/tactical-mode \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "disable_animations": true,
    "reduce_refresh_rate": true,
    "minimal_cards_only": true
  }'
```

## Operational Playbook

### 1. Configure Operations Dashboard
```
1. Set layout to "operations"
2. Add session_list card (top-left, large)
3. Add metric cards for active sessions, listeners, alerts
4. Set refresh interval to 5 seconds
5. Enable WebSocket for real-time updates
6. Save as custom layout
```

### 2. Set Up Infrastructure Monitoring
```
1. Switch to "infrastructure" layout
2. Add bridge_pool card showing all TOR bridges
3. Add dispersal session tracker
4. Add node health status cards
5. Configure alerts for degraded bridges
6. Set high refresh rate (10s)
```

### 3. Configure for Field Operations
```
1. Enable tactical mode
2. Switch to "minimal" layout
3. Enable high contrast theme
4. Disable animations
5. Reduce refresh rate to 30s
6. Show only essential metric cards
```

### 4. Manage User Access
```
1. Check current visibility matrix
2. Adjust user clearance levels as needed
3. Use temporary overrides for time-limited access
4. Verify correct pages are visible/hidden
5. Audit access changes in audit log
```

## References
- `quantum-c2-v6-operator` — Master operator guide with API reference
- `quantum-c2-infra` — Infrastructure management (TOR, dispersal)
- `frontend/src/pages/` — All React page components
- `frontend/src/components/` — Shared UI components
- `frontend/src/hooks/useWebSocket.ts` — WebSocket connection hook
