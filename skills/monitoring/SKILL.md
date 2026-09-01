---
name: monitoring
description: System monitoring and health checks for Quantum C2. Use when checking service health, reviewing logs, diagnosing performance issues, or setting up alerts. Triggers on "health check", "monitor", "system status", "check logs", "performance", "uptime", "diagnostics", "service health".
---

# Monitoring (Defensive)

System health checks, log review, and performance diagnostics.

## Quick Health Check

```bash
# Python backend status
curl -s http://localhost:8000/health 2>/dev/null || echo "Backend not running"

# Process check
tasklist /FI "IMAGENAME eq python.exe" 2>/dev/null | head -5

# Port check
netstat -ano | findstr :8000
```

## Log Locations

| Log | Path | Purpose |
|-----|------|---------|
| Application | `logs/quantum.log` | App-level events |
| Access | `logs/access.log` | HTTP requests |
| Error | `logs/error.log` | Exception tracebacks |
| Security | `logs/security.log` | Auth events, RBAC |

## Reading Logs

```bash
# Last 50 lines
tail -50 logs/quantum.log

# Filter errors
grep -i "error\|exception\|traceback" logs/quantum.log | tail -20

# Filter by time range
grep "2026-08-18" logs/quantum.log | head -30

# Security events
grep -i "auth\|login\|rbac\|clearance" logs/security.log | tail -20
```

## Performance Check

```bash
# Python process memory/CPU
python -c "
import psutil
for p in psutil.process_iter(['pid','name','memory_percent','cpu_percent']):
    if 'python' in p.info['name'].lower():
        print(f\"PID {p.info['pid']}: {p.info['memory_percent']:.1f}% mem, {p.info['cpu_percent']:.1f}% cpu\")
"

# Disk usage
python -c "
import shutil
total, used, free = shutil.disk_usage('/')
print(f'Disk: {used/(2**30):.1f}GB used / {total/(2**30):.1f}GB total ({used/total*100:.0f}%)')
"

# Database size
ls -lh test.db 2>/dev/null || echo "No local DB"
```

## Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU | >70% | >90% |
| Memory | >75% | >90% |
| Disk | >80% | >95% |
| Response time | >500ms | >2000ms |
| Error rate | >1% | >5% |

## Diagnostic Workflow

1. **Check** — Run health endpoint
2. **Review** — Read recent logs for errors
3. **Measure** — Check resource usage
4. **Isolate** — Identify failing component
5. **Report** — Document findings and fix

## Service Status Template

```
## Service Health Report

**Time:** YYYY-MM-DD HH:MM:SS
**Uptime:** Xh Xm

| Service | Status | Response | Notes |
|---------|--------|----------|-------|
| Backend API | OK | 45ms | — |
| Database | OK | 12ms | — |
| Frontend | OK | Static | — |

**Resources:** CPU X% | Memory X% | Disk X%
**Errors (last 24h):** X
```
