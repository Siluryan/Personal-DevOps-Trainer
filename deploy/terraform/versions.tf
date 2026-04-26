terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }

  # State remoto recomendado. Crie o bucket/tabela uma única vez (bootstrap)
  # antes do primeiro `terraform init`, ou comente este bloco para usar
  # state local até criar o bucket.
  backend "s3" {
    bucket         = "REPLACE-ME-tfstate-bucket"
    key            = "pdt/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "REPLACE-ME-tfstate-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = var.owner
    }
  }
}
