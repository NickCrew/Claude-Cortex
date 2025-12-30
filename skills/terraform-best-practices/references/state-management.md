# State Management Best Practices

## 1. Remote Backend Configuration

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

## 2. State File Security

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

## 3. State Operations

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

## 4. Workspace Strategies

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
