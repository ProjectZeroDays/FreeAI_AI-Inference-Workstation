---
name: code-search
description: Advanced code search patterns, grep/ripgrep techniques, AST-based search, code navigation, and codebase exploration. Use when the user asks about finding code patterns, searching across codebases, using grep/ripgrep effectively, or exploring unfamiliar code.
---

# Code Search

## Grep Patterns

### Basic Search
```bash
# Search for exact string
grep -r "functionName" src/

# Case-insensitive
grep -ri "error" src/

# Include specific file types
grep -r "TODO" --include="*.ts" --include="*.js" src/

# Exclude directories
grep -r "deprecated" --exclude-dir=node_modules --exclude-dir=dist src/

# Show line numbers
grep -rn "console.log" src/

# Count matches per file
grep -rc "import.*from" src/ | grep -v ":0$"
```

### Regex Patterns
```bash
# Find function definitions
grep -rn "function \w\+(" src/

# Find class definitions
grep -rn "class \w\+" src/

# Find imports
grep -rn "import.*from ['\"]" src/

# Find TODO/FIXME/HACK
grep -rn "TODO\|FIXME\|HACK\|XXX" src/

# Find console.log (for cleanup)
grep -rn "console\.\(log\|debug\|info\)" src/

# Find async functions
grep -rn "async function\|async (" src/

# Find type definitions
grep -rn "interface \|type \|enum " src/
```

## Ripgrep (rg) Patterns

```bash
# Faster recursive search
rg "pattern" src/

# Search with context (3 lines before/after)
rg -C 3 "function" src/

# Search with file type filter
rg -t ts "interface" src/
rg -t py "def " src/

# Search specific files
rg -g "*.test.ts" "describe\(" src/

# Word match (whole word only)
rg -w "test" src/

# Fixed string (no regex)
rg -F "console.log('debug')" src/

# Multiline search
rg -U "import.*\n.*from" src/

# JSON output
rg --json "pattern" src/

# Count matches
rg -c "function" src/ | sort -t: -k2 -rn
```

## AST-Based Search

### Using tree-sitter (Python)
```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def find_functions(source_code: str) -> list[dict]:
    tree = parser.parse(bytes(source_code, "utf8"))
    
    query = PY_LANGUAGE.query("""
        (function_definition
            name: (identifier) @name
            parameters: (parameters) @params
            body: (block) @body) @func
    """)
    
    matches = query.matches(tree.root_node)
    results = []
    for match in matches:
        results.append({
            "name": match["captures"]["name"][0].text.decode(),
            "start": match["captures"]["func"][0].start_point,
            "end": match["captures"]["func"][0].end_point,
        })
    return results
```

### Using ripgrep with AST patterns
```bash
# Find all exported functions
rg "export (default )?(async )?function \w+" src/

# Find React components
rg "export (default )?(function|const) \w+\s*[:(]" --include="*.tsx" src/

# Find API routes
rg "app\.(get|post|put|delete)\(" src/
rg "router\.(get|post|put|delete)\(" src/
```

## Code Navigation

### Find Definition
```bash
# Find where a function is defined
rg -l "function calculateTotal" src/
rg -l "def calculate_total" src/
rg -l "class UserService" src/

# Find all usages
rg -n "calculateTotal" src/
rg -n "UserService" src/
```

### Find References
```bash
# Find imports of a module
rg "from ['\"].*user" src/
rg "import.*['\"].*user" src/

# Find where a file is imported
rg "from ['\"].*user-service" src/
rg -l "user-service" src/
```

## Search Strategies

### Exploring New Codebase
```bash
# 1. Project structure
find . -type f -name "*.ts" -o -name "*.tsx" | head -20

# 2. Entry points
rg "createApp\|createServer\|main\(" src/

# 3. Configuration
rg "export default\|module.exports" -g "config*" src/

# 4. Database models
rg "Schema\|model\|@Entity" src/

# 5. API routes
rg "router\.\w+\(|app\.\w+\(" src/
```

### Finding Patterns
```bash
# Find error handling patterns
rg "catch|except|raise|throw" src/

# Find logging patterns
rg "log\(|logger\.|console\." src/

# Find authentication
rg "auth|token|jwt|session" src/

# Find database queries
rg "SELECT|INSERT|UPDATE|DELETE|query\(" src/
```

## IDE-Style Search

### VS Code Search (via CLI)
```bash
# Search with context
code -g "src/**/*" --grep "pattern"

# Find files
code src/**/*test*.ts
```

### Using fzf
```bash
# Find files interactively
find . -type f -name "*.ts" | fzf

# Search content interactively
rg -l "pattern" . | fzf

# Preview file content
find . -type f -name "*.ts" | fzf --preview 'cat {}'
```

## Search Filters

```bash
# By date (modified recently)
find . -name "*.ts" -mtime -7

# By size
find . -name "*.ts" -size +100k

# By content
grep -rl "deprecated" --include="*.ts" src/

# By git status
git diff --name-only           # Changed files
git diff --cached --name-only  # Staged files
git log --diff-filter=D --name-only  # Deleted files
```

## Useful Aliases

```bash
# Add to .bashrc/.zshrc
alias g="grep -rn"
alias rg="rg --hidden --glob '!.git'"
alias ffind="find . -type f -name"
alias ff="find . -type f | fzf"
```
