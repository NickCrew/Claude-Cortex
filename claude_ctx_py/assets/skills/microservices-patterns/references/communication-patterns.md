# Communication Patterns

Patterns for synchronous and asynchronous service-to-service communication.

## Synchronous Communication

### Pattern: API Gateway

**Purpose**: Single entry point for all clients, routing to appropriate services.

```
Client → API Gateway → [Auth, Rate Limiting, Routing] → Microservices

Benefits:
- Simplified client interface
- Centralized cross-cutting concerns
- Protocol translation (REST → gRPC)
- Request aggregation

Implementations: Kong, AWS API Gateway, Nginx, Traefik
```

### Pattern: Service-to-Service REST

**Best Practices:**
```http
# Use service discovery (Consul, Eureka, Kubernetes DNS)
GET http://order-service:8080/orders/123

# Include correlation IDs for tracing
X-Correlation-ID: a3f7c9b2-d8e1-4f6g-h9i0

# Use circuit breakers (Hystrix, Resilience4j)
@CircuitBreaker(name = "inventory-service")
public Product getProduct(String id) {
  return restTemplate.getForObject(
    "http://inventory-service/products/" + id,
    Product.class
  );
}

# Implement timeouts
connect-timeout: 2000
read-timeout: 5000
```

### Pattern: gRPC for Internal Communication

**When to Use:**
- High performance requirements
- Type-safe contracts (Protocol Buffers)
- Streaming data (server/client/bidirectional)
- Internal service-to-service communication

```protobuf
service OrderService {
  rpc GetOrder (GetOrderRequest) returns (Order);
  rpc CreateOrder (CreateOrderRequest) returns (Order);
  rpc StreamOrders (StreamRequest) returns (stream Order);
}

message Order {
  string id = 1;
  string customer_id = 2;
  repeated OrderItem items = 3;
  double total = 4;
}
```

## Asynchronous Communication

### Pattern: Event-Driven Architecture

**Purpose**: Services communicate via events, decoupled in time and space.

```
Event Types:

1. Domain Events (business events):
   - OrderCreated
   - PaymentProcessed
   - InventoryReserved

2. Change Data Capture (CDC):
   - OrderStatusChanged
   - CustomerUpdated

3. Integration Events (cross-service):
   - SendWelcomeEmail
   - UpdateRecommendations
```

**Event Structure:**
```json
{
  "event_id": "evt_a3f7c9b2",
  "event_type": "order.created",
  "event_version": "1.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "order-service",
  "correlation_id": "corr_x1y2z3",
  "data": {
    "order_id": "ord_123",
    "customer_id": "cust_456",
    "total": 99.99,
    "items": [...]
  },
  "metadata": {
    "user_id": "user_789",
    "tenant_id": "tenant_abc"
  }
}
```

### Pattern: Message Queue (Point-to-Point)

**Use Case**: Work distribution, background jobs, reliable delivery.

```
Producer → Queue → Consumer(s)

Examples:
- Order placed → Queue → Payment processor
- Email requested → Queue → Email sender
- Image uploaded → Queue → Thumbnail generator

Implementations: RabbitMQ, AWS SQS, Azure Service Bus
```

### Pattern: Publish-Subscribe (Pub/Sub)

**Use Case**: Broadcasting events to multiple interested services.

```
Publisher → Topic → Subscriber 1
                  → Subscriber 2
                  → Subscriber N

Example:
OrderCreated event published to "orders" topic
Subscribers:
  - Inventory Service (reserve stock)
  - Fulfillment Service (prepare shipment)
  - Analytics Service (update metrics)
  - Notification Service (send confirmation email)

Implementations: Apache Kafka, AWS SNS, Google Pub/Sub
```

### Pattern: Event Sourcing

**Definition**: Store all state changes as a sequence of events, not current state.

```
Traditional (CRUD):
  orders table: id, customer_id, status, total

Event Sourcing:
  order_events table:
    - OrderCreated(order_id, customer_id, items, total)
    - PaymentReceived(order_id, amount, payment_method)
    - OrderShipped(order_id, tracking_number)
    - OrderDelivered(order_id, delivery_time)

Current state = replay all events

Benefits:
- Complete audit trail
- Temporal queries ("what was the state at time T?")
- Event replay for debugging
- Easy to add new projections

Challenges:
- Query complexity
- Event versioning
- Storage growth
```

