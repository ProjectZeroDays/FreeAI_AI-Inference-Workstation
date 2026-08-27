---
name: quantum-c2-system-hardening-configurator
description: >
  Quantum C2 system hardening configurator skill. Use when the user asks about system hardening, OS security, or hardening configuration. Triggers on: "system hardening", "OS security", "Linux hardening", "Windows hardening", "macOS hardening", "container hardening", "kernel tuning", "audit configuration", "file integrity".
---

# Quantum C2 System Hardening Configurator

Configure system hardening across Linux, Windows, macOS, and container environments.

## Linux Hardening

### Ubuntu/Debian
```bash
# Get current hardening status
GET /api/hardening/linux/ubuntu/status
```

**Response:**
```json
{
  "os": "Ubuntu 22.04 LTS",
  "kernel": "5.15.0",
  "hardening_score": 72,
  "checks": [
    {"name": "SSH hardening", "status": "pass", "score": 85},
    {"name": "Firewall (UFW)", "status": "pass", "score": 90},
    {"name": "Audit subsystem", "status": "fail", "score": 40},
    {"name": "Kernel parameters", "status": "warning", "score": 65}
  ]
}
```

### Harden Ubuntu
```bash
POST /api/hardening/linux/ubuntu/harden
{
  "level": "hardened",
  "apply_immediately": true
}
```

**Applied Settings:**
- SSH: Disable root login, key-only auth, change port
- Firewall: Default deny, allow only essential ports
- Audit: Enable auditd, configure rules
- Kernel: Sysctl hardening parameters
- PAM: Strong password policies
- File permissions: Secure /tmp, /var/tmp
- Syslog: Centralized logging
- Unattended upgrades: Automatic security updates

### Kali Linux
```bash
POST /api/hardening/linux/kali/harden
{
  "level": "balanced",
  "preserve_tools": true
}
```

**Note:** Kali hardening preserves security tools while hardening the base system.

## Windows Hardening

### Get Status
```bash
GET /api/hardening/windows/status
```

**Response:**
```json
{
  "os": "Windows 11 Pro",
  "build": "22621",
  "hardening_score": 65,
  "checks": [
    {"name": "Windows Firewall", "status": "pass", "score": 90},
    {"name": "UAC", "status": "pass", "score": 80},
    {"name": "Password policy", "status": "fail", "score": 30},
    {"name": "Windows Update", "status": "warning", "score": 70}
  ]
}
```

### Harden Windows
```bash
POST /api/hardening/windows/harden
{
  "level": "hardened",
  "apply_immediately": true
}
```

**Applied Settings:**
- Firewall: Enable, default deny inbound
- UAC: Maximum prompts
- Password policy: Complex, 14+ characters
- Windows Update: Automatic security updates
- PowerShell: Constrained language mode
- SMB: Disable SMBv1, enable SMB signing
- RDP: NLA required, disable guest
- LAPS: Local admin password solution
- Attack surface reduction rules
- Defender real-time protection

## macOS Hardening

### Get Status
```bash
GET /api/hardening/macos/status
```

### Harden macOS
```bash
POST /api/hardening/macos/harden
{
  "level": "hardened"
}
```

**Applied Settings:**
- FileVault: Enable full disk encryption
- Firewall: Enable blocking incoming connections
- SIP: Verify enabled
- Gatekeeper: Strict mode
- Privacy: Location services restricted
- Screensaver: Require password
- Sharing: Disable unnecessary services
- Sudo: Require password, timeout 5 min
- SIP lockdown
- TCC database hardened

## Container Hardening

### Docker
```bash
# Get Docker security status
GET /api/hardening/docker/status

# Harden Docker
POST /api/hardening/docker/harden
{
  "level": "hardened"
}
```

**Applied Settings:**
- No root containers
- Read-only root filesystem
- Drop all capabilities
- Seccomp profiles
- AppArmor profiles
- Network isolation
- Resource limits
- No privileged containers

### Kubernetes
```bash
# Get K8s security status
GET /api/hardening/kubernetes/status

# Harden Kubernetes
POST /api/hardening/kubernetes/harden
{
  "level": "hardened"
}
```

**Applied Settings:**
- Pod security policies (restricted)
- Network policies default deny
- RBAC least privilege
- Admission controllers
- Image scanning
- Runtime security
- Audit logging
- Secrets encryption

## Service Hardening

### Apache
```bash
POST /api/hardening/service/apache
{
  "level": "hardened"
}
```

### Nginx
```bash
POST /api/hardening/service/nginx
{
  "level": "hardened"
}
```

### SSH
```bash
POST /api/hardening/service/ssh
{
  "level": "hardened",
  "port": 2222,
  "permit_root": false,
  "password_auth": false
}
```

### MySQL
```bash
POST /api/hardening/service/mysql
{
  "level": "hardened",
  "bind_address": "127.0.0.1",
  "remove_test_db": true
}
```

### PostgreSQL
```bash
POST /api/hardening/service/postgresql
{
  "level": "hardened",
  "bind_address": "127.0.0.1"
}
```

## Kernel Parameter Tuning

### Get Current Parameters
```bash
GET /api/hardening/kernel/parameters
```

### Harden Kernel
```bash
POST /api/hardening/kernel/harden
{
  "level": "hardened"
}
```

**Applied Parameters:**
```
net.ipv4.ip_forward = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_source_route = 0
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
kernel.randomize_va_space = 2
fs.suid_dumpable = 0
```

## Audit Configuration

### Linux Audit
```bash
# Get audit status
GET /api/hardening/audit/linux/status

# Configure audit
POST /api/hardening/audit/linux/config
{
  "enabled": true,
  "log_path": "/var/log/audit/audit.log",
  "max_log_file": 100,
  "action_on_max_log": "syscall",
  "rules": [
    "-w /etc/passwd -p wa -k identity",
    "-w /etc/shadow -p wa -k identity",
    "-w /etc/sudoers -p wa -k privilege",
    "-w /usr/bin/sudo -p x -k privilege"
  ]
}
```

