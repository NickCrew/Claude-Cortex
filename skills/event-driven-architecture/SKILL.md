---
name: event-driven-architecture
description: Event-driven architecture patterns with event sourcing, CQRS, and message-driven communication. Use when designing distributed systems, microservices communication, or systems requiring eventual consistency and scalability.
---

# Event-Driven Architecture Patterns

Expert guidance for designing, implementing, and operating event-driven systems with proven patterns for event sourcing, CQRS, message brokers, saga coordination, and eventual consistency management.

## When to Use This Skill

- Designing systems with asynchronous, decoupled communication
- Implementing event sourcing and CQRS patterns
- Building systems requiring eventual consistency and high scalability
- Managing distributed transactions across microservices
- Processing real-time event streams and data pipelines
- Implementing publish-subscribe or message queue architectures
- Designing reactive systems with complex event flows

## Core Principles

### 1. Events as First-Class Citizens
Events represent facts that have occurred in the system and are immutable.

**Event Characteristics:**
```
✓ Immutable (cannot be changed after creation)
✓ Past tense naming (OrderCreated, PaymentProcessed)
✓ Self-contained (all necessary data included)
✓ Timestamped and versioned

✗ Commands (CreateOrder vs OrderCreated)
✗ Mutable state changes
✗ Missing context or correlation data
```

### 2. Eventual Consistency
Systems achieve consistency over time rather than immediately.

**Trade-off:**
- Immediate Consistency: Strong guarantees, lower availability/scalability
- Eventual Consistency: Higher availability/scalability, temporary inconsistency

### 3. Loose Coupling
Services communicate through events without direct dependencies.

### 4. Asynchronous Communication
Operations don't block waiting for responses.

### 5. Event-Driven Thinking
Design around what happened (events) rather than what to do (commands).

## Event Fundamentals

### Event Structure

**Well-Designed Event:**
```json
{
  "event_id": "evt_a3f7c9b2d8e1",
  "event_type": "order.created",
  "event_version": "1.0",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "source": "order-service",
  "correlation_id": "corr_x1y2z3a4b5",
  "causation_id": "evt_previous_event",
  "data": {
    "order_id": "ord_123456",
    "customer_id": "cust_789012",
    "total_amount": 99.99,
    "currency": "USD",
    "items": [
      {
        "product_id": "prod_abc",
        "quantity": 2,
        "price": 49.99
      }
    ]
  },
  "metadata": {
    "user_id": "user_xyz",
    "tenant_id": "tenant_001",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Key Fields:**
- `event_id`: Unique identifier for idempotency
- `event_type`: Semantic event name (dot notation)
- `event_version`: Schema version for evolution
- `timestamp`: When event occurred (ISO 8601)
- `correlation_id`: Track related events across services
- `causation_id`: Which event caused this one
- `data`: Business payload
- `metadata`: Contextual information

### Event Types

**1. Domain Events (Business Events):**
```
Business facts within bounded context:
- OrderCreated
- PaymentProcessed
- InventoryReserved
- CustomerRegistered
- ShipmentDelivered
```

**2. Integration Events (Cross-Service):**
```
Events published across service boundaries:
- Order.Created (published to event bus)
- Customer.Updated (for other services)
- Payment.Succeeded (trigger workflows)
```

**3. Change Data Capture (CDC):**
```
Database changes as events:
- Record inserted → RecordCreated event
- Record updated → RecordUpdated event
- Record deleted → RecordDeleted event

