# Gateway Implementations

Comparison of major API gateway solutions with configuration examples and selection criteria.

## 1. Kong (Lua-based, plugin ecosystem)

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
```

**Strengths:**
- Rich plugin ecosystem (100+ plugins)
- Declarative configuration
- High performance (Nginx + OpenResty)
- Enterprise features (RBAC, analytics)

**When to Use:** Need plugins, enterprise support, Kubernetes

## 2. Nginx (High performance, widespread adoption)

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
```

**Strengths:**
- Extremely high performance
- Battle-tested stability
- Low resource footprint
- Flexible configuration

**When to Use:** Performance-critical, simple routing, existing Nginx expertise

## 3. Envoy (Modern, cloud-native, observability)

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
```

**Strengths:**
- Advanced observability (tracing, metrics)
- Service mesh integration (Istio)
- Modern L7 features
- Dynamic configuration (xDS protocol)

**When to Use:** Service mesh, Kubernetes, observability requirements

## 4. AWS API Gateway (Managed, serverless)

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
```

**Strengths:**
- Fully managed (no infrastructure)
- Native AWS integration (Lambda, DynamoDB)
- Built-in features (auth, throttling, caching)
- Pay per request

**When to Use:** AWS ecosystem, serverless architecture, rapid deployment

## Selection Criteria

| Feature | Kong | Nginx | Envoy | AWS API Gateway |
|---------|------|-------|-------|-----------------|
| Performance | High | Very High | High | Medium |
| Plugin Ecosystem | Excellent | Good | Growing | Limited |
| Observability | Good | Basic | Excellent | Good |
| Managed Option | Yes (Cloud) | No | No | Yes |
| Learning Curve | Medium | Low | High | Low |
| Cost | Free/Paid | Free | Free | Pay-per-use |
| Kubernetes Native | Yes | Partial | Yes | No |
| Service Mesh | Limited | No | Yes (Istio) | No |
