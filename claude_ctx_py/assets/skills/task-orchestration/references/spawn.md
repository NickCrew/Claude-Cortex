# Reference: spawn

# /orchestrate:spawn - Meta-System Task Orchestration

## Triggers
- Complex multi-domain operations requiring intelligent task breakdown
- Large-scale system operations spanning multiple technical areas
- Operations requiring parallel coordination and dependency management
- Meta-level orchestration beyond standard command capabilities

## Usage
```
/orchestrate:spawn [complex-task] [--strategy sequential|parallel|adaptive] [--depth normal|deep]
```

## Behavioral Flow
1. **Analyze**: Parse complex operation requirements and assess scope across domains
2. **Decompose**: Break down operation into coordinated subtask hierarchies
3. **Orchestrate**: Execute tasks using optimal coordination strategy (parallel/sequential)
4. **Monitor**: Track progress across task hierarchies with dependency management
5. **Integrate**: Aggregate results and provide comprehensive orchestration summary

Key behaviors:
- Meta-system task decomposition with Epic → Story → Task → Subtask breakdown
- Intelligent coordination strategy selection based on operation characteristics
- Cross-domain operation management with parallel and sequential execution patterns
- Advanced dependency analysis and resource optimization across task hierarchies
## MCP Integration
- **Native Orchestration**: Meta-system command uses native coordination without MCP dependencies
- **Progressive Integration**: Coordination with systematic execution for progressive enhancement
- **Framework Integration**: Advanced integration with SuperClaude orchestration layers

## Personas (Thinking Modes)
Meta-system orchestration benefits from high-level architectural thinking:
- **architect**: System-wide design, component relationships, scalability patterns
- **analyzer**: Dependency analysis, complexity assessment, risk evaluation

*Note: Spawn is meta-level - it breaks down operations and delegates to subagents. Each spawned subagent may adopt additional personas as needed.*

## Delegation Protocol

**This command ALWAYS delegates** - spawn is specifically for complex multi-domain operations requiring subagent coordination.

**When spawn is triggered**:
- ✅ Operations spanning >5 technical domains
- ✅ System-wide changes (>10 files or >3 directories)
- ✅ Complex dependency chains requiring careful orchestration
- ✅ Enterprise-scale operations with governance requirements

**Delegation strategy**:
1. **Analyze**: Break down operation into independent workstreams
2. **Map dependencies**: Identify what must be sequential vs parallel
3. **Launch subagents**: Use Task tool to spawn multiple subagents
4. **Coordinate**: Monitor progress and integrate results
5. **Validate**: Apply quality gates across all workstreams

**Typical subagent usage**:
```xml
<!-- Spawn launches multiple Task tool subagents based on decomposition -->
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Analyze existing system architecture</description>
  <prompt>Explore codebase to understand current patterns...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Implement backend components</description>
  <prompt>Build backend services with architect guidance...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Implement frontend components</description>
  <prompt>Build frontend UI components...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>test-automator</subagent_type>
  <description>Generate comprehensive test suite</description>
  <prompt>Create tests covering all components...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Review entire implementation</description>
  <prompt>System-wide quality and security review...</prompt>
</invoke>
</function_calls>
```

## Tool Coordination
- **Task tool**: PRIMARY mechanism - spawns subagents for all workstreams
- **TodoWrite**: Hierarchical task breakdown at Epic → Story → Task → Subtask levels
- **Read/Grep/Glob**: Initial analysis (often delegated to Explore subagent)
- **Direct file tools**: Only for spawn's own coordination needs (not delegated work)
- **Bash**: System-level operations when needed for orchestration

## Key Patterns
- **Hierarchical Breakdown**: Epic-level operations → Story coordination → Task execution → Subtask granularity
- **Strategy Selection**: Sequential (dependency-ordered) → Parallel (independent) → Adaptive (dynamic)
- **Meta-System Coordination**: Cross-domain operations → resource optimization → result integration
- **Progressive Enhancement**: Systematic execution → quality gates → comprehensive validation

## Examples

### Complex Feature Implementation
```
/orchestrate:spawn "implement user authentication system"
# Breakdown: Database design → Backend API → Frontend UI → Testing
# Coordinates across multiple domains with dependency management
```

### Large-Scale System Operation
```
/orchestrate:spawn "migrate legacy monolith to microservices" --strategy adaptive --depth deep
# Enterprise-scale operation with sophisticated orchestration
# Adaptive coordination based on operation characteristics
```

### Cross-Domain Infrastructure
```
/orchestrate:spawn "establish CI/CD pipeline with security scanning"
# System-wide infrastructure operation spanning DevOps, Security, Quality domains
# Parallel execution of independent components with validation gates
```

## Boundaries

**Will:**
- Decompose complex multi-domain operations into coordinated task hierarchies
- Provide intelligent orchestration with parallel and sequential coordination strategies
- Execute meta-system operations beyond standard command capabilities

**Will Not:**
- Replace domain-specific commands for simple operations
- Override user coordination preferences or execution strategies
- Execute operations without proper dependency analysis and validation
