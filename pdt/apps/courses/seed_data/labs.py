"""60 laboratórios autorais (1 por tópico), base para expandir 1 lab por página.

Resolve a queixa "não tem laboratório prático de verdade" sem exigir sandbox
real (a plataforma roda numa t4g.nano, 512 MB — sandbox por aluno exigiria
uma fleet própria) e sem depender de computador (todo formato é por toque,
não por digitação — importa pra quem estuda pelo celular).

Cada entrada tem `topic_title` (deve bater exatamente com o "title" do
tópico em phaseN.py), `kind` (um de apps.courses.models.Lab.Kind) e `spec`
no formato esperado por aquele kind (ver static/js/lab.js):

  terminal:  {scenario, correct_command: [tok,...],
              accepted_commands?: [[tok,...], ...],  # ordens equivalentes
              distractor_tokens: [...], explanation}
  find_flaw: {scenario, lines: [...], flaw_line_index, explanation}
  order:     {scenario, steps_shuffled: [...], correct_order: [...], explanation}
  blanks:    {scenario, template: "...___KEY___...", blanks: {KEY: {options:[...], correct}}, explanation}
  scenario:  {situation, choices: [{text, outcome, good}], explanation}

Carregado no banco por `python manage.py seed_labs` (mesmo padrão de
seed_topics/seed_glossary: idempotente, respeita seed_managed).
"""
from __future__ import annotations

