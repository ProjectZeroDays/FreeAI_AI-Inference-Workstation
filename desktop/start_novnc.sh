#!/usr/bin/env bash
set -e

NOVNC_WEB="/usr/share/novnc"
WS="/usr/share/novnc/utils/websockify"
if [ ! -x "$WS" ]; then
  WS="$(command -v websockify)"
fi

echo "[desktop] Starting noVNC on :6080 -> localhost:5901"
exec "$WS" --web "$NOVNC_WEB" 6080 localhost:5901
