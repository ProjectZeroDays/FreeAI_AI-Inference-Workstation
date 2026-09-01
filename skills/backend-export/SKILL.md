---
name: backend-export
description: Comprehensive backend code generation and export for all major languages and databases. Generates production-ready CRUD APIs, authentication systems, database schemas, migrations, and complete project structures. Supports Python (FastAPI/Django/Flask), Java (Spring Boot), Go (Gin/Fiber), Node.js/TypeScript (Express/NestJS), C#/.NET (ASP.NET Core), Ruby (Rails), PHP (Laravel), Rust (Actix/Axum) with MySQL, PostgreSQL, MongoDB, Redis, and SQLite. Use when building backend APIs, generating database schemas, creating CRUD operations, setting up authentication, designing REST/GraphQL endpoints, or scaffolding complete backend projects.
---

# Backend Export

Generate production-ready backend code for any major language and database combination.

## Workflow

1. **Identify requirements** - Language, framework, database, features
2. **Select reference** - Load language and database reference files
3. **Generate code** - API routes, models, services, configs
4. **Verify patterns** - Check against reference examples

## Language Selection

| Use Case | Language | Framework |
|----------|----------|-----------|
| Rapid prototyping | Python | FastAPI |
| Enterprise/Corporate | Java | Spring Boot |
| High performance | Go | Gin or Fiber |
| Full-stack/TypeScript | Node.js | NestJS |
| Microsoft ecosystem | C# | ASP.NET Core |
| Convention-over-configuration | Ruby | Rails |
| PHP ecosystem | PHP | Laravel |
| Maximum performance | Rust | Actix Web |

## Database Selection

| Use Case | Database | Best For |
|----------|----------|----------|
| Relational data | MySQL | General purpose, web apps |
| Advanced SQL | PostgreSQL | Complex queries, JSON, full-text |
| Document store | MongoDB | Flexible schemas, nested data |
| Caching/Sessions | Redis | Speed, pub/sub, sessions |
| Embedded/Embedded | SQLite | Mobile, desktop, small apps |

## Code Generation Workflow

### 1. Generate Project Structure

For each language, create:
```
project/
├── src/
│   ├── controllers/    # HTTP handlers
│   ├── models/         # Data models
│   ├── services/       # Business logic
│   ├── repositories/   # Database access
│   └── middleware/      # Auth, logging, etc.
├── config/
│   └── database.js     # DB connection
├── migrations/         # Schema changes
├── tests/
└── requirements.txt    # Dependencies
```

### 2. Generate CRUD Operations

Read the appropriate language reference, then generate:

**Model/Entity** with:
- ID field (auto-increment or UUID)
- Timestamps (created_at, updated_at)
- Validation constraints
- Relationships

**Repository/DAO** with:
- `findAll(limit, offset)` - List with pagination
- `findById(id)` - Get by ID
- `create(data)` - Insert
- `update(id, data)` - Update
- `delete(id)` - Soft or hard delete

**Controller/Handler** with:
- `GET /resource` - List
- `GET /resource/:id` - Get one
- `POST /resource` - Create
- `PUT /resource/:id` - Update
- `DELETE /resource/:id` - Delete

**Service** with:
- Business logic validation
- Error handling
- Transaction support

### 3. Generate Authentication

Read `references/auth.md` for JWT patterns, then add:
- Login/register endpoints
- Password hashing (bcrypt/argon2)
- JWT token generation
- Auth middleware
- Role-based access control

### 4. Generate Database Schema

Read the appropriate database reference, then create:
- Table/collection definitions
- Indexes for common queries
- Foreign key constraints
- Migration files

## Quick Reference Files

### Languages
- `references/python.md` - FastAPI, Django, Flask, SQLAlchemy
- `references/java.md` - Spring Boot, JPA, Service layer
- `references/go.md` - Gin, Fiber, GORM
- `references/nodejs.md` - Express, NestJS, Prisma
- `references/csharp.md` - ASP.NET Core, EF Core
- `references/ruby.md` - Rails, ActiveRecord
- `references/php.md` - Laravel, Eloquent
- `references/rust.md` - Actix Web, Axum, SQLx

### Databases
- `references/mysql.md` - Schema, queries, indexing
- `references/postgresql.md` - Advanced SQL, CTEs, JSON
- `references/mongodb.md` - Aggregation, indexing, transactions
- `references/redis.md` - Caching, pub/sub, locking
- `references/sqlite.md` - WAL mode, pragmas

### Patterns
- `references/auth.md` - JWT, OAuth2, sessions, RBAC
- `references/migrations.md` - Zero-downtime, rollback

## Example User Requests

| Request | Action |
|---------|--------|
| "Build me a REST API for users in Python" | Generate FastAPI + SQLAlchemy + PostgreSQL |
| "Create a Spring Boot CRUD for products" | Generate Spring Boot + JPA + MySQL |
| "Generate Go backend with Gin" | Generate Gin + GORM + MySQL |
| "Build Node.js API with authentication" | Generate NestJS + Prisma + JWT |
| "Create Laravel API with roles" | Generate Laravel + Eloquent + RBAC |

## Output Format

For each request, output:
1. **File tree** - Project structure
2. **Core files** - Models, controllers, services
3. **Config files** - Database, dependencies
4. **Instructions** - How to run and test

Generate complete, runnable code. No placeholders or TODOs in output.
