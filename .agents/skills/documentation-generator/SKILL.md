---
name: documentation-generator
description: Auto-generate documentation for code, APIs, databases, and projects. Use when the user asks about generating README files, API docs, code documentation, JSDoc/docstrings, or project documentation.
---

# Documentation Generator

## README Template

```markdown
# Project Name

One-line description of what this project does.

## Features

- Feature 1
- Feature 2
- Feature 3

## Quick Start

### Prerequisites

- Node.js 20+
- PostgreSQL 16

### Installation

```bash
git clone https://github.com/user/repo
cd repo
npm install
```

### Setup

```bash
cp .env.example .env
# Edit .env with your configuration
npm run db:migrate
npm run dev
```

## Usage

```bash
# Development
npm run dev

# Build
npm run build

# Test
npm run test
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/users | List all users |
| POST | /api/users | Create user |
| GET | /api/users/:id | Get user by ID |

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Server port | 3000 |
| DATABASE_URL | Database connection | - |
| LOG_LEVEL | Logging level | info |

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## License

MIT
```

## JSDoc (TypeScript/JavaScript)

```typescript
/**
 * Calculates the total price including tax.
 * 
 * @param items - Array of items with price property
 * @param taxRate - Tax rate as decimal (e.g., 0.1 for 10%)
 * @returns Total price including tax, rounded to 2 decimal places
 * @throws {Error} If items array is empty
 * @example
 * ```ts
 * const total = calculateTotal([{ price: 10 }, { price: 20 }], 0.1);
 * // Returns 33
 * ```
 */
function calculateTotal(items: Array<{ price: number }>, taxRate: number): number {
  if (items.length === 0) throw new Error('Items cannot be empty');
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  return Math.round(subtotal * (1 + taxRate) * 100) / 100;
}

/**
 * User authentication result.
 * @property success - Whether authentication succeeded
 * @property token - JWT token (only if success is true)
 * @property error - Error message (only if success is false)
 */
interface AuthResult {
  success: boolean;
  token?: string;
  error?: string;
}
```

## Python Docstrings

```python
def calculate_total(items: list[dict], tax_rate: float) -> float:
    """Calculate the total price including tax.

    Args:
        items: List of dictionaries with 'price' key.
        tax_rate: Tax rate as decimal (e.g., 0.1 for 10%).

    Returns:
        Total price including tax, rounded to 2 decimal places.

    Raises:
        ValueError: If items list is empty.

    Examples:
        >>> calculate_total([{"price": 10}, {"price": 20}], 0.1)
        33.0
    """
    if not items:
        raise ValueError("Items cannot be empty")
    subtotal = sum(item["price"] for item in items)
    return round(subtotal * (1 + tax_rate), 2)
```

## API Documentation (OpenAPI)

```yaml
openapi: 3.1.0
info:
  title: My API
  version: 1.0.0
  description: |
    API for managing users and posts.
    
    ## Authentication
    All endpoints require Bearer token authentication.
    
    ## Rate Limiting
    - 100 requests per minute
    - 429 status code when exceeded

paths:
  /users:
    get:
      summary: List users
      tags: [Users]
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
      responses:
        "200":
          description: User list
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UserList"

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

## Changelog Format

```markdown
# Changelog

## [1.2.0] - 2024-01-15

### Added
- User profile customization
- Dark mode support
- Export to PDF feature

### Changed
- Improved dashboard performance
- Updated dependency versions

### Fixed
- Fixed login timeout issue
- Resolved memory leak in worker

### Removed
- Deprecated v1 API endpoints

## [1.1.0] - 2024-01-01

### Added
- Initial release features
```

## Architecture Decision Record

```markdown
# ADR-001: Use PostgreSQL as Primary Database

## Status: Accepted

## Context
We need a relational database that supports:
- Complex queries and joins
- JSON storage for flexible fields
- Full-text search
- ACID compliance

## Decision
Use PostgreSQL 16 as our primary database.

## Consequences

### Positive
- Mature ecosystem with excellent tooling
- Native JSONB support
- Strong community

### Negative
- Requires more setup than SQLite
- Larger memory footprint
```

## Documentation Best Practices

1. Write for your audience (developer vs user)
2. Include code examples
3. Keep documentation near the code
4. Use consistent formatting
5. Document decisions, not just code
6. Include setup instructions
7. Version your documentation
8. Review docs with code changes
