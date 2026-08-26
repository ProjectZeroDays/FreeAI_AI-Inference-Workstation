---
name: deployment-guide
description: Deploy Quantum C2 to various environments (Docker, Kubernetes, cloud providers). Use when deploying, provisioning, or setting up the platform.
trigger_keywords: deploy, deploy to, install, setup, docker, kubernetes, k8s, provision
---

## Purpose
Provides deployment guidance and executes deployment workflows for Quantum C2 across Docker, Kubernetes, and cloud environments.

## When to Use
- First-time installation
- Production deployment
- Cloud provider deployment
- Environment migration
- When user asks to "deploy Quantum C2"

## Workflow
1. Pre-flight checks (Docker, secrets, dependencies)
2. Generate secrets if needed
3. Build and start services
4. Wait for health checks
5. Verify deployment
6. Generate deployment report

## Commands
```bash
# Generate secrets (required before deployment)
python scripts/generate_secrets.py

# Copy environment template
cp .env.example .env
# Edit .env with real values

# Docker Compose deployment
docker-compose up -d --build

# Check deployment status
docker-compose ps

# View logs
docker-compose logs -f backend

# Deploy with Kubernetes
kubectl apply -f k8s/
kubectl rollout status deployment/quantum-backend -n quantum-c2

# Windows PowerShell deployment
.\scripts\deploy.ps1 -Environment production

# Linux deployment
./scripts/deploy.sh

# Disaster recovery backup before deploy
python scripts/disaster_recovery.py backup
```

## Environments
| Environment | Command | Ports |
|-------------|---------|-------|
| Docker Compose | `docker-compose up -d` | 3000 (UI), 8000 (API) |
| Kubernetes | `kubectl apply -f k8s/` | Service-based |
| DigitalOcean | `./scripts/deploy-digitalocean.sh` | Configured |
| Hetzner | `./scripts/deploy-hetzner.sh` | Configured |
| OVH | `./scripts/deploy-ovh.sh` | Configured |
| Vultr | `./scripts/deploy-vultr.sh` | Configured |

## Pre-Deployment Checklist
- [ ] `.env` file configured with secrets
- [ ] `python scripts/generate_secrets.py` executed
- [ ] Database migrations complete
- [ ] Frontend build succeeds
- [ ] Health checks pass
- [ ] Backup created

## Post-Deployment Verification
```bash
# Health check
curl http://localhost:8000/api/health

# Frontend check
curl http://localhost:3000

# API docs
curl http://localhost:8000/docs

# Run production check
python scripts/production_check.py
```

## Notes
- Docker Compose is the default deployment method
- Kubernetes manifests in `k8s/` directory
- Cloud deployment scripts in `scripts/`
- Secrets MUST be rotated before production
- See `.learnings/ERRORS.md` for known deployment issues