Tools: Debezium, Maxwell, AWS DMS
```

## Pattern 1: Event Sourcing

### Definition
Store all state changes as a sequence of immutable events instead of current state.

### Traditional vs Event Sourcing

**Traditional CRUD:**
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

**Event Sourcing:**
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

### Event Sourcing Implementation

**Event Store Interface:**
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

### Benefits

1. **Complete Audit Trail**: Every state change recorded
2. **Temporal Queries**: "What was the state at time T?"
3. **Event Replay**: Rebuild state, fix bugs, test scenarios
4. **New Projections**: Create new read models from existing events
5. **Debugging**: Understand exactly what happened
6. **Business Intelligence**: Rich historical data

### Challenges

1. **Query Complexity**: Need projections for queries
2. **Event Versioning**: Schema evolution over time
3. **Storage Growth**: Events accumulate indefinitely
4. **Eventual Consistency**: Read models lag behind writes
5. **Learning Curve**: Different mindset from CRUD

### Event Store Solutions

**Specialized Event Stores:**
- **EventStoreDB**: Purpose-built for event sourcing
- **Axon Server**: Event sourcing and CQRS framework
- **Marten**: PostgreSQL-based for .NET

**General-Purpose with Event Sourcing:**
- PostgreSQL with JSONB
- MongoDB
- DynamoDB with streams
- Kafka as event store

## Pattern 2: CQRS (Command Query Responsibility Segregation)

### Definition
Separate read (query) and write (command) models for optimal performance.

### Architecture

```
Command Side (Write Model):
  User → Command → Aggregate → Event Store
                              ↓
                         Event Published
                              ↓
Read Side (Query Model):
  Event Handler → Update Read DB → Query API → User
```

### Implementation Example

**Command Side:**
```typescript
// Command (intent to change state)
interface CreateOrderCommand {
  customerId: string;
  items: OrderItem[];
}

// Command Handler (validates and executes)
class CreateOrderCommandHandler {
  constructor(
    private eventStore: EventStore,
    private orderRepository: OrderRepository
  ) {}

  async handle(command: CreateOrderCommand): Promise<string> {
    // Business logic validation
    if (command.items.length === 0) {
      throw new Error('Order must have items');
    }

    // Create aggregate
    const order = Order.create(command.customerId, command.items);

    // Get events from aggregate
    const events = order.getUncommittedEvents();

    // Save to event store
    await this.eventStore.appendEvents(
      `order-${order.id}`,
      events,
      0  // expected version
    );

    return order.id;
  }
}
```

**Read Side (Projection):**
```typescript
// Read Model (optimized for queries)
interface OrderSummary {
  orderId: string;
  customerId: string;
  customerName: string;  // denormalized
  totalAmount: number;
  itemCount: number;
  status: string;
  createdAt: Date;
  updatedAt: Date;
}

// Event Handler (updates read model)
class OrderProjection {
  constructor(private db: Database) {}

  async on(event: OrderCreated): Promise<void> {
    // Fetch customer name (could be cached)
    const customer = await this.getCustomer(event.customerId);

    // Insert into read model
    await this.db.orderSummaries.insert({
      orderId: event.orderId,
      customerId: event.customerId,
      customerName: customer.name,
      totalAmount: event.totalAmount,
      itemCount: event.items.length,
      status: 'PENDING',
      createdAt: event.timestamp,
      updatedAt: event.timestamp
    });
  }

  async on(event: OrderPaid): Promise<void> {
    await this.db.orderSummaries.update(
      { orderId: event.orderId },
      {
        status: 'PAID',
        updatedAt: event.timestamp
      }
    );
  }
}

// Query API (reads from optimized model)
class OrderQueryService {
  async getOrderSummary(orderId: string): Promise<OrderSummary> {
    return await this.db.orderSummaries.findOne({ orderId });
  }

  async getCustomerOrders(customerId: string): Promise<OrderSummary[]> {
    return await this.db.orderSummaries.find({ customerId });
  }
}
```

### Benefits

1. **Optimized Models**: Write for consistency, read for performance
2. **Independent Scaling**: Scale reads and writes separately
3. **Multiple Read Models**: Different views from same events
4. **Simplified Queries**: Denormalized data, no complex joins
5. **Technology Choice**: Different databases for read/write

### When to Use CQRS

**Good Fit:**
- High read:write ratio (10:1 or higher)
- Complex query requirements
- Need for multiple read models
- Performance bottlenecks in traditional model

**Avoid When:**
- Simple CRUD applications
- Strong consistency required immediately
- Team unfamiliar with pattern
- Low complexity domain

## Pattern 3: Message Brokers and Event Buses

### Message Queue (Point-to-Point)

**Use Case**: Work distribution, reliable delivery, load balancing.

```
Producer → Queue → Consumer 1
                → Consumer 2 (competes for messages)
                → Consumer N

Characteristics:
- One message consumed by one consumer
- Load balancing across consumers
- Guaranteed delivery
- Message ordering (within partition/queue)

