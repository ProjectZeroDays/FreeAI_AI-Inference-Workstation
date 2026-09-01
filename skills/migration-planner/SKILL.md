---
name: migration-planner
description: Database migration planning, schema evolution, data migration strategies, zero-downtime migrations, and version control for databases. Use when the user asks about planning database migrations, schema changes, data transformations, or zero-downtime deployment strategies.
---

# Migration Planner

## Migration Strategies

### Forward Migration
```sql
-- Version 001: Add column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Version 002: Populate from existing data
UPDATE users SET phone = 'N/A' WHERE phone IS NULL;

-- Version 003: Make NOT NULL
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
```

### Backward-Compatible Migration
```sql
-- Step 1: Add new column (nullable)
ALTER TABLE users ADD COLUMN email_normalized VARCHAR(255);

-- Step 2: Backfill
UPDATE users SET email_normalized = LOWER(email);

-- Step 3: Add index
CREATE INDEX idx_users_email_normalized ON users(email_normalized);

-- Step 4: Update application to use new column

-- Step 5: Drop old column (separate migration)
ALTER TABLE users DROP COLUMN email;
ALTER TABLE users RENAME COLUMN email_normalized TO email;
```

## Zero-Downtime Patterns

### Expand and Contract
```
Phase 1: EXPAND (add new, keep old)
├── Add new table/column
├── Write to both old and new
├── Read from old
└── Backfill new

Phase 2: MIGRATE (switch reads)
├── Read from new
├── Write to both
└── Validate consistency

Phase 3: CONTRACT (remove old)
├── Stop writing to old
├── Drop old table/column
└── Clean up
```

### Double-Write Pattern
```python
# Phase 1: Write to both
async def create_user(data):
    # Write to old table
    await db.execute("INSERT INTO users_old ...", data)
    # Write to new table
    await db.execute("INSERT INTO users_new ...", data)

# Phase 2: Read from new, write to both
async def get_user(user_id):
    return await db.fetch("SELECT * FROM users_new WHERE id = $1", user_id)

# Phase 3: Only new table
async def create_user(data):
    await db.execute("INSERT INTO users ...", data)
```

## Schema Evolution

### Add Column
```sql
-- Safe: nullable column with default
ALTER TABLE users ADD COLUMN bio TEXT DEFAULT '';
```

### Remove Column
```sql
-- Step 1: Stop using in code
-- Step 2: Add migration to drop
ALTER TABLE users DROP COLUMN legacy_field;
```

### Rename Column
```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(200);
UPDATE users SET full_name = first_name || ' ' || last_name;

-- Step 2: Update code to use new column

-- Step 3: Drop old columns
ALTER TABLE users DROP COLUMN first_name;
ALTER TABLE users DROP COLUMN last_name;
```

### Change Type
```sql
-- Step 1: Add new column
ALTER TABLE orders ADD COLUMN total_decimal DECIMAL(10,2);

-- Step 2: Copy data
UPDATE orders SET total_decimal = total::DECIMAL;

-- Step 3: Switch code to use new column

-- Step 4: Drop old column
ALTER TABLE orders DROP COLUMN total;
ALTER TABLE orders RENAME COLUMN total_decimal TO total;
```

## Data Migration

### Batch Processing
```python
async def migrate_users_batch(batch_size=1000):
    offset = 0
    while True:
        # Fetch batch
        users = await db.fetch(
            "SELECT * FROM users_old ORDER BY id LIMIT $1 OFFSET $2",
            batch_size, offset
        )
        if not users:
            break
        
        # Transform
        transformed = [transform_user(u) for u in users]
        
        # Insert batch
        await db.executemany(
            "INSERT INTO users_new (id, name, email) VALUES ($1, $2, $3)",
            [(u['id'], u['name'], u['email']) for u in transformed]
        )
        
        offset += batch_size
        print(f"Migrated {offset} users...")
```

### Validation
```python
async def validate_migration():
    old_count = await db.fetchval("SELECT COUNT(*) FROM users_old")
    new_count = await db.fetchval("SELECT COUNT(*) FROM users_new")
    
    if old_count != new_count:
        raise MigrationError(f"Count mismatch: {old_count} vs {new_count}")
    
    # Spot check random records
    samples = await db.fetch("SELECT id FROM users_old ORDER BY RANDOM() LIMIT 100")
    for sample in samples:
        old = await db.fetchrow("SELECT * FROM users_old WHERE id = $1", sample['id'])
        new = await db.fetchrow("SELECT * FROM users_new WHERE id = $1", sample['id'])
        if old != new:
            raise MigrationError(f"Data mismatch for id {sample['id']}")
    
    print("Migration validated successfully")
```

## Migration File Structure

```
migrations/
├── 001_create_users/
│   ├── up.sql
│   └── down.sql
├── 002_add_email_index/
│   ├── up.sql
│   └── down.sql
└── 003_normalize_users/
    ├── up.sql
    ├── down.sql
    └── backfill.py
```

```sql
-- 001_create_users/up.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 001_create_users/down.sql
DROP TABLE users;
```

## Rollback Strategy

```python
class MigrationRunner:
    def run(self, version: int):
        try:
            for migration in self.get_pending(version):
                self.run_up(migration)
                self.record_migration(migration)
        except Exception as e:
            self.rollback()
            raise

    def rollback(self):
        applied = self.get_applied_migrations()
        for migration in reversed(applied):
            self.run_down(migration)
            self.remove_migration_record(migration)
```

## Checklist

- [ ] Test migration on copy of production data
- [ ] Verify rollback works
- [ ] Check for blocking operations (large table locks)
- [ ] Plan for backfilling data
- [ ] Monitor performance during migration
- [ ] Have a rollback plan
- [ ] Schedule during low-traffic window
- [ ] Notify team of migration window
- [ ] Validate data integrity after completion
