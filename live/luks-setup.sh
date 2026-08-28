#!/bin/bash
# ============================================================================
# FreeAIOS — LUKS boot-time unlock script
#
# Detects LUKS-encrypted root at boot, prompts for passphrase via initramfs,
# unlocks the container, and hands control to the real root filesystem.
#
# Install into initramfs:
#   cp luks-setup.sh /usr/sbin/luks-setup.sh
#   update-initramfs -u
#
# Kernel cmdline param: cryptopts=target=freeai_crypt,source=<disk>1,lvm=<vg>/<lv>
# ============================================================================
set -u

LOG="/var/log/luks-setup.log"
PARTITION_INFO="/etc/freeai/partition-info.json"
MAX_RETRIES=3
RETRY_DELAY=5

log() {
  local ts; ts="$(date -Is)"
  echo "[$ts] $*" | tee -a "$LOG"
}

# ------------------------------------------------------------------ detect LUKS
detect_luks_devices() {
  log "Scanning for LUKS devices..."
  local devs
  devs="$(lsblk -d -n -o NAME,TYPE,MODEL | grep -E 'sd|vd|nvme' | awk '$2=="disk"{print "/dev/"$1}')"
  for dev in $devs; do
    if blkid -o value -s TYPE "$dev" 2>/dev/null | grep -q luks; then
      echo "$dev"
    fi
    # Also check partitions
    for p in "${dev}"[0-9]*; do
      [ -b "$p" ] || continue
      if blkid -o value -s TYPE "$p" 2>/dev/null | grep -q luks; then
        echo "$p"
      fi
    done
  done
}

# ------------------------------------------------------------------ prompt for passphrase
read_passphrase() {
  local prompt="$1"
  local pass1 pass2
  local attempt=1

  while [ "$attempt" -le "$MAX_RETRIES" ]; do
    echo "$prompt (attempt $attempt/$MAX_RETRIES):"
    read -r -s pass1
    echo ""
    if [ -n "$pass1" ]; then
      echo "$pass1"
      return 0
    fi
    attempt=$((attempt + 1))
  done
  return 1
}

# ------------------------------------------------------------------ unlock LUKS
unlock_luks() {
  local luks_dev="$1"
  local passphrase="$2"
  local mapper_name="freeai_crypt"

  log "Opening LUKS device: $luks_dev"

  if echo "$passphrase" | cryptsetup open "$luks_dev" "$mapper_name" --type luks2 --key-file=- 2>/dev/null; then
    log "LUKS device unlocked: /dev/mapper/$mapper_name"
    return 0
  fi

  log "FAILED to open LUKS device $luks_dev"
  return 1
}

# ------------------------------------------------------------------ main
main() {
  mkdir -p "$(dirname "$LOG")"
  log "=== LUKS setup script started ==="

  # Check if kernel passed cryptopts
  local cryptopts=""
  if [ -f /proc/cmdline ]; then
    cryptopts="$(cat /proc/cmdline | tr ' ' '\n' | grep '^cryptopts=' | head -1 | cut -d= -f2-)"
  fi
  log "cryptopts from kernel: ${cryptopts:-<none>}"

  # Detect LUKS devices
  local luks_devs
  luks_devs="$(detect_luks_devices)"
  if [ -z "$luks_devs" ]; then
    log "No LUKS devices detected — proceeding with normal boot"
    exit 0
  fi

  log "Found LUKS devices:"
  echo "$luks_devs" | while read -r d; do log "  $d"; done

  # Prompt user for passphrase (recovery_key in partition-info.json is a random reference string, NOT the LUKS passphrase)
  local first_dev
  first_dev="$(echo "$luks_devs" | head -1)"
  if ! passphrase="$(read_passphrase "Enter LUKS passphrase for ${first_dev}")"; then
    log "Too many failed attempts — dropping to emergency shell"
    echo ""
    echo "EMERGENCY: LUKS unlock failed after $MAX_RETRIES attempts."
    echo "Available commands: cryptsetup, lsblk, fdisk, mount, reboot"
    echo "Type 'exit' to retry, 'reboot' to restart."
    /bin/sh
    exit 1
  fi

  # Try each LUKS device
  local unlocked=0
  for dev in $luks_devs; do
    if unlock_luks "$dev" "$passphrase"; then
      unlocked=1
      break
    fi
    log "Retrying in ${RETRY_DELAY}s..."
    sleep "$RETRY_DELAY"
  done

  if [ "$unlocked" -eq 0 ]; then
    log "All LUKS unlock attempts failed"
    echo "EMERGENCY: Could not unlock any LUKS container."
    /bin/sh
    exit 1
  fi

  log "=== LUKS setup complete ==="
}

main "$@"
