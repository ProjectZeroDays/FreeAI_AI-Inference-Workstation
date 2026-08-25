#!/bin/bash
# Tokugawa stack onstart for Vast.ai (CUDA 13 image).
# Downloads the release bundle, provisions, launches clients + desktop.
set -u

REPO_DIR="${REPO_DIR:-/opt/tokugawa}"
BUNDLE_URL="${PROVISIONING_SCRIPT:-}"
LOG="/var/log/tokugawa-onstart.log"
exec >> "$LOG" 2>&1

echo "[onstart] $(date -Is) starting"

# 1) NVIDIA driver (image ships toolkit only; host driver passthrough on Vast)
nvidia-smi || { echo "[onstart] no GPU visible - continuing (MOCK possible)"; }

# 2) fetch + unpack bundle
mkdir -p "$REPO_DIR"
curl -fsSL "$BUNDLE_URL" -o /tmp/bundle.tar.gz \
  && tar -xzf /tmp/bundle.tar.gz -C "$REPO_DIR" --strip-components=1 \
  || { echo "[onstart] bundle fetch failed"; exit 1; }

# 3) provision (drivers already on Vast images -> skip apt driver step)
cd "$REPO_DIR"
bash install.sh || echo "[onstart] install.sh partial - continuing"

# 4) models (resumable)
bash models/auto-download-models.sh || true

# 5) coding clients + desktop (llmv parity)
bash scripts/clients-provision.sh || true
bash desktop/start_xfce.sh >> "$REPO_DIR/logs/desktop.log" 2>&1 &
bash desktop/start_vnc.sh  >> "$REPO_DIR/logs/desktop.log" 2>&1 &
bash desktop/start_novnc.sh >> "$REPO_DIR/logs/desktop.log" 2>&1 &

# 6) stack via systemd if available, else start.sh
if command -v systemctl >/dev/null 2>&1 && pidof systemd >/dev/null; then
  sed -e "s|__STACK_DIR__|$REPO_DIR|g" -e "s|__STACK_USER__|root|g" \
      hardware/tokugawa-stack.service > /etc/systemd/system/tokugawa-stack.service
  systemctl daemon-reload && systemctl restart tokugawa-stack
else
  nohup bash start.sh >> "$REPO_DIR/logs/stack.log" 2>&1 &
fi

echo "[onstart] done - dashboard :8030 | portal :1111 | jupyter :8888"
