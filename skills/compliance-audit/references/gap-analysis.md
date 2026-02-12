# Gap Analysis Reference

Control mapping methodology, gap identification, risk scoring, remediation planning,
and timeline analysis for compliance audits.

---

## Control Mapping Methodology

### Step 1: Build the Requirements Matrix

For each applicable framework, list every control requirement:

```
| Control ID | Requirement Description | Category | Priority |
|------------|------------------------|----------|----------|
| CC6.1 | Restrict logical access | Access Control | High |
| CC6.2 | Authenticate users before access | Authentication | High |
| CC6.3 | Manage authorization for access | Authorization | High |
```

### Step 2: Map to Existing Controls

For each requirement, document the current state:

| Requirement ID | Existing Control | Implementation | Coverage |
|---------------|-----------------|----------------|----------|
| CC6.1 | AWS IAM policies + Okta SSO | Automated provisioning/deprovisioning | Full |
| CC6.2 | Okta MFA for all users | Enforced at IdP level | Full |
| CC6.3 | Role-based access in app | Manual role assignment, no periodic review | Partial |

### Coverage Levels

| Level | Definition | Action Required |
|-------|-----------|----------------|
| **Full** | Control fully implemented and operating effectively | Evidence collection only |
| **Partial** | Control exists but has gaps in coverage or effectiveness | Gap remediation |
| **None** | No control addresses this requirement | New control implementation |
| **N/A** | Requirement not applicable to this scope | Document justification |

---

## Gap Identification

### Gap Categories

| Category | Description | Example |
|----------|-------------|---------|
| **Documentation** | Control exists but is not documented | MFA enforced but no written policy |
| **Process** | Procedure exists informally but not standardized | Ad-hoc access reviews |
| **Technology** | Technical control is missing or incomplete | No encryption at rest for backups |
| **Training** | People lack awareness or skills | No security training program |
| **Monitoring** | Control exists but no way to verify ongoing compliance | No alerting on policy violations |
| **Testing** | Control never validated for effectiveness | Backup recovery never tested |

### Gap Discovery Techniques

1. **Control walkthroughs**: Ask control owners to demonstrate the control in action
2. **Sample testing**: Select a sample of transactions/events and verify the control operated
3. **Configuration review**: Compare system settings against documented requirements
4. **Log analysis**: Review audit logs for control failures or bypasses
5. **Automated scanning**: Run compliance scanners (Prowler, ScoutSuite, Checkov)
6. **Interview**: Ask process participants about actual practice vs documented procedure

### Gap Documentation Template

```markdown
## Gap: [GAP-ID]

**Framework Requirement**: [Control ID — description]
**Category**: [Documentation | Process | Technology | Training | Monitoring | Testing]
**Current State**: [What exists today]
**Required State**: [What compliance requires]
**Gap Description**: [Specific description of what is missing]
**Risk Impact**: [What could go wrong if this gap is not addressed]
**Discovered**: [Date]
**Evidence**: [How the gap was identified]
```

---

## Risk Scoring

### Risk Assessment Matrix

Score each gap on two dimensions:

**Likelihood** (how likely is the gap to cause a compliance failure or security incident):

| Score | Level | Criteria |
|-------|-------|----------|
| 1 | Rare | Unlikely to occur, strong compensating controls |
| 2 | Unlikely | Could occur but compensating controls reduce probability |
| 3 | Possible | May occur, limited compensating controls |
| 4 | Likely | Expected to occur without remediation |
| 5 | Almost Certain | Gap is actively causing issues or has no compensating controls |

**Impact** (severity of the consequence if the gap is exploited or causes failure):

| Score | Level | Criteria |
|-------|-------|----------|
| 1 | Negligible | Minor documentation issue, no operational impact |
| 2 | Minor | Limited operational impact, easily remediated |
| 3 | Moderate | Compliance finding, requires remediation plan |
| 4 | Major | Significant compliance failure, potential regulatory action |
| 5 | Critical | Breach, data loss, or regulatory penalty |

### Risk Score Calculation

```
Risk Score = Likelihood x Impact
```

