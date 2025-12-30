# Replication Patterns

## Primary-Replica Replication

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

## Replication Modes

### Synchronous Replication
```sql
-- PostgreSQL synchronous replication
synchronous_commit = on
synchronous_standby_names = 'replica1,replica2'

-- Write waits for replica acknowledgment
-- Pros: No data loss, strong consistency
-- Cons: Higher latency, availability depends on replicas
```

### Asynchronous Replication
```sql
-- PostgreSQL asynchronous replication
synchronous_commit = off

-- Write returns immediately
-- Pros: Low latency, high availability
-- Cons: Potential data loss, eventual consistency
```

## Read Scaling Strategy

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

## Replication Lag Handling

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

## Multi-Leader Replication

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

## Leaderless Replication (Quorum)

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
