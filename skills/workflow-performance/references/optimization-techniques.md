# Performance Optimization Techniques

Practical techniques for profiling, optimizing, and validating performance across the full stack.

## Profiling Methodology

### CPU Profiling

**Goal**: Identify functions consuming the most CPU time.

```bash
# Node.js: built-in profiler
node --prof app.js
node --prof-process isolate-*.log > processed.txt

# Node.js: clinic.js flame graphs
npx clinic flame -- node app.js

# Python: cProfile
python -m cProfile -s cumulative app.py

# Python: py-spy (sampling profiler, no code changes)
py-spy record -o profile.svg -- python app.py
```

**Analysis checklist**:
- Look for hot functions (>5% of total CPU time)
- Check for unexpected recursive calls or tight loops
- Identify synchronous operations that should be async
- Compare user time vs. system time vs. idle time

### Memory Profiling

```bash
# Node.js: heap snapshot
node --inspect app.js
# Then in Chrome DevTools: Memory -> Take Heap Snapshot

# Node.js: track allocations over time
node --expose-gc --inspect app.js

# Python: tracemalloc
python -c "
import tracemalloc
tracemalloc.start()
# ... run code ...
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:10]:
    print(stat)
"
```

**Memory leak detection pattern**:
1. Take baseline heap snapshot
2. Exercise the suspected leaking operation 100x
3. Force garbage collection
4. Take second snapshot
5. Compare: growing object counts indicate a leak

### I/O Profiling

```bash
# Linux: identify I/O bottlenecks
iostat -x 1 10
iotop -o

# Database query profiling (PostgreSQL)
SET log_min_duration_statement = 100;  -- log queries > 100ms
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 20;

# Network latency tracing
curl -w "@curl-timing.txt" -o /dev/null -s https://api.example.com/endpoint
```

**curl-timing.txt format**:
```
    DNS lookup:  %{time_namelookup}s
    TCP connect: %{time_connect}s
    TLS handshake: %{time_appconnect}s
    First byte:  %{time_starttransfer}s
    Total:       %{time_total}s
```

### Profiling Decision Tree

```
Symptom: High latency
  -> Is CPU utilization high?
     YES -> CPU profile -> optimize hot paths
     NO  -> Is memory pressure high?
            YES -> Memory profile -> fix leaks/reduce allocations
            NO  -> Is I/O wait high?
                   YES -> I/O profile -> optimize queries/network
                   NO  -> Check for lock contention / event loop blocking
```

## Core Web Vitals Optimization

### Largest Contentful Paint (LCP) - Target: < 2.5s

**Common causes and fixes**:

| Cause | Fix |
|---|---|
| Slow server response | CDN, edge caching, server-side caching |
| Render-blocking resources | `async`/`defer` scripts, inline critical CSS |
| Slow resource load | Preload hero image, use responsive images, WebP/AVIF |
| Client-side rendering | SSR/SSG for initial content, streaming HTML |

```html
<!-- Preload LCP image -->
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">

<!-- Inline critical CSS -->
<style>/* critical path CSS here */</style>
<link rel="stylesheet" href="/full.css" media="print" onload="this.media='all'">
```

### Interaction to Next Paint (INP) - Target: < 200ms

**Common causes and fixes**:

| Cause | Fix |
|---|---|
| Long tasks blocking main thread | Break into smaller tasks with `scheduler.yield()` |
| Heavy event handlers | Debounce, throttle, use `requestIdleCallback` |
| Layout thrashing | Batch DOM reads/writes, use `requestAnimationFrame` |
| Expensive re-renders | Memoize components, virtualize long lists |

```javascript
// Break up long tasks
async function processItems(items) {
  for (const item of items) {
    processItem(item);
    // Yield to main thread between items
    if (navigator.scheduling?.isInputPending()) {
      await scheduler.yield();
    }
  }
}
```

### Cumulative Layout Shift (CLS) - Target: < 0.1

**Prevention checklist**:
- Set explicit `width`/`height` on images and videos
- Use `aspect-ratio` CSS for responsive media
- Reserve space for dynamic content (ads, embeds)
- Use `transform` animations instead of layout-triggering properties
- Add `font-display: swap` with proper fallback font metrics

