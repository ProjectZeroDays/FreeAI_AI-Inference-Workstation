# Build Sheet — FreeAI Workstation

Single-GPU AI inference workstation sized for the full FreeAI stack:
CUDA llama.cpp, router + parallel hot models, workflow engine,
autonomous SDLC, RAG/Qdrant, WebSocket streaming, FreeToken MoE,
self-healing watchdogs, and the AI power optimizer.

## Actual build (as shipped)

| Component | Part | Why it matters for this stack |
|---|---|---|
| OS | Windows 11 Pro → **Ubuntu 24.04 LTS** (dual-boot) | stack targets Linux + NVIDIA; see FIRST-BOOT-GUIDE |
| CPU | Intel Core i9-14900KF (8P+16E, 32 threads, 6.0 GHz TVB) | agents, SDLC sandbox compiles, RAG ingestion all scale past 24 threads |
| GPU | MSI GeForce RTX 4090 Gaming X Trio 24 GB (DLSS 3) | full-GPU 9B roster Q6_K, 40+ layers, ~35–60 tok/s |
| Motherboard | MSI Z790 Tomahawk WiFi DDR5 | PCIe 5.0 NVMe + Gen4 x16 GPU slot |
| RAM | TeamGroup Delta RGB 128 GB DDR5-6000 (4×32) | 1M-context KV offload headroom, big RAG batches, VMs |
| Storage | 2× MSI 2 TB M.2 NVMe | NVMe1: OS + hot models; NVMe2: RAG + cold models + logs |
| Cooler | EKWB RGB 360 mm AIO | 253 W PL2 sustained during 24/7 SDLC loops |
| PSU | ABS 1000 W Gold ATX 3.0 | 450 W GPU spikes + full system under load |
| Case | Deepcool CH510 ATX | mesh airflow for 24/7 inference duty |
| Network | Wi-Fi 6E + BT 5.3 (**use wired**) | remote desktop + token streaming want low jitter |

## GPU tier comparison

| GPU | VRAM | Class | Strengths for this stack | Limits |
|---|---|---|---|---|
| **RTX 4090** (this build) | 24 GB | Ada gaming | best price/perf; all 9B models full-GPU; 40–80 layers | tight for 32B; consumer thermals |
| RTX 6000 Ada | 48 GB | workstation | ECC; 9B–32B in VRAM; parallel hot models + vLLM coexistence | ~3× price |
| RTX PRO 6000 Blackwell | 96 GB | workstation | 9B–70B full offload; huge contexts; multi-agent concurrency | very expensive |
| A100 80GB | 80 GB | datacenter | proven GGUF/vLLM workhorse | server chassis + cooling |
| H100/H200 | 94/141 GB | datacenter | fastest inference available | overkill for 9B roster |

## Model performance (llama.cpp CUDA + flash-attn, approximate)

| Model | Params | RTX 4090 24 GB | RTX 6000 Ada 48 GB | Blackwell 96 GB |
|---|---|---|---|---|
| Qwen3.6 12B (Ultra Coder) | 12B | 28–48 tok/s, ~44 layers | 45–70 tok/s | 60–95 tok/s |
| Qwen3.5-9B / HighIQ | 9B | 35–60 tok/s, 40 layers | 50–80 tok/s | 60–100 tok/s, parallel instances |
| Qwen3.5-Thinking-9B | 9B | 30–50 tok/s | 45–70 tok/s | concurrent thinking agents |
| Claude-Code-9B (CodeClawd) | 9B | 30–55 tok/s | 45–75 tok/s | many coding agents |
| Qwythos v2 / Qwable 9B | 9B | 30–55 tok/s (vision mmproj) | 45–75 tok/s | parallel multimodal |
| moe-13b (L3.1 2×8B MoE) | 13.7B | 25–45 tok/s (2 experts active) | 40–65 tok/s | 60–90 tok/s |
| Mixtral-class 8×7B | ~47B | partial offload, 10–18 tok/s | mostly VRAM, 15–25 tok/s | full VRAM, 30–45 tok/s |
| 32B GGUF (future) | 32B | heavy NVMe paging | mostly VRAM, decent | fully VRAM, fast |

## Power & thermals (measured class expectations)

| State | GPU | Wall | Notes |
|---|---|---|---|
| Idle (timed window) | ~6% util, 198 W cap, 2400 MHz | ~120–180 W | optimizer eco mode |
| Balanced 24/7 | ~240 W cap, 2520 MHz | ~300–380 W | default steady state |
| Max SDLC burst | stock 450 W, 2610 MHz | ~550–650 W | short runs; AIO handles CPU PL2 |

## Parts policy

- NVIDIA only — the stack is CUDA-centric (llama.cpp CUDA 13.0, driver ≥ 580)
- 64 GB RAM is the floor; 128 GB recommended for 1M-context models + RAG
- 2×2 TB NVMe split (hot vs cold) keeps model swaps off the OS disk
- Wired Ethernet strongly preferred for noVNC + streaming
