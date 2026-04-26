"""Fase 1, O Alicerce (Sistemas e Redes)."""
from ._helpers import m, q

PHASE1 = {
    "name": "Fase 1: O Alicerce (Sistemas e Redes)",
    "description": "Onde tudo começa: o servidor e o sistema operacional.",
    "topics": [
        # =====================================================================
        # 1.1 Fundamentos de Linux
        # =====================================================================
        {
            "title": "Fundamentos de Linux",
            "summary": "Permissões de arquivos, usuários e gestão de processos, a base de qualquer servidor.",
            "lesson": {
                "intro": (
                    "Praticamente todo servidor de produção do mundo roda Linux. AWS, Azure, "
                    "GCP, todos usam Linux como base de seus serviços gerenciados (RDS, EKS, "
                    "Lambda etc.) e a esmagadora maioria dos containers em K8s são linuxinhos. "
                    "Saber Linux <strong>fundo</strong> é o que separa o engenheiro que entende "
                    "o que faz do que apenas copia comando do Stack Overflow.<br><br>"
                    "Esta aula cobre o modelo mental do sistema operacional: o que são "
                    "usuários, processos e permissões, não como abstração de livro, mas como "
                    "elementos que atacantes exploram todos os dias. Toda CVE de container "
                    "começa exatamente aqui."
                ),
                "body": (
                    "<h3>1. Filosofia: tudo é arquivo</h3>"
                    "<p>O lema do Unix vale também no Linux: <strong>tudo é representado como "
                    "arquivo</strong>. Disco (<code>/dev/sda</code>), socket de rede "
                    "(<code>/proc/net/tcp</code>), processos rodando (<code>/proc/&lt;pid&gt;</code>), "
                    "configuração do kernel (<code>/sys</code>), até dispositivos USB e GPIOs. "
                    "Isso significa que o mesmo modelo de permissões (rwx + dono/grupo) controla "
                    "literalmente <em>tudo</em>. Quando um atacante explora uma vulnerabilidade "
                    "para escrever em <code>/dev/mem</code> ou <code>/proc/sys/kernel/core_pattern</code>, "
                    "ele está apenas usando o modelo de arquivos para subverter o kernel.</p>"
                    "<p>Aprender Linux fundo é, em larga medida, aprender quais arquivos importam "
                    "e quem deveria poder ler/escrever em cada um.</p>"

                    "<h3>2. Modelo de identidade: UID, GID e processos</h3>"
                    "<p>Cada processo é executado em nome de um <strong>UID</strong> (effective "
                    "user id) e tem um <strong>GID</strong> primário mais um conjunto de grupos "
                    "suplementares. Todo processo herda do pai, o init/<code>systemd</code> roda "
                    "como UID 0 (root) e os filhos vão derivando.</p>"
                    "<ul>"
                    "<li><strong>UID 0</strong>: <code>root</code>, ignora todo check de "
                    "permissão. É o motivo de não rodar serviços expostos à internet como root.</li>"
                    "<li><strong>UID 1-999</strong>: usuários de sistema (criados pelos pacotes: "
                    "<code>www-data</code>, <code>postgres</code>, <code>nobody</code>...).</li>"
                    "<li><strong>UID ≥ 1000</strong>: usuários humanos (em distros modernas).</li>"
                    "</ul>"
                    "<p>Inspecione com:</p>"
                    "<pre><code>id                 # quem sou eu (uid, gid, grupos)\n"
                    "id deploy          # idem para outro usuário\n"
                    "ps -eo pid,uid,user,cmd | head\n"
                    "cat /etc/passwd    # mapeamento UID ↔ login ↔ shell\n"
                    "cat /etc/group     # mapeamento GID ↔ nome do grupo</code></pre>"
                    "<p>Senhas <strong>nunca</strong> ficam em <code>/etc/passwd</code> em sistemas "
                    "modernos: o hash mora em <code>/etc/shadow</code>, legível só pelo root. "
                    "Usar <code>/etc/passwd</code> como atalho leitor está bem; vazar "
                    "<code>/etc/shadow</code> para outro usuário é incidente de segurança.</p>"

                    "<h3>3. Permissões clássicas: o modelo rwx</h3>"
                    "<p>Cada arquivo tem dono, grupo e três classes de permissão "
                    "(<em>user / group / other</em>) em três bits cada (<code>r</code>=4, "
                    "<code>w</code>=2, <code>x</code>=1). Em octal:</p>"
                    "<pre><code>chmod 750 deploy.sh\n"
                    "  └ user 7 = r+w+x\n"
                    "  └ group 5 = r+x  (sem write)\n"
                    "  └ other 0 = nada\n\n"
                    "ls -l deploy.sh\n"
                    "-rwxr-x---  1 deploy web  142 Apr 25 16:12 deploy.sh</code></pre>"
                    "<p>Para diretórios, o significado é diferente: <code>r</code> permite "
                    "<em>listar</em> nomes, <code>x</code> permite <em>entrar</em>, e "
                    "<code>w</code> permite <em>criar/remover</em> arquivos lá dentro. É "
                    "perfeitamente possível ter um diretório com permissão <code>x</code> mas "
                    "sem <code>r</code>, você consegue acessar arquivos por nome conhecido, "
                    "mas não consegue listar.</p>"
                    "<p>O modo simbólico costuma ser mais legível para mudanças incrementais:</p>"
                    "<pre><code>chmod g+rw arquivo       # add read+write para o grupo\n"
                    "chmod o-x  diretorio/     # remove execute do 'other'\n"
                    "chmod -R u+rwX,g+rX,o-rwx /srv/app/   # X executa só em diretórios</code></pre>"

                    "<h3>4. Bits especiais: setuid, setgid, sticky</h3>"
                    "<p>Três bits 'extras' alteram comportamento de execução:</p>"
                    "<ul>"
                    "<li><strong>setuid (4xxx)</strong>: o programa, ao ser executado, roda "
                    "com privilégio do <em>dono</em> do arquivo, não de quem o invocou. É como "
                    "<code>passwd</code> consegue alterar <code>/etc/shadow</code> sendo "
                    "executado por usuário comum. Mal usado, é vetor clássico de escalada, "
                    "todo binário setuid mantido na sua máquina deveria estar em uma whitelist.</li>"
                    "<li><strong>setgid (2xxx)</strong>: idem, mas com privilégio do grupo. Em "
                    "diretórios, garante que arquivos novos herdem o grupo do diretório (útil "
                    "para diretórios compartilhados de equipe).</li>"
                    "<li><strong>sticky bit (1xxx)</strong>: em diretórios, só o dono do arquivo "
                    "(ou do diretório) pode apagá-lo. Por isso <code>/tmp</code> tem modo "
                    "<code>1777</code>: qualquer um cria, mas só o criador apaga.</li>"
                    "</ul>"
                    "<pre><code>find / -perm -4000 -type f 2&gt;/dev/null   # binários setuid\n"
                    "find / -perm -2000 -type f 2&gt;/dev/null   # binários setgid</code></pre>"

                    "<h3>5. Para além de rwx: ACLs e capabilities</h3>"
                    "<p>O modelo rwx tem só três classes, quando você precisa de granularidade "
                    "mais fina, use <strong>ACLs POSIX</strong>:</p>"
                    "<pre><code>setfacl -m u:carlos:r-- /srv/data/relatorio.csv\n"
                    "setfacl -m g:auditoria:r-x /srv/scripts/\n"
                    "getfacl /srv/data/relatorio.csv</code></pre>"
                    "<p>Já as <strong>Linux capabilities</strong> decompõem o poder de root em "
                    "~40 grãos (<code>man capabilities(7)</code>): em vez de dar root inteiro a "
                    "um binário web só para ele bindar a porta 80, você concede só "
                    "<code>CAP_NET_BIND_SERVICE</code>:</p>"
                    "<pre><code>setcap cap_net_bind_service=+ep /usr/local/bin/myserver\n"
                    "getcap /usr/local/bin/myserver</code></pre>"
                    "<p>Esse é o mecanismo por trás de imagens Docker bem feitas que rodam como "
                    "não-root mas conseguem escutar em portas privilegiadas.</p>"

                    "<h3>6. Processos, sinais e systemd</h3>"
                    "<p>Cada processo tem um <strong>PID</strong>, um pai (<strong>PPID</strong>) "
                    "e um estado (<code>R</code>=running, <code>S</code>=sleeping, "
                    "<code>D</code>=disk wait, <code>Z</code>=zombie). Inspecione com "
                    "<code>ps auxf</code> ou interativamente com <code>htop</code>.</p>"
                    "<p>O kernel se comunica com processos via <strong>sinais</strong>:</p>"
                    "<ul>"
                    "<li><code>SIGTERM (15)</code>, pede para terminar; processo bem-comportado "
                    "fecha conexões, salva estado e sai. Sempre tente esse primeiro.</li>"
                    "<li><code>SIGKILL (9)</code>, termina imediatamente; processo não tem "
                    "chance de cleanup. Use só quando SIGTERM não responde.</li>"
                    "<li><code>SIGHUP (1)</code>, historicamente 'hangup'; serviços usam para "
                    "<em>recarregar configuração</em> sem reiniciar.</li>"
                    "<li><code>SIGINT (2)</code>, Ctrl+C no terminal.</li>"
                    "<li><code>SIGSTOP/SIGCONT</code>, pausa/retoma o processo.</li>"
                    "</ul>"
                    "<p>Em distros modernas, todo serviço é gerenciado pelo "
                    "<strong>systemd</strong> via <em>units</em>:</p>"
                    "<pre><code>systemctl status nginx\n"
                    "systemctl restart nginx\n"
                    "systemctl reload nginx       # equivale a SIGHUP, sem downtime\n"
                    "journalctl -u nginx -f       # logs em tempo real\n"
                    "systemctl list-units --failed</code></pre>"

                    "<h3>7. Filesystem hierarchy padrão (FHS)</h3>"
                    "<p>Saber onde cada coisa mora economiza horas de busca:</p>"
                    "<ul>"
                    "<li><code>/etc</code>, configuração do sistema. Apenas root escreve.</li>"
                    "<li><code>/usr/bin</code>, <code>/usr/sbin</code>, binários do sistema.</li>"
                    "<li><code>/usr/local/bin</code>, binários instalados manualmente.</li>"
                    "<li><code>/var</code>, dados <em>variáveis</em>: logs, caches, spool, "
                    "bancos de dados. Faz sentido em FS separado em produção.</li>"
                    "<li><code>/home</code>, dados de usuários humanos.</li>"
                    "<li><code>/srv</code>, dados servidos por serviços (web, ftp).</li>"
                    "<li><code>/opt</code>, software de terceiros 'self-contained'.</li>"
                    "<li><code>/proc</code>, <code>/sys</code>, pseudo-FS exposto pelo kernel.</li>"
                    "<li><code>/dev</code>, dispositivos.</li>"
                    "<li><code>/run</code>, <code>/tmp</code>, efêmeros (zerados ao reboot).</li>"
                    "</ul>"

                    "<h3>8. Anti-patterns clássicos</h3>"
                    "<ul>"
                    "<li><strong><code>chmod 777 /srv/app</code></strong>: qualquer usuário do "
                    "sistema escreve. Atacante com qualquer outra conta no mesmo host injeta "
                    "payload no app legítimo, escalada trivial.</li>"
                    "<li><strong>Rodar serviços como root</strong>: cada bug no serviço "
                    "(Heartbleed, Log4Shell, etc.) vira RCE como root e portanto comprometimento "
                    "total da máquina. Use usuário dedicado + <code>User=</code> no systemd.</li>"
                    "<li><strong>Adicionar usuário ao grupo <code>sudo</code> sem regras "
                    "específicas</strong>: dá poder total. Prefira drops em "
                    "<code>/etc/sudoers.d/</code> liberando comandos específicos.</li>"
                    "<li><strong>Editar arquivo de config como root sem backup</strong>: um "
                    "<code>vim /etc/sshd_config</code> esquecendo o <code>PermitRootLogin</code> "
                    "e você acabou de se trancar fora do servidor de produção. Sempre "
                    "<code>cp arquivo arquivo.bak</code> antes.</li>"
                    "<li><strong>Esquecer permissão em <code>~/.ssh</code></strong>: o sshd "
                    "<em>silenciosamente</em> recusa autenticação se o diretório/arquivo tiver "
                    "permissão frouxa. Você só descobre olhando <code>journalctl -u sshd</code>.</li>"
                    "</ul>"

                    "<h3>9. Caso real: o ataque no <code>/tmp</code></h3>"
                    "<p>Em 2016, várias distros tiveram que mudar o default de <code>/tmp</code> "
                    "para um <em>tmpfs</em> isolado por usuário porque o <code>/tmp</code> "
                    "compartilhado virou vetor recorrente: serviço A criava arquivo previsível "
                    "(<code>/tmp/upload.txt</code>); atacante criava antes um symlink apontando "
                    "para <code>/etc/shadow</code>; o serviço, rodando como root, sobrescrevia "
                    "shadow. Daí veio a popularização do <code>PrivateTmp=true</code> no systemd, "
                    "que monta um <code>/tmp</code> exclusivo por serviço, pequena mudança no "
                    "kernel/systemd que matou uma classe inteira de bugs.</p>"

                    "<h3>10. Checklist mental ao se conectar a um host novo</h3>"
                    "<ol>"
                    "<li><code>uname -a</code>, kernel e arquitetura.</li>"
                    "<li><code>cat /etc/os-release</code>, qual distro/versão.</li>"
                    "<li><code>id</code> e <code>sudo -l</code>, quem sou e o que posso.</li>"
                    "<li><code>ss -tulpn</code>, quais portas estão abertas e quem escuta.</li>"
                    "<li><code>systemctl list-units --type=service --state=running</code>.</li>"
                    "<li><code>df -h</code> e <code>free -h</code>, disco e memória.</li>"
                    "<li><code>journalctl -p err -S 'today'</code>, erros recentes do sistema.</li>"
                    "</ol>"
                    "<p>Em 2 minutos você sabe se está em terreno familiar ou se pisou em uma "
                    "máquina já comprometida.</p>"
                ),
                "practical": (
                    "Em uma VM ou container limpo:<br>"
                    "(1) Crie o usuário <code>app</code> e o grupo <code>web</code>; adicione "
                    "<code>app</code> ao grupo. Verifique com <code>id app</code>.<br>"
                    "(2) Crie o diretório <code>/srv/app</code> com dono <code>app:web</code> e "
                    "modo <code>2750</code> (note o setgid). Crie um arquivo dentro, confirme "
                    "que ele herdou o grupo <code>web</code>.<br>"
                    "(3) Crie um segundo usuário <code>visitante</code> sem entrar no grupo. "
                    "Tente ler o arquivo como ele e veja a falha. Use <code>strace -e openat</code> "
                    "para ver o EACCES vindo do kernel.<br>"
                    "(4) Adicione uma ACL: "
                    "<code>setfacl -m u:visitante:r-- /srv/app/config.yml</code>. Confirme que "
                    "agora ele lê.<br>"
                    "(5) Bônus: configure um <code>nc -l -p 8080</code> rodando como "
                    "<code>app</code> e dê a ele <code>CAP_NET_BIND_SERVICE</code> via "
                    "<code>setcap</code> em uma cópia do <code>nc</code>; tente bindar na porta 80 "
                    "com e sem a capability."
                ),
            },
            "materials": [
                m("The Linux Documentation Project: Permissions",
                  "https://tldp.org/LDP/intro-linux/html/sect_03_04.html",
                  "docs", "Resumo clássico sobre permissões em Linux."),
                m("man chmod", "https://man7.org/linux/man-pages/man1/chmod.1.html",
                  "docs", "Manual oficial."),
                m("man chown", "https://man7.org/linux/man-pages/man1/chown.1.html",
                  "docs", "Manual oficial."),
                m("Red Hat: Managing processes with systemd",
                  "https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_processes_with_systemd/index",
                  "docs", "Gestão moderna de processos."),
                m("Linux Journey: Command Line",
                  "https://linuxjourney.com/lesson/the-shell",
                  "course", "Curso interativo gratuito introduzindo o shell."),
                m("man capabilities(7)",
                  "https://man7.org/linux/man-pages/man7/capabilities.7.html",
                  "docs", "Como decompor o poder de root em pedaços."),
            ],
            "questions": [
                q("O que representa o '7' em `chmod 750 arquivo`?",
                  "Permissão completa (leitura, escrita e execução) para o dono do arquivo.",
                  ["Permissão de leitura para todos.",
                   "Octal de SUID + sticky bit.",
                   "Permissão somente leitura."],
                  "Em octal: 4 (read) + 2 (write) + 1 (execute) = 7. O segundo dígito (5) "
                  "é r-x para o grupo e o terceiro (0) bloqueia o resto do mundo."),
                q("Qual comando exibe os processos em execução com seu PID?",
                  "ps", ["chmod", "ls", "tar"],
                  "ps lista os processos do shell atual; `ps auxf` mostra todos com hierarquia."),
                q("Como alterar o dono do arquivo `app.log` para o usuário `deploy`?",
                  "chown deploy app.log",
                  ["chmod deploy app.log", "chgrp deploy app.log", "passwd deploy app.log"],
                  "chown muda o dono. chgrp só muda o grupo; chmod muda permissões."),
                q("O que é o UID 0 em sistemas Linux?",
                  "É o ID do superusuário (root).",
                  ["Usuário convidado.", "Usuário sem permissões.", "Usuário do nginx."],
                  "UID 0 ignora checks de permissão, por isso processos críticos não devem rodar como root."),
                q("Qual sinal `kill -9 PID` envia para o processo?",
                  "SIGKILL, termina o processo imediatamente sem chance de cleanup.",
                  ["SIGTERM, com chance de cleanup.",
                   "SIGHUP, recarregando configuração.",
                   "SIGSTOP, pausando o processo."],
                  "SIGKILL não pode ser ignorado nem capturado. Prefira SIGTERM (15) sempre que possível."),
                q("Em `ls -l`, a string `-rwxr-x---` significa que o grupo pode:",
                  "Ler e executar, mas não escrever.",
                  ["Escrever, ler e executar.",
                   "Apenas escrever.",
                   "Nada, o grupo está bloqueado."],
                  "r-x para o grupo (5 em octal) e --- para outros (0). Modo final 750."),
                q("Onde ficam os usuários e seus shells padrão?",
                  "/etc/passwd",
                  ["/etc/shadow apenas.", "/var/log/users.", "/root/.bashrc."],
                  "Hashes de senha ficam em /etc/shadow (legível só para root). /etc/passwd "
                  "lista usuários, UIDs, home e shell."),
                q("Qual comando mostra o uso de disco por diretório?",
                  "du", ["df apenas raiz.", "ls -lh.", "free -m."],
                  "`du -sh *` é o atalho clássico. df mostra uso por filesystem; free mostra memória."),
                q("O que faz o bit setuid (`chmod u+s`) em um executável?",
                  "Roda o programa com os privilégios do dono do arquivo, não de quem o executou.",
                  ["Aumenta a velocidade do binário.",
                   "Esconde o arquivo do `ls`.",
                   "Bloqueia escrita no arquivo."],
                  "É o que faz `passwd` poder alterar /etc/shadow mesmo executado por usuário comum. "
                  "Mal usado é vetor de escalada, só em binários muito auditados."),
                q("Qual diretório guarda configurações de sistema em Linux?",
                  "/etc",
                  ["/var", "/usr/bin", "/home"],
                  "/etc é o diretório padrão de configuração. /var guarda dados variáveis (logs, "
                  "spool); /usr/bin tem binários; /home tem dados dos usuários."),
            ],
        },
        # =====================================================================
        # 1.2 Redes de Computadores
        # =====================================================================
        {
            "title": "Redes de Computadores",
            "summary": "TCP/IP, DNS, portas e roteamento, o vocabulário comum de qualquer sistema distribuído.",
            "lesson": {
                "intro": (
                    "Quando algo quebra em produção e o stack trace não diz nada, em 80% dos "
                    "casos o problema é de rede: DNS lento, certificado expirado, MTU errado em "
                    "VPN, security group bloqueando uma porta nova, NAT exaurido. Engenheiro "
                    "que não tem fluência em TCP/IP fica refém do time de infra para abrir "
                    "ticket de cada incidente.<br><br>"
                    "Esta aula é um <em>crash course</em> direto ao ponto: modelo mental, "
                    "ferramentas que diagnosticam 95% dos problemas e os erros mais caros que "
                    "vi gente cometer."
                ),
                "body": (
                    "<h3>1. As quatro camadas que importam (modelo TCP/IP)</h3>"
                    "<p>Esqueça as 7 camadas do OSI por enquanto. O modelo prático é o "
                    "TCP/IP de quatro camadas:</p>"
                    "<ol>"
                    "<li><strong>Link</strong>: Ethernet, Wi-Fi. Endereçamento por MAC. Você "
                    "lida com isso só em datacenter ou debug profundo.</li>"
                    "<li><strong>Internet</strong>: IP. Endereçamento e roteamento entre redes. "
                    "IPv4 e IPv6.</li>"
                    "<li><strong>Transporte</strong>: TCP (confiável, ordenado) e UDP (rápido, "
                    "sem garantia). Multiplexa por porta.</li>"
                    "<li><strong>Aplicação</strong>: HTTP, DNS, SSH, gRPC, AMQP, onde a sua "
                    "app vive.</li>"
                    "</ol>"
                    "<p>Cada pacote é encapsulado de cima para baixo na saída e desencapsulado "
                    "na entrada. Saber em qual camada o problema mora é o que faz o "
                    "diagnóstico ser de minutos em vez de horas.</p>"

                    "<h3>2. Endereçamento, CIDR e RFC 1918</h3>"
                    "<p>Endereços IPv4 são 32 bits (~4 bilhões, esgotado em 2011); IPv6 é "
                    "128 bits. Usamos <strong>CIDR</strong> para falar de blocos:</p>"
                    "<pre><code>10.0.0.0/8       # 16M endereços (privada, RFC 1918)\n"
                    "172.16.0.0/12    # 1M endereços (privada, RFC 1918)\n"
                    "192.168.0.0/16   # 65k endereços (privada, RFC 1918)\n"
                    "169.254.0.0/16   # link-local (auto-configurado)\n"
                    "127.0.0.0/8      # loopback\n"
                    "0.0.0.0/0        # 'qualquer' (rota default, bind em todas as interfaces)</code></pre>"
                    "<p>O número após a barra é a <em>máscara</em> de rede em bits. <code>/24</code> "
                    "= 256 endereços; <code>/16</code> = 65 536; <code>/8</code> = 16 milhões. "
                    "Em cada bloco, dois endereços não são utilizáveis (rede e broadcast), então "
                    "<code>/24</code> dá 254 hosts.</p>"

                    "<h3>3. TCP vs UDP, quando usar cada um</h3>"
                    "<p>TCP estabelece conexão com <strong>three-way handshake</strong> "
                    "(SYN → SYN-ACK → ACK), depois transmite dados garantindo:</p>"
                    "<ul>"
                    "<li>Ordem (numera segmentos);</li>"
                    "<li>Entrega (retransmite o que perde);</li>"
                    "<li>Controle de fluxo (ajusta a janela de envio à capacidade do receptor);</li>"
                    "<li>Controle de congestão (ajusta-se à rede, Reno, Cubic, BBR).</li>"
                    "</ul>"
                    "<p>Tudo isso tem custo: handshake cobra um RTT antes do primeiro byte útil "
                    "e o head-of-line blocking faz uma perda travar todo o stream. Por isso "
                    "<strong>HTTP/3</strong> abandonou TCP e foi para QUIC sobre UDP.</p>"
                    "<p>UDP é stateless: só envia o datagrama. Sem retransmissão, sem ordem. "
                    "Use quando latência &gt; confiabilidade: DNS, voz/vídeo em tempo real, "
                    "QUIC, WireGuard, jogos online.</p>"

                    "<h3>4. Portas: quem fala com quem</h3>"
                    "<p>Portas são números de 16 bits que multiplexam serviços em um mesmo IP:</p>"
                    "<ul>"
                    "<li><strong>0-1023</strong>, <em>well-known</em>. Bind precisa de root "
                    "(ou <code>CAP_NET_BIND_SERVICE</code>). HTTP=80, HTTPS=443, SSH=22, "
                    "DNS=53, SMTP=25.</li>"
                    "<li><strong>1024-49151</strong>, registradas. PostgreSQL=5432, "
                    "MySQL=3306, Redis=6379, MongoDB=27017.</li>"
                    "<li><strong>49152-65535</strong>, efêmeras. O kernel tira daqui a porta de "
                    "origem de cada conexão de saída.</li>"
                    "</ul>"
                    "<p>A exaustão de portas efêmeras é uma das causas mais sub-diagnosticadas "
                    "de outage: load balancer fechando conexão por timeout enquanto a "
                    "<code>net.ipv4.ip_local_port_range</code> está em default.</p>"

                    "<h3>5. DNS, o telefone da internet (e o melhor lugar pra causar outage)</h3>"
                    "<p>DNS resolve nomes em IPs com cache em vários níveis: resolver da app, "
                    "stub do SO (<code>/etc/nsswitch</code> + <code>systemd-resolved</code>), "
                    "resolver do ISP/cloud, autoritativos. Tipos de registro essenciais:</p>"
                    "<table style='border-collapse:collapse'>"
                    "<tr><td><code>A</code></td><td>nome → IPv4</td></tr>"
                    "<tr><td><code>AAAA</code></td><td>nome → IPv6</td></tr>"
                    "<tr><td><code>CNAME</code></td><td>nome → outro nome</td></tr>"
                    "<tr><td><code>MX</code></td><td>servidor de e-mail</td></tr>"
                    "<tr><td><code>TXT</code></td><td>texto livre, SPF, DKIM, validações</td></tr>"
                    "<tr><td><code>NS</code></td><td>delegação de zona</td></tr>"
                    "<tr><td><code>SRV</code></td><td>serviço + porta (LDAP, XMPP, Kerberos)</td></tr>"
                    "<tr><td><code>CAA</code></td><td>quais CAs podem emitir cert para o domínio</td></tr>"
                    "</table>"
                    "<p>O <strong>TTL</strong> diz por quanto tempo um resolver pode cachear. "
                    "Em produção: TTL alto (3600s) é eficiente mas migração leva horas. TTL "
                    "baixo (30s) acelera failover mas multiplica custo de queries. Padrão "
                    "<em>health-checked</em>: TTL baixo + autoridade que retira IPs unhealthy "
                    "(Route 53, Cloudflare).</p>"

                    "<h3>6. Toolbox: as ferramentas que resolvem 95% dos problemas</h3>"
                    "<pre><code># Conectividade básica\n"
                    "ping -c 3 1.1.1.1               # ICMP, alguns firewalls bloqueiam\n"
                    "mtr 1.1.1.1                     # traceroute contínuo, mostra perdas\n"
                    "\n"
                    "# DNS\n"
                    "dig +short example.com\n"
                    "dig +trace example.com          # resolução completa, root → autoritativo\n"
                    "dig @8.8.8.8 example.com        # forçando resolver\n"
                    "drill -T example.com            # alternativa moderna\n"
                    "\n"
                    "# Sockets locais\n"
                    "ss -tulpn                       # tcp+udp listening, processo, numérico\n"
                    "ss -tan state established       # conexões estabelecidas\n"
                    "lsof -i :443                    # quem usa a porta 443\n"
                    "\n"
                    "# Captura de pacotes\n"
                    "sudo tcpdump -i any -nn 'tcp port 443 and host api.example.com' -w /tmp/d.pcap\n"
                    "wireshark /tmp/d.pcap           # análise visual\n"
                    "\n"
                    "# HTTP\n"
                    "curl -v --resolve api.example.com:443:10.0.1.5 https://api.example.com/health\n"
                    "curl -w '@curl-format.txt' -o /dev/null -s https://example.com\n"
                    "                                # dns_time, connect, ssl, ttfb, total\n"
                    "\n"
                    "# IP / rotas\n"
                    "ip a                            # interfaces e endereços\n"
                    "ip r                            # tabela de roteamento\n"
                    "ip neigh                        # cache ARP\n"
                    "\n"
                    "# Stress / load (cuidado!)\n"
                    "hey -n 1000 -c 50 https://api.example.com/  # carga simples\n"
                    "iperf3 -c host                              # banda</code></pre>"

                    "<h3>7. Anatomia de uma requisição HTTPS</h3>"
                    "<p>O que <em>realmente</em> acontece quando você faz "
                    "<code>curl https://api.example.com</code>:</p>"
                    "<ol>"
                    "<li><strong>DNS</strong>: resolve <code>api.example.com</code> → IP (cache "
                    "miss = ~5-50ms; hit = sub-ms).</li>"
                    "<li><strong>TCP handshake</strong>: SYN/SYN-ACK/ACK = 1 RTT.</li>"
                    "<li><strong>TLS handshake</strong>: 1-2 RTTs em TLS 1.3 (1 RTT no caso "
                    "comum, 0-RTT em sessão retomada). Aqui certificado é validado.</li>"
                    "<li><strong>HTTP request</strong>: envia headers e (se POST) body.</li>"
                    "<li><strong>Server processing</strong>: app processa.</li>"
                    "<li><strong>HTTP response</strong>: chega ao cliente.</li>"
                    "</ol>"
                    "<p>Quando alguém diz 'a API está lenta', você precisa saber em qual desses "
                    "passos. <code>curl -w</code> com formato customizado revela cada um.</p>"

                    "<h3>8. NAT, proxy, load balancer e o problema do IP real</h3>"
                    "<p>Em produção quase ninguém fala com o servidor diretamente. Há sempre "
                    "uma cadeia: Cloudflare → ALB → NLB → Pod K8s → app. Cada salto pode "
                    "(a) trocar o IP de origem (NAT) ou (b) preservá-lo via "
                    "<code>X-Forwarded-For</code>/<code>Forwarded</code>/Proxy Protocol.</p>"
                    "<p>Anti-pattern clássico: confiar cegamente em "
                    "<code>X-Forwarded-For</code> do request sem checar quantos proxies de "
                    "confiança você tem na frente. Atacante manda <code>X-Forwarded-For: "
                    "127.0.0.1</code> e bypassa rate limit. Mitigação: configure no proxy "
                    "(Nginx <code>set_real_ip_from</code>, ALB com "
                    "<code>X-Forwarded-For</code> trust hops) e nunca confie no header "
                    "vindo direto do cliente.</p>"

                    "<h3>9. Segurança em rede: o que pode dar errado</h3>"
                    "<ul>"
                    "<li><strong>Portas abertas demais</strong>: cada porta em "
                    "<code>0.0.0.0</code> é superfície de ataque. Default-deny no firewall.</li>"
                    "<li><strong>DNS sem DNSSEC + cache poisoning</strong>: caso clássico "
                    "Kaminsky 2008.</li>"
                    "<li><strong>TLS mal configurado</strong>: TLS 1.0/1.1, cipher suites "
                    "fracas, certificado curinga vazado. Use SSL Labs e Mozilla SSL Generator.</li>"
                    "<li><strong>BGP hijacking</strong>: prefixo seu sequestrado por outro AS. "
                    "Solução: RPKI, MANRS.</li>"
                    "<li><strong>SSRF</strong>: app fala com URL controlada pelo usuário sem "
                    "validar, bate em <code>169.254.169.254</code> (metadata) e exfiltra "
                    "credencial IAM. <em>Veja Capital One 2019</em>.</li>"
                    "</ul>"

                    "<h3>10. Caso real: Cloudflare 2020, o BGP outage</h3>"
                    "<p>Em julho de 2020, Cloudflare ficou fora 27 minutos porque um update de "
                    "config de roteamento BGP retirou anúncios para um conjunto de prefixos. "
                    "Sites que dependiam de Cloudflare ficaram inalcançáveis. Lição: roteamento "
                    "é frágil; tenha plano B (multi-CDN ou DNS com health-check direto a "
                    "origem).</p>"
                ),
                "practical": (
                    "(1) <code>dig +trace seudominio.com</code>: identifique cada delegação até "
                    "o autoritativo. Anote os TTLs.<br>"
                    "(2) Em uma VM, abra dois terminais. Em um, "
                    "<code>sudo tcpdump -i any -nn -w /tmp/r.pcap port 80 or port 443</code>; "
                    "no outro, faça <code>curl -v https://example.com</code>. Pare o tcpdump e "
                    "abra o pcap no Wireshark, identifique handshake TCP, ClientHello TLS, "
                    "ApplicationData.<br>"
                    "(3) <code>curl -w '@-' -o /dev/null -s https://example.com</code> com um "
                    "format file que imprima dns/connect/ssl/ttfb/total. Repita com outro "
                    "domínio mais distante e compare.<br>"
                    "(4) <code>ss -tulpn</code> em sua máquina: para cada porta, identifique o "
                    "processo dono e justifique se ela deveria estar aberta."
                ),
            },
            "materials": [
                m("Beej's Guide to Network Programming", "https://beej.us/guide/bgnet/",
                  "book", "Conceitos fundamentais com clareza."),
                m("Cloudflare: O que é DNS?",
                  "https://www.cloudflare.com/learning/dns/what-is-dns/",
                  "article", "Explicação acessível."),
                m("MDN: HTTP overview",
                  "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview",
                  "docs", ""),
                m("RFC 1180, A TCP/IP Tutorial",
                  "https://www.rfc-editor.org/rfc/rfc1180", "docs",
                  "Curto, antigo e excelente."),
                m("Linux Network Diagnostics with ss",
                  "https://man7.org/linux/man-pages/man8/ss.8.html", "docs", ""),
                m("HTTP/3 Explained (Cloudflare)",
                  "https://blog.cloudflare.com/http3-the-past-present-and-future/",
                  "article", ""),
            ],
            "questions": [
                q("Qual porta padrão do HTTPS?",
                  "443", ["80", "22", "8080"],
                  "443 é a porta well-known do HTTPS. 80 é HTTP, 22 é SSH, 8080 é uma alternativa comum em proxies."),
                q("Qual protocolo é orientado a conexão?",
                  "TCP", ["UDP", "ICMP", "ARP"],
                  "TCP usa handshake e garante ordem/retransmissão. UDP é sem conexão; ICMP é "
                  "para mensagens de controle; ARP resolve MAC↔IP."),
                q("O que faz o comando `dig example.com`?",
                  "Consulta registros DNS para o domínio.",
                  ["Mostra rota até o destino.",
                   "Faz uma requisição HTTP.",
                   "Abre um socket TCP."],
                  "dig é a ferramenta padrão para consultar DNS, substituiu o `nslookup` em "
                  "ambientes profissionais."),
                q("Qual registro DNS aponta um nome para um IP IPv4?",
                  "A", ["AAAA (IPv6).", "CNAME (alias).", "MX (mail)."],
                  "A = IPv4, AAAA = IPv6 (4 vezes maior), CNAME = alias, MX = servidor de e-mail."),
                q("O que indica TTL em respostas DNS?",
                  "Por quanto tempo o resultado pode ficar em cache.",
                  ["A latência da rede.", "A versão do protocolo.", "O tamanho do pacote."],
                  "TTL alto → menos consultas mas migração lenta. TTL baixo → mais carga mas "
                  "mudanças se propagam rápido."),
                q("Qual ferramenta lista sockets em escuta no Linux moderno?",
                  "ss -tulpn", ["ifconfig", "route", "ipset"],
                  "netstat foi substituído por ss em distros modernas. -tulpn lista TCP, UDP, "
                  "listening, processo e numérico."),
                q("Qual IP é o loopback IPv4?",
                  "127.0.0.1", ["192.168.0.1", "10.0.0.1", "0.0.0.0"],
                  "127.0.0.0/8 inteiro é loopback; 0.0.0.0 representa 'todas as interfaces' ao bindar."),
                q("CIDR /24 corresponde a:",
                  "Máscara 255.255.255.0", ["255.0.0.0", "255.255.0.0", "255.255.255.255"],
                  "Os primeiros 24 bits são rede; restam 8 bits → 256 endereços, sendo 254 usáveis "
                  "(rede + broadcast)."),
                q("UDP é normalmente usado em:",
                  "DNS, vídeo em tempo real e streaming de baixa latência.",
                  ["Transações bancárias.",
                   "Transferência confiável de arquivos.",
                   "Conexões SSH."],
                  "UDP é stateless e sem retransmissão, perfeito quando latência > confiabilidade."),
                q("O que `curl -v` mostra além do corpo?",
                  "Cabeçalhos da requisição e da resposta.",
                  ["Apenas o status code.",
                   "Apenas o JSON pretty-print.",
                   "Apenas tempo de resposta."],
                  "-v também mostra o handshake TLS, redirecionamentos e tempo de cada fase. "
                  "É a ferramenta de debug HTTP universal."),
            ],
        },
        # =====================================================================
        # 1.3 Bash / Shell Scripting
        # =====================================================================
        {
            "title": "Bash/Shell Scripting",
            "summary": "Automatizar tarefas repetitivas de forma robusta e segura.",
            "lesson": {
                "intro": (
                    "Bash é o esperanto da operação Linux: está em todo lugar, em todo "
                    "container, em todo CI. Saber bash bem é multiplicador imediato de "
                    "produtividade. Saber bash <em>mal</em> é fonte recorrente de "
                    "vulnerabilidades graves: scripts amadores em produção vazam segredo, "
                    "apagam dado errado, abrem RCE.<br><br>"
                    "Esta aula assume que você já viu <code>echo</code> e <code>if</code>. "
                    "Aqui vamos para o que diferencia um script descartável de um script que "
                    "você deixa rodar como root em produção sem perder o sono."
                ),
                "body": (
                    "<h3>1. Cabeçalho seguro: o 'unsafe at any speed' do bash</h3>"
                    "<p>Sempre comece com:</p>"
                    "<pre><code>#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    "IFS=$'\\n\\t'</code></pre>"
                    "<p>Cada flag resolve uma classe de bug:</p>"
                    "<ul>"
                    "<li><code>-e</code>: aborta no primeiro comando que retornar erro. Sem "
                    "isso, o script <em>continua</em> e você pode acabar deletando a base certa "
                    "depois de falhar criar o backup.</li>"
                    "<li><code>-u</code>: erro ao referenciar variável não definida. Pega "
                    "typos antes que virem string vazia em <code>rm -rf $TARGET/*</code>.</li>"
                    "<li><code>-o pipefail</code>: o status do pipe é o do <em>pior</em> "
                    "estágio. Sem isso, <code>backup_db | gzip &gt; out.gz</code> retorna 0 "
                    "mesmo se <code>backup_db</code> falhar.</li>"
                    "<li><code>IFS=$'\\n\\t'</code>: word-splitting só em quebra de linha e "
                    "tab. Evita bug clássico de nomes de arquivo com espaço.</li>"
                    "</ul>"
                    "<p>Depois você ativa <code>set -x</code> em modo debug e desativa em "
                    "produção. Para depurar uma seção específica:</p>"
                    "<pre><code>{ set -x; comando_problematico; } 2&gt;&amp;1 | tee /tmp/debug.log\n"
                    "set +x</code></pre>"

                    "<h3>2. Aspas, a primeira regra é citar tudo</h3>"
                    "<p>O ponto mais comum de bugs em bash é word-splitting e glob expansion "
                    "inesperado:</p>"
                    "<pre><code># RUIM: arquivo 'meu doc.txt' vira dois argumentos\n"
                    "rm $arquivo\n\n"
                    "# BOM\n"
                    "rm \"$arquivo\"\n\n"
                    "# RUIM: se $files for vazio, vira `for f in` (loop não executa, ok)\n"
                    "#       mas se for um glob solto, expande no momento errado\n"
                    "for f in $files; do echo $f; done\n\n"
                    "# BOM: array preserva elementos individualmente\n"
                    "files=( '/srv/a 1.txt' '/srv/b.txt' )\n"
                    "for f in \"${files[@]}\"; do echo \"$f\"; done</code></pre>"
                    "<p>Regra: <strong>cite toda variável ao expandir</strong>, exceto quando "
                    "você <em>quer</em> word-splitting (raro).</p>"

                    "<h3>3. Estruturas de controle modernas</h3>"
                    "<p>Prefira <code>[[ ... ]]</code> a <code>[ ... ]</code>, suporta regex, "
                    "operadores compostos e não tem armadilhas com strings vazias:</p>"
                    "<pre><code>if [[ -z \"$1\" ]]; then\n"
                    "  echo 'uso: deploy.sh &lt;ambiente&gt;' &gt;&amp;2\n"
                    "  exit 64    # EX_USAGE\n"
                    "fi\n\n"
                    "if [[ \"$ENV\" =~ ^(dev|staging|prod)$ ]]; then\n"
                    "  echo \"deploy em $ENV\"\n"
                    "fi\n\n"
                    "case \"$ENV\" in\n"
                    "  dev|staging)  HOST=internal.example.com ;;\n"
                    "  prod)         HOST=api.example.com ;;\n"
                    "  *)            echo 'ambiente inválido' &gt;&amp;2; exit 64 ;;\n"
                    "esac</code></pre>"

                    "<h3>4. Iterando arquivos com nome 'esquisito'</h3>"
                    "<p>Existe basicamente <em>uma</em> forma 100% segura, separador NUL:</p>"
                    "<pre><code># RUIM: quebra com espaço, tab ou newline no nome\n"
                    "for f in $(ls *.log); do\n"
                    "  process \"$f\"\n"
                    "done\n\n"
                    "# RUIM ainda: ls não é parseável\n"
                    "find . -name '*.log' | while read f; do process \"$f\"; done\n\n"
                    "# BOM: -print0 emite separadores NUL\n"
                    "find . -type f -name '*.log' -print0 | \\\n"
                    "  while IFS= read -r -d '' f; do\n"
                    "    process \"$f\"\n"
                    "  done\n\n"
                    "# Alternativa elegante com bash 4+ (mapfile)\n"
                    "mapfile -d '' -t files &lt; &lt;(find . -type f -name '*.log' -print0)\n"
                    "for f in \"${files[@]}\"; do process \"$f\"; done</code></pre>"

                    "<h3>5. Funções, retorno e erro propagado</h3>"
                    "<pre><code>require_env() {\n"
                    "  local var=$1\n"
                    "  if [[ -z \"${!var:-}\" ]]; then\n"
                    "    echo \"FATAL: variável $var não definida\" &gt;&amp;2\n"
                    "    return 1\n"
                    "  fi\n"
                    "}\n\n"
                    "deploy() {\n"
                    "  require_env GITHUB_TOKEN\n"
                    "  require_env DEPLOY_KEY\n"
                    "  # ...\n"
                    "}\n\n"
                    "deploy || { echo 'deploy falhou' &gt;&amp;2; exit 1; }</code></pre>"
                    "<p>Use <code>local</code> para variáveis dentro de função (evita "
                    "vazamento global). <code>${!var}</code> faz indireção "
                    "(referencia a variável cujo nome está em <code>$var</code>).</p>"

                    "<h3>6. Trap para cleanup determinístico</h3>"
                    "<pre><code>tmp=$(mktemp -d)\n"
                    "trap 'rm -rf \"$tmp\"' EXIT INT TERM\n\n"
                    "echo 'baixando…' &gt; \"$tmp/log\"\n"
                    "curl https://api.example.com/dump &gt; \"$tmp/dump.json\"\n"
                    "process \"$tmp/dump.json\"\n"
                    "# o trap cuida da limpeza mesmo se algo falhar</code></pre>"
                    "<p>Sem <code>trap</code>, um <code>exit 1</code> ou Ctrl+C deixa lixo em "
                    "<code>/tmp</code>. Em scripts longos isso entope disco.</p>"

                    "<h3>7. Validação de input, trate como hostil</h3>"
                    "<pre><code># Recebido por argumento ou variável de ambiente\n"
                    "name=${1:?uso: ./script.sh &lt;nome&gt;}\n\n"
                    "# Whitelist é melhor que blacklist\n"
                    "if [[ ! \"$name\" =~ ^[a-zA-Z0-9_-]{1,32}$ ]]; then\n"
                    "  echo \"nome inválido: $name\" &gt;&amp;2\n"
                    "  exit 64\n"
                    "fi\n\n"
                    "# NUNCA: rm -rf /srv/$name (com $name vazio = rm -rf /srv/)\n"
                    "# NUNCA: eval \"$name\"\n"
                    "# NUNCA: bash -c \"echo $name\"   ← injeção de comando</code></pre>"

                    "<h3>8. Logging com timestamp e níveis</h3>"
                    "<pre><code>log() {\n"
                    "  local level=$1; shift\n"
                    "  printf '%s [%s] %s\\n' \"$(date -Iseconds)\" \"$level\" \"$*\" &gt;&amp;2\n"
                    "}\n\n"
                    "log INFO  'iniciando deploy'\n"
                    "log WARN  'cache vazio, baixando do registry'\n"
                    "log ERROR 'falha ao subir container'</code></pre>"
                    "<p>Logue em <code>stderr</code> para que stdout fique livre para a saída "
                    "<em>útil</em> do script (que pode ser piped para outro comando).</p>"

                    "<h3>9. Anti-patterns que custam caro</h3>"
                    "<table style='border-collapse:collapse'>"
                    "<tr><td><code>eval \"$input\"</code></td>"
                    "<td>RCE garantido se input vier de fora.</td></tr>"
                    "<tr><td><code>rm -rf $dir/</code></td>"
                    "<td>Sem checar <code>$dir</code>, com <code>set -u</code> off, vira "
                    "<code>rm -rf /</code>.</td></tr>"
                    "<tr><td><code>curl ... | bash</code></td>"
                    "<td>Executa código remoto sem verificação. Se o servidor for comprometido, "
                    "RCE no seu host.</td></tr>"
                    "<tr><td><code>ssh host \"$cmd\"</code></td>"
                    "<td>Sem aspas adicionais e validação, injeção de comando.</td></tr>"
                    "<tr><td><code>readlink</code> sem <code>-f</code></td>"
                    "<td>Não resolve symlinks aninhados.</td></tr>"
                    "<tr><td><code>cat $file | grep …</code></td>"
                    "<td>Useless use of cat. Prefira <code>grep … &lt; $file</code>.</td></tr>"
                    "</table>"

                    "<h3>10. shellcheck, shfmt e quando subir para Python</h3>"
                    "<p><code>shellcheck</code> pega 95% dos bugs comuns automaticamente. "
                    "Integre na CI e no editor, falhe o pipeline em qualquer warning. "
                    "<code>shfmt</code> formata o código.</p>"
                    "<p>Bash brilha em scripts ≤ 150 linhas. Quando precisa de:</p>"
                    "<ul>"
                    "<li>Estruturas de dados não-triviais;</li>"
                    "<li>Lógica de retry/backoff complexa;</li>"
                    "<li>Concorrência além de <code>&amp;</code> simples;</li>"
                    "<li>Testes unitários reais;</li>"
                    "</ul>"
                    "<p>...suba para Python (com <code>typer</code>) ou Go. Tempo de manutenção "
                    "compensa.</p>"

                    "<h3>11. Caso real: o <code>rm -rf $STEAMROOT/*</code> da Steam</h3>"
                    "<p>Em 2015, o launcher da Steam para Linux trazia um script de "
                    "desinstalação que continha literalmente <code>rm -rf \"$STEAMROOT/\"*</code>. "
                    "Quando a variável estava vazia, o comando virava "
                    "<code>rm -rf \"/\"*</code> e <em>apagava todos os arquivos do usuário</em>, "
                    "o sistema todo, na verdade. O bug existia há anos. A correção foi de "
                    "uma linha: validar que <code>$STEAMROOT</code> não está vazio. "
                    "Isso é o que <code>set -u</code> e validação de input previnem."
                ),
                "practical": (
                    "Escreva um script <code>analyze_logs.sh</code> que:<br>"
                    "(a) recebe um diretório como argumento (validado por regex);<br>"
                    "(b) usa <code>set -euo pipefail</code> e <code>trap</code> para limpar "
                    "tmp;<br>"
                    "(c) encontra os 5 arquivos <code>.log</code> maiores recursivamente, "
                    "tratando nomes com espaço corretamente;<br>"
                    "(d) imprime estatísticas (linhas totais, ERROR/WARN/INFO) com "
                    "<code>awk</code>;<br>"
                    "(e) loga em stderr com timestamp em ISO-8601;<br>"
                    "(f) sai com código não-zero específico em cada falha (64 input, 65 fs, "
                    "66 dependência).<br>"
                    "Rode <code>shellcheck -S style</code> nele até zerar todos os warnings."
                ),
            },
            "materials": [
                m("Bash Reference Manual",
                  "https://www.gnu.org/software/bash/manual/bash.html", "docs", ""),
                m("Google Shell Style Guide",
                  "https://google.github.io/styleguide/shellguide.html",
                  "article", "Padrões reais de produção."),
                m("ShellCheck", "https://www.shellcheck.net/",
                  "tool", "Linter obrigatório para scripts bash."),
                m("Bash Pitfalls (Greg's Wiki)",
                  "https://mywiki.wooledge.org/BashPitfalls", "article",
                  "Catálogo de erros clássicos."),
                m("Advanced Bash-Scripting Guide",
                  "https://tldp.org/LDP/abs/html/", "book", ""),
                m("explainshell.com", "https://explainshell.com/",
                  "tool", "Quebra qualquer linha de shell em pedaços com explicação."),
            ],
            "questions": [
                q("Para que serve `set -e` em um script bash?",
                  "Aborta a execução se um comando retornar erro.",
                  ["Ativa modo verboso.",
                   "Define variável de ambiente.",
                   "Roda script em paralelo."],
                  "Sem -e, um falha intermediária passa despercebida e o script continua "
                  "como se tudo desse certo."),
                q("Qual a forma correta de citar uma variável?",
                  "echo \"$var\"", ["echo $var", "echo '$var'", "echo `var`"],
                  "Aspas duplas evitam word splitting e expansão de glob mantendo a expansão "
                  "da variável."),
                q("O que `pipefail` faz?",
                  "Faz o pipeline falhar se qualquer comando intermediário falhar.",
                  ["Recarrega o pipe automaticamente.",
                   "Suprime erros do pipe.",
                   "Retorna sempre 0."],
                  "Sem pipefail, `cmd1 | cmd2` retorna o status de cmd2 mesmo que cmd1 tenha "
                  "explodido, fonte recorrente de bugs silenciosos."),
                q("Como capturar a saída de um comando em uma variável?",
                  "result=$(comando)", ["result=`comando`", "result=$comando", "result=>'comando'"],
                  "Backticks aninham mal e são considerados legados; preferir $(...)."),
                q("Qual comando lista todos os scripts shell num diretório recursivamente?",
                  "find . -type f -name '*.sh'",
                  ["ls -la *.sh", "grep -r '*.sh'", "tree --shell"],
                  "ls não recursa por padrão; grep busca conteúdo, não nome. find é a ferramenta correta."),
                q("Por que `eval` com input externo é perigoso?",
                  "Permite execução arbitrária de código se a string vier de fora.",
                  ["É lento.", "Não funciona em macOS.", "Sempre retorna erro."],
                  "Eval interpreta a string como comando bash, então qualquer coisa do tipo "
                  "`; rm -rf /` no input é executada."),
                q("Como passar argumento posicional em script bash?",
                  "$1, $2, $3...", ["arg1, arg2", "&1, &2", "%1, %2"],
                  "$@ tem todos os argumentos; $# o número deles. Cite com aspas: \"$@\"."),
                q("Qual ferramenta detecta bugs comuns em scripts?",
                  "shellcheck", ["pylint", "eslint", "rubocop"],
                  "shellcheck é o linter de fato para bash/sh, integra com a maioria das IDEs."),
                q("`[[ -z \"$x\" ]]` é verdadeiro quando:",
                  "x está vazio ou não definida.",
                  ["x é igual a 0.", "x é um arquivo.", "x é diretório."],
                  "-z testa string vazia. -n é o oposto. Use sempre as aspas para evitar erro de sintaxe."),
                q("Qual o jeito recomendado de iterar arquivos com espaços no nome?",
                  "find ... -print0 | xargs -0",
                  ["for f in $(ls)", "ls | while read f", "echo *"],
                  "-print0/-0 separa por NUL em vez de espaço/quebra-de-linha, único jeito "
                  "100% seguro com nomes arbitrários."),
            ],
        },
        # =====================================================================
        # 1.4 SSH
        # =====================================================================
        {
            "title": "SSH & Chaves Criptográficas",
            "summary": "Acesso remoto seguro e gestão de identidades com chaves assimétricas.",
            "lesson": {
                "intro": (
                    "SSH é provavelmente o protocolo mais importante do dia a dia DevSecOps. "
                    "Você logou em servidor, deu git push, configurou ansible, fez deploy: tudo "
                    "isso tipicamente roda sobre SSH. E é onde se concentra muita "
                    "vulnerabilidade boba: chave fraca, chave compartilhada por humanos, "
                    "<code>authorized_keys</code> nunca rotacionada, <code>known_hosts</code> "
                    "ignorado, agent forwarding indo para servidor não confiável.<br><br>"
                    "Esta aula cobre o modelo mental de criptografia assimétrica como a usamos "
                    "em SSH, hardening do servidor (sshd_config), uso operacional do cliente, "
                    "e por que você deve sair de <code>authorized_keys</code> manual e ir para "
                    "uma CA SSH em qualquer ambiente sério."
                ),
                "body": (
                    "<h3>1. Modelo mental de criptografia assimétrica</h3>"
                    "<p>Cada lado tem um par de chaves matemáticamente ligadas:</p>"
                    "<ul>"
                    "<li>A <strong>chave privada</strong> nunca sai do dono. É secreta.</li>"
                    "<li>A <strong>chave pública</strong> pode ser distribuída livremente.</li>"
                    "</ul>"
                    "<p>O que uma cripta, a outra decifra (e vice-versa). Em SSH:</p>"
                    "<ol>"
                    "<li>Cliente prova posse da privada assinando um desafio enviado pelo "
                    "servidor.</li>"
                    "<li>Servidor verifica a assinatura com a pública (que está em "
                    "<code>~/.ssh/authorized_keys</code> do usuário).</li>"
                    "<li>Após autenticação, ambos derivam chaves <strong>simétricas</strong> "
                    "(AES, ChaCha20) para criptografar a sessão, assimétrico só é usado para "
                    "estabelecer a sessão, não para o tráfego em si (seria lento demais).</li>"
                    "</ol>"
                    "<p>O servidor também tem seu par: a chave pública do servidor (host key) "
                    "vai para o seu <code>~/.ssh/known_hosts</code> na primeira conexão. "
                    "Se na próxima vez for diferente, o cliente <em>recusa</em> com "
                    "<code>WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED</code>, pode ser "
                    "MITM ou rebuild legítimo do servidor.</p>"

                    "<h3>2. Gerando chaves modernas, Ed25519</h3>"
                    "<p>Em 2025+ o padrão é <strong>Ed25519</strong>:</p>"
                    "<pre><code>ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519 -C 'meu@email.com'</code></pre>"
                    "<ul>"
                    "<li><code>-t ed25519</code>: curva elíptica moderna; chave pública de "
                    "~68 bytes.</li>"
                    "<li><code>-a 100</code>: 100 rounds de KDF para a passphrase (mais lento "
                    "para força bruta).</li>"
                    "<li><code>-C</code>: comentário (apenas marcador, usado para identificar "
                    "a chave em <code>authorized_keys</code>).</li>"
                    "</ul>"
                    "<p>Sempre proteja com passphrase. Sem ela, qualquer um que tenha acesso "
                    "ao seu disco tem acesso a todos os seus servidores.</p>"
                    "<p>RSA-2048 está sendo aposentado; se precisar de RSA por compatibilidade, "
                    "use ≥ 3072 bits. ECDSA tem ressalvas (NIST curves), prefira Ed25519.</p>"

                    "<h3>3. ssh-agent: digitar passphrase uma vez por sessão</h3>"
                    "<pre><code>eval $(ssh-agent -s)\n"
                    "ssh-add -t 4h ~/.ssh/id_ed25519     # libera por 4 horas\n"
                    "ssh-add -l                           # lista chaves carregadas\n"
                    "ssh-add -D                           # remove todas (logout)</code></pre>"
                    "<p>O agent guarda a chave decifrada em memória e fala com o cliente SSH "
                    "via socket Unix (<code>$SSH_AUTH_SOCK</code>). Em desktops modernos "
                    "(macOS, GNOME), há agents nativos integrados.</p>"
                    "<p><strong>Cuidado com agent forwarding</strong> "
                    "(<code>ssh -A host</code>): o servidor de destino pode usar suas chaves "
                    "para se conectar a outros lugares enquanto a sessão estiver aberta. Se "
                    "ele estiver comprometido, vira pivô. Use <code>ProxyJump</code> em vez de "
                    "<code>-A</code> sempre que possível:</p>"
                    "<pre><code>ssh -J bastion.example.com app-01.internal</code></pre>"

                    "<h3>4. ~/.ssh/config, configuração que economiza horas</h3>"
                    "<pre><code># ~/.ssh/config\n"
                    "Host bastion\n"
                    "  HostName bastion.example.com\n"
                    "  User deploy\n"
                    "  IdentityFile ~/.ssh/id_ed25519\n"
                    "  IdentitiesOnly yes\n"
                    "  ServerAliveInterval 60\n"
                    "\n"
                    "Host app-*\n"
                    "  ProxyJump bastion\n"
                    "  User deploy\n"
                    "  IdentityFile ~/.ssh/id_ed25519\n"
                    "  IdentitiesOnly yes\n"
                    "\n"
                    "Host github.com\n"
                    "  IdentityFile ~/.ssh/id_ed25519_github\n"
                    "  IdentitiesOnly yes\n"
                    "  AddKeysToAgent yes</code></pre>"
                    "<p><code>IdentitiesOnly yes</code> é obrigatório se você tem várias "
                    "chaves: caso contrário, o cliente tenta todas e dispara "
                    "<code>MaxAuthTries</code> antes de chegar na correta.</p>"

                    "<h3>5. Endurecendo o servidor: sshd_config</h3>"
                    "<p>Em <code>/etc/ssh/sshd_config</code> (ou drop em "
                    "<code>/etc/ssh/sshd_config.d/</code>):</p>"
                    "<pre><code># Autenticação\n"
                    "PasswordAuthentication no\n"
                    "PermitRootLogin no\n"
                    "PubkeyAuthentication yes\n"
                    "ChallengeResponseAuthentication no\n"
                    "UsePAM yes              # mantém integração com pam_faillock\n"
                    "AuthenticationMethods publickey\n"
                    "\n"
                    "# Limites\n"
                    "MaxAuthTries 3\n"
                    "MaxSessions 4\n"
                    "LoginGraceTime 20\n"
                    "ClientAliveInterval 300\n"
                    "ClientAliveCountMax 2\n"
                    "\n"
                    "# Lista branca de quem pode logar\n"
                    "AllowUsers deploy ops\n"
                    "AllowGroups ssh-users\n"
                    "\n"
                    "# Cripto moderna (Mozilla 'modern')\n"
                    "KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org\n"
                    "Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com\n"
                    "MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com\n"
                    "\n"
                    "# Forwarding restritivo\n"
                    "AllowAgentForwarding no\n"
                    "AllowTcpForwarding no\n"
                    "X11Forwarding no\n"
                    "PermitTunnel no\n"
                    "\n"
                    "# Banner para deixar claro o que vai acontecer (legal em muitos países)\n"
                    "Banner /etc/issue.net</code></pre>"
                    "<p>Sempre teste antes de aplicar:</p>"
                    "<pre><code>sudo sshd -t                              # valida sintaxe\n"
                    "sudo systemctl reload sshd                 # recarrega sem dropar conexões\n"
                    "# em outra janela já aberta, tente novo login antes de fechar a primeira</code></pre>"

                    "<h3>6. Pegadinhas de permissão</h3>"
                    "<p>O OpenSSH é exigente:</p>"
                    "<pre><code>chmod 700 ~/.ssh\n"
                    "chmod 600 ~/.ssh/authorized_keys\n"
                    "chmod 600 ~/.ssh/id_ed25519\n"
                    "chmod 644 ~/.ssh/id_ed25519.pub\n"
                    "chown -R $USER:$USER ~/.ssh</code></pre>"
                    "<p>Se algo está mais aberto que isso, o sshd <em>silenciosamente</em> "
                    "ignora a chave, você só descobre olhando "
                    "<code>journalctl -u sshd</code>. É a fonte de bug mais frustrante de SSH.</p>"

                    "<h3>7. SSH com certificados (CA SSH), escala de verdade</h3>"
                    "<p>Em frota grande, distribuir <code>authorized_keys</code> manualmente "
                    "vira pesadelo: nova chave de funcionário precisa entrar em N hosts; "
                    "saída precisa remover de N hosts; rotação é prática raríssima. Solução: "
                    "<strong>certificados SSH</strong>.</p>"
                    "<p>Como funciona:</p>"
                    "<ol>"
                    "<li>Você tem uma <strong>CA</strong> (par de chaves dedicadas) com chave "
                    "privada bem guardada (Vault, HSM).</li>"
                    "<li>O servidor é configurado com "
                    "<code>TrustedUserCAKeys /etc/ssh/ca.pub</code>, confia em qualquer "
                    "chave assinada pela CA.</li>"
                    "<li>Funcionário pede um certificado para a CA (autenticando via SSO/MFA); "
                    "recebe um certificado com TTL curto (1h-8h) e principal "
                    "<code>deploy</code> ou <code>ops</code>.</li>"
                    "<li>SSH apresenta certificado, servidor valida assinatura da CA e "
                    "extrai principal.</li>"
                    "</ol>"
                    "<p>Vantagens: revogação central instantânea (CRL), zero gestão de "
                    "<code>authorized_keys</code> no servidor, log forensicamente útil "
                    "(<code>certificate ID</code> do funcionário), TTL curto (chave vazada "
                    "expira sozinha).</p>"
                    "<p>Ferramentas: <strong>HashiCorp Vault</strong> (SSH secrets engine), "
                    "<strong>Smallstep step-ca</strong>, <strong>Teleport</strong>, "
                    "<strong>BastionZero</strong>.</p>"

                    "<h3>8. SSH e CI/CD</h3>"
                    "<p>Anti-pattern clássico: chave SSH longa armazenada em segredo do "
                    "GitHub Actions/GitLab e usada para <code>scp</code> ao servidor. Chave "
                    "vaza, atacante tem acesso permanente. Padrões melhores:</p>"
                    "<ul>"
                    "<li><strong>OIDC + CA SSH</strong>: o pipeline troca um token JWT (com "
                    "claim do repo, branch e SHA) por um certificado SSH efêmero. Vault e "
                    "step-ca suportam.</li>"
                    "<li><strong>Self-hosted runner dentro da VPC</strong>: pipeline fala com "
                    "host privado, sem expor SSH na internet.</li>"
                    "<li><strong>Pull-based deploy</strong>: ArgoCD/Flux puxa do Git em vez "
                    "de o pipeline empurrar.</li>"
                    "</ul>"

                    "<h3>9. Caso real: o ataque GitHub.com de 2023 (RSA host key)</h3>"
                    "<p>Em março/2023, GitHub anunciou ter exposto sua chave RSA privada de "
                    "host por engano em um repositório público, por horas, qualquer um podia "
                    "fazer MITM em conexões SSH para <code>github.com</code> via RSA. O fix "
                    "foi rotacionar a host key e pedir para milhões de usuários atualizarem "
                    "<code>known_hosts</code>. Lições: (a) host key importa muito; "
                    "(b) tenha plano de rotação; (c) Ed25519 estava intacto, diversidade de "
                    "algoritmos ajudou.</p>"

                    "<h3>10. Anti-patterns recorrentes</h3>"
                    "<ul>"
                    "<li>Compartilhar chaves entre humanos ('chave do time').</li>"
                    "<li>Não usar passphrase 'porque é incômodo', agente resolve.</li>"
                    "<li>Aceitar host key cegamente em scripts "
                    "(<code>StrictHostKeyChecking=no</code>) sem registrar via "
                    "<code>ssh-keyscan</code> + verificação out-of-band.</li>"
                    "<li>Habilitar <code>PermitRootLogin yes</code> 'temporariamente' e "
                    "esquecer.</li>"
                    "<li>Deixar <code>AllowAgentForwarding yes</code> default em servidor "
                    "exposto.</li>"
                    "<li>Não rotacionar nunca, chave de 2017 ainda em "
                    "<code>authorized_keys</code> de 2025.</li>"
                    "</ul>"
                ),
                "practical": (
                    "Em duas VMs:<br>"
                    "(1) Gere uma chave Ed25519 com passphrase: "
                    "<code>ssh-keygen -t ed25519 -a 100</code>.<br>"
                    "(2) Copie para a outra VM com "
                    "<code>ssh-copy-id user@host</code>; verifique permissões.<br>"
                    "(3) No servidor, edite <code>/etc/ssh/sshd_config.d/99-hardening.conf</code> "
                    "com <code>PasswordAuthentication no</code>, "
                    "<code>PermitRootLogin no</code>, <code>MaxAuthTries 3</code>, "
                    "<code>AllowUsers $SEU_USER</code>. Valide com <code>sshd -t</code> e "
                    "recarregue com <code>systemctl reload sshd</code>.<br>"
                    "(4) <strong>Não feche a sessão atual</strong>. Em outro terminal, tente "
                    "logar com senha (deve falhar) e com a chave (deve passar).<br>"
                    "(5) <code>journalctl -u sshd -n 50</code> e veja a auditoria.<br>"
                    "(6) Bônus: configure um <code>~/.ssh/config</code> com host alias e "
                    "<code>ProxyJump</code>, depois <code>ssh app01</code> deve atravessar o "
                    "bastion sozinho."
                ),
            },
            "materials": [
                m("OpenSSH Manual", "https://www.openssh.com/manual.html", "docs", ""),
                m("SSH.com: Public Key Authentication",
                  "https://www.ssh.com/academy/ssh/public-key-authentication",
                  "article", ""),
                m("DigitalOcean: SSH Essentials",
                  "https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys",
                  "article", ""),
                m("Mozilla SSH Guidelines",
                  "https://infosec.mozilla.org/guidelines/openssh",
                  "article", "Recomendações endurecidas."),
                m("Why Ed25519",
                  "https://blog.g3rt.nl/upgrade-your-ssh-keys.html", "article", ""),
                m("Smallstep: SSH certificates",
                  "https://smallstep.com/blog/use-ssh-certificates/",
                  "article", "Sair de authorized_keys para PKI."),
            ],
            "questions": [
                q("Qual algoritmo é recomendado para novas chaves SSH?",
                  "Ed25519",
                  ["DSA", "RSA-1024", "MD5"],
                  "Ed25519 oferece chave curta, assinatura rápida e segurança equivalente a RSA-3072+. "
                  "DSA está depreciado, RSA-1024 é fraco e MD5 nem é algoritmo de chave."),
                q("Onde fica a chave pública do usuário no servidor?",
                  "~/.ssh/authorized_keys",
                  ["/etc/passwd", "~/.bashrc", "/root/keys.pub"],
                  "Cada usuário do servidor mantém suas chaves autorizadas no próprio home."),
                q("Qual diretiva no `sshd_config` desabilita login com senha?",
                  "PasswordAuthentication no",
                  ["AllowPassword false", "DenyPassword yes", "DisablePassword on"],
                  "Após mudar, é preciso recarregar o sshd (`systemctl reload sshd`)."),
                q("O que `ssh-agent` resolve?",
                  "Mantém a chave privada decifrada em memória durante a sessão.",
                  ["Sincroniza chaves entre máquinas.",
                   "Gera novas chaves automaticamente.",
                   "Substitui o openssh-server."],
                  "Sem agent, você teria que digitar a passphrase a cada conexão. Com forwarding, "
                  "use com cuidado: agent forwarding mal configurado vaza a identidade."),
                q("Qual permissão é exigida pelo OpenSSH para `~/.ssh/authorized_keys`?",
                  "600 (rw apenas para o dono).",
                  ["644", "777", "400 com dono root"],
                  "O sshd recusa silenciosamente a chave se o arquivo for legível por outros."),
                q("Como copiar a chave pública para o servidor?",
                  "ssh-copy-id user@host",
                  ["scp -p chave.pub", "rsync key", "ssh --send-key"],
                  "ssh-copy-id já faz append em authorized_keys e ajusta permissões."),
                q("Qual variável de ambiente o ssh-agent define?",
                  "SSH_AUTH_SOCK",
                  ["SSH_KEY", "SSH_PASS", "SSH_TOKEN"],
                  "É o socket Unix por onde o cliente fala com o agent."),
                q("O que é uma chave de host em SSH?",
                  "Chave que identifica o servidor para evitar MITM.",
                  ["Chave do usuário convidado.",
                   "Chave para criptografar pacotes.",
                   "Chave de root."],
                  "Na primeira conexão, você aceita a chave; depois ela vai pra known_hosts. "
                  "Se mudar inesperadamente, é sinal de MITM (ou rebuild legítimo)."),
                q("Por que evitar PermitRootLogin yes?",
                  "Aumenta a superfície de ataque dando acesso direto a um usuário onipotente.",
                  ["Reduz performance.",
                   "Não é compatível com Ed25519.",
                   "Bloqueia o sshd."],
                  "Use um usuário comum com sudo; tenha rastreabilidade individual no audit log."),
                q("Qual a vantagem de SSH com certificados?",
                  "Eliminar autorização chave-a-chave em cada servidor; rotação centralizada.",
                  ["Senhas mais curtas.",
                   "Não precisa do sshd.",
                   "Funciona sem rede."],
                  "Servidores confiam na CA. Emite certificado com TTL de horas e revoga "
                  "centralmente, escala muito melhor que authorized_keys."),
            ],
        },
        # =====================================================================
        # 1.5 PoLP
        # =====================================================================
        {
            "title": "Princípio do Privilégio Mínimo (PoLP)",
            "summary": "Por que nunca rodar nada como 'root', e como aplicar isso em todos os níveis.",
            "lesson": {
                "intro": (
                    "Princípio do Privilégio Mínimo (PoLP, do inglês <em>Principle of Least "
                    "Privilege</em>) é a ideia simples e devastadora: cada identidade, "
                    "humano, serviço, processo, role IAM, service account, deve ter "
                    "<em>exatamente</em> os privilégios necessários para sua função. Nada além.<br><br>"
                    "Quase toda escalada de privilégios em incidentes reais começa explorando "
                    "uma identidade que tinha mais poder do que precisava. Capital One (2019), "
                    "SolarWinds (2020), Uber (2022), todos têm violação de PoLP no caminho "
                    "crítico do ataque.<br><br>"
                    "Esta aula mostra como aplicar PoLP em cinco camadas: usuários do SO, "
                    "sudo, systemd, containers (Docker/K8s) e cloud (IAM)."
                ),
                "body": (
                    "<h3>1. Por que PoLP é fundamental</h3>"
                    "<p>Pense em PoLP como <strong>blast radius</strong>: o quanto se "
                    "compromete quando uma identidade vaza. Se a aplicação web tem credencial "
                    "<code>AdministratorAccess</code> em AWS e é comprometida, atacante "
                    "controla toda a conta, derruba banco, exfiltra S3, sobe instância para "
                    "minerar crypto. Se a mesma app tinha apenas <code>s3:GetObject</code> "
                    "num bucket específico, o blast radius cabe em um relatório.</p>"
                    "<p>PoLP é defensa em profundidade <em>posta em prática</em>. Não evita "
                    "comprometimento; limita as consequências. É o que separa um incidente "
                    "constrangedor de uma crise de imagem.</p>"

                    "<h3>2. PoLP no host Linux: usuários dedicados por serviço</h3>"
                    "<p>Cada serviço (nginx, postgres, app) deve ter usuário próprio:</p>"
                    "<pre><code>useradd --system --shell /usr/sbin/nologin --home-dir /var/lib/app app\n"
                    "chown -R app:app /opt/app /var/lib/app /var/log/app</code></pre>"
                    "<p>Vantagens:</p>"
                    "<ul>"
                    "<li>Compromisso da app não dá acesso a outros serviços.</li>"
                    "<li>Permissões granulares: app não consegue ler "
                    "<code>/etc/postgres</code>.</li>"
                    "<li>Auditoria por usuário: <code>journalctl _UID=$(id -u app)</code>.</li>"
                    "<li>Limites por usuário (ulimit, cgroups).</li>"
                    "</ul>"

                    "<h3>3. systemd hardening: a camada que muita gente ignora</h3>"
                    "<p>Em <code>/etc/systemd/system/app.service</code>:</p>"
                    "<pre><code>[Service]\n"
                    "ExecStart=/opt/app/bin/server\n"
                    "User=app\n"
                    "Group=app\n"
                    "\n"
                    "# Identidade\n"
                    "NoNewPrivileges=true       # impede setuid/setcap em descendentes\n"
                    "\n"
                    "# Filesystem\n"
                    "ProtectSystem=strict       # tudo readonly exceto paths permitidos\n"
                    "ProtectHome=true           # /home, /root, /run/user invisíveis\n"
                    "PrivateTmp=true            # /tmp isolado por instância\n"
                    "ReadWritePaths=/var/lib/app /var/log/app\n"
                    "\n"
                    "# Capabilities\n"
                    "CapabilityBoundingSet=     # vazio = abre mão de tudo\n"
                    "AmbientCapabilities=\n"
                    "\n"
                    "# Syscalls (via seccomp-bpf)\n"
                    "SystemCallFilter=@system-service\n"
                    "SystemCallErrorNumber=EPERM\n"
                    "\n"
                    "# Rede\n"
                    "RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX\n"
                    "PrivateNetwork=false       # true = sem acesso de rede algum\n"
                    "\n"
                    "# Outros\n"
                    "ProtectKernelModules=true\n"
                    "ProtectKernelTunables=true\n"
                    "ProtectControlGroups=true\n"
                    "RestrictNamespaces=true\n"
                    "LockPersonality=true\n"
                    "MemoryDenyWriteExecute=true</code></pre>"
                    "<p>Para auditar o que uma unit já tem habilitado:</p>"
                    "<pre><code>systemd-analyze security app.service</code></pre>"
                    "<p>Ele dá uma nota de 0 a 10 com sugestões. Mire em &lt; 3 (mais seguro).</p>"

                    "<h3>4. sudo, mas com critério</h3>"
                    "<p><code>ALL=(ALL:ALL) ALL</code> é o atalho mais comum e o pior. Em "
                    "<code>/etc/sudoers.d/deploy</code>:</p>"
                    "<pre><code># Usuário deploy só pode reiniciar o nginx, sem senha\n"
                    "deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart nginx\n"
                    "deploy ALL=(root) NOPASSWD: /usr/bin/systemctl reload nginx\n"
                    "\n"
                    "# Negar shell escapes\n"
                    "Defaults:deploy !requiretty\n"
                    "Defaults:deploy log_year, logfile=/var/log/sudo-deploy.log</code></pre>"
                    "<p>Sempre edite com <code>visudo -f /etc/sudoers.d/arquivo</code>, ele "
                    "valida sintaxe antes de salvar. Sem isso, um typo deixa todo mundo sem "
                    "sudo.</p>"

                    "<h3>5. PoLP em containers Docker</h3>"
                    "<pre><code># Dockerfile\n"
                    "FROM python:3.12-slim\n"
                    "RUN useradd --uid 10001 --system --no-create-home app\n"
                    "WORKDIR /app\n"
                    "COPY --chown=app:app . .\n"
                    "RUN pip install --no-cache-dir -r requirements.txt\n"
                    "USER app                          # nunca rode como root\n"
                    "EXPOSE 8000\n"
                    "CMD [\"gunicorn\", \"-b\", \"0.0.0.0:8000\", \"app.wsgi\"]</code></pre>"
                    "<p>No <code>docker run</code>, vá além:</p>"
                    "<pre><code>docker run --rm \\\n"
                    "  --user 10001:10001 \\\n"
                    "  --read-only \\\n"
                    "  --tmpfs /tmp \\\n"
                    "  --cap-drop=ALL \\\n"
                    "  --cap-add=NET_BIND_SERVICE \\\n"
                    "  --security-opt=no-new-privileges \\\n"
                    "  --pids-limit 200 \\\n"
                    "  -p 8000:8000 myapp:1.0</code></pre>"

                    "<h3>6. PoLP em Kubernetes (securityContext)</h3>"
                    "<pre><code>apiVersion: apps/v1\n"
                    "kind: Deployment\n"
                    "metadata: { name: app }\n"
                    "spec:\n"
                    "  template:\n"
                    "    spec:\n"
                    "      automountServiceAccountToken: false   # se a app não chama K8s API\n"
                    "      securityContext:\n"
                    "        runAsNonRoot: true\n"
                    "        runAsUser: 10001\n"
                    "        fsGroup: 10001\n"
                    "        seccompProfile: { type: RuntimeDefault }\n"
                    "      containers:\n"
                    "      - name: app\n"
                    "        image: myapp:1.0\n"
                    "        securityContext:\n"
                    "          allowPrivilegeEscalation: false\n"
                    "          readOnlyRootFilesystem: true\n"
                    "          capabilities: { drop: [\"ALL\"] }</code></pre>"
                    "<p>Use <strong>Pod Security Standards</strong> (restricted) no namespace "
                    "para forçar o padrão em todo deploy:</p>"
                    "<pre><code>kubectl label ns app pod-security.kubernetes.io/enforce=restricted</code></pre>"

                    "<h3>7. PoLP em Cloud (IAM)</h3>"
                    "<p>Princípios:</p>"
                    "<ul>"
                    "<li><strong>Roles, não chaves estáticas</strong>: workload identity "
                    "(IRSA na AWS, Workload Identity no GKE, Managed Identity no AKS).</li>"
                    "<li><strong>Policies granulares</strong>: <code>s3:GetObject</code> em "
                    "<code>arn:aws:s3:::bucket-x/*</code>, não <code>s3:*</code> em "
                    "<code>*</code>.</li>"
                    "<li><strong>Permission Boundaries / SCPs</strong>: guard-rails "
                    "estruturais que nem o admin de uma sub-conta pode exceder.</li>"
                    "<li><strong>Condicionais</strong>: <code>aws:SourceVpc</code>, "
                    "<code>aws:MultiFactorAuthPresent</code>, "
                    "<code>aws:RequestedRegion</code>.</li>"
                    "<li><strong>Tempo limitado</strong>: STS AssumeRole com TTL curto.</li>"
                    "</ul>"
                    "<pre><code>// IAM policy mínima\n"
                    "{\n"
                    "  \"Version\": \"2012-10-17\",\n"
                    "  \"Statement\": [\n"
                    "    {\n"
                    "      \"Effect\": \"Allow\",\n"
                    "      \"Action\": [\"s3:GetObject\"],\n"
                    "      \"Resource\": \"arn:aws:s3:::reports-prod/*\",\n"
                    "      \"Condition\": {\n"
                    "        \"StringEquals\": {\"aws:SourceVpc\": \"vpc-abc\"}\n"
                    "      }\n"
                    "    }\n"
                    "  ]\n"
                    "}</code></pre>"

                    "<h3>8. Privilege creep, o inimigo invisível</h3>"
                    "<p>Sem auditoria, todo mundo só <em>adiciona</em> permissão. Ninguém "
                    "remove. Em 2 anos, a IAM role 'app-prod' que começou com "
                    "<code>s3:GetObject</code> em um bucket está com 47 permissões e ninguém "
                    "sabe quais são realmente usadas.</p>"
                    "<p>Ferramentas para auditar:</p>"
                    "<ul>"
                    "<li><strong>AWS IAM Access Analyzer</strong>: gera relatório do que cada "
                    "principal <em>realmente</em> usou nos últimos 90 dias.</li>"
                    "<li><strong>Cloudsplaining</strong> (Salesforce): scanner que avalia "
                    "policies por risco.</li>"
                    "<li><strong>Steampipe</strong>: SQL sobre seu cloud, "
                    "<code>select * from aws_iam_role where assume_role_policy like '%*%'</code>.</li>"
                    "<li><strong>cloudquery</strong>: catálogo continuamente atualizado.</li>"
                    "</ul>"

                    "<h3>9. Caso real: Capital One 2019</h3>"
                    "<p>Atacante explorou um WAF mal configurado (SSRF) para obter "
                    "credenciais IAM via <code>169.254.169.254</code>. As credenciais tinham "
                    "permissão <code>s3:ListAllMyBuckets</code> e <code>s3:GetObject</code> "
                    "<em>em todos os buckets da empresa</em>, para 'simplicidade'. "
                    "Resultado: 100M de registros de clientes vazados, multa de US$ 80M, "
                    "CISO demitida. Se a role tivesse acesso só ao bucket que o WAF realmente "
                    "precisava, o vazamento seria de 1% do que foi.</p>"

                    "<h3>10. Anti-patterns</h3>"
                    "<ul>"
                    "<li><code>chmod 777</code> 'porque tava dando erro'.</li>"
                    "<li><code>kubectl create clusterrolebinding app-admin --clusterrole=cluster-admin</code>.</li>"
                    "<li>App rodando como root no container 'porque a imagem oficial é assim'.</li>"
                    "<li>IAM role <code>*</code> em <code>*</code> 'depois eu restrinjo'.</li>"
                    "<li>Compartilhar credencial de service account entre humanos.</li>"
                    "<li>Acesso permanente em vez de just-in-time (JIT).</li>"
                    "</ul>"
                    "<p>Para cada um deles, há uma alternativa segura que custa minutos a "
                    "configurar e horas economizadas em incidente.</p>"
                ),
                "practical": (
                    "(1) Pegue um serviço systemd existente em sua máquina e rode "
                    "<code>systemd-analyze security &lt;unit&gt;</code>. Anote a nota.<br>"
                    "(2) Crie drop-in em "
                    "<code>/etc/systemd/system/&lt;unit&gt;.d/hardening.conf</code> com "
                    "<code>NoNewPrivileges=true</code>, <code>PrivateTmp=true</code>, "
                    "<code>ProtectSystem=strict</code>, <code>ProtectHome=true</code> e "
                    "<code>ReadWritePaths=</code> só para os caminhos necessários.<br>"
                    "(3) <code>systemctl daemon-reload &amp;&amp; systemctl restart &lt;unit&gt;</code> "
                    "e veja se quebra. Se quebrar, leia <code>journalctl</code> e ajuste "
                    "<code>ReadWritePaths</code>.<br>"
                    "(4) Rode <code>systemd-analyze security</code> de novo. A nota deve cair "
                    "(mais seguro = nota menor).<br>"
                    "(5) Bônus: faça o mesmo exercício em um Dockerfile, adicione "
                    "<code>USER</code> não-root, <code>--cap-drop=ALL</code>, "
                    "<code>--read-only</code> e veja se app continua funcionando."
                ),
            },
            "materials": [
                m("OWASP Top 10: Broken Access Control",
                  "https://owasp.org/Top10/A01_2021-Broken_Access_Control/", "docs", ""),
                m("NIST: Least Privilege",
                  "https://csrc.nist.gov/glossary/term/least_privilege", "docs", ""),
                m("Run Docker as non-root",
                  "https://docs.docker.com/engine/security/userns-remap/", "docs", ""),
                m("man capabilities(7)",
                  "https://man7.org/linux/man-pages/man7/capabilities.7.html", "docs", ""),
                m("AWS IAM Best Practices",
                  "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html",
                  "docs", ""),
                m("systemd hardening cheatsheet",
                  "https://www.redhat.com/sysadmin/mastering-systemd",
                  "article", ""),
            ],
            "questions": [
                q("Por que evitar rodar serviços como root?",
                  "Se o serviço for comprometido, o atacante já tem privilégios totais.",
                  ["Porque o root é mais lento.",
                   "Porque o root não pode usar HTTPS.",
                   "Porque o root reinicia o sistema."],
                  "Cada vulnerabilidade (heartbleed, log4shell, etc.) num serviço root vira "
                  "comprometimento total da máquina."),
                q("Qual arquivo controla regras de `sudo`?",
                  "/etc/sudoers (e /etc/sudoers.d/)",
                  ["/etc/passwd", "/root/.bashrc", "/var/log/sudo"],
                  "Edite com `visudo` ou drops em /etc/sudoers.d/, que evita corromper o arquivo principal."),
                q("O que fazem as Linux capabilities?",
                  "Decompõem privilégios de root em grãos menores (ex.: NET_BIND_SERVICE).",
                  ["Substituem firewalls.",
                   "Aceleram syscalls.",
                   "Implementam quotas de disco."],
                  "Em vez de root inteiro, dê só CAP_NET_BIND_SERVICE para um binário web bindar a 80/443."),
                q("Em Kubernetes, qual campo do PodSpec exige que o container rode como não-root?",
                  "securityContext.runAsNonRoot: true",
                  ["spec.privileged: false",
                   "metadata.root: false",
                   "spec.uid: 0"],
                  "Combine com runAsUser específico e a imagem precisa estar pronta para isso."),
                q("Qual prática viola PoLP?",
                  "Dar 'AdministratorAccess' a uma role de aplicação.",
                  ["Usar IAM com policies específicas.",
                   "Rotacionar credenciais.",
                   "Aplicar service accounts dedicadas."],
                  "Aplicação não precisa de admin. PoLP é dar exatamente o que ela usa."),
                q("`chmod 777 /opt/app` é problemático porque:",
                  "Qualquer usuário do sistema pode escrever, ler e executar, escalada trivial.",
                  ["É mais lento.",
                   "Não funciona em ext4.",
                   "Apaga o conteúdo."],
                  "Atacante com qualquer usuário do sistema injeta payload no app legítimo."),
                q("O que é uma 'identity-based policy' em IAM?",
                  "Regras anexadas a um usuário/role definindo o que pode fazer.",
                  ["Senha rotativa.",
                   "Backup criptografado.",
                   "Token DNS."],
                  "Resource-based policies, em contraste, ficam no recurso (ex.: bucket policy)."),
                q("Qual ferramenta confina syscalls de processos no Linux?",
                  "seccomp",
                  ["iptables", "cron", "udev"],
                  "seccomp-bpf permite whitelistar quais syscalls um processo pode executar, "
                  "Docker e K8s usam isso."),
                q("Quando uso 'sudo -i', o que acontece?",
                  "Inicio um shell de login como root.",
                  ["Roda em modo lento.",
                   "Apenas verifico se sou sudo.",
                   "Atualizo o sistema."],
                  "-i carrega o ambiente de login do root; -s mantém o ambiente atual; "
                  "sem flags, executa um comando único."),
                q("A rotação periódica de credenciais ajuda PoLP porque:",
                  "Reduz a janela de exploração caso uma credencial vaze.",
                  ["Aumenta a entropia.",
                   "Faz log do uso.",
                   "Substitui MFA."],
                  "Não substitui PoLP, mas limita o blast radius de um vazamento."),
            ],
        },
        # =====================================================================
        # 1.6 Firewall
        # =====================================================================
        {
            "title": "Firewall Básico",
            "summary": "Configuração de regras de entrada/saída com UFW/iptables/nftables.",
            "lesson": {
                "intro": (
                    "Firewall é a primeira linha de defesa do host. Não substitui as outras "
                    "camadas (TLS, autenticação, validação de input), mas filtra ruído e "
                    "bloqueia ataques de oportunidade que constituem 90% do tráfego malicioso "
                    "que chega a um IP público.<br><br>"
                    "Esta aula cobre o filtro de pacotes do kernel Linux (netfilter) e suas "
                    "interfaces históricas (iptables) e modernas (nftables, ufw), além de "
                    "padrões operacionais e armadilhas que travam admins fora do servidor."
                ),
                "body": (
                    "<h3>1. O subsystem netfilter</h3>"
                    "<p>O kernel Linux tem um framework de filtro de pacotes chamado "
                    "<strong>netfilter</strong>, com hooks em pontos do caminho do pacote:</p>"
                    "<ul>"
                    "<li><code>PRE-ROUTING</code>: antes de decidir destino (NAT entrada).</li>"
                    "<li><code>INPUT</code>: pacote destinado ao próprio host.</li>"
                    "<li><code>FORWARD</code>: pacote roteado pela máquina (gateway/router).</li>"
                    "<li><code>OUTPUT</code>: pacote saindo do host.</li>"
                    "<li><code>POST-ROUTING</code>: depois de roteado (NAT saída).</li>"
                    "</ul>"
                    "<p>As interfaces de usuário (iptables/nftables/ufw) só montam regras "
                    "nessas hooks. Trocar de interface não muda o motor.</p>"

                    "<h3>2. iptables vs nftables vs ufw</h3>"
                    "<p>Linha do tempo:</p>"
                    "<ul>"
                    "<li><strong>iptables</strong> (1998): clássico, sintaxe verbosa, "
                    "tabela separada para IPv6 (ip6tables), ARP, ebtables.</li>"
                    "<li><strong>nftables</strong> (2014): substituto unificado, sintaxe "
                    "nova, performance melhor, IPv4+IPv6 numa só árvore. Em distros novas "
                    "(Debian 11+, RHEL 9, Ubuntu 22.04+), <code>iptables</code> é só um shim "
                    "que traduz para nftables.</li>"
                    "<li><strong>UFW</strong> (Uncomplicated Firewall): wrapper amigável "
                    "para iniciantes. <code>ufw allow ssh</code> e pronto.</li>"
                    "<li><strong>firewalld</strong> (RHEL/Fedora): wrapper diferente, "
                    "orientado a 'zonas'.</li>"
                    "</ul>"

                    "<h3>3. UFW na prática</h3>"
                    "<pre><code># Estado / status\n"
                    "ufw status verbose\n"
                    "ufw status numbered\n"
                    "\n"
                    "# Política default (default-deny inbound é o caminho)\n"
                    "ufw default deny incoming\n"
                    "ufw default allow outgoing\n"
                    "\n"
                    "# Regras\n"
                    "ufw allow ssh                            # equivale a 22/tcp\n"
                    "ufw allow 80,443/tcp                     # web\n"
                    "ufw allow from 10.0.1.0/24 to any port 5432  # postgres só da subnet\n"
                    "ufw limit ssh                            # rate limit (anti brute force)\n"
                    "\n"
                    "# Aplicar\n"
                    "ufw enable\n"
                    "\n"
                    "# Remover regra\n"
                    "ufw status numbered\n"
                    "ufw delete 3</code></pre>"
                    "<p><code>ufw limit</code> bloqueia IPs com mais de 6 conexões em 30s, "
                    "útil contra brute-force a SSH. Para resposta mais agressiva, combine com "
                    "<code>fail2ban</code> que banem por mais tempo e em mais portas.</p>"

                    "<h3>4. nftables raw, para quando UFW não basta</h3>"
                    "<pre><code># /etc/nftables.conf\n"
                    "table inet filter {\n"
                    "  chain input {\n"
                    "    type filter hook input priority 0; policy drop;\n"
                    "    \n"
                    "    iif lo accept\n"
                    "    ct state established,related accept\n"
                    "    ct state invalid drop\n"
                    "    \n"
                    "    icmp type echo-request limit rate 5/second accept\n"
                    "    icmpv6 type { echo-request, nd-neighbor-solicit, nd-router-advert, \\\n"
                    "                  nd-neighbor-advert } accept\n"
                    "    \n"
                    "    tcp dport 22 limit rate 10/minute accept    # ssh com rate limit\n"
                    "    tcp dport { 80, 443 } accept                 # web\n"
                    "    \n"
                    "    log prefix \"nft drop: \" level info limit rate 5/minute\n"
                    "  }\n"
                    "  chain forward { type filter hook forward priority 0; policy drop; }\n"
                    "  chain output  { type filter hook output  priority 0; policy accept; }\n"
                    "}</code></pre>"
                    "<p>Aplicar: <code>nft -f /etc/nftables.conf &amp;&amp; "
                    "systemctl enable nftables</code>.</p>"

                    "<h3>5. DROP vs REJECT vs ACCEPT</h3>"
                    "<table>"
                    "<tr><td><code>ACCEPT</code></td><td>passa</td></tr>"
                    "<tr><td><code>DROP</code></td><td>descarta silenciosamente. Atacante vê "
                    "timeout, mais difícil de mapear. Padrão em internet pública.</td></tr>"
                    "<tr><td><code>REJECT</code></td><td>responde com ICMP "
                    "<em>port-unreachable</em> ou TCP RST. 'Mais educado'; cliente legítimo "
                    "descobre o erro mais rápido. Bom em rede interna.</td></tr>"
                    "</table>"
                    "<p>Conntrack (<code>ct state established,related accept</code>) é o que "
                    "permite respostas de conexões iniciadas pelo host de saírem sem regra "
                    "explícita.</p>"

                    "<h3>6. Cuidados em produção: não se trave fora!</h3>"
                    "<p>Antes de aplicar regras restritivas em SSH remoto:</p>"
                    "<pre><code># Plano B: reverte automaticamente em 5 min se você não desativar\n"
                    "echo 'iptables-restore &lt; /tmp/rules.backup' | at now +5 minutes\n"
                    "\n"
                    "iptables-save &gt; /tmp/rules.backup\n"
                    "# ... aplica novas regras ...\n"
                    "# se você confirma que continua funcionando:\n"
                    "atrm $(atq | tail -1 | awk '{print $1}')</code></pre>"
                    "<p>Para nftables: <code>nft list ruleset &gt; /tmp/before.nft</code> "
                    "antes; reverter com <code>nft -f /tmp/before.nft</code>.</p>"
                    "<p>Sempre <strong>persista</strong> as regras: distros costumam ter "
                    "<code>netfilter-persistent</code>, <code>iptables-persistent</code> ou "
                    "<code>nftables.service</code> que carrega as regras no boot. Sem isso, um "
                    "reboot zera tudo e você fica com host wide-open.</p>"

                    "<h3>7. Limites de firewall L3/L4</h3>"
                    "<p>Firewall por porta não enxerga:</p>"
                    "<ul>"
                    "<li>Conteúdo HTTPS (criptografado).</li>"
                    "<li>Lógica de aplicação (SQLi, XSS, RCE).</li>"
                    "<li>Comportamento de usuário legítimo (credential stuffing com IPs "
                    "rotativos).</li>"
                    "</ul>"
                    "<p>Para isso existe a camada 7:</p>"
                    "<ul>"
                    "<li><strong>WAF</strong> (Web Application Firewall): ModSecurity, "
                    "Cloudflare, AWS WAF, Azure FrontDoor.</li>"
                    "<li><strong>API Gateway</strong>: Kong, Tyk, AWS API Gateway, rate "
                    "limit por chave, schema validation.</li>"
                    "<li><strong>Service Mesh</strong>: Istio, Linkerd, autenticação mTLS "
                    "entre serviços.</li>"
                    "</ul>"

                    "<h3>8. Firewall em cloud: Security Groups e NACLs</h3>"
                    "<p>Em AWS (e equivalentes):</p>"
                    "<ul>"
                    "<li><strong>Security Group</strong>: stateful, anexa em ENI/instância. "
                    "Default deny inbound, allow outbound. Regra de saída pode ser "
                    "destinada a outro SG (composição).</li>"
                    "<li><strong>Network ACL</strong>: stateless, em subnet. Regras "
                    "numeradas (avaliadas em ordem). Útil para bloquear IPs maliciosos sem "
                    "tocar no SG.</li>"
                    "</ul>"
                    "<p>Use Security Group como firewall de aplicação ('app fala com "
                    "postgres') e NACL como guard-rail por subnet ('subnet privada não recebe "
                    "internet').</p>"

                    "<h3>9. Caso real: o ipv6-bypass</h3>"
                    "<p>Por anos, admins configuravam <code>iptables</code> mas esqueciam "
                    "<code>ip6tables</code>, deixando IPv6 totalmente aberto. Atacantes "
                    "automatizados descobriam o IPv6 do host (geralmente exposto em DNS) e "
                    "entravam direto. Em 2014, isso ficou famoso quando "
                    "<code>kubelet</code> em K8s expunha-se em IPv6 por default. Lição: "
                    "use <code>nftables</code> com tabela <code>inet</code> (filtra IPv4 e "
                    "IPv6 juntos) ou seja explícito em ambas as stacks.</p>"

                    "<h3>10. Checklist de hardening</h3>"
                    "<ol>"
                    "<li>Default-deny inbound; default-allow outbound (com revisão "
                    "periódica).</li>"
                    "<li>Apenas portas estritamente necessárias abertas.</li>"
                    "<li>SSH com rate-limit (<code>ufw limit</code> + fail2ban).</li>"
                    "<li>ICMP echo aceitando mas com rate-limit.</li>"
                    "<li>Conntrack para established/related; drop para invalid.</li>"
                    "<li>Logs em todos os DROP no início (sample 5/min para não encher "
                    "disco).</li>"
                    "<li>Persistência configurada (sobrevive a reboot).</li>"
                    "<li>IPv6 também filtrado.</li>"
                    "<li>Plano de reversão antes de qualquer mudança remota.</li>"
                    "<li>Auditoria periódica: o que cada porta aberta serve?</li>"
                    "</ol>"
                ),
                "practical": (
                    "Em uma VM:<br>"
                    "(1) <code>ufw default deny incoming</code> e "
                    "<code>ufw default allow outgoing</code>.<br>"
                    "(2) <code>ufw limit ssh</code> e <code>ufw allow 80,443/tcp</code>.<br>"
                    "(3) <code>ufw enable</code>; verifique com <code>ufw status verbose</code>.<br>"
                    "(4) De <em>outra</em> máquina, rode "
                    "<code>nmap -sS -p 1-1024 &lt;ip&gt;</code>, só 22, 80, 443 devem "
                    "aparecer.<br>"
                    "(5) Faça 10 tentativas de SSH com senha errada de uma terceira máquina "
                    "(use <code>sshpass</code>) e veja o rate-limit kicar, IP banido por "
                    "alguns minutos.<br>"
                    "(6) Bônus: reescreva as mesmas regras em nftables raw e veja "
                    "<code>nft list ruleset</code>."
                ),
            },
            "materials": [
                m("UFW, Ubuntu Help", "https://help.ubuntu.com/community/UFW", "docs", ""),
                m("nftables wiki",
                  "https://wiki.nftables.org/wiki-nftables/index.php/Main_Page", "docs", ""),
                m("iptables tutorial",
                  "https://www.frozentux.net/iptables-tutorial/iptables-tutorial.html",
                  "docs", "Referência clássica."),
                m("DigitalOcean: UFW Essentials",
                  "https://www.digitalocean.com/community/tutorials/ufw-essentials-common-firewall-rules-and-commands",
                  "article", ""),
                m("Linux netfilter packet-filtering HOWTO",
                  "https://netfilter.org/documentation/HOWTO/packet-filtering-HOWTO.html",
                  "docs", ""),
                m("Cloudflare: WAF basics",
                  "https://www.cloudflare.com/learning/ddos/glossary/web-application-firewall-waf/",
                  "article", ""),
            ],
            "questions": [
                q("Qual comando UFW permite SSH?",
                  "ufw allow ssh",
                  ["ufw open 22 always", "ufw bind 22", "ufw forward ssh"],
                  "UFW reconhece nomes de serviço (ssh, http, https) ou número de porta."),
                q("Política recomendada de entrada (INPUT)?",
                  "default deny, só permite o explicitamente autorizado.",
                  ["default allow",
                   "ignorar tudo",
                   "drop saída e permitir entrada"],
                  "Default-deny inverte o padrão: nada entra a menos que você diga sim."),
                q("Qual chain do iptables filtra pacotes destinados ao próprio host?",
                  "INPUT", ["OUTPUT", "FORWARD", "POSTROUTING"],
                  "OUTPUT = pacotes saídos pelo host. FORWARD = pacotes roteados pela máquina (gateway)."),
                q("Diferença chave entre DROP e REJECT?",
                  "DROP descarta silenciosamente; REJECT envia ICMP/RST informando bloqueio.",
                  ["DROP é mais lento.",
                   "REJECT requer NAT.",
                   "DROP só funciona em UDP."],
                  "DROP é o padrão em internet pública (não dá pista para o atacante); "
                  "REJECT pode acelerar debug em rede interna."),
                q("Por que limitar conexões a SSH (rate limiting)?",
                  "Mitiga brute force.",
                  ["Acelera o handshake.",
                   "Diminui CPU do kernel.",
                   "É exigência POSIX."],
                  "ufw limit bloqueia IPs com mais de 6 tentativas em 30s, combina bem com fail2ban."),
                q("Qual o sucessor moderno do iptables?",
                  "nftables",
                  ["ipset", "ipchains", "netcat"],
                  "nftables unifica vários antigos; iptables atual é shim sobre nft em distros novas."),
                q("`ufw status numbered` mostra:",
                  "Lista numerada de regras para edição/exclusão.",
                  ["O uso de banda.",
                   "Ataques recentes.",
                   "Tráfego em tempo real."],
                  "Permite remover por índice: `ufw delete 3`."),
                q("Qual porta 53 é tipicamente liberada para?",
                  "DNS", ["HTTP", "RDP", "SMB"],
                  "DNS usa 53 em UDP (queries normais) e TCP (zone transfer e mensagens grandes)."),
                q("`ufw deny from 10.0.0.5` faz o quê?",
                  "Bloqueia conexões originadas desse IP.",
                  ["Permite apenas esse IP.",
                   "Apaga rota para esse IP.",
                   "Renomeia interface."],
                  "Útil para banir IPs maliciosos rapidamente."),
                q("Por que abrir 'all' (qualquer porta) em produção é ruim?",
                  "Aumenta drasticamente a superfície de ataque.",
                  ["Quebra DNS.",
                   "Reduz performance.",
                   "Não é permitido pelo kernel."],
                  "Cada porta exposta é uma chance a mais para encontrar uma vulnerabilidade."),
            ],
        },
        # =====================================================================
        # 1.7 Web Servers
        # =====================================================================
        {
            "title": "Web Servers (Nginx/Apache)",
            "summary": "Como hospedar e proteger uma aplicação web simples.",
            "lesson": {
                "intro": (
                    "Mesmo na era de Kubernetes e service mesh, na borda de quase toda "
                    "aplicação web ainda existe um Nginx, Caddy, Apache ou Traefik. Eles "
                    "fazem TLS termination, compressão, cache, rate limit, autenticação básica, "
                    "redirecionamento e proxy reverso para apps em uvicorn/gunicorn/php-fpm.<br><br>"
                    "Configurar bem evita uma classe inteira de bugs de segurança e performance "
                    "que muitos times só descobrem no incidente. Esta aula é Nginx-centric (o "
                    "mais usado na indústria) com pontes para Apache e Caddy."
                ),
                "body": (
                    "<h3>1. Por que ainda existe TLS termination na borda</h3>"
                    "<p>Mesmo com mTLS dentro do mesh, há motivos para ter um proxy de borda:</p>"
                    "<ul>"
                    "<li>Certificado público (Let's Encrypt) gerenciado em um único lugar.</li>"
                    "<li>HTTP/2 e HTTP/3 (QUIC) por default sem que cada microservice precise "
                    "implementar.</li>"
                    "<li>Compressão (gzip, brotli) e cache de respostas.</li>"
                    "<li>WAF (ModSecurity).</li>"
                    "<li>Roteamento por path/host com lógica complexa.</li>"
                    "</ul>"
                    "<p>Padrão clássico: Nginx em 80/443 → "
                    "<code>proxy_pass http://127.0.0.1:8000</code> (gunicorn/uvicorn/daphne) "
                    "ou socket Unix.</p>"

                    "<h3>2. Configuração mínima viável</h3>"
                    "<pre><code># /etc/nginx/sites-available/api.example.com\n"
                    "upstream api_backend {\n"
                    "  server 127.0.0.1:8000 fail_timeout=5s;\n"
                    "  keepalive 32;\n"
                    "}\n"
                    "\n"
                    "server {\n"
                    "  listen 80;\n"
                    "  listen [::]:80;\n"
                    "  server_name api.example.com;\n"
                    "  return 301 https://$host$request_uri;        # força HTTPS\n"
                    "}\n"
                    "\n"
                    "server {\n"
                    "  listen 443 ssl http2;\n"
                    "  listen [::]:443 ssl http2;\n"
                    "  server_name api.example.com;\n"
                    "  \n"
                    "  ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;\n"
                    "  ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;\n"
                    "  \n"
                    "  # Mozilla 'modern' (apenas TLS 1.3) ou 'intermediate' (1.2+1.3)\n"
                    "  ssl_protocols TLSv1.3;\n"
                    "  ssl_prefer_server_ciphers off;\n"
                    "  ssl_ciphers TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384;\n"
                    "  ssl_session_timeout 1d;\n"
                    "  ssl_session_cache shared:SSL:10m;\n"
                    "  ssl_session_tickets off;\n"
                    "  ssl_stapling on;\n"
                    "  ssl_stapling_verify on;\n"
                    "  \n"
                    "  # Headers de segurança\n"
                    "  add_header Strict-Transport-Security \"max-age=63072000; includeSubDomains; preload\" always;\n"
                    "  add_header X-Frame-Options DENY always;\n"
                    "  add_header X-Content-Type-Options nosniff always;\n"
                    "  add_header Referrer-Policy strict-origin-when-cross-origin always;\n"
                    "  add_header Permissions-Policy \"camera=(), microphone=(), geolocation=()\" always;\n"
                    "  add_header Content-Security-Policy \"default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'\" always;\n"
                    "  \n"
                    "  # Esconde versão do Nginx\n"
                    "  server_tokens off;\n"
                    "  \n"
                    "  # Tamanho máximo de body\n"
                    "  client_max_body_size 5M;\n"
                    "  \n"
                    "  # Compressão\n"
                    "  gzip on;\n"
                    "  gzip_types text/plain text/css application/json application/javascript;\n"
                    "  \n"
                    "  # Rate limit em /login\n"
                    "  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;\n"
                    "  \n"
                    "  location = /login {\n"
                    "    limit_req zone=login burst=10 nodelay;\n"
                    "    proxy_pass http://api_backend;\n"
                    "  }\n"
                    "  \n"
                    "  location / {\n"
                    "    proxy_http_version 1.1;\n"
                    "    proxy_set_header Connection \"\";\n"
                    "    proxy_set_header Host $host;\n"
                    "    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
                    "    proxy_set_header X-Forwarded-Proto $scheme;\n"
                    "    proxy_set_header X-Real-IP $remote_addr;\n"
                    "    proxy_pass http://api_backend;\n"
                    "    proxy_read_timeout 60s;\n"
                    "  }\n"
                    "}</code></pre>"

                    "<h3>3. Headers de segurança detalhados</h3>"
                    "<table>"
                    "<tr><td><code>Strict-Transport-Security</code></td>"
                    "<td>Browser vai usar HTTPS por X segundos sem nem tentar HTTP.</td></tr>"
                    "<tr><td><code>X-Frame-Options DENY</code></td>"
                    "<td>Mata clickjacking via &lt;iframe&gt;.</td></tr>"
                    "<tr><td><code>X-Content-Type-Options nosniff</code></td>"
                    "<td>Browser não 'adivinha' MIME, para upload de avatar virar HTML.</td></tr>"
                    "<tr><td><code>Content-Security-Policy</code></td>"
                    "<td>A defesa contra XSS mais poderosa. "
                    "Define quais origens podem rodar JS, carregar imagem, etc.</td></tr>"
                    "<tr><td><code>Referrer-Policy</code></td>"
                    "<td>Controla quanto da URL atual é enviado em <em>navegação</em>.</td></tr>"
                    "<tr><td><code>Permissions-Policy</code></td>"
                    "<td>Câmera, microfone, geolocalização, só com opt-in explícito.</td></tr>"
                    "</table>"
                    "<p>Audite com <a href='https://securityheaders.com'>securityheaders.com</a> "
                    "e <a href='https://www.ssllabs.com/ssltest/'>SSL Labs</a>.</p>"

                    "<h3>4. CSP, o headache que vale o esforço</h3>"
                    "<p>Comece em modo report-only para não quebrar produção:</p>"
                    "<pre><code>add_header Content-Security-Policy-Report-Only \"\n"
                    "  default-src 'self';\n"
                    "  script-src 'self' 'sha256-XXX...';\n"
                    "  style-src 'self' https://fonts.googleapis.com;\n"
                    "  img-src 'self' data: https:;\n"
                    "  connect-src 'self' https://api.example.com;\n"
                    "  frame-ancestors 'none';\n"
                    "  report-uri /csp-report;\n"
                    "\" always;</code></pre>"
                    "<p>Colete violações por algumas semanas, ajuste, e troque "
                    "<code>Content-Security-Policy-Report-Only</code> por "
                    "<code>Content-Security-Policy</code>.</p>"

                    "<h3>5. Rate limiting, o ABC contra credential stuffing</h3>"
                    "<p>Rotas como <code>/login</code>, <code>/register</code>, "
                    "<code>/forgot-password</code> são alvos óbvios. No Nginx:</p>"
                    "<pre><code>http {\n"
                    "  limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;\n"
                    "  limit_req_zone $binary_remote_addr zone=api:10m rate=600r/m;\n"
                    "}\n"
                    "\n"
                    "server {\n"
                    "  location ~ ^/(login|register|forgot)$ {\n"
                    "    limit_req zone=auth burst=5 nodelay;\n"
                    "    proxy_pass http://app;\n"
                    "  }\n"
                    "  location /api/ {\n"
                    "    limit_req zone=api burst=100;\n"
                    "    proxy_pass http://app;\n"
                    "  }\n"
                    "}</code></pre>"
                    "<p>Combine com rate-limit por usuário/api-key na app, IP-based sozinho "
                    "é facilmente bypassado com proxy/botnet.</p>"

                    "<h3>6. Proxy reverso e o problema do IP real</h3>"
                    "<p>Quando o Nginx faz <code>proxy_pass</code>, a app vê IP "
                    "<code>127.0.0.1</code>. Para preservar o IP real:</p>"
                    "<pre><code>proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
                    "proxy_set_header X-Forwarded-Proto $scheme;\n"
                    "proxy_set_header X-Real-IP $remote_addr;</code></pre>"
                    "<p>Na app (Django):</p>"
                    "<pre><code>USE_X_FORWARDED_HOST = True\n"
                    "SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')</code></pre>"
                    "<p><strong>NUNCA</strong> confie em <code>X-Forwarded-For</code> vindo "
                    "diretamente do cliente. Configure o número de hops confiáveis (Nginx: "
                    "<code>set_real_ip_from</code> + <code>real_ip_recursive on</code>; ALB: "
                    "trust hops).</p>"

                    "<h3>7. Caching para performance e proteção</h3>"
                    "<pre><code># Cache de respostas estáticas\n"
                    "location ~* \\.(jpg|css|js|woff2)$ {\n"
                    "  expires 30d;\n"
                    "  add_header Cache-Control \"public, immutable\";\n"
                    "}\n"
                    "\n"
                    "# Cache de respostas dinâmicas (chamadas idempotentes)\n"
                    "proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app:10m max_size=1g;\n"
                    "\n"
                    "location /api/products {\n"
                    "  proxy_cache app;\n"
                    "  proxy_cache_valid 200 5m;\n"
                    "  proxy_cache_use_stale error timeout updating;\n"
                    "  add_header X-Cache-Status $upstream_cache_status;\n"
                    "  proxy_pass http://app;\n"
                    "}</code></pre>"
                    "<p>Cache também é proteção contra DoS, request repetida não chega na "
                    "app.</p>"

                    "<h3>8. ModSecurity, WAF embedded</h3>"
                    "<p>ModSecurity v3 + OWASP Core Rule Set bloqueia padrões clássicos "
                    "(SQLi, XSS, path traversal). Cuidado: false positives podem quebrar app "
                    "legítima. Comece em <code>DetectionOnly</code>:</p>"
                    "<pre><code># /etc/nginx/modsec/main.conf\n"
                    "Include /etc/nginx/modsec/coreruleset/crs-setup.conf\n"
                    "Include /etc/nginx/modsec/coreruleset/rules/*.conf\n"
                    "SecRuleEngine DetectionOnly\n"
                    "SecAuditLog /var/log/nginx/modsec_audit.log\n"
                    "SecAuditLogFormat JSON</code></pre>"
                    "<p>Após semanas de log, vire <code>SecRuleEngine On</code> e tunne falsos "
                    "positivos com <code>SecRuleRemoveById</code>.</p>"

                    "<h3>9. Caddy, alternativa moderna</h3>"
                    "<p>Caddy faz TLS automático (Let's Encrypt embutido), HTTP/3 default, "
                    "config simples:</p>"
                    "<pre><code># Caddyfile\n"
                    "api.example.com {\n"
                    "  reverse_proxy 127.0.0.1:8000\n"
                    "  encode zstd gzip\n"
                    "  header {\n"
                    "    Strict-Transport-Security \"max-age=63072000; includeSubDomains; preload\"\n"
                    "    X-Content-Type-Options nosniff\n"
                    "  }\n"
                    "  rate_limit {\n"
                    "    zone login {\n"
                    "      key {http.request.remote.host}\n"
                    "      events 5\n"
                    "      window 60s\n"
                    "    }\n"
                    "  }\n"
                    "}</code></pre>"

                    "<h3>10. Anti-patterns + caso real</h3>"
                    "<ul>"
                    "<li><code>autoindex on</code> em produção: lista diretórios, vazamento "
                    "trivial.</li>"
                    "<li>Servir <code>.git</code> ou <code>.env</code>: <em>caso real</em>, "
                    "muitos sites WordPress já vazaram credenciais por isso. Bloqueie em "
                    "regex.</li>"
                    "<li>TLS 1.0/1.1: vulnerável (BEAST, POODLE). Desabilite.</li>"
                    "<li>Sem <code>server_tokens off</code>: revela versão exata do Nginx, "
                    "facilita CVE matching.</li>"
                    "<li>Sem <code>client_max_body_size</code>: aberto para DoS por upload "
                    "gigante.</li>"
                    "<li>Default config sem testar TLS no SSL Labs: muitos times só descobrem "
                    "depois que o cliente reclamou.</li>"
                    "</ul>"
                ),
                "practical": (
                    "(1) Suba uma app simples (FastAPI/Django) na porta 8000.<br>"
                    "(2) Configure Nginx como proxy reverso para ela com TLS via "
                    "<code>certbot --nginx</code>.<br>"
                    "(3) Adicione todos os headers de segurança da aula. Adicione um "
                    "<code>limit_req</code> em <code>/login</code>.<br>"
                    "(4) Teste em "
                    "<a href='https://www.ssllabs.com/ssltest/'>SSL Labs</a> e "
                    "<a href='https://securityheaders.com'>securityheaders.com</a>. Mire em "
                    "A+ em ambos.<br>"
                    "(5) Bônus: bloqueie acesso a <code>.env</code>, <code>.git</code> e "
                    "<code>.htaccess</code> via:<br>"
                    "<code>location ~ /\\.(env|git|htaccess) { deny all; }</code>.<br>"
                    "(6) Bônus avançado: instale o ModSecurity em "
                    "<code>SecRuleEngine DetectionOnly</code> e gere alguns ataques de SQLi "
                    "via <code>curl</code>; veja o log em "
                    "<code>/var/log/nginx/modsec_audit.log</code>."
                ),
            },
            "materials": [
                m("Nginx Beginner's Guide",
                  "https://nginx.org/en/docs/beginners_guide.html", "docs", ""),
                m("Mozilla SSL Configuration Generator",
                  "https://ssl-config.mozilla.org/", "tool", ""),
                m("OWASP Secure Headers",
                  "https://owasp.org/www-project-secure-headers/", "docs", ""),
                m("Let's Encrypt + certbot", "https://certbot.eff.org/", "tool", ""),
                m("Apache HTTP Server Documentation",
                  "https://httpd.apache.org/docs/current/", "docs", ""),
                m("SSL Labs server test",
                  "https://www.ssllabs.com/ssltest/",
                  "tool", "Auditoria pública de TLS de qualquer endpoint."),
            ],
            "questions": [
                q("Qual diretiva no Nginx oculta o número da versão?",
                  "server_tokens off;",
                  ["hide_version yes;", "no_version on;", "server_hidden 1;"],
                  "Reduz o fingerprint para scanners automatizados."),
                q("Qual header força HTTPS em browsers compatíveis?",
                  "Strict-Transport-Security (HSTS)",
                  ["Force-HTTPS", "Upgrade-Required", "Cache-Secure"],
                  "Inclua max-age longo e includeSubDomains; considere preload list após estável."),
                q("Em Nginx, como configurar um proxy reverso?",
                  "Usando proxy_pass http://backend; em um bloco location.",
                  ["Apenas root html",
                   "fastcgi_pass *",
                   "rewrite ^.*$"],
                  "Lembre-se de proxy_set_header Host $host e X-Forwarded-* para a app saber o cliente real."),
                q("Qual a porta padrão do TLS/HTTPS?",
                  "443", ["8443 sempre", "80", "23"],
                  "443 é well-known. 80 é HTTP puro, 23 é Telnet (legado e inseguro)."),
                q("Por que ativar gzip/brotli?",
                  "Reduz tamanho da resposta, acelera entrega.",
                  ["Aumenta segurança.",
                   "Substitui o cache.",
                   "Necessário para HTTP/2."],
                  "Cuidado com BREACH/CRIME se concatenar conteúdo do usuário com segredo na mesma resposta."),
                q("Qual diretiva limita tamanho do body em Nginx?",
                  "client_max_body_size",
                  ["max_body_kb", "request_size_limit", "post_size"],
                  "Mitiga abuso por uploads gigantes; ajuste por endpoint quando for upload legítimo."),
                q("O que faz o Mozilla SSL Configuration Generator?",
                  "Gera configurações TLS recomendadas (modern/intermediate/old).",
                  ["Renova certificados.",
                   "Cria chaves SSH.",
                   "Mede latência."],
                  "Atualizado pela Mozilla com base em pesquisa de browsers e CVEs."),
                q("Como redirecionar HTTP para HTTPS em Nginx?",
                  "return 301 https://$host$request_uri;",
                  ["proxy_pass https",
                   "if ($http) drop;",
                   "rewrite ^/ /https/"],
                  "301 (permanente) ajuda cache e SEO. Use return em vez de rewrite, mais rápido."),
                q("Por que rate limiting em /login?",
                  "Mitiga ataques de força bruta e credential stuffing.",
                  ["Reduz consumo de RAM.",
                   "Acelera o login.",
                   "Ativa MFA."],
                  "Limit_req_zone + limit_req em Nginx, ou middleware na própria app."),
                q("Qual ferramenta automatiza certificados TLS gratuitos?",
                  "certbot (Let's Encrypt).",
                  ["docker compose", "cron-tls", "iptables"],
                  "ACME é o protocolo; certbot, acme.sh, lego e o próprio Caddy implementam."),
            ],
        },
        # =====================================================================
        # 1.8 Pacotes
        # =====================================================================
        {
            "title": "Gestão de Pacotes e Repositórios",
            "summary": "Instalação segura de softwares e verificação de assinaturas.",
            "lesson": {
                "intro": (
                    "Em quase todo incidente sério de <em>supply chain</em> da última década, "
                    "SolarWinds (2020), Codecov (2021), npm 'colors' (2022), xz-utils (2024), "
                    "uma das raízes é instalação de pacote sem verificação de origem. APT, DNF "
                    "e seus pares têm cripto embutida que resolveria isso; gerentes de pacote "
                    "de linguagem (npm, pypi, cargo) também estão melhorando.<br><br>"
                    "Esta aula cobre como repositórios garantem integridade, como adicionar "
                    "fontes externas com segurança, pinning de versões, mirror interno e "
                    "como gerar SBOM para sobreviver à próxima Log4Shell."
                ),
                "body": (
                    "<h3>1. Modelo de confiança em APT</h3>"
                    "<p>O processo:</p>"
                    "<ol>"
                    "<li>O repositório publica um <code>Release</code> file com hash de cada "
                    "<code>Packages</code>.</li>"
                    "<li>O <code>Release</code> é assinado com GPG. A assinatura vai em "
                    "<code>Release.gpg</code> (ou <code>InRelease</code> com tudo num só "
                    "arquivo).</li>"
                    "<li>O cliente baixa <code>Release</code>, valida com a chave pública do "
                    "mantenedor (em <code>/etc/apt/keyrings/</code> ou "
                    "<code>/etc/apt/trusted.gpg.d/</code>) e só então confia nos hashes "
                    "listados.</li>"
                    "<li>Cada pacote (<code>.deb</code>) tem hash que precisa bater.</li>"
                    "</ol>"
                    "<p>Assim, mesmo que um espelho seja comprometido, o atacante não "
                    "consegue trocar pacotes sem invalidar a assinatura.</p>"

                    "<h3>2. Adicionando repositórios externos com segurança</h3>"
                    "<p>A forma <strong>antiga</strong> (<code>apt-key add -</code>) está "
                    "depreciada porque adicionava confiança global no sistema todo. A forma "
                    "moderna usa <code>signed-by</code> para limitar o escopo da chave a "
                    "<em>aquele</em> repositório:</p>"
                    "<pre><code># 1. Baixe a chave em formato dearmored\n"
                    "curl -fsSL https://download.docker.com/linux/ubuntu/gpg \\\n"
                    "  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg\n"
                    "sudo chmod 644 /etc/apt/keyrings/docker.gpg\n"
                    "\n"
                    "# 2. Adicione o repositório referenciando essa chave\n"
                    "echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] \\\n"
                    "  https://download.docker.com/linux/ubuntu jammy stable' \\\n"
                    "  | sudo tee /etc/apt/sources.list.d/docker.list\n"
                    "\n"
                    "# 3. Verifique a chave antes de aceitar\n"
                    "gpg --no-default-keyring --keyring /etc/apt/keyrings/docker.gpg --list-keys\n"
                    "# Compare o fingerprint com o que está na docs oficial.\n"
                    "\n"
                    "sudo apt update\n"
                    "sudo apt install docker-ce</code></pre>"
                    "<p>Em RHEL/Fedora:</p>"
                    "<pre><code>sudo rpm --import https://download.docker.com/linux/centos/gpg\n"
                    "sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo\n"
                    "# /etc/yum.repos.d/docker-ce.repo precisa ter gpgcheck=1</code></pre>"

                    "<h3>3. Pinning de versões em produção</h3>"
                    "<p>Em produção, <strong>nunca</strong> rode <code>apt upgrade</code> em "
                    "pipeline sem testar primeiro. Você pode acordar com nginx atualizado e "
                    "config quebrada. Soluções:</p>"
                    "<pre><code># /etc/apt/preferences.d/nginx\n"
                    "Package: nginx*\n"
                    "Pin: version 1.24.*\n"
                    "Pin-Priority: 1001\n"
                    "\n"
                    "# Ou marque como hold\n"
                    "sudo apt-mark hold nginx\n"
                    "\n"
                    "# Ou, em containers, pin direto no Dockerfile\n"
                    "RUN apt-get update &amp;&amp; apt-get install -y --no-install-recommends \\\n"
                    "    nginx=1.24.* \\\n"
                    "  &amp;&amp; rm -rf /var/lib/apt/lists/*</code></pre>"
                    "<p>Em RHEL: <code>dnf versionlock add nginx</code>.</p>"

                    "<h3>4. Mirror/registry interno: por que vale a pena</h3>"
                    "<p>Em ambientes corporativos sérios:</p>"
                    "<ul>"
                    "<li><strong>Independência</strong>: build não falha quando upstream cai.</li>"
                    "<li><strong>Auditoria</strong>: quem baixou o quê, quando.</li>"
                    "<li><strong>Scanning</strong>: pacote é varrido antes de chegar ao "
                    "build.</li>"
                    "<li><strong>Velocidade</strong>: dentro da VPC é mais rápido que pegar "
                    "no mantenedor.</li>"
                    "<li><strong>Compliance</strong>: SOC 2, ISO 27001 olham para isso.</li>"
                    "</ul>"
                    "<p>Ferramentas: <strong>JFrog Artifactory</strong> "
                    "(comercial, suporta tudo), <strong>Sonatype Nexus</strong> "
                    "(comercial/free), <strong>Pulpcore</strong> (open source, RHEL).</p>"

                    "<h3>5. Pacotes de linguagem: o oeste selvagem</h3>"
                    "<p>npm, pypi, rubygems, crates.io têm modelo diferente: qualquer um "
                    "publica. Atacantes exploram via:</p>"
                    "<ul>"
                    "<li><strong>Typosquatting</strong>: pacote com nome parecido. Já houve "
                    "<code>colourama</code>, <code>requestes</code>, <code>pythn</code>.</li>"
                    "<li><strong>Dependency confusion</strong>: pacote <em>privado</em> com "
                    "nome que existe no público; o gerente prefere o público (mais novo).</li>"
                    "<li><strong>Account takeover</strong>: mantenedor original perde "
                    "credencial; atacante publica versão maliciosa do pacote legítimo. "
                    "<em>Caso 'colors.js'</em> em 2022.</li>"
                    "<li><strong>Long con</strong>: contribuidor 'útil' por anos eventualmente "
                    "adiciona backdoor. <em>xz-utils 2024</em>.</li>"
                    "</ul>"
                    "<p>Mitigações:</p>"
                    "<ul>"
                    "<li><strong>Lockfiles obrigatórios</strong>: "
                    "<code>poetry.lock</code>, <code>package-lock.json</code>, "
                    "<code>Cargo.lock</code> com hash. Build determinístico.</li>"
                    "<li><strong>Mirror interno</strong> (Artifactory) com whitelist de "
                    "pacotes aprovados.</li>"
                    "<li><strong>Scanners</strong>: <code>pip-audit</code>, "
                    "<code>npm audit</code>, <code>cargo audit</code>, "
                    "<code>OSV-Scanner</code>, <code>Trivy</code>.</li>"
                    "<li><strong>Dependency review</strong> nos PRs: GitHub e GitLab têm "
                    "checks nativos.</li>"
                    "</ul>"

                    "<h3>6. SBOM, Software Bill of Materials</h3>"
                    "<p>Um SBOM é a lista 'de ingredientes' do seu software. Em incidente "
                    "(ex.: nova CVE em libxml), você consulta o SBOM e em segundos sabe "
                    "exatamente quais imagens/serviços estão afetados, em vez de varrer 200 "
                    "Dockerfiles.</p>"
                    "<p>Formatos padronizados:</p>"
                    "<ul>"
                    "<li><strong>CycloneDX</strong> (OWASP).</li>"
                    "<li><strong>SPDX</strong> (Linux Foundation).</li>"
                    "</ul>"
                    "<p>Geração:</p>"
                    "<pre><code># Imagem Docker\n"
                    "syft myapp:1.0 -o cyclonedx-json &gt; sbom.json\n"
                    "\n"
                    "# Sistema de arquivos\n"
                    "syft dir:/opt/app -o spdx-json &gt; sbom-spdx.json\n"
                    "\n"
                    "# Python apenas\n"
                    "cyclonedx-py -i requirements.txt -o sbom.xml\n"
                    "\n"
                    "# Cruzando com CVEs\n"
                    "grype sbom:./sbom.json</code></pre>"
                    "<p>Em alguns setores (US Federal, automotive, médicos), SBOM virou "
                    "obrigação legal, Executive Order 14028 nos EUA.</p>"

                    "<h3>7. Reproducibilidade de builds</h3>"
                    "<p>Build reprodutível: dado o mesmo source + mesmo ambiente, mesmo "
                    "binário (byte a byte). Permite verificar que um binário foi gerado a "
                    "partir do código alegado. Conceito-chave do projeto "
                    "<a href='https://reproducible-builds.org/'>Reproducible Builds</a>. "
                    "Práticas:</p>"
                    "<ul>"
                    "<li>Pin de versão em todos os steps.</li>"
                    "<li>Datas determinísticas "
                    "(<code>SOURCE_DATE_EPOCH</code>).</li>"
                    "<li>Sem aleatoriedade em ordem (sort em listas de arquivos).</li>"
                    "<li>Toolchain pinada (compilador específico).</li>"
                    "</ul>"

                    "<h3>8. Caso real: xz-utils 2024</h3>"
                    "<p>Em março/2024, descobriu-se que <code>xz-utils</code> 5.6.0/5.6.1, "
                    "biblioteca usada em quase toda distro Linux, tinha backdoor injetada "
                    "via <code>libsystemd</code> que permitia RCE em sshd remotamente. O "
                    "atacante (Jia Tan) foi mantenedor confiável por anos antes de inserir o "
                    "código. Salvou-se: um engenheiro da Microsoft notou latência incomum no "
                    "ssh e investigou. Lições:</p>"
                    "<ul>"
                    "<li>SBOM teria identificado servidores afetados em minutos.</li>"
                    "<li>Releases que demoram demais a aparecer em distros estáveis "
                    "(quarentena natural) salvaram a maioria dos casos.</li>"
                    "<li>Reproducible builds não pegariam, o tarball tinha código diferente "
                    "do repo.</li>"
                    "<li>Open source não é mágica: precisa de revisão real.</li>"
                    "</ul>"

                    "<h3>9. Anti-patterns</h3>"
                    "<ul>"
                    "<li><code>curl ... | bash</code>: RCE se servidor de origem comprometido.</li>"
                    "<li><code>--allow-unauthenticated</code> ou "
                    "<code>nodaemon=true</code> para 'ignorar erro de assinatura'.</li>"
                    "<li>Adicionar PPA/repos externos sem verificar fingerprint.</li>"
                    "<li>Não pinar nada, sempre usar 'latest'.</li>"
                    "<li>Misturar repositórios estáveis e instáveis, Frankenstein de versões.</li>"
                    "<li>Pular release notes e atualizar produção sem ler.</li>"
                    "</ul>"

                    "<h3>10. Workflow recomendado</h3>"
                    "<ol>"
                    "<li>CI: <code>pip-audit</code>/<code>npm audit</code> em todo PR. Falha "
                    "para CVEs Critical/High.</li>"
                    "<li>Build: gera SBOM e armazena com a artifact.</li>"
                    "<li>Push: scan no registry (Trivy/Grype) com policy.</li>"
                    "<li>Deploy: admission controller (Kyverno) só aceita imagem com SBOM "
                    "anexado.</li>"
                    "<li>Operação: re-scan periódico (Harbor, Trivy operator), CVEs novas "
                    "aparecem depois.</li>"
                    "<li>Renovate/Dependabot abre PRs de update automaticamente.</li>"
                    "</ol>"
                ),
                "practical": (
                    "(1) Adicione o repositório oficial Docker em uma VM Ubuntu via "
                    "<code>signed-by=/etc/apt/keyrings/...</code>. Verifique fingerprint "
                    "antes.<br>"
                    "(2) Pin a versão do <code>docker-ce</code> em "
                    "<code>/etc/apt/preferences.d/docker</code> e marque com "
                    "<code>apt-mark hold</code>.<br>"
                    "(3) Instale <code>syft</code> e gere um SBOM CycloneDX da imagem "
                    "<code>nginx:1.24-alpine</code>: "
                    "<code>syft nginx:1.24-alpine -o cyclonedx-json &gt; nginx.sbom.json</code>.<br>"
                    "(4) Instale <code>grype</code> e cruze o SBOM contra CVEs: "
                    "<code>grype sbom:./nginx.sbom.json</code>.<br>"
                    "(5) Bônus: tente <code>apt install</code> de pacote que não tem "
                    "assinatura, observe o erro do APT e pesquise o que "
                    "<code>--allow-unauthenticated</code> faz (e por que você não deveria "
                    "usar)."
                ),
            },
            "materials": [
                m("Debian apt-secure", "https://wiki.debian.org/SecureApt", "docs", ""),
                m("DNF docs", "https://dnf.readthedocs.io/", "docs", ""),
                m("APT user manual",
                  "https://www.debian.org/doc/manuals/apt-guide/index.en.html", "docs", ""),
                m("Reproducible builds", "https://reproducible-builds.org/",
                  "article", "Por que builds determinísticos importam."),
                m("OpenSSF Best Practices", "https://www.bestpractices.dev/", "docs", ""),
                m("syft (SBOM)", "https://github.com/anchore/syft", "tool", ""),
            ],
            "questions": [
                q("O que é um arquivo `.gpg` em /etc/apt/trusted.gpg.d/?",
                  "Chave pública usada para validar assinaturas de pacotes do repositório.",
                  ["Chave privada do mantenedor.",
                   "Token OAuth.",
                   "Hash do binário."],
                  "É a parte pública; APT a usa para verificar a assinatura do Release file."),
                q("`apt update` faz o quê?",
                  "Baixa metadados (índices) dos repositórios.",
                  ["Reinstala todos os pacotes.",
                   "Apaga cache.",
                   "Aplica patches do kernel."],
                  "Atualiza o conhecimento sobre versões disponíveis. `apt upgrade` é que aplica."),
                q("Como bloquear uma versão específica em apt?",
                  "Pinning via /etc/apt/preferences.",
                  ["apt-get freeze",
                   "dpkg --hold-version",
                   "apt-mark exclude"],
                  "`apt-mark hold` também funciona; pinning oferece mais granularidade (priority por origem)."),
                q("Por que evitar `curl ... | sh`?",
                  "Executa código remoto sem verificação de assinatura.",
                  ["É mais lento.",
                   "Não funciona com bash.",
                   "Quebra TLS."],
                  "MITM ou comprometimento do servidor de origem viram RCE imediato. Prefira pacote assinado."),
                q("`dpkg -l` lista:",
                  "Pacotes instalados em sistemas Debian.",
                  ["Logs do kernel.",
                   "Repositórios configurados.",
                   "Apenas dependências quebradas."],
                  "É o equivalente a `rpm -qa` no mundo RHEL."),
                q("Em supply chain, 'typosquatting' é:",
                  "Publicar pacotes com nomes parecidos para enganar usuários (ex.: 'numpyy').",
                  ["Erro de digitação no kernel.",
                   "Bug de DNS.",
                   "Patch automático."],
                  "Caso famoso: pacotes maliciosos com nomes próximos a 'request', 'pyyaml', 'colorama' etc."),
                q("Qual ferramenta gera SBOM em projetos Python?",
                  "syft (ou pip-audit/cyclonedx-py).",
                  ["pylint", "isort", "tox"],
                  "syft funciona em qualquer linguagem; cyclonedx-py é específico de Python."),
                q("Por que assinar pacotes internos?",
                  "Garante autenticidade e integridade frente a tampering.",
                  ["Reduz tamanho.",
                   "Aumenta velocidade de download.",
                   "Substitui antivirus."],
                  "Mesmo em rede 'segura', uma máquina comprometida poderia injetar binário se não houver assinatura."),
                q("Em RHEL, qual comando equivalente a `apt update`?",
                  "dnf check-update", ["dnf install all", "yum reset", "rpm -i all"],
                  "Em RHEL 8+ é dnf; antes era yum (mantido como alias)."),
                q("Por que fixar versões em produção?",
                  "Reprodutibilidade e evitar atualizações automáticas que quebrem o sistema.",
                  ["Reduz consumo de CPU.",
                   "Permite hot reload.",
                   "Habilita modo verbose."],
                  "Update automático em pipeline sem testes = receita para outage."),
            ],
        },
        # =====================================================================
        # 1.9 Logs
        # =====================================================================
        {
            "title": "Log Management",
            "summary": "Onde os erros e ataques ficam registrados no sistema.",
            "lesson": {
                "intro": (
                    "Sem logs, debug vira adivinhação e investigação de incidente vira "
                    "ficção, você inventa o que aconteceu. Logs estruturados, centralizados "
                    "e correlacionáveis são o que separa um time profissional de um time "
                    "amador.<br><br>"
                    "Esta aula cobre: (a) onde ficam os logs do SO, (b) como sua app deve "
                    "logar, (c) o que <em>nunca</em> deveria ir para log (LGPD/PCI), "
                    "(d) como centralizar e (e) por que logs são apenas uma das três "
                    "pernas da observabilidade."
                ),
                "body": (
                    "<h3>1. Logs do SO via systemd-journald</h3>"
                    "<p>Distros modernas centralizam tudo no <code>journald</code>:</p>"
                    "<pre><code>journalctl -u nginx                    # serviço específico\n"
                    "journalctl -u nginx -f                 # follow (tail -f)\n"
                    "journalctl -u nginx -p err -S today    # erros de hoje\n"
                    "journalctl -k -p crit                  # kernel, criticais\n"
                    "journalctl _UID=1000                   # de um usuário\n"
                    "journalctl --since '1 hour ago' --until '5 min ago'\n"
                    "journalctl -o json-pretty -u nginx | jq .   # JSON estruturado\n"
                    "journalctl --disk-usage                # quanto está ocupando</code></pre>"
                    "<p>Persistência: por padrão journald guarda só em RAM (<code>/run/log</code>). "
                    "Para sobreviver a reboot:</p>"
                    "<pre><code># /etc/systemd/journald.conf\n"
                    "[Journal]\n"
                    "Storage=persistent\n"
                    "SystemMaxUse=2G\n"
                    "MaxRetentionSec=30day</code></pre>"

                    "<h3>2. Logs estruturados na sua app</h3>"
                    "<p>Texto livre vira regex doloroso na hora de buscar. JSON é o caminho. "
                    "Em Python:</p>"
                    "<pre><code>import structlog\n"
                    "import logging\n"
                    "\n"
                    "structlog.configure(\n"
                    "    processors=[\n"
                    "        structlog.contextvars.merge_contextvars,\n"
                    "        structlog.processors.add_log_level,\n"
                    "        structlog.processors.TimeStamper(fmt='iso'),\n"
                    "        structlog.processors.JSONRenderer(),\n"
                    "    ],\n"
                    "    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),\n"
                    ")\n"
                    "\n"
                    "log = structlog.get_logger()\n"
                    "\n"
                    "structlog.contextvars.bind_contextvars(\n"
                    "    request_id='req-123',\n"
                    "    user_id=42,\n"
                    ")\n"
                    "\n"
                    "log.info('user.login', method='password', mfa=True)\n"
                    "# {\"event\":\"user.login\",\"method\":\"password\",\"mfa\":true,\n"
                    "#  \"request_id\":\"req-123\",\"user_id\":42,\"level\":\"info\",\n"
                    "#  \"timestamp\":\"2026-04-25T16:23:11.452123Z\"}</code></pre>"
                    "<p>Equivalentes: <code>pino</code> (Node), <code>zap</code> (Go), "
                    "<code>logback-json</code> (Java), <code>slog</code> (Go 1.21+).</p>"

                    "<h3>3. Correlation/trace ID, colando logs entre serviços</h3>"
                    "<p>Microservices têm um problema: o log de uma request fica espalhado em "
                    "5 serviços diferentes. Solução: propague um <strong>trace ID</strong> em "
                    "todo request (header HTTP <code>traceparent</code>, padrão W3C). "
                    "Cada serviço inclui esse ID em todo log que emite.</p>"
                    "<p>OpenTelemetry SDK faz isso transparentemente:</p>"
                    "<pre><code>from opentelemetry import trace\n"
                    "from opentelemetry.instrumentation.django import DjangoInstrumentor\n"
                    "DjangoInstrumentor().instrument()\n"
                    "\n"
                    "# Em qualquer log emitido durante a request, trace_id estará presente\n"
                    "log.info('order.created', order_id=order.id, total=order.total)</code></pre>"
                    "<p>Em incidente: pega o trace_id do log de erro, busca em todos os "
                    "serviços, vê a request inteira em ordem.</p>"

                    "<h3>4. O que NÃO logar (LGPD, GDPR, PCI-DSS)</h3>"
                    "<table>"
                    "<tr><td>Senhas, hashes, tokens</td><td>Mesmo em headers.</td></tr>"
                    "<tr><td>CPF, RG, dados de cartão</td><td>LGPD/PCI proíbem.</td></tr>"
                    "<tr><td>Dados de saúde</td><td>HIPAA, LGPD.</td></tr>"
                    "<tr><td>Cookies de sessão</td><td>Permitem session hijacking.</td></tr>"
                    "<tr><td>Conteúdo de uploads</td><td>Pode ter PII.</td></tr>"
                    "<tr><td>Endereços de email completos</td><td>Pseudonimize.</td></tr>"
                    "</table>"
                    "<p>Mitigações:</p>"
                    "<pre><code># Redaction com structlog\n"
                    "REDACT_KEYS = {'password', 'token', 'authorization', 'cookie', 'cpf'}\n"
                    "\n"
                    "def redact(_, __, event):\n"
                    "    for key in list(event):\n"
                    "        if key.lower() in REDACT_KEYS:\n"
                    "            event[key] = '***REDACTED***'\n"
                    "    return event\n"
                    "\n"
                    "structlog.configure(processors=[redact, ...])</code></pre>"
                    "<p>Auditoria periódica: pegue 1000 linhas aleatórias dos logs de prod e "
                    "veja se algo sensível escapou. Repita trimestralmente.</p>"

                    "<h3>5. Centralização: ELK, Loki, Cloud-native</h3>"
                    "<p>Opções:</p>"
                    "<ul>"
                    "<li><strong>Elastic Stack (ELK)</strong>: indexa tudo full-text. "
                    "Buscas poderosas. Caro em armazenamento e operação.</li>"
                    "<li><strong>OpenSearch</strong>: fork do Elastic (Apache 2.0).</li>"
                    "<li><strong>Grafana Loki</strong>: indexa só labels (não o conteúdo). "
                    "Storage barato (S3). Buscas via LogQL similar a PromQL. <em>Recomendado "
                    "para a maioria.</em></li>"
                    "<li><strong>CloudWatch Logs</strong> / <strong>Azure Monitor</strong> / "
                    "<strong>Cloud Logging</strong>: gerenciados, ótimos para começar, "
                    "podem ficar caros em escala.</li>"
                    "<li><strong>Datadog</strong>, <strong>New Relic</strong>, "
                    "<strong>Splunk</strong>: comerciais, completos, premium.</li>"
                    "</ul>"
                    "<p>Coletor (agente) recomendado: "
                    "<strong>OpenTelemetry Collector</strong>, vendor neutral, suporta "
                    "todos os destinos. Alternativas: <strong>Vector</strong> (rust, "
                    "rápido), <strong>Fluent Bit</strong>, <strong>Promtail</strong> (Loki).</p>"

                    "<h3>6. Stack típica em K8s</h3>"
                    "<pre><code># App emite JSON em stdout/stderr\n"
                    "# Promtail (DaemonSet) lê do filesystem do node\n"
                    "# Loki guarda em S3\n"
                    "# Grafana faz dashboards e queries\n"
                    "\n"
                    "{namespace=\"prod\", app=\"api\"} |= \"error\" | json | level=\"ERROR\" \\\n"
                    "  | line_format \"{{.timestamp}} {{.user_id}} {{.event}}\"</code></pre>"

                    "<h3>7. Retenção e custo</h3>"
                    "<p>Logs crescem rápido. Política típica:</p>"
                    "<ul>"
                    "<li><strong>Quente</strong> (busca rápida, indexado): 7-30 dias. "
                    "Loki/ES no SSD.</li>"
                    "<li><strong>Frio</strong> (busca lenta mas barato): 90-365 dias. "
                    "S3/Glacier.</li>"
                    "<li><strong>Auditoria</strong> (compliance): 1-7+ anos em bucket WORM "
                    "com object-lock. Imutável.</li>"
                    "</ul>"
                    "<p>Em SOC 2 Type II você costuma precisar provar 12 meses de logs de "
                    "auth. PCI-DSS exige 12 meses (3 imediatos). LGPD não tem mínimo legal "
                    "mas tem máximo (apague o que não precisa mais).</p>"

                    "<h3>8. Logs em incident response</h3>"
                    "<p>Em incidente, hostagent comprometido pode ter logs <em>locais</em> "
                    "alterados pelo atacante para esconder rastros. Por isso:</p>"
                    "<ul>"
                    "<li>Centralize antes do host ser comprometido.</li>"
                    "<li>Use bucket/sistema imutável para logs forensicamente relevantes "
                    "(auth, audit).</li>"
                    "<li>Tenha replication offsite (cross-region, ou cloud diferente).</li>"
                    "</ul>"
                    "<p>Logs que importam em incidente: auth (login, sudo, ssh), audit "
                    "(comandos privilegiados), network (firewall drops, DNS queries), "
                    "aplicação (errors, anomalias)."

                    "<h3>9. Métricas vs logs vs traces</h3>"
                    "<p>Os três pilares da observabilidade:</p>"
                    "<table>"
                    "<tr><th>Sinal</th><th>Cardinalidade</th><th>Custo</th><th>Uso típico</th></tr>"
                    "<tr><td>Métricas</td><td>baixa</td><td>baixo</td>"
                    "<td>'Quantas requests por segundo? Latência p99?'</td></tr>"
                    "<tr><td>Logs</td><td>alta</td><td>médio-alto</td>"
                    "<td>'O que aconteceu naquela requisição específica?'</td></tr>"
                    "<tr><td>Traces</td><td>muito alta</td><td>alto</td>"
                    "<td>'Por onde passou e quanto demorou cada salto?'</td></tr>"
                    "</table>"
                    "<p>OpenTelemetry padroniza coleta dos três; armazenamento ainda é "
                    "separado (Prometheus para métricas, Loki para logs, Tempo para "
                    "traces).</p>"

                    "<h3>10. Caso real: o log que custou US$ 1B</h3>"
                    "<p>Em 2017, a Equifax foi violada (147M de americanos). Investigação "
                    "mostrou que o atacante esteve dentro da rede por 76 dias. Os logs "
                    "tinham os indícios, incluindo tráfego enorme saindo para um IP "
                    "estrangeiro, mas o sistema de monitoramento estava configurado para "
                    "ignorar uma certa categoria, e o time não revisava os logs "
                    "manualmente. Resultado: US$ 1.4B em multas, settlement e perdas. "
                    "Lição: log sem alerta+revisão é só armazenamento caro.</p>"
                ),
                "practical": (
                    "(1) Configure sua app para emitir JSON estruturado com "
                    "<code>structlog</code> (Python) ou similar, incluindo "
                    "<code>trace_id</code> e <code>user_id</code> em cada linha.<br>"
                    "(2) Localmente, leia com <code>jq</code>: "
                    "<code>./app | jq 'select(.level==\"error\")'</code>.<br>"
                    "(3) Suba Loki + Promtail + Grafana via docker-compose "
                    "(<a href='https://grafana.com/docs/loki/latest/setup/install/docker/'>guia</a>) "
                    "e envie os logs.<br>"
                    "(4) Em Grafana, crie dashboard com:<br>"
                    "&nbsp;&nbsp;• taxa de erros nos últimos 5min;<br>"
                    "&nbsp;&nbsp;• top 10 user_ids com mais erros;<br>"
                    "&nbsp;&nbsp;• grafico de logs por nível ao longo do tempo.<br>"
                    "(5) Bônus: simule uma sessão de incidente, pegue um trace_id de erro, "
                    "filtre todos os logs com aquele trace_id e reconstitua a request "
                    "completa."
                ),
            },
            "materials": [
                m("systemd journald",
                  "https://www.freedesktop.org/software/systemd/man/latest/systemd-journald.service.html",
                  "docs", ""),
                m("OWASP Logging Cheat Sheet",
                  "https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html",
                  "docs", ""),
                m("Honeycomb: Structured logging",
                  "https://www.honeycomb.io/blog/structured-logging-and-your-team",
                  "article", ""),
                m("Grafana Loki", "https://grafana.com/docs/loki/latest/", "docs", ""),
                m("rsyslog manual", "https://www.rsyslog.com/doc/", "docs", ""),
                m("structlog (Python)",
                  "https://www.structlog.org/", "tool",
                  "Logs estruturados em Python sem dor."),
            ],
            "questions": [
                q("Qual comando vê logs do serviço nginx via systemd?",
                  "journalctl -u nginx",
                  ["systemctl logs nginx", "logread nginx", "tail /etc/nginx"],
                  "-u filtra por unidade. -f acompanha em tempo real, -p err filtra por prioridade."),
                q("Por que preferir logs em JSON?",
                  "Facilita parsing, indexação e busca por campo.",
                  ["São menores.",
                   "Substituem métricas.",
                   "Compactam automaticamente."],
                  "Texto livre vira regex doloroso. JSON tem schema e ferramentas de busca/agg nativas."),
                q("O que é correlation ID?",
                  "Identificador único que liga logs da mesma requisição entre serviços.",
                  ["Chave de criptografia.",
                   "Hash do disco.",
                   "Versão do schema."],
                  "Geralmente o trace_id do OpenTelemetry, propagado em headers HTTP."),
                q("Onde NÃO devem aparecer dados sensíveis (senhas, CPF)?",
                  "Em logs.",
                  ["Em variáveis de ambiente.",
                   "Em arquivos rotacionados.",
                   "Em traces criptografados."],
                  "LGPD/GDPR/PCI proíbem. Use redaction no logger e revise periodicamente uma "
                  "amostra dos logs."),
                q("Qual ferramenta agrega logs com baixo custo armazenando-os no S3?",
                  "Grafana Loki",
                  ["Prometheus", "Tempo (traces)", "Beats apenas"],
                  "Loki indexa apenas labels (não o corpo) e usa storage barato, perfeito para alto volume."),
                q("Por que rotacionar logs?",
                  "Evitar que ocupem todo o disco e facilitar arquivamento.",
                  ["Aumentar performance da CPU.",
                   "Substituir backup.",
                   "Habilitar IPv6."],
                  "logrotate é o utilitário padrão. journald já rotaciona internamente por tamanho/tempo."),
                q("`logrotate` configura-se em:",
                  "/etc/logrotate.conf e /etc/logrotate.d/*",
                  ["/etc/passwd", "/var/lib/rotate", "/proc/log"],
                  "Cada serviço pode ter um arquivo próprio em /etc/logrotate.d/ com sua política."),
                q("Qual prioridade no syslog representa erros críticos?",
                  "crit (2)",
                  ["debug (7)", "info (6)", "notice (5)"],
                  "Hierarquia: emerg(0), alert(1), crit(2), err(3), warning(4), notice(5), info(6), debug(7)."),
                q("`journalctl --vacuum-size=200M` faz:",
                  "Reduz o journal a no máximo 200 MB.",
                  ["Reinicia o journald.",
                   "Move logs para o S3.",
                   "Apaga só logs do kernel."],
                  "Há também --vacuum-time=7d para limitar por idade."),
                q("Por que centralizar logs?",
                  "Permite correlação entre máquinas e sobrevive à perda do host.",
                  ["Aumenta a entropia.",
                   "Substitui logs locais.",
                   "Acelera o boot."],
                  "Em incidente, host pode estar comprometido e logs locais alterados, central é forensics-friendly."),
            ],
        },
        # =====================================================================
        # 1.10 Cultura DevSecOps
        # =====================================================================
        {
            "title": "Cultura DevSecOps",
            "summary": "Segurança não é uma fase, é um hábito em todas as etapas.",
            "lesson": {
                "intro": (
                    "Toda ferramenta cara do mercado, SAST de US$ 100k/ano, scanner de "
                    "vulnerabilidade gigante, SOC terceirizado, falha sem cultura. "
                    "DevSecOps é o que transforma 'segurança não é meu problema' em "
                    "'segurança é parte do meu trabalho como engenheiro'.<br><br>"
                    "Esta aula é menos sobre código e mais sobre <em>como times reais "
                    "operam</em>. Por que cultura ganha de processo e ferramenta sempre, "
                    "como construir essa cultura, métricas que importam, e os anti-padrões "
                    "organizacionais que matam programas de segurança."
                ),
                "body": (
                    "<h3>1. O que é DevSecOps de verdade</h3>"
                    "<p>DevOps tirou paredes entre dev e ops. DevSecOps faz o mesmo com "
                    "segurança. Em prática:</p>"
                    "<ul>"
                    "<li>Segurança é responsabilidade <em>de todos</em>, não 'do time de "
                    "segurança'.</li>"
                    "<li>Controles automatizados &gt; gate humano em pull request.</li>"
                    "<li>Feedback rápido (segundos no editor, minutos no PR) "
                    "&gt; relatório de auditoria 6 meses depois.</li>"
                    "<li>Erros são oportunidade de aprendizado, não cassação.</li>"
                    "</ul>"
                    "<p>O time de segurança vira <em>enabler</em>: ferramentas, treinamento, "
                    "padrões. As decisões ficam com quem está mais perto do código.</p>"

                    "<h3>2. Shift-left que funciona vs shift-left teatro</h3>"
                    "<p>Shift-left é trazer segurança para fases iniciais. Mas existe versão "
                    "boa e versão ruim:</p>"
                    "<table>"
                    "<tr><th>Funciona</th><th>É teatro</th></tr>"
                    "<tr><td>Linter no editor</td>"
                    "<td>Relatório PDF mensal</td></tr>"
                    "<tr><td>SAST no PR (3-min)</td>"
                    "<td>Pentest anual no fim do release</td></tr>"
                    "<tr><td>Threat model em design review</td>"
                    "<td>Reunião de aprovação 3h antes do deploy</td></tr>"
                    "<tr><td>SBOM gerado em todo build</td>"
                    "<td>Planilha que ninguém atualiza</td></tr>"
                    "<tr><td>Runbook executável (PIR)</td>"
                    "<td>Wiki que ninguém abre</td></tr>"
                    "</table>"
                    "<p>Critério: <em>o engenheiro recebe feedback enquanto ainda está "
                    "trabalhando no problema</em>.</p>"

                    "<h3>3. Threat modeling, STRIDE em 1 página</h3>"
                    "<p>STRIDE são as 6 categorias de ameaça:</p>"
                    "<ul>"
                    "<li><strong>S</strong>poofing, alguém finge ser outro.</li>"
                    "<li><strong>T</strong>ampering, alguém altera dados em trânsito ou "
                    "repouso.</li>"
                    "<li><strong>R</strong>epudiation, alguém nega ter feito algo, sem "
                    "rastro.</li>"
                    "<li><strong>I</strong>nformation Disclosure, vazamento.</li>"
                    "<li><strong>D</strong>enial of Service, sistema cai sob carga ou "
                    "ataque.</li>"
                    "<li><strong>E</strong>levation of Privilege, usuário comum vira admin.</li>"
                    "</ul>"
                    "<p>Em design review de feature relevante, escreva uma página "
                    "respondendo:</p>"
                    "<ol>"
                    "<li><strong>O que estamos construindo?</strong> (1 parágrafo + "
                    "diagrama)</li>"
                    "<li><strong>Quais são os ativos?</strong> (dados, contas, etc.)</li>"
                    "<li><strong>Quem são os atores?</strong> (legítimos e hostis)</li>"
                    "<li><strong>Para cada componente, 1 ameaça por categoria STRIDE</strong></li>"
                    "<li><strong>Mitigação para cada ameaça</strong> (e o que aceitamos como "
                    "risco residual)</li>"
                    "</ol>"
                    "<p>Mudar arquitetura pré-código é barato. Pós-deploy é caro e político.</p>"

                    "<h3>4. Postmortems blameless</h3>"
                    "<p>O timing do incidente é o de menor capacidade emocional. Em vez de "
                    "'quem aprovou aquilo?', faça:</p>"
                    "<ul>"
                    "<li><strong>Timeline factual</strong>: que aconteceu quando, baseado em "
                    "logs.</li>"
                    "<li><strong>Causas contributivas</strong> (não 'a causa'): que decisões/"
                    "lacunas/condições levaram aqui?</li>"
                    "<li><strong>O que funcionou bem</strong>: detecção, comunicação, "
                    "rollback.</li>"
                    "<li><strong>Action items</strong> com dono e prazo. Nem tudo precisa ser "
                    "corrigido, algumas coisas são <em>aceito como risco</em> com "
                    "justificativa.</li>"
                    "</ul>"
                    "<p>Compartilhe internamente sem censura. Falhas são professores caros, "
                    "aproveite. Cultura blameless dá segurança psicológica para o time "
                    "<em>relatar</em>, sem ela, próximos incidentes serão escondidos.</p>"

                    "<h3>5. Métricas DORA + DevSecOps</h3>"
                    "<p>O <a href='https://dora.dev/'>relatório DORA</a> identifica 4 métricas "
                    "que separam times de elite:</p>"
                    "<ul>"
                    "<li><strong>Lead time</strong>: do commit ao prod.</li>"
                    "<li><strong>Deployment frequency</strong>: quantas vezes por dia/semana.</li>"
                    "<li><strong>Change failure rate</strong>: % de deploys que dão problema.</li>"
                    "<li><strong>MTTR</strong>: tempo médio para recuperar.</li>"
                    "</ul>"
                    "<p>Métricas de segurança que se acoplam bem:</p>"
                    "<ul>"
                    "<li><strong>SLA de patching</strong>: critical em 72h, high em 7 dias, "
                    "medium em 30 dias. Mede % dentro do SLA.</li>"
                    "<li><strong>MTTD</strong>: tempo médio para detectar incidente.</li>"
                    "<li><strong>Cobertura de SAST/SCA</strong>: % de repos com pipeline ativo.</li>"
                    "<li><strong>Falsos positivos suprimidos com justificativa</strong> "
                    "(qualidade do programa).</li>"
                    "<li><strong>Threat models por release</strong>.</li>"
                    "<li><strong>Tempo médio do quiz CTF interno</strong> (se você roda).</li>"
                    "</ul>"
                    "<p>Cuidado: métrica vira competição perversa. Se você mede 'CVEs "
                    "fechadas', as pessoas vão fechar trivialidades e ignorar high. Mire em "
                    "métricas de <em>comportamento</em>, não de output.</p>"

                    "<h3>6. Security champions</h3>"
                    "<p>Modelo de escala: em vez de centralizar tudo no time de segurança "
                    "(que vira gargalo), plante 'campeões' dentro de cada squad, devs com "
                    "interesse no tema.</p>"
                    "<p>Como rodar:</p>"
                    "<ol>"
                    "<li>Cada squad escolhe (não impõe) um champion.</li>"
                    "<li>Encontro mensal de champions com o time de segurança: brief de "
                    "novidades, casos recentes, ferramentas.</li>"
                    "<li>Trilha de capacitação: cursos, CTFs internos, conferências.</li>"
                    "<li>Reconhecimento real: prêmio anual, menção em performance review.</li>"
                    "<li>Champions são <em>ponto focal</em>, não responsáveis sozinhos.</li>"
                    "</ol>"
                    "<p>Resultado: time de segurança escala 5-10x sem aumentar headcount.</p>"

                    "<h3>7. OWASP SAMM, modelo de maturidade</h3>"
                    "<p>SAMM (Software Assurance Maturity Model) avalia 5 funções:</p>"
                    "<ol>"
                    "<li><strong>Governance</strong> (estratégia, política, educação)</li>"
                    "<li><strong>Design</strong> (threat modeling, requisitos)</li>"
                    "<li><strong>Implementation</strong> (build seguro, hardening)</li>"
                    "<li><strong>Verification</strong> (test/SAST/DAST, code review)</li>"
                    "<li><strong>Operations</strong> (incident, vulnerability mgmt, env "
                    "hardening)</li>"
                    "</ol>"
                    "<p>Cada uma em 4 níveis (0=ausente, 3=otimizado). Use como mapa de "
                    "investimento, pegue as duas funções mais fracas e priorize.</p>"

                    "<h3>8. Anti-patterns organizacionais</h3>"
                    "<table>"
                    "<tr><td><strong>Time de seg como gate</strong></td>"
                    "<td>Aprovação manual de cada deploy. Vira gargalo, gera atrito, "
                    "force times a contornar.</td></tr>"
                    "<tr><td><strong>Compras-lideradas</strong></td>"
                    "<td>Contratam ferramenta de US$ 200k/ano sem definir como vai ser usada. "
                    "Shelfware caro.</td></tr>"
                    "<tr><td><strong>Métricas vaidade</strong></td>"
                    "<td>'Bloqueamos 1M de ataques!' sem dizer quais eram bots vs humanos.</td></tr>"
                    "<tr><td><strong>Empurrar débito</strong></td>"
                    "<td>'Resolve depois do release' indefinidamente. Juros chegam em "
                    "incidente.</td></tr>"
                    "<tr><td><strong>Heroísmo</strong></td>"
                    "<td>Uma pessoa carrega tudo. Quando ela sai, programa cai.</td></tr>"
                    "<tr><td><strong>Compliance teatro</strong></td>"
                    "<td>Performar para auditor sem proteger nada de fato.</td></tr>"
                    "</table>"

                    "<h3>9. Caso real: a transformação da Microsoft</h3>"
                    "<p>Após anos de ataques (Slammer, Blaster, etc.), Bill Gates mandou em "
                    "2002 um email para toda a empresa: 'Trustworthy Computing'. Em pouco "
                    "tempo:</p>"
                    "<ul>"
                    "<li>Treinamento obrigatório em SDL para 8000+ engenheiros.</li>"
                    "<li>Threat modeling obrigatório para qualquer feature relevante.</li>"
                    "<li>SDL (Security Development Lifecycle) virou parte do processo "
                    "padrão.</li>"
                    "<li>Internalização de fuzzing, code analysis, pentest.</li>"
                    "</ul>"
                    "<p>Resultado: 5 anos depois, a Microsoft saiu de 'piada de segurança' "
                    "para referência da indústria, e abriu o playbook para todo mundo. "
                    "Isso é cultura.</p>"

                    "<h3>10. Resumo: o que sobrar quando processos falham</h3>"
                    "<p>Cultura é o que sobra quando processos falham. Quando o engenheiro vê "
                    "uma vulnerabilidade no código do colega e abre PR consertando, cultura. "
                    "Quando o PM aceita atrasar uma feature para fechar débito de segurança, "
                    "cultura. Quando o CEO reage a incidente com 'o que precisamos para isso "
                    "não acontecer de novo?' em vez de 'quem demitimos?', cultura.</p>"
                    "<p>Ferramenta ajuda. Processo organiza. Cultura sustenta.</p>"
                ),
                "practical": (
                    "Pegue uma feature que sua equipe vai construir nas próximas 2 semanas "
                    "(ex.: upload de avatar, exportação de relatório, login social). Faça um "
                    "threat model STRIDE de 1 página:<br>"
                    "(1) Diagrama de fluxo (data flow diagram simples).<br>"
                    "(2) Liste 1 ameaça por categoria STRIDE, total 6.<br>"
                    "(3) Para cada uma, escreva 1 mitigação concreta.<br>"
                    "(4) Para cada mitigação, marque: 'já temos / vamos implementar / "
                    "aceitamos como risco'.<br>"
                    "(5) Compartilhe com o time. Peça crítica honesta.<br>"
                    "(6) Bônus: depois do feature deploy, revise o doc, quantas das "
                    "mitigações realmente entraram? O que aprendeu?"
                ),
            },
            "materials": [
                m("DevSecOps Manifesto", "https://www.devsecops.org/", "article", ""),
                m("Google SRE Book, Postmortem Culture",
                  "https://sre.google/sre-book/postmortem-culture/", "book", ""),
                m("OWASP SAMM", "https://owaspsamm.org/", "docs",
                  "Modelo de maturidade em segurança de software."),
                m("ThoughtWorks Tech Radar",
                  "https://www.thoughtworks.com/radar", "article", ""),
                m("Microsoft STRIDE",
                  "https://learn.microsoft.com/azure/security/develop/threat-modeling-tool-threats",
                  "docs", ""),
                m("DORA: Accelerate State of DevOps",
                  "https://dora.dev/research/", "article",
                  "Pesquisa anual com métricas de elite."),
            ],
            "questions": [
                q("O que significa 'shift-left' em DevSecOps?",
                  "Trazer segurança para fases iniciais do desenvolvimento.",
                  ["Ignorar segurança no deploy.",
                   "Mudar para a esquerda no monitor.",
                   "Empurrar para a direita do pipeline."],
                  "Linter no editor, SAST no PR, feedback rápido em vez de bloqueio no fim."),
                q("STRIDE serve para:",
                  "Threat modeling (Spoofing, Tampering, Repudiation, Info disclosure, DoS, Elevation).",
                  ["Tipos de TLS.",
                   "Formatos de log.",
                   "Modos de container."],
                  "Cada letra é uma categoria, força você a pensar fora da sua zona."),
                q("O que é um postmortem 'blameless'?",
                  "Foco em causas sistêmicas, não em culpar pessoas.",
                  ["Documento secreto.",
                   "Substituto de SLA.",
                   "Backup periódico."],
                  "Cultura blameless dá segurança psicológica para o time relatar erros honestamente."),
                q("MTTR mede:",
                  "Tempo médio para restauração após incidente.",
                  ["Quantidade de bugs.",
                   "Latência de rede.",
                   "Tempo de boot."],
                  "Junto com MTTD, é métrica DORA de operação. Menor = melhor."),
                q("Qual NÃO é prática DevSecOps?",
                  "Atrasar correções para depois do release.",
                  ["Automatizar SAST no CI.",
                   "Threat modeling em design review.",
                   "Rotacionar segredos."],
                  "Empurrar débito de segurança para depois é como deixar de pagar boleto: "
                  "juros (incidente) chegam."),
                q("DevSecOps depende mais de:",
                  "Cultura e responsabilidade compartilhada.",
                  ["Comprar a ferramenta mais cara.",
                   "Centralizar tudo no time de segurança.",
                   "Ignorar dev."],
                  "Ferramenta sem cultura vira shelfware caro."),
                q("OWASP SAMM é:",
                  "Um modelo de maturidade em segurança de software.",
                  ["Um framework JS.",
                   "Um padrão de criptografia.",
                   "Um banco de dados."],
                  "Avalia 5 funções (governança, design, implementação, verificação, operações) em 4 níveis."),
                q("Como medir maturidade do pipeline?",
                  "Definindo KPIs como cobertura SAST, SCA, falsos positivos e tempo de patch.",
                  ["Contando linhas de código.",
                   "Pelo número de commits.",
                   "Pelo tamanho do binário."],
                  "Métrica precisa estar atrelada a comportamento, não vira competição numérica vazia."),
                q("Threat modeling é mais útil:",
                  "Cedo, no design, antes do código existir.",
                  ["Após o incidente.",
                   "Apenas em produção.",
                   "Só em apps mobile."],
                  "Mudar arquitetura pré-código é barato; pós-deploy é caro e político."),
                q("Quem é responsável pela segurança em DevSecOps?",
                  "Todos no time, com champions de segurança apoiando.",
                  ["Apenas o blue team.",
                   "Apenas o auditor externo.",
                   "Apenas o CISO."],
                  "Modelo distribuído ('shift-everywhere') escala muito melhor que centralizado."),
            ],
        },
    ],
}
