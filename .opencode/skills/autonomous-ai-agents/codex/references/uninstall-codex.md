# Uninstalling OpenAI Codex CLI

This reference documents the complete removal procedure for OpenAI Codex CLI and all associated files.

## Complete Removal Checklist

### 1. Uninstall npm Package
```bash
npm uninstall -g @openai/codex
```

### 2. Remove Hidden Configuration Directories
```bash
rm -rf ~/.codex
rm -rf ~/.config/codex
```

The `~/.codex` directory contains:
- `config.toml` - Configuration file
- `logs_2.sqlite` - SQLite database
- `state_5.sqlite*` - State files
- `log/` - Log files
- `tmp/` - Temporary files
- `memories/` - Memory storage

### 3. Verify Removal
```bash
# Command should not be found
which codex || echo "codex command removed from PATH"

# Package should not appear in npm list
npm list -g --depth=0 | grep -i codex || echo "Codex package uninstalled from npm"

# No remaining files
ls -la ~/.codex 2>/dev/null || echo "Config directory already removed"
```

## Files Removed (Confirmed)

| Location | Type | Description |
|----------|------|-------------|
| `/usr/local/bin/codex` | Binary | CLI executable |
| `/usr/local/lib/node_modules/@openai/codex` | Package | npm package (v0.130.0) |
| `/usr/local/lib/node_modules/@openai` | Directory | Empty directory (removed) |
| `~/.codex/` | Directory | Config/state directory |
| `~/.config/codex/` | Directory | Additional config directory |

## Verification Script

```bash
#!/bin/bash
set -e

echo "Verifying Codex removal..."

# Check command
if command -v codex &> /dev/null; then
    echo "ERROR: codex command still exists"
    exit 1
else
    echo "✓ codex command removed from PATH"
fi

# Check npm
if npm list -g --depth=0 2>/dev/null | grep -qi codex; then
    echo "ERROR: codex still in npm packages"
    exit 1
else
    echo "✓ Codex package uninstalled from npm"
fi

# Check directories
for dir in ~/.codex ~/.config/codex; do
    if [ -d "$dir" ]; then
        echo "ERROR: $dir still exists"
        exit 1
    else
        echo "✓ $dir removed"
    fi
done

echo "✓ All verifications passed"
```

## Notes

- The uninstallation removes ALL local state and configuration
- Any custom OpenRouter patches applied to the binary will be lost
- If Codex was patched for OpenRouter integration (see `binary-patching.md`), those patches must be re-applied after reinstallation
- Environment variables like `OPENAI_API_BASE_URL` and `OPENAI_API_KEY` for OpenRouter do not need to be unset - they are harmless if Codex is not present