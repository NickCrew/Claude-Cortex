---
name: secure-coding-practices
description: Secure coding practices and defensive programming patterns for building security-first applications. Use when implementing authentication, handling user input, managing sensitive data, or conducting secure code reviews.
---

# Secure Coding Practices

Comprehensive guidance for implementing security-first development patterns with defensive programming techniques and proactive threat mitigation strategies.

## When to Use This Skill

- Implementing authentication and authorization systems
- Processing user input or external data
- Handling sensitive data (PII, credentials, financial information)
- Building APIs and web services
- Managing cryptographic operations (hashing, encryption)
- Conducting security-focused code reviews
- Establishing secure development standards for teams
- Evaluating third-party dependencies and libraries
- Designing error handling and logging strategies
- Implementing session management and token handling

## Input Validation & Sanitization

**Principle:** Never trust user input. Validate all data from untrusted sources before processing.

### Allowlist Validation

```javascript
// VULNERABLE: Blocklist approach (incomplete, bypassable)
function validateUsername(username) {
  const blocked = ['admin', 'root', 'system'];
  return !blocked.includes(username);
}

// SECURE: Allowlist approach (explicit, comprehensive)
function validateUsername(username) {
  // Only allow alphanumeric characters, underscores, and hyphens
  const pattern = /^[a-zA-Z0-9_-]{3,20}$/;
  return pattern.test(username);
}

// SECURE: Multi-layered validation
function validateEmail(email) {
  // 1. Type check
  if (typeof email !== 'string') return false;

  // 2. Length validation
  if (email.length > 254) return false;

  // 3. Format validation
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(email)) return false;

  // 4. Domain validation (optional)
  const allowedDomains = ['example.com', 'trusted.org'];
  const domain = email.split('@')[1];
  if (!allowedDomains.includes(domain)) return false;

  return true;
}
```

### Server-Side Validation

```javascript
// NEVER trust client-side validation alone
const express = require('express');
const { body, validationResult } = require('express-validator');

app.post('/api/register',
  // Define validation rules
  [
    body('email')
      .isEmail()
      .normalizeEmail()
      .withMessage('Invalid email format'),
    body('password')
      .isLength({ min: 12 })
      .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])/)
      .withMessage('Password must be 12+ chars with upper, lower, number, special char'),
    body('age')
      .isInt({ min: 18, max: 120 })
      .withMessage('Age must be between 18 and 120'),
  ],
  (req, res) => {
    // Check validation results
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Proceed with validated data
    createUser(req.body);
  }
);
```

### Type Coercion Defense

```javascript
// VULNERABLE: Loose comparison
if (req.body.isAdmin == true) {
  grantAdminAccess();
}
// Attack: isAdmin = "true" or isAdmin = 1

// SECURE: Strict type checking
if (req.body.isAdmin === true && typeof req.body.isAdmin === 'boolean') {
  grantAdminAccess();
}

// SECURE: Schema validation with libraries
const Joi = require('joi');

const userSchema = Joi.object({
  username: Joi.string().alphanum().min(3).max(30).required(),
  email: Joi.string().email().required(),
  age: Joi.number().integer().min(18).max(120).required(),
  isAdmin: Joi.boolean().required()
});

const { error, value } = userSchema.validate(req.body);
if (error) {
  return res.status(400).json({ error: error.details[0].message });
}
```

## Output Encoding & Context-Aware Escaping

**Principle:** Encode all output based on the context where it will be used.

### HTML Context Escaping

```javascript
// VULNERABLE: Direct output without encoding
app.get('/welcome', (req, res) => {
  const name = req.query.name;
  res.send(`<h1>Welcome ${name}!</h1>`);
  // XSS: /welcome?name=<script>alert('XSS')</script>
});

// SECURE: HTML entity encoding
const escapeHtml = (str) => {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };
  return str.replace(/[&<>"'/]/g, (char) => map[char]);
};

app.get('/welcome', (req, res) => {
  const name = escapeHtml(req.query.name);
  res.send(`<h1>Welcome ${name}!</h1>`);
});

// BETTER: Use templating engines with auto-escaping
const handlebars = require('handlebars');
const template = handlebars.compile('<h1>Welcome {{name}}!</h1>');
app.get('/welcome', (req, res) => {
  res.send(template({ name: req.query.name }));
});
```

