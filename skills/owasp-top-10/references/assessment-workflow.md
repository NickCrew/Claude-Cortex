# OWASP Assessment Workflow

Structured methodology for conducting OWASP Top 10 security assessments, from scoping through remediation tracking.

## Phase 1: Scoping and Pre-Assessment

### Define Assessment Boundaries

- **Application inventory**: Identify all in-scope components (frontend, backend, APIs, microservices, databases)
- **Technology stack**: Document languages, frameworks, libraries, infrastructure
- **Data classification**: Identify sensitive data flows (PII, credentials, financial, health)
- **Trust boundaries**: Map where data crosses privilege levels or network zones
- **Third-party integrations**: Catalog external services, APIs, and dependencies

### Establish Rules of Engagement

```markdown
## Assessment Scope Document

**Target Application**: [name]
**Environment**: [production/staging/dev]
**Assessment Type**: [code review / dynamic testing / both]
**Timeline**: [start] - [end]
**Excluded Components**: [list]
**Emergency Contact**: [name, phone, email]
**Authorization Reference**: [document ID]
```

### Prioritize Assessment Areas

Map application features to OWASP categories by risk:

| Feature Area | Primary OWASP Categories | Priority |
|---|---|---|
| Authentication | A01, A02, A07 | Critical |
| API endpoints | A01, A03, A10 | Critical |
| User input forms | A03, A08 | High |
| File upload/download | A01, A04, A08 | High |
| Admin panels | A01, A05, A07 | Critical |
| Third-party integrations | A06, A08, A10 | Medium |
| Logging infrastructure | A09 | Medium |

## Phase 2: Testing Methodology

### Per-Category Testing Approach

#### A01 - Broken Access Control

```
Checklist:
[ ] Verify RBAC enforcement on every endpoint
[ ] Test horizontal privilege escalation (user A accessing user B data)
[ ] Test vertical privilege escalation (user accessing admin functions)
[ ] Check IDOR via sequential/predictable IDs
[ ] Verify CORS policy is restrictive
[ ] Test directory traversal on file operations
[ ] Confirm deny-by-default on new endpoints
[ ] Validate JWT/session token scope enforcement
```

#### A02 - Cryptographic Failures

```
Checklist:
[ ] Verify TLS 1.2+ on all external connections
[ ] Check for sensitive data in URLs or logs
[ ] Validate password hashing (bcrypt/argon2, not MD5/SHA1)
[ ] Verify encryption at rest for sensitive data
[ ] Check key management (rotation, storage, access)
[ ] Confirm no hardcoded secrets in source
[ ] Validate certificate pinning where applicable
```

#### A03 - Injection

```
Checklist:
[ ] Test SQL injection on all parameterized inputs
[ ] Verify ORM/parameterized queries (no string concatenation)
[ ] Test NoSQL injection on document queries
[ ] Check command injection on system calls
[ ] Test LDAP injection on directory queries
[ ] Validate template injection in server-side rendering
[ ] Verify XSS (reflected, stored, DOM-based) on all outputs
```

#### A04 - Insecure Design

```
Checklist:
[ ] Review threat model for business logic flaws
[ ] Check rate limiting on sensitive operations
[ ] Verify multi-step workflows can't be bypassed
[ ] Test for race conditions in concurrent operations
[ ] Validate business rule enforcement server-side
[ ] Review error handling for information disclosure
```

#### A05 - Security Misconfiguration

```
Checklist:
[ ] Check for default credentials on all services
[ ] Verify unnecessary features/ports are disabled
[ ] Review HTTP security headers (CSP, HSTS, X-Frame-Options)
[ ] Confirm error pages don't leak stack traces
[ ] Validate cloud/container security configurations
[ ] Check for directory listing on web servers
[ ] Review CORS, cookie, and cache-control settings
```

#### A06 - Vulnerable Components

```
Checklist:
[ ] Run dependency audit (npm audit, pip-audit, etc.)
[ ] Check for known CVEs in all dependencies
[ ] Verify dependency versions are actively maintained
[ ] Review transitive dependency risks
[ ] Confirm automated dependency update process exists
[ ] Check container base image for vulnerabilities
```

#### A07 - Authentication Failures

```
Checklist:
[ ] Test brute force protection (lockout/rate limiting)
[ ] Verify password complexity requirements
[ ] Check session fixation on login
[ ] Test multi-factor authentication bypass
[ ] Validate session timeout and invalidation
[ ] Verify credential recovery flow security
[ ] Check for credential stuffing protections
```

#### A08 - Integrity Failures

```
Checklist:
[ ] Verify CI/CD pipeline integrity (signed commits, protected branches)
[ ] Check for insecure deserialization of user input
[ ] Validate software update mechanisms use signatures
[ ] Review data integrity checks on critical operations
[ ] Verify CSP and SRI for frontend assets
```

#### A09 - Logging and Monitoring

```
Checklist:
[ ] Verify authentication events are logged
[ ] Check authorization failure logging
[ ] Validate log integrity (tamper protection)
[ ] Confirm alerting on suspicious patterns
[ ] Verify logs don't contain sensitive data
[ ] Check log retention meets compliance requirements
[ ] Test incident response playbook activation
```

#### A10 - SSRF

```
Checklist:
[ ] Test all URL/URI input parameters for SSRF
[ ] Verify allow-list enforcement on outbound requests
[ ] Check for cloud metadata endpoint access (169.254.169.254)
[ ] Test DNS rebinding protections
[ ] Validate internal network access restrictions
[ ] Check redirect-following behavior
```

### Testing Tools by Phase

