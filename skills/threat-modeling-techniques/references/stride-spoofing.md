# STRIDE: Spoofing Identity

**Definition:** Pretending to be someone or something else to gain unauthorized access.

## Threat Examples

### JWT Manipulation Without Verification

```javascript
// THREAT: Spoofing user identity via JWT manipulation
// Attacker modifies JWT payload without signature verification

// VULNERABLE: No signature verification
app.get('/api/profile', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  const decoded = JSON.parse(Buffer.from(token.split('.')[1], 'base64'));
  // Using decoded.userId without verification
  const user = db.getUser(decoded.userId);
  res.json(user);
});

// MITIGATION: Proper JWT verification
const jwt = require('jsonwebtoken');

app.get('/api/profile', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = db.getUser(decoded.userId);
    res.json(user);
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
});
```

## Mitigations

- **Strong authentication mechanisms**: MFA, certificate-based auth
- **Digital signatures**: Cryptographic verification of identity claims
- **Secure credential storage**: Hashed passwords, encrypted keys
- **Session management**: Secure tokens with expiration and rotation
- **Mutual TLS**: For service-to-service communication
- **Anti-spoofing headers**: SPF, DKIM, DMARC for email systems
