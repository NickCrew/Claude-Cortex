# Modernization Patterns

## Strangler Fig Pattern

The strangler fig pattern replaces a legacy system incrementally by routing requests to new implementations one feature at a time, while the old system continues serving unmodified paths.

### Route-Level Strangler Fig

Redirect individual routes or endpoints from old to new system:

```
                    ┌─────────────┐
  Request ────────> │   Router /  │
                    │   Proxy     │
                    └──┬──────┬───┘
                       │      │
              /new/*   │      │  /legacy/*
                       v      v
                ┌─────────┐ ┌─────────┐
                │   New   │ │ Legacy  │
                │ Service │ │ System  │
                └─────────┘ └─────────┘
```

**Implementation steps:**
1. Place a proxy/router in front of the legacy system
2. Build the new implementation for one route
3. Redirect that route to the new service
4. Verify behavior matches; keep legacy as fallback
5. Repeat for next route until legacy has zero traffic
6. Decommission the legacy system

### Feature-Level Strangler Fig

Replace internal modules or features rather than routes:

```python
# adapter layer wraps legacy and new implementations
class PaymentProcessor:
    def __init__(self, use_new_engine: bool):
        self._legacy = LegacyPaymentEngine()
        self._new = ModernPaymentEngine()
        self._use_new = use_new_engine

    def process(self, payment):
        if self._use_new:
            return self._new.process(payment)
        return self._legacy.process(payment)
```

**When to use feature-level:**
- Internal libraries or modules without clear HTTP boundaries
- Tightly coupled components that share data stores
- Batch processing systems

---

## Feature Flag Strategies

### Release Toggles

Control rollout of new features to specific user segments:

```python
# gradual rollout by percentage
if feature_flags.is_enabled("new_checkout", user_id=user.id, rollout=25):
    return new_checkout_flow(cart)
return legacy_checkout_flow(cart)
```

**Lifecycle:** Short-lived. Remove after full rollout (days to weeks).

### Experiment Toggles

A/B test new implementations against legacy:

```python
if feature_flags.get_variant("search_engine", user_id=user.id) == "elasticsearch":
    results = elasticsearch_search(query)
else:
    results = legacy_sql_search(query)

# track metrics for both paths
metrics.record("search_latency", latency, variant=variant)
```

**Lifecycle:** Medium-lived. Remove after experiment concludes.

### Ops Toggles

Kill switches for new systems under load or failure:

```python
if feature_flags.is_enabled("use_new_payment_gateway"):
    try:
        return new_gateway.charge(amount)
    except NewGatewayError:
        feature_flags.disable("use_new_payment_gateway")  # auto-fallback
        return legacy_gateway.charge(amount)
return legacy_gateway.charge(amount)
```

**Lifecycle:** Long-lived. Keep as operational safety valves.

### Flag Hygiene

- Name flags with clear prefixes: `migration_`, `experiment_`, `ops_`
- Set expiration dates; review stale flags monthly
- Clean up flags and dead code paths after rollout completes
- Log flag evaluations for debugging migration issues

---

## Migration Checklists

### Data Migration

- [ ] Audit source data: schema, volume, quality, encoding
- [ ] Design target schema with forward compatibility
- [ ] Build ETL/ELT pipeline with validation at each stage
- [ ] Run migration on a copy of production data first
- [ ] Verify row counts, checksums, referential integrity
- [ ] Plan dual-write period if zero-downtime is required
- [ ] Script rollback to restore original data
- [ ] Test rollback procedure before production migration

### API Migration

- [ ] Document all existing API consumers and their usage patterns
- [ ] Version the new API (URL path or header-based)
- [ ] Provide adapter/shim for old clients during transition
- [ ] Set deprecation timeline and communicate to consumers
- [ ] Monitor old API usage to track consumer migration progress
- [ ] Remove old API only after all consumers have migrated

### UI Migration

- [ ] Identify all pages/components to migrate
- [ ] Run old and new UI side by side (micro-frontends or feature flags)
- [ ] Match visual parity and functional behavior
- [ ] Test across browsers, devices, and accessibility standards
- [ ] Redirect old routes to new UI with 301 redirects
- [ ] Remove old UI assets after transition period

### Infrastructure Migration

- [ ] Inventory current infrastructure (servers, services, networking)
- [ ] Design target infrastructure with IaC (Terraform, CloudFormation)
- [ ] Set up parallel environments for testing
- [ ] Migrate DNS and load balancer rules incrementally
- [ ] Validate monitoring, alerting, and logging on new infrastructure
- [ ] Keep old infrastructure available for rollback window

---

## Monolith Decomposition

### Identifying Service Boundaries

