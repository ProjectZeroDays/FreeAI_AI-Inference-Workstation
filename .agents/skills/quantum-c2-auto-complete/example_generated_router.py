"""
Example of a generated router with authentication (v2.0)

This file demonstrates what the generate_services.py script will produce
after the security fix has been applied.

Tool: Bettercap (Network exploitation framework)
"""

import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.services.bettercap_service import get_bettercap_service

# Authentication dependency
QUANTUM_C2_API_KEY = os.environ.get("QUANTUM_C2_API_KEY", "")


def verify_auth(request: Request):
    """Verify API key authentication for Quantum C2 endpoints."""
    if not QUANTUM_C2_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="QUANTUM_C2_API_KEY environment variable not configured",
        )

    provided = (
        request.headers.get("X-API-Key")
        or request.headers.get("X-Auth-Token")
        or request.headers.get("Authorization", "").replace("Bearer ", "")
    )

    if provided != QUANTUM_C2_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return True


router = APIRouter(
    prefix="/api/exploit/bettercap",
    tags=["Bettercap"],
    dependencies=[Depends(verify_auth)],
)

_service = get_bettercap_service()


@router.post("/run")
async def run(req: dict[str, Any] = {}):
    """Run bettercap session."""
    return await _service.run(req)


@router.get("/status")
async def get_status():
    """Get bettercap status."""
    return await _service.get_status()


@router.post("/stop")
async def stop(req: dict[str, Any] = {}):
    """Stop bettercap session."""
    return await _service.stop(req)


@router.get("/events")
async def get_events():
    """Get bettercap events."""
    return await _service.get_events()


"""
SECURITY NOTES:

1. Authentication is enforced at the router level via dependencies=[Depends(verify_auth)]
   - This means ALL routes under this router require authentication
   - No individual route can bypass authentication

2. The verify_auth function checks:
   - If QUANTUM_C2_API_KEY is configured (fail-secure if not)
   - If request includes authentication header
   - If provided key matches configured key

3. Supported authentication headers:
   - X-API-Key: your-api-key
   - X-Auth-Token: your-api-key
   - Authorization: Bearer your-api-key

4. Error responses:
   - HTTP 500: QUANTUM_C2_API_KEY not configured
   - HTTP 401: Missing or invalid authentication

5. Usage example:
   curl -H "X-API-Key: your-key" \\
     http://localhost:8000/api/exploit/bettercap/run \\
     -X POST -d '{"target": "192.168.1.0/24"}'
"""
