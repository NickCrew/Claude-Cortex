# Reference: prepare-release

# /deploy:prepare-release - Release Preparation

## Purpose
Systematically prepare application for production release with all necessary checks and documentation.

## Triggers
- Version release requests
- Production deployment preparation
- Release candidate creation
- Deployment readiness validation

## Usage
```
/deploy:prepare-release [version] [--type major|minor|patch]
```

## Release Preparation Process

### 1. Pre-Release Validation
- Run full test suite (unit, integration, e2e)
- Execute security audit
- Perform performance benchmarking
- Validate configuration for production
- Check dependency vulnerabilities

### 2. Version Management
- Update version numbers (package.json, etc.)
- Generate changelog from commits
- Tag release in version control
- Update API documentation versions

### 3. Build Optimization
- Create production build
- Optimize bundle size
- Generate source maps
- Minify and compress assets
- Validate build artifacts

### 4. Documentation Updates
- Update README if needed
- Generate API documentation
- Create release notes
- Document breaking changes
- Update migration guides

### 5. Deployment Planning
- Create deployment checklist
- Generate rollback plan
- Document environment variables
- Prepare database migrations
- Configure monitoring and alerts

### 6. Final Checks
- Smoke test production build
- Verify all services health
- Validate external integrations
- Check SSL certificates
- Review security headers

## Checklist Output

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

## Personas (Thinking Modes)
- **deployment-engineer**: Deployment strategy, infrastructure, rollback planning, production readiness
- **quality-engineer**: Quality validation, testing standards, release criteria
- **security-specialist**: Security audit, vulnerability assessment, production security

## Delegation Protocol

**This command USUALLY delegates** - Release preparation is comprehensive multi-phase work.

**When to delegate** (use Task tool):
- ✅ Any release preparation (always multiple phases)
- ✅ Production deployment validation
- ✅ Security and quality audits required
- ✅ Comprehensive checklist execution

**Available subagents**:
- **general-purpose**: Version management, build optimization, documentation
- **code-reviewer**: Pre-release code quality validation
- **security-auditor**: Security audit and vulnerability scanning
- **test-automator**: Full test suite execution and validation

**Delegation strategy for release preparation**:
```xml
<function_calls>
<!-- Phase 1: Pre-Release Validation (Parallel) -->
<invoke name="Task">
  <subagent_type>test-automator</subagent_type>
  <description>Run full test suite</description>
  <prompt>
    Execute comprehensive testing:
    - Unit tests
    - Integration tests
    - E2E tests
    - Performance benchmarks
    All must pass for release.
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>security-auditor</subagent_type>
  <description>Execute security audit</description>
  <prompt>
    Comprehensive security audit:
    - Dependency vulnerabilities
    - OWASP Top 10 check
    - Production configuration
    - Security headers
    Critical issues block release.
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Final quality validation</description>
  <prompt>
    Pre-release quality check:
    - Code quality assessment
    - Performance review
    - Best practices compliance
    Quality-engineer thinking.
  </prompt>
</invoke>

<!-- Phase 2: Release Preparation (Sequential after validation) -->
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Prepare release artifacts</description>
  <prompt>
    Release preparation for version: [version]
    Type: [major|minor|patch]
    - Version management
    - Changelog generation
    - Production build
    - Documentation updates
    - Deployment planning
    Deployment-engineer thinking.
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple version bump (no full release)
- ❌ Documentation-only update

## Tool Coordination
- **Task tool**: Launches subagents for comprehensive release preparation (4 subagents)
- **Bash**: Build commands, git operations (by subagents)
- **Read/Write**: Documentation, changelog (by subagents)
- **TodoWrite**: Release checklist tracking

## Example
```
/deploy:prepare-release 2.1.0 --type minor
```
