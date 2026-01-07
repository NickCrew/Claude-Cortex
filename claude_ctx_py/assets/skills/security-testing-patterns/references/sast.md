# Static Application Security Testing (SAST)

## Overview
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

## Popular SAST Tools

### JavaScript/TypeScript
```bash
# ESLint with security plugins
npm install --save-dev eslint eslint-plugin-security

# SonarQube scanner
npm install --save-dev sonarqube-scanner

# Semgrep - polyglot static analysis
npm install -g @semgrep/cli
semgrep --config=auto src/
```

### Python
```bash
# Bandit - Python security linter
pip install bandit
bandit -r ./src -f json -o security-report.json

# Semgrep for Python
semgrep --config=p/python src/
```

### Java
```bash
# SpotBugs with Find Security Bugs plugin
mvn spotbugs:check

# SonarQube
mvn sonar:sonar
```

## SAST Integration in CI/CD

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

## Custom SAST Rules

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
