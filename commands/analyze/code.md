---
name: code
description: "Comprehensive code analysis across quality, security, performance, and architecture domains"
category: utility
complexity: basic
mcp-servers: []
personas: []
---

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

## Tool Coordination
- **Glob**: File discovery and project structure analysis
- **Grep**: Pattern analysis and code search operations
- **Read**: Source code inspection and configuration analysis
- **Bash**: External analysis tool execution and validation
- **Write**: Report generation and metrics documentation

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
