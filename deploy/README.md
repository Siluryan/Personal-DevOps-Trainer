# Deploy do PDT na AWS (t4g.nano, ARM64) — Terraform + GitHub Actions

Este diretório provisiona uma instância t4g.nano (ARM64/Graviton) Ubuntu 24.04 LTS na AWS,
roda o stack Django + Channels + nginx + Postgres + Redis, expõe a aplicação via
**Cloudflare Tunnel** (sem EIP nem portas 80/443 públicas na origem), aplica patches
semanais via SSM Patch Manager, faz backups diários para o S3 e expõe deploy contínuo via
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
    │   ├── pdt-daphne.service
    │   └── cloudflared.service
    └── scripts/
        ├── deploy.sh         # chamado pelo SSM SendCommand do GHA
        ├── backup.sh         # chamado por SSM Association diário
        └── healthcheck.sh
```

## Topologia

```
Internet ── HTTPS ── Cloudflare (TLS + proxy) ── cloudflared (outbound) ── nginx 127.0.0.1:8080
                                                      ├── /static/  → /opt/pdt/app/pdt/staticfiles/
                                                      ├── /media/   → /opt/pdt/app/pdt/media/
                                                      ├── /ws/      → daphne 127.0.0.1:8000 (WebSocket)
                                                      └── /        → daphne 127.0.0.1:8000 (HTTP)

EC2 (t4g.nano, ARM64) — sem EIP, sem 80/443 públicos
├── postgres 16 (local, 30 conexões, 128MB shared_buffers)
├── redis 7    (bind 127.0.0.1, 96MB maxmemory)
├── docker     (app arm64 via ECR, network_mode: host)
├── nginx      (HTTP localhost:8080, proxy para daphne)
├── cloudflared (tunnel outbound para Cloudflare)
├── ufw        (22 opcional, deny all inbound restante)
├── fail2ban   (sshd)
├── auditd     (regras /etc/passwd, sudoers, sshd_config, /opt/pdt)
└── unattended-upgrades + AWS SSM Patch Manager (defesa em profundidade)
```

## Pré-requisitos

1. Conta AWS, com permissão para o `terraform apply` (recomendado: usuário/role
   admin separado, fora do CI).
2. Bucket + tabela DynamoDB para o state remoto (substitua os valores em
   `versions.tf` antes do primeiro `init`).
3. Domínio no **Cloudflare** (`vars.PDT_DOMAIN_NAME`) com DNS gerenciado lá.
4. **Cloudflare Tunnel** criado em Zero Trust → Networks → Tunnels (remotely-managed).
5. Repositório no GitHub com permissão para criar OIDC role.

## Cloudflare Tunnel (configuração)

1. Em [Cloudflare Zero Trust](https://one.dash.cloudflare.com/) → **Networks** → **Tunnels** → **Create a tunnel**.
2. Escolha **Cloudflared** e copie o **token** do connector.
3. Em **Public Hostname**, adicione rotas para o origin local:
   - `personaldevopstrainer.online` → `http://127.0.0.1:8080`
   - `www.personaldevopstrainer.online` → `http://127.0.0.1:8080`
4. Habilite **WebSockets** se o painel oferecer (necessário para `/ws/`).
5. No DNS da Cloudflare, remova o **A record** apontando para o EIP antigo.
   O tunnel cria/atualiza os registros automaticamente (CNAME para `*.cfargotunnel.com`).
6. Guarde o token:
   - GitHub secret `CLOUDFLARE_TUNNEL_TOKEN` (para `terraform.yml`), e/ou
   - `cloudflare_tunnel_token` em `terraform.tfvars`.

TLS termina na Cloudflare (modo **Full** ou **Full (strict)**). A origem fala HTTP
com nginx em localhost; não é necessário certbot/Let's Encrypt na EC2.

## Bootstrap inicial

