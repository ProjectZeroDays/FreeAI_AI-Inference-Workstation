# Migration Guide: Adding Authentication to Quantum C2 Routes

## Overview

This guide helps you migrate from unauthenticated Quantum C2 routes (v1.0) to authenticated routes (v2.0).

## Impact Assessment

### What's Affected

All 30 generated Quantum C2 integration routes:
- `/api/crypto/*` - Cryptographic operations
- `/api/proxy/*` - Proxy management
- `/api/recon/*` - Reconnaissance tools
- `/api/exploit/*` - Exploitation frameworks
- `/api/admin/*` - Administrative operations
- `/api/security/*` - Security tools
- `/api/intel/*` - Threat intelligence
- `/api/tools/*` - Utility tools

### Breaking Changes

1. **All routes now require authentication**
   - Requests without authentication headers will receive HTTP 401
   - Invalid API keys will receive HTTP 401
   - Missing `QUANTUM_C2_API_KEY` configuration will cause HTTP 500

2. **Environment variable required**
   - `QUANTUM_C2_API_KEY` must be set before starting the application
   - Application will fail-secure if not configured

3. **Client code must be updated**
   - All API clients must include authentication headers
   - Three header formats supported: `X-API-Key`, `X-Auth-Token`, `Authorization: Bearer`

## Migration Steps

### Step 1: Generate Secure API Key

Generate a cryptographically secure API key:

```bash
# Option 1: Using OpenSSL (recommended)
openssl rand -hex 32

# Option 2: Using Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Option 3: Using /dev/urandom (Linux/macOS)
head -c 32 /dev/urandom | xxd -p -c 32
```

**Example output:**
```
a7f3c8e9d2b4f1a6c8e5d9f2b7a4c1e8f3d6b9a2c5e8f1d4b7a0c3e6f9d2b5a8
```

### Step 2: Configure Environment Variable

#### Development Environment

```bash
# Linux/macOS - Add to ~/.bashrc or ~/.zshrc
export QUANTUM_C2_API_KEY="your-generated-key-here"

# Windows PowerShell - Add to profile
$env:QUANTUM_C2_API_KEY="your-generated-key-here"

# Windows CMD
set QUANTUM_C2_API_KEY=your-generated-key-here
```

#### Production Environment

**Docker:**
```yaml
# docker-compose.yml
services:
  quantum-c2:
    environment:
      - QUANTUM_C2_API_KEY=${QUANTUM_C2_API_KEY}
```

```bash
# .env file (DO NOT COMMIT)
QUANTUM_C2_API_KEY=your-generated-key-here
```

**Kubernetes:**
```yaml
# Create secret
apiVersion: v1
kind: Secret
metadata:
  name: quantum-c2-secrets
type: Opaque
stringData:
  api-key: your-generated-key-here

---
# Reference in deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quantum-c2
spec:
  template:
    spec:
      containers:
      - name: quantum-c2
        env:
        - name: QUANTUM_C2_API_KEY
          valueFrom:
            secretKeyRef:
              name: quantum-c2-secrets
              key: api-key
```

**Systemd Service:**
```ini
# /etc/systemd/system/quantum-c2.service
[Service]
Environment="QUANTUM_C2_API_KEY=your-generated-key-here"
```

**AWS ECS:**
```json
{
  "containerDefinitions": [{
    "environment": [
      {
        "name": "QUANTUM_C2_API_KEY",
        "value": "your-generated-key-here"
      }
    ]
  }]
}
```

### Step 3: Regenerate Routes

```bash
cd .agents/skills/quantum-c2-auto-complete

# Regenerate all service and router files
python generate_services.py

# Update integration files
python update_integrations.py
```

**Expected output:**
```
Created: C:\Projects\Quantum C2\backend\app\services\openpgpjs_service.py
Created: C:\Projects\Quantum C2\backend\app\routers\openpgpjs_routes.py
...
Done: 30 services, 30 routers

Updated C:\Projects\Quantum C2\backend\app\routers\__init__.py
Updated C:\Projects\Quantum C2\backend\app\api\all_routes.py
Updated C:\Projects\Quantum C2\backend\app\main.py

All integration files updated successfully.
```

### Step 4: Verify Generated Code

Check that authentication is present in a generated router:

```bash
# View a generated router file
cat "C:\Projects\Quantum C2\backend\app\routers\openpgpjs_routes.py"
```

**Verify these components exist:**
- `import os`
- `from fastapi import APIRouter, Depends, HTTPException, Request`
- `QUANTUM_C2_API_KEY = os.environ.get("QUANTUM_C2_API_KEY", "")`
- `def verify_auth(request: Request):`
- `dependencies=[Depends(verify_auth)]` in router definition

### Step 5: Update Client Code

#### Before (v1.0 - Insecure):
```python
import requests

response = requests.post(
    "http://localhost:8000/api/exploit/bettercap/run",
    json={"target": "192.168.1.0/24"}
)
```

#### After (v2.0 - Secure):
```python
import requests
import os

API_KEY = os.environ.get("QUANTUM_C2_API_KEY")

response = requests.post(
    "http://localhost:8000/api/exploit/bettercap/run",
    headers={"X-API-Key": API_KEY},
    json={"target": "192.168.1.0/24"}
)
```

### Step 6: Test Authentication

