---
name: incident-response
description: Security incident handling: triage, containment, forensic capture, report. Use when the user asks about security incidents, breach response, forensic analysis, incident containment, or security reporting.
---

# Incident Response

## Incident Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| SEV-1 | Active data breach, system compromise | 15 min | Ransomware, credential leak |
| SEV-2 | Potential breach, no confirmed impact | 1 hour | Suspicious login, anomalous traffic |
| SEV-3 | Policy violation, low risk | 4 hours | Misconfigured bucket, weak auth |
| SEV-4 | Informational, no risk | 24 hours | Failed attack attempt, phishing test |

## Phase 1: Preparation

```bash
# Required tools
# Forensic: dd, binwalk, volatility, strings
# Network: tcpdump, wireshark, tshark
# Analysis: grep, awk, jq, sqlite3
# Documentation: ticket system, timeline template

# Contact tree
TEAM_LEAD="security-lead@company.com"
INCIDENT_CHANNEL="#incident-response"
ESCALATION_CONTACT="ciso@company.com"
```

## Phase 2: Identification

### Triage Checklist

```
1. What is the incident type?
   [ ] Unauthorized access
   [ ] Malware/Ransomware
   [ ] Data exfiltration
   [ ] DDoS
   [ ] Insider threat
   [ ] Phishing/Social engineering
   [ ] Vulnerability exploitation

2. What systems are affected?
   - List all affected hosts/services
   - Determine scope of blast radius

3. What data is at risk?
   [ ] PII/Personal data
   [ ] Financial data
   [ ] Intellectual property
   [ ] Credentials/secrets
   [ ] System integrity

4. When did it start?
   - First indicator time
   - Last known good state
```

### Log Sources to Preserve

```bash
# Authentication logs
journalctl -u ssh --since "2024-01-01" > /forensics/auth.log
sudo last -a > /forensics/last.log
sudo pamctl status > /forensics/pam.log

# System logs
sudo journalctl --no-pager > /forensics/journal.log
sudo lslogins > /forensics/users.log

# Network logs
sudo tcpdump -w /forensics/packet-capture.pcap -G 3600 -W 24
# Rotate hourly, max 24 files

# Process audit
sudo ps auxf > /forensics/processes.txt
sudo lsof > /forensics/open-files.txt
```

## Phase 3: Containment

### Short-Term Containment

```bash
# Network isolation
iptables -A INPUT -s <attacker_ip> -j DROP
# or
az network nsg rule create --name block-attacker --nsg-name main-nsg \
    --priority 100 --source-address-prefixes "$attacker_ip" --action Deny

# Disable compromised accounts
aws iam update-user --user-name compromised-user --max-session-duration 0
# or
ldapmodify -x -D "cn=admin" -w secret <<EOF
dn: uid=compromised,dc=example,dc=com
changetype: modify
replace: userPassword
userPassword: {SSHA}impossibleto_guess
EOF

# Isolate affected host
virsh destroy <vm-name>
# Preserve RAM state before power off
vmstat -a > /forensics/mem-state.txt
```

### Long-Term Containment

```
- [ ] Firewall rules blocking attacker C2
- [ ] Compromised credentials rotated
- [ ] Affected systems patched
- [ ] Monitoring enhanced on related systems
- [ ] Backup verified and available
```

## Phase 4: Eradication

```bash
# Remove malware
sudo find / -name "*malware*" -type f 2>/dev/null
sudo rm -rf /tmp/.hidden_backdoor

# Kill malicious processes
sudo kill -9 <pid>
sudo pkill -f "suspicious_script.py"

# Remove persistence mechanisms
sudo crontab -l | grep -v "suspicious" | sudo crontab -
sudo systemctl disable suspicious-service
sudo rm /etc/systemd/system/suspicious.service

# Patch vulnerability
sudo apt update && sudo apt upgrade -y
# or
yum update -y
```

## Phase 5: Recovery

```bash
# Restore from clean backup
rsync -avz /backup/clean/ /app/data/
chmod -R 750 /app/data
chown -R appuser:appgroup /app/data

# Verify system integrity
sudo debsums -c  # Debian/Ubuntu package verification
sudo rpm -Va     # RHEL/CentOS package verification
sudo fsck /dev/sda1

# Validate application
python manage.py migrate --check
npm test
pytest tests/ -v
```

## Phase 6: Lessons Learned

### Incident Report Template

```markdown
# Incident Report: [TITLE]

## Summary
[1-2 sentence description of what happened]

## Timeline
| Time (UTC) | Event | Source |
|------------|-------|--------|
| 2024-01-15 03:14 | Initial compromise detected | SIEM alert |
| 2024-01-15 03:17 | First responder notified | PagerDuty |
| 2024-01-15 03:45 | Containment initiated | IR team |
| 2024-01-15 05:00 | Eradication complete | IR team |
| 2024-01-15 06:30 | Recovery verified | IR team |

## Impact
- Systems affected: [list]
- Data exposed: [type and volume]
- Downtime: [duration]
- Financial impact: [estimate]

## Root Cause
[Technical explanation of how the incident occurred]

## Actions Taken
1. [Containment action]
2. [Eradication action]
3. [Recovery action]

## Recommendations
1. [Preventive measure]
2. [Detection improvement]
3. [Process improvement]

## Evidence Preserved
- /forensics/auth.log
- /forensics/packet-capture.pcap
- /forensics/mem-state.txt
- Volatility profile: /forensics/volatility-profile.bin
```

## Communication Templates

### Internal Notification
```
Subject: [SEV-1] Security Incident - [Brief Description]

Team,

A security incident has been identified affecting [systems].
Incident commander: [name]
Status: [active/contained/resolved]
Next update: [time]

Action required: [if any]
Full details: [incident channel/ticket]
```

### External Notification (if required)
```
Subject: Security Incident Notification

We are writing to inform you of a security incident that may
affect your data. We discovered [brief description] on [date].

We have [contained the incident / are working to contain it].
Affected systems: [list]

Recommended actions:
- Change your password
- Enable multi-factor authentication
- Monitor accounts for suspicious activity

Contact: [security email/phone]
```

## Evidence Chain of Custody

```bash
# Record all evidence handling
echo "Evidence: $(basename $file)" >> /forensics/chain-of-custody.log
echo "Date: $(date -u)" >> /forensics/chain-of-custody.log
echo "Handler: $(whoami)" >> /forensics/chain-of-custody.log
echo "Hash: $(sha256sum $file)" >> /forensics/chain-of-custody.log
echo "---" >> /forensics/chain-of-custody.log

# Preserve original hashes
sha256sum /forensics/* > /forensics/evidence-hashes.sha256
```
