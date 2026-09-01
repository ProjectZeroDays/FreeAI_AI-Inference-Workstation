---
name: system-hardening
description: Periodically harden systems against zero-click and zero-day exploits. Triggers when user types "harden my system". Detects OS, applies comprehensive security hardening, configures defenses, and generates verification report. Supports Windows, macOS, and Linux with network and browser hardening. Use when hardening systems, applying security configurations, or defending against zero-click/zero-day exploits.
---

# System Hardening

Harden systems against zero-click and zero-day exploits. Triggers on "harden my system".

## Workflow

### Phase 1: Detection
1. Detect operating system
2. Identify OS version
3. Check current configuration
4. Create backup/restore point

### Phase 2: Assessment
1. Read `references/checklists.md` for pre-hardening checklist
2. Read OS-specific reference:
   - Windows: `references/windows.md`
   - macOS: `references/macos.md`
   - Linux: `references/linux.md`
3. Document current state

### Phase 3: Hardening
1. Apply OS-specific hardening
2. Configure network defenses: `references/network.md`
3. Configure browser security: `references/browser.md`
4. Verify changes

### Phase 4: Verification
1. Run verification commands
2. Test system functionality
3. Generate hardening report
4. Schedule next review

## Quick Start

When user types "harden my system":

```
[SYSTEM-HARDENING] Detecting system...

Detected: [OS] [Version]
Starting hardening process...

Phase 1: System Updates
[Apply updates]

Phase 2: Account Security
[Configure accounts]

Phase 3: Service Hardening
[Disable services]

Phase 4: Network Security
[Configure firewall]

Phase 5: Exploit Protection
[Enable protections]

Phase 6: Audit & Logging
[Enable logging]

Hardening complete. Generating report...
```

## OS-Specific Workflows

### Windows
```powershell
# 1. Updates
Install-Module PSWindowsUpdate -Force
Get-WindowsUpdate -AcceptAll -Install

# 2. ASR Rules
# See references/windows.md

# 3. Exploit Protection
# See references/windows.md

# 4. Credential Guard
# See references/windows.md
```

### macOS
```bash
# 1. Updates
softwareupdate -ia

# 2. SIP
csrutil status

# 3. FileVault
fdesetup status

# 4. Firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
```

### Linux
```bash
# 1. Updates
sudo apt-get update && sudo apt-get upgrade -y

# 2. Kernel hardening
# See references/linux.md

# 3. AppArmor/SELinux
sudo aa-enforce /etc/apparmor.d/*

# 4. SSH hardening
# See references/linux.md
```

## Hardening Categories

| Category | Priority | Reference |
|----------|----------|-----------|
| System Updates | Critical | OS-specific |
| Account Security | Critical | OS-specific |
| Exploit Protection | Critical | windows.md |
| Kernel Hardening | High | linux.md |
| Network Security | High | network.md |
| Browser Security | Medium | browser.md |
| Service Hardening | Medium | OS-specific |
| Audit Logging | Medium | OS-specific |

## Verification Commands

### Windows
```powershell
Get-MpComputerStatus
Get-NetFirewallProfile
Get-ProcessMitigation -System
```

### macOS
```bash
csrutil status
fdesetup status
spctl --status
```

### Linux
```bash
sysctl -a | grep randomize_va_space
sudo aa-status
sudo nft list ruleset
```

## Report Format

```markdown
# System Hardening Report

## System Information
- **OS**: [Detected OS]
- **Version**: [OS Version]
- **Date**: [Hardening Date]

## Changes Applied
| Category | Change | Status |
|----------|--------|--------|
| Updates | Installed | Complete |
| Accounts | Secured | Complete |
| Services | Hardened | Complete |
| Network | Configured | Complete |
| Exploit Protection | Enabled | Complete |

## Verification
- [ ] All checks passed
- [ ] System functional
- [ ] No critical issues

## Next Review
- **Date**: [Date + 30 days]
- **Focus**: [Areas to review]
```

## Scheduling

After hardening, recommend schedule:

| Task | Frequency |
|------|-----------|
| Security updates | Weekly |
| Configuration review | Monthly |
| Full hardening | Quarterly |
| Vulnerability scan | Monthly |
| Access review | Monthly |

## Safety Notes

1. **Backup first**: Always create restore point before hardening
2. **Test changes**: Verify system functionality after each change
3. **Document exceptions**: Record any settings that cannot be applied
4. **Plan rollback**: Know how to undo changes if needed
5. **Gradual approach**: Apply changes incrementally, not all at once

## Troubleshooting

If system becomes unstable:

### Windows
```powershell
# System Restore
Restore-Computer -RestorePoint "Before Hardening"

# Or use safe mode
```

### macOS
```bash
# Reset SIP
# Boot to Recovery Mode
# csrutil disable
```

### Linux
```bash
# Restore sysctl
sudo cp /etc/sysctl.d/99-security.conf.bak /etc/sysctl.d/99-security.conf
sudo sysctl -p

# Restore SSH
sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config
sudo systemctl restart sshd
```
