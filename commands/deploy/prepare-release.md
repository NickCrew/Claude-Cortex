---
name: prepare-release
description: Prepare application for production deployment
category: deployment
agents: [deployment-engineer, quality-engineer]
---

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

## Agents Used
- `deployment-engineer`: Deployment preparation and planning
- `quality-engineer`: Final quality validation

## Example
```
/deploy:prepare-release 2.1.0 --type minor
```