## Communication Best Practices

### When to Use Sync vs Async

**Synchronous (REST/gRPC)**:
- ✅ Real-time queries (get user profile)
- ✅ Request/response workflows
- ✅ Low latency requirements
- ❌ Long-running operations
- ❌ Fire-and-forget actions

**Asynchronous (Events/Messages)**:
- ✅ Fire-and-forget operations
- ✅ Long-running processes
- ✅ Broadcasting to multiple consumers
- ✅ Decoupling services in time
- ❌ Immediate response needed

### Service Discovery

**Pattern**: Services find each other dynamically without hard-coded URLs.

```
Options:
1. Client-Side Discovery:
   Client → Service Registry (Consul/Eureka) → Get service instances → Direct call

2. Server-Side Discovery:
   Client → Load Balancer → Service Registry → Route to instance

3. DNS-Based (Kubernetes):
   Client → DNS lookup (service-name.namespace.svc.cluster.local) → Service IP

Implementations:
- Consul (HashiCorp)
- Eureka (Netflix)
- Kubernetes DNS
- AWS Cloud Map
```

### API Versioning

**Pattern**: Maintain backward compatibility while evolving APIs.

```
Strategies:

1. URL Versioning:
   /api/v1/orders
   /api/v2/orders

2. Header Versioning:
   Accept: application/vnd.myapi.v2+json

3. Query Parameter:
   /api/orders?version=2

4. Content Negotiation:
   Accept: application/vnd.myapi+json;version=2

Recommendation: URL versioning (simplest, most explicit)

Version Lifecycle:
- v1: Production (supported)
- v2: Production (current, recommended)
- v3: Beta (early adopters)
- Deprecation policy: 6-12 months notice
```

### Error Handling

**Pattern**: Consistent error responses across services.

```json
Standard error format:
{
  "error": {
    "code": "INSUFFICIENT_INVENTORY",
    "message": "Not enough stock for product SKU-123",
    "details": {
      "product_id": "SKU-123",
      "requested": 10,
      "available": 3
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "trace_id": "abc123",
    "path": "/api/v1/orders"
  }
}

HTTP Status Codes:
- 200: Success
- 201: Created
- 400: Client error (bad request)
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 409: Conflict (business rule violation)
- 429: Too many requests (rate limited)
- 500: Server error
- 503: Service unavailable (circuit breaker open)
```

### Idempotency

**Pattern**: Same request can be repeated safely without side effects.

```
Idempotency Key:
POST /api/orders
Idempotency-Key: a3f7c9b2-d8e1-4f6g

Server stores key + response:
1. First request → Process → Save (key, response) → Return response
2. Duplicate request → Find key → Return cached response

Use for:
- Payment processing
- Order creation
- Any state-changing operation

Implementation:
- Redis/Memcached for key storage
- TTL: 24 hours
- Status: "processing", "completed", "failed"
```

## Tools and Technologies

### Synchronous Communication
- **REST**: Spring Boot, Express.js, FastAPI, ASP.NET Core
- **gRPC**: Protocol Buffers, gRPC-Go, gRPC-Java, gRPC-Web
- **API Gateway**: Kong, AWS API Gateway, Azure API Management, Apigee
- **Service Discovery**: Consul, Eureka, Kubernetes DNS, etcd

### Asynchronous Communication
- **Message Queue**: RabbitMQ, AWS SQS, Azure Service Bus
- **Pub/Sub**: Apache Kafka, AWS SNS+SQS, Google Pub/Sub, NATS
- **Event Streaming**: Apache Kafka, AWS Kinesis, Azure Event Hubs
- **Event Sourcing**: Axon Framework, EventStore, Marten

### Supporting Tools
- **Circuit Breakers**: Resilience4j, Hystrix, Polly
- **Tracing**: Jaeger, Zipkin, AWS X-Ray, DataDog APM
- **Load Balancing**: Nginx, HAProxy, Envoy, Traefik

## Further Reading

- "Enterprise Integration Patterns" by Gregor Hohpe
- "Designing Data-Intensive Applications" by Martin Kleppmann
- microservices.io/patterns/communication-style
- kafka.apache.org/documentation
- grpc.io/docs/what-is-grpc
