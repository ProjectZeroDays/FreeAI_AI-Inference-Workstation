# Quantum C2 Auto-Complete Security Configuration

## Overview

The Quantum C2 auto-complete generator creates FastAPI routers for 30 security tools including:
- Exploitation frameworks (Bettercap, GrapheneX, BloodyAD, Fastjson RCE)
- Administrative tools (Nginx Proxy Manager, OpenVPN, DNSCrypt, Certbot)
- Reconnaissance tools (Amass, Asscan, Active Onions, Webscraping)
- Cryptographic tools (OpenPGP, Nucypher, DCipher, Hash Detector)
- Proxy tools (Shadowsocks, V2Ray, Mitmproxy)
- Attack simulation (Attack Range, Password Spraying, King Phisher)
- Threat intelligence (OpenCTI, Cowrie Honeypot)

All generated routes now require authentication by default.

## Authentication Mechanism

### API Key Authentication

All generated routers enforce API key authentication using the `QUANTUM_C2_API_KEY` environment variable.

**Supported Authentication Headers:**
- `X-API-Key: <your-api-key>`
- `X-Auth-Token: <your-api-key>`
- `Authorization: Bearer <your-api-key>`

### Configuration

**REQUIRED:** Set the `QUANTUM_C2_API_KEY` environment variable before starting the application:

```bash
export QUANTUM_C2_API_KEY="your-secure-random-key-here"
```

**Generate a secure API key:**
```bash
# Linux/macOS
openssl rand -hex 32

# Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Security Behavior

1. **Missing API Key Configuration:**
   - If `QUANTUM_C2_API_KEY` is not set, all endpoints return HTTP 500
   - Error: "QUANTUM_C2_API_KEY environment variable not configured"
   - This prevents accidental deployment without authentication

2. **Invalid or Missing Authentication:**
   - If no authentication header is provided, returns HTTP 401
   - If authentication header doesn't match the configured key, returns HTTP 401
   - Error: "Unauthorized"

3. **Valid Authentication:**
   - Request proceeds to the service handler
   - Full access to all endpoint functionality

## Implementation Details

### Router-Level Authentication

Authentication is enforced at the router level using FastAPI's `dependencies` parameter:

```python
router = APIRouter(
    prefix="/api/...",
    tags=["..."],
    dependencies=[Depends(verify_auth)]
)
```

This ensures:
- All routes under the router are protected
- Authentication is checked before any endpoint handler executes
- No bypass is possible without modifying the generated code

### Authentication Function

Each generated router includes a `verify_auth` dependency:

```python
def verify_auth(request: Request):
    """Verify API key authentication for Quantum C2 endpoints."""
    if not QUANTUM_C2_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="QUANTUM_C2_API_KEY environment variable not configured"
        )
    
    provided = (
        request.headers.get("X-API-Key")
        or request.headers.get("X-Auth-Token")
        or request.headers.get("Authorization", "").replace("Bearer ", "")
    )
    
    if provided != QUANTUM_C2_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return True
```

## Usage Examples

### cURL

```bash
# Using X-API-Key header
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/exploit/bettercap/run \
  -X POST -d '{"target": "192.168.1.0/24"}'

# Using Authorization Bearer header
curl -H "Authorization: Bearer your-api-key" \
  http://localhost:8000/api/admin/nginx-pm/status

# Using X-Auth-Token header
curl -H "X-Auth-Token: your-api-key" \
  http://localhost:8000/api/recon/amass/enumerate \
  -X POST -d '{"domain": "example.com"}'
```

### Python Requests

```python
import requests

API_KEY = "your-api-key"
BASE_URL = "http://localhost:8000"

# Using X-API-Key header
headers = {"X-API-Key": API_KEY}
response = requests.post(
    f"{BASE_URL}/api/exploit/bettercap/run",
    headers=headers,
    json={"target": "192.168.1.0/24"}
)

# Using Authorization Bearer header
headers = {"Authorization": f"Bearer {API_KEY}"}
response = requests.get(
    f"{BASE_URL}/api/admin/nginx-pm/status",
    headers=headers
)
```

### JavaScript/Fetch

```javascript
const API_KEY = "your-api-key";
const BASE_URL = "http://localhost:8000";

// Using X-API-Key header
fetch(`${BASE_URL}/api/exploit/bettercap/run`, {
  method: "POST",
  headers: {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ target: "192.168.1.0/24" })
});

// Using Authorization Bearer header
fetch(`${BASE_URL}/api/admin/nginx-pm/status`, {
  headers: {
    "Authorization": `Bearer ${API_KEY}`
  }
});
```

## Deployment Checklist

- [ ] Generate a cryptographically secure API key
- [ ] Set `QUANTUM_C2_API_KEY` environment variable in production
- [ ] Store API key securely (e.g., secrets manager, encrypted vault)
- [ ] Rotate API key periodically
- [ ] Use HTTPS in production to protect API key in transit
- [ ] Implement rate limiting at the infrastructure level
- [ ] Monitor authentication failures for potential attacks
- [ ] Document API key distribution process for authorized users
- [ ] Implement API key revocation procedure

## Additional Security Considerations

### Network-Level Controls

While authentication is now enforced, consider additional defense-in-depth measures:

1. **Network Segmentation:** Deploy Quantum C2 on an isolated network segment
2. **Firewall Rules:** Restrict access to authorized IP addresses/ranges
3. **VPN/Bastion:** Require VPN or bastion host access
4. **Rate Limiting:** Implement rate limiting to prevent brute force attacks

### Application-Level Enhancements

For production deployments, consider implementing:

1. **Role-Based Access Control (RBAC):** Different permissions for different users
2. **Audit Logging:** Log all API access with user identity and actions
3. **Multi-Factor Authentication:** Additional authentication factors
4. **API Key Scoping:** Different keys with different permission levels
5. **Temporary Tokens:** Short-lived tokens instead of long-lived API keys

### Monitoring and Alerting

Monitor for:
- Failed authentication attempts (potential brute force)
- Unusual access patterns (potential compromise)
- Access from unexpected IP addresses
- High-risk operations (exploitation, admin changes)

## Regenerating Routes

After modifying `generate_services.py`, regenerate all routes:

```bash
cd .agents/skills/quantum-c2-auto-complete
python generate_services.py
python update_integrations.py
```

All newly generated routes will include authentication enforcement.

## Support

For security issues or questions:
1. Review this documentation
2. Check environment variable configuration
3. Verify API key is correctly set and matches
4. Review application logs for authentication errors
5. Test with a simple endpoint first (e.g., `/api/tools/hex/convert`)

## Version History

- **v2.0** (Current): Added mandatory API key authentication to all generated routes
- **v1.0** (Deprecated): No authentication - INSECURE, do not use in production
