# Query Optimization Techniques

## Query Analysis

```sql
-- PostgreSQL EXPLAIN
EXPLAIN ANALYZE
SELECT c.customer_name, COUNT(o.order_id)
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-01-01'
GROUP BY c.customer_name;

-- Look for:
-- - Sequential scans (add indexes)
-- - High cost operations
-- - Inefficient joins
-- - Missing statistics
```

## Optimization Strategies

### 1. Index Optimization
```sql
-- Before: Sequential scan
SELECT * FROM orders WHERE customer_id = 123;
-- Execution time: 500ms

-- Add index
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- After: Index scan
-- Execution time: 5ms
```

### 2. Query Rewriting
```sql
-- Inefficient: Subquery in SELECT
SELECT
  p.product_name,
  (SELECT COUNT(*) FROM orders o
   WHERE o.product_id = p.product_id) as order_count
FROM products p;

-- Efficient: JOIN with aggregation
SELECT
  p.product_name,
  COUNT(o.order_id) as order_count
FROM products p
LEFT JOIN orders o ON p.product_id = o.product_id
GROUP BY p.product_id, p.product_name;
```

### 3. Avoid N+1 Queries
```python
# Bad: N+1 queries (1 for users + N for orders)
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user.id)

# Good: Single join query
users_with_orders = db.query("""
    SELECT u.*, o.order_id, o.order_date, o.order_total
    FROM users u
    LEFT JOIN orders o ON u.user_id = o.user_id
""")
```

### 4. Pagination
```sql
-- Inefficient: OFFSET grows slower
SELECT * FROM orders
ORDER BY order_date DESC
LIMIT 100 OFFSET 10000;  -- Scans 10,100 rows

-- Efficient: Keyset pagination
SELECT * FROM orders
WHERE order_date < '2024-01-01'
ORDER BY order_date DESC
LIMIT 100;  -- Uses index
```

### 5. Batch Operations
```sql
-- Inefficient: Multiple single inserts
INSERT INTO orders (customer_id, order_date) VALUES (1, '2024-01-01');
INSERT INTO orders (customer_id, order_date) VALUES (2, '2024-01-01');
INSERT INTO orders (customer_id, order_date) VALUES (3, '2024-01-01');

-- Efficient: Batch insert
INSERT INTO orders (customer_id, order_date) VALUES
  (1, '2024-01-01'),
  (2, '2024-01-01'),
  (3, '2024-01-01');
```

## Caching Strategies

### Application-Level Caching
```python
# Redis caching layer
def get_user(user_id):
    # Check cache first
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)

    # Cache miss: query database
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)

    # Store in cache (TTL: 1 hour)
    redis.setex(f"user:{user_id}", 3600, json.dumps(user))

    return user

# Cache invalidation on update
def update_user(user_id, data):
    db.execute("UPDATE users SET ... WHERE id = ?", user_id)
    redis.delete(f"user:{user_id}")  # Invalidate cache
```

### Query Result Caching
```sql
-- Materialized views (PostgreSQL)
CREATE MATERIALIZED VIEW daily_sales_summary AS
SELECT
  DATE(order_date) as sale_date,
  SUM(order_total) as total_sales,
  COUNT(*) as order_count
FROM orders
GROUP BY DATE(order_date);

-- Refresh periodically
REFRESH MATERIALIZED VIEW daily_sales_summary;

-- Query cached results
SELECT * FROM daily_sales_summary WHERE sale_date = CURRENT_DATE;
```

## Connection Pooling

**Purpose**: Reuse database connections to reduce overhead.

```python
# Without pooling (inefficient)
def query_database():
    conn = psycopg2.connect(...)  # New connection each time
    cursor = conn.cursor()
    cursor.execute("SELECT ...")
    conn.close()

# With pooling (efficient)
from psycopg2.pool import SimpleConnectionPool

pool = SimpleConnectionPool(
    minconn=5,
    maxconn=20,
    host="localhost",
    database="mydb"
)

def query_database():
    conn = pool.getconn()  # Reuse existing connection
    cursor = conn.cursor()
    cursor.execute("SELECT ...")
    pool.putconn(conn)  # Return to pool
```

**Configuration Guidelines:**
```
Pool Size = (Number of Application Servers × Threads per Server) / Number of DB Servers

Example:
  5 app servers × 10 threads = 50 connections
  2 database servers = 25 connections per DB

Avoid:
  - Too small: Connection exhaustion, queuing
  - Too large: Memory overhead, connection limits
```
