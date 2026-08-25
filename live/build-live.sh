#!/usr/bin/env bash
# TokugawaOS live ISO builder (run on Ubuntu 24.04 with ~40GB free).
# Produces live/tokugawaos-<arch>.iso with a GRUB menu offering:
#   1) Try Tokugawa Live   2) Install to disk (autoinstall)  3) Rescue shell
set -euo pipefail

WORK="${WORK:-$PWD/live/work}"
OUT_DIR="$(cd "$(dirname "$0")" && pwd)"
CODENAME="${CODENAME:-noble}"

command -v lb >/dev/null 2>&1 || {
  echo "install live-build: sudo apt-get install -y live-build"; exit 1; }

rm -rf "$WORK"; mkdir -p "$WORK"
cd "$WORK"

lb config noauto \
  --distribution "$CODENAME" \
  --archive-areas "main restricted universe multiverse" \
  --architecture amd64 \
  --binary-images iso-hybrid \
  --bootappend-live "boot=live components autologin" \
  --debian-installer live \
  --debian-installer-distribution "$CODENAME" \
  ${LB_ARGS:-}

mkdir -p config/includes.chroot/opt
git clone --depth 1 "$(git -C "$(dirname "$0")/.." remote get-url origin 2>/dev/null || echo .)" \
  config/includes.chroot/opt/unified-ai-stack || cp -r .. config/includes.chroot/opt/unified-ai-stack

# first-boot service: GPU detect -> install-stack or MOCK demo
cat > config/includes.chroot/usr/local/sbin/tokugawa-first-boot <<'EOF'
#!/bin/bash
if nvidia-smi >/dev/null 2>&1 || ubuntu-drivers autoinstall; then
  bash /opt/unified-ai-stack/hardware/install-stack.sh NO_START=1
else
  systemd-run --unit=tokugawa-demo \
    env MOCK_LLM=1 /opt/unified-ai-stack/start.sh
fi
systemctl --no-pager status tokugawa-stack || true
EOF
chmod +x config/includes.chroot/usr/local/sbin/tokugawa-first-boot

# autoinstall seed for the "Install to disk" entry
mkdir -p config/includes.chroot/var/lib/installer
cat > config/includes.chroot/var/lib/installer/autoinstall.yaml <<'EOF'
version: 1
identity: { hostname: tokugawa, username: tokugawa, password: "$6$rounds=4096$tokugawa$CHANGE_ME" }
storage:
  layout: { name: direct }
user-data:
  packages: [nvidia-driver-570-server]
  runcmd:
    - bash /usr/local/sbin/tokugawa-first-boot
EOF

echo "[live] building (this takes a while)..."
sudo lb build 2>&1 | tail -n 20

ISO="live-image-amd64.iso"
[ -f "$ISO" ] && mv "$ISO" "$OUT_DIR/tokugawaos-$(date +%Y%m%d)-amd64.iso"
echo "[live] done → $OUT_DIR"