Examples:
- RabbitMQ queues
- AWS SQS
- Azure Service Bus queues
```

**RabbitMQ Example:**
```typescript
// Producer
const queue = 'order-processing';
channel.sendToQueue(
  queue,
  Buffer.from(JSON.stringify(orderEvent)),
  { persistent: true }  // survive broker restart
);

// Consumer
channel.consume(queue, async (msg) => {
  const event = JSON.parse(msg.content.toString());

  try {
    await processOrder(event);
    channel.ack(msg);  // acknowledge success
  } catch (error) {
    channel.nack(msg, false, true);  // requeue on failure
  }
});
```

### Publish-Subscribe (Pub/Sub)

**Use Case**: Broadcasting events to multiple interested services.

```
Publisher → Topic → Subscriber 1 (all messages)
                  → Subscriber 2 (all messages)
                  → Subscriber N (all messages)

Characteristics:
- One message received by all subscribers
- Decoupled publishers and subscribers
- Dynamic subscription
- Topic-based or content-based routing

Examples:
- Apache Kafka topics
- AWS SNS
- Google Cloud Pub/Sub
- Azure Service Bus topics
```

**Kafka Example:**
```typescript
// Producer
await producer.send({
  topic: 'orders',
  messages: [
    {
      key: orderEvent.orderId,  // partition key
      value: JSON.stringify(orderEvent),
      headers: {
        'event-type': 'OrderCreated',
        'correlation-id': correlationId
      }
    }
  ]
});

// Consumer Group (load balanced)
const consumer = kafka.consumer({ groupId: 'order-analytics' });
await consumer.subscribe({ topic: 'orders' });

await consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    const event = JSON.parse(message.value.toString());
    await updateAnalytics(event);
  }
});
```

### Message Broker Comparison

**RabbitMQ:**
```
Strengths:
- Rich routing (exchanges, bindings)
- Message acknowledgment and requeue
- Priority queues
- Dead letter exchanges

Best for:
- Task distribution
- Complex routing patterns
- Guaranteed delivery
- Lower throughput needs (<100K msg/sec)
```

**Apache Kafka:**
```
Strengths:
- High throughput (millions msg/sec)
- Event log persistence
- Replay capability
- Partition-based parallelism

Best for:
- Event streaming
- High-volume systems
- Event sourcing backend
- Log aggregation
```

**AWS SQS/SNS:**
```
Strengths:
- Fully managed
- Infinite scale
- Simple integration
- Pay per use

Best for:
- AWS-native architectures
- Variable load
- Simple pub/sub or queuing
- Minimal ops overhead
```

## Pattern 4: Saga Pattern (Distributed Transactions)

### Definition
Manage data consistency across services using a sequence of local transactions coordinated by events or orchestration.

### Orchestration-Based Saga

**Central coordinator manages transaction flow.**

```typescript
// Saga Orchestrator
class OrderSaga {
  async execute(createOrderCommand: CreateOrderCommand): Promise<void> {
    const sagaId = generateId();
    const state = new SagaState(sagaId);

    try {
      // Step 1: Create order
      state.orderId = await this.orderService.createOrder(
        createOrderCommand
      );
      state.mark('ORDER_CREATED');

      // Step 2: Reserve inventory
      await this.inventoryService.reserveInventory({
        orderId: state.orderId,
        items: createOrderCommand.items
      });
      state.mark('INVENTORY_RESERVED');

      // Step 3: Process payment
      await this.paymentService.processPayment({
        orderId: state.orderId,
        amount: createOrderCommand.totalAmount
      });
      state.mark('PAYMENT_PROCESSED');

      // Step 4: Confirm order
      await this.orderService.confirmOrder(state.orderId);
      state.mark('COMPLETED');

    } catch (error) {
      // Compensate in reverse order
      await this.compensate(state, error);
      throw new SagaFailedException(sagaId, error);
    }
  }

