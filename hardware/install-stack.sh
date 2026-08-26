#!/usr/bin/env bash
# ============================================================================
# Center AI Workstation — Ubuntu 24.04 provisioner
# Drivers -> CUDA toolkit -> Docker -> FreeAI stack -> systemd -> firewall.
#
# Usage:
#   sudo ./install-stack.sh                      # full provisioning (prompts for autonomous vs manual)
#   SETUP_MODE=autonomous sudo ./install-stack.sh # autonomous, recommended, zero prompts
#   SETUP_MODE=manual sudo ./install-stack.sh     # manual step-by-step
#   ENABLE_CLOUDFLARED=1 sudo ./install-stack.sh # also install cloudflared
#   NO_START=1 sudo ./install-stack.sh           # don't auto-start services
#
# Safe to re-run: every step is idempotent.
# ============================================================================
set -euo pipefail

STACK_DIR="${STACK_DIR:-}"
STACK_REPO="${STACK_REPO:-}"          # optional git URL to clone from
DRIVER_VERSION="${DRIVER_VERSION:-570-server}"
CUDA_VERSION="${CUDA_VERSION:-13-0}"  # llmv parity; fallback 12-6 below
INSTALL_DOCKER="${INSTALL_DOCKER:-1}"
ENABLE_UFW="${ENABLE_UFW:-1}"
ENABLE_CLOUDFLARED="${ENABLE_CLOUDFLARED:-0}"
NO_START="${NO_START:-0}"

SUDO="sudo"
[ "$(id -u)" -eq 0 ] && SUDO=""

REAL_USER="${SUDO_USER:-$USER}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Default stack dir: the repo this script ships inside, unless overridden.
[ -z "$STACK_DIR" ] && STACK_DIR="$REPO_ROOT"

# ── Setup mode: autonomous (recommended) vs manual ────────────────
SETUP_MODE="${SETUP_MODE:-}"  # autonomous | manual
if [ -z "$SETUP_MODE" ] && [ -t 0 ]; then
  echo
  echo "╔══════════════════════════════════════════════════════════╗"
  echo "║  FreeAI Initial Setup — Choose Configuration Mode       ║"
  echo "╠══════════════════════════════════════════════════════════╣"
  echo "║  [1] Autonomous — Recommended                           ║"
  echo "║      Auto-detects GPU/RAM/CPU and applies optimal       ║"
  echo "║      settings (gpu layers, ctx, providers). Zero       ║"
  echo "║      prompts, uses existing .env keys if present.      ║"
  echo "║  [2] Manual — Full Control                              ║"
  echo "║      Step-by-step: you configure every provider key,   ║"
  echo "║      GPU tuning, and GUI options interactively.        ║"
  echo "╚══════════════════════════════════════════════════════════╝"
  read -r -p "Select [1/2] (default 1): " _choice || _choice=1
  case "$_choice" in 2|manual) SETUP_MODE=manual ;; *) SETUP_MODE=autonomous ;; esac
fi
[ -z "$SETUP_MODE" ] && SETUP_MODE=autonomous
export FREEAI_AUTONOMOUS_SETUP=0
[ "$SETUP_MODE" = "autonomous" ] && FREEAI_AUTONOMOUS_SETUP=1
# Allow non-interactive override: SETUP_MODE=autonomous sudo ./install-stack.sh

log() { echo "[stack] $*"; }
REBOOT_REQUIRED=0

. /etc/os-release
case "${ID:-}" in
  ubuntu) log "Ubuntu ${VERSION_ID} detected" ;;
  *) log "WARN: untested distro '${ID}' — continuing best-effort" ;;
esac

# --------------------------------------------------------------- 1. base pkgs
log "Installing base packages..."
export DEBIAN_FRONTEND=noninteractive
$SUDO apt-get update -y
$SUDO apt-get install -y \
  git curl wget ca-certificates build-essential cmake pkg-config \
  python3 python3-pip python3-venv jq ufw dkms linux-headers-"$(uname -r)"

# ------------------------------------------------------- 2. NVIDIA driver
if command -v nvidia-smi >/dev/null 2>&1; then
  log "NVIDIA driver present: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n1)"
  # persistence daemon: stops driver state reloads between CUDA procs
  $SUDO systemctl enable --now nvidia-persistenced 2>/dev/null \
    || log "nvidia-persistenced not available (non-fatal)"
