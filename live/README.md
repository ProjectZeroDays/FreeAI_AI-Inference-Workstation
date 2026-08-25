# TokugawaOS — Live ISO

Remasters the official **Ubuntu 24.04 live-server** ISO into a bootable
Tokugawa installer. Built on any Ubuntu host:

```bash
sudo apt-get install -y xorriso isolinux
UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso ./build-live.sh
# optional: bake the repo into the ISO for offline stack install
REPO_TARBALL=../dist/unified-ai-stack-v1.2.0.tar.gz ./build-live.sh
```

## Boot menu (on the built ISO)

| Entry | What it does |
|---|---|
| **Install Tokugawa AI Stack (wipes disk)** | Unattended Subiquity install (autoinstall seed on the ISO): Ubuntu 24.04 + NVIDIA server driver + SSH, then a first-boot systemd unit runs `install-stack.sh`, downloads models, provisions coding clients, and starts the stack. Login: `tokugawa` / `tokugawa` — **change it immediately**. |
| **Try Ubuntu Server (Tokugawa Live)** | Stock live session (RAM) — inspect the machine, then run the installer manually if you prefer. |
| **Rescue shell** | Live session straight into rescue target. |

## Requirements / notes

- **Network required during install**: the NVIDIA driver + CUDA toolkit
  come from apt (the Ubuntu ISO pool has no NVIDIA packages). Everything
  Tokugawa-specific is on the ISO itself (`/cdrom/tokugawa/repo.tar.gz`).
- **Wipes the target disk** — the autoinstall uses `storage.layout:
  direct` (single root partition). Boot the *Try* entry if you need to
  back up first.
- UEFI + BIOS hybrid boot via the standard Ubuntu `xorriso` repack flags.
- First boot after install: `tokugawa-first-boot.service` provisions and
  starts everything; progress in `/var/log/tokugawa-first-boot.log`.
  Dashboard on `:8030`, autonomous API on `:8050`.
