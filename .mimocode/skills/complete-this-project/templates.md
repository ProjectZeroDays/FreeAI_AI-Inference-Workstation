# Audit Templates

Reusable audit templates for different project aspects.

## Dashboard Audit

```markdown
## Dashboard Coverage Audit

| Dashboard | Template | Backend Route | API Endpoints | Tests | Status |
|-----------|----------|---------------|---------------|-------|--------|
| Todos | todos.html | /todos | GET/POST /api/todos | 46 | ✅ |
| Salad | salad.html | /salad | GET/POST /api/salad/* | ? | ⚠️ |
| Encryption | encryption.html | /encryption | GET/POST /api/encryption/* | ? | ⚠️ |
| Remote Access | remote-access.html | /remote-access | GET/POST /api/remote-access/* | ? | ⚠️ |
```

## API Coverage Audit

```markdown
## Backend API Coverage Audit

| Endpoint | Method | Auth Required | Frontend UI | Tests | Status |
|----------|--------|--------------|-------------|-------|--------|
| /api/todos | GET | ✅ | todos.html | 46 | ✅ |
| /api/todos | POST | ✅ | todos.html | ? | ⚠️ |
| /api/auth/login | POST | ❌ | login.html | ? | ⚠️ |
```

## Test Coverage Audit

```markdown
## Test Coverage Audit

| Module | File | Tests | Coverage | Status |
|--------|------|-------|----------|--------|
| todos | tests/test_todos.py | 46 | 100% | ✅ |
| auth | tests/test_jwt.py | 16 | 80% | ⚠️ |
| secrets | tests/test_secrets.py | 29 | 90% | ✅ |
```

## Security Audit

```markdown
## Security Vulnerability Scan

| Category | Finding | Severity | File | Status |
|----------|---------|----------|------|--------|
| Hardcoded Secrets | API key in source | HIGH | ? | ⚠️ |
| Input Validation | Missing on /api/endpoint | MEDIUM | ? | ⚠️ |
| Auth Bypass | Unprotected endpoint | HIGH | ? | ⚠️ |
```

## UI Consistency Audit

```markdown
## UI Consistency Audit

| Check | Criteria | Status |
|-------|----------|--------|
| CSS Variables | All pages use --bg, --panel, --border | ? |
| Theme Toggle | Dark/light switch works on all pages | ? |
| Responsive | Mobile layout on all pages | ? |
| Accessibility | ARIA labels, keyboard nav | ? |
| Loading States | Spinners on all async operations | ? |
| Error Handling | Inline errors on all forms | ? |
```
