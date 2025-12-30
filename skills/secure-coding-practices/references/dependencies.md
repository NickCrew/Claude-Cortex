# Secure Dependencies & Supply Chain

## Dependency Auditing

```bash
# Regular vulnerability scanning
npm audit
npm audit fix

# Use production dependencies only
npm audit --production

# Advanced scanning with Snyk
npx snyk test
npx snyk monitor

# Check for outdated packages
npm outdated

# Automated dependency updates with security focus
npx npm-check-updates -u
```

## Dependency Validation

```javascript
// package.json: Lock dependency versions
{
  "dependencies": {
    "express": "4.18.2", // Exact version, not "^4.18.2"
    "jsonwebtoken": "9.0.0"
  }
}

// Use package-lock.json or yarn.lock
// Commit lock files to version control

// Verify package integrity
npm ci # Use in CI/CD instead of npm install
```

## Subresource Integrity (SRI)

```html
<!-- VULNERABLE: Unverified CDN resource -->
<script src="https://cdn.example.com/library.js"></script>

<!-- SECURE: SRI hash verification -->
<script
  src="https://cdn.example.com/library.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
  crossorigin="anonymous">
</script>
```

## Private Package Registry

```javascript
// .npmrc: Use private registry for sensitive packages
registry=https://registry.npmjs.org/
@mycompany:registry=https://npm.internal.company.com/
//npm.internal.company.com/:_authToken=${NPM_TOKEN}

// Enable audit for private packages
audit=true
audit-level=moderate
```

## Supply Chain Security Checklist

- [ ] Run npm audit regularly (weekly minimum)
- [ ] Lock dependency versions in package.json
- [ ] Commit package-lock.json to version control
- [ ] Use npm ci in CI/CD pipelines
- [ ] Monitor dependencies with Snyk/Dependabot
- [ ] Verify package integrity with SRI for CDN resources
- [ ] Review dependency licenses for compliance
- [ ] Audit transitive dependencies
- [ ] Use private registry for internal packages
- [ ] Implement automated security scanning in CI/CD

## Best Practices

1. **Pin versions** - Use exact versions, not ranges (^, ~)
2. **Audit frequently** - Run npm audit before deployments
3. **Update regularly** - Balance security updates with stability
4. **Minimize dependencies** - Less code = smaller attack surface
5. **Verify sources** - Check package maintainers and download counts
6. **Use SRI** - Verify integrity of CDN resources
7. **Monitor continuously** - Automated alerts for new vulnerabilities
8. **Review changes** - Check changelogs before updating dependencies
