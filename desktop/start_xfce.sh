#!/usr/bin/env bash
set -e

echo "[desktop] Starting XFCE session..."
export DISPLAY="${VNC_DISPLAY:-:1}"
startxfce4 &
