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
2. **Install FreeAI AI Stack — LUKS Encrypted (wipes + encrypts disk)** -
   same as above but with full-disk LUKS2 encryption. Requires
   `LIVE_ENCRYPT=1` at build time. Kernel cmdline includes
   `cryptopts=target=freeai_crypt`. Passphrase prompt appears in initramfs.
3. **Try Ubuntu Server (FreeAI Live)** - stock live session.
4. **Rescue shell** - live rescue target.

Build: any Ubuntu 24.04 host, `apt install xorriso isolinux`, one
command. Network required during *installation* (NVIDIA apt packages);
the FreeAI payload itself rides on the ISO. Acceptance: boot menu
shows entries; entry 1 completes unattended on a wipe-test VM and
`freeai.py status` reports all services UP on first boot; entry 2
boots a LUKS-encrypted install with passphrase prompt.

---

## Track C.1 — LUKS Full-Disk Encryption

### Overview

FreeAIOS supports three LUKS partitioning schemas, configurable via the
interactive partitioner or the ISO installer menu.

### Partitioner

`live/installer-partitioner.sh` is an interactive root-only script that
runs in the live environment:

```bash
sudo live/installer-partitioner.sh              # interactive
sudo live/installer-partitioner.sh --dry-run    # preview only
sudo live/installer-partitioner.sh --disk /dev/nvme0n1
```

Three schemas are offered:

| Option | Schema | Description |
|---|---|---|
| **a** | Full-disk LUKS2 | Single LUKS2 container spanning the entire disk; LVM inside with `root` LV |
| **b** | Custom LUKS | Separate `/boot` (ext4), swap, and LUKS2-encrypted root |
| **c** | LVM + LUKS | LUKS2 container with VG `freeai_vg` and LVs for root, swap, and home |

After partitioning, the script writes `/etc/freeai/partition-info.json`
containing the schema, disk layout, LUKS parameters, and a 32-character
recovery key.

### Runtime unlock

`live/luks-setup.sh` handles boot-time LUKS unlocking inside the
initramfs:

1. Scans block devices for `type=luks` via `blkid`
2. If `/etc/freeai/partition-info.json` exists, attempts the recovery
   key first
3. Prompts the user for the LUKS passphrase (up to 3 retries)
4. Falls back to an emergency `/bin/sh` shell on repeated failure

Kernel parameter for encrypted installs:
```
cryptopts=target=freeai_crypt,source=/dev/sda1,lvm=freeai_vg:root
```

### Default LUKS settings

`config/luks-defaults.json` controls encryption parameters:

```json
{
  "luks_version": "luks2",
  "cipher": "aes-xts-plain64",
  "key_size": 512,
  "pbkdf": "argon2id",
  "pbkdf_memory": 65536,
  "recovery_key_length": 32
}
```

### Building with LUKS support

```bash
LIVE_ENCRYPT=1 UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso ./live/build-live.sh
```

This adds `cryptsetup-bin` and `lvm2` to the autoinstall package list,
copies `installer-partitioner.sh` and `luks-setup.sh` into the ISO
payload, and adds a "LUKS Encrypted" GRUB boot entry with an amber
status indicator in the theme.

### Recovery procedures

**Forgotten passphrase:**
1. Boot into the Rescue shell entry
2. Run `sudo live/installer-partitioner.sh --dry-run` to inspect the
   partition layout
3. Locate the recovery key in `/etc/freeai/partition-info.json`
4. Use it: `echo '<recovery-key>' | cryptsetup luksOpen /dev/sda1 freeai_crypt --key-file=-`

**Regenerate recovery key (after unlock):**
1. From the running system, visit `http://<host>:8030/encryption`
2. Click "Generate New Key" — this updates
   `/etc/freeai/partition-info.json`
3. The old recovery key is immediately invalidated

**Re-encrypt a disk:**
1. Boot the ISO and select the LUKS Encrypted install entry
2. Or run manually in live mode:
   ```bash
   sudo live/installer-partitioner.sh --disk /dev/sda
   ```


