# Saga Pattern (Distributed Transactions)

## Definition
Manage data consistency across services using a sequence of local transactions coordinated by events or orchestration.

## Orchestration-Based Saga

### Central coordinator manages transaction flow.

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

### Benefits:
- Centralized logic, easy to understand
- Explicit control flow
- Simple error handling

### Drawbacks:
- Single point of failure
- Tight coupling to orchestrator
- Can become complex with many steps

## Choreography-Based Saga

### Services coordinate via events without central controller.

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

### Event Flow:
```
Success Flow:
OrderCreated → InventoryReserved → PaymentProcessed → OrderConfirmed

Failure Flow (Payment fails):
OrderCreated → InventoryReserved → PaymentFailed → OrderCancelled
  → InventoryReleased (compensation)
```

### Benefits:
- Decentralized, no single point of failure
- Services remain autonomous
- Natural event-driven flow

### Drawbacks:
- Implicit control flow, harder to understand
- Debugging complexity
- Risk of circular dependencies

## Saga Design Patterns

### 1. Compensating Transactions:
```
Action: ReserveInventory
Compensation: ReleaseInventory

Action: ProcessPayment
Compensation: RefundPayment

Action: CreateShipment
Compensation: CancelShipment
```

### 2. Semantic Lock:
```
Mark resource as "pending" to prevent concurrent access:
- Order status: PENDING_PAYMENT
- Inventory: RESERVED (not available for other orders)
- Payment: AUTHORIZED (not captured yet)
```

### 3. Saga Log:
```
Persist saga state for recovery:
- Current step
- Completed steps
- Compensation state
- Allows restart after failure
```