1. **Domain-driven design**: Map bounded contexts from business capabilities
2. **Data ownership**: Each service owns its data store
3. **Change frequency**: Extract components that change independently
4. **Team alignment**: Service boundaries should follow team boundaries

### Decomposition Order

Start with the edges, not the core:

1. **Peripheral services first**: Notifications, reporting, logging
2. **Read-heavy services next**: Search, recommendations, analytics
3. **Write-heavy services**: Payments, orders, user management
4. **Core domain last**: The most coupled, highest-risk component

### Shared Database Escape

```
Phase 1: Monolith reads/writes shared DB
Phase 2: New service reads shared DB, writes own DB (dual-write)
Phase 3: New service reads/writes own DB, sync to shared DB
Phase 4: Remove shared DB dependency entirely
```

---

## Database Migration Patterns

### Expand-Contract Pattern

Make changes in two phases to avoid breaking existing code:

1. **Expand**: Add new columns/tables alongside old ones
2. **Migrate**: Copy data, update application code to use new schema
3. **Contract**: Remove old columns/tables after all code is updated

```sql
-- Phase 1: Expand - add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);

-- Phase 2: Migrate - populate new column
UPDATE users SET full_name = CONCAT(first_name, ' ', last_name);

-- Phase 3: Contract - drop old columns (after code is updated)
ALTER TABLE users DROP COLUMN first_name, DROP COLUMN last_name;
```

### Shadow Reads/Writes

Validate new data store by running both in parallel:

```python
def get_user(user_id):
    # primary: legacy database
    result = legacy_db.get_user(user_id)

    # shadow: new database (async, non-blocking)
    async_compare(lambda: new_db.get_user(user_id), result, metric="user_read_mismatch")

    return result  # always return legacy result during validation
```

---

## Backward Compatibility Strategies

### Semantic Versioning for Internal APIs

- MAJOR: Breaking changes (require consumer updates)
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

### Adapter Pattern

Wrap new interfaces to match old contracts:

```python
class LegacyAPIAdapter:
    """Translates new service responses to legacy format."""
    def __init__(self, new_service):
        self._service = new_service

    def get_user_info(self, user_id):
        user = self._service.get_user(user_id)
        # translate to legacy response format
        return {
            "userName": user.name,       # legacy used camelCase
            "userEmail": user.email,
            "isActive": user.status == "active",  # legacy used boolean
        }
```

### Deprecation Communication

```
Phase 1: Announce deprecation with timeline (minimum 2 release cycles)
Phase 2: Add deprecation warnings in logs and responses
Phase 3: Reduce support (bug fixes only, no new features)
Phase 4: Final removal date with migration guide
```

---

## Testing During Migration

### Characterization Tests

Capture existing behavior before refactoring:

```python
def test_legacy_checkout_total():
    """Characterization test: documents existing behavior, not desired behavior."""
    cart = Cart(items=[Item("widget", 9.99), Item("gadget", 24.99)])
    # legacy rounds differently than expected - this test documents that
    assert legacy_checkout(cart).total == 34.97  # not 34.98
```

### Contract Tests

Verify new implementations match legacy behavior:

```python
@pytest.mark.parametrize("implementation", [legacy_search, new_search])
def test_search_contract(implementation):
    """Both implementations must return same results for same input."""
    results = implementation(query="test widget", limit=10)
    assert len(results) <= 10
    assert all(r.relevance_score > 0 for r in results)
    assert results == sorted(results, key=lambda r: r.relevance_score, reverse=True)
```

### Shadow Testing in Production

Run new code path in parallel without affecting users:

```python
def handle_request(request):
    legacy_response = legacy_handler(request)

    # shadow: run new handler async, compare results
    shadow_run(new_handler, request, expected=legacy_response)

    return legacy_response  # always serve legacy during shadow period
```

---

## Rollback Procedures

### Per-Phase Rollback Plan

Every migration phase needs a documented rollback:

| Phase | Action | Rollback | Time Estimate |
| --- | --- | --- | --- |
| 1 | Deploy proxy router | Remove proxy, restore direct traffic | 5 min |
| 2 | Migrate user service | Disable feature flag, revert to legacy | 2 min |
| 3 | Dual-write to new DB | Stop writes to new DB, no data loss | 1 min |
| 4 | Switch reads to new DB | Revert read config to legacy DB | 2 min |
| 5 | Decommission legacy DB | Restore from backup (tested weekly) | 30 min |

### Rollback Triggers

Define criteria that automatically trigger rollback:

- Error rate exceeds baseline by more than 5%
- P99 latency exceeds SLA threshold
- Data consistency check fails
- Critical functionality unavailable for more than 2 minutes

### Rollback Verification

After every rollback:

1. Confirm all traffic flows through legacy path
2. Verify no data corruption from partial migration
3. Run smoke tests against legacy system
4. Document what went wrong for the next attempt
