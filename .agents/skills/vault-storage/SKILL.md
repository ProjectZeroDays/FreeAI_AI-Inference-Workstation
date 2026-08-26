---
name: vault-storage
description: Management of highly sensitive data using encrypted file containers. Integrates with cloud storage for off-site, encrypted backups of reports, evidence, and exploits.
---

# Vault Storage

This skill ensures the absolute secrecy of the framework's most critical assets.

## Vault Operations
- **Containerization**: Store files in an encrypted binary blob that requires a master key to mount.
- **Cloud Mirroring**: Sync the encrypted container to Google Drive or other platforms, ensuring the cloud provider only sees encrypted noise.
- **Evidence Isolation**: Store forensic logs and exfiltrated loot in separate, isolated vault partitions.

## Integration with Cloud
- **Cryptomator Logic**: Use client-side encryption before uploading to ensure zero-knowledge storage.
- **Auto-Sync**: Automatically mirror the vault to a remote cloud account upon every critical update.
