# Reference: build

# /dev:build - Project Building and Packaging

## Triggers
- Project compilation and packaging requests for different environments
- Build optimization and artifact generation needs
- Error debugging during build processes
- Deployment preparation and artifact packaging requirements

## Usage
```
/dev:build [target] [--type dev|prod|test] [--clean] [--optimize] [--verbose]
```

## Behavioral Flow
1. **Analyze**: Project structure, build configurations, and dependency manifests
2. **Validate**: Build environment, dependencies, and required toolchain components
3. **Execute**: Build process with real-time monitoring and error detection
4. **Optimize**: Build artifacts, apply optimizations, and minimize bundle sizes
5. **Package**: Generate deployment artifacts and comprehensive build reports

Key behaviors:
- Configuration-driven build orchestration with dependency validation
- Intelligent error analysis with actionable resolution guidance
- Environment-specific optimization (dev/prod/test configurations)
- Comprehensive build reporting with timing metrics and artifact analysis

## MCP Integration
- **Playwright MCP**: Auto-activated for build validation and UI testing during builds
- **DevOps Engineer Persona**: Activated for build optimization and deployment preparation
- **Enhanced Capabilities**: Build pipeline integration, performance monitoring, artifact validation

## Personas (Thinking Modes)
- **devops-engineer**: Build pipeline optimization, deployment preparation, artifact management
- **performance-engineer**: Build performance, optimization strategies, bundle analysis

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Build failure analysis (complex error diagnosis)
- ✅ Build optimization (--optimize flag with analysis)
- ✅ Multi-component builds (>3 targets)
- ✅ Validation with Playwright (--validate flag)

**Available subagents**:
- **general-purpose**: Complex error analysis, optimization implementation

**Delegation strategy for build issues**:
```xml
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Analyze build failure and optimize</description>
  <prompt>
    Build failed. Analyze errors and apply fixes:
    - Parse build logs
    - Identify root cause
    - Apply appropriate fixes
    - Re-run build
    - Generate report
    DevOps engineer thinking for deployment.
  </prompt>
</invoke>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple build execution (standard dev/prod builds)
- ❌ Clean builds (no analysis needed)
- ❌ Quick artifact generation

## Tool Coordination
- **Task tool**: Delegates to subagent for complex error analysis and optimization
- **Bash**: Build execution (direct)
- **Read**: Configuration analysis (direct)
- **Grep**: Error parsing (direct for simple, by subagent for complex)
- **Glob**: Artifact discovery (direct)
- **Write**: Build reports (direct)

## Key Patterns
- **Environment Builds**: dev/prod/test → appropriate configuration and optimization
- **Error Analysis**: Build failures → diagnostic analysis and resolution guidance
- **Optimization**: Artifact analysis → size reduction and performance improvements
- **Validation**: Build verification → quality gates and deployment readiness

## Examples

### Standard Project Build
```
/dev:build
# Builds entire project using default configuration
# Generates artifacts and comprehensive build report
```

### Production Optimization Build
```
/dev:build --type prod --clean --optimize
# Clean production build with advanced optimizations
# Minification, tree-shaking, and deployment preparation
```

### Targeted Component Build
```
/dev:build frontend --verbose
# Builds specific project component with detailed output
# Real-time progress monitoring and diagnostic information
```

### Development Build with Validation
```
/dev:build --type dev --validate
# Development build with Playwright validation
# UI testing and build verification integration
```

## Boundaries

**Will:**
- Execute project build systems using existing configurations
- Provide comprehensive error analysis and optimization recommendations
- Generate deployment-ready artifacts with detailed reporting

**Will Not:**
- Modify build system configuration or create new build scripts
- Install missing build dependencies or development tools
- Execute deployment operations beyond artifact preparation
