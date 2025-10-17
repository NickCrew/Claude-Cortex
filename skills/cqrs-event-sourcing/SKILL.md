---
name: cqrs-event-sourcing
description: CQRS and Event Sourcing patterns for scalable, auditable systems with separated read/write models. Use when building audit-required systems, implementing temporal queries, or designing high-scale applications with complex domain logic.
---

# CQRS and Event Sourcing Patterns

Expert guidance for implementing Command Query Responsibility Segregation (CQRS) and Event Sourcing patterns to build scalable, auditable systems with complete historical tracking and optimized read/write models.

## When to Use This Skill

- Building systems requiring complete audit trails and compliance
- Implementing temporal queries ("show me the state at time T")
- Designing high-scale applications with complex domain logic
- Creating systems with significantly different read and write patterns
- Building event-driven architectures with historical replay capability
- Implementing systems requiring multiple read model projections
- Designing applications where understanding "what happened" is critical
- Building collaborative systems with conflict resolution needs

## Core Principles

### 1. Command Query Separation
Separate operations that change state (commands) from operations that read state (queries).

**Foundation:**
```
Commands (Write):
✓ Express intent (CreateOrder, UpdatePrice)
✓ Can be rejected (validation failures)
✓ Return success/failure, not data
✓ Change system state

Queries (Read):
✓ Return data, never change state
✓ Can be cached and optimized
✓ Multiple models for different needs
✓ Eventually consistent with writes
```

### 2. Events as Source of Truth
Store state changes as immutable events rather than current state snapshots.

**Paradigm Shift:**
```
Traditional: Store what IS
Event Sourcing: Store what HAPPENED

Traditional: UPDATE users SET email = 'new@email.com'
Event Sourcing: APPEND UserEmailChanged event

Result: Complete history, temporal queries, audit trail
```

### 3. Eventual Consistency
Accept temporary inconsistency between write and read models for scalability.

**Trade-off:**
- Writes: Optimized for correctness and business rules
- Reads: Optimized for query performance and user experience
- Synchronization: Asynchronous through event handlers

### 4. Domain-Driven Design Integration
CQRS and Event Sourcing naturally align with DDD concepts.

**Alignment:**
- Aggregates enforce business invariants
- Events represent domain facts
- Commands express domain operations
- Bounded contexts define consistency boundaries

## CQRS Pattern Deep Dive

### Basic CQRS Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                         │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
     ┌───────▼────────┐          ┌───────▼────────┐
     │   COMMAND API  │          │   QUERY API    │
     └───────┬────────┘          └───────┬────────┘
             │                            │
     ┌───────▼────────┐          ┌───────▼────────┐
     │ Command Handler│          │ Query Handler  │
     └───────┬────────┘          └───────┬────────┘
             │                            │
     ┌───────▼────────┐          ┌───────▼────────┐
     │  Write Model   │──Events──▶│  Read Model(s) │
     │  (Aggregates)  │          │  (Projections) │
     └────────────────┘          └────────────────┘
```

### Command Side Implementation

**Command Structure:**
```typescript
// Command represents intent to change state
interface CreateOrderCommand {
  readonly commandId: string;         // Idempotency key
  readonly timestamp: Date;
  readonly userId: string;            // Authorization context
  readonly customerId: string;
  readonly items: OrderItem[];
  readonly shippingAddress: Address;
}

interface OrderItem {
  readonly productId: string;
  readonly quantity: number;
  readonly priceAtOrder: Money;       // Capture price snapshot
}
```

**Command Handler:**
```typescript
class CreateOrderCommandHandler {
  constructor(
    private readonly orderRepository: OrderRepository,
    private readonly inventoryService: InventoryService,
    private readonly pricingService: PricingService
  ) {}

  async handle(command: CreateOrderCommand): Promise<Result<string>> {
    // 1. Validation
    if (command.items.length === 0) {
      return Result.failure('Order must contain items');
    }

    // 2. Business rule verification
    const availability = await this.inventoryService.checkAvailability(
      command.items
    );

    if (!availability.allAvailable) {
      return Result.failure(
        `Insufficient stock for items: ${availability.unavailableItems}`
      );
    }

    // 3. Create aggregate and apply domain logic
    const order = Order.create({
      customerId: command.customerId,
      items: command.items,
      shippingAddress: command.shippingAddress
    });

    // 4. Persist aggregate (saves events)
    await this.orderRepository.save(order);

    // 5. Return aggregate ID
    return Result.success(order.id);
  }
}
```

**Aggregate Root with Event Sourcing:**
```typescript
class Order extends AggregateRoot {
  private id: string;
  private customerId: string;
  private items: OrderItem[] = [];
  private status: OrderStatus;
  private totalAmount: Money;
  private version: number = 0;

