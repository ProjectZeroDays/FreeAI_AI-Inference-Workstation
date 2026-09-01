---
name: quantum-flask-router
description: Adds new Flask API routes and WebSocket handlers to the Quantum backend. Use when creating new API endpoints, adding WebSocket events, or extending the backend API.
---

# Quantum Flask Router

Adds new API routes to the Quantum backend following established conventions.

## Architecture

```
core/web_interface/
├── app.py              # Flask app factory
├── routes/
│   ├── __init__.py     # Route registration
│   ├── auth.py         # Authentication routes
│   ├── api.py          # Main API routes
│   └── ...
└── templates/
    ├── c2.html         # Style source of truth
    └── quantum_unified.html  # Unified dashboard
```

## Route Template

```python
"""
Quantum API Routes - [Feature Name]
"""
from flask import Blueprint, request, jsonify
from functools import wraps
import logging

logger = logging.getLogger(__name__)
[feature]_bp = Blueprint('[feature]', __name__)


def require_auth(f):
    """Authentication decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Auth check logic
        return f(*args, **kwargs)
    return decorated


@[feature]_bp.route('/api/[feature]', methods=['GET'])
@require_auth
def get_[feature]():
    """Get [feature] data."""
    try:
        data = {
            "status": "success",
            "data": {},
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error in get_[feature]: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@[feature]_bp.route('/api/[feature]', methods=['POST'])
@require_auth
def create_[feature]():
    """Create new [feature]."""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"status": "error", "message": "No payload"}), 400

        result = {
            "status": "success",
            "message": "[Feature] created"
        }
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error in create_[feature]: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
```

## Register Blueprint

In `app.py` or `routes/__init__.py`:
```python
from routes.[feature] import [feature]_bp
app.register_blueprint([feature]_bp)
```

## WebSocket Events

```python
# In Flask-SocketIO setup
@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")

@socketio.on('[feature]_request')
def handle_[feature]_request(data):
    """Handle [feature] WebSocket request."""
    try:
        result = process_[feature](data)
        emit('[feature]_response', result)
    except Exception as e:
        emit('[feature]_error', {"message": str(e)})
```

## API Conventions

- **Base URL**: `https://localhost:4433/api/`
- **Auth**: Session-based, via `require_auth` decorator
- **Response format**: `{"status": "success/error", "data": {...}, "timestamp": "..."}`
- **Error codes**: 400 (bad request), 401 (unauthorized), 404 (not found), 500 (server error)
- **Content-Type**: `application/json`
- **HTTPS only**: All routes served over TLS on port 4433

## Port Map

| Service | Port |
|---------|------|
| Flask HTTPS | 4433 |
| HTTP→HTTPS redirect | 8080 |
| Backend API (direct) | 5000 |
| WebSocket | 8765 |
