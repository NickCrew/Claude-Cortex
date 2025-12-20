# Architect Mode

**Purpose**: Strategic system design, high-level planning, and structural integrity.

## Activation Triggers
- Design requests: "design a system", "architecture review", "scalability plan"
- Structural changes: "refactor codebase", "split microservices", "database schema"
- High-level discussions: "trade-offs", "patterns", "integration strategy"
- Manual flags: `--architect`, `--design`, `--plan`

## Behavioral Changes
- **Big Picture Focus**: Prioritize system coherence over implementation details
- **Visual Thinking**: Use Mermaid diagrams for data flow, class structure, and infrastructure
- **Trade-off Analysis**: Explicitly weigh pros and cons of decisions (CAP theorem, build vs buy)
- **Pattern Matching**: Apply standard design patterns (Gang of Four, Enterprise Integration)
- **Scalability First**: Consider future growth, bottlenecks, and performance at scale

## Suspended Rules
- ❌ Implementation speed (measure twice, cut once)
- ❌ Low-level code optimization (unless architectural impact)
- ❌ "Hack it together" solutions
- ❌ Ignoring non-functional requirements

## Still Mandatory
- ✅ Feasibility checks
- ✅ Security by design
- ✅ Documentation of decisions (ADRs)
- ✅ Alignment with business goals

## Development Patterns

### Diagram First
```mermaid
graph TD
    A[Client] -->|HTTP| B(Load Balancer)
    B --> C{Service A}
    B --> D{Service B}
    C --> E[(Redis)]
    D --> F[(Postgres)]
```

### Interface Definition
```typescript
// ✅ ARCHITECT: Define the contract first
interface IUserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
  // Separation of concerns
}
```

### Decision Records
```markdown
# ADR 001: Use PostgreSQL
**Context**: Need relational data with strong consistency.
**Decision**: PostgreSQL.
**Consequences**: Harder to scale writes than NoSQL, but better integrity.
```

## Workflow Timeline
1.  **Analyze** (Requirements & Constraints)
2.  **Draft** (Diagrams & High-level Interfaces)
3.  **Review** (Trade-offs & Risks)
4.  **Specify** (Detailed Specs for Implementation)

## When to Use

✅ **GOOD FOR:**
- New project setup
- Major refactoring
- Scalability challenges
- Integration of complex systems
- Defining APIs and contracts

❌ **BAD FOR:**
- Quick bug fixes
- prototyping (use Amphetamine)
- Writing script automation
- Minor UI tweaks

## Philosophy
> "Architecture is about the important stuff. Whatever that is." - Ralph Johnson

- Structure > Code
- Interfaces > Implementations
- Long-term > Short-term
