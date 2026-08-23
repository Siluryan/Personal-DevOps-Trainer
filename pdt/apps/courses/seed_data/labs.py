"""60 laboratórios práticos, um por tópico, todos interativos client-side.

Resolve a queixa "não tem laboratório prático de verdade" sem exigir sandbox
real (a plataforma roda numa t4g.nano, 512 MB — sandbox por aluno exigiria
uma fleet própria) e sem depender de computador (todo formato é por toque,
não por digitação — importa pra quem estuda pelo celular).

Cada entrada tem `topic_title` (deve bater exatamente com o "title" do
tópico em phaseN.py), `kind` (um de apps.courses.models.Lab.Kind) e `spec`
no formato esperado por aquele kind (ver static/js/lab.js):

  terminal:  {scenario, correct_command: [tok,...], distractor_tokens: [...], explanation}
  find_flaw: {scenario, lines: [...], flaw_line_index, explanation}
  order:     {scenario, steps_shuffled: [...], correct_order: [...], explanation}
  blanks:    {scenario, template: "...___KEY___...", blanks: {KEY: {options:[...], correct}}, explanation}
  scenario:  {situation, choices: [{text, outcome, good}], explanation}

Carregado no banco por `python manage.py seed_labs` (mesmo padrão de
seed_topics/seed_glossary: idempotente, respeita seed_managed).
"""
from __future__ import annotations

