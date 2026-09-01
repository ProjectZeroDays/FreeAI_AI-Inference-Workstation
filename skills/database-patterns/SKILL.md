---
name: database-patterns
description: Database design patterns, SQL optimization, migrations, indexing strategies, connection pooling, and ORM best practices. Use when the user asks about database schema design, writing efficient SQL, database migrations, indexing, or ORM configuration.
---

# Database Patterns

## Schema Design

### Normalization (3NF)
```sql
-- 1NF: No repeating groups
-- 2NF: No partial dependencies
-- 3NF: No transitional dependencies

-- Bad (denormalized)
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    product_name VARCHAR(100),
    product_price DECIMAL
);

-- Good (normalized)
CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE
);

CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    product_id INT REFERENCES products(id),
    quantity INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Indexing

```sql
-- B-tree index (default, good for equality and range)
CREATE INDEX idx_users_email ON users(email);

-- Composite index (order matters)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, created_at DESC);

-- Partial index (index only relevant rows)
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- Covering index (includes all needed columns)
CREATE INDEX idx_orders_covering ON orders(customer_id, created_at)
    INCLUDE (total, status);

-- GIN index (for arrays, JSONB, full-text search)
CREATE INDEX idx_products_tags ON products USING GIN(tags);

-- Check index usage
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

## Common SQL Patterns

### Pagination
```sql
-- Offset-based (slow for large offsets)
SELECT * FROM posts
ORDER BY id
LIMIT 20 OFFSET 1000;

-- Cursor-based (fast, consistent)
SELECT * FROM posts
WHERE id > 1000
ORDER BY id
LIMIT 20;
```

### Aggregation
```sql
-- Running total
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) AS running_total
FROM daily_sales;

-- Year-over-year comparison
SELECT
    EXTRACT(YEAR FROM created_at) AS year,
    COUNT(*) AS orders,
    LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM created_at)) AS prev_year
FROM orders
GROUP BY 1;

-- Top N per group
SELECT * FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) AS rank
    FROM products
) ranked
WHERE rank <= 3;
```

### Window Functions
```sql
-- Ranking
SELECT
    name,
    score,
    RANK() OVER (ORDER BY score DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS row_num
FROM students;

-- Moving average
SELECT
    date,
    revenue,
    AVG(revenue) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM daily_revenue;
```

## Migrations

```sql
-- Version-controlled migrations
-- 001_create_users.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 002_add_user_avatar.sql
ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);

-- 003_create_posts.sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Connection Pooling

```python
# Python (psycopg2)
from psycopg2 import pool

connection_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host="localhost",
    database="mydb",
    user="user",
    password="pass"
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)
```

```javascript
// Node.js (pg)
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  database: 'mydb',
  user: 'user',
  password: 'pass',
  max: 20,
  idleTimeoutMillis: 30000,
});

const client = await pool.connect();
try {
  await client.query('SELECT * FROM users');
} finally {
  client.release();
}
```

## ORM Patterns (Prisma)

```prisma
// schema.prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([email])
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  Int

  @@index([authorId])
  @@index([published, createdAt])
}
```

```typescript
// Efficient queries
const userWithPosts = await prisma.user.findUnique({
  where: { id: 1 },
  include: {
    posts: {
      where: { published: true },
      orderBy: { createdAt: 'desc' },
      take: 10,
    },
  },
});

// Batch operations
await prisma.post.updateMany({
  where: { authorId: 1, published: false },
  data: { published: true },
});
```

## Performance Tips

1. Use EXPLAIN ANALYZE to understand query plans
2. Add indexes on WHERE, JOIN, and ORDER BY columns
3. Avoid SELECT * — fetch only needed columns
4. Use connection pooling
5. Batch inserts instead of individual INSERTs
6. Use prepared statements for repeated queries
7. Monitor slow query logs
8. Consider read replicas for read-heavy workloads