  // Factory method for creation
  static create(data: CreateOrderData): Order {
    const order = new Order();
    const event = new OrderCreatedEvent({
      orderId: generateId(),
      customerId: data.customerId,
      items: data.items,
      shippingAddress: data.shippingAddress,
      totalAmount: calculateTotal(data.items),
      timestamp: new Date()
    });

    order.apply(event);
    order.addUncommittedEvent(event);
    return order;
  }

  // Reconstruct from event history
  static fromEvents(events: OrderEvent[]): Order {
    const order = new Order();
    for (const event of events) {
      order.apply(event);
      order.version++;
    }
    return order;
  }

  // Command methods create events
  markAsPaid(paymentId: string): void {
    if (this.status !== 'PENDING') {
      throw new InvalidOperationError(
        `Cannot mark order as paid. Current status: ${this.status}`
      );
    }

    const event = new OrderPaidEvent({
      orderId: this.id,
      paymentId,
      timestamp: new Date()
    });

    this.apply(event);
    this.addUncommittedEvent(event);
  }

  // Event application mutates state
  private apply(event: OrderEvent): void {
    switch (event.constructor) {
      case OrderCreatedEvent:
        this.applyOrderCreated(event as OrderCreatedEvent);
        break;
      case OrderPaidEvent:
        this.applyOrderPaid(event as OrderPaidEvent);
        break;
      case OrderShippedEvent:
        this.applyOrderShipped(event as OrderShippedEvent);
        break;
      case OrderCancelledEvent:
        this.applyOrderCancelled(event as OrderCancelledEvent);
        break;
    }
  }

  private applyOrderCreated(event: OrderCreatedEvent): void {
    this.id = event.orderId;
    this.customerId = event.customerId;
    this.items = event.items;
    this.totalAmount = event.totalAmount;
    this.status = 'PENDING';
  }

  private applyOrderPaid(event: OrderPaidEvent): void {
    this.status = 'PAID';
  }

  private applyOrderShipped(event: OrderShippedEvent): void {
    this.status = 'SHIPPED';
  }

  private applyOrderCancelled(event: OrderCancelledEvent): void {
    this.status = 'CANCELLED';
  }
}
```

### Query Side Implementation

**Read Model (Projection):**
```typescript
// Optimized for queries, denormalized
interface OrderListItemReadModel {
  orderId: string;
  orderNumber: string;              // Human-readable
  customerId: string;
  customerName: string;             // Denormalized
  customerEmail: string;            // Denormalized
  totalAmount: number;
  currency: string;
  itemCount: number;
  status: string;
  createdAt: Date;
  updatedAt: Date;
  lastEventVersion: number;         // Idempotency tracking
}

// Different read model for different view
interface OrderDetailsReadModel {
  orderId: string;
  orderNumber: string;
  customer: {
    id: string;
    name: string;
    email: string;
    phone: string;
  };
  items: Array<{
    productId: string;
    productName: string;            // Denormalized
    productImageUrl: string;        // Denormalized
    quantity: number;
    unitPrice: number;
    totalPrice: number;
  }>;
  shippingAddress: Address;
  billingAddress: Address;
  payment: {
    method: string;
    status: string;
    transactionId: string;
  };
  shipping: {
    method: string;
    trackingNumber: string;
    estimatedDelivery: Date;
  };
  timeline: Array<{
    event: string;
    timestamp: Date;
    description: string;
  }>;
  totalAmount: number;
  currency: string;
  status: string;
  createdAt: Date;
  updatedAt: Date;
}
```

**Projection Handler:**
```typescript
class OrderProjectionHandler {
  constructor(
    private readonly readDb: ReadDatabase,
    private readonly customerService: CustomerService
  ) {}

