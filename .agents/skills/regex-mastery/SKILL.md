---
name: regex-mastery
description: Regular expression patterns, common use cases, and debugging. Use when the user asks about writing regex, parsing text patterns, validating input with regex, or understanding/fixing regular expressions.
---

# Regex Mastery

## Core Syntax

| Pattern | Matches |
|---------|---------|
| `.` | Any character except newline |
| `\d` | Digit [0-9] |
| `\D` | Non-digit |
| `\w` | Word character [a-zA-Z0-9_] |
| `\W` | Non-word character |
| `\s` | Whitespace |
| `\S` | Non-whitespace |
| `\b` | Word boundary |
| `^` | Start of string/line |
| `$` | End of string/line |

## Quantifiers

| Pattern | Meaning |
|---------|---------|
| `*` | 0 or more |
| `+` | 1 or more |
| `?` | 0 or 1 (also: lazy when after quantifier) |
| `{n}` | Exactly n |
| `{n,}` | n or more |
| `{n,m}` | Between n and m |
| `*?`, `+?` | Lazy (non-greedy) versions |

## Character Classes

```
[abc]      → a, b, or c
[^abc]     → not a, b, or c
[a-z]      → lowercase letter
[A-Za-z]   → any letter
[0-9]      → digit
[^0-9]     → non-digit
```

## Groups and Capturing

```
(abc)           → capturing group 1
(?:abc)         → non-capturing group
(?<name>abc)    → named group
\1              → backreference to group 1
```

## Common Patterns

### Email
```regex
[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
```

### URL
```regex
https?:\/\/[^\s/$.?#].[^\s]*
```

### Phone (US)
```regex
\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}
```

### IP Address (v4)
```regex
\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b
```

### Date (YYYY-MM-DD)
```regex
\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])
```

### Hex Color
```regex
#(?:[0-9a-fA-F]{3}){1,2}\b
```

### Strong Password
```regex
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$
```

### HTML Tag
```regex
<([a-z]+)([^<]*)(?:>(.*)<\/\1>|\s*\/>)
```

### Markdown Link
```regex
\[([^\]]+)\]\(([^)]+)\)
```

## Lookaheads and Lookbehinds

```
(?=abc)    → positive lookahead: abc must follow
(?!abc)    → negative lookahead: abc must NOT follow
(?<=abc)   → positive lookbehind: abc must precede
(?<!abc)   → negative lookbehind: abc must NOT precede
```

### Examples
```regex
\b\w+(?=\s+account)  → word before "account"
(?<=@)[\w.-]+        → domain part of email
(?<!\w)the(?!\w)      → "the" as standalone word
```

## Flags

| Flag | Effect |
|------|--------|
| `g` | Global (all matches) |
| `i` | Case-insensitive |
| `m` | Multiline (^/$ match line boundaries) |
| `s` | Dotall (`.` matches newline) |
| `u` | Unicode |

## Python Examples

```python
import re

# Find all emails
emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)

# Search with groups
match = re.search(r'(\d{4})-(\d{2})-(\d{2})', 'Born 1990-05-15')
if match:
    year, month, day = match.groups()

# Replace
result = re.sub(r'\bfoo\b', 'bar', text, flags=re.IGNORECASE)

# Split
words = re.split(r'[,;\s]+', 'hello, world;  foo   bar')

# Compile for reuse
EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
all_emails = EMAIL_RE.findall(text)
```

## JavaScript Examples

```javascript
// Test pattern
/^[a-z]+$/i.test("Hello")  // false

// Match with flags
"Hello World".match(/\b\w+\b/g)  // ["Hello", "World"]

// Replace
"foo bar foo".replace(/\bfoo\b/g, "baz")  // "baz bar baz"

// Named groups
"2024-01-15".match(/(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/)

// Validate
const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
```

## Debugging Tips

1. Use regex101.com for testing and explanation
2. Start simple, add complexity incrementally
3. Use non-capturing groups `(?:...)` when you don't need the capture
4. Use named groups for readability: `(?P<name>...)`
5. Avoid catastrophic backtracking: don't nest quantifiers like `(a+)+`
6. Use `\b` word boundaries for whole-word matching
7. Prefer `.*?` (lazy) over `.*` (greedy) when you want minimal match
