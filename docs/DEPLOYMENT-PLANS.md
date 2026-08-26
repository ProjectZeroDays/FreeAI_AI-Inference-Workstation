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
1. ✅ artifacts in tree; build: `docker build -f docker/all-in-one.Dockerfile -t freeai/allinone .`
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

## Track C - Live ISO (FreeAIOS)

**Approach (final): remaster the official Ubuntu 24.04 live-server ISO.**
`live/build-live.sh` extracts the ISO, adds a `/freeai/` payload (repo
tarball + first-boot provisioner), writes a cloud-init NoCloud autoinstall
seed, prepends three GRUB entries, and repacks with the canonical Ubuntu
UEFI/BIOS xorriso flags.

Boot menu on the built ISO:

1. **Install FreeAI AI Stack (wipes disk)** - boots Subiquity with
   `autoinstall ds=nocloud;s=/cdrom/autoinstall`: unattended Ubuntu +
   `nvidia-driver-570-server` + SSH; late-commands copy the repo to
   `/opt/freeai` and enable `freeai-first-boot.service`, which runs
   `install-stack.sh` (CUDA llama.cpp build), downloads models,
   provisions coding clients, and starts the stack. Login
   `freeai/freeai` - forced-change note in live/README.md.
2. **Try Ubuntu Server (FreeAI Live)** - stock live session.
3. **Rescue shell** - live rescue target.

Build: any Ubuntu 24.04 host, `apt install xorriso isolinux`, one
command. Network required during *installation* (NVIDIA apt packages);
the FreeAI payload itself rides on the ISO. Acceptance: boot menu
shows 3 entries; entry 1 completes unattended on a wipe-test VM and
`freeai.py status` reports all services UP on first boot; entry 2
boots a working live session.

