---
name: security-audit
description: Security audit patterns, vulnerability detection, OWASP Top 10, secure coding practices, and dependency scanning. Use when the user asks about security reviews, finding vulnerabilities, securing code, OWASP guidelines, secrets detection, or security best practices.
---

# Security Audit

## OWASP Top 10 Quick Reference

### 1. Broken Access Control
```python
# BAD: Check client-side only
if request.headers.get("X-Admin") == "true":
    return admin_data

# GOOD: Verify on server
def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated
```

### 2. Cryptographic Failures
```python
# BAD: Storing plaintext passwords
user.password = request.form["password"]

# GOOD: Hash with bcrypt
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
user.password_hash = hashed
```

### 3. Injection (SQL)
```python
# BAD: String concatenation
query = f"SELECT * FROM users WHERE id = {user_id}"

# GOOD: Parameterized query
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

### 4. Insecure Design
- Apply rate limiting on auth endpoints
- Implement fail-secure defaults
- Separate tenants at the data layer

### 5. Security Misconfiguration
```yaml
# BAD
debug: true
SECRET_KEY: "hardcoded-secret"

# GOOD
debug: ${DEBUG}
SECRET_KEY: ${SECRET_KEY}
```

### 6. Vulnerable Components
```bash
# Check for known vulnerabilities
npm audit
pip-audit
bundle audit
```

### 7. Auth Failures
```python
# Implement account lockout
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

if failed_attempts >= MAX_ATTEMPTS:
    if now - last_attempt < LOCKOUT_DURATION:
        raise TooManyAttempts()
```

### 8. Data Integrity Failures
- Verify file uploads (magic numbers, not just extension)
- Use signed URLs for file access
- Validate CI/CD pipeline integrity

### 9. Logging Failures
```python
# Log security events without exposing secrets
logger.warning("Failed login attempt",
    user_id=user_id,
    ip=request.remote_addr,
    timestamp=datetime.utcnow()
)
# NEVER log: passwords, tokens, full card numbers
```

### 10. SSRF
```python
# BAD: User-controlled URL
resp = requests.get(user_url)

# GOOD: Validate URL target
from urllib.parse import urlparse
import ipaddress

def is_safe_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
        return ip.is_private is False
    except (socket.gaierror, ValueError):
        return False
```

## Secrets Detection

```bash
# Check for hardcoded secrets
grep -rn "password\|secret\|api_key\|token" --include="*.{py,js,ts,go}"
grep -rn "BEGIN.*PRIVATE KEY" --include="*.{pem,key}"

# Use gitleaks
gitleaks detect --source . --verbose
```

## Input Validation

```python
# Whitelist validation
import re

def validate_username(username):
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValidationError("Invalid username")
    return username

# Type validation
from pydantic import BaseModel, constr

class CreateUserRequest(BaseModel):
    username: constr(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    age: int = Field(ge=0, le=150)
```

## XSS Prevention

```javascript
// BAD: Inserting raw HTML
element.innerHTML = userInput;

// GOOD: Use textContent
element.textContent = userInput;

// GOOD: Sanitize if HTML needed
import DOMPurify;
element.innerHTML = DOMPurify.sanitize(userInput);
```

## CSRF Protection

```python
# Flask example
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# In template
<form method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
</form>
```

## Secure Headers

```yaml
# Nginx / server config
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; script-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
```

## Dependency Scanning

```bash
# Python
pip-audit
safety check

# Node
npm audit
npx snyk test

# Go
govulncheck ./...
```

## Checklist

- [ ] All user input validated and sanitized
- [ ] SQL queries use parameterized statements
- [ ] Passwords hashed with bcrypt/argon2
- [ ] HTTPS enforced, HSTS enabled
- [ ] CSRF tokens on state-changing requests
- [ ] Rate limiting on auth endpoints
- [ ] Secrets not in code or version control
- [ ] Dependencies scanned for vulnerabilities
- [ ] Error messages don't leak internals
- [ ] Logging captures security events
- [ ] File uploads validated (type, size)
- [ ] CORS configured restrictively
