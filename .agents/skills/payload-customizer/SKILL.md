---
name: payload-customizer
description: Tailoring raw payloads to specific target networks and devices. Focuses on bypassing environment-specific EDR/AV and ensuring stability on the target architecture.
---

# Payload Customizer

This skill transforms generic exploits into surgical tools.

## Customization Process
1. **Environment Mapping**: Use `pegasus-intel-hub` to determine the target's security software and OS build.
2. **Obfuscation Tuning**: Apply specific polymorphic mutations that are known to bypass the detected EDR.
3. **Configuration**: Set C2 callback URLs, master keys, and persistence paths specific to the target's directory structure.
4. **Validation**: Run the customized payload against a mirrored environment to ensure it doesn't crash the target.
