# Deploy do PDT na AWS (t3.micro) — Terraform + GitHub Actions

Este diretório provisiona uma instância t3.micro Ubuntu 24.04 LTS na AWS,
roda o stack Django + Channels + nginx + Postgres + Redis, emite TLS via
Let's Encrypt (com renovação automática), aplica patches semanais via SSM
Patch Manager, faz backups diários para o S3 e expõe deploy contínuo via
GitHub Actions usando OIDC (sem chave AWS de longa duração no repo).

```
deploy/
├── terraform/                # IaC (VPC, EC2, IAM, S3, SSM)
│   ├── versions.tf
│   ├── variables.tf
│   ├── networking.tf
│   ├── security_groups (em networking.tf)
│   ├── iam.tf
│   ├── github_oidc.tf
│   ├── ec2.tf
│   ├── backups.tf
│   ├── ssm_patching.tf
│   ├── user_data.sh.tpl      # bootstrap + hardening
│   └── terraform.tfvars.example
└── server/
    ├── nginx/
    │   ├── pdt.conf.tpl
    │   └── snippets/pdt_proxy.conf
    ├── systemd/
    │   └── pdt-daphne.service
    └── scripts/
        ├── deploy.sh         # chamado pelo SSM SendCommand do GHA
        ├── backup.sh         # chamado por SSM Association diário
        └── healthcheck.sh
```

## Topologia

```
Internet ── 80/443 ── nginx ──┬── /static/  → /opt/pdt/app/pdt/staticfiles/
                              ├── /media/   → /opt/pdt/app/pdt/media/
                              ├── /ws/      → daphne 127.0.0.1:8000 (WebSocket)
                              └── /        → daphne 127.0.0.1:8000 (HTTP)

EC2 (t3.micro)
├── postgres 16 (local, 30 conexões, 128MB shared_buffers)
├── redis 7    (bind 127.0.0.1, 96MB maxmemory)
├── daphne     (systemd, ASGI)
├── nginx      (TLS via Let's Encrypt + HSTS)
├── certbot    (renew via systemd timer)
├── ufw        (22 op, 80/443 mundo, deny all)
├── fail2ban   (sshd, nginx-bad-request, nginx-botsearch)
├── auditd     (regras /etc/passwd, sudoers, sshd_config, /opt/pdt)
└── unattended-upgrades + AWS SSM Patch Manager (defesa em profundidade)
```

## Pré-requisitos

1. Conta AWS, com permissão para o `terraform apply` (recomendado: usuário/role
   admin separado, fora do CI).
2. Bucket + tabela DynamoDB para o state remoto (substitua os valores em
   `versions.tf` antes do primeiro `init`).
3. Domínio público (`vars.PDT_DOMAIN_NAME`) com um A record apontando para o
   EIP (output `ec2_public_ip`). É possível criar a EC2 antes do DNS apontar:
   nesse caso o certbot inicial vai falhar e você reexecuta `certbot --nginx`
   manualmente após o DNS propagar.
4. Repositório no GitHub com permissão para criar OIDC role.

## Bootstrap inicial

```bash
cd deploy/terraform
cp terraform.tfvars.example terraform.tfvars
# edite terraform.tfvars (domínio, e-mail, github_repo)

terraform init
terraform apply
```

Saídas relevantes:

- `ec2_public_ip` — apontar o A record do domínio.
- `github_actions_role_arn` — usar como secret `GHA_DEPLOY_ROLE_ARN` no repo.
- `backup_bucket` — onde os dumps do Postgres e tar.gz de media param.

Após o DNS propagar, conecte via SSM Session Manager e rode:

```bash
sudo certbot --nginx -d pdt.exemplo.com --non-interactive --agree-tos -m ops@exemplo.com --redirect
```

## Variáveis no GitHub

Em `Settings → Secrets and variables → Actions` do repositório, configure:

### Secrets
| nome                    | usado em       | descrição                                |
| ----------------------- | -------------- | ---------------------------------------- |
| `GHA_DEPLOY_ROLE_ARN`   | `deploy.yml`   | Role do OIDC (output `github_actions_role_arn`). |
| `TF_AWS_ROLE_ARN`       | `terraform.yml`| Role com permissão de Terraform (NÃO criada por este código; provisione manualmente com permissões só ao que o TF maneja). |

### Variables
| nome                  | descrição                                              |
| --------------------- | ------------------------------------------------------ |
| `PDT_DOMAIN_NAME`     | Mesmo domínio que está no `terraform.tfvars`.          |
| `LETSENCRYPT_EMAIL`   | E-mail de notificação do Let's Encrypt.                |
| `PDT_SSH_PUBLIC_KEY`  | Chave OpenSSH (opcional; vazio = só Session Manager).  |
| `PDT_OPERATOR_CIDRS`  | JSON `["1.2.3.4/32"]` (opcional).                      |

