#!/usr/bin/env bash
# Housekeeping: rotate logs, prune old autonomous workspaces + artifacts.
# Designed for a systemd timer (tokugawa-cleanup.timer) or cron.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_MAX_BYTES=$((25 * 1024 * 1024))   # 25MB per log before rotation
LOG_KEEP=5
WORKSPACE_DAYS="${WORKSPACE_RETENTION_DAYS:-7}"

log() { echo "[cleanup] $*"; }

# ---- rotate oversized logs (keep N rotated copies) ----
mkdir -p "$ROOT/logs"
for f in "$ROOT"/logs/*.log; do
  [ -e "$f" ] || continue
  size=$(stat -c%s "$f" 2>/dev/null || echo 0)
  if [ "$size" -gt "$LOG_MAX_BYTES" ]; then
    i=$((LOG_KEEP))
    while [ "$i" -gt 1 ]; do
      [ -f "$f.$((i-1))" ] && mv "$f.$((i-1))" "$f.$i"
      i=$((i-1))
    done
    mv "$f" "$f.1"
    : > "$f"
    log "rotated $(basename "$f") (${size}B)"
  fi
done

# ---- delete autonomous workspaces older than retention ----
WS_DIR="$ROOT/workspaces"
if [ -d "$WS_DIR" ]; then
  count=$(find "$WS_DIR" -mindepth 1 -maxdepth 1 -type d -mtime \
          +"$WORKSPACE_DAYS" | wc -l)
  if [ "$count" -gt 0 ]; then
    find "$WS_DIR" -mindepth 1 -maxdepth 1 -type d -mtime \
      +"$WORKSPACE_DAYS" -exec rm -rf {} +
    log "pruned $count workspace(s) older than ${WORKSPACE_DAYS}d"
  fi
fi

# ---- drop rotated logs beyond keep count ----
find "$ROOT/logs" -name "*.log.[2-9]" -delete 2>/dev/null || true

log "done."