| Score Range | Risk Level | Response |
|-------------|-----------|----------|
| 1-4 | **Low** | Accept or schedule remediation in normal cycle |
| 5-9 | **Medium** | Remediate within 90 days |
| 10-15 | **High** | Remediate within 30 days |
| 16-25 | **Critical** | Immediate remediation or escalation |

### Risk Heat Map

```
Impact →        1       2       3       4       5
Likelihood ↓
    5           5      10      15      20      25
    4           4       8      12      16      20
    3           3       6       9      12      15
    2           2       4       6       8      10
    1           1       2       3       4       5
```

---

## Remediation Planning

### Remediation Plan Template

| Field | Content |
|-------|---------|
| Gap ID | GAP-001 |
| Risk Score | 12 (High) |
| Remediation Action | Implement automated quarterly access reviews |
| Owner | Security Engineering |
| Approver | CISO |
| Start Date | 2026-02-01 |
| Target Completion | 2026-03-15 |
| Dependencies | IAM integration with HR system (GAP-003) |
| Resources Required | 1 engineer, 2 sprints |
| Success Criteria | First automated review completed with documented results |
| Verification Method | Audit log of review execution + access changes |

### Prioritization Framework

Prioritize remediation based on:

1. **Risk score** — highest risk first
2. **Dependencies** — unblock other remediations
3. **Quick wins** — low effort + high impact
4. **Audit timeline** — items needed before upcoming audits
5. **Regulatory deadlines** — hard compliance dates

### Remediation Categories

| Category | Typical Effort | Examples |
|----------|---------------|---------|
| **Quick fix** | <1 day | Enable a setting, update a policy document |
| **Configuration** | 1-5 days | Implement encryption, configure logging |
| **Process** | 1-4 weeks | Build a review process, create training program |
| **Architecture** | 1-3 months | Redesign access model, implement segmentation |
| **Cultural** | 3-12 months | Security awareness program, compliance culture shift |

---

## Timeline Analysis

### Audit Readiness Timeline

```
Months before audit:

12  │ Start gap analysis, begin long-lead remediations
    │
 9  │ Architecture changes and process redesigns in progress
    │
 6  │ All controls implemented, begin evidence collection
    │ SOC 2 Type II observation period starts
    │
 3  │ Internal audit / readiness assessment
    │ Remediate any new findings
    │
 1  │ Evidence package preparation
    │ Pre-audit review with auditor
    │
 0  │ External audit
```

### Progress Tracking

Track remediation progress with these metrics:

| Metric | Calculation | Target |
|--------|-------------|--------|
| Gaps Closed Rate | Gaps remediated / Total gaps | 100% critical by audit |
| On-Time Rate | Gaps closed by target date / Total gaps | >90% |
| Risk Reduction | Starting risk score total - Current risk score total | Trending down |
| Evidence Coverage | Controls with current evidence / Total controls | >95% |
| Audit Readiness | Controls passing verification / Total required controls | >90% |

### Status Reporting Template

```markdown
## Compliance Gap Remediation Status — [Date]

### Summary
- Total gaps identified: [N]
- Remediated: [N] ([%])
- In progress: [N]
- Not started: [N]
- Overdue: [N]

### Risk Distribution
- Critical: [N] gaps ([N] remediated)
- High: [N] gaps ([N] remediated)
- Medium: [N] gaps ([N] remediated)
- Low: [N] gaps ([N] remediated)

### Key Changes Since Last Report
- [Gap ID]: [Status change and details]

### Blockers
- [Description of any blocked remediations]

### Next Steps
- [Upcoming milestones and target dates]
```

---

## Compensating Controls

When a gap cannot be remediated directly, document compensating controls:

| Field | Content |
|-------|---------|
| Original Requirement | [What the framework requires] |
| Constraint | [Why the requirement cannot be met directly] |
| Compensating Control | [Alternative control that mitigates the risk] |
| Risk Reduction | [How much risk the compensating control addresses] |
| Residual Risk | [What risk remains after the compensating control] |
| Approval | [Who approved the compensating control and when] |
| Review Date | [When to re-evaluate if the original control can be implemented] |

Compensating controls should be:
- Above and beyond other existing controls
- Commensurate with the risk of the original requirement
- Documented with clear justification
- Reviewed periodically (at least annually)
