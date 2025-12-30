# Indexing Strategies

## Index Types

### B-Tree Indexes (Default for Most Databases)

**Purpose**: Fast lookups, range queries, sorting.

```sql
-- Single column index
CREATE INDEX idx_customers_email ON customers(email);

-- Composite index (order matters!)
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date);

-- Query benefits from composite index (uses both columns)
SELECT * FROM orders
WHERE customer_id = 123
AND order_date >= '2024-01-01';

-- Query benefits partially (uses only customer_id)
SELECT * FROM orders
WHERE customer_id = 123;

-- Query does NOT benefit (order_date not leftmost)
SELECT * FROM orders
WHERE order_date >= '2024-01-01';
```

**Composite Index Guidelines:**
- Equality conditions first, then range conditions
- Most selective columns first
- Consider query patterns

### Hash Indexes

**Purpose**: Exact match lookups (very fast, O(1)).

```sql
-- PostgreSQL hash index
CREATE INDEX idx_users_username_hash
ON users USING HASH (username);

-- Only useful for equality checks
SELECT * FROM users WHERE username = 'john_doe';  -- Fast

-- NOT useful for range queries
SELECT * FROM users WHERE username > 'john';  -- Won't use index
```

**When to Use:**
- Equality searches only
- High cardinality columns (many unique values)
- Memory constraints (smaller than B-tree)

### Covering Indexes

**Purpose**: Query satisfied entirely by index (no table lookup).

```sql
-- Covering index includes all query columns
CREATE INDEX idx_orders_covering
ON orders(customer_id, order_date, order_total);

-- Query uses index-only scan (very fast)
SELECT customer_id, order_date, order_total
FROM orders
WHERE customer_id = 123
AND order_date >= '2024-01-01';
```

### Partial Indexes

**Purpose**: Index only subset of rows.

```sql
-- Index only active orders
CREATE INDEX idx_active_orders
ON orders(order_date)
WHERE status = 'active';

-- Smaller index, faster queries for active orders
SELECT * FROM orders
WHERE status = 'active'
AND order_date >= '2024-01-01';
```

### Full-Text Indexes

**Purpose**: Search text content efficiently.

```sql
-- PostgreSQL full-text index
CREATE INDEX idx_products_fulltext
ON products USING GIN (to_tsvector('english', description));

-- Full-text search query
SELECT * FROM products
WHERE to_tsvector('english', description) @@ to_tsquery('laptop & wireless');
```

## Index Best Practices

```sql
-- 1. Analyze query execution plans
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 123;

-- 2. Monitor index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan;

-- 3. Remove unused indexes
DROP INDEX idx_rarely_used;

-- 4. Consider index maintenance cost
-- Indexes slow down INSERT, UPDATE, DELETE operations
-- Balance read performance vs. write performance
```

**Index Anti-Patterns:**
- Over-indexing (too many indexes)
- Indexes on low-cardinality columns (e.g., boolean)
- Redundant indexes (column already in composite index)
- Indexes never used by queries
