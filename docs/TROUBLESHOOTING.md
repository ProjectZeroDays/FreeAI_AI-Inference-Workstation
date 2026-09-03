# Troubleshooting Guide

Common errors, log locations, health checks, and debug procedures.

---

## Symptom Quick-Reference

| Symptom | Likely Cause | Fix |
|---|---|---|
| **GPU not detected** | Missing NVIDIA driver or CUDA toolkit | `nvidia-smi` — if missing, `sudo apt install nvidia-driver-570-server` |
| **CUDA OOM (out of memory)** | Model too large for VRAM | Reduce `N_GPU_LAYERS` or use a smaller model; set `LLAMA_CTX=32768` |
| **Port 8010 already in use** | Another process holding the port | `lsof -i :8010` to find it; override with `ROUTER_PORT=8110` |
| **Router 502 Bad Gateway** | llama.cpp backend is down | `curl localhost:9001/health` — check `logs/llama.log` for model load errors |
| **401 Unauthorized from Router** | Missing or wrong API key | Set `ROUTER_API_KEY` env var; include `X-API-Key` header in requests |
| **429 Rate Limited** | Token bucket exhausted | Increase `RATE_LIMIT_CAPACITY` in config; restart router |
| **Model download stalls** | Network interruption | Re-run `bash models/auto-download-models.sh` — it resumes with `wget -c` |
| **Model download disk full** | Insufficient free space | Set `MODEL_DIR=/data/models` to redirect; preflight requires +10 GB |
| **llama-server not found** | Binary not built | Re-run `./install.sh` to build llama.cpp; ensure `nvcc` for CUDA build |
| **CUDA build skipped** | `nvcc` not on PATH | Install NVIDIA CUDA Toolkit; verify with `nvcc --version` |
| **Cache returning stale answers** | LRU cache not invalidated | `freeai stop && freeai start`; or set `cache_enabled: false` in config |
| **Workflow step fails 3x** | Agent error or bad prompt | Check `logs/workflow-audit.jsonl` for failure details |
| **Dashboard shows GPU as zeros** | nvidia-smi not visible in container | Ensure `--gpus all` flag; verify NVIDIA Container Toolkit |
| **Settings not applying** | Router reads settings at startup | Run `freeai stop && freeai start` after config changes |
| **SOPS decryption fails** | Missing age key | Set `SOPS_AGE_KEY_FILE`; regenerate with `age-keygen -o age.key` |
| **Docker healthcheck fails** | Service not ready yet | `docker compose logs --tail=50 <service>`; retry after 30s |
| **No GPU detected in Docker** | Missing NVIDIA runtime | `docker run --gpus all --rm nvidia/cuda:12.0-base nvidia-smi` |
| **ISO build fails** | Missing build tools | Install `xorriso`, `isolinux`, `genisoimage`; need 4GB+ RAM |
| **Agent API 502** | Router supervisor down | `systemctl status freeai-supervisor`; check `logs/agents.log` |
| **Idle window never restores** | Resource optimizer down | `systemctl status resource-optimizer`; check `ps aux | grep resource_optimizer` |

---

## Log Locations

| Log File | Content |
|---|---|
| `logs/router.log` | Router requests, cache hits/misses, fallback chains, errors |
| `logs/llama.log` | llama.cpp server output, model loading, GPU memory |
| `logs/agents.log` | Agent API requests, profile usage, session memory ops |
| `logs/workflow-audit.jsonl` | Workflow step events (started/ok/retry/failed with workflow_id) |
| `logs/dashboard.log` | Dashboard requests, GPU telemetry errors |
| `logs/autonomous.log` | Autonomous SDLC phase transitions, workspace ops |
| `dashboard.err.log` | Dashboard Python tracebacks |

Tail logs in real-time:
```bash
# CLI log viewer
freeai logs router -n 50
freeai logs llama
freeai logs all   # tail all logs

# Manual tail
tail -f logs/router.log logs/llama.log
```

---

## Health Check Commands

### Quick Status

```bash
freeai status
```

Expected output:
```
Router      :8010  ✓ healthy
Agent API   :8020  ✓ healthy
Dashboard   :8030  ✓ healthy
Workflow    :8040  ✓ healthy
llama.cpp   :9001  ✓ healthy
═══════════════════════════
ALL_SYSTEMS_OPERATIONAL
```

### Manual Endpoint Checks

```bash
# Router health
curl -s http://localhost:8010/health | jq .

# Router models
curl -s http://localhost:8010/models | jq '.models[].status'

# Agent API
curl -s http://localhost:8020/profiles | jq .

# Dashboard
curl -s http://localhost:8030/api/status | jq .

# llama.cpp
curl -s http://localhost:9001/health | jq .
```

### Smoke Test

```bash
./scripts/smoke-test.sh
```

Runs an 11-endpoint live sweep + inference round-trip. Reports `ALL_SYSTEMS_OPERATIONAL` on success.

---

## Common Errors and Fixes

### `llama-server not found`

The llama.cpp binary was not built or is not on PATH.

```bash
# Re-run installer (builds llama.cpp with CUDA if nvcc present)
./install.sh

# Verify binary exists
ls llama.cpp/build/bin/llama-server
```

### CUDA Build Skipped

`nvcc` not found during install. Install the NVIDIA CUDA Toolkit:

```bash
# Ubuntu/Debian
sudo apt install nvidia-cuda-toolkit

# Verify
nvcc --version
```

Then re-run: `./install.sh`

### Model Download Stalls

The downloader uses `wget -c` for resumable downloads. If stuck:

