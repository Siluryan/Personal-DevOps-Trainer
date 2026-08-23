"""Fase 4, Containers e Modernização (Platform Engineering)."""
from ._helpers import m, q

PHASE4 = {
    "name": "Fase 4: Containers e Modernização (Platform Engineering)",
    "description": "O primeiro passo em direção aos microsserviços.",
    "topics": [
        # =====================================================================
        # 4.1 Docker Fundamentals
        # =====================================================================
        {
            "title": "Docker Fundamentals",
            "summary": "Como empacotar sua aplicação e dependências.",
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
            },
            "materials": [
                m("Docker Get Started", "https://docs.docker.com/get-started/", "docs", ""),
                m("Best practices for Dockerfiles", "https://docs.docker.com/build/building/best-practices/", "docs", ""),
                m("Play with Docker", "https://labs.play-with-docker.com/", "tool", ""),
                m("Buildpacks (alternativa)", "https://buildpacks.io/docs/", "docs", ""),
                m("dive (analisar imagem)", "https://github.com/wagoodman/dive", "tool", ""),
                m("12-Factor App", "https://12factor.net/", "article", "Princípios para apps em container."),
            ],
            "questions": [
                q("`docker run` faz:",
                  "Cria e inicia um container a partir de uma imagem.",
                  ["Faz build.", "Sobe registry.", "Apaga volume."],
                  "`docker run` = `docker create` + `docker start`. Para builds, é `docker build`."),
                q("Multi-stage build:",
                  "Permite usar imagem maior para build e menor para runtime.",
                  ["Aumenta tamanho.", "Apenas Python.", "Substitui CI."],
                  "Ex.: imagem com gcc só na fase de compilação; runtime tem só o binário."),
                q("Diferença entre image e container:",
                  "Imagem é o template (read-only); container é a instância em execução.",
                  ["São o mesmo.", "Imagem é volátil.", "Container é só estatístico."],
                  "Várias instâncias podem rodar a mesma imagem com configs diferentes (env, volumes)."),
                q("Volume serve para:",
                  "Persistir dados fora do ciclo de vida do container.",
                  ["Aumentar memória.", "Substituir DNS.", "Melhorar build."],
                  "Container pode ser destruído/recriado sem perder dados se eles estão em volume."),
                q("`COPY` vs `ADD`:",
                  "Prefira COPY; ADD tem comportamento extra (download/extract) que pode surpreender.",
                  ["São idênticos.", "ADD é melhor sempre.", "COPY é depreciado."],
                  "ADD baixa URL e extrai tar automaticamente, recursos perigosos sem necessidade na maioria dos casos."),
                q("Layer caching no Docker:",
                  "Reaproveita camadas inalteradas, ordem dos comandos importa.",
                  ["Não existe.", "Apenas em prod.", "Substitui registry."],
                  "Mudou uma camada? Todas após são invalidadas. Por isso copy de código vai por último."),
                q(".dockerignore evita:",
                  "Enviar arquivos desnecessários para o build context.",
                  ["Apaga arquivos.", "Reduz CPU.", "Substitui git ignore."],
                  "Sem ele, `docker build` envia o repo todo (.git, node_modules) ao daemon, lento e perigoso."),
                q("Por que NÃO usar latest em produção?",
                  "Falta rastreabilidade, pode mudar.",
                  ["Latest é mais lento.", "Latest não funciona.", "Latest exige licença."],
                  "Em rollback você não consegue voltar 'para qual latest era ontem'. Use SHA ou semver."),
                q("Para aplicações stateless:",
                  "Containers facilitam escala horizontal.",
                  ["Containers atrapalham.", "É melhor VM.", "Não há vantagem."],
                  "Sem estado em disco local, basta subir mais réplicas. Estado vai para DB/cache externos."),
                q("Imagem de 1 GB para Python:",
                  "Provavelmente pode ser otimizada com multi-stage e base slim/alpine.",
                  ["Tamanho ideal.", "Menor que possível.", "Sempre necessário."],
                  "Imagem Python 3.12 normal é ~1GB; slim é ~150MB; distroless ~50MB."),
            ],
        },
        # =====================================================================
        # 4.2 Segurança de Imagens
        # =====================================================================
        {
            "title": "Segurança de Imagens",
            "summary": "Não usar imagens de fontes desconhecidas e reduzir o tamanho.",
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
                "body": (
                    "<h3>1. Princípio: minimalismo radical</h3>"
                    "<p>Toda biblioteca que você inclui é potencial bug. Toda binário "
                    "extra é potencial exploit. <em>Reduzir é segurança</em>. Imagem "
                    "Ubuntu padrão: ~28MB de pacotes + dezenas de daemons inativos + "
                    "shell + utilitários (apt, find, vim...). Imagem distroless: ~20MB "
                    "só com runtime + libs essenciais, sem shell, sem apt.</p>"
                    "<p>Espectro de bases (do maior ao menor):</p>"
                    "<table>"
                    "<tr><th>Base</th><th>Tamanho típico</th><th>Trade-off</th></tr>"
                    "<tr><td>ubuntu:22.04</td><td>~80MB</td><td>Familiar; muito que vc não usa.</td></tr>"
                    "<tr><td>debian:12</td><td>~120MB</td><td>Pacotes maduros.</td></tr>"
                    "<tr><td>debian:12-slim</td><td>~75MB</td><td>Sem doc, sem locales extras.</td></tr>"
                    "<tr><td>python:3.12-slim</td><td>~150MB</td><td>Slim + Python.</td></tr>"
                    "<tr><td>alpine:3.19</td><td>~7MB</td><td>musl libc; pode quebrar wheels Python.</td></tr>"
                    "<tr><td>wolfi-base (Chainguard)</td><td>~10MB</td><td>glibc, SBOM nativo, patches diários.</td></tr>"
                    "<tr><td>distroless/static</td><td>~2MB</td><td>Só libs. Sem shell. Bom para Go/Rust.</td></tr>"
                    "<tr><td>distroless/python</td><td>~50MB</td><td>Python runtime. Sem pip, sem shell.</td></tr>"
                    "<tr><td>scratch</td><td>0MB</td><td>Vazia. Você adiciona binário estático.</td></tr>"
                    "</table>"
                    "<h4>Distroless: o equilíbrio</h4>"
                    "<p>Imagens Google distroless contêm <em>apenas</em> a app e suas "
                    "dependências runtime. Sem <code>sh</code>, sem <code>apt</code>, "
                    "sem <code>cat</code>. Atacante que escapa do app não tem onde "
                    "rodar comando.</p>"
                    "<pre><code>FROM golang:1.22 AS builder\n"
                    "RUN CGO_ENABLED=0 go build -o /app ./cmd/app\n"
                    "\n"
                    "FROM gcr.io/distroless/static-debian12:nonroot\n"
                    "COPY --from=builder /app /app\n"
                    "ENTRYPOINT [\"/app\"]</code></pre>"
                    "<p>Trade-off: debug é menos confortável. Use <code>:debug</code> "
                    "tag em dev, <code>:nonroot</code> em prod.</p>"
                    "<h4>Wolfi e Chainguard</h4>"
                    "<p>Distro 'undistro' otimizada para containers: pacotes "
                    "assinados, glibc-based (compatível com mais ecossistemas que "
                    "alpine), SBOM gerado automaticamente, builds reprodutíveis. "
                    "Imagens Chainguard são patcheadas diariamente, você quase nunca "
                    "vê CVE 'velho' em base.</p>"

                    "<h3>2. Pin por digest, não só por tag</h3>"
                    "<p>Tag é mutável. <code>python:3.12-slim</code> hoje pode ser "
                    "outro digest amanhã (mantenedor republica). Pin por digest "
                    "garante reprodutibilidade absoluta:</p>"
                    "<pre><code>FROM python:3.12-slim@sha256:f0a1b2c3d4e5f6...\n"
                    "# Não:\n"
                    "# FROM python:3.12-slim\n"
                    "# FROM python:latest</code></pre>"
                    "<p>Renove digests com Renovate quando houver patch:</p>"
                    "<pre><code># renovate.json\n"
                    "{\n"
                    "  \"docker\": {\n"
                    "    \"pinDigests\": true,\n"
                    "    \"enabled\": true\n"
                    "  }\n"
                    "}</code></pre>"

                    "<h3>3. USER não-root + capabilities reduzidas</h3>"
                    "<p>Imagens Docker rodam como root por default. Se atacante "
                    "explora app, está como root <em>no namespace</em>, e em "
                    "configs sem user namespace mapping, é root no host.</p>"
                    "<pre><code>FROM python:3.12-slim\n"
                    "RUN groupadd -g 1000 app && useradd -u 1000 -g 1000 -m app\n"
                    "WORKDIR /app\n"
                    "COPY --chown=app:app . .\n"
                    "USER 1000:1000   # numérico funciona em K8s securityContext\n"
                    "CMD [\"python\", \"main.py\"]</code></pre>"
                    "<p>Em runtime, reduza capabilities:</p>"
                    "<pre><code># Docker\n"
                    "docker run \\\n"
                    "  --read-only \\\n"
                    "  --tmpfs /tmp \\\n"
                    "  --cap-drop=ALL \\\n"
                    "  --cap-add=NET_BIND_SERVICE \\\n"
                    "  --security-opt=no-new-privileges \\\n"
                    "  --user 1000:1000 \\\n"
                    "  myapp\n"
                    "\n"
                    "# Kubernetes securityContext\n"
                    "spec:\n"
                    "  securityContext:\n"
                    "    runAsNonRoot: true\n"
                    "    runAsUser: 1000\n"
                    "    fsGroup: 1000\n"
                    "    seccompProfile: { type: RuntimeDefault }\n"
                    "  containers:\n"
                    "    - name: app\n"
                    "      securityContext:\n"
                    "        readOnlyRootFilesystem: true\n"
                    "        allowPrivilegeEscalation: false\n"
                    "        capabilities:\n"
                    "          drop: [\"ALL\"]\n"
                    "          add: [\"NET_BIND_SERVICE\"]</code></pre>"
                    "<p>Se app não precisa bind em &lt;1024, sequer adicione "
                    "<code>NET_BIND_SERVICE</code>. Use porta 8080+.</p>"

                    "<h3>4. Scanning de vulnerabilidades</h3>"
                    "<p>Imagem inclui pacotes do SO (glibc, openssl) e libs da app "
                    "(django, lodash). Cada um tem CVEs conhecidos. Scanners cruzam "
                    "SBOM com NVD/OSV.</p>"
                    "<p>Ferramentas:</p>"
                    "<ul>"
                    "<li><strong>Trivy</strong>: gratuito, rápido, multi-target.</li>"
                    "<li><strong>Grype</strong>: pareado com Syft.</li>"
                    "<li><strong>Snyk</strong>: comercial freemium; sugere fix.</li>"
                    "<li><strong>Docker Scout</strong>: integrado ao Docker Desktop.</li>"
                    "<li><strong>ECR Enhanced/Inspector</strong>, <strong>Harbor</strong>: scan no registry.</li>"
                    "</ul>"
                    "<pre><code># CI: falha se CVE crítico\n"
                    "$ trivy image --severity CRITICAL --exit-code 1 myapp:dev\n"
                    "\n"
                    "# Re-scan periódico no registry detecta CVEs novos\n"
                    "$ trivy image --severity HIGH,CRITICAL myapp:v1.4.2\n"
                    "\n"
                    "# Ignorar específicos com motivo\n"
                    "$ cat .trivyignore\n"
                    "CVE-2024-12345  # não exploitable em nosso uso, ver ADR-42\n"
                    "\n"
                    "# Gerar SBOM\n"
                    "$ trivy image --format cyclonedx --output sbom.json myapp:dev</code></pre>"
                    "<p>Política de bloqueio típica:</p>"
                    "<ul>"
                    "<li>CRITICAL: bloqueia.</li>"
                    "<li>HIGH com fix disponível: bloqueia.</li>"
                    "<li>HIGH sem fix: ticket, prazo SLA.</li>"
                    "<li>MEDIUM/LOW: backlog.</li>"
                    "</ul>"

                    "<h3>5. Assinatura: Cosign + Sigstore</h3>"
                    "<p>Sem assinatura, atacante que comprometa o registry pode trocar "
                    "imagem. Cosign assina (com chave ou OIDC keyless), Rekor (Sigstore) "
                    "registra em transparency log público.</p>"
                    "<pre><code># Sign no CI (OIDC keyless, sem chave armazenada)\n"
                    "$ cosign sign --yes ghcr.io/empresa/app@$DIGEST\n"
                    "\n"
                    "# Verify\n"
                    "$ cosign verify ghcr.io/empresa/app:v1.4.2 \\\n"
                    "    --certificate-identity ci@empresa.com \\\n"
                    "    --certificate-oidc-issuer https://token.actions.githubusercontent.com</code></pre>"
                    "<p>Em K8s, admission controller (Kyverno, Connaisseur, Sigstore "
                    "Policy Controller) rejeita imagens não assinadas:</p>"
                    "<pre><code>apiVersion: kyverno.io/v1\n"
                    "kind: ClusterPolicy\n"
                    "metadata: { name: signed-images-only }\n"
                    "spec:\n"
                    "  validationFailureAction: Enforce\n"
                    "  rules:\n"
                    "    - name: verify-signature\n"
                    "      match:\n"
                    "        any: [{ resources: { kinds: [Pod] } }]\n"
                    "      verifyImages:\n"
                    "        - imageReferences: ['ghcr.io/empresa/*']\n"
                    "          attestors:\n"
                    "            - keyless: { subject: ci@empresa.com }</code></pre>"

                    "<h3>6. SBOM e atestados (provenance)</h3>"
                    "<p>SBOM = ingredientes da imagem. Anexe ao registry como "
                    "<code>referrer</code>:</p>"
                    "<pre><code>$ syft myapp:dev -o cyclonedx-json &gt; sbom.json\n"
                    "$ cosign attach sbom --sbom sbom.json myapp:dev\n"
                    "$ cosign attest --predicate sbom.json --type cyclonedx myapp:dev</code></pre>"
                    "<p>Quando próxima Log4Shell aparecer, você consulta SBOM por "
                    "imagem e sabe em segundos se tem o pacote vulnerável.</p>"
                    "<p>SLSA provenance: atestado de como foi construído. Github "
                    "Actions com slsa-framework gera nível 3 (builder confiável):</p>"
                    "<pre><code>jobs:\n"
                    "  build:\n"
                    "    uses: slsa-framework/slsa-github-generator/.github/workflows/builder_container_slsa3.yml@v1.10.0\n"
                    "    with:\n"
                    "      image: ghcr.io/empresa/app\n"
                    "      digest: ${{ needs.build.outputs.digest }}</code></pre>"

                    "<h3>7. Dockerfile securo: checklist</h3>"
                    "<pre><code># 1. Base mínima e pinada por digest\n"
                    "FROM python:3.12-slim@sha256:abc123...\n"
                    "\n"
                    "# 2. Não cachear apt; clean lists\n"
                    "RUN apt-get update && apt-get install -y --no-install-recommends \\\n"
                    "      libpq5 && \\\n"
                    "    rm -rf /var/lib/apt/lists/*\n"
                    "\n"
                    "# 3. Diretórios e usuário\n"
                    "RUN groupadd -g 1000 app && useradd -u 1000 -g 1000 -m app\n"
                    "WORKDIR /app\n"
                    "\n"
                    "# 4. Deps primeiro (camada cacheada)\n"
                    "COPY requirements.txt .\n"
                    "RUN pip install --no-cache-dir -r requirements.txt\n"
                    "\n"
                    "# 5. Código com ownership correto\n"
                    "COPY --chown=app:app . .\n"
                    "\n"
                    "# 6. Switch USER antes do CMD\n"
                    "USER 1000:1000\n"
                    "\n"
                    "# 7. Healthcheck\n"
                    "HEALTHCHECK --interval=30s CMD python -c \"import requests; requests.get('http://localhost:8000/health').raise_for_status()\"\n"
                    "\n"
                    "# 8. CMD em JSON form\n"
                    "CMD [\"gunicorn\", \"--bind\", \"0.0.0.0:8000\", \"app.wsgi\"]</code></pre>"

                    "<h3>8. Caso real: xz-utils backdoor (CVE-2024-3094)</h3>"
                    "<p>Em março de 2024, descobriu-se backdoor no xz-utils 5.6.0/5.6.1, "
                    "resultado de social engineering de mantenedor por &gt;2 anos. "
                    "Imagens 'rolling' (Debian testing, Fedora rawhide, alpine edge) já "
                    "tinham o pacote. Quem detectou primeiro? Devs com SBOMs e "
                    "monitoring de pacotes em uso. Quem foi pego cego? Quem usava "
                    "<code>FROM ubuntu:latest</code> sem SBOM.</p>"
                    "<p>Lições:</p>"
                    "<ul>"
                    "<li>Pin específico, evite <code>:latest</code> em prod.</li>"
                    "<li>SBOM permite resposta rápida a 'qual imagem tem isso?'.</li>"
                    "<li>Re-scan periódico em registry pega CVE pós-push.</li>"
                    "<li>Distros 'lentas' (Debian stable) raramente tinham as versões "
                    "vulneráveis, trade-off de fast vs stable.</li>"
                    "</ul>"

                    "<h3>9. Anti-patterns clássicos</h3>"
                    "<ul>"
                    "<li><strong>FROM ubuntu:18.04</strong> (EOL): sem patches.</li>"
                    "<li><strong>RUN curl ... | bash</strong>: sem verify; supply chain risk.</li>"
                    "<li><strong>USER root</strong> 'porque é mais fácil'.</li>"
                    "<li><strong>Senha em ENV</strong> no Dockerfile.</li>"
                    "<li><strong>Imagem com 200 CVEs</strong> de pacotes não-usados.</li>"
                    "<li><strong>chmod 777</strong> em diretórios.</li>"
                    "<li><strong>Bind mount de <code>/var/run/docker.sock</code></strong> no container.</li>"
                    "<li><strong>--privileged</strong> sem necessidade real.</li>"
                    "<li><strong>Imagens não-assinadas</strong> em produção.</li>"
                    "<li><strong>Sem retenção</strong>: registry cheio de imagens vulneráveis antigas.</li>"
                    "</ul>"
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
            },
            "materials": [
                m("Distroless", "https://github.com/GoogleContainerTools/distroless", "tool", ""),
                m("Trivy", "https://aquasecurity.github.io/trivy/", "tool", ""),
                m("Snyk: Container security", "https://snyk.io/learn/container-security/", "article", ""),
                m("Wolfi", "https://wolfi.dev/", "tool", "Distro otimizada para containers."),
                m("CIS Docker Benchmark", "https://www.cisecurity.org/benchmark/docker", "docs", ""),
                m("Chainguard images", "https://images.chainguard.dev/", "tool", "Imagens minimal com SBOM/Sigstore."),
            ],
            "questions": [
                q("Distroless serve para:",
                  "Imagens minimalistas, sem shell e package manager.",
                  ["Apenas Python.", "Maior performance.", "Aumentar logs."],
                  "Sem shell, atacante não tem como sair do container facilmente. Debug fica menos confortável, trade-off."),
                q("Pin por digest sha256 garante:",
                  "Reprodutibilidade, mesma imagem sempre.",
                  ["Maior velocidade.", "Auto-renovação.", "TLS forte."],
                  "Tag pode ser sobrescrita; digest é hash do conteúdo, único."),
                q("Imagem alpine é:",
                  "Pequena, mas com musl libc, pode quebrar pacotes glibc.",
                  ["Idêntica a Debian.", "Sem libc.", "Sempre lenta."],
                  "Alguns wheels Python só vêm em manylinux (glibc). Mede antes de migrar."),
                q("Escanear imagem em CI:",
                  "Para pegar CVEs antes do push em registry.",
                  ["Apenas em prod.", "Não tem efeito.", "Substitui SAST."],
                  "Falha rápida no PR é melhor que descobrir CVE em produção."),
                q("Rodar como root no container:",
                  "Risco, escalada privilege se sair do container.",
                  ["Boa prática.", "Necessário sempre.", "Reduz CPU."],
                  "Container scape + root no host = comprometimento total. UserNS adiciona camada extra."),
                q("Capabilities padrão do Docker:",
                  "Devem ser reduzidas ao mínimo (drop ALL e add o que precisa).",
                  ["Devem ser ampliadas.", "São imutáveis.", "Não importam."],
                  "Padrão dá ~14 capabilities. App web normal precisa de zero (com porta >1024)."),
                q("Imagem de 4GB com vulnerabilidades:",
                  "Crie versão menor e escaneie regularmente.",
                  ["Tamanho ideal.", "Sem solução.", "Use sempre."],
                  "Cada MB que sobra é potencial CVE em pacote que a app nem usa."),
                q("Wolfi é:",
                  "Distro 'undistro' otimizada para SBOM e segurança.",
                  ["Container runtime.", "Substituto do Docker.", "Linter."],
                  "Mantida pela Chainguard. Pacotes assinados, glibc-based, com SBOM nativo."),
                q("Imutabilidade da imagem:",
                  "Mesmo digest = mesmo conteúdo.",
                  ["Pode mudar com tag.", "Sempre muda.", "Não existe."],
                  "Princípio que torna deploys reproduzíveis e rollbacks confiáveis."),
                q("Fix de CVE em imagem base:",
                  "Requer rebuild da imagem do app.",
                  ["Auto-aplica.", "Não é necessário.", "Apenas em K8s."],
                  "CVE foi corrigido no Debian 12.6? Você precisa rebuildar para herdar o patch."),
            ],
        },
        # =====================================================================
        # 4.3 Container Registry
        # =====================================================================
        {
            "title": "Container Registry",
            "summary": "Onde hospedar suas imagens Docker de forma privada.",
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
                "body": (
                    "<h3>1. Opções principais</h3>"
                    "<table>"
                    "<tr><th>Registry</th><th>Modelo</th><th>Notas</th></tr>"
                    "<tr><td>Docker Hub</td><td>SaaS público</td><td>Free com limites; bom para imagens base públicas. Em prod privado, pago.</td></tr>"
                    "<tr><td>AWS ECR</td><td>SaaS/IAM</td><td>Nativo AWS; integra com IAM, scan, lifecycle.</td></tr>"
                    "<tr><td>Google Artifact Registry (GAR)</td><td>SaaS/IAM</td><td>Multi-formato (Docker, Maven, npm, PyPI...).</td></tr>"
                    "<tr><td>Azure ACR</td><td>SaaS/IAM</td><td>Nativo Azure; tasks built-in para build.</td></tr>"
                    "<tr><td>GHCR</td><td>SaaS</td><td>Integrado a GitHub Actions (token automático). Free para públicos.</td></tr>"
                    "<tr><td>GitLab Registry</td><td>SaaS/Self</td><td>Integrado a GitLab CI.</td></tr>"
                    "<tr><td>Harbor</td><td>Self-hosted</td><td>OSS, RBAC, scan, replicação. Padrão K8s on-prem.</td></tr>"
                    "<tr><td>JFrog Artifactory</td><td>Self/SaaS</td><td>Multi-formato; veterano, caro.</td></tr>"
                    "<tr><td>Sonatype Nexus</td><td>Self/SaaS</td><td>OSS edition; multi-formato.</td></tr>"
                    "<tr><td>Quay (Red Hat)</td><td>SaaS/Self</td><td>Comercial; Project Quay open source.</td></tr>"
                    "</table>"

                    "<h3>2. Autenticação moderna</h3>"
                    "<p>Tokens estáticos (PAT, robot account) vazam. Prefira sempre "
                    "que possível:</p>"
                    "<h4>2.1 OIDC para CI</h4>"
                    "<pre><code># GitHub Actions → AWS ECR via OIDC (sem chave armazenada)\n"
                    "permissions:\n"
                    "  id-token: write\n"
                    "  contents: read\n"
                    "jobs:\n"
                    "  push:\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - uses: aws-actions/configure-aws-credentials@v4\n"
                    "        with:\n"
                    "          role-to-assume: arn:aws:iam::111:role/gh-pusher\n"
                    "          aws-region: us-east-1\n"
                    "      - uses: aws-actions/amazon-ecr-login@v2\n"
                    "      - run: |\n"
                    "          docker build -t $ECR/myapp:$SHA .\n"
                    "          docker push $ECR/myapp:$SHA</code></pre>"
                    "<h4>2.2 Workload Identity em K8s</h4>"
                    "<p>Pod assume role IAM via service account, sem chave montada. "
                    "ECR/GAR/ACR helpers fazem auth automaticamente.</p>"
                    "<h4>2.3 Image pull secret</h4>"
                    "<p>Para registry privado puxar em K8s, crie Secret tipo "
                    "<code>kubernetes.io/dockerconfigjson</code>:</p>"
                    "<pre><code>kubectl create secret docker-registry regcred \\\n"
                    "  --docker-server=ghcr.io \\\n"
                    "  --docker-username=ci-bot \\\n"
                    "  --docker-password=$TOKEN\n"
                    "\n"
                    "# Pod\n"
                    "spec:\n"
                    "  imagePullSecrets:\n"
                    "    - name: regcred\n"
                    "  containers:\n"
                    "    - name: app\n"
                    "      image: ghcr.io/empresa/myapp:v1.4.2</code></pre>"
                    "<p>Em escala, prefira External Secrets Operator que rotaciona "
                    "automaticamente.</p>"

                    "<h3>3. Tagging e imutabilidade</h3>"
                    "<h4>3.1 Estratégia de tags</h4>"
                    "<pre><code># Bom, múltiplas tags úteis para mesma imagem\n"
                    "ghcr.io/empresa/app:abc1234              # commit SHA (imutável de fato)\n"
                    "ghcr.io/empresa/app:v1.4.2               # semver (não sobrescreva!)\n"
                    "ghcr.io/empresa/app:v1.4                 # rolling, ok em dev\n"
                    "ghcr.io/empresa/app:dev                  # tip de branch dev\n"
                    "ghcr.io/empresa/app@sha256:f0a1b2...     # digest absoluto, gold standard</code></pre>"
                    "<p>Em prod, use SHA ou digest. <code>latest</code>/<code>dev</code> "
                    "tags <em>nunca</em> em manifests de prod.</p>"
                    "<h4>3.2 Habilitar tag immutability</h4>"
                    "<p>Configure no registry, uma tag não pode ser sobrescrita após "
                    "push. Evita 'alguém republicou v1.4.2 com fix' (e o cluster "
                    "rodando v1.4.2 antigo).</p>"
                    "<pre><code># ECR\n"
                    "aws ecr put-image-tag-mutability \\\n"
                    "  --repository-name myapp \\\n"
                    "  --image-tag-mutability IMMUTABLE\n"
                    "\n"
                    "# Harbor: project settings → Tag Immutability Rules\n"
                    "# ACR: az acr config repository --name myapp --immutability enabled</code></pre>"

                    "<h3>4. Retenção: o destino dos GBs</h3>"
                    "<p>Sem política, GBs viram TBs. Cada PR build é uma imagem; "
                    "retenção infinita inflaciona custo e mantém versões vulneráveis "
                    "antigas acessíveis.</p>"
                    "<pre><code># ECR lifecycle\n"
                    "{\n"
                    "  \"rules\": [\n"
                    "    {\n"
                    "      \"rulePriority\": 1,\n"
                    "      \"description\": \"Manter últimas 30 imagens semver\",\n"
                    "      \"selection\": {\n"
                    "        \"tagStatus\": \"tagged\",\n"
                    "        \"tagPrefixList\": [\"v\"],\n"
                    "        \"countType\": \"imageCountMoreThan\",\n"
                    "        \"countNumber\": 30\n"
                    "      },\n"
                    "      \"action\": { \"type\": \"expire\" }\n"
                    "    },\n"
                    "    {\n"
                    "      \"rulePriority\": 2,\n"
                    "      \"description\": \"Apagar untagged após 7d\",\n"
                    "      \"selection\": {\n"
                    "        \"tagStatus\": \"untagged\",\n"
                    "        \"countType\": \"sinceImagePushed\",\n"
                    "        \"countUnit\": \"days\",\n"
                    "        \"countNumber\": 7\n"
                    "      },\n"
                    "      \"action\": { \"type\": \"expire\" }\n"
                    "    }\n"
                    "  ]\n"
                    "}</code></pre>"

                    "<h3>5. Pull-through cache: rate-limit do Docker Hub</h3>"
                    "<p>Docker Hub limita 100 pulls/6h por IP anônimo, 200 para "
                    "autenticados free. Em CI corporativo com múltiplos jobs "
                    "simultâneos, isso paralisa.</p>"
                    "<p>Solução: configure registry interno como pull-through cache:</p>"
                    "<ul>"
                    "<li><strong>Harbor proxy cache</strong>: project como proxy de "
                    "Docker Hub/Quay/GHCR.</li>"
                    "<li><strong>ECR pull-through</strong>: configurável para Docker "
                    "Hub, Quay, GHCR, GitLab, Microsoft Container Registry, Kubernetes "
                    "registry.</li>"
                    "<li><strong>Artifactory remote</strong>: remote repo cacheia.</li>"
                    "</ul>"
                    "<p>Vantagens:</p>"
                    "<ul>"
                    "<li>Acelera builds (cache local).</li>"
                    "<li>Sobrevive a outage do upstream.</li>"
                    "<li>Auditoria: tudo passa por seu registry.</li>"
                    "<li>Possibilidade de scan/quarentena de imagens externas.</li>"
                    "</ul>"

                    "<h3>6. Scan contínuo</h3>"
                    "<p>Scan no push é insuficiente: CVEs novos aparecem depois. "
                    "Configure re-scan periódico:</p>"
                    "<ul>"
                    "<li><strong>Harbor</strong>: scan schedule diário.</li>"
                    "<li><strong>ECR Enhanced Scanning</strong> (Inspector): contínuo.</li>"
                    "<li><strong>Trivy operator</strong> em K8s: escaneia imagens em "
                    "uso e cria CRDs com achados.</li>"
                    "</ul>"
                    "<p>Webhook → Slack quando imagem em produção fica vulnerável "
                    "por CVE recém-descoberta.</p>"

                    "<h3>7. RBAC e segregação</h3>"
                    "<ul>"
                    "<li><strong>Write apenas CI</strong>, nunca dev direto.</li>"
                    "<li><strong>Read scoped</strong>: por equipe/produto.</li>"
                    "<li><strong>Multi-tenant</strong>: namespaces ou projetos.</li>"
                    "<li><strong>Pull em prod</strong>: pull-secret específico, não "
                    "credencial humana.</li>"
                    "<li><strong>OIDC &gt; tokens estáticos</strong>.</li>"
                    "<li><strong>Audit logs</strong>: registry registra quem puxou o "
                    "quê e quando. Vital em incidente.</li>"
                    "</ul>"

                    "<h3>8. Webhooks e GitOps</h3>"
                    "<p>Registry pode disparar webhook em push. Ferramentas:</p>"
                    "<ul>"
                    "<li><strong>Argo CD Image Updater</strong>: detecta nova versão e "
                    "atualiza manifest no Git automaticamente.</li>"
                    "<li><strong>Flux Image Automation</strong>: similar, parte do "
                    "Flux.</li>"
                    "<li><strong>Keel</strong>: específico para K8s.</li>"
                    "</ul>"
                    "<pre><code># Argo CD Image Updater annotations no manifest\n"
                    "metadata:\n"
                    "  annotations:\n"
                    "    argocd-image-updater.argoproj.io/image-list: app=ghcr.io/empresa/app\n"
                    "    argocd-image-updater.argoproj.io/app.update-strategy: semver\n"
                    "    argocd-image-updater.argoproj.io/app.allow-tags: regexp:^v[0-9]+\\.[0-9]+\\.[0-9]+$</code></pre>"

                    "<h3>9. Multi-arch e manifest list</h3>"
                    "<pre><code>$ docker buildx create --use\n"
                    "$ docker buildx build \\\n"
                    "    --platform linux/amd64,linux/arm64 \\\n"
                    "    --tag ghcr.io/empresa/app:v1.4.2 \\\n"
                    "    --push .</code></pre>"
                    "<p>Resultado: manifest list (índice multi-arch). Quando ARM "
                    "puxa, recebe arm64; AMD64 recebe amd64. Indispensável hoje "
                    "(Graviton, Apple Silicon, Raspberry Pi).</p>"

                    "<h3>10. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Tags mutáveis em prod</strong>: <code>latest</code>, "
                    "<code>main</code>, <code>dev</code>.</li>"
                    "<li><strong>Build em prod</strong>: 'rebuild lá' ≠ artefato testado.</li>"
                    "<li><strong>PAT eterno</strong> em CI: vaza, atacante puxa tudo. Use OIDC.</li>"
                    "<li><strong>Sem scan</strong>: imagens vulneráveis em produção sem alarme.</li>"
                    "<li><strong>Sem retenção</strong>: TBs acumulando, custo escalando.</li>"
                    "<li><strong>Imagens sem assinatura</strong>: supply chain fraca.</li>"
                    "<li><strong>Push direto humano</strong>: sem auditoria, sem trilha. Tudo via CI.</li>"
                    "<li><strong>Mistura prod e dev</strong> no mesmo namespace: blast radius alto.</li>"
                    "</ul>"
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
            },
            "materials": [
                m("Harbor", "https://goharbor.io/docs/", "tool", ""),
                m("AWS ECR", "https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html", "docs", ""),
                m("GHCR", "https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry", "docs", ""),
                m("Distribution (open source)", "https://distribution.github.io/distribution/", "tool", ""),
                m("Cosign", "https://docs.sigstore.dev/cosign/overview/", "tool", ""),
                m("Argo CD Image Updater", "https://argocd-image-updater.readthedocs.io/", "tool", ""),
            ],
            "questions": [
                q("Docker Hub público é:",
                  "Útil para imagens base, arriscado para imagens privadas.",
                  ["Sempre seguro.", "Free sempre.", "Substituto do GHCR."],
                  "Para imagem privada de empresa, use GHCR/ECR/Harbor."),
                q("Rate limit do Docker Hub:",
                  "Pode bloquear pulls em CI sem auth.",
                  ["Não existe.", "Apenas em prod.", "Substitui RBAC."],
                  "100 pulls/6h por IP anônimo. Mirror interno resolve."),
                q("Registry self-hosted:",
                  "Maior controle mas requer manutenção.",
                  ["Sempre menor custo.", "Sem manutenção.", "Auto-rotação."],
                  "Você cuida de upgrade, backup, HA. Em escala pequena, SaaS sai mais barato."),
                q("Promotion entre ambientes:",
                  "Promove a mesma imagem (digest) entre dev/stg/prod.",
                  ["Build novo em cada ambiente.", "Apenas latest.", "Sem versionamento."],
                  "Garante que o que passou em staging é o mesmo bit-a-bit que foi para prod."),
                q("Webhook em registry:",
                  "Dispara CI/CD quando imagem nova é publicada.",
                  ["Substitui IAM.", "Apaga imagens.", "Reduz custo."],
                  "Base para GitOps com Argo Image Updater ou Flux."),
                q("Cleanup policies:",
                  "Apagam imagens antigas/não usadas.",
                  ["Aumentam custo.", "Substituem RBAC.", "Bloqueiam pulls."],
                  "Mantenha tags semver e últimas N revisões; resto vai embora automaticamente."),
                q("Mirror de imagens públicas:",
                  "Reduz dependência externa e rate-limits.",
                  ["Aumenta latência sempre.", "Substitui CI.", "Quebra TLS."],
                  "Harbor proxy cache, ECR pull-through. Opera como CDN para suas imagens base."),
                q("Para autenticar de fora:",
                  "Use docker login com PAT/OIDC.",
                  ["Substitua DNS.", "Reinicie containerd.", "Use telnet."],
                  "Em CI moderno, OIDC > PAT. Tokens curtos > eternos."),
                q("Tag por commit SHA:",
                  "Garante rastreabilidade ao código exato.",
                  ["Não é seguro.", "Idêntico a latest.", "Depreciado."],
                  "Útil em incidentes: 'qual código estava rodando?' = mesma SHA do git."),
                q("Em registries SaaS:",
                  "Confie mas verifique, leia o shared responsibility.",
                  ["Não cobra.", "Imune a outage.", "Sem necessidade de RBAC."],
                  "Mesmo registries SaaS já tiveram outages globais. Tenha plano de continuidade."),
            ],
        },
        # =====================================================================
        # 4.4 Orquestração Simples
        # =====================================================================
        {
            "title": "Orquestração Simples",
            "summary": "Gerir múltiplos containers sem a complexidade total do K8s.",
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
                "body": (
                """<h3>1. Docker Compose: um único YAML declara toda a aplicação multi-container</h3>
<p>Compose descreve serviços, redes e volumes num arquivo declarativo —
<code>docker compose up</code> sobe tudo na ordem certa,
<code>docker compose down</code> desmonta. A versão atual é um plugin do
próprio CLI do Docker (comando <code>docker compose</code>, com espaço);
o binário separado antigo (<code>docker-compose</code>, com hífen) está
oficialmente fora de suporte:</p>
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
            },
            "materials": [
                m("Docker Compose", "https://docs.docker.com/compose/", "docs", ""),
                m("HashiCorp Nomad", "https://developer.hashicorp.com/nomad/docs", "docs", ""),
                m("Docker Swarm", "https://docs.docker.com/engine/swarm/", "docs", ""),
                m("Compose Spec", "https://compose-spec.io/", "docs", ""),
                m("Awesome Compose", "https://github.com/docker/awesome-compose", "tool", ""),
                m("Nomad vs K8s", "https://developer.hashicorp.com/nomad/docs/nomad-vs-kubernetes",
                  "article", ""),
            ],
            "questions": [
                q("Docker Compose é apropriado para:",
                  "Desenvolvimento e workloads simples.",
                  ["Substituto do K8s sempre.", "Sistemas distribuídos globais.", "Apenas Windows."],
                  "Em prod single-host, atende muitos casos. Para multi-host/HA real, use Swarm/Nomad/K8s."),
                q("Swarm e K8s diferem em:",
                  "Complexidade, K8s mais features e curva.",
                  ["Linguagem.", "Idioma.", "Cor."],
                  "K8s tem CRDs, operadores, ecossistema enorme. Swarm é mais simples, com menos features."),
                q("Healthcheck em Compose:",
                  "Define como saber se serviço está saudável.",
                  ["É opcional sem efeito.", "Substitui logs.", "Apaga container."],
                  "Permite usar `depends_on: condition: service_healthy` para esperar dependência ficar pronta."),
                q("Volumes nomeados em Compose:",
                  "Persistem dados gerenciados pelo Docker.",
                  ["Caminho absoluto sempre.", "Não persistem.", "Apenas RAM."],
                  "Sobrevivem a `docker compose down`. Use `down -v` para remover."),
                q("Network bridge default:",
                  "Permite comunicação entre containers da mesma rede.",
                  ["Bloqueia comunicação.", "Substitui DNS.", "Apenas IPv6."],
                  "Em user-defined bridge, containers se enxergam pelo nome (DNS interno)."),
                q("Compose v2 difere de v1:",
                  "É plugin do Docker CLI (`docker compose`), não binário separado.",
                  ["Mesma coisa.", "É grátis.", "Apenas em macOS."],
                  "v1 (`docker-compose`) está EOL. Use v2 sempre."),
                q("Para HA em Compose:",
                  "Use deploy.replicas em Swarm ou suba para K8s.",
                  ["Compose já faz HA.", "Não há HA.", "Apenas backup."],
                  "Compose puro é single-host. HA real exige Swarm mode ou K8s."),
                q("`depends_on` faz:",
                  "Define ordem de startup, mas não espera healthcheck por default.",
                  ["Espera tudo.", "Apenas testa.", "Apaga deps."],
                  "Para esperar saudável, use `condition: service_healthy` (Compose v2 spec)."),
                q("Override file:",
                  "Permite sobrepor configs por ambiente.",
                  ["Substitui o principal.", "Apaga rede.", "Apenas dev."],
                  "Chain: base.yml + override.yml combina; chave repetida sobrescreve."),
                q("Nomad pode rodar:",
                  "Containers, binários e VMs.",
                  ["Apenas Java.", "Apenas K8s.", "Apenas browser."],
                  "Drivers para Docker, exec (binário direto), java, qemu. Útil em ambientes legados."),
            ],
        },
        # =====================================================================
        # 4.5 SBOM
        # =====================================================================
        {
            "title": "Software Bill of Materials (SBOM)",
            "summary": "Criar a lista de 'ingredientes' do seu software.",
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
                "body": (
                    "<h3>1. O que é SBOM</h3>"
                    "<p>SBOM (Software Bill of Materials) é a lista detalhada de "
                    "<em>todos</em> os componentes que compõem um artefato:</p>"
                    "<ul>"
                    "<li>Nome e versão de cada dependência (direta e transitiva).</li>"
                    "<li>Hash do conteúdo (verificação de integridade).</li>"
                    "<li>Licença (compliance).</li>"
                    "<li>Supplier/origem.</li>"
                    "<li>Relacionamentos (X depende de Y).</li>"
                    "</ul>"
                    "<p>Mínimo viável definido pela NTIA (National Telecommunications "
                    "and Information Administration):</p>"
                    "<ul>"
                    "<li>Supplier name</li>"
                    "<li>Component name</li>"
                    "<li>Version</li>"
                    "<li>Other unique identifiers (PURL, CPE)</li>"
                    "<li>Dependency relationships</li>"
                    "<li>Author of SBOM data</li>"
                    "<li>Timestamp</li>"
                    "</ul>"

                    "<h3>2. Formatos</h3>"
                    "<table>"
                    "<tr><th>Formato</th><th>Origem</th><th>Foco</th></tr>"
                    "<tr><td>CycloneDX</td><td>OWASP</td><td>Segurança (vuln, VEX, attestations).</td></tr>"
                    "<tr><td>SPDX</td><td>Linux Foundation</td><td>Compliance/licenças. Padrão ISO/IEC 5962.</td></tr>"
                    "<tr><td>SWID</td><td>NIST</td><td>Identificação de software.</td></tr>"
                    "</table>"
                    "<p>Ambos CycloneDX e SPDX em JSON, XML, YAML, protobuf. "
                    "Conversores existem (SPDX ↔ CycloneDX).</p>"
                    "<p>Exemplo CycloneDX simplificado:</p>"
                    "<pre><code>{\n"
                    "  \"bomFormat\": \"CycloneDX\",\n"
                    "  \"specVersion\": \"1.5\",\n"
                    "  \"serialNumber\": \"urn:uuid:abc-123\",\n"
                    "  \"version\": 1,\n"
                    "  \"metadata\": {\n"
                    "    \"timestamp\": \"2025-04-25T16:30:00Z\",\n"
                    "    \"tools\": [{\"name\": \"syft\", \"version\": \"1.0.0\"}],\n"
                    "    \"component\": {\n"
                    "      \"type\": \"container\",\n"
                    "      \"name\": \"empresa/app\",\n"
                    "      \"version\": \"v1.4.2\"\n"
                    "    }\n"
                    "  },\n"
                    "  \"components\": [\n"
                    "    {\n"
                    "      \"type\": \"library\",\n"
                    "      \"name\": \"django\",\n"
                    "      \"version\": \"5.1.4\",\n"
                    "      \"purl\": \"pkg:pypi/django@5.1.4\",\n"
                    "      \"licenses\": [{\"license\": {\"id\": \"BSD-3-Clause\"}}],\n"
                    "      \"hashes\": [{\"alg\": \"SHA-256\", \"content\": \"...\"}]\n"
                    "    }\n"
                    "  ]\n"
                    "}</code></pre>"

                    "<h3>3. Geração: nunca à mão</h3>"
                    "<p>Gere SBOM no build, automaticamente:</p>"
                    "<h4>3.1 Syft (Anchore)</h4>"
                    "<p>O canivete suíço. Suporta dezenas de ecossistemas:</p>"
                    "<pre><code># De diretório\n"
                    "$ syft dir:. -o cyclonedx-json &gt; sbom.json\n"
                    "\n"
                    "# De imagem (sem rodar)\n"
                    "$ syft ghcr.io/empresa/app:v1.4.2 -o spdx-json &gt; sbom.spdx.json\n"
                    "\n"
                    "# De binário Go\n"
                    "$ syft ./bin/app -o cyclonedx-json\n"
                    "\n"
                    "# Saída tabular (humano)\n"
                    "$ syft myapp:dev\n"
                    "NAME              VERSION    TYPE\n"
                    "django            5.1.4      python\n"
                    "asgiref           3.8.1      python\n"
                    "openssl           3.1.5      deb\n"
                    "...</code></pre>"
                    "<h4>3.2 Trivy</h4>"
                    "<p>Gera SBOM enquanto faz vuln scan:</p>"
                    "<pre><code>$ trivy image --format cyclonedx --output sbom.json myapp:v1.4.2\n"
                    "$ trivy fs --format spdx-json --output sbom-source.json .</code></pre>"
                    "<h4>3.3 Tooling nativo de cada ecossistema</h4>"
                    "<pre><code>$ npm sbom --sbom-format=cyclonedx                # npm 10+\n"
                    "$ cargo cyclonedx                                 # Rust\n"
                    "$ mvn cyclonedx:makeAggregateBom                  # Java\n"
                    "$ python -m cyclonedx_py environment              # Python</code></pre>"
                    "<h4>3.4 cdxgen (OWASP)</h4>"
                    "<p>Suporta ecossistemas obscuros (PHP composer, .NET, GraalVM).</p>"

                    "<h3>4. Distribuição: SBOM viaja com o artefato</h3>"
                    "<h4>4.1 Anexar como referrer no registry OCI</h4>"
                    "<pre><code>$ syft myapp:v1.4.2 -o cyclonedx-json &gt; sbom.json\n"
                    "$ cosign attach sbom --sbom sbom.json myapp:v1.4.2\n"
                    "\n"
                    "# Como atestado assinado (mais robusto)\n"
                    "$ cosign attest --predicate sbom.json --type cyclonedx myapp:v1.4.2\n"
                    "\n"
                    "# Verificar atestados\n"
                    "$ cosign verify-attestation --type cyclonedx myapp:v1.4.2 \\\n"
                    "    --certificate-identity ci@empresa.com \\\n"
                    "    --certificate-oidc-issuer https://token.actions.githubusercontent.com</code></pre>"
                    "<h4>4.2 Como asset do release</h4>"
                    "<p>GitHub Release / GitLab Release com SBOM anexado. Útil para "
                    "binários standalone.</p>"
                    "<h4>4.3 Em compras públicas dos EUA</h4>"
                    "<p>Fornecedores federais devem entregar SBOM como parte do "
                    "Software Acquisition Process (SP 800-218 / SSDF). Outros "
                    "setores convergem.</p>"

                    "<h3>5. VEX (Vulnerability Exploitability eXchange)</h3>"
                    "<p>SBOM diz 'lib X versão Y está aqui'. Cruzar com NVD diz "
                    "'CVE existe'. Mas existe ≠ explorável. VEX é declaração assinada "
                    "que expressa exploitability:</p>"
                    "<pre><code>{\n"
                    "  \"vulnerabilities\": [\n"
                    "    {\n"
                    "      \"id\": \"CVE-2024-12345\",\n"
                    "      \"analysis\": {\n"
                    "        \"state\": \"not_affected\",\n"
                    "        \"justification\": \"vulnerable_code_not_in_execute_path\",\n"
                    "        \"detail\": \"Função vulnerável só é chamada com input "
                    "interno controlado, never user-supplied.\"\n"
                    "      },\n"
                    "      \"affects\": [{\"ref\": \"pkg:pypi/lib-x@1.2.3\"}]\n"
                    "    }\n"
                    "  ]\n"
                    "}</code></pre>"
                    "<p>Estados possíveis:</p>"
                    "<ul>"
                    "<li><code>not_affected</code>: explica por que.</li>"
                    "<li><code>affected</code>: trabalho em andamento.</li>"
                    "<li><code>fixed</code>: corrigido em versão X.</li>"
                    "<li><code>under_investigation</code>: em análise.</li>"
                    "</ul>"
                    "<p>Reduz fadiga de alertas. Padrões: CSAF (OASIS), CycloneDX VEX.</p>"

                    "<h3>6. Operacionalização: Dependency-Track</h3>"
                    "<p>SBOM por imagem é dado bruto. Operacionalizar exige plataforma "
                    "central que ingere SBOMs de todos os builds, cruza continuamente "
                    "com NVD/OSV/EPSS, alerta em CVEs novos e mostra dashboards.</p>"
                    "<p>Exemplo: <strong>Dependency-Track</strong> (OWASP, OSS):</p>"
                    "<ul>"
                    "<li>Recebe SBOMs via API.</li>"
                    "<li>Re-cruza periodicamente com bases de CVE.</li>"
                    "<li>Notifica em mudanças (CVE nova surge para projeto X).</li>"
                    "<li>Suporta VEX para reduzir ruído.</li>"
                    "<li>Métricas: vulnerabilidades por projeto, por severity.</li>"
                    "</ul>"
                    "<pre><code># CI: enviar SBOM ao Dependency-Track\n"
                    "$ curl -X POST https://dt.empresa.com/api/v1/bom \\\n"
                    "    -H \"X-Api-Key: $DT_TOKEN\" \\\n"
                    "    -F project=$PROJECT_UUID \\\n"
                    "    -F bom=@sbom.json</code></pre>"

                    "<h3>7. SBOM em código vs SBOM em build</h3>"
                    "<p>Diferenças:</p>"
                    "<ul>"
                    "<li><strong>Source SBOM</strong>: dependências do "
                    "<code>package.json</code>/<code>requirements.txt</code>. Não vê "
                    "linkagem estática, libs do SO.</li>"
                    "<li><strong>Build SBOM</strong>: extraído do binário/imagem. Vê "
                    "tudo. Mais completo.</li>"
                    "</ul>"
                    "<p>Boa prática: gere ambos. Source SBOM para shift-left (PR "
                    "valida deps); build SBOM para inventário em produção.</p>"

                    "<h3>8. Limitações de SBOM</h3>"
                    "<ul>"
                    "<li><strong>Compilação estática</strong>: Go binário pode "
                    "incluir lib sem registrar. Use <code>-buildvcs</code> e "
                    "ferramentas Go-aware.</li>"
                    "<li><strong>Minified JS</strong>: dependências obscurecidas; "
                    "use SBOM de pre-minify.</li>"
                    "<li><strong>Containers multi-stage</strong>: ferramentas "
                    "modernas inspecionam o resultado final.</li>"
                    "<li><strong>Linkagem dinâmica</strong> (libc, openssl): "
                    "Syft/Trivy detectam pacotes do SO.</li>"
                    "<li><strong>Forks com mods</strong>: aparece como o original; "
                    "scanner não sabe que vc patcheu localmente.</li>"
                    "</ul>"

                    "<h3>9. Pipeline com SBOM completo</h3>"
                    "<pre><code>name: build-sbom-sign\n"
                    "jobs:\n"
                    "  build:\n"
                    "    permissions: { id-token: write, contents: read, packages: write }\n"
                    "    outputs:\n"
                    "      digest: ${{ steps.push.outputs.digest }}\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - uses: docker/setup-buildx-action@v3\n"
                    "      - uses: docker/login-action@v3\n"
                    "        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }\n"
                    "      - id: push\n"
                    "        uses: docker/build-push-action@v5\n"
                    "        with:\n"
                    "          push: true\n"
                    "          tags: ghcr.io/empresa/app:${{ github.sha }}\n"
                    "      - name: Generate SBOM\n"
                    "        uses: anchore/sbom-action@v0\n"
                    "        with:\n"
                    "          image: ghcr.io/empresa/app@${{ steps.push.outputs.digest }}\n"
                    "          format: cyclonedx-json\n"
                    "          output-file: sbom.json\n"
                    "      - uses: sigstore/cosign-installer@v3\n"
                    "      - name: Sign image + attach SBOM as attestation\n"
                    "        run: |\n"
                    "          cosign sign --yes ghcr.io/empresa/app@${{ steps.push.outputs.digest }}\n"
                    "          cosign attest --yes --predicate sbom.json --type cyclonedx \\\n"
                    "            ghcr.io/empresa/app@${{ steps.push.outputs.digest }}\n"
                    "      - name: Send SBOM to Dependency-Track\n"
                    "        run: |\n"
                    "          curl -X POST https://dt.empresa.com/api/v1/bom \\\n"
                    "            -H \"X-Api-Key: $DT_API_KEY\" \\\n"
                    "            -F \"projectName=app\" \\\n"
                    "            -F \"projectVersion=${{ github.sha }}\" \\\n"
                    "            -F \"autoCreate=true\" \\\n"
                    "            -F \"bom=@sbom.json\"\n"
                    "        env: { DT_API_KEY: ${{ secrets.DT_API_KEY }} }</code></pre>"

                    "<h3>10. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>SBOM manual</strong>: desatualizado em horas.</li>"
                    "<li><strong>SBOM sem distribuição</strong>: arquivo em pasta morta.</li>"
                    "<li><strong>SBOM sem operacionalização</strong>: nunca consultado.</li>"
                    "<li><strong>SBOM apenas em build, não em uso</strong>: incidente "
                    "exige saber 'quem TEM isso rodando'.</li>"
                    "<li><strong>Sem VEX</strong>: alertas crescem até serem ignorados.</li>"
                    "<li><strong>Formato proprietário</strong>: prefira CycloneDX/SPDX.</li>"
                    "</ul>"
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
            },
            "materials": [
                m("CISA SBOM", "https://www.cisa.gov/sbom", "docs", ""),
                m("CycloneDX", "https://cyclonedx.org/specification/overview/", "docs", ""),
                m("SPDX", "https://spdx.dev/", "docs", ""),
                m("Syft", "https://github.com/anchore/syft", "tool", ""),
                m("VEX (CISA)", "https://www.cisa.gov/sites/default/files/2023-04/minimum-requirements-for-vex-508c.pdf", "docs", ""),
                m("Dependency-Track", "https://dependencytrack.org/", "tool",
                  "Plataforma OSS para SBOM ops."),
            ],
            "questions": [
                q("SBOM é:",
                  "Inventário detalhado de componentes do software.",
                  ["Linter.", "Backup.", "Tipo de TLS."],
                  "Inclui versão, supplier, hash. Permite responder 'tenho Log4j 2.14?' em segundos."),
                q("Formato aberto popular:",
                  "CycloneDX e SPDX.",
                  ["JSON Web Token.", "Apenas CSV.", "Markdown."],
                  "Os dois são padrões reconhecidos pelo NIST e usados pela CISA."),
                q("SBOM ajuda em:",
                  "Resposta rápida a CVEs.",
                  ["Marketing.", "Pricing.", "DNS."],
                  "Em Log4Shell, empresas com SBOM consultaram em segundos; o resto fez forensics manual."),
                q("VEX descreve:",
                  "Se uma vulnerabilidade afeta de fato seu produto.",
                  ["Versão do TLS.", "Tipo de log.", "Backup."],
                  "Reduz fadiga: 'CVE existe mas função não é alcançável no nosso uso'."),
                q("SBOM deve ser:",
                  "Legível por máquina, gerado automaticamente.",
                  ["Manual sempre.", "Em PDF apenas.", "Imutável humano."],
                  "Manual é desatualizado e impreciso. Geração no build é regra."),
                q("Syft gera SBOM de:",
                  "Imagens, diretórios, archives.",
                  ["Apenas Python.", "Apenas Docker.", "Apenas zip."],
                  "Suporta Python, Node, Java, Go, Rust, etc. Detecta ecossistema automaticamente."),
                q("Após Log4Shell, SBOM virou:",
                  "Requisito quase regulatório em muitos setores.",
                  ["Opção desnecessária.", "Apenas BR.", "Modal."],
                  "EO 14028 (EUA) tornou SBOM obrigatório para compras federais."),
                q("SBOM e SCA:",
                  "Complementares, SBOM é o inventário, SCA é a análise.",
                  ["Sinônimos.", "Concorrentes.", "Substitutos."],
                  "Trivy faz ambos. SBOM é o 'o quê'; SCA é 'tem CVE/EPSS no quê'."),
                q("Distribuir SBOM:",
                  "Junto do artefato, em registry OCI ou anexo do release.",
                  ["Apenas em e-mail.", "Manualmente.", "Não distribuir."],
                  "Cosign attach sbom anexa ao manifest no registry. Quem puxa a imagem pode puxar a SBOM."),
                q("SBOM sem governança é:",
                  "Arquivo morto, precisa rotina de uso.",
                  ["Inútil sempre.", "Auto-gerador.", "Substitui patch."],
                  "Sem ingestion (Dependency-Track) e alertas, SBOM fica esquecido."),
            ],
        },
        # =====================================================================
        # 4.6 IDP
        # =====================================================================
        {
            "title": "Internal Developer Platforms (IDP)",
            "summary": "Facilitar a vida do dev criando ferramentas self-service.",
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
                "body": (
                    "<h3>1. Por que IDP existe</h3>"
                    "<p>Empresa cresce. Cada time decide individualmente:</p>"
                    "<ul>"
                    "<li>Como fazer pipeline?</li>"
                    "<li>Como configurar logs/metrics?</li>"
                    "<li>Qual padrão de service mesh?</li>"
                    "<li>Como provisionar DB/bucket/queue?</li>"
                    "<li>Quem revisa segurança?</li>"
                    "</ul>"
                    "<p>Resultado: 50 jeitos diferentes. Manutenção explode. Onboarding "
                    "vira 3 meses. Segurança cobre uns 30%. Visibilidade zero entre "
                    "times.</p>"
                    "<p>Com IDP:</p>"
                    "<ul>"
                    "<li><strong>Golden paths</strong>: 'jeito recomendado' com "
                    "tudo pronto.</li>"
                    "<li><strong>Self-service</strong>: dev provisiona DB sem "
                    "ticket → 4 dias.</li>"
                    "<li><strong>Guard-rails embutidos</strong>: você não precisa "
                    "lembrar de habilitar encryption, já vem.</li>"
                    "<li><strong>Catálogo unificado</strong>: 'qual time é dono "
                    "do serviço X?' → 1 clique.</li>"
                    "<li><strong>Observability default</strong>: cada serviço novo "
                    "ganha dashboards e SLOs gratuitos.</li>"
                    "</ul>"

                    "<h3>2. Componentes típicos de uma IDP</h3>"
                    "<table>"
                    "<tr><th>Componente</th><th>O que faz</th><th>Ferramentas</th></tr>"
                    "<tr><td>Portal</td><td>UI única para devs</td><td>Backstage, Port, OpsLevel</td></tr>"
                    "<tr><td>Catálogo</td><td>Inventário de serviços/teams/APIs</td><td>Backstage Software Catalog</td></tr>"
                    "<tr><td>Templates/Scaffolder</td><td>Bootstrap padronizado de novos serviços</td><td>Backstage Scaffolder, Cookiecutter, Yeoman</td></tr>"
                    "<tr><td>Self-service infra</td><td>Provisão sem ticket</td><td>Crossplane, Humanitec, Terraform via TFC</td></tr>"
                    "<tr><td>Pipeline padrão</td><td>CI/CD reutilizável</td><td>GitHub Actions reusable workflows, GitLab include</td></tr>"
                    "<tr><td>Observability default</td><td>Dashboards/SLOs auto</td><td>Datadog APIs, Grafana provisioning</td></tr>"
                    "<tr><td>Docs/TechDocs</td><td>Docs as code</td><td>Backstage TechDocs, Docusaurus</td></tr>"
                    "<tr><td>Compliance/Policy</td><td>Guard-rails</td><td>OPA/Conftest, Kyverno, Sentinel</td></tr>"
                    "</table>"

                    "<h3>3. Backstage: o portal de fato</h3>"
                    "<p>Backstage é OSS criado pelo Spotify (2020), agora hosted pela "
                    "CNCF. Plugins para tudo: Kubernetes, GitHub, GitLab, Datadog, "
                    "Sentry, PagerDuty, Argo CD, Sonar, Jenkins, AWS, GCP, Azure...</p>"
                    "<h4>3.1 Software Catalog</h4>"
                    "<p>Modelo de entidades: Component, API, System, Resource, "
                    "Domain, Group, User. Relações: Component <em>ownedBy</em> Group, "
                    "<em>consumes</em> API, <em>partOf</em> System.</p>"
                    "<pre><code># catalog-info.yaml (no repo do serviço)\n"
                    "apiVersion: backstage.io/v1alpha1\n"
                    "kind: Component\n"
                    "metadata:\n"
                    "  name: orders-api\n"
                    "  description: API de pedidos\n"
                    "  annotations:\n"
                    "    backstage.io/techdocs-ref: dir:.\n"
                    "    github.com/project-slug: empresa/orders-api\n"
                    "    pagerduty.com/service-id: PXYZ123\n"
                    "    sentry.io/project-slug: orders-api\n"
                    "    grafana/dashboard-selector: \"folderTitle = 'Orders'\"\n"
                    "spec:\n"
                    "  type: service\n"
                    "  lifecycle: production\n"
                    "  owner: payments-team\n"
                    "  system: payments\n"
                    "  consumesApis:\n"
                    "    - users-api\n"
                    "  providesApis:\n"
                    "    - orders-api</code></pre>"
                    "<h4>3.2 Scaffolder (templates)</h4>"
                    "<p>Dev escolhe 'Criar novo microsserviço Python', preenche "
                    "form (nome, owner, dependências). Backstage:</p>"
                    "<ol>"
                    "<li>Cria repo no GitHub a partir de template.</li>"
                    "<li>Aplica Dockerfile, CI, observability, docs padrão.</li>"
                    "<li>Registra como Component no catalog.</li>"
                    "<li>Cria PagerDuty service.</li>"
                    "<li>Configura Sentry/Datadog.</li>"
                    "<li>Provisiona DB via Crossplane (opcional).</li>"
                    "</ol>"
                    "<pre><code># template.yaml\n"
                    "apiVersion: scaffolder.backstage.io/v1beta3\n"
                    "kind: Template\n"
                    "metadata: { name: python-service }\n"
                    "spec:\n"
                    "  parameters:\n"
                    "    - title: Service info\n"
                    "      properties:\n"
                    "        name: { title: Name, type: string }\n"
                    "        owner: { title: Owner, type: string, ui:field: OwnerPicker }\n"
                    "  steps:\n"
                    "    - id: fetch\n"
                    "      action: fetch:template\n"
                    "      input:\n"
                    "        url: ./skeleton\n"
                    "        values: { name: ${{ parameters.name }} }\n"
                    "    - id: publish\n"
                    "      action: publish:github\n"
                    "      input:\n"
                    "        repoUrl: github.com?owner=empresa&repo=${{ parameters.name }}\n"
                    "        defaultBranch: main\n"
                    "    - id: register\n"
                    "      action: catalog:register\n"
                    "      input:\n"
                    "        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}</code></pre>"
                    "<h4>3.3 TechDocs</h4>"
                    "<p>Docs em Markdown no próprio repo, renderizados em Backstage. "
                    "Sempre próximo ao código, atualizados em PR.</p>"

                    "<h3>4. Self-service de infra</h3>"
                    "<h4>4.1 Crossplane (K8s-native)</h4>"
                    "<p>Você define <em>Composite Resources</em> (XRD) e Composições "
                    "que abstraem cloud:</p>"
                    "<pre><code># XRD: API de alto nível 'Database'\n"
                    "apiVersion: apiextensions.crossplane.io/v1\n"
                    "kind: CompositeResourceDefinition\n"
                    "metadata: { name: xdatabases.platform.empresa.com }\n"
                    "spec:\n"
                    "  group: platform.empresa.com\n"
                    "  names: { kind: XDatabase, plural: xdatabases }\n"
                    "  claimNames: { kind: Database, plural: databases }\n"
                    "  versions:\n"
                    "    - name: v1\n"
                    "      schema:\n"
                    "        openAPIV3Schema:\n"
                    "          properties:\n"
                    "            spec:\n"
                    "              properties:\n"
                    "                size: { enum: [small, medium, large] }\n"
                    "                env: { enum: [dev, staging, prod] }\n"
                    "\n"
                    "# Composition: como traduzir para AWS RDS\n"
                    "# (omitido aqui, em prática, mapeia size→instance class etc.)\n"
                    "\n"
                    "# Dev consome:\n"
                    "apiVersion: platform.empresa.com/v1\n"
                    "kind: Database\n"
                    "metadata: { name: orders-db, namespace: payments }\n"
                    "spec:\n"
                    "  size: medium\n"
                    "  env: prod</code></pre>"
                    "<p>Dev viu 'small/medium/large + dev/staging/prod' e ganhou RDS "
                    "com encryption + backup + multi-AZ + VPC + secret manager + "
                    "monitoring tudo configurado.</p>"
                    "<h4>4.2 Humanitec</h4>"
                    "<p>SaaS comercial; 'workload definitions' YAML que dev escreve, "
                    "plataforma traduz para K8s/cloud específico. Trade-off: rápido "
                    "para começar, lock-in moderado.</p>"
                    "<h4>4.3 Terraform via TFC/Spacelift</h4>"
                    "<p>Para times Terraform-heavy: módulos da empresa expostos via "
                    "Terraform Cloud workspaces; dev preenche variables na UI, TFC "
                    "aplica. Backstage Scaffolder pode disparar.</p>"

                    "<h3>5. Team Topologies: organização que sustenta IDP</h3>"
                    "<p>Padrão de Manuel Pais e Matthew Skelton. 4 tipos de time:</p>"
                    "<ul>"
                    "<li><strong>Stream-aligned</strong>: time de produto, dono de "
                    "uma capability/jornada/cliente. Foca em delivery.</li>"
                    "<li><strong>Platform</strong>: constrói a IDP como produto "
                    "<em>interno</em>. Tem PM, UX, roadmap. Cliente é o stream-aligned "
                    "team.</li>"
                    "<li><strong>Enabling</strong>: consultoria interna. Ajuda "
                    "stream-aligned em dor temporária (ex.: novo paradigma de ML).</li>"
                    "<li><strong>Complicated subsystem</strong>: squad para problema "
                    "intrinsecamente complicado (engine, ML core, blockchain).</li>"
                    "</ul>"
                    "<p>Plataforma <em>como produto</em> é vital. Sem PM/UX, vira "
                    "ticket factory ou wrapper sem valor.</p>"

                    "<h3>6. Métricas de sucesso</h3>"
                    "<ul>"
                    "<li><strong>Time-to-first-deploy</strong> de novo serviço: "
                    "horas, não meses.</li>"
                    "<li><strong>% de novos serviços usando templates</strong>: alta "
                    "adoção indica produto desejável.</li>"
                    "<li><strong>NPS interno</strong> (devs satisfeitos com plataforma).</li>"
                    "<li><strong>Tickets para SRE</strong>: tendência decrescente.</li>"
                    "<li><strong>DORA metrics</strong>: melhoria pós-IDP.</li>"
                    "<li><strong>Time-to-restore</strong> em incidente: catálogo + "
                    "runbooks reduzem.</li>"
                    "</ul>"

                    "<h3>7. Anti-patterns clássicos</h3>"
                    "<ul>"
                    "<li><strong>Plataforma sem demanda</strong>: time constrói o que "
                    "ninguém usa. Resolve com discovery, MVPs.</li>"
                    "<li><strong>Plataforma controle-freak</strong>: bloqueia tudo, "
                    "vira gargalo. Devs criam shadow-IT em paralelo.</li>"
                    "<li><strong>Wrapper bonito sem valor</strong>: portal só esconde "
                    "clicar no console. Adicione abstração real.</li>"
                    "<li><strong>Sem ownership</strong>: ninguém mantém templates. "
                    "Trate plataforma como produto com PM dedicado.</li>"
                    "<li><strong>Tudo obrigatório</strong>: golden path sem escapes "
                    "para casos especiais frustra times maduros.</li>"
                    "<li><strong>Sem comunidade</strong>: plataforma é entrega "
                    "unilateral. Construa com guilds, office hours, RFCs.</li>"
                    "<li><strong>Métricas de vaidade</strong>: 'temos 50 plugins!' "
                    "sem medir adoção real.</li>"
                    "</ul>"

                    "<h3>8. Caso real: Spotify Backstage</h3>"
                    "<p>Spotify, ~6000 engenheiros. Tinha 4 portais internos diferentes. "
                    "Construiu Backstage internamente para unificar. Resultados:</p>"
                    "<ul>"
                    "<li>Onboarding: meses → semanas.</li>"
                    "<li>Time-to-first-deploy: 60d → 1d.</li>"
                    "<li>Adoção interna &gt;90% em 3 anos.</li>"
                    "<li>Open-source em 2020; CNCF incubation.</li>"
                    "</ul>"
                    "<p>Hoje: Netflix, American Airlines, HBO, Wayfair, Box rodam "
                    "Backstage internamente.</p>"

                    "<h3>9. Por onde começar</h3>"
                    "<ol>"
                    "<li>Identifique 3 dores reais dos devs (entrevistas).</li>"
                    "<li>Escolha 1: ex.: 'criar novo serviço leva 2 semanas'.</li>"
                    "<li>MVP: template + scaffolder + CI básico + dashboard padrão.</li>"
                    "<li>Adote em 1-2 squads piloto, meça.</li>"
                    "<li>Itere: ouve feedback, melhora.</li>"
                    "<li>Escale para outros squads.</li>"
                    "<li>Adicione novo recurso (self-service DB) só após o anterior "
                    "ser bem usado.</li>"
                    "</ol>"
                    "<p>Não tente construir 'a plataforma definitiva' em 1 ano. "
                    "Comece pequeno, prove valor, expanda.</p>"
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
            },
            "materials": [
                m("Backstage", "https://backstage.io/docs/overview/what-is-backstage", "docs", ""),
                m("Team Topologies", "https://teamtopologies.com/key-concepts", "article", ""),
                m("ThoughtWorks: IDPs", "https://www.thoughtworks.com/insights/articles/seismic-shift-in-platform-engineering", "article", ""),
                m("Humanitec", "https://humanitec.com/platform-orchestrator", "docs", ""),
                m("OSS Internal Dev Portal", "https://github.com/cnoe-io/idpbuilder", "tool", ""),
                m("Crossplane", "https://www.crossplane.io/", "tool", "Infra control plane K8s-native."),
            ],
            "questions": [
                q("IDP é:",
                  "Plataforma interna que abstrai infra para o dev.",
                  ["Apenas frontend.", "Apenas IAM.", "Modal de lint."],
                  "Não substitui infra; padroniza e expõe via UX/APIs amigáveis."),
                q("Golden path significa:",
                  "Caminho recomendado e padronizado para criar/operar serviços.",
                  ["Logo dourado.", "Tipo de TLS.", "Endpoint de IAM."],
                  "Dev pode sair do golden path com justificativa, mas tem que arcar com manutenção própria."),
                q("Backstage é:",
                  "Portal de devs OSS feito pelo Spotify.",
                  ["IDE proprietária.", "DNS server.", "Pipeline de CI."],
                  "Adotado por Spotify, Netflix, American Airlines, etc. Hospedado pela CNCF."),
                q("IDP visa:",
                  "Reduzir o custo cognitivo da operação.",
                  ["Aumentar burocracia.", "Reduzir testes.", "Centralizar storage."],
                  "Dev foca em código de negócio; plataforma cuida do resto."),
                q("Self-service em IDP:",
                  "Permite dev provisionar recursos sem ticket.",
                  ["Aumenta dependência de SRE.", "Acaba com testes.", "Substitui RBAC."],
                  "Com guard-rails (Policy as Code), risco fica baixo. Sem guard-rails, vira faroeste."),
                q("Templates em IDP:",
                  "Bootstrap padronizado de serviços.",
                  ["Reduzem qualidade.", "Substituem CI.", "Apagam segurança."],
                  "Garantem que cada novo serviço sai com Dockerfile, CI, monitoring, segurança alinhados."),
                q("Catálogo de serviços:",
                  "Inventário com dono, deps, dashboards.",
                  ["Substituto do Git.", "Pipeline.", "Disco compartilhado."],
                  "Em incidente: 'quem é dono desse microsserviço?' resolve em 1 clique."),
                q("IDP X K8s diretamente:",
                  "IDP esconde a complexidade do K8s atrás de UX.",
                  ["São idênticos.", "K8s substitui IDP.", "Não se relacionam."],
                  "Dev raramente edita YAML de K8s direto; preenche form e plataforma gera tudo."),
                q("Métrica de sucesso de IDP:",
                  "Time-to-production de novos serviços.",
                  ["Número de tickets abertos.", "Tamanho do time SRE.", "Linhas de Helm."],
                  "Mede impacto real. Combine com DORA e NPS dos devs."),
                q("Time topology recomendada:",
                  "Stream-aligned + Platform team + Enabling team.",
                  ["Apenas devs.", "Apenas SRE.", "Apenas seg."],
                  "Plataforma como produto requer roles claros e ownership de longo prazo."),
            ],
        },
        # =====================================================================
        # 4.7 Policy as Code
        # =====================================================================
        {
            "title": "Policy as Code (PaC)",
            "summary": "Definir regras (ex.: 'nenhum servidor pode ser público') via código.",
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
            },
            "materials": [
                m("Open Policy Agent", "https://www.openpolicyagent.org/docs/latest/", "docs", ""),
                m("Conftest", "https://www.conftest.dev/", "tool", ""),
                m("Kyverno", "https://kyverno.io/docs/", "tool", ""),
                m("Sentinel (HashiCorp)", "https://developer.hashicorp.com/sentinel", "docs", ""),
                m("OPA Gatekeeper", "https://open-policy-agent.github.io/gatekeeper/website/docs/", "docs", ""),
                m("Cloud Custodian", "https://cloudcustodian.io/", "tool", ""),
            ],
            "questions": [
                q("Policy as Code permite:",
                  "Versionar e revisar políticas como qualquer código.",
                  ["Substituir CI.", "Apagar IAM.", "Reduzir testes."],
                  "Auditoria fica simples: git log mostra quando regra mudou e quem aprovou."),
                q("OPA usa linguagem:",
                  "Rego.",
                  ["YAML puro.", "Bash.", "Java."],
                  "Rego é declarativa, parecida com Datalog. Curva inicial existe, mas paga rápido."),
                q("Kyverno é específico para:",
                  "Kubernetes.",
                  ["Cloud Functions.", "AWS apenas.", "Apenas Helm."],
                  "Diferencial: políticas em YAML, sem precisar Rego. Boa entrada para times K8s."),
                q("Admission controller:",
                  "Intercepta criação/update de recursos antes de persistir.",
                  ["Apaga clusters.", "Substitui Helm.", "Reseta DNS."],
                  "Validating (rejeita) e mutating (modifica). Webhook chamado pelo apiserver."),
                q("Conftest serve para:",
                  "Validar arquivos de configuração com OPA fora do K8s.",
                  ["Substituir terraform.", "Mostrar logs.", "Substituir docker."],
                  "Roda em CI: `conftest test plan.json` aplica políticas Rego."),
                q("Policy de 'nenhum bucket público':",
                  "Pode ser aplicada em CI (pre-merge) e cluster (admission).",
                  ["Apenas em prod.", "Apenas com ticket.", "Não é possível."],
                  "Defesa em camadas: PR bloqueia, mas se algo passar, admission impede no provisionamento."),
                q("Falha em policy deve:",
                  "Bloquear o merge/deploy ou marcar não-compliant.",
                  ["Ser silenciada.", "Ignorada por padrão.", "Aprovar tudo."],
                  "Em ambientes regulados, audit trail mostra exceção justificada."),
                q("Fast feedback ao dev:",
                  "Rodar policy localmente via pre-commit.",
                  ["Apenas no console.", "Em prod só.", "Substitui CI."],
                  "Conftest pre-commit ajuda dev a corrigir antes mesmo do PR."),
                q("Difference SAST vs PaC:",
                  "SAST código; PaC config/infra/cluster.",
                  ["São idênticos.", "PaC é só Java.", "SAST é só YAML."],
                  "SAST olha código fonte; PaC olha configurações de infra/runtime."),
                q("Govern via PaC reduz:",
                  "Decisões caso-a-caso e configura tribal knowledge em código.",
                  ["Aumenta tickets.", "Reduz visibilidade.", "Apaga histórico."],
                  "Sem PaC, regra vira folclore: 'só fulano sabe'. Com PaC, está no repo."),
            ],
        },
        # =====================================================================
        # 4.8 DAST inicial
        # =====================================================================
        {
            "title": "DAST inicial",
            "summary": "Testar a aplicação rodando à procura de falhas web comuns (OWASP).",
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
                "body": (
                    "<h3>1. Filosofia: as 4 abordagens</h3>"
                    "<table>"
                    "<tr><th>Abordagem</th><th>Acesso</th><th>Foco</th><th>Limitação</th></tr>"
                    "<tr><td>SAST (white-box)</td><td>Código</td><td>Lógica, sinks</td><td>Não vê runtime</td></tr>"
                    "<tr><td>DAST (black-box)</td><td>App rodando</td><td>HTTP/runtime</td><td>Não vê código</td></tr>"
                    "<tr><td>IAST (gray-box)</td><td>Agente em runtime</td><td>Combina os dois</td><td>Adiciona overhead</td></tr>"
                    "<tr><td>RASP</td><td>Agente em runtime (defesa)</td><td>Bloqueia em produção</td><td>Pode degradar perf</td></tr>"
                    "</table>"
                    "<p>Use vários, pegam coisas diferentes. DAST passivo (baseline "
                    "scan) é barato e captura headers, redirects, defaults. "
                    "DAST ativo (full scan) faz fuzzing e ataques reais, não rode "
                    "contra produção sem autorização.</p>"

                    "<h3>2. OWASP ZAP: o canivete suíço gratuito</h3>"
                    "<p>Open source, multiplataforma, modos baseline/full/spider/"
                    "active scan. Útil em CI.</p>"
                    "<h4>2.1 Baseline scan</h4>"
                    "<pre><code># Baseline: scan passivo, ~5min, quase sem risco\n"
                    "$ docker run --rm -v $(pwd)/zap:/zap/wrk owasp/zap2docker-stable \\\n"
                    "    zap-baseline.py -t https://staging.exemplo.com \\\n"
                    "    -r baseline-report.html\n"
                    "\n"
                    "# Em CI\n"
                    "- name: ZAP Baseline\n"
                    "  uses: zaproxy/action-baseline@v0.10.0\n"
                    "  with:\n"
                    "    target: https://staging.exemplo.com\n"
                    "    fail_action: true   # falha CI se High</code></pre>"
                    "<h4>2.2 Full scan (ativo)</h4>"
                    "<p>Faz fuzz de inputs, tenta SQLi, XSS, path traversal. Demora "
                    "horas. Roda contra ambiente isolado com dados sintéticos.</p>"
                    "<pre><code>$ zap-full-scan.py -t https://staging.exemplo.com</code></pre>"
                    "<h4>2.3 Auth context</h4>"
                    "<p>DAST cego só vê pages públicas. Configure authentication para "
                    "cobrir rotas autenticadas:</p>"
                    "<pre><code># context.xml em ZAP\n"
                    "&lt;context&gt;\n"
                    "  &lt;authentication&gt;\n"
                    "    &lt;type&gt;form-based&lt;/type&gt;\n"
                    "    &lt;loginUrl&gt;https://app/login&lt;/loginUrl&gt;\n"
                    "    &lt;loginRequestData&gt;username={%username%}&password={%password%}&lt;/loginRequestData&gt;\n"
                    "  &lt;/authentication&gt;\n"
                    "  &lt;users&gt;\n"
                    "    &lt;user&gt;{ name: alice, credentials: {...} }&lt;/user&gt;\n"
                    "  &lt;/users&gt;\n"
                    "&lt;/context&gt;</code></pre>"

                    "<h3>3. Burp Suite: padrão da indústria</h3>"
                    "<p>Comercial (Pro). Proxy interativo + scanner. Padrão entre "
                    "pentesters profissionais.</p>"
                    "<ul>"
                    "<li><strong>Proxy</strong>: intercepta requests do browser; "
                    "permite editar/repetir.</li>"
                    "<li><strong>Repeater</strong>: enviar mesma request com "
                    "variações.</li>"
                    "<li><strong>Intruder</strong>: fuzz com payloads.</li>"
                    "<li><strong>Scanner</strong>: ataques automáticos (Pro).</li>"
                    "<li><strong>Decoder/Comparer</strong>: utilitários.</li>"
                    "<li><strong>Extensions</strong>: ecossistema rico (BApp Store).</li>"
                    "</ul>"

                    "<h3>4. Nuclei: detecção rápida</h3>"
                    "<p>Templates declarativos para detectar CVEs, misconfigurations, "
                    "tokens expostos. Rápido e preciso:</p>"
                    "<pre><code>$ nuclei -u https://staging.exemplo.com \\\n"
                    "    -t http/cves/ \\\n"
                    "    -t http/exposures/ \\\n"
                    "    -severity high,critical\n"
                    "\n"
                    "[2024-CVE-XXXX] [http] [high] https://staging.exemplo.com/.git/config\n"
                    "[exposed-tokens] [http] [critical] https://staging.exemplo.com/.env</code></pre>"

                    "<h3>5. Em CI: pipeline com DAST</h3>"
                    "<pre><code>name: dast\n"
                    "on:\n"
                    "  pull_request: {}\n"
                    "  schedule: [{ cron: '0 2 * * *' }]   # nightly\n"
                    "jobs:\n"
                    "  zap:\n"
                    "    runs-on: ubuntu-latest\n"
                    "    services:\n"
                    "      app:\n"
                    "        image: ghcr.io/empresa/app:${{ github.sha }}\n"
                    "        ports: [8000:8000]\n"
                    "      db:\n"
                    "        image: postgres:16\n"
                    "        env: { POSTGRES_PASSWORD: dast }\n"
                    "    steps:\n"
                    "      - run: ./scripts/wait-for-app.sh http://localhost:8000\n"
                    "      - run: ./scripts/seed-test-data.sh\n"
                    "      - uses: zaproxy/action-baseline@v0.10.0\n"
                    "        with:\n"
                    "          target: http://localhost:8000\n"
                    "          rules_file_name: .zap/rules.tsv\n"
                    "          cmd_options: '-z \"-config api.disablekey=true\"'\n"
                    "      - run: nuclei -u http://localhost:8000 -severity critical -ec\n"
                    "      - if: failure()\n"
                    "        uses: actions/upload-artifact@v4\n"
                    "        with: { name: dast-report, path: report_html.html }</code></pre>"

                    "<h3>6. OWASP Top 10 (2021): o que DAST detecta</h3>"
                    "<table>"
                    "<tr><th>Categoria</th><th>O que DAST detecta</th></tr>"
                    "<tr><td>A01: Broken Access Control</td><td>IDOR via fuzz, paths não autorizados, BOLA</td></tr>"
                    "<tr><td>A02: Cryptographic Failures</td><td>TLS fraco, mixed content, sem HSTS</td></tr>"
                    "<tr><td>A03: Injection</td><td>SQLi, NoSQLi, command injection, XSS, LDAPi</td></tr>"
                    "<tr><td>A04: Insecure Design</td><td>Limitado, DAST não 'pensa' como humano</td></tr>"
                    "<tr><td>A05: Security Misconfiguration</td><td>Headers, debug=true, defaults expostos</td></tr>"
                    "<tr><td>A06: Vulnerable Components</td><td>Detecta versões antigas</td></tr>"
                    "<tr><td>A07: Auth Failures</td><td>Brute force, sessão fraca, credenciais default</td></tr>"
                    "<tr><td>A08: Software/Data Integrity</td><td>Limitado</td></tr>"
                    "<tr><td>A09: Logging/Monitoring</td><td>Não detecta diretamente</td></tr>"
                    "<tr><td>A10: SSRF</td><td>Fuzz de URL parameters</td></tr>"
                    "</table>"

                    "<h3>7. Headers de segurança</h3>"
                    "<p>DAST checa que app retorna headers apropriados:</p>"
                    "<pre><code>Strict-Transport-Security: max-age=31536000; includeSubDomains; preload\n"
                    "Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123'\n"
                    "X-Content-Type-Options: nosniff\n"
                    "X-Frame-Options: DENY\n"
                    "Referrer-Policy: strict-origin-when-cross-origin\n"
                    "Permissions-Policy: geolocation=(), camera=()\n"
                    "Cross-Origin-Opener-Policy: same-origin\n"
                    "Cross-Origin-Embedder-Policy: require-corp</code></pre>"
                    "<p>Mozilla Observatory dá score A+/F para sua url e sugere "
                    "headers faltando.</p>"

                    "<h3>8. CORS comum errado</h3>"
                    "<p>API com CORS permissivo permite frontend malicioso fazer "
                    "request com cookies de sessão:</p>"
                    "<pre><code># RUIM\n"
                    "Access-Control-Allow-Origin: *\n"
                    "Access-Control-Allow-Credentials: true   # browser ignora isso, mas...\n"
                    "\n"
                    "# RUIM (reflete origin sem validar)\n"
                    "Access-Control-Allow-Origin: $REQUEST_ORIGIN\n"
                    "\n"
                    "# BOM: allow-list explícito\n"
                    "if origin in ALLOWED_ORIGINS:\n"
                    "    Access-Control-Allow-Origin: origin</code></pre>"

                    "<h3>9. SSRF (Server-Side Request Forgery)</h3>"
                    "<p>App faz request HTTP para URL fornecida pelo usuário. "
                    "Atacante envia <code>http://169.254.169.254/latest/meta-data/</code> "
                    "(metadata service AWS) e exfiltra credenciais.</p>"
                    "<p>Mitigação:</p>"
                    "<ul>"
                    "<li>Allow-list de domínios.</li>"
                    "<li>Bloqueio de IPs privados (10.x, 192.168.x, 169.254.x).</li>"
                    "<li>IMDSv2 obrigatório no AWS.</li>"
                    "<li>Egress restrito por NACL/Security Group.</li>"
                    "</ul>"

                    "<h3>10. DAST vs Pentest vs Bug Bounty</h3>"
                    "<table>"
                    "<tr><th>Tipo</th><th>Quando</th><th>Cobertura</th><th>Custo</th></tr>"
                    "<tr><td>DAST (CI)</td><td>A cada PR</td><td>Padrões conhecidos automatizados</td><td>~$0</td></tr>"
                    "<tr><td>Pentest</td><td>Anual ou pré-launch</td><td>Profundo, criatividade humana</td><td>$$$</td></tr>"
                    "<tr><td>Bug Bounty</td><td>Contínuo</td><td>Crowd-sourced, qualidade variada</td><td>$ por bug encontrado</td></tr>"
                    "<tr><td>Red Team</td><td>1-2x ano</td><td>Simula ataque real, full-scope</td><td>$$$$</td></tr>"
                    "</table>"
                    "<p>Estratégia madura: DAST contínuo + pentest anual (ou em "
                    "release major) + bug bounty para coverage extra.</p>"

                    "<h3>11. Aviso legal</h3>"
                    "<p>Escaneamento de sistema sem autorização expressa pode ser "
                    "crime (Marco Civil BR, CFAA EUA, GDPR EU). Use somente:</p>"
                    "<ul>"
                    "<li>Sistemas próprios.</li>"
                    "<li>Ambientes contratados (pentest).</li>"
                    "<li>Bug bounty programs com escopo definido.</li>"
                    "<li>Plataformas de prática (HackTheBox, TryHackMe, "
                    "PortSwigger Academy).</li>"
                    "</ul>"

                    "<h3>12. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>DAST contra produção sem autorização</strong>: "
                    "potencial DoS + crime.</li>"
                    "<li><strong>Sem auth context</strong>: vc só escaneia tela de login.</li>"
                    "<li><strong>Mil falsos positivos</strong>: configure tuning, "
                    "exclude paths.</li>"
                    "<li><strong>Sem SLA de remediação</strong>: achados acumulam.</li>"
                    "<li><strong>DAST sozinho</strong>: complementa SAST e pentest, "
                    "não substitui.</li>"
                    "</ul>"
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
            },
            "materials": [
                m("OWASP ZAP", "https://www.zaproxy.org/", "tool", ""),
                m("Burp Suite", "https://portswigger.net/burp", "tool", ""),
                m("Nuclei", "https://github.com/projectdiscovery/nuclei", "tool", ""),
                m("OWASP Top 10", "https://owasp.org/www-project-top-ten/", "docs", ""),
                m("HackTricks", "https://book.hacktricks.xyz/", "book", ""),
                m("PortSwigger Web Security Academy", "https://portswigger.net/web-security",
                  "course", "Treinamento gratuito de qualidade."),
            ],
            "questions": [
                q("DAST exige:",
                  "App rodando.",
                  ["Apenas código.", "Apenas IaC.", "Apenas YAML."],
                  "Por isso DAST roda em staging/QA com dados sintéticos."),
                q("ZAP em modo baseline:",
                  "Faz scan rápido sem ataques agressivos.",
                  ["Substitui pentest.", "Apenas frontend.", "Apenas IaC."],
                  "Verifica passivamente cabeçalhos, redirects, configs. Quase sem risco para o app."),
                q("XSS é:",
                  "Cross-site scripting, injeção de JS via input.",
                  ["Tipo de TLS.", "Backup.", "Variante de SQL."],
                  "Reflected, stored, DOM-based. Mitigação: output encoding, CSP."),
                q("SQLi é:",
                  "SQL Injection, input que altera queries.",
                  ["Tipo de DNS.", "Apenas em XML.", "Sempre browser."],
                  "Mitigação: prepared statements / ORM com parameterized queries. Nunca string concat."),
                q("Idealmente DAST roda:",
                  "Em pipeline contra ambiente isolado.",
                  ["Apenas em prod.", "Manualmente em produção.", "Não roda."],
                  "Staging com dados sintéticos. Em produção, só com autorização e janela controlada."),
                q("Auth em DAST:",
                  "Permite cobrir endpoints autenticados.",
                  ["É opcional sempre.", "Substitui senha.", "Bloqueia o scan."],
                  "Sem auth, scanner só vê página de login. Config 'authentication context' no scanner."),
                q("Headers de segurança:",
                  "DAST checa CSP, HSTS, X-Frame-Options etc.",
                  ["Apenas DNS.", "Apenas TLS.", "Apenas SAST."],
                  "Headers como CSP, HSTS, X-Content-Type-Options reduzem risco com config simples."),
                q("CSRF:",
                  "Cross-site request forgery, request feita em nome do usuário sem consentimento.",
                  ["Tipo de cripto.", "Padrão DNS.", "Variante MFA."],
                  "Mitigação: CSRF token, SameSite cookies, double-submit cookie."),
                q("Pentest difere de DAST porque:",
                  "Pentest envolve criatividade humana e exploração.",
                  ["Pentest é só script.", "DAST é manual.", "Não diferem."],
                  "Pentester encadeia falhas baixas em compromisso. DAST sozinho raramente faz isso."),
                q("DAST exige consentimento:",
                  "Sim, sempre, antes de testar sistemas alheios.",
                  ["Não, é livre.", "Apenas em fim de semana.", "Apenas com VPN."],
                  "Escaneamento sem autorização pode ser crime (Marco Civil, CFAA, etc.)."),
            ],
        },
        # =====================================================================
        # 4.9 API Security
        # =====================================================================
        {
            "title": "API Security",
            "summary": "Como proteger os pontos de entrada das aplicações.",
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
            },
            "materials": [
                m("OWASP API Top 10", "https://owasp.org/API-Security/editions/2023/en/0x11-t10/", "docs", ""),
                m("OAuth 2.0 (RFC 6749)", "https://datatracker.ietf.org/doc/html/rfc6749", "docs", ""),
                m("OpenAPI Specification", "https://swagger.io/specification/", "docs", ""),
                m("k6", "https://k6.io/docs/", "tool", ""),
                m("OIDC (OpenID Connect)", "https://openid.net/developers/how-connect-works/", "docs", ""),
                m("JWT.io", "https://jwt.io/", "tool", "Decoder e referência."),
            ],
            "questions": [
                q("OAuth 2.0 difere de OIDC porque:",
                  "OIDC adiciona camada de identidade (id_token) sobre OAuth.",
                  ["São idênticos.", "OAuth tem id_token.", "OIDC é menos seguro."],
                  "OAuth = autorização (delegação de acesso). OIDC = identidade (id_token assinado)."),
                q("BOLA (Broken Object Level Auth):",
                  "Checar autorização no nível do recurso individual.",
                  ["Tipo de TLS.", "Bug Bounty.", "Cripto fraca."],
                  "API que aceita /orders/{id} sem checar se o usuário é dono do pedido."),
                q("Rate limit ajuda contra:",
                  "Brute force e DoS.",
                  ["Performance.", "Logs.", "TLS."],
                  "Camadas: gateway + app. Use Redis para sliding window distribuído."),
                q("Validação de schema:",
                  "Rejeita payloads que não obedecem à API spec.",
                  ["Aceita tudo.", "Apenas em prod.", "Substitui auth."],
                  "OpenAPI + framework auto-validador (FastAPI, Spring). Reduz exploits de input."),
                q("Token JWT deve:",
                  "Ter exp curta + refresh token + assinatura forte.",
                  ["Ser eterno.", "Ser sem assinatura.", "Conter senha."],
                  "Algoritmo: RS256/EdDSA, não 'none'. Exp típico: 5-15 min para acesso."),
                q("CORS mal configurado:",
                  "Permite frontends maliciosos chamarem sua API.",
                  ["Acelera browser.", "Substitui auth.", "Comprime resposta."],
                  "Allow-list explícito de origins; nunca `*` com `credentials: true`."),
                q("API Gateway serve para:",
                  "Centralizar auth, rate limit, observability.",
                  ["Substituir cluster.", "Apagar microserviço.", "Substituir IAM."],
                  "Tira responsabilidades transversais de cada serviço. Kong, AWS API Gateway, NGINX."),
                q("Mass assignment:",
                  "Cliente injeta campos não esperados no body (ex.: is_admin).",
                  ["Tipo de TLS.", "Categoria de log.", "Backup."],
                  "Mitigação: DTOs com allow-list explícito; nunca passar request.json direto pro ORM."),
                q("Excessive Data Exposure:",
                  "API retorna mais campos que o necessário.",
                  ["Tipo de DNS.", "Backup.", "Otimização."],
                  "Use response models específicos por endpoint. Cuide de PII e segredos no retorno."),
                q("Webhook seguro precisa:",
                  "Assinatura HMAC verificada no destino.",
                  ["Sempre HTTP.", "Sem auth.", "Apenas IPv6."],
                  "Stripe, GitHub, Slack assinam com HMAC. Receptor valida antes de processar."),
            ],
        },
        # =====================================================================
        # 4.10 Centralized Logging
        # =====================================================================
        {
            "title": "Centralized Logging",
            "summary": "Trazer logs de vários lugares para uma tela só.",
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
                "body": (
                    "<h3>1. Pilhas comuns</h3>"
                    "<table>"
                    "<tr><th>Stack</th><th>Componentes</th><th>Notas</th></tr>"
                    "<tr><td>ELK</td><td>Elasticsearch + Logstash + Kibana</td><td>Maduro, poderoso. Caro em escala (RAM-hungry).</td></tr>"
                    "<tr><td>EFK</td><td>Elasticsearch + Fluentd/Bit + Kibana</td><td>Logstash → Fluent (mais leve).</td></tr>"
                    "<tr><td>OpenSearch</td><td>Fork ASL2 do ES</td><td>Após mudança de licença ES (2021).</td></tr>"
                    "<tr><td>Grafana Loki</td><td>Loki + Promtail/Vector + Grafana</td><td>Indexa só labels. Custo &lt;&lt; ELK.</td></tr>"
                    "<tr><td>Datadog/Splunk/New Relic</td><td>SaaS</td><td>UX top, $ alto, retenção limitada.</td></tr>"
                    "<tr><td>VictoriaLogs</td><td>OSS, eficiente</td><td>Performance forte, ainda jovem.</td></tr>"
                    "</table>"

                    "<h3>2. Logs estruturados (JSON)</h3>"
                    "<p>Texto livre é ilegível por máquina. JSON em uma linha "
                    "(NDJSON) permite query por campo:</p>"
                    "<pre><code># RUIM\n"
                    "[2024-04-25 10:30:15] INFO User 123 placed order 456 for $99.50\n"
                    "\n"
                    "# BOM\n"
                    "{\"ts\":\"2024-04-25T10:30:15Z\",\"level\":\"info\",\"service\":\"orders\",\n"
                    " \"event\":\"order_placed\",\"user_id\":\"u_123\",\"order_id\":\"o_456\",\n"
                    " \"amount\":99.50,\"currency\":\"USD\",\"trace_id\":\"abc-123\",\n"
                    " \"span_id\":\"span-xyz\"}</code></pre>"
                    "<p>Campos padrão recomendados:</p>"
                    "<ul>"
                    "<li><code>ts</code>: ISO 8601 UTC com timezone.</li>"
                    "<li><code>level</code>: debug/info/warn/error/fatal.</li>"
                    "<li><code>service</code>: nome do app.</li>"
                    "<li><code>env</code>: prod/staging/dev.</li>"
                    "<li><code>version</code>: SHA do build.</li>"
                    "<li><code>trace_id</code>, <code>span_id</code>: correlação "
                    "com tracing (OpenTelemetry).</li>"
                    "<li><code>user_id</code> hash (sem PII direto), "
                    "<code>request_id</code>.</li>"
                    "<li><code>event</code>: nome semântico do evento.</li>"
                    "<li><code>message</code>: descrição humana opcional.</li>"
                    "</ul>"
                    "<p>Em Python:</p>"
                    "<pre><code>import structlog\n"
                    "structlog.configure(\n"
                    "    processors=[\n"
                    "        structlog.processors.add_log_level,\n"
                    "        structlog.processors.TimeStamper(fmt='iso'),\n"
                    "        structlog.contextvars.merge_contextvars,\n"
                    "        structlog.processors.JSONRenderer(),\n"
                    "    ],\n"
                    ")\n"
                    "log = structlog.get_logger()\n"
                    "\n"
                    "log.info('order_placed', user_id=user.id_hash, order_id=order.id, amount=99.50)\n"
                    "# {\"event\":\"order_placed\",\"timestamp\":\"...\",\"level\":\"info\",...}</code></pre>"

                    "<h3>3. Coleta: app → coletor → backend</h3>"
                    "<p>App escreve em stdout (12-factor). Coletor (DaemonSet em K8s, "
                    "agent no host) lê e envia.</p>"
                    "<table>"
                    "<tr><th>Coletor</th><th>Linguagem</th><th>Notas</th></tr>"
                    "<tr><td>Fluentd</td><td>Ruby</td><td>Veterano, plugins ricos.</td></tr>"
                    "<tr><td>Fluent Bit</td><td>C</td><td>Mais leve; default em K8s.</td></tr>"
                    "<tr><td>Vector</td><td>Rust</td><td>Performant, VRL para transformações.</td></tr>"
                    "<tr><td>Promtail</td><td>Go</td><td>Específico para Loki.</td></tr>"
                    "<tr><td>OTel Collector</td><td>Go</td><td>Multi-signal (logs+metrics+traces).</td></tr>"
                    "<tr><td>Logstash</td><td>JVM</td><td>Pesado; legado.</td></tr>"
                    "</table>"
                    "<pre><code># Fluent Bit em K8s (DaemonSet), config\n"
                    "[INPUT]\n"
                    "    Name              tail\n"
                    "    Path              /var/log/containers/*.log\n"
                    "    Parser            docker\n"
                    "    DB                /var/log/flb_kube.db\n"
                    "    Tag               kube.*\n"
                    "[FILTER]\n"
                    "    Name              kubernetes\n"
                    "    Match             kube.*\n"
                    "    Merge_Log         On\n"
                    "[FILTER]\n"
                    "    Name              modify\n"
                    "    Match             kube.*\n"
                    "    Remove            stream\n"
                    "[OUTPUT]\n"
                    "    Name              loki\n"
                    "    Match             kube.*\n"
                    "    Host              loki.observability\n"
                    "    Labels            $kubernetes['namespace_name'],$kubernetes['pod_name']</code></pre>"

                    "<h3>4. Loki: low-cost via labels</h3>"
                    "<p>Diferente de Elasticsearch, Loki <em>não indexa o conteúdo</em>. "
                    "Indexa só labels (chave-valor). Conteúdo bruto é comprimido e "
                    "lido sob demanda. Custo &lt;&lt; ELK.</p>"
                    "<p>Trade-off: queries por substring varrem todos os logs (mais "
                    "lento). Queries por label (<code>{namespace=\"prod\", "
                    "service=\"api\", level=\"error\"}</code>) são rápidas.</p>"
                    "<p>LogQL (linguagem de query Loki):</p>"
                    "<pre><code># Filtro por labels + texto\n"
                    "{namespace=\"prod\", service=\"api\"} |= \"error\" | json | status &gt;= 500\n"
                    "\n"
                    "# Métricas a partir de logs\n"
                    "rate({namespace=\"prod\"} |= \"error\" [5m])\n"
                    "\n"
                    "# p99 latency dos logs\n"
                    "quantile_over_time(0.99, {service=\"api\"} | json | unwrap latency_ms [5m])</code></pre>"
                    "<p>Cuidado com cardinalidade: <em>nunca</em> use ID único "
                    "(user_id, request_id) como label, explode índice.</p>"

                    "<h3>5. Retenção, custo e tiering</h3>"
                    "<p>Logs crescem rápido (TBs/mês). Política por categoria:</p>"
                    "<table>"
                    "<tr><th>Categoria</th><th>Retenção típica</th></tr>"
                    "<tr><td>Debug app</td><td>3-7 dias</td></tr>"
                    "<tr><td>Info app</td><td>14-30 dias</td></tr>"
                    "<tr><td>Error app</td><td>30-90 dias</td></tr>"
                    "<tr><td>Audit (auth, perm change)</td><td>1-7 anos (compliance)</td></tr>"
                    "<tr><td>Payment/PCI</td><td>1+ ano</td></tr>"
                    "<tr><td>HIPAA</td><td>6 anos</td></tr>"
                    "</table>"
                    "<p>Tiering hot/warm/cold:</p>"
                    "<ul>"
                    "<li><strong>Hot</strong> (SSD, busca rápida): últimos 7d.</li>"
                    "<li><strong>Warm</strong> (HDD, busca mais lenta): 7-30d.</li>"
                    "<li><strong>Cold</strong> (S3 Glacier): 30d+.</li>"
                    "</ul>"
                    "<p>Em ELK: ILM (Index Lifecycle Management) automatiza.</p>"

                    "<h3>6. PII em logs: o pesadelo legal</h3>"
                    "<p>Log com CPF/email/token vira problema:</p>"
                    "<ul>"
                    "<li>LGPD/GDPR: pode constituir vazamento.</li>"
                    "<li>SIEM/Datadog: dados em terceiro.</li>"
                    "<li>Backups: dado replicado em múltiplos lugares.</li>"
                    "<li>Once logged, forever logged.</li>"
                    "</ul>"
                    "<p>Sanitize em camadas:</p>"
                    "<ol>"
                    "<li><strong>App</strong>: nunca log direto. Use "
                    "<code>mask_email()</code>, <code>hash_user_id()</code>.</li>"
                    "<li><strong>Coletor</strong>: filtros que apagam padrões "
                    "(regex CPF, cartão).</li>"
                    "<li><strong>Pré-ingest</strong>: Vector VRL transforma.</li>"
                    "</ol>"
                    "<pre><code># Vector VRL para sanitize\n"
                    "transforms.sanitize_pii:\n"
                    "  type: remap\n"
                    "  inputs: [logs_in]\n"
                    "  source: |\n"
                    "    .message = redact(.message, filters: [\\\n"
                    "      {\"type\": \"pattern\", \"patterns\": [r'\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}']},\\\n"
                    "      {\"type\": \"pattern\", \"patterns\": [r'\\d{16}']}\\\n"
                    "    ])\n"
                    "    if exists(.user.email) {\n"
                    "      .user.email_hash = sha2(string!(.user.email), \"SHA-256\")\n"
                    "      del(.user.email)\n"
                    "    }</code></pre>"
                    "<p>Lista do que <strong>nunca</strong> logar:</p>"
                    "<ul>"
                    "<li>Senhas, tokens, secrets.</li>"
                    "<li>Cartão de crédito, CVV.</li>"
                    "<li>CPF/SSN/RG sem mask.</li>"
                    "<li>JWT, session cookie.</li>"
                    "<li>Headers de auth (<code>Authorization</code>).</li>"
                    "<li>Body de request com PII em rotas sensíveis.</li>"
                    "</ul>"

                    "<h3>7. Sampling: reduz volume mantendo sinal</h3>"
                    "<ul>"
                    "<li><strong>Em logs DEBUG</strong>: 1-10% sampling. ERROR sempre 100%.</li>"
                    "<li><strong>Em traces</strong>: head sampling 1%; tail sampling "
                    "100% para errors/slow.</li>"
                    "<li><strong>Cost-based</strong>: dynamic sampling.</li>"
                    "</ul>"

                    "<h3>8. Os três pilares da observabilidade</h3>"
                    "<table>"
                    "<tr><th>Sinal</th><th>Responde</th><th>Custo típico</th></tr>"
                    "<tr><td>Logs</td><td>O que aconteceu (eventos)</td><td>Alto (volume)</td></tr>"
                    "<tr><td>Métricas</td><td>Quanto/com que frequência</td><td>Baixo (agregação)</td></tr>"
                    "<tr><td>Traces</td><td>Qual fluxo (entre serviços)</td><td>Médio (com sampling)</td></tr>"
                    "</table>"
                    "<p>Correlation id (<code>trace_id</code>) permite saltar entre "
                    "os três. OpenTelemetry padroniza em coleta única.</p>"
                    "<pre><code># Em log\n"
                    "{\"event\":\"order_placed\",\"trace_id\":\"abc-123\",...}\n"
                    "\n"
                    "# Em métrica (exemplar do Prometheus)\n"
                    "http_request_duration_seconds_bucket{...} 0.42 # exemplar trace_id=abc-123\n"
                    "\n"
                    "# Em trace\n"
                    "trace_id=abc-123 → vê spans dos serviços envolvidos</code></pre>"

                    "<h3>9. Stack moderna recomendada</h3>"
                    "<ul>"
                    "<li><strong>Logs</strong>: Loki (custo) ou OpenSearch (search rico).</li>"
                    "<li><strong>Métricas</strong>: Prometheus + Grafana.</li>"
                    "<li><strong>Traces</strong>: Jaeger ou Tempo + OpenTelemetry.</li>"
                    "<li><strong>Coleta</strong>: OTel Collector ou Vector.</li>"
                    "<li><strong>Visualização única</strong>: Grafana (logs, "
                    "metrics, traces na mesma interface).</li>"
                    "<li><strong>Alertas</strong>: Alertmanager + PagerDuty/"
                    "Opsgenie.</li>"
                    "</ul>"

                    "<h3>10. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Log em arquivo dentro do container</strong>: ninguém vê.</li>"
                    "<li><strong>Texto livre não-estruturado</strong>: ilegível por máquina.</li>"
                    "<li><strong>PII em log</strong>: bomba-relógio legal.</li>"
                    "<li><strong>Cardinalidade alta em labels</strong>: explode índice.</li>"
                    "<li><strong>Retenção 'para sempre'</strong>: custo descontrolado.</li>"
                    "<li><strong>Sem correlation id</strong>: incidente vira detetive.</li>"
                    "<li><strong>print() em vez de logger</strong>: sem level, sem JSON.</li>"
                    "<li><strong>Logar tudo em DEBUG em prod</strong>: ruído + custo.</li>"
                    "<li><strong>Stack trace para usuário</strong>: leak de info.</li>"
                    "</ul>"
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
            },
            "materials": [
                m("Grafana Loki", "https://grafana.com/docs/loki/latest/", "docs", ""),
                m("Elastic Stack", "https://www.elastic.co/guide/index.html", "docs", ""),
                m("OpenSearch", "https://opensearch.org/docs/", "docs", ""),
                m("Vector", "https://vector.dev/docs/", "tool", ""),
                m("Logstash", "https://www.elastic.co/guide/en/logstash/current/index.html", "docs", ""),
                m("OpenTelemetry Logs", "https://opentelemetry.io/docs/concepts/signals/logs/",
                  "docs", ""),
            ],
            "questions": [
                q("Centralizar logs ajuda em:",
                  "Correlação de incidentes entre serviços.",
                  ["Aumentar latência.", "Substituir backup.", "Reduzir custo."],
                  "Permite seguir trace_id por 5 microsserviços em uma busca só."),
                q("Loki indexa:",
                  "Apenas labels, não o conteúdo do log.",
                  ["Tudo.", "Apenas timestamp.", "Apenas nível."],
                  "Por isso é barato. Conteúdo é comprimido e lido sob demanda. Queries por substring varrem."),
                q("ELK stack contém:",
                  "Elasticsearch + Logstash + Kibana.",
                  ["Apache + Nginx + HAProxy.", "Postgres + Redis + Mongo.", "Docker + K8s + Helm."],
                  "Variantes: EFK (Fluentd no lugar de Logstash). OpenSearch é fork ASL2."),
                q("Retenção precisa equilibrar:",
                  "Custo vs requisitos de compliance.",
                  ["Apenas custo.", "Apenas SLA.", "Apenas TLS."],
                  "Audit logs em alguns setores precisam 1+ ano. Logs de debug raramente."),
                q("Anonimização em logs:",
                  "Remover PII para reduzir risco em vazamentos.",
                  ["É opcional sempre.", "É proibido.", "Substitui encryption."],
                  "Hash de email, mascarar CPF (***.***.123-45). LGPD/GDPR olham para isso."),
                q("Vector é:",
                  "Pipeline de logs/metrics performant em Rust.",
                  ["Banco de dados.", "Linguagem.", "Cluster K8s."],
                  "Substitui Logstash e Fluentd com performance superior. VRL para transformações."),
                q("Estruturar logs em JSON:",
                  "Permite buscar por campo.",
                  ["Aumenta tamanho 10x.", "Substitui métricas.", "Apaga timestamps."],
                  "Tamanho cresce ~30%, mas valor de query é incomparável."),
                q("Sampling:",
                  "Reduz volume preservando representatividade.",
                  ["Aumenta volume.", "Substitui retenção.", "Não tem efeito."],
                  "Em traces, sampling de 1-10% é comum. Em logs, sampling do INFO mantendo todos os ERROR."),
                q("Tracing (distributed):",
                  "Complementa logs com fluxo entre serviços.",
                  ["Substitui métricas.", "Substitui logs.", "Apenas web."],
                  "Spans em árvore mostram tempo gasto em cada step. Combine com logs por trace_id."),
                q("Log com PII em CW:",
                  "Pode violar LGPD/GDPR, sanitize antes.",
                  ["É necessário sempre.", "Sem risco.", "Imune a auditoria."],
                  "Mesmo logs internos podem ser exfiltrados. ANPD (BR) já multou por logs imprudentes."),
            ],
        },
    ],
}
