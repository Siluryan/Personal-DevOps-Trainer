data "aws_caller_identity" "current" {}

# ─────────────────────────────────────────────────────────────────────────
# IAM da EC2: SSM (Session Manager + Patch) + acesso ao bucket de backup
# ─────────────────────────────────────────────────────────────────────────
data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2" {
  name               = "${var.project_name}-${var.environment}-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
}

resource "aws_iam_role_policy_attachment" "ssm_managed" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ssm_patch" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMPatchAssociation"
}

resource "aws_iam_role_policy_attachment" "cw_agent" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

data "aws_iam_policy_document" "backup_rw" {
  statement {
    actions = ["s3:ListBucket", "s3:GetBucketLocation"]
    resources = [aws_s3_bucket.backups.arn]
  }
  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject",
      "s3:AbortMultipartUpload",
    ]
    resources = ["${aws_s3_bucket.backups.arn}/*"]
  }
}

resource "aws_iam_policy" "backup_rw" {
  name        = "${var.project_name}-${var.environment}-backup-rw"
  description = "EC2 grava backups no S3."
  policy      = data.aws_iam_policy_document.backup_rw.json
}

resource "aws_iam_role_policy_attachment" "backup_rw" {
  role       = aws_iam_role.ec2.name
  policy_arn = aws_iam_policy.backup_rw.arn
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project_name}-${var.environment}-ec2-profile"
  role = aws_iam_role.ec2.name
}

# ─────────────────────────────────────────────────────────────────────────
# IAM Role para Maintenance Window (SSM)
# ─────────────────────────────────────────────────────────────────────────
data "aws_iam_policy_document" "ssm_mw_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ssm_maintenance" {
  name               = "${var.project_name}-${var.environment}-ssm-mw-role"
  assume_role_policy = data.aws_iam_policy_document.ssm_mw_assume.json
}

resource "aws_iam_role_policy_attachment" "ssm_maintenance" {
  role       = aws_iam_role.ssm_maintenance.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonSSMMaintenanceWindowRole"
}
