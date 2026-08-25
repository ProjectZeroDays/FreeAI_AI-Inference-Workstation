#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# --check: drift report only (no changes)
if [ "${1:-}" = "--check" ]; then
  echo "== drift report =="
  rc=0
  for unit in tokugawa-stack tokugawa-agents gpu-tune resource-optimizer; do
    st=$(systemctl is-active "$unit.service" 2>/dev/null || echo missing)
    printf '  %-28s %s\n' "$unit" "$st"
    [ "$st" = "active" ] || rc=1
  done
  if command -v ss >/dev/null 2>&1; then
    for port in 8010 8030 9001; do
      if ss -tln 2>/dev/null | grep -q ":$port "; then
        echo "  port $port bound"
      else
        echo "  port $port NOT bound"; rc=1
      fi
    done
  fi
  [ -x llama.cpp/build/bin/llama-server ] || { echo "  llama-server missing"; rc=1; }
  [ $rc -eq 0 ] && echo "STATE: CONVERGED" || echo "STATE: DRIFT DETECTED"
  exit $rc
fi

# --update-llama: refresh llama.cpp to latest master and rebuild only
if [ "${1:-}" = "--update-llama" ]; then
  LLAMA_DIR="$ROOT/llama.cpp"
  if [ ! -d "$LLAMA_DIR/.git" ]; then
    echo "[update] no llama.cpp checkout — run a full ./install.sh first" >&2
    exit 1
  fi
  echo "[update] pulling latest llama.cpp..."
  git -C "$LLAMA_DIR" fetch --depth 1 origin master
  git -C "$LLAMA_DIR" reset --hard FETCH_HEAD
  echo "[update] rebuilding..."
  CUDA_FLAGS=(-DGGML_CUDA=OFF)
  command -v nvcc >/dev/null 2>&1 && CUDA_FLAGS=(-DGGML_CUDA=ON)
  cmake -S "$LLAMA_DIR" -B "$LLAMA_DIR/build" "${CUDA_FLAGS[@]}"
  cmake --build "$LLAMA_DIR/build" --config Release -j "$(nproc)"
  echo "[update] done — restart the stack (systemctl restart tokugawa-stack)"
  exit 0
fi

echo "[install] Updating system..."
sudo apt-get update -y

echo "[install] Installing base packages..."
sudo apt-get install -y \
  git curl wget build-essential cmake pkg-config \
  libcurl4-openssl-dev \
  python3 python3-pip python3-venv \
  xfce4 xfce4-goodies \
  tigervnc-standalone-server \
  novnc websockify

echo "[install] Creating Python venv..."
[ -d venv ] || python3 -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[install] Fetching llama.cpp..."
LLAMA_DIR="$ROOT/llama.cpp"
if [ ! -d "$LLAMA_DIR/.git" ]; then
  git clone --depth 1 https://github.com/ggerganov/llama.cpp.git "$LLAMA_DIR"
fi

CUDA_FLAGS=(-DGGML_CUDA=OFF)
if command -v nvcc >/dev/null 2>&1; then
  echo "[install] CUDA toolchain found — building GPU backend"
  CUDA_FLAGS=(-DGGML_CUDA=ON)
else
  echo "[install] nvcc not found — building CPU-only llama.cpp (install CUDA toolkit for GPU accel)"
fi

echo "[install] Building llama.cpp..."
cmake -S "$LLAMA_DIR" -B "$LLAMA_DIR/build" "${CUDA_FLAGS[@]}"
cmake --build "$LLAMA_DIR/build" --config Release -j "$(nproc)"

mkdir -p models logs
echo "[install] Done."
echo "Next: bash models/auto-download-models.sh && ./start.sh"
