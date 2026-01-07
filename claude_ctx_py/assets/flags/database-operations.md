# Database Operations Flags

Flags for database design, query optimization, and migration safety.

**Estimated tokens: ~180**

---

**--db / --database-focus**
- Trigger: Schema changes, query optimization, data modeling, database migrations
- Behavior: Database-first thinking with migration safety and performance focus
- Auto-enables: Query analysis, index recommendations, N+1 detection, migration validation
- Validates: Migration reversibility, data consistency, referential integrity, performance impact
- Analyzes: Query patterns, access patterns, data growth, read vs write ratios
- Tools: EXPLAIN plans, query profiling, slow query logs, database metrics

**--query-optimize**
- Trigger: Slow queries, high database load, scalability issues, timeout errors
- Behavior: Analyze and optimize database queries for performance
- Checks: Index usage (covering indexes, partial indexes), query plans, JOIN efficiency
- Detects: Sequential scans, missing indexes, inefficient JOINs, N+1 queries
- Suggests: Index creation, query rewrites, denormalization, caching strategies, pagination
- Reports: Query execution time, rows examined, index usage, optimization impact
- Tools: EXPLAIN ANALYZE, query profilers, pg_stat_statements, slow query logs

**--schema-design**
- Trigger: New features, data model changes, normalization decisions, schema evolution
- Behavior: Design optimal database schemas with best practices
- Validates: Normalization (1NF, 2NF, 3NF), relationships (1:1, 1:N, N:M), constraints (FK, UNIQUE, CHECK)
- Considers: Read vs write patterns, query patterns, data access patterns, future scalability
- Patterns: Single table inheritance, polymorphic associations, event sourcing, CQRS
- Trade-offs: Normalization vs denormalization, joins vs redundancy, consistency vs performance
- Generates: Entity-relationship diagrams, schema migration scripts, index strategies

**--index-strategy**
- Trigger: Query optimization, performance tuning, slow queries, table scans
- Behavior: Design and validate database indexing strategies
- Analyzes: Query patterns, WHERE clauses, JOIN conditions, ORDER BY usage, covering indexes
- Types: B-tree (default), Hash, GiST, GIN (full-text), partial indexes, expression indexes
- Validates: Index selectivity, index size vs benefit, index maintenance cost
- Prevents: Over-indexing (write penalty), missing indexes (read penalty), redundant indexes
- Reports: Index usage statistics, unused indexes, index bloat, maintenance recommendations

**--transaction-safety**
- Trigger: Concurrent writes, data consistency requirements, ACID guarantees
- Behavior: Ensure proper transaction isolation and consistency
- Validates: Isolation levels (Read Uncommitted, Read Committed, Repeatable Read, Serializable)
- Detects: Race conditions, lost updates, dirty reads, phantom reads, deadlocks
- Patterns: Optimistic locking (version column), pessimistic locking (SELECT FOR UPDATE)
- Ensures: Atomicity, consistency, isolation, durability (ACID properties)
- Handles: Deadlock detection, retry logic, timeout configuration, connection pooling

**--data-integrity**
- Trigger: Data validation, constraint enforcement, referential integrity
- Behavior: Enforce data integrity through database constraints and validation
- Validates: NOT NULL constraints, UNIQUE constraints, CHECK constraints, foreign keys
- Checks: Orphaned records, constraint violations, data type mismatches, invalid states
- Patterns: Database-level validation vs application-level validation trade-offs
- Ensures: Referential integrity, domain integrity, entity integrity, user-defined integrity
- Tools: Constraint checking, data validation queries, integrity verification scripts

**--connection-pooling**
- Trigger: High concurrency, scalability requirements, connection exhaustion
- Behavior: Configure and optimize database connection pooling
- Parameters: Pool size (min/max), timeout, idle timeout, connection lifetime
- Patterns: Connection pooling, connection reuse, lazy connection acquisition
- Validates: No connection leaks, proper connection cleanup, timeout configuration
- Monitors: Active connections, idle connections, wait time, connection errors
- Tools: PgBouncer, HikariCP, connection pool libraries, database metrics