else
  log "Installing NVIDIA driver ${DRIVER_VERSION}..."
  $SUDO apt-get install -y "nvidia-driver-${DRIVER_VERSION}" \
    || $SUDO apt-get install -y nvidia-driver-550-server \
    || { log "driver install failed — install manually and re-run"; exit 1; }
  REBOOT_REQUIRED=1
fi

# ------------------------------------------------------------ 3. CUDA (nvcc)
if ! command -v nvcc >/dev/null 2>&1; then
  log "Installing CUDA Toolkit ${CUDA_VERSION} (for llama.cpp CUDA build)..."
  keyring="/tmp/cuda-keyring_1.1_all.deb"
  if curl -fsSL -o "$keyring" \
      https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1_all.deb; then
    $SUDO dpkg -i "$keyring"
    $SUDO apt-get update -y
    $SUDO apt-get install -y "cuda-toolkit-${CUDA_VERSION}" \
    || { CUDA_VERSION="12-6"; $SUDO apt-get install -y cuda-toolkit-12-6; } \
      || log "cuda-toolkit install failed — falling back to apt toolkit"
  fi
  command -v nvcc >/dev/null 2>&1 \
    || $SUDO apt-get install -y nvidia-cuda-toolkit \
    || log "WARN: no nvcc — llama.cpp will build CPU-only until fixed"
else
  log "nvcc present: $(nvcc --version | tail -n1)"
fi

# ---------------------------------------------------------------- 4. Docker
if [ "$INSTALL_DOCKER" = "1" ] && ! command -v docker >/dev/null 2>&1; then
  log "Installing Docker Engine..."
  curl -fsSL https://get.docker.com | $SUDO sh
fi
if command -v docker >/dev/null 2>&1; then
  $SUDO usermod -aG docker "$REAL_USER" 2>/dev/null || true
  log "Docker $(docker --version | cut -d' ' -f3 | tr -d ',')"
fi

# ------------------------------------------------------------ 5. stack code
if [ ! -d "$STACK_DIR/.git" ] && [ -n "$STACK_REPO" ]; then
  log "Cloning stack repo into $STACK_DIR ..."
  git clone "$STACK_REPO" "$STACK_DIR"
fi
if [ ! -f "$STACK_DIR/install.sh" ]; then
  log "ERROR: no install.sh at $STACK_DIR (set STACK_DIR or STACK_REPO)"
  exit 1
fi

log "Building venv + llama.cpp (CUDA if nvcc available)..."
(cd "$STACK_DIR" && bash install.sh)

# ------------------------------------------------------------- 6. models
if [ "${AUTO_MODELS:-1}" = "1" ]; then
  log "Downloading GGUF models (resumable — rerun anytime)..."
  (cd "$STACK_DIR" && bash models/auto-download-models.sh) \
    || log "WARN: model download incomplete — rerun later"
fi

# -------------------------------------------------------------- 7. systemd
UNIT_SRC="$SCRIPT_DIR/freeai-stack.service"
UNIT_DST="/etc/systemd/system/freeai-stack.service"
if [ -f "$UNIT_SRC" ]; then
  log "Installing freeai-stack.service..."
  sed -e "s|__STACK_DIR__|$STACK_DIR|g" \
      -e "s|__STACK_USER__|$REAL_USER|g" \
      "$UNIT_SRC" | $SUDO tee "$UNIT_DST" > /dev/null
  $SUDO systemctl daemon-reload
  $SUDO systemctl enable freeai-stack.service
  if [ "$NO_START" != "1" ]; then
    $SUDO systemctl restart freeai-stack.service || \
      log "service start deferred (needs reboot for driver first?)"
  fi
fi

# auxiliary units: watchdog agents + GPU tune + resource optimizer
for unit in freeai-agents gpu-tune resource-optimizer; do
  SRC="$SCRIPT_DIR/systemd/$unit.service"
  [ -f "$SRC" ] || continue
  DST="/etc/systemd/system/$unit.service"
  sed -e "s|__STACK_DIR__|$STACK_DIR|g" \
      -e "s|__STACK_USER__|$REAL_USER|g" \
      "$SRC" | $SUDO tee "$DST" > /dev/null
  $SUDO systemctl daemon-reload
  $SUDO systemctl enable "$unit.service"
done