  // Handle OrderCreated event
  async on(event: OrderCreatedEvent): Promise<void> {
    // Fetch additional data for denormalization
    const customer = await this.customerService.getCustomer(
      event.customerId
    );

    // Create list item projection
    await this.readDb.orderListItems.insert({
      orderId: event.orderId,
      orderNumber: this.generateOrderNumber(event.orderId),
      customerId: event.customerId,
      customerName: customer.name,
      customerEmail: customer.email,
      totalAmount: event.totalAmount.amount,
      currency: event.totalAmount.currency,
      itemCount: event.items.length,
      status: 'PENDING',
      createdAt: event.timestamp,
      updatedAt: event.timestamp,
      lastEventVersion: 1
    });

    // Create detailed projection
    await this.readDb.orderDetails.insert({
      orderId: event.orderId,
      orderNumber: this.generateOrderNumber(event.orderId),
      customer: {
        id: customer.id,
        name: customer.name,
        email: customer.email,
        phone: customer.phone
      },
      items: await this.enrichOrderItems(event.items),
      shippingAddress: event.shippingAddress,
      totalAmount: event.totalAmount.amount,
      currency: event.totalAmount.currency,
      status: 'PENDING',
      timeline: [{
        event: 'OrderCreated',
        timestamp: event.timestamp,
        description: 'Order created'
      }],
      createdAt: event.timestamp,
      updatedAt: event.timestamp
    });
  }

  // Handle OrderPaid event
  async on(event: OrderPaidEvent): Promise<void> {
    // Update list item (minimal)
    await this.readDb.orderListItems.update(
      { orderId: event.orderId },
      {
        status: 'PAID',
        updatedAt: event.timestamp,
        lastEventVersion: event.version
      }
    );

    // Update detailed view (add to timeline)
    await this.readDb.orderDetails.update(
      { orderId: event.orderId },
      {
        status: 'PAID',
        payment: {
          status: 'COMPLETED',
          transactionId: event.paymentId
        },
        $push: {
          timeline: {
            event: 'OrderPaid',
            timestamp: event.timestamp,
            description: 'Payment processed successfully'
          }
        },
        updatedAt: event.timestamp
      }
    );
  }

  // Idempotent event handling
  private async isEventProcessed(
    orderId: string,
    eventVersion: number
  ): Promise<boolean> {
    const order = await this.readDb.orderListItems.findOne({ orderId });
    return order && order.lastEventVersion >= eventVersion;
  }

  private async enrichOrderItems(
    items: OrderItem[]
  ): Promise<EnrichedOrderItem[]> {
    // Fetch product details for denormalization
    const productIds = items.map(i => i.productId);
    const products = await this.productService.getProducts(productIds);

    return items.map(item => {
      const product = products.find(p => p.id === item.productId);
      return {
        productId: item.productId,
        productName: product.name,
        productImageUrl: product.primaryImageUrl,
        quantity: item.quantity,
        unitPrice: item.priceAtOrder.amount,
        totalPrice: item.priceAtOrder.amount * item.quantity
      };
    });
  }
}
```

**Query Service:**
```typescript
class OrderQueryService {
  constructor(private readonly readDb: ReadDatabase) {}

  // Simple queries against optimized read models
  async getOrderList(
    customerId: string,
    options: PaginationOptions
  ): Promise<PagedResult<OrderListItemReadModel>> {
    return await this.readDb.orderListItems.find(
      { customerId },
      {
        sort: { createdAt: -1 },
        skip: options.offset,
        limit: options.limit
      }
    );
  }

  async getOrderDetails(orderId: string): Promise<OrderDetailsReadModel> {
    return await this.readDb.orderDetails.findOne({ orderId });
  }

  async searchOrders(
    criteria: OrderSearchCriteria
  ): Promise<OrderListItemReadModel[]> {
    const query: any = {};

    if (criteria.status) {
      query.status = criteria.status;
    }

    if (criteria.customerEmail) {
      query.customerEmail = new RegExp(criteria.customerEmail, 'i');
    }

    if (criteria.minAmount) {
      query.totalAmount = { $gte: criteria.minAmount };
    }

    if (criteria.dateRange) {
      query.createdAt = {
        $gte: criteria.dateRange.start,
        $lte: criteria.dateRange.end
      };
    }

    return await this.readDb.orderListItems.find(query);
  }

