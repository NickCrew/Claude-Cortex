# CQRS (Command Query Responsibility Segregation)

## Definition
Separate read (query) and write (command) models for optimal performance.

## Architecture

```
Command Side (Write Model):
  User → Command → Aggregate → Event Store
                              ↓
                         Event Published
                              ↓
Read Side (Query Model):
  Event Handler → Update Read DB → Query API → User
```

## Implementation Example

### Command Side:
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

### Read Side (Projection):
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

## Benefits

1. **Optimized Models**: Write for consistency, read for performance
2. **Independent Scaling**: Scale reads and writes separately
3. **Multiple Read Models**: Different views from same events
4. **Simplified Queries**: Denormalized data, no complex joins
5. **Technology Choice**: Different databases for read/write

## When to Use CQRS

### Good Fit:
- High read:write ratio (10:1 or higher)
- Complex query requirements
- Need for multiple read models
- Performance bottlenecks in traditional model

### Avoid When:
- Simple CRUD applications
- Strong consistency required immediately
- Team unfamiliar with pattern
- Low complexity domain
