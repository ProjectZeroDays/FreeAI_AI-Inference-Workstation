# Todo API Reference

REST API for the Todo module, served on the Dashboard port (`:8030`).

## Base URL

```
http://localhost:8030
```

## Authentication

All Todo endpoints require a JWT Bearer token obtained via `/auth/login`.

```
Authorization: Bearer <token>
```

See [API-GUIDE.md](API-GUIDE.md) for the full auth reference.

---

## Auth Endpoints

### POST /auth/login

Authenticate and receive a JWT access token.

**Request:**
```json
{
  "username": "admin",
  "password": "your-password"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

**Errors:**
| Status | Body |
|---|---|
| 400 | `{"error": "username and password required"}` |
| 401 | `{"error": "invalid credentials"}` |
| 429 | `{"error": "too many login attempts, try again later"}` |
| 503 | `{"error": "JWT auth not configured"}` |

### POST /auth/register

> **Note:** Public registration is not exposed. New users are created by admins via `POST /auth/users` (admin required).

### POST /auth/refresh

Refresh an expired access token using a valid refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### GET /auth/me

Get the current authenticated user's profile.

**Response (200):**
```json
{
  "authenticated": true,
  "username": "admin",
  "role": "admin"
}
```

**Response (unauthenticated):**
```json
{"authenticated": false}
```

---

## Todo Endpoints

### GET /api/todos

List all todos for the authenticated user with pagination and filters.

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Items per page (max 100) |
| `completed` | string | — | Filter by completion: `true` / `false` |
| `priority` | int | — | Filter by priority level (0–5) |
| `search` | string | `""` | Full-text search on title and description |

**Example:**
```http
GET /api/todos?page=1&per_page=10&completed=false&priority=3&search=urgent
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "todos": [
      {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "title": "Fix login bug",
        "description": "Users unable to log in after password reset",
        "completed": false,
        "priority": 3,
        "created_at": "2026-01-15T10:30:00Z",
        "updated_at": "2026-01-15T10:30:00Z",
        "user_id": "user-uuid-here"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 42,
      "pages": 5
    }
  }
}
```

---

### GET /api/todos/<id>

Get a single todo by ID.

**Path Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `id` | int | Todo UUID |

**Example:**
```http
GET /api/todos/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Fix login bug",
    "description": "Users unable to log in after password reset",
    "completed": false,
    "priority": 3,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:30:00Z",
    "user_id": "user-uuid-here"
  }
}
```

**Errors:**
| Status | Body |
|---|---|
| 404 | `{"status": "error", "message": "todo not found"}` |

---

### POST /api/todos

Create a new todo.

**Request Body:**
```json
{
  "title": "Implement rate limiting",
  "description": "Add rate limiting to the router endpoint",
  "priority": 2
}
```

**Fields:**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `title` | string | yes | — | Todo title (1–200 chars, trimmed) |
| `description` | string | no | `""` | Optional description |
| `priority` | int | no | 0 | Priority level (0–5, higher = more urgent) |

**Example:**
```bash
curl -X POST http://localhost:8030/api/todos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Deploy to staging","priority":4}'
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "title": "Deploy to staging",
    "description": null,
    "completed": false,
    "priority": 4,
    "created_at": "2026-01-15T12:00:00Z",
    "updated_at": "2026-01-15T12:00:00Z",
    "user_id": "user-uuid-here"
  }
}
```

**Errors:**
| Status | Body |
|---|---|
| 400 | `{"status": "error", "message": "title is required"}` |
| 400 | `{"status": "error", "message": "invalid priority value"}` |
| 500 | `{"status": "error", "message": "<error details>"}` |

---

### PUT /api/todos/<id>

Update an existing todo. Only provided fields are patched; omitted fields are unchanged.

**Path Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `id` | int | Todo UUID |

**Request Body (all fields optional):**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "priority": 5
}
```

**Example:**
```bash
curl -X PUT http://localhost:8030/api/todos/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true, "priority": 5}'
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Fix login bug",
    "description": "Users unable to log in after password reset",
    "completed": true,
    "priority": 5,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T14:22:00Z",
    "user_id": "user-uuid-here"
  }
}
```

**Errors:**
| Status | Body |
|---|---|
| 400 | `{"status": "error", "message": "title cannot be empty"}` |
| 400 | `{"status": "error", "message": "invalid priority value"}` |
| 404 | `{"status": "error", "message": "todo not found"}` |
| 500 | `{"status": "error", "message": "<error details>"}` |

---

### DELETE /api/todos/<id>

Delete a todo permanently.

**Path Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `id` | int | Todo UUID |

**Example:**
```bash
curl -X DELETE http://localhost:8030/api/todos/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

**Errors:**
| Status | Body |
|---|---|
| 404 | `{"status": "error", "message": "todo not found"}` |
| 500 | `{"status": "error", "message": "<error details>"}` |

---

### PATCH /api/todos/<id>/toggle

Toggle the `completed` status of a todo between `true` and `false`.

**Path Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `id` | int | Todo UUID |

**Example:**
```bash
curl -X PATCH http://localhost:8030/api/todos/a1b2c3d4-e5f6-7890-abcd-ef1234567890/toggle \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Fix login bug",
    "description": "Users unable to log in after password reset",
    "completed": true,
    "priority": 3,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T14:30:00Z",
    "user_id": "user-uuid-here"
  }
}
```

**Errors:**
| Status | Body |
|---|---|
| 404 | `{"status": "error", "message": "todo not found"}` |
| 500 | `{"status": "error", "message": "<error details>"}` |

---

## Error Response Format

All error responses follow this structure:

```json
{
  "status": "error",
  "message": "human-readable error description"
}
```

Auth-specific errors use the `"error"` key instead of `"status"`:

```json
{
  "error": "unauthorized"
}
```

---

## Todo Model Schema

| Field | Type | Description |
|---|---|---|
| `id` | string (UUID) | Unique identifier |
| `title` | string (max 200) | Todo title |
| `description` | string (nullable) | Optional description |
| `completed` | boolean | Completion status |
| `priority` | int (0–5) | Urgency level; higher is more urgent |
| `created_at` | string (ISO 8601) | Creation timestamp |
| `updated_at` | string (ISO 8601) | Last update timestamp |
| `user_id` | string (UUID) | Owner user ID |

---

## Source

- API: `todos/api.py`
- Models: `todos/models.py`
- Auth: `todos/auth.py`
- Route: `dashboard/backend.py`
