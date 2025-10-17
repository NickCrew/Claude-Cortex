---
name: database-design-patterns
description: Database schema design patterns and optimization strategies for relational and NoSQL databases. Use when designing database schemas, optimizing query performance, or implementing data persistence layers at scale.
---

# Database Design Patterns

Expert guidance for designing scalable database schemas, optimizing query performance, and implementing robust data persistence layers across relational and NoSQL databases.

## When to Use This Skill

- Designing database schemas for new applications
- Optimizing slow queries and database performance
- Choosing between normalization and denormalization strategies
- Implementing partitioning, sharding, or replication strategies
- Migrating between database technologies (SQL to NoSQL or vice versa)
- Designing for high availability and disaster recovery
- Implementing caching strategies and read replicas
- Scaling databases horizontally or vertically
- Ensuring data consistency in distributed systems

## Core Principles

### 1. Data Modeling Fundamentals
Schema design should reflect business domain, access patterns, and consistency requirements.

**Key Considerations:**
```
✓ Model entities and relationships clearly
✓ Design for your query patterns, not just storage
✓ Consider read vs. write ratios
✓ Plan for data growth and scalability
✓ Balance normalization with performance needs

✗ Over-normalize for OLTP workloads
✗ Ignore access patterns
✗ Premature optimization
✗ One-size-fits-all approach
```

### 2. ACID vs. BASE Trade-offs

**ACID (Relational Databases):**
- **Atomicity**: All-or-nothing transactions
- **Consistency**: Data integrity rules enforced
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed data persists

**BASE (NoSQL Databases):**
- **Basically Available**: System operates despite failures
- **Soft State**: State may change without input
- **Eventually Consistent**: Consistency achieved over time

### 3. CAP Theorem
Distributed systems can guarantee only two of three:
- **Consistency**: All nodes see same data
- **Availability**: Every request receives response
- **Partition Tolerance**: System continues despite network partitions

### 4. Polyglot Persistence
Use the right database for each use case:
- **PostgreSQL/MySQL**: Transactional data, complex queries
- **MongoDB**: Flexible schemas, document storage
- **Redis**: Caching, session storage, real-time data
- **Elasticsearch**: Full-text search, log analysis
- **Cassandra**: High write throughput, time-series data
- **Neo4j**: Graph relationships, social networks

## Schema Design Patterns

### Pattern 1: Normalization (1NF, 2NF, 3NF, BCNF)

**Purpose**: Eliminate data redundancy and maintain consistency.

**First Normal Form (1NF):**
```sql
-- Violation: Multiple values in single column
CREATE TABLE orders (
  order_id INT PRIMARY KEY,
  customer_name VARCHAR(100),
  products VARCHAR(500)  -- "Product1,Product2,Product3"
);

-- 1NF: Atomic values only
CREATE TABLE orders (
  order_id INT PRIMARY KEY,
  customer_name VARCHAR(100)
);

CREATE TABLE order_items (
  order_id INT,
  product_id INT,
  quantity INT,
  PRIMARY KEY (order_id, product_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```

**Third Normal Form (3NF):**
```sql
-- Violation: Transitive dependency
CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  employee_name VARCHAR(100),
  department_id INT,
  department_name VARCHAR(100),  -- Depends on department_id
  department_budget DECIMAL(12,2)  -- Depends on department_id
);

-- 3NF: Remove transitive dependencies
CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  employee_name VARCHAR(100),
  department_id INT,
  FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE departments (
  department_id INT PRIMARY KEY,
  department_name VARCHAR(100),
  department_budget DECIMAL(12,2)
);
```

**When to Use:**
- OLTP systems with frequent writes
- Strong consistency requirements
- Complex business rules
- Data integrity critical

**Trade-offs:**
- More tables = more joins
- Can slow down read-heavy workloads
- Complex queries for reporting

### Pattern 2: Denormalization for Performance

**Purpose**: Optimize read performance by storing redundant data.

```sql
-- Normalized (requires joins)
SELECT o.order_id, o.order_date, c.customer_name, c.email
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;

-- Denormalized (single table query)
CREATE TABLE orders_denormalized (
  order_id INT PRIMARY KEY,
  order_date DATE,
  customer_id INT,
  customer_name VARCHAR(100),  -- Redundant
  customer_email VARCHAR(100),  -- Redundant
  order_total DECIMAL(10,2)
);

-- Trade-off: Faster reads, but must update customer info in multiple places
```

