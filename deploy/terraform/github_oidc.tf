# ─────────────────────────────────────────────────────────────────────────
# OIDC do GitHub Actions: o provider na conta (URL token.actions... ) costuma
# já existir; referenciamos o existente em vez de criar outro (409).
# data.aws_caller_identity.current em iam.tf.
# ─────────────────────────────────────────────────────────────────────────
data "aws_iam_openid_connect_provider" "github" {
  arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"
}

# O `sub` do GitHub OIDC varia consoante o job use ou não `environment:`
#   - com environment:  repo:org/repo:environment:prod
#   - sem environment:  repo:org/repo:ref:refs/heads/main
# Os dois têm de estar na trust policy se usares os dois padrões.
# Ver: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services#configuring-the-role-and-trust-policy
locals {
  github_actions_oidc_subjects = concat(
    [for ref in var.github_default_branches : "repo:${var.github_repo}:ref:${ref}"],
    [for env in var.github_deployment_environments : "repo:${var.github_repo}:environment:${env}"],
  )
}

data "aws_iam_policy_document" "gha_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = local.github_actions_oidc_subjects
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
