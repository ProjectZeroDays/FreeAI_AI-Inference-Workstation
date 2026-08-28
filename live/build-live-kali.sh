#!/usr/bin/env bash
# ============================================================================
# Build a Kali Linux Live ISO with FreeAI security tooling.
#
# Usage:
#   ./build-live-kali.sh [kali_iso] [output_iso]
#
# Requires: xorriso, kali-live ISO
# ============================================================================
set -euo pipefail

KALI_ISO="${1:-${KALI_ISO:-}}"
OUT="${2:-${OUT:-$(pwd)/freeaios-kali-amd64.iso}}"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_TARBALL="${REPO_TARBALL:-}"

if [ -z "$KALI_ISO" ]; then
  echo "Usage: $0 [kali.iso] [output.iso]"
  echo "  or:  KALI_ISO=kali.iso ./build-live-kali.sh"
  exit 1
fi

[ -f "$KALI_ISO" ] || { echo "Kali ISO not found: $KALI_ISO"; exit 1; }
command -v xorriso >/dev/null || { echo "need xorriso: sudo apt-get install -y xorriso"; exit 1; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/freeai-kali.XXXXXX")"
SRC="$WORK/src"
NEW="$WORK/new"
trap 'chmod -R u+w "$WORK" 2>/dev/null; rm -rf "$WORK"' EXIT

echo "[kali] extracting Kali ISO..."
xorriso -osirrox on -indev "$KALI_ISO" -extract / "$SRC" >/dev/null 2>&1
chmod -R u+w "$SRC" 2>/dev/null || true
cp -a "$SRC" "$NEW"
chmod -R u+w "$NEW" 2>/dev/null || true

# ---------------------------------------------------------------- repo payload
mkdir -p "$NEW/freeai"
if [ -n "$REPO_TARBALL" ] && [ -f "$REPO_TARBALL" ]; then
  cp "$REPO_TARBALL" "$NEW/freeai/repo.tar.gz"
else
  echo "[kali] bundling local repo tree..."
  tar --exclude='./.git' --exclude='./venv' --exclude='./.venv-vllm' \
      --exclude='./llama.cpp' --exclude='./models/*.gguf' \
      --exclude='./workspaces' --exclude='./backups' \
      -czf "$NEW/freeai/repo.tar.gz" -C "$HERE/.." . 2>/dev/null || true
fi

# ---------------------------------------------------------------- Kali security tools manifest
cat > "$NEW/freeai/kali-tools.list" <<'EOF'
nmap metasploit-framework wireshark burpsuite john hashcat aircrack-ng
sqlmap ffuf gobuster dirb hydra netcat-traditional socat tcpdump tshark
airgeddon fern-wifi-cracker wifite chntpw volatility autopsy sleuthkit
responder crackmapexec beef skipfish w3af zaproxy theharvester amass
dnsrecon cloudquery llm-guard garak strings binwalk testdisk photorec
EOF

# ---------------------------------------------------------------- first-boot
mkdir -p "$NEW/freeai/firstboot"
cat > "$NEW/freeai/firstboot/freeai-first-boot" <<'EOF'
#!/bin/bash
set -u
LOG=/var/log/freeai-first-boot.log
exec >> "$LOG" 2>&1
echo "[firstboot] $(date -Is) starting"
[ -f /opt/freeai/hardware/install-stack.sh ] && /opt/freeai/hardware/install-stack.sh || true
[ -f /opt/freeai/models/auto-download-models.sh ] && bash /opt/freeai/models/auto-download-models.sh || true
systemctl enable freeai-stack 2>/dev/null || true
systemctl restart freeai-stack 2>/dev/null || bash /opt/freeai/start.sh >> "$LOG" 2>&1 &
echo "[firstboot] done - dashboard :8030 | tools ready"
EOF
chmod +x "$NEW/freeai/firstboot/freeai-first-boot"

# ---------------------------------------------------------------- repack
echo "[kali] repacking ISO..."
xorriso -as mkisofs -r \
  -V "FREEAI_KALI" \
  -o "$OUT" \
  -J -joliet-long -l \
  -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin 2>/dev/null \
  --protective-msdos-label \
  "$NEW"

echo "[kali] built: $OUT ($(du -h "$OUT" | cut -f1))"
echo "[kali] boot: live/kali-freeai (Kali + FreeAI security tools)"