**When to Use:**
- Read-heavy workloads (OLAP, analytics)
- Reporting dashboards
- Caching materialized views
- Data warehouses

**Strategies:**
- Materialized views
- Aggregate tables
- Computed columns
- ETL into data warehouse

### Pattern 3: Star Schema (Data Warehousing)

**Purpose**: Optimize analytical queries with fact and dimension tables.

```sql
-- Fact table (quantitative data)
CREATE TABLE sales_fact (
  sale_id BIGINT PRIMARY KEY,
  date_id INT,
  product_id INT,
  customer_id INT,
  store_id INT,
  quantity INT,
  revenue DECIMAL(12,2),
  cost DECIMAL(12,2),
  profit DECIMAL(12,2),
  FOREIGN KEY (date_id) REFERENCES date_dimension(date_id),
  FOREIGN KEY (product_id) REFERENCES product_dimension(product_id),
  FOREIGN KEY (customer_id) REFERENCES customer_dimension(customer_id),
  FOREIGN KEY (store_id) REFERENCES store_dimension(store_id)
);

-- Dimension tables (descriptive attributes)
CREATE TABLE date_dimension (
  date_id INT PRIMARY KEY,
  date DATE,
  year INT,
  quarter INT,
  month INT,
  day_of_week VARCHAR(10),
  is_holiday BOOLEAN
);

CREATE TABLE product_dimension (
  product_id INT PRIMARY KEY,
  product_name VARCHAR(200),
  category VARCHAR(100),
  brand VARCHAR(100),
  price DECIMAL(10,2)
);

-- Query: Total revenue by product category and quarter
SELECT
  p.category,
  d.year,
  d.quarter,
  SUM(s.revenue) as total_revenue
FROM sales_fact s
JOIN product_dimension p ON s.product_id = p.product_id
JOIN date_dimension d ON s.date_id = d.date_id
GROUP BY p.category, d.year, d.quarter;
```

**Benefits:**
- Simple queries for analysts
- Excellent query performance
- Easy to understand structure

### Pattern 4: Document Design (MongoDB)

**Purpose**: Store related data together for efficient retrieval.

**Embedding (One-to-Few):**
```javascript
// Good: Embed related data accessed together
{
  "_id": ObjectId("..."),
  "customer_name": "John Doe",
  "email": "john@example.com",
  "addresses": [
    {
      "type": "shipping",
      "street": "123 Main St",
      "city": "Boston",
      "state": "MA",
      "zip": "02101"
    },
    {
      "type": "billing",
      "street": "456 Oak Ave",
      "city": "Boston",
      "state": "MA",
      "zip": "02102"
    }
  ]
}
```

**Referencing (One-to-Many):**
```javascript
// Orders collection (parent)
{
  "_id": ObjectId("..."),
  "order_date": ISODate("2024-01-15"),
  "customer_id": ObjectId("..."),
  "item_ids": [
    ObjectId("item1"),
    ObjectId("item2"),
    ObjectId("item3")
  ]
}

// Order Items collection (children)
{
  "_id": ObjectId("item1"),
  "product_id": ObjectId("..."),
  "quantity": 2,
  "price": 29.99
}
```

**Two-Way Referencing (Many-to-Many):**
```javascript
// Products collection
{
  "_id": ObjectId("prod123"),
  "name": "Laptop",
  "category_ids": [ObjectId("cat1"), ObjectId("cat2")]
}

// Categories collection
{
  "_id": ObjectId("cat1"),
  "name": "Electronics",
  "product_ids": [ObjectId("prod123"), ObjectId("prod456")]
}
```

**Guidelines:**
- Embed data accessed together
- Reference when data is updated independently
- Avoid unbounded arrays (use pagination)
- Consider 16MB document size limit

## Indexing Strategies

### Index Types

#### B-Tree Indexes (Default for Most Databases)

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

#### Hash Indexes

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

#### Covering Indexes

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

#### Partial Indexes

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

#### Full-Text Indexes

**Purpose**: Search text content efficiently.

```sql
-- PostgreSQL full-text index
CREATE INDEX idx_products_fulltext
ON products USING GIN (to_tsvector('english', description));

-- Full-text search query
SELECT * FROM products
WHERE to_tsvector('english', description) @@ to_tsquery('laptop & wireless');
```

