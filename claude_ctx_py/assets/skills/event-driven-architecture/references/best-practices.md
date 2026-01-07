# Best Practices for Event-Driven Architecture

## Event Design

1. **Immutable Events**: Never modify published events
2. **Past Tense**: Name events for what happened (OrderCreated, not CreateOrder)
3. **Rich Events**: Include all data consumers need
4. **Versioning**: Plan for schema evolution from day one
5. **Correlation**: Always include correlation and causation IDs

## Architecture

1. **Idempotency**: All event handlers must be idempotent
2. **At-Least-Once**: Design for duplicate event delivery
3. **Ordering**: Don't assume global ordering unless guaranteed
4. **Partitioning**: Use partition keys for ordered processing
5. **Dead Letters**: Handle poison messages with DLQ

## Implementation

1. **Event Store First**: Append to event store before publishing
2. **Transactional Outbox**: Ensure events published exactly once
3. **Snapshots**: Use snapshots for long event streams
4. **Projections**: Keep read models eventually consistent
5. **Monitoring**: Track event lag, processing time, failures

## Operations

1. **Event Replay**: Build capability to replay events
2. **Schema Registry**: Centralize event schema management
3. **Testing**: Test event handlers in isolation
4. **Debugging**: Use correlation IDs for distributed tracing
5. **Versioning**: Support multiple event versions simultaneously

## Scaling

1. **Partitioning**: Partition by aggregate ID for parallelism
2. **Consumer Groups**: Scale consumers horizontally
3. **Backpressure**: Handle slow consumers gracefully
4. **Retention**: Define event retention policies
5. **Archival**: Archive old events to cold storage

## Common Anti-Patterns

### 1. Event as Command
```
❌ Bad: PublishCreateOrder()
✓ Good: PublishOrderCreated()

Events are facts, not instructions.
```

### 2. Missing Idempotency
```
❌ Bad: handler processes same event twice → duplicate actions
✓ Good: handler checks event_id before processing

All handlers must be idempotent.
```

### 3. Synchronous Event Chain
```
❌ Bad: Service A waits for Service B's event processing
✓ Good: Service A publishes and continues, Service B processes async

Events should be fire-and-forget.
```

### 4. Events Without Schema Version
```
❌ Bad: { "type": "OrderCreated", "data": {...} }
✓ Good: { "type": "OrderCreated", "version": "1.0", "data": {...} }

Always version your events for evolution.
```

### 5. Coupling Through Events
```
❌ Bad: Event contains specific implementation details
✓ Good: Event contains business-level data only

Events should be domain-focused, not implementation-focused.
```

## Testing Strategies

### Unit Testing Event Handlers:
```typescript
describe('OrderProjection', () => {
  it('creates order summary on OrderCreated', async () => {
    const event = new OrderCreated({ orderId: '123', ... });

    await projection.on(event);

    const summary = await db.findOrder('123');
    expect(summary.status).toBe('PENDING');
  });
});
```

### Integration Testing Sagas:
```typescript
describe('OrderSaga', () => {
  it('completes full order flow', async () => {
    const command = new CreateOrderCommand({ ... });

    await saga.execute(command);

    expect(orderService.confirmOrder).toHaveBeenCalled();
    expect(inventoryService.reserveInventory).toHaveBeenCalled();
    expect(paymentService.processPayment).toHaveBeenCalled();
  });

  it('compensates on payment failure', async () => {
    paymentService.processPayment.mockRejectedValue(new Error('Declined'));

    await expect(saga.execute(command)).rejects.toThrow();

    expect(inventoryService.releaseInventory).toHaveBeenCalled();
    expect(orderService.cancelOrder).toHaveBeenCalled();
  });
});
```

### Contract Testing Events:
```typescript
describe('OrderCreated Event Schema', () => {
  it('matches published contract', () => {
    const event = new OrderCreated({ ... });

    const schema = loadSchema('OrderCreated', 'v1.0');
    expect(event).toMatchSchema(schema);
  });
});
```
