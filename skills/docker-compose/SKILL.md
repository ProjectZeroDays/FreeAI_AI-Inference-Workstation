---
name: docker-compose
description: Docker Compose service orchestration for multi-container applications. Use when the user asks about setting up local dev environments, defining services, configuring volumes/networks, multi-stage builds, health checks, or containerized application architecture.
---

# Docker Compose

## Basic Structure

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app
      - /app/node_modules
    networks:
      - backend

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - backend

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - backend

volumes:
  pgdata:

networks:
  backend:
```

## Common Commands

```bash
# Start all services (detached)
docker compose up -d

# Build and start
docker compose up --build

# Stop and remove containers
docker compose down

# Stop and remove volumes too
docker compose down -v

# View logs
docker compose logs -f app

# Execute command in running container
docker compose exec app bash

# Scale a service
docker compose up -d --scale worker=3

# Restart single service
docker compose restart app

# View running services
docker compose ps
```

## Multi-Stage Builds

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

## Profiles

Run optional services only when needed:

```yaml
services:
  app:
    build: .
    profiles: ["default"]

  debug:
    image: busybox
    profiles: ["debug"]

  test:
    profiles: ["test"]
    build:
      target: test
```

```bash
docker compose --profile debug up -d
docker compose --profile test up --build
```

## Environment Management

```yaml
services:
  app:
    env_file:
      - .env
      - .env.local
    environment:
      - NODE_ENV=production
      - LOG_LEVEL=${LOG_LEVEL:-info}
```

```bash
# Override env file
docker compose --env-file .env.staging up -d
```

## Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          memory: 256M
```

## Volume Types

```yaml
services:
  app:
    volumes:
      # Named volume (persistent)
      - data:/app/data
      # Bind mount (host path)
      - ./src:/app/src
      # Read-only mount
      - ./config:/app/config:ro
      # Anonymous volume
      - /app/node_modules

volumes:
  data:
    driver: local
```

## Networking

```yaml
services:
  frontend:
    networks:
      - frontend
  backend:
    networks:
      - frontend
      - backend
  db:
    networks:
      - backend

networks:
  frontend:
  backend:
    driver: bridge
```

Services on the same network resolve each other by service name (e.g., `db`, `redis`).

## Health Checks

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Use `depends_on.condition: service_healthy` to wait for healthy dependencies.

## Development Overrides

Create `docker-compose.override.yml` for dev-specific config:

```yaml
# docker-compose.override.yml (loaded automatically)
services:
  app:
    volumes:
      - ./src:/app/src
    environment:
      - NODE_ENV=development
      - DEBUG=*
    command: npm run dev
```

Use a separate file for production:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