```css
/* Prevent CLS from web fonts */
@font-face {
  font-family: 'CustomFont';
  src: url('/font.woff2') format('woff2');
  font-display: swap;
  size-adjust: 105%;       /* Match fallback metrics */
  ascent-override: 90%;
  descent-override: 20%;
}
```

## Caching Strategies

### Cache Layer Hierarchy

```
Request -> Browser Cache -> CDN/Edge -> Reverse Proxy -> App Cache -> Database Cache -> Database
```

### Browser Caching

```
# Immutable assets (hashed filenames)
Cache-Control: public, max-age=31536000, immutable

# HTML pages (revalidate every time)
Cache-Control: no-cache
ETag: "abc123"

# API responses (short TTL)
Cache-Control: private, max-age=60, stale-while-revalidate=300
```

### CDN Caching

**Strategy by content type**:

| Content | TTL | Cache Key | Invalidation |
|---|---|---|---|
| Static assets (JS/CSS/images) | 1 year | URL (hashed filename) | Deploy new hash |
| HTML pages | 60s | URL + vary headers | Purge on publish |
| API responses | 5-60s | URL + auth token | TTL expiry |
| User-specific content | 0 (bypass) | - | - |

### Application-Level Caching

```python
# Redis caching pattern with cache-aside
import redis
import json

cache = redis.Redis()

def get_user_profile(user_id):
    cache_key = f"user:profile:{user_id}"

    # 1. Check cache
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. Cache miss: query database
    profile = db.query("SELECT * FROM users WHERE id = %s", user_id)

    # 3. Populate cache with TTL
    cache.setex(cache_key, 300, json.dumps(profile))  # 5 min TTL

    return profile

def update_user_profile(user_id, data):
    db.update("UPDATE users SET ... WHERE id = %s", user_id)
    # Invalidate cache on write
    cache.delete(f"user:profile:{user_id}")
```

### Database Query Caching

- **Query result cache**: Cache frequent read queries (Redis, Memcached)
- **Materialized views**: Pre-compute expensive aggregations
- **Prepared statements**: Reduce query parse overhead
- **Connection pooling**: Reuse database connections (PgBouncer, ProxySQL)

## Database Query Optimization

### Query Analysis Workflow

```sql
-- 1. Find slow queries (PostgreSQL)
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 20;

-- 2. Analyze execution plan
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;

-- 3. Check for sequential scans on large tables
SELECT relname, seq_scan, idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan AND n_live_tup > 10000
ORDER BY seq_scan DESC;
```

### Common Optimization Patterns

| Problem | Solution |
|---|---|
| Sequential scan on large table | Add index on WHERE/JOIN columns |
| N+1 queries | Batch with JOIN or IN clause |
| Sorting large result sets | Index on ORDER BY columns |
| Complex aggregations | Materialized view or pre-computed table |
| Full table locks | Row-level locking, optimistic concurrency |
| Excessive columns | Select only needed columns |

### Index Strategy

```sql
-- Composite index (match query column order)
CREATE INDEX idx_orders_user_date ON orders (user_id, created_at DESC);

-- Partial index (reduce index size)
CREATE INDEX idx_orders_active ON orders (user_id) WHERE status = 'active';

-- Covering index (avoid table lookup)
CREATE INDEX idx_orders_cover ON orders (user_id, created_at) INCLUDE (total, status);
```

**Index decision rules**:
- Index columns used in WHERE, JOIN, ORDER BY
- Put high-selectivity columns first in composite indexes
- Use partial indexes when queries filter on a constant value
- Drop unused indexes (they slow writes): check `pg_stat_user_indexes`

## Frontend Bundle Optimization

### Analysis

```bash
# Webpack bundle analysis
npx webpack-bundle-analyzer stats.json

# Vite bundle analysis
npx vite-bundle-visualizer

# Next.js built-in
ANALYZE=true next build
```

### Optimization Techniques

