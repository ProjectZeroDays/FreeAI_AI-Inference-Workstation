# Enhancement Plan & Recommendations

Status legend: ✅ implemented · 🔜 planned (with approach sketched) ·
🕐 future/needs-infrastructure.

## 1. Reliability & data safety

| Item | Status | Notes |
|---|---|---|
| Config/registry/manifest backups w/ retention | ✅ | `scripts/backup.sh` (+ `restore` mode), weekly `tokugawa-backup.timer` |
| Daily log rotation + workspace pruning | ✅ | `scripts/cleanup.sh`, `tokugawa-cleanup.timer` |
| Model-download disk preflight | ✅ | aborts before filling the models SSD |
| Port-collision preflight at `start.sh` | ✅ | fails fast with clear message (`ALLOW_PORT_REUSE=1` overrides) |
| Off-site backup sync (rclone → S3/B2) | 🔜 | wrap `backup.sh` output: `rclone copy backups/ remote:tokugawa-backups` after tar; add `BACKUP_REMOTE` env |
| Restore drill in CI | 🕐 | needs a disposable runner with the stack |

## 2. Live dashboard / control plane

| Item | Status | Notes |
|---|---|---|
| Presets (4 recommended + custom CRUD) | ✅ | `/api/presets*` |
| Timed idle window w/ auto-restore | ✅ | optimizer lifecycle, survives restarts |
| Settings change push to all dashboards | ✅ | SSE `/api/events` (version-bumped), Tokugawa UI follows on next phase |
| Router live metrics on dashboard | ✅ | `/api/status` embeds router `/metrics` |
| Model shelf (registry vs disk) | ✅ | `/api/models-status`: present/missing + free disk |
| Security headers | ✅ | nosniff / frame-deny / referrer-policy |
| Auth on dashboard write endpoints | 🔜 | require `X-API-Key` (reuse ROUTER_API_KEY) for POST routes when set; GET stays open on LAN |
| WebSocket bi-directional agent feed | 🕐 | flask-sock; SSE covers 90% today |

## 3. Inference coherence (already shipped)

`--jinja`, Q6_K-only downloader + quant sanity check, server-side
repeat-penalty guards, degenerate-output detection with automatic
fallback retry, `install.sh --update-llama`.

## 4. Agent workflow enhancements

| Item | Status | Notes |
|---|---|---|
| SDLC concurrency cap (GPU thrash guard) | ✅ | `max_concurrent_runs`, enforced per request |
| Prompt-template library for agents | 🔜 | `agents/templates/*.md` loaded by api.py; dashboard picker writes `template_id` into requests |
| Run artifacts index page in dashboard | 🔜 | reuse autonomous `/auto/runs`; render table + artifact links |
| Multi-agent code review gate (two-model review) | 🔜 | reviewer step already exists; add second pass via different model key from registry |

## 5. Ops tooling

| Item | Status | Notes |
|---|---|---|
| Makefile (test/lint/up/down/backup/update) | ✅ | single entry point |
| CLI presets/settings commands | ✅ | `tokugawa.py presets/preset/settings` |
| GitHub Pages docs publish (MkDocs) | 🔜 | `.github/workflows/docs-pages.yml`: `mkdocs gh-deploy` on main |
| Image size diet (slim llama build stage) | 🔜 | multi-stage Dockerfile: devel→runtime copy of `llama-server` only |
| Prometheus exporter endpoint | 🕐 | translate `/metrics` JSON to text format |

## 6. Future (unchanged)

Function calling/tool use, RAG + vector DB, repo-wide auto-refactor of
existing trees, multi-GPU tensor parallelism, model registry UI,
Kubernetes GitOps (Argo), secrets vault integration.
