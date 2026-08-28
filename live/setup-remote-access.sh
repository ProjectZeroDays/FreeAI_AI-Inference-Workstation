#!/usr/bin/env bash
# ============================================================================
# FreeAI — SSH / noVNC / TigerVNC auto-setup (first boot)
#
# Detects first-boot via /etc/.remote-setup-done flag.
# Prompts interactively for SSH password, VNC password, and SSH public keys.
# Installs and configures:
#   - openssh-server  (port 22)
#   - tigervnc-standalone-server (port 5900)
#   - noVNC           (port 6080, web-based VNC client)
# Creates firewall allow rules for ports 22, 5900, 6080.
# Writes final config to /etc/freeai/remote-access.json.
# ============================================================================
set -euo pipefail

FLAG_FILE="/etc/.remote-setup-done"
CONFIG_DIR="/etc/freeai"
CONFIG_FILE="$CONFIG_DIR/remote-access.json"
LOG_FILE="/var/log/freeai-remote-setup.log"

exec >> "$LOG_FILE" 2>&1
echo "[$(date -Is)] remote-access setup starting"

# ── Source .env if available ────────────────────────────────────
for _ENV_PATH in /etc/freeai/.env "$HOME/.freeai/.env"; do
    if [ -f "$_ENV_PATH" ]; then
        set -a; source "$_ENV_PATH"; set +a
        echo "[$(date -Is)] sourced $_ENV_PATH"
        break
    fi
done

# ── First-boot guard ─────────────────────────────────────────────
if [ -f "$FLAG_FILE" ]; then
    echo "[$(date -Is)] already configured ($FLAG_FILE exists), skipping"
    exit 0
fi

# ── Package install ──────────────────────────────────────────────
echo "[$(date -Is)] installing packages ..."
apt-get update -qq
apt-get install -y -qq openssh-server tigervnc-standalone-server tigervnc-common novnc websockify 2>/dev/null || \
    apt-get install -y -qq openssh-server tigervnc-standalone-server tigervnc-common novnc websockify

# ── Helpers ──────────────────────────────────────────────────────
gen_random_pw() {
    < /dev/urandom tr -dc 'A-Za-z0-9!#$%&()*+,-./:;<=>?@[\]^_`{|}~' | head -c 20
}

