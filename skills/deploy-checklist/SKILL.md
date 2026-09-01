---
name: deploy-checklist
description: Deployment validation: env vars, dependencies, migrations, rollback plan. Use when the user asks about deployment preparation, pre-deploy checks, release validation, migration safety, or rollback planning.
---

# Deploy Checklist

## Pre-Deploy Validation

### Environment Variables

```bash
# Verify all required env vars are set
REQUIRED_VARS=(
    "DATABASE_URL"
    "SECRET_KEY"
    "REDIS_URL"
    "API_KEY"
    "LOG_LEVEL"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "ERROR: Missing required env var: $var"
        exit 1
    fi
done

# Check for hardcoded secrets
if grep -r "password\s*=\s*['\"][^'\"]\{8,\}" src/ --include="*.py" --include="*.js"; then
    echo "ERROR: Potential hardcoded password found"
    exit 1
fi
```

### Dependency Check

```bash
# Python
pip install -r requirements.txt --dry-run
# or
pip check

# Node
npm ci --prefer-offline
npm audit --audit-level=high

# Go
go mod download
go mod verify

# Docker image layers
docker build --progress=plain -t app:deploy .
```

### Migration Safety

```bash
# Django
python manage.py migrate --check
python manage.py sqlmigrate app 0002 --backwards

# Rails
rake db:migrate:status
rake db:rollback STEP=1  # test rollback path

# PostgreSQL (general)
psql -c "SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 5;"
```

## Deployment Command

```bash
# Blue-green deployment
./deploy.sh --strategy blue-green --slot green

# Canary deployment
./deploy.sh --strategy canary --weight 10%

# Rolling deployment
./deploy.sh --strategy rolling --max-surge=1 --max-unavailable=0
```

## Rollback Plan

```bash
#!/bin/bash
# rollback.sh

VERSION=${1:-$(cat VERSION.prev)}
echo "Rolling back to version: $VERSION"

# 1. Stop new deployment
kubectl rollout undo deployment/app

# 2. Verify rollback
kubectl rollout status deployment/app --timeout=120s

# 3. Run health check
curl -f http://localhost:8080/health || exit 1

# 4. Verify database compatibility
python manage.py migrate --check

# 5. Notify team
echo "Rollback to $VERSION complete"
```

## Post-Deploy Verification

```bash
# Health check
curl -f http://localhost:8080/health
curl -f http://localhost:8080/ready

# Smoke tests
pytest tests/smoke/ -v

# Verify key endpoints
for path in /api/users /api/orders /api/health; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080$path)
    if [ "$response" != "200" ]; then
        echo "FAIL: $path returned $response"
        exit 1
    fi
done

# Check error rate
errors=$(curl -s http://localhost:9090/api/errors | jq '.count')
if [ "$errors" -gt 10 ]; then
    echo "WARN: Elevated error count: $errors"
fi

# Verify database connections
psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
```

## Deployment Checklist

### Before Deploy

- [ ] All tests passing (unit, integration, smoke)
- [ ] No pending database migrations that are backwards-incompatible
- [ ] Environment variables verified
- [ ] Secrets rotated if deployed to new environment
- [ ] Rollback plan documented and tested
- [ ] Team notified (Slack/DM)
- [ ] Monitoring dashboards ready

### During Deploy

- [ ] Deployment strategy selected (rolling/blue-green/canary)
- [ ] Progress monitored in real-time
- [ ] Error rate tracked
- [ ] Latency monitored
- [ ] Rollback trigger defined (error rate > 1% for 5min)

### After Deploy

- [ ] Health checks pass
- [ ] Key user flows verified (smoke tests)
- [ ] Error rate within baseline
- [ ] Database migrations applied successfully
- [ ] Performance benchmarks within threshold
- [ ] Rollback version recorded for future reference
- [ ] Deployment log archived

## Rollback Triggers

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error rate | > 1% for 5 min | Auto-rollback |
| p99 latency | > 2x baseline | Alert, prepare rollback |
| Database connection pool | 90% utilized | Slow down deployment |
| Disk usage | > 85% | Halt deployment |
| Out-of-memory errors | Any | Immediate rollback |

## Configuration Template

```yaml
# deploy-config.yaml
version: "2.0"
strategy: blue-green
health_check:
  path: /health
  interval: 10s
  timeout: 5s
  healthy_threshold: 3
  unhealthy_threshold: 2
rollback:
  auto: true
  triggers:
    - metric: error_rate
      threshold: 0.01
      duration: 5m
    - metric: p99_latency_ms
      threshold: 1000
      duration: 3m
notifications:
  on_deploy: "#deployments"
  on_rollback: "#deployments"
  on_success: "#deployments"
```