  private async compensate(state: SagaState, error: Error): Promise<void> {
    if (state.has('PAYMENT_PROCESSED')) {
      await this.paymentService.refundPayment(state.orderId);
    }

    if (state.has('INVENTORY_RESERVED')) {
      await this.inventoryService.releaseInventory(state.orderId);
    }

    if (state.has('ORDER_CREATED')) {
      await this.orderService.cancelOrder(state.orderId);
    }
  }
}
```

**Benefits:**
- Centralized logic, easy to understand
- Explicit control flow
- Simple error handling

**Drawbacks:**
- Single point of failure
- Tight coupling to orchestrator
- Can become complex with many steps

### Choreography-Based Saga

**Services coordinate via events without central controller.**

```typescript
// Order Service
class OrderService {
  async createOrder(command: CreateOrderCommand): Promise<void> {
    const order = new Order(command);
    await this.repository.save(order);

    // Publish event
    await this.eventBus.publish(new OrderCreated({
      orderId: order.id,
      customerId: order.customerId,
      items: order.items,
      totalAmount: order.totalAmount
    }));
  }
}

// Inventory Service (reacts to OrderCreated)
class InventoryService {
  @EventHandler(OrderCreated)
  async onOrderCreated(event: OrderCreated): Promise<void> {
    try {
      await this.reserveStock(event.items);

      // Publish success event
      await this.eventBus.publish(new InventoryReserved({
        orderId: event.orderId,
        items: event.items
      }));
    } catch (error) {
      // Publish failure event (triggers compensation)
      await this.eventBus.publish(new InventoryReservationFailed({
        orderId: event.orderId,
        reason: error.message
      }));
    }
  }

  // Compensation handler
  @EventHandler(OrderCancelled)
  async onOrderCancelled(event: OrderCancelled): Promise<void> {
    await this.releaseStock(event.orderId);
  }
}

// Payment Service (reacts to InventoryReserved)
class PaymentService {
  @EventHandler(InventoryReserved)
  async onInventoryReserved(event: InventoryReserved): Promise<void> {
    try {
      await this.processPayment(event.orderId);

      await this.eventBus.publish(new PaymentProcessed({
        orderId: event.orderId
      }));
    } catch (error) {
      await this.eventBus.publish(new PaymentFailed({
        orderId: event.orderId,
        reason: error.message
      }));
    }
  }

  // Compensation
  @EventHandler(OrderCancelled)
  async onOrderCancelled(event: OrderCancelled): Promise<void> {
    await this.refundPayment(event.orderId);
  }
}
```

**Event Flow:**
```
Success Flow:
OrderCreated → InventoryReserved → PaymentProcessed → OrderConfirmed

Failure Flow (Payment fails):
OrderCreated → InventoryReserved → PaymentFailed → OrderCancelled
  → InventoryReleased (compensation)
```

**Benefits:**
- Decentralized, no single point of failure
- Services remain autonomous
- Natural event-driven flow

**Drawbacks:**
- Implicit control flow, harder to understand
- Debugging complexity
- Risk of circular dependencies

### Saga Design Patterns

**1. Compensating Transactions:**
```
Action: ReserveInventory
Compensation: ReleaseInventory

Action: ProcessPayment
Compensation: RefundPayment

Action: CreateShipment
Compensation: CancelShipment
```

**2. Semantic Lock:**
```
Mark resource as "pending" to prevent concurrent access:
- Order status: PENDING_PAYMENT
- Inventory: RESERVED (not available for other orders)
- Payment: AUTHORIZED (not captured yet)
```

**3. Saga Log:**
```
Persist saga state for recovery:
- Current step
- Completed steps
- Compensation state
- Allows restart after failure
```

## Pattern 5: Event Choreography vs Orchestration

### Event Choreography

**Decentralized coordination through events.**

```
Service A → Event 1 → Service B → Event 2 → Service C
                    ↓
                  Service D
```

**When to Use:**
- Simple workflows (2-4 steps)
- Services naturally reactive
- High autonomy desired
- Event-driven culture

**Example: User Registration**
```
1. Auth Service: UserRegistered event
   → Email Service: sends welcome email
   → Analytics Service: tracks signup
   → CRM Service: creates contact

Each service reacts independently.
```

### Event Orchestration

**Centralized coordinator manages flow.**

```
Orchestrator → Service A
           → Service B
           → Service C

Orchestrator controls sequence and dependencies.
```

**When to Use:**
- Complex workflows (5+ steps)
- Sequential dependencies
- Business logic in workflow
- Need visibility/monitoring

**Example: Order Processing**
```
OrderOrchestrator:
1. Validate order
2. Reserve inventory (wait)
3. Process payment (wait)
4. Create shipment (wait)
5. Confirm order

