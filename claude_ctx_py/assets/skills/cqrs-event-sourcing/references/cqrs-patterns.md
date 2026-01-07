# Reference: CQRS Pattern Deep Dive

Comprehensive implementation patterns for Command Query Responsibility Segregation.

## Basic CQRS Architecture

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

## Command Side Implementation

### Command Structure

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

### Command Handler

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

### Aggregate Root with Event Sourcing

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

## Query Side Implementation

### Read Model (Projection)

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

### Projection Handler

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

### Query Service

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
