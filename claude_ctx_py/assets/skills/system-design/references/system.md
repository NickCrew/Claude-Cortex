# Reference: system

# /design:system - System and Component Design

## Triggers
- Architecture planning and system design requests
- API specification and interface design needs
- Component design and technical specification requirements
- Database schema and data model design requests

## Usage
```
/design:system [target] [--type architecture|api|component|database] [--format diagram|spec|code]
```

## Behavioral Flow
1. **Analyze**: Examine target requirements and existing system context
2. **Plan**: Define design approach and structure based on type and format
3. **Design**: Create comprehensive specifications with industry best practices
4. **Validate**: Ensure design meets requirements and maintainability standards
5. **Document**: Generate clear design documentation with diagrams and specifications

Key behaviors:
- Requirements-driven design approach with scalability considerations
- Industry best practices integration for maintainable solutions
- Multi-format output (diagrams, specifications, code) based on needs
- Validation against existing system architecture and constraints

## Personas (Thinking Modes)
- **architect**: System structure, scalability patterns, component relationships
- **system-designer**: Design principles, interface contracts, specification clarity

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Large system design (>10 components)
- ✅ Existing system analysis needed for integration
- ✅ Complex API specification (>20 endpoints)
- ✅ Multi-system architecture design

**Available subagents**:
- **Explore**: Existing system analysis, pattern discovery, integration points
- **general-purpose**: Complex design analysis, specification generation

**Delegation strategy for comprehensive design**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Analyze existing system architecture</description>
  <prompt>
    Explore for design context:
    - Current architecture patterns
    - Existing APIs and interfaces
    - Component relationships
    - Integration points
    Thoroughness: medium
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Generate design specification</description>
  <prompt>
    Create [architecture|api|component|database] design:
    - Type: [type]
    - Format: [diagram|spec|code]
    - Apply architect + system-designer thinking
    - Use Context7 for best practices
    - Use Sequential for complex analysis
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple component design (single component, clear interface)
- ❌ Small API spec (<10 endpoints)
- ❌ Diagram-only output (no deep analysis)
- ❌ Design refinement (already have context)

## Tool Coordination
- **Task tool**: Launches subagents for complex system design requiring exploration
- **Read**: Requirements, existing specs (direct for simple, by subagent for complex)
- **Grep/Glob**: Pattern analysis (by subagent for complex)
- **Write**: Design documentation (direct for simple, by subagent for complex)
- **Context7**: Best practices and design patterns
- **Sequential**: Multi-step design analysis

## Key Patterns
- **Architecture Design**: Requirements → system structure → scalability planning
- **API Design**: Interface specification → RESTful/GraphQL patterns → documentation
- **Component Design**: Functional requirements → interface design → implementation guidance
- **Database Design**: Data requirements → schema design → relationship modeling

## Examples

### System Architecture Design
```
/design:system user-management-system --type architecture --format diagram
# Creates comprehensive system architecture with component relationships
# Includes scalability considerations and best practices
```

### API Specification Design
```
/design:system payment-api --type api --format spec
# Generates detailed API specification with endpoints and data models
# Follows RESTful design principles and industry standards
```

### Component Interface Design
```
/design:system notification-service --type component --format code
# Designs component interfaces with clear contracts and dependencies
# Provides implementation guidance and integration patterns
```

### Database Schema Design
```
/design:system e-commerce-db --type database --format diagram
# Creates database schema with entity relationships and constraints
# Includes normalization and performance considerations
```

## Boundaries

**Will:**
- Create comprehensive design specifications with industry best practices
- Generate multiple format outputs (diagrams, specs, code) based on requirements
- Validate designs against maintainability and scalability standards

**Will Not:**
- Generate actual implementation code (use /dev:implement for implementation)
- Modify existing system architecture without explicit design approval
- Create designs that violate established architectural constraints
