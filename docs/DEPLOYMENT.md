# Deployment Guide

## Local Development Setup

### Prerequisites

- Python 3.10+
- NVIDIA GPU with CUDA 12.x (optional — `MOCK_LLM=1` for CPU-only dev)
- 10GB+ disk space for models
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation

# Run preflight validation
./validate.sh

# Install dependencies, build llama.cpp (CUDA if nvcc present)
./install.sh

# Download models (3 GGUF models, resumable)
bash models/auto-download-models.sh

# Configure environment (optional overrides)
cp .env.example .env
# Edit .env to set API keys, ports, etc.

# Start all services
./start.sh

# Validate installation
./validate.sh
```

### Local Dev Without a GPU

```bash
MOCK_LLM=1 python3 router/router.py    # Canned completions, no GPU needed
python3 agents/api.py                   # Agent API on :8020
python3 workflow/engine.py              # Workflow engine on :8040
python3 run_dashboard.py                # Dashboard on :8030
pytest                                # Full offline test suite
```

### Environment Profiles

| Profile | `MOCK_LLM` | Notes |
|---|---|---|
| `dev` | `1` | Router returns canned completions; no GPU needed |
| `staging` | `0` | Real backends, relaxed rate limits |
| `prod` | `0` | Set `ROUTER_API_KEY`, tune `RATE_LIMIT_*` |

### Configuration

`config/config.json` is the single source of truth. Every value can be overridden by environment variables (see `router/settings.py`).

Key environment variables:
```bash
# Service ports
ROUTER_PORT=8010
AGENT_API_PORT=8020
DASHBOARD_PORT=8030
WORKFLOW_PORT=8040

# Model paths
LLAMA_MODEL_PATH=/path/to/model.gguf
MODEL_DIR=./models

# API keys (never commit these)
ROUTER_API_KEY=your-key-here
DASHBOARD_AUTH_TOKEN=your-token-here
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# GPU config
N_GPU_LAYERS=35              # Layers offloaded to GPU (0-100)
MOCK_LLM=0                   # Set to 1 for CPU-only dev mode
ENABLE_SHELL_TOOLS=0         # Set to 1 for autonomous SDLC shell access
```

---

## Docker Compose Deployment

### Prerequisites

- Docker 24+ with Docker Compose v2
- NVIDIA Container Toolkit installed
- `nvidia-smi` accessible inside containers

### Core Stack

```bash
# Build and start core services
docker compose up -d --build

# Verify all services
docker compose ps
curl -s http://localhost:8010/health
curl -s http://localhost:8030/api/status
```

### Optional Profiles

```bash
# + vLLM high-throughput backend
docker compose --profile vllm up -d

# One-shot GPU warmup (run after services are healthy)
docker compose --profile warmup up -d

# + XFCE desktop with VNC/noVNC access
docker compose --profile desktop up -d

# + Secondary llama.cpp shard on :9003
docker compose --profile llama2 up -d

# + FreeToken edge MoE engine (:9100, 290B+ models)
docker compose --profile freetoken up -d

# + LoLLMs chat UI (:9600)
docker compose --profile lollms up -d

# + Qdrant RAG sidecar (:6333)
docker compose --profile rag up -d

# + Caddy TLS gateway with automatic HTTPS
docker compose --profile tls up -d

# + MCP server for Codex/OpenCode integration (:8090)
docker compose --profile mcp up -d

# All services in one command
docker compose --profile allinone up -d
```

### Model Storage

Models are mounted from the host:
```bash
# Ensure models directory exists
mkdir -p models
# Copy or download GGUF files into models/
```

In Docker Compose, the `./models` volume maps to `/models` inside containers.

### Production Environment

```bash
# Copy and customize environment
cp .env.example .env
# Edit .env with your keys and configuration

# Start with production overrides
docker compose -f docker-compose.yml --env-file .env up -d
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes 1.28+ cluster
- NVIDIA GPU node plugin installed
- `kubectl` configured with cluster access
- PVC provisioner available (for model storage)

### Quick Deploy

```bash
# Create namespace
kubectl apply -f k8s/namespace.yml

# Provision model storage PVC (do this first)
kubectl apply -f k8s/models-pvc.yml

# Deploy services
kubectl apply -f k8s/llama-deployment.yml
kubectl apply -f k8s/vllm-deployment.yml
kubectl apply -f k8s/router-deployment.yml
kubectl apply -f k8s/agents-deployment.yml
kubectl apply -f k8s/workflow-deployment.yml
kubectl apply -f k8s/autonomous-deployment.yml
kubectl apply -f k8s/hpa.yml

# Optional: Istio gateway for traffic management
kubectl apply -f k8s/istio-gateway.yml

# Optional: Network policies
kubectl apply -f k8s/network-policy.yml

# Optional: Sealed secrets for sensitive config
kubectl apply -f k8s/sealed-secrets/
```

