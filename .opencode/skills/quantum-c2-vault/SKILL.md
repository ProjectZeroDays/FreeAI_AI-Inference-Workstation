---
name: quantum-c2-vault
description: >
  Credential vault and encryption operations for Quantum C2. Use when the user needs to manage credentials, access the vault, encrypt/decrypt data, or work with cryptographic primitives. Triggers on: "vault", "credentials", "encrypt", "decrypt", "crypto", "password", "SSH key", "API key", "credential management", "encryption".
---

# Quantum C2 Vault & Encryption Skill

Manage credentials and cryptographic operations.

## Vault Operations

### List Credentials
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/vault/credentials
```

### Add Credential
```bash
curl -X POST http://localhost:8000/api/vault/credentials \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Target Server SSH Key",
    "username": "admin",
    "value": "ssh-rsa AAAA...",
    "type": "ssh_key",
    "target": "192.168.1.100",
    "notes": "Production server access"
  }'
```

### Get Credential
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/vault/credentials/{id}
```

### Unlock Vault
```bash
curl -X POST http://localhost:8000/api/vault/{id}/unlock \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Crypto Primitives

### List Available Primitives
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/vault/primitives
```

### Encrypt Data
```bash
curl -X POST http://localhost:8000/api/vault/encrypt \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "sensitive information",
    "algorithm": "aes256"
  }'
```

### Decrypt Data
```bash
curl -X POST http://localhost:8000/api/vault/decrypt \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "encrypted_data": "<base64_encoded>",
    "algorithm": "aes256"
  }'
```

## Encryption Algorithms

| Algorithm | Key Size | Use Case |
|-----------|----------|----------|
| `aes256` | 256-bit | Symmetric encryption |
| `rsa4096` | 4096-bit | Asymmetric encryption |
| `sha256` | 256-bit | Hashing |
| `hmac-sha256` | 256-bit | Message authentication |
| `base64` | — | Encoding |
| `xor-stream` | Variable | Stream encryption |

## Quantum-Resistant Cryptography

### PQC Algorithms
| Algorithm | Standard | Purpose |
|-----------|----------|---------|
| `ML-KEM (Kyber)` | FIPS 203 | Key encapsulation |
| `ML-DSA (Dilithium)` | FIPS 204 | Digital signatures |
| `SPHINCS+` | FIPS 205 | Stateless hash signatures |
| `hybrid` | — | ML-KEM + AES-256-GCM |

### Use PQC Encryption
```bash
curl -X POST http://localhost:8000/api/vault/encrypt \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data":"sensitive","algorithm":"hybrid"}'
```

## Credential Types

| Type | Use Case |
|------|----------|
| `password` | Standard passwords |
| `ssh_key` | SSH private keys |
| `api_key` | API tokens |
| `certificate` | TLS/SSL certificates |
| `hash` | Password hashes |

## Vault Features

| Feature | Description |
|---------|-------------|
| Encrypted Storage | AES-256-GCM for credential encryption |
| Value Hiding | Stored values show as MD5 hash only |
| Target Grouping | Group credentials by target device |
| Audit Trail | All vault operations logged |
| Quantum-Resistant | NIST-standard post-quantum algorithms |

## Quick Operations

```bash
# Add credential
curl -s -X POST http://localhost:8000/api/vault/credentials \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","username":"admin","value":"password123","type":"password"}'

# List all
curl -s -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/vault/credentials

# Encrypt data
curl -s -X POST http://localhost:8000/api/vault/encrypt \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data":"secret message","algorithm":"aes256"}'
```