  // Analytics query (separate projection)
  async getOrderStatistics(
    customerId: string
  ): Promise<OrderStatistics> {
    return await this.readDb.orderStatistics.findOne({ customerId });
  }
}
```

## Event Sourcing Deep Dive

### Event Store Design

**Event Store Schema:**
```sql
-- PostgreSQL example
CREATE TABLE events (
  event_id UUID PRIMARY KEY,
  stream_id VARCHAR(255) NOT NULL,      -- Aggregate ID
  stream_type VARCHAR(100) NOT NULL,    -- Aggregate type
  event_type VARCHAR(100) NOT NULL,
  event_data JSONB NOT NULL,
  event_metadata JSONB,
  event_version INTEGER NOT NULL,       -- Aggregate version
  global_position BIGSERIAL NOT NULL,   -- Global ordering
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  correlation_id UUID,
  causation_id UUID,

  CONSTRAINT unique_stream_version
    UNIQUE (stream_id, event_version)
);

-- Indexes for performance
CREATE INDEX idx_events_stream ON events(stream_id, event_version);
CREATE INDEX idx_events_global_position ON events(global_position);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_correlation ON events(correlation_id);

-- Snapshots for performance optimization
CREATE TABLE snapshots (
  snapshot_id UUID PRIMARY KEY,
  stream_id VARCHAR(255) NOT NULL,
  stream_type VARCHAR(100) NOT NULL,
  aggregate_data JSONB NOT NULL,
  version INTEGER NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT unique_stream_version_snapshot
    UNIQUE (stream_id, version)
);

CREATE INDEX idx_snapshots_stream ON snapshots(stream_id, version DESC);
```

**Event Store Implementation:**
```typescript
class PostgresEventStore implements EventStore {
  constructor(private readonly pool: Pool) {}

