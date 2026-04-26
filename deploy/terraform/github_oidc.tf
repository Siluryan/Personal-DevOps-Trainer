# ─────────────────────────────────────────────────────────────────────────
# OIDC do GitHub Actions: dispensa secret AWS de longa duração no repositório.
# Cria provider e a IAM role que o workflow assume durante o deploy.
# ─────────────────────────────────────────────────────────────────────────
data "tls_certificate" "github" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.github.certificates[0].sha1_fingerprint]
}

data "aws_iam_policy_document" "gha_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = [for ref in var.github_default_branches : "repo:${var.github_repo}:ref:${ref}"]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "${var.project_name}-${var.environment}-gha-deploy"
  assume_role_policy = data.aws_iam_policy_document.gha_assume.json
}

# Permissões mínimas para o pipeline:
#  - Disparar SSM SendCommand na EC2 alvo (deploy)
#  - Acompanhar a invocação
#  - Ler outputs do Terraform via state remoto (não precisa, é via S3 do TF)
data "aws_iam_policy_document" "gha_deploy" {
  # Operações de leitura: necessárias para o workflow consultar status das
  # invocações e descobrir a instância pela tag.
  statement {
    sid = "SsmReadAndDescribe"
    actions = [
      "ssm:ListCommandInvocations",
      "ssm:ListCommands",
      "ssm:GetCommandInvocation",
      "ssm:DescribeInstanceInformation",
      "ec2:DescribeInstances",
      "ec2:DescribeTags",
    ]
    resources = ["*"]
  }

  # SendCommand: restrito a este AWS-RunShellScript específico…
  statement {
    sid       = "SsmSendCommandDocument"
    actions   = ["ssm:SendCommand"]
    resources = ["arn:aws:ssm:${var.aws_region}::document/AWS-RunShellScript"]
  }

  # …e à instância exata da app. Os dois statements casam em conjunto.
  statement {
    sid       = "SsmSendCommandTargetInstance"
    actions   = ["ssm:SendCommand"]
    resources = [aws_instance.app.arn]
  }
}

resource "aws_iam_policy" "gha_deploy" {
  name   = "${var.project_name}-${var.environment}-gha-deploy"
  policy = data.aws_iam_policy_document.gha_deploy.json
}

resource "aws_iam_role_policy_attachment" "gha_deploy" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.gha_deploy.arn
}

# Política adicional para o workflow `terraform.yml` planejar/aplicar:
#   atribua manualmente, ou refine. Por padrão criamos só com permissões de
#   deploy. Para o pipeline de Terraform, recomenda-se uma role separada
#   com permissões mais amplas (não criada aqui para reduzir blast radius).
