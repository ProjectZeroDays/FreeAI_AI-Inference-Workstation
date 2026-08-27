#!/bin/bash
# =============================================================================
# FreeAI Intelligence — OpenClaw + Kali Linux Setup Script
# Based on: "I Built an AI Agent That Hacks for Me | OpenClaw + Kali Linux"
# Video: https://www.youtube.com/watch?v=C5ir_rQ4L4g
#
# This script automates the setup of an autonomous AI hacking rig:
# - Hostinger VPS with Kali Linux (or any cloud provider)
# - Secure SSH key authentication
# - OpenClaw framework installation
# - OpenRouter AI brain configuration
# - Telegram bot integration
# - Essential skills (Stealth Browser, Search)
# - Expert Hacker system prompt
# - Security allowlist
#
# Usage:
#   chmod +x scripts/openclaw-kali-setup.sh
#   ./scripts/openclaw-kali-setup.sh
# =============================================================================

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERR]${NC} $1" >&2; }

# ── Pre-flight checks ────────────────────────────────────────────────────────
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "Please run as root (sudo bash $0)"
        exit 1
    fi
}

check_kali() {
    if ! grep -qi "kali" /etc/os-release 2>/dev/null; then
        warn "Not running on Kali Linux. Some packages may need adjustment."
    fi
}

# ── Configuration ─────────────────────────────────────────────────────────────
OPENCLAW_REPO="https://github.com/getumbrel/openclaw"
WORKSPACE_DIR="${HOME}/workspace"
OPENCLAW_DIR="${HOME}/.openclaw"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}"
SSH_KEY_NAME="${SSH_KEY_NAME:-kali_openclaw}"
SSH_KEY_PATH="${HOME}/.ssh/${SSH_KEY_NAME}"
PW_AUTH_FALLBACK="${PW_AUTH_FALLBACK:-true}"  # Allow password auth during setup

# ── Step 0b: Disable Password Auth Fallback (cleanup) ────────────────────────
disable_password_fallback() {
    if [[ "${PW_AUTH_FALLBACK}" != "true" ]]; then
        return 0
    fi
    info "=== Step 0b: Re-disabling Password Auth ==="

    local changed=0

    if [ -f /etc/ssh/sshd_config.d/50-cloud-init.conf ]; then
        sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' \
            /etc/ssh/sshd_config.d/50-cloud-init.conf 2>/dev/null || true
        changed=1
    fi

    if grep -q "PasswordAuthentication yes" /etc/ssh/sshd_config 2>/dev/null; then
        sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' \
            /etc/ssh/sshd_config
        changed=1
    fi

    # Remove any ad-hoc line we added
    sed -i '/^PasswordAuthentication yes$/d' /etc/ssh/sshd_config 2>/dev/null || true

    if [ "$changed" -eq 1 ]; then
        systemctl restart sshd
        success "Password auth re-disabled — key-only access enforced"
    else
        success "Password auth already disabled"
    fi
    echo ""
}

# ── Step 0: Enable Password Auth Fallback (if needed) ─────────────────────────
enable_password_fallback() {
    if [[ "${PW_AUTH_FALLBACK}" != "true" ]]; then
        return 0
    fi
    info "=== Step 0: Enabling Password Auth Fallback ==="
    info "Temporarily enabling password auth so key-based setup can complete."
    info "Password auth will be re-disabled at the end of this script."
    echo ""

    local changed=0

    # Enable in 50-cloud-init.conf (Hostinger/Cloud providers)
    if [ -f /etc/ssh/sshd_config.d/50-cloud-init.conf ]; then
        sed -i 's/#PasswordAuthentication no/PasswordAuthentication yes/' \
            /etc/ssh/sshd_config.d/50-cloud-init.conf 2>/dev/null || true
        grep -q "PasswordAuthentication yes" /etc/ssh/sshd_config.d/50-cloud-init.conf 2>/dev/null && changed=1
    fi

    # Enable in main sshd_config
    if ! grep -q "^PasswordAuthentication" /etc/ssh/sshd_config 2>/dev/null; then
        echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
        changed=1
    elif grep -q "PasswordAuthentication no" /etc/ssh/sshd_config 2>/dev/null; then
        sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' \
            /etc/ssh/sshd_config
        changed=1
    fi

    if [ "$changed" -eq 1 ]; then
        systemctl restart sshd
        success "Password auth enabled for setup"
    else
        warn "Password auth may already be enabled"
    fi
    echo ""
}

