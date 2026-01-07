# Prevention Strategies

## Defense in Depth

Layer multiple security controls so failure of one doesn't compromise the system:

1. **Network layer** - Firewalls, segmentation, IDS/IPS
2. **Application layer** - Input validation, output encoding, authentication
3. **Data layer** - Encryption, access control, backups
4. **Monitoring layer** - Logging, alerting, incident response

## Secure by Default

- Deny all access by default, explicitly grant
- Fail securely (errors should not expose information)
- Minimize attack surface (disable unused features)
- Least privilege for all accounts and services
- No security through obscurity
- Complete mediation (check every access)
- Separation of duties

## Input Validation Strategy

```javascript
// Comprehensive validation approach
function validateInput(input, schema) {
  // 1. Type check
  if (typeof input !== schema.type) return false;

  // 2. Length/range check
  if (schema.maxLength && input.length > schema.maxLength) return false;

  // 3. Format validation (regex)
  if (schema.pattern && !schema.pattern.test(input)) return false;

  // 4. Allow-list validation
  if (schema.allowedValues && !schema.allowedValues.includes(input)) return false;

  return true;
}

// Example usage
const emailSchema = {
  type: 'string',
  maxLength: 254,
  pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
};

if (!validateInput(req.body.email, emailSchema)) {
  return res.status(400).json({ error: 'Invalid email format' });
}
```

## Best Practices Summary

1. **Access Control**: Implement RBAC/ABAC, deny by default, verify on every request
2. **Cryptography**: Use strong algorithms (AES-256, RSA-2048+), never roll your own crypto
3. **Injection Prevention**: Parameterized queries, input validation, output encoding
4. **Secure Design**: Threat modeling, security requirements, defense in depth
5. **Configuration**: Hardened defaults, security headers, minimal attack surface
6. **Dependencies**: Regular updates, vulnerability scanning, SCA tools
7. **Authentication**: MFA, strong passwords, secure session management
8. **Integrity**: Code signing, integrity verification, secure CI/CD
9. **Logging**: Comprehensive security event logging, monitoring, alerting
10. **SSRF Prevention**: URL validation, network segmentation, allow-lists

## Security Testing Checklist

- [ ] Static Application Security Testing (SAST)
- [ ] Dynamic Application Security Testing (DAST)
- [ ] Interactive Application Security Testing (IAST)
- [ ] Software Composition Analysis (SCA)
- [ ] Penetration testing (manual + automated)
- [ ] Security code review
- [ ] Threat modeling and risk assessment
- [ ] Dependency vulnerability scanning
- [ ] Configuration security audit
- [ ] Authentication and authorization testing
- [ ] Session management testing
- [ ] Input validation testing
- [ ] Error handling and logging review
- [ ] Cryptography implementation audit