**Code splitting**:
```javascript
// Route-level splitting (React)
const Dashboard = React.lazy(() => import('./Dashboard'));

// Component-level splitting
const HeavyChart = React.lazy(() =>
  import(/* webpackChunkName: "chart" */ './HeavyChart')
);
```

**Tree shaking**:
```javascript
// BAD: imports entire library
import _ from 'lodash';
_.get(obj, 'path');

// GOOD: imports only what's needed
import get from 'lodash/get';
get(obj, 'path');
```

**Asset optimization checklist**:
- [ ] Images: WebP/AVIF with fallback, responsive `srcset`, lazy load below fold
- [ ] Fonts: Subset to used characters, `woff2` format, `font-display: swap`
- [ ] CSS: Purge unused styles, critical CSS inline, async load remainder
- [ ] JavaScript: Minify, compress (gzip/brotli), defer non-critical scripts

### Bundle Size Budgets

| Asset Type | Budget |
|---|---|
| Initial JS | < 200 KB (compressed) |
| Initial CSS | < 50 KB (compressed) |
| Hero image | < 100 KB |
| Web font (per family) | < 50 KB |
| Total initial page weight | < 500 KB |

## Load Testing Methodology

### Test Scenarios

| Scenario | Purpose | Configuration |
|---|---|---|
| Smoke test | Verify system works under minimal load | 1-5 VUs, 1 min |
| Load test | Validate performance at expected traffic | Target VUs, 30 min |
| Stress test | Find the breaking point | Ramp to 2-3x target, 15 min |
| Soak test | Detect memory leaks and degradation | Target VUs, 2-4 hours |
| Spike test | Test sudden traffic bursts | 0 to 10x VUs in 1 min |

### k6 Load Test Example

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // ramp up
    { duration: '5m', target: 50 },   // steady state
    { duration: '2m', target: 100 },  // push to peak
    { duration: '5m', target: 100 },  // hold peak
    { duration: '2m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/endpoint');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

### Interpreting Results

**Key metrics to track**:
- **p50/p95/p99 response times**: p95 is the primary target
- **Error rate**: Should stay below 1% under normal load
- **Throughput**: Requests per second at steady state
- **Resource utilization**: CPU, memory, connections during test

**Red flags**:
- p99 > 3x p50 (high variance, likely contention)
- Error rate spikes at specific VU count (capacity ceiling)
- Steady latency increase over time (resource leak)
- Throughput plateau while latency climbs (saturation)

## Monitoring and Alerting

### Key Metrics to Monitor

| Layer | Metrics | Tool Examples |
|---|---|---|
| Frontend | LCP, INP, CLS, JS errors | RUM (Datadog, Sentry) |
| API | p95 latency, error rate, throughput | APM (Datadog, New Relic) |
| Database | Query time, connections, replication lag | pg_stat, slow query log |
| Infrastructure | CPU, memory, disk, network | Prometheus + Grafana |

### Alerting Thresholds

```yaml
# Example alerting rules
alerts:
  - name: high_api_latency
    condition: p95_response_time > 500ms for 5m
    severity: warning

  - name: critical_api_latency
    condition: p95_response_time > 2000ms for 2m
    severity: critical

  - name: high_error_rate
    condition: error_rate > 1% for 5m
    severity: warning

  - name: critical_error_rate
    condition: error_rate > 5% for 2m
    severity: critical

  - name: memory_leak_suspect
    condition: memory_usage increasing > 10% over 1h
    severity: warning

  - name: database_connection_saturation
    condition: active_connections > 80% of max for 5m
    severity: warning
```

### Performance Dashboard Essentials

A useful performance dashboard should include:

1. **Overview panel**: Request rate, error rate, p50/p95/p99 latency (last 24h)
2. **Endpoint breakdown**: Top 10 slowest endpoints with trend lines
3. **Database panel**: Slow queries, connection pool usage, replication lag
4. **Infrastructure panel**: CPU, memory, disk I/O per service
5. **Frontend panel**: Core Web Vitals distribution, JS error rate
6. **Comparison view**: Current vs. previous deploy metrics