```bash
# Check disk space
df -h models/

# Re-run — it resumes automatically
bash models/auto-download-models.sh
```

### Router 502 Bad Gateway

All backends are unhealthy. Check llama.cpp logs:

```bash
cat logs/llama.log | tail -50
curl -s http://localhost:9001/health
```

Common causes:
- Model file missing or corrupted — re-download
- GPU OOM — reduce `N_GPU_LAYERS` or use a smaller model
- Port conflict — check `lsof -i :9001`

### 401 Unauthorized from Router

`ROUTER_API_KEY` is set but the client is not sending it:

```bash
# Verify key is set
echo $ROUTER_API_KEY

# Include in requests
curl -H "X-API-Key: $ROUTER_API_KEY" http://localhost:8010/route \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test"}'
```

### 429 Rate Limited

Token bucket is empty. Increase limits in `config/config.json`:

```json
{
  "router": {
    "rate_limit_capacity": 200,
    "rate_limit_refill_per_min": 200
  }
}
```

Then restart the router:
```bash
freeai stop && freeai start
```

### Cache Returning Stale Answers

```bash
# Option 1: Restart router (clears in-memory cache)
freeai stop && freeai start

# Option 2: Disable cache temporarily
# In config.json:
# "router": { "cache_enabled": false }
```

### Workflow Step Fails 3x

Check the audit log for the failing step:

```bash
grep "failed" logs/workflow-audit.jsonl | tail -20
grep "<workflow_id>" logs/workflow-audit.jsonl
```

### Agent API 502

Router is down; the supervisor should restore it within 10 seconds. Check:

```bash
# Supervisor status
systemctl status freeai-supervisor

# Agent API directly
curl -s http://localhost:8020/profiles
```

### Dashboard Shows Zeros for GPU

`nvidia-smi` is missing or not visible in the container:

```bash
# Verify nvidia-smi works
nvidia-smi

# In Docker, ensure NVIDIA Container Toolkit is installed
# and the container has --gpus all
docker run --gpus all -it nvidia/cuda:12.0-base nvidia-smi
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8010    # Router
lsof -i :8020    # Agents
lsof -i :9001    # llama

# Override ports via environment
ROUTER_PORT=8110 ./start.sh

# Or force reuse
ALLOW_PORT_REUSE=1 ./start.sh
```

### Settings Changed But Router Unchanged

The router reads settings at **process start**. Changes to `runtime-settings.json` take effect after a restart:

```bash
freeai stop && freeai start
```

### Idle Window Never Restores

The resource optimizer may be down:

```bash
systemctl status resource-optimizer
# or
ps aux | grep resource_optimizer
```

State lives in `config/runtime-settings.json` — check that `settings.idle.restore` is populated after applying a timed idle preset.

### Model Download Aborts: Disk Full

The preflight check requires model size + 10GB free. Clear space or redirect:

```bash
# Point MODEL_DIR elsewhere
MODEL_DIR=/data/models bash models/auto-download-models.sh
```

### GPU Warmup Fails

```bash
# Run warmup manually with verbose output
docker compose --profile warmup up
# or
bash agents/gpu-warmup.sh
```

---

## Debug Mode

### Router Debug

```bash
# Enable verbose logging
ROUTER_LOG_LEVEL=debug python3 router/router.py

# Test classification without full pipeline
python3 -c "
from router.classifier import classify_task
print(classify_task('Write a Python function'))
"
```

### Agent Debug

```bash
# Enable agent API debug logging
AGENT_LOG_LEVEL=debug python3 agents/api.py

# Test a specific agent profile
curl -X POST http://localhost:8020/agent/debug \
  -H "Content-Type: application/json" \
  -d '{"code":"print(1/0)","error":"ZeroDivisionError","profile":"strict"}'
```

### Autonomous SDLC Debug

```bash
# Run with verbose output
ENABLE_SHELL_TOOLS=1 python3 autonomous/agent.py --debug

# Check workspace state
ls workspaces/<run_id>/

# View phase transitions
cat logs/autonomous.log | grep "<run_id>"
```

### Browser Engine Debug

```bash
# Check army status
curl -s http://localhost:8030/api/browser/status | jq .

# View browser logs
tail -f logs/browser.log

# Reset to defaults
curl -X GET http://localhost:8030/api/browser/reset
```

### Docker Debug

```bash
# View service logs
docker compose logs -f router
docker compose logs -f llama

# Enter a running container
docker exec -it llama_cpp bash

# Check container health
docker compose ps
docker inspect --format='{{.State.Health.Status}}' llama_cpp
```

### Kubernetes Debug

```bash
# Check pod status
kubectl get pods -n freeai
kubectl describe pod <pod-name> -n freeai

# View logs
kubectl logs -n freeai -f deployment/router

# Port-forward for local testing
kubectl port-forward -n freeai svc/router 8010:8010
```

---

## Drift Report

After installation, check for configuration drift:

```bash
./install.sh --check
```

Reports on:
- Systemd units status
- Bound ports
- llama.cpp binary presence
- Python dependency versions
- Model file integrity

Expected: `CONVERGED`. If `DRIFT` is reported, review the output for missing components.

---

## Log Rotation

Logs are managed by the daily cleanup timer. To rotate manually:

```bash
# Compress old logs
gzip -k logs/*.log
# or
./scripts/backup.sh --rotate
```

---

## Getting Help

1. Check `freeai status` and include output in any issue
2. Collect relevant log tails: `logs/router.log`, `logs/llama.log`
3. Run `freeai.py --help` for CLI options
4. Review `docs/TROUBLESHOOTING.md` for your specific symptom
5. For GPU issues, include `nvidia-smi` output
