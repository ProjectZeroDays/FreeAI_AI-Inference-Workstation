# Secure Deployment — Production Hardening

Protect your FreeAI deployment with network isolation, authentication, and monitoring.

## Network Security

### Firewall (UFW)

The installer enables UFW by default, exposing only:
- `22` — SSH
- `8030` — Dashboard
- `8050` — Autonomous API

```bash
# Verify rules
sudo ufw status verbose

# Add additional ports if needed
sudo ufw allow 8010/tcp comment "Router"
```

### Router & Model Isolation

By default, router (:8010) and llama.cpp (:9001) bind to `127.0.0.1` only. To expose:

```bash
# In config/config.json
{
  "router": {"host": "0.0.0.0", "port": 8010},
  "llama": {"host": "0.0.0.0", "port": 9001}
}
```

> **Warning:** Only expose behind a VPN, TailScale, or reverse proxy.

## Authentication

Set API keys for each service:

```bash
# .env
ROUTER_API_KEY=your-router-key
AGENT_API_KEY=your-agent-key
AUTONOMOUS_API_KEY=your-autonomous-key
DASHBOARD_AUTH_TOKEN=your-dashboard-token
```

Clients must include the key:
```bash
curl -X POST localhost:8010/route \
  -H "X-API-Key: $ROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello"}'
```

## Dashboard Security Headers

FreeAI sets these headers automatically:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: default-src 'self'`

## Secrets Management

Secrets are encrypted with SOPS:
```bash
# Decrypt
sops --decrypt config/secrets.enc.yaml

# Edit
sops --encrypt --in-place config/secrets.enc.yaml
```

Never commit `.env` or `secrets.enc.yaml` to git.

## TLS Gateway (Optional)

Expose via Caddy with automatic HTTPS:
```bash
docker compose --profile tls up -d
# Dashboard at https://your-host:8443
```

## Audit Logging

All write operations are logged:
```bash
# View audit log
tail -f config/audit.jsonl

# Filter by action
grep '"action":"run"' config/audit.jsonl
```

## Next Steps

- [Troubleshooting](TROUBLESHOOTING.md)
- [Security Policy](../SECURITY.md)
