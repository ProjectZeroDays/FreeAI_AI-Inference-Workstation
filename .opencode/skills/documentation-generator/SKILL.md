---
name: documentation-generator
description: >
  Generate comprehensive documentation for Quantum C2 and similar projects. Use when creating README files, API documentation, architecture guides, or project documentation. Triggers on: "generate documentation", "create README", "API docs", "architecture documentation", "project documentation", "generate docs", "document the project", "create documentation".
---

# Documentation Generator Skill

Generate comprehensive, production-ready documentation following industry best practices.

## Documentation Types

### 1. README.md
- Project overview and description
- Features list with badges
- Architecture diagram
- Quick start guide
- Deployment instructions
- Configuration reference
- Security notes
- Contributing guidelines
- License information

### 2. API_REFERENCE.md
- Base URL and authentication
- All endpoints grouped by module
- Request/response schemas
- Error codes and handling
- Rate limits
- WebSocket messages
- Code examples

### 3. CHANGELOG.md
- Version history
- Added/Changed/Fixed/Removed sections
- Migration guides
- Breaking changes

### 4. WIKI.md (Comprehensive)
- Table of contents
- Getting started
- Deployment guide
- All dashboard cards
- Complete API reference
- Database structure
- AI configuration
- Vault and encryption
- Logging and monitoring
- Attack vectors
- Troubleshooting
- Extending the framework

### 5. ARCHITECTURE.md
- System architecture
- Component diagrams
- Data flow
- Security architecture
- Deployment architecture
- Module relationships

### 6. SECURITY.md
- Security features
- Authentication flow
- Authorization model
- Data encryption
- Network security
- Audit logging
- Compliance

## Documentation Standards

### File Organization
```
docs/
├── API_REFERENCE.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── SECURITY.md
└── DEPLOYMENT.md
```

### Markdown Conventions
- Use ATX headings (#, ##, ###)
- Include table of contents for long docs
- Use code blocks with language tags
- Include screenshots where helpful
- Keep sections under 50 lines
- Use consistent terminology

### API Documentation Format
```markdown
### METHOD /endpoint
Brief description.

**Request Body:**
\`\`\`json
{
  "key": "value"
}
\`\`\`

**Response:**
\`\`\`json
{
  "status": "success",
  "data": {}
}
\`\`\`

**Errors:**
- 400: Bad request
- 401: Unauthorized
- 404: Not found
- 429: Rate limited
```

### Code Examples
- Include language tag
- Use realistic values
- Show error handling
- Comment complex logic
- Keep examples concise

## Quick Commands

```bash
# Generate README
python scripts/generate_docs.py --type readme

# Generate API docs
python scripts/generate_docs.py --type api

# Generate full docs
python scripts/generate_docs.py --type all

# Validate docs
python scripts/generate_docs.py --validate
```

## Templates

See `templates/` directory for:
- README template
- API reference template
- Architecture diagram template
- Changelog template

## Best Practices

1. **Write for your audience** - Developers vs operators need different detail levels
2. **Include working examples** - Users learn by doing
3. **Keep docs current** - Update with every release
4. **Use consistent formatting** - Same style throughout
5. **Document decisions** - Why > What
6. **Include setup instructions** - Reduce onboarding friction
7. **Version your docs** - Match code versions
8. **Review with code changes** - Docs update cycle

## Common Patterns

### Feature Documentation
```markdown
## Feature Name

Brief description of what the feature does.

### Usage
\`\`\`bash
# Example command
command --flag value
\`\`\`

### Configuration
| Setting | Default | Description |
|---------|---------|-------------|
| `setting` | `value` | Description |

### Examples
\`\`\`python
# Code example
result = function(arg)
\`\`\`
```

### API Endpoint Documentation
```markdown
### GET /api/resource

Retrieve a list of resources.

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `limit` | int | No | Max results (default: 20) |
| `offset` | int | No | Pagination offset |

**Response:**
\`\`\`json
{
  "resources": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
\`\`\`
```

### Configuration Documentation
```markdown
## Configuration

All settings are managed via environment variables in `.env`.

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | JWT signing key | - | Yes |
| `DATABASE_URL` | Database connection | sqlite:///... | Yes |
| `LOG_LEVEL` | Logging verbosity | INFO | No |

### Examples

\`\`\`bash
# Development
SECRET_KEY=dev-key DATABASE_URL=sqlite:///dev.db python app.py

# Production
SECRET_KEY=$(openssl rand -hex 32) DATABASE_URL=postgresql://... python app.py
\`\`\`
```
