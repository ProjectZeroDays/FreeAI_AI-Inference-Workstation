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

- Router auth (`X-API-Key` / `AGENT_API_KEY`), rate limiting, and provider key handling
- SDLC sandbox (`workspaces/<run_id>/` traversal guards, `ENABLE_SHELL_TOOLS` gating)
- Supply chain: Docker images (`ghcr.io/.../freeai-*`), Live ISO build (`live/build-live.sh`)

## Hardening

The default install enables UFW (22/8030/8050), `fail2ban` (sshd), and `unattended-upgrades`. For internet-exposed hosts, use `ENABLE_DESKTOP_PORTS=1` only behind TailScale/Cloudflare, and set `AGENT_API_KEY` + `DASHBOARD_AUTH_TOKEN`.

## Past Advisories

- `sk-or-v1` placeholder keys in skill docs were redacted in `6004c83` (push-protection). Rotate any key you may have pasted from docs.
