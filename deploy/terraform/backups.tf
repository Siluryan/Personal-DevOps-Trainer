resource "random_id" "bucket_suffix" {
  byte_length = 4
}

locals {
  backup_bucket_name = (
    var.backup_bucket_name_override != ""
    ? var.backup_bucket_name_override
    : "${var.project_name}-${var.environment}-backups-${random_id.bucket_suffix.hex}"
  )
}

resource "aws_s3_bucket" "backups" {
  bucket        = local.backup_bucket_name
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket                  = aws_s3_bucket.backups.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  versioning_configuration {
    # Objetos são únicos por timestamp; versioning só aumenta custo sem benefício.
    status = "Suspended"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "expire-old"
    status = "Enabled"

    filter {}

    # Retenção curta em Standard: mais barato que Glacier IR para dumps pequenos
    # (~500 KiB/dia) — evita taxa mínima por objeto e custo de transição.
    expiration {
      days = var.backup_retention_days
    }
  }
}

# Nome do bucket lido no runtime (p.ex. `deploy-from-ecr.sh` reconstrui /opt/pdt/pdt.env).
resource "aws_ssm_parameter" "backup_bucket" {
  name  = "/${var.project_name}/${var.environment}/backup_bucket"
  type  = "String"
  value = aws_s3_bucket.backups.bucket
}
