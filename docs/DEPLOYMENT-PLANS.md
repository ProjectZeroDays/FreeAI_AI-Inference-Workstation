# Deployment Plans — Live ISO · All-in-One Container · GPU Providers

Three distribution tracks for the same stack. Each is a plan with
starter artifacts already in-tree; execution order recommended:
Docker → Providers → Live ISO.

---

## Track A — All-in-One Docker image (`allinone` profile)

One CUDA image running every service under supervisord; dashboards come
up with `docker compose --profile allinone up`.

Starter artifacts:
- `docker/all-in-one.Dockerfile` — cuda devel base → builds llama.cpp,
  installs venv deps, supervisord entry
- `docker/supervisord-all.conf` — programs: llama, router, agents,
  workflow, autonomous, dashboard (+ auto-restart, stdout logs)

Plan:
1. ✅ artifacts in tree; build: `docker build -f docker/all-in-one.Dockerfile -t tokugawa/allinone .`
2. compose service `allinone` (profile `allinone`) mounting ./models,
   publishing 8010/8020/8030/8040/8050/9001
3. CI: add matrix entry to docker-publish.yml building/pushing
   `ghcr.io/<repo>-allinone` on tags
4. Healthcheck = dashboard /api/status; supervisor handles per-service
   restarts inside the container

## Track B — GPU provider launches (replace Vast.ai workflows)

| Provider | Launch path | Notes |
|---|---|---|
| **Vast.ai** | existing pattern: template env `PROVISIONING_SCRIPT` → GitHub Release bundle tarball → onstart fetch+run | reuse control-plane-deploy experience; publish bundle via release.yml |
| **RunPod** | Docker template from GHCR allinone image; container registry auth public; env = stack.env values; volume mount `/models` | no systemd — supervisord image fits perfectly |
| **Lambda Labs / Paperspace** | bare Ubuntu + `install-stack.sh` (drivers preinstalled) | fastest bare-metal path |
| **Hetzner GPU / OVH** | same as Lambda; add UFW block from provisioner | EU latency win |
| **AWS g5/g6· Azure NC · GCP G2 (spot)** | Terraform module (future): spot VM + cloud-init running install-stack.sh | cost guard: optimizer's eco mode matters most here |

Common contract: any host that can run
`curl bundle | bash` or pull one image gets the full stack + dashboards.
Provider-specific work reduces to env plumbing.

## Track C — Live ISO ("TokugawaOS")

Bootable USB: try live session *with* the stack preinstalled, or install
to disk. Starter: `live/build-live.sh` + `live/README.md`.

Build pipeline (on an Ubuntu build box):
1. `live-build` (Ubuntu squashfs) with these layers:
   - ubuntu-noble base + `ubuntu-drivers-common`, HWE kernel
   - NVIDIA driver `.deb`s bundled (server-570 series) so live boots
     accelerated on target GPUs without network
   - our repo cloned into `/opt/unified-ai-stack` + venv prebuilt
     CPU-mode fallback (llama.cpp CUDA build happens at first boot when
     GPU detected — keeps ISO arch-portable)
2. Boot menu (GRUB) entries:
   - `Try Tokugawa Live (RAM)` — desktop-less autologin, starts
     `tokugawa-stack-live.service` (CPU llama if no GPU)
   - `Install to disk (autoinstall)` — boots Subiquity autoinstall seed:
     partitions, copies /opt stack, enables install-stack.sh first-boot
     unit, sets hostname/user prompts
   - `Rescue shell`
3. First-boot unit (`live/first-boot.sh`) detects GPU:
   - NVIDIA present → apt driver already bundled → run install-stack.sh
     (builds CUDA llama.cpp), starts services, prints dashboard URL on
     TTY1 + optional hotspot QR page
   - No GPU → MOCK_LLM demo mode so the ISO is testable in VMs
4. Persistence: optional casper-rw partition stores models/workspaces
5. Artifacts: ISO ~4–6 GB; CI job on self-hosted runner publishes
   release asset monthly

Acceptance checks per track are listed inline above; each track lands
behind its own git tag (`iso-v0.1`, `allinone-v0.1`) with release notes.
