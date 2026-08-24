#!/usr/bin/env bash
set -e

echo "[desktop] Starting VNC server..."
vncserver "${VNC_DISPLAY:-:1}" -geometry 1920x1080 -depth 24
