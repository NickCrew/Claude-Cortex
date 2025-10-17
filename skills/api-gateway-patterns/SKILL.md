---
name: api-gateway-patterns
description: API Gateway patterns for routing, authentication, rate limiting, and service composition in microservices architectures. Use when implementing API gateways, building BFF layers, or managing service-to-service communication at scale.
---

# API Gateway Patterns

Expert guidance for implementing API gateways with routing, authentication, traffic management, and service composition patterns for microservices architectures at scale.

## When to Use This Skill

- Implementing API gateway infrastructure for microservices
- Designing Backend for Frontend (BFF) layers
- Adding authentication and authorization at the gateway level
- Implementing rate limiting, circuit breakers, and retry logic
- Setting up service discovery and dynamic routing
- Building API composition and aggregation layers
- Managing cross-cutting concerns (logging, monitoring, CORS)
- Evaluating gateway solutions (Kong, Nginx, Envoy, AWS API Gateway)

## Core Gateway Patterns

### 1. Gateway Routing

**Path-Based Routing:**
```yaml
# Kong/Nginx configuration style
routes:
  - path: /users/*
    service: user-service
    strip_path: true

  - path: /orders/*
    service: order-service

  - path: /payments/*
    service: payment-service
    methods: [POST, GET]

Benefits:
- Clear service boundaries
- Independent service scaling
- Simplified client integration
When: Multi-service architectures, domain-driven design
```

**Header-Based Routing:**
```yaml
routes:
  - headers:
      X-API-Version: v2
    service: user-service-v2

  - headers:
      X-Client-Type: mobile
    service: mobile-optimized-service

Use Cases:
- A/B testing and canary deployments
- Version-based routing
- Client-specific optimizations
- Feature flagging
```

**Host-Based Routing:**
```yaml
routes:
  - hosts: [api.example.com]
    service: public-api

  - hosts: [internal.example.com]
    service: internal-api

  - hosts: [partner.example.com]
    service: partner-api

Benefits:
- Multi-tenancy support
- Environment separation
- Partner-specific routing
```

### 2. Request/Response Transformation

**Request Transformation:**
```javascript
// Envoy Lua filter / Kong plugin pattern
function transform_request(request)
  -- Add correlation ID
  request.headers["X-Correlation-ID"] = generate_uuid()

  -- Transform body structure
  local body = json.decode(request.body)
  body.metadata = {
    timestamp: current_time(),
    source: request.headers["User-Agent"]
  }
  request.body = json.encode(body)

  -- Normalize headers
  request.headers["X-Forwarded-For"] = request.remote_addr
end

Use Cases:
- Header injection/normalization
- Body structure transformation
- Legacy API adaptation
- Adding metadata
```

**Response Transformation:**
```javascript
function transform_response(response)
  -- Remove sensitive fields
  local body = json.decode(response.body)
  body.internal_id = nil
  body.database_metadata = nil

  -- Add pagination metadata
  response.headers["X-Total-Count"] = body.total
  response.headers["X-Page-Size"] = body.page_size

  response.body = json.encode(body)
end

Benefits:
- Security (filter sensitive data)
- Consistency (standardized responses)
- Client optimization (field filtering)
```

### 3. API Composition and Aggregation

**Sequential Composition:**
```javascript
// Gateway aggregation pattern
async function getOrderWithDetails(orderId) {
  // 1. Fetch order
  const order = await fetch(`/orders/${orderId}`)

  // 2. Fetch user (depends on order)
  const user = await fetch(`/users/${order.userId}`)

  // 3. Fetch items (depends on order)
  const items = await Promise.all(
    order.itemIds.map(id => fetch(`/items/${id}`))
  )

  // 4. Aggregate response
  return {
    order: {
      id: order.id,
      status: order.status,
      total: order.total
    },
    customer: {
      name: user.name,
      email: user.email
    },
    items: items.map(i => ({
      name: i.name,
      price: i.price
    }))
  }
}

Pros: Single client request, reduced latency
Cons: Gateway complexity, cascading failures
When: Mobile apps, high-latency networks
```

