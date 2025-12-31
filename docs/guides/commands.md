---
layout: default
title: Command Reference
nav_order: 3
---

# Slash Commands API Reference

Complete API documentation for all slash commands in the Cortex Plugin.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Command Categories](#command-categories)
  - [Collaboration Commands](#collaboration-commands)
  - [Analyze Commands](#analyze-commands)
  - [Deploy Commands](#deploy-commands)
  - [Design Commands](#design-commands)
  - [Dev Commands](#dev-commands)
  - [Docs Commands](#docs-commands)
  - [Orchestrate Commands](#orchestrate-commands)
  - [Quality Commands](#quality-commands)
  - [Session Commands](#session-commands)
  - [Test Commands](#test-commands)
  - [Tools Commands](#tools-commands)
- [Flag Reference](#flag-reference)
- [MCP Integration Patterns](#mcp-integration-patterns)
- [Common Workflows](#common-workflows)

---

## Quick Reference

### By Use Case

**Code Quality & Analysis**

- `/analyze:code` - Comprehensive code analysis
- `/analyze:security-scan` - Security vulnerability assessment
- `/dev:code-review` - Code quality review
- `/quality:cleanup` - Dead code removal and cleanup
- `/quality:improve` - Systematic code improvements

**Development Workflow**

- `/dev:implement` - Feature implementation
- `/dev:build` - Project building and packaging
- `/dev:test` - Test execution with coverage
- `/dev:git` - Git operations with smart commits
- `/test:generate-tests` - Test suite generation

**Documentation & Planning**

- `/ctx:brainstorm` - Structured Supersaiyan ideation *(new)*
- `/ctx:plan` - Multi-stream planning + Task TUI sync *(new)*
- `/ctx:execute-plan` - Execute plans with verification *(new)*
- `/docs:generate` - Focused documentation generation
- `/docs:index` - Project documentation indexing
- `/design:system` - System architecture design
- `/design:workflow` - Implementation workflow generation
- `/analyze:explain` - Code and concept explanations

**Project Management**

- `/orchestrate:brainstorm` - Requirements discovery
- `/orchestrate:task` - Task management and delegation
- `/orchestrate:spawn` - Complex task orchestration
- `/analyze:estimate` - Development estimation
- `/analyze:troubleshoot` - Issue diagnosis and resolution
- `/reasoning:adjust` - Dynamic reasoning depth control
- `/reasoning:budget` - Thinking budget control (128K extended mode)
- `/reasoning:metrics` - Reasoning effectiveness analytics

**Session Management**

- `/session:load` - Load project context
- `/session:save` - Save session context
- `/session:reflect` - Task reflection and validation

---

## Command Categories

## Collaboration Commands

### /ctx:brainstorm

**Description**: Supersaiyan-aligned brainstorming flow (adapted from Superpowers). Captures goals, constraints, assets, and at least three solution options before coding.

**Usage**:

```bash
/ctx:brainstorm [topic] [--constraints ...]
```

**Flow**:

1. Load `modes/Super_Saiyan.md`.
2. Summarize objectives, success signals, constraints, and existing assets.
3. List ≥3 options with verification + risk notes.
4. Seed Task TUI items or hand off to `/ctx:plan`.

### /ctx:plan

**Description**: Converts brainstorm output into multi-stream plans, with explicit Definition of Done and verification per task.

**Usage**:

```bash
/ctx:plan [summary] [--streams n] [--save]
```

**Flow**:

1. Restate objective and constraints.
2. Break work into streams; map required agents/modes/rules.
3. Define tasks + verification steps and sync the Task TUI.
4. Optionally save plan under `docs/plans/`.

### /ctx:execute-plan

**Description**: Drives the plan through orchestration view + Task TUI, ensuring verification and status updates.

**Usage**:

```bash
/ctx:execute-plan [plan-link] [--sync-tasks] [--verify]
```

**Flow**:

1. Sync/validate tasks for each plan bullet.
2. Toggle required modes/rules.
3. Loop: pick task → implement → verify → update.
4. Publish status, close tasks, capture retrospective notes.

---

## Skill Commands

### /ctx:skill

**Description**: Directly invoke a skill from the skill library.

**Usage**:

```bash
/ctx:skill <skill-name>
```

**Behavioral Flow**:

1. **Load Skill**: The specified skill is loaded into the context.
2. **Execute Skill**: The instructions within the skill are executed.

**Note**: While many skills are activated automatically based on keywords in your request, you can use this command to directly invoke a skill when you know which one you need. For a complete list of available skills, see the [Agent Skills Guide](skills.md).

---

## Analyze Commands

### /analyze:code

**Description**: Comprehensive code analysis across quality, security, performance, and architecture domains

**Category**: utility | **Complexity**: basic

**Triggers**:

- Code quality assessment requests for projects or specific components
- Security vulnerability scanning and compliance validation needs
- Performance bottleneck identification and optimization planning
- Architecture review and technical debt assessment requirements

**Usage**:

```bash
/analyze:code [target] [--focus quality|security|performance|architecture] [--depth quick|deep|ultra] [--reasoning-profile default|security|performance] [--format text|json|report]
```

**Behavioral Flow**:

1. **Discover**: Categorize source files using language detection and project analysis
2. **Scan**: Apply domain-specific analysis techniques and pattern matching
3. **Evaluate**: Generate prioritized findings with severity ratings and impact assessment
4. **Recommend**: Create actionable recommendations with implementation guidance
5. **Report**: Present comprehensive analysis with metrics and improvement roadmap

**Tool Coordination**:

- **Glob**: File discovery and project structure analysis
- **Grep**: Pattern analysis and code search operations
- **Read**: Source code inspection and configuration analysis
- **Bash**: External analysis tool execution and validation
- **Write**: Report generation and metrics documentation

**Reasoning Profiles**:

**default**

- Balanced analysis across all focus domains
- Standard severity assessment and prioritization
- Comprehensive reporting with actionable insights

**security**

- Deep threat modeling and attack vector analysis
- OWASP Top 10 pattern matching and CVE correlation
- Enhanced severity scoring for security vulnerabilities
- Compliance validation (GDPR, SOC2, PCI-DSS considerations)
- Enables: Context7 for security best practices, Sequential for threat chains

**performance**

- Algorithmic complexity analysis (Big-O notation)
- Resource usage profiling and bottleneck identification
- Scalability assessment and load testing recommendations
- Database query optimization and N+1 detection
- Enables: Sequential for performance impact chains

**Key Patterns**:

- **Domain Analysis**: Quality/Security/Performance/Architecture → specialized assessment
- **Pattern Recognition**: Language detection → appropriate analysis techniques
- **Severity Assessment**: Issue classification → prioritized recommendations
- **Report Generation**: Analysis results → structured documentation
- **Profile Specialization**: Reasoning profile → domain-specific depth and tool activation

**Examples**:

```bash
# Comprehensive Project Analysis
/analyze:code
# Multi-domain analysis of entire project
# Generates comprehensive report with key findings and roadmap

# Focused Security Assessment
/analyze:code src/auth --focus security --depth deep
# Deep security analysis of authentication components
# Vulnerability assessment with detailed remediation guidance

# Performance Optimization Analysis
/analyze:code --focus performance --format report
# Performance bottleneck identification
# Generates HTML report with optimization recommendations

# Quick Quality Check
/analyze:code src/components --focus quality --depth quick
# Rapid quality assessment of component directory
# Identifies code smells and maintainability issues
```

**Boundaries**:

**Will**:

- Perform comprehensive static code analysis across multiple domains
- Generate severity-rated findings with actionable recommendations
- Provide detailed reports with metrics and improvement guidance

**Will Not**:

- Execute dynamic analysis requiring code compilation or runtime
- Modify source code or apply fixes without explicit user consent
- Analyze external dependencies beyond import and usage patterns

**Related Commands**: `/analyze:security-scan`, `/dev:code-review`, `/quality:improve`

---

### /analyze:estimate

**Description**: Provide development estimates for tasks, features, or projects with intelligent analysis

**Category**: special | **Complexity**: standard

**MCP Servers**: sequential, context7

**Personas**: architect, performance, project-manager

**Triggers**:

- Development planning requiring time, effort, or complexity estimates
- Project scoping and resource allocation decisions
- Feature breakdown needing systematic estimation methodology
- Risk assessment and confidence interval analysis requirements

**Usage**:

```bash
/analyze:estimate [target] [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]
```

**Behavioral Flow**:

1. **Analyze**: Examine scope, complexity factors, dependencies, and framework patterns
2. **Calculate**: Apply estimation methodology with historical benchmarks and complexity scoring
3. **Validate**: Cross-reference estimates with project patterns and domain expertise
4. **Present**: Provide detailed breakdown with confidence intervals and risk assessment
5. **Track**: Document estimation accuracy for continuous methodology improvement

**MCP Integration**:

- **Sequential MCP**: Complex multi-step estimation analysis and systematic complexity assessment
- **Context7 MCP**: Framework-specific estimation patterns and historical benchmark data
- **Persona Coordination**: Architect (design complexity), Performance (optimization effort), Project Manager (timeline)

**Tool Coordination**:

- **Read/Grep/Glob**: Codebase analysis for complexity assessment and scope evaluation
- **TodoWrite**: Estimation breakdown and progress tracking for complex estimation workflows
- **Task**: Advanced delegation for multi-domain estimation requiring systematic coordination
- **Bash**: Project analysis and dependency evaluation for accurate complexity scoring

**Key Patterns**:

- **Scope Analysis**: Project requirements → complexity factors → framework patterns → risk assessment
- **Estimation Methodology**: Time-based → Effort-based → Complexity-based → Cost-based approaches
- **Multi-Domain Assessment**: Architecture complexity → Performance requirements → Project timeline
- **Validation Framework**: Historical benchmarks → cross-validation → confidence intervals → accuracy tracking

**Examples**:

```bash
# Feature Development Estimation
/analyze:estimate "user authentication system" --type time --unit days --breakdown
# Systematic analysis: Database design (2 days) + Backend API (3 days) + Frontend UI (2 days) + Testing (1 day)
# Total: 8 days with 85% confidence interval

# Project Complexity Assessment
/analyze:estimate "migrate monolith to microservices" --type complexity --breakdown
# Architecture complexity analysis with risk factors and dependency mapping
# Multi-persona coordination for comprehensive assessment

# Performance Optimization Effort
/analyze:estimate "optimize application performance" --type effort --unit hours
# Performance persona analysis with benchmark comparisons
# Effort breakdown by optimization category and expected impact
```

**Boundaries**:

**Will**:

- Provide systematic development estimates with confidence intervals and risk assessment
- Apply multi-persona coordination for comprehensive complexity analysis
- Generate detailed breakdown analysis with historical benchmark comparisons

**Will Not**:

- Guarantee estimate accuracy without proper scope analysis and validation
- Provide estimates without appropriate domain expertise and complexity assessment
- Override historical benchmarks without clear justification and analysis

**Related Commands**: `/design:workflow`, `/orchestrate:task`, `/orchestrate:brainstorm`

---

### /analyze:explain

**Description**: Provide clear explanations of code, concepts, and system behavior with educational clarity

**Category**: workflow | **Complexity**: standard

**MCP Servers**: sequential, context7

**Personas**: educator, architect, security

**Triggers**:

- Code understanding and documentation requests for complex functionality
- System behavior explanation needs for architectural components
- Educational content generation for knowledge transfer
- Framework-specific concept clarification requirements

**Usage**:

```bash
/analyze:explain [target] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]
```

**Behavioral Flow**:

1. **Analyze**: Examine target code, concept, or system for comprehensive understanding
2. **Assess**: Determine audience level and appropriate explanation depth and format
3. **Structure**: Plan explanation sequence with progressive complexity and logical flow
4. **Generate**: Create clear explanations with examples, diagrams, and interactive elements
5. **Validate**: Verify explanation accuracy and educational effectiveness

**MCP Integration**:

- **Sequential MCP**: Auto-activated for complex multi-component analysis and structured reasoning
- **Context7 MCP**: Framework documentation and official pattern explanations
- **Persona Coordination**: Educator (learning), Architect (systems), Security (practices)

**Tool Coordination**:

- **Read/Grep/Glob**: Code analysis and pattern identification for explanation content
- **TodoWrite**: Progress tracking for complex multi-part explanations
- **Task**: Delegation for comprehensive explanation workflows requiring systematic breakdown

**Key Patterns**:

- **Progressive Learning**: Basic concepts → intermediate details → advanced implementation
- **Framework Integration**: Context7 documentation → accurate official patterns and practices
- **Multi-Domain Analysis**: Technical accuracy + educational clarity + security awareness
- **Interactive Explanation**: Static content → examples → interactive exploration

**Examples**:

```bash
# Basic Code Explanation
/analyze:explain authentication.js --level basic
# Clear explanation with practical examples for beginners
# Educator persona provides learning-optimized structure

# Framework Concept Explanation
/analyze:explain react-hooks --level intermediate --context react
# Context7 integration for official React documentation patterns
# Structured explanation with progressive complexity

# System Architecture Explanation
/analyze:explain microservices-system --level advanced --format interactive
# Architect persona explains system design and patterns
# Interactive exploration with Sequential analysis breakdown

# Security Concept Explanation
/analyze:explain jwt-authentication --context security --level basic
# Security persona explains authentication concepts and best practices
# Framework-agnostic security principles with practical examples
```

**Boundaries**:

**Will**:

- Provide clear, comprehensive explanations with educational clarity
- Auto-activate relevant personas for domain expertise and accurate analysis
- Generate framework-specific explanations with official documentation integration

**Will Not**:

- Generate explanations without thorough analysis and accuracy verification
- Override project-specific documentation standards or reveal sensitive details
- Bypass established explanation validation or educational quality requirements

**Related Commands**: `/docs:generate`, `/docs:index`, `/analyze:code`

---

### /analyze:security-scan

**Description**: Comprehensive security vulnerability assessment

**Category**: analysis

**Agents**: security-auditor

**Triggers**:

- Security audit requests
- Pre-release security checks
- Compliance requirements
- Vulnerability reports

**Usage**:

```bash
/analyze:security-scan [path] [--standard OWASP|GDPR|SOC2|HIPAA]
```

**Security Analysis Process**:

1. **Threat Modeling**
   - Identify potential attack vectors
   - Map trust boundaries
   - Analyze data flow
   - Assess risk levels
   - Create threat matrix

2. **Vulnerability Scanning**
   - Dependency vulnerability check
   - Static code analysis
   - Secret scanning
   - Configuration review
   - API security assessment

3. **Code Security Review**
   - Input validation analysis
   - Output encoding checks
   - Authentication logic review
   - Authorization verification
   - Session management audit
   - Cryptography usage validation

4. **Penetration Testing**
   - SQL injection testing
   - XSS attack simulation
   - CSRF vulnerability check
   - Authentication bypass attempts
   - Privilege escalation testing
   - API abuse scenarios

5. **Compliance Validation**
   - OWASP Top 10 compliance
   - GDPR data protection
   - SOC 2 security controls
   - HIPAA requirements (if applicable)
   - Industry-specific standards

**Security Checks**:

**Authentication & Authorization**

- Password security
- Session management
- Token validation
- Access control
- Permission boundaries

**Data Protection**

- Encryption at rest
- Encryption in transit
- Data sanitization
- PII handling
- Secure storage

**API Security**

- Rate limiting
- Input validation
- Authentication
- CORS configuration
- Error handling

**Infrastructure**

- Security headers
- SSL/TLS configuration
- Firewall rules
- Network segmentation
- Logging and monitoring

**Severity Levels**:

- **Critical**: Immediate fix required
- **High**: Fix within 7 days
- **Medium**: Fix within 30 days
- **Low**: Fix when possible
- **Informational**: Best practice recommendations

**Output Format**:

**Executive Summary**

- Overall security posture
- Critical findings count
- Risk assessment
- Compliance status

**Detailed Findings**

- Vulnerability description
- Affected components
- Severity rating
- Remediation steps
- Code examples

**Compliance Report**

- Standard requirements
- Compliance gaps
- Recommendations
- Implementation timeline

**Example**:

```bash
/analyze:security-scan src/auth --standard OWASP
```

**Boundaries**:

**Will**:

- Perform comprehensive security analysis following industry standards
- Identify vulnerabilities with detailed remediation guidance
- Generate compliance reports for specified security frameworks

**Will Not**:

- Perform actual penetration testing on production systems
- Automatically fix security vulnerabilities without explicit authorization
- Guarantee 100% security coverage (security is defense-in-depth)

**Related Commands**: `/analyze:code`, `/dev:code-review`, `/quality:improve`

---

### /analyze:troubleshoot

**Description**: Diagnose and resolve issues in code, builds, deployments, and system behavior

**Category**: utility | **Complexity**: basic

**Triggers**:

- Code defects and runtime error investigation requests
- Build failure analysis and resolution needs
- Performance issue diagnosis and optimization requirements
- Deployment problem analysis and system behavior debugging

**Usage**:

```bash
/analyze:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]
```

**Behavioral Flow**:

1. **Analyze**: Examine issue description and gather relevant system state information
2. **Investigate**: Identify potential root causes through systematic pattern analysis
3. **Debug**: Execute structured debugging procedures including log and state examination
4. **Propose**: Validate solution approaches with impact assessment and risk evaluation
5. **Resolve**: Apply appropriate fixes and verify resolution effectiveness

**Tool Coordination**:

- **Read**: Log analysis and system state examination
- **Bash**: Diagnostic command execution and system investigation
- **Grep**: Error pattern detection and log analysis
- **Write**: Diagnostic reports and resolution documentation

**Key Patterns**:

- **Bug Investigation**: Error analysis → stack trace examination → code inspection → fix validation
- **Build Troubleshooting**: Build log analysis → dependency checking → configuration validation
- **Performance Diagnosis**: Metrics analysis → bottleneck identification → optimization recommendations
- **Deployment Issues**: Environment analysis → configuration verification → service validation

**Examples**:

```bash
# Code Bug Investigation
/analyze:troubleshoot "Null pointer exception in user service" --type bug --trace
# Systematic analysis of error context and stack traces
# Identifies root cause and provides targeted fix recommendations

# Build Failure Analysis
/analyze:troubleshoot "TypeScript compilation errors" --type build --fix
# Analyzes build logs and TypeScript configuration
# Automatically applies safe fixes for common compilation issues

# Performance Issue Diagnosis
/analyze:troubleshoot "API response times degraded" --type performance
# Performance metrics analysis and bottleneck identification
# Provides optimization recommendations and monitoring guidance

# Deployment Problem Resolution
/analyze:troubleshoot "Service not starting in production" --type deployment --trace
# Environment and configuration analysis
# Systematic verification of deployment requirements and dependencies
```

**Boundaries**:

**Will**:

- Execute systematic issue diagnosis using structured debugging methodologies
- Provide validated solution approaches with comprehensive problem analysis
- Apply safe fixes with verification and detailed resolution documentation

**Will Not**:

- Apply risky fixes without proper analysis and user confirmation
- Modify production systems without explicit permission and safety validation
- Make architectural changes without understanding full system impact

**Related Commands**: `/analyze:code`, `/dev:build`, `/dev:test`

---

## Deploy Commands

### /deploy:prepare-release

**Description**: Prepare application for production deployment

**Category**: deployment

**Agents**: deployment-engineer, quality-engineer

**Triggers**:

- Version release requests
- Production deployment preparation
- Release candidate creation
- Deployment readiness validation

**Usage**:

```bash
/deploy:prepare-release [version] [--type major|minor|patch]
```

**Release Preparation Process**:

1. **Pre-Release Validation**
   - Run full test suite (unit, integration, e2e)
   - Execute security audit
   - Perform performance benchmarking
   - Validate configuration for production
   - Check dependency vulnerabilities

2. **Version Management**
   - Update version numbers (package.json, etc.)
   - Generate changelog from commits
   - Tag release in version control
   - Update API documentation versions

3. **Build Optimization**
   - Create production build
   - Optimize bundle size
   - Generate source maps
   - Minify and compress assets
   - Validate build artifacts

4. **Documentation Updates**
   - Update README if needed
   - Generate API documentation
   - Create release notes
   - Document breaking changes
   - Update migration guides

5. **Deployment Planning**
   - Create deployment checklist
   - Generate rollback plan
   - Document environment variables
   - Prepare database migrations
   - Configure monitoring and alerts

6. **Final Checks**
   - Smoke test production build
   - Verify all services health
   - Validate external integrations
   - Check SSL certificates
   - Review security headers

**Checklist Output**:

**Pre-Release**

- [ ] All tests passing
- [ ] Security audit complete
- [ ] Performance validated
- [ ] Dependencies updated

**Version Control**

- [ ] Version bumped
- [ ] Changelog generated
- [ ] Git tag created
- [ ] Branch merged

**Build**

- [ ] Production build created
- [ ] Assets optimized
- [ ] Source maps generated
- [ ] Build validated

**Documentation**

- [ ] Release notes written
- [ ] API docs updated
- [ ] Migration guide ready
- [ ] Changelog complete

**Deployment**

- [ ] Rollback plan documented
- [ ] Environment configured
- [ ] Monitoring setup
- [ ] Team notified

**Example**:

```bash
/deploy:prepare-release 2.1.0 --type minor
```

**Boundaries**:

**Will**:

- Execute comprehensive pre-release validation and preparation
- Generate deployment checklists and rollback plans
- Update version management and documentation systematically

**Will Not**:

- Automatically deploy to production without explicit approval
- Skip critical validation steps for faster deployment
- Modify production infrastructure without proper planning

**Related Commands**: `/dev:build`, `/dev:test`, `/analyze:security-scan`

---

## Design Commands

### /design:system

**Description**: Design system architecture, APIs, and component interfaces with comprehensive specifications

**Category**: utility | **Complexity**: basic

**Triggers**:

- Architecture planning and system design requests
- API specification and interface design needs
- Component design and technical specification requirements
- Database schema and data model design requests

**Usage**:

```bash
/design:system [target] [--type architecture|api|component|database] [--format diagram|spec|code]
```

**Behavioral Flow**:

1. **Analyze**: Examine target requirements and existing system context
2. **Plan**: Define design approach and structure based on type and format
3. **Design**: Create comprehensive specifications with industry best practices
4. **Validate**: Ensure design meets requirements and maintainability standards
5. **Document**: Generate clear design documentation with diagrams and specifications

**Tool Coordination**:

- **Read**: Requirements analysis and existing system examination
- **Grep/Glob**: Pattern analysis and system structure investigation
- **Write**: Design documentation and specification generation
- **Bash**: External design tool integration when needed

**Key Patterns**:

- **Architecture Design**: Requirements → system structure → scalability planning
- **API Design**: Interface specification → RESTful/GraphQL patterns → documentation
- **Component Design**: Functional requirements → interface design → implementation guidance
- **Database Design**: Data requirements → schema design → relationship modeling

**Examples**:

```bash
# System Architecture Design
/design:system user-management-system --type architecture --format diagram
# Creates comprehensive system architecture with component relationships
# Includes scalability considerations and best practices

# API Specification Design
/design:system payment-api --type api --format spec
# Generates detailed API specification with endpoints and data models
# Follows RESTful design principles and industry standards

# Component Interface Design
/design:system notification-service --type component --format code
# Designs component interfaces with clear contracts and dependencies
# Provides implementation guidance and integration patterns

# Database Schema Design
/design:system e-commerce-db --type database --format diagram
# Creates database schema with entity relationships and constraints
# Includes normalization and performance considerations
```

**Boundaries**:

**Will**:

- Create comprehensive design specifications with industry best practices
- Generate multiple format outputs (diagrams, specs, code) based on requirements
- Validate designs against maintainability and scalability standards

**Will Not**:

- Generate actual implementation code (use /dev:implement for implementation)
- Modify existing system architecture without explicit design approval
- Create designs that violate established architectural constraints

**Related Commands**: `/design:workflow`, `/analyze:estimate`, `/dev:implement`

---

### /design:workflow

**Description**: Generate structured implementation workflows from PRDs and feature requirements

**Category**: orchestration | **Complexity**: advanced

**MCP Servers**: sequential, context7, magic, playwright, morphllm, serena

**Personas**: architect, analyzer, frontend, backend, security, devops, project-manager

**Triggers**:

- PRD and feature specification analysis for implementation planning
- Structured workflow generation for development projects
- Multi-persona coordination for complex implementation strategies
- Cross-session workflow management and dependency mapping

**Usage**:

```bash
/design:workflow [prd-file|feature-description] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```

**Behavioral Flow**:

1. **Analyze**: Parse PRD and feature specifications to understand implementation requirements
2. **Plan**: Generate comprehensive workflow structure with dependency mapping and task orchestration
3. **Coordinate**: Activate multiple personas for domain expertise and implementation strategy
4. **Execute**: Create structured step-by-step workflows with automated task coordination
5. **Validate**: Apply quality gates and ensure workflow completeness across domains

**MCP Integration**:

- **Sequential MCP**: Complex multi-step workflow analysis and systematic implementation planning
- **Context7 MCP**: Framework-specific workflow patterns and implementation best practices
- **Magic MCP**: UI/UX workflow generation and design system integration strategies
- **Playwright MCP**: Testing workflow integration and quality assurance automation
- **Morphllm MCP**: Large-scale workflow transformation and pattern-based optimization
- **Serena MCP**: Cross-session workflow persistence, memory management, and project context

**Tool Coordination**:

- **Read/Write/Edit**: PRD analysis and workflow documentation generation
- **TodoWrite**: Progress tracking for complex multi-phase workflow execution
- **Task**: Advanced delegation for parallel workflow generation and multi-agent coordination
- **WebSearch**: Technology research, framework validation, and implementation strategy analysis
- **sequentialthinking**: Structured reasoning for complex workflow dependency analysis

**Key Patterns**:

- **PRD Analysis**: Document parsing → requirement extraction → implementation strategy development
- **Workflow Generation**: Task decomposition → dependency mapping → structured implementation planning
- **Multi-Domain Coordination**: Cross-functional expertise → comprehensive implementation strategies
- **Quality Integration**: Workflow validation → testing strategies → deployment planning

**Examples**:

```bash
# Systematic PRD Workflow
/design:workflow ClaudeDocs/PRD/feature-spec.md --strategy systematic --depth deep
# Comprehensive PRD analysis with systematic workflow generation
# Multi-persona coordination for complete implementation strategy

# Agile Feature Workflow
/design:workflow "user authentication system" --strategy agile --parallel
# Agile workflow generation with parallel task coordination
# Context7 and Magic MCP for framework and UI workflow patterns

# Enterprise Implementation Planning
/design:workflow enterprise-prd.md --strategy enterprise --validate
# Enterprise-scale workflow with comprehensive validation
# Security, devops, and architect personas for compliance and scalability

# Cross-Session Workflow Management
/design:workflow project-brief.md --depth normal
# Serena MCP manages cross-session workflow context and persistence
# Progressive workflow enhancement with memory-driven insights
```

**Boundaries**:

**Will**:

- Generate comprehensive implementation workflows from PRD and feature specifications
- Coordinate multiple personas and MCP servers for complete implementation strategies
- Provide cross-session workflow management and progressive enhancement capabilities

**Will Not**:

- Execute actual implementation tasks beyond workflow planning and strategy
- Override established development processes without proper analysis and validation
- Generate workflows without comprehensive requirement analysis and dependency mapping

**Related Commands**: `/orchestrate:brainstorm`, `/orchestrate:task`, `/design:system`, `/analyze:estimate`

---

## Dev Commands

### /dev:build

**Description**: Build, compile, and package projects with intelligent error handling and optimization

**Category**: utility | **Complexity**: enhanced

**MCP Servers**: playwright

**Personas**: devops-engineer

**Triggers**:

- Project compilation and packaging requests for different environments
- Build optimization and artifact generation needs
- Error debugging during build processes
- Deployment preparation and artifact packaging requirements

**Usage**:

```bash
/dev:build [target] [--type dev|prod|test] [--clean] [--optimize] [--verbose]
```

**Behavioral Flow**:

1. **Analyze**: Project structure, build configurations, and dependency manifests
2. **Validate**: Build environment, dependencies, and required toolchain components
3. **Execute**: Build process with real-time monitoring and error detection
4. **Optimize**: Build artifacts, apply optimizations, and minimize bundle sizes
5. **Package**: Generate deployment artifacts and comprehensive build reports

**MCP Integration**:

- **Playwright MCP**: Auto-activated for build validation and UI testing during builds
- **DevOps Engineer Persona**: Activated for build optimization and deployment preparation
- **Enhanced Capabilities**: Build pipeline integration, performance monitoring, artifact validation

**Tool Coordination**:

- **Bash**: Build system execution and process management
- **Read**: Configuration analysis and manifest inspection
- **Grep**: Error parsing and build log analysis
- **Glob**: Artifact discovery and validation
- **Write**: Build reports and deployment documentation

**Key Patterns**:

- **Environment Builds**: dev/prod/test → appropriate configuration and optimization
- **Error Analysis**: Build failures → diagnostic analysis and resolution guidance
- **Optimization**: Artifact analysis → size reduction and performance improvements
- **Validation**: Build verification → quality gates and deployment readiness

**Examples**:

```bash
# Standard Project Build
/dev:build
# Builds entire project using default configuration
# Generates artifacts and comprehensive build report

# Production Optimization Build
/dev:build --type prod --clean --optimize
# Clean production build with advanced optimizations
# Minification, tree-shaking, and deployment preparation

# Targeted Component Build
/dev:build frontend --verbose
# Builds specific project component with detailed output
# Real-time progress monitoring and diagnostic information

# Development Build with Validation
/dev:build --type dev --validate
# Development build with Playwright validation
# UI testing and build verification integration
```

**Boundaries**:

**Will**:

- Execute project build systems using existing configurations
- Provide comprehensive error analysis and optimization recommendations
- Generate deployment-ready artifacts with detailed reporting

**Will Not**:

- Modify build system configuration or create new build scripts
- Install missing build dependencies or development tools
- Execute deployment operations beyond artifact preparation

**Related Commands**: `/dev:test`, `/deploy:prepare-release`, `/analyze:troubleshoot`

---

### /dev:code-review

**Description**: Comprehensive code quality review and analysis

**Category**: development

**Agents**: code-reviewer, security-auditor

**Triggers**:

- Pull request reviews
- Pre-commit code quality checks
- Refactoring validation
- Manual code review requests

**Usage**:

```bash
/dev:code-review [path] [--focus quality|security|performance|all]
```

**Review Process**:

1. **Code Quality Analysis**
   - Identify code smells and anti-patterns
   - Check naming conventions and consistency
   - Review error handling patterns
   - Assess code readability and maintainability
   - Find unused imports, variables, or dead code

2. **Security Assessment**
   - Scan for common vulnerabilities (OWASP Top 10)
   - Check for hardcoded secrets or credentials
   - Review authentication and authorization logic
   - Examine input validation and sanitization
   - Identify security risks in dependencies

3. **Performance Review**
   - Identify potential performance bottlenecks
   - Check for inefficient algorithms or queries
   - Review memory usage patterns
   - Analyze bundle size and optimization opportunities

4. **Architecture Evaluation**
   - Evaluate code organization and separation of concerns
   - Check for proper abstraction and modularity
   - Review dependency management and coupling
   - Assess scalability and maintainability

**Output Format**:

**Summary**: Overall code health score and key findings

**Critical Issues**: Must-fix problems (blocking)
**Important Issues**: Should-fix problems (high priority)
**Suggestions**: Nice-to-have improvements

**Best Practices**: Recommendations for improvement

**Example**:

```bash
/dev:code-review src/auth --focus security
```

**Boundaries**:

**Will**:

- Perform comprehensive code review across multiple quality dimensions
- Identify issues with severity ratings and actionable recommendations
- Generate detailed review reports with improvement guidance

**Will Not**:

- Automatically apply code changes without explicit approval
- Override project-specific coding standards or conventions
- Guarantee 100% issue detection (review is advisory)

**Related Commands**: `/analyze:code`, `/analyze:security-scan`, `/quality:improve`

---

### /dev:git

**Description**: Git operations with intelligent commit messages and workflow optimization

**Category**: utility | **Complexity**: basic

**Triggers**:

- Git repository operations: status, add, commit, push, pull, branch
- Need for intelligent commit message generation
- Repository workflow optimization requests
- Branch management and merge operations

**Usage**:

```bash
/dev:git [operation] [args] [--smart-commit] [--interactive]
```

**Behavioral Flow**:

1. **Analyze**: Check repository state and working directory changes
2. **Validate**: Ensure operation is appropriate for current Git context
3. **Execute**: Run Git command with intelligent automation
4. **Optimize**: Apply smart commit messages and workflow patterns
5. **Report**: Provide status and next steps guidance

**Tool Coordination**:

- **Bash**: Git command execution and repository operations
- **Read**: Repository state analysis and configuration review
- **Grep**: Log parsing and status analysis
- **Write**: Commit message generation and documentation

**Key Patterns**:

- **Smart Commits**: Analyze changes → generate conventional commit message
- **Status Analysis**: Repository state → actionable recommendations
- **Branch Strategy**: Consistent naming and workflow enforcement
- **Error Recovery**: Conflict resolution and state restoration guidance

**Examples**:

```bash
# Smart Status Analysis
/dev:git status
# Analyzes repository state with change summary
# Provides next steps and workflow recommendations

# Intelligent Commit
/dev:git commit --smart-commit
# Generates conventional commit message from change analysis
# Applies best practices and consistent formatting

# Interactive Operations
/dev:git merge feature-branch --interactive
# Guided merge with conflict resolution assistance
```

**Boundaries**:

**Will**:

- Execute Git operations with intelligent automation
- Generate conventional commit messages from change analysis
- Provide workflow optimization and best practice guidance

**Will Not**:

- Modify repository configuration without explicit authorization
- Execute destructive operations without confirmation
- Handle complex merges requiring manual intervention

**Note**: Does not sign off commits or name Claude as co-author

**Related Commands**: `/dev:code-review`, `/deploy:prepare-release`

---

### /dev:implement

**Description**: Feature and code implementation with intelligent persona activation and MCP integration

**Category**: workflow | **Complexity**: standard

**MCP Servers**: context7, sequential, magic, playwright

**Personas**: architect, frontend, backend, security, qa-specialist

**Triggers**:

- Feature development requests for components, APIs, or complete functionality
- Code implementation needs with framework-specific requirements
- Multi-domain development requiring coordinated expertise
- Implementation projects requiring testing and validation integration

**Usage**:

```bash
/dev:implement [feature-description] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]
```

**Behavioral Flow**:

1. **Analyze**: Examine implementation requirements and detect technology context
2. **Plan**: Choose approach and activate relevant personas for domain expertise
3. **Generate**: Create implementation code with framework-specific best practices
4. **Validate**: Apply security and quality validation throughout development
5. **Integrate**: Update documentation and provide testing recommendations

**MCP Integration**:

- **Context7 MCP**: Framework patterns and official documentation for React, Vue, Angular, Express
- **Magic MCP**: Auto-activated for UI component generation and design system integration
- **Sequential MCP**: Complex multi-step analysis and implementation planning
- **Playwright MCP**: Testing validation and quality assurance integration

**Tool Coordination**:

- **Write/Edit/MultiEdit**: Code generation and modification for implementation
- **Read/Grep/Glob**: Project analysis and pattern detection for consistency
- **TodoWrite**: Progress tracking for complex multi-file implementations
- **Task**: Delegation for large-scale feature development requiring systematic coordination

**Key Patterns**:

- **Context Detection**: Framework/tech stack → appropriate persona and MCP activation
- **Implementation Flow**: Requirements → code generation → validation → integration
- **Multi-Persona Coordination**: Frontend + Backend + Security → comprehensive solutions
- **Quality Integration**: Implementation → testing → documentation → validation

**Examples**:

```bash
# React Component Implementation
/dev:implement user profile component --type component --framework react
# Magic MCP generates UI component with design system integration
# Frontend persona ensures best practices and accessibility

# API Service Implementation
/dev:implement user authentication API --type api --safe --with-tests
# Backend persona handles server-side logic and data processing
# Security persona ensures authentication best practices

# Full-Stack Feature
/dev:implement payment processing system --type feature --with-tests
# Multi-persona coordination: architect, frontend, backend, security
# Sequential MCP breaks down complex implementation steps

# Framework-Specific Implementation
/dev:implement dashboard widget --framework vue
# Context7 MCP provides Vue-specific patterns and documentation
# Framework-appropriate implementation with official best practices
```

**Boundaries**:

**Will**:

- Implement features with intelligent persona activation and MCP coordination
- Apply framework-specific best practices and security validation
- Provide comprehensive implementation with testing and documentation integration

**Will Not**:

- Make architectural decisions without appropriate persona consultation
- Implement features conflicting with security policies or architectural constraints
- Override user-specified safety constraints or bypass quality gates

**Related Commands**: `/design:system`, `/dev:test`, `/quality:improve`

---

### /dev:test

**Description**: Execute tests with coverage analysis and automated quality reporting

**Category**: utility | **Complexity**: enhanced

**MCP Servers**: playwright

**Personas**: qa-specialist

**Triggers**:

- Test execution requests for unit, integration, or e2e tests
- Coverage analysis and quality gate validation needs
- Continuous testing and watch mode scenarios
- Test failure analysis and debugging requirements

**Usage**:

```bash
/dev:test [target] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]
```

**Behavioral Flow**:

1. **Discover**: Categorize available tests using runner patterns and conventions
2. **Configure**: Set up appropriate test environment and execution parameters
3. **Execute**: Run tests with monitoring and real-time progress tracking
4. **Analyze**: Generate coverage reports and failure diagnostics
5. **Report**: Provide actionable recommendations and quality metrics

**MCP Integration**:

- **Playwright MCP**: Auto-activated for `--type e2e` browser testing
- **QA Specialist Persona**: Activated for test analysis and quality assessment
- **Enhanced Capabilities**: Cross-browser testing, visual validation, performance metrics

**Tool Coordination**:

- **Bash**: Test runner execution and environment management
- **Glob**: Test discovery and file pattern matching
- **Grep**: Result parsing and failure analysis
- **Write**: Coverage reports and test summaries

**Key Patterns**:

- **Test Discovery**: Pattern-based categorization → appropriate runner selection
- **Coverage Analysis**: Execution metrics → comprehensive coverage reporting
- **E2E Testing**: Browser automation → cross-platform validation
- **Watch Mode**: File monitoring → continuous test execution

**Examples**:

```bash
# Basic Test Execution
/dev:test
# Discovers and runs all tests with standard configuration
# Generates pass/fail summary and basic coverage

# Targeted Coverage Analysis
/dev:test src/components --type unit --coverage
# Unit tests for specific directory with detailed coverage metrics

# Browser Testing
/dev:test --type e2e
# Activates Playwright MCP for comprehensive browser testing
# Cross-browser compatibility and visual validation

# Development Watch Mode
/dev:test --watch --fix
# Continuous testing with automatic simple failure fixes
# Real-time feedback during development
```

**Boundaries**:

**Will**:

- Execute existing test suites using project's configured test runner
- Generate coverage reports and quality metrics
- Provide intelligent test failure analysis with actionable recommendations

**Will Not**:

- Generate test cases or modify test framework configuration
- Execute tests requiring external services without proper setup
- Make destructive changes to test files without explicit permission

**Related Commands**: `/test:generate-tests`, `/dev:build`, `/quality:improve`

---

## Docs Commands

### /docs:generate

**Description**: Generate focused documentation for components, functions, APIs, and features

**Category**: utility | **Complexity**: basic

**Triggers**:

- Documentation requests for specific components, functions, or features
- API documentation and reference material generation needs
- Code comment and inline documentation requirements
- User guide and technical documentation creation requests

**Usage**:

```bash
/docs:generate [target] [--type inline|external|api|guide] [--style brief|detailed]
```

**Behavioral Flow**:

1. **Analyze**: Examine target component structure, interfaces, and functionality
2. **Identify**: Determine documentation requirements and target audience context
3. **Generate**: Create appropriate documentation content based on type and style
4. **Format**: Apply consistent structure and organizational patterns
5. **Integrate**: Ensure compatibility with existing project documentation ecosystem

**Tool Coordination**:

- **Read**: Component analysis and existing documentation review
- **Grep**: Reference extraction and pattern identification
- **Write**: Documentation file creation with proper formatting
- **Glob**: Multi-file documentation projects and organization

**Key Patterns**:

- **Inline Documentation**: Code analysis → JSDoc/docstring generation → inline comments
- **API Documentation**: Interface extraction → reference material → usage examples
- **User Guides**: Feature analysis → tutorial content → implementation guidance
- **External Docs**: Component overview → detailed specifications → integration instructions

**Examples**:

```bash
# Inline Code Documentation
/docs:generate src/auth/login.js --type inline
# Generates JSDoc comments with parameter and return descriptions
# Adds comprehensive inline documentation for functions and classes

# API Reference Generation
/docs:generate src/api --type api --style detailed
# Creates comprehensive API documentation with endpoints and schemas
# Generates usage examples and integration guidelines

# User Guide Creation
/docs:generate payment-module --type guide --style brief
# Creates user-focused documentation with practical examples
# Focuses on implementation patterns and common use cases

# Component Documentation
/docs:generate components/ --type external
# Generates external documentation files for component library
# Includes props, usage examples, and integration patterns
```

**Boundaries**:

**Will**:

- Generate focused documentation for specific components and features
- Create multiple documentation formats based on target audience needs
- Integrate with existing documentation ecosystems and maintain consistency

**Will Not**:

- Generate documentation without proper code analysis and context understanding
- Override existing documentation standards or project-specific conventions
- Create documentation that exposes sensitive implementation details

**Related Commands**: `/docs:index`, `/analyze:explain`, `/design:system`

---

### /docs:index

**Description**: Generate comprehensive project documentation and knowledge base with intelligent organization

**Category**: special | **Complexity**: standard

**MCP Servers**: sequential, context7

**Personas**: architect, scribe, quality

**Triggers**:

- Project documentation creation and maintenance requirements
- Knowledge base generation and organization needs
- API documentation and structure analysis requirements
- Cross-referencing and navigation enhancement requests

**Usage**:

```bash
/docs:index [target] [--type docs|api|structure|readme] [--format md|json|yaml]
```

**Behavioral Flow**:

1. **Analyze**: Examine project structure and identify key documentation components
2. **Organize**: Apply intelligent organization patterns and cross-referencing strategies
3. **Generate**: Create comprehensive documentation with framework-specific patterns
4. **Validate**: Ensure documentation completeness and quality standards
5. **Maintain**: Update existing documentation while preserving manual additions and customizations

**MCP Integration**:

- **Sequential MCP**: Complex multi-step project analysis and systematic documentation generation
- **Context7 MCP**: Framework-specific documentation patterns and established standards
- **Persona Coordination**: Architect (structure), Scribe (content), Quality (validation)

**Tool Coordination**:

- **Read/Grep/Glob**: Project structure analysis and content extraction for documentation generation
- **Write**: Documentation creation with intelligent organization and cross-referencing
- **TodoWrite**: Progress tracking for complex multi-component documentation workflows
- **Task**: Advanced delegation for large-scale documentation requiring systematic coordination

**Key Patterns**:

- **Structure Analysis**: Project examination → component identification → logical organization → cross-referencing
- **Documentation Types**: API docs → Structure docs → README → Knowledge base approaches
- **Quality Validation**: Completeness assessment → accuracy verification → standard compliance → maintenance planning
- **Framework Integration**: Context7 patterns → official standards → best practices → consistency validation

**Examples**:

```bash
# Project Structure Documentation
/docs:index project-root --type structure --format md
# Comprehensive project structure documentation with intelligent organization
# Creates navigable structure with cross-references and component relationships

# API Documentation Generation
/docs:index src/api --type api --format json
# API documentation with systematic analysis and validation
# Scribe and quality personas ensure completeness and accuracy

# Knowledge Base Creation
/docs:index . --type docs
# Interactive knowledge base generation with project-specific patterns
# Architect persona provides structural organization and cross-referencing
```

**Boundaries**:

**Will**:

- Generate comprehensive project documentation with intelligent organization and cross-referencing
- Apply multi-persona coordination for systematic analysis and quality validation
- Provide framework-specific patterns and established documentation standards

**Will Not**:

- Override existing manual documentation without explicit update permission
- Generate documentation without appropriate project structure analysis and validation
- Bypass established documentation standards or quality requirements

**Related Commands**: `/docs:generate`, `/design:system`, `/analyze:explain`

---

## Orchestrate Commands

### /orchestrate:brainstorm

**Description**: Interactive requirements discovery through Socratic dialogue and systematic exploration

**Category**: orchestration | **Complexity**: advanced

**MCP Servers**: sequential, context7, magic, playwright, morphllm, serena

**Personas**: architect, analyzer, frontend, backend, security, devops, project-manager

**Triggers**:

- Ambiguous project ideas requiring structured exploration
- Requirements discovery and specification development needs
- Concept validation and feasibility assessment requests
- Cross-session brainstorming and iterative refinement scenarios

**Usage**:

```bash
/orchestrate:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```

**Behavioral Flow**:

1. **Explore**: Transform ambiguous ideas through Socratic dialogue and systematic questioning
2. **Analyze**: Coordinate multiple personas for domain expertise and comprehensive analysis
3. **Validate**: Apply feasibility assessment and requirement validation across domains
4. **Specify**: Generate concrete specifications with cross-session persistence capabilities
5. **Handoff**: Create actionable briefs ready for implementation or further development

**MCP Integration**:

- **Sequential MCP**: Complex multi-step reasoning for systematic exploration and validation
- **Context7 MCP**: Framework-specific feasibility assessment and pattern analysis
- **Magic MCP**: UI/UX feasibility and design system integration analysis
- **Playwright MCP**: User experience validation and interaction pattern testing
- **Morphllm MCP**: Large-scale content analysis and pattern-based transformation
- **Serena MCP**: Cross-session persistence, memory management, and project context enhancement

**Tool Coordination**:

- **Read/Write/Edit**: Requirements documentation and specification generation
- **TodoWrite**: Progress tracking for complex multi-phase exploration
- **Task**: Advanced delegation for parallel exploration paths and multi-agent coordination
- **WebSearch**: Market research, competitive analysis, and technology validation
- **sequentialthinking**: Structured reasoning for complex requirements analysis

**Key Patterns**:

- **Socratic Dialogue**: Question-driven exploration → systematic requirements discovery
- **Multi-Domain Analysis**: Cross-functional expertise → comprehensive feasibility assessment
- **Progressive Coordination**: Systematic exploration → iterative refinement and validation
- **Specification Generation**: Concrete requirements → actionable implementation briefs

**Examples**:

```bash
# Systematic Product Discovery
/orchestrate:brainstorm "AI-powered project management tool" --strategy systematic --depth deep
# Multi-persona analysis: architect (system design), analyzer (feasibility), project-manager (requirements)
# Sequential MCP provides structured exploration framework

# Agile Feature Exploration
/orchestrate:brainstorm "real-time collaboration features" --strategy agile --parallel
# Parallel exploration paths with frontend, backend, and security personas
# Context7 and Magic MCP for framework and UI pattern analysis

# Enterprise Solution Validation
/orchestrate:brainstorm "enterprise data analytics platform" --strategy enterprise --validate
# Comprehensive validation with security, devops, and architect personas
# Serena MCP for cross-session persistence and enterprise requirements tracking

# Cross-Session Refinement
/orchestrate:brainstorm "mobile app monetization strategy" --depth normal
# Serena MCP manages cross-session context and iterative refinement
# Progressive dialogue enhancement with memory-driven insights
```

**Boundaries**:

**Will**:

- Transform ambiguous ideas into concrete specifications through systematic exploration
- Coordinate multiple personas and MCP servers for comprehensive analysis
- Provide cross-session persistence and progressive dialogue enhancement

**Will Not**:

- Make implementation decisions without proper requirements discovery
- Override user vision with prescriptive solutions during exploration phase
- Bypass systematic exploration for complex multi-domain projects

**Related Commands**: `/design:workflow`, `/orchestrate:task`, `/analyze:estimate`

---

### /reasoning:adjust

### /reasoning:budget

**Description**: Control internal reasoning token budget for cost and quality optimization

**Category**: utility | **Complexity**: basic

**Triggers**:

- Need to control reasoning depth and cost trade-offs
- Complex problems requiring extended thinking time
- Budget-conscious operations with quality requirements

**Usage**:

```bash
/reasoning:budget [4000|10000|32000|128000] [--auto-adjust] [--show-usage]
```

**Budget Levels**:

- **4K**: Standard reasoning (~$0.012) - routine tasks
- **10K**: Deep reasoning (~$0.030) - architectural decisions  
- **32K**: Maximum reasoning (~$0.096) - critical redesign
- **128K**: Extended thinking (~$0.384) - extreme complexity (5x cheaper than OpenAI o1)

**Examples**:

```bash
# Extended thinking for critical issue
/reasoning:budget 128000 --show-usage

# Budget-conscious analysis
/reasoning:budget 10000
/analyze:code src/auth --reasoning-profile security
```

**Related Commands**: `/reasoning:adjust`, `/reasoning:metrics`

---

### /reasoning:metrics

**Description**: Track reasoning effectiveness and optimization metrics across commands

**Category**: utility | **Complexity**: basic

**Triggers**:

- Need to understand reasoning effectiveness and costs
- Optimization of reasoning depth for specific task types
- Budget planning and cost analysis

**Usage**:

```bash
/reasoning:metrics [--command <name>] [--timeframe 7d|30d|all] [--export json|markdown|csv]
```

**Metrics Tracked**:

- Token usage by reasoning level and command
- Success rates and confidence scores
- Cost analysis and budget efficiency
- MCP server activation patterns
- Optimization recommendations

**Examples**:

```bash
# Overall dashboard
/reasoning:metrics

# Command-specific analysis
/reasoning:metrics --command analyze:code

# Export for analysis
/reasoning:metrics --timeframe 30d --export json
```

**Related Commands**: `/reasoning:budget`, `/reasoning:adjust`

---

**Description**: Dynamically adjust reasoning depth during task execution

**Category**: utility | **Complexity**: basic

**Triggers**:

- Need to escalate or reduce reasoning depth during complex task execution
- Initial analysis insufficient or overly verbose for current subtask
- Performance optimization during long-running operations
- Runtime adaptation based on emerging task complexity

**Usage**:

```bash
/reasoning:adjust [low|medium|high|ultra] [--scope current|remaining]
```

**Reasoning Depth Levels**:

**low (~2K tokens)**

- Simple operations, quick iterations, prototyping
- No MCP servers (native tools only)
- Direct solutions, minimal exploration

**medium (~4K tokens)**

- Standard development tasks, moderate complexity
- MCP: Sequential (structured reasoning)
- Systematic exploration, hypothesis testing
- Equivalent to `--think` flag

**high (~10K tokens)**

- Architectural decisions, system-wide dependencies
- MCP: Sequential + Context7 (official patterns)
- Deep exploration, trade-off analysis
- Equivalent to `--think-hard` flag

**ultra (~32K tokens)**

- Critical redesigns, legacy modernization, complex debugging
- MCP: All available (Sequential, Context7, Serena, etc.)
- Maximum depth, exhaustive exploration, meta-analysis
- Equivalent to `--ultrathink` flag
- Auto-enables `--introspect` transparency markers

**Scope Control**:

- `--scope current`: Apply to current subtask only, revert after completion
- `--scope remaining`: Apply to all remaining work (default)

**Examples**:

```bash
# Escalate for complex subtask
/reasoning:adjust ultra --scope current
# Maximum depth for current subtask, then revert

# Optimize long-running analysis
/reasoning:adjust medium --scope remaining
# Reduce depth for faster iteration

# Spike for architecture decision
/reasoning:adjust high --scope current
# Deep analysis for decision, return to standard depth
```

**Related Commands**: `/orchestrate:spawn`, `/analyze:code`, `/design:system`

---

### /orchestrate:spawn

**Description**: Meta-system task orchestration with intelligent breakdown and delegation

**Category**: special | **Complexity**: high

**Triggers**:

- Complex multi-domain operations requiring intelligent task breakdown
- Large-scale system operations spanning multiple technical areas
- Operations requiring parallel coordination and dependency management
- Meta-level orchestration beyond standard command capabilities

**Usage**:

```bash
/orchestrate:spawn [complex-task] [--strategy sequential|parallel|adaptive] [--depth normal|deep]
```

**Behavioral Flow**:

1. **Analyze**: Parse complex operation requirements and assess scope across domains
2. **Decompose**: Break down operation into coordinated subtask hierarchies
3. **Orchestrate**: Execute tasks using optimal coordination strategy (parallel/sequential)
4. **Monitor**: Track progress across task hierarchies with dependency management
5. **Integrate**: Aggregate results and provide comprehensive orchestration summary

**MCP Integration**:

- **Native Orchestration**: Meta-system command uses native coordination without MCP dependencies
- **Progressive Integration**: Coordination with systematic execution for progressive enhancement
- **Framework Integration**: Advanced integration with SuperClaude orchestration layers

**Tool Coordination**:

- **TodoWrite**: Hierarchical task breakdown and progress tracking across Epic → Story → Task levels
- **Read/Grep/Glob**: System analysis and dependency mapping for complex operations
- **Edit/MultiEdit/Write**: Coordinated file operations with parallel and sequential execution
- **Bash**: System-level operations coordination with intelligent resource management

**Key Patterns**:

- **Hierarchical Breakdown**: Epic-level operations → Story coordination → Task execution → Subtask granularity
- **Strategy Selection**: Sequential (dependency-ordered) → Parallel (independent) → Adaptive (dynamic)
- **Meta-System Coordination**: Cross-domain operations → resource optimization → result integration
- **Progressive Enhancement**: Systematic execution → quality gates → comprehensive validation

**Examples**:

```bash
# Complex Feature Implementation
/orchestrate:spawn "implement user authentication system"
# Breakdown: Database design → Backend API → Frontend UI → Testing
# Coordinates across multiple domains with dependency management

# Large-Scale System Operation
/orchestrate:spawn "migrate legacy monolith to microservices" --strategy adaptive --depth deep
# Enterprise-scale operation with sophisticated orchestration
# Adaptive coordination based on operation characteristics

# Cross-Domain Infrastructure
/orchestrate:spawn "establish CI/CD pipeline with security scanning"
# System-wide infrastructure operation spanning DevOps, Security, Quality domains
# Parallel execution of independent components with validation gates
```

**Boundaries**:

**Will**:

- Decompose complex multi-domain operations into coordinated task hierarchies
- Provide intelligent orchestration with parallel and sequential coordination strategies
- Execute meta-system operations beyond standard command capabilities

**Will Not**:

- Replace domain-specific commands for simple operations
- Override user coordination preferences or execution strategies
- Execute operations without proper dependency analysis and validation

**Related Commands**: `/orchestrate:task`, `/design:workflow`, `/orchestrate:brainstorm`

---

### /orchestrate:task

**Description**: Execute complex tasks with intelligent workflow management and delegation

**Category**: special | **Complexity**: advanced

**MCP Servers**: sequential, context7, magic, playwright, morphllm, serena

**Personas**: architect, analyzer, frontend, backend, security, devops, project-manager

**Triggers**:

- Complex tasks requiring multi-agent coordination and delegation
- Projects needing structured workflow management and cross-session persistence
- Operations requiring intelligent MCP server routing and domain expertise
- Tasks benefiting from systematic execution and progressive enhancement

**Usage**:

```bash
/orchestrate:task [action] [target] [--strategy systematic|agile|enterprise] [--parallel] [--delegate]
```

**Behavioral Flow**:

1. **Analyze**: Parse task requirements and determine optimal execution strategy
2. **Delegate**: Route to appropriate MCP servers and activate relevant personas
3. **Coordinate**: Execute tasks with intelligent workflow management and parallel processing
4. **Validate**: Apply quality gates and comprehensive task completion verification
5. **Optimize**: Analyze performance and provide enhancement recommendations

**MCP Integration**:

- **Sequential MCP**: Complex multi-step task analysis and systematic execution planning
- **Context7 MCP**: Framework-specific patterns and implementation best practices
- **Magic MCP**: UI/UX task coordination and design system integration
- **Playwright MCP**: Testing workflow integration and validation automation
- **Morphllm MCP**: Large-scale task transformation and pattern-based optimization
- **Serena MCP**: Cross-session task persistence and project memory management

**Tool Coordination**:

- **TodoWrite**: Hierarchical task breakdown and progress tracking across Epic → Story → Task levels
- **Task**: Advanced delegation for complex multi-agent coordination and sub-task management
- **Read/Write/Edit**: Task documentation and implementation coordination
- **sequentialthinking**: Structured reasoning for complex task dependency analysis

**Key Patterns**:

- **Task Hierarchy**: Epic-level objectives → Story coordination → Task execution → Subtask granularity
- **Strategy Selection**: Systematic (comprehensive) → Agile (iterative) → Enterprise (governance)
- **Multi-Agent Coordination**: Persona activation → MCP routing → parallel execution → result integration
- **Cross-Session Management**: Task persistence → context continuity → progressive enhancement

**Examples**:

```bash
# Complex Feature Development
/orchestrate:task create "enterprise authentication system" --strategy systematic --parallel
# Comprehensive task breakdown with multi-domain coordination
# Activates architect, security, backend, frontend personas

# Agile Sprint Coordination
/orchestrate:task execute "feature backlog" --strategy agile --delegate
# Iterative task execution with intelligent delegation
# Cross-session persistence for sprint continuity

# Multi-Domain Integration
/orchestrate:task execute "microservices platform" --strategy enterprise --parallel
# Enterprise-scale coordination with compliance validation
# Parallel execution across multiple technical domains
```

**Boundaries**:

**Will**:

- Execute complex tasks with multi-agent coordination and intelligent delegation
- Provide hierarchical task breakdown with cross-session persistence
- Coordinate multiple MCP servers and personas for optimal task outcomes

**Will Not**:

- Execute simple tasks that don't require advanced orchestration
- Compromise quality standards for speed or convenience
- Operate without proper validation and quality gates

**Related Commands**: `/orchestrate:spawn`, `/design:workflow`, `/dev:implement`

---

## Quality Commands

### /quality:cleanup

**Description**: Systematically clean up code, remove dead code, and optimize project structure

**Category**: workflow | **Complexity**: standard

**MCP Servers**: sequential, context7

**Personas**: architect, quality, security

**Triggers**:

- Code maintenance and technical debt reduction requests
- Dead code removal and import optimization needs
- Project structure improvement and organization requirements
- Codebase hygiene and quality improvement initiatives

**Usage**:

```bash
/quality:cleanup [target] [--type code|imports|files|all] [--safe|--aggressive] [--interactive]
```

**Behavioral Flow**:

1. **Analyze**: Assess cleanup opportunities and safety considerations across target scope
2. **Plan**: Choose cleanup approach and activate relevant personas for domain expertise
3. **Execute**: Apply systematic cleanup with intelligent dead code detection and removal
4. **Validate**: Ensure no functionality loss through testing and safety verification
5. **Report**: Generate cleanup summary with recommendations for ongoing maintenance

**MCP Integration**:

- **Sequential MCP**: Auto-activated for complex multi-step cleanup analysis and planning
- **Context7 MCP**: Framework-specific cleanup patterns and best practices
- **Persona Coordination**: Architect (structure), Quality (debt), Security (credentials)

**Tool Coordination**:

- **Read/Grep/Glob**: Code analysis and pattern detection for cleanup opportunities
- **Edit/MultiEdit**: Safe code modification and structure optimization
- **TodoWrite**: Progress tracking for complex multi-file cleanup operations
- **Task**: Delegation for large-scale cleanup workflows requiring systematic coordination

**Key Patterns**:

- **Dead Code Detection**: Usage analysis → safe removal with dependency validation
- **Import Optimization**: Dependency analysis → unused import removal and organization
- **Structure Cleanup**: Architectural analysis → file organization and modular improvements
- **Safety Validation**: Pre/during/post checks → preserve functionality throughout cleanup

**Examples**:

```bash
# Safe Code Cleanup
/quality:cleanup src/ --type code --safe
# Conservative cleanup with automatic safety validation
# Removes dead code while preserving all functionality

# Import Optimization
/quality:cleanup --type imports --preview
# Analyzes and shows unused import cleanup without execution
# Framework-aware optimization via Context7 patterns

# Comprehensive Project Cleanup
/quality:cleanup --type all --interactive
# Multi-domain cleanup with user guidance for complex decisions
# Activates all personas for comprehensive analysis

# Framework-Specific Cleanup
/quality:cleanup components/ --aggressive
# Thorough cleanup with Context7 framework patterns
# Sequential analysis for complex dependency management
```

**Boundaries**:

**Will**:

- Systematically clean code, remove dead code, and optimize project structure
- Provide comprehensive safety validation with backup and rollback capabilities
- Apply intelligent cleanup algorithms with framework-specific pattern recognition

**Will Not**:

- Remove code without thorough safety analysis and validation
- Override project-specific cleanup exclusions or architectural constraints
- Apply cleanup operations that compromise functionality or introduce bugs

**Related Commands**: `/quality:improve`, `/analyze:code`, `/dev:code-review`

---

### /quality:improve

**Description**: Apply systematic improvements to code quality, performance, and maintainability

**Category**: workflow | **Complexity**: standard

**MCP Servers**: sequential, context7

**Personas**: architect, performance, quality, security

**Triggers**:

- Code quality enhancement and refactoring requests
- Performance optimization and bottleneck resolution needs
- Maintainability improvements and technical debt reduction
- Best practices application and coding standards enforcement

**Usage**:

```bash
/quality:improve [target] [--type quality|performance|maintainability|style] [--safe] [--interactive]
```

**Behavioral Flow**:

1. **Analyze**: Examine codebase for improvement opportunities and quality issues
2. **Plan**: Choose improvement approach and activate relevant personas for expertise
3. **Execute**: Apply systematic improvements with domain-specific best practices
4. **Validate**: Ensure improvements preserve functionality and meet quality standards
5. **Document**: Generate improvement summary and recommendations for future work

**MCP Integration**:

- **Sequential MCP**: Auto-activated for complex multi-step improvement analysis and planning
- **Context7 MCP**: Framework-specific best practices and optimization patterns
- **Persona Coordination**: Architect (structure), Performance (speed), Quality (maintainability), Security (safety)

**Tool Coordination**:

- **Read/Grep/Glob**: Code analysis and improvement opportunity identification
- **Edit/MultiEdit**: Safe code modification and systematic refactoring
- **TodoWrite**: Progress tracking for complex multi-file improvement operations
- **Task**: Delegation for large-scale improvement workflows requiring systematic coordination

**Key Patterns**:

- **Quality Improvement**: Code analysis → technical debt identification → refactoring application
- **Performance Optimization**: Profiling analysis → bottleneck identification → optimization implementation
- **Maintainability Enhancement**: Structure analysis → complexity reduction → documentation improvement
- **Security Hardening**: Vulnerability analysis → security pattern application → validation verification

**Examples**:

```bash
# Code Quality Enhancement
/quality:improve src/ --type quality --safe
# Systematic quality analysis with safe refactoring application
# Improves code structure, reduces technical debt, enhances readability

# Performance Optimization
/quality:improve api-endpoints --type performance --interactive
# Performance persona analyzes bottlenecks and optimization opportunities
# Interactive guidance for complex performance improvement decisions

# Maintainability Improvements
/quality:improve legacy-modules --type maintainability --preview
# Architect persona analyzes structure and suggests maintainability improvements
# Preview mode shows changes before application for review

# Security Hardening
/quality:improve auth-service --type security --validate
# Security persona identifies vulnerabilities and applies security patterns
# Comprehensive validation ensures security improvements are effective
```

**Boundaries**:

**Will**:

- Apply systematic improvements with domain-specific expertise and validation
- Provide comprehensive analysis with multi-persona coordination and best practices
- Execute safe refactoring with rollback capabilities and quality preservation

**Will Not**:

- Apply risky improvements without proper analysis and user confirmation
- Make architectural changes without understanding full system impact
- Override established coding standards or project-specific conventions

**Related Commands**: `/quality:cleanup`, `/analyze:code`, `/dev:code-review`

---

## Session Commands

### /session:load

**Description**: Session lifecycle management with Serena MCP integration for project context loading

**Category**: session | **Complexity**: standard

**MCP Servers**: serena

**Triggers**:

- Session initialization and project context loading requests
- Cross-session persistence and memory retrieval needs
- Project activation and context management requirements
- Session lifecycle management and checkpoint loading scenarios

**Usage**:

```bash
/session:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]
```

**Behavioral Flow**:

1. **Initialize**: Establish Serena MCP connection and session context management
2. **Discover**: Analyze project structure and identify context loading requirements
3. **Load**: Retrieve project memories, checkpoints, and cross-session persistence data
4. **Activate**: Establish project context and prepare for development workflow
5. **Validate**: Ensure loaded context integrity and session readiness

**MCP Integration**:

- **Serena MCP**: Mandatory integration for project activation, memory retrieval, and session management
- **Memory Operations**: Cross-session persistence, checkpoint loading, and context restoration
- **Performance Critical**: <200ms for core operations, <1s for checkpoint creation

**Tool Coordination**:

- **activate_project**: Core project activation and context establishment
- **list_memories/read_memory**: Memory retrieval and session context loading
- **Read/Grep/Glob**: Project structure analysis and configuration discovery
- **Write**: Session context documentation and checkpoint creation

**Key Patterns**:

- **Project Activation**: Directory analysis → memory retrieval → context establishment
- **Session Restoration**: Checkpoint loading → context validation → workflow preparation
- **Memory Management**: Cross-session persistence → context continuity → development efficiency
- **Performance Critical**: Fast initialization → immediate productivity → session readiness

**Examples**:

```bash
# Basic Project Loading
/session:load
# Loads current directory project context with Serena memory integration
# Establishes session context and prepares for development workflow

# Specific Project Loading
/session:load /path/to/project --type project --analyze
# Loads specific project with comprehensive analysis
# Activates project context and retrieves cross-session memories

# Checkpoint Restoration
/session:load --type checkpoint --checkpoint session_123
# Restores specific checkpoint with session context
# Continues previous work session with full context preservation

# Dependency Context Loading
/session:load --type deps --refresh
# Loads dependency context with fresh analysis
# Updates project understanding and dependency mapping
```

**Boundaries**:

**Will**:

- Load project context using Serena MCP integration for memory management
- Provide session lifecycle management with cross-session persistence
- Establish project activation with comprehensive context loading

**Will Not**:

- Modify project structure or configuration without explicit permission
- Load context without proper Serena MCP integration and validation
- Override existing session context without checkpoint preservation

**Related Commands**: `/session:save`, `/session:reflect`

---

### /session:reflect

**Description**: Task reflection and validation using Serena MCP analysis capabilities

**Category**: special | **Complexity**: standard

**MCP Servers**: serena

**Triggers**:

- Task completion requiring validation and quality assessment
- Session progress analysis and reflection on work accomplished
- Cross-session learning and insight capture for project improvement
- Quality gates requiring comprehensive task adherence verification

**Usage**:

```bash
/session:reflect [--type task|session|completion] [--analyze] [--validate]
```

**Behavioral Flow**:

1. **Analyze**: Examine current task state and session progress using Serena reflection tools
2. **Validate**: Assess task adherence, completion quality, and requirement fulfillment
3. **Reflect**: Apply deep analysis of collected information and session insights
4. **Document**: Update session metadata and capture learning insights
5. **Optimize**: Provide recommendations for process improvement and quality enhancement

**MCP Integration**:

- **Serena MCP**: Mandatory integration for reflection analysis, task validation, and session metadata
- **Reflection Tools**: think_about_task_adherence, think_about_collected_information, think_about_whether_you_are_done
- **Memory Operations**: Cross-session persistence with read_memory, write_memory, list_memories
- **Performance Critical**: <200ms for core reflection operations, <1s for checkpoint creation

**Tool Coordination**:

- **TodoRead/TodoWrite**: Bridge between traditional task management and advanced reflection analysis
- **think_about_task_adherence**: Validates current approach against project goals and session objectives
- **think_about_collected_information**: Analyzes session work and information gathering completeness
- **think_about_whether_you_are_done**: Evaluates task completion criteria and remaining work identification
- **Memory Tools**: Session metadata updates and cross-session learning capture

**Key Patterns**:

- **Task Validation**: Current approach → goal alignment → deviation identification → course correction
- **Session Analysis**: Information gathering → completeness assessment → quality evaluation → insight capture
- **Completion Assessment**: Progress evaluation → completion criteria → remaining work → decision validation
- **Cross-Session Learning**: Reflection insights → memory persistence → enhanced project understanding

**Examples**:

```bash
# Task Adherence Reflection
/session:reflect --type task --analyze
# Validates current approach against project goals
# Identifies deviations and provides course correction recommendations

# Session Progress Analysis
/session:reflect --type session --validate
# Comprehensive analysis of session work and information gathering
# Quality assessment and gap identification for project improvement

# Completion Validation
/session:reflect --type completion
# Evaluates task completion criteria against actual progress
# Determines readiness for task completion and identifies remaining blockers
```

**Boundaries**:

**Will**:

- Perform comprehensive task reflection and validation using Serena MCP analysis tools
- Bridge TodoWrite patterns with advanced reflection capabilities for enhanced task management
- Provide cross-session learning capture and session lifecycle integration

**Will Not**:

- Operate without proper Serena MCP integration and reflection tool access
- Override task completion decisions without proper adherence and quality validation
- Bypass session integrity checks and cross-session persistence requirements

**Related Commands**: `/session:load`, `/session:save`

---

### /session:save

**Description**: Session lifecycle management with Serena MCP integration for session context persistence

**Category**: session | **Complexity**: standard

**MCP Servers**: serena

**Triggers**:

- Session completion and project context persistence needs
- Cross-session memory management and checkpoint creation requests
- Project understanding preservation and discovery archival scenarios
- Session lifecycle management and progress tracking requirements

**Usage**:

```bash
/session:save [--type session|learnings|context|all] [--summarize] [--checkpoint]
```

**Behavioral Flow**:

1. **Analyze**: Examine session progress and identify discoveries worth preserving
2. **Persist**: Save session context and learnings using Serena MCP memory management
3. **Checkpoint**: Create recovery points for complex sessions and progress tracking
4. **Validate**: Ensure session data integrity and cross-session compatibility
5. **Prepare**: Ready session context for seamless continuation in future sessions

**MCP Integration**:

- **Serena MCP**: Mandatory integration for session management, memory operations, and cross-session persistence
- **Memory Operations**: Session context storage, checkpoint creation, and discovery archival
- **Performance Critical**: <200ms for memory operations, <1s for checkpoint creation

**Tool Coordination**:

- **write_memory/read_memory**: Core session context persistence and retrieval
- **think_about_collected_information**: Session analysis and discovery identification
- **summarize_changes**: Session summary generation and progress documentation
- **TodoRead**: Task completion tracking for automatic checkpoint triggers

**Key Patterns**:

- **Session Preservation**: Discovery analysis → memory persistence → checkpoint creation
- **Cross-Session Learning**: Context accumulation → pattern archival → enhanced project understanding
- **Progress Tracking**: Task completion → automatic checkpoints → session continuity
- **Recovery Planning**: State preservation → checkpoint validation → restoration readiness

**Examples**:

```bash
# Basic Session Save
/session:save
# Saves current session discoveries and context to Serena MCP
# Automatically creates checkpoint if session exceeds 30 minutes

# Comprehensive Session Checkpoint
/session:save --type all --checkpoint
# Complete session preservation with recovery checkpoint
# Includes all learnings, context, and progress for session restoration

# Session Summary Generation
/session:save --summarize
# Creates session summary with discovery documentation
# Updates cross-session learning patterns and project insights

# Discovery-Only Persistence
/session:save --type learnings
# Saves only new patterns and insights discovered during session
# Updates project understanding without full session preservation
```

**Boundaries**:

**Will**:

- Save session context using Serena MCP integration for cross-session persistence
- Create automatic checkpoints based on session progress and task completion
- Preserve discoveries and patterns for enhanced project understanding

**Will Not**:

- Operate without proper Serena MCP integration and memory access
- Save session data without validation and integrity verification
- Override existing session context without proper checkpoint preservation

**Related Commands**: `/session:load`, `/session:reflect`

---

## Test Commands

### /test:generate-tests

**Description**: Generate comprehensive test suite with high coverage

**Category**: testing

**Agents**: test-automator, quality-engineer

**Triggers**:

- New feature implementation
- Low test coverage areas
- Regression testing needs
- API endpoint testing

**Usage**:

```bash
/test:generate-tests [path] [--type unit|integration|e2e|all] [--coverage-target 80]
```

**Test Generation Process**:

1. **Code Analysis**
   - Analyze code structure and dependencies
   - Identify testable units and edge cases
   - Map code paths and decision points
   - Determine test requirements

2. **Test Creation**
   - Generate unit tests for core logic
   - Create integration tests for component interactions
   - Build e2e tests for user workflows
   - Add edge case and error scenario tests

3. **Coverage Analysis**
   - Measure code coverage percentage
   - Identify uncovered code paths
   - Generate coverage reports
   - Suggest additional test cases

4. **Test Quality**
   - Ensure test independence and isolation
   - Implement proper setup and teardown
   - Add descriptive test names and documentation
   - Follow testing best practices

**Test Types**:

**Unit Tests**

- Individual function/method testing
- Mocked dependencies
- Fast execution
- High coverage of business logic

**Integration Tests**

- Component interaction testing
- Database and API integration
- Service communication
- Realistic scenarios

**End-to-End Tests**

- User workflow testing
- Full system integration
- Browser automation (if web app)
- Production-like environment

**Coverage Targets**:

- Unit tests: 80%+ coverage
- Integration tests: Key workflows covered
- E2e tests: Critical user paths validated

**Output**:

- Generated test files in appropriate directories
- Coverage report with metrics
- Test execution commands
- Suggested improvements for uncovered areas

**Example**:

```bash
/test:generate-tests src/api --type integration --coverage-target 90
```

**Boundaries**:

**Will**:

- Generate comprehensive test suites with high coverage targets
- Create tests following framework-specific best practices
- Provide coverage analysis and improvement recommendations

**Will Not**:

- Replace manual testing or QA processes
- Generate tests requiring complex domain knowledge without guidance
- Guarantee 100% coverage (some code may be untestable)

**Related Commands**: `/dev:test`, `/dev:code-review`, `/quality:improve`

---

## Tools Commands

### /tools:select

**Description**: Intelligent MCP tool selection based on complexity scoring and operation analysis

**Category**: special | **Complexity**: high

**MCP Servers**: serena, morphllm

**Triggers**:

- Operations requiring optimal MCP tool selection between Serena and Morphllm
- Meta-system decisions needing complexity analysis and capability matching
- Tool routing decisions requiring performance vs accuracy trade-offs
- Operations benefiting from intelligent tool capability assessment

**Usage**:

```bash
/tools:select [operation] [--analyze] [--explain]
```

**Behavioral Flow**:

1. **Parse**: Analyze operation type, scope, file count, and complexity indicators
2. **Score**: Apply multi-dimensional complexity scoring across various operation factors
3. **Match**: Compare operation requirements against Serena and Morphllm capabilities
4. **Select**: Choose optimal tool based on scoring matrix and performance requirements
5. **Validate**: Verify selection accuracy and provide confidence metrics

**MCP Integration**:

- **Serena MCP**: Optimal for semantic operations, LSP functionality, symbol navigation, and project context
- **Morphllm MCP**: Optimal for pattern-based edits, bulk transformations, and speed-critical operations
- **Decision Matrix**: Intelligent routing based on complexity scoring and operation characteristics

**Tool Coordination**:

- **get_current_config**: System configuration analysis for tool capability assessment
- **execute_sketched_edit**: Operation testing and validation for selection accuracy
- **Read/Grep**: Operation context analysis and complexity factor identification
- **Integration**: Automatic selection logic used by refactor, edit, implement, and improve commands

**Key Patterns**:

- **Direct Mapping**: Symbol operations → Serena, Pattern edits → Morphllm, Memory operations → Serena
- **Complexity Thresholds**: Score >0.6 → Serena, Score <0.4 → Morphllm, 0.4-0.6 → Feature-based
- **Performance Trade-offs**: Speed requirements → Morphllm, Accuracy requirements → Serena
- **Fallback Strategy**: Serena → Morphllm → Native tools degradation chain

**Examples**:

```bash
# Complex Refactoring Operation
/tools:select "rename function across 10 files" --analyze
# Analysis: High complexity (multi-file, symbol operations)
# Selection: Serena MCP (LSP capabilities, semantic understanding)

# Pattern-Based Bulk Edit
/tools:select "update console.log to logger.info across project" --explain
# Analysis: Pattern-based transformation, speed priority
# Selection: Morphllm MCP (pattern matching, bulk operations)

# Memory Management Operation
/tools:select "save project context and discoveries"
# Direct mapping: Memory operations → Serena MCP
# Rationale: Project context and cross-session persistence
```

**Boundaries**:

**Will**:

- Analyze operations and provide optimal tool selection between Serena and Morphllm
- Apply complexity scoring based on file count, operation type, and requirements
- Provide sub-100ms decision time with >95% selection accuracy

**Will Not**:

- Override explicit tool specifications when user has clear preference
- Select tools without proper complexity analysis and capability matching
- Compromise performance requirements for convenience or speed

**Related Commands**: All commands that leverage MCP tool routing

---

## Flag Reference

Flags are modular instruction packs stored in `flags/`. Enable or disable them by adding or removing
`@flags/<file>.md` lines in `FLAGS.md`. The TUI Flag Explorer (press `F`) and Flag Manager can toggle
these for you.

### Available Flag Modules

| Flag Module | Summary |
| --- | --- |
| `analysis-depth.md` | Control the depth and thoroughness of analysis and reasoning. |
| `auto-escalation.md` | Flags for automatic reasoning depth adjustment based on task signals. |
| `ci-cd.md` | Flags optimized for continuous integration and automated pipelines. |
| `cost-budget.md` | Flags for controlling API costs and optimizing token usage. |
| `database-operations.md` | Flags for database design, query optimization, and migration safety. |
| `debugging-trace.md` | Flags for debugging, verbose output, and execution tracing. |
| `documentation-generation.md` | Flags for generating and maintaining comprehensive documentation. |
| `domain-presets.md` | Quick presets for common development domains and workflows. |
| `execution-control.md` | Flags to control execution behavior, validation, and safety. |
| `git-workflow.md` | Flags for version control best practices, PR workflows, and commit discipline. |
| `interactive-control.md` | Flags for controlling user interaction and approval workflows. |
| `learning-education.md` | Flags for educational mode, explanations, and knowledge transfer. |
| `mcp-servers.md` | Flags to control Model Context Protocol server selection and usage. |
| `migration-upgrade.md` | Flags for safe migrations, dependency upgrades, and feature flag management. |
| `mode-activation.md` | Behavioral flags to activate specific execution modes and mindsets. |
| `output-optimization.md` | Flags for controlling output verbosity and scope. |
| `performance-optimization.md` | Flags for performance analysis, profiling, and optimization workflows. |
| `refactoring-safety.md` | Flags for safe code transformation and behavior preservation. |
| `security-hardening.md` | Flags for security-focused development, threat modeling, and compliance. |
| `testing-quality.md` | Flags for test-driven development, coverage enforcement, and quality gates. |
| `thinking-budget.md` | Control internal reasoning token allocation and cost trade-offs. |
| `visual-excellence.md` | Flags for UI/UX enhancement and visual polish across all platforms. |

For detailed toggling and profiles, see `guides/FLAGS_MANAGEMENT.md`.

---

## MCP Integration Patterns

### Sequential MCP Pattern

**Use Case**: Complex multi-step reasoning, systematic analysis

**Best For**:

- Implementation workflow planning
- Complex estimation and breakdown
- Multi-component explanation
- Requirements discovery

**Commands Using Sequential**:

- `/design:workflow`
- `/analyze:estimate`
- `/analyze:explain`
- `/orchestrate:brainstorm`
- `/orchestrate:task`
- `/docs:index`
- `/quality:cleanup`
- `/quality:improve`

**Integration Pattern**:

```
User Request → Sequential Analysis → Structured Breakdown → Systematic Execution
```

### Context7 MCP Pattern

**Use Case**: Framework-specific patterns, official documentation

**Best For**:

- Framework-specific implementation
- Library best practices
- Official pattern adherence
- Technology validation

**Commands Using Context7**:

- `/dev:implement`
- `/design:workflow`
- `/analyze:estimate`
- `/analyze:explain`
- `/orchestrate:brainstorm`
- `/orchestrate:task`
- `/docs:index`
- `/quality:cleanup`
- `/quality:improve`

**Integration Pattern**:

```
Framework Detection → Context7 Lookup → Official Patterns → Implementation
```

### Magic MCP Pattern

**Use Case**: UI component generation, design systems

**Best For**:

- React/Vue/Angular components
- Design system integration
- UI implementation
- Frontend development

**Commands Using Magic**:

- `/dev:implement`
- `/design:workflow`
- `/orchestrate:brainstorm`
- `/orchestrate:task`

**Integration Pattern**:

```
Component Request → Magic Generation → Design System → Framework Integration
```

### Playwright MCP Pattern

**Use Case**: Browser testing, E2E validation

**Best For**:

- End-to-end testing
- Browser automation
- Visual validation
- Cross-browser testing

**Commands Using Playwright**:

- `/dev:test`
- `/dev:build`
- `/dev:implement`
- `/design:workflow`
- `/orchestrate:brainstorm`
- `/orchestrate:task`

**Integration Pattern**:

```
Test Request → Playwright Setup → Browser Automation → Validation Report
```

### Serena MCP Pattern

**Use Case**: Project memory, cross-session persistence

**Best For**:

- Session management
- Project context
- Memory operations
- Symbol navigation

**Commands Using Serena**:

- `/session:load`
- `/session:save`
- `/session:reflect`
- `/design:workflow`
- `/orchestrate:brainstorm`
- `/orchestrate:task`
- `/tools:select`

**Integration Pattern**:

```
Session Start → Serena Activation → Context Loading → Memory Persistence
```

### Morphllm MCP Pattern

**Use Case**: Pattern-based bulk edits, transformations

**Best For**:

- Multi-file refactoring
- Pattern replacements
- Bulk transformations
- Speed-critical edits

**Commands Using Morphllm**:

- `/design:workflow`
- `/orchestrate:brainstorm`
- `/orchestrate:task`
- `/tools:select`

**Integration Pattern**:

```
Pattern Detection → Morphllm Processing → Bulk Transform → Validation
```

---

## Common Workflows

### Feature Development Workflow

```bash
# 1. Requirements Discovery
/orchestrate:brainstorm "user profile management" --strategy agile

# 2. Design System Architecture
/design:system user-profile --type component --format spec

# 3. Generate Implementation Workflow
/design:workflow user-profile-spec.md --strategy systematic

# 4. Implement Feature
/dev:implement user-profile-component --framework react --with-tests

# 5. Run Tests
/dev:test src/components/UserProfile --type unit --coverage

# 6. Code Review
/dev:code-review src/components/UserProfile --focus all

# 7. Optimize and Improve
/quality:improve src/components/UserProfile --type quality --safe

# 8. Generate Documentation
/docs:generate src/components/UserProfile --type external --style detailed
```

### Code Quality Improvement Workflow

```bash
# 1. Analyze Current Code Quality
/analyze:code src/ --focus quality --depth deep

# 2. Clean Up Dead Code and Imports
/quality:cleanup src/ --type all --safe

# 3. Apply Systematic Improvements
/quality:improve src/ --type quality --safe

# 4. Security Audit
/analyze:security-scan src/ --standard OWASP

# 5. Performance Optimization
/quality:improve src/ --type performance --interactive

# 6. Code Review
/dev:code-review src/ --focus all

# 7. Generate Tests
/test:generate-tests src/ --type all --coverage-target 85

# 8. Run Test Suite
/dev:test --type all --coverage
```

### Project Documentation Workflow

```bash
# 1. Generate Project Structure Documentation
/docs:index . --type structure --format md

# 2. Generate API Documentation
/docs:index src/api --type api --format json

# 3. Generate Component Documentation
/docs:generate src/components --type external --style detailed

# 4. Explain Complex Systems
/analyze:explain src/core/engine --level advanced --format interactive

# 5. Create User Guides
/docs:generate src/features --type guide --style brief

# 6. Update README
/docs:index . --type readme
```

### Deployment Preparation Workflow

```bash
# 1. Run Full Test Suite
/dev:test --type all --coverage

# 2. Security Audit
/analyze:security-scan src/ --standard OWASP

# 3. Performance Analysis
/analyze:code src/ --focus performance --depth deep

# 4. Build Optimization
/dev:build --type prod --clean --optimize

# 5. Code Review
/dev:code-review src/ --focus all

# 6. Prepare Release
/deploy:prepare-release 1.2.0 --type minor

# 7. Generate Documentation
/docs:index . --type all --format md
```

### Troubleshooting Workflow

```bash
# 1. Analyze the Issue
/analyze:troubleshoot "API timeout errors" --type performance --trace

# 2. Review Affected Code
/dev:code-review src/api --focus performance

# 3. Analyze Code Quality
/analyze:code src/api --focus performance --depth deep

# 4. Apply Fixes
/quality:improve src/api --type performance --safe

# 5. Test Changes
/dev:test src/api --type integration --coverage

# 6. Validate Fix
/analyze:troubleshoot "API timeout errors" --type performance --validate
```

### Session Management Workflow

```bash
# 1. Load Project Context
/session:load --type project --analyze

# 2. Work on Tasks
# ... perform development work ...

# 3. Reflect on Progress
/session:reflect --type session --validate

# 4. Save Session Context
/session:save --type all --checkpoint

# 5. Next Session - Restore Context
/session:load --type checkpoint --checkpoint session_123
```

### Enterprise Development Workflow

```bash
# 1. Requirements Discovery
/orchestrate:brainstorm "enterprise analytics platform" --strategy enterprise --depth deep

# 2. Architectural Planning
/design:system analytics-platform --type architecture --format diagram

# 3. Estimate Development
/analyze:estimate "analytics platform implementation" --type time --unit weeks --breakdown

# 4. Generate Implementation Workflow
/design:workflow analytics-platform-prd.md --strategy enterprise --validate

# 5. Complex Task Orchestration
/orchestrate:spawn "implement analytics platform" --strategy adaptive --depth deep

# 6. Security Scan
/analyze:security-scan src/ --standard SOC2

# 7. Comprehensive Testing
/dev:test --type all --coverage

# 8. Deployment Preparation
/deploy:prepare-release 2.0.0 --type major
```

---

## Best Practices

### Command Selection

1. **Start Simple**: Use basic commands for straightforward tasks
2. **Escalate Complexity**: Move to orchestration commands for complex multi-domain tasks
3. **Leverage MCP**: Enable relevant MCP servers for specialized capabilities
4. **Use Flags**: Apply appropriate flags to fine-tune command behavior

### Workflow Organization

1. **Plan First**: Use brainstorm and design commands before implementation
2. **Iterate**: Use improvement and cleanup commands regularly
3. **Validate Often**: Run tests and reviews frequently during development
4. **Document Continuously**: Generate docs alongside implementation

### Session Management

1. **Load Context**: Start sessions with `/session:load`
2. **Reflect Regularly**: Use `/session:reflect` to validate progress
3. **Save Progress**: End sessions with `/session:save --checkpoint`
4. **Persist Learning**: Capture insights for cross-session enhancement

### Quality Assurance

1. **Test Early**: Generate and run tests throughout development
2. **Review Regularly**: Use code review commands frequently
3. **Security First**: Run security scans before deployment
4. **Performance Matters**: Include performance analysis in workflow

---

## Command Index by Complexity

### Basic (Complexity: basic)

- `/analyze:code`
- `/analyze:troubleshoot`
- `/design:system`
- `/dev:git`
- `/docs:generate`

### Standard (Complexity: standard)

- `/analyze:estimate`
- `/analyze:explain`
- `/dev:implement`
- `/docs:index`
- `/quality:cleanup`
- `/quality:improve`
- `/session:load`
- `/session:reflect`
- `/session:save`

### Enhanced (Complexity: enhanced)

- `/dev:build`
- `/dev:test`

### Advanced (Complexity: advanced)

- `/design:workflow`
- `/orchestrate:brainstorm`
- `/orchestrate:task`

### High (Complexity: high)

- `/orchestrate:spawn`
- `/tools:select`

---

## Troubleshooting

### Common Issues

**MCP Server Not Available**

- Solution: Check MCP server configuration and ensure server is running
- Related: `--no-mcp` flag to fall back to native tools

**Command Not Responding**

- Solution: Check for syntax errors in command usage
- Related: Use `--help` flag or consult this documentation

**Unexpected Results**

- Solution: Try adding `--validate` or `--safe` flags
- Related: Use `--interactive` for guided workflows

**Performance Issues**

- Solution: Use `--token-efficient` or `--uc` flags
- Related: Adjust `--concurrency` settings

### Getting Help

- Check command-specific documentation sections above
- Review flag reference for appropriate modifiers
- Consult common workflows for usage patterns
- Use `--explain` flag where available for command reasoning

---

**Last Updated**: 2025-10-17
**Version**: 1.0.0
**Total Commands**: 26 slash commands + 8 agent-based commands
