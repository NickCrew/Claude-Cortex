---
name: microservices-patterns
description: Comprehensive microservices architecture patterns covering service decomposition, communication, data management, and resilience strategies. Use when designing distributed systems, breaking down monoliths, or implementing service-to-service communication.
---

# Microservices Architecture Patterns

Expert guidance for designing, implementing, and operating microservices architectures with proven patterns for service decomposition, inter-service communication, data management, and operational resilience.

## When to Use This Skill

- Breaking down monolithic applications into services
- Designing new distributed systems from scratch
- Implementing service-to-service communication patterns
- Managing data consistency across services
- Building resilient distributed systems
- Defining service boundaries and responsibilities
- Implementing API gateways and service meshes
- Designing event-driven architectures
- Managing cross-cutting concerns (auth, logging, tracing)

## Core Principles

### 1. Single Responsibility per Service
Each microservice should have one reason to change and one business capability.

**Good Service Boundaries:**
```
✓ User Authentication Service
✓ Order Management Service
✓ Inventory Service
✓ Notification Service

✗ User and Order Management Service
✗ Everything Service
```

### 2. Independent Deployability
Services should be deployable without coordinating with other services.

### 3. Decentralized Data Management
Each service owns its data and doesn't share databases.

### 4. Design for Failure
Failures are inevitable in distributed systems; design for resilience.

### 5. Infrastructure Automation
Automate deployment, scaling, and recovery.

## Service Decomposition Patterns

### Pattern 1: Decompose by Business Capability

**Definition**: Organize services around business capabilities, not technical layers.

**Example:**
```
Business Capabilities → Services

Order Management:
  - Order Service (create, track, cancel orders)
  - Fulfillment Service (pick, pack, ship)

Customer Management:
  - Customer Profile Service
  - Customer Preferences Service

Inventory:
  - Stock Management Service
  - Warehouse Service
```

**Benefits:**
- Services aligned with business domains
- Clear ownership boundaries
- Easier to understand and maintain
- Teams organized around business capabilities

**Trade-offs:**
- Requires deep business understanding
- May need refactoring as business evolves
- Service boundaries can be subjective

### Pattern 2: Decompose by Subdomain (DDD)

**Definition**: Use Domain-Driven Design to identify bounded contexts as service boundaries.

**Example:**
```
E-commerce Domain:

Core Subdomains (competitive advantage):
  - Product Catalog Service
  - Order Processing Service
  - Pricing Engine Service

Supporting Subdomains:
  - Customer Service
  - Notification Service

Generic Subdomains (buy vs. build):
  - Payment Gateway (integrate Stripe)
  - Shipping (integrate FedEx/UPS)
```

**Bounded Context Indicators:**
- Different language/terminology
- Different business rules
- Independent rate of change
- Different data models

### Pattern 3: Decompose by Transaction

**Definition**: Group operations that need to be ACID transactions into a service.

**Example:**
```
Order Service includes:
  - Create Order
  - Reserve Inventory
  - Calculate Total
  - Apply Discount

Why? These operations need to be atomic and consistent.
```

**When to Use:**
- Operations require strong consistency
- Complex business rules span multiple entities
- Avoid distributed transactions

## Communication Patterns

### Synchronous Communication

#### Pattern: API Gateway

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

#### Pattern: Service-to-Service REST

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

#### Pattern: gRPC for Internal Communication

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

### Asynchronous Communication

#### Pattern: Event-Driven Architecture

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

#### Pattern: Message Queue (Point-to-Point)

**Use Case**: Work distribution, background jobs, reliable delivery.

```
Producer → Queue → Consumer(s)

Examples:
- Order placed → Queue → Payment processor
- Email requested → Queue → Email sender
- Image uploaded → Queue → Thumbnail generator

Implementations: RabbitMQ, AWS SQS, Azure Service Bus
```

#### Pattern: Publish-Subscribe (Pub/Sub)

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

#### Pattern: Event Sourcing

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

## Data Management Patterns

### Pattern: Database per Service

**Principle**: Each service has its own database, never shared.

```
Order Service → Orders DB (PostgreSQL)
Inventory Service → Inventory DB (PostgreSQL)
Product Service → Products DB (MongoDB)
Analytics Service → Analytics DB (ClickHouse)

Benefits:
- Independent scaling
- Technology choice flexibility
- Loose coupling
- Clear ownership

Challenges:
- No cross-service joins
- Distributed transactions
- Data consistency
```

### Pattern: Saga (Distributed Transactions)

**Purpose**: Maintain data consistency across services without 2PC.