```bash
# Set API key
export QUANTUM_C2_API_KEY="your-generated-key-here"

# Start application
cd "C:\Projects\Quantum C2\backend"
python -m uvicorn app.main:app --reload

# Test 1: Request without authentication (should fail with 401)
curl http://localhost:8000/api/crypto/pgp/keys

# Test 2: Request with invalid key (should fail with 401)
curl -H "X-API-Key: wrong-key" http://localhost:8000/api/crypto/pgp/keys

# Test 3: Request with valid key (should succeed)
curl -H "X-API-Key: your-generated-key-here" http://localhost:8000/api/crypto/pgp/keys
```

**Expected responses:**

Test 1 & 2:
```json
{"detail": "Unauthorized"}
```

Test 3:
```json
{"status": "ok", "data": {}}
```

### Step 7: Update Documentation

Update your API documentation to include authentication requirements:

```markdown
## Authentication

All Quantum C2 API endpoints require authentication.

Include one of these headers in your requests:
- `X-API-Key: your-api-key`
- `X-Auth-Token: your-api-key`
- `Authorization: Bearer your-api-key`

Contact your administrator for an API key.
```

### Step 8: Distribute API Keys

**For team members:**
1. Generate individual API keys (if implementing per-user keys)
2. Securely share keys (use password manager, encrypted channel)
3. Document key rotation policy
4. Provide usage examples

**For automated systems:**
1. Store keys in secrets management system (Vault, AWS Secrets Manager, etc.)
2. Inject keys via environment variables
3. Implement key rotation automation
4. Monitor for unauthorized access attempts

## Rollback Plan

If you need to temporarily rollback to unauthenticated routes:

### Option 1: Use Previous Version (Not Recommended)

```bash
# Checkout previous version of generate_services.py
git checkout HEAD~1 .agents/skills/quantum-c2-auto-complete/generate_services.py

# Regenerate routes
python generate_services.py
python update_integrations.py
```

**WARNING:** This removes all authentication. Only use in isolated development environments.

### Option 2: Temporary Bypass (Emergency Only)

Modify generated routers to remove authentication:

```python
# Change this:
router = APIRouter(prefix="/api/...", tags=["..."], dependencies=[Depends(verify_auth)])

# To this:
router = APIRouter(prefix="/api/...", tags=["..."])
```

**WARNING:** This creates a critical security vulnerability. Only use for emergency troubleshooting.

## Validation Checklist

After migration, verify:

- [ ] `QUANTUM_C2_API_KEY` environment variable is set
- [ ] All 30 router files have been regenerated
- [ ] Generated routers include `verify_auth` function
- [ ] Generated routers include `dependencies=[Depends(verify_auth)]`
- [ ] Application starts without errors
- [ ] Requests without authentication receive HTTP 401
- [ ] Requests with invalid keys receive HTTP 401
- [ ] Requests with valid keys succeed
- [ ] All client code has been updated
- [ ] API documentation has been updated
- [ ] Team members have received API keys
- [ ] Monitoring/alerting is configured for auth failures

## Troubleshooting

### Issue: HTTP 500 "QUANTUM_C2_API_KEY environment variable not configured"

**Cause:** Environment variable not set

**Solution:**
```bash
export QUANTUM_C2_API_KEY="your-key"
# Restart application
```

### Issue: HTTP 401 "Unauthorized" with correct key

**Possible causes:**
1. Key has extra whitespace
2. Key doesn't match environment variable
3. Environment variable not loaded by application

**Debug:**
```python
# Add to router file temporarily
import os
print(f"Configured key: {os.environ.get('QUANTUM_C2_API_KEY', 'NOT SET')}")
print(f"Provided key: {request.headers.get('X-API-Key', 'NOT PROVIDED')}")
```

### Issue: Some routes still unauthenticated

**Cause:** Routes not regenerated or old files cached

**Solution:**
```bash
# Delete old router files
rm "C:\Projects\Quantum C2\backend\app\routers\*_routes.py"

# Regenerate
python generate_services.py
python update_integrations.py

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Restart application
```

### Issue: Client code failing after migration

**Cause:** Client not sending authentication headers

**Solution:**
```python
# Add authentication header to all requests
headers = {"X-API-Key": os.environ.get("QUANTUM_C2_API_KEY")}
response = requests.post(url, headers=headers, json=data)
```

## Security Best Practices

After migration:

1. **Rotate keys regularly** (e.g., every 90 days)
2. **Use HTTPS in production** to protect keys in transit
3. **Monitor authentication failures** for potential attacks
4. **Implement rate limiting** to prevent brute force
5. **Use different keys per environment** (dev, staging, prod)
6. **Store keys securely** (secrets manager, not in code)
7. **Audit API access** regularly
8. **Revoke compromised keys** immediately

## Support

If you encounter issues during migration:

1. Review this guide thoroughly
2. Check application logs for detailed error messages
3. Verify environment variable is set correctly
4. Test with a simple endpoint first
5. Ensure all files were regenerated
6. Clear Python cache and restart application

For security concerns, follow your organization's security incident response procedures.

## Additional Resources

- [SECURITY.md](./SECURITY.md) - Complete security documentation
- [README.md](./README.md) - Generator usage and architecture
- [test_authentication.py](./test_authentication.py) - Authentication test suite
