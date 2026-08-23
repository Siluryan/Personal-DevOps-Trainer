"""Fase 6, Programação em Python para DevOps & DevSecOps."""
from ._helpers import m, q

PHASE6 = {
    "name": "Fase 6: Programação em Python para DevOps",
    "description": (
        "A linguagem 'cola' do mundo de operações: scripts, automação, "
        "ferramentas internas, APIs e integração com nuvem e Kubernetes."
    ),
    "topics": [
        # =====================================================================
        # 6.1 Fundamentos de Python moderno
        # =====================================================================
        {
            "title": "Fundamentos de Python moderno",
            "summary": "Sintaxe, tipos, controle de fluxo, funções e type hints, a base que todo script de produção assume.",
            "lesson": {
                "intro": (
                    "Python é a linguagem de fato do mundo DevOps. Está nos clientes oficiais "
                    "da AWS (boto3), Kubernetes, GCP, Ansible, SaltStack, Apache Airflow, "
                    "Jupyter, e em milhares de scripts <em>colando</em> ferramentas em "
                    "pipelines reais. Esta primeira aula cobre o subset que mais aparece "
                    "em código de produção, não a versão de livro, mas a que você precisa "
                    "ler e escrever todo dia.<br><br>"
                    "Vamos focar em Python 3.11+ (versão alvo recomendada): pattern matching, "
                    "type hints e mensagens de erro melhoradas mudaram bastante o jeito de "
                    "escrever ferramentas modernas."
                ),
                "body": (
                    "<h3>1. Tipos primitivos e modelo de objeto</h3>"
                    "<p>Em Python, <strong>tudo é objeto</strong>. Inteiros, strings, funções, "
                    "classes, todos têm atributos e métodos. Os tipos primitivos importantes:</p>"
                    "<pre><code>x: int   = 42\n"
                    "y: float = 3.14\n"
                    "s: str   = \"hello\"\n"
                    "b: bool  = True\n"
                    "n: None  = None  # type literal None == NoneType\n"
                    "lst: list[int]      = [1, 2, 3]\n"
                    "tup: tuple[int, str] = (1, \"a\")\n"
                    "st:  set[str]       = {\"a\", \"b\"}\n"
                    "d:   dict[str, int] = {\"k\": 1}</code></pre>"
                    "<p>Diferenças críticas:</p>"
                    "<ul>"
                    "<li><code>list</code> é mutável; <code>tuple</code> é imutável (e portanto "
                    "<em>hashable</em>: pode ser chave de dicionário ou item de set).</li>"
                    "<li><code>str</code> é imutável, toda 'modificação' cria nova string. "
                    "Concatenar em loop com <code>+=</code> é O(n²); use "
                    "<code>\"\".join(list)</code>.</li>"
                    "<li>Inteiros têm precisão arbitrária (não estouram em 64 bits).</li>"
                    "</ul>"

                    "<h3>2. Variáveis, escopo e mutabilidade</h3>"
                    "<p>Variáveis em Python são <em>nomes</em> apontando para objetos. "
                    "Atribuição não copia:</p>"
                    "<pre><code>a = [1, 2, 3]\n"
                    "b = a               # b aponta para o MESMO objeto\n"
                    "b.append(4)\n"
                    "print(a)            # [1, 2, 3, 4]  ← surpresa para iniciantes\n\n"
                    "import copy\n"
                    "c = copy.copy(a)        # cópia rasa\n"
                    "d = copy.deepcopy(a)    # cópia profunda</code></pre>"
                    "<p>Escopo segue a regra <strong>LEGB</strong>: Local → Enclosing → "
                    "Global → Built-in. Para <em>escrever</em> em escopo externo dentro de "
                    "função, use <code>global</code> (ruim) ou <code>nonlocal</code> "
                    "(closures); melhor: receba/retorne valores explicitamente.</p>"

                    "<h3>3. Controle de fluxo: if, while, for</h3>"
                    "<p>O <code>for</code> em Python itera sobre <strong>iteráveis</strong>, "
                    "não sobre índices. O loop com índice (<code>for i in range(len(...))"
                    "</code>) é code smell, quase sempre dá pra usar <code>enumerate</code> "
                    "ou <code>zip</code>:</p>"
                    "<pre><code>servers = [\"web1\", \"web2\", \"db1\"]\n"
                    "ports   = [80, 80, 5432]\n\n"
                    "for i, name in enumerate(servers, start=1):\n"
                    "    print(f\"#{i} {name}\")\n\n"
                    "for name, port in zip(servers, ports, strict=True):\n"
                    "    print(f\"{name} :{port}\")</code></pre>"
                    "<p><strong>Truthiness</strong>: em Python, <code>0</code>, "
                    "<code>None</code>, listas/dicts/strings vazias, <code>False</code> são "
                    "todos <em>falsy</em>. Não escreva <code>if len(lst) &gt; 0:</code>, "
                    "escreva <code>if lst:</code>. E não compare com <code>True/False</code> "
                    "(<code>if x == True</code>). Compare com <code>None</code> usando "
                    "<code>is</code>: <code>if x is None</code>.</p>"

                    "<h3>4. <code>match</code>: pattern matching estrutural (3.10+)</h3>"
                    "<p>O <code>match</code> não é um <code>switch</code>: ele faz "
                    "<em>destructuring</em> + checagem de tipo:</p>"
                    "<pre><code>def handle(event: dict) -&gt; str:\n"
                    "    match event:\n"
                    "        case {\"type\": \"deploy\", \"env\": \"prod\", \"image\": img}:\n"
                    "            return f\"PROD deploy: {img}\"\n"
                    "        case {\"type\": \"deploy\", \"env\": env}:\n"
                    "            return f\"{env} deploy\"\n"
                    "        case {\"type\": \"rollback\", \"version\": v} if v &lt; 10:\n"
                    "            return f\"rollback recente para {v}\"\n"
                    "        case _:\n"
                    "            return \"unknown\"</code></pre>"
                    "<p>Útil pra parsear payloads de webhooks, eventos de SQS/PubSub, "
                    "CloudEvents, etc.</p>"

                    "<h3>5. Funções: argumentos posicionais, kwargs, defaults</h3>"
                    "<pre><code>def deploy(\n"
                    "    image: str,                       # posicional\n"
                    "    *,                                # tudo depois é keyword-only\n"
                    "    replicas: int = 3,\n"
                    "    canary: bool = False,\n"
                    "    extra_env: dict[str, str] | None = None,\n"
                    ") -&gt; bool:\n"
                    "    ...\n\n"
                    "deploy(\"web:1.2\", replicas=5, canary=True)</code></pre>"
                    "<p>Boas práticas:</p>"
                    "<ul>"
                    "<li>Use <code>*</code> para forçar parâmetros como keyword-only quando "
                    "houver ambiguidade (ex: 'deploy(\"web\", 5, True)' fica obscuro).</li>"
                    "<li><strong>Nunca</strong> use objetos mutáveis como default: "
                    "<code>def f(x=[])</code> compartilha a mesma lista entre chamadas. "
                    "Use <code>None</code> e crie dentro.</li>"
                    "<li><code>*args</code> e <code>**kwargs</code> recebem extras. Ótimo para "
                    "decorators e wrappers; perigoso para APIs públicas (perde-se a "
                    "documentação).</li>"
                    "</ul>"

                    "<h3>6. Type hints e por que escrevê-los</h3>"
                    "<p>Type hints não afetam o runtime (Python continua dinâmico), mas "
                    "habilitam ferramentas:</p>"
                    "<ul>"
                    "<li><strong>mypy</strong> / <strong>pyright</strong>: pegam bugs na CI "
                    "(passar <code>None</code> onde se esperava <code>str</code>, esquecer "
                    "branch, etc.).</li>"
                    "<li><strong>IDE</strong>: autocomplete real, navegação, refactor seguro.</li>"
                    "<li><strong>Documentação</strong>: a assinatura já é o contrato.</li>"
                    "</ul>"
                    "<pre><code>from typing import Iterable, Protocol\n\n"
                    "def total(items: Iterable[float]) -&gt; float:\n"
                    "    return sum(items)\n\n"
                    "class Storer(Protocol):\n"
                    "    def save(self, key: str, blob: bytes) -&gt; None: ...\n\n"
                    "def upload(s: Storer, k: str, b: bytes) -&gt; None:\n"
                    "    s.save(k, b)   # qualquer classe com .save() compatível serve</code></pre>"
                    "<p>Em Python 3.10+ você usa <code>X | Y</code> (em vez de "
                    "<code>Union[X, Y]</code>) e <code>list[int]</code> (em vez de "
                    "<code>List[int]</code>).</p>"

                    "<h3>7. Strings: f-strings e formatação</h3>"
                    "<p>F-strings (3.6+) são o padrão. Em 3.12+ aceitam aspas e backslashes:</p>"
                    "<pre><code>name, port = \"web\", 80\n"
                    "print(f\"{name}:{port}\")             # web:80\n"
                    "print(f\"{name:&gt;10}|{port:05d}\")    # padding e zero-pad\n"
                    "print(f\"{3.14159:.2f}\")             # 3.14\n"
                    "print(f\"{name=}, {port=}\")           # debug: name='web', port=80</code></pre>"
                    "<p>Para logs estruturados, prefira <code>logger.info(\"deploying %s\", "
                    "name)</code> em vez de f-string, assim o log handler decide se "
                    "renderiza (economia de CPU em DEBUG desativado).</p>"

                    "<h3>8. Erros mais comuns para quem vem de outra linguagem</h3>"
                    "<ul>"
                    "<li>Comparar floats com <code>==</code>: use <code>math.isclose()</code>.</li>"
                    "<li>Confundir <code>is</code> com <code>==</code>: <code>is</code> "
                    "compara identidade (mesmo objeto), <code>==</code> compara valor.</li>"
                    "<li>Usar <code>type(x) == int</code> em vez de "
                    "<code>isinstance(x, int)</code>: o segundo aceita subclasses.</li>"
                    "<li>Não usar context managers: arquivos, locks, conexões "
                    "<strong>devem</strong> ser usados com <code>with</code>.</li>"
                    "</ul>"
                ),
                "practical": (
                    "Crie um script <code>checklog.py</code> que: (1) recebe via "
                    "<code>sys.argv</code> um caminho de arquivo de log; (2) abre com "
                    "<code>with open()</code>; (3) conta linhas contendo "
                    "<code>ERROR</code>, <code>WARN</code>, <code>INFO</code>; (4) imprime "
                    "um sumário formatado com f-strings (largura fixa). Use type hints em "
                    "todas as funções e rode <code>python -m mypy checklog.py</code> sem "
                    "erros."
                ),
            },
            "materials": [
                m("Python Tutorial, docs oficial",
                  "https://docs.python.org/3/tutorial/",
                  "docs", "Tutorial canônico, leitura obrigatória."),
                m("Real Python: Python Type Checking",
                  "https://realpython.com/python-type-checking/",
                  "article", "Guia prático de type hints."),
                m("PEP 8, Style Guide",
                  "https://peps.python.org/pep-0008/",
                  "docs", "Convenções de formatação que todos seguem."),
                m("PEP 634, Structural Pattern Matching",
                  "https://peps.python.org/pep-0634/",
                  "docs", "Especificação do match/case."),
                m("Trey Hunner: Python truthiness",
                  "https://treyhunner.com/2019/03/unique-and-sentinel-values-in-python/",
                  "article", "Por que `if x:` é melhor que `if x is True`."),
                m("Anthony Sottile (anthonywritescode), YouTube",
                  "https://www.youtube.com/c/anthonywritescode",
                  "video", "Vídeos curtos sobre Python idiomático."),
            ],
            "questions": [
                q("Qual a saída de `a = [1, 2]; b = a; b.append(3); print(a)`?",
                  "[1, 2, 3]",
                  ["[1, 2]", "Erro de execução", "[3]"],
                  "Atribuição não copia em Python: `b` referencia o mesmo objeto que `a`. "
                  "Para copiar use `a.copy()` ou `copy.deepcopy(a)`."),
                q("Qual destes tipos NÃO pode ser chave de um dicionário?",
                  "list",
                  ["tuple", "str", "frozenset"],
                  "Chaves de dict precisam ser hashable (imutáveis). list é mutável, "
                  "logo não é hashable. tuple, str e frozenset são imutáveis."),
                q("Qual é a forma idiomática de checar se uma lista NÃO está vazia?",
                  "if lst:",
                  ["if len(lst) > 0:",
                   "if lst != []:",
                   "if lst is not None:"],
                  "Listas vazias são falsy. `if lst:` é claro e idiomático. "
                  "`is not None` checaria coisa diferente (existência da variável, não vazio)."),
                q("O que faz `*` na assinatura `def f(a, *, b, c):`?",
                  "Força b e c a serem passados como argumentos keyword-only.",
                  ["Cria parâmetros opcionais.",
                   "Recebe argumentos extras como tupla.",
                   "É um erro de sintaxe."],
                  "O `*` sozinho marca o limite: tudo depois precisa ser nomeado na chamada. "
                  "`*args` (com nome) é diferente, captura posicionais extras."),
                q("Por que `def f(x=[]):` é considerado um bug latente?",
                  "A lista default é compartilhada entre todas as chamadas e pode acumular estado.",
                  ["Python não permite valores mutáveis como default.",
                   "É só uma questão de estilo, sem efeito prático.",
                   "Causa erro de sintaxe a partir do 3.10."],
                  "Defaults são avaliados uma vez na definição da função. Se mutável, "
                  "todas as chamadas compartilham. Idiomático: `def f(x=None): x = x or []`."),
                q("Em Python 3.10+, como anotar 'string ou None'?",
                  "str | None",
                  ["Optional[str] (deprecado)",
                   "string?",
                   "str.None"],
                  "A sintaxe `X | Y` substituiu `Union[X, Y]` em 3.10+. "
                  "`Optional[X]` ainda funciona mas `X | None` é preferido."),
                q("Qual a diferença entre `is` e `==`?",
                  "`is` compara identidade (mesmo objeto na memória); `==` compara valor.",
                  ["São sinônimos.",
                   "`is` só funciona com inteiros.",
                   "`==` é mais lento."],
                  "Use `is` para comparar com `None`, `True`, `False`. Para igualdade "
                  "de valor use `==`."),
                q("O que `f\"{x=}\"` produz se x = 42?",
                  "x=42",
                  ["42", "x", "{x: 42}"],
                  "Sintaxe de debug das f-strings (3.8+): inclui o nome da variável "
                  "seguido do valor, útil pra logs rápidos."),
                q("Como concatenar muitas strings com performance O(n)?",
                  "\"\".join(lista_de_strings)",
                  ["soma com += em loop",
                   "string + string + ...",
                   "operator.concat()"],
                  "Strings são imutáveis: cada `+=` cria nova. `str.join` aloca uma vez."),
                q("Qual destas é a maneira correta de iterar com índice?",
                  "for i, item in enumerate(lst):",
                  ["for i in range(len(lst)): item = lst[i]",
                   "for i, item in zip(range(len(lst)), lst):",
                   "i = 0; for item in lst: i += 1"],
                  "`enumerate` é o padrão. As outras funcionam mas são verbosas."),
            ],
        },
        # =====================================================================
        # 6.2 Estruturas de dados e código Pythonic
        # =====================================================================
        {
            "title": "Estruturas de dados e código Pythonic",
            "summary": "List, dict, set, comprehensions, generators e a stdlib que economiza horas (collections, itertools).",
            "lesson": {
                "intro": (
                    "Aqui mora a diferença entre código Python e código 'Java escrito em "
                    "Python'. Código pythonic costuma ser mais curto, mais rápido e mais "
                    "legível, porque delega para estruturas e funções otimizadas em C "
                    "(<code>list</code>, <code>dict</code>, <code>itertools</code>...).<br><br>"
                    "Esta aula é um catálogo do que aparece em código de produção real "
                    "todos os dias."
                ),
                "body": (
                    "<h3>1. Listas, tuplas, sets, dicts: quando usar cada um</h3>"
                    "<table>"
                    "<thead><tr><th>Estrutura</th><th>Acesso</th><th>Mutável</th>"
                    "<th>Caso típico</th></tr></thead>"
                    "<tbody>"
                    "<tr><td><code>list</code></td><td>O(1) por índice</td><td>Sim</td>"
                    "<td>Coleção ordenada, fila de tarefas, batch.</td></tr>"
                    "<tr><td><code>tuple</code></td><td>O(1) por índice</td><td>Não</td>"
                    "<td>Registro fixo (lat, lng), retorno múltiplo.</td></tr>"
                    "<tr><td><code>set</code></td><td>O(1) <em>in</em></td><td>Sim</td>"
                    "<td>Deduplicação, testes de pertencimento.</td></tr>"
                    "<tr><td><code>dict</code></td><td>O(1) por chave</td><td>Sim</td>"
                    "<td>Mapeamento, contadores, configs.</td></tr>"
                    "</tbody></table>"
                    "<p>Regra prática: se você está fazendo <code>x in lista</code> dentro "
                    "de loop, troque por <code>set</code>, vai de O(n) para O(1).</p>"

                    "<h3>2. Comprehensions: o pão com manteiga</h3>"
                    "<pre><code># list\n"
                    "ips = [host[\"ip\"] for host in hosts if host[\"alive\"]]\n\n"
                    "# dict\n"
                    "by_name = {h[\"name\"]: h for h in hosts}\n\n"
                    "# set\n"
                    "unique_envs = {h[\"env\"] for h in hosts}\n\n"
                    "# generator (lazy)\n"
                    "total = sum(h[\"cpu\"] for h in hosts)</code></pre>"
                    "<p>Diretrizes:</p>"
                    "<ul>"
                    "<li>Comprehension é mais rápida que <code>for + append</code>.</li>"
                    "<li>Não escreva comprehension de comprehension de comprehension. "
                    "Se passou de duas linhas, vire um <code>for</code>.</li>"
                    "<li>Para acumulação com efeito colateral (gravar em log, escrever "
                    "no banco), use loop normal, não comprehension.</li>"
                    "</ul>"

                    "<h3>3. Generators: lazy evaluation</h3>"
                    "<p>Generators produzem itens sob demanda (não constroem a lista "
                    "inteira em memória). Essenciais para arquivos grandes:</p>"
                    "<pre><code>def parse_log(path: str):\n"
                    "    with open(path) as f:\n"
                    "        for line in f:\n"
                    "            if \"ERROR\" in line:\n"
                    "                yield line.strip()\n\n"
                    "for err in parse_log(\"/var/log/app.log\"):\n"
                    "    print(err)</code></pre>"
                    "<p>O arquivo pode ter 50 GB, só uma linha por vez na memória. "
                    "Equivalentes idiomáticos:</p>"
                    "<pre><code>errors = (line for line in open(\"app.log\") if \"ERROR\" in line)\n"
                    "first_5 = list(itertools.islice(errors, 5))</code></pre>"

                    "<h3>4. <code>collections</code>: a stdlib que ninguém lê</h3>"
                    "<pre><code>from collections import Counter, defaultdict, deque, namedtuple, OrderedDict\n\n"
                    "# Counter, conta ocorrências em uma linha\n"
                    "c = Counter(line.split()[0] for line in open(\"access.log\"))\n"
                    "c.most_common(10)        # top 10 IPs\n\n"
                    "# defaultdict, sem precisar checar 'if key not in d'\n"
                    "by_status = defaultdict(list)\n"
                    "for req in requests:\n"
                    "    by_status[req.status].append(req)\n\n"
                    "# deque, fila com pop/append O(1) em ambas pontas\n"
                    "rolling = deque(maxlen=100)   # janela deslizante\n"
                    "for v in stream: rolling.append(v)\n\n"
                    "# namedtuple, registro imutável com nomes\n"
                    "Host = namedtuple(\"Host\", [\"name\", \"ip\", \"port\"])\n"
                    "h = Host(\"web1\", \"10.0.1.5\", 80)\n"
                    "print(h.ip)</code></pre>"

                    "<h3>5. <code>itertools</code>: combinatória e iteração eficiente</h3>"
                    "<pre><code>import itertools as it\n\n"
                    "# chain: concatenar iteráveis\n"
                    "for x in it.chain(list_a, list_b, list_c): ...\n\n"
                    "# groupby: agrupa adjacentes (precisa estar ordenado)\n"
                    "logs.sort(key=lambda l: l.host)\n"
                    "for host, entries in it.groupby(logs, key=lambda l: l.host):\n"
                    "    print(host, sum(1 for _ in entries))\n\n"
                    "# product: produto cartesiano\n"
                    "for env, region in it.product([\"dev\",\"prod\"], [\"us-east\",\"sa-east\"]):\n"
                    "    deploy(env, region)\n\n"
                    "# islice: paginação\n"
                    "page = list(it.islice(big_iter, 100, 200))   # itens 100..199</code></pre>"

                    "<h3>6. <code>dataclasses</code>: o jeito moderno de criar registros</h3>"
                    "<pre><code>from dataclasses import dataclass, field\n\n"
                    "@dataclass(frozen=True, slots=True)\n"
                    "class Host:\n"
                    "    name: str\n"
                    "    ip: str\n"
                    "    port: int = 22\n"
                    "    tags: tuple[str, ...] = ()\n\n"
                    "h = Host(\"web1\", \"10.0.1.5\", tags=(\"prod\", \"web\"))\n"
                    "# __init__, __repr__, __eq__ gerados automaticamente\n"
                    "# frozen=True torna imutável (hashable)\n"
                    "# slots=True economiza memória (sem __dict__)</code></pre>"
                    "<p>Para validação automática + serialização, considere "
                    "<strong>Pydantic v2</strong> (compatível com type hints).</p>"

                    "<h3>7. Slicing e desempacotamento</h3>"
                    "<pre><code>lst = [10, 20, 30, 40, 50]\n"
                    "lst[1:3]      # [20, 30]\n"
                    "lst[::2]      # [10, 30, 50], step 2\n"
                    "lst[::-1]     # [50, 40, 30, 20, 10], invertido\n\n"
                    "# Desempacotamento estendido\n"
                    "first, *middle, last = lst\n"
                    "# first=10, middle=[20,30,40], last=50\n\n"
                    "# Em dicts (3.5+)\n"
                    "merged = {**defaults, **user_overrides, \"build\": 42}</code></pre>"

                    "<h3>8. <code>enum.Enum</code> e <code>StrEnum</code> (3.11+)</h3>"
                    "<pre><code>from enum import StrEnum, auto\n\n"
                    "class Severity(StrEnum):\n"
                    "    INFO  = \"info\"\n"
                    "    WARN  = \"warn\"\n"
                    "    ERROR = \"error\"\n"
                    "    CRIT  = auto()\n\n"
                    "if level &gt;= Severity.WARN:   # comparações como string\n"
                    "    alert(level)</code></pre>"
                    "<p>Substitui <em>magic strings</em> ('error', 'warn'...) por "
                    "constantes type-safe.</p>"

                    "<h3>9. Caso real: pipeline de processamento de logs</h3>"
                    "<pre><code>from collections import Counter\n"
                    "import itertools as it, gzip, re\n\n"
                    "PAT = re.compile(r'^(\\S+) .* \"(\\w+) (\\S+) HTTP/.*\" (\\d+)')\n\n"
                    "def open_log(p):\n"
                    "    return gzip.open(p, 'rt') if p.endswith('.gz') else open(p)\n\n"
                    "def lines(paths):\n"
                    "    for p in paths:\n"
                    "        with open_log(p) as f:\n"
                    "            yield from f\n\n"
                    "def parsed(lines):\n"
                    "    for ln in lines:\n"
                    "        if (m := PAT.match(ln)):\n"
                    "            yield m.group(1), m.group(2), m.group(3), int(m.group(4))\n\n"
                    "files = [\"a.log\", \"b.log.gz\", \"c.log\"]\n"
                    "errors = (r for r in parsed(lines(files)) if r[3] &gt;= 500)\n"
                    "top = Counter(r[0] for r in it.islice(errors, 10000)).most_common(5)\n"
                    "print(top)</code></pre>"
                    "<p>Tudo lazy: lê só o necessário, processa em pipeline, sem carregar "
                    "GB em memória.</p>"
                ),
                "practical": (
                    "Escreva <code>top_users.py</code> que lê um <code>access.log</code> "
                    "(formato Combined do nginx/Apache) e imprime, em uma linha cada, os 10 "
                    "IPs mais frequentes <em>e</em> a quantidade de requisições com status "
                    "≥ 500 de cada um. Restrições: (1) use <code>collections.Counter</code>; "
                    "(2) não carregue o arquivo todo em memória, use generator; "
                    "(3) suporte arquivos <code>.gz</code> via <code>gzip.open</code>."
                ),
            },
            "materials": [
                m("Python docs, collections",
                  "https://docs.python.org/3/library/collections.html",
                  "docs", "Counter, defaultdict, deque, namedtuple."),
                m("Python docs, itertools",
                  "https://docs.python.org/3/library/itertools.html",
                  "docs", "Receitas de combinatória e iteração."),
                m("Real Python, Comprehensions",
                  "https://realpython.com/list-comprehension-python/",
                  "article", "Tutorial completo de comprehensions."),
                m("Dataclasses tutorial, RealPython",
                  "https://realpython.com/python-data-classes/",
                  "article", "Quando usar @dataclass."),
                m("Fluent Python (Luciano Ramalho)",
                  "https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/",
                  "book", "Livro de referência sobre código pythonic."),
                m("PEP 3132, Extended Iterable Unpacking",
                  "https://peps.python.org/pep-3132/",
                  "docs", "Sintaxe `first, *middle, last = lst`."),
            ],
            "questions": [
                q("Qual estrutura escolher para testar 'item está nesta coleção' rapidamente?",
                  "set",
                  ["list (com `in`)",
                   "tuple",
                   "string"],
                  "`x in set` é O(1). `x in list` é O(n). Para checagens repetidas em "
                  "loop, set é muito superior."),
                q("O que faz `[x*2 for x in range(5)]`?",
                  "Cria a lista [0, 2, 4, 6, 8].",
                  ["Cria um generator que produz 0, 2, 4, 6, 8.",
                   "Multiplica cada elemento por 2 in-place.",
                   "Retorna 5 vezes 2."],
                  "Comprehension entre colchetes constrói lista. Entre parênteses seria "
                  "generator (lazy)."),
                q("Por que generators são ideais para arquivos grandes?",
                  "Produzem um item por vez, não carregam tudo em memória.",
                  ["São sempre mais rápidos que listas.",
                   "Aproveitam multi-thread automaticamente.",
                   "Comprimem os dados."],
                  "Memória constante: você processa um arquivo de 50 GB com poucos KB "
                  "de RAM."),
                q("O que `Counter([\"a\",\"b\",\"a\"]).most_common(1)` retorna?",
                  "[('a', 2)]",
                  ["{'a': 2, 'b': 1}", "['a']", "2"],
                  "Counter é um dict que mapeia item→contagem; `most_common(n)` retorna "
                  "lista de tuplas ordenadas por contagem decrescente."),
                q("Para que serve `defaultdict(list)`?",
                  "Cria um dict que retorna [] automaticamente para chaves inexistentes.",
                  ["É um dict que ordena as chaves.",
                   "Compactua dicts em paralelo.",
                   "Limita o tamanho do dict."],
                  "Evita o padrão `if k not in d: d[k] = []`. Uma chave acessada que "
                  "não existe é criada com o valor default."),
                q("`@dataclass(frozen=True)` torna a classe...",
                  "Imutável e hashable (utilizável como chave de dict ou item de set).",
                  ["Mais rápida em runtime.",
                   "Sincronizada para multi-thread.",
                   "Compactável com pickle obrigatoriamente."],
                  "frozen impede modificação após init e ativa __hash__ baseado nos "
                  "campos."),
                q("Qual a saída de `lst[::-1]` se lst = [1,2,3]?",
                  "[3, 2, 1]",
                  ["[1, 2, 3]", "[]", "[1]"],
                  "Slice com step -1 inverte a sequência. Atalho clássico para "
                  "reverter listas/strings."),
                q("Qual destas é uma DESVANTAGEM de comprehensions?",
                  "Ficam ilegíveis quando aninhadas profundamente ou com filtros complexos.",
                  ["São mais lentas que loops for.",
                   "Não funcionam com generators.",
                   "Não suportam condicionais."],
                  "Performance é geralmente melhor que for+append. O risco é cognitivo: "
                  "comprehension de 4 linhas com 2 ifs é pior que loop explícito."),
                q("`{**a, **b}` quando há chaves repetidas...",
                  "Mantém o valor do último dict (b sobrescreve a).",
                  ["Soma os valores.",
                   "Levanta KeyError.",
                   "Mantém o primeiro (a)."],
                  "Padrão merge: o último ganha. Idiomático para juntar config default + "
                  "override do usuário."),
                q("Para iterar uma coleção descobrindo o índice ao mesmo tempo:",
                  "for i, x in enumerate(lst):",
                  ["for i in range(len(lst)): x = lst[i]",
                   "for x, i in lst.items():",
                   "for x in lst.keys(): ..."],
                  "`enumerate` é a forma idiomática. Aceita `start=1` para numerar a "
                  "partir de 1."),
            ],
        },
        # =====================================================================
        # 6.3 POO, exceções e context managers
        # =====================================================================
        {
            "title": "POO, exceções e context managers",
            "summary": "Classes em Python real, dunder methods, hierarquia de exceções e gerenciamento de recursos.",
            "lesson": {
                "intro": (
                    "Python não força você a usar classes, funções e dicts cobrem 80% "
                    "dos casos. Mas quando o estado fica grande ou um comportamento "
                    "precisa de polimorfismo (vários backends de storage, drivers de "
                    "banco diferentes), classes pagam a complexidade. Esta aula cobre o "
                    "modelo OOP de Python, os dunder methods que você precisa conhecer, "
                    "como tratar erros sem 'engolir' bugs e como usar context managers "
                    "para garantir cleanup."
                ),
                "body": (
                    "<h3>1. Classes básicas</h3>"
                    "<pre><code>class Server:\n"
                    "    def __init__(self, name: str, ip: str, port: int = 22) -&gt; None:\n"
                    "        self.name = name\n"
                    "        self.ip   = ip\n"
                    "        self.port = port\n\n"
                    "    def url(self) -&gt; str:\n"
                    "        return f\"ssh://{self.ip}:{self.port}\"\n\n"
                    "s = Server(\"web1\", \"10.0.1.5\")\n"
                    "print(s.url())</code></pre>"
                    "<p>Pontos importantes:</p>"
                    "<ul>"
                    "<li><code>__init__</code> NÃO é o construtor, é o inicializador. O "
                    "construtor real é <code>__new__</code> (raro mexer).</li>"
                    "<li><code>self</code> é convenção, não palavra reservada. Mas todo "
                    "mundo espera ver <code>self</code>.</li>"
                    "<li>Em classes que viram registro/struct, prefira "
                    "<code>@dataclass</code> em vez de escrever <code>__init__</code> e "
                    "<code>__repr__</code> à mão.</li>"
                    "</ul>"

                    "<h3>2. Atributos de classe vs. de instância</h3>"
                    "<pre><code>class Cache:\n"
                    "    DEFAULT_TTL = 60                  # atributo de classe (compartilhado)\n\n"
                    "    def __init__(self):\n"
                    "        self.store = {}               # atributo de instância (próprio)\n"
                    "\n"
                    "Cache.DEFAULT_TTL = 120              # muda para todo mundo\n"
                    "Cache().DEFAULT_TTL = 30             # cria instância: shadow!</code></pre>"
                    "<p>Erro clássico: usar <code>list</code> como atributo de classe, "
                    "vira estado global compartilhado entre todas as instâncias.</p>"

                    "<h3>3. Herança e <code>super()</code></h3>"
                    "<pre><code>class HTTPError(Exception):\n"
                    "    pass\n\n"
                    "class RetryableHTTPError(HTTPError):\n"
                    "    def __init__(self, status: int, body: str):\n"
                    "        super().__init__(f\"retryable {status}\")\n"
                    "        self.status = status\n"
                    "        self.body   = body</code></pre>"
                    "<p>Herança múltipla existe e é útil para mixins (ex: "
                    "<code>LoggingMixin</code>); evite hierarquias profundas.</p>"

                    "<h3>4. Dunder methods que valem decorar</h3>"
                    "<table>"
                    "<thead><tr><th>Método</th><th>Para quê</th></tr></thead>"
                    "<tbody>"
                    "<tr><td><code>__repr__</code></td><td>Representação de debug. Sempre defina.</td></tr>"
                    "<tr><td><code>__str__</code></td><td>Para humanos (<code>str(x)</code>, <code>print</code>).</td></tr>"
                    "<tr><td><code>__eq__</code>, <code>__hash__</code></td><td>Igualdade e uso em set/dict.</td></tr>"
                    "<tr><td><code>__len__</code>, <code>__contains__</code>, <code>__iter__</code></td><td>Coleções customizadas.</td></tr>"
                    "<tr><td><code>__enter__</code>, <code>__exit__</code></td><td>Context manager (<code>with</code>).</td></tr>"
                    "<tr><td><code>__call__</code></td><td>Faz a instância ser chamável como função.</td></tr>"
                    "</tbody></table>"

                    "<h3>5. Properties: getters/setters bem feitos</h3>"
                    "<pre><code>class Replica:\n"
                    "    def __init__(self, count: int):\n"
                    "        self._count = 0\n"
                    "        self.count = count   # passa pelo setter\n\n"
                    "    @property\n"
                    "    def count(self) -&gt; int:\n"
                    "        return self._count\n\n"
                    "    @count.setter\n"
                    "    def count(self, v: int) -&gt; None:\n"
                    "        if v &lt; 0 or v &gt; 100:\n"
                    "            raise ValueError(f\"replicas {v} fora do range\")\n"
                    "        self._count = v</code></pre>"
                    "<p>Use property quando precisa validar ou calcular, não para todo "
                    "atributo. Atributo público é a maneira pythonic; só promova a "
                    "property quando há regra.</p>"

                    "<h3>6. Hierarquia de exceções</h3>"
                    "<p>Exceções são objetos de classes que descendem de "
                    "<code>BaseException</code>:</p>"
                    "<pre><code>BaseException\n"
                    "├── SystemExit         # sys.exit(), não capture genericamente\n"
                    "├── KeyboardInterrupt  # Ctrl+C, não capture genericamente\n"
                    "├── GeneratorExit\n"
                    "└── Exception          # ← capture este\n"
                    "    ├── ValueError\n"
                    "    ├── TypeError\n"
                    "    ├── KeyError\n"
                    "    ├── OSError\n"
                    "    │   ├── FileNotFoundError\n"
                    "    │   ├── PermissionError\n"
                    "    │   ├── ConnectionError\n"
                    "    │   └── TimeoutError\n"
                    "    └── ...</code></pre>"
                    "<p>Regras:</p>"
                    "<ul>"
                    "<li>Capture o <strong>mais específico</strong> que você sabe tratar. "
                    "<code>except Exception</code> só na borda do programa (handlers HTTP, "
                    "main loop). <code>except:</code> sem nada é proibido, captura até "
                    "<code>KeyboardInterrupt</code>.</li>"
                    "<li>Re-lançar com contexto: <code>raise NewError(...) from old</code>. "
                    "O traceback fica encadeado, ótimo para debugging.</li>"
                    "<li>Crie suas próprias classes para erros do domínio: "
                    "<code>class DeployError(Exception): ...</code>.</li>"
                    "</ul>"

                    "<h3>7. <code>try / except / else / finally</code></h3>"
                    "<pre><code>try:\n"
                    "    cfg = load_config(path)\n"
                    "except FileNotFoundError:\n"
                    "    cfg = default_config()\n"
                    "except OSError as e:\n"
                    "    log.error(\"erro de I/O\", exc_info=e)\n"
                    "    raise\n"
                    "else:\n"
                    "    log.info(\"config carregada\")    # só se NÃO houve exceção\n"
                    "finally:\n"
                    "    cleanup()                          # sempre roda</code></pre>"
                    "<p>O <code>else</code> ajuda a manter o try com a operação "
                    "<em>arriscada</em> apenas, facilita ver onde a exceção pode vir.</p>"

                    "<h3>8. Context managers e o <code>with</code></h3>"
                    "<p>Garantem cleanup mesmo em caso de erro. O padrão é o "
                    "<code>open()</code>:</p>"
                    "<pre><code>with open(\"/etc/passwd\") as f:\n"
                    "    data = f.read()\n"
                    "# arquivo fechado AQUI, com ou sem exceção</code></pre>"
                    "<p>Para criar o seu, use <code>contextlib.contextmanager</code>:</p>"
                    "<pre><code>from contextlib import contextmanager\n"
                    "import time\n\n"
                    "@contextmanager\n"
                    "def timer(label: str):\n"
                    "    t = time.perf_counter()\n"
                    "    try:\n"
                    "        yield\n"
                    "    finally:\n"
                    "        print(f\"{label}: {time.perf_counter()-t:.3f}s\")\n\n"
                    "with timer(\"deploy\"):\n"
                    "    run_deploy()</code></pre>"
                    "<p>Combinar múltiplos:</p>"
                    "<pre><code>with open(\"a\") as a, open(\"b\") as b, lock:\n"
                    "    process(a, b)</code></pre>"

                    "<h3>9. ExceptionGroup (3.11+) e <code>except*</code></h3>"
                    "<p>Quando uma operação produz <em>vários</em> erros simultâneos "
                    "(asyncio.gather, TaskGroup), use <code>ExceptionGroup</code>:</p>"
                    "<pre><code>try:\n"
                    "    async with asyncio.TaskGroup() as tg:\n"
                    "        tg.create_task(fetch_a())\n"
                    "        tg.create_task(fetch_b())\n"
                    "except* ConnectionError as eg:\n"
                    "    log.warn(\"conexão: %d falhas\", len(eg.exceptions))\n"
                    "except* TimeoutError as eg:\n"
                    "    log.warn(\"timeout: %d\", len(eg.exceptions))</code></pre>"
                ),
                "practical": (
                    "Implemente uma classe <code>RetryableHTTP</code> com método "
                    "<code>get(url, retries=3)</code> que: (1) usa <code>requests.get</code>; "
                    "(2) captura <code>requests.HTTPError</code> apenas em status 5xx; "
                    "(3) faz retry com backoff exponencial (1s, 2s, 4s); (4) re-lança como "
                    "<code>DeployError</code> personalizado, encadeando a exceção original "
                    "com <code>raise ... from</code>. Adicione um context manager "
                    "<code>timed</code> que registra a duração de cada chamada."
                ),
            },
            "materials": [
                m("Python docs, Classes",
                  "https://docs.python.org/3/tutorial/classes.html",
                  "docs", "Tutorial oficial de classes."),
                m("Python docs, Errors and Exceptions",
                  "https://docs.python.org/3/tutorial/errors.html",
                  "docs", "Hierarquia de exceções."),
                m("Python docs, contextlib",
                  "https://docs.python.org/3/library/contextlib.html",
                  "docs", "Context managers prontos e helpers."),
                m("Real Python: OOP in Python",
                  "https://realpython.com/python3-object-oriented-programming/",
                  "article", "Tutorial detalhado de OOP."),
                m("PEP 654, Exception Groups",
                  "https://peps.python.org/pep-0654/",
                  "docs", "ExceptionGroup e except*."),
                m("Hynek Schlawack, Subclass at your own risk",
                  "https://hynek.me/articles/python-subclassing-redux/",
                  "article", "Quando NÃO usar herança."),
            ],
            "questions": [
                q("Qual destes deveria SEMPRE ser definido em uma classe customizada?",
                  "__repr__",
                  ["__init__ vazio para sobrescrever",
                   "__del__ para garantir cleanup",
                   "Nenhum dunder é obrigatório."],
                  "__repr__ é o que aparece em logs e debugger. Sem ele, depurar erros "
                  "vira advinhação. __del__ é raramente útil."),
                q("Para garantir que um arquivo seja fechado mesmo em caso de exceção:",
                  "with open(path) as f: ...",
                  ["try: f = open(path)\\n  ...\\nexcept: f.close()",
                   "Definir um destrutor.",
                   "Usar global e finalize manualmente."],
                  "Context manager (`with`) garante __exit__ sempre, mesmo com exceção. "
                  "É o jeito pythonic e seguro."),
                q("Capturar `BaseException` em código de aplicação é problemático porque...",
                  "Captura também SystemExit e KeyboardInterrupt, impedindo encerramento limpo.",
                  ["É lento.",
                   "Não funciona em Python 3.",
                   "Captura só erros de tipo."],
                  "BaseException é o topo. Aplicação deve capturar Exception ou subclasses. "
                  "Capturar BaseException pode ignorar Ctrl+C e sys.exit()."),
                q("`raise NewError(\"...\") from old` faz o quê?",
                  "Lança a nova exceção encadeando a original (preserva traceback).",
                  ["Substitui silenciosamente a original.",
                   "Causa erro de sintaxe.",
                   "Lança ambas em paralelo."],
                  "O `from` deixa explícito o encadeamento, o traceback mostra 'The "
                  "above exception was the direct cause of...' facilitando debugging."),
                q("Em `class Cache: items = []`, o que tem de errado se duas instâncias chamarem `.items.append(x)`?",
                  "items é atributo de classe (compartilhado), todas as instâncias enxergam o mesmo list.",
                  ["Nada de errado.",
                   "Perde-se o append por causa de GC.",
                   "Python proíbe atributo mutável de classe."],
                  "Atributos de classe são compartilhados. Para estado por instância, "
                  "inicialize em `__init__` (`self.items = []`)."),
                q("`@property` é apropriado quando...",
                  "Você precisa validar ou calcular dinamicamente um atributo.",
                  ["Quer trocar atributos públicos por getters/setters em todas as classes.",
                   "Quer otimizar acesso.",
                   "É obrigatório em Python 3.10+."],
                  "Property só vale quando há regra/validação/cálculo. Para campos "
                  "simples, atributo público é o jeito pythonic."),
                q("`@contextmanager` permite criar context manager via:",
                  "Função geradora com um único `yield`.",
                  ["Decorador automático em qualquer função.",
                   "Subclasse de ABC.",
                   "Não é mais usado, deprecou em 3.10."],
                  "A função tem o setup antes do yield, e o cleanup depois. Equivale a "
                  "uma classe com __enter__/__exit__."),
                q("Qual a diferença entre `except Exception as e` e `except:` (sem tipo)?",
                  "`except:` captura também BaseException (KeyboardInterrupt, SystemExit), o que é perigoso.",
                  ["Não há diferença prática.",
                   "`except:` é mais rápido.",
                   "Apenas o segundo funciona em 3.10+."],
                  "Bare `except:` é proibido pelo PEP 8. Sempre use `except Exception` "
                  "no mínimo."),
                q("`super().__init__(...)` em uma subclasse...",
                  "Chama o __init__ da classe pai.",
                  ["Sobrescreve o __init__ pai permanentemente.",
                   "É equivalente a `self.__init__()` direto.",
                   "Só funciona em herança simples."],
                  "Padrão para reusar inicialização do pai. Em herança múltipla, "
                  "super() segue o MRO (Method Resolution Order)."),
                q("Para um pedaço de código que SEMPRE deve rodar (limpeza), use:",
                  "finally:",
                  ["else:", "raise:", "pass:"],
                  "`finally:` executa com ou sem exceção, com ou sem `return`. É o "
                  "lugar de fechar conexões, soltar locks, remover arquivos temporários."),
            ],
        },
        # =====================================================================
        # 6.4 Manipulação de arquivos e CLI
        # =====================================================================
        {
            "title": "Manipulação de arquivos, paths e CLI",
            "summary": "pathlib moderno, leitura/escrita robusta, JSON/YAML/TOML e construção de ferramentas de linha de comando.",
            "lesson": {
                "intro": (
                    "Quase todo script DevOps começa lendo um arquivo (config, log, "
                    "inventário) e expõe alguma flag (<code>--dry-run</code>, "
                    "<code>--env=prod</code>). Esta aula cobre como fazer isso "
                    "<em>direito</em>: <code>pathlib</code> em vez de strings, "
                    "<code>argparse</code>/<code>typer</code> em vez de "
                    "<code>sys.argv[1]</code>, e parsing de JSON/YAML/TOML sem "
                    "armadilhas comuns."
                ),
                "body": (
                    "<h3>1. <code>pathlib</code>: o jeito moderno</h3>"
                    "<p>Esqueça <code>os.path.join</code>. Use <code>Path</code>:</p>"
                    "<pre><code>from pathlib import Path\n\n"
                    "root   = Path(\"/var/log\")\n"
                    "logfile = root / \"app\" / \"app.log\"        # operador / monta path\n"
                    "logfile.exists()\n"
                    "logfile.is_file()\n"
                    "logfile.parent                            # /var/log/app\n"
                    "logfile.suffix                            # '.log'\n"
                    "logfile.stem                              # 'app'\n"
                    "logfile.with_suffix(\".log.1\")             # rotação simples\n\n"
                    "# Iterar diretório\n"
                    "for log in Path(\"/var/log\").rglob(\"*.gz\"):\n"
                    "    print(log, log.stat().st_size)\n\n"
                    "# Ler/escrever em uma linha\n"
                    "txt = Path(\"config.toml\").read_text(encoding=\"utf-8\")\n"
                    "Path(\"out.json\").write_text(json.dumps(d, indent=2))</code></pre>"
                    "<p>Vantagens: tipo dedicado, métodos descobertos pelo IDE, "
                    "suporte a Windows e Linux nativo, encoding explícito.</p>"

                    "<h3>2. Lendo arquivos sem se queimar</h3>"
                    "<p>O grande inimigo é o <strong>encoding</strong>:</p>"
                    "<pre><code># EVITE: assume locale do sistema (pode ser ASCII em servidor)\n"
                    "open(\"file.txt\").read()\n\n"
                    "# CERTO: explicite encoding e modo\n"
                    "with open(\"file.txt\", encoding=\"utf-8\") as f:\n"
                    "    data = f.read()</code></pre>"
                    "<p>Para arquivos binários (imagens, gzip, parquet), use "
                    "<code>\"rb\"</code> e <em>não</em> defina encoding. "
                    "Para CSV use <code>csv.DictReader</code> em vez de "
                    "<code>line.split(\",\")</code>, vírgula dentro de aspas vai "
                    "estragar seu split.</p>"

                    "<h3>3. Configuração: JSON, YAML, TOML, .env</h3>"
                    "<pre><code># JSON, stdlib, sem dependência\n"
                    "import json\n"
                    "cfg = json.loads(Path(\"cfg.json\").read_text())\n"
                    "Path(\"out.json\").write_text(json.dumps(cfg, indent=2, sort_keys=True))\n\n"
                    "# TOML, leitura nativa em 3.11+\n"
                    "import tomllib\n"
                    "with open(\"pyproject.toml\", \"rb\") as f:\n"
                    "    pyproj = tomllib.load(f)\n\n"
                    "# YAML, pacote externo\n"
                    "import yaml          # pip install pyyaml\n"
                    "k = yaml.safe_load(Path(\"deploy.yaml\").read_text())\n\n"
                    "# .env, uso típico em containers\n"
                    "from dotenv import load_dotenv  # pip install python-dotenv\n"
                    "load_dotenv()\n"
                    "import os; secret = os.environ[\"DB_PASSWORD\"]</code></pre>"
                    "<p><strong>Importante</strong>: ao parsear YAML <em>sempre</em> use "
                    "<code>safe_load</code>; <code>load</code> permite construir objetos "
                    "Python arbitrários, vetor de RCE quando o YAML vem de fora.</p>"

                    "<h3>4. Argparse: a stdlib do CLI</h3>"
                    "<pre><code>import argparse\n"
                    "from pathlib import Path\n\n"
                    "def main() -&gt; int:\n"
                    "    p = argparse.ArgumentParser(prog=\"deploy\", description=\"Faz deploy.\")\n"
                    "    p.add_argument(\"image\", help=\"Imagem Docker, ex: web:1.2\")\n"
                    "    p.add_argument(\"--env\", choices=[\"dev\",\"stg\",\"prod\"], required=True)\n"
                    "    p.add_argument(\"--replicas\", type=int, default=3)\n"
                    "    p.add_argument(\"--config\", type=Path, default=Path(\"deploy.yaml\"))\n"
                    "    p.add_argument(\"--dry-run\", action=\"store_true\")\n"
                    "    p.add_argument(\"-v\", \"--verbose\", action=\"count\", default=0)\n"
                    "    args = p.parse_args()\n"
                    "    print(args)\n"
                    "    return 0\n\n"
                    "if __name__ == \"__main__\":\n"
                    "    raise SystemExit(main())</code></pre>"
                    "<p>Detalhes que evitam bug:</p>"
                    "<ul>"
                    "<li><code>type=Path</code> dá um objeto pronto.</li>"
                    "<li><code>choices=[...]</code> valida e gera mensagem de erro humana.</li>"
                    "<li><code>action=\"store_true\"</code> para flags booleanas.</li>"
                    "<li><code>action=\"count\"</code> para verbosidade (<code>-v</code>, "
                    "<code>-vv</code>...).</li>"
                    "<li>Subcomandos via <code>add_subparsers</code> (mesmo padrão de "
                    "<code>git commit</code>, <code>git push</code>).</li>"
                    "</ul>"

                    "<h3>5. <code>typer</code> e <code>click</code>: CLIs ergonômicos</h3>"
                    "<p>Para ferramentas que crescem, <code>typer</code> (que usa type "
                    "hints) escala melhor:</p>"
                    "<pre><code>import typer\n"
                    "app = typer.Typer()\n\n"
                    "@app.command()\n"
                    "def deploy(image: str, env: str = \"dev\", replicas: int = 3) -&gt; None:\n"
                    "    typer.echo(f\"Deploying {image} to {env} ×{replicas}\")\n\n"
                    "@app.command()\n"
                    "def rollback(version: int) -&gt; None:\n"
                    "    typer.echo(f\"Rolling back to {version}\")\n\n"
                    "if __name__ == \"__main__\":\n"
                    "    app()</code></pre>"

                    "<h3>6. Logs estruturados</h3>"
                    "<p>Use <code>logging</code> da stdlib em vez de <code>print()</code>:</p>"
                    "<pre><code>import logging\n\n"
                    "logging.basicConfig(\n"
                    "    level=logging.INFO,\n"
                    "    format=\"%(asctime)s %(levelname)s %(name)s :: %(message)s\",\n"
                    ")\n"
                    "log = logging.getLogger(\"deploy\")\n\n"
                    "log.info(\"deploying image=%s env=%s\", image, env)   # lazy interpolation\n"
                    "log.warning(\"replicas=%d acima do recomendado\", n)\n"
                    "log.error(\"falhou\", exc_info=True)                  # inclui traceback</code></pre>"
                    "<p>Em produção, troque o handler para emitir JSON "
                    "(<code>python-json-logger</code>), facilita ingestão em "
                    "Datadog/Loki/CloudWatch.</p>"

                    "<h3>7. Saída para stdout vs. stderr</h3>"
                    "<p>Convenção: <code>stdout</code> para o resultado do programa "
                    "(parsável); <code>stderr</code> para diagnóstico humano. Quem usa "
                    "seu CLI em pipeline depende disso:</p>"
                    "<pre><code>import sys\n"
                    "print(json.dumps(result))                # stdout\n"
                    "print(\"WARN: ...\", file=sys.stderr)      # stderr</code></pre>"

                    "<h3>8. Códigos de saída</h3>"
                    "<p>Convenção POSIX: 0 = sucesso, 1 = erro genérico, 2 = uso "
                    "incorreto. Documente os outros que você usar:</p>"
                    "<pre><code>def main() -&gt; int:\n"
                    "    try: do_work()\n"
                    "    except ConfigError: return 65   # data format error\n"
                    "    except NetworkError: return 69  # service unavailable\n"
                    "    return 0\n\n"
                    "if __name__ == \"__main__\":\n"
                    "    raise SystemExit(main())</code></pre>"
                ),
                "practical": (
                    "Crie um CLI <code>diskhog.py</code> que: (1) recebe via "
                    "<code>--root</code> um diretório (default <code>.</code>); "
                    "(2) tem flag <code>--top N</code> (default 10); (3) percorre "
                    "recursivamente com <code>Path.rglob('*')</code> e imprime os N maiores "
                    "arquivos com tamanho legível (KB/MB/GB); (4) usa <code>logging</code> "
                    "para mensagens de progresso em stderr; (5) sai com 0 normalmente, 2 "
                    "se o root não existe."
                ),
            },
            "materials": [
                m("Python docs, pathlib",
                  "https://docs.python.org/3/library/pathlib.html",
                  "docs", "API moderna de paths."),
                m("Python docs, argparse",
                  "https://docs.python.org/3/library/argparse.html",
                  "docs", "Construção de CLI com a stdlib."),
                m("Typer documentation",
                  "https://typer.tiangolo.com/",
                  "docs", "Framework CLI baseado em type hints."),
                m("Click documentation",
                  "https://click.palletsprojects.com/",
                  "docs", "Framework CLI mais antigo, muito maduro."),
                m("Real Python, logging",
                  "https://realpython.com/python-logging/",
                  "article", "Tutorial completo de logging."),
                m("Brett Cannon, Why YAML safe_load",
                  "https://snarky.ca/i-dont-understand-pyyaml-s-yaml-load-function/",
                  "article", "Por que `yaml.load` é perigoso."),
            ],
            "questions": [
                q("Como combinar dois paths de forma portátil em Python moderno?",
                  "Path('/var/log') / 'app.log'",
                  ["'/var/log' + '/' + 'app.log'",
                   "os.path.concat(...)",
                   "string.format('/var/log/{}', 'app.log')"],
                  "pathlib usa o operador `/` para concatenar partes. Funciona em "
                  "Linux/Mac/Windows."),
                q("Qual o risco de `yaml.load(user_input)`?",
                  "Permite executar código Python arbitrário (RCE).",
                  ["Não suporta unicode.",
                   "É lento para arquivos grandes.",
                   "Não funciona em 3.11."],
                  "yaml.load aceita tags `!!python/object` que instanciam classes, "
                  "vetor de RCE. Sempre use `yaml.safe_load`."),
                q("Para parsear pyproject.toml na stdlib (3.11+), use:",
                  "tomllib",
                  ["tomli (sempre)", "configparser", "json"],
                  "tomllib é a stdlib a partir do 3.11. Para versões anteriores use "
                  "tomli (mesma API)."),
                q("Em argparse, `action='store_true'` é usado para...",
                  "Flags booleanas (--verbose ⇒ args.verbose = True).",
                  ["Armazenar a string 'true'.",
                   "Forçar argumento obrigatório.",
                   "É equivalente a default=True."],
                  "Sem o flag → False; com o flag → True. Mais natural que --verbose=true."),
                q("Por que separar saída em stdout vs stderr em um CLI?",
                  "Para que pipelines possam capturar só o resultado (stdout), enquanto diagnóstico vai para stderr.",
                  ["É só estético.",
                   "stderr é mais rápido.",
                   "stdout não suporta UTF-8."],
                  "Convenção POSIX. Permite `meu-cli | jq ...` sem misturar logs."),
                q("Por que evitar `open(p).read()` direto, sem context manager?",
                  "O arquivo pode não ser fechado se o GC demorar, em servidores de longa vida vaza descritores.",
                  ["É erro de sintaxe.",
                   "É mais lento.",
                   "Funciona só em Windows."],
                  "Sem `with`, dependemos do GC para chamar __del__ que fecha o arquivo. "
                  "Em CPython funciona quase sempre, mas não é portável e em PyPy demora."),
                q("Qual destes é o nível mais detalhado em logging padrão?",
                  "DEBUG",
                  ["INFO", "TRACE", "VERBOSE"],
                  "Níveis: DEBUG < INFO < WARNING < ERROR < CRITICAL. TRACE/VERBOSE "
                  "não existem nativamente."),
                q("Forma idiomática de receber um caminho via CLI já tipado:",
                  "p.add_argument('--config', type=Path)",
                  ["p.add_argument('--config', type=str)",
                   "p.add_argument('--config', type='path')",
                   "p.add_argument('--config'); Path(args.config)"],
                  "argparse converte para Path automaticamente; mais limpo que converter "
                  "depois."),
                q("Para encerrar com código de saída 2 a partir de main():",
                  "return 2 (e usar SystemExit(main()) no entry point)",
                  ["sys.exit('2')",
                   "raise Exit(2)",
                   "os.exit(2)"],
                  "Padrão idiomático: `def main() -> int: ...; raise SystemExit(main())`. "
                  "Evita `sys.exit` espalhado e facilita testar a função main()."),
                q("Para iterar recursivamente em todos os arquivos *.py de um diretório:",
                  "Path('.').rglob('*.py')",
                  ["os.walk('.', filter='*.py')",
                   "Path('.').glob('*.py')",
                   "shutil.find('*.py')"],
                  "rglob faz busca recursiva; glob só procura no diretório atual."),
            ],
        },
        # =====================================================================
        # 6.5 HTTP, APIs e SDKs
        # =====================================================================
        {
            "title": "HTTP, APIs REST e SDKs",
            "summary": "requests/httpx, autenticação, retry com backoff, paginação, JSON e clientes de cloud.",
            "lesson": {
                "intro": (
                    "Boa parte de DevOps é cola entre APIs: GitHub, GitLab, Slack, PagerDuty, "
                    "Cloudflare, Vault, Vercel, AWS, GCP. Saber consumir HTTP "
                    "<em>profissionalmente</em>, com timeout, retry, autenticação correta e "
                    "manejo de paginação, separa script frágil de ferramenta confiável."
                ),
                "body": (
                """<h3>1. `requests`: por que timeout e `raise_for_status` não são opcionais</h3>
<pre><code>import requests

r = requests.get(
    "https://api.github.com/repos/python/cpython",
    headers={"User-Agent": "my-tool/1.0", "Accept": "application/vnd.github+json"},
    timeout=(3.05, 10),  # (connect, read), SEMPRE
)
r.raise_for_status()
data = r.json()
print(data["stargazers_count"])</code></pre>
<p>Sem <code>timeout</code>, o socket TCP fica aberto até o sistema
operacional decidir encerrá-lo — que em muitos ambientes é <em>nunca</em>
(sem keepalive configurado, pode ficar pendurado por horas). Um script de
deploy que trava numa chamada HTTP sem timeout não falha visivelmente: ele
simplesmente para, e quem está olhando o pipeline vê "rodando" indefinidamente,
sem log de erro nenhum — o pior tipo de falha para diagnosticar, porque nada
"quebrou". O par <code>(connect, read)</code> existe porque são duas etapas
distintas: o tempo para abrir a conexão costuma ser curto e estável; o tempo
para o servidor responder pode legitimamente ser mais longo (uma API lenta
processando), então vale limites diferentes.</p>
<p><code>raise_for_status()</code> resolve um problema sutil: <code>requests</code>
não levanta exceção sozinho quando a API responde 404 ou 500 — ela devolve
um objeto <code>Response</code> normal, e cabe a você checar
<code>r.status_code</code>. Sem essa chamada, um código que faz
<code>data = r.json()</code> direto processa o corpo de um erro 500 (que
pode nem ser JSON válido, ou ser um JSON de formato de erro totalmente
diferente do esperado) como se fosse a resposta de sucesso — e o bug só
aparece muito depois, num <code>KeyError</code> confuso longe de onde o
problema de verdade está.</p>

<h3>2. `Session`: reaproveitando a conexão, não só os headers</h3>
<pre><code>s = requests.Session()
s.headers.update({"User-Agent": "my-tool/1.0",
                  "Authorization": f"Bearer {token}"})

for repo in repos:
    r = s.get(f"https://api.github.com/repos/{repo}", timeout=10)
    r.raise_for_status()</code></pre>
<p>O ganho de usar <code>Session</code> em vez de <code>requests.get()</code>
solto não é só evitar repetir headers: cada chamada de <code>requests.get()</code>
sem sessão abre uma conexão TCP nova e, se for HTTPS, refaz o handshake TLS
inteiro — dois ou três round-trips extras de rede <em>por chamada</em>. Numa
sessão, a conexão fica no pool e é reaproveitada entre requisições ao mesmo
host. Em um script que faz 100 chamadas à mesma API, a diferença entre
sessão e chamadas soltas costuma ser a diferença entre segundos e minutos.</p>

<h3>3. Retry com backoff: só para falhas que valem repetir</h3>
<p>Erros transitórios (502, 503, 504, timeout de rede) tendem a se resolver
sozinhos numa nova tentativa — o servidor estava sobrecarregado por um
instante, não quebrado. Configurar isso no nível de transporte, não em
laços manuais, garante que a lógica de retry se aplique a toda chamada da
sessão de forma consistente:</p>
<pre><code>from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"],
)
adapter = HTTPAdapter(max_retries=retry)
s.mount("https://", adapter)
s.mount("http://", adapter)</code></pre>
<p><code>backoff_factor</code> cresce exponencialmente entre tentativas
(0.5s, 1s, 2s, 4s...) — sem esse espaçamento crescente, um retry imediato
repetido contra um serviço já sobrecarregado piora a sobrecarga em vez de
esperar ela passar, um efeito conhecido como <em>thundering herd</em>. O
detalhe perigoso fica em <code>allowed_methods</code> incluir
<code>"POST"</code>: repetir automaticamente um POST que NÃO é idempotente
(criar um recurso, disparar um pagamento) pode duplicar o efeito colateral
se a primeira tentativa teve sucesso no servidor mas a resposta se perdeu
no caminho de volta. Só inclua POST no retry se a API suportar uma
<code>Idempotency-Key</code> que deduplique no lado do servidor.</p>

<h3>4. Autenticação: Basic, Bearer, mTLS — e onde o token NUNCA vai</h3>
<pre><code># Bearer (mais comum em APIs modernas)
headers = {"Authorization": f"Bearer {token}"}

# Basic (legacy)
from requests.auth import HTTPBasicAuth
r = requests.get(url, auth=HTTPBasicAuth(user, password))

# mTLS, certificado de cliente
r = requests.get(url, cert=("client.crt", "client.key"), verify="ca.pem")</code></pre>
<p>Bearer token é hoje o padrão porque é <em>opaco</em> para quem o carrega
— o cliente não sabe nem precisa saber o que há dentro, só o repassa. Basic
Auth vai usuário e senha em texto (só protegido pelo TLS do transporte, não
por si só) a cada requisição, o que aumenta a superfície de exposição se um
proxy no meio do caminho logar headers. mTLS inverte quem prova identidade:
em vez do cliente provar quem é, o SERVIDOR também exige provar a dele — útil
entre serviços internos onde ambos os lados precisam confiar um no outro,
não só o cliente confiar no servidor.</p>
<p>Tokens nunca vão em código-fonte, nem "só por enquanto", nem em
variável hardcoded que você promete remover depois — vão para variável de
ambiente injetada em runtime, ou um secret manager (AWS Secrets Manager, GCP
Secret Manager, Vault). O motivo prático: qualquer coisa commitada no git
continua acessível pelo histórico mesmo depois de "removida" num commit
seguinte — rotacionar a credencial exposta é a única correção real.</p>

<h3>5. Paginação: por que ignorá-la corrompe dados silenciosamente</h3>
<p>Quase toda API real que lista recursos limita quantos devolve por
chamada — geralmente entre 20 e 100. Ignorar isso não dá erro: você recebe
uma resposta 200 válida com a primeira página, e o script segue achando que
processou "todos os repositórios" quando processou só os 30 primeiros. Os
três padrões mais comuns:</p>
<ul>
<li><strong>Page/per_page</strong>: <code>?page=2&per_page=100</code> — simples,
mas pode pular ou repetir itens se a lista mudar entre uma página e
outra.</li>
<li><strong>Cursor</strong>: a resposta traz um <code>next_cursor</code>
opaco que você repassa na próxima chamada — estável mesmo com a lista
mudando, porque o cursor marca uma posição real, não um número de página
recalculado.</li>
<li><strong>Link header</strong>: GitHub e outras APIs HTTP "puras" usam
<code>Link: &lt;...&gt;; rel="next"</code> no cabeçalho da resposta, em vez
de um campo no corpo JSON.</li>
</ul>
<pre><code>def all_repos(org: str):
    url = f"https://api.github.com/orgs/{org}/repos"
    while url:
        r = s.get(url, params={"per_page": 100}, timeout=10)
        r.raise_for_status()
        yield from r.json()
        url = r.links.get("next", {}).get("url")</code></pre>
<p>Usar <code>yield</code> em vez de acumular tudo numa lista antes de
devolver mantém memória constante mesmo com dezenas de milhares de itens —
o chamador processa item a item conforme cada página chega, sem nunca
segurar a coleção inteira na RAM de uma vez.</p>

<h3>6. `httpx`: o mesmo modelo, com concorrência real</h3>
<p><code>httpx</code> tem API quase idêntica à do <code>requests</code>
(a migração costuma ser trocar o import), mas resolve uma limitação
estrutural: <code>requests</code> é síncrono por dentro, então consultar 50
endpoints significa esperar cada resposta chegar antes de disparar a
próxima. <code>httpx</code> suporta <code>async</code>, permitindo disparar
todas as chamadas de uma vez e aguardar juntas:</p>
<pre><code>import httpx

async with httpx.AsyncClient(timeout=10.0) as client:
    tasks = [client.get(u) for u in urls]
    responses = await asyncio.gather(*tasks)
    for r in responses:
        r.raise_for_status()</code></pre>
<p>Para I/O de rede (que passa a maior parte do tempo esperando, não
processando), esse padrão de fan-out concorrente costuma reduzir o tempo
total de "soma de todas as latências" para "a latência da mais lenta" — a
diferença entre minutos e segundos ao consultar dezenas de serviços.</p>

<h3>7. Construindo APIs com FastAPI: tipos como contrato, não decoração</h3>
<pre><code>from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Deploy(BaseModel):
    image: str
    env:   str
    replicas: int = 3

@app.post("/deploy")
def deploy(body: Deploy):
    if body.replicas &gt; 100:
        raise HTTPException(400, "replicas demais")
    return {"status": "queued", "id": "d-123"}</code></pre>
<p>A diferença de FastAPI para escrever um handler HTTP cru é que as type
hints da classe <code>Deploy</code> não são só documentação para humanos:
o Pydantic as usa em runtime para VALIDAR o corpo da requisição antes do
seu código rodar — um POST sem o campo <code>image</code>, ou com
<code>replicas</code> como string não-numérica, é rejeitado automaticamente
com um 422 detalhado, sem você escrever nenhuma checagem manual. As mesmas
anotações geram a documentação OpenAPI navegável em <code>/docs</code>. Para
ferramentas internas (um endpoint que aciona um deploy, por exemplo), isso
elimina uma classe inteira de bugs de "esqueci de validar um campo".</p>

<h3>8. Webhooks: por que comparar assinaturas com `==` é uma falha de segurança</h3>
<pre><code>import hmac, hashlib

def verify_github(payload: bytes, signature: str, secret: str) -&gt; bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)</code></pre>
<p>Um webhook é uma API invertida: em vez de você chamar o serviço externo,
ele chama VOCÊ — e como o endpoint precisa ficar público na internet para
recebê-lo, qualquer um pode mandar uma requisição fingindo ser o GitHub.
A assinatura HMAC no cabeçalho prova que o corpo veio de quem tem o
segredo compartilhado, calculando um hash sobre o payload e comparando com
o que o remetente enviou.</p>
<p>O detalhe que faz essa comparação valer a pena está em
<code>hmac.compare_digest</code> em vez de um simples <code>==</code>:
comparação de string comum no Python para no primeiro caractere diferente,
então o TEMPO que a comparação leva vaza informação sobre quantos
caracteres do início já batem — um atacante pode, byte a byte, medir
minúsculas diferenças de latência e reconstruir a assinatura válida sem
nunca precisar quebrar o hash em si. <code>compare_digest</code> sempre
compara em tempo constante, independente de quantos caracteres coincidem.</p>"""
                ),
                "practical": (
                    "Implemente <code>gh_repos.py</code> que: (1) lê o token GitHub de "
                    "<code>os.environ['GITHUB_TOKEN']</code>; (2) usa <code>Session</code> "
                    "com retry configurado; (3) lista TODOS os repositórios de uma "
                    "organização (paginação por Link header); (4) imprime nome, stars, "
                    "última atualização em CSV no stdout; (5) gerencia rate limit lendo "
                    "o header <code>X-RateLimit-Remaining</code> e dormindo se passar "
                    "abaixo de 100."
                ),
            },
            "materials": [
                m("requests, quickstart",
                  "https://requests.readthedocs.io/en/latest/user/quickstart/",
                  "docs", "Documentação oficial do requests."),
                m("httpx documentation",
                  "https://www.python-httpx.org/",
                  "docs", "Cliente HTTP/2 sync e async."),
                m("urllib3 Retry",
                  "https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry",
                  "docs", "Configuração de retry."),
                m("FastAPI tutorial",
                  "https://fastapi.tiangolo.com/tutorial/",
                  "docs", "Construindo APIs com FastAPI."),
                m("REST API Design, Microsoft Guidelines",
                  "https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md",
                  "docs", "Boas práticas de design REST."),
                m("Stripe, API best practices (idempotency)",
                  "https://stripe.com/docs/api/idempotent_requests",
                  "docs", "Como Stripe evita duplicações em retries."),
            ],
            "questions": [
                q("Por que `requests.get(url)` sem timeout é perigoso em produção?",
                  "A chamada pode travar indefinidamente se o servidor não responder.",
                  ["É mais lento que com timeout.",
                   "Causa erro de sintaxe em 3.11+.",
                   "Não suporta HTTPS."],
                  "Sem timeout, uma conexão problemática pode travar o programa para "
                  "sempre. Sempre defina (connect_timeout, read_timeout)."),
                q("`raise_for_status()` faz o quê?",
                  "Lança HTTPError se o status code for 4xx ou 5xx.",
                  ["Sempre lança um erro.",
                   "Imprime o status na tela.",
                   "Reenvia a request."],
                  "É a forma idiomática de tratar erros HTTP. Sem ela, você processa "
                  "respostas de erro como se fossem sucesso."),
                q("Para retry de erros transitórios (5xx), você deveria configurar...",
                  "urllib3.Retry com backoff_factor e status_forcelist.",
                  ["Loop while True com sleep manual.",
                   "Threading com try/except.",
                   "Não fazer retry, sempre falha rápido."],
                  "Retry com backoff exponencial é o padrão. Loop manual sem jitter "
                  "pode causar thundering herd."),
                q("Por que usar `requests.Session` em vez de chamadas avulsas?",
                  "Reusa conexões TCP/TLS (connection pooling), reduzindo latência.",
                  ["Funciona offline.",
                   "Persiste cookies por 24h.",
                   "É exigido a partir de 3.10."],
                  "Em scripts com várias chamadas ao mesmo host, Session evita "
                  "handshake TLS repetido."),
                q("Para verificar uma assinatura HMAC de webhook com segurança:",
                  "hmac.compare_digest(esperado, recebido)",
                  ["esperado == recebido",
                   "esperado in recebido",
                   "str(esperado).startswith(recebido)"],
                  "compare_digest é constant-time: não vaza informação por timing. "
                  "`==` para de comparar no primeiro byte diferente."),
                q("Em paginação por Link header (estilo GitHub), o atributo `r.links['next']['url']` retorna...",
                  "A URL completa da próxima página.",
                  ["Apenas o número da página.",
                   "O total de páginas.",
                   "Um booleano indicando se há próxima."],
                  "requests parseia o Link header automaticamente em dict, basta "
                  "checar 'next'."),
                q("Token de API em código-fonte é problema porque...",
                  "Vai parar no git e em logs; rotação fica difícil; quem tem acesso ao repo tem o token.",
                  ["É só estética.",
                   "Causa falha em servidores Linux.",
                   "Reduz performance."],
                  "Tokens devem vir de env, secret manager ou keyring. Se vazar, "
                  "rotacione imediatamente."),
                q("`httpx.AsyncClient` é particularmente útil quando...",
                  "Você precisa fazer várias requisições em paralelo (fan-out).",
                  ["Tem só uma requisição.",
                   "Quer evitar HTTPS.",
                   "Está em Python 2."],
                  "Async + gather permite N requisições simultâneas com baixa overhead. "
                  "Síncrono seria sequencial."),
                q("Para autenticação Bearer Token, o header correto é:",
                  "Authorization: Bearer <token>",
                  ["X-Bearer: <token>",
                   "Cookie: token=<token>",
                   "Auth: <token>"],
                  "Padrão RFC 6750. Sempre o esquema explícito antes do token."),
                q("Vale a pena usar `r.json()` se o status for 500?",
                  "Não, chame raise_for_status() primeiro; senão pode parsear body de erro como dado válido.",
                  ["Sempre vale.",
                   "Apenas em produção.",
                   "Só em chamadas internas."],
                  "5xx geralmente vêm com body em texto/HTML, parsear como JSON gera "
                  "erro confuso. raise_for_status interrompe antes."),
            ],
        },
        # =====================================================================
        # 6.6 Automação de sistema
        # =====================================================================
        {
            "title": "Automação de sistema com Python",
            "summary": "subprocess seguro, manipulação de processos, ssh remoto, integrações com shell e Ansible.",
            "lesson": {
                "intro": (
                    "Python brilha como cola entre comandos do sistema, chamando "
                    "<code>kubectl</code>, <code>terraform</code>, <code>aws</code>, "
                    "<code>git</code>... O perigo é fazer isso ingenuamente: "
                    "<code>os.system(\"rm \" + user_input)</code> é uma das classes "
                    "clássicas de injeção. Esta aula mostra como automatizar comandos com "
                    "segurança, lendo saída em tempo real e tratando erros corretamente."
                ),
                "body": (
                    "<h3>1. <code>subprocess.run</code>: o jeito moderno</h3>"
                    "<pre><code>import subprocess\n\n"
                    "result = subprocess.run(\n"
                    "    [\"kubectl\", \"get\", \"pods\", \"-n\", namespace, \"-o\", \"json\"],\n"
                    "    capture_output=True,\n"
                    "    text=True,        # decodifica como str (utf-8 default)\n"
                    "    timeout=30,\n"
                    "    check=True,       # raise CalledProcessError se exit != 0\n"
                    ")\n"
                    "data = json.loads(result.stdout)</code></pre>"
                    "<p>Detalhes que importam:</p>"
                    "<ul>"
                    "<li><strong>Lista, não string</strong>: <code>[\"ls\", \"-l\", path]</code> "
                    "evita que <code>path = \"; rm -rf /\"</code> vire injeção. "
                    "<code>shell=True</code> só com input controlado.</li>"
                    "<li><strong>timeout</strong>: igual em HTTP, comandos podem travar "
                    "(rede lenta, prompt esperando input).</li>"
                    "<li><strong>check=True</strong>: sem isso, exit code != 0 passa "
                    "despercebido.</li>"
                    "<li><strong>text=True</strong>: dá <code>str</code> em vez de "
                    "<code>bytes</code>; com <code>encoding=</code> para casos "
                    "específicos.</li>"
                    "</ul>"

                    "<h3>2. Streaming de saída em tempo real</h3>"
                    "<p>Para processos longos (terraform apply, build), você quer ver "
                    "logs enquanto rodam, não esperar terminar:</p>"
                    "<pre><code>p = subprocess.Popen(\n"
                    "    [\"terraform\", \"apply\", \"-auto-approve\"],\n"
                    "    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,\n"
                    ")\n"
                    "for line in p.stdout:\n"
                    "    print(line, end=\"\")          # mostra na hora\n"
                    "    log_file.write(line)\n"
                    "rc = p.wait(timeout=3600)\n"
                    "if rc != 0:\n"
                    "    raise SystemExit(rc)</code></pre>"

                    "<h3>3. Variáveis de ambiente para subprocessos</h3>"
                    "<pre><code>env = os.environ.copy()       # NUNCA passe os.environ direto e mute\n"
                    "env[\"KUBECONFIG\"] = \"/etc/k8s/prod.kubeconfig\"\n"
                    "env[\"AWS_PROFILE\"] = \"prod\"\n"
                    "subprocess.run([\"kubectl\", \"get\", \"ns\"], env=env, check=True)</code></pre>"
                    "<p>Cuidado: redirigir <code>env=</code> remove TUDO que não está "
                    "no dict. Comece com <code>os.environ.copy()</code> e modifique.</p>"

                    "<h3>4. <code>shell=True</code>: quando e como</h3>"
                    "<p>Útil para usar pipes ou redirecionamento <em>nativo</em>:</p>"
                    "<pre><code>cmd = \"ps aux | grep nginx | wc -l\"\n"
                    "subprocess.run(cmd, shell=True, check=True)</code></pre>"
                    "<p>Risco: se a string tiver entrada do usuário, é injeção. "
                    "Alternativa segura para pipes:</p>"
                    "<pre><code>p1 = subprocess.Popen([\"ps\", \"aux\"], stdout=subprocess.PIPE)\n"
                    "p2 = subprocess.Popen([\"grep\", \"nginx\"], stdin=p1.stdout, stdout=subprocess.PIPE)\n"
                    "p1.stdout.close()\n"
                    "out = p2.communicate()[0]</code></pre>"
                    "<p>Ou use <code>shlex.quote</code> para escapar quando shell=True "
                    "for inevitável:</p>"
                    "<pre><code>import shlex\n"
                    "subprocess.run(f\"ls {shlex.quote(user_path)}\", shell=True)</code></pre>"

                    "<h3>5. Operações de filesystem (<code>shutil</code>, <code>os</code>)</h3>"
                    "<pre><code>import shutil, os\n\n"
                    "shutil.copy2(src, dst)            # mantém metadata\n"
                    "shutil.copytree(src, dst)         # recursivo\n"
                    "shutil.rmtree(path, ignore_errors=False)\n"
                    "shutil.move(src, dst)             # atômico no MESMO FS\n"
                    "shutil.disk_usage(\"/\")            # (total, used, free) bytes\n"
                    "shutil.which(\"terraform\")         # localiza binário no PATH\n\n"
                    "os.replace(src, dst)              # move atômico\n"
                    "os.path.expanduser(\"~/.kube/config\")\n"
                    "os.environ.get(\"HOME\", \"/root\")</code></pre>"

                    "<h3>6. Tempfiles seguros</h3>"
                    "<pre><code>import tempfile\n\n"
                    "# arquivo temporário\n"
                    "with tempfile.NamedTemporaryFile(\"w\", suffix=\".yaml\", delete=False) as f:\n"
                    "    f.write(yaml_content)\n"
                    "    tmp_path = f.name\n"
                    "try:\n"
                    "    subprocess.run([\"kubectl\", \"apply\", \"-f\", tmp_path], check=True)\n"
                    "finally:\n"
                    "    Path(tmp_path).unlink(missing_ok=True)\n\n"
                    "# diretório temporário (cleanup automático)\n"
                    "with tempfile.TemporaryDirectory() as d:\n"
                    "    Path(d, \"file.txt\").write_text(\"oi\")\n"
                    "    # diretório removido ao sair</code></pre>"

                    "<h3>7. SSH remoto e Fabric</h3>"
                    "<pre><code>from fabric import Connection   # pip install fabric\n\n"
                    "with Connection(\"deploy@10.0.1.5\", connect_kwargs={\"key_filename\": \"~/.ssh/id_ed25519\"}) as c:\n"
                    "    r = c.run(\"systemctl status nginx\", warn=True)\n"
                    "    if r.return_code != 0:\n"
                    "        c.sudo(\"systemctl restart nginx\")\n"
                    "    c.put(\"./nginx.conf\", \"/etc/nginx/conf.d/app.conf\")\n"
                    "    c.run(\"nginx -t && systemctl reload nginx\")</code></pre>"
                    "<p>Para inventários grandes, <strong>Ansible</strong> sempre será "
                    "melhor que script Python, mas Fabric vale para tarefas pontuais.</p>"

                    "<h3>8. Tratamento de sinais</h3>"
                    "<p>Em ferramentas longas, capture <code>SIGINT</code>/<code>SIGTERM</code> "
                    "para fazer cleanup:</p>"
                    "<pre><code>import signal\n\n"
                    "shutdown = False\n"
                    "def _handle(sig, frame):\n"
                    "    global shutdown; shutdown = True\n\n"
                    "signal.signal(signal.SIGTERM, _handle)\n"
                    "signal.signal(signal.SIGINT,  _handle)\n\n"
                    "while not shutdown:\n"
                    "    do_iteration()\n"
                    "cleanup()</code></pre>"

                    "<h3>9. Boas práticas para scripts em produção</h3>"
                    "<ul>"
                    "<li>Sempre <code>check=True</code>, sempre <code>timeout</code>.</li>"
                    "<li>Nunca <code>shell=True</code> com input do usuário não escapado.</li>"
                    "<li>Logue o comando exato (com <code>shlex.join</code>) antes de executar.</li>"
                    "<li>Para retry, use lib (tenacity), não escreva o seu.</li>"
                    "<li>Defina <code>cwd=</code> explicitamente quando relevante.</li>"
                    "<li>Não dependa de <code>$PATH</code> em produção: use caminho "
                    "absoluto (<code>/usr/local/bin/kubectl</code>) ou "
                    "<code>shutil.which</code>.</li>"
                    "</ul>"
                ),
                "practical": (
                    "Crie <code>backup_db.py</code> que: (1) executa "
                    "<code>pg_dump</code> com timeout de 5 min, capturando saída; (2) gera "
                    "arquivo em <code>/tmp/&lt;db&gt;-&lt;data&gt;.sql.gz</code> usando "
                    "<code>gzip</code>; (3) sobe para S3 via <code>aws s3 cp</code> "
                    "(também via subprocess); (4) limpa o arquivo local em "
                    "<code>finally</code>; (5) registra no log: comando exato (escapado), "
                    "duração e status."
                ),
            },
            "materials": [
                m("Python docs, subprocess",
                  "https://docs.python.org/3/library/subprocess.html",
                  "docs", "Referência completa de subprocess."),
                m("Real Python, subprocess",
                  "https://realpython.com/python-subprocess/",
                  "article", "Tutorial com exemplos práticos."),
                m("shutil, alto nível para arquivos",
                  "https://docs.python.org/3/library/shutil.html",
                  "docs", "Cópias, moves, espaço em disco."),
                m("Fabric documentation",
                  "https://www.fabfile.org/",
                  "docs", "Automação SSH em Python."),
                m("Paramiko, SSH puro Python",
                  "https://www.paramiko.org/",
                  "docs", "Lib subjacente ao Fabric."),
                m("Tenacity, retry library",
                  "https://tenacity.readthedocs.io/",
                  "docs", "Decoradores de retry com backoff."),
            ],
            "questions": [
                q("Por que `subprocess.run([\"rm\", path])` é mais seguro que `os.system(f\"rm {path}\")`?",
                  "Argumentos em lista são passados direto ao processo, sem interpretação de shell, evitando injeção.",
                  ["É só mais rápido.",
                   "subprocess sempre captura a saída.",
                   "os.system não existe mais."],
                  "Lista evita interpretação de espaços, `;`, `|`, `$()`. Vetor clássico "
                  "de injeção desaparece."),
                q("Para garantir que `subprocess.run` falhe se o exit code não for 0:",
                  "Passe `check=True`.",
                  ["Verifique manualmente result.returncode (sempre).",
                   "Use stderr=PIPE.",
                   "Não há jeito direto."],
                  "check=True levanta CalledProcessError automaticamente. Manual também "
                  "funciona, mas é fácil esquecer."),
                q("`shell=True` é arriscado quando...",
                  "A string contém input não escapado vindo de fora (usuário, arquivo, rede).",
                  ["Sempre.",
                   "Apenas em Windows.",
                   "Apenas se houver pipe."],
                  "shell=True interpreta metacaracteres do shell. Se um deles vier do "
                  "usuário, é RCE. Use lista de args ou shlex.quote."),
                q("Para mostrar saída de um processo longo enquanto ele roda, use:",
                  "subprocess.Popen com stdout=PIPE e iterar p.stdout linha a linha.",
                  ["subprocess.run com capture_output (que só retorna no fim).",
                   "os.system (mostra na hora).",
                   "subprocess.check_output."],
                  "run/check_output bloqueiam até o fim. Popen + iter dá streaming "
                  "em tempo real."),
                q("Ao definir env= em subprocess, qual erro é comum?",
                  "Esquecer de copiar os.environ, o subprocesso fica sem PATH e variáveis essenciais.",
                  ["Não é possível passar env.",
                   "Sempre quebra HOME.",
                   "Causa segfault."],
                  "Comece com `env = os.environ.copy()` e adicione/sobrescreva. Senão "
                  "perde PATH, HOME, USER, etc."),
                q("Para criar arquivo temporário que será removido automaticamente:",
                  "with tempfile.NamedTemporaryFile() as f: ... (delete=True default)",
                  ["open(\"/tmp/\" + str(uuid4()), \"w\")",
                   "tempfile.mktemp() (deprecado, race condition).",
                   "shutil.create_temp()"],
                  "NamedTemporaryFile remove ao sair do `with` (delete=True default). "
                  "mktemp é race-condition vulnerable."),
                q("`shutil.move(src, dst)` em FS diferentes...",
                  "Cai para copiar+remover (não é atômico).",
                  ["É sempre atômico.",
                   "Falha sempre.",
                   "Usa pipe interno."],
                  "Em FS diferentes, copia e depois remove. Atômico só dentro do mesmo "
                  "FS via rename(2)."),
                q("Para localizar um binário no PATH:",
                  "shutil.which('kubectl')",
                  ["which.find('kubectl')",
                   "os.locate('kubectl')",
                   "Path.find('kubectl')"],
                  "shutil.which retorna o caminho absoluto ou None. Útil pra checar "
                  "dependências antes de chamar."),
                q("`signal.signal(SIGTERM, handler)` é útil para...",
                  "Interceptar pedido de parada e fazer cleanup gracioso (fechar arquivos, drenar fila).",
                  ["Aumentar a prioridade do processo.",
                   "Forçar reboot.",
                   "Detectar erros de programa."],
                  "Workers/daemons precisam disso para shutdown limpo. SIGKILL não pode "
                  "ser interceptado, só SIGTERM/SIGINT."),
                q("Para escapar uma string que VAI para shell=True com segurança:",
                  "shlex.quote(s)",
                  ["s.replace(\"'\", \"\\\\'\")",
                   "f\"'{s}'\" (aspas simples)",
                   "Não há forma segura."],
                  "shlex.quote escapa corretamente em todos os casos. Concatenação "
                  "manual sempre tem casos extremos."),
            ],
        },
        # =====================================================================
        # 6.7 Concorrência: threads, async, multiprocessing
        # =====================================================================
        {
            "title": "Concorrência: threads, asyncio e multiprocessing",
            "summary": "GIL, quando usar cada modelo, async/await na prática e armadilhas comuns.",
            "lesson": {
                "intro": (
                    "Python tem três modelos de concorrência, e a escolha errada faz "
                    "código <em>mais lento</em> que o serial. Esta aula explica o GIL, "
                    "quando threads ajudam, quando você precisa de processos e por que "
                    "<code>asyncio</code> tomou o mundo de I/O em rede."
                ),
                "body": (
                    "<h3>1. O GIL em uma frase</h3>"
                    "<p>O <strong>Global Interpreter Lock</strong> é um lock no "
                    "interpretador CPython que garante que apenas <em>uma</em> thread "
                    "Python execute bytecode por vez. Consequências:</p>"
                    "<ul>"
                    "<li><strong>CPU-bound (cálculo puro)</strong>: threads NÃO ajudam. "
                    "Use <code>multiprocessing</code> ou bibliotecas em C que liberam o "
                    "GIL (numpy, polars).</li>"
                    "<li><strong>I/O-bound (rede, disco)</strong>: threads e asyncio "
                    "ajudam, durante I/O o GIL é liberado.</li>"
                    "</ul>"
                    "<p>Em Python 3.13 começou a aparecer <strong>free-threading</strong> "
                    "(no-GIL builds), mas para 99% dos times ainda é experimental.</p>"

                    "<h3>2. Threads para I/O</h3>"
                    "<pre><code>from concurrent.futures import ThreadPoolExecutor\n\n"
                    "def fetch(url: str) -&gt; tuple[str, int]:\n"
                    "    r = requests.get(url, timeout=10)\n"
                    "    return url, r.status_code\n\n"
                    "with ThreadPoolExecutor(max_workers=20) as pool:\n"
                    "    for url, status in pool.map(fetch, urls):\n"
                    "        print(url, status)</code></pre>"
                    "<p><code>ThreadPoolExecutor</code> é a forma idiomática, esquece "
                    "<code>threading.Thread</code> direto. Para 50 chamadas HTTP em "
                    "paralelo dá ganho enorme em relação a sequencial.</p>"

                    "<h3>3. <code>asyncio</code>: cooperative multitasking</h3>"
                    "<p>Em vez de threads, uma única thread alterna entre tarefas em "
                    "pontos de espera (<code>await</code>):</p>"
                    "<pre><code>import asyncio, httpx\n\n"
                    "async def fetch(client: httpx.AsyncClient, url: str) -&gt; int:\n"
                    "    r = await client.get(url, timeout=10)\n"
                    "    return r.status_code\n\n"
                    "async def main():\n"
                    "    async with httpx.AsyncClient() as client:\n"
                    "        async with asyncio.TaskGroup() as tg:    # 3.11+\n"
                    "            tasks = [tg.create_task(fetch(client, u)) for u in urls]\n"
                    "        for t in tasks:\n"
                    "            print(t.result())\n\n"
                    "asyncio.run(main())</code></pre>"
                    "<p>Vantagens sobre threads: menos overhead (10000 tarefas viáveis), "
                    "estado compartilhado é seguro (sem race), API mais clara. "
                    "Desvantagem: precisa lib async em todo lugar, chamar função "
                    "síncrona bloqueante 'congela' o event loop.</p>"

                    "<h3>4. <code>asyncio</code>: padrões essenciais</h3>"
                    "<pre><code># gather: aguarda várias tarefas, retorna lista\n"
                    "results = await asyncio.gather(t1, t2, t3, return_exceptions=True)\n\n"
                    "# wait_for: timeout em uma corrotina\n"
                    "try:\n"
                    "    r = await asyncio.wait_for(slow_op(), timeout=5)\n"
                    "except asyncio.TimeoutError: ...\n\n"
                    "# semaphore: limita concorrência\n"
                    "sem = asyncio.Semaphore(10)\n"
                    "async def fetch(url):\n"
                    "    async with sem:\n"
                    "        return await client.get(url)\n\n"
                    "# cancelar tarefa\n"
                    "task.cancel()\n"
                    "try: await task\n"
                    "except asyncio.CancelledError: ...</code></pre>"

                    "<h3>5. Misturando sync e async</h3>"
                    "<p>Chamar função sync bloqueante em async <em>congela</em> tudo. "
                    "Use <code>run_in_executor</code> ou <code>asyncio.to_thread</code> "
                    "(3.9+):</p>"
                    "<pre><code>import asyncio\n\n"
                    "def cpu_bound(n: int) -&gt; int:\n"
                    "    return sum(range(n))\n\n"
                    "async def main():\n"
                    "    r = await asyncio.to_thread(cpu_bound, 10**7)\n"
                    "    print(r)</code></pre>"

                    "<h3>6. <code>multiprocessing</code> para CPU-bound</h3>"
                    "<pre><code>from concurrent.futures import ProcessPoolExecutor\n\n"
                    "def hash_file(path: str) -&gt; tuple[str, str]:\n"
                    "    import hashlib\n"
                    "    h = hashlib.sha256(Path(path).read_bytes()).hexdigest()\n"
                    "    return path, h\n\n"
                    "with ProcessPoolExecutor() as pool:\n"
                    "    for p, sha in pool.map(hash_file, files):\n"
                    "        print(p, sha)</code></pre>"
                    "<p>Cada worker é um processo Python separado, ignora o GIL e usa "
                    "todos os cores. Custo: serialização (pickle) entre processos. Não "
                    "compartilhe objetos grandes; passe paths/IDs.</p>"

                    "<h3>7. Sincronização: Lock, Queue, Event</h3>"
                    "<pre><code># threading\n"
                    "from threading import Lock\n"
                    "counter = 0\n"
                    "lock = Lock()\n"
                    "def inc():\n"
                    "    global counter\n"
                    "    with lock:\n"
                    "        counter += 1     # GIL não garante atomicidade de operações compostas\n\n"
                    "# producer/consumer\n"
                    "from queue import Queue\n"
                    "q = Queue(maxsize=100)\n"
                    "def producer():\n"
                    "    for item in source: q.put(item)\n"
                    "def consumer():\n"
                    "    while True:\n"
                    "        item = q.get()\n"
                    "        process(item); q.task_done()</code></pre>"

                    "<h3>8. Cuidados clássicos</h3>"
                    "<ul>"
                    "<li><strong>Race condition</strong>: contadores, dicts, listas em "
                    "thread NÃO são atômicos para incrementos/append. Use Lock.</li>"
                    "<li><strong>Deadlock</strong>: pegando dois locks em ordens "
                    "diferentes em threads diferentes. Sempre adquira em ordem fixa.</li>"
                    "<li><strong>asyncio bloqueio acidental</strong>: chamar "
                    "<code>requests.get</code> dentro de async congela o loop. Use "
                    "<code>httpx.AsyncClient</code> ou <code>aiohttp</code>.</li>"
                    "<li><strong>multiprocessing no Windows</strong>: precisa "
                    "<code>if __name__ == \"__main__\":</code> ao redor do código que "
                    "spawna, senão o filho re-executa o módulo todo.</li>"
                    "</ul>"

                    "<h3>9. Quando usar o quê, guia rápido</h3>"
                    "<table>"
                    "<thead><tr><th>Caso</th><th>Escolha</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>20 chamadas HTTP em script único</td><td>ThreadPoolExecutor (simples)</td></tr>"
                    "<tr><td>Servidor web com 1000+ conexões</td><td>asyncio + uvicorn/FastAPI</td></tr>"
                    "<tr><td>Processar 50 GB de logs com regex</td><td>ProcessPoolExecutor</td></tr>"
                    "<tr><td>Hash de muitos arquivos</td><td>ProcessPoolExecutor</td></tr>"
                    "<tr><td>Numpy/Polars cálculos</td><td>Já libera o GIL, threads bastam</td></tr>"
                    "<tr><td>Apenas alguns segundos sequenciais</td><td>Não otimize</td></tr>"
                    "</tbody></table>"
                ),
                "practical": (
                    "Implemente <code>healthcheck.py</code> que recebe via CLI uma lista "
                    "de URLs e verifica todas em paralelo, com no máximo 20 conexões "
                    "simultâneas. Faça duas versões: (1) com "
                    "<code>ThreadPoolExecutor + requests</code>; (2) com "
                    "<code>asyncio + httpx + Semaphore(20)</code>. Compare o tempo total "
                    "para 200 URLs. Trate timeouts (5s por URL) e imprima sumário no "
                    "stderr (OK / FAIL counts) e os detalhes em JSON no stdout."
                ),
            },
            "materials": [
                m("Python docs, asyncio",
                  "https://docs.python.org/3/library/asyncio.html",
                  "docs", "Referência oficial de asyncio."),
                m("Python docs, concurrent.futures",
                  "https://docs.python.org/3/library/concurrent.futures.html",
                  "docs", "Pool de threads e processos com API uniforme."),
                m("Real Python, async IO",
                  "https://realpython.com/async-io-python/",
                  "article", "Tutorial completo de asyncio."),
                m("David Beazley, Understanding the Python GIL",
                  "https://www.dabeaz.com/python/UnderstandingGIL.pdf",
                  "article", "Análise clássica do GIL."),
                m("Łukasz Langa, Async Python is not Faster",
                  "https://calpaterson.com/async-python-is-not-faster.html",
                  "article", "Mitos e fatos sobre async em Python."),
                m("PEP 703, Making the GIL Optional",
                  "https://peps.python.org/pep-0703/",
                  "docs", "Free-threading no Python 3.13+."),
            ],
            "questions": [
                q("Para 100 chamadas HTTP em paralelo num script, a escolha mais simples é:",
                  "ThreadPoolExecutor com requests.",
                  ["multiprocessing.Pool",
                   "Threading manual com Lock global",
                   "Subprocess de curl"],
                  "I/O-bound: threads ajudam (GIL libera durante I/O). Pool simplifica. "
                  "Multiprocessing seria caro pelo overhead de pickle."),
                q("O GIL impede que threads ajudem em qual cenário?",
                  "Cálculos CPU-bound em Python puro.",
                  ["Chamadas HTTP",
                   "Leitura de arquivo grande",
                   "Esperar timer"],
                  "GIL serializa execução de bytecode. Para CPU-bound, use "
                  "multiprocessing ou libs C que liberam o GIL."),
                q("Em asyncio, o que acontece se você chamar `time.sleep(5)` dentro de async?",
                  "Bloqueia todo o event loop por 5s, todas as outras tarefas pausam.",
                  ["Continua paralelo automaticamente.",
                   "Lança AsyncError.",
                   "É equivalente a `await asyncio.sleep(5)`."],
                  "time.sleep é síncrono. Em async use `await asyncio.sleep`. "
                  "Bloqueio acidental é a armadilha número 1."),
                q("`asyncio.gather(*tasks)` com return_exceptions=False...",
                  "Cancela as outras tarefas se uma falhar.",
                  ["Espera todas terminarem mesmo com erros.",
                   "Não usa o event loop.",
                   "Só funciona em 3.12+."],
                  "Quando uma falha, gather propaga a exceção. Para coletar todas, "
                  "use return_exceptions=True (cada item pode ser exceção)."),
                q("Para limitar a 10 conexões simultâneas em asyncio:",
                  "asyncio.Semaphore(10) com `async with sem:` ao redor da chamada.",
                  ["Limitar threads.",
                   "Loop sleep manual.",
                   "Não há como limitar."],
                  "Semaphore é o mecanismo padrão. Cada acquire decrementa, release "
                  "incrementa; bloqueia quando zerado."),
                q("`asyncio.to_thread(fn, *args)` é útil para...",
                  "Rodar função síncrona bloqueante sem congelar o event loop.",
                  ["Lançar Exception em outra thread.",
                   "Aumentar GIL.",
                   "Substituir gather."],
                  "Move a chamada para um pool de threads, retorna corrotina que "
                  "espera o resultado. Ideal para integrar libs sync em async."),
                q("Race condition em threads acontece tipicamente quando:",
                  "Duas threads modificam estado compartilhado sem sincronização.",
                  ["O processador é multi-core.",
                   "Você usa muitos imports.",
                   "O Python é lento."],
                  "Operações compostas (count += 1) não são atômicas. Use Lock, "
                  "Queue ou estruturas thread-safe."),
                q("Para CPU-bound em Python puro, use:",
                  "ProcessPoolExecutor (multiprocessing).",
                  ["asyncio com gather.",
                   "ThreadPoolExecutor.",
                   "concurrent.futures.Future direto."],
                  "Processos contornam o GIL, usam todos os cores. Custo: serialização "
                  "via pickle entre processos."),
                q("Em multiprocessing no Windows, o código que dispara workers DEVE estar dentro de:",
                  "if __name__ == '__main__':",
                  ["try/except",
                   "with",
                   "async def"],
                  "Windows usa 'spawn' que re-executa o módulo no filho. Sem o guard, "
                  "o filho dispara workers de novo → fork bomb."),
                q("`asyncio.TaskGroup` (3.11+) tem qual vantagem sobre gather?",
                  "Cancelamento estruturado: se uma falhar, as outras são canceladas e erros vêm em ExceptionGroup.",
                  ["É mais rápido.",
                   "Funciona em threads.",
                   "Substitui Semaphore."],
                  "TaskGroup implementa structured concurrency, escopo explícito, "
                  "cleanup automático, erros agregados."),
            ],
        },
        # =====================================================================
        # 6.8 Testes
        # =====================================================================
        {
            "title": "Testes com pytest, mocks e cobertura",
            "summary": "Pytest essencial, fixtures, parametrize, mocks de I/O e métricas de cobertura.",
            "lesson": {
                "intro": (
                    "Testes automatizados não são opcionais em código que vai pra "
                    "produção. Em DevOps são especialmente críticos: um script de "
                    "deploy errado derruba ambientes; um pipeline sem teste nas "
                    "ferramentas custa downtime real. Esta aula é um curso intensivo "
                    "de pytest, a ferramenta de teste do ecossistema Python."
                ),
                "body": (
                """<h3>1. Por que pytest e não unittest</h3>
<p><code>unittest</code> é stdlib e funciona, mas força um estilo verboso: você
herda de <code>TestCase</code>, escreve <code>self.assertEqual(a, b)</code> em
vez de <code>assert a == b</code>, e perde a introspecção de que Python já é
capaz sozinho. O pytest resolve isso com um truque que vale entender, porque
explica por que <code>assert</code> puro em pytest te dá um diff detalhado
igual a uma asserção "rica" de outros frameworks: ao importar um arquivo de
teste, o pytest reescreve o bytecode de cada <code>assert</code>, trocando a
expressão booleana por uma versão instrumentada que sabe o valor de cada
subexpressão. É por isso que <code>assert response.json() == esperado</code>
falha mostrando os dois dicts lado a lado, com o campo que diverge destacado
— sem você jamais ter escrito uma linha de comparação especial. unittest não
tem esse mecanismo; sua saída de erro é genérica ("False is not true").</p>
<p>Fora esse detalhe de implementação, o que realmente muda o dia a dia é o
ecossistema: fixtures componíveis (seção 3), parametrização declarativa
(seção 4) e um catálogo enorme de plugins (cobertura, asyncio, Django, mock,
retry de teste flaky). unittest exige escrever essa infraestrutura à mão.</p>

<h3>2. Descoberta de testes: como o pytest te encontra</h3>
<p>O pytest não roda "tudo que existe": ele varre diretórios procurando
arquivos <code>test_*.py</code> ou <code>*_test.py</code>, e dentro deles
funções <code>test_*</code> (ou métodos <code>test_*</code> em classes
<code>Test*</code>, sem <code>__init__</code>). Fugir dessa convenção é a
causa nº 1 de "meu teste não roda e não dá nem erro": um arquivo chamado
<code>utils_test_helpers.py</code> ou uma função <code>testa_login()</code>
(sem underscore) são simplesmente invisíveis para o coletor — ele não avisa,
só não os lista.</p>
<pre><code># app/utils.py
def parse_image(s: str) -&gt; tuple[str, str]:
    if ":" not in s:
        return s, "latest"
    name, tag = s.rsplit(":", 1)
    return name, tag

# tests/test_utils.py
from app.utils import parse_image

def test_implicit_latest():
    assert parse_image("web") == ("web", "latest")

def test_explicit_tag():
    assert parse_image("web:1.2") == ("web", "1.2")

# rodar: pytest -v</code></pre>
<p>Um <code>conftest.py</code> colocado em qualquer nível de diretório é
carregado automaticamente pelo pytest para todo teste abaixo dele — sem
import explícito. É o lugar certo para fixtures compartilhadas; import
manual de fixture entre arquivos de teste é sinal de que ela deveria estar
ali.</p>

<h3>3. Fixtures: injeção de dependência, não decoração</h3>
<p>Uma fixture não é açúcar sintático para "código que roda antes do teste":
é um grafo de dependências resolvido por nome. Quando uma função de teste
declara um parâmetro <code>tmp_config</code>, o pytest procura uma fixture
com esse nome, executa o que vier antes do <code>yield</code> (ou o
<code>return</code>), injeta o valor, roda o teste, e só depois executa o
que vier depois do <code>yield</code> — o teardown. Fixtures podem depender
de outras fixtures do mesmo jeito, formando uma árvore resolvida na ordem
certa automaticamente.</p>
<pre><code>import pytest, tempfile
from pathlib import Path

@pytest.fixture
def tmp_config(tmp_path: Path) -&gt; Path:
    cfg = tmp_path / "app.yaml"
    cfg.write_text("env: test\\nport: 8080\\n")
    return cfg

def test_load_config(tmp_config):
    data = load(tmp_config)
    assert data["port"] == 8080</code></pre>
<p>O parâmetro <code>scope</code> ("function", "class", "module", "session")
decide QUANTAS VEZES a fixture roda — e é onde mora um bug clássico:
uma fixture <code>session</code>-scoped que devolve um objeto mutável (uma
lista, um dict, um client HTTP com estado) é <em>compartilhada</em> entre
todos os testes da sessão. Se o teste A modifica esse objeto e não desfaz,
o teste B recebe o estado sujo — um vazamento de estado entre testes que
some quando você roda o arquivo isolado (porque não há teste anterior para
sujar nada) e só aparece rodando a suíte inteira, o pior tipo de
intermitência para debugar.</p>
<p>Fixtures embutidas que valem conhecer de cor:</p>
<ul>
<li><code>tmp_path</code>: <code>Path</code> temporário, único por teste,
removido depois — evita <code>TemporaryDirectory</code> manual e o risco de
esquecer o cleanup.</li>
<li><code>monkeypatch</code>: substitui atributo, item de dict ou variável
de ambiente, com rollback automático no teardown, mesmo se o teste
falhar.</li>
<li><code>capsys</code>: captura stdout/stderr para asserção — útil para
testar CLIs sem redirecionar o terminal de verdade.</li>
<li><code>caplog</code>: captura registros de <code>logging</code>, para
afirmar que um WARNING específico foi (ou não) emitido.</li>
</ul>

<h3>4. Parametrize: uma tabela de casos, não um laço</h3>
<pre><code>@pytest.mark.parametrize("input,expected", [
    ("web",       ("web", "latest")),
    ("web:1.2",   ("web", "1.2")),
    ("r/r:tag",   ("r/r", "tag")),
    ("",          ("", "latest")),
])
def test_parse(input, expected):
    assert parse_image(input) == expected</code></pre>
<p>A diferença para um <code>for case in cases: ...</code> dentro de uma
função de teste única não é só estética: cada linha do parametrize vira um
<strong>teste independente</strong> no relatório do pytest, com nome
próprio (<code>test_parse[web:1.2-expected1]</code>). Se o terceiro caso
falhar, você vê exatamente qual — com o laço manual, o teste inteiro para
no primeiro <code>assert</code> que falhar e você não sabe se os outros
três também quebrariam. O trade-off do parametrize é o oposto: ele tenta
esconder que aqueles quatro casos têm exatamente a mesma lógica de teste;
se um dia o comportamento divergir por caso (um precisa de um mock
diferente, por exemplo), forçar tudo numa tabela produz um teste
artificialmente genérico. Nesse ponto, separar em funções distintas é mais
honesto do que espremer no parametrize.</p>

<h3>5. Mocks: isolando o que está fora do teste — e o erro mais comum ao usá-los</h3>
<p>Testes unitários não devem fazer chamadas reais a API, banco ou shell:
isso os torna lentos, dependentes de rede e não-determinísticos (a API pode
estar fora do ar no CI). A solução é substituir a dependência por um dublê
— mas o detalhe que confunde todo mundo na primeira vez é <strong>onde</strong>
aplicar o patch: você não faz mock de onde a função foi <em>definida</em>,
e sim de onde ela foi <em>importada e é chamada</em>. Se
<code>app/service.py</code> tem <code>from app.client import fetch_user</code>
e você usa a função dentro de <code>service.py</code>, o alvo do
<code>monkeypatch</code>/<code>mocker.patch</code> é
<code>"app.service.fetch_user"</code>, não <code>"app.client.fetch_user"</code>
— porque <code>service.py</code> já tem sua própria referência ao nome, e
substituir o original em <code>client.py</code> não afeta quem já importou.</p>
<pre><code>def fetch_user(client, uid: int):
    r = client.get(f"/users/{uid}")
    r.raise_for_status()
    return r.json()

def test_fetch_user(mocker):     # pytest-mock
    fake = mocker.MagicMock()
    fake.get.return_value.json.return_value = {"id": 7, "name": "Ana"}
    fake.get.return_value.raise_for_status.return_value = None
    user = fetch_user(fake, 7)
    fake.get.assert_called_once_with("/users/7")
    assert user["name"] == "Ana"</code></pre>
<p>Para HTTP especificamente, prefira <code>responses</code> (requests) ou
<code>respx</code> (httpx) a mockar o client inteiro à mão: eles simulam a
camada de transporte, então o resto do código real (serialização, retry,
headers) continua rodando de verdade — você só substitui a rede. O risco do
mock genérico com <code>MagicMock</code> é confiança falsa: como qualquer
atributo ou chamada "funciona" (devolve outro MagicMock), um erro de
digitação no nome do método invocado passa batido silenciosamente em vez de
estourar um <code>AttributeError</code> como aconteceria no objeto real.</p>

<h3>6. Testando exceções: `pytest.raises` e a pegadinha do `match`</h3>
<pre><code>import pytest

def test_invalid_replicas():
    with pytest.raises(ValueError, match=r"replicas.*fora"):
        Replica(count=999)</code></pre>
<p><code>match</code> não compara a mensagem inteira: ele roda
<code>re.search</code>, então basta a mensagem CONTER o padrão em algum
lugar. É proposital (a mensagem de erro pode mudar de detalhe sem quebrar o
teste), mas também mascara: um regex frouxo demais (<code>match="erro"</code>)
passa mesmo se a exceção certa nunca foi levantada e outra, qualquer uma que
também contenha a palavra "erro", ocupou o lugar. Prefira um trecho
específico da mensagem real, não uma palavra genérica.</p>

<h3>7. Marks: organizando a suíte por categoria</h3>
<pre><code>@pytest.mark.skipif(sys.platform == "win32", reason="só Linux")
def test_unix_socket(): ...

@pytest.mark.xfail(reason="bug conhecido #123")
def test_known_bug(): ...

@pytest.mark.slow
def test_full_pipeline(): ...
# rodar: pytest -m "not slow"</code></pre>
<p>Marks arbitrários como <code>slow</code> geram um <code>PytestUnknownMarkWarning</code>
até serem registrados em <code>pyproject.toml</code>
(<code>[tool.pytest.ini_options] markers = ["slow: teste lento, roda só no merge"]</code>)
— sem isso, um typo no nome do mark (<code>@pytest.mark.solw</code>) não
falha nada, só silenciosamente deixa de filtrar aquele teste, e ele roda
onde não devia. <code>xfail</code> tem uma armadilha própria: por padrão,
se o teste marcado "esperado para falhar" passar, o resultado é apenas um
aviso (XPASS), não uma falha — use <code>strict=True</code> quando quiser
ser avisado no momento em que o bug for corrigido de verdade.</p>

<h3>8. Cobertura: o que ela mede, e o que ela não mede</h3>
<pre><code># pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=app --cov-report=term --cov-report=html --cov-branch"

# rodar
pytest                     # tabela no terminal
open htmlcov/index.html    # report visual</code></pre>
<p>Cobertura de LINHA (o padrão) só diz que aquela linha executou pelo menos
uma vez — não que todos os caminhos por ela passaram. <code>if x &gt; 0:
resultado = a / x</code> conta como "coberta" mesmo que <code>x</code> nunca
tenha sido zero no teste, escondendo exatamente o caso que quebraria em
produção. <code>--cov-branch</code> mede cobertura de RAMO: exige que tanto
o <code>if</code> quanto o <code>else</code> implícito tenham sido
exercitados, uma medida mais honesta. De qualquer forma, cobertura é um
piso, não uma meta: 100% de linhas cobertas por testes que nunca checam o
valor de retorno (só chamam a função) prova zero sobre correção. Use
<code>--cov-fail-under=80</code> para o CI reprovar quando a cobertura
cair, não para persegui-la como número isolado.</p>

<h3>9. Testes assíncronos: o loop de eventos que ninguém vê</h3>
<pre><code># pip install pytest-asyncio
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch("https://example.com")
    assert result.status == 200</code></pre>
<p><code>pytest-asyncio</code> cria um event loop por teste (ou por módulo,
dependendo do <code>asyncio_mode</code> configurado) e roda a corrotina
dentro dele — é por isso que uma função <code>async def</code> sem esse
plugin simplesmente "passa" sem executar nada: pytest chama a função,
recebe de volta um objeto corrotina não-aguardado, e um objeto não é
<code>False</code>, então o teste nem chega a falhar. Configure
<code>asyncio_mode = "auto"</code> no <code>pyproject.toml</code> para não
precisar do <code>@pytest.mark.asyncio</code> em cada função — e cuidado ao
misturar fixture síncrona que abre um recurso (client HTTP, conexão) com
teste assíncrono: se o recurso não foi criado dentro do mesmo loop, operações
nele podem travar ou lançar <code>RuntimeError: attached to a different
loop</code>, um erro que só aparece rodando a suíte inteira em paralelo.</p>

<h3>10. Unitário, integração, e2e: a pirâmide e por que invertê-la é caro</h3>
<ul>
<li><strong>Unitário</strong>: testa função/método isolado, rápido
(&lt;100ms), sem I/O real. Roda a cada commit, em segundos.</li>
<li><strong>Integração</strong>: testa contra dependência real (banco, fila,
API), tipicamente com containers efêmeros via <code>testcontainers</code>.
Mais lento, mas pega bugs que mock nenhum detecta — um schema de banco que
mudou, uma API que passou a exigir um header novo.</li>
<li><strong>Ponta a ponta (e2e)</strong>: sobe o sistema inteiro e simula um
usuário real. O mais caro e o mais frágil: qualquer serviço fora do ar,
qualquer timing de rede, derruba o teste sem o código ter mudado.</li>
</ul>
<p>A pirâmide (muitos unitários na base, menos integração no meio, poucos
e2e no topo) não é dogma estético: é sobre onde o tempo de CI e a
estabilidade da suíte vão parar. Uma suíte invertida — poucos unitários,
muitos e2e — fica lenta (minutos por rodada) e "flaky" (falha
intermitente sem relação com bug real), e o time aprende a ignorar CI
vermelho porque "provavelmente é flakiness" — o momento em que os testes
param de proteger de verdade.</p>"""
                ),
                "practical": (
                    "Para o <code>top_users.py</code> que você escreveu na aula 6.2: "
                    "(1) crie <code>tests/test_top_users.py</code>; (2) escreva uma "
                    "fixture <code>access_log</code> usando <code>tmp_path</code> que "
                    "gera um log fictício com 50 linhas, status variados; "
                    "(3) parametrize 5 casos diferentes (top 1, top 3, vazio, todas 200, "
                    "mistura); (4) garanta cobertura ≥ 90% com "
                    "<code>pytest --cov=top_users --cov-fail-under=90</code>."
                ),
            },
            "materials": [
                m("pytest documentation",
                  "https://docs.pytest.org/",
                  "docs", "Documentação oficial."),
                m("Brian Okken, pytest book",
                  "https://pythontest.com/pytest-book/",
                  "book", "Livro de referência."),
                m("Real Python, Effective Python Testing With Pytest",
                  "https://realpython.com/pytest-python-testing/",
                  "article", "Tutorial completo."),
                m("coverage.py",
                  "https://coverage.readthedocs.io/",
                  "docs", "Cobertura de código."),
                m("pytest-mock",
                  "https://pytest-mock.readthedocs.io/",
                  "docs", "Plugin para mocks com fixture."),
                m("testcontainers-python",
                  "https://testcontainers-python.readthedocs.io/",
                  "docs", "DB e serviços reais em containers para testes."),
            ],
            "questions": [
                q("A vantagem principal do pytest sobre unittest é:",
                  "Sintaxe direta com `assert` e fixtures componíveis.",
                  ["Mais rápido no Linux.",
                   "Tem mais funções built-in.",
                   "É a única ferramenta com cobertura."],
                  "pytest reduz boilerplate. fixtures, parametrize e plugins são o "
                  "diferencial."),
                q("`@pytest.mark.parametrize` é usado para:",
                  "Rodar o mesmo teste com múltiplos conjuntos de inputs.",
                  ["Marcar testes como lentos.",
                   "Pular testes em CI.",
                   "Configurar fixtures."],
                  "Cada linha do parametrize gera um caso de teste, com nome legível "
                  "indicando qual falhou."),
                q("`tmp_path` em pytest é:",
                  "Uma fixture built-in que dá um diretório temporário único por teste.",
                  ["Variável de ambiente.",
                   "Função do sistema.",
                   "Atributo de classe."],
                  "Cleanup automático ao fim do teste. Evita TemporaryDirectory manual."),
                q("Para verificar que uma função levanta uma exceção específica:",
                  "with pytest.raises(ValueError): ...",
                  ["assert raises(ValueError, fn)",
                   "try: fn(); except: pass",
                   "@pytest.expect(ValueError)"],
                  "pytest.raises é o jeito idiomático. Aceita `match=` para checar "
                  "mensagem por regex."),
                q("Por que mockar chamadas externas em testes unitários?",
                  "Para testes serem rápidos, determinísticos e independentes da rede.",
                  ["É exigência do pytest.",
                   "Aumenta a cobertura automaticamente.",
                   "Evita logs."],
                  "Testes unitários devem rodar offline e em milissegundos. Mocks "
                  "isolam o código sob teste."),
                q("`monkeypatch.setenv('TOKEN', 'x')` em pytest:",
                  "Define a variável de ambiente apenas durante o teste; rollback automático.",
                  ["Grava .env no disco.",
                   "Modifica permanentemente a env.",
                   "Funciona só no Linux."],
                  "monkeypatch desfaz tudo no teardown. Essencial para testar configs "
                  "via env."),
                q("Cobertura de 100% garante código sem bugs?",
                  "Não, só garante que cada linha foi executada, não que os casos de borda foram cobertos.",
                  ["Sim.",
                   "Sim, em código puro.",
                   "Apenas em Python 3.12+."],
                  "Cobertura é métrica de presença, não de qualidade. Casos de borda "
                  "(None, listas vazias, valores extremos) precisam ser explícitos."),
                q("Para testar código async com pytest, instale:",
                  "pytest-asyncio e use @pytest.mark.asyncio",
                  ["asyncio-test (não existe)",
                   "Usa unittest.AsyncTestCase",
                   "Não dá para testar código async."],
                  "pytest-asyncio é o plugin padrão. Configure mode='auto' no "
                  "pyproject.toml para evitar mark em todo teste."),
                q("Onde colocar fixtures que múltiplos arquivos de teste compartilham?",
                  "conftest.py no diretório de testes.",
                  ["No próprio arquivo de teste, sempre.",
                   "Em fixtures.py importado manualmente.",
                   "Em um plugin externo."],
                  "conftest.py é detectado automaticamente. Útil para fixtures globais "
                  "(client HTTP fake, DB de teste, etc.)."),
                q("`pytest -m \"not slow\"` faz o quê?",
                  "Roda apenas testes não marcados com @pytest.mark.slow.",
                  ["Roda os mais lentos primeiro.",
                   "Define um nome para a suíte.",
                   "Causa erro de sintaxe."],
                  "Marks permitem segmentar a suíte. Ideal para CI: rodar 'not slow' "
                  "no PR; tudo no merge."),
            ],
        },
        # =====================================================================
        # 6.9 Empacotamento e qualidade
        # =====================================================================
        {
            "title": "Empacotamento moderno e qualidade de código",
            "summary": "pyproject.toml, venv, pip, uv, ruff e mypy, o ferramental de um projeto Python profissional.",
            "lesson": {
                "intro": (
                    "Um script .py funciona; um <em>projeto</em> Python tem ambiente "
                    "isolado, dependências travadas, formatador, linter, type checker e "
                    "build reprodutível. Esta aula mostra o stack moderno (2024-2026) e "
                    "como organizar um projeto novo do zero, não a versão de 2010 com "
                    "<code>setup.py</code>."
                ),
                "body": (
                """<h3>1. Ambientes virtuais: por que isolar é o que evita "funciona na minha máquina"</h3>
<pre><code>python -m venv .venv
source .venv/bin/activate         # Linux/Mac
.venv\\Scripts\\activate            # Windows
python -m pip install --upgrade pip
pip install requests pytest</code></pre>
<p>Sem ambiente isolado, todo <code>pip install</code> vai para o Python
global do sistema — e como dois projetos raramente concordam na mesma
versão exata de uma dependência, instalar a versão que o projeto B precisa
pode silenciosamente quebrar o projeto A, que já estava rodando com outra
versão minutos antes. Em distros Linux, o problema é pior: ferramentas do
próprio sistema operacional (como o <code>apt</code> em algumas distros)
dependem de pacotes Python instalados globalmente, e um
<code>pip install --upgrade</code> descuidado consegue quebrar
utilitários do SO. Um <code>venv</code> por projeto elimina essa classe
inteira de conflito: cada ambiente tem seu próprio conjunto de pacotes,
completamente isolado dos outros.</p>

<h3>2. `uv`: o mesmo problema, resolvido sem reescrever o resolvedor de dependências a cada instalação</h3>
<p><code>uv</code> (da Astral, mesma equipe do ruff) substitui
pip+virtualenv+pip-tools numa ferramenta só, escrita em Rust — 10 a 100
vezes mais rápida no caso comum. A diferença de velocidade não é só
"implementação mais rápida da mesma coisa": pip resolve dependências
baixando e testando pacotes incrementalmente a cada conflito, enquanto uv
mantém um cache global de metadados e resolve o grafo inteiro antes de
baixar qualquer coisa, evitando trabalho repetido entre projetos que
compartilham dependências.</p>
<pre><code>curl -LsSf https://astral.sh/uv/install.sh | sh

uv init meu-projeto && cd meu-projeto
uv add requests pydantic
uv add --dev pytest mypy ruff
uv run pytest                  # roda no env do projeto
uv lock                        # gera uv.lock determinístico
uv sync                        # restaura ambiente exato</code></pre>
<p>O <code>uv.lock</code> gerado é o que resolve o problema clássico de
"funcionava ontem": ele trava não só a versão de cada dependência direta,
mas de toda a árvore transitiva, com hash de integridade. Commitado no
git, garante que o ambiente que roda no CI é bit-a-bit o mesmo que roda na
sua máquina — sem isso, um <code>pip install -r requirements.txt</code>
hoje pode trazer uma versão mais nova de uma dependência transitiva do que
trouxe há um mês, e um bug "que ninguém mexeu" aparece do nada.</p>

<h3>3. `pyproject.toml`: um arquivo central em vez de três desencontrados</h3>
<pre><code>[project]
name = "deploy-tool"
version = "0.3.0"
description = "Internal tool for deploys"
readme = "README.md"
requires-python = "&gt;=3.11"
dependencies = [
    "requests&gt;=2.31",
    "pydantic&gt;=2.0",
    "typer&gt;=0.9",
]

[project.optional-dependencies]
dev = ["pytest", "mypy", "ruff"]

[project.scripts]
deploy = "deploy_tool.cli:main"   # vira comando 'deploy' instalável

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"</code></pre>
<p>Antes deste padrão (formalizado pela PEP 621), um projeto Python
espalhava a mesma informação em <code>setup.py</code> (metadados +
lógica de build misturados, executável, logo uma superfície de ataque —
instalar um pacote malicioso podia rodar código arbitrário só de importar
o <code>setup.py</code>), <code>setup.cfg</code> e
<code>requirements.txt</code>. Consolidar tudo num TOML declarativo (sem
código executável) elimina essa superfície e dá um único lugar onde
qualquer ferramenta — pip, uv, ruff, mypy, pytest — sabe procurar sua
configuração.</p>

<h3>4. Layout `src/`: por que um diretório a mais evita um bug de import</h3>
<pre><code>meu-projeto/
├── pyproject.toml
├── README.md
├── src/
│   └── deploy_tool/
│       ├── __init__.py
│       ├── cli.py
│       └── core.py
└── tests/
    └── test_core.py</code></pre>
<p>Sem o <code>src/</code>, com o pacote direto na raiz do repositório, é
fácil rodar os testes sem nunca ter instalado o pacote de verdade — o
Python encontra o código local pelo diretório de trabalho atual, e os
testes passam mesmo que o <code>pyproject.toml</code> esteja com uma
dependência faltando ou um caminho de import errado, porque o mecanismo
que "esconderia" esse erro na instalação de outra pessoa nunca chegou a
rodar. Com o código dentro de <code>src/</code>, ele só fica importável
depois de <code>pip install -e .</code> — forçando o teste a validar
exatamente o que seria publicado e instalado por outra pessoa, não um
atalho que só existe no seu checkout local.</p>

<h3>5. `ruff`: uma ferramenta em Rust cobrindo o que antes eram quatro em Python</h3>
<p><code>ruff</code> reimplementa as regras de flake8, isort, pylint e
black numa única ferramenta compilada — a diferença de velocidade (segundos
viram milissegundos num projeto grande) importa na prática porque muda o
que é viável rodar: um linter lento demais para rodar a cada save do editor
só roda no CI, onde o feedback chega minutos depois, e não no momento em
que o erro foi escrito.</p>
<pre><code>ruff check .                  # lint (encontra problemas)
ruff check --fix .            # lint + correções automáticas
ruff format .                 # formatador (substitui black)

# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "S"]
# E = pycodestyle, F = pyflakes, I = isort,
# B = bugbear, UP = pyupgrade, S = bandit (security)</code></pre>
<p>O conjunto <code>S</code> (regras de segurança, portadas do bandit) é o
que pega coisas como <code>subprocess.run(cmd, shell=True)</code> com
input não sanitizado ou uso de <code>eval</code> — vale ativar mesmo em
projeto interno, porque script de automação de infraestrutura é
exatamente o tipo de código que, comprometido, tem acesso amplo demais
para ser tratado como "não é código de produção".</p>

<h3>6. `mypy`: type checking estático, e por que começar `strict` trava o time</h3>
<pre><code>mypy src/                   # checa types

# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true</code></pre>
<p>Type hints em Python não são checadas em runtime — <code>def f(x: int)</code>
aceita uma string sem reclamar, a anotação é só metadado. <code>mypy</code>
analisa o código estaticamente (sem executá-lo) e sinaliza onde os tipos
declarados não batem com o uso real, pegando uma classe de bug (passar o
tipo errado para uma função) antes mesmo de rodar um teste. O
custo-benefício de <code>strict = true</code> muda com a idade do código:
num projeto novo, sem dívida acumulada, é barato manter tudo tipado desde
o início. Em código legado sem anotação nenhuma, ligar `strict` de uma vez
produz centenas de erros simultâneos e o time aprende a ignorar o mypy
inteiro — melhor ativar módulo por módulo (<code>[[tool.mypy.overrides]]</code>
por pacote) conforme cada um ganha tipos reais.</p>

<h3>7. Pre-commit hooks: mover a checagem para antes do commit existir</h3>
<pre><code># .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy</code></pre>
<pre><code>pre-commit install
git commit -m "x"   # roda lint/format/types antes</code></pre>
<p>A diferença entre rodar lint só no CI e rodar via pre-commit é
QUANDO o autor descobre o problema: no CI, minutos depois, já trocou de
tarefa, e corrigir exige voltar ao contexto. No pre-commit, o commit
simplesmente não acontece até o código passar — o feedback chega no
segundo em que o problema ainda está na cabeça de quem escreveu. O
trade-off é que hooks lentos demais frustram o fluxo de commit; é por
isso que ruff (rápido) entra aqui e suítes de teste completas (lentas)
ficam reservadas para o CI.</p>

<h3>8. CI mínima: repetir localmente o que vai rodar remotamente</h3>
<pre><code># .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --extra dev
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy src/
      - run: uv run pytest --cov=src --cov-fail-under=80</code></pre>
<p>Rodar contra uma MATRIZ de versões de Python (3.11 e 3.12 aqui) pega um
tipo de bug que testar numa versão só nunca revela: comportamento que
mudou entre versões (ordem de dict em casos extremos, mudanças em stdlib,
sintaxe nova disponível numa versão mas não na outra). Sem a matriz, o
projeto só descobre que quebrou em 3.12 quando alguém tenta rodar em
produção nessa versão — tarde demais para ser um problema de CI.</p>

<h3>9. Distribuição: do wheel local ao registro privado</h3>
<pre><code>uv build                    # cria dist/*.whl e *.tar.gz
uv publish                  # publica no PyPI (requer token)

# para repositório privado (CodeArtifact, Artifactory, GCP AR)
uv publish --publish-url https://my-private/pypi/</code></pre>
<p>Um <em>wheel</em> (<code>.whl</code>) é um pacote pré-compilado — para
código puro-Python, "compilado" só significa empacotado com metadados
prontos, sem precisar rodar <code>setup.py</code> na máquina de quem
instala (que é justamente a superfície de execução arbitrária que o
<code>pyproject.toml</code> declarativo elimina, seção 3). Ferramenta
interna de uma empresa não deveria ir para o PyPI público — um registro
privado (CodeArtifact na AWS, Artifactory, Google Artifact Registry) dá o
mesmo fluxo de <code>pip install</code>/<code>uv add</code> sem expor
nome de projeto, estrutura interna ou, pior, vazar acidentalmente uma
dependência com segredo embutido para a internet.</p>

<h3>10. Resumo: stack mínimo recomendado (2026)</h3>
<table>
<thead><tr><th>Função</th><th>Ferramenta</th></tr></thead>
<tbody>
<tr><td>Ambiente + deps</td><td><code>uv</code></td></tr>
<tr><td>Build</td><td><code>hatchling</code> (via uv)</td></tr>
<tr><td>Linter + formatter</td><td><code>ruff</code></td></tr>
<tr><td>Type checker</td><td><code>mypy</code> ou <code>pyright</code></td></tr>
<tr><td>Testes</td><td><code>pytest</code> + <code>pytest-cov</code></td></tr>
<tr><td>Pre-commit</td><td><code>pre-commit</code></td></tr>
</tbody>
</table>"""
                ),
                "practical": (
                    "Crie um projeto novo <code>uv init mytool</code> com src layout. "
                    "Adicione: (1) dependências <code>typer, requests</code>; "
                    "(2) dev deps <code>pytest, mypy, ruff</code>; "
                    "(3) script entrypoint <code>mytool</code>; (4) configure ruff "
                    "(line-length 100, regras E/F/I/B/UP) e mypy strict no "
                    "<code>pyproject.toml</code>; (5) <code>.pre-commit-config.yaml</code> "
                    "rodando ruff e mypy; (6) faça um commit propositalmente quebrando "
                    "estilo e veja o pre-commit barrar."
                ),
            },
            "materials": [
                m("PEP 621, pyproject.toml metadata",
                  "https://peps.python.org/pep-0621/",
                  "docs", "Especificação oficial do pyproject.toml."),
                m("uv documentation",
                  "https://docs.astral.sh/uv/",
                  "docs", "Doc oficial do uv (Astral)."),
                m("ruff documentation",
                  "https://docs.astral.sh/ruff/",
                  "docs", "Lint + format ultrarrápido."),
                m("mypy, Type checking",
                  "https://mypy.readthedocs.io/",
                  "docs", "Verificador de tipos estático."),
                m("Hatch project",
                  "https://hatch.pypa.io/",
                  "docs", "Build backend moderno (hatchling)."),
                m("pre-commit framework",
                  "https://pre-commit.com/",
                  "docs", "Hooks padronizados de Git."),
            ],
            "questions": [
                q("Por que usar venv (ou similar) em vez de instalar deps globalmente?",
                  "Para isolar dependências por projeto e não afetar o Python do sistema.",
                  ["É mais rápido.",
                   "Reduz uso de disco.",
                   "É só convenção, não muda nada na prática."],
                  "Sem venv, projetos brigam por versões e você pode quebrar o pacote "
                  "do SO instalando lib global."),
                q("O `pyproject.toml` substitui historicamente:",
                  "setup.py, setup.cfg e requirements.txt em muitos casos.",
                  ["Apenas requirements.txt.",
                   "Apenas Makefile.",
                   "Não substitui nada, é só metadata."],
                  "PEP 517/518/621 trouxeram pyproject.toml como arquivo de configuração "
                  "central de build, deps e ferramentas."),
                q("`uv add requests` faz o quê?",
                  "Instala requests no ambiente do projeto e atualiza pyproject.toml/uv.lock.",
                  ["Só baixa o tarball.",
                   "Instala globalmente.",
                   "Cria um virtualenv novo a cada chamada."],
                  "Equivalente a `pip install requests + atualizar requirements`. "
                  "uv mantém lockfile determinístico."),
                q("`ruff` substitui qual conjunto de ferramentas?",
                  "flake8, pylint, isort e black (lint + formatter).",
                  ["Apenas mypy.",
                   "pip e venv.",
                   "pytest."],
                  "ruff é um único binário (Rust) que faz lint, ordenação de imports e "
                  "formatação. Não é type checker."),
                q("O 'src layout' (pacote em src/) tem qual vantagem prática?",
                  "Força instalar o pacote para testar, testes rodam no que será publicado.",
                  ["É exigido pelo PyPI.",
                   "Faz pip ser mais rápido.",
                   "Permite múltiplos pacotes."],
                  "Sem src/, `import meu_pkg` pode pegar o código avulso do diretório "
                  "atual, não a versão instalada, bugs de empacotamento ficam ocultos."),
                q("`pre-commit install` configura o quê?",
                  "Hooks de Git que rodam linters/formatters antes de cada commit.",
                  ["Instala o pacote em /usr/bin.",
                   "Cria um virtualenv.",
                   "É só apelido para pip install -e ."],
                  "Os hooks impedem commit de código fora do padrão. Em time, "
                  "elimina discussão de estilo em PR."),
                q("Para uma dependência usada apenas em desenvolvimento (ex: pytest), você usa:",
                  "[project.optional-dependencies] ou um grupo de dev no uv.",
                  ["Adicionar normalmente em dependencies.",
                   "Compilar manualmente.",
                   "Instalar global no sistema."],
                  "Optional/dev deps não vão para o usuário final que instalar seu "
                  "pacote. Mantém o package final enxuto."),
                q("`mypy --strict` em código legado costuma:",
                  "Gerar muitos erros de cara (type hints ausentes, Any implícito).",
                  ["Rodar instantaneamente sem erros.",
                   "Causar segfault.",
                   "Substituir os testes."],
                  "Strict ativa todas as regras. Em legado, comece sem strict e "
                  "ative módulo por módulo."),
                q("`uv build` produz:",
                  "Um arquivo .whl (wheel) e um sdist .tar.gz na pasta dist/.",
                  ["Um Dockerfile.",
                   "Apenas o tarball original.",
                   "Um binário compilado em C."],
                  "Wheel é o formato binário moderno (rápido de instalar). sdist é o "
                  "código-fonte. Ambos vão para o PyPI."),
                q("Configuração centralizada no pyproject.toml ajuda a evitar:",
                  "Inconsistências entre dev e CI sobre versão de regras de lint, format e types.",
                  ["Conflitos de imports.",
                   "Deadlocks em produção.",
                   "Falhas de DNS."],
                  "Tudo em um único arquivo versionado: dev e CI usam exatamente as "
                  "mesmas regras."),
            ],
        },
        # =====================================================================
        # 6.10 Python para DevSecOps na prática
        # =====================================================================
        {
            "title": "Python para DevSecOps na prática",
            "summary": "Automação de AWS (boto3), Kubernetes (kubernetes-client), métricas Prometheus e CI customizado.",
            "lesson": {
                "intro": (
                    "Esta aula final amarra tudo: usando o Python que você aprendeu, "
                    "vamos ver como interagir com AWS, com a API do Kubernetes, expor "
                    "métricas Prometheus de uma ferramenta interna e construir um job "
                    "customizado de CI. São os casos que mais aparecem em times de "
                    "DevSecOps reais."
                ),
                "body": (
                    "<h3>1. AWS com <code>boto3</code></h3>"
                    "<pre><code>import boto3\n\n"
                    "s3   = boto3.client(\"s3\")\n"
                    "ec2  = boto3.resource(\"ec2\")\n"
                    "sts  = boto3.client(\"sts\")\n\n"
                    "# Identidade efetiva (saber em qual conta/role você está)\n"
                    "ident = sts.get_caller_identity()\n"
                    "print(ident[\"Arn\"])\n\n"
                    "# Listar buckets paginando\n"
                    "for b in s3.list_buckets()[\"Buckets\"]:\n"
                    "    print(b[\"Name\"], b[\"CreationDate\"])\n\n"
                    "# Listar instâncias EC2 com filtro\n"
                    "for inst in ec2.instances.filter(\n"
                    "    Filters=[{\"Name\": \"instance-state-name\", \"Values\": [\"running\"]}]\n"
                    "):\n"
                    "    name = next((t[\"Value\"] for t in (inst.tags or []) if t[\"Key\"] == \"Name\"), \"-\")\n"
                    "    print(inst.id, name, inst.instance_type, inst.private_ip_address)</code></pre>"
                    "<p>Padrões importantes:</p>"
                    "<ul>"
                    "<li><strong>Paginação</strong>: muitas APIs retornam paginadores. "
                    "Use <code>client.get_paginator(\"list_objects_v2\")</code>.</li>"
                    "<li><strong>Credenciais</strong>: nunca hardcoded. Use IAM Role "
                    "(EC2/EKS/Lambda), <code>~/.aws/credentials</code> com profile, "
                    "AWS SSO, ou OIDC em CI.</li>"
                    "<li><strong>Retry/backoff</strong>: <code>botocore</code> já faz, "
                    "mas configure <code>Config(retries={\"mode\": \"adaptive\"})</code> "
                    "para throttling.</li>"
                    "</ul>"

                    "<h3>2. Kubernetes com <code>kubernetes</code> client</h3>"
                    "<pre><code>from kubernetes import client, config\n\n"
                    "# Auto-detect: kubeconfig local ou ServiceAccount in-cluster\n"
                    "try:\n"
                    "    config.load_incluster_config()\n"
                    "except config.ConfigException:\n"
                    "    config.load_kube_config()\n\n"
                    "v1 = client.CoreV1Api()\n"
                    "apps = client.AppsV1Api()\n\n"
                    "# Listar pods em todos os namespaces\n"
                    "for p in v1.list_pod_for_all_namespaces().items:\n"
                    "    print(p.metadata.namespace, p.metadata.name, p.status.phase)\n\n"
                    "# Reiniciar deployment (padrão kubectl rollout restart)\n"
                    "import datetime\n"
                    "patch = {\n"
                    "    \"spec\": {\"template\": {\"metadata\": {\"annotations\": {\n"
                    "        \"kubectl.kubernetes.io/restartedAt\": datetime.datetime.utcnow().isoformat()\n"
                    "    }}}}\n"
                    "}\n"
                    "apps.patch_namespaced_deployment(\"web\", \"prod\", patch)</code></pre>"

                    "<h3>3. Watch: streaming de eventos do K8s</h3>"
                    "<pre><code>from kubernetes import watch\n\n"
                    "w = watch.Watch()\n"
                    "for event in w.stream(v1.list_namespaced_pod, namespace=\"prod\", timeout_seconds=0):\n"
                    "    pod = event[\"object\"]\n"
                    "    if event[\"type\"] in (\"ADDED\", \"MODIFIED\") and pod.status.phase == \"Failed\":\n"
                    "        notify_slack(f\"Pod {pod.metadata.name} falhou\")</code></pre>"
                    "<p>Excelente para construir operadores customizados, controllers, "
                    "ou alertas custom que kube-prometheus não cobre.</p>"

                    "<h3>4. Expor métricas Prometheus de um job</h3>"
                    "<pre><code># pip install prometheus-client\n"
                    "from prometheus_client import Counter, Histogram, start_http_server\n"
                    "import time, random\n\n"
                    "deploys = Counter(\"deploys_total\", \"Total de deploys\", [\"env\", \"status\"])\n"
                    "durations = Histogram(\"deploy_duration_seconds\", \"Duração de deploys\")\n\n"
                    "start_http_server(9090)        # /metrics\n\n"
                    "while True:\n"
                    "    env = random.choice([\"dev\", \"prod\"])\n"
                    "    with durations.time():\n"
                    "        time.sleep(random.uniform(0.1, 1.0))\n"
                    "    deploys.labels(env=env, status=\"success\").inc()</code></pre>"
                    "<p>O endpoint <code>/metrics</code> fica em formato Prometheus, "
                    "configure scrape no Prometheus e métricas customizadas viram "
                    "alertas e dashboards.</p>"

                    "<h3>5. Pushgateway para batch jobs</h3>"
                    "<p>Jobs que rodam e morrem (cron, K8s Job) não têm como ser "
                    "scrapeados. Empurre para Pushgateway:</p>"
                    "<pre><code>from prometheus_client import CollectorRegistry, Gauge, push_to_gateway\n\n"
                    "reg = CollectorRegistry()\n"
                    "g = Gauge(\"backup_last_success_unix\", \"Timestamp do último backup\", registry=reg)\n"
                    "g.set_to_current_time()\n"
                    "push_to_gateway(\"pushgateway:9091\", job=\"daily_backup\", registry=reg)</code></pre>"

                    "<h3>6. Construindo um CI step custom: scan de licenças</h3>"
                    "<p>Caso real: uma policy proíbe libs com licença GPL. Vamos "
                    "construir o step:</p>"
                    "<pre><code>import json, subprocess, sys\n\n"
                    "BLOCKED = {\"GPL-3.0\", \"GPL-2.0\", \"AGPL-3.0\"}\n\n"
                    "out = subprocess.run([\n"
                    "    \"uv\", \"pip\", \"list\", \"--format\", \"json\"\n"
                    "], capture_output=True, text=True, check=True)\n"
                    "pkgs = json.loads(out.stdout)\n\n"
                    "violations = []\n"
                    "for p in pkgs:\n"
                    "    meta = subprocess.run([\"pip\", \"show\", p[\"name\"]],\n"
                    "                          capture_output=True, text=True, check=True).stdout\n"
                    "    license_line = next((l for l in meta.splitlines() if l.startswith(\"License:\")), \"\")\n"
                    "    lic = license_line.replace(\"License:\", \"\").strip()\n"
                    "    if lic in BLOCKED:\n"
                    "        violations.append((p[\"name\"], lic))\n\n"
                    "if violations:\n"
                    "    for n, lic in violations:\n"
                    "        print(f\"::error:: {n} usa licença bloqueada {lic}\", file=sys.stderr)\n"
                    "    sys.exit(1)\n"
                    "print(\"OK, nenhuma licença bloqueada.\")</code></pre>"
                    "<p>Em GitHub Actions, <code>::error::</code> vira annotation no "
                    "PR. GitLab tem syntax similar.</p>"

                    "<h3>7. Notificação no Slack quando algo dá errado</h3>"
                    "<pre><code>import os, requests\n\n"
                    "def slack_alert(text: str, channel: str = \"#alerts\"):\n"
                    "    url = os.environ[\"SLACK_WEBHOOK_URL\"]\n"
                    "    r = requests.post(url, json={\"text\": text, \"channel\": channel}, timeout=5)\n"
                    "    r.raise_for_status()\n\n"
                    "try:\n"
                    "    deploy_to_prod()\n"
                    "except Exception as e:\n"
                    "    slack_alert(f\":rotating_light: Deploy falhou: `{e}`\")\n"
                    "    raise</code></pre>"

                    "<h3>8. Operadores personalizados (kopf)</h3>"
                    "<p>Quando você precisa de um controller K8s próprio "
                    "(ex: criar buckets S3 a partir de um CRD), "
                    "<code>kopf</code> simplifica:</p>"
                    "<pre><code># pip install kopf\n"
                    "import kopf\n\n"
                    "@kopf.on.create(\"example.com\", \"v1\", \"buckets\")\n"
                    "def create_bucket(spec, name, **kwargs):\n"
                    "    boto3.client(\"s3\").create_bucket(Bucket=spec[\"name\"])\n"
                    "    return {\"createdBucket\": spec[\"name\"]}\n\n"
                    "@kopf.on.delete(\"example.com\", \"v1\", \"buckets\")\n"
                    "def delete_bucket(spec, **kwargs):\n"
                    "    boto3.client(\"s3\").delete_bucket(Bucket=spec[\"name\"])</code></pre>"

                    "<h3>9. Boas práticas para ferramentas DevSecOps em Python</h3>"
                    "<ul>"
                    "<li>Saída em JSON quando o consumidor é máquina; legível para humanos.</li>"
                    "<li>Códigos de saída específicos (deploy 0, validation 65, network 69).</li>"
                    "<li>Logue o comando exato e parâmetros, auditoria gratuita.</li>"
                    "<li>Idempotência: rodar duas vezes não deve causar problema (verifique antes de criar).</li>"
                    "<li>Suporte a <code>--dry-run</code> em qualquer ferramenta destrutiva.</li>"
                    "<li>Não armazene credenciais em log/output. Censure: "
                    "<code>token[:4] + '***'</code>.</li>"
                    "<li>Tempos de execução em métrica (Histogram). Se a média sobe, há "
                    "regressão, mesmo sem erro.</li>"
                    "</ul>"
                ),
                "practical": (
                    "Construa <code>license_gate.py</code> que: (1) percorre "
                    "<code>uv.lock</code> ou <code>pyproject.toml</code> do projeto; "
                    "(2) consulta a API do <a href=\"https://pypi.org\">PyPI JSON</a> "
                    "para cada lib (<code>https://pypi.org/pypi/&lt;name&gt;/json</code>); "
                    "(3) extrai a licença e bloqueia se estiver na lista negra "
                    "(<code>GPL-*</code>, <code>AGPL-*</code>); (4) emite "
                    "<code>::error::</code> no formato GitHub Actions e exit code 1 se "
                    "houver violações; (5) tem flag <code>--allow-list path</code> "
                    "para sobrescrever defaults."
                ),
            },
            "materials": [
                m("boto3 documentation",
                  "https://boto3.amazonaws.com/v1/documentation/api/latest/index.html",
                  "docs", "SDK oficial AWS para Python."),
                m("kubernetes Python client",
                  "https://github.com/kubernetes-client/python",
                  "docs", "Cliente oficial do K8s para Python."),
                m("prometheus-client",
                  "https://github.com/prometheus/client_python",
                  "docs", "Lib para expor métricas Prometheus."),
                m("Pushgateway",
                  "https://github.com/prometheus/pushgateway",
                  "docs", "Coletor para batch jobs."),
                m("kopf, Kubernetes Operators in Python",
                  "https://kopf.readthedocs.io/",
                  "docs", "Framework para operadores K8s."),
                m("AWS Well-Architected, Python on Lambda",
                  "https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html",
                  "docs", "Práticas de Python em Lambda."),
            ],
            "questions": [
                q("Qual o jeito recomendado de autenticar boto3 em uma EC2 da própria AWS?",
                  "Anexar um IAM Role à instância, o SDK pega credenciais via IMDS automaticamente.",
                  ["Hardcoded em config.py.",
                   "Variáveis de ambiente em /etc/environment.",
                   "OIDC com Vault (sempre)."],
                  "IAM Role + IMDSv2 é a forma segura. Sem credenciais persistidas, "
                  "sem rotação manual."),
                q("`config.load_incluster_config()` falha quando rodando localmente. Como tratar?",
                  "Tentar primeiro e cair para `load_kube_config()` em ConfigException.",
                  ["Sempre usar load_kube_config().",
                   "Forçar variável KUBECONFIG.",
                   "Não há jeito, precisa de container."],
                  "Padrão clássico: tenta in-cluster (vê /var/run/secrets/...); "
                  "se não, usa kubeconfig local. Mesma ferramenta funciona em ambos "
                  "contextos."),
                q("Para um job batch que termina, expor métricas Prometheus como?",
                  "Empurrar para Pushgateway com push_to_gateway.",
                  ["Iniciar um servidor HTTP que fica de pé.",
                   "Salvar em arquivo .prom.",
                   "Não dá para coletar."],
                  "Pushgateway armazena temporariamente as métricas para Prometheus "
                  "scrape. É o padrão para jobs efêmeros."),
                q("Para listar todos os objetos de um bucket S3 grande:",
                  "client.get_paginator('list_objects_v2').paginate(Bucket=name)",
                  ["client.list_objects(Bucket=name) (sempre completo).",
                   "boto3.list_all().",
                   "ec2.objects.all()."],
                  "list_objects_v2 retorna 1000 itens por página. Paginator itera "
                  "automaticamente todas as páginas."),
                q("`subprocess.run([..., 'aws', 's3', 'cp', ...])` vs. boto3, qual a vantagem do boto3?",
                  "Type-safe, tratamento de erros pythonic, sem dependência do CLI instalado.",
                  ["É sempre mais rápido.",
                   "Funciona offline.",
                   "Não requer credenciais."],
                  "boto3 retorna dicts e levanta exceções tipadas. subprocess depende "
                  "do CLI estar no PATH e tem overhead de serialização JSON."),
                q("Para reagir a eventos em tempo real no K8s, use:",
                  "kubernetes.watch.Watch().stream(...)",
                  ["Polling com sleep(60).",
                   "Não há jeito, só CLI.",
                   "ETag manual."],
                  "Watch usa long-polling do API Server: receberia eventos imediatos. "
                  "Polling é desperdício de quota e atrasa reação."),
                q("Em uma ferramenta de CI, a saída idealmente vai em JSON quando:",
                  "O consumidor é outra ferramenta (script, pipeline).",
                  ["Sempre.",
                   "Apenas em produção.",
                   "Apenas se houver erro."],
                  "Humanos preferem texto formatado; máquinas preferem JSON. Idiomático: "
                  "flag --json para alternar."),
                q("`::error file=app.py,line=10::Erro X` em GitHub Actions...",
                  "Cria uma annotation no arquivo/linha indicado no PR.",
                  ["É um print colorido.",
                   "Faz a action falhar automaticamente.",
                   "É comentário ignorado."],
                  "Workflow commands. ::error gera annotation; ::warning idem; "
                  "::set-output (deprecado em favor de $GITHUB_OUTPUT)."),
                q("Boa prática para ferramentas destrutivas (delete, drop):",
                  "Implementar --dry-run que mostra o que faria sem executar.",
                  ["Pedir senha em todo run.",
                   "Logar em produção apenas.",
                   "Fazer rollback automático sempre."],
                  "Dry-run é o equivalente de `terraform plan`. Permite revisar antes "
                  "de aplicar; vital para evitar erros operacionais."),
                q("Idempotência em scripts DevOps significa:",
                  "Rodar o mesmo script várias vezes leva ao mesmo estado, sem efeitos colaterais extras.",
                  ["Ele só roda uma vez.",
                   "Tem retry interno.",
                   "Não usa I/O."],
                  "Ex: 'criar bucket' deveria checar se existe primeiro. Idempotência "
                  "é base de Ansible, Terraform e bons pipelines de deploy."),
            ],
        },
    ],
}
