# Eventual Consistency Patterns

## Read-Your-Writes Consistency

### Problem
User makes change, immediately queries, sees stale data.

### Solutions

#### 1. Synchronous Projection Update:
```typescript
async createOrder(command: CreateOrderCommand): Promise<OrderSummary> {
  // Write to event store
  await this.eventStore.append(orderCreatedEvent);

  // Immediately update read model (synchronously)
  const summary = await this.projection.apply(orderCreatedEvent);

  return summary;  // User sees their change
}
```

#### 2. Version-Based Consistency:
```typescript
// Return version with write
const result = await createOrder(command);
// version: 5

// Query with minimum version
const order = await queryOrder(orderId, minVersion: 5);
// Wait until read model catches up to version 5
```

#### 3. Client-Side Optimistic Update:
```typescript
// Client immediately shows optimistic state
this.orders.push(newOrder);

// Background: wait for confirmation
await waitForEvent('OrderCreated', newOrder.id);
```

## Compensating Actions

When eventual consistency fails, undo changes:

```typescript
// Original action
await inventoryService.reserveStock(orderId, items);

// Later: payment fails, compensate
await inventoryService.releaseStock(orderId);

// Idempotent: safe to call multiple times
```

## Conflict Resolution

### Last-Write-Wins (LWW):
```typescript
if (event1.timestamp > event2.timestamp) {
  apply(event1);
} else {
  apply(event2);
}
```

### Custom Business Logic:
```typescript
// Merge inventory updates
const finalQuantity = Math.max(
  update1.quantity,
  update2.quantity
);
```

### CRDTs (Conflict-free Replicated Data Types):
```typescript
// Automatic conflict resolution
const counter = new PNCounter();
counter.increment(5);  // replica 1
counter.increment(3);  // replica 2
// Automatically merges to 8
```

## Consistency Levels

### Strong Consistency
- All replicas see same data immediately
- Lower availability, higher latency
- Use when: financial transactions, inventory counts

### Eventual Consistency
- Replicas converge over time
- Higher availability, lower latency
- Use when: social media feeds, analytics, caching

### Causal Consistency
- Events maintain cause-effect relationships
- Balance between strong and eventual
- Use when: messaging, collaborative editing
