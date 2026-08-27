---
name: binary-patching-for-ai-providers
description: Modify AI provider settings in applications through direct binary patching for seamless integration
version: 1.0.0
author: Hermes Agent
---
# Binary Patching for AI Provider Modification

## Overview
This skill describes how to modify AI provider settings in applications through direct binary patching, allowing seamless integration without environment variables or configuration files. This technique is useful when you want to change default models, providers, or API endpoints in AI applications at the binary level.

## When to Use
- You want to modify an AI application's default provider/model settings permanently
- You prefer native integration over external proxies or configuration files (respect explicit user preferences for binary patching when stated)
- The application doesn't provide adequate configuration options for your needs
- You need to maintain exact binary structure while making string replacements
- The user has explicitly stated they want to modify binaries natively rather than using environment variables or configuration files

## Prerequisites
- Access to the target binary (executable or library)
- A reverse engineering tool (Ghidra, IDA, Binary Ninja, etc.)
- Basic understanding of strings and memory layout in binaries
- The target strings you want to replace and their replacements

## Procedure

### 1. Locate Target Strings in Binary
```bash
# Using strings command to find relevant strings
strings -t x /path/to/binary | grep -i "openai\|gpt\|api\|model\|provider"

# Or using Ghidra:
# - Load binary into Ghidra
# - Search for strings (Search â†’ For Strings)
# - Look for strings containing: "api.openai.com", "gpt-", "openai", etc.
```

### 1b. Alternative Strategy: Finding Suitable Replacement Candidates
When the exact target string isn't found (common with customized defaults):
- Search for strings of the target length or longer that contain relevant keywords
- For base URL: look for `https://` strings containing `api` or `openai`
- For provider: look for strings containing `open`, `ai`, or `provider`  
- For model: look for strings containing `gpt`, `model`, or version-like patterns
- Prioritize candidates that appear to be configuration-like rather than embedded in messages or code

### 2. Identify Exact Offsets and Context
For each target string you wish to replace:
- Note the exact file offset (virtual address)
- Examine surrounding bytes to understand the context
- Determine if the string is null-terminated or length-prefixed
- Check what comes immediately before and after the string

### 3. Verify Replacement String Length
Critical: To maintain binary integrity without breaking pointers or structure:
- Your replacement string MUST be the same length as the original
- Or you must pad/truncate appropriately while maintaining null termination
- Never change the overall binary size unless you understand relocation tables

### 4. Perform the Patching
Using a hex editor or binary patching tool:

#### Option A: Same-length replacement (preferred)
If replacement string equals original length:
```bash
# Using dd for in-place replacement
printf "new_string_here" | dd of=/path/to/binary bs=1 seek=<offset> count=<length> conv=notrunc
```

#### Option B: Padding when replacement is shorter
If replacement string is shorter than original:
```bash
# Replace with new string + null terminator + padding
printf "new_string\\0$(printf '\\0%.0s' {1..<padding_length>})" | \
  dd of=/path/to/binary bs=1 seek=<offset> count=<original_length> conv=notrunc
```

#### Option C: Truncating when replacement is longer (use with caution)
Only do this if you can safely overwrite non-critical following bytes:
```bash
# Truncate replacement to fit original length
printf "new_string_here" | cut -c1-<original_length> | \
  dd of=/path/to/binary bs=1 seek=<offset> count=<original_length> conv=notrunc
```

### 5. Verify Patch Integrity
After patching:
```bash
# Verify the string was replaced correctly
strings -t x /path/to/binary | grep -i "part_of_your_replacement"

# Check that the binary still executes
/path/to/binary --help  # or equivalent command

# Ensure no immediate crashes or obvious corruption
```

## Specific Example: Modifying Codex for OpenRouter

Based on the user's successful modification of Codex CLI:

### Targets to Replace:
1. **Base URL**: `https://api.openai.com/v1` â†’ `https://openrouter.ai/api/v1` (both 28 bytes)
2. **Provider**: `openai` variants â†’ `openrouter` (10 bytes, padded)
3. **Model**: `gpt-5.1-codex-ma` â†’ `poolside/laguna-xs.2:free` (25 bytes)

