---
name: owasp-top-10
description: OWASP Top 10 security vulnerabilities with detection and remediation patterns. Use when conducting security audits, implementing secure coding practices, or reviewing code for common security vulnerabilities.
---

# OWASP Top 10 Security Vulnerabilities

Expert guidance for identifying, preventing, and remediating the most critical web application security risks based on OWASP Top 10 2021.

## When to Use This Skill

- Conducting security audits and code reviews
- Implementing secure coding practices in new features
- Reviewing authentication and authorization systems
- Assessing input validation and sanitization
- Evaluating third-party dependencies for vulnerabilities
- Designing security controls and defense-in-depth strategies
- Preparing for security certifications or compliance audits
- Investigating security incidents or suspicious behavior
- Training teams on common security vulnerabilities

## OWASP Top 10 2021 Overview

**Rank by Risk Severity:**
1. A01:2021 - Broken Access Control (moved from #5)
2. A02:2021 - Cryptographic Failures (formerly Sensitive Data Exposure)
3. A03:2021 - Injection (dropped from #1)
4. A04:2021 - Insecure Design (new category)
5. A05:2021 - Security Misconfiguration
6. A06:2021 - Vulnerable and Outdated Components
7. A07:2021 - Identification and Authentication Failures
8. A08:2021 - Software and Data Integrity Failures (new category)
9. A09:2021 - Security Logging and Monitoring Failures
10. A10:2021 - Server-Side Request Forgery (SSRF) (new category)

## Critical Vulnerabilities (Top 5)

### A01: Broken Access Control

**Description:** Users can act outside their intended permissions, accessing unauthorized data or functions.

**Common Patterns:**
```javascript
// VULNERABLE: Direct object reference without authorization
app.get('/api/users/:id/profile', (req, res) => {
  const profile = db.getProfile(req.params.id);
  res.json(profile); // No check if user can access this profile
});

// VULNERABLE: Path traversal
app.get('/files/:filename', (req, res) => {
  res.sendFile(`./uploads/${req.params.filename}`);
  // Attack: GET /files/../../etc/passwd
});

// VULNERABLE: Missing function-level access control
app.post('/api/admin/users', (req, res) => {
  // No admin role check
  createUser(req.body);
});
```

**Secure Implementation:**
```javascript
// SECURE: Verify authorization for each request
app.get('/api/users/:id/profile', authenticate, (req, res) => {
  if (req.user.id !== req.params.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const profile = db.getProfile(req.params.id);
  res.json(profile);
});

// SECURE: Sanitize file paths
const path = require('path');
app.get('/files/:filename', authenticate, (req, res) => {
  const filename = path.basename(req.params.filename);
  const filepath = path.join(__dirname, 'uploads', filename);

  if (!filepath.startsWith(path.join(__dirname, 'uploads'))) {
    return res.status(400).json({ error: 'Invalid path' });
  }
  res.sendFile(filepath);
});

// SECURE: Function-level access control
app.post('/api/admin/users', authenticate, requireRole('admin'), (req, res) => {
  createUser(req.body);
});
```

**Prevention Checklist:**
- Deny by default, explicit allow for authorized access
- Implement attribute-based or role-based access control (ABAC/RBAC)
- Disable directory listing on web servers
- Log access control failures and alert on repeated violations
- Invalidate JWT tokens on logout
- Rate-limit API endpoints to minimize automated attacks

### A02: Cryptographic Failures

**Description:** Exposing sensitive data due to missing or weak cryptography.

**Common Vulnerabilities:**
```javascript
// VULNERABLE: Storing passwords in plaintext
db.createUser({ username, password: password });

// VULNERABLE: Weak hashing
const hash = crypto.createHash('md5').update(password).digest('hex');

// VULNERABLE: Transmitting sensitive data over HTTP
fetch('http://api.example.com/payment', {
  body: JSON.stringify({ cardNumber, cvv })
});

// VULNERABLE: Hardcoded secrets
const API_KEY = 'sk_live_a3f7c9b2d8e1f4g6h9';
```

**Secure Implementation:**
```javascript
// SECURE: Strong password hashing with bcrypt
const bcrypt = require('bcrypt');
const saltRounds = 12;
const hash = await bcrypt.hash(password, saltRounds);
db.createUser({ username, passwordHash: hash });

// Verification
const isValid = await bcrypt.compare(password, user.passwordHash);

// SECURE: Encrypt sensitive data at rest
const crypto = require('crypto');
const algorithm = 'aes-256-gcm';
const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex'); // 32 bytes

function encrypt(text) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  const encrypted = Buffer.concat([cipher.update(text, 'utf8'), cipher.final()]);
  const authTag = cipher.getAuthTag();
  return { iv: iv.toString('hex'), authTag: authTag.toString('hex'), data: encrypted.toString('hex') };
}

// SECURE: Use environment variables for secrets
require('dotenv').config();
const apiKey = process.env.API_KEY;
```

**Prevention Checklist:**
- Classify data based on sensitivity (PII, financial, health)
- Encrypt all sensitive data at rest (AES-256)
- Encrypt data in transit with TLS 1.2+ only
- Use strong adaptive hashing (bcrypt, scrypt, Argon2)
- Rotate keys regularly and use proper key management (KMS)
- Disable caching for sensitive data responses
- Apply data retention policies and secure deletion

### A03: Injection

**Description:** Untrusted data sent to interpreters as part of commands or queries.

**Types:** SQL, NoSQL, OS command, LDAP, XPath, template injection

**SQL Injection:**
```javascript
// VULNERABLE: String concatenation
const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
// Attack: username = "admin'--"

// SECURE: Parameterized queries
const query = 'SELECT * FROM users WHERE username = ? AND password = ?';
db.query(query, [username, password]);

// SECURE: ORM with parameterization
const user = await User.findOne({
  where: { username, password }
});
```

**NoSQL Injection:**
```javascript
// VULNERABLE: Direct object injection
db.collection('users').findOne({
  username: req.body.username,
  password: req.body.password
});
// Attack: { "username": "admin", "password": { "$ne": null } }

// SECURE: Type validation and sanitization
const { username, password } = req.body;
if (typeof username !== 'string' || typeof password !== 'string') {
  return res.status(400).json({ error: 'Invalid input' });
}
db.collection('users').findOne({ username, password });
```

**Command Injection:**
```javascript
// VULNERABLE: Shell command with user input
const { exec } = require('child_process');
exec(`ping -c 4 ${req.body.host}`, callback);
// Attack: host = "google.com; rm -rf /"

// SECURE: Use safe APIs and validation
const { spawn } = require('child_process');
const host = req.body.host;
if (!/^[a-zA-Z0-9.-]+$/.test(host)) {
  return res.status(400).json({ error: 'Invalid host' });
}
const ping = spawn('ping', ['-c', '4', host]);
```

**Prevention Checklist:**
- Use parameterized queries or ORMs exclusively
- Validate all input against strict allow-lists
- Escape special characters for the specific interpreter
- Use LIMIT in SQL queries to minimize data exposure
- Implement least privilege for database accounts
- Use static analysis tools (SAST) to detect injection

### A04: Insecure Design

**Description:** Missing or ineffective security controls in design phase.

**Threat Modeling Examples:**
```javascript
// INSECURE DESIGN: No rate limiting on sensitive endpoints
app.post('/api/login', async (req, res) => {
  const user = await authenticate(req.body);
  // Vulnerable to credential stuffing
});

// SECURE DESIGN: Rate limiting + CAPTCHA
const rateLimit = require('express-rate-limit');
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  skipSuccessfulRequests: true
});

app.post('/api/login', loginLimiter, async (req, res) => {
  if (req.session.failedAttempts >= 3) {
    const captchaValid = await verifyCaptcha(req.body.captcha);
    if (!captchaValid) {
      return res.status(400).json({ error: 'Invalid CAPTCHA' });
    }
  }
  const user = await authenticate(req.body);
});

// INSECURE DESIGN: No transaction limits
app.post('/api/transfer', authenticate, async (req, res) => {
  await transferFunds(req.user.id, req.body.to, req.body.amount);
});

// SECURE DESIGN: Transaction limits + verification
app.post('/api/transfer', authenticate, async (req, res) => {
  const { to, amount } = req.body;

  // Business logic validation
  if (amount > 10000) {
    const verified = await require2FA(req.user);
    if (!verified) {
      return res.status(403).json({ error: '2FA required for large transfers' });
    }
  }

  // Daily limit check
  const dailyTotal = await getDailyTransferTotal(req.user.id);
  if (dailyTotal + amount > 50000) {
    return res.status(403).json({ error: 'Daily limit exceeded' });
  }

  await transferFunds(req.user.id, to, amount);
});
```

**Design Principles:**
- Establish secure development lifecycle (SDLC)
- Use threat modeling (STRIDE, PASTA, OCTAVE)
- Write security user stories and abuse cases
- Implement defense in depth (layered security)
- Separate tenants and layers by design
- Limit resource consumption per user/tenant

### A05: Security Misconfiguration

**Description:** Missing hardening, unnecessary features, default credentials, verbose errors.

**Common Issues:**
```javascript
// VULNERABLE: Verbose error messages
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack // Exposes internal structure
  });
});

// SECURE: Generic error messages
app.use((err, req, res, next) => {
  console.error(err); // Log internally only
  res.status(500).json({
    error: 'Internal server error',
    requestId: req.id
  });
});

// VULNERABLE: Unnecessary features enabled
app.use(express.static('public', { dotfiles: 'allow' }));
// Exposes .env, .git files

// SECURE: Restrict access
app.use(express.static('public', {
  dotfiles: 'deny',
  index: false // Disable directory listing
}));

// VULNERABLE: Missing security headers
app.get('/', (req, res) => {
  res.send('<h1>Welcome</h1>');
});

// SECURE: Security headers
const helmet = require('helmet');
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

**Prevention Checklist:**
- Implement automated hardening processes
- Remove unused features, frameworks, dependencies
- Review and update configurations regularly
- Use security headers (CSP, HSTS, X-Frame-Options)
- Disable default accounts and change default passwords
- Segment application architecture (containers, cloud)
- Keep error messages generic, log details internally

## Additional Vulnerabilities (6-10)

### A06: Vulnerable and Outdated Components

**Detection:**
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

**Prevention:**
- Remove unused dependencies
- Monitor CVE databases (NVD, Snyk, GitHub Security)
- Subscribe to security bulletins for components
- Use Software Composition Analysis (SCA) tools
- Obtain components from official, trusted sources only
- Prefer signed packages with active maintenance

### A07: Identification and Authentication Failures

**Common Weaknesses:**
```javascript
// VULNERABLE: Weak session management
app.post('/login', async (req, res) => {
  const user = await authenticate(req.body);
  req.session.userId = user.id; // Predictable session ID
  req.session.cookie.secure = false; // Transmitted over HTTP
});

// SECURE: Strong session management
const session = require('express-session');
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true, // HTTPS only
    httpOnly: true, // No JavaScript access
    maxAge: 3600000, // 1 hour
    sameSite: 'strict'
  },
  name: 'sessionId', // Custom name, not default 'connect.sid'
}));
```

**Best Practices:**
- Implement multi-factor authentication (MFA)
- Use strong password policies (length, complexity, breach detection)
- Harden registration and credential recovery flows
- Limit or delay failed login attempts
- Use cryptographically random session identifiers
- Invalidate sessions on logout and timeout

### A08: Software and Data Integrity Failures

**Focus:** Insecure CI/CD, auto-updates, unsigned objects

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

**Prevention:**
- Use digital signatures for software/data verification
- Verify integrity of downloads (checksums, GPG)
- Implement secure CI/CD pipelines with segregation
- Review code and configuration changes
- Use libraries that prevent deserialization attacks

### A09: Security Logging and Monitoring Failures

**Effective Logging:**
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'security.log' })
  ]
});

// Log security events
app.post('/api/login', async (req, res) => {
  try {
    const user = await authenticate(req.body);
    logger.info('Login success', {
      userId: user.id,
      ip: req.ip,
      timestamp: new Date()
    });
  } catch (err) {
    logger.warn('Login failed', {
      username: req.body.username,
      ip: req.ip,
      timestamp: new Date()
    });
  }
});
```