### Index Best Practices

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

## Partitioning Patterns

### Horizontal Partitioning (Sharding)

**Purpose**: Distribute data across multiple servers for scalability.

#### Range Partitioning

```sql
-- PostgreSQL range partitioning by date
CREATE TABLE orders (
  order_id BIGINT,
  order_date DATE,
  customer_id INT,
  order_total DECIMAL(10,2)
) PARTITION BY RANGE (order_date);

-- Partitions by month
CREATE TABLE orders_2024_01 PARTITION OF orders
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Query automatically routes to correct partition
SELECT * FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31';
```

**Benefits:**
- Old data can be archived/dropped easily
- Queries scan only relevant partitions
- Maintenance operations (VACUUM, REINDEX) per partition

#### Hash Partitioning

```sql
-- Distribute data evenly across partitions
CREATE TABLE customers (
  customer_id INT,
  customer_name VARCHAR(100),
  email VARCHAR(100)
) PARTITION BY HASH (customer_id);

CREATE TABLE customers_p0 PARTITION OF customers
FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE customers_p1 PARTITION OF customers
FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE customers_p2 PARTITION OF customers
FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE customers_p3 PARTITION OF customers
FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

**Use Cases:**
- Evenly distribute data
- No natural partitioning key
- Parallel query processing

#### List Partitioning

```sql
-- Partition by discrete values
CREATE TABLE sales (
  sale_id BIGINT,
  region VARCHAR(50),
  sale_amount DECIMAL(10,2)
) PARTITION BY LIST (region);

CREATE TABLE sales_north_america PARTITION OF sales
FOR VALUES IN ('USA', 'Canada', 'Mexico');

CREATE TABLE sales_europe PARTITION OF sales
FOR VALUES IN ('UK', 'France', 'Germany', 'Italy');

CREATE TABLE sales_asia PARTITION OF sales
FOR VALUES IN ('Japan', 'China', 'India', 'Singapore');
```

### Sharding Strategies

**Purpose**: Distribute data across multiple database servers.

#### Application-Level Sharding

```python
# Shard routing logic in application
def get_db_connection(customer_id):
    shard_id = customer_id % NUM_SHARDS
    return db_connections[shard_id]

# Write
db = get_db_connection(customer_id)
db.execute("INSERT INTO orders ...")

# Read
db = get_db_connection(customer_id)
orders = db.query("SELECT * FROM orders WHERE customer_id = ?", customer_id)
```

**Sharding Keys:**
- **Customer ID**: Isolate customer data
- **Geography**: Region-based routing
- **Tenant ID**: Multi-tenant SaaS applications
- **Hash of ID**: Even distribution

**Challenges:**
- Cross-shard queries expensive
- Rebalancing shards complex
- Transactions across shards difficult
- Schema changes require coordination

#### Database-Level Sharding

```sql
-- MongoDB sharding (automatic)
sh.enableSharding("mydb")
sh.shardCollection("mydb.orders", { customer_id: 1 })

-- Citus (PostgreSQL extension)
SELECT create_distributed_table('orders', 'customer_id');
```

**Benefits:**
- Automatic routing and balancing
- Transparent to application
- Built-in failover

## Replication Patterns

### Primary-Replica Replication

**Purpose**: Scale reads and provide high availability.

```
Primary (Write) → [Replication] → Replica 1 (Read)
                              → Replica 2 (Read)
                              → Replica 3 (Read)

Write Path:
  Application → Primary → Sync to replicas → Acknowledge

Read Path:
  Application → Load Balancer → Replica (round-robin)
```

**Replication Modes:**

#### Synchronous Replication
```sql
-- PostgreSQL synchronous replication
synchronous_commit = on
synchronous_standby_names = 'replica1,replica2'

-- Write waits for replica acknowledgment
-- Pros: No data loss, strong consistency
-- Cons: Higher latency, availability depends on replicas
```

#### Asynchronous Replication
```sql
-- PostgreSQL asynchronous replication
synchronous_commit = off

-- Write returns immediately
-- Pros: Low latency, high availability
-- Cons: Potential data loss, eventual consistency
```

**Read Scaling Strategy:**
```python
# Route reads to replicas, writes to primary
class DatabaseRouter:
    def db_for_read(self):
        return random.choice(REPLICA_CONNECTIONS)

    def db_for_write(self):
        return PRIMARY_CONNECTION

