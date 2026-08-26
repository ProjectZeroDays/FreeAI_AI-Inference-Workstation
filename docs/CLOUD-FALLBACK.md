# Cloud Fallback Plan

FreeAI stays useful when the local GPU is absent, busy, or interrupted.
Two modes cover everything from "my 4090 is occupied" to "the whole box
is a spot instance that just died."

Supported providers: **Vast.ai, RunPod, Lambda, Hetzner, Paperspace,
AWS, Azure, GCP (spot or on-demand)**.

## Provider matrix

| Provider | Best for | Launch path | Notes |
|---|---|---|---|
| Vast.ai | cheapest per-hour GPU | `vastai/template.json` + `vastai/onstart.sh` | Instance Portal config; onstart clones repo + boots stack |
| RunPod | persistent + serverless GPU | GHCR image or docker build | pod template with volume mount for models |
| Lambda | bare-metal 24/7 | `hardware/install-stack.sh` over SSH | driver + CUDA preinstalled on their images |
| Hetzner | dedicated GPU (CC/Dedicated) | `hardware/install-stack.sh` | cheapest 24/7 bare metal; GPU lines limited |
| Paperspace | notebooks + gradient | docker compose profile | H100/A4000 pools; persistent storage |
| AWS | enterprise + spot fleets | `deploy.ps1` (EC2 g5/g6/p-series) | spot interrupts: see Mode B resilience |
| Azure | enterprise + NV/ND series | `deploy.ps1` | azurerm; use spot VMSS for cost |
| GCP (spot) | deep-spot discounts | `deploy.ps1` (a2/g2 instances) | preemption notices: stack re-boots clean |

## Mode A — Local router, cloud inference

The router, agents, workflow engine, dashboard, and SDLC orchestrator
stay on the local box. Heavy models run on a cloud GPU.

1. Launch a cloud box with any path above (fastest: Vast.ai template).
2. On the cloud box, only llama needs to run:
   ```bash
   ./llama/llama-server -m /models/<model>.gguf --host 0.0.0.0 --port 9001 \
     -ngl 40 --flash-attn --jinja
   ```
   (or `docker compose up llama` with the repo cloned).
3. On the local box, point a registry entry at the cloud endpoint:
   ```json
   {"id": "qwen3.6-12b-cloud", "backend": "llama",
    "endpoint": "http://<cloud-ip>:9001/v1/chat/completions",
    "role": "primary coder"}
   ```
4. Router fallback chains now try local first, cloud second (or the
   reverse — order is the chain order in `registry/registry.json`).

Traffic is one HTTPS POST per completion; latency is WAN-bound, not
VRAM-bound. Use cloud entries for heavy models, keep 9B hot models
local for snappy interactive work.

## Mode B — Full cloud stack

The entire stack (router + agents + workflow + SDLC + dashboard) runs
in the cloud; your laptop only uses the dashboard/CLI.

```powershell
# Windows provisioner: builds, ships, and boots the stack remotely
.\deploy.ps1 -Provider gcp -Instance a2-highgpu-1g -Spot
.\deploy.ps1 -Provider aws  -Instance g6.xlarge   -Spot
.\deploy.ps1 -Provider hetzner -Instance CCX43-GPU
```

or on any Ubuntu box:

```bash
sudo ./hardware/install-stack.sh          # bare metal / cloud VM
NO_START=1 sudo ./hardware/install-stack.sh   # provision without starting
```

**Same registry, same GGUFs.** `models/auto-download-models.sh` fetches
the identical Q6_K roster, and `registry/registry.json` ships with the
repo — so a cloud deployment behaves exactly like the workstation.

### Spot resilience

- systemd units auto-restart everything after a preemption reboot
- `scripts/backup.sh` + weekly timer keep config/registry restorable
- workflow JSONL audit logs survive reboots; re-run interrupted runs via
  `freeai.py auto-start <spec>`
- for Vast/GCP spot: keep models on the provider volume so re-boots skip
  the ~70 GB download

## Security hardening (cloud-exposed boxes)

`hardware/install-stack.sh` already: enables UFW (SSH + 8030 dashboard
+ 8050 autonomous only), enables unattended security upgrades + NTP.

For cloud deployments additionally:

```bash
# VNC/noVNC ports if you use the desktop profile behind the firewall
sudo ufw allow 5901/tcp   # TigerVNC
sudo ufw allow 6080/tcp   # noVNC (web)
sudo ufw allow 9001/tcp   # ONLY if external clients need llama direct

# fail2ban against SSH brute force
sudo apt-get install -y fail2ban
sudo systemctl enable --now fail2ban
```

Rules of thumb:

- never open 8010/8020/8040/8050 to 0.0.0.0/0 without the Caddy
  basic-auth gateway (`docker/Caddyfile.public`, `--profile tls`)
- prefer noVNC (:6080) over raw VNC (:5901) on public IPs — it is
  token-gated by the desktop image
- cloud firewalls (AWS SG, GCP firewall rules, Azure NSG) should mirror
  UFW: 22 + 8030 + (optional) 6080, nothing else
