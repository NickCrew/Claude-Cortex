# Evidence Collection Reference

Patterns for automated evidence gathering, artifact organization, retention policies,
and audit trail maintenance.

---

## Evidence Types

| Type | Description | Examples |
|------|-------------|---------|
| **Configuration** | System settings and infrastructure state | Cloud IAM policies, firewall rules, encryption settings |
| **Logs** | Time-stamped records of activity | Access logs, audit trails, change logs |
| **Screenshots** | Visual proof of control implementation | Dashboard views, settings pages, alert configurations |
| **Exports** | Machine-readable data exports | User access lists, scan results, inventory reports |
| **Attestations** | Human confirmations of process adherence | Training acknowledgments, policy sign-offs |
| **Test Results** | Output from control testing | Penetration test reports, vulnerability scan results |
| **Process Records** | Documentation of procedures followed | Incident response records, change tickets |

---

## Automated Evidence Gathering

### Cloud Provider Evidence

**AWS:**
```bash
# IAM policy export
aws iam get-account-authorization-details > evidence/aws-iam-$(date +%Y%m%d).json

# S3 bucket encryption status
aws s3api list-buckets --query 'Buckets[].Name' | \
  xargs -I {} aws s3api get-bucket-encryption --bucket {} > evidence/aws-s3-encryption-$(date +%Y%m%d).json

# Security group rules
aws ec2 describe-security-groups > evidence/aws-security-groups-$(date +%Y%m%d).json

# CloudTrail status
aws cloudtrail describe-trails > evidence/aws-cloudtrail-$(date +%Y%m%d).json
```

**GCP:**
```bash
# IAM policy
gcloud projects get-iam-policy $PROJECT_ID --format=json > evidence/gcp-iam-$(date +%Y%m%d).json

# Firewall rules
gcloud compute firewall-rules list --format=json > evidence/gcp-firewall-$(date +%Y%m%d).json

# Audit logging config
gcloud projects get-iam-policy $PROJECT_ID --format=json | \
  jq '.auditConfigs' > evidence/gcp-audit-config-$(date +%Y%m%d).json
```

**Azure:**
```bash
# Role assignments
az role assignment list --all > evidence/azure-rbac-$(date +%Y%m%d).json

# NSG rules
az network nsg list > evidence/azure-nsg-$(date +%Y%m%d).json

# Key vault configuration
az keyvault list --query '[].{name:name,sku:properties.sku}' > evidence/azure-keyvault-$(date +%Y%m%d).json
```

### Infrastructure as Code Evidence

```bash
# Terraform state (sanitized — remove secrets)
terraform show -json | jq 'del(.. | .sensitive_values?)' > evidence/terraform-state-$(date +%Y%m%d).json

# Checkov scan results
checkov -d . --output json > evidence/iac-scan-$(date +%Y%m%d).json

# Terrascan results
terrascan scan -d . -o json > evidence/terrascan-$(date +%Y%m%d).json
```

### Application-Level Evidence

```bash
# Dependency vulnerability scan
npm audit --json > evidence/npm-audit-$(date +%Y%m%d).json

# SAST scan results
semgrep --config=auto --json . > evidence/sast-$(date +%Y%m%d).json

# Access control export (application-specific)
curl -H "Authorization: Bearer $TOKEN" \
  https://api.internal/admin/users?include=roles \
  > evidence/access-control-$(date +%Y%m%d).json
```

---

## Artifact Organization

### Directory Structure

```
evidence/
  {framework}/                    # e.g., soc2, pci-dss, gdpr
    {control-id}/                 # e.g., CC6.1, req-3, art-32
      {date}-{artifact-name}/
        artifact.{ext}            # The actual evidence file
        metadata.yaml             # Collection metadata
        README.md                 # Human-readable description
```

### Metadata Schema

Every artifact must have a `metadata.yaml`:

