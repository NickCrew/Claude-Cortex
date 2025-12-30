# Security Best Practices

## 1. Sensitive Variable Management

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

## 2. State Encryption

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

## 3. IAM and Access Control

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

## 4. Security Scanning

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

## 5. Resource Tagging

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
