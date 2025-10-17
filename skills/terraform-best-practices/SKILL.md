---
name: terraform-best-practices
description: Terraform infrastructure-as-code best practices for scalable and maintainable cloud infrastructure. Use when writing Terraform modules, managing infrastructure state, or implementing infrastructure automation at scale.
---

# Terraform Best Practices

Expert guidance for building production-grade Terraform infrastructure with enterprise patterns for module design, state management, security, testing, and multi-environment deployments.

## When to Use This Skill

- Writing reusable Terraform modules for teams or organizations
- Setting up secure remote state management and backend configuration
- Designing multi-environment infrastructure (dev/staging/prod)
- Implementing infrastructure CI/CD pipelines with automated validation
- Managing infrastructure at scale across multiple teams or projects
- Migrating from manual infrastructure to infrastructure-as-code
- Refactoring existing Terraform for better maintainability
- Implementing security best practices for infrastructure code

## Module Design Patterns

### 1. Module Structure

**Standard module layout:**
```
terraform-aws-vpc/
├── main.tf           # Primary resource definitions
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── versions.tf       # Provider and Terraform version constraints
├── README.md         # Documentation with examples
├── examples/
│   ├── simple/       # Minimal example
│   └── complete/     # Full-featured example
└── tests/            # Terratest or validation tests
```

### 2. Composition over Monoliths

**Child modules for reusability:**
```hcl
# Root module orchestrates child modules
module "vpc" {
  source = "./modules/vpc"

  cidr_block = var.vpc_cidr
  environment = var.environment
}

module "eks_cluster" {
  source = "./modules/eks"

  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  cluster_name = "${var.environment}-cluster"
}

# Benefits: Testable, reusable, maintainable
```

### 3. Variable Design

**Type constraints and validation:**
```hcl
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_config" {
  description = "Instance configuration"
  type = object({
    instance_type = string
    count         = number
    tags          = map(string)
  })

  default = {
    instance_type = "t3.medium"
    count         = 2
    tags          = {}
  }
}

# Use complex types for structured configuration
```

### 4. Output Organization

**Well-structured outputs:**
```hcl
output "vpc_id" {
  description = "VPC identifier"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "Private subnet identifiers for workload placement"
  value       = aws_subnet.private[*].id
}

output "connection_info" {
  description = "Database connection information"
  value = {
    endpoint = aws_db_instance.main.endpoint
    port     = aws_db_instance.main.port
  }
  sensitive = true  # Mark sensitive outputs
}
```

### 5. Dynamic Blocks for Flexibility

```hcl
resource "aws_security_group" "main" {
  name   = "${var.environment}-sg"
  vpc_id = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}

# Enables flexible configuration without code duplication
```

## State Management Best Practices

### 1. Remote Backend Configuration

**S3 with DynamoDB locking:**
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "projects/myapp/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"

    # Enable versioning on S3 bucket for state history
    # Enable encryption at rest with KMS
  }
}

# Required AWS resources (separate bootstrap):
# - S3 bucket with versioning enabled
# - S3 bucket encryption with KMS
# - DynamoDB table with LockID primary key
# - IAM policies for terraform execution role
```

**Terraform Cloud backend:**
```hcl
terraform {
  cloud {
    organization = "company-name"

    workspaces {
      name = "myapp-production"
      # OR tags = ["myapp", "production"] for dynamic workspaces
    }
  }
}

# Benefits: Built-in state locking, versioning, collaboration
# Remote execution, policy as code, cost estimation
```

### 2. State File Security

```hcl
# Never commit state files to version control
# .gitignore
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl

# Encrypt state at rest (S3 KMS encryption)
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.terraform.id
    }
  }
}

# Restrict state bucket access with strict IAM policies
# Enable MFA delete for production state buckets
```

### 3. State Operations

```bash
# Import existing resources
terraform import aws_instance.example i-1234567890abcdef0

# Move resources between modules
terraform state mv aws_instance.old aws_instance.new

# Remove resources from state (doesn't destroy)
terraform state rm aws_instance.example

# Refresh state from actual infrastructure
terraform refresh

# List all resources in state
terraform state list

# Show specific resource details
terraform state show aws_instance.example
```

### 4. Workspace Strategies

**When to use workspaces:**
```bash
# Same code, different state (dev/staging/prod)
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Access workspace name in code
resource "aws_instance" "example" {
  tags = {
    Environment = terraform.workspace
  }
}

# Limitations:
# - All workspaces share same backend configuration
# - Cannot have different provider settings per workspace
# - Better for similar environments, not vastly different ones
```

**Directory-based environments (preferred for production):**
```
project/
├── modules/          # Shared modules
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── backend.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── backend.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       ├── backend.tf
│       └── terraform.tfvars

# Benefits: Complete isolation, different backends,
# environment-specific configurations
```

## Workspace & Environment Management

### 1. Variable Precedence

```bash
# Terraform variable precedence (highest to lowest):
# 1. -var or -var-file CLI flags
# 2. *.auto.tfvars or *.auto.tfvars.json (alphabetical)
# 3. terraform.tfvars or terraform.tfvars.json
# 4. Environment variables (TF_VAR_name)

# Example usage:
terraform plan -var="environment=prod" -var-file="prod.tfvars"

