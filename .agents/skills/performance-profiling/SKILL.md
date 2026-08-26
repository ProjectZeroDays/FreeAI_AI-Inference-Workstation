---
name: performance-profiling
description: Performance optimization, profiling tools, memory analysis, CPU profiling, query optimization, and benchmarking. Use when the user asks about making code faster, profiling performance, reducing memory usage, optimizing queries, or benchmarking code.
---

# Performance Profiling

## Python Profiling

### cProfile
```python
import cProfile
import pstats

# Profile a function
cProfile.run('my_function()', 'profile_output')

# Analyze results
stats = pstats.Stats('profile_output')
stats.sort_stats('cumulative')
stats.print_stats(20)

# Context manager
with cProfile.Profile() as pr:
    my_function()
pr.print_stats(sort='cumulative')
```

### Line Profiler
```python
# pip install line_profiler
@profile
def slow_function():
    ...

# Run: kernprof -l -v script.py
```

### Memory Profiler
```python
# pip install memory_profiler
@profile
def memory_heavy():
    data = [i for i in range(1000000)]
    return sum(data)

# Run: python -m memory_profiler script.py
```

## Node.js Profiling

### Built-in Profiler
```bash
# CPU profile
node --prof app.js
node --prof-process isolate-*.log > processed.txt

# Chrome DevTools
node --inspect app.js
# Open chrome://inspect
```

### Clinic.js
```bash
npx clinic doctor -- node app.js
npx clinic flame -- node app.js
npx clinic bubbleprof -- node app.js
```

## Database Query Optimization

### PostgreSQL
```sql
-- Find slow queries
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Analyze query plan
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@example.com';

-- Add index
CREATE INDEX idx_users_email ON users(email);

-- Partial index
CREATE INDEX idx_active_users ON users(email)
WHERE active = true;
```

### Common Optimizations
```sql
-- BAD: SELECT *
SELECT * FROM orders WHERE user_id = 123;

-- GOOD: Select only needed columns
SELECT id, total, status FROM orders WHERE user_id = 123;

-- BAD: N+1 queries
-- Loop: SELECT * FROM posts WHERE user_id = ?

-- GOOD: JOIN
SELECT p.*, u.name
FROM posts p
JOIN users u ON p.user_id = u.id
WHERE p.user_id IN (1, 2, 3);
```

## Frontend Performance

### Core Web Vitals
```
LCP (Largest Contentful Paint): < 2.5s
FID (First Input Delay): < 100ms
CLS (Cumulative Layout Shift): < 0.1
```

### Lazy Loading
```javascript
// Image lazy loading
<img loading="lazy" src="photo.jpg" />

// Route lazy loading
const Dashboard = lazy(() => import('./Dashboard'));

// Intersection Observer
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      loadComponent(entry.target);
    }
  });
});
```

### Bundle Optimization
```javascript
// Dynamic imports
button.addEventListener('click', async () => {
  const { heavyModule } = await import('./heavy-module');
  heavyModule.doWork();
});
```

## Go Profiling

```go
import "runtime/pprof"

// CPU Profile
f, _ := os.Create("cpu.prof")
pprof.StartCPUProfile(f)
defer pprof.StopCPUProfile()

// Memory Profile
f, _ := os.Create("mem.prof")
pprof.WriteHeapProfile(f)
f.Close()

// Analyze: go tool pprof cpu.prof
```

## Benchmarking

### Python
```python
import timeit

# Quick benchmark
timeit.timeit('sum(range(1000))', number=10000)

# Compare approaches
t1 = timeit.timeit(lambda: [i**2 for i in range(1000)], number=1000)
t2 = timeit.timeit(lambda: list(map(lambda x: x**2, range(1000))), number=1000)
print(f"List comp: {t1:.3f}s, Map: {t2:.3f}s")
```

### Go
```go
func BenchmarkSlow(b *testing.B) {
    for i := 0; i < b.N; i++ {
        slowFunction()
    }
}

// Run: go test -bench=. -benchmem
```

## Common Bottlenecks

| Bottleneck | Solution |
|-----------|----------|
| N+1 queries | Use JOINs or eager loading |
| Missing index | Add database index |
| Blocking I/O | Use async/non-blocking |
| Large allocations | Use object pooling |
| Repeated computation | Memoization/caching |
| Uncompressed assets | gzip/brotli compression |
| Synchronous rendering | Streaming/SSR |

## Caching Strategies

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(n):
    return sum(i ** 2 for i in range(n))

# Cache invalidation
@lru_cache(maxsize=100)
def get_user(user_id):
    return db.query(User).get(user_id)

# Manual invalidation
get_user.cache_clear()
```

## Monitoring in Production

```bash
# System resources
top -o %CPU
htop
free -h
iostat -x 1

# Network
netstat -tlnp
ss -tlnp

# Database
pg_top  # PostgreSQL
```