**Parallel Composition:**
```javascript
async function getDashboard(userId) {
  // Parallel fetching of independent data
  const [profile, orders, recommendations, notifications] =
    await Promise.all([
      fetch(`/users/${userId}/profile`),
      fetch(`/users/${userId}/orders`),
      fetch(`/recommendations/${userId}`),
      fetch(`/notifications/${userId}`)
    ])

  return {
    profile,
    recentOrders: orders.slice(0, 5),
    recommendations,
    unreadCount: notifications.unread_count
  }
}

Benefits:
- Optimal performance (parallel execution)
- Reduced round trips
- Better UX (single load)
```

**GraphQL Gateway Pattern:**
```graphql
# Schema stitching across services
type Query {
  user(id: ID!): User @resolve(service: "user-service")
  orders(userId: ID!): [Order] @resolve(service: "order-service")
}

type User {
  id: ID!
  name: String!
  orders: [Order] @resolve(service: "order-service", field: "userId")
}

Benefits:
- Client-driven data fetching
- Eliminates over/under-fetching
- Strong typing
When: Complex data requirements, mobile/web apps
```

## Authentication & Authorization Patterns

### 1. Token Validation at Gateway

**JWT Validation:**
```yaml
# Kong JWT plugin configuration
plugins:
  - name: jwt
    config:
      key_claim_name: iss
      secret_is_base64: false
      claims_to_verify: [exp, iss]

  - name: jwt-claims
    config:
      # Forward claims to upstream
      claims:
        - user_id
        - roles
        - permissions
      header_names:
        - X-User-ID
        - X-User-Roles
        - X-Permissions

Flow:
1. Client sends: Authorization: Bearer <jwt>
2. Gateway validates signature and claims
3. Gateway forwards verified claims as headers
4. Upstream services trust gateway headers

Benefits:
- Centralized token validation
- Services freed from auth logic
- Consistent security policy
```

**OAuth 2.0 Integration:**
```yaml
# API Gateway OAuth configuration
oauth:
  authorization_endpoint: https://auth.example.com/oauth/authorize
  token_endpoint: https://auth.example.com/oauth/token

  flows:
    authorization_code:
      enabled: true
      scopes: [read, write, admin]

  token_validation:
    introspection_endpoint: https://auth.example.com/oauth/introspect
    cache_ttl: 300  # 5 minutes

routes:
  - path: /api/admin/*
    oauth_scopes: [admin]

  - path: /api/users/*
    oauth_scopes: [read, write]
```

### 2. API Key Management

**Key-Based Authentication:**
```yaml
# Multi-tier API key pattern
api_keys:
  - key: ak_prod_abc123
    rate_limit: 10000/hour
    tier: enterprise
    services: [users, orders, payments]

  - key: ak_prod_xyz789
    rate_limit: 1000/hour
    tier: standard
    services: [users, orders]

validation:
  header_name: X-API-Key
  cache_duration: 600

on_invalid:
  status: 401
  response:
    error: "Invalid or missing API key"
    docs: "https://docs.example.com/auth"
```

### 3. Role-Based Access Control (RBAC)

**Policy Enforcement:**
```javascript
// OPA (Open Policy Agent) integration
const policy = `
package authz

default allow = false

# Admin can access everything
allow {
  input.user.roles[_] == "admin"
}

# Users can access own resources
allow {
  input.method == "GET"
  input.path = ["users", user_id, _]
  input.user.id == user_id
}

# Order access requires ownership
allow {
  input.path = ["orders", order_id]
  order = data.orders[order_id]
  order.user_id == input.user.id
}
`

// Gateway enforcement
async function authorize(request, user) {
  const decision = await opa.evaluate({
    method: request.method,
    path: request.path.split('/'),
    user: user
  })

  if (!decision.allow) {
    return 403  // Forbidden
  }
}

Benefits:
- Declarative policies
- Fine-grained access control
- Audit trail
```

## Traffic Management Patterns

### 1. Rate Limiting

