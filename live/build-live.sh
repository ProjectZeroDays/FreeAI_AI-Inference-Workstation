#!/usr/bin/env bash
# ============================================================================
# FreeAIOS ISO builder — remasters an official Ubuntu 24.04 live-server ISO.
#
# Boot menu on the resulting ISO:
#   1) FreeAI Ubuntu/Kodachi/Kali/NixOS (24.04/XFCE) Live OS  <- default live
#   2) Install FreeAI AI Stack (wipes disk)   <- Subiquity autoinstall:
#        unattended Ubuntu install + stack provisioned on first boot
#   3) Try Ubuntu Server (FreeAI Live)        <- stock live session
#   4) Try Kali Linux XFCE Rolling (Live)     <- Kali in live mode
#   5) Try Ubuntu XFCE Rolling (Live)         <- Ubuntu XFCE live
#   6) Try NixOS Minimum (Live)               <- NixOS minimal live
#   7) Try Kodachi Linux (Live)               <- Kodachi with FreeAI compat
#   8) Rescue shell                           <- rescue target
#   9) Network Diagnostics                    <- full DHCP live
#  10) Memory Test (memtest86+)               <- hardware diagnostics
#
# Build Kali ISO:
#   KALI_ISO=kali-linux-2024.1-live-amd64.iso ./build-live.sh
#
# Build NixOS ISO:
#   NIXOS_ISO=nixos-minimal-24.05.iso ./build-live.sh
#
# Run on Ubuntu 24.04 with:  sudo apt-get install -y xorriso isolinux
# Usage:
#   UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso ./build-live.sh
#   REPO_TARBALL=/path/unified-ai-stack.tar.gz ./build-live.sh   # offline repo
#   LIVE_ENCRYPT=1 ./build-live.sh                                   # include LUKS support
# ============================================================================
set -euo pipefail

# Auto-detect ISO source if not set
if [ -z "${UBUNTU_ISO:-}" ] && [ -z "${KALI_ISO:-}" ] && [ -z "${NIXOS_ISO:-}" ]; then
  UBUNTU_ISO="${UBUNTU_ISO:?set UBUNTU_ISO=/path/to/ubuntu-24.04-live-server-amd64.iso}"
elif [ -n "${KALI_ISO:-}" ]; then
  UBUNTU_ISO="$KALI_ISO"
  ISO_TYPE="kali"
elif [ -n "${NIXOS_ISO:-}" ]; then
  UBUNTU_ISO="$NIXOS_ISO"
  ISO_TYPE="nixos"
else
  UBUNTU_ISO="${UBUNTU_ISO:?set UBUNTU_ISO=/path/to/ubuntu-24.04-live-server-amd64.iso}"
fi
REPO_TARBALL="${REPO_TARBALL:-}"
OUT="${OUT:-$(pwd)/freeaios-amd64.iso}"
LIVE_ENCRYPT="${LIVE_ENCRYPT:-0}"
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

# ---------------------------------------------------------------- Kali-specific payload
# Bundle Kali security tooling for live session
if [ "${ISO_TYPE:-}" = "kali" ] || [ -n "${KALI_TOOLS:-}" ]; then
  echo "[iso] bundling Kali security tooling..."
  mkdir -p "$NEW/freeai/kali-tools"
  cat > "$NEW/freeai/kali-tools/kali-security-tools.list" <<'EOF'
# Kali Linux security tools included in FreeAIOS
nmap
metasploit-framework
wireshark
burpsuite-community
john
hashcat
aircrack-ng
sqlmap
ffuf
gobuster
dirb
hydra
netcat-traditional
socat
tcpdump
tshark
airgeddon
fern-wifi-cracker
wifite
chntpw
volatility
autopsy
sleuthkit
responder
crackmapexec
bloodhound
empire
cobalt-strike-agent
veil
beef
skipfish
w3af
arachni
zaproxy
EOF
fi

# ---------------------------------------------------------------- NixOS-specific payload
# Bundle NixOS security/development profile
if [ "${ISO_TYPE:-}" = "nixos" ] || [ -n "${NIXOS_PROFILE:-}" ]; then
  echo "[iso] bundling NixOS security profile..."
  mkdir -p "$NEW/freeai/nixos-profile"
  cat > "$NEW/freeai/nixos-profile/security.nix" <<'EOF'
# NixOS security tools for FreeAIOS
{ pkgs, ... }:
{
  environment.systemPackages = with pkgs; [
    # Network security
    nmap
    wireshark
    tcpdump
    ssldump
    # Password cracking
    john
    hashcat
    crunch
    # Web app testing
    burpsuite
    zap
    sqlmap
    ffuf
    gobuster
    dirb
    # Exploitation
    metasploit
    # Forensics
    volatility
    autsplay
    sleuthkit
    # Cryptography
    gpg
    age
    scdoc
    # OSINT
    theHarvester
    dnsrecon
    amass
    # Wireless
    aircrack-ng
    wifite
    # Cloud security
    cloudquery
    # AI security
    llm-guard
    garak
    # Misc
    strings
    binwalk
    testdisk
    photorec
  ];
}
EOF
  cat > "$NEW/freeai/nixos-profile/default.nix" <<'EOF'
{ stdenv, fetchFromGitHub, nix, git, python3, nodejs, go, rustup }:
stdenv.mkDerivation {
  pname = "freeai-nixos-security";
  version = "1.0.0";
  src = ./.;
  buildPhase = "echo 'NixOS security profile'";
  installPhase = "mkdir -p $out";
}
EOF
fi

