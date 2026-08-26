# First-Boot Guide — FreeAI Workstation

Ten steps from bare hardware to streaming tokens, sized for the
BUILD-SHEET rig (i9-14900KF / RTX 4090 / Z790 / 128 GB DDR5 / 2×2 TB
NVMe). The stack targets **Ubuntu 24.04 LTS** — dual-boot alongside
Windows 11 Pro or wipe; either works.

## Step 1 — Assemble

- CPU + AIO (EKWB 360) + 4× DDR5 DIMMs + 2× NVMe into the Z790 Tomahawk
- RTX 4090 in the top PCIe x16 slot; both 12VHPWR/8-pin power cables
- ABS 1000 W: 24-pin, 2× 8-pin CPU, GPU, NVMe power
- Deepcool CH510: fans in, cable management out of the GPU airflow path
- Monitor + keyboard; **wireless is fine for setup — use wired Ethernet for production**

## Step 2 — BIOS

1. `Del` to enter BIOS; update to the latest BIOS (Z790 memory support)
2. Enable **XMP** → DDR5-6000 profile for the TeamGroup kit
3. Confirm Resizable BAR on for the GPU
4. Boot order: USB first

## Step 3 — Install Ubuntu 24.04 LTS

1. Flash the Ubuntu 24.04 live-server (or desktop) ISO to USB
2. Install to **NVMe1**; keep NVMe2 for models/RAG (mount at `/srv`)
3. Minimal install + **OpenSSH server** enabled
4. Reboot, apply updates:

```bash
sudo apt update && sudo apt upgrade -y
```

## Step 4 — NVIDIA driver + CUDA

```bash
sudo ubuntu-drivers autoinstall      # or driver 580+ for CUDA 13.0
sudo reboot
nvidia-smi                           # expect: RTX 4090, 24564 MiB
```

## Step 5 — Clone the repo

```bash
git clone https://github.com/ProjectZeroDays/FreeAI_Ubuntu-AI-Inference-Workstation.git
cd FreeAI_Ubuntu-AI-Inference-Workstation
```

## Step 6 — One-shot installer

```bash
sudo ./hardware/install-stack.sh
```

Chains: base packages → NVIDIA driver sanity → CUDA toolkit → Docker →
stack venv + llama.cpp CUDA build → model downloads (Q6_K roster) →
systemd units (core, watchdogs, gpu-tune, optimizer, timers) → UFW
(22/8030/8050; add 5901/6080 if using the desktop profile) → fail2ban →
unattended upgrades + NTP.

Reboot once after driver install, then:

```bash
systemctl status freeai-stack
```

## Step 7 — Model registry

Point the roster at your drives and tune per-GPU layers
(see OPTIMIZATION-AUDIT §4 for the planned `quant`/`n_gpu_layers`
registry fields):

- NVMe1 `/srv/models/hot/` — 8-model Q6_K roster (hot-swap pool)
- NVMe2 `/srv/models/cold/` — future 32B+ experiments
- Start at **40 GPU layers** for 9B models; raise until VRAM ~90%

## Step 8 — Start services

```bash
sudo systemctl enable --now freeai-router freeai-agents freeai-llama freeai-workflow
# or containers:
docker compose up -d router agents workflow dashboard
```

## Step 9 — Verify

Open `http://<workstation-ip>:8030`:

- GPU utilization/temp/power/clock streaming
- services all UP (router, agents, llama, workflow, dashboard)
- router metrics + model shelf populated
- apply the "24-7 Balanced" preset; try "Idle (timed)" to watch the
  eco banner + power drop

CLI sanity:

```bash
python3 freeai.py status
python3 freeai.py route "hello" --max-tokens 32
```

## Step 10 — Remote access

- Desktop profile: `docker compose --profile desktop up -d`
  (XFCE + TigerVNC :5901 + noVNC :6080)
- Connect from your laptop to `http://<ip>:6080` — no VNC client needed
- Run a test agent: FreeAI UI → pick a model → "Refactor this function"
  and watch tokens stream over WebSocket

Then read `docs/CLOUD-FALLBACK.md` if you also want a cloud GPU
overflow, and `docs/OPTIMIZATION-AUDIT.md` for the tuning roadmap.
