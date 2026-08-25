#!/usr/bin/env bash
set -e

# VNC password from env (llmv parity)
if [ -n "${VNC_PASSWORD:-}" ] && command -v vncpasswd >/dev/null 2>&1; then
  mkdir -p "$HOME/.vnc"
  printf "%s" "$VNC_PASSWORD" | vncpasswd -f > "$HOME/.vnc/passwd"
  chmod 600 "$HOME/.vnc/passwd"
fi

echo "[desktop] Starting VNC server..."
vncserver "${VNC_DISPLAY:-:1}" -geometry 1920x1080 -depth 24