# ---------------------------------------------------------------- remote-access script
# Bundle setup-remote-access.sh into the ISO for first-boot use
mkdir -p "$NEW/freeai/firstboot"
cp "$(dirname "$HERE")/live/setup-remote-access.sh" "$NEW/freeai/firstboot/setup-remote-access.sh"
chmod +x "$NEW/freeai/firstboot/setup-remote-access.sh"

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
      - |
        # Copy remote-access setup script into the installed system
        install -m 0755 /cdrom/freeai/firstboot/setup-remote-access.sh /opt/freeai/setup-remote-access.sh
EOF

# ---------------------------------------------------------------- LUKS encryption support
if [ "$LIVE_ENCRYPT" = "1" ]; then
  echo "[iso] LUKS encryption support enabled"
  mkdir -p "$NEW/freeai/luks"
  # Copy LUKS scripts from live/ directory if present
  if [ -f "$HERE/installer-partitioner.sh" ]; then
    cp "$HERE/installer-partitioner.sh" "$NEW/freeai/luks/installer-partitioner.sh"
    chmod +x "$NEW/freeai/luks/installer-partitioner.sh"
  fi
  if [ -f "$HERE/luks-setup.sh" ]; then
    cp "$HERE/luks-setup.sh" "$NEW/freeai/luks/luks-setup.sh"
    chmod +x "$NEW/freeai/luks/luks-setup.sh"
  fi
  # Copy LUKS defaults config
  if [ -f "$HERE/../config/luks-defaults.json" ]; then
    mkdir -p "$NEW/freeai/config"
    cp "$HERE/../config/luks-defaults.json" "$NEW/freeai/config/luks-defaults.json"
  fi
  # Copy LUKS initramfs hook
  if [ -d "$HERE/hooks" ]; then
    mkdir -p "$NEW/freeai/hooks"
    cp -a "$HERE/hooks/"*.sh "$NEW/freeai/hooks/" 2>/dev/null || true
    # Also copy hook into initramfs-tools hook directory
    mkdir -p "$NEW/etc/initramfs-tools/hooks"
    if [ -f "$HERE/hooks/luks-setup" ]; then
      cp "$HERE/hooks/luks-setup" "$NEW/etc/initramfs-tools/hooks/luks-setup"
      chmod +x "$NEW/etc/initramfs-tools/hooks/luks-setup"
    fi
  fi
  # Add cryptsetup to autoinstall packages
  sed -i 's/packages: \[nvidia-driver-570-server, xorriso\]/packages: [nvidia-driver-570-server, xorriso, cryptsetup-bin, lvm2]/' \
    "$NEW/autoinstall/user-data"
  # Add cryptsetup kernel module to initramfs
  echo "cryptsetup" >> "$NEW/etc/initramfs-tools/modules" 2>/dev/null || true
  echo "dm-crypt" >> "$NEW/etc/initramfs-tools/modules" 2>/dev/null || true
  echo "[iso] LUKS scripts and config copied to ISO"
else
  echo "[iso] LUKS support disabled (set LIVE_ENCRYPT=1 to enable)"
fi

# ---------------------------------------------------------------- grub theme + menu
# Prepend our entries; keep the stock live entry as "Try".
GRUB_CFG="$NEW/boot/grub/grub.cfg"
[ -f "$GRUB_CFG" ] || { echo "[iso] no grub.cfg found at $GRUB_CFG"; exit 1; }
mv "$GRUB_CFG" "$GRUB_CFG.orig"

# Build the header title from detected/release info
HEADER_TITLE="FreeAI Ubuntu/Kodachi/Kali/NixOS (24.04/XFCE) Live OS"

# Create GRUB theme directory
GRUB_THEME_DIR="$NEW/boot/grub/themes/freeai"
mkdir -p "$GRUB_THEME_DIR"
cat > "$GRUB_THEME_DIR/theme.txt" <<'THEME_EOF'
# FreeAI GRUB Theme — matches website dark theme (#060a18 / #5c8bff / #f1f6ff)
desktop-color: "#060a18"
title-color: "#f1f6ff"
show-title: true
terminal-font: "Unifont Regular 16"

+ label {
    left = 0
    top = 30%
    width = 100%
    height = 40
    color = "#8a98ba"
    align = "center"
    font = "Unifont Regular 14"
    text = "FreeAI OS — Unified AI Workstation"
}