## Renovação de certificados

O pacote `certbot` instalado pelo `user_data` cria o timer
`certbot.timer` (e `snap.certbot.renew.timer` quando aplicável). O timer
roda 2× ao dia e renova certificados que estão a 30 dias do vencimento.
Após renovar, o hook `--deploy-hook` recarrega o nginx (já configurado pelo
`certbot --nginx` na primeira emissão).

Você pode forçar manualmente:

```bash
sudo certbot renew --dry-run
sudo systemctl list-timers certbot.timer
```

## Patches agendados

Dois mecanismos rodam em paralelo:

1. **`unattended-upgrades`** (no SO): aplica security updates diariamente,
   com reboot às 04:30 UTC se algum pacote pediu.
2. **AWS SSM Patch Manager**: scan diário (cron 06:00 UTC) +
   Maintenance Window de instalação semanal (`patch_window_cron`,
   default domingo 04:00 UTC) com `RebootIfNeeded`.

Se você usar Patch Manager apenas, comente o bloco de
`unattended-upgrades` no `user_data.sh.tpl`.

## Backups

`SSM Association` `pdt-prod-backup` roda às 05:00 UTC todo dia, executando
`/opt/pdt/scripts/backup.sh`. Sobe para o bucket `aws_s3_bucket.backups`:

- `db/pdt_<TS>.dump` — formato custom do `pg_dump` (restore com `pg_restore`).
- `media/media_<TS>.tar.gz` — tarball do diretório `media/`.

Lifecycle do bucket move objetos para Glacier IR depois de 30 dias e
expira após `backup_retention_days * 12`. Ajuste em `backups.tf`.

## Hardening aplicado

| área              | medida |
| ----------------- | ------ |
| **SSH**           | sem root, sem senha, sem X11/agent/TCP forwarding, MaxAuthTries=3, banner |
| **Firewall**      | UFW deny in/allow out + SG (defesa em profundidade) |
| **Brute-force**   | fail2ban com jails sshd/nginx (logs via systemd) |
| **Kernel**        | sysctl: rp_filter, syncookies, ptrace_scope=2, kptr_restrict, dmesg_restrict, BPF não-privilegiado off, randomize_va_space=2 |
| **Filesystem**    | protected_{hardlinks,symlinks,fifos,regular}, suid_dumpable=0, EBS gp3 + KMS |
| **AppArmor**      | habilitado por padrão no Ubuntu 24.04 (perfis nginx/postgres ativos) |
| **Auditd**        | regras /etc/passwd, /etc/shadow, /etc/sudoers, /etc/ssh/sshd_config, /opt/pdt |
| **Patches**       | unattended-upgrades (auto-reboot 04:30) + SSM Patch Manager semanal |
| **App**           | Daphne em systemd com NoNewPrivileges, ProtectSystem=strict, PrivateTmp, MemoryDenyWriteExecute, SystemCallFilter |
| **TLS**           | TLSv1.2/1.3, HSTS 1y, OCSP stapling, ciphers GCM apenas |
| **HTTP**          | X-Frame-Options DENY, nosniff, Referrer-Policy, Permissions-Policy |
| **IMDS**          | v2 obrigatório, hop limit 2 |
| **Secrets**       | Postgres + Django SECRET_KEY em SSM Parameter Store (SecureString) |
| **EBS**           | criptografia em repouso (KMS aws/ebs) |
| **S3 backups**    | Versioning + SSE-AES256 + Public Access Block + Lifecycle |
| **Acesso**        | preferir SSM Session Manager (não exige porta 22 aberta) |

## CI / CD

| workflow         | trigger                                | função |
| ---------------- | -------------------------------------- | ------ |
| `ci.yml`         | push/PR                                | pytest + tf fmt/validate |
| `terraform.yml`  | PR/push em `deploy/terraform/**`       | plan em PR (comenta), apply em push (env `prod`) |
| `deploy.yml`     | push em `main` (fora de `deploy/terraform`) | OIDC → `aws ssm send-command` → `/opt/pdt/scripts/deploy.sh` → smoke test |

## Custo aproximado (us-east-1, 2026)

| recurso        | preço/mês (USD) |
| -------------- | --------------- |
| t3.micro       | ~7.50 (free tier 1º ano: $0) |
| EBS gp3 20GB   | ~1.60 |
| EIP em uso     | $0 |
| S3 (poucos MB) | <$1 |
| Data transfer  | varia (100GB grátis no free tier) |

Total típico: **$10–15/mês** após o free tier.
