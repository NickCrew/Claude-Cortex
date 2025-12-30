# A06: Vulnerable and Outdated Components

**Description:** Using components with known vulnerabilities or outdated versions.

## Detection

```bash
# Check for known vulnerabilities
npm audit
npm audit fix

# Use security scanning tools
npx snyk test
npx retire

# Check outdated packages
npm outdated
```

## Prevention

- Remove unused dependencies
- Monitor CVE databases (NVD, Snyk, GitHub Security)
- Subscribe to security bulletins for components
- Use Software Composition Analysis (SCA) tools
- Obtain components from official, trusted sources only
- Prefer signed packages with active maintenance
- Automate dependency updates with tools like Dependabot
- Test updates in staging before production
- Maintain inventory of all components and versions
- Establish vulnerability disclosure process
