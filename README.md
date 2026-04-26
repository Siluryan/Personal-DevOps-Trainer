# Personal DevOps Trainer (PDT)

Plataforma online com gamificação, ranking público (opt-in) e doação para
o criador, focada em formar profissionais **DevSecOps** do básico ao
avançado.

> Software liberado sob **licença restritiva**. Leia [LICENSE](./LICENSE)
> antes de usar, hospedar ou distribuir. Operação e exploração comercial
> exigem autorização do mantenedor.

## Visão geral

- **Teste de admissão** com 10 questões de Linux e Redes (mínimo 5/10).
  Quem não passa, não acessa o conteúdo principal.
- **Cadastro profissional** com LinkedIn e GitHub (deixamos explícito que
  os dados são usados para conectar alunos dedicados a vagas).
- **Trilha DevSecOps** com 6 fases e 60 tópicos, cada um com:
  - aula completa (introdução, corpo, parte prática);
  - 5+ materiais externos curados;
  - prova final de 10 questões.
- **Gráfico de desempenho** estilo radar com os 60 tópicos como pontos
  (zoom suave do texto ao passar o mouse para facilitar a leitura).
- **Leaderboard top 50** público (apenas para quem optou em aparecer).
  Ao clicar em um usuário do ranking, exibe seus contatos profissionais
  (LinkedIn, GitHub, bio, país, nível de carreira), também opt-in.
- **Mapa em tempo real** com todos os usuários online (Leaflet +
  WebSocket via Django Channels). Cada ponto é verde por padrão; o
  usuário pode pedir ajuda e virar vermelho. Outros usuários abrem uma
  **sala de ajuda nativa com voz (WebRTC) + chat de texto** e ganham
  pontos quando resolvem o problema. O estado "pedindo ajuda" persiste
  entre recargas, só sai do vermelho ao resolver/cancelar.
