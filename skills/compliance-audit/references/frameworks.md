# Compliance Frameworks Reference

Key requirements, control mappings, and certification paths for the major regulatory
and security compliance frameworks.

---

## GDPR (General Data Protection Regulation)

### Key Requirements

| Area | Requirement | Articles |
|------|-------------|----------|
| Lawful basis | Processing must have a documented legal basis | Art. 6 |
| Consent | Must be freely given, specific, informed, and unambiguous | Art. 7 |
| Data subject rights | Right to access, rectification, erasure, portability, objection | Art. 15-22 |
| Data protection by design | Privacy built into systems from the start | Art. 25 |
| Breach notification | 72-hour notification to supervisory authority | Art. 33 |
| DPO appointment | Required for large-scale processing of sensitive data | Art. 37 |
| DPIA | Required for high-risk processing activities | Art. 35 |
| Cross-border transfers | Adequate safeguards for transfers outside EEA | Art. 44-49 |

### Control Mapping

```
GDPR Art. 5 (Principles) → ISO 27001 A.5 (Information Security Policies)
GDPR Art. 25 (By Design) → ISO 27001 A.14 (System Acquisition/Development)
GDPR Art. 32 (Security)  → ISO 27001 A.9-A.14 (Access, Crypto, Operations)
GDPR Art. 33 (Breach)    → ISO 27001 A.16 (Incident Management)
```

### Certification Path

1. Data inventory and lawful basis mapping
2. Privacy notices and consent mechanisms
3. Data subject rights automation
4. Data protection impact assessments
5. Breach detection and notification procedures
6. Cross-border transfer safeguards (SCCs, BCRs)
7. DPO appointment and governance structure
8. Ongoing monitoring and annual review

---

## HIPAA (Health Insurance Portability and Accountability Act)

### Key Requirements

| Rule | Focus | Key Controls |
|------|-------|-------------|
| Privacy Rule | How PHI can be used and disclosed | Minimum necessary, patient rights, authorization |
| Security Rule | Technical safeguards for ePHI | Access control, audit controls, integrity, transmission security |
| Breach Notification | Response to unauthorized PHI disclosure | Risk assessment, notification within 60 days |
| Enforcement Rule | Penalties for non-compliance | Civil and criminal penalties by tier |

### Security Rule Safeguards

**Administrative Safeguards (164.308):**
- Security management process (risk analysis, risk management)
- Assigned security responsibility
- Workforce security (authorization, clearance, termination)
- Information access management
- Security awareness and training
- Security incident procedures
- Contingency plan (backup, disaster recovery, emergency mode)

**Physical Safeguards (164.310):**
- Facility access controls
- Workstation use and security
- Device and media controls

**Technical Safeguards (164.312):**
- Access control (unique user ID, emergency access, auto logoff, encryption)
- Audit controls (log all ePHI access)
- Integrity controls (authentication of ePHI)
- Transmission security (encryption in transit)

### Certification Path

HIPAA does not have a formal certification. Compliance is demonstrated through:
1. Comprehensive risk analysis
2. Documented policies and procedures
3. Business Associate Agreements (BAAs)
4. Workforce training records
5. Incident response plan and testing
6. Regular audits (internal or third-party)
7. Remediation tracking for identified risks

---

## PCI DSS (Payment Card Industry Data Security Standard)

### 12 Requirements

| # | Requirement | Focus |
|---|-------------|-------|
| 1 | Install and maintain network security controls | Firewalls, network segmentation |
| 2 | Apply secure configurations | Vendor defaults, hardening |
| 3 | Protect stored account data | Encryption, masking, retention |
| 4 | Protect cardholder data in transit | TLS, strong cryptography |
| 5 | Protect from malicious software | Anti-malware, integrity monitoring |
| 6 | Develop and maintain secure systems | Vulnerability management, secure SDLC |
| 7 | Restrict access by business need | Role-based access control |
| 8 | Identify users and authenticate access | MFA, strong passwords |
| 9 | Restrict physical access to cardholder data | Physical security controls |
| 10 | Log and monitor all access | Audit logging, SIEM, log review |
| 11 | Test security regularly | Vulnerability scans, penetration tests |
| 12 | Support security with policies and programs | Security policies, risk assessment |

### Compliance Levels

| Level | Criteria | Validation |
|-------|----------|------------|
| 1 | >6M transactions/year | Annual on-site assessment by QSA |
| 2 | 1-6M transactions/year | Annual SAQ, quarterly network scan |
| 3 | 20K-1M e-commerce transactions/year | Annual SAQ, quarterly network scan |
| 4 | <20K e-commerce or <1M other | Annual SAQ, quarterly network scan |

### Certification Path

1. Scope the cardholder data environment (CDE)
2. Reduce scope through segmentation and tokenization
3. Implement controls for all 12 requirements
4. Conduct internal vulnerability scanning
5. Perform penetration testing
6. Complete Self-Assessment Questionnaire (SAQ) or QSA assessment
7. Submit Attestation of Compliance (AOC)
8. Maintain quarterly ASV scans

