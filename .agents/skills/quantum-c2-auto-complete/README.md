# Quantum C2 Auto-Complete Generator

## Security Update - BREAKING CHANGE

**Version 2.0** introduces mandatory authentication for all generated routes.

### What Changed

All generated FastAPI routers now require API key authentication. Previously, routes were generated without any authentication mechanism, making them accessible to anyone who could reach the API.

### Migration Required

If you have previously generated routes using this tool, you must:

1. **Set the API Key Environment Variable:**
   ```bash
   export QUANTUM_C2_API_KEY="$(openssl rand -hex 32)"
   ```

2. **Regenerate All Routes:**
   ```bash
   python generate_services.py
   python update_integrations.py
   ```

3. **Update API Clients:**
   All API clients must now include authentication headers:
   ```bash
   curl -H "X-API-Key: your-api-key" http://localhost:8000/api/...
   ```

### Why This Change Was Made

The previous version generated routes for sensitive operations including:
- Exploitation frameworks (Bettercap, BloodyAD, Fastjson RCE)
- Administrative tools (OpenVPN installation, Nginx proxy management)
- Reconnaissance tools (Amass, subdomain enumeration)
- Password spraying and phishing campaign management

These routes were accessible without any authentication, creating a critical security vulnerability.

### Security Model

**Authentication is now enforced at the router level:**
- Every generated router includes a `verify_auth` dependency
- The dependency is applied to the entire router using `dependencies=[Depends(verify_auth)]`
- All routes under the router are automatically protected
- No individual route can bypass authentication

**Fail-secure by default:**
- If `QUANTUM_C2_API_KEY` is not configured, all endpoints return HTTP 500
- This prevents accidental deployment without authentication
- Operators must explicitly configure authentication to use the API

### Documentation

See [SECURITY.md](./SECURITY.md) for:
- Complete authentication documentation
- Configuration instructions
- Usage examples
- Deployment checklist
- Additional security recommendations

## Usage

### Generate Services and Routes

```bash
python generate_services.py
```

This generates 30 service files and 30 router files for the Quantum C2 integration.

### Update Integration Files

```bash
python update_integrations.py
```

This updates the application's route registration to include all generated routers.

### Generated Tools

The generator creates authenticated routes for:

**Cryptographic Tools:**
- OpenPGP.js (PGP encryption/decryption)
- Nucypher (threshold cryptography)
- DCipher (hash/encoding detection)
- Hash Detector (hash type identification)

**Proxy & Anonymity:**
- Shadowsocks Manager
- Shadowsocks REST API
- V2Ray Plugin
- DNSCrypt Proxy

**Reconnaissance:**
- Amass (subdomain enumeration)
- Asscan (AS number scanning)
- Active Onions (Tor hidden services)
- Webscraping Framework

**Exploitation:**
- Bettercap (MITM attacks)
- GrapheneX (network exploitation)
- BloodyAD (Active Directory attacks)
- Fastjson RCE (exploitation testing)
- Password Spraying Toolkit
- King Phisher (phishing campaigns)

**Administrative:**
- Nginx Proxy Manager
- OpenVPN Installer
- Certbot (SSL certificates)

**Security & Defense:**
- Tor Detection
- Cowrie Honeypot
- Attack Range (MITRE ATT&CK simulation)

**Analysis & Intelligence:**
- OpenCTI (threat intelligence)
- Binary Analyzer
- URL Analyzer
- Hex Tools
- Mitmproxy
- Security Toolbox

## Architecture

### Service Layer
Each tool gets a service class with:
- Async methods for all operations
- Result storage and retrieval
- Cleanup methods
- Singleton pattern

### Router Layer
Each tool gets a FastAPI router with:
- **Authentication enforcement** (NEW in v2.0)
- REST endpoints for all operations
- Proper HTTP methods (GET, POST, PUT, DELETE)
- Path parameters where appropriate
- Request/response models

### Integration Layer
The `update_integrations.py` script:
- Updates `routers/__init__.py` with imports
- Updates `api/all_routes.py` with route registration
- Updates `main.py` with service initialization

## Development

### Adding a New Tool

1. Add tool definition to `TOOLS` list in `generate_services.py`:
```python
{
    "name": "tool_name",
    "service_class": "ToolNameService",
    "get_func": "get_tool_name_service",
    "prefix": "/api/category/tool-name",
    "tag": "Tool Display Name",
    "routes": [
        ("POST", "/action", "action_method", "Action description"),
        ("GET", "/results", "get_results", "Get results"),
    ],
    "features": "Brief description of tool features"
}
```

2. Add to `TOOLS` list in `update_integrations.py`

3. Add prefix mapping in `PREFIXES` dict in `update_integrations.py`

4. Add service mapping in `SERVICE_MAP` dict in `update_integrations.py`

5. Run both scripts to generate and integrate

### Testing Generated Routes

```bash
# Set API key
export QUANTUM_C2_API_KEY="test-key-123"

# Start the application
cd "C:\Projects\Quantum C2\backend"
python -m uvicorn app.main:app --reload

# Test an endpoint
curl -H "X-API-Key: test-key-123" \
  http://localhost:8000/api/crypto/pgp/keys
```

## Security Considerations

### Authentication is Mandatory

All generated routes require authentication. This is enforced at the router level and cannot be bypassed without modifying the generated code.

### Environment Variable Security

- Never commit `QUANTUM_C2_API_KEY` to version control
- Use a secrets manager in production
- Rotate keys periodically
- Use different keys for different environments

### Additional Protections

Consider implementing:
- Rate limiting
- IP allowlisting
- VPN/bastion host requirements
- Audit logging
- Role-based access control (RBAC)

See [SECURITY.md](./SECURITY.md) for detailed security guidance.

## Troubleshooting

### HTTP 500: "QUANTUM_C2_API_KEY environment variable not configured"

**Cause:** The `QUANTUM_C2_API_KEY` environment variable is not set.

**Solution:**
```bash
export QUANTUM_C2_API_KEY="your-secure-key"
```

### HTTP 401: "Unauthorized"

**Cause:** The provided API key doesn't match the configured key.

**Solution:**
- Verify the API key is correct
- Check the authentication header format
- Ensure no extra whitespace in the key

### Routes Not Found

**Cause:** Routes haven't been generated or integrated.

**Solution:**
```bash
python generate_services.py
python update_integrations.py
# Restart the application
```

## License

This tool generates code for the Quantum C2 project. Refer to the main project license.

## Changelog

### Version 2.0 (Current)
- **BREAKING:** Added mandatory API key authentication to all generated routes
- Added `verify_auth` dependency function to each router
- Added `QUANTUM_C2_API_KEY` environment variable requirement
- Added comprehensive security documentation
- Fail-secure by default (HTTP 500 if API key not configured)

### Version 1.0 (Deprecated - INSECURE)
- Initial release
- Generated routes without authentication
- **DO NOT USE IN PRODUCTION**
