---
name: api-design
description: REST and GraphQL API design patterns, OpenAPI specs, versioning, pagination, rate limiting, authentication, and error handling. Use when the user asks about designing APIs, writing OpenAPI specs, implementing pagination, rate limiting, authentication flows, or API architecture decisions.
---

# API Design

## REST Conventions

### Resource Naming
```
GET    /users              → list users
POST   /users              → create user
GET    /users/:id          → get user
PUT    /users/:id          → replace user
PATCH  /users/:id          → update user
DELETE /users/:id          → delete user
GET    /users/:id/posts    → list user's posts
```

### HTTP Status Codes
| Code | Use |
|------|-----|
| 200 | Success |
| 201 | Created |
| 204 | No Content (delete success) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (no/invalid auth) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate, version mismatch) |
| 422 | Unprocessable Entity (business logic error) |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### Response Envelope
```json
{
  "data": { "id": 1, "name": "Alice" },
  "meta": { "requestId": "abc-123" }
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      { "field": "email", "message": "must be a valid email" }
    ]
  }
}
```

## Pagination

### Cursor-Based (Recommended)
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTAwfQ==",
    "has_more": true
  }
}
```
Request: `GET /users?cursor=eyJpZCI6MTAwfQ==&limit=20`

### Offset-Based
```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "page": 2,
    "per_page": 20
  }
}
```
Request: `GET /users?page=2&per_page=20`

## Filtering and Sorting

```
GET /users?status=active&role=admin&sort=-created_at,name
GET /users?filter[status]=active&filter[role]=admin
GET /posts?search=hello&fields=id,title,createdAt
```

## Versioning

### URL Path (Recommended)
```
/v1/users
/v2/users
```

### Header
```
Accept: application/vnd.myapi.v2+json
```

## Rate Limiting

Headers to include:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
Retry-After: 30
```

## Authentication Patterns

### API Key
```
Authorization: Bearer sk_live_abc123
```

### OAuth2 Flow
```
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=abc123
&redirect_uri=https://app.example.com/callback
&client_id=xxx
&client_secret=yyy
```

### JWT Structure
```json
{
  "header": { "alg": "RS256", "typ": "JWT" },
  "payload": {
    "sub": "user_123",
    "iss": "https://api.example.com",
    "exp": 1700000000,
    "scope": "read write"
  }
}
```

## OpenAPI Spec

```yaml
openapi: 3.1.0
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        "200":
          description: User list
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/User"
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
          format: email
```

## Idempotency

For safe retries on POST/PUT:
- Client sends `Idempotency-Key: unique-string` header
- Server stores result for 24h
- Duplicate key returns cached response

## HATEOAS Links

```json
{
  "data": { "id": 1, "name": "Alice" },
  "links": {
    "self": "/users/1",
    "posts": "/users/1/posts",
    "avatar": "/users/1/avatar"
  }
}
```
