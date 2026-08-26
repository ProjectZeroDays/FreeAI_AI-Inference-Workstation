# Security -- Advanced (ROADMAP 8)

| Control | How |
|---|---|
| **JWT for agents/workflows** | `agents/api.py` + `workflow/api.py` now accept `Authorization: Bearer <JWT>` (HS256, `JWT_SECRET` env). Router `X-API-Key` still works; JWT is for service-to-service. |
| **TLS termination** | Caddy (`--profile tls`) -- `docker/Caddyfile.public` with ACME (`TOKUGAWA_DOMAIN`/`FREEAI_DOMAIN` + `ACME_EMAIL`). Internal services remain HTTP behind Caddy. |
| **RBAC** | `config/rbac.json` ? `{"admin": ["*"], "operator": ["route","agent/*"], "viewer": ["status","metrics"]}`. Enforced in Flask `before_request`. |
| **Audit logs** | `logs/audit.jsonl` (append-only, JSON per line: who, what, when, result). Rotated by `scripts/cleanup.sh` (keep 14 days). |
| **Network segmentation** | Compose `networks: { frontend, backend }` -- router/agents/workflow on `backend` only; dashboard + Caddy on `frontend`. K8s NetworkPolicy in `k8s/network-policy.yml`. |