# Environment variables
export TF_VAR_region="us-west-2"
export TF_VAR_instance_count=5
```

### 2. Environment Configuration

**Separate tfvars per environment:**
```hcl
# environments/dev/terraform.tfvars
environment      = "dev"
instance_type    = "t3.small"
instance_count   = 1
enable_monitoring = false

# environments/prod/terraform.tfvars
environment      = "prod"
instance_type    = "m5.large"
instance_count   = 3
enable_monitoring = true
enable_backups   = true
```

### 3. Terragrunt for DRY Configuration

```hcl
# terragrunt.hcl (root)
remote_state {
  backend = "s3"
  config = {
    bucket         = "company-terraform-state"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# environments/prod/vpc/terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../modules/vpc"
}

inputs = {
  environment = "prod"
  cidr_block  = "10.0.0.0/16"
}

# Benefits: DRY backend config, dependency management,
# automatic remote state handling
```

## Security Best Practices

### 1. Sensitive Variable Management

```hcl
variable "database_password" {
  description = "Database master password"
  type        = string
  sensitive   = true  # Prevents output in logs
}

# Use external secret management
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/db/password"
}

resource "aws_db_instance" "main" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string

  # Never hardcode secrets in code
  # Use AWS Secrets Manager, HashiCorp Vault, etc.
}
```

### 2. State Encryption

```hcl
# Enable encryption in backend configuration
terraform {
  backend "s3" {
    encrypt = true  # Client-side encryption
    kms_key_id = "arn:aws:kms:region:account:key/id"
  }
}

# S3 bucket encryption at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.terraform.arn
    }
    bucket_key_enabled = true
  }
}
```

### 3. IAM and Access Control

```hcl
# Principle of least privilege for Terraform execution
data "aws_iam_policy_document" "terraform_execution" {
  statement {
    actions = [
      "ec2:*",
      "s3:*",
      "rds:*"
    ]
    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = ["us-east-1", "us-west-2"]
    }
  }
}

# Separate IAM roles for different environments
# terraform-dev, terraform-staging, terraform-prod
```

### 4. Security Scanning

```bash
# tfsec - Static analysis security scanner
tfsec .

# Checkov - Policy-as-code scanner
checkov -d .

# Terrascan - Compliance and security scanner
terrascan scan

# Integrate in CI/CD pipeline
# Fail builds on critical security issues
```

### 5. Resource Tagging

```hcl
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = var.project_name
    Owner       = var.team_email
    CostCenter  = var.cost_center
  }
}

resource "aws_instance" "example" {
  ami           = var.ami_id
  instance_type = var.instance_type

  tags = merge(
    local.common_tags,
    {
      Name = "${var.environment}-web-server"
      Role = "web"
    }
  )
}

# Enables cost tracking, ownership, compliance
```

## Testing & Validation

### 1. Pre-Commit Validation

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

### 2. Terraform Validate & Plan

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

### 3. Automated Testing with Terratest

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

### 4. Policy as Code

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

## Best Practices Summary

### Code Organization
1. **Modular design**: Break code into reusable modules
2. **Consistent structure**: Follow standard file layouts
3. **Clear naming**: Use descriptive resource and variable names
4. **DRY principles**: Avoid duplication with modules and locals

### State Management
1. **Remote backends**: Always use remote state for teams
2. **State encryption**: Enable encryption at rest and in transit
3. **State locking**: Prevent concurrent modifications
4. **Backup strategy**: Enable versioning on state storage

### Security
1. **Sensitive data**: Use secret management, never hardcode
2. **IAM policies**: Principle of least privilege
3. **Security scanning**: Integrate tools in CI/CD
4. **Resource tagging**: Enable tracking and compliance

### Quality & Testing
1. **Validation**: Run terraform validate in CI/CD
2. **Static analysis**: Use tfsec, checkov, terrascan
3. **Automated tests**: Write Terratest for critical modules
4. **Code review**: Peer review all infrastructure changes

### Deployment
1. **Plan before apply**: Always review execution plans
2. **Incremental changes**: Small, frequent updates over large batches
3. **Rollback strategy**: Maintain previous state versions
4. **Change tracking**: Git history for all infrastructure code

### Documentation
1. **README files**: Document module usage with examples
2. **Variable descriptions**: Clear, comprehensive descriptions
3. **Output documentation**: Explain output values and usage
4. **Architecture diagrams**: Visual representation of infrastructure

### Version Management
1. **Provider constraints**: Pin major versions, allow minor updates
2. **Module versions**: Use semantic versioning for modules
3. **Terraform version**: Specify minimum required version
4. **Dependency locking**: Commit .terraform.lock.hcl

### Performance
1. **Resource parallelism**: Use -parallelism flag for large infrastructures
2. **Targeted operations**: Use -target for specific resources when needed
3. **State optimization**: Keep state size manageable, split large projects
4. **Provider caching**: Use plugin cache directory

## Resources

- **Official Docs**: https://developer.hashicorp.com/terraform/docs
- **Style Guide**: https://developer.hashicorp.com/terraform/language/syntax/style
- **Module Registry**: https://registry.terraform.io/
- **Terragrunt**: https://terragrunt.gruntwork.io/
- **Terratest**: https://terratest.gruntwork.io/
- **tfsec**: https://aquasecurity.github.io/tfsec/
- **Checkov**: https://www.checkov.io/
- **Best Practices**: https://www.terraform-best-practices.com/
- **AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
