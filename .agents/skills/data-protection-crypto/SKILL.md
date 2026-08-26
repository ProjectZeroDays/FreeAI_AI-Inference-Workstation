---
name: data-protection-crypto
description: Autonomous encryption and protection of high-value data. Focuses on securing loot, evidence, and database files using advanced cryptographic standards.
---

# Data Protection & Crypto

This skill ensures that stolen data and framework state remain secure from discovery.

## Encryption Workflows
- **Loot Encryption**: Automatically encrypt exfiltrated data (credentials, docs) using AES-256-GCM before storage.
- **Database Hardening**: Apply transparent data encryption (TDE) to the C2 database files.
- **Key Rotation**: Periodically rotate encryption keys across all active agents.

## Secure Storage
- **Encrypted Archives**: Package loot into password-protected, encrypted containers.
- **Memory-Only Keys**: Implement keys that only exist in volatile memory to prevent forensic recovery from disk.
