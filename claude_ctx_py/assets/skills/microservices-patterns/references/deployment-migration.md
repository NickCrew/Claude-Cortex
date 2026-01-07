# Deployment & Migration Patterns

Strategies for deploying microservices and migrating from monolithic architectures.

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

## Continuous Deployment Strategies

### Feature Flags

**Pattern**: Deploy code, enable features gradually via configuration.

```
Code:
if (featureFlags.isEnabled("new-checkout-flow", userId)) {
  return newCheckoutService.process(order);
} else {
  return legacyCheckoutService.process(order);
}

Benefits:
- Deploy anytime, release separately
- Gradual rollout (1% → 10% → 100%)
- A/B testing
- Instant rollback (no deploy needed)
- Per-user targeting

Tools:
- LaunchDarkly (commercial)
- Unleash (open source)
- AWS AppConfig
- Custom solution (database + cache)
```

### Database Migration Strategies

**Pattern**: Evolve database schema without downtime.

```
Phase 1: Expand
- Add new column (nullable)
- Deploy code that writes to both old and new
- Backfill existing data

Phase 2: Migrate
- All code using new column
- Old column no longer written

Phase 3: Contract
- Remove old column
- Deploy code without old column references

Never:
- Rename columns in-place
- Drop columns with active code
- Change types without migration
```

### Zero-Downtime Deployment Checklist

```
✓ **Before Deployment**:
- [ ] Backward-compatible changes only
- [ ] Database migrations deployed separately
- [ ] Feature flags for risky changes
- [ ] Rollback plan documented
- [ ] Health checks configured

✓ **During Deployment**:
- [ ] Rolling deployment (not all-at-once)
- [ ] Monitor error rates
- [ ] Watch response times
- [ ] Check dependency health

✓ **After Deployment**:
- [ ] Verify metrics return to normal
- [ ] Check logs for errors
- [ ] Validate business metrics
- [ ] Document any issues
```

## Migration Best Practices

### Strangler Fig Execution Plan

```
Step 1: Analysis
- Map monolith functionality
- Identify service boundaries
- Prioritize extraction order

Step 2: Setup Infrastructure
- Deploy API gateway/router
- Setup monitoring
- Implement tracing

Step 3: Extract First Service (low-risk)
- Choose independent, low-traffic feature
- Implement as microservice
- Route small % of traffic
- Validate and increase traffic

Step 4: Extract Core Services
- One at a time
- Validate each extraction
- Maintain monolith functioning

Step 5: Retire Monolith
- When all functionality extracted
- Gradual deprecation
- Final decommission
```

### Data Migration Strategies

**Pattern**: Migrate data ownership from monolith to services.

```
Strategy 1: ETL (Extract-Transform-Load)
- One-time bulk copy
- Use for read-only/archive data
- Simple but downtime risk

Strategy 2: Dual-Write
- Write to both old and new
- Gradually switch reads
- Risk: consistency issues
- Use for transitional period only

Strategy 3: Event-Driven Sync
- Monolith publishes events
- Service consumes and builds own data
- Eventual consistency
- Best for ongoing migration

Strategy 4: Change Data Capture (CDC)
- Capture database changes
- Publish as events
- Services subscribe
- No monolith code changes
```

### API Gateway Configuration

**Pattern**: Route requests between monolith and services.

```nginx
# Nginx example
location /api/orders {
  proxy_pass http://order-service:8080;
}

location /api/products {
  proxy_pass http://product-service:8080;
}

location / {
  proxy_pass http://monolith:8080;
}

# Kong example (declarative config)
services:
  - name: order-service
    url: http://order-service:8080
    routes:
      - paths: ["/api/orders"]

  - name: monolith
    url: http://monolith:8080
    routes:
      - paths: ["/"]
```

## Testing Strategies

### Service Testing Pyramid

```
End-to-End (5%):
- Full system integration tests
- Expensive, slow, fragile
- Use sparingly for critical paths

Integration (20%):
- Service + dependencies (DB, cache)
- Test service in isolation
- Use test containers

Contract (25%):
- API contract validation
- Consumer-driven contracts (Pact)
- Ensure API compatibility

Unit (50%):
- Fast, isolated, deterministic
- Business logic coverage
- Foundation of test suite
```

### Contract Testing

**Pattern**: Verify service compatibility without integration tests.

