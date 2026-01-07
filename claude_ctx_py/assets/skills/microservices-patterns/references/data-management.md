# Data Management Patterns

## Pattern: Database per Service

**Principle**: Each service has its own database, never shared.

```
Order Service → Orders DB (PostgreSQL)
Inventory Service → Inventory DB (PostgreSQL)
Product Service → Products DB (MongoDB)
Analytics Service → Analytics DB (ClickHouse)

Benefits:
- Independent scaling
- Technology choice flexibility
- Loose coupling
- Clear ownership

Challenges:
- No cross-service joins
- Distributed transactions
- Data consistency
```

## Pattern: Saga (Distributed Transactions)

**Purpose**: Maintain data consistency across services without 2PC.

### Orchestration-Based Saga
```
Order Saga Orchestrator:

1. Create Order (Order Service)
   ↓ success
2. Reserve Inventory (Inventory Service)
   ↓ success
3. Process Payment (Payment Service)
   ↓ success
4. Update Order Status (Order Service)
   ↓ failure → Compensate
5. Compensating Transactions:
   - Release Inventory
   - Refund Payment
   - Cancel Order

Implementation:
- Orchestrator maintains state machine
- Explicit control flow
- Centralized logic
```

### Choreography-Based Saga
```
Event-Driven Saga:

OrderCreated event
  → Inventory Service reserves stock
    → InventoryReserved event
      → Payment Service processes payment
        → PaymentProcessed event
          → Order Service updates status

If failure at any step:
  → Compensating events cascade backwards

Implementation:
- Decentralized coordination
- Event-driven
- Implicit control flow
```

## Pattern: CQRS (Command Query Responsibility Segregation)

**Definition**: Separate read and write models for optimal performance.

```
Write Model (Commands):
  - Optimized for consistency
  - Normalized schema
  - Transactional

Read Model (Queries):
  - Optimized for performance
  - Denormalized views
  - Eventually consistent
  - Materialized views/caching

Sync via events:
  Command → Write DB → Event → Read DB(s)

Example:
  Write: OrderCreated → Orders DB (PostgreSQL)
  Event: OrderCreated published
  Read: Update OrderSummary view (Redis)
        Update OrderAnalytics (Elasticsearch)
```

## Pattern: API Composition

**Purpose**: Join data from multiple services at the API layer.

```
GET /customers/123/dashboard

API Gateway:
1. GET /customers/123 (Customer Service)
2. GET /orders?customer_id=123 (Order Service)
3. GET /recommendations/123 (Recommendation Service)
4. Compose response:

{
  "customer": {...},
  "recent_orders": [...],
  "recommendations": [...]
}

Challenges:
- N+1 queries
- Slower response time
- Complex error handling

Optimizations:
- Parallel requests
- GraphQL (client-controlled aggregation)
- Backend for Frontend (BFF) pattern
```

## Data Consistency Strategies

### Eventual Consistency

**Definition**: Data becomes consistent over time, not immediately.

```
Example: Order placed
1. Order Service: Create order (status: PENDING)
2. Event published: OrderCreated
3. Inventory Service: Reserve stock (async)
4. Payment Service: Process payment (async)
5. Order Service: Update status to CONFIRMED (eventually)

Time window: seconds to minutes

Acceptable for:
- Social media feeds
- Product recommendations
- Analytics dashboards
- Non-critical updates

NOT acceptable for:
- Financial transactions (use Saga)
- Inventory reservations (use Saga)
- Critical business rules
```

### Strong Consistency (within service)

**Pattern**: ACID transactions within service boundaries.

```
Order Service Transaction:
BEGIN;
  INSERT INTO orders (...);
  UPDATE inventory SET reserved = reserved + qty;
  INSERT INTO order_items (...);
COMMIT;

Keep related data in same service to maintain ACID.
```

## Data Replication Patterns

### Change Data Capture (CDC)

**Pattern**: Capture database changes and publish as events.

