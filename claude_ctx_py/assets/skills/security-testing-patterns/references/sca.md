# Software Composition Analysis (SCA)

## Dependency Scanning

### npm audit
```bash
# Basic vulnerability check
npm audit

# Generate detailed JSON report
npm audit --json > security-audit.json

# Fix automatically
npm audit fix

# Fix with breaking changes
npm audit fix --force
```

### Snyk Integration
```bash
# Install Snyk CLI
npm install -g snyk

# Authenticate
snyk auth

# Test for vulnerabilities
snyk test

# Monitor project
snyk monitor

# Test with custom severity threshold
snyk test --severity-threshold=high

# Generate JSON report
snyk test --json > snyk-report.json
```

### GitHub Dependabot Configuration
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "security"
      - "dependencies"
    # Security updates only
    versioning-strategy: increase-if-necessary
```

### OWASP Dependency-Check
```bash
# Run dependency check
dependency-check --project "MyApp" \
  --scan ./package.json \
  --format JSON \
  --out ./reports

# With suppression file
dependency-check --project "MyApp" \
  --scan ./package.json \
  --suppression ./dependency-check-suppressions.xml \
  --format HTML \
  --out ./reports
```
