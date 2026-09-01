---
name: infrastructure-as-code
description: Infrastructure as Code with Terraform, Pulumi, and Ansible. Use when the user asks about provisioning cloud infrastructure, writing Terraform configs, managing infrastructure state, or automating server configuration.
---

# Infrastructure as Code

## Terraform Basics

### Provider Configuration
```hcl
# main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "my-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}
```

### Variables and Outputs
```hcl
# variables.tf
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

# outputs.tf
output "instance_ip" {
  value = aws_instance.web.public_ip
}

output "db_endpoint" {
  value = aws_db_instance.main.endpoint
}
```

### EC2 Instance
```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = var.instance_type
  
  tags = {
    Name        = "web-server"
    Environment = var.environment
  }

  vpc_security_group_ids = [aws_security_group.web.id]
  subnet_id              = aws_subnet.public.id
}
```

### VPC
```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "main-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}
```

### Security Group
```hcl
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### RDS Database
```hcl
resource "aws_db_instance" "main" {
  identifier     = "myapp-db"
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100

  db_name  = "myapp"
  username = var.db_username
  password = var.db_password

  backup_retention_period = 7
  multi_az               = true
  storage_encrypted      = true

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
}
```

## Modules

```hcl
# modules/ecs-service/main.tf
variable "name" {}
variable "image" {}
variable "port" {}
variable "cpu" {}
variable "memory" {}

resource "aws_ecs_service" "this" {
  name            = var.name
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = 2

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = var.name
    container_port   = var.port
  }
}

output "service_name" {
  value = aws_ecs_service.this.name
}

# Usage
module "api_service" {
  source = "./modules/ecs-service"
  
  name            = "api"
  image           = "123456.dkr.ecr.us-east-1.amazonaws.com/api:latest"
  port            = 3000
  cpu             = 256
  memory          = 512
  cluster_id      = aws_ecs_cluster.main.id
  target_group_arn = aws_lb_target_group.api.arn
}
```

## Workspaces

```bash
# Create workspace for environment
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch workspace
terraform workspace select dev

# List workspaces
terraform workspace list
```

## Terraform Commands

```bash
# Initialize
terraform init

# Plan changes
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan

# Destroy resources
terraform destroy

# Format code
terraform fmt -recursive

# Validate
terraform validate

# Show state
terraform show

# Import existing resource
terraform import aws_instance.web i-1234567890abcdef0
```

## Ansible Playbook

```yaml
# playbook.yml
---
- hosts: webservers
  become: yes
  vars:
    app_version: "1.2.3"
    app_port: 3000

  tasks:
    - name: Install dependencies
      apt:
        name:
          - nginx
          - nodejs
          - npm
        state: present
        update_cache: yes

    - name: Copy nginx config
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/sites-available/myapp
      notify: Restart nginx

    - name: Deploy application
      git:
        repo: https://github.com/myorg/myapp.git
        dest: /opt/myapp
        version: "v{{ app_version }}"
      notify: Restart app

    - name: Install npm dependencies
      npm:
        path: /opt/myapp
        state: present

    - name: Start application
      systemd:
        name: myapp
        state: started
        enabled: yes

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted

    - name: Restart app
      systemd:
        name: myapp
        state: restarted
```

## Best Practices

1. Store state remotely (S3 + DynamoDB locking)
2. Use workspaces for environments
3. Version your infrastructure code
4. Use modules for reusable components
5. Plan before applying
6. Tag all resources
7. Use variables for configurable values
8. Keep secrets out of code (use vault/KMS)
9. Implement drift detection
10. Document your infrastructure
