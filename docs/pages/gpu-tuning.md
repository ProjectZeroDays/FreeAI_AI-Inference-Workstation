# GPU Tuning — Maximize Performance, Minimize Power

Optimize your GPU for inference workloads with power capping, clock locking, and eco modes.

## Power Modes

FreeAI's resource optimizer automatically shifts between three modes:

| Mode | Power | Clock | Trigger |
|---|---|---|---|
| **performance** | Stock | Stock | util >= 85% and temp <= 75°C |
| **balanced** | 240W | 2520MHz | Steady state (default) |
| **eco** | 200W | 2400MHz | temp >= 82°C or util <= 10% |

## Manual Control

```bash
# View current settings
cat config/runtime-settings.json

# Override via dashboard Settings panel
# Or set environment variables:
export GPU_POWER_LIMIT_W=240
export GPU_LOCKED_CLOCK_MHZ=2520
```

## Undervolting (Advanced)

```bash
# Apply undervolt profile
sudo ./hardware/gpu-power-tune.sh apply

# Check results
sudo ./hardware/gpu-power-tune.sh status

# Reset to stock
sudo ./hardware/gpu-power-tune.sh reset
```

## NVIDIA Persistence Daemon

Enable for faster model loading:

```bash
sudo nvidia-persistenced
sudo systemctl enable nvidia-persistenced
```

## Monitoring

```bash
# Real-time GPU stats
watch -n 1 nvidia-smi

# Detailed power draw
nvidia-smi --query-gpu=power.draw,temperature.gpu,clocks.current --format=csv -l 1

# Utilization history
nvidia-smi pmon -c 1
```

## Next Steps

- [Resource Optimizer](OPTIMIZATION-AUDIT.md) — Automated power management
- [Build Sheet](BUILD-SHEET.md) — Hardware recommendations
