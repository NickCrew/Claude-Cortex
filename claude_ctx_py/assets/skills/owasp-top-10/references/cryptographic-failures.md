# A02: Cryptographic Failures

**Description:** Exposing sensitive data due to missing or weak cryptography.

## Common Vulnerabilities

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

## Secure Implementation

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

## Prevention Checklist

- [ ] Classify data based on sensitivity (PII, financial, health)
- [ ] Encrypt all sensitive data at rest (AES-256)
- [ ] Encrypt data in transit with TLS 1.2+ only
- [ ] Use strong adaptive hashing (bcrypt, scrypt, Argon2)
- [ ] Rotate keys regularly and use proper key management (KMS)
- [ ] Disable caching for sensitive data responses
- [ ] Apply data retention policies and secure deletion
