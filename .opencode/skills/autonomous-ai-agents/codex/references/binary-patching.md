# Binary Patching Guide for Codex CLI

## Overview
This guide details how to reverse engineer and patch the Codex CLI binary to use OpenRouter natively without environment variables.

## Binary Location
```
/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/codex/codex
```

## Prerequisites
- Ghidra (NSA's reverse engineering framework)
- Basic understanding of x86-64 assembly
- Hex editor (or use Ghidra's built-in editor)
- Backup of original binary

## Step-by-Step Patching Process

### 1. Backup Original Binary
```bash
cp /usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/codex/codex \
   /usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/codex/codex.backup
```

### 2. Load Binary in Ghidra
- File → New Project → Non-shared project
- Import the codex binary
- Accept default analysis options
- Wait for auto-analysis to complete

### 3. Locate API Endpoint String\n**Method A: String Search**\n- Search → For Strings...\n- Minimum length: 10\n- Search for: `api.openai.com`\n- Double-click result\n\n**Method B: Known Offset (Verified from session)**\n- Press G (Go To)\n- Enter: `0xa46bd4c` (confirmed location from successful patching)\n- You should see: `https://api.openai.com/v1`

### 4. Analyze String Context
Check what comes before and after the string:
- Before: `...struct ModelProviderInfo...`
- After: `...size overflows MAX_SIZE...`

### 5. Patch the String (Length-Sensitive)\n**Critical**: Replacement must be SAME LENGTH or SHORTER\n\nOriginal: `https://api.openai.com/v1` (24 bytes)\n\n**Option A: Local Proxy** (Same length replacement)\n```\nhttps://localhost:8080/v1  (24 bytes - perfect fit)\n```\n\n**Option B: Shorter domain with DNS**\n```\nhttps://or.ai/v1             (15 bytes - pad with nulls)\n```\n\n**Option C: Jump to new string** (Advanced - User Preferred)\nFind free space in .rodata section, write new string there, patch pointer\n- **User's Verified Approach**: Patch to OpenRouter URL with header injection\n- **OpenRouter URL**: `https://openrouter.ai/api/v1` (28 bytes - requires jumping)\n- **Jump Technique**: Allocate space in .rodata, write URL there, redirect pointers\n\n### 5.1 Verified User Session Details\nFrom the session, the user successfully patched the Codex binary using:\n- **API Endpoint Offset**: 0xa46bd4c\n- **Original Bytes**: `68 74 74 70 73 3a 2f 2f 61 70 69 2e 6f 70 65 6e 61 69 2e 63 6f 6d 2f 76 31` (https://api.openai.com/v1)\n- **Following Bytes**: `73 69 7a 65 20 6f 76 65 72` (ASCII: " size over" - start of "size overflows MAX_SIZE...")\n- **Target OpenRouter URL**: `https://openrouter.ai/api/v1`\n- **API Key**: `REDACTED`\n- **Required Headers**:\n  - `Authorization: Bearer REDACTED`\n  - `HTTP-Referer: https://hermes.ai`\n  - `X-Title: Hermes-Agent`\n\n**User's Preferred Method**: Native binary modification without external proxies or environment variables, achieved through Ghidra string patching and header construction modification.

### 6. Performing the Patch in Ghidra
1. Navigate to the string address
2. Switch to Listing view
3. Click on first byte of the string
4. Right-click → Patch Instruction (or Ctrl+Shift+G)
5. In Bytes view:
   - Click the lock icon to enable editing
   - Overwrite hex values with replacement string
   - Fill remaining bytes with 00 (null) if shorter
6. Accept changes

### 7. Patch Model String (Optional)
Search for model strings like:
- `gpt-5.5-sonnet`
- `gpt-4`
- `codex`

Replace with target model (ensure length compatibility):
- Target: `nvidia/nemotron-3-super-120b-a12b:free` (42 bytes)
- May need to find longer original string or use jumping technique

### 8. API Key Handling Options
**Option A: Environment Variable Intercept**
- Find `OPENAI_API_KEY` string reference
- Trace where it's read (getenv call)
- Patch to read `OPENROUTER_API_KEY` instead
- Set `OPENROUTER_API_KEY` environment variable

**Option B: Hardcode API Key**
- Find writable data section (.data or .bss)
- Locate free space
- Insert API key: `REDACTED`
- Patch getenv call to return pointer to your hardcoded key

**Option C: Redirect Auth Header**
- Find where Authorization header is constructed
- Patch to always use OpenRouter key
- More complex but cleanest

### 9. Export Patched Binary
- File → Export Program...
- Format: Binary (creates new file)
- Save as: `codex-patched`
- OR: Original File (overwrites - BE CAREFUL)

### 10. Verification
```bash
# Check strings were modified
strings codex-patched | grep -E "localhost:8080|or.ai|nemotron"

# Verify binary still valid
file codex-patched

# Test basic functionality
./codex-patched --help

# Test with proxy running
# (Start your localhost:8080 proxy that forwards to OpenRouter)
./codex-patched exec "Say hello"
```

## Local Proxy Implementation
Create a simple Python proxy that runs on localhost:8080 and forwards to OpenRouter:

```python
#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request

API_KEY = "REDACTED"
OPENROUTER_BASE = "https://openrouter.ai/api/v1"

class OpenRouterProxy(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Forward to OpenRouter
        url = OPENROUTER_BASE + self.path
        req = urllib.request.Request(
            url,
            data=post_data,
            headers={
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': self.headers.get('Content-Type', 'application/json'),
                'HTTP-Referer': 'https://hermes.ai',
                'X-Title': 'Hermes-Agent',
                **{k: v for k, v in self.headers.items() 
                   if k.lower() not in ['host', 'content-length']}
            },
            method='POST'
        )
        
        try:
            response = urllib.request.urlopen(req)
            self.send_response(response.status)
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response.read())
        except Exception as e:
            self.send_error(502, f"Bad Gateway: {e}")
    
    def do_GET(self):
        # Handle GET requests similarly
        self.do_POST()  # Simplified - in reality handle appropriately
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

if __name__ == '__main__':
    port = 8080
    server = HTTPServer(('localhost', port), OpenRouterProxy)
    print(f"OpenRouter proxy listening on http://localhost:{port}")
    print(f"Forwarding to: {OPENROUTER_BASE}")
    print("Add this line to your ~/.bashrc or shell profile:")
    print(f"  export OPENAI_API_BASE_URL=http://localhost:{port}/v1")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down proxy...")
        server.server_close()
```

## Alternative: Hex Patching Script
For those who prefer command-line patching:

```bash
#!/usr/bin/env python3
import sys

def patch_codex_binary(input_path, output_path):
    # Read binary
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())
    
    # Define patches (offset, original, replacement)
    patches = [
        # API Endpoint: https://api.openai.com/v1 -> https://localhost:8080/v1
        (0xa46bd4c, 
         b"https://api.openai.com/v1",
         b"https://localhost:8080/v1"),
         
        # Add more patches as needed
        # (offset, original_bytes, new_bytes)
    ]
    
    total_patched = 0
    for offset, original, replacement in patches:
        if len(original) != len(replacement):
            print(f"ERROR: Patch at 0x{offset:x} length mismatch: {len(original)} != {len(replacement)}")
            return False
            
        # Find all occurrences
        pos = data.find(original, offset)
        while pos != -1:
            # Verify it's the right context (optional but recommended)
            # Replace
            data[pos:pos+len(original)] = replacement
            total_patched += 1
            pos = data.find(original, pos + len(original))
    
    # Write patched binary
    with open(output_path, 'wb') as f:
        f.write(data)
    
    print(f"Successfully patched {total_patched} locations")
    print(f"Output saved to: {output_path}")
    return True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 patch_codex.py <input_binary> <output_binary>")
        sys.exit(1)
    
    success = patch_codex_binary(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
```

## Verification Checklist
[ ] Binary still runs: `./codex-patched --help` works
[ ] Strings patched: `strings codex-patched | grep localhost`
[ ] Proxy functioning: Test with simple curl to localhost:8080
[ ] Codex can connect: `./codex-patched exec "ping"` (or simple command)
[ ] No crashes during operation
[ ] Responses come from OpenRouter (check headers or use known model)

## Safety Notes
1. Always keep a backup of the original binary
2. Test patches in a disposable environment first
3. Start with simple string replacements before attempting complex code modifications
4. Monitor process behavior after patching
5. Consider using API key restrictions in OpenRouter dashboard

## Troubleshooting
- **Binary won't run**: You likely corrupted critical structure - restore backup
- **Connection fails**: Verify proxy is running and accessible
- **Authentication errors**: Check that proxy is forwarding headers correctly
- **Model not found**: Verify model name spelling and availability in OpenRouter
- **Length errors**: Ensure all string replacements maintain exact byte length