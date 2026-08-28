#!/bin/bash
# ============================================================================
# FreeAIOS Live Installer — LUKS Partitioner
#
# Interactive partitioning tool for the FreeAIOS Live environment.
# Supports:
#   a) Full-disk LUKS2 encryption
#   b) Custom partitioning (boot/swap/root with LUKS on root)
#   c) LVM + LUKS
#
# Usage (from live session):
#   sudo -E live/installer-partitioner.sh [--dry-run] [--disk /dev/sda]
#
# Writes partition map to /etc/freeai/partition-info.json after commit.
# ============================================================================
set -euo pipefail

DRY_RUN=0
TARGET_DISK=""
LOG_FILE="/var/log/freeai-partitioner.log"
PARTITION_INFO="/etc/freeai/partition-info.json"
LUKS_DEFAULTS="/opt/freeai/config/luks-defaults.json"

# ------------------------------------------------------------------ helpers
log() {
  local ts; ts="$(date -Is)"
  echo "[$ts] $*" | tee -a "$LOG_FILE"
}

err() {
  echo "ERROR: $*" >&2
  log "ERROR: $*"
}

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    err "This script must be run as root (sudo)"
    exit 1
  fi
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --dry-run)  DRY_RUN=1 ;;
      --disk)     shift; TARGET_DISK="$1" ;;
      -h|--help)  usage; exit 0 ;;
      *)          err "Unknown option: $1"; usage; exit 1 ;;
    esac
    shift
  done
}

usage() {
  cat <<'EOF'
Usage: installer-partitioner.sh [OPTIONS]

Options:
  --dry-run    Show what would be done without making changes
  --disk DEV   Target disk (e.g. /dev/sda) — skips auto-detect
  -h, --help   Show this help

Environments:
  LIVE_ENCRYPT=1        Enable encryption mode
  PARTITIONER_LOG_LEVEL DEBUG|INFO
EOF
}

# ------------------------------------------------------------------ disk detection
detect_disks() {
  log "Scanning block devices..."
  # Show only disks (not partitions), exclude loop/virtual
  lsblk -d -n -o NAME,SIZE,TYPE,MODEL,ROTA,MOUNTPOINT 2>/dev/null | \
    grep -E '^sd|^vd|^nvme|^mmc' | \
    awk '{printf "  %s  %-12s  %s  %s\n", $1, $2, $4, ($5 == "1" ? "[HDD]" : "[SSD]")}' || true
}