**Critical Events to Log:**
- Login/logout (success and failures)
- Access control failures (authorization denials)
- Input validation failures
- Authentication token anomalies
- Server-side exceptions and errors

**Prevention:**
- Ensure logs are tamper-proof (append-only)
- Implement centralized log management (SIEM)
- Establish effective monitoring and alerting
- Define incident response and recovery plan
- Use correlation IDs to track requests

### A10: Server-Side Request Forgery (SSRF)

**Vulnerability:**
```javascript
// VULNERABLE: Fetching user-supplied URLs
app.get('/fetch', async (req, res) => {
  const data = await fetch(req.query.url);
  res.send(await data.text());
  // Attack: /fetch?url=http://localhost:6379/
  // Access internal services (Redis, databases)
});

// SECURE: Validate and restrict URLs
const { URL } = require('url');
const ALLOWED_HOSTS = ['api.example.com', 'cdn.example.com'];

app.get('/fetch', async (req, res) => {
  try {
    const url = new URL(req.query.url);

    // Block internal IPs
    const hostname = url.hostname;
    if (hostname === 'localhost' ||
        hostname.startsWith('127.') ||
        hostname.startsWith('192.168.') ||
        hostname.startsWith('10.') ||
        hostname.startsWith('169.254.')) {
      return res.status(400).json({ error: 'Invalid URL' });
    }

    // Allow-list hostnames
    if (!ALLOWED_HOSTS.includes(hostname)) {
      return res.status(400).json({ error: 'Host not allowed' });
    }

    const data = await fetch(url.href);
    res.send(await data.text());
  } catch (err) {
    res.status(400).json({ error: 'Invalid URL' });
  }
});
```

**Prevention:**
- Sanitize and validate all client-supplied input data
- Enforce URL schema, port, destination with allow-list
- Disable HTTP redirections
- Use network segmentation to separate critical services
- Implement deny-by-default firewall policies

## Prevention Strategies

### Defense in Depth
Layer multiple security controls so failure of one doesn't compromise the system:
1. Network layer (firewalls, segmentation)
2. Application layer (input validation, output encoding)
3. Data layer (encryption, access control)
4. Monitoring layer (logging, alerting, incident response)

### Secure by Default
- Deny all access by default, explicitly grant
- Fail securely (errors should not expose information)
- Minimize attack surface (disable unused features)
- Least privilege for all accounts and services

### Input Validation Strategy
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

## Resources

- **OWASP Top 10 2021**: https://owasp.org/Top10/
- **OWASP Cheat Sheets**: https://cheatsheetseries.owasp.org/
- **OWASP ASVS**: Application Security Verification Standard
- **CWE Top 25**: Common Weakness Enumeration
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **SANS Top 25**: Most dangerous software errors
- **CVE Database**: https://cve.mitre.org/
- **Snyk Vulnerability Database**: https://snyk.io/vuln/
