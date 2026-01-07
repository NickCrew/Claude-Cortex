# Testing & Validation

## 1. Pre-Commit Validation

```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_docs
      - id: terraform_tflint
      - id: terraform_tfsec

# Ensures code quality before commits
```

## 2. Terraform Validate & Plan

```bash
# Always validate before planning
terraform init
terraform validate

# Review plan output thoroughly
terraform plan -out=tfplan

# Save and review plans before applying
terraform show tfplan

# Apply only after approval
terraform apply tfplan
```

## 3. Automated Testing with Terratest

```go
// test/vpc_test.go
func TestVPCCreation(t *testing.T) {
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../examples/simple",
        Vars: map[string]interface{}{
            "environment": "test",
            "cidr_block":  "10.0.0.0/16",
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcID)
}
```

## 4. Policy as Code

```rego
# policy/deny_public_s3_buckets.rego
package terraform.s3

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    resource.change.after.acl == "public-read"

    msg := sprintf("S3 bucket '%s' has public ACL", [resource.name])
}

# Use Open Policy Agent (OPA) or Sentinel
# Enforce policies in CI/CD pipeline
```

## 5. Validation Workflow

1. **Pre-commit hooks**: Format, validate, lint
2. **Local validation**: `terraform validate` before commits
3. **CI/CD validation**: Automated testing on PR
4. **Security scanning**: tfsec, Checkov in pipeline
5. **Plan review**: Manual review before apply
6. **Automated tests**: Terratest for critical modules
7. **Policy enforcement**: OPA/Sentinel gates
