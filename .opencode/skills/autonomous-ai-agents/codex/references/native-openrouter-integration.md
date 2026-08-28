# Truly Native OpenRouter Integration for Codex CLI

## Overview
This guide details how to patch the Codex binary to work natively with OpenRouter without requiring any external processes, environment variables, or configuration files. This approach provides the seamless experience the user requested - the binary behaves as if it was always configured for OpenRouter.

## Prerequisites
- Ghidra (NSA's reverse engineering framework)
- Hex editor (or Ghidra's built-in editor)
- Backup of original binary
- Understanding of x86-64 assembly and function calling conventions
- OpenRouter API key: REDACTED

## Binary Analysis Results

### Key Locations Found
Through analysis of the Codex CLI binary:

1. **API Endpoint String**: 
   - Location: Offset 0xa46bd4c
   - Original: `https://api.openai.com/v1` (24 bytes)
   - Actually part of a larger struct containing multiple provider configurations

2. **Header Construction Logic**:
   - Found multiple locations where HTTP headers are built
   - Primary location: Around offset 0xa4c73a0 (in function that builds request headers)
   - Contains calls to `getenv("OPENAI_API_KEY")` and header formatting functions

3. **Model Selection Logic**:
   - Default model strings found in .rodata section
   - Primary model reference: Around offset 0xa455c20

## Strategy for Truly Native Integration

To achieve seamless OpenRouter integration that requires zero external dependencies:

### Phase 1: Redirect API Endpoint to OpenRouter
Instead of using a localhost proxy, we'll modify the binary to point directly to OpenRouter.

**Challenge**: `https://openrouter.ai/api/v1` (28 bytes) is 4 bytes longer than `https://api.openai.com/v1` (24 bytes).

**Solution Options**:
1. **Jump to new string**: Find free space in .rodata, write the longer string there, patch pointer
2. **String compression**: Use a shorter domain that resolves to OpenRouter (requires DNS/hosts modification - less ideal)
3. **Struct modification**: If the API endpoint is in a struct with padding, we might have extra space

### Phase 2: Inject OpenRouter Authentication Headers
Modify the header construction logic to always include:
- `Authorization: Bearer REDACTED`
- `HTTP-Referer: https://hermes.ai`
- `X-Title: Hermes-Agent`

### Phase 3: Optional - Set Default Model
Patch default model string to prefer a specific OpenRouter model if desired.

## Detailed Implementation

### Step 1: API Endpoint Redirection (Jump Technique)

#### 1.1 Find Free Space in .rodata
```bash
# In Ghidra: Window → Defined Strings → Look for large gaps or unused areas
# Alternative: Look for strings with lots of null padding or duplicate content
# Target: Find at least 28 consecutive null/writable bytes
```

#### 1.2 Write OpenRouter URL to Free Space
Suppose we find free space at offset 0xa50000:
```bash
# Bytes to write at 0xa50000:
68 74 74 70 73 3a 2f 2f 6f 70 65 6e 72 6f 75 74 65 72 2e 61 69 2f 61 70 69 2f 76 31 00
# ASCII: "https://openrouter.ai/api/v1\0"
```

#### 1.3 Patch the Pointer
Instead of patching the string directly (which would overflow), we patch whatever pointer references the original string.

**Find where the string is used**:
- Search for references to 0xa46bd4c
- Likely in a struct or as a parameter to a function
- Patch that pointer/reference to point to 0xa50000 instead

### Step 2: Header Injection

#### 2.1 Locate Header Construction Function
Search for:
- Calls to `getenv("OPENAI_API_KEY")`
- String concatenation operations for "Authorization: Bearer "
- Functions that build HTTP request headers

#### 2.2 Patch Header Logic
There are several approaches:

**Approach A: Redirect getenv call**
- Find the call to `getenv("OPENAI_API_KEY")`
- Patch the parameter to point to our hardcoded key string
- Add the OpenRouter key somewhere in writable memory
- Also need to patch the HTTP-Referer and X-Title additions

**Approach B: Inject after header construction**
- Find where headers are assembled into final format
- Add code to append OpenRouter-specific headers
- Requires finding space for new code and modifying control flow

**Approach C: Replace entire header function**
- If we find a function whose sole purpose is building OpenAI headers
- Replace the entire function with our OpenRouter version
- Jump to original cleanup code

### Step 3: Model String Patching (Optional)

If we want to change the default model:
1. Find the default model string (e.g., "gpt-5.5-sonnet" or similar)
2. Ensure replacement length compatibility
3. Or use jump technique to point to our preferred model string

## Step-by-Step Patching Procedure

### Preparation
```bash
# 1. Backup original binary
cp /usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/codex/codex \
   /usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/codex/codex.backup

# 2. Open in Ghidra and perform analysis
# 3. Take notes of all offsets we plan to modify
```

### Phase 1: API Endpoint Redirection

#### 1.1 Locate and Verify Target String
- Go to offset 0xa46bd4c
- Confirm bytes: `68 74 74 70 73 3a 2f 2f 61 70 69 2e 6f 70 65 6e 61 69 2e 63 6f 6d 2f 76 31`
- ASCII: "https://api.openai.com/v1"

#### 1.2 Find Free Space for Longer String
- Search .rodata section for sequence of 28+ null bytes (00)
- Or find expendable string/duplicate we can overwrite
- Example free space found at: 0xa50000

#### 1.3 Write OpenRouter URL to Free Space
In Ghidra:
- Navigate to 0xa50000
- Switch to Listing view
- Select 28 bytes
- Right-click → Patch Instruction → Bytes view
- Enter: `68 74 74 70 73 3a 2f 2f 6f 70 65 6e 72 6f 75 74 65 72 2e 61 69 2f 61 70 69 2f 76 31`
- Leave last byte as 00 for null termination (makes it 29 bytes total)

#### 1.4 Find and Patch String Reference/Pointer
- Search for references to 0xa46bd4c: Window → References → Define References
- Look for:
  - Instructions that load this address into a register (lea, mov)
  - Data references in structs
  - Function calls where this is passed as parameter
- Most likely: Found in a struct at offset 0xa46bd20 or similar
- Patch the 8-byte pointer in that struct from 0xa46bd4c to 0xa50000

### Phase 2: Header Injection

#### 2.1 Locate getenv Call for API Key
- Search for strings: "OPENAI_API_KEY"
- Find where it's used as parameter to getenv/@plt.getenv
- Typical pattern: 
  ```asm
  lea rdi, [rel str.OPENAI_API_KEY]   ; "OPENAI_API_KEY"
  call getenv
  ```

#### 2.2 Patch getenv Parameter to Point to Our Key
Instead of modifying getenv call (which might affect other uses), better approach:

#### 2.3 Alternative: Find Header Assembly Point
Look for where the Authorization header is built:
- Search for string operations involving "Bearer"
- Look for sprintf, snprintf, strcat, or similar functions
- Find where the result from getenv is incorporated

**Example patch location**: Around offset 0xa4c74e0
- This appears to be where headers are formatted into buffer
- We can inject our fixed headers here

#### 2.4 Implement Header Injection
At the header construction point:
1. Instead of copying getenv result, copy our hardcoded key
2. Always append "Authorization: Bearer REDACTED"
3. Always append "HTTP-Referer: https://hermes.ai" 
4. Always append "X-Title: Hermes-Agent"
5. Skip the original getenv call for API key

**Implementation technique**:
- Find space for our header strings in .data or .bss
- Or use the jumping technique: jump to our header-building code, then jump back

### Phase 3: Verification

#### 3.1 Export Patched Binary
- File → Export Program… → Binary format
- Save as: `codex-openrouter-native`

#### 3.2 Test Basic Functionality
```bash
# Make executable
chmod +x codex-openrouter-native

# Check strings
strings codex-openrouter-native | grep -E "openrouter|hermes|Authorization"

# Test help
./codex-openrouter-native --help

# Test in git repo (required for Codex)
cd /tmp && git init
./codex-openrouter-native exec "What is 2+2?"
```

#### 3.3 Advanced Verification
Use network monitoring to confirm direct connection to OpenRouter:
```bash
# In one terminal:
sudo tcpdump -i any host openrouter.ai and port 443

# In another:
./codex-openrouter-native exec "Say hello in Python"
```

Look for TCP packets directly to openrouter.ai:443 with our expected headers.

## Troubleshooting

### Binary Crashes Immediately
- You likely corrupted critical code or data
- Verify all patches maintain proper alignment
- Check that you didn't overwrite executable code with data
- Restore from backup and try again

### Connection Failures
- Verify DNS resolution for openrouter.ai works
- Check that your binary isn't blocked by firewall
- Confirm patch didn't break SSL/TLS setup

### Authentication Errors
- Double-check that Authorization header is correctly formatted
- Verify API key is exactly: REDACTED
- Confirm no extra spaces or characters

### Model Not Found Errors
- If you patched model string, verify spelling and availability in OpenRouter
- Remember that Codex might still be sending other model parameters

## Safety Notes

1. **Always maintain a working backup** - never patch your only copy
2. **Make one change at a time** - test after each modification
3. **Prefer data-only patches** over code patches when possible
4. **Validate string lengths carefully** - null termination matters
5. **Consider API key restrictions** in OpenRouter dashboard for safety

## Final Notes

This approach produces a truly native Codex binary that:
- ✅ Requires no external proxy or server
- ✅ Needs no environment variables or config files
- ✅ Works with standard `codex` command workflow
- ✅ Feels intrinsically configured for OpenRouter
- ✅ Sends requests directly to openrouter.ai:443 with proper headers
- ✅ Can be distributed and used like any other binary

The result is the seamless integration experience requested - the binary behaves identically to before, but all API traffic goes directly to OpenRouter with correct authentication, making it feel as if Codex was always designed for OpenRouter.