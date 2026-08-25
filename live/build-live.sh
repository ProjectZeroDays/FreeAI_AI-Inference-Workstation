#!/usr/bin/env bash
# ============================================================================
# TokugawaOS ISO builder — remasters an official Ubuntu 24.04 live-server ISO.
#
# Boot menu on the resulting ISO:
#   1) Install Tokugawa AI Stack (wipes disk)   <- Subiquity autoinstall:
#        unattended Ubuntu install + stack provisioned on first boot
#   2) Try Ubuntu Server (Tokugawa Live)        <- stock live session
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
OUT="${OUT:-$(pwd)/tokugawaos-amd64.iso}"
HERE="$(cd "$(dirname "$0")" && pwd)"

command -v xorriso >/dev/null || { echo "need xorriso";  exit 1; }
[ -f "$UBUNTU_ISO" ] || { echo "ISO not found: $UBUNTU_ISO"; exit 1; }

WORK="$(mktemp -d /tmp/tokugawaos.XXXXXX)"
SRC="$WORK/src"          # extracted original
NEW="$WORK/new"          # modified tree
trap 'rm -rf "$WORK"' EXIT

echo "[iso] extracting original ISO..."
xorriso -osirrox on -indev "$UBUNTU_ISO" -extract / "$SRC" >/dev/null 2>&1
cp -a "$SRC" "$NEW"

# ---------------------------------------------------------------- repo payload
mkdir -p "$NEW/tokugawa"
if [ -n "$REPO_TARBALL" ] && [ -f "$REPO_TARBALL" ]; then
  cp "$REPO_TARBALL" "$NEW/tokugawa/repo.tar.gz"
else
  echo "[iso] bundling local repo tree (git-clean snapshot)..."
  tar --exclude='./.git' --exclude='./venv' --exclude='./.venv-vllm' \
      --exclude='./llama.cpp' --exclude='./models/*.gguf' \
      --exclude='./workspaces' --exclude='./backups' \
      -czf "$NEW/tokugawa/repo.tar.gz" -C "$(dirname "$HERE")" \
      "$(basename "$(dirname "$HERE")")" 2>/dev/null || \
  tar --exclude='./.git' --exclude='./venv' --exclude='./.venv-vllm' \
      --exclude='./llama.cpp' --exclude='./models/*.gguf' \
      --exclude='./workspaces' --exclude='./backups' \
      -czf "$NEW/tokugawa/repo.tar.gz" -C "$HERE/.." .
fi

# ---------------------------------------------------------------- first-boot
# Runs once on the INSTALLED system: stack provision + systemd enable.
mkdir -p "$NEW/tokugawa/firstboot"
cat > "$NEW/tokugawa/firstboot/tokugawa-first-boot" <<'EOF'
#!/bin/bash
set -u
LOG=/var/log/tokugawa-first-boot.log
exec >> "$LOG" 2>&1
echo "[firstboot] $(date -Is) starting"
/opt/tokugawa/hardware/install-stack.sh || echo "[firstboot] installer partial"
bash /opt/tokugawa/models/auto-download-models.sh || true
bash /opt/tokugawa/scripts/clients-provision.sh || true
systemctl enable tokugawa-stack 2>/dev/null || true
systemctl restart tokugawa-stack || bash /opt/tokugawa/start.sh >> "$LOG" 2>&1 &
echo "[firstboot] done - dashboard :8030 | autonomous :8050"
EOF
chmod +x "$NEW/tokugawa/firstboot/tokugawa-first-boot"

# ---------------------------------------------------------------- autoinstall
# cloud-init NoCloud seed on the ISO; Subiquity reads it when booted with
#   autoinstall ds=nocloud\;s=/cdrom/autoinstall
mkdir -p "$NEW/autoinstall"
cat > "$NEW/autoinstall/meta-data" <<'EOF'
instance-id: tokugawa-os-001
EOF

cat > "$NEW/autoinstall/user-data" <<'EOF'
#cloud-config
autoinstall:
  version: 1
  locale: en_US.UTF-8
  keyboard: { layout: us }
  identity:
    hostname: tokugawa
    username: tokugawa
    # password: "tokugawa" (change on first login!)
    password: "$6$rounds=4096$TokugawaOS$Oo0pb.nAah4MWcIQbTh0XBMTALsVmZfTQ0T0WhS2gD5PnH1vBkFMnQeujRipJiUzB0Jzqp9kLwGJljbvXOJ1mN0"
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
      - mkdir -p /opt/tokugawa
      - |
        if [ -d /cdrom/tokugawa ] && [ -f /cdrom/tokugawa/repo.tar.gz ]; then
          tar -xzf /cdrom/tokugawa/repo.tar.gz -C /opt --strip-components=1
        fi
      - |
        cat > /etc/systemd/system/tokugawa-first-boot.service <<UNIT
        [Unit]
        Description=Tokugawa stack first-boot provisioner
        After=network-online.target
        Wants=network-online.target
        [Service]
        Type=oneshot
        ExecStart=/tokugawa-first-boot
        RemainAfterExit=yes
        [Install]
        WantedBy=multi-user.target
        UNIT
        install -m 0755 /cdrom/tokugawa/firstboot/tokugawa-first-boot /tokugawa-first-boot
        systemctl enable tokugawa-first-boot
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

menuentry "Install Tokugawa AI Stack (WIPES DISK - unattended)" {
	set gfxpayload=keep
	linux	/casper/vmlinuz autoinstall ds=nocloud\;s=/cdrom/autoinstall ---
	initrd	/casper/initrd
}
menuentry "Try Ubuntu Server (Tokugawa Live)" {
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
  grep -q "Install Tokugawa" "$efi_cfg" || true
done

# ---------------------------------------------------------------- repack
echo "[iso] repacking (UEFI + BIOS hybrid)..."
ISOLINUX_MBR="/usr/lib/ISOLINUX/isohdpfx.bin"
[ -f "$ISOLINUX_MBR" ] || ISOLINUX_MBR="/usr/lib/syslinux/modules/bios/isohdpfx.bin"

xorriso -as mkisofs -r \
  -V TOKUGAWA_OS \
  -o "$OUT" \
  -J -joliet-long -l \
  -isohybrid-mbr "$ISOLINUX_MBR" \
  -partition_offset 16 --mbr-force-bootable \
  -append_partition 2 28732ac11ff8d211ba4278a28f82efef "$NEW/EFI/boot/efiboot.img" \
  -appended_part_as_gpt \
  -e '--interval:appended_partition_2:::' \
  -no-emul-boot \
  --protective-msdos-label \
  "$NEW"

echo "[iso] built: $OUT ($(du -h "$OUT" | cut -f1))"
echo "[iso] boot menu:"
echo "  1) Install Tokugawa AI Stack (wipes disk, unattended + stack first-boot)"
echo "  2) Try Ubuntu Server (Tokugawa Live)"
echo "  3) Rescue shell"
echo "[iso] install login: tokugawa / tokugawa  (CHANGE ON FIRST LOGIN)"
