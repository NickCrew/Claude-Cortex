# Dynamic Application Security Testing (DAST)

## Overview
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

## OWASP ZAP (Zed Attack Proxy)

### Basic Scan
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

### ZAP Configuration File
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

### ZAP API Integration
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

## Burp Suite Integration

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

## DAST in CI/CD

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
