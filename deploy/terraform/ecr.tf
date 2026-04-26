# ─────────────────────────────────────────────────────────────────────────
# ECR: imagem da app (build no GitHub Actions, pull na EC2).
# ─────────────────────────────────────────────────────────────────────────
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}/web"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# GitHub Actions: push (e cache de build) para o repositório.
data "aws_iam_policy_document" "gha_ecr_push" {
  statement {
    sid    = "EcrGetToken"
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
    ]
    resources = ["*"]
  }
  statement {
    sid    = "EcrPush"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]
    resources = [aws_ecr_repository.app.arn]
  }
}

resource "aws_iam_policy" "gha_ecr_push" {
  name   = "${var.project_name}-${var.environment}-gha-ecr-push"
  policy = data.aws_iam_policy_document.gha_ecr_push.json
}

resource "aws_iam_role_policy_attachment" "gha_ecr_push" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.gha_ecr_push.arn
}

# EC2: pull de imagem para deploy.
data "aws_iam_policy_document" "ec2_ecr_pull" {
  statement {
    sid    = "EcrGetToken"
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
    ]
    resources = ["*"]
  }
  statement {
    sid    = "EcrPull"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]
    resources = [aws_ecr_repository.app.arn]
  }
}

resource "aws_iam_policy" "ec2_ecr_pull" {
  name   = "${var.project_name}-${var.environment}-ec2-ecr-pull"
  policy = data.aws_iam_policy_document.ec2_ecr_pull.json
}

resource "aws_iam_role_policy_attachment" "ec2_ecr_pull" {
  role       = aws_iam_role.ec2.name
  policy_arn = aws_iam_policy.ec2_ecr_pull.arn
}
