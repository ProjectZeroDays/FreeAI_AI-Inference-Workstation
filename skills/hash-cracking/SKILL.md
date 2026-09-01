---
name: hash-cracking
description: Professional cryptanalysis and hash cracking. Implements various attack strategies (dictionary, brute-force, rainbow tables) and integrates with GPU-accelerated models.
---

# Hash Cracking & Cryptanalysis

This skill focuses on recovering plaintext credentials from encrypted hashes.

## Cracking Strategies
- **Dictionary Attack**: Using curated wordlists tailored to the target's industry or region.
- **Rule-Based Attack**: Applying common password mutations (e.g., replacing 'a' with '@').
- **GPU Acceleration**: Offloading intensive computations to specialized models and hardware.
- **Rainbow Tables**: Using pre-computed hashes for common passwords.

## Workflow
1. **Hash Identification**: Determine the hash type (e.g., NTLM, SHA-256, bcrypt).
2. **Strategy Selection**: Choose the most efficient attack based on hash complexity.
3. **Execution**: Run the cracker and monitor for hits.
4. **Integration**: Feed recovered credentials back into the `pegasus-c2-manager` for subsequent access.
