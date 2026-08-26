---
name: backup-restore
description: Backup and restore Quantum C2 data and configuration. Use when creating backups, restoring from backup, or managing disaster recovery.
trigger_keywords: backup, restore, disaster recovery, snapshot, migrate, data protection
---

## Purpose
Manages backups and restores for Quantum C2 databases (PostgreSQL, SQLite, Redis), configuration, and Kubernetes manifests.

## When to Use
- Before deployments or major changes
- When user asks to "backup" or "restore"
- As part of disaster recovery procedures
- Before migration operations

## Workflow
1. Create pre-change backup
2. Verify backup integrity
3. Perform operation
4. Restore from backup if needed
5. Verify restored state

## Commands
```bash
# Create full backup (PowerShell)
.\scripts\backup.ps1 -Type all -RetainDays 30

# Create database-only backup
.\scripts\backup.ps1 -Type database

# Backup with disaster recovery script
python scripts/disaster_recovery.py backup

# Restore PostgreSQL
python scripts/disaster_recovery.py restore-postgres --backup-file path/to/backup

# Restore Redis
python scripts/disaster_recovery.py restore-redis --backup-file path/to/backup

# Rollback Kubernetes deployment
python scripts/disaster_recovery.py rollback --deployment quantum-backend

# Failover to secondary cluster
python scripts/disaster_recovery.py failover --cluster secondary

# Health check all services
python scripts/disaster_recovery.py health-check

# Generate DR report
python scripts/disaster_recovery.py report

# List available backups
ls backups/
```

## Backup Types
| Type | Script | Target |
|------|--------|--------|
| PostgreSQL | `backup.ps1` | Docker container |
| SQLite | `backup.ps1` | Local database file |
| Redis | `backup.ps1` | RDB snapshot |
| Full DR | `disaster_recovery.py` | K8s + all databases |

## Backup Location
- Windows: `backups/` directory
- Kubernetes: Persistent volumes
- Format: `*-backup-{timestamp}.{type}`

## Retention Policy
- Default: 30 days
- Configurable via `-RetainDays` parameter
- Automatic cleanup of expired backups

## Disaster Recovery Steps
```bash
# 1. Assess situation
python scripts/disaster_recovery.py health-check

# 2. Generate DR report
python scripts/disaster_recovery.py report

# 3. Restore from latest backup
python scripts/disaster_recovery.py backup  # Create safety snapshot first
python scripts/disaster_recovery.py restore-postgres

# 4. Verify services
python scripts/disaster_recovery.py health-check

# 5. Rollback if needed
python scripts/disaster_recovery.py rollback --deployment quantum-backend
```

## Notes
- Always create a backup before restore operations
- Backup files are timestamped for easy identification
- Kubernetes backups include deployment manifests
- See `.learnings/FEATURE_REQUESTS.md` for disaster recovery feature requests
