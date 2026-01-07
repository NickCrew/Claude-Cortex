# Reference: code

# /analyze:code - Code Analysis and Quality Assessment

## Triggers
- Code quality assessment requests for projects or specific components
- Security vulnerability scanning and compliance validation needs
- Performance bottleneck identification and optimization planning
- Architecture review and technical debt assessment requirements

## Usage
```
/analyze:code [target] [--focus quality|security|performance|architecture] [--depth quick|deep|ultra] [--reasoning-profile default|security|performance|architecture|data|testing] [--format text|json|report]
```

## Behavioral Flow
1. **Discover**: Categorize source files using language detection and project analysis
2. **Scan**: Apply domain-specific analysis techniques and pattern matching
3. **Evaluate**: Generate prioritized findings with severity ratings and impact assessment
4. **Recommend**: Create actionable recommendations with implementation guidance
5. **Report**: Present comprehensive analysis with metrics and improvement roadmap

Key behaviors:
- Multi-domain analysis combining static analysis and heuristic evaluation
- Intelligent file discovery and language-specific pattern recognition
- Severity-based prioritization of findings and recommendations
- Comprehensive reporting with metrics, trends, and actionable insights

## Personas (Thinking Modes)
- **analyzer**: Deep analysis, pattern recognition, systematic evaluation
- **architect**: System design understanding, architecture patterns, scalability thinking
- **security-specialist**: Security-first mindset, threat awareness, vulnerability detection
- **performance-engineer**: Performance optimization, bottleneck identification, efficiency focus

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Deep analysis (--depth deep or ultra)
- ✅ Multi-domain analysis (multiple focus areas)
- ✅ Large codebase (>20 files)
- ✅ Security or performance focused analysis requiring specialized expertise

**Available subagents**:
- **code-reviewer**: Quality, maintainability, architecture analysis
- **security-auditor**: Security vulnerabilities, threat modeling, compliance
- **Explore**: Codebase discovery, pattern identification, dependency analysis

**Delegation strategy for comprehensive analysis**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Discover and categorize project structure</description>
  <prompt>
    Analyze project structure:
    - File organization and patterns
    - Language distribution
    - Key components and dependencies
    - Architecture patterns
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Quality and architecture analysis</description>
  <prompt>
    Multi-domain analysis focusing on: [quality|performance|architecture]
    - Code smells and anti-patterns
    - Best practices compliance
    - Performance considerations
    Reasoning profile: [default|performance|architecture]
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>security-auditor</subagent_type>
  <description>Security vulnerability assessment</description>
  <prompt>
    Security-focused analysis:
    - OWASP Top 10 patterns
    - Authentication/authorization
    - Data protection
    Reasoning profile: security
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Quick quality check (--depth quick, small codebase)
- ❌ Single file analysis
- ❌ Simple pattern searches

## Tool Coordination
- **Task tool**: Delegates to subagents for deep multi-domain analysis
- **Glob**: File discovery (direct for quick, by subagent for deep)
- **Grep**: Pattern analysis (direct for quick, by subagent for deep)
- **Read**: Source code inspection (direct for quick, by subagent for deep)
- **Bash**: External analysis tools (by subagent when needed)
- **Write**: Report generation

## Reasoning Profiles

### default
- Balanced analysis across all focus domains
- Standard severity assessment and prioritization
- Comprehensive reporting with actionable insights

### security
- Deep threat modeling and attack vector analysis
- OWASP Top 10 pattern matching and CVE correlation
- Enhanced severity scoring for security vulnerabilities
- Compliance validation (GDPR, SOC2, PCI-DSS considerations)
- Enables: Context7 for security best practices, Sequential for threat chains

### performance
- Algorithmic complexity analysis (Big-O notation)
- Resource usage profiling and bottleneck identification
- Scalability assessment and load testing recommendations
- Database query optimization and N+1 detection
- Enables: Sequential for performance impact chains

### architecture
- System design pattern recognition and anti-pattern detection
- Service boundary analysis and microservices decomposition strategies
- Dependency graph analysis with circular dependency detection
- API design evaluation and REST/GraphQL best practices
- Scalability and resilience architecture assessment
- Event-driven architecture and message flow analysis
- Enables: Context7 for api-design-patterns, microservices-patterns skills
- Enables: Sequential for dependency chain analysis

### data
- Database schema design analysis and normalization assessment
- Query performance optimization and index recommendations
- Data flow mapping and ETL pipeline evaluation
- CQRS and Event Sourcing pattern application
- Data consistency and integrity validation
- Migration strategy assessment for schema changes
- Enables: Context7 for database-design-patterns, cqrs-event-sourcing skills
- Enables: Sequential for data flow impact analysis

### testing
- Test coverage gap identification and quality assessment
- Test pattern analysis (unit, integration, e2e structure)
- Property-based testing opportunity detection
- Mock and stub usage evaluation
- Test maintainability and flakiness analysis
- TDD/BDD pattern compliance verification
- Enables: Context7 for python-testing-patterns skill
- Enables: Sequential for test dependency analysis

## Key Patterns
- **Domain Analysis**: Quality/Security/Performance/Architecture → specialized assessment
- **Pattern Recognition**: Language detection → appropriate analysis techniques
- **Severity Assessment**: Issue classification → prioritized recommendations
- **Report Generation**: Analysis results → structured documentation
- **Profile Specialization**: Reasoning profile → domain-specific depth and tool activation

## Examples

### Comprehensive Project Analysis
```
/analyze:code
# Multi-domain analysis of entire project
# Generates comprehensive report with key findings and roadmap
```

### Focused Security Assessment
```
/analyze:code src/auth --focus security --depth deep --reasoning-profile security
# Deep security analysis of authentication components
# Enables threat modeling, OWASP patterns, CVE correlation
# Vulnerability assessment with detailed remediation guidance
```

### Performance Optimization Analysis
```
/analyze:code --focus performance --depth ultra --reasoning-profile performance --format report
# Performance bottleneck identification with deep analysis
# Algorithmic complexity analysis, resource profiling
# Generates comprehensive report with optimization recommendations
```

### Quick Quality Check
```
/analyze:code src/components --focus quality --depth quick
# Rapid quality assessment of component directory
# Identifies code smells and maintainability issues
```

## Boundaries

**Will:**
- Perform comprehensive static code analysis across multiple domains
- Generate severity-rated findings with actionable recommendations
- Provide detailed reports with metrics and improvement guidance

**Will Not:**
- Execute dynamic analysis requiring code compilation or runtime
- Modify source code or apply fixes without explicit user consent
- Analyze external dependencies beyond import and usage patterns