### Offsets Found:
- Base URL: 0xa1e8ef0 (in a longer https:// string context)
- Provider: 0xfacc8d 
- Model: 0xa1f1510

### Patching Commands Used:
```bash
# Base URL patch (exact length match)
printf 'https://openrouter.ai/api/v1' | \
  dd of=/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/codex/codex \
  bs=1 seek=0xa1e8ef0 count=28 conv=notrunc

# Provider patch (shorter, null-padded)
printf 'openrouter\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0' | \
  dd of=/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/codex/codex \
  bs=1 seek=0xfacc8d count=35 conv=notrunc

# Model patch (shorter, null-padded)
printf 'poolside/laguna-xs.2:free\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0' | \
  dd of=/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/codex/codex \
  bs=1 seek=0xa1f1510 count=48 conv=notrunc
```

## Pitfalls and Safety Considerations

### âš ï¸ Critical Pitfalls to Avoid

1. **Length Mismatches**
   - **Problem**: Replacement strings of different lengths can corrupt binary structure
   - **Prevention**: Always measure exact lengths and pad/truncate appropriately
   - **Verification**: Check that strings are properly null-terminated after patching

2. **Overwriting Critical Structures**
   - **Problem**: Patching into code sections, vtables, or control data
   - **Prevention**: 
     - Patch only in readable string/data sections (.rodata, .rdata)
     - Avoid .text (code) sections unless you know exactly what you're doing
     - Use strings command output to identify safe locations

3. **Breaking Null Termination**
   - **Problem**: Forgetting null terminators can cause buffer overruns
   - **Prevention**: 
     - If original was null-terminated, replacement must be too
     - When padding shorter strings, always include null terminator
     - Verify with: `strings -t x /path/to/binary | grep "your_string"`

4. **Missing Context Dependencies**
   - **Problem**: Some applications validate strings or expect specific formats
   - **Prevention**:
     - Look for validation code around string usage (in disassembler)
     - Test thoroughly after patching
     - Keep backups of original binaries

### âœ… Best Practices

1. **Always Backup First**
   ```bash
   cp /path/to/binary /path/to/binary.backup.orig
   ```

2. **Work in a Copy** 
   - Patch a copy of the binary for testing
   - Only replace original after verification

3. **Verify String Context**
   - Before patching, check 10-20 bytes before/after target string
   - Ensure you're not in the middle of a larger structure

4. **Test Incrementally**
   - Patch one string at a time
   - Verify application still works after each patch

5. **Document Your Changes**
   - Keep notes of:
     - Original string â†’ New string
     - Offsets used
     - Length considerations
     - Any special padding/truncation needed

## Verification Checklist

After patching, verify:
- [ ] Binary executes without immediate crashes
- [ ] Help/version commands still work
- [ ] Target strings show as replaced when using `strings` command
- [ ] Application behaves as expected with new settings
- [ ] No obvious corruption in related functionality
- [ ] Binary size unchanged (unless intentionally modified)

## Troubleshooting

### If Binary Crashes After Patching:
1. Check for length mismatches - did you alter binary size unintentionally?
2. Verify you didn't patch into executable code
3. Ensure strings are properly null-terminated
4. Try reverting one patch at a time to isolate issue

### If Application Doesn't Use New Settings:
1. Double-check you patched the right string instances
2. Look for multiple copies of the same string
3. Check if application uses configuration files that override binary defaults
4. Verify the strings are actually used at runtime (strings in binary â‰  strings used)

### If Binary Won't Execute:
1. You may have corrupted headers or critical structures
2. Compare with backup using hex editor to see what changed
3. Consider that some strings might be length-prefixed rather than null-terminated

## Configuration-Based Approach (Alternative)

When binary patching is not required or desired, a TOML configuration file approach provides a cleaner, maintainable solution:

### When to Use Configuration-Based Approach
- User explicitly prefers configuration files over binary modification
### Configuration-Based Approach (Primary Method)

When binary patching is not required or desired, a TOML configuration file approach provides a cleaner, maintainable solution:

**Implementation Pattern (Updated from Session)**

1. **Create patch script** (`scripts/patch_openrouter.js`):
```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

const CONFIG_DIR = path.join(os.homedir(), '.codex');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.toml');

// Configuration values from package.json or environment
const API_KEY = "REDACTED";
const DEFAULT_MODEL = 'poolside/laguna-xs.2:free';

// Ensure directory exists
if (!fs.existsSync(CONFIG_DIR)) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
}

// Generate config.toml
const config = `[model_provider_configs.openrouter]
api_key = "${API_KEY}"
base_url = "https://openrouter.ai/api/v1"

[profiles.openrouter-free]
model = "${DEFAULT_MODEL}"
model_provider = "openrouter"
`;

fs.writeFileSync(CONFIG_FILE, config);
console.log('âœ… Configuration patched successfully');
```

2. **Add postinstall hook** to `package.json`:
```json
{
  "scripts": {
    "postinstall": "node scripts/patch_openrouter.js",
    "start": "node cli.js"
  },
  "bin": {
    "codex": "./cli.js"
  }
}
```

3. **Create CLI entry point** (`cli.js`):
```javascript
#!/usr/bin/env node
const path = require('path');
const fs = require('fs');
const os = require('os');

const CONFIG_PATH = path.join(os.homedir(), '.codex', 'config.toml');
// ... load config, start chat interface
```

4. **Result**: Application automatically configured on install with `npm install`

### Advantages Over Binary Patching
- No risk of binary corruption
- Easy to audit and version control
- Can be updated without reinstalling
- Works with application's intended configuration system
- Supports multiple profiles/providers cleanly
- Easy rollback - just delete config file
- Can be modified at runtime without reinstalling
    "postinstall": "node scripts/patch_openrouter.js"
  }
}
```

3. **Result**: Application automatically configured on install

### Advantages Over Binary Patching
- No risk of binary corruption
- Easy to audit and version control
- Can be updated without reinstalling
- Works with application's intended configuration system
- Supports multiple profiles/providers cleanly

### Codex-Specific Configuration

The `~/.codex/config.toml` structure for OpenRouter:
```toml
[model_provider_configs.openrouter]
api_key = "REDACTED"
base_url = "https://openrouter.ai/api/v1"

