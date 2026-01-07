# API Security Testing (OWASP API Top 10)

## API1: Broken Object Level Authorization

```javascript
// Test for BOLA vulnerabilities
async function testBOLA(apiUrl, authToken) {
  const testCases = [
    {
      name: "Access other user's resource",
      endpoint: `${apiUrl}/users/999/orders`,
      method: 'GET'
    },
    {
      name: "Modify other user's resource",
      endpoint: `${apiUrl}/users/999/profile`,
      method: 'PUT',
      body: { name: 'Attacker' }
    },
    {
      name: "Delete other user's resource",
      endpoint: `${apiUrl}/users/999/account`,
      method: 'DELETE'
    }
  ];

  for (const test of testCases) {
    const response = await fetch(test.endpoint, {
      method: test.method,
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      body: test.body ? JSON.stringify(test.body) : undefined
    });

    if (response.status === 200) {
      console.error(`BOLA vulnerability: ${test.name}`);
    }
  }
}
```

## API2: Broken Authentication

```javascript
// JWT security tests
function testJWTSecurity(token) {
  const tests = {
    // Test 1: Algorithm confusion
    noneAlgorithm: () => {
      const decoded = jwt.decode(token, { complete: true });
      const payload = decoded.payload;
      // Create token with "none" algorithm
      const maliciousToken = jwt.sign(payload, '', { algorithm: 'none' });
      return maliciousToken;
    },

    // Test 2: Weak secret
    weakSecret: async () => {
      const commonSecrets = ['secret', '123456', 'password', 'jwt'];
      for (const secret of commonSecrets) {
        try {
          jwt.verify(token, secret);
          console.error(`Weak JWT secret detected: ${secret}`);
          return true;
        } catch (err) {
          // Continue testing
        }
      }
      return false;
    },

    // Test 3: Token expiration
    expiration: () => {
      const decoded = jwt.decode(token);
      if (!decoded.exp) {
        console.error('JWT token has no expiration');
        return false;
      }
      const expirationTime = decoded.exp - decoded.iat;
      if (expirationTime > 3600) { // More than 1 hour
        console.warn('JWT token has long expiration time');
      }
      return true;
    }
  };

  return tests;
}
```

## API3: Excessive Data Exposure

```javascript
// Test for data leakage
async function testDataExposure(apiUrl, authToken) {
  const response = await fetch(`${apiUrl}/users/me`, {
    headers: { Authorization: `Bearer ${authToken}` }
  });

  const userData = await response.json();

  // Check for sensitive fields
  const sensitiveFields = [
    'password', 'passwordHash', 'ssn', 'creditCard',
    'bankAccount', 'taxId', 'secret', 'privateKey'
  ];

  const exposedFields = sensitiveFields.filter(field =>
    JSON.stringify(userData).toLowerCase().includes(field.toLowerCase())
  );

  if (exposedFields.length > 0) {
    console.error('Sensitive data exposed:', exposedFields);
  }
}
```

## API4: Lack of Resources & Rate Limiting

```javascript
// Rate limiting test
async function testRateLimiting(apiUrl, authToken) {
  const endpoint = `${apiUrl}/api/search`;
  const requests = 100;
  const results = [];

  console.log(`Sending ${requests} requests...`);

  for (let i = 0; i < requests; i++) {
    const start = Date.now();
    try {
      const response = await fetch(endpoint, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      results.push({
        status: response.status,
        time: Date.now() - start,
        rateLimitRemaining: response.headers.get('X-RateLimit-Remaining')
      });
    } catch (err) {
      results.push({ error: err.message });
    }
  }

  // Analyze results
  const successfulRequests = results.filter(r => r.status === 200).length;
  const rateLimited = results.filter(r => r.status === 429).length;

  console.log(`Successful: ${successfulRequests}/${requests}`);
  console.log(`Rate limited: ${rateLimited}/${requests}`);

  if (successfulRequests === requests) {
    console.error('No rate limiting detected - API vulnerable to abuse');
  }
}
```
