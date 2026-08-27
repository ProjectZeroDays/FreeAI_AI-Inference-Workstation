# OpenClaw + Kali Linux Setup Guide
**Source:** [YouTube Video](https://www.youtube.com/watch?v=C5ir_rQ4L4g) by zSecurity (Ace from CC Security)

> **Disclaimer:** This guide is for educational purposes only. Only test systems you own or have explicit permission to test. Unauthorized access to computer systems is illegal.

## Overview

This guide shows you how to build a fully autonomous AI hacking rig using **OpenClaw** running on a **Kali Linux** cloud server. The agent can be controlled via **Telegram** and has access to professional security tools like Nmap, Metasploit, and web browsers.

## Architecture

```
Your Phone (Telegram) 
       ↓
OpenClaw Agent (Kali Linux VPS)
       ↓
AI Brain (OpenRouter → Claude/DeepSeek/Gemini)
       ↓
Tools Available:
├── Nmap (Network scanning)
├── Metasploit (Exploitation framework)
├── TheHarvester (OSINT)
├── Sublist3r (Subdomain enumeration)
├── SQLMap (SQL injection)
├── Nikto (Web scanning)
├── Dirb (Directory brute-forcing)
├── John the Ripper (Password cracking)
├── Hashcat (Advanced password cracking)
├── Aircrack-ng (WiFi security)
├── Wireshark (Packet analysis)
└── Stealth Browser (Anti-detection web automation)
```

## Step-by-Step Setup

### Step 1: Provision Cloud VPS (Hostinger)

**Recommended Plan:** Hostinger KVM 2
- **Price:** ~$7/month (use coupon `ZSECURITY` for extra 10% off)
- **Specs:** 8GB RAM, 2 vCPU, 160GB SSD
- **OS:** Kali Linux (one-click install)

**Alternative providers:** AWS, DigitalOcean, Vultr, Linode (any cloud with Kali image)

**Setup process:**
1. Go to [Hostinger](https://www.hostinger.com/zsecurity) (affiliate link)
2. Select **KVM 2** plan ($7/mo)
3. Choose **12-month** billing for best price
4. Enter coupon: `ZSECURITY`
5. Select **Kali Linux** as operating system
6. Complete checkout

### Step 2: Generate SSH Keys

On your local machine (Windows/Mac/Linux):

```bash
# Generate Ed25519 key pair
ssh-keygen -t ed25519 -C "kali-openclaw"

# Name your key file (e.g., kali_openclaw)
# Set a strong passphrase (recommended)

# View public key to add to Hostinger
cat ~/.ssh/kali_openclaw.pub
```

**During Hostinger setup:**
1. Click "Add new SSH key"
2. Paste the public key content
3. Name it "kali-openclaw"
4. Save and finish

### Step 3: Connect to Your VPS

```bash
# SSH into your Kali machine
ssh -i ~/.ssh/kali_openclaw root@<YOUR_VPS_IP>

# Accept the host key fingerprint
# Enter your SSH key passphrase if set
```

### Step 4: Run the Setup Script

```bash
# Download the setup script
curl -O https://raw.githubusercontent.com/ProjectZeroDays/unified-ai-stack/main/scripts/setup-openclaw-kali.sh

# Make it executable
chmod +x setup-openclaw-kali.sh

# Run as root
sudo ./setup-openclaw-kali.sh
```

The script will:
1. ✅ Update system packages
2. ✅ Install security tools (Nmap, Metasploit, etc.)
3. ✅ Generate SSH keys (if needed)
4. ✅ Harden the server (SSH config, fail2ban, UFW)
5. ✅ Install OpenClaw framework
6. ✅ Configure OpenRouter API
7. ✅ Set up Telegram bot integration
8. ✅ Configure allowlist security
9. ✅ Install essential skills
10. ✅ Create systemd service

### Step 5: Configure OpenRouter (AI Brain)

During setup, you'll be prompted for your OpenRouter API key:

1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up / Log in
3. Navigate to **Keys** section
4. Create a new API key (name it "openclaw")
5. Copy the key (starts with `sk-or-v1-...`)
6. Paste it into the setup script

**Recommended models:**
- `anthropic/claude-3.5-sonnet` — Best for complex tasks
- `google/gemini-2.0-flash-001` — Fast and cost-effective
- `deepseek/deepseek-chat` — Budget option

### Step 6: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g., "Neo")
4. Choose a username (must end in `bot`, e.g., `neo_hacker_bot`)
5. **Copy the API token** provided
6. Paste it into the setup script

### Step 7: Set Up Allowlist

To prevent unauthorized access:

1. Find your Telegram User ID:
   - Message **@userinfobot** on Telegram
   - It will reply with your numeric ID
   
2. Enter your User ID when prompted by the setup script

Only this ID can control the agent.

### Step 8: Install Skills

The setup script installs these essential skills:

| Skill | Purpose |
|-------|---------|
| **stealth_browser** | Bypass Cloudflare, CAPTCHAs, bot detection |
| **search_osint** | OSINT gathering (Shodan, Censys, Google dorks) |
| **nmap_recon** | Network scanning and enumeration |
| **metasploit** | Exploitation framework integration |

**⚠️ Security Note:** 12% of skills on ClawHub were malicious. Always:
- Scan skills before installing
- Verify source reputation
- Use the skill-scanning capability

### Step 9: Configure Expert Hacker Prompt

The system prompt is configured for ethical hacking:

```markdown
# Expert Hacker System Prompt

You are an autonomous ethical hacking agent operating in a 
controlled, authorized environment.

## Rules of Engagement
- ONLY target systems with explicit permission
- NEVER access systems outside authorized scope
- ALWAYS maintain professional conduct
- DOCUMENT all actions taken
- REPORT findings promptly
```

### Step 10: Start the Agent

```bash
# Start the OpenClaw service
sudo systemctl start openclaw

# Check status
sudo systemctl status openclaw

# View logs in real-time
sudo journalctl -u openclaw -f
```

## Usage Examples

### Example 1: Find CCTV Cameras (OSINT)

Message your bot:
> "Find public CCTV cameras in downtown Portland using OSINT techniques"

The agent will:
1. Search public camera directories (Insecam, etc.)
2. Use geolocation data
3. Cross-reference with social media
4. Compile a report with links

### Example 2: Vulnerability Scan

Message your bot:
> "Scan target.com for vulnerabilities using Nmap and Nikto"

The agent will:
1. Run Nmap reconnaissance
2. Execute Nikto web scan
3. Analyze results
4. Generate vulnerability report

### Example 3: Multi-Agent Operation

Message your bot:
> "Spawn a sub-agent to perform depth recon on example.com while you test for SQL injection"

The agent will:
1. Delegate recon to sub-agent
2. Run SQLMap against target
3. Correlate findings
4. Provide unified report

## Security Best Practices

### 1. Keep Your VPS Secure
```bash
# Regular updates
apt-get update && apt-get upgrade -y

# Check fail2ban status
fail2ban-client status

# Review UFW rules
ufw status verbose
```

### 2. Monitor Agent Activity
```bash
# View logs
journalctl -u openclaw -f --since "1 hour ago"

# Check running processes
ps aux | grep openclaw

# Monitor network connections
netstat -tulpn | grep python
```

### 3. Backup Configuration
```bash
# Backup workspace
tar -czf openclaw-backup-$(date +%Y%m%d).tar.gz ~/openclaw-workspace/

# Store securely
scp openclaw-backup-*.tar.gz local-machine:/backups/
```

### 4. Rotate Credentials
- Rotate OpenRouter API keys monthly
- Regenerate SSH keys annually
- Update Telegram bot token if compromised

## Troubleshooting

### Agent won't start
```bash
# Check service status
sudo systemctl status openclaw

# View detailed logs
sudo journalctl -u openclaw -n 100 --no-pager

# Test configuration
cd /opt/openclaw && source venv/bin/activate && python -m openclaw --test-config
```

### Telegram bot not responding
1. Verify bot token is correct
2. Check allowlist includes your User ID
3. Ensure bot is started: `/start` the bot in Telegram
4. Review logs: `journalctl -u openclaw -f`

### Tools not found
```bash
# Reinstall security tools
apt-get install --reinstall nmap metasploit-framework sqlmap

# Verify paths
which nmap
which msfconsole
```

### High CPU/Memory usage
```bash
# Check resource usage
htop

# Limit concurrent agents in config.yaml
max_concurrent_agents: 2

# Restart service
sudo systemctl restart openclaw
```

## Cost Estimate

| Component | Monthly Cost |
|-----------|-------------|
| Hostinger KVM 2 VPS | $7.00 |
| OpenRouter API (Claude) | ~$5-20* |
| **Total** | **~$12-27** |

*Varies by usage. Free models available but less capable.

## Resources

- **OpenClaw GitHub:** https://github.com/openclaw/openclaw
- **OpenRouter:** https://openrouter.ai
- **Hostinger (affiliate):** https://www.hostinger.com/zsecurity
- **zSecurity Courses:** https://zsecurity.org/courses/
- **ClawHub Skills:** https://clawhub.com

## Legal Considerations

✅ **DO:**
- Test systems you own
- Get written permission for authorized testing
- Use in educational/capture-the-flag contexts
- Report vulnerabilities responsibly

❌ **DON'T:**
- Access systems without permission
- Test on production environments without authorization
- Use for malicious purposes
- Share credentials or access tokens

## Next Steps

1. **Join the community:** https://zsecurity.org/community
2. **Take the Hacking Masterclass:** https://zsecurity.org/courses/masterclass-membership
3. **Explore more tools:** Check the full toolkit list in the video description
4. **Share responsibly:** Like and share if you found this helpful!

---

**Video Timestamps:**
- 0:00 - Intro: Finding CCTV cameras with AI
- 0:27 - What is OpenClaw?
- 1:35 - Why we run this on Kali Linux
- 2:12 - Setting up the Cloud VPS
- 3:57 - Creating Secure SSH Keys
- 5:15 - Connecting to your Cloud Kali Machine
- 6:06 - Securing your Server
- 7:44 - Installing OpenClaw
- 8:34 - Configuring OpenClaw
- 9:20 - Connecting the AI Brain (OpenRouter Setup)
- 11:50 - Linking to Telegram (Creating the Bot)
- 13:14 - Security: Setting up the Allowlist
- 14:15 - Waking up the Agent & First Prompt
- 15:35 - Installing Essential Skills (Stealth Browser & Search)
- 17:35 - The "Expert Hacker" System Prompt
- 19:00 - Demo 1: Locating CCTV Cameras
- 19:50 - Demo 2: Automated OSINT & Vulnerability Scanning
- 22:50 - Reviewing the Hacking Reports
- 24:15 - Conclusion & Next Steps
