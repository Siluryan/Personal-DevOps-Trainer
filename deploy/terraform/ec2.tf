# Ubuntu Server 24.04 LTS (Noble) — Canonical, x86_64.
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "random_password" "django_secret" {
  length  = 64
  special = false
}

resource "random_password" "postgres" {
  length  = 32
  special = false
}

# Os secrets ficam em SSM Parameter Store (cifrados com KMS aws/ssm).
# A EC2 lê via cloud-init, evitando deixá-los em plaintext no user_data.
resource "aws_ssm_parameter" "django_secret" {
  name  = "/${var.project_name}/${var.environment}/django/secret_key"
  type  = "SecureString"
  value = random_password.django_secret.result
}

resource "aws_ssm_parameter" "postgres_password" {
  name  = "/${var.project_name}/${var.environment}/postgres/password"
  type  = "SecureString"
  value = random_password.postgres.result
}

resource "aws_ssm_parameter" "domain_name" {
  name  = "/${var.project_name}/${var.environment}/domain_name"
  type  = "String"
  value = var.domain_name
}

# A EC2 precisa poder ler esses parâmetros (chave KMS aws/ssm é gerenciada).
data "aws_iam_policy_document" "ssm_params_read" {
  statement {
    actions = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
    resources = [
      aws_ssm_parameter.django_secret.arn,
      aws_ssm_parameter.postgres_password.arn,
      aws_ssm_parameter.domain_name.arn,
    ]
  }
}

resource "aws_iam_policy" "ssm_params_read" {
  name   = "${var.project_name}-${var.environment}-ssm-params-read"
  policy = data.aws_iam_policy_document.ssm_params_read.json
}

resource "aws_iam_role_policy_attachment" "ssm_params_read" {
  role       = aws_iam_role.ec2.name
  policy_arn = aws_iam_policy.ssm_params_read.arn
}

# Chave SSH só é importada se foi fornecida; quem não fornecer usa SSM Session Manager.
resource "aws_key_pair" "deploy" {
  count      = var.ssh_public_key != "" ? 1 : 0
  key_name   = "${var.project_name}-${var.environment}-deploy"
  public_key = var.ssh_public_key
}

locals {
  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    project_name      = var.project_name
    environment       = var.environment
    aws_region        = var.aws_region
    domain_name       = var.domain_name
    letsencrypt_email = var.letsencrypt_email
    github_repo       = var.github_repo
    backup_bucket     = aws_s3_bucket.backups.bucket
    ssm_django_secret = aws_ssm_parameter.django_secret.name
    ssm_postgres_pwd  = aws_ssm_parameter.postgres_password.name
  })
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.app.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2.name
  associate_public_ip_address = true
  key_name                    = var.ssh_public_key != "" ? aws_key_pair.deploy[0].key_name : null
  user_data                   = local.user_data
  user_data_replace_on_change = false

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required" # IMDSv2 obrigatório
    http_put_response_hop_limit = 2
  }

  monitoring = true # detailed monitoring (1 min)

  root_block_device {
    volume_size           = var.ebs_root_size_gb
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = false
    tags = {
      Name = "${var.project_name}-${var.environment}-root"
    }
  }

  lifecycle {
    ignore_changes = [
      ami,
      user_data, # user_data muda ao editar template; recriaria a EC2.
    ]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
    PatchGroup  = "${var.project_name}-${var.environment}"
  }
}

resource "aws_eip" "app" {
  domain   = "vpc"
  instance = aws_instance.app.id
  tags     = { Name = "${var.project_name}-${var.environment}-eip" }
}
