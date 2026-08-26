---
name: env-config
description: Environment configuration, .env management, secrets handling, config validation, and twelve-factor app patterns. Use when the user asks about setting up environment variables, managing secrets, config validation, .env files, or environment-specific configuration.
---

# Environment Configuration

## Twelve-Factor App Config

1. Store config in environment variables, not code
2. Use `.env` files for local development only
3. Never commit `.env` to version control
4. Validate config at startup

## .env Structure

```bash
# .env (committed - defaults)
NODE_ENV=development
PORT=3000
LOG_LEVEL=info

# .env.local (not committed - overrides)
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=sk_test_abc123
```

```gitignore
# .gitignore
.env
.env.local
.env.*.local
```

## Config Validation (TypeScript)

```typescript
import { z } from 'zod';

const configSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
  REDIS_URL: z.string().url().optional(),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});

const config = configSchema.parse(process.env);

export default config;
```

## Config Validation (Python)

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    NODE_ENV: str = "development"
    PORT: int = 3000
    DATABASE_URL: str
    API_KEY: str
    REDIS_URL: str | None = None
    LOG_LEVEL: str = "info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## Environment-Specific Files

```
.env                # Defaults (committed)
.env.local          # Local overrides (gitignored)
.env.development    # Dev-specific (committed)
.env.production     # Prod-specific (committed)
.env.test           # Test-specific (committed)
```

Load order (later overrides earlier):
1. `.env`
2. `.env.local`
3. `.env.{NODE_ENV}`
4. `.env.{NODE_ENV}.local`

## Docker Environment

```yaml
# docker-compose.yml
services:
  app:
    env_file:
      - .env
      - .env.local
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
```

```bash
# Pass env vars directly
docker run -e API_KEY=abc -e DB_HOST=localhost myapp

# Use env file
docker run --env-file .env.production myapp
```

## CI/CD Secrets

### GitHub Actions
```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Shell
```bash
# Load .env for scripts
set -a; source .env; set +a

# Or use direnv
echo "dotenv" > .envrc
direnv allow
```

## Config as Code

```typescript
// config/index.ts
import config from './schema';
export default config;

// config/database.ts
import config from './index';

export const dbConfig = {
  url: config.DATABASE_URL,
  ssl: config.NODE_ENV === 'production',
  pool: { min: 2, max: 10 },
};

// config/redis.ts
import config from './index';

export const redisConfig = {
  url: config.REDIS_URL ?? 'redis://localhost:6379',
};
```

## Secret Rotation

```python
# Pattern: secrets with fallback and cache
import os
from functools import lru_cache

@lru_cache
def get_secret(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing secret: {name}")
    return value

# Usage
api_key = get_secret("API_KEY")
```

## Common Patterns

### Feature Flags
```bash
# .env
FEATURE_NEW_DASHBOARD=true
FEATURE_BETA_SEARCH=false
```

```typescript
const features = {
  newDashboard: process.env.FEATURE_NEW_DASHBOARD === 'true',
  betaSearch: process.env.FEATURE_BETA_SEARCH === 'true',
};
```

### Public vs Private Env
```bash
# Client-side (exposed to browser)
NEXT_PUBLIC_API_URL=https://api.example.com

# Server-side only
DATABASE_URL=postgresql://...
```

### Connection Strings
```bash
# Parse database URL
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require

# Parse Redis URL
REDIS_URL=redis://:password@host:6379/0
```
