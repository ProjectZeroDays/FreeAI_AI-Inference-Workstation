# MCP Server Security

## Overview

The MCP (Model Context Protocol) server provides a gateway to FreeAI's internal services including routing, agents, workflows, and autonomous operations. As of this security update, the MCP server implements authentication to prevent unauthorized access.

## Authentication

### Configuration

Set the `MCP_API_KEY` environment variable to enable authentication:

```bash
export MCP_API_KEY="your-secret-key-here"
```

When `MCP_API_KEY` is set, all endpoints except `/health` require authentication.

### Authentication Methods

The MCP server accepts authentication via any of the following headers:

1. **X-API-Key header**
   ```
   X-API-Key: your-secret-key-here
   ```

2. **X-Auth-Token header**
   ```
   X-Auth-Token: your-secret-key-here
   ```

3. **Authorization Bearer token**
   ```
   Authorization: Bearer your-secret-key-here
   ```

### Example Requests

**Without authentication (when MCP_API_KEY is not set):**
```bash
curl http://localhost:8090/mcp/tools
```

**With authentication (when MCP_API_KEY is set):**
```bash
curl -H "X-API-Key: your-secret-key-here" http://localhost:8090/mcp/tools
```

```bash
curl -H "Authorization: Bearer your-secret-key-here" \
  -X POST http://localhost:8090/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "route", "args": {"prompt": "Hello"}}'
```

## Security Considerations

### Network Binding

The MCP server binds to `0.0.0.0` by default, making it accessible from all network interfaces. When deploying in production:

1. **Always set MCP_API_KEY** to require authentication
2. **Use a strong, randomly generated key** (minimum 32 characters)
3. **Consider network-level restrictions** (firewall rules, VPC configuration)
4. **Use TLS/HTTPS** when exposing the service externally

### Downstream Service Authentication

When `MCP_API_KEY` is configured, the MCP server forwards the authentication header to downstream services (router, agents, workflow, autonomous). Ensure these services are also configured with matching API keys:

```bash
export MCP_API_KEY="shared-secret"
export ROUTER_API_KEY="shared-secret"
export AGENT_API_KEY="shared-secret"
```

### Health Endpoint

The `/health` endpoint is intentionally excluded from authentication requirements to support:
- Load balancer health checks
- Container orchestration readiness probes
- Monitoring systems

The health endpoint only returns status information and whether authentication is required.

## Deployment Recommendations

### Development

For local development, authentication can be disabled by leaving `MCP_API_KEY` unset:

```bash
python mcp/server.py
```

### Production

For production deployments, always enable authentication:

```bash
export MCP_API_KEY="$(openssl rand -base64 32)"
python mcp/server.py
```

Or using Docker:

```bash
docker run -e MCP_API_KEY="your-secret-key" -p 8090:8090 freeai-mcp
```

### Docker Compose

Add to your `.env` file:

```
MCP_API_KEY=your-secret-key-here
```

## Testing

Run the authentication tests:

```bash
pytest tests/test_mcp_server.py -v
```

## Migration Guide

If you have existing MCP clients:

1. **Generate a secure API key:**
   ```bash
   openssl rand -base64 32
   ```

2. **Set the environment variable:**
   ```bash
   export MCP_API_KEY="generated-key"
   ```

3. **Update your clients** to include the authentication header in all requests (except `/health`)

4. **Verify authentication is working:**
   ```bash
   # Should return 401 Unauthorized
   curl http://localhost:8090/mcp/tools
   
   # Should return 200 OK
   curl -H "X-API-Key: generated-key" http://localhost:8090/mcp/tools
   ```

## Troubleshooting

### 401 Unauthorized Errors

- Verify `MCP_API_KEY` is set correctly
- Check that the client is sending the authentication header
- Ensure the key matches exactly (no extra whitespace)

### Authentication Not Required

- Check that `MCP_API_KEY` environment variable is set
- Verify the server was restarted after setting the variable
- Check `/health` endpoint to confirm `auth_required: true`

## Security Disclosure

This authentication mechanism was implemented to address a security finding where the MCP gateway accepted unauthenticated requests and forwarded them to internal services. The fix ensures:

1. All non-health endpoints require authentication when `MCP_API_KEY` is set
2. Authentication credentials are forwarded to downstream services
3. The server can still operate without authentication for development/testing
4. Multiple authentication header formats are supported for compatibility
