# Partitioning Patterns

## Horizontal Partitioning (Sharding)

**Purpose**: Distribute data across multiple servers for scalability.

### Range Partitioning

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

### Hash Partitioning

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

### List Partitioning

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

## Sharding Strategies

**Purpose**: Distribute data across multiple database servers.

### Application-Level Sharding

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

### Database-Level Sharding

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
