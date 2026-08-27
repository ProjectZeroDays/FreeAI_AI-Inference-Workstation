# Autonomous API Security

## Overview

The Autonomous SDLC API now requires authentication for all write and execute operations to prevent unauthorized access and code execution.

## Authentication

### Environment Variable

Set the `AUTONOMOUS_API_KEY` environment variable to enable authentication:

```bash
export AUTONOMOUS_API_KEY="your-secure-random-key-here"
```

**Important:** Use a strong, randomly generated key. Example generation:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Authentication Headers

When `AUTONOMOUS_API_KEY` is set, all protected endpoints require one of these headers:

- `X-API-Key: <your-key>`
- `X-Auth-Token: <your-key>`
- `Authorization: Bearer <your-key>`

### Protected Endpoints

The following endpoints require authentication when `AUTONOMOUS_API_KEY` is set:

- `POST /auto/start` - Start a new autonomous run
- `POST /auto/runs/{run_id}/cancel` - Cancel a running job
- `POST /auto/runs/{run_id}/shell` - Execute shell commands in a workspace

### Public Endpoints

These endpoints remain accessible without authentication for monitoring:

- `GET /health` - Service health check
- `GET /auto/runs` - List all runs
- `GET /auto/runs/{run_id}` - Get run details
- `GET /auto/runs/{run_id}/artifact` - Download run artifact

## Usage Examples

### CLI (freeai.py)

The CLI automatically uses `AUTONOMOUS_API_KEY` from the environment:

```bash
export AUTONOMOUS_API_KEY="your-key"
python3 freeai.py auto-start "Build a REST API"
python3 freeai.py auto-cancel <run-id>
```

### cURL

```bash
# Start a run
curl -X POST http://localhost:8050/auto/start \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"spec": "Build a REST API", "profile": "balanced"}'

# Cancel a run
curl -X POST http://localhost:8050/auto/runs/<run-id>/cancel \
  -H "X-API-Key: your-key"

# Execute shell command (requires ENABLE_SHELL_TOOLS=1)
curl -X POST http://localhost:8050/auto/runs/<run-id>/shell \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la"}'
```

### Python

```python
import requests
import os

API_KEY = os.environ.get("AUTONOMOUS_API_KEY")
headers = {"X-API-Key": API_KEY}

# Start a run
response = requests.post(
    "http://localhost:8050/auto/start",
    json={"spec": "Build a REST API", "profile": "balanced"},
    headers=headers
)
run_id = response.json()["run_id"]

# Check status (no auth required)
status = requests.get(f"http://localhost:8050/auto/runs/{run_id}")
print(status.json())
```

## MCP Integration

The MCP SDLC server (`mcp/servers/sdlc.py`) automatically uses `AUTONOMOUS_API_KEY` from the environment when making API calls.

## Deployment Recommendations

### Development

For local development, authentication is optional. If `AUTONOMOUS_API_KEY` is not set, the API operates without authentication.

### Production

**Always set `AUTONOMOUS_API_KEY` in production environments**, especially when:

1. The service is exposed to the internet
2. `ENABLE_SHELL_TOOLS=1` is enabled
3. Multiple users or services access the API

### Additional Security Measures

1. **Network Isolation**: Keep the autonomous API on a private network when possible
2. **Firewall Rules**: Use UFW or iptables to restrict access to port 8050
3. **Reverse Proxy**: Use Caddy/nginx with TLS and additional authentication layers
4. **Shell Tools**: Only enable `ENABLE_SHELL_TOOLS=1` when necessary
5. **Monitoring**: Monitor the `/auto/runs` endpoint for suspicious activity

## Migration Guide

### Existing Deployments

1. Generate a secure API key:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Set the environment variable in your deployment:
   - Docker Compose: Add to `environment:` section
   - Systemd: Add to service file's `Environment=` directive
   - Kubernetes: Add to deployment's `env:` section

3. Update clients to include the authentication header

4. Restart the autonomous service

### Backward Compatibility

- If `AUTONOMOUS_API_KEY` is not set, the API operates without authentication (for local dev)
- Existing clients will receive 401 errors if they don't provide the key
- Read-only endpoints remain accessible without authentication

## Security Considerations

### Run Ownership

The API now tracks an optional `owner` field for runs. While currently not enforced for authorization, this enables future fine-grained access control where users can only access their own runs.

### Shell Command Execution

Shell command execution (`/auto/runs/{run_id}/shell`) is protected by:

1. Authentication (when `AUTONOMOUS_API_KEY` is set)
2. Global shell tools flag (`ENABLE_SHELL_TOOLS=1` required)
3. Run existence check
4. Workspace isolation (commands execute in sandboxed workspace)

### Test Execution

When `ENABLE_SHELL_TOOLS=1` and `enable_shell: true` are set:

- Generated Python test files are executed via pytest/unittest
- Tests run in isolated workspace directories
- Authentication prevents unauthorized test execution

## Troubleshooting

### 401 Unauthorized

- Verify `AUTONOMOUS_API_KEY` is set in the environment
- Check that the client is sending the correct header
- Ensure the key matches exactly (no extra whitespace)

### Shell Commands Fail

- Verify `ENABLE_SHELL_TOOLS=1` is set
- Check that authentication is provided
- Ensure the run exists and is in a valid state

## Related Documentation

- [SECURITY.md](SECURITY.md) - Overall security policy
- [README.md](README.md) - Environment variables reference
- [docs/SDLC-TUTORIAL.md](docs/SDLC-TUTORIAL.md) - Autonomous SDLC usage guide
