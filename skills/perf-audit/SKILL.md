---
name: perf-audit
description: Performance auditing: identify bottlenecks, slow queries, memory leaks, CPU hotspots. Use when the user asks about performance issues, slow code, memory leaks, CPU usage, or optimizing application performance.
---

# Performance Audit

## Audit Workflow

```
1. Establish baseline metrics
2. Identify hotspots (CPU, memory, I/O, network)
3. Profile to find root causes
4. Optimize and re-measure
5. Document results
```

## CPU Hotspots

### Python

```python
import cProfile
import pstats

# Profile entire module
cProfile.run('main()', 'cpu.prof')
stats = pstats.Stats('cpu.prof')
stats.sort_stats('cumulative').print_stats(20)

# Per-function timing
from line_profiler import line_profiler

@line_profiler
def slow_function():
    total = 0
    for i in range(1000000):
        total += i * i
    return total

# Run: kernprof -l -v script.py
```

### JavaScript

```bash
# Node built-in profiler
node --prof app.js
node --prof-process isolate-*.log > processed.txt

# Chrome DevTools (most detailed)
node --inspect app.js
# Visit chrome://inspect, attach, take CPU profile

# clinic.js (production-friendly)
npx clinic doctor -- node app.js
npx clinic flame -- node app.js
```

### Go

```go
import _ "net/http/pprof"
// Add to imports — exposes /debug/pprof

// Capture CPU profile
f, _ := os.Create("cpu.prof")
pprof.StartCPUProfile(f)
defer pprof.StopCPUProfile()

// Analyze
go tool pprof cpu.prof
```

## Memory Leaks

### Python

```python
import tracemalloc

tracemalloc.start()

# ... run code ...

snapshot = tracemalloc.take_snapshot()
top = snapshot.statistics('lineno')
for stat in top[:10]:
    print(stat)

# Check for cycles
import gc
gc.set_debug(gc.DEBUG_SAVEALL)
gc.collect()
print(f"Unreachable objects: {len(gc.garbage)}")
```

### JavaScript

```javascript
// Chrome DevTools Memory tab
// 1. Take heap snapshot
// 2. Compare two snapshots
// 3. Look for retained size growth

// Node.js
const m = process.memoryUsage();
console.log(m); // { rss, heapTotal, heapUsed, external }

// Monitor over time
setInterval(() => {
    const m = process.memoryUsage();
    if (m.heapUsed > threshold) console.warn('Memory leak suspect');
}, 5000);
```

### Common Leak Patterns

```python
# Pattern 1: Growing cache without eviction
cache = {}  # BAD — unbounded
from functools import lru_cache  # GOOD — bounded

# Pattern 2: Event handler accumulation
element.addEventListener('scroll', handler)
# Missing: element.removeEventListener('scroll', handler)

# Pattern 3: Closure holding reference
def make_handler():
    data = expensive_data()
    return lambda: process(data)
# data never freed until handler is GC'd
```

## Database Query Audit

### Slow Query Detection

```sql
-- PostgreSQL
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- MySQL
SHOW PROCESSLIST;
SHOW VARIABLES LIKE 'slow_query_log%';
```

### EXPLAIN Analysis

```sql
EXPLAIN ANALYZE
SELECT u.name, o.total
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
ORDER BY o.total DESC
LIMIT 10;
```

Look for:
- `Seq Scan` on large tables → add index
- `Sort` without available index → add ORDER BY index
- `Nested Loop` with large inner → use hash join or index

### N+1 Query Detection

```python
# BAD — N+1
for user in users:
    print(user.orders.count())  # 1 query per user

# GOOD — batch
order_counts = Order.objects.filter(user__in=users).values('user_id').annotate(count=Count('id'))
order_counts_map = {c['user_id']: c['count'] for c in order_counts}
```

## I/O Bottlenecks

### File I/O

```python
# BAD — reading entire file into memory
with open('large.csv') as f:
    data = f.read()

# GOOD — streaming
with open('large.csv') as f:
    for line in f:  # line by line
        process(line)
```

### Network I/O

```python
# BAD — sequential requests
results = []
for url in urls:
    results.append(requests.get(url).json())

# GOOD — concurrent
import asyncio
import aiohttp

async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

## Load Testing

```bash
# k6
npx k6 run load-test.js

# Locust
locust -f load_test.py --headless -u 100 -r 10 --run-time 30s

# Wrk (HTTP)
wrk -t12 -c400 -d30s http://localhost:8080/api/users
```

```javascript
// k6 example
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 100 },
        { duration: '1m', target: 100 },
        { duration: '30s', target: 0 },
    ],
};

export default function() {
    const res = http.get('http://localhost:8080/api/users');
    check(res, { 'status 200': (r) => r.status === 200 });
    sleep(1);
}
```

## Performance Budget

| Metric | Target | Alert |
|--------|--------|-------|
| p95 response time | < 200ms | > 500ms |
| p99 response time | < 500ms | > 1s |
| CPU usage (per core) | < 70% | > 90% |
| Memory growth rate | 0 MB/hr | > 10 MB/hr |
| Database query time | < 50ms | > 200ms |
| Cache hit rate | > 90% | < 70% |

## Optimization Checklist

- [ ] Baseline measurements recorded
- [ ] Hotspots identified with profiler data
- [ ] N+1 queries eliminated
- [ ] Database indexes reviewed
- [ ] Caching strategy in place
- [ ] Memory growth monitored
- [ ] I/O made asynchronous where possible
- [ ] Large payloads chunked/streamed
- [ ] Load test results within budget
- [ ] Optimization documented with before/after metrics
