variable "project_name" {
  description = "Prefixo curto, vai em todo nome de recurso."
  type        = string
  default     = "pdt"
}

variable "environment" {
  description = "Nome do ambiente (prod, staging, dev)."
  type        = string
  default     = "prod"
}

variable "owner" {
  description = "Pessoa/squad responsável (vai em tag, útil pra cobrança)."
  type        = string
  default     = "platform"
}

variable "aws_region" {
  description = "Região AWS."
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR da VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR da única subnet pública (t3.micro mora aqui)."
  type        = string
  default     = "10.42.1.0/24"
}

variable "instance_type" {
  description = "Tipo da instância EC2."
  type        = string
  default     = "t3.micro"
}

variable "ebs_root_size_gb" {
  description = "Tamanho do disco raiz, GB."
  type        = number
  default     = 20
}

variable "domain_name" {
  description = "Domínio público que vai apontar para o EIP (ex.: pdt.exemplo.com)."
  type        = string
}

variable "letsencrypt_email" {
  description = "E-mail usado pelo certbot para o Let's Encrypt."
  type        = string
}

variable "operator_cidrs" {
  description = "Lista de CIDRs autorizados a abrir SSH na porta 22 (use seu IP /32)."
  type        = list(string)
  default     = []
}

variable "ssh_public_key" {
  description = "Chave SSH pública (string OpenSSH) instalada no usuário deploy."
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "Nome do repositório GitHub no formato owner/repo (usado para OIDC e deploy)."
  type        = string
}

variable "github_default_branches" {
  description = "Branches/refs cujo `sub` OIDC é `repo:...:ref:...` (workflows sem GitHub Environment)."
  type        = list(string)
  default     = ["refs/heads/main"]
}

variable "github_deployment_environments" {
  description = <<-EOT
    Nomes de GitHub Environments (bloco `environment: X` no workflow). O claim
    `sub` nesses casos é `repo:owner/repo:environment:nome` — não o mesmo que
    `ref:refs/heads/...`, por isso a role deve listar estes nomes.
  EOT
  type        = list(string)
  default     = ["prod"]
}

variable "patch_window_cron" {
  description = "Janela semanal de patching (cron AWS). Padrão: domingo 04:00 UTC."
  type        = string
  default     = "cron(0 4 ? * SUN *)"
}

variable "backup_bucket_name_override" {
  description = "Sobrescreve o nome do bucket de backup. Vazio = nome gerado."
  type        = string
  default     = ""
}

variable "backup_retention_days" {
  description = "Dias de retenção dos backups antes do glacier/expiração."
  type        = number
  default     = 30
}
