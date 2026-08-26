# User Space Management

## Description
Comprehensive environment awareness skill managing configuration files, package managers, and documentation. Ensures the system stays informed of its dependencies, versions, and state.

## When to Use
- Managing .ini/.yaml configuration files
- Tracking package dependencies (pip, npm)
- Updating documentation and wikis
- Environment variable management

## Implementation Method
- REST API scripts to fetch dependency lists from package.json
- GraphQL integration with MediaWiki/Notion for documentation
- Automated config validation and synchronization
- Version tracking and compatibility checking

## Usage
```bash
# List all dependencies
GET /api/env/dependencies

# Update configuration
POST /api/env/config
{
  "file": "config.yaml",
  "changes": {"key": "new_value"}
}

# Sync documentation
POST /api/docs/sync
{
  "target": "notion|mediawiki",
  "scope": "all|changed"
}
```

## Benefits
- Maintains environment consistency
- Prevents dependency conflicts
- Keeps documentation current automatically
- Provides real-time environment awareness
