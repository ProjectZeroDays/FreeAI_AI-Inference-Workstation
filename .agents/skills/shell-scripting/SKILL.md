---
name: shell-scripting
description: Shell scripting for automation, Bash/PowerShell one-liners, file manipulation, text processing, and system administration. Use when the user asks about writing shell scripts, Bash commands, text processing with awk/sed/grep, automation scripts, or system administration tasks.
---

# Shell Scripting

## Bash Essentials

### Script Structure
```bash
#!/usr/bin/env bash
set -euo pipefail

# Variables
NAME="world"
COUNT=0

# Functions
greet() {
    local name="${1:-stranger}"
    echo "Hello, ${name}!"
}

# Conditionals
if [[ -f "$file" ]]; then
    echo "File exists"
elif [[ -d "$dir" ]]; then
    echo "Directory exists"
else
    echo "Not found"
fi

# Loops
for file in *.txt; do
    echo "Processing: $file"
done

for i in {1..10}; do
    echo "Number: $i"
done

# While read
while IFS= read -r line; do
    echo "$line"
done < input.txt
```

## Common One-Liners

### Find Files
```bash
# Files modified in last 24 hours
find . -mtime -1 -type f

# Files larger than 10MB
find . -size +10M -type f

# Find and delete
find . -name "*.tmp" -delete

# Find by content
grep -rl "TODO" --include="*.py" .
```

### Text Processing
```bash
# Replace in file
sed -i 's/old/new/g' file.txt

# Extract between patterns
sed -n '/BEGIN/,/END/p' file.txt

# Count lines/words/chars
wc -l file.txt

# Sort and unique
sort file.txt | uniq -c | sort -rn

# Cut columns
cut -d',' -f1,3 data.csv

# Format with awk
awk '{print $1, $3}' data.txt
awk -F',' '{sum += $2} END {print sum}' data.csv
```

### Git Shortcuts
```bash
# Show last 5 commits
git log --oneline -5

# Find large files in history
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectsize) %(objectname) %(rest)' | \
  awk '/^blob/ {print $2, $3, $4}' | sort -rn | head -10

# Clean untracked files
git clean -fd

# Interactive rebase last N commits
git rebase -i HEAD~5
```

## Useful Patterns

### Safe File Operations
```bash
# Backup before modifying
cp config.yml config.yml.bak

# Temp file with cleanup
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

# Check if file exists before reading
[[ -f "$config" ]] && source "$config"
```

### Argument Parsing
```bash
#!/usr/bin/env bash
set -euo pipefail

VERBOSE=false
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [-v] [-o output]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done
```

### Parallel Execution
```bash
# Run commands in parallel
for file in *.csv; do
    process_file "$file" &
done
wait

# GNU Parallel
parallel process_file ::: *.csv

# xargs parallel
find . -name "*.log" | xargs -P 4 -I {} gzip {}
```

### Error Handling
```bash
#!/usr/bin/env bash
set -euo pipefail

error() {
    echo "ERROR: $*" >&2
    exit 1
}

cleanup() {
    rm -f "$TMPFILE"
}
trap cleanup EXIT

# Retry with backoff
retry() {
    local max_attempts=$1
    local delay=$2
    shift 2
    local cmd=("$@")

    for ((i = 1; i <= max_attempts; i++)); do
        if "${cmd[@]}"; then
            return 0
        fi
        echo "Attempt $i failed, retrying in ${delay}s..."
        sleep "$delay"
        delay=$((delay * 2))
    done
    return 1
}

retry 3 1 curl -f https://example.com
```

## PowerShell Equivalents

```powershell
# Find files
Get-ChildItem -Recurse -Filter *.txt

# Filter
Get-Process | Where-Object { $_.CPU -gt 100 }

# Select properties
Get-ChildItem | Select-Object Name, Length, LastWriteTime

# Sort
Get-Content data.txt | Sort-Object

# Unique
Get-Content data.txt | Sort-Object -Unique

# Replace
(Get-Content file.txt) -replace 'old', 'new' | Set-Content file.txt

# Pipeline
Get-Service | Where-Object Status -eq 'Running' | Select-Object Name
```

## Docker/Container Scripts

```bash
# Wait for service to be ready
wait_for_service() {
    local host=$1 port=$2
    until nc -z "$host" "$port" 2>/dev/null; do
        sleep 1
    done
}

wait_for_service db 5432
echo "Database is ready"
```

## Script Best Practices

1. Always use `set -euo pipefail`
2. Quote variables: `"$var"` not `$var`
3. Use `[[ ]]` over `[ ]` for conditionals
4. Use `local` for function variables
5. Handle errors with `trap`
6. Use `mktemp` for temp files
7. Check command existence before calling
8. Use `--` to separate options from arguments