LABS: list[dict] = [{'topic_title': 'Fundamentos de Linux',
  'kind': 'terminal',
  'title': 'Ache o dono certo',
  'title_en': 'Find the right owner',
  'spec': {'scenario': 'Você precisa dar permissão de LEITURA a um usuário específico '
                       '(visitante) num arquivo, sem mudar o dono nem o grupo dele.',
           'correct_command': ['setfacl', '-m', 'u:visitante:r--', 'config.yml'],
           'distractor_tokens': ['chmod', 'chown', '-R'],
           'explanation': 'ACL (setfacl) adiciona permissão pra um usuário específico '
                          'sem mexer no dono/grupo tradicional. chmod/chown mudariam a '
                          'permissão de todo mundo, não só do visitante.'},
  'spec_en': {'scenario': 'You need to grant READ permission to a specific user '
                          '(visitor) on a file, without changing its owner or group.',
              'correct_command': ['setfacl', '-m', 'u:visitante:r--', 'config.yml'],
              'distractor_tokens': ['chmod', 'chown', '-R'],
              'explanation': 'ACL (setfacl) adds permission for a specific user '
                             'without touching the traditional owner/group. '
                             'chmod/chown would change permission for everyone, not '
                             'just the visitor.'}},
 {'topic_title': 'Redes de Computadores',
  'kind': 'terminal',
  'title': 'Resolva o nome',
  'title_en': 'Resolve the name',
  'spec': {'scenario': 'Descubra rapidamente pra qual IP o nome exemplo.com resolve, '
                       'sem ruído extra na saída.',
           'correct_command': ['dig', '+short', 'exemplo.com'],
           'accepted_commands': [['dig', 'exemplo.com', '+short']],
           'distractor_tokens': ['ping', '-c', 'nslookup'],
           'explanation': '`dig +short` retorna só o IP, direto ao ponto. `ping` testa '
                          'conectividade (não é resolução pura); `nslookup` funciona '
                          'mas está deprecado em favor de `dig`.'},
  'spec_en': {'scenario': 'Quickly find which IP the name exemplo.com resolves to, '
                          'without extra noise in the output.',
              'correct_command': ['dig', '+short', 'exemplo.com'],
              'accepted_commands': [['dig', 'exemplo.com', '+short']],
              'distractor_tokens': ['ping', '-c', 'nslookup'],
              'explanation': '`dig +short` returns only the IP, straight to the point. '
                             '`ping` tests connectivity (not pure resolution); '
                             '`nslookup` works but is deprecated in favor of `dig`.'}},
 {'topic_title': 'Bash/Shell Scripting',
  'kind': 'find_flaw',
  'title': 'Ache o bug do loop',
  'title_en': 'Find the loop bug',
  'spec': {'scenario': 'Este script apaga arquivos .txt de um diretório, mas quebra '
                       'com nome de arquivo que tem espaço. Ache a linha do bug.',
           'lines': ['#!/bin/bash',
                     'for f in $(ls *.txt)',
                     'do  # inicialização de rotina',
                     '  rm $f',
                     'done'],
           'flaw_line_index': 1,
           'explanation': '`$(ls *.txt)` sem aspas sofre word splitting: um arquivo '
                          'chamado "relatório final.txt" vira dois argumentos '
                          'separados. O jeito certo é `for f in *.txt` (glob direto do '
                          'shell, sem `ls`).'},
  'spec_en': {'scenario': 'This script deletes .txt files from a directory, but breaks '
                          'on filenames that contain spaces. Find the buggy line.',
              'lines': ['#!/bin/bash',
                        'for f in $(ls *.txt)',
                        'do  # routine initialization',
                        '  rm $f',
                        'done'],
              'flaw_line_index': 1,
              'explanation': '`$(ls *.txt)` without quotes suffers word splitting: a '
                             'file named "final report.txt" becomes two separate '
                             'arguments. The right way is `for f in *.txt` (shell glob '
                             'directly, without `ls`).'}},
 {'topic_title': 'SSH & Chaves Criptográficas',
  'kind': 'terminal',
  'title': 'Gere as chaves',
  'title_en': 'Generate the keys',
  'spec': {'scenario': 'Gere um novo par de chaves SSH usando o algoritmo moderno '
                       'recomendado (Ed25519, mais rápido e seguro que RSA).',
           'correct_command': ['ssh-keygen', '-t', 'ed25519'],
           'distractor_tokens': ['rsa', '-b', '4096'],
           'explanation': '`-t ed25519` escolhe o algoritmo moderno. RSA ainda '
                          'funciona, mas exige chave maior (4096 bits) pra segurança '
                          'equivalente e é mais lento pra gerar e verificar.'},
  'spec_en': {'scenario': 'Generate a new SSH key pair using the modern recommended '
                          'algorithm (Ed25519, faster and more secure than RSA).',
              'correct_command': ['ssh-keygen', '-t', 'ed25519'],
              'distractor_tokens': ['rsa', '-b', '4096'],
              'explanation': '`-t ed25519` selects the modern algorithm. RSA still '
                             'works, but needs a larger key (4096 bits) for equivalent '
                             'security and is slower to generate and verify.'}},
 {'topic_title': 'Princípio do Privilégio Mínimo (PoLP)',
  'kind': 'find_flaw',
  'title': 'Ache a permissão exagerada',
  'title_en': 'Find the excessive permission',
  'spec': {'scenario': 'Esta política IAM deveria permitir só a leitura de objetos de '
                       'um bucket. Ache a linha que viola o PoLP.',
           'lines': ['{',
                     '  "Effect": "Allow",',
                     '  "Action": "s3:*",',
                     '  "Resource": "arn:aws:s3:::meu-bucket/*"',
                     '}'],
           'flaw_line_index': 2,
           'explanation': '`s3:*` libera TODA ação do S3 (deletar, sobrescrever, mudar '
                          'permissão), não só ler. O certo seria `s3:GetObject`, a '
                          'ação mínima necessária pro que foi pedido.'},
  'spec_en': {'scenario': 'This IAM policy should only allow reading objects from a '
                          'bucket. Find the line that violates PoLP.',
              'lines': ['{',
                        '  "Effect": "Allow",',
                        '  "Action": "s3:*",',
                        '  "Resource": "arn:aws:s3:::meu-bucket/*"',
                        '}'],
              'flaw_line_index': 2,
              'explanation': '`s3:*` grants EVERY S3 action (delete, overwrite, change '
                             'permission), not just read. The correct action would be '
                             '`s3:GetObject`, the minimum needed for what was '
                             'requested.'}},
 {'topic_title': 'Firewall Básico',
  'kind': 'blanks',
  'title': 'Feche a porta certa',
  'title_en': 'Open the right port',
  'spec': {'scenario': 'Configure o firewall pra negar tudo por padrão e liberar só a '
                       'porta do SSH.',
           'template': 'ufw default ___POLICY___\nufw allow ___PORT___/tcp',
           'blanks': {'POLICY': {'options': ['deny', 'allow'], 'correct': 'deny'},
                      'PORT': {'options': ['22', '3389', '23'], 'correct': '22'}},
           'explanation': 'Política padrão DENY é a base de um firewall seguro: só '
                          'passa o que foi explicitamente liberado. 22 é a porta do '
                          'SSH; 3389 é RDP (Windows) e 23 é Telnet (sem criptografia, '
                          'evite).'},
  'spec_en': {'scenario': 'Configure the firewall to deny everything by default and '
                          'allow only the SSH port.',
              'template': 'ufw default ___POLICY___\nufw allow ___PORT___/tcp',
              'blanks': {'POLICY': {'options': ['deny', 'allow'], 'correct': 'deny'},
                         'PORT': {'options': ['22', '3389', '23'], 'correct': '22'}},
              'explanation': 'A default DENY policy is the foundation of a secure '
                             'firewall: only what was explicitly allowed gets through. '
                             '22 is the SSH port; 3389 is RDP (Windows) and 23 is '
                             'Telnet (unencrypted, avoid).'}},
 {'topic_title': 'Web Servers (Nginx/Apache)',
  'kind': 'find_flaw',
  'title': 'Ache a config exposta',
  'title_en': 'Find the exposed config',
  'spec': {'scenario': 'Este bloco do Nginx tem uma configuração que ajuda um atacante '
                       'a mirar exploits conhecidos da versão exata do servidor.',
           'lines': ['server {',
                     '  listen 443 ssl;',
                     '  server_tokens on;',
                     '  ssl_certificate /etc/ssl/cert.pem;',
                     '}'],
           'flaw_line_index': 2,
           'explanation': '`server_tokens on` inclui a versão exata do Nginx no header '
                          '`Server` de toda resposta — informação de graça pra quem '
                          'procura CVE daquela versão específica. Configuração '
                          'recomendada: `off`.'},
  'spec_en': {'scenario': 'This Nginx block has a setting that helps an attacker '
                          'target known exploits for the exact server version.',
              'lines': ['server {',
                        '  listen 443 ssl;',
                        '  server_tokens on;',
                        '  ssl_certificate /etc/ssl/cert.pem;',
                        '}'],
              'flaw_line_index': 2,
              'explanation': '`server_tokens on` includes the exact Nginx version in '
                             'the `Server` header of every response — free information '
                             'for anyone hunting CVEs for that specific version. '
                             'Recommended setting: `off`.'}},
 {'topic_title': 'Gestão de Pacotes e Repositórios',
  'kind': 'order',
  'title': 'Instale com segurança',
  'title_en': 'Install safely',
  'spec': {'scenario': 'Ordene os passos corretos pra instalar um pacote garantindo '
                       'que veio de um índice atualizado.',
           'steps_shuffled': ['apt list --installed | grep pacote',
                              'apt install pacote',
                              'apt update'],
           'correct_order': ['apt update',
                             'apt install pacote',
                             'apt list --installed | grep pacote'],
           'explanation': '`update` primeiro sincroniza o índice de pacotes '
                          'disponíveis (sem isso você pode instalar uma versão '
                          'desatualizada ou já removida do espelho). Verificar depois '
                          'confirma que instalou.'},
  'spec_en': {'scenario': 'Order the correct steps to install a package ensuring it '
                          'comes from an up-to-date index.',
              'steps_shuffled': ['apt list --installed | grep pacote',
                                 'apt install pacote',
                                 'apt update'],
              'correct_order': ['apt update',
                                'apt install pacote',
                                'apt list --installed | grep pacote'],
              'explanation': '`update` first syncs the available package index '
                             '(without it you may install an outdated version or one '
                             'already removed from the mirror). Verifying afterward '
                             'confirms the install.'}},
 {'topic_title': 'Log Management',
  'kind': 'terminal',
  'title': 'Ache os erros de hoje',
  'title_en': "Find today's errors",
  'spec': {'scenario': 'Usando journalctl, veja só as mensagens de erro (ou pior) '
                       'registradas hoje.',
           'correct_command': ['journalctl', '-p', 'err', '-S', 'today'],
           'accepted_commands': [['journalctl', '-S', 'today', '-p', 'err']],
           'distractor_tokens': ['-u', 'nginx'],
           'explanation': '`-p err` filtra por prioridade (erro ou mais grave); `-S '
                          'today` limita ao dia atual. `-u nginx` filtraria por '
                          'serviço específico — útil, mas não foi pedido aqui.'},
  'spec_en': {'scenario': 'Using journalctl, show only error messages (or worse) '
                          'logged today.',
              'correct_command': ['journalctl', '-p', 'err', '-S', 'today'],
              'accepted_commands': [['journalctl', '-S', 'today', '-p', 'err']],
              'distractor_tokens': ['-u', 'nginx'],
              'explanation': '`-p err` filters by priority (error or more severe); `-S '
                             'today` limits to the current day. `-u nginx` would '
                             'filter by a specific service — useful, but not what was '
                             'asked here.'}},
 {'topic_title': 'Cultura DevSecOps',
  'kind': 'scenario',
  'title': 'CVE a 10 minutos do deploy',
  'title_en': 'CVE 10 minutes before deploy',
  'spec': {'situation': 'O SCA aponta uma CVE crítica numa dependência, 10 minutos '
                        'antes do deploy de sexta-feira que o time já estava '
                        'esperando.',
           'choices': [{'text': 'Faz o deploy assim mesmo e corrige na próxima semana.',
                        'outcome': 'A CVE fica explorável em produção o fim de semana '
                                   'inteiro, sem ninguém de plantão acompanhando de '
                                   'perto.',
                        'good': False},
                       {'text': 'Bloqueia o deploy e aciona quem puder corrigir agora.',
                        'outcome': 'O deploy atrasa, mas a falha crítica é fechada '
                                   'antes de qualquer exposição real.',
                        'good': True}],
           'explanation': 'Cultura DevSecOps trata segurança como parte do "pronto", '
                          'não como etapa opcional que dá pra empurrar quando aperta o '
                          'prazo — sobretudo numa CVE crítica.'},
  'spec_en': {'situation': 'SCA flags a critical CVE in a dependency, 10 minutes '
                           'before the Friday deploy the team was already waiting for.',
              'choices': [{'text': 'Ship the deploy anyway and fix it next week when '
                                   'things are calmer.',
                           'outcome': 'The CVE stays exploitable in production all '
                                      'weekend, with no one on call watching closely.',
                           'good': False},
                          {'text': 'Block the deploy and get whoever can fix it '
                                   'involved now.',
                           'outcome': 'The deploy slips, but the critical flaw is '
                                      'closed before any real exposure.',
                           'good': True}],
              'explanation': 'DevSecOps culture treats security as part of "done", not '
                             'an optional step you can push when the deadline is tight '
                             '— especially with a critical CVE.'}},
 {'topic_title': 'Virtualização vs. Cloud',
  'kind': 'scenario',
  'title': 'Kernel incompatível',
  'title_en': 'Incompatible kernel',
  'spec': {'situation': 'Uma aplicação legada só funciona com um kernel Linux 3.x '
                        'específico, incompatível com o kernel do host moderno.',
           'choices': [{'text': 'Roda a aplicação isolada dentro de um container '
                                'comum.',
                        'outcome': 'Falha: o container compartilha o kernel do host, '
                                   'não traz um kernel próprio junto.',
                        'good': False},
                       {'text': 'Roda a aplicação numa máquina virtual.',
                        'outcome': 'Funciona: o hypervisor dá à VM seu próprio kernel, '
                                   'isolado do host.',
                        'good': True}],
           'explanation': 'Container é isolamento de processo sobre o MESMO kernel; '
                          'quando a dependência é o kernel em si, só a virtualização '
                          'completa (VM) resolve.'},
  'spec_en': {'situation': 'A legacy application only works with a specific Linux 3.x '
                           'kernel, incompatible with the modern host kernel.',
              'choices': [{'text': 'Run the application isolated inside a regular '
                                   'container on the host.',
                           'outcome': 'Fails: the container shares the host kernel and '
                                      'does not bring its own.',
                           'good': False},
                          {'text': 'Run the application inside a virtual machine '
                                   'instead.',
                           'outcome': 'Works: the hypervisor gives the VM its own '
                                      'kernel, isolated from the host.',
                           'good': True}],
              'explanation': 'A container is process isolation on the SAME kernel; '
                             'when the dependency is the kernel itself, only full '
                             'virtualization (VM) solves it.'}},
 {'topic_title': 'Shared Responsibility Model',
  'kind': 'find_flaw',
  'title': 'De quem é a culpa?',
  'title_en': 'Whose fault is it?',
  'spec': {'scenario': 'Uma dessas quatro responsabilidades está atribuída à pessoa '
                       'errada. Ache qual.',
           'lines': ['Cliente configura as regras de IAM.',
                     'Provedor aplica patch no hypervisor.',
                     'Cliente aplica patch no hypervisor.',
                     'Cliente configura o security group.'],
           'flaw_line_index': 2,
           'explanation': 'O hypervisor é infraestrutura do PROVEDOR — o cliente nunca '
                          'tem acesso pra sequer tentar aplicar patch nele. IAM e '
                          'security group são configuração, sempre do lado do '
                          'cliente.'},
  'spec_en': {'scenario': 'One of these four responsibilities is assigned to the wrong '
                          'party. Find which.',
              'lines': ['Customer configures the IAM rules.',
                        'Provider applies patches to the hypervisor.',
                        'Customer applies patches to the hypervisor.',
                        'Customer configures the security group.'],
              'flaw_line_index': 2,
              'explanation': "The hypervisor is the PROVIDER's infrastructure — the "
                             'customer never has access to even try patching it. IAM '
                             'and security group are configuration, always on the '
                             'customer side.'}},
 {'topic_title': 'IAM (Identity and Access Management)',
  'kind': 'blanks',
  'title': 'Política mínima',
  'title_en': 'Minimum policy',
  'spec': {'scenario': 'Dê a um serviço só a permissão de LER objetos de UM bucket '
                       'específico, seguindo o PoLP.',
           'template': '{\n'
                       '  "Effect": "Allow",\n'
                       '  "Action": "___ACTION___",\n'
                       '  "Resource": "___RESOURCE___"\n'
                       '}',
           'blanks': {'ACTION': {'options': ['s3:GetObject', 's3:*', '*'],
                                 'correct': 's3:GetObject'},
                      'RESOURCE': {'options': ['arn:aws:s3:::meu-bucket/*',
                                               '*',
                                               'arn:aws:s3:::*'],
                                   'correct': 'arn:aws:s3:::meu-bucket/*'}},
           'explanation': 'Ação específica (`GetObject`, não `s3:*`) e recurso '
                          'restrito a UM bucket (não `*`, que libera todos) é o PoLP '
                          'na prática: o mínimo necessário, nada além.'},
  'spec_en': {'scenario': 'Give a service only the permission to READ objects from ONE '
                          'specific bucket, following PoLP.',
              'template': '{\n'
                          '  "Effect": "Allow",\n'
                          '  "Action": "___ACTION___",\n'
                          '  "Resource": "___RESOURCE___"\n'
                          '}',
              'blanks': {'ACTION': {'options': ['s3:GetObject', 's3:*', '*'],
                                    'correct': 's3:GetObject'},
                         'RESOURCE': {'options': ['arn:aws:s3:::meu-bucket/*',
                                                  '*',
                                                  'arn:aws:s3:::*'],
                                      'correct': 'arn:aws:s3:::meu-bucket/*'}},
              'explanation': 'A specific action (`GetObject`, not `s3:*`) and a '
                             'resource limited to ONE bucket (not `*`, which opens '
                             'all) is PoLP in practice: the minimum necessary, nothing '
                             'more.'}},
 {'topic_title': 'VPC & Subnets',
  'kind': 'order',
  'title': 'O caminho do pacote',
  'title_en': 'The packet path',
  'spec': {'scenario': 'Ordene o caminho que um pacote percorre saindo de uma '
                       'instância PRIVADA até a internet.',
           'steps_shuffled': ['Internet Gateway',
                              'Instância na subnet privada',
                              'Internet',
                              'NAT Gateway na subnet pública'],
           'correct_order': ['Instância na subnet privada',
                             'NAT Gateway na subnet pública',
                             'Internet Gateway',
                             'Internet'],
           'explanation': 'Instância privada não tem IP público: ela sai pelo NAT '
                          'Gateway (que fica numa subnet pública), que por sua vez sai '
                          'pelo Internet Gateway da VPC.'},
  'spec_en': {'scenario': 'Order the path a packet takes leaving a PRIVATE instance '
                          'toward the internet.',
              'steps_shuffled': ['Internet Gateway',
                                 'Instance in the private subnet',
                                 'Internet',
                                 'NAT Gateway in the public subnet'],
              'correct_order': ['Instance in the private subnet',
                                'NAT Gateway in the public subnet',
                                'Internet Gateway',
                                'Internet'],
              'explanation': 'A private instance has no public IP: it exits through '
                             'the NAT Gateway (which sits in a public subnet), which '
                             "in turn exits through the VPC's Internet Gateway."}},
 {'topic_title': 'Security Groups & ACLs',
  'kind': 'scenario',
  'title': 'Faltou a volta',
  'title_en': 'Missing the return path',
  'spec': {'situation': 'Você libera a porta 443 de ENTRADA numa Network ACL '
                        '(stateless). A resposta do servidor sai sem problema?',
           'choices': [{'text': 'Sim, a NACL libera o tráfego de saída '
                                'automaticamente.',
                        'outcome': 'Errado: NACL é stateless, ela não lembra da '
                                   'conexão de entrada pra liberar a volta sozinha.',
                        'good': False},
                       {'text': 'Não, precisa de uma regra de SAÍDA própria também.',
                        'outcome': 'Certo: diferente do Security Group (stateful), a '
                                   'NACL exige regra explícita nos dois sentidos.',
                        'good': True}],
           'explanation': 'Security Group lembra da conexão (stateful): libera '
                          'entrada, a resposta sai de graça. Network ACL não lembra '
                          '(stateless): cada sentido precisa da própria regra.'},
  'spec_en': {'situation': 'You allow inbound port 443 on a Network ACL (stateless). '
                           "Does the server's response go out without issues?",
              'choices': [{'text': 'Yes, the NACL automatically allows the outbound '
                                   'return traffic.',
                           'outcome': 'Wrong: NACLs are stateless; they do not '
                                      'remember the inbound connection to allow the '
                                      'return on their own.',
                           'good': False},
                          {'text': 'No, you also need an explicit outbound rule of '
                                   'your own.',
                           'outcome': 'Correct: unlike a Security Group (stateful), a '
                                      'NACL requires an explicit rule in both '
                                      'directions.',
                           'good': True}],
              'explanation': 'A Security Group remembers the connection (stateful): '
                             'allow inbound, and the reply goes out for free. A '
                             'Network ACL does not remember (stateless): each '
                             'direction needs its own rule.'}},
 {'topic_title': 'Object Storage (S3)',
  'kind': 'terminal',
  'title': 'Liste o bucket',
  'title_en': 'List the bucket',
  'spec': {'scenario': 'Liste todos os objetos dentro de um bucket S3 usando o CLI da '
                       'AWS.',
           'correct_command': ['aws', 's3', 'ls', 's3://meu-bucket'],
           'distractor_tokens': ['cp', '--recursive'],
           'explanation': '`aws s3 ls s3://bucket` lista o conteúdo. `cp --recursive` '
                          'serve pra COPIAR uma árvore inteira, não pra listar.'},
  'spec_en': {'scenario': 'List all objects inside an S3 bucket using the AWS CLI.',
              'correct_command': ['aws', 's3', 'ls', 's3://meu-bucket'],
              'distractor_tokens': ['cp', '--recursive'],
              'explanation': '`aws s3 ls s3://bucket` lists the contents. `cp '
                             '--recursive` is for COPYING an entire tree, not '
                             'listing.'}},
 {'topic_title': 'Criptografia em Repouso e Trânsito',
  'kind': 'find_flaw',
  'title': 'Ache o backup exposto',
  'title_en': 'Find the exposed backup',
  'spec': {'scenario': 'Destas quatro práticas de segurança, uma delas deixa dado '
                       'sensível vulnerável em repouso. Ache qual.',
           'lines': ['Certificado TLS 1.3 configurado no load balancer.',
                     'Backup do banco de dados sem criptografia.',
                     'Chave do KMS rotacionada anualmente.',
                     'HSTS habilitado no servidor web.'],
           'flaw_line_index': 1,
           'explanation': 'TLS e HSTS protegem o dado EM TRÂNSITO; a chave de KMS '
                          'protege o dado em repouso — mas um backup sem criptografia '
                          'nenhuma deixa tudo exposto pra quem tiver acesso ao arquivo '
                          'físico.'},
  'spec_en': {'scenario': 'Of these four security practices, one leaves sensitive data '
                          'vulnerable at rest. Find which.',
              'lines': ['TLS 1.3 certificate configured on the load balancer.',
                        'Database backup with no encryption at all.',
                        'KMS key rotated on an annual schedule.',
                        'HSTS enabled on the web server configuration.'],
              'flaw_line_index': 1,
              'explanation': 'TLS and HSTS protect data IN TRANSIT; the KMS key '
                             'protects data at rest — but a backup with no encryption '
                             'at all leaves everything exposed to whoever has access '
                             'to the physical file.'}},
 {'topic_title': 'Monitoramento Básico (CloudWatch/Monitor)',
  'kind': 'blanks',
  'title': 'Configure o alarme',
  'title_en': 'Configure the alarm',
  'spec': {'scenario': 'Configure um alarme que dispara quando a CPU fica ALTA por '
                       'tempo prolongado.',
           'template': 'Alarm: CPUUtilization ___OP___ ___THRESHOLD___% por 5 minutos '
                       '→ dispara',
           'blanks': {'OP': {'options': ['>', '<', '='], 'correct': '>'},
                      'THRESHOLD': {'options': ['80', '10', '100'], 'correct': '80'}},
           'explanation': 'Alarme de CPU alta usa `>` com um limiar realista (80%) — '
                          '100% raramente é sustentado por 5 minutos inteiros sem já '
                          'ter causado impacto visível, e 10% seria alarme falso '
                          'constante.'},
  'spec_en': {'scenario': 'Configure an alarm that fires when CPU stays HIGH for a '
                          'prolonged time.',
              'template': 'Alarm: CPUUtilization ___OP___ ___THRESHOLD___% for 5 '
                          'minutes → fires',
              'blanks': {'OP': {'options': ['>', '<', '='], 'correct': '>'},
                         'THRESHOLD': {'options': ['80', '10', '100'],
                                       'correct': '80'}},
              'explanation': 'A high-CPU alarm uses `>` with a realistic threshold '
                             '(80%) — 100% is rarely sustained for a full 5 minutes '
                             'without already causing visible impact, and 10% would be '
                             'constant false alarms.'}},
 {'topic_title': 'Backup & Disaster Recovery',
  'kind': 'order',
  'title': 'Depois do desastre',
  'title_en': 'After the disaster',
  'spec': {'scenario': 'Ordene os passos de um ciclo saudável de disaster recovery.',
           'steps_shuffled': ['Serviço volta a operar',
                              'Postmortem documenta RPO/RTO reais',
                              'Backup automatizado diário',
                              'Incidente derruba o serviço',
                              'Restaura o backup mais recente'],
           'correct_order': ['Backup automatizado diário',
                             'Incidente derruba o serviço',
                             'Restaura o backup mais recente',
                             'Serviço volta a operar',
                             'Postmortem documenta RPO/RTO reais'],
           'explanation': 'Backup precisa existir ANTES do incidente pra servir de '
                          'algo. Depois de restaurar e voltar a operar, o postmortem '
                          'mede se o RPO/RTO prometidos bateram com o que aconteceu de '
                          'verdade.'},
  'spec_en': {'scenario': 'Order the steps of a healthy disaster recovery cycle.',
              'steps_shuffled': ['Service returns to operation',
                                 'Postmortem documents actual RPO/RTO',
                                 'Automated daily backup',
                                 'Incident takes the service down',
                                 'Restore the most recent backup'],
              'correct_order': ['Automated daily backup',
                                'Incident takes the service down',
                                'Restore the most recent backup',
                                'Service returns to operation',
                                'Postmortem documents actual RPO/RTO'],
              'explanation': 'Backup must exist BEFORE the incident to be of any use. '
                             'After restoring and returning to operation, the '
                             'postmortem measures whether the promised RPO/RTO matched '
                             'what actually happened.'}},
 {'topic_title': 'FinOps Inicial',
  'kind': 'scenario',
  'title': 'A instância ociosa',
  'title_en': 'The idle instance',
  'spec': {'situation': 'O dashboard de custo mostra uma instância rodando 24/7 com 5% '
                        'de uso médio de CPU nos últimos 30 dias.',
           'choices': [{'text': 'Deixa a instância rodando do jeito que está, porque '
                                'pode precisar dela de novo em breve.',
                        'outcome': 'O custo mensal segue alto por uma capacidade que '
                                   'ninguém está usando.',
                        'good': False},
                       {'text': 'Redimensiona pra um tipo menor ou desliga fora do '
                                'horário de uso.',
                        'outcome': 'O custo cai proporcionalmente, sem perder a '
                                   'capacidade que de fato é usada.',
                        'good': True}],
           'explanation': 'FinOps é visibilidade virando ação: achar o recurso ocioso '
                          'é só metade do trabalho, a outra metade é realmente '
                          'ajustar.'},
  'spec_en': {'situation': 'The cost dashboard shows an instance running 24/7 with 5% '
                           'average CPU usage over the last 30 days.',
              'choices': [{'text': 'Leave the instance running as-is, because you '
                                   'might need it again soon enough.',
                           'outcome': 'Monthly cost stays high for capacity that '
                                      'nobody is actually using.',
                           'good': False},
                          {'text': 'Downsize to a smaller type or shut it off outside '
                                   'usage hours.',
                           'outcome': 'Cost drops proportionally, without losing the '
                                      'capacity that is actually used.',
                           'good': True}],
              'explanation': 'FinOps is visibility turning into action: finding the '
                             'idle resource is only half the job; the other half is '
                             'actually adjusting it.'}},
 {'topic_title': 'Versionamento com Git',
  'kind': 'terminal',
  'title': 'Nova feature, nova branch',
  'title_en': 'New feature, new branch',
  'spec': {'scenario': "Crie uma branch nova chamada 'feature' e já mude pra ela, num "
                       'comando só.',
           'correct_command': ['git', 'checkout', '-b', 'feature'],
           'distractor_tokens': ['branch', 'merge'],
           'explanation': '`checkout -b` cria E muda de branch num comando. `git '
                          'branch` sozinho só criaria, sem trocar; `merge` é pra '
                          'juntar branches, não criar uma nova.'},
  'spec_en': {'scenario': "Create a new branch called 'feature' and switch to it, in a "
                          'single command.',
              'correct_command': ['git', 'checkout', '-b', 'feature'],
              'distractor_tokens': ['branch', 'merge'],
              'explanation': '`checkout -b` creates AND switches branch in one '
                             'command. `git branch` alone would only create it, '
                             'without switching; `merge` is for joining branches, not '
                             'creating a new one.'}},
 {'topic_title': 'Infraestrutura como Código (Terraform)',
  'kind': 'order',
  'title': 'Do plano ao apply',
  'title_en': 'From plan to apply',
  'spec': {'scenario': 'Ordene o fluxo seguro de uma mudança de infraestrutura via '
                       'Terraform.',
           'steps_shuffled': ['terraform apply',
                              'Escreve ou edita o .tf',
                              'Revisa o diff mostrado',
                              'terraform plan'],
           'correct_order': ['Escreve ou edita o .tf',
                             'terraform plan',
                             'Revisa o diff mostrado',
                             'terraform apply'],
           'explanation': '`plan` mostra o que vai mudar SEM aplicar — pular a revisão '
                          'do diff e ir direto pro `apply` é como assinar um contrato '
                          'sem ler.'},
  'spec_en': {'scenario': 'Order the safe flow for an infrastructure change via '
                          'Terraform.',
              'steps_shuffled': ['terraform apply',
                                 'Write or edit the .tf',
                                 'Review the shown diff',
                                 'terraform plan'],
              'correct_order': ['Write or edit the .tf',
                                'terraform plan',
                                'Review the shown diff',
                                'terraform apply'],
              'explanation': '`plan` shows what will change WITHOUT applying — '
                             'skipping the diff review and going straight to `apply` '
                             'is like signing a contract without reading it.'}},
 {'topic_title': 'Gestão de Configuração (Ansible)',
  'kind': 'find_flaw',
  'title': 'Ache a senha no playbook',
  'title_en': 'Find the password in the playbook',
  'spec': {'scenario': 'Este playbook Ansible tem um problema de segurança clássico. '
                       'Ache a linha.',
           'lines': ['- name: Instala pacote  # inicialização de rotina',
                     '  apt: name=nginx state=present',
                     '- name: Configura senha do banco',
                     '  lineinfile: line="DB_PASS=supersecreto123"'],
           'flaw_line_index': 3,
           'explanation': 'Senha em texto puro dentro do playbook vai parar no Git, '
                          'visível pra qualquer um com acesso ao repositório. O certo '
                          'é usar Ansible Vault ou um cofre de segredos externo.'},
  'spec_en': {'scenario': 'This Ansible playbook has a classic security problem. Find '
                          'the line.',
              'lines': ['- name: Instala pacote  # routine initialization',
                        '  apt: name=nginx state=present',
                        '- name: Configura senha do banco',
                        '  lineinfile: line="DB_PASS=supersecreto123"'],
              'flaw_line_index': 3,
              'explanation': 'A plaintext password inside the playbook ends up in Git, '
                             'visible to anyone with repo access. The right approach '
                             'is to use Ansible Vault or an external secrets vault.'}},
 {'topic_title': 'Secret Management',
  'kind': 'find_flaw',
  'title': 'Ache a chave exposta',
  'title_en': 'Find the exposed key',
  'spec': {'scenario': 'Este código tem uma credencial exposta de um jeito perigoso. '
                       'Ache a linha.',
           'lines': ['import os',
                     'API_KEY = "sk_live_51H8xJ2KZ..."',
                     "response = requests.get(url, headers={'Authorization': "
                     'API_KEY})'],
           'flaw_line_index': 1,
           'explanation': 'Chave hardcoded no código-fonte vai pro Git, pra qualquer '
                          'clone do repo e pro histórico de commits pra sempre. O '
                          'certo é ler de uma variável de ambiente ou de um cofre de '
                          'segredos.'},
  'spec_en': {'scenario': 'This code has a credential exposed in a dangerous way. Find '
                          'the line.',
              'lines': ['import os',
                        'API_KEY = "sk_live_51H8xJ2KZ..."',
                        "response = requests.get(url, headers={'Authorization': "
                        'API_KEY})'],
              'flaw_line_index': 1,
              'explanation': 'A hardcoded key in source code goes to Git, to every '
                             'clone of the repo, and into commit history forever. The '
                             'right approach is to read it from an environment '
                             'variable or a secrets vault.'}},
 {'topic_title': 'CI/CD Básico',
  'kind': 'order',
  'title': 'Do commit ao deploy',
  'title_en': 'From commit to deploy',
  'spec': {'scenario': 'Ordene as etapas de um pipeline CI/CD básico.',
           'steps_shuffled': ['Deploy', 'Testes automatizados', 'Commit', 'Build'],
           'correct_order': ['Commit', 'Build', 'Testes automatizados', 'Deploy'],
           'explanation': 'Cada etapa só faz sentido depois da anterior: build sem '
                          'commit não tem o que compilar, deploy sem teste não sabe se '
                          'o que vai subir funciona.'},
  'spec_en': {'scenario': 'Order the stages of a basic CI/CD pipeline.',
              'steps_shuffled': ['Deploy', 'Automated tests', 'Commit', 'Build'],
              'correct_order': ['Commit', 'Build', 'Automated tests', 'Deploy'],
              'explanation': 'Each stage only makes sense after the previous one: '
                             'build without commit has nothing to compile; deploy '
                             'without tests does not know whether what is going up '
                             'actually works.'}},
 {'topic_title': 'Linting de Código e IaC',
  'kind': 'find_flaw',
  'title': 'Ache o bucket público',
  'title_en': 'Find the public bucket',
  'spec': {'scenario': 'Um linter de IaC (como tfsec ou checkov) bloquearia este bloco '
                       'Terraform. Ache a linha do problema.',
           'lines': ['resource "aws_s3_bucket" "data" {',
                     '  bucket = "my-bucket-12345"',
                     '  acl    = "public-read"',
                     '}'],
           'flaw_line_index': 2,
           'explanation': '`acl = "public-read"` deixa o bucket legível por qualquer '
                          'um na internet — exatamente o tipo de erro que um linter de '
                          'IaC existe pra pegar antes do `apply`.'},
  'spec_en': {'scenario': 'An IaC linter (like tfsec or checkov) would block this '
                          'Terraform block. Find the problem line.',
              'lines': ['resource "aws_s3_bucket" "data" {',
                        '  bucket = "my-bucket-12345"',
                        '  acl    = "public-read"',
                        '}'],
              'flaw_line_index': 2,
              'explanation': '`acl = "public-read"` makes the bucket readable by '
                             'anyone on the internet — exactly the kind of mistake an '
                             'IaC linter exists to catch before `apply`.'}},
 {'topic_title': 'SAST',
  'kind': 'find_flaw',
  'title': 'Ache a injeção de SQL',
  'title_en': 'Find the SQL injection',
  'spec': {'scenario': 'Um SAST real acusaria esta função. Ache a linha vulnerável.',
           'lines': ['def get_user(request):  # código auxiliar, fora do escopo do '
                     'problema',
                     "    user_id = request.GET['id']",
                     '    query = f"SELECT * FROM users WHERE id = {user_id}"',
                     '    return db.execute(query)'],
           'flaw_line_index': 2,
           'explanation': 'Concatenar input do usuário direto numa query via f-string '
                          'permite SQL Injection (`id=1 OR 1=1`). O certo é usar '
                          'parametrização (`WHERE id = %s`, [user_id]).'},
  'spec_en': {'scenario': 'A real SAST tool would flag this function. Find the '
                          'vulnerable line.',
              'lines': ['def get_user(request):  # helper code, outside the problem '
                        'scope',
                        "    user_id = request.GET['id']",
                        '    query = f"SELECT * FROM users WHERE id = {user_id}"',
                        '    return db.execute(query)'],
              'flaw_line_index': 2,
              'explanation': 'Concatenating user input directly into a query via '
                             'f-string allows SQL Injection (`id=1 OR 1=1`). The right '
                             'approach is parameterization (`WHERE id = %s`, '
                             '[user_id]).'}},
 {'topic_title': 'SCA',
  'kind': 'scenario',
  'title': 'Atualizar dá trabalho',
  'title_en': 'Updating is hard work',
  'spec': {'situation': 'O SCA aponta uma CVE crítica numa lib usada em 12 lugares do '
                        'projeto, mas atualizar ela quebra a API em 3 desses lugares.',
           'choices': [{'text': 'Ignora o alerta, atualizar dá muito trabalho agora.',
                        'outcome': 'A vulnerabilidade crítica continua explorável em '
                                   'produção indefinidamente.',
                        'good': False},
                       {'text': 'Atualiza a lib e corrige os 3 pontos que quebraram.',
                        'outcome': 'Leva mais tempo, mas a CVE crítica é fechada de '
                                   'verdade.',
                        'good': True}],
           'explanation': 'SCA sem ação vira ruído: encontrar a CVE e não corrigir '
                          'porque dá trabalho anula o propósito da ferramenta.'},
  'spec_en': {'situation': 'SCA flags a critical CVE in a library used in 12 places in '
                           'the project, but updating it breaks the API in 3 of those '
                           'places.',
              'choices': [{'text': 'Ignore the alert for now; updating is too much '
                                   'work at the moment.',
                           'outcome': 'The critical vulnerability stays exploitable in '
                                      'production indefinitely.',
                           'good': False},
                          {'text': 'Update the library and fix the 3 places that '
                                   'broke.',
                           'outcome': 'It takes more time, but the critical CVE is '
                                      'actually closed.',
                           'good': True}],
              'explanation': 'SCA without action becomes noise: finding the CVE and '
                             'not fixing it because it is hard work defeats the '
                             'purpose of the tool.'}},
 {'topic_title': 'Code Review',
  'kind': 'scenario',
  'title': 'Confiar sem ler',
  'title_en': 'Trust without reading',
  'spec': {'situation': 'Um PR de um dev sênior chega pra sua revisão. Você não '
                        'entende totalmente uma parte da mudança, mas confia na '
                        'experiência dele.',
           'choices': [{'text': 'Aprova o PR direto, sem comentar, só confiando na '
                                'experiência que o autor já tem.',
                        'outcome': 'Meses depois, um bug sutil justamente naquela '
                                   'parte causa um incidente — que ninguém tinha '
                                   'revisado de verdade.',
                        'good': False},
                       {'text': 'Pergunta e pede pra ele explicar a parte que você não '
                                'entendeu.',
                        'outcome': 'A conversa revela um edge case não tratado, '
                                   'corrigido antes do merge.',
                        'good': True}],
           'explanation': 'Rubber stamp (aprovar sem ler) é mais comum justamente com '
                          'autor sênior — e é aí que mais escapa bug, porque ninguém '
                          'questiona.'},
  'spec_en': {'situation': 'A PR from a senior developer lands for your review. You do '
                           'not fully understand one part of the change, but you trust '
                           'their experience.',
              'choices': [{'text': 'Approve the PR right away, with no comments, just '
                                   "trusting the author's existing experience.",
                           'outcome': 'Months later, a subtle bug right in that part '
                                      'causes an incident — that nobody had truly '
                                      'reviewed.',
                           'good': False},
                          {'text': 'Ask questions and request an explanation of the '
                                   'part you did not understand.',
                           'outcome': 'The conversation reveals an untreated edge '
                                      'case, fixed before the merge.',
                           'good': True}],
              'explanation': 'Rubber-stamping (approving without reading) is most '
                             'common with senior authors — and that is exactly where '
                             'bugs slip through, because nobody questions them.'}},
 {'topic_title': 'Artifact Repositories',
  'kind': 'terminal',
  'title': 'Assine o artefato',
  'title_en': 'Sign the artifact',
  'spec': {'scenario': 'Assine uma imagem de container recém publicada usando Cosign, '
                       'pra provar sua origem.',
           'correct_command': ['cosign', 'sign', 'imagem:tag'],
           'distractor_tokens': ['verify', '--yes'],
           'explanation': '`cosign sign` assina o artefato. `cosign verify` faria o '
                          'inverso: checar uma assinatura já existente.'},
  'spec_en': {'scenario': 'Sign a newly published container image using Cosign, to '
                          'prove its origin.',
              'correct_command': ['cosign', 'sign', 'imagem:tag'],
              'distractor_tokens': ['verify', '--yes'],
              'explanation': '`cosign sign` signs the artifact. `cosign verify` would '
                             'do the inverse: check an already existing signature.'}},
 {'topic_title': 'Docker Fundamentals',
  'kind': 'order',
  'title': 'Do Dockerfile ao container',
  'title_en': 'From Dockerfile to container',
  'spec': {'scenario': 'Ordene o fluxo básico de empacotar e rodar uma aplicação com '
                       'Docker.',
           'steps_shuffled': ['docker run app',
                              'Escreve o Dockerfile',
                              'docker build -t app .'],
           'correct_order': ['Escreve o Dockerfile',
                             'docker build -t app .',
                             'docker run app'],
           'explanation': 'O Dockerfile descreve como construir a imagem; `build` gera '
                          'a imagem a partir dele; `run` cria e inicia um container a '
                          'partir da imagem já construída.'},
  'spec_en': {'scenario': 'Order the basic flow of packaging and running an '
                          'application with Docker.',
              'steps_shuffled': ['docker run app',
                                 'Write the Dockerfile',
                                 'docker build -t app .'],
              'correct_order': ['Write the Dockerfile',
                                'docker build -t app .',
                                'docker run app'],
              'explanation': 'The Dockerfile describes how to build the image; `build` '
                             'produces the image from it; `run` creates and starts a '
                             'container from the already built image.'}},
 {'topic_title': 'Segurança de Imagens',
  'kind': 'find_flaw',
  'title': 'Ache o root desnecessário',
  'title_en': 'Find the unnecessary root',
  'spec': {'scenario': 'Este Dockerfile tem uma prática de segurança ruim. Ache a '
                       'linha.',
           'lines': ['FROM python:3.12',
                     'COPY . /app',
                     'RUN pip install -r requirements.txt',
                     'USER root',
                     'CMD ["python", "app.py"]'],
           'flaw_line_index': 3,
           'explanation': 'Rodar como root dentro do container amplia MUITO o impacto '
                          'de qualquer vulnerabilidade explorada lá dentro. O ideal é '
                          'criar um usuário sem privilégio e usar `USER` com ele.'},
  'spec_en': {'scenario': 'This Dockerfile has a poor security practice. Find the '
                          'line.',
              'lines': ['FROM python:3.12',
                        'COPY . /app',
                        'RUN pip install -r requirements.txt',
                        'USER root',
                        'CMD ["python", "app.py"]'],
              'flaw_line_index': 3,
              'explanation': 'Running as root inside the container greatly amplifies '
                             'the impact of any vulnerability exploited there. The '
                             'ideal is to create an unprivileged user and use `USER` '
                             'with that account.'}},
 {'topic_title': 'Container Registry',
  'kind': 'terminal',
  'title': 'Puxe pelo digest certo',
  'title_en': 'Pull by the right digest',
  'spec': {'scenario': 'Puxe uma imagem garantindo que é EXATAMENTE aquele conteúdo, '
                       'imutável, não uma tag que pode mudar.',
           'correct_command': ['docker', 'pull', 'app@sha256:abc123'],
           'distractor_tokens': ['app:latest', 'docker push'],
           'explanation': 'Puxar por digest (`@sha256:...`) garante o conteúdo exato e '
                          'imutável. `app:latest` é uma tag móvel: o que ela aponta '
                          'pode mudar amanhã sem aviso.'},
  'spec_en': {'scenario': 'Pull an image ensuring it is EXACTLY that content, '
                          'immutable, not a tag that can change.',
              'correct_command': ['docker', 'pull', 'app@sha256:abc123'],
              'distractor_tokens': ['app:latest', 'docker push'],
              'explanation': 'Pulling by digest (`@sha256:...`) guarantees the exact, '
                             'immutable content. `app:latest` is a moving tag: what it '
                             'points to can change tomorrow without notice.'}},
 {'topic_title': 'Orquestração Simples',
  'kind': 'blanks',
  'title': 'Complete o healthcheck',
  'title_en': 'Complete the healthcheck',
  'spec': {'scenario': 'Complete o docker-compose.yml pra que o Docker saiba verificar '
                       'se o serviço está saudável.',
           'template': 'services:\n'
                       '  app:\n'
                       '    image: app:latest\n'
                       '    depends_on:\n'
                       '      - db\n'
                       '    ___KEY___:\n'
                       '      test: ["CMD", "curl", "-f", "http://localhost/health"]',
           'blanks': {'KEY': {'options': ['healthcheck', 'restart', 'ports'],
                              'correct': 'healthcheck'}},
           'explanation': '`healthcheck` diz ao Docker como testar se o serviço está '
                          'de pé de verdade, não só se o processo iniciou.'},
  'spec_en': {'scenario': 'Complete the docker-compose.yml so Docker knows how to '
                          'verify the service is healthy.',
              'template': 'services:\n'
                          '  app:\n'
                          '    image: app:latest\n'
                          '    depends_on:\n'
                          '      - db\n'
                          '    ___KEY___:\n'
                          '      test: ["CMD", "curl", "-f", '
                          '"http://localhost/health"]',
              'blanks': {'KEY': {'options': ['healthcheck', 'restart', 'ports'],
                                 'correct': 'healthcheck'}},
              'explanation': '`healthcheck` tells Docker how to test whether the '
                             'service is truly up, not just whether the process '
                             'started.'}},
 {'topic_title': 'Software Bill of Materials (SBOM)',
  'kind': 'terminal',
  'title': 'Gere o inventário',
  'title_en': 'Generate the inventory',
  'spec': {'scenario': 'Gere um SBOM de uma imagem de container no formato CycloneDX, '
                       'usando o Syft.',
           'correct_command': ['syft', 'imagem:tag', '-o', 'cyclonedx-json'],
           'accepted_commands': [['syft', '-o', 'cyclonedx-json', 'imagem:tag']],
           'distractor_tokens': ['--scan', 'trivy'],
           'explanation': '`syft <imagem> -o cyclonedx-json` gera o inventário de '
                          'componentes no formato CycloneDX. Trivy é outra ferramenta '
                          '(mais focada em scan de CVE do que em gerar SBOM).'},
  'spec_en': {'scenario': 'Generate an SBOM for a container image in CycloneDX format, '
                          'using Syft.',
              'correct_command': ['syft', 'imagem:tag', '-o', 'cyclonedx-json'],
              'accepted_commands': [['syft', '-o', 'cyclonedx-json', 'imagem:tag']],
              'distractor_tokens': ['--scan', 'trivy'],
              'explanation': '`syft <image> -o cyclonedx-json` generates the component '
                             'inventory in CycloneDX format. Trivy is another tool '
                             '(more focused on CVE scanning than generating an '
                             'SBOM).'}},
 {'topic_title': 'Internal Developer Platforms (IDP)',
  'kind': 'scenario',
  'title': 'Ticket ou self-service?',
  'title_en': 'Ticket or self-service?',
  'spec': {'situation': 'Um dev precisa criar um microsserviço novo, já com CI/CD, '
                        'monitoramento e permissões corretas desde o primeiro dia.',
           'choices': [{'text': 'Abre um ticket separado pra cada time (infra, '
                                'segurança, SRE).',
                        'outcome': 'Leva semanas até tudo estar pronto e consistente '
                                   'entre os times.',
                        'good': False},
                       {'text': 'Usa o template golden path da plataforma interna.',
                        'outcome': 'Em minutos, o serviço nasce com CI/CD, '
                                   'observabilidade e IAM já configurados do jeito '
                                   'certo.',
                        'good': True}],
           'explanation': 'O golden path de uma IDP existe justamente pra eliminar '
                          'essa espera: o caminho recomendado já vem pronto, sem '
                          'depender de vários times manualmente.'},
  'spec_en': {'situation': 'A developer needs to create a new microservice, already '
                           'with CI/CD, monitoring, and correct permissions from day '
                           'one.',
              'choices': [{'text': 'Open a separate ticket for each team (infra, '
                                   'security, SRE) and wait.',
                           'outcome': 'It takes weeks until everything is ready and '
                                      'consistent across teams.',
                           'good': False},
                          {'text': "Use the internal platform's golden path template "
                                   'instead.',
                           'outcome': 'In minutes, the service is born with CI/CD, '
                                      'observability, and IAM already configured the '
                                      'right way.',
                           'good': True}],
              'explanation': 'An IDP golden path exists precisely to eliminate that '
                             'wait: the recommended path comes ready, without '
                             'depending on several teams manually.'}},
 {'topic_title': 'Policy as Code (PaC)',
  'kind': 'find_flaw',
  'title': 'Ache o pod privilegiado',
  'title_en': 'Find the privileged pod',
  'spec': {'scenario': 'Um admission controller com boas políticas bloquearia este '
                       'manifesto. Ache a linha.',
           'lines': ['apiVersion: v1',
                     'kind: Pod',
                     'spec:  # detalhe de implementação sem impacto',
                     '  containers:',
                     '  - name: app',
                     '    image: app:latest',
                     '    securityContext:',
                     '      privileged: true'],
           'flaw_line_index': 7,
           'explanation': '`privileged: true` dá ao container acesso quase irrestrito '
                          'ao host — exatamente o tipo de configuração que uma '
                          'política (OPA/Kyverno) deveria barrar antes de criar o '
                          'recurso.'},
  'spec_en': {'scenario': 'An admission controller with good policies would block this '
                          'manifest. Find the line.',
              'lines': ['apiVersion: v1',
                        'kind: Pod',
                        'spec:  # implementation detail with no impact',
                        '  containers:',
                        '  - name: app',
                        '    image: app:latest',
                        '    securityContext:',
                        '      privileged: true'],
              'flaw_line_index': 7,
              'explanation': '`privileged: true` gives the container nearly '
                             'unrestricted access to the host — exactly the kind of '
                             'configuration a policy (OPA/Kyverno) should block before '
                             'creating the resource.'}},
 {'topic_title': 'DAST inicial',
  'kind': 'order',
  'title': 'Ataque de fora',
  'title_en': 'Attack from the outside',
  'spec': {'scenario': 'Ordene as etapas de um scan DAST contra uma aplicação já '
                       'rodando.',
           'steps_shuffled': ['Reporta a vulnerabilidade encontrada',
                              'Analisa as respostas recebidas',
                              'App sobe em ambiente isolado de staging',
                              'Scanner envia requisições maliciosas'],
           'correct_order': ['App sobe em ambiente isolado de staging',
                             'Scanner envia requisições maliciosas',
                             'Analisa as respostas recebidas',
                             'Reporta a vulnerabilidade encontrada'],
           'explanation': 'DAST precisa da aplicação rodando de verdade (diferente do '
                          'SAST, que lê código parado) — por isso o app precisa estar '
                          'de pé, num ambiente isolado, antes do ataque simulado '
                          'começar.'},
  'spec_en': {'scenario': 'Order the stages of a DAST scan against an already running '
                          'application.',
              'steps_shuffled': ['Report the vulnerability found',
                                 'Analyze the responses received',
                                 'App comes up in an isolated staging environment',
                                 'Scanner sends malicious requests'],
              'correct_order': ['App comes up in an isolated staging environment',
                                'Scanner sends malicious requests',
                                'Analyze the responses received',
                                'Report the vulnerability found'],
              'explanation': 'DAST needs the application actually running (unlike '
                             'SAST, which reads static code) — so the app must be up, '
                             'in an isolated environment, before the simulated attack '
                             'starts.'}},
 {'topic_title': 'API Security',
  'kind': 'find_flaw',
  'title': 'Ache o pedido de outro usuário',
  'title_en': "Find another user's order",
  'spec': {'scenario': 'Este endpoint tem uma falha clássica de BOLA (Broken Object '
                       'Level Authorization). Ache a linha.',
           'lines': ["@app.get('/pedidos/{id}')  # trecho de suporte, sem risco",
                     'def get_pedido(id, user=Depends(get_current_user)):',
                     '    pedido = db.query(Pedido).filter_by(id=id).first()',
                     '    return pedido  # parte normal do fluxo'],
           'flaw_line_index': 2,
           'explanation': 'A query busca o pedido só pelo `id`, sem checar se ele '
                          'pertence ao `user` autenticado. Qualquer usuário logado '
                          'pode ler o pedido de qualquer outro só trocando o id na '
                          'URL.'},
  'spec_en': {'scenario': 'This endpoint has a classic BOLA (Broken Object Level '
                          'Authorization) flaw. Find the line.',
              'lines': ["@app.get('/pedidos/{id}')  # support snippet only, no "
                        'authorization risk here',
                        'def get_pedido(id, user=Depends(get_current_user)):',
                        '    pedido = db.query(Pedido).filter_by(id=id).first()',
                        '    return pedido  # normal part of the happy-path response '
                        'flow'],
              'flaw_line_index': 2,
              'explanation': 'The query fetches the order only by `id`, without '
                             'checking whether it belongs to the authenticated `user`. '
                             "Any logged-in user can read anyone else's order just by "
                             'changing the id in the URL.'}},
 {'topic_title': 'Centralized Logging',
  'kind': 'find_flaw',
  'title': 'Ache o dado sensível no log',
  'title_en': 'Find the sensitive data in the log',
  'spec': {'scenario': 'Uma dessas três linhas de log vai parar num sistema de log '
                       'centralizado com um dado que nunca deveria estar lá. Ache '
                       'qual.',
           'lines': ["logger.info(f'Login: user={user.email}')  # trecho de suporte, "
                     'sem risco',
                     "logger.info(f'Pagamento processado: card={card_number}')",
                     "logger.error('Falha ao conectar no banco')"],
           'flaw_line_index': 1,
           'explanation': 'Número de cartão em log centralizado é dado de altíssima '
                          'sensibilidade (PCI DSS) espalhado por todo sistema que lê '
                          'aquele log — exatamente o tipo de coisa que se mascara '
                          'antes de logar.'},
  'spec_en': {'scenario': 'One of these three log lines will end up in a centralized '
                          'logging system with data that should never be there. Find '
                          'which.',
              'lines': ["logger.info(f'Login: user={user.email}')  # support snippet, "
                        'no risk',
                        "logger.info(f'Pagamento processado: card={card_number}')",
                        "logger.error('Falha ao conectar no banco')"],
              'flaw_line_index': 1,
              'explanation': 'A card number in centralized logs is extremely sensitive '
                             'data (PCI DSS) spread across every system that reads '
                             'that log — exactly the kind of thing you mask before '
                             'logging.'}},
 {'topic_title': 'Introdução ao Kubernetes (K8s)',
  'kind': 'terminal',
  'title': 'Liste os pods',
  'title_en': 'List the pods',
  'spec': {'scenario': "Liste os pods do namespace 'default' no cluster.",
           'correct_command': ['kubectl', 'get', 'pods', '-n', 'default'],
           'accepted_commands': [
               ['kubectl', 'get', '-n', 'default', 'pods'],
               ['kubectl', '-n', 'default', 'get', 'pods'],
           ],
           'distractor_tokens': ['-A', 'describe'],
           'explanation': '`-n default` filtra pro namespace pedido. `-A` listaria de '
                          'TODOS os namespaces; `describe` mostraria detalhe de UM pod '
                          'específico, não a lista.'},
  'spec_en': {'scenario': "List the pods in the 'default' namespace on the cluster.",
              'correct_command': ['kubectl', 'get', 'pods', '-n', 'default'],
              'accepted_commands': [
                  ['kubectl', 'get', '-n', 'default', 'pods'],
                  ['kubectl', '-n', 'default', 'get', 'pods'],
              ],
              'distractor_tokens': ['-A', 'describe'],
              'explanation': '`-n default` filters to the requested namespace. `-A` '
                             'would list ALL namespaces; `describe` would show detail '
                             'for ONE specific pod, not the list.'}},
 {'topic_title': 'K8s Hardening',
  'kind': 'find_flaw',
  'title': 'Ache o container arriscado',
  'title_en': 'Find the risky container',
  'spec': {'scenario': 'Este manifesto tem uma configuração que um cluster hardened '
                       'não deveria permitir. Ache a linha.',
           'lines': ['apiVersion: v1',
                     'kind: Pod',
                     'spec:  # linha comum de configuração',
                     '  containers:',
                     '  - name: app',
                     '    securityContext:',
                     '      runAsNonRoot: false'],
           'flaw_line_index': 6,
           'explanation': '`runAsNonRoot: false` permite explicitamente que o '
                          'container rode como root — o oposto do hardening '
                          'recomendado, que exige `true` por padrão em qualquer '
                          'PodSecurity policy séria.'},
  'spec_en': {'scenario': 'This manifest has a configuration a hardened cluster should '
                          'not allow. Find the line.',
              'lines': ['apiVersion: v1',
                        'kind: Pod',
                        'spec:  # common configuration line',
                        '  containers:',
                        '  - name: app',
                        '    securityContext:',
                        '      runAsNonRoot: false'],
              'flaw_line_index': 6,
              'explanation': '`runAsNonRoot: false` explicitly allows the container to '
                             'run as root — the opposite of recommended hardening, '
                             'which requires `true` by default in any serious '
                             'PodSecurity policy.'}},
 {'topic_title': 'Network Policies',
  'kind': 'blanks',
  'title': 'Negue por padrão',
  'title_en': 'Deny by default',
  'spec': {'scenario': 'Complete a NetworkPolicy que bloqueia todo tráfego de ENTRADA '
                       'por padrão num namespace.',
           'template': 'kind: NetworkPolicy\n'
                       'spec:\n'
                       '  podSelector: {}\n'
                       '  policyTypes:\n'
                       '  - ___TYPE___',
           'blanks': {'TYPE': {'options': ['Ingress', 'Egress', 'Both'],
                               'correct': 'Ingress'}},
           'explanation': '`podSelector: {}` seleciona TODOS os pods do namespace; sem '
                          'nenhuma regra de `ingress` declarada, `policyTypes: '
                          '[Ingress]` vira um default-deny de entrada pra eles.'},
  'spec_en': {'scenario': 'Complete the NetworkPolicy that blocks all INBOUND traffic '
                          'by default in a namespace.',
              'template': 'kind: NetworkPolicy\n'
                          'spec:\n'
                          '  podSelector: {}\n'
                          '  policyTypes:\n'
                          '  - ___TYPE___',
              'blanks': {'TYPE': {'options': ['Ingress', 'Egress', 'Both'],
                                  'correct': 'Ingress'}},
              'explanation': '`podSelector: {}` selects ALL pods in the namespace; '
                             'with no `ingress` rule declared, `policyTypes: '
                             '[Ingress]` becomes a default-deny of inbound traffic for '
                             'them.'}},
 {'topic_title': 'Admission Controllers',
  'kind': 'order',
  'title': 'Do apply ao etcd',
  'title_en': 'From apply to etcd',
  'spec': {'scenario': 'Ordene o caminho de uma requisição `kubectl apply` até ser '
                       'persistida.',
           'steps_shuffled': ['Recurso persistido no etcd',
                              'kubectl apply enviado à API server',
                              'Validating webhook processa',
                              'Mutating webhook processa'],
           'correct_order': ['kubectl apply enviado à API server',
                             'Mutating webhook processa',
                             'Validating webhook processa',
                             'Recurso persistido no etcd'],
           'explanation': 'Mutating roda ANTES de validating de propósito: um webhook '
                          'pode injetar um valor (ex.: sidecar) que só depois é '
                          'validado — validar antes de mutar checaria um recurso que '
                          'ainda vai mudar.'},
  'spec_en': {'scenario': 'Order the path of a `kubectl apply` request until it is '
                          'persisted.',
              'steps_shuffled': ['Resource persisted in etcd',
                                 'kubectl apply sent to the API server',
                                 'Validating webhook processes',
                                 'Mutating webhook processes'],
              'correct_order': ['kubectl apply sent to the API server',
                                'Mutating webhook processes',
                                'Validating webhook processes',
                                'Resource persisted in etcd'],
              'explanation': 'Mutating runs BEFORE validating on purpose: a webhook '
                             'can inject a value (e.g. a sidecar) that is only then '
                             'validated — validating before mutating would check a '
                             'resource that is still about to change.'}},
 {'topic_title': 'Zero Trust Architecture',
  'kind': 'scenario',
  'title': 'Confiar na rede ou na identidade?',
  'title_en': 'Trust the network or the identity?',
  'spec': {'situation': 'Um funcionário tenta acessar um sistema interno de casa, fora '
                        'da VPN corporativa.',
           'choices': [{'text': 'Bloqueia o acesso por padrão, já que a conexão não '
                                'vem da rede interna da empresa.',
                        'outcome': 'Isso é o modelo de perímetro antigo — exatamente o '
                                   'que Zero Trust existe pra substituir.',
                        'good': False},
                       {'text': 'Verifica identidade e postura do dispositivo, '
                                'independente da rede de origem.',
                        'outcome': 'O acesso é avaliado pelo contexto real (quem é, '
                                   'dispositivo confiável), não pela localização de '
                                   'rede.',
                        'good': True}],
           'explanation': 'Zero Trust parte da premissa de que rede nenhuma é '
                          'automaticamente confiável — dentro OU fora do escritório. O '
                          'que decide é identidade + contexto, sempre.'},
  'spec_en': {'situation': 'An employee tries to access an internal system from home, '
                           'outside the corporate VPN.',
              'choices': [{'text': 'Block access by default, since the connection does '
                                   "not come from the company's internal network.",
                           'outcome': 'That is the old perimeter model — exactly what '
                                      'Zero Trust exists to replace.',
                           'good': False},
                          {'text': 'Verify identity and device posture, regardless of '
                                   'the source network.',
                           'outcome': 'Access is evaluated by real context (who they '
                                      'are, trusted device), not by network location.',
                           'good': True}],
              'explanation': 'Zero Trust starts from the premise that no network is '
                             'automatically trusted — inside OR outside the office. '
                             'What decides is identity + context, always.'}},
 {'topic_title': 'Runtime Security',
  'kind': 'find_flaw',
  'title': 'Ache o comportamento estranho',
  'title_en': 'Find the strange behavior',
  'spec': {'scenario': 'Um monitor de runtime (tipo Falco) geraria alerta pra um '
                       'destes três eventos. Ache qual.',
           'lines': ['Container abriu conexão de saída na porta 443 (esperado)',
                     'Container executou /bin/sh interativo (não esperado)',
                     'Container leu um arquivo de configuração local (esperado)'],
           'flaw_line_index': 1,
           'explanation': 'Um shell interativo dentro de um container de produção é '
                          'clássico sinal de comprometimento — na maioria dos '
                          'workloads, ninguém deveria estar abrindo shell ali ao '
                          'vivo.'},
  'spec_en': {'scenario': 'A runtime monitor (like Falco) would alert on one of these '
                          'three events. Find which.',
              'lines': ['Container opened an outbound connection on port 443 '
                        '(expected)',
                        'Container executed an interactive /bin/sh (unexpected)',
                        'Container read a local configuration file (expected)'],
              'flaw_line_index': 1,
              'explanation': 'An interactive shell inside a production container is a '
                             'classic compromise signal — in most workloads, nobody '
                             'should be opening a live shell there.'}},
 {'topic_title': 'Observabilidade Avançada',
  'kind': 'blanks',
  'title': 'Correlacione pelo trace',
  'title_en': 'Correlate by the trace',
  'spec': {'scenario': 'Complete o log pra que ele possa ser correlacionado com o '
                       'trace distribuído da mesma requisição.',
           'template': "logger.info('processing request', extra={'___KEY___': "
                       'span.trace_id})',
           'blanks': {'KEY': {'options': ['trace_id', 'user_id', 'timestamp'],
                              'correct': 'trace_id'}},
           'explanation': 'Incluir o `trace_id` no log é o que permite pular do log '
                          'direto pro trace correspondente — a correlação entre os '
                          'dois pilares da observabilidade.'},
  'spec_en': {'scenario': 'Complete the log so it can be correlated with the '
                          'distributed trace of the same request.',
              'template': "logger.info('processing request', extra={'___KEY___': "
                          'span.trace_id})',
              'blanks': {'KEY': {'options': ['trace_id', 'user_id', 'timestamp'],
                                 'correct': 'trace_id'}},
              'explanation': 'Including the `trace_id` in the log is what lets you '
                             'jump from the log straight to the matching trace — the '
                             'correlation between the two pillars of observability.'}},
 {'topic_title': 'Security Chaos Engineering',
  'kind': 'order',
  'title': 'Experimento controlado',
  'title_en': 'Controlled experiment',
  'spec': {'scenario': 'Ordene os passos de um experimento de chaos engineering '
                       'responsável.',
           'steps_shuffled': ['Observa o resultado',
                              'Define o blast radius',
                              'Documenta o aprendizado',
                              'Formula a hipótese',
                              'Executa o experimento controlado'],
           'correct_order': ['Formula a hipótese',
                             'Define o blast radius',
                             'Executa o experimento controlado',
                             'Observa o resultado',
                             'Documenta o aprendizado'],
           'explanation': 'Sem hipótese e blast radius definidos ANTES, o experimento '
                          'vira só "quebrar coisa aleatoriamente" — o oposto do método '
                          'científico que dá valor ao chaos engineering.'},
  'spec_en': {'scenario': 'Order the steps of a responsible chaos engineering '
                          'experiment.',
              'steps_shuffled': ['Observe the result',
                                 'Define the blast radius',
                                 'Document the learning',
                                 'Formulate the hypothesis',
                                 'Run the controlled experiment'],
              'correct_order': ['Formulate the hypothesis',
                                'Define the blast radius',
                                'Run the controlled experiment',
                                'Observe the result',
                                'Document the learning'],
              'explanation': 'Without hypothesis and blast radius defined BEFOREHAND, '
                             'the experiment becomes just "breaking things at random" '
                             '— the opposite of the scientific method that gives chaos '
                             'engineering its value.'}},
 {'topic_title': 'Incident Response',
  'kind': 'order',
  'title': 'As fases do incidente',
  'title_en': 'The incident phases',
  'spec': {'scenario': 'Ordene as fases do ciclo de resposta a incidente (modelo do '
                       'NIST).',
           'steps_shuffled': ['Containment',
                              'Recovery',
                              'Preparation',
                              'Eradication',
                              'Detection & Analysis'],
           'correct_order': ['Preparation',
                             'Detection & Analysis',
                             'Containment',
                             'Eradication',
                             'Recovery'],
           'explanation': 'Preparation vem antes de qualquer incidente acontecer '
                          '(runbook, ferramentas prontas); depois é detectar, conter o '
                          'avanço, erradicar a causa e só então recuperar o serviço.'},
  'spec_en': {'scenario': 'Order the phases of the incident response cycle (NIST '
                          'model).',
              'steps_shuffled': ['Containment',
                                 'Recovery',
                                 'Preparation',
                                 'Eradication',
                                 'Detection & Analysis'],
              'correct_order': ['Preparation',
                                'Detection & Analysis',
                                'Containment',
                                'Eradication',
                                'Recovery'],
              'explanation': 'Preparation comes before any incident happens (runbook, '
                             'tools ready); then detect, contain the spread, eradicate '
                             'the cause, and only then recover the service.'}},
 {'topic_title': 'Compliance Contínuo',
  'kind': 'scenario',
  'title': 'Corrigir agora ou depois?',
  'title_en': 'Fix now or later?',
  'spec': {'situation': 'Uma checagem automática encontra um bucket S3 público que '
                        'deveria ser privado.',
           'choices': [{'text': 'Registra o achado pra revisar com calma na próxima '
                                'auditoria anual.',
                        'outcome': 'O bucket fica exposto publicamente por meses até a '
                                   'auditoria acontecer.',
                        'good': False},
                       {'text': 'Corrige automaticamente agora e gera evidência do '
                                'ocorrido.',
                        'outcome': 'O desvio é fechado na hora, com rastro completo '
                                   'pra auditoria futura.',
                        'good': True}],
           'explanation': 'Compliance CONTÍNUO significa detectar e corrigir desvio em '
                          'tempo real, não só uma vez por ano — é essa a diferença pro '
                          'modelo de auditoria pontual antigo.'},
  'spec_en': {'situation': 'An automated check finds a public S3 bucket that should be '
                           'private.',
              'choices': [{'text': 'Log the finding to review calmly with the '
                                   'compliance team at the next annual audit.',
                           'outcome': 'The bucket stays publicly exposed for months '
                                      'until the audit happens.',
                           'good': False},
                          {'text': 'Remediate automatically now and generate evidence '
                                   'of what happened.',
                           'outcome': 'The drift is closed immediately, with a full '
                                      'trail for future audits.',
                           'good': True}],
              'explanation': 'CONTINUOUS compliance means detecting and fixing drift '
                             'in real time, not just once a year — that is the '
                             'difference from the old point-in-time audit model.'}},
 {'topic_title': 'Fundamentos de Python moderno',
  'kind': 'find_flaw',
  'title': 'A lista que não esquece',
  'title_en': 'The list that never forgets',
  'spec': {'scenario': 'Esta função tem o bug clássico do argumento default mutável. '
                       'Ache a linha.',
           'lines': ['def add_item(item, cart=[]):',
                     '    cart.append(item)',
                     '    return cart  # detalhe de implementação sem impacto'],
           'flaw_line_index': 0,
           'explanation': 'A lista `[]` é criada UMA vez, na definição da função — '
                          'todas as chamadas sem argumento reusam a MESMA lista, '
                          'acumulando item de chamadas anteriores. O certo é '
                          '`cart=None` e criar a lista dentro do corpo se `cart is '
                          'None`.'},
  'spec_en': {'scenario': 'This function has the classic mutable default argument bug. '
                          'Find the line.',
              'lines': ['def add_item(item, cart=[]):',
                        '    cart.append(item)',
                        '    return cart  # implementation detail with no impact'],
              'flaw_line_index': 0,
              'explanation': 'The list `[]` is created ONCE, at function definition '
                             'time — every call without an argument reuses the SAME '
                             'list, accumulating items from previous calls. The right '
                             'approach is `cart=None` and create the list inside the '
                             'body if `cart is None`.'}},
 {'topic_title': 'Estruturas de dados e código Pythonic',
  'kind': 'find_flaw',
  'title': 'Tudo na memória de uma vez',
  'title_en': 'Everything in memory at once',
  'spec': {'scenario': 'Esta função devia processar um arquivo GRANDE linha por linha, '
                       'sem estourar a memória. Ache a linha do problema.',
           'lines': ['def process(filename):  # inicialização de rotina',
                     '    lines = [l for l in open(filename)]',
                     '    return sum(len(l) for l in lines)'],
           'flaw_line_index': 1,
           'explanation': 'Os colchetes forçam carregar TODO o arquivo na memória de '
                          'uma vez numa lista. Trocar por um generator (sem colchetes: '
                          '`l for l in open(filename)`) processa uma linha por vez.'},
  'spec_en': {'scenario': 'This function should process a LARGE file line by line, '
                          'without blowing up memory. Find the problem line.',
              'lines': ['def process(filename):  # routine initialization',
                        '    lines = [l for l in open(filename)]',
                        '    return sum(len(l) for l in lines)'],
              'flaw_line_index': 1,
              'explanation': 'The brackets force loading the ENTIRE file into memory '
                             'at once as a list. Switching to a generator (without '
                             'brackets: `l for l in open(filename)`) processes one '
                             'line at a time.'}},
 {'topic_title': 'POO, exceções e context managers',
  'kind': 'find_flaw',
  'title': 'Esqueceu de fechar',
  'title_en': 'Forgot to close',
  'spec': {'scenario': 'Este código abre um arquivo sem garantir que ele seja fechado '
                       'se algo der errado no meio. Ache a linha.',
           'lines': ["f = open('dados.txt')",
                     'data = f.read()',
                     'process(data)  # detalhe de implementação sem impacto'],
           'flaw_line_index': 0,
           'explanation': 'Sem `with`, se `process(data)` levantar uma exceção, o '
                          'arquivo nunca é fechado explicitamente — em processo de '
                          'longa vida, isso vaza descritor de arquivo aos poucos.'},
  'spec_en': {'scenario': 'This code opens a file without guaranteeing it is closed if '
                          'something goes wrong in the middle. Find the line.',
              'lines': ["f = open('dados.txt')",
                        'data = f.read()',
                        'process(data)  # implementation detail with no impact'],
              'flaw_line_index': 0,
              'explanation': 'Without `with`, if `process(data)` raises an exception, '
                             'the file is never closed explicitly — in a long-lived '
                             'process, that slowly leaks file descriptors.'}},
 {'topic_title': 'Manipulação de arquivos, paths e CLI',
  'kind': 'blanks',
  'title': 'Carregar com segurança',
  'title_en': 'Load safely',
  'spec': {'scenario': 'Complete o parse do YAML usando o Loader que NÃO permite '
                       'executar código arbitrário.',
           'template': 'import yaml\n'
                       "config = yaml.load(open('config.yml'), Loader=___LOADER___)",
           'blanks': {'LOADER': {'options': ['yaml.SafeLoader',
                                             'yaml.Loader',
                                             'yaml.UnsafeLoader'],
                                 'correct': 'yaml.SafeLoader'}},
           'explanation': '`yaml.Loader` (o padrão antigo) e `UnsafeLoader` permitem '
                          'construir objetos Python arbitrários a partir do YAML — '
                          'abrindo caminho pra RCE se o arquivo vier de fonte não '
                          'confiável. `SafeLoader` só cria tipos básicos (str, int, '
                          'list, dict).'},
  'spec_en': {'scenario': 'Complete the YAML parse using the Loader that does NOT '
                          'allow executing arbitrary code.',
              'template': 'import yaml\n'
                          "config = yaml.load(open('config.yml'), Loader=___LOADER___)",
              'blanks': {'LOADER': {'options': ['yaml.SafeLoader',
                                                'yaml.Loader',
                                                'yaml.UnsafeLoader'],
                                    'correct': 'yaml.SafeLoader'}},
              'explanation': '`yaml.Loader` (the old default) and `UnsafeLoader` allow '
                             'constructing arbitrary Python objects from YAML — '
                             'opening a path to RCE if the file comes from an '
                             'untrusted source. `SafeLoader` only creates basic types '
                             '(str, int, list, dict).'}},
 {'topic_title': 'HTTP, APIs REST e SDKs',
  'kind': 'find_flaw',
  'title': 'Sem prazo de espera',
  'title_en': 'No timeout',
  'spec': {'scenario': 'Esta chamada HTTP tem um risco sério em produção. Ache a '
                       'linha.',
           'lines': ['import requests  # etapa padrão do processo',
                     'response = requests.get(url)',
                     'data = response.json()'],
           'flaw_line_index': 1,
           'explanation': 'Sem `timeout`, se o servidor remoto nunca responder, essa '
                          'chamada trava o processo INDEFINIDAMENTE — em produção isso '
                          'esgota conexões/threads até derrubar o serviço inteiro.'},
  'spec_en': {'scenario': 'This HTTP call has a serious risk in production. Find the '
                          'line.',
              'lines': ['import requests  # standard process step',
                        'response = requests.get(url)',
                        'data = response.json()'],
              'flaw_line_index': 1,
              'explanation': 'Without `timeout`, if the remote server never responds, '
                             'that call hangs the process INDEFINITELY — in production '
                             'that exhausts connections/threads until the whole '
                             'service goes down.'}},
 {'topic_title': 'Automação de sistema com Python',
  'kind': 'find_flaw',
  'title': 'Comando perigoso',
  'title_en': 'Dangerous command',
  'spec': {'scenario': 'Este script de automação tem uma falha clássica de shell '
                       'injection. Ache a linha.',
           'lines': ['import os',
                     "filename = input('Arquivo: ')",
                     "os.system(f'rm {filename}')"],
           'flaw_line_index': 2,
           'explanation': 'Se o usuário digitar `arquivo.txt; rm -rf ~`, o `os.system` '
                          'roda os DOIS comandos, já que o input vira parte da string '
                          "interpretada pelo shell. `subprocess.run(['rm', filename])` "
                          'evita isso, passando o nome como argumento literal.'},
  'spec_en': {'scenario': 'This automation script has a classic shell injection flaw. '
                          'Find the line.',
              'lines': ['import os',
                        "filename = input('Arquivo: ')",
                        "os.system(f'rm {filename}')"],
              'flaw_line_index': 2,
              'explanation': 'If the user types `arquivo.txt; rm -rf ~`, `os.system` '
                             'runs BOTH commands, since the input becomes part of the '
                             "string interpreted by the shell. `subprocess.run(['rm', "
                             'filename])` avoids that, passing the name as a literal '
                             'argument.'}},
 {'topic_title': 'Concorrência: threads, asyncio e multiprocessing',
  'kind': 'find_flaw',
  'title': 'Travou o event loop',
  'title_en': 'Blocked the event loop',
  'spec': {'scenario': 'Esta função async tem um erro que trava TODAS as outras '
                       'tarefas do event loop. Ache a linha.',
           'lines': ['async def fetch_all(urls):',
                     '    for url in urls:',
                     '        time.sleep(1)',
                     '        await fetch(url)'],
           'flaw_line_index': 2,
           'explanation': '`time.sleep` é bloqueante: ele trava a thread inteira, '
                          'inclusive o event loop, impedindo QUALQUER outra tarefa '
                          'async de rodar nesse segundo. O certo é `await '
                          'asyncio.sleep(1)`.'},
  'spec_en': {'scenario': 'This async function has a bug that freezes ALL other tasks '
                          'on the event loop. Find the line.',
              'lines': ['async def fetch_all(urls):',
                        '    for url in urls:',
                        '        time.sleep(1)',
                        '        await fetch(url)'],
              'flaw_line_index': 2,
              'explanation': '`time.sleep` is blocking: it freezes the entire thread, '
                             'including the event loop, preventing ANY other async '
                             'task from running during that second. The right call is '
                             '`await asyncio.sleep(1)`.'}},
 {'topic_title': 'Testes com pytest, mocks e cobertura',
  'kind': 'find_flaw',
  'title': 'Teste que liga pra API de verdade',
  'title_en': 'Test that hits the real API',
  'spec': {'scenario': 'Este teste unitário tem um problema que o torna lento, '
                       'instável e caro. Ache a linha.',
           'lines': ['def test_send_email():  # inicialização de rotina',
                     "    result = send_email_via_real_api('a@b.com')",
                     '    assert result.status == 200'],
           'flaw_line_index': 1,
           'explanation': 'Chamar a API real de e-mail num teste unitário deixa o '
                          'teste lento, dependente de rede e sujeito a falhar por '
                          'motivo alheio ao código. O certo é mockar a chamada '
                          'externa.'},
  'spec_en': {'scenario': 'This unit test has a problem that makes it slow, flaky, and '
                          'expensive. Find the line.',
              'lines': ['def test_send_email():  # routine initialization',
                        "    result = send_email_via_real_api('a@b.com')",
                        '    assert result.status == 200'],
              'flaw_line_index': 1,
              'explanation': 'Calling the real email API in a unit test makes the test '
                             'slow, network-dependent, and prone to fail for reasons '
                             'unrelated to the code. The right approach is to mock the '
                             'external call.'}},
 {'topic_title': 'Empacotamento moderno e qualidade de código',
  'kind': 'blanks',
  'title': 'Onde vai a dependência de dev?',
  'title_en': 'Where does the dev dependency go?',
  'spec': {'scenario': 'Complete o pyproject.toml pra declarar pytest e ruff como '
                       'dependências só de desenvolvimento.',
           'template': '[project]\n'
                       'dependencies = ["requests"]\n'
                       '\n'
                       '[___SECTION___]\n'
                       'dev = ["pytest", "ruff"]',
           'blanks': {'SECTION': {'options': ['project.optional-dependencies',
                                              'project.dependencies',
                                              'tool.dev'],
                                  'correct': 'project.optional-dependencies'}},
           'explanation': '`[project.optional-dependencies]` com um grupo `dev` é o '
                          'jeito padrão de separar o que é necessário pra RODAR o '
                          'projeto do que é só pra desenvolver nele.'},
  'spec_en': {'scenario': 'Complete the pyproject.toml to declare pytest and ruff as '
                          'development-only dependencies.',
              'template': '[project]\n'
                          'dependencies = ["requests"]\n'
                          '\n'
                          '[___SECTION___]\n'
                          'dev = ["pytest", "ruff"]',
              'blanks': {'SECTION': {'options': ['project.optional-dependencies',
                                                 'project.dependencies',
                                                 'tool.dev'],
                                     'correct': 'project.optional-dependencies'}},
              'explanation': '`[project.optional-dependencies]` with a `dev` group is '
                             'the standard way to separate what is needed to RUN the '
                             'project from what is only for developing it.'}},
 {'topic_title': 'Python para DevSecOps na prática',
  'kind': 'find_flaw',
  'title': 'Credencial no código',
  'title_en': 'Credential in the code',
  'spec': {'scenario': 'Este script Python usando boto3 tem um erro grave de '
                       'segurança. Ache a linha.',
           'lines': ['import boto3  # SDK oficial da AWS para uso em aplicações Python',
                     "session = boto3.Session(aws_access_key_id='AKIA123', "
                     "aws_secret_access_key='segredo')",
                     "s3 = session.client('s3', region_name='us-east-1')  # cria o "
                     'cliente autenticado do S3'],
           'flaw_line_index': 1,
           'explanation': 'Credencial AWS hardcoded no código vai pro Git pra sempre. '
                          'Rodando numa EC2, o certo é nem precisar disso: anexar um '
                          'IAM Role à instância e deixar o boto3 pegar credencial via '
                          'IMDS.'},
  'spec_en': {'scenario': 'This Python script using boto3 has a serious security '
                          'error. Find the line.',
              'lines': ['import boto3  # official AWS SDK for use in Python '
                        'applications',
                        "session = boto3.Session(aws_access_key_id='AKIA123', "
                        "aws_secret_access_key='segredo')",
                        "s3 = session.client('s3', region_name='us-east-1')  # creates "
                        'the authenticated S3 client'],
              'flaw_line_index': 1,
              'explanation': 'A hardcoded AWS credential in code goes to Git forever. '
                             'Running on an EC2, the right approach is not to need '
                             'that at all: attach an IAM Role to the instance and let '
                             'boto3 pick up credentials via IMDS.'}}]
