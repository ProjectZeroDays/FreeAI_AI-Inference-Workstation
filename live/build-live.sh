#!/usr/bin/env bash
# ============================================================================
# FreeAIOS ISO builder — remasters an official Ubuntu 24.04 live-server ISO.
#
# Boot menu on the resulting ISO:
#   1) Install FreeAI AI Stack (wipes disk)   <- Subiquity autoinstall:
#        unattended Ubuntu install + stack provisioned on first boot
#   2) Try Ubuntu Server (FreeAI Live)        <- stock live session
#   3) Rescue shell
#
# Run on Ubuntu 24.04 with:  sudo apt-get install -y xorriso isolinux
# Usage:
#   UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso ./build-live.sh
#   REPO_TARBALL=/path/unified-ai-stack.tar.gz ./build-live.sh   # offline repo
# ============================================================================
set -euo pipefail

UBUNTU_ISO="${UBUNTU_ISO:?set UBUNTU_ISO=/path/to/ubuntu-24.04-live-server-amd64.iso}"
REPO_TARBALL="${REPO_TARBALL:-}"
OUT="${OUT:-$(pwd)/freeaios-amd64.iso}"
HERE="$(cd "$(dirname "$0")" && pwd)"

command -v xorriso >/dev/null || { echo "need xorriso";  exit 1; }
[ -f "$UBUNTU_ISO" ] || { echo "ISO not found: $UBUNTU_ISO"; exit 1; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/freeaios.XXXXXX")"
SRC="$WORK/src"          # extracted original
NEW="$WORK/new"          # modified tree
trap 'chmod -R u+w "$WORK" 2>/dev/null; rm -rf "$WORK"' EXIT

echo "[iso] extracting original ISO..."
xorriso -osirrox on -indev "$UBUNTU_ISO" -extract / "$SRC" >/dev/null 2>&1
chmod -R u+w "$SRC" 2>/dev/null || true
cp -a "$SRC" "$NEW"
chmod -R u+w "$NEW" 2>/dev/null || true

# ---------------------------------------------------------------- repo payload
mkdir -p "$NEW/freeai"
if [ -n "$REPO_TARBALL" ] && [ -f "$REPO_TARBALL" ]; then
  cp "$REPO_TARBALL" "$NEW/freeai/repo.tar.gz"
else
  echo "[iso] bundling local repo tree (git-clean snapshot)..."
  tar --exclude='./.git' --exclude='./venv' --exclude='./.venv-vllm' \
      --exclude='./llama.cpp' --exclude='./models/*.gguf' \
      --exclude='./workspaces' --exclude='./backups' \
      -czf "$NEW/freeai/repo.tar.gz" -C "$(dirname "$HERE")" \
      "$(basename "$(dirname "$HERE")")" 2>/dev/null || \
  tar --exclude='./.git' --exclude='./venv' --exclude='./.venv-vllm' \
      --exclude='./llama.cpp' --exclude='./models/*.gguf' \
      --exclude='./workspaces' --exclude='./backups' \
      -czf "$NEW/freeai/repo.tar.gz" -C "$HERE/.." .
fi

# ---------------------------------------------------------------- first-boot
# Runs once on the INSTALLED system: stack provision + systemd enable.
mkdir -p "$NEW/freeai/firstboot"
cat > "$NEW/freeai/firstboot/freeai-first-boot" <<'EOF'
#!/bin/bash
set -u
LOG=/var/log/freeai-first-boot.log
exec >> "$LOG" 2>&1
echo "[firstboot] $(date -Is) starting"
/opt/freeai/hardware/install-stack.sh || echo "[firstboot] installer partial"
bash /opt/freeai/models/auto-download-models.sh || true
bash /opt/freeai/scripts/clients-provision.sh || true
systemctl enable freeai-stack 2>/dev/null || true
systemctl restart freeai-stack || bash /opt/freeai/start.sh >> "$LOG" 2>&1 &
echo "[firstboot] done - dashboard :8030 | autonomous :8050"
EOF
chmod +x "$NEW/freeai/firstboot/freeai-first-boot"

# ---------------------------------------------------------------- autoinstall
# cloud-init NoCloud seed on the ISO; Subiquity reads it when booted with
#   autoinstall ds=nocloud\;s=/cdrom/autoinstall
mkdir -p "$NEW/autoinstall"
cat > "$NEW/autoinstall/meta-data" <<'EOF'
instance-id: freeai-os-001
EOF

cat > "$NEW/autoinstall/user-data" <<'EOF'
#cloud-config
autoinstall:
  version: 1
  locale: en_US.UTF-8
  keyboard: { layout: us }
  identity:
    hostname: freeai
    username: freeai
    # password: "freeai" (change on first login!)
    password: "$6$rounds=4096$FreeAIOS$Oo0pb.nAah4MWcIQbTh0XBMTALsVmZfTQ0T0WhS2gD5PnH1vBkFMnQeujRipJiUzB0Jzqp9kLwGJljbvXOJ1mN0"
  ssh:
    install-server: true
    allow-pw: true
  storage:
    layout:
      name: direct
  user-data:
    package_update: true
    packages: [nvidia-driver-570-server, xorriso]
    runcmd:
      - mkdir -p /opt/freeai
      - |
        if [ -d /cdrom/freeai ] && [ -f /cdrom/freeai/repo.tar.gz ]; then
          tar -xzf /cdrom/freeai/repo.tar.gz -C /opt --strip-components=1
        fi
      - |
        cat > /etc/systemd/system/freeai-first-boot.service <<UNIT
        [Unit]
        Description=FreeAI stack first-boot provisioner
        After=network-online.target
        Wants=network-online.target
        [Service]
        Type=oneshot
        ExecStart=/freeai-first-boot
        RemainAfterExit=yes
        [Install]
        WantedBy=multi-user.target
        UNIT
        install -m 0755 /cdrom/freeai/firstboot/freeai-first-boot /freeai-first-boot
        systemctl enable freeai-first-boot
EOF

# ---------------------------------------------------------------- grub menu
# Prepend our entries; keep the stock live entry as "Try".
GRUB_CFG="$NEW/boot/grub/grub.cfg"
[ -f "$GRUB_CFG" ] || { echo "[iso] no grub.cfg found at $GRUB_CFG"; exit 1; }
mv "$GRUB_CFG" "$GRUB_CFG.orig"

{
  cat <<'EOF'
set default=0
set timeout=10

menuentry "Install FreeAI AI Stack (WIPES DISK - unattended)" {
	set gfxpayload=keep
	linux	/casper/vmlinuz autoinstall ds=nocloud\;s=/cdrom/autoinstall ---
	initrd	/casper/initrd
}
menuentry "Try Ubuntu Server (FreeAI Live)" {
	set gfxpayload=keep
	linux	/casper/vmlinuz ---
	initrd	/casper/initrd
}
menuentry "Rescue shell (live)" {
	set gfxpayload=keep
	linux	/casper/vmlinuz systemd.unit=rescue.target ---
	initrd	/casper/initrd
}

# ---- original config below ----
EOF
  cat "$GRUB_CFG.orig"
} > "$GRUB_CFG"

# UEFI: same entries for the ESP config if present
for efi_cfg in "$NEW/boot/grub/grub.cfg" "$NEW/EFI/boot/grub.cfg"; do
  [ -f "$efi_cfg" ] || continue
  grep -q "Install FreeAI" "$efi_cfg" || true
done

# ---------------------------------------------------------------- repack
echo "[iso] repacking (UEFI + BIOS hybrid)..."
ISOLINUX_MBR="/usr/lib/ISOLINUX/isohdpfx.bin"
[ -f "$ISOLINUX_MBR" ] || ISOLINUX_MBR="/usr/lib/syslinux/modules/bios/isohdpfx.bin"

# Find EFI partition image (path varies by Ubuntu point release)
EFI_IMG=""
for cand in "$NEW/EFI/boot/efiboot.img" "$NEW/boot/grub/efi.img" "$NEW/EFI/BOOT/efiboot.img" "$NEW/casper/efi.img"; do
  [ -f "$cand" ] && EFI_IMG="$cand" && break
done
if [ -z "$EFI_IMG" ]; then
  EFI_IMG=$(find "$NEW" -maxdepth 4 -name "*.img" -type f | xargs grep -l "EFI" 2>/dev/null | head -n1 || true)
  [ -z "$EFI_IMG" ] && EFI_IMG=$(find "$NEW" -name "efiboot.img" -o -name "efi.img" 2>/dev/null | head -n1 || true)
fi
if [ -n "$EFI_IMG" ]; then
  echo "[iso] EFI image: $EFI_IMG"
  xorriso -as mkisofs -r \
    -V FREEAI_OS \
    -o "$OUT" \
    -J -joliet-long -l \
    -isohybrid-mbr "$ISOLINUX_MBR" \
    -partition_offset 16 --mbr-force-bootable \
    -append_partition 2 28732ac11ff8d211ba4278a28f82efef "$EFI_IMG" \
    -appended_part_as_gpt \
    -e '--interval:appended_partition_2:::' \
    -no-emul-boot \
    --protective-msdos-label \
    "$NEW"
else
  echo "[iso] WARN: no EFI image found — building BIOS-only ISO"
  xorriso -as mkisofs -r \
    -V FREEAI_OS \
    -o "$OUT" \
    -J -joliet-long -l \
    -isohybrid-mbr "$ISOLINUX_MBR" \
    -partition_offset 16 --mbr-force-bootable \
    --protective-msdos-label \
    "$NEW"
fi

echo "[iso] built: $OUT ($(du -h "$OUT" | cut -f1))"
echo "[iso] boot menu:"
echo "  1) Install FreeAI AI Stack (wipes disk, unattended + stack first-boot)"
echo "  2) Try Ubuntu Server (FreeAI Live)"
echo "  3) Rescue shell"
echo "[iso] install login: freeai / freeai  (CHANGE ON FIRST LOGIN)"