### JavaScript Context Escaping

```javascript
// VULNERABLE: Injecting into JavaScript
res.send(`
  <script>
    var username = "${req.query.username}";
  </script>
`);
// Attack: username="; alert('XSS'); //

// SECURE: JSON encoding for JavaScript context
res.send(`
  <script>
    var username = ${JSON.stringify(req.query.username)};
  </script>
`);
```

### URL Context Encoding

```javascript
// VULNERABLE: Unencoded URL parameter
const redirectUrl = `/profile?user=${req.query.user}`;
// Attack: user=admin&admin=true

// SECURE: Proper URL encoding
const redirectUrl = `/profile?user=${encodeURIComponent(req.query.user)}`;
```

### Content Security Policy (CSP)

```javascript
// Implement CSP headers to prevent XSS
const helmet = require('helmet');

app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'nonce-{random}'"], // Use nonces for inline scripts
    styleSrc: ["'self'", "https://trusted-cdn.com"],
    imgSrc: ["'self'", "data:", "https:"],
    connectSrc: ["'self'"],
    fontSrc: ["'self'"],
    objectSrc: ["'none'"],
    mediaSrc: ["'self'"],
    frameSrc: ["'none'"],
    upgradeInsecureRequests: []
  }
}));
```

## Authentication & Session Management

### Secure Password Handling

```javascript
// SECURE: Password hashing with bcrypt
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12; // Adjusts computational cost

async function registerUser(username, password) {
  // Validate password strength
  if (password.length < 12) {
    throw new Error('Password must be at least 12 characters');
  }

  // Hash password
  const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);

  // Store username and hash (NEVER store plaintext)
  await db.users.create({ username, passwordHash });
}

async function authenticateUser(username, password) {
  const user = await db.users.findOne({ username });
  if (!user) {
    // Use constant-time comparison to prevent timing attacks
    await bcrypt.compare(password, '$2b$12$dummy.hash.to.prevent.timing.attack');
    throw new Error('Invalid credentials');
  }

  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    throw new Error('Invalid credentials');
  }

  return user;
}
```

### Secure Session Management

```javascript
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const { createClient } = require('redis');

// Initialize Redis client
const redisClient = createClient({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT,
  password: process.env.REDIS_PASSWORD
});

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET, // Strong random secret
  name: 'sessionId', // Non-default name
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true, // HTTPS only
    httpOnly: true, // No JavaScript access
    maxAge: 1800000, // 30 minutes
    sameSite: 'strict', // CSRF protection
    domain: 'example.com',
    path: '/'
  },
  rolling: true, // Reset expiration on activity
  genid: () => {
    // Cryptographically secure session ID
    return require('crypto').randomBytes(32).toString('hex');
  }
}));
```

### JWT Best Practices

```javascript
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

// SECURE: JWT implementation
const JWT_SECRET = process.env.JWT_SECRET; // Strong random secret
const JWT_EXPIRY = '15m'; // Short expiration
const REFRESH_TOKEN_EXPIRY = '7d';

function generateTokens(userId) {
  // Access token (short-lived)
  const accessToken = jwt.sign(
    { userId, type: 'access' },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRY, algorithm: 'HS256' }
  );

  // Refresh token (long-lived, stored securely)
  const refreshToken = jwt.sign(
    { userId, type: 'refresh', jti: crypto.randomBytes(16).toString('hex') },
    JWT_SECRET,
    { expiresIn: REFRESH_TOKEN_EXPIRY, algorithm: 'HS256' }
  );

  return { accessToken, refreshToken };
}

function verifyAccessToken(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid token' });
  }

  const token = authHeader.substring(7);

  try {
    const decoded = jwt.verify(token, JWT_SECRET, { algorithms: ['HS256'] });

    if (decoded.type !== 'access') {
      return res.status(401).json({ error: 'Invalid token type' });
    }

    req.user = { userId: decoded.userId };
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired' });
    }
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

### Multi-Factor Authentication (MFA)

```javascript
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');

// Enable TOTP-based MFA
async function enableMFA(userId) {
  const secret = speakeasy.generateSecret({
    name: `MyApp (${userId})`,
    length: 32
  });

  // Store secret.base32 encrypted in database
  await db.users.update(userId, {
    mfaSecret: encrypt(secret.base32),
    mfaEnabled: false // Activated after verification
  });

  // Generate QR code for user to scan
  const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);

  return { secret: secret.base32, qrCode: qrCodeUrl };
}

