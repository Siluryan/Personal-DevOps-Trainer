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
<div class="mermaid">
flowchart LR
    DF["Dockerfile"] --> Build["docker build"]
    Build --> Img["Imagem, read-only, em camadas"]
    Img --> Run["docker run"]
    Run --> Cont["Container, camada gravável por cima"]
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
                  ["Compila a imagem a partir de um Dockerfile local, erro típico de configuração feita às pressas, sem revisão posterior.", "Sobe um serviço de registry para guardar imagens, erro comum de quem aprendeu por tentativa e erro, sem revisar a documentação oficial.", "Remove um volume e os dados persistidos nele, abordagem que resolve o sintoma, não a causa raiz do problema."],
                  "`docker run` = `docker create` + `docker start`. Para builds, é `docker build`."),
                q("Multi-stage build:",
                  "Permite usar imagem maior para build e menor para runtime.",
                  ["Deixa a imagem final maior, com todas as dependências de build.", "Só funciona em projeto escrito em Python.", "Substitui a etapa de build feita no pipeline de CI."],
                  "Ex.: imagem com gcc só na fase de compilação; runtime tem só o binário."),
                q("Diferença entre image e container:",
                  "Imagem é o template (read-only); container é a instância em execução.",
                  ["A imagem muda de conteúdo sozinha a cada execução, atalho que ignora exatamente o cenário que mais importa evitar.", "O container é só um registro estatístico de uso, abordagem que ignora o cenário de falha mais provável na prática.", "Imagem e container são exatamente a mesma coisa, sem diferença, suposição que só vale em ambiente de desenvolvimento, não em produção."],
                  "Várias instâncias podem rodar a mesma imagem com configs diferentes (env, volumes)."),
                q("Volume serve para:",
                  "Persistir dados fora do ciclo de vida do container.",
                  ["Aumentar a memória RAM disponível para o container.", "Substituir o serviço de DNS usado pela aplicação.", "Melhorar o tempo de build da imagem Docker."],
                  "Container pode ser destruído/recriado sem perder dados se eles estão em volume."),
                q("`COPY` vs `ADD`:",
                  "Prefira COPY; ADD tem comportamento extra (download/extract) que pode surpreender.",
                  ["COPY está depreciado e não deve mais ser usado no Dockerfile, atalho que troca segurança por conveniência de curto prazo.", "COPY e ADD fazem exatamente a mesma coisa, sem diferença alguma, suposição que vale só até o primeiro imprevisto de rede ou hardware.", "ADD costuma ser considerado a opção superior mesmo em casos simples, suposição que só vale em ambiente de desenvolvimento, não em produção."],
                  "ADD baixa URL e extrai tar automaticamente, recursos perigosos sem necessidade na maioria dos casos."),
                q("Layer caching no Docker:",
                  "Reaproveita camadas inalteradas, ordem dos comandos importa.",
                  ["Essa funcionalidade de cache simplesmente não existe no Docker.", "Só funciona quando a build roda em ambiente de produção.", "Substitui a necessidade de usar um registry para as imagens."],
                  "Mudou uma camada? Todas após são invalidadas. Por isso copy de código vai por último."),
                q(".dockerignore evita:",
                  "Enviar arquivos desnecessários para o build context.",
                  ["Apagar arquivos do disco local automaticamente.", "Reduzir o uso de CPU durante o processo de build.", "Substituir por completo o arquivo .gitignore do repositório."],
                  "Sem ele, `docker build` envia o repo todo (.git, node_modules) ao daemon, lento e perigoso."),
                q("Por que NÃO usar latest em produção?",
                  "Falta rastreabilidade, pode mudar.",
                  ["Fazer pull da tag latest costuma ser mais lento que outras tags.", "A tag latest simplesmente não funciona em algum ambiente.", "A tag latest exige uma licença paga do Docker Hub."],
                  "Em rollback você não consegue voltar 'para qual latest era ontem'. Use SHA ou semver."),
                q("Para aplicações stateless:",
                  "Containers facilitam escala horizontal.",
                  ["Containers atrapalham mais do que ajudam nesse caso.", "Uma VM tradicional costuma ser melhor nesse cenário.", "Não existe vantagem real em usar container aqui."],
                  "Sem estado em disco local, basta subir mais réplicas. Estado vai para DB/cache externos."),
                q("Imagem de 1 GB para Python:",
                  "Provavelmente pode ser otimizada com multi-stage e base slim/alpine.",
                  ["Esse tamanho já é considerado ideal para imagem Python, decisão que parece segura até o primeiro teste de penetração real.", "Esse tamanho é necessário na grande maioria dos casos, decisão que parece razoável isolada, mas quebra a arquitetura no conjunto.", "Esse tamanho já é o menor tecnicamente possível para Python, suposição que ignora como o recurso realmente se comporta em escala."],
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
    A["Imagem base completa"] --> B["Remove shell e package manager"]
    B --> C["Roda como usuário não-root"]
    C --> D["Imagem distroless / minimalista"]
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
                  ["Funciona só para imagens escritas em Python, decisão que parece segura até o primeiro teste de penetração real.", "Ter maior performance de rede entre containers, prática que gera falso senso de segurança no time.", "Aumentar o volume de logs gerados pela imagem, suposição que raramente se sustenta fora do ambiente controlado de laboratório."],
                  "Sem shell, atacante não tem como sair do container facilmente. Debug fica menos confortável, trade-off."),
                q("Pin por digest sha256 garante:",
                  "Reprodutibilidade, mesma imagem sempre.",
                  ["Renovação automática do certificado usado na imagem.", "Uma conexão TLS mais forte entre cliente e registry.", "Maior velocidade de download da imagem no pull."],
                  "Tag pode ser sobrescrita; digest é hash do conteúdo, único."),
                q("Imagem alpine é:",
                  "Pequena, mas com musl libc, pode quebrar pacotes glibc.",
                  ["Não inclui alguma implementação de libc na imagem, decisão que parece segura até o primeiro teste de penetração real.", "Costuma ser mais lenta que outras distros base, atalho que ignora exatamente o cenário que mais importa evitar.", "Tecnicamente idêntica à imagem base do Debian, prática que gera falso senso de segurança no time."],
                  "Alguns wheels Python só vêm em manylinux (glibc). Mede antes de migrar."),
                q("Escanear imagem em CI:",
                  "Para pegar CVEs antes do push em registry.",
                  ["Substitui completamente a etapa de SAST no pipeline.", "Só faz sentido rodar isso já em produção.", "Não tem efeito prático algum na segurança final."],
                  "Falha rápida no PR é melhor que descobrir CVE em produção."),
                q("Rodar como root no container:",
                  "Risco, escalada privilege se sair do container.",
                  ["Reduz o uso de CPU consumido pelo processo principal.", "Uma boa prática recomendada pela maioria dos guias.", "Necessário na grande maioria dos cenários de produção."],
                  "Container scape + root no host = comprometimento total. UserNS adiciona camada extra."),
                q("Capabilities padrão do Docker:",
                  "Devem ser reduzidas ao mínimo (drop ALL e add o que precisa).",
                  ["Devem ser ampliadas para cobrir qualquer cenário futuro, comportamento que só some quando alguém finalmente lê a documentação.", "São imutáveis e não podem ser alteradas pelo operador, escolha que economiza tempo agora e cobra o preço mais tarde.", "Não importam de verdade para a segurança do container, decisão que parece segura até o primeiro teste de penetração real."],
                  "Padrão dá ~14 capabilities. App web normal precisa de zero (com porta >1024)."),
                q("Imagem de 4GB com vulnerabilidades:",
                  "Crie versão menor e escaneie regularmente.",
                  ["Esse tamanho já é considerado ideal para produção.", "Não existe solução real para esse tipo de problema.", "Continue usando essa mesma imagem sem mudar muito pouco."],
                  "Cada MB que sobra é potencial CVE em pacote que a app nem usa."),
                q("Wolfi é:",
                  "Distro 'undistro' otimizada para SBOM e segurança.",
                  ["Um runtime de container alternativo ao containerd.", "Um substituto direto e completo do Docker Engine.", "Uma ferramenta de linter para Dockerfile."],
                  "Mantida pela Chainguard. Pacotes assinados, glibc-based, com SBOM nativo."),
                q("Imutabilidade da imagem:",
                  "Mesmo digest = mesmo conteúdo.",
                  ["O conteúdo muda a cada novo pull da imagem.", "Esse conceito de imutabilidade não existe no Docker.", "Pode mudar de conteúdo mesmo mantendo a mesma tag."],
                  "Princípio que torna deploys reproduzíveis e rollbacks confiáveis."),
                q("Fix de CVE em imagem base:",
                  "Requer rebuild da imagem do app.",
                  ["É aplicado automaticamente sem precisar de rebuild.", "Não é necessário fazer muito pouco além de esperar.", "Só é necessário quando a imagem roda em cluster K8s."],
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
flowchart LR
    CI["Pipeline de CI"] -- "push com digest" --> Reg["Registry"]
    Reg -- "pull por digest, imutável" --> Prod["Produção"]
    Reg -- "pull por tag, pode mudar" --> Dev["Ambiente de dev"]
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
                  ["Seguro o bastante para guardar qualquer imagem privada, comportamento que gera alerta falso ou silencia alerta real, dependendo do caso.", "Gratuito para qualquer volume de uso, sem limite, suposição que ignora como o recurso realmente se comporta em escala.", "Um substituto direto e completo do GHCR da GitHub, escolha que economiza tempo agora e cobra o preço mais tarde."],
                  "Para imagem privada de empresa, use GHCR/ECR/Harbor."),
                q("Rate limit do Docker Hub:",
                  "Pode bloquear pulls em CI sem auth.",
                  ["Só acontece quando o pull roda em produção.", "Esse tipo de limite simplesmente não existe no Docker Hub.", "Substitui a necessidade de configurar RBAC no registry."],
                  "100 pulls/6h por IP anônimo. Mirror interno resolve."),
                q("Registry self-hosted:",
                  "Maior controle mas requer manutenção.",
                  ["Não exige alguma manutenção contínua da equipe.", "Faz rotação automática de credenciais sem configuração.", "Costuma sair mais barato que qualquer opção gerenciada."],
                  "Você cuida de upgrade, backup, HA. Em escala pequena, SaaS sai mais barato."),
                q("Promotion entre ambientes:",
                  "Promove a mesma imagem (digest) entre dev/stg/prod.",
                  ["Só funciona promovendo a tag latest entre ambientes.", "Gera um build totalmente novo em cada ambiente.", "Não depende de algum tipo de versionamento de imagem."],
                  "Garante que o que passou em staging é o mesmo bit-a-bit que foi para prod."),
                q("Webhook em registry:",
                  "Dispara CI/CD quando imagem nova é publicada.",
                  ["Substitui a necessidade de configurar IAM no registry.", "Reduz o custo de armazenamento cobrado pelo registry.", "Apaga automaticamente imagens antigas do registry."],
                  "Base para GitOps com Argo Image Updater ou Flux."),
                q("Cleanup policies:",
                  "Apagam imagens antigas/não usadas.",
                  ["Aumentam o custo mensal cobrado pelo registry.", "Substituem a necessidade de configurar RBAC.", "Bloqueiam qualquer pull feito a partir do CI."],
                  "Mantenha tags semver e últimas N revisões; resto vai embora automaticamente."),
                q("Mirror de imagens públicas:",
                  "Reduz dependência externa e rate-limits.",
                  ["Costuma aumentar a latência percebida pelo cliente.", "Quebra a verificação de TLS entre cliente e registry.", "Substitui a etapa de build feita no pipeline de CI."],
                  "Harbor proxy cache, ECR pull-through. Opera como CDN para suas imagens base."),
                q("Para autenticar de fora:",
                  "Use docker login com PAT/OIDC.",
                  ["Reinicie o daemon containerd na máquina local.", "Conecte usando telnet direto na porta do registry.", "Substitua o servidor de DNS usado pela máquina."],
                  "Em CI moderno, OIDC > PAT. Tokens curtos > eternos."),
                q("Tag por commit SHA:",
                  "Garante rastreabilidade ao código exato.",
                  ["É uma prática considerada depreciada pela comunidade.", "Funciona de forma idêntica a usar a tag latest.", "Não é considerado uma prática segura pela indústria."],
                  "Útil em incidentes: 'qual código estava rodando?' = mesma SHA do git."),
                q("Em registries SaaS:",
                  "Confie mas verifique, leia o shared responsibility.",
                  ["Esse tipo de registry SaaS normalmente não cobra pelo uso.", "É completamente imune a qualquer outage do provedor.", "Dispensa qualquer necessidade de configurar RBAC."],
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
                  ["Funciona só em máquinas rodando Windows.", "Substitui o Kubernetes em qualquer cenário de produção.", "Sistemas distribuídos operando em escala global."],
                  "Em prod single-host, atende muitos casos. Para multi-host/HA real, use Swarm/Nomad/K8s."),
                q("Swarm e K8s diferem em:",
                  "Complexidade, K8s mais features e curva.",
                  ["A cor usada no logo de cada uma das ferramentas.", "O idioma principal da documentação oficial de cada uma.", "A linguagem de programação usada para escrever cada uma."],
                  "K8s tem CRDs, operadores, ecossistema enorme. Swarm é mais simples, com menos features."),
                q("Healthcheck em Compose:",
                  "Define como saber se serviço está saudável.",
                  ["É só um campo opcional sem algum efeito prático.", "Apaga o container automaticamente após cada execução.", "Substitui a necessidade de configurar logs no serviço."],
                  "Permite usar `depends_on: condition: service_healthy` para esperar dependência ficar pronta."),
                q("Volumes nomeados em Compose:",
                  "Persistem dados gerenciados pelo Docker.",
                  ["Não persistem algum dado além do ciclo do container.", "Guardam os dados só em memória RAM temporária.", "Exigem um caminho absoluto fixo no host."],
                  "Sobrevivem a `docker compose down`. Use `down -v` para remover."),
                q("Network bridge default:",
                  "Permite comunicação entre containers da mesma rede.",
                  ["Bloqueia qualquer comunicação entre os containers, atalho comum quando o prazo aperta e ninguém revisa depois.", "Substitui a necessidade de configurar DNS interno, suposição que só vale em ambiente de desenvolvimento, não em produção.", "Funciona só com endereçamento IPv6 configurado, algo que passa no code review quando ninguém olha com atenção."],
                  "Em user-defined bridge, containers se enxergam pelo nome (DNS interno)."),
                q("Compose v2 difere de v1:",
                  "É plugin do Docker CLI (`docker compose`), não binário separado.",
                  ["É exatamente a mesma coisa que a versão anterior, atalho que ignora exatamente o cenário que mais importa evitar.", "É uma versão totalmente gratuita, diferente da anterior, que só aparece como problema depois que o sistema já está em produção.", "Funciona só em máquinas rodando macOS, erro típico de configuração feita às pressas, sem revisão posterior."],
                  "v1 (`docker-compose`) está EOL. Use v2 sempre."),
                q("Para HA em Compose:",
                  "Use deploy.replicas em Swarm ou suba para K8s.",
                  ["O Compose sozinho já garante alta disponibilidade.", "Não existe alguma forma de conseguir alta disponibilidade.", "Basta configurar um backup periódico do serviço."],
                  "Compose puro é single-host. HA real exige Swarm mode ou K8s."),
                q("`depends_on` faz:",
                  "Define ordem de startup, mas não espera healthcheck por default.",
                  ["Apaga as dependências declaradas no arquivo compose.", "Espera vários healthchecks internos ficarem saudáveis antes de iniciar.", "Só testa a conectividade entre os serviços."],
                  "Para esperar saudável, use `condition: service_healthy` (Compose v2 spec)."),
                q("Override file:",
                  "Permite sobrepor configs por ambiente.",
                  ["Só funciona para o ambiente de desenvolvimento local.", "Substitui por completo o arquivo compose principal.", "Apaga a configuração de rede do arquivo principal."],
                  "Chain: base.yml + override.yml combina; chave repetida sobrescreve."),
                q("Nomad pode rodar:",
                  "Containers, binários e VMs.",
                  ["Só consegue rodar aplicações escritas em Java.", "Só consegue rodar aplicações dentro do browser.", "Só consegue rodar workloads dentro de um cluster K8s."],
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
                  ["Uma ferramenta de linter para checar estilo de código.", "Um tipo específico de configuração de TLS.", "Um mecanismo de backup automático do artefato."],
                  "Inclui versão, supplier, hash. Permite responder 'tenho Log4j 2.14?' em segundos."),
                q("Formato aberto popular:",
                  "CycloneDX e SPDX.",
                  ["Um formato de token usado para autenticação.", "Só um arquivo simples no formato CSV.", "Um arquivo de texto formatado em Markdown."],
                  "Os dois são padrões reconhecidos pelo NIST e usados pela CISA."),
                q("SBOM ajuda em:",
                  "Resposta rápida a CVEs.",
                  ["Ajuda a calcular o preço cobrado pelo fornecedor.", "Serve como material de marketing para o produto.", "Ajuda a configurar registros de DNS do serviço."],
                  "Em Log4Shell, empresas com SBOM consultaram em segundos; o resto fez forensics manual."),
                q("VEX descreve:",
                  "Se uma vulnerabilidade afeta de fato seu produto.",
                  ["A versão específica de TLS usada na conexão, erro comum de quem aprendeu por tentativa e erro, sem revisar a documentação oficial.", "Um tipo específico de log gerado pela aplicação, prática que gera falso senso de segurança no time.", "Uma cópia de backup guardada do artefato final, algo que passa no code review quando ninguém olha com atenção."],
                  "Reduz fadiga: 'CVE existe mas função não é alcançável no nosso uso'."),
                q("SBOM deve ser:",
                  "Legível por máquina, gerado automaticamente.",
                  ["Preenchido manualmente a cada novo release.", "Entregue só em formato PDF fechado.", "Escrito e revisado só por humanos, sem automação."],
                  "Manual é desatualizado e impreciso. Geração no build é regra."),
                q("Syft gera SBOM de:",
                  "Imagens, diretórios, archives.",
                  ["Só consegue gerar SBOM de projetos em Python.", "Só consegue gerar SBOM a partir de arquivo zip.", "Só consegue gerar SBOM de imagem Docker."],
                  "Suporta Python, Node, Java, Go, Rust, etc. Detecta ecossistema automaticamente."),
                q("Após Log4Shell, SBOM virou:",
                  "Requisito quase regulatório em muitos setores.",
                  ["Uma opção considerada desnecessária pela maioria.", "Uma exigência que existe só no Brasil.", "Só um modal de interface dentro da ferramenta."],
                  "EO 14028 (EUA) tornou SBOM obrigatório para compras federais."),
                q("SBOM e SCA:",
                  "Complementares, SBOM é o inventário, SCA é a análise.",
                  ["Ferramentas substitutas uma da outra, raramente usadas juntas.", "Duas ferramentas concorrentes que competem pelo mesmo mercado.", "Dois termos sinônimos para exatamente a mesma coisa."],
                  "Trivy faz ambos. SBOM é o 'o quê'; SCA é 'tem CVE/EPSS no quê'."),
                q("Distribuir SBOM:",
                  "Junto do artefato, em registry OCI ou anexo do release.",
                  ["Enviado manualmente por e-mail para o time de segurança.", "Não precisa ser distribuído junto de muito pouco.", "Distribuído só por e-mail para o time responsável."],
                  "Cosign attach sbom anexa ao manifest no registry. Quem puxa a imagem pode puxar a SBOM."),
                q("SBOM sem governança é:",
                  "Arquivo morto, precisa rotina de uso.",
                  ["Substitui a necessidade de aplicar qualquer patch.", "Completamente inútil em qualquer cenário de uso.", "Um gerador automático de patches para o time."],
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
                  ["Só um modal de interface para rodar lint.", "Só uma ferramenta de gestão de identidade e acesso.", "Só um framework de frontend para construir telas."],
                  "Não substitui infra; padroniza e expõe via UX/APIs amigáveis."),
                q("Golden path significa:",
                  "Caminho recomendado e padronizado para criar/operar serviços.",
                  ["Um endpoint específico dentro do serviço de IAM, prática que só aparece como erro grave durante um incidente real.", "Só o logo dourado usado na marca da plataforma, decisão que parece segura até o primeiro teste de penetração real.", "Um tipo específico de configuração de TLS de rede, suposição incorreta sobre como o sistema realmente se comporta sob estresse."],
                  "Dev pode sair do golden path com justificativa, mas tem que arcar com manutenção própria."),
                q("Backstage é:",
                  "Portal de devs OSS feito pelo Spotify.",
                  ["Um pipeline de CI mantido internamente pelo Spotify.", "Uma IDE proprietária vendida como produto fechado.", "Um servidor de DNS interno usado pela plataforma."],
                  "Adotado por Spotify, Netflix, American Airlines, etc. Hospedado pela CNCF."),
                q("IDP visa:",
                  "Reduzir o custo cognitivo da operação.",
                  ["Centralizar o storage usado por vários times.", "Aumentar a burocracia envolvida em cada deploy.", "Reduzir a quantidade de testes exigida no pipeline."],
                  "Dev foca em código de negócio; plataforma cuida do resto."),
                q("Self-service em IDP:",
                  "Permite dev provisionar recursos sem ticket.",
                  ["Acaba com a necessidade de rodar qualquer teste.", "Aumenta a dependência do time de SRE em cada request.", "Substitui a necessidade de configurar RBAC no cluster."],
                  "Com guard-rails (Policy as Code), risco fica baixo. Sem guard-rails, vira faroeste."),
                q("Templates em IDP:",
                  "Bootstrap padronizado de serviços.",
                  ["Reduzem a qualidade final do serviço entregue.", "Substituem a etapa de build feita no pipeline de CI.", "Apagam as configurações de segurança do serviço."],
                  "Garantem que cada novo serviço sai com Dockerfile, CI, monitoring, segurança alinhados."),
                q("Catálogo de serviços:",
                  "Inventário com dono, deps, dashboards.",
                  ["Um substituto direto e completo do próprio Git.", "Um pipeline de CI/CD mantido pela plataforma.", "Um disco compartilhado montado em vários serviços."],
                  "Em incidente: 'quem é dono desse microsserviço?' resolve em 1 clique."),
                q("IDP X K8s diretamente:",
                  "IDP esconde a complexidade do K8s atrás de UX.",
                  ["O Kubernetes substitui por completo qualquer IDP.", "São exatamente a mesma coisa, sem diferença real.", "Não têm alguma relação prática entre si."],
                  "Dev raramente edita YAML de K8s direto; preenche form e plataforma gera tudo."),
                q("Métrica de sucesso de IDP:",
                  "Time-to-production de novos serviços.",
                  ["O número de linhas escritas em cada chart Helm.", "O número total de tickets abertos no mês.", "O tamanho do time de SRE responsável pela plataforma."],
                  "Mede impacto real. Combine com DORA e NPS dos devs."),
                q("Time topology recomendada:",
                  "Stream-aligned + Platform team + Enabling team.",
                  ["Só um time dedicado exclusivamente à segurança.", "Só um time dedicado exclusivamente ao SRE.", "Só os desenvolvedores organizados sem algum outro time."],
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
<div class="mermaid">
flowchart LR
    Request["Pedido de criar recurso"] --> Admission["Admission controller"]
    Admission --> Policy{"Passa nas políticas, OPA ou Kyverno?"}
    Policy -- "Sim" --> Create["Recurso é criado"]
    Policy -- "Não" --> Reject["Pedido rejeitado"]
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
                  ["Reduzir a quantidade de testes exigida no pipeline.", "Substituir por completo a etapa de CI do pipeline.", "Apagar as políticas de IAM configuradas na conta."],
                  "Auditoria fica simples: git log mostra quando regra mudou e quem aprovou."),
                q("OPA usa linguagem:",
                  "Rego.",
                  ["YAML puro.", "Bash.", "Java."],
                  "Rego é declarativa, parecida com Datalog. Curva inicial existe, mas paga rápido."),
                q("Kyverno é específico para:",
                  "Kubernetes.",
                  ["Só funciona dentro de charts escritos em Helm.", "Funções serverless rodando como Cloud Functions.", "Só funciona dentro da nuvem da AWS."],
                  "Diferencial: políticas em YAML, sem precisar Rego. Boa entrada para times K8s."),
                q("Admission controller:",
                  "Intercepta criação/update de recursos antes de persistir.",
                  ["Apaga clusters inteiros automaticamente sem aviso, prática que gera falso senso de segurança no time.", "Substitui a necessidade de usar Helm no deploy, prática que aumenta a superfície de ataque sem ninguém perceber.", "Reseta a configuração de DNS interna do cluster, decisão que ignora justamente o motivo pelo qual a prática recomendada existe."],
                  "Validating (rejeita) e mutating (modifica). Webhook chamado pelo apiserver."),
                q("Conftest serve para:",
                  "Validar arquivos de configuração com OPA fora do K8s.",
                  ["Substituir por completo o Terraform usado na infra, erro comum de quem aprendeu por tentativa e erro, sem revisar a documentação oficial.", "Mostrar os logs gerados durante o deploy do cluster, abordagem que funciona bem até o primeiro pico de carga real.", "Substituir por completo o uso do Docker no build, suposição que só vale em ambiente de desenvolvimento, não em produção."],
                  "Roda em CI: `conftest test plan.json` aplica políticas Rego."),
                q("Policy de 'nenhum bucket público':",
                  "Pode ser aplicada em CI (pre-merge) e cluster (admission).",
                  ["Só pode ser aplicada já em ambiente de produção, prática que gera falso senso de segurança no time.", "Só pode ser aplicada abrindo um ticket manual, que só aparece como problema depois que o sistema já está em produção.", "Não é tecnicamente possível aplicar esse tipo de regra, comportamento que só some quando alguém finalmente lê a documentação."],
                  "Defesa em camadas: PR bloqueia, mas se algo passar, admission impede no provisionamento."),
                q("Falha em policy deve:",
                  "Bloquear o merge/deploy ou marcar não-compliant.",
                  ["Aprovar o merge mesmo assim, sem restrição alguma.", "Ser ignorada por padrão em qualquer pipeline.", "Ser silenciada automaticamente pela ferramenta."],
                  "Em ambientes regulados, audit trail mostra exceção justificada."),
                q("Fast feedback ao dev:",
                  "Rodar policy localmente via pre-commit.",
                  ["Só rodar a policy já em ambiente de produção.", "Substituir por completo a etapa de CI do pipeline.", "Só rodar a policy manualmente pelo console."],
                  "Conftest pre-commit ajuda dev a corrigir antes mesmo do PR."),
                q("Difference SAST vs PaC:",
                  "SAST código; PaC config/infra/cluster.",
                  ["São exatamente a mesma coisa, sem diferença real.", "SAST analisa só arquivos escritos em YAML.", "PaC analisa só código escrito em Java."],
                  "SAST olha código fonte; PaC olha configurações de infra/runtime."),
                q("Govern via PaC reduz:",
                  "Decisões caso-a-caso e configura tribal knowledge em código.",
                  ["Apaga o histórico de decisões tomadas pelo time, decisão que parece razoável isolada, mas quebra a arquitetura no conjunto.", "Aumenta o número de tickets abertos para aprovação, comportamento que só é notado quando alguém audita os logs depois.", "Reduz a visibilidade que o time tem sobre as regras, decisão que parece inofensiva isolada, mas se acumula com o tempo."],
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
flowchart LR
    App["App rodando em ambiente isolado"] --> DAST["Scanner DAST ataca de fora"]
    DAST --> Report["Reporta a vulnerabilidade encontrada"]
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
                  ["Só um arquivo de configuração escrito em YAML.", "Só o código de infraestrutura definido em IaC.", "Só o código-fonte da aplicação, sem execução."],
                  "Por isso DAST roda em staging/QA com dados sintéticos."),
                q("ZAP em modo baseline:",
                  "Faz scan rápido sem ataques agressivos.",
                  ["Substitui por completo a necessidade de pentest.", "Só analisa o código de infraestrutura em IaC.", "Só analisa o código do frontend da aplicação."],
                  "Verifica passivamente cabeçalhos, redirects, configs. Quase sem risco para o app."),
                q("XSS é:",
                  "Cross-site scripting, injeção de JS via input.",
                  ["Um tipo específico de configuração de TLS, decisão que parece inofensiva isolada, mas se acumula com o tempo.", "Um mecanismo de backup automático do banco, atalho comum quando o prazo aperta e ninguém revisa depois.", "Uma variante específica de injeção via SQL, decisão que parece razoável isolada, mas quebra a arquitetura no conjunto."],
                  "Reflected, stored, DOM-based. Mitigação: output encoding, CSP."),
                q("SQLi é:",
                  "SQL Injection, input que altera queries.",
                  ["Um problema que só ocorre em documentos XML.", "Um problema que costuma acontecer no browser.", "Um tipo específico de configuração de DNS."],
                  "Mitigação: prepared statements / ORM com parameterized queries. Nunca string concat."),
                q("Idealmente DAST roda:",
                  "Em pipeline contra ambiente isolado.",
                  ["Manualmente, testando direto em produção real.", "Só faz sentido rodar já em produção real.", "Simplesmente não roda em algum tipo de pipeline."],
                  "Staging com dados sintéticos. Em produção, só com autorização e janela controlada."),
                q("Auth em DAST:",
                  "Permite cobrir endpoints autenticados.",
                  ["Bloqueia completamente a execução do scan.", "É totalmente opcional em qualquer cenário.", "Substitui a necessidade de usar senha no login."],
                  "Sem auth, scanner só vê página de login. Config 'authentication context' no scanner."),
                q("Headers de segurança:",
                  "DAST checa CSP, HSTS, X-Frame-Options etc.",
                  ["Só verifica a configuração de TLS da conexão.", "Só verifica os registros de DNS do domínio.", "Só verifica os resultados de uma análise SAST."],
                  "Headers como CSP, HSTS, X-Content-Type-Options reduzem risco com config simples."),
                q("CSRF:",
                  "Cross-site request forgery, request feita em nome do usuário sem consentimento.",
                  ["Um tipo específico de algoritmo de criptografia, suposição que raramente se sustenta fora do ambiente controlado de laboratório.", "Um padrão específico de configuração de DNS, erro típico de configuração feita às pressas, sem revisão posterior.", "Uma variante específica de autenticação multifator, erro que só é percebido quando o time de operação já está lidando com o incidente."],
                  "Mitigação: CSRF token, SameSite cookies, double-submit cookie."),
                q("Pentest difere de DAST porque:",
                  "Pentest envolve criatividade humana e exploração.",
                  ["O DAST é feito de forma totalmente manual por humanos.", "Não existe diferença real entre as duas abordagens.", "O pentest é feito só rodando scripts automatizados."],
                  "Pentester encadeia falhas baixas em compromisso. DAST sozinho raramente faz isso."),
                q("DAST exige consentimento:",
                  "Sim, sempre, antes de testar sistemas alheios.",
                  ["Só é necessário quando se usa uma VPN corporativa.", "Não, qualquer sistema pode ser testado livremente.", "Só é permitido testar durante o fim de semana."],
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
<div class="mermaid">
flowchart TD
    Req["GET /pedidos/123"] --> Auth{"Usuário autenticado?"}
    Auth -- "Não" --> Deny["401"]
    Auth -- "Sim" --> Owner{"O pedido 123 pertence a este usuário?"}
    Owner -- "Não" --> Forbid["403, previne BOLA"]
    Owner -- "Sim" --> Allow["Retorna o pedido"]
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
                  ["São exatamente o mesmo protocolo, sem diferença real, resultado típico de copiar configuração de outro projeto sem adaptar.", "O OAuth puro já inclui um id_token por padrão, abordagem que ignora o cenário de falha mais provável na prática.", "O OIDC é considerado uma camada menos segura que o OAuth, prática ainda comum em sistema legado que raramente é atualizado."],
                  "OAuth = autorização (delegação de acesso). OIDC = identidade (id_token assinado)."),
                q("BOLA (Broken Object Level Auth):",
                  "Checar autorização no nível do recurso individual.",
                  ["Um algoritmo de criptografia considerado fraco.", "Um tipo específico de configuração de TLS.", "Um programa de recompensa por vulnerabilidades encontradas."],
                  "API que aceita /orders/{id} sem checar se o usuário é dono do pedido."),
                q("Rate limit ajuda contra:",
                  "Brute force e DoS.",
                  ["Melhorar a performance geral de resposta da API.", "Fortalecer a configuração de TLS usada na conexão.", "Melhorar o formato dos logs gerados pela API."],
                  "Camadas: gateway + app. Use Redis para sliding window distribuído."),
                q("Validação de schema:",
                  "Rejeita payloads que não obedecem à API spec.",
                  ["Só é aplicada já em ambiente de produção.", "Substitui a necessidade de autenticar a chamada.", "Aceita qualquer payload enviado, sem restrição."],
                  "OpenAPI + framework auto-validador (FastAPI, Spring). Reduz exploits de input."),
                q("Token JWT deve:",
                  "Ter exp curta + refresh token + assinatura forte.",
                  ["Ser eterno, sem alguma data de expiração definida.", "Conter a senha do usuário em texto plano no payload.", "Ser emitido sem alguma assinatura criptográfica."],
                  "Algoritmo: RS256/EdDSA, não 'none'. Exp típico: 5-15 min para acesso."),
                q("CORS mal configurado:",
                  "Permite frontends maliciosos chamarem sua API.",
                  ["Acelera o carregamento de páginas no browser.", "Substitui a necessidade de autenticar a chamada.", "Comprime o tamanho da resposta enviada pela API."],
                  "Allow-list explícito de origins; nunca `*` com `credentials: true`."),
                q("API Gateway serve para:",
                  "Centralizar auth, rate limit, observability.",
                  ["Apagar automaticamente microserviços sem uso.", "Substituir por completo o cluster de Kubernetes.", "Substituir a necessidade de configurar IAM na conta."],
                  "Tira responsabilidades transversais de cada serviço. Kong, AWS API Gateway, NGINX."),
                q("Mass assignment:",
                  "Cliente injeta campos não esperados no body (ex.: is_admin).",
                  ["Um tipo específico de configuração de TLS, resultado típico de copiar configuração de outro projeto sem adaptar.", "Uma categoria específica de log gerado pela API, comportamento que só é notado quando alguém audita os logs depois.", "Um mecanismo de backup automático do banco de dados, atalho que parece seguro isolado, mas quebra quando combinado com outros sistemas."],
                  "Mitigação: DTOs com allow-list explícito; nunca passar request.json direto pro ORM."),
                q("Excessive Data Exposure:",
                  "API retorna mais campos que o necessário.",
                  ["Um mecanismo de backup automático dos dados da API.", "Um tipo específico de configuração de DNS.", "Uma técnica de otimização de performance da API."],
                  "Use response models específicos por endpoint. Cuide de PII e segredos no retorno."),
                q("Webhook seguro precisa:",
                  "Assinatura HMAC verificada no destino.",
                  ["Só funcionar sobre endereçamento IPv6 configurado.", "Funcionar sem algum tipo de autenticação no destino.", "Trafegar por HTTP puro, sem alguma criptografia."],
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
flowchart LR
    S1["Serviço 1"] --> Agent["Agente de coleta"]
    S2["Serviço 2"] --> Agent
    S3["Serviço 3"] --> Agent
    Agent --> Central["Armazenamento centralizado"]
    Central --> Dash["Dashboard e alerta"]
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
                  ["Aumentar a latência percebida entre os serviços.", "Substituir a necessidade de manter backup dos dados.", "Reduzir diretamente o custo de infraestrutura do time."],
                  "Permite seguir trace_id por 5 microsserviços em uma busca só."),
                q("Loki indexa:",
                  "Apenas labels, não o conteúdo do log.",
                  ["Grande parte do o conteúdo completo de cada linha de log.", "Só o timestamp de cada linha de log indexada.", "Só o nível de severidade de cada linha de log."],
                  "Por isso é barato. Conteúdo é comprimido e lido sob demanda. Queries por substring varrem."),
                q("ELK stack contém:",
                  "Elasticsearch + Logstash + Kibana.",
                  ["Postgres, Redis e Mongo combinados num só stack.", "Docker, Kubernetes e Helm combinados num só stack.", "Apache, Nginx e HAProxy combinados num só stack."],
                  "Variantes: EFK (Fluentd no lugar de Logstash). OpenSearch é fork ASL2."),
                q("Retenção precisa equilibrar:",
                  "Custo vs requisitos de compliance.",
                  ["Só a configuração de TLS usada na transmissão.", "Só o SLA acordado com o cliente final.", "Só o custo de armazenamento cobrado pelo provedor."],
                  "Audit logs em alguns setores precisam 1+ ano. Logs de debug raramente."),
                q("Anonimização em logs:",
                  "Remover PII para reduzir risco em vazamentos.",
                  ["Substitui a necessidade de usar encryption nos dados.", "É uma prática proibida por qualquer regulação vigente.", "É totalmente opcional em qualquer contexto regulado."],
                  "Hash de email, mascarar CPF (***.***.123-45). LGPD/GDPR olham para isso."),
                q("Vector é:",
                  "Pipeline de logs/metrics performant em Rust.",
                  ["Uma linguagem de programação criada pela Mozilla.", "Um tipo específico de cluster gerenciado do Kubernetes.", "Um banco de dados otimizado para série temporal."],
                  "Substitui Logstash e Fluentd com performance superior. VRL para transformações."),
                q("Estruturar logs em JSON:",
                  "Permite buscar por campo.",
                  ["Apaga os timestamps de cada linha ao estruturar.", "Substitui a necessidade de coletar métricas.", "Aumenta em dez vezes o tamanho do arquivo de log."],
                  "Tamanho cresce ~30%, mas valor de query é incomparável."),
                q("Sampling:",
                  "Reduz volume preservando representatividade.",
                  ["Não tem efeito algum sobre o volume de dados.", "Substitui a necessidade de definir uma retenção.", "Aumenta o volume total de dados armazenados."],
                  "Em traces, sampling de 1-10% é comum. Em logs, sampling do INFO mantendo todos os ERROR."),
                q("Tracing (distributed):",
                  "Complementa logs com fluxo entre serviços.",
                  ["Substitui por completo a necessidade de manter logs.", "Só funciona para aplicações rodando na web.", "Substitui a necessidade de coletar métricas."],
                  "Spans em árvore mostram tempo gasto em cada step. Combine com logs por trace_id."),
                q("Log com PII em CW:",
                  "Pode violar LGPD/GDPR, sanitize antes.",
                  ["Sem algum risco legal associado a essa prática.", "É uma prática necessária em qualquer cenário.", "Completamente imune a qualquer tipo de auditoria."],
                  "Mesmo logs internos podem ser exfiltrados. ANPD (BR) já multou por logs imprudentes."),
            ],
        },
    ],
}