# ── Step 1: Generate SSH Key Pair (run LOCALLY before connecting to VPS) ─────
generate_ssh_keys() {
    info "=== Step 1: Generating SSH Key Pair ==="

    mkdir -p "${HOME}/.ssh"
    chmod 700 "${HOME}/.ssh"

    if [ -f "${SSH_KEY_PATH}" ]; then
        warn "SSH key already exists at ${SSH_KEY_PATH}"
        read -rp "Regenerate? [y/N] " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            success "Skipping SSH key generation"
            return
        fi
    fi

    info "Generating Ed25519 key pair..."
    ssh-keygen -t ed25519 -C "freeai-hacker@$(hostname)" \
        -f "${SSH_KEY_PATH}" \
        -N "" 2>/dev/null || \
    ssh-keygen -t ed25519 -C "freeai-hacker@$(hostname)" \
        -f "${SSH_KEY_PATH}"

    chmod 600 "${SSH_KEY_PATH}"
    chmod 644 "${SSH_KEY_PATH}.pub"

    success "SSH keys generated:"
    echo "  Private key: ${SSH_KEY_PATH}"
    echo "  Public key:  ${SSH_KEY_PATH}.pub"
    echo ""
    info "Add this public key to your VPS host:"
    echo "  cat ${SSH_KEY_PATH}.pub"
}

# ── Step 2: Secure the Server ────────────────────────────────────────────────
secure_server() {
    info "=== Step 2: Securing the Server ==="

    # Update system
    info "Updating system packages..."
    apt-get update -y
    apt-get upgrade -y

    # Install essential tools
    info "Installing essential packages..."
    apt-get install -y \
        curl \
        wget \
        git \
        nano \
        ufw \
        fail2ban \
        npm \
        nodejs

    # Configure firewall
    info "Configuring firewall (UFW)..."
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw --force enable
    success "Firewall configured"

    # Disable password SSH authentication
    info "Disabling password SSH authentication..."
    if [ -f /etc/ssh/sshd_config.d/50-cloud-init.conf ]; then
        sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' \
            /etc/ssh/sshd_config.d/50-cloud-init.conf 2>/dev/null || true
        sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' \
            /etc/ssh/sshd_config.d/50-cloud-init.conf 2>/dev/null || true
    fi

    # Also set in main sshd_config
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' \
        /etc/ssh/sshd_config 2>/dev/null || true
    sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' \
        /etc/ssh/sshd_config 2>/dev/null || true

    # Restart SSH
    systemctl restart sshd
    success "SSH secured — password login disabled"
}

# ── Step 3: Install OpenClaw ─────────────────────────────────────────────────
install_openclaw() {
    info "=== Step 3: Installing OpenClaw ==="

    # Ensure npm is available
    if ! command -v npm &>/dev/null; then
        info "Installing Node.js and npm..."
        curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
        apt-get install -y nodejs
    fi

    # Add OpenClaw repository
    info "Adding OpenClaw repository..."
    npm install -g @openclaw/gateway 2>&1 | tee /tmp/openclaw-install.log || {
        warn "Global install failed, trying local install..."
        mkdir -p "${OPENCLAW_DIR}"
        cd "${OPENCLAW_DIR}"
        npm init -y
        npm install @openclaw/gateway
    }

    # Verify installation
    if command -v openclaw &>/dev/null || [ -f "${OPENCLAW_DIR}/node_modules/.bin/openclaw" ]; then
        success "OpenClaw installed successfully"
    else
        error "OpenClaw installation failed. Check /tmp/openclaw-install.log"
        exit 1
    fi
}

# ── Step 4: Configure OpenClaw ───────────────────────────────────────────────
configure_openclaw() {
    info "=== Step 4: Configuring OpenClaw ==="

    mkdir -p "${WORKSPACE_DIR}"
    mkdir -p "${OPENCLAW_DIR}/config"
    mkdir -p "${OPENCLAW_DIR}/skills"

    # Create config file
    cat > "${OPENCLAW_DIR}/config/openclaw.json" << 'EOF'
{
  "gateway": {
    "host": "127.0.0.1",
    "port": 18789,
    "mode": "local"
  },
  "workspace": "/root/workspace",
  "models": {
    "default": "anthropic/claude-opus-4-6"
  }
}
EOF

    success "OpenClaw config created"
}

