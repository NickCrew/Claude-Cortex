# Event Sourcing Pattern

## Definition
Store all state changes as a sequence of immutable events instead of current state.

## Traditional vs Event Sourcing

### Traditional CRUD:
```sql
-- Users table stores current state
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255),
  status VARCHAR(50),
  updated_at TIMESTAMP
);

-- Single row, state overwrites history
UPDATE users SET email = 'new@email.com' WHERE id = 'user_123';
```

### Event Sourcing:
```sql
-- Event store holds all changes
CREATE TABLE user_events (
  event_id UUID PRIMARY KEY,
  aggregate_id UUID,  -- user_id
  event_type VARCHAR(100),
  event_data JSONB,
  event_version INTEGER,
  timestamp TIMESTAMP,
  sequence_number BIGSERIAL
);

-- Append-only, never update
INSERT INTO user_events VALUES (
  'evt_001', 'user_123', 'UserCreated',
  '{"name": "John", "email": "john@example.com"}', 1, NOW()
);

INSERT INTO user_events VALUES (
  'evt_002', 'user_123', 'EmailChanged',
  '{"old_email": "john@example.com", "new_email": "new@email.com"}', 1, NOW()
);

-- Current state = replay all events
```

## Implementation

### Event Store Interface:
```typescript
interface EventStore {
  // Append events to stream
  appendEvents(
    streamId: string,
    events: DomainEvent[],
    expectedVersion: number
  ): Promise<void>;

  // Read events from stream
  readEvents(
    streamId: string,
    fromVersion?: number
  ): Promise<DomainEvent[]>;

  // Read all events across streams
  readAllEvents(
    fromPosition?: number,
    maxCount?: number
  ): Promise<DomainEvent[]>;
}

// Aggregate root reconstructs from events
class Order {
  private id: string;
  private status: OrderStatus;
  private items: OrderItem[];
  private version: number = 0;

  // Replay events to rebuild state
  static fromEvents(events: OrderEvent[]): Order {
    const order = new Order();
    for (const event of events) {
      order.apply(event);
      order.version++;
    }
    return order;
  }

  private apply(event: OrderEvent): void {
    switch (event.type) {
      case 'OrderCreated':
        this.id = event.data.orderId;
        this.status = 'PENDING';
        this.items = event.data.items;
        break;
      case 'OrderPaid':
        this.status = 'PAID';
        break;
      case 'OrderShipped':
        this.status = 'SHIPPED';
        break;
    }
  }
}
```

## Benefits

1. **Complete Audit Trail**: Every state change recorded
2. **Temporal Queries**: "What was the state at time T?"
3. **Event Replay**: Rebuild state, fix bugs, test scenarios
4. **New Projections**: Create new read models from existing events
5. **Debugging**: Understand exactly what happened
6. **Business Intelligence**: Rich historical data

## Challenges

1. **Query Complexity**: Need projections for queries
2. **Event Versioning**: Schema evolution over time
3. **Storage Growth**: Events accumulate indefinitely
4. **Eventual Consistency**: Read models lag behind writes
5. **Learning Curve**: Different mindset from CRUD

## Event Store Solutions

### Specialized Event Stores:
- **EventStoreDB**: Purpose-built for event sourcing
- **Axon Server**: Event sourcing and CQRS framework
- **Marten**: PostgreSQL-based for .NET

### General-Purpose with Event Sourcing:
- PostgreSQL with JSONB
- MongoDB
- DynamoDB with streams
- Kafka as event store