### Windows Audit
```bash
# Configure Windows audit
POST /api/hardening/audit/windows/config
{
  "audit_policy": "advanced",
  "log_on_failure": true,
  "log_on_success": true,
  "categories": ["logon", "privilege_use", "object_access", "policy_change"]
}
```

## Logging Configuration

### Syslog
```bash
POST /api/hardening/logging/syslog
{
  "remote_server": "syslog.example.com",
  "remote_port": 514,
  "protocol": "tcp",
  "tls": true,
  "filter": ["auth", "daemon", "syslog"]
}
```

### Windows Event Log
```bash
POST /api/hardening/logging/windows
{
  "max_size_mb": 100,
  "overwrite_policy": "never",
  "retention_days": 365,
  "enable_audit_logging": true
}
```

## File Integrity Monitoring

### AIDE Configuration
```bash
POST /api/hardening/fim/aide
{
  "enabled": true,
  "database_path": "/var/lib/aide",
  "scan_schedule": "0 3 * * *",
  "alert_email": "admin@example.com",
  "monitor_paths": [
    "/etc",
    "/bin",
    "/sbin",
    "/usr/bin",
    "/usr/sbin"
  ]
}
```

### OSSEC Configuration
```bash
POST /api/hardening/fim/ossec
{
  "enabled": true,
  "local_monitoring": true,
  "rootcheck": true,
  "syscheck": {
    "frequency": 43200,
    "directories": ["/etc", "/usr", "/bin"]
  }
}
```

## Security Scanning

### Vulnerability Scan
```bash
GET /api/hardening/scan/vulnerabilities
```

### Compliance Check
```bash
POST /api/hardening/compliance/check
{
  "framework": "cis",
  "level": "1"
}
```

### Security Score
```bash
GET /api/hardening/security-score
```

**Response:**
```json
{
  "overall_score": 78,
  "categories": {
    "network": 85,
    "host": 72,
    "application": 80,
    "data": 70,
    "identity": 82
  }
}
```

## API Reference

### Linux
```
GET    /api/hardening/linux/ubuntu/status
POST   /api/hardening/linux/ubuntu/harden
POST   /api/hardening/linux/kali/harden
```

### Windows
```
GET    /api/hardening/windows/status
POST   /api/hardening/windows/harden
```

### macOS
```
GET    /api/hardening/macos/status
POST   /api/hardening/macos/harden
```

### Containers
```
GET    /api/hardening/docker/status
POST   /api/hardening/docker/harden
GET    /api/hardening/kubernetes/status
POST   /api/hardening/kubernetes/harden
```

### Services
```
POST   /api/hardening/service/apache
POST   /api/hardening/service/nginx
POST   /api/hardening/service/ssh
POST   /api/hardening/service/mysql
POST   /api/hardening/service/postgresql
```

### Kernel
```
GET    /api/hardening/kernel/parameters
POST   /api/hardening/kernel/harden
```

### Audit
```
GET    /api/hardening/audit/linux/status
POST   /api/hardening/audit/linux/config
POST   /api/hardening/audit/windows/config
```

### Logging
```
POST   /api/hardening/logging/syslog
POST   /api/hardening/logging/windows
```

### FIM
```
POST   /api/hardening/fim/aide
POST   /api/hardening/fim/ossec
```

### Scan
```
GET    /api/hardening/scan/vulnerabilities
POST   /api/hardening/compliance/check
GET    /api/hardening/security-score
```

## Workflows

### Full System Hardening
```bash
# 1. Check current status
curl http://localhost:8000/api/hardening/security-score

# 2. Harden Linux
curl -X POST http://localhost:8000/api/hardening/linux/ubuntu/harden \
  -H "Content-Type: application/json" \
  -d '{"level": "hardened"}'

# 3. Harden SSH
curl -X POST http://localhost:8000/api/hardening/service/ssh \
  -H "Content-Type: application/json" \
  -d '{"level": "hardened"}'

# 4. Harden kernel
curl -X POST http://localhost:8000/api/hardening/kernel/harden \
  -H "Content-Type: application/json" \
  -d '{"level": "hardened"}'

# 5. Configure audit
curl -X POST http://localhost:8000/api/hardening/audit/linux/config \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "rules": ["-w /etc/passwd -p wa -k identity"]}'

# 6. Enable FIM
curl -X POST http://localhost:8000/api/hardening/fim/aide \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# 7. Verify
curl http://localhost:8000/api/hardening/security-score
```

## Best Practices

1. **Baseline first** — Check current state before hardening
2. **Document changes** — Track all modifications
3. **Test in staging** — Validate before production
4. **Update regularly** — Keep up with security patches
5. **Monitor compliance** — Regular audits
6. **Least privilege** — Minimal required access
7. **Defense in depth** — Multiple security layers
8. **Automate** — Schedule regular hardening

## Troubleshooting

### Hardening Failed
```bash
# Check logs
curl http://localhost:8000/api/hardening/logs

# Get error details
curl http://localhost:8000/api/hardening/errors
```

### Service Not Starting
```bash
# Check service status
curl http://localhost:8000/api/hardening/services/status

# Restart service
curl -X POST http://localhost:8000/api/hardening/services/restart \
  -d '{"service": "ssh"}'
```

### Rollback Changes
```bash
# Generate backup
curl -X POST http://localhost:8000/api/hardening/backup/create

# Rollback
curl -X POST http://localhost:8000/api/hardening/rollback \
  -d '{"backup_id": "backup-001"}'
```
