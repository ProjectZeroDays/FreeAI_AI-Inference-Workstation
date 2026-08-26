# Troubleshooting

| Symptom | Fix |
|---|---|
| `llama-server not found` | run `./install.sh`; binary lands in `llama.cpp/build/bin/` |
| CUDA build skipped | install NVIDIA toolkit so `nvcc` is on PATH, re-run installer |
| Model download stalls | re-run downloader — resumes with `wget -c` |
| Router 502 | all backends unhealthy; check `logs/llama.log`, hit `/health` on :9001 |
| 401 from router | `ROUTER_API_KEY` set — send `X-API-Key` header |
| 429 rate limited | raise `RATE_LIMIT_CAPACITY` / `RATE_LIMIT_REFILL_PER_MIN` |
| Cache returning stale answers | restart router or set `CACHE_ENABLED=false` |
| Workflow step fails 3x | inspect `logs/workflow-audit.jsonl` for the failing agent + error |
| Agent API 502 | router down; supervisor should restore it within 10s |
| Dashboard shows zeros | `nvidia-smi` missing or no GPU visible in the container |
| Port conflicts | override via env: `ROUTER_PORT`, `LLAMA_PORT`, `AGENT_API_PORT`, `WORKFLOW_PORT`, `DASHBOARD_PORT` |

| Port already in use at start | `start.sh` aborts with the busy ports; stop the other stack or `ALLOW_PORT_REUSE=1` |
| Model download aborts: disk | preflight needs size+10GB free; clear space or point MODEL_DIR elsewhere |
| Settings changed but router unchanged | rate-limit/cache/timeout apply on router restart |
| Idle window never restored | optimizer service down? `systemctl status resource-optimizer`; state is in runtime-settings.json |

## Local dev without a GPU

```bash
MOCK_LLM=1 python3 router/router.py   # canned completions
pytest                                # full offline test suite
```
