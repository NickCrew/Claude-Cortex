# Reference: diagrams

# /docs:diagrams - Mermaid Diagram Builder

## Triggers
- Requests for system, workflow, or API visualizations
- Documentation needing flowcharts, sequence diagrams, ERDs, or timelines
- Architecture or process explanations that benefit from diagrams
- User journeys, state machines, or decision tree visualizations

## Usage
```
/docs:diagrams [description|input] [--type flowchart|sequence|erd|state|gantt|timeline|class|journey|quadrant|pie|gitgraph] [--style basic|styled]
```

## Behavioral Flow
1. **Scope**: Identify entities, relationships, and target audience
2. **Select**: Choose the best Mermaid diagram type for the data
3. **Draft**: Produce a clean base diagram and a styled variant
4. **Validate**: Ensure readability, labeling, and rendering compatibility
5. **Deliver**: Provide render tips, export formats, and alternatives

Key behaviors:
- Always deliver both basic and styled Mermaid code blocks
- Include comments for non-obvious Mermaid syntax
- Provide at least one alternative diagram option when multiple types fit
- Add accessibility notes (color contrast, labels, reading order)

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Complex diagrams with >10 nodes or >2 lanes
- ✅ Multi-diagram deliverables (e.g., sequence + ERD)
- ✅ Architecture visualizations needing layering and annotations

**Available subagents**:
- **mermaid-expert**: Diagram selection, Mermaid syntax, styling, and export guidance

**Delegation strategy**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>mermaid-expert</subagent_type>
  <description>Create Mermaid diagrams from the provided description</description>
  <prompt>
    Build Mermaid diagrams with both basic and styled variants.
    Requirements:
    - Choose the best diagram type
    - Provide alternative option if applicable
    - Include comments for complex syntax
    - Add rendering and export recommendations
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Single, simple diagram (<6 nodes)
- ❌ Minor tweaks to existing Mermaid code

## Tool Coordination
- **Task tool**: Delegates to mermaid-expert for complex diagram requests
- **Read**: Ingest specs or existing docs
- **Write**: Deliver Mermaid code in documentation files

## Examples

### Flowchart
```
/docs:diagrams "User login flow with MFA and lockout" --type flowchart
```

### Sequence Diagram
```
/docs:diagrams "Checkout API interaction across frontend, payments, and inventory" --type sequence
```

### ERD
```
/docs:diagrams "Customer, Order, Invoice, Payment schema" --type erd
```

## Boundaries

**Will:**
- Produce clear Mermaid diagrams with basic + styled variants
- Add labels, comments, and accessibility guidance
- Suggest export formats and tooling for rendering

**Will Not:**
- Ship diagrams without confirming intent or scope when inputs are ambiguous
- Produce unreadable, overly dense diagrams without proposing simplifications
