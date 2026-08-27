---
name: quantum-c2-deploy
description: >
  Deployment and configuration for Quantum C2. Use when the user needs to deploy, configure, troubleshoot, or maintain the Quantum C2 framework. Covers installation, Docker deployment, automated deployment scripts, configuration management, and health checks. Triggers on: "deploy Quantum", "install Quantum C2", "configure Quantum", "setup C2", "docker deploy", "production deployment", "health check", "troubleshoot", "update config", "backup database".
---

# Quantum C2 Deployment & Configuration Skill

Deploy and maintain the Quantum C2 framework.

## Deployment Options

### Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Restart
docker-compose restart
```

### Manual Installation
```bash
# Backend
cd backend
pip install -r requirements.txt
python -m app.main

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Automated Deployment

#### Hetzner (Recommended — €4.49/mo)
```bash
HETZNER_TOKEN=your-token ./scripts/deploy-all.sh hetzner cx22 nbg1 c2.yourdomain.com
```

#### Vultr ($12/mo)
```bash
VULTR_TOKEN=your-token ./scripts/deploy-all.sh vultr vc2-2c-2gb ams c2.yourdomain.com
```

#### DigitalOcean ($12/mo)
```bash
DIGITALOCEAN_TOKEN=your-token ./scripts/deploy-all.sh do 2gb nyc3 c2.yourdomain.com
```

#### OVH (€3.50/mo)
```bash
# Setup OVH API credentials first
./scripts/setup-ovh-api.sh

# Then deploy
OVH_APPLICATION_KEY=x OVH_APPLICATION_SECRET=x OVH_CONSUMER_KEY=x \
  ./scripts/deploy-all.sh ovh vps-ssd-2 GRA c2.yourdomain.com
```

#### Existing Server
```bash
./scripts/deploy-all.sh manual 198.51.100.42 c2.yourdomain.com
```

## Configuration

### Environment Variables
```bash
# Edit configuration
nano configs/.env
```

### Key Settings
| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | `change-me...` | JWT signing key (32+ chars) |
| `APP_DEFAULT_PASS` | `cyber-warware-7` | Default admin password |
| `DATABASE_URL` | `sqlite+aiosqlite:///./quantum_c2.db` | Database connection |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | Allowed frontend origins |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### AI Provider Keys
```bash
# Add to configs/.env
OPENAI_API_KEY=sk-...
VENICE_API_KEY=ven-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
DEEPSEEK_API_KEY=sk-...
LM_STUDIO_BASE_URL=http://localhost:1234/v1
```

## Database Setup

### PostgreSQL (Production)
```bash
./scripts/setup-database.sh postgresql
# Or with custom password:
./scripts/setup-database.sh postgresql "MyStr0ngP@ss!"
```

### SQLite (Development)
```bash
./scripts/setup-database.sh sqlite
```

### Run Migrations
```bash
# Apply all pending migrations
python -m app.database.migrations.run
```

## Health Checks

### Basic Health
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/health
```

### Service Status
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/status
```

### Docker Health
```bash
docker-compose ps
docker-compose logs --tail=50 backend
```

### Component Checks
```bash
# Backend API
curl http://localhost:8000/api/dashboard/

# Frontend
curl http://localhost:3000

# Database
docker exec -it quantum-c2-db-1 psql -U quantum -d quantum_c2 -c "SELECT 1"

# Redis
docker exec -it quantum-c2-redis-1 redis-cli ping
```

## Backup & Restore

### Database Backup
```bash
# PostgreSQL
./scripts/backup.sh postgres

# SQLite
./scripts/backup.sh sqlite
```

### Restore
```bash
./scripts/backup.sh restore /path/to/backup.sql
```

## Update & Maintenance

### Pull Latest Code
```bash
git pull origin main
```

### Update Dependencies
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### Rebuild
```bash
docker-compose down
docker-compose up -d --build
```

## Troubleshooting

### Backend Won't Start
```bash
# Check dependencies
pip install -r backend/requirements.txt

# Check database
ls backend/quantum_c2.db

# Check ports
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

### Frontend Won't Connect
```bash
# Verify backend
curl http://localhost:8000/health

# Check CORS
# Ensure FRONTEND_URL in .env matches dev server
```

### Container Health Issues
```bash
# View logs
docker-compose logs backend
docker-compose logs frontend

# Restart
docker-compose restart backend
```

### Database Issues
```bash
# Check connection
docker exec -it <postgres_container> psql -U quantum -d quantum_c2

# Run migrations
python -m app.database.migrations.run
```

## Port Reference

| Service | Port | Protocol |
|---------|------|----------|
| Backend API | 8000 | HTTP |
| Frontend | 3000 | HTTP |
| PostgreSQL | 5432 | TCP |
| Redis | 6379 | TCP |
| NGINX | 80/443 | HTTP/HTTPS |
| WebSocket | 8000 | WS/WSS |

## Production Checklist

- [ ] Change default admin password
- [ ] Set strong SECRET_KEY
- [ ] Configure CORS for production domain
- [ ] Enable HTTPS with Let's Encrypt
- [ ] Set up firewall (UFW/iptables)
- [ ] Configure fail2ban
- [ ] Set up automated backups
- [ ] Enable health monitoring
- [ ] Configure log rotation
- [ ] Set up SSL certificates