```bash
cd deploy/terraform
cp terraform.tfvars.example terraform.tfvars
# edite terraform.tfvars (domínio, cloudflare_tunnel_token, github_repo)

terraform init
terraform apply
```

Saídas relevantes:

- `ec2_public_ip` — IP efêmero (outbound/SSM); tráfego web não passa por aqui.
- `cloudflare_tunnel_token_ssm` — parâmetro SSM onde o token fica armazenado.
- `github_actions_role_arn` — usar como secret `GHA_DEPLOY_ROLE_ARN` no repo.
- `backup_bucket` — onde os dumps do Postgres e tar.gz de media param.

Após o apply, dispare um deploy (`push` na main ou workflow manual) para
instalar/atualizar nginx localhost + cloudflared na instância existente.

## Variáveis no GitHub

Em `Settings → Secrets and variables → Actions` do repositório, configure:

### Secrets
| nome                       | usado em        | descrição                                |
| -------------------------- | --------------- | ---------------------------------------- |
| `GHA_DEPLOY_ROLE_ARN`      | `deploy.yml`    | Role do OIDC (output `github_actions_role_arn`). |
| `TF_AWS_ROLE_ARN`          | `terraform.yml` | Role com permissão de Terraform.         |
| `CLOUDFLARE_TUNNEL_TOKEN`  | `terraform.yml` | Token do Cloudflare Tunnel (remotely-managed). |

### Variables
| nome                  | descrição                                              |
| --------------------- | ------------------------------------------------------ |
| `PDT_DOMAIN_NAME`     | Domínio no Cloudflare (ex.: `personaldevopstrainer.online`). |
| `PDT_SSH_PUBLIC_KEY`  | Chave OpenSSH (opcional; vazio = só Session Manager).  |
| `PDT_OPERATOR_CIDRS`  | JSON `["1.2.3.4/32"]` (opcional).                      |

## Migração de EIP → Cloudflare Tunnel

Se você já tinha produção com EIP + Let's Encrypt:

1. Crie o tunnel e configure hostnames (`127.0.0.1:8080`) **antes** de remover o A record.
2. Adicione `CLOUDFLARE_TUNNEL_TOKEN` no GitHub e rode `terraform apply` (remove EIP, fecha SG 80/443).
3. Dispare deploy para reconfigurar nginx + cloudflared na EC2.
4. Remova o A record antigo no Cloudflare; confirme que o tunnel assumiu o DNS.
5. Opcional: desative certbot na instância (`systemctl disable --now certbot.timer`).

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
| **Brute-force**   | fail2ban com jail sshd |
| **Exposição**     | origem fechada (sem 80/443 públicos); tráfego via Cloudflare Tunnel |
| **Kernel**        | sysctl: rp_filter, syncookies, ptrace_scope=2, kptr_restrict, dmesg_restrict, BPF não-privilegiado off, randomize_va_space=2 |
| **Filesystem**    | protected_{hardlinks,symlinks,fifos,regular}, suid_dumpable=0, EBS gp3 + KMS |
| **AppArmor**      | habilitado por padrão no Ubuntu 24.04 (perfis nginx/postgres ativos) |
| **Auditd**        | regras /etc/passwd, /etc/shadow, /etc/sudoers, /etc/ssh/sshd_config, /opt/pdt |
| **Patches**       | unattended-upgrades (auto-reboot 04:30) + SSM Patch Manager semanal |
| **App**           | Daphne em systemd com NoNewPrivileges, ProtectSystem=strict, PrivateTmp, MemoryDenyWriteExecute, SystemCallFilter |
| **TLS**           | terminado na Cloudflare (Full/Full strict) |
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
| t4g.nano       | ~3.00 (ARM64/Graviton, on-demand us-east-1) |
| EBS gp3 20GB   | ~1.60 |
| Cloudflare Tunnel | $0 (plano Free) |
| S3 (poucos MB) | <$1 |
| Data transfer  | varia (100GB grátis no free tier) |

Total típico: **$6–10/mês** após o free tier.