#### Orchestration-Based Saga
```
Order Saga Orchestrator:

1. Create Order (Order Service)
   ↓ success
2. Reserve Inventory (Inventory Service)
   ↓ success
3. Process Payment (Payment Service)
   ↓ success
4. Update Order Status (Order Service)
   ↓ failure → Compensate
5. Compensating Transactions:
   - Release Inventory
   - Refund Payment
   - Cancel Order

Implementation:
- Orchestrator maintains state machine
- Explicit control flow
- Centralized logic
```

#### Choreography-Based Saga
```
Event-Driven Saga:

OrderCreated event
  → Inventory Service reserves stock
    → InventoryReserved event
      → Payment Service processes payment
        → PaymentProcessed event
          → Order Service updates status

If failure at any step:
  → Compensating events cascade backwards

Implementation:
- Decentralized coordination
- Event-driven
- Implicit control flow
```

### Pattern: CQRS (Command Query Responsibility Segregation)

**Definition**: Separate read and write models for optimal performance.

```
Write Model (Commands):
  - Optimized for consistency
  - Normalized schema
  - Transactional

Read Model (Queries):
  - Optimized for performance
  - Denormalized views
  - Eventually consistent
  - Materialized views/caching

Sync via events:
  Command → Write DB → Event → Read DB(s)

Example:
  Write: OrderCreated → Orders DB (PostgreSQL)
  Event: OrderCreated published
  Read: Update OrderSummary view (Redis)
        Update OrderAnalytics (Elasticsearch)
```

### Pattern: API Composition

**Purpose**: Join data from multiple services at the API layer.

```
GET /customers/123/dashboard

API Gateway:
1. GET /customers/123 (Customer Service)
2. GET /orders?customer_id=123 (Order Service)
3. GET /recommendations/123 (Recommendation Service)
4. Compose response:

{
  "customer": {...},
  "recent_orders": [...],
  "recommendations": [...]
}

Challenges:
- N+1 queries
- Slower response time
- Complex error handling

Optimizations:
- Parallel requests
- GraphQL (client-controlled aggregation)
- Backend for Frontend (BFF) pattern
```

## Resilience Patterns

### Pattern: Circuit Breaker

**Purpose**: Prevent cascading failures by failing fast.

```
States:
  Closed → Normal operation, requests pass through
  Open → Failure threshold reached, fail fast
  Half-Open → Test if service recovered

Configuration:
  failure_threshold: 5 failures in 10s
  timeout: 30s
  half_open_max_calls: 3

@CircuitBreaker(name = "payment-service")
public PaymentResult processPayment(Payment payment) {
  return paymentClient.process(payment);
}

Libraries: Resilience4j, Hystrix, Polly
```

### Pattern: Retry with Exponential Backoff

**Purpose**: Retry failed requests with increasing delays.

```
@Retry(
  maxAttempts = 3,
  backoff = @Backoff(
    delay = 1000,  // 1s initial
    multiplier = 2,  // 1s, 2s, 4s
    maxDelay = 10000
  )
)
public Order getOrder(String id) {
  return orderClient.getOrder(id);
}

Add jitter to prevent thundering herd:
delay = base_delay * (2 ^ attempt) + random(0, 1000)
```

### Pattern: Bulkhead

**Purpose**: Isolate resources to prevent one failure affecting others.

```
Thread Pool Isolation:

payment-service:
  thread_pool_size: 10
  queue_size: 20

inventory-service:
  thread_pool_size: 20
  queue_size: 50

If payment-service threads exhaust, inventory-service unaffected.

@Bulkhead(
  name = "payment-service",
  type = Bulkhead.Type.THREADPOOL,
  maxThreadPoolSize = 10
)
```

### Pattern: Rate Limiting

**Purpose**: Protect services from overload.

```
Strategies:

1. Token Bucket:
   - Tokens refill at fixed rate
   - Request consumes token
   - Burst capacity allowed

2. Leaky Bucket:
   - Requests queued
   - Processed at fixed rate
   - Queue overflow rejected

3. Fixed Window:
   - 100 requests per minute
   - Counter resets each minute

4. Sliding Window:
   - More accurate
   - Prevents burst at window boundary

Implementation:
@RateLimiter(
  name = "api",
  limitForPeriod = 100,
  limitRefreshPeriod = "1m"
)
```

### Pattern: Timeout

**Purpose**: Prevent indefinite waiting.

```
Timeout Hierarchy:

Client → (5s) → API Gateway → (3s) → Service A → (1s) → Service B

Each layer has shorter timeout than caller.

RestTemplate:
  .setConnectTimeout(2000)
  .setReadTimeout(5000)

HTTP Client:
  HttpClient.newBuilder()
    .connectTimeout(Duration.ofSeconds(2))
    .build()
```

## Cross-Cutting Concerns

### Observability Patterns