- **Simulador de entrevistas** com 3 níveis (Júnior, Pleno, Sênior),
  100 questões por nível, e progressão de carreira destravada por 80%
  de acerto. Detalhes em [Simulador de entrevistas](#simulador-de-entrevistas).
- **"Pague um café"** configurável via variável de ambiente.

A pasta `imagens/` traz a referência visual do gráfico de desempenho.

## Stack

- Python 3.12 + Django 5.1 (ASGI com Daphne)
- PostgreSQL 16
- Redis 7 (cache e Channels layer)
- Django Channels (WebSocket do mapa)
- HTMX + Alpine.js + Tailwind (CDN) no front
- Chart.js (radar) + Leaflet/OpenStreetMap (mapa)
- django-allauth (auth/cadastro)

Tudo orquestrado via `docker compose`.

## Estrutura do repositório

```
.
├── ideia-do-projeto.md        # requisitos originais
├── tópicos.md                 # estrutura das 6 fases / 60 tópicos
├── imagens/                   # referências visuais
├── LICENSE                    # licença restritiva (uso com consentimento)
├── CONTRIBUTING.md            # regras para contribuir
└── pdt/                       # aplicação Django
    ├── docker-compose.yml
    ├── Dockerfile
    ├── Dockerfile.test
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── .env.example
    ├── manage.py
    ├── config/                # settings, urls, asgi/wsgi
    ├── apps/
    │   ├── core/              # landing, dashboard, helpers
    │   ├── accounts/          # User customizado, perfil, gating, carreira
    │   ├── assessments/       # teste de admissão
    │   ├── courses/           # fases, tópicos, aulas, quizzes, seeds
    │   ├── gamification/      # pontuação, radar, leaderboard
    │   ├── presence/          # mapa em tempo real, pedidos de ajuda
    │   ├── interviews/        # simulador de entrevistas (Júnior/Pleno/Sênior)
    │   └── donations/         # link "pague um café"
    ├── templates/             # base + páginas Tailwind/HTMX
    ├── static/                # CSS/JS/imagens
    └── scripts/entrypoint.sh
```

## Subindo o projeto local

Pré-requisitos: Docker e Docker Compose v2.

```bash
cd pdt
cp .env.example .env       # ajuste o que precisar (segredo, donation, etc.)
docker compose up --build
```

Na primeira subida, o `entrypoint.sh`:

1. Espera o Postgres responder.
2. Aplica as migrações versionadas no repositório.
3. Coleta arquivos estáticos.
4. Roda os seeds idempotentes:
   - `python manage.py seed_topics` (6 fases, 60 tópicos, materiais e
     questões);
   - `python manage.py seed_admission_test` (banco de questões do teste
     de admissão);
   - `python manage.py seed_interviews` (300 questões do simulador de
     entrevistas, 100 por nível; embaralha alternativas de forma
     determinística, com mais mistura no pleno e ainda mais no sênior).
5. Inicia o Daphne na porta `8000`.

Acesse:

- App: <http://localhost:8000>
- Admin: <http://localhost:8000/admin>

Para criar um superusuário:

```bash
docker compose exec web python manage.py createsuperuser
```

## Variáveis de ambiente principais

| Variável | Descrição | Padrão |
|---|---|---|
| `DJANGO_SECRET_KEY` | chave secreta do Django | obrigatória |
| `DJANGO_DEBUG` | modo debug | `True` em dev |
| `DJANGO_ALLOWED_HOSTS` | hosts permitidos (CSV) | `localhost,...` |
| `POSTGRES_*` | credenciais e host do banco | ver `.env.example` |
| `REDIS_URL` | URL do Redis | `redis://redis:6379/0` |
| `DONATION_URL` | link "pague um café" (Buy Me a Coffee, Pix, etc.) | exemplo |
| `DONATION_LABEL` | rótulo exibido no rodapé/footer | exemplo |
| `ADMISSION_PASS_SCORE` | nota mínima do teste de admissão (0-10) | `5` |

## Fluxo do usuário

1. Visita a landing, cria conta (e-mail/senha via allauth).
2. É direcionado para o **teste de admissão** (10 questões aleatórias).
3. Se acerta ≥ `ADMISSION_PASS_SCORE`, conclui o **perfil** com LinkedIn
   e GitHub e ganha acesso pleno. Caso contrário, pode tentar novamente
   após ler novamente os materiais sugeridos.
4. Recebe automaticamente o título de **Estagiário** e pode acessar o
   **simulador de entrevistas** (`/entrevistas`) para subir de carreira.
5. Estuda a **trilha** (`/cursos`) e responde quizzes, cada acerto vira
   ponto no tópico correspondente.
6. Liga/desliga sua presença no **mapa** (`/mapa`). Pode pedir ajuda em
   um tópico específico, virando ponto vermelho até que alguém o ajude.
7. Quem ajudou recebe pontos automaticamente quando o autor do pedido
   marca a ajuda como resolvida.
8. Aparece no **ranking top 50** se tiver optado em "show in leaderboard"
   no perfil; outros usuários veem seu título de carreira ao lado do nome
   e podem acessar seus contatos profissionais (se opt-in).

## Simulador de entrevistas

Cada usuário começa com o título **Estagiário** e pode subir de carreira
ao passar nos testes do simulador (`/entrevistas`).

| Nível | Foco | Pré-requisito |
|-------|------|---------------|
| Júnior | Linux, redes, Git, Docker, CI/CD, cloud, programação, banco, monitoramento, segurança, comportamental | Liberado por padrão |
| Pleno | Kubernetes, IaC (Terraform), observability, DevSecOps, performance, troubleshooting, networking avançado, banco em produção | ≥ 80% no teste de Júnior |
| Sênior | **Arquitetura** (microservices, SOA), escalabilidade, multi-region/HA/DR, Zero Trust, SRE, custo, migração, liderança técnica, trade-offs | ≥ 80% no teste de Pleno |

**Características:**

- 100 questões por teste (300 no total), embaralhadas a cada tentativa.
- **Salvar e continuar depois**: cada resposta é persistida no servidor;
  você pode sair a qualquer momento e retomar exatamente de onde parou.
- Apenas uma tentativa em andamento por nível (descartável a qualquer
  momento). Tentativas finalizadas viram histórico.
- Score de **80% ou mais** promove o usuário ao próximo nível e o título
  é refletido em todo o site (header, dashboard, perfil, ranking).
- Resultado mostra **gabarito completo** com explicação em cada questão,
  para uso como material de estudo.
- **Distratores plausíveis**: as alternativas erradas são desenhadas para
  parecerem verdadeiras a quem só conhece o tópico de forma rasa
  (sintaxe vizinha, half-truths, inversões sutis, padrões correlatos).
  Um suite anti-regressão (`apps/interviews/test_question_quality.py`)
  garante que distratores nunca caiam de novo em frases preguiçosas como
  *"Não há motivo."* ou alternativas drasticamente menores que a correta.

### Viés de posição no arquivo fonte e embaralhamento das alternativas

Nos arquivos `seed_data` (júnior, pleno, sênior), o campo `correct_index`
indica qual alternativa é a correta **antes** de qualquer tratamento. Esse
fonte histórico ficou **enviesado**: em vários níveis a resposta certa aparecia
com frequência desproporcional na mesma letra (por exemplo, **~78%** das
questões de júnior e **~96%** de sênior com gabarito na **segunda** opção, e
**~49%** no pleno). Quem marcava sempre a mesma posição sem ler o enunciado
podia obter nota alta sem refletir o conhecimento real.

O comando `python manage.py seed_interviews` corrige isso ao persistir as
questões no banco:

- **Embaralha a ordem das quatro alternativas** de cada pergunta de modo
  **determinístico** (mesmo repositório + mesmo índice da questão → mesma
  permutação após cada seed), para a prova não depender da letra “padrão” do
  YAML.
- Usa **entropia em camadas por nível**: júnior mistura com base só no nível e
  na ordem da questão; **pleno** incorpora hash do enunciado e do texto da
  alternativa correta; **sênior** aplica uma rodada extra de mistura sobre esse
  material, ficando **o mais sensível ao conteúdo** e menos previsível só pelo
  número da questão.
- Há testes que exigem que, após o seed, nenhuma posição (A/B/C/D) concentre a
  maioria das respostas certas em um nível.

Isso é **independente** do embaralhamento da **lista das 100 questões** de cada
tentativa: ao iniciar um teste, o servidor sorteia quais 100 IDs entram e em que
ordem (`random.shuffle` no fluxo de início). Ou seja: cada prova já traz ordem
de questões aleatória; o seed cuida para que **dentro** de cada questão a letra
correta não siga um padrão fixo vindo do arquivo.

Para depuração pontual (não use em produção), é possível manter a ordem literal
do arquivo com `python manage.py seed_interviews --no-shuffle`.

## Regenerando migrações localmente (opcional)

Se você alterar modelos:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

Caso prefira gerar migrações fora do container, há um settings reduzido
em `pdt/config/settings_genmigrations.py` (sem dependências de
allauth/channels) usado durante o setup inicial. Não use em produção.

## Rodando os testes

A suíte usa **pytest + pytest-django + pytest-asyncio** com SQLite em
memória e `InMemoryChannelLayer`, então **não precisa de Postgres nem de
Redis** rodando, apenas Docker para garantir o Python 3.12 e as
dependências congeladas em `requirements.txt`.

```bash
cd pdt
# opção 1: build + run direto
docker build -f Dockerfile.test -t pdt-test:local .
docker run --rm pdt-test:local            # roda toda a suíte
docker run --rm pdt-test:local -k assess  # filtra por nome
docker run --rm pdt-test:local apps/courses/tests.py

# opção 2: via docker compose (profile dedicado, não interfere no `up`)
docker compose --profile test run --rm tests
docker compose --profile test run --rm tests -k assess
```

A suíte cobre, entre outros (160 testes, 0 falhas):

- modelo `User` (manager + e-mail-as-username + display name + carreira);
- middleware `AdmissionGateMiddleware` (gating + bypass de staff);
- fluxo completo do **teste de admissão** (sorteio 5 Linux + 5 redes,
  cooldown, aprovação no limite, marca `admission_passed`);
- **integridade do conteúdo**: 6 fases × 10 tópicos × 10 questões com
  exatamente 1 alternativa correta, 5+ materiais e aulas com
  `intro/body/practical` preenchidos;
- comando `seed_topics` idempotente;
- fluxo do **quiz** + atualização de `TopicScore` (mantém o melhor);
- radar e **leaderboard** (opt-in, ordenação, exclusão de pendentes);
- API HTTP de **mapa e pedidos de ajuda** (criação, join, resolve com
  bônus, cancelamento, ACL);
- **WebSocket** da sala de ajuda (`HelpRoomConsumer`): autenticação,
  rejeição de estranhos, propagação de chat, relay de sinalização
  WebRTC apenas para o peer correto;
- **simulador de entrevistas**: progressão de carreira sequencial
  (`Estagiário → Júnior → Pleno → Sênior`), bloqueio quando não há
  pré-requisito, aprovação a 80%, persistência de respostas com
  retomada exata da próxima questão sem resposta, save & exit, ações
  `next/prev/finish/cancel`, isolamento entre usuários, comando
  `seed_interviews` idempotente com 300 questões e embaralhamento
  determinístico em camadas (júnior → pleno → sênior).
- **qualidade das questões do simulador**: garantia anti-regressão de
  que distratores não voltem a ser preguiçosos, frases como
  *"Não há motivo."*, *"Festa."* ou *"Apenas marketing."* ficam
  bloqueadas por banlist; distratores precisam ter ≥ 3 palavras e
  ≥ 14 caracteres (ou serem siglas correlatas quando a correta é sigla)
  e nunca podem ser drasticamente mais curtos que a alternativa correta.

## Design de Cores, Baseado em Evidências

A paleta de cores da plataforma foi projetada a partir de pesquisa científica
sobre cognição e aprendizagem, não apenas estética.

### Fontes consultadas

| Estudo | Achado aplicado |
|--------|----------------|
| *Frontiers in Psychology* 2024, Interplay of Information Relevance and Colorfulness | Contraste de cor em conteúdo relevante vs. irrelevante reduz carga cognitiva e aumenta retenção/transferência (p < 0,001) |
| Estudo de Sala de Aula 2024 (RC Research Archive) | Ambientes **cool** (azul, teal, verde) obtiveram AAS **81,15 vs 72,40** em ambientes warm, diferença estatisticamente significativa em atenção |
| *Frontiers Psych* 2025 / Beihang + PMC | Fundo **verde-claro em telas** reduz fadiga visual, emoção negativa e melhora desempenho de leitura vs. branco puro |
| Shift eLearning / Psychology Town | Azul melhora atenção sustentada; **color-coding congruente** eleva recall; vermelho reservado para urgência |

### Decisões de paleta

| Elemento | Cor anterior | Cor nova | Razão científica |
|----------|-------------|----------|-----------------|
| Fundo base | `#020617` (preto-slate) | `#04091c` navy profundo | Azul escuro reduz stress vs preto absoluto |
| Cards / superfícies | slate-900 cinza | `#07122a` navy | Mais azul → mais foco |
| Accent primário | `#10b981` emerald | `#0891b2` sky-teal | Combina **azul** (foco) + **verde** (leitura) |
| Cabeçalhos de aula | branco puro | `#7dd3fc` sky-300 | Color-coding de estrutura → navegação cognitiva |
| Sub-seções | branco | `#93c5fd` blue-300 | Hierarquia visual → reduz carga cognitiva |
| Código inline | cinza neutro | `#67e8f9` cyan-300 | Máximo contraste para tokens técnicos |
| Bloco de código | sem âncora | `border-left: 4px teal` | Âncora visual → facilita scanning do código |
| Área de leitura | `prose-invert` genérico | `.lesson-body` dedicado | `font-size: 1.0625rem`, `line-height: 1.75`, `max-width: 72ch`, faixa ótima de legibilidade |
| Seleção de texto | padrão do navegador | fundo teal translúcido | Reforço de cor durante leitura ativa |

### Princípio geral

> Tons **frios** (azul, teal) dominam áreas de concentração/leitura.
> Tons **quentes** (âmbar, vermelho) são reservados exclusivamente para
> estados de alerta, erro ou urgência (ex.: pin de pedido de ajuda no mapa).
> Isso segue o princípio de *signaling* estudado em design instrucional.

---

## Roadmap não-implementado nesta versão

- **Compartilhamento de tela** na sala de ajuda. Hoje a sala já roda
  voz + chat de texto via WebRTC nativo (sinalização por WebSocket); a
  feature de screen-share pode ser adicionada com
  `getDisplayMedia()` + outra `RTCPeerConnection`.
- **TURN server dedicado**. Os ICE servers padrão são apenas STUNs
  públicos do Google, suficientes para a maioria das redes domésticas.
  Em redes corporativas com NAT simétrico, configure um TURN próprio
  (ex.: Coturn) e exporte via `WEBRTC_ICE_SERVERS_JSON`.
- Internacionalização (hoje todo o conteúdo está em pt-BR).
- Pipelines de CI/CD com lint, testes e build da imagem Docker.

## Contribuindo

Veja [CONTRIBUTING.md](./CONTRIBUTING.md). Em resumo: abra issue antes,
fork, branch com prefixo padronizado (`feat/`, `fix/`, `content/` etc.),
respeite o estilo e a licença.

## Contato

Para autorização de uso/operação ou parcerias, abra uma issue com a label
`license-request` ou envie e-mail para o mantenedor (atualize aqui o seu
endereço pessoal antes de tornar o repositório público).

## Licença

Distribuído sob os termos do arquivo [LICENSE](./LICENSE), uso somente
com **consentimento prévio do criador**.
