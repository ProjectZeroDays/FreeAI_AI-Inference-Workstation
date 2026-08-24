#!/usr/bin/env bash
# Remote access setup: Tailscale (private mesh) and/or Cloudflare Tunnel.
# Usage:
#   ./setup-remote-access.sh tailscale|cloudflare|both
set -euo pipefail

MODE="${1:-tailscale}"
SUDO="sudo"
[ "$(id -u)" -eq 0 ] && SUDO=""

case "$MODE" in
  tailscale)
    if ! command -v tailscale >/dev/null 2>&1; then
      echo "[remote] installing Tailscale..."
      curl -fsSL https://tailscale.com/install.sh | sh
    fi
    echo "[remote] bringing up Tailscale (browser auth will open/print URL)..."
    $SUDO tailscale up --ssh 2>&1 | sed 's/^/[tailscale] /' || true
    echo "[remote] tailnet IP:"
    $SUDO tailscale ip -4 || true
    cat <<EOF

[remote] Done. From any device on your tailnet:
  dashboard : http://<tailnet-ip>:8030
  autonomous: http://<tailnet-ip>:8050
  router    : http://<tailnet-ip>:8010   (keep off public internet)
EOF
    ;;

  cloudflare)
    if ! command -v cloudflared >/dev/null 2>&1; then
      echo "[remote] installing cloudflared..."
      $SUDO mkdir -p --mode=0755 /usr/share/keyrings
      curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg \
        | $SUDO tee /usr/share/keyrings/cloudflare-main.gpg > /dev/null
      echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" \
        | $SUDO tee /etc/apt/sources.list.d/cloudflared.list > /dev/null
      $SUDO apt-get update -y && $SUDO apt-get install -y cloudflared
    fi
    cat <<'EOF'

[remote] Cloudflare Tunnel steps (interactive, run yourself):
  cloudflared tunnel login
  cloudflared tunnel create center
  cloudflared tunnel route dns center ai.yourdomain.com
  cloudflared tunnel run --url http://localhost:8030 center

For a permanent service:
  sudo cloudflared service install   # after writing ~/.cloudflared/config.yml

Recommended config (~/.cloudflared/config.yml):
  tunnel: center
  credentials-file: /home/YOU/.cloudflared/<tunnel-id>.json
  ingress:
    - hostname: ai.yourdomain.com
      service: http://localhost:8030
    - service: http_status:404
EOF
    ;;

  both)
    "$0" tailscale
    echo
    "$0" cloudflare
    ;;
  *)
    echo "usage: $0 tailscale|cloudflare|both" >&2
    exit 1
    ;;
esac
