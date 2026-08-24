# Local Deployment Guide

Run the Unified GPU Inference Stack on your own hardware instead of
renting cloud GPUs (Vast.ai et al).

## Which path is right?

| Path | Verdict for 24/7 multi-agent workloads |
|---|---|
| **Build a workstation** (this repo's target) | Best: CUDA-only features (llama.cpp GPU offload, vLLM), no hourly billing, no throttling, full control. Pays for itself vs cloud in months of constant use. |
| Used Mac (Apple Silicon) | Not viable here: no CUDA, no vLLM, GGUF runs CPU/Metal-only — fine for chat, wrong for this stack. |
| Cloud GPU instances | Good for bursts and 70B+ experiments you don't host; expensive for always-on agents. |

## Minimum requirements

| Tier | GPU VRAM | RAM | Storage | Runs |
|---|---|---|---|---|
| **Floor** | 8 GB (RTX 3060 Ti / 4060) | 32 GB DDR4 | 500 GB SSD | Qwen3.5-9B Q4_K only, short ctx, 1–2 concurrent agents |
| **Recommended (this build)** | 16 GB (RTX 4070 Ti SUPER / 4080) | 64 GB DDR5-6000 | 1 TB OS + 2 TB models | All three roster models Q6_K, full SDLC agent loops 24/7 |
| **Headroom** | 24 GB (RTX 4090 / 3090) | 96–128 GB | +4 TB models | Larger coder models, heavier vLLM coexistence |

Software floor: Ubuntu Server 24.04 LTS, NVIDIA driver ≥ 550,
CUDA toolkit (for source builds), Docker optional.

## The recommended build (verified MPNs)

Full table with prices and store references:
[parts-list.md](parts-list.md). Summary:

Ryzen 9 7900 · NH-D15S · ASUS TUF B650-PLUS WIFI · GIGABYTE RTX 4070
Ti SUPER Gaming OC **16G** · 64GB DDR5-6000 CL30 EXPO (`F5-6000J3040G32GX2-FX5`)
· 990 EVO 1TB (OS) + SN850X 2TB (models) · RM850x · Fractal North /
Meshify 2 Compact · NF-A14 fans.

Assembly: [BUILD.md](BUILD.md).

## One-shot provisioning

```bash
sudo ./hardware/install-stack.sh          # drivers→CUDA→Docker→stack→systemd→UFW
sudo ./vllm/install-vllm.sh               # optional: bare-metal vLLM backend
./hardware/setup-remote-access.sh tailscale   # or: cloudflare
sudo systemctl enable --now gpu-tune      # undervolt profile (-10..20°C)
```

## 24/7 economics

- Idle draw ≈ 15–25 W; typical agent load 180–260 W at the wall
- `gpu-tune` power cap (~240 W) + `nvidia-persistenced` cut heat and
  cost with <5% throughput loss
- `agents/resource-optimizer.py` (installed as a service) watches
  GPU temperature/utilization and shifts between
  **performance / balanced / eco** power profiles automatically —
  saving money when idle, full speed when the SDLC agents are hammering
- Current mode shows on the Tokugawa Dashboard

Compare: an always-on Vast.ai RTX 4090 class instance costs roughly
$300–450/month — this build breaks even in well under a year of
continuous use, with zero throttling and zero queue times.
