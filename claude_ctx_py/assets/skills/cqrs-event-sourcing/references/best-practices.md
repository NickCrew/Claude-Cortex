# Reference: Best Practices Summary

Comprehensive best practices checklist for CQRS and Event Sourcing implementations.

## Command Design

1. **Intent Expression**: Commands represent user intent, not technical operations
2. **Validation**: Validate commands before they reach aggregates
3. **Immutability**: Commands are immutable value objects
4. **Rich Context**: Include correlation IDs, user context, timestamps
5. **Idempotency**: Include command ID for duplicate detection

## Event Design

1. **Past Tense**: Events represent facts that occurred (OrderCreated, not CreateOrder)
2. **Immutability**: Never modify published events
3. **Rich Data**: Include all data needed by consumers
4. **Versioning**: Plan for schema evolution from day one
5. **Small and Focused**: One event per state change

## Aggregate Design

1. **Consistency Boundary**: Aggregate is transaction boundary
2. **Single Responsibility**: One aggregate type per business entity
3. **Small Aggregates**: Prefer smaller aggregates for scalability
4. **Reference by ID**: Don't embed other aggregates
5. **Invariant Protection**: Enforce business rules within aggregate

## Projection Design

1. **Denormalization**: Include data from multiple aggregates
2. **Purpose-Built**: Create projections for specific query needs
3. **Idempotent Handlers**: Handle duplicate events gracefully
4. **Version Tracking**: Track last processed event version
5. **Rebuild Capability**: Support projection rebuild from events

## Event Store Management

1. **Append-Only**: Never update or delete events
2. **Snapshots**: Use snapshots for long event streams (>50 events)
3. **Archival**: Archive old events to cold storage
4. **Indexing**: Index by stream ID, type, correlation ID
5. **Monitoring**: Track event volume, processing lag, errors

## Anti-Patterns to Avoid

- ❌ **Large aggregates** - Keep them small and focused
- ❌ **Modifying events** - Events are immutable facts
- ❌ **Skipping validation** - Always validate commands
- ❌ **Tight coupling** - Aggregates should reference each other by ID only
- ❌ **Missing idempotency** - Both commands and event handlers need it
- ❌ **No versioning strategy** - Plan for schema evolution upfront
