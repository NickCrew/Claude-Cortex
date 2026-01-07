# Workspace & Environment Management

## 1. Variable Precedence

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

## 2. Environment Configuration

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

## 3. Terragrunt for DRY Configuration

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