```
Database → Transaction Log → CDC Tool → Event Stream → Consumers

Tools:
- Debezium (Kafka Connect)
- AWS DMS
- Maxwell's Daemon
- Databus (LinkedIn)

Example:
orders table changes → Debezium → Kafka topic → Analytics Service

Benefits:
- No application code changes
- Guaranteed event publication
- Ordered events per entity
```

### Read Replicas

**Pattern**: Replicate data for read scaling.

```
Write: Client → Primary DB
Read: Client → Read Replica 1/2/3

Lag: Eventually consistent (seconds)

Use for:
- Analytics queries
- Search indexing
- Reporting dashboards
- Read-heavy workloads
```

## Data Access Patterns

### API per Service

**Rule**: Only access service data through its API, never directly to database.

```
❌ WRONG:
Order Service → Inventory DB (direct access)

✅ CORRECT:
Order Service → Inventory Service API → Inventory DB

Why?
- Maintains encapsulation
- Allows service to evolve data model
- Enables security/validation
- Supports versioning
```

### Shared Data Services

**Pattern**: Create dedicated service for truly shared data.

```
Example: Reference Data Service
- Country codes
- Currency rates
- Product categories
- Tax rates

Characteristics:
- Read-mostly data
- Infrequent updates
- Needed by multiple services
- Cacheable
```

## Data Migration Strategies

### Dual Writes (Transitional)

**Pattern**: Write to both old and new data stores during migration.

```
Migration phases:
1. Old DB only (monolith)
2. Dual write (old + new)
3. Migrate existing data
4. Verify consistency
5. Switch reads to new
6. Remove old writes
7. Decommission old DB

Caution: Not atomic, use for read-mostly data
```

### Event-Based Migration

**Pattern**: Publish events from monolith, new services consume.

```
Monolith → Events → New Microservice
         → Old DB → (gradually deprecated)

Advantages:
- Less risky than dual writes
- Services can evolve independently
- Supports gradual migration
```

## Tools and Technologies

### Databases
- **Relational**: PostgreSQL, MySQL, SQL Server
- **Document**: MongoDB, Couchbase, DynamoDB
- **Key-Value**: Redis, Memcached
- **Column**: Cassandra, HBase
- **Search**: Elasticsearch, Solr
- **Time-Series**: InfluxDB, TimescaleDB
- **Graph**: Neo4j, Amazon Neptune

### Saga Orchestration
- **Frameworks**: Axon Framework, Eventuate, Temporal
- **Workflow Engines**: Camunda, Zeebe, Conductor (Netflix)
- **Custom**: State machine in code

### CDC Tools
- **Debezium**: Kafka-based CDC for MySQL, PostgreSQL, MongoDB
- **Maxwell**: MySQL binlog to Kafka
- **AWS DMS**: Database Migration Service

## Best Practices

1. **Database per Service** - Mandatory, no exceptions
2. **Own Your Data** - Each service is the source of truth for its data
3. **Event-Driven** - Use events for cross-service data synchronization
4. **Embrace Eventual Consistency** - Design for it from the start
5. **Saga for Transactions** - Use orchestration or choreography patterns
6. **CQRS for Complex Queries** - Separate read/write models when needed
7. **Cache Aggressively** - Reduce cross-service calls with caching
8. **Monitor Data Lag** - Track eventual consistency lag in production
9. **Version Your Events** - Event schema evolution strategy
10. **Test Distributed Scenarios** - Chaos engineering for data consistency

## Common Pitfalls

❌ **Shared Database** - Multiple services accessing same database
❌ **Distributed Transactions** - 2PC across services (avoid at all costs)
❌ **Synchronous Saga** - Blocking saga calls (use async)
❌ **Missing Compensations** - Saga without rollback logic
❌ **No Idempotency** - Duplicate event processing causes issues
❌ **Ignoring Data Lag** - Not monitoring eventual consistency delays
❌ **Direct DB Access** - Bypassing service APIs

## Further Reading

- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Microservices Patterns" by Chris Richardson (Saga patterns)
- microservices.io/patterns/data
- martinfowler.com/articles/microservices.html#DecentralizedDataManagement