```yaml
artifact_id: "CC6.1-2026-01-15-iam-export"
framework: soc2
control_id: CC6.1
control_name: "Logical Access Security"
collected_at: "2026-01-15T10:30:00Z"
collected_by: "automated/aws-evidence-collector"
collection_method: "API export"
source_system: "AWS IAM"
environment: production
hash: "sha256:abc123..."        # Integrity verification
retention_until: "2029-01-15"   # 3-year retention
review_status: pending          # pending | reviewed | approved
reviewer: null
reviewed_at: null
notes: ""
```

### Naming Conventions

- Use ISO 8601 dates: `2026-01-15`
- Lowercase with hyphens: `iam-policy-export`
- Include the environment: `prod`, `staging`, `dev`
- Version artifacts when updated: `v1`, `v2`

---

## Retention Policies

| Framework | Minimum Retention | Recommended |
|-----------|------------------|-------------|
| GDPR | Duration of processing + statute of limitations | 5 years after collection |
| HIPAA | 6 years from creation or last effective date | 7 years |
| PCI DSS | 1 year of audit logs, 3 years of policies | 3 years for all evidence |
| SOC 2 | Duration of audit period + 1 year | 3 years |
| ISO 27001 | 3-year certification cycle | 3 years minimum |

### Retention Automation

```yaml
# retention-policy.yaml
rules:
  - match: "evidence/soc2/**"
    retain_for: "3 years"
    action_on_expiry: archive
    archive_to: "s3://compliance-archive/"

  - match: "evidence/hipaa/**"
    retain_for: "7 years"
    action_on_expiry: archive

  - match: "evidence/**/logs/**"
    retain_for: "1 year"
    action_on_expiry: delete

  - match: "evidence/**/scan-results/**"
    retain_for: "3 years"
    action_on_expiry: archive
```

---

## Audit Trail Patterns

### What to Log

Every compliance-relevant action should generate an audit record:

| Event | Required Fields |
|-------|----------------|
| User access granted/revoked | Who, what resource, by whom, when, justification |
| Configuration change | What changed, old value, new value, who, when, ticket |
| Data access | Who accessed what data, when, from where |
| Evidence collected | What artifact, source, method, collector, timestamp |
| Policy acknowledged | Who, which policy, version, timestamp |
| Incident detected/resolved | Type, severity, timeline, actions taken, resolution |

### Audit Log Format

```json
{
  "timestamp": "2026-01-15T10:30:00Z",
  "event_type": "access_granted",
  "actor": "admin@company.com",
  "action": "grant_role",
  "resource": "production-database",
  "details": {
    "role": "read-only",
    "granted_to": "developer@company.com",
    "justification": "JIRA-1234",
    "approved_by": "manager@company.com",
    "expires_at": "2026-04-15T00:00:00Z"
  },
  "source_ip": "10.0.1.50",
  "user_agent": "internal-admin-portal/2.1"
}
```

### Integrity Protection

- Write logs to append-only storage (e.g., S3 Object Lock, WORM drives)
- Hash log entries for tamper detection
- Forward logs to a centralized SIEM in near real-time
- Separate log storage from systems being audited
- Restrict log deletion to break-glass procedures only

---

## Collection Scheduling

### Recommended Cadence

| Evidence Type | Collection Frequency |
|---------------|---------------------|
| Access control lists | Weekly |
| Configuration exports | Weekly |
| Vulnerability scan results | Monthly (or per scan) |
| Penetration test reports | Annually or after major changes |
| Training completion records | Quarterly |
| Policy acknowledgments | On policy update + annual refresh |
| Audit logs | Continuous (streamed) |
| Incident response records | Per incident |
| Vendor assessments | Annually |

### Automation Checklist

- [ ] Evidence collection scripts run on schedule (cron, CI/CD pipeline)
- [ ] Collection failures trigger alerts
- [ ] Metadata is auto-generated with each artifact
- [ ] Integrity hashes are computed at collection time
- [ ] Retention rules are enforced automatically
- [ ] Expired artifacts are archived or deleted per policy
- [ ] Collection dashboard shows freshness and gaps
