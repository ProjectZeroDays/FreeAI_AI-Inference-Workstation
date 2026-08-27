---
name: brute_force
description: >
  GPU-accelerated brute force and password cracking: hashcat, rainbow tables, SecLists, hydra.
  Targets NTLM SAM, bcrypt, SHA, ZIP/RAR/PDF/Office passwords, SSH keys, and JWT secrets.
triggers:
  - brute force
  - password crack
  - hash crack
  - hydra attack
  - hashcat
  - jwt crack
  - zip crack
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-08-27"
  agent: agents/specialized/brute_force.py
---

# Brute Force Agent

GPU-accelerated password cracking and service brute forcing.

## Purpose
Crack hashed passwords and brute-force authentication services using GPU acceleration and comprehensive wordlists.

## Targets
- **NTLM SAM**: Windows password hashes
- **bcrypt**: Modern hashing algorithm
- **SHA-256/512**: Common hash functions
- **ZIP/RAR/PDF/Office**: Document passwords
- **SSH keys**: Private key passphrase cracking
- **JWT**: JSON Web Token secret recovery

## Usage
```python
from agents.specialized.brute_force import BruteForceAgent

agent = BruteForceAgent()
# Crack a hash
result = agent.crack_hash("5f4dcc3b5aa765d61d8327deb882cf99", hash_type="md5")
# Hydra attack
result = agent.hydra_attack("192.168.1.1", service="ssh", user="root")
# Rainbow lookup
result = agent.rainbow_lookup("5f4dcc3b5aa765d61d8327deb882cf99")
# ZIP crack
result = agent.attack_zip("/path/to/encrypted.zip")
# JWT crack
result = agent.attack_jwt("eyJhbGciOiJIUzI1NiIs...")
```

## Wordlists
- SecLists (all Discovery/Web-Content and Passwords subsets)
- rockyou.txt
- xato-net-10-million
- Common-Credentials top lists
- JWT-specific secret lists

## GPU Support
- Hashcat with CUDA/OpenCL
- Multi-GPU parallel cracking
- Rule-based mutation attacks
