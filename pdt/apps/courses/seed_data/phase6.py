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
                """<h3>1. Tipos primitivos e o modelo de objeto que explica tudo</h3>
<p>Em Python, <strong>tudo é objeto</strong> — inteiros, strings, funções e
classes têm igualmente atributos e métodos, e são todos alocados no heap e
referenciados por nome. Essa uniformidade é o que torna Python tão
flexível (você pode passar uma função como argumento do mesmo jeito que
passa um número) e é também a raiz de comportamentos que surpreendem quem
vem de linguagens com tipos primitivos "de verdade" (seção 2).</p>
<div class="mermaid">
flowchart LR
    A["def f(x=[])"] --> B["Lista criada uma vez, na definição"]
    B --> C["Toda chamada sem argumento reusa a MESMA lista"]
    C --> D["Estado vaza entre chamadas"]
</div>

<pre><code>x: int   = 42
y: float = 3.14
s: str   = "hello"
b: bool  = True
n: None  = None  # type literal None == NoneType
lst: list[int]      = [1, 2, 3]
tup: tuple[int, str] = (1, "a")
st:  set[str]       = {"a", "b"}
d:   dict[str, int] = {"k": 1}</code></pre>
<p>A diferença entre <code>list</code> e <code>tuple</code> não é só
sintática: <code>tuple</code> é imutável, e por ser imutável é
<em>hashable</em> — pode virar chave de dicionário ou item de um
<code>set</code>. <code>list</code> não pode, porque seu conteúdo pode
mudar depois de inserida, o que quebraria a estrutura de hash que já
calculou uma posição para ela. Pelo mesmo motivo, <code>str</code> é
imutável: toda operação que "modifica" uma string na verdade cria uma
string nova. Isso tem um custo real — concatenar em loop com
<code>+=</code> aloca uma string nova a cada iteração, um comportamento
O(n²) para n concatenações; <code>"".join(lista)</code> aloca uma vez só,
O(n).</p>

<h3>2. Variáveis são nomes, não caixas: por que atribuição não copia</h3>
<p>Quem vem de linguagens onde variável é uma "caixa com valor" leva um
susto na primeira vez que isso acontece:</p>
<pre><code>a = [1, 2, 3]
b = a               # b aponta para o MESMO objeto
b.append(4)
print(a)            # [1, 2, 3, 4]  ← surpresa para iniciantes

import copy
c = copy.copy(a)        # cópia rasa
d = copy.deepcopy(a)    # cópia profunda</code></pre>
<p>Em Python, uma variável é só um NOME apontando para um objeto que existe
independente dela. <code>b = a</code> não copia o conteúdo — cria um
segundo nome apontando para o mesmo objeto na memória. Modificar o objeto
por qualquer um dos dois nomes afeta o que o outro nome "vê", porque não
há dois objetos, há um só com dois rótulos. Isso só surpreende com objetos
MUTÁVEIS (listas, dicts); com <code>int</code> ou <code>str</code>
(imutáveis) o efeito nunca aparece, porque qualquer "modificação"
já cria um objeto novo em vez de alterar o existente — daí a confusão de
quem só testou com números antes de testar com listas.</p>
<p>Escopo de nome segue a regra <strong>LEGB</strong>: Local → Enclosing →
Global → Built-in — o interpretador procura nessa ordem até achar o nome.
Para ESCREVER (não só ler) num escopo externo de dentro de uma função,
você precisa de <code>global</code> ou <code>nonlocal</code> explícito;
sem isso, uma atribuição dentro da função sempre cria uma variável LOCAL
nova, mesmo que exista um nome igual fora — um dos erros mais comuns e
mais confusos para quem começa (a função parece "não enxergar" a
variável externa, quando na verdade criou uma sombra local dela).</p>

<h3>3. `for` itera sobre iteráveis, não sobre posições</h3>
<pre><code>servers = ["web1", "web2", "db1"]
ports   = [80, 80, 5432]

for i, name in enumerate(servers, start=1):
    print(f"#{i} {name}")

for name, port in zip(servers, ports, strict=True):
    print(f"{name} :{port}")</code></pre>
<p><code>for i in range(len(lista)): item = lista[i]</code> funciona, mas
reimplementa manualmente o que <code>enumerate</code> já faz — e sinaliza
para quem lê o código que talvez você não conheça o idioma da linguagem, o
que gera desconfiança sobre o resto do código também. <code>zip(...,
strict=True)</code> (3.10+) é o detalhe que vale conhecer: sem
<code>strict</code>, zipar duas listas de tamanhos diferentes trunca
silenciosamente na mais curta — um bug de "por que só processei metade dos
servidores" que não gera nenhum erro, só resultado incompleto.
<code>strict=True</code> levanta <code>ValueError</code> se os tamanhos
não baterem.</p>
<p><strong>Truthiness</strong>: em Python, <code>0</code>, <code>None</code>,
coleções vazias e <code>False</code> são todos <em>falsy</em> — não porque
sejam convertidos para booleano de alguma forma mágica, mas porque todo
objeto implementa (ou herda) um método <code>__bool__</code> ou
<code>__len__</code> que decide isso. <code>if len(lst) &gt; 0:</code>
funciona, mas <code>if lst:</code> usa exatamente esse mecanismo e é o
idioma esperado. Comparar com <code>True</code>/<code>False</code>
explicitamente (<code>if x == True</code>) é redundante e frágil: prefira
<code>if x:</code>, e para <code>None</code> especificamente use
<code>is None</code> — comparação de identidade, não de valor, porque
existe exatamente UM objeto <code>None</code> na memória inteira do
processo.</p>

<h3>4. `match`: destructuring estrutural, não um switch disfarçado</h3>
<p>Quem vê <code>match</code> pela primeira vez tende a tratá-lo como um
<code>switch</code> de C — mas ele faz muito mais: cada <code>case</code>
tenta DESESTRUTURAR o valor contra um padrão, extraindo variáveis no
processo, não só comparar igualdade:</p>
<pre><code>def handle(event: dict) -&gt; str:
    match event:
        case {"type": "deploy", "env": "prod", "image": img}:
            return f"PROD deploy: {img}"
        case {"type": "deploy", "env": env}:
            return f"{env} deploy"
        case {"type": "rollback", "version": v} if v &lt; 10:
            return f"rollback recente para {v}"
        case _:
            return "unknown"</code></pre>
<p>O primeiro <code>case</code> só casa se o dict tiver EXATAMENTE
<code>type="deploy"</code> e <code>env="prod"</code>, e nesse casamento já
extrai <code>img</code> como variável local — sem esse recurso, você
escreveria três <code>if</code> aninhados checando cada chave manualmente.
A cláusula <code>if v &lt; 10</code> no terceiro caso (um "guard") permite
condição adicional além do formato. É o padrão certo para parsear payloads
de webhook, eventos de fila (SQS, Pub/Sub) ou CloudEvents, onde a forma do
JSON varia conforme o tipo de evento.</p>

<h3>5. Funções: por que `*` existe e por que default mutável é uma armadilha</h3>
<pre><code>def deploy(
    image: str,                       # posicional
    *,                                # tudo depois é keyword-only
    replicas: int = 3,
    canary: bool = False,
    extra_env: dict[str, str] | None = None,
) -&gt; bool:
    ...

deploy("web:1.2", replicas=5, canary=True)</code></pre>
<p>O <code>*</code> sozinho na assinatura não recebe nada — é um marcador:
tudo que vem depois só pode ser passado por nome na chamada. Sem ele,
<code>deploy("web", 5, True)</code> compilaria e rodaria, mas ninguém lendo
essa chamada sabe o que "5" e "True" significam sem ir checar a
assinatura; forçar keyword-only nesses casos transforma a chamada em
autodocumentada.</p>
<p>O bug mais citado da linguagem é <code>def f(x=[]):</code>. O valor
default de um parâmetro é avaliado UMA VEZ, no momento em que a função é
definida (não a cada chamada) — então aquela lista vazia é criada uma
única vez e reutilizada como o MESMO objeto em toda chamada subsequente
que não passar <code>x</code> explicitamente. Se uma chamada faz
<code>x.append(1)</code>, a próxima chamada sem argumento recebe a lista já
com aquele item, um vazamento de estado entre chamadas completamente
invisível no código de quem só olha a assinatura. O idioma correto é
<code>def f(x=None): x = x if x is not None else []</code>, criando a lista
nova a cada chamada de verdade.</p>

<h3>6. Type hints: contrato para ferramentas, não para o interpretador</h3>
<p>Anotações de tipo NÃO mudam o comportamento em runtime — Python
continua dinamicamente tipado, e nada impede de fato passar uma string
onde a assinatura pede um <code>int</code>. O valor está inteiro nas
ferramentas que leem essas anotações sem executar o código: mypy/pyright
pegam a incompatibilidade de tipo na revisão (antes de rodar um teste
sequer), o editor ganha autocomplete real baseado em tipo, e a assinatura
vira documentação que não pode ficar desatualizada silenciosamente, porque
o type checker reclama se ela mentir.</p>
<pre><code>from typing import Iterable, Protocol

def total(items: Iterable[float]) -&gt; float:
    return sum(items)

class Storer(Protocol):
    def save(self, key: str, blob: bytes) -&gt; None: ...

def upload(s: Storer, k: str, b: bytes) -&gt; None:
    s.save(k, b)   # qualquer classe com .save() compatível serve</code></pre>
<p><code>Protocol</code> é tipagem estrutural — <code>upload</code> aceita
QUALQUER objeto que tenha um método <code>save(key, blob)</code> com essa
assinatura, sem precisar herdar de <code>Storer</code> explicitamente
("se anda como pato..."). Útil para desacoplar código de uma implementação
concreta (um cliente S3, um cliente de disco local) sem herança forçada.
Em 3.10+, prefira <code>X | Y</code> a <code>Union[X, Y]</code> e
<code>list[int]</code> a <code>List[int]</code> — sintaxe nativa, sem
import extra de <code>typing</code>.</p>

<h3>7. F-strings: formatação e o motivo de evitá-las em log</h3>
<pre><code>name, port = "web", 80
print(f"{name}:{port}")             # web:80
print(f"{name:&gt;10}|{port:05d}")    # padding e zero-pad
print(f"{3.14159:.2f}")             # 3.14
print(f"{name=}, {port=}")           # debug: name='web', port=80</code></pre>
<p>F-strings são avaliadas IMEDIATAMENTE, no ponto em que a linha executa
— é por isso que <code>logger.info(f"deploying {name}")</code> é uma
prática desaconselhada: a interpolação (formatar a string) acontece
sempre, mesmo se o nível de log DEBUG/INFO estiver desativado e a mensagem
for descartada sem nunca ser escrita. <code>logger.info("deploying %s",
name)</code> passa os argumentos separados, e o logging só formata a
string se realmente for emitir o log — economia real de CPU em sistemas
que geram muitos logs de debug desligados em produção.</p>

<h3>8. Erros clássicos de quem vem de outra linguagem</h3>
<ul>
<li>Comparar floats com <code>==</code>: ponto flutuante tem erro de
arredondamento (<code>0.1 + 0.2 != 0.3</code> em Python, como na maioria
das linguagens); use <code>math.isclose()</code>.</li>
<li>Confundir <code>is</code> com <code>==</code>: <code>is</code> compara
IDENTIDADE (é o mesmo objeto na memória?), <code>==</code> compara VALOR
(chama <code>__eq__</code>). Dois objetos podem ter o mesmo valor sem
serem o mesmo objeto.</li>
<li>Usar <code>type(x) == int</code> em vez de <code>isinstance(x, int)</code>:
o primeiro rejeita subclasses de <code>int</code>; o segundo as aceita —
importante em código que recebe objetos de bibliotecas que podem
subclassificar tipos built-in.</li>
<li>Não usar context managers: arquivos, locks e conexões abertos sem
<code>with</code> ficam dependendo do garbage collector para fechar — em
processos de longa duração (um daemon, um servidor), isso vaza descritores
de arquivo até o processo cair.</li>
</ul>"""
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
                  ["Torna os parâmetros seguintes opcionais, com valor default implícito.", "Recebe qualquer argumento extra passado como uma tupla.", "Gera um erro de sintaxe assim que o código é interpretado."],
                  "O `*` sozinho marca o limite: tudo depois precisa ser nomeado na chamada. "
                  "`*args` (com nome) é diferente, captura posicionais extras."),
                q("Por que `def f(x=[]):` é considerado um bug latente?",
                  "A lista default é compartilhada entre todas as chamadas e pode acumular estado.",
                  ["Isso só passa a causar um erro de sintaxe a partir da versão 3.10 do interpretador.", "O Python impede completamente qualquer valor mutável usado como argumento default.", "É só uma preferência de estilo de código, sem qualquer efeito real no comportamento."],
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
                  ["O operador `==` costuma ser bem mais lento de executar do que o `is` na prática.", "Os dois operadores fazem exatamente a mesma comparação, sem diferença alguma entre eles.", "O operador `is` só funciona de forma correta quando comparando números inteiros pequenos."],
                  "Use `is` para comparar com `None`, `True`, `False`. Para igualdade "
                  "de valor use `==`."),
                q("O que `f\"{x=}\"` produz se x = 42?",
                  "x=42",
                  ["42", "x", "{x: 42}"],
                  "Sintaxe de debug das f-strings (3.8+): inclui o nome da variável "
                  "seguido do valor, útil pra logs rápidos."),
                q("Como concatenar muitas strings com performance O(n)?",
                  "\"\".join(lista_de_strings)",
                  ["str1 + str2 + str3 + str4 + ...", "operator.concat(str1, str2, str3)", "resultado += item for item in lista"],
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
                """<h3>1. Listas, tuplas, sets, dicts: a mesma escolha que decide performance</h3>
<table>
<thead><tr><th>Estrutura</th><th>Acesso</th><th>Mutável</th>
<th>Caso típico</th></tr></thead>
<tbody>
<tr><td><code>list</code></td><td>O(1) por índice</td><td>Sim</td>
<td>Coleção ordenada, fila de tarefas, batch.</td></tr>
<tr><td><code>tuple</code></td><td>O(1) por índice</td><td>Não</td>
<td>Registro fixo (lat, lng), retorno múltiplo.</td></tr>
<tr><td><code>set</code></td><td>O(1) <em>in</em></td><td>Sim</td>
<td>Deduplicação, testes de pertencimento.</td></tr>
<tr><td><code>dict</code></td><td>O(1) por chave</td><td>Sim</td>
<td>Mapeamento, contadores, configs.</td></tr>
</tbody></table>
<p>O que faz <code>list</code> e <code>dict</code>/<code>set</code>
divergirem tanto em desempenho para busca é a estrutura por baixo:
<code>list</code> é um array contíguo, então achar um item exige
percorrer posição por posição (O(n)) até encontrar ou chegar ao fim; dict
e set usam tabela hash, calculam a posição do item direto a partir do seu
hash (O(1) esperado), sem percorrer nada. Na prática: qualquer
<code>x in colecao</code> dentro de um loop que roda muitas vezes é
candidato imediato a virar <code>set</code> — a mudança de O(n²) total
para O(n) num laço de milhares de itens é a diferença entre milissegundos
e minutos.</p>
<div class="mermaid">
flowchart LR
    A["Lista: colchetes"] --> B["Carrega tudo na memória de uma vez"]
    C["Generator: parênteses"] --> D["Produz um item por vez, sob demanda"]
</div>


<h3>2. Comprehensions: por que a versão "curta" também é mais rápida</h3>
<pre><code># list
ips = [host["ip"] for host in hosts if host["alive"]]

# dict
by_name = {h["name"]: h for h in hosts}

# set
unique_envs = {h["env"] for h in hosts}

# generator (lazy)
total = sum(h["cpu"] for h in hosts)</code></pre>
<p>Comprehension não é só sintaxe compacta: o laço explícito
<code>for item in x: resultado.append(f(item))</code> faz uma chamada de
método (<code>.append</code>) por iteração, resolvida em Python puro; a
comprehension é compilada para um bytecode dedicado que evita essa
chamada repetida, executando mais perto do C internamente — o ganho de
velocidade é real, não só estético. O limite é legibilidade: uma
comprehension aninhada com dois filtros já é mais difícil de ler que um
<code>for</code> equivalente, e nesse ponto a "elegância" vira o oposto —
código que exige reler duas vezes para entender o que filtra e o que
transforma. Para acumulação com efeito colateral (gravar em log, escrever
no banco a cada item), use loop normal: o valor de uma comprehension é a
lista que ela produz, e usá-la só pelo efeito colateral descartando o
resultado confunde quem lê o motivo dela existir.</p>

<h3>3. Generators: por que "não carrega tudo em memória" é literal</h3>
<pre><code>def parse_log(path: str):
    with open(path) as f:
        for line in f:
            if "ERROR" in line:
                yield line.strip()

for err in parse_log("/var/log/app.log"):
    print(err)</code></pre>
<p>Uma função com <code>yield</code> não roda quando chamada — chamar
<code>parse_log(path)</code> devolve um objeto generator, e o CORPO da
função só avança até o próximo <code>yield</code> quando alguém pede o
próximo item (via <code>for</code>, <code>next()</code>, etc.). É por
isso que um arquivo de 50 GB pode ser processado assim mantendo só UMA
linha na memória por vez: o generator nunca materializa a lista inteira,
processa e descarta linha a linha conforme o consumidor avança.</p>
<pre><code>errors = (line for line in open("app.log") if "ERROR" in line)
first_5 = list(itertools.islice(errors, 5))</code></pre>
<p>A expressão geradora (parênteses em vez de colchetes) tem exatamente a
mesma economia de memória de uma função com <code>yield</code>, útil
quando o pipeline cabe numa linha.</p>

<h3>4. `collections`: nomes que resolvem padrões que todo mundo reinventa</h3>
<pre><code>from collections import Counter, defaultdict, deque, namedtuple, OrderedDict

# Counter, conta ocorrências em uma linha
c = Counter(line.split()[0] for line in open("access.log"))
c.most_common(10)        # top 10 IPs

# defaultdict, sem precisar checar 'if key not in d'
by_status = defaultdict(list)
for req in requests:
    by_status[req.status].append(req)

# deque, fila com pop/append O(1) em ambas pontas
rolling = deque(maxlen=100)   # janela deslizante
for v in stream: rolling.append(v)

# namedtuple, registro imutável com nomes
Host = namedtuple("Host", ["name", "ip", "port"])
h = Host("web1", "10.0.1.5", 80)
print(h.ip)</code></pre>
<p><code>defaultdict</code> não é mágica: ao acessar uma chave ausente, ela
chama a factory (<code>list</code>, <code>int</code>, o que você passar) e
INSERE o resultado no dict antes de devolvê-lo — é por isso que checar
<code>len(by_status)</code> depois de só LER uma chave inexistente pode
mostrar uma entrada a mais do que você esperava, uma pegadinha comum. Já
<code>deque</code> resolve um problema de desempenho que uma lista comum
tem escondido: <code>list.pop(0)</code> (remover do início) é O(n) porque
todo o resto do array precisa deslocar uma posição; <code>deque</code> é
implementada como lista duplamente encadeada por blocos, com O(1) em
ambas as pontas — essencial para filas e janelas deslizantes de tamanho
fixo (<code>maxlen</code> descarta o item mais antigo automaticamente).</p>

<h3>5. `itertools`: combinar iteráveis sem nunca materializar a combinação</h3>
<pre><code>import itertools as it

# chain: concatenar iteráveis
for x in it.chain(list_a, list_b, list_c): ...

# groupby: agrupa adjacentes (precisa estar ordenado)
logs.sort(key=lambda l: l.host)
for host, entries in it.groupby(logs, key=lambda l: l.host):
    print(host, sum(1 for _ in entries))

# product: produto cartesiano
for env, region in it.product(["dev","prod"], ["us-east","sa-east"]):
    deploy(env, region)

# islice: paginação
page = list(it.islice(big_iter, 100, 200))   # itens 100..199</code></pre>
<p>O detalhe que pega quem usa <code>groupby</code> pela primeira vez:
ele só agrupa itens ADJACENTES com a mesma chave — não agrupa a coleção
inteira por chave como um <code>defaultdict</code> faria. Por isso o
<code>logs.sort(...)</code> antes é obrigatório: sem ordenar primeiro, o
mesmo host aparecendo em duas posições não-adjacentes vira dois grupos
separados, um bug silencioso (o código roda, só produz contagens erradas)
fácil de não perceber até alguém comparar com o total esperado.</p>

<h3>6. `dataclasses`: registros com igualdade e repr de graça</h3>
<pre><code>from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class Host:
    name: str
    ip: str
    port: int = 22
    tags: tuple[str, ...] = ()

h = Host("web1", "10.0.1.5", tags=("prod", "web"))
# __init__, __repr__, __eq__ gerados automaticamente
# frozen=True torna imutável (hashable)
# slots=True economiza memória (sem __dict__)</code></pre>
<p>Sem <code>@dataclass</code>, uma classe de dados pura ainda precisa de
<code>__init__</code> escrito à mão (atribuindo cada campo), e sem
<code>__eq__</code> dois objetos com os MESMOS valores comparam como
diferentes (comparação de identidade padrão), o que costuma surpreender
em teste ("por que <code>Host(...) == Host(...)</code> deu False?").
<code>slots=True</code> resolve um custo escondido: por padrão toda
instância Python carrega um <code>__dict__</code> interno para permitir
atributos dinâmicos — <code>slots</code> elimina esse dicionário e
declara os atributos de antemão, economizando memória real quando você
cria milhares de instâncias (um registro por linha de log, por exemplo).
Para validação automática de tipo em runtime (rejeitar
<code>port="oitenta"</code> na criação) e serialização para JSON,
Pydantic v2 estende essa mesma ideia com verificação ativa.</p>

<h3>7. Slicing e desempacotamento: os idiomas que substituem laços inteiros</h3>
<pre><code>lst = [10, 20, 30, 40, 50]
lst[1:3]      # [20, 30]
lst[::2]      # [10, 30, 50], step 2
lst[::-1]     # [50, 40, 30, 20, 10], invertido

# Desempacotamento estendido
first, *middle, last = lst
# first=10, middle=[20,30,40], last=50

# Em dicts (3.5+)
merged = {**defaults, **user_overrides, "build": 42}</code></pre>
<p><code>{**a, **b}</code> resolve conflito de chave por ORDEM de
aparição: se a mesma chave existe em <code>a</code> e <code>b</code>, o
valor de <code>b</code> vence — porque o dict resultante é construído
inserindo as chaves de <code>a</code> primeiro e depois as de
<code>b</code>, e inserir de novo uma chave existente sobrescreve.
É o padrão idiomático para "config default + override do usuário",
DESDE que o override venha depois no merge — inverter a ordem inverte
qual lado ganha, um erro sutil de copiar o padrão sem pensar em qual
dict deveria prevalecer.</p>

<h3>8. `enum.Enum`/`StrEnum`: eliminar o typo que o interpretador não pega</h3>
<pre><code>from enum import StrEnum, auto

class Severity(StrEnum):
    INFO  = "info"
    WARN  = "warn"
    ERROR = "error"
    CRIT  = auto()

if level &gt;= Severity.WARN:   # comparações como string
    alert(level)</code></pre>
<p>Uma "magic string" como <code>"eror"</code> (com erro de digitação)
passa despercebida até o runtime — e às vezes nem aí, se a comparação
simplesmente nunca casar e o código seguir por um caminho errado sem
levantar exceção nenhuma. Um <code>Enum</code> transforma esse erro num
<code>AttributeError</code> imediato (<code>Severity.EROR</code> não
existe) já na revisão de código ou no primeiro type-check — o erro migra
de "silencioso em produção" para "óbvio antes de commitar".
<code>StrEnum</code> (3.11+) especificamente permite comparar e formatar
os valores como string normal, útil quando o valor precisa ir para um
log ou JSON sem conversão extra.</p>

<h3>9. Caso real: um pipeline de log que nunca carrega o arquivo inteiro</h3>
<pre><code>from collections import Counter
import itertools as it, gzip, re

PAT = re.compile(r'^(\\S+) .* "(\\w+) (\\S+) HTTP/.*" (\\d+)')

def open_log(p):
    return gzip.open(p, 'rt') if p.endswith('.gz') else open(p)

def lines(paths):
    for p in paths:
        with open_log(p) as f:
            yield from f

def parsed(lines):
    for ln in lines:
        if (m := PAT.match(ln)):
            yield m.group(1), m.group(2), m.group(3), int(m.group(4))

files = ["a.log", "b.log.gz", "c.log"]
errors = (r for r in parsed(lines(files)) if r[3] &gt;= 500)
top = Counter(r[0] for r in it.islice(errors, 10000)).most_common(5)
print(top)</code></pre>
<p>Todo elo dessa cadeia é lazy: <code>lines()</code> abre um arquivo por
vez e só lê a próxima linha quando pedida (via <code>yield from</code>,
que repassa a iteração para o generator interno sem materializar nada);
<code>parsed()</code> processa uma linha por vez; a expressão geradora
<code>errors</code> filtra sem gerar lista intermediária. Nenhum ponto
dessa cadeia carrega mais de uma linha na memória — é o motivo pelo qual
esse padrão processa gigabytes de log com uso de memória constante e
minúsculo, o oposto de <code>lines = open(f).readlines()</code>, que
materializaria o arquivo inteiro de uma vez antes de processar qualquer
coisa.</p>"""
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
                  ["Comprimem automaticamente os dados armazenados em memória.", "Aproveitam múltiplas threads automaticamente para acelerar o processamento.", "Costumam ser mais rápidos que uma lista em qualquer cenário."],
                  "Memória constante: você processa um arquivo de 50 GB com poucos KB "
                  "de RAM."),
                q("O que `Counter([\"a\",\"b\",\"a\"]).most_common(1)` retorna?",
                  "[('a', 2)]",
                  ["{'a': 2, 'b': 1}", "['a']", "2"],
                  "Counter é um dict que mapeia item→contagem; `most_common(n)` retorna "
                  "lista de tuplas ordenadas por contagem decrescente."),
                q("Para que serve `defaultdict(list)`?",
                  "Cria um dict que retorna [] automaticamente para chaves inexistentes.",
                  ["Impõe um limite máximo para o número de itens guardados dentro do dict.", "Cria um dict que mantém automaticamente as chaves ordenadas em ordem alfabética.", "Combina o conteúdo de múltiplos dicts em paralelo usando várias threads."],
                  "Evita o padrão `if k not in d: d[k] = []`. Uma chave acessada que "
                  "não existe é criada com o valor default."),
                q("`@dataclass(frozen=True)` torna a classe...",
                  "Imutável e hashable (utilizável como chave de dict ou item de set).",
                  ["Compatível com o módulo pickle de forma obrigatória, sem qualquer exceção possível.", "Sincronizada automaticamente para permitir uso seguro entre múltiplas threads.", "Consideravelmente mais rápida em runtime do que uma classe comum equivalente."],
                  "frozen impede modificação após init e ativa __hash__ baseado nos "
                  "campos."),
                q("Qual a saída de `lst[::-1]` se lst = [1,2,3]?",
                  "[3, 2, 1]",
                  ["[1, 2, 3]", "[]", "[1]"],
                  "Slice com step -1 inverte a sequência. Atalho clássico para "
                  "reverter listas/strings."),
                q("Qual destas é uma DESVANTAGEM de comprehensions?",
                  "Ficam ilegíveis quando aninhadas profundamente ou com filtros complexos.",
                  ["Não conseguem incluir algum tipo de condicional dentro da própria expressão.", "Costumam rodar visivelmente mais devagar do que um loop for equivalente.", "Não podem ser combinadas de forma alguma com uma expressão geradora."],
                  "Performance é geralmente melhor que for+append. O risco é cognitivo: "
                  "comprehension de 4 linhas com 2 ifs é pior que loop explícito."),
                q("`{**a, **b}` quando há chaves repetidas...",
                  "Mantém o valor do último dict (b sobrescreve a).",
                  ["Soma automaticamente os valores das duas chaves repetidas.", "Levanta uma exceção KeyError assim que encontra a repetição.", "Mantém o valor do primeiro dict, ignorando o segundo (a vence)."],
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
                """<h3>1. Classes: `__init__` inicializa, não constrói</h3>
<pre><code>class Server:
    def __init__(self, name: str, ip: str, port: int = 22) -&gt; None:
        self.name = name
        self.ip   = ip
        self.port = port

    def url(self) -&gt; str:
        return f"ssh://{self.ip}:{self.port}"

s = Server("web1", "10.0.1.5")
print(s.url())</code></pre>
<p>A distinção entre <code>__new__</code> (constrói o objeto, aloca a
memória) e <code>__init__</code> (inicializa o que já foi alocado) raramente
importa no dia a dia — mas explica por que subclassificar tipos imutáveis
(<code>str</code>, <code>int</code>, <code>tuple</code>) exige sobrescrever
<code>__new__</code>: nessas classes o VALOR é fixado na construção, antes
de <code>__init__</code> rodar, então tentar mudar o valor em
<code>__init__</code> simplesmente não tem efeito. <code>self</code> é só
uma convenção de nome (o primeiro parâmetro de um método sempre recebe a
instância, chame-o do que quiser), mas quebrar essa convenção confunde
qualquer leitor treinado no idioma da linguagem. Para uma classe que só
guarda dados (sem lógica além de acessar campos), escrever
<code>__init__</code> e <code>__repr__</code> à mão é trabalho que
<code>@dataclass</code> (visto na aula anterior) já resolve.</p>
<div class="mermaid">
flowchart LR
    A["with obj as f"] --> B["obj.__enter__()"]
    B --> C["Bloco de código roda"]
    C --> D["obj.__exit__() roda sempre, mesmo com exceção"]
</div>


<h3>2. Atributo de classe vs. de instância: o bug que parece compartilhamento mágico</h3>
<pre><code>class Cache:
    DEFAULT_TTL = 60                  # atributo de classe (compartilhado)

    def __init__(self):
        self.store = {}               # atributo de instância (próprio)

Cache.DEFAULT_TTL = 120              # muda para todo mundo
Cache().DEFAULT_TTL = 30             # cria instância: shadow!</code></pre>
<p>Um atributo definido no corpo da classe (fora de <code>__init__</code>)
vive num único lugar — o objeto CLASSE, não em cada instância — e toda
instância que não tem um atributo com esse nome próprio "enxerga" o valor
da classe através dele. O erro mais citado da linguagem sai exatamente
daqui: <code>class Cache: items = []</code> cria UMA lista compartilhada
por todas as instâncias; <code>instancia.items.append(x)</code> modifica
essa lista única, então uma segunda instância criada depois já nasce
"vendo" os itens que a primeira inseriu — parece um bug de referência
compartilhada porque é exatamente isso. A correção é declarar
<code>self.items = []</code> dentro de <code>__init__</code>, criando uma
lista nova por instância.</p>

<h3>3. Herança e `super()`: reaproveitar comportamento sem reescrevê-lo</h3>
<pre><code>class HTTPError(Exception):
    pass

class RetryableHTTPError(HTTPError):
    def __init__(self, status: int, body: str):
        super().__init__(f"retryable {status}")
        self.status = status
        self.body   = body</code></pre>
<p><code>super().__init__(...)</code> chama o inicializador da classe PAI
antes de adicionar o comportamento próprio da subclasse — sem essa
chamada, o <code>Exception</code> base nunca recebe a mensagem, e
<code>str(erro)</code> viria vazio mesmo com <code>status</code> e
<code>body</code> preenchidos. Herança múltipla existe em Python e é
usada de forma legítima para mixins (uma classe pequena que só adiciona
um comportamento, como <code>LoggingMixin</code>, combinada com a classe
principal via <code>class Foo(LoggingMixin, Base):</code>) — mas
hierarquias profundas (herança de herança de herança) tornam difícil
saber de onde um método realmente vem, e a maioria dos designers de
API modernos prefere composição (uma classe que GUARDA outra como
atributo) a herança nesses casos.</p>

<h3>4. Dunder methods: o contrato que faz sua classe se comportar como as nativas</h3>
<table>
<thead><tr><th>Método</th><th>Para quê</th></tr></thead>
<tbody>
<tr><td><code>__repr__</code></td><td>Representação de debug. Sempre defina.</td></tr>
<tr><td><code>__str__</code></td><td>Para humanos (<code>str(x)</code>, <code>print</code>).</td></tr>
<tr><td><code>__eq__</code>, <code>__hash__</code></td><td>Igualdade e uso em set/dict.</td></tr>
<tr><td><code>__len__</code>, <code>__contains__</code>, <code>__iter__</code></td><td>Coleções customizadas.</td></tr>
<tr><td><code>__enter__</code>, <code>__exit__</code></td><td>Context manager (<code>with</code>).</td></tr>
<tr><td><code>__call__</code></td><td>Faz a instância ser chamável como função.</td></tr>
</tbody></table>
<p>Sem <code>__repr__</code>, imprimir um objeto no console ou num log
produz algo como <code>&lt;Server object at 0x7f...&gt;</code> — o
endereço de memória, zero informação útil para debugar. É a diferença
entre um log que diz o que quebrou e um que só diz "alguma coisa do tipo
Server quebrou em algum lugar". <code>__eq__</code> e <code>__hash__</code>
andam juntos por uma regra que a linguagem impõe: se você define
<code>__eq__</code> sem <code>__hash__</code>, a classe se torna
NÃO-hashable automaticamente (Python assume que objetos "iguais" por
valor não deveriam ter hashes diferentes, e por segurança desativa o hash
default) — um efeito colateral que quebra silenciosamente qualquer código
que tentasse usar essa classe como chave de dict ou item de set.</p>

<h3>5. Properties: quando um atributo devia ser uma função disfarçada</h3>
<pre><code>class Replica:
    def __init__(self, count: int):
        self._count = 0
        self.count = count   # passa pelo setter

    @property
    def count(self) -&gt; int:
        return self._count

    @count.setter
    def count(self, v: int) -&gt; None:
        if v &lt; 0 or v &gt; 100:
            raise ValueError(f"replicas {v} fora do range")
        self._count = v</code></pre>
<p>A vantagem de <code>@property</code> sobre um getter/setter explícito
(<code>get_count()</code>/<code>set_count()</code>, comum em outras
linguagens) é que o CÓDIGO CHAMADOR continua escrevendo
<code>replica.count = 200</code> — sintaxe de atributo comum — enquanto
por baixo roda a validação. Isso permite começar uma classe com atributo
público simples e, se um dia surgir a necessidade de validar ou calcular,
promover para property SEM quebrar quem já usa a classe (o código
chamador não muda uma linha). O erro comum é o oposto: criar property
para TODO atributo "por precaução", adicionando indireção onde não há
regra nenhuma para justificar.</p>

<h3>6. A hierarquia de exceções, e por que dois ramos são proibidos de capturar</h3>
<pre><code>BaseException
├── SystemExit         # sys.exit(), não capture genericamente
├── KeyboardInterrupt  # Ctrl+C, não capture genericamente
├── GeneratorExit
└── Exception          # ← capture este
    ├── ValueError
    ├── TypeError
    ├── KeyError
    ├── OSError
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   ├── ConnectionError
    │   └── TimeoutError
    └── ...</code></pre>
<p><code>SystemExit</code> e <code>KeyboardInterrupt</code> herdam de
<code>BaseException</code> diretamente, FORA da árvore de
<code>Exception</code> — uma decisão de design deliberada: um
<code>except Exception:</code> genérico não captura esses dois, então
<code>sys.exit()</code> e Ctrl+C continuam funcionando mesmo dentro de
código com tratamento de erro amplo. Um <code>except:</code> nu (sem tipo
nenhum) captura TUDO, inclusive esses dois — é por isso que ele é proibido
pelo PEP 8: um processo que deveria morrer com Ctrl+C simplesmente ignora
o sinal e continua rodando, exigindo <code>kill -9</code> para parar de
verdade. A regra prática é capturar o tipo MAIS ESPECÍFICO que você sabe
tratar, deixar o resto propagar, e usar <code>raise NovoErro(...) from
original</code> ao converter uma exceção de baixo nível numa exceção de
domínio — o traceback resultante mostra a cadeia completa ("a exceção
acima foi a causa direta de..."), em vez de esconder a causa raiz.</p>

<h3>7. `try/except/else/finally`: quatro blocos, quatro papéis diferentes</h3>
<pre><code>try:
    cfg = load_config(path)
except FileNotFoundError:
    cfg = default_config()
except OSError as e:
    log.error("erro de I/O", exc_info=e)
    raise
else:
    log.info("config carregada")    # só se NÃO houve exceção
finally:
    cleanup()                          # sempre roda</code></pre>
<p><code>else</code> só executa se o bloco <code>try</code> terminou SEM
levantar exceção — sua função é separar "o código que pode falhar" (dentro
do <code>try</code>) de "o que só deveria rodar se deu tudo certo" (no
<code>else</code>), evitando que uma exceção lançada acidentalmente pelo
código de sucesso seja capturada pelo <code>except</code> errado, como se
fosse um erro do <code>load_config</code>. <code>finally</code> roda
SEMPRE — com exceção, sem exceção, ou mesmo se um <code>return</code>
aconteceu dentro do <code>try</code> — o lugar certo para cleanup que não
pode ser pulado de jeito nenhum.</p>

<h3>8. Context managers: `with` como garantia, não como conveniência</h3>
<p>O padrão mais visto é <code>open()</code>:</p>
<pre><code>with open("/etc/passwd") as f:
    data = f.read()
# arquivo fechado AQUI, com ou sem exceção</code></pre>
<p>A garantia que <code>with</code> oferece é justamente essa: o método
<code>__exit__</code> do objeto roda MESMO que uma exceção estoure dentro
do bloco — algo que um <code>f.close()</code> escrito na linha seguinte ao
<code>open()</code> não garante, porque uma exceção no meio do caminho pula
direto para o <code>except</code>/fim de função sem passar por aquele
<code>close()</code>. Para criar o seu próprio, a forma mais simples é uma
função geradora decorada:</p>
<pre><code>from contextlib import contextmanager
import time

@contextmanager
def timer(label: str):
    t = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter()-t:.3f}s")

with timer("deploy"):
    run_deploy()</code></pre>
<p>O código antes do <code>yield</code> é o <code>__enter__</code>
implícito; o que vem depois (dentro do <code>finally</code>, para rodar
mesmo com exceção) é o <code>__exit__</code>. Múltiplos context managers
podem ser combinados numa linha:</p>
<pre><code>with open("a") as a, open("b") as b, lock:
    process(a, b)</code></pre>

<h3>9. `ExceptionGroup` e `except*` (3.11+): quando um erro não basta</h3>
<p>Operações concorrentes (<code>asyncio.gather</code>,
<code>TaskGroup</code>, visto na aula de concorrência) podem falhar em
MAIS DE UMA tarefa ao mesmo tempo — um <code>try/except</code> tradicional
só sabe lidar com uma exceção por vez, então antes do 3.11 a segunda falha
simultânea ficava escondida ou exigia agregação manual.
<code>ExceptionGroup</code> resolve isso agrupando todas as falhas
ocorridas, e <code>except*</code> permite tratar cada TIPO de erro dentro
do grupo separadamente:</p>
<pre><code>try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(fetch_a())
        tg.create_task(fetch_b())
except* ConnectionError as eg:
    log.warn("conexão: %d falhas", len(eg.exceptions))
except* TimeoutError as eg:
    log.warn("timeout: %d", len(eg.exceptions))</code></pre>
<p><code>eg.exceptions</code> é uma tupla com TODAS as exceções daquele
tipo que ocorreram nas tarefas do grupo — se três tarefas falharam com
<code>ConnectionError</code> e uma com <code>TimeoutError</code>, os dois
blocos <code>except*</code> rodam, cada um vendo só as exceções do seu
tipo, sem que uma mascare a outra.</p>"""
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
                  ["__init__ sobrescrito e vazio", "__del__ implementado manualmente", "__str__ isolado, sem __repr__"],
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
                  ["Essa forma de captura simplesmente deixou de existir a partir do Python 3.", "Captura só exceções relacionadas especificamente a erro de tipo (TypeError).", "Costuma deixar o programa consideravelmente mais lento do que capturar Exception."],
                  "BaseException é o topo. Aplicação deve capturar Exception ou subclasses. "
                  "Capturar BaseException pode ignorar Ctrl+C e sys.exit()."),
                q("`raise NewError(\"...\") from old` faz o quê?",
                  "Lança a nova exceção encadeando a original (preserva traceback).",
                  ["Substitui a exceção original de forma silenciosa, sem deixar algum registro dela.", "Causa um erro de sintaxe assim que o interpretador tenta ler esse trecho de código.", "Lança as duas exceções ao mesmo tempo, rodando de forma paralela uma à outra."],
                  "O `from` deixa explícito o encadeamento, o traceback mostra 'The "
                  "above exception was the direct cause of...' facilitando debugging."),
                q("Em `class Cache: items = []`, o que tem de errado se duas instâncias chamarem `.items.append(x)`?",
                  "items é atributo de classe (compartilhado), todas as instâncias enxergam o mesmo list.",
                  ["O interpretador Python proíbe explicitamente atributo mutável definido direto na classe.", "O valor guardado no append acaba se perdendo por causa da atuação do garbage collector.", "Não há problema algum nesse tipo de código, é só uma escolha de estilo pessoal."],
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
                  ["Só essa segunda forma, sem tipo, passou a funcionar a partir da versão 3.10, prática ainda comum em sistema legado que raramente é atualizado.", "As duas formas se comportam de maneira idêntica, sem diferença prática relevante, prática que só aparece como erro grave durante um incidente real.", "A forma `except:` costuma rodar visivelmente mais rápido do que `except Exception`, que só aparece como problema depois que o sistema já está em produção."],
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
                  ["except Exception: (bloco genérico)", "else: (só roda sem exceção)", "pass (dentro do except)"],
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
                """<h3>1. `pathlib`: um objeto que sabe o que é caminho, não uma string qualquer</h3>
<pre><code>from pathlib import Path

root   = Path("/var/log")
logfile = root / "app" / "app.log"        # operador / monta path
logfile.exists()
logfile.is_file()
logfile.parent                            # /var/log/app
logfile.suffix                            # '.log'
logfile.stem                              # 'app'
logfile.with_suffix(".log.1")             # rotação simples

# Iterar diretório
for log in Path("/var/log").rglob("*.gz"):
    print(log, log.stat().st_size)

# Ler/escrever em uma linha
txt = Path("config.toml").read_text(encoding="utf-8")
Path("out.json").write_text(json.dumps(d, indent=2))</code></pre>
<p><code>os.path.join("/var/log", "app.log")</code> e string concatenada
com <code>+</code> parecem equivalentes a <code>Path("/var/log") /
"app.log"</code>, mas divergem no que fazem quando o caminho tem
separadores errados (barra em vez de contrabarra no Windows) ou barras
duplicadas: <code>Path</code> normaliza isso automaticamente, porque
representa o caminho como estrutura, não como texto — cada operação
(<code>.parent</code>, <code>.suffix</code>, <code>/</code>) manipula a
estrutura, não faz manipulação de string por trás dos panos. É por isso
que código que mistura <code>os.path</code> com strings manuais tende a
quebrar silenciosamente em outro sistema operacional, enquanto código
todo em <code>pathlib</code> costuma simplesmente funcionar nos dois.</p>
<div class="mermaid">
flowchart LR
    CLI["Linha de comando"] --> Parser["argparse.ArgumentParser"]
    Parser --> Args["Namespace com os argumentos"]
    Args --> Main["Lógica do programa"]
</div>


<h3>2. Ler arquivos sem se queimar no encoding</h3>
<pre><code># EVITE: assume locale do sistema (pode ser ASCII em servidor)
open("file.txt").read()

# CERTO: explicite encoding e modo
with open("file.txt", encoding="utf-8") as f:
    data = f.read()</code></pre>
<p>Sem <code>encoding="utf-8"</code> explícito, Python usa o encoding
PADRÃO DO SISTEMA OPERACIONAL onde o script roda — que costuma ser UTF-8
no seu laptop e pode ser ASCII ou latin-1 em algumas configurações de
servidor Linux minimalista. O bug clássico é "funciona na minha máquina,
quebra no servidor": um arquivo com acento ou emoji lido sem encoding
explícito estoura <code>UnicodeDecodeError</code> só no ambiente onde o
locale padrão diverge — e como isso depende de configuração de sistema,
não do código em si, é um dos bugs mais frustrantes de reproduzir
localmente. Para binários (imagem, gzip, parquet), use modo
<code>"rb"</code> SEM encoding — misturar os dois é erro de tipo, texto
binário não tem "codificação de caracteres" para decodificar. Para CSV,
prefira <code>csv.DictReader</code> a <code>linha.split(",")</code>: uma
vírgula dentro de um campo entre aspas (comum em campos com texto livre)
quebra o split ingênuo de um jeito que só aparece quando alguém digita um
valor com vírgula, meses depois do código estar em produção.</p>

<h3>3. Configuração: por que YAML tem um modo "seguro" e o outro não deveria existir</h3>
<pre><code># JSON, stdlib, sem dependência
import json
cfg = json.loads(Path("cfg.json").read_text())
Path("out.json").write_text(json.dumps(cfg, indent=2, sort_keys=True))

# TOML, leitura nativa em 3.11+
import tomllib
with open("pyproject.toml", "rb") as f:
    pyproj = tomllib.load(f)

# YAML, pacote externo
import yaml          # pip install pyyaml
k = yaml.safe_load(Path("deploy.yaml").read_text())

# .env, uso típico em containers
from dotenv import load_dotenv  # pip install python-dotenv
load_dotenv()
import os; secret = os.environ["DB_PASSWORD"]</code></pre>
<p>O motivo de <code>yaml.safe_load</code> existir como função separada
de <code>yaml.load</code> é sério: a especificação YAML permite tags como
<code>!!python/object:algum.modulo.Classe</code> que instruem o parser a
INSTANCIAR uma classe Python arbitrária com os dados do documento —
<code>yaml.load</code> (sem o "safe") obedece essa tag, o que significa
que um YAML malicioso pode fazer o parser executar código Python
arbitrário só de ser carregado, antes mesmo do seu programa "usar" o
conteúdo. <code>safe_load</code> restringe a estruturas de dados simples
(dict, list, str, int...), sem capacidade de instanciar nada. Qualquer
YAML que vier de fora do seu controle direto (upload de usuário, arquivo
de outro time, configuração baixada de rede) deve SEMPRE passar por
<code>safe_load</code>, nunca por <code>load</code>.</p>

<h3>4. `argparse`: a stdlib que documenta a si mesma</h3>
<pre><code>import argparse
from pathlib import Path

def main() -&gt; int:
    p = argparse.ArgumentParser(prog="deploy", description="Faz deploy.")
    p.add_argument("image", help="Imagem Docker, ex: web:1.2")
    p.add_argument("--env", choices=["dev","stg","prod"], required=True)
    p.add_argument("--replicas", type=int, default=3)
    p.add_argument("--config", type=Path, default=Path("deploy.yaml"))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-v", "--verbose", action="count", default=0)
    args = p.parse_args()
    print(args)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())</code></pre>
<p>Cada <code>add_argument</code> gera automaticamente a mensagem de
<code>--help</code>, valida o tipo antes do seu código rodar
(<code>type=Path</code> entrega um objeto pronto, não uma string que você
converteria manualmente) e recusa entrada fora de <code>choices</code>
com mensagem legível — sem <code>argparse</code>, cada uma dessas
validações seria código manual espalhado pelo <code>main()</code>, fácil
de esquecer em algum argumento. <code>action="count"</code> para
verbosidade é o padrão por trás de <code>-v</code>/<code>-vv</code>/<code>-vvv</code>
que ferramentas Unix usam há décadas: cada ocorrência da flag soma 1 ao
contador. Subcomandos (<code>add_subparsers</code>) seguem o mesmo padrão
de <code>git commit</code>/<code>git push</code> — cada subcomando com seu
próprio conjunto de argumentos, compartilhando só os globais.</p>

<h3>5. `typer`: a mesma coisa, derivada das type hints</h3>
<pre><code>import typer
app = typer.Typer()

@app.command()
def deploy(image: str, env: str = "dev", replicas: int = 3) -&gt; None:
    typer.echo(f"Deploying {image} to {env} ×{replicas}")

@app.command()
def rollback(version: int) -&gt; None:
    typer.echo(f"Rolling back to {version}")

if __name__ == "__main__":
    app()</code></pre>
<p>A vantagem de <code>typer</code> sobre <code>argparse</code> cru
aparece quando o CLI cresce: em vez de declarar cada argumento duas vezes
(uma no <code>add_argument</code>, outra ao ler <code>args.campo</code>
no corpo da função), a assinatura da própria função Python — com type
hints — já É a definição do CLI. Menos código duplicado significa menos
chance de a validação e o uso divergirem conforme o projeto evolui.</p>

<h3>6. Logging estruturado: por que não é só um `print` mais chique</h3>
<pre><code>import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
log = logging.getLogger("deploy")

log.info("deploying image=%s env=%s", image, env)   # lazy interpolation
log.warning("replicas=%d acima do recomendado", n)
log.error("falhou", exc_info=True)                  # inclui traceback</code></pre>
<p>Passar os valores como argumentos separados
(<code>"%s", image</code>) em vez de já formatados
(<code>f"...{image}..."</code>) não é estilo — é <em>lazy evaluation</em>:
o logging só formata a string se o nível configurado realmente for emitir
aquele log. Com f-string, a interpolação acontece SEMPRE, mesmo que o
nível DEBUG esteja desativado e a mensagem seja descartada em seguida —
desperdício real de CPU em sistemas que emitem centenas de logs DEBUG por
segundo mas rodam em produção com nível INFO. Em produção, trocar o
handler para emitir JSON estruturado (via <code>python-json-logger</code>)
facilita a ingestão por Datadog, Loki ou CloudWatch, que esperam campos
separados (timestamp, nível, mensagem) em vez de uma linha de texto livre
para fazer parsing.</p>

<h3>7. stdout vs. stderr: o contrato que faz seu CLI compor com outros</h3>
<pre><code>import sys
print(json.dumps(result))                # stdout
print("WARN: ...", file=sys.stderr)      # stderr</code></pre>
<p>A convenção POSIX reserva <code>stdout</code> para o RESULTADO do
programa — o que outro programa vai consumir via pipe — e
<code>stderr</code> para diagnóstico dirigido a um humano. Misturar os
dois (um <code>print("Iniciando deploy...")</code> solto antes do JSON de
resultado) quebra qualquer composição com outra ferramenta:
<code>meu-cli | jq '.status'</code> falha ao tentar parsear "Iniciando
deploy..." como JSON, porque essa linha nunca deveria ter ido para
stdout. Todo log de progresso, aviso ou erro que um humano lê no
terminal — mas que um script consumidor não deveria ver — vai para
stderr.</p>

<h3>8. Códigos de saída: o protocolo que scripts de automação verificam</h3>
<pre><code>def main() -&gt; int:
    try: do_work()
    except ConfigError: return 65   # data format error
    except NetworkError: return 69  # service unavailable
    return 0

if __name__ == "__main__":
    raise SystemExit(main())</code></pre>
<p>0 significa sucesso; qualquer outro valor significa falha — é o único
sinal que um script de shell chamando seu CLI (<code>if
meu-cli; then ...</code>) enxerga sem precisar interpretar a saída de
texto. Convenção POSIX (definida em <code>sysexits.h</code>) reserva
faixas específicas — 65 para erro de formato de dados, 69 para serviço
indisponível — que ferramentas de automação de infraestrutura já
reconhecem; usar 1 genérico para tudo obriga quem integra seu CLI a ler
mensagens de texto para saber o que deu errado, em vez de checar o código
de saída. O padrão <code>def main() -&gt; int: ...</code> +
<code>raise SystemExit(main())</code> mantém a lógica de saída dentro de
uma função testável — testar que <code>main()</code> retorna 65 num
cenário de configuração inválida é trivial; testar que o PROCESSO sai com
código 65 exigiria rodar um subprocesso de verdade a cada teste.</p>"""
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
                  ["Não suporta corretamente caracteres unicode no arquivo.", "Fica bem mais lento quando o arquivo de entrada é grande.", "Simplesmente para de funcionar a partir da versão 3.11."],
                  "yaml.load aceita tags `!!python/object` que instanciam classes, "
                  "vetor de RCE. Sempre use `yaml.safe_load`."),
                q("Para parsear pyproject.toml na stdlib (3.11+), use:",
                  "tomllib",
                  ["tomli (pacote externo via pip)", "configparser (formato .ini)", "json (formato incompatível)"],
                  "tomllib é a stdlib a partir do 3.11. Para versões anteriores use "
                  "tomli (mesma API)."),
                q("Em argparse, `action='store_true'` é usado para...",
                  "Flags booleanas (--verbose ⇒ args.verbose = True).",
                  ["É exatamente equivalente a definir `default=True` sozinho.", "Forçar que o argumento seja passado de forma obrigatória.", "Armazenar literalmente a string `'true'` como valor do argumento."],
                  "Sem o flag → False; com o flag → True. Mais natural que --verbose=true."),
                q("Por que separar saída em stdout vs stderr em um CLI?",
                  "Para que pipelines possam capturar só o resultado (stdout), enquanto diagnóstico vai para stderr.",
                  ["É puramente uma escolha estética de organização, sem qualquer impacto real no uso do CLI, prática ainda comum em sistema legado que raramente é atualizado.", "O canal stderr costuma ser escrito de forma consideravelmente mais rápida que o stdout, erro típico de configuração feita às pressas, sem revisão posterior.", "O stdout, por padrão, não consegue exibir corretamente caracteres codificados em UTF-8, comportamento que só some quando alguém finalmente lê a documentação."],
                  "Convenção POSIX. Permite `meu-cli | jq ...` sem misturar logs."),
                q("Por que evitar `open(p).read()` direto, sem context manager?",
                  "O arquivo pode não ser fechado se o GC demorar, em servidores de longa vida vaza descritores.",
                  ["Escrever direto assim costuma causar um erro de sintaxe já na leitura do código, suposição que vale só até o primeiro imprevisto de rede ou hardware.", "Essa forma direta costuma rodar visivelmente mais devagar que usar um context manager, erro típico de configuração feita às pressas, sem revisão posterior.", "Esse problema só costuma aparecer em máquinas rodando especificamente o Windows, abordagem que funciona bem até o primeiro pico de carga real."],
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
                  ["sys.exit('2') com o código como string, direto na main", "raise Exit(2), classe que não existe na stdlib do Python", "os.exit(2), função que não existe no módulo os padrão"],
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
<div class="mermaid">
flowchart LR
    Client["Cliente"] -- "request" --> API["API"]
    API -- "5xx" --> Retry{"Tentativas esgotadas?"}
    Retry -- "Não" --> Client
    Retry -- "Sim" --> Fail["Levanta exceção"]
    API -- "2xx" --> Success["Retorna o dado"]
</div>

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
                  ["A chamada fica só um pouco mais lenta do que fazer o mesmo request com timeout.", "A chamada deixa de funcionar por completo quando a URL usa o protocolo HTTPS.", "Isso passa a causar um erro de sintaxe a partir especificamente da versão 3.11."],
                  "Sem timeout, uma conexão problemática pode travar o programa para "
                  "sempre. Sempre defina (connect_timeout, read_timeout)."),
                q("`raise_for_status()` faz o quê?",
                  "Lança HTTPError se o status code for 4xx ou 5xx.",
                  ["Reenvia automaticamente a mesma requisição para o servidor.", "Lança um erro em qualquer status code recebido, mesmo 2xx.", "Só imprime o status code recebido diretamente na tela."],
                  "É a forma idiomática de tratar erros HTTP. Sem ela, você processa "
                  "respostas de erro como se fossem sucesso."),
                q("Para retry de erros transitórios (5xx), você deveria configurar...",
                  "urllib3.Retry com backoff_factor e status_forcelist.",
                  ["Escrever um loop `while True` chamando `sleep` manualmente.", "Rodar a chamada numa thread separada dentro de um try/except.", "Não fazer retry algum e deixar a chamada falhar rápido."],
                  "Retry com backoff exponencial é o padrão. Loop manual sem jitter "
                  "pode causar thundering herd."),
                q("Por que usar `requests.Session` em vez de chamadas avulsas?",
                  "Reusa conexões TCP/TLS (connection pooling), reduzindo latência.",
                  ["Mantém os cookies recebidos guardados por um período fixo de exatamente 24 horas.", "Passou a ser uma exigência obrigatória da biblioteca a partir da versão 3.10.", "Permite que as requisições continuem sendo feitas mesmo sem conexão de rede."],
                  "Em scripts com várias chamadas ao mesmo host, Session evita "
                  "handshake TLS repetido."),
                q("Para verificar uma assinatura HMAC de webhook com segurança:",
                  "hmac.compare_digest(esperado, recebido)",
                  ["esperado == recebido (comparação direta)", "esperado in recebido (contido em vez de igual)", "recebido.startswith(esperado) (prefixo)"],
                  "compare_digest é constant-time: não vaza informação por timing. "
                  "`==` para de comparar no primeiro byte diferente."),
                q("Em paginação por Link header (estilo GitHub), o atributo `r.links['next']['url']` retorna...",
                  "A URL completa da próxima página.",
                  ["Retorna só o número correspondente à próxima página.", "Retorna um booleano indicando só se existe próxima página.", "Retorna o número total de páginas disponíveis na resposta."],
                  "requests parseia o Link header automaticamente em dict, basta "
                  "checar 'next'."),
                q("Token de API em código-fonte é problema porque...",
                  "Vai parar no git e em logs; rotação fica difícil; quem tem acesso ao repo tem o token.",
                  ["É só uma questão de organização estética do código-fonte, muito pouco mais além disso.", "Reduz de forma perceptível a performance da aplicação já em ambiente de produção.", "Costuma causar falha de execução especificamente em servidores rodando Linux."],
                  "Tokens devem vir de env, secret manager ou keyring. Se vazar, "
                  "rotacione imediatamente."),
                q("`httpx.AsyncClient` é particularmente útil quando...",
                  "Você precisa fazer várias requisições em paralelo (fan-out).",
                  ["Você quer, por algum motivo, evitar usar conexões HTTPS na sua aplicação.", "O seu projeto ainda depende inteiramente da versão antiga, o Python 2.", "Você só precisa mesmo fazer uma única requisição isolada e simples."],
                  "Async + gather permite N requisições simultâneas com baixa overhead. "
                  "Síncrono seria sequencial."),
                q("Para autenticação Bearer Token, o header correto é:",
                  "Authorization: Bearer <token>",
                  ["Auth: <token> (header customizado)", "X-Bearer: <token> (header customizado)", "Cookie: token=<token> (via cookie)"],
                  "Padrão RFC 6750. Sempre o esquema explícito antes do token."),
                q("Vale a pena usar `r.json()` se o status for 500?",
                  "Não, chame raise_for_status() primeiro; senão pode parsear body de erro como dado válido.",
                  ["Vale a pena fazer isso em qualquer situação, mesmo sem checar o status antes, resultado típico de copiar configuração de outro projeto sem adaptar.", "Só vale a pena fazer isso quando a aplicação já está rodando em produção, atalho que parece seguro isolado, mas quebra quando combinado com outros sistemas.", "Só vale a pena fazer isso quando a chamada acontece dentro da rede interna, suposição que só se sustenta enquanto o time é pequeno."],
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
                """<h3>1. `subprocess.run`: por que lista de argumentos é a defesa, não um detalhe de estilo</h3>
<pre><code>import subprocess

result = subprocess.run(
    ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
    capture_output=True,
    text=True,        # decodifica como str (utf-8 default)
    timeout=30,
    check=True,       # raise CalledProcessError se exit != 0
)
data = json.loads(result.stdout)</code></pre>
<p>Quando você passa uma LISTA de argumentos, cada elemento vai direto
para o processo filho como um argumento separado — o sistema operacional
nunca interpreta espaço, ponto-e-vírgula, pipe ou <code>$()</code> dentro
de um desses elementos como sintaxe especial, porque não existe shell
nenhum no meio interpretando a string. É por isso que
<code>["ls", "-l", caminho]</code> é seguro mesmo se
<code>caminho = "; rm -rf /"</code>: esse valor inteiro vira UM argumento
literal chamado "; rm -rf /", não uma sequência de comandos. Já
<code>os.system(f"ls {caminho}")</code> ou <code>subprocess.run(cmd,
shell=True)</code> passam a string inteira para um shell de verdade
(<code>/bin/sh</code>) interpretá-la — e nesse ponto, qualquer
metacaractere shell dentro do valor vira comando executável. Esse é o
motivo pelo qual "concatenar comando + input do usuário" é uma das
classes mais antigas e mais exploradas de vulnerabilidade em ferramentas
de automação.</p>
<div class="mermaid">
flowchart LR
    Py["Script Python"] --> Sub["subprocess.run com lista de args"]
    Sub --> Proc["Processo filho"]
    Proc --> Out["stdout, stderr e returncode"]
    Out --> Py
</div>

<p><code>timeout</code> existe pela mesma razão que em chamadas HTTP: um
processo filho pode travar esperando algo que nunca chega (um prompt
interativo pedindo confirmação, uma conexão de rede que não cai) e sem
timeout o script pai fica pendurado indefinidamente. <code>check=True</code>
converte um exit code diferente de zero em exceção — sem ele, um comando
que falhou silenciosamente (o kubectl não achou o namespace, por exemplo)
deixa <code>result.stdout</code> vazio ou com erro, e o
<code>json.loads</code> seguinte quebra de um jeito que não deixa claro
que o comando em si já tinha falhado antes.</p>

<h3>2. Streaming: por que esperar o processo terminar às vezes é a escolha errada</h3>
<pre><code>p = subprocess.Popen(
    ["terraform", "apply", "-auto-approve"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
)
for line in p.stdout:
    print(line, end="")          # mostra na hora
    log_file.write(line)
rc = p.wait(timeout=3600)
if rc != 0:
    raise SystemExit(rc)</code></pre>
<p><code>subprocess.run</code> só devolve controle quando o processo
termina — para um <code>terraform apply</code> de 20 minutos, isso
significa ficar sem NENHUM feedback até o fim, sem saber se está
progredindo ou travado. <code>Popen</code> devolve controle imediatamente
com um handle para o processo ainda rodando; iterar
<code>p.stdout</code> linha a linha entrega cada linha assim que o
processo a produz, permitindo mostrar progresso em tempo real e gravar
num arquivo de log simultaneamente — o mesmo padrão por trás de qualquer
ferramenta de CI que mostra logs "ao vivo" em vez de só o resultado
final.</p>

<h3>3. Variáveis de ambiente do subprocesso: herdar por padrão, sobrescrever com cuidado</h3>
<pre><code>env = os.environ.copy()       # NUNCA passe os.environ direto e mute
env["KUBECONFIG"] = "/etc/k8s/prod.kubeconfig"
env["AWS_PROFILE"] = "prod"
subprocess.run(["kubectl", "get", "ns"], env=env, check=True)</code></pre>
<p>O parâmetro <code>env=</code>, quando informado, SUBSTITUI o ambiente
inteiro do processo filho — não faz merge com o ambiente atual. Passar
<code>env={"KUBECONFIG": "..."}</code> diretamente (sem o
<code>.copy()</code> de <code>os.environ</code> antes) apaga
<code>PATH</code>, <code>HOME</code>, <code>USER</code> e tudo mais que o
processo filho normalmente herdaria — um erro que se manifesta como o
subprocesso não encontrando binários que deveriam estar no PATH, um
sintoma que não aponta óbvio para "esqueci de copiar o ambiente".</p>

<h3>4. `shell=True`: quando o risco vale o benefício, e a alternativa sem shell</h3>
<pre><code>cmd = "ps aux | grep nginx | wc -l"
subprocess.run(cmd, shell=True, check=True)</code></pre>
<p>Pipes e redirecionamento nativos do shell (<code>|</code>,
<code>&gt;</code>, <code>&amp;&amp;</code>) só existem quando um shell de
verdade interpreta a string — é o único caso onde <code>shell=True</code>
economiza trabalho de verdade. O risco é o mesmo da seção 1: se qualquer
parte dessa string vier de fora (usuário, arquivo, variável de rede), é
injeção. Para o mesmo resultado sem abrir mão da segurança de listas,
compõe-se o pipeline manualmente encadeando processos:</p>
<pre><code>p1 = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE)
p2 = subprocess.Popen(["grep", "nginx"], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
out = p2.communicate()[0]</code></pre>
<p>Quando <code>shell=True</code> for realmente inevitável (compatibilidade
com um script legado, por exemplo) e parte do comando vier de fora,
<code>shlex.quote</code> escapa a string de forma que o shell a trate como
um único token literal, neutralizando metacaracteres:</p>
<pre><code>import shlex
subprocess.run(f"ls {shlex.quote(user_path)}", shell=True)</code></pre>

<h3>5. Operações de filesystem: `shutil` e as garantias que cada função oferece</h3>
<pre><code>import shutil, os

shutil.copy2(src, dst)            # mantém metadata
shutil.copytree(src, dst)         # recursivo
shutil.rmtree(path, ignore_errors=False)
shutil.move(src, dst)             # atômico no MESMO FS
shutil.disk_usage("/")            # (total, used, free) bytes
shutil.which("terraform")         # localiza binário no PATH

os.replace(src, dst)              # move atômico
os.path.expanduser("~/.kube/config")
os.environ.get("HOME", "/root")</code></pre>
<p>A palavra "atômico" em <code>shutil.move</code>/<code>os.replace</code>
tem um limite importante: a operação só é atômica (tudo-ou-nada, sem
estado intermediário visível) quando origem e destino estão no MESMO
sistema de arquivos, porque nesse caso o SO só precisa atualizar um
ponteiro de diretório (a chamada <code>rename(2)</code> do kernel). Entre
filesystems diferentes (por exemplo, mover de <code>/tmp</code> tmpfs
para um disco montado), não existe rename direto possível — a biblioteca
cai automaticamente para copiar e depois apagar o original, uma operação
que pode ser interrompida no meio, deixando os dois lados parcialmente
escritos se o processo morrer entre a cópia e a remoção.</p>

<h3>6. Arquivos temporários: por que `mktemp` foi abandonado</h3>
<pre><code>import tempfile

# arquivo temporário
with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
    f.write(yaml_content)
    tmp_path = f.name
try:
    subprocess.run(["kubectl", "apply", "-f", tmp_path], check=True)
finally:
    Path(tmp_path).unlink(missing_ok=True)

# diretório temporário (cleanup automático)
with tempfile.TemporaryDirectory() as d:
    Path(d, "file.txt").write_text("oi")
    # diretório removido ao sair</code></pre>
<p>A função antiga <code>tempfile.mktemp()</code> só GERAVA um nome de
arquivo supostamente único, sem criar o arquivo — deixando uma janela de
tempo entre "gerar o nome" e "abrir o arquivo" onde outro processo (ou um
atacante local) poderia criar um arquivo ou symlink com aquele mesmo nome
primeiro, uma race condition clássica (a mesma classe de bug do ataque
histórico em <code>/tmp</code> compartilhado, visto na aula de Linux da
Fase 1). <code>NamedTemporaryFile</code> resolve isso criando o arquivo
ATOMICAMENTE já no momento de gerar o nome, sem essa janela.</p>

<h3>7. SSH remoto: Fabric para tarefas pontuais, Ansible para escala</h3>
<pre><code>from fabric import Connection   # pip install fabric

with Connection("deploy@10.0.1.5", connect_kwargs={"key_filename": "~/.ssh/id_ed25519"}) as c:
    r = c.run("systemctl status nginx", warn=True)
    if r.return_code != 0:
        c.sudo("systemctl restart nginx")
    c.put("./nginx.conf", "/etc/nginx/conf.d/app.conf")
    c.run("nginx -t && systemctl reload nginx")</code></pre>
<p><code>warn=True</code> em <code>c.run</code> é o oposto do
<code>check=True</code> visto na seção 1: em vez de levantar exceção
automática num exit code não-zero, deixa o código checar
<code>r.return_code</code> manualmente e decidir o que fazer — necessário
aqui porque "nginx não está rodando" é um resultado ESPERADO que o script
trata (reiniciando), não um erro fatal que deveria abortar. Para um
inventário de dezenas ou centenas de hosts, Ansible ganha por já ter
paralelismo, idempotência declarativa e um formato de playbook que
outra pessoa do time consegue ler sem saber Python — Fabric fica melhor
para automação pontual onde escrever Python de verdade (com toda a lógica
condicional da linguagem) compensa o esforço extra.</p>

<h3>8. Sinais: encerrar graciosamente em vez de morrer no meio de uma escrita</h3>
<pre><code>import signal

shutdown = False
def _handle(sig, frame):
    global shutdown; shutdown = True

signal.signal(signal.SIGTERM, _handle)
signal.signal(signal.SIGINT,  _handle)

while not shutdown:
    do_iteration()
cleanup()</code></pre>
<p>Sem esse handler, um <code>SIGTERM</code> (o sinal padrão que
<code>systemctl stop</code> ou um orquestrador de containers envia antes
de matar um processo) interrompe o programa NO PONTO EXATO onde ele
estava — no meio de uma escrita em arquivo, de uma transação, de uma
chamada de rede — sem chance de fechar recursos ou salvar estado.
Registrar um handler transforma o sinal numa flag que o loop principal
verifica no seu próprio ritmo, terminando a iteração em andamento antes
de sair. <code>SIGKILL</code> (o "mate agora" do <code>kill -9</code>) não
pode ser interceptado por nenhum handler — é o sinal de último recurso
quando um processo ignora <code>SIGTERM</code> repetidamente.</p>

<h3>9. Checklist para scripts que vão rodar em produção</h3>
<ul>
<li>Sempre <code>check=True</code>, sempre <code>timeout</code> — as duas
proteções mais baratas contra as duas falhas mais comuns (erro
silencioso, travamento indefinido).</li>
<li>Nunca <code>shell=True</code> com input do usuário não escapado —
mesmo "só uma vez, script interno" vira problema quando o script cresce e
alguém adiciona uma fonte de input que você não previu.</li>
<li>Logue o comando exato (com <code>shlex.join</code>, que faz o inverso
de <code>shlex.quote</code>) antes de executar — quando algo falhar em
produção, poder ver o comando literal que rodou economiza horas de
"reproduzir o bug".</li>
<li>Para retry, use uma lib madura (tenacity) em vez de reescrever
backoff exponencial à mão — a versão "rápida" costuma esquecer jitter ou
limite máximo de tentativas.</li>
<li>Defina <code>cwd=</code> explicitamente quando o comando depende de
diretório de trabalho — não assuma que o script sempre roda de onde você
testou.</li>
<li>Não dependa de <code>$PATH</code> em produção: use caminho absoluto
ou <code>shutil.which</code> e falhe cedo se o binário não existir, em
vez de um erro genérico de "comando não encontrado" no meio da
execução.</li>
</ul>"""
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
                  ["É só uma forma um pouco mais rápida de rodar o mesmo comando, só isso, decisão que parece inofensiva isolada, mas se acumula com o tempo.", "O `subprocess` geralmente captura a saída do comando automaticamente por padrão, prática que troca previsibilidade por economia de esforço imediato.", "A função `os.system` simplesmente deixou de existir a partir do Python 3, suposição que só vale em ambiente de desenvolvimento, não em produção."],
                  "Lista evita interpretação de espaços, `;`, `|`, `$()`. Vetor clássico "
                  "de injeção desaparece."),
                q("Para garantir que `subprocess.run` falhe se o exit code não for 0:",
                  "Passe `check=True`.",
                  ["Verificar manualmente o valor de `result.returncode` depois de cada chamada.", "Não existe forma direta de fazer esse tipo de verificação.", "Configurar o parâmetro `stderr=PIPE` na chamada do subprocess."],
                  "check=True levanta CalledProcessError automaticamente. Manual também "
                  "funciona, mas é fácil esquecer."),
                q("`shell=True` é arriscado quando...",
                  "A string contém input não escapado vindo de fora (usuário, arquivo, rede).",
                  ["Só fica arriscado quando o comando envolve algum tipo de pipe entre processos.", "Fica arriscado em praticamente qualquer chamada, mesmo sem qualquer input externo.", "Só fica arriscado quando o comando é executado especificamente em Windows."],
                  "shell=True interpreta metacaracteres do shell. Se um deles vier do "
                  "usuário, é RCE. Use lista de args ou shlex.quote."),
                q("Para mostrar saída de um processo longo enquanto ele roda, use:",
                  "subprocess.Popen com stdout=PIPE e iterar p.stdout linha a linha.",
                  ["Chamar `subprocess.check_output`, que só retorna ao final.", "Usar `subprocess.run` com `capture_output`, que só retorna no fim da execução.", "Chamar `os.system`, que mostra a saída direto no terminal."],
                  "run/check_output bloqueiam até o fim. Popen + iter dá streaming "
                  "em tempo real."),
                q("Ao definir env= em subprocess, qual erro é comum?",
                  "Esquecer de copiar os.environ, o subprocesso fica sem PATH e variáveis essenciais.",
                  ["Costuma provocar diretamente um segfault dentro do processo filho criado.", "Costuma quebrar de forma específica a variável de ambiente chamada HOME.", "Torna tecnicamente muito difícil passar qualquer variável de ambiente customizada."],
                  "Comece com `env = os.environ.copy()` e adicione/sobrescreva. Senão "
                  "perde PATH, HOME, USER, etc."),
                q("Para criar arquivo temporário que será removido automaticamente:",
                  "with tempfile.NamedTemporaryFile() as f: ... (delete=True default)",
                  ["open('/tmp/' + str(uuid4()), 'w') sem cleanup automático depois", "tempfile.mktemp() (deprecado, com race condition conhecida há anos)", "shutil.create_temp() (função que não existe no módulo shutil)"],
                  "NamedTemporaryFile remove ao sair do `with` (delete=True default). "
                  "mktemp é race-condition vulnerable."),
                q("`shutil.move(src, dst)` em FS diferentes...",
                  "Cai para copiar+remover (não é atômico).",
                  ["Continua sendo uma operação atômica, independente do filesystem.", "Usa internamente um pipe para transferir os bytes do arquivo.", "Acaba falhando na maioria dos casos quando os filesystems são diferentes."],
                  "Em FS diferentes, copia e depois remove. Atômico só dentro do mesmo "
                  "FS via rename(2)."),
                q("Para localizar um binário no PATH:",
                  "shutil.which('kubectl')",
                  ["Path.find('kubectl', True)", "os.locate('kubectl', True)", "which.find('kubectl', True)"],
                  "shutil.which retorna o caminho absoluto ou None. Útil pra checar "
                  "dependências antes de chamar."),
                q("`signal.signal(SIGTERM, handler)` é útil para...",
                  "Interceptar pedido de parada e fazer cleanup gracioso (fechar arquivos, drenar fila).",
                  ["Aumentar manualmente a prioridade de agendamento desse processo no sistema, erro que só é percebido quando o time de operação já está lidando com o incidente.", "Forçar o reboot completo da máquina onde esse processo está rodando, decisão que parece inofensiva isolada, mas se acumula com o tempo.", "Detectar de forma automática erros de lógica dentro do próprio código do programa, comportamento que só é notado quando alguém audita os logs depois."],
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
                """<h3>1. O GIL: um lock que explica por que "mais threads" às vezes não ajuda nada</h3>
<p>O <strong>Global Interpreter Lock</strong> é um lock único, dentro do
próprio interpretador CPython, que garante que apenas UMA thread execute
bytecode Python por vez — mesmo numa máquina com 32 núcleos, só um núcleo
está rodando código Python num dado instante. Isso existe porque o
gerenciamento de memória do CPython (contagem de referências para saber
quando liberar um objeto) não é thread-safe por padrão, e o GIL é a
solução histórica mais simples para isso: em vez de sincronizar cada
acesso a cada objeto individualmente (caro e complexo), trava tudo com um
lock só. A consequência prática divide o mundo em dois:</p>
<div class="mermaid">
flowchart TD
    subgraph Threads ["threading, com GIL"]
        T1["Thread 1"] --> GIL["Só uma roda bytecode Python por vez"]
        T2["Thread 2"] --> GIL
    end
    subgraph Multi ["multiprocessing"]
        P1["Processo 1, próprio interpretador"]
        P2["Processo 2, próprio interpretador"]
    end
</div>

<ul>
<li><strong>CPU-bound (cálculo puro)</strong>: threads NÃO ajudam — o
GIL garante que só uma rode por vez, então 4 threads calculando não são
mais rápidas que 1, só trocam de contexto entre si sem ganho real. Use
<code>multiprocessing</code> (processos separados, cada um com seu
próprio interpretador e seu próprio GIL) ou bibliotecas em C que liberam o
GIL explicitamente durante o cálculo pesado (numpy, polars).</li>
<li><strong>I/O-bound (rede, disco)</strong>: threads e asyncio ajudam de
verdade, porque toda chamada de I/O no CPython LIBERA o GIL enquanto
espera o kernel responder — é justamente essa espera (não o cálculo) que
domina o tempo de uma chamada de rede, e é nela que outra thread pode
rodar.</li>
</ul>
<p>Python 3.13 introduziu builds experimentais sem GIL
(<em>free-threading</em>), mas para a maioria dos times ainda é cedo para
depender disso em produção — o ecossistema de extensões em C ainda está
migrando para suportar esse modo.</p>

<h3>2. Threads para I/O: o caso simples que resolve 80% dos scripts</h3>
<pre><code>from concurrent.futures import ThreadPoolExecutor

def fetch(url: str) -&gt; tuple[str, int]:
    r = requests.get(url, timeout=10)
    return url, r.status_code

with ThreadPoolExecutor(max_workers=20) as pool:
    for url, status in pool.map(fetch, urls):
        print(url, status)</code></pre>
<p><code>ThreadPoolExecutor</code> gerencia o ciclo de vida das threads
(criação, distribuição de trabalho, coleta de resultado, encerramento) —
usar <code>threading.Thread</code> diretamente exige reimplementar
manualmente uma fila de trabalho e coordenação de encerramento, trabalho
que raramente compensa fazer à mão. Para 50 chamadas HTTP sequenciais
esperando ~200ms cada, o tempo total seria ~10 segundos; com 20 threads
paralelas, o tempo se aproxima do tempo da chamada MAIS LENTA, não da
soma — porque enquanto uma thread espera resposta de rede (GIL liberado),
outra já está fazendo sua própria chamada.</p>

<h3>3. `asyncio`: uma thread só, alternando em pontos explícitos de espera</h3>
<p>Em vez de várias threads do sistema operacional, <code>asyncio</code>
roda tudo numa única thread que alterna entre tarefas exatamente nos
pontos marcados com <code>await</code> — um modelo cooperativo em vez de
preemptivo (o sistema operacional decidindo quando trocar de thread):</p>
<pre><code>import asyncio, httpx

async def fetch(client: httpx.AsyncClient, url: str) -&gt; int:
    r = await client.get(url, timeout=10)
    return r.status_code

async def main():
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:    # 3.11+
            tasks = [tg.create_task(fetch(client, u)) for u in urls]
        for t in tasks:
            print(t.result())

asyncio.run(main())</code></pre>
<p>A vantagem sobre threads aparece em escala: cada thread do SO consome
memória (pilha própria, tipicamente megabytes) e troca de contexto tem
custo real de kernel — dez mil threads simultâneas é inviável. Dez mil
tarefas asyncio (objetos leves gerenciados pelo próprio interpretador)
são rotineiras. Como só uma "linha de execução" roda por vez e ela só
troca em pontos explícitos de <code>await</code>, também não há race
condition entre tarefas asyncio tocando o mesmo estado — ao contrário de
threads, onde qualquer acesso concorrente a dado compartilhado precisa de
lock. O preço: TODA a cadeia de chamadas precisa ser assíncrona; uma
única função síncrona bloqueante chamada de dentro de uma corrotina
CONGELA o event loop inteiro, travando todas as outras tarefas até ela
terminar (seção 5).</p>

<h3>4. Padrões essenciais de `asyncio`</h3>
<pre><code># gather: aguarda várias tarefas, retorna lista
results = await asyncio.gather(t1, t2, t3, return_exceptions=True)

# wait_for: timeout em uma corrotina
try:
    r = await asyncio.wait_for(slow_op(), timeout=5)
except asyncio.TimeoutError: ...

# semaphore: limita concorrência
sem = asyncio.Semaphore(10)
async def fetch(url):
    async with sem:
        return await client.get(url)

# cancelar tarefa
task.cancel()
try: await task
except asyncio.CancelledError: ...</code></pre>
<p><code>return_exceptions=True</code> em <code>gather</code> muda o
comportamento de forma que vale entender: sem essa flag, se UMA tarefa
levantar exceção, <code>gather</code> propaga essa exceção imediatamente
e cancela as outras — útil quando qualquer falha invalida o resultado
inteiro. Com a flag, cada posição da lista de resultado recebe ou o valor
de sucesso ou o OBJETO da exceção (não relançada), permitindo processar
"o que deu certo" mesmo com falhas parciais — o padrão certo para,
por exemplo, checar a saúde de 50 serviços onde alguns poderem estar fora
do ar é esperado e não deve derrubar o restante da checagem.
<code>Semaphore</code> limita quantas corrotinas passam do
<code>async with sem</code> ao mesmo tempo — sem isso, disparar 10.000
requisições simultâneas para uma API pode derrubá-la ou estourar limites
de rate limit que ela mesma impõe.</p>

<h3>5. Misturar sync e async: onde o congelamento acontece</h3>
<pre><code>import asyncio

def cpu_bound(n: int) -&gt; int:
    return sum(range(n))

async def main():
    r = await asyncio.to_thread(cpu_bound, 10**7)
    print(r)</code></pre>
<p>Chamar uma função síncrona bloqueante (uma soma pesada, uma chamada de
biblioteca que não é async, um <code>requests.get</code> comum dentro de
código <code>async def</code>) trava o ÚNICO thread que o event loop usa
— e como não há mais nenhuma outra thread rodando as demais tarefas,
TODAS elas param até essa chamada terminar, mesmo tarefas que não têm
nada a ver com ela. <code>asyncio.to_thread</code> (3.9+) resolve isso
delegando a chamada síncrona para um pool de threads separado, liberando
o event loop principal para continuar processando outras tarefas enquanto
aquela chamada bloqueante roda em paralelo, numa thread de verdade.</p>

<h3>6. `multiprocessing`: contornar o GIL usando processos, não threads</h3>
<pre><code>from concurrent.futures import ProcessPoolExecutor

def hash_file(path: str) -&gt; tuple[str, str]:
    import hashlib
    h = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return path, h

with ProcessPoolExecutor() as pool:
    for p, sha in pool.map(hash_file, files):
        print(p, sha)</code></pre>
<p>Cada worker de um <code>ProcessPoolExecutor</code> é um processo
Python COMPLETO, com seu próprio interpretador e seu próprio GIL — é por
isso que multiprocessing de fato usa todos os núcleos para trabalho
CPU-bound, ao contrário de threads. O custo dessa independência é
serialização: como processos não compartilham memória diretamente, todo
argumento enviado a um worker e todo resultado devolvido precisa ser
"picklado" (serializado) e transmitido entre processos — passar objetos
grandes (um DataFrame de gigabytes, por exemplo) tem overhead real; o
padrão mais eficiente é passar caminhos ou IDs pequenos e deixar cada
worker ler/processar seus próprios dados localmente.</p>

<h3>7. Sincronização: por que "operação simples" ainda precisa de Lock</h3>
<pre><code># threading
from threading import Lock
counter = 0
lock = Lock()
def inc():
    global counter
    with lock:
        counter += 1     # GIL não garante atomicidade de operações compostas

# producer/consumer
from queue import Queue
q = Queue(maxsize=100)
def producer():
    for item in source: q.put(item)
def consumer():
    while True:
        item = q.get()
        process(item); q.task_done()</code></pre>
<p><code>counter += 1</code> PARECE uma operação atômica, mas na verdade
é três passos (ler o valor atual, somar 1, gravar de volta) — e o GIL
pode trocar de thread ENTRE esses passos, já que ele garante só que UM
bytecode roda por vez, não que uma sequência de bytecodes relacionados
roda sem interrupção. Duas threads incrementando o mesmo contador sem
lock podem perder incrementos: ambas leem o mesmo valor antes de qualquer
uma escrever de volta, e o resultado final é menor do que a soma real de
incrementos feitos. <code>Queue</code> (thread-safe por design, ao
contrário de listas comuns) é o padrão certo para comunicação entre
threads produtoras e consumidoras, sem precisar de lock manual em cada
acesso.</p>

<h3>8. As quatro armadilhas que pegam todo mundo pelo menos uma vez</h3>
<ul>
<li><strong>Race condition</strong>: contadores, dicts, listas em thread
NÃO são atômicos para incrementos/append compostos. Use Lock ou
estruturas já thread-safe (Queue).</li>
<li><strong>Deadlock</strong>: duas threads pegando dois locks em ORDENS
diferentes (A pega lock1 depois lock2; B pega lock2 depois lock1) podem
travar mutuamente esperando o lock que a outra já tem. Adquira locks
sempre na mesma ordem em todo o código.</li>
<li><strong>Bloqueio acidental do event loop</strong>: chamar
<code>requests.get</code> (síncrono) dentro de código
<code>async def</code> congela TODO o loop, não só aquela tarefa. Use
<code>httpx.AsyncClient</code> ou <code>aiohttp</code>, bibliotecas
desenhadas para <code>await</code>.</li>
<li><strong>multiprocessing no Windows</strong>: o mecanismo de criar
processos filhos ali reimporta o módulo principal do zero em cada worker
— sem <code>if __name__ == "__main__":</code> ao redor do código que
dispara o pool, cada worker reexecutaria a criação do próprio pool
recursivamente.</li>
</ul>

<h3>9. Guia rápido: qual modelo para qual problema</h3>
<table>
<thead><tr><th>Caso</th><th>Escolha</th></tr></thead>
<tbody>
<tr><td>20 chamadas HTTP em script único</td><td>ThreadPoolExecutor (simples)</td></tr>
<tr><td>Servidor web com 1000+ conexões</td><td>asyncio + uvicorn/FastAPI</td></tr>
<tr><td>Processar 50 GB de logs com regex</td><td>ProcessPoolExecutor</td></tr>
<tr><td>Hash de muitos arquivos</td><td>ProcessPoolExecutor</td></tr>
<tr><td>Numpy/Polars cálculos</td><td>Já libera o GIL, threads bastam</td></tr>
<tr><td>Apenas alguns segundos sequenciais</td><td>Não otimize</td></tr>
</tbody></table>
<p>A regra por trás da tabela: identifique se o gargalo é ESPERAR
(rede, disco — threads ou asyncio ajudam, porque o GIL libera durante a
espera) ou CALCULAR (CPU — só processos separados contornam o GIL de
verdade). Aplicar o modelo errado ao problema errado — threads para
CPU-bound, ou multiprocessing para uma única chamada HTTP — costuma
deixar o código mais lento e mais complexo que a versão sequencial mais
simples, pelo overhead de coordenação sem ganho real.</p>"""
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
                  ["A leitura de um arquivo grande feita em disco.", "Esperar a contagem de um timer chegar ao fim.", "Fazer chamadas de rede via HTTP para outro serviço."],
                  "GIL serializa execução de bytecode. Para CPU-bound, use "
                  "multiprocessing ou libs C que liberam o GIL."),
                q("Em asyncio, o que acontece se você chamar `time.sleep(5)` dentro de async?",
                  "Bloqueia todo o event loop por 5s, todas as outras tarefas pausam.",
                  ["Continua rodando em paralelo automaticamente, sem travar muito pouco.", "É tecnicamente equivalente a chamar `await asyncio.sleep(5)`.", "Lança uma exceção chamada `AsyncError`, que não existe."],
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
                  ["Escrever um loop manual controlando um contador junto de um `sleep`.", "Limitar diretamente o número de threads criadas pelo processo principal.", "Não existe alguma forma direta de limitar esse tipo de concorrência em asyncio."],
                  "Semaphore é o mecanismo padrão. Cada acquire decrementa, release "
                  "incrementa; bloqueia quando zerado."),
                q("`asyncio.to_thread(fn, *args)` é útil para...",
                  "Rodar função síncrona bloqueante sem congelar o event loop.",
                  ["Substituir por completo a necessidade de usar `asyncio.gather`.", "Aumentar de alguma forma a força do GIL do interpretador.", "Lançar uma exceção manualmente dentro de outra thread."],
                  "Move a chamada para um pool de threads, retorna corrotina que "
                  "espera o resultado. Ideal para integrar libs sync em async."),
                q("Race condition em threads acontece tipicamente quando:",
                  "Duas threads modificam estado compartilhado sem sincronização.",
                  ["O código importa uma quantidade grande demais de módulos diferentes.", "O processador da máquina onde o código roda tem várias cores disponíveis.", "O interpretador Python é considerado lento demais nesse tipo de cenário."],
                  "Operações compostas (count += 1) não são atômicas. Use Lock, "
                  "Queue ou estruturas thread-safe."),
                q("Para CPU-bound em Python puro, use:",
                  "ProcessPoolExecutor (multiprocessing).",
                  ["Usar `ThreadPoolExecutor`, que ainda compartilha o mesmo GIL.", "Usar `asyncio` combinado com `gather` para paralelizar.", "Criar instâncias de `concurrent.futures.Future` diretamente."],
                  "Processos contornam o GIL, usam todos os cores. Custo: serialização "
                  "via pickle entre processos."),
                q("Em multiprocessing no Windows, o código que dispara workers DEVE estar dentro de:",
                  "if __name__ == '__main__':",
                  ["try/except ao redor do disparo dos workers", "with usado como context manager qualquer", "async def no lugar de uma função comum"],
                  "Windows usa 'spawn' que re-executa o módulo no filho. Sem o guard, "
                  "o filho dispara workers de novo → fork bomb."),
                q("`asyncio.TaskGroup` (3.11+) tem qual vantagem sobre gather?",
                  "Cancelamento estruturado: se uma falhar, as outras são canceladas e erros vêm em ExceptionGroup.",
                  ["É consideravelmente mais rápido de executar na prática do que o próprio gather, suposição incorreta sobre como o sistema realmente se comporta sob estresse.", "Funciona rodando diretamente dentro de threads separadas do sistema operacional, suposição que raramente se sustenta fora do ambiente controlado de laboratório.", "Substitui por completo a necessidade de usar um Semaphore em qualquer cenário, que só aparece como problema depois que o sistema já está em produção."],
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
<div class="mermaid">
flowchart LR
    A["Escreve o teste"] --> B["Roda pytest"]
    B --> C{"Passou?"}
    C -- "Não, vermelho" --> D["Ajusta o código"]
    D --> B
    C -- "Sim, verde" --> E["Segue pro próximo caso"]
</div>

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
                  ["Vem com uma quantidade maior de funções built-in prontas.", "Costuma rodar mais rápido especificamente em máquinas Linux.", "É a única ferramenta capaz de medir cobertura de código."],
                  "pytest reduz boilerplate. fixtures, parametrize e plugins são o "
                  "diferencial."),
                q("`@pytest.mark.parametrize` é usado para:",
                  "Rodar o mesmo teste com múltiplos conjuntos de inputs.",
                  ["Configurar fixtures compartilhadas entre vários arquivos de teste.", "Marcar testes específicos como lentos para o CI.", "Pular a execução de testes específicos quando rodando em CI."],
                  "Cada linha do parametrize gera um caso de teste, com nome legível "
                  "indicando qual falhou."),
                q("`tmp_path` em pytest é:",
                  "Uma fixture built-in que dá um diretório temporário único por teste.",
                  ["Um atributo de classe definido manualmente pelo próprio desenvolvedor do teste.", "Uma chamada de função do sistema operacional feita diretamente pelo pytest.", "Uma variável de ambiente lida de forma automática pelo próprio pytest."],
                  "Cleanup automático ao fim do teste. Evita TemporaryDirectory manual."),
                q("Para verificar que uma função levanta uma exceção específica:",
                  "with pytest.raises(ValueError): ...",
                  ["assert raises(ValueError, fn) (função inexistente)", "try/except genérico ignorando o erro", "@pytest.expect(ValueError) (decorator inexistente)"],
                  "pytest.raises é o jeito idiomático. Aceita `match=` para checar "
                  "mensagem por regex."),
                q("Por que mockar chamadas externas em testes unitários?",
                  "Para testes serem rápidos, determinísticos e independentes da rede.",
                  ["Evita que logs desnecessários apareçam durante a execução dos testes.", "Aumenta automaticamente a porcentagem de cobertura medida.", "É uma exigência técnica imposta diretamente pelo próprio pytest."],
                  "Testes unitários devem rodar offline e em milissegundos. Mocks "
                  "isolam o código sob teste."),
                q("`monkeypatch.setenv('TOKEN', 'x')` em pytest:",
                  "Define a variável de ambiente apenas durante o teste; rollback automático.",
                  ["Modifica de forma permanente a variável de ambiente usada pelo sistema operacional.", "Grava um arquivo `.env` no disco durante a execução completa do teste.", "Só funciona corretamente quando os testes estão rodando em Linux."],
                  "monkeypatch desfaz tudo no teardown. Essencial para testar configs "
                  "via env."),
                q("Cobertura de 100% garante código sem bugs?",
                  "Não, só garante que cada linha foi executada, não que os casos de borda foram cobertos.",
                  ["Sim, desde que o código em questão seja considerado puro, sem efeito colateral algum, algo que passa no code review quando ninguém olha com atenção.", "Só garante isso de fato a partir especificamente da versão 3.12 do Python, decisão que cria dívida técnica silenciosa, sem gerar erro imediato.", "Sim, cobertura de 100% garante que o código está livre de qualquer tipo de bug, erro típico de configuração feita às pressas, sem revisão posterior."],
                  "Cobertura é métrica de presença, não de qualidade. Casos de borda "
                  "(None, listas vazias, valores extremos) precisam ser explícitos."),
                q("Para testar código async com pytest, instale:",
                  "pytest-asyncio e use @pytest.mark.asyncio",
                  ["asyncio-test (pacote que não existe no PyPI)", "unittest.AsyncTestCase (classe que não existe)", "Não há suporte a código async no pytest puro"],
                  "pytest-asyncio é o plugin padrão. Configure mode='auto' no "
                  "pyproject.toml para evitar mark em todo teste."),
                q("Onde colocar fixtures que múltiplos arquivos de teste compartilham?",
                  "conftest.py no diretório de testes.",
                  ["Num arquivo `fixtures.py` importado manualmente em cada teste.", "Dentro de um plugin externo instalado separadamente via pip.", "Duplicada dentro de cada arquivo de teste individualmente."],
                  "conftest.py é detectado automaticamente. Útil para fixtures globais "
                  "(client HTTP fake, DB de teste, etc.)."),
                q("`pytest -m \"not slow\"` faz o quê?",
                  "Roda apenas testes não marcados com @pytest.mark.slow.",
                  ["Roda os testes mais lentos primeiro, antes dos demais.", "Apenas define um nome customizado para a suíte de testes.", "Causa um erro de sintaxe assim que o pytest interpreta a expressão."],
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
<div class="mermaid">
flowchart LR
    Src["Código-fonte"] --> Pyproject["pyproject.toml"]
    Pyproject --> Build["uv build"]
    Build --> Wheel["wheel e sdist na pasta dist"]
    Wheel --> Publish["Publica no índice de pacotes"]
</div>


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
                  ["Reduz consideravelmente o uso de disco em comparação com instalar global.", "É uma convenção estética, sem diferença real de comportamento.", "Deixa a instalação de pacotes consideravelmente mais rápida."],
                  "Sem venv, projetos brigam por versões e você pode quebrar o pacote "
                  "do SO instalando lib global."),
                q("O `pyproject.toml` substitui historicamente:",
                  "setup.py, setup.cfg e requirements.txt em muitos casos.",
                  ["Não substitui muito pouco de fato, funciona só como metadata extra.", "Substitui só o arquivo `requirements.txt` usado no projeto.", "Substitui só o `Makefile` usado para automatizar tarefas."],
                  "PEP 517/518/621 trouxeram pyproject.toml como arquivo de configuração "
                  "central de build, deps e ferramentas."),
                q("`uv add requests` faz o quê?",
                  "Instala requests no ambiente do projeto e atualiza pyproject.toml/uv.lock.",
                  ["Instala o pacote de forma global no sistema, fora do ambiente do projeto atual.", "Cria um virtualenv inteiramente novo cada vez que o comando é chamado.", "Só baixa o tarball do pacote, sem de fato instalar coisa alguma."],
                  "Equivalente a `pip install requests + atualizar requirements`. "
                  "uv mantém lockfile determinístico."),
                q("`ruff` substitui qual conjunto de ferramentas?",
                  "flake8, pylint, isort e black (lint + formatter).",
                  ["O framework de testes `pytest`, usado para rodar a suíte.", "Só o verificador de tipos estáticos `mypy`.", "As ferramentas de gestão de pacote `pip` e `venv`."],
                  "ruff é um único binário (Rust) que faz lint, ordenação de imports e "
                  "formatação. Não é type checker."),
                q("O 'src layout' (pacote em src/) tem qual vantagem prática?",
                  "Força instalar o pacote para testar, testes rodam no que será publicado.",
                  ["É uma exigência formal imposta diretamente pelo próprio índice oficial do PyPI.", "Deixa o `pip` consideravelmente mais rápido no momento de instalar o pacote.", "Permite manter múltiplos pacotes dentro de um mesmo repositório de código."],
                  "Sem src/, `import meu_pkg` pode pegar o código avulso do diretório "
                  "atual, não a versão instalada, bugs de empacotamento ficam ocultos."),
                q("`pre-commit install` configura o quê?",
                  "Hooks de Git que rodam linters/formatters antes de cada commit.",
                  ["É um apelido interno para `pip install -e .`, muito pouco mais.", "Instala o binário do pacote diretamente na pasta `/usr/bin`.", "Cria um novo virtualenv isolado dentro do projeto."],
                  "Os hooks impedem commit de código fora do padrão. Em time, "
                  "elimina discussão de estilo em PR."),
                q("Para uma dependência usada apenas em desenvolvimento (ex: pytest), você usa:",
                  "[project.optional-dependencies] ou um grupo de dev no uv.",
                  ["Adicionar normalmente dentro da lista principal de `dependencies`.", "Instalar a dependência de forma global, direto no sistema.", "Compilar manualmente o pacote a partir do código-fonte."],
                  "Optional/dev deps não vão para o usuário final que instalar seu "
                  "pacote. Mantém o package final enxuto."),
                q("`mypy --strict` em código legado costuma:",
                  "Gerar muitos erros de cara (type hints ausentes, Any implícito).",
                  ["Substituir por completo a necessidade de manter testes.", "Rodar de forma praticamente instantânea, sem apontar erro algum.", "Causar um segfault direto no processo do verificador de tipos."],
                  "Strict ativa todas as regras. Em legado, comece sem strict e "
                  "ative módulo por módulo."),
                q("`uv build` produz:",
                  "Um arquivo .whl (wheel) e um sdist .tar.gz na pasta dist/.",
                  ["Um `Dockerfile` pronto para buildar a imagem do projeto.", "Um binário já compilado diretamente na linguagem C.", "Só o tarball original do código-fonte, sem mais muito pouco."],
                  "Wheel é o formato binário moderno (rápido de instalar). sdist é o "
                  "código-fonte. Ambos vão para o PyPI."),
                q("Configuração centralizada no pyproject.toml ajuda a evitar:",
                  "Inconsistências entre dev e CI sobre versão de regras de lint, format e types.",
                  ["Conflitos de import entre módulos que compartilham o mesmo nome no projeto, decisão que funciona no papel, mas não sobrevive ao primeiro incidente real.", "Deadlocks que costumam acontecer só depois que o código já está em produção, prática que gera falso senso de segurança no time.", "Falhas relacionadas à resolução de nomes de DNS durante o pipeline de CI, atalho que troca segurança por conveniência de curto prazo."],
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
                """<h3>1. AWS com `boto3`: identidade, paginação e credenciais que nunca ficam no código</h3>
<pre><code>import boto3

s3   = boto3.client("s3")
ec2  = boto3.resource("ec2")
sts  = boto3.client("sts")

# Identidade efetiva (saber em qual conta/role você está)
ident = sts.get_caller_identity()
print(ident["Arn"])

# Listar buckets paginando
for b in s3.list_buckets()["Buckets"]:
    print(b["Name"], b["CreationDate"])

# Listar instâncias EC2 com filtro
for inst in ec2.instances.filter(
    Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
):
    name = next((t["Value"] for t in (inst.tags or []) if t["Key"] == "Name"), "-")
    print(inst.id, name, inst.instance_type, inst.private_ip_address)</code></pre>
<p><code>sts.get_caller_identity()</code> antes de qualquer operação
destrutiva é um hábito barato que evita um erro caro: rodar um script
contra a conta AWS errada porque o profile ativo não era o esperado —
imprimir o ARN confirma exatamente quem você é antes de continuar.
Muitas chamadas da AWS (listar objetos de um bucket, instâncias, logs)
não devolvem tudo de uma vez — devolvem uma página com um token para a
próxima. Chamar <code>list_objects_v2</code> direto numa conta com
milhões de objetos devolve só os primeiros mil silenciosamente, sem erro
algum indicando que faltou o resto; <code>client.get_paginator(...)</code>
resolve isso internamente, iterando todas as páginas automaticamente.</p>
<div class="mermaid">
flowchart LR
    EC2["Instância EC2"] --> Role["IAM Role anexado"]
    Role --> IMDS["Credenciais via IMDS"]
    IMDS --> SDK["boto3 usa automaticamente"]
</div>

<p>Sobre credenciais: hardcoded no código é a violação mais básica e mais
citada de segurança em nuvem — qualquer coisa commitada permanece no
histórico do git mesmo depois de removida num commit seguinte. Rodando
dentro da própria AWS (EC2, EKS, Lambda), um IAM Role anexado à instância
entrega credenciais temporárias automaticamente via metadata service, sem
nenhum segredo para vazar ou rotacionar manualmente. <code>botocore</code>
já faz retry automático em erros transitórios, mas vale configurar
<code>Config(retries={"mode": "adaptive"})</code> quando a conta sofre
throttling (limite de requisições por segundo) da própria AWS.</p>

<h3>2. Kubernetes com o client oficial: uma ferramenta, dois ambientes</h3>
<pre><code>from kubernetes import client, config

# Auto-detect: kubeconfig local ou ServiceAccount in-cluster
try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1 = client.CoreV1Api()
apps = client.AppsV1Api()

# Listar pods em todos os namespaces
for p in v1.list_pod_for_all_namespaces().items:
    print(p.metadata.namespace, p.metadata.name, p.status.phase)

# Reiniciar deployment (padrão kubectl rollout restart)
import datetime
patch = {
    "spec": {"template": {"metadata": {"annotations": {
        "kubectl.kubernetes.io/restartedAt": datetime.datetime.utcnow().isoformat()
    }}}}
}
apps.patch_namespaced_deployment("web", "prod", patch)</code></pre>
<p>O padrão try/except aqui não é tratamento de erro genérico — é
DETECÇÃO DE AMBIENTE: <code>load_incluster_config()</code> só funciona
quando o script roda DENTRO de um pod (lê o token de ServiceAccount
montado automaticamente em <code>/var/run/secrets/...</code>); fora de um
cluster, essa leitura falha com <code>ConfigException</code>, e o
<code>except</code> cai para o kubeconfig local que você usa no laptop.
Essa dupla checagem é o que permite escrever a MESMA ferramenta e rodá-la
tanto localmente durante desenvolvimento quanto como um Job dentro do
próprio cluster em produção, sem nenhuma flag ou variável extra. O truque
do "restart" de deployment merece nota: o Kubernetes não tem um comando
nativo de restart — <code>kubectl rollout restart</code> por baixo só
muda uma annotation no template do pod, o que o controller de deployment
interpreta como "configuração mudou" e dispara um rollout normal,
substituindo os pods gradualmente.</p>

<h3>3. Watch: reagir a eventos em vez de perguntar em loop</h3>
<pre><code>from kubernetes import watch

w = watch.Watch()
for event in w.stream(v1.list_namespaced_pod, namespace="prod", timeout_seconds=0):
    pod = event["object"]
    if event["type"] in ("ADDED", "MODIFIED") and pod.status.phase == "Failed":
        notify_slack(f"Pod {pod.metadata.name} falhou")</code></pre>
<p><code>Watch</code> abre uma conexão de long-polling com o API Server:
em vez de perguntar "o que mudou?" a cada N segundos (polling, que
desperdiça requisições e atrasa a reação até o próximo ciclo), o servidor
EMPURRA cada evento (pod criado, modificado, removido) assim que
acontece. É o mecanismo por trás de qualquer operador ou controller
customizado do Kubernetes — inclusive dos controllers embutidos do
próprio kube-apiserver — e é a base certa para alertas específicos que o
kube-prometheus padrão não cobre.</p>

<h3>4. Métricas Prometheus: instrumentar um serviço que fica de pé</h3>
<pre><code># pip install prometheus-client
from prometheus_client import Counter, Histogram, start_http_server
import time, random

deploys = Counter("deploys_total", "Total de deploys", ["env", "status"])
durations = Histogram("deploy_duration_seconds", "Duração de deploys")

start_http_server(9090)        # /metrics

while True:
    env = random.choice(["dev", "prod"])
    with durations.time():
        time.sleep(random.uniform(0.1, 1.0))
    deploys.labels(env=env, status="success").inc()</code></pre>
<p><code>Counter</code> só sobe (contagem cumulativa — total de deploys
desde o início do processo); <code>Histogram</code> registra a
DISTRIBUIÇÃO de uma medida (aqui, duração), permitindo calcular
percentis depois (p50, p95, p99) em vez de só uma média que esconde
outliers. O endpoint <code>/metrics</code> que <code>start_http_server</code>
expõe é passivo: ele só responde quando o Prometheus vem "puxar"
(scrape) periodicamente — funciona bem para um serviço de longa duração,
mas quebra para um job que termina antes do próximo scrape acontecer
(seção 5).</p>

<h3>5. Pushgateway: métricas de um job que já morreu quando alguém for olhar</h3>
<pre><code>from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

reg = CollectorRegistry()
g = Gauge("backup_last_success_unix", "Timestamp do último backup", registry=reg)
g.set_to_current_time()
push_to_gateway("pushgateway:9091", job="daily_backup", registry=reg)</code></pre>
<p>Um cron job ou um K8s Job roda por alguns segundos e termina — se ele
expusesse um endpoint <code>/metrics</code> como na seção 4, o processo já
teria saído antes do Prometheus conseguir fazer scrape, e a métrica nunca
chegaria a ser coletada. O Pushgateway inverte o fluxo: o JOB empurra a
métrica ativamente para um serviço intermediário que fica de pé, e o
Prometheus faz scrape DESSE intermediário (que sempre está disponível),
não do job efêmero diretamente. É o único caso legítimo de "empurrar"
métricas em vez do modelo pull padrão do Prometheus.</p>

<h3>6. CI customizado: um gate que bloqueia licença proibida antes do merge</h3>
<pre><code>import json, subprocess, sys

BLOCKED = {"GPL-3.0", "GPL-2.0", "AGPL-3.0"}

out = subprocess.run([
    "uv", "pip", "list", "--format", "json"
], capture_output=True, text=True, check=True)
pkgs = json.loads(out.stdout)

violations = []
for p in pkgs:
    meta = subprocess.run(["pip", "show", p["name"]],
                          capture_output=True, text=True, check=True).stdout
    license_line = next((l for l in meta.splitlines() if l.startswith("License:")), "")
    lic = license_line.replace("License:", "").strip()
    if lic in BLOCKED:
        violations.append((p["name"], lic))

if violations:
    for n, lic in violations:
        print(f"::error:: {n} usa licença bloqueada {lic}", file=sys.stderr)
    sys.exit(1)
print("OK, nenhuma licença bloqueada.")</code></pre>
<p>O ponto pedagógico aqui é que esse script não usa nenhuma API nova —
é a combinação de tudo visto nas aulas anteriores: <code>subprocess.run</code>
com lista de argumentos (aula 6.6), parsing de JSON (aula 6.4), saída em
stderr com código de saída específico (aula 6.4). Um "CI customizado" na
prática é quase sempre exatamente isso: automação comum aplicada a uma
regra de negócio específica. <code>::error::</code> é sintaxe própria do
GitHub Actions que transforma essa linha de log numa anotação visível
diretamente no diff do Pull Request, sem precisar abrir o log completo
do job para descobrir o que falhou.</p>

<h3>7. Notificação: transformar falha silenciosa em alerta visível</h3>
<pre><code>import os, requests

def slack_alert(text: str, channel: str = "#alerts"):
    url = os.environ["SLACK_WEBHOOK_URL"]
    r = requests.post(url, json={"text": text, "channel": channel}, timeout=5)
    r.raise_for_status()

try:
    deploy_to_prod()
except Exception as e:
    slack_alert(f":rotating_light: Deploy falhou: `{e}`")
    raise</code></pre>
<p>Note o <code>raise</code> no final do <code>except</code>: o alerta é
um EFEITO COLATERAL da falha, não uma forma de "tratá-la" e seguir em
frente. Sem relançar, um script que engole a exceção depois de notificar
pareceria ter terminado com sucesso para qualquer sistema de automação
que só olha o código de saída do processo — o Slack avisaria um humano,
mas o pipeline de CI marcaria o job como verde, uma contradição perigosa
entre o que o alerta diz e o que o sistema registra oficialmente.</p>

<h3>8. Operadores customizados com `kopf`: extensões nativas do Kubernetes</h3>
<p>Quando o comportamento desejado é "quando um CRD (Custom Resource) for
criado, faça algo externo ao cluster" (por exemplo, criar um bucket S3
correspondente), <code>kopf</code> reduz o boilerplate de escrever um
operador do zero a decoradores simples:</p>
<pre><code># pip install kopf
import kopf

@kopf.on.create("example.com", "v1", "buckets")
def create_bucket(spec, name, **kwargs):
    boto3.client("s3").create_bucket(Bucket=spec["name"])
    return {"createdBucket": spec["name"]}

@kopf.on.delete("example.com", "v1", "buckets")
def delete_bucket(spec, **kwargs):
    boto3.client("s3").delete_bucket(Bucket=spec["name"])</code></pre>
<p>Por baixo, <code>kopf</code> usa exatamente o mecanismo de Watch da
seção 3 — ele assina eventos de criação/atualização/remoção do recurso
customizado e chama a função decorada correspondente. O ganho é não
precisar escrever esse loop de watch, reconexão em caso de queda, e
tratamento de erro manualmente a cada operador novo.</p>

<h3>9. Checklist para ferramentas DevSecOps que outras pessoas vão rodar</h3>
<ul>
<li>Saída em JSON quando o consumidor é máquina (outro script, um
pipeline); texto legível quando é humano — decidir isso cedo evita
reescrever a saída depois que alguém já depende do formato antigo.</li>
<li>Códigos de saída específicos por categoria de falha (validação,
rede, permissão) — permite ao chamador reagir diferente a cada tipo, não
só "deu erro, algo".</li>
<li>Logue o comando exato e os parâmetros usados — auditoria
essencialmente gratuita, e a primeira coisa que se precisa quando algo em
produção precisa ser investigado depois do fato.</li>
<li>Idempotência: rodar duas vezes não deve causar problema — verifique
se o recurso já existe antes de criar, em vez de deixar a segunda
execução falhar com "já existe" como se fosse um erro real.</li>
<li>Suporte a <code>--dry-run</code> em qualquer ferramenta que crie,
modifique ou apague algo — a diferença entre testar em produção com
segurança e descobrir um bug depois que o dano já foi feito.</li>
<li>Nunca armazene credenciais em log ou saída padrão, mesmo
parcialmente — se precisar mostrar QUE um token foi usado, mostre só um
prefixo (<code>token[:4] + "***"</code>), nunca o valor inteiro nem
mesmo em ambiente de debug.</li>
<li>Registre tempo de execução como métrica (Histogram) — uma regressão
de performance silenciosa (a ferramenta continua funcionando, só fica
mais lenta a cada semana) só aparece com dado histórico, nunca olhando
uma execução isolada.</li>
</ul>"""
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
                  ["Deixar as credenciais escritas diretamente dentro do arquivo `config.py`.", "Configurar um fluxo de OIDC integrado a um Vault externo, mesmo já dentro da AWS.", "Guardar as credenciais dentro de variáveis definidas em `/etc/environment`."],
                  "IAM Role + IMDSv2 é a forma segura. Sem credenciais persistidas, "
                  "sem rotação manual."),
                q("`config.load_incluster_config()` falha quando rodando localmente. Como tratar?",
                  "Tentar primeiro e cair para `load_kube_config()` em ConfigException.",
                  ["Usar só `load_kube_config()` em qualquer ambiente, sem tentar o outro.", "Forçar manualmente a variável de ambiente `KUBECONFIG`.", "Não existe outra forma, é preciso rodar dentro de um container."],
                  "Padrão clássico: tenta in-cluster (vê /var/run/secrets/...); "
                  "se não, usa kubeconfig local. Mesma ferramenta funciona em ambos "
                  "contextos."),
                q("Para um job batch que termina, expor métricas Prometheus como?",
                  "Empurrar para Pushgateway com push_to_gateway.",
                  ["Simplesmente não é possível coletar métricas desse tipo de job.", "Salvar as métricas manualmente num arquivo `.prom` local.", "Iniciar um servidor HTTP que continua de pé mesmo após o job terminar."],
                  "Pushgateway armazena temporariamente as métricas para Prometheus "
                  "scrape. É o padrão para jobs efêmeros."),
                q("Para listar todos os objetos de um bucket S3 grande:",
                  "client.get_paginator('list_objects_v2').paginate(Bucket=name)",
                  ["client.list_objects(Bucket=name, MaxKeys=1000, Prefix='', Marker='')", "boto3.list_all(Bucket=name, recursive=True, retry=3, timeout=30)", "ec2.objects.all(Bucket=name, filter=True, limit=None, sort='asc')"],
                  "list_objects_v2 retorna 1000 itens por página. Paginator itera "
                  "automaticamente todas as páginas."),
                q("`subprocess.run([..., 'aws', 's3', 'cp', ...])` vs. boto3, qual a vantagem do boto3?",
                  "Type-safe, tratamento de erros pythonic, sem dependência do CLI instalado.",
                  ["Dispensa qualquer tipo de configuração prévia de credencial na máquina.", "É consideravelmente mais rápido de executar na prática do que usar o CLI.", "Continua funcionando normalmente mesmo sem qualquer conexão de rede disponível."],
                  "boto3 retorna dicts e levanta exceções tipadas. subprocess depende "
                  "do CLI estar no PATH e tem overhead de serialização JSON."),
                q("Para reagir a eventos em tempo real no K8s, use:",
                  "kubernetes.watch.Watch().stream(...)",
                  ["ETag controlado manualmente a cada chamada", "polling com sleep(60) entre chamadas", "Só via CLI, sem qualquer suporte no SDK Python"],
                  "Watch usa long-polling do API Server: receberia eventos imediatos. "
                  "Polling é desperdício de quota e atrasa reação."),
                q("Em uma ferramenta de CI, a saída idealmente vai em JSON quando:",
                  "O consumidor é outra ferramenta (script, pipeline).",
                  ["A saída deveria ir em JSON em qualquer cenário, mesmo lida por humano.", "Só quando a ferramenta está rodando já em produção.", "Só quando a execução termina encontrando algum erro."],
                  "Humanos preferem texto formatado; máquinas preferem JSON. Idiomático: "
                  "flag --json para alternar."),
                q("`::error file=app.py,line=10::Erro X` em GitHub Actions...",
                  "Cria uma annotation no arquivo/linha indicado no PR.",
                  ["Faz a action inteira falhar automaticamente assim que aparece.", "É tratado como um comentário qualquer, sem efeito especial.", "É só um print colorido exibido no terminal do runner."],
                  "Workflow commands. ::error gera annotation; ::warning idem; "
                  "::set-output (deprecado em favor de $GITHUB_OUTPUT)."),
                q("Boa prática para ferramentas destrutivas (delete, drop):",
                  "Implementar --dry-run que mostra o que faria sem executar.",
                  ["Fazer rollback automático depois de qualquer execução destrutiva.", "Só registrar logs quando a ferramenta roda em produção.", "Pedir uma senha extra em grande parte da execução da ferramenta."],
                  "Dry-run é o equivalente de `terraform plan`. Permite revisar antes "
                  "de aplicar; vital para evitar erros operacionais."),
                q("Idempotência em scripts DevOps significa:",
                  "Rodar o mesmo script várias vezes leva ao mesmo estado, sem efeitos colaterais extras.",
                  ["Significa que o script só pode ser executado uma única vez ao longo do tempo, abordagem que funciona bem até o primeiro pico de carga real.", "Significa que o script já vem com um mecanismo de retry embutido internamente, prática que gera falso senso de segurança no time.", "Significa que o script em questão não faz qualquer operação de I/O, comportamento que confunde quem está debugando meses depois."],
                  "Ex: 'criar bucket' deveria checar se existe primeiro. Idempotência "
                  "é base de Ansible, Terraform e bons pipelines de deploy."),
            ],
        },
    ],
}