# daily housekeeping (log rotation + workspace pruning)
CLEAN_SVC="$SCRIPT_DIR/systemd/freeai-cleanup.service"
CLEAN_TMR="$SCRIPT_DIR/systemd/freeai-cleanup.timer"
if [ -f "$CLEAN_SVC" ] && [ -f "$CLEAN_TMR" ]; then
  for f in "$CLEAN_SVC" "$CLEAN_TMR"; do
    DST="/etc/systemd/system/$(basename "$f")"
    sed -e "s|__STACK_DIR__|$STACK_DIR|g" \
        -e "s|__STACK_USER__|$REAL_USER|g" \
        "$f" | $SUDO tee "$DST" > /dev/null
  done
  $SUDO systemctl daemon-reload
  $SUDO systemctl enable --now freeai-cleanup.timer
fi

[ "$NO_START" != "1" ] && \
  $SUDO systemctl start freeai-agents.service gpu-tune.service \
    resource-optimizer.service 2>/dev/null || true

# ---- unattended security updates + clock sync (24/7 box hygiene) ----
log "Enabling unattended security upgrades..."
$SUDO apt-get install -y unattended-upgrades > /dev/null 2>&1 || true
$SUDO dpkg-reconfigure -f noninteractive unattended-upgrades \
  > /dev/null 2>&1 || true
$SUDO timedatectl set-ntp true 2>/dev/null || true

# ---- fail2ban (SSH brute-force protection, default sshd jail) ----
log "Installing fail2ban..."
$SUDO apt-get install -y fail2ban > /dev/null 2>&1 || true
$SUDO systemctl enable --now fail2ban 2>/dev/null || true

# -------------------------------------------------------------- 8. firewall
if [ "$ENABLE_UFW" = "1" ]; then
  log "Configuring UFW (SSH + dashboard + autonomous only)..."
  $SUDO ufw allow OpenSSH
  $SUDO ufw allow 8030/tcp   # dashboard
  $SUDO ufw allow 8050/tcp   # autonomous SDLC
  # desktop profile remote access (opt-in via ENABLE_DESKTOP_PORTS=1)
  if [ "$ENABLE_DESKTOP_PORTS" = "1" ]; then
    $SUDO ufw allow 5901/tcp   # TigerVNC
    $SUDO ufw allow 6080/tcp   # noVNC (web client)
  fi
  # router :8010 and llama.cpp :9001 intentionally NOT exposed
  $SUDO ufw --force enable
fi

# ------------------------------------------------------------ 9. cloudflared
if [ "$ENABLE_CLOUDFLARED" = "1" ] && ! command -v cloudflared >/dev/null 2>&1; then
  log "Installing cloudflared..."
  $SUDO mkdir -p --mode=0755 /usr/share/keyrings
  curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg \
    | $SUDO tee /usr/share/keyrings/cloudflare-main.gpg > /dev/null
  echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" \
    | $SUDO tee /etc/apt/sources.list.d/cloudflared.list > /dev/null
  $SUDO apt-get update -y && $SUDO apt-get install -y cloudflared
  log "Next: cloudflared tunnel login && cloudflared tunnel create center"
fi

# ------------------------------------------------------- 9b. autoconfigure
log "Running FreeAI autoconfigure ($SETUP_MODE)..."
if [ "$SETUP_MODE" = "autonomous" ]; then
  python3 "$REPO_ROOT/scripts/autoconfigure.py" --autonomous || log "autoconfigure autonomous: partial (check .env)"
else
  if [ -t 0 ]; then
    python3 "$REPO_ROOT/scripts/autoconfigure.py" --manual || log "autoconfigure manual: cancelled"
  else
    log "Non-interactive manual requested but no TTY — falling back to autonomous"
    python3 "$REPO_ROOT/scripts/autoconfigure.py" --autonomous || true
  fi
fi

# ------------------------------------------------------------------ summary
echo
log "================ PROVISIONING COMPLETE ================"
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi | head -n12 || \
  log "nvidia-smi unavailable yet"
echo
log "Stack dir : $STACK_DIR"
log "Service   : systemctl status freeai-stack"
log "Dashboard : http://localhost:8030"
log "Autonomous: http://localhost:8050"
log "Router    : http://localhost:8010 (local/tailnet only)"
[ "$REBOOT_REQUIRED" = "1" ] && \
  log "*** REBOOT REQUIRED to activate NVIDIA driver ***"
log "Then verify: python3 $STACK_DIR/freeai.py status"