Clear sequence, centralized control.
```

### Hybrid Approach

Combine both for complex systems:
```
High-level: Orchestration (order saga)
  Step 1: Process Order (choreography within)
    → Validate
    → Price calculation
    → Tax calculation
  Step 2: Fulfill Order (choreography within)
    → Pick items
    → Pack
    → Label
```

## Eventual Consistency Patterns

### Pattern: Read-Your-Writes Consistency

**Problem**: User makes change, immediately queries, sees stale data.

**Solutions:**

**1. Synchronous Projection Update:**
```typescript
async createOrder(command: CreateOrderCommand): Promise<OrderSummary> {
  // Write to event store
  await this.eventStore.append(orderCreatedEvent);

  // Immediately update read model (synchronously)
  const summary = await this.projection.apply(orderCreatedEvent);

  return summary;  // User sees their change
}
```

**2. Version-Based Consistency:**
```typescript
// Return version with write
const result = await createOrder(command);
// version: 5

// Query with minimum version
const order = await queryOrder(orderId, minVersion: 5);
// Wait until read model catches up to version 5
```

**3. Client-Side Optimistic Update:**
```typescript
// Client immediately shows optimistic state
this.orders.push(newOrder);

// Background: wait for confirmation
await waitForEvent('OrderCreated', newOrder.id);
```

### Pattern: Compensating Actions

When eventual consistency fails, undo changes:

```typescript
// Original action
await inventoryService.reserveStock(orderId, items);

// Later: payment fails, compensate
await inventoryService.releaseStock(orderId);

// Idempotent: safe to call multiple times
```

### Pattern: Conflict Resolution

**Last-Write-Wins (LWW):**
```typescript
if (event1.timestamp > event2.timestamp) {
  apply(event1);
} else {
  apply(event2);
}
```

**Custom Business Logic:**
```typescript
// Merge inventory updates
const finalQuantity = Math.max(
  update1.quantity,
  update2.quantity
);
```

**CRDTs (Conflict-free Replicated Data Types):**
```typescript
// Automatic conflict resolution
const counter = new PNCounter();
counter.increment(5);  // replica 1
counter.increment(3);  // replica 2
// Automatically merges to 8
```

## Best Practices Summary

### Event Design
1. **Immutable Events**: Never modify published events
2. **Past Tense**: Name events for what happened (OrderCreated, not CreateOrder)
3. **Rich Events**: Include all data consumers need
4. **Versioning**: Plan for schema evolution from day one
5. **Correlation**: Always include correlation and causation IDs

### Architecture
1. **Idempotency**: All event handlers must be idempotent
2. **At-Least-Once**: Design for duplicate event delivery
3. **Ordering**: Don't assume global ordering unless guaranteed
4. **Partitioning**: Use partition keys for ordered processing
5. **Dead Letters**: Handle poison messages with DLQ

### Implementation
1. **Event Store First**: Append to event store before publishing
2. **Transactional Outbox**: Ensure events published exactly once
3. **Snapshots**: Use snapshots for long event streams
4. **Projections**: Keep read models eventually consistent
5. **Monitoring**: Track event lag, processing time, failures

### Operations
1. **Event Replay**: Build capability to replay events
2. **Schema Registry**: Centralize event schema management
3. **Testing**: Test event handlers in isolation
4. **Debugging**: Use correlation IDs for distributed tracing
5. **Versioning**: Support multiple event versions simultaneously

### Scaling
1. **Partitioning**: Partition by aggregate ID for parallelism
2. **Consumer Groups**: Scale consumers horizontally
3. **Backpressure**: Handle slow consumers gracefully
4. **Retention**: Define event retention policies
5. **Archival**: Archive old events to cold storage

## Resources

- **Books**: "Designing Event-Driven Systems" (Stopford), "Versioning in an Event Sourced System" (Young)
- **Sites**: eventuate.io, event-driven.io, Martin Fowler's event sourcing articles
- **Tools**: Kafka, EventStoreDB, RabbitMQ, Axon Framework, MassTransit
- **Patterns**: Event Sourcing, CQRS, Saga, Outbox, CDC, Event Streaming
