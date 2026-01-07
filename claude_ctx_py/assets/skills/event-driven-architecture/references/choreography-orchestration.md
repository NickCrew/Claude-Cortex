# Event Choreography vs Orchestration

## Event Choreography

### Definition
Decentralized coordination through events.

### Architecture
```
Service A → Event 1 → Service B → Event 2 → Service C
                    ↓
                  Service D
```

### When to Use:
- Simple workflows (2-4 steps)
- Services naturally reactive
- High autonomy desired
- Event-driven culture

### Example: User Registration
```
1. Auth Service: UserRegistered event
   → Email Service: sends welcome email
   → Analytics Service: tracks signup
   → CRM Service: creates contact

Each service reacts independently.
```

## Event Orchestration

### Definition
Centralized coordinator manages flow.

### Architecture
```
Orchestrator → Service A
           → Service B
           → Service C

Orchestrator controls sequence and dependencies.
```

### When to Use:
- Complex workflows (5+ steps)
- Sequential dependencies
- Business logic in workflow
- Need visibility/monitoring

### Example: Order Processing
```
OrderOrchestrator:
1. Validate order
2. Reserve inventory (wait)
3. Process payment (wait)
4. Create shipment (wait)
5. Confirm order

Clear sequence, centralized control.
```

## Hybrid Approach

Combine both for complex systems:
```
High-level: Orchestration (order saga)
  Step 1: Process Order (choreography within)
    → Validate
    → Price calculation
    → Tax calculation
  Step 2: Fulfill Order (choreography within)
    → Pick items
    → Pack
    → Label
```

## Decision Matrix

| Factor | Choreography | Orchestration |
|--------|--------------|---------------|
| Workflow Complexity | 2-4 steps | 5+ steps |
| Control Flow | Implicit | Explicit |
| Service Coupling | Loose | Tighter |
| Debugging | Harder | Easier |
| Single Point of Failure | No | Yes (orchestrator) |
| Service Autonomy | High | Lower |
| Visibility | Distributed | Centralized |
| Best For | Simple, reactive flows | Complex, sequential flows |