### GPU Configuration

GPU nodes require the `nvidia.com/gpu` device plugin. llama/vLLM pods carry nodeSelector and tolerations already:

```yaml
# k8s/llama-deployment.yml excerpt
spec:
  nodeSelector:
    nvidia.com/gpu: "true"
  tolerations:
    - key: "nvidia.com/gpu"
      operator: "Exists"
      effect: "NoSchedule"
```

### Autoscaling

HPA manifests are in `k8s/hpa.yml`. Default configuration:
- Router: 2-8 replicas
- Agents: 1-4 replicas
- Workflow: 1-3 replicas

### Model Persistence

Models are served from a shared PVC (`models-pvc.yml`). Ensure the PVC is bound before deploying:

```bash
kubectl get pvc freeai-models
# Should show STATUS: Bound
```

### Verifying Deployment

```bash
# Check pod health
kubectl get pods -n freeai

# Port-forward for local testing
kubectl port-forward -n freeai svc/router 8010:8010
kubectl port-forward -n freeai svc/dashboard 8030:8030

# Test routing
curl http://localhost:8010/health
curl http://localhost:8030/api/status
```

---

## Vast.ai Template Deployment

### Prerequisites

- Vast.ai account
- GPU instance with 32GB+ VRAM recommended
- Instance IP and SSH access

### Using the Template

1. Create a Vast.ai instance from the FreeAI template
2. The `onstart.sh` script runs automatically on boot
3. Wait ~5 minutes for model download and service startup
4. Access dashboard at `http://<instance-ip>:8030`

### Template Configuration

The Vast.ai kit includes:
- `vastai/template.json` — Instance Portal configuration
- `vastai/onstart.sh` — Automated provisioning script
- Selkies + Guacamole for remote desktop access

### Manual Deployment on Vast.ai

```bash
# SSH into your instance
ssh root@<instance-ip>

# Clone and deploy
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation

# Install (auto-detects GPU)
./install.sh

# Download models
bash models/auto-download-models.sh

# Start services
./start.sh
```

---

## Live ISO Creation

### Overview

The Live ISO ("FreeAIOS") is built by remastering the official Ubuntu 24.04 live-server ISO. It provides three boot options: Install, Live Try, and Rescue.

### Build Prerequisites

```bash
# On an Ubuntu 24.04 host
apt update
apt install -y xorriso isolinux genisoimage
```

### Build the ISO

```bash
cd live
./build-live.sh
```

### Boot Menu Options

1. **Install FreeAI AI Stack** — Unattended Ubuntu install + FreeAI stack
   - Boots Subiquity with `autoinstall ds=nocloud;s=/cdrom/autoinstall`
   - Installs `nvidia-driver-570-server` + SSH
   - Runs `install-stack.sh` (CUDA llama.cpp build, model download, client provisioning)
   - Default login: `freeai/freeai`

2. **Try Ubuntu Server (FreeAI Live)** — Stock live session without installation

3. **Rescue shell** — Live rescue target for troubleshooting

### ISO Output

The built ISO is placed in `live/dist/` and can be written to USB:
```bash
dd if=live/dist/freeaios-amd64.iso of=/dev/sdX bs=4M status=progress
```

---

## Provider-Specific Deployment

### RunPod

```bash
# Deploy from GHCR all-in-one image
podctl create \
  --image ghcr.io/projectzerodays/freeai-allinone:latest \
  --env-file .env \
  --volume /models:/models \
  --gpus all
```

### Lambda Labs / Paperspace

```bash
# Bare Ubuntu with pre-installed NVIDIA drivers
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation
./install-stack.sh
bash models/auto-download-models.sh
./start.sh
```

### AWS / Azure / GCP (Spot Instances)

```bash
# Terraform module (future) — spot VM + cloud-init
# For now, use Lambda Labs path with cloud-init running install-stack.sh
# Key cost guard: enable optimizer eco mode for spot instances
```

---

## Health Verification

After any deployment, verify with:

```bash
# CLI health check
freeai status

# Endpoint sweep
./scripts/smoke-test.sh

# Drift report (bare metal)
./install.sh --check
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

---

## Troubleshooting Deployment

| Issue | Fix |
|---|---|
| CUDA build skipped | Ensure `nvcc` is on PATH; install NVIDIA CUDA Toolkit |
| Port already in use | Set `ALLOW_PORT_REUSE=1` or override with `ROUTER_PORT`, etc. |
| Model download fails | Re-run downloader — it resumes with `wget -c` |
| GPU not visible in container | Verify NVIDIA Container Toolkit: `nvidia-smi` inside container |
| Router 502 on all backends | Check `logs/llama.log`; hit `/health` on :9001 directly |
| Settings not propagating | Router reads settings at process start — restart required |
| ISO build fails | Ensure `xorriso` and `isolinux` installed; 4GB+ RAM required |
