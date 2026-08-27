---
name: database-migration
description: Manage database migrations for Quantum C2. Use when migrating from SQLite to PostgreSQL, running migrations, or managing database schema.
trigger_keywords: migrate, database migration, db migrate, postgres, postgresql, schema, alembic
---

# Database Migration Skill

## Overview
This skill manages database migrations for Quantum C2, supporting both SQLite and PostgreSQL.

## Commands

### Check Current Database
```bash
python -c "from app.database.connection_unified import is_sqlite; print(f'Using SQLite: {is_sqlite()}')"
```

### Migrate to PostgreSQL
```bash
# 1. Generate migration script
python -m app.database.postgres_migration

# 2. Run migration
python scripts/db_migrate.py --to-postgres

# 3. Validate
python -c "from app.database.postgres_primary import get_postgres_manager; m = get_postgres_manager(); print(m.get_statistics())"
```

### Run Alembic Migrations
```bash
cd backend
alembic upgrade head
```

### Generate Migration
```bash
alembic revision --autogenerate -m "description"
```

## Database Options

| Database | URL Format | Use Case |
|----------|------------|----------|
| SQLite | `sqlite+aiosqlite:///quantum.db` | Development |
| PostgreSQL | `postgresql+asyncpg://user:pass@host/db` | Production |

## Migration Steps
1. Backup SQLite database
2. Generate PostgreSQL schema
3. Migrate data in batches
4. Validate row counts
5. Update DATABASE_URL in .env
6. Run tests

## Commands
- `/migrate-db` - Start database migration
- `/check-db` - Check current database
- `/backup-db` - Backup database
- `/validate-migration` - Validate migration