```
Producer (Order Service):
- Publishes contract: "POST /orders expects {items, total}"
- Contract tests verify implementation matches

Consumer (UI):
- Defines expectations: "When I POST /orders, I get 201 with order_id"
- Contract tests verify producer meets expectations

Tool: Pact
1. Consumer writes Pact test
2. Publishes contract to broker
3. Producer verifies contract
4. Both can deploy independently if contracts match
```

## Deployment Tools and Platforms

### Container Orchestration

```
Kubernetes:
- Industry standard
- Complex but powerful
- Rich ecosystem
- Automatic scaling, healing

Docker Swarm:
- Simpler than K8s
- Less feature-rich
- Built into Docker
- Good for small-medium deployments

AWS ECS/Fargate:
- AWS-specific
- Simpler than K8s
- Serverless option (Fargate)
- Tight AWS integration
```

### CI/CD Pipelines

```
Typical Pipeline:

1. Code Push
   ↓
2. Build & Test
   - Unit tests
   - Linting
   - Security scan
   ↓
3. Build Container Image
   - Docker build
   - Push to registry
   ↓
4. Deploy to Staging
   - Run integration tests
   - Contract tests
   ↓
5. Deploy to Production
   - Canary deployment
   - Monitor metrics
   - Gradual rollout

Tools:
- Jenkins (self-hosted)
- GitLab CI (integrated)
- GitHub Actions (cloud)
- CircleCI (cloud)
- AWS CodePipeline (AWS)
```

### Infrastructure as Code

```
Terraform:
resource "kubernetes_deployment" "order_service" {
  metadata {
    name = "order-service"
  }
  spec {
    replicas = 3
    selector {
      match_labels = {
        app = "order-service"
      }
    }
    template {
      metadata {
        labels = {
          app = "order-service"
        }
      }
      spec {
        container {
          image = "order-service:1.2.3"
          name  = "order-service"
        }
      }
    }
  }
}

Benefits:
- Version controlled infrastructure
- Reproducible environments
- Automated provisioning
- Documentation as code
```

## Anti-Patterns to Avoid

1. **Distributed Monolith** - Tightly coupled services, must deploy together
2. **Shared Database** - Multiple services accessing same database
3. **Chatty APIs** - Excessive synchronous service calls
4. **Mega Services** - Services too large, violating single responsibility
5. **Missing Circuit Breakers** - No cascading failure protection
6. **Synchronous Everything** - No asynchronous communication
7. **God Service** - One service orchestrating everything
8. **Ignoring Network Failures** - Assuming reliable network
9. **No Versioning** - Breaking changes without versioning
10. **Missing Monitoring** - Deploying without observability
11. **Big Bang Migration** - Rewrite everything at once
12. **No Rollback Plan** - Can't undo deployments
13. **Manual Deployments** - No automation, error-prone

## Migration Checklist

### Pre-Migration
- [ ] Business case validated
- [ ] Team has microservices experience
- [ ] Monitoring infrastructure ready
- [ ] CI/CD pipelines established
- [ ] Service boundaries defined
- [ ] Migration roadmap created

### During Migration
- [ ] Extract services incrementally
- [ ] Maintain monolith stability
- [ ] Monitor both old and new
- [ ] Document service APIs
- [ ] Implement circuit breakers
- [ ] Add distributed tracing

### Post-Migration
- [ ] Decommission monolith
- [ ] Update documentation
- [ ] Conduct retrospective
- [ ] Optimize performance
- [ ] Refine monitoring
- [ ] Plan next services

## Tools and Technologies

### Deployment Platforms
- **Kubernetes**: Container orchestration
- **AWS ECS/Fargate**: Managed containers
- **Google Cloud Run**: Serverless containers
- **Azure Container Instances**: Managed containers

### Service Mesh
- **Istio**: Full-featured, complex
- **Linkerd**: Lightweight, simple
- **Consul**: Service discovery + mesh

### CI/CD
- **Jenkins**: Self-hosted, flexible
- **GitLab CI**: Integrated with Git
- **GitHub Actions**: Cloud-based
- **ArgoCD**: GitOps for Kubernetes

### Feature Flags
- **LaunchDarkly**: Enterprise feature management
- **Unleash**: Open source feature flags
- **Split.io**: Feature delivery platform

### Migration Tools
- **Debezium**: Change data capture
- **AWS DMS**: Database migration service
- **Liquibase/Flyway**: Database schema migration

## Further Reading

- "Monolith to Microservices" by Sam Newman
- "Accelerate" by Nicole Forsgren (DevOps practices)
- "Continuous Delivery" by Jez Humble
- martinfowler.com/bliki/StranglerFigApplication.html
- kubernetes.io/docs/concepts/workloads
