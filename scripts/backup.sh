#!/usr/bin/env bash
# Backup configs, registries, manifests + autonomous run manifests.
#   backup.sh            create backups/backup-<ts>.tar.gz (keep 10)
#   backup.sh restore <file.tar.gz>   restore config/ registry/ manifest/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$ROOT/backups"
KEEP="${BACKUP_KEEP:-10}"

mkdir -p "$BACKUP_DIR"

manifest_list() {
  # paths to archive: small, precious, cheap to restore
  {
    [ -d "$ROOT/config" ] && find "$ROOT/config" -type f \
      ! -name 'llama.env' -printf '%P\n' | sed 's|^|config/|'
    [ -d "$ROOT/registry" ] && find "$ROOT/registry" -type f \
      -printf '%P\n' | sed 's|^|registry/|'
    [ -d "$ROOT/manifest" ] && find "$ROOT/manifest" -type f \
      -printf '%P\n' | sed 's|^|manifest/|'
    [ -f "$ROOT/VERSION" ] && echo "VERSION"
    [ -d "$ROOT/workspaces" ] && \
      find "$ROOT/workspaces" -name '_run.json' -printf '%p\n' \
        | sed "s|$ROOT/||"
    true   # don't let a missing-dir guard fail the whole pipeline
  } | sort -u
}

case "${1:-backup}" in
  backup)
    TS="$(date +%Y%m%d-%H%M%S)"
    OUT="$BACKUP_DIR/backup-$TS.tar.gz"
    LIST="$BACKUP_DIR/.list-$TS"
    manifest_list > "$LIST"

    if [ ! -s "$LIST" ]; then
      echo "[backup] nothing to back up yet"; rm -f "$LIST"; exit 0
    fi
    tar -czf "$OUT" -C "$ROOT" -T "$LIST"
    rm -f "$LIST"
    count=$(ls -1t "$BACKUP_DIR"/backup-*.tar.gz | wc -l)
    ls -1t "$BACKUP_DIR"/backup-*.tar.gz | tail -n +"$((KEEP + 1))" \
      | xargs -r rm -f
    echo "[backup] wrote $OUT ($(du -h "$OUT" | cut -f1)); " \
         "keeping $count newest (retention $KEEP)"
    ;;

  restore)
    FILE="${2:-}"
    [ -n "$FILE" ] && [ -f "$FILE" ] || {
      echo "usage: backup.sh restore <backup.tar.gz>" >&2; exit 1; }
    echo "[backup] restoring from $FILE into $ROOT"
    tar -xzf "$FILE" -C "$ROOT"
    echo "[backup] done. Restart the stack to pick up changes:"
    echo "  sudo systemctl restart freeai-stack"
    ;;

  list)
    ls -1ht "$BACKUP_DIR"/backup-*.tar.gz 2>/dev/null || \
      echo "[backup] no backups yet"
    ;;

  *)
    echo "usage: backup.sh [backup|restore <file>|list]" >&2
    exit 1
    ;;
esac
