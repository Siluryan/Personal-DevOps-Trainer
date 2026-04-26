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
                    "<h3>1. O que é um container, fisicamente</h3>"
                    "<p>Container <strong>não é</strong> uma VM leve. Container é "
                    "<strong>um ou mais processos Linux normais</strong>, isolados de "
                    "outros processos via primitives do kernel:</p>"
                    "<ul>"
                    "<li><strong>Namespaces</strong> (isolamento):"
                    "<ul>"
                    "<li><code>PID</code>: processos dentro do container só veem outros "
                    "do mesmo container; PID 1 é o seu app.</li>"
                    "<li><code>NET</code>: interface de rede, tabela de roteamento, "
                    "iptables próprios.</li>"
                    "<li><code>MNT</code>: filesystem isolado.</li>"
                    "<li><code>UTS</code>: hostname/domain próprio.</li>"
                    "<li><code>IPC</code>: shared memory, semáforos próprios.</li>"
                    "<li><code>USER</code>: UID/GID mapeáveis (root no container ≠ root "
                    "no host se configurado).</li>"
                    "<li><code>cgroup</code>: o próprio cgroup é namespaced.</li>"
                    "<li><code>time</code>: clock próprio (mais raro).</li>"
                    "</ul></li>"
                    "<li><strong>cgroups</strong> (limites): CPU, memória, IO, PIDs "
                    "máximos. Sem cgroup, container pode comer 100% da CPU/RAM do host.</li>"
                    "<li><strong>Capabilities</strong>: subdivisão de root. Em vez de "
                    "'root pode tudo', você pode dar só <code>NET_BIND_SERVICE</code> "
                    "(bind em porta &lt;1024).</li>"
                    "<li><strong>Seccomp</strong>: filtro de syscalls permitidas.</li>"
                    "<li><strong>AppArmor/SELinux</strong>: mandatory access control "
                    "complementar.</li>"
                    "</ul>"
                    "<p>Demonstre você mesmo:</p>"
                    "<pre><code>$ docker run -d --name web nginx\n"
                    "$ docker top web\n"
                    "PID  USER   CMD\n"
                    "1234 root   nginx: master process\n"
                    "$ ps -ef | grep 1234\n"
                    "root  1234  ...  nginx: master process   # mesmo PID, mas só visível no host</code></pre>"
                    "<p>Compartilha o kernel do host. Por isso é leve: sem boot, sem "
                    "kernel próprio, sem hardware virtual. Trade-off: container Linux só "
                    "roda em host Linux (Docker Desktop em Mac/Win usa VM Linux por "
                    "trás).</p>"

                    "<h3>2. Imagem ≠ Container</h3>"
                    "<p>Termos confundem iniciantes:</p>"
                    "<ul>"
                    "<li><strong>Imagem</strong>: template imutável, snapshot do filesystem "
                    "+ metadados (CMD, ENV, EXPOSE...). Composta por <em>camadas</em> "
                    "read-only sobrepostas (overlayfs).</li>"
                    "<li><strong>Container</strong>: instância em execução de uma imagem, "
                    "com uma camada writable por cima. Você pode subir 100 containers da "
                    "mesma imagem; cada um com env vars/volumes/redes diferentes.</li>"
                    "<li><strong>Registry</strong>: armazena imagens (Docker Hub, GHCR, "
                    "ECR, etc.).</li>"
                    "<li><strong>Tag</strong>: alias humano para um digest "
                    "(<code>nginx:1.25.3</code> aponta para um sha256 específico).</li>"
                    "<li><strong>Digest</strong>: <code>sha256:f0a1b2...</code>; "
                    "imutável, único.</li>"
                    "</ul>"

                    "<h3>3. Dockerfile produtivo</h3>"
                    "<p>Receita declarativa para construir a imagem. <strong>Cada "
                    "instrução vira uma camada cacheada</strong>. Ordem importa "
                    "muito:</p>"
                    "<pre><code># Dockerfile RUIM (cache invalida toda hora)\n"
                    "FROM python:3.12\n"
                    "COPY . /app                    # qualquer mudança em código invalida tudo abaixo\n"
                    "RUN pip install -r /app/requirements.txt\n"
                    "WORKDIR /app\n"
                    "CMD [\"python\", \"main.py\"]</code></pre>"
                    "<pre><code># Dockerfile BOM (cache amigável)\n"
                    "FROM python:3.12-slim AS base\n"
                    "ENV PYTHONUNBUFFERED=1 \\\n"
                    "    PYTHONDONTWRITEBYTECODE=1 \\\n"
                    "    PIP_NO_CACHE_DIR=1\n"
                    "\n"
                    "WORKDIR /app\n"
                    "\n"
                    "# Copia só requirements primeiro, camada cacheada se reqs não mudam\n"
                    "COPY requirements.txt .\n"
                    "RUN pip install --no-cache-dir -r requirements.txt\n"
                    "\n"
                    "# Código por último, mudanças aqui não invalidam pip install\n"
                    "COPY . .\n"
                    "\n"
                    "RUN useradd -m -u 1000 app && chown -R app:app /app\n"
                    "USER app\n"
                    "\n"
                    "EXPOSE 8000\n"
                    "HEALTHCHECK --interval=30s --timeout=3s --retries=3 \\\n"
                    "  CMD curl -f http://localhost:8000/health || exit 1\n"
                    "\n"
                    "CMD [\"gunicorn\", \"--bind\", \"0.0.0.0:8000\", \"app.wsgi\"]</code></pre>"
                    "<p>Detalhes importantes:</p>"
                    "<ul>"
                    "<li><strong>Base slim/alpine/distroless</strong>: menos bytes, "
                    "menos CVEs.</li>"
                    "<li><strong>Tag específica</strong>: <code>3.12-slim</code>, não "
                    "<code>latest</code> nem <code>3</code>.</li>"
                    "<li><strong>ENV</strong>: <code>PYTHONUNBUFFERED=1</code> garante "
                    "logs em stdout sem buffering.</li>"
                    "<li><strong>WORKDIR</strong> definido cedo.</li>"
                    "<li><strong>USER não-root</strong>: princípio do menor privilégio. "
                    "Se atacante escapar do app, não é root no namespace.</li>"
                    "<li><strong>HEALTHCHECK</strong>: orquestrador sabe se app está "
                    "respondendo, não só 'processo vivo'.</li>"
                    "<li><strong>CMD vs ENTRYPOINT</strong>: CMD é override-friendly; "
                    "ENTRYPOINT trava o comando.</li>"
                    "<li><strong>JSON form</strong>: <code>CMD [\"app\"]</code> não passa "
                    "por shell, sem expansão acidental.</li>"
                    "</ul>"

                    "<h3>4. Multi-stage build: imagens menores e mais seguras</h3>"
                    "<p>Use uma imagem 'gorda' para compilar e copie só o resultado "
                    "para uma imagem mínima de runtime. Reduz tamanho em ordens de "
                    "grandeza.</p>"
                    "<pre><code># Stage 1: build com toolchain completa\n"
                    "FROM golang:1.22 AS builder\n"
                    "WORKDIR /src\n"
                    "COPY go.mod go.sum ./\n"
                    "RUN go mod download\n"
                    "COPY . .\n"
                    "RUN CGO_ENABLED=0 GOOS=linux go build -ldflags='-s -w' -o /out/app ./cmd/app\n"
                    "\n"
                    "# Stage 2: runtime mínimo (distroless: sem shell, sem apt, ~20MB)\n"
                    "FROM gcr.io/distroless/static-debian12:nonroot\n"
                    "COPY --from=builder /out/app /app\n"
                    "USER nonroot\n"
                    "EXPOSE 8080\n"
                    "ENTRYPOINT [\"/app\"]</code></pre>"
                    "<p>Resultado: ~20MB em vez de ~800MB. Sem shell, sem apt, "
                    "atacante que escapar do app encontra ambiente vazio.</p>"
                    "<p>Em Python:</p>"
                    "<pre><code>FROM python:3.12-slim AS builder\n"
                    "RUN apt-get update && apt-get install -y --no-install-recommends \\\n"
                    "      build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*\n"
                    "WORKDIR /app\n"
                    "RUN python -m venv /opt/venv\n"
                    "ENV PATH=\"/opt/venv/bin:$PATH\"\n"
                    "COPY requirements.txt .\n"
                    "RUN pip install --no-cache-dir -r requirements.txt\n"
                    "\n"
                    "FROM python:3.12-slim\n"
                    "RUN apt-get update && apt-get install -y --no-install-recommends \\\n"
                    "      libpq5 && rm -rf /var/lib/apt/lists/*\n"
                    "COPY --from=builder /opt/venv /opt/venv\n"
                    "WORKDIR /app\n"
                    "COPY . .\n"
                    "ENV PATH=\"/opt/venv/bin:$PATH\"\n"
                    "RUN useradd -m -u 1000 app && chown -R app /app\n"
                    "USER app\n"
                    "CMD [\"gunicorn\", \"app.wsgi\"]</code></pre>"

                    "<h3>5. Networking</h3>"
                    "<p>Tipos de redes Docker:</p>"
                    "<ul>"
                    "<li><strong>bridge</strong> (default): rede privada do daemon. "
                    "Containers conversam por IP; resolução por nome só com "
                    "<em>user-defined bridge</em>.</li>"
                    "<li><strong>user-defined bridge</strong>: containers conversam "
                    "por nome (DNS interno). Padrão para multi-container.</li>"
                    "<li><strong>host</strong>: container compartilha stack de rede do "
                    "host, sem isolamento de porta. Performance máxima, segurança "
                    "mínima.</li>"
                    "<li><strong>none</strong>: sem rede.</li>"
                    "<li><strong>overlay</strong>: rede multi-host (Swarm/K8s).</li>"
                    "<li><strong>macvlan</strong>: container ganha MAC própria; vira "
                    "'host' na rede física.</li>"
                    "</ul>"
                    "<pre><code>$ docker network create app-net\n"
                    "$ docker run -d --name db --network app-net postgres\n"
                    "$ docker run -d --name api --network app-net -e DB_HOST=db myapp\n"
                    "# api consegue conectar em 'db' por nome (DNS interno)</code></pre>"
                    "<p>Port mapping: <code>-p 8080:80</code> mapeia porta 8080 do "
                    "host para 80 do container.</p>"

                    "<h3>6. Volumes e persistência</h3>"
                    "<ul>"
                    "<li><strong>Volume nomeado</strong>: gerenciado pelo Docker, "
                    "armazenado em <code>/var/lib/docker/volumes/</code>. Sobrevive a "
                    "<code>docker rm</code>. Ideal para prod.</li>"
                    "<li><strong>Bind mount</strong>: mapeia diretório do host. "
                    "Excelente para dev (código local refletido no container). Em prod, "
                    "cuidado com permissões e portabilidade.</li>"
                    "<li><strong>tmpfs mount</strong>: armazenado em RAM, sumiu com "
                    "container. Bom para dados sensíveis temporários.</li>"
                    "</ul>"
                    "<pre><code>$ docker volume create pgdata\n"
                    "$ docker run -d --name db -v pgdata:/var/lib/postgresql/data postgres\n"
                    "\n"
                    "# Bind mount em dev\n"
                    "$ docker run -d -v $(pwd):/app -w /app python:3.12 python main.py\n"
                    "\n"
                    "# tmpfs para sessões temporárias\n"
                    "$ docker run -d --tmpfs /tmp:rw,size=100m myapp</code></pre>"

                    "<h3>7. .dockerignore: economia e segurança</h3>"
                    "<p><code>docker build</code> envia <em>tudo</em> do diretório "
                    "atual ('build context') ao daemon. Sem .dockerignore, vai "
                    "<code>.git</code>, <code>node_modules</code>, <code>.env</code>, "
                    "logs antigos. Lento e perigoso (segredo em <code>.env</code> pode "
                    "vazar para imagem se você fizer <code>COPY . .</code>).</p>"
                    "<pre><code># .dockerignore\n"
                    ".git\n"
                    ".gitignore\n"
                    "node_modules/\n"
                    "__pycache__/\n"
                    "*.pyc\n"
                    ".pytest_cache/\n"
                    ".env\n"
                    ".env.*\n"
                    "*.log\n"
                    ".vscode/\n"
                    ".idea/\n"
                    "Dockerfile\n"
                    "docker-compose*.yml\n"
                    "README.md</code></pre>"

                    "<h3>8. Boas práticas (12-factor app)</h3>"
                    "<p>Princípios da metodologia 12-factor (heroku) aplicáveis ao "
                    "Docker:</p>"
                    "<ul>"
                    "<li><strong>Config via env vars</strong>: nada de "
                    "<code>config.prod.yml</code> versus <code>config.dev.yml</code> "
                    "embutidos. Imagem é a mesma, env muda.</li>"
                    "<li><strong>Logs em stdout/stderr</strong>: orquestrador captura. "
                    "Não escreva em arquivo.</li>"
                    "<li><strong>Stateless</strong>: estado em DB/cache externo, não "
                    "em filesystem local. Permite escala horizontal sem dor.</li>"
                    "<li><strong>Build → Release → Run</strong>: estágios separados. "
                    "Imagem é build; deploy é release; container rodando é run.</li>"
                    "<li><strong>Processes</strong>: 1 processo principal por "
                    "container. Para reaping de zombies (PID 1 problem), use "
                    "<code>tini</code> ou <code>--init</code>.</li>"
                    "<li><strong>Disposability</strong>: app deve subir rápido (cold "
                    "start &lt;5s) e desligar limpo (handle SIGTERM, drain).</li>"
                    "<li><strong>Dev/prod parity</strong>: mesma imagem dev e prod, "
                    "minimizando diferenças.</li>"
                    "</ul>"

                    "<h3>9. PID 1 problem e tini</h3>"
                    "<p>PID 1 no Linux tem responsabilidades especiais: deve adotar "
                    "processos órfãos e fazer reaping de zombies, e propaga sinais. "
                    "Apps típicas (Python, Node) não fazem isso. Resultado:</p>"
                    "<ul>"
                    "<li>Subprocessos viram zombies, acumulam PIDs.</li>"
                    "<li>SIGTERM do <code>docker stop</code> não chega aos filhos.</li>"
                    "<li>Container demora 10s para morrer (timeout) e é SIGKILL.</li>"
                    "</ul>"
                    "<p>Solução: <code>tini</code> como init mínimo:</p>"
                    "<pre><code>$ docker run --init myapp\n"
                    "# Ou no Dockerfile:\n"
                    "ENTRYPOINT [\"tini\", \"--\", \"python\", \"main.py\"]</code></pre>"

                    "<h3>10. BuildKit: build moderno</h3>"
                    "<p>BuildKit é o engine de build padrão hoje. Recursos:</p>"
                    "<ul>"
                    "<li>Builds paralelos de stages independentes.</li>"
                    "<li><code>--mount=type=cache</code>: cache persistente "
                    "(node_modules entre builds).</li>"
                    "<li><code>--mount=type=secret</code>: passa secret sem ir para "
                    "imagem.</li>"
                    "<li><code>--mount=type=ssh</code>: forwarding de ssh-agent para "
                    "git clone privado.</li>"
                    "<li>Multi-arch (<code>buildx</code>).</li>"
                    "<li>Inline cache em registries.</li>"
                    "</ul>"
                    "<pre><code># syntax=docker/dockerfile:1\n"
                    "FROM python:3.12-slim\n"
                    "WORKDIR /app\n"
                    "COPY requirements.txt .\n"
                    "RUN --mount=type=cache,target=/root/.cache/pip \\\n"
                    "    pip install -r requirements.txt\n"
                    "COPY . .\n"
                    "CMD [\"python\", \"main.py\"]</code></pre>"

                    "<h3>11. Comandos essenciais</h3>"
                    "<pre><code># Lifecycle\n"
                    "docker build -t myapp:dev .\n"
                    "docker run -d --name app -p 8000:8000 myapp:dev\n"
                    "docker exec -it app sh                # entra no container\n"
                    "docker logs -f app                    # tail logs\n"
                    "docker stop app && docker rm app\n"
                    "\n"
                    "# Inspeção\n"
                    "docker ps -a                          # listar (incluindo parados)\n"
                    "docker inspect app                    # JSON completo\n"
                    "docker stats                          # CPU/RAM em tempo real\n"
                    "docker diff app                       # mudanças no FS desde criação\n"
                    "docker history myapp:dev              # camadas\n"
                    "\n"
                    "# Limpeza (cuidado!)\n"
                    "docker system prune -a --volumes      # remove tudo não usado</code></pre>"

                    "<h3>12. Anti-patterns comuns</h3>"
                    "<ul>"
                    "<li><strong><code>FROM ubuntu:latest</code></strong>: "
                    "irreproduzível. Pin pelo menos o major.</li>"
                    "<li><strong><code>USER root</code></strong> (default): "
                    "container scape vira root no host (com config padrão).</li>"
                    "<li><strong>Múltiplos processos via supervisor</strong>: "
                    "complica logs, healthcheck, restart. Quebre em containers.</li>"
                    "<li><strong>Senha em ENV no Dockerfile</strong>: vai pra "
                    "imagem. Use secrets em runtime.</li>"
                    "<li><strong><code>RUN apt update</code></strong> sem "
                    "<code>install -y</code> na mesma camada: cache desatualizado.</li>"
                    "<li><strong>Imagem 4GB</strong>: provavelmente otimizável com "
                    "multi-stage.</li>"
                    "<li><strong>Sem HEALTHCHECK</strong>: orquestrador nunca sabe que "
                    "app travou.</li>"
                    "<li><strong>Logs em arquivo</strong>: ninguém vê.</li>"
                    "<li><strong>Bind mount de <code>/var/run/docker.sock</code></strong>: "
                    "container vira root do host instantaneamente.</li>"
                    "</ul>"
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
                    "<h3>1. Docker Compose: dev local e prod simples</h3>"
                    "<p>YAML descreve serviços, redes, volumes. <code>docker compose "
                    "up</code> sobe tudo, <code>docker compose down</code> tira. Padrão "
                    "v2 (plugin do CLI). v1 (<code>docker-compose</code> binário) está "
                    "EOL.</p>"
                    "<pre><code># compose.yaml, full example\n"
                    "services:\n"
                    "  app:\n"
                    "    image: ghcr.io/acme/app:abc1234\n"
                    "    build:\n"
                    "      context: .\n"
                    "      dockerfile: Dockerfile\n"
                    "      target: production\n"
                    "    ports:\n"
                    "      - \"8000:8000\"\n"
                    "    environment:\n"
                    "      DATABASE_URL: postgres://app:${DB_PASSWORD}@db:5432/app\n"
                    "      REDIS_URL: redis://cache:6379/0\n"
                    "    secrets:\n"
                    "      - db_password\n"
                    "    healthcheck:\n"
                    "      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:8000/health\"]\n"
                    "      interval: 30s\n"
                    "      timeout: 5s\n"
                    "      retries: 3\n"
                    "      start_period: 20s\n"
                    "    depends_on:\n"
                    "      db: { condition: service_healthy }\n"
                    "      cache: { condition: service_started }\n"
                    "    deploy:\n"
                    "      replicas: 2\n"
                    "      resources:\n"
                    "        limits: { cpus: '0.5', memory: 512M }\n"
                    "      restart_policy:\n"
                    "        condition: on-failure\n"
                    "        max_attempts: 3\n"
                    "    logging:\n"
                    "      driver: json-file\n"
                    "      options: { max-size: 10m, max-file: '3' }\n"
                    "  db:\n"
                    "    image: postgres:16-alpine\n"
                    "    environment:\n"
                    "      POSTGRES_USER: app\n"
                    "      POSTGRES_PASSWORD_FILE: /run/secrets/db_password\n"
                    "      POSTGRES_DB: app\n"
                    "    volumes:\n"
                    "      - pgdata:/var/lib/postgresql/data\n"
                    "    healthcheck:\n"
                    "      test: [\"CMD-SHELL\", \"pg_isready -U app\"]\n"
                    "      interval: 5s\n"
                    "      retries: 10\n"
                    "    secrets: [db_password]\n"
                    "  cache:\n"
                    "    image: redis:7-alpine\n"
                    "    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru\n"
                    "    healthcheck: { test: [\"CMD\", \"redis-cli\", \"ping\"] }\n"
                    "\n"
                    "volumes:\n"
                    "  pgdata: {}\n"
                    "\n"
                    "secrets:\n"
                    "  db_password:\n"
                    "    file: ./secrets/db_password.txt\n"
                    "    # Em prod com Swarm: external: true\n"
                    "\n"
                    "networks:\n"
                    "  default:\n"
                    "    driver: bridge</code></pre>"

                    "<h3>2. Override files: dev vs prod com mesmo base</h3>"
                    "<pre><code># compose.yaml (base, neutro)\n"
                    "# compose.dev.yaml (override para dev)\n"
                    "services:\n"
                    "  app:\n"
                    "    build:\n"
                    "      target: dev\n"
                    "    volumes:\n"
                    "      - .:/app   # bind mount para hot reload\n"
                    "    environment:\n"
                    "      DEBUG: 1\n"
                    "    command: python manage.py runserver 0.0.0.0:8000\n"
                    "\n"
                    "# compose.prod.yaml\n"
                    "services:\n"
                    "  app:\n"
                    "    image: ghcr.io/acme/app:${VERSION}\n"
                    "    deploy:\n"
                    "      replicas: 3\n"
                    "      update_config: { parallelism: 1, order: start-first }</code></pre>"
                    "<pre><code># Uso\n"
                    "$ docker compose -f compose.yaml -f compose.dev.yaml up\n"
                    "$ docker compose -f compose.yaml -f compose.prod.yaml up -d\n"
                    "\n"
                    "# Profiles para serviços opcionais\n"
                    "services:\n"
                    "  mailhog:\n"
                    "    image: mailhog/mailhog\n"
                    "    profiles: [dev]   # só sobe com --profile dev\n"
                    "$ docker compose --profile dev up</code></pre>"

                    "<h3>3. Variáveis e secrets</h3>"
                    "<pre><code># .env (gitignored!)\n"
                    "DB_PASSWORD=supersecret\n"
                    "VERSION=v1.4.2\n"
                    "\n"
                    "# .env.example (commitado, sem valores)\n"
                    "DB_PASSWORD=\n"
                    "VERSION=</code></pre>"
                    "<p>Compose lê <code>.env</code> automaticamente. Em prod, prefira "
                    "secrets injetados pelo runtime (Docker secrets, K8s Secrets, "
                    "Vault).</p>"

                    "<h3>4. Docker Swarm: 'K8s lite'</h3>"
                    "<p>Built-in no Docker, multi-node. Mesmo YAML do Compose com "
                    "seção <code>deploy:</code> (replicas, update strategy, placement "
                    "constraints).</p>"
                    "<pre><code>$ docker swarm init                      # nó 1 vira manager\n"
                    "$ docker swarm join-token worker          # comando para outros nós\n"
                    "$ docker stack deploy -c compose.yaml app\n"
                    "$ docker service ls\n"
                    "$ docker service scale app_web=5\n"
                    "$ docker service update --image ghcr.io/acme/app:v1.5.0 app_web</code></pre>"
                    "<p>Vantagens vs K8s:</p>"
                    "<ul>"
                    "<li>Setup em minutos.</li>"
                    "<li>Mesmo YAML de dev (Compose).</li>"
                    "<li>Routing mesh built-in (qualquer nó atende qualquer porta).</li>"
                    "<li>Secrets criptografados em raft.</li>"
                    "<li>Encrypted overlay network nativo.</li>"
                    "</ul>"
                    "<p>Desvantagens:</p>"
                    "<ul>"
                    "<li>Comunidade e features ficaram para trás vs K8s.</li>"
                    "<li>Sem CRDs/operators/ecossistema rico.</li>"
                    "<li>Auto-scaling limitado (apenas via API/CLI).</li>"
                    "<li>Service discovery menos rico.</li>"
                    "</ul>"

                    "<h3>5. HashiCorp Nomad: orquestrador genérico</h3>"
                    "<p>Roda <em>qualquer coisa</em>, containers Docker/Podman, "
                    "binários nativos, VMs (qemu), JVM, Java WAR. Mais simples que "
                    "K8s. Integra natural com Consul (service discovery) e Vault "
                    "(secrets) para uma stack 'HashiCorp full'.</p>"
                    "<pre><code># job.nomad.hcl\n"
                    "job \"web\" {\n"
                    "  datacenters = [\"dc1\"]\n"
                    "  type = \"service\"\n"
                    "  group \"app\" {\n"
                    "    count = 3\n"
                    "    network {\n"
                    "      port \"http\" { to = 8000 }\n"
                    "    }\n"
                    "    service {\n"
                    "      name = \"web\"\n"
                    "      port = \"http\"\n"
                    "      check { type = \"http\", path = \"/health\", interval = \"10s\", timeout = \"2s\" }\n"
                    "    }\n"
                    "    task \"server\" {\n"
                    "      driver = \"docker\"\n"
                    "      config {\n"
                    "        image = \"ghcr.io/acme/app:v1.4.2\"\n"
                    "        ports = [\"http\"]\n"
                    "      }\n"
                    "      resources { cpu = 500, memory = 256 }\n"
                    "    }\n"
                    "  }\n"
                    "}</code></pre>"
                    "<pre><code>$ nomad job run job.nomad.hcl</code></pre>"
                    "<p>Quando faz sentido: workload misto (não só container), time "
                    "pequeno sem capacidade para K8s, infra HashiCorp já existente.</p>"

                    "<h3>6. Persistência e estado</h3>"
                    "<p>Em Compose/Swarm single-host, volumes nomeados resolvem "
                    "(dados ficam no disco do host). Para HA real:</p>"
                    "<ul>"
                    "<li><strong>DB gerenciado</strong> (RDS, Cloud SQL, Aurora): "
                    "apropriado para 95% dos casos.</li>"
                    "<li><strong>Storage de rede</strong> (NFS, EFS, Longhorn): "
                    "lento, mas portável entre nós.</li>"
                    "<li><strong>Replicação na própria DB</strong>: Postgres "
                    "streaming replication, MySQL InnoDB Cluster.</li>"
                    "</ul>"
                    "<p>Não tente correr stateful complexo (Postgres HA, Kafka) em "
                    "Compose, não é a ferramenta. K8s tem operators (Zalando "
                    "Postgres, Strimzi Kafka).</p>"

                    "<h3>7. Healthchecks e dependências</h3>"
                    "<p><code>depends_on</code> apenas garante ordem de start. Para "
                    "esperar saudável:</p>"
                    "<pre><code>services:\n"
                    "  app:\n"
                    "    depends_on:\n"
                    "      db:\n"
                    "        condition: service_healthy\n"
                    "      cache:\n"
                    "        condition: service_started\n"
                    "        restart: true   # restart app se cache reiniciar</code></pre>"

                    "<h3>8. Networking em Compose</h3>"
                    "<ul>"
                    "<li>Cada Compose project cria uma rede default; serviços "
                    "conversam por nome (DNS interno).</li>"
                    "<li>Múltiplas redes para segmentação:</li>"
                    "</ul>"
                    "<pre><code>services:\n"
                    "  api:\n"
                    "    networks: [frontend, backend]\n"
                    "  db:\n"
                    "    networks: [backend]\n"
                    "networks:\n"
                    "  frontend: {}\n"
                    "  backend:\n"
                    "    internal: true   # sem acesso à internet</code></pre>"
                    "<p><code>internal: true</code> é boa prática para rede de "
                    "DBs/serviços internos.</p>"

                    "<h3>9. Quando migrar para K8s</h3>"
                    "<p>Sinais que sugerem K8s:</p>"
                    "<ul>"
                    "<li>Múltiplos hosts compartilhando workload (não só HA).</li>"
                    "<li>Múltiplos times sharing infra (multi-tenancy).</li>"
                    "<li>Auto-scaling baseado em métricas (HPA/KEDA).</li>"
                    "<li>Roll-out canário gerenciado (Argo Rollouts).</li>"
                    "<li>30-50+ serviços (orquestração manual fica caos).</li>"
                    "<li>Operators avançados (Postgres, Kafka, ML platforms).</li>"
                    "<li>Service mesh (Istio, Linkerd).</li>"
                    "<li>Compliance que exige network policies, RBAC fino, audit nativo.</li>"
                    "</ul>"
                    "<p>Sinais de que K8s é overkill:</p>"
                    "<ul>"
                    "<li>1 app + 1 DB + 1 cache em 1 host.</li>"
                    "<li>Time pequeno (&lt;5 devs) sem dedicação para platform.</li>"
                    "<li>Tráfego baixo, sem necessidade de auto-scale.</li>"
                    "<li>Stateful crítico que vc não quer correr você mesmo.</li>"
                    "</ul>"

                    "<h3>10. Operação prática</h3>"
                    "<pre><code># Logs\n"
                    "docker compose logs -f app                # live tail\n"
                    "docker compose logs --tail=100 app\n"
                    "\n"
                    "# Restart só um serviço\n"
                    "docker compose restart app\n"
                    "\n"
                    "# Recriar (depois de mudar config)\n"
                    "docker compose up -d --force-recreate app\n"
                    "\n"
                    "# Scale\n"
                    "docker compose up -d --scale app=3\n"
                    "\n"
                    "# Backup volume\n"
                    "docker run --rm -v pgdata:/data -v $(pwd):/backup alpine \\\n"
                    "  tar czf /backup/pgdata-$(date +%F).tgz -C /data .</code></pre>"

                    "<h3>11. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Compose como prod multi-host</strong>: não escala. "
                    "Use Swarm/Nomad/K8s.</li>"
                    "<li><strong>Stateful complexo em Compose</strong>: HA real "
                    "requer ferramenta dedicada.</li>"
                    "<li><strong>Bind mount em prod</strong>: portabilidade ruim, "
                    "permissões complicam.</li>"
                    "<li><strong>Sem healthcheck</strong>: dependências quebram em "
                    "race condition.</li>"
                    "<li><strong>Variáveis sensíveis em compose.yaml</strong>: "
                    "commitado. Use .env (gitignore) ou secrets.</li>"
                    "<li><strong>Misturar prod e dev no mesmo YAML</strong>: use "
                    "overrides.</li>"
                    "</ul>"
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
                    "<h3>1. Conceito: política como código</h3>"
                    "<p>Regras de negócio/segurança/compliance escritas em linguagem "
                    "versionada (Rego, YAML, etc.), revisáveis em PR, testáveis com "
                    "unit tests, e <em>aplicadas automaticamente</em> em pontos do "
                    "ciclo:</p>"
                    "<ul>"
                    "<li><strong>Dev</strong>: editor com linter/IDE plugin.</li>"
                    "<li><strong>Pre-commit</strong>: hook local roda Conftest.</li>"
                    "<li><strong>CI</strong>: bloqueia merge em violação.</li>"
                    "<li><strong>Admission controller (K8s)</strong>: rejeita criação "
                    "de recursos não-conformes.</li>"
                    "<li><strong>Cloud account</strong>: SCP (AWS), Azure Policy, GCP "
                    "Org Policy aplicam transversalmente.</li>"
                    "<li><strong>Runtime</strong>: políticas de autorização em APIs.</li>"
                    "</ul>"
                    "<p>Defesa em camadas: mesmo se uma camada falhar, próxima pega.</p>"

                    "<h3>2. OPA (Open Policy Agent) e Rego</h3>"
                    "<p>OPA é engine multipropósito. CNCF graduado. Linguagem "
                    "<strong>Rego</strong> declarativa, baseada em Datalog. Curva "
                    "inicial existe, mas paga rápido.</p>"
                    "<p>Anatomia de uma policy:</p>"
                    "<pre><code>package terraform.s3   # namespace\n"
                    "\n"
                    "import future.keywords\n"
                    "\n"
                    "# Inputs vêm de fora (terraform plan json)\n"
                    "deny[msg] {\n"
                    "  resource := input.resource.aws_s3_bucket[name]\n"
                    "  resource.acl == \"public-read\"\n"
                    "  msg := sprintf(\"Bucket %v não pode ser public-read\", [name])\n"
                    "}\n"
                    "\n"
                    "deny[msg] {\n"
                    "  resource := input.resource.aws_security_group[name]\n"
                    "  rule := resource.ingress[_]\n"
                    "  rule.cidr_blocks[_] == \"0.0.0.0/0\"\n"
                    "  rule.from_port == 22\n"
                    "  msg := sprintf(\"SG %v não pode ter SSH aberto ao mundo\", [name])\n"
                    "}\n"
                    "\n"
                    "warn[msg] {\n"
                    "  resource := input.resource.aws_db_instance[name]\n"
                    "  not resource.storage_encrypted\n"
                    "  msg := sprintf(\"RDS %v deveria ter encryption\", [name])\n"
                    "}</code></pre>"
                    "<p>Rego é <em>set-based</em>: queries retornam conjuntos de "
                    "valores. <code>deny[msg]</code> coleta todas as mensagens. "
                    "<code>_</code> é wildcard.</p>"

                    "<h3>3. Conftest: validação fora do K8s</h3>"
                    "<p>Roda OPA contra arquivos de configuração (TF plan, K8s "
                    "manifests, Dockerfile, JSON, YAML, INI, etc.).</p>"
                    "<pre><code># CI: validar Terraform plan\n"
                    "$ terraform show -json tfplan &gt; plan.json\n"
                    "$ conftest test plan.json --policy ./policies\n"
                    "FAIL - plan.json - Bucket app-data não pode ser public-read\n"
                    "FAIL - plan.json - SG web não pode ter SSH aberto ao mundo\n"
                    "WARN - plan.json - RDS db-prod deveria ter encryption\n"
                    "\n"
                    "$ echo $?\n"
                    "1   # exit code falha o build</code></pre>"

                    "<h3>4. Kyverno: K8s-native, sem precisar Rego</h3>"
                    "<p>Para K8s, Kyverno é mais simples, políticas em YAML. Curva "
                    "de aprendizado quase nula:</p>"
                    "<pre><code>apiVersion: kyverno.io/v1\n"
                    "kind: ClusterPolicy\n"
                    "metadata: { name: require-non-root }\n"
                    "spec:\n"
                    "  validationFailureAction: Enforce\n"
                    "  background: true   # também aplica em recursos existentes (audit)\n"
                    "  rules:\n"
                    "    - name: check-runAsNonRoot\n"
                    "      match:\n"
                    "        any:\n"
                    "          - resources: { kinds: [Pod], namespaces: ['prod-*'] }\n"
                    "      validate:\n"
                    "        message: \"Containers em prod-* devem rodar como non-root.\"\n"
                    "        pattern:\n"
                    "          spec:\n"
                    "            =(securityContext):\n"
                    "              =(runAsNonRoot): true\n"
                    "            containers:\n"
                    "              - =(securityContext):\n"
                    "                  =(runAsNonRoot): true\n"
                    "    - name: drop-all-capabilities\n"
                    "      match: { any: [{ resources: { kinds: [Pod] } }] }\n"
                    "      validate:\n"
                    "        pattern:\n"
                    "          spec:\n"
                    "            containers:\n"
                    "              - securityContext:\n"
                    "                  capabilities:\n"
                    "                    drop: [\"ALL\"]</code></pre>"
                    "<p>Kyverno também suporta:</p>"
                    "<ul>"
                    "<li><strong>Mutate</strong>: injetar securityContext padrão "
                    "automaticamente.</li>"
                    "<li><strong>Generate</strong>: criar Secret/ConfigMap em todo "
                    "namespace.</li>"
                    "<li><strong>Verify images</strong>: assinatura Cosign.</li>"
                    "<li><strong>Cleanup</strong>: apagar recursos órfãos.</li>"
                    "</ul>"

                    "<h3>5. OPA Gatekeeper: OPA empacotado para K8s</h3>"
                    "<p>Gatekeeper traz OPA/Rego para admission controller K8s via "
                    "ConstraintTemplates e Constraints:</p>"
                    "<pre><code># Template (Rego)\n"
                    "apiVersion: templates.gatekeeper.sh/v1\n"
                    "kind: ConstraintTemplate\n"
                    "metadata: { name: k8srequiredlabels }\n"
                    "spec:\n"
                    "  crd:\n"
                    "    spec:\n"
                    "      names: { kind: K8sRequiredLabels }\n"
                    "  targets:\n"
                    "    - target: admission.k8s.gatekeeper.sh\n"
                    "      rego: |\n"
                    "        package k8srequiredlabels\n"
                    "        violation[{\"msg\": msg}] {\n"
                    "          missing := input.parameters.labels - \\\n"
                    "                     {label | input.review.object.metadata.labels[label]}\n"
                    "          count(missing) &gt; 0\n"
                    "          msg := sprintf(\"Labels obrigatórios faltando: %v\", [missing])\n"
                    "        }\n"
                    "\n"
                    "# Constraint (uso)\n"
                    "apiVersion: constraints.gatekeeper.sh/v1beta1\n"
                    "kind: K8sRequiredLabels\n"
                    "metadata: { name: ns-must-have-owner }\n"
                    "spec:\n"
                    "  match: { kinds: [{ kinds: [Namespace] }] }\n"
                    "  parameters: { labels: [\"owner\", \"environment\"] }</code></pre>"

                    "<h3>6. Sentinel (HashiCorp)</h3>"
                    "<p>DSL própria, integrada a Terraform Cloud, Vault, Consul, "
                    "Nomad. Útil em times all-in HashiCorp:</p>"
                    "<pre><code># sentinel.hcl\n"
                    "policy \"require-encryption\" {\n"
                    "  source = \"./require-encryption.sentinel\"\n"
                    "  enforcement_level = \"hard-mandatory\"\n"
                    "}\n"
                    "\n"
                    "# require-encryption.sentinel\n"
                    "import \"tfplan/v2\" as tfplan\n"
                    "\n"
                    "main = rule {\n"
                    "  all tfplan.resource_changes as _, rc {\n"
                    "    rc.type is \"aws_s3_bucket\" implies\n"
                    "      rc.change.after.server_side_encryption_configuration is not null\n"
                    "  }\n"
                    "}</code></pre>"

                    "<h3>7. Cloud Custodian: políticas cloud em YAML</h3>"
                    "<p>Para AWS/Azure/GCP, Cloud Custodian aplica/audita políticas:</p>"
                    "<pre><code># custodian.yaml\n"
                    "policies:\n"
                    "  - name: stop-untagged-ec2\n"
                    "    resource: aws.ec2\n"
                    "    filters:\n"
                    "      - 'tag:Owner': absent\n"
                    "      - State.Name: running\n"
                    "    actions:\n"
                    "      - type: notify\n"
                    "        to: [security@empresa.com]\n"
                    "      - stop\n"
                    "\n"
                    "  - name: encrypt-s3-buckets\n"
                    "    resource: aws.s3\n"
                    "    filters:\n"
                    "      - type: bucket-encryption\n"
                    "        state: false\n"
                    "    actions:\n"
                    "      - type: set-bucket-encryption</code></pre>"

                    "<h3>8. SCPs e Org Policies (transversal)</h3>"
                    "<p>Para regras 'da empresa toda', use:</p>"
                    "<ul>"
                    "<li><strong>AWS SCP</strong> (Service Control Policy): aplicado "
                    "em OUs, restringe IAM. 'Ninguém pode criar bucket sem TLS.'</li>"
                    "<li><strong>Azure Policy</strong>: deny/audit/append em recursos. "
                    "Policy Initiative (set de policies).</li>"
                    "<li><strong>GCP Org Policy</strong>: constraints em organização "
                    "ou pasta.</li>"
                    "</ul>"
                    "<p>Versionados como IaC (Terraform):</p>"
                    "<pre><code>resource \"aws_organizations_policy\" \"deny-public-buckets\" {\n"
                    "  name = \"deny-public-buckets\"\n"
                    "  type = \"SERVICE_CONTROL_POLICY\"\n"
                    "  content = jsonencode({\n"
                    "    Version = \"2012-10-17\"\n"
                    "    Statement = [{\n"
                    "      Effect = \"Deny\"\n"
                    "      Action = [\"s3:PutBucketAcl\"]\n"
                    "      Resource = \"*\"\n"
                    "      Condition = {\n"
                    "        \"StringEquals\" = { \"s3:x-amz-acl\" = [\"public-read\", \"public-read-write\"] }\n"
                    "      }\n"
                    "    }]\n"
                    "  })\n"
                    "}</code></pre>"

                    "<h3>9. Adoção: warn primeiro, enforce depois</h3>"
                    "<p>Erro comum: ligar enforce em produção no dia 1. Resultado: "
                    "metade dos times bloqueados, revolta, política desligada para "
                    "sempre.</p>"
                    "<p>Padrão sugerido:</p>"
                    "<ol>"
                    "<li><strong>Audit only</strong>: política reporta violações sem "
                    "bloquear. Mapeie escopo do problema.</li>"
                    "<li><strong>Warn em PR</strong>: bloqueia PRs novos, não "
                    "existentes. Devs aprendem.</li>"
                    "<li><strong>Enforce em ambientes baixos</strong> (dev, staging): "
                    "bloqueia.</li>"
                    "<li><strong>Enforce em prod</strong>: depois de meses limpando.</li>"
                    "<li><strong>Documente exceções</strong>: label de recurso, "
                    "namespace exempt list. Auditar trimestralmente.</li>"
                    "</ol>"

                    "<h3>10. Testes de políticas</h3>"
                    "<p>Política tem bug como qualquer código. Teste:</p>"
                    "<pre><code># OPA testing\n"
                    "test_deny_public_bucket {\n"
                    "  result := deny with input as {\n"
                    "    \"resource\": {\n"
                    "      \"aws_s3_bucket\": {\n"
                    "        \"data\": {\"acl\": \"public-read\"}\n"
                    "      }\n"
                    "    }\n"
                    "  }\n"
                    "  count(result) == 1\n"
                    "}\n"
                    "\n"
                    "$ opa test policies/ -v\n"
                    "PASS: 5/5</code></pre>"

                    "<h3>11. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Enforce no dia 1 em prod</strong>: revolta garantida.</li>"
                    "<li><strong>Sem testes de policy</strong>: bug bloqueia tudo um dia.</li>"
                    "<li><strong>Mensagem de erro genérica</strong>: dev não sabe "
                    "o que fazer. Sempre inclua link/explicação.</li>"
                    "<li><strong>Política sem dono</strong>: vira lixo.</li>"
                    "<li><strong>Sem mecanismo de exceção</strong>: legítimas "
                    "alternativas perdem-se.</li>"
                    "<li><strong>Mil políticas</strong>: foco no top 10 que importa.</li>"
                    "<li><strong>Apenas em CI</strong>: alguém aplica direto, "
                    "drift cresce. Defesa em camadas.</li>"
                    "</ul>"
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
                    "<h3>1. Autenticação: quem é você</h3>"
                    "<h4>1.1 OAuth 2.0 e OIDC</h4>"
                    "<p>OAuth 2.0 é framework de autorização: token de bearer com "
                    "scopes. OIDC adiciona camada de identidade (id_token JWT "
                    "assinado).</p>"
                    "<p>Fluxos comuns:</p>"
                    "<ul>"
                    "<li><strong>Authorization Code + PKCE</strong>: padrão para "
                    "SPA/mobile. PKCE protege contra interceptação do code.</li>"
                    "<li><strong>Client Credentials</strong>: machine-to-machine "
                    "(microsserviço A → microsserviço B).</li>"
                    "<li><strong>Refresh Token</strong>: renovar access_token sem "
                    "re-login.</li>"
                    "<li><strong>Device Code</strong>: TVs, CLI.</li>"
                    "</ul>"
                    "<p><strong>Não use</strong>: implicit flow (depreciado), "
                    "ROPC (resource owner password credentials, só legados).</p>"
                    "<h4>1.2 JWT bem usado</h4>"
                    "<pre><code># Header\n"
                    "{\"alg\": \"RS256\", \"typ\": \"JWT\", \"kid\": \"key-2024\"}\n"
                    "\n"
                    "# Payload\n"
                    "{\n"
                    "  \"iss\": \"https://auth.empresa.com\",\n"
                    "  \"aud\": \"https://api.empresa.com\",\n"
                    "  \"sub\": \"user-123\",\n"
                    "  \"iat\": 1714053000,\n"
                    "  \"exp\": 1714053900,         // 15min\n"
                    "  \"scope\": \"read:orders write:orders\",\n"
                    "  \"jti\": \"random-uuid\"     // permite revogação\n"
                    "}\n"
                    "\n"
                    "# Signature\n"
                    "RSASHA256(base64(header) + '.' + base64(payload), private_key)</code></pre>"
                    "<p>Boas práticas JWT:</p>"
                    "<ul>"
                    "<li><strong>Algoritmo</strong>: RS256, ES256, EdDSA, nunca "
                    "<code>none</code>; cuidado com HS256 + chave compartilhada (qualquer "
                    "um que assina pode forjar).</li>"
                    "<li><strong>Validar</strong>: <code>iss</code>, <code>aud</code>, "
                    "<code>exp</code>, <code>nbf</code>, assinatura.</li>"
                    "<li><strong>JWKS</strong>: rotacione chave de assinatura "
                    "periodicamente; <code>kid</code> permite múltiplas válidas.</li>"
                    "<li><strong>TTL curto</strong>: 5-15min para access_token; "
                    "refresh para sessão longa.</li>"
                    "<li><strong>Não armazene em localStorage</strong> em "
                    "browser (XSS rouba). Use cookie HttpOnly + SameSite=Strict.</li>"
                    "<li><strong>Revogação</strong>: blacklist via <code>jti</code> "
                    "em Redis (TTL = exp).</li>"
                    "<li><strong>Não coloque senha/PII no payload</strong>: JWT é "
                    "base64, não cripto.</li>"
                    "</ul>"

                    "<h3>2. Autorização: o que pode fazer</h3>"
                    "<h4>2.1 BOLA (Broken Object Level Authorization), top 1</h4>"
                    "<p>API que checa só 'usuário logado' mas não 'usuário é dono "
                    "do recurso':</p>"
                    "<pre><code># RUIM\n"
                    "@app.get('/orders/{order_id}')\n"
                    "def get_order(order_id: int, user = Depends(current_user)):\n"
                    "    return Order.objects.get(id=order_id)   # qualquer logado vê qualquer pedido\n"
                    "\n"
                    "# BOM\n"
                    "@app.get('/orders/{order_id}')\n"
                    "def get_order(order_id: int, user = Depends(current_user)):\n"
                    "    order = Order.objects.get(id=order_id)\n"
                    "    if order.user_id != user.id and not user.is_admin:\n"
                    "        raise HTTPException(403)\n"
                    "    return order</code></pre>"
                    "<p>Ataques: trocar <code>order_id</code> sequencialmente "
                    "(<code>?id=1</code>, <code>?id=2</code>...). Defesa: "
                    "authorization no nível do recurso, sempre.</p>"
                    "<h4>2.2 Scopes</h4>"
                    "<p>Token com scope mínimo necessário. <code>read:orders</code> "
                    "≠ <code>write:orders</code>. Aplicação valida.</p>"
                    "<h4>2.3 ABAC (Attribute-Based Access Control)</h4>"
                    "<p>Decisão baseada em atributos do user, recurso, contexto:</p>"
                    "<pre><code># OPA policy para autorização\n"
                    "package authz\n"
                    "default allow = false\n"
                    "\n"
                    "allow {\n"
                    "  input.action == \"read\"\n"
                    "  input.resource.type == \"order\"\n"
                    "  input.resource.user_id == input.subject.id\n"
                    "}\n"
                    "\n"
                    "allow {\n"
                    "  input.subject.role == \"admin\"\n"
                    "}</code></pre>"

                    "<h3>3. Validação de input e schema</h3>"
                    "<p>Defina API com OpenAPI 3.x ou GraphQL schema. Frameworks "
                    "modernos validam automaticamente:</p>"
                    "<pre><code># FastAPI: schema vira validação\n"
                    "from pydantic import BaseModel, Field, EmailStr\n"
                    "\n"
                    "class CreateOrder(BaseModel):\n"
                    "    items: list[int] = Field(..., min_length=1, max_length=100)\n"
                    "    shipping_address: str = Field(..., max_length=500)\n"
                    "    customer_email: EmailStr\n"
                    "    notes: str | None = Field(None, max_length=1000)\n"
                    "\n"
                    "@app.post('/orders')\n"
                    "def create_order(order: CreateOrder, user = Depends(current_user)):\n"
                    "    # Pydantic já validou tipos, ranges, formatos.\n"
                    "    ...</code></pre>"
                    "<p>Em GraphQL:</p>"
                    "<ul>"
                    "<li>Limite profundidade de query (depth limit).</li>"
                    "<li>Limite complexidade (cost analysis).</li>"
                    "<li>Disable introspection em prod (a menos que público).</li>"
                    "<li>Persisted queries, só aceita queries pré-aprovadas.</li>"
                    "</ul>"

                    "<h3>4. Rate limiting e quotas</h3>"
                    "<p>Camadas:</p>"
                    "<ul>"
                    "<li><strong>Edge</strong>: WAF (Cloudflare, AWS WAF), CDN. "
                    "Bloqueia bots/DDoS antes de chegar ao backend.</li>"
                    "<li><strong>Gateway</strong>: Kong, AWS API Gateway, NGINX. "
                    "Rate limit por API key/IP/user.</li>"
                    "<li><strong>App</strong>: lógica de negócio, ex.: 5 tentativas "
                    "de login em 15min.</li>"
                    "</ul>"
                    "<p>Algoritmos:</p>"
                    "<ul>"
                    "<li><strong>Fixed window</strong>: 1000 req/min por IP. Simples, "
                    "permite burst no virar do minuto.</li>"
                    "<li><strong>Sliding window</strong>: mais suave, mais cálculo.</li>"
                    "<li><strong>Token bucket</strong>: permite burst até a capacidade.</li>"
                    "<li><strong>Leaky bucket</strong>: throughput constante.</li>"
                    "</ul>"
                    "<p>Implementação Redis sliding window:</p>"
                    "<pre><code>def rate_limit(key: str, max_req: int, window_sec: int) -&gt; bool:\n"
                    "    now = time.time()\n"
                    "    pipe = redis.pipeline()\n"
                    "    pipe.zremrangebyscore(key, 0, now - window_sec)\n"
                    "    pipe.zcard(key)\n"
                    "    pipe.zadd(key, {str(uuid.uuid4()): now})\n"
                    "    pipe.expire(key, window_sec)\n"
                    "    _, count, _, _ = pipe.execute()\n"
                    "    return count &lt; max_req</code></pre>"
                    "<p>Resposta 429 deve incluir <code>Retry-After</code>:</p>"
                    "<pre><code>HTTP/1.1 429 Too Many Requests\n"
                    "Retry-After: 60\n"
                    "X-RateLimit-Limit: 1000\n"
                    "X-RateLimit-Remaining: 0\n"
                    "X-RateLimit-Reset: 1714053900</code></pre>"

                    "<h3>5. Mass Assignment</h3>"
                    "<p>App que aceita request.json direto no ORM:</p>"
                    "<pre><code># RUIM\n"
                    "@app.put('/users/{id}')\n"
                    "def update_user(id, body: dict):\n"
                    "    user = User.objects.get(id=id)\n"
                    "    for k, v in body.items():\n"
                    "        setattr(user, k, v)   # cliente passa is_admin: true → ele vira admin!\n"
                    "    user.save()\n"
                    "\n"
                    "# BOM: schema com allow-list\n"
                    "class UserUpdate(BaseModel):\n"
                    "    name: str | None\n"
                    "    email: EmailStr | None\n"
                    "    # is_admin NÃO está aqui, não pode ser setado por API pública\n"
                    "\n"
                    "@app.put('/users/{id}')\n"
                    "def update_user(id, body: UserUpdate, user = Depends(current_user)):\n"
                    "    if user.id != id: raise HTTPException(403)\n"
                    "    target = User.objects.get(id=id)\n"
                    "    for k, v in body.dict(exclude_unset=True).items():\n"
                    "        setattr(target, k, v)\n"
                    "    target.save()</code></pre>"

                    "<h3>6. Excessive Data Exposure</h3>"
                    "<p>Retornar User completo quando só precisa do nome:</p>"
                    "<pre><code># RUIM\n"
                    "@app.get('/users/{id}')\n"
                    "def get_user(id):\n"
                    "    return User.objects.get(id=id).to_dict()\n"
                    "    # Retorna password_hash, internal_notes, ssn...\n"
                    "\n"
                    "# BOM: response model explícito\n"
                    "class UserPublic(BaseModel):\n"
                    "    id: int\n"
                    "    name: str\n"
                    "    avatar_url: str | None\n"
                    "\n"
                    "@app.get('/users/{id}', response_model=UserPublic)\n"
                    "def get_user(id):\n"
                    "    return User.objects.get(id=id)</code></pre>"

                    "<h3>7. Transporte: TLS, mTLS</h3>"
                    "<ul>"
                    "<li>TLS 1.2+ obrigatório, 1.3 preferido.</li>"
                    "<li>HSTS com max-age longo + preload.</li>"
                    "<li>Certificate pinning em mobile (com cuidado).</li>"
                    "<li><strong>mTLS</strong> entre microsserviços internos: "
                    "ambos provam identidade. Service mesh (Istio, Linkerd) "
                    "automatiza.</li>"
                    "<li>Tokens <em>nunca</em> em URL, vão para logs/proxies. "
                    "Apenas em <code>Authorization: Bearer</code>.</li>"
                    "</ul>"

                    "<h3>8. Webhooks: assinatura HMAC</h3>"
                    "<p>Receber webhook sem verificar = atacante pode forjar. "
                    "Padrão: provider assina payload com HMAC:</p>"
                    "<pre><code>POST /webhooks/stripe HTTP/1.1\n"
                    "Stripe-Signature: t=1614243000,v1=abc123def456...\n"
                    "Content-Type: application/json\n"
                    "\n"
                    "{\"id\": \"evt_...\", \"type\": \"charge.succeeded\", ...}\n"
                    "\n"
                    "# Receptor valida\n"
                    "import hmac, hashlib, time\n"
                    "\n"
                    "def verify_webhook(body: bytes, signature_header: str, secret: str):\n"
                    "    timestamp, sig = parse_header(signature_header)\n"
                    "    if abs(time.time() - timestamp) &gt; 300:   # &gt;5min, replay\n"
                    "        raise Invalid('stale')\n"
                    "    expected = hmac.new(\n"
                    "        secret.encode(),\n"
                    "        f\"{timestamp}.{body.decode()}\".encode(),\n"
                    "        hashlib.sha256\n"
                    "    ).hexdigest()\n"
                    "    if not hmac.compare_digest(expected, sig):\n"
                    "        raise Invalid('signature')</code></pre>"
                    "<p>Use <code>compare_digest</code> (timing-safe) sempre.</p>"

                    "<h3>9. Errors sem leak</h3>"
                    "<pre><code># RUIM\n"
                    "except Exception as e:\n"
                    "    return {\"error\": str(e), \"trace\": traceback.format_exc()}\n"
                    "\n"
                    "# BOM\n"
                    "except Exception as e:\n"
                    "    correlation_id = uuid.uuid4()\n"
                    "    logger.exception(\"erro\", extra={\"correlation_id\": correlation_id})\n"
                    "    return JSONResponse(\n"
                    "        status_code=500,\n"
                    "        content={\"error\": \"internal\", \"correlation_id\": str(correlation_id)}\n"
                    "    )</code></pre>"
                    "<p>Cliente vê id genérico; suporte busca log pelo correlation_id.</p>"

                    "<h3>10. Observability</h3>"
                    "<ul>"
                    "<li><strong>Logs estruturados</strong> (JSON) com "
                    "<code>request_id</code>, <code>user_id</code> hash, "
                    "<code>route</code>, <code>status</code>, <code>latency</code>, "
                    "sem PII em claro.</li>"
                    "<li><strong>Metrics</strong> por rota: req/s, error rate, "
                    "latência p50/p99.</li>"
                    "<li><strong>Traces</strong> (OpenTelemetry): saltar entre "
                    "serviços por trace_id.</li>"
                    "<li><strong>Alertas</strong>: spike de 401 (brute force?), "
                    "spike de 429 (DoS?), latência subiu.</li>"
                    "</ul>"

                    "<h3>11. API Gateway: o que centraliza</h3>"
                    "<ul>"
                    "<li>Auth (validação JWT) na borda; serviços confiam.</li>"
                    "<li>Rate limit unificado.</li>"
                    "<li>Logging/metrics central.</li>"
                    "<li>Versionamento de API (v1, v2).</li>"
                    "<li>Routing.</li>"
                    "<li>Caching de respostas.</li>"
                    "</ul>"
                    "<p>Opções: Kong, AWS API Gateway, Apigee, NGINX, Traefik, "
                    "Envoy.</p>"

                    "<h3>12. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>JWT em localStorage</strong> em browser (XSS).</li>"
                    "<li><strong>Token sem expiração</strong>.</li>"
                    "<li><strong>HS256 com secret compartilhado entre serviços</strong>.</li>"
                    "<li><strong>API sem rate limit</strong>.</li>"
                    "<li><strong>BOLA</strong> (não checar dono do recurso).</li>"
                    "<li><strong>Stack trace em error</strong>.</li>"
                    "<li><strong>Token em URL</strong>.</li>"
                    "<li><strong>CORS *</strong> com credentials.</li>"
                    "<li><strong>Webhook sem verificação</strong>.</li>"
                    "<li><strong>Validação só client-side</strong>.</li>"
                    "<li><strong>Endpoint admin sem MFA/extra-auth</strong>.</li>"
                    "</ul>"
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
