# Full Application Stack Development

## Description
Comprehensive skill integrating every layer from frontend to backend. Unifies HTML, Python3, MySQL, and DevOps tools into a cohesive development workflow.

## When to Use
- Building full-stack applications from scratch
- Integrating frontend UI with backend APIs
- Setting up database schemas and migrations
- Configuring CI/CD pipelines for deployment

## Implementation Method
- Python Flask/Django for application layer
- SQLAlchemy for MySQL database integration
- React/TypeScript for frontend rendering
- GitHub Actions for CI/CD automation
- pip/npm for dependency management

## Usage
```bash
# Initialize full-stack project
python scripts/init_project.py --name "project_name" --db mysql

# Generate API endpoints
python scripts/generate_api.py --model "User" --fields "name,email,role"

# Build frontend components
npm run generate:component -- --name "Dashboard" --type "page"

# Deploy with CI/CD
gh workflow run deploy --ref main
```

## Benefits
- Unifies functionality across all layers
- Ensures cohesive and maintainable architecture
- Automates setup and deployment processes
- Provides type-safe development with TypeScript
