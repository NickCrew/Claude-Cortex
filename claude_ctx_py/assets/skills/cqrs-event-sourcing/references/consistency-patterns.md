# Reference: Consistency Patterns

Patterns for managing consistency within and across aggregates in CQRS/Event Sourcing systems.

## Immediate Consistency Within Aggregate

Strong consistency boundary:

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

## Eventual Consistency Across Aggregates

Process managers for cross-aggregate coordination:

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

## Key Concepts

### Aggregate as Consistency Boundary

- **All changes within an aggregate are immediately consistent**
- **Business invariants are enforced before events are emitted**
- **One aggregate = one transaction**

### Process Managers for Coordination

- **Orchestrate workflows across multiple aggregates**
- **Handle compensation for failures**
- **Maintain eventually consistent state across boundaries**

### Saga Pattern Alternative

When you need more complex compensation logic, consider the Saga pattern:

1. Each step has a corresponding compensation action
2. On failure, compensations are executed in reverse order
3. Maintains eventual consistency across distributed transactions