#### Distributed Tracing
```
Request ID propagation:

Client → API Gateway [trace_id: abc123]
  → Service A [trace_id: abc123, span_id: 001]
    → Service B [trace_id: abc123, span_id: 002]
    → Service C [trace_id: abc123, span_id: 003]

Implementations: Jaeger, Zipkin, AWS X-Ray

Correlation:
X-Correlation-ID: abc123
X-Request-ID: req_xyz789
```

#### Centralized Logging
```
Log aggregation pattern:

Services → Log Shipper → Log Aggregator → Search/Analysis

Structure logs (JSON):
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "order-service",
  "trace_id": "abc123",
  "span_id": "001",
  "message": "Order created",
  "order_id": "ord_123",
  "customer_id": "cust_456"
}

Stack: Filebeat → Logstash → Elasticsearch → Kibana
       Fluentd → Kafka → Splunk
```

#### Metrics & Monitoring
```
Key Metrics (RED method):
  - Rate: requests per second
  - Errors: error rate
  - Duration: response time (p50, p95, p99)

USE method (infrastructure):
  - Utilization: CPU, memory, disk
  - Saturation: queue depth
  - Errors: error counts

Implementations: Prometheus, Grafana, DataDog
```

### Service Mesh

**Purpose**: Infrastructure layer handling service-to-service communication.

```
Features:
  - Traffic management (routing, retries, timeouts)
  - Security (mTLS, authentication)
  - Observability (metrics, tracing)
  - Resilience (circuit breaking, rate limiting)

Architecture:
  Service A ←→ Sidecar Proxy (Envoy)
                    ↕
             Control Plane (Istio/Linkerd)
                    ↕
  Service B ←→ Sidecar Proxy (Envoy)

Implementations: Istio, Linkerd, Consul Connect
```

## Deployment Patterns

### Blue-Green Deployment
```
Load Balancer
  → Blue (current version, 100% traffic)
  → Green (new version, 0% traffic)

Deploy to Green → Test → Switch traffic → Blue becomes standby
```

### Canary Deployment
```
Load Balancer
  → v1 (95% traffic)
  → v2 (5% traffic - canary)

Monitor metrics → Increase traffic → Full rollout
```

### Rolling Deployment
```
Instances: [v1, v1, v1, v1]
Step 1:    [v2, v1, v1, v1]
Step 2:    [v2, v2, v1, v1]
Step 3:    [v2, v2, v2, v1]
Step 4:    [v2, v2, v2, v2]
```

## Anti-Patterns to Avoid

1. **Distributed Monolith**: Services tightly coupled, must deploy together
2. **Shared Database**: Multiple services accessing same database
3. **Chatty APIs**: Too many synchronous calls between services
4. **Mega Services**: Services too large, violating single responsibility
5. **Missing Circuit Breakers**: No protection against cascading failures
6. **Synchronous Everything**: No asynchronous communication
7. **God Service**: One service orchestrating everything
8. **Ignoring Network Failures**: Assuming network is reliable
9. **No Versioning**: Breaking changes without versioning strategy
10. **Missing Monitoring**: Deploying without observability

## Migration Strategies

### Strangler Fig Pattern

**Purpose**: Gradually migrate from monolith to microservices.

```
Phase 1: Routing layer intercepts requests
  Client → Router → Monolith (all traffic)

Phase 2: Extract first service
  Client → Router → Service A (10% traffic)
                 → Monolith (90% traffic)

Phase 3: Extract more services
  Client → Router → Service A (all orders)
                 → Service B (all users)
                 → Monolith (remaining)

Phase N: Retire monolith
  Client → Router → Services A, B, C, ... (all traffic)
```

### Branch by Abstraction

**Purpose**: Refactor incrementally without feature branches.

```
1. Create abstraction layer
2. Implement new service behind abstraction
3. Gradually migrate calls to new implementation
4. Remove old implementation
5. Remove abstraction (optional)
```

## Best Practices Summary

1. **Service Boundaries**: Align with business capabilities, not technical layers
2. **Data Ownership**: Each service owns its data, no shared databases
3. **Communication**: Async for events, sync for queries, choose appropriately
4. **Resilience**: Circuit breakers, retries, timeouts on all external calls
5. **Observability**: Distributed tracing, centralized logging, metrics everywhere
6. **Deployment**: Automate everything, blue-green or canary deploys
7. **Versioning**: Version all APIs, maintain backward compatibility
8. **Testing**: Unit, integration, contract, end-to-end, chaos engineering
9. **Security**: mTLS between services, API gateway for external auth
10. **Documentation**: Service catalog, API specs, architecture diagrams

## Resources

- **Books**: "Building Microservices" (Newman), "Microservices Patterns" (Richardson)
- **Sites**: microservices.io, Martin Fowler's microservices articles
- **Tools**: Kubernetes, Istio, Linkerd, Kafka, Kong, Jaeger
- **Patterns**: CQRS, Event Sourcing, Saga, Circuit Breaker, API Gateway
