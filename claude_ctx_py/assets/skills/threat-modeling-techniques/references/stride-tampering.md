# STRIDE: Tampering with Data

**Definition:** Malicious modification of data in transit or at rest.

## Threat Examples

### Man-in-the-Middle Attack

```javascript
// THREAT: Man-in-the-middle attack modifying API requests

// VULNERABLE: Unencrypted data transmission
fetch('http://api.example.com/transfer', {
  method: 'POST',
  body: JSON.stringify({ amount: 100, to: 'account123' })
});

// MITIGATION: HTTPS + request signing
const crypto = require('crypto');

function signRequest(data, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(JSON.stringify(data));
  return hmac.digest('hex');
}

const data = { amount: 100, to: 'account123', timestamp: Date.now() };
const signature = signRequest(data, process.env.API_SECRET);

fetch('https://api.example.com/transfer', {
  method: 'POST',
  headers: {
    'X-Signature': signature,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});
```

## Mitigations

- **TLS/HTTPS**: Encrypt data in transit
- **Digital signatures & HMAC**: Verify data integrity
- **Input validation**: Sanitize and validate all inputs
- **Immutable audit logs**: Tamper-proof logging
- **Database transaction controls**: ACID properties, checksums
- **File integrity monitoring (FIM)**: Detect unauthorized changes
- **Content Security Policy (CSP)**: Prevent XSS tampering