| Phase | SAST Tools | DAST Tools |
|---|---|---|
| Code Review | Semgrep, SonarQube, CodeQL | - |
| Authentication | - | Burp Suite, OWASP ZAP |
| Injection | Semgrep rules | SQLMap, Burp Intruder |
| Dependencies | npm audit, Snyk, Trivy | - |
| Configuration | Checkov, ScoutSuite | Nmap, Nikto |
| Infrastructure | tfsec, kube-bench | Nuclei, Prowler |

## Phase 3: Risk Scoring

### CVSS v3.1 Quick Reference

Score each finding using CVSS Base metrics:

| Metric | Values |
|---|---|
| Attack Vector (AV) | Network (0.85) / Adjacent (0.62) / Local (0.55) / Physical (0.20) |
| Attack Complexity (AC) | Low (0.77) / High (0.44) |
| Privileges Required (PR) | None (0.85) / Low (0.62/0.68) / High (0.27/0.50) |
| User Interaction (UI) | None (0.85) / Required (0.62) |
| Scope (S) | Unchanged / Changed |
| Confidentiality (C) | None / Low / High |
| Integrity (I) | None / Low / High |
| Availability (A) | None / Low / High |

**Severity Bands**: Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.1-3.9), Info (0.0)

### DREAD Risk Model (Lightweight Alternative)

When full CVSS scoring is impractical, use DREAD for rapid triage:

| Factor | 1 (Low) | 2 (Medium) | 3 (High) |
|---|---|---|---|
| **D**amage | Minor data leak | Significant data loss | Full system compromise |
| **R**eproducibility | Difficult to reproduce | Requires specific conditions | Reliably reproducible |
| **E**xploitability | Requires advanced skills | Requires some skill | Automated/trivial |
| **A**ffected Users | Single user | Subset of users | All users |
| **D**iscoverability | Requires insider knowledge | Discoverable with effort | Obvious/public |

**Score**: Sum / 5 = Average (1.0-3.0 scale). Map to severity: >2.5 Critical, >2.0 High, >1.5 Medium, <=1.5 Low.

### Contextual Risk Adjustment

Adjust raw scores based on business context:

```
Adjusted Risk = Base Score x Environment Factor x Data Sensitivity Factor

Environment Factors:
  Production (internet-facing): 1.0
  Production (internal):        0.8
  Staging:                      0.5
  Development:                  0.3

Data Sensitivity Factors:
  PII / Financial / Health:     1.2
  Internal business data:       1.0
  Public data:                  0.7
```

## Phase 4: Evidence Documentation

### Finding Template

```markdown
## [FINDING-ID]: [Title]

**Severity**: [Critical/High/Medium/Low/Info]
**CVSS Score**: [0.0-10.0] ([vector string])
**OWASP Category**: [A01-A10]
**CWE**: [CWE-ID]
**Status**: [Open/In Progress/Remediated/Accepted Risk]

### Description
[What the vulnerability is and why it matters]

### Affected Components
- [file:line or endpoint]

### Steps to Reproduce
1. [step]
2. [step]
3. [step]

### Evidence
[Screenshots, request/response pairs, code snippets]

### Impact
[What an attacker could achieve]

### Remediation
**Recommended fix**: [specific guidance]
**Code example**:
[secure code pattern]

### References
- [relevant OWASP page, CWE link, etc.]
```

### Evidence Collection Standards

- **Screenshots**: Annotated with timestamps, redacted sensitive data
- **HTTP traffic**: Full request/response pairs from Burp/ZAP (sanitized)
- **Code snippets**: Include file path, line numbers, and surrounding context
- **Tool output**: Raw scanner output with false positives marked
- **Proof of concept**: Minimal, safe PoC that demonstrates the issue without causing damage

## Phase 5: Remediation Prioritization

### Priority Matrix

| | High Exploitability | Low Exploitability |
|---|---|---|
| **High Impact** | P0 - Fix immediately | P1 - Fix this sprint |
| **Low Impact** | P2 - Fix next sprint | P3 - Backlog |

### Prioritization Decision Framework

```
For each finding, evaluate:

1. Is it actively exploitable in production?
   YES -> P0 (immediate hotfix)

2. Does it expose sensitive data or allow privilege escalation?
   YES + Easy to exploit -> P0
   YES + Hard to exploit -> P1

3. Is it a configuration or dependency issue with a known fix?
   YES -> P1 (low effort, high value)

4. Does it require architectural changes?
   YES -> P2 with design spike

5. Is it informational or defense-in-depth?
   YES -> P3 (backlog)
```

### Remediation Tracking

```markdown
## Remediation Status Report

| Finding ID | Severity | Owner | Status | Target Date | Verified |
|---|---|---|---|---|---|
| FIND-001 | Critical | @dev-a | In Progress | 2025-02-01 | - |
| FIND-002 | High | @dev-b | Remediated | 2025-01-20 | Pending |
| FIND-003 | Medium | @dev-a | Open | 2025-03-01 | - |
```

### Retest Protocol

After remediation:
1. Re-run the original test case to confirm the fix
2. Test for regressions (did the fix break adjacent functionality)
3. Test for bypass (can the fix be circumvented with a variation)
4. Update finding status and add verification evidence
5. Run automated scanners to catch any new issues introduced by the fix

## Assessment Report Structure

```
1. Executive Summary
   - Scope and methodology
   - Key findings summary (critical/high/medium/low counts)
   - Overall risk posture assessment
   - Top 3 recommendations

2. Detailed Findings (by severity, then OWASP category)
   - Finding details using template above
   - Grouped by OWASP category for remediation planning

3. Remediation Roadmap
   - Prioritized action items with owners and timelines
   - Quick wins vs. strategic fixes
   - Dependency mapping between fixes

4. Appendices
   - Full tool output and scan results
   - Testing methodology details
   - Glossary and references
```