select_disk() {
  if [ -n "$TARGET_DISK" ]; then
    if ! blockdev --exists "$TARGET_DISK" 2>/dev/null; then
      err "Disk $TARGET_DISK not found"
      exit 1
    fi
    echo "$TARGET_DISK"
    return
  fi

  local disks
  disks="$(lsblk -d -n -o NAME,SIZE,TYPE | grep -E '^(sd|vd|nvme|mmc)blk?[0-9]+\s+\S+\sdisk' | awk '{print $1}')"
  if [ -z "$disks" ]; then
    err "No block disks found"
    exit 1
  fi

  echo ""
  echo "Available disks:"
  detect_disks
  echo ""

  while true; do
    echo -n "Select disk (e.g. sda, nvme0n1) or type path: "
    read -r ans
    ans="$(echo "$ans" | tr -d '[:space:]')"
    [ -z "$ans" ] && continue
    # Accept bare name or full path
    case "$ans" in
      /dev/*) TARGET_DISK="$ans" ;;
      *)      TARGET_DISK="/dev/$ans" ;;
    esac
    if blockdev --exists "$TARGET_DISK" 2>/dev/null; then
      echo "Target: $TARGET_DISK"
      break
    else
      echo "  Disk not found. Try again."
    fi
  done
}

# ------------------------------------------------------------------ passphrase
read_passphrase() {
  local label="$1"
  local pass1 pass2
  while true; do
    echo -n "$label"
    read -r -s pass1
    echo ""
    echo -n "Confirm passphrase: "
    read -r -s pass2
    echo ""
    if [ "$pass1" = "$pass2" ] && [ -n "$pass1" ]; then
      echo "$pass1"
      return
    fi
    echo "  Passphrases do not match or are empty. Try again."
  done
}

generate_recovery_key() {
  head -c 32 /dev/urandom | base64 | tr -d '\n' | head -c 32
}

# ------------------------------------------------------------------ partition schemas
# a) Full-disk LUKS2
partition_full_disk_luks() {
  local disk="$1"
  local passphrase="$2"
  local size; size="$(blockdev --getsize64 "$disk" 2>/dev/null || echo 0)"

  log "Full-disk LUKS2 partitioning on $disk (${size} bytes)"

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] Would wipe $disk, create single LUKS2 partition covering entire disk"
    return
  fi

  # Wipe existing signatures
  wipefs -a "$disk" 2>/dev/null || true
  dd if=/dev/urandom of="$disk" bs=1M count=10 status=progress 2>/dev/null || true

  # Create single partition spanning full disk
  parted -s "$disk" mklabel gpt
  parted -s "$disk" mkpart primary ext4 1MiB 100%
  parted -s "$disk" set 1 boot on 2>/dev/null || true

  local part="${disk}1"
  log "Created partition $part"

  # Format with LUKS2
  echo "$passphrase" | cryptsetup luksFormat --type luks2 \
    --cipher aes-xts-plain64 \
    --key-size 512 \
    --pbkdf argon2id \
    --pbkdf-memory 65536 \
    --pbkdf-iterations 4 \
    --batch-mode \
    --key-file=- "$part"

  log "LUKS2 container created on $part"

  # Open LUKS
  echo "$passphrase" | cryptsetup open "$part" freeai_crypt --type luks2 --key-file=-
  log "Opened LUKS container as /dev/mapper/freeai_crypt"

  # Format LVM inside LUKS
  pvcreate "/dev/mapper/freeai_crypt"
  vgcreate freeai_vg "/dev/mapper/freeai_crypt"
  lvcreate -l 100%FREE -n root freeai_vg
  mkfs.ext4 -L freeai-root "/dev/freeai_vg/root"
  log "LVM + ext4 created inside LUKS"

  # Write partition info
  write_partition_info "$disk" "full-disk-luks" "$part" "$part"
}

# b) Custom: boot + swap + LUKS root
partition_custom_luks() {
  local disk="$1"
  local passphrase="$2"
  local mem_size_kb; mem_size_kb="$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
  local swap_size_mb=$(( mem_size_kb / 1024 ))
  [ "$swap_size_mb" -gt 65536 ] && swap_size_mb=65536
  [ "$swap_size_mb" -lt 2048 ] && swap_size_mb=2048

  log "Custom partitioning on $disk (boot + swap + LUKS root)"

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] Would create: /boot (512MiB), swap (${swap_size_mb}MiB), LUKS2 root"
    return
  fi

  wipefs -a "$disk" 2>/dev/null || true
  dd if=/dev/urandom of="$disk" bs=1M count=10 status=progress 2>/dev/null || true

  parted -s "$disk" mklabel gpt
  parted -s "$disk" mkpart boot ext4 1MiB 513MiB
  parted -s "$disk" mkpart primary linux-swap 513MiB "${swap_size_mb}MiB"
  parted -s "$disk" mkpart primary ext4 "${swap_size_mb}MiB" 100%
  parted -s "$disk" set 1 boot on

  local boot_part="${disk}1"
  local swap_part="${disk}2"
  local root_part="${disk}3"

  mkfs.ext4 -L boot "$boot_part"
  mkswap -L swap "$swap_part"
  log "Partitioned: boot=$boot_part swap=$swap_part root=$root_part"

  # LUKS on root
  echo "$passphrase" | cryptsetup luksFormat --type luks2 \
    --cipher aes-xts-plain64 \
    --key-size 512 \
    --pbkdf argon2id \
    --pbkdf-memory 65536 \
    --batch-mode \
    --key-file=- "$root_part"

  echo "$passphrase" | cryptsetup open "$root_part" freeai_crypt --type luks2 --key-file=-
  mkfs.ext4 -L root "/dev/mapper/freeai_crypt"
  log "LUKS2 root unlocked and formatted"

  write_partition_info "$disk" "custom-luks" "$boot_part $swap_part $root_part" "$root_part"
}

# c) LVM + LUKS (flexible)
partition_lvm_luks() {
  local disk="$1"
  local passphrase="$2"

  log "LVM+LUKS partitioning on $disk"

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] Would create: LUKS2 container → VG freeai_vg → LVs root, swap, home"
    return
  fi

  wipefs -a "$disk" 2>/dev/null || true
  dd if=/dev/urandom of="$disk" bs=1M count=10 status=progress 2>/dev/null || true

  parted -s "$disk" mklabel gpt
  parted -s "$disk" mkpart primary ext4 1MiB 100%
  local data_part="${disk}1"

  echo "$passphrase" | cryptsetup luksFormat --type luks2 \
    --cipher aes-xts-plain64 \
    --key-size 512 \
    --pbkdf argon2id \
    --pbkdf-memory 65536 \
    --batch-mode \
    --key-file=- "$data_part"

  echo "$passphrase" | cryptsetup open "$data_part" freeai_crypt --type luks2 --key-file=-

  local mapper="/dev/mapper/freeai_crypt"
  pvcreate "$mapper"
  vgcreate freeai_vg "$mapper"

  local mem_kb; mem_kb="$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
  local swap_mb=$(( mem_kb / 1024 ))
  [ "$swap_mb" -gt 65536 ] && swap_mb=65536
  [ "$swap_mb" -lt 2048 ] && swap_mb=2048

  lvcreate -L "${swap_mb}m" -n swap freeai_vg
  lvcreate -l 100%FREE -n root freeai_vg
  lvcreate -l 50%VG -n home freeai_vg 2>/dev/null || true

  mkswap -L swap "/dev/freeai_vg/swap"
  mkfs.ext4 -L root "/dev/freeai_vg/root"
  mkfs.ext4 -L home "/dev/freeai_vg/home" 2>/dev/null || true

  log "LVM+LUKS layout: VG=freeai_vg LVs=root,swap,home"
  write_partition_info "$disk" "lvm-luks" "$data_part" "$data_part"
}

# ------------------------------------------------------------------ partition info JSON
write_partition_info() {
  local disk="$1"
  local schema="$2"
  local parts="$3"
  local luks_dev="$4"
  local recovery_key; recovery_key="$(generate_recovery_key)"
  local luks_uuid; luks_uuid="$(blkid -o value -s UUID "$luks_dev" 2>/dev/null || echo "")"

  mkdir -p "$(dirname "$PARTITION_INFO")"

  cat > "$PARTITION_INFO" <<EOF
{
  "schema": "$schema",
  "disk": "$disk",
  "partitions": "$parts",
  "luks": {
    "version": "luks2",
    "cipher": "aes-xts-plain64",
    "key_size": 512,
    "pbkdf": "argon2id",
    "pbkdf_memory_kb": 65536,
    "uuid": "$luks_uuid"
  },
  "luks_uuid": "$luks_uuid",
  "recovery_key": "$recovery_key",
  "created_at": "$(date -Is)",
  "hostname": "$(hostname)"
}
EOF
  log "Wrote partition info to $PARTITION_INFO"
  echo ""
  echo "RECOVERY KEY: $recovery_key"
  echo "Save this key — it is a random reference string, NOT the passphrase."
  echo "You will be prompted for your passphrase at every boot."
}

# ------------------------------------------------------------------ main
main() {
  parse_args "$@"
  require_root

  mkdir -p "$(dirname "$LOG_FILE")" "$(dirname "$PARTITION_INFO")"
  log "=== FreeAIOS LUKS Partitioner started ==="
  log "Dry run: $DRY_RUN"

  select_disk

  echo ""
  echo "Partitioning options:"
  echo "  [a] Encrypt entire disk (LUKS2 + LVM)"
  echo "  [b] Custom: /boot + swap + LUKS2 root"
  echo "  [c] LVM + LUKS (root + swap + home)"
  echo ""
  echo -n "Select option [a/b/c]: "
  read -r opt
  opt="$(echo "$opt" | tr '[:upper:]' '[:lower:]')"

  echo ""
  echo -n "Enter LUKS passphrase: "
  local passphrase
  passphrase="$(read_passphrase '')"
  echo ""

  case "$opt" in
    a) partition_full_disk_luks "$TARGET_DISK" "$passphrase" ;;
    b) partition_custom_luks "$TARGET_DISK" "$passphrase" ;;
    c) partition_lvm_luks "$TARGET_DISK" "$passphrase" ;;
    *) err "Invalid option: $opt"; exit 1 ;;
  esac

  log "=== Partitioner completed successfully ==="
  echo ""
  echo "Partitioning complete. Run 'sudo live/installer-partitioner.sh --dry-run' to verify."
}

main "$@"