  async appendEvents(
    streamId: string,
    streamType: string,
    events: DomainEvent[],
    expectedVersion: number
  ): Promise<void> {
    const client = await this.pool.connect();

    try {
      await client.query('BEGIN');

      for (let i = 0; i < events.length; i++) {
        const event = events[i];
        const version = expectedVersion + i + 1;

        await client.query(
          `INSERT INTO events (
            event_id, stream_id, stream_type, event_type,
            event_data, event_metadata, event_version,
            timestamp, correlation_id, causation_id
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
          [
            event.eventId,
            streamId,
            streamType,
            event.eventType,
            JSON.stringify(event.data),
            JSON.stringify(event.metadata),
            version,
            event.timestamp,
            event.correlationId,
            event.causationId
          ]
        );
      }

      await client.query('COMMIT');
    } catch (error) {
      await client.query('ROLLBACK');

      // Optimistic concurrency check
      if (error.code === '23505') { // Unique constraint violation
        throw new ConcurrencyError(
          `Stream ${streamId} was modified by another process`
        );
      }

      throw error;
    } finally {
      client.release();
    }
  }

  async readEvents(
    streamId: string,
    fromVersion: number = 0
  ): Promise<DomainEvent[]> {
    const result = await this.pool.query(
      `SELECT event_id, event_type, event_data, event_metadata,
              event_version, timestamp, correlation_id, causation_id
       FROM events
       WHERE stream_id = $1 AND event_version > $2
       ORDER BY event_version ASC`,
      [streamId, fromVersion]
    );

    return result.rows.map(row => this.deserializeEvent(row));
  }

  async readAllEvents(
    fromPosition: number = 0,
    maxCount: number = 1000
  ): Promise<DomainEvent[]> {
    const result = await this.pool.query(
      `SELECT stream_id, stream_type, event_id, event_type,
              event_data, event_metadata, event_version,
              global_position, timestamp, correlation_id, causation_id
       FROM events
       WHERE global_position > $1
       ORDER BY global_position ASC
       LIMIT $2`,
      [fromPosition, maxCount]
    );

    return result.rows.map(row => this.deserializeEvent(row));
  }

  async getStreamVersion(streamId: string): Promise<number> {
    const result = await this.pool.query(
      `SELECT MAX(event_version) as version
       FROM events
       WHERE stream_id = $1`,
      [streamId]
    );

    return result.rows[0]?.version || 0;
  }

  private deserializeEvent(row: any): DomainEvent {
    return {
      eventId: row.event_id,
      streamId: row.stream_id,
      streamType: row.stream_type,
      eventType: row.event_type,
      data: row.event_data,
      metadata: row.event_metadata,
      version: row.event_version,
      globalPosition: row.global_position,
      timestamp: row.timestamp,
      correlationId: row.correlation_id,
      causationId: row.causation_id
    };
  }
}
```

### Snapshot Pattern

**Snapshot Strategy:**
```typescript
class SnapshotStrategy {
  // Snapshot every N events
  shouldCreateSnapshot(version: number): boolean {
    return version % 50 === 0;
  }

  async saveSnapshot(
    streamId: string,
    streamType: string,
    aggregate: AggregateRoot,
    version: number
  ): Promise<void> {
    await this.pool.query(
      `INSERT INTO snapshots (
        snapshot_id, stream_id, stream_type,
        aggregate_data, version, timestamp
      ) VALUES ($1, $2, $3, $4, $5, NOW())`,
      [
        generateId(),
        streamId,
        streamType,
        JSON.stringify(aggregate.getState()),
        version
      ]
    );
  }

  async loadSnapshot(
    streamId: string
  ): Promise<{ snapshot: any; version: number } | null> {
    const result = await this.pool.query(
      `SELECT aggregate_data, version
       FROM snapshots
       WHERE stream_id = $1
       ORDER BY version DESC
       LIMIT 1`,
      [streamId]
    );

    if (result.rows.length === 0) {
      return null;
    }

    return {
      snapshot: result.rows[0].aggregate_data,
      version: result.rows[0].version
    };
  }
}

// Repository with snapshot support
class SnapshotAwareRepository {
  async load(streamId: string): Promise<Order> {
    // Try to load from snapshot
    const snapshotData = await this.snapshotStrategy.loadSnapshot(streamId);

    let order: Order;
    let fromVersion: number;

    if (snapshotData) {
      // Reconstruct from snapshot
      order = Order.fromSnapshot(snapshotData.snapshot);
      fromVersion = snapshotData.version;
    } else {
      // Start fresh
      order = new Order();
      fromVersion = 0;
    }

    // Load events since snapshot
    const events = await this.eventStore.readEvents(streamId, fromVersion);

    // Apply remaining events
    for (const event of events) {
      order.apply(event);
    }

    return order;
  }

  async save(order: Order): Promise<void> {
    const streamId = order.getId();
    const uncommittedEvents = order.getUncommittedEvents();
    const expectedVersion = order.getVersion() - uncommittedEvents.length;

    // Append events
    await this.eventStore.appendEvents(
      streamId,
      'Order',
      uncommittedEvents,
      expectedVersion
    );

    // Check if snapshot needed
    if (this.snapshotStrategy.shouldCreateSnapshot(order.getVersion())) {
      await this.snapshotStrategy.saveSnapshot(
        streamId,
        'Order',
        order,
        order.getVersion()
      );
    }

    order.markEventsAsCommitted();
  }
}
```

### Temporal Queries

**Point-in-Time Reconstruction:**
```typescript
class TemporalQueryService {
  async getAggregateAtTime(
    streamId: string,
    asOfDate: Date
  ): Promise<Order> {
    // Load events up to specified time
    const events = await this.pool.query(
      `SELECT event_id, event_type, event_data, event_metadata,
              event_version, timestamp
       FROM events
       WHERE stream_id = $1 AND timestamp <= $2
       ORDER BY event_version ASC`,
      [streamId, asOfDate]
    );

    // Reconstruct aggregate
    const order = new Order();
    for (const row of events.rows) {
      const event = this.deserializeEvent(row);
      order.apply(event);
    }

    return order;
  }

  async getOrderStatusHistory(
    orderId: string
  ): Promise<OrderStatusHistoryItem[]> {
    const events = await this.eventStore.readEvents(orderId);

    const history: OrderStatusHistoryItem[] = [];
    let currentStatus = 'PENDING';

    for (const event of events) {
      switch (event.eventType) {
        case 'OrderCreated':
          history.push({
            status: 'PENDING',
            timestamp: event.timestamp,
            version: event.version
          });
          break;

        case 'OrderPaid':
          currentStatus = 'PAID';
          history.push({
            status: 'PAID',
            timestamp: event.timestamp,
            version: event.version
          });
          break;

        case 'OrderShipped':
          currentStatus = 'SHIPPED';
          history.push({
            status: 'SHIPPED',
            timestamp: event.timestamp,
            version: event.version
          });
          break;

        case 'OrderCancelled':
          currentStatus = 'CANCELLED';
          history.push({
            status: 'CANCELLED',
            timestamp: event.timestamp,
            version: event.version
          });
          break;
      }
    }

    return history;
  }

  async getAggregateAtVersion(
    streamId: string,
    version: number
  ): Promise<Order> {
    const events = await this.pool.query(
      `SELECT event_id, event_type, event_data, event_metadata,
              event_version, timestamp
       FROM events
       WHERE stream_id = $1 AND event_version <= $2
       ORDER BY event_version ASC`,
      [streamId, version]
    );

    const order = new Order();
    for (const row of events.rows) {
      const event = this.deserializeEvent(row);
      order.apply(event);
    }

    return order;
  }
}
```

## Event Store Technology Patterns

### EventStoreDB Pattern

**Using EventStoreDB (specialized event store):**
```typescript
import { EventStoreDBClient, jsonEvent } from '@eventstore/db-client';

class EventStoreDBAdapter {
  private client: EventStoreDBClient;

  constructor(connectionString: string) {
    this.client = EventStoreDBClient.connectionString(connectionString);
  }

  async appendToStream(
    streamName: string,
    events: DomainEvent[],
    expectedRevision: number | 'any' | 'no_stream'
  ): Promise<void> {
    const eventData = events.map(event =>
      jsonEvent({
        type: event.eventType,
        data: event.data,
        metadata: {
          correlationId: event.correlationId,
          causationId: event.causationId,
          timestamp: event.timestamp.toISOString()
        }
      })
    );

    await this.client.appendToStream(
      streamName,
      eventData,
      { expectedRevision }
    );
  }

  async readStream(streamName: string): Promise<DomainEvent[]> {
    const events = this.client.readStream(streamName);
    const result: DomainEvent[] = [];

    for await (const resolvedEvent of events) {
      result.push({
        eventId: resolvedEvent.event!.id,
        eventType: resolvedEvent.event!.type,
        data: resolvedEvent.event!.data,
        metadata: resolvedEvent.event!.metadata,
        version: Number(resolvedEvent.event!.revision),
        timestamp: resolvedEvent.event!.created
      });
    }

    return result;
  }

  async subscribeToAll(
    handler: (event: DomainEvent) => Promise<void>
  ): Promise<void> {
    const subscription = this.client.subscribeToAll();

    for await (const resolvedEvent of subscription) {
      if (resolvedEvent.event) {
        await handler({
          eventId: resolvedEvent.event.id,
          eventType: resolvedEvent.event.type,
          data: resolvedEvent.event.data,
          metadata: resolvedEvent.event.metadata,
          version: Number(resolvedEvent.event.revision),
          globalPosition: Number(resolvedEvent.event.position.commit),
          timestamp: resolvedEvent.event.created
        });
      }
    }
  }
}
```

### Axon Framework Pattern

**Using Axon Framework (Java/Spring):**
```java
// Aggregate
@Aggregate
public class OrderAggregate {
    @AggregateIdentifier
    private String orderId;
    private OrderStatus status;
    private List<OrderItem> items;

    // Command handler
    @CommandHandler
    public OrderAggregate(CreateOrderCommand command) {
        AggregateLifecycle.apply(new OrderCreatedEvent(
            command.getOrderId(),
            command.getCustomerId(),
            command.getItems(),
            command.getTotalAmount()
        ));
    }

    @CommandHandler
    public void handle(PayOrderCommand command) {
        if (status != OrderStatus.PENDING) {
            throw new IllegalStateException("Order cannot be paid");
        }

        AggregateLifecycle.apply(new OrderPaidEvent(
            orderId,
            command.getPaymentId()
        ));
    }

    // Event sourcing handlers
    @EventSourcingHandler
    public void on(OrderCreatedEvent event) {
        this.orderId = event.getOrderId();
        this.status = OrderStatus.PENDING;
        this.items = event.getItems();
    }

    @EventSourcingHandler
    public void on(OrderPaidEvent event) {
        this.status = OrderStatus.PAID;
    }
}

// Projection
@ProcessingGroup("order-projection")
public class OrderProjection {
    @EventHandler
    public void on(OrderCreatedEvent event) {
        OrderListItemEntity entity = new OrderListItemEntity();
        entity.setOrderId(event.getOrderId());
        entity.setCustomerId(event.getCustomerId());
        entity.setStatus("PENDING");
        entity.setTotalAmount(event.getTotalAmount());

        repository.save(entity);
    }

    @EventHandler
    public void on(OrderPaidEvent event) {
        OrderListItemEntity entity = repository.findById(event.getOrderId())
            .orElseThrow();
        entity.setStatus("PAID");
        repository.save(entity);
    }
}
```

## Consistency Patterns

### Immediate Consistency Within Aggregate

**Strong consistency boundary:**
```typescript
class Order extends AggregateRoot {
  private items: OrderItem[] = [];
  private totalAmount: Money;

  addItem(item: OrderItem): void {
    // Business rule: Max 10 items per order
    if (this.items.length >= 10) {
      throw new BusinessRuleViolation('Cannot add more than 10 items');
    }

    // Business rule: Cannot modify after payment
    if (this.status !== 'PENDING') {
      throw new InvalidOperationError('Cannot modify paid order');
    }

    const event = new ItemAddedToOrderEvent({
      orderId: this.id,
      item: item,
      timestamp: new Date()
    });

    this.apply(event);
    this.addUncommittedEvent(event);
  }

  // Aggregate ensures consistency of invariants
  private applyItemAddedToOrder(event: ItemAddedToOrderEvent): void {
    this.items.push(event.item);
    this.totalAmount = this.calculateTotal();
  }
}
```

### Eventual Consistency Across Aggregates

**Process managers for cross-aggregate coordination:**
```typescript
class OrderFulfillmentProcessManager {
  @EventHandler(OrderPaidEvent)
  async onOrderPaid(event: OrderPaidEvent): Promise<void> {
    // Send command to different aggregate
    await this.commandBus.dispatch(
      new ReserveInventoryCommand({
        orderId: event.orderId,
        items: event.items
      })
    );
  }

  @EventHandler(InventoryReservedEvent)
  async onInventoryReserved(event: InventoryReservedEvent): Promise<void> {
    await this.commandBus.dispatch(
      new CreateShipmentCommand({
        orderId: event.orderId,
        items: event.items
      })
    );
  }

  @EventHandler(InventoryReservationFailedEvent)
  async onInventoryReservationFailed(
    event: InventoryReservationFailedEvent
  ): Promise<void> {
    // Compensate: refund payment
    await this.commandBus.dispatch(
      new RefundPaymentCommand({
        orderId: event.orderId,
        reason: 'Insufficient inventory'
      })
    );
  }
}
```

## Best Practices Summary

### Command Design
1. **Intent Expression**: Commands represent user intent, not technical operations
2. **Validation**: Validate commands before they reach aggregates
3. **Immutability**: Commands are immutable value objects
4. **Rich Context**: Include correlation IDs, user context, timestamps
5. **Idempotency**: Include command ID for duplicate detection

### Event Design
1. **Past Tense**: Events represent facts that occurred (OrderCreated, not CreateOrder)
2. **Immutability**: Never modify published events
3. **Rich Data**: Include all data needed by consumers
4. **Versioning**: Plan for schema evolution from day one
5. **Small and Focused**: One event per state change

### Aggregate Design
1. **Consistency Boundary**: Aggregate is transaction boundary
2. **Single Responsibility**: One aggregate type per business entity
3. **Small Aggregates**: Prefer smaller aggregates for scalability
4. **Reference by ID**: Don't embed other aggregates
5. **Invariant Protection**: Enforce business rules within aggregate

### Projection Design
1. **Denormalization**: Include data from multiple aggregates
2. **Purpose-Built**: Create projections for specific query needs
3. **Idempotent Handlers**: Handle duplicate events gracefully
4. **Version Tracking**: Track last processed event version
5. **Rebuild Capability**: Support projection rebuild from events

### Event Store Management
1. **Append-Only**: Never update or delete events
2. **Snapshots**: Use snapshots for long event streams (>50 events)
3. **Archival**: Archive old events to cold storage
4. **Indexing**: Index by stream ID, type, correlation ID
5. **Monitoring**: Track event volume, processing lag, errors

## Resources

- **Books**: "Implementing Domain-Driven Design" (Vernon), "Event Sourcing & CQRS" (Betts et al)
- **Sites**: cqrs.wordpress.com, eventstore.com/blog, axoniq.io/resources
- **Tools**: EventStoreDB, Axon Framework, Marten, Eventuous
- **Patterns**: Event Sourcing, CQRS, Process Manager, Saga, Snapshot
