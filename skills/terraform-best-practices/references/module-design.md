# Module Design Patterns

## 1. Module Structure

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

## 2. Composition over Monoliths

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

## 3. Variable Design

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

## 4. Output Organization

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

## 5. Dynamic Blocks for Flexibility

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
