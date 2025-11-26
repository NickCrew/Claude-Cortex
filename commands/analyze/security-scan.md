---
name: security-scan
description: Comprehensive security vulnerability assessment
category: analysis
personas: [security-specialist, compliance-auditor]
subagents: [security-auditor]
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

## Personas (Thinking Modes)
- **security-specialist**: Security-first mindset, threat modeling, vulnerability expertise
- **compliance-auditor**: Regulatory standards, compliance requirements, audit rigor

## Delegation Protocol

**This command ALWAYS delegates** - security scanning requires specialized security expertise.

**When triggered**:
- ✅ Any security scan request
- ✅ Compliance assessment needed
- ✅ Vulnerability analysis required

**Subagent launched** (via Task tool):
```xml
<invoke name="Task">
  <subagent_type>security-auditor</subagent_type>
  <description>Security vulnerability assessment for [path]</description>
  <prompt>
    Perform comprehensive security analysis:
    1. Threat modeling and attack vector identification
    2. Vulnerability scanning (dependencies, code, config)
    3. Code security review (auth, validation, crypto)
    4. Penetration testing scenarios
    5. Compliance validation for: [OWASP|GDPR|SOC2|HIPAA]

    Provide findings with:
    - Severity levels (Critical, High, Medium, Low, Info)
    - Remediation steps
    - Compliance gap analysis
    - Risk assessment
  </prompt>
</invoke>
```

**For multi-component systems**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>security-auditor</subagent_type>
  <description>Frontend security assessment</description>
  <prompt>Focus on: XSS, CSRF, client-side vulnerabilities...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>security-auditor</subagent_type>
  <description>Backend security assessment</description>
  <prompt>Focus on: SQL injection, authentication, authorization...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>security-auditor</subagent_type>
  <description>Infrastructure security assessment</description>
  <prompt>Focus on: SSL/TLS, headers, network security...</prompt>
</invoke>
</function_calls>
```

**Tool Coordination**:
- **Task tool**: Launches security-auditor subagent(s) for comprehensive assessment
- **Read/Grep**: Vulnerability pattern scanning (done by subagent)
- **Bash**: Dependency scanning tools (done by subagent if needed)

## Example
```
/analyze:security-scan src/auth --standard OWASP
```