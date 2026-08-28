#!/usr/bin/env bash
# ============================================================================
# Build a NixOS Minimum Live ISO with FreeAI security tooling.
#
# Usage:
#   ./build-live-nixos.sh [nixos_iso] [output_iso]
#
# Requires: xorriso, NixOS minimal ISO
# ============================================================================
set -euo pipefail

NIXOS_ISO="${1:-${NIXOS_ISO:-}}"
OUT="${2:-${OUT:-$(pwd)/freeaios-nixos-amd64.iso}}"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_TARBALL="${REPO_TARBALL:-}"

if [ -z "$NIXOS_ISO" ]; then
  echo "Usage: $0 [nixos.iso] [output.iso]"
  echo "  or:  NIXOS_ISO=nixos.iso ./build-live-nixos.sh"
  exit 1
fi

[ -f "$NIXOS_ISO" ] || { echo "NixOS ISO not found: $NIXOS_ISO"; exit 1; }
command -v xorriso >/dev/null || { echo "need xorriso: sudo apt-get install -y xorriso"; exit 1; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/freeai-nixos.XXXXXX")"
SRC="$WORK/src"
NEW="$WORK/new"
trap 'chmod -R u+w "$WORK" 2>/dev/null; rm -rf "$WORK"' EXIT

echo "[nixos] extracting NixOS ISO..."
xorriso -osirrox on -indev "$NIXOS_ISO" -extract / "$SRC" >/dev/null 2>&1
chmod -R u+w "$SRC" 2>/dev/null || true
cp -a "$SRC" "$NEW"
chmod -R u+w "$NEW" 2>/dev/null || true

# ---------------------------------------------------------------- repo payload
mkdir -p "$NEW/freeai"
if [ -n "$REPO_TARBALL" ] && [ -f "$REPO_TARBALL" ]; then
  cp "$REPO_TARBALL" "$NEW/freeai/repo.tar.gz"
else
  echo "[nixos] bundling local repo tree..."
  tar --exclude='./.git' --exclude='./venv' --exclude='./.venv-vllm' \
      --exclude='./llama.cpp' --exclude='./models/*.gguf' \
      --exclude='./workspaces' --exclude='./backups' \
      -czf "$NEW/freeai/repo.tar.gz" -C "$HERE/.." . 2>/dev/null || true
fi

# ---------------------------------------------------------------- NixOS security profile
mkdir -p "$NEW/freeai/nixos-profile"
cat > "$NEW/freeai/nixos-profile/security.nix" <<'EOF'
{ pkgs, ... }:
{
  environment.systemPackages = with pkgs; [
    nmap wireshark tcpdump ssldump
    john hashcat crunch
    sqlmap ffuf gobuster dirb
    metasploit
    volatility autsplay sleuthkit
    gpg age scdoc
    theharvester dnsrecon amass
    aircrack-ng wifite
    cloudquery
    llm-guard garak
    strings binwalk testdisk photorec
  ];
  # FreeAI stack first-boot
  services.freeai = {
    enable = true;
    dashboardPort = 8030;
    autonomousPort = 8050;
  };
}
EOF

# ---------------------------------------------------------------- first-boot
mkdir -p "$NEW/freeai/firstboot"
cat > "$NEW/freeai/firstboot/freeai-first-boot" <<'EOF'
#!/bin/bash
set -u
LOG=/var/log/freeai-first-boot.log
exec >> "$LOG" 2>&1
echo "[firstboot] $(date -Is) starting NixOS"
[ -f /nix/var/nix/profiles/default/bin/nixos-rebuild ] && \
  nixos-rebuild switch --flake /opt/freeai/nixos-profile 2>/dev/null || true
[ -f /opt/freeai/hardware/install-stack.sh ] && /opt/freeai/hardware/install-stack.sh || true
systemctl enable freeai-stack 2>/dev/null || true
systemctl restart freeai-stack 2>/dev/null || bash /opt/freeai/start.sh >> "$LOG" 2>&1 &
echo "[firstboot] done - NixOS + FreeAI stack on :8030"
EOF
chmod +x "$NEW/freeai/firstboot/freeai-first-boot"

# ---------------------------------------------------------------- repack
echo "[nixos] repacking ISO..."
xorriso -as mkisofs -r \
  -V "FREEAI_NIXOS" \
  -o "$OUT" \
  -J -joliet-long -l \
  -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin 2>/dev/null \
  --protective-msdos-label \
  "$NEW"

echo "[nixos] built: $OUT ($(du -h "$OUT" | cut -f1))"
echo "[nixos] boot: NixOS + FreeAI security tools"
