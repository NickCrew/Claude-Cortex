# Mitigation Strategies

## Risk Prioritization Matrix

**Risk Level = Likelihood × Impact**

| Impact →     | Low (1) | Medium (2) | High (3) | Critical (4) |
|--------------|---------|------------|----------|--------------|
| **High (3)** | Medium  | High       | Critical | Critical     |
| **Med (2)**  | Low     | Medium     | High     | Critical     |
| **Low (1)**  | Low     | Low        | Medium   | High         |

**Priority Actions:**
- **Critical**: Immediate action, stop release if necessary
- **High**: Fix before next release
- **Medium**: Schedule in upcoming sprint
- **Low**: Backlog, fix when convenient

## Four Mitigation Approaches

### 1. Eliminate

**Strategy:** Remove the threat entirely by eliminating the vulnerable feature or attack surface.

**When to Use:**
- Feature is not critical to functionality
- Risk significantly outweighs benefit
- Simpler alternatives exist

**Examples:**
- Disable unused administrative endpoints
- Remove unnecessary file upload functionality
- Eliminate deprecated authentication methods
- Shut down unused network services
- Remove debug endpoints in production

**Pros:**
- Most effective mitigation (threat gone)
- No ongoing maintenance cost
- No performance impact

**Cons:**
- May reduce functionality
- May require architecture changes

### 2. Reduce

**Strategy:** Implement security controls to reduce the likelihood or impact of the threat.

**When to Use:**
- Feature is necessary
- Risk can be managed to acceptable level
- Controls are cost-effective

**Examples:**
- Add authentication/authorization to exposed endpoints
- Implement input validation and sanitization
- Apply principle of least privilege
- Add rate limiting and throttling
- Encrypt sensitive data
- Add logging and monitoring

**Pros:**
- Maintains functionality
- Can reduce risk significantly
- Industry-standard approach

**Cons:**
- Requires implementation effort
- Ongoing maintenance needed
- May impact performance

### 3. Transfer

**Strategy:** Shift the risk to a third party or external service.

**When to Use:**
- Third party has better security expertise
- Risk is too high to manage internally
- Compliance requires specialized controls

**Examples:**
- Use Auth0/Okta instead of custom authentication
- Use cloud provider's encryption (KMS, AWS Secrets Manager)
- Purchase cyber insurance
- Use payment processor for credit card handling (PCI compliance)
- Leverage CDN for DDoS protection (Cloudflare, Akamai)

**Pros:**
- Reduced internal complexity
- Expert-managed security
- Insurance coverage for incidents

**Cons:**
- Ongoing costs
- Vendor dependency
- May not eliminate risk entirely

### 4. Accept

**Strategy:** Acknowledge the risk and accept the potential consequences.

**When to Use:**
- Mitigation cost exceeds potential damage
- Risk level is very low
- Legal/compliance obligations met

**Examples:**
- Known UI bug with minimal impact
- Theoretical attack requiring nation-state resources
- Low-value internal tool with limited exposure

**Requirements:**
- **Document risk acceptance**: Written record with justification
- **Get approval**: Management sign-off on acceptance
- **Implement monitoring**: Detect if risk materializes
- **Plan incident response**: Know what to do if exploited
- **Review periodically**: Risk may increase over time

**Pros:**
- No implementation cost
- Focus resources on higher risks

**Cons:**
- Risk remains present
- May materialize despite low likelihood
- Potential liability if exploited

## Control Types

### Preventive Controls

**Purpose:** Stop threats before they occur

**Examples:**
- **Input validation**: Block malicious inputs at entry
- **Access controls**: RBAC, ABAC, least privilege
- **Encryption**: Protect data at rest and in transit
- **Authentication**: MFA, certificate-based auth
- **Secure coding**: Parameterized queries, output encoding
- **Network segmentation**: Firewalls, VLANs, DMZ
- **Secure configuration**: Disable defaults, harden systems

**Characteristics:**
- First line of defense
- Most cost-effective (prevent > detect > respond)
- Requires design-time implementation

### Detective Controls

**Purpose:** Identify threats in progress or after occurrence

**Examples:**
- **Logging and monitoring**: Centralized log aggregation
- **Intrusion detection systems (IDS)**: Network and host-based
- **SIEM**: Security information and event management
- **File integrity monitoring (FIM)**: Detect unauthorized changes
- **Anomaly detection**: ML-based behavior analysis
- **Audit trails**: Comprehensive activity logging
- **Vulnerability scanning**: Regular automated scans

**Characteristics:**
- Second line of defense
- Enables quick response
- Requires ongoing monitoring

### Corrective Controls

**Purpose:** Respond to detected threats and restore normal operations

**Examples:**
- **Incident response procedures**: Documented playbooks
- **Backup and recovery**: Regular backups, tested restores
- **Patching and updates**: Automated patch management
- **Account lockout**: Automatic response to brute force
- **Failover systems**: Redundant infrastructure
- **Rollback mechanisms**: Version control, database snapshots

**Characteristics:**
- Third line of defense
- Minimizes damage and downtime
- Requires preparation and testing

## Defense in Depth

**Principle:** Layer multiple controls so failure of one doesn't compromise security.

### Example Layered Defense

**Threat:** SQL Injection

**Layer 1 - Preventive:**
- Use parameterized queries (ORM, prepared statements)
- Input validation with allow-lists
- Least privilege database accounts

**Layer 2 - Detective:**
- Database activity monitoring
- SIEM alerts on suspicious queries
- Anomaly detection for data access patterns

**Layer 3 - Corrective:**
- Automated query blocking on detection
- Database connection kill switches
- Backup and recovery procedures

**Result:** Even if one layer fails, others provide protection

## Mitigation Effectiveness

### Measuring Control Effectiveness

**Metrics:**
- **Risk Reduction**: DREAD score before and after mitigation
- **Coverage**: Percentage of attack paths blocked
- **Detection Rate**: True positives vs. false positives
- **Response Time**: Time to detect and respond
- **Cost**: Implementation and ongoing maintenance

### Example Effectiveness Analysis

**Threat:** Credential Stuffing Attack

**Mitigation Options:**

| Control | Risk Reduction | Coverage | Implementation Cost | Ongoing Cost | Effectiveness Score |
|---------|----------------|----------|---------------------|--------------|---------------------|
| Rate Limiting | Medium (30%) | 60% | Low | Low | **Good** |
| CAPTCHA | High (60%) | 80% | Low | Medium | **Excellent** |
| MFA | Very High (90%) | 95% | Medium | Low | **Outstanding** |
| Passwordless Auth | Complete (100%) | 100% | High | Medium | **Best** |

**Recommendation:** Implement MFA as immediate mitigation, plan migration to passwordless authentication for long-term solution.

## Security Requirements Template

**From threat model to actionable requirements:**

```markdown
## Security Requirement: [ID]

### Threat Context
- **Threat**: [Brief description]
- **STRIDE Category**: [S/T/R/I/D/E]
- **Risk Score (DREAD)**: [Score] ([Low/Medium/High/Critical])
- **Attack Vector**: [How the attack works]

### Requirement
[Specific, testable security control to implement]

### Acceptance Criteria
- [ ] [Criterion 1 - must be testable]
- [ ] [Criterion 2 - must be testable]
- [ ] [Criterion 3 - must be testable]

### Implementation Notes
[Technical guidance, patterns, libraries to use]

### Verification Method
- **Code Review**: [What to look for]
- **Testing**: [How to test]
- **Tools**: [SAST, DAST, manual testing]

### Owner
- **Team**: [Responsible team]
- **Due Date**: [Sprint/release]

### Dependencies
- [Required changes, infrastructure, etc.]
```

### Example Security Requirement

```markdown
## Security Requirement: SEC-001

### Threat Context
- **Threat**: SQL Injection in product search endpoint
- **STRIDE Category**: Tampering, Information Disclosure, Elevation of Privilege
- **Risk Score (DREAD)**: 8.8 (Critical)
- **Attack Vector**: Malicious SQL in search parameter

### Requirement
All database queries MUST use parameterized statements or ORM methods. String concatenation for SQL queries is prohibited.

### Acceptance Criteria
- [ ] No string concatenation in any SQL query
- [ ] ORM (Sequelize) used for all database operations
- [ ] Input validation with allow-list for search terms
- [ ] SQL injection testing included in automated test suite
- [ ] SAST tool configured to detect SQL concatenation

### Implementation Notes
- Use Sequelize ORM for all queries
- For complex queries requiring raw SQL, use `sequelize.query()` with bound parameters
- Validate input: alphanumeric characters only, max 100 chars
- Library: `validator.js` for input sanitization

### Verification Method
- **Code Review**: Check for raw SQL, string interpolation
- **Testing**: Automated SQLMap scan, manual injection attempts
- **Tools**: SonarQube (SAST), OWASP ZAP (DAST)

### Owner
- **Team**: Backend Team
- **Due Date**: Sprint 23 (before release)

### Dependencies
- Sequelize ORM already in use
- Update test suite with security test cases
```
