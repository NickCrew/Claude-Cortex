# A08: Software and Data Integrity Failures

**Description:** Code and infrastructure that doesn't protect against integrity violations.

**Focus:** Insecure CI/CD, auto-updates, unsigned objects, insecure deserialization

## Vulnerabilities

```javascript
// VULNERABLE: Accepting unsigned packages
npm install untrusted-package

// SECURE: Verify package integrity
// Use npm audit, lock files (package-lock.json)
// Verify checksums and signatures

// VULNERABLE: Insecure deserialization
const userData = JSON.parse(req.cookies.user);
eval(userData.code); // Arbitrary code execution

// SECURE: Avoid deserialization of untrusted data
const userData = JSON.parse(req.cookies.user);
// Validate schema, never execute code from untrusted sources
```

## Prevention

- Use digital signatures for software/data verification
- Verify integrity of downloads (checksums, GPG)
- Implement secure CI/CD pipelines with segregation
- Review code and configuration changes
- Use libraries that prevent deserialization attacks
- Use lock files for dependency versions (package-lock.json, yarn.lock)
- Implement Software Bill of Materials (SBOM)
- Verify artifacts before deployment
- Separate build, test, and production environments
- Use signed commits and tags in version control