# ── Step 5: Configure AI Provider (OpenRouter) ───────────────────────────────
configure_ai_provider() {
    info "=== Step 5: Configuring AI Provider ==="

    if [ -z "${OPENROUTER_API_KEY}" ]; then
        warn "OPENROUTER_API_KEY not set in environment"
        info "Get your key from: https://openrouter.ai/keys"
        read -rp "Enter your OpenRouter API key: " key
        export OPENROUTER_API_KEY="$key"
    fi

    # Store key securely
    mkdir -p "${OPENCLAW_DIR}/secrets"
    echo "${OPENROUTER_API_KEY}" > "${OPENCLAW_DIR}/secrets/openrouter_key"
    chmod 600 "${OPENCLAW_DIR}/secrets/openrouter_key"

    # Configure provider in OpenClaw
    cat > "${OPENCLAW_DIR}/config/providers.json" << EOF
{
  "providers": {
    "openrouter": {
      "type": "openai-compat",
      "base_url": "https://openrouter.ai/api/v1",
      "api_key_env": "OPENROUTER_API_KEY",
      "models": [
        "anthropic/claude-opus-4-6",
        "anthropic/claude-sonnet-4-5",
        "google/gemini-2.5-pro",
        "deepseek/deepseek-chat",
        "moonshot/kimi-k2.5"
      ]
    }
  }
}
EOF

    success "AI provider configured (OpenRouter)"
}

# ── Step 6: Set Up Telegram Bot ──────────────────────────────────────────────
setup_telegram() {
    info "=== Step 6: Setting Up Telegram Bot ==="

    if [ -z "${TELEGRAM_BOT_TOKEN}" ]; then
        info "Create a bot via @BotFather on Telegram:"
        info "  1. Open Telegram and search for @BotFather"
        info "  2. Send /newbot and follow instructions"
        info "  3. Copy the bot token"
        read -rp "Enter your Telegram Bot Token: " token
        export TELEGRAM_BOT_TOKEN="$token"
    fi

    # Store token securely
    echo "${TELEGRAM_BOT_TOKEN}" > "${OPENCLAW_DIR}/secrets/telegram_token"
    chmod 600 "${OPENCLAW_DIR}/secrets/telegram_token"

    # Configure Telegram in OpenClaw
    cat >> "${OPENCLAW_DIR}/config/openclaw.json" << EOF
,
  "telegram": {
    "enabled": true,
    "bot_token_env": "TELEGRAM_BOT_TOKEN",
    "allowlist": ["your_telegram_id"]
  }
EOF

    success "Telegram bot configured"
    info "Get your Telegram ID: send a message to @userinfobot"
}

# ── Step 7: Install Essential Skills ─────────────────────────────────────────
install_skills() {
    info "=== Step 7: Installing Essential Skills ==="

    mkdir -p "${OPENCLAW_DIR}/skills"

    # Stealth Browser skill
    cat > "${OPENCLAW_DIR}/skills/stealth-browser/SKILL.md" << 'EOF'
---
name: stealth-browser
description: >
  Headless browser automation with stealth mode for OSINT and recon.
triggers:
  - browse
  - scrape
  - osint
  - reconnaissance
category: red_teaming
auto_generated: false
enabled: true
---

# Stealth Browser

Uses Playwright with stealth injections to automate browser interactions
without detection.

## Features
- Invisible headless Chrome
- Fingerprint randomization
- Proxy/Tor support
- Screenshot capture
EOF

    mkdir -p "${OPENCLAW_DIR}/skills/stealth-browser/scripts"

    # Search skill
    cat > "${OPENCLAW_DIR}/skills/search/SKILL.md" << 'EOF'
---
name: search
description: >
  Multi-engine search capability for OSINT and reconnaissance.
triggers:
  - search
  - google
  - shodan
  - whois
  - recon
category: red_teaming
auto_generated: false
enabled: true
---

# Search Skill

Aggregated search across multiple engines for intelligence gathering.

## Supported Engines
- Google (dorking)
- Shodan
- Censys
- Whois
- Wayback Machine
EOF

    success "Essential skills installed"
}