**Token Bucket Algorithm:**
```yaml
# Kong rate-limiting plugin
plugins:
  - name: rate-limiting
    config:
      second: 10
      hour: 1000
      policy: redis  # Distributed rate limiting

      # Per-consumer limits
      limit_by: consumer

      # Custom identifier
      identifier: ip

      # Headers in response
      headers:
        - X-RateLimit-Limit
        - X-RateLimit-Remaining
        - X-RateLimit-Reset

Response headers:
X-RateLimit-Limit-Second: 10
X-RateLimit-Remaining-Second: 7
X-RateLimit-Reset: 1705320045
```

**Tiered Rate Limiting:**
```javascript
// Custom rate limiter with tiers
const rateLimits = {
  free: { requests: 100, window: '1h' },
  standard: { requests: 1000, window: '1h' },
  premium: { requests: 10000, window: '1h' },
  enterprise: { requests: 100000, window: '1h' }
}

async function checkRateLimit(apiKey, tier) {
  const limit = rateLimits[tier]
  const key = `ratelimit:${tier}:${apiKey}`

  const current = await redis.incr(key)
  if (current === 1) {
    await redis.expire(key, parseWindow(limit.window))
  }

  if (current > limit.requests) {
    throw new RateLimitError(limit)
  }

  return {
    limit: limit.requests,
    remaining: limit.requests - current,
    reset: await redis.ttl(key)
  }
}
```

### 2. Circuit Breaker Pattern

**Implementation:**
```javascript
class CircuitBreaker {
  constructor(service, options = {}) {
    this.service = service
    this.failureThreshold = options.failureThreshold || 5
    this.recoveryTimeout = options.recoveryTimeout || 60000
    this.requestTimeout = options.requestTimeout || 5000

    this.state = 'CLOSED'  // CLOSED, OPEN, HALF_OPEN
    this.failures = 0
    this.nextAttempt = Date.now()
  }

  async call(request) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new CircuitOpenError('Service unavailable')
      }
      this.state = 'HALF_OPEN'
    }

    try {
      const response = await timeout(
        this.service.call(request),
        this.requestTimeout
      )

      this.onSuccess()
      return response

    } catch (error) {
      this.onFailure()
      throw error
    }
  }

  onSuccess() {
    this.failures = 0
    this.state = 'CLOSED'
  }

  onFailure() {
    this.failures++

    if (this.failures >= this.failureThreshold) {
      this.state = 'OPEN'
      this.nextAttempt = Date.now() + this.recoveryTimeout
    }
  }
}

// Usage
const userServiceBreaker = new CircuitBreaker(userService, {
  failureThreshold: 5,
  recoveryTimeout: 60000
})

app.get('/users/:id', async (req, res) => {
  try {
    const user = await userServiceBreaker.call(req)
    res.json(user)
  } catch (error) {
    if (error instanceof CircuitOpenError) {
      res.status(503).json({ error: 'Service temporarily unavailable' })
    }
  }
})
```

### 3. Retry Logic with Backoff

**Exponential Backoff:**
```javascript
async function retryWithBackoff(fn, options = {}) {
  const maxRetries = options.maxRetries || 3
  const baseDelay = options.baseDelay || 1000
  const maxDelay = options.maxDelay || 10000
  const retryableErrors = options.retryableErrors || [502, 503, 504]

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()

    } catch (error) {
      const isLastAttempt = attempt === maxRetries
      const isRetryable = retryableErrors.includes(error.status)

      if (isLastAttempt || !isRetryable) {
        throw error
      }

      // Exponential backoff with jitter
      const delay = Math.min(
        baseDelay * Math.pow(2, attempt) + Math.random() * 1000,
        maxDelay
      )

      await sleep(delay)
    }
  }
}

// Gateway usage
app.get('/users/:id', async (req, res) => {
  const user = await retryWithBackoff(
    () => userService.get(req.params.id),
    { maxRetries: 3, baseDelay: 1000 }
  )
  res.json(user)
})
```

## Backend for Frontend (BFF) Pattern

### Concept
```
Mobile App  ──→  Mobile BFF  ──→  ┐
                                  │
Web App     ──→  Web BFF     ──→  ├──→  Microservices
                                  │
Admin Panel ──→  Admin BFF   ──→  ┘

Each BFF optimized for specific client needs
```