# Application code
user = User.objects.using('replica').get(id=123)  # Read from replica
user.name = "New Name"
user.save(using='primary')  # Write to primary
```

**Replication Lag Handling:**
```python
# Read-your-writes consistency
def update_user(user_id, data):
    # Write to primary
    primary_db.execute("UPDATE users SET ... WHERE id = ?", user_id)

    # Read from primary immediately after write
    return primary_db.query("SELECT * FROM users WHERE id = ?", user_id)

# For non-critical reads, use replica
def get_user_profile(user_id):
    return replica_db.query("SELECT * FROM users WHERE id = ?", user_id)
```

### Multi-Leader Replication

**Purpose**: Accept writes at multiple locations (geo-distributed).

```
Leader 1 (US) ←→ [Replication] ←→ Leader 2 (EU)
       ↓                                  ↓
   Replica 1                         Replica 2

Applications in US → Leader 1
Applications in EU → Leader 2
```

**Conflict Resolution:**
```sql
-- Last-write-wins (LWW)
UPDATE users SET
  name = 'Alice',
  updated_at = CURRENT_TIMESTAMP
WHERE id = 123;

-- Custom merge logic
-- User 1 changes email, User 2 changes name
-- Result: Both changes applied

-- Version vectors (Cassandra, DynamoDB)
-- Track changes per node
```

**Use Cases:**
- Multi-datacenter deployments
- Offline-first applications
- Collaborative editing

### Leaderless Replication (Quorum)

**Purpose**: No single leader, all nodes accept reads/writes.

```
Application → [Write to N nodes] → Node 1
                                → Node 2
                                → Node 3

Quorum: W + R > N
  N = Total replicas
  W = Write quorum
  R = Read quorum

Example: N=3, W=2, R=2
  Write succeeds when 2/3 nodes acknowledge
  Read from 2/3 nodes guarantees latest value
```

**Cassandra Example:**
```sql
-- Consistency level per query
SELECT * FROM users WHERE id = 123;
CONSISTENCY QUORUM;  -- Read from majority

INSERT INTO users (id, name) VALUES (123, 'Alice');
CONSISTENCY QUORUM;  -- Write to majority
```

**Tunable Consistency:**
- **QUORUM**: Majority (balance consistency/availability)
- **ONE**: Fastest, least consistent
- **ALL**: Slowest, most consistent
- **LOCAL_QUORUM**: Within single datacenter

## Query Optimization Techniques

### Query Analysis

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

### Optimization Strategies

#### 1. Index Optimization
```sql
-- Before: Sequential scan
SELECT * FROM orders WHERE customer_id = 123;
-- Execution time: 500ms

-- Add index
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- After: Index scan
-- Execution time: 5ms
```

#### 2. Query Rewriting
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

#### 3. Avoid N+1 Queries
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

#### 4. Pagination
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

#### 5. Batch Operations
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

### Caching Strategies

#### Application-Level Caching
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

#### Query Result Caching
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

## Best Practices Summary

1. **Schema Design**: Model for access patterns, balance normalization vs. performance
2. **Indexing**: Index frequently queried columns, avoid over-indexing
3. **Partitioning**: Use for large tables (>100M rows), time-series data
4. **Replication**: Primary-replica for read scaling, multi-leader for geo-distribution
5. **Query Optimization**: Analyze execution plans, avoid N+1 queries, use pagination
6. **Caching**: Cache hot data, invalidate on updates, use appropriate TTLs
7. **Connection Pooling**: Size pools appropriately, monitor usage
8. **Monitoring**: Track query performance, index usage, replication lag
9. **Capacity Planning**: Estimate growth, plan for 3x current load
10. **Consistency Trade-offs**: Choose appropriate consistency level per use case

## Resources

- **Books**: "Designing Data-Intensive Applications" (Kleppmann), "High Performance MySQL" (Schwartz)
- **Sites**: use-the-index-luke.com, PostgreSQL docs, MongoDB docs
- **Tools**: EXPLAIN ANALYZE, pg_stat_statements, Percona Toolkit, pt-query-digest
- **Patterns**: Star schema, event sourcing, CQRS, saga pattern, polyglot persistence
