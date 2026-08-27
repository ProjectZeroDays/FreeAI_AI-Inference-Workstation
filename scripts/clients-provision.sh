#!/usr/bin/env bash
# Coding-clients provisioning (llmv port): Jupyter + OpenCode + ZCode +
# MimoCode + JCode, auto-wired to llama.cpp /v1 and the router.
# Bare-metal systemd path (compose: use --profile jupyter + clients images).
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LLAMA_PORT="${LLAMA_PORT:-9001}"
ROUTER_PORT="${ROUTER_PORT:-8010}"
JUPYTER_PORT="${JUPYTER_PORT:-8888}"
OPENCODE_PORT="${OPENCODE_PORT:-3000}"
ZCODE_PORT="${ZCODE_PORT:-5000}"
LOG_DIR="${LOG_DIR:-$ROOT/logs}"
MODEL_API="http://127.0.0.1:${LLAMA_PORT}/v1"
ROUTER_API="http://127.0.0.1:${ROUTER_PORT}"
mkdir -p "$LOG_DIR" "$ROOT/notebooks"
export DEBIAN_FRONTEND=noninteractive

SUDO="sudo"; [ "$(id -u)" -eq 0 ] && SUDO=""

# ---------------- Jupyter :8888 ----------------
if [ "${JUPYTER_ENABLE:-true}" = "true" ]; then
  echo "[clients] installing JupyterLab..."
  pip3 install -q jupyterlab 2>/dev/null || pip3 install jupyterlab || true
  $SUDO tee /etc/systemd/system/jupyter.service > /dev/null <<EOF
[Unit]
Description=JupyterLab :${JUPYTER_PORT}
After=network.target
[Service]
User=$USER
ExecStart=/usr/bin/env python3 -m jupyterlab --ip=0.0.0.0 --port=${JUPYTER_PORT} --no-browser --allow-root --ServerApp.token='' --notebook-dir=$ROOT/notebooks
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
  $SUDO systemctl daemon-reload
  $SUDO systemctl enable --now jupyter 2>/dev/null || \
    nohup python3 -m jupyterlab --ip=0.0.0.0 --port=${JUPYTER_PORT} \
      --no-browser --allow-root --ServerApp.token= \
      --notebook-dir="$ROOT/notebooks" \
      >>"$LOG_DIR/jupyter-direct.log" 2>&1 &
fi

# ---------------- OpenCode :3000 (provider -> router/llama) ----------------
mkdir -p "$HOME/.config/opencode"
cat > "$HOME/.config/opencode/opencode.json" <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "llama/qwen3.6-12b",
  "small_model": "llama/qwen3.5-9b",
  "provider": {
    "llama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama.cpp (vision)",
      "options": { "baseURL": "${MODEL_API}" },
      "models": {
        "qwen3.6-12b": { "name": "Qwen3.6-12B Heretic" },
        "qwen3.5-9b":  { "name": "Qwen3.5-9B Aggressive" }
      }
    },
    "router": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "FreeAI Router",
      "options": { "baseURL": "${ROUTER_API}/v1" },
      "models": { "auto": { "name": "Router Auto" } }
    }
  }
}
EOF
echo "[clients] opencode.json written ($HOME/.config/opencode/)"

if [ "${INSTALL_CLIENTS:-1}" = "1" ]; then
  echo "[clients] best-effort installs: opencode / zcode / mimicode ..."
  pip3 install -q opencode zcode mimicode 2>/dev/null \
    || npm install -g opencode-ai 2>/dev/null \
    || echo "[clients] package installs unavailable - use compose profiles"

  $SUDO tee /etc/systemd/system/opencode.service > /dev/null <<EOF
[Unit]
Description=OpenCode Server :${OPENCODE_PORT}
After=network.target
[Service]
User=$USER
Environment=PORT=${OPENCODE_PORT}
ExecStart=/bin/bash -c 'command -v opencode >/dev/null && opencode serve --port ${OPENCODE_PORT} --hostname 0.0.0.0 || npx -y opencode-ai serve --port ${OPENCODE_PORT} --hostname 0.0.0.0'
Restart=always
[Install]
WantedBy=multi-user.target
EOF
  $SUDO tee /etc/systemd/system/zcode.service > /dev/null <<EOF
[Unit]
Description=ZCode :${ZCODE_PORT}
After=network.target
[Service]
User=$USER
Environment=PORT=${ZCODE_PORT}
ExecStart=/bin/bash -c 'command -v zcode >/dev/null && zcode serve --port ${ZCODE_PORT} --hostname 0.0.0.0 || true'
Restart=always
[Install]
WantedBy=multi-user.target
EOF
  $SUDO systemctl daemon-reload
  $SUDO systemctl enable opencode zcode 2>/dev/null || true
  $SUDO systemctl restart opencode zcode 2>/dev/null || true
fi

echo "[clients] done. Surfaces: Jupyter :${JUPYTER_PORT} | OpenCode :${OPENCODE_PORT} | ZCode :${ZCODE_PORT}"
echo "[clients] switchboard manifest: mimocode/clients.json (dashboard Clients panel)"
