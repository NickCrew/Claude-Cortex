# Authentication & Authorization Patterns

Gateway-level authentication and authorization strategies including JWT, OAuth 2.0, API keys, and RBAC.

## Token Validation at Gateway

### JWT Validation

**Configuration:**
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
```

**Flow:**
1. Client sends: Authorization: Bearer <jwt>
2. Gateway validates signature and claims
3. Gateway forwards verified claims as headers
4. Upstream services trust gateway headers

**Benefits:**
- Centralized token validation
- Services freed from auth logic
- Consistent security policy

### OAuth 2.0 Integration

**Configuration:**
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

## API Key Management

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

## Role-Based Access Control (RBAC)

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
```

**Benefits:**
- Declarative policies
- Fine-grained access control
- Audit trail
