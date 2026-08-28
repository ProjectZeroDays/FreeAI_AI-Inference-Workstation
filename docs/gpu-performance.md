# GPU Performance Optimization Guide

## Overview

This guide covers GPU performance optimizations for the FreeAI inference workstation. These optimizations are most effective on Linux with NVIDIA GPUs and gracefully degrade on other platforms.

## CUDA Graphs

### What They Are
CUDA graphs capture a sequence of CUDA API calls into a replayable graph, reducing CPU-side overhead and improving GPU utilization. This is especially beneficial for inference workloads with small batch sizes and fixed sequence lengths.

### When to Use Them
- **Best for**: Stable inference workloads with consistent batch sizes and sequence lengths
- **Capture time**: 10-30 seconds per configuration (non-blocking in production)
- **Typical speedup**: 10-20% latency reduction for small batches
- **Not recommended for**: Highly variable batch sizes or dynamic sequence lengths

### Configuration
```python
from router.gpu_perf import get_graph_manager

manager = get_graph_manager()
result = manager.capture(model_name="Qwen2.5-7B", batch_size=4, seq_len=512)
```

| Setting | Default | Description |
|---------|---------|-------------|
| `CUDA_GRAPH_ENABLED` | `1` | Enable CUDA graph capture |
| `CUDA_GRAPH_DYNAMIC_SEQ` | `1` | Support dynamic sequence lengths |
| `CUDA_GRAPH_CAPTURE_TIMEOUT_S` | `30` | Timeout for capture operation |

## Quantized KV Cache

### What It Is
The KV cache stores key and value tensors from previous decoding steps. Quantizing this cache to 8-bit or 4-bit significantly reduces VRAM usage, allowing longer sequences or larger batch sizes.

### 8-bit vs 4-bit

| Bit-depth | VRAM Savings | Quality Impact | Recommended For |
|-----------|-------------|----------------|-----------------|
| 8-bit | ~50% | Minimal (often imperceptible) | General use, production |
| 4-bit | ~75% | Noticeable quality drop | Memory-constrained setups |

### Configuration
```python
from router.gpu_perf import get_kv_cache

cache = get_kv_cache(bits=8)
result = cache.allocate(model_name="Qwen2.5-7B", max_seq_len=2048)
```

| Setting | Default | Description |
|---------|---------|-------------|
| `KV_CACHE_QUANT_BITS` | `8` | Quantization bit-depth (4 or 8) |
| `KV_CACHE_QUANT_ENABLED` | `1` | Enable quantized KV cache |
| `KV_CACHE_QUANT_THRESHOLD` | `0.9` | Min GPU utilization to enable |

## Speculative Decoding

### What It Is
Speculative decoding uses a smaller "draft" model to propose tokens, which are then verified in parallel by the larger target model. This can significantly increase throughput when the draft model's proposals are frequently accepted.

### Setup
```python
from router.gpu_perf import get_speculative_decoding

sd = get_speculative_decoding()
result = sd.configure(
    draft_model="Qwen2.5-1.5B-Instruct",
    accept_threshold=0.5,
    max_draft_tokens=5,
)
```

### How It Works
1. Draft model generates N tokens in parallel
2. Target model evaluates draft tokens against its probability distribution
3. Tokens above the acceptance threshold are kept
4. Process repeats until rejection or max tokens reached

| Setting | Default | Description |
|---------|---------|-------------|
| `SPECULATIVE_DECODING_ENABLED` | `0` | Enable speculative decoding |
| `SPECULATIVE_DRAFT_MODEL` | `""` | Path to draft model |
| `SPECULATIVE_ACCEPT_THRESHOLD` | `0.5` | Min probability for acceptance |
| `SPECULATIVE_MAX_DRAFT_TOKENS` | `5` | Max tokens to draft per step |

### Performance Expectations
- Good draft/target model pairing: 1.5-2x throughput improvement
- Acceptance rate target: >50%
- Overhead: ~10% additional VRAM for draft model

## K8s GPU Deployment

### Prerequisites
- NVIDIA GPU nodes with `nvidia.com/gpu.present=true` label
- NVIDIA Container Toolkit installed
- NVIDIA Device Plugin running in the cluster

### Key Components

1. **GPU Resources**: Requests `nvidia.com/gpu: 1` to reserve a GPU
2. **CUDA_VISIBLE_DEVICES**: Controls which GPU(s) the container sees
3. **DCGM Exporter**: Sidecar for NVIDIA telemetry via Prometheus
4. **Shared Memory**: `/dev/shm` mounted as tmpfs for multi-GPU communication

### Deployment
```bash
kubectl apply -f k8s/gpu-deployment.yml
```

### Monitoring
- Prometheus metrics available at `:9400/metrics` (DCGM)
- GPU utilization: `DCGM_FI_DEV_GPU_UTIL`
- Memory usage: `DCGM_FI_DEV_MEMORY_USAGE`
- Temperature: `DCGM_FI_DEV_GPU_TEMP`

## Performance Expectations

| Optimization | Typical Speedup | VRAM Impact | Notes |
|-------------|----------------|-------------|-------|
| CUDA Graphs | 10-20% | None | Best for fixed batch/seq |
| 8-bit KV Cache | 0% (indirect) | -50% | Enables larger batches |
| 4-bit KV Cache | 0% (indirect) | -75% | May affect quality |
| Speculative Decoding | 50-100% | +10% (draft) | Depends on draft quality |

## Platform Notes

- **Linux + NVIDIA**: Full optimization support
- **Windows/WSL**: Mock implementations return gracefully with warnings
- **No GPU**: All optimizations skip with logged warnings
- **AMD GPUs**: Not currently supported; requires ROCm migration