---

## SOC 2 (Service Organization Control 2)

### Trust Service Criteria

| Criteria | Focus | When Required |
|----------|-------|--------------|
| **Security** (Common Criteria) | Protection against unauthorized access | Always required |
| **Availability** | System uptime and operational performance | SaaS, hosting, critical services |
| **Processing Integrity** | Data processing is complete and accurate | Payment, financial, data processing |
| **Confidentiality** | Protection of confidential information | B2B, regulated data handling |
| **Privacy** | Personal information handling | Consumer-facing services with PII |

### Common Criteria Controls (CC Series)

```
CC1: Control Environment        — Governance, ethics, accountability
CC2: Communication & Information — Internal/external communication
CC3: Risk Assessment            — Risk identification and management
CC4: Monitoring Activities      — Ongoing and periodic evaluation
CC5: Control Activities         — Policies implemented through actions
CC6: Logical & Physical Access  — Access provisioning and review
CC7: System Operations          — Detection and response to anomalies
CC8: Change Management          — Change authorization and testing
CC9: Risk Mitigation            — Risk acceptance and vendor management
```

### Type I vs Type II

| Aspect | Type I | Type II |
|--------|--------|---------|
| Scope | Design of controls at a point in time | Design and operating effectiveness over a period |
| Duration | Snapshot audit | Minimum 6-month observation period (12 months typical) |
| Value | "We have controls" | "Our controls work consistently" |
| Typical use | First-time SOC 2 | Ongoing compliance demonstration |

### Certification Path

1. Select trust service criteria based on customer requirements
2. Identify and document all in-scope controls
3. Implement controls and begin evidence collection
4. Engage a CPA firm as the auditor
5. Readiness assessment (gap analysis)
6. Type I audit (point-in-time control design)
7. Type II audit (operational effectiveness over 6-12 months)
8. Annual re-audit with continuous monitoring

---

## ISO 27001 (Information Security Management System)

### Structure

| Clause | Topic |
|--------|-------|
| 4 | Context of the organization |
| 5 | Leadership and commitment |
| 6 | Planning (risk assessment, risk treatment) |
| 7 | Support (resources, competence, awareness, communication, documentation) |
| 8 | Operation (risk treatment implementation) |
| 9 | Performance evaluation (monitoring, internal audit, management review) |
| 10 | Improvement (nonconformity, corrective action, continual improvement) |

### Annex A Control Domains (ISO 27001:2022)

| Domain | Controls | Focus |
|--------|----------|-------|
| A.5 | Organizational controls (37) | Policies, roles, asset management, access, supply chain |
| A.6 | People controls (8) | Screening, terms, awareness, remote work, reporting |
| A.7 | Physical controls (14) | Perimeter, entry, securing areas, equipment, media |
| A.8 | Technological controls (34) | Endpoints, access, crypto, development, operations, networks |

### Certification Path

1. Establish ISMS scope and context
2. Conduct risk assessment (identify, analyze, evaluate)
3. Create Statement of Applicability (SoA)
4. Implement risk treatment plan
5. Internal audit
6. Management review
7. Stage 1 audit (documentation review by certification body)
8. Stage 2 audit (implementation verification)
9. Certification granted (3-year cycle)
10. Annual surveillance audits (years 1 and 2)
11. Recertification audit (year 3)

---

## Cross-Framework Control Mapping

Common controls that satisfy multiple frameworks simultaneously:

| Control | GDPR | HIPAA | PCI DSS | SOC 2 | ISO 27001 |
|---------|------|-------|---------|-------|-----------|
| Access control / RBAC | Art. 32 | 164.312(a) | Req. 7-8 | CC6 | A.8.3-8.5 |
| Encryption at rest | Art. 32 | 164.312(a)(2)(iv) | Req. 3 | CC6 | A.8.24 |
| Encryption in transit | Art. 32 | 164.312(e)(1) | Req. 4 | CC6 | A.8.24 |
| Audit logging | Art. 30 | 164.312(b) | Req. 10 | CC7 | A.8.15 |
| Incident response | Art. 33-34 | 164.308(a)(6) | Req. 12 | CC7 | A.5.24-5.28 |
| Vulnerability management | Art. 32 | 164.308(a)(1) | Req. 6, 11 | CC7 | A.8.8 |
| Security training | Art. 39 | 164.308(a)(5) | Req. 12 | CC1 | A.6.3 |
| Vendor management | Art. 28 | 164.308(b)(1) | Req. 12 | CC9 | A.5.19-5.22 |
| Data retention | Art. 5(1)(e) | 164.530(j) | Req. 3 | P6 | A.5.33 |
| Backup / recovery | Art. 32 | 164.308(a)(7) | Req. 12 | A1 | A.8.13-8.14 |

**Strategy**: Implement controls once, map evidence to multiple frameworks to reduce
duplication and audit fatigue.