### Mobile BFF Example
```javascript
// Mobile-optimized endpoint
app.get('/mobile/dashboard', async (req, res) => {
  const userId = req.user.id

  // Parallel fetch with reduced data
  const [profile, orders, notifications] = await Promise.all([
    userService.get(userId, { fields: 'id,name,avatar' }),
    orderService.list(userId, { limit: 5, status: 'active' }),
    notificationService.count(userId, { unread: true })
  ])

  // Mobile-optimized response
  res.json({
    user: {
      name: profile.name,
      avatar: profile.avatar,
      thumbnailUrl: generateThumbnail(profile.avatar, '100x100')
    },
    activeOrders: orders.map(o => ({
      id: o.id,
      status: o.status,
      totalFormatted: formatCurrency(o.total)
    })),
    unreadNotifications: notifications.count
  })
})
```

### Web BFF Example
```javascript
// Web-optimized endpoint with richer data
app.get('/web/dashboard', async (req, res) => {
  const userId = req.user.id

  const [profile, orders, recommendations, analytics] = await Promise.all([
    userService.get(userId),  // Full profile
    orderService.list(userId, { limit: 20 }),  // More orders
    recommendationService.get(userId),
    analyticsService.getStats(userId)
  ])

  res.json({
    user: profile,
    orders: orders,
    recommendations: recommendations,
    analytics: {
      totalSpent: analytics.totalSpent,
      orderCount: analytics.orderCount,
      averageOrderValue: analytics.averageOrderValue
    }
  })
})
```

**Benefits:**
- Client-specific optimization (payload size, data structure)
- Independent evolution (mobile vs web requirements)
- Reduced client complexity (aggregation at BFF)
- Better performance (tailored data fetching)

## Service Discovery Integration

### Dynamic Service Registry
```javascript
// Consul integration pattern
const consul = require('consul')({ host: 'consul.service' })

// Service registration
async function registerService() {
  await consul.agent.service.register({
    id: `user-service-${process.env.INSTANCE_ID}`,
    name: 'user-service',
    address: process.env.SERVICE_IP,
    port: process.env.SERVICE_PORT,
    check: {
      http: `http://${process.env.SERVICE_IP}:${process.env.SERVICE_PORT}/health`,
      interval: '10s',
      timeout: '5s'
    },
    tags: ['api', 'v1', 'production']
  })
}

// Service discovery in gateway
async function getServiceInstances(serviceName) {
  const result = await consul.health.service({
    service: serviceName,
    passing: true  // Only healthy instances
  })

  return result.map(entry => ({
    address: entry.Service.Address,
    port: entry.Service.Port
  }))
}

// Load balancing
async function routeRequest(serviceName, request) {
  const instances = await getServiceInstances(serviceName)
  const instance = loadBalancer.pick(instances)  // Round-robin, least-conn, etc.

  return proxy.forward(request, `http://${instance.address}:${instance.port}`)
}
```

## Gateway Implementations

### 1. Kong (Lua-based, plugin ecosystem)

**Configuration:**
```yaml
services:
  - name: user-service
    url: http://user-service:8080

routes:
  - name: user-routes
    service: user-service
    paths: [/users]

plugins:
  - name: jwt
  - name: rate-limiting
    config:
      minute: 100
  - name: cors
  - name: request-transformer
    config:
      add:
        headers:
          - X-Gateway: Kong

Strengths:
- Rich plugin ecosystem (100+ plugins)
- Declarative configuration
- High performance (Nginx + OpenResty)
- Enterprise features (RBAC, analytics)

When: Need plugins, enterprise support, Kubernetes
```

### 2. Nginx (High performance, widespread adoption)

**Configuration:**
```nginx
upstream user_service {
  least_conn;
  server user-service-1:8080 max_fails=3 fail_timeout=30s;
  server user-service-2:8080 max_fails=3 fail_timeout=30s;
}

