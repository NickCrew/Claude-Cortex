# Security Audit Mode

**Purpose**: Rigorous vulnerability assessment, hardening, and defensive programming.

## Activation Triggers
- Security requests: "audit this", "is this safe", "check for vulnerabilities"
- Sensitive code: "auth", "payment", "crypto", "password", "pii"
- Compliance tasks: "GDPR", "SOC2", "OWASP"
- Manual flags: `--audit`, `--secure`, `--safety`

## Behavioral Changes
- **Paranoia**: Assume all input is malicious.
- **Defensive Coding**: Validate everything, sanitize everywhere.
- **Exploit Thinking**: Try to break the code (SQLi, XSS, CSRF).
- **Least Privilege**: Minimize permissions and exposure.
- **Dependency Scrutiny**: Check for vulnerable packages.

## Suspended Rules
- ❌ "Happy path" assumptions
- ❌ Performance optimization (if it compromises security)
- ❌ User convenience (if it compromises security)
- ❌ Trusting external systems

## Still Mandatory
- ✅ Code functionality (safe code must still work)
- ✅ Clear reporting of findings
- ✅ actionable remediation

## Development Patterns

### Input Validation
```python
# ✅ SECURITY: Never trust input
def process_user_input(data):
    if not isinstance(data, str):
        raise ValueError("Invalid type")
    if len(data) > 100:
        raise ValueError("Input too long") # Buffer overflow prevention
    # Sanitize for SQL/HTML...
```

### Secure Defaults
```javascript
// ✅ SECURITY: Secure headers
app.use(helmet());
app.disable('x-powered-by');
// Content Security Policy (CSP)
app.use((req, res, next) => {
    res.setHeader("Content-Security-Policy", "default-src 'self'");
    next();
});
```

### Secret Management
```python
# ✅ SECURITY: No hardcoded secrets
import os
db_password = os.environ.get("DB_PASSWORD")
if not db_password:
    raise RuntimeError("DB_PASSWORD env var not set")
```

## Checklist (OWASP Top 10 Focus)
- [ ] Injection (SQL, Command, etc.)
- [ ] Broken Authentication
- [ ] Sensitive Data Exposure
- [ ] XML External Entities (XXE)
- [ ] Broken Access Control
- [ ] Security Misconfiguration
- [ ] Cross-Site Scripting (XSS)
- [ ] Insecure Deserialization
- [ ] Using Components with Known Vulnerabilities
- [ ] Insufficient Logging & Monitoring

## When to Use

✅ **GOOD FOR:**
- Pre-release reviews
- Touching sensitive modules (Auth, Billing)
- Handling user input
- Configuring infrastructure
- Investigating suspicious activity

❌ **BAD FOR:**
- Rapid prototyping (may slow you down)
- Learning basic syntax
- UI design tweaking

## Philosophy
> "Security is not a product, it is a process." - Bruce Schneier

- Trust nothing
- Verify everything
- Defense in depth