LABS: list[dict] = [
    # ══════════════════════════════════════════════════════════ FASE 1 ═══
    {
        "topic_title": "Fundamentos de Linux",
        "kind": "terminal",
        "title": "Ache o dono certo",
        "spec": {
            "scenario": (
                "Você precisa dar permissão de LEITURA a um usuário específico "
                "(visitante) num arquivo, sem mudar o dono nem o grupo dele."
            ),
            "correct_command": ["setfacl", "-m", "u:visitante:r--", "config.yml"],
            "distractor_tokens": ["chmod", "chown", "-R"],
            "explanation": (
                "ACL (setfacl) adiciona permissão pra um usuário específico sem "
                "mexer no dono/grupo tradicional. chmod/chown mudariam a permissão "
                "de todo mundo, não só do visitante."
            ),
        },
    },
    {
        "topic_title": "Redes de Computadores",
        "kind": "terminal",
        "title": "Resolva o nome",
        "spec": {
            "scenario": "Descubra rapidamente pra qual IP o nome exemplo.com resolve, sem ruído extra na saída.",
            "correct_command": ["dig", "exemplo.com", "+short"],
            "distractor_tokens": ["ping", "-c", "nslookup"],
            "explanation": (
                "`dig +short` retorna só o IP, direto ao ponto. `ping` testa "
                "conectividade (não é resolução pura); `nslookup` funciona mas "
                "está deprecado em favor de `dig`."
            ),
        },
    },
    {
        "topic_title": "Bash/Shell Scripting",
        "kind": "find_flaw",
        "title": "Ache o bug do loop",
        "spec": {
            "scenario": "Este script apaga arquivos .txt de um diretório, mas quebra com nome de arquivo que tem espaço. Ache a linha do bug.",
            "lines": [
                "#!/bin/bash",
                "for f in $(ls *.txt)",
                "do",
                "  rm $f",
                "done",
            ],
            "flaw_line_index": 1,
            "explanation": (
                "`$(ls *.txt)` sem aspas sofre word splitting: um arquivo chamado "
                "\"relatório final.txt\" vira dois argumentos separados. O jeito "
                "certo é `for f in *.txt` (glob direto do shell, sem `ls`)."
            ),
        },
    },
    {
        "topic_title": "SSH & Chaves Criptográficas",
        "kind": "terminal",
        "title": "Gere as chaves",
        "spec": {
            "scenario": "Gere um novo par de chaves SSH usando o algoritmo moderno recomendado (Ed25519, mais rápido e seguro que RSA).",
            "correct_command": ["ssh-keygen", "-t", "ed25519"],
            "distractor_tokens": ["rsa", "-b", "4096"],
            "explanation": (
                "`-t ed25519` escolhe o algoritmo moderno. RSA ainda funciona, "
                "mas exige chave maior (4096 bits) pra segurança equivalente e é "
                "mais lento pra gerar e verificar."
            ),
        },
    },
    {
        "topic_title": "Princípio do Privilégio Mínimo (PoLP)",
        "kind": "find_flaw",
        "title": "Ache a permissão exagerada",
        "spec": {
            "scenario": "Esta política IAM deveria permitir só a leitura de objetos de um bucket. Ache a linha que viola o PoLP.",
            "lines": [
                "{",
                '  "Effect": "Allow",',
                '  "Action": "s3:*",',
                '  "Resource": "arn:aws:s3:::meu-bucket/*"',
                "}",
            ],
            "flaw_line_index": 2,
            "explanation": (
                '`s3:*` libera TODA ação do S3 (deletar, sobrescrever, mudar '
                "permissão), não só ler. O certo seria `s3:GetObject`, a ação "
                "mínima necessária pro que foi pedido."
            ),
        },
    },
    {
        "topic_title": "Firewall Básico",
        "kind": "blanks",
        "title": "Feche a porta certa",
        "spec": {
            "scenario": "Configure o firewall pra negar tudo por padrão e liberar só a porta do SSH.",
            "template": "ufw default ___POLICY___\nufw allow ___PORT___/tcp",
            "blanks": {
                "POLICY": {"options": ["deny", "allow"], "correct": "deny"},
                "PORT": {"options": ["22", "3389", "23"], "correct": "22"},
            },
            "explanation": (
                "Política padrão DENY é a base de um firewall seguro: só passa o "
                "que foi explicitamente liberado. 22 é a porta do SSH; 3389 é "
                "RDP (Windows) e 23 é Telnet (sem criptografia, evite)."
            ),
        },
    },
    {
        "topic_title": "Web Servers (Nginx/Apache)",
        "kind": "find_flaw",
        "title": "Ache a config exposta",
        "spec": {
            "scenario": "Este bloco do Nginx tem uma configuração que ajuda um atacante a mirar exploits conhecidos da versão exata do servidor.",
            "lines": [
                "server {",
                "  listen 443 ssl;",
                "  server_tokens on;",
                "  ssl_certificate /etc/ssl/cert.pem;",
                "}",
            ],
            "flaw_line_index": 2,
            "explanation": (
                "`server_tokens on` inclui a versão exata do Nginx no header "
                "`Server` de toda resposta — informação de graça pra quem procura "
                "CVE daquela versão específica. Configuração recomendada: `off`."
            ),
        },
    },
    {
        "topic_title": "Gestão de Pacotes e Repositórios",
        "kind": "order",
        "title": "Instale com segurança",
        "spec": {
            "scenario": "Ordene os passos corretos pra instalar um pacote garantindo que veio de um índice atualizado.",
            "steps_shuffled": [
                "apt list --installed | grep pacote",
                "apt install pacote",
                "apt update",
            ],
            "correct_order": [
                "apt update",
                "apt install pacote",
                "apt list --installed | grep pacote",
            ],
            "explanation": (
                "`update` primeiro sincroniza o índice de pacotes disponíveis "
                "(sem isso você pode instalar uma versão desatualizada ou já "
                "removida do espelho). Verificar depois confirma que instalou."
            ),
        },
    },
    {
        "topic_title": "Log Management",
        "kind": "terminal",
        "title": "Ache os erros de hoje",
        "spec": {
            "scenario": "Usando journalctl, veja só as mensagens de erro (ou pior) registradas hoje.",
            "correct_command": ["journalctl", "-p", "err", "-S", "today"],
            "distractor_tokens": ["-u", "nginx"],
            "explanation": (
                "`-p err` filtra por prioridade (erro ou mais grave); `-S today` "
                "limita ao dia atual. `-u nginx` filtraria por serviço específico "
                "— útil, mas não foi pedido aqui."
            ),
        },
    },
    {
        "topic_title": "Cultura DevSecOps",
        "kind": "scenario",
        "title": "CVE a 10 minutos do deploy",
        "spec": {
            "situation": (
                "O SCA aponta uma CVE crítica numa dependência, 10 minutos antes "
                "do deploy de sexta-feira que o time já estava esperando."
            ),
            "choices": [
                {
                    "text": "Faz o deploy assim mesmo e corrige na próxima semana.",
                    "outcome": "A CVE fica explorável em produção o fim de semana inteiro, sem ninguém de plantão acompanhando de perto.",
                    "good": False,
                },
                {
                    "text": "Bloqueia o deploy e aciona quem puder corrigir agora.",
                    "outcome": "O deploy atrasa, mas a falha crítica é fechada antes de qualquer exposição real.",
                    "good": True,
                },
            ],
            "explanation": (
                "Cultura DevSecOps trata segurança como parte do "
                "\"pronto\", não como etapa opcional que dá pra empurrar quando "
                "aperta o prazo — sobretudo numa CVE crítica."
            ),
        },
    },
    # ══════════════════════════════════════════════════════════ FASE 2 ═══
    {
        "topic_title": "Virtualização vs. Cloud",
        "kind": "scenario",
        "title": "Kernel incompatível",
        "spec": {
            "situation": (
                "Uma aplicação legada só funciona com um kernel Linux 3.x "
                "específico, incompatível com o kernel do host moderno."
            ),
            "choices": [
                {
                    "text": "Roda a aplicação num container.",
                    "outcome": "Falha: o container compartilha o kernel do host, não traz um kernel próprio junto.",
                    "good": False,
                },
                {
                    "text": "Roda a aplicação numa máquina virtual.",
                    "outcome": "Funciona: o hypervisor dá à VM seu próprio kernel, isolado do host.",
                    "good": True,
                },
            ],
            "explanation": (
                "Container é isolamento de processo sobre o MESMO kernel; "
                "quando a dependência é o kernel em si, só a virtualização "
                "completa (VM) resolve."
            ),
        },
    },
    {
        "topic_title": "Shared Responsibility Model",
        "kind": "find_flaw",
        "title": "De quem é a culpa?",
        "spec": {
            "scenario": "Uma dessas quatro responsabilidades está atribuída à pessoa errada. Ache qual.",
            "lines": [
                "Cliente configura as regras de IAM.",
                "Provedor aplica patch no hypervisor.",
                "Cliente aplica patch no hypervisor.",
                "Cliente configura o security group.",
            ],
            "flaw_line_index": 2,
            "explanation": (
                "O hypervisor é infraestrutura do PROVEDOR — o cliente nunca tem "
                "acesso pra sequer tentar aplicar patch nele. IAM e security "
                "group são configuração, sempre do lado do cliente."
            ),
        },
    },
    {
        "topic_title": "IAM (Identity and Access Management)",
        "kind": "blanks",
        "title": "Política mínima",
        "spec": {
            "scenario": "Dê a um serviço só a permissão de LER objetos de UM bucket específico, seguindo o PoLP.",
            "template": '{\n  "Effect": "Allow",\n  "Action": "___ACTION___",\n  "Resource": "___RESOURCE___"\n}',
            "blanks": {
                "ACTION": {
                    "options": ["s3:GetObject", "s3:*", "*"],
                    "correct": "s3:GetObject",
                },
                "RESOURCE": {
                    "options": [
                        "arn:aws:s3:::meu-bucket/*",
                        "*",
                        "arn:aws:s3:::*",
                    ],
                    "correct": "arn:aws:s3:::meu-bucket/*",
                },
            },
            "explanation": (
                "Ação específica (`GetObject`, não `s3:*`) e recurso restrito a "
                "UM bucket (não `*`, que libera todos) é o PoLP na prática: o "
                "mínimo necessário, nada além."
            ),
        },
    },
    {
        "topic_title": "VPC & Subnets",
        "kind": "order",
        "title": "O caminho do pacote",
        "spec": {
            "scenario": "Ordene o caminho que um pacote percorre saindo de uma instância PRIVADA até a internet.",
            "steps_shuffled": [
                "Internet Gateway",
                "Instância na subnet privada",
                "Internet",
                "NAT Gateway na subnet pública",
            ],
            "correct_order": [
                "Instância na subnet privada",
                "NAT Gateway na subnet pública",
                "Internet Gateway",
                "Internet",
            ],
            "explanation": (
                "Instância privada não tem IP público: ela sai pelo NAT Gateway "
                "(que fica numa subnet pública), que por sua vez sai pelo "
                "Internet Gateway da VPC."
            ),
        },
    },
    {
        "topic_title": "Security Groups & ACLs",
        "kind": "scenario",
        "title": "Faltou a volta",
        "spec": {
            "situation": (
                "Você libera a porta 443 de ENTRADA numa Network ACL (stateless). "
                "A resposta do servidor sai sem problema?"
            ),
            "choices": [
                {
                    "text": "Sim, a NACL libera a saída automaticamente.",
                    "outcome": "Errado: NACL é stateless, ela não lembra da conexão de entrada pra liberar a volta sozinha.",
                    "good": False,
                },
                {
                    "text": "Não, precisa de uma regra de SAÍDA própria também.",
                    "outcome": "Certo: diferente do Security Group (stateful), a NACL exige regra explícita nos dois sentidos.",
                    "good": True,
                },
            ],
            "explanation": (
                "Security Group lembra da conexão (stateful): libera entrada, a "
                "resposta sai de graça. Network ACL não lembra (stateless): cada "
                "sentido precisa da própria regra."
            ),
        },
    },
    {
        "topic_title": "Object Storage (S3)",
        "kind": "terminal",
        "title": "Liste o bucket",
        "spec": {
            "scenario": "Liste todos os objetos dentro de um bucket S3 usando o CLI da AWS.",
            "correct_command": ["aws", "s3", "ls", "s3://meu-bucket"],
            "distractor_tokens": ["cp", "--recursive"],
            "explanation": (
                "`aws s3 ls s3://bucket` lista o conteúdo. `cp --recursive` "
                "serve pra COPIAR uma árvore inteira, não pra listar."
            ),
        },
    },
    {
        "topic_title": "Criptografia em Repouso e Trânsito",
        "kind": "find_flaw",
        "title": "Ache o backup exposto",
        "spec": {
            "scenario": "Destas quatro práticas de segurança, uma delas deixa dado sensível vulnerável em repouso. Ache qual.",
            "lines": [
                "Certificado TLS 1.3 configurado no load balancer.",
                "Backup do banco de dados sem criptografia.",
                "Chave do KMS rotacionada anualmente.",
                "HSTS habilitado no servidor web.",
            ],
            "flaw_line_index": 1,
            "explanation": (
                "TLS e HSTS protegem o dado EM TRÂNSITO; a chave de KMS protege "
                "o dado em repouso — mas um backup sem criptografia nenhuma "
                "deixa tudo exposto pra quem tiver acesso ao arquivo físico."
            ),
        },
    },
    {
        "topic_title": "Monitoramento Básico (CloudWatch/Monitor)",
        "kind": "blanks",
        "title": "Configure o alarme",
        "spec": {
            "scenario": "Configure um alarme que dispara quando a CPU fica ALTA por tempo prolongado.",
            "template": "Alarm: CPUUtilization ___OP___ ___THRESHOLD___% por 5 minutos → dispara",
            "blanks": {
                "OP": {"options": [">", "<", "="], "correct": ">"},
                "THRESHOLD": {"options": ["80", "10", "100"], "correct": "80"},
            },
            "explanation": (
                "Alarme de CPU alta usa `>` com um limiar realista (80%) — "
                "100% raramente é sustentado por 5 minutos inteiros sem já "
                "ter causado impacto visível, e 10% seria alarme falso constante."
            ),
        },
    },
    {
        "topic_title": "Backup & Disaster Recovery",
        "kind": "order",
        "title": "Depois do desastre",
        "spec": {
            "scenario": "Ordene os passos de um ciclo saudável de disaster recovery.",
            "steps_shuffled": [
                "Serviço volta a operar",
                "Postmortem documenta RPO/RTO reais",
                "Backup automatizado diário",
                "Incidente derruba o serviço",
                "Restaura o backup mais recente",
            ],
            "correct_order": [
                "Backup automatizado diário",
                "Incidente derruba o serviço",
                "Restaura o backup mais recente",
                "Serviço volta a operar",
                "Postmortem documenta RPO/RTO reais",
            ],
            "explanation": (
                "Backup precisa existir ANTES do incidente pra servir de algo. "
                "Depois de restaurar e voltar a operar, o postmortem mede se o "
                "RPO/RTO prometidos bateram com o que aconteceu de verdade."
            ),
        },
    },
    {
        "topic_title": "FinOps Inicial",
        "kind": "scenario",
        "title": "A instância ociosa",
        "spec": {
            "situation": (
                "O dashboard de custo mostra uma instância rodando 24/7 com "
                "5% de uso médio de CPU nos últimos 30 dias."
            ),
            "choices": [
                {
                    "text": "Deixa rodando, pode precisar depois.",
                    "outcome": "O custo mensal segue alto por uma capacidade que ninguém está usando.",
                    "good": False,
                },
                {
                    "text": "Redimensiona pra um tipo menor ou desliga fora do horário de uso.",
                    "outcome": "O custo cai proporcionalmente, sem perder a capacidade que de fato é usada.",
                    "good": True,
                },
            ],
            "explanation": (
                "FinOps é visibilidade virando ação: achar o recurso ocioso é só "
                "metade do trabalho, a outra metade é realmente ajustar."
            ),
        },
    },
    # ══════════════════════════════════════════════════════════ FASE 3 ═══
    {
        "topic_title": "Versionamento com Git",
        "kind": "terminal",
        "title": "Nova feature, nova branch",
        "spec": {
            "scenario": "Crie uma branch nova chamada 'feature' e já mude pra ela, num comando só.",
            "correct_command": ["git", "checkout", "-b", "feature"],
            "distractor_tokens": ["branch", "merge"],
            "explanation": (
                "`checkout -b` cria E muda de branch num comando. `git branch` "
                "sozinho só criaria, sem trocar; `merge` é pra juntar branches, "
                "não criar uma nova."
            ),
        },
    },
    {
        "topic_title": "Infraestrutura como Código (Terraform)",
        "kind": "order",
        "title": "Do plano ao apply",
        "spec": {
            "scenario": "Ordene o fluxo seguro de uma mudança de infraestrutura via Terraform.",
            "steps_shuffled": [
                "terraform apply",
                "Escreve ou edita o .tf",
                "Revisa o diff mostrado",
                "terraform plan",
            ],
            "correct_order": [
                "Escreve ou edita o .tf",
                "terraform plan",
                "Revisa o diff mostrado",
                "terraform apply",
            ],
            "explanation": (
                "`plan` mostra o que vai mudar SEM aplicar — pular a revisão do "
                "diff e ir direto pro `apply` é como assinar um contrato sem ler."
            ),
        },
    },
    {
        "topic_title": "Gestão de Configuração (Ansible)",
        "kind": "find_flaw",
        "title": "Ache a senha no playbook",
        "spec": {
            "scenario": "Este playbook Ansible tem um problema de segurança clássico. Ache a linha.",
            "lines": [
                "- name: Instala pacote",
                "  apt: name=nginx state=present",
                "- name: Configura senha do banco",
                '  lineinfile: line="DB_PASS=supersecreto123"',
            ],
            "flaw_line_index": 3,
            "explanation": (
                "Senha em texto puro dentro do playbook vai parar no Git, "
                "visível pra qualquer um com acesso ao repositório. O certo é "
                "usar Ansible Vault ou um cofre de segredos externo."
            ),
        },
    },
    {
        "topic_title": "Secret Management",
        "kind": "find_flaw",
        "title": "Ache a chave exposta",
        "spec": {
            "scenario": "Este código tem uma credencial exposta de um jeito perigoso. Ache a linha.",
            "lines": [
                "import os",
                'API_KEY = "sk_live_51H8xJ2KZ..."',
                "response = requests.get(url, headers={'Authorization': API_KEY})",
            ],
            "flaw_line_index": 1,
            "explanation": (
                "Chave hardcoded no código-fonte vai pro Git, pra qualquer "
                "clone do repo e pro histórico de commits pra sempre. O certo é "
                "ler de uma variável de ambiente ou de um cofre de segredos."
            ),
        },
    },
    {
        "topic_title": "CI/CD Básico",
        "kind": "order",
        "title": "Do commit ao deploy",
        "spec": {
            "scenario": "Ordene as etapas de um pipeline CI/CD básico.",
            "steps_shuffled": ["Deploy", "Testes automatizados", "Commit", "Build"],
            "correct_order": ["Commit", "Build", "Testes automatizados", "Deploy"],
            "explanation": (
                "Cada etapa só faz sentido depois da anterior: build sem "
                "commit não tem o que compilar, deploy sem teste não sabe se "
                "o que vai subir funciona."
            ),
        },
    },
    {
        "topic_title": "Linting de Código e IaC",
        "kind": "find_flaw",
        "title": "Ache o bucket público",
        "spec": {
            "scenario": "Um linter de IaC (como tfsec ou checkov) bloquearia este bloco Terraform. Ache a linha do problema.",
            "lines": [
                'resource "aws_s3_bucket" "data" {',
                '  bucket = "my-bucket-12345"',
                '  acl    = "public-read"',
                "}",
            ],
            "flaw_line_index": 2,
            "explanation": (
                '`acl = "public-read"` deixa o bucket legível por qualquer um '
                "na internet — exatamente o tipo de erro que um linter de IaC "
                "existe pra pegar antes do `apply`."
            ),
        },
    },
    {
        "topic_title": "SAST",
        "kind": "find_flaw",
        "title": "Ache a injeção de SQL",
        "spec": {
            "scenario": "Um SAST real acusaria esta função. Ache a linha vulnerável.",
            "lines": [
                "def get_user(request):",
                "    user_id = request.GET['id']",
                '    query = f"SELECT * FROM users WHERE id = {user_id}"',
                "    return db.execute(query)",
            ],
            "flaw_line_index": 2,
            "explanation": (
                "Concatenar input do usuário direto numa query via f-string "
                "permite SQL Injection (`id=1 OR 1=1`). O certo é usar "
                "parametrização (`WHERE id = %s`, [user_id])."
            ),
        },
    },
    {
        "topic_title": "SCA",
        "kind": "scenario",
        "title": "Atualizar dá trabalho",
        "spec": {
            "situation": (
                "O SCA aponta uma CVE crítica numa lib usada em 12 lugares do "
                "projeto, mas atualizar ela quebra a API em 3 desses lugares."
            ),
            "choices": [
                {
                    "text": "Ignora o alerta, atualizar dá muito trabalho agora.",
                    "outcome": "A vulnerabilidade crítica continua explorável em produção indefinidamente.",
                    "good": False,
                },
                {
                    "text": "Atualiza a lib e corrige os 3 pontos que quebraram.",
                    "outcome": "Leva mais tempo, mas a CVE crítica é fechada de verdade.",
                    "good": True,
                },
            ],
            "explanation": (
                "SCA sem ação vira ruído: encontrar a CVE e não corrigir "
                "porque dá trabalho anula o propósito da ferramenta."
            ),
        },
    },
    {
        "topic_title": "Code Review",
        "kind": "scenario",
        "title": "Confiar sem ler",
        "spec": {
            "situation": (
                "Um PR de um dev sênior chega pra sua revisão. Você não entende "
                "totalmente uma parte da mudança, mas confia na experiência dele."
            ),
            "choices": [
                {
                    "text": "Aprova sem comentar, confiando na experiência do autor.",
                    "outcome": "Meses depois, um bug sutil justamente naquela parte causa um incidente — que ninguém tinha revisado de verdade.",
                    "good": False,
                },
                {
                    "text": "Pergunta e pede pra ele explicar a parte que você não entendeu.",
                    "outcome": "A conversa revela um edge case não tratado, corrigido antes do merge.",
                    "good": True,
                },
            ],
            "explanation": (
                "Rubber stamp (aprovar sem ler) é mais comum justamente com "
                "autor sênior — e é aí que mais escapa bug, porque ninguém "
                "questiona."
            ),
        },
    },
    {
        "topic_title": "Artifact Repositories",
        "kind": "terminal",
        "title": "Assine o artefato",
        "spec": {
            "scenario": "Assine uma imagem de container recém publicada usando Cosign, pra provar sua origem.",
            "correct_command": ["cosign", "sign", "imagem:tag"],
            "distractor_tokens": ["verify", "--yes"],
            "explanation": (
                "`cosign sign` assina o artefato. `cosign verify` faria o "
                "inverso: checar uma assinatura já existente."
            ),
        },
    },
    # ══════════════════════════════════════════════════════════ FASE 4 ═══
    {
        "topic_title": "Docker Fundamentals",
        "kind": "order",
        "title": "Do Dockerfile ao container",
        "spec": {
            "scenario": "Ordene o fluxo básico de empacotar e rodar uma aplicação com Docker.",
            "steps_shuffled": ["docker run app", "Escreve o Dockerfile", "docker build -t app ."],
            "correct_order": ["Escreve o Dockerfile", "docker build -t app .", "docker run app"],
            "explanation": (
                "O Dockerfile descreve como construir a imagem; `build` gera a "
                "imagem a partir dele; `run` cria e inicia um container a "
                "partir da imagem já construída."
            ),
        },
    },
    {
        "topic_title": "Segurança de Imagens",
        "kind": "find_flaw",
        "title": "Ache o root desnecessário",
        "spec": {
            "scenario": "Este Dockerfile tem uma prática de segurança ruim. Ache a linha.",
            "lines": [
                "FROM python:3.12",
                "COPY . /app",
                "RUN pip install -r requirements.txt",
                "USER root",
                'CMD ["python", "app.py"]',
            ],
            "flaw_line_index": 3,
            "explanation": (
                "Rodar como root dentro do container amplia MUITO o impacto de "
                "qualquer vulnerabilidade explorada lá dentro. O ideal é criar "
                "um usuário sem privilégio e usar `USER` com ele."
            ),
        },
    },
    {
        "topic_title": "Container Registry",
        "kind": "terminal",
        "title": "Puxe pelo digest certo",
        "spec": {
            "scenario": "Puxe uma imagem garantindo que é EXATAMENTE aquele conteúdo, imutável, não uma tag que pode mudar.",
            "correct_command": ["docker", "pull", "app@sha256:abc123"],
            "distractor_tokens": ["app:latest", "docker push"],
            "explanation": (
                "Puxar por digest (`@sha256:...`) garante o conteúdo exato e "
                "imutável. `app:latest` é uma tag móvel: o que ela aponta pode "
                "mudar amanhã sem aviso."
            ),
        },
    },
    {
        "topic_title": "Orquestração Simples",
        "kind": "blanks",
        "title": "Complete o healthcheck",
        "spec": {
            "scenario": "Complete o docker-compose.yml pra que o Docker saiba verificar se o serviço está saudável.",
            "template": (
                "services:\n  app:\n    image: app:latest\n    depends_on:\n"
                '      - db\n    ___KEY___:\n      test: ["CMD", "curl", "-f", "http://localhost/health"]'
            ),
            "blanks": {
                "KEY": {
                    "options": ["healthcheck", "restart", "ports"],
                    "correct": "healthcheck",
                },
            },
            "explanation": (
                "`healthcheck` diz ao Docker como testar se o serviço está de "
                "pé de verdade, não só se o processo iniciou."
            ),
        },
    },
    {
        "topic_title": "Software Bill of Materials (SBOM)",
        "kind": "terminal",
        "title": "Gere o inventário",
        "spec": {
            "scenario": "Gere um SBOM de uma imagem de container no formato CycloneDX, usando o Syft.",
            "correct_command": ["syft", "imagem:tag", "-o", "cyclonedx-json"],
            "distractor_tokens": ["--scan", "trivy"],
            "explanation": (
                "`syft <imagem> -o cyclonedx-json` gera o inventário de "
                "componentes no formato CycloneDX. Trivy é outra ferramenta "
                "(mais focada em scan de CVE do que em gerar SBOM)."
            ),
        },
    },
    {
        "topic_title": "Internal Developer Platforms (IDP)",
        "kind": "scenario",
        "title": "Ticket ou self-service?",
        "spec": {
            "situation": (
                "Um dev precisa criar um microsserviço novo, já com CI/CD, "
                "monitoramento e permissões corretas desde o primeiro dia."
            ),
            "choices": [
                {
                    "text": "Abre um ticket separado pra cada time (infra, segurança, SRE).",
                    "outcome": "Leva semanas até tudo estar pronto e consistente entre os times.",
                    "good": False,
                },
                {
                    "text": "Usa o template golden path da plataforma interna.",
                    "outcome": "Em minutos, o serviço nasce com CI/CD, observabilidade e IAM já configurados do jeito certo.",
                    "good": True,
                },
            ],
            "explanation": (
                "O golden path de uma IDP existe justamente pra eliminar essa "
                "espera: o caminho recomendado já vem pronto, sem depender de "
                "vários times manualmente."
            ),
        },
    },
    {
        "topic_title": "Policy as Code (PaC)",
        "kind": "find_flaw",
        "title": "Ache o pod privilegiado",
        "spec": {
            "scenario": "Um admission controller com boas políticas bloquearia este manifesto. Ache a linha.",
            "lines": [
                "apiVersion: v1",
                "kind: Pod",
                "spec:",
                "  containers:",
                "  - name: app",
                "    image: app:latest",
                "    securityContext:",
                "      privileged: true",
            ],
            "flaw_line_index": 7,
            "explanation": (
                "`privileged: true` dá ao container acesso quase irrestrito ao "
                "host — exatamente o tipo de configuração que uma política "
                "(OPA/Kyverno) deveria barrar antes de criar o recurso."
            ),
        },
    },
    {
        "topic_title": "DAST inicial",
        "kind": "order",
        "title": "Ataque de fora",
        "spec": {
            "scenario": "Ordene as etapas de um scan DAST contra uma aplicação já rodando.",
            "steps_shuffled": [
                "Reporta a vulnerabilidade encontrada",
                "Analisa as respostas recebidas",
                "App sobe em ambiente isolado de staging",
                "Scanner envia requisições maliciosas",
            ],
            "correct_order": [
                "App sobe em ambiente isolado de staging",
                "Scanner envia requisições maliciosas",
                "Analisa as respostas recebidas",
                "Reporta a vulnerabilidade encontrada",
            ],
            "explanation": (
                "DAST precisa da aplicação rodando de verdade (diferente do "
                "SAST, que lê código parado) — por isso o app precisa estar de "
                "pé, num ambiente isolado, antes do ataque simulado começar."
            ),
        },
    },
    {
        "topic_title": "API Security",
        "kind": "find_flaw",
        "title": "Ache o pedido de outro usuário",
        "spec": {
            "scenario": "Este endpoint tem uma falha clássica de BOLA (Broken Object Level Authorization). Ache a linha.",
            "lines": [
                "@app.get('/pedidos/{id}')",
                "def get_pedido(id, user=Depends(get_current_user)):",
                "    pedido = db.query(Pedido).filter_by(id=id).first()",
                "    return pedido",
            ],
            "flaw_line_index": 2,
            "explanation": (
                "A query busca o pedido só pelo `id`, sem checar se ele "
                "pertence ao `user` autenticado. Qualquer usuário logado pode "
                "ler o pedido de qualquer outro só trocando o id na URL."
            ),
        },
    },
    {
        "topic_title": "Centralized Logging",
        "kind": "find_flaw",
        "title": "Ache o dado sensível no log",
        "spec": {
            "scenario": "Uma dessas três linhas de log vai parar num sistema de log centralizado com um dado que nunca deveria estar lá. Ache qual.",
            "lines": [
                "logger.info(f'Login: user={user.email}')",
                "logger.info(f'Pagamento processado: card={card_number}')",
                "logger.error('Falha ao conectar no banco')",
            ],
            "flaw_line_index": 1,
            "explanation": (
                "Número de cartão em log centralizado é dado de altíssima "
                "sensibilidade (PCI DSS) espalhado por todo sistema que lê "
                "aquele log — exatamente o tipo de coisa que se mascara antes de logar."
            ),
        },
    },
    # ══════════════════════════════════════════════════════════ FASE 5 ═══
    {
        "topic_title": "Introdução ao Kubernetes (K8s)",
        "kind": "terminal",
        "title": "Liste os pods",
        "spec": {
            "scenario": "Liste os pods do namespace 'default' no cluster.",
            "correct_command": ["kubectl", "get", "pods", "-n", "default"],
            "distractor_tokens": ["-A", "describe"],
            "explanation": (
                "`-n default` filtra pro namespace pedido. `-A` listaria de "
                "TODOS os namespaces; `describe` mostraria detalhe de UM pod "
                "específico, não a lista."
            ),
        },
    },
    {
        "topic_title": "K8s Hardening",
        "kind": "find_flaw",
        "title": "Ache o container arriscado",
        "spec": {
            "scenario": "Este manifesto tem uma configuração que um cluster hardened não deveria permitir. Ache a linha.",
            "lines": [
                "apiVersion: v1",
                "kind: Pod",
                "spec:",
                "  containers:",
                "  - name: app",
                "    securityContext:",
                "      runAsNonRoot: false",
            ],
            "flaw_line_index": 6,
            "explanation": (
                "`runAsNonRoot: false` permite explicitamente que o container "
                "rode como root — o oposto do hardening recomendado, que exige "
                "`true` por padrão em qualquer PodSecurity policy séria."
            ),
        },
    },
    {
        "topic_title": "Network Policies",
        "kind": "blanks",
        "title": "Negue por padrão",
        "spec": {
            "scenario": "Complete a NetworkPolicy que bloqueia todo tráfego de ENTRADA por padrão num namespace.",
            "template": "kind: NetworkPolicy\nspec:\n  podSelector: {}\n  policyTypes:\n  - ___TYPE___",
            "blanks": {
                "TYPE": {"options": ["Ingress", "Egress", "Both"], "correct": "Ingress"},
            },
            "explanation": (
                "`podSelector: {}` seleciona TODOS os pods do namespace; sem "
                "nenhuma regra de `ingress` declarada, `policyTypes: [Ingress]` "
                "vira um default-deny de entrada pra eles."
            ),
        },
    },
    {
        "topic_title": "Admission Controllers",
        "kind": "order",
        "title": "Do apply ao etcd",
        "spec": {
            "scenario": "Ordene o caminho de uma requisição `kubectl apply` até ser persistida.",
            "steps_shuffled": [
                "Recurso persistido no etcd",
                "kubectl apply enviado à API server",
                "Validating webhook processa",
                "Mutating webhook processa",
            ],
            "correct_order": [
                "kubectl apply enviado à API server",
                "Mutating webhook processa",
                "Validating webhook processa",
                "Recurso persistido no etcd",
            ],
            "explanation": (
                "Mutating roda ANTES de validating de propósito: um webhook "
                "pode injetar um valor (ex.: sidecar) que só depois é validado "
                "— validar antes de mutar checaria um recurso que ainda vai mudar."
            ),
        },
    },
    {
        "topic_title": "Zero Trust Architecture",
        "kind": "scenario",
        "title": "Confiar na rede ou na identidade?",
        "spec": {
            "situation": "Um funcionário tenta acessar um sistema interno de casa, fora da VPN corporativa.",
            "choices": [
                {
                    "text": "Bloqueia por padrão, já que não está na rede da empresa.",
                    "outcome": "Isso é o modelo de perímetro antigo — exatamente o que Zero Trust existe pra substituir.",
                    "good": False,
                },
                {
                    "text": "Verifica identidade e postura do dispositivo, independente da rede de origem.",
                    "outcome": "O acesso é avaliado pelo contexto real (quem é, dispositivo confiável), não pela localização de rede.",
                    "good": True,
                },
            ],
            "explanation": (
                "Zero Trust parte da premissa de que rede nenhuma é "
                "automaticamente confiável — dentro OU fora do escritório. "
                "O que decide é identidade + contexto, sempre."
            ),
        },
    },
    {
        "topic_title": "Runtime Security",
        "kind": "find_flaw",
        "title": "Ache o comportamento estranho",
        "spec": {
            "scenario": "Um monitor de runtime (tipo Falco) geraria alerta pra um destes três eventos. Ache qual.",
            "lines": [
                "Container abriu conexão de saída na porta 443 (esperado)",
                "Container executou /bin/sh interativo (não esperado)",
                "Container leu um arquivo de configuração local (esperado)",
            ],
            "flaw_line_index": 1,
            "explanation": (
                "Um shell interativo dentro de um container de produção é "
                "clássico sinal de comprometimento — na maioria dos workloads, "
                "ninguém deveria estar abrindo shell ali ao vivo."
            ),
        },
    },
    {
        "topic_title": "Observabilidade Avançada",
        "kind": "blanks",
        "title": "Correlacione pelo trace",
        "spec": {
            "scenario": "Complete o log pra que ele possa ser correlacionado com o trace distribuído da mesma requisição.",
            "template": "logger.info('processing request', extra={'___KEY___': span.trace_id})",
            "blanks": {
                "KEY": {"options": ["trace_id", "user_id", "timestamp"], "correct": "trace_id"},
            },
            "explanation": (
                "Incluir o `trace_id` no log é o que permite pular do log "
                "direto pro trace correspondente — a correlação entre os dois "
                "pilares da observabilidade."
            ),
        },
    },
    {
        "topic_title": "Security Chaos Engineering",
        "kind": "order",
        "title": "Experimento controlado",
        "spec": {
            "scenario": "Ordene os passos de um experimento de chaos engineering responsável.",
            "steps_shuffled": [
                "Observa o resultado",
                "Define o blast radius",
                "Documenta o aprendizado",
                "Formula a hipótese",
                "Executa o experimento controlado",
            ],
            "correct_order": [
                "Formula a hipótese",
                "Define o blast radius",
                "Executa o experimento controlado",
                "Observa o resultado",
                "Documenta o aprendizado",
            ],
            "explanation": (
                "Sem hipótese e blast radius definidos ANTES, o experimento "
                "vira só \"quebrar coisa aleatoriamente\" — o oposto do método "
                "científico que dá valor ao chaos engineering."
            ),
        },
    },
    {
        "topic_title": "Incident Response",
        "kind": "order",
        "title": "As fases do incidente",
        "spec": {
            "scenario": "Ordene as fases do ciclo de resposta a incidente (modelo do NIST).",
            "steps_shuffled": [
                "Containment",
                "Recovery",
                "Preparation",
                "Eradication",
                "Detection & Analysis",
            ],
            "correct_order": [
                "Preparation",
                "Detection & Analysis",
                "Containment",
                "Eradication",
                "Recovery",
            ],
            "explanation": (
                "Preparation vem antes de qualquer incidente acontecer "
                "(runbook, ferramentas prontas); depois é detectar, conter o "
                "avanço, erradicar a causa e só então recuperar o serviço."
            ),
        },
    },
    {
        "topic_title": "Compliance Contínuo",
        "kind": "scenario",
        "title": "Corrigir agora ou depois?",
        "spec": {
            "situation": "Uma checagem automática encontra um bucket S3 público que deveria ser privado.",
            "choices": [
                {
                    "text": "Registra pra revisar na próxima auditoria anual.",
                    "outcome": "O bucket fica exposto publicamente por meses até a auditoria acontecer.",
                    "good": False,
                },
                {
                    "text": "Corrige automaticamente agora e gera evidência do ocorrido.",
                    "outcome": "O desvio é fechado na hora, com rastro completo pra auditoria futura.",
                    "good": True,
                },
            ],
            "explanation": (
                "Compliance CONTÍNUO significa detectar e corrigir desvio em "
                "tempo real, não só uma vez por ano — é essa a diferença pro "
                "modelo de auditoria pontual antigo."
            ),
        },
    },
    # ══════════════════════════════════════════════════════════ FASE 6 ═══
    {
        "topic_title": "Fundamentos de Python moderno",
        "kind": "find_flaw",
        "title": "A lista que não esquece",
        "spec": {
            "scenario": "Esta função tem o bug clássico do argumento default mutável. Ache a linha.",
            "lines": [
                "def add_item(item, cart=[]):",
                "    cart.append(item)",
                "    return cart",
            ],
            "flaw_line_index": 0,
            "explanation": (
                "A lista `[]` é criada UMA vez, na definição da função — todas "
                "as chamadas sem argumento reusam a MESMA lista, acumulando "
                "item de chamadas anteriores. O certo é `cart=None` e criar "
                "a lista dentro do corpo se `cart is None`."
            ),
        },
    },
    {
        "topic_title": "Estruturas de dados e código Pythonic",
        "kind": "find_flaw",
        "title": "Tudo na memória de uma vez",
        "spec": {
            "scenario": "Esta função devia processar um arquivo GRANDE linha por linha, sem estourar a memória. Ache a linha do problema.",
            "lines": [
                "def process(filename):",
                "    lines = [l for l in open(filename)]",
                "    return sum(len(l) for l in lines)",
            ],
            "flaw_line_index": 1,
            "explanation": (
                "Os colchetes forçam carregar TODO o arquivo na memória de uma "
                "vez numa lista. Trocar por um generator (sem colchetes: `l "
                "for l in open(filename)`) processa uma linha por vez."
            ),
        },
    },
    {
        "topic_title": "POO, exceções e context managers",
        "kind": "find_flaw",
        "title": "Esqueceu de fechar",
        "spec": {
            "scenario": "Este código abre um arquivo sem garantir que ele seja fechado se algo der errado no meio. Ache a linha.",
            "lines": [
                "f = open('dados.txt')",
                "data = f.read()",
                "process(data)",
            ],
            "flaw_line_index": 0,
            "explanation": (
                "Sem `with`, se `process(data)` levantar uma exceção, o "
                "arquivo nunca é fechado explicitamente — em processo de longa "
                "vida, isso vaza descritor de arquivo aos poucos."
            ),
        },
    },
    {
        "topic_title": "Manipulação de arquivos, paths e CLI",
        "kind": "blanks",
        "title": "Carregar com segurança",
        "spec": {
            "scenario": "Complete o parse do YAML usando o Loader que NÃO permite executar código arbitrário.",
            "template": "import yaml\nconfig = yaml.load(open('config.yml'), Loader=___LOADER___)",
            "blanks": {
                "LOADER": {
                    "options": ["yaml.SafeLoader", "yaml.Loader", "yaml.UnsafeLoader"],
                    "correct": "yaml.SafeLoader",
                },
            },
            "explanation": (
                "`yaml.Loader` (o padrão antigo) e `UnsafeLoader` permitem "
                "construir objetos Python arbitrários a partir do YAML — "
                "abrindo caminho pra RCE se o arquivo vier de fonte não confiável. "
                "`SafeLoader` só cria tipos básicos (str, int, list, dict)."
            ),
        },
    },
    {
        "topic_title": "HTTP, APIs REST e SDKs",
        "kind": "find_flaw",
        "title": "Sem prazo de espera",
        "spec": {
            "scenario": "Esta chamada HTTP tem um risco sério em produção. Ache a linha.",
            "lines": [
                "import requests",
                "response = requests.get(url)",
                "data = response.json()",
            ],
            "flaw_line_index": 1,
            "explanation": (
                "Sem `timeout`, se o servidor remoto nunca responder, essa "
                "chamada trava o processo INDEFINIDAMENTE — em produção isso "
                "esgota conexões/threads até derrubar o serviço inteiro."
            ),
        },
    },
    {
        "topic_title": "Automação de sistema com Python",
        "kind": "find_flaw",
        "title": "Comando perigoso",
        "spec": {
            "scenario": "Este script de automação tem uma falha clássica de shell injection. Ache a linha.",
            "lines": [
                "import os",
                "filename = input('Arquivo: ')",
                "os.system(f'rm {filename}')",
            ],
            "flaw_line_index": 2,
            "explanation": (
                "Se o usuário digitar `arquivo.txt; rm -rf ~`, o `os.system` "
                "roda os DOIS comandos, já que o input vira parte da string "
                "interpretada pelo shell. `subprocess.run(['rm', filename])` "
                "evita isso, passando o nome como argumento literal."
            ),
        },
    },
    {
        "topic_title": "Concorrência: threads, asyncio e multiprocessing",
        "kind": "find_flaw",
        "title": "Travou o event loop",
        "spec": {
            "scenario": "Esta função async tem um erro que trava TODAS as outras tarefas do event loop. Ache a linha.",
            "lines": [
                "async def fetch_all(urls):",
                "    for url in urls:",
                "        time.sleep(1)",
                "        await fetch(url)",
            ],
            "flaw_line_index": 2,
            "explanation": (
                "`time.sleep` é bloqueante: ele trava a thread inteira, "
                "inclusive o event loop, impedindo QUALQUER outra tarefa "
                "async de rodar nesse segundo. O certo é `await asyncio.sleep(1)`."
            ),
        },
    },
    {
        "topic_title": "Testes com pytest, mocks e cobertura",
        "kind": "find_flaw",
        "title": "Teste que liga pra API de verdade",
        "spec": {
            "scenario": "Este teste unitário tem um problema que o torna lento, instável e caro. Ache a linha.",
            "lines": [
                "def test_send_email():",
                "    result = send_email_via_real_api('a@b.com')",
                "    assert result.status == 200",
            ],
            "flaw_line_index": 1,
            "explanation": (
                "Chamar a API real de e-mail num teste unitário deixa o teste "
                "lento, dependente de rede e sujeito a falhar por motivo "
                "alheio ao código. O certo é mockar a chamada externa."
            ),
        },
    },
    {
        "topic_title": "Empacotamento moderno e qualidade de código",
        "kind": "blanks",
        "title": "Onde vai a dependência de dev?",
        "spec": {
            "scenario": "Complete o pyproject.toml pra declarar pytest e ruff como dependências só de desenvolvimento.",
            "template": '[project]\ndependencies = ["requests"]\n\n[___SECTION___]\ndev = ["pytest", "ruff"]',
            "blanks": {
                "SECTION": {
                    "options": [
                        "project.optional-dependencies",
                        "project.dependencies",
                        "tool.dev",
                    ],
                    "correct": "project.optional-dependencies",
                },
            },
            "explanation": (
                "`[project.optional-dependencies]` com um grupo `dev` é o "
                "jeito padrão de separar o que é necessário pra RODAR o "
                "projeto do que é só pra desenvolver nele."
            ),
        },
    },
    {
        "topic_title": "Python para DevSecOps na prática",
        "kind": "find_flaw",
        "title": "Credencial no código",
        "spec": {
            "scenario": "Este script Python usando boto3 tem um erro grave de segurança. Ache a linha.",
            "lines": [
                "import boto3",
                "session = boto3.Session(aws_access_key_id='AKIAEXAMPLE', aws_secret_access_key='secret123')",
                "s3 = session.client('s3')",
            ],
            "flaw_line_index": 1,
            "explanation": (
                "Credencial AWS hardcoded no código vai pro Git pra sempre. "
                "Rodando numa EC2, o certo é nem precisar disso: anexar um "
                "IAM Role à instância e deixar o boto3 pegar credencial via IMDS."
            ),
        },
    },
]
