# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| `main` (latest) | ✔ |
| tagged `v1.2.x` | ✔ |
| older tags | ✖ |

## Reporting a Vulnerability

**Do not open a public issue.**

- **Preferred:** GitHub → Security → Report a vulnerability (private advisory) on this repo
- **Fallback:** Email `security@freeai.local` with subject `[FreeAI Security]`

Include: affected version/commit, reproduction steps, impact, and any logs. We aim to acknowledge within 72h and ship a fix with a coordinated disclosure.

## Scope

- Router auth (`X-API-Key` / `ROUTER_API_KEY`), rate limiting, and provider key handling
- Agent API auth (`X-API-Key` / `AGENT_API_KEY`) for red/blue/purple team operations
- Autonomous API auth (`X-API-Key` / `AUTONOMOUS_API_KEY`) for run creation and shell operations
- SDLC sandbox (`workspaces/<run_id>/` traversal guards, `ENABLE_SHELL_TOOLS` gating)
- Supply chain: Docker images (`ghcr.io/.../freeai-*`), Live ISO build (`live/build-live.sh`)

## Hardening

The default install enables UFW (22/8030/8050), `fail2ban` (sshd), and `unattended-upgrades`. For internet-exposed hosts:

1. **Always set authentication keys:**
   - `ROUTER_API_KEY` for router access
   - `AGENT_API_KEY` for agent API (especially red/blue/purple team operations)
   - `AUTONOMOUS_API_KEY` for autonomous SDLC API (required when `ENABLE_SHELL_TOOLS=1`)
   - `DASHBOARD_AUTH_TOKEN` for dashboard write operations

2. **Network isolation:**
   - Use `ENABLE_DESKTOP_PORTS=1` only behind TailScale/Cloudflare
   - Keep router (:8010) and llama.cpp (:9001) on localhost/tailnet only
   - Expose only dashboard (:8030) and autonomous (:8050) to the internet when necessary

3. **Shell tools:**
   - Only enable `ENABLE_SHELL_TOOLS=1` when necessary
   - Always set `AUTONOMOUS_API_KEY` when shell tools are enabled
   - Monitor `/auto/runs` endpoint for suspicious activity

See [AUTONOMOUS_SECURITY.md](AUTONOMOUS_SECURITY.md) for detailed autonomous API security configuration.

## Past Advisories

- `sk-or-v1` placeholder keys in skill docs were redacted in `6004c83` (push-protection). Rotate any key you may have pasted from docs.
