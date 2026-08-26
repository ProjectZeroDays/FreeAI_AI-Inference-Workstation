# FreeAIOS — Live ISO

Remasters the official **Ubuntu 24.04 live-server** ISO into a bootable
FreeAI installer. Built on any Ubuntu host:

```bash
sudo apt-get install -y xorriso isolinux
UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso ./build-live.sh
# optional: bake the repo into the ISO for offline stack install
REPO_TARBALL=../dist/unified-ai-stack-v1.2.0.tar.gz ./build-live.sh
```

## Boot menu (on the built ISO)

![FreeAIOS GRUB boot menu](../docs/screenshots/boot-menu.png)

*Rendered preview from the builder's grub.cfg entries - compile the ISO
on an Ubuntu host to boot it for real.*


| Entry | What it does |
|---|---|
| **Install FreeAI AI Stack (wipes disk)** | Unattended Subiquity install (autoinstall seed on the ISO): Ubuntu 24.04 + NVIDIA server driver + SSH, then a first-boot systemd unit runs `install-stack.sh`, downloads models, provisions coding clients, and starts the stack. Login: `freeai` / `freeai` — **change it immediately**. |
| **Try Ubuntu Server (FreeAI Live)** | Stock live session (RAM) — inspect the machine, then run the installer manually if you prefer. |
| **Rescue shell** | Live session straight into rescue target. |

## Requirements / notes

- **Network required during install**: the NVIDIA driver + CUDA toolkit
  come from apt (the Ubuntu ISO pool has no NVIDIA packages). Everything
  FreeAI-specific is on the ISO itself (`/cdrom/freeai/repo.tar.gz`).
- **Wipes the target disk** — the autoinstall uses `storage.layout:
  direct` (single root partition). Boot the *Try* entry if you need to
  back up first.
- UEFI + BIOS hybrid boot via the standard Ubuntu `xorriso` repack flags.
- First boot after install: `freeai-first-boot.service` provisions and
  starts everything; progress in `/var/log/freeai-first-boot.log`.
  Dashboard on `:8030`, autonomous API on `:8050`.
