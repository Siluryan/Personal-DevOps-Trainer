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
                """<h3>1. Filosofia: tudo é arquivo</h3>
<p>O lema clássico do Unix se aplica integralmente no Linux: tudo é
representado como arquivo — disco (<code>/dev/sda</code>), socket de
rede (<code>/proc/net/tcp</code>), processo rodando
(<code>/proc/&lt;pid&gt;</code>), configuração do próprio kernel
(<code>/sys</code>), até dispositivo USB e GPIO. A consequência prática
é que o MESMO modelo de permissão (rwx combinado com dono e grupo)
controla literalmente tudo isso de uma vez, sem exceção especial para
cada tipo de recurso. Quando um atacante explora uma vulnerabilidade
para escrever em <code>/dev/mem</code> ou
<code>/proc/sys/kernel/core_pattern</code>, ele está usando exatamente
esse modelo de arquivo unificado para subverter o kernel — não um
mecanismo diferente. Aprender Linux a fundo é, em boa medida, aprender
quais arquivos específicos importam e quem deveria ter permissão de ler
ou escrever em cada um.</p>

<h3>2. Modelo de identidade: UID, GID e processos</h3>
<p>Todo processo roda em nome de um <strong>UID</strong> (effective
user id) e carrega um <strong>GID</strong> primário mais um conjunto de
grupo suplementar. Cada processo HERDA essa identidade do próprio pai
— o init/<code>systemd</code> começa como UID 0 (root), e todo processo
filho deriva dessa raiz. Três faixas de UID têm significado
convencional: <strong>UID 0</strong> é o próprio root, que ignora
literalmente todo check de permissão — é exatamente por isso que
serviço exposto à internet nunca deveria rodar sob esse UID; UID entre
1 e 999 são usuários de sistema criados pelos próprios pacotes
(<code>www-data</code>, <code>postgres</code>, <code>nobody</code>); e
UID a partir de 1000 são usuários humanos em distribuição moderna.
Inspecionar essa identidade é direto:</p>
<pre><code>id                 # quem sou eu (uid, gid, grupos)
id deploy          # idem para outro usuário
ps -eo pid,uid,user,cmd | head
cat /etc/passwd    # mapeamento UID ↔ login ↔ shell
cat /etc/group     # mapeamento GID ↔ nome do grupo</code></pre>
<p>Um detalhe de segurança que muita gente ignora: senha NUNCA fica em
<code>/etc/passwd</code> em sistema moderno — o hash mora
especificamente em <code>/etc/shadow</code>, legível só pelo root. Usar
<code>/etc/passwd</code> como referência de leitura geral é normal e
esperado; vazar <code>/etc/shadow</code> para outro usuário já é
incidente de segurança propriamente dito.</p>

<h3>3. Permissões clássicas: o modelo rwx</h3>
<p>Todo arquivo carrega dono, grupo, e três classes de permissão
(user, group, other), cada uma com três bits (<code>r</code>=4,
<code>w</code>=2, <code>x</code>=1) representáveis em octal:</p>
<pre><code>chmod 750 deploy.sh
  └ user 7 = r+w+x
  └ group 5 = r+x  (sem write)
  └ other 0 = nada

ls -l deploy.sh
-rwxr-x---  1 deploy web  142 Apr 25 16:12 deploy.sh</code></pre>
<p>Em diretório, o significado muda de forma sutil e importante:
<code>r</code> permite LISTAR nomes de arquivo dentro, <code>x</code>
permite ENTRAR no diretório, e <code>w</code> permite CRIAR ou
REMOVER arquivo ali. Isso torna perfeitamente possível ter um
diretório com <code>x</code> mas sem <code>r</code> — nesse caso, é
possível acessar um arquivo específico se você já souber o nome exato,
mas impossível listar o conteúdo do diretório para descobrir esse nome
por conta própria. Para mudança incremental, o modo simbólico costuma
ser mais legível que recalcular o octal inteiro:</p>
<pre><code>chmod g+rw arquivo       # add read+write para o grupo
chmod o-x  diretorio/     # remove execute do 'other'
chmod -R u+rwX,g+rX,o-rwx /srv/app/   # X executa só em diretórios</code></pre>

<h3>4. Bits especiais: setuid, setgid, sticky</h3>
<p>Três bits adicionais alteram como um binário se comporta em
execução. O <strong>setuid</strong> (4xxx) faz o programa rodar com o
privilégio do DONO do arquivo, não de quem o invocou na prática — é
exatamente assim que o comando <code>passwd</code> consegue alterar
<code>/etc/shadow</code> mesmo sendo executado por um usuário comum sem
privilégio nenhum. Mal aplicado, é um vetor clássico de escalada de
privilégio — todo binário com setuid presente numa máquina deveria
estar numa whitelist auditada, não deixado ao acaso. O
<strong>setgid</strong> (2xxx) segue a mesma lógica, mas com o grupo em
vez do dono; em diretório, garante que todo arquivo NOVO criado ali
herda automaticamente o grupo do diretório, útil especificamente para
área compartilhada de equipe. E o <strong>sticky bit</strong> (1xxx),
aplicado a diretório, restringe quem pode APAGAR um arquivo àquele que
o criou (ou ao dono do próprio diretório) — é exatamente por isso que
<code>/tmp</code> roda com modo <code>1777</code>: qualquer usuário
cria arquivo ali livremente, mas só quem criou consegue apagar o
próprio arquivo depois.</p>
<pre><code>find / -perm -4000 -type f 2&gt;/dev/null   # binários setuid
find / -perm -2000 -type f 2&gt;/dev/null   # binários setgid</code></pre>

<h3>5. Para além de rwx: ACLs e capabilities</h3>
<p>O modelo rwx tem apenas três classes fixas de permissão — quando
isso não basta, as ACLs POSIX permitem granularidade por usuário ou
grupo específico, além do dono e grupo padrão do arquivo:</p>
<pre><code>setfacl -m u:carlos:r-- /srv/data/relatorio.csv
setfacl -m g:auditoria:r-x /srv/scripts/
getfacl /srv/data/relatorio.csv</code></pre>
<p>As Linux capabilities resolvem um problema diferente: decompõem o
poder inteiro de root em cerca de 40 grãos individuais
(<code>man capabilities(7)</code>). Em vez de conceder root completo a
um binário web só porque ele precisa bindar na porta 80 (abaixo de
1024, restrita por padrão a root), é possível conceder apenas
<code>CAP_NET_BIND_SERVICE</code>, exatamente a fração de privilégio
necessária:</p>
<pre><code>setcap cap_net_bind_service=+ep /usr/local/bin/myserver
getcap /usr/local/bin/myserver</code></pre>
<p>Esse é justamente o mecanismo por trás de imagem Docker bem
construída que consegue escutar em porta privilegiada mesmo rodando
como usuário não-root dentro do container.</p>

<h3>6. Processos, sinais e systemd</h3>
<p>Todo processo carrega um <strong>PID</strong>, um pai
(<strong>PPID</strong>), e um estado — <code>R</code> (running),
<code>S</code> (sleeping), <code>D</code> (disk wait), <code>Z</code>
(zombie) — inspecionável via <code>ps auxf</code> ou interativamente
via <code>htop</code>. O kernel se comunica com processo através de
<strong>sinais</strong>, cada um com um significado convencional
específico: <code>SIGTERM (15)</code> pede terminação educada — um
processo bem-comportado fecha conexão, salva estado e sai sozinho, e
deveria ser sempre o primeiro tentado; <code>SIGKILL (9)</code> termina
imediatamente sem NENHUMA chance de cleanup, reservado para quando
SIGTERM já não responde; <code>SIGHUP (1)</code>, historicamente
"hangup", virou o sinal convencional para recarregar configuração sem
reiniciar o processo inteiro; <code>SIGINT (2)</code> é o Ctrl+C do
terminal; e <code>SIGSTOP/SIGCONT</code> pausam e retomam a execução.
Em distribuição moderna, todo serviço é gerenciado pelo systemd através
de units:</p>
<pre><code>systemctl status nginx
systemctl restart nginx
systemctl reload nginx       # equivale a SIGHUP, sem downtime
journalctl -u nginx -f       # logs em tempo real
systemctl list-units --failed</code></pre>

<h3>7. Filesystem hierarchy padrão (FHS)</h3>
<p>Saber de antemão onde cada tipo de arquivo mora economiza tempo real
de busca em qualquer investigação. <code>/etc</code> guarda
configuração do sistema, editável apenas por root. <code>/usr/bin</code>
e <code>/usr/sbin</code> guardam binário do sistema, enquanto
<code>/usr/local/bin</code> é reservado para binário instalado
manualmente fora do gerenciador de pacote. <code>/var</code> guarda
dado VARIÁVEL — log, cache, spool, banco de dados — e faz sentido
morar num filesystem separado em produção, justamente porque cresce de
forma imprevisível. <code>/home</code> guarda dado de usuário humano.
<code>/srv</code> guarda dado servido diretamente por um serviço (web,
FTP). <code>/opt</code> guarda software de terceiro "self-contained",
empacotado de forma independente do resto do sistema. <code>/proc</code>
e <code>/sys</code> são pseudo-filesystems expostos diretamente pelo
kernel, sem existir fisicamente em disco. <code>/dev</code> representa
dispositivo. E <code>/run</code> e <code>/tmp</code> são efêmeros,
zerados a cada reboot.</p>

<h3>8. Anti-patterns clássicos</h3>
<ul>
<li><strong><code>chmod 777 /srv/app</code></strong>: qualquer usuário
do mesmo sistema ganha permissão de escrita — um atacante com QUALQUER
outra conta na mesma máquina consegue injetar payload direto na
aplicação legítima, uma escalada trivial de executar.</li>
<li><strong>Rodar serviço como root</strong>: qualquer bug conhecido
no serviço (Heartbleed, Log4Shell) vira automaticamente RCE como
root, e portanto comprometimento total da máquina — usuário dedicado
combinado com <code>User=</code> no systemd fecha essa lacuna
diretamente.</li>
<li><strong>Adicionar usuário ao grupo <code>sudo</code> sem regra
específica</strong>: concede poder total quando provavelmente só um
comando pontual era realmente necessário — prefira um drop-in em
<code>/etc/sudoers.d/</code> liberando exatamente o comando
específico.</li>
<li><strong>Editar arquivo de configuração como root sem backup
antes</strong>: um <code>vim /etc/sshd_config</code> esquecendo de
revisar <code>PermitRootLogin</code> pode trancar o próprio operador
fora do servidor de produção sem aviso — <code>cp arquivo
arquivo.bak</code> antes de qualquer edição custa segundos e evita
esse cenário inteiro.</li>
<li><strong>Esquecer a permissão correta em <code>~/.ssh</code></strong>:
o sshd recusa autenticação SILENCIOSAMENTE quando o diretório ou
arquivo tem permissão frouxa demais — a única forma de descobrir isso é
olhando <code>journalctl -u sshd</code> depois que a autenticação já
falhou sem mensagem clara na tela do cliente.</li>
</ul>

<h3>9. Caso real: o ataque no <code>/tmp</code></h3>
<p>Em 2016, várias distribuições precisaram mudar o comportamento
padrão de <code>/tmp</code> para um tmpfs isolado por usuário, porque
um <code>/tmp</code> compartilhado entre todos os processos virou vetor
recorrente de ataque: um serviço A criava um arquivo com nome
PREVISÍVEL (<code>/tmp/upload.txt</code>); um atacante, sabendo disso
de antemão, criava ANTES um symlink com esse mesmo nome apontando para
<code>/etc/shadow</code>; e o serviço, rodando como root, ao "criar"
seu próprio arquivo temporário, na verdade sobrescrevia o shadow
inteiro através do symlink já plantado. Foi exatamente esse padrão de
ataque que popularizou o <code>PrivateTmp=true</code> no systemd —
uma mudança relativamente pequena no kernel e no systemd que eliminou
uma classe inteira de bug de uma vez, sem exigir que cada serviço
individual fosse corrigido separadamente.</p>

<h3>10. Checklist mental ao se conectar a um host novo</h3>
<ol>
<li><code>uname -a</code>, para conhecer kernel e arquitetura.</li>
<li><code>cat /etc/os-release</code>, para saber qual distribuição e
versão exatamente.</li>
<li><code>id</code> e <code>sudo -l</code>, para saber quem você é e o
que exatamente pode fazer.</li>
<li><code>ss -tulpn</code>, para ver quais portas estão abertas e
quem está escutando cada uma.</li>
<li><code>systemctl list-units --type=service --state=running</code>,
para o inventário de serviço ativo.</li>
<li><code>df -h</code> e <code>free -h</code>, para disco e memória
disponíveis.</li>
<li><code>journalctl -p err -S 'today'</code>, para erro recente que
já pode indicar problema em andamento.</li>
</ol>
<p>Em dois minutos rodando essa sequência, dá para saber se está pisando
em terreno familiar e saudável, ou se a máquina já apresenta sinal de
algo comprometido antes mesmo de investigar mais a fundo.</p>"""
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
                  "Leitura, escrita e execução (rwx) para o dono do arquivo.",
                  ["Um bit de SUID combinado com sticky bit, não permissão comum de dono.",
                   "Leitura e escrita combinadas para o grupo, sem execução liberada.",
                   "Execução isolada para o dono, sem leitura ou escrita concedidas."],
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
                  ["Um usuário de sistema criado especificamente para rodar o servidor web nginx.",
                   "Um usuário criado durante a instalação, mas sem qualquer privilégio especial.",
                   "Uma conta reservada para acesso temporário de visitantes na máquina."],
                  "UID 0 ignora checks de permissão, por isso processos críticos não devem rodar como root."),
                q("Qual sinal `kill -9 PID` envia para o processo?",
                  "SIGKILL, termina o processo imediatamente sem chance de cleanup.",
                  ["SIGTERM, pede o encerramento e dá tempo para o processo salvar estado antes.",
                   "SIGHUP, recarrega a configuração do processo sem derrubar a conexão atual.",
                   "SIGSTOP, pausa o processo, que pode ser retomado depois com SIGCONT."],
                  "SIGKILL não pode ser ignorado nem capturado. Prefira SIGTERM (15) sempre que possível."),
                q("Em `ls -l`, a string `-rwxr-x---` significa que o grupo pode:",
                  "Ler e executar, mas não escrever.",
                  ["Escrever e ler o conteúdo, mas sem permissão para executar o arquivo.",
                   "Executar sem restrição, incluindo escrita liberada para o grupo inteiro.",
                   "Bloqueado por completo, o grupo não acessa o arquivo de forma alguma."],
                  "r-x para o grupo (5 em octal) e --- para outros (0). Modo final 750."),
                q("Onde ficam os usuários e seus shells padrão?",
                  "/etc/passwd",
                  ["/etc/shadow, onde o hash de senha fica guardado, legível só pelo root.",
                   "/var/log/users, um arquivo de log que não existe por padrão no Linux.",
                   "/root/.bashrc, configuração de shell exclusiva da conta root."],
                  "Hashes de senha ficam em /etc/shadow (legível só para root). /etc/passwd "
                  "lista usuários, UIDs, home e shell."),
                q("Qual comando mostra o uso de disco por diretório?",
                  "du",
                  ["ls -lh, que lista arquivo por arquivo sem somar o total do diretório.",
                   "free -m, que mostra memória RAM e swap, não uso de disco.",
                   "df, que mostra uso por sistema de arquivo montado, não por diretório."],
                  "`du -sh *` é o atalho clássico. df mostra uso por filesystem; free mostra memória."),
                q("O que faz o bit setuid (`chmod u+s`) em um executável?",
                  "Roda o programa com privilégio do dono do arquivo, não de quem o executou.",
                  ["Aumenta a prioridade de agendamento do processo no escalonador do kernel.",
                   "Bloqueia qualquer escrita no arquivo, mesmo pelo próprio dono original do binário.",
                   "Esconde o arquivo de listagens comuns, exigindo uma flag extra passada ao ls."],
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
                  ["Mostra a rota de rede percorrida até o destino, hop a hop.",
                   "Faz uma requisição HTTP e imprime corpo e status code.",
                   "Abre um socket TCP bruto sem passar por camada de protocolo de aplicação."],
                  "dig é a ferramenta padrão para consultar DNS, substituiu o `nslookup` em "
                  "ambientes profissionais."),
                q("Qual registro DNS aponta um nome para um IP IPv4?",
                  "A", ["AAAA (IPv6).", "CNAME (alias).", "MX (mail)."],
                  "A = IPv4, AAAA = IPv6 (4 vezes maior), CNAME = alias, MX = servidor de e-mail."),
                q("O que indica TTL em respostas DNS?",
                  "Por quanto tempo o resultado pode ficar em cache.",
                  ["A latência da rede medida entre cliente e servidor autoritativo.",
                   "A versão do protocolo DNS usada na consulta e resposta.",
                   "O tamanho em bytes do pacote de resposta enviado pelo servidor."],
                  "TTL alto → menos consultas mas migração lenta. TTL baixo → mais carga mas "
                  "mudanças se propagam rápido."),
                q("Qual ferramenta lista sockets em escuta no Linux moderno?",
                  "ss -tulpn",
                  ["ifconfig, que mostra interface de rede, não socket em escuta.",
                   "route, que mostra tabela de roteamento, não porta aberta.",
                   "ipset, que gerencia conjunto de IP para firewall, não sockets."],
                  "netstat foi substituído por ss em distros modernas. -tulpn lista TCP, UDP, "
                  "listening, processo e numérico."),
                q("Qual IP é o loopback IPv4?",
                  "127.0.0.1", ["192.168.0.1", "10.0.0.1", "0.0.0.0"],
                  "127.0.0.0/8 inteiro é loopback; 0.0.0.0 representa 'todas as interfaces' ao bindar."),
                q("CIDR /24 corresponde a:",
                  "Máscara 255.255.255.0",
                  ["255.0.0.0, equivalente a /8, rede bem maior que /24.",
                   "255.255.0.0, equivalente a /16, ainda maior que /24.",
                   "255.255.255.255, máscara de host único, equivalente a /32."],
                  "Os primeiros 24 bits são rede; restam 8 bits → 256 endereços, sendo 254 usáveis "
                  "(rede + broadcast)."),
                q("UDP é normalmente usado em:",
                  "DNS, vídeo em tempo real e streaming de baixa latência.",
                  ["Transferência confiável de arquivo ponta a ponta, sem perda de pacote no caminho.",
                   "Transação bancária, onde ordem e confirmação de entrega importam muito.",
                   "Conexão SSH interativa, que depende de fluxo ordenado e confiável de bytes."],
                  "UDP é stateless e sem retransmissão, perfeito quando latência > confiabilidade."),
                q("O que `curl -v` mostra além do corpo?",
                  "Cabeçalhos da requisição e da resposta.",
                  ["O status code numérico da resposta HTTP recebida do servidor.",
                   "O corpo da resposta formatado como JSON legível, sem mais detalhe.",
                   "O tempo total gasto na requisição, do início até o fim."],
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
                """<h3>1. Cabeçalho seguro: o 'unsafe at any speed' do bash</h3>
<p>Todo script sério começa com a mesma combinação de três configurações:</p>
<pre><code>#!/usr/bin/env bash
set -euo pipefail
IFS=$'\\n\\t'</code></pre>
<p>Cada flag fecha uma classe específica de bug. O <code>-e</code>
aborta a execução no primeiro comando que retornar erro — sem ele, o
script simplesmente CONTINUA depois de uma falha, o que pode significar
apagar a base de dados errada logo depois de um backup que falhou
silenciosamente. O <code>-u</code> gera erro ao referenciar uma
variável não definida — pega um typo antes que ele vire uma string
vazia dentro de <code>rm -rf $TARGET/*</code>, transformando o comando
em algo bem mais destrutivo do que pretendido. O <code>-o pipefail</code>
faz o status do pipe refletir o PIOR estágio, não o último — sem ele,
<code>backup_db | gzip &gt; out.gz</code> retorna sucesso mesmo que
<code>backup_db</code> tenha falhado completamente, um silêncio
perigoso justamente onde o script mais precisaria alertar. E o
<code>IFS=$'\\n\\t'</code> restringe o word-splitting a quebra de linha
e tab, evitando o bug clássico de nome de arquivo com espaço quebrando
em pedaços inesperados. Para depuração pontual, ativar
<code>set -x</code> temporariamente numa seção específica isola o
problema sem poluir o log inteiro do script:</p>
<pre><code>{ set -x; comando_problematico; } 2&gt;&amp;1 | tee /tmp/debug.log
set +x</code></pre>

<h3>2. Aspas, a primeira regra é citar tudo</h3>
<p>A fonte mais comum de bug em bash é word-splitting e expansão de
glob acontecendo num momento inesperado:</p>
<pre><code># RUIM: arquivo 'meu doc.txt' vira dois argumentos
rm $arquivo

# BOM
rm "$arquivo"

# RUIM: se $files for vazio, vira `for f in` (loop não executa, ok)
#       mas se for um glob solto, expande no momento errado
for f in $files; do echo $f; done

# BOM: array preserva elementos individualmente
files=( '/srv/a 1.txt' '/srv/b.txt' )
for f in "${files[@]}"; do echo "$f"; done</code></pre>
<p>A regra prática é citar TODA variável no momento da expansão, exceto
no raro caso em que word-splitting é exatamente o comportamento
desejado.</p>

<h3>3. Estruturas de controle modernas</h3>
<p><code>[[ ... ]]</code> deveria ser preferido a <code>[ ... ]</code>
sempre que possível — suporta regex nativamente, operadores compostos, e
não carrega as armadilhas clássicas de <code>[ ]</code> com string
vazia não citada:</p>
<pre><code>if [[ -z "$1" ]]; then
  echo 'uso: deploy.sh &lt;ambiente&gt;' &gt;&amp;2
  exit 64    # EX_USAGE
fi

if [[ "$ENV" =~ ^(dev|staging|prod)$ ]]; then
  echo "deploy em $ENV"
fi

case "$ENV" in
  dev|staging)  HOST=internal.example.com ;;
  prod)         HOST=api.example.com ;;
  *)            echo 'ambiente inválido' &gt;&amp;2; exit 64 ;;
esac</code></pre>

<h3>4. Iterando arquivos com nome 'esquisito'</h3>
<p>Existe basicamente uma única forma 100% segura de iterar arquivo por
arquivo sem quebrar em nome com caractere especial: usar separador NUL
de ponta a ponta:</p>
<pre><code># RUIM: quebra com espaço, tab ou newline no nome
for f in $(ls *.log); do
  process "$f"
done

# RUIM ainda: ls não é parseável
find . -name '*.log' | while read f; do process "$f"; done

# BOM: -print0 emite separadores NUL
find . -type f -name '*.log' -print0 | \\
  while IFS= read -r -d '' f; do
    process "$f"
  done

# Alternativa elegante com bash 4+ (mapfile)
mapfile -d '' -t files &lt; &lt;(find . -type f -name '*.log' -print0)
for f in "${files[@]}"; do process "$f"; done</code></pre>
<p>Ambas as versões "RUIM" quebram silenciosamente diante de espaço,
tab ou quebra de linha embutidos no nome do arquivo — o separador NUL é
o único caractere garantido a nunca aparecer num nome de arquivo válido
em sistema POSIX, o que o torna o único delimitador realmente seguro
para esse propósito.</p>

<h3>5. Funções, retorno e erro propagado</h3>
<pre><code>require_env() {
  local var=$1
  if [[ -z "${!var:-}" ]]; then
    echo "FATAL: variável $var não definida" &gt;&amp;2
    return 1
  fi
}

deploy() {
  require_env GITHUB_TOKEN
  require_env DEPLOY_KEY
  # ...
}

deploy || { echo 'deploy falhou' &gt;&amp;2; exit 1; }</code></pre>
<p>Usar <code>local</code> para toda variável dentro de uma função
evita que ela vaze para o escopo global sem querer, um efeito colateral
fácil de esquecer em bash. E <code>${!var}</code> faz indireção —
referencia a variável cujo NOME está guardado dentro de
<code>$var</code>, o que é o que permite <code>require_env</code>
checar dinamicamente qualquer nome de variável passado como
argumento.</p>

<h3>6. Trap para cleanup determinístico</h3>
<pre><code>tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT INT TERM

echo 'baixando…' &gt; "$tmp/log"
curl https://api.example.com/dump &gt; "$tmp/dump.json"
process "$tmp/dump.json"
# o trap cuida da limpeza mesmo se algo falhar</code></pre>
<p>Sem o <code>trap</code>, um <code>exit 1</code> no meio do script ou
um Ctrl+C do usuário deixa lixo acumulando em <code>/tmp</code> — em
script rodando com frequência, isso entope disco silenciosamente ao
longo do tempo, sem nenhum sinal óbvio até o disco realmente encher.</p>

<h3>7. Validação de input, trate como hostil</h3>
<pre><code># Recebido por argumento ou variável de ambiente
name=${1:?uso: ./script.sh &lt;nome&gt;}

# Whitelist é melhor que blacklist
if [[ ! "$name" =~ ^[a-zA-Z0-9_-]{1,32}$ ]]; then
  echo "nome inválido: $name" &gt;&amp;2
  exit 64
fi

# NUNCA: rm -rf /srv/$name (com $name vazio = rm -rf /srv/)
# NUNCA: eval "$name"
# NUNCA: bash -c "echo $name"   ← injeção de comando</code></pre>
<p>A escolha entre whitelist e blacklist não é estilística: uma
whitelist define explicitamente o que é PERMITIDO, então qualquer coisa
fora desse padrão falha por padrão; uma blacklist tenta listar o que é
PROIBIDO, e sempre existe algum caractere ou sequência esquecida que
escapa da lista — a assimetria entre as duas abordagens é o que torna
whitelist estruturalmente mais segura.</p>

<h3>8. Logging com timestamp e níveis</h3>
<pre><code>log() {
  local level=$1; shift
  printf '%s [%s] %s\\n' "$(date -Iseconds)" "$level" "$*" &gt;&amp;2
}

log INFO  'iniciando deploy'
log WARN  'cache vazio, baixando do registry'
log ERROR 'falha ao subir container'</code></pre>
<p>Registrar log no <code>stderr</code> mantém o <code>stdout</code>
livre exclusivamente para a saída ÚTIL do script — a parte que
eventualmente vai ser encadeada com pipe para outro comando. Misturar
log e saída útil no mesmo stream quebra qualquer composição posterior
do script com outra ferramenta via pipe.</p>

<h3>9. Anti-patterns que custam caro</h3>
<table style='border-collapse:collapse'>
<tr><td><code>eval "$input"</code></td>
<td>RCE garantido se input vier de fora.</td></tr>
<tr><td><code>rm -rf $dir/</code></td>
<td>Sem checar <code>$dir</code>, com <code>set -u</code> off, vira
<code>rm -rf /</code>.</td></tr>
<tr><td><code>curl ... | bash</code></td>
<td>Executa código remoto sem verificação. Se o servidor for comprometido,
RCE no seu host.</td></tr>
<tr><td><code>ssh host "$cmd"</code></td>
<td>Sem aspas adicionais e validação, injeção de comando.</td></tr>
<tr><td><code>readlink</code> sem <code>-f</code></td>
<td>Não resolve symlinks aninhados.</td></tr>
<tr><td><code>cat $file | grep …</code></td>
<td>Useless use of cat. Prefira <code>grep … &lt; $file</code>.</td></tr>
</table>

<h3>10. shellcheck, shfmt e quando subir para Python</h3>
<p>O <code>shellcheck</code> pega cerca de 95% dos bugs mais comuns
automaticamente, sem exigir revisão manual linha por linha — integrar
no CI e no editor, falhando o pipeline em qualquer warning, transforma
essa classe inteira de erro em algo pego antes do merge, não depois do
incidente. O <code>shfmt</code> cuida da formatação de forma
equivalente. Bash brilha em script de até aproximadamente 150 linhas —
além desse tamanho, ou quando o script precisa de estrutura de dado
não-trivial, lógica de retry/backoff mais elaborada, concorrência além
de um <code>&amp;</code> simples, ou teste unitário de verdade, a
manutenção em bash puro fica cada vez mais cara — nesse ponto, subir
para Python (com <code>typer</code>) ou Go compensa o tempo investido
na migração.</p>

<h3>11. Caso real: o <code>rm -rf $STEAMROOT/*</code> da Steam</h3>
<p>Em 2015, o launcher da Steam para Linux trazia um script de
desinstalação contendo literalmente
<code>rm -rf "$STEAMROOT/"*</code>. Quando a variável
<code>$STEAMROOT</code> estava vazia — algo que podia acontecer
dependendo de como o script era invocado — o comando virava
efetivamente <code>rm -rf "/"*</code>, apagando todo o conteúdo do
sistema de arquivos acessível pelo usuário, não só os arquivos da
Steam. O bug existiu no script por anos antes de ser descoberto e
reportado publicamente. A correção final foi de uma única linha:
validar explicitamente que <code>$STEAMROOT</code> não está vazio antes
de qualquer operação destrutiva — exatamente o tipo de proteção que
<code>set -u</code> (seção 1) e a validação de input (seção 7)
previnem estruturalmente, em vez de depender de alguém lembrar de
checar manualmente em cada script novo.</p>"""
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
                  ["Ativa modo verboso, imprimindo cada comando antes de executá-lo.",
                   "Define uma variável de ambiente visível para os subprocessos do script.",
                   "Roda o script inteiro num processo separado, em paralelo com o terminal atual."],
                  "Sem -e, um falha intermediária passa despercebida e o script continua "
                  "como se tudo desse certo."),
                q("Qual a forma correta de citar uma variável?",
                  "echo \"$var\"", ["echo $var", "echo '$var'", "echo `var`"],
                  "Aspas duplas evitam word splitting e expansão de glob mantendo a expansão "
                  "da variável."),
                q("O que `pipefail` faz?",
                  "Faz o pipeline falhar se qualquer comando intermediário falhar.",
                  ["Reinicia o pipe inteiro automaticamente após qualquer comando interno travar.",
                   "Ignora e descarta qualquer código de erro vindo de dentro do pipe.",
                   "Faz o pipeline retornar sucesso mesmo quando algo dentro dele falhou de verdade."],
                  "Sem pipefail, `cmd1 | cmd2` retorna o status de cmd2 mesmo que cmd1 tenha "
                  "explodido, fonte recorrente de bugs silenciosos."),
                q("Como capturar a saída de um comando em uma variável?",
                  "result=$(comando)", ["result=`comando`", "result=$comando", "result=>'comando'"],
                  "Backticks aninham mal e são considerados legados; preferir $(...)."),
                q("Qual comando lista todos os scripts shell num diretório recursivamente?",
                  "find . -type f -name '*.sh'",
                  ["ls -la *.sh, que lista só o diretório atual, sem recursão real.",
                   "grep -r '*.sh', que busca esse texto dentro dos arquivos, não pelo nome.",
                   "tree --shell, uma flag que não existe no comando tree padrão."],
                  "ls não recursa por padrão; grep busca conteúdo, não nome. find é a ferramenta correta."),
                q("Por que `eval` com input externo é perigoso?",
                  "Permite execução arbitrária de código se a string vier de fora.",
                  ["Deixa o script mais lento, porque precisa reinterpretar a string a cada execução.",
                   "Não funciona em versões antigas do macOS que ainda usam bash 3.2.",
                   "Gera erro de sintaxe quando a string contém aspas desbalanceadas dentro dela."],
                  "Eval interpreta a string como comando bash, então qualquer coisa do tipo "
                  "`; rm -rf /` no input é executada."),
                q("Como passar argumento posicional em script bash?",
                  "$1, $2, $3...",
                  ["arg1, arg2, uma sintaxe de outras linguagens que bash não reconhece.",
                   "&1, &2, sintaxe usada para redirecionar descritor de arquivo, não argumento.",
                   "%1, %2, sintaxe do PowerShell/batch do Windows, não de bash."],
                  "$@ tem todos os argumentos; $# o número deles. Cite com aspas: \"$@\"."),
                q("Qual ferramenta detecta bugs comuns em scripts?",
                  "shellcheck",
                  ["pylint, linter de Python, não entende sintaxe de shell.",
                   "eslint, linter de JavaScript/TypeScript, não de shell.",
                   "rubocop, linter de Ruby, não de shell."],
                  "shellcheck é o linter de fato para bash/sh, integra com a maioria das IDEs."),
                q("`[[ -z \"$x\" ]]` é verdadeiro quando:",
                  "x está vazio ou não definida.",
                  ["x é igual a 0, um teste numérico diferente (-eq), não de string.",
                   "x aponta para um arquivo existente, o que -f testaria, não -z.",
                   "x aponta para um diretório existente, o que -d testaria, não -z."],
                  "-z testa string vazia. -n é o oposto. Use sempre as aspas para evitar erro de sintaxe."),
                q("Qual o jeito recomendado de iterar arquivos com espaços no nome?",
                  "find ... -print0 | xargs -0",
                  ["for f in $(ls), que quebra em espaço e não lida bem com nome esquisito.",
                   "ls | while read f, que também quebra com espaço no meio do nome.",
                   "echo *, que expande via glob do shell, sem separar nomes com espaço corretamente."],
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
                  ["/etc/passwd, onde ficam usuário e shell, não chave SSH.",
                   "~/.bashrc, script de configuração do shell, não guarda chave.",
                   "/root/keys.pub, um caminho que o OpenSSH não reconhece por padrão."],
                  "Cada usuário do servidor mantém suas chaves autorizadas no próprio home."),
                q("Qual diretiva no `sshd_config` desabilita login com senha?",
                  "PasswordAuthentication no",
                  ["DisablePassword on, uma diretiva que não existe no sshd_config.",
                   "AllowPassword false, também inexistente; a diretiva certa é outra.",
                   "DenyPassword yes, nome plausível mas não reconhecido pelo sshd."],
                  "Após mudar, é preciso recarregar o sshd (`systemctl reload sshd`)."),
                q("O que `ssh-agent` resolve?",
                  "Mantém a chave privada decifrada em memória durante a sessão.",
                  ["Substitui completamente o pacote openssh-server no sistema.",
                   "Sincroniza automaticamente as chaves entre as máquinas do mesmo usuário.",
                   "Gera uma chave nova a cada vez que uma sessão SSH é iniciada pelo usuário."],
                  "Sem agent, você teria que digitar a passphrase a cada conexão. Com forwarding, "
                  "use com cuidado: agent forwarding mal configurado vaza a identidade."),
                q("Qual permissão é exigida pelo OpenSSH para `~/.ssh/authorized_keys`?",
                  "600 (rw apenas para o dono).",
                  ["777, que dá leitura e escrita para qualquer usuário do sistema.",
                   "644, que ainda permite outros usuários lerem o conteúdo da chave.",
                   "400 com dono root, inacessível até para o próprio usuário do serviço."],
                  "O sshd recusa silenciosamente a chave se o arquivo for legível por outros."),
                q("Como copiar a chave pública para o servidor?",
                  "ssh-copy-id user@host",
                  ["scp -p chave.pub, que copia o arquivo mas não ajusta a permissão.",
                   "rsync key, um comando incompleto que não existe como está escrito.",
                   "ssh --send-key, uma flag que não existe no cliente OpenSSH padrão."],
                  "ssh-copy-id já faz append em authorized_keys e ajusta permissões."),
                q("Qual variável de ambiente o ssh-agent define?",
                  "SSH_AUTH_SOCK",
                  ["SSH_KEY, uma variável inventada; o OpenSSH usa outro nome para isso.",
                   "SSH_PASS, usada por outra ferramenta (sshpass), não pelo ssh-agent.",
                   "SSH_TOKEN, um nome que soa plausível mas não é usado pelo protocolo."],
                  "É o socket Unix por onde o cliente fala com o agent."),
                q("O que é uma chave de host em SSH?",
                  "Chave que identifica o servidor para evitar MITM.",
                  ["Chave temporária gerada para um usuário convidado sem privilégio real.",
                   "Chave dedicada só a criptografar o conteúdo dos pacotes trafegados.",
                   "Chave usada exclusivamente pela conta root para tarefa administrativa."],
                  "Na primeira conexão, você aceita a chave; depois ela vai pra known_hosts. "
                  "Se mudar inesperadamente, é sinal de MITM (ou rebuild legítimo)."),
                q("Por que evitar PermitRootLogin yes?",
                  "Aumenta a superfície de ataque dando acesso direto a um usuário onipotente.",
                  ["Bloqueia completamente o serviço sshd assim que a opção é ativada.",
                   "Reduz a performance geral do servidor por causa da checagem extra de root.",
                   "Deixa de funcionar corretamente quando combinado com uma chave Ed25519 mais recente."],
                  "Use um usuário comum com sudo; tenha rastreabilidade individual no audit log."),
                q("Qual a vantagem de SSH com certificados?",
                  "Eliminar autorização chave-a-chave em cada servidor; rotação centralizada.",
                  ["Continua funcionando mesmo com a rede completamente indisponível no momento.",
                   "Permite senha mais curta do que a exigida pela política atual da empresa.",
                   "Elimina a necessidade de instalar e manter o próprio daemon sshd."],
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
                """<h3>1. Por que PoLP é fundamental</h3>
<p>A forma mais útil de pensar em PoLP é como controle de
<strong>blast radius</strong>: quanto se compromete no momento em que
uma identidade específica vaza. Se uma aplicação web carrega credencial
<code>AdministratorAccess</code> na AWS e é comprometida, o atacante
controla a conta inteira — derruba banco, exfiltra bucket S3, sobe
instância própria para minerar criptomoeda com o cartão da empresa. Se
a mesma aplicação tivesse apenas <code>s3:GetObject</code> num bucket
específico, o vazamento cabe numa única linha de relatório de
incidente, não numa manchete. PoLP não IMPEDE o comprometimento em si —
é defesa em profundidade posta em prática, limitando a CONSEQUÊNCIA de
algo que eventualmente vai acontecer de qualquer forma. É exatamente o
que separa um incidente constrangedor de uma crise de imagem completa.</p>

<h3>2. PoLP no host Linux: usuários dedicados por serviço</h3>
<p>Cada serviço — nginx, postgres, a própria aplicação — deveria ter
seu usuário de sistema próprio, nunca compartilhado:</p>
<pre><code>useradd --system --shell /usr/sbin/nologin --home-dir /var/lib/app app
chown -R app:app /opt/app /var/lib/app /var/log/app</code></pre>
<p>Isso traz quatro vantagens concretas: o comprometimento de uma
aplicação não dá acesso automático a nenhum outro serviço rodando na
mesma máquina; a permissão fica granular o suficiente para que a
aplicação nem consiga LER <code>/etc/postgres</code>, por exemplo;
auditoria por usuário fica trivial (<code>journalctl
_UID=$(id -u app)</code> isola exatamente o que aquele processo
fez); e limite de recurso (ulimit, cgroup) pode ser aplicado por
usuário individualmente, sem afetar os demais serviços da mesma
máquina.</p>

<h3>3. systemd hardening: a camada que muita gente ignora</h3>
<p>Em <code>/etc/systemd/system/app.service</code>:</p>
<pre><code>[Service]
ExecStart=/opt/app/bin/server
User=app
Group=app

# Identidade
NoNewPrivileges=true       # impede setuid/setcap em descendentes

# Filesystem
ProtectSystem=strict       # tudo readonly exceto paths permitidos
ProtectHome=true           # /home, /root, /run/user invisíveis
PrivateTmp=true            # /tmp isolado por instância
ReadWritePaths=/var/lib/app /var/log/app

# Capabilities
CapabilityBoundingSet=     # vazio = abre mão de tudo
AmbientCapabilities=

# Syscalls (via seccomp-bpf)
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM

# Rede
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
PrivateNetwork=false       # true = sem acesso de rede algum

# Outros
ProtectKernelModules=true
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictNamespaces=true
LockPersonality=true
MemoryDenyWriteExecute=true</code></pre>
<p>Cada uma dessas diretivas fecha um vetor de escalada específico —
<code>NoNewPrivileges</code>, por exemplo, impede que um processo
comprometido ganhe MAIS privilégio do que já tinha via um binário
setuid encontrado no sistema. Para saber exatamente onde uma unit já
está, o próprio systemd oferece um auditor embutido:</p>
<pre><code>systemd-analyze security app.service</code></pre>
<p>Ele devolve uma nota de 0 a 10 com sugestão concreta do que ainda
falta endurecer — quanto MENOR a nota, mais seguro o serviço já está
configurado.</p>

<h3>4. sudo, mas com critério</h3>
<p>A entrada <code>ALL=(ALL:ALL) ALL</code> é o atalho mais comum e
também o pior possível — concede exatamente o oposto do que PoLP
pede. Em <code>/etc/sudoers.d/deploy</code>, a alternativa granular
concede apenas o comando específico necessário:</p>
<pre><code># Usuário deploy só pode reiniciar o nginx, sem senha
deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart nginx
deploy ALL=(root) NOPASSWD: /usr/bin/systemctl reload nginx

# Negar shell escapes
Defaults:deploy !requiretty
Defaults:deploy log_year, logfile=/var/log/sudo-deploy.log</code></pre>
<p>Editar sempre com <code>visudo -f /etc/sudoers.d/arquivo</code> é
uma proteção estrutural própria: o comando VALIDA a sintaxe antes de
salvar — sem essa validação, um typo simples pode deixar o sistema
inteiro sem ninguém conseguindo usar sudo até alguém corrigir via
acesso físico ou console de emergência.</p>

<h3>5. PoLP em containers Docker</h3>
<pre><code># Dockerfile
FROM python:3.12-slim
RUN useradd --uid 10001 --system --no-create-home app
WORKDIR /app
COPY --chown=app:app . .
RUN pip install --no-cache-dir -r requirements.txt
USER app                          # nunca rode como root
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.wsgi"]</code></pre>
<p>No momento de rodar o container, ainda há espaço para ir além do
que o Dockerfile já garante:</p>
<pre><code>docker run --rm \\
  --user 10001:10001 \\
  --read-only \\
  --tmpfs /tmp \\
  --cap-drop=ALL \\
  --cap-add=NET_BIND_SERVICE \\
  --security-opt=no-new-privileges \\
  --pids-limit 200 \\
  -p 8000:8000 myapp:1.0</code></pre>
<p>O <code>--cap-drop=ALL</code> combinado com um único
<code>--cap-add</code> específico (aqui, apenas
<code>NET_BIND_SERVICE</code>, necessário só para bindar em porta
abaixo de 1024) ilustra o próprio PoLP em ação: em vez de conceder o
conjunto completo de capability do kernel, concede exatamente a única
que a aplicação de fato precisa.</p>

<h3>6. PoLP em Kubernetes (securityContext)</h3>
<pre><code>apiVersion: apps/v1
kind: Deployment
metadata: { name: app }
spec:
  template:
    spec:
      automountServiceAccountToken: false   # se a app não chama K8s API
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        fsGroup: 10001
        seccompProfile: { type: RuntimeDefault }
      containers:
      - name: app
        image: myapp:1.0
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities: { drop: ["ALL"] }</code></pre>
<p>Os Pod Security Standards, no modo <code>restricted</code>, aplicam
esse padrão inteiro FORÇADAMENTE em todo deploy dentro do namespace, em
vez de depender de cada time lembrar de configurar isso manualmente:</p>
<pre><code>kubectl label ns app pod-security.kubernetes.io/enforce=restricted</code></pre>

<h3>7. PoLP em Cloud (IAM)</h3>
<p>Cinco princípios sustentam PoLP na camada de nuvem. Preferir role a
chave estática — via workload identity (IRSA na AWS, Workload Identity
no GKE, Managed Identity no AKS) — elimina o problema de uma
credencial de longa duração vazando permanentemente. Policy granular
concede <code>s3:GetObject</code> num
<code>arn:aws:s3:::bucket-x/*</code> específico, nunca
<code>s3:*</code> em <code>*</code> por conveniência. Permission
Boundaries e SCPs funcionam como guard-rail estrutural que nem o
administrador de uma sub-conta consegue exceder, mesmo com a melhor das
intenções. Condicionais (<code>aws:SourceVpc</code>,
<code>aws:MultiFactorAuthPresent</code>,
<code>aws:RequestedRegion</code>) restringem QUANDO e DE ONDE uma
permissão vale, não só O QUE ela permite. E tempo limitado — via STS
AssumeRole com TTL curto — garante que mesmo uma credencial concedida
corretamente expire sozinha, reduzindo a janela de exploração em caso
de vazamento:</p>
<pre><code>// IAM policy mínima
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::reports-prod/*",
      "Condition": {
        "StringEquals": {"aws:SourceVpc": "vpc-abc"}
      }
    }
  ]
}</code></pre>

<h3>8. Privilege creep, o inimigo invisível</h3>
<p>Sem auditoria periódica, o padrão natural é todo mundo só
ADICIONAR permissão nova, e ninguém nunca remover a antiga que deixou
de ser necessária. Em dois anos, uma role IAM que começou com um único
<code>s3:GetObject</code> num bucket específico acumula 47 permissões
diferentes, e ninguém mais consegue dizer com certeza quais delas ainda
são realmente usadas na prática. Quatro ferramentas resolvem essa
opacidade: o AWS IAM Access Analyzer gera relatório do que cada
principal REALMENTE usou nos últimos 90 dias, revelando o que pode ser
podado com segurança; o Cloudsplaining (originalmente da Salesforce) é
um scanner que avalia risco diretamente na policy declarada; o
Steampipe permite rodar SQL direto sobre o estado real da nuvem — uma
consulta como <code>select * from aws_iam_role where
assume_role_policy like '%*%'</code> encontra role perigosamente aberta
em segundos; e o cloudquery mantém um catálogo continuamente atualizado
para consulta recorrente.</p>

<h3>9. Caso real: Capital One 2019</h3>
<p>O atacante explorou um WAF mal configurado, permitindo SSRF que
extraiu credencial IAM temporária via
<code>169.254.169.254</code> — o serviço de metadados da própria AWS.
Essa credencial carregava <code>s3:ListAllMyBuckets</code> e
<code>s3:GetObject</code> liberado em TODOS os buckets da empresa, uma
decisão justificada internamente como "simplicidade" na hora de
configurar. O resultado foi 100 milhões de registro de cliente
vazado, uma multa de US$ 80 milhões, e a demissão da CISO responsável.
Se a role tivesse acesso restrito apenas ao bucket específico que o
WAF realmente precisava tocar, o vazamento teria ficado numa fração
mínima do que de fato aconteceu — o incidente inteiro é, no fundo, um
caso de PoLP violado desde o desenho original da permissão.</p>

<h3>10. Anti-patterns</h3>
<ul>
<li><strong><code>chmod 777</code> "porque tava dando erro"</strong>:
resolve o sintoma imediato abrindo uma porta permanente que qualquer
usuário do sistema pode explorar depois.</li>
<li><strong><code>kubectl create clusterrolebinding app-admin
--clusterrole=cluster-admin</code></strong>: concede controle total
sobre o cluster inteiro para resolver um problema que provavelmente
precisava de uma fração disso.</li>
<li><strong>Aplicação rodando como root no container "porque a imagem
oficial é assim"</strong>: aceita o default sem questionar se ele
atende ao caso de uso real (seção 5).</li>
<li><strong>IAM role <code>*</code> em <code>*</code> "depois eu
restrinjo"</strong>: o "depois" quase nunca chega, e o acesso amplo
vira o estado permanente de fato.</li>
<li><strong>Compartilhar credencial de service account entre
humanos</strong>: elimina toda rastreabilidade de quem fez o quê,
exatamente o oposto do que auditoria por identidade (seção 2)
propõe.</li>
<li><strong>Acesso permanente em vez de just-in-time</strong>: mantém
privilégio elevado ativo o tempo todo, quando ele só é necessário por
uma janela específica de tempo.</li>
</ul>
<p>Para cada um desses padrões, existe uma alternativa segura que
custa minutos a configurar e potencialmente evita horas — ou dias — de
resposta a incidente depois.</p>"""
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
                  ["Porque o root consome mais recurso de CPU e memória do que outro usuário.",
                   "Porque o protocolo HTTPS exige explicitamente que o processo não seja root.",
                   "Porque o processo root reinicia o sistema inteiro assim que qualquer serviço trava."],
                  "Cada vulnerabilidade (heartbleed, log4shell, etc.) num serviço root vira "
                  "comprometimento total da máquina."),
                q("Qual arquivo controla regras de `sudo`?",
                  "/etc/sudoers (e /etc/sudoers.d/)",
                  ["/etc/passwd, onde ficam usuário, UID, home e shell, não regra de sudo.",
                   "/root/.bashrc, script pessoal de shell da conta root, não regra de sudo.",
                   "/var/log/sudo, um caminho que o sudo não usa por padrão em distro alguma."],
                  "Edite com `visudo` ou drops em /etc/sudoers.d/, que evita corromper o arquivo principal."),
                q("O que fazem as Linux capabilities?",
                  "Decompõem privilégios de root em grãos menores (ex.: NET_BIND_SERVICE).",
                  ["Aceleram a execução de syscall trocando o escalonador padrão do kernel.",
                   "Implementam cota de uso de disco por usuário ou grupo do sistema.",
                   "Substituem regra de firewall por uma verificação feita dentro do próprio processo."],
                  "Em vez de root inteiro, dê só CAP_NET_BIND_SERVICE para um binário web bindar a 80/443."),
                q("Em Kubernetes, qual campo do PodSpec exige que o container rode como não-root?",
                  "securityContext.runAsNonRoot: true",
                  ["spec.privileged: false, que restringe capability, não identidade do usuário.",
                   "metadata.root: false, um campo que não existe no schema do Kubernetes.",
                   "spec.uid: 0, que nem é um campo válido dentro da especificação de Pod."],
                  "Combine com runAsUser específico e a imagem precisa estar pronta para isso."),
                q("Qual prática viola PoLP?",
                  "Dar 'AdministratorAccess' a uma role de aplicação.",
                  ["Aplicar service account dedicada com permissão mínima para cada workload.",
                   "Rotacionar credencial periodicamente conforme a política de segurança da equipe.",
                   "Usar policy do IAM com escopo restrito a um recurso e ação específicos."],
                  "Aplicação não precisa de admin. PoLP é dar exatamente o que ela usa."),
                q("`chmod 777 /opt/app` é problemático porque:",
                  "Qualquer usuário do sistema pode escrever, ler e executar, escalada trivial.",
                  ["Apaga o conteúdo do arquivo assim que o comando chmod termina de rodar.",
                   "Não funciona em sistema de arquivo ext4 mais antigo, mas funciona em outros.",
                   "É mais lento que ajustar permissão via ACL específica para cada usuário."],
                  "Atacante com qualquer usuário do sistema injeta payload no app legítimo."),
                q("O que é uma 'identity-based policy' em IAM?",
                  "Regras anexadas a um usuário/role definindo o que pode fazer.",
                  ["Senha rotativa gerada automaticamente a cada login bem-sucedido do usuário.",
                   "Token de DNS usado para provar propriedade de um domínio específico.",
                   "Backup criptografado guardado numa conta separada da conta de produção."],
                  "Resource-based policies, em contraste, ficam no recurso (ex.: bucket policy)."),
                q("Qual ferramenta confina syscalls de processos no Linux?",
                  "seccomp",
                  ["iptables", "cron", "udev"],
                  "seccomp-bpf permite whitelistar quais syscalls um processo pode executar, "
                  "Docker e K8s usam isso."),
                q("Quando uso 'sudo -i', o que acontece?",
                  "Inicio um shell de login como root.",
                  ["Atualizo o sistema operacional inteiro sem pedir confirmação adicional.",
                   "Rodo o próximo comando com um atraso extra, sem trocar de usuário atual.",
                   "Confirmo que minha conta tem permissão de usar sudo, sem executar comando algum depois disso."],
                  "-i carrega o ambiente de login do root; -s mantém o ambiente atual; "
                  "sem flags, executa um comando único."),
                q("A rotação periódica de credenciais ajuda PoLP porque:",
                  "Reduz a janela de exploração caso uma credencial vaze.",
                  ["Aumenta a entropia do gerador de senha usado para criar a credencial nova.",
                   "Faz log detalhado do uso completo da credencial nas últimas semanas de operação.",
                   "Substitui completamente a necessidade de configurar MFA na conta do usuário."],
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
                """<h3>1. O subsystem netfilter</h3>
<p>O kernel Linux implementa um framework de filtro de pacotes chamado
netfilter, com hook em cinco pontos distintos ao longo do caminho de
um pacote pela pilha de rede. O <code>PRE-ROUTING</code> atua antes
mesmo de decidir o destino final, sendo onde NAT de entrada acontece. O
<code>INPUT</code> filtra pacote destinado ao próprio host. O
<code>FORWARD</code> filtra pacote apenas roteado através da máquina —
o cenário de um gateway ou router. O <code>OUTPUT</code> filtra pacote
saindo do próprio host. E o <code>POST-ROUTING</code> atua depois de já
roteado, onde NAT de saída acontece. Um detalhe importante para quem
compara ferramentas: as interfaces de usuário — iptables, nftables, ufw
— só MONTAM regra sobre esses hooks já existentes, elas não trocam o
motor por baixo. Trocar de <code>iptables</code> para
<code>nftables</code> muda a sintaxe, não o comportamento fundamental
do kernel.</p>

<h3>2. iptables vs nftables vs ufw</h3>
<p>Quatro ferramentas cobrem o mesmo espaço em momentos históricos
diferentes. O <strong>iptables</strong> (1998) é o clássico, com
sintaxe verbosa e tabela SEPARADA para IPv6 (via
<code>ip6tables</code>), ARP e ebtables — esquecer de replicar uma
regra em <code>ip6tables</code> é uma fonte histórica de vazamento
(seção 9). O <strong>nftables</strong> (2014) veio como substituto
unificado, com sintaxe nova, performance melhor, e IPv4 e IPv6
convivendo na mesma árvore de regra — em distribuição recente (Debian
11+, RHEL 9, Ubuntu 22.04+), o próprio comando <code>iptables</code>
virou apenas um shim que traduz internamente para nftables. O
<strong>UFW</strong> (Uncomplicated Firewall) é um wrapper amigável
para quem está começando — <code>ufw allow ssh</code> resolve sem
precisar entender hook nem chain. E o <strong>firewalld</strong>
(comum em RHEL/Fedora) segue um modelo diferente, organizado em torno
de "zonas" em vez de regra explícita direta.</p>

<h3>3. UFW na prática</h3>
<pre><code># Estado / status
ufw status verbose
ufw status numbered

# Política default (default-deny inbound é o caminho)
ufw default deny incoming
ufw default allow outgoing

# Regras
ufw allow ssh                            # equivale a 22/tcp
ufw allow 80,443/tcp                     # web
ufw allow from 10.0.1.0/24 to any port 5432  # postgres só da subnet
ufw limit ssh                            # rate limit (anti brute force)

# Aplicar
ufw enable

# Remover regra
ufw status numbered
ufw delete 3</code></pre>
<p>O <code>ufw limit</code> bloqueia automaticamente IP com mais de 6
tentativas de conexão em 30 segundos — uma proteção direta contra
brute-force em SSH, sem precisar de ferramenta externa. Para uma
resposta ainda mais agressiva, combinar com <code>fail2ban</code>
adiciona banimento por período mais longo e cobrindo mais portas ao
mesmo tempo.</p>

<h3>4. nftables raw, para quando UFW não basta</h3>
<pre><code># /etc/nftables.conf
table inet filter {
  chain input {
    type filter hook input priority 0; policy drop;
    
    iif lo accept
    ct state established,related accept
    ct state invalid drop
    
    icmp type echo-request limit rate 5/second accept
    icmpv6 type { echo-request, nd-neighbor-solicit, nd-router-advert, \\
                  nd-neighbor-advert } accept
    
    tcp dport 22 limit rate 10/minute accept    # ssh com rate limit
    tcp dport { 80, 443 } accept                 # web
    
    log prefix "nft drop: " level info limit rate 5/minute
  }
  chain forward { type filter hook forward priority 0; policy drop; }
  chain output  { type filter hook output  priority 0; policy accept; }
}</code></pre>
<p>Aplicar essa configuração e garantir que ela persista no boot é um
único comando: <code>nft -f /etc/nftables.conf &amp;&amp; systemctl
enable nftables</code>.</p>

<h3>5. DROP vs REJECT vs ACCEPT</h3>
<table>
<tr><td><code>ACCEPT</code></td><td>passa</td></tr>
<tr><td><code>DROP</code></td><td>descarta silenciosamente. Atacante vê
timeout, mais difícil de mapear. Padrão em internet pública.</td></tr>
<tr><td><code>REJECT</code></td><td>responde com ICMP
<em>port-unreachable</em> ou TCP RST. 'Mais educado'; cliente legítimo
descobre o erro mais rápido. Bom em rede interna.</td></tr>
</table>
<p>A escolha entre DROP e REJECT não é neutra: DROP faz o atacante
gastar tempo esperando um timeout que nunca chega, dificultando mapear
quais portas realmente existem por trás — o padrão correto para
qualquer interface exposta à internet pública. REJECT, ao contrário,
informa imediatamente que a porta está fechada, o que é útil em rede
interna onde não há adversário tentando mapear o ambiente, só um
colega tentando debugar mais rápido por que algo não conecta. E a linha
<code>ct state established,related accept</code> é o que permite a
RESPOSTA de uma conexão que o próprio host iniciou voltar livremente,
sem precisar de uma regra explícita separada para cada tipo de tráfego
de retorno.</p>

<h3>6. Cuidados em produção: não se trave fora!</h3>
<p>Antes de aplicar uma regra restritiva via SSH remoto, um plano de
reversão automática evita o cenário clássico de perder acesso ao
próprio servidor:</p>
<pre><code># Plano B: reverte automaticamente em 5 min se você não desativar
echo 'iptables-restore &lt; /tmp/rules.backup' | at now +5 minutes

iptables-save &gt; /tmp/rules.backup
# ... aplica novas regras ...
# se você confirma que continua funcionando:
atrm $(atq | tail -1 | awk '{print $1}')</code></pre>
<p>Para nftables, o mesmo princípio se aplica salvando o estado atual
com <code>nft list ruleset &gt; /tmp/before.nft</code> antes de
qualquer mudança, com <code>nft -f /tmp/before.nft</code> pronto para
reverter caso algo saia errado. E persistir a regra é igualmente
crítico: distribuições costumam oferecer
<code>netfilter-persistent</code>, <code>iptables-persistent</code> ou
o próprio <code>nftables.service</code> para carregar a configuração
novamente no boot — sem isso, um simples reboot zera tudo e o host
volta a ficar completamente exposto sem ninguém perceber
imediatamente.</p>

<h3>7. Limites de firewall L3/L4</h3>
<p>Um firewall operando por porta e protocolo simplesmente não enxerga
três categorias inteiras de ataque: o conteúdo de uma conexão HTTPS,
que chega criptografado; a lógica da própria aplicação, onde SQL
injection, XSS e RCE acontecem inteiramente dentro do payload
permitido; e o comportamento de um usuário aparentemente legítimo, como
credential stuffing distribuído entre muitos IPs rotativos diferentes,
cada um individualmente abaixo de qualquer limite de taxa configurado.
Para cobrir essa lacuna existe a camada 7: um WAF (ModSecurity,
Cloudflare, AWS WAF, Azure Front Door) inspeciona o conteúdo real da
requisição; um API Gateway (Kong, Tyk, AWS API Gateway) aplica rate
limit por chave de API e validação de schema; e um service mesh
(Istio, Linkerd) garante autenticação mTLS genuína entre serviços
internos.</p>

<h3>8. Firewall em cloud: Security Groups e NACLs</h3>
<p>Na AWS (e equivalentes), o Security Group é STATEFUL e anexado
diretamente a uma ENI ou instância, com default deny no inbound e
allow no outbound — e uma regra de saída pode referenciar outro
Security Group diretamente como destino, permitindo composição de
arquitetura inteira via referência (detalhado na aula de rede em
nuvem). O Network ACL é STATELESS e opera a nível de subnet, com regra
numerada avaliada em ordem sequencial — útil especificamente para
bloquear um IP malicioso amplo sem precisar tocar em nenhum Security
Group individual. O padrão prático de uso divide o papel de cada um:
Security Group como firewall de aplicação ("a aplicação fala com o
Postgres, mais nada"), e NACL como guard-rail estrutural por subnet
("a subnet privada não recebe tráfego de internet, ponto final").</p>

<h3>9. Caso real: o ipv6-bypass</h3>
<p>Por anos, administradores configuravam <code>iptables</code> com
cuidado e simplesmente esqueciam de replicar a mesma configuração em
<code>ip6tables</code>, deixando o tráfego IPv6 completamente aberto
mesmo com o IPv4 bem protegido. Atacante automatizado descobria o
endereço IPv6 do host — frequentemente exposto pelo próprio DNS — e
entrava direto por essa porta lateral esquecida. Em 2014, esse padrão
ficou particularmente conhecido quando o próprio <code>kubelet</code>
do Kubernetes se expunha via IPv6 por configuração default sem que
ninguém tivesse pensado nisso explicitamente. A lição prática direta:
usar <code>nftables</code> com a tabela <code>inet</code> — que filtra
IPv4 e IPv6 na mesma árvore de regra simultaneamente — elimina
estruturalmente esse tipo de esquecimento, em vez de depender de
lembrar manualmente de duplicar cada regra nas duas stacks
separadas.</p>

<h3>10. Checklist de hardening</h3>
<ol>
<li>Default-deny no inbound; default-allow no outbound, com revisão
periódica mesmo assim.</li>
<li>Apenas as portas estritamente necessárias abertas, nada "por via
das dúvidas".</li>
<li>SSH com rate-limit (<code>ufw limit</code> combinado com
fail2ban).</li>
<li>ICMP echo aceito mas com rate-limit aplicado, evitando abuso
como vetor de flood.</li>
<li>Conntrack aceitando established/related, e descartando
explicitamente estado invalid.</li>
<li>Log em todo DROP inicial, mas amostrado (5 por minuto, por
exemplo) para não encher o disco com ruído repetitivo.</li>
<li>Persistência configurada, garantindo que a regra sobrevive a um
reboot (seção 6).</li>
<li>IPv6 filtrado com o mesmo rigor do IPv4 (seção 9).</li>
<li>Plano de reversão pronto antes de qualquer mudança remota via
SSH.</li>
<li>Auditoria periódica perguntando, para cada porta ainda aberta, "o
que exatamente ela serve hoje?".</li>
</ol>"""
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
                  ["default allow, que libera qualquer conexão sem restrição.",
                   "ignorar tudo, deixando o kernel decidir sem regra aplicada de propósito.",
                   "drop saída e permitir entrada, o inverso do padrão recomendado."],
                  "Default-deny inverte o padrão: nada entra a menos que você diga sim."),
                q("Qual chain do iptables filtra pacotes destinados ao próprio host?",
                  "INPUT", ["OUTPUT", "FORWARD", "POSTROUTING"],
                  "OUTPUT = pacotes saídos pelo host. FORWARD = pacotes roteados pela máquina (gateway)."),
                q("Diferença chave entre DROP e REJECT?",
                  "DROP descarta silenciosamente; REJECT envia ICMP/RST informando bloqueio.",
                  ["DROP é mais lento que REJECT porque processa mais campos de cada pacote recebido.",
                   "REJECT exige NAT configurado antes de funcionar corretamente na rede local.",
                   "DROP funciona só em pacote UDP, não em conexão TCP já estabelecida antes."],
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
                  ["O uso de banda consumido por cada interface de rede monitorada.",
                   "Ataques recentes registrados no log do sistema de detecção.",
                   "Tráfego em tempo real passando por cada porta aberta agora."],
                  "Permite remover por índice: `ufw delete 3`."),
                q("Qual porta 53 é tipicamente liberada para?",
                  "DNS", ["HTTP", "RDP", "SMB"],
                  "DNS usa 53 em UDP (queries normais) e TCP (zone transfer e mensagens grandes)."),
                q("`ufw deny from 10.0.0.5` faz o quê?",
                  "Bloqueia conexões originadas desse IP.",
                  ["Renomeia a interface de rede associada àquele endereço específico.",
                   "Apaga a rota de rede configurada para alcançar esse IP específico.",
                   "Permite conexão vinda exclusivamente desse IP, bloqueando os demais."],
                  "Útil para banir IPs maliciosos rapidamente."),
                q("Por que abrir 'all' (qualquer porta) em produção é ruim?",
                  "Aumenta drasticamente a superfície de ataque.",
                  ["Quebra a resolução de DNS para qualquer requisição feita depois disso.",
                   "Reduz a performance do roteador por processar mais regra por pacote.",
                   "Não é uma configuração permitida pelo kernel na maioria das distribuições."],
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
                """<h3>1. Por que ainda existe TLS termination na borda</h3>
<p>Mesmo num ambiente com mTLS pleno dentro do mesh, o proxy de borda
continua justificado por cinco razões concretas: certificado público
(Let's Encrypt) gerenciado num único lugar central, em vez de espalhado
por dezenas de microserviços; HTTP/2 e HTTP/3 (QUIC) disponíveis por
padrão sem que cada serviço individual precise implementar isso
sozinho; compressão (gzip, brotli) e cache de resposta aplicados numa
única camada; um WAF (ModSecurity) inspecionando tudo que entra antes
mesmo de chegar na aplicação; e roteamento por path ou host com lógica
potencialmente complexa, centralizada num só lugar em vez de
duplicada. O padrão clássico é o Nginx escutando em 80/443, e fazendo
<code>proxy_pass http://127.0.0.1:8000</code> para gunicorn, uvicorn ou
daphne — ou, quando disponível, um socket Unix diretamente.</p>

<h3>2. Configuração mínima viável</h3>
<pre><code># /etc/nginx/sites-available/api.example.com
upstream api_backend {
  server 127.0.0.1:8000 fail_timeout=5s;
  keepalive 32;
}

server {
  listen 80;
  listen [::]:80;
  server_name api.example.com;
  return 301 https://$host$request_uri;        # força HTTPS
}

server {
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  server_name api.example.com;
  
  ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
  
  # Mozilla 'modern' (apenas TLS 1.3) ou 'intermediate' (1.2+1.3)
  ssl_protocols TLSv1.3;
  ssl_prefer_server_ciphers off;
  ssl_ciphers TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384;
  ssl_session_timeout 1d;
  ssl_session_cache shared:SSL:10m;
  ssl_session_tickets off;
  ssl_stapling on;
  ssl_stapling_verify on;
  
  # Headers de segurança
  add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
  add_header X-Frame-Options DENY always;
  add_header X-Content-Type-Options nosniff always;
  add_header Referrer-Policy strict-origin-when-cross-origin always;
  add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
  add_header Content-Security-Policy "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'" always;
  
  # Esconde versão do Nginx
  server_tokens off;
  
  # Tamanho máximo de body
  client_max_body_size 5M;
  
  # Compressão
  gzip on;
  gzip_types text/plain text/css application/json application/javascript;
  
  # Rate limit em /login
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  
  location = /login {
    limit_req zone=login burst=10 nodelay;
    proxy_pass http://api_backend;
  }
  
  location / {
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_pass http://api_backend;
    proxy_read_timeout 60s;
  }
}</code></pre>

<h3>3. Headers de segurança detalhados</h3>
<table>
<tr><td><code>Strict-Transport-Security</code></td>
<td>Browser vai usar HTTPS por X segundos sem nem tentar HTTP.</td></tr>
<tr><td><code>X-Frame-Options DENY</code></td>
<td>Mata clickjacking via &lt;iframe&gt;.</td></tr>
<tr><td><code>X-Content-Type-Options nosniff</code></td>
<td>Browser não 'adivinha' MIME, para upload de avatar virar HTML.</td></tr>
<tr><td><code>Content-Security-Policy</code></td>
<td>A defesa contra XSS mais poderosa.
Define quais origens podem rodar JS, carregar imagem, etc.</td></tr>
<tr><td><code>Referrer-Policy</code></td>
<td>Controla quanto da URL atual é enviado em <em>navegação</em>.</td></tr>
<tr><td><code>Permissions-Policy</code></td>
<td>Câmera, microfone, geolocalização, só com opt-in explícito.</td></tr>
</table>
<p>Cada um desses headers fecha um vetor de ataque específico que o
navegador, sozinho, deixaria aberto por default — o
<code>X-Frame-Options</code>, por exemplo, existe porque sem ele
qualquer site pode embutir sua página inteira num iframe invisível e
capturar clique do usuário sem que ele perceba. Auditar tudo isso de
uma vez via securityheaders.com e SSL Labs revela rapidamente qual
header está faltando antes de alguém precisar descobrir isso num
incidente.</p>

<h3>4. CSP, o headache que vale o esforço</h3>
<p>Aplicar Content-Security-Policy direto em modo enforcement corre o
risco real de quebrar algo em produção sem aviso — o caminho seguro é
começar em modo report-only, que só REGISTRA violação sem bloquear
nada:</p>
<pre><code>add_header Content-Security-Policy-Report-Only "
  default-src 'self';
  script-src 'self' 'sha256-XXX...';
  style-src 'self' https://fonts.googleapis.com;
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  report-uri /csp-report;
" always;</code></pre>
<p>Depois de coletar violação real por algumas semanas e ajustar a
policy conforme o que aparece, trocar
<code>Content-Security-Policy-Report-Only</code> por
<code>Content-Security-Policy</code> passa do modo observação para
bloqueio de verdade, já calibrado contra falso positivo do próprio
tráfego legítimo.</p>

<h3>5. Rate limiting, o ABC contra credential stuffing</h3>
<p>Rotas como <code>/login</code>, <code>/register</code> e
<code>/forgot-password</code> são alvo óbvio de tentativa automatizada
de login em massa. No Nginx, isso vira uma zona de rate limit
dedicada:</p>
<pre><code>http {
  limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;
  limit_req_zone $binary_remote_addr zone=api:10m rate=600r/m;
}

server {
  location ~ ^/(login|register|forgot)$ {
    limit_req zone=auth burst=5 nodelay;
    proxy_pass http://app;
  }
  location /api/ {
    limit_req zone=api burst=100;
    proxy_pass http://app;
  }
}</code></pre>
<p>Combinar isso com rate-limit adicional por usuário ou api-key
diretamente na aplicação é importante porque rate-limit baseado só em
IP é facilmente contornado com proxy rotativo ou botnet distribuído —
uma segunda camada olhando a IDENTIDADE, não só a origem de rede,
fecha essa lacuna.</p>

<h3>6. Proxy reverso e o problema do IP real</h3>
<p>Quando o Nginx faz <code>proxy_pass</code>, a aplicação por trás
enxerga o IP <code>127.0.0.1</code> — o endereço do próprio proxy, não
do cliente real. Preservar o IP verdadeiro exige três headers
explícitos:</p>
<pre><code>proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Real-IP $remote_addr;</code></pre>
<p>E do lado da aplicação (Django, por exemplo), configurar
explicitamente que confia nesse header:</p>
<pre><code>USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')</code></pre>
<p>O detalhe crítico é NUNCA confiar em <code>X-Forwarded-For</code>
vindo diretamente de um cliente não confiável — sem um proxy
intermediário validando isso, qualquer cliente pode simplesmente
FORJAR esse header e se passar por qualquer IP que quiser. Configurar
explicitamente o número de "hops" confiáveis (via
<code>set_real_ip_from</code> combinado com
<code>real_ip_recursive on</code> no Nginx, ou a configuração
equivalente de trust hops num ALB) garante que só o valor inserido pelo
proxy legítimo seja aceito como verdadeiro.</p>

<h3>7. Caching para performance e proteção</h3>
<pre><code># Cache de respostas estáticas
location ~* \\.(jpg|css|js|woff2)$ {
  expires 30d;
  add_header Cache-Control "public, immutable";
}

# Cache de respostas dinâmicas (chamadas idempotentes)
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app:10m max_size=1g;

location /api/products {
  proxy_cache app;
  proxy_cache_valid 200 5m;
  proxy_cache_use_stale error timeout updating;
  add_header X-Cache-Status $upstream_cache_status;
  proxy_pass http://app;
}</code></pre>
<p>Além do ganho óbvio de performance, cache funciona como proteção
adicional contra DoS: uma requisição repetida encontra resposta pronta
no proxy e nunca chega a sobrecarregar a aplicação por trás, mesmo sob
volume alto de tráfego repetitivo.</p>

<h3>8. ModSecurity, WAF embedded</h3>
<p>O ModSecurity v3 combinado com o OWASP Core Rule Set bloqueia
padrão clássico de ataque — SQL injection, XSS, path traversal —
diretamente na camada do proxy. O risco real é falso positivo
quebrando funcionalidade legítima da aplicação, o que justifica
começar em modo <code>DetectionOnly</code>, só registrando sem
bloquear ainda:</p>
<pre><code># /etc/nginx/modsec/main.conf
Include /etc/nginx/modsec/coreruleset/crs-setup.conf
Include /etc/nginx/modsec/coreruleset/rules/*.conf
SecRuleEngine DetectionOnly
SecAuditLog /var/log/nginx/modsec_audit.log
SecAuditLogFormat JSON</code></pre>
<p>Depois de algumas semanas analisando o log gerado nesse modo,
mudar para <code>SecRuleEngine On</code> e ajustar falso positivo
específico com <code>SecRuleRemoveById</code> completa a transição para
bloqueio efetivo, já calibrado contra o tráfego real daquela
aplicação.</p>

<h3>9. Caddy, alternativa moderna</h3>
<p>O Caddy resolve boa parte da fricção de configuração manual:
provisiona TLS automaticamente via Let's Encrypt embutido, habilita
HTTP/3 por padrão, e mantém a sintaxe de configuração deliberadamente
mais simples que o Nginx equivalente:</p>
<pre><code># Caddyfile
api.example.com {
  reverse_proxy 127.0.0.1:8000
  encode zstd gzip
  header {
    Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    X-Content-Type-Options nosniff
  }
  rate_limit {
    zone login {
      key {http.request.remote.host}
      events 5
      window 60s
    }
  }
}</code></pre>

<h3>10. Anti-patterns + caso real</h3>
<ul>
<li><strong><code>autoindex on</code> em produção</strong>: lista o
conteúdo do diretório inteiro, um vazamento trivial de estrutura interna
sem nenhum esforço do atacante.</li>
<li><strong>Servir <code>.git</code> ou <code>.env</code></strong>:
caso real e recorrente — muitos site WordPress já vazaram credencial
inteira exatamente por não bloquear esses caminhos explicitamente via
regex.</li>
<li><strong>TLS 1.0/1.1 ainda habilitado</strong>: vulnerável a BEAST
e POODLE, ataques conhecidos há anos — desabilitar é trivial e sem
custo real de compatibilidade hoje.</li>
<li><strong>Sem <code>server_tokens off</code></strong>: revela a
versão exata do Nginx rodando, facilitando o atacante casar uma CVE
específica sem precisar adivinhar.</li>
<li><strong>Sem <code>client_max_body_size</code></strong>: deixa a
porta aberta para DoS via upload de arquivo desproporcionalmente
grande.</li>
<li><strong>Configuração default nunca testada no SSL Labs</strong>:
muitos times só descobrem a nota real quando um cliente reclama, não
antes.</li>
</ul>"""
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
                  ["hide_version yes;, também não é reconhecida pela config do Nginx.",
                   "no_version on;, uma diretiva que não existe no Nginx.",
                   "server_hidden 1;, sintaxe inventada, sem efeito real no Nginx."],
                  "Reduz o fingerprint para scanners automatizados."),
                q("Qual header força HTTPS em browsers compatíveis?",
                  "Strict-Transport-Security (HSTS)",
                  ["Force-HTTPS, nome inventado; não faz parte do padrão HTTP.",
                   "Upgrade-Required, um header real mas usado em outro contexto.",
                   "Cache-Secure, um nome que soa plausível mas não existe como header."],
                  "Inclua max-age longo e includeSubDomains; considere preload list após estável."),
                q("Em Nginx, como configurar um proxy reverso?",
                  "Usando proxy_pass http://backend; em um bloco location.",
                  ["Configurar root html sozinho, sem proxy de fato envolvido no caminho.",
                   "fastcgi_pass *, sintaxe inválida usada para PHP-FPM, não proxy HTTP.",
                   "rewrite ^.*$, reescreve a URL mas não encaminha para outro servidor."],
                  "Lembre-se de proxy_set_header Host $host e X-Forwarded-* para a app saber o cliente real."),
                q("Qual a porta padrão do TLS/HTTPS?",
                  "443",
                  ["8443, porta alternativa comum, mas não a padrão oficial do HTTPS.",
                   "80, a porta padrão do HTTP puro, sem qualquer camada de TLS.",
                   "23, a porta do Telnet, protocolo antigo e sem criptografia."],
                  "443 é well-known. 80 é HTTP puro, 23 é Telnet (legado e inseguro)."),
                q("Por que ativar gzip/brotli?",
                  "Reduz tamanho da resposta, acelera entrega.",
                  ["Aumenta a segurança da conexão contra ataque de interceptação.",
                   "Substitui completamente o cache do navegador e do proxy.",
                   "É um requisito real para habilitar o protocolo HTTP/2 no servidor."],
                  "Cuidado com BREACH/CRIME se concatenar conteúdo do usuário com segredo na mesma resposta."),
                q("Qual diretiva limita tamanho do body em Nginx?",
                  "client_max_body_size",
                  ["max_body_kb, um nome de diretiva que não existe no Nginx.",
                   "request_size_limit, nome plausível mas não usado pelo Nginx real.",
                   "post_size, sintaxe inventada; Nginx não reconhece essa diretiva."],
                  "Mitiga abuso por uploads gigantes; ajuste por endpoint quando for upload legítimo."),
                q("O que faz o Mozilla SSL Configuration Generator?",
                  "Gera configurações TLS recomendadas (modern/intermediate/old).",
                  ["Renova certificado TLS automaticamente antes dele expirar de vez.",
                   "Cria par de chave SSH para autenticação de acesso remoto ao servidor.",
                   "Mede a latência de rede entre o cliente e o servidor de destino."],
                  "Atualizado pela Mozilla com base em pesquisa de browsers e CVEs."),
                q("Como redirecionar HTTP para HTTPS em Nginx?",
                  "return 301 https://$host$request_uri;",
                  ["proxy_pass https, sintaxe incompleta sem destino de upstream definido.",
                   "if ($http) drop;, combinação de diretiva que o Nginx não reconhece.",
                   "rewrite ^/ /https/, reescreve o path, não força o protocolo em si."],
                  "301 (permanente) ajuda cache e SEO. Use return em vez de rewrite, mais rápido."),
                q("Por que rate limiting em /login?",
                  "Mitiga ataques de força bruta e credential stuffing.",
                  ["Reduz o consumo de memória RAM do processo worker do Nginx.",
                   "Acelera o processo de login reduzindo etapa de validação.",
                   "Ativa autenticação multifator diretamente na camada do Nginx."],
                  "Limit_req_zone + limit_req em Nginx, ou middleware na própria app."),
                q("Qual ferramenta automatiza certificados TLS gratuitos?",
                  "certbot (Let's Encrypt).",
                  ["docker compose, orquestra container, não emite certificado TLS.",
                   "cron-tls, nome inventado; não existe ferramenta com esse nome.",
                   "iptables, ferramenta de firewall, não emissão de certificado."],
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
                """<h3>1. Modelo de confiança em APT</h3>
<p>O processo de validação de pacote no APT segue quatro passos
encadeados, cada um dependendo do anterior. O repositório publica um
arquivo <code>Release</code> contendo o hash de cada
<code>Packages</code>. Esse arquivo <code>Release</code> é assinado com
GPG, com a assinatura indo em <code>Release.gpg</code> (ou embutida
junto no <code>InRelease</code>). O cliente baixa o <code>Release</code>,
valida a assinatura com a chave pública do mantenedor — guardada em
<code>/etc/apt/keyrings/</code> ou <code>/etc/apt/trusted.gpg.d/</code>
— e só DEPOIS de confirmar a assinatura passa a confiar nos hashes
listados dentro. E cada pacote <code>.deb</code> individual carrega um
hash que precisa bater exatamente com o registrado. O resultado prático
dessa cadeia é que, mesmo que um espelho seja comprometido, o atacante
não consegue trocar um pacote sem invalidar a assinatura de todo o
resto — forjar um pacote isolado exigiria também forjar a assinatura
GPG do mantenedor, algo que a criptografia por trás torna
inviável.</p>

<h3>2. Adicionando repositórios externos com segurança</h3>
<p>A forma antiga (<code>apt-key add -</code>) está depreciada
justamente porque adicionava confiança GLOBAL ao sistema inteiro — uma
chave adicionada dessa forma passava a poder assinar QUALQUER pacote
de QUALQUER repositório, não só o repositório específico que a
introduziu. A forma moderna usa <code>signed-by</code> para restringir
o escopo da chave a apenas aquele repositório declarado:</p>
<pre><code># 1. Baixe a chave em formato dearmored
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \\
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod 644 /etc/apt/keyrings/docker.gpg

# 2. Adicione o repositório referenciando essa chave
echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] \\
  https://download.docker.com/linux/ubuntu jammy stable' \\
  | sudo tee /etc/apt/sources.list.d/docker.list

# 3. Verifique a chave antes de aceitar
gpg --no-default-keyring --keyring /etc/apt/keyrings/docker.gpg --list-keys
# Compare o fingerprint com o que está na docs oficial.

sudo apt update
sudo apt install docker-ce</code></pre>
<p>O passo 3 — comparar o fingerprint com a documentação oficial antes
de confiar — é o que fecha a lacuna real: baixar a chave sozinho não
prova que ela veio do mantenedor legítimo, só que veio de ALGUM lugar.
Em RHEL/Fedora o mesmo princípio se aplica:</p>
<pre><code>sudo rpm --import https://download.docker.com/linux/centos/gpg
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
# /etc/yum.repos.d/docker-ce.repo precisa ter gpgcheck=1</code></pre>

<h3>3. Pinning de versões em produção</h3>
<p>Rodar <code>apt upgrade</code> num pipeline de produção sem testar
antes é uma aposta arriscada — o Nginx pode atualizar sozinho e a
configuração que funcionava até ontem quebrar sem aviso. Três
mecanismos resolvem isso de forma progressivamente mais explícita:
pinning por prioridade, marcação de hold, ou fixar a versão diretamente
no Dockerfile:</p>
<pre><code># /etc/apt/preferences.d/nginx
Package: nginx*
Pin: version 1.24.*
Pin-Priority: 1001

# Ou marque como hold
sudo apt-mark hold nginx

# Ou, em containers, pin direto no Dockerfile
RUN apt-get update &amp;&amp; apt-get install -y --no-install-recommends \\
    nginx=1.24.* \\
  &amp;&amp; rm -rf /var/lib/apt/lists/*</code></pre>
<p>Em RHEL, o equivalente é <code>dnf versionlock add nginx</code>.</p>

<h3>4. Mirror/registry interno: por que vale a pena</h3>
<p>Um mirror interno resolve cinco problemas de uma vez em ambiente
corporativo maduro: independência (o build não falha quando o upstream
externo cai temporariamente); auditoria (fica registrado exatamente
quem baixou o quê e quando); scanning (o pacote é varrido antes de
sequer chegar ao build, não depois); velocidade (baixar de dentro da
própria VPC é mais rápido que ir até o mantenedor original toda vez);
e compliance (auditorias como SOC 2 e ISO 27001 explicitamente
verificam esse tipo de controle). JFrog Artifactory (comercial, cobre
praticamente todo formato), Sonatype Nexus (comercial ou free) e
Pulpcore (open source, comum em ecossistema RHEL) são as ferramentas
dominantes desse espaço.</p>

<h3>5. Pacotes de linguagem: o oeste selvagem</h3>
<p>npm, PyPI, RubyGems e crates.io operam num modelo estruturalmente
diferente do APT: qualquer pessoa publica, sem barreira de curadoria
central. Isso abre quatro vetores de ataque específicos. O
<strong>typosquatting</strong> planta um pacote malicioso com nome
parecido ao legítimo — já existiram <code>colourama</code>,
<code>requestes</code>, <code>pythn</code>, cada um apostando num erro
de digitação comum. A <strong>dependency confusion</strong> explora um
pacote PRIVADO cujo nome também existe publicamente — se a configuração
de resolução não distinguir isso corretamente, o gerenciador de pacote
acaba preferindo o público (geralmente por ter versão mais recente),
puxando código de origem desconhecida no lugar do privado esperado. O
<strong>account takeover</strong> acontece quando o mantenedor original
perde a própria credencial e um atacante publica versão maliciosa
diretamente sobre o pacote legítimo já estabelecido — o caso
"colors.js" de 2022 seguiu exatamente esse padrão. E o
<strong>long con</strong> é o mais paciente dos quatro: um contribuidor
se estabelece como confiável ao longo de ANOS antes de finalmente
inserir um backdoor — o caso xz-utils de 2024 (seção 8) é o exemplo
mais estudado dessa categoria. Quatro mitigações reduzem essa
superfície: lockfile obrigatório (<code>poetry.lock</code>,
<code>package-lock.json</code>, <code>Cargo.lock</code> com hash),
garantindo build determinístico; mirror interno com whitelist de
pacote aprovado; scanner dedicado (<code>pip-audit</code>,
<code>npm audit</code>, <code>cargo audit</code>, OSV-Scanner, Trivy);
e dependency review direto no PR, já nativo tanto no GitHub quanto no
GitLab.</p>

<h3>6. SBOM, Software Bill of Materials</h3>
<p>Um SBOM é literalmente a lista de "ingredientes" de um software —
quando uma CVE nova aparece numa biblioteca comum (como libxml, por
exemplo), consultar o SBOM revela em segundos exatamente quais imagens
ou serviços são afetados, em vez de varrer manualmente duzentos
Dockerfiles um por um. Dois formatos dominam: CycloneDX (mantido pela
OWASP) e SPDX (mantido pela Linux Foundation). A geração é direta:</p>
<pre><code># Imagem Docker
syft myapp:1.0 -o cyclonedx-json &gt; sbom.json

# Sistema de arquivos
syft dir:/opt/app -o spdx-json &gt; sbom-spdx.json

# Python apenas
cyclonedx-py -i requirements.txt -o sbom.xml

# Cruzando com CVEs
grype sbom:./sbom.json</code></pre>
<p>Em setores específicos (governo federal dos EUA, automotivo,
médico), SBOM já deixou de ser boa prática opcional e virou obrigação
legal — via Executive Order 14028 nos Estados Unidos, por exemplo.</p>

<h3>7. Reproducibilidade de builds</h3>
<p>Um build reprodutível garante que o mesmo código-fonte, no mesmo
ambiente, sempre produz exatamente o mesmo binário byte a byte — essa
propriedade é o que permite VERIFICAR de forma independente que um
binário publicado realmente veio do código-fonte que ele alega
representar, sem precisar confiar cegamente na palavra de quem
publicou. É o conceito central do projeto Reproducible Builds, e depende
de quatro práticas: pin de versão em cada etapa do processo de build;
uma data determinística (via <code>SOURCE_DATE_EPOCH</code>, em vez do
timestamp real da execução); ausência de aleatoriedade em ordenação
(por exemplo, ordenar explicitamente uma lista de arquivo antes de
processá-la); e uma toolchain fixada, com compilador de versão
específica, não "o que estiver instalado no momento".</p>

<h3>8. Caso real: xz-utils 2024</h3>
<p>Em março de 2024, descobriu-se que as versões 5.6.0 e 5.6.1 do
<code>xz-utils</code> — uma biblioteca presente em praticamente toda
distribuição Linux — carregavam um backdoor injetado através da
<code>libsystemd</code>, permitindo execução remota de código via
sshd. O atacante, conhecido pelo pseudônimo Jia Tan, havia sido
mantenedor confiável do projeto por ANOS antes de finalmente inserir o
código malicioso — exatamente o padrão "long con" descrito na seção 5.
O que salvou a situação foi quase acidental: um engenheiro da
Microsoft notou uma latência ligeiramente incomum numa conexão SSH e
decidiu investigar por curiosidade, não porque algum alerta automatizado
tivesse disparado. As lições documentadas depois: um SBOM já em uso
teria identificado todo servidor afetado em minutos, não em dias de
investigação manual; o próprio delay natural entre uma versão nova
sair e chegar às distribuições Linux consideradas "estáveis" funcionou
como uma quarentena acidental que salvou a maioria dos casos reais;
build reproduzível, nesse incidente específico, NÃO teria pego o
problema — o tarball distribuído continha código efetivamente diferente
do que estava no repositório Git público, um detalhe que só uma
auditoria manual comparando os dois revelaria; e todo o episódio serve
de lembrete de que open source não é mágica automática de segurança —
ainda depende de revisão humana real acontecendo de fato, não apenas
presumida por estar "aberto ao público".</p>

<h3>9. Anti-patterns</h3>
<ul>
<li><strong><code>curl ... | bash</code></strong>: vira RCE completo
se o servidor de origem for comprometido em qualquer momento entre a
publicação e o download.</li>
<li><strong><code>--allow-unauthenticated</code></strong> ou
equivalente "ignorar erro de assinatura": remove precisamente a
proteção descrita na seção 1, tornando o pacote instalado
indistinguível de um forjado.</li>
<li><strong>Adicionar PPA ou repositório externo sem verificar
fingerprint</strong>: pula o único passo que realmente prova a origem
da chave (seção 2).</li>
<li><strong>Nunca pinar nada, sempre usar "latest"</strong>: abre
espaço para uma atualização inesperada quebrar produção sem aviso
prévio.</li>
<li><strong>Misturar repositório estável e instável</strong>: cria uma
combinação de versão imprevisível, um "Frankenstein" difícil de
depurar quando algo quebra.</li>
<li><strong>Pular release notes e atualizar produção direto</strong>:
ignora justamente a fonte de informação que alertaria sobre mudança
que quebra compatibilidade.</li>
</ul>

<h3>10. Workflow recomendado</h3>
<ol>
<li>No CI, rodar <code>pip-audit</code> ou <code>npm audit</code> em
todo PR, falhando explicitamente para CVE Critical ou High.</li>
<li>No build, gerar o SBOM e armazená-lo junto do artefato produzido.</li>
<li>No push, escanear no próprio registry (Trivy, Grype) contra uma
policy definida.</li>
<li>No deploy, um admission controller (Kyverno) só aceita imagem que
já venha com SBOM anexado.</li>
<li>Em operação, um re-scan periódico (Harbor, Trivy operator) pega
CVE nova que só foi divulgada depois do deploy original.</li>
<li>Renovate ou Dependabot abrindo PR de atualização automaticamente
mantém esse ciclo funcionando sem depender de alguém lembrar
manualmente.</li>
</ol>"""
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
                  ["Chave privada do mantenedor, que jamais deveria sair da máquina onde foi gerada.",
                   "Um token OAuth usado para autenticar uma chamada de API do repositório remoto.",
                   "O hash do binário do pacote, calculado bem antes de qualquer assinatura existir."],
                  "É a parte pública; APT a usa para verificar a assinatura do Release file."),
                q("`apt update` faz o quê?",
                  "Baixa metadados (índices) dos repositórios.",
                  ["Reinstala cada pacote já presente no sistema, um por um.",
                   "Apaga o cache local de pacote já baixado anteriormente.",
                   "Aplica patch de segurança direto no kernel em execução."],
                  "Atualiza o conhecimento sobre versões disponíveis. `apt upgrade` é que aplica."),
                q("Como bloquear uma versão específica em apt?",
                  "Pinning via /etc/apt/preferences.",
                  ["apt-get freeze, um subcomando que não existe no apt real.",
                   "dpkg --hold-version, flag inventada; dpkg não reconhece isso.",
                   "apt-mark exclude, opção que não existe no apt-mark de verdade."],
                  "`apt-mark hold` também funciona; pinning oferece mais granularidade (priority por origem)."),
                q("Por que evitar `curl ... | sh`?",
                  "Executa código remoto sem verificação de assinatura.",
                  ["Deixa o download mais lento por não usar cache do gerenciador.",
                   "Não funciona quando o shell padrão do sistema não é o bash.",
                   "Quebra a verificação de certificado TLS da conexão HTTPS."],
                  "MITM ou comprometimento do servidor de origem viram RCE imediato. Prefira pacote assinado."),
                q("`dpkg -l` lista:",
                  "Pacotes instalados em sistemas Debian.",
                  ["Logs recentes gerados pelo kernel durante o boot do sistema.",
                   "Repositórios configurados atualmente em /etc/apt/sources.list.",
                   "Só as dependências quebradas, sem listar o pacote inteiro."],
                  "É o equivalente a `rpm -qa` no mundo RHEL."),
                q("Em supply chain, 'typosquatting' é:",
                  "Publicar pacotes com nomes parecidos para enganar usuários (ex.: 'numpyy').",
                  ["Um erro de digitação cometido dentro do próprio código-fonte do kernel Linux.",
                   "Uma falha de resolução de nome causada por configuração errada de servidor DNS.",
                   "Um patch de segurança aplicado automaticamente sem revisão humana alguma antes."],
                  "Caso famoso: pacotes maliciosos com nomes próximos a 'request', 'pyyaml', 'colorama' etc."),
                q("Qual ferramenta gera SBOM em projetos Python?",
                  "syft (ou pip-audit/cyclonedx-py).",
                  ["pylint, linter de qualidade de código Python, não gerador de SBOM.",
                   "isort, organizador de import Python, não tem relação com SBOM.",
                   "tox, ferramenta de automação de teste, não gera lista de dependência."],
                  "syft funciona em qualquer linguagem; cyclonedx-py é específico de Python."),
                q("Por que assinar pacotes internos?",
                  "Garante autenticidade e integridade frente a tampering.",
                  ["Reduz o tamanho final do pacote compactado antes da distribuição.",
                   "Aumenta a velocidade de download por usar um servidor mais próximo.",
                   "Substitui a necessidade de rodar antivírus na máquina de destino."],
                  "Mesmo em rede 'segura', uma máquina comprometida poderia injetar binário se não houver assinatura."),
                q("Em RHEL, qual comando equivalente a `apt update`?",
                  "dnf check-update",
                  ["dnf install all, sintaxe inválida; install exige nome de pacote.",
                   "yum reset, subcomando que não existe no yum nem no dnf.",
                   "rpm -i all, instala um arquivo chamado 'all', não atualiza índice."],
                  "Em RHEL 8+ é dnf; antes era yum (mantido como alias)."),
                q("Por que fixar versões em produção?",
                  "Reprodutibilidade e evitar atualizações automáticas que quebrem o sistema.",
                  ["Reduz o consumo de CPU do processo gerenciador de pacotes durante a instalação.",
                   "Permite hot reload da aplicação inteira sem reiniciar o processo principal dela.",
                   "Habilita um modo verbose, mostrando muito mais detalhe durante a instalação inteira."],
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
                    "aplicação (errors, anomalias).</p>"

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
                  ["Compactam automaticamente o arquivo de log gerado no disco.",
                   "Ocupam menos espaço em disco do que o formato de texto livre.",
                   "Substituem completamente a necessidade de qualquer métrica numérica."],
                  "Texto livre vira regex doloroso. JSON tem schema e ferramentas de busca/agg nativas."),
                q("O que é correlation ID?",
                  "Identificador único que liga logs da mesma requisição entre serviços.",
                  ["Hash do conteúdo do disco, calculado periodicamente pelo sistema operacional.",
                   "Chave de criptografia usada para cifrar o conteúdo do arquivo de log.",
                   "Versão do schema de dado usada pela aplicação num momento específico."],
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
                  ["Prometheus, focado em métrica numérica, não em texto de log.",
                   "Beats, agente de coleta que envia dado para outro lugar, não armazena.",
                   "Tempo, ferramenta de trace distribuído, não de agregação de log."],
                  "Loki indexa apenas labels (não o corpo) e usa storage barato, perfeito para alto volume."),
                q("Por que rotacionar logs?",
                  "Evitar que ocupem todo o disco e facilitar arquivamento.",
                  ["Substituir completamente a necessidade de fazer qualquer backup.",
                   "Habilitar suporte a IPv6 na interface de rede do servidor.",
                   "Aumentar a performance da CPU durante o processamento de log."],
                  "logrotate é o utilitário padrão. journald já rotaciona internamente por tamanho/tempo."),
                q("`logrotate` configura-se em:",
                  "/etc/logrotate.conf e /etc/logrotate.d/*",
                  ["/etc/passwd, onde ficam usuário e shell, não configuração de log.",
                   "/proc/log, um caminho que não existe no sistema de arquivos /proc.",
                   "/var/lib/rotate, um diretório que o logrotate real não usa."],
                  "Cada serviço pode ter um arquivo próprio em /etc/logrotate.d/ com sua política."),
                q("Qual prioridade no syslog representa erros críticos?",
                  "crit (2)",
                  ["debug (7)", "info (6)", "notice (5)"],
                  "Hierarquia: emerg(0), alert(1), crit(2), err(3), warning(4), notice(5), info(6), debug(7)."),
                q("`journalctl --vacuum-size=200M` faz:",
                  "Reduz o journal a no máximo 200 MB.",
                  ["Reinicia o serviço journald por completo, sem limitar tamanho.",
                   "Move o conteúdo do journal inteiro para um bucket S3 remoto.",
                   "Apaga só o log gerado pelo kernel, sem tocar no resto do journal."],
                  "Há também --vacuum-time=7d para limitar por idade."),
                q("Por que centralizar logs?",
                  "Permite correlação entre máquinas e sobrevive à perda do host.",
                  ["Substitui log local por completo, sem manter cópia alguma na própria máquina.",
                   "Acelera o boot do sistema ao pular a etapa de inicialização do log.",
                   "Aumenta a entropia disponível para geração de número aleatório no host."],
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
                  ["Empurrar grande parte da validação de segurança para o fim do pipeline de deploy.",
                   "Mudar a posição da janela de monitoramento para o lado esquerdo da tela.",
                   "Ignorar completamente a etapa de segurança no momento final do deploy."],
                  "Linter no editor, SAST no PR, feedback rápido em vez de bloqueio no fim."),
                q("STRIDE serve para:",
                  "Threat modeling (Spoofing, Tampering, Repudiation, Info disclosure, DoS, Elevation).",
                  ["Formatos de log estruturado usados por ferramenta de observabilidade moderna, não modelagem.",
                   "Tipos de certificado TLS aceitos por navegador e servidor web atual, sem relação com ameaça.",
                   "Modos de execução de container, como privileged e rootless, definidos no runtime escolhido."],
                  "Cada letra é uma categoria, força você a pensar fora da sua zona."),
                q("O que é um postmortem 'blameless'?",
                  "Foco em causas sistêmicas, não em culpar pessoas.",
                  ["Documento secreto que só a liderança sênior tem permissão de ler.",
                   "Backup periódico do banco de dados, feito de forma automática diária.",
                   "Substituto formal do SLA assinado com o cliente antes do incidente."],
                  "Cultura blameless dá segurança psicológica para o time relatar erros honestamente."),
                q("MTTR mede:",
                  "Tempo médio para restauração após incidente.",
                  ["Quantidade total de bug reportado durante um trimestre inteiro.",
                   "Tempo de boot do servidor, medido do desligamento até voltar.",
                   "Latência de rede entre dois pontos medidos durante o incidente."],
                  "Junto com MTTD, é métrica DORA de operação. Menor = melhor."),
                q("Qual NÃO é prática DevSecOps?",
                  "Atrasar correções para depois do release.",
                  ["Fazer threat modeling logo na fase de design da revisão.",
                   "Rotacionar segredo de acesso periodicamente conforme política interna.",
                   "Automatizar execução de SAST diretamente dentro do pipeline de CI."],
                  "Empurrar débito de segurança para depois é como deixar de pagar boleto: "
                  "juros (incidente) chegam."),
                q("DevSecOps depende mais de:",
                  "Cultura e responsabilidade compartilhada.",
                  ["Comprar a ferramenta de segurança mais cara disponível no mercado.",
                   "Ignorar completamente a opinião do time de desenvolvimento no processo.",
                   "Centralizar boa parte da decisão de segurança dentro de um único time isolado."],
                  "Ferramenta sem cultura vira shelfware caro."),
                q("OWASP SAMM é:",
                  "Um modelo de maturidade em segurança de software.",
                  ["Um padrão de criptografia usado para proteger dado em repouso.",
                   "Um framework JavaScript usado para construir interface de usuário.",
                   "Um banco de dados relacional usado para guardar log de auditoria."],
                  "Avalia 5 funções (governança, design, implementação, verificação, operações) em 4 níveis."),
                q("Como medir maturidade do pipeline?",
                  "Definindo KPIs como cobertura SAST, SCA, falsos positivos e tempo de patch.",
                  ["Contando o número total de linha de código escrita pelo time inteiro.",
                   "Somando o número de commits feitos por cada desenvolvedor durante o mês inteiro.",
                   "Medindo o tamanho final do binário compilado e gerado ao término do pipeline."],
                  "Métrica precisa estar atrelada a comportamento, não vira competição numérica vazia."),
                q("Threat modeling é mais útil:",
                  "Cedo, no design, antes do código existir.",
                  ["Depois que o incidente já aconteceu e o dano está feito.",
                   "Exclusivamente quando a aplicação já está rodando em produção.",
                   "Só quando o time está construindo um aplicativo mobile específico."],
                  "Mudar arquitetura pré-código é barato; pós-deploy é caro e político."),
                q("Quem é responsável pela segurança em DevSecOps?",
                  "Todos no time, com champions de segurança apoiando.",
                  ["Só o blue team interno, sem envolvimento de mais ninguém no processo.",
                   "Só o time de auditoria externa contratado especificamente para isso.",
                   "Só a pessoa que ocupa o cargo de CISO dentro da empresa."],
                  "Modelo distribuído ('shift-everywhere') escala muito melhor que centralizado."),
            ],
        },
    ],
}
