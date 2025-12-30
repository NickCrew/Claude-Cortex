# Core Principles

## Data Modeling Fundamentals
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

## ACID vs. BASE Trade-offs

**ACID (Relational Databases):**
- **Atomicity**: All-or-nothing transactions
- **Consistency**: Data integrity rules enforced
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed data persists

**BASE (NoSQL Databases):**
- **Basically Available**: System operates despite failures
- **Soft State**: State may change without input
- **Eventually Consistent**: Consistency achieved over time

## CAP Theorem
Distributed systems can guarantee only two of three:
- **Consistency**: All nodes see same data
- **Availability**: Every request receives response
- **Partition Tolerance**: System continues despite network partitions

## Polyglot Persistence
Use the right database for each use case:
- **PostgreSQL/MySQL**: Transactional data, complex queries
- **MongoDB**: Flexible schemas, document storage
- **Redis**: Caching, session storage, real-time data
- **Elasticsearch**: Full-text search, log analysis
- **Cassandra**: High write throughput, time-series data
- **Neo4j**: Graph relationships, social networks
