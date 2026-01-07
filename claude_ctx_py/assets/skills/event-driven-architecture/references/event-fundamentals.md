# Event Fundamentals

## Event Structure

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

## Event Types

### 1. Domain Events (Business Events)
Business facts within bounded context:
- OrderCreated
- PaymentProcessed
- InventoryReserved
- CustomerRegistered
- ShipmentDelivered

### 2. Integration Events (Cross-Service)
Events published across service boundaries:
- Order.Created (published to event bus)
- Customer.Updated (for other services)
- Payment.Succeeded (trigger workflows)

### 3. Change Data Capture (CDC)
Database changes as events:
- Record inserted → RecordCreated event
- Record updated → RecordUpdated event
- Record deleted → RecordDeleted event

**Tools**: Debezium, Maxwell, AWS DMS

## Event Characteristics

✓ **Good Events:**
- Immutable (cannot be changed after creation)
- Past tense naming (OrderCreated, PaymentProcessed)
- Self-contained (all necessary data included)
- Timestamped and versioned

✗ **Avoid:**
- Commands (CreateOrder vs OrderCreated)
- Mutable state changes
- Missing context or correlation data
