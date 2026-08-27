# Agent API Security Model

## Overview

The Agent API enforces mandatory authentication for all sensitive endpoints. This document describes the security model and configuration requirements.

## Authentication Configuration

### Required Environment Variables

Set **one** of the following environment variables to enable the service:

- `AGENT_API_KEY` - Primary API key for agent service authentication
- `ROUTER_API_KEY` - Fallback to router's API key if AGENT_API_KEY is not set

**Important**: If neither variable is set, all protected endpoints will return HTTP 503 (Service Unavailable) with the message "authentication not configured".

### Example Configuration

#### Docker Compose
```yaml
services:
  agents:
    environment:
      - AGENT_API_KEY=your-secret-key-here
```

#### Kubernetes
```yaml
env:
  - name: AGENT_API_KEY
    valueFrom:
      secretKeyRef:
        name: agent-api-secrets
        key: api-key
```

#### Direct Execution
```bash
export AGENT_API_KEY="your-secret-key-here"
python agents/api.py
```

## Client Authentication

Clients must provide the API key in one of the following HTTP headers:

1. `X-API-Key: your-secret-key-here`
2. `X-Auth-Token: your-secret-key-here`
3. `Authorization: Bearer your-secret-key-here`

### Example Request
```bash
curl -H "X-API-Key: your-secret-key-here" \
     -H "Content-Type: application/json" \
     -d '{"spec": "Build a REST API"}' \
     http://localhost:8020/agent/project
```

## Endpoint Security Matrix

### Public Endpoints (No Authentication Required)

These endpoints provide read-only informational data:

- `GET /health` - Service health check
- `GET /metrics` - Service metrics
- `GET /profiles` - Available agent profiles
- `GET /env/status` - Environment status
- `GET /env/agents` - List available agents
- `GET /env/plugins` - List available plugins
- `GET /env/skills` - List available skills

### Protected Endpoints (Authentication Required)

All endpoints that execute agents, access memory, or modify state require authentication:

#### Agent Execution
- `POST /agent/project` - Project generation agent
- `POST /agent/refactor` - Code refactoring agent
- `POST /agent/debug` - Debugging agent
- `POST /agent/analyze` - Analysis agent
- `POST /agent/orchestrate` - Orchestration agent
- `POST /agent/chat` - Chat agent with session memory
- `POST /agent/red` - Red team operations
- `POST /agent/blue` - Blue team operations
- `POST /agent/purple` - Purple team operations

#### Memory Access
- `GET /memory/{session_id}` - Retrieve session memory
- `DELETE /memory/{session_id}` - Clear session memory
- `GET /env/memory/{session_id}` - Retrieve environment memory
- `POST /env/memory/search` - Search global knowledge base

#### Environment Operations
- `POST /env/chat` - Unified chat with agent routing
- `POST /env/plugins/{name}/install` - Install plugins

## Security Considerations

### Session Isolation

While authentication is now enforced, session identifiers are still caller-controlled. In multi-tenant deployments, consider implementing additional authorization checks to ensure users can only access their own sessions.

### API Key Management

- **Never commit API keys to version control**
- Use environment variables or secret management systems
- Rotate keys periodically
- Use different keys for different environments (dev/staging/prod)
- Monitor for unauthorized access attempts in logs

### Network Security

- Deploy behind a reverse proxy with TLS termination
- Use network policies to restrict access to the agent service
- Consider IP allowlisting for additional security
- Enable rate limiting at the proxy level

### Audit Logging

Consider implementing audit logging for:
- Authentication failures
- Session access patterns
- Agent execution requests
- Memory access and modifications

## Migration Guide

### For Existing Deployments

If you have an existing deployment without authentication:

1. **Generate a secure API key**:
   ```bash
   openssl rand -hex 32
   ```

2. **Update your deployment configuration** to include the API key

3. **Update all clients** to include the API key in requests

4. **Restart the agent service**

5. **Verify authentication** is working:
   ```bash
   # Should fail with 503 or 401
   curl http://localhost:8020/agent/project
   
   # Should succeed
   curl -H "X-API-Key: your-key" http://localhost:8020/agent/project
   ```

### For New Deployments

1. Set `AGENT_API_KEY` before starting the service
2. Configure clients with the same key
3. Test authentication before exposing to network

## Troubleshooting

### HTTP 503: "authentication not configured"

**Cause**: Neither `AGENT_API_KEY` nor `ROUTER_API_KEY` is set.

**Solution**: Set one of these environment variables and restart the service.

### HTTP 401: "unauthorized"

**Cause**: The provided API key does not match the configured key.

**Solution**: Verify the client is sending the correct key in one of the supported headers.

### Public endpoints still accessible

**Expected behavior**: Health, metrics, and informational endpoints remain public for monitoring and discovery purposes.

## Security Disclosure

If you discover a security vulnerability, please report it to the security team following responsible disclosure practices.