# ── Prompt user (TTY) or fall back to random ────────────────────
if [ -t 0 ] && [ -t 1 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║     FreeAI — Remote Access Setup (first boot)            ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    # SSH password (consume from .env if set)
    if [ -z "${SSH_PASSWORD:-}" ]; then
        read -rp "SSH password (leave empty for random): " SSH_PASSWORD_INPUT
        if [ -z "$SSH_PASSWORD_INPUT" ]; then
            SSH_PASSWORD="$(gen_random_pw)"
            echo "  → generated random SSH password"
        else
            SSH_PASSWORD="$SSH_PASSWORD_INPUT"
        fi
    else
        echo "[$(date -Is)] using SSH_PASSWORD from .env"
    fi

    # VNC password (max 8 chars for TigerVNC) — consume from .env if set
    if [ -z "${VNC_PASSWORD:-}" ]; then
        read -rp "VNC password (max 8 chars, leave empty for random): " VNC_PASSWORD_INPUT
        if [ -z "$VNC_PASSWORD_INPUT" ]; then
            VNC_PASSWORD="$(gen_random_pw | head -c 8)"
            echo "  → generated random VNC password"
        else
            VNC_PASSWORD="${VNC_PASSWORD_INPUT:0:8}"
        fi
    else
        VNC_PASSWORD="${VNC_PASSWORD:0:8}"
        echo "[$(date -Is)] using VNC_PASSWORD from .env"
    fi

    # SSH public keys (consume from .env if set)
    if [ -z "${SSHAuthorizedKeys:-}" ]; then
        echo ""
        echo "Paste one or more SSH public keys (one per line), then press Ctrl-D:"
        SSH_KEYS=""
        while IFS- read -r line; do
            [ -n "$line" ] && SSH_KEYS+="$line"$'\n'
        done
        SSH_KEYS="${SSH_KEYS%$'\n'}"  # trim trailing newline
    else
        SSH_KEYS="$SSHAuthorizedKeys"
        echo "[$(date -Is)] using SSHAuthorizedKeys from .env"
    fi
else
    echo "[$(date -Is)] non-interactive environment — generating random credentials"
    SSH_PASSWORD="$(gen_random_pw)"
    VNC_PASSWORD="$(gen_random_pw | head -c 8)"
    SSH_KEYS=""
fi

echo "[$(date -Is)] credentials generated"

# ── Configure SSH ───────────────────────────────────────────────
echo "[$(date -Is)] configuring SSH ..."
mkdir -p /etc/ssh/sshd_config.d

cat > /etc/ssh/sshd_config.d/freeai.conf <<'SSHCONF'
PermitRootLogin prohibit-password
PasswordAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
X11Forwarding no
TCPKeepAlive yes
ClientAliveInterval 300
ClientAliveCountMax 2
SSHCONF

# Set the freeai user password if user exists
if id -u freeai &>/dev/null; then
    echo "freeai:$SSH_PASSWORD" | chpasswd 2>/dev/null || true
    mkdir -p /home/freeai/.ssh
    if [ -n "$SSH_KEYS" ]; then
        echo "$SSH_KEYS" > /home/freeai/.ssh/authorized_keys
        chown -R freeai:freeai /home/freeai/.ssh
        chmod 700 /home/freeai/.ssh
        chmod 600 /home/freeai/.ssh/authorized_keys
    fi
fi

# Also set for root
mkdir -p /root/.ssh
if [ -n "$SSH_KEYS" ]; then
    echo "$SSH_KEYS" > /root/.ssh/authorized_keys
    chmod 700 /root/.ssh
    chmod 600 /root/.ssh/authorized_keys
fi

echo "[$(date -Is)] starting SSH ..."
service ssh restart 2>/dev/null || /usr/sbin/sshd 2>/dev/null || true

# ── Configure TigerVNC ──────────────────────────────────────────
echo "[$(date -Is)] configuring TigerVNC ..."
VNC_DIR="/root/.vnc"
mkdir -p "$VNC_DIR"

# Write VNC password (TigerVNC expects passwd file)
echo "$VNC_PASSWORD" | vncpasswd -f > "$VNC_DIR/passwd" 2>/dev/null || \
    echo "$VNC_PASSWORD" | vncpasswd >/dev/null 2>&1
chmod 600 "$VNC_DIR/passwd"

# xstartup
cat > "$VNC_DIR/xstartup" <<'VNCSTART'
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
export XDG_SESSION_TYPE=x11
exec startxfce4 &
VNCSTART
chmod +x "$VNC_DIR/xstartup"

# Start VNC on display :0 (port 5900)
vncserver :0 -geometry 1920x1080 -depth 24 -localhost no 2>/dev/null || true

# ── Configure noVNC + websockify ────────────────────────────────
echo "[$(date -Is)] configuring noVNC ..."
NOVNC_DIR="/usr/share/novnc"
if [ ! -d "$NOVNC_DIR" ]; then
    NOVNC_DIR="$(dirname "$(command -v vncproxy)" 2>/dev/null)" || NOVNC_DIR="/opt/novnc"
fi

# Ensure noVNC html exists
if [ -f "$NOVNC_DIR/vnc.html" ]; then
    mkdir -p /var/www/novnc
    cp -a "$NOVNC_DIR" /var/www/novnc/ 2>/dev/null || true
fi

# Start websockify forwarding 6080 → 5900
pkill -f 'websockify 6080' 2>/dev/null || true
nohup websockify --web /var/www/novnc 6080 localhost:5900 > /var/log/freeai-websockify.log 2>&1 &
echo "[$(date -Is)] websockify PID: $!"

# ── Firewall rules (ufw / iptables) ────────────────────────────
echo "[$(date -Is)] applying firewall rules ..."
if command -v ufw &>/dev/null; then
    ufw allow 22/tcp 2>/dev/null || true
    ufw allow 5900/tcp 2>/dev/null || true
    ufw allow 6080/tcp 2>/dev/null || true
elif command -v iptables &>/dev/null; then
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT 2>/dev/null || true
    iptables -A INPUT -p tcp --dport 5900 -j ACCEPT 2>/dev/null || true
    iptables -A INPUT -p tcp --dport 6080 -j ACCEPT 2>/dev/null || true
fi

# ── Persist config ──────────────────────────────────────────────
mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_FILE" <<EOF
{
  "ssh": {
    "enabled": true,
    "port": 22,
    "password_set": true,
    "keys_count": $([ -n "$SSH_KEYS" ] && echo "$(echo "$SSH_KEYS" | wc -l)" || echo 0)
  },
   "vnc": {
     "enabled": true,
     "port": 5900,
     "display": 0,
     "password_set": true
   },
  "novnc": {
    "enabled": true,
    "port": 6080,
    "url": "http://localhost:6080/vnc.html?host=localhost&port=6080"
  },
  "setup_at": "$(date -Is)",
  "setup_complete": true
}
EOF

# ── Mark done ───────────────────────────────────────────────────
touch "$FLAG_FILE"
echo "[$(date -Is)] setup complete — flags: $FLAG_FILE  config: $CONFIG_FILE"
echo ""
echo "  SSH:    ssh freeai@<host>  (port 22)"
echo "  VNC:    <host>:5900"
echo "  noVNC:  http://<host>:6080/vnc.html"
echo ""
