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
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "expire-old"
    status = "Enabled"

    filter {}

    transition {
      days          = 30
      storage_class = "GLACIER_IR"
    }

    expiration {
      days = var.backup_retention_days * 12
    }

    noncurrent_version_expiration {
      noncurrent_days = var.backup_retention_days
    }
  }
}

# Nome do bucket lido no runtime (p.ex. `deploy-from-ecr.sh` reconstrui /opt/pdt/pdt.env).
resource "aws_ssm_parameter" "backup_bucket" {
  name  = "/${var.project_name}/${var.environment}/backup_bucket"
  type  = "String"
  value = aws_s3_bucket.backups.bucket
}