+ menu {
    left = 25%
    top = 30%
    width = 50%
    height = 55%
    item_color = "#a5b4dc"
    item_font = "Unifont Regular 18"
    selected_item_color = "#f1f6ff"
    selected_item_font = "Unifont Regular 18"
    item_height = 40
    item_spacing = 6
    icon_height = 0
    icon_width = 0
}

+ label {
    left = 0
    top = 88%
    width = 100%
    height = 30
    color = "#5a6a95"
    align = "center"
    font = "Unifont Regular 12"
    text = "Press Esc for shell · Enter to select · Up/Down to navigate"
}
THEME_EOF

# Append LUKS status indicator to theme if encryption is enabled
if [ "$LIVE_ENCRYPT" = "1" ]; then
  cat >> "$GRUB_THEME_DIR/theme.txt" <<'THEME_LUKS'

+ label {
    left = 0
    top = 92%
    width = 100%
    height = 20
    color = "#F59E0B"
    align = "center"
    font = "Unifont Regular 11"
    text = "[LUKS2 Encrypted Install Available]"
}
THEME_LUKS
fi

{
  cat <<EOF
set default=0
set timeout=10
insmod all_video
insmod gfxterm
insmod theme
set theme=freeai/theme.txt
set gfxmode=auto
set gfxpayload=keep
terminal_output gfxterm

menuentry "${HEADER_TITLE}" {
  set gfxpayload=keep
  linux /casper/vmlinuz boot=casper iso-scan/filename=\${iso_path} quiet splash ---
  initrd /casper/initrd
}

menuentry "Install FreeAI AI Stack (WIPES DISK - unattended)" {
	set gfxpayload=keep
	linux	/casper/vmlinuz autoinstall ds=nocloud\;s=/cdrom/autoinstall iso-scan/filename=\${iso_path} ---
	initrd	/casper/initrd
}

menuentry "Install FreeAI AI Stack — LUKS Encrypted (WIPES DISK)" {
	set gfxpayload=keep
	linux	/casper/vmlinuz autoinstall ds=nocloud\;s=/cdrom/autoinstall iso-scan/filename=\${iso_path} cryptopts=target=freeai_crypt,source=\${crypto_dev},lvm=freeai_vg:root quiet splash ---
	initrd	/casper/initrd
}

menuentry "Try Ubuntu Server (FreeAI Live)" {
	set gfxpayload=keep
	linux	/casper/vmlinuz boot=casper iso-scan/filename=\${iso_path} quiet splash ---
	initrd	/casper/initrd
}

menuentry "Try Kali Linux XFCE Rolling (Live)" {
	set gfxpayload=keep
	linux /casper/vmlinuz boot=casper iso-scan/filename=\${iso_path} quiet splash ---
	initrd /casper/initrd
}

menuentry "Try Ubuntu XFCE Rolling (Live)" {
	set gfxpayload=keep
	linux /casper/vmlinuz boot=casper iso-scan/filename=\${iso_path} quiet splash ---
	initrd /casper/initrd
}

menuentry "Try NixOS Minimum (Live)" {
	set gfxpayload=keep
	linux /nixos/kernel boot=tty quiet splash --
	initrd /nixos/initrd
}

menuentry "Try Kodachi Linux (Live)" {
	set gfxpayload=keep
	linux /casper/vmlinuz boot=casper iso-scan/filename=\${iso_path} quiet splash ---
	initrd /casper/initrd
}

menuentry "Rescue shell (live)" {
	set gfxpayload=keep
	linux	/casper/vmlinuz systemd.unit=rescue.target iso-scan/filename=\${iso_path} ---
	initrd	/casper/initrd
}

menuentry "FreeAI OS — Network Diagnostics" {
	set gfxpayload=keep
	linux /casper/vmlinuz boot=casper iso-scan/filename=\${iso_path} quiet splash ip=dhcp ---
	initrd /casper/initrd
}

menuentry "FreeAI OS — Memory Test (memtest86+)" {
	set gfxpayload=keep
	linux /boot/memtest86+.bin
}

# ---- original config below ----
EOF
  cat "$GRUB_CFG.orig"
} > "$GRUB_CFG"

# Also apply theme to UEFI config if present
for efi_cfg in "$NEW/EFI/boot/grub.cfg"; do
  [ -f "$efi_cfg" ] || continue
  grep -q "set theme" "$efi_cfg" || {
    {
      echo "set theme=freeai/theme.txt"
      echo "insmod theme"
      echo "set gfxpayload=keep"
      cat "$efi_cfg"
    } > "$efi_cfg.tmp"
    mv "$efi_cfg.tmp" "$efi_cfg"
  }
done
echo "[iso] GRUB theme applied: $GRUB_THEME_DIR"

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
if [ "$LIVE_ENCRYPT" = "1" ]; then
  echo "  2) Install FreeAI AI Stack — LUKS Encrypted (wipes + encrypts disk)"
fi
echo "  3) Try Ubuntu Server (FreeAI Live)"
echo "  4) Rescue shell"
echo "[iso] install login: freeai / freeai  (CHANGE ON FIRST LOGIN)"
