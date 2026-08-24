# Deployment Guide

## Bare metal (Linux + NVIDIA)

```bash
./install.sh                          # deps, venv, builds llama.cpp (CUDA if nvcc present)
bash models/auto-download-models.sh   # 3 GGUF models, resumable
cp .env.example .env                  # optional overrides
./start.sh                            # everything, logs in ./logs/
./validate.sh                         # preflight
```

## Docker Compose

```bash
docker compose up -d --build            # core stack
docker compose --profile vllm up -d     # + vLLM backend
docker compose --profile warmup up -d   # one-shot GPU warmup after healthy
docker compose --profile desktop up -d  # + XFCE/VNC/noVNC
```

## Kubernetes

```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/models-pvc.yml    # provision model storage first
# build & push images (CI does this on tags), then:
kubectl apply -f k8s/llama-deployment.yml \
              -f k8s/vllm-deployment.yml \
              -f k8s/router-deployment.yml \
              -f k8s/agents-deployment.yml \
              -f k8s/workflow-deployment.yml \
              -f k8s/hpa.yml
```

GPU nodes need the `nvidia.com/gpu` device plugin; llama/vLLM pods carry
nodeSelector + tolerations already.

## Environment profiles

| Profile | MOCK_LLM | Notes |
|---|---|---|
| dev | 1 | router returns canned completions; no GPU needed |
| staging | 0 | real backends, relaxed rate limits |
| prod | 0 | set `ROUTER_API_KEY`, tune `RATE_LIMIT_*` |

## Docs site

```bash
pip install mkdocs && mkdocs serve   # renders docs/ via mkdocs.yml
```
