output "ec2_public_ip" {
  description = "IP público fixo (EIP) da instância."
  value       = aws_eip.app.public_ip
}

output "ec2_instance_id" {
  description = "ID da EC2."
  value       = aws_instance.app.id
}

output "ec2_instance_arn" {
  description = "ARN da EC2 (usado pelo SSM SendCommand a partir do GitHub)."
  value       = aws_instance.app.arn
}

output "backup_bucket" {
  description = "Bucket S3 onde a instância faz upload de backups."
  value       = aws_s3_bucket.backups.bucket
}

output "github_actions_role_arn" {
  description = "ARN da IAM role assumida pelo workflow do GitHub via OIDC."
  value       = aws_iam_role.github_actions.arn
}

output "ecr_repository_url" {
  description = "URL do repositório ECR (sem tag). Defina no GitHub como ECR_REPOSITORY."
  value       = aws_ecr_repository.app.repository_url
}

output "ssh_command_hint" {
  description = "Comando de exemplo para acessar a instância via SSH (operador autorizado)."
  value       = "ssh -i <sua-chave> deploy@${aws_eip.app.public_ip}"
}