function verifyMFAToken(secret, token) {
  return speakeasy.totp.verify({
    secret,
    encoding: 'base32',
    token,
    window: 2 // Allow 2 time steps for clock drift
  });
}
```

## Cryptography Best Practices

### Encryption with AES-256-GCM

```javascript
const crypto = require('crypto');

// SECURE: Symmetric encryption with authenticated encryption
class SecureEncryption {
  constructor() {
    // 256-bit key from environment
    this.key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
    if (this.key.length !== 32) {
      throw new Error('Encryption key must be 32 bytes (256 bits)');
    }
    this.algorithm = 'aes-256-gcm';
  }

  encrypt(plaintext) {
    // Generate random IV (96 bits for GCM)
    const iv = crypto.randomBytes(12);

    // Create cipher
    const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);

    // Encrypt data
    const encrypted = Buffer.concat([
      cipher.update(plaintext, 'utf8'),
      cipher.final()
    ]);

    // Get authentication tag
    const authTag = cipher.getAuthTag();

    // Return IV + authTag + ciphertext (all needed for decryption)
    return {
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex'),
      ciphertext: encrypted.toString('hex')
    };
  }

  decrypt(encryptedData) {
    const iv = Buffer.from(encryptedData.iv, 'hex');
    const authTag = Buffer.from(encryptedData.authTag, 'hex');
    const ciphertext = Buffer.from(encryptedData.ciphertext, 'hex');

    // Create decipher
    const decipher = crypto.createDecipheriv(this.algorithm, this.key, iv);
    decipher.setAuthTag(authTag);

    // Decrypt data
    const decrypted = Buffer.concat([
      decipher.update(ciphertext),
      decipher.final()
    ]);

    return decrypted.toString('utf8');
  }
}

// Usage
const encryption = new SecureEncryption();
const encrypted = encryption.encrypt('sensitive data');
const decrypted = encryption.decrypt(encrypted);
```

### Key Management

```javascript
// NEVER hardcode keys in source code
// BAD: const SECRET_KEY = 'hardcoded-secret-123';

// GOOD: Use environment variables
require('dotenv').config();
const SECRET_KEY = process.env.SECRET_KEY;

// BETTER: Use dedicated key management service
const { SecretsManagerClient, GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');

async function getSecret(secretName) {
  const client = new SecretsManagerClient({ region: 'us-east-1' });
  const command = new GetSecretValueCommand({ SecretId: secretName });
  const response = await client.send(command);
  return response.SecretString;
}

// Key rotation strategy
async function rotateEncryptionKey(oldKey, newKey) {
  const records = await db.sensitiveData.findAll();

  for (const record of records) {
    // Decrypt with old key
    const decrypted = decryptWithKey(record.data, oldKey);

    // Re-encrypt with new key
    const encrypted = encryptWithKey(decrypted, newKey);

    // Update record
    await db.sensitiveData.update(record.id, { data: encrypted });
  }
}
```

### Secure Random Number Generation

```javascript
const crypto = require('crypto');

// VULNERABLE: Predictable randomness
Math.random(); // NEVER use for security

// SECURE: Cryptographically secure randomness
const token = crypto.randomBytes(32).toString('hex'); // 256-bit token
const resetToken = crypto.randomBytes(20).toString('hex'); // Password reset
const sessionId = crypto.randomBytes(16).toString('base64url'); // Session IDs

// SECURE: Random integer in range
function getSecureRandomInt(min, max) {
  const range = max - min;
  const bytesNeeded = Math.ceil(Math.log2(range) / 8);
  const maxValid = Math.floor(256 ** bytesNeeded / range) * range;

  let randomValue;
  do {
    randomValue = crypto.randomBytes(bytesNeeded).readUIntBE(0, bytesNeeded);
  } while (randomValue >= maxValid);

  return min + (randomValue % range);
}
```

## Secure Dependencies & Supply Chain

### Dependency Auditing

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

### Dependency Validation

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

### Subresource Integrity (SRI)

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

### Private Package Registry

```javascript
// .npmrc: Use private registry for sensitive packages
registry=https://registry.npmjs.org/
@mycompany:registry=https://npm.internal.company.com/
//npm.internal.company.com/:_authToken=${NPM_TOKEN}

// Enable audit for private packages
audit=true
audit-level=moderate
```

## Error Handling & Logging Security

### Secure Error Handling

```javascript
// VULNERABLE: Exposing stack traces to users
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack, // Leaks internal paths, dependencies
    query: req.query // Leaks user input
  });
});

