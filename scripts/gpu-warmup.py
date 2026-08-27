"""GPU warmup — launches a dummy CUDA inference to prime kernels.

Detects available NVIDIA GPUs, runs a small forward pass, measures
warmup latency, and stores results in config/gpu-warmup.json.

Usage:
    python scripts/gpu-warmup.py              # warm all GPUs
    python scripts/gpu-warmup.py --devices 0  # warm GPU 0 only
    python scripts/gpu-warmup.py --dry-run    # detect without running
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
RESULTS_PATH = CONFIG_DIR / "gpu-warmup.json"

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def detect_gpus_torch():
    """Return list of torch CUDA device info dicts."""
    if not TORCH_AVAILABLE or not torch.cuda.is_available():
        return []
    count = torch.cuda.device_count()
    devices = []
    for i in range(count):
        devices.append({
            "index": i,
            "name": torch.cuda.get_device_name(i),
            "total_vram_mb": torch.cuda.get_device_properties(i).total_mem // (1024 * 1024),
        })
    return devices


def detect_gpus_nvidia_smi():
    """Fallback: parse nvidia-smi for GPU list."""
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return []
        devices = []
        for line in r.stdout.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                devices.append({
                    "index": int(parts[0]),
                    "name": parts[1],
                    "total_vram_mb": int(parts[2]) * 1024,
                })
        return devices
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        return []


def warmup_device_torch(device_index, batch_size=1, seq_len=64, iters=3):
    """Run dummy forward passes on one GPU and return timing dict."""
    torch.cuda.set_device(device_index)
    dtype = torch.float16 if torch.cuda.is_bf16_supported() else torch.float32
    # Simulate a small transformer-like forward pass
    hidden = 512
    # Warmup: allocate + run a few matmuls to prime CUDA context
    warmup_times = []
    for iteration in range(iters):
        torch.cuda.reset_peak_memory_stats(device_index)
        torch.cuda.synchronize()
        t0 = time.perf_counter()

        # Small linear layers to exercise the GPU
        for _ in range(5):
            a = torch.randn(batch_size, seq_len, hidden, device=f"cuda:{device_index}", dtype=dtype)
            b = torch.randn(hidden, hidden, device=f"cuda:{device_index}", dtype=dtype)
            _ = torch.mm(a.reshape(-1, hidden), b)

        torch.cuda.synchronize()
        dt = (time.perf_counter() - t0) * 1000  # ms
        warmup_times.append(dt)

        peak_mb = torch.cuda.max_memory_allocated(device_index) / (1024 * 1024)

    avg_ms = sum(warmup_times) / len(warmup_times)
    return {
        "device_index": device_index,
        "avg_latency_ms": round(avg_ms, 2),
        "peak_vram_mb": round(peak_mb, 1),
        "iters": iters,
        "status": "ok",
    }


def run_warmup(device_indices=None):
    """Run warmup on specified GPUs; returns list of per-device results."""
    # Detect GPUs
    if TORCH_AVAILABLE and torch.cuda.is_available():
        all_devices = detect_gpus_torch()
    else:
        all_devices = detect_gpus_nvidia_smi()

    if not all_devices:
        return {"skipped": True, "reason": "No NVIDIA GPU detected", "devices": []}

    if device_indices is not None:
        all_devices = [d for d in all_devices if d["index"] in device_indices]

    results = []
    for dev in all_devices:
        idx = dev["index"]
        print(f"  [warmup] GPU {idx}: {dev['name']} ({dev['total_vram_mb']} MB)")
        try:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                r = warmup_device_torch(idx)
            else:
                r = {
                    "device_index": idx,
                    "avg_latency_ms": None,
                    "peak_vram_mb": None,
                    "iters": 0,
                    "status": "skipped-no-torch",
                }
            results.append(r)
            print(f"           → latency={r['avg_latency_ms']}ms  peak_vram={r['peak_vram_mb']}MB")
        except Exception as e:
            results.append({
                "device_index": idx,
                "status": f"error: {e}",
            })

    return {
        "skipped": False,
        "gpu_count": len(all_devices),
        "batch_size": 1,
        "seq_len": 64,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="GPU warmup for FreeAI")
    parser.add_argument("--devices", nargs="+", type=int, help="GPU indices to warm (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Detect GPUs only, skip inference")
    parser.add_argument("--output", type=str, default=str(RESULTS_PATH), help="Results JSON path")
    args = parser.parse_args()

    print("=" * 50)
    print("  GPU Warmup — FreeAI Workstation")
    print("=" * 50)

    # Detect
    if TORCH_AVAILABLE and torch.cuda.is_available():
        devices = detect_gpus_torch()
        print(f"\nDetected {len(devices)} CUDA device(s) via torch")
    else:
        devices = detect_gpus_nvidia_smi()
        if devices:
            print(f"\nDetected {len(devices)} GPU(s) via nvidia-smi (torch unavailable)")
        else:
            print("\nNo NVIDIA GPU detected. Skipping warmup.")
            result = {"skipped": True, "reason": "no-gpu", "devices": []}
            if args.dry_run:
                print(json.dumps(result, indent=2))
                return
            RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
            RESULTS_PATH.write_text(json.dumps(result, indent=2))
            return

    if args.dry_run:
        print("\nDry run — no inference executed.")
        result = {"skipped": True, "reason": "dry-run", "detected": devices}
        print(json.dumps(result, indent=2))
        return

    # Warmup
    print("\nRunning warmup inference (batch=1, seq=64)...")
    indices = args.devices if args.devices else None
    result = run_warmup(indices)

    print("\n" + "-" * 50)
    if result.get("skipped"):
        print(f"  Skipped: {result.get('reason', '?')}")
    else:
        print(f"  GPUs warmed: {result['gpu_count']}")
        for r in result["results"]:
            status = r.get("status", "?")
            lat = r.get("avg_latency_ms")
            print(f"  GPU {r['device_index']}: {status}"
                  + (f"  latency={lat}ms" if lat else ""))

    # Persist
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(f"\nResults saved → {out}")
    print("=" * 50)


if __name__ == "__main__":
    main()
