"""Fase 4, Containers e Modernização (Platform Engineering)."""
from ._helpers import m, q

PHASE4 = {
    "name": "Fase 4: Containers e Modernização (Platform Engineering)",
    "name_en": "Phase 4: Containers and Modernization (Platform Engineering)",
    "description": "O primeiro passo em direção aos microsserviços.",
    "description_en": "The first step toward microservices.",
    "topics": [
        # =====================================================================
        # 4.1 Docker Fundamentals
        # =====================================================================
        {
            "title": "Docker Fundamentals",
            "title_en": "Docker Fundamentals",
            "summary": "Como empacotar sua aplicação e dependências.",
            "summary_en": "How to package your application and its dependencies.",
            "lesson": {
                "intro": (
                    "'Funciona na minha máquina' é a piada mais antiga e mais cara da "
                    "engenharia de software. Por décadas, deploy era pesadelo: dev usava "
                    "Ubuntu 18.04 com Python 3.8 + libssl 1.1 + glibc 2.27, prod tinha "
                    "CentOS 7 com Python 3.6 + libssl 1.0 + glibc 2.17. App quebrava em "
                    "lugares que ninguém previa. Containers resolveram isso ao empacotar "
                    "<em>tudo</em> que o app precisa, código, runtime, libs, deps de "
                    "sistema, em uma imagem reproduzível. Roda igual em qualquer host com "
                    "kernel Linux compatível. Esta aula vai do que é container internamente "
                    "(namespaces + cgroups), passa por Dockerfile produtivo, multi-stage "
                    "builds, redes, volumes, healthchecks e termina em padrões 12-factor. "
                    "Sem fundação sólida aqui, K8s vira mistério depois."
                ),
                "intro_en": (
                    "'It works on my machine' is the oldest and most expensive joke in "
                    "software engineering. For decades, deployment was a nightmare: dev "
                    "used Ubuntu 18.04 with Python 3.8 + libssl 1.1 + glibc 2.27, prod had "
                    "CentOS 7 with Python 3.6 + libssl 1.0 + glibc 2.17. The app broke in "
                    "places nobody predicted. Containers solved this by packaging "
                    "<em>everything</em> the app needs, code, runtime, libs, system deps, "
                    "into a reproducible image. It runs the same on any host with a "
                    "compatible Linux kernel. This lesson goes from what a container "
                    "actually is internally (namespaces + cgroups), through a production "
                    "Dockerfile, multi-stage builds, networking, volumes, healthchecks, and "
                    "ends on 12-factor patterns. Without a solid foundation here, K8s turns "
                    "into a mystery later."
                ),
                "body": (
                """<h3>1. Um container, fisicamente: processos Linux comuns, isolados por primitivas do kernel</h3>
<p>Um container NÃO é uma VM leve, apesar da comparação comum — é um ou
mais processos Linux completamente normais, isolados dos demais processos
do sistema por primitivas específicas do próprio kernel, sem nenhuma
camada de virtualização de hardware. Os <strong>namespaces</strong> são
o mecanismo central de isolamento: o namespace <code>PID</code> faz com
que processos dentro do container só enxerguem outros processos do mesmo
container — o processo principal da aplicação vira PID 1 dentro desse
mundo isolado, mesmo tendo um PID diferente e "normal" visto de fora,
pelo host; o namespace <code>NET</code> dá ao container sua própria
interface de rede, tabela de roteamento e regras de iptables,
independentes do host; <code>MNT</code> isola o filesystem visível;
<code>UTS</code> dá hostname próprio; <code>IPC</code> isola memória
compartilhada e semáforos; <code>USER</code> permite mapear UID/GID de
forma que "root" dentro do container não seja necessariamente root no
host (quando configurado); e até o próprio <code>cgroup</code> e o
relógio (<code>time</code>, mais raro) podem ser namespaced. Os
<strong>cgroups</strong> impõem os LIMITES de recurso — CPU, memória,
I/O, número máximo de processos — sem eles, um único container pode
consumir 100% da CPU ou RAM do host inteiro, afetando todos os outros
processos e containers rodando ali. <strong>Capabilities</strong>
subdividem o poder de root em unidades granulares: em vez de "root pode
fazer absolutamente tudo", um processo pode receber só
<code>NET_BIND_SERVICE</code> (a capacidade específica de abrir uma
porta abaixo de 1024) sem ganhar nenhum dos outros poderes de root.
<strong>Seccomp</strong> filtra quais syscalls o processo tem permissão
de chamar ao kernel. E AppArmor/SELinux acrescentam controle de acesso
obrigatório como camada complementar. Você pode observar esse isolamento
diretamente:</p>
<div class="mermaid">
flowchart TB
    Host["Host Linux, um kernel"] --> NS["Namespaces: PID, NET, MNT, UTS, IPC, USER"]
    Host --> CG["cgroups: CPU, memória, I/O"]
    NS --> C1["Container A isolado"]
    NS --> C2["Container B isolado"]
    CG --> C1
    CG --> C2
</div>

<pre><code>$ docker run -d --name web nginx
$ docker top web
PID  USER   CMD
1234 root   nginx: master process
$ ps -ef | grep 1234
root  1234  ...  nginx: master process   # mesmo PID, mas só visível no host</code></pre>
<p>O fato de o container COMPARTILHAR o kernel do host é exatamente o
que o torna leve — sem boot próprio, sem kernel dedicado, sem hardware
virtualizado. O trade-off inevitável: um container Linux só roda
nativamente em host Linux — é por isso que Docker Desktop no Mac e
Windows precisa rodar uma VM Linux por trás das cortinas.</p>

<h3>2. Imagem, container, registry, tag, digest: cinco termos que se confundem no começo</h3>
<p>Uma <strong>imagem</strong> é um template imutável — um snapshot do
filesystem mais metadados (CMD, ENV, EXPOSE) — composto de várias camadas
somente-leitura empilhadas via overlayfs. Um <strong>container</strong>
é uma INSTÂNCIA em execução dessa imagem, com uma camada adicional
GRAVÁVEL por cima — você pode subir cem containers a partir da mesma
imagem, cada um com suas próprias variáveis de ambiente, volumes e redes,
sem que um afete o outro. Um <strong>registry</strong> armazena e serve
imagens (Docker Hub, GHCR, ECR). Uma <strong>tag</strong> é um alias
humano legível para um digest específico — <code>nginx:1.25.3</code> na
verdade aponta para um hash sha256 concreto por trás. E o
<strong>digest</strong> (<code>sha256:f0a1b2...</code>) é o identificador
imutável de verdade — diferente da tag, ele nunca muda de conteúdo, o que
o torna a única referência verdadeiramente confiável para reproduzir
exatamente a mesma imagem depois.</p>

<h3>3. Dockerfile produtivo: por que a ORDEM das instruções decide a velocidade do build</h3>
<p>Cada instrução do Dockerfile vira uma camada CACHEADA — e o Docker só
reconstrói uma camada (e todas as que vêm depois dela) se algo relevante
mudou. Isso torna a ordem das instruções uma decisão de desempenho, não
só de estilo:</p>
<pre><code># Dockerfile RUIM (cache invalida toda hora)
FROM python:3.12
COPY . /app                    # qualquer mudança em código invalida tudo abaixo
RUN pip install -r /app/requirements.txt
WORKDIR /app
CMD ["python", "main.py"]</code></pre>
<pre><code># Dockerfile BOM (cache amigável)
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copia só requirements primeiro, camada cacheada se reqs não mudam
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código por último, mudanças aqui não invalidam pip install
COPY . .

RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \\
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]</code></pre>
<p>A versão ruim copia TODO o código antes de instalar dependências —
qualquer alteração de uma linha de código, mesmo sem tocar em
<code>requirements.txt</code>, invalida a camada de <code>COPY</code> e
força reinstalar TODAS as dependências do zero a cada build. A versão
boa copia só <code>requirements.txt</code> primeiro, instala
dependências, e SÓ ENTÃO copia o resto do código — mudanças de código
comuns (o caso mais frequente) não tocam a camada cara de instalação de
dependências. Outros detalhes que compõem um Dockerfile de produção:
base <code>slim</code>/<code>alpine</code>/distroless reduz bytes e
superfície de CVE; uma tag ESPECÍFICA (<code>3.12-slim</code>, nunca
<code>latest</code> ou só <code>3</code>) garante reprodutibilidade;
<code>PYTHONUNBUFFERED=1</code> garante que logs cheguem ao stdout sem
buffer interno do Python atrasando a visibilidade; <code>USER</code>
não-root aplica o princípio de menor privilégio — se um atacante
escapar da aplicação, não herda root automaticamente; <code>HEALTHCHECK</code>
dá ao orquestrador uma forma de saber se a aplicação está de fato
RESPONDENDO, não só "o processo ainda existe"; e usar a forma JSON de
<code>CMD</code> (<code>["app"]</code>, não uma string) evita que o
comando passe por um shell intermediário, eliminando expansão de
variável acidental.</p>

<h3>4. Multi-stage build: compilar numa imagem "gorda", rodar numa mínima</h3>
<p>A técnica de multi-stage usa uma imagem completa (com toolchain de
compilação inteira) só para o BUILD, e copia apenas o resultado final
para uma imagem mínima de runtime — reduzindo o tamanho final em ordens
de grandeza:</p>
<pre><code># Stage 1: build com toolchain completa
FROM golang:1.22 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags='-s -w' -o /out/app ./cmd/app

# Stage 2: runtime mínimo (distroless: sem shell, sem apt, ~20MB)
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /out/app /app
USER nonroot
EXPOSE 8080
ENTRYPOINT ["/app"]</code></pre>
<p>O resultado prático: ~20MB em vez de ~800MB da imagem de build
completa. E o ganho não é só de tamanho — uma imagem distroless não tem
shell nem gerenciador de pacotes, então um atacante que consiga executar
código dentro do container encontra um ambiente essencialmente vazio,
sem ferramentas básicas do sistema para explorar mais nada. O mesmo
padrão se aplica em Python, embora com uma nuance: como Python não
compila para binário nativo, o segundo estágio ainda precisa do
interpretador, mas mesmo assim se beneficia de excluir o toolchain de
compilação (gcc, headers de desenvolvimento) usado só para instalar
dependências com extensões nativas:</p>
<pre><code>FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \\
      build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \\
      libpq5 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY . .
ENV PATH="/opt/venv/bin:$PATH"
RUN useradd -m -u 1000 app && chown -R app /app
USER app
CMD ["gunicorn", "app.wsgi"]</code></pre>

<h3>5. Networking: por que "conversar por IP" só funciona até você recriar um container</h3>
<p>O Docker oferece vários modelos de rede, cada um com um trade-off
distinto. <strong>bridge</strong> (o padrão) cria uma rede privada
gerenciada pelo daemon — containers conversam por IP, mas resolução por
NOME só funciona numa <em>user-defined bridge</em>. <strong>user-defined
bridge</strong> é o padrão recomendado para aplicações multi-container:
containers na mesma rede se resolvem por NOME via DNS interno, o que
sobrevive a recriações onde o IP mudaria. <strong>host</strong> faz o
container compartilhar a pilha de rede do próprio host diretamente —
desempenho máximo, mas sem isolamento de porta nenhum, um trade-off de
segurança real. <strong>none</strong> desliga rede completamente.
<strong>overlay</strong> conecta containers através de múltiplos hosts
(usado por Swarm e conceitualmente por Kubernetes). E
<strong>macvlan</strong> dá ao container um endereço MAC próprio,
fazendo-o aparecer como um dispositivo físico independente na rede:</p>
<div class="mermaid">
flowchart LR
    Web["serviço web"] --> Br["rede bridge"]
    Api["serviço api"] --> Br
    Br --> Dns["DNS embutido: web resolve api pelo nome"]
</div>

<pre><code>$ docker network create app-net
$ docker run -d --name db --network app-net postgres
$ docker run -d --name api --network app-net -e DB_HOST=db myapp
# api consegue conectar em 'db' por nome (DNS interno)</code></pre>
<p><code>-p 8080:80</code> mapeia a porta 8080 do host para a porta 80
dentro do container — a forma padrão de expor uma porta de container
para fora, sem depender de rede <code>host</code>.</p>

<h3>6. Volumes: onde o dado sobrevive ao ciclo de vida do container</h3>
<p>Um <strong>volume nomeado</strong> é gerenciado inteiramente pelo
Docker, armazenado em <code>/var/lib/docker/volumes/</code>, e SOBREVIVE
a um <code>docker rm</code> do container que o usava — a escolha certa
para dado de produção que precisa persistir independente do ciclo de
vida do container. Um <strong>bind mount</strong> mapeia diretamente um
diretório do HOST para dentro do container — excelente em desenvolvimento
(código local refletido em tempo real dentro do container, sem rebuild),
mas exige cuidado com permissões e portabilidade em produção, já que
depende de um caminho específico do sistema de arquivos do host. Um
<strong>tmpfs mount</strong> vive inteiramente em RAM e desaparece junto
com o container — apropriado para dado sensível temporário que não deve
NUNCA tocar disco:</p>
<pre><code>$ docker volume create pgdata
$ docker run -d --name db -v pgdata:/var/lib/postgresql/data postgres

# Bind mount em dev
$ docker run -d -v $(pwd):/app -w /app python:3.12 python main.py

# tmpfs para sessões temporárias
$ docker run -d --tmpfs /tmp:rw,size=100m myapp</code></pre>

<h3>7. `.dockerignore`: economia de tempo e prevenção de vazamento acidental</h3>
<p><code>docker build</code> envia TODO o conteúdo do diretório atual (o
"contexto de build") para o daemon antes de começar a construir — sem um
<code>.dockerignore</code>, isso inclui <code>.git</code>,
<code>node_modules</code>, arquivos de log antigos, e potencialmente um
<code>.env</code> com segredos. O risco não é só velocidade: se o
Dockerfile fizer um <code>COPY . .</code> genérico, qualquer arquivo
sensível presente no diretório pode acabar DENTRO da imagem final,
visível para qualquer um com acesso a ela:</p>
<pre><code># .dockerignore
.git
.gitignore
node_modules/
__pycache__/
*.pyc
.pytest_cache/
.env
.env.*
*.log
.vscode/
.idea/
Dockerfile
docker-compose*.yml
README.md</code></pre>

<h3>8. Doze fatores aplicados a container: princípios que evitam a próxima dor de cabeça</h3>
<p>A metodologia 12-factor (originada na Heroku) mapeia diretamente para
boas práticas de container: configuração deve vir de variáveis de
ambiente, nunca de arquivos como <code>config.prod.yml</code> versus
<code>config.dev.yml</code> embutidos na imagem — a MESMA imagem serve
todos os ambientes, só o ambiente de execução muda. Logs vão para
stdout/stderr, nunca para arquivo — é o orquestrador (ou o próprio
Docker) quem captura e roteia esses logs, escrever em arquivo local
dentro do container é invisível para qualquer ferramenta de observabilidade
externa. A aplicação deve ser STATELESS — estado vive em banco ou cache
externos, não no filesystem local do container — o que permite escalar
horizontalmente sem coordenação especial entre réplicas. Build, Release e
Run são estágios SEPARADOS: a imagem é o build, o deploy é o release, o
container rodando é o run — misturar essas etapas dificulta rastrear em
qual estágio um problema surgiu. Um processo PRINCIPAL por container —
para lidar com o "problema do PID 1" (seção 9), use <code>tini</code> ou
<code>--init</code> em vez de rodar múltiplos processos via supervisor
interno. Disposability exige que a aplicação suba rápido (idealmente
menos de 5 segundos de cold start) e desligue de forma limpa,
respeitando SIGTERM e drenando conexões em andamento antes de sair. E
paridade dev/prod significa usar a MESMA imagem em desenvolvimento e
produção, minimizando diferenças que só aparecem "no ambiente real".</p>

<h3>9. O problema do PID 1, e por que sua aplicação provavelmente não deveria ser PID 1</h3>
<p>No Linux, o processo PID 1 carrega responsabilidades especiais que a
maioria das aplicações nunca foi desenhada para cumprir: ele deve adotar
processos órfãos e fazer "reaping" de processos zumbis, e precisa
propagar sinais corretamente para seus filhos. Uma aplicação Python ou
Node.js típica não implementa nada disso, porque nunca precisou — em
execução normal, o kernel/init do sistema cuida disso por ela. Dentro de
um container, se a aplicação for diretamente PID 1, três problemas
aparecem: subprocessos esquecidos viram zumbis e acumulam PIDs sem
limpeza; um SIGTERM enviado pelo <code>docker stop</code> pode nunca
chegar aos processos FILHOS da aplicação, só ao processo principal; e o
container demora o timeout completo (frequentemente 10 segundos) até ser
morto à força com SIGKILL, porque o encerramento gracioso nunca
aconteceu de verdade. A solução padrão é um init mínimo como
<code>tini</code>, que assume o papel de PID 1 de verdade e repassa
sinais e reaping corretamente para o processo real da aplicação:</p>
<pre><code>$ docker run --init myapp
# Ou no Dockerfile:
ENTRYPOINT ["tini", "--", "python", "main.py"]</code></pre>

<h3>10. BuildKit: o motor de build que resolve problemas que o build clássico nunca teve resposta</h3>
<p>BuildKit é o motor de build padrão atual, e resolve limitações reais
do sistema anterior: builds de estágios INDEPENDENTES rodam em paralelo,
em vez de sequencialmente; <code>--mount=type=cache</code> mantém um
cache PERSISTENTE entre builds (dependências de Node ou Python
reaproveitadas sem reinstalar do zero a cada vez); <code>--mount=type=secret</code>
permite passar um segredo durante o build SEM ele acabar gravado em
nenhuma camada da imagem final — resolvendo um vazamento clássico de
segredo em `ARG`; <code>--mount=type=ssh</code> encaminha um agente SSH
para dentro do build, permitindo clonar um repositório privado sem
embutir uma chave na imagem; e <code>buildx</code> permite build
multi-arquitetura (amd64 e arm64 na mesma pipeline):</p>
<pre><code># syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \\
    pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]</code></pre>

<h3>11. Comandos que resolvem o dia a dia, do build à inspeção</h3>
<pre><code># Lifecycle
docker build -t myapp:dev .
docker run -d --name app -p 8000:8000 myapp:dev
docker exec -it app sh                # entra no container
docker logs -f app                    # tail logs
docker stop app && docker rm app

# Inspeção
docker ps -a                          # listar (incluindo parados)
docker inspect app                    # JSON completo
docker stats                          # CPU/RAM em tempo real
docker diff app                       # mudanças no FS desde criação
docker history myapp:dev              # camadas

# Limpeza (cuidado!)
docker system prune -a --volumes      # remove tudo não usado</code></pre>
<p><code>docker diff</code> merece destaque: ele mostra exatamente o que
mudou no filesystem do container desde que foi criado, comparado com a
imagem original — útil tanto para debugar comportamento inesperado
quanto para investigar se algo persistiu escrita fora dos volumes
esperados, um sinal potencial de comprometimento.</p>

<h3>12. Nove anti-padrões que aparecem repetidamente em imagens reais</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Evite</strong><p>USER root, FROM latest, copiar .env, um estágio único gordo.</p></div>
    <div class="lesson-viz-card"><strong>Prefira</strong><p>USER não-root, tag/digest fixos, multi-stage, .dockerignore.</p></div>
  </div>
  <figcaption>Anti-padrões de imagem vs. base mínima segura.</figcaption>
</figure>

<ul>
<li><strong><code>FROM ubuntu:latest</code></strong>: irreproduzível —
fixe pelo menos a versão principal.</li>
<li><strong><code>USER root</code></strong> por padrão (não especificar
nenhum USER): um escape de container com configuração padrão vira root
no host.</li>
<li><strong>Múltiplos processos via supervisor interno</strong>:
complica logs, healthcheck e reinício — cada processo merece seu próprio
container, gerenciado pelo orquestrador.</li>
<li><strong>Senha em `ENV` dentro do Dockerfile</strong>: fica gravada
permanentemente na imagem, visível para qualquer um com
<code>docker history</code> — use secrets injetados em runtime.</li>
<li><strong><code>RUN apt update</code> numa camada separada do
`install`</strong>: cache desatualizado — sempre combine update e
install na MESMA instrução RUN.</li>
<li><strong>Imagem de 4GB</strong>: quase sempre otimizável com
multi-stage e base mais enxuta.</li>
<li><strong>Sem HEALTHCHECK</strong>: o orquestrador nunca descobre que
a aplicação travou internamente, mesmo com o processo ainda "vivo".</li>
<li><strong>Log em arquivo dentro do container</strong>: ninguém nunca
vê, porque nenhuma ferramenta de observabilidade externa consulta o
filesystem interno do container por padrão.</li>
<li><strong>Bind mount de `/var/run/docker.sock`</strong>: dá ao
container controle total sobre o daemon Docker do host — equivalente a
root no host instantaneamente, um dos vetores de escalada mais diretos
que existem.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. A container, physically: ordinary Linux processes isolated by kernel primitives</h3>
<p>A container is NOT a lightweight VM, despite the common comparison — it
is one or more completely normal Linux processes, isolated from the rest
of the system's processes by specific kernel-level primitives, with no
hardware virtualization layer at all. <strong>Namespaces</strong> are the
central isolation mechanism: the <code>PID</code> namespace makes
processes inside the container only see other processes in the same
container — the application's main process becomes PID 1 inside that
isolated world, even though it has a different, "normal" PID as seen from
outside, on the host; the <code>NET</code> namespace gives the container
its own network interface, routing table and iptables rules, independent
from the host; <code>MNT</code> isolates the visible filesystem;
<code>UTS</code> gives it its own hostname; <code>IPC</code> isolates
shared memory and semaphores; <code>USER</code> allows mapping UID/GID so
that "root" inside the container isn't necessarily root on the host (when
configured); and even <code>cgroup</code> itself and the clock
(<code>time</code>, rarer) can be namespaced. <strong>Cgroups</strong>
enforce resource LIMITS — CPU, memory, I/O, maximum number of processes —
without them, a single container can consume 100% of the host's entire
CPU or RAM, affecting every other process and container running there.
<strong>Capabilities</strong> subdivide root's power into granular units:
instead of "root can do absolutely everything", a process can be granted
just <code>NET_BIND_SERVICE</code> (the specific capability of opening a
port below 1024) without gaining any of root's other powers.
<strong>Seccomp</strong> filters which syscalls the process is allowed to
call into the kernel. And AppArmor/SELinux add mandatory access control
as a complementary layer. You can observe this isolation directly:</p>
<div class="mermaid">
flowchart TB
    Host["Linux host, one kernel"] --> NS["Namespaces: PID, NET, MNT, UTS, IPC, USER"]
    Host --> CG["cgroups: CPU, memory, I/O"]
    NS --> C1["Isolated container A"]
    NS --> C2["Isolated container B"]
    CG --> C1
    CG --> C2
</div>

<pre><code>$ docker run -d --name web nginx
$ docker top web
PID  USER   CMD
1234 root   nginx: master process
$ ps -ef | grep 1234
root  1234  ...  nginx: master process   # mesmo PID, mas só visível no host</code></pre>
<p>The fact that the container SHARES the host's kernel is exactly what
makes it lightweight — no boot of its own, no dedicated kernel, no
virtualized hardware. The unavoidable trade-off: a Linux container only
runs natively on a Linux host — that's why Docker Desktop on Mac and
Windows needs to run a Linux VM behind the scenes.</p>

<h3>2. Image, container, registry, tag, digest: five terms that get confused early on</h3>
<p>An <strong>image</strong> is an immutable template — a filesystem
snapshot plus metadata (CMD, ENV, EXPOSE) — made up of several read-only
layers stacked via overlayfs. A <strong>container</strong> is a RUNNING
INSTANCE of that image, with an additional WRITABLE layer on top — you
can spin up a hundred containers from the same image, each with its own
environment variables, volumes and networks, without one affecting the
other. A <strong>registry</strong> stores and serves images (Docker Hub,
GHCR, ECR). A <strong>tag</strong> is a human-readable alias for a
specific digest — <code>nginx:1.25.3</code> actually points to a concrete
sha256 hash behind the scenes. And the <strong>digest</strong>
(<code>sha256:f0a1b2...</code>) is the truly immutable identifier —
unlike the tag, it never changes content, which makes it the only truly
reliable reference to reproduce exactly the same image later.</p>

<h3>3. A production Dockerfile: why instruction ORDER decides build speed</h3>
<p>Every Dockerfile instruction becomes a CACHED layer — and Docker only
rebuilds a layer (and everything after it) if something relevant
changed. That makes instruction order a performance decision, not just a
style choice:</p>
<pre><code># Dockerfile RUIM (cache invalida toda hora)
FROM python:3.12
COPY . /app                    # qualquer mudança em código invalida tudo abaixo
RUN pip install -r /app/requirements.txt
WORKDIR /app
CMD ["python", "main.py"]</code></pre>
<pre><code># Dockerfile BOM (cache amigável)
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copia só requirements primeiro, camada cacheada se reqs não mudam
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código por último, mudanças aqui não invalidam pip install
COPY . .

RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \\
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]</code></pre>
<p>The bad version copies ALL the code before installing dependencies —
any single-line code change, even without touching
<code>requirements.txt</code>, invalidates the <code>COPY</code> layer
and forces reinstalling ALL dependencies from scratch on every build. The
good version copies only <code>requirements.txt</code> first, installs
dependencies, and ONLY THEN copies the rest of the code — common code
changes (the most frequent case) never touch the expensive dependency
installation layer. Other details that make up a production Dockerfile:
a <code>slim</code>/<code>alpine</code>/distroless base reduces bytes and
CVE surface; a SPECIFIC tag (<code>3.12-slim</code>, never
<code>latest</code> or just <code>3</code>) guarantees reproducibility;
<code>PYTHONUNBUFFERED=1</code> ensures logs reach stdout without
Python's internal buffer delaying visibility; a non-root <code>USER</code>
applies the principle of least privilege — if an attacker escapes the
application, they don't automatically inherit root; <code>HEALTHCHECK</code>
gives the orchestrator a way to know whether the application is actually
RESPONDING, not just "the process still exists"; and using the JSON form
of <code>CMD</code> (<code>["app"]</code>, not a string) avoids the
command going through an intermediate shell, eliminating accidental
variable expansion.</p>

<h3>4. Multi-stage build: compile in a "fat" image, run from a minimal one</h3>
<p>The multi-stage technique uses a full image (with the entire
compilation toolchain) just for the BUILD, and copies only the final
result into a minimal runtime image — reducing the final size by orders
of magnitude:</p>
<pre><code># Stage 1: build com toolchain completa
FROM golang:1.22 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags='-s -w' -o /out/app ./cmd/app

# Stage 2: runtime mínimo (distroless: sem shell, sem apt, ~20MB)
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /out/app /app
USER nonroot
EXPOSE 8080
ENTRYPOINT ["/app"]</code></pre>
<p>The practical result: ~20MB instead of ~800MB for the full build
image. And the gain isn't just size — a distroless image has no shell and
no package manager, so an attacker who manages to execute arbitrary code
inside the container finds an essentially empty environment, with no
basic system tools to explore anything further. The same pattern applies
to Python, though with a nuance: since Python doesn't compile to a native
binary, the second stage still needs the interpreter, but it still
benefits from excluding the compilation toolchain (gcc, dev headers) used
only to install dependencies with native extensions:</p>
<pre><code>FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \\
      build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \\
      libpq5 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY . .
ENV PATH="/opt/venv/bin:$PATH"
RUN useradd -m -u 1000 app && chown -R app /app
USER app
CMD ["gunicorn", "app.wsgi"]</code></pre>

<h3>5. Networking: why "talking by IP" only works until you recreate a container</h3>
<p>Docker offers several networking models, each with a distinct
trade-off. <strong>bridge</strong> (the default) creates a private
network managed by the daemon — containers talk over IP, but NAME
resolution only works on a <em>user-defined bridge</em>.
<strong>user-defined bridge</strong> is the recommended default for
multi-container applications: containers on the same network resolve
each other by NAME via internal DNS, which survives recreations where the
IP would change. <strong>host</strong> makes the container share the
host's own network stack directly — maximum performance, but with zero
port isolation, a real security trade-off. <strong>none</strong> turns
networking off completely. <strong>overlay</strong> connects containers
across multiple hosts (used by Swarm and conceptually by Kubernetes). And
<strong>macvlan</strong> gives the container its own MAC address, making
it appear as an independent physical device on the network:</p>
<div class="mermaid">
flowchart LR
    Web["web service"] --> Br["bridge network"]
    Api["api service"] --> Br
    Br --> Dns["Built-in DNS: web resolves api by name"]
</div>

<pre><code>$ docker network create app-net
$ docker run -d --name db --network app-net postgres
$ docker run -d --name api --network app-net -e DB_HOST=db myapp
# api consegue conectar em 'db' por nome (DNS interno)</code></pre>
<p><code>-p 8080:80</code> maps host port 8080 to container port 80 — the
standard way to expose a container's port to the outside, without relying
on <code>host</code> networking.</p>

<h3>6. Volumes: where data survives the container's lifecycle</h3>
<p>A <strong>named volume</strong> is managed entirely by Docker, stored
under <code>/var/lib/docker/volumes/</code>, and SURVIVES a
<code>docker rm</code> of the container that used it — the right choice
for production data that must persist independent of the container's
lifecycle. A <strong>bind mount</strong> maps a HOST directory directly
into the container — excellent for development (local code reflected
inside the container in real time, no rebuild), but requires care with
permissions and portability in production, since it depends on a
specific path on the host's filesystem. A <strong>tmpfs mount</strong>
lives entirely in RAM and disappears along with the container —
appropriate for temporary sensitive data that must NEVER touch disk:</p>
<pre><code>$ docker volume create pgdata
$ docker run -d --name db -v pgdata:/var/lib/postgresql/data postgres

# Bind mount em dev
$ docker run -d -v $(pwd):/app -w /app python:3.12 python main.py

# tmpfs para sessões temporárias
$ docker run -d --tmpfs /tmp:rw,size=100m myapp</code></pre>

<h3>7. `.dockerignore`: saving build time and preventing accidental leakage</h3>
<p><code>docker build</code> sends ALL the contents of the current
directory (the "build context") to the daemon before starting the build
— without a <code>.dockerignore</code>, this includes <code>.git</code>,
<code>node_modules</code>, old log files, and potentially a
<code>.env</code> with secrets. The risk isn't just speed: if the
Dockerfile does a generic <code>COPY . .</code>, any sensitive file
present in the directory can end up INSIDE the final image, visible to
anyone with access to it:</p>
<pre><code># .dockerignore
.git
.gitignore
node_modules/
__pycache__/
*.pyc
.pytest_cache/
.env
.env.*
*.log
.vscode/
.idea/
Dockerfile
docker-compose*.yml
README.md</code></pre>

<h3>8. Twelve factors applied to containers: principles that avoid the next headache</h3>
<p>The 12-factor methodology (originating at Heroku) maps directly to
container best practices: configuration must come from environment
variables, never from files like <code>config.prod.yml</code> versus
<code>config.dev.yml</code> baked into the image — the SAME image serves
every environment, only the runtime environment changes. Logs go to
stdout/stderr, never to a file — it's the orchestrator (or Docker itself)
that captures and routes those logs; writing to a local file inside the
container is invisible to any external observability tool. The
application must be STATELESS — state lives in an external database or
cache, not on the container's local filesystem — which allows horizontal
scaling without special coordination between replicas. Build, Release and
Run are SEPARATE stages: the image is the build, the deploy is the
release, the running container is the run — mixing these stages makes it
harder to trace which stage a problem originated in. One MAIN process per
container — to handle the "PID 1 problem" (section 9), use
<code>tini</code> or <code>--init</code> instead of running multiple
processes via an internal supervisor. Disposability requires the
application to start fast (ideally under 5 seconds of cold start) and
shut down cleanly, respecting SIGTERM and draining in-flight connections
before exiting. And dev/prod parity means using the SAME image in
development and production, minimizing differences that only show up "in
the real environment".</p>

<h3>9. The PID 1 problem, and why your application probably shouldn't be PID 1</h3>
<p>On Linux, the PID 1 process carries special responsibilities that most
applications were never designed to fulfill: it must adopt orphaned
processes and reap zombie processes, and it needs to propagate signals
correctly to its children. A typical Python or Node.js application
implements none of this, because it never had to — under normal
execution, the system's kernel/init handles it. Inside a container, if
the application is directly PID 1, three problems appear: forgotten
subprocesses become zombies and accumulate PIDs with no cleanup; a
SIGTERM sent by <code>docker stop</code> may never reach the
application's CHILD processes, only the main process; and the container
takes the full timeout (often 10 seconds) before being force-killed with
SIGKILL, because graceful shutdown never actually happened. The standard
solution is a minimal init like <code>tini</code>, which takes on the
real PID 1 role and correctly forwards signals and reaping to the actual
application process:</p>
<pre><code>$ docker run --init myapp
# Ou no Dockerfile:
ENTRYPOINT ["tini", "--", "python", "main.py"]</code></pre>

<h3>10. BuildKit: the build engine that solves problems the classic builder never answered</h3>
<p>BuildKit is the current default build engine, and it solves real
limitations of the previous system: INDEPENDENT stage builds run in
parallel instead of sequentially; <code>--mount=type=cache</code> keeps a
PERSISTENT cache between builds (Node or Python dependencies reused
instead of reinstalled from scratch every time);
<code>--mount=type=secret</code> lets you pass a secret during the build
WITHOUT it ending up written into any layer of the final image —
resolving a classic secret leak via `ARG`; <code>--mount=type=ssh</code>
forwards an SSH agent into the build, allowing you to clone a private
repository without embedding a key in the image; and <code>buildx</code>
enables multi-architecture builds (amd64 and arm64 in the same
pipeline):</p>
<pre><code># syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \\
    pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]</code></pre>

<h3>11. Commands that handle day-to-day work, from build to inspection</h3>
<pre><code># Lifecycle
docker build -t myapp:dev .
docker run -d --name app -p 8000:8000 myapp:dev
docker exec -it app sh                # entra no container
docker logs -f app                    # tail logs
docker stop app && docker rm app

# Inspeção
docker ps -a                          # listar (incluindo parados)
docker inspect app                    # JSON completo
docker stats                          # CPU/RAM em tempo real
docker diff app                       # mudanças no FS desde criação
docker history myapp:dev              # camadas

# Limpeza (cuidado!)
docker system prune -a --volumes      # remove tudo não usado</code></pre>
<p><code>docker diff</code> deserves a mention: it shows exactly what
changed in the container's filesystem since it was created, compared to
the original image — useful both for debugging unexpected behavior and
for investigating whether something wrote outside the expected volumes, a
potential sign of compromise.</p>

<h3>12. Nine anti-patterns that repeatedly show up in real images</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Avoid</strong><p>USER root, FROM latest, copying .env, one fat single stage.</p></div>
    <div class="lesson-viz-card"><strong>Prefer</strong><p>Non-root USER, pinned tag/digest, multi-stage, .dockerignore.</p></div>
  </div>
  <figcaption>Image anti-patterns vs. a minimal secure baseline.</figcaption>
</figure>

<ul>
<li><strong><code>FROM ubuntu:latest</code></strong>: not reproducible —
pin at least the major version.</li>
<li><strong><code>USER root</code></strong> by default (not specifying
any USER): a container escape with default configuration becomes root on
the host.</li>
<li><strong>Multiple processes via an internal supervisor</strong>:
complicates logs, healthchecks and restarts — each process deserves its
own container, managed by the orchestrator.</li>
<li><strong>Password in `ENV` inside the Dockerfile</strong>: stays
permanently baked into the image, visible to anyone with
<code>docker history</code> — use secrets injected at runtime.</li>
<li><strong><code>RUN apt update</code> in a layer separate from
`install`</strong>: stale cache — always combine update and install in
the SAME RUN instruction.</li>
<li><strong>4GB image</strong>: almost always optimizable with
multi-stage and a leaner base.</li>
<li><strong>No HEALTHCHECK</strong>: the orchestrator never discovers
that the application hung internally, even with the process still
"alive".</li>
<li><strong>Logging to a file inside the container</strong>: nobody ever
sees it, because no external observability tool queries the container's
internal filesystem by default.</li>
<li><strong>Bind mount of `/var/run/docker.sock`</strong>: gives the
container full control over the host's Docker daemon — instantly
equivalent to root on the host, one of the most direct escalation vectors
that exist.</li>
</ul>"""
                ),
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Escreva Dockerfile multi-stage para app Python: stage builder "
                    "com toolchain, stage final com python:3.12-slim, USER não-root, "
                    "HEALTHCHECK, CMD em JSON.</li>"
                    "<li>Crie .dockerignore excluindo .git, .env, __pycache__, etc.</li>"
                    "<li>Build com BuildKit + cache mount: "
                    "<code>DOCKER_BUILDKIT=1 docker build -t app .</code>.</li>"
                    "<li>Use <code>dive app:latest</code> para inspecionar camadas e "
                    "achar bytes desperdiçados.</li>"
                    "<li>Compare tamanho: full vs slim vs distroless. Quanto cada "
                    "transição economiza?</li>"
                    "<li>Rode com limites: <code>--memory=256m --cpus=0.5 "
                    "--read-only --cap-drop=ALL --security-opt=no-new-privileges</code>.</li>"
                    "<li>Configure HEALTHCHECK e veja status com <code>docker ps</code> "
                    "(coluna 'STATUS' mostra 'healthy').</li>"
                    "<li>Bonus: build multi-arch com buildx para amd64+arm64.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Complete hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>Write a multi-stage Dockerfile for a Python app: a builder "
                    "stage with the toolchain, a final stage with python:3.12-slim, "
                    "non-root USER, HEALTHCHECK, CMD in JSON form.</li>"
                    "<li>Create a .dockerignore excluding .git, .env, __pycache__, etc.</li>"
                    "<li>Build with BuildKit + cache mount: "
                    "<code>DOCKER_BUILDKIT=1 docker build -t app .</code>.</li>"
                    "<li>Use <code>dive app:latest</code> to inspect layers and "
                    "find wasted bytes.</li>"
                    "<li>Compare sizes: full vs slim vs distroless. How much does each "
                    "transition save?</li>"
                    "<li>Run with limits: <code>--memory=256m --cpus=0.5 "
                    "--read-only --cap-drop=ALL --security-opt=no-new-privileges</code>.</li>"
                    "<li>Configure HEALTHCHECK and check status with <code>docker ps</code> "
                    "(the 'STATUS' column shows 'healthy').</li>"
                    "<li>Bonus: build multi-arch with buildx for amd64+arm64.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("Docker Get Started", "https://docs.docker.com/get-started/", "docs", "", title_en="Docker Get Started", description_en=""),
                m("Best practices for Dockerfiles", "https://docs.docker.com/build/building/best-practices/", "docs", "", title_en="Best practices for Dockerfiles", description_en=""),
                m("Play with Docker", "https://labs.play-with-docker.com/", "tool", "", title_en="Play with Docker", description_en=""),
                m("Buildpacks (alternativa)", "https://buildpacks.io/docs/", "docs", "", title_en="Buildpacks (alternative)", description_en=""),
                m("dive (analisar imagem)", "https://github.com/wagoodman/dive", "tool", "", title_en="dive (analyze image)", description_en=""),
                m("12-Factor App", "https://12factor.net/", "article", "Princípios para apps em container.", title_en="12-Factor App", description_en="Principles for containerized apps."),
            ],
            "questions": [
                q("`docker run` faz:",
                  "Cria e inicia um container a partir de uma imagem.",
                  ["Compila a imagem a partir de um Dockerfile local, erro típico de configuração feita às pressas, sem revisão posterior.", "Sobe um serviço de registry para guardar imagens, erro comum de quem aprendeu por tentativa e erro, sem revisar a documentação oficial.", "Remove um volume e os dados persistidos nele, abordagem que resolve o sintoma, não a causa raiz do problema."],
                  "`docker run` = `docker create` + `docker start`. Para builds, é `docker build`.",
                  statement_en="`docker run` does:",
                  correct_en="Creates and starts a container from an image.",
                  wrong_en=["Compiles the image from a local Dockerfile, a typical mistake from configuration done in a rush without later review.", "Starts a registry service to store images, a common mistake for those who learned by trial and error without reading the official docs.", "Removes a volume and the data persisted in it, an approach that fixes the symptom, not the root cause of the problem."],
                  explanation_en="`docker run` = `docker create` + `docker start`. For builds, it's `docker build`."),
                q("Multi-stage build:",
                  "Permite usar imagem maior para build e menor para runtime.",
                  ["Deixa a imagem final maior, com todas as dependências de build.", "Só funciona em projeto escrito em Python.", "Substitui a etapa de build feita no pipeline de CI."],
                  "Ex.: imagem com gcc só na fase de compilação; runtime tem só o binário.",
                  statement_en="Multi-stage build:",
                  correct_en="Allows using a larger image for the build and a smaller one for runtime.",
                  wrong_en=['Makes the final image larger, carrying all build dependencies, a common shortcut that looks fine until production surprises you.', 'Only works for projects written in Python, which tends to fail quietly until someone audits the setup.', 'Replaces the build step done in the CI pipeline, an assumption that rarely survives the first real incident review.'],
                  explanation_en="E.g.: image with gcc only during the compile phase; runtime has only the binary."),
                q("Diferença entre image e container:",
                  "Imagem é o template (read-only); container é a instância em execução.",
                  ["A imagem muda de conteúdo sozinha a cada execução, atalho que ignora exatamente o cenário que mais importa evitar.", "O container é só um registro estatístico de uso, abordagem que ignora o cenário de falha mais provável na prática.", "Imagem e container são exatamente a mesma coisa, sem diferença, suposição que só vale em ambiente de desenvolvimento, não em produção."],
                  "Várias instâncias podem rodar a mesma imagem com configs diferentes (env, volumes).",
                  statement_en="Difference between image and container:",
                  correct_en="An image is the read-only template; a container is the running instance.",
                  wrong_en=["The image changes its own content on every run, a shortcut that ignores exactly the scenario it matters most to avoid.", "The container is just a usage statistics record, an approach that ignores the most likely failure scenario in practice.", "Image and container are exactly the same thing, with no difference, an assumption that only holds in development, never in production."],
                  explanation_en="Multiple instances can run the same image with different configs (env, volumes)."),
                q("Volume serve para:",
                  "Persistir dados fora do ciclo de vida do container.",
                  ["Aumentar a memória RAM disponível para o container.", "Substituir o serviço de DNS usado pela aplicação.", "Melhorar o tempo de build da imagem Docker."],
                  "Container pode ser destruído/recriado sem perder dados se eles estão em volume.",
                  statement_en="A volume is used to:",
                  correct_en="Persist data outside the container's lifecycle.",
                  wrong_en=["Increase the RAM memory available to the container.", "Replace the DNS service used by the application.", "Improve the Docker image's build time."],
                  explanation_en="A container can be destroyed/recreated without losing data if it lives in a volume."),
                q("`COPY` vs `ADD`:",
                  "Prefira COPY; ADD tem comportamento extra (download/extract) que pode surpreender.",
                  ["COPY está depreciado e não deve mais ser usado no Dockerfile, atalho que troca segurança por conveniência de curto prazo.", "COPY e ADD fazem exatamente a mesma coisa, sem diferença alguma, suposição que vale só até o primeiro imprevisto de rede ou hardware.", "ADD costuma ser considerado a opção superior mesmo em casos simples, suposição que só vale em ambiente de desenvolvimento, não em produção."],
                  "ADD baixa URL e extrai tar automaticamente, recursos perigosos sem necessidade na maioria dos casos.",
                  statement_en="`COPY` vs `ADD`:",
                  correct_en="Prefer COPY; ADD has extra behavior (download/extract) that can be surprising.",
                  wrong_en=["COPY is deprecated and should no longer be used in the Dockerfile, a shortcut that trades security for short-term convenience.", "COPY and ADD do exactly the same thing, with no difference at all, an assumption that holds only until the first network or hardware surprise.", "ADD is usually considered the superior option even in simple cases, an assumption that only holds in development, never in production."],
                  explanation_en="ADD downloads a URL and auto-extracts tar archives, dangerous features that are unnecessary in most cases."),
                q("Layer caching no Docker:",
                  "Reaproveita camadas inalteradas, ordem dos comandos importa.",
                  ["Essa funcionalidade de cache simplesmente não existe no Docker.", "Só funciona quando a build roda em ambiente de produção.", "Substitui a necessidade de usar um registry para as imagens."],
                  "Mudou uma camada? Todas após são invalidadas. Por isso copy de código vai por último.",
                  statement_en="Docker layer caching:",
                  correct_en="Reuses unchanged layers; instruction order matters.",
                  wrong_en=["This caching feature simply doesn't exist in Docker.", "Only works when the build runs in a production environment.", "Replaces the need to use a registry for the images."],
                  explanation_en="Changed one layer? Everything after it is invalidated. That's why copying code goes last."),
                q(".dockerignore evita:",
                  "Enviar arquivos desnecessários para o build context.",
                  ["Apagar arquivos do disco local automaticamente.", "Reduzir o uso de CPU durante o processo de build.", "Substituir por completo o arquivo .gitignore do repositório."],
                  "Sem ele, `docker build` envia o repo todo (.git, node_modules) ao daemon, lento e perigoso.",
                  statement_en=".dockerignore prevents:",
                  correct_en="Sending unnecessary files into the build context.",
                  wrong_en=["Automatically deleting files from local disk.", "Reducing CPU usage during the build process.", "Completely replacing the repository's .gitignore file."],
                  explanation_en="Without it, `docker build` sends the whole repo (.git, node_modules) to the daemon, slow and risky."),
                q("Por que NÃO usar latest em produção?",
                  "Falta rastreabilidade, pode mudar.",
                  ["Fazer pull da tag latest costuma ser mais lento que outras tags.", "A tag latest simplesmente não funciona em algum ambiente.", "A tag latest exige uma licença paga do Docker Hub."],
                  "Em rollback você não consegue voltar 'para qual latest era ontem'. Use SHA ou semver.",
                  statement_en="Why NOT use latest in production?",
                  correct_en="It lacks traceability and can change content.",
                  wrong_en=["Pulling the latest tag tends to be slower than other tags.", "The latest tag simply doesn't work in some environments.", "The latest tag requires a paid Docker Hub license."],
                  explanation_en="On rollback you can't go back to 'whichever latest was yesterday'. Use a SHA or semver."),
                q("Para aplicações stateless:",
                  "Containers facilitam escala horizontal.",
                  ["Containers atrapalham mais do que ajudam nesse caso.", "Uma VM tradicional costuma ser melhor nesse cenário.", "Não existe vantagem real em usar container aqui."],
                  "Sem estado em disco local, basta subir mais réplicas. Estado vai para DB/cache externos.",
                  statement_en="For stateless applications:",
                  correct_en="Containers make horizontal scaling easier.",
                  wrong_en=["Containers get in the way more than they help in this case.", "A traditional VM tends to be better in this scenario.", "There's no real advantage to using a container here."],
                  explanation_en="With no state on local disk, you just spin up more replicas. State lives in an external DB/cache."),
                q("Imagem de 1 GB para Python:",
                  "Provavelmente pode ser otimizada com multi-stage e base slim/alpine.",
                  ["Esse tamanho já é considerado ideal para imagem Python, decisão que parece segura até o primeiro teste de penetração real.", "Esse tamanho é necessário na grande maioria dos casos, decisão que parece razoável isolada, mas quebra a arquitetura no conjunto.", "Esse tamanho já é o menor tecnicamente possível para Python, suposição que ignora como o recurso realmente se comporta em escala."],
                  "Imagem Python 3.12 normal é ~1GB; slim é ~150MB; distroless ~50MB.",
                  statement_en="A 1 GB image for Python:",
                  correct_en="Can probably be optimized with multi-stage builds and a slim/alpine base.",
                  wrong_en=["This size is already considered ideal for a Python image, a decision that looks safe until the first real penetration test.", "This size is necessary in the vast majority of cases, a decision that looks reasonable in isolation but breaks the architecture as a whole.", "This size is already the smallest technically possible for Python, an assumption that ignores how the resource actually behaves at scale."],
                  explanation_en="A normal Python 3.12 image is ~1GB; slim is ~150MB; distroless is ~50MB."),
            ],
        },
        # =====================================================================
        # 4.2 Segurança de Imagens
        # =====================================================================
        {
            "title": "Segurança de Imagens",
            "title_en": "Image Security",
            "summary": "Não usar imagens de fontes desconhecidas e reduzir o tamanho.",
            "summary_en": "Avoid images from unknown sources and reduce their size.",
            "lesson": {
                "intro": (
                    "Cada linha de Dockerfile pode virar um buraco. Cada MB extra de "
                    "imagem é mais código não-necessário com potencial CVE. Em "
                    "incidentes recentes (Log4Shell, xz backdoor de 2024), times com "
                    "imagens enxutas e SBOM responderam em horas; quem tinha 'imagem "
                    "ubuntu:latest com tudo' levou semanas só para descobrir o que "
                    "estava rodando. Esta aula cobre minimalismo, pin por digest, "
                    "USER não-root, scanning, assinatura, e os anti-patterns mais "
                    "comuns que viram CVE."
                ),
                "intro_en": (
                    "Every line in a Dockerfile can become a hole. Every extra MB in an "
                    "image is more unnecessary code with potential CVEs. In recent "
                    "incidents (Log4Shell, the 2024 xz backdoor), teams with lean images "
                    "and an SBOM responded in hours; whoever had a 'ubuntu:latest with "
                    "everything' image took weeks just to find out what was even running. "
                    "This lesson covers minimalism, digest pinning, non-root USER, "
                    "scanning, signing, and the most common anti-patterns that turn into "
                    "CVEs."
                ),
                "body": (
                """<h3>1. Minimalismo radical: cada byte extra é superfície de ataque potencial</h3>
<p>Toda biblioteca incluída numa imagem é um bug em potencial; todo
binário extra é um exploit em potencial. Reduzir o que está presente na
imagem NÃO é otimização de espaço em disco — é uma medida de segurança
direta. Uma imagem Ubuntu padrão carrega dezenas de megabytes de
pacotes, incluindo daemons inativos, um shell completo e utilitários
como <code>apt</code>, <code>find</code> e <code>vim</code> — nenhum
deles necessário para a APLICAÇÃO rodar, mas todos disponíveis para um
atacante que consiga executar código dentro do container. Uma imagem
distroless carrega só o runtime e as bibliotecas essenciais, sem shell,
sem gerenciador de pacotes algum. O espectro de bases disponíveis varia
enormemente:</p>
<div class="mermaid">
flowchart LR
    Full["Imagem base completa"] --> Strip["Remove shell e package manager"]
    Strip --> NonRoot["Roda como usuário não-root"]
    NonRoot --> Min["Imagem distroless / minimalista"]
</div>

<table>
<tr><th>Base</th><th>Tamanho típico</th><th>Trade-off</th></tr>
<tr><td>ubuntu:22.04</td><td>~80MB</td><td>Familiar; muito que vc não usa.</td></tr>
<tr><td>debian:12</td><td>~120MB</td><td>Pacotes maduros.</td></tr>
<tr><td>debian:12-slim</td><td>~75MB</td><td>Sem doc, sem locales extras.</td></tr>
<tr><td>python:3.12-slim</td><td>~150MB</td><td>Slim + Python.</td></tr>
<tr><td>alpine:3.19</td><td>~7MB</td><td>musl libc; pode quebrar wheels Python.</td></tr>
<tr><td>wolfi-base (Chainguard)</td><td>~10MB</td><td>glibc, SBOM nativo, patches diários.</td></tr>
<tr><td>distroless/static</td><td>~2MB</td><td>Só libs. Sem shell. Bom para Go/Rust.</td></tr>
<tr><td>distroless/python</td><td>~50MB</td><td>Python runtime. Sem pip, sem shell.</td></tr>
<tr><td>scratch</td><td>0MB</td><td>Vazia. Você adiciona binário estático.</td></tr>
</table>
<p>As imagens distroless do Google representam um bom ponto de
equilíbrio: contêm APENAS a aplicação e as dependências de runtime que
ela precisa — sem <code>sh</code>, sem <code>apt</code>, sem
<code>cat</code>. Um atacante que consiga executar código arbitrário
dentro da aplicação não tem sequer um shell disponível para rodar o
próximo comando:</p>
<pre><code>FROM golang:1.22 AS builder
RUN CGO_ENABLED=0 go build -o /app ./cmd/app

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app /app
ENTRYPOINT ["/app"]</code></pre>
<p>O trade-off inevitável é conforto de debug: sem shell, um
<code>docker exec -it ... sh</code> simplesmente não funciona — a
variante <code>:debug</code> da imagem distroless existe justamente para
esse cenário em desenvolvimento, mantendo <code>:nonroot</code> em
produção. Wolfi (mantida pela Chainguard) resolve uma limitação real do
Alpine: por usar glibc em vez de musl, é compatível com uma gama muito
maior de pacotes pré-compilados (muitos wheels Python, por exemplo,
assumem glibc e simplesmente falham em Alpine). Imagens Chainguard
adicionam SBOM gerado automaticamente, builds reprodutíveis, e patches
de segurança aplicados diariamente — na prática, você raramente vê uma
CVE "velha e conhecida" persistindo na base por semanas.</p>

<h3>2. Pin por digest: a única forma de garantir que a imagem de hoje é a de amanhã</h3>
<p>Uma tag como <code>python:3.12-slim</code> é apenas um APELIDO
mutável — o mantenedor da imagem pode republicá-la apontando para um
conteúdo diferente a qualquer momento, sem aviso. Fixar pelo DIGEST
(o hash sha256 do conteúdo exato) garante reprodutibilidade absoluta:</p>
<pre><code>FROM python:3.12-slim@sha256:f0a1b2c3d4e5f6...
# Não:
# FROM python:3.12-slim
# FROM python:latest</code></pre>
<p>O custo óbvio dessa prática é que um digest fixo NUNCA recebe patch
de segurança automaticamente — uma ferramenta como Renovate resolve isso
monitorando a tag original e abrindo PR automaticamente quando um novo
digest com patch de segurança é publicado, mantendo o controle explícito
sobre CADA atualização (revisável, testável) em vez de puxar mudança
silenciosa a cada build:</p>
<pre><code># renovate.json
{
  "docker": {
    "pinDigests": true,
    "enabled": true
  }
}</code></pre>

<h3>3. Usuário não-root e capabilities reduzidas: o mínimo aceitável, não um extra</h3>
<p>Uma imagem Docker roda como root por padrão — se um atacante
explorar a aplicação, ele herda esse root DENTRO do namespace do
container, e em configurações sem mapeamento de user namespace, esse
root equivale a root no HOST:</p>
<pre><code>FROM python:3.12-slim
RUN groupadd -g 1000 app && useradd -u 1000 -g 1000 -m app
WORKDIR /app
COPY --chown=app:app . .
USER 1000:1000   # numérico funciona em K8s securityContext
CMD ["python", "main.py"]</code></pre>
<p>Usar o UID NUMÉRICO (em vez do nome) garante compatibilidade direta
com o <code>securityContext</code> do Kubernetes, que referencia UID
numérico. Em runtime, reduzir capabilities do Linux ao mínimo
estritamente necessário fecha ainda mais a superfície:</p>
<pre><code># Docker
docker run \\
  --read-only \\
  --tmpfs /tmp \\
  --cap-drop=ALL \\
  --cap-add=NET_BIND_SERVICE \\
  --security-opt=no-new-privileges \\
  --user 1000:1000 \\
  myapp

# Kubernetes securityContext
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile: { type: RuntimeDefault }
  containers:
    - name: app
      securityContext:
        readOnlyRootFilesystem: true
        allowPrivilegeEscalation: false
        capabilities:
          drop: ["ALL"]
          add: ["NET_BIND_SERVICE"]</code></pre>
<p>Se a aplicação nunca precisa escutar numa porta abaixo de 1024, nem
mesmo <code>NET_BIND_SERVICE</code> deveria ser adicionado de volta —
use uma porta acima de 8000 e mantenha o descarte total de capabilities
sem exceção nenhuma.</p>

<h3>4. Scanning: cruzar o que está na imagem contra o que já é vulnerabilidade conhecida</h3>
<p>Toda imagem carrega pacotes do sistema operacional (glibc, openssl) e
bibliotecas da aplicação (Django, lodash) — cada um com histórico
próprio de CVEs conhecidas. Um scanner cruza o SBOM da imagem (aula
anterior) contra bases como NVD e OSV, sinalizando cada correspondência.
Trivy é gratuito, rápido e cobre múltiplos tipos de alvo (imagem,
sistema de arquivos, repositório Git) numa única ferramenta; Grype
trabalha em par com Syft; Snyk é comercial (com camada gratuita) e se
diferencia sugerindo a CORREÇÃO específica, não só apontando o problema;
Docker Scout vem integrado ao Docker Desktop; e ECR Enhanced Scanning ou
Harbor fazem a varredura diretamente dentro do próprio registry, sem
depender de uma etapa separada de CI:</p>
<pre><code># CI: falha se CVE crítico
$ trivy image --severity CRITICAL --exit-code 1 myapp:dev

# Re-scan periódico no registry detecta CVEs novos
$ trivy image --severity HIGH,CRITICAL myapp:v1.4.2

# Ignorar específicos com motivo
$ cat .trivyignore
CVE-2024-12345  # não exploitable em nosso uso, ver ADR-42

# Gerar SBOM
$ trivy image --format cyclonedx --output sbom.json myapp:dev</code></pre>
<p>Uma política de bloqueio típica escalona a resposta pela severidade:
CRITICAL bloqueia o build sempre; HIGH com correção já disponível também
bloqueia (não há motivo para esperar); HIGH sem correção disponível
ainda vira ticket com prazo de acompanhamento, mas não trava o pipeline
imediatamente; e MEDIUM/LOW entram no backlog geral, sem urgência de
bloqueio.</p>

<h3>5. Assinatura de imagem: provar que ninguém trocou o conteúdo depois do build</h3>
<p>Sem assinatura, um atacante que comprometa o REGISTRY (não a
aplicação, o registry em si) pode trocar silenciosamente a imagem por
uma versão maliciosa mantendo o mesmo nome e tag — ninguém puxando essa
imagem teria como perceber a substituição. Cosign assina a imagem (com
chave própria, ou "keyless" via OIDC — provando identidade através do
próprio workflow de CI, sem gerenciar chave nenhuma manualmente), e o
Rekor do projeto Sigstore registra essa assinatura num transparency log
público e auditável:</p>
<div class="mermaid">
flowchart LR
    Build["Build da imagem"] --> Sign["cosign sign"]
    Sign --> Reg["Registry"]
    Reg --> Verify["cosign verify no deploy"]
    Verify --> Run["Só sobe se a assinatura for válida"]
</div>

<pre><code># Sign no CI (OIDC keyless, sem chave armazenada)
$ cosign sign --yes ghcr.io/empresa/app@$DIGEST

# Verify
$ cosign verify ghcr.io/empresa/app:v1.4.2 \\
    --certificate-identity ci@empresa.com \\
    --certificate-oidc-issuer https://token.actions.githubusercontent.com</code></pre>
<p>Em Kubernetes, um admission controller (Kyverno, Connaisseur, ou o
Sigstore Policy Controller) pode REJEITAR qualquer imagem não assinada
antes mesmo de criar o pod:</p>
<pre><code>apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: signed-images-only }
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-signature
      match:
        any: [{ resources: { kinds: [Pod] } }]
      verifyImages:
        - imageReferences: ['ghcr.io/empresa/*']
          attestors:
            - keyless: { subject: ci@empresa.com }</code></pre>

<h3>6. SBOM e proveniência: saber em segundos o que cada imagem contém</h3>
<p>O SBOM (detalhado na aula anterior) é a lista de ingredientes da
imagem — anexá-lo diretamente ao registry como um "referrer" garante que
ele viaja junto com a imagem, não fica separado num arquivo qualquer:</p>
<pre><code>$ syft myapp:dev -o cyclonedx-json &gt; sbom.json
$ cosign attach sbom --sbom sbom.json myapp:dev
$ cosign attest --predicate sbom.json --type cyclonedx myapp:dev</code></pre>
<p>Quando a próxima Log4Shell inevitavelmente aparecer, consultar o
SBOM de cada imagem responde em segundos "temos esse pacote vulnerável
em produção?" — sem essa infraestrutura pronta, a mesma pergunta exige
investigação manual, potencialmente por dias. A proveniência SLSA vai um
passo além do SBOM: em vez de só listar O QUE está na imagem, atesta
COMO ela foi construída — qual pipeline, qual commit exato, sob quais
condições. GitHub Actions com o framework SLSA consegue gerar atestado
de nível 3 (indicando um builder confiável e isolado):</p>
<pre><code>jobs:
  build:
    uses: slsa-framework/slsa-github-generator/.github/workflows/builder_container_slsa3.yml@v1.10.0
    with:
      image: ghcr.io/empresa/app
      digest: ${{ needs.build.outputs.digest }}</code></pre>

<h3>7. Um Dockerfile seguro, do início ao fim</h3>
<pre><code># 1. Base mínima e pinada por digest
FROM python:3.12-slim@sha256:abc123...

# 2. Não cachear apt; clean lists
RUN apt-get update && apt-get install -y --no-install-recommends \\
      libpq5 && \\
    rm -rf /var/lib/apt/lists/*

# 3. Diretórios e usuário
RUN groupadd -g 1000 app && useradd -u 1000 -g 1000 -m app
WORKDIR /app

# 4. Deps primeiro (camada cacheada)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Código com ownership correto
COPY --chown=app:app . .

# 6. Switch USER antes do CMD
USER 1000:1000

# 7. Healthcheck
HEALTHCHECK --interval=30s CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"

# 8. CMD em JSON form
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]</code></pre>
<p>Cada numeração aqui corresponde a uma decisão específica das seções
anteriores — este checklist é literalmente a síntese prática da aula
inteira aplicada num único arquivo.</p>

<h3>8. Caso real: o backdoor do xz-utils, e por que quem tinha SBOM viu primeiro</h3>
<p>Em março de 2024, foi descoberto um backdoor deliberadamente inserido
no xz-utils 5.6.0/5.6.1 — resultado de um esquema de engenharia social
contra o mantenedor do projeto, sustentado por MAIS DE DOIS ANOS até a
inserção final acontecer. Distribuições "rolling" (Debian testing,
Fedora rawhide, Alpine edge) já tinham o pacote comprometido em
produção assim que ele foi publicado. Quem detectou o problema primeiro
nas próprias organizações? Times que já tinham SBOM gerado
automaticamente e monitoramento contínuo de pacote em uso — uma consulta
simples respondeu "temos essa versão específica?" em minutos. Quem foi
pego completamente às cegas? Quem usava algo como
<code>FROM ubuntu:latest</code> sem nenhum SBOM, sem saber ao certo o
que estava rodando até investigar manualmente. As lições diretas: pin
específico evita puxar uma versão comprometida sem perceber, SBOM
transforma "qual imagem tem isso?" numa consulta de segundos em vez de
uma investigação de dias, re-scan periódico no registry pega uma CVE
publicada DEPOIS que a imagem já tinha sido enviada, e distribuições
mais "lentas" e conservadoras (Debian stable) raramente tinham as
versões vulneráveis instaladas — um trade-off real entre adotar pacote
recente rapidamente e a exposição a esse tipo de ataque de supply
chain.</p>

<h3>9. Dez anti-padrões que, somados, explicam a maioria das CVEs evitáveis</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Base mínima e pin por digest.</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Scan + SBOM em todo push.</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Assinar e exigir verify no deploy.</p></div>
  </div>
  <figcaption>Checklist curto contra a maioria das CVEs evitáveis.</figcaption>
</figure>

<ul>
<li><strong><code>FROM ubuntu:18.04</code></strong> (fim de suporte):
sem patch de segurança novo chegando.</li>
<li><strong><code>RUN curl ... | bash</code></strong>: executa
conteúdo remoto sem nenhuma verificação, um risco direto de supply
chain.</li>
<li><strong><code>USER root</code></strong> só "porque é mais fácil"
durante o desenvolvimento, e nunca revertido antes de produção.</li>
<li><strong>Senha em `ENV` no Dockerfile</strong>: permanece gravada
permanentemente na imagem.</li>
<li><strong>Imagem com 200 CVEs</strong> de pacotes que a aplicação
nem usa, só presentes porque a base nunca foi enxugada.</li>
<li><strong><code>chmod 777</code></strong> em diretórios "para
resolver permissão rápido".</li>
<li><strong>Bind mount de `/var/run/docker.sock`</strong> dentro do
container: dá controle total sobre o daemon do host.</li>
<li><strong><code>--privileged</code></strong> sem necessidade real
comprovada — quase sempre existe uma capability específica que resolve
sem conceder privilégio total.</li>
<li><strong>Imagem não assinada</strong> em produção: nenhuma garantia
de proveniência.</li>
<li><strong>Sem política de retenção</strong>: o registry acumula
imagens antigas e vulneráveis indefinidamente, aumentando a superfície
de ataque de tudo que ainda está tecnicamente disponível para deploy.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. Radical minimalism: every extra byte is potential attack surface</h3>
<p>Every library included in an image is a potential bug; every extra
binary is a potential exploit. Reducing what's present in the image is
NOT disk-space optimization — it's a direct security measure. A standard
Ubuntu image carries dozens of megabytes of packages, including inactive
daemons, a full shell, and utilities like <code>apt</code>,
<code>find</code> and <code>vim</code> — none of them necessary for the
APPLICATION to run, but all available to an attacker who manages to
execute code inside the container. A distroless image carries only the
runtime and the essential libraries, with no shell, no package manager at
all. The available base spectrum varies enormously:</p>
<div class="mermaid">
flowchart LR
    Full["Full base image"] --> Strip["Remove shell and package manager"]
    Strip --> NonRoot["Run as non-root user"]
    NonRoot --> Min["Distroless / minimal image"]
</div>

<table>
<tr><th>Base</th><th>Tamanho típico</th><th>Trade-off</th></tr>
<tr><td>ubuntu:22.04</td><td>~80MB</td><td>Familiar; muito que vc não usa.</td></tr>
<tr><td>debian:12</td><td>~120MB</td><td>Pacotes maduros.</td></tr>
<tr><td>debian:12-slim</td><td>~75MB</td><td>Sem doc, sem locales extras.</td></tr>
<tr><td>python:3.12-slim</td><td>~150MB</td><td>Slim + Python.</td></tr>
<tr><td>alpine:3.19</td><td>~7MB</td><td>musl libc; pode quebrar wheels Python.</td></tr>
<tr><td>wolfi-base (Chainguard)</td><td>~10MB</td><td>glibc, SBOM nativo, patches diários.</td></tr>
<tr><td>distroless/static</td><td>~2MB</td><td>Só libs. Sem shell. Bom para Go/Rust.</td></tr>
<tr><td>distroless/python</td><td>~50MB</td><td>Python runtime. Sem pip, sem shell.</td></tr>
<tr><td>scratch</td><td>0MB</td><td>Vazia. Você adiciona binário estático.</td></tr>
</table>
<p>Google's distroless images represent a good balance: they contain ONLY
the application and the runtime dependencies it actually needs — no
<code>sh</code>, no <code>apt</code>, no <code>cat</code>. An attacker
who manages to execute arbitrary code inside the application doesn't even
have a shell available to run the next command:</p>
<pre><code>FROM golang:1.22 AS builder
RUN CGO_ENABLED=0 go build -o /app ./cmd/app

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app /app
ENTRYPOINT ["/app"]</code></pre>
<p>The unavoidable trade-off is debugging comfort: with no shell, a
<code>docker exec -it ... sh</code> simply doesn't work — the
<code>:debug</code> variant of the distroless image exists exactly for
that development scenario, keeping <code>:nonroot</code> in production.
Wolfi (maintained by Chainguard) solves a real Alpine limitation: by using
glibc instead of musl, it's compatible with a much wider range of
precompiled packages (many Python wheels, for example, assume glibc and
simply fail on Alpine). Chainguard images add automatically generated
SBOMs, reproducible builds, and daily security patches — in practice, you
rarely see an "old, well-known" CVE lingering in the base for weeks.</p>

<h3>2. Pinning by digest: the only way to guarantee today's image is tomorrow's image</h3>
<p>A tag like <code>python:3.12-slim</code> is just a mutable ALIAS — the
image maintainer can republish it pointing to different content at any
time, without notice. Pinning by DIGEST (the sha256 hash of the exact
content) guarantees absolute reproducibility:</p>
<pre><code>FROM python:3.12-slim@sha256:f0a1b2c3d4e5f6...
# Não:
# FROM python:3.12-slim
# FROM python:latest</code></pre>
<p>The obvious cost of this practice is that a fixed digest NEVER
receives a security patch automatically — a tool like Renovate solves
this by monitoring the original tag and automatically opening a PR when a
new digest with a security patch is published, keeping explicit control
over EACH update (reviewable, testable) instead of silently pulling a
change on every build:</p>
<pre><code># renovate.json
{
  "docker": {
    "pinDigests": true,
    "enabled": true
  }
}</code></pre>

<h3>3. Non-root user and reduced capabilities: the acceptable minimum, not an extra</h3>
<p>A Docker image runs as root by default — if an attacker exploits the
application, they inherit that root INSIDE the container's namespace,
and in configurations without user namespace mapping, that root is
equivalent to root on the HOST:</p>
<pre><code>FROM python:3.12-slim
RUN groupadd -g 1000 app && useradd -u 1000 -g 1000 -m app
WORKDIR /app
COPY --chown=app:app . .
USER 1000:1000   # numérico funciona em K8s securityContext
CMD ["python", "main.py"]</code></pre>
<p>Using the NUMERIC UID (instead of the name) guarantees direct
compatibility with Kubernetes' <code>securityContext</code>, which
references numeric UID. At runtime, reducing Linux capabilities to the
strict minimum needed closes the surface even further:</p>
<pre><code># Docker
docker run \\
  --read-only \\
  --tmpfs /tmp \\
  --cap-drop=ALL \\
  --cap-add=NET_BIND_SERVICE \\
  --security-opt=no-new-privileges \\
  --user 1000:1000 \\
  myapp

# Kubernetes securityContext
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile: { type: RuntimeDefault }
  containers:
    - name: app
      securityContext:
        readOnlyRootFilesystem: true
        allowPrivilegeEscalation: false
        capabilities:
          drop: ["ALL"]
          add: ["NET_BIND_SERVICE"]</code></pre>
<p>If the application never needs to listen on a port below 1024, not
even <code>NET_BIND_SERVICE</code> should be added back — use a port
above 8000 and keep the full capability drop with no exceptions at
all.</p>

<h3>4. Scanning: cross-referencing what's in the image against known vulnerabilities</h3>
<p>Every image carries operating-system packages (glibc, openssl) and
application libraries (Django, lodash) — each with its own history of
known CVEs. A scanner cross-references the image's SBOM (previous lesson)
against databases like NVD and OSV, flagging every match. Trivy is free,
fast, and covers multiple target types (image, filesystem, Git
repository) in a single tool; Grype pairs with Syft; Snyk is commercial
(with a free tier) and stands out by suggesting the specific FIX, not
just pointing out the problem; Docker Scout comes built into Docker
Desktop; and ECR Enhanced Scanning or Harbor scan directly inside the
registry itself, without relying on a separate CI step:</p>
<pre><code># CI: falha se CVE crítico
$ trivy image --severity CRITICAL --exit-code 1 myapp:dev

# Re-scan periódico no registry detecta CVEs novos
$ trivy image --severity HIGH,CRITICAL myapp:v1.4.2

# Ignorar específicos com motivo
$ cat .trivyignore
CVE-2024-12345  # não exploitable em nosso uso, ver ADR-42

# Gerar SBOM
$ trivy image --format cyclonedx --output sbom.json myapp:dev</code></pre>
<p>A typical blocking policy escalates the response by severity:
CRITICAL always blocks the build; HIGH with a fix already available also
blocks (there's no reason to wait); HIGH with no fix available yet
becomes a ticket with a follow-up deadline, but doesn't halt the pipeline
immediately; and MEDIUM/LOW go into the general backlog, with no urgency
to block.</p>

<h3>5. Image signing: proving nobody swapped the content after the build</h3>
<p>Without signing, an attacker who compromises the REGISTRY itself (not
the application, the registry) can silently swap the image for a
malicious version while keeping the same name and tag — nobody pulling
that image would have any way to notice the substitution. Cosign signs
the image (with its own key, or "keyless" via OIDC — proving identity
through the CI workflow itself, with no key to manage manually), and the
Sigstore project's Rekor records that signature in a public, auditable
transparency log:</p>
<div class="mermaid">
flowchart LR
    Build["Image build"] --> Sign["cosign sign"]
    Sign --> Reg["Registry"]
    Reg --> Verify["cosign verify at deploy"]
    Verify --> Run["Runs only if signature is valid"]
</div>

<pre><code># Sign no CI (OIDC keyless, sem chave armazenada)
$ cosign sign --yes ghcr.io/empresa/app@$DIGEST

# Verify
$ cosign verify ghcr.io/empresa/app:v1.4.2 \\
    --certificate-identity ci@empresa.com \\
    --certificate-oidc-issuer https://token.actions.githubusercontent.com</code></pre>
<p>In Kubernetes, an admission controller (Kyverno, Connaisseur, or the
Sigstore Policy Controller) can REJECT any unsigned image before the pod
is even created:</p>
<pre><code>apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: signed-images-only }
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-signature
      match:
        any: [{ resources: { kinds: [Pod] } }]
      verifyImages:
        - imageReferences: ['ghcr.io/empresa/*']
          attestors:
            - keyless: { subject: ci@empresa.com }</code></pre>

<h3>6. SBOM and provenance: knowing in seconds what each image contains</h3>
<p>The SBOM (detailed in the previous lesson) is the image's list of
ingredients — attaching it directly to the registry as a "referrer"
guarantees that it travels along with the image, instead of living
separately in some random file:</p>
<pre><code>$ syft myapp:dev -o cyclonedx-json &gt; sbom.json
$ cosign attach sbom --sbom sbom.json myapp:dev
$ cosign attest --predicate sbom.json --type cyclonedx myapp:dev</code></pre>
<p>When the next Log4Shell inevitably shows up, checking each image's
SBOM answers "do we have that vulnerable package in production?" in
seconds — without that infrastructure already in place, the same
question requires manual investigation, potentially taking days. SLSA
provenance goes a step further than the SBOM: instead of just listing
WHAT is in the image, it attests HOW it was built — which pipeline,
which exact commit, under which conditions. GitHub Actions with the SLSA
framework can generate a level-3 attestation (indicating a trusted,
isolated builder):</p>
<pre><code>jobs:
  build:
    uses: slsa-framework/slsa-github-generator/.github/workflows/builder_container_slsa3.yml@v1.10.0
    with:
      image: ghcr.io/empresa/app
      digest: ${{ needs.build.outputs.digest }}</code></pre>

<h3>7. A secure Dockerfile, start to finish</h3>
<pre><code># 1. Base mínima e pinada por digest
FROM python:3.12-slim@sha256:abc123...

# 2. Não cachear apt; clean lists
RUN apt-get update && apt-get install -y --no-install-recommends \\
      libpq5 && \\
    rm -rf /var/lib/apt/lists/*

# 3. Diretórios e usuário
RUN groupadd -g 1000 app && useradd -u 1000 -g 1000 -m app
WORKDIR /app

# 4. Deps primeiro (camada cacheada)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Código com ownership correto
COPY --chown=app:app . .

# 6. Switch USER antes do CMD
USER 1000:1000

# 7. Healthcheck
HEALTHCHECK --interval=30s CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"

# 8. CMD em JSON form
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]</code></pre>
<p>Each numbered step here corresponds to a specific decision from the
sections above — this checklist is literally the practical synthesis of
the whole lesson applied to a single file.</p>

<h3>8. A real case: the xz-utils backdoor, and why whoever had an SBOM saw it first</h3>
<p>In March 2024, a deliberately inserted backdoor was discovered in
xz-utils 5.6.0/5.6.1 — the result of a social-engineering scheme against
the project's maintainer, sustained for OVER TWO YEARS until the final
insertion happened. "Rolling" distributions (Debian testing, Fedora
rawhide, Alpine edge) already had the compromised package in production
as soon as it was published. Who detected the problem first within their
own organizations? Teams that already had an automatically generated SBOM
and continuous monitoring of packages in use — a simple query answered
"do we have this specific version?" within minutes. Who got caught
completely blindsided? Whoever was running something like
<code>FROM ubuntu:latest</code> with no SBOM at all, with no clear idea of
what was even running until manually investigating. The direct lessons:
specific pinning avoids accidentally pulling a compromised version, an
SBOM turns "which image has this?" into a query taking seconds instead of
a days-long investigation, periodic re-scanning on the registry catches a
CVE published AFTER the image had already been pushed, and "slower", more
conservative distributions (Debian stable) rarely had the vulnerable
versions installed — a real trade-off between adopting a recent package
quickly and the exposure to this kind of supply-chain attack.</p>

<h3>9. Ten anti-patterns that, combined, explain most avoidable CVEs</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Minimal base and digest pin.</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Scan + SBOM on every push.</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Sign and require verify at deploy.</p></div>
  </div>
  <figcaption>Short checklist against most avoidable CVEs.</figcaption>
</figure>

<ul>
<li><strong><code>FROM ubuntu:18.04</code></strong> (end of support): no
new security patches arriving.</li>
<li><strong><code>RUN curl ... | bash</code></strong>: executes remote
content with no verification at all, a direct supply-chain risk.</li>
<li><strong><code>USER root</code></strong> only "because it's easier"
during development, and never reverted before production.</li>
<li><strong>Password in `ENV` in the Dockerfile</strong>: stays
permanently baked into the image.</li>
<li><strong>Image with 200 CVEs</strong> from packages the application
doesn't even use, present only because the base was never trimmed
down.</li>
<li><strong><code>chmod 777</code></strong> on directories "to quickly
fix permissions".</li>
<li><strong>Bind mount of `/var/run/docker.sock`</strong> inside the
container: gives full control over the host's daemon.</li>
<li><strong><code>--privileged</code></strong> with no proven real need
— there's almost always a specific capability that solves it without
granting total privilege.</li>
<li><strong>Unsigned image</strong> in production: no provenance
guarantee whatsoever.</li>
<li><strong>No retention policy</strong>: the registry accumulates old,
vulnerable images indefinitely, increasing the attack surface of
everything still technically available for deployment.</li>
</ul>"""
                ),
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Pegue uma imagem sua. Substitua base por distroless ou wolfi. "
                    "Compare tamanho com <code>docker images</code>.</li>"
                    "<li>Pin por digest sha256.</li>"
                    "<li>Adicione USER não-root, capabilities reduzidas, "
                    "<code>--read-only --cap-drop=ALL</code>.</li>"
                    "<li>Scan com <code>trivy image</code> antes/depois, quantos "
                    "CVEs sumiram?</li>"
                    "<li>Configure GitHub Actions com Trivy + assinatura Cosign + "
                    "atestado SLSA L3.</li>"
                    "<li>Em K8s (kind), instale Kyverno e crie policy que exige "
                    "imagens assinadas.</li>"
                    "<li>Tente subir Pod com imagem não-assinada → veja rejeição.</li>"
                    "<li>Bonus: configure Renovate para autoatualizar digests com "
                    "patches de segurança.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    '<p><strong>Complete hands-on exercise</strong>:</p><ol><li>Take one of your images. Replace the base with distroless or wolfi. Compare size with <code>docker images</code>.</li><li>Pin by sha256 digest.</li><li>Add a non-root USER, reduced capabilities, <code>--read-only --cap-drop=ALL</code>.</li><li>Scan with <code>trivy image</code> before/after — how many CVEs disappeared?</li><li>Configure GitHub Actions with Trivy + Cosign signing + SLSA L3 attestation.</li><li>On K8s (kind), install Kyverno and create a policy that requires signed images.</li><li>Try to start a Pod with an unsigned image → see the rejection.</li><li>Bonus: configure Renovate to auto-update digests with security patches.</li></ol>'
                ),
            },
            "materials": [
                m("Distroless", "https://github.com/GoogleContainerTools/distroless", "tool", "", title_en='Distroless', description_en=''),
                m("Trivy", "https://aquasecurity.github.io/trivy/", "tool", "", title_en='Trivy', description_en=''),
                m("Snyk: Container security", "https://snyk.io/learn/container-security/", "article", "", title_en='Snyk: Container security', description_en=''),
                m("Wolfi", "https://wolfi.dev/", "tool", "Distro otimizada para containers.", title_en='Wolfi', description_en='Distro optimized for containers.'),
                m("CIS Docker Benchmark", "https://www.cisecurity.org/benchmark/docker", "docs", "", title_en='CIS Docker Benchmark', description_en=''),
                m("Chainguard images", "https://images.chainguard.dev/", "tool", "Imagens minimal com SBOM/Sigstore.", title_en='Chainguard images', description_en='Minimal images with SBOM/Sigstore.'),
            ],
            "questions": [
                q("Distroless serve para:",
                  "Imagens minimalistas, sem shell e package manager.",
                  ["Funciona só para imagens escritas em Python, decisão que parece segura até o primeiro teste de penetração real.", "Ter maior performance de rede entre containers, prática que gera falso senso de segurança no time.", "Aumentar o volume de logs gerados pela imagem, suposição que raramente se sustenta fora do ambiente controlado de laboratório."],
                  "Sem shell, atacante não tem como sair do container facilmente. Debug fica menos confortável, trade-off.",
                  statement_en='Distroless is for:',
                  correct_en='Minimalist images, with no shell or package manager.',
                  wrong_en=['It only works for images written in Python, a decision that looks safe until the first real penetration test.', 'Getting higher network performance between containers, a practice that creates a false sense of security on the team.', 'Increasing the volume of logs the image generates, an assumption that rarely holds outside a controlled lab environment.'],
                  explanation_en="With no shell, an attacker has a harder time escaping the container. Debugging is less comfortable — that's the trade-off."),
                q("Pin por digest sha256 garante:",
                  "Reprodutibilidade, mesma imagem sempre.",
                  ["Renovação automática do certificado usado na imagem.", "Uma conexão TLS mais forte entre cliente e registry.", "Maior velocidade de download da imagem no pull."],
                  "Tag pode ser sobrescrita; digest é hash do conteúdo, único.",
                  statement_en='Pinning by sha256 digest guarantees:',
                  correct_en='Reproducibility — the same image every time.',
                  wrong_en=['Automatic renewal of the certificate used by the image.', 'A stronger TLS connection between client and registry.', 'Faster image download speed on pull.'],
                  explanation_en='A tag can be overwritten; the digest is a unique hash of the content.'),
                q("Imagem alpine é:",
                  "Pequena, mas com musl libc, pode quebrar pacotes glibc.",
                  ["Não inclui alguma implementação de libc na imagem, decisão que parece segura até o primeiro teste de penetração real.", "Costuma ser mais lenta que outras distros base, atalho que ignora exatamente o cenário que mais importa evitar.", "Tecnicamente idêntica à imagem base do Debian, prática que gera falso senso de segurança no time."],
                  "Alguns wheels Python só vêm em manylinux (glibc). Mede antes de migrar.",
                  statement_en='An Alpine image is:',
                  correct_en='Small, but with musl libc it can break glibc packages.',
                  wrong_en=["It doesn't include any libc implementation in the image, a decision that looks safe until the first real penetration test.", 'Usually slower than other base distros, a shortcut that ignores exactly the scenario that matters most to avoid.', 'Technically identical to the Debian base image, a practice that creates a false sense of security on the team.'],
                  explanation_en='Some Python wheels only ship as manylinux (glibc). Measure before migrating.'),
                q("Escanear imagem em CI:",
                  "Para pegar CVEs antes do push em registry.",
                  ["Substitui completamente a etapa de SAST no pipeline.", "Só faz sentido rodar isso já em produção.", "Não tem efeito prático algum na segurança final."],
                  "Falha rápida no PR é melhor que descobrir CVE em produção.",
                  statement_en='Scanning an image in CI:',
                  correct_en='To catch CVEs before pushing to the registry.',
                  wrong_en=['Completely replaces the SAST step in the pipeline.', 'Only makes sense to run once already in production.', 'Has no practical effect on final security at all.'],
                  explanation_en='Failing fast on the PR is better than discovering a CVE in production.'),
                q("Rodar como root no container:",
                  "Risco, escalada privilege se sair do container.",
                  ["Reduz o uso de CPU consumido pelo processo principal.", "Uma boa prática recomendada pela maioria dos guias.", "Necessário na grande maioria dos cenários de produção."],
                  "Container scape + root no host = comprometimento total. UserNS adiciona camada extra.",
                  statement_en='Running as root in the container:',
                  correct_en='A risk — privilege escalation if you escape the container.',
                  wrong_en=['Reduces the CPU usage consumed by the main process, a common shortcut that looks fine until production surprises you.', 'A good practice recommended by most guides, which tends to fail quietly until someone audits the setup.', 'Required in the vast majority of production scenarios, an assumption that rarely survives the first real incident review.'],
                  explanation_en='Container escape + root on the host = full compromise. UserNS adds an extra layer.'),
                q("Capabilities padrão do Docker:",
                  "Devem ser reduzidas ao mínimo (drop ALL e add o que precisa).",
                  ["Devem ser ampliadas para cobrir qualquer cenário futuro, comportamento que só some quando alguém finalmente lê a documentação.", "São imutáveis e não podem ser alteradas pelo operador, escolha que economiza tempo agora e cobra o preço mais tarde.", "Não importam de verdade para a segurança do container, decisão que parece segura até o primeiro teste de penetração real."],
                  "Padrão dá ~14 capabilities. App web normal precisa de zero (com porta >1024).",
                  statement_en="Docker's default capabilities:",
                  correct_en='Should be reduced to the minimum (drop ALL and add what you need).',
                  wrong_en=['Should be expanded to cover any future scenario, a behavior that only goes away when someone finally reads the docs.', 'Are immutable and cannot be changed by the operator, a choice that saves time now and exacts the price later.', "Don't really matter for container security, a decision that looks safe until the first real penetration test."],
                  explanation_en='The default grants ~14 capabilities. A normal web app needs zero (with port >1024).'),
                q("Imagem de 4GB com vulnerabilidades:",
                  "Crie versão menor e escaneie regularmente.",
                  ["Esse tamanho já é considerado ideal para produção.", "Não existe solução real para esse tipo de problema.", "Continue usando essa mesma imagem sem mudar muito pouco."],
                  "Cada MB que sobra é potencial CVE em pacote que a app nem usa.",
                  statement_en='A 4GB image with vulnerabilities:',
                  correct_en='Create a smaller version and scan regularly.',
                  wrong_en=['That size is already considered ideal for production.', 'There is no real solution for this kind of problem.', 'Keep using that same image without changing much at all.'],
                  explanation_en="Every leftover MB is a potential CVE in a package the app doesn't even use."),
                q("Wolfi é:",
                  "Distro 'undistro' otimizada para SBOM e segurança.",
                  ["Um runtime de container alternativo ao containerd.", "Um substituto direto e completo do Docker Engine.", "Uma ferramenta de linter para Dockerfile."],
                  "Mantida pela Chainguard. Pacotes assinados, glibc-based, com SBOM nativo.",
                  statement_en='Wolfi is:',
                  correct_en="An 'undistro' distro optimized for SBOM and security.",
                  wrong_en=['An alternative container runtime to containerd, a common shortcut that looks fine until production surprises you.', 'A direct, complete replacement for Docker Engine, which tends to fail quietly until someone audits the setup.', 'A linter tool for Dockerfiles, an assumption that rarely survives the first real incident review.'],
                  explanation_en='Maintained by Chainguard. Signed packages, glibc-based, with a native SBOM.'),
                q("Imutabilidade da imagem:",
                  "Mesmo digest = mesmo conteúdo.",
                  ["O conteúdo muda a cada novo pull da imagem.", "Esse conceito de imutabilidade não existe no Docker.", "Pode mudar de conteúdo mesmo mantendo a mesma tag."],
                  "Princípio que torna deploys reproduzíveis e rollbacks confiáveis.",
                  statement_en='Image immutability:',
                  correct_en='Same digest = same content.',
                  wrong_en=['The content changes on every new pull of the image.', "This concept of immutability simply doesn't exist in Docker.", 'It can change content even while keeping the same tag.'],
                  explanation_en='The principle that makes deployments reproducible and rollbacks trustworthy.'),
                q("Fix de CVE em imagem base:",
                  "Requer rebuild da imagem do app.",
                  ["É aplicado automaticamente sem precisar de rebuild.", "Não é necessário fazer muito pouco além de esperar.", "Só é necessário quando a imagem roda em cluster K8s."],
                  "CVE foi corrigido no Debian 12.6? Você precisa rebuildar para herdar o patch.",
                  statement_en='Fixing a CVE in a base image:',
                  correct_en='Requires rebuilding the app image.',
                  wrong_en=['Is applied automatically without needing a rebuild.', "Doesn't require doing much beyond waiting.", 'Is only needed when the image runs in a K8s cluster.'],
                  explanation_en='CVE fixed in Debian 12.6? You need to rebuild to inherit the patch.'),
            ],
        },
        # =====================================================================
        # 4.3 Container Registry
        # =====================================================================
        {
            "title": "Container Registry",
            "title_en": 'Container Registry',
            "summary": "Onde hospedar suas imagens Docker de forma privada.",
            "summary_en": 'Where to host your Docker images privately.',
            "lesson": {
                "intro": (
                    "Registry é a 'biblioteca' das suas imagens. A escolha afeta "
                    "segurança (RBAC, scan, assinatura), custo (egress, storage), "
                    "performance (latência, rate-limit) e governança (auditoria, "
                    "compliance). Docker Hub público é tentador para projetos "
                    "open source, mas frequentemente errado para empresas. Esta aula "
                    "cobre opções, autenticação moderna (OIDC vs PAT), tags e "
                    "imutabilidade, retenção, pull-through cache, scan contínuo e "
                    "GitOps com webhooks."
                ),
                "intro_en": "A registry is the 'library' for your images. The choice affects security (RBAC, scan, signing), cost (egress, storage), performance (latency, rate limits) and governance (audit, compliance). Public Docker Hub is tempting for open-source projects, but often wrong for companies. This lesson covers options, modern authentication (OIDC vs PAT), tags and immutability, retention, pull-through cache, continuous scanning, and GitOps with webhooks.",
                "body": (
                """<h3>1. As opções principais, e o que cada uma resolve melhor</h3>
<table>
<tr><th>Registry</th><th>Modelo</th><th>Notas</th></tr>
<tr><td>Docker Hub</td><td>SaaS público</td><td>Free com limites; bom para imagens base públicas. Em prod privado, pago.</td></tr>
<tr><td>AWS ECR</td><td>SaaS/IAM</td><td>Nativo AWS; integra com IAM, scan, lifecycle.</td></tr>
<tr><td>Google Artifact Registry (GAR)</td><td>SaaS/IAM</td><td>Multi-formato (Docker, Maven, npm, PyPI...).</td></tr>
<tr><td>Azure ACR</td><td>SaaS/IAM</td><td>Nativo Azure; tasks built-in para build.</td></tr>
<tr><td>GHCR</td><td>SaaS</td><td>Integrado a GitHub Actions (token automático). Free para públicos.</td></tr>
<tr><td>GitLab Registry</td><td>SaaS/Self</td><td>Integrado a GitLab CI.</td></tr>
<tr><td>Harbor</td><td>Self-hosted</td><td>OSS, RBAC, scan, replicação. Padrão K8s on-prem.</td></tr>
<tr><td>JFrog Artifactory</td><td>Self/SaaS</td><td>Multi-formato; veterano, caro.</td></tr>
<tr><td>Sonatype Nexus</td><td>Self/SaaS</td><td>OSS edition; multi-formato.</td></tr>
<tr><td>Quay (Red Hat)</td><td>SaaS/Self</td><td>Comercial; Project Quay open source.</td></tr>
</table>
<p>A escolha raramente é neutra: registries nativos de nuvem (ECR, GAR,
ACR) ganham em integração direta com IAM e scan já embutido, mas
amarram você àquele provedor; GHCR e GitLab Registry ganham em
simplicidade quando o código já vive naquela plataforma, com
autenticação de CI praticamente automática; Harbor é a escolha
dominante para quem opera Kubernetes on-premise e precisa de RBAC,
scan e replicação sem depender de nuvem nenhuma; e Artifactory/Nexus se
justificam quando a organização já precisa de um registro multi-formato
cobrindo não só imagem de container, mas também artefato Maven, pacote
npm, entre outros, numa única plataforma.</p>
<div class="mermaid">
flowchart TB
    Need["Escolha de registry"] --> Hub["Docker Hub: público e simples"]
    Need --> Cloud["ECR / ACR / GCR: cloud nativo"]
    Need --> GHCR["GHCR: próximo ao código no GitHub"]
    Need --> Harbor["Harbor: on-prem, scan e políticas"]
</div>


<h3>2. Autenticação moderna: por que um token estático é sempre o elo mais fraco</h3>
<p>Um Personal Access Token (PAT) ou conta de robô com credencial fixa
vaza mais cedo ou mais tarde — commitado por engano, exposto num log,
copiado para um lugar errado. A alternativa preferível sempre que
disponível é OIDC: o CI PROVA sua identidade através de um token de
curta duração emitido pelo próprio provedor de CI, sem NENHUM segredo
persistente armazenado em lugar nenhum:</p>
<pre><code># GitHub Actions → AWS ECR via OIDC (sem chave armazenada)
permissions:
  id-token: write
  contents: read
jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111:role/gh-pusher
          aws-region: us-east-1
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker build -t $ECR/myapp:$SHA .
          docker push $ECR/myapp:$SHA</code></pre>
<p>Dentro de um cluster Kubernetes, o equivalente é Workload Identity —
um pod assume uma role IAM diretamente através da sua ServiceAccount,
sem nenhuma chave montada como Secret; os helpers de autenticação de
ECR/GAR/ACR resolvem essa troca automaticamente. Quando o registry é
privado e o cluster precisa PUXAR (não só publicar) imagens, o
mecanismo padrão é um Secret do tipo
<code>kubernetes.io/dockerconfigjson</code>:</p>
<pre><code>kubectl create secret docker-registry regcred \\
  --docker-server=ghcr.io \\
  --docker-username=ci-bot \\
  --docker-password=$TOKEN

# Pod
spec:
  imagePullSecrets:
    - name: regcred
  containers:
    - name: app
      image: ghcr.io/empresa/myapp:v1.4.2</code></pre>
<p>Em escala, gerenciar esse Secret manualmente (e rotacioná-lo antes de
expirar) se torna trabalho operacional real — um External Secrets
Operator resolve isso automaticamente, sincronizando e rotacionando sem
intervenção manual.</p>

<h3>3. Tags e imutabilidade: por que "a mesma tag" não significa "o mesmo conteúdo"</h3>
<p>Uma imagem publicada com várias tags simultâneas serve propósitos
diferentes — nem toda tag tem a mesma garantia de estabilidade:</p>
<pre><code># Bom, múltiplas tags úteis para mesma imagem
ghcr.io/empresa/app:abc1234              # commit SHA (imutável de fato)
ghcr.io/empresa/app:v1.4.2               # semver (não sobrescreva!)
ghcr.io/empresa/app:v1.4                 # rolling, ok em dev
ghcr.io/empresa/app:dev                  # tip de branch dev
ghcr.io/empresa/app@sha256:f0a1b2...     # digest absoluto, gold standard</code></pre>
<p>Em produção, use o SHA do commit ou o digest absoluto — tags como
<code>latest</code> ou <code>dev</code> NUNCA deveriam aparecer num
manifesto de produção, porque seu conteúdo pode mudar sem que o
manifesto em si tenha sido tocado. Habilitar imutabilidade de tag
diretamente no registry fecha essa brecha de vez: uma vez publicada,
aquela tag específica não pode ser sobrescrita por um push posterior —
prevenindo exatamente o cenário "alguém republicou v1.4.2 com um fix" e
um cluster que já estava rodando a v1.4.2 ANTIGA continuar achando que
está na versão corrigida:</p>
<pre><code># ECR
aws ecr put-image-tag-mutability \\
  --repository-name myapp \\
  --image-tag-mutability IMMUTABLE

# Harbor: project settings → Tag Immutability Rules
# ACR: az acr config repository --name myapp --immutability enabled</code></pre>

<h3>4. Retenção: cada build de PR é uma imagem, e imagens acumulam rápido</h3>
<p>Sem política de retenção explícita, o volume de armazenamento cresce
de gigabytes para terabytes silenciosamente — cada build de Pull Request
gera uma imagem nova, e sem limpeza automática essas imagens (muitas
delas nunca mais usadas) permanecem indefinidamente, inflando custo e
mantendo versões antigas e potencialmente vulneráveis tecnicamente
disponíveis para deploy:</p>
<pre><code># ECR lifecycle
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Manter últimas 30 imagens semver",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["v"],
        "countType": "imageCountMoreThan",
        "countNumber": 30
      },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 2,
      "description": "Apagar untagged após 7d",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 7
      },
      "action": { "type": "expire" }
    }
  ]
}</code></pre>

<h3>5. Pull-through cache: contornar o rate limit do Docker Hub antes que ele pare seu CI</h3>
<p>O Docker Hub limita pulls anônimos a 100 a cada 6 horas por IP, e 200
para contas autenticadas gratuitas — um limite que um CI corporativo com
múltiplos jobs simultâneos consumindo a mesma base de imagem estoura
rapidamente, resultando em builds falhando por "too many requests", não
por bug nenhum de código. A solução é configurar um registry interno
como PULL-THROUGH CACHE: Harbor pode operar um projeto como proxy do
Docker Hub, Quay ou GHCR; ECR tem pull-through nativo configurável para
os mesmos destinos; e o Artifactory resolve com repositórios remotos que
cacheiam automaticamente. Os benefícios vão além de só evitar o rate
limit: builds ficam mais rápidos (cache local, sem round-trip externo a
cada pull), o pipeline sobrevive a uma instabilidade momentânea do
upstream, toda imagem externa passa a ter trilha de auditoria pelo seu
próprio registry, e abre a possibilidade de escanear ou colocar em
quarentena uma imagem externa ANTES dela chegar a qualquer pipeline
interno.</p>
<div class="mermaid">
flowchart LR
    CI["Jobs de CI"] --> Cache["Pull-through cache"]
    Cache --> Hub["Docker Hub / upstream"]
    Cache --> Local["Serve cópia local"]
    CI --> Local
</div>


<h3>6. Scan contínuo: uma checagem no push não é o fim da história</h3>
<p>Escanear no momento do push só captura vulnerabilidades JÁ conhecidas
naquele instante — uma CVE publicada dias ou semanas depois, afetando
uma imagem que já estava tranquilamente em produção, nunca dispara
alerta se não houver re-scan periódico. Harbor permite agendar scan
diário; ECR Enhanced Scanning (via Inspector) opera continuamente sem
configuração manual de agenda; e o Trivy Operator, rodando dentro de um
cluster Kubernetes, escaneia especificamente as imagens EM USO
(não todo o registry, só o que está de fato rodando) e registra os
achados como CRDs consultáveis. Um webhook disparando notificação no
Slack quando uma imagem já em produção se torna vulnerável por uma CVE
recém-descoberta fecha o ciclo entre detecção e ação humana.</p>

<h3>7. RBAC: quem publica, quem só consulta, e por que humano nunca deveria fazer push direto</h3>
<p>A prática recomendada segrega estritamente por função: apenas o CI
tem permissão de ESCRITA no registry — nenhum desenvolvedor faz push
manual diretamente, porque isso elimina a trilha de auditoria que o
pipeline automaticamente gera. Leitura é escopada por time ou produto,
não um acesso amplo genérico para todo mundo. Ambientes multi-tenant se
beneficiam de namespaces ou projetos separados por time. Em produção,
o pull usa um secret ESPECÍFICO para essa finalidade, nunca uma
credencial pessoal de um humano. E como na seção 2, OIDC é preferível a
token estático sempre que a plataforma suportar. Logs de auditoria do
próprio registry — quem puxou o quê e quando — são um dos primeiros
lugares a consultar durante um incidente envolvendo possível
comprometimento de imagem.</p>

<h3>8. Webhooks e GitOps: do push da imagem à atualização automática do manifesto</h3>
<p>Um registry pode disparar um webhook a cada push — o gatilho que
conecta "nova imagem publicada" a "manifesto do cluster atualizado
automaticamente", sem intervenção manual. Argo CD Image Updater detecta
uma nova versão e atualiza o manifesto correspondente diretamente no
Git (mantendo o fluxo GitOps intacto, visto na aula de Introdução ao
Kubernetes); Flux Image Automation resolve o mesmo problema dentro do
ecossistema Flux; e Keel é uma alternativa mais simples e focada
especificamente nesse caso de uso:</p>
<pre><code># Argo CD Image Updater annotations no manifest
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: app=ghcr.io/empresa/app
    argocd-image-updater.argoproj.io/app.update-strategy: semver
    argocd-image-updater.argoproj.io/app.allow-tags: regexp:^v[0-9]+\\.[0-9]+\\.[0-9]+$</code></pre>
<p>A anotação <code>allow-tags</code> com uma expressão regular restrita
a versionamento semântico é o que impede o Image Updater de puxar
acidentalmente uma tag <code>dev</code> ou <code>latest</code> — só
versões que seguem o padrão esperado disparam a atualização automática.</p>

<h3>9. Multi-arquitetura: uma tag, várias plataformas de CPU por trás</h3>
<pre><code>$ docker buildx create --use
$ docker buildx build \\
    --platform linux/amd64,linux/arm64 \\
    --tag ghcr.io/empresa/app:v1.4.2 \\
    --push .</code></pre>
<p>O resultado desse build não é uma única imagem — é uma "manifest
list", um índice que aponta para uma imagem por arquitetura. Quando um
node ARM (Graviton na AWS, um Apple Silicon local, um Raspberry Pi)
puxa <code>app:v1.4.2</code>, o registry resolve automaticamente para o
manifest arm64 correspondente; um node amd64 recebe a variante amd64 —
a MESMA tag, resolvida de forma transparente conforme a arquitetura de
quem pede. Essa capacidade deixou de ser nicho: com Graviton
consolidado na AWS e Apple Silicon dominando o desenvolvimento local,
build multi-arch é hoje expectativa padrão, não recurso avançado
opcional.</p>

<h3>10. Oito anti-padrões que comprometem segurança, custo ou confiabilidade do registry</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Arriscado</strong><p>Tags mutáveis, push humano, sem retenção, sem scan contínuo.</p></div>
    <div class="lesson-viz-card"><strong>Saudável</strong><p>Digest imutável, CI-only push, retenção e scan contínuo.</p></div>
  </div>
  <figcaption>Higiene de registry: o que costuma quebrar segurança e custo.</figcaption>
</figure>

<ul>
<li><strong>Tags mutáveis em produção</strong>: <code>latest</code>,
<code>main</code>, <code>dev</code> nunca deveriam aparecer num
manifesto real.</li>
<li><strong>Build direto em produção</strong>: "reconstrua lá" nunca é
o mesmo artefato que passou por teste — é um artefato NOVO, não
validado.</li>
<li><strong>PAT eterno no CI</strong>: se vazar, um atacante consegue
puxar (ou publicar) qualquer coisa indefinidamente — use OIDC.</li>
<li><strong>Sem scan configurado</strong>: imagem vulnerável circula em
produção sem nenhum alarme disparando.</li>
<li><strong>Sem política de retenção</strong>: terabytes acumulando e
custo crescendo sem correspondência de valor real (seção 4).</li>
<li><strong>Imagens sem assinatura</strong>: cadeia de supply chain
fraca, sem prova de proveniência.</li>
<li><strong>Push direto por humano</strong>: sem auditoria, sem trilha
— tudo deveria passar pelo CI (seção 7).</li>
<li><strong>Produção e desenvolvimento no mesmo namespace do
registry</strong>: um comprometimento em qualquer um dos dois afeta o
raio de impacto do outro, sem segmentação nenhuma entre eles.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. The main options, and what each one solves best</h3>
<table>
<tr><th>Registry</th><th>Modelo</th><th>Notas</th></tr>
<tr><td>Docker Hub</td><td>SaaS público</td><td>Free com limites; bom para imagens base públicas. Em prod privado, pago.</td></tr>
<tr><td>AWS ECR</td><td>SaaS/IAM</td><td>Nativo AWS; integra com IAM, scan, lifecycle.</td></tr>
<tr><td>Google Artifact Registry (GAR)</td><td>SaaS/IAM</td><td>Multi-formato (Docker, Maven, npm, PyPI...).</td></tr>
<tr><td>Azure ACR</td><td>SaaS/IAM</td><td>Nativo Azure; tasks built-in para build.</td></tr>
<tr><td>GHCR</td><td>SaaS</td><td>Integrado a GitHub Actions (token automático). Free para públicos.</td></tr>
<tr><td>GitLab Registry</td><td>SaaS/Self</td><td>Integrado a GitLab CI.</td></tr>
<tr><td>Harbor</td><td>Self-hosted</td><td>OSS, RBAC, scan, replicação. Padrão K8s on-prem.</td></tr>
<tr><td>JFrog Artifactory</td><td>Self/SaaS</td><td>Multi-formato; veterano, caro.</td></tr>
<tr><td>Sonatype Nexus</td><td>Self/SaaS</td><td>OSS edition; multi-formato.</td></tr>
<tr><td>Quay (Red Hat)</td><td>SaaS/Self</td><td>Comercial; Project Quay open source.</td></tr>
</table>
<p>The choice is rarely neutral: cloud-native registries (ECR, GAR,
ACR) win on direct IAM integration and built-in scanning, but they
tie you to that provider; GHCR and GitLab Registry win on
simplicity when the code already lives on that platform, with
almost automatic CI authentication; Harbor is the dominant choice
for anyone running on-premise Kubernetes who needs RBAC,
scanning, and replication without depending on any cloud; and
Artifactory/Nexus make sense when the organization already needs a
multi-format registry covering not only container images but also
Maven artifacts, npm packages, and more, on a single platform.</p>
<div class="mermaid">
flowchart TB
    Need["Registry choice"] --> Hub["Docker Hub: public and simple"]
    Need --> Cloud["ECR / ACR / GCR: cloud-native"]
    Need --> GHCR["GHCR: close to GitHub code"]
    Need --> Harbor["Harbor: on-prem, scan and policies"]
</div>


<h3>2. Modern authentication: why a static token is always the weakest link</h3>
<p>A Personal Access Token (PAT) or a robot account with a fixed
credential leaks sooner or later — committed by mistake, exposed in
a log, copied to the wrong place. The preferable alternative whenever
available is OIDC: the CI PROVES its identity through a short-lived
token issued by the CI provider itself, with NO persistent secret
stored anywhere:</p>
<pre><code># GitHub Actions → AWS ECR via OIDC (sem chave armazenada)
permissions:
  id-token: write
  contents: read
jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111:role/gh-pusher
          aws-region: us-east-1
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker build -t $ECR/myapp:$SHA .
          docker push $ECR/myapp:$SHA</code></pre>
<p>Inside a Kubernetes cluster, the equivalent is Workload Identity —
a pod assumes an IAM role directly through its ServiceAccount,
with no key mounted as a Secret; the ECR/GAR/ACR authentication
helpers resolve that exchange automatically. When the registry is
private and the cluster needs to PULL (not just publish) images, the
standard mechanism is a Secret of type
<code>kubernetes.io/dockerconfigjson</code>:</p>
<pre><code>kubectl create secret docker-registry regcred \\
  --docker-server=ghcr.io \\
  --docker-username=ci-bot \\
  --docker-password=$TOKEN

# Pod
spec:
  imagePullSecrets:
    - name: regcred
  containers:
    - name: app
      image: ghcr.io/empresa/myapp:v1.4.2</code></pre>
<p>At scale, managing that Secret manually (and rotating it before it
expires) becomes real operational work — an External Secrets
Operator solves this automatically, syncing and rotating without
manual intervention.</p>

<h3>3. Tags and immutability: why "the same tag" does not mean "the same content"</h3>
<p>An image published with several tags at once serves different
purposes — not every tag has the same stability guarantee:</p>
<pre><code># Bom, múltiplas tags úteis para mesma imagem
ghcr.io/empresa/app:abc1234              # commit SHA (imutável de fato)
ghcr.io/empresa/app:v1.4.2               # semver (não sobrescreva!)
ghcr.io/empresa/app:v1.4                 # rolling, ok em dev
ghcr.io/empresa/app:dev                  # tip de branch dev
ghcr.io/empresa/app@sha256:f0a1b2...     # digest absoluto, gold standard</code></pre>
<p>In production, use the commit SHA or the absolute digest — tags like
<code>latest</code> or <code>dev</code> should NEVER appear in a
production manifest, because their content can change without the
manifest itself being touched. Enabling tag immutability
directly on the registry closes that gap for good: once published,
that specific tag cannot be overwritten by a later push —
preventing exactly the scenario where "someone republished v1.4.2
with a fix" and a cluster still running the OLD v1.4.2 keeps
thinking it's on the corrected version:</p>
<pre><code># ECR
aws ecr put-image-tag-mutability \\
  --repository-name myapp \\
  --image-tag-mutability IMMUTABLE

# Harbor: project settings → Tag Immutability Rules
# ACR: az acr config repository --name myapp --immutability enabled</code></pre>

<h3>4. Retention: every PR build is an image, and images pile up fast</h3>
<p>Without an explicit retention policy, storage volume grows from
gigabytes to terabytes silently — every Pull Request build
produces a new image, and without automatic cleanup those images
(many of them never used again) stay forever, inflating cost and
keeping old, potentially vulnerable versions technically
available for deploy:</p>
<pre><code># ECR lifecycle
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Manter últimas 30 imagens semver",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["v"],
        "countType": "imageCountMoreThan",
        "countNumber": 30
      },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 2,
      "description": "Apagar untagged após 7d",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 7
      },
      "action": { "type": "expire" }
    }
  ]
}</code></pre>

<h3>5. Pull-through cache: bypass Docker Hub rate limits before they stop your CI</h3>
<p>Docker Hub limits anonymous pulls to 100 every 6 hours per IP, and
200 for free authenticated accounts — a limit that a corporate CI
with multiple concurrent jobs consuming the same base image blows
through quickly, resulting in builds failing with "too many
requests", not because of any code bug. The solution is to configure
an internal registry as a PULL-THROUGH CACHE: Harbor can run a
project as a proxy for Docker Hub, Quay, or GHCR; ECR has native
pull-through configurable for the same destinations; and
Artifactory solves it with remote repositories that cache
automatically. The benefits go beyond just avoiding the rate
limit: builds get faster (local cache, no external round-trip on
every pull), the pipeline survives a momentary upstream outage,
every external image gets an audit trail through your own
registry, and you can scan or quarantine an external image BEFORE
it reaches any internal pipeline.</p>
<div class="mermaid">
flowchart LR
    CI["CI jobs"] --> Cache["Pull-through cache"]
    Cache --> Hub["Docker Hub / upstream"]
    Cache --> Local["Serve local copy"]
    CI --> Local
</div>


<h3>6. Continuous scanning: a check at push time is not the end of the story</h3>
<p>Scanning at push time only catches vulnerabilities ALREADY known
at that instant — a CVE published days or weeks later, affecting
an image that was already sitting quietly in production, never
fires an alert if there is no periodic re-scan. Harbor can schedule
daily scans; ECR Enhanced Scanning (via Inspector) runs continuously
without a manual schedule; and the Trivy Operator, running inside a
Kubernetes cluster, specifically scans images IN USE
(not the whole registry, only what is actually running) and records
findings as queryable CRDs. A webhook firing a Slack notification
when an image already in production becomes vulnerable due to a
newly discovered CVE closes the loop between detection and human
action.</p>

<h3>7. RBAC: who publishes, who only reads, and why humans should never push directly</h3>
<p>The recommended practice segregates strictly by role: only CI
has WRITE permission on the registry — no developer pushes
manually directly, because that eliminates the audit trail the
pipeline automatically generates. Read access is scoped by team or
product, not a generic broad access for everyone. Multi-tenant
environments benefit from separate namespaces or projects per
team. In production, pulls use a Secret SPECIFIC to that purpose,
never a human's personal credential. And as in section 2, OIDC is
preferable to a static token whenever the platform supports it.
The registry's own audit logs — who pulled what and when — are
among the first places to check during an incident involving a
possible image compromise.</p>

<h3>8. Webhooks and GitOps: from image push to automatic manifest update</h3>
<p>A registry can fire a webhook on every push — the trigger that
connects "new image published" to "cluster manifest updated
automatically", with no manual intervention. Argo CD Image Updater
detects a new version and updates the corresponding manifest
directly in Git (keeping the GitOps flow intact, as seen in the
Introduction to Kubernetes lesson); Flux Image Automation solves
the same problem inside the Flux ecosystem; and Keel is a simpler
alternative focused specifically on this use case:</p>
<pre><code># Argo CD Image Updater annotations no manifest
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: app=ghcr.io/empresa/app
    argocd-image-updater.argoproj.io/app.update-strategy: semver
    argocd-image-updater.argoproj.io/app.allow-tags: regexp:^v[0-9]+\\.[0-9]+\\.[0-9]+$</code></pre>
<p>The <code>allow-tags</code> annotation with a regular expression
restricted to semantic versioning is what stops the Image Updater
from accidentally pulling a <code>dev</code> or <code>latest</code>
tag — only versions that follow the expected pattern trigger the
automatic update.</p>

<h3>9. Multi-architecture: one tag, several CPU platforms behind it</h3>
<pre><code>$ docker buildx create --use
$ docker buildx build \\
    --platform linux/amd64,linux/arm64 \\
    --tag ghcr.io/empresa/app:v1.4.2 \\
    --push .</code></pre>
<p>The result of that build is not a single image — it is a "manifest
list", an index that points to one image per architecture. When an
ARM node (Graviton on AWS, local Apple Silicon, a Raspberry Pi)
pulls <code>app:v1.4.2</code>, the registry automatically resolves
to the corresponding arm64 manifest; an amd64 node gets the amd64
variant — the SAME tag, resolved transparently according to the
architecture of whoever asks. That capability is no longer niche:
with Graviton consolidated on AWS and Apple Silicon dominating
local development, multi-arch builds are now a standard expectation,
not an optional advanced feature.</p>

<h3>10. Eight anti-patterns that compromise registry security, cost, or reliability</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Risky</strong><p>Mutable tags, human push, no retention, no continuous scan.</p></div>
    <div class="lesson-viz-card"><strong>Healthy</strong><p>Immutable digest, CI-only push, retention and continuous scan.</p></div>
  </div>
  <figcaption>Registry hygiene: what usually breaks security and cost.</figcaption>
</figure>

<ul>
<li><strong>Mutable tags in production</strong>: <code>latest</code>,
<code>main</code>, <code>dev</code> should never appear in a
real manifest.</li>
<li><strong>Building directly in production</strong>: "rebuild it there"
is never the same artifact that passed testing — it is a NEW,
unvalidated artifact.</li>
<li><strong>Eternal PAT in CI</strong>: if it leaks, an attacker can
pull (or publish) anything indefinitely — use OIDC.</li>
<li><strong>No scan configured</strong>: a vulnerable image circulates in
production with no alarm firing.</li>
<li><strong>No retention policy</strong>: terabytes accumulating and
cost growing with no matching real value (section 4).</li>
<li><strong>Unsigned images</strong>: a weak supply-chain,
with no proof of provenance.</li>
<li><strong>Direct human push</strong>: no audit, no trail
— everything should go through CI (section 7).</li>
<li><strong>Production and development in the same registry
namespace</strong>: a compromise in either one expands the
blast radius of the other, with no segmentation between them.</li>
</ul>"""
                ),
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>No GHCR: configure tag immutability, retenção (manter 30 "
                    "semver, apagar untagged após 7d), autenticação OIDC do GitHub "
                    "Actions (sem PAT estático).</li>"
                    "<li>Faça push de imagem com tag SHA + tag semver.</li>"
                    "<li>Adicione assinatura Cosign (keyless OIDC).</li>"
                    "<li>Anexe SBOM como referrer.</li>"
                    "<li>Em K8s local (kind), instale Argo CD Image Updater. "
                    "Configure para atualizar manifest automaticamente em nova "
                    "versão semver.</li>"
                    "<li>Configure pull-through cache (em ECR) para Docker Hub.</li>"
                    "<li>Em registry privado, instale Trivy operator e veja "
                    "achados CRDs em K8s.</li>"
                    "<li>Bonus: build multi-arch (amd64+arm64) e teste em ambos.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    '<p><strong>Complete hands-on exercise</strong>:</p><ol><li>On GHCR: configure tag immutability, retention (keep 30 semver, delete untagged after 7d), GitHub Actions OIDC auth (no static PAT).</li><li>Push an image with a SHA tag + a semver tag.</li><li>Add Cosign signing (keyless OIDC).</li><li>Attach an SBOM as a referrer.</li><li>On local K8s (kind), install Argo CD Image Updater. Configure it to update the manifest automatically on a new semver version.</li><li>Configure a pull-through cache (on ECR) for Docker Hub.</li><li>On a private registry, install the Trivy operator and see findings as CRDs in K8s.</li><li>Bonus: multi-arch build (amd64+arm64) and test on both.</li></ol>'
                ),
            },
            "materials": [
                m("Harbor", "https://goharbor.io/docs/", "tool", "", title_en='Harbor', description_en=''),
                m("AWS ECR", "https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html", "docs", "", title_en='AWS ECR', description_en=''),
                m("GHCR", "https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry", "docs", "", title_en='GHCR', description_en=''),
                m("Distribution (open source)", "https://distribution.github.io/distribution/", "tool", "", title_en='Distribution (open source)', description_en=''),
                m("Cosign", "https://docs.sigstore.dev/cosign/overview/", "tool", "", title_en='Cosign', description_en=''),
                m("Argo CD Image Updater", "https://argocd-image-updater.readthedocs.io/", "tool", "", title_en='Argo CD Image Updater', description_en=''),
            ],
            "questions": [
                q("Docker Hub público é:",
                  "Útil para imagens base, arriscado para imagens privadas.",
                  ["Seguro o bastante para guardar qualquer imagem privada, comportamento que gera alerta falso ou silencia alerta real, dependendo do caso.", "Gratuito para qualquer volume de uso, sem limite, suposição que ignora como o recurso realmente se comporta em escala.", "Um substituto direto e completo do GHCR da GitHub, escolha que economiza tempo agora e cobra o preço mais tarde."],
                  "Para imagem privada de empresa, use GHCR/ECR/Harbor.",
                  statement_en='Public Docker Hub is:',
                  correct_en='Useful for base images, risky for private images.',
                  wrong_en=['Safe enough to store any private image, behavior that creates false alerts or silences real ones depending on the case.', 'Free for any usage volume, with no limit, an assumption that ignores how the resource actually behaves at scale.', "A direct, complete replacement for GitHub's GHCR, a choice that saves time now and exacts the price later."],
                  explanation_en="For a company's private image, use GHCR/ECR/Harbor."),
                q("Rate limit do Docker Hub:",
                  "Pode bloquear pulls em CI sem auth.",
                  ["Só acontece quando o pull roda em produção.", "Esse tipo de limite simplesmente não existe no Docker Hub.", "Substitui a necessidade de configurar RBAC no registry."],
                  "100 pulls/6h por IP anônimo. Mirror interno resolve.",
                  statement_en='Docker Hub rate limiting:',
                  correct_en='Can block pulls in CI without auth.',
                  wrong_en=['Only happens when the pull runs in production.', "This kind of limit simply doesn't exist on Docker Hub.", 'Replaces the need to configure RBAC on the registry.'],
                  explanation_en='100 pulls/6h per anonymous IP. An internal mirror solves it.'),
                q("Registry self-hosted:",
                  "Maior controle mas requer manutenção.",
                  ["Não exige alguma manutenção contínua da equipe.", "Faz rotação automática de credenciais sem configuração.", "Costuma sair mais barato que qualquer opção gerenciada."],
                  "Você cuida de upgrade, backup, HA. Em escala pequena, SaaS sai mais barato.",
                  statement_en='A self-hosted registry:',
                  correct_en='More control, but requires maintenance.',
                  wrong_en=["Doesn't require any ongoing team maintenance.", 'Automatically rotates credentials with no configuration.', 'Usually comes out cheaper than any managed option.'],
                  explanation_en='You own upgrades, backups, HA. At small scale, SaaS often costs less.'),
                q("Promotion entre ambientes:",
                  "Promove a mesma imagem (digest) entre dev/stg/prod.",
                  ["Só funciona promovendo a tag latest entre ambientes.", "Gera um build totalmente novo em cada ambiente.", "Não depende de algum tipo de versionamento de imagem."],
                  "Garante que o que passou em staging é o mesmo bit-a-bit que foi para prod.",
                  statement_en='Promotion across environments:',
                  correct_en='Promotes the same image (digest) across dev/stg/prod.',
                  wrong_en=['Only works by promoting the latest tag across environments.', 'Generates a brand-new build in each environment.', "Doesn't depend on any kind of image versioning."],
                  explanation_en='Guarantees that what passed staging is bit-for-bit the same thing that went to prod.'),
                q("Webhook em registry:",
                  "Dispara CI/CD quando imagem nova é publicada.",
                  ["Substitui a necessidade de configurar IAM no registry.", "Reduz o custo de armazenamento cobrado pelo registry.", "Apaga automaticamente imagens antigas do registry."],
                  "Base para GitOps com Argo Image Updater ou Flux.",
                  statement_en='A registry webhook:',
                  correct_en='Triggers CI/CD when a new image is published.',
                  wrong_en=['Replaces the need to configure IAM on the registry.', 'Reduces the storage cost charged by the registry.', 'Automatically deletes old images from the registry.'],
                  explanation_en='Foundation for GitOps with Argo Image Updater or Flux.'),
                q("Cleanup policies:",
                  "Apagam imagens antigas/não usadas.",
                  ["Aumentam o custo mensal cobrado pelo registry.", "Substituem a necessidade de configurar RBAC.", "Bloqueiam qualquer pull feito a partir do CI."],
                  "Mantenha tags semver e últimas N revisões; resto vai embora automaticamente.",
                  statement_en='Cleanup policies:',
                  correct_en='Delete old/unused images.',
                  wrong_en=['Increase the monthly cost charged by the registry.', 'Replace the need to configure RBAC.', 'Block any pull made from CI.'],
                  explanation_en='Keep semver tags and the last N revisions; the rest goes away automatically.'),
                q("Mirror de imagens públicas:",
                  "Reduz dependência externa e rate-limits.",
                  ["Costuma aumentar a latência percebida pelo cliente.", "Quebra a verificação de TLS entre cliente e registry.", "Substitui a etapa de build feita no pipeline de CI."],
                  "Harbor proxy cache, ECR pull-through. Opera como CDN para suas imagens base.",
                  statement_en='Mirroring public images:',
                  correct_en='Reduces external dependency and rate limits.',
                  wrong_en=['Usually increases the latency perceived by the client.', 'Breaks TLS verification between client and registry.', 'Replaces the build step done in the CI pipeline.'],
                  explanation_en='Harbor proxy cache, ECR pull-through. Acts as a CDN for your base images.'),
                q("Para autenticar de fora:",
                  "Use docker login com PAT/OIDC.",
                  ["Reinicie o daemon containerd na máquina local.", "Conecte usando telnet direto na porta do registry.", "Substitua o servidor de DNS usado pela máquina."],
                  "Em CI moderno, OIDC > PAT. Tokens curtos > eternos.",
                  statement_en='To authenticate from outside:',
                  correct_en='Use docker login with a PAT/OIDC.',
                  wrong_en=['Restart the containerd daemon on the local machine.', 'Connect using telnet directly to the registry port.', 'Replace the DNS server used by the machine.'],
                  explanation_en='In modern CI, OIDC > PAT. Short-lived tokens > eternal ones.'),
                q("Tag por commit SHA:",
                  "Garante rastreabilidade ao código exato.",
                  ["É uma prática considerada depreciada pela comunidade.", "Funciona de forma idêntica a usar a tag latest.", "Não é considerado uma prática segura pela indústria."],
                  "Útil em incidentes: 'qual código estava rodando?' = mesma SHA do git.",
                  statement_en='Tagging by commit SHA:',
                  correct_en='Guarantees traceability back to the exact code.',
                  wrong_en=['Is considered a deprecated practice by the community.', 'Works identically to using the latest tag.', "Isn't considered a safe practice by the industry."],
                  explanation_en="Useful in incidents: 'which code was running?' = the same git SHA."),
                q("Em registries SaaS:",
                  "Confie mas verifique, leia o shared responsibility.",
                  ["Esse tipo de registry SaaS normalmente não cobra pelo uso.", "É completamente imune a qualquer outage do provedor.", "Dispensa qualquer necessidade de configurar RBAC."],
                  "Mesmo registries SaaS já tiveram outages globais. Tenha plano de continuidade.",
                  statement_en='On SaaS registries:',
                  correct_en='Trust but verify — read the shared responsibility model.',
                  wrong_en=["This kind of SaaS registry usually doesn't charge for usage.", 'Is completely immune to any provider outage.', 'Removes any need to configure RBAC.'],
                  explanation_en='Even SaaS registries have had global outages. Have a continuity plan.'),
            ],
        },
        # =====================================================================
        # 4.4 Orquestração Simples
        # =====================================================================
        {
            "title": "Orquestração Simples",
            "title_en": 'Simple Orchestration',
            "summary": "Gerir múltiplos containers sem a complexidade total do K8s.",
            "summary_en": 'Manage multiple containers without the full complexity of K8s.',
            "lesson": {
                "intro": (
                    "Kubernetes é incrivelmente poderoso, e incrivelmente complexo. "
                    "Para muitas aplicações (um app + um banco + cache), K8s é "
                    "overengineering caro. Antes de pular direto pra ele, vale dominar "
                    "Docker Compose (dev local + prod single-host simples), Docker "
                    "Swarm (multi-host nativo Docker, mais simples que K8s) e Nomad "
                    "(orquestrador HashiCorp generalista). Esta aula compara essas "
                    "opções, mostra quando cada uma faz sentido, e pinta o quadro de "
                    "quando migrar para K8s."
                ),
                "intro_en": "Kubernetes is incredibly powerful — and incredibly complex. For many applications (an app + a database + a cache), K8s is expensive overengineering. Before jumping straight to it, it's worth mastering Docker Compose (local dev + simple single-host prod), Docker Swarm (Docker-native multi-host, simpler than K8s) and Nomad (HashiCorp's generalist orchestrator). This lesson compares those options, shows when each one makes sense, and paints the picture of when to migrate to K8s.",
                "body": (
                """<h3>1. Docker Compose: um único YAML declara toda a aplicação multi-container</h3>
<p>Compose descreve serviços, redes e volumes num arquivo declarativo —
<code>docker compose up</code> sobe tudo na ordem certa,
<code>docker compose down</code> desmonta. A versão atual é um plugin do
próprio CLI do Docker (comando <code>docker compose</code>, com espaço);
o binário separado antigo (<code>docker-compose</code>, com hífen) está
oficialmente fora de suporte:</p>
<div class="mermaid">
flowchart TD
    Compose["docker-compose.yml"] --> App["Serviço: app"]
    Compose --> DB["Serviço: banco"]
    Compose --> Cache["Serviço: cache"]
    App --> DB
    App --> Cache
</div>

<pre><code># compose.yaml, full example
services:
  app:
    image: ghcr.io/acme/app:abc1234
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgres://app:${DB_PASSWORD}@db:5432/app
      REDIS_URL: redis://cache:6379/0
    secrets:
      - db_password
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s
    depends_on:
      db: { condition: service_healthy }
      cache: { condition: service_started }
    deploy:
      replicas: 2
      resources:
        limits: { cpus: '0.5', memory: 512M }
      restart_policy:
        condition: on-failure
        max_attempts: 3
    logging:
      driver: json-file
      options: { max-size: 10m, max-file: '3' }
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 10
    secrets: [db_password]
  cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck: { test: ["CMD", "redis-cli", "ping"] }

volumes:
  pgdata: {}

secrets:
  db_password:
    file: ./secrets/db_password.txt
    # Em prod com Swarm: external: true

networks:
  default:
    driver: bridge</code></pre>
<p>Este exemplo já mostra o que separa um Compose de "brinquedo" de um
de produção: <code>healthcheck</code> em cada serviço (sem ele,
<code>depends_on</code> só garante ORDEM de início, não que a dependência
está de fato PRONTA — seção 7); <code>POSTGRES_PASSWORD_FILE</code> em
vez de senha em texto puro na variável de ambiente; e
<code>deploy.resources.limits</code> evitando que um serviço consuma
recurso do host sem limite algum.</p>

<h3>2. Override files: o mesmo YAML base, ambientes diferentes por composição</h3>
<p>Em vez de duplicar o arquivo inteiro para dev e produção, Compose
permite CAMADAR arquivos — um base neutro mais um override específico do
ambiente:</p>
<pre><code># compose.yaml (base, neutro)
# compose.dev.yaml (override para dev)
services:
  app:
    build:
      target: dev
    volumes:
      - .:/app   # bind mount para hot reload
    environment:
      DEBUG: 1
    command: python manage.py runserver 0.0.0.0:8000

# compose.prod.yaml
services:
  app:
    image: ghcr.io/acme/app:${VERSION}
    deploy:
      replicas: 3
      update_config: { parallelism: 1, order: start-first }</code></pre>
<pre><code># Uso
$ docker compose -f compose.yaml -f compose.dev.yaml up
$ docker compose -f compose.yaml -f compose.prod.yaml up -d

# Profiles para serviços opcionais
services:
  mailhog:
    image: mailhog/mailhog
    profiles: [dev]   # só sobe com --profile dev
$ docker compose --profile dev up</code></pre>
<p>Ferramentas de e-mail de teste (MailHog) ou administração de banco
(PgAdmin) que só fazem sentido em desenvolvimento entram num
<code>profile</code> específico — elas nunca sobem em produção sem
alguém pedir explicitamente com a flag correspondente, evitando que um
serviço de conveniência de dev acidentalmente vá junto para o ambiente
real.</p>

<h3>3. Variáveis e segredos: `.env` funciona, mas tem limite claro</h3>
<pre><code># .env (gitignored!)
DB_PASSWORD=supersecret
VERSION=v1.4.2

# .env.example (commitado, sem valores)
DB_PASSWORD=
VERSION=</code></pre>
<p>Compose lê <code>.env</code> automaticamente do diretório do
projeto — conveniente para desenvolvimento, mas em produção a prática
recomendada é usar segredos injetados diretamente pelo runtime (Docker
secrets, Kubernetes Secrets, ou Vault), porque um arquivo <code>.env</code>
em disco fica exposto a qualquer processo com acesso àquele filesystem,
sem controle de acesso granular nenhum.</p>

<h3>4. Docker Swarm: a mesma sintaxe de Compose, agora multi-host</h3>
<p>Swarm vem EMBUTIDO no Docker (sem instalação separada) e estende a
MESMA sintaxe de Compose com a seção <code>deploy:</code> (réplicas,
estratégia de atualização, restrições de posicionamento):</p>
<pre><code>$ docker swarm init                      # nó 1 vira manager
$ docker swarm join-token worker          # comando para outros nós
$ docker stack deploy -c compose.yaml app
$ docker service ls
$ docker service scale app_web=5
$ docker service update --image ghcr.io/acme/app:v1.5.0 app_web</code></pre>
<p>As vantagens reais sobre Kubernetes: configuração em minutos, o mesmo
YAML usado em desenvolvimento local funciona em produção multi-nó sem
tradução, um "routing mesh" embutido faz qualquer nó do cluster
responder por qualquer porta de serviço (mesmo se o container não estiver
rodando ali fisicamente), segredos são criptografados nativamente via
Raft, e a rede overlay entre nós já vem criptografada por padrão. As
desvantagens que motivaram a maior parte da indústria a migrar para
Kubernetes: comunidade e desenvolvimento de features ficaram
significativamente para trás, não há CRDs nem operadores nem o
ecossistema rico que orbita Kubernetes, auto-scaling é limitado ao que
API/CLI permitem manualmente, e service discovery é mais simples e menos
rico.</p>

<h3>5. Nomad: um orquestrador que não se limita a container</h3>
<p>Nomad (HashiCorp) roda praticamente QUALQUER carga de trabalho —
container Docker ou Podman, binário nativo, VM via qemu, até JAR/WAR de
Java — com um modelo operacional mais simples que Kubernetes. Integra
naturalmente com Consul (service discovery) e Vault (segredos) para
quem já usa a pilha HashiCorp completa:</p>
<div class="mermaid">
flowchart LR
    Nomad["Nomad"] --> Docker["Containers Docker/Podman"]
    Nomad --> Bin["Binário nativo"]
    Nomad --> Vm["VM / qemu"]
    Nomad --> Java["JAR / WAR"]
</div>

<pre><code># job.nomad.hcl
job "web" {
  datacenters = ["dc1"]
  type = "service"
  group "app" {
    count = 3
    network {
      port "http" { to = 8000 }
    }
    service {
      name = "web"
      port = "http"
      check { type = "http", path = "/health", interval = "10s", timeout = "2s" }
    }
    task "server" {
      driver = "docker"
      config {
        image = "ghcr.io/acme/app:v1.4.2"
        ports = ["http"]
      }
      resources { cpu = 500, memory = 256 }
    }
  }
}</code></pre>
<pre><code>$ nomad job run job.nomad.hcl</code></pre>
<p>Nomad faz mais sentido quando a carga de trabalho é MISTA — não só
container, um time pequeno sem capacidade dedicada para operar
Kubernetes, ou uma infraestrutura HashiCorp já estabelecida onde
adicionar mais uma ferramenta do mesmo ecossistema tem custo marginal
menor que introduzir Kubernetes do zero.</p>

<h3>6. Persistência: onde volume local para de resolver, e o que fazer depois</h3>
<p>Em Compose ou Swarm single-host, volumes nomeados resolvem
adequadamente — o dado fica no disco do próprio host. Para alta
disponibilidade de verdade, três caminhos costumam funcionar melhor que
gerenciar isso manualmente: banco de dados GERENCIADO (RDS, Cloud SQL,
Aurora) resolve o caso mais comum, delegando replicação, backup e
failover ao provedor de nuvem; storage de REDE (NFS, EFS, Longhorn) é
mais lento por natureza, mas portável entre nós, útil quando o dado
precisa acompanhar um container migrando de host; e replicação nativa do
PRÓPRIO banco (streaming replication do Postgres, InnoDB Cluster do
MySQL) resolve para quem precisa de controle mais fino sobre a topologia
de réplica. O que definitivamente NÃO vale tentar é rodar stateful
complexo (Postgres em alta disponibilidade real, um cluster Kafka)
diretamente em Compose — não é a ferramenta desenhada para esse nível de
coordenação; Kubernetes tem operadores maduros especificamente para isso
(Zalando Postgres Operator, Strimzi para Kafka) que resolvem os detalhes
que o Compose simplesmente não modela.</p>

<h3>7. Healthcheck e dependência: `depends_on` sozinho só garante ordem, não prontidão</h3>
<pre><code>services:
  app:
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
        restart: true   # restart app se cache reiniciar</code></pre>
<p><code>depends_on</code> sem <code>condition</code> só garante que o
container do banco vai INICIAR antes do container da aplicação — não
que o banco já está aceitando conexões nesse momento. Um banco que leva
alguns segundos para ficar pronto para conexões, mas cuja aplicação já
tenta conectar imediatamente após o container "iniciar", produz um erro
de conexão intermitente que parece aleatório mas é perfeitamente
determinístico: uma corrida entre "container começou" e "serviço
realmente pronto". <code>condition: service_healthy</code> resolve isso
esperando o HEALTHCHECK do banco passar antes de sequer iniciar a
aplicação.</p>

<h3>8. Redes em Compose: isolamento por segmento, não só um bridge único</h3>
<p>Cada projeto Compose cria uma rede padrão onde os serviços se
resolvem por nome via DNS interno — mas para segmentação real (limitar
quais serviços conseguem alcançar quais outros), múltiplas redes
nomeadas separam responsabilidades:</p>
<pre><code>services:
  api:
    networks: [frontend, backend]
  db:
    networks: [backend]
networks:
  frontend: {}
  backend:
    internal: true   # sem acesso à internet</code></pre>
<p><code>internal: true</code> é boa prática para a rede que hospeda
banco de dados e serviços internos: mesmo que um container nessa rede
seja comprometido, ele não consegue estabelecer conexão de SAÍDA para a
internet, limitando diretamente a capacidade de exfiltrar dados ou
baixar ferramenta adicional.</p>

<h3>9. Quando migrar para Kubernetes de verdade, e quando isso seria overkill</h3>
<p>Alguns sinais concretos sugerem que chegou a hora de migrar: múltiplos
hosts precisando compartilhar carga de trabalho de forma coordenada (não
só alta disponibilidade simples); múltiplos times compartilhando a mesma
infraestrutura (multi-tenancy real); necessidade de auto-scaling baseado
em métrica (HPA, KEDA); rollout canário GERENCIADO por ferramenta (Argo
Rollouts), não script manual; a organização já opera 30 a 50 ou mais
serviços, ponto em que orquestração manual vira caos organizacional;
necessidade de operadores avançados (Postgres, Kafka, plataformas de
ML); adoção de service mesh (Istio, Linkerd); ou exigência de
compliance que demanda NetworkPolicy, RBAC granular e audit nativo — os
tópicos das últimas aulas da Fase 5. Por outro lado, sinais claros de
que Kubernetes seria complexidade desnecessária: uma aplicação com
banco e cache rodando num único host; time pequeno (menos de cinco
desenvolvedores) sem capacidade dedicada para operar uma plataforma;
tráfego baixo, sem necessidade real de escalar automaticamente; ou um
componente stateful crítico que ninguém no time quer operar diretamente
(nesse caso, um serviço gerenciado resolve melhor que qualquer
orquestrador).</p>

<h3>10. Operação do dia a dia: os comandos que resolvem manutenção comum</h3>
<pre><code># Logs
docker compose logs -f app                # live tail
docker compose logs --tail=100 app

# Restart só um serviço
docker compose restart app

# Recriar (depois de mudar config)
docker compose up -d --force-recreate app

# Scale
docker compose up -d --scale app=3

# Backup volume
docker run --rm -v pgdata:/data -v $(pwd):/backup alpine \\
  tar czf /backup/pgdata-$(date +%F).tgz -C /data .</code></pre>
<p>O comando de backup merece atenção: ele sobe um container TEMPORÁRIO
(<code>alpine</code>, descartado logo depois via <code>--rm</code>)
montando o volume de dado e o diretório de destino, e usa
<code>tar</code> para compactar o conteúdo — um padrão simples e portátil
que não depende de nenhuma ferramenta específica de backup instalada no
host.</p>

<h3>11. Seis anti-padrões que aparecem em quem tenta esticar Compose além do que ele resolve</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Compose basta</strong><p>Dev local, demo, um host, poucos serviços.</p></div>
    <div class="lesson-viz-card"><strong>Hora de orquestrar</strong><p>Multi-host, autoscaling, rolling e discovery reais.</p></div>
  </div>
  <figcaption>Quando esticar Compose vira anti-padrão operacional.</figcaption>
</figure>

<ul>
<li><strong>Compose como produção multi-host</strong>: não escala para
esse cenário — use Swarm, Nomad ou Kubernetes conforme a necessidade
real (seção 9).</li>
<li><strong>Stateful complexo em Compose</strong>: alta disponibilidade
de verdade para um banco ou fila exige ferramenta dedicada, não
orquestração manual de volumes.</li>
<li><strong>Bind mount em produção</strong>: portabilidade ruim entre
hosts diferentes, e permissões de arquivo entre host e container
frequentemente complicam de formas sutis.</li>
<li><strong>Sem healthcheck configurado</strong>: dependências entre
serviços quebram em race condition exatamente como descrito na seção 7.</li>
<li><strong>Variável sensível direto no `compose.yaml`</strong>: o
arquivo normalmente é commitado no Git — use <code>.env</code>
(no <code>.gitignore</code>) ou segredos gerenciados pelo runtime.</li>
<li><strong>Misturar configuração de produção e desenvolvimento no
mesmo arquivo</strong>: use o padrão de override files da seção 2 em vez
de condicionais dentro de um único YAML.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. Docker Compose: a single YAML declares the whole multi-container application</h3>
<p>Compose describes services, networks, and volumes in a declarative file —
<code>docker compose up</code> brings everything up in the right order,
<code>docker compose down</code> tears it down. The current version is a
plugin of Docker's own CLI (the <code>docker compose</code> command, with
a space); the old separate binary (<code>docker-compose</code>, with a
hyphen) is officially out of support:</p>
<div class="mermaid">
flowchart TD
    Compose["docker-compose.yml"] --> App["Service: app"]
    Compose --> DB["Service: database"]
    Compose --> Cache["Service: cache"]
    App --> DB
    App --> Cache
</div>

<pre><code># compose.yaml, full example
services:
  app:
    image: ghcr.io/acme/app:abc1234
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgres://app:${DB_PASSWORD}@db:5432/app
      REDIS_URL: redis://cache:6379/0
    secrets:
      - db_password
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s
    depends_on:
      db: { condition: service_healthy }
      cache: { condition: service_started }
    deploy:
      replicas: 2
      resources:
        limits: { cpus: '0.5', memory: 512M }
      restart_policy:
        condition: on-failure
        max_attempts: 3
    logging:
      driver: json-file
      options: { max-size: 10m, max-file: '3' }
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 10
    secrets: [db_password]
  cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck: { test: ["CMD", "redis-cli", "ping"] }

volumes:
  pgdata: {}

secrets:
  db_password:
    file: ./secrets/db_password.txt
    # Em prod com Swarm: external: true

networks:
  default:
    driver: bridge</code></pre>
<p>This example already shows what separates a "toy" Compose from a
production one: <code>healthcheck</code> on every service (without it,
<code>depends_on</code> only guarantees START ORDER, not that the
dependency is actually READY — section 7); <code>POSTGRES_PASSWORD_FILE</code>
instead of a plaintext password in an environment variable; and
<code>deploy.resources.limits</code> preventing a service from consuming
host resources with no limit at all.</p>

<h3>2. Override files: the same base YAML, different environments by composition</h3>
<p>Instead of duplicating the whole file for dev and production, Compose
lets you LAYER files — a neutral base plus an environment-specific
override:</p>
<pre><code># compose.yaml (base, neutro)
# compose.dev.yaml (override para dev)
services:
  app:
    build:
      target: dev
    volumes:
      - .:/app   # bind mount para hot reload
    environment:
      DEBUG: 1
    command: python manage.py runserver 0.0.0.0:8000

# compose.prod.yaml
services:
  app:
    image: ghcr.io/acme/app:${VERSION}
    deploy:
      replicas: 3
      update_config: { parallelism: 1, order: start-first }</code></pre>
<pre><code># Uso
$ docker compose -f compose.yaml -f compose.dev.yaml up
$ docker compose -f compose.yaml -f compose.prod.yaml up -d

# Profiles para serviços opcionais
services:
  mailhog:
    image: mailhog/mailhog
    profiles: [dev]   # só sobe com --profile dev
$ docker compose --profile dev up</code></pre>
<p>Test email tools (MailHog) or database admin UIs (PgAdmin) that only
make sense in development go into a specific <code>profile</code> — they
never start in production unless someone explicitly asks with the
matching flag, avoiding a convenience-only dev service accidentally
shipping to the real environment.</p>

<h3>3. Variables and secrets: `.env` works, but has a clear limit</h3>
<pre><code># .env (gitignored!)
DB_PASSWORD=supersecret
VERSION=v1.4.2

# .env.example (commitado, sem valores)
DB_PASSWORD=
VERSION=</code></pre>
<p>Compose automatically reads <code>.env</code> from the project
directory — convenient for development, but in production the recommended
practice is to use secrets injected directly by the runtime (Docker
secrets, Kubernetes Secrets, or Vault), because a <code>.env</code>
file on disk is exposed to any process with access to that filesystem,
with no granular access control at all.</p>

<h3>4. Docker Swarm: the same Compose syntax, now multi-host</h3>
<p>Swarm comes BUILT INTO Docker (no separate install) and extends the
SAME Compose syntax with the <code>deploy:</code> section (replicas,
update strategy, placement constraints):</p>
<pre><code>$ docker swarm init                      # nó 1 vira manager
$ docker swarm join-token worker          # comando para outros nós
$ docker stack deploy -c compose.yaml app
$ docker service ls
$ docker service scale app_web=5
$ docker service update --image ghcr.io/acme/app:v1.5.0 app_web</code></pre>
<p>The real advantages over Kubernetes: configuration in minutes, the same
YAML used in local development works in multi-node production without
translation, a built-in "routing mesh" makes any cluster node
respond on any service port (even if the container isn't physically
running there), secrets are encrypted natively via Raft, and the overlay
network between nodes comes encrypted by default. The disadvantages that
pushed most of the industry to migrate to Kubernetes: community and
feature development fell significantly behind, there are no CRDs or
operators or the rich ecosystem that orbits Kubernetes, auto-scaling is
limited to what the API/CLI allow manually, and service discovery is
simpler and less rich.</p>

<h3>5. Nomad: an orchestrator that is not limited to containers</h3>
<p>Nomad (HashiCorp) runs practically ANY workload — a Docker or Podman
container, a native binary, a VM via qemu, even a Java JAR/WAR — with an
operational model simpler than Kubernetes. It integrates naturally with
Consul (service discovery) and Vault (secrets) for anyone already using
the full HashiCorp stack:</p>
<div class="mermaid">
flowchart LR
    Nomad["Nomad"] --> Docker["Docker/Podman containers"]
    Nomad --> Bin["Native binary"]
    Nomad --> Vm["VM / qemu"]
    Nomad --> Java["JAR / WAR"]
</div>

<pre><code># job.nomad.hcl
job "web" {
  datacenters = ["dc1"]
  type = "service"
  group "app" {
    count = 3
    network {
      port "http" { to = 8000 }
    }
    service {
      name = "web"
      port = "http"
      check { type = "http", path = "/health", interval = "10s", timeout = "2s" }
    }
    task "server" {
      driver = "docker"
      config {
        image = "ghcr.io/acme/app:v1.4.2"
        ports = ["http"]
      }
      resources { cpu = 500, memory = 256 }
    }
  }
}</code></pre>
<pre><code>$ nomad job run job.nomad.hcl</code></pre>
<p>Nomad makes more sense when the workload is MIXED — not only
containers, a small team without dedicated capacity to operate
Kubernetes, or an already established HashiCorp infrastructure where
adding one more tool from the same ecosystem has lower marginal cost
than introducing Kubernetes from scratch.</p>

<h3>6. Persistence: where a local volume stops working, and what to do next</h3>
<p>In single-host Compose or Swarm, named volumes solve things
adequately — the data lives on the host's own disk. For real high
availability, three paths usually work better than managing this
manually: a MANAGED database (RDS, Cloud SQL, Aurora) solves the most
common case, delegating replication, backup, and failover to the cloud
provider; NETWORK storage (NFS, EFS, Longhorn) is slower by nature but
portable across nodes, useful when data must follow a container migrating
hosts; and native replication of the DATABASE ITSELF (Postgres streaming
replication, MySQL InnoDB Cluster) works for anyone who needs finer
control over replica topology. What definitely is NOT worth trying is
running complex stateful systems (real HA Postgres, a Kafka cluster)
directly in Compose — it is not the tool designed for that level of
coordination; Kubernetes has mature operators specifically for this
(Zalando Postgres Operator, Strimzi for Kafka) that handle details
Compose simply does not model.</p>

<h3>7. Healthcheck and dependency: `depends_on` alone only guarantees order, not readiness</h3>
<pre><code>services:
  app:
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
        restart: true   # restart app se cache reiniciar</code></pre>
<p><code>depends_on</code> without <code>condition</code> only guarantees
that the database container will START before the application container —
not that the database is already accepting connections at that moment. A
database that takes a few seconds to be ready for connections, while the
application already tries to connect immediately after the container
"starts", produces an intermittent connection error that looks random but
is perfectly deterministic: a race between "container started" and
"service actually ready". <code>condition: service_healthy</code> solves
this by waiting for the database HEALTHCHECK to pass before even starting
the application.</p>

<h3>8. Networks in Compose: isolation by segment, not just a single bridge</h3>
<p>Every Compose project creates a default network where services
resolve by name via internal DNS — but for real segmentation (limiting
which services can reach which others), multiple named networks
separate responsibilities:</p>
<pre><code>services:
  api:
    networks: [frontend, backend]
  db:
    networks: [backend]
networks:
  frontend: {}
  backend:
    internal: true   # sem acesso à internet</code></pre>
<p><code>internal: true</code> is good practice for the network that hosts
databases and internal services: even if a container on that network is
compromised, it cannot establish an OUTBOUND connection to the
internet, directly limiting the ability to exfiltrate data or
download additional tooling.</p>

<h3>9. When to migrate to real Kubernetes, and when that would be overkill</h3>
<p>Some concrete signals suggest it's time to migrate: multiple
hosts needing to share workload in a coordinated way (not just simple
high availability); multiple teams sharing the same infrastructure
(real multi-tenancy); need for metric-based auto-scaling (HPA, KEDA);
canary rollouts MANAGED by a tool (Argo Rollouts), not a manual script;
the organization already runs 30 to 50 or more services, the point where
manual orchestration becomes organizational chaos; need for advanced
operators (Postgres, Kafka, ML platforms); adopting a service mesh
(Istio, Linkerd); or a compliance requirement that demands NetworkPolicy,
granular RBAC, and native audit — the topics of the last lessons in
Phase 5. On the other hand, clear signals that Kubernetes would be
unnecessary complexity: an application with a database and cache on a
single host; a small team (fewer than five developers) without dedicated
capacity to operate a platform; low traffic, with no real need to scale
automatically; or a critical stateful component that nobody on the team
wants to operate directly (in that case, a managed service solves it
better than any orchestrator).</p>

<h3>10. Day-to-day operations: the commands that handle common maintenance</h3>
<pre><code># Logs
docker compose logs -f app                # live tail
docker compose logs --tail=100 app

# Restart só um serviço
docker compose restart app

# Recriar (depois de mudar config)
docker compose up -d --force-recreate app

# Scale
docker compose up -d --scale app=3

# Backup volume
docker run --rm -v pgdata:/data -v $(pwd):/backup alpine \\
  tar czf /backup/pgdata-$(date +%F).tgz -C /data .</code></pre>
<p>The backup command deserves attention: it starts a TEMPORARY container
(<code>alpine</code>, discarded right after via <code>--rm</code>)
mounting the data volume and the destination directory, and uses
<code>tar</code> to compress the contents — a simple, portable pattern
that doesn't depend on any host-specific backup tool.</p>

<h3>11. Six anti-patterns that show up when people stretch Compose beyond what it solves</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Compose is enough</strong><p>Local dev, demos, one host, few services.</p></div>
    <div class="lesson-viz-card"><strong>Time to orchestrate</strong><p>Multi-host, autoscaling, real rolling and discovery.</p></div>
  </div>
  <figcaption>When stretching Compose becomes an operational anti-pattern.</figcaption>
</figure>

<ul>
<li><strong>Compose as multi-host production</strong>: it doesn't scale for
that scenario — use Swarm, Nomad, or Kubernetes according to the real
need (section 9).</li>
<li><strong>Complex stateful in Compose</strong>: real high availability
for a database or queue needs a dedicated tool, not manual volume
orchestration.</li>
<li><strong>Bind mounts in production</strong>: poor portability across
different hosts, and file permissions between host and container
often complicate things in subtle ways.</li>
<li><strong>No healthcheck configured</strong>: inter-service dependencies
break in race conditions exactly as described in section 7.</li>
<li><strong>Sensitive variable directly in `compose.yaml`</strong>: the
file is normally committed to Git — use <code>.env</code>
(in <code>.gitignore</code>) or runtime-managed secrets.</li>
<li><strong>Mixing production and development config in the
same file</strong>: use the override-file pattern from section 2 instead
of conditionals inside a single YAML.</li>
</ul>"""
                ),
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Suba app + Postgres + Redis com Compose v2: healthchecks, "
                    "<code>depends_on</code> com <code>condition: service_healthy</code>, "
                    "volumes nomeados, secrets via arquivo.</li>"
                    "<li>Crie <code>compose.dev.yaml</code> com bind mount + DEBUG=1 "
                    "e <code>compose.prod.yaml</code> com replicas=3 e tag por SHA.</li>"
                    "<li>Configure rede backend interna (sem acesso à internet) para "
                    "DB.</li>"
                    "<li>Use <code>--profile dev</code> para opcionalmente subir "
                    "MailHog/PgAdmin.</li>"
                    "<li>Bonus: converta para Swarm (<code>docker stack deploy</code>) "
                    "e teste em 3 nós (pode ser 3 VMs/Docker Desktops).</li>"
                    "<li>Bonus 2: rode mesma app em Nomad com job HCL e veja diferença "
                    "de UX.</li>"
                    "<li>Bonus 3: configure backup automático do volume pgdata via "
                    "cron + <code>docker run alpine tar</code>.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    '<p><strong>Complete hands-on exercise</strong>:</p><ol><li>Bring up app + Postgres + Redis with Compose v2: healthchecks, <code>depends_on</code> with <code>condition: service_healthy</code>, named volumes, secrets via file.</li><li>Create <code>compose.dev.yaml</code> with bind mount + DEBUG=1 and <code>compose.prod.yaml</code> with replicas=3 and a SHA tag.</li><li>Configure an internal backend network (no internet access) for the DB.</li><li>Use <code>--profile dev</code> to optionally bring up MailHog/PgAdmin.</li><li>Bonus: convert to Swarm (<code>docker stack deploy</code>) and test on 3 nodes (can be 3 VMs/Docker Desktops).</li><li>Bonus 2: run the same app on Nomad with an HCL job and see the UX difference.</li><li>Bonus 3: configure automatic backup of the pgdata volume via cron + <code>docker run alpine tar</code>.</li></ol>'
                ),
            },
            "materials": [
                m("Docker Compose", "https://docs.docker.com/compose/", "docs", "", title_en='Docker Compose', description_en=''),
                m("HashiCorp Nomad", "https://developer.hashicorp.com/nomad/docs", "docs", "", title_en='HashiCorp Nomad', description_en=''),
                m("Docker Swarm", "https://docs.docker.com/engine/swarm/", "docs", "", title_en='Docker Swarm', description_en=''),
                m("Compose Spec", "https://compose-spec.io/", "docs", "", title_en='Compose Spec', description_en=''),
                m("Awesome Compose", "https://github.com/docker/awesome-compose", "tool", "", title_en='Awesome Compose', description_en=''),
                m("Nomad vs K8s", "https://developer.hashicorp.com/nomad/docs/nomad-vs-kubernetes",
                  "article", "", title_en='Nomad vs K8s', description_en=''),
            ],
            "questions": [
                q("Docker Compose é apropriado para:",
                  "Desenvolvimento e workloads simples.",
                  ["Funciona só em máquinas rodando Windows.", "Substitui o Kubernetes em qualquer cenário de produção.", "Sistemas distribuídos operando em escala global."],
                  "Em prod single-host, atende muitos casos. Para multi-host/HA real, use Swarm/Nomad/K8s.",
                  statement_en='Docker Compose is appropriate for:',
                  correct_en='Development and simple workloads.',
                  wrong_en=['It only works on machines running Windows.', 'It replaces Kubernetes in any production scenario.', 'Distributed systems operating at global scale.'],
                  explanation_en='In single-host prod, it covers many cases. For real multi-host/HA, use Swarm/Nomad/K8s.'),
                q("Swarm e K8s diferem em:",
                  "Complexidade, K8s mais features e curva.",
                  ["A cor usada no logo de cada uma das ferramentas.", "O idioma principal da documentação oficial de cada uma.", "A linguagem de programação usada para escrever cada uma."],
                  "K8s tem CRDs, operadores, ecossistema enorme. Swarm é mais simples, com menos features.",
                  statement_en='Swarm and K8s differ in:',
                  correct_en='Complexity — K8s has more features and a steeper curve.',
                  wrong_en=["The color used in each tool's logo.", "The primary language of each tool's official documentation.", 'The programming language used to write each one.'],
                  explanation_en='K8s has CRDs, operators, a huge ecosystem. Swarm is simpler, with fewer features.'),
                q("Healthcheck em Compose:",
                  "Define como saber se serviço está saudável.",
                  ["É só um campo opcional sem algum efeito prático.", "Apaga o container automaticamente após cada execução.", "Substitui a necessidade de configurar logs no serviço."],
                  "Permite usar `depends_on: condition: service_healthy` para esperar dependência ficar pronta.",
                  statement_en='A healthcheck in Compose:',
                  correct_en='Defines how to know whether the service is healthy.',
                  wrong_en=["It's just an optional field with no practical effect.", 'Automatically increases the CPU available to the container.', 'Only works when the cluster is running Kubernetes.'],
                  explanation_en='Lets you use `depends_on: condition: service_healthy` to wait for a ready dependency.'),
                q("Volumes nomeados em Compose:",
                  "Persistem dados gerenciados pelo Docker.",
                  ["Não persistem algum dado além do ciclo do container.", "Guardam os dados só em memória RAM temporária.", "Exigem um caminho absoluto fixo no host."],
                  "Sobrevivem a `docker compose down`. Use `down -v` para remover.",
                  statement_en='Named volumes in Compose:',
                  correct_en='Persist data managed by Docker.',
                  wrong_en=["Don't persist any data beyond the container's lifecycle.", 'Increase the RAM available to the service.', 'Replace the DNS service used by the application.'],
                  explanation_en='They survive `docker compose down`. Use `down -v` to remove them.'),
                q("Network bridge default:",
                  "Permite comunicação entre containers da mesma rede.",
                  ["Bloqueia qualquer comunicação entre os containers, atalho comum quando o prazo aperta e ninguém revisa depois.", "Substitui a necessidade de configurar DNS interno, suposição que só vale em ambiente de desenvolvimento, não em produção.", "Funciona só com endereçamento IPv6 configurado, algo que passa no code review quando ninguém olha com atenção."],
                  "Em user-defined bridge, containers se enxergam pelo nome (DNS interno).",
                  statement_en='The default bridge network:',
                  correct_en='Allows communication between containers on the same network.',
                  wrong_en=['Blocks any communication between containers, a shortcut that looks safe in isolation but breaks when combined with other systems.', 'Automatically encrypts all traffic between services.', 'Replaces the need to define any network at all.'],
                  explanation_en='On a user-defined bridge, containers see each other by name (internal DNS).'),
                q("Compose v2 difere de v1:",
                  "É plugin do Docker CLI (`docker compose`), não binário separado.",
                  ["É exatamente a mesma coisa que a versão anterior, atalho que ignora exatamente o cenário que mais importa evitar.", "É uma versão totalmente gratuita, diferente da anterior, que só aparece como problema depois que o sistema já está em produção.", "Funciona só em máquinas rodando macOS, erro típico de configuração feita às pressas, sem revisão posterior."],
                  "v1 (`docker-compose`) está EOL. Use v2 sempre.",
                  statement_en='Compose v2 differs from v1:',
                  correct_en="It's a Docker CLI plugin (`docker compose`), not a separate binary.",
                  wrong_en=["It's exactly the same thing as the previous version, a shortcut that ignores exactly the scenario that matters most to avoid.", 'It only works on the Windows operating system.', 'It completely replaces the need for a Dockerfile.'],
                  explanation_en='v1 (`docker-compose`) is EOL. Always use v2.'),
                q("Para HA em Compose:",
                  "Use deploy.replicas em Swarm ou suba para K8s.",
                  ["O Compose sozinho já garante alta disponibilidade.", "Não existe alguma forma de conseguir alta disponibilidade.", "Basta configurar um backup periódico do serviço."],
                  "Compose puro é single-host. HA real exige Swarm mode ou K8s.",
                  statement_en='For HA with Compose:',
                  correct_en='Use deploy.replicas in Swarm or move up to K8s.',
                  wrong_en=['Compose alone already guarantees high availability.', 'It only works when using Nomad as the orchestrator.', 'HA is unnecessary for any kind of application.'],
                  explanation_en='Plain Compose is single-host. Real HA needs Swarm mode or K8s.'),
                q("`depends_on` faz:",
                  "Define ordem de startup, mas não espera healthcheck por default.",
                  ["Apaga as dependências declaradas no arquivo compose.", "Espera vários healthchecks internos ficarem saudáveis antes de iniciar.", "Só testa a conectividade entre os serviços."],
                  "Para esperar saudável, use `condition: service_healthy` (Compose v2 spec).",
                  statement_en='`depends_on` does:',
                  correct_en="Defines startup order, but doesn't wait for a healthcheck by default.",
                  wrong_en=['Deletes the dependencies declared in the compose file, a common shortcut that looks fine until production surprises you.', 'Automatically runs migrations before starting the app, which tends to fail quietly until someone audits the setup.', 'Replaces the need to configure any healthcheck, an assumption that rarely survives the first real incident review.'],
                  explanation_en='To wait until healthy, use `condition: service_healthy` (Compose v2 spec).'),
                q("Override file:",
                  "Permite sobrepor configs por ambiente.",
                  ["Só funciona para o ambiente de desenvolvimento local.", "Substitui por completo o arquivo compose principal.", "Apaga a configuração de rede do arquivo principal."],
                  "Chain: base.yml + override.yml combina; chave repetida sobrescreve.",
                  statement_en='An override file:',
                  correct_en='Lets you overlay configs per environment.',
                  wrong_en=['Only works for the local development environment.', 'Automatically encrypts secrets in the repository.', 'Replaces the need to use environment variables.'],
                  explanation_en='Chain: base.yml + override.yml merges; a repeated key overrides.'),
                q("Nomad pode rodar:",
                  "Containers, binários e VMs.",
                  ["Só consegue rodar aplicações escritas em Java.", "Só consegue rodar aplicações dentro do browser.", "Só consegue rodar workloads dentro de um cluster K8s."],
                  "Drivers para Docker, exec (binário direto), java, qemu. Útil em ambientes legados.",
                  statement_en='Nomad can run:',
                  correct_en='Containers, binaries, and VMs.',
                  wrong_en=['It can only run applications written in Java.', 'It completely replaces the need for a container registry.', 'It only runs on the Windows operating system.'],
                  explanation_en='Drivers for Docker, exec (direct binary), java, qemu. Useful in mixed legacy environments.'),
            ],
        },
        # =====================================================================
        # 4.5 SBOM
        # =====================================================================
        {
            "title": "Software Bill of Materials (SBOM)",
            "title_en": 'Software Bill of Materials (SBOM)',
            "summary": "Criar a lista de 'ingredientes' do seu software.",
            "summary_en": "Build the list of 'ingredients' in your software.",
            "lesson": {
                "intro": (
                    "Em dezembro de 2021, Log4Shell (CVE-2021-44228) mostrou ao mundo "
                    "uma verdade desconfortável: muitas empresas <em>não sabiam</em> o "
                    "que rodavam. 'Temos Log4j? Em qual versão? Em quais sistemas?' "
                    "Resposta sincera: 'estamos mapeando manualmente'. Quem tinha SBOM "
                    "consultou em segundos. Quem não tinha, fez forensics em planilhas. "
                    "O Executive Order 14028 (Biden, 2021) consolidou SBOM como "
                    "exigência para fornecedores federais nos EUA. Desde então, "
                    "automotive, médico, financeiro também adotaram. SBOM não é "
                    "burocracia, é o pré-requisito para responder rápido a CVEs e a "
                    "ataques de supply chain."
                ),
                "intro_en": (
                    'In December 2021, Log4Shell (CVE-2021-44228) showed the world an '
                    "uncomfortable truth: many companies <em>didn't know</em> what they "
                    "were running. 'Do we have Log4j? Which version? On which systems?' "
                    "Honest answer: 'we're mapping it manually'. Whoever had an SBOM "
                    "checked in seconds. Whoever didn't did forensics in spreadsheets. "
                    'Executive Order 14028 (Biden, 2021) cemented SBOM as a requirement '
                    'for federal suppliers in the US. Since then, automotive, medical, '
                    "and financial sectors have adopted it too. An SBOM isn't bureaucracy "
                    "— it's the prerequisite for responding quickly to CVEs and "
                    'supply-chain attacks.'
                ),
                "body": (
                """<h3>1. O que é SBOM, e por que Log4Shell mudou a conversa sobre isso</h3>
<p>SBOM (Software Bill of Materials) é a lista detalhada de TODOS os
componentes que compõem um artefato — nome e versão de cada dependência
(direta e transitiva), hash de conteúdo para verificação de integridade,
licença de cada componente, o fornecedor de origem, e o relacionamento
entre eles ("X depende de Y"). Antes de dezembro de 2021, ter isso
mapeado com precisão era considerado boa prática opcional. Quando
Log4Shell (CVE-2021-44228) explodiu, a pergunta que toda organização
precisou responder rapidamente foi simplesmente "temos Log4j? Em qual
versão? Em quais sistemas?" — e quem já tinha SBOM gerado automaticamente
consultou essa resposta em SEGUNDOS; quem não tinha, passou dias fazendo
o equivalente a perícia forense em planilhas e memória institucional. O
Executive Order 14028 (governo americano, 2021) consolidou SBOM como
exigência formal para fornecedores federais, e desde então setores como
automotivo, médico e financeiro convergiram para o mesmo padrão — não
por burocracia, mas porque é literalmente o pré-requisito para responder
rápido tanto a uma CVE nova quanto a um ataque de supply chain. A NTIA
(National Telecommunications and Information Administration) define o
mínimo viável de campos que um SBOM precisa ter: nome do fornecedor,
nome do componente, versão, identificador único adicional (PURL ou CPE),
relacionamento de dependência, autor dos dados do SBOM, e timestamp de
geração.</p>
<div class="mermaid">
flowchart LR
    Build["Build do artefato"] --> Syft["Gera SBOM, ex.: Syft"]
    Syft --> SBOM["SBOM: lista de componentes"]
    SBOM --> Scan["Cruza com base de CVE"]
    Scan --> Alert["Alerta se componente vulnerável"]
</div>


<h3>2. Formatos: CycloneDX para segurança, SPDX para compliance de licença</h3>
<table>
<tr><th>Formato</th><th>Origem</th><th>Foco</th></tr>
<tr><td>CycloneDX</td><td>OWASP</td><td>Segurança (vuln, VEX, attestations).</td></tr>
<tr><td>SPDX</td><td>Linux Foundation</td><td>Compliance/licenças. Padrão ISO/IEC 5962.</td></tr>
<tr><td>SWID</td><td>NIST</td><td>Identificação de software.</td></tr>
</table>
<p>CycloneDX nasceu com foco explícito em segurança (integra
naturalmente com VEX, seção 5) enquanto SPDX nasceu com foco em
compliance de licença, sendo inclusive padronizado como norma ISO/IEC —
na prática, muitas organizações geram os dois, já que existem
conversores entre eles e cada um serve uma auditoria diferente. Ambos
suportam serialização em JSON, XML, YAML ou protobuf. Um SBOM CycloneDX
simplificado ilustra a estrutura:</p>
<pre><code>{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:abc-123",
  "version": 1,
  "metadata": {
    "timestamp": "2025-04-25T16:30:00Z",
    "tools": [{"name": "syft", "version": "1.0.0"}],
    "component": {
      "type": "container",
      "name": "empresa/app",
      "version": "v1.4.2"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "django",
      "version": "5.1.4",
      "purl": "pkg:pypi/django@5.1.4",
      "licenses": [{"license": {"id": "BSD-3-Clause"}}],
      "hashes": [{"alg": "SHA-256", "content": "..."}]
    }
  ]
}</code></pre>
<p>O campo <code>purl</code> (Package URL) é o que permite cruzar esse
componente automaticamente contra bases de vulnerabilidade — um
identificador padronizado e sem ambiguidade, diferente de "django versão
5.1.4" em texto livre, que diferentes ferramentas poderiam interpretar
de formas ligeiramente distintas.</p>

<h3>3. Geração: sempre automatizada, nunca manual</h3>
<p>Um SBOM criado à mão está desatualizado no momento em que a primeira
dependência muda — a única prática viável é gerar automaticamente a
cada build. <strong>Syft</strong> (Anchore) é o "canivete suíço" desse
espaço, suportando dezenas de ecossistemas de linguagem numa única
ferramenta:</p>
<pre><code># De diretório
$ syft dir:. -o cyclonedx-json &gt; sbom.json

# De imagem (sem rodar)
$ syft ghcr.io/empresa/app:v1.4.2 -o spdx-json &gt; sbom.spdx.json

# De binário Go
$ syft ./bin/app -o cyclonedx-json

# Saída tabular (humano)
$ syft myapp:dev
NAME              VERSION    TYPE
django            5.1.4      python
asgiref           3.8.1      python
openssl           3.1.5      deb
...</code></pre>
<p><strong>Trivy</strong> gera SBOM ao mesmo tempo que já faz scan de
vulnerabilidade, unindo as duas tarefas numa chamada:</p>
<pre><code>$ trivy image --format cyclonedx --output sbom.json myapp:v1.4.2
$ trivy fs --format spdx-json --output sbom-source.json .</code></pre>
<p>Muitos ecossistemas de linguagem já embutem geração nativa de SBOM em
suas próprias ferramentas de build — npm 10+, Cargo (Rust), Maven
(Java) e um plugin dedicado para Python:</p>
<pre><code>$ npm sbom --sbom-format=cyclonedx                # npm 10+
$ cargo cyclonedx                                 # Rust
$ mvn cyclonedx:makeAggregateBom                  # Java
$ python -m cyclonedx_py environment              # Python</code></pre>
<p>Para ecossistemas menos comuns (PHP Composer, .NET, GraalVM),
<strong>cdxgen</strong> (também um projeto OWASP) preenche lacunas que
as outras ferramentas ainda não cobrem.</p>

<h3>4. Distribuição: o SBOM precisa viajar JUNTO com o artefato, não numa pasta separada</h3>
<p>Um SBOM gerado e guardado num diretório qualquer, desconectado da
imagem que descreve, perde valor rapidamente — a distribuição correta
ancora o SBOM diretamente ao artefato no próprio registry:</p>
<pre><code>$ syft myapp:v1.4.2 -o cyclonedx-json &gt; sbom.json
$ cosign attach sbom --sbom sbom.json myapp:v1.4.2

# Como atestado assinado (mais robusto)
$ cosign attest --predicate sbom.json --type cyclonedx myapp:v1.4.2

# Verificar atestados
$ cosign verify-attestation --type cyclonedx myapp:v1.4.2 \\
    --certificate-identity ci@empresa.com \\
    --certificate-oidc-issuer https://token.actions.githubusercontent.com</code></pre>
<p>Anexar como ATESTADO ASSINADO (não só um arquivo solto) prova que o
SBOM foi de fato gerado por um pipeline autorizado, não adicionado
depois por alguém tentando forjar conformidade — a mesma lógica de
proveniência vista na verificação de assinatura de imagem (aula de
Admission Controllers). Também é possível anexar como asset de um
release do GitHub/GitLab, útil especialmente para binários standalone
distribuídos fora de um registry de container. E para fornecedores
federais americanos, entregar SBOM já é parte formal do processo de
aquisição de software (SP 800-218/SSDF) — outros setores regulados vêm
convergindo para a mesma exigência.</p>

<h3>5. VEX: separar "a vulnerabilidade existe no componente" de "ela me afeta de verdade"</h3>
<p>Um SBOM diz "a biblioteca X versão Y está presente"; cruzar isso com o
NVD diz "existe uma CVE registrada para essa versão". Mas EXISTIR não é
o mesmo que ser EXPLORÁVEL no seu contexto específico — uma função
vulnerável que nunca é chamada com input controlável pelo usuário
representa risco teórico, não risco prático. VEX (Vulnerability
Exploitability eXchange) é uma declaração ASSINADA que expressa essa
distinção explicitamente:</p>
<div class="mermaid">
flowchart LR
    CVE["CVE no componente"] --> Present["Presente no SBOM?"]
    Present --> Vex{"VEX: explorável aqui?"}
    Vex -- "Não" --> Suppress["Suprime / documenta"]
    Vex -- "Sim" --> Patch["Prioriza patch"]
</div>

<pre><code>{
  "vulnerabilities": [
    {
      "id": "CVE-2024-12345",
      "analysis": {
        "state": "not_affected",
        "justification": "vulnerable_code_not_in_execute_path",
        "detail": "Função vulnerável só é chamada com input interno controlado, never user-supplied."
      },
      "affects": [{"ref": "pkg:pypi/lib-x@1.2.3"}]
    }
  ]
}</code></pre>
<p>Os quatro estados possíveis cobrem o ciclo de vida completo de uma
descoberta: <code>not_affected</code> explica formalmente por que a
vulnerabilidade não se aplica; <code>affected</code> reconhece que sim,
afeta, e trabalho de correção está em andamento; <code>fixed</code>
confirma que já foi corrigido numa versão específica; e
<code>under_investigation</code> sinaliza análise ainda em curso. O
ganho prático de VEX é reduzir FADIGA de alerta: sem ele, todo scanner
de segurança dispara alarme para toda CVE teoricamente presente,
inclusive as centenas que nunca seriam exploráveis no contexto real da
aplicação — VEX permite ao time de segurança triar isso uma vez e
documentar a decisão, em vez de reavaliar manualmente o mesmo alerta
repetidamente a cada scan. CSAF (OASIS) e a extensão VEX do próprio
CycloneDX são os padrões mais usados para expressar isso.</p>

<h3>6. Operacionalizar SBOM: de arquivo estático a plataforma que alerta sozinha</h3>
<p>Um SBOM por imagem, isolado, é dado bruto — o valor real aparece
quando uma plataforma CENTRAL ingere SBOMs de TODOS os builds, cruza
CONTINUAMENTE com bases de CVE (NVD, OSV, EPSS) e alerta automaticamente
quando uma vulnerabilidade nova é publicada para um componente já
presente em produção. <strong>Dependency-Track</strong> (projeto OWASP,
open-source) é a implementação de referência dessa ideia: recebe SBOMs
via API, re-cruza periodicamente contra as bases de CVE mesmo para
projetos que não tiveram build novo, notifica quando uma CVE nova surge
para um componente já catalogado, suporta VEX para reduzir ruído (seção
5), e mantém dashboards de vulnerabilidade por projeto e por
severidade:</p>
<pre><code># CI: enviar SBOM ao Dependency-Track
$ curl -X POST https://dt.empresa.com/api/v1/bom \\
    -H "X-Api-Key: $DT_TOKEN" \\
    -F project=$PROJECT_UUID \\
    -F bom=@sbom.json</code></pre>
<p>O detalhe importante aqui é "re-cruza PERIODICAMENTE, mesmo sem build
novo" — uma CVE publicada hoje para uma biblioteca que você usa desde o
ano passado, sem nenhuma mudança de código sua, ainda precisa ser
detectada; sem esse recruzamento contínuo, você só descobriria no
próximo build, que pode nunca acontecer se aquele projeto estiver
estável.</p>

<h3>7. SBOM de código-fonte vs. SBOM de build: visões diferentes, completude diferente</h3>
<p>Um <strong>SBOM de fonte</strong> extrai dependências declaradas em
<code>package.json</code> ou <code>requirements.txt</code> — mas não
enxerga linkagem estática nem bibliotecas do sistema operacional que
acabam embutidas no artefato final. Um <strong>SBOM de build</strong>,
extraído diretamente do binário ou da imagem já construída, vê TUDO que
de fato compõe o artefato final, incluindo o que a análise de código-fonte
sozinha jamais capturaria. A prática recomendada é gerar os DOIS: o SBOM
de fonte serve para "shift-left" — validar dependências ainda no Pull
Request, antes mesmo de construir qualquer coisa — enquanto o SBOM de
build serve como inventário definitivo do que está de fato rodando em
produção.</p>

<h3>8. Cinco limitações honestas do SBOM, mesmo bem implementado</h3>
<p>Compilação estática (típica em Go) pode incluir uma biblioteca sem
que ela apareça de forma óbvia no binário final — ferramentas
"Go-aware" e a flag <code>-buildvcs</code> ajudam a capturar isso
corretamente, mas exige atenção específica. JavaScript minificado
obscurece dependências no artefato final — gerar o SBOM a partir do
código PRÉ-minificação evita essa perda de informação. Containers
multi-stage, felizmente, são bem tratados por ferramentas modernas, que
inspecionam o resultado FINAL do build, não os estágios intermediários
descartados. Linkagem dinâmica contra bibliotecas do sistema (libc,
openssl) é capturada corretamente por Syft e Trivy, que detectam
pacotes do próprio SO instalados na imagem. E o caso mais sutil: um fork
com modificação local aparece no SBOM como se fosse o pacote ORIGINAL —
o scanner não tem como saber que você aplicou um patch próprio por cima,
então uma CVE já corrigida no seu fork ainda apareceria como presente,
ou o inverso, uma modificação sua introduzindo um problema novo não
apareceria em nenhuma base pública.</p>

<h3>9. Um pipeline completo: build, SBOM, assinatura e envio, tudo automatizado</h3>
<pre><code>name: build-sbom-sign
jobs:
  build:
    permissions: { id-token: write, contents: read, packages: write }
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - id: push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/empresa/app:${{ github.sha }}
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/empresa/app@${{ steps.push.outputs.digest }}
          format: cyclonedx-json
          output-file: sbom.json
      - uses: sigstore/cosign-installer@v3
      - name: Sign image + attach SBOM as attestation
        run: |
          cosign sign --yes ghcr.io/empresa/app@${{ steps.push.outputs.digest }}
          cosign attest --yes --predicate sbom.json --type cyclonedx \\
            ghcr.io/empresa/app@${{ steps.push.outputs.digest }}
      - name: Send SBOM to Dependency-Track
        run: |
          curl -X POST https://dt.empresa.com/api/v1/bom \\
            -H "X-Api-Key: $DT_API_KEY" \\
            -F "projectName=app" \\
            -F "projectVersion=${{ github.sha }}" \\
            -F "autoCreate=true" \\
            -F "bom=@sbom.json"
        env: { DT_API_KEY: ${{ secrets.DT_API_KEY }} }</code></pre>
<p>Este pipeline conecta cada peça vista nas seções anteriores numa
sequência única: constrói e publica a imagem, gera o SBOM sobre o
DIGEST específico (não a tag mutável), assina a imagem e anexa o SBOM
como atestado verificável, e envia uma cópia para a plataforma central
que vai monitorar continuamente por CVE nova.</p>

<h3>10. Seis anti-padrões que tornam SBOM um exercício de checklist sem valor real</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Gerar SBOM no build, nunca à mão.</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Publicar junto do artefato.</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Alertar com VEX, não só com lista crua.</p></div>
  </div>
  <figcaption>SBOM útil: automatizado, anexado e acionável.</figcaption>
</figure>

<ul>
<li><strong>SBOM gerado manualmente</strong>: desatualizado em horas,
pelo simples fato de dependências mudarem constantemente.</li>
<li><strong>SBOM sem distribuição</strong>: um arquivo esquecido numa
pasta, nunca anexado ao artefato que descreve.</li>
<li><strong>SBOM sem operacionalização</strong>: gerado, mas nunca
efetivamente consultado por ninguém nem cruzado com CVE nova.</li>
<li><strong>SBOM só no momento do build, nunca sobre o que está EM
USO</strong>: um incidente real exige saber quem TEM aquele componente
rodando agora, não só quem o teve num build passado.</li>
<li><strong>Sem VEX</strong>: alertas crescem até o time simplesmente
parar de olhar para eles, o efeito exato que VEX existe para prevenir.</li>
<li><strong>Formato proprietário</strong>: prefira CycloneDX ou SPDX —
formatos abertos e amplamente suportados por ferramentas de terceiros,
em vez de um formato que só a sua própria plataforma entende.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. What an SBOM is, and why Log4Shell changed the conversation about it</h3>
<p>SBOM (Software Bill of Materials) is the detailed list of ALL
components that make up an artifact — name and version of every
dependency (direct and transitive), content hash for integrity
verification, each component's license, the originating supplier, and
the relationship between them ("X depends on Y"). Before December 2021,
having this mapped precisely was considered optional good practice. When
Log4Shell (CVE-2021-44228) exploded, the question every organization
needed to answer quickly was simply "do we have Log4j? Which version? On
which systems?" — and whoever already had an automatically generated SBOM
looked up that answer in SECONDS; whoever didn't spent days doing the
equivalent of forensic work in spreadsheets and institutional memory. Executive
Order 14028 (US government, 2021) cemented SBOM as a formal requirement
for federal suppliers, and since then sectors like automotive, medical,
and financial have converged on the same standard — not for bureaucracy,
but because it is literally the prerequisite for responding quickly both
to a new CVE and to a supply-chain attack. The NTIA (National
Telecommunications and Information Administration) defines the minimum
viable fields an SBOM needs: supplier name, component name, version,
additional unique identifier (PURL or CPE), dependency relationship,
author of the SBOM data, and generation timestamp.</p>
<div class="mermaid">
flowchart LR
    Build["Artifact build"] --> Syft["Generate SBOM, e.g. Syft"]
    Syft --> SBOM["SBOM: component list"]
    SBOM --> Scan["Cross-check CVE database"]
    Scan --> Alert["Alert if a component is vulnerable"]
</div>


<h3>2. Formats: CycloneDX for security, SPDX for license compliance</h3>
<table>
<tr><th>Formato</th><th>Origem</th><th>Foco</th></tr>
<tr><td>CycloneDX</td><td>OWASP</td><td>Segurança (vuln, VEX, attestations).</td></tr>
<tr><td>SPDX</td><td>Linux Foundation</td><td>Compliance/licenças. Padrão ISO/IEC 5962.</td></tr>
<tr><td>SWID</td><td>NIST</td><td>Identificação de software.</td></tr>
</table>
<p>CycloneDX was born with an explicit security focus (it integrates
naturally with VEX, section 5) while SPDX was born with a license
compliance focus, even standardized as an ISO/IEC norm — in practice,
many organizations generate both, since converters exist between them
and each serves a different audit. Both support serialization in JSON,
XML, YAML, or protobuf. A simplified CycloneDX SBOM illustrates the
structure:</p>
<pre><code>{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:abc-123",
  "version": 1,
  "metadata": {
    "timestamp": "2025-04-25T16:30:00Z",
    "tools": [{"name": "syft", "version": "1.0.0"}],
    "component": {
      "type": "container",
      "name": "empresa/app",
      "version": "v1.4.2"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "django",
      "version": "5.1.4",
      "purl": "pkg:pypi/django@5.1.4",
      "licenses": [{"license": {"id": "BSD-3-Clause"}}],
      "hashes": [{"alg": "SHA-256", "content": "..."}]
    }
  ]
}</code></pre>
<p>The <code>purl</code> field (Package URL) is what lets you
automatically cross-reference that component against vulnerability
databases — a standardized, unambiguous identifier, unlike "django
version 5.1.4" in free text, which different tools could interpret in
slightly different ways.</p>

<h3>3. Generation: always automated, never manual</h3>
<p>A hand-built SBOM is stale the moment the first dependency changes —
the only viable practice is to generate automatically on every build.
<strong>Syft</strong> (Anchore) is the "Swiss army knife" of this
space, supporting dozens of language ecosystems in a single tool:</p>
<pre><code># De diretório
$ syft dir:. -o cyclonedx-json &gt; sbom.json

# De imagem (sem rodar)
$ syft ghcr.io/empresa/app:v1.4.2 -o spdx-json &gt; sbom.spdx.json

# De binário Go
$ syft ./bin/app -o cyclonedx-json

# Saída tabular (humano)
$ syft myapp:dev
NAME              VERSION    TYPE
django            5.1.4      python
asgiref           3.8.1      python
openssl           3.1.5      deb
...</code></pre>
<p><strong>Trivy</strong> generates an SBOM at the same time it already
runs a vulnerability scan, combining both tasks in one call:</p>
<pre><code>$ trivy image --format cyclonedx --output sbom.json myapp:v1.4.2
$ trivy fs --format spdx-json --output sbom-source.json .</code></pre>
<p>Many language ecosystems already embed native SBOM generation in
their own build tools — npm 10+, Cargo (Rust), Maven (Java), and a
dedicated plugin for Python:</p>
<pre><code>$ npm sbom --sbom-format=cyclonedx                # npm 10+
$ cargo cyclonedx                                 # Rust
$ mvn cyclonedx:makeAggregateBom                  # Java
$ python -m cyclonedx_py environment              # Python</code></pre>
<p>For less common ecosystems (PHP Composer, .NET, GraalVM),
<strong>cdxgen</strong> (also an OWASP project) fills gaps the other
tools still don't cover.</p>

<h3>4. Distribution: the SBOM must travel WITH the artifact, not in a separate folder</h3>
<p>An SBOM generated and stored in some random directory, disconnected
from the image it describes, loses value quickly — correct distribution
anchors the SBOM directly to the artifact in the registry itself:</p>
<pre><code>$ syft myapp:v1.4.2 -o cyclonedx-json &gt; sbom.json
$ cosign attach sbom --sbom sbom.json myapp:v1.4.2

# Como atestado assinado (mais robusto)
$ cosign attest --predicate sbom.json --type cyclonedx myapp:v1.4.2

# Verificar atestados
$ cosign verify-attestation --type cyclonedx myapp:v1.4.2 \\
    --certificate-identity ci@empresa.com \\
    --certificate-oidc-issuer https://token.actions.githubusercontent.com</code></pre>
<p>Attaching it as a SIGNED ATTESTATION (not just a loose file) proves
the SBOM was actually generated by an authorized pipeline, not added
later by someone trying to fake compliance — the same provenance logic
seen in image signature verification (Admission Controllers lesson). It
is also possible to attach it as a GitHub/GitLab release asset, especially
useful for standalone binaries distributed outside a container registry.
And for US federal suppliers, delivering an SBOM is already a formal part
of the software acquisition process (SP 800-218/SSDF) — other regulated
sectors are converging on the same requirement.</p>

<h3>5. VEX: separating "the vulnerability exists in the component" from "it actually affects me"</h3>
<p>An SBOM says "library X version Y is present"; crossing that with the
NVD says "there is a CVE registered for that version". But EXISTING is
not the same as being EXPLOITABLE in your specific context — a vulnerable
function that is never called with user-controllable input represents
theoretical risk, not practical risk. VEX (Vulnerability Exploitability
eXchange) is a SIGNED declaration that expresses that distinction
explicitly:</p>
<div class="mermaid">
flowchart LR
    CVE["CVE in component"] --> Present["Present in SBOM?"]
    Present --> Vex{"VEX: exploitable here?"}
    Vex -- "No" --> Suppress["Suppress / document"]
    Vex -- "Yes" --> Patch["Prioritize patch"]
</div>

<pre><code>{
  "vulnerabilities": [
    {
      "id": "CVE-2024-12345",
      "analysis": {
        "state": "not_affected",
        "justification": "vulnerable_code_not_in_execute_path",
        "detail": "Função vulnerável só é chamada com input interno controlado, never user-supplied."
      },
      "affects": [{"ref": "pkg:pypi/lib-x@1.2.3"}]
    }
  ]
}</code></pre>
<p>The four possible states cover the full lifecycle of a finding:
<code>not_affected</code> formally explains why the vulnerability does
not apply; <code>affected</code> acknowledges that yes, it affects, and
remediation work is underway; <code>fixed</code> confirms it was already
fixed in a specific version; and <code>under_investigation</code> signals
analysis still in progress. The practical gain of VEX is reducing alert
FATIGUE: without it, every security scanner fires an alarm for every
theoretically present CVE, including the hundreds that would never be
exploitable in the application's real context — VEX lets the security
team triage that once and document the decision, instead of manually
re-evaluating the same alert repeatedly on every scan. CSAF (OASIS) and
CycloneDX's own VEX extension are the most used standards to express
this.</p>

<h3>6. Operationalizing SBOM: from a static file to a platform that alerts on its own</h3>
<p>One SBOM per image, isolated, is raw data — the real value appears
when a CENTRAL platform ingests SBOMs from ALL builds, CONTINUOUSLY
cross-references vulnerability databases (NVD, OSV, EPSS), and alerts
automatically when a new vulnerability is published for a component
already present in production. <strong>Dependency-Track</strong> (OWASP
project, open-source) is the reference implementation of that idea: it
receives SBOMs via API, periodically re-crosses CVE databases even for
projects that had no new build, notifies when a new CVE appears for an
already catalogued component, supports VEX to reduce noise (section 5),
and keeps vulnerability dashboards by project and by severity:</p>
<pre><code># CI: enviar SBOM ao Dependency-Track
$ curl -X POST https://dt.empresa.com/api/v1/bom \\
    -H "X-Api-Key: $DT_TOKEN" \\
    -F project=$PROJECT_UUID \\
    -F bom=@sbom.json</code></pre>
<p>The important detail here is "re-crosses PERIODICALLY, even without a
new build" — a CVE published today for a library you've used since last
year, with no code change of yours, still needs to be detected; without
that continuous re-crossing, you would only discover it on the next
build, which may never happen if that project is stable.</p>

<h3>7. Source SBOM vs build SBOM: different views, different completeness</h3>
<p>A <strong>source SBOM</strong> extracts dependencies declared in
<code>package.json</code> or <code>requirements.txt</code> — but it
doesn't see static linking or operating-system libraries that end up
embedded in the final artifact. A <strong>build SBOM</strong>,
extracted directly from the already-built binary or image, sees
EVERYTHING that actually makes up the final artifact, including what
source analysis alone would never capture. The recommended practice is
to generate BOTH: the source SBOM serves "shift-left" — validating
dependencies still in the Pull Request, before building anything —
while the build SBOM serves as the definitive inventory of what is
actually running in production.</p>

<h3>8. Five honest limitations of SBOM, even when well implemented</h3>
<p>Static compilation (typical in Go) can include a library without it
appearing obviously in the final binary — "Go-aware" tools and the
<code>-buildvcs</code> flag help capture that correctly, but it needs
specific attention. Minified JavaScript obscures dependencies in the
final artifact — generating the SBOM from PRE-minification code avoids
that information loss. Multi-stage containers, fortunately, are well
handled by modern tools, which inspect the FINAL build result, not the
discarded intermediate stages. Dynamic linking against system libraries
(libc, openssl) is correctly captured by Syft and Trivy, which detect
OS packages installed in the image. And the most subtle case: a fork
with a local modification appears in the SBOM as if it were the ORIGINAL
package — the scanner has no way to know you applied your own patch on
top, so a CVE already fixed in your fork would still appear as present,
or the inverse, a modification of yours introducing a new problem would
not appear in any public database.</p>

<h3>9. A complete pipeline: build, SBOM, signing, and upload — all automated</h3>
<pre><code>name: build-sbom-sign
jobs:
  build:
    permissions: { id-token: write, contents: read, packages: write }
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - id: push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/empresa/app:${{ github.sha }}
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/empresa/app@${{ steps.push.outputs.digest }}
          format: cyclonedx-json
          output-file: sbom.json
      - uses: sigstore/cosign-installer@v3
      - name: Sign image + attach SBOM as attestation
        run: |
          cosign sign --yes ghcr.io/empresa/app@${{ steps.push.outputs.digest }}
          cosign attest --yes --predicate sbom.json --type cyclonedx \\
            ghcr.io/empresa/app@${{ steps.push.outputs.digest }}
      - name: Send SBOM to Dependency-Track
        run: |
          curl -X POST https://dt.empresa.com/api/v1/bom \\
            -H "X-Api-Key: $DT_API_KEY" \\
            -F "projectName=app" \\
            -F "projectVersion=${{ github.sha }}" \\
            -F "autoCreate=true" \\
            -F "bom=@sbom.json"
        env: { DT_API_KEY: ${{ secrets.DT_API_KEY }} }</code></pre>
<p>This pipeline connects every piece from the previous sections into a
single sequence: builds and publishes the image, generates the SBOM over
the specific DIGEST (not the mutable tag), signs the image and attaches
the SBOM as a verifiable attestation, and sends a copy to the central
platform that will continuously monitor for new CVEs.</p>

<h3>10. Six anti-patterns that turn SBOM into a checklist exercise with no real value</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Generate SBOM in the build, never by hand.</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Publish it with the artifact.</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Alert with VEX, not a raw list alone.</p></div>
  </div>
  <figcaption>Useful SBOM: automated, attached, and actionable.</figcaption>
</figure>

<ul>
<li><strong>Manually generated SBOM</strong>: stale within hours,
simply because dependencies change constantly.</li>
<li><strong>SBOM without distribution</strong>: a forgotten file in a
folder, never attached to the artifact it describes.</li>
<li><strong>SBOM without operationalization</strong>: generated, but never
actually consulted by anyone or crossed with new CVEs.</li>
<li><strong>SBOM only at build time, never over what is IN
USE</strong>: a real incident requires knowing who HAS that component
running now, not only who had it in a past build.</li>
<li><strong>No VEX</strong>: alerts grow until the team simply
stops looking at them — the exact effect VEX exists to prevent.</li>
<li><strong>Proprietary format</strong>: prefer CycloneDX or SPDX —
open formats widely supported by third-party tools,
instead of a format only your own platform understands.</li>
</ul>"""
                ),
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Gere SBOM da sua imagem com Syft "
                    "(<code>syft myapp:dev -o cyclonedx-json &gt; sbom.json</code>).</li>"
                    "<li>Anexe ao registry com <code>cosign attest</code>.</li>"
                    "<li>Cruze com Trivy: <code>trivy sbom sbom.json</code>.</li>"
                    "<li>Suba Dependency-Track local (Docker Compose) e envie SBOMs "
                    "do CI.</li>"
                    "<li>Crie um VEX para 1 CVE marcando como "
                    "<code>not_affected</code> com justificativa.</li>"
                    "<li>Configure GitHub Action que envia SBOM para "
                    "Dependency-Track em todo build.</li>"
                    "<li>Bonus: gere atestado SLSA L3 + SBOM como referrers no GHCR.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    '<p><strong>Complete hands-on exercise</strong>:</p><ol><li>Generate an SBOM for your image with Syft (<code>syft myapp:dev -o cyclonedx-json &gt; sbom.json</code>).</li><li>Attach it to the registry with <code>cosign attest</code>.</li><li>Cross-check with Trivy: <code>trivy sbom sbom.json</code>.</li><li>Bring up Dependency-Track locally (Docker Compose) and send SBOMs from CI.</li><li>Create a VEX for 1 CVE marking it as <code>not_affected</code> with a justification.</li><li>Configure a GitHub Action that sends the SBOM to Dependency-Track on every build.</li><li>Bonus: generate an SLSA L3 attestation + SBOM as referrers on GHCR.</li></ol>'
                ),
            },
            "materials": [
                m("CISA SBOM", "https://www.cisa.gov/sbom", "docs", "", title_en='CISA SBOM', description_en=''),
                m("CycloneDX", "https://cyclonedx.org/specification/overview/", "docs", "", title_en='CycloneDX', description_en=''),
                m("SPDX", "https://spdx.dev/", "docs", "", title_en='SPDX', description_en=''),
                m("Syft", "https://github.com/anchore/syft", "tool", "", title_en='Syft', description_en=''),
                m("VEX (CISA)", "https://www.cisa.gov/sites/default/files/2023-04/minimum-requirements-for-vex-508c.pdf", "docs", "", title_en='VEX (CISA)', description_en=''),
                m("Dependency-Track", "https://dependencytrack.org/", "tool",
                  "Plataforma OSS para SBOM ops.", title_en='Dependency-Track', description_en='OSS platform for SBOM ops.'),
            ],
            "questions": [
                q("SBOM é:",
                  "Inventário detalhado de componentes do software.",
                  ["Uma ferramenta de linter para checar estilo de código.", "Um tipo específico de configuração de TLS.", "Um mecanismo de backup automático do artefato."],
                  "Inclui versão, supplier, hash. Permite responder 'tenho Log4j 2.14?' em segundos.",
                  statement_en='An SBOM is:',
                  correct_en="A detailed inventory of the software's components.",
                  wrong_en=['A linter tool for checking code style, a common shortcut that looks fine until production surprises you.', 'A type of TLS certificate used in the connection, which tends to fail quietly until someone audits the setup.', 'A Kubernetes orchestrator for containers, an assumption that rarely survives the first real incident review.'],
                  explanation_en="Includes version, supplier, hash. Lets you answer 'do we have Log4j 2.14?' in seconds."),
                q("Formato aberto popular:",
                  "CycloneDX e SPDX.",
                  ["Um formato de token usado para autenticação.", "Só um arquivo simples no formato CSV.", "Um arquivo de texto formatado em Markdown."],
                  "Os dois são padrões reconhecidos pelo NIST e usados pela CISA.",
                  statement_en='A popular open format:',
                  correct_en='CycloneDX and SPDX.',
                  wrong_en=['A token format used for authentication.', 'A proprietary format exclusive to AWS.', "A binary format that can't be read by tools."],
                  explanation_en='Both are standards recognized by NIST and used by CISA.'),
                q("SBOM ajuda em:",
                  "Resposta rápida a CVEs.",
                  ["Ajuda a calcular o preço cobrado pelo fornecedor.", "Serve como material de marketing para o produto.", "Ajuda a configurar registros de DNS do serviço."],
                  "Em Log4Shell, empresas com SBOM consultaram em segundos; o resto fez forensics manual.",
                  statement_en='An SBOM helps with:',
                  correct_en='Fast response to CVEs.',
                  wrong_en=['Helping calculate the price charged by the vendor.', 'Automatically compiling the application source code.', 'Replacing the need for any kind of backup.'],
                  explanation_en='In Log4Shell, companies with an SBOM checked in seconds; everyone else did manual forensics.'),
                q("VEX descreve:",
                  "Se uma vulnerabilidade afeta de fato seu produto.",
                  ["A versão específica de TLS usada na conexão, erro comum de quem aprendeu por tentativa e erro, sem revisar a documentação oficial.", "Um tipo específico de log gerado pela aplicação, prática que gera falso senso de segurança no time.", "Uma cópia de backup guardada do artefato final, algo que passa no code review quando ninguém olha com atenção."],
                  "Reduz fadiga: 'CVE existe mas função não é alcançável no nosso uso'.",
                  statement_en='VEX describes:',
                  correct_en='Whether a vulnerability actually affects your product.',
                  wrong_en=['The specific TLS version used in the connection, a common mistake for those who learned by trial and error.', 'The exact size of the Docker image in megabytes.', 'The DNS configuration of the production domain.'],
                  explanation_en="Reduces fatigue: 'the CVE exists but the function isn't reachable in our usage'."),
                q("SBOM deve ser:",
                  "Legível por máquina, gerado automaticamente.",
                  ["Preenchido manualmente a cada novo release.", "Entregue só em formato PDF fechado.", "Escrito e revisado só por humanos, sem automação."],
                  "Manual é desatualizado e impreciso. Geração no build é regra.",
                  statement_en='An SBOM should be:',
                  correct_en='Machine-readable, generated automatically.',
                  wrong_en=['Filled in manually on every new release, a common shortcut that looks fine until production surprises you.', 'Written only in natural language prose, which tends to fail quietly until someone audits the setup.', 'Optional in any regulated environment, an assumption that rarely survives the first real incident review.'],
                  explanation_en='Manual is stale and inaccurate. Generation at build time is the rule.'),
                q("Syft gera SBOM de:",
                  "Imagens, diretórios, archives.",
                  ["Só consegue gerar SBOM de projetos em Python.", "Só consegue gerar SBOM a partir de arquivo zip.", "Só consegue gerar SBOM de imagem Docker."],
                  "Suporta Python, Node, Java, Go, Rust, etc. Detecta ecossistema automaticamente.",
                  statement_en='Syft generates an SBOM from:',
                  correct_en='Images, directories, archives.',
                  wrong_en=['It can only generate an SBOM for Python projects.', 'It only works on the Windows operating system.', 'It only analyzes network traffic between services.'],
                  explanation_en='Supports Python, Node, Java, Go, Rust, etc. Detects the ecosystem automatically.'),
                q("Após Log4Shell, SBOM virou:",
                  "Requisito quase regulatório em muitos setores.",
                  ["Uma opção considerada desnecessária pela maioria.", "Uma exigência que existe só no Brasil.", "Só um modal de interface dentro da ferramenta."],
                  "EO 14028 (EUA) tornou SBOM obrigatório para compras federais.",
                  statement_en='After Log4Shell, SBOM became:',
                  correct_en='An almost regulatory requirement in many sectors.',
                  wrong_en=['An option considered unnecessary by most people.', 'A practice exclusive to open-source projects.', 'A replacement for any kind of vulnerability scanning.'],
                  explanation_en='EO 14028 (US) made SBOM mandatory for federal purchases.'),
                q("SBOM e SCA:",
                  "Complementares, SBOM é o inventário, SCA é a análise.",
                  ["Ferramentas substitutas uma da outra, raramente usadas juntas.", "Duas ferramentas concorrentes que competem pelo mesmo mercado.", "Dois termos sinônimos para exatamente a mesma coisa."],
                  "Trivy faz ambos. SBOM é o 'o quê'; SCA é 'tem CVE/EPSS no quê'.",
                  statement_en='SBOM and SCA:',
                  correct_en='Complementary — SBOM is the inventory, SCA is the analysis.',
                  wrong_en=['Tools that substitute for each other, rarely used together.', 'Exactly the same thing with different names.', "Incompatible approaches that can't be combined."],
                  explanation_en="Trivy does both. SBOM is the 'what'; SCA is 'is there a CVE/EPSS in the what'."),
                q("Distribuir SBOM:",
                  "Junto do artefato, em registry OCI ou anexo do release.",
                  ["Enviado manualmente por e-mail para o time de segurança.", "Não precisa ser distribuído junto de muito pouco.", "Distribuído só por e-mail para o time responsável."],
                  "Cosign attach sbom anexa ao manifest no registry. Quem puxa a imagem pode puxar a SBOM.",
                  statement_en='Distributing an SBOM:',
                  correct_en='Alongside the artifact, in an OCI registry or release attachment.',
                  wrong_en=['Sent manually by email to the security team, a common shortcut that looks fine until production surprises you.', "Stored only on a local developer's laptop, which tends to fail quietly until someone audits the setup.", 'Published exclusively as a PDF in Confluence, an assumption that rarely survives the first real incident review.'],
                  explanation_en='Cosign attach sbom attaches it to the manifest in the registry. Whoever pulls the image can pull the SBOM.'),
                q("SBOM sem governança é:",
                  "Arquivo morto, precisa rotina de uso.",
                  ["Substitui a necessidade de aplicar qualquer patch.", "Completamente inútil em qualquer cenário de uso.", "Um gerador automático de patches para o time."],
                  "Sem ingestion (Dependency-Track) e alertas, SBOM fica esquecido.",
                  statement_en='An SBOM without governance is:',
                  correct_en='A dead file — it needs a usage routine.',
                  wrong_en=['A replacement for the need to apply any patch.', 'Enough on its own to guarantee total security.', 'Automatically updated without any tooling.'],
                  explanation_en='Without ingestion (Dependency-Track) and alerts, the SBOM gets forgotten.'),
            ],
        },
        # =====================================================================
        # 4.6 IDP
        # =====================================================================
        {
            "title": "Internal Developer Platforms (IDP)",
            "title_en": 'Internal Developer Platforms (IDP)',
            "summary": "Facilitar a vida do dev criando ferramentas self-service.",
            "summary_en": "Make developers' lives easier by building self-service tools.",
            "lesson": {
                "intro": (
                    "Empresa moderna tem &gt;50 ferramentas: GitHub, K8s, Terraform, "
                    "Datadog, Sentry, PagerDuty, Vault, Jenkins/GH Actions, AWS, etc. "
                    "Dev precisa entender todas para entregar valor? Não, esse é o "
                    "papel de Internal Developer Platform (IDP). IDP empacota infra "
                    "como produto interno: dev preenche form, plataforma provisiona; "
                    "dev abre PR, plataforma valida com guard-rails; dev abre dashboard, "
                    "plataforma mostra logs/métricas/traces correlacionados. Empresas "
                    "que fazem bem (Spotify, Netflix, American Airlines) reduzem "
                    "time-to-first-deploy de novo serviço de meses para horas. Esta "
                    "aula cobre o porquê, componentes (Backstage, Crossplane, "
                    "Humanitec), Team Topologies como modelo organizacional, e os "
                    "armadilhas mais comuns."
                ),
                "intro_en": "A modern company has &gt;50 tools: GitHub, K8s, Terraform, Datadog, Sentry, PagerDuty, Vault, Jenkins/GH Actions, AWS, and more. Does a developer need to understand all of them to deliver value? No — that's the job of an Internal Developer Platform (IDP). An IDP packages infra as an internal product: the developer fills out a form, the platform provisions; the developer opens a PR, the platform validates with guardrails; the developer opens a dashboard, the platform shows correlated logs/metrics/traces. Companies that do this well (Spotify, Netflix, American Airlines) cut time-to-first-deploy of a new service from months to hours. This lesson covers the why, the components (Backstage, Crossplane, Humanitec), Team Topologies as an organizational model, and the most common pitfalls.",
                "body": (
                """<h3>1. Por que uma IDP existe: cada time reinventando a roda, multiplicado por dezenas</h3>
<p>Numa organização que cresce, cada time novo acaba decidindo
individualmente como montar seu próprio pipeline, como configurar log e
métrica, qual padrão de service mesh seguir, como provisionar banco ou
fila, e quem exatamente revisa segurança daquele serviço específico. O
resultado, multiplicado por dezenas de times, é uma organização com
dezenas de formas diferentes de resolver o MESMO problema — manutenção
explode (cada variação precisa de suporte próprio), onboarding de um
engenheiro novo vira meses (cada time tem seu jeito único de fazer
deploy), a cobertura real de segurança fica inconsistente entre times, e
não há visibilidade nenhuma sobre o que times diferentes estão fazendo.
Uma Internal Developer Platform ataca isso oferecendo um "caminho de
ouro" (golden path) — o jeito recomendado, já pronto, para as tarefas
comuns; self-service real, onde provisionar um banco vira uma ação
imediata em vez de um ticket esperando dias por resposta humana;
guard-rails EMBUTIDOS, onde o desenvolvedor não precisa lembrar de
habilitar encryption porque ela já vem ligada por padrão; um catálogo
unificado que responde "quem é dono do serviço X?" em um clique, não uma
busca em planilha desatualizada; e observabilidade padrão, onde todo
serviço novo já nasce com dashboard e SLO configurados, sem trabalho
manual extra.</p>
<div class="mermaid">
flowchart LR
    Dev["Desenvolvedor"] -- "Pede um serviço novo" --> Portal["Portal da IDP"]
    Portal --> Template["Aplica o golden path"]
    Template --> Infra["Provisiona infraestrutura"]
    Infra --> Dev
</div>


<h3>2. Os componentes que compõem uma plataforma completa</h3>
<table>
<tr><th>Componente</th><th>O que faz</th><th>Ferramentas</th></tr>
<tr><td>Portal</td><td>UI única para devs</td><td>Backstage, Port, OpsLevel</td></tr>
<tr><td>Catálogo</td><td>Inventário de serviços/teams/APIs</td><td>Backstage Software Catalog</td></tr>
<tr><td>Templates/Scaffolder</td><td>Bootstrap padronizado de novos serviços</td><td>Backstage Scaffolder, Cookiecutter, Yeoman</td></tr>
<tr><td>Self-service infra</td><td>Provisão sem ticket</td><td>Crossplane, Humanitec, Terraform via TFC</td></tr>
<tr><td>Pipeline padrão</td><td>CI/CD reutilizável</td><td>GitHub Actions reusable workflows, GitLab include</td></tr>
<tr><td>Observability default</td><td>Dashboards/SLOs auto</td><td>Datadog APIs, Grafana provisioning</td></tr>
<tr><td>Docs/TechDocs</td><td>Docs as code</td><td>Backstage TechDocs, Docusaurus</td></tr>
<tr><td>Compliance/Policy</td><td>Guard-rails</td><td>OPA/Conftest, Kyverno, Sentinel</td></tr>
</table>
<p>Nenhuma organização precisa de TODOS esses componentes desde o
primeiro dia — a maioria dos programas de plataforma bem-sucedidos
começa com portal e templates (as dores mais visíveis) e adiciona
self-service de infraestrutura e observabilidade automática conforme o
programa amadurece e ganha confiança dos times.</p>

<h3>3. Backstage: o portal que virou referência do setor</h3>
<p>Backstage é open-source, criado pelo Spotify em 2020 e hoje hospedado
pela CNCF, com plugins cobrindo praticamente toda ferramenta comum de
engenharia — Kubernetes, GitHub, GitLab, Datadog, Sentry, PagerDuty,
Argo CD, entre dezenas de outros. O Software Catalog modela o mundo em
entidades — Component, API, System, Resource, Domain, Group, User — e as
relações entre elas (um Component é "owned by" um Group, "consumes" uma
API, "part of" um System) constroem um grafo de dependência e
propriedade navegável:</p>
<pre><code># catalog-info.yaml (no repo do serviço)
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: orders-api
  description: API de pedidos
  annotations:
    backstage.io/techdocs-ref: dir:.
    github.com/project-slug: empresa/orders-api
    pagerduty.com/service-id: PXYZ123
    sentry.io/project-slug: orders-api
    grafana/dashboard-selector: "folderTitle = 'Orders'"
spec:
  type: service
  lifecycle: production
  owner: payments-team
  system: payments
  consumesApis:
    - users-api
  providesApis:
    - orders-api</code></pre>
<p>O Scaffolder automatiza o nascimento de um serviço novo: o
desenvolvedor escolhe "Criar novo microsserviço Python", preenche um
formulário simples (nome, dono, dependências), e a plataforma executa,
em sequência, a criação do repositório a partir de um template já
aprovado, aplica Dockerfile/CI/observabilidade/docs padrão, registra o
serviço automaticamente no catálogo, cria o serviço correspondente no
PagerDuty, configura Sentry e Datadog, e opcionalmente já provisiona um
banco de dados via Crossplane — tudo o que antes exigia dias de
configuração manual e conhecimento tribal de "como fazemos as coisas
aqui" vira minutos, de forma consistente para todo serviço novo:</p>
<pre><code># template.yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata: { name: python-service }
spec:
  parameters:
    - title: Service info
      properties:
        name: { title: Name, type: string }
        owner: { title: Owner, type: string, ui:field: OwnerPicker }
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
        values: { name: ${{ parameters.name }} }
    - id: publish
      action: publish:github
      input:
        repoUrl: github.com?owner=empresa&repo=${{ parameters.name }}
        defaultBranch: main
    - id: register
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}</code></pre>
<p>TechDocs mantém a documentação como Markdown DENTRO do próprio
repositório do serviço, renderizada automaticamente no Backstage — o
efeito prático é que a documentação fica próxima do código e tende a ser
atualizada no mesmo PR que muda o comportamento, em vez de viver
desconectada num wiki que ninguém lembra de sincronizar.</p>

<h3>4. Self-service de infraestrutura: abstrair a nuvem atrás de uma API simples</h3>
<p>Crossplane traz essa ideia para dentro do próprio Kubernetes: você
define Composite Resource Definitions (XRDs) e Composições que abstraem
detalhes de nuvem específicos atrás de uma API de alto nível:</p>
<pre><code># XRD: API de alto nível 'Database'
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata: { name: xdatabases.platform.empresa.com }
spec:
  group: platform.empresa.com
  names: { kind: XDatabase, plural: xdatabases }
  claimNames: { kind: Database, plural: databases }
  versions:
    - name: v1
      schema:
        openAPIV3Schema:
          properties:
            spec:
              properties:
                size: { enum: [small, medium, large] }
                env: { enum: [dev, staging, prod] }

# Composition: como traduzir para AWS RDS
# (omitido aqui, em prática, mapeia size→instance class etc.)

# Dev consome:
apiVersion: platform.empresa.com/v1
kind: Database
metadata: { name: orders-db, namespace: payments }
spec:
  size: medium
  env: prod</code></pre>
<p>O desenvolvedor só escolhe entre "small/medium/large" e
"dev/staging/prod" — por trás dessa escolha simples, a Composição já
traduz automaticamente para um RDS completo, com encryption habilitada,
backup configurado, multi-AZ para alta disponibilidade, VPC correta e
integração com o gerenciador de segredos, tudo já certo por padrão sem o
desenvolvedor precisar conhecer nenhum desses detalhes. Humanitec resolve
o mesmo problema como SaaS comercial, onde o desenvolvedor escreve
"workload definitions" em YAML e a plataforma traduz para o cluster e
nuvem específicos — mais rápido para começar, com algum nível de
dependência do fornecedor como trade-off. E para times já fortemente
investidos em Terraform, expor módulos internos via Terraform Cloud ou
Spacelift permite ao desenvolvedor preencher variáveis numa interface
simples enquanto o Scaffolder do Backstage dispara a execução por trás.</p>

<h3>5. Team Topologies: a estrutura organizacional que faz a plataforma funcionar de verdade</h3>
<p>O modelo de Manuel Pais e Matthew Skelton define quatro tipos de time
com responsabilidades bem distintas. O time <strong>stream-aligned</strong>
é o time de produto, dono de uma capacidade ou jornada de cliente
específica, focado em entregar valor de negócio. O time
<strong>platform</strong> constrói a IDP como um PRODUTO INTERNO de
verdade — com product manager, design de experiência e roadmap próprio
— cujo cliente é justamente o time stream-aligned. O time
<strong>enabling</strong> funciona como consultoria interna temporária,
ajudando um time stream-aligned a superar uma dor específica e passageira
(adotar um paradigma novo de machine learning, por exemplo) sem virar
dependência permanente. E o time de <strong>subsistema complicado</strong>
existe para um problema intrinsecamente difícil e isolado — um motor de
física, o núcleo de um sistema de ML, algo que exige especialização
profunda e concentrada. O ponto central desse modelo, e o mais fácil de
negligenciar: tratar a plataforma como PRODUTO exige investimento real
em product management e experiência de uso — sem isso, ela tende a
degradar para uma fábrica de tickets ou um wrapper decorativo sem valor
real agregado.</p>
<div class="mermaid">
flowchart TB
    SA["Time stream-aligned"] --> Plat["Time de plataforma"]
    Plat --> SA
    En["Time enabling"] --> SA
    Comp["Complicated-subsystem"] --> SA
</div>


<h3>6. Métricas de sucesso: como provar que a plataforma está funcionando, não só existindo</h3>
<p>Time-to-first-deploy de um serviço novo — medido em horas em vez de
meses — é o indicador mais direto de impacto. O percentual de serviços
novos que de fato adotam os templates oferecidos revela se a plataforma
é um produto DESEJÁVEL, não só disponível. NPS interno mede satisfação
real dos desenvolvedores usando a plataforma no dia a dia. Uma tendência
DECRESCENTE de tickets abertos para o time de SRE indica que problemas
comuns estão sendo resolvidos pela plataforma antes de precisar de
intervenção humana. Métricas DORA melhorando depois da adoção da IDP
conectam o investimento em plataforma a resultado de engenharia
mensurável. E tempo de recuperação (time-to-restore) durante incidente
tende a cair quando o catálogo e os runbooks associados já estão
prontos e acessíveis — em vez de alguém precisar descobrir na hora quem
é dono de qual serviço.</p>

<h3>7. Sete anti-padrões que explicam a maioria dos programas de plataforma que fracassam</h3>
<ul>
<li><strong>Plataforma sem demanda real</strong>: o time constrói o que
ACHA que os desenvolvedores precisam, sem validar antes — a correção é
descoberta ativa (entrevistas) e MVPs pequenos testados cedo.</li>
<li><strong>Plataforma "controle-freak"</strong>: bloqueia toda
flexibilidade e vira gargalo por si só — desenvolvedores acabam criando
"shadow IT" paralelo só para contornar a própria plataforma que deveria
ajudá-los.</li>
<li><strong>Wrapper bonito sem valor real</strong>: um portal que só
esconde visualmente um clique no console da nuvem, sem adicionar
abstração ou automação de verdade por trás.</li>
<li><strong>Sem ownership definido</strong>: templates e ferramentas
ficam sem manutenção contínua — tratar a plataforma como produto exige um
dono de produto dedicado, não um projeto lateral de alguém.</li>
<li><strong>Tudo obrigatório, sem escape hatch</strong>: um golden path
sem exceção nenhuma para casos legitimamente especiais frustra times
mais experientes que têm uma necessidade real fora do padrão comum.</li>
<li><strong>Sem comunidade em volta</strong>: a plataforma vira uma
entrega unilateral de cima para baixo — construir com guildas, horários
de atendimento abertos e RFCs colaborativos gera adoção genuína em vez
de resistência.</li>
<li><strong>Métricas de vaidade</strong>: "temos 50 plugins instalados"
não mede nada de valor real — meça adoção efetiva e impacto, não volume
de recurso disponível.</li>
</ul>

<h3>8. Caso real: como o Backstage nasceu de um problema concreto no Spotify</h3>
<p>O Spotify, com cerca de 6 mil engenheiros, chegou a operar QUATRO
portais internos diferentes e desconectados antes de construir o
Backstage para unificá-los. Os resultados documentados foram
substanciais: onboarding de um novo engenheiro caiu de meses para
semanas; time-to-first-deploy de um serviço novo caiu de 60 dias para 1
dia; adoção interna ultrapassou 90% em três anos. O projeto foi
open-sourced em 2020 e hoje está em incubação na CNCF — e desde então
Netflix, American Airlines, HBO, Wayfair e Box, entre muitas outras,
rodam Backstage internamente como sua própria plataforma de
desenvolvedor.</p>

<h3>9. Por onde começar, sem tentar construir a plataforma perfeita no primeiro ano</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Entreviste dores reais dos times.</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Entregue um único golden path.</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Meça lead time e adoção antes de expandir.</p></div>
  </div>
  <figcaption>Começar pequeno: plataforma que resolve uma dor primeiro.</figcaption>
</figure>

<ol>
<li>Identifique três dores REAIS através de entrevista direta com
desenvolvedores — não suposição do time de plataforma sobre o que eles
precisariam.</li>
<li>Escolha UMA delas para atacar primeiro (por exemplo, "criar um
serviço novo leva duas semanas").</li>
<li>Construa um MVP mínimo: um template, um scaffolder básico, CI
simples, dashboard padrão — o suficiente para provar o conceito, não a
solução completa.</li>
<li>Adote com um ou dois times piloto, e MEÇA o resultado real, não a
impressão subjetiva de sucesso.</li>
<li>Itere com base no feedback recebido antes de expandir mais.</li>
<li>Escale gradualmente para outros squads conforme a confiança
cresce.</li>
<li>Só adicione a próxima capacidade (self-service de banco de dados,
por exemplo) depois que a anterior já estiver bem adotada e estável —
empilhar funcionalidade nova sobre uma base ainda instável multiplica
risco sem necessidade.</li>
</ol>
<p>O erro mais caro em iniciativas de plataforma é tentar construir "a
plataforma definitiva" de uma vez, num único grande esforço de um ano —
começar pequeno, provar valor mensurável, e expandir a partir de sucesso
real é o padrão que consistentemente funciona nos casos documentados de
sucesso.</p>"""
                ),
                "body_en": (
                """<h3>1. Why an IDP exists: every team reinventing the wheel, multiplied by dozens</h3>
<p>In a growing organization, each new team ends up deciding
individually how to build its own pipeline, how to configure logs and
metrics, which service-mesh pattern to follow, how to provision a
database or queue, and who exactly reviews security for that specific
service. The result, multiplied by dozens of teams, is an organization
with dozens of different ways to solve the SAME problem — maintenance
explodes (each variation needs its own support), onboarding a new
engineer turns into months (each team has its unique way to deploy),
real security coverage becomes inconsistent across teams, and there is
no visibility into what different teams are doing. An Internal Developer
Platform attacks this by offering a "golden path" — the recommended,
ready-made way for common tasks; real self-service, where provisioning a
database becomes an immediate action instead of a ticket waiting days for
a human response; BUILT-IN guardrails, where the developer doesn't need
to remember to enable encryption because it already comes on by default;
a unified catalog that answers "who owns service X?" in one click, not a
search through a stale spreadsheet; and standard observability, where
every new service is born with a dashboard and SLO already configured,
with no extra manual work.</p>
<div class="mermaid">
flowchart LR
    Dev["Developer"] -- "Requests a new service" --> Portal["IDP portal"]
    Portal --> Template["Applies the golden path"]
    Template --> Infra["Provisions infrastructure"]
    Infra --> Dev
</div>


<h3>2. The components that make up a complete platform</h3>
<table>
<tr><th>Componente</th><th>O que faz</th><th>Ferramentas</th></tr>
<tr><td>Portal</td><td>UI única para devs</td><td>Backstage, Port, OpsLevel</td></tr>
<tr><td>Catálogo</td><td>Inventário de serviços/teams/APIs</td><td>Backstage Software Catalog</td></tr>
<tr><td>Templates/Scaffolder</td><td>Bootstrap padronizado de novos serviços</td><td>Backstage Scaffolder, Cookiecutter, Yeoman</td></tr>
<tr><td>Self-service infra</td><td>Provisão sem ticket</td><td>Crossplane, Humanitec, Terraform via TFC</td></tr>
<tr><td>Pipeline padrão</td><td>CI/CD reutilizável</td><td>GitHub Actions reusable workflows, GitLab include</td></tr>
<tr><td>Observability default</td><td>Dashboards/SLOs auto</td><td>Datadog APIs, Grafana provisioning</td></tr>
<tr><td>Docs/TechDocs</td><td>Docs as code</td><td>Backstage TechDocs, Docusaurus</td></tr>
<tr><td>Compliance/Policy</td><td>Guard-rails</td><td>OPA/Conftest, Kyverno, Sentinel</td></tr>
</table>
<p>No organization needs ALL of these components from day
one — most successful platform programs start with a portal and templates
(the most visible pains) and add infrastructure self-service and automatic
observability as the program matures and earns team trust.</p>

<h3>3. Backstage: the portal that became the industry reference</h3>
<p>Backstage is open-source, created by Spotify in 2020 and now hosted
by the CNCF, with plugins covering practically every common engineering
tool — Kubernetes, GitHub, GitLab, Datadog, Sentry, PagerDuty,
Argo CD, among dozens of others. The Software Catalog models the world in
entities — Component, API, System, Resource, Domain, Group, User — and the
relationships between them (a Component is "owned by" a Group, "consumes" an
API, "part of" a System) build a navigable dependency and ownership graph:</p>
<pre><code># catalog-info.yaml (no repo do serviço)
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: orders-api
  description: API de pedidos
  annotations:
    backstage.io/techdocs-ref: dir:.
    github.com/project-slug: empresa/orders-api
    pagerduty.com/service-id: PXYZ123
    sentry.io/project-slug: orders-api
    grafana/dashboard-selector: "folderTitle = 'Orders'"
spec:
  type: service
  lifecycle: production
  owner: payments-team
  system: payments
  consumesApis:
    - users-api
  providesApis:
    - orders-api</code></pre>
<p>The Scaffolder automates the birth of a new service: the
developer chooses "Create new Python microservice", fills a simple form
(name, owner, dependencies), and the platform runs, in sequence,
repository creation from an already approved template, applies standard
Dockerfile/CI/observability/docs, automatically registers the service in
the catalog, creates the corresponding PagerDuty service, configures
Sentry and Datadog, and optionally already provisions a database via
Crossplane — everything that used to take days of manual configuration
and tribal knowledge of "how we do things here" becomes minutes, consistently
for every new service:</p>
<pre><code># template.yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata: { name: python-service }
spec:
  parameters:
    - title: Service info
      properties:
        name: { title: Name, type: string }
        owner: { title: Owner, type: string, ui:field: OwnerPicker }
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
        values: { name: ${{ parameters.name }} }
    - id: publish
      action: publish:github
      input:
        repoUrl: github.com?owner=empresa&repo=${{ parameters.name }}
        defaultBranch: main
    - id: register
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}</code></pre>
<p>TechDocs keeps documentation as Markdown INSIDE the service's own
repository, automatically rendered in Backstage — the practical effect is
that docs stay close to the code and tend to be updated in the same PR
that changes behavior, instead of living disconnected in a wiki nobody
remembers to sync.</p>

<h3>4. Infrastructure self-service: abstracting the cloud behind a simple API</h3>
<p>Crossplane brings that idea into Kubernetes itself: you
define Composite Resource Definitions (XRDs) and Compositions that abstract
cloud-specific details behind a high-level API:</p>
<pre><code># XRD: API de alto nível 'Database'
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata: { name: xdatabases.platform.empresa.com }
spec:
  group: platform.empresa.com
  names: { kind: XDatabase, plural: xdatabases }
  claimNames: { kind: Database, plural: databases }
  versions:
    - name: v1
      schema:
        openAPIV3Schema:
          properties:
            spec:
              properties:
                size: { enum: [small, medium, large] }
                env: { enum: [dev, staging, prod] }

# Composition: como traduzir para AWS RDS
# (omitido aqui, em prática, mapeia size→instance class etc.)

# Dev consome:
apiVersion: platform.empresa.com/v1
kind: Database
metadata: { name: orders-db, namespace: payments }
spec:
  size: medium
  env: prod</code></pre>
<p>The developer only chooses among "small/medium/large" and
"dev/staging/prod" — behind that simple choice, the Composition already
automatically translates to a full RDS, with encryption enabled,
backup configured, multi-AZ for high availability, the correct VPC, and
secrets-manager integration, all correct by default without the
developer needing to know any of those details. Humanitec solves the
same problem as commercial SaaS, where the developer writes "workload
definitions" in YAML and the platform translates to the specific cluster
and cloud — faster to start, with some vendor dependency as the
trade-off. And for teams already heavily invested in Terraform, exposing
internal modules via Terraform Cloud or Spacelift lets the developer fill
variables in a simple UI while the Backstage Scaffolder triggers execution
behind the scenes.</p>

<h3>5. Team Topologies: the org structure that makes the platform actually work</h3>
<p>Manuel Pais and Matthew Skelton's model defines four team types
with clearly distinct responsibilities. The <strong>stream-aligned</strong>
team is the product team, owner of a specific customer capability or
journey, focused on delivering business value. The
<strong>platform</strong> team builds the IDP as a real INTERNAL PRODUCT
— with a product manager, experience design, and its own roadmap —
whose customer is precisely the stream-aligned team. The
<strong>enabling</strong> team works as temporary internal consulting,
helping a stream-aligned team overcome a specific, passing pain
(adopting a new machine-learning paradigm, for example) without becoming
a permanent dependency. And the <strong>complicated-subsystem</strong>
team exists for an intrinsically hard, isolated problem — a physics
engine, the core of an ML system, something that demands deep,
concentrated specialization. The central point of this model, and the
easiest to neglect: treating the platform as a PRODUCT requires real
investment in product management and user experience — without that, it
tends to degrade into a ticket factory or a decorative wrapper with no
real aggregated value.</p>
<div class="mermaid">
flowchart TB
    SA["Stream-aligned team"] --> Plat["Platform team"]
    Plat --> SA
    En["Enabling team"] --> SA
    Comp["Complicated-subsystem"] --> SA
</div>


<h3>6. Success metrics: how to prove the platform is working, not just existing</h3>
<p>Time-to-first-deploy of a new service — measured in hours instead of
months — is the most direct impact indicator. The percentage of new
services that actually adopt the offered templates reveals whether the
platform is a DESIRABLE product, not just an available one. Internal NPS
measures real satisfaction of developers using the platform day to day. A
DECREASING trend in tickets opened to the SRE team indicates that common
problems are being solved by the platform before needing human
intervention. Improving DORA metrics after IDP adoption connects the
platform investment to measurable engineering outcomes. And recovery time
(time-to-restore) during an incident tends to drop when the catalog and
associated runbooks are already ready and accessible — instead of someone
needing to discover on the spot who owns which service.</p>

<h3>7. Seven anti-patterns that explain most failed platform programs</h3>
<ul>
<li><strong>Platform without real demand</strong>: the team builds what
it THINKS developers need, without validating first — the fix is
active discovery (interviews) and small MVPs tested early.</li>
<li><strong>"Control-freak" platform</strong>: blocks all flexibility
and becomes a bottleneck itself — developers end up creating parallel
"shadow IT" just to work around the very platform that should help them.</li>
<li><strong>Pretty wrapper with no real value</strong>: a portal that only
visually hides a click on the cloud console, without adding real
abstraction or automation behind it.</li>
<li><strong>No defined ownership</strong>: templates and tools
go without continuous maintenance — treating the platform as a product
requires a dedicated product owner, not someone's side project.</li>
<li><strong>Everything mandatory, no escape hatch</strong>: a golden path
with no exception at all for legitimately special cases frustrates more
experienced teams that have a real need outside the common pattern.</li>
<li><strong>No community around it</strong>: the platform becomes a
top-down unilateral delivery — building with guilds, open office hours,
and collaborative RFCs generates genuine adoption instead of resistance.</li>
<li><strong>Vanity metrics</strong>: "we have 50 plugins installed"
measures nothing of real value — measure effective adoption and impact,
not volume of available features.</li>
</ul>

<h3>8. A real case: how Backstage was born from a concrete problem at Spotify</h3>
<p>Spotify, with about 6 thousand engineers, ended up operating FOUR
different, disconnected internal portals before building Backstage to
unify them. The documented results were substantial: onboarding a new
engineer dropped from months to weeks; time-to-first-deploy of a new
service dropped from 60 days to 1 day; internal adoption surpassed 90%
in three years. The project was open-sourced in 2020 and is now in CNCF
incubation — and since then Netflix, American Airlines, HBO, Wayfair, and
Box, among many others, run Backstage internally as their own developer
platform.</p>

<h3>9. Where to start, without trying to build the perfect platform in year one</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Interview real team pain points.</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Ship a single golden path.</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Measure lead time and adoption before expanding.</p></div>
  </div>
  <figcaption>Start small: a platform that fixes one pain first.</figcaption>
</figure>

<ol>
<li>Identify three REAL pains through direct interviews with
developers — not the platform team's assumption about what they
would need.</li>
<li>Pick ONE of them to attack first (for example, "creating a
new service takes two weeks").</li>
<li>Build a minimal MVP: one template, a basic scaffolder, simple CI,
a standard dashboard — enough to prove the concept, not the complete
solution.</li>
<li>Adopt with one or two pilot teams, and MEASURE the real result, not
the subjective impression of success.</li>
<li>Iterate based on the feedback received before expanding further.</li>
<li>Scale gradually to other squads as confidence grows.</li>
<li>Only add the next capability (database self-service,
for example) after the previous one is already well adopted and stable —
stacking new functionality on an still-unstable base multiplies
risk without need.</li>
</ol>
<p>The most expensive mistake in platform initiatives is trying to build
"the definitive platform" all at once, in a single year-long big push —
starting small, proving measurable value, and expanding from real success
is the pattern that consistently works in documented success cases.</p>"""
                ),
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Suba Backstage local: <code>npx @backstage/create-app</code>, "
                    "rode em dev mode.</li>"
                    "<li>Configure auth GitHub.</li>"
                    "<li>Importe 1 repositório como Component (catalog-info.yaml).</li>"
                    "<li>Crie 1 template Scaffolder que gera repo + workflow básico.</li>"
                    "<li>Adicione plugin Kubernetes para mostrar pods do seu cluster "
                    "kind.</li>"
                    "<li>Adicione TechDocs (Markdown no repo, renderizado).</li>"
                    "<li>Bonus: instale Crossplane no cluster e crie XRD para "
                    "<code>Database</code>; Backstage scaffolder dispara claim.</li>"
                    "<li>Bonus 2: meça time-to-first-deploy com e sem template.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    '<p><strong>Complete hands-on exercise</strong>:</p><ol><li>Bring up Backstage locally: <code>npx @backstage/create-app</code>, run in dev mode.</li><li>Configure GitHub auth.</li><li>Import 1 repository as a Component (catalog-info.yaml).</li><li>Create 1 Scaffolder template that generates a repo + basic workflow.</li><li>Add the Kubernetes plugin to show pods from your kind cluster.</li><li>Add TechDocs (Markdown in the repo, rendered).</li><li>Bonus: install Crossplane on the cluster and create an XRD for <code>Database</code>; the Backstage scaffolder fires a claim.</li><li>Bonus 2: measure time-to-first-deploy with and without the template.</li></ol>'
                ),
            },
            "materials": [
                m("Backstage", "https://backstage.io/docs/overview/what-is-backstage", "docs", "", title_en='Backstage', description_en=''),
                m("Team Topologies", "https://teamtopologies.com/key-concepts", "article", "", title_en='Team Topologies', description_en=''),
                m("ThoughtWorks: IDPs", "https://www.thoughtworks.com/insights/articles/seismic-shift-in-platform-engineering", "article", "", title_en='ThoughtWorks: IDPs', description_en=''),
                m("Humanitec", "https://humanitec.com/platform-orchestrator", "docs", "", title_en='Humanitec', description_en=''),
                m("OSS Internal Dev Portal", "https://github.com/cnoe-io/idpbuilder", "tool", "", title_en='OSS Internal Dev Portal', description_en=''),
                m("Crossplane", "https://www.crossplane.io/", "tool", "Infra control plane K8s-native.", title_en='Crossplane', description_en='K8s-native infra control plane.'),
            ],
            "questions": [
                q("IDP é:",
                  "Plataforma interna que abstrai infra para o dev.",
                  ["Só um modal de interface para rodar lint.", "Só uma ferramenta de gestão de identidade e acesso.", "Só um framework de frontend para construir telas."],
                  "Não substitui infra; padroniza e expõe via UX/APIs amigáveis.",
                  statement_en='An IDP is:',
                  correct_en='An internal platform that abstracts infra for the developer.',
                  wrong_en=['Just a UI modal for running a linter, a common shortcut that looks fine until production surprises you.', 'A complete replacement for any cloud provider, which tends to fail quietly until someone audits the setup.', 'A type of relational database for microservices, an assumption that rarely survives the first real incident review.'],
                  explanation_en="It doesn't replace infra; it standardizes and exposes it via friendly UX/APIs."),
                q("Golden path significa:",
                  "Caminho recomendado e padronizado para criar/operar serviços.",
                  ["Um endpoint específico dentro do serviço de IAM, prática que só aparece como erro grave durante um incidente real.", "Só o logo dourado usado na marca da plataforma, decisão que parece segura até o primeiro teste de penetração real.", "Um tipo específico de configuração de TLS de rede, suposição incorreta sobre como o sistema realmente se comporta sob estresse."],
                  "Dev pode sair do golden path com justificativa, mas tem que arcar com manutenção própria.",
                  statement_en='Golden path means:',
                  correct_en='A recommended, standardized path to create/operate services.',
                  wrong_en=['A specific endpoint inside the IAM service, a practice that creates a false sense of security on the team.', 'A Kubernetes network protocol exclusive to CNCF.', 'An encryption algorithm used in TLS connections.'],
                  explanation_en='A developer can leave the golden path with justification, but then owns the maintenance.'),
                q("Backstage é:",
                  "Portal de devs OSS feito pelo Spotify.",
                  ["Um pipeline de CI mantido internamente pelo Spotify.", "Uma IDE proprietária vendida como produto fechado.", "Um servidor de DNS interno usado pela plataforma."],
                  "Adotado por Spotify, Netflix, American Airlines, etc. Hospedado pela CNCF.",
                  statement_en='Backstage is:',
                  correct_en='An OSS developer portal built by Spotify.',
                  wrong_en=['A CI pipeline maintained internally by Spotify.', 'A container registry exclusive to the CNCF.', 'A programming language created by Spotify.'],
                  explanation_en='Adopted by Spotify, Netflix, American Airlines, etc. Hosted by the CNCF.'),
                q("IDP visa:",
                  "Reduzir o custo cognitivo da operação.",
                  ["Centralizar o storage usado por vários times.", "Aumentar a burocracia envolvida em cada deploy.", "Reduzir a quantidade de testes exigida no pipeline."],
                  "Dev foca em código de negócio; plataforma cuida do resto.",
                  statement_en='An IDP aims to:',
                  correct_en='Reduce the cognitive cost of operations.',
                  wrong_en=['Centralize the storage used by multiple teams.', 'Eliminate the need for any automated testing.', 'Replace the application source code entirely.'],
                  explanation_en='Developers focus on business code; the platform handles the rest.'),
                q("Self-service em IDP:",
                  "Permite dev provisionar recursos sem ticket.",
                  ["Acaba com a necessidade de rodar qualquer teste.", "Aumenta a dependência do time de SRE em cada request.", "Substitui a necessidade de configurar RBAC no cluster."],
                  "Com guard-rails (Policy as Code), risco fica baixo. Sem guard-rails, vira faroeste.",
                  statement_en='Self-service in an IDP:',
                  correct_en='Lets developers provision resources without a ticket.',
                  wrong_en=['Removes the need to run any tests, a common shortcut that looks fine until production surprises you.', 'Automatically deletes unused microservices, which tends to fail quietly until someone audits the setup.', 'Replaces the need to configure RBAC, an assumption that rarely survives the first real incident review.'],
                  explanation_en='With guardrails (Policy as Code), risk stays low. Without guardrails, it becomes a free-for-all.'),
                q("Templates em IDP:",
                  "Bootstrap padronizado de serviços.",
                  ["Reduzem a qualidade final do serviço entregue.", "Substituem a etapa de build feita no pipeline de CI.", "Apagam as configurações de segurança do serviço."],
                  "Garantem que cada novo serviço sai com Dockerfile, CI, monitoring, segurança alinhados.",
                  statement_en='Templates in an IDP:',
                  correct_en='Standardized bootstrapping of services.',
                  wrong_en=['Reduce the final quality of the delivered service.', 'Only work for applications written in Java.', 'Replace the need for any kind of documentation.'],
                  explanation_en='They ensure every new service ships with a Dockerfile, CI, monitoring, and security already wired in.'),
                q("Catálogo de serviços:",
                  "Inventário com dono, deps, dashboards.",
                  ["Um substituto direto e completo do próprio Git.", "Um pipeline de CI/CD mantido pela plataforma.", "Um disco compartilhado montado em vários serviços."],
                  "Em incidente: 'quem é dono desse microsserviço?' resolve em 1 clique.",
                  statement_en='A service catalog:',
                  correct_en='An inventory with owner, deps, dashboards.',
                  wrong_en=['A direct, complete replacement for Git itself.', 'An automatic backup of the production database.', 'A type of TLS certificate for internal APIs.'],
                  explanation_en="In an incident: 'who owns this microservice?' resolved in one click."),
                q("IDP X K8s diretamente:",
                  "IDP esconde a complexidade do K8s atrás de UX.",
                  ["O Kubernetes substitui por completo qualquer IDP.", "São exatamente a mesma coisa, sem diferença real.", "Não têm alguma relação prática entre si."],
                  "Dev raramente edita YAML de K8s direto; preenche form e plataforma gera tudo.",
                  statement_en='IDP vs talking to K8s directly:',
                  correct_en='An IDP hides K8s complexity behind UX.',
                  wrong_en=['Kubernetes completely replaces any IDP.', 'An IDP only works without Kubernetes.', "There's no real relationship between the two."],
                  explanation_en='Developers rarely edit K8s YAML directly; they fill a form and the platform generates everything.'),
                q("Métrica de sucesso de IDP:",
                  "Time-to-production de novos serviços.",
                  ["O número de linhas escritas em cada chart Helm.", "O número total de tickets abertos no mês.", "O tamanho do time de SRE responsável pela plataforma."],
                  "Mede impacto real. Combine com DORA e NPS dos devs.",
                  statement_en='An IDP success metric:',
                  correct_en='Time-to-production for new services.',
                  wrong_en=['The number of lines written in each Helm chart.', 'The color scheme used in the portal UI.', 'The number of Kubernetes nodes in the cluster.'],
                  explanation_en='Measures real impact. Combine with DORA and developer NPS.'),
                q("Time topology recomendada:",
                  "Stream-aligned + Platform team + Enabling team.",
                  ["Só um time dedicado exclusivamente à segurança.", "Só um time dedicado exclusivamente ao SRE.", "Só os desenvolvedores organizados sem algum outro time."],
                  "Plataforma como produto requer roles claros e ownership de longo prazo.",
                  statement_en='Recommended team topology:',
                  correct_en='Stream-aligned + Platform team + Enabling team.',
                  wrong_en=['Only a team dedicated exclusively to security.', 'A single team responsible for everything with no specialization.', 'Only outsourced teams with no internal ownership.'],
                  explanation_en='Platform-as-product requires clear roles and long-term ownership.'),
            ],
        },
        # =====================================================================
        # 4.7 Policy as Code
        # =====================================================================
        {
            "title": "Policy as Code (PaC)",
            "title_en": 'Policy as Code (PaC)',
            "summary": "Definir regras (ex.: 'nenhum servidor pode ser público') via código.",
            "summary_en": "Define rules (e.g. 'no server may be public') via code.",
            "lesson": {
                "intro": (
                    "Compliance em PowerPoint não evita acidente. Política em Confluence "
                    "também não, alguém esquece, alguém sai da empresa, alguém clica "
                    "errado. Em código, política vira <em>guard-rail automático</em>: "
                    "PR que viola é rejeitado em segundos; pod sem securityContext não "
                    "sobe; bucket público nem é criado. Esta aula cobre Policy as Code "
                    "com OPA/Rego, Kyverno (K8s-native), Conftest (CI), Sentinel "
                    "(Terraform Cloud) e Cloud Custodian (cloud), com casos reais e "
                    "padrões de adoção (warn → enforce) que evitam revolta do time."
                ),
                "intro_en": (
                    "Compliance in PowerPoint doesn't prevent accidents. A policy in "
                    "Confluence doesn't either — someone forgets, someone leaves the "
                    'company, someone clicks the wrong thing. In code, policy becomes an '
                    '<em>automatic guardrail</em>: a PR that violates it is rejected in '
                    "seconds; a pod without a securityContext doesn't start; a public "
                    "bucket isn't even created. This lesson covers Policy as Code with "
                    'OPA/Rego, Kyverno (K8s-native), Conftest (CI), Sentinel (Terraform '
                    'Cloud) and Cloud Custodian (cloud), with real cases and adoption '
                    'patterns (warn → enforce) that avoid a team revolt.'
                ),
                "body": (
                """<h3>1. Política como código: a mesma regra, aplicada em cinco pontos diferentes do ciclo</h3>
<p>Regra de negócio, segurança ou compliance escrita numa linguagem
VERSIONADA (Rego, YAML) muda de natureza: passa a ser revisável em PR
como qualquer código, testável com testes unitários, e — o ganho central
— APLICADA AUTOMATICAMENTE em vários pontos do ciclo de vida, em vez de
depender de alguém lembrar de checar manualmente. No editor, um plugin de
IDE já sinaliza violação enquanto o código é escrito. No pre-commit, um
hook local roda Conftest antes do commit existir. No CI, a mesma
política bloqueia o merge de um PR que viole a regra. No admission
controller do Kubernetes, a criação de um recurso não-conforme é
rejeitada antes de chegar ao etcd. Na conta de nuvem, SCPs (AWS), Azure
Policy ou GCP Org Policy aplicam a regra TRANSVERSALMENTE, mesmo para
quem tenta contornar o CI. E em runtime, políticas de autorização
controlam o que uma API aceita processar. O valor de aplicar a MESMA
regra em várias camadas não é redundância por redundância — é defesa em
profundidade: se uma camada falhar ou for contornada, a próxima ainda
pega.</p>
<div class="mermaid">
flowchart LR
    Ide["IDE / pre-commit"] --> Ci["CI / Conftest"]
    Ci --> Admit["Admission no cluster"]
    Admit --> Runtime["Runtime / Custodian"]
    Runtime --> Org["SCP / Org Policy"]
</div>


<h3>2. OPA e Rego: uma engine genérica, uma linguagem que pensa em conjuntos</h3>
<p>Open Policy Agent (projeto CNCF graduado) é uma engine de política de
propósito geral — não amarrada a Kubernetes especificamente, capaz de
avaliar qualquer entrada estruturada contra regras declaradas em Rego,
uma linguagem baseada em Datalog. A curva de aprendizado inicial de Rego
é real (a sintaxe declarativa confunde quem só programou
imperativamente antes), mas se paga rápido pela expressividade:</p>
<pre><code>package terraform.s3   # namespace

import future.keywords

# Inputs vêm de fora (terraform plan json)
deny[msg] {
  resource := input.resource.aws_s3_bucket[name]
  resource.acl == "public-read"
  msg := sprintf("Bucket %v não pode ser public-read", [name])
}

deny[msg] {
  resource := input.resource.aws_security_group[name]
  rule := resource.ingress[_]
  rule.cidr_blocks[_] == "0.0.0.0/0"
  rule.from_port == 22
  msg := sprintf("SG %v não pode ter SSH aberto ao mundo", [name])
}

warn[msg] {
  resource := input.resource.aws_db_instance[name]
  not resource.storage_encrypted
  msg := sprintf("RDS %v deveria ter encryption", [name])
}</code></pre>
<p>Rego é fundamentalmente baseado em CONJUNTOS: uma query não retorna
"sim/não", retorna o CONJUNTO de todos os valores que satisfazem as
condições declaradas — <code>deny[msg]</code> coleta TODAS as mensagens
de violação encontradas, não só a primeira. O underscore
(<code>_</code>) funciona como coringa, casando qualquer elemento de uma
coleção sem precisar nomeá-lo individualmente. Essa forma de pensar
("declare o que CONSTITUI uma violação, deixe o motor encontrar todas as
ocorrências") é o que torna Rego poderoso para políticas complexas, mas
também o que exige uma virada de chave mental de quem vem de linguagem
imperativa tradicional.</p>

<h3>3. Conftest: a mesma engine OPA, aplicada fora do Kubernetes</h3>
<p>Conftest roda OPA contra QUALQUER arquivo de configuração estruturado
— plano do Terraform, manifesto Kubernetes, Dockerfile, JSON, YAML,
INI — sem exigir um cluster ou admission controller no meio:</p>
<pre><code># CI: validar Terraform plan
$ terraform show -json tfplan &gt; plan.json
$ conftest test plan.json --policy ./policies
FAIL - plan.json - Bucket app-data não pode ser public-read
FAIL - plan.json - SG web não pode ter SSH aberto ao mundo
WARN - plan.json - RDS db-prod deveria ter encryption

$ echo $?
1   # exit code falha o build</code></pre>
<p>Rodar a checagem contra o PLANO do Terraform (não contra o código-fonte
diretamente) é o detalhe que faz essa validação valer: o plano representa
o que de fato vai mudar na infraestrutura real, incluindo valores
computados e dependências resolvidas — checar o `.tf` bruto perderia
justamente os casos onde uma variável ou módulo produz um resultado
perigoso só visível depois do plan.</p>

<h3>4. Kyverno: a mesma proteção, sem exigir que o time aprenda Rego</h3>
<p>Para Kubernetes especificamente, Kyverno reduz a barreira de entrada
escrevendo políticas em YAML puro — a mesma sintaxe de qualquer outro
manifesto do cluster, sem exigir aprender uma linguagem nova:</p>
<pre><code>apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-non-root }
spec:
  validationFailureAction: Enforce
  background: true   # também aplica em recursos existentes (audit)
  rules:
    - name: check-runAsNonRoot
      match:
        any:
          - resources: { kinds: [Pod], namespaces: ['prod-*'] }
      validate:
        message: "Containers em prod-* devem rodar como non-root."
        pattern:
          spec:
            =(securityContext):
              =(runAsNonRoot): true
            containers:
              - =(securityContext):
                  =(runAsNonRoot): true
    - name: drop-all-capabilities
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        pattern:
          spec:
            containers:
              - securityContext:
                  capabilities:
                    drop: ["ALL"]</code></pre>
<p><code>background: true</code> estende a política para AVALIAR recursos
JÁ EXISTENTES no cluster (em modo audit), não só os que chegarem daqui
em diante — essencial para descobrir violações pré-existentes antes de
promover a política para bloqueio ativo. Além de validar, Kyverno também
suporta MUTAR (injetar um <code>securityContext</code> padrão em pods que
não declararam nenhum), GERAR (criar automaticamente um Secret ou
ConfigMap em todo namespace novo), VERIFICAR ASSINATURA de imagem (via
Cosign) e LIMPAR recursos órfãos — um conjunto de capacidades bem mais
amplo que "só validar sim ou não".</p>

<h3>5. OPA Gatekeeper: a mesma expressividade do Rego, empacotada como admission controller</h3>
<p>Gatekeeper traz OPA/Rego para o Kubernetes através de dois objetos
complementares: <code>ConstraintTemplate</code> define a REGRA (em Rego),
e <code>Constraint</code> INSTANCIA essa regra com parâmetros
específicos — a mesma separação vista na aula de Admission Controllers,
permitindo reusar a mesma lógica com parâmetros diferentes por
instância:</p>
<div class="mermaid">
flowchart LR
    CT["ConstraintTemplate em Rego"] --> C["Constraint com parâmetros"]
    C --> Adm["Admission Gatekeeper"]
    Adm -- "viola" --> Deny["Rejeita"]
    Adm -- "ok" --> Allow["Cria recurso"]
</div>

<pre><code># Template (Rego)
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata: { name: k8srequiredlabels }
spec:
  crd:
    spec:
      names: { kind: K8sRequiredLabels }
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          missing := input.parameters.labels - \\
                     {label | input.review.object.metadata.labels[label]}
          count(missing) &gt; 0
          msg := sprintf("Labels obrigatórios faltando: %v", [missing])
        }

# Constraint (uso)
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata: { name: ns-must-have-owner }
spec:
  match: { kinds: [{ kinds: [Namespace] }] }
  parameters: { labels: ["owner", "environment"] }</code></pre>

<h3>6. Sentinel: a escolha natural para quem já vive dentro do ecossistema HashiCorp</h3>
<p>Sentinel é uma DSL própria da HashiCorp, integrada nativamente a
Terraform Cloud, Vault, Consul e Nomad — a vantagem real aparece quando
o time já usa várias dessas ferramentas e prefere uma linguagem de
política única atravessando todas elas, em vez de manter Rego para uma
coisa e outra sintaxe para outra:</p>
<pre><code># sentinel.hcl
policy "require-encryption" {
  source = "./require-encryption.sentinel"
  enforcement_level = "hard-mandatory"
}

# require-encryption.sentinel
import "tfplan/v2" as tfplan

main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type is "aws_s3_bucket" implies
      rc.change.after.server_side_encryption_configuration is not null
  }
}</code></pre>
<p><code>enforcement_level = "hard-mandatory"</code> é o equivalente
Sentinel de "enforce" — diferente de níveis mais brandos que só avisam,
essa configuração bloqueia o apply de fato quando a política falha.</p>

<h3>7. Cloud Custodian: política e remediação de infraestrutura já provisionada</h3>
<p>Diferente das ferramentas anteriores, que atuam ANTES do recurso
existir (CI, admission), Cloud Custodian audita e AGE sobre recursos JÁ
EXISTENTES na nuvem, combinando filtro e ação numa política declarativa:</p>
<pre><code># custodian.yaml
policies:
  - name: stop-untagged-ec2
    resource: aws.ec2
    filters:
      - 'tag:Owner': absent
      - State.Name: running
    actions:
      - type: notify
        to: [security@empresa.com]
      - stop

  - name: encrypt-s3-buckets
    resource: aws.s3
    filters:
      - type: bucket-encryption
        state: false
    actions:
      - type: set-bucket-encryption</code></pre>
<p>A primeira política não só DETECTA uma instância EC2 sem a tag
<code>Owner</code> obrigatória — ela NOTIFICA o time de segurança e PARA
a instância automaticamente, uma remediação ativa, não só um relatório
passivo de conformidade.</p>

<h3>8. SCPs e Org Policies: a regra que ninguém consegue contornar, nem por acidente</h3>
<p>Para regras que precisam valer para a EMPRESA INTEIRA, independente
de qual pipeline ou ferramenta alguém use, a resposta vive na camada de
conta de nuvem, não em CI. AWS SCP (Service Control Policy) aplicado
numa Organizational Unit inteira restringe o que QUALQUER IAM role
consegue fazer, mesmo com permissão administrativa total — "ninguém pode
criar bucket sem TLS" vale mesmo para quem tem acesso root na conta.
Azure Policy oferece efeitos deny/audit/append sobre recursos, agrupados
em "Policy Initiatives" para aplicar um conjunto coeso de uma vez. GCP
Org Policy aplica constraints no nível de organização ou pasta. E o
padrão recomendado é versionar essas políticas como infraestrutura,
exatamente como qualquer outro recurso Terraform:</p>
<pre><code>resource "aws_organizations_policy" "deny-public-buckets" {
  name = "deny-public-buckets"
  type = "SERVICE_CONTROL_POLICY"
  content = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Deny"
      Action = ["s3:PutBucketAcl"]
      Resource = "*"
      Condition = {
        "StringEquals" = { "s3:x-amz-acl" = ["public-read", "public-read-write"] }
      }
    }]
  })
}</code></pre>

<h3>9. Adoção: por que "enforce no dia 1" é a forma mais confiável de matar o programa inteiro</h3>
<p>O erro mais citado em Policy as Code é ativar bloqueio total em
produção logo no primeiro dia — o resultado quase garantido é metade dos
times travados sem aviso prévio, revolta imediata, e a política sendo
desligada permanentemente na primeira crise. A progressão que de fato
funciona tem cinco estágios: primeiro <strong>audit only</strong>, onde
a política apenas REPORTA violações sem bloquear nada, mapeando o
tamanho real do problema antes de qualquer ação. Depois
<strong>warn em PR</strong>, bloqueando só PRs NOVOS (não o que já
existe), dando tempo para os times aprenderem a regra organicamente.
Em seguida <strong>enforce em ambientes de baixo risco</strong>
(dev, staging), validando o comportamento antes de tocar produção.
Só então <strong>enforce em produção</strong>, depois de meses limpando
violações conhecidas. E ao longo de todo o processo,
<strong>documentar exceções</strong> explicitamente (via label de
recurso ou lista de namespaces isentos), com auditoria periódica dessas
exceções — sem isso, a lista de "casos especiais" cresce
silenciosamente até a política perder sentido.</p>

<h3>10. Testar política como qualquer outro código, porque ela tem bug como qualquer outro código</h3>
<pre><code># OPA testing
test_deny_public_bucket {
  result := deny with input as {
    "resource": {
      "aws_s3_bucket": {
        "data": {"acl": "public-read"}
      }
    }
  }
  count(result) == 1
}

$ opa test policies/ -v
PASS: 5/5</code></pre>
<p>Uma política sem teste unitário corre o mesmo risco de qualquer código
sem teste: um ajuste aparentemente inocente numa regra pode, sem
ninguém perceber até o incidente acontecer, passar a bloquear TUDO (um
falso positivo geral) ou parar de bloquear NADA (a política vira
decorativa) — e como a política roda automaticamente em produção, o
raio de impacto de um bug ali costuma ser maior que um bug de aplicação
comum.</p>

<h3>11. Sete anti-padrões que decidem se o programa de Policy as Code sobrevive</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Mata o programa</strong><p>Enforce no dia 1, sem testes, exceções eternas.</p></div>
    <div class="lesson-viz-card"><strong>Faz sobreviver</strong><p>Audit primeiro, teste como código, exceções com prazo.</p></div>
  </div>
  <figcaption>Adoção de Policy as Code: cultura antes de bloqueio duro.</figcaption>
</figure>

<ul>
<li><strong>Enforce logo no dia 1 em produção</strong>: revolta
praticamente garantida, e a política acaba desligada de vez (seção 9).</li>
<li><strong>Sem teste de política</strong>: um bug bloqueia tudo um dia,
sem aviso.</li>
<li><strong>Mensagem de erro genérica</strong>: o desenvolvedor vê
"denied" sem entender o que corrigir — sempre inclua explicação ou link
para o runbook relevante.</li>
<li><strong>Política sem dono definido</strong>: com o tempo, vira lixo
que ninguém mais entende nem sabe se ainda faz sentido manter.</li>
<li><strong>Sem mecanismo de exceção legítimo</strong>: casos especiais
reais (que existem em qualquer organização) acabam burlando a política
por fora, em vez de serem documentados dentro dela.</li>
<li><strong>Mil políticas simultâneas desde o início</strong>: foque nas
dez que realmente importam primeiro — cobertura ampla e rasa vale menos
que cobertura estreita e bem mantida.</li>
<li><strong>Política só em CI, nunca no admission controller</strong>:
alguém aplica um manifesto diretamente no cluster, contornando o CI, e o
drift cresce silenciosamente — a defesa em camadas da seção 1 existe
exatamente para esse cenário.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. Policy as code: the same rule, applied at five different points in the cycle</h3>
<p>A business, security, or compliance rule written in a VERSIONED
language (Rego, YAML) changes nature: it becomes reviewable in a PR
like any code, testable with unit tests, and — the central gain —
APPLIED AUTOMATICALLY at several points in the lifecycle, instead of
depending on someone remembering to check manually. In the editor, an IDE
plugin already flags violations while the code is being written. In
pre-commit, a local hook runs Conftest before the commit even exists. In
CI, the same policy blocks merging a PR that violates the rule. In the
Kubernetes admission controller, creating a non-compliant resource is
rejected before it reaches etcd. On the cloud account, SCPs (AWS), Azure
Policy, or GCP Org Policy apply the rule CROSS-CUTTINGLY, even for
anyone trying to bypass CI. And at runtime, authorization policies
control what an API accepts to process. The value of applying the SAME
rule across several layers is not redundancy for redundancy's sake — it
is defense in depth: if one layer fails or is bypassed, the next still
catches it.</p>
<div class="mermaid">
flowchart LR
    Ide["IDE / pre-commit"] --> Ci["CI / Conftest"]
    Ci --> Admit["Cluster admission"]
    Admit --> Runtime["Runtime / Custodian"]
    Runtime --> Org["SCP / Org Policy"]
</div>


<h3>2. OPA and Rego: a generic engine, a language that thinks in sets</h3>
<p>Open Policy Agent (a graduated CNCF project) is a general-purpose
policy engine — not tied to Kubernetes specifically, able to evaluate
any structured input against rules declared in Rego, a Datalog-based
language. Rego's initial learning curve is real (the declarative syntax
confuses people who have only programmed imperatively before), but it
pays off quickly through expressiveness:</p>
<pre><code>package terraform.s3   # namespace

import future.keywords

# Inputs vêm de fora (terraform plan json)
deny[msg] {
  resource := input.resource.aws_s3_bucket[name]
  resource.acl == "public-read"
  msg := sprintf("Bucket %v não pode ser public-read", [name])
}

deny[msg] {
  resource := input.resource.aws_security_group[name]
  rule := resource.ingress[_]
  rule.cidr_blocks[_] == "0.0.0.0/0"
  rule.from_port == 22
  msg := sprintf("SG %v não pode ter SSH aberto ao mundo", [name])
}

warn[msg] {
  resource := input.resource.aws_db_instance[name]
  not resource.storage_encrypted
  msg := sprintf("RDS %v deveria ter encryption", [name])
}</code></pre>
<p>Rego is fundamentally based on SETS: a query does not return
"yes/no", it returns the SET of all values that satisfy the declared
conditions — <code>deny[msg]</code> collects ALL violation messages
found, not just the first. The underscore (<code>_</code>) works as a
wildcard, matching any element of a collection without needing to name
it individually. That way of thinking ("declare what CONSTITUTES a
violation, let the engine find every occurrence") is what makes Rego
powerful for complex policies, but also what requires a mental shift for
anyone coming from a traditional imperative language.</p>

<h3>3. Conftest: the same OPA engine, applied outside Kubernetes</h3>
<p>Conftest runs OPA against ANY structured configuration file —
Terraform plan, Kubernetes manifest, Dockerfile, JSON, YAML,
INI — without requiring a cluster or admission controller in between:</p>
<pre><code># CI: validar Terraform plan
$ terraform show -json tfplan &gt; plan.json
$ conftest test plan.json --policy ./policies
FAIL - plan.json - Bucket app-data não pode ser public-read
FAIL - plan.json - SG web não pode ter SSH aberto ao mundo
WARN - plan.json - RDS db-prod deveria ter encryption

$ echo $?
1   # exit code falha o build</code></pre>
<p>Running the check against the Terraform PLAN (not against the source
code directly) is the detail that makes this validation worthwhile: the
plan represents what will actually change in real infrastructure,
including computed values and resolved dependencies — checking raw
<code>.tf</code> would miss exactly the cases where a variable or module
produces a dangerous result only visible after the plan.</p>

<h3>4. Kyverno: the same protection, without requiring the team to learn Rego</h3>
<p>For Kubernetes specifically, Kyverno lowers the entry barrier by
writing policies in pure YAML — the same syntax as any other cluster
manifest, without requiring learning a new language:</p>
<pre><code>apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-non-root }
spec:
  validationFailureAction: Enforce
  background: true   # também aplica em recursos existentes (audit)
  rules:
    - name: check-runAsNonRoot
      match:
        any:
          - resources: { kinds: [Pod], namespaces: ['prod-*'] }
      validate:
        message: "Containers em prod-* devem rodar como non-root."
        pattern:
          spec:
            =(securityContext):
              =(runAsNonRoot): true
            containers:
              - =(securityContext):
                  =(runAsNonRoot): true
    - name: drop-all-capabilities
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        pattern:
          spec:
            containers:
              - securityContext:
                  capabilities:
                    drop: ["ALL"]</code></pre>
<p><code>background: true</code> extends the policy to EVALUATE
ALREADY EXISTING resources in the cluster (in audit mode), not only ones
that arrive from now on — essential for discovering pre-existing
violations before promoting the policy to active blocking. Beyond
validating, Kyverno also supports MUTATING (injecting a default
<code>securityContext</code> into pods that declared none), GENERATING
(automatically creating a Secret or ConfigMap in every new namespace),
VERIFYING image SIGNATURES (via Cosign), and CLEANING orphaned resources
— a much broader set of capabilities than "just validate yes or no".</p>

<h3>5. OPA Gatekeeper: the same Rego expressiveness, packaged as an admission controller</h3>
<p>Gatekeeper brings OPA/Rego into Kubernetes through two complementary
objects: <code>ConstraintTemplate</code> defines the RULE (in Rego),
and <code>Constraint</code> INSTANTIATES that rule with specific
parameters — the same separation seen in the Admission Controllers
lesson, allowing reuse of the same logic with different parameters per
instance:</p>
<div class="mermaid">
flowchart LR
    CT["ConstraintTemplate in Rego"] --> C["Constraint with parameters"]
    C --> Adm["Gatekeeper admission"]
    Adm -- "violates" --> Deny["Reject"]
    Adm -- "ok" --> Allow["Create resource"]
</div>

<pre><code># Template (Rego)
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata: { name: k8srequiredlabels }
spec:
  crd:
    spec:
      names: { kind: K8sRequiredLabels }
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          missing := input.parameters.labels - \\
                     {label | input.review.object.metadata.labels[label]}
          count(missing) &gt; 0
          msg := sprintf("Labels obrigatórios faltando: %v", [missing])
        }

# Constraint (uso)
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata: { name: ns-must-have-owner }
spec:
  match: { kinds: [{ kinds: [Namespace] }] }
  parameters: { labels: ["owner", "environment"] }</code></pre>

<h3>6. Sentinel: the natural choice for anyone already living in the HashiCorp ecosystem</h3>
<p>Sentinel is HashiCorp's own DSL, natively integrated with Terraform
Cloud, Vault, Consul, and Nomad — the real advantage appears when the
team already uses several of those tools and prefers a single policy
language across all of them, instead of keeping Rego for one thing and
another syntax for another:</p>
<pre><code># sentinel.hcl
policy "require-encryption" {
  source = "./require-encryption.sentinel"
  enforcement_level = "hard-mandatory"
}

# require-encryption.sentinel
import "tfplan/v2" as tfplan

main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type is "aws_s3_bucket" implies
      rc.change.after.server_side_encryption_configuration is not null
  }
}</code></pre>
<p><code>enforcement_level = "hard-mandatory"</code> is Sentinel's
equivalent of "enforce" — unlike softer levels that only warn, this
configuration actually blocks the apply when the policy fails.</p>

<h3>7. Cloud Custodian: policy and remediation for already-provisioned infrastructure</h3>
<p>Unlike the previous tools, which act BEFORE the resource exists
(CI, admission), Cloud Custodian audits and ACTS on ALREADY EXISTING
cloud resources, combining filter and action in a declarative policy:</p>
<pre><code># custodian.yaml
policies:
  - name: stop-untagged-ec2
    resource: aws.ec2
    filters:
      - 'tag:Owner': absent
      - State.Name: running
    actions:
      - type: notify
        to: [security@empresa.com]
      - stop

  - name: encrypt-s3-buckets
    resource: aws.s3
    filters:
      - type: bucket-encryption
        state: false
    actions:
      - type: set-bucket-encryption</code></pre>
<p>The first policy not only DETECTS an EC2 instance without the
mandatory <code>Owner</code> tag — it NOTIFIES the security team and
STOPS the instance automatically, active remediation, not just a passive
compliance report.</p>

<h3>8. SCPs and Org Policies: the rule nobody can bypass, even by accident</h3>
<p>For rules that must apply to the ENTIRE COMPANY, regardless of which
pipeline or tool someone uses, the answer lives at the cloud-account
layer, not in CI. An AWS SCP (Service Control Policy) applied to an
entire Organizational Unit restricts what ANY IAM role can do, even with
full administrative permission — "nobody can create a bucket without TLS"
holds even for someone with root access on the account. Azure Policy
offers deny/audit/append effects on resources, grouped into "Policy
Initiatives" to apply a cohesive set at once. GCP Org Policy applies
constraints at the organization or folder level. And the recommended
pattern is to version those policies as infrastructure, exactly like any
other Terraform resource:</p>
<pre><code>resource "aws_organizations_policy" "deny-public-buckets" {
  name = "deny-public-buckets"
  type = "SERVICE_CONTROL_POLICY"
  content = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Deny"
      Action = ["s3:PutBucketAcl"]
      Resource = "*"
      Condition = {
        "StringEquals" = { "s3:x-amz-acl" = ["public-read", "public-read-write"] }
      }
    }]
  })
}</code></pre>

<h3>9. Adoption: why "enforce on day 1" is the most reliable way to kill the whole program</h3>
<p>The most cited mistake in Policy as Code is enabling full blocking in
production on day one — the almost guaranteed result is half the teams
stuck without prior notice, immediate revolt, and the policy being
permanently turned off at the first crisis. The progression that actually
works has five stages: first <strong>audit only</strong>, where the
policy only REPORTS violations without blocking anything, mapping the
real size of the problem before any action. Then <strong>warn on
PR</strong>, blocking only NEW PRs (not what already exists), giving
teams time to learn the rule organically. Next <strong>enforce in
low-risk environments</strong> (dev, staging), validating behavior before
touching production. Only then <strong>enforce in production</strong>,
after months cleaning known violations. And throughout the process,
<strong>document exceptions</strong> explicitly (via a resource label or
list of exempt namespaces), with periodic audit of those exceptions —
without that, the list of "special cases" grows silently until the
policy loses meaning.</p>

<h3>10. Test policy like any other code, because it has bugs like any other code</h3>
<pre><code># OPA testing
test_deny_public_bucket {
  result := deny with input as {
    "resource": {
      "aws_s3_bucket": {
        "data": {"acl": "public-read"}
      }
    }
  }
  count(result) == 1
}

$ opa test policies/ -v
PASS: 5/5</code></pre>
<p>A policy without a unit test runs the same risk as any untested code:
an apparently innocent tweak to a rule can, without anyone noticing until
the incident happens, start blocking EVERYTHING (a general false
positive) or stop blocking NOTHING (the policy becomes decorative) — and
because the policy runs automatically in production, the blast radius of
a bug there is usually larger than a common application bug.</p>

<h3>11. Seven anti-patterns that decide whether a Policy as Code program survives</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Kills the program</strong><p>Day-1 enforce, no tests, endless exceptions.</p></div>
    <div class="lesson-viz-card"><strong>Makes it survive</strong><p>Audit first, test like code, time-boxed exceptions.</p></div>
  </div>
  <figcaption>Policy as Code adoption: culture before hard blocking.</figcaption>
</figure>

<ul>
<li><strong>Enforce on day 1 in production</strong>: revolt is
practically guaranteed, and the policy ends up permanently disabled
(section 9).</li>
<li><strong>No policy tests</strong>: a bug blocks everything one day,
with no warning.</li>
<li><strong>Generic error message</strong>: the developer sees
"denied" without understanding what to fix — always include an
explanation or link to the relevant runbook.</li>
<li><strong>Policy with no defined owner</strong>: over time it becomes
junk nobody understands or knows whether it's still worth keeping.</li>
<li><strong>No legitimate exception mechanism</strong>: real special
cases (which exist in any organization) end up bypassing the policy
from outside, instead of being documented inside it.</li>
<li><strong>A thousand simultaneous policies from the start</strong>:
focus on the ten that really matter first — broad shallow coverage is
worth less than narrow, well-maintained coverage.</li>
<li><strong>Policy only in CI, never in the admission controller</strong>:
someone applies a manifest directly to the cluster, bypassing CI, and
drift grows silently — the defense in depth from section 1 exists
exactly for that scenario.</li>
</ul>"""
                ),
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Escreva policy OPA Rego que rejeita: bucket S3 público; SG "
                    "com SSH 0.0.0.0/0; RDS sem encryption.</li>"
                    "<li>Teste com <code>opa test</code> (3-5 unit tests).</li>"
                    "<li>Configure Conftest no GitHub Actions: <code>terraform plan "
                    "-out=tfplan && terraform show -json tfplan | conftest test -</code>.</li>"
                    "<li>Em K8s local (kind), instale Kyverno; crie ClusterPolicy "
                    "exigindo runAsNonRoot e cap drop ALL.</li>"
                    "<li>Tente subir Pod violando, veja rejeição.</li>"
                    "<li>Crie ClusterPolicy de mutate que injeta securityContext "
                    "padrão se não tiver.</li>"
                    "<li>Bonus: AWS SCP que bloqueia criação de bucket sem TLS via "
                    "Terraform.</li>"
                    "<li>Bonus 2: Cloud Custodian rule que para EC2 sem tag Owner.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    '<p><strong>Complete hands-on exercise</strong>:</p><ol><li>Write an OPA Rego policy that rejects: a public S3 bucket; an SG with SSH 0.0.0.0/0; RDS without encryption.</li><li>Test with <code>opa test</code> (3–5 unit tests).</li><li>Configure Conftest in GitHub Actions: <code>terraform plan -out=tfplan && terraform show -json tfplan | conftest test -</code>.</li><li>On local K8s (kind), install Kyverno; create a ClusterPolicy requiring runAsNonRoot and cap drop ALL.</li><li>Try to start a violating Pod and see the rejection.</li><li>Create a mutating ClusterPolicy that injects a default securityContext if missing.</li><li>Bonus: an AWS SCP that blocks creating a bucket without TLS via Terraform.</li><li>Bonus 2: a Cloud Custodian rule that stops EC2 without an Owner tag.</li></ol>'
                ),
            },
            "materials": [
                m("Open Policy Agent", "https://www.openpolicyagent.org/docs/latest/", "docs", "", title_en='Open Policy Agent', description_en=''),
                m("Conftest", "https://www.conftest.dev/", "tool", "", title_en='Conftest', description_en=''),
                m("Kyverno", "https://kyverno.io/docs/", "tool", "", title_en='Kyverno', description_en=''),
                m("Sentinel (HashiCorp)", "https://developer.hashicorp.com/sentinel", "docs", "", title_en='Sentinel (HashiCorp)', description_en=''),
                m("OPA Gatekeeper", "https://open-policy-agent.github.io/gatekeeper/website/docs/", "docs", "", title_en='OPA Gatekeeper', description_en=''),
                m("Cloud Custodian", "https://cloudcustodian.io/", "tool", "", title_en='Cloud Custodian', description_en=''),
            ],
            "questions": [
                q("Policy as Code permite:",
                  "Versionar e revisar políticas como qualquer código.",
                  ["Reduzir a quantidade de testes exigida no pipeline.", "Substituir por completo a etapa de CI do pipeline.", "Apagar as políticas de IAM configuradas na conta."],
                  "Auditoria fica simples: git log mostra quando regra mudou e quem aprovou.",
                  statement_en='Policy as Code lets you:',
                  correct_en='Version and review policies like any other code.',
                  wrong_en=['Reduce the number of tests required in the pipeline.', 'Automatically compile the application source code.', 'Replace the need for any kind of authentication.'],
                  explanation_en='Auditing becomes simple: git log shows when a rule changed and who approved it.'),
                q("OPA usa linguagem:",
                  "Rego.",
                  ["YAML puro.", "Bash.", "Java."],
                  "Rego é declarativa, parecida com Datalog. Curva inicial existe, mas paga rápido.",
                  statement_en='OPA uses the language:',
                  correct_en='Rego.',
                  wrong_en=['Pure YAML.', 'Only Python scripts.', 'Only JSON Schema.'],
                  explanation_en="Rego is declarative, similar to Datalog. There's an initial learning curve, but it pays off quickly."),
                q("Kyverno é específico para:",
                  "Kubernetes.",
                  ["Só funciona dentro de charts escritos em Helm.", "Funções serverless rodando como Cloud Functions.", "Só funciona dentro da nuvem da AWS."],
                  "Diferencial: políticas em YAML, sem precisar Rego. Boa entrada para times K8s.",
                  statement_en='Kyverno is specific to:',
                  correct_en='Kubernetes.',
                  wrong_en=['It only works inside charts written in Helm.', 'It only validates Terraform plans.', 'It only runs on the Windows operating system.'],
                  explanation_en='Differentiator: policies in YAML, no Rego needed. A good entry point for K8s teams.'),
                q("Admission controller:",
                  "Intercepta criação/update de recursos antes de persistir.",
                  ["Apaga clusters inteiros automaticamente sem aviso, prática que gera falso senso de segurança no time.", "Substitui a necessidade de usar Helm no deploy, prática que aumenta a superfície de ataque sem ninguém perceber.", "Reseta a configuração de DNS interna do cluster, decisão que ignora justamente o motivo pelo qual a prática recomendada existe."],
                  "Validating (rejeita) e mutating (modifica). Webhook chamado pelo apiserver.",
                  statement_en='An admission controller:',
                  correct_en='Intercepts create/update of resources before they persist.',
                  wrong_en=['Automatically deletes entire clusters without warning, a practice that creates a false sense of security on the team.', 'Replaces the need to configure RBAC in the cluster.', 'Only works for applications written in Go.'],
                  explanation_en='Validating (rejects) and mutating (modifies). Webhook called by the apiserver.'),
                q("Conftest serve para:",
                  "Validar arquivos de configuração com OPA fora do K8s.",
                  ["Substituir por completo o Terraform usado na infra, erro comum de quem aprendeu por tentativa e erro, sem revisar a documentação oficial.", "Mostrar os logs gerados durante o deploy do cluster, abordagem que funciona bem até o primeiro pico de carga real.", "Substituir por completo o uso do Docker no build, suposição que só vale em ambiente de desenvolvimento, não em produção."],
                  "Roda em CI: `conftest test plan.json` aplica políticas Rego.",
                  statement_en='Conftest is for:',
                  correct_en='Validating config files with OPA outside of K8s.',
                  wrong_en=['Completely replacing the Terraform used for infra, a common mistake for those who learned by trial and error.', 'Automatically compiling Docker images in CI.', 'Replacing the need for any container registry.'],
                  explanation_en='Runs in CI: `conftest test plan.json` applies Rego policies.'),
                q("Policy de 'nenhum bucket público':",
                  "Pode ser aplicada em CI (pre-merge) e cluster (admission).",
                  ["Só pode ser aplicada já em ambiente de produção, prática que gera falso senso de segurança no time.", "Só pode ser aplicada abrindo um ticket manual, que só aparece como problema depois que o sistema já está em produção.", "Não é tecnicamente possível aplicar esse tipo de regra, comportamento que só some quando alguém finalmente lê a documentação."],
                  "Defesa em camadas: PR bloqueia, mas se algo passar, admission impede no provisionamento.",
                  statement_en="A 'no public buckets' policy:",
                  correct_en='Can be applied in CI (pre-merge) and in the cluster (admission).',
                  wrong_en=['Can only be applied once already in production, a practice that creates a false sense of security on the team.', 'Only works for buckets created manually in the console.', 'Replaces the need for any encryption on the data.'],
                  explanation_en='Defense in depth: the PR blocks it, but if something slips through, admission stops it at provision time.'),
                q("Falha em policy deve:",
                  "Bloquear o merge/deploy ou marcar não-compliant.",
                  ["Aprovar o merge mesmo assim, sem restrição alguma.", "Ser ignorada por padrão em qualquer pipeline.", "Ser silenciada automaticamente pela ferramenta."],
                  "Em ambientes regulados, audit trail mostra exceção justificada.",
                  statement_en='A policy failure should:',
                  correct_en='Block the merge/deploy or mark it non-compliant.',
                  wrong_en=['Approve the merge anyway, with no restriction at all.', 'Automatically delete the entire repository.', 'Only send an email with no further action.'],
                  explanation_en='In regulated environments, the audit trail shows a justified exception.'),
                q("Fast feedback ao dev:",
                  "Rodar policy localmente via pre-commit.",
                  ["Só rodar a policy já em ambiente de produção.", "Substituir por completo a etapa de CI do pipeline.", "Só rodar a policy manualmente pelo console."],
                  "Conftest pre-commit ajuda dev a corrigir antes mesmo do PR.",
                  statement_en='Fast feedback to the developer:',
                  correct_en='Run the policy locally via pre-commit.',
                  wrong_en=['Only run the policy once already in production.', 'Send the policy result exclusively by postal mail.', 'Disable all policies during development.'],
                  explanation_en='Conftest as a pre-commit hook helps the developer fix issues even before the PR.'),
                q("Difference SAST vs PaC:",
                  "SAST código; PaC config/infra/cluster.",
                  ["São exatamente a mesma coisa, sem diferença real.", "SAST analisa só arquivos escritos em YAML.", "PaC analisa só código escrito em Java."],
                  "SAST olha código fonte; PaC olha configurações de infra/runtime.",
                  statement_en='Difference between SAST and PaC:',
                  correct_en='SAST is code; PaC is config/infra/cluster.',
                  wrong_en=['They are exactly the same thing, with no real difference.', 'SAST only analyzes infrastructure.', 'PaC only analyzes application source code.'],
                  explanation_en='SAST looks at source code; PaC looks at infra/runtime configuration.'),
                q("Govern via PaC reduz:",
                  "Decisões caso-a-caso e configura tribal knowledge em código.",
                  ["Apaga o histórico de decisões tomadas pelo time, decisão que parece razoável isolada, mas quebra a arquitetura no conjunto.", "Aumenta o número de tickets abertos para aprovação, comportamento que só é notado quando alguém audita os logs depois.", "Reduz a visibilidade que o time tem sobre as regras, decisão que parece inofensiva isolada, mas se acumula com o tempo."],
                  "Sem PaC, regra vira folclore: 'só fulano sabe'. Com PaC, está no repo.",
                  statement_en='Governing via PaC reduces:',
                  correct_en='Case-by-case decisions and encodes tribal knowledge in code.',
                  wrong_en=['Deletes the history of decisions made by the team, a decision that looks safe until the first real penetration test.', 'The need to version anything in git.', 'The possibility of reviewing changes in a PR.'],
                  explanation_en="Without PaC, the rule becomes folklore: 'only so-and-so knows'. With PaC, it's in the repo."),
            ],
        },
        # =====================================================================
        # 4.8 DAST inicial
        # =====================================================================
        {
            "title": "DAST inicial",
            "title_en": 'Initial DAST',
            "summary": "Testar a aplicação rodando à procura de falhas web comuns (OWASP).",
            "summary_en": 'Test the running application for common web flaws (OWASP).',
            "lesson": {
                "intro": (
                    "SAST analisa código sem rodar. DAST faz o oposto: ataca a app "
                    "rodando, simulando atacante real. Pega coisas que SAST nunca "
                    "veria, headers ausentes, redirects abertos, cors mal "
                    "configurado, defaults inseguros do servidor, fluxos dinâmicos. "
                    "Esta aula cobre filosofia (white-box vs black-box vs gray-box), "
                    "ferramentas (OWASP ZAP, Burp, Nuclei), integração no CI, "
                    "categorias OWASP Top 10, e a diferença crucial entre DAST "
                    "automatizado e pentest humano."
                ),
                "intro_en": 'SAST analyzes code without running it. DAST does the opposite: it attacks the running app, simulating a real attacker. It catches things SAST would never see — missing headers, open redirects, misconfigured CORS, insecure server defaults, dynamic flows. This lesson covers the philosophy (white-box vs black-box vs gray-box), tools (OWASP ZAP, Burp, Nuclei), CI integration, OWASP Top 10 categories, and the crucial difference between automated DAST and human pentesting.',
                "body": (
                """<h3>1. Quatro abordagens de teste, e por que nenhuma sozinha basta</h3>
<table>
<tr><th>Abordagem</th><th>Acesso</th><th>Foco</th><th>Limitação</th></tr>
<tr><td>SAST (white-box)</td><td>Código</td><td>Lógica, sinks</td><td>Não vê runtime</td></tr>
<tr><td>DAST (black-box)</td><td>App rodando</td><td>HTTP/runtime</td><td>Não vê código</td></tr>
<tr><td>IAST (gray-box)</td><td>Agente em runtime</td><td>Combina os dois</td><td>Adiciona overhead</td></tr>
<tr><td>RASP</td><td>Agente em runtime (defesa)</td><td>Bloqueia em produção</td><td>Pode degradar perf</td></tr>
</table>
<p>SAST analisa o CÓDIGO sem nunca executá-lo — enxerga a lógica interna
e onde um dado perigoso poderia fluir (um "sink"), mas nunca vê o
comportamento real em runtime: um header ausente, um redirect aberto, um
CORS mal configurado, um default inseguro do próprio servidor web —
nada disso aparece analisando código-fonte estático. DAST inverte
completamente essa perspectiva: ataca a aplicação RODANDO, como um
atacante real faria pela rede, sem nenhum acesso ao código — pega
exatamente as falhas que SAST nunca veria, ao custo de nunca enxergar a
lógica interna que produziu o comportamento observado. IAST tenta o
melhor dos dois mundos, com um agente instrumentando a aplicação em
runtime enquanto ainda tem acesso ao contexto de código — mais completo,
ao custo de overhead de performance real. E RASP não é bem um método de
TESTE, é uma camada de DEFESA ativa: um agente rodando em produção que
bloqueia comportamento malicioso detectado em tempo real, com o mesmo
trade-off de possível degradação de performance. Um DAST "passivo" (scan
de baseline) é barato e só captura o que já está visível sem tentar
explorar nada — headers, redirects, defaults expostos. Um DAST "ativo"
(full scan) faz fuzzing de verdade e tenta ataques reais — nunca rode
isso contra produção sem autorização explícita, dado o potencial de
causar dano real.</p>
<div class="mermaid">
flowchart TB
    Code["Código-fonte"] --> SAST["SAST"]
    Deps["Dependências"] --> SCA["SCA"]
    Run["App em execução"] --> DAST["DAST"]
    Run --> IAST["IAST"]
</div>


<h3>2. OWASP ZAP: o canivete suíço gratuito, do scan mais leve ao mais agressivo</h3>
<p>OWASP ZAP é open source, multiplataforma, e opera em modos com
intensidade crescente. O scan de <strong>baseline</strong> é passivo —
não tenta explorar nada, só observa o tráfego e sinaliza problema óbvio
(header ausente, cookie mal configurado) — leva minutos e o risco de
causar qualquer efeito colateral é praticamente nulo:</p>
<pre><code># Baseline: scan passivo, ~5min, quase sem risco
$ docker run --rm -v $(pwd)/zap:/zap/wrk owasp/zap2docker-stable \\
    zap-baseline.py -t https://staging.exemplo.com \\
    -r baseline-report.html

# Em CI
- name: ZAP Baseline
  uses: zaproxy/action-baseline@v0.10.0
  with:
    target: https://staging.exemplo.com
    fail_action: true   # falha CI se High</code></pre>
<p>O <strong>full scan</strong> (ativo) faz fuzzing de verdade,
tentando SQL injection, XSS, path traversal — demora horas e SÓ deve
rodar contra ambiente isolado com dados sintéticos, nunca contra dado
real de produção:</p>
<pre><code>$ zap-full-scan.py -t https://staging.exemplo.com</code></pre>
<p>Um DAST "cego" (sem autenticação configurada) só enxerga páginas
públicas — as rotas mais interessantes de uma aplicação real, aquelas
que exigem login, ficam completamente fora do alcance sem configurar um
contexto de autenticação explícito:</p>
<pre><code># context.xml em ZAP
&lt;context&gt;
  &lt;authentication&gt;
    &lt;type&gt;form-based&lt;/type&gt;
    &lt;loginUrl&gt;https://app/login&lt;/loginUrl&gt;
    &lt;loginRequestData&gt;username={%username%}&password={%password%}&lt;/loginRequestData&gt;
  &lt;/authentication&gt;
  &lt;users&gt;
    &lt;user&gt;{ name: alice, credentials: {...} }&lt;/user&gt;
  &lt;/users&gt;
&lt;/context&gt;</code></pre>

<h3>3. Burp Suite: o padrão que pentester profissional usa todo dia</h3>
<p>Comercial (na versão Pro), Burp Suite combina um proxy interativo com
um scanner automatizado, e é o padrão de fato entre pentesters
profissionais. O <strong>Proxy</strong> intercepta cada requisição saindo
do navegador, permitindo editar e reenviar manualmente. O
<strong>Repeater</strong> facilita enviar a mesma requisição com
pequenas variações repetidamente, útil para testar manualmente hipóteses
específicas. O <strong>Intruder</strong> automatiza fuzzing com listas de
payload configuráveis. O <strong>Scanner</strong> (só na versão Pro)
automatiza ataques comuns sem intervenção manual constante.
<strong>Decoder</strong> e <strong>Comparer</strong> são utilitários de
apoio para manipular e comparar dados codificados. E um ecossistema rico
de extensões (BApp Store) estende a ferramenta para casos específicos
que o núcleo não cobre nativamente.</p>

<h3>4. Nuclei: detecção rápida via template declarativo</h3>
<p>Nuclei usa templates declarativos (não código imperativo) para
detectar CVEs conhecidas, misconfigurações comuns e tokens expostos
acidentalmente — rápido e preciso justamente por focar em padrões JÁ
conhecidos, em vez de tentar descobrir algo novo:</p>
<pre><code>$ nuclei -u https://staging.exemplo.com \\
    -t http/cves/ \\
    -t http/exposures/ \\
    -severity high,critical

[2024-CVE-XXXX] [http] [high] https://staging.exemplo.com/.git/config
[exposed-tokens] [http] [critical] https://staging.exemplo.com/.env</code></pre>
<p>Encontrar um <code>.git/config</code> ou <code>.env</code> exposto
publicamente é surpreendentemente comum — arquivos que nunca deveriam
estar acessíveis via HTTP, mas que uma configuração de servidor web
descuidada acaba servindo como se fossem estáticos comuns.</p>

<h3>5. Um pipeline de CI que roda DAST contra o próprio build, não contra produção</h3>
<pre><code>name: dast
on:
  pull_request: {}
  schedule: [{ cron: '0 2 * * *' }]   # nightly
jobs:
  zap:
    runs-on: ubuntu-latest
    services:
      app:
        image: ghcr.io/empresa/app:${{ github.sha }}
        ports: [8000:8000]
      db:
        image: postgres:16
        env: { POSTGRES_PASSWORD: dast }
    steps:
      - run: ./scripts/wait-for-app.sh http://localhost:8000
      - run: ./scripts/seed-test-data.sh
      - uses: zaproxy/action-baseline@v0.10.0
        with:
          target: http://localhost:8000
          rules_file_name: .zap/rules.tsv
          cmd_options: '-z "-config api.disablekey=true"'
      - run: nuclei -u http://localhost:8000 -severity critical -ec
      - if: failure()
        uses: actions/upload-artifact@v4
        with: { name: dast-report, path: report_html.html }</code></pre>
<div class="mermaid">
flowchart LR
    PR["Pull request"] --> Build["Build da imagem"]
    Build --> Eph["Ambiente efêmero"]
    Eph --> Zap["ZAP / DAST"]
    Zap --> Gate["Gate do pipeline"]
</div>

<p>Subir a aplicação como um "service container" EFÊMERO dentro do
próprio job de CI, com dado sintético semeado especificamente para o
teste, resolve o dilema de "onde rodar DAST sem risco": o alvo é
descartado ao final do job, nunca chegando perto de dado real.</p>

<h3>6. OWASP Top 10: onde DAST é forte, e onde ele simplesmente não alcança</h3>
<table>
<tr><th>Categoria</th><th>O que DAST detecta</th></tr>
<tr><td>A01: Broken Access Control</td><td>IDOR via fuzz, paths não autorizados, BOLA</td></tr>
<tr><td>A02: Cryptographic Failures</td><td>TLS fraco, mixed content, sem HSTS</td></tr>
<tr><td>A03: Injection</td><td>SQLi, NoSQLi, command injection, XSS, LDAPi</td></tr>
<tr><td>A04: Insecure Design</td><td>Limitado, DAST não 'pensa' como humano</td></tr>
<tr><td>A05: Security Misconfiguration</td><td>Headers, debug=true, defaults expostos</td></tr>
<tr><td>A06: Vulnerable Components</td><td>Detecta versões antigas</td></tr>
<tr><td>A07: Auth Failures</td><td>Brute force, sessão fraca, credenciais default</td></tr>
<tr><td>A08: Software/Data Integrity</td><td>Limitado</td></tr>
<tr><td>A09: Logging/Monitoring</td><td>Não detecta diretamente</td></tr>
<tr><td>A10: SSRF</td><td>Fuzz de URL parameters</td></tr>
</table>
<p>O padrão que emerge dessa tabela é revelador: DAST é forte
justamente onde o problema se manifesta de forma OBSERVÁVEL pela rede —
injeção, configuração exposta, autenticação fraca. É fraco ou cego onde
o problema é de DESIGN ou de PROCESSO (design inseguro, integridade de
dado, monitoramento ausente) — categorias que exigem julgamento humano
sobre "isso deveria funcionar assim?", não um scanner automatizado
seguindo um padrão conhecido.</p>

<h3>7. Cabeçalhos de segurança: pequenas linhas de configuração, redução real de risco</h3>
<pre><code>Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=()
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp</code></pre>
<p>Cada um desses cabeçalhos fecha um vetor específico: HSTS impede
downgrade para HTTP mesmo que alguém tente forçar; CSP restringe de onde
script pode ser carregado, mitigando XSS mesmo se uma injeção
acontecer; <code>X-Frame-Options</code> impede que sua página seja
embutida num iframe malicioso (clickjacking); e os cabeçalhos de
isolamento cross-origin mais recentes fecham vetores de vazamento entre
abas do navegador. Ferramentas como o Mozilla Observatory avaliam uma
URL pública e devolvem uma nota (A+ a F) junto com a lista exata de
cabeçalhos faltando — uma forma rápida de auditar sem rodar nenhuma
ferramenta local.</p>

<h3>8. CORS: o erro que parece proteção mas na prática abre a porta</h3>
<pre><code># RUIM
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true   # browser ignora isso, mas...

# RUIM (reflete origin sem validar)
Access-Control-Allow-Origin: $REQUEST_ORIGIN

# BOM: allow-list explícito
if origin in ALLOWED_ORIGINS:
    Access-Control-Allow-Origin: origin</code></pre>
<p>Um erro comum é achar que "refletir o Origin da requisição de volta"
é uma configuração dinâmica inofensiva — na prática, isso permite
QUALQUER site (incluindo um malicioso) fazer requisição autenticada com
os cookies de sessão do usuário, porque o servidor aceita de volta
exatamente a origem que o próprio atacante controla. A correção correta
é uma allow-list EXPLÍCITA de origens confiáveis, verificada no
servidor antes de ecoar de volta qualquer valor.</p>

<h3>9. SSRF: quando a própria aplicação vira o proxy do atacante</h3>
<p>Quando uma aplicação faz uma requisição HTTP para uma URL fornecida
pelo próprio usuário (buscar uma imagem de um link, validar um webhook),
um atacante pode fornecer
<code>http://169.254.169.254/latest/meta-data/</code> — o endereço do
serviço de metadados da AWS, acessível apenas de DENTRO da própria
infraestrutura — e fazer a APLICAÇÃO (não o atacante diretamente) buscar
credenciais internas da instância e devolvê-las na resposta. A mitigação
combina várias camadas: uma allow-list explícita de domínios permitidos
para essas requisições; bloqueio ativo de faixas de IP privado (10.x,
192.168.x, e especificamente 169.254.x, onde vive o serviço de
metadados); IMDSv2 obrigatório na AWS, que exige um token de sessão
prévio dificultando exatamente esse tipo de exploração; e restrição de
egress via NACL ou Security Group, limitando para onde a própria
instância consegue iniciar conexão.</p>

<h3>10. DAST, Pentest e Bug Bounty: métodos complementares, não substitutos</h3>
<table>
<tr><th>Tipo</th><th>Quando</th><th>Cobertura</th><th>Custo</th></tr>
<tr><td>DAST (CI)</td><td>A cada PR</td><td>Padrões conhecidos automatizados</td><td>~$0</td></tr>
<tr><td>Pentest</td><td>Anual ou pré-launch</td><td>Profundo, criatividade humana</td><td>$$$</td></tr>
<tr><td>Bug Bounty</td><td>Contínuo</td><td>Crowd-sourced, qualidade variada</td><td>$ por bug encontrado</td></tr>
<tr><td>Red Team</td><td>1-2x ano</td><td>Simula ataque real, full-scope</td><td>$$$$</td></tr>
</table>
<p>A diferença central entre DAST e pentest não é só profundidade — é
CRIATIVIDADE: um pentester humano encadeia várias falhas de severidade
baixa individualmente para produzir um comprometimento sério, um
raciocínio que nenhuma ferramenta automatizada replica de forma
confiável ainda. Uma estratégia madura combina as camadas: DAST contínuo
pega regressão rápida e barata a cada mudança de código; pentest anual
(ou antes de um lançamento importante) traz profundidade humana
periódica; e um programa de bug bounty adiciona cobertura contínua de
uma comunidade externa diversa, com custo proporcional ao que
efetivamente encontrarem.</p>

<h3>11. O aviso legal que precede qualquer scan: autorização não é opcional</h3>
<p>Escanear um sistema sem autorização EXPRESSA pode configurar crime em
várias jurisdições (Marco Civil da Internet no Brasil, CFAA nos EUA,
regulamentações equivalentes na União Europeia) — mesmo com intenção
puramente educativa ou "só para testar". Use DAST ativo apenas contra
sistemas próprios, ambientes explicitamente contratados para pentest,
programas de bug bounty com escopo formalmente definido, ou plataformas
de prática desenhadas exatamente para esse fim (HackTheBox, TryHackMe,
PortSwigger Web Security Academy) — nunca contra um alvo de terceiro sem
permissão documentada.</p>

<h3>12. Cinco anti-padrões que tornam DAST inútil ou perigoso</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Perigoso</strong><p>Scan ativo em produção, sem auth, sem escopo.</p></div>
    <div class="lesson-viz-card"><strong>Seguro</strong><p>Ambiente isolado, credenciais de teste, autorização explícita.</p></div>
  </div>
  <figcaption>DAST útil exige ambiente e autorização — não bravura.</figcaption>
</figure>

<ul>
<li><strong>DAST ativo contra produção sem autorização</strong>: risco
real de causar negação de serviço, além da questão legal da seção
11.</li>
<li><strong>Sem contexto de autenticação</strong>: o scan só alcança a
tela de login, deixando toda a superfície autenticada — normalmente a
maior parte de uma aplicação real — completamente fora de cobertura.</li>
<li><strong>Mil falsos positivos sem afinamento</strong>: sem
configurar exclusões e ajustar regras, o time aprende a ignorar o
relatório inteiro, inclusive os achados reais.</li>
<li><strong>Sem SLA de remediação para o que é encontrado</strong>:
achados acumulam indefinidamente sem correção, tornando o próprio scan
um exercício sem efeito prático.</li>
<li><strong>DAST como única linha de defesa</strong>: complementa SAST e
pentest humano — nunca substitui nenhum dos dois, dado que cada método
enxerga uma fatia diferente do problema (seção 1).</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. Four testing approaches, and why none alone is enough</h3>
<table>
<tr><th>Abordagem</th><th>Acesso</th><th>Foco</th><th>Limitação</th></tr>
<tr><td>SAST (white-box)</td><td>Código</td><td>Lógica, sinks</td><td>Não vê runtime</td></tr>
<tr><td>DAST (black-box)</td><td>App rodando</td><td>HTTP/runtime</td><td>Não vê código</td></tr>
<tr><td>IAST (gray-box)</td><td>Agente em runtime</td><td>Combina os dois</td><td>Adiciona overhead</td></tr>
<tr><td>RASP</td><td>Agente em runtime (defesa)</td><td>Bloqueia em produção</td><td>Pode degradar perf</td></tr>
</table>
<p>SAST analyzes CODE without ever executing it — it sees internal
logic and where dangerous data could flow (a "sink"), but never sees
real runtime behavior: a missing header, an open redirect, misconfigured
CORS, an insecure default of the web server itself — none of that
appears when analyzing static source. DAST completely inverts that
perspective: it attacks the RUNNING application, simulating a real
attacker from the outside. White-box (full source access), black-box
(no internal knowledge), and gray-box (partial access, e.g. credentials)
are complementary approaches — mature programs combine them instead of
betting on a single one.</p>
<div class="mermaid">
flowchart TB
    Code["Source code"] --> SAST["SAST"]
    Deps["Dependencies"] --> SCA["SCA"]
    Run["Running app"] --> DAST["DAST"]
    Run --> IAST["IAST"]
</div>


<h3>2. OWASP ZAP: the free Swiss army knife, from the lightest scan to the most aggressive</h3>
<p>OWASP ZAP is open source, cross-platform, and operates in modes with
increasing intensity. The <strong>baseline</strong> scan is passive —
it does not try to exploit anything, only observes traffic and flags
obvious problems (missing header, misconfigured cookie) — it takes
minutes and the risk of any side effect is practically nil:</p>
<pre><code># Baseline: scan passivo, ~5min, quase sem risco
$ docker run --rm -v $(pwd)/zap:/zap/wrk owasp/zap2docker-stable \\
    zap-baseline.py -t https://staging.exemplo.com \\
    -r baseline-report.html

# Em CI
- name: ZAP Baseline
  uses: zaproxy/action-baseline@v0.10.0
  with:
    target: https://staging.exemplo.com
    fail_action: true   # falha CI se High</code></pre>
<p>The <strong>full scan</strong> (active) does real fuzzing,
trying SQL injection, XSS, path traversal — it takes hours and MUST
only run against an isolated environment with synthetic data, never
against real production data:</p>
<pre><code>$ zap-full-scan.py -t https://staging.exemplo.com</code></pre>
<p>A "blind" DAST (with no authentication configured) only sees public
pages — the most interesting routes of a real application, those that
require login, stay completely out of reach without configuring an
explicit authentication context:</p>
<pre><code># context.xml em ZAP
&lt;context&gt;
  &lt;authentication&gt;
    &lt;type&gt;form-based&lt;/type&gt;
    &lt;loginUrl&gt;https://app/login&lt;/loginUrl&gt;
    &lt;loginRequestData&gt;username={%username%}&password={%password%}&lt;/loginRequestData&gt;
  &lt;/authentication&gt;
  &lt;users&gt;
    &lt;user&gt;{ name: alice, credentials: {...} }&lt;/user&gt;
  &lt;/users&gt;
&lt;/context&gt;</code></pre>

<h3>3. Burp Suite: the standard professional pentesters use every day</h3>
<p>Commercial (in the Pro version), Burp Suite combines an interactive
proxy with an automated scanner, and is the de facto standard among
professional pentesters. The <strong>Proxy</strong> intercepts every
request leaving the browser, allowing manual edit and replay. The
<strong>Repeater</strong> makes it easy to send the same request with
small variations repeatedly, useful for manually testing hypotheses.
The <strong>Intruder</strong> automates payload brute-force. And the
<strong>Scanner</strong> runs automated active checks similar to ZAP's
full scan.</p>

<h3>4. Nuclei: fast detection via declarative templates</h3>
<p>Nuclei uses declarative templates (not imperative code) to detect
known CVEs, common misconfigurations, and accidentally exposed tokens —
fast and precise precisely because it focuses on ALREADY known patterns,
instead of trying to discover something new:</p>
<pre><code>$ nuclei -u https://staging.exemplo.com \\
    -t http/cves/ \\
    -t http/exposures/ \\
    -severity high,critical

[2024-CVE-XXXX] [http] [high] https://staging.exemplo.com/.git/config
[exposed-tokens] [http] [critical] https://staging.exemplo.com/.env</code></pre>
<p>Finding a publicly exposed <code>.git/config</code> or
<code>.env</code> is surprisingly common — files that should never be
reachable via HTTP, but that a careless web-server configuration ends up
serving as if they were ordinary static assets.</p>

<h3>5. A CI pipeline that runs DAST against the build itself, not against production</h3>
<pre><code>name: dast
on:
  pull_request: {}
  schedule: [{ cron: '0 2 * * *' }]   # nightly
jobs:
  zap:
    runs-on: ubuntu-latest
    services:
      app:
        image: ghcr.io/empresa/app:${{ github.sha }}
        ports: [8000:8000]
      db:
        image: postgres:16
        env: { POSTGRES_PASSWORD: dast }
    steps:
      - run: ./scripts/wait-for-app.sh http://localhost:8000
      - run: ./scripts/seed-test-data.sh
      - uses: zaproxy/action-baseline@v0.10.0
        with:
          target: http://localhost:8000
          rules_file_name: .zap/rules.tsv
          cmd_options: '-z "-config api.disablekey=true"'
      - run: nuclei -u http://localhost:8000 -severity critical -ec
      - if: failure()
        uses: actions/upload-artifact@v4
        with: { name: dast-report, path: report_html.html }</code></pre>
<div class="mermaid">
flowchart LR
    PR["Pull request"] --> Build["Image build"]
    Build --> Eph["Ephemeral environment"]
    Eph --> Zap["ZAP / DAST"]
    Zap --> Gate["Pipeline gate"]
</div>

<p>Bringing the application up as an EPHEMERAL "service container"
inside the CI job itself, with synthetic data seeded specifically for
the test, solves the dilemma of "where to run DAST without risk": the
target is discarded at the end of the job, never getting near real
data.</p>

<h3>6. OWASP Top 10: where DAST is strong, and where it simply cannot reach</h3>
<table>
<tr><th>Categoria</th><th>O que DAST detecta</th></tr>
<tr><td>A01: Broken Access Control</td><td>IDOR via fuzz, paths não autorizados, BOLA</td></tr>
<tr><td>A02: Cryptographic Failures</td><td>TLS fraco, mixed content, sem HSTS</td></tr>
<tr><td>A03: Injection</td><td>SQLi, NoSQLi, command injection, XSS, LDAPi</td></tr>
<tr><td>A04: Insecure Design</td><td>Limitado, DAST não 'pensa' como humano</td></tr>
<tr><td>A05: Security Misconfiguration</td><td>Headers, debug=true, defaults expostos</td></tr>
<tr><td>A06: Vulnerable Components</td><td>Detecta versões antigas</td></tr>
<tr><td>A07: Auth Failures</td><td>Brute force, sessão fraca, credenciais default</td></tr>
<tr><td>A08: Software/Data Integrity</td><td>Limitado</td></tr>
<tr><td>A09: Logging/Monitoring</td><td>Não detecta diretamente</td></tr>
<tr><td>A10: SSRF</td><td>Fuzz de URL parameters</td></tr>
</table>
<p>The pattern that emerges from that table is revealing: DAST is strong
exactly where the problem manifests in a NETWORK-OBSERVABLE way —
injection, exposed configuration, weak authentication. It is weak or
blind where the problem is DESIGN or PROCESS (insecure design, data
integrity, missing monitoring) — categories that require human judgment
about "should this work this way?", not a scanner probing endpoints.</p>

<h3>7. Security headers: small configuration lines, real risk reduction</h3>
<pre><code>Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=()
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp</code></pre>
<p>Each of those headers closes a specific vector: HSTS prevents
downgrade to HTTP even if someone tries to force it; CSP restricts where
script can be loaded from, mitigating XSS even if an injection happens;
<code>X-Frame-Options</code> prevents your page from being embedded in a
malicious iframe (clickjacking); and newer cross-origin isolation headers
close side-channel leakage vectors between origins.</p>

<h3>8. CORS: the mistake that looks like protection but in practice opens the door</h3>
<pre><code># RUIM
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true   # browser ignora isso, mas...

# RUIM (reflete origin sem validar)
Access-Control-Allow-Origin: $REQUEST_ORIGIN

# BOM: allow-list explícito
if origin in ALLOWED_ORIGINS:
    Access-Control-Allow-Origin: origin</code></pre>
<p>A common mistake is thinking that "reflecting the request Origin back"
is a harmless dynamic configuration — in practice, that lets ANY site
(including a malicious one) make an authenticated request with the user's
session cookies, because the server accepts back exactly the origin the
attacker themselves control. The correct fix is an EXPLICIT allow-list of
trusted origins, verified server-side.</p>

<h3>9. SSRF: when the application itself becomes the attacker's proxy</h3>
<p>When an application makes an HTTP request to a URL provided by the
user themselves (fetch an image from a link, validate a webhook), an
attacker can supply
<code>http://169.254.169.254/latest/meta-data/</code> — the AWS metadata
service address, reachable only from INSIDE the infrastructure itself —
and make the APPLICATION (not the attacker directly) fetch internal
credentials of the instance, turning the app into an involuntary proxy.</p>

<h3>10. DAST, Pentest, and Bug Bounty: complementary methods, not substitutes</h3>
<table>
<tr><th>Tipo</th><th>Quando</th><th>Cobertura</th><th>Custo</th></tr>
<tr><td>DAST (CI)</td><td>A cada PR</td><td>Padrões conhecidos automatizados</td><td>~$0</td></tr>
<tr><td>Pentest</td><td>Anual ou pré-launch</td><td>Profundo, criatividade humana</td><td>$$$</td></tr>
<tr><td>Bug Bounty</td><td>Contínuo</td><td>Crowd-sourced, qualidade variada</td><td>$ por bug encontrado</td></tr>
<tr><td>Red Team</td><td>1-2x ano</td><td>Simula ataque real, full-scope</td><td>$$$$</td></tr>
</table>
<p>The central difference between DAST and pentesting is not only depth —
it is CREATIVITY: a human pentester chains several individually low-
severity findings into a serious compromise, reasoning that no automated
tool reliably replicates yet. A mature strategy combines layers:
continuous DAST catches cheap, fast regressions on every code change;
periodic pentests explore creative chaining; bug bounty expands coverage
with diverse external researchers on a defined scope.</p>

<h3>11. The legal notice that precedes any scan: authorization is not optional</h3>
<p>Scanning a system without EXPRESS authorization can constitute a crime
in several jurisdictions (Marco Civil da Internet in Brazil, CFAA in the
US, equivalent regulations in the European Union) — even with purely
educational intent or "just to test". Use active DAST only against your
own systems, environments explicitly contracted for pentest, or bug
bounty programs with a formally defined scope.</p>

<h3>12. Five anti-patterns that make DAST useless or dangerous</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Dangerous</strong><p>Active scan in production, no auth, no scope.</p></div>
    <div class="lesson-viz-card"><strong>Safe</strong><p>Isolated env, test credentials, explicit authorization.</p></div>
  </div>
  <figcaption>Useful DAST needs environment and authorization — not bravado.</figcaption>
</figure>

<ul>
<li><strong>Active DAST against production without authorization</strong>:
real risk of causing denial of service, plus the legal issue from
section 11.</li>
<li><strong>No authentication context</strong>: the scan only reaches the
login screen, leaving the entire authenticated surface — usually most of
a real application — completely uncovered.</li>
<li><strong>A thousand false positives without tuning</strong>: without
configuring exclusions and adjusting rules, the team learns to ignore the
entire report, including the real findings.</li>
<li><strong>No remediation SLA for what is found</strong>:
findings accumulate indefinitely without fixes, making the scan itself
an exercise with no practical effect.</li>
<li><strong>DAST as the only line of defense</strong>: it complements SAST
and human pentesting — never replaces either, given that each method
sees a different slice of the problem (section 1).</li>
</ul>"""
                ),
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Suba app vulnerável intencionalmente (ex.: OWASP Juice Shop "
                    "ou DVWA) em Docker.</li>"
                    "<li>Rode <code>zap-baseline.py -t http://localhost:3000</code>.</li>"
                    "<li>Configure auth context e rode novamente cobrindo rotas "
                    "autenticadas.</li>"
                    "<li>Rode <code>nuclei</code> com templates CVE + exposures.</li>"
                    "<li>Em CI (GitHub Actions), suba app efêmero em service container "
                    "e rode ZAP baseline; falhe build em High.</li>"
                    "<li>Configure headers de segurança no servidor; re-rode DAST e "
                    "veja achados sumirem.</li>"
                    "<li>Verifique sua app real no Mozilla Observatory.</li>"
                    "<li>Bonus: faça PortSwigger Academy (gratuito) e ataque labs "
                    "manualmente.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    '<p><strong>Complete hands-on exercise</strong>:</p><ol><li>Bring up an intentionally vulnerable app (e.g. OWASP Juice Shop or DVWA) in Docker.</li><li>Run <code>zap-baseline.py -t http://localhost:3000</code>.</li><li>Configure an auth context and run again covering authenticated routes.</li><li>Run <code>nuclei</code> with CVE + exposure templates.</li><li>In CI (GitHub Actions), bring up an ephemeral app as a service container and run ZAP baseline; fail the build on High.</li><li>Configure security headers on the server; re-run DAST and watch findings disappear.</li><li>Check your real app on Mozilla Observatory.</li><li>Bonus: do PortSwigger Academy (free) and attack labs manually.</li></ol>'
                ),
            },
            "materials": [
                m("OWASP ZAP", "https://www.zaproxy.org/", "tool", "", title_en='OWASP ZAP', description_en=''),
                m("Burp Suite", "https://portswigger.net/burp", "tool", "", title_en='Burp Suite', description_en=''),
                m("Nuclei", "https://github.com/projectdiscovery/nuclei", "tool", "", title_en='Nuclei', description_en=''),
                m("OWASP Top 10", "https://owasp.org/www-project-top-ten/", "docs", "", title_en='OWASP Top 10', description_en=''),
                m("HackTricks", "https://book.hacktricks.xyz/", "book", "", title_en='HackTricks', description_en=''),
                m("PortSwigger Web Security Academy", "https://portswigger.net/web-security",
                  "course", "Treinamento gratuito de qualidade.", title_en='PortSwigger Web Security Academy', description_en='High-quality free training.'),
            ],
            "questions": [
                q("DAST exige:",
                  "App rodando.",
                  ["Só um arquivo de configuração escrito em YAML.", "Só o código de infraestrutura definido em IaC.", "Só o código-fonte da aplicação, sem execução."],
                  "Por isso DAST roda em staging/QA com dados sintéticos.",
                  statement_en='DAST requires:',
                  correct_en='A running app.',
                  wrong_en=['Only a YAML configuration file.', 'Only the application source code.', 'Only a static PDF report.'],
                  explanation_en="That's why DAST runs in staging/QA with synthetic data."),
                q("ZAP em modo baseline:",
                  "Faz scan rápido sem ataques agressivos.",
                  ["Substitui por completo a necessidade de pentest.", "Só analisa o código de infraestrutura em IaC.", "Só analisa o código do frontend da aplicação."],
                  "Verifica passivamente cabeçalhos, redirects, configs. Quase sem risco para o app.",
                  statement_en='ZAP in baseline mode:',
                  correct_en='Runs a quick scan without aggressive attacks.',
                  wrong_en=['Completely replaces the need for a pentest.', 'Only works against applications written in Java.', 'Automatically deletes vulnerable endpoints.'],
                  explanation_en='Passively checks headers, redirects, configs. Almost no risk to the app.'),
                q("XSS é:",
                  "Cross-site scripting, injeção de JS via input.",
                  ["Um tipo específico de configuração de TLS, decisão que parece inofensiva isolada, mas se acumula com o tempo.", "Um mecanismo de backup automático do banco, atalho comum quando o prazo aperta e ninguém revisa depois.", "Uma variante específica de injeção via SQL, decisão que parece razoável isolada, mas quebra a arquitetura no conjunto."],
                  "Reflected, stored, DOM-based. Mitigação: output encoding, CSP.",
                  statement_en='XSS is:',
                  correct_en='Cross-site scripting — JS injection via input.',
                  wrong_en=['A specific type of TLS configuration, a decision that looks safe until the first real penetration test.', 'A DNS configuration pattern for the domain.', 'A type of relational database backup.'],
                  explanation_en='Reflected, stored, DOM-based. Mitigation: output encoding, CSP.'),
                q("SQLi é:",
                  "SQL Injection, input que altera queries.",
                  ["Um problema que só ocorre em documentos XML.", "Um problema que costuma acontecer no browser.", "Um tipo específico de configuração de DNS."],
                  "Mitigação: prepared statements / ORM com parameterized queries. Nunca string concat.",
                  statement_en='SQLi is:',
                  correct_en='SQL Injection — input that alters queries.',
                  wrong_en=['A problem that only occurs in XML documents.', 'A type of TLS certificate used in the connection.', 'A metric for measuring API latency.'],
                  explanation_en='Mitigation: prepared statements / ORM with parameterized queries. Never concatenate strings.'),
                q("Idealmente DAST roda:",
                  "Em pipeline contra ambiente isolado.",
                  ["Manualmente, testando direto em produção real.", "Só faz sentido rodar já em produção real.", "Simplesmente não roda em algum tipo de pipeline."],
                  "Staging com dados sintéticos. Em produção, só com autorização e janela controlada.",
                  statement_en='Ideally DAST runs:',
                  correct_en='In the pipeline against an isolated environment.',
                  wrong_en=['Manually, testing directly against real production.', 'Only once a year with no automation.', "Exclusively on the developer's laptop with no CI."],
                  explanation_en='Staging with synthetic data. In production, only with authorization and a controlled window.'),
                q("Auth em DAST:",
                  "Permite cobrir endpoints autenticados.",
                  ["Bloqueia completamente a execução do scan.", "É totalmente opcional em qualquer cenário.", "Substitui a necessidade de usar senha no login."],
                  "Sem auth, scanner só vê página de login. Config 'authentication context' no scanner.",
                  statement_en='Auth in DAST:',
                  correct_en='Lets you cover authenticated endpoints.',
                  wrong_en=['Completely blocks the scan from running.', 'Replaces the need for any authorization check in the app.', 'Only works with basic authentication.'],
                  explanation_en="Without auth, the scanner only sees the login page. Configure an 'authentication context' in the scanner."),
                q("Headers de segurança:",
                  "DAST checa CSP, HSTS, X-Frame-Options etc.",
                  ["Só verifica a configuração de TLS da conexão.", "Só verifica os registros de DNS do domínio.", "Só verifica os resultados de uma análise SAST."],
                  "Headers como CSP, HSTS, X-Content-Type-Options reduzem risco com config simples.",
                  statement_en='Security headers:',
                  correct_en='DAST checks CSP, HSTS, X-Frame-Options, etc.',
                  wrong_en=['It only verifies the TLS configuration of the connection.', "It only verifies the domain's DNS records.", 'It only verifies the results of a SAST analysis.'],
                  explanation_en='Headers like CSP, HSTS, X-Content-Type-Options reduce risk with simple config.'),
                q("CSRF:",
                  "Cross-site request forgery, request feita em nome do usuário sem consentimento.",
                  ["Um tipo específico de algoritmo de criptografia, suposição que raramente se sustenta fora do ambiente controlado de laboratório.", "Um padrão específico de configuração de DNS, erro típico de configuração feita às pressas, sem revisão posterior.", "Uma variante específica de autenticação multifator, erro que só é percebido quando o time de operação já está lidando com o incidente."],
                  "Mitigação: CSRF token, SameSite cookies, double-submit cookie.",
                  statement_en='CSRF:',
                  correct_en="Cross-site request forgery — a request made on the user's behalf without consent.",
                  wrong_en=['A specific type of encryption algorithm, an assumption that rarely holds outside a controlled lab environment.', 'A specific DNS configuration pattern, a typical mistake from config done in a rush without later review.', 'A specific variant of multifactor authentication, an error only noticed when the ops team is already handling the incident.'],
                  explanation_en='Mitigation: CSRF token, SameSite cookies, double-submit cookie.'),
                q("Pentest difere de DAST porque:",
                  "Pentest envolve criatividade humana e exploração.",
                  ["O DAST é feito de forma totalmente manual por humanos.", "Não existe diferença real entre as duas abordagens.", "O pentest é feito só rodando scripts automatizados."],
                  "Pentester encadeia falhas baixas em compromisso. DAST sozinho raramente faz isso.",
                  statement_en='Pentesting differs from DAST because:',
                  correct_en='Pentesting involves human creativity and exploitation.',
                  wrong_en=['DAST is done entirely manually by humans.', 'There is no real difference between the two approaches.', 'Pentesting is done only by running automated scripts.'],
                  explanation_en='A pentester chains low findings into a compromise. DAST alone rarely does that.'),
                q("DAST exige consentimento:",
                  "Sim, sempre, antes de testar sistemas alheios.",
                  ["Só é necessário quando se usa uma VPN corporativa.", "Não, qualquer sistema pode ser testado livremente.", "Só é permitido testar durante o fim de semana."],
                  "Escaneamento sem autorização pode ser crime (Marco Civil, CFAA, etc.).",
                  statement_en='DAST requires consent:',
                  correct_en="Yes, always, before testing other people's systems.",
                  wrong_en=['Only required when using a corporate VPN, a common shortcut that looks fine until production surprises you.', 'No, any system can be tested freely, which tends to fail quietly until someone audits the setup.', 'Only allowed to test during the weekend, an assumption that rarely survives the first real incident review.'],
                  explanation_en='Unauthorized scanning can be a crime (Marco Civil, CFAA, etc.).'),
            ],
        },
        # =====================================================================
        # 4.9 API Security
        # =====================================================================
        {
            "title": "API Security",
            "title_en": 'API Security',
            "summary": "Como proteger os pontos de entrada das aplicações.",
            "summary_en": 'How to protect application entry points.',
            "lesson": {
                "intro": (
                    "APIs são a porta da frente da maioria dos sistemas modernos. "
                    "Mobile, SPA, integrações B2B, microsserviços internos, tudo "
                    "fala por API. Por isso, atacantes amam APIs. OWASP API "
                    "Security Top 10 mostra que falhas em APIs são <em>diferentes</em> "
                    "das tradicionais web: BOLA (autorização por objeto) é o nº1, "
                    "broken auth é nº2, excessive data exposure é nº3. Esta aula "
                    "cobre OAuth/OIDC, JWT bem usado, schemas, rate limiting, mass "
                    "assignment, mTLS, observability e webhook security."
                ),
                "intro_en": (
                    'APIs are the front door of most modern systems. Mobile, SPAs, B2B '
                    'integrations, internal microservices — everything talks over an API. '
                    "That's why attackers love APIs. The OWASP API Security Top 10 shows "
                    'that API failures are <em>different</em> from traditional web ones: '
                    'BOLA (object-level authorization) is #1, broken auth is #2, '
                    'excessive data exposure is #3. This lesson covers OAuth/OIDC, JWTs '
                    'used well, schemas, rate limiting, mass assignment, mTLS, '
                    'observability, and webhook security.'
                ),
                "body": (
                """<h3>1. Autenticação: provar quem está chamando, sem reinventar criptografia</h3>
<p>OAuth 2.0 é um framework de AUTORIZAÇÃO — um token bearer carregando
escopos específicos do que o portador pode fazer — enquanto o OIDC
adiciona uma camada de IDENTIDADE por cima, na forma de um
<code>id_token</code> em JWT assinado, respondendo especificamente "quem
é essa pessoa", não só "o que ela pode fazer". Quatro fluxos cobrem a
maioria dos casos reais: <strong>Authorization Code com PKCE</strong> é
o padrão atual para SPAs e aplicativos móveis — o PKCE (Proof Key for
Code Exchange) protege contra um código de autorização sendo
interceptado no meio do caminho e trocado por um token por outra parte;
<strong>Client Credentials</strong> serve comunicação
máquina-a-máquina, quando um microsserviço chama outro sem usuário
humano envolvido; <strong>Refresh Token</strong> renova o token de
acesso sem forçar novo login; e <strong>Device Code</strong> atende
dispositivos sem teclado prático (TVs, algumas CLIs). O fluxo Implicit
está deprecado e ROPC (Resource Owner Password Credentials, onde a
aplicação manuseia a senha do usuário diretamente) só deveria existir em
sistemas legados que ainda não migraram — ambos expõem mais superfície
de risco do que os fluxos modernos.</p>
<div class="mermaid">
flowchart LR
    Client["Cliente"] --> IdP["IdP OAuth2 / OIDC"]
    IdP --> Tok["Access token / JWT"]
    Tok --> Api["API"]
    Api --> Val["Valida assinatura, exp e audience"]
</div>

<p>Um JWT bem formado carrega estrutura específica que vale entender
campo a campo:</p>
<pre><code># Header
{"alg": "RS256", "typ": "JWT", "kid": "key-2024"}

# Payload
{
  "iss": "https://auth.empresa.com",
  "aud": "https://api.empresa.com",
  "sub": "user-123",
  "iat": 1714053000,
  "exp": 1714053900,         // 15min
  "scope": "read:orders write:orders",
  "jti": "random-uuid"     // permite revogação
}

# Signature
RSASHA256(base64(header) + '.' + base64(payload), private_key)</code></pre>
<p>O algoritmo de assinatura importa mais do que parece: RS256, ES256 ou
EdDSA usam par de chaves assimétrico (quem VALIDA o token não precisa da
chave privada que o ASSINOU) — <code>none</code> nunca deveria ser
aceito (permitiria um token sem assinatura nenhuma), e HS256 com chave
COMPARTILHADA entre múltiplos serviços é arriscado porque qualquer
serviço que possa VALIDAR o token também consegue FORJAR um novo, já que
a mesma chave serve para as duas operações. Validar de verdade significa
checar <code>iss</code> (emissor esperado), <code>aud</code> (audiência
— este token foi emitido PARA esta API específica?), <code>exp</code> e
<code>nbf</code> (janela de validade temporal), além da assinatura
propriamente dita — pular qualquer um desses campos abre uma classe
específica de vulnerabilidade (aceitar um token válido, mas emitido para
outra audiência, por exemplo). JWKS permite rotacionar a chave de
assinatura periodicamente, com o campo <code>kid</code> indicando qual
chave específica validar contra, permitindo múltiplas chaves válidas
simultaneamente durante a transição. TTL curto (5 a 15 minutos) para o
token de acesso limita a janela de uso se ele vazar, com o refresh token
cobrindo sessões mais longas. Nunca armazenar o token em
<code>localStorage</code> do navegador — um XSS bem-sucedido lê
localStorage livremente; um cookie <code>HttpOnly</code> com
<code>SameSite=Strict</code> não é acessível via JavaScript, fechando
essa via de roubo. Revogação antes do <code>exp</code> natural exige uma
lista negra indexada por <code>jti</code> (armazenada em Redis, com TTL
igual ao <code>exp</code> original, para não crescer indefinidamente). E
nunca colocar senha ou PII no payload — JWT é apenas CODIFICADO em
base64, não criptografado, qualquer um com o token em mãos lê o payload
inteiro.</p>

<h3>2. Autorização: BOLA é a falha nº1 do OWASP API Top 10, e o motivo é simples</h3>
<p>BOLA (Broken Object Level Authorization) acontece quando a API checa
"esse usuário está logado?" mas esquece de checar "esse usuário é DONO
do recurso específico que está pedindo?":</p>
<pre><code># RUIM
@app.get('/orders/{order_id}')
def get_order(order_id: int, user = Depends(current_user)):
    return Order.objects.get(id=order_id)   # qualquer logado vê qualquer pedido

# BOM
@app.get('/orders/{order_id}')
def get_order(order_id: int, user = Depends(current_user)):
    order = Order.objects.get(id=order_id)
    if order.user_id != user.id and not user.is_admin:
        raise HTTPException(403)
    return order</code></pre>
<p>O ataque é trivial de executar e por isso tão comum: trocar
<code>order_id</code> sequencialmente na URL (<code>?id=1</code>,
<code>?id=2</code>...) e ver quais respondem — nenhuma sofisticação
técnica necessária, só paciência. A defesa correspondente também é
simples de enunciar e fácil de esquecer: verificação de posse no nível
do RECURSO, em toda rota que aceita um identificador, sempre — é o tipo
de checagem que "óbvia depois do fato" mas que passa despercebida
justamente por parecer implícita demais para escrever explicitamente.
Scopes complementam essa defesa limitando o que um token PODE fazer
mesmo que a autorização de recurso falhe — um token com
<code>read:orders</code> nunca deveria conseguir executar uma operação
de escrita, independente de qualquer outra checagem. Para regras mais
elaboradas que dependem de múltiplos atributos (papel do usuário, tipo
do recurso, contexto da requisição), ABAC (Attribute-Based Access
Control) via engine dedicada como OPA expressa a lógica de forma
declarativa e testável isoladamente:</p>
<pre><code># OPA policy para autorização
package authz
default allow = false

allow {
  input.action == "read"
  input.resource.type == "order"
  input.resource.user_id == input.subject.id
}

allow {
  input.subject.role == "admin"
}</code></pre>

<h3>3. Validação de schema: deixar o framework rejeitar o que nunca deveria chegar ao seu código</h3>
<p>Definir a API formalmente via OpenAPI 3.x ou schema GraphQL, e deixar
o framework validar automaticamente contra essa definição, elimina uma
classe inteira de bug de validação manual esquecida:</p>
<pre><code># FastAPI: schema vira validação
from pydantic import BaseModel, Field, EmailStr

class CreateOrder(BaseModel):
    items: list[int] = Field(..., min_length=1, max_length=100)
    shipping_address: str = Field(..., max_length=500)
    customer_email: EmailStr
    notes: str | None = Field(None, max_length=1000)

@app.post('/orders')
def create_order(order: CreateOrder, user = Depends(current_user)):
    # Pydantic já validou tipos, ranges, formatos.
    ...</code></pre>
<p>O código do handler nunca chega a rodar com dado malformado — Pydantic
rejeita ANTES, com uma mensagem de erro estruturada, sem o desenvolvedor
precisar escrever um único <code>if</code> de validação manual. Em
GraphQL, o mesmo princípio de "limitar o que o cliente pode pedir" se
traduz em controles específicos: limitar a PROFUNDIDADE de uma query
evita consultas aninhadas exponencialmente caras; limitar a
COMPLEXIDADE (cost analysis) atribui um "custo" a cada campo e rejeita
queries acima de um limite total; desabilitar introspecção em produção
(a menos que a API seja deliberadamente pública) evita expor o schema
inteiro para reconhecimento de um atacante; e "persisted queries" restringe
o servidor a aceitar apenas queries PRÉ-APROVADAS, eliminando a
possibilidade de um cliente enviar uma query arbitrária nunca revisada.</p>

<h3>4. Rate limiting: três camadas, quatro algoritmos, e por que 429 sozinho não basta</h3>
<p>Rate limiting eficaz normalmente combina três camadas: na
<strong>borda</strong>, um WAF ou CDN (Cloudflare, AWS WAF) bloqueia bot
e tentativa de DDoS antes mesmo de chegar ao backend; no
<strong>gateway</strong> (Kong, AWS API Gateway, NGINX), limite por
chave de API, IP ou usuário; e na <strong>aplicação</strong>, regra de
negócio específica (5 tentativas de login em 15 minutos, por exemplo).
Os algoritmos por trás variam no trade-off entre simplicidade e
suavidade: <strong>fixed window</strong> (1000 req/min por IP) é simples
de implementar mas permite um "burst" duplo bem no limite da virada de
minuto; <strong>sliding window</strong> suaviza esse efeito ao custo de
mais cálculo; <strong>token bucket</strong> permite rajadas controladas
até uma capacidade acumulada; e <strong>leaky bucket</strong> impõe
throughput constante, sem rajada nenhuma. Uma implementação real de
sliding window com Redis usa um sorted set indexado por timestamp:</p>
<pre><code>def rate_limit(key: str, max_req: int, window_sec: int) -&gt; bool:
    now = time.time()
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, now - window_sec)
    pipe.zcard(key)
    pipe.zadd(key, {str(uuid.uuid4()): now})
    pipe.expire(key, window_sec)
    _, count, _, _ = pipe.execute()
    return count &lt; max_req</code></pre>
<p>Uma resposta 429 completa não é só o código de status — o cabeçalho
<code>Retry-After</code> diz ao cliente exatamente quanto tempo esperar
antes de tentar de novo, e os cabeçalhos <code>X-RateLimit-*</code> dão
visibilidade do estado atual do limite:</p>
<pre><code>HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1714053900</code></pre>

<h3>5. Mass Assignment: quando o corpo da requisição vira parâmetro direto do ORM</h3>
<p>Um handler que aceita o JSON da requisição e o aplica DIRETAMENTE nos
atributos de um objeto de banco de dados dá ao cliente controle sobre
QUALQUER campo do modelo, inclusive campos que nunca deveriam ser
editáveis externamente:</p>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Mass assignment</strong><p>JSON do request vira atributos do ORM sem allowlist.</p></div>
    <div class="lesson-viz-card"><strong>Seguro</strong><p>Schema explícito; só campos permitidos chegam ao modelo.</p></div>
  </div>
  <figcaption>Mass assignment: o corpo da requisição não é o modelo.</figcaption>
</figure>

<pre><code># RUIM
@app.put('/users/{id}')
def update_user(id, body: dict):
    user = User.objects.get(id=id)
    for k, v in body.items():
        setattr(user, k, v)   # cliente passa is_admin: true → ele vira admin!
    user.save()

# BOM: schema com allow-list
class UserUpdate(BaseModel):
    name: str | None
    email: EmailStr | None
    # is_admin NÃO está aqui, não pode ser setado por API pública

@app.put('/users/{id}')
def update_user(id, body: UserUpdate, user = Depends(current_user)):
    if user.id != id: raise HTTPException(403)
    target = User.objects.get(id=id)
    for k, v in body.dict(exclude_unset=True).items():
        setattr(target, k, v)
    target.save()</code></pre>
<p>O ataque é surpreendentemente direto: um cliente descobre (por
inspeção de resposta, documentação vazada, ou tentativa e erro) que o
modelo tem um campo <code>is_admin</code>, inclui esse campo no corpo do
PUT, e se o servidor aplicar tudo cegamente, o próprio usuário se
promove a administrador sem nenhuma checagem de permissão específica
para essa mudança. A correção não é "validar melhor" no sentido de
checagem de tipo — é usar uma ALLOW-LIST explícita de campos editáveis
(o schema <code>UserUpdate</code> acima), onde qualquer campo NÃO
declarado simplesmente não existe do ponto de vista de quem chama a
API.</p>

<h3>6. Excessive Data Exposure: retornar o objeto inteiro é mais fácil, e mais perigoso</h3>
<pre><code># RUIM
@app.get('/users/{id}')
def get_user(id):
    return User.objects.get(id=id).to_dict()
    # Retorna password_hash, internal_notes, ssn...

# BOM: response model explícito
class UserPublic(BaseModel):
    id: int
    name: str
    avatar_url: str | None

@app.get('/users/{id}', response_model=UserPublic)
def get_user(id):
    return User.objects.get(id=id)</code></pre>
<p>Serializar o objeto de banco INTEIRO é o caminho de menor esforço
imediato — e é exatamente por isso que aparece com tanta frequência:
funciona no primeiro teste, e só revela o problema quando alguém inspeciona
a resposta HTTP e encontra campos que nunca deveriam estar ali
(hash de senha, notas internas, dado sensível de outro contexto). Um
modelo de resposta EXPLÍCITO, declarando exatamente quais campos saem,
inverte o padrão de risco: um campo novo adicionado ao modelo de banco
não vaza automaticamente para a API só porque existe — precisa ser
adicionado deliberadamente ao <code>response_model</code> para
aparecer.</p>

<h3>7. Transporte: TLS não é opcional, e mTLS resolve o que TLS unilateral não alcança</h3>
<p>TLS 1.2 no mínimo, com 1.3 preferido sempre que possível, é a base
inegociável. HSTS com <code>max-age</code> longo e a flag preload
garante que o navegador nunca tente sequer uma conexão HTTP não
criptografada depois da primeira visita. Certificate pinning em
aplicativos móveis adiciona uma camada extra contra certificado
fraudulento, embora exija cuidado operacional (rotacionar o certificado
sem quebrar apps já publicados é um desafio real). Entre microsserviços
internos, TLS unilateral só prova a identidade do SERVIDOR para o
cliente — mTLS exige que AMBOS os lados apresentem certificado, provando
identidade mútua; um service mesh (Istio, Linkerd) automatiza essa
troca de certificado sem exigir código específico em cada serviço. E
tokens NUNCA devem ir na URL — parâmetros de URL acabam em logs de
acesso, em histórico de proxy, em cache de navegador — o único lugar
seguro para um token é o cabeçalho
<code>Authorization: Bearer ...</code>.</p>

<h3>8. Webhooks: verificar a assinatura antes de confiar em qualquer coisa que chegue</h3>
<p>Um endpoint de webhook é, por natureza, exposto publicamente para
receber chamadas de um serviço externo — e sem verificação, qualquer um
que descubra a URL pode enviar um payload forjado se passando pelo
provedor legítimo:</p>
<pre><code>POST /webhooks/stripe HTTP/1.1
Stripe-Signature: t=1614243000,v1=abc123def456...
Content-Type: application/json

{"id": "evt_...", "type": "charge.succeeded", ...}

# Receptor valida
import hmac, hashlib, time

def verify_webhook(body: bytes, signature_header: str, secret: str):
    timestamp, sig = parse_header(signature_header)
    if abs(time.time() - timestamp) &gt; 300:   # &gt;5min, replay
        raise Invalid('stale')
    expected = hmac.new(
        secret.encode(),
        f"{timestamp}.{body.decode()}".encode(),
        hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise Invalid('signature')</code></pre>
<p>A checagem de timestamp (rejeitar qualquer coisa mais velha que 5
minutos) fecha um vetor de ataque de replay: mesmo que um atacante
capture um payload assinado legítimo em trânsito, reenviá-lo depois da
janela de validade é rejeitado. E <code>hmac.compare_digest</code>
compara em tempo CONSTANTE — uma comparação ingênua com <code>==</code>
vaza informação sobre quantos caracteres do início já coincidem através
do tempo de execução, permitindo reconstruir a assinatura válida byte a
byte via medição cuidadosa de latência.</p>

<h3>9. Mensagens de erro: útil para você, inútil (de propósito) para quem não deveria ver</h3>
<pre><code># RUIM
except Exception as e:
    return {"error": str(e), "trace": traceback.format_exc()}

# BOM
except Exception as e:
    correlation_id = uuid.uuid4()
    logger.exception("erro", extra={"correlation_id": correlation_id})
    return JSONResponse(
        status_code=500,
        content={"error": "internal", "correlation_id": str(correlation_id)}
    )</code></pre>
<p>Devolver o traceback completo na resposta HTTP entrega ao cliente
(inclusive um atacante testando a API) detalhes de implementação
interna — nome de tabela, caminho de arquivo, versão de biblioteca —
informação que facilita um ataque direcionado subsequente. A alternativa
correta preserva os dois lados do problema: o cliente recebe um ID de
correlação genérico e opaco, e o log DETALHADO (com o traceback
completo) fica registrado internamente indexado por esse mesmo ID — o
time de suporte busca pelo <code>correlation_id</code> quando o cliente
reportar o problema, sem nunca ter exposto detalhe nenhum publicamente.</p>

<h3>10. Observabilidade de API: os quatro sinais que revelam ataque em andamento</h3>
<p>Logs estruturados em JSON, carregando <code>request_id</code>, um
hash do <code>user_id</code> (nunca o ID em claro se ele for sensível),
rota, status e latência — sem PII exposta diretamente no log — formam a
base investigativa. Métricas por rota (requisições/segundo, taxa de
erro, latência em p50/p99) revelam degradação antes de virar incidente
visível para o usuário. Traces via OpenTelemetry permitem seguir uma
requisição saltando entre serviços pelo mesmo <code>trace_id</code>
(detalhado na aula de Observabilidade Avançada). E alertas específicos
merecem atenção redobrada em API: um pico de respostas 401 sugere
tentativa de força bruta de credencial em andamento; um pico de 429
sugere tentativa de negação de serviço ou scraping agressivo; e um
aumento de latência sem mudança de tráfego correspondente sugere algo
consumindo recurso de forma anômala.</p>

<h3>11. API Gateway: centralizar o que, sem ele, cada serviço reimplementaria isoladamente</h3>
<p>Validar o JWT numa única camada de borda, deixando os serviços
internos CONFIAREM no resultado dessa validação, evita reimplementar a
mesma lógica de autenticação em cada microsserviço separadamente. Rate
limiting unificado impõe o mesmo limite de forma consistente, em vez de
cada serviço ter sua própria (e potencialmente inconsistente)
implementação. Logging e métricas centralizados dão visão agregada sem
depender de cada serviço instrumentar exatamente da mesma forma.
Versionamento de API (v1, v2 convivendo) e roteamento ficam numa camada
só, sem espalhar lógica de compatibilidade por todo o backend. E cache
de resposta na borda reduz carga nos serviços de origem para
requisições repetidas. Kong, AWS API Gateway, Apigee, NGINX, Traefik e
Envoy são as opções mais usadas nesse papel.</p>

<h3>12. Oito anti-padrões que resumem praticamente toda a aula</h3>
<div class="mermaid">
flowchart TD
    Req["Request"] --> Authn["Autenticação"]
    Authn --> Authz["Autorização / anti-BOLA"]
    Authz --> Schema["Validação de schema"]
    Schema --> Rate["Rate limit"]
    Rate --> Ok["Resposta"]
</div>

<ul>
<li><strong>JWT em localStorage do navegador</strong>: acessível a
qualquer XSS bem-sucedido.</li>
<li><strong>Token sem expiração</strong>: uma vez vazado, vale para
sempre.</li>
<li><strong>HS256 com segredo compartilhado entre serviços</strong>:
qualquer serviço que valida também consegue forjar.</li>
<li><strong>API sem rate limit nenhum</strong>: aberta a força bruta e
abuso de recurso sem custo para o atacante.</li>
<li><strong>BOLA</strong>: não checar posse do recurso, a falha nº1 do
OWASP API Top 10 (seção 2).</li>
<li><strong>Stack trace na resposta de erro</strong>: entrega detalhe
interno de graça a quem está testando a API.</li>
<li><strong>Token na URL</strong>: acaba em log de acesso, histórico de
proxy, cache de navegador.</li>
<li><strong>CORS com origem `*` e credentials habilitado</strong>:
permite QUALQUER site fazer requisição autenticada em nome do usuário —
uma combinação que navegadores modernos já bloqueiam por padrão, mas que
configuração incorreta ainda consegue contornar.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. Authentication: proving who is calling, without reinventing cryptography</h3>
<p>OAuth 2.0 is an AUTHORIZATION framework — a bearer token carrying
specific scopes of what the bearer can do — while OIDC adds an IDENTITY
layer on top, in the form of a signed JWT <code>id_token</code>,
answering specifically "who is this person", not only "what can they do".
Four flows cover most real cases: <strong>Authorization Code with
PKCE</strong> for SPAs and mobile; <strong>Client Credentials</strong>
for service-to-service; <strong>Device Code</strong> for limited-input
devices; and the deprecated Implicit flow, which should no longer be
used.</p>
<div class="mermaid">
flowchart LR
    Client["Client"] --> IdP["OAuth2 / OIDC IdP"]
    IdP --> Tok["Access token / JWT"]
    Tok --> Api["API"]
    Api --> Val["Validate signature, exp, and audience"]
</div>

<p>A well-formed JWT carries specific structure worth understanding
field by field:</p>
<pre><code># Header
{"alg": "RS256", "typ": "JWT", "kid": "key-2024"}

# Payload
{
  "iss": "https://auth.empresa.com",
  "aud": "https://api.empresa.com",
  "sub": "user-123",
  "iat": 1714053000,
  "exp": 1714053900,         // 15min
  "scope": "read:orders write:orders",
  "jti": "random-uuid"     // permite revogação
}

# Signature
RSASHA256(base64(header) + '.' + base64(payload), private_key)</code></pre>
<p>The signing algorithm matters more than it seems: RS256, ES256, or
EdDSA use an asymmetric key pair (whoever VALIDATES the token does not
need the private key that SIGNED it) — <code>none</code> should never be
accepted (it would allow a token with no signature at all), and HS256
with a SHARED secret across multiple services is risky because any
service that can VALIDATE the token can also FORGE one.</p>

<h3>2. Authorization: BOLA is #1 in the OWASP API Top 10, and the reason is simple</h3>
<p>BOLA (Broken Object Level Authorization) happens when the API checks
"is this user logged in?" but forgets to check "is this user the OWNER
of the specific resource they are asking for?":</p>
<pre><code># RUIM
@app.get('/orders/{order_id}')
def get_order(order_id: int, user = Depends(current_user)):
    return Order.objects.get(id=order_id)   # qualquer logado vê qualquer pedido

# BOM
@app.get('/orders/{order_id}')
def get_order(order_id: int, user = Depends(current_user)):
    order = Order.objects.get(id=order_id)
    if order.user_id != user.id and not user.is_admin:
        raise HTTPException(403)
    return order</code></pre>
<p>The attack is trivial to execute and therefore so common: swap
<code>order_id</code> sequentially in the URL (<code>?id=1</code>,
<code>?id=2</code>...) and see which ones respond — no technical
sophistication needed, just patience. The corresponding defense is also
simple to state and easy to forget: ownership verification at the
RESOURCE level, on every route that accepts an identifier, always —
that is the #1 item in the OWASP API Top 10 for a reason.</p>
<pre><code># OPA policy para autorização
package authz
default allow = false

allow {
  input.action == "read"
  input.resource.type == "order"
  input.resource.user_id == input.subject.id
}

allow {
  input.subject.role == "admin"
}</code></pre>

<h3>3. Schema validation: let the framework reject what should never reach your code</h3>
<p>Defining the API formally via OpenAPI 3.x or a GraphQL schema, and
letting the framework validate automatically against that definition,
eliminates an entire class of forgotten manual validation bugs:</p>
<pre><code># FastAPI: schema vira validação
from pydantic import BaseModel, Field, EmailStr

class CreateOrder(BaseModel):
    items: list[int] = Field(..., min_length=1, max_length=100)
    shipping_address: str = Field(..., max_length=500)
    customer_email: EmailStr
    notes: str | None = Field(None, max_length=1000)

@app.post('/orders')
def create_order(order: CreateOrder, user = Depends(current_user)):
    # Pydantic já validou tipos, ranges, formatos.
    ...</code></pre>
<p>Handler code never even runs with malformed data — Pydantic rejects
BEFORE, with a structured error message, without the developer writing a
single manual validation <code>if</code>. In GraphQL, the same principle
of "limit what the client can ask" translates into specific controls:
limiting query DEPTH avoids exponentially expensive nested queries;
limiting COMPLEXITY caps the cost of a single request; and persisted
queries restrict the client to a pre-approved set of operations.</p>

<h3>4. Rate limiting: three layers, four algorithms, and why 429 alone is not enough</h3>
<p>Effective rate limiting usually combines three layers: at the
<strong>edge</strong>, a WAF or CDN (Cloudflare, AWS WAF) blocks bots
and DDoS attempts before they even reach the backend; at the
<strong>gateway</strong> (Kong, AWS API Gateway, NGINX), limits by API
key, IP, or user; and in the <strong>application</strong>, specific
business rules (5 login attempts in 15 minutes, for example). Common
algorithms include fixed window, sliding window, token bucket, and
leaky bucket — Redis is the usual distributed counter store.</p>
<pre><code>def rate_limit(key: str, max_req: int, window_sec: int) -&gt; bool:
    now = time.time()
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, now - window_sec)
    pipe.zcard(key)
    pipe.zadd(key, {str(uuid.uuid4()): now})
    pipe.expire(key, window_sec)
    _, count, _, _ = pipe.execute()
    return count &lt; max_req</code></pre>
<p>A complete 429 response is not just the status code — the
<code>Retry-After</code> header tells the client exactly how long to wait
before trying again, and the <code>X-RateLimit-*</code> headers give
visibility into the current limit state:</p>
<pre><code>HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1714053900</code></pre>

<h3>5. Mass Assignment: when the request body becomes a direct ORM parameter</h3>
<p>A handler that accepts the request JSON and applies it DIRECTLY to
the attributes of a database object gives the client control over ANY
model field, including fields that should never be editable externally:</p>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Mass assignment</strong><p>Request JSON becomes ORM attributes with no allowlist.</p></div>
    <div class="lesson-viz-card"><strong>Safe</strong><p>Explicit schema; only allowed fields reach the model.</p></div>
  </div>
  <figcaption>Mass assignment: the request body is not the model.</figcaption>
</figure>

<pre><code># RUIM
@app.put('/users/{id}')
def update_user(id, body: dict):
    user = User.objects.get(id=id)
    for k, v in body.items():
        setattr(user, k, v)   # cliente passa is_admin: true → ele vira admin!
    user.save()

# BOM: schema com allow-list
class UserUpdate(BaseModel):
    name: str | None
    email: EmailStr | None
    # is_admin NÃO está aqui, não pode ser setado por API pública

@app.put('/users/{id}')
def update_user(id, body: UserUpdate, user = Depends(current_user)):
    if user.id != id: raise HTTPException(403)
    target = User.objects.get(id=id)
    for k, v in body.dict(exclude_unset=True).items():
        setattr(target, k, v)
    target.save()</code></pre>
<p>The attack is surprisingly direct: a client discovers (by inspecting
responses, leaked docs, or trial and error) that the model has an
<code>is_admin</code> field, includes that field in the PUT body, and if
the server applies everything blindly, the user promotes themselves to
administrator with no specific permission check for that change. The fix
is not "validate better" in the sense of more ifs — it is an explicit
DTO/allow-list of fields the client is allowed to set.</p>

<h3>6. Excessive Data Exposure: returning the whole object is easier — and more dangerous</h3>
<pre><code># RUIM
@app.get('/users/{id}')
def get_user(id):
    return User.objects.get(id=id).to_dict()
    # Retorna password_hash, internal_notes, ssn...

# BOM: response model explícito
class UserPublic(BaseModel):
    id: int
    name: str
    avatar_url: str | None

@app.get('/users/{id}', response_model=UserPublic)
def get_user(id):
    return User.objects.get(id=id)</code></pre>
<p>Serializing the ENTIRE database object is the path of least immediate
effort — and that is exactly why it shows up so often: it works on the
first test, and only reveals the problem when someone inspects the HTTP
response and finds fields that should never be there (password hash,
internal notes, sensitive data from another context). An EXPLICIT
response model, declaring exactly which fields leave the API, closes
that class of leak.</p>

<h3>7. Transport: TLS is not optional, and mTLS solves what unilateral TLS cannot reach</h3>
<p>TLS 1.2 at minimum, with 1.3 preferred whenever possible, is the
non-negotiable base. HSTS with a long <code>max-age</code> and the
preload flag ensures the browser never even tries an unencrypted HTTP
connection after the first visit. Certificate pinning in mobile apps
adds an extra layer against fraudulent certificates, though it needs
operational care (rotating the certificate without bricking clients).
And mTLS between microservices proves identity of BOTH ends of the
connection — not only that the channel is encrypted.</p>

<h3>8. Webhooks: verify the signature before trusting anything that arrives</h3>
<p>A webhook endpoint is, by nature, publicly exposed to receive calls
from an external service — and without verification, anyone who discovers
the URL can send a forged payload pretending to be the legitimate
provider:</p>
<pre><code>POST /webhooks/stripe HTTP/1.1
Stripe-Signature: t=1614243000,v1=abc123def456...
Content-Type: application/json

{"id": "evt_...", "type": "charge.succeeded", ...}

# Receptor valida
import hmac, hashlib, time

def verify_webhook(body: bytes, signature_header: str, secret: str):
    timestamp, sig = parse_header(signature_header)
    if abs(time.time() - timestamp) &gt; 300:   # &gt;5min, replay
        raise Invalid('stale')
    expected = hmac.new(
        secret.encode(),
        f"{timestamp}.{body.decode()}".encode(),
        hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise Invalid('signature')</code></pre>
<p>The timestamp check (rejecting anything older than 5 minutes) closes
a replay attack vector: even if an attacker captures a legitimate signed
payload in transit, resending it after the validity window is rejected.
And <code>hmac.compare_digest</code> compares in CONSTANT time — a naive
<code>==</code> comparison leaks information about how many leading
characters already matched.</p>

<h3>9. Error messages: useful for you, useless (on purpose) for anyone who shouldn't see</h3>
<pre><code># RUIM
except Exception as e:
    return {"error": str(e), "trace": traceback.format_exc()}

# BOM
except Exception as e:
    correlation_id = uuid.uuid4()
    logger.exception("erro", extra={"correlation_id": correlation_id})
    return JSONResponse(
        status_code=500,
        content={"error": "internal", "correlation_id": str(correlation_id)}
    )</code></pre>
<p>Returning the full traceback in the HTTP response hands the client
(including an attacker probing the API) internal implementation details —
table name, file path, library version — information that helps a
subsequent targeted attack. The correct alternative preserves both sides
of the problem: the client receives a generic, opaque correlation ID,
and the DETAILED log (with the traceback) stays on the server side,
tied to that same ID.</p>

<h3>10. API observability: the four signals that reveal an attack in progress</h3>
<p>Structured JSON logs carrying <code>request_id</code>, a hash of
<code>user_id</code> (never the clear ID if sensitive), route, status,
and latency — without PII exposed directly in the log — form the
investigative base. Per-route metrics (requests/second, error rate,
p50/p99 latency) reveal degradation before it becomes a user-visible
incident. Traces via OpenTelemetry let you follow a request across
services. And security-specific signals — spike in 401/403, unusual
BOLA patterns, rate-limit hits — often are the earliest indicators of
an attack in progress.</p>

<h3>11. API Gateway: centralize what each service would otherwise reimplement alone</h3>
<p>Validating the JWT at a single edge layer, letting internal services
TRUST that validation result, avoids reimplementing the same
authentication logic in every microservice separately. Unified rate
limiting imposes the same limit consistently, instead of each service
having its own (and potentially inconsistent) implementation. Centralized
logging and metrics give an aggregated view. An API Gateway (Kong, AWS
API Gateway, Apigee, NGINX) is where those cross-cutting concerns live —
so each service can focus on its business logic.</p>

<h3>12. Eight anti-patterns that practically summarize the whole lesson</h3>
<div class="mermaid">
flowchart TD
    Req["Request"] --> Authn["Authentication"]
    Authn --> Authz["Authorization / anti-BOLA"]
    Authz --> Schema["Schema validation"]
    Schema --> Rate["Rate limit"]
    Rate --> Ok["Response"]
</div>

<ul>
<li><strong>JWT in browser localStorage</strong>: accessible to any
successful XSS.</li>
<li><strong>Token with no expiration</strong>: once leaked, it is valid
forever.</li>
<li><strong>HS256 with a secret shared across services</strong>:
any service that validates can also forge.</li>
<li><strong>API with no rate limit at all</strong>: open to brute force and
resource abuse at no cost to the attacker.</li>
<li><strong>BOLA</strong>: not checking resource ownership, #1 failure in
the OWASP API Top 10 (section 2).</li>
<li><strong>Stack trace in the error response</strong>: hands internal
detail for free to anyone probing the API.</li>
<li><strong>Token in the URL</strong>: ends up in access logs, proxy
history, browser cache.</li>
<li><strong>CORS with origin `*` and credentials enabled</strong>:
lets ANY site make an authenticated request on the user's behalf — a
combination modern browsers already block by default, but incorrect
configuration can still work around.</li>
</ul>"""
                ),
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Implemente OAuth 2.0 Authorization Code + PKCE em FastAPI/"
                    "Express (use Authlib/passport).</li>"
                    "<li>Valide JWT corretamente: iss, aud, exp, signature via JWKS.</li>"
                    "<li>Implemente BOLA-resistant: cada endpoint checa "
                    "<code>resource.owner == user.id</code>.</li>"
                    "<li>Adicione rate limit Redis sliding window por user.</li>"
                    "<li>Use Pydantic/Zod para validar input com schemas.</li>"
                    "<li>Configure response_model para evitar excessive data exposure.</li>"
                    "<li>Implemente webhook receiver com HMAC verification.</li>"
                    "<li>Adicione headers de segurança (CSP, HSTS) e teste com "
                    "Mozilla Observatory.</li>"
                    "<li>Carga: <code>k6 run script.js</code> simula burst, veja 429.</li>"
                    "<li>Bonus: mTLS entre 2 microsserviços com Linkerd local.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    '<p><strong>Complete hands-on exercise</strong>:</p><ol><li>Implement OAuth 2.0 Authorization Code + PKCE in FastAPI/Express (use Authlib/passport).</li><li>Validate JWTs correctly: iss, aud, exp, signature via JWKS.</li><li>Implement BOLA-resistant checks: every endpoint verifies <code>resource.owner == user.id</code>.</li><li>Add a Redis sliding-window rate limit per user.</li><li>Use Pydantic/Zod to validate input with schemas.</li><li>Configure response_model to avoid excessive data exposure.</li><li>Implement a webhook receiver with HMAC verification.</li><li>Add security headers (CSP, HSTS) and test with Mozilla Observatory.</li><li>Load: <code>k6 run script.js</code> simulates a burst, watch for 429.</li><li>Bonus: mTLS between 2 microservices with local Linkerd.</li></ol>'
                ),
            },
            "materials": [
                m("OWASP API Top 10", "https://owasp.org/API-Security/editions/2023/en/0x11-t10/", "docs", "", title_en='OWASP API Top 10', description_en=''),
                m("OAuth 2.0 (RFC 6749)", "https://datatracker.ietf.org/doc/html/rfc6749", "docs", "", title_en='OAuth 2.0 (RFC 6749)', description_en=''),
                m("OpenAPI Specification", "https://swagger.io/specification/", "docs", "", title_en='OpenAPI Specification', description_en=''),
                m("k6", "https://k6.io/docs/", "tool", "", title_en='k6', description_en=''),
                m("OIDC (OpenID Connect)", "https://openid.net/developers/how-connect-works/", "docs", "", title_en='OIDC (OpenID Connect)', description_en=''),
                m("JWT.io", "https://jwt.io/", "tool", "Decoder e referência.", title_en='JWT.io', description_en='Decoder and reference.'),
            ],
            "questions": [
                q("OAuth 2.0 difere de OIDC porque:",
                  "OIDC adiciona camada de identidade (id_token) sobre OAuth.",
                  ["São exatamente o mesmo protocolo, sem diferença real, resultado típico de copiar configuração de outro projeto sem adaptar.", "O OAuth puro já inclui um id_token por padrão, abordagem que ignora o cenário de falha mais provável na prática.", "O OIDC é considerado uma camada menos segura que o OAuth, prática ainda comum em sistema legado que raramente é atualizado."],
                  "OAuth = autorização (delegação de acesso). OIDC = identidade (id_token assinado).",
                  statement_en='OAuth 2.0 differs from OIDC because:',
                  correct_en='OIDC adds an identity layer (id_token) on top of OAuth.',
                  wrong_en=['They are exactly the same protocol, with no real difference, a typical result of copying config from another project without adapting.', 'Pure OAuth already includes an id_token by default, an approach that ignores the most likely failure scenario in practice.', 'OIDC is considered a less secure layer than OAuth, a practice still common in legacy systems that are rarely updated.'],
                  explanation_en='OAuth = authorization (access delegation). OIDC = identity (signed id_token).'),
                q("BOLA (Broken Object Level Auth):",
                  "Checar autorização no nível do recurso individual.",
                  ["Um algoritmo de criptografia considerado fraco.", "Um tipo específico de configuração de TLS.", "Um programa de recompensa por vulnerabilidades encontradas."],
                  "API que aceita /orders/{id} sem checar se o usuário é dono do pedido.",
                  statement_en='BOLA (Broken Object Level Auth):',
                  correct_en='Checking authorization at the individual resource level.',
                  wrong_en=['A cryptography algorithm considered weak, a common shortcut that looks fine until production surprises you.', 'A specific type of TLS configuration, which tends to fail quietly until someone audits the setup.', 'A bug bounty program for found vulnerabilities, an assumption that rarely survives the first real incident review.'],
                  explanation_en='An API that accepts /orders/{id} without checking whether the user owns the order.'),
                q("Rate limit ajuda contra:",
                  "Brute force e DoS.",
                  ["Melhorar a performance geral de resposta da API.", "Fortalecer a configuração de TLS usada na conexão.", "Melhorar o formato dos logs gerados pela API."],
                  "Camadas: gateway + app. Use Redis para sliding window distribuído.",
                  statement_en='Rate limiting helps against:',
                  correct_en='Brute force and DoS.',
                  wrong_en=['Improving the overall response performance of the API.', 'Strengthening the TLS configuration used in the connection.', 'Improving the format of logs generated by the API.'],
                  explanation_en='Layers: gateway + app. Use Redis for a distributed sliding window.'),
                q("Validação de schema:",
                  "Rejeita payloads que não obedecem à API spec.",
                  ["Só é aplicada já em ambiente de produção.", "Substitui a necessidade de autenticar a chamada.", "Aceita qualquer payload enviado, sem restrição."],
                  "OpenAPI + framework auto-validador (FastAPI, Spring). Reduz exploits de input.",
                  statement_en='Schema validation:',
                  correct_en="Rejects payloads that don't obey the API spec.",
                  wrong_en=['Is only applied once already in production.', 'Replaces the need to authenticate the call.', 'Accepts any payload sent, with no restriction.'],
                  explanation_en='OpenAPI + an auto-validating framework (FastAPI, Spring). Reduces input exploits.'),
                q("Token JWT deve:",
                  "Ter exp curta + refresh token + assinatura forte.",
                  ["Ser eterno, sem alguma data de expiração definida.", "Conter a senha do usuário em texto plano no payload.", "Ser emitido sem alguma assinatura criptográfica."],
                  "Algoritmo: RS256/EdDSA, não 'none'. Exp típico: 5-15 min para acesso.",
                  statement_en='A JWT token should:',
                  correct_en='Have a short exp + refresh token + strong signature.',
                  wrong_en=['Be eternal, with no expiration date defined.', "Contain the user's password in plain text in the payload.", 'Be issued without any cryptographic signature.'],
                  explanation_en="Algorithm: RS256/EdDSA, not 'none'. Typical exp: 5–15 min for access."),
                q("CORS mal configurado:",
                  "Permite frontends maliciosos chamarem sua API.",
                  ["Acelera o carregamento de páginas no browser.", "Substitui a necessidade de autenticar a chamada.", "Comprime o tamanho da resposta enviada pela API."],
                  "Allow-list explícito de origins; nunca `*` com `credentials: true`.",
                  statement_en='Misconfigured CORS:',
                  correct_en='Allows malicious frontends to call your API.',
                  wrong_en=['Speeds up page loading in the browser.', 'Replaces the need to authenticate the call.', 'Compresses the size of the response sent by the API.'],
                  explanation_en='Explicit allow-list of origins; never `*` with `credentials: true`.'),
                q("API Gateway serve para:",
                  "Centralizar auth, rate limit, observability.",
                  ["Apagar automaticamente microserviços sem uso.", "Substituir por completo o cluster de Kubernetes.", "Substituir a necessidade de configurar IAM na conta."],
                  "Tira responsabilidades transversais de cada serviço. Kong, AWS API Gateway, NGINX.",
                  statement_en='An API Gateway is for:',
                  correct_en='Centralizing auth, rate limiting, observability.',
                  wrong_en=['Automatically deleting unused microservices.', 'Completely replacing the Kubernetes cluster.', 'Replacing the need to configure IAM on the account.'],
                  explanation_en='Takes cross-cutting responsibilities out of each service. Kong, AWS API Gateway, NGINX.'),
                q("Mass assignment:",
                  "Cliente injeta campos não esperados no body (ex.: is_admin).",
                  ["Um tipo específico de configuração de TLS, resultado típico de copiar configuração de outro projeto sem adaptar.", "Uma categoria específica de log gerado pela API, comportamento que só é notado quando alguém audita os logs depois.", "Um mecanismo de backup automático do banco de dados, atalho que parece seguro isolado, mas quebra quando combinado com outros sistemas."],
                  "Mitigação: DTOs com allow-list explícito; nunca passar request.json direto pro ORM.",
                  statement_en='Mass assignment:',
                  correct_en='The client injects unexpected fields in the body (e.g. is_admin).',
                  wrong_en=['A specific type of TLS configuration, a typical result of copying config from another project without adapting.', 'A specific category of log generated by the API, behavior only noticed when someone audits the logs later.', 'An automatic database backup mechanism, a shortcut that looks safe in isolation but breaks when combined with other systems.'],
                  explanation_en='Mitigation: DTOs with an explicit allow-list; never pass request.json straight to the ORM.'),
                q("Excessive Data Exposure:",
                  "API retorna mais campos que o necessário.",
                  ["Um mecanismo de backup automático dos dados da API.", "Um tipo específico de configuração de DNS.", "Uma técnica de otimização de performance da API."],
                  "Use response models específicos por endpoint. Cuide de PII e segredos no retorno.",
                  statement_en='Excessive Data Exposure:',
                  correct_en='The API returns more fields than necessary.',
                  wrong_en=["An automatic backup mechanism for the API's data.", 'A specific type of DNS configuration.', 'A technique for optimizing API performance.'],
                  explanation_en='Use response models specific to each endpoint. Watch for PII and secrets in the return.'),
                q("Webhook seguro precisa:",
                  "Assinatura HMAC verificada no destino.",
                  ["Só funcionar sobre endereçamento IPv6 configurado.", "Funcionar sem algum tipo de autenticação no destino.", "Trafegar por HTTP puro, sem alguma criptografia."],
                  "Stripe, GitHub, Slack assinam com HMAC. Receptor valida antes de processar.",
                  statement_en='A secure webhook needs:',
                  correct_en='An HMAC signature verified at the destination.',
                  wrong_en=['To only work over configured IPv6 addressing.', 'To work without any authentication at the destination.', 'To travel over plain HTTP, with no encryption.'],
                  explanation_en='Stripe, GitHub, Slack sign with HMAC. The receiver validates before processing.'),
            ],
        },
        # =====================================================================
        # 4.10 Centralized Logging
        # =====================================================================
        {
            "title": "Centralized Logging",
            "title_en": 'Centralized Logging',
            "summary": "Trazer logs de vários lugares para uma tela só.",
            "summary_en": 'Bring logs from many places onto a single screen.',
            "lesson": {
                "intro": (
                    "Investigar incidente entre 20 servidores via SSH manual é "
                    "castigo medieval. Em microsserviços, com 50+ pods efêmeros, é "
                    "impossível. Logs centralizados são o pré-requisito básico de "
                    "operação moderna. Esta aula cobre stacks (ELK, EFK, Grafana "
                    "Loki, OpenSearch, SaaS), logs estruturados em JSON, coleta "
                    "(Fluent Bit, Vector, Promtail), retenção e custo, sanitização "
                    "de PII, e como logs se relacionam com métricas e traces nos "
                    "três pilares da observabilidade."
                ),
                "intro_en": "Investigating an incident across 20 servers via manual SSH is medieval punishment. In microservices, with 50+ ephemeral pods, it's impossible. Centralized logs are the basic prerequisite of modern operations. This lesson covers stacks (ELK, EFK, Grafana Loki, OpenSearch, SaaS), structured JSON logs, collection (Fluent Bit, Vector, Promtail), retention and cost, PII sanitization, and how logs relate to metrics and traces in the three pillars of observability.",
                "body": (
                """<h3>1. Pilhas comuns: cada uma resolve o mesmo problema com um trade-off diferente</h3>
<table>
<tr><th>Stack</th><th>Componentes</th><th>Notas</th></tr>
<tr><td>ELK</td><td>Elasticsearch + Logstash + Kibana</td><td>Maduro, poderoso. Caro em escala (RAM-hungry).</td></tr>
<tr><td>EFK</td><td>Elasticsearch + Fluentd/Bit + Kibana</td><td>Logstash → Fluent (mais leve).</td></tr>
<tr><td>OpenSearch</td><td>Fork ASL2 do ES</td><td>Após mudança de licença ES (2021).</td></tr>
<tr><td>Grafana Loki</td><td>Loki + Promtail/Vector + Grafana</td><td>Indexa só labels. Custo &lt;&lt; ELK.</td></tr>
<tr><td>Datadog/Splunk/New Relic</td><td>SaaS</td><td>UX top, $ alto, retenção limitada.</td></tr>
<tr><td>VictoriaLogs</td><td>OSS, eficiente</td><td>Performance forte, ainda jovem.</td></tr>
</table>
<p>A escolha entre elas raramente é sobre qual é "melhor" em abstrato —
é sobre onde o time quer pagar o custo. ELK/EFK entregam busca de texto
completo poderosa, ao preço de indexar TUDO (caro em RAM e disco em
volume alto). Loki inverte essa troca radicalmente (detalhado na seção
4), indexando só metadados e comprimindo o resto — muito mais barato,
mas com busca de conteúdo mais lenta. OpenSearch existe especificamente
porque a Elastic mudou a licença do Elasticsearch em 2021 para uma menos
permissiva, e a comunidade fez um fork sob licença Apache 2.0 aberta
para preservar a opção open-source de verdade. E as opções SaaS
(Datadog, Splunk, New Relic) trocam operação própria por assinatura —
UX geralmente superior, mas custo que escala rápido com volume, e
retenção padrão frequentemente mais curta do que uma solução self-hosted
permitiria pelo mesmo orçamento.</p>
<div class="mermaid">
flowchart TB
    Apps["Serviços"] --> Elk["ELK / OpenSearch"]
    Apps --> Loki["Grafana Loki"]
    Apps --> Cloud["CloudWatch / Stackdriver"]
</div>


<h3>2. Log estruturado: texto livre é para humano ler, JSON é para máquina consultar</h3>
<p>Um log em texto livre é fácil de escrever e ilegível para uma
ferramenta buscar por campo específico — a única forma de "consultar"
é grep por substring, frágil a qualquer mudança de formato:</p>
<pre><code># RUIM
[2024-04-25 10:30:15] INFO User 123 placed order 456 for $99.50

# BOM
{"ts":"2024-04-25T10:30:15Z","level":"info","service":"orders",
 "event":"order_placed","user_id":"u_123","order_id":"o_456",
 "amount":99.50,"currency":"USD","trace_id":"abc-123",
 "span_id":"span-xyz"}</code></pre>
<p>Com JSON em uma linha (NDJSON), consultar "todas as ordens acima de
$100 que falharam no serviço de pagamento" vira uma query estruturada
por campo, não uma expressão regular tentando adivinhar onde o valor
está na string. Um conjunto de campos padrão vale adotar
consistentemente em toda a organização: <code>ts</code> em ISO 8601 UTC
com timezone explícito; <code>level</code> seguindo a escala
debug/info/warn/error/fatal; <code>service</code> e <code>env</code>
identificando de onde veio; <code>version</code> (o SHA do build)
permitindo correlacionar um comportamento com uma versão específica;
<code>trace_id</code>/<code>span_id</code> para correlação com tracing
distribuído (seção 8); um hash de <code>user_id</code> (nunca o valor
direto se for sensível) mais <code>request_id</code>; um
<code>event</code> semântico nomeando o que aconteceu; e opcionalmente
uma <code>message</code> legível por humano complementando os campos
estruturados. Em Python, uma biblioteca como structlog automatiza essa
estrutura sem exigir montar o JSON manualmente a cada chamada de log:</p>
<pre><code>import structlog
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.contextvars.merge_contextvars,
        structlog.processors.JSONRenderer(),
    ],
)
log = structlog.get_logger()

log.info('order_placed', user_id=user.id_hash, order_id=order.id, amount=99.50)
# {"event":"order_placed","timestamp":"...","level":"info",...}</code></pre>

<h3>3. Coleta: da aplicação ao backend, passando por um agente dedicado</h3>
<p>Seguindo o princípio 12-factor (aula de Docker Fundamentals), a
aplicação escreve em stdout, e é responsabilidade de um COLETOR separado
(rodando como DaemonSet em Kubernetes, ou agente no host) ler esse
stream e encaminhar para o backend de armazenamento. Cada coletor tem um
perfil de trade-off diferente:</p>
<table>
<tr><th>Coletor</th><th>Linguagem</th><th>Notas</th></tr>
<tr><td>Fluentd</td><td>Ruby</td><td>Veterano, plugins ricos.</td></tr>
<tr><td>Fluent Bit</td><td>C</td><td>Mais leve; default em K8s.</td></tr>
<tr><td>Vector</td><td>Rust</td><td>Performant, VRL para transformações.</td></tr>
<tr><td>Promtail</td><td>Go</td><td>Específico para Loki.</td></tr>
<tr><td>OTel Collector</td><td>Go</td><td>Multi-signal (logs+metrics+traces).</td></tr>
<tr><td>Logstash</td><td>JVM</td><td>Pesado; legado.</td></tr>
</table>
<p>Fluent Bit se tornou o padrão de fato em Kubernetes justamente por
rodar em C — footprint de memória pequeno o suficiente para rodar como
DaemonSet em TODO node sem competir por recurso com as cargas de
trabalho reais. Uma configuração típica lê os arquivos de log de
container, enriquece com metadados do Kubernetes (namespace, nome do
pod), e encaminha para um backend como Loki:</p>
<pre><code># Fluent Bit em K8s (DaemonSet), config
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            docker
    DB                /var/log/flb_kube.db
    Tag               kube.*
[FILTER]
    Name              kubernetes
    Match             kube.*
    Merge_Log         On
[FILTER]
    Name              modify
    Match             kube.*
    Remove            stream
[OUTPUT]
    Name              loki
    Match             kube.*
    Host              loki.observability
    Labels            $kubernetes['namespace_name'],$kubernetes['pod_name']</code></pre>

<h3>4. Loki: barato porque indexa só o rótulo, não o conteúdo</h3>
<p>A diferença estrutural de Loki para Elasticsearch é a decisão central
de design: Loki NÃO indexa o conteúdo do log — indexa só os LABELS
(pares chave-valor), enquanto o conteúdo bruto é comprimido e lido sob
demanda quando uma query específica precisa dele. Essa escolha é o que
torna o custo de operação de Loki drasticamente menor que ELK em volumes
altos — o índice fica pequeno mesmo com terabytes de log bruto
armazenado. O trade-off correspondente: uma busca por SUBSTRING dentro
do conteúdo precisa varrer todos os logs que casam com o filtro de
label (mais lenta), enquanto uma busca por LABEL específico
(<code>{namespace="prod", service="api", level="error"}</code>) é
rápida, porque só toca o índice, não o conteúdo bruto. LogQL, a
linguagem de query do Loki, combina os dois:</p>
<pre><code># Filtro por labels + texto
{namespace="prod", service="api"} |= "error" | json | status &gt;= 500

# Métricas a partir de logs
rate({namespace="prod"} |= "error" [5m])

# p99 latency dos logs
quantile_over_time(0.99, {service="api"} | json | unwrap latency_ms [5m])</code></pre>
<p>O cuidado mais crítico ao operar Loki: NUNCA usar um identificador
com alta cardinalidade (<code>user_id</code>, <code>request_id</code>)
como label — cada valor distinto de label vira uma série de índice
separada, e um identificador único por requisição explode o índice para
um tamanho tão grande quanto o problema que Loki foi escolhido
especificamente para evitar.</p>

<h3>5. Retenção e tiering: nem todo log merece o mesmo tempo de vida</h3>
<p>Log cresce rápido — facilmente terabytes por mês numa aplicação de
tráfego médio — e reter tudo indefinidamente no mesmo tier de
armazenamento caro é desperdício. Uma política sensata varia por
categoria: log de DEBUG raramente precisa de mais que alguns dias (3 a
7); log de INFO tipicamente 14 a 30 dias; log de ERROR merece um pouco
mais, 30 a 90 dias, por servir de evidência de incidentes recentes; e
log de AUDITORIA (autenticação, mudança de permissão) frequentemente
precisa de 1 a 7 ANOS por exigência regulatória — pagamento sob PCI DSS
exige pelo menos 1 ano, e dado de saúde sob HIPAA exige 6 anos. A
estratégia de "tiering" reflete essa diferença de urgência de acesso:
armazenamento HOT (SSD, busca rápida) para os últimos 7 dias, WARM (HDD,
busca mais lenta) para 7 a 30 dias, e COLD (algo como S3 Glacier) para
qualquer coisa além de 30 dias — dado raramente consultado não precisa
pagar o preço de armazenamento de acesso rápido. No ELK, o ILM (Index
Lifecycle Management) automatiza essa transição entre tiers sem
intervenção manual contínua.</p>
<div class="mermaid">
flowchart LR
    Hot["Hot: 7–30 dias"] --> Warm["Warm: ~90 dias"]
    Warm --> Cold["Cold / archive: 1 ano+"]
</div>


<h3>6. PII em log: um vazamento que já aconteceu no momento em que a linha foi escrita</h3>
<p>Um log contendo CPF, e-mail em claro ou token de acesso não é só um
risco de segurança abstrato — é um problema concreto em várias frentes
simultâneas: sob LGPD/GDPR, pode constituir um vazamento de dado pessoal
por si só; se o log é enviado a um SIEM ou plataforma SaaS de terceiro
(Datadog, Splunk), o dado sensível agora está fisicamente presente em
infraestrutura de outra empresa; backups replicam esse dado sensível em
múltiplos lugares adicionais, cada um uma superfície de exposição extra;
e o princípio mais desconfortável de todos: uma vez logado, o dado
permanece logado — apagar retroativamente de todos os sistemas
downstream (backup, réplica, cache) raramente é trivial. A sanitização
precisa acontecer em CAMADAS: na aplicação, nunca logar o valor sensível
diretamente — usar funções dedicadas como <code>mask_email()</code> ou
<code>hash_user_id()</code> antes mesmo de chamar o logger; no coletor,
filtros que detectam e removem padrões conhecidos (regex de CPF, de
número de cartão) como uma segunda linha de defesa; e no estágio de
pré-ingestão, uma ferramenta como Vector com sua linguagem VRL pode
transformar o dado antes dele chegar ao armazenamento definitivo:</p>
<pre><code># Vector VRL para sanitize
transforms.sanitize_pii:
  type: remap
  inputs: [logs_in]
  source: |
    .message = redact(.message, filters: [\\
      {"type": "pattern", "patterns": [r'\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}']},\\
      {"type": "pattern", "patterns": [r'\\d{16}']}\\
    ])
    if exists(.user.email) {
      .user.email_hash = sha2(string!(.user.email), "SHA-256")
      del(.user.email)
    }</code></pre>
<p>Uma lista curta do que NUNCA deveria aparecer em log, sob nenhuma
circunstância: senha, token ou segredo de qualquer natureza; número de
cartão de crédito ou CVV; CPF/SSN/RG sem mascaramento; JWT ou cookie de
sessão; o cabeçalho <code>Authorization</code> completo; e o corpo
inteiro de uma requisição em rotas que lidam com dado sensível.</p>

<h3>7. Sampling: manter o sinal relevante, descartar o volume que não agrega</h3>
<p>Em log de nível DEBUG, amostrar 1% a 10% do volume total costuma
preservar sinal suficiente para debug, mantendo custo de armazenamento
controlado — enquanto log de ERROR deveria ser preservado a 100%, já que
cada ocorrência individual pode ser o único registro de um incidente
específico. Em traces (detalhado na aula de Observabilidade Avançada), o
mesmo princípio se aplica com nuance: "head sampling" de 1% do tráfego
total, combinado com "tail sampling" garantindo 100% de captura para
erros e requisições lentas especificamente — o padrão que prioriza
justamente os casos raros e caros de perder. Sampling dinâmico baseado
em custo ajusta essa taxa automaticamente conforme o orçamento de
observabilidade disponível.</p>

<h3>8. Os três pilares, e por que log sozinho não conta a história inteira</h3>
<table>
<tr><th>Sinal</th><th>Responde</th><th>Custo típico</th></tr>
<tr><td>Logs</td><td>O que aconteceu (eventos)</td><td>Alto (volume)</td></tr>
<tr><td>Métricas</td><td>Quanto/com que frequência</td><td>Baixo (agregação)</td></tr>
<tr><td>Traces</td><td>Qual fluxo (entre serviços)</td><td>Médio (com sampling)</td></tr>
</table>
<p>Um <code>trace_id</code> compartilhado entre os três sinais é o que
permite SALTAR de um para o outro durante uma investigação — ver um pico
de erro numa métrica, filtrar os logs daquele intervalo específico pelo
mesmo <code>trace_id</code>, e de lá pular direto para a árvore de spans
que mostra exatamente onde o tempo foi gasto ou onde a falha ocorreu.
OpenTelemetry padroniza essa correlação numa coleta única, em vez de
cada sinal vivendo em ferramentas isoladas sem conexão entre si:</p>
<pre><code># Em log
{"event":"order_placed","trace_id":"abc-123",...}

# Em métrica (exemplar do Prometheus)
http_request_duration_seconds_bucket{...} 0.42 # exemplar trace_id=abc-123

# Em trace
trace_id=abc-123 → vê spans dos serviços envolvidos</code></pre>

<h3>9. Uma stack moderna recomendada, peça por peça</h3>
<p>Para logs, Loki quando custo é a prioridade, ou OpenSearch quando
busca rica de texto importa mais que economia. Para métricas, Prometheus
com Grafana como visualização, o par mais estabelecido do ecossistema
cloud-native. Para traces, Jaeger ou Tempo alimentados por
instrumentação OpenTelemetry. Para coleta, o OTel Collector (multi-sinal
nativo) ou Vector (mais flexível para transformação complexa via VRL).
Grafana como camada de visualização ÚNICA permite consultar logs,
métricas e traces na mesma interface, sem alternar entre ferramentas
diferentes durante uma investigação. E Alertmanager integrado a
PagerDuty ou Opsgenie fecha o ciclo, transformando uma condição
detectada em notificação para um humano responder.</p>

<h3>10. Nove anti-padrões que aparecem repetidamente em operações de log mal desenhadas</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Anti-padrão</strong><p>Log em arquivo no container, texto livre, PII sem redaction.</p></div>
    <div class="lesson-viz-card"><strong>Padrão saudável</strong><p>Stdout JSON, agente dedicado, retenção por tier.</p></div>
  </div>
  <figcaption>Logging centralizado começa no formato e no destino, não no dashboard.</figcaption>
</figure>

<ul>
<li><strong>Log em arquivo dentro do container</strong>: nenhuma
ferramenta de coleta externa o vê por padrão.</li>
<li><strong>Texto livre não-estruturado</strong>: ilegível por máquina,
força busca frágil por substring.</li>
<li><strong>PII em log</strong>: um risco legal e de segurança
concreto, detalhado na seção 6.</li>
<li><strong>Cardinalidade alta em labels do Loki</strong>: explode o
índice exatamente como descrito na seção 4.</li>
<li><strong>Retenção "para sempre" sem categorização</strong>: custo de
armazenamento cresce sem limite e sem justificativa proporcional ao
valor do dado retido.</li>
<li><strong>Sem ID de correlação</strong>: investigar um incidente
distribuído vira trabalho de detetive sem nenhuma pista compartilhada
entre serviços.</li>
<li><strong>`print()` em vez de logger estruturado</strong>: sem nível,
sem JSON, sem nenhum dos campos padrão da seção 2.</li>
<li><strong>Logar tudo em nível DEBUG em produção</strong>: ruído
excessivo mascarando o que realmente importa, além do custo direto de
armazenamento desnecessário.</li>
<li><strong>Stack trace completo devolvido ao usuário final</strong>:
vaza detalhe interno de implementação, o mesmo problema abordado na aula
de API Security.</li>
</ul>"""
                ),
                "body_en": (
                """<h3>1. Common stacks: each solves the same problem with a different trade-off</h3>
<table>
<tr><th>Stack</th><th>Componentes</th><th>Notas</th></tr>
<tr><td>ELK</td><td>Elasticsearch + Logstash + Kibana</td><td>Maduro, poderoso. Caro em escala (RAM-hungry).</td></tr>
<tr><td>EFK</td><td>Elasticsearch + Fluentd/Bit + Kibana</td><td>Logstash → Fluent (mais leve).</td></tr>
<tr><td>OpenSearch</td><td>Fork ASL2 do ES</td><td>Após mudança de licença ES (2021).</td></tr>
<tr><td>Grafana Loki</td><td>Loki + Promtail/Vector + Grafana</td><td>Indexa só labels. Custo &lt;&lt; ELK.</td></tr>
<tr><td>Datadog/Splunk/New Relic</td><td>SaaS</td><td>UX top, $ alto, retenção limitada.</td></tr>
<tr><td>VictoriaLogs</td><td>OSS, eficiente</td><td>Performance forte, ainda jovem.</td></tr>
</table>
<p>The choice between them is rarely about which is "better" in the
abstract — it is about where the team wants to pay the cost. ELK/EFK
deliver powerful full-text search, at the price of indexing EVERYTHING
(expensive in RAM and disk at high volume). Loki radically inverts that
trade (detailed in section 4), indexing only metadata and compressing
the rest — much cheaper, but with slower content search. OpenSearch is
the ASL2 fork of Elasticsearch. And SaaS options (Datadog, Splunk,
CloudWatch Logs, Grafana Cloud) trade operational cost for invoice
cost.</p>
<div class="mermaid">
flowchart TB
    Apps["Services"] --> Elk["ELK / OpenSearch"]
    Apps --> Loki["Grafana Loki"]
    Apps --> Cloud["CloudWatch / Stackdriver"]
</div>


<h3>2. Structured logs: free text is for humans to read, JSON is for machines to query</h3>
<p>A free-text log is easy to write and illegible for a tool searching
by a specific field — the only way to "query" is grep by substring,
fragile to any format change:</p>
<pre><code># RUIM
[2024-04-25 10:30:15] INFO User 123 placed order 456 for $99.50

# BOM
{"ts":"2024-04-25T10:30:15Z","level":"info","service":"orders",
 "event":"order_placed","user_id":"u_123","order_id":"o_456",
 "amount":99.50,"currency":"USD","trace_id":"abc-123",
 "span_id":"span-xyz"}</code></pre>
<p>With single-line JSON (NDJSON), querying "all orders above $100 that
failed in the payment service" becomes a structured field query, not a
regular expression trying to guess where the value sits in the string. A
standard set of fields is worth adopting consistently across the
organization: <code>ts</code> in ISO 8601 UTC with explicit timezone;
<code>level</code> following the debug/info/warn/error/critical scale;
<code>service</code>, <code>env</code>, <code>trace_id</code>,
<code>request_id</code>; and a hashed <code>user_id</code> when needed.</p>
<pre><code>import structlog
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.contextvars.merge_contextvars,
        structlog.processors.JSONRenderer(),
    ],
)
log = structlog.get_logger()

log.info('order_placed', user_id=user.id_hash, order_id=order.id, amount=99.50)
# {"event":"order_placed","timestamp":"...","level":"info",...}</code></pre>

<h3>3. Collection: from the application to the backend, through a dedicated agent</h3>
<p>Following the 12-factor principle (Docker Fundamentals lesson), the
application writes to stdout, and it is the responsibility of a separate
COLLECTOR (running as a DaemonSet in Kubernetes, or an agent on the host)
to read that stream and forward it to the storage backend. Each collector
has a different trade-off profile:</p>
<table>
<tr><th>Coletor</th><th>Linguagem</th><th>Notas</th></tr>
<tr><td>Fluentd</td><td>Ruby</td><td>Veterano, plugins ricos.</td></tr>
<tr><td>Fluent Bit</td><td>C</td><td>Mais leve; default em K8s.</td></tr>
<tr><td>Vector</td><td>Rust</td><td>Performant, VRL para transformações.</td></tr>
<tr><td>Promtail</td><td>Go</td><td>Específico para Loki.</td></tr>
<tr><td>OTel Collector</td><td>Go</td><td>Multi-signal (logs+metrics+traces).</td></tr>
<tr><td>Logstash</td><td>JVM</td><td>Pesado; legado.</td></tr>
</table>
<p>Fluent Bit became the de facto standard in Kubernetes precisely
because it runs in C — a memory footprint small enough to run as a
DaemonSet on EVERY node without competing for resources with real
workloads. A typical configuration reads container log files, enriches
with Kubernetes metadata (namespace, pod name), and forwards to a backend
like Loki:</p>
<pre><code># Fluent Bit em K8s (DaemonSet), config
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            docker
    DB                /var/log/flb_kube.db
    Tag               kube.*
[FILTER]
    Name              kubernetes
    Match             kube.*
    Merge_Log         On
[FILTER]
    Name              modify
    Match             kube.*
    Remove            stream
[OUTPUT]
    Name              loki
    Match             kube.*
    Host              loki.observability
    Labels            $kubernetes['namespace_name'],$kubernetes['pod_name']</code></pre>

<h3>4. Loki: cheap because it indexes only the label, not the content</h3>
<p>Loki's structural difference from Elasticsearch is the central design
decision: Loki does NOT index log content — it indexes only LABELS
(key-value pairs), while raw content is compressed and read on demand
when a specific query needs it. That choice is what makes Loki's
operating cost drastically lower than ELK at high volumes — the index
stays small even with terabytes of content.</p>
<pre><code># Filtro por labels + texto
{namespace="prod", service="api"} |= "error" | json | status &gt;= 500

# Métricas a partir de logs
rate({namespace="prod"} |= "error" [5m])

# p99 latency dos logs
quantile_over_time(0.99, {service="api"} | json | unwrap latency_ms [5m])</code></pre>
<p>The most critical care when operating Loki: NEVER use a high-
cardinality identifier (<code>user_id</code>, <code>request_id</code>)
as a label — each distinct label value becomes a separate index series,
and a unique identifier per request explodes the index to a size as large
as the problem Loki was specifically chosen to avoid.</p>

<h3>5. Retention and tiering: not every log deserves the same lifetime</h3>
<p>Logs grow fast — easily terabytes per month in a medium-traffic
application — and retaining everything indefinitely in the same expensive
storage tier is waste. A sensible policy varies by category: DEBUG logs
rarely need more than a few days (3 to 7); INFO logs typically 14 to 30
days; ERROR logs deserve a bit more, 30 to 90 days, as evidence of recent
incidents; and audit/compliance logs may need 1+ year depending on the
sector. Hot/warm/cold/archive tiering moves older data to cheaper
storage automatically.</p>
<div class="mermaid">
flowchart LR
    Hot["Hot: 7–30 days"] --> Warm["Warm: ~90 days"]
    Warm --> Cold["Cold / archive: 1 year+"]
</div>


<h3>6. PII in logs: a leak that already happened the moment the line was written</h3>
<p>A log containing CPF, cleartext email, or an access token is not just
an abstract security risk — it is a concrete problem on several fronts at
once: under LGPD/GDPR, it can constitute a personal-data leak by itself;
if the log is sent to a third-party SIEM or SaaS platform (Datadog,
Splunk), the sensitive data is now physically present in another
company's infrastructure; backups replicate the problem; and an incident
response that dumps logs expands the blast radius further.</p>
<pre><code># Vector VRL para sanitize
transforms.sanitize_pii:
  type: remap
  inputs: [logs_in]
  source: |
    .message = redact(.message, filters: [\\
      {"type": "pattern", "patterns": [r'\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}']},\\
      {"type": "pattern", "patterns": [r'\\d{16}']}\\
    ])
    if exists(.user.email) {
      .user.email_hash = sha2(string!(.user.email), "SHA-256")
      del(.user.email)
    }</code></pre>
<p>A short list of what should NEVER appear in a log, under any
circumstance: password, token, or secret of any kind; credit-card number
or CVV; CPF/SSN/RG without masking; JWT or session cookie; the full
<code>Authorization</code> header; and the entire request body on routes
that handle sensitive data.</p>

<h3>7. Sampling: keep the relevant signal, discard volume that adds nothing</h3>
<p>At DEBUG level, sampling 1% to 10% of total volume usually preserves
enough signal for debugging while keeping storage cost controlled —
while ERROR logs should be preserved at 100%, since each individual
occurrence may be the only record of a specific incident. In traces
(detailed in the Advanced Observability lesson), the same principle
applies with nuance: "head sampling" decides at the start of the trace;
"tail sampling" keeps interesting traces (errors, slow ones) after the
fact.</p>

<h3>8. The three pillars, and why logs alone do not tell the whole story</h3>
<table>
<tr><th>Sinal</th><th>Responde</th><th>Custo típico</th></tr>
<tr><td>Logs</td><td>O que aconteceu (eventos)</td><td>Alto (volume)</td></tr>
<tr><td>Métricas</td><td>Quanto/com que frequência</td><td>Baixo (agregação)</td></tr>
<tr><td>Traces</td><td>Qual fluxo (entre serviços)</td><td>Médio (com sampling)</td></tr>
</table>
<p>A <code>trace_id</code> shared across the three signals is what lets
you JUMP from one to another during an investigation — see an error spike
in a metric, filter logs for that specific interval by the same
<code>trace_id</code>, and from there jump straight to the span tree that
shows exactly where time was spent or where the failure occurred.
OpenTelemetry standardizes that correlation in a vendor-neutral way.</p>
<pre><code># Em log
{"event":"order_placed","trace_id":"abc-123",...}

# Em métrica (exemplar do Prometheus)
http_request_duration_seconds_bucket{...} 0.42 # exemplar trace_id=abc-123

# Em trace
trace_id=abc-123 → vê spans dos serviços envolvidos</code></pre>

<h3>9. A recommended modern stack, piece by piece</h3>
<p>For logs, Loki when cost is the priority, or OpenSearch when rich
text search matters more than savings. For metrics, Prometheus with
Grafana as visualization, the most established pair in the cloud-native
ecosystem. For traces, Jaeger or Tempo fed by OpenTelemetry
instrumentation. For collection, the OTel Collector (native multi-signal)
or Vector (more flexible for complex transformation). And for alerting,
Grafana Alerting or Alertmanager tied to runbooks.</p>

<h3>10. Nine anti-patterns that show up repeatedly in poorly designed log operations</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Anti-pattern</strong><p>Log file in the container, free text, PII without redaction.</p></div>
    <div class="lesson-viz-card"><strong>Healthy pattern</strong><p>JSON stdout, dedicated agent, tiered retention.</p></div>
  </div>
  <figcaption>Centralized logging starts with format and destination, not the dashboard.</figcaption>
</figure>

<ul>
<li><strong>Log to a file inside the container</strong>: no external
collection tool sees it by default.</li>
<li><strong>Unstructured free text</strong>: machine-illegible,
forces fragile substring search.</li>
<li><strong>PII in logs</strong>: a concrete legal and security
risk, detailed in section 6.</li>
<li><strong>High cardinality in Loki labels</strong>: explodes the
index exactly as described in section 4.</li>
<li><strong>"Forever" retention without categorization</strong>: storage
cost grows without limit and without justification proportional to the
value of the retained data.</li>
<li><strong>No correlation ID</strong>: investigating a distributed
incident becomes detective work with no shared clue across services.</li>
<li><strong>`print()` instead of a structured logger</strong>: no level,
no JSON, none of the standard fields from section 2.</li>
<li><strong>Logging everything at DEBUG in production</strong>: excessive
noise masking what actually matters, plus the direct cost of unnecessary
storage.</li>
<li><strong>Full stack trace returned to the end user</strong>:
leaks internal implementation detail, the same problem covered in the
API Security lesson.</li>
</ul>"""
                ),
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Em Docker Compose, suba Loki + Promtail + Grafana.</li>"
                    "<li>Configure sua app para emitir JSON estruturado em stdout "
                    "(structlog/pino/logback-json).</li>"
                    "<li>Adicione campos: ts, level, service, trace_id, request_id, "
                    "user_id_hash.</li>"
                    "<li>Configure Promtail para coletar dos containers Docker.</li>"
                    "<li>No Grafana, configure datasource Loki e busque "
                    "<code>{service=\"api\"} | json | level=\"error\"</code>.</li>"
                    "<li>Implemente sanitização de PII (CPF, email) em VRL/Vector.</li>"
                    "<li>Adicione tracing com OpenTelemetry; correlacione log e trace "
                    "via trace_id.</li>"
                    "<li>Configure retenção: 7d hot.</li>"
                    "<li>Bonus: alertas em spike de erro 5xx via Grafana → Slack.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    '<p><strong>Complete hands-on exercise</strong>:</p><ol><li>In Docker Compose, bring up Loki + Promtail + Grafana.</li><li>Configure your app to emit structured JSON on stdout (structlog/pino/logback-json).</li><li>Add fields: ts, level, service, trace_id, request_id, user_id_hash.</li><li>Configure Promtail to collect from Docker containers.</li><li>In Grafana, configure the Loki datasource and search <code>{service="api"} | json | level="error"</code>.</li><li>Implement PII sanitization (CPF, email) in VRL/Vector.</li><li>Add tracing with OpenTelemetry; correlate log and trace via trace_id.</li><li>Configure retention: 7d hot.</li><li>Bonus: alerts on a 5xx error spike via Grafana → Slack.</li></ol>'
                ),
            },
            "materials": [
                m("Grafana Loki", "https://grafana.com/docs/loki/latest/", "docs", "", title_en='Grafana Loki', description_en=''),
                m("Elastic Stack", "https://www.elastic.co/guide/index.html", "docs", "", title_en='Elastic Stack', description_en=''),
                m("OpenSearch", "https://opensearch.org/docs/", "docs", "", title_en='OpenSearch', description_en=''),
                m("Vector", "https://vector.dev/docs/", "tool", "", title_en='Vector', description_en=''),
                m("Logstash", "https://www.elastic.co/guide/en/logstash/current/index.html", "docs", "", title_en='Logstash', description_en=''),
                m("OpenTelemetry Logs", "https://opentelemetry.io/docs/concepts/signals/logs/",
                  "docs", "", title_en='OpenTelemetry Logs', description_en=''),
            ],
            "questions": [
                q("Centralizar logs ajuda em:",
                  "Correlação de incidentes entre serviços.",
                  ["Aumentar a latência percebida entre os serviços.", "Substituir a necessidade de manter backup dos dados.", "Reduzir diretamente o custo de infraestrutura do time."],
                  "Permite seguir trace_id por 5 microsserviços em uma busca só.",
                  statement_en='Centralizing logs helps with:',
                  correct_en='Correlating incidents across services.',
                  wrong_en=['Increasing the latency perceived between services.', 'Replacing the need to keep data backups.', "Directly reducing the team's infrastructure cost."],
                  explanation_en='Lets you follow a trace_id across 5 microservices in a single search.'),
                q("Loki indexa:",
                  "Apenas labels, não o conteúdo do log.",
                  ["Grande parte do o conteúdo completo de cada linha de log.", "Só o timestamp de cada linha de log indexada.", "Só o nível de severidade de cada linha de log."],
                  "Por isso é barato. Conteúdo é comprimido e lido sob demanda. Queries por substring varrem.",
                  statement_en='Loki indexes:',
                  correct_en='Only labels, not the log content.',
                  wrong_en=['Most of the full content of every log line.', 'Only the timestamp of each indexed log line.', 'Only the severity level of each log line.'],
                  explanation_en="That's why it's cheap. Content is compressed and read on demand. Substring queries scan."),
                q("ELK stack contém:",
                  "Elasticsearch + Logstash + Kibana.",
                  ["Postgres, Redis e Mongo combinados num só stack.", "Docker, Kubernetes e Helm combinados num só stack.", "Apache, Nginx e HAProxy combinados num só stack."],
                  "Variantes: EFK (Fluentd no lugar de Logstash). OpenSearch é fork ASL2.",
                  statement_en='The ELK stack contains:',
                  correct_en='Elasticsearch + Logstash + Kibana.',
                  wrong_en=['Postgres, Redis and Mongo combined into one stack.', 'Docker, Kubernetes and Helm combined into one stack.', 'Apache, Nginx and HAProxy combined into one stack.'],
                  explanation_en='Variants: EFK (Fluentd instead of Logstash). OpenSearch is an ASL2 fork.'),
                q("Retenção precisa equilibrar:",
                  "Custo vs requisitos de compliance.",
                  ["Só a configuração de TLS usada na transmissão.", "Só o SLA acordado com o cliente final.", "Só o custo de armazenamento cobrado pelo provedor."],
                  "Audit logs em alguns setores precisam 1+ ano. Logs de debug raramente.",
                  statement_en='Retention needs to balance:',
                  correct_en='Cost vs compliance requirements.',
                  wrong_en=['Only the TLS configuration used in transmission.', 'Only the SLA agreed with the end customer.', 'Only the storage cost charged by the provider.'],
                  explanation_en='Audit logs in some sectors need 1+ year. Debug logs rarely do.'),
                q("Anonimização em logs:",
                  "Remover PII para reduzir risco em vazamentos.",
                  ["Substitui a necessidade de usar encryption nos dados.", "É uma prática proibida por qualquer regulação vigente.", "É totalmente opcional em qualquer contexto regulado."],
                  "Hash de email, mascarar CPF (***.***.123-45). LGPD/GDPR olham para isso.",
                  statement_en='Anonymization in logs:',
                  correct_en='Remove PII to reduce risk in breaches.',
                  wrong_en=['Replaces the need to use encryption on the data.', 'Is a practice forbidden by any current regulation.', 'Is totally optional in any regulated context.'],
                  explanation_en='Hash emails, mask CPF (***.***.123-45). LGPD/GDPR look at this.'),
                q("Vector é:",
                  "Pipeline de logs/metrics performant em Rust.",
                  ["Uma linguagem de programação criada pela Mozilla.", "Um tipo específico de cluster gerenciado do Kubernetes.", "Um banco de dados otimizado para série temporal."],
                  "Substitui Logstash e Fluentd com performance superior. VRL para transformações.",
                  statement_en='Vector is:',
                  correct_en='A high-performance logs/metrics pipeline in Rust.',
                  wrong_en=['A programming language created by Mozilla, a common shortcut that looks fine until production surprises you.', 'A specific type of managed Kubernetes cluster, which tends to fail quietly until someone audits the setup.', 'A database optimized for time series, an assumption that rarely survives the first real incident review.'],
                  explanation_en='Replaces Logstash and Fluentd with superior performance. VRL for transformations.'),
                q("Estruturar logs em JSON:",
                  "Permite buscar por campo.",
                  ["Apaga os timestamps de cada linha ao estruturar.", "Substitui a necessidade de coletar métricas.", "Aumenta em dez vezes o tamanho do arquivo de log."],
                  "Tamanho cresce ~30%, mas valor de query é incomparável.",
                  statement_en='Structuring logs as JSON:',
                  correct_en='Lets you search by field.',
                  wrong_en=['Deletes the timestamps of every line when structuring.', 'Replaces the need to collect metrics.', 'Increases the log file size tenfold.'],
                  explanation_en='Size grows ~30%, but query value is incomparable.'),
                q("Sampling:",
                  "Reduz volume preservando representatividade.",
                  ["Não tem efeito algum sobre o volume de dados.", "Substitui a necessidade de definir uma retenção.", "Aumenta o volume total de dados armazenados."],
                  "Em traces, sampling de 1-10% é comum. Em logs, sampling do INFO mantendo todos os ERROR.",
                  statement_en='Sampling:',
                  correct_en='Reduces volume while preserving representativeness.',
                  wrong_en=['Has no effect at all on data volume, a common shortcut that looks fine until production surprises you.', 'Replaces the need to define retention, which tends to fail quietly until someone audits the setup.', 'Increases the total volume of stored data, an assumption that rarely survives the first real incident review.'],
                  explanation_en='In traces, 1–10% sampling is common. In logs, sample INFO while keeping all ERROR.'),
                q("Tracing (distributed):",
                  "Complementa logs com fluxo entre serviços.",
                  ["Substitui por completo a necessidade de manter logs.", "Só funciona para aplicações rodando na web.", "Substitui a necessidade de coletar métricas."],
                  "Spans em árvore mostram tempo gasto em cada step. Combine com logs por trace_id.",
                  statement_en='Distributed tracing:',
                  correct_en='Complements logs with the flow across services.',
                  wrong_en=['Completely replaces the need to keep logs.', 'Only works for applications running on the web.', 'Replaces the need to collect metrics.'],
                  explanation_en='Tree-shaped spans show time spent in each step. Combine with logs via trace_id.'),
                q("Log com PII em CW:",
                  "Pode violar LGPD/GDPR, sanitize antes.",
                  ["Sem algum risco legal associado a essa prática.", "É uma prática necessária em qualquer cenário.", "Completamente imune a qualquer tipo de auditoria."],
                  "Mesmo logs internos podem ser exfiltrados. ANPD (BR) já multou por logs imprudentes.",
                  statement_en='A log with PII in CloudWatch:',
                  correct_en='Can violate LGPD/GDPR — sanitize first.',
                  wrong_en=['Has no legal risk associated with that practice.', 'Is a necessary practice in any scenario.', 'Completely immune to any kind of audit.'],
                  explanation_en='Even internal logs can be exfiltrated. ANPD (BR) has already fined for careless logs.'),
            ],
        },
    ],
}