server {
  listen 80;

  location /users {
    limit_req zone=api_limit burst=20 nodelay;

    proxy_pass http://user_service;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    # Timeouts
    proxy_connect_timeout 5s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
  }
}

Strengths:
- Extremely high performance
- Battle-tested stability
- Low resource footprint
- Flexible configuration

When: Performance-critical, simple routing, existing Nginx expertise
```

### 3. Envoy (Modern, cloud-native, observability)

**Configuration:**
```yaml
static_resources:
  listeners:
    - address:
        socket_address: { address: 0.0.0.0, port_value: 8080 }
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                stat_prefix: ingress_http
                route_config:
                  virtual_hosts:
                    - name: backend
                      domains: ["*"]
                      routes:
                        - match: { prefix: "/users" }
                          route: { cluster: user_service }

  clusters:
    - name: user_service
      type: STRICT_DNS
      lb_policy: ROUND_ROBIN
      health_checks:
        - timeout: 1s
          interval: 10s
          http_health_check:
            path: /health
      load_assignment:
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address: { socket_address: { address: user-service, port_value: 8080 } }

Strengths:
- Advanced observability (tracing, metrics)
- Service mesh integration (Istio)
- Modern L7 features
- Dynamic configuration (xDS protocol)

When: Service mesh, Kubernetes, observability requirements
```

### 4. AWS API Gateway (Managed, serverless)

**Configuration:**
```yaml
# OpenAPI specification
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0

paths:
  /users/{id}:
    get:
      x-amazon-apigateway-integration:
        uri: arn:aws:lambda:us-east-1:123456:function:getUser
        httpMethod: POST
        type: aws_proxy

      x-amazon-apigateway-request-validator: all

      x-amazon-apigateway-throttle:
        rateLimit: 1000
        burstLimit: 2000

Strengths:
- Fully managed (no infrastructure)
- Native AWS integration (Lambda, DynamoDB)
- Built-in features (auth, throttling, caching)
- Pay per request

When: AWS ecosystem, serverless architecture, rapid deployment
```

## Best Practices Summary

1. **Centralize Cross-Cutting Concerns**: Authentication, logging, monitoring at gateway
2. **Keep Gateway Lightweight**: Avoid complex business logic, delegate to services
3. **Implement Health Checks**: Monitor upstream service health, remove unhealthy instances
4. **Use Circuit Breakers**: Prevent cascading failures, fail fast
5. **Apply Rate Limiting**: Protect services from overload, implement tiered limits
6. **Enable Observability**: Distributed tracing, metrics, structured logging
7. **Version APIs**: Support multiple API versions, plan deprecation
8. **Secure Communication**: TLS everywhere, mutual TLS for service-to-service
9. **Cache Strategically**: Response caching, but invalidate properly
10. **Test Resilience**: Chaos engineering, failure injection, load testing

## Anti-Patterns to Avoid

1. **Business Logic in Gateway**: Keep gateway focused on routing/security
2. **Chatty Composition**: Too many upstream calls (use BFF, GraphQL)
3. **Single Point of Failure**: Deploy redundantly, use load balancers
4. **No Timeout Configuration**: Always set connection/read timeouts
5. **Ignoring Backpressure**: Implement queue limits, graceful degradation
6. **Over-Aggregation**: Don't make gateway do too much work
7. **Inadequate Monitoring**: Must track latency, errors, throughput
8. **No Rate Limiting**: Services will be overwhelmed eventually
9. **Synchronous Everything**: Use async patterns for non-critical operations
10. **No Version Strategy**: Breaking changes break all clients

## Resources

- **Kong**: https://docs.konghq.com/gateway/latest/
- **Nginx**: https://nginx.org/en/docs/
- **Envoy**: https://www.envoyproxy.io/docs/envoy/latest/
- **AWS API Gateway**: https://docs.aws.amazon.com/apigateway/
- **Patterns**: "Microservices Patterns" by Chris Richardson
- **Service Mesh**: https://istio.io/latest/docs/
- **Circuit Breakers**: Martin Fowler's CircuitBreaker pattern
- **BFF Pattern**: Sam Newman's "Building Microservices"
