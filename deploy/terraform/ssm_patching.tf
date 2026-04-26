# ─────────────────────────────────────────────────────────────────────────
# Patch Manager: aplica updates de segurança automaticamente toda semana.
# Linha de defesa adicional ao unattended-upgrades configurado no user_data.
# ─────────────────────────────────────────────────────────────────────────

resource "aws_ssm_patch_baseline" "ubuntu" {
  name             = "${var.project_name}-${var.environment}-baseline"
  description      = "Baseline Ubuntu: aprova patches Security/Critical/Important."
  operating_system = "UBUNTU"

  approval_rule {
    approve_after_days  = 0
    compliance_level    = "CRITICAL"
    enable_non_security = false

    patch_filter {
      key    = "PRIORITY"
      values = ["Required", "Important", "Standard"]
    }

    patch_filter {
      key    = "SECTION"
      values = ["*"]
    }
  }
}

resource "aws_ssm_patch_group" "this" {
  baseline_id = aws_ssm_patch_baseline.ubuntu.id
  patch_group = "${var.project_name}-${var.environment}"
}

resource "aws_ssm_maintenance_window" "patch" {
  name                       = "${var.project_name}-${var.environment}-patch-window"
  description                = "Janela semanal de aplicação de patches."
  schedule                   = var.patch_window_cron
  duration                   = 2
  cutoff                     = 1
  schedule_timezone          = "UTC"
  allow_unassociated_targets = false
}

resource "aws_ssm_maintenance_window_target" "patch" {
  window_id     = aws_ssm_maintenance_window.patch.id
  name          = "${var.project_name}-${var.environment}-targets"
  resource_type = "INSTANCE"

  targets {
    key    = "tag:PatchGroup"
    values = ["${var.project_name}-${var.environment}"]
  }
}

resource "aws_ssm_maintenance_window_task" "patch_install" {
  name             = "${var.project_name}-${var.environment}-patch-install"
  window_id        = aws_ssm_maintenance_window.patch.id
  task_type        = "RUN_COMMAND"
  task_arn         = "AWS-RunPatchBaseline"
  service_role_arn = aws_iam_role.ssm_maintenance.arn
  priority         = 1
  max_concurrency  = "1"
  max_errors       = "0"

  targets {
    key    = "WindowTargetIds"
    values = [aws_ssm_maintenance_window_target.patch.id]
  }

  task_invocation_parameters {
    run_command_parameters {
      timeout_seconds = 3600

      parameter {
        name   = "Operation"
        values = ["Install"]
      }
      parameter {
        name   = "RebootOption"
        values = ["RebootIfNeeded"]
      }
    }
  }
}

# Compliance/scan diário, fora da janela: avisa se a instância ficou
# defasada antes do próximo install agendado.
resource "aws_ssm_association" "scan_daily" {
  name                = "AWS-RunPatchBaseline"
  association_name    = "${var.project_name}-${var.environment}-scan"
  schedule_expression = "cron(0 6 * * ? *)"

  targets {
    key    = "tag:PatchGroup"
    values = ["${var.project_name}-${var.environment}"]
  }

  parameters = {
    Operation = "Scan"
  }
}

# ─────────────────────────────────────────────────────────────────────────
# Backup diário: roda /opt/pdt/scripts/backup.sh via SSM cron
# ─────────────────────────────────────────────────────────────────────────
resource "aws_ssm_association" "backup_daily" {
  name                = "AWS-RunShellScript"
  association_name    = "${var.project_name}-${var.environment}-backup"
  schedule_expression = "cron(0 5 * * ? *)" # 05:00 UTC = 02:00 BRT

  targets {
    key    = "InstanceIds"
    values = [aws_instance.app.id]
  }

  parameters = {
    commands = "/opt/pdt/scripts/backup.sh || logger -t pdt-backup 'falhou'"
  }
}
