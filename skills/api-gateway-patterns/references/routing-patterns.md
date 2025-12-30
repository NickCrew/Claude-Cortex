# Gateway Routing Patterns

Comprehensive routing strategies for API gateways including path-based, header-based, and host-based routing.

## Path-Based Routing

**Configuration Example:**
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
```

**Benefits:**
- Clear service boundaries
- Independent service scaling
- Simplified client integration

**When to Use:** Multi-service architectures, domain-driven design

## Header-Based Routing

**Configuration Example:**
```yaml
routes:
  - headers:
      X-API-Version: v2
    service: user-service-v2

  - headers:
      X-Client-Type: mobile
    service: mobile-optimized-service
```

**Use Cases:**
- A/B testing and canary deployments
- Version-based routing
- Client-specific optimizations
- Feature flagging

## Host-Based Routing

**Configuration Example:**
```yaml
routes:
  - hosts: [api.example.com]
    service: public-api

  - hosts: [internal.example.com]
    service: internal-api

  - hosts: [partner.example.com]
    service: partner-api
```

**Benefits:**
- Multi-tenancy support
- Environment separation
- Partner-specific routing
