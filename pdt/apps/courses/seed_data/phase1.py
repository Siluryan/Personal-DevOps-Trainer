"""Fase 1, O Alicerce (Sistemas e Redes)."""
from ._helpers import m, q

PHASE1 = {
    "name": "Fase 1: O Alicerce (Sistemas e Redes)",
    "name_en": "Phase 1: The Foundation (Systems and Networking)",
    "description": "Onde tudo começa: o servidor e o sistema operacional.",
    "description_en": "Where everything starts: the server and the operating system.",
    "topics": [
        # =====================================================================
        # 1.1 Fundamentos de Linux
        # =====================================================================
        {
            "title": "Fundamentos de Linux",
            "title_en": "Linux Fundamentals",
            "summary": "Permissões de arquivos, usuários e gestão de processos, a base de qualquer servidor.",
            "summary_en": "File permissions, users, and process management, the foundation of any server.",
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
                "intro_en": (
                    "Practically every production server in the world runs Linux. AWS, Azure, "
                    "GCP, all of them use Linux as the base for their managed services (RDS, EKS, "
                    "Lambda, etc.) and the overwhelming majority of containers in K8s are little "
                    "Linux boxes. Knowing Linux <strong>deeply</strong> is what separates the "
                    "engineer who understands what they're doing from the one who just copies "
                    "commands off Stack Overflow.<br><br>"
                    "This lesson covers the operating system's mental model: what users, "
                    "processes, and permissions are, not as textbook abstractions, but as "
                    "elements attackers exploit every day. Every container CVE starts exactly "
                    "here."
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
<div class="mermaid">
flowchart TD
    A["Processo pede acesso a um arquivo"] --> B{"UID do processo é o dono do arquivo?"}
    B -- "Sim" --> C["Aplica permissão do DONO (primeiros 3 bits)"]
    B -- "Não" --> D{"GID do processo está no grupo do arquivo?"}
    D -- "Sim" --> E["Aplica permissão do GRUPO (bits do meio)"]
    D -- "Não" --> F["Aplica permissão de OUTROS (últimos 3 bits)"]
    C --> G{"Bit pedido (r/w/x) está setado?"}
    E --> G
    F --> G
    G -- "Sim" --> H["Acesso permitido"]
    G -- "Não" --> I["Acesso negado (EACCES)"]
</div>


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
                "body_en": (
                """<h3>1. Philosophy: everything is a file</h3>
<p>Unix's classic motto applies fully to Linux: everything is
represented as a file — disk (<code>/dev/sda</code>), network
socket (<code>/proc/net/tcp</code>), a running process
(<code>/proc/&lt;pid&gt;</code>), the kernel's own configuration
(<code>/sys</code>), even USB devices and GPIO. The practical
consequence is that the SAME permission model (rwx combined with
owner and group) controls literally all of this at once, with no
special exception for any resource type. When an attacker exploits a
vulnerability to write to <code>/dev/mem</code> or
<code>/proc/sys/kernel/core_pattern</code>, they're using exactly
that same unified file model to subvert the kernel — not a
different mechanism. Learning Linux deeply is, to a large extent,
learning which specific files matter and who should be allowed to
read or write to each one.</p>
<div class="mermaid">
flowchart TD
    A["Processo pede acesso a um arquivo"] --> B{"UID do processo é o dono do arquivo?"}
    B -- "Sim" --> C["Aplica permissão do DONO (primeiros 3 bits)"]
    B -- "Não" --> D{"GID do processo está no grupo do arquivo?"}
    D -- "Sim" --> E["Aplica permissão do GRUPO (bits do meio)"]
    D -- "Não" --> F["Aplica permissão de OUTROS (últimos 3 bits)"]
    C --> G{"Bit pedido (r/w/x) está setado?"}
    E --> G
    F --> G
    G -- "Sim" --> H["Acesso permitido"]
    G -- "Não" --> I["Acesso negado (EACCES)"]
</div>


<h3>2. Identity model: UID, GID and processes</h3>
<p>Every process runs on behalf of a <strong>UID</strong> (effective
user id) and carries a primary <strong>GID</strong> plus a set of
supplementary groups. Every process INHERITS this identity from its
own parent — init/<code>systemd</code> starts as UID 0 (root), and
every child process derives from that root. Three UID ranges carry
conventional meaning: <strong>UID 0</strong> is root itself, which
literally ignores every permission check — that's exactly why an
internet-facing service should never run under that UID; UIDs
between 1 and 999 are system users created by the packages
themselves (<code>www-data</code>, <code>postgres</code>,
<code>nobody</code>); and UIDs from 1000 onward are human users on a
modern distribution. Inspecting this identity is direct:</p>
<pre><code>id                 # quem sou eu (uid, gid, grupos)
id deploy          # idem para outro usuário
ps -eo pid,uid,user,cmd | head
cat /etc/passwd    # mapeamento UID ↔ login ↔ shell
cat /etc/group     # mapeamento GID ↔ nome do grupo</code></pre>
<p>A security detail many people overlook: the password NEVER lives
in <code>/etc/passwd</code> on a modern system — the hash lives
specifically in <code>/etc/shadow</code>, readable only by root.
Using <code>/etc/passwd</code> as a general read reference is normal
and expected; leaking <code>/etc/shadow</code> to another user is
already a security incident in its own right.</p>

<h3>3. Classic permissions: the rwx model</h3>
<p>Every file carries an owner, a group, and three permission
classes (user, group, other), each with three bits (<code>r</code>=4,
<code>w</code>=2, <code>x</code>=1) representable in octal:</p>
<pre><code>chmod 750 deploy.sh
  └ user 7 = r+w+x
  └ group 5 = r+x  (sem write)
  └ other 0 = nada

ls -l deploy.sh
-rwxr-x---  1 deploy web  142 Apr 25 16:12 deploy.sh</code></pre>
<p>In a directory, the meaning changes in a subtle and important
way: <code>r</code> allows LISTING file names inside, <code>x</code>
allows ENTERING the directory, and <code>w</code> allows CREATING or
REMOVING a file there. That makes it perfectly possible to have a
directory with <code>x</code> but without <code>r</code> — in that
case, you can access a specific file if you already know its exact
name, but you can't list the directory's contents to discover that
name on your own. For an incremental change, symbolic mode tends to
be more readable than recomputing the whole octal number:</p>
<pre><code>chmod g+rw arquivo       # add read+write para o grupo
chmod o-x  diretorio/     # remove execute do 'other'
chmod -R u+rwX,g+rX,o-rwx /srv/app/   # X executa só em diretórios</code></pre>

<h3>4. Special bits: setuid, setgid, sticky</h3>
<p>Three additional bits change how a binary behaves when executed.
<strong>setuid</strong> (4xxx) makes the program run with the
privilege of the file's OWNER, not the caller's — that's exactly how
the <code>passwd</code> command manages to modify
<code>/etc/shadow</code> even when run by an ordinary user with no
privilege at all. Misapplied, it's a classic privilege-escalation
vector — every setuid binary present on a machine should be on an
audited whitelist, not left to chance. <strong>setgid</strong>
(2xxx) follows the same logic, but with the group instead of the
owner; on a directory, it guarantees every NEW file created there
automatically inherits the directory's group, useful specifically
for a shared team area. And the <strong>sticky bit</strong> (1xxx),
applied to a directory, restricts who can DELETE a file to whoever
created it (or the directory's own owner) — that's exactly why
<code>/tmp</code> runs with mode <code>1777</code>: any user creates
a file there freely, but only whoever created it can delete their
own file afterward.</p>
<pre><code>find / -perm -4000 -type f 2&gt;/dev/null   # binários setuid
find / -perm -2000 -type f 2&gt;/dev/null   # binários setgid</code></pre>

<h3>5. Beyond rwx: ACLs and capabilities</h3>
<p>The rwx model has only three fixed permission classes — when that
isn't enough, POSIX ACLs allow granularity per specific user or
group, on top of the file's default owner and group:</p>
<pre><code>setfacl -m u:carlos:r-- /srv/data/relatorio.csv
setfacl -m g:auditoria:r-x /srv/scripts/
getfacl /srv/data/relatorio.csv</code></pre>
<p>Linux capabilities solve a different problem: they decompose
root's entire power into about 40 individual grains
(<code>man capabilities(7)</code>). Instead of granting full root to
a web binary just because it needs to bind on port 80 (below 1024,
restricted to root by default), you can grant just
<code>CAP_NET_BIND_SERVICE</code>, exactly the fraction of privilege
needed:</p>
<pre><code>setcap cap_net_bind_service=+ep /usr/local/bin/myserver
getcap /usr/local/bin/myserver</code></pre>
<p>That's precisely the mechanism behind a well-built Docker image
that manages to listen on a privileged port while still running as a
non-root user inside the container.</p>

<h3>6. Processes, signals and systemd</h3>
<p>Every process carries a <strong>PID</strong>, a parent
(<strong>PPID</strong>), and a state — <code>R</code> (running),
<code>S</code> (sleeping), <code>D</code> (disk wait), <code>Z</code>
(zombie) — inspectable via <code>ps auxf</code> or interactively via
<code>htop</code>. The kernel communicates with a process through
<strong>signals</strong>, each with a specific conventional meaning:
<code>SIGTERM (15)</code> asks for a polite termination — a
well-behaved process closes connections, saves state, and exits on
its own, and it should always be the first one tried;
<code>SIGKILL (9)</code> terminates immediately with NO chance for
cleanup, reserved for when SIGTERM no longer gets a response;
<code>SIGHUP (1)</code>, historically "hangup", became the
conventional signal for reloading configuration without restarting
the whole process; <code>SIGINT (2)</code> is the terminal's Ctrl+C;
and <code>SIGSTOP/SIGCONT</code> pause and resume execution. On a
modern distribution, every service is managed by systemd through
units:</p>
<pre><code>systemctl status nginx
systemctl restart nginx
systemctl reload nginx       # equivale a SIGHUP, sem downtime
journalctl -u nginx -f       # logs em tempo real
systemctl list-units --failed</code></pre>

<h3>7. Standard filesystem hierarchy (FHS)</h3>
<p>Knowing in advance where each type of file lives saves real
search time in any investigation. <code>/etc</code> holds system
configuration, editable only by root. <code>/usr/bin</code> and
<code>/usr/sbin</code> hold system binaries, while
<code>/usr/local/bin</code> is reserved for binaries installed
manually outside the package manager. <code>/var</code> holds
VARIABLE data — logs, cache, spool, databases — and it makes sense
for it to live on a separate filesystem in production, precisely
because it grows unpredictably. <code>/home</code> holds human user
data. <code>/srv</code> holds data served directly by a service
(web, FTP). <code>/opt</code> holds "self-contained" third-party
software, packaged independently from the rest of the system.
<code>/proc</code> and <code>/sys</code> are pseudo-filesystems
exposed directly by the kernel, without physically existing on disk.
<code>/dev</code> represents devices. And <code>/run</code> and
<code>/tmp</code> are ephemeral, wiped on every reboot.</p>

<h3>8. Classic anti-patterns</h3>
<ul>
<li><strong><code>chmod 777 /srv/app</code></strong>: any user on
the same system gains write permission — an attacker with ANY other
account on the same machine can inject a payload directly into the
legitimate application, a trivially easy escalation.</li>
<li><strong>Running a service as root</strong>: any known bug in the
service (Heartbleed, Log4Shell) automatically becomes RCE as root,
and therefore full compromise of the machine — a dedicated user
combined with <code>User=</code> in systemd closes that gap
directly.</li>
<li><strong>Adding a user to the <code>sudo</code> group without a
specific rule</strong>: grants total power when probably only one
specific command was really needed — prefer a drop-in in
<code>/etc/sudoers.d/</code> allowing exactly that specific
command.</li>
<li><strong>Editing a configuration file as root without a backup
first</strong>: a <code>vim /etc/sshd_config</code> that forgets to
review <code>PermitRootLogin</code> can lock the operator themselves
out of the production server without warning — <code>cp arquivo
arquivo.bak</code> before any edit costs seconds and avoids this
entire scenario.</li>
<li><strong>Forgetting the correct permission on <code>~/.ssh</code></strong>:
sshd SILENTLY refuses authentication when the directory or file has
too loose a permission — the only way to discover this is by looking
at <code>journalctl -u sshd</code> after authentication has already
failed with no clear message on the client's screen.</li>
</ul>

<h3>9. Real case: the <code>/tmp</code> attack</h3>
<p>In 2016, several distributions had to change the default behavior
of <code>/tmp</code> to a per-user isolated tmpfs, because a
<code>/tmp</code> shared among all processes had become a recurring
attack vector: service A would create a file with a PREDICTABLE name
(<code>/tmp/upload.txt</code>); an attacker, knowing this in advance,
would create a symlink with that same name beforehand, pointing to
<code>/etc/shadow</code>; and the service, running as root, when
"creating" its own temporary file, would actually overwrite the
entire shadow file through the already-planted symlink. It was
exactly this attack pattern that popularized
<code>PrivateTmp=true</code> in systemd — a relatively small change
in the kernel and in systemd that eliminated an entire class of bug
at once, without requiring every individual service to be fixed
separately.</p>

<h3>10. Mental checklist when connecting to a new host</h3>
<ol>
<li><code>uname -a</code>, to learn the kernel and architecture.</li>
<li><code>cat /etc/os-release</code>, to know exactly which
distribution and version.</li>
<li><code>id</code> and <code>sudo -l</code>, to know who you are
and exactly what you can do.</li>
<li><code>ss -tulpn</code>, to see which ports are open and who is
listening on each one.</li>
<li><code>systemctl list-units --type=service --state=running</code>,
for the inventory of active services.</li>
<li><code>df -h</code> and <code>free -h</code>, for available disk
and memory.</li>
<li><code>journalctl -p err -S 'today'</code>, for a recent error
that might already indicate an ongoing problem.</li>
</ol>
<p>Running through this sequence in two minutes tells you whether
you're stepping onto familiar, healthy ground, or whether the
machine already shows signs of something compromised before you even
dig further.</p>"""
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
                "practical_en": (
                    "On a clean VM or container:<br>"
                    "(1) Create the user <code>app</code> and the group <code>web</code>; add "
                    "<code>app</code> to the group. Verify with <code>id app</code>.<br>"
                    "(2) Create the directory <code>/srv/app</code> owned by <code>app:web</code> "
                    "with mode <code>2750</code> (note the setgid). Create a file inside, confirm "
                    "it inherited the <code>web</code> group.<br>"
                    "(3) Create a second user <code>visitante</code> not in that group. Try to "
                    "read the file as that user and watch it fail. Use <code>strace -e openat</code> "
                    "to see the EACCES coming from the kernel.<br>"
                    "(4) Add an ACL: "
                    "<code>setfacl -m u:visitante:r-- /srv/app/config.yml</code>. Confirm that "
                    "now it can read it.<br>"
                    "(5) Bonus: set up an <code>nc -l -p 8080</code> running as "
                    "<code>app</code> and grant it <code>CAP_NET_BIND_SERVICE</code> via "
                    "<code>setcap</code> on a copy of <code>nc</code>; try binding to port 80 "
                    "with and without the capability."
                ),
            },
            "materials": [
                m("The Linux Documentation Project: Permissions",
                  "https://tldp.org/LDP/intro-linux/html/sect_03_04.html",
                  "docs", "Resumo clássico sobre permissões em Linux.",
                  title_en="The Linux Documentation Project: Permissions",
                  description_en="Classic summary of Linux permissions."),
                m("man chmod", "https://man7.org/linux/man-pages/man1/chmod.1.html",
                  "docs", "Manual oficial.", title_en="man chmod", description_en="Official manual."),
                m("man chown", "https://man7.org/linux/man-pages/man1/chown.1.html",
                  "docs", "Manual oficial.", title_en="man chown", description_en="Official manual."),
                m("Red Hat: Managing processes with systemd",
                  "https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_processes_with_systemd/index",
                  "docs", "Gestão moderna de processos.",
                  title_en="Red Hat: Managing processes with systemd",
                  description_en="Modern process management."),
                m("Linux Journey: Command Line",
                  "https://linuxjourney.com/lesson/the-shell",
                  "course", "Curso interativo gratuito introduzindo o shell.",
                  title_en="Linux Journey: Command Line",
                  description_en="Free interactive course introducing the shell."),
                m("man capabilities(7)",
                  "https://man7.org/linux/man-pages/man7/capabilities.7.html",
                  "docs", "Como decompor o poder de root em pedaços.",
                  title_en="man capabilities(7)",
                  description_en="How to decompose root's power into pieces."),
            ],
            "questions": [
                q("O que representa o '7' em `chmod 750 arquivo`?",
                  "Leitura, escrita e execução (rwx) para o dono do arquivo.",
                  ["Um bit de SUID combinado com sticky bit, não permissão comum de dono.",
                   "Leitura e escrita combinadas para o grupo, sem execução liberada.",
                   "Execução isolada para o dono, sem leitura ou escrita concedidas."],
                  "Em octal: 4 (read) + 2 (write) + 1 (execute) = 7. O segundo dígito (5) "
                  "é r-x para o grupo e o terceiro (0) bloqueia o resto do mundo.",
                  statement_en="What does the '7' represent in `chmod 750 file`?",
                  correct_en="Read, write, and execute (rwx) for the file's owner.",
                  wrong_en=["A SUID bit combined with the sticky bit, not a regular owner permission.",
                            "Read and write combined for the group, with execute left out.",
                            "Execute only for the owner, with no read or write granted at all."],
                  explanation_en="In octal: 4 (read) + 2 (write) + 1 (execute) = 7. The second "
                  "digit (5) is r-x for the group, and the third (0) blocks everyone else."),
                q("Qual comando exibe os processos em execução com seu PID?",
                  "ps", ["chmod", "ls", "tar"],
                  "ps lista os processos do shell atual; `ps auxf` mostra todos com hierarquia.",
                  statement_en="Which command displays running processes along with their PID?",
                  correct_en="ps", wrong_en=["chmod", "ls", "tar"],
                  explanation_en="ps lists the processes of the current shell; `ps auxf` shows "
                  "all of them with a hierarchy."),
                q("Como alterar o dono do arquivo `app.log` para o usuário `deploy`?",
                  "chown deploy app.log",
                  ["chmod deploy app.log", "chgrp deploy app.log", "passwd deploy app.log"],
                  "chown muda o dono. chgrp só muda o grupo; chmod muda permissões.",
                  statement_en="How do you change the owner of the file `app.log` to the user `deploy`?",
                  correct_en="chown deploy app.log",
                  wrong_en=["chmod deploy app.log", "chgrp deploy app.log", "passwd deploy app.log"],
                  explanation_en="chown changes the owner. chgrp only changes the group; chmod "
                  "changes permissions."),
                q("O que é o UID 0 em sistemas Linux?",
                  "É o ID do superusuário (root).",
                  ["Um usuário de sistema criado especificamente para rodar o servidor web nginx.",
                   "Um usuário criado durante a instalação, mas sem qualquer privilégio especial.",
                   "Uma conta reservada para acesso temporário de visitantes na máquina."],
                  "UID 0 ignora checks de permissão, por isso processos críticos não devem rodar como root.",
                  statement_en="What is UID 0 on Linux systems?",
                  correct_en="It's the ID of the superuser (root).",
                  wrong_en=["A system user created specifically to run the nginx web server.",
                            "A user created during installation, but with no special privilege at all.",
                            "An account reserved for temporary guest access on the machine."],
                  explanation_en="UID 0 ignores permission checks entirely, which is why critical "
                  "processes should never run as root."),
                q("Qual sinal `kill -9 PID` envia para o processo?",
                  "SIGKILL, termina o processo imediatamente sem chance de cleanup.",
                  ["SIGTERM, pede o encerramento e dá tempo para o processo salvar estado antes.",
                   "SIGHUP, recarrega a configuração do processo sem derrubar a conexão atual.",
                   "SIGSTOP, pausa o processo, que pode ser retomado depois com SIGCONT."],
                  "SIGKILL não pode ser ignorado nem capturado. Prefira SIGTERM (15) sempre que possível.",
                  statement_en="Which signal does `kill -9 PID` send to the process?",
                  correct_en="SIGKILL, terminates the process immediately with no chance for cleanup.",
                  wrong_en=["SIGTERM, asks for termination and gives the process time to save state first.",
                            "SIGHUP, reloads the process configuration without dropping the current connection.",
                            "SIGSTOP, pauses the process, which can later be resumed with SIGCONT."],
                  explanation_en="SIGKILL cannot be ignored or caught. Prefer SIGTERM (15) whenever "
                  "possible."),
                q("Em `ls -l`, a string `-rwxr-x---` significa que o grupo pode:",
                  "Ler e executar, mas não escrever.",
                  ["Escrever e ler o conteúdo, mas sem permissão para executar o arquivo.",
                   "Executar sem restrição, incluindo escrita liberada para o grupo inteiro.",
                   "Bloqueado por completo, o grupo não acessa o arquivo de forma alguma."],
                  "r-x para o grupo (5 em octal) e --- para outros (0). Modo final 750.",
                  statement_en="In `ls -l`, the string `-rwxr-x---` means the group can:",
                  correct_en="Read and execute, but not write.",
                  wrong_en=["Write and read the content, but without permission to execute the file.",
                            "Execute without restriction, including write access for the whole group.",
                            "Fully blocked, the group cannot access the file in any way."],
                  explanation_en="r-x for the group (5 in octal) and --- for others (0). Final "
                  "mode 750."),
                q("Onde ficam os usuários e seus shells padrão?",
                  "/etc/passwd",
                  ["/etc/shadow", "/var/log/users", "/root/.bashrc"],
                  "Hashes de senha ficam em /etc/shadow (legível só para root). /etc/passwd "
                  "lista usuários, UIDs, home e shell.",
                  statement_en="Where do users and their default shells live?",
                  correct_en="/etc/passwd",
                  wrong_en=["/etc/shadow", "/var/log/users", "/root/.bashrc"],
                  explanation_en="Password hashes live in /etc/shadow (readable only by root). "
                  "/etc/passwd lists users, UIDs, home directory, and shell."),
                q("Qual comando mostra o uso de disco por diretório?",
                  "du",
                  ["free -m", "df", "ls -lh"],
                  "`du -sh *` é o atalho clássico. df mostra uso por filesystem; free mostra memória.",
                  statement_en="Which command shows disk usage per directory?",
                  correct_en="du", wrong_en=["free -m", "df", "ls -lh"],
                  explanation_en="`du -sh *` is the classic shortcut. df shows usage per "
                  "filesystem; free shows memory."),
                q("O que faz o bit setuid (`chmod u+s`) em um executável?",
                  "Roda o programa com privilégio do dono do arquivo, não de quem o executou.",
                  ["Aumenta a prioridade de agendamento do processo no escalonador do kernel.",
                   "Bloqueia qualquer escrita no arquivo, mesmo pelo próprio dono original do binário.",
                   "Esconde o arquivo de listagens comuns, exigindo uma flag extra passada ao ls."],
                  "É o que faz `passwd` poder alterar /etc/shadow mesmo executado por usuário comum. "
                  "Mal usado é vetor de escalada, só em binários muito auditados.",
                  statement_en="What does the setuid bit (`chmod u+s`) do on an executable?",
                  correct_en="Runs the program with the privilege of the file's owner, not the caller's.",
                  wrong_en=["Increases the process's scheduling priority in the kernel's scheduler.",
                            "Blocks any write to the file, even by the binary's own original owner.",
                            "Hides the file from ordinary listings, requiring an extra flag passed to ls."],
                  explanation_en="It's what lets `passwd` modify /etc/shadow even when run by an "
                  "ordinary user. Misused, it's an escalation vector, only for heavily audited "
                  "binaries."),
                q("Qual diretório guarda configurações de sistema em Linux?",
                  "/etc",
                  ["/var", "/usr/bin", "/home"],
                  "/etc é o diretório padrão de configuração. /var guarda dados variáveis (logs, "
                  "spool); /usr/bin tem binários; /home tem dados dos usuários.",
                  statement_en="Which directory holds system configuration on Linux?",
                  correct_en="/etc",
                  wrong_en=["/var", "/usr/bin", "/home"],
                  explanation_en="/etc is the default configuration directory. /var holds "
                  "variable data (logs, spool); /usr/bin has binaries; /home has user data."),
            ],
        },
        # =====================================================================
        # 1.2 Redes de Computadores
        # =====================================================================
        {
            "title": "Redes de Computadores",
            "title_en": "Computer Networking",
            "summary": "TCP/IP, DNS, portas e roteamento, o vocabulário comum de qualquer sistema distribuído.",
            "summary_en": "TCP/IP, DNS, ports, and routing, the common vocabulary of any distributed system.",
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
                "intro_en": (
                    "When something breaks in production and the stack trace says nothing, 80% "
                    "of the time the problem is network-related: slow DNS, an expired "
                    "certificate, a wrong MTU on a VPN, a security group blocking a new port, "
                    "exhausted NAT. An engineer with no fluency in TCP/IP is stuck depending on "
                    "the infra team to open a ticket for every incident.<br><br>"
                    "This lesson is a straight-to-the-point <em>crash course</em>: the mental "
                    "model, the tools that diagnose 95% of problems, and the most expensive "
                    "mistakes I've seen people make."
                ),
                "body": (
                    "<h3>1. As quatro camadas que importam (modelo TCP/IP)</h3>"
                    "<p>Esqueça as 7 camadas do OSI por enquanto. O modelo prático é o "
                    "TCP/IP de quatro camadas:</p>"
                    """
<div class="mermaid">
sequenceDiagram
    participant C as Cliente
    participant R as Resolver do SO
    participant Root as Servidor raiz
    participant TLD as Servidor .com
    participant Auth as Servidor autoritativo
    C->>R: Resolver exemplo.com
    R->>Root: Quem responde por .com?
    Root-->>R: Endereço do servidor TLD
    R->>TLD: Quem responde por exemplo.com?
    TLD-->>R: Endereço do autoritativo
    R->>Auth: Qual o IP de exemplo.com?
    Auth-->>R: 93.184.216.34
    R-->>C: 93.184.216.34, cacheado até o TTL expirar
</div>
"""
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
                "body_en": (
                    "<h3>1. The four layers that matter (TCP/IP model)</h3>"
                    "<p>Forget the 7 OSI layers for now. The practical model is the "
                    "four-layer TCP/IP:</p>"
                    """
<div class="mermaid">
sequenceDiagram
    participant C as Cliente
    participant R as Resolver do SO
    participant Root as Servidor raiz
    participant TLD as Servidor .com
    participant Auth as Servidor autoritativo
    C->>R: Resolver exemplo.com
    R->>Root: Quem responde por .com?
    Root-->>R: Endereço do servidor TLD
    R->>TLD: Quem responde por exemplo.com?
    TLD-->>R: Endereço do autoritativo
    R->>Auth: Qual o IP de exemplo.com?
    Auth-->>R: 93.184.216.34
    R-->>C: 93.184.216.34, cacheado até o TTL expirar
</div>
"""
                    "<ol>"
                    "<li><strong>Link</strong>: Ethernet, Wi-Fi. Addressing by MAC. You "
                    "only deal with this in a datacenter or deep debugging.</li>"
                    "<li><strong>Internet</strong>: IP. Addressing and routing between "
                    "networks. IPv4 and IPv6.</li>"
                    "<li><strong>Transport</strong>: TCP (reliable, ordered) and UDP (fast, "
                    "no guarantee). Multiplexes by port.</li>"
                    "<li><strong>Application</strong>: HTTP, DNS, SSH, gRPC, AMQP, where your "
                    "app lives.</li>"
                    "</ol>"
                    "<p>Each packet is encapsulated top-down on the way out and decapsulated "
                    "on the way in. Knowing which layer the problem lives in is what makes "
                    "diagnosis take minutes instead of hours.</p>"

                    "<h3>2. Addressing, CIDR, and RFC 1918</h3>"
                    "<p>IPv4 addresses are 32 bits (~4 billion, exhausted in 2011); IPv6 is "
                    "128 bits. We use <strong>CIDR</strong> to talk about blocks:</p>"
                    "<pre><code>10.0.0.0/8       # 16M endereços (privada, RFC 1918)\n"
                    "172.16.0.0/12    # 1M endereços (privada, RFC 1918)\n"
                    "192.168.0.0/16   # 65k endereços (privada, RFC 1918)\n"
                    "169.254.0.0/16   # link-local (auto-configurado)\n"
                    "127.0.0.0/8      # loopback\n"
                    "0.0.0.0/0        # 'qualquer' (rota default, bind em todas as interfaces)</code></pre>"
                    "<p>The number after the slash is the network <em>mask</em> in bits. "
                    "<code>/24</code> = 256 addresses; <code>/16</code> = 65,536; "
                    "<code>/8</code> = 16 million. In each block, two addresses aren't usable "
                    "(network and broadcast), so <code>/24</code> gives you 254 hosts.</p>"

                    "<h3>3. TCP vs UDP, when to use each</h3>"
                    "<p>TCP establishes a connection with a <strong>three-way handshake</strong> "
                    "(SYN → SYN-ACK → ACK), then transmits data guaranteeing:</p>"
                    "<ul>"
                    "<li>Order (numbers segments);</li>"
                    "<li>Delivery (retransmits what's lost);</li>"
                    "<li>Flow control (adjusts the send window to the receiver's capacity);</li>"
                    "<li>Congestion control (adapts to the network, Reno, Cubic, BBR).</li>"
                    "</ul>"
                    "<p>All of this has a cost: the handshake charges one RTT before the "
                    "first useful byte, and head-of-line blocking makes a single loss stall "
                    "the whole stream. That's why <strong>HTTP/3</strong> abandoned TCP and "
                    "moved to QUIC over UDP.</p>"
                    "<p>UDP is stateless: it just sends the datagram. No retransmission, no "
                    "order. Use it when latency &gt; reliability: DNS, real-time voice/video, "
                    "QUIC, WireGuard, online games.</p>"

                    "<h3>4. Ports: who talks to whom</h3>"
                    "<p>Ports are 16-bit numbers that multiplex services on the same IP:</p>"
                    "<ul>"
                    "<li><strong>0-1023</strong>, <em>well-known</em>. Binding requires root "
                    "(or <code>CAP_NET_BIND_SERVICE</code>). HTTP=80, HTTPS=443, SSH=22, "
                    "DNS=53, SMTP=25.</li>"
                    "<li><strong>1024-49151</strong>, registered. PostgreSQL=5432, "
                    "MySQL=3306, Redis=6379, MongoDB=27017.</li>"
                    "<li><strong>49152-65535</strong>, ephemeral. The kernel picks the "
                    "source port for each outgoing connection from here.</li>"
                    "</ul>"
                    "<p>Ephemeral port exhaustion is one of the most under-diagnosed causes "
                    "of outages: the load balancer closing connections on timeout while "
                    "<code>net.ipv4.ip_local_port_range</code> is left at default.</p>"

                    "<h3>5. DNS, the internet's phone book (and the best place to cause an outage)</h3>"
                    "<p>DNS resolves names into IPs with caching at several levels: the app's "
                    "resolver, the OS stub (<code>/etc/nsswitch</code> + "
                    "<code>systemd-resolved</code>), the ISP/cloud resolver, the "
                    "authoritatives. Essential record types:</p>"
                    "<table style='border-collapse:collapse'>"
                    "<tr><td><code>A</code></td><td>name → IPv4</td></tr>"
                    "<tr><td><code>AAAA</code></td><td>name → IPv6</td></tr>"
                    "<tr><td><code>CNAME</code></td><td>name → another name</td></tr>"
                    "<tr><td><code>MX</code></td><td>mail server</td></tr>"
                    "<tr><td><code>TXT</code></td><td>free text, SPF, DKIM, verifications</td></tr>"
                    "<tr><td><code>NS</code></td><td>zone delegation</td></tr>"
                    "<tr><td><code>SRV</code></td><td>service + port (LDAP, XMPP, Kerberos)</td></tr>"
                    "<tr><td><code>CAA</code></td><td>which CAs may issue a cert for the domain</td></tr>"
                    "</table>"
                    "<p>The <strong>TTL</strong> says how long a resolver may cache a result. "
                    "In production: a high TTL (3600s) is efficient but migrations take hours. "
                    "A low TTL (30s) speeds up failover but multiplies query cost. The "
                    "<em>health-checked</em> standard: low TTL + an authority that removes "
                    "unhealthy IPs (Route 53, Cloudflare).</p>"

                    "<h3>6. Toolbox: the tools that solve 95% of problems</h3>"
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

                    "<h3>7. Anatomy of an HTTPS request</h3>"
                    "<p>What <em>actually</em> happens when you run "
                    "<code>curl https://api.example.com</code>:</p>"
                    "<ol>"
                    "<li><strong>DNS</strong>: resolves <code>api.example.com</code> → IP "
                    "(cache miss = ~5-50ms; hit = sub-ms).</li>"
                    "<li><strong>TCP handshake</strong>: SYN/SYN-ACK/ACK = 1 RTT.</li>"
                    "<li><strong>TLS handshake</strong>: 1-2 RTTs on TLS 1.3 (1 RTT in the "
                    "common case, 0-RTT on a resumed session). This is where the certificate "
                    "is validated.</li>"
                    "<li><strong>HTTP request</strong>: sends headers and (if POST) a body.</li>"
                    "<li><strong>Server processing</strong>: the app processes it.</li>"
                    "<li><strong>HTTP response</strong>: reaches the client.</li>"
                    "</ol>"
                    "<p>When someone says 'the API is slow', you need to know which of these "
                    "steps it's in. <code>curl -w</code> with a custom format reveals each "
                    "one.</p>"

                    "<h3>8. NAT, proxy, load balancer, and the real-IP problem</h3>"
                    "<p>In production almost nobody talks to the server directly. There's "
                    "always a chain: Cloudflare → ALB → NLB → K8s Pod → app. Each hop can "
                    "(a) swap the source IP (NAT) or (b) preserve it via "
                    "<code>X-Forwarded-For</code>/<code>Forwarded</code>/Proxy Protocol.</p>"
                    "<p>Classic anti-pattern: blindly trusting the request's "
                    "<code>X-Forwarded-For</code> without checking how many trusted proxies "
                    "you have in front. An attacker sends <code>X-Forwarded-For: "
                    "127.0.0.1</code> and bypasses rate limiting. Mitigation: configure it on "
                    "the proxy (Nginx <code>set_real_ip_from</code>, ALB with "
                    "<code>X-Forwarded-For</code> trust hops) and never trust the header "
                    "coming straight from the client.</p>"

                    "<h3>9. Network security: what can go wrong</h3>"
                    "<ul>"
                    "<li><strong>Too many open ports</strong>: every port on "
                    "<code>0.0.0.0</code> is attack surface. Default-deny on the firewall.</li>"
                    "<li><strong>DNS without DNSSEC + cache poisoning</strong>: the classic "
                    "Kaminsky 2008 case.</li>"
                    "<li><strong>Misconfigured TLS</strong>: TLS 1.0/1.1, weak cipher suites, "
                    "leaked wildcard certificate. Use SSL Labs and the Mozilla SSL Generator.</li>"
                    "<li><strong>BGP hijacking</strong>: your prefix hijacked by another AS. "
                    "Solution: RPKI, MANRS.</li>"
                    "<li><strong>SSRF</strong>: the app talks to a user-controlled URL without "
                    "validating it, hits <code>169.254.169.254</code> (metadata) and "
                    "exfiltrates an IAM credential. <em>See Capital One 2019</em>.</li>"
                    "</ul>"

                    "<h3>10. Real case: Cloudflare 2020, the BGP outage</h3>"
                    "<p>In July 2020, Cloudflare went down for 27 minutes because a BGP "
                    "routing config update withdrew announcements for a set of prefixes. "
                    "Sites depending on Cloudflare became unreachable. Lesson: routing is "
                    "fragile; have a plan B (multi-CDN or DNS with a direct health-check to "
                    "origin).</p>"
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
                "practical_en": (
                    "(1) <code>dig +trace yourdomain.com</code>: identify each delegation "
                    "down to the authoritative. Note the TTLs.<br>"
                    "(2) On a VM, open two terminals. In one, "
                    "<code>sudo tcpdump -i any -nn -w /tmp/r.pcap port 80 or port 443</code>; "
                    "in the other, run <code>curl -v https://example.com</code>. Stop tcpdump "
                    "and open the pcap in Wireshark, identify the TCP handshake, TLS "
                    "ClientHello, ApplicationData.<br>"
                    "(3) <code>curl -w '@-' -o /dev/null -s https://example.com</code> with a "
                    "format file that prints dns/connect/ssl/ttfb/total. Repeat with another, "
                    "more distant domain and compare.<br>"
                    "(4) <code>ss -tulpn</code> on your machine: for each port, identify the "
                    "owning process and justify whether it should be open."
                ),
            },
            "materials": [
                m("Beej's Guide to Network Programming", "https://beej.us/guide/bgnet/",
                  "book", "Conceitos fundamentais com clareza.",
                  title_en="Beej's Guide to Network Programming",
                  description_en="Fundamental concepts explained clearly."),
                m("Cloudflare: O que é DNS?",
                  "https://www.cloudflare.com/learning/dns/what-is-dns/",
                  "article", "Explicação acessível.",
                  title_en="Cloudflare: What is DNS?",
                  description_en="Accessible explanation."),
                m("MDN: HTTP overview",
                  "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview",
                  "docs", "", title_en="MDN: HTTP overview", description_en=""),
                m("RFC 1180, A TCP/IP Tutorial",
                  "https://www.rfc-editor.org/rfc/rfc1180", "docs",
                  "Curto, antigo e excelente.",
                  title_en="RFC 1180, A TCP/IP Tutorial",
                  description_en="Short, old, and excellent."),
                m("Linux Network Diagnostics with ss",
                  "https://man7.org/linux/man-pages/man8/ss.8.html", "docs", "",
                  title_en="Linux Network Diagnostics with ss", description_en=""),
                m("HTTP/3 Explained (Cloudflare)",
                  "https://blog.cloudflare.com/http3-the-past-present-and-future/",
                  "article", "", title_en="HTTP/3 Explained (Cloudflare)", description_en=""),
            ],
            "questions": [
                q("Qual porta padrão do HTTPS?",
                  "443", ["80", "22", "8080"],
                  "443 é a porta well-known do HTTPS. 80 é HTTP, 22 é SSH, 8080 é uma alternativa comum em proxies.",
                  statement_en="What is the default HTTPS port?",
                  correct_en="443", wrong_en=["80", "22", "8080"],
                  explanation_en="443 is the well-known HTTPS port. 80 is HTTP, 22 is SSH, "
                  "8080 is a common alternative on proxies."),
                q("Qual protocolo é orientado a conexão?",
                  "TCP", ["UDP", "ICMP", "ARP"],
                  "TCP usa handshake e garante ordem/retransmissão. UDP é sem conexão; ICMP é "
                  "para mensagens de controle; ARP resolve MAC↔IP.",
                  statement_en="Which protocol is connection-oriented?",
                  correct_en="TCP", wrong_en=["UDP", "ICMP", "ARP"],
                  explanation_en="TCP uses a handshake and guarantees order/retransmission. "
                  "UDP is connectionless; ICMP is for control messages; ARP resolves MAC↔IP."),
                q("O que faz o comando `dig example.com`?",
                  "Consulta registros DNS para o domínio.",
                  ["Mostra a rota de rede percorrida até o destino, hop a hop.",
                   "Faz uma requisição HTTP e imprime corpo e status code.",
                   "Abre um socket TCP bruto sem passar por camada de protocolo de aplicação."],
                  "dig é a ferramenta padrão para consultar DNS, substituiu o `nslookup` em "
                  "ambientes profissionais.",
                  statement_en="What does the `dig example.com` command do?",
                  correct_en="Queries DNS records for the domain.",
                  wrong_en=["Shows the network route traveled to the destination, hop by hop.",
                            "Makes an HTTP request and prints the body and status code.",
                            "Opens a raw TCP socket without going through an application protocol layer."],
                  explanation_en="dig is the standard tool for querying DNS, it replaced "
                  "`nslookup` in professional environments."),
                q("Qual registro DNS aponta um nome para um IP IPv4?",
                  "A", ["MX", "CNAME", "AAAA"],
                  "A = IPv4, AAAA = IPv6 (4 vezes maior), CNAME = alias, MX = servidor de e-mail.",
                  statement_en="Which DNS record points a name to an IPv4 address?",
                  correct_en="A", wrong_en=["MX", "CNAME", "AAAA"],
                  explanation_en="A = IPv4, AAAA = IPv6 (4 times larger), CNAME = alias, MX = "
                  "mail server."),
                q("O que indica TTL em respostas DNS?",
                  "Por quanto tempo o resultado pode ficar em cache.",
                  ["A latência da rede medida entre cliente e servidor autoritativo.",
                   "A versão do protocolo DNS usada na consulta e resposta.",
                   "O tamanho em bytes do pacote de resposta enviado pelo servidor."],
                  "TTL alto → menos consultas mas migração lenta. TTL baixo → mais carga mas "
                  "mudanças se propagam rápido.",
                  statement_en="What does TTL indicate in DNS responses?",
                  correct_en="How long the result may stay cached.",
                  wrong_en=["The network latency measured between client and authoritative server.",
                            "The version of the DNS protocol used in the query and response.",
                            "The size in bytes of the response packet sent by the server."],
                  explanation_en="High TTL → fewer queries but slow migration. Low TTL → more "
                  "load but changes propagate fast."),
                q("Qual ferramenta lista sockets em escuta no Linux moderno?",
                  "ss -tulpn",
                  ["ifconfig -a", "ipset list", "route -n"],
                  "netstat foi substituído por ss em distros modernas. -tulpn lista TCP, UDP, "
                  "listening, processo e numérico.",
                  statement_en="Which tool lists listening sockets on modern Linux?",
                  correct_en="ss -tulpn",
                  wrong_en=["ifconfig -a", "ipset list", "route -n"],
                  explanation_en="netstat was replaced by ss on modern distros. -tulpn lists "
                  "TCP, UDP, listening, process, and numeric."),
                q("Qual IP é o loopback IPv4?",
                  "127.0.0.1", ["192.168.0.1", "10.0.0.1", "0.0.0.0"],
                  "127.0.0.0/8 inteiro é loopback; 0.0.0.0 representa 'todas as interfaces' ao bindar.",
                  statement_en="Which IP is the IPv4 loopback?",
                  correct_en="127.0.0.1", wrong_en=["192.168.0.1", "10.0.0.1", "0.0.0.0"],
                  explanation_en="The entire 127.0.0.0/8 block is loopback; 0.0.0.0 represents "
                  "'all interfaces' when binding."),
                q("CIDR /24 corresponde a:",
                  "Máscara 255.255.255.0",
                  ["Máscara 255.255.0.0", "Máscara 255.0.0.0", "Máscara 255.255.255.255"],
                  "Os primeiros 24 bits são rede; restam 8 bits → 256 endereços, sendo 254 usáveis "
                  "(rede + broadcast).",
                  statement_en="CIDR /24 corresponds to:",
                  correct_en="Mask 255.255.255.0",
                  wrong_en=["Mask 255.255.0.0", "Mask 255.0.0.0", "Mask 255.255.255.255"],
                  explanation_en="The first 24 bits are network; 8 bits remain → 256 addresses, "
                  "254 of them usable (network + broadcast)."),
                q("UDP é normalmente usado em:",
                  "DNS, vídeo em tempo real e streaming de baixa latência.",
                  ["Transferência confiável de arquivo ponta a ponta, sem perda de pacote no caminho.",
                   "Transação bancária, onde ordem e confirmação de entrega importam muito.",
                   "Conexão SSH interativa, que depende de fluxo ordenado e confiável de bytes."],
                  "UDP é stateless e sem retransmissão, perfeito quando latência > confiabilidade.",
                  statement_en="UDP is typically used for:",
                  correct_en="DNS, real-time video, and low-latency streaming.",
                  wrong_en=["Reliable end-to-end file transfer, with no packet loss along the way.",
                            "Bank transactions, where order and delivery confirmation matter a lot.",
                            "Interactive SSH connections, which depend on an ordered, reliable byte stream."],
                  explanation_en="UDP is stateless and has no retransmission, perfect when "
                  "latency > reliability."),
                q("O que `curl -v` mostra além do corpo?",
                  "Cabeçalhos da requisição e da resposta.",
                  ["O status code numérico da resposta HTTP recebida do servidor.",
                   "O corpo da resposta formatado como JSON legível, sem mais detalhe.",
                   "O tempo total gasto na requisição, do início até o fim."],
                  "-v também mostra o handshake TLS, redirecionamentos e tempo de cada fase. "
                  "É a ferramenta de debug HTTP universal.",
                  statement_en="What does `curl -v` show besides the body?",
                  correct_en="The request and response headers.",
                  wrong_en=["The numeric status code of the HTTP response received from the server.",
                            "The response body formatted as readable JSON, with no further detail.",
                            "The total time spent on the request, from start to finish."],
                  explanation_en="-v also shows the TLS handshake, redirects, and the timing of "
                  "each phase. It's the universal HTTP debugging tool."),
            ],
        },
        # =====================================================================
        # 1.3 Bash / Shell Scripting
        # =====================================================================
        {
            "title": "Bash/Shell Scripting",
            "title_en": "Bash/Shell Scripting",
            "summary": "Automatizar tarefas repetitivas de forma robusta e segura.",
            "summary_en": "Automating repetitive tasks in a robust and secure way.",
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
                "intro_en": (
                    "Bash is the Esperanto of Linux operations: it's everywhere, in every "
                    "container, in every CI. Knowing bash well is an immediate productivity "
                    "multiplier. Knowing bash <em>badly</em> is a recurring source of serious "
                    "vulnerabilities: amateur scripts in production leak secrets, delete the "
                    "wrong data, open up RCE.<br><br>"
                    "This lesson assumes you've already seen <code>echo</code> and "
                    "<code>if</code>. Here we go into what separates a throwaway script from "
                    "one you let run as root in production without losing sleep over it."
                ),
                "body": (
                """<h3>1. Cabeçalho seguro: o 'unsafe at any speed' do bash</h3>
<p>Todo script sério começa com a mesma combinação de três configurações:</p>
<div class="mermaid">
flowchart LR
    A["comando1"] -- "stdout, fd 1" --> B["comando2"]
    A -- "stderr, fd 2" --> T["terminal"]
    B -- "stdout, fd 1" --> F["arquivo.txt"]
    B -- "stderr, fd 2" --> T
</div>

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
                "body_en": (
                """<h3>1. Safe header: bash's 'unsafe at any speed'</h3>
<p>Every serious script starts with the same combination of three settings:</p>
<div class="mermaid">
flowchart LR
    A["comando1"] -- "stdout, fd 1" --> B["comando2"]
    A -- "stderr, fd 2" --> T["terminal"]
    B -- "stdout, fd 1" --> F["arquivo.txt"]
    B -- "stderr, fd 2" --> T
</div>

<pre><code>#!/usr/bin/env bash
set -euo pipefail
IFS=$'\\n\\t'</code></pre>
<p>Each flag closes a specific class of bug. <code>-e</code> aborts
execution on the first command that returns an error — without it,
the script simply CONTINUES after a failure, which can mean deleting
the wrong database right after a backup that silently failed.
<code>-u</code> raises an error when referencing an undefined
variable — it catches a typo before it turns into an empty string
inside <code>rm -rf $TARGET/*</code>, turning the command into
something far more destructive than intended. <code>-o pipefail</code>
makes the pipe's status reflect the WORST stage, not the last —
without it, <code>backup_db | gzip &gt; out.gz</code> returns success
even if <code>backup_db</code> failed completely, a dangerous
silence exactly where the script would most need to raise an alarm.
And <code>IFS=$'\\n\\t'</code> restricts word-splitting to newline
and tab, avoiding the classic bug of a filename with a space breaking
into unexpected pieces. For targeted debugging, temporarily enabling
<code>set -x</code> in a specific section isolates the problem
without polluting the script's entire log:</p>
<pre><code>{ set -x; comando_problematico; } 2&gt;&amp;1 | tee /tmp/debug.log
set +x</code></pre>

<h3>2. Quoting, the first rule is quote everything</h3>
<p>The most common source of bugs in bash is word-splitting and glob
expansion happening at an unexpected moment:</p>
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
<p>The practical rule is to quote EVERY variable at the moment of
expansion, except in the rare case where word-splitting is exactly
the desired behavior.</p>

<h3>3. Modern control structures</h3>
<p><code>[[ ... ]]</code> should be preferred over <code>[ ... ]</code>
whenever possible — it natively supports regex, compound operators,
and doesn't carry the classic pitfalls of <code>[ ]</code> with an
unquoted empty string:</p>
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

<h3>4. Iterating over files with 'weird' names</h3>
<p>There's basically one 100% safe way to iterate file by file
without breaking on a name with a special character: use a NUL
separator end to end:</p>
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
<p>Both "BAD" versions break silently in the face of a space, tab, or
embedded newline in the file name — the NUL separator is the only
character guaranteed to never appear in a valid file name on a
POSIX system, which makes it the only truly safe delimiter for this
purpose.</p>

<h3>5. Functions, return values, and propagated errors</h3>
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
<p>Using <code>local</code> for every variable inside a function
prevents it from leaking into the global scope by accident, an easy
side effect to forget in bash. And <code>${!var}</code> performs
indirection — it references the variable whose NAME is stored inside
<code>$var</code>, which is what allows <code>require_env</code> to
dynamically check any variable name passed as an argument.</p>

<h3>6. Trap for deterministic cleanup</h3>
<pre><code>tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT INT TERM

echo 'baixando…' &gt; "$tmp/log"
curl https://api.example.com/dump &gt; "$tmp/dump.json"
process "$tmp/dump.json"
# o trap cuida da limpeza mesmo se algo falhar</code></pre>
<p>Without <code>trap</code>, an <code>exit 1</code> partway through
the script or a Ctrl+C from the user leaves garbage accumulating in
<code>/tmp</code> — in a frequently run script, that silently fills
up disk over time, with no obvious sign until the disk is actually
full.</p>

<h3>7. Input validation, treat it as hostile</h3>
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
<p>The choice between whitelist and blacklist isn't stylistic: a
whitelist explicitly defines what is ALLOWED, so anything outside
that pattern fails by default; a blacklist tries to list what is
FORBIDDEN, and there's always some forgotten character or sequence
that slips past the list — the asymmetry between the two approaches
is what makes a whitelist structurally more secure.</p>

<h3>8. Logging with timestamps and levels</h3>
<pre><code>log() {
  local level=$1; shift
  printf '%s [%s] %s\\n' "$(date -Iseconds)" "$level" "$*" &gt;&amp;2
}

log INFO  'iniciando deploy'
log WARN  'cache vazio, baixando do registry'
log ERROR 'falha ao subir container'</code></pre>
<p>Logging to <code>stderr</code> keeps <code>stdout</code> free
exclusively for the script's USEFUL output — the part that will
eventually be piped into another command. Mixing log output and
useful output in the same stream breaks any later composition of
the script with another tool via pipe.</p>

<h3>9. Anti-patterns that cost dearly</h3>
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

<h3>10. shellcheck, shfmt, and when to move up to Python</h3>
<p><code>shellcheck</code> catches about 95% of the most common bugs
automatically, without requiring line-by-line manual review —
wiring it into CI and the editor, failing the pipeline on any
warning, turns this entire class of error into something caught
before the merge, not after the incident. <code>shfmt</code> handles
formatting in an equivalent way. Bash shines in scripts up to about
150 lines — beyond that size, or when the script needs a non-trivial
data structure, more elaborate retry/backoff logic, concurrency
beyond a simple <code>&amp;</code>, or real unit testing, maintaining
pure bash gets more and more expensive — at that point, moving up to
Python (with <code>typer</code>) or Go pays off the time invested in
the migration.</p>

<h3>11. Real case: Steam's <code>rm -rf $STEAMROOT/*</code></h3>
<p>In 2015, the Steam launcher for Linux shipped an uninstall script
literally containing <code>rm -rf "$STEAMROOT/"*</code>. When the
<code>$STEAMROOT</code> variable was empty — something that could
happen depending on how the script was invoked — the command
effectively became <code>rm -rf "/"*</code>, deleting the entire
filesystem accessible to the user, not just Steam's own files. The
bug existed in the script for years before being discovered and
publicly reported. The final fix was a single line: explicitly
validating that <code>$STEAMROOT</code> is not empty before any
destructive operation — exactly the kind of protection that
<code>set -u</code> (section 1) and input validation (section 7)
prevent structurally, instead of relying on someone remembering to
check manually in every new script.</p>"""
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
                "practical_en": (
                    "Write a script <code>analyze_logs.sh</code> that:<br>"
                    "(a) takes a directory as an argument (validated by regex);<br>"
                    "(b) uses <code>set -euo pipefail</code> and <code>trap</code> to clean up "
                    "tmp files;<br>"
                    "(c) finds the 5 largest <code>.log</code> files recursively, correctly "
                    "handling names with spaces;<br>"
                    "(d) prints statistics (total lines, ERROR/WARN/INFO) with "
                    "<code>awk</code>;<br>"
                    "(e) logs to stderr with an ISO-8601 timestamp;<br>"
                    "(f) exits with a specific non-zero code for each failure (64 input, 65 "
                    "filesystem, 66 dependency).<br>"
                    "Run <code>shellcheck -S style</code> on it until every warning is gone."
                ),
            },
            "materials": [
                m("Bash Reference Manual",
                  "https://www.gnu.org/software/bash/manual/bash.html", "docs", "",
                  title_en="Bash Reference Manual", description_en=""),
                m("Google Shell Style Guide",
                  "https://google.github.io/styleguide/shellguide.html",
                  "article", "Padrões reais de produção.",
                  title_en="Google Shell Style Guide",
                  description_en="Real-world production standards."),
                m("ShellCheck", "https://www.shellcheck.net/",
                  "tool", "Linter obrigatório para scripts bash.",
                  title_en="ShellCheck", description_en="Mandatory linter for bash scripts."),
                m("Bash Pitfalls (Greg's Wiki)",
                  "https://mywiki.wooledge.org/BashPitfalls", "article",
                  "Catálogo de erros clássicos.",
                  title_en="Bash Pitfalls (Greg's Wiki)",
                  description_en="Catalog of classic mistakes."),
                m("Advanced Bash-Scripting Guide",
                  "https://tldp.org/LDP/abs/html/", "book", "",
                  title_en="Advanced Bash-Scripting Guide", description_en=""),
                m("explainshell.com", "https://explainshell.com/",
                  "tool", "Quebra qualquer linha de shell em pedaços com explicação.",
                  title_en="explainshell.com",
                  description_en="Breaks any shell line into pieces with an explanation."),
            ],
            "questions": [
                q("Para que serve `set -e` em um script bash?",
                  "Aborta a execução se um comando retornar erro.",
                  ["Ativa modo verboso, imprimindo cada comando antes de executá-lo.",
                   "Define uma variável de ambiente visível para os subprocessos do script.",
                   "Roda o script inteiro num processo separado, em paralelo com o terminal atual."],
                  "Sem -e, um falha intermediária passa despercebida e o script continua "
                  "como se tudo desse certo.",
                  statement_en="What does `set -e` do in a bash script?",
                  correct_en="Aborts execution if a command returns an error.",
                  wrong_en=["Enables verbose mode, printing each command before executing it.",
                            "Defines an environment variable visible to the script's subprocesses.",
                            "Runs the entire script in a separate process, in parallel with the current terminal."],
                  explanation_en="Without -e, an intermediate failure goes unnoticed and the "
                  "script continues as if everything went fine."),
                q("Qual a forma correta de citar uma variável?",
                  "echo \"$var\"", ["echo $var", "echo '$var'", "echo `var`"],
                  "Aspas duplas evitam word splitting e expansão de glob mantendo a expansão "
                  "da variável.",
                  statement_en="What is the correct way to quote a variable?",
                  correct_en="echo \"$var\"",
                  wrong_en=["echo $var", "echo '$var'", "echo `var`"],
                  explanation_en="Double quotes avoid word splitting and glob expansion while "
                  "still expanding the variable."),
                q("O que `pipefail` faz?",
                  "Faz o pipeline falhar se qualquer comando intermediário falhar.",
                  ["Reinicia o pipe inteiro automaticamente após qualquer comando interno travar.",
                   "Ignora e descarta qualquer código de erro vindo de dentro do pipe.",
                   "Faz o pipeline retornar sucesso mesmo quando algo dentro dele falhou de verdade."],
                  "Sem pipefail, `cmd1 | cmd2` retorna o status de cmd2 mesmo que cmd1 tenha "
                  "explodido, fonte recorrente de bugs silenciosos.",
                  statement_en="What does `pipefail` do?",
                  correct_en="Makes the pipeline fail if any intermediate command fails.",
                  wrong_en=["Automatically restarts the whole pipe after any internal command hangs.",
                            "Ignores and discards any error code coming from inside the pipe.",
                            "Makes the pipeline return success even when something inside it truly failed."],
                  explanation_en="Without pipefail, `cmd1 | cmd2` returns cmd2's status even if "
                  "cmd1 blew up, a recurring source of silent bugs."),
                q("Como capturar a saída de um comando em uma variável?",
                  "result=$(comando)", ["result=`comando`", "result=$comando", "result=>'comando'"],
                  "Backticks aninham mal e são considerados legados; preferir $(...).",
                  statement_en="How do you capture a command's output into a variable?",
                  correct_en="result=$(command)",
                  wrong_en=["result=`command`", "result=$command", "result=>'command'"],
                  explanation_en="Backticks nest poorly and are considered legacy; prefer "
                  "$(...)."),
                q("Qual comando lista todos os scripts shell num diretório recursivamente?",
                  "find . -type f -name '*.sh'",
                  ["grep -rl '*.sh' /home/usuario", "ls -la -R --color=auto *.sh", "tree --shell -P '*.sh' -fi"],
                  "ls não recursa por padrão; grep busca conteúdo, não nome. find é a ferramenta correta.",
                  statement_en="Which command lists all shell scripts in a directory recursively?",
                  correct_en="find . -type f -name '*.sh'",
                  wrong_en=["grep -rl '*.sh' /home/user", "ls -la -R --color=auto *.sh", "tree --shell -P '*.sh' -fi"],
                  explanation_en="ls doesn't recurse by default; grep searches content, not "
                  "names. find is the right tool."),
                q("Por que `eval` com input externo é perigoso?",
                  "Permite execução arbitrária de código se a string vier de fora.",
                  ["Deixa o script mais lento, porque precisa reinterpretar a string a cada execução.",
                   "Não funciona em versões antigas do macOS que ainda usam bash 3.2.",
                   "Gera erro de sintaxe quando a string contém aspas desbalanceadas dentro dela."],
                  "Eval interpreta a string como comando bash, então qualquer coisa do tipo "
                  "`; rm -rf /` no input é executada.",
                  statement_en="Why is `eval` with external input dangerous?",
                  correct_en="It allows arbitrary code execution if the string comes from outside.",
                  wrong_en=["It makes the script slower, because it has to reinterpret the string on every run.",
                            "It doesn't work on old macOS versions that still use bash 3.2.",
                            "It raises a syntax error when the string contains unbalanced quotes inside it."],
                  explanation_en="Eval interprets the string as a bash command, so anything "
                  "like `; rm -rf /` in the input gets executed."),
                q("Como passar argumento posicional em script bash?",
                  "$1, $2, $3...",
                  ["%1, %2, %3...", "&1, &2, &3...", "arg1, arg2, arg3..."],
                  "$@ tem todos os argumentos; $# o número deles. Cite com aspas: \"$@\".",
                  statement_en="How do you pass positional arguments in a bash script?",
                  correct_en="$1, $2, $3...",
                  wrong_en=["%1, %2, %3...", "&1, &2, &3...", "arg1, arg2, arg3..."],
                  explanation_en="$@ has all the arguments; $# has their count. Quote it as "
                  "\"$@\"."),
                q("Qual ferramenta detecta bugs comuns em scripts?",
                  "shellcheck",
                  ["eslint --fix", "rubocop --auto", "pylint --errors-only"],
                  "shellcheck é o linter de fato para bash/sh, integra com a maioria das IDEs.",
                  statement_en="Which tool detects common bugs in scripts?",
                  correct_en="shellcheck",
                  wrong_en=["eslint --fix", "rubocop --auto", "pylint --errors-only"],
                  explanation_en="shellcheck is the de facto linter for bash/sh, it integrates "
                  "with most IDEs."),
                q("`[[ -z \"$x\" ]]` é verdadeiro quando:",
                  "x está vazio ou não definida.",
                  ["x é igual a 0, um teste numérico diferente (-eq), não de string.",
                   "x aponta para um arquivo existente, o que -f testaria, não -z.",
                   "x aponta para um diretório existente, o que -d testaria, não -z."],
                  "-z testa string vazia. -n é o oposto. Use sempre as aspas para evitar erro de sintaxe.",
                  statement_en="`[[ -z \"$x\" ]]` is true when:",
                  correct_en="x is empty or unset.",
                  wrong_en=["x equals 0, a different numeric test (-eq), not a string test.",
                            "x points to an existing file, which -f would test, not -z.",
                            "x points to an existing directory, which -d would test, not -z."],
                  explanation_en="-z tests for an empty string. -n is the opposite. Always use "
                  "quotes to avoid a syntax error."),
                q("Qual o jeito recomendado de iterar arquivos com espaços no nome?",
                  "find ... -print0 | xargs -0",
                  ["for f in $(ls -1 *.sh)", "echo * | tr ' ' '\\n' | cat", "ls -1 | while read -r f; do"],
                  "-print0/-0 separa por NUL em vez de espaço/quebra-de-linha, único jeito "
                  "100% seguro com nomes arbitrários.",
                  statement_en="What is the recommended way to iterate over files with spaces in their names?",
                  correct_en="find ... -print0 | xargs -0",
                  wrong_en=["for f in $(ls -1 *.sh)", "echo * | tr ' ' '\\n' | cat", "ls -1 | while read -r f; do"],
                  explanation_en="-print0/-0 separates by NUL instead of space/newline, the "
                  "only 100% safe way with arbitrary names."),
            ],
        },
        # =====================================================================
        # 1.4 SSH
        # =====================================================================
        {
            "title": "SSH & Chaves Criptográficas",
            "title_en": "SSH & Cryptographic Keys",
            "summary": "Acesso remoto seguro e gestão de identidades com chaves assimétricas.",
            "summary_en": "Secure remote access and identity management with asymmetric keys.",
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
                "intro_en": (
                    "SSH is probably the single most important protocol in day-to-day "
                    "DevSecOps work. Logging into a server, doing a git push, configuring "
                    "ansible, deploying: all of that typically runs over SSH. And it's where a "
                    "lot of silly vulnerabilities pile up: weak keys, keys shared between "
                    "humans, an <code>authorized_keys</code> that never rotates, an ignored "
                    "<code>known_hosts</code>, agent forwarding going to an untrusted "
                    "server.<br><br>"
                    "This lesson covers the mental model of asymmetric cryptography as we use "
                    "it in SSH, server hardening (sshd_config), operational client usage, and "
                    "why you should move away from manual <code>authorized_keys</code> and "
                    "toward an SSH CA in any serious environment."
                ),
                "body": (
                    "<h3>1. Modelo mental de criptografia assimétrica</h3>"
                    "<p>Cada lado tem um par de chaves matemáticamente ligadas:</p>"
                    """
<div class="mermaid">
sequenceDiagram
    participant Cliente
    participant Servidor
    Cliente->>Servidor: Pedido de conexão
    Servidor-->>Cliente: Desafio com nonce aleatório
    Cliente->>Cliente: Assina o nonce com a chave privada
    Cliente->>Servidor: Envia a assinatura
    Servidor->>Servidor: Verifica com a chave pública em authorized_keys
    Servidor-->>Cliente: Acesso concedido, senha nunca trafegou
</div>
"""
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
                "body_en": (
                    "<h3>1. Mental model of asymmetric cryptography</h3>"
                    "<p>Each side has a pair of mathematically linked keys:</p>"
                    """
<div class="mermaid">
sequenceDiagram
    participant Cliente
    participant Servidor
    Cliente->>Servidor: Pedido de conexão
    Servidor-->>Cliente: Desafio com nonce aleatório
    Cliente->>Cliente: Assina o nonce com a chave privada
    Cliente->>Servidor: Envia a assinatura
    Servidor->>Servidor: Verifica com a chave pública em authorized_keys
    Servidor-->>Cliente: Acesso concedido, senha nunca trafegou
</div>
"""
                    "<ul>"
                    "<li>The <strong>private key</strong> never leaves its owner. It's secret.</li>"
                    "<li>The <strong>public key</strong> can be freely distributed.</li>"
                    "</ul>"
                    "<p>What one encrypts, the other decrypts (and vice versa). In SSH:</p>"
                    "<ol>"
                    "<li>The client proves possession of the private key by signing a "
                    "challenge sent by the server.</li>"
                    "<li>The server verifies the signature with the public key (which is in "
                    "the user's <code>~/.ssh/authorized_keys</code>).</li>"
                    "<li>After authentication, both sides derive <strong>symmetric</strong> "
                    "keys (AES, ChaCha20) to encrypt the session, asymmetric crypto is only "
                    "used to establish the session, not for the traffic itself (it would be "
                    "too slow).</li>"
                    "</ol>"
                    "<p>The server also has its own pair: the server's public key (host key) "
                    "goes into your <code>~/.ssh/known_hosts</code> on first connection. If "
                    "next time it's different, the client <em>refuses</em> with "
                    "<code>WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED</code>, it could be "
                    "a MITM or a legitimate server rebuild.</p>"

                    "<h3>2. Generating modern keys, Ed25519</h3>"
                    "<p>In 2025+ the standard is <strong>Ed25519</strong>:</p>"
                    "<pre><code>ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519 -C 'meu@email.com'</code></pre>"
                    "<ul>"
                    "<li><code>-t ed25519</code>: modern elliptic curve; public key of "
                    "~68 bytes.</li>"
                    "<li><code>-a 100</code>: 100 rounds of KDF for the passphrase (slower "
                    "against brute force).</li>"
                    "<li><code>-C</code>: comment (just a marker, used to identify the key in "
                    "<code>authorized_keys</code>).</li>"
                    "</ul>"
                    "<p>Always protect it with a passphrase. Without one, anyone with access "
                    "to your disk has access to all your servers.</p>"
                    "<p>RSA-2048 is being retired; if you need RSA for compatibility, use "
                    "≥ 3072 bits. ECDSA has caveats (NIST curves), prefer Ed25519.</p>"

                    "<h3>3. ssh-agent: type the passphrase once per session</h3>"
                    "<pre><code>eval $(ssh-agent -s)\n"
                    "ssh-add -t 4h ~/.ssh/id_ed25519     # libera por 4 horas\n"
                    "ssh-add -l                           # lista chaves carregadas\n"
                    "ssh-add -D                           # remove todas (logout)</code></pre>"
                    "<p>The agent holds the decrypted key in memory and talks to the SSH "
                    "client over a Unix socket (<code>$SSH_AUTH_SOCK</code>). On modern "
                    "desktops (macOS, GNOME), there are integrated native agents.</p>"
                    "<p><strong>Be careful with agent forwarding</strong> "
                    "(<code>ssh -A host</code>): the destination server can use your keys to "
                    "connect elsewhere while the session is open. If it's compromised, it "
                    "becomes a pivot. Use <code>ProxyJump</code> instead of <code>-A</code> "
                    "whenever possible:</p>"
                    "<pre><code>ssh -J bastion.example.com app-01.internal</code></pre>"

                    "<h3>4. ~/.ssh/config, configuration that saves hours</h3>"
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
                    "<p><code>IdentitiesOnly yes</code> is mandatory if you have several keys: "
                    "otherwise, the client tries all of them and triggers "
                    "<code>MaxAuthTries</code> before reaching the correct one.</p>"

                    "<h3>5. Hardening the server: sshd_config</h3>"
                    "<p>In <code>/etc/ssh/sshd_config</code> (or a drop-in under "
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
                    "<p>Always test before applying:</p>"
                    "<pre><code>sudo sshd -t                              # valida sintaxe\n"
                    "sudo systemctl reload sshd                 # recarrega sem dropar conexões\n"
                    "# em outra janela já aberta, tente novo login antes de fechar a primeira</code></pre>"

                    "<h3>6. Permission pitfalls</h3>"
                    "<p>OpenSSH is strict:</p>"
                    "<pre><code>chmod 700 ~/.ssh\n"
                    "chmod 600 ~/.ssh/authorized_keys\n"
                    "chmod 600 ~/.ssh/id_ed25519\n"
                    "chmod 644 ~/.ssh/id_ed25519.pub\n"
                    "chown -R $USER:$USER ~/.ssh</code></pre>"
                    "<p>If anything is more open than that, sshd <em>silently</em> ignores the "
                    "key, and you only find out by checking "
                    "<code>journalctl -u sshd</code>. It's the most frustrating source of SSH "
                    "bugs.</p>"

                    "<h3>7. SSH with certificates (SSH CA), real scale</h3>"
                    "<p>At large fleet scale, distributing <code>authorized_keys</code> "
                    "manually becomes a nightmare: a new employee's key needs to go into N "
                    "hosts; departure needs it removed from N hosts; rotation is a very rare "
                    "practice. Solution: <strong>SSH certificates</strong>.</p>"
                    "<p>How it works:</p>"
                    "<ol>"
                    "<li>You have a <strong>CA</strong> (a dedicated key pair) with the private "
                    "key well guarded (Vault, HSM).</li>"
                    "<li>The server is configured with "
                    "<code>TrustedUserCAKeys /etc/ssh/ca.pub</code>, trusting any key signed "
                    "by the CA.</li>"
                    "<li>The employee requests a certificate from the CA (authenticating via "
                    "SSO/MFA); receives a certificate with a short TTL (1h-8h) and a principal "
                    "of <code>deploy</code> or <code>ops</code>.</li>"
                    "<li>SSH presents the certificate, the server validates the CA's signature "
                    "and extracts the principal.</li>"
                    "</ol>"
                    "<p>Advantages: instant central revocation (CRL), zero "
                    "<code>authorized_keys</code> management on the server, forensically "
                    "useful logging (the employee's <code>certificate ID</code>), short TTL "
                    "(a leaked key expires on its own).</p>"
                    "<p>Tools: <strong>HashiCorp Vault</strong> (SSH secrets engine), "
                    "<strong>Smallstep step-ca</strong>, <strong>Teleport</strong>, "
                    "<strong>BastionZero</strong>.</p>"

                    "<h3>8. SSH and CI/CD</h3>"
                    "<p>Classic anti-pattern: a long-lived SSH key stored as a GitHub "
                    "Actions/GitLab secret and used to <code>scp</code> to the server. The "
                    "key leaks, the attacker gets permanent access. Better patterns:</p>"
                    "<ul>"
                    "<li><strong>OIDC + SSH CA</strong>: the pipeline exchanges a JWT token "
                    "(with claims for repo, branch, and SHA) for an ephemeral SSH certificate. "
                    "Vault and step-ca support this.</li>"
                    "<li><strong>Self-hosted runner inside the VPC</strong>: the pipeline "
                    "talks to a private host, without exposing SSH to the internet.</li>"
                    "<li><strong>Pull-based deploy</strong>: ArgoCD/Flux pulls from Git "
                    "instead of the pipeline pushing.</li>"
                    "</ul>"

                    "<h3>9. Real case: the GitHub.com 2023 incident (RSA host key)</h3>"
                    "<p>In March 2023, GitHub announced it had accidentally exposed its "
                    "private RSA host key in a public repository for hours, anyone could "
                    "MITM SSH connections to <code>github.com</code> via RSA. The fix was to "
                    "rotate the host key and ask millions of users to update "
                    "<code>known_hosts</code>. Lessons: (a) the host key matters a great deal; "
                    "(b) have a rotation plan; (c) Ed25519 remained intact, algorithm "
                    "diversity helped.</p>"

                    "<h3>10. Recurring anti-patterns</h3>"
                    "<ul>"
                    "<li>Sharing keys between humans ('the team's key').</li>"
                    "<li>Not using a passphrase 'because it's annoying', the agent solves it.</li>"
                    "<li>Blindly accepting a host key in scripts "
                    "(<code>StrictHostKeyChecking=no</code>) without registering it via "
                    "<code>ssh-keyscan</code> + out-of-band verification.</li>"
                    "<li>Enabling <code>PermitRootLogin yes</code> 'temporarily' and "
                    "forgetting about it.</li>"
                    "<li>Leaving <code>AllowAgentForwarding yes</code> as the default on an "
                    "exposed server.</li>"
                    "<li>Never rotating, a 2017 key still in the 2025 "
                    "<code>authorized_keys</code>.</li>"
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
                "practical_en": (
                    "On two VMs:<br>"
                    "(1) Generate an Ed25519 key with a passphrase: "
                    "<code>ssh-keygen -t ed25519 -a 100</code>.<br>"
                    "(2) Copy it to the other VM with "
                    "<code>ssh-copy-id user@host</code>; verify permissions.<br>"
                    "(3) On the server, edit <code>/etc/ssh/sshd_config.d/99-hardening.conf</code> "
                    "with <code>PasswordAuthentication no</code>, "
                    "<code>PermitRootLogin no</code>, <code>MaxAuthTries 3</code>, "
                    "<code>AllowUsers $YOUR_USER</code>. Validate with <code>sshd -t</code> and "
                    "reload with <code>systemctl reload sshd</code>.<br>"
                    "(4) <strong>Do not close the current session</strong>. In another "
                    "terminal, try logging in with a password (should fail) and with the key "
                    "(should succeed).<br>"
                    "(5) <code>journalctl -u sshd -n 50</code> and check the audit trail.<br>"
                    "(6) Bonus: set up a <code>~/.ssh/config</code> with a host alias and "
                    "<code>ProxyJump</code>, then <code>ssh app01</code> should traverse the "
                    "bastion on its own."
                ),
            },
            "materials": [
                m("OpenSSH Manual", "https://www.openssh.com/manual.html", "docs", "",
                  title_en="OpenSSH Manual", description_en=""),
                m("SSH.com: Public Key Authentication",
                  "https://www.ssh.com/academy/ssh/public-key-authentication",
                  "article", "", title_en="SSH.com: Public Key Authentication", description_en=""),
                m("DigitalOcean: SSH Essentials",
                  "https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys",
                  "article", "", title_en="DigitalOcean: SSH Essentials", description_en=""),
                m("Mozilla SSH Guidelines",
                  "https://infosec.mozilla.org/guidelines/openssh",
                  "article", "Recomendações endurecidas.",
                  title_en="Mozilla SSH Guidelines",
                  description_en="Hardened recommendations."),
                m("Why Ed25519",
                  "https://blog.g3rt.nl/upgrade-your-ssh-keys.html", "article", "",
                  title_en="Why Ed25519", description_en=""),
                m("Smallstep: SSH certificates",
                  "https://smallstep.com/blog/use-ssh-certificates/",
                  "article", "Sair de authorized_keys para PKI.",
                  title_en="Smallstep: SSH certificates",
                  description_en="Moving from authorized_keys to PKI."),
            ],
            "questions": [
                q("Qual algoritmo é recomendado para novas chaves SSH?",
                  "Ed25519",
                  ["DSA", "RSA-1024", "MD5"],
                  "Ed25519 oferece chave curta, assinatura rápida e segurança equivalente a RSA-3072+. "
                  "DSA está depreciado, RSA-1024 é fraco e MD5 nem é algoritmo de chave.",
                  statement_en="Which algorithm is recommended for new SSH keys?",
                  correct_en="Ed25519",
                  wrong_en=["DSA", "RSA-1024", "MD5"],
                  explanation_en="Ed25519 offers a short key, fast signing, and security "
                  "equivalent to RSA-3072+. DSA is deprecated, RSA-1024 is weak, and MD5 isn't "
                  "even a key algorithm."),
                q("Onde fica a chave pública do usuário no servidor?",
                  "~/.ssh/authorized_keys",
                  ["~/.bashrc.d/keys.conf.bak", "/root/keys.pub.backup.old", "/etc/passwd.d/keys.backup"],
                  "Cada usuário do servidor mantém suas chaves autorizadas no próprio home.",
                  statement_en="Where does the user's public key live on the server?",
                  correct_en="~/.ssh/authorized_keys",
                  wrong_en=["~/.bashrc.d/keys.conf.bak", "/root/keys.pub.backup.old", "/etc/passwd.d/keys.backup"],
                  explanation_en="Each server user keeps their authorized keys in their own "
                  "home directory."),
                q("Qual diretiva no `sshd_config` desabilita login com senha?",
                  "PasswordAuthentication no",
                  ["DenyPassword yes always", "DisablePassword on strict", "AllowPassword false global"],
                  "Após mudar, é preciso recarregar o sshd (`systemctl reload sshd`).",
                  statement_en="Which directive in `sshd_config` disables password login?",
                  correct_en="PasswordAuthentication no",
                  wrong_en=["DenyPassword yes always", "DisablePassword on strict", "AllowPassword false global"],
                  explanation_en="After changing it, you need to reload sshd "
                  "(`systemctl reload sshd`)."),
                q("O que `ssh-agent` resolve?",
                  "Mantém a chave privada decifrada em memória durante a sessão.",
                  ["Substitui completamente o pacote openssh-server no sistema.",
                   "Sincroniza automaticamente as chaves entre as máquinas do mesmo usuário.",
                   "Gera uma chave nova a cada vez que uma sessão SSH é iniciada pelo usuário."],
                  "Sem agent, você teria que digitar a passphrase a cada conexão. Com forwarding, "
                  "use com cuidado: agent forwarding mal configurado vaza a identidade.",
                  statement_en="What problem does `ssh-agent` solve?",
                  correct_en="It keeps the decrypted private key in memory during the session.",
                  wrong_en=["It completely replaces the openssh-server package on the system.",
                            "It automatically syncs keys between the same user's machines.",
                            "It generates a new key every time an SSH session is started by the user."],
                  explanation_en="Without the agent, you'd have to type the passphrase on "
                  "every connection. With forwarding, use it carefully: misconfigured agent "
                  "forwarding leaks the identity."),
                q("Qual permissão é exigida pelo OpenSSH para `~/.ssh/authorized_keys`?",
                  "600 (rw apenas para o dono).",
                  ["777, que dá leitura e escrita para qualquer usuário do sistema.",
                   "644, que ainda permite outros usuários lerem o conteúdo da chave.",
                   "400 com dono root, inacessível até para o próprio usuário do serviço."],
                  "O sshd recusa silenciosamente a chave se o arquivo for legível por outros.",
                  statement_en="Which permission does OpenSSH require for `~/.ssh/authorized_keys`?",
                  correct_en="600 (read/write for the owner only).",
                  wrong_en=["777, which gives read and write to any user on the system.",
                            "644, which still lets other users read the key's contents.",
                            "400 owned by root, inaccessible even to the service's own user."],
                  explanation_en="sshd silently refuses the key if the file is readable by "
                  "others."),
                q("Como copiar a chave pública para o servidor?",
                  "ssh-copy-id user@host",
                  ["ssh --send-key user@host", "rsync key user@host:~/", "scp -p chave.pub user@host"],
                  "ssh-copy-id já faz append em authorized_keys e ajusta permissões.",
                  statement_en="How do you copy the public key to the server?",
                  correct_en="ssh-copy-id user@host",
                  wrong_en=["ssh --send-key user@host", "rsync key user@host:~/", "scp -p key.pub user@host"],
                  explanation_en="ssh-copy-id already appends to authorized_keys and adjusts "
                  "permissions."),
                q("Qual variável de ambiente o ssh-agent define?",
                  "SSH_AUTH_SOCK",
                  ["SSH_TOKEN_PATH", "SSH_PASS_AGENT", "SSH_KEY_SOCKET"],
                  "É o socket Unix por onde o cliente fala com o agent.",
                  statement_en="Which environment variable does ssh-agent set?",
                  correct_en="SSH_AUTH_SOCK",
                  wrong_en=["SSH_TOKEN_PATH", "SSH_PASS_AGENT", "SSH_KEY_SOCKET"],
                  explanation_en="It's the Unix socket through which the client talks to the "
                  "agent."),
                q("O que é uma chave de host em SSH?",
                  "Chave que identifica o servidor para evitar MITM.",
                  ["Chave temporária gerada para um usuário convidado sem privilégio real.",
                   "Chave dedicada só a criptografar o conteúdo dos pacotes trafegados.",
                   "Chave usada exclusivamente pela conta root para tarefa administrativa."],
                  "Na primeira conexão, você aceita a chave; depois ela vai pra known_hosts. "
                  "Se mudar inesperadamente, é sinal de MITM (ou rebuild legítimo).",
                  statement_en="What is a host key in SSH?",
                  correct_en="A key that identifies the server to prevent MITM.",
                  wrong_en=["A temporary key generated for a guest user with no real privilege.",
                            "A key dedicated only to encrypting the content of packets in transit.",
                            "A key used exclusively by the root account for administrative tasks."],
                  explanation_en="On the first connection, you accept the key; afterward it "
                  "goes into known_hosts. If it changes unexpectedly, that's a sign of MITM "
                  "(or a legitimate rebuild)."),
                q("Por que evitar PermitRootLogin yes?",
                  "Aumenta a superfície de ataque dando acesso direto a um usuário onipotente.",
                  ["Bloqueia completamente o serviço sshd assim que a opção é ativada.",
                   "Reduz a performance geral do servidor por causa da checagem extra de root.",
                   "Deixa de funcionar corretamente quando combinado com uma chave Ed25519 mais recente."],
                  "Use um usuário comum com sudo; tenha rastreabilidade individual no audit log.",
                  statement_en="Why avoid PermitRootLogin yes?",
                  correct_en="It increases the attack surface by giving direct access to an all-powerful user.",
                  wrong_en=["It completely blocks the sshd service as soon as the option is enabled.",
                            "It reduces overall server performance due to the extra root check.",
                            "It stops working correctly when combined with a newer Ed25519 key."],
                  explanation_en="Use a regular user with sudo; keep individual traceability in "
                  "the audit log."),
                q("Qual a vantagem de SSH com certificados?",
                  "Eliminar autorização chave-a-chave em cada servidor; rotação centralizada.",
                  ["Continua funcionando mesmo com a rede completamente indisponível no momento.",
                   "Permite senha mais curta do que a exigida pela política atual da empresa.",
                   "Elimina a necessidade de instalar e manter o próprio daemon sshd."],
                  "Servidores confiam na CA. Emite certificado com TTL de horas e revoga "
                  "centralmente, escala muito melhor que authorized_keys.",
                  statement_en="What is the advantage of SSH with certificates?",
                  correct_en="Eliminating key-by-key authorization on each server; centralized rotation.",
                  wrong_en=["It keeps working even when the network is completely unavailable at the moment.",
                            "It allows a shorter password than the company's current policy requires.",
                            "It removes the need to install and maintain the sshd daemon itself."],
                  explanation_en="Servers trust the CA. It issues a certificate with a TTL of "
                  "hours and revokes centrally, scaling far better than authorized_keys."),
            ],
        },
        # =====================================================================
        # 1.5 PoLP
        # =====================================================================
        {
            "title": "Princípio do Privilégio Mínimo (PoLP)",
            "title_en": "Principle of Least Privilege (PoLP)",
            "summary": "Por que nunca rodar nada como 'root', e como aplicar isso em todos os níveis.",
            "summary_en": "Why you should never run anything as 'root', and how to apply that at every level.",
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
                "intro_en": (
                    "The Principle of Least Privilege (PoLP) is the simple and devastating "
                    "idea: every identity, human, service, process, IAM role, service account, "
                    "should have <em>exactly</em> the privileges its function needs. Nothing "
                    "more.<br><br>"
                    "Almost every privilege escalation in real incidents starts by exploiting "
                    "an identity that had more power than it needed. Capital One (2019), "
                    "SolarWinds (2020), Uber (2022), they all have a PoLP violation somewhere "
                    "on the attack's critical path.<br><br>"
                    "This lesson shows how to apply PoLP across five layers: OS users, sudo, "
                    "systemd, containers (Docker/K8s), and cloud (IAM)."
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
<div class="mermaid">
flowchart TD
    subgraph SemPoLP ["Sem PoLP"]
        U1["Credencial única"] --> A1["Lê e escreve no banco inteiro"]
        U1 --> A2["Administra toda a infraestrutura"]
        U1 --> A3["Lê todos os segredos do cofre"]
    end
    subgraph ComPoLP ["Com PoLP"]
        U2["Credencial do serviço de billing"] --> B1["Só lê a tabela de faturas"]
    end
</div>


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
                "body_en": (
                """<h3>1. Why PoLP is foundational</h3>
<p>The most useful way to think about PoLP is as
<strong>blast radius</strong> control: how much is compromised the
moment a specific identity leaks. If a web application carries an
<code>AdministratorAccess</code> credential on AWS and is compromised,
the attacker controls the entire account — they take down the database,
exfiltrate an S3 bucket, spin up their own instance to mine crypto on
the company card. If that same application had only
<code>s3:GetObject</code> on a specific bucket, the leak fits in a
single line of an incident report, not a headline. PoLP does not
PREVENT compromise itself — it is defense in depth put into practice,
limiting the CONSEQUENCE of something that will eventually happen
anyway. That is exactly what separates an embarrassing incident from a
full-blown reputation crisis.</p>
<div class="mermaid">
flowchart TD
    subgraph SemPoLP ["Sem PoLP"]
        U1["Credencial única"] --> A1["Lê e escreve no banco inteiro"]
        U1 --> A2["Administra toda a infraestrutura"]
        U1 --> A3["Lê todos os segredos do cofre"]
    end
    subgraph ComPoLP ["Com PoLP"]
        U2["Credencial do serviço de billing"] --> B1["Só lê a tabela de faturas"]
    end
</div>


<h3>2. PoLP on the Linux host: dedicated users per service</h3>
<p>Every service — nginx, postgres, the application itself — should
have its own system user, never shared:</p>
<pre><code>useradd --system --shell /usr/sbin/nologin --home-dir /var/lib/app app
chown -R app:app /opt/app /var/lib/app /var/log/app</code></pre>
<p>That brings four concrete advantages: compromising one application
does not automatically grant access to any other service on the same
machine; permission is granular enough that the application cannot even
READ <code>/etc/postgres</code>, for example; per-user auditing becomes
trivial (<code>journalctl
_UID=$(id -u app)</code> isolates exactly what that process did); and
resource limits (ulimit, cgroup) can be applied per user individually,
without affecting the other services on the same machine.</p>

<h3>3. systemd hardening: the layer many people ignore</h3>
<p>In <code>/etc/systemd/system/app.service</code>:</p>
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
<p>Each of these directives closes a specific escalation vector —
<code>NoNewPrivileges</code>, for example, prevents a compromised
process from gaining MORE privilege than it already had via a setuid
binary found on the system. To see exactly where a unit already stands,
systemd itself offers a built-in auditor:</p>
<pre><code>systemd-analyze security app.service</code></pre>
<p>It returns a score from 0 to 10 with concrete suggestions for what
still needs hardening — the LOWER the score, the more securely the
service is already configured.</p>

<h3>4. sudo, but with judgment</h3>
<p>The entry <code>ALL=(ALL:ALL) ALL</code> is the most common shortcut
and also the worst possible one — it grants exactly the opposite of
what PoLP asks for. In <code>/etc/sudoers.d/deploy</code>, the granular
alternative grants only the specific command that is needed:</p>
<pre><code># Usuário deploy só pode reiniciar o nginx, sem senha
deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart nginx
deploy ALL=(root) NOPASSWD: /usr/bin/systemctl reload nginx

# Negar shell escapes
Defaults:deploy !requiretty
Defaults:deploy log_year, logfile=/var/log/sudo-deploy.log</code></pre>
<p>Always editing with <code>visudo -f /etc/sudoers.d/arquivo</code> is
a structural protection of its own: the command VALIDATES syntax before
saving — without that validation, a simple typo can leave the entire
system with nobody able to use sudo until someone fixes it via physical
access or an emergency console.</p>

<h3>5. PoLP in Docker containers</h3>
<pre><code># Dockerfile
FROM python:3.12-slim
RUN useradd --uid 10001 --system --no-create-home app
WORKDIR /app
COPY --chown=app:app . .
RUN pip install --no-cache-dir -r requirements.txt
USER app                          # nunca rode como root
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.wsgi"]</code></pre>
<p>At container runtime there is still room to go beyond what the
Dockerfile already guarantees:</p>
<pre><code>docker run --rm \\
  --user 10001:10001 \\
  --read-only \\
  --tmpfs /tmp \\
  --cap-drop=ALL \\
  --cap-add=NET_BIND_SERVICE \\
  --security-opt=no-new-privileges \\
  --pids-limit 200 \\
  -p 8000:8000 myapp:1.0</code></pre>
<p>Combining <code>--cap-drop=ALL</code> with a single specific
<code>--cap-add</code> (here, only
<code>NET_BIND_SERVICE</code>, needed solely to bind ports below 1024)
illustrates PoLP in action: instead of granting the full set of kernel
capabilities, grant exactly the one capability the application actually
needs.</p>

<h3>6. PoLP in Kubernetes (securityContext)</h3>
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
<p>Pod Security Standards, in <code>restricted</code> mode, apply this
entire pattern FORCIBLY on every deploy inside the namespace, instead of
depending on each team remembering to configure it manually:</p>
<pre><code>kubectl label ns app pod-security.kubernetes.io/enforce=restricted</code></pre>

<h3>7. PoLP in the cloud (IAM)</h3>
<p>Five principles sustain PoLP at the cloud layer. Prefer a role over
a static key — via workload identity (IRSA on AWS, Workload Identity on
GKE, Managed Identity on AKS) — eliminating the problem of a long-lived
credential leaking permanently. A granular policy grants
<code>s3:GetObject</code> on a specific
<code>arn:aws:s3:::bucket-x/*</code>, not
<code>s3:*</code> on <code>*</code> for convenience. Permission
Boundaries and SCPs act as structural guard-rails that even a sub-account
administrator cannot exceed, even with the best of intentions.
Conditionals (<code>aws:SourceVpc</code>,
<code>aws:MultiFactorAuthPresent</code>,
<code>aws:RequestedRegion</code>) restrict WHEN and FROM WHERE a
permission applies, not just WHAT it allows. And time-bounding — via STS
AssumeRole with a short TTL — ensures that even a correctly granted
credential expires on its own, shrinking the exploitation window if it
leaks:</p>
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

<h3>8. Privilege creep, the invisible enemy</h3>
<p>Without periodic audits, the natural pattern is that everyone only
ADDS new permissions, and nobody removes the old ones that are no longer
needed. In two years, an IAM role that started with a single
<code>s3:GetObject</code> on a specific bucket accumulates 47 different
permissions, and nobody can say with certainty which of them are still
actually used in practice. Four tools fix that opacity: AWS IAM Access
Analyzer reports what each principal REALLY used in the last 90 days,
revealing what can be pruned safely; Cloudsplaining (originally from
Salesforce) is a scanner that evaluates risk directly on the declared
policy; Steampipe lets you run SQL straight against live cloud state — a
query like <code>select * from aws_iam_role where
assume_role_policy like '%*%'</code> finds a dangerously open role in
seconds; and cloudquery keeps a continuously updated catalog for
recurring queries.</p>

<h3>9. Real case: Capital One 2019</h3>
<p>The attacker exploited a misconfigured WAF, enabling SSRF that
extracted a temporary IAM credential via
<code>169.254.169.254</code> — AWS's own metadata service.
That credential carried <code>s3:ListAllMyBuckets</code> and
<code>s3:GetObject</code> open on ALL of the company's buckets, a
decision justified internally as "simplicity" at configuration time.
The result was 100 million customer records leaked, an US$ 80 million
fine, and the responsible CISO being fired. If the role had been
restricted to the specific bucket the WAF actually needed to touch, the
leak would have been a tiny fraction of what actually happened — the
entire incident is, at bottom, a PoLP violation from the original
permission design.</p>

<h3>10. Anti-patterns</h3>
<ul>
<li><strong><code>chmod 777</code> "because it was throwing an error"</strong>:
fixes the immediate symptom while opening a permanent door that any
system user can exploit later.</li>
<li><strong><code>kubectl create clusterrolebinding app-admin
--clusterrole=cluster-admin</code></strong>: grants total control over
the entire cluster to solve a problem that probably needed a fraction
of that.</li>
<li><strong>Application running as root in the container "because the
official image is like that"</strong>: accepts the default without
questioning whether it fits the real use case (section 5).</li>
<li><strong>IAM role <code>*</code> on <code>*</code> "I'll tighten it
later"</strong>: the "later" almost never arrives, and broad access
becomes the permanent de facto state.</li>
<li><strong>Sharing a service account credential among
humans</strong>: eliminates all traceability of who did what, exactly
the opposite of what per-identity auditing (section 2) proposes.</li>
<li><strong>Permanent access instead of just-in-time</strong>: keeps
elevated privilege active all the time, when it is only needed for a
specific window of time.</li>
</ul>
<p>For each of these patterns there is a safe alternative that takes
minutes to configure and can potentially avoid hours — or days — of
incident response later.</p>
"""
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
                "practical_en": (
                    "(1) Pick an existing systemd service on your machine and run "
                    "<code>systemd-analyze security &lt;unit&gt;</code>. Note the score.<br>(2) "
                    "Create a drop-in at "
                    "<code>/etc/systemd/system/&lt;unit&gt;.d/hardening.conf</code> with "
                    "<code>NoNewPrivileges=true</code>, <code>PrivateTmp=true</code>, "
                    "<code>ProtectSystem=strict</code>, <code>ProtectHome=true</code>, and "
                    "<code>ReadWritePaths=</code> only for the paths you need.<br>(3) "
                    "<code>systemctl daemon-reload &amp;&amp; systemctl restart "
                    "&lt;unit&gt;</code> and see if it breaks. If it breaks, read "
                    "<code>journalctl</code> and adjust <code>ReadWritePaths</code>.<br>(4) Run "
                    "<code>systemd-analyze security</code> again. The score should drop (more "
                    "secure = lower score).<br>(5) Bonus: do the same exercise on a Dockerfile — "
                    "add a non-root <code>USER</code>, <code>--cap-drop=ALL</code>, "
                    "<code>--read-only</code>, and see whether the app still works."
                ),
            },
            "materials": [
                m("OWASP Top 10: Broken Access Control",
                  "https://owasp.org/Top10/A01_2021-Broken_Access_Control/", "docs", "", title_en="OWASP Top 10: Broken Access Control", description_en=""),
                m("NIST: Least Privilege",
                  "https://csrc.nist.gov/glossary/term/least_privilege", "docs", "", title_en="NIST: Least Privilege", description_en=""),
                m("Run Docker as non-root",
                  "https://docs.docker.com/engine/security/userns-remap/", "docs", "", title_en="Run Docker as non-root", description_en=""),
                m("man capabilities(7)",
                  "https://man7.org/linux/man-pages/man7/capabilities.7.html", "docs", "", title_en="man capabilities(7)", description_en=""),
                m("AWS IAM Best Practices",
                  "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html",
                  "docs", "", title_en="AWS IAM Best Practices", description_en=""),
                m("systemd hardening cheatsheet",
                  "https://www.redhat.com/sysadmin/mastering-systemd",
                  "article", "", title_en="systemd hardening cheatsheet", description_en=""),
            ],
            "questions": [
                q("Por que evitar rodar serviços como root?",
                  "Se o serviço for comprometido, o atacante já tem privilégios totais.",
                  ["Porque o root consome mais recurso de CPU e memória do que outro usuário.",
                   "Porque o protocolo HTTPS exige explicitamente que o processo não seja root.",
                   "Porque o processo root reinicia o sistema inteiro assim que qualquer serviço trava."],
                  "Cada vulnerabilidade (heartbleed, log4shell, etc.) num serviço root vira "
                  "comprometimento total da máquina.",
                  statement_en="Why avoid running services as root?",
                  correct_en="If the service is compromised, the attacker already has full privileges.",
                  wrong_en=[
                    "Because root consumes more CPU and memory resources than another user account.",
                    "Because the HTTPS protocol explicitly requires that the process not be root.",
                    "Because a root process reboots the entire system as soon as any service crashes."
                ],
                  explanation_en="Every vulnerability (heartbleed, log4shell, etc.) in a root service becomes"
                  "full machine compromise."),
                q("Qual arquivo controla regras de `sudo`?",
                  "/etc/sudoers (e /etc/sudoers.d/)",
                  ["/etc/passwd e /etc/shadow.bak.old", "/root/.bashrc pessoal da conta root", "/var/log/sudo.log rotativo diário"],
                  "Edite com `visudo` ou drops em /etc/sudoers.d/, que evita corromper o arquivo principal.",
                  statement_en="Which file controls `sudo` rules?",
                  correct_en="/etc/sudoers (and /etc/sudoers.d/)",
                  wrong_en=[
                    "/etc/passwd and /etc/shadow.bak.old",
                    "/root/.bashrc belonging to the root account",
                    "/var/log/sudo.log rotated on a daily schedule"
                ],
                  explanation_en="Edit with `visudo` or drop-ins under /etc/sudoers.d/, which avoids"
                  "corrupting the main file."),
                q("O que fazem as Linux capabilities?",
                  "Decompõem privilégios de root em grãos menores (ex.: NET_BIND_SERVICE).",
                  ["Aceleram a execução de syscall trocando o escalonador padrão do kernel.",
                   "Implementam cota de uso de disco por usuário ou grupo do sistema.",
                   "Substituem regra de firewall por uma verificação feita dentro do próprio processo."],
                  "Em vez de root inteiro, dê só CAP_NET_BIND_SERVICE para um binário web bindar a 80/443.",
                  statement_en="What do Linux capabilities do?",
                  correct_en="They split root privileges into smaller grains (e.g. NET_BIND_SERVICE).",
                  wrong_en=[
                    "They speed up syscall execution by swapping the kernel's default scheduler.",
                    "They enforce disk usage quotas per user or group on the system.",
                    "They replace firewall rules with a check performed inside the process itself."
                ],
                  explanation_en="Instead of full root, grant only CAP_NET_BIND_SERVICE so a web binary can"
                  "bind to 80/443."),
                q("Em Kubernetes, qual campo do PodSpec exige que o container rode como não-root?",
                  "securityContext.runAsNonRoot: true",
                  ["spec.privileged: false configurado", "metadata.root: false customizado", "spec.uid: 0 explícito no manifest"],
                  "Combine com runAsUser específico e a imagem precisa estar pronta para isso.",
                  statement_en="In Kubernetes, which PodSpec field requires the container to run as non-root?",
                  correct_en="securityContext.runAsNonRoot: true",
                  wrong_en=[
                    "spec.privileged: false configured",
                    "metadata.root: false customized",
                    "spec.uid: 0 set explicitly in the manifest"
                ],
                  explanation_en="Combine it with a specific runAsUser, and the image must be ready for that."),
                q("Qual prática viola PoLP?",
                  "Dar 'AdministratorAccess' a uma role de aplicação.",
                  ["Aplicar service account dedicada com permissão mínima para cada workload.",
                   "Rotacionar credencial periodicamente conforme a política de segurança da equipe.",
                   "Usar policy do IAM com escopo restrito a um recurso e ação específicos."],
                  "Aplicação não precisa de admin. PoLP é dar exatamente o que ela usa.",
                  statement_en="Which practice violates PoLP?",
                  correct_en="Granting 'AdministratorAccess' to an application role.",
                  wrong_en=[
                    "Applying a dedicated service account with minimal permission for each workload.",
                    "Rotating credentials on a schedule according to the team's security policy.",
                    "Using an IAM policy scoped to a specific resource and action."
                ],
                  explanation_en="An application does not need admin. PoLP means giving exactly what it uses."),
                q("`chmod 777 /opt/app` é problemático porque:",
                  "Qualquer usuário do sistema pode escrever, ler e executar, escalada trivial.",
                  ["Apaga o conteúdo do arquivo assim que o comando chmod termina de rodar.",
                   "Não funciona em sistema de arquivo ext4 mais antigo, mas funciona em outros.",
                   "É mais lento que ajustar permissão via ACL específica para cada usuário."],
                  "Atacante com qualquer usuário do sistema injeta payload no app legítimo.",
                  statement_en="`chmod 777 /opt/app` is problematic because:",
                  correct_en="Any user on the system can read, write, and execute — trivial escalation.",
                  wrong_en=[
                    "It deletes the file contents as soon as the chmod command finishes running.",
                    "It fails on older ext4 filesystems, though it works on other filesystem types.",
                    "It is slower than adjusting permissions via a per-user ACL for each account."
                ],
                  explanation_en="An attacker with any local user can inject a payload into the legitimate app."),
                q("O que é uma 'identity-based policy' em IAM?",
                  "Regras anexadas a um usuário/role definindo o que pode fazer.",
                  ["Senha rotativa gerada automaticamente a cada login bem-sucedido do usuário.",
                   "Token de DNS usado para provar propriedade de um domínio específico.",
                   "Backup criptografado guardado numa conta separada da conta de produção."],
                  "Resource-based policies, em contraste, ficam no recurso (ex.: bucket policy).",
                  statement_en="What is an 'identity-based policy' in IAM?",
                  correct_en="Rules attached to a user/role defining what it is allowed to do.",
                  wrong_en=[
                    "A rotating password generated automatically after every successful user login.",
                    "A DNS token used to prove ownership of a specific domain name.",
                    "An encrypted backup stored in an account separate from the production account."
                ],
                  explanation_en="Resource-based policies, by contrast, live on the resource (e.g. a bucket"
                  "policy)."),
                q("Qual ferramenta confina syscalls de processos no Linux?",
                  "seccomp",
                  ["iptables", "cron", "udev"],
                  "seccomp-bpf permite whitelistar quais syscalls um processo pode executar, "
                  "Docker e K8s usam isso.",
                  statement_en="Which tool confines process syscalls on Linux?",
                  correct_en="seccomp",
                  wrong_en=[
                    "iptables with a custom chain for process filtering",
                    "cron with a restricted schedule for privileged jobs",
                    "udev with a rule that blocks device node creation"
                ],
                  explanation_en="seccomp-bpf lets you whitelist which syscalls a process may execute; Docker"
                  "and K8s use it."),
                q("Quando uso 'sudo -i', o que acontece?",
                  "Inicio um shell de login como root.",
                  ["Atualizo o sistema operacional inteiro sem pedir confirmação adicional.",
                   "Rodo o próximo comando com um atraso extra, sem trocar de usuário atual.",
                   "Confirmo que minha conta tem permissão de usar sudo, sem executar comando algum depois disso."],
                  "-i carrega o ambiente de login do root; -s mantém o ambiente atual; "
                  "sem flags, executa um comando único.",
                  statement_en="When I use 'sudo -i', what happens?",
                  correct_en="I start a login shell as root.",
                  wrong_en=[
                    "I update the entire operating system without asking for extra confirmation.",
                    "I run the next command with an extra delay, without changing the current user.",
                    "I confirm my account may use sudo, without running any further command afterward."
                ],
                  explanation_en="-i loads root's login environment; -s keeps the current environment; with"
                  "no flags, it runs a single command."),
                q("A rotação periódica de credenciais ajuda PoLP porque:",
                  "Reduz a janela de exploração caso uma credencial vaze.",
                  ["Aumenta a entropia do gerador de senha usado para criar a credencial nova.",
                   "Faz log detalhado do uso completo da credencial nas últimas semanas de operação.",
                   "Substitui completamente a necessidade de configurar MFA na conta do usuário."],
                  "Não substitui PoLP, mas limita o blast radius de um vazamento.",
                  statement_en="Periodic credential rotation helps PoLP because:",
                  correct_en="It shrinks the exploitation window if a credential leaks.",
                  wrong_en=[
                    "It increases the entropy of the password generator used to create the new credential.",
                    "It produces a detailed log of full credential usage over the last weeks of operation.",
                    "It fully replaces the need to configure MFA on the user's account."
                ],
                  explanation_en="It does not replace PoLP, but it limits the blast radius of a leak."),
            ],
        },
        # =====================================================================
        # 1.6 Firewall
        # =====================================================================
        {
            "title": "Firewall Básico",
            "title_en": "Basic Firewall",
            "summary": "Configuração de regras de entrada/saída com UFW/iptables/nftables.",
            "summary_en": "Configuring inbound/outbound rules with UFW/iptables/nftables.",
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
                "intro_en": (
                    "A firewall is the host's first line of defense. It does not replace the "
                    "other layers (TLS, authentication, input validation), but it filters noise "
                    "and blocks opportunistic attacks that make up 90% of the malicious traffic "
                    "that hits a public IP.<br><br>This lesson covers the Linux kernel packet "
                    "filter (netfilter) and its historical (iptables) and modern (nftables, ufw) "
                    "interfaces, plus operational patterns and pitfalls that lock admins out of "
                    "the server."
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
<div class="mermaid">
flowchart TD
    A["Pacote chega na interface"] --> B{"Bate com alguma regra?"}
    B -- "Sim, ACCEPT" --> C["Segue para o destino"]
    B -- "Sim, DROP" --> D["Descartado em silêncio"]
    B -- "Sim, REJECT" --> E["Recusado, ICMP de erro enviado"]
    B -- "Não bate com nenhuma" --> F["Política padrão do firewall"]
</div>


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
                "body_en": (
                """<h3>1. The netfilter subsystem</h3>
<p>The Linux kernel implements a packet-filtering framework called
netfilter, with hooks at five distinct points along a packet's path
through the network stack. <code>PRE-ROUTING</code> acts even before
the final destination is decided, and that is where inbound NAT
happens. <code>INPUT</code> filters packets destined for the host
itself. <code>FORWARD</code> filters packets that are only routed
through the machine — the gateway or router scenario.
<code>OUTPUT</code> filters packets leaving the host itself. And
<code>POST-ROUTING</code> acts after routing is done, where outbound
NAT happens. An important detail when comparing tools: the user
interfaces — iptables, nftables, ufw — only BUILD rules on top of
those existing hooks; they do not swap the engine underneath.
Switching from <code>iptables</code> to <code>nftables</code> changes
the syntax, not the kernel's fundamental behavior.</p>
<div class="mermaid">
flowchart TD
    A["Pacote chega na interface"] --> B{"Bate com alguma regra?"}
    B -- "Sim, ACCEPT" --> C["Segue para o destino"]
    B -- "Sim, DROP" --> D["Descartado em silêncio"]
    B -- "Sim, REJECT" --> E["Recusado, ICMP de erro enviado"]
    B -- "Não bate com nenhuma" --> F["Política padrão do firewall"]
</div>


<h3>2. iptables vs nftables vs ufw</h3>
<p>Four tools cover the same space at different historical moments.
<strong>iptables</strong> (1998) is the classic, with verbose syntax
and a SEPARATE table for IPv6 (via <code>ip6tables</code>), ARP, and
ebtables — forgetting to replicate a rule in <code>ip6tables</code>
is a historical source of leaks (section 9). <strong>nftables</strong>
(2014) arrived as a unified replacement, with new syntax, better
performance, and IPv4 and IPv6 living in the same rule tree — on recent
distributions (Debian 11+, RHEL 9, Ubuntu 22.04+), the
<code>iptables</code> command itself became just a shim that translates
internally to nftables. <strong>UFW</strong> (Uncomplicated Firewall)
is a friendly wrapper for beginners — <code>ufw allow ssh</code>
works without needing to understand hooks or chains. And
<strong>firewalld</strong> (common on RHEL/Fedora) follows a different
model, organized around "zones" instead of direct explicit rules.</p>

<h3>3. UFW in practice</h3>
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
<p><code>ufw limit</code> automatically blocks an IP with more than 6
connection attempts in 30 seconds — direct protection against SSH
brute-force, without needing an external tool. For an even more
aggressive response, combining it with <code>fail2ban</code> adds
longer bans covering more ports at once.</p>

<h3>4. Raw nftables, for when UFW is not enough</h3>
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
<p>Applying that configuration and making it persist across boot is a
single command: <code>nft -f /etc/nftables.conf &amp;&amp; systemctl
enable nftables</code>.</p>

<h3>5. DROP vs REJECT vs ACCEPT</h3>
<table>
<tr><td><code>ACCEPT</code></td><td>lets it through</td></tr>
<tr><td><code>DROP</code></td><td>discards silently. The attacker sees
a timeout, harder to map. Baseline on the public internet.</td></tr>
<tr><td><code>REJECT</code></td><td>responds with ICMP
<em>port-unreachable</em> or TCP RST. 'More polite'; a legitimate
client discovers the error faster. Good on an internal network.</td></tr>
</table>
<p>The choice between DROP and REJECT is not neutral: DROP makes the
attacker spend time waiting for a timeout that never arrives, making
it harder to map which ports actually exist behind it — the correct
baseline for any interface exposed to the public internet. REJECT, on
the other hand, immediately reports that the port is closed, which is
useful on an internal network where there is no adversary trying to
map the environment, just a colleague trying to debug faster why
something will not connect. And the line
<code>ct state established,related accept</code> is what lets the
REPLY of a connection the host itself started come back freely,
without needing a separate explicit rule for every kind of return
traffic.</p>

<h3>6. Production care: do not lock yourself out!</h3>
<p>Before applying a restrictive rule over remote SSH, an automatic
rollback plan avoids the classic scenario of losing access to your own
server:</p>
<pre><code># Plano B: reverte automaticamente em 5 min se você não desativar
echo 'iptables-restore &lt; /tmp/rules.backup' | at now +5 minutes

iptables-save &gt; /tmp/rules.backup
# ... aplica novas regras ...
# se você confirma que continua funcionando:
atrm $(atq | tail -1 | awk '{print $1}')</code></pre>
<p>For nftables, the same principle applies by saving the current state
with <code>nft list ruleset &gt; /tmp/before.nft</code> before any
change, with <code>nft -f /tmp/before.nft</code> ready to revert if
something goes wrong. Persisting the rule is equally critical:
distributions usually offer <code>netfilter-persistent</code>,
<code>iptables-persistent</code>, or <code>nftables.service</code>
itself to reload the configuration at boot — without that, a simple
reboot wipes everything and the host is fully exposed again without
anyone noticing immediately.</p>

<h3>7. Limits of L3/L4 firewalls</h3>
<p>A firewall operating on port and protocol simply cannot see three
entire categories of attack: the contents of an HTTPS connection, which
arrive encrypted; the application's own logic, where SQL injection, XSS,
and RCE happen entirely inside an allowed payload; and the behavior of
an apparently legitimate user, such as credential stuffing distributed
across many rotating IPs, each individually below any configured rate
limit. To cover that gap there is layer 7: a WAF (ModSecurity,
Cloudflare, AWS WAF, Azure Front Door) inspects the real request
content; an API Gateway (Kong, Tyk, AWS API Gateway) applies rate
limits per API key and schema validation; and a service mesh
(Istio, Linkerd) provides genuine mTLS authentication between internal
services.</p>

<h3>8. Cloud firewalls: Security Groups and NACLs</h3>
<p>On AWS (and equivalents), the Security Group is STATEFUL and attached
directly to an ENI or instance, with default deny on inbound and allow
on outbound — and an outbound rule can reference another Security Group
directly as the destination, enabling whole-architecture composition by
reference (covered in the cloud networking lesson). The Network ACL is
STATELESS and operates at the subnet level, with numbered rules
evaluated in sequential order — useful specifically for blocking a broad
malicious IP without touching any individual Security Group. The
practical usage pattern splits the role of each: Security Group as the
application firewall ("the app talks to Postgres, nothing else"), and
NACL as the structural subnet guard-rail ("the private subnet does not
receive internet traffic, period").</p>

<h3>9. Real case: the ipv6-bypass</h3>
<p>For years, administrators carefully configured <code>iptables</code>
and simply forgot to replicate the same configuration in
<code>ip6tables</code>, leaving IPv6 traffic completely open even with
IPv4 well protected. Automated attackers discovered the host's IPv6
address — often exposed by DNS itself — and walked straight through that
forgotten side door. In 2014 this pattern became particularly well known
when Kubernetes' own <code>kubelet</code> exposed itself over IPv6 by
default without anyone having thought about it explicitly. The direct
practical lesson: use <code>nftables</code> with the <code>inet</code>
table — which filters IPv4 and IPv6 in the same rule tree at once —
structurally eliminates that kind of oversight, instead of depending on
manually remembering to duplicate every rule on both stacks.</p>

<h3>10. Hardening checklist</h3>
<ol>
<li>Default-deny on inbound; default-allow on outbound, with periodic
review even so.</li>
<li>Only the strictly necessary ports open, nothing "just in
case".</li>
<li>SSH with rate-limit (<code>ufw limit</code> combined with
fail2ban).</li>
<li>ICMP echo accepted but with rate-limit applied, avoiding abuse as a
flood vector.</li>
<li>Conntrack accepting established/related, and explicitly dropping
invalid state.</li>
<li>Log every initial DROP, but sampled (5 per minute, for example) so
the disk is not filled with repetitive noise.</li>
<li>Persistence configured, ensuring the rule survives a reboot
(section 6).</li>
<li>IPv6 filtered with the same rigor as IPv4 (section 9).</li>
<li>A rollback plan ready before any remote change over SSH.</li>
<li>Periodic audit asking, for every still-open port, "what exactly does
it serve today?".</li>
</ol>
"""
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
                "practical_en": (
                    "On a VM:<br>(1) <code>ufw default deny incoming</code> and <code>ufw "
                    "default allow outgoing</code>.<br>(2) <code>ufw limit ssh</code> and "
                    "<code>ufw allow 80,443/tcp</code>.<br>(3) <code>ufw enable</code>; verify "
                    "with <code>ufw status verbose</code>.<br>(4) From <em>another</em> machine, "
                    "run <code>nmap -sS -p 1-1024 &lt;ip&gt;</code> — only 22, 80, 443 should "
                    "appear.<br>(5) Make 10 SSH attempts with the wrong password from a third "
                    "machine (use <code>sshpass</code>) and watch the rate-limit kick in, IP "
                    "banned for a few minutes.<br>(6) Bonus: rewrite the same rules in raw "
                    "nftables and check <code>nft list ruleset</code>."
                ),
            },
            "materials": [
                m("UFW, Ubuntu Help", "https://help.ubuntu.com/community/UFW", "docs", "", title_en="UFW, Ubuntu Help", description_en=""),
                m("nftables wiki",
                  "https://wiki.nftables.org/wiki-nftables/index.php/Main_Page", "docs", "", title_en="nftables wiki", description_en=""),
                m("iptables tutorial",
                  "https://www.frozentux.net/iptables-tutorial/iptables-tutorial.html",
                  "docs", "Referência clássica.", title_en="iptables tutorial", description_en="Classic reference."),
                m("DigitalOcean: UFW Essentials",
                  "https://www.digitalocean.com/community/tutorials/ufw-essentials-common-firewall-rules-and-commands",
                  "article", "", title_en="DigitalOcean: UFW Essentials", description_en=""),
                m("Linux netfilter packet-filtering HOWTO",
                  "https://netfilter.org/documentation/HOWTO/packet-filtering-HOWTO.html",
                  "docs", "", title_en="Linux netfilter packet-filtering HOWTO", description_en=""),
                m("Cloudflare: WAF basics",
                  "https://www.cloudflare.com/learning/ddos/glossary/web-application-firewall-waf/",
                  "article", "", title_en="Cloudflare: WAF basics", description_en=""),
            ],
            "questions": [
                q("Qual comando UFW permite SSH?",
                  "ufw allow ssh",
                  ["ufw open 22 always", "ufw bind 22", "ufw forward ssh"],
                  "UFW reconhece nomes de serviço (ssh, http, https) ou número de porta.",
                  statement_en="Which UFW command allows SSH?",
                  correct_en="ufw allow ssh",
                  wrong_en=["ufw open 22 forever", "ufw bind 22", "ufw forward ssh"],
                  explanation_en="UFW recognizes service names (ssh, http, https) or a port number."),
                q("Política recomendada de entrada (INPUT)?",
                  "default deny, só permite o explicitamente autorizado.",
                  ["default allow, que libera qualquer conexão sem restrição.",
                   "ignorar tudo, deixando o kernel decidir sem regra aplicada de propósito.",
                   "drop saída e permitir entrada, o inverso do padrão recomendado."],
                  "Default-deny inverte o padrão: nada entra a menos que você diga sim.",
                  statement_en="Recommended inbound (INPUT) policy?",
                  correct_en="default deny, allowing only what you explicitly authorize.",
                  wrong_en=[
                    "default allow, which opens every connection with no restriction applied.",
                    "ignore everything, leaving the kernel to decide without any intentional rule.",
                    "drop outbound and allow inbound, the inverse of the recommended baseline."
                ],
                  explanation_en="Default-deny flips the default: nothing enters unless you say yes."),
                q("Qual chain do iptables filtra pacotes destinados ao próprio host?",
                  "INPUT", ["OUTPUT", "FORWARD", "POSTROUTING"],
                  "OUTPUT = pacotes saídos pelo host. FORWARD = pacotes roteados pela máquina (gateway).",
                  statement_en="Which iptables chain filters packets destined for the host itself?",
                  correct_en="INPUT",
                  wrong_en=["OUTPUT", "FORWARD", "POSTROUTING"],
                  explanation_en="OUTPUT = packets leaving the host. FORWARD = packets routed through the"
                  "machine (gateway)."),
                q("Diferença chave entre DROP e REJECT?",
                  "DROP descarta silenciosamente; REJECT envia ICMP/RST informando bloqueio.",
                  ["DROP é mais lento que REJECT porque processa mais campos de cada pacote recebido.",
                   "REJECT exige NAT configurado antes de funcionar corretamente na rede local.",
                   "DROP funciona só em pacote UDP, não em conexão TCP já estabelecida antes."],
                  "DROP é o padrão em internet pública (não dá pista para o atacante); "
                  "REJECT pode acelerar debug em rede interna.",
                  statement_en="Key difference between DROP and REJECT?",
                  correct_en="DROP discards silently; REJECT sends ICMP/RST announcing the block.",
                  wrong_en=[
                    "DROP is slower than REJECT because it processes more fields on every received packet.",
                    "REJECT requires NAT to be configured before it works correctly on the local network.",
                    "DROP works solely on UDP packets, not on a TCP connection already established earlier."
                ],
                  explanation_en="DROP is the baseline on the public internet (no hint for the attacker);"
                  "REJECT can speed up debugging on an internal network."),
                q("Por que limitar conexões a SSH (rate limiting)?",
                  "Mitiga brute force.",
                  ["Acelera o handshake.",
                   "Diminui CPU do kernel.",
                   "É exigência POSIX."],
                  "ufw limit bloqueia IPs com mais de 6 tentativas em 30s, combina bem com fail2ban.",
                  statement_en="Why rate-limit SSH connections?",
                  correct_en="It mitigates brute force.",
                  wrong_en=[
                    "It speeds up the SSH handshake for legitimate clients on the network.",
                    "It reduces kernel CPU usage by skipping checksum validation on each packet.",
                    "It is a hard requirement defined by the POSIX networking specification."
                ],
                  explanation_en="ufw limit blocks IPs with more than 6 attempts in 30s; it pairs well with"
                  "fail2ban."),
                q("Qual o sucessor moderno do iptables?",
                  "nftables",
                  ["ipset", "ipchains", "netcat"],
                  "nftables unifica vários antigos; iptables atual é shim sobre nft em distros novas.",
                  statement_en="What is the modern successor to iptables?",
                  correct_en="nftables",
                  wrong_en=[
                    "ipset used as a full firewall replacement",
                    "ipchains from the early Linux 2.2 era",
                    "netcat listening as a packet filter daemon"
                ],
                  explanation_en="nftables unifies several older tools; current iptables is often a shim over"
                  "nft on newer distros."),
                q("`ufw status numbered` mostra:",
                  "Lista numerada de regras para edição/exclusão.",
                  ["O uso de banda consumido por cada interface de rede monitorada.",
                   "Ataques recentes registrados no log do sistema de detecção.",
                   "Tráfego em tempo real passando por cada porta aberta agora."],
                  "Permite remover por índice: `ufw delete 3`.",
                  statement_en="`ufw status numbered` shows:",
                  correct_en="A numbered list of rules for editing/deletion.",
                  wrong_en=[
                    "Bandwidth usage consumed by each monitored network interface.",
                    "Recent attacks recorded in the system's detection log facility.",
                    "Live traffic currently flowing through each open port right now."
                ],
                  explanation_en="Lets you remove by index: `ufw delete 3`."),
                q("Qual porta 53 é tipicamente liberada para?",
                  "DNS", ["HTTP", "RDP", "SMB"],
                  "DNS usa 53 em UDP (queries normais) e TCP (zone transfer e mensagens grandes).",
                  statement_en="Port 53 is typically opened for?",
                  correct_en="DNS",
                  wrong_en=[
                    "HTTP reverse-proxy traffic on cleartext port 80",
                    "RDP remote desktop sessions to Windows hosts",
                    "SMB file sharing between Windows clients and servers"
                ],
                  explanation_en="DNS uses 53 on UDP (normal queries) and TCP (zone transfers and large messages)."),
                q("`ufw deny from 10.0.0.5` faz o quê?",
                  "Bloqueia conexões originadas desse IP.",
                  ["Renomeia a interface de rede associada àquele endereço específico.",
                   "Apaga a rota de rede configurada para alcançar esse IP específico.",
                   "Permite conexão vinda exclusivamente desse IP, bloqueando os demais."],
                  "Útil para banir IPs maliciosos rapidamente.",
                  statement_en="What does `ufw deny from 10.0.0.5` do?",
                  correct_en="It blocks connections originating from that IP.",
                  wrong_en=[
                    "It renames the network interface associated with that specific address.",
                    "It deletes the network route configured to reach that specific IP.",
                    "It allows connections exclusively from that IP, blocking everyone else."
                ],
                  explanation_en="Useful for banning malicious IPs quickly."),
                q("Por que abrir 'all' (qualquer porta) em produção é ruim?",
                  "Aumenta drasticamente a superfície de ataque.",
                  ["Quebra a resolução de DNS para qualquer requisição feita depois disso.",
                   "Reduz a performance do roteador por processar mais regra por pacote.",
                   "Não é uma configuração permitida pelo kernel na maioria das distribuições."],
                  "Cada porta exposta é uma chance a mais para encontrar uma vulnerabilidade.",
                  statement_en="Why is opening 'all' (every port) in production a bad idea?",
                  correct_en="It drastically increases the attack surface.",
                  wrong_en=[
                    "It breaks DNS resolution for any request made after that change.",
                    "It reduces router performance by processing more rules per packet.",
                    "It is a configuration the kernel rejects on most Linux distributions."
                ],
                  explanation_en="Every exposed port is another chance to find a vulnerability."),
            ],
        },
        # =====================================================================
        # 1.7 Web Servers
        # =====================================================================
        {
            "title": "Web Servers (Nginx/Apache)",
            "title_en": "Web Servers (Nginx/Apache)",
            "summary": "Como hospedar e proteger uma aplicação web simples.",
            "summary_en": "How to host and harden a simple web application.",
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
                "intro_en": (
                    "Even in the age of Kubernetes and service meshes, at the edge of almost "
                    "every web application there is still an Nginx, Caddy, Apache, or Traefik. "
                    "They do TLS termination, compression, caching, rate limiting, basic "
                    "authentication, redirects, and reverse proxying to apps on "
                    "uvicorn/gunicorn/php-fpm.<br><br>Configuring them well prevents an entire "
                    "class of security and performance bugs that many teams only discover during "
                    "an incident. This lesson is Nginx-centric (the most used in industry) with "
                    "bridges to Apache and Caddy."
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
<div class="mermaid">
flowchart LR
    Client["Cliente"] -- "HTTPS, porta 443" --> Nginx["Nginx, reverse proxy"]
    Nginx -- "HTTP, porta 8000" --> App1["App server 1"]
    Nginx -- "HTTP, porta 8001" --> App2["App server 2"]
</div>


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
                "body_en": (
                """<h3>1. Why TLS termination still exists at the edge</h3>
<p>Even in an environment with full mTLS inside the mesh, the edge
proxy remains justified for five concrete reasons: a public certificate
(Let's Encrypt) managed in a single central place, instead of spread
across dozens of microservices; HTTP/2 and HTTP/3 (QUIC) available by
default without each individual service having to implement that alone;
compression (gzip, brotli) and response caching applied in a single
layer; a WAF (ModSecurity) inspecting everything that comes in before
it even reaches the application; and path or host routing with
potentially complex logic, centralized in one place instead of
duplicated. The classic pattern is Nginx listening on 80/443 and doing
<code>proxy_pass http://127.0.0.1:8000</code> to gunicorn, uvicorn, or
daphne — or, when available, a Unix socket directly.</p>
<div class="mermaid">
flowchart LR
    Client["Cliente"] -- "HTTPS, porta 443" --> Nginx["Nginx, reverse proxy"]
    Nginx -- "HTTP, porta 8000" --> App1["App server 1"]
    Nginx -- "HTTP, porta 8001" --> App2["App server 2"]
</div>


<h3>2. Minimum viable configuration</h3>
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

<h3>3. Security headers in detail</h3>
<table>
<tr><td><code>Strict-Transport-Security</code></td>
<td>The browser will use HTTPS for X seconds without even trying HTTP.</td></tr>
<tr><td><code>X-Frame-Options DENY</code></td>
<td>Kills clickjacking via &lt;iframe&gt;.</td></tr>
<tr><td><code>X-Content-Type-Options nosniff</code></td>
<td>The browser will not 'guess' MIME types, so an avatar upload cannot become HTML.</td></tr>
<tr><td><code>Content-Security-Policy</code></td>
<td>The most powerful defense against XSS.
Defines which origins may run JS, load images, etc.</td></tr>
<tr><td><code>Referrer-Policy</code></td>
<td>Controls how much of the current URL is sent on <em>navigation</em>.</td></tr>
<tr><td><code>Permissions-Policy</code></td>
<td>Camera, microphone, geolocation — only with explicit opt-in.</td></tr>
</table>
<p>Each of these headers closes a specific attack vector that the
browser alone would leave open by default —
<code>X-Frame-Options</code>, for example, exists because without it
any site can embed your entire page in an invisible iframe and capture
the user's clicks without them noticing. Auditing all of this at once
via securityheaders.com and SSL Labs quickly reveals which header is
missing before someone has to discover it in an incident.</p>

<h3>4. CSP, the headache that is worth the effort</h3>
<p>Applying Content-Security-Policy directly in enforcement mode risks
breaking something in production without warning — the safe path is to
start in report-only mode, which only RECORDS violations without
blocking anything:</p>
<pre><code>add_header Content-Security-Policy-Report-Only "
  default-src 'self';
  script-src 'self' 'sha256-XXX...';
  style-src 'self' https://fonts.googleapis.com;
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  report-uri /csp-report;
" always;</code></pre>
<p>After collecting real violations for a few weeks and adjusting the
policy based on what shows up, swapping
<code>Content-Security-Policy-Report-Only</code> for
<code>Content-Security-Policy</code> moves from observation mode into
real blocking, already calibrated against false positives from
legitimate traffic itself.</p>

<h3>5. Rate limiting, the ABC against credential stuffing</h3>
<p>Routes like <code>/login</code>, <code>/register</code>, and
<code>/forgot-password</code> are obvious targets for automated mass
login attempts. In Nginx, that becomes a dedicated rate-limit zone:</p>
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
<p>Combining that with additional rate-limiting per user or API key
directly in the application matters because IP-only rate limits are
easily bypassed with rotating proxies or a distributed botnet — a
second layer looking at IDENTITY, not just network origin, closes that
gap.</p>

<h3>6. Reverse proxies and the real-IP problem</h3>
<p>When Nginx does <code>proxy_pass</code>, the application behind it
sees IP <code>127.0.0.1</code> — the proxy's own address, not the real
client. Preserving the true IP requires three explicit headers:</p>
<pre><code>proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Real-IP $remote_addr;</code></pre>
<p>And on the application side (Django, for example), configure
explicitly that it trusts that header:</p>
<pre><code>USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')</code></pre>
<p>The critical detail is NEVER trusting <code>X-Forwarded-For</code>
coming directly from an untrusted client — without an intermediate
proxy validating it, any client can simply FORGE that header and
pretend to be any IP they want. Explicitly configuring the number of
trusted hops (via <code>set_real_ip_from</code> combined with
<code>real_ip_recursive on</code> in Nginx, or the equivalent trust-hops
setting on an ALB) ensures that only the value inserted by the
legitimate proxy is accepted as true.</p>

<h3>7. Caching for performance and protection</h3>
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
<p>Beyond the obvious performance gain, caching also works as extra
protection against DoS: a repeated request finds a ready response at
the proxy and never reaches the application behind it, even under high
volumes of repetitive traffic.</p>

<h3>8. ModSecurity, embedded WAF</h3>
<p>ModSecurity v3 combined with the OWASP Core Rule Set blocks classic
attack patterns — SQL injection, XSS, path traversal — directly at the
proxy layer. The real risk is false positives breaking legitimate
application functionality, which justifies starting in
<code>DetectionOnly</code> mode, only logging without blocking yet:</p>
<pre><code># /etc/nginx/modsec/main.conf
Include /etc/nginx/modsec/coreruleset/crs-setup.conf
Include /etc/nginx/modsec/coreruleset/rules/*.conf
SecRuleEngine DetectionOnly
SecAuditLog /var/log/nginx/modsec_audit.log
SecAuditLogFormat JSON</code></pre>
<p>After a few weeks analyzing the log generated in that mode, switching
to <code>SecRuleEngine On</code> and tuning specific false positives
with <code>SecRuleRemoveById</code> completes the transition to effective
blocking, already calibrated against that application's real traffic.</p>

<h3>9. Caddy, a modern alternative</h3>
<p>Caddy removes much of the manual configuration friction: it
provisions TLS automatically via built-in Let's Encrypt, enables HTTP/3
by default, and keeps configuration syntax deliberately simpler than
the Nginx equivalent:</p>
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

<h3>10. Anti-patterns + real case</h3>
<ul>
<li><strong><code>autoindex on</code> in production</strong>: lists the
entire directory contents, a trivial leak of internal structure with no
effort from the attacker.</li>
<li><strong>Serving <code>.git</code> or <code>.env</code></strong>: a
real and recurring case — many WordPress sites have already leaked full
credentials exactly by not blocking those paths explicitly via
regex.</li>
<li><strong>TLS 1.0/1.1 still enabled</strong>: vulnerable to BEAST and
POODLE, attacks known for years — disabling them is trivial and has no
real compatibility cost today.</li>
<li><strong>Without <code>server_tokens off</code></strong>: reveals the
exact Nginx version running, making it easier for an attacker to match a
specific CVE without guessing.</li>
<li><strong>Without <code>client_max_body_size</code></strong>: leaves
the door open for DoS via disproportionately large file uploads.</li>
<li><strong>Default configuration never tested on SSL Labs</strong>:
many teams only discover the real grade when a customer complains, not
before.</li>
</ul>
"""
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
                "practical_en": (
                    "(1) Bring up a simple app (FastAPI/Django) on port 8000.<br>(2) Configure "
                    "Nginx as a reverse proxy to it with TLS via <code>certbot "
                    "--nginx</code>.<br>(3) Add all the security headers from the lesson. Add a "
                    "<code>limit_req</code> on <code>/login</code>.<br>(4) Test on <a "
                    "href='https://www.ssllabs.com/ssltest/'>SSL Labs</a> and <a "
                    "href='https://securityheaders.com'>securityheaders.com</a>. Aim for A+ on "
                    "both.<br>(5) Bonus: block access to <code>.env</code>, <code>.git</code>, "
                    "and <code>.htaccess</code> via:<br><code>location ~ /\\.(env|git|htaccess) { "
                    "deny all; }</code>.<br>(6) Advanced bonus: install ModSecurity in "
                    "<code>SecRuleEngine DetectionOnly</code> and generate a few SQLi attacks "
                    "via <code>curl</code>; check the log at "
                    "<code>/var/log/nginx/modsec_audit.log</code>."
                ),
            },
            "materials": [
                m("Nginx Beginner's Guide",
                  "https://nginx.org/en/docs/beginners_guide.html", "docs", "", title_en="Nginx Beginner's Guide", description_en=""),
                m("Mozilla SSL Configuration Generator",
                  "https://ssl-config.mozilla.org/", "tool", "", title_en="Mozilla SSL Configuration Generator", description_en=""),
                m("OWASP Secure Headers",
                  "https://owasp.org/www-project-secure-headers/", "docs", "", title_en="OWASP Secure Headers", description_en=""),
                m("Let's Encrypt + certbot", "https://certbot.eff.org/", "tool", "", title_en="Let's Encrypt + certbot", description_en=""),
                m("Apache HTTP Server Documentation",
                  "https://httpd.apache.org/docs/current/", "docs", "", title_en="Apache HTTP Server Documentation", description_en=""),
                m("SSL Labs server test",
                  "https://www.ssllabs.com/ssltest/",
                  "tool", "Auditoria pública de TLS de qualquer endpoint.", title_en="SSL Labs server test", description_en="Public TLS audit of any endpoint."),
            ],
            "questions": [
                q("Qual diretiva no Nginx oculta o número da versão?",
                  "server_tokens off;",
                  ["no_version on; custom", "server_hidden 1; ativo", "hide_version yes; extra"],
                  "Reduz o fingerprint para scanners automatizados.",
                  statement_en="Which Nginx directive hides the version number?",
                  correct_en="server_tokens off;",
                  wrong_en=["no_version on; custom", "server_hidden 1; ativo", "hide_version yes; extra"],
                  explanation_en="Reduces fingerprinting for automated scanners."),
                q("Qual header força HTTPS em browsers compatíveis?",
                  "Strict-Transport-Security (HSTS)",
                  ["Upgrade-Required (customizado antigo)", "Cache-Secure (nome totalmente inventado)", "Force-HTTPS (não padronizado ainda)"],
                  "Inclua max-age longo e includeSubDomains; considere preload list após estável.",
                  statement_en="Which header forces HTTPS in compatible browsers?",
                  correct_en="Strict-Transport-Security (HSTS)",
                  wrong_en=[
                    "Upgrade-Required (legacy custom name)",
                    "Cache-Secure (a completely invented header name)",
                    "Force-HTTPS (not a standardized header yet)"
                ],
                  explanation_en="Include a long max-age and includeSubDomains; consider the preload list"
                  "after things are stable."),
                q("Em Nginx, como configurar um proxy reverso?",
                  "Usando proxy_pass http://backend; em um bloco location.",
                  ["Configurar root html sozinho, sem proxy de fato envolvido no caminho.",
                   "fastcgi_pass *, sintaxe inválida usada para PHP-FPM, não proxy HTTP.",
                   "rewrite ^.*$, reescreve a URL mas não encaminha para outro servidor."],
                  "Lembre-se de proxy_set_header Host $host e X-Forwarded-* para a app saber o cliente real.",
                  statement_en="In Nginx, how do you configure a reverse proxy?",
                  correct_en="Using proxy_pass http://backend; inside a location block.",
                  wrong_en=[
                    "Configure root html alone, with no actual proxy involved in the path.",
                    "fastcgi_pass *, invalid syntax used for PHP-FPM, not an HTTP proxy.",
                    "rewrite ^.*$, which rewrites the URL but does not forward to another server."
                ],
                  explanation_en="Remember proxy_set_header Host $host and X-Forwarded-* so the app knows the"
                  "real client."),
                q("Qual a porta padrão do TLS/HTTPS?",
                  "443",
                  ["8443", "80", "23"],
                  "443 é well-known. 80 é HTTP puro, 23 é Telnet (legado e inseguro).",
                  statement_en="What is the default TLS/HTTPS port?",
                  correct_en="443",
                  wrong_en=[
                    "8443 used as an alternate TLS listener port",
                    "80 used for cleartext HTTP without encryption",
                    "23 used historically for the Telnet remote shell"
                ],
                  explanation_en="443 is well-known. 80 is plain HTTP; 23 is Telnet (legacy and insecure)."),
                q("Por que ativar gzip/brotli?",
                  "Reduz tamanho da resposta, acelera entrega.",
                  ["Aumenta a segurança da conexão contra ataque de interceptação.",
                   "Substitui completamente o cache do navegador e do proxy.",
                   "É um requisito real para habilitar o protocolo HTTP/2 no servidor."],
                  "Cuidado com BREACH/CRIME se concatenar conteúdo do usuário com segredo na mesma resposta.",
                  statement_en="Why enable gzip/brotli?",
                  correct_en="It shrinks response size and speeds up delivery.",
                  wrong_en=[
                    "It increases connection security against interception attacks.",
                    "It completely replaces the browser cache and the proxy cache.",
                    "It is a hard requirement to enable the HTTP/2 protocol on the server."
                ],
                  explanation_en="Watch for BREACH/CRIME if you concatenate user content with a secret in the"
                  "same response."),
                q("Qual diretiva limita tamanho do body em Nginx?",
                  "client_max_body_size",
                  ["max_body_kb inválido", "post_size não existe", "request_size_limit falso"],
                  "Mitiga abuso por uploads gigantes; ajuste por endpoint quando for upload legítimo.",
                  statement_en="Which Nginx directive limits body size?",
                  correct_en="client_max_body_size",
                  wrong_en=[
                    "max_body_kb which is not a valid Nginx directive",
                    "post_size which does not exist in Nginx configuration",
                    "request_size_limit which is a made-up directive name"
                ],
                  explanation_en="Mitigates abuse via giant uploads; adjust per endpoint when legitimate"
                  "uploads are needed."),
                q("O que faz o Mozilla SSL Configuration Generator?",
                  "Gera configurações TLS recomendadas (modern/intermediate/old).",
                  ["Renova certificado TLS automaticamente antes dele expirar de vez.",
                   "Cria par de chave SSH para autenticação de acesso remoto ao servidor.",
                   "Mede a latência de rede entre o cliente e o servidor de destino."],
                  "Atualizado pela Mozilla com base em pesquisa de browsers e CVEs.",
                  statement_en="What does the Mozilla SSL Configuration Generator do?",
                  correct_en="It generates recommended TLS configs (modern/intermediate/old).",
                  wrong_en=[
                    "It renews a TLS certificate automatically before it fully expires.",
                    "It creates an SSH key pair for remote authentication to the server.",
                    "It measures network latency between the client and the destination server."
                ],
                  explanation_en="Kept up to date by Mozilla based on browser research and CVEs."),
                q("Como redirecionar HTTP para HTTPS em Nginx?",
                  "return 301 https://$host$request_uri;",
                  ["proxy_pass https://$host/upstream;", "rewrite ^/ /https/ permanent always;", "if ($http) drop; return 403 forbidden;"],
                  "301 (permanente) ajuda cache e SEO. Use return em vez de rewrite, mais rápido.",
                  statement_en="How do you redirect HTTP to HTTPS in Nginx?",
                  correct_en="return 301 https://$host$request_uri;",
                  wrong_en=[
                    "proxy_pass https://$host/upstream;",
                    "rewrite ^/ /https/ permanent forever;",
                    "if ($http) drop; return 403 forbidden;"
                ],
                  explanation_en="301 (permanent) helps caching and SEO. Prefer return over rewrite — it is"
                  "faster."),
                q("Por que rate limiting em /login?",
                  "Mitiga ataques de força bruta e credential stuffing.",
                  ["Reduz o consumo de memória RAM do processo worker do Nginx.",
                   "Acelera o processo de login reduzindo etapa de validação.",
                   "Ativa autenticação multifator diretamente na camada do Nginx."],
                  "Limit_req_zone + limit_req em Nginx, ou middleware na própria app.",
                  statement_en="Why rate-limit /login?",
                  correct_en="It mitigates brute-force and credential stuffing attacks.",
                  wrong_en=[
                    "It reduces RAM usage of the Nginx worker process itself.",
                    "It speeds up login by skipping a validation step in the flow.",
                    "It enables multifactor authentication directly at the Nginx layer."
                ],
                  explanation_en="limit_req_zone + limit_req in Nginx, or middleware in the app itself."),
                q("Qual ferramenta automatiza certificados TLS gratuitos?",
                  "certbot (Let's Encrypt).",
                  ["docker compose, orquestra container, não emite certificado TLS.",
                   "cron-tls, nome inventado; não existe ferramenta com esse nome.",
                   "iptables, ferramenta de firewall, não emissão de certificado."],
                  "ACME é o protocolo; certbot, acme.sh, lego e o próprio Caddy implementam.",
                  statement_en="Which tool automates free TLS certificates?",
                  correct_en="certbot (Let's Encrypt).",
                  wrong_en=[
                    "docker compose, which orchestrates containers and does not issue TLS certificates.",
                    "cron-tls, an invented name; no tool with that name exists.",
                    "iptables, a firewall tool, not a certificate issuer."
                ],
                  explanation_en="ACME is the protocol; certbot, acme.sh, lego, and Caddy itself implement it."),
            ],
        },
        # =====================================================================
        # 1.8 Pacotes
        # =====================================================================
        {
            "title": "Gestão de Pacotes e Repositórios",
            "title_en": "Package Management and Repositories",
            "summary": "Instalação segura de softwares e verificação de assinaturas.",
            "summary_en": "How software gets onto the server, and how to keep it trustworthy.",
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
                "intro_en": (
                    "In almost every serious <em>supply chain</em> incident of the last decade — "
                    "SolarWinds (2020), Codecov (2021), npm 'colors' (2022), xz-utils (2024) — "
                    "one of the roots is installing a package without verifying its origin. APT, "
                    "DNF, and their peers have crypto built in that would solve that; language "
                    "package managers (npm, pypi, cargo) are also improving.<br><br>This lesson "
                    "covers how repositories guarantee integrity, how to add external sources "
                    "safely, version pinning, internal mirrors, and how to generate an SBOM to "
                    "survive the next Log4Shell."
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
<div class="mermaid">
flowchart TD
    A["apt install pacote-x"] --> B["Consulta o repositório configurado"]
    B --> C["Resolve a árvore de dependências"]
    C --> D{"Dependência já instalada em versão compatível?"}
    D -- "Sim" --> E["Reaproveita a já instalada"]
    D -- "Não" --> F["Baixa e instala a versão exigida"]
    E --> G["Instala pacote-x"]
    F --> G
</div>


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
                "body_en": (
                """<h3>1. The APT trust model</h3>
<p>Package validation in APT follows four chained steps, each depending
on the previous one. The repository publishes a <code>Release</code>
file containing the hash of each <code>Packages</code> file. That
<code>Release</code> file is signed with GPG, with the signature going
into <code>Release.gpg</code> (or embedded together in
<code>InRelease</code>). The client downloads <code>Release</code>,
validates the signature with the maintainer's public key — stored in
<code>/etc/apt/keyrings/</code> or <code>/etc/apt/trusted.gpg.d/</code>
— and only AFTER confirming the signature starts trusting the hashes
listed inside. And each individual <code>.deb</code> package carries a
hash that must match exactly what was registered. The practical result
of that chain is that even if a mirror is compromised, the attacker
cannot swap a package without invalidating the signature of everything
else — forging an isolated package would also require forging the
maintainer's GPG signature, which the cryptography behind it makes
infeasible.</p>
<div class="mermaid">
flowchart TD
    A["apt install pacote-x"] --> B["Consulta o repositório configurado"]
    B --> C["Resolve a árvore de dependências"]
    C --> D{"Dependência já instalada em versão compatível?"}
    D -- "Sim" --> E["Reaproveita a já instalada"]
    D -- "Não" --> F["Baixa e instala a versão exigida"]
    E --> G["Instala pacote-x"]
    F --> G
</div>


<h3>2. Adding external repositories safely</h3>
<p>The old form (<code>apt-key add -</code>) is deprecated precisely
because it added GLOBAL trust to the entire system — a key added that
way could sign ANY package from ANY repository, not just the specific
repository that introduced it. The modern form uses
<code>signed-by</code> to restrict the key's scope to only that declared
repository:</p>
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
<p>Step 3 — comparing the fingerprint with official documentation
before trusting — is what closes the real gap: downloading the key
alone does not prove it came from the legitimate maintainer, only that
it came from SOMEWHERE. On RHEL/Fedora the same principle applies:</p>
<pre><code>sudo rpm --import https://download.docker.com/linux/centos/gpg
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
# /etc/yum.repos.d/docker-ce.repo precisa ter gpgcheck=1</code></pre>

<h3>3. Version pinning in production</h3>
<p>Running <code>apt upgrade</code> in a production pipeline without
testing first is a risky bet — Nginx can update itself and a
configuration that worked until yesterday can break without warning.
Three mechanisms solve that with progressively more explicit control:
priority pinning, hold marks, or pinning the version directly in the
Dockerfile:</p>
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
<p>On RHEL, the equivalent is <code>dnf versionlock add nginx</code>.</p>

<h3>4. Internal mirror/registry: why it is worth it</h3>
<p>An internal mirror solves five problems at once in a mature
corporate environment: independence (the build does not fail when
upstream goes down temporarily); auditing (it is recorded exactly who
downloaded what and when); scanning (the package is scanned before it
even reaches the build, not after); speed (downloading from inside the
VPC is faster than going to the original maintainer every time); and
compliance (audits such as SOC 2 and ISO 27001 explicitly check this
kind of control). JFrog Artifactory (commercial, covers nearly every
format), Sonatype Nexus (commercial or free), and Pulpcore (open
source, common in the RHEL ecosystem) are the dominant tools in that
space.</p>

<h3>5. Language packages: the wild west</h3>
<p>npm, PyPI, RubyGems, and crates.io operate on a structurally
different model from APT: anyone can publish, with no central curation
barrier. That opens four specific attack vectors.
<strong>Typosquatting</strong> plants a malicious package with a name
similar to the legitimate one — there have already been
<code>colourama</code>, <code>requestes</code>, <code>pythn</code>, each
betting on a common typo. <strong>Dependency confusion</strong>
exploits a PRIVATE package whose name also exists publicly — if the
resolution configuration does not distinguish that correctly, the
package manager ends up preferring the public one (usually because it
has a newer version), pulling code from an unknown origin in place of
the expected private package. <strong>Account takeover</strong> happens
when the original maintainer loses their own credential and an attacker
publishes a malicious version directly on top of the already established
legitimate package — the 2022 "colors.js" case followed exactly that
pattern. And the <strong>long con</strong> is the most patient of the
four: a contributor establishes themselves as trustworthy over YEARS
before finally inserting a backdoor — the 2024 xz-utils case (section 8)
is the most studied example of that category. Four mitigations shrink
that surface: a mandatory lockfile (<code>poetry.lock</code>,
<code>package-lock.json</code>, <code>Cargo.lock</code> with hashes),
guaranteeing deterministic builds; an internal mirror with a whitelist of
approved packages; a dedicated scanner (<code>pip-audit</code>,
<code>npm audit</code>, <code>cargo audit</code>, OSV-Scanner, Trivy);
and dependency review directly on the PR, already native on both GitHub
and GitLab.</p>

<h3>6. SBOM, Software Bill of Materials</h3>
<p>An SBOM is literally the "ingredient list" of a piece of software —
when a new CVE appears in a common library (such as libxml, for
example), querying the SBOM reveals in seconds exactly which images or
services are affected, instead of manually scanning two hundred
Dockerfiles one by one. Two formats dominate: CycloneDX (maintained by
OWASP) and SPDX (maintained by the Linux Foundation). Generation is
straightforward:</p>
<pre><code># Imagem Docker
syft myapp:1.0 -o cyclonedx-json &gt; sbom.json

# Sistema de arquivos
syft dir:/opt/app -o spdx-json &gt; sbom-spdx.json

# Python apenas
cyclonedx-py -i requirements.txt -o sbom.xml

# Cruzando com CVEs
grype sbom:./sbom.json</code></pre>
<p>In specific sectors (US federal government, automotive, medical),
SBOM has already stopped being optional good practice and become a legal
obligation — via Executive Order 14028 in the United States, for
example.</p>

<h3>7. Build reproducibility</h3>
<p>A reproducible build guarantees that the same source code, in the
same environment, always produces exactly the same binary byte for byte
— that property is what makes it possible to VERIFY independently that a
published binary really came from the source code it claims to
represent, without having to blindly trust whoever published it. It is
the central concept of the Reproducible Builds project, and it depends
on four practices: pinning versions at every step of the build process;
a deterministic date (via <code>SOURCE_DATE_EPOCH</code>, instead of the
real execution timestamp); absence of randomness in ordering (for
example, explicitly sorting a file list before processing it); and a
fixed toolchain, with a specific compiler version, not "whatever is
installed at the moment".</p>

<h3>8. Real case: xz-utils 2024</h3>
<p>In March 2024 it was discovered that versions 5.6.0 and 5.6.1 of
<code>xz-utils</code> — a library present on virtually every Linux
distribution — carried a backdoor injected through
<code>libsystemd</code>, allowing remote code execution via sshd. The
attacker, known by the pseudonym Jia Tan, had been a trusted maintainer
of the project for YEARS before finally inserting the malicious code —
exactly the "long con" pattern described in section 5. What saved the
situation was almost accidental: a Microsoft engineer noticed a
slightly unusual latency on an SSH connection and decided to
investigate out of curiosity, not because any automated alert had
fired. The lessons documented afterward: an SBOM already in use would
have identified every affected server in minutes, not days of manual
investigation; the natural delay between a new version shipping and
reaching Linux distributions considered "stable" worked as an accidental
quarantine that saved most real-world cases; a reproducible build, in
this specific incident, would NOT have caught the problem — the
distributed tarball contained code that was effectively different from
what was in the public Git repository, a detail only a manual audit
comparing the two would reveal; and the whole episode is a reminder that
open source is not automatic security magic — it still depends on real
human review actually happening, not merely presumed because it is
"open to the public".</p>

<h3>9. Anti-patterns</h3>
<ul>
<li><strong><code>curl ... | bash</code></strong>: becomes full RCE if
the origin server is compromised at any moment between publication and
download.</li>
<li><strong><code>--allow-unauthenticated</code></strong> or the
equivalent "ignore signature error": removes precisely the protection
described in section 1, making the installed package indistinguishable
from a forged one.</li>
<li><strong>Adding a PPA or external repository without verifying the
fingerprint</strong>: skips the only step that actually proves the key's
origin (section 2).</li>
<li><strong>Never pinning anything, always using "latest"</strong>:
opens the door for an unexpected update to break production without
prior warning.</li>
<li><strong>Mixing stable and unstable repositories</strong>: creates an
unpredictable version combination, a "Frankenstein" that is hard to
debug when something breaks.</li>
<li><strong>Skipping release notes and updating production
directly</strong>: ignores exactly the information source that would
warn about a compatibility-breaking change.</li>
</ul>

<h3>10. Recommended workflow</h3>
<ol>
<li>In CI, run <code>pip-audit</code> or <code>npm audit</code> on every
PR, failing explicitly for Critical or High CVEs.</li>
<li>At build time, generate the SBOM and store it alongside the produced
artifact.</li>
<li>On push, scan in the registry itself (Trivy, Grype) against a
defined policy.</li>
<li>At deploy time, an admission controller (Kyverno) only accepts an
image that already comes with an attached SBOM.</li>
<li>In operations, periodic re-scanning (Harbor, Trivy operator) catches
a new CVE that was only disclosed after the original deploy.</li>
<li>Renovate or Dependabot opening update PRs automatically keeps that
cycle running without depending on someone remembering manually.</li>
</ol>
"""
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
                "practical_en": (
                    "(1) Add the official Docker repository on an Ubuntu VM via "
                    "<code>signed-by=/etc/apt/keyrings/...</code>. Verify the fingerprint "
                    "first.<br>(2) Pin the <code>docker-ce</code> version in "
                    "<code>/etc/apt/preferences.d/docker</code> and mark it with <code>apt-mark "
                    "hold</code>.<br>(3) Install <code>syft</code> and generate a CycloneDX SBOM "
                    "of the <code>nginx:1.24-alpine</code> image: <code>syft nginx:1.24-alpine "
                    "-o cyclonedx-json &gt; nginx.sbom.json</code>.<br>(4) Install "
                    "<code>grype</code> and cross the SBOM against CVEs: <code>grype "
                    "sbom:./nginx.sbom.json</code>.<br>(5) Bonus: try <code>apt install</code> "
                    "of a package that has no signature, observe APT's error, and research what "
                    "<code>--allow-unauthenticated</code> does (and why you should not use it)."
                ),
            },
            "materials": [
                m("Debian apt-secure", "https://wiki.debian.org/SecureApt", "docs", "", title_en="Debian apt-secure", description_en=""),
                m("DNF docs", "https://dnf.readthedocs.io/", "docs", "", title_en="DNF docs", description_en=""),
                m("APT user manual",
                  "https://www.debian.org/doc/manuals/apt-guide/index.en.html", "docs", "", title_en="APT user manual", description_en=""),
                m("Reproducible builds", "https://reproducible-builds.org/",
                  "article", "Por que builds determinísticos importam.", title_en="Reproducible builds", description_en="Why deterministic builds matter."),
                m("OpenSSF Best Practices", "https://www.bestpractices.dev/", "docs", "", title_en="OpenSSF Best Practices", description_en=""),
                m("syft (SBOM)", "https://github.com/anchore/syft", "tool", "", title_en="syft (SBOM)", description_en=""),
            ],
            "questions": [
                q("O que é um arquivo `.gpg` em /etc/apt/trusted.gpg.d/?",
                  "Chave pública usada para validar assinaturas de pacotes do repositório.",
                  ["Chave privada do mantenedor, que jamais deveria sair da máquina onde foi gerada.",
                   "Um token OAuth usado para autenticar uma chamada de API do repositório remoto.",
                   "O hash do binário do pacote, calculado bem antes de qualquer assinatura existir."],
                  "É a parte pública; APT a usa para verificar a assinatura do Release file.",
                  statement_en="What is a `.gpg` file under /etc/apt/trusted.gpg.d/?",
                  correct_en="A public key used to validate package signatures from the repository.",
                  wrong_en=[
                    "The maintainer's private key, which should not leave the machine where it was generated.",
                    "An OAuth token used to authenticate an API call to the remote repository.",
                    "The package binary hash, computed well before any signature exists."
                ],
                  explanation_en="It is the public part; APT uses it to verify the Release file signature."),
                q("`apt update` faz o quê?",
                  "Baixa metadados (índices) dos repositórios.",
                  ["Reinstala cada pacote já presente no sistema, um por um.",
                   "Apaga o cache local de pacote já baixado anteriormente.",
                   "Aplica patch de segurança direto no kernel em execução."],
                  "Atualiza o conhecimento sobre versões disponíveis. `apt upgrade` é que aplica.",
                  statement_en="What does `apt update` do?",
                  correct_en="It downloads metadata (indexes) from the repositories.",
                  wrong_en=[
                    "It reinstalls every package already present on the system, one by one.",
                    "It deletes the local cache of packages previously downloaded.",
                    "It applies a security patch directly to the running kernel."
                ],
                  explanation_en="It refreshes knowledge of available versions. `apt upgrade` is what applies"
                  "them."),
                q("Como bloquear uma versão específica em apt?",
                  "Pinning via /etc/apt/preferences.",
                  ["apt-get freeze, um subcomando que não existe no apt real.",
                   "dpkg --hold-version, flag inventada; dpkg não reconhece isso.",
                   "apt-mark exclude, opção que não existe no apt-mark de verdade."],
                  "`apt-mark hold` também funciona; pinning oferece mais granularidade (priority por origem).",
                  statement_en="How do you pin a specific version in apt?",
                  correct_en="Pinning via /etc/apt/preferences.",
                  wrong_en=[
                    "apt-get freeze, a subcommand that does not exist in real apt.",
                    "dpkg --hold-version, an invented flag; dpkg does not recognize it.",
                    "apt-mark exclude, an option that does not exist in real apt-mark."
                ],
                  explanation_en="`apt-mark hold` also works; pinning offers more granularity (priority by"
                  "origin)."),
                q("Por que evitar `curl ... | sh`?",
                  "Executa código remoto sem verificação de assinatura.",
                  ["Deixa o download mais lento por não usar cache do gerenciador.",
                   "Não funciona quando o shell padrão do sistema não é o bash.",
                   "Quebra a verificação de certificado TLS da conexão HTTPS."],
                  "MITM ou comprometimento do servidor de origem viram RCE imediato. Prefira pacote assinado.",
                  statement_en="Why avoid `curl ... | sh`?",
                  correct_en="It runs remote code without signature verification.",
                  wrong_en=[
                    "It makes the download slower by not using the package manager cache.",
                    "It fails when the system's default shell is not bash.",
                    "It breaks TLS certificate verification on the HTTPS connection."
                ],
                  explanation_en="MITM or a compromised origin server becomes immediate RCE. Prefer a signed"
                  "package."),
                q("`dpkg -l` lista:",
                  "Pacotes instalados em sistemas Debian.",
                  ["Logs recentes gerados pelo kernel durante o boot do sistema.",
                   "Repositórios configurados atualmente em /etc/apt/sources.list.",
                   "Só as dependências quebradas, sem listar o pacote inteiro."],
                  "É o equivalente a `rpm -qa` no mundo RHEL.",
                  statement_en="`dpkg -l` lists:",
                  correct_en="Installed packages on Debian systems.",
                  wrong_en=[
                    "Recent logs generated by the kernel during system boot.",
                    "Repositories currently configured in /etc/apt/sources.list.",
                    "Broken dependencies alone, without listing the full package set."
                ],
                  explanation_en="It is the equivalent of `rpm -qa` in the RHEL world."),
                q("Em supply chain, 'typosquatting' é:",
                  "Publicar pacotes com nomes parecidos para enganar usuários (ex.: 'numpyy').",
                  ["Um erro de digitação cometido dentro do próprio código-fonte do kernel Linux.",
                   "Uma falha de resolução de nome causada por configuração errada de servidor DNS.",
                   "Um patch de segurança aplicado automaticamente sem revisão humana alguma antes."],
                  "Caso famoso: pacotes maliciosos com nomes próximos a 'request', 'pyyaml', 'colorama' etc.",
                  statement_en="In supply chain, 'typosquatting' is:",
                  correct_en="Publishing packages with similar names to trick users (e.g. 'numpyy').",
                  wrong_en=[
                    "A typo made inside the Linux kernel's own source code.",
                    "A name-resolution failure caused by a misconfigured DNS server.",
                    "A security patch applied automatically with no human review beforehand."
                ],
                  explanation_en="Famous cases: malicious packages with names close to 'request', 'pyyaml',"
                  "'colorama', etc."),
                q("Qual ferramenta gera SBOM em projetos Python?",
                  "syft (ou pip-audit/cyclonedx-py).",
                  ["pylint, linter de qualidade de código Python, não gerador de SBOM.",
                   "isort, organizador de import Python, não tem relação com SBOM.",
                   "tox, ferramenta de automação de teste, não gera lista de dependência."],
                  "syft funciona em qualquer linguagem; cyclonedx-py é específico de Python.",
                  statement_en="Which tool generates an SBOM for Python projects?",
                  correct_en="syft (or pip-audit/cyclonedx-py).",
                  wrong_en=[
                    "pylint, a Python code-quality linter, not an SBOM generator.",
                    "isort, a Python import organizer, unrelated to SBOM.",
                    "tox, a test automation tool, which does not generate a dependency list."
                ],
                  explanation_en="syft works for any language; cyclonedx-py is Python-specific."),
                q("Por que assinar pacotes internos?",
                  "Garante autenticidade e integridade frente a tampering.",
                  ["Reduz o tamanho final do pacote compactado antes da distribuição.",
                   "Aumenta a velocidade de download por usar um servidor mais próximo.",
                   "Substitui a necessidade de rodar antivírus na máquina de destino."],
                  "Mesmo em rede 'segura', uma máquina comprometida poderia injetar binário se não houver assinatura.",
                  statement_en="Why sign internal packages?",
                  correct_en="It guarantees authenticity and integrity against tampering.",
                  wrong_en=[
                    "It reduces the final size of the compressed package before distribution.",
                    "It increases download speed by using a closer mirror server.",
                    "It replaces the need to run antivirus on the destination machine."
                ],
                  explanation_en="Even on a 'secure' network, a compromised machine could inject a binary if"
                  "there is no signature."),
                q("Em RHEL, qual comando equivalente a `apt update`?",
                  "dnf check-update",
                  ["yum reset --force --all", "rpm -i all --nodeps", "dnf install all --assumeyes"],
                  "Em RHEL 8+ é dnf; antes era yum (mantido como alias).",
                  statement_en="On RHEL, which command is equivalent to `apt update`?",
                  correct_en="dnf check-update",
                  wrong_en=["yum reset --force --everything", "rpm -i everything --nodeps", "dnf install everything --assumeyes"],
                  explanation_en="On RHEL 8+ it is dnf; earlier it was yum (kept as an alias)."),
                q("Por que fixar versões em produção?",
                  "Reprodutibilidade e evitar atualizações automáticas que quebrem o sistema.",
                  ["Reduz o consumo de CPU do processo gerenciador de pacotes durante a instalação.",
                   "Permite hot reload da aplicação inteira sem reiniciar o processo principal dela.",
                   "Habilita um modo verbose, mostrando muito mais detalhe durante a instalação inteira."],
                  "Update automático em pipeline sem testes = receita para outage.",
                  statement_en="Why pin versions in production?",
                  correct_en="Reproducibility and avoiding automatic updates that break the system.",
                  wrong_en=[
                    "It reduces CPU use of the package manager process during installation.",
                    "It enables hot reload of the entire application without restarting the main process.",
                    "It enables a verbose mode showing much more detail during the whole install."
                ],
                  explanation_en="Automatic updates in a pipeline without tests are a recipe for outage."),
            ],
        },
        # =====================================================================
        # 1.9 Logs
        # =====================================================================
        {
            "title": "Log Management",
            "title_en": "Log Management",
            "summary": "Onde os erros e ataques ficam registrados no sistema.",
            "summary_en": "Collecting, structuring, and searching logs so incidents do not go blind.",
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
                "intro_en": (
                    "Without logs, debugging becomes guesswork and incident investigation "
                    "becomes fiction — you invent what happened. Structured, centralized, "
                    "correlatable logs are what separate a professional team from an amateur "
                    "one.<br><br>This lesson covers: (a) where OS logs live, (b) how your app "
                    "should log, (c) what should <em>never</em> go into a log (LGPD/PCI), (d) "
                    "how to centralize, and (e) why logs are only one of the three legs of "
                    "observability."
                ),
                "body": (
                    "<h3>1. Logs do SO via systemd-journald</h3>"
                    "<p>Distros modernas centralizam tudo no <code>journald</code>:</p>"
                    """
<div class="mermaid">
flowchart LR
    App["Aplicação"] --> Agent["Agente de coleta"]
    Agent --> Buffer["Fila / buffer local"]
    Buffer --> Storage["Armazenamento centralizado"]
    Storage --> Query["Consulta e alerta"]
</div>
"""
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
                "body_en": (
                """<h3>1. OS logs via systemd-journald</h3><p>Modern distros centralize everything in <code>journald</code>:</p>
<div class="mermaid">
flowchart LR
    App["Aplicação"] --> Agent["Agente de coleta"]
    Agent --> Buffer["Fila / buffer local"]
    Buffer --> Storage["Armazenamento centralizado"]
    Storage --> Query["Consulta e alerta"]
</div>
<pre><code>journalctl -u nginx                    # serviço específico
journalctl -u nginx -f                 # follow (tail -f)
journalctl -u nginx -p err -S today    # erros de hoje
journalctl -k -p crit                  # kernel, criticais
journalctl _UID=1000                   # de um usuário
journalctl --since '1 hour ago' --until '5 min ago'
journalctl -o json-pretty -u nginx | jq .   # JSON estruturado
journalctl --disk-usage                # quanto está ocupando</code></pre><p>Persistence: by default journald only keeps logs in RAM (<code>/run/log</code>). To survive reboot:</p><pre><code># /etc/systemd/journald.conf
[Journal]
Storage=persistent
SystemMaxUse=2G
MaxRetentionSec=30day</code></pre><h3>2. Structured logs in your app</h3><p>Free-form text turns into painful regex when you need to search. JSON is the way. In Python:</p><pre><code>import structlog
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)

log = structlog.get_logger()

structlog.contextvars.bind_contextvars(
    request_id='req-123',
    user_id=42,
)

log.info('user.login', method='password', mfa=True)
# {"event":"user.login","method":"password","mfa":true,
#  "request_id":"req-123","user_id":42,"level":"info",
#  "timestamp":"2026-04-25T16:23:11.452123Z"}</code></pre><p>Equivalents: <code>pino</code> (Node), <code>zap</code> (Go), <code>logback-json</code> (Java), <code>slog</code> (Go 1.21+).</p><h3>3. Correlation/trace ID, gluing logs across services</h3><p>Microservices have a problem: the log for one request is scattered across 5 different services. Solution: propagate a <strong>trace ID</strong> on every request (HTTP header <code>traceparent</code>, W3C standard). Each service includes that ID in every log it emits.</p><p>The OpenTelemetry SDK does this transparently:</p><pre><code>from opentelemetry import trace
from opentelemetry.instrumentation.django import DjangoInstrumentor
DjangoInstrumentor().instrument()

# Em qualquer log emitido durante a request, trace_id estará presente
log.info('order.created', order_id=order.id, total=order.total)</code></pre><p>In an incident: grab the trace_id from the error log, search across all services, see the entire request in order.</p><h3>4. What NOT to log (LGPD, GDPR, PCI-DSS)</h3><table><tr><td>Passwords, hashes, tokens</td><td>Even in headers.</td></tr><tr><td>National IDs, card data</td><td>LGPD/PCI forbid it.</td></tr><tr><td>Health data</td><td>HIPAA, LGPD.</td></tr><tr><td>Session cookies</td><td>Enable session hijacking.</td></tr><tr><td>Upload contents</td><td>May contain PII.</td></tr><tr><td>Full email addresses</td><td>Pseudonymize.</td></tr></table><p>Mitigations:</p><pre><code># Redaction com structlog
REDACT_KEYS = {'password', 'token', 'authorization', 'cookie', 'cpf'}

def redact(_, __, event):
    for key in list(event):
        if key.lower() in REDACT_KEYS:
            event[key] = '***REDACTED***'
    return event

structlog.configure(processors=[redact, ...])</code></pre><p>Periodic audit: take 1000 random lines from prod logs and check whether anything sensitive escaped. Repeat quarterly.</p><h3>5. Centralization: ELK, Loki, cloud-native</h3><p>Options:</p><ul><li><strong>Elastic Stack (ELK)</strong>: indexes everything full-text. Powerful searches. Expensive in storage and operations.</li><li><strong>OpenSearch</strong>: Elastic fork (Apache 2.0).</li><li><strong>Grafana Loki</strong>: indexes only labels (not content). Cheap storage (S3). Searches via LogQL similar to PromQL. <em>Recommended for most teams.</em></li><li><strong>CloudWatch Logs</strong> / <strong>Azure Monitor</strong> / <strong>Cloud Logging</strong>: managed, great to start, can get expensive at scale.</li><li><strong>Datadog</strong>, <strong>New Relic</strong>, <strong>Splunk</strong>: commercial, complete, premium.</li></ul><p>Recommended collector (agent): <strong>OpenTelemetry Collector</strong>, vendor-neutral, supports all destinations. Alternatives: <strong>Vector</strong> (rust, fast), <strong>Fluent Bit</strong>, <strong>Promtail</strong> (Loki).</p><h3>6. Typical stack on K8s</h3><pre><code># App emite JSON em stdout/stderr
# Promtail (DaemonSet) lê do filesystem do node
# Loki guarda em S3
# Grafana faz dashboards e queries

{namespace="prod", app="api"} |= "error" | json | level="ERROR" \\
  | line_format "{{.timestamp}} {{.user_id}} {{.event}}"</code></pre><h3>7. Retention and cost</h3><p>Logs grow fast. A typical policy:</p><ul><li><strong>Hot</strong> (fast search, indexed): 7-30 days. Loki/ES on SSD.</li><li><strong>Cold</strong> (slow search but cheap): 90-365 days. S3/Glacier.</li><li><strong>Audit</strong> (compliance): 1-7+ years in a WORM bucket with object-lock. Immutable.</li></ul><p>Under SOC 2 Type II you usually need to prove 12 months of auth logs. PCI-DSS requires 12 months (3 immediate). LGPD has no legal minimum but does have a maximum (delete what you no longer need).</p><h3>8. Logs in incident response</h3><p>In an incident, a compromised host agent may have had <em>local</em> logs altered by the attacker to hide tracks. That is why:</p><ul><li>Centralize before the host is compromised.</li><li>Use an immutable bucket/system for forensically relevant logs (auth, audit).</li><li>Have offsite replication (cross-region, or a different cloud).</li></ul><p>Logs that matter in an incident: auth (login, sudo, ssh), audit (privileged commands), network (firewall drops, DNS queries), application (errors, anomalies).</p><h3>9. Metrics vs logs vs traces</h3><p>The three pillars of observability:</p><table><tr><th>Signal</th><th>Cardinality</th><th>Cost</th><th>Typical use</th></tr><tr><td>Metrics</td><td>low</td><td>low</td><td>'How many requests per second? p99 latency?'</td></tr><tr><td>Logs</td><td>high</td><td>medium-high</td><td>'What happened on that specific request?'</td></tr><tr><td>Traces</td><td>very high</td><td>high</td><td>'Where did it go and how long did each hop take?'</td></tr></table><p>OpenTelemetry standardizes collection of all three; storage is still separate (Prometheus for metrics, Loki for logs, Tempo for traces).</p><h3>10. Real case: the log that cost US$ 1B</h3><p>In 2017, Equifax was breached (147M Americans). Investigation showed the attacker was inside the network for 76 days. The logs had the indicators, including huge traffic leaving to a foreign IP, but the monitoring system was configured to ignore a certain category, and the team did not review logs manually. Result: US$ 1.4B in fines, settlement, and losses. Lesson: logs without alerting+review are just expensive storage.</p>
"""
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
                "practical_en": (
                    "(1) Configure your app to emit structured JSON with <code>structlog</code> "
                    "(Python) or similar, including <code>trace_id</code> and "
                    "<code>user_id</code> on every line.<br>(2) Locally, read with "
                    "<code>jq</code>: <code>./app | jq 'select(.level==\"error\")'</code>.<br>(3) "
                    "Bring up Loki + Promtail + Grafana via docker-compose (<a "
                    "href='https://grafana.com/docs/loki/latest/setup/install/docker/'>guide</a>) "
                    "and ship the logs.<br>(4) In Grafana, create a dashboard "
                    "with:<br>&nbsp;&nbsp;• error rate over the last 5 minutes;<br>&nbsp;&nbsp;• "
                    "top 10 user_ids with the most errors;<br>&nbsp;&nbsp;• a graph of logs by "
                    "level over time.<br>(5) Bonus: simulate an incident session — grab a "
                    "trace_id from an error, filter all logs with that trace_id, and reconstruct "
                    "the full request."
                ),
            },
            "materials": [
                m("systemd journald",
                  "https://www.freedesktop.org/software/systemd/man/latest/systemd-journald.service.html",
                  "docs", "", title_en="systemd journald", description_en=""),
                m("OWASP Logging Cheat Sheet",
                  "https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html",
                  "docs", "", title_en="OWASP Logging Cheat Sheet", description_en=""),
                m("Honeycomb: Structured logging",
                  "https://www.honeycomb.io/blog/structured-logging-and-your-team",
                  "article", "", title_en="Honeycomb: Structured logging", description_en=""),
                m("Grafana Loki", "https://grafana.com/docs/loki/latest/", "docs", "", title_en="Grafana Loki", description_en=""),
                m("rsyslog manual", "https://www.rsyslog.com/doc/", "docs", "", title_en="rsyslog manual", description_en=""),
                m("structlog (Python)",
                  "https://www.structlog.org/", "tool",
                  "Logs estruturados em Python sem dor.", title_en="structlog (Python)", description_en="Structured logging in Python without the pain."),
            ],
            "questions": [
                q("Qual comando vê logs do serviço nginx via systemd?",
                  "journalctl -u nginx",
                  ["systemctl logs nginx", "logread nginx", "tail /etc/nginx"],
                  "-u filtra por unidade. -f acompanha em tempo real, -p err filtra por prioridade.",
                  statement_en="Which command shows nginx service logs via systemd?",
                  correct_en="journalctl -u nginx",
                  wrong_en=[
                    "systemctl logs nginx as a built-in subcommand",
                    "logread nginx from an OpenWRT-style utility",
                    "tail /etc/nginx reading the config directory as if it were a log"
                ],
                  explanation_en="-u filters by unit. -f follows in real time; -p err filters by priority."),
                q("Por que preferir logs em JSON?",
                  "Facilita parsing, indexação e busca por campo.",
                  ["Compactam automaticamente o arquivo de log gerado no disco.",
                   "Ocupam menos espaço em disco do que o formato de texto livre.",
                   "Substituem completamente a necessidade de qualquer métrica numérica."],
                  "Texto livre vira regex doloroso. JSON tem schema e ferramentas de busca/agg nativas.",
                  statement_en="Why prefer JSON logs?",
                  correct_en="They make parsing, indexing, and field-based search easier.",
                  wrong_en=[
                    "They automatically compress the log file written to disk after each rotation cycle.",
                    "They use less disk space than free-form text format across long retention windows.",
                    "They completely replace the need for any numeric metrics collected by the monitoring stack."
                ],
                  explanation_en="Free-form text becomes painful regex. JSON has schema and native search/agg"
                  "tools."),
                q("O que é correlation ID?",
                  "Identificador único que liga logs da mesma requisição entre serviços.",
                  ["Hash do conteúdo do disco, calculado periodicamente pelo sistema operacional.",
                   "Chave de criptografia usada para cifrar o conteúdo do arquivo de log.",
                   "Versão do schema de dado usada pela aplicação num momento específico."],
                  "Geralmente o trace_id do OpenTelemetry, propagado em headers HTTP.",
                  statement_en="What is a correlation ID?",
                  correct_en="A unique identifier linking logs for the same request across services.",
                  wrong_en=[
                    "A hash of disk contents, computed periodically by the operating system.",
                    "An encryption key used to cipher the contents of the log file.",
                    "A data-schema version used by the application at a specific moment."
                ],
                  explanation_en="Usually the OpenTelemetry trace_id, propagated in HTTP headers."),
                q("Onde NÃO devem aparecer dados sensíveis (senhas, CPF)?",
                  "Em logs.",
                  ["Em variáveis de ambiente.",
                   "Em arquivos rotacionados.",
                   "Em traces criptografados."],
                  "LGPD/GDPR/PCI proíbem. Use redaction no logger e revise periodicamente uma "
                  "amostra dos logs.",
                  statement_en="Where should sensitive data (passwords, national IDs) NOT appear?",
                  correct_en="In logs.",
                  wrong_en=[
                    "In environment variables used by the running process",
                    "In rotated files managed by logrotate on the host",
                    "In encrypted traces stored by the observability backend"
                ],
                  explanation_en="LGPD/GDPR/PCI forbid it. Use redaction in the logger and periodically"
                  "review a sample of logs."),
                q("Qual ferramenta agrega logs com baixo custo armazenando-os no S3?",
                  "Grafana Loki",
                  ["Prometheus + Thanos", "Grafana Tempo", "Elastic Beats"],
                  "Loki indexa apenas labels (não o corpo) e usa storage barato, perfeito para alto volume.",
                  statement_en="Which tool aggregates logs cheaply by storing them in S3?",
                  correct_en="Grafana Loki",
                  wrong_en=[
                    "Prometheus + Thanos for metrics long-term storage",
                    "Grafana Tempo for distributed tracing backends",
                    "Elastic Beats as a log shipper without cheap object storage"
                ],
                  explanation_en="Loki indexes only labels (not the body) and uses cheap storage — ideal for"
                  "high volume."),
                q("Por que rotacionar logs?",
                  "Evitar que ocupem todo o disco e facilitar arquivamento.",
                  ["Substituir completamente a necessidade de fazer qualquer backup.",
                   "Habilitar suporte a IPv6 na interface de rede do servidor.",
                   "Aumentar a performance da CPU durante o processamento de log."],
                  "logrotate é o utilitário padrão. journald já rotaciona internamente por tamanho/tempo.",
                  statement_en="Why rotate logs?",
                  correct_en="To keep them from filling the disk and to make archiving easier.",
                  wrong_en=[
                    "To completely replace the need to take any backup of application or system data whatsoever.",
                    "To enable IPv6 support on the server's network interface without changing other settings.",
                    "To increase CPU performance while processing log lines during peak traffic periods."
                ],
                  explanation_en="logrotate is the standard utility. journald already rotates internally by"
                  "size/time."),
                q("`logrotate` configura-se em:",
                  "/etc/logrotate.conf e /etc/logrotate.d/*",
                  ["/etc/passwd e /etc/shadow.backup.antigo", "/var/lib/rotate.conf e /var/lib/rotate.d/*", "/proc/log/rotate.conf e /proc/log/rotate.d/*"],
                  "Cada serviço pode ter um arquivo próprio em /etc/logrotate.d/ com sua política.",
                  statement_en="`logrotate` is configured in:",
                  correct_en="/etc/logrotate.conf and /etc/logrotate.d/*",
                  wrong_en=[
                    "/etc/passwd and /etc/shadow.backup.antigo",
                    "/var/lib/rotate.conf and /var/lib/rotate.d/*",
                    "/proc/log/rotate.conf and /proc/log/rotate.d/*"
                ],
                  explanation_en="Each service can have its own file under /etc/logrotate.d/ with its policy."),
                q("Qual prioridade no syslog representa erros críticos?",
                  "crit (2)",
                  ["debug (7)", "info (6)", "notice (5)"],
                  "Hierarquia: emerg(0), alert(1), crit(2), err(3), warning(4), notice(5), info(6), debug(7).",
                  statement_en="Which syslog priority represents critical errors?",
                  correct_en="crit (2)",
                  wrong_en=[
                    "debug (7) used for verbose diagnostic output",
                    "info (6) used for routine operational messages",
                    "notice (5) used for significant but non-error events"
                ],
                  explanation_en="Hierarchy: emerg(0), alert(1), crit(2), err(3), warning(4), notice(5),"
                  "info(6), debug(7)."),
                q("`journalctl --vacuum-size=200M` faz:",
                  "Reduz o journal a no máximo 200 MB.",
                  ["Reinicia o serviço journald por completo, sem limitar tamanho.",
                   "Move o conteúdo do journal inteiro para um bucket S3 remoto.",
                   "Apaga só o log gerado pelo kernel, sem tocar no resto do journal."],
                  "Há também --vacuum-time=7d para limitar por idade.",
                  statement_en="`journalctl --vacuum-size=200M` does:",
                  correct_en="Shrinks the journal to at most 200 MB.",
                  wrong_en=[
                    "Fully restarts the journald service without limiting size.",
                    "Moves the entire journal contents to a remote S3 bucket.",
                    "Deletes solely kernel-generated logs, leaving the rest of the journal."
                ],
                  explanation_en="There is also --vacuum-time=7d to limit by age."),
                q("Por que centralizar logs?",
                  "Permite correlação entre máquinas e sobrevive à perda do host.",
                  ["Substitui log local por completo, sem manter cópia alguma na própria máquina.",
                   "Acelera o boot do sistema ao pular a etapa de inicialização do log.",
                   "Aumenta a entropia disponível para geração de número aleatório no host."],
                  "Em incidente, host pode estar comprometido e logs locais alterados, central é forensics-friendly.",
                  statement_en="Why centralize logs?",
                  correct_en="It enables correlation across machines and survives host loss.",
                  wrong_en=[
                    "It fully replaces local logs, keeping no copy on the machine itself.",
                    "It speeds up system boot by skipping the log initialization step.",
                    "It increases available entropy for random-number generation on the host."
                ],
                  explanation_en="In an incident the host may be compromised and local logs altered — a"
                  "central store is forensics-friendly."),
            ],
        },
        # =====================================================================
        # 1.10 Cultura DevSecOps
        # =====================================================================
        {
            "title": "Cultura DevSecOps",
            "title_en": "DevSecOps Culture",
            "summary": "Segurança não é uma fase, é um hábito em todas as etapas.",
            "summary_en": "Security as a shared habit, not a gate at the end of the pipeline.",
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
                "intro_en": (
                    "Every expensive tool on the market — a US$ 100k/year SAST, a giant "
                    "vulnerability scanner, an outsourced SOC — fails without culture. DevSecOps "
                    "is what turns 'security is not my problem' into 'security is part of my job "
                    "as an engineer'.<br><br>This lesson is less about code and more about "
                    "<em>how real teams operate</em>. Why culture beats process and tools every "
                    "time, how to build that culture, metrics that matter, and the "
                    "organizational anti-patterns that kill security programs."
                ),
                "body": (
                    "<h3>1. O que é DevSecOps de verdade</h3>"
                    "<p>DevOps tirou paredes entre dev e ops. DevSecOps faz o mesmo com "
                    "segurança. Em prática:</p>"
                    """
<div class="mermaid">
flowchart LR
    A["Código"] --> B["Commit"]
    B --> C["CI: SAST + SCA"]
    C --> D["Build"]
    D --> E["CD: DAST + Policy as Code"]
    E --> F["Produção: runtime security"]
</div>
"""
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
                "body_en": (
                """<h3>1. What DevSecOps really is</h3><p>DevOps tore down walls between dev and ops. DevSecOps does the same with security. In practice:</p>
<div class="mermaid">
flowchart LR
    A["Código"] --> B["Commit"]
    B --> C["CI: SAST + SCA"]
    C --> D["Build"]
    D --> E["CD: DAST + Policy as Code"]
    E --> F["Produção: runtime security"]
</div>
<ul><li>Security is <em>everyone's</em> responsibility, not 'the security team's'.</li><li>Automated controls &gt; a human gate on every pull request.</li><li>Fast feedback (seconds in the editor, minutes on the PR) &gt; an audit report 6 months later.</li><li>Mistakes are learning opportunities, not firings.</li></ul><p>The security team becomes an <em>enabler</em>: tools, training, standards. Decisions stay with whoever is closest to the code.</p><h3>2. Shift-left that works vs shift-left theater</h3><p>Shift-left means bringing security into earlier phases. But there is a good version and a bad version:</p><table><tr><th>Works</th><th>Is theater</th></tr><tr><td>Linter in the editor</td><td>Monthly PDF report</td></tr><tr><td>SAST on the PR (3-min)</td><td>Annual pentest at the end of the release</td></tr><tr><td>Threat model in design review</td><td>3-hour approval meeting before deploy</td></tr><tr><td>SBOM generated on every build</td><td>Spreadsheet nobody updates</td></tr><tr><td>Executable runbook (PIR)</td><td>Wiki nobody opens</td></tr></table><p>Criterion: <em>the engineer gets feedback while still working on the problem</em>.</p><h3>3. Threat modeling, STRIDE on 1 page</h3><p>STRIDE is the 6 threat categories:</p><ul><li><strong>S</strong>poofing — someone pretends to be someone else.</li><li><strong>T</strong>ampering — someone alters data in transit or at rest.</li><li><strong>R</strong>epudiation — someone denies having done something, with no trail.</li><li><strong>I</strong>nformation Disclosure — a leak.</li><li><strong>D</strong>enial of Service — the system falls under load or attack.</li><li><strong>E</strong>levation of Privilege — a normal user becomes admin.</li></ul><p>In a design review for a relevant feature, write one page answering:</p><ol><li><strong>What are we building?</strong> (1 paragraph + diagram)</li><li><strong>What are the assets?</strong> (data, accounts, etc.)</li><li><strong>Who are the actors?</strong> (legitimate and hostile)</li><li><strong>For each component, 1 threat per STRIDE category</strong></li><li><strong>Mitigation for each threat</strong> (and what we accept as residual risk)</li></ol><p>Changing architecture pre-code is cheap. Post-deploy is expensive and political.</p><h3>4. Blameless postmortems</h3><p>Incident timing is when emotional capacity is lowest. Instead of 'who approved that?', do:</p><ul><li><strong>Factual timeline</strong>: what happened when, based on logs.</li><li><strong>Contributing causes</strong> (not 'the cause'): which decisions/gaps/conditions led here?</li><li><strong>What worked well</strong>: detection, communication, rollback.</li><li><strong>Action items</strong> with an owner and a deadline. Not everything needs to be fixed; some things are <em>accepted as risk</em> with justification.</li></ul><p>Share internally without censorship. Failures are expensive teachers — use them. Blameless culture gives the team psychological safety to <em>report</em>; without it, the next incidents will be hidden.</p><h3>5. DORA metrics + DevSecOps</h3><p>The <a href='https://dora.dev/'>DORA report</a> identifies 4 metrics that separate elite teams:</p><ul><li><strong>Lead time</strong>: from commit to prod.</li><li><strong>Deployment frequency</strong>: how many times per day/week.</li><li><strong>Change failure rate</strong>: % of deploys that cause problems.</li><li><strong>MTTR</strong>: mean time to recover.</li></ul><p>Security metrics that couple well:</p><ul><li><strong>Patching SLA</strong>: critical in 72h, high in 7 days, medium in 30 days. Measure % within SLA.</li><li><strong>MTTD</strong>: mean time to detect an incident.</li><li><strong>SAST/SCA coverage</strong>: % of repos with an active pipeline.</li><li><strong>False positives suppressed with justification</strong> (program quality).</li><li><strong>Threat models per release</strong>.</li><li><strong>Average time on an internal CTF quiz</strong> (if you run one).</li></ul><p>Caution: metrics become perverse competition. If you measure 'CVEs closed', people will close trivia and ignore highs. Aim for <em>behavior</em> metrics, not output metrics.</p><h3>6. Security champions</h3><p>Scaling model: instead of centralizing everything in the security team (which becomes a bottleneck), plant 'champions' inside each squad — developers interested in the topic.</p><p>How to run it:</p><ol><li>Each squad chooses (does not impose) a champion.</li><li>Monthly champions meetup with the security team: news brief, recent cases, tools.</li><li>Enablement track: courses, internal CTFs, conferences.</li><li>Real recognition: annual award, mention in performance review.</li><li>Champions are a <em>focal point</em>, not sole owners.</li></ol><p>Result: the security team scales 5-10x without increasing headcount.</p><h3>7. OWASP SAMM, maturity model</h3><p>SAMM (Software Assurance Maturity Model) evaluates 5 functions:</p><ol><li><strong>Governance</strong> (strategy, policy, education)</li><li><strong>Design</strong> (threat modeling, requirements)</li><li><strong>Implementation</strong> (secure build, hardening)</li><li><strong>Verification</strong> (test/SAST/DAST, code review)</li><li><strong>Operations</strong> (incident, vulnerability mgmt, env hardening)</li></ol><p>Each one on 4 levels (0=absent, 3=optimized). Use it as an investment map — take the two weakest functions and prioritize them.</p><h3>8. Organizational anti-patterns</h3><table><tr><td><strong>Security team as a gate</strong></td><td>Manual approval of every deploy. Becomes a bottleneck, creates friction, forces teams to work around it.</td></tr><tr><td><strong>Purchase-led</strong></td><td>Buy a US$ 200k/year tool without defining how it will be used. Expensive shelfware.</td></tr><tr><td><strong>Vanity metrics</strong></td><td>'We blocked 1M attacks!' without saying which were bots vs humans.</td></tr><tr><td><strong>Pushing debt</strong></td><td>'Fix it after the release' indefinitely. Interest arrives as an incident.</td></tr><tr><td><strong>Heroism</strong></td><td>One person carries everything. When they leave, the program collapses.</td></tr><tr><td><strong>Compliance theater</strong></td><td>Performing for the auditor without protecting anything in practice.</td></tr></table><h3>9. Real case: Microsoft's transformation</h3><p>After years of attacks (Slammer, Blaster, etc.), Bill Gates sent a 2002 email to the entire company: 'Trustworthy Computing'. Before long:</p><ul><li>Mandatory SDL training for 8000+ engineers.</li><li>Mandatory threat modeling for any relevant feature.</li><li>SDL (Security Development Lifecycle) became part of the standard process.</li><li>Internalization of fuzzing, code analysis, pentest.</li></ul><p>Result: 5 years later, Microsoft went from 'security punchline' to an industry reference, and opened the playbook for everyone. That is culture.</p><h3>10. Summary: what remains when processes fail</h3><p>Culture is what remains when processes fail. When an engineer sees a vulnerability in a colleague's code and opens a PR fixing it — culture. When a PM accepts delaying a feature to close security debt — culture. When the CEO reacts to an incident with 'what do we need so this does not happen again?' instead of 'who do we fire?' — culture.</p><p>Tools help. Process organizes. Culture sustains.</p>
"""
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
                "practical_en": (
                    "Pick a feature your team will build in the next 2 weeks (e.g. avatar "
                    "upload, report export, social login). Do a 1-page STRIDE threat "
                    "model:<br>(1) Flow diagram (simple data flow diagram).<br>(2) List 1 threat "
                    "per STRIDE category — 6 total.<br>(3) For each one, write 1 concrete "
                    "mitigation.<br>(4) For each mitigation, mark: 'we already have it / we will "
                    "implement / we accept as risk'.<br>(5) Share with the team. Ask for honest "
                    "critique.<br>(6) Bonus: after the feature deploys, review the doc — how "
                    "many mitigations actually landed? What did you learn?"
                ),
            },
            "materials": [
                m("DevSecOps Manifesto", "https://www.devsecops.org/", "article", "", title_en="DevSecOps Manifesto", description_en=""),
                m("Google SRE Book, Postmortem Culture",
                  "https://sre.google/sre-book/postmortem-culture/", "book", "", title_en="Google SRE Book, Postmortem Culture", description_en=""),
                m("OWASP SAMM", "https://owaspsamm.org/", "docs",
                  "Modelo de maturidade em segurança de software.", title_en="OWASP SAMM", description_en="A software security maturity model."),
                m("ThoughtWorks Tech Radar",
                  "https://www.thoughtworks.com/radar", "article", "", title_en="ThoughtWorks Tech Radar", description_en=""),
                m("Microsoft STRIDE",
                  "https://learn.microsoft.com/azure/security/develop/threat-modeling-tool-threats",
                  "docs", "", title_en="Microsoft STRIDE", description_en=""),
                m("DORA: Accelerate State of DevOps",
                  "https://dora.dev/research/", "article",
                  "Pesquisa anual com métricas de elite.", title_en="DORA: Accelerate State of DevOps", description_en="Annual research with elite-team metrics."),
            ],
            "questions": [
                q("O que significa 'shift-left' em DevSecOps?",
                  "Trazer segurança para fases iniciais do desenvolvimento.",
                  ["Empurrar grande parte da validação de segurança para o fim do pipeline de deploy.",
                   "Mudar a posição da janela de monitoramento para o lado esquerdo da tela.",
                   "Ignorar completamente a etapa de segurança no momento final do deploy."],
                  "Linter no editor, SAST no PR, feedback rápido em vez de bloqueio no fim.",
                  statement_en="What does 'shift-left' mean in DevSecOps?",
                  correct_en="Bringing security into the early phases of development.",
                  wrong_en=[
                    "Pushing most security validation to the end of the deploy pipeline.",
                    "Moving the monitoring window to the left side of the screen.",
                    "Completely skipping the security step at the final moment of deploy."
                ],
                  explanation_en="Linter in the editor, SAST on the PR, fast feedback instead of a gate at"
                  "the end."),
                q("STRIDE serve para:",
                  "Threat modeling (Spoofing, Tampering, Repudiation, Info disclosure, DoS, Elevation).",
                  ["Formatos de log estruturado usados por ferramenta de observabilidade moderna, não modelagem.",
                   "Tipos de certificado TLS aceitos por navegador e servidor web atual, sem relação com ameaça.",
                   "Modos de execução de container, como privileged e rootless, definidos no runtime escolhido."],
                  "Cada letra é uma categoria, força você a pensar fora da sua zona.",
                  statement_en="STRIDE is used for:",
                  correct_en="Threat modeling (Spoofing, Tampering, Repudiation, Info disclosure, DoS, Elevation).",
                  wrong_en=[
                    "Structured log formats used by modern observability tools, not threat modeling.",
                    "TLS certificate types accepted by current browsers and web servers, unrelated to threats.",
                    "Container execution modes such as privileged and rootless, defined by the chosen runtime."
                ],
                  explanation_en="Each letter is a category — it forces you to think outside your usual zone."),
                q("O que é um postmortem 'blameless'?",
                  "Foco em causas sistêmicas, não em culpar pessoas.",
                  ["Documento secreto que só a liderança sênior tem permissão de ler.",
                   "Backup periódico do banco de dados, feito de forma automática diária.",
                   "Substituto formal do SLA assinado com o cliente antes do incidente."],
                  "Cultura blameless dá segurança psicológica para o time relatar erros honestamente.",
                  statement_en="What is a 'blameless' postmortem?",
                  correct_en="Focus on systemic causes, not blaming people.",
                  wrong_en=[
                    "A secret document that senior leadership alone is allowed to read.",
                    "A periodic database backup, done automatically every day.",
                    "A formal substitute for the SLA signed with the customer before the incident."
                ],
                  explanation_en="Blameless culture gives psychological safety for the team to report"
                  "mistakes honestly."),
                q("MTTR mede:",
                  "Tempo médio para restauração após incidente.",
                  ["Quantidade total de bug reportado durante um trimestre inteiro.",
                   "Tempo de boot do servidor, medido do desligamento até voltar.",
                   "Latência de rede entre dois pontos medidos durante o incidente."],
                  "Junto com MTTD, é métrica DORA de operação. Menor = melhor.",
                  statement_en="MTTR measures:",
                  correct_en="Mean time to restore after an incident.",
                  wrong_en=[
                    "The total number of bugs reported during an entire quarter.",
                    "Server boot time, measured from shutdown until it comes back.",
                    "Network latency between two points measured during the incident."
                ],
                  explanation_en="Together with MTTD, it is a DORA operations metric. Lower is better."),
                q("Qual NÃO é prática DevSecOps?",
                  "Atrasar correções para depois do release.",
                  ["Fazer threat modeling logo na fase de design da revisão.",
                   "Rotacionar segredo de acesso periodicamente conforme política interna.",
                   "Automatizar execução de SAST diretamente dentro do pipeline de CI."],
                  "Empurrar débito de segurança para depois é como deixar de pagar boleto: "
                  "juros (incidente) chegam.",
                  statement_en="Which is NOT a DevSecOps practice?",
                  correct_en="Delaying fixes until after the release.",
                  wrong_en=[
                    "Doing threat modeling early in the design review phase.",
                    "Rotating access secrets periodically per internal policy.",
                    "Automating SAST execution directly inside the CI pipeline."
                ],
                  explanation_en="Pushing security debt to later is like skipping a bill — interest (the"
                  "incident) arrives."),
                q("DevSecOps depende mais de:",
                  "Cultura e responsabilidade compartilhada.",
                  ["Comprar a ferramenta de segurança mais cara disponível no mercado.",
                   "Ignorar completamente a opinião do time de desenvolvimento no processo.",
                   "Centralizar boa parte da decisão de segurança dentro de um único time isolado."],
                  "Ferramenta sem cultura vira shelfware caro.",
                  statement_en="DevSecOps depends more on:",
                  correct_en="Culture and shared responsibility.",
                  wrong_en=[
                    "Buying the most expensive security tool available on the market.",
                    "Completely ignoring the development team's opinion in the process.",
                    "Centralizing most security decisions inside a single isolated team."
                ],
                  explanation_en="A tool without culture becomes expensive shelfware."),
                q("OWASP SAMM é:",
                  "Um modelo de maturidade em segurança de software.",
                  ["Um padrão de criptografia usado para proteger dado em repouso.",
                   "Um framework JavaScript usado para construir interface de usuário.",
                   "Um banco de dados relacional usado para guardar log de auditoria."],
                  "Avalia 5 funções (governança, design, implementação, verificação, operações) em 4 níveis.",
                  statement_en="OWASP SAMM is:",
                  correct_en="A software security maturity model.",
                  wrong_en=[
                    "An encryption standard used to protect data at rest.",
                    "A JavaScript framework used to build user interfaces.",
                    "A relational database used to store audit logs."
                ],
                  explanation_en="It evaluates 5 functions (governance, design, implementation, verification,"
                  "operations) across 4 levels."),
                q("Como medir maturidade do pipeline?",
                  "Definindo KPIs como cobertura SAST, SCA, falsos positivos e tempo de patch.",
                  ["Contando o número total de linha de código escrita pelo time inteiro.",
                   "Somando o número de commits feitos por cada desenvolvedor durante o mês inteiro.",
                   "Medindo o tamanho final do binário compilado e gerado ao término do pipeline."],
                  "Métrica precisa estar atrelada a comportamento, não vira competição numérica vazia.",
                  statement_en="How do you measure pipeline maturity?",
                  correct_en="By defining KPIs such as SAST/SCA coverage, false positives, and patch time.",
                  wrong_en=[
                    "By counting the total number of lines of code written by the whole team.",
                    "By summing the number of commits each developer made during the entire month.",
                    "By measuring the final size of the binary compiled at the end of the pipeline."
                ],
                  explanation_en="Metrics need to be tied to behavior, not become empty numeric competition."),
                q("Threat modeling é mais útil:",
                  "Cedo, no design, antes do código existir.",
                  ["Depois que o incidente já aconteceu e o dano está feito.",
                   "Exclusivamente quando a aplicação já está rodando em produção.",
                   "Só quando o time está construindo um aplicativo mobile específico."],
                  "Mudar arquitetura pré-código é barato; pós-deploy é caro e político.",
                  statement_en="Threat modeling is most useful:",
                  correct_en="Early, during design, before the code exists.",
                  wrong_en=[
                    "After the incident has already happened and the damage is done.",
                    "Exclusively when the application is already running in production.",
                    "When the team is building a specific mobile application exclusively."
                ],
                  explanation_en="Changing architecture pre-code is cheap; post-deploy is expensive and political."),
                q("Quem é responsável pela segurança em DevSecOps?",
                  "Todos no time, com champions de segurança apoiando.",
                  ["Só o blue team interno, sem envolvimento de mais ninguém no processo.",
                   "Só o time de auditoria externa contratado especificamente para isso.",
                   "Só a pessoa que ocupa o cargo de CISO dentro da empresa."],
                  "Modelo distribuído ('shift-everywhere') escala muito melhor que centralizado.",
                  statement_en="Who is responsible for security in DevSecOps?",
                  correct_en="Everyone on the team, with security champions supporting.",
                  wrong_en=[
                    "Just the internal blue team, with nobody else involved in the process.",
                    "Just the external audit team hired specifically for that purpose.",
                    "Just the person who holds the CISO role inside the company."
                ],
                  explanation_en="A distributed model ('shift-everywhere') scales much better than a"
                  "centralized one."),
            ],
        },
    ],
}
