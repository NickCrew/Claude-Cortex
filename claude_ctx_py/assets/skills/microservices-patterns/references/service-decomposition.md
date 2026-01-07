# Service Decomposition Patterns

Strategies for breaking down monoliths and defining service boundaries.

## Pattern 1: Decompose by Business Capability

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
- Stable over time (business capabilities change slowly)

**Trade-offs:**
- Requires deep business understanding
- May need refactoring as business evolves
- Service boundaries can be subjective

**Process:**
1. Identify business capabilities (what the business does)
2. Group related capabilities
3. Define service per capability
4. Validate with domain experts

## Pattern 2: Decompose by Subdomain (DDD)

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

**DDD Concepts:**
- **Bounded Context**: Clear boundary for a model's applicability
- **Ubiquitous Language**: Shared vocabulary within a context
- **Context Map**: Relationships between bounded contexts
- **Aggregates**: Consistency boundaries within a service

**Bounded Context Indicators:**
- Different language/terminology
- Different business rules
- Independent rate of change
- Different data models

**Process:**
1. Perform domain analysis (Event Storming workshop)
2. Identify bounded contexts
3. Map context relationships
4. Create service per bounded context

## Pattern 3: Decompose by Transaction

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

**Trade-offs:**
- ✅ Strong consistency within service
- ❌ May create larger services
- ❌ Can conflict with business capability alignment

## Service Boundary Validation

### Checklist for Good Service Boundaries

✓ **Single Responsibility**
- Service has one reason to change
- Clear, focused purpose
- No overlapping concerns

✓ **Independent Deployability**
- Can deploy without coordinating with other teams
- Breaking changes don't affect other services
- Versioned APIs for backward compatibility

✓ **Data Ownership**
- Service owns its data exclusively
- No shared databases
- Clear data access patterns

✓ **Team Ownership**
- One team owns the service
- Team can make decisions independently
- Clear accountability

✓ **Minimal Coupling**
- Few dependencies on other services
- Async communication preferred
- Well-defined contracts

### Anti-patterns to Avoid

❌ **Distributed Monolith**
- Services must deploy together
- Tight coupling through shared data
- Synchronous call chains

❌ **Anemic Services**
- Service is just a CRUD wrapper
- No business logic
- No clear responsibility

❌ **God Service**
- Service does too much
- Multiple unrelated responsibilities
- Becomes a bottleneck

## Service Sizing Guidelines

### Micro vs Macro Services

**Microservices** (small, focused):
- Single business capability
- Small team ownership (2-pizza team)
- Quick to understand and modify
- May require more orchestration

**Macroservices** (larger, self-contained):
- Multiple related capabilities
- Reduced inter-service communication
- Simpler operational overhead
- May be harder to understand

**Right Size**:
> "A service should be as small as possible but as large as necessary"
> - Focus on clear boundaries, not arbitrary size

### Size Indicators

**Too Small** (consider merging):
- Excessive inter-service communication
- Always deploy together
- Shared data models
- No independent value

**Too Large** (consider splitting):
- Multiple teams working on same service
- Frequent merge conflicts
- Unrelated features bundled together
- Performance bottlenecks

## Tools and Techniques

### Event Storming
Workshop technique to discover domain events and boundaries:
- Gather domain experts
- Identify domain events (past tense verbs)
- Group events into bounded contexts
- Define service boundaries

### Context Mapping
Visualize relationships between services:
- Upstream/Downstream dependencies
- Customer/Supplier relationships
- Shared Kernel (shared code/data)
- Anti-Corruption Layer (translation between contexts)

### Service Blueprint
Document service architecture:
- Service responsibilities
- Dependencies (upstream/downstream)
- Data ownership
- API contracts

## Decision Framework

### Questions to Ask

1. **What business capability does this serve?**
   - Aligns service with business organization

2. **Who owns this domain?**
   - Defines team boundaries

3. **What data does this need exclusive access to?**
   - Determines data ownership

4. **What must be strongly consistent?**
   - Groups transactions appropriately

5. **What changes together?**
   - Identifies coupling

6. **What scales independently?**
   - Separates different scalability needs

## Further Reading

- "Domain-Driven Design" by Eric Evans
- "Implementing Domain-Driven Design" by Vaughn Vernon
- "Building Microservices" by Sam Newman
- microservices.io/patterns/decomposition
