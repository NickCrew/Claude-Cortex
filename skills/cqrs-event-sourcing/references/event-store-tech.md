# Reference: Event Store Technology Patterns

Implementation patterns for popular event store technologies including EventStoreDB and Axon Framework.

## EventStoreDB Pattern

Using EventStoreDB (specialized event store):

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

## Axon Framework Pattern

Using Axon Framework (Java/Spring):

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
