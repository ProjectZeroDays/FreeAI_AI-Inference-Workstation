# Session Verification: Codex Binary Analysis for OpenRouter Integration

## Key Findings from Session

### Verified Binary Offsets
- **API Endpoint String**: Confirmed at offset `0xa46bd4c`
  - Original bytes: `68 74 74 70 73 3a 2f 2f 61 70 69 2e 6f 70 65 6e 61 69 2e 63 6f 6d 2f 76 31` 
    (ASCII: "https://api.openai.com/v1" - 24 bytes)
  - Followed by: `73 69 7a 65 20 6f 76 65 72` (ASCII: " size over" - part of "size overflows MAX_SIZE...")
  
- **Second API Endpoint Offset**: `0xa4c74e2`
  - Identical string in different context

### String Length Analysis
- Original: `https://api.openai.com/v1` = 24 bytes
- OpenRouter: `https://openrouter.ai/api/v1` = 28 bytes (+4 bytes)
- Same-length alternative: `http://127.0.0.1:80/v1` = 24 bytes (exact match)

### Binary Characteristics
- File: `/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/codex/codex`
- Type: ELF 64-bit LSB PIE executable, x86-64, static-pie linked
- Size: ~214 MB
- Backup location: Same directory with `.backup` extension

### Header Requirements for OpenRouter
Based on OpenRouter API documentation and session requirements:
- **Authorization**: `Bearer REDACTED`
- **HTTP-Referer**: `https://hermes.ai`
- **X-Title**: `Hermes-Agent`
- **Content-Type**: `application/json` (for POST requests)
- **User-Agent**: Preserve original or set to `Codex/1.0`

### Patching Approaches Evaluated

#### Approach 1: Jump Technique (True Native)
1. Find free space in binary (null byte sequences)
2. Write OpenRouter URL + null terminator to free space
3. Patch string reference points to use new location
4. Patch header construction to inject OpenRouter headers
5. **Pros**: Zero external dependencies, fully native
6. **Cons**: Requires locating string reference points in code

#### Approach 2: Same-length Placeholder + Forwarder
1. Patch API endpoint to `http://127.0.0.1:80/v1` (24 bytes)
2. Run local forwarder that:
   - Listens on localhost:80
   - Adds OpenRouter-required headers
   - Forwards to `https://openrouter.ai/api/v1`
3. **Pros**: Immediate implementation, reliable
4. **Cons**: Requires local forwarder process

### Files Created During Session
- `/root/seamless_openrouter_integration.md` - Complete integration guide
- `/root/native_openrouter_patcher.py` - Patching script (conceptual)
- `/root/seamless_native_openrouter.py` - Unified solution (conceptual)

### Verification Methods
1. String verification: `strings ./codex-patched | grep "127.0.0.1:80"`
2. Binary execution: `./codex-patched --help`
3. End-to-end test: `./codex-patched exec "simple prompt"` in git repo
4. Forwarder logs: Check `/tmp/codex-forwarder.log` for activity

### Recommended Implementation Path
Based on user preference for native binary modification:
1. **Short-term**: Use Approach 2 (placeholder + forwarder) for immediate seamless experience
2. **Long-term**: Implement Approach 1 (jump technique) for zero-dependency native integration
3. **Always**: Preserve original binary via backup
4. **Always**: Test in git repository context (Codex requirement)

## References
- Original analysis: Previous context summary showing verified offsets
- OpenRouter API docs: https://openrouter.ai/docs
- Codex binary structure: ELF static PIE for Linux x86-64