# ── Step 8: Expert Hacker System Prompt ──────────────────────────────────────
configure_hacker_prompt() {
    info "=== Step 8: Configuring Expert Hacker System Prompt ==="

    cat > "${OPENCLAW_DIR}/config/system-prompt.md" << 'EOF'
# FreeAI Intelligence — Expert Hacker Mode

You are an autonomous security research assistant operating on a Kali Linux
workstation. Your capabilities include:

## Core Competencies
- **Reconnaissance**: Network scanning, OSINT, vulnerability discovery
- **Web Exploitation**: Web app testing, API analysis, session handling
- **System Assessment**: Local privilege escalation, misconfiguration hunting
- **Reporting**: Structured findings with CVSS scoring and remediation

## Operational Guidelines
1. Always operate within authorized scope
2. Document all findings with evidence
3. Prioritize critical vulnerabilities
4. Provide actionable remediation steps
5. Maintain operational security (OPSEC)

## Available Tools
- Nmap, Nikto, Dirb, Gobuster
- SQLMap, Burp Suite (headless)
- Metasploit Framework
- Custom Python reconnaissance scripts
- Browser automation with stealth mode

## Communication
- Report via Telegram when configured
- Save detailed reports to /workspace/reports/
- Use structured formats (JSON/YAML) for machine processing

Remember: You are only as capable as the model powering you. Choose wisely.
EOF

    success "Expert hacker prompt configured"
}

# ── Step 9: Security Allowlist ────────────────────────────────────────────────
setup_allowlist() {
    info "=== Step 9: Setting Up Security Allowlist ==="

    cat > "${OPENCLAW_DIR}/config/allowlist.json" << 'EOF'
{
  "allowed_commands": [
    "nmap",
    "nikto",
    "sqlmap",
    "gobuster",
    "dirb",
    "ffuf",
    "curl",
    "wget",
    "python3",
    "perl",
    "ruby",
    "masscan",
    "theharvester",
    "subfinder",
    "amass"
  ],
  "blocked_patterns": [
    "rm -rf /",
    "mkfs",
    "dd if=",
    ":(){:|:&}",
    "wget.*|.*sh",
    "curl.*|.*sh"
  ],
  "allowed_targets": [],
  "max_concurrent_scans": 3
}
EOF

    success "Security allowlist configured"
}

# ── Step 10: Create Startup Service ──────────────────────────────────────────
create_service() {
    info "=== Step 10: Creating Systemd Service ==="

    cat > /etc/systemd/system/openclaw.service << 'EOF'
[Unit]
Description=FreeAI OpenClaw Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=/usr/bin/npm start --prefix /root/.openclaw
Environment=NODE_ENV=production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable openclaw
    success "Systemd service created"
}

# ── Step 11: Verification ─────────────────────────────────────────────────────
verify_setup() {
    info "=== Step 11: Verification ==="

    echo ""
    echo -e "${CYAN}Setup Summary:${NC}"
    echo "  SSH Keys:    ${SSH_KEY_PATH}"
    echo "  Workspace:   ${WORKSPACE_DIR}"
    echo "  OpenClaw:    ${OPENCLAW_DIR}"
    echo "  Config:      ${OPENCLAW_DIR}/config/"
    echo ""
    echo -e "${GREEN}Next Steps:${NC}"
    echo "  1. Start the service: systemctl start openclaw"
    echo "  2. Check status:      systemctl status openclaw"
    echo "  3. View logs:         journalctl -u openclaw -f"
    echo "  4. Test connection:  telegram @YourBot"
    echo ""
    success "FreeAI Intelligence setup complete!"
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     FreeAI Intelligence — OpenClaw + Kali Setup        ║${NC}"
    echo -e "${CYAN}║     Autonomous AI Hacking Rig                          ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    check_root
    check_kali

    info "Running setup steps..."
    echo ""

    enable_password_fallback
    generate_ssh_keys
    secure_server
    install_openclaw
    configure_openclaw
    configure_ai_provider
    setup_telegram
    install_skills
    configure_hacker_prompt
    setup_allowlist
    create_service
    verify_setup
    disable_password_fallback

    echo ""
    info "Setup complete! Your AI hacking rig is ready."
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