[profiles.openrouter-free]
model = "poolside/laguna-xs.2:free"
model_provider = "openrouter"
```

Supported models:
- `poolside/laguna-xs.2:free`
- `baidu/cobuddy:free`
- `nvidia/nemotron-3-super-120b-a12b:free`
- `baidu/qianfan-ocr-fast:free`

### When to Choose Configuration Over Binary Patching
- User preference explicitly states configuration-based approach
- Application has documented configuration file support
- Need for easy maintenance and rollback
- Multiple environments or providers to manage
- Compliance requirements for non-binary modifications

### User Preference: Configuration-Based Approach

**Important**: The user explicitly prefers configuration-based integration over binary patching. This skill now prioritizes the configuration approach as the primary method, with binary patching as a fallback for cases where configuration files are not supported.

Key preference signals from this session:
- User requested "configuration file method instead of binary patching"
- User wants seamless npm-based setup with postinstall hooks
- Configuration should be version-controllable and easily reversible

### When to Consider Alternatives

Before binary patching, consider (in order of preference):
1. **Configuration files** (~/.codex/config.toml) - **PREFERRED** - Use when application supports external config
2. Environment variables (OPENAI_API_BASE, etc.)
3. Command-line flags (--base-url, --model)
4. Wrapper scripts that set appropriate variables
5. **Binary patching** - Only when configuration is not possible

Choose binary patching only when:
- Configuration file support is not available
- Native, seamless integration is required without any config files
- No other configuration methods suffice
- You control the distribution and can maintain patched binaries
- The application specifically resists other configuration methods

## References
- Ghidra documentation: String searching and patching
- ELF/Portable Executable format specifications
- Application-specific string usage patterns (learn through observation)
- Session-specific reference: `references/codex-openrouter-config-session.md`
- Template: `templates/package-config-approach.json` (configuration-based)
- Template: `templates/package.json` (binary patching approach)