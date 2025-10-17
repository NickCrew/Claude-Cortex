---
name: security-scan
description: Comprehensive security vulnerability assessment
category: analysis
agents: [security-auditor]
---

# /analyze:security-scan - Security Vulnerability Assessment

## Purpose
Perform comprehensive security analysis to identify and remediate vulnerabilities.

## Triggers
- Security audit requests
- Pre-release security checks
- Compliance requirements
- Vulnerability reports

## Usage
```
/analyze:security-scan [path] [--standard OWASP|GDPR|SOC2|HIPAA]
```

## Security Analysis Process

### 1. Threat Modeling
- Identify potential attack vectors
- Map trust boundaries
- Analyze data flow
- Assess risk levels
- Create threat matrix

### 2. Vulnerability Scanning
- Dependency vulnerability check
- Static code analysis
- Secret scanning
- Configuration review
- API security assessment

### 3. Code Security Review
- Input validation analysis
- Output encoding checks
- Authentication logic review
- Authorization verification
- Session management audit
- Cryptography usage validation

### 4. Penetration Testing
- SQL injection testing
- XSS attack simulation
- CSRF vulnerability check
- Authentication bypass attempts
- Privilege escalation testing
- API abuse scenarios

### 5. Compliance Validation
- OWASP Top 10 compliance
- GDPR data protection
- SOC 2 security controls
- HIPAA requirements (if applicable)
- Industry-specific standards

## Security Checks

**Authentication & Authorization**
- Password security
- Session management
- Token validation
- Access control
- Permission boundaries

**Data Protection**
- Encryption at rest
- Encryption in transit
- Data sanitization
- PII handling
- Secure storage

**API Security**
- Rate limiting
- Input validation
- Authentication
- CORS configuration
- Error handling

**Infrastructure**
- Security headers
- SSL/TLS configuration
- Firewall rules
- Network segmentation
- Logging and monitoring

## Severity Levels

**Critical** - Immediate fix required
**High** - Fix within 7 days
**Medium** - Fix within 30 days
**Low** - Fix when possible
**Informational** - Best practice recommendations

## Output Format

**Executive Summary**
- Overall security posture
- Critical findings count
- Risk assessment
- Compliance status

**Detailed Findings**
- Vulnerability description
- Affected components
- Severity rating
- Remediation steps
- Code examples

**Compliance Report**
- Standard requirements
- Compliance gaps
- Recommendations
- Implementation timeline

## Agents Used
- `security-auditor`: Comprehensive security assessment

## Example
```
/analyze:security-scan src/auth --standard OWASP
```