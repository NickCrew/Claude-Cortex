# Security & Hardening Flags

Flags for security-focused development, threat modeling, and compliance.

**Estimated tokens: ~190**

---

**--secure / --security-first**
- Trigger: Authentication, authorization, payments, PII handling, production deployment
- Behavior: Enable security-focused code review, threat modeling, and vulnerability detection
- Auto-enables: security-auditor agent, OWASP Top 10 checks, dependency vulnerability scanning
- Validates: Input sanitization, SQL injection prevention, XSS protection, CSRF tokens
- Checks: Authentication flows, authorization logic, session management, password hashing
- Standards: OWASP ASVS, CWE Top 25, NIST guidelines
- Reports: Security vulnerabilities by severity, remediation guidance, compliance status

**--threat-model**
- Trigger: New features touching security boundaries, API design, data flow changes
- Behavior: Generate comprehensive threat model before implementation
- Methodology: STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
- Produces: Attack surface analysis, threat scenarios, trust boundaries, mitigation strategies
- Analyzes: Data flows, entry points, trust zones, assets at risk, threat actors
- Deliverables: Threat model diagram, prioritized risks, security controls, acceptance criteria
- Related: Security requirements, abuse cases, attack trees

**--audit-log**
- Trigger: Compliance requirements, financial systems, healthcare data, audit trails
- Behavior: Ensure all security-relevant actions are logged comprehensively
- Validates: Comprehensive audit logging, immutable log storage, log retention policies
- Captures: Who (user/service), What (action), When (timestamp), Where (IP/location), Why (context)
- Standards: SOC2, HIPAA, PCI-DSS, GDPR audit requirements
- Ensures: Log integrity, tamper detection, log rotation, secure log storage
- Prevents: Log injection, sensitive data in logs, insufficient audit trails

**--secrets-management**
- Trigger: API keys, database passwords, certificates, encryption keys
- Behavior: Enforce proper secrets management and prevent credential leaks
- Validates: No hardcoded secrets, environment variable usage, secret rotation
- Checks: .env files not committed, secure secret storage (Vault, AWS Secrets Manager)
- Scans: Git history for leaked credentials, common secret patterns
- Recommends: Secret encryption at rest, least privilege access, key rotation schedules
- Tools: git-secrets, truffleHog, detect-secrets

**--secure-dependencies**
- Trigger: npm install, pip install, dependency updates, CI/CD pipelines
- Behavior: Analyze dependencies for known vulnerabilities and supply chain risks
- Scans: CVE databases, GitHub Security Advisories, Snyk, OSV
- Checks: Dependency licenses, transitive dependencies, outdated packages
- Reports: Vulnerability severity, exploitability, fix versions, workarounds
- Automates: Dependency update PRs for security patches
- Tools: npm audit, pip-audit, Dependabot, Renovate

**--principle-least-privilege**
- Trigger: IAM policies, database permissions, API access control, service accounts
- Behavior: Enforce least privilege access throughout the system
- Validates: Minimal permissions granted, role-based access control, permission boundaries
- Checks: Overly permissive roles, unused permissions, privilege escalation paths
- Recommends: Fine-grained permissions, temporary credentials, just-in-time access
- Standards: Zero trust architecture, defense in depth