// SECURE: Generic error messages with internal logging
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

app.use((err, req, res, next) => {
  // Log full error details internally
  logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    ip: req.ip,
    userId: req.user?.id,
    requestId: req.id,
    timestamp: new Date().toISOString()
  });

  // Return generic message to user
  res.status(500).json({
    error: 'An internal error occurred',
    requestId: req.id // For support inquiries
  });
});
```

### Safe Logging Practices

```javascript
// NEVER log sensitive data
logger.info('User login', {
  username: user.username,
  password: user.password, // NEVER!
  creditCard: user.card // NEVER!
});

// SECURE: Sanitize before logging
function sanitizeForLogging(obj) {
  const sensitiveFields = ['password', 'creditCard', 'ssn', 'token', 'secret'];
  const sanitized = { ...obj };

  for (const field of sensitiveFields) {
    if (sanitized[field]) {
      sanitized[field] = '[REDACTED]';
    }
  }

  return sanitized;
}

logger.info('User login', sanitizeForLogging({
  username: user.username,
  password: user.password,
  ip: req.ip
}));
// Logs: { username: 'john', password: '[REDACTED]', ip: '192.168.1.1' }

// Log security events
logger.warn('Failed login attempt', {
  username: req.body.username,
  ip: req.ip,
  timestamp: new Date().toISOString()
});

logger.info('Authorization failure', {
  userId: req.user.id,
  resource: req.path,
  action: req.method,
  timestamp: new Date().toISOString()
});
```

### Structured Logging

```javascript
// Use correlation IDs to track requests
const { v4: uuidv4 } = require('uuid');

app.use((req, res, next) => {
  req.id = uuidv4();
  res.setHeader('X-Request-ID', req.id);
  next();
});

// Log with consistent structure
logger.info('Request received', {
  requestId: req.id,
  method: req.method,
  path: req.path,
  userId: req.user?.id,
  ip: req.ip,
  userAgent: req.headers['user-agent']
});
```

## Secure Defaults & Configuration

### Security Headers

```javascript
const helmet = require('helmet');

// Apply secure defaults
app.use(helmet({
  // Prevent clickjacking
  frameguard: { action: 'deny' },

  // Enforce HTTPS
  hsts: {
    maxAge: 31536000, // 1 year
    includeSubDomains: true,
    preload: true
  },

  // Prevent MIME sniffing
  noSniff: true,

  // XSS protection
  xssFilter: true,

  // Referrer policy
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },

  // Permissions policy
  permissionsPolicy: {
    features: {
      geolocation: ["'self'"],
      camera: ["'none'"],
      microphone: ["'none'"]
    }
  }
}));

// CORS configuration
const cors = require('cors');
app.use(cors({
  origin: ['https://trusted-domain.com'],
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 86400 // 24 hours
}));
```

### Principle of Least Privilege

```javascript
// Database: Create limited-privilege users
// NEVER use root/admin for application connections

// PostgreSQL example:
/*
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
GRANT SELECT ON products TO app_user;
-- Do NOT grant DELETE, DROP, or admin privileges
*/

// Application: Role-based access control
const roles = {
  USER: ['read:profile', 'update:profile'],
  MODERATOR: ['read:profile', 'update:profile', 'delete:comments'],
  ADMIN: ['read:profile', 'update:profile', 'delete:comments', 'manage:users']
};

