# Reference: estimate

# /analyze:estimate - Development Estimation

## Triggers
- Development planning requiring time, effort, or complexity estimates
- Project scoping and resource allocation decisions
- Feature breakdown needing systematic estimation methodology
- Risk assessment and confidence interval analysis requirements

## Usage
```
/analyze:estimate [target] [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]
```

## Behavioral Flow
1. **Analyze**: Examine scope, complexity factors, dependencies, and framework patterns
2. **Calculate**: Apply estimation methodology with historical benchmarks and complexity scoring
3. **Validate**: Cross-reference estimates with project patterns and domain expertise
4. **Present**: Provide detailed breakdown with confidence intervals and risk assessment
5. **Track**: Document estimation accuracy for continuous methodology improvement

Key behaviors:
- Multi-persona coordination (architect, performance, project-manager) based on estimation scope
- Sequential MCP integration for systematic analysis and complexity assessment
- Context7 MCP integration for framework-specific patterns and historical benchmarks
- Intelligent breakdown analysis with confidence intervals and risk factors

## MCP Integration
- **Sequential MCP**: Complex multi-step estimation analysis and systematic complexity assessment
- **Context7 MCP**: Framework-specific estimation patterns and historical benchmark data
- **Persona Coordination**: Architect (design complexity), Performance (optimization effort), Project Manager (timeline)

## Personas (Thinking Modes)
- **architect**: Design complexity assessment, component organization, integration points
- **performance-engineer**: Performance optimization effort, technical debt evaluation
- **project-manager**: Timeline estimation, resource allocation, risk assessment

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Large project estimation (>10 components)
- ✅ Requires deep codebase analysis
- ✅ Multi-domain complexity assessment
- ✅ Detailed breakdown requested (--breakdown flag)

**Available subagents**:
- **Explore**: Codebase complexity analysis, pattern discovery, scope evaluation
- **general-purpose**: Estimation calculation, breakdown generation, risk assessment

**Delegation strategy for comprehensive estimation**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Analyze codebase for estimation context</description>
  <prompt>
    Explore for estimation:
    - Component complexity
    - Dependencies and integrations
    - Framework patterns
    - Existing implementations
    - Technical debt factors
    Thoroughness: medium
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Generate detailed estimation</description>
  <prompt>
    Estimate: [target]
    Type: [time|effort|complexity]
    Unit: [hours|days|weeks]
    - Apply architect + performance + PM personas
    - Use Sequential for systematic analysis
    - Use Context7 for framework benchmarks
    - Provide confidence intervals
    - Include risk factors
    - Generate breakdown if requested
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple task estimation (<5 steps)
- ❌ Quick complexity score (no detailed analysis)
- ❌ Rough estimate (order of magnitude)

## Tool Coordination
- **Task tool**: Delegates for large/complex estimation requiring codebase analysis
- **Read/Grep/Glob**: Codebase analysis (direct for simple, by subagent for complex)
- **TodoWrite**: Estimation breakdown tracking
- **Bash**: Project analysis (by subagent when needed)
- **Sequential MCP**: Systematic estimation methodology
- **Context7 MCP**: Framework-specific benchmarks

## Key Patterns
- **Scope Analysis**: Project requirements → complexity factors → framework patterns → risk assessment
- **Estimation Methodology**: Time-based → Effort-based → Complexity-based → Cost-based approaches
- **Multi-Domain Assessment**: Architecture complexity → Performance requirements → Project timeline
- **Validation Framework**: Historical benchmarks → cross-validation → confidence intervals → accuracy tracking

## Examples

### Feature Development Estimation
```
/analyze:estimate "user authentication system" --type time --unit days --breakdown
# Systematic analysis: Database design (2 days) + Backend API (3 days) + Frontend UI (2 days) + Testing (1 day)
# Total: 8 days with 85% confidence interval
```

### Project Complexity Assessment
```
/analyze:estimate "migrate monolith to microservices" --type complexity --breakdown
# Architecture complexity analysis with risk factors and dependency mapping
# Multi-persona coordination for comprehensive assessment
```

### Performance Optimization Effort
```
/analyze:estimate "optimize application performance" --type effort --unit hours
# Performance persona analysis with benchmark comparisons
# Effort breakdown by optimization category and expected impact
```

## Boundaries

**Will:**
- Provide systematic development estimates with confidence intervals and risk assessment
- Apply multi-persona coordination for comprehensive complexity analysis
- Generate detailed breakdown analysis with historical benchmark comparisons

**Will Not:**
- Guarantee estimate accuracy without proper scope analysis and validation
- Provide estimates without appropriate domain expertise and complexity assessment
- Override historical benchmarks without clear justification and analysis
