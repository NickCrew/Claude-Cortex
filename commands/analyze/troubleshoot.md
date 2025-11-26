---
name: troubleshoot
description: "Diagnose and resolve issues in code, builds, deployments, and system behavior"
category: utility
complexity: basic
mcp-servers: [sequential]
personas: [debugger, system-analyst, devops-engineer]
subagents: [general-purpose, Explore]
---

# /analyze:troubleshoot - Issue Diagnosis and Resolution

## Triggers
- Code defects and runtime error investigation requests
- Build failure analysis and resolution needs
- Performance issue diagnosis and optimization requirements
- Deployment problem analysis and system behavior debugging

## Usage
```
/analyze:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]
```

## Behavioral Flow
1. **Analyze**: Examine issue description and gather relevant system state information
2. **Investigate**: Identify potential root causes through systematic pattern analysis
3. **Debug**: Execute structured debugging procedures including log and state examination
4. **Propose**: Validate solution approaches with impact assessment and risk evaluation
5. **Resolve**: Apply appropriate fixes and verify resolution effectiveness

Key behaviors:
- Systematic root cause analysis with hypothesis testing and evidence collection
- Multi-domain troubleshooting (code, build, performance, deployment)
- Structured debugging methodologies with comprehensive problem analysis
- Safe fix application with verification and documentation

## Personas (Thinking Modes)
- **debugger**: Systematic debugging, hypothesis testing, root cause analysis
- **system-analyst**: System behavior understanding, pattern recognition, integration analysis
- **devops-engineer**: Deployment expertise, environment configuration, infrastructure knowledge

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Complex multi-component issues
- ✅ Requires deep codebase exploration
- ✅ Performance profiling needed
- ✅ System-wide debugging (>5 components)

**Available subagents**:
- **Explore**: Codebase investigation, pattern discovery, dependency analysis
- **general-purpose**: Issue diagnosis, fix implementation, validation

**Delegation strategy for complex troubleshooting**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Investigate codebase for issue context</description>
  <prompt>
    Explore for troubleshooting:
    - Related components
    - Error propagation paths
    - Dependency relationships
    - Similar patterns
    Thoroughness: medium
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Diagnose and resolve issue</description>
  <prompt>
    Issue: [description]
    Type: [bug|build|performance|deployment]
    - Systematic root cause analysis
    - Hypothesis testing
    - Apply fix (if --fix flag)
    - Validation
    Use Sequential for structured debugging.
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple bug fix (clear error message, single file)
- ❌ Configuration issue (obvious solution)
- ❌ Log analysis only (no code changes)

## Tool Coordination
- **Task tool**: Delegates for complex multi-component issues
- **Read**: Log analysis (direct for simple, by subagent for complex)
- **Bash**: Diagnostics (direct for simple, by subagent for complex)
- **Grep**: Error patterns (direct for simple, by subagent for complex)
- **Write**: Reports (direct)
- **Sequential MCP**: Structured debugging reasoning

## Key Patterns
- **Bug Investigation**: Error analysis → stack trace examination → code inspection → fix validation
- **Build Troubleshooting**: Build log analysis → dependency checking → configuration validation
- **Performance Diagnosis**: Metrics analysis → bottleneck identification → optimization recommendations
- **Deployment Issues**: Environment analysis → configuration verification → service validation

## Examples

### Code Bug Investigation
```
/analyze:troubleshoot "Null pointer exception in user service" --type bug --trace
# Systematic analysis of error context and stack traces
# Identifies root cause and provides targeted fix recommendations
```

### Build Failure Analysis
```
/analyze:troubleshoot "TypeScript compilation errors" --type build --fix
# Analyzes build logs and TypeScript configuration
# Automatically applies safe fixes for common compilation issues
```

### Performance Issue Diagnosis
```
/analyze:troubleshoot "API response times degraded" --type performance
# Performance metrics analysis and bottleneck identification
# Provides optimization recommendations and monitoring guidance
```

### Deployment Problem Resolution
```
/analyze:troubleshoot "Service not starting in production" --type deployment --trace
# Environment and configuration analysis
# Systematic verification of deployment requirements and dependencies
```

## Boundaries

**Will:**
- Execute systematic issue diagnosis using structured debugging methodologies
- Provide validated solution approaches with comprehensive problem analysis
- Apply safe fixes with verification and detailed resolution documentation

**Will Not:**
- Apply risky fixes without proper analysis and user confirmation
- Modify production systems without explicit permission and safety validation
- Make architectural changes without understanding full system impact