function authorize(requiredPermission) {
  return (req, res, next) => {
    const userRole = req.user.role;
    const permissions = roles[userRole] || [];

    if (!permissions.includes(requiredPermission)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
}

app.delete('/api/users/:id', authenticate, authorize('manage:users'), (req, res) => {
  deleteUser(req.params.id);
});
```

### Secure Configuration Management

```javascript
// Environment-based configuration
const config = {
  development: {
    database: {
      host: 'localhost',
      ssl: false,
      debug: true
    },
    logging: 'debug'
  },
  production: {
    database: {
      host: process.env.DB_HOST,
      ssl: {
        rejectUnauthorized: true,
        ca: fs.readFileSync('/path/to/ca-cert.pem')
      },
      debug: false
    },
    logging: 'error'
  }
};

const env = process.env.NODE_ENV || 'development';
const activeConfig = config[env];

// Fail securely
if (env === 'production' && !activeConfig.database.ssl) {
  throw new Error('SSL required for production database');
}
```

## Best Practices Summary

### Security Checklist

**Input Validation:**
- [ ] Validate all user input server-side with allowlists
- [ ] Use schema validation libraries (Joi, Yup, Zod)
- [ ] Implement strict type checking
- [ ] Sanitize file paths and prevent traversal
- [ ] Validate file uploads (type, size, content)

**Output Encoding:**
- [ ] Apply context-aware encoding (HTML, JS, URL, SQL)
- [ ] Use templating engines with auto-escaping
- [ ] Implement Content Security Policy (CSP)
- [ ] Set secure HTTP headers (Helmet.js)

**Authentication & Authorization:**
- [ ] Hash passwords with bcrypt/Argon2 (salt rounds ≥12)
- [ ] Implement secure session management
- [ ] Use HTTPS-only cookies with HttpOnly and SameSite
- [ ] Apply rate limiting on authentication endpoints
- [ ] Implement multi-factor authentication (MFA)
- [ ] Enforce principle of least privilege
- [ ] Verify authorization on every request

**Cryptography:**
- [ ] Use AES-256-GCM for encryption
- [ ] Generate keys with crypto.randomBytes()
- [ ] Store secrets in environment variables or KMS
- [ ] Implement key rotation strategy
- [ ] Never roll your own crypto

**Dependencies:**
- [ ] Run npm audit regularly
- [ ] Lock dependency versions in package.json
- [ ] Commit package-lock.json
- [ ] Use Snyk/Dependabot for monitoring
- [ ] Verify package integrity (SRI for CDN)

**Error Handling & Logging:**
- [ ] Return generic error messages to users
- [ ] Log errors with correlation IDs
- [ ] Never log passwords, tokens, or PII
- [ ] Implement structured logging
- [ ] Monitor security events and alerts

**Configuration:**
- [ ] Disable debug mode in production
- [ ] Remove unnecessary endpoints and features
- [ ] Set secure defaults (deny-by-default)
- [ ] Use environment-based configuration
- [ ] Implement security headers

### Code Review Checklist

**High-Risk Patterns to Check:**
1. String concatenation in SQL queries (injection risk)
2. Direct file path construction from user input (traversal risk)
3. eval(), Function(), or exec() with user input (code injection)
4. Deserialization of untrusted data (RCE risk)
5. Hardcoded secrets or credentials (exposure risk)
6. Missing authentication/authorization checks (access control)
7. Weak cryptography (MD5, SHA1, ECB mode)
8. Verbose error messages in production (information disclosure)
9. Missing input validation (injection, DoS)
10. Insecure session configuration (hijacking risk)

## Resources

**OWASP Resources:**
- **OWASP Top 10**: https://owasp.org/Top10/
- **OWASP Cheat Sheet Series**: https://cheatsheetseries.owasp.org/
- **OWASP ASVS**: Application Security Verification Standard
- **OWASP Dependency-Check**: https://owasp.org/www-project-dependency-check/
- **OWASP ZAP**: Web application security scanner

**CWE (Common Weakness Enumeration):**
- **CWE Top 25**: https://cwe.mitre.org/top25/
- **CWE-79**: Cross-site Scripting (XSS)
- **CWE-89**: SQL Injection
- **CWE-20**: Improper Input Validation
- **CWE-200**: Exposure of Sensitive Information
- **CWE-287**: Improper Authentication

**Standards & Guidelines:**
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **NIST SP 800-63B**: Digital Identity Guidelines (Authentication)
- **PCI DSS**: Payment Card Industry Data Security Standard
- **GDPR**: General Data Protection Regulation requirements
- **ISO 27001**: Information Security Management

**Tools:**
- **SAST**: SonarQube, Semgrep, CodeQL
- **DAST**: OWASP ZAP, Burp Suite
- **SCA**: Snyk, npm audit, Dependabot
- **Secrets Detection**: TruffleHog, git-secrets
- **Runtime Protection**: Sqreen, Contrast Security
