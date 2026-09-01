"""Fase 6, Programação em Python para DevOps & DevSecOps."""
from ._helpers import m, q

PHASE6 = {
    "name": "Fase 6: Programação em Python para DevOps",
    "name_en": "Phase 6: Python Programming for DevOps",
    "description": (
        "A linguagem 'cola' do mundo de operações: scripts, automação, "
        "ferramentas internas, APIs e integração com nuvem e Kubernetes."
    ),
    "description_en": (
        "The 'glue' language of the operations world: scripts, automation, "
        "internal tools, APIs and integration with cloud and Kubernetes."
    ),
    "topics": [
        # =====================================================================
        # 6.1 Fundamentos de Python moderno
        # =====================================================================
        {
            "title": "Fundamentos de Python moderno",
            "title_en": "Modern Python Fundamentals",
            "summary": "Sintaxe, tipos, controle de fluxo, funções e type hints, a base que todo script de produção assume.",
            "summary_en": "Syntax, types, control flow, functions and type hints, the foundation every production script assumes.",
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
                "intro_en": (
                    "Python is the de facto language of the DevOps world. It powers the "
                    "official clients for AWS (boto3), Kubernetes, GCP, Ansible, SaltStack, "
                    "Apache Airflow, Jupyter, and thousands of scripts <em>gluing</em> tools "
                    "together in real pipelines. This first lesson covers the subset that "
                    "shows up most in production code, not the textbook version, but the one "
                    "you need to read and write every day.<br><br>"
                    "We'll focus on Python 3.11+ (recommended target version): pattern "
                    "matching, type hints and improved error messages changed a lot about how "
                    "modern tools are written."
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
    Nome["Nome: x"] --> Obj["Objeto no heap"]
    Obj --> Attrs["Atributos e métodos"]
    Tipo["int / str / list / função"] --> Obj
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
<div class="mermaid">
flowchart LR
    A["def f(x=[])"] --> B["Lista criada uma vez, na definição"]
    B --> C["Toda chamada sem argumento reusa a MESMA lista"]
    C --> D["Estado vaza entre chamadas"]
</div>
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Evite</strong><p>Usar == em float, is no lugar de ==, type(x) == int, abrir arquivo sem with.</p></div>
    <div class="lesson-viz-card"><strong>Prefira</strong><p>math.isclose(), == para valor, isinstance(), context managers.</p></div>
  </div>
  <figcaption>Erros clássicos: o idioma errado costuma funcionar até falhar em produção.</figcaption>
</figure>
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
                "body_en": (
                """<h3>1. Primitive types and the object model that explains everything</h3>
<p>In Python, <strong>everything is an object</strong> — integers, strings,
functions and classes all equally have attributes and methods, and are all
allocated on the heap and referenced by name. This uniformity is what
makes Python so flexible (you can pass a function as an argument the same
way you pass a number), and it's also the root of behaviors that surprise
people coming from languages with "real" primitive types (section 2).</p>
<div class="mermaid">
flowchart LR
    Name["Name: x"] --> Obj["Object on the heap"]
    Obj --> Attrs["Attributes and methods"]
    Type["int / str / list / function"] --> Obj
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
<p>The difference between <code>list</code> and <code>tuple</code> isn't
just syntax: <code>tuple</code> is immutable, and being immutable makes it
<em>hashable</em> — it can become a dictionary key or a <code>set</code>
item. <code>list</code> can't, because its contents can change after
insertion, which would break the hash structure that already computed a
position for it. For the same reason, <code>str</code> is immutable: every
operation that "modifies" a string actually creates a new string. That has
a real cost — concatenating in a loop with <code>+=</code> allocates a new
string on every iteration, an O(n²) behavior for n concatenations;
<code>"".join(list)</code> allocates only once, O(n).</p>

<h3>2. Variables are names, not boxes: why assignment doesn't copy</h3>
<p>People coming from languages where a variable is a "box with a value"
get a shock the first time this happens:</p>
<pre><code>a = [1, 2, 3]
b = a               # b aponta para o MESMO objeto
b.append(4)
print(a)            # [1, 2, 3, 4]  ← surpresa para iniciantes

import copy
c = copy.copy(a)        # cópia rasa
d = copy.deepcopy(a)    # cópia profunda</code></pre>
<p>In Python, a variable is just a NAME pointing to an object that exists
independently of it. <code>b = a</code> doesn't copy the content — it
creates a second name pointing to the same object in memory. Modifying the
object through either name affects what the other name "sees", because
there aren't two objects, there's one with two labels. This only surprises
people with MUTABLE objects (lists, dicts); with <code>int</code> or
<code>str</code> (immutable) the effect never shows up, because any
"modification" already creates a new object instead of altering the
existing one — hence the confusion of people who only tested with numbers
before testing with lists.</p>
<p>Name scoping follows the <strong>LEGB</strong> rule: Local → Enclosing →
Global → Built-in — the interpreter searches in that order until it finds
the name. To WRITE (not just read) to an outer scope from inside a
function, you need an explicit <code>global</code> or
<code>nonlocal</code>; without it, an assignment inside the function
always creates a NEW LOCAL variable, even if a name with the same name
exists outside — one of the most common and confusing mistakes for
beginners (the function seems to "not see" the outer variable, when it
actually created a local shadow of it).</p>

<h3>3. `for` iterates over iterables, not over positions</h3>
<pre><code>servers = ["web1", "web2", "db1"]
ports   = [80, 80, 5432]

for i, name in enumerate(servers, start=1):
    print(f"#{i} {name}")

for name, port in zip(servers, ports, strict=True):
    print(f"{name} :{port}")</code></pre>
<p><code>for i in range(len(lista)): item = lista[i]</code> works, but it
manually reimplements what <code>enumerate</code> already does — and
signals to anyone reading the code that you may not know the language's
idiom, which raises doubts about the rest of the code too. <code>zip(...,
strict=True)</code> (3.10+) is the detail worth knowing: without
<code>strict</code>, zipping two lists of different sizes silently
truncates to the shorter one — a "why did I only process half the
servers" bug that raises no error at all, just an incomplete result.
<code>strict=True</code> raises <code>ValueError</code> if the sizes don't
match.</p>
<p><strong>Truthiness</strong>: in Python, <code>0</code>, <code>None</code>,
empty collections and <code>False</code> are all <em>falsy</em> — not
because they're magically converted to boolean, but because every object
implements (or inherits) a <code>__bool__</code> or <code>__len__</code>
method that decides this. <code>if len(lst) &gt; 0:</code> works, but
<code>if lst:</code> uses exactly this mechanism and is the expected
idiom. Comparing explicitly with <code>True</code>/<code>False</code>
(<code>if x == True</code>) is redundant and fragile: prefer
<code>if x:</code>, and for <code>None</code> specifically use
<code>is None</code> — identity comparison, not value comparison, because
there is exactly ONE <code>None</code> object in the entire process's
memory.</p>

<h3>4. `match`: structural destructuring, not a disguised switch</h3>
<p>People seeing <code>match</code> for the first time tend to treat it as
a C <code>switch</code> — but it does much more: each <code>case</code>
tries to DESTRUCTURE the value against a pattern, extracting variables in
the process, not just comparing equality:</p>
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
<p>The first <code>case</code> only matches if the dict has EXACTLY
<code>type="deploy"</code> and <code>env="prod"</code>, and that match
already extracts <code>img</code> as a local variable — without this
feature, you'd write three nested <code>if</code>s manually checking each
key. The <code>if v &lt; 10</code> clause in the third case (a "guard")
allows an additional condition beyond the shape. It's the right pattern
for parsing webhook payloads, queue events (SQS, Pub/Sub) or CloudEvents,
where the JSON shape varies depending on the event type.</p>

<h3>5. Functions: why `*` exists and why a mutable default is a trap</h3>
<div class="mermaid">
flowchart LR
    A["def f(x=[])"] --> B["List created once, at definition time"]
    B --> C["Every call without an argument reuses the SAME list"]
    C --> D["State leaks across calls"]
</div>
<pre><code>def deploy(
    image: str,                       # posicional
    *,                                # tudo depois é keyword-only
    replicas: int = 3,
    canary: bool = False,
    extra_env: dict[str, str] | None = None,
) -&gt; bool:
    ...

deploy("web:1.2", replicas=5, canary=True)</code></pre>
<p>The lone <code>*</code> in the signature doesn't receive anything — it's
a marker: everything after it can only be passed by name in the call.
Without it, <code>deploy("web", 5, True)</code> would compile and run, but
no one reading that call knows what "5" and "True" mean without checking
the signature; forcing keyword-only here turns the call into
self-documenting.</p>
<p>The most cited bug in the language is <code>def f(x=[]):</code>. A
parameter's default value is evaluated ONCE, at the moment the function is
defined (not on every call) — so that empty list is created a single time
and reused as the SAME object on every subsequent call that doesn't pass
<code>x</code> explicitly. If one call does <code>x.append(1)</code>, the
next call with no argument receives the list already carrying that item, a
completely invisible state leak between calls for anyone just looking at
the signature. The correct idiom is
<code>def f(x=None): x = x if x is not None else []</code>, creating a
genuinely new list on every call.</p>

<h3>6. Type hints: a contract for tooling, not for the interpreter</h3>
<p>Type annotations do NOT change runtime behavior — Python remains
dynamically typed, and nothing actually prevents passing a string where
the signature expects an <code>int</code>. The value lies entirely in
tools that read those annotations without executing the code:
mypy/pyright catch the type mismatch at review time (before running a
single test), the editor gets real type-based autocomplete, and the
signature becomes documentation that can't silently go stale, because the
type checker complains if it lies.</p>
<pre><code>from typing import Iterable, Protocol

def total(items: Iterable[float]) -&gt; float:
    return sum(items)

class Storer(Protocol):
    def save(self, key: str, blob: bytes) -&gt; None: ...

def upload(s: Storer, k: str, b: bytes) -&gt; None:
    s.save(k, b)   # qualquer classe com .save() compatível serve</code></pre>
<p><code>Protocol</code> is structural typing — <code>upload</code>
accepts ANY object that has a <code>save(key, blob)</code> method with
that signature, without needing to explicitly inherit from
<code>Storer</code> ("if it walks like a duck..."). Useful for decoupling
code from a concrete implementation (an S3 client, a local disk client)
without forced inheritance. In 3.10+, prefer <code>X | Y</code> over
<code>Union[X, Y]</code> and <code>list[int]</code> over
<code>List[int]</code> — native syntax, no extra <code>typing</code>
import needed.</p>

<h3>7. F-strings: formatting and why to avoid them in logging</h3>
<pre><code>name, port = "web", 80
print(f"{name}:{port}")             # web:80
print(f"{name:&gt;10}|{port:05d}")    # padding e zero-pad
print(f"{3.14159:.2f}")             # 3.14
print(f"{name=}, {port=}")           # debug: name='web', port=80</code></pre>
<p>F-strings are evaluated IMMEDIATELY, at the point the line runs — that's
why <code>logger.info(f"deploying {name}")</code> is a discouraged
practice: the interpolation (formatting the string) always happens, even
if the DEBUG/INFO log level is disabled and the message is discarded
without ever being written. <code>logger.info("deploying %s", name)</code>
passes the arguments separately, and logging only formats the string if it
will actually emit the log — real CPU savings in systems generating many
debug logs turned off in production.</p>

<h3>8. Classic mistakes from people coming from another language</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Avoid</strong><p>Using == on floats, is instead of ==, type(x) == int, opening files without with.</p></div>
    <div class="lesson-viz-card"><strong>Prefer</strong><p>math.isclose(), == for value, isinstance(), context managers.</p></div>
  </div>
  <figcaption>Classic mistakes: the wrong idiom often works until it fails in production.</figcaption>
</figure>
<ul>
<li>Comparing floats with <code>==</code>: floating point has rounding
error (<code>0.1 + 0.2 != 0.3</code> in Python, as in most languages); use
<code>math.isclose()</code>.</li>
<li>Confusing <code>is</code> with <code>==</code>: <code>is</code>
compares IDENTITY (is it the same object in memory?), <code>==</code>
compares VALUE (calls <code>__eq__</code>). Two objects can have the same
value without being the same object.</li>
<li>Using <code>type(x) == int</code> instead of <code>isinstance(x, int)</code>:
the first rejects subclasses of <code>int</code>; the second accepts them
— important in code that receives objects from libraries that may
subclass built-in types.</li>
<li>Not using context managers: files, locks and connections opened
without <code>with</code> end up depending on the garbage collector to
close — in long-running processes (a daemon, a server), this leaks file
descriptors until the process crashes.</li>
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
                "practical_en": (
                    "Create a script <code>checklog.py</code> that: (1) receives a log file "
                    "path via <code>sys.argv</code>; (2) opens it with "
                    "<code>with open()</code>; (3) counts lines containing "
                    "<code>ERROR</code>, <code>WARN</code>, <code>INFO</code>; (4) prints "
                    "a formatted summary using f-strings (fixed width). Use type hints on "
                    "every function and run <code>python -m mypy checklog.py</code> with no "
                    "errors."
                ),
            },
            "materials": [
                m("Python Tutorial, docs oficial",
                  "https://docs.python.org/3/tutorial/",
                  "docs", "Tutorial canônico, leitura obrigatória.",
                  title_en="Python Tutorial, official docs",
                  description_en="Canonical tutorial, required reading."),
                m("Real Python: Python Type Checking",
                  "https://realpython.com/python-type-checking/",
                  "article", "Guia prático de type hints.",
                  title_en="Real Python: Python Type Checking",
                  description_en="Practical guide to type hints."),
                m("PEP 8, Style Guide",
                  "https://peps.python.org/pep-0008/",
                  "docs", "Convenções de formatação que todos seguem.",
                  title_en="PEP 8, Style Guide",
                  description_en="Formatting conventions everyone follows."),
                m("PEP 634, Structural Pattern Matching",
                  "https://peps.python.org/pep-0634/",
                  "docs", "Especificação do match/case.",
                  title_en="PEP 634, Structural Pattern Matching",
                  description_en="Specification of match/case."),
                m("Trey Hunner: Python truthiness",
                  "https://treyhunner.com/2019/03/unique-and-sentinel-values-in-python/",
                  "article", "Por que `if x:` é melhor que `if x is True`.",
                  title_en="Trey Hunner: Python truthiness",
                  description_en="Why `if x:` is better than `if x is True`."),
                m("Anthony Sottile (anthonywritescode), YouTube",
                  "https://www.youtube.com/c/anthonywritescode",
                  "video", "Vídeos curtos sobre Python idiomático.",
                  title_en="Anthony Sottile (anthonywritescode), YouTube",
                  description_en="Short videos about idiomatic Python."),
            ],
            "questions": [
                q("Qual a saída de `a = [1, 2]; b = a; b.append(3); print(a)`?",
                  "[1, 2, 3]",
                  ["[1, 2]", "Erro de execução", "[3]"],
                  "Atribuição não copia em Python: `b` referencia o mesmo objeto que `a`. "
                  "Para copiar use `a.copy()` ou `copy.deepcopy(a)`.",
                  statement_en="What is the output of `a = [1, 2]; b = a; b.append(3); print(a)`?",
                  correct_en="[1, 2, 3]",
                  wrong_en=["[1, 2]", "Runtime error", "[3]"],
                  explanation_en="Assignment doesn't copy in Python: `b` references the same "
                  "object as `a`. To copy, use `a.copy()` or `copy.deepcopy(a)`."),
                q("Qual destes tipos NÃO pode ser chave de um dicionário?",
                  "list",
                  ["tuple", "str", "frozenset"],
                  "Chaves de dict precisam ser hashable (imutáveis). list é mutável, "
                  "logo não é hashable. tuple, str e frozenset são imutáveis.",
                  statement_en="Which of these types CANNOT be a dictionary key?",
                  correct_en="list",
                  wrong_en=["tuple", "str", "frozenset"],
                  explanation_en="Dict keys need to be hashable (immutable). list is mutable, "
                  "so it isn't hashable. tuple, str and frozenset are immutable."),
                q("Qual é a forma idiomática de checar se uma lista NÃO está vazia?",
                  "if lst:",
                  ["if len(lst) > 0:",
                   "if lst != []:",
                   "if lst is not None:"],
                  "Listas vazias são falsy. `if lst:` é claro e idiomático. "
                  "`is not None` checaria coisa diferente (existência da variável, não vazio).",
                  statement_en="What is the idiomatic way to check that a list is NOT empty?",
                  correct_en="if lst:",
                  wrong_en=["if len(lst) > 0:",
                            "if lst != []:",
                            "if lst is not None:"],
                  explanation_en="Empty lists are falsy. `if lst:` is clear and idiomatic. "
                  "`is not None` would check something different (variable existence, not emptiness)."),
                q("O que faz `*` na assinatura `def f(a, *, b, c):`?",
                  "Força b e c a serem passados como argumentos keyword-only.",
                  ["Torna os parâmetros seguintes opcionais, com valor default implícito.", "Recebe qualquer argumento extra passado como uma tupla.", "Gera um erro de sintaxe assim que o código é interpretado."],
                  "O `*` sozinho marca o limite: tudo depois precisa ser nomeado na chamada. "
                  "`*args` (com nome) é diferente, captura posicionais extras.",
                  statement_en="What does `*` do in the signature `def f(a, *, b, c):`?",
                  correct_en="Forces b and c to be passed as keyword-only arguments.",
                  wrong_en=["Makes the following parameters optional, with an implicit default value.", "Receives any extra argument passed as a tuple.", "Raises a syntax error as soon as the code is parsed."],
                  explanation_en="The lone `*` marks the boundary: everything after it must be "
                  "named in the call. `*args` (with a name) is different, it captures extra "
                  "positional arguments."),
                q("Por que `def f(x=[]):` é considerado um bug latente?",
                  "A lista default é compartilhada entre todas as chamadas e pode acumular estado.",
                  ["Isso só passa a causar um erro de sintaxe a partir da versão 3.10 do interpretador.", "O Python impede completamente qualquer valor mutável usado como argumento default.", "É só uma preferência de estilo de código, sem qualquer efeito real no comportamento."],
                  "Defaults são avaliados uma vez na definição da função. Se mutável, "
                  "todas as chamadas compartilham. Idiomático: `def f(x=None): x = x or []`.",
                  statement_en="Why is `def f(x=[]):` considered a latent bug?",
                  correct_en="The default list is shared across all calls and can accumulate state.",
                  wrong_en=["This only starts causing a syntax error from interpreter version 3.10 onward.", "Python completely prevents any mutable value from being used as a default argument.", "It's just a code style preference, with no real effect on behavior whatsoever."],
                  explanation_en="Defaults are evaluated once, at function definition. If mutable, "
                  "every call shares it. Idiomatic: `def f(x=None): x = x or []`."),
                q("Em Python 3.10+, como anotar 'string ou None'?",
                  "str | None",
                  ["Optional[str] (deprecado)",
                   "string?",
                   "str.None"],
                  "A sintaxe `X | Y` substituiu `Union[X, Y]` em 3.10+. "
                  "`Optional[X]` ainda funciona mas `X | None` é preferido.",
                  statement_en="In Python 3.10+, how do you annotate 'string or None'?",
                  correct_en="str | None",
                  wrong_en=["Optional[str] (deprecated)",
                            "string?",
                            "str.None"],
                  explanation_en="The `X | Y` syntax replaced `Union[X, Y]` in 3.10+. "
                  "`Optional[X]` still works but `X | None` is preferred."),
                q("Qual a diferença entre `is` e `==`?",
                  "`is` compara identidade (mesmo objeto na memória); `==` compara valor.",
                  ["O operador `==` costuma ser bem mais lento de executar do que o `is` na prática.", "Os dois operadores fazem exatamente a mesma comparação, sem diferença alguma entre eles.", "O operador `is` só funciona de forma correta quando comparando números inteiros pequenos."],
                  "Use `is` para comparar com `None`, `True`, `False`. Para igualdade "
                  "de valor use `==`.",
                  statement_en="What's the difference between `is` and `==`?",
                  correct_en="`is` compares identity (same object in memory); `==` compares value.",
                  wrong_en=["The `==` operator tends to be noticeably slower to run than `is` in practice.", "The two operators do exactly the same comparison, with no difference between them at all.", "The `is` operator only works correctly when comparing small integer numbers."],
                  explanation_en="Use `is` to compare with `None`, `True`, `False`. For value "
                  "equality use `==`."),
                q("O que `f\"{x=}\"` produz se x = 42?",
                  "x=42",
                  ["42", "x", "{x: 42}"],
                  "Sintaxe de debug das f-strings (3.8+): inclui o nome da variável "
                  "seguido do valor, útil pra logs rápidos.",
                  statement_en="What does `f\"{x=}\"` produce if x = 42?",
                  correct_en="x=42",
                  wrong_en=["42", "x", "{x: 42}"],
                  explanation_en="F-string debug syntax (3.8+): includes the variable name "
                  "followed by the value, handy for quick logging."),
                q("Como concatenar muitas strings com performance O(n)?",
                  "\"\".join(lista_de_strings)",
                  ["str1 + str2 + str3 + str4 + ...", "operator.concat(str1, str2, str3)", "resultado += item for item in lista"],
                  "Strings são imutáveis: cada `+=` cria nova. `str.join` aloca uma vez.",
                  statement_en="How do you concatenate many strings with O(n) performance?",
                  correct_en="\"\".join(list_of_strings)",
                  wrong_en=["str1 + str2 + str3 + str4 + ...", "operator.concat(str1, str2, str3)", "result += item for item in list"],
                  explanation_en="Strings are immutable: each `+=` creates a new one. `str.join` "
                  "allocates just once."),
                q("Qual destas é a maneira correta de iterar com índice?",
                  "for i, item in enumerate(lst):",
                  ["for i in range(len(lst)): item = lst[i]",
                   "for i, item in zip(range(len(lst)), lst):",
                   "i = 0; for item in lst: i += 1"],
                  "`enumerate` é o padrão. As outras funcionam mas são verbosas.",
                  statement_en="Which of these is the correct way to iterate with an index?",
                  correct_en="for i, item in enumerate(lst):",
                  wrong_en=["for i in range(len(lst)): item = lst[i]",
                            "for i, item in zip(range(len(lst)), lst):",
                            "i = 0; for item in lst: i += 1"],
                  explanation_en="`enumerate` is the standard. The others work but are verbose."),
            ],
        },
        # =====================================================================
        # 6.2 Estruturas de dados e código Pythonic
        # =====================================================================
        {
            "title": "Estruturas de dados e código Pythonic",
            "title_en": "Data Structures and Pythonic Code",
            "summary": "List, dict, set, comprehensions, generators e a stdlib que economiza horas (collections, itertools).",
            "summary_en": "List, dict, set, comprehensions, generators and the stdlib that saves hours (collections, itertools).",
            "lesson": {
                "intro": (
                    "Aqui mora a diferença entre código Python e código 'Java escrito em "
                    "Python'. Código pythonic costuma ser mais curto, mais rápido e mais "
                    "legível, porque delega para estruturas e funções otimizadas em C "
                    "(<code>list</code>, <code>dict</code>, <code>itertools</code>...).<br><br>"
                    "Esta aula é um catálogo do que aparece em código de produção real "
                    "todos os dias."
                ),
                "intro_en": (
                    "This is where the difference between Python code and 'Java written in "
                    "Python' lives. Pythonic code tends to be shorter, faster and more "
                    "readable, because it delegates to structures and functions optimized in "
                    "C (<code>list</code>, <code>dict</code>, <code>itertools</code>...).<br><br>"
                    "This lesson is a catalog of what shows up in real production code "
                    "every day."
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
flowchart TD
    Need["Preciso de..."] --> Q1{"Ordem importa?"}
    Q1 -- "Sim" --> Q2{"Mutável?"}
    Q1 -- "Não, únicos" --> Set["set"]
    Q1 -- "Chave → valor" --> Dict["dict"]
    Q2 -- "Sim" --> List["list"]
    Q2 -- "Não" --> Tup["tuple"]
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
<div class="mermaid">
flowchart LR
    A["Lista: colchetes"] --> B["Carrega tudo na memória de uma vez"]
    C["Generator: parênteses"] --> D["Produz um item por vez, sob demanda"]
</div>
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Abrir o arquivo como stream</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Filtrar linhas com generator</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Agregar só o que importa</p></div>
  </div>
  <figcaption>Pipeline Pythonic: processar sob demanda em vez de listar o arquivo inteiro.</figcaption>
</figure>
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
                "body_en": (
                """<h3>1. Lists, tuples, sets, dicts: the same choice that decides performance</h3>
<table>
<thead><tr><th>Structure</th><th>Access</th><th>Mutable</th>
<th>Typical case</th></tr></thead>
<tbody>
<tr><td><code>list</code></td><td>O(1) by index</td><td>Yes</td>
<td>Ordered collection, task queue, batch.</td></tr>
<tr><td><code>tuple</code></td><td>O(1) by index</td><td>No</td>
<td>Fixed record (lat, lng), multiple return values.</td></tr>
<tr><td><code>set</code></td><td>O(1) <em>in</em></td><td>Yes</td>
<td>Deduplication, membership tests.</td></tr>
<tr><td><code>dict</code></td><td>O(1) by key</td><td>Yes</td>
<td>Mapping, counters, configs.</td></tr>
</tbody></table>
<p>What makes <code>list</code> and <code>dict</code>/<code>set</code>
diverge so much in lookup performance is the underlying structure:
<code>list</code> is a contiguous array, so finding an item requires
walking position by position (O(n)) until finding it or reaching the end;
dict and set use a hash table, computing the item's position directly from
its hash (expected O(1)), without traversing anything. In practice: any
<code>x in collection</code> inside a loop that runs many times is an
immediate candidate to become a <code>set</code> — the change from total
O(n²) to O(n) in a loop of thousands of items is the difference between
milliseconds and minutes.</p>
<div class="mermaid">
flowchart TD
    Need["I need..."] --> Q1{"Order matters?"}
    Q1 -- "Yes" --> Q2{"Mutable?"}
    Q1 -- "No, unique" --> Set["set"]
    Q1 -- "Key to value" --> Dict["dict"]
    Q2 -- "Yes" --> List["list"]
    Q2 -- "No" --> Tup["tuple"]
</div>


<h3>2. Comprehensions: why the "shorter" version is also faster</h3>
<pre><code># list
ips = [host["ip"] for host in hosts if host["alive"]]

# dict
by_name = {h["name"]: h for h in hosts}

# set
unique_envs = {h["env"] for h in hosts}

# generator (lazy)
total = sum(h["cpu"] for h in hosts)</code></pre>
<p>A comprehension isn't just compact syntax: the explicit loop
<code>for item in x: result.append(f(item))</code> makes a method call
(<code>.append</code>) per iteration, resolved in pure Python; the
comprehension compiles to dedicated bytecode that avoids that repeated
call, running closer to C internally — the speed gain is real, not just
cosmetic. The limit is readability: a nested comprehension with two
filters is already harder to read than an equivalent <code>for</code>,
and at that point "elegance" becomes the opposite — code that requires
rereading twice to understand what filters and what transforms. For
accumulation with a side effect (writing to a log, writing to the
database on every item), use a normal loop: a comprehension's value is
the list it produces, and using it only for the side effect while
discarding the result confuses whoever reads it about why it exists.</p>

<h3>3. Generators: why "doesn't load everything into memory" is literal</h3>
<pre><code>def parse_log(path: str):
    with open(path) as f:
        for line in f:
            if "ERROR" in line:
                yield line.strip()

for err in parse_log("/var/log/app.log"):
    print(err)</code></pre>
<p>A function with <code>yield</code> doesn't run when called — calling
<code>parse_log(path)</code> returns a generator object, and the
function's BODY only advances to the next <code>yield</code> when
someone asks for the next item (via <code>for</code>, <code>next()</code>,
etc.). That's why a 50 GB file can be processed this way while keeping
only ONE line in memory at a time: the generator never materializes the
whole list, it processes and discards line by line as the consumer
advances.</p>
<pre><code>errors = (line for line in open("app.log") if "ERROR" in line)
first_5 = list(itertools.islice(errors, 5))</code></pre>
<p>The generator expression (parentheses instead of brackets) has exactly
the same memory efficiency as a function with <code>yield</code>, handy
when the pipeline fits on one line.</p>

<h3>4. `collections`: names that solve patterns everyone reinvents</h3>
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
<p><code>defaultdict</code> isn't magic: when accessing a missing key, it
calls the factory (<code>list</code>, <code>int</code>, whatever you
pass) and INSERTS the result into the dict before returning it — that's
why checking <code>len(by_status)</code> after only READING a
nonexistent key can show one more entry than you expected, a common
gotcha. As for <code>deque</code>, it solves a hidden performance problem
that a plain list has: <code>list.pop(0)</code> (removing from the
front) is O(n) because the rest of the array needs to shift one
position; <code>deque</code> is implemented as a doubly linked list of
blocks, with O(1) at both ends — essential for queues and fixed-size
sliding windows (<code>maxlen</code> automatically drops the oldest
item).</p>

<h3>5. `itertools`: combining iterables without ever materializing the combination</h3>
<div class="mermaid">
flowchart LR
    A["List: brackets"] --> B["Loads everything into memory at once"]
    C["Generator: parentheses"] --> D["Yields one item at a time, on demand"]
</div>
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
<p>The detail that catches people using <code>groupby</code> for the
first time: it only groups ADJACENT items with the same key — it doesn't
group the entire collection by key the way a <code>defaultdict</code>
would. That's why <code>logs.sort(...)</code> beforehand is mandatory:
without sorting first, the same host appearing in two non-adjacent
positions becomes two separate groups, a silent bug (the code runs, it
just produces wrong counts) easy to miss until someone compares against
the expected total.</p>

<h3>6. `dataclasses`: records with equality and repr for free</h3>
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
<p>Without <code>@dataclass</code>, a pure data class still needs a
hand-written <code>__init__</code> (assigning each field), and without
<code>__eq__</code> two objects with the SAME values compare as
different (default identity comparison), which usually surprises people
in tests ("why did <code>Host(...) == Host(...)</code> come back
False?"). <code>slots=True</code> solves a hidden cost: by default every
Python instance carries an internal <code>__dict__</code> to allow
dynamic attributes — <code>slots</code> eliminates that dictionary and
declares the attributes up front, saving real memory when you create
thousands of instances (one record per log line, for example). For
automatic runtime type validation (rejecting <code>port="eighty"</code>
at creation) and JSON serialization, Pydantic v2 extends this same idea
with active checking.</p>

<h3>7. Slicing and unpacking: idioms that replace entire loops</h3>
<pre><code>lst = [10, 20, 30, 40, 50]
lst[1:3]      # [20, 30]
lst[::2]      # [10, 30, 50], step 2
lst[::-1]     # [50, 40, 30, 20, 10], invertido

# Desempacotamento estendido
first, *middle, last = lst
# first=10, middle=[20,30,40], last=50

# Em dicts (3.5+)
merged = {**defaults, **user_overrides, "build": 42}</code></pre>
<p><code>{**a, **b}</code> resolves key conflicts by ORDER of
appearance: if the same key exists in both <code>a</code> and
<code>b</code>, <code>b</code>'s value wins — because the resulting dict
is built by inserting <code>a</code>'s keys first and then
<code>b</code>'s, and re-inserting an existing key overwrites it. It's
the idiomatic pattern for "default config + user override", AS LONG AS
the override comes later in the merge — reversing the order flips which
side wins, a subtle mistake from copying the pattern without thinking
about which dict should prevail.</p>

<h3>8. `enum.Enum`/`StrEnum`: eliminating the typo the interpreter won't catch</h3>
<pre><code>from enum import StrEnum, auto

class Severity(StrEnum):
    INFO  = "info"
    WARN  = "warn"
    ERROR = "error"
    CRIT  = auto()

if level &gt;= Severity.WARN:   # comparações como string
    alert(level)</code></pre>
<p>A "magic string" like <code>"eror"</code> (with a typo) goes
unnoticed until runtime — and sometimes not even then, if the comparison
simply never matches and the code follows the wrong path without
raising any exception. An <code>Enum</code> turns that mistake into an
immediate <code>AttributeError</code> (<code>Severity.EROR</code>
doesn't exist) right at code review or the first type check — the error
migrates from "silent in production" to "obvious before committing".
<code>StrEnum</code> (3.11+) specifically allows comparing and
formatting the values as a normal string, useful when the value needs to
go into a log or JSON without extra conversion.</p>

<h3>9. Real case: a log pipeline that never loads the whole file</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Open the file as a stream</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Filter lines with a generator</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Aggregate only what matters</p></div>
  </div>
  <figcaption>Pythonic pipeline: process on demand instead of listing the whole file.</figcaption>
</figure>
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
<p>Every link in this chain is lazy: <code>lines()</code> opens one file
at a time and only reads the next line when asked (via
<code>yield from</code>, which forwards the iteration to the inner
generator without materializing anything); <code>parsed()</code>
processes one line at a time; the generator expression
<code>errors</code> filters without producing an intermediate list. No
point in this chain holds more than one line in memory — that's why this
pattern processes gigabytes of logs with constant, tiny memory usage,
the opposite of <code>lines = open(f).readlines()</code>, which would
materialize the entire file at once before processing anything.</p>"""
                ),
                "practical": (
                    "Escreva <code>top_users.py</code> que lê um <code>access.log</code> "
                    "(formato Combined do nginx/Apache) e imprime, em uma linha cada, os 10 "
                    "IPs mais frequentes <em>e</em> a quantidade de requisições com status "
                    "≥ 500 de cada um. Restrições: (1) use <code>collections.Counter</code>; "
                    "(2) não carregue o arquivo todo em memória, use generator; "
                    "(3) suporte arquivos <code>.gz</code> via <code>gzip.open</code>."
                ),
                "practical_en": (
                    "Write <code>top_users.py</code> that reads an <code>access.log</code> "
                    "(nginx/Apache Combined format) and prints, one per line, the 10 most "
                    "frequent IPs <em>and</em> the count of status ≥ 500 requests for each. "
                    "Constraints: (1) use <code>collections.Counter</code>; "
                    "(2) don't load the whole file into memory, use a generator; "
                    "(3) support <code>.gz</code> files via <code>gzip.open</code>."
                ),
            },
            "materials": [
                m("Python docs, collections",
                  "https://docs.python.org/3/library/collections.html",
                  "docs", "Counter, defaultdict, deque, namedtuple.",
                  title_en="Python docs, collections",
                  description_en="Counter, defaultdict, deque, namedtuple."),
                m("Python docs, itertools",
                  "https://docs.python.org/3/library/itertools.html",
                  "docs", "Receitas de combinatória e iteração.",
                  title_en="Python docs, itertools",
                  description_en="Combinatorics and iteration recipes."),
                m("Real Python, Comprehensions",
                  "https://realpython.com/list-comprehension-python/",
                  "article", "Tutorial completo de comprehensions.",
                  title_en="Real Python, Comprehensions",
                  description_en="Complete tutorial on comprehensions."),
                m("Dataclasses tutorial, RealPython",
                  "https://realpython.com/python-data-classes/",
                  "article", "Quando usar @dataclass.",
                  title_en="Dataclasses tutorial, RealPython",
                  description_en="When to use @dataclass."),
                m("Fluent Python (Luciano Ramalho)",
                  "https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/",
                  "book", "Livro de referência sobre código pythonic.",
                  title_en="Fluent Python (Luciano Ramalho)",
                  description_en="Reference book on pythonic code."),
                m("PEP 3132, Extended Iterable Unpacking",
                  "https://peps.python.org/pep-3132/",
                  "docs", "Sintaxe `first, *middle, last = lst`.",
                  title_en="PEP 3132, Extended Iterable Unpacking",
                  description_en="Syntax for `first, *middle, last = lst`."),
            ],
            "questions": [
                q("Qual estrutura escolher para testar 'item está nesta coleção' rapidamente?",
                  "set",
                  ["list (com `in`)",
                   "tuple",
                   "string"],
                  "`x in set` é O(1). `x in list` é O(n). Para checagens repetidas em "
                  "loop, set é muito superior.",
                  statement_en="Which structure should you pick to test 'item is in this collection' quickly?",
                  correct_en="set",
                  wrong_en=["list (with `in`)", "tuple", "string"],
                  explanation_en="`x in set` is O(1). `x in list` is O(n). For repeated checks in a loop, set is far superior."),
                q("O que faz `[x*2 for x in range(5)]`?",
                  "Cria a lista [0, 2, 4, 6, 8].",
                  ["Cria um generator que produz 0, 2, 4, 6, 8.",
                   "Multiplica cada elemento por 2 in-place.",
                   "Retorna 5 vezes 2."],
                  "Comprehension entre colchetes constrói lista. Entre parênteses seria "
                  "generator (lazy).",
                  statement_en="What does `[x*2 for x in range(5)]` do?",
                  correct_en="Creates the list [0, 2, 4, 6, 8].",
                  wrong_en=[
                            "Creates a generator that yields 0, 2, 4, 6, 8.",
                            "Multiplies each element by 2 in-place.",
                            "Returns 5 times 2.",
                        ],
                  explanation_en="A comprehension in brackets builds a list. In parentheses it would be a generator (lazy)."),
                q("Por que generators são ideais para arquivos grandes?",
                  "Produzem um item por vez, não carregam tudo em memória.",
                  ["Comprimem automaticamente os dados armazenados em memória.", "Aproveitam múltiplas threads automaticamente para acelerar o processamento.", "Costumam ser mais rápidos que uma lista em qualquer cenário."],
                  "Memória constante: você processa um arquivo de 50 GB com poucos KB "
                  "de RAM.",
                  statement_en="Why are generators ideal for large files?",
                  correct_en="They produce one item at a time and don't load everything into memory.",
                  wrong_en=[
                            "They automatically compress data stored in memory.",
                            "They automatically use multiple threads to speed up processing.",
                            "They tend to be faster than a list in every scenario.",
                        ],
                  explanation_en="Constant memory: you can process a 50 GB file with only a few KB of RAM."),
                q("O que `Counter([\"a\",\"b\",\"a\"]).most_common(1)` retorna?",
                  "[('a', 2)]",
                  ["{'a': 2, 'b': 1}", "['a']", "2"],
                  "Counter é um dict que mapeia item→contagem; `most_common(n)` retorna "
                  "lista de tuplas ordenadas por contagem decrescente.",
                  statement_en="What does `Counter([\"a\",\"b\",\"a\"]).most_common(1)` return?",
                  correct_en="[('a', 2)]",
                  wrong_en=["{'a': 2, 'b': 1}", "['a']", "2"],
                  explanation_en="Counter is a dict mapping item→count; `most_common(n)` returns a list of tuples ordered by descending count."),
                q("Para que serve `defaultdict(list)`?",
                  "Cria um dict que retorna [] automaticamente para chaves inexistentes.",
                  ["Impõe um limite máximo para o número de itens guardados dentro do dict.", "Cria um dict que mantém automaticamente as chaves ordenadas em ordem alfabética.", "Combina o conteúdo de múltiplos dicts em paralelo usando várias threads."],
                  "Evita o padrão `if k not in d: d[k] = []`. Uma chave acessada que "
                  "não existe é criada com o valor default.",
                  statement_en="What is `defaultdict(list)` for?",
                  correct_en="Creates a dict that automatically returns [] for missing keys.",
                  wrong_en=[
                            "Imposes a maximum limit on how many items the dict may hold.",
                            "Creates a dict that automatically keeps keys sorted alphabetically.",
                            "Merges the contents of multiple dicts in parallel using several threads.",
                        ],
                  explanation_en="Avoids the `if k not in d: d[k] = []` pattern. Accessing a missing key creates it with the default value."),
                q("`@dataclass(frozen=True)` torna a classe...",
                  "Imutável e hashable (utilizável como chave de dict ou item de set).",
                  ["Compatível com o módulo pickle de forma obrigatória, sem qualquer exceção possível.", "Sincronizada automaticamente para permitir uso seguro entre múltiplas threads.", "Consideravelmente mais rápida em runtime do que uma classe comum equivalente."],
                  "frozen impede modificação após init e ativa __hash__ baseado nos "
                  "campos.",
                  statement_en="`@dataclass(frozen=True)` makes the class...",
                  correct_en="Immutable and hashable (usable as a dict key or set item).",
                  wrong_en=[
                            "Mandatory-compatible with the pickle module, with no possible exceptions.",
                            "Automatically synchronized for safe use across multiple threads.",
                            "Considerably faster at runtime than an equivalent plain class.",
                        ],
                  explanation_en="frozen prevents modification after init and enables __hash__ based on the fields."),
                q("Qual a saída de `lst[::-1]` se lst = [1,2,3]?",
                  "[3, 2, 1]",
                  ["[1, 2, 3]", "[]", "[1]"],
                  "Slice com step -1 inverte a sequência. Atalho clássico para "
                  "reverter listas/strings.",
                  statement_en="What is the output of `lst[::-1]` if lst = [1,2,3]?",
                  correct_en="[3, 2, 1]",
                  wrong_en=["[1, 2, 3]", "[]", "[1]"],
                  explanation_en="A slice with step -1 reverses the sequence. Classic shortcut to reverse lists/strings."),
                q("Qual destas é uma DESVANTAGEM de comprehensions?",
                  "Ficam ilegíveis quando aninhadas profundamente ou com filtros complexos.",
                  ["Não conseguem incluir algum tipo de condicional dentro da própria expressão.", "Costumam rodar visivelmente mais devagar do que um loop for equivalente.", "Não podem ser combinadas de forma alguma com uma expressão geradora."],
                  "Performance é geralmente melhor que for+append. O risco é cognitivo: "
                  "comprehension de 4 linhas com 2 ifs é pior que loop explícito.",
                  statement_en="Which of these is a DISADVANTAGE of comprehensions?",
                  correct_en="They become unreadable when deeply nested or with complex filters.",
                  wrong_en=[
                            "They cannot include any kind of conditional inside the expression itself.",
                            "They tend to run noticeably slower than an equivalent for loop.",
                            "They cannot be combined with a generator expression in any way.",
                        ],
                  explanation_en="Performance is generally better than for+append. The risk is cognitive: a 4-line comprehension with 2 ifs is worse than a loop."),
                q("`{**a, **b}` quando há chaves repetidas...",
                  "Mantém o valor do último dict (b sobrescreve a).",
                  ["Soma automaticamente os valores das duas chaves repetidas.", "Levanta uma exceção KeyError assim que encontra a repetição.", "Mantém o valor do primeiro dict, ignorando o segundo (a vence)."],
                  "Padrão merge: o último ganha. Idiomático para juntar config default + "
                  "override do usuário.",
                  statement_en="`{**a, **b}` when there are duplicate keys...",
                  correct_en="Keeps the value from the last dict (b overwrites a).",
                  wrong_en=[
                            "Automatically sums the values of the two duplicate keys.",
                            "Raises a KeyError as soon as it finds the duplicate.",
                            "Keeps the value from the first dict, ignoring the second (a wins).",
                        ],
                  explanation_en="Merge pattern: last one wins. Idiomatic for joining default config + user override."),
                q("Para iterar uma coleção descobrindo o índice ao mesmo tempo:",
                  "for i, x in enumerate(lst):",
                  ["for i in range(len(lst)): x = lst[i]",
                   "for x, i in lst.items():",
                   "for x in lst.keys(): ..."],
                  "`enumerate` é a forma idiomática. Aceita `start=1` para numerar a "
                  "partir de 1.",
                  statement_en="To iterate a collection while also discovering the index:",
                  correct_en="for i, x in enumerate(lst):",
                  wrong_en=[
                            "for i in range(len(lst)): x = lst[i]",
                            "for x, i in lst.items():",
                            "for x in lst.keys(): ...",
                        ],
                  explanation_en="`enumerate` is the idiomatic form. It accepts `start=1` to number from 1."),
            ],
        },
        # =====================================================================
        # 6.3 POO, exceções e context managers
        # =====================================================================
        {
            "title": "POO, exceções e context managers",
            "title_en": "OOP, Exceptions and Context Managers",
            "summary": "Classes em Python real, dunder methods, hierarquia de exceções e gerenciamento de recursos.",
            "summary_en": "Real-world Python classes, dunder methods, exception hierarchy and resource management.",
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
                "intro_en": (
                    "Python doesn't force you to use classes — functions and dicts cover 80% "
                    "of cases. But when state grows large or a behavior needs polymorphism "
                    "(multiple storage backends, different database drivers), classes pay "
                    "for the complexity. This lesson covers Python's OOP model, the dunder "
                    "methods you need to know, how to handle errors without 'swallowing' "
                    "bugs, and how to use context managers to guarantee cleanup."
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
    Call["Classe()"] --> New["__new__ aloca"]
    New --> Init["__init__ inicializa"]
    Init --> Inst["Instância pronta"]
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
<div class="mermaid">
flowchart TD
    Base["BaseException"] --> Sys["SystemExit / KeyboardInterrupt"]
    Base --> Exc["Exception"]
    Exc --> Val["ValueError / TypeError"]
    Exc --> OS["OSError"]
    Exc --> Runtime["RuntimeError"]
</div>
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
<div class="mermaid">
flowchart LR
    A["with obj as f"] --> B["obj.__enter__()"]
    B --> C["Bloco de código roda"]
    C --> D["obj.__exit__() roda sempre, mesmo com exceção"]
</div>
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
                "body_en": (
                """<h3>1. Classes: `__init__` initializes, it doesn't construct</h3>
<pre><code>class Server:
    def __init__(self, name: str, ip: str, port: int = 22) -&gt; None:
        self.name = name
        self.ip   = ip
        self.port = port

    def url(self) -&gt; str:
        return f"ssh://{self.ip}:{self.port}"

s = Server("web1", "10.0.1.5")
print(s.url())</code></pre>
<p>The distinction between <code>__new__</code> (constructs the object, allocates
memory) and <code>__init__</code> (initializes what was already allocated) rarely
matters day to day — but it explains why subclassing immutable types
(<code>str</code>, <code>int</code>, <code>tuple</code>) requires overriding
<code>__new__</code>: in those classes the VALUE is fixed at construction, before
<code>__init__</code> runs, so trying to change the value in
<code>__init__</code> simply has no effect. <code>self</code> is just
a naming convention (the first parameter of a method always receives the
instance, call it whatever you want), but breaking that convention confuses
any reader trained in the language's idiom. For a class that only
holds data (no logic beyond accessing fields), writing
<code>__init__</code> and <code>__repr__</code> by hand is work that
<code>@dataclass</code> (seen in the previous lesson) already solves.</p>
<div class="mermaid">
flowchart LR
    Call["Class()"] --> New["__new__ allocates"]
    New --> Init["__init__ initializes"]
    Init --> Inst["Ready instance"]
</div>


<h3>2. Class vs instance attribute: the bug that looks like magical sharing</h3>
<pre><code>class Cache:
    DEFAULT_TTL = 60                  # atributo de classe (compartilhado)

    def __init__(self):
        self.store = {}               # atributo de instância (próprio)

Cache.DEFAULT_TTL = 120              # muda para todo mundo
Cache().DEFAULT_TTL = 30             # cria instância: shadow!</code></pre>
<p>An attribute defined in the class body (outside <code>__init__</code>)
lives in a single place — the CLASS object, not on each instance — and every
instance that doesn't have its own attribute with that name "sees" the class
value through it. The language's most-cited mistake comes exactly
from here: <code>class Cache: items = []</code> creates ONE list shared
by all instances; <code>instance.items.append(x)</code> modifies
that single list, so a second instance created later is already born
"seeing" the items the first one inserted — it looks like a shared-reference
bug because that's exactly what it is. The fix is to declare
<code>self.items = []</code> inside <code>__init__</code>, creating a
new list per instance.</p>

<h3>3. Inheritance and `super()`: reuse behavior without rewriting it</h3>
<pre><code>class HTTPError(Exception):
    pass

class RetryableHTTPError(HTTPError):
    def __init__(self, status: int, body: str):
        super().__init__(f"retryable {status}")
        self.status = status
        self.body   = body</code></pre>
<p><code>super().__init__(...)</code> calls the PARENT class initializer
before adding the subclass's own behavior — without that
call, the base <code>Exception</code> never receives the message, and
<code>str(error)</code> would come back empty even with <code>status</code> and
<code>body</code> filled in. Multiple inheritance exists in Python and is
legitimately used for mixins (a small class that only adds
one behavior, like <code>LoggingMixin</code>, combined with the main
class via <code>class Foo(LoggingMixin, Base):</code>) — but
deep hierarchies (inheritance of inheritance of inheritance) make it hard
to know where a method really comes from, and most modern API
designers prefer composition (a class that HOLDS another as
an attribute) over inheritance in those cases.</p>

<h3>4. Dunder methods: the contract that makes your class behave like the built-ins</h3>
<table>
<thead><tr><th>Method</th><th>What for</th></tr></thead>
<tbody>
<tr><td><code>__repr__</code></td><td>Debug representation. Always define it.</td></tr>
<tr><td><code>__str__</code></td><td>For humans (<code>str(x)</code>, <code>print</code>).</td></tr>
<tr><td><code>__eq__</code>, <code>__hash__</code></td><td>Equality and use in set/dict.</td></tr>
<tr><td><code>__len__</code>, <code>__contains__</code>, <code>__iter__</code></td><td>Custom collections.</td></tr>
<tr><td><code>__enter__</code>, <code>__exit__</code></td><td>Context manager (<code>with</code>).</td></tr>
<tr><td><code>__call__</code></td><td>Makes the instance callable like a function.</td></tr>
</tbody></table>
<p>Without <code>__repr__</code>, printing an object in the console or a log
produces something like <code>&lt;Server object at 0x7f...&gt;</code> — the
memory address, zero useful debugging information. It's the difference
between a log that says what broke and one that only says "something of type
Server broke somewhere". <code>__eq__</code> and <code>__hash__</code>
go together under a rule the language enforces: if you define
<code>__eq__</code> without <code>__hash__</code>, the class becomes
automatically unhashable (Python assumes objects "equal" by
value shouldn't have different hashes, and for safety disables the default
hash) — a side effect that silently breaks any code
that tried to use that class as a dict key or set item.</p>

<h3>5. Properties: when an attribute should be a disguised function</h3>
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
<p>The advantage of <code>@property</code> over an explicit getter/setter
(<code>get_count()</code>/<code>set_count()</code>, common in other
languages) is that CALLING CODE keeps writing
<code>replica.count = 200</code> — ordinary attribute syntax — while
validation runs underneath. That lets you start a class with a simple
public attribute and, if validation or computation is needed later,
promote it to a property WITHOUT breaking anyone already using the class
(callers don't change a single line). The common mistake is the opposite:
creating a property for EVERY attribute "just in case", adding indirection
where there's no rule to justify it.</p>

<h3>6. The exception hierarchy, and why two branches must not be caught</h3>
<div class="mermaid">
flowchart TD
    Base["BaseException"] --> Sys["SystemExit / KeyboardInterrupt"]
    Base --> Exc["Exception"]
    Exc --> Val["ValueError / TypeError"]
    Exc --> OS["OSError"]
    Exc --> Runtime["RuntimeError"]
</div>
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
<p><code>SystemExit</code> and <code>KeyboardInterrupt</code> inherit from
<code>BaseException</code> directly, OUTSIDE the
<code>Exception</code> tree — a deliberate design decision: a generic
<code>except Exception:</code> doesn't catch those two, so
<code>sys.exit()</code> and Ctrl+C keep working even inside
code with broad error handling. A bare <code>except:</code> (no type
at all) catches EVERYTHING, including those two — that's why PEP 8
forbids it: a process that should die on Ctrl+C simply ignores
the signal and keeps running, requiring <code>kill -9</code> to really
stop. The practical rule is to catch the MOST SPECIFIC type you know
how to handle, let the rest propagate, and use <code>raise NewError(...) from
original</code> when converting a low-level exception into a domain
exception — the resulting traceback shows the full chain ("the above
exception was the direct cause of..."), instead of hiding the root cause.</p>

<h3>7. `try/except/else/finally`: four blocks, four different roles</h3>
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
<p><code>else</code> only runs if the <code>try</code> block finished WITHOUT
raising an exception — its job is to separate "code that may fail" (inside
<code>try</code>) from "what should only run if everything succeeded" (in
<code>else</code>), avoiding an exception accidentally raised by
success-path code being caught by the wrong <code>except</code>, as if
it were a <code>load_config</code> error. <code>finally</code> runs
ALWAYS — with an exception, without one, or even if a <code>return</code>
happened inside <code>try</code> — the right place for cleanup that
must not be skipped under any circumstance.</p>

<h3>8. Context managers: `with` as a guarantee, not a convenience</h3>
<div class="mermaid">
flowchart LR
    A["with obj as f"] --> B["obj.__enter__()"]
    B --> C["Code block runs"]
    C --> D["obj.__exit__() always runs, even on exception"]
</div>
<p>The most common pattern is <code>open()</code>:</p>
<pre><code>with open("/etc/passwd") as f:
    data = f.read()
# arquivo fechado AQUI, com ou sem exceção</code></pre>
<p>The guarantee <code>with</code> offers is exactly this: the object's
<code>__exit__</code> method runs EVEN if an exception blows up inside
the block — something an <code>f.close()</code> written on the next line after
<code>open()</code> does not guarantee, because an exception in between jumps
straight to <code>except</code>/end of function without passing through that
<code>close()</code>. To create your own, the simplest form is a
decorated generator function:</p>
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
<p>The code before <code>yield</code> is the implicit
<code>__enter__</code>; what comes after (inside <code>finally</code>, to run
even on exception) is <code>__exit__</code>. Multiple context managers
can be combined on one line:</p>
<pre><code>with open("a") as a, open("b") as b, lock:
    process(a, b)</code></pre>

<h3>9. `ExceptionGroup` and `except*` (3.11+): when one error isn't enough</h3>
<p>Concurrent operations (<code>asyncio.gather</code>,
<code>TaskGroup</code>, seen in the concurrency lesson) can fail in
MORE THAN ONE task at the same time — a traditional <code>try/except</code>
only knows how to handle one exception at a time, so before 3.11 the second
simultaneous failure stayed hidden or required manual aggregation.
<code>ExceptionGroup</code> solves that by grouping all failures
that occurred, and <code>except*</code> lets you handle each error TYPE inside
the group separately:</p>
<pre><code>try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(fetch_a())
        tg.create_task(fetch_b())
except* ConnectionError as eg:
    log.warn("conexão: %d falhas", len(eg.exceptions))
except* TimeoutError as eg:
    log.warn("timeout: %d", len(eg.exceptions))</code></pre>
<p><code>eg.exceptions</code> is a tuple with ALL exceptions of that
type that occurred in the group's tasks — if three tasks failed with
<code>ConnectionError</code> and one with <code>TimeoutError</code>, both
<code>except*</code> blocks run, each seeing only its own type's
exceptions, without one masking the other.</p>
"""
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
                "practical_en": (
                    "Implement a <code>RetryableHTTP</code> class with a method "
                    "<code>get(url, retries=3)</code> that: (1) uses "
                    "<code>requests.get</code>; (2) catches <code>requests.HTTPError</code> "
                    "only on 5xx status; (3) retries with exponential backoff (1s, 2s, 4s); "
                    "(4) re-raises as a custom <code>DeployError</code>, chaining the "
                    "original exception with <code>raise ... from</code>. Add a "
                    "<code>timed</code> context manager that logs the duration of each call."
                ),
            },
            "materials": [
                m("Python docs, Classes",
                  "https://docs.python.org/3/tutorial/classes.html",
                  "docs", "Tutorial oficial de classes.",
                  title_en="Python docs, Classes",
                  description_en="Official classes tutorial."),
                m("Python docs, Errors and Exceptions",
                  "https://docs.python.org/3/tutorial/errors.html",
                  "docs", "Hierarquia de exceções.",
                  title_en="Python docs, Errors and Exceptions",
                  description_en="Exception hierarchy."),
                m("Python docs, contextlib",
                  "https://docs.python.org/3/library/contextlib.html",
                  "docs", "Context managers prontos e helpers.",
                  title_en="Python docs, contextlib",
                  description_en="Ready-made context managers and helpers."),
                m("Real Python: OOP in Python",
                  "https://realpython.com/python3-object-oriented-programming/",
                  "article", "Tutorial detalhado de OOP.",
                  title_en="Real Python: OOP in Python",
                  description_en="Detailed OOP tutorial."),
                m("PEP 654, Exception Groups",
                  "https://peps.python.org/pep-0654/",
                  "docs", "ExceptionGroup e except*.",
                  title_en="PEP 654, Exception Groups",
                  description_en="ExceptionGroup and except*."),
                m("Hynek Schlawack, Subclass at your own risk",
                  "https://hynek.me/articles/python-subclassing-redux/",
                  "article", "Quando NÃO usar herança.",
                  title_en="Hynek Schlawack, Subclass at your own risk",
                  description_en="When NOT to use inheritance."),
            ],
            "questions": [
                q("Qual destes deveria SEMPRE ser definido em uma classe customizada?",
                  "__repr__",
                  ["__init__ sobrescrito e vazio", "__del__ implementado manualmente", "__str__ isolado, sem __repr__"],
                  "__repr__ é o que aparece em logs e debugger. Sem ele, depurar erros "
                  "vira advinhação. __del__ é raramente útil.",
                  statement_en="Which of these should ALWAYS be defined on a custom class?",
                  correct_en="__repr__",
                  wrong_en=[
                            "An overridden empty __init__",
                            "A manually implemented __del__",
                            "__str__ alone, without __repr__",
                        ],
                  explanation_en="__repr__ is what shows up in logs and the debugger. Without it, debugging becomes guesswork. __del__ is rarely useful."),
                q("Para garantir que um arquivo seja fechado mesmo em caso de exceção:",
                  "with open(path) as f: ...",
                  ["try: f = open(path)\\n  ...\\nexcept: f.close()",
                   "Definir um destrutor.",
                   "Usar global e finalize manualmente."],
                  "Context manager (`with`) garante __exit__ sempre, mesmo com exceção. "
                  "É o jeito pythonic e seguro.",
                  statement_en="To ensure a file is closed even if an exception occurs:",
                  correct_en="with open(path) as f: ...",
                  wrong_en=[
                            "try: f = open(path)\\n  ...\\nexcept: f.close()",
                            "Define a destructor.",
                            "Use global and finalize manually.",
                        ],
                  explanation_en="A context manager (`with`) always guarantees __exit__, even on exception. It's the pythonic, safe way."),
                q("Capturar `BaseException` em código de aplicação é problemático porque...",
                  "Captura também SystemExit e KeyboardInterrupt, impedindo encerramento limpo.",
                  ["Essa forma de captura simplesmente deixou de existir a partir do Python 3.", "Captura só exceções relacionadas especificamente a erro de tipo (TypeError).", "Costuma deixar o programa consideravelmente mais lento do que capturar Exception."],
                  "BaseException é o topo. Aplicação deve capturar Exception ou subclasses. "
                  "Capturar BaseException pode ignorar Ctrl+C e sys.exit().",
                  statement_en="Catching `BaseException` in application code is problematic because...",
                  correct_en="It also catches SystemExit and KeyboardInterrupt, preventing clean shutdown.",
                  wrong_en=[
                            "That form of catching simply stopped existing starting with Python 3.",
                            "It only catches exceptions specifically related to type errors (TypeError).",
                            "It tends to make the program considerably slower than catching Exception.",
                        ],
                  explanation_en="BaseException is the top. Applications should catch Exception or subclasses. Catching BaseException can ignore Ctrl+C and sys.exit()."),
                q("`raise NewError(\"...\") from old` faz o quê?",
                  "Lança a nova exceção encadeando a original (preserva traceback).",
                  ["Substitui a exceção original de forma silenciosa, sem deixar algum registro dela.", "Causa um erro de sintaxe assim que o interpretador tenta ler esse trecho de código.", "Lança as duas exceções ao mesmo tempo, rodando de forma paralela uma à outra."],
                  "O `from` deixa explícito o encadeamento, o traceback mostra 'The "
                  "above exception was the direct cause of...' facilitando debugging.",
                  statement_en="What does `raise NewError(\"...\") from old` do?",
                  correct_en="Raises the new exception chaining the original (preserves traceback).",
                  wrong_en=[
                            "Silently replaces the original exception, leaving no record of it.",
                            "Causes a syntax error as soon as the interpreter tries to read that code.",
                            "Raises both exceptions at once, running them in parallel with each other.",
                        ],
                  explanation_en="The `from` makes the chain explicit; the traceback shows 'The above exception was the direct cause of...' aiding debugging."),
                q("Em `class Cache: items = []`, o que tem de errado se duas instâncias chamarem `.items.append(x)`?",
                  "items é atributo de classe (compartilhado), todas as instâncias enxergam o mesmo list.",
                  ["O interpretador Python proíbe explicitamente atributo mutável definido direto na classe.", "O valor guardado no append acaba se perdendo por causa da atuação do garbage collector.", "Não há problema algum nesse tipo de código, é só uma escolha de estilo pessoal."],
                  "Atributos de classe são compartilhados. Para estado por instância, "
                  "inicialize em `__init__` (`self.items = []`).",
                  statement_en="In `class Cache: items = []`, what's wrong if two instances call `.items.append(x)`?",
                  correct_en="items is a class attribute (shared); every instance sees the same list.",
                  wrong_en=[
                            "The Python interpreter explicitly forbids a mutable attribute defined directly on the class.",
                            "The value stored by append ends up lost because of the garbage collector.",
                            "There's nothing wrong with this kind of code; it's just a personal style choice.",
                        ],
                  explanation_en="Class attributes are shared. For per-instance state, initialize in `__init__` (`self.items = []`)."),
                q("`@property` é apropriado quando...",
                  "Você precisa validar ou calcular dinamicamente um atributo.",
                  ["Quer trocar atributos públicos por getters/setters em todas as classes.",
                   "Quer otimizar acesso.",
                   "É obrigatório em Python 3.10+."],
                  "Property só vale quando há regra/validação/cálculo. Para campos "
                  "simples, atributo público é o jeito pythonic.",
                  statement_en="`@property` is appropriate when...",
                  correct_en="You need to validate or dynamically compute an attribute.",
                  wrong_en=[
                            "You want to replace public attributes with getters/setters in every class.",
                            "You want to optimize access.",
                            "It's mandatory in Python 3.10+.",
                        ],
                  explanation_en="Property only pays off when there's a rule/validation/computation. For simple fields, a public attribute is the pythonic way."),
                q("`@contextmanager` permite criar context manager via:",
                  "Função geradora com um único `yield`.",
                  ["Decorador automático em qualquer função.",
                   "Subclasse de ABC.",
                   "Não é mais usado, deprecou em 3.10."],
                  "A função tem o setup antes do yield, e o cleanup depois. Equivale a "
                  "uma classe com __enter__/__exit__.",
                  statement_en="`@contextmanager` lets you create a context manager via:",
                  correct_en="A generator function with a single `yield`.",
                  wrong_en=[
                            "An automatic decorator on any function.",
                            "An ABC subclass.",
                            "It's no longer used; deprecated in 3.10.",
                        ],
                  explanation_en="The function has setup before the yield and cleanup after. Equivalent to a class with __enter__/__exit__."),
                q("Qual a diferença entre `except Exception as e` e `except:` (sem tipo)?",
                  "`except:` captura também BaseException (KeyboardInterrupt, SystemExit), o que é perigoso.",
                  ["Só essa segunda forma, sem tipo, passou a funcionar a partir da versão 3.10, prática ainda comum em sistema legado que raramente é atualizado.", "As duas formas se comportam de maneira idêntica, sem diferença prática relevante, prática que só aparece como erro grave durante um incidente real.", "A forma `except:` costuma rodar visivelmente mais rápido do que `except Exception`, que só aparece como problema depois que o sistema já está em produção."],
                  "Bare `except:` é proibido pelo PEP 8. Sempre use `except Exception` "
                  "no mínimo.",
                  statement_en="What's the difference between `except Exception as e` and `except:` (no type)?",
                  correct_en="`except:` also catches BaseException (KeyboardInterrupt, SystemExit), which is dangerous.",
                  wrong_en=[
                            "Only that second typeless form started working from version 3.10, a practice still common in rarely updated legacy systems.",
                            "Both forms behave identically, with no relevant practical difference, a practice that only shows up as a serious error during a real incident.",
                            "The `except:` form tends to run visibly faster than `except Exception`, which only shows up as a problem once the system is already in production.",
                        ],
                  explanation_en="Bare `except:` is forbidden by PEP 8. Always use at least `except Exception`."),
                q("`super().__init__(...)` em uma subclasse...",
                  "Chama o __init__ da classe pai.",
                  ["Sobrescreve o __init__ pai permanentemente.",
                   "É equivalente a `self.__init__()` direto.",
                   "Só funciona em herança simples."],
                  "Padrão para reusar inicialização do pai. Em herança múltipla, "
                  "super() segue o MRO (Method Resolution Order).",
                  statement_en="`super().__init__(...)` in a subclass...",
                  correct_en="Calls the parent class's __init__.",
                  wrong_en=[
                            "Permanently overrides the parent's __init__.",
                            "Is equivalent to calling `self.__init__()` directly.",
                            "Only works with single inheritance.",
                        ],
                  explanation_en="Standard pattern to reuse the parent's initialization. With multiple inheritance, super() follows the MRO (Method Resolution Order)."),
                q("Para um pedaço de código que SEMPRE deve rodar (limpeza), use:",
                  "finally:",
                  ["except Exception: (bloco genérico)", "else: (só roda sem exceção)", "pass (dentro do except)"],
                  "`finally:` executa com ou sem exceção, com ou sem `return`. É o "
                  "lugar de fechar conexões, soltar locks, remover arquivos temporários.",
                  statement_en="For a piece of code that MUST always run (cleanup), use:",
                  correct_en="finally:",
                  wrong_en=[
                            "except Exception: (generic block)",
                            "else: (runs only with no exception)",
                            "pass (inside the except)",
                        ],
                  explanation_en="`finally:` runs with or without an exception, with or without `return`. It's the place to close connections, release locks, remove temp files."),
            ],
        },
        # =====================================================================
        # 6.4 Manipulação de arquivos e CLI
        # =====================================================================
        {
            "title": "Manipulação de arquivos, paths e CLI",
            "title_en": "File Handling, Paths and CLI",
            "summary": "pathlib moderno, leitura/escrita robusta, JSON/YAML/TOML e construção de ferramentas de linha de comando.",
            "summary_en": "Modern pathlib, robust read/write, JSON/YAML/TOML and building command-line tools.",
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
                "intro_en": (
                    "Almost every DevOps script starts by reading a file (config, log, "
                    "inventory) and exposes some flag (<code>--dry-run</code>, "
                    "<code>--env=prod</code>). This lesson covers how to do it "
                    "<em>right</em>: <code>pathlib</code> instead of strings, "
                    "<code>argparse</code>/<code>typer</code> instead of "
                    "<code>sys.argv[1]</code>, and JSON/YAML/TOML parsing without common "
                    "pitfalls."
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
    P["Path"] --> Resolve["resolve / exists"]
    P --> Parts["parent / name / suffix"]
    P --> IO["read_text / write_text / open"]
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
<div class="mermaid">
flowchart LR
    CLI["Linha de comando"] --> Parser["argparse.ArgumentParser"]
    Parser --> Args["Namespace com os argumentos"]
    Args --> Main["Lógica do programa"]
</div>
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Sucesso</strong><p>return 0 — o contrato padrão que pipelines e shells esperam.</p></div>
    <div class="lesson-viz-card"><strong>Falha</strong><p>Códigos distintos (config, permissão, timeout) para quem chama decidir o próximo passo.</p></div>
  </div>
  <figcaption>CLI bem comportado: stdout para dados, stderr para diagnóstico, exit code para status.</figcaption>
</figure>
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
                "body_en": (
                """<h3>1. `pathlib`: an object that knows what a path is, not just any string</h3>
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
<p><code>os.path.join("/var/log", "app.log")</code> and string concatenation
with <code>+</code> look equivalent to <code>Path("/var/log") /
"app.log"</code>, but they diverge when the path has
wrong separators (slash instead of backslash on Windows) or duplicate
slashes: <code>Path</code> normalizes that automatically, because
it represents the path as a structure, not as text — each operation
(<code>.parent</code>, <code>.suffix</code>, <code>/</code>) manipulates the
structure, it doesn't do string manipulation behind the scenes. That's why
code that mixes <code>os.path</code> with hand-rolled strings tends to
break silently on another operating system, while code
written entirely in <code>pathlib</code> usually just works on both.</p>
<div class="mermaid">
flowchart LR
    P["Path"] --> Resolve["resolve / exists"]
    P --> Parts["parent / name / suffix"]
    P --> IO["read_text / write_text / open"]
</div>


<h3>2. Reading files without getting burned by encoding</h3>
<pre><code># EVITE: assume locale do sistema (pode ser ASCII em servidor)
open("file.txt").read()

# CERTO: explicite encoding e modo
with open("file.txt", encoding="utf-8") as f:
    data = f.read()</code></pre>
<p>Without an explicit <code>encoding="utf-8"</code>, Python uses the
DEFAULT ENCODING OF THE OPERATING SYSTEM where the script runs — usually UTF-8
on your laptop and possibly ASCII or latin-1 on some minimalist
Linux server setups. The classic bug is "works on my machine,
breaks on the server": a file with an accent or emoji read without an explicit
encoding raises <code>UnicodeDecodeError</code> only in the environment where the
default locale differs — and because that depends on system configuration,
not on the code itself, it's one of the most frustrating bugs to reproduce
locally. For binaries (image, gzip, parquet), use mode
<code>"rb"</code> WITHOUT encoding — mixing the two is a type error; binary
data has no "character encoding" to decode. For CSV,
prefer <code>csv.DictReader</code> over <code>line.split(",")</code>: a
comma inside a quoted field (common in free-text fields)
breaks the naive split in a way that only shows up when someone types a
value with a comma, months after the code is in production.</p>

<h3>3. Configuration: why YAML has a "safe" mode and the other shouldn't exist</h3>
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
<p>The reason <code>yaml.safe_load</code> exists as a separate function from
<code>yaml.load</code> is serious: the YAML specification allows tags like
<code>!!python/object:some.module.Class</code> that instruct the parser to
INSTANTIATE an arbitrary Python class with the document data —
<code>yaml.load</code> (without "safe") obeys that tag, which means
a malicious YAML can make the parser execute arbitrary Python code
just by being loaded, before your program even "uses" the
content. <code>safe_load</code> restricts itself to simple data structures
(dict, list, str, int...), with no ability to instantiate anything. Any
YAML that comes from outside your direct control (user upload, another
team's file, config downloaded from the network) must ALWAYS go through
<code>safe_load</code>, never through <code>load</code>.</p>

<h3>4. `argparse`: the stdlib that documents itself</h3>
<div class="mermaid">
flowchart LR
    CLI["Command line"] --> Parser["argparse.ArgumentParser"]
    Parser --> Args["Namespace with arguments"]
    Args --> Main["Program logic"]
</div>
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
<p>Each <code>add_argument</code> automatically generates the
<code>--help</code> message, validates the type before your code runs
(<code>type=Path</code> delivers a ready-made object, not a string you'd
convert manually) and rejects input outside <code>choices</code>
with a readable message — without <code>argparse</code>, each of those
validations would be manual code scattered through <code>main()</code>, easy
to forget on some argument. <code>action="count"</code> for
verbosity is the pattern behind <code>-v</code>/<code>-vv</code>/<code>-vvv</code>
that Unix tools have used for decades: each occurrence of the flag adds 1 to the
counter. Subcommands (<code>add_subparsers</code>) follow the same pattern as
<code>git commit</code>/<code>git push</code> — each subcommand with its
own set of arguments, sharing only the globals.</p>

<h3>5. `typer`: the same thing, derived from type hints</h3>
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
<p>The advantage of <code>typer</code> over raw <code>argparse</code>
shows up when the CLI grows: instead of declaring each argument twice
(once in <code>add_argument</code>, again when reading <code>args.field</code>
in the function body), the Python function's own signature — with type
hints — already IS the CLI definition. Less duplicated code means less
chance that validation and usage drift apart as the project evolves.</p>

<h3>6. Structured logging: why it isn't just a fancier `print`</h3>
<pre><code>import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
log = logging.getLogger("deploy")

log.info("deploying image=%s env=%s", image, env)   # lazy interpolation
log.warning("replicas=%d acima do recomendado", n)
log.error("falhou", exc_info=True)                  # inclui traceback</code></pre>
<p>Passing values as separate arguments
(<code>"%s", image</code>) instead of already formatted
(<code>f"...{image}..."</code>) isn't style — it's <em>lazy evaluation</em>:
logging only formats the string if the configured level will actually emit
that log. With an f-string, interpolation ALWAYS happens, even if the
DEBUG level is off and the message is discarded next —
real CPU waste on systems that emit hundreds of DEBUG logs per
second but run in production at INFO. In production, switching the
handler to emit structured JSON (via <code>python-json-logger</code>)
makes ingestion by Datadog, Loki or CloudWatch easier, since they expect separate
fields (timestamp, level, message) instead of a free-text line
to parse.</p>

<h3>7. stdout vs stderr: the contract that lets your CLI compose with others</h3>
<pre><code>import sys
print(json.dumps(result))                # stdout
print("WARN: ...", file=sys.stderr)      # stderr</code></pre>
<p>The POSIX convention reserves <code>stdout</code> for the program's RESULT
— what another program will consume via a pipe — and
<code>stderr</code> for diagnostics aimed at a human. Mixing the
two (a loose <code>print("Starting deploy...")</code> before the result
JSON) breaks any composition with another tool:
<code>my-cli | jq '.status'</code> fails trying to parse "Starting
deploy..." as JSON, because that line should never have gone to
stdout. Every progress log, warning or error that a human reads in the
terminal — but that a consuming script shouldn't see — goes to
stderr.</p>

<h3>8. Exit codes: the protocol automation scripts check</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Success</strong><p>return 0 — the default contract pipelines and shells expect.</p></div>
    <div class="lesson-viz-card"><strong>Failure</strong><p>Distinct codes (config, permission, timeout) so the caller can decide the next step.</p></div>
  </div>
  <figcaption>Well-behaved CLI: stdout for data, stderr for diagnostics, exit code for status.</figcaption>
</figure>
<pre><code>def main() -&gt; int:
    try: do_work()
    except ConfigError: return 65   # data format error
    except NetworkError: return 69  # service unavailable
    return 0

if __name__ == "__main__":
    raise SystemExit(main())</code></pre>
<p>0 means success; any other value means failure — it's the only
signal a shell script calling your CLI (<code>if
my-cli; then ...</code>) sees without needing to interpret text
output. The POSIX convention (defined in <code>sysexits.h</code>) reserves
specific ranges — 65 for data format error, 69 for service
unavailable — that infrastructure automation tools already
recognize; using a generic 1 for everything forces anyone integrating your CLI to read
text messages to know what went wrong, instead of checking the exit
code. The <code>def main() -&gt; int: ...</code> +
<code>raise SystemExit(main())</code> pattern keeps exit logic inside a
testable function — testing that <code>main()</code> returns 65 in an
invalid-config scenario is trivial; testing that the PROCESS exits with
code 65 would require running a real subprocess on every test.</p>
"""
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
                "practical_en": (
                    "Create a <code>diskhog.py</code> CLI that: (1) takes a directory via "
                    "<code>--root</code> (default <code>.</code>); (2) has a <code>--top "
                    "N</code> flag (default 10); (3) walks recursively with "
                    "<code>Path.rglob('*')</code> and prints the N largest files with "
                    "human-readable sizes (KB/MB/GB); (4) uses <code>logging</code> for "
                    "progress messages on stderr; (5) exits 0 normally, 2 if root doesn't "
                    "exist."
                ),
            },
            "materials": [
                m("Python docs, pathlib",
                  "https://docs.python.org/3/library/pathlib.html",
                  "docs", "API moderna de paths.",
                  title_en="Python docs, pathlib",
                  description_en="Modern path API."),
                m("Python docs, argparse",
                  "https://docs.python.org/3/library/argparse.html",
                  "docs", "Construção de CLI com a stdlib.",
                  title_en="Python docs, argparse",
                  description_en="Building CLIs with the stdlib."),
                m("Typer documentation",
                  "https://typer.tiangolo.com/",
                  "docs", "Framework CLI baseado em type hints.",
                  title_en="Typer documentation",
                  description_en="CLI framework based on type hints."),
                m("Click documentation",
                  "https://click.palletsprojects.com/",
                  "docs", "Framework CLI mais antigo, muito maduro.",
                  title_en="Click documentation",
                  description_en="Older, very mature CLI framework."),
                m("Real Python, logging",
                  "https://realpython.com/python-logging/",
                  "article", "Tutorial completo de logging.",
                  title_en="Real Python, logging",
                  description_en="Complete logging tutorial."),
                m("Brett Cannon, Why YAML safe_load",
                  "https://snarky.ca/i-dont-understand-pyyaml-s-yaml-load-function/",
                  "article", "Por que `yaml.load` é perigoso.",
                  title_en="Brett Cannon, Why YAML safe_load",
                  description_en="Why yaml.load is dangerous."),
            ],
            "questions": [
                q("Como combinar dois paths de forma portátil em Python moderno?",
                  "Path('/var/log') / 'app.log'",
                  ["'/var/log' + '/' + 'app.log'",
                   "os.path.concat(...)",
                   "string.format('/var/log/{}', 'app.log')"],
                  "pathlib usa o operador `/` para concatenar partes. Funciona em "
                  "Linux/Mac/Windows.",
                  statement_en="How do you combine two paths portably in modern Python?",
                  correct_en="Path('/var/log') / 'app.log'",
                  wrong_en=[
                            "'/var/log' + '/' + 'app.log'",
                            "os.path.concat(...)",
                            "string.format('/var/log/{}', 'app.log')",
                        ],
                  explanation_en="pathlib uses the `/` operator to join parts. It works on Linux/Mac/Windows."),
                q("Qual o risco de `yaml.load(user_input)`?",
                  "Permite executar código Python arbitrário (RCE).",
                  ["Não suporta corretamente caracteres unicode no arquivo.", "Fica bem mais lento quando o arquivo de entrada é grande.", "Simplesmente para de funcionar a partir da versão 3.11."],
                  "yaml.load aceita tags `!!python/object` que instanciam classes, "
                  "vetor de RCE. Sempre use `yaml.safe_load`.",
                  statement_en="What's the risk of `yaml.load(user_input)`?",
                  correct_en="It allows executing arbitrary Python code (RCE).",
                  wrong_en=[
                            "It doesn't correctly support unicode characters in the file.",
                            "It gets much slower when the input file is large.",
                            "It simply stops working starting with version 3.11.",
                        ],
                  explanation_en="yaml.load accepts `!!python/object` tags that instantiate classes — an RCE vector. Always use `yaml.safe_load`."),
                q("Para parsear pyproject.toml na stdlib (3.11+), use:",
                  "tomllib",
                  ["tomli (pacote externo via pip)", "configparser (formato .ini)", "json (formato incompatível)"],
                  "tomllib é a stdlib a partir do 3.11. Para versões anteriores use "
                  "tomli (mesma API).",
                  statement_en="To parse pyproject.toml with the stdlib (3.11+), use:",
                  correct_en="tomllib",
                  wrong_en=[
                            "tomli (external pip package)",
                            "configparser (.ini format)",
                            "json (incompatible format)",
                        ],
                  explanation_en="tomllib is in the stdlib from 3.11. For earlier versions use tomli (same API)."),
                q("Em argparse, `action='store_true'` é usado para...",
                  "Flags booleanas (--verbose ⇒ args.verbose = True).",
                  ["É exatamente equivalente a definir `default=True` sozinho.", "Forçar que o argumento seja passado de forma obrigatória.", "Armazenar literalmente a string `'true'` como valor do argumento."],
                  "Sem o flag → False; com o flag → True. Mais natural que --verbose=true.",
                  statement_en="In argparse, `action='store_true'` is used for...",
                  correct_en="Boolean flags (--verbose ⇒ args.verbose = True).",
                  wrong_en=[
                            "It's exactly equivalent to setting `default=True` alone.",
                            "Forcing the argument to be passed as required.",
                            "Literally storing the string `'true'` as the argument value.",
                        ],
                  explanation_en="Without the flag → False; with the flag → True. More natural than --verbose=true."),
                q("Por que separar saída em stdout vs stderr em um CLI?",
                  "Para que pipelines possam capturar só o resultado (stdout), enquanto diagnóstico vai para stderr.",
                  ["É puramente uma escolha estética de organização, sem qualquer impacto real no uso do CLI, prática ainda comum em sistema legado que raramente é atualizado.", "O canal stderr costuma ser escrito de forma consideravelmente mais rápida que o stdout, erro típico de configuração feita às pressas, sem revisão posterior.", "O stdout, por padrão, não consegue exibir corretamente caracteres codificados em UTF-8, comportamento que só some quando alguém finalmente lê a documentação."],
                  "Convenção POSIX. Permite `meu-cli | jq ...` sem misturar logs.",
                  statement_en="Why separate output into stdout vs stderr in a CLI?",
                  correct_en="So pipelines can capture only the result (stdout), while diagnostics go to stderr.",
                  wrong_en=[
                            "It's purely an aesthetic organization choice, with no real impact on CLI use, still common in rarely updated legacy systems.",
                            "The stderr channel tends to be written considerably faster than stdout, a typical rushed-configuration error without later review.",
                            "By default stdout cannot correctly display UTF-8-encoded characters, a behavior that only goes away when someone finally reads the docs.",
                        ],
                  explanation_en="POSIX convention. Allows `my-cli | jq ...` without mixing in logs."),
                q("Por que evitar `open(p).read()` direto, sem context manager?",
                  "O arquivo pode não ser fechado se o GC demorar, em servidores de longa vida vaza descritores.",
                  ["Escrever direto assim costuma causar um erro de sintaxe já na leitura do código, suposição que vale só até o primeiro imprevisto de rede ou hardware.", "Essa forma direta costuma rodar visivelmente mais devagar que usar um context manager, erro típico de configuração feita às pressas, sem revisão posterior.", "Esse problema só costuma aparecer em máquinas rodando especificamente o Windows, abordagem que funciona bem até o primeiro pico de carga real."],
                  "Sem `with`, dependemos do GC para chamar __del__ que fecha o arquivo. "
                  "Em CPython funciona quase sempre, mas não é portável e em PyPy demora.",
                  statement_en="Why avoid `open(p).read()` directly, without a context manager?",
                  correct_en="The file may not be closed if GC is slow; on long-lived servers that leaks descriptors.",
                  wrong_en=[
                            "Writing it that way usually causes a syntax error already when reading the code, an assumption that holds only until the first network or hardware surprise.",
                            "That direct form tends to run visibly slower than using a context manager, a typical rushed-configuration error without later review.",
                            "This problem usually only appears on machines specifically running Windows, an approach that works fine until the first real load spike.",
                        ],
                  explanation_en="Without `with`, we rely on GC calling __del__ to close the file. In CPython it almost always works, but it isn't portable or guaranteed."),
                q("Qual destes é o nível mais detalhado em logging padrão?",
                  "DEBUG",
                  ["INFO", "TRACE", "VERBOSE"],
                  "Níveis: DEBUG < INFO < WARNING < ERROR < CRITICAL. TRACE/VERBOSE "
                  "não existem nativamente.",
                  statement_en="Which of these is the most detailed level in standard logging?",
                  correct_en="DEBUG",
                  wrong_en=["INFO", "TRACE", "VERBOSE"],
                  explanation_en="Levels: DEBUG < INFO < WARNING < ERROR < CRITICAL. TRACE/VERBOSE don't exist natively."),
                q("Forma idiomática de receber um caminho via CLI já tipado:",
                  "p.add_argument('--config', type=Path)",
                  ["p.add_argument('--config', type=str)",
                   "p.add_argument('--config', type='path')",
                   "p.add_argument('--config'); Path(args.config)"],
                  "argparse converte para Path automaticamente; mais limpo que converter "
                  "depois.",
                  statement_en="Idiomatic way to receive an already-typed path via CLI:",
                  correct_en="p.add_argument('--config', type=Path)",
                  wrong_en=[
                            "p.add_argument('--config', type=str)",
                            "p.add_argument('--config', type='path')",
                            "p.add_argument('--config'); Path(args.config)",
                        ],
                  explanation_en="argparse converts to Path automatically; cleaner than converting afterward."),
                q("Para encerrar com código de saída 2 a partir de main():",
                  "return 2 (e usar SystemExit(main()) no entry point)",
                  ["sys.exit('2') com o código como string, direto na main", "raise Exit(2), classe que não existe na stdlib do Python", "os.exit(2), função que não existe no módulo os padrão"],
                  "Padrão idiomático: `def main() -> int: ...; raise SystemExit(main())`. "
                  "Evita `sys.exit` espalhado e facilita testar a função main().",
                  statement_en="To exit with status code 2 from main():",
                  correct_en="return 2 (and use SystemExit(main()) at the entry point)",
                  wrong_en=[
                            "sys.exit('2') with the code as a string, directly in main",
                            "raise Exit(2), a class that doesn't exist in the Python stdlib",
                            "os.exit(2), a function that doesn't exist in the standard os module",
                        ],
                  explanation_en="Idiomatic pattern: `def main() -> int: ...; raise SystemExit(main())`. Avoids scattered `sys.exit` and makes the function easy to test."),
                q("Para iterar recursivamente em todos os arquivos *.py de um diretório:",
                  "Path('.').rglob('*.py')",
                  ["os.walk('.', filter='*.py')",
                   "Path('.').glob('*.py')",
                   "shutil.find('*.py')"],
                  "rglob faz busca recursiva; glob só procura no diretório atual.",
                  statement_en="To recursively iterate all *.py files in a directory:",
                  correct_en="Path('.').rglob('*.py')",
                  wrong_en=["os.walk('.', filter='*.py')", "Path('.').glob('*.py')", "shutil.find('*.py')"],
                  explanation_en="rglob does a recursive search; glob only looks in the current directory."),
            ],
        },
        # =====================================================================
        # 6.5 HTTP, APIs e SDKs
        # =====================================================================
        {
            "title": "HTTP, APIs REST e SDKs",
            "title_en": "HTTP, REST APIs and SDKs",
            "summary": "requests/httpx, autenticação, retry com backoff, paginação, JSON e clientes de cloud.",
            "summary_en": "requests/httpx, authentication, retry with backoff, pagination, JSON and cloud clients.",
            "lesson": {
                "intro": (
                    "Boa parte de DevOps é cola entre APIs: GitHub, GitLab, Slack, PagerDuty, "
                    "Cloudflare, Vault, Vercel, AWS, GCP. Saber consumir HTTP "
                    "<em>profissionalmente</em>, com timeout, retry, autenticação correta e "
                    "manejo de paginação, separa script frágil de ferramenta confiável."
                ),
                "intro_en": (
                    "A large part of DevOps is glue between APIs: GitHub, GitLab, Slack, "
                    "PagerDuty, Cloudflare, Vault, Vercel, AWS, GCP. Knowing how to consume "
                    "HTTP <em>professionally</em> — with timeouts, retries, correct "
                    "authentication and pagination handling — separates a fragile script "
                    "from a reliable tool."
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
    Req["requests.get"] --> TO{"timeout definido?"}
    TO -- "Não" --> Hang["Pode travar para sempre"]
    TO -- "Sim" --> Resp["Response"]
    Resp --> RFS["raise_for_status"]
    RFS --> OK["2xx: segue"]
    RFS --> Err["4xx/5xx: exceção"]
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
<div class="mermaid">
flowchart LR
    Client["Cliente"] -- "request" --> API["API"]
    API -- "5xx" --> Retry{"Tentativas esgotadas?"}
    Retry -- "Não" --> Client
    Retry -- "Sim" --> Fail["Levanta exceção"]
    API -- "2xx" --> Success["Retorna o dado"]
</div>
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Frágil</strong><p>if sig == expected — comparação que vaza timing e falha em edge cases.</p></div>
    <div class="lesson-viz-card"><strong>Seguro</strong><p>hmac.compare_digest(sig, expected) — constante no tempo e explícito.</p></div>
  </div>
  <figcaption>Assinatura de webhook: trate como segredo criptográfico, não como string comum.</figcaption>
</figure>
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
                "body_en": (
                """<h3>1. `requests`: why timeout and `raise_for_status` are not optional</h3>
<pre><code>import requests

r = requests.get(
    "https://api.github.com/repos/python/cpython",
    headers={"User-Agent": "my-tool/1.0", "Accept": "application/vnd.github+json"},
    timeout=(3.05, 10),  # (connect, read), SEMPRE
)
r.raise_for_status()
data = r.json()
print(data["stargazers_count"])</code></pre>
<p>Without a <code>timeout</code>, the TCP socket stays open until the operating
system decides to close it — which in many environments is <em>never</em>
(without keepalive configured, it can hang for hours). A deploy
script that stalls on an HTTP call without a timeout doesn't fail visibly: it
simply stops, and whoever is watching the pipeline sees "running" indefinitely,
with no error log at all — the worst kind of failure to diagnose, because nothing
"broke". The <code>(connect, read)</code> pair exists because they are two distinct
stages: time to open the connection is usually short and stable; time
for the server to respond can legitimately be longer (a slow API
processing), so different limits make sense.</p>
<div class="mermaid">
flowchart LR
    Req["requests.get"] --> TO{"timeout set?"}
    TO -- "No" --> Hang["Can hang forever"]
    TO -- "Yes" --> Resp["Response"]
    Resp --> RFS["raise_for_status"]
    RFS --> OK["2xx: continue"]
    RFS --> Err["4xx/5xx: exception"]
</div>

<p><code>raise_for_status()</code> solves a subtle problem: <code>requests</code>
does not raise an exception on its own when the API responds 404 or 500 — it returns
a normal <code>Response</code> object, and it's up to you to check
<code>r.status_code</code>. Without that call, code that does
<code>data = r.json()</code> directly processes a 500 error body (which
may not even be valid JSON, or may be an error-format JSON totally
different from what was expected) as if it were the success response — and the bug only
shows up much later, in a confusing <code>KeyError</code> far from where the
real problem is.</p>

<h3>2. `Session`: reusing the connection, not just the headers</h3>
<pre><code>s = requests.Session()
s.headers.update({"User-Agent": "my-tool/1.0",
                  "Authorization": f"Bearer {token}"})

for repo in repos:
    r = s.get(f"https://api.github.com/repos/{repo}", timeout=10)
    r.raise_for_status()</code></pre>
<p>The gain from using <code>Session</code> instead of a bare
<code>requests.get()</code> isn't only avoiding repeated headers: each
<code>requests.get()</code> call without a session opens a new TCP connection and,
if HTTPS, reds the entire TLS handshake — two or three extra network
round-trips <em>per call</em>. In a session, the connection stays in the pool and is
reused across requests to the same host. In a script that makes 100 calls to the same
API, the difference between session and one-off calls is often the difference between
seconds and minutes.</p>

<h3>3. Retry with backoff: only for failures worth repeating</h3>
<div class="mermaid">
flowchart LR
    Client["Client"] -- "request" --> API["API"]
    API -- "5xx" --> Retry{"Retries exhausted?"}
    Retry -- "No" --> Client
    Retry -- "Yes" --> Fail["Raise exception"]
    API -- "2xx" --> Success["Return the data"]
</div>
<p>Transient errors (502, 503, 504, network timeout) tend to resolve
themselves on a new attempt — the server was overloaded for a
moment, not broken. Configuring this at the transport layer, not in
manual loops, ensures retry logic applies to every call on the
session consistently:</p>
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
<p><code>backoff_factor</code> grows exponentially between attempts
(0.5s, 1s, 2s, 4s...) — without that growing spacing, an immediate retry
repeated against an already overloaded service worsens the overload instead of
waiting for it to pass, an effect known as a <em>thundering herd</em>. The
dangerous detail is <code>allowed_methods</code> including
<code>"POST"</code>: automatically retrying a POST that is NOT idempotent
(creating a resource, triggering a payment) can duplicate the side effect
if the first attempt succeeded on the server but the response was lost
on the way back. Only include POST in retry if the API supports an
<code>Idempotency-Key</code> that deduplicates on the server side.</p>

<h3>4. Authentication: Basic, Bearer, mTLS — and where the token NEVER goes</h3>
<pre><code># Bearer (mais comum em APIs modernas)
headers = {"Authorization": f"Bearer {token}"}

# Basic (legacy)
from requests.auth import HTTPBasicAuth
r = requests.get(url, auth=HTTPBasicAuth(user, password))

# mTLS, certificado de cliente
r = requests.get(url, cert=("client.crt", "client.key"), verify="ca.pem")</code></pre>
<p>Bearer token is the standard today because it is <em>opaque</em> to whoever carries it
— the client doesn't know and doesn't need to know what's inside, it just forwards it. Basic
Auth sends username and password in text (only protected by transport TLS, not
by itself) on every request, which increases the exposure surface if a
proxy along the way logs headers. mTLS flips who proves identity:
instead of only the client proving who it is, the SERVER also must prove its own — useful
between internal services where both sides need to trust each other,
not only the client trusting the server.</p>
<p>Tokens never go in source code, not even "just for now", nor in a
hardcoded variable you promise to remove later — they go into an environment
variable injected at runtime, or a secret manager (AWS Secrets Manager, GCP
Secret Manager, Vault). The practical reason: anything committed to git
remains accessible in history even after being "removed" in a later
commit — rotating the exposed credential is the only real fix.</p>

<h3>5. Pagination: why ignoring it silently corrupts data</h3>
<p>Almost every real API that lists resources limits how many it returns per
call — usually between 20 and 100. Ignoring that doesn't error: you get
a valid 200 response with the first page, and the script keeps thinking it
processed "all repositories" when it only processed the first 30. The
three most common patterns:</p>
<ul>
<li><strong>Page/per_page</strong>: <code>?page=2&per_page=100</code> — simple,
but can skip or repeat items if the list changes between one page and
another.</li>
<li><strong>Cursor</strong>: the response brings an opaque
<code>next_cursor</code> that you pass on the next call — stable even as the list
changes, because the cursor marks a real position, not a recalculated page
number.</li>
<li><strong>Link header</strong>: GitHub and other "pure" HTTP APIs use
<code>Link: &lt;...&gt;; rel="next"</code> in the response header, instead
of a field in the JSON body.</li>
</ul>
<pre><code>def all_repos(org: str):
    url = f"https://api.github.com/orgs/{org}/repos"
    while url:
        r = s.get(url, params={"per_page": 100}, timeout=10)
        r.raise_for_status()
        yield from r.json()
        url = r.links.get("next", {}).get("url")</code></pre>
<p>Using <code>yield</code> instead of accumulating everything in a list before
returning keeps memory constant even with tens of thousands of items —
the caller processes item by item as each page arrives, without ever
holding the entire collection in RAM at once.</p>

<h3>6. `httpx`: the same model, with real concurrency</h3>
<p><code>httpx</code> has an API almost identical to <code>requests</code>
(migration is usually swapping the import), but solves a structural
limitation: <code>requests</code> is synchronous underneath, so querying 50
endpoints means waiting for each response before firing the
next. <code>httpx</code> supports <code>async</code>, letting you fire
all calls at once and await them together:</p>
<pre><code>import httpx

async with httpx.AsyncClient(timeout=10.0) as client:
    tasks = [client.get(u) for u in urls]
    responses = await asyncio.gather(*tasks)
    for r in responses:
        r.raise_for_status()</code></pre>
<p>For network I/O (which spends most of its time waiting, not
processing), this concurrent fan-out pattern usually reduces total time
from "sum of all latencies" to "latency of the slowest" — the
difference between minutes and seconds when querying dozens of services.</p>

<h3>7. Building APIs with FastAPI: types as contract, not decoration</h3>
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
<p>The difference between FastAPI and writing a raw HTTP handler is that the type
hints on the <code>Deploy</code> class aren't just documentation for humans:
Pydantic uses them at runtime to VALIDATE the request body before
your code runs — a POST missing the <code>image</code> field, or with
<code>replicas</code> as a non-numeric string, is rejected automatically
with a detailed 422, without you writing any manual check. The same
annotations generate browsable OpenAPI docs at <code>/docs</code>. For
internal tools (an endpoint that triggers a deploy, for example), that
eliminates an entire class of "I forgot to validate a field" bugs.</p>

<h3>8. Webhooks: why comparing signatures with `==` is a security failure</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Fragile</strong><p>if sig == expected — a comparison that leaks timing and fails on edge cases.</p></div>
    <div class="lesson-viz-card"><strong>Safe</strong><p>hmac.compare_digest(sig, expected) — constant-time and explicit.</p></div>
  </div>
  <figcaption>Webhook signatures: treat them as cryptographic secrets, not ordinary strings.</figcaption>
</figure>
<pre><code>import hmac, hashlib

def verify_github(payload: bytes, signature: str, secret: str) -&gt; bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)</code></pre>
<p>A webhook is an inverted API: instead of you calling the external service,
it calls YOU — and because the endpoint must stay public on the internet to
receive it, anyone can send a request pretending to be GitHub.
The HMAC signature in the header proves the body came from whoever has the
shared secret, by computing a hash over the payload and comparing it with
what the sender sent.</p>
<p>The detail that makes that comparison worthwhile is
<code>hmac.compare_digest</code> instead of a simple <code>==</code>:
ordinary string comparison in Python stops at the first differing character,
so the TIME the comparison takes leaks information about how many
leading characters already match — an attacker can, byte by byte, measure
tiny latency differences and reconstruct the valid signature without
ever needing to break the hash itself. <code>compare_digest</code> always
compares in constant time, regardless of how many characters match.</p>
"""
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
                "practical_en": (
                    "Implement <code>gh_repos.py</code> that: (1) reads the GitHub token "
                    "from <code>os.environ['GITHUB_TOKEN']</code>; (2) uses a "
                    "<code>Session</code> with retry configured; (3) lists ALL repositories "
                    "of an organization (pagination via Link header); (4) prints name, "
                    "stars, last update as CSV on stdout; (5) manages rate limit by reading "
                    "the <code>X-RateLimit-Remaining</code> header and sleeping if it drops "
                    "below 100."
                ),
            },
            "materials": [
                m("requests, quickstart",
                  "https://requests.readthedocs.io/en/latest/user/quickstart/",
                  "docs", "Documentação oficial do requests.",
                  title_en="requests, quickstart",
                  description_en="Official requests documentation."),
                m("httpx documentation",
                  "https://www.python-httpx.org/",
                  "docs", "Cliente HTTP/2 sync e async.",
                  title_en="httpx documentation",
                  description_en="Sync and async HTTP/2 client."),
                m("urllib3 Retry",
                  "https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry",
                  "docs", "Configuração de retry.",
                  title_en="urllib3 Retry",
                  description_en="Retry configuration."),
                m("FastAPI tutorial",
                  "https://fastapi.tiangolo.com/tutorial/",
                  "docs", "Construindo APIs com FastAPI.",
                  title_en="FastAPI tutorial",
                  description_en="Building APIs with FastAPI."),
                m("REST API Design, Microsoft Guidelines",
                  "https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md",
                  "docs", "Boas práticas de design REST.",
                  title_en="REST API Design, Microsoft Guidelines",
                  description_en="REST design guidelines."),
                m("Stripe, API best practices (idempotency)",
                  "https://stripe.com/docs/api/idempotent_requests",
                  "docs", "Como Stripe evita duplicações em retries.",
                  title_en="Stripe, API best practices (idempotency)",
                  description_en="Idempotency keys and API design."),
            ],
            "questions": [
                q("Por que `requests.get(url)` sem timeout é perigoso em produção?",
                  "A chamada pode travar indefinidamente se o servidor não responder.",
                  ["A chamada fica só um pouco mais lenta do que fazer o mesmo request com timeout.", "A chamada deixa de funcionar por completo quando a URL usa o protocolo HTTPS.", "Isso passa a causar um erro de sintaxe a partir especificamente da versão 3.11."],
                  "Sem timeout, uma conexão problemática pode travar o programa para "
                  "sempre. Sempre defina (connect_timeout, read_timeout).",
                  statement_en="Why is `requests.get(url)` without a timeout dangerous in production?",
                  correct_en="The call can hang indefinitely if the server doesn't respond.",
                  wrong_en=[
                            "The call only gets a bit slower than doing the same request with a timeout.",
                            "The call completely stops working when the URL uses the HTTPS protocol.",
                            "It starts causing a syntax error specifically from version 3.11 onward.",
                        ],
                  explanation_en="Without a timeout, a problematic connection can freeze the program forever. Always set (connect_timeout, read_timeout)."),
                q("`raise_for_status()` faz o quê?",
                  "Lança HTTPError se o status code for 4xx ou 5xx.",
                  ["Reenvia automaticamente a mesma requisição para o servidor.", "Lança um erro em qualquer status code recebido, mesmo 2xx.", "Só imprime o status code recebido diretamente na tela."],
                  "É a forma idiomática de tratar erros HTTP. Sem ela, você processa "
                  "respostas de erro como se fossem sucesso.",
                  statement_en="What does `raise_for_status()` do?",
                  correct_en="Raises HTTPError if the status code is 4xx or 5xx.",
                  wrong_en=[
                            "Automatically resends the same request to the server.",
                            "Raises an error on any received status code, even 2xx.",
                            "Only prints the received status code directly to the screen.",
                        ],
                  explanation_en="It's the idiomatic way to handle HTTP errors. Without it, you process error responses as if they were success."),
                q("Para retry de erros transitórios (5xx), você deveria configurar...",
                  "urllib3.Retry com backoff_factor e status_forcelist.",
                  ["Escrever um loop `while True` chamando `sleep` manualmente.", "Rodar a chamada numa thread separada dentro de um try/except.", "Não fazer retry algum e deixar a chamada falhar rápido."],
                  "Retry com backoff exponencial é o padrão. Loop manual sem jitter "
                  "pode causar thundering herd.",
                  statement_en="For retrying transient errors (5xx), you should configure...",
                  correct_en="urllib3.Retry with backoff_factor and status_forcelist.",
                  wrong_en=[
                            "Writing a `while True` loop that calls `sleep` manually.",
                            "Running the call in a separate thread inside a try/except.",
                            "Not retrying at all and letting the call fail fast.",
                        ],
                  explanation_en="Retry with exponential backoff is the standard. A manual loop without jitter can cause a thundering herd."),
                q("Por que usar `requests.Session` em vez de chamadas avulsas?",
                  "Reusa conexões TCP/TLS (connection pooling), reduzindo latência.",
                  ["Mantém os cookies recebidos guardados por um período fixo de exatamente 24 horas.", "Passou a ser uma exigência obrigatória da biblioteca a partir da versão 3.10.", "Permite que as requisições continuem sendo feitas mesmo sem conexão de rede."],
                  "Em scripts com várias chamadas ao mesmo host, Session evita "
                  "handshake TLS repetido.",
                  statement_en="Why use `requests.Session` instead of one-off calls?",
                  correct_en="It reuses TCP/TLS connections (connection pooling), reducing latency.",
                  wrong_en=[
                            "It keeps received cookies stored for a fixed period of exactly 24 hours.",
                            "It became a mandatory library requirement starting with version 3.10.",
                            "It allows requests to keep being made even without a network connection.",
                        ],
                  explanation_en="In scripts with many calls to the same host, Session avoids repeated TLS handshakes."),
                q("Para verificar uma assinatura HMAC de webhook com segurança:",
                  "hmac.compare_digest(esperado, recebido)",
                  ["esperado == recebido (comparação direta)", "esperado in recebido (contido em vez de igual)", "recebido.startswith(esperado) (prefixo)"],
                  "compare_digest é constant-time: não vaza informação por timing. "
                  "`==` para de comparar no primeiro byte diferente.",
                  statement_en="To verify a webhook HMAC signature securely:",
                  correct_en="hmac.compare_digest(expected, received)",
                  wrong_en=[
                            "expected == received (direct comparison)",
                            "expected in received (contained instead of equal)",
                            "received.startswith(expected) (prefix)",
                        ],
                  explanation_en="compare_digest is constant-time: it doesn't leak information via timing. `==` stops comparing at the first differing byte."),
                q("Em paginação por Link header (estilo GitHub), o atributo `r.links['next']['url']` retorna...",
                  "A URL completa da próxima página.",
                  ["Retorna só o número correspondente à próxima página.", "Retorna um booleano indicando só se existe próxima página.", "Retorna o número total de páginas disponíveis na resposta."],
                  "requests parseia o Link header automaticamente em dict, basta "
                  "checar 'next'.",
                  statement_en="In Link-header pagination (GitHub style), `r.links['next']['url']` returns...",
                  correct_en="The full URL of the next page.",
                  wrong_en=[
                            "Only the number corresponding to the next page.",
                            "A boolean indicating only whether a next page exists.",
                            "The total number of pages available in the response.",
                        ],
                  explanation_en="requests parses the Link header automatically into a dict; just check for 'next'."),
                q("Token de API em código-fonte é problema porque...",
                  "Vai parar no git e em logs; rotação fica difícil; quem tem acesso ao repo tem o token.",
                  ["É só uma questão de organização estética do código-fonte, muito pouco mais além disso.", "Reduz de forma perceptível a performance da aplicação já em ambiente de produção.", "Costuma causar falha de execução especificamente em servidores rodando Linux."],
                  "Tokens devem vir de env, secret manager ou keyring. Se vazar, "
                  "rotacione imediatamente.",
                  statement_en="An API token in source code is a problem because...",
                  correct_en="It ends up in git and logs; rotation gets hard; anyone with repo access has the token.",
                  wrong_en=[
                            "It's only a matter of aesthetic source-code organization, little more than that.",
                            "It noticeably reduces application performance already in production.",
                            "It tends to cause runtime failure specifically on servers running Linux.",
                        ],
                  explanation_en="Tokens should come from env, a secret manager, or a keyring. If leaked, rotate immediately."),
                q("`httpx.AsyncClient` é particularmente útil quando...",
                  "Você precisa fazer várias requisições em paralelo (fan-out).",
                  ["Você quer, por algum motivo, evitar usar conexões HTTPS na sua aplicação.", "O seu projeto ainda depende inteiramente da versão antiga, o Python 2.", "Você só precisa mesmo fazer uma única requisição isolada e simples."],
                  "Async + gather permite N requisições simultâneas com baixa overhead. "
                  "Síncrono seria sequencial.",
                  statement_en="`httpx.AsyncClient` is particularly useful when...",
                  correct_en="You need to make several requests in parallel (fan-out).",
                  wrong_en=[
                            "You want, for some reason, to avoid using HTTPS connections in your app.",
                            "Your project still depends entirely on the old version, Python 2.",
                            "You really only need to make a single simple isolated request.",
                        ],
                  explanation_en="Async + gather allows N simultaneous requests with low overhead. Sync would be sequential."),
                q("Para autenticação Bearer Token, o header correto é:",
                  "Authorization: Bearer <token>",
                  ["Auth: <token> (header customizado)", "X-Bearer: <token> (header customizado)", "Cookie: token=<token> (via cookie)"],
                  "Padrão RFC 6750. Sempre o esquema explícito antes do token.",
                  statement_en="For Bearer Token authentication, the correct header is:",
                  correct_en="Authorization: Bearer <token>",
                  wrong_en=[
                            "Auth: <token> (custom header)",
                            "X-Bearer: <token> (custom header)",
                            "Cookie: token=<token> (via cookie)",
                        ],
                  explanation_en="RFC 6750 standard. Always the explicit scheme before the token."),
                q("Vale a pena usar `r.json()` se o status for 500?",
                  "Não, chame raise_for_status() primeiro; senão pode parsear body de erro como dado válido.",
                  ["Vale a pena fazer isso em qualquer situação, mesmo sem checar o status antes, resultado típico de copiar configuração de outro projeto sem adaptar.", "Só vale a pena fazer isso quando a aplicação já está rodando em produção, atalho que parece seguro isolado, mas quebra quando combinado com outros sistemas.", "Só vale a pena fazer isso quando a chamada acontece dentro da rede interna, suposição que só se sustenta enquanto o time é pequeno."],
                  "5xx geralmente vêm com body em texto/HTML, parsear como JSON gera "
                  "erro confuso. raise_for_status interrompe antes.",
                  statement_en="Is it worth using `r.json()` if the status is 500?",
                  correct_en="No — call raise_for_status() first; otherwise you may parse an error body as valid data.",
                  wrong_en=[
                            "It's worth doing in any situation, even without checking status first — a typical result of copying config from another project without adapting it.",
                            "It's only worth doing when the app is already running in production — a shortcut that seems safe alone but breaks when combined with other systems.",
                            "It's only worth doing when the call happens inside the internal network — an assumption that only holds while the team is small.",
                        ],
                  explanation_en="5xx responses usually come with a text/HTML body; parsing as JSON yields a confusing error. raise_for_status stops before that."),
            ],
        },
        # =====================================================================
        # 6.6 Automação de sistema
        # =====================================================================
        {
            "title": "Automação de sistema com Python",
            "title_en": "System Automation with Python",
            "summary": "subprocess seguro, manipulação de processos, ssh remoto, integrações com shell e Ansible.",
            "summary_en": "Safe subprocess, process control, remote SSH, shell integrations and Ansible.",
            "lesson": {
                "intro": (
                    "Python brilha como cola entre comandos do sistema, chamando "
                    "<code>kubectl</code>, <code>terraform</code>, <code>aws</code>, "
                    "<code>git</code>... O perigo é fazer isso ingenuamente: "
                    "<code>os.system(\"rm \" + user_input)</code> é uma das classes "
                    "clássicas de injeção. Esta aula mostra como automatizar comandos com "
                    "segurança, lendo saída em tempo real e tratando erros corretamente."
                ),
                "intro_en": (
                    "Python shines as glue between system commands, calling "
                    "<code>kubectl</code>, <code>terraform</code>, <code>aws</code>, "
                    "<code>git</code>... The danger is doing it naively: <code>os.system(\"rm "
                    "\" + user_input)</code> is one of the classic injection classes. This "
                    "lesson shows how to automate commands safely, reading output in real "
                    "time and handling errors correctly."
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>shell=True</strong><p>Pipe e glob fáceis — mas injeção se qualquer pedaço vier de input externo.</p></div>
    <div class="lesson-viz-card"><strong>Lista de args</strong><p>Sem shell: o binário recebe argv já separado; user input não vira comando.</p></div>
  </div>
  <figcaption>Regra prática: shell só quando o shell é indispensável e a string é 100% controlada.</figcaption>
</figure>
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>check=True + timeout em todo subprocess</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Logs em stderr, dados em stdout</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Tratar sinais e limpar temporários</p></div>
  </div>
  <figcaption>Checklist mínimo antes de colocar o script no cron ou no CI.</figcaption>
</figure>
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
                "body_en": (
                """<h3>1. `subprocess.run`: why an argument list is the defense, not a style detail</h3>
<pre><code>import subprocess

result = subprocess.run(
    ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
    capture_output=True,
    text=True,        # decodifica como str (utf-8 default)
    timeout=30,
    check=True,       # raise CalledProcessError se exit != 0
)
data = json.loads(result.stdout)</code></pre>
<p>When you pass a LIST of arguments, each element goes straight
to the child process as a separate argument — the operating system
never interprets space, semicolon, pipe or <code>$()</code> inside
one of those elements as special syntax, because there is no shell
in the middle interpreting the string. That's why
<code>["ls", "-l", path]</code> is safe even if
<code>path = "; rm -rf /"</code>: that entire value becomes ONE literal
argument named "; rm -rf /", not a sequence of commands. Meanwhile
<code>os.system(f"ls {path}")</code> or <code>subprocess.run(cmd,
shell=True)</code> pass the whole string to a real shell
(<code>/bin/sh</code>) to interpret it — and at that point, any
shell metacharacter inside the value becomes an executable command. That's the
reason "concatenate command + user input" is one of the
oldest and most exploited vulnerability classes in
automation tools.</p>
<div class="mermaid">
flowchart LR
    Py["Python script"] --> Sub["subprocess.run with arg list"]
    Sub --> Proc["Child process"]
    Proc --> Out["stdout, stderr and returncode"]
    Out --> Py
</div>

<p><code>timeout</code> exists for the same reason as in HTTP calls: a
child process can hang waiting for something that never arrives (an interactive
prompt asking for confirmation, a network connection that never drops) and without a
timeout the parent script hangs indefinitely. <code>check=True</code>
turns a non-zero exit code into an exception — without it, a command
that failed silently (kubectl didn't find the namespace, for example)
leaves <code>result.stdout</code> empty or with an error, and the following
<code>json.loads</code> breaks in a way that doesn't make clear
the command itself had already failed.</p>

<h3>2. Streaming: why waiting for the process to finish is sometimes the wrong choice</h3>
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
<p><code>subprocess.run</code> only returns control when the process
finishes — for a 20-minute <code>terraform apply</code>, that
means getting NO feedback until the end, with no way to know if it's
progressing or stuck. <code>Popen</code> returns control immediately
with a handle to the still-running process; iterating
<code>p.stdout</code> line by line delivers each line as soon as the
process produces it, letting you show real-time progress and write
to a log file at the same time — the same pattern behind any
CI tool that shows "live" logs instead of only the final
result.</p>

<h3>3. Subprocess environment variables: inherit by default, override carefully</h3>
<pre><code>env = os.environ.copy()       # NUNCA passe os.environ direto e mute
env["KUBECONFIG"] = "/etc/k8s/prod.kubeconfig"
env["AWS_PROFILE"] = "prod"
subprocess.run(["kubectl", "get", "ns"], env=env, check=True)</code></pre>
<p>The <code>env=</code> parameter, when provided, REPLACES the entire child
process environment — it does not merge with the current environment. Passing
<code>env={"KUBECONFIG": "..."}</code> directly (without
<code>.copy()</code> of <code>os.environ</code> first) wipes
<code>PATH</code>, <code>HOME</code>, <code>USER</code> and everything else the
child would normally inherit — a mistake that shows up as the
subprocess not finding binaries that should be on PATH, a
symptom that doesn't obviously point to "I forgot to copy the environment".</p>

<h3>4. `shell=True`: when the risk is worth the benefit, and the shell-free alternative</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>shell=True</strong><p>Easy pipes and globs — but injection if any piece comes from external input.</p></div>
    <div class="lesson-viz-card"><strong>Arg list</strong><p>No shell: the binary gets a separated argv; user input does not become a command.</p></div>
  </div>
  <figcaption>Practical rule: shell only when the shell is indispensable and the string is fully controlled.</figcaption>
</figure>
<pre><code>cmd = "ps aux | grep nginx | wc -l"
subprocess.run(cmd, shell=True, check=True)</code></pre>
<p>Native shell pipes and redirection (<code>|</code>,
<code>&gt;</code>, <code>&amp;&amp;</code>) only exist when a real shell
interprets the string — it's the only case where <code>shell=True</code>
actually saves work. The risk is the same as section 1: if any
part of that string comes from outside (user, file, network variable), it's
injection. For the same result without giving up list safety,
you compose the pipeline manually by chaining processes:</p>
<pre><code>p1 = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE)
p2 = subprocess.Popen(["grep", "nginx"], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
out = p2.communicate()[0]</code></pre>
<p>When <code>shell=True</code> is truly unavoidable (compatibility
with a legacy script, for example) and part of the command comes from outside,
<code>shlex.quote</code> escapes the string so the shell treats it as
a single literal token, neutralizing metacharacters:</p>
<pre><code>import shlex
subprocess.run(f"ls {shlex.quote(user_path)}", shell=True)</code></pre>

<h3>5. Filesystem operations: `shutil` and the guarantees each function offers</h3>
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
<p>The word "atomic" in <code>shutil.move</code>/<code>os.replace</code>
has an important limit: the operation is only atomic (all-or-nothing, with no
visible intermediate state) when source and destination are on the SAME
filesystem, because then the OS only needs to update a
directory pointer (the kernel's <code>rename(2)</code> call). Across
different filesystems (for example, moving from tmpfs <code>/tmp</code>
to a mounted disk), no direct rename is possible — the library
automatically falls back to copy then delete the original, an operation
that can be interrupted mid-way, leaving both sides partially
written if the process dies between the copy and the removal.</p>

<h3>6. Temporary files: why `mktemp` was abandoned</h3>
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
<p>The old <code>tempfile.mktemp()</code> function only GENERATED a supposedly unique
filename without creating the file — leaving a time window
between "generate the name" and "open the file" where another process (or a
local attacker) could create a file or symlink with that same name
first, a classic race condition (the same bug class as the historic
shared <code>/tmp</code> attack, seen in the Linux lesson of
Phase 1). <code>NamedTemporaryFile</code> solves that by creating the file
ATOMICALLY at the moment the name is generated, with no such window.</p>

<h3>7. Remote SSH: Fabric for one-off tasks, Ansible for scale</h3>
<pre><code>from fabric import Connection   # pip install fabric

with Connection("deploy@10.0.1.5", connect_kwargs={"key_filename": "~/.ssh/id_ed25519"}) as c:
    r = c.run("systemctl status nginx", warn=True)
    if r.return_code != 0:
        c.sudo("systemctl restart nginx")
    c.put("./nginx.conf", "/etc/nginx/conf.d/app.conf")
    c.run("nginx -t && systemctl reload nginx")</code></pre>
<p><code>warn=True</code> on <code>c.run</code> is the opposite of
<code>check=True</code> from section 1: instead of raising an automatic exception
on a non-zero exit code, it lets the code check
<code>r.return_code</code> manually and decide what to do — needed
here because "nginx is not running" is an EXPECTED result the script
handles (by restarting), not a fatal error that should abort. For an
inventory of dozens or hundreds of hosts, Ansible wins by already having
parallelism, declarative idempotency and a playbook format that
someone else on the team can read without knowing Python — Fabric is better
for one-off automation where writing real Python (with all the language's
conditional logic) is worth the extra effort.</p>

<h3>8. Signals: shut down gracefully instead of dying mid-write</h3>
<pre><code>import signal

shutdown = False
def _handle(sig, frame):
    global shutdown; shutdown = True

signal.signal(signal.SIGTERM, _handle)
signal.signal(signal.SIGINT,  _handle)

while not shutdown:
    do_iteration()
cleanup()</code></pre>
<p>Without this handler, a <code>SIGTERM</code> (the default signal that
<code>systemctl stop</code> or a container orchestrator sends before
killing a process) interrupts the program AT THE EXACT POINT where it
was — mid file write, mid transaction, mid
network call — with no chance to close resources or save state.
Registering a handler turns the signal into a flag the main loop
checks at its own pace, finishing the iteration in progress before
exiting. <code>SIGKILL</code> (the "kill now" of <code>kill -9</code>) cannot
be intercepted by any handler — it's the last-resort signal
when a process repeatedly ignores <code>SIGTERM</code>.</p>

<h3>9. Checklist for scripts that will run in production</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>check=True + timeout on every subprocess</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Logs on stderr, data on stdout</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Handle signals and clean up temps</p></div>
  </div>
  <figcaption>Minimum checklist before putting the script in cron or CI.</figcaption>
</figure>
<ul>
<li>Always <code>check=True</code>, always <code>timeout</code> — the two
cheapest protections against the two most common failures (silent
error, indefinite hang).</li>
<li>Never <code>shell=True</code> with unescaped user input —
even "just once, internal script" becomes a problem when the script grows and
someone adds an input source you didn't anticipate.</li>
<li>Log the exact command (with <code>shlex.join</code>, the inverse
of <code>shlex.quote</code>) before executing — when something fails in
production, being able to see the literal command that ran saves hours of
"reproduce the bug".</li>
<li>For retry, use a mature lib (tenacity) instead of rewriting
exponential backoff by hand — the "quick" homemade version usually forgets jitter
and turns a partial outage into a thundering herd.</li>
<li>Handle <code>SIGTERM</code> if the script can take more than a few
seconds — especially anything that writes state or holds locks.</li>
</ul>
"""
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
                "practical_en": (
                    "Create <code>backup_db.py</code> that: (1) runs <code>pg_dump</code> "
                    "with a 5-minute timeout, capturing output; (2) writes a file to "
                    "<code>/tmp/&lt;db&gt;-&lt;date&gt;.sql.gz</code> using "
                    "<code>gzip</code>; (3) uploads to S3 via <code>aws s3 cp</code> (also "
                    "via subprocess); (4) cleans up the local file in <code>finally</code>; "
                    "(5) logs the exact command (escaped), duration and status."
                ),
            },
            "materials": [
                m("Python docs, subprocess",
                  "https://docs.python.org/3/library/subprocess.html",
                  "docs", "Referência completa de subprocess.",
                  title_en="Python docs, subprocess",
                  description_en="Official subprocess documentation."),
                m("Real Python, subprocess",
                  "https://realpython.com/python-subprocess/",
                  "article", "Tutorial com exemplos práticos.",
                  title_en="Real Python, subprocess",
                  description_en="Practical subprocess guide."),
                m("shutil, alto nível para arquivos",
                  "https://docs.python.org/3/library/shutil.html",
                  "docs", "Cópias, moves, espaço em disco.",
                  title_en="shutil, high-level file operations",
                  description_en="High-level file operations."),
                m("Fabric documentation",
                  "https://www.fabfile.org/",
                  "docs", "Automação SSH em Python.",
                  title_en="Fabric documentation",
                  description_en="Remote SSH execution with Fabric."),
                m("Paramiko, SSH puro Python",
                  "https://www.paramiko.org/",
                  "docs", "Lib subjacente ao Fabric.",
                  title_en="Paramiko, pure-Python SSH",
                  description_en="Pure-Python SSH library."),
                m("Tenacity, retry library",
                  "https://tenacity.readthedocs.io/",
                  "docs", "Decoradores de retry com backoff.",
                  title_en="Tenacity, retry library",
                  description_en="Declarative retry library."),
            ],
            "questions": [
                q("Por que `subprocess.run([\"rm\", path])` é mais seguro que `os.system(f\"rm {path}\")`?",
                  "Argumentos em lista são passados direto ao processo, sem interpretação de shell, evitando injeção.",
                  ["É só uma forma um pouco mais rápida de rodar o mesmo comando, só isso, decisão que parece inofensiva isolada, mas se acumula com o tempo.", "O `subprocess` geralmente captura a saída do comando automaticamente por padrão, prática que troca previsibilidade por economia de esforço imediato.", "A função `os.system` simplesmente deixou de existir a partir do Python 3, suposição que só vale em ambiente de desenvolvimento, não em produção."],
                  "Lista evita interpretação de espaços, `;`, `|`, `$()`. Vetor clássico "
                  "de injeção desaparece.",
                  statement_en="Why is `subprocess.run([\"rm\", path])` safer than `os.system(f\"rm {path}\")`?",
                  correct_en="List arguments are passed straight to the process, with no shell interpretation, avoiding injection.",
                  wrong_en=[
                            "It's just a slightly faster way to run the same command, nothing more — a decision that seems harmless alone but accumulates over time.",
                            "subprocess usually captures command output automatically by default — a practice that trades predictability for immediate effort savings.",
                            "The `os.system` function simply stopped existing starting with Python 3 — an assumption that only holds in development, not production.",
                        ],
                  explanation_en="A list avoids interpretation of spaces, `;`, `|`, `$()`. The classic injection vector disappears."),
                q("Para garantir que `subprocess.run` falhe se o exit code não for 0:",
                  "Passe `check=True`.",
                  ["Verificar manualmente o valor de `result.returncode` depois de cada chamada.", "Não existe forma direta de fazer esse tipo de verificação.", "Configurar o parâmetro `stderr=PIPE` na chamada do subprocess."],
                  "check=True levanta CalledProcessError automaticamente. Manual também "
                  "funciona, mas é fácil esquecer.",
                  statement_en="To ensure `subprocess.run` fails if the exit code isn't 0:",
                  correct_en="Pass `check=True`.",
                  wrong_en=[
                            "Manually check `result.returncode` after every call.",
                            "There is no direct way to do this kind of check.",
                            "Set the `stderr=PIPE` parameter on the subprocess call.",
                        ],
                  explanation_en="check=True raises CalledProcessError automatically. Manual checks also work, but they're easy to forget."),
                q("`shell=True` é arriscado quando...",
                  "A string contém input não escapado vindo de fora (usuário, arquivo, rede).",
                  ["Só fica arriscado quando o comando envolve algum tipo de pipe entre processos.", "Fica arriscado em praticamente qualquer chamada, mesmo sem qualquer input externo.", "Só fica arriscado quando o comando é executado especificamente em Windows."],
                  "shell=True interpreta metacaracteres do shell. Se um deles vier do "
                  "usuário, é RCE. Use lista de args ou shlex.quote.",
                  statement_en="`shell=True` is risky when...",
                  correct_en="The string contains unescaped input from outside (user, file, network).",
                  wrong_en=[
                            "It's only risky when the command involves some kind of pipe between processes.",
                            "It's risky on virtually any call, even without any external input.",
                            "It's only risky when the command runs specifically on Windows.",
                        ],
                  explanation_en="shell=True interprets shell metacharacters. If one comes from the user, it's RCE. Use an arg list or shlex.quote."),
                q("Para mostrar saída de um processo longo enquanto ele roda, use:",
                  "subprocess.Popen com stdout=PIPE e iterar p.stdout linha a linha.",
                  ["Chamar `subprocess.check_output`, que só retorna ao final.", "Usar `subprocess.run` com `capture_output`, que só retorna no fim da execução.", "Chamar `os.system`, que mostra a saída direto no terminal."],
                  "run/check_output bloqueiam até o fim. Popen + iter dá streaming "
                  "em tempo real.",
                  statement_en="To show output from a long-running process while it runs, use:",
                  correct_en="subprocess.Popen with stdout=PIPE and iterate p.stdout line by line.",
                  wrong_en=[
                            "Call `subprocess.check_output`, which only returns at the end.",
                            "Use `subprocess.run` with `capture_output`, which only returns when execution finishes.",
                            "Call `os.system`, which shows output directly in the terminal.",
                        ],
                  explanation_en="run/check_output block until the end. Popen + iterate gives real-time streaming."),
                q("Ao definir env= em subprocess, qual erro é comum?",
                  "Esquecer de copiar os.environ, o subprocesso fica sem PATH e variáveis essenciais.",
                  ["Costuma provocar diretamente um segfault dentro do processo filho criado.", "Costuma quebrar de forma específica a variável de ambiente chamada HOME.", "Torna tecnicamente muito difícil passar qualquer variável de ambiente customizada."],
                  "Comece com `env = os.environ.copy()` e adicione/sobrescreva. Senão "
                  "perde PATH, HOME, USER, etc.",
                  statement_en="When setting env= on subprocess, which common mistake occurs?",
                  correct_en="Forgetting to copy os.environ — the child process has no PATH and essential variables.",
                  wrong_en=[
                            "It usually directly causes a segfault inside the created child process.",
                            "It usually specifically breaks the environment variable called HOME.",
                            "It makes it technically very hard to pass any custom environment variable.",
                        ],
                  explanation_en="Start with `env = os.environ.copy()` and add/override. Otherwise you lose PATH, HOME, USER, etc."),
                q("Para criar arquivo temporário que será removido automaticamente:",
                  "with tempfile.NamedTemporaryFile() as f: ... (delete=True default)",
                  ["open('/tmp/' + str(uuid4()), 'w') sem cleanup automático depois", "tempfile.mktemp() (deprecado, com race condition conhecida há anos)", "shutil.create_temp() (função que não existe no módulo shutil)"],
                  "NamedTemporaryFile remove ao sair do `with` (delete=True default). "
                  "mktemp é race-condition vulnerable.",
                  statement_en="To create a temporary file that will be removed automatically:",
                  correct_en="with tempfile.NamedTemporaryFile() as f: ... (delete=True by default)",
                  wrong_en=[
                            "open('/tmp/' + str(uuid4()), 'w') with no automatic cleanup afterward",
                            "tempfile.mktemp() (deprecated, with a known race condition for years)",
                            "shutil.create_temp() (a function that doesn't exist in shutil)",
                        ],
                  explanation_en="NamedTemporaryFile removes the file on leaving `with` (delete=True default). mktemp is race-condition vulnerable."),
                q("`shutil.move(src, dst)` em FS diferentes...",
                  "Cai para copiar+remover (não é atômico).",
                  ["Continua sendo uma operação atômica, independente do filesystem.", "Usa internamente um pipe para transferir os bytes do arquivo.", "Acaba falhando na maioria dos casos quando os filesystems são diferentes."],
                  "Em FS diferentes, copia e depois remove. Atômico só dentro do mesmo "
                  "FS via rename(2).",
                  statement_en="`shutil.move(src, dst)` across different filesystems...",
                  correct_en="Falls back to copy+remove (not atomic).",
                  wrong_en=[
                            "Remains an atomic operation regardless of filesystem.",
                            "Internally uses a pipe to transfer the file bytes.",
                            "Ends up failing in most cases when the filesystems differ.",
                        ],
                  explanation_en="On different filesystems it copies then removes. Atomic only within the same FS via rename(2)."),
                q("Para localizar um binário no PATH:",
                  "shutil.which('kubectl')",
                  ["Path.find('kubectl', True)", "os.locate('kubectl', True)", "which.find('kubectl', True)"],
                  "shutil.which retorna o caminho absoluto ou None. Útil pra checar "
                  "dependências antes de chamar.",
                  statement_en="To locate a binary on PATH:",
                  correct_en="shutil.which('kubectl')",
                  wrong_en=[
                            "Path.find('kubectl', True)",
                            "os.locate('kubectl', True)",
                            "which.find('kubectl', True)",
                        ],
                  explanation_en="shutil.which returns the absolute path or None. Useful to check dependencies before calling them."),
                q("`signal.signal(SIGTERM, handler)` é útil para...",
                  "Interceptar pedido de parada e fazer cleanup gracioso (fechar arquivos, drenar fila).",
                  ["Aumentar manualmente a prioridade de agendamento desse processo no sistema, erro que só é percebido quando o time de operação já está lidando com o incidente.", "Forçar o reboot completo da máquina onde esse processo está rodando, decisão que parece inofensiva isolada, mas se acumula com o tempo.", "Detectar de forma automática erros de lógica dentro do próprio código do programa, comportamento que só é notado quando alguém audita os logs depois."],
                  "Workers/daemons precisam disso para shutdown limpo. SIGKILL não pode "
                  "ser interceptado, só SIGTERM/SIGINT.",
                  statement_en="`signal.signal(SIGTERM, handler)` is useful to...",
                  correct_en="Intercept a stop request and do graceful cleanup (close files, drain queue).",
                  wrong_en=[
                            "Manually raise this process's scheduling priority on the system — an error only noticed when ops is already handling the incident.",
                            "Force a full reboot of the machine where this process is running — a decision that seems harmless alone but accumulates over time.",
                            "Automatically detect logic errors inside the program's own code — behavior only noticed when someone audits the logs later.",
                        ],
                  explanation_en="Workers/daemons need this for clean shutdown. SIGKILL cannot be intercepted, only SIGTERM/SIGINT."),
                q("Para escapar uma string que VAI para shell=True com segurança:",
                  "shlex.quote(s)",
                  ["s.replace(\"'\", \"\\\\'\")",
                   "f\"'{s}'\" (aspas simples)",
                   "Não há forma segura."],
                  "shlex.quote escapa corretamente em todos os casos. Concatenação "
                  "manual sempre tem casos extremos.",
                  statement_en="To safely escape a string that WILL go into shell=True:",
                  correct_en="shlex.quote(s)",
                  wrong_en=["s.replace(\"'\", \"\\\\'\")", "f\"'{s}'\" (single quotes)", "There is no safe way."],
                  explanation_en="shlex.quote escapes correctly in all cases. Manual concatenation always has edge cases."),
            ],
        },
        # =====================================================================
        # 6.7 Concorrência: threads, async, multiprocessing
        # =====================================================================
        {
            "title": "Concorrência: threads, asyncio e multiprocessing",
            "title_en": "Concurrency: Threads, asyncio and Multiprocessing",
            "summary": "GIL, quando usar cada modelo, async/await na prática e armadilhas comuns.",
            "summary_en": "The GIL, when to use each model, async/await in practice and common pitfalls.",
            "lesson": {
                "intro": (
                    "Python tem três modelos de concorrência, e a escolha errada faz "
                    "código <em>mais lento</em> que o serial. Esta aula explica o GIL, "
                    "quando threads ajudam, quando você precisa de processos e por que "
                    "<code>asyncio</code> tomou o mundo de I/O em rede."
                ),
                "intro_en": (
                    "Python has three concurrency models, and the wrong choice makes code "
                    "<em>slower</em> than serial. This lesson explains the GIL, when threads "
                    "help, when you need processes, and why <code>asyncio</code> took over "
                    "the world of network I/O."
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Criar tasks com create_task / gather</p></div>
    <div class="lesson-viz-step"><span>2</span><p>await nos pontos de I/O</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Não bloquear a event loop com CPU sync</p></div>
  </div>
  <figcaption>asyncio: uma thread, vários awaits — o trabalho avança enquanto espera I/O.</figcaption>
</figure>
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>I/O paralelo</strong><p>threads ou asyncio — muitas esperas, pouco CPU Python.</p></div>
    <div class="lesson-viz-card"><strong>CPU paralelo</strong><p>multiprocessing — contorna o GIL com processos separados.</p></div>
  </div>
  <figcaption>Escolha pelo gargalo: espera de rede ≠ cálculo pesado.</figcaption>
</figure>
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
                "body_en": (
                """<h3>1. The GIL: a lock that explains why "more threads" sometimes doesn't help at all</h3>
<p>The Global Interpreter Lock ensures only one thread executes Python bytecode
at a time, even on a multi-core machine. For CPU-bound work in pure Python
(heavy parsing, encryption in Python, numerical loops), threads don't
parallelize — they take turns. For I/O-bound work (network, disk, waiting on
a subprocess), the GIL is released during the wait, so threads do help: while
one waits for the network, another runs.</p>
<div class="mermaid">
flowchart TD
    subgraph Threads ["threading, with GIL"]
        T1["Thread 1"] --> GIL["Only one runs Python bytecode at a time"]
        T2["Thread 2"] --> GIL
    end
    subgraph Multi ["multiprocessing"]
        P1["Process 1, own interpreter"]
        P2["Process 2, own interpreter"]
    end
</div>
<p><code>ThreadPoolExecutor</code> hides the boilerplate of creating/joining
threads and collecting results. The <code>max_workers</code> default is usually
fine for I/O; for many short HTTP calls, 20–40 workers is a common sweet spot.
Avoid sharing mutable state between workers without a <code>Lock</code> or
<code>queue.Queue</code> — race conditions are subtle and intermittent.</p>

<h3>2. Threads for I/O: the simple case that solves 80% of scripts</h3>
<pre><code>from concurrent.futures import ThreadPoolExecutor

def fetch(url: str) -&gt; tuple[str, int]:
    r = requests.get(url, timeout=10)
    return url, r.status_code

with ThreadPoolExecutor(max_workers=20) as pool:
    for url, status in pool.map(fetch, urls):
        print(url, status)</code></pre>
<p>Most DevOps scripts that "need parallelism" are really waiting on the
network: hitting 50 APIs, checking 200 hosts, pulling many S3 objects.
<code>concurrent.futures.ThreadPoolExecutor</code> plus a sync HTTP client
is often the simplest correct answer — no event loop, no async migration of
every library you touch.</p>

<h3>3. `asyncio`: a single thread, switching at explicit wait points</h3>
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
<p><code>async</code>/<code>await</code> cooperatively multiplexes many
tasks on one thread. The catch: any blocking call (<code>time.sleep</code>,
sync <code>requests.get</code>, heavy CPU) freezes the whole loop. Use
<code>await asyncio.sleep</code>, async clients (<code>httpx</code>,
<code>aiohttp</code>), or <code>asyncio.to_thread</code> for unavoidable sync
work.</p>

<h3>4. Essential `asyncio` patterns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Create tasks with create_task / gather</p></div>
    <div class="lesson-viz-step"><span>2</span><p>await at I/O points</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Do not block the event loop with sync CPU work</p></div>
  </div>
  <figcaption>asyncio: one thread, many awaits — work progresses while waiting on I/O.</figcaption>
</figure>
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
<p><code>asyncio.gather</code> fans out tasks; <code>return_exceptions=True</code>
collects failures instead of cancelling siblings. <code>Semaphore</code> caps
concurrency (e.g. 20 open connections). <code>TaskGroup</code> (3.11+) gives
structured concurrency: one failure cancels the group and aggregates errors in
an <code>ExceptionGroup</code>.</p>

<h3>5. Mixing sync and async: where the freeze happens</h3>
<pre><code>import asyncio

def cpu_bound(n: int) -&gt; int:
    return sum(range(n))

async def main():
    r = await asyncio.to_thread(cpu_bound, 10**7)
    print(r)</code></pre>
<p>The classic trap is calling sync I/O inside a coroutine. The event loop
stops scheduling other tasks until that call returns. Bridge with
<code>asyncio.to_thread(fn, *args)</code> or run a dedicated executor. Conversely,
don't call <code>asyncio.run</code> from inside an already-running loop.</p>

<h3>6. `multiprocessing`: bypassing the GIL with processes, not threads</h3>
<pre><code>from concurrent.futures import ProcessPoolExecutor

def hash_file(path: str) -&gt; tuple[str, str]:
    import hashlib
    h = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return path, h

with ProcessPoolExecutor() as pool:
    for p, sha in pool.map(hash_file, files):
        print(p, sha)</code></pre>
<p>Separate processes each have their own interpreter and GIL, so CPU-bound
pure Python can use multiple cores. Cost: pickling arguments/results across
process boundaries, higher memory, and on Windows the
<code>if __name__ == "__main__":</code> guard is mandatory with spawn.</p>

<h3>7. Synchronization: why a "simple operation" still needs a Lock</h3>
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
<p><code>count += 1</code> is not atomic: read-modify-write can interleave
between threads. Prefer <code>queue.Queue</code>, <code>threading.Lock</code>,
or immutable message passing. In asyncio, prefer single-threaded design; if you
must share, use <code>asyncio.Lock</code>.</p>

<h3>8. The four traps that catch everyone at least once</h3>
<ul>
<li>Using threads for CPU-bound pure Python and expecting speedup.</li>
<li>Calling <code>time.sleep</code> / sync I/O inside async code.</li>
<li>Forgetting <code>if __name__ == "__main__":</code> with multiprocessing on Windows.</li>
<li>Sharing mutable state across threads without synchronization.</li>
</ul>

<h3>9. Quick guide: which model for which problem</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Parallel I/O</strong><p>threads or asyncio — many waits, little Python CPU.</p></div>
    <div class="lesson-viz-card"><strong>Parallel CPU</strong><p>multiprocessing — bypasses the GIL with separate processes.</p></div>
  </div>
  <figcaption>Choose by bottleneck: network wait ≠ heavy compute.</figcaption>
</figure>
<table>
<thead><tr><th>Problem</th><th>Prefer</th></tr></thead>
<tbody>
<tr><td>Many network/disk waits</td><td>ThreadPoolExecutor or asyncio</td></tr>
<tr><td>CPU-bound pure Python</td><td>ProcessPoolExecutor</td></tr>
<tr><td>Already-async stack (httpx, FastAPI)</td><td>asyncio + Semaphore</td></tr>
<tr><td>Simple script, few calls</td><td>Sequential — concurrency has cost</td></tr>
</tbody></table>
"""
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
                "practical_en": (
                    "Implement <code>healthcheck.py</code> that takes a list of URLs via CLI "
                    "and checks them all in parallel, with at most 20 simultaneous "
                    "connections. Make two versions: (1) with <code>ThreadPoolExecutor + "
                    "requests</code>; (2) with <code>asyncio + httpx + Semaphore(20)</code>. "
                    "Compare total time for 200 URLs. Handle timeouts (5s per URL) and print "
                    "a summary on stderr (OK / FAIL counts) and details as JSON on stdout."
                ),
            },
            "materials": [
                m("Python docs, asyncio",
                  "https://docs.python.org/3/library/asyncio.html",
                  "docs", "Referência oficial de asyncio.",
                  title_en="Python docs, asyncio",
                  description_en="Official asyncio documentation."),
                m("Python docs, concurrent.futures",
                  "https://docs.python.org/3/library/concurrent.futures.html",
                  "docs", "Pool de threads e processos com API uniforme.",
                  title_en="Python docs, concurrent.futures",
                  description_en="Thread and process pools."),
                m("Real Python, async IO",
                  "https://realpython.com/async-io-python/",
                  "article", "Tutorial completo de asyncio.",
                  title_en="Real Python, async IO",
                  description_en="Async IO tutorial."),
                m("David Beazley, Understanding the Python GIL",
                  "https://www.dabeaz.com/python/UnderstandingGIL.pdf",
                  "article", "Análise clássica do GIL.",
                  title_en="David Beazley, Understanding the Python GIL",
                  description_en="Deep dive into the GIL."),
                m("Łukasz Langa, Async Python is not Faster",
                  "https://calpaterson.com/async-python-is-not-faster.html",
                  "article", "Mitos e fatos sobre async em Python.",
                  title_en="Łukasz Langa, Async Python is not Faster",
                  description_en="When async does and doesn't help."),
                m("PEP 703, Making the GIL Optional",
                  "https://peps.python.org/pep-0703/",
                  "docs", "Free-threading no Python 3.13+.",
                  title_en="PEP 703, Making the GIL Optional",
                  description_en="Free-threaded Python."),
            ],
            "questions": [
                q("Para 100 chamadas HTTP em paralelo num script, a escolha mais simples é:",
                  "ThreadPoolExecutor com requests.",
                  ["multiprocessing.Pool",
                   "Threading manual com Lock global",
                   "Subprocess de curl"],
                  "I/O-bound: threads ajudam (GIL libera durante I/O). Pool simplifica. "
                  "Multiprocessing seria caro pelo overhead de pickle.",
                  statement_en="For 100 parallel HTTP calls in a script, the simplest choice is:",
                  correct_en="ThreadPoolExecutor with requests.",
                  wrong_en=[
                            "multiprocessing.Pool",
                            "Manual threading with a global Lock",
                            "A curl subprocess",
                        ],
                  explanation_en="I/O-bound: threads help (GIL is released during I/O). Pool simplifies things. Multiprocessing would be costly due to pickle overhead."),
                q("O GIL impede que threads ajudem em qual cenário?",
                  "Cálculos CPU-bound em Python puro.",
                  ["A leitura de um arquivo grande feita em disco.", "Esperar a contagem de um timer chegar ao fim.", "Fazer chamadas de rede via HTTP para outro serviço."],
                  "GIL serializa execução de bytecode. Para CPU-bound, use "
                  "multiprocessing ou libs C que liberam o GIL.",
                  statement_en="The GIL prevents threads from helping in which scenario?",
                  correct_en="CPU-bound computations in pure Python.",
                  wrong_en=[
                            "Reading a large file from disk.",
                            "Waiting for a timer countdown to finish.",
                            "Making HTTP network calls to another service.",
                        ],
                  explanation_en="The GIL serializes bytecode execution. For CPU-bound work, use multiprocessing or C libs that release the GIL."),
                q("Em asyncio, o que acontece se você chamar `time.sleep(5)` dentro de async?",
                  "Bloqueia todo o event loop por 5s, todas as outras tarefas pausam.",
                  ["Continua rodando em paralelo automaticamente, sem travar muito pouco.", "É tecnicamente equivalente a chamar `await asyncio.sleep(5)`.", "Lança uma exceção chamada `AsyncError`, que não existe."],
                  "time.sleep é síncrono. Em async use `await asyncio.sleep`. "
                  "Bloqueio acidental é a armadilha número 1.",
                  statement_en="In asyncio, what happens if you call `time.sleep(5)` inside async code?",
                  correct_en="It blocks the entire event loop for 5s; all other tasks pause.",
                  wrong_en=[
                            "It keeps running in parallel automatically, without really freezing much.",
                            "It's technically equivalent to calling `await asyncio.sleep(5)`.",
                            "It raises an `AsyncError` exception, which doesn't exist.",
                        ],
                  explanation_en="time.sleep is synchronous. In async use `await asyncio.sleep`. Accidental blocking is trap number one."),
                q("`asyncio.gather(*tasks)` com return_exceptions=False...",
                  "Cancela as outras tarefas se uma falhar.",
                  ["Espera todas terminarem mesmo com erros.",
                   "Não usa o event loop.",
                   "Só funciona em 3.12+."],
                  "Quando uma falha, gather propaga a exceção. Para coletar todas, "
                  "use return_exceptions=True (cada item pode ser exceção).",
                  statement_en="`asyncio.gather(*tasks)` with return_exceptions=False...",
                  correct_en="Cancels the other tasks if one fails.",
                  wrong_en=[
                            "Waits for all to finish even with errors.",
                            "Doesn't use the event loop.",
                            "Only works in 3.12+.",
                        ],
                  explanation_en="When one fails, gather propagates the exception. To collect all, use return_exceptions=True (each item may be an exception)."),
                q("Para limitar a 10 conexões simultâneas em asyncio:",
                  "asyncio.Semaphore(10) com `async with sem:` ao redor da chamada.",
                  ["Escrever um loop manual controlando um contador junto de um `sleep`.", "Limitar diretamente o número de threads criadas pelo processo principal.", "Não existe alguma forma direta de limitar esse tipo de concorrência em asyncio."],
                  "Semaphore é o mecanismo padrão. Cada acquire decrementa, release "
                  "incrementa; bloqueia quando zerado.",
                  statement_en="To limit to 10 simultaneous connections in asyncio:",
                  correct_en="asyncio.Semaphore(10) with `async with sem:` around the call.",
                  wrong_en=[
                            "Write a manual loop controlling a counter plus a `sleep`.",
                            "Directly limit the number of threads created by the main process.",
                            "There is no direct way to limit this kind of concurrency in asyncio.",
                        ],
                  explanation_en="Semaphore is the standard mechanism. Each acquire decrements, release increments; it blocks when zero."),
                q("`asyncio.to_thread(fn, *args)` é útil para...",
                  "Rodar função síncrona bloqueante sem congelar o event loop.",
                  ["Substituir por completo a necessidade de usar `asyncio.gather`.", "Aumentar de alguma forma a força do GIL do interpretador.", "Lançar uma exceção manualmente dentro de outra thread."],
                  "Move a chamada para um pool de threads, retorna corrotina que "
                  "espera o resultado. Ideal para integrar libs sync em async.",
                  statement_en="`asyncio.to_thread(fn, *args)` is useful to...",
                  correct_en="Run a blocking synchronous function without freezing the event loop.",
                  wrong_en=[
                            "Completely replace the need to use `asyncio.gather` in every case.",
                            "Somehow strengthen the interpreter's GIL across all threads.",
                            "Manually raise an exception from inside another OS thread.",
                        ],
                  explanation_en="Moves the call to a thread pool and returns a coroutine that waits for the result. Ideal for integrating sync libs into async."),
                q("Race condition em threads acontece tipicamente quando:",
                  "Duas threads modificam estado compartilhado sem sincronização.",
                  ["O código importa uma quantidade grande demais de módulos diferentes.", "O processador da máquina onde o código roda tem várias cores disponíveis.", "O interpretador Python é considerado lento demais nesse tipo de cenário."],
                  "Operações compostas (count += 1) não são atômicas. Use Lock, "
                  "Queue ou estruturas thread-safe.",
                  statement_en="A race condition in threads typically happens when:",
                  correct_en="Two threads modify shared state without synchronization.",
                  wrong_en=[
                            "The code imports far too many different modules.",
                            "The machine's processor where the code runs has several cores available.",
                            "The Python interpreter is considered too slow for this kind of scenario.",
                        ],
                  explanation_en="Compound operations (count += 1) aren't atomic. Use Lock, Queue, or thread-safe structures."),
                q("Para CPU-bound em Python puro, use:",
                  "ProcessPoolExecutor (multiprocessing).",
                  ["Usar `ThreadPoolExecutor`, que ainda compartilha o mesmo GIL.", "Usar `asyncio` combinado com `gather` para paralelizar.", "Criar instâncias de `concurrent.futures.Future` diretamente."],
                  "Processos contornam o GIL, usam todos os cores. Custo: serialização "
                  "via pickle entre processos.",
                  statement_en="For CPU-bound work in pure Python, use:",
                  correct_en="ProcessPoolExecutor (multiprocessing).",
                  wrong_en=[
                            "Use `ThreadPoolExecutor`, which still shares the same GIL.",
                            "Use `asyncio` combined with `gather` to parallelize.",
                            "Create `concurrent.futures.Future` instances directly.",
                        ],
                  explanation_en="Processes bypass the GIL and use all cores. Cost: pickle serialization between processes."),
                q("Em multiprocessing no Windows, o código que dispara workers DEVE estar dentro de:",
                  "if __name__ == '__main__':",
                  ["try/except ao redor do disparo dos workers", "with usado como context manager qualquer", "async def no lugar de uma função comum"],
                  "Windows usa 'spawn' que re-executa o módulo no filho. Sem o guard, "
                  "o filho dispara workers de novo → fork bomb.",
                  statement_en="In multiprocessing on Windows, code that starts workers MUST be inside:",
                  correct_en="if __name__ == '__main__':",
                  wrong_en=[
                            "try/except around starting the workers",
                            "with used as some arbitrary context manager",
                            "async def instead of a regular function",
                        ],
                  explanation_en="Windows uses 'spawn', which re-executes the module in the child. Without the guard, the child starts workers again → fork bomb."),
                q("`asyncio.TaskGroup` (3.11+) tem qual vantagem sobre gather?",
                  "Cancelamento estruturado: se uma falhar, as outras são canceladas e erros vêm em ExceptionGroup.",
                  ["É consideravelmente mais rápido de executar na prática do que o próprio gather, suposição incorreta sobre como o sistema realmente se comporta sob estresse.", "Funciona rodando diretamente dentro de threads separadas do sistema operacional, suposição que raramente se sustenta fora do ambiente controlado de laboratório.", "Substitui por completo a necessidade de usar um Semaphore em qualquer cenário, que só aparece como problema depois que o sistema já está em produção."],
                  "TaskGroup implementa structured concurrency, escopo explícito, "
                  "cleanup automático, erros agregados.",
                  statement_en="What advantage does `asyncio.TaskGroup` (3.11+) have over gather?",
                  correct_en="Structured cancellation: if one fails, others are cancelled and errors come in an ExceptionGroup.",
                  wrong_en=[
                            "It's considerably faster to run in practice than gather itself — an incorrect assumption about how the system really behaves under stress.",
                            "It works by running directly inside separate OS threads — an assumption that rarely holds outside a controlled lab environment.",
                            "It completely replaces the need to use a Semaphore in any scenario — which only shows up as a problem once the system is already in production.",
                        ],
                  explanation_en="TaskGroup implements structured concurrency: explicit scope, automatic cleanup, aggregated errors."),
            ],
        },
        # =====================================================================
        # 6.8 Testes
        # =====================================================================
        {
            "title": "Testes com pytest, mocks e cobertura",
            "title_en": "Testing with pytest, Mocks and Coverage",
            "summary": "Pytest essencial, fixtures, parametrize, mocks de I/O e métricas de cobertura.",
            "summary_en": "Essential pytest, fixtures, parametrize, I/O mocks and coverage metrics.",
            "lesson": {
                "intro": (
                    "Testes automatizados não são opcionais em código que vai pra "
                    "produção. Em DevOps são especialmente críticos: um script de "
                    "deploy errado derruba ambientes; um pipeline sem teste nas "
                    "ferramentas custa downtime real. Esta aula é um curso intensivo "
                    "de pytest, a ferramenta de teste do ecossistema Python."
                ),
                "intro_en": (
                    "Automated tests aren't optional for code that goes to production. In "
                    "DevOps they're especially critical: a wrong deploy script takes "
                    "environments down; a pipeline without tests on its tools costs real "
                    "downtime. This lesson is an intensive course on pytest, the testing "
                    "tool of the Python ecosystem."
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Identificar dependência externa</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Patch no local de uso, não na definição</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Assertar chamada e resultado</p></div>
  </div>
  <figcaption>Mock bem feito: isola I/O sem mentir sobre o que o código realmente chama.</figcaption>
</figure>
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
<div class="mermaid">
flowchart TD
    E2E["Poucos e2e: lentos, frágeis"] --> Int["Alguns integração"]
    Int --> Unit["Muitos unitários: rápidos e baratos"]
</div>
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
                "body_en": (
                """<h3>1. Why pytest and not unittest</h3>
<p>pytest cuts boilerplate: plain <code>assert</code> instead of
<code>self.assertEqual</code>, composable fixtures instead of class hierarchies,
and a plugin ecosystem (cov, asyncio, mock, xdist). unittest still works, but
modern Python projects standardize on pytest.</p>
<div class="mermaid">
flowchart LR
    A["Write the test"] --> B["Run pytest"]
    B --> C{"Passed?"}
    C -- "No, red" --> D["Fix the code"]
    D --> B
    C -- "Yes, green" --> E["Move to the next case"]
</div>
<p>Discovery is convention-based: files named <code>test_*.py</code> or
<code>*_test.py</code>, functions/classes prefixed with <code>test</code>.
Run <code>pytest</code> from the project root; it finds tests without you listing
them. Use <code>-k</code> to select by name and <code>-m</code> to select by marks.</p>

<h3>2. Test discovery: how pytest finds you</h3>
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
<p>Fixtures inject dependencies into tests by parameter name. A fixture can
create a temp directory, a fake HTTP client, or a DB connection, and tear it
down afterward. Scope (<code>function</code>, <code>module</code>, <code>session</code>)
controls how often setup runs. Shared fixtures live in <code>conftest.py</code>.</p>

<h3>3. Fixtures: dependency injection, not decoration</h3>
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
<p><code>@pytest.mark.parametrize</code> turns a table of inputs into separate
test cases with clear failure names. Prefer parametrize over a manual for-loop
inside one test — you get per-case reporting and selective reruns.</p>

<h3>4. Parametrize: a table of cases, not a loop</h3>
<pre><code>@pytest.mark.parametrize("input,expected", [
    ("web",       ("web", "latest")),
    ("web:1.2",   ("web", "1.2")),
    ("r/r:tag",   ("r/r", "tag")),
    ("",          ("", "latest")),
])
def test_parse(input, expected):
    assert parse_image(input) == expected</code></pre>
<p>Mocks isolate external I/O: HTTP, disk, clocks, env vars. The common mistake
is mocking the system under test itself until the test only proves the mock
works. Mock at the boundary (the HTTP client, <code>open</code>, subprocess),
not deep internals. <code>monkeypatch</code> and <code>unittest.mock</code> /
<code>pytest-mock</code> cover most cases.</p>

<h3>5. Mocks: isolating what's outside the test — and the most common misuse</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Identify the external dependency</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Patch where it is used, not where it is defined</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Assert the call and the result</p></div>
  </div>
  <figcaption>Good mocks: isolate I/O without lying about what the code actually calls.</figcaption>
</figure>
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
<p><code>with pytest.raises(ValueError):</code> asserts an exception type.
Add <code>match=</code> for a regex on the message when the type alone is too
broad. Don't use a bare try/except that swallows and asserts manually — raises
is clearer when it fails.</p>

<h3>6. Testing exceptions: `pytest.raises` and the `match` pitfall</h3>
<pre><code>import pytest

def test_invalid_replicas():
    with pytest.raises(ValueError, match=r"replicas.*fora"):
        Replica(count=999)</code></pre>
<p>Marks categorize tests: <code>@pytest.mark.slow</code>, <code>integration</code>,
<code>unit</code>. CI can run <code>pytest -m "not slow"</code> on PRs and the full
suite on merge. Register custom marks in <code>pytest.ini</code> /
<code>pyproject.toml</code> to avoid warnings.</p>

<h3>7. Marks: organizing the suite by category</h3>
<pre><code>@pytest.mark.skipif(sys.platform == "win32", reason="só Linux")
def test_unix_socket(): ...

@pytest.mark.xfail(reason="bug conhecido #123")
def test_known_bug(): ...

@pytest.mark.slow
def test_full_pipeline(): ...
# rodar: pytest -m "not slow"</code></pre>
<p>Coverage measures which lines executed — not whether edge cases were thought
through. 100% coverage with weak asserts still ships bugs. Use
<code>pytest --cov</code> as a floor (often 80–90%), then add cases for
<code>None</code>, empty collections, and error paths.</p>

<h3>8. Coverage: what it measures, and what it doesn't</h3>
<pre><code># pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=app --cov-report=term --cov-report=html --cov-branch"

# rodar
pytest                     # tabela no terminal
open htmlcov/index.html    # report visual</code></pre>
<p>Install <code>pytest-asyncio</code> and mark async tests (or set
<code>asyncio_mode = auto</code>). Never call <code>asyncio.run</code> inside a
test if the plugin already provides a loop — nested loops fail confusingly.</p>

<h3>9. Async tests: the event loop nobody sees</h3>
<pre><code># pip install pytest-asyncio
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch("https://example.com")
    assert result.status == 200</code></pre>
<p>Unit tests are fast and isolated; integration tests hit real collaborators
(containers, localstack); e2e tests drive the full path. Inverting the pyramid
(mostly e2e) makes the suite slow and flaky. Prefer many unit tests, fewer
integration tests, and a thin e2e layer for critical flows.</p>

<h3>10. Unit, integration, e2e: the pyramid and why inverting it is expensive</h3>
<div class="mermaid">
flowchart TD
    E2E["Few e2e: slow, fragile"] --> Int["Some integration"]
    Int --> Unit["Many unit tests: fast and cheap"]
</div>
<p>In DevOps tooling, unit-test pure logic (parsing, policy decisions) and
integration-test subprocess/API boundaries with mocks or testcontainers. Keep
e2e for "does the CLI exit 0 on a happy path in CI".</p>
"""
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
                "practical_en": (
                    "For the <code>top_users.py</code> you wrote in lesson 6.2: (1) create "
                    "<code>tests/test_top_users.py</code>; (2) write an "
                    "<code>access_log</code> fixture using <code>tmp_path</code> that "
                    "generates a fake log with 50 lines and varied statuses; (3) parametrize "
                    "5 different cases (top 1, top 3, empty, all 200s, mixed); (4) ensure ≥ "
                    "90% coverage with <code>pytest --cov=top_users "
                    "--cov-fail-under=90</code>."
                ),
            },
            "materials": [
                m("pytest documentation",
                  "https://docs.pytest.org/",
                  "docs", "Documentação oficial.",
                  title_en="pytest documentation",
                  description_en="Official pytest docs."),
                m("Brian Okken, pytest book",
                  "https://pythontest.com/pytest-book/",
                  "book", "Livro de referência.",
                  title_en="Brian Okken, pytest book",
                  description_en="Python Testing with pytest."),
                m("Real Python, Effective Python Testing With Pytest",
                  "https://realpython.com/pytest-python-testing/",
                  "article", "Tutorial completo.",
                  title_en="Real Python, Effective Python Testing With Pytest",
                  description_en="Practical pytest guide."),
                m("coverage.py",
                  "https://coverage.readthedocs.io/",
                  "docs", "Cobertura de código.",
                  title_en="coverage.py",
                  description_en="Code coverage measurement."),
                m("pytest-mock",
                  "https://pytest-mock.readthedocs.io/",
                  "docs", "Plugin para mocks com fixture.",
                  title_en="pytest-mock",
                  description_en="Thin wrapper around unittest.mock."),
                m("testcontainers-python",
                  "https://testcontainers-python.readthedocs.io/",
                  "docs", "DB e serviços reais em containers para testes.",
                  title_en="testcontainers-python",
                  description_en="Real dependencies in Docker for tests."),
            ],
            "questions": [
                q("A vantagem principal do pytest sobre unittest é:",
                  "Sintaxe direta com `assert` e fixtures componíveis.",
                  ["Vem com uma quantidade maior de funções built-in prontas.", "Costuma rodar mais rápido especificamente em máquinas Linux.", "É a única ferramenta capaz de medir cobertura de código."],
                  "pytest reduz boilerplate. fixtures, parametrize e plugins são o "
                  "diferencial.",
                  statement_en="The main advantage of pytest over unittest is:",
                  correct_en="Direct syntax with `assert` and composable fixtures.",
                  wrong_en=[
                            "It comes with a larger number of ready-made built-in functions.",
                            "It tends to run faster specifically on Linux machines.",
                            "It's the only tool capable of measuring code coverage.",
                        ],
                  explanation_en="pytest reduces boilerplate. fixtures, parametrize and plugins are the differentiators."),
                q("`@pytest.mark.parametrize` é usado para:",
                  "Rodar o mesmo teste com múltiplos conjuntos de inputs.",
                  ["Configurar fixtures compartilhadas entre vários arquivos de teste.", "Marcar testes específicos como lentos para o CI.", "Pular a execução de testes específicos quando rodando em CI."],
                  "Cada linha do parametrize gera um caso de teste, com nome legível "
                  "indicando qual falhou.",
                  statement_en="`@pytest.mark.parametrize` is used to:",
                  correct_en="Run the same test with multiple sets of inputs.",
                  wrong_en=[
                            "Configure fixtures shared across several test files.",
                            "Mark specific tests as slow for CI.",
                            "Skip running specific tests when running in CI.",
                        ],
                  explanation_en="Each parametrize row generates a test case, with a readable name showing which one failed."),
                q("`tmp_path` em pytest é:",
                  "Uma fixture built-in que dá um diretório temporário único por teste.",
                  ["Um atributo de classe definido manualmente pelo próprio desenvolvedor do teste.", "Uma chamada de função do sistema operacional feita diretamente pelo pytest.", "Uma variável de ambiente lida de forma automática pelo próprio pytest."],
                  "Cleanup automático ao fim do teste. Evita TemporaryDirectory manual.",
                  statement_en="`tmp_path` in pytest is:",
                  correct_en="A built-in fixture that gives a unique temporary directory per test.",
                  wrong_en=[
                            "A class attribute defined manually by the test developer.",
                            "An operating-system function call made directly by pytest.",
                            "An environment variable read automatically by pytest itself.",
                        ],
                  explanation_en="Automatic cleanup at the end of the test. Avoids manual TemporaryDirectory."),
                q("Para verificar que uma função levanta uma exceção específica:",
                  "with pytest.raises(ValueError): ...",
                  ["assert raises(ValueError, fn) (função inexistente)", "try/except genérico ignorando o erro", "@pytest.expect(ValueError) (decorator inexistente)"],
                  "pytest.raises é o jeito idiomático. Aceita `match=` para checar "
                  "mensagem por regex.",
                  statement_en="To verify that a function raises a specific exception:",
                  correct_en="with pytest.raises(ValueError): ...",
                  wrong_en=[
                            "assert raises(ValueError, fn) (nonexistent function)",
                            "generic try/except ignoring the error",
                            "@pytest.expect(ValueError) (nonexistent decorator)",
                        ],
                  explanation_en="pytest.raises is the idiomatic way. It accepts `match=` to check the message by regex."),
                q("Por que mockar chamadas externas em testes unitários?",
                  "Para testes serem rápidos, determinísticos e independentes da rede.",
                  ["Evita que logs desnecessários apareçam durante a execução dos testes.", "Aumenta automaticamente a porcentagem de cobertura medida.", "É uma exigência técnica imposta diretamente pelo próprio pytest."],
                  "Testes unitários devem rodar offline e em milissegundos. Mocks "
                  "isolam o código sob teste.",
                  statement_en="Why mock external calls in unit tests?",
                  correct_en="So tests are fast, deterministic and network-independent.",
                  wrong_en=[
                            "It prevents unnecessary logs from appearing during test execution.",
                            "It automatically increases the measured coverage percentage.",
                            "It's a technical requirement imposed directly by pytest itself.",
                        ],
                  explanation_en="Unit tests should run offline and in milliseconds. Mocks isolate the code under test."),
                q("`monkeypatch.setenv('TOKEN', 'x')` em pytest:",
                  "Define a variável de ambiente apenas durante o teste; rollback automático.",
                  ["Modifica de forma permanente a variável de ambiente usada pelo sistema operacional.", "Grava um arquivo `.env` no disco durante a execução completa do teste.", "Só funciona corretamente quando os testes estão rodando em Linux."],
                  "monkeypatch desfaz tudo no teardown. Essencial para testar configs "
                  "via env.",
                  statement_en="`monkeypatch.setenv('TOKEN', 'x')` in pytest:",
                  correct_en="Sets the environment variable only during the test; automatic rollback.",
                  wrong_en=[
                            "Permanently modifies the environment variable used by the operating system.",
                            "Writes a `.env` file to disk during the full test run.",
                            "Only works correctly when tests are running on Linux.",
                        ],
                  explanation_en="monkeypatch undoes everything on teardown. Essential for testing env-based configs."),
                q("Cobertura de 100% garante código sem bugs?",
                  "Não, só garante que cada linha foi executada, não que os casos de borda foram cobertos.",
                  ["Sim, desde que o código em questão seja considerado puro, sem efeito colateral algum, algo que passa no code review quando ninguém olha com atenção.", "Só garante isso de fato a partir especificamente da versão 3.12 do Python, decisão que cria dívida técnica silenciosa, sem gerar erro imediato.", "Sim, cobertura de 100% garante que o código está livre de qualquer tipo de bug, erro típico de configuração feita às pressas, sem revisão posterior."],
                  "Cobertura é métrica de presença, não de qualidade. Casos de borda "
                  "(None, listas vazias, valores extremos) precisam ser explícitos.",
                  statement_en="Does 100% coverage guarantee bug-free code?",
                  correct_en="No — it only guarantees every line was executed, not that edge cases were covered.",
                  wrong_en=[
                            "Yes, as long as the code in question is considered pure, with no side effects at all — something that passes code review when nobody looks carefully.",
                            "It only actually guarantees that starting specifically with Python version 3.12 — a decision that creates silent technical debt without an immediate error.",
                            "Yes, 100% coverage guarantees the code is free of any kind of bug — a typical rushed-configuration error without later review.",
                        ],
                  explanation_en="Coverage is a presence metric, not a quality metric. Edge cases (None, empty lists, extreme values) still need to be exercised."),
                q("Para testar código async com pytest, instale:",
                  "pytest-asyncio e use @pytest.mark.asyncio",
                  ["asyncio-test (pacote que não existe no PyPI)", "unittest.AsyncTestCase (classe que não existe)", "Não há suporte a código async no pytest puro"],
                  "pytest-asyncio é o plugin padrão. Configure mode='auto' no "
                  "pyproject.toml para evitar mark em todo teste.",
                  statement_en="To test async code with pytest, install:",
                  correct_en="pytest-asyncio and use @pytest.mark.asyncio",
                  wrong_en=[
                            "asyncio-test (a package that doesn't exist on PyPI)",
                            "unittest.AsyncTestCase (a class that doesn't exist)",
                            "There is no support for async code in plain pytest",
                        ],
                  explanation_en="pytest-asyncio is the standard plugin. Configure mode='auto' in pyproject.toml to avoid marking every test."),
                q("Onde colocar fixtures que múltiplos arquivos de teste compartilham?",
                  "conftest.py no diretório de testes.",
                  ["Num arquivo `fixtures.py` importado manualmente em cada teste.", "Dentro de um plugin externo instalado separadamente via pip.", "Duplicada dentro de cada arquivo de teste individualmente."],
                  "conftest.py é detectado automaticamente. Útil para fixtures globais "
                  "(client HTTP fake, DB de teste, etc.).",
                  statement_en="Where should fixtures shared by multiple test files go?",
                  correct_en="conftest.py in the tests directory.",
                  wrong_en=[
                            "In a `fixtures.py` file imported manually in each test.",
                            "Inside an external plugin installed separately via pip.",
                            "Duplicated inside each individual test file.",
                        ],
                  explanation_en="conftest.py is detected automatically. Useful for global fixtures (fake HTTP client, test DB, etc.)."),
                q("`pytest -m \"not slow\"` faz o quê?",
                  "Roda apenas testes não marcados com @pytest.mark.slow.",
                  ["Roda os testes mais lentos primeiro, antes dos demais.", "Apenas define um nome customizado para a suíte de testes.", "Causa um erro de sintaxe assim que o pytest interpreta a expressão."],
                  "Marks permitem segmentar a suíte. Ideal para CI: rodar 'not slow' "
                  "no PR; tudo no merge.",
                  statement_en="What does `pytest -m \"not slow\"` do?",
                  correct_en="Runs only tests not marked with @pytest.mark.slow.",
                  wrong_en=[
                            "Runs the slowest tests first, before the others.",
                            "Only defines a custom name for the test suite.",
                            "Causes a syntax error as soon as pytest parses the expression.",
                        ],
                  explanation_en="Marks let you segment the suite. Ideal for CI: run 'not slow' on PRs; everything on merge."),
            ],
        },
        # =====================================================================
        # 6.9 Empacotamento e qualidade
        # =====================================================================
        {
            "title": "Empacotamento moderno e qualidade de código",
            "title_en": "Modern Packaging and Code Quality",
            "summary": "pyproject.toml, venv, pip, uv, ruff e mypy, o ferramental de um projeto Python profissional.",
            "summary_en": "pyproject.toml, venv, pip, uv, ruff and mypy — the tooling of a professional Python project.",
            "lesson": {
                "intro": (
                    "Um script .py funciona; um <em>projeto</em> Python tem ambiente "
                    "isolado, dependências travadas, formatador, linter, type checker e "
                    "build reprodutível. Esta aula mostra o stack moderno (2024-2026) e "
                    "como organizar um projeto novo do zero, não a versão de 2010 com "
                    "<code>setup.py</code>."
                ),
                "intro_en": (
                    "A .py script works; a Python <em>project</em> has an isolated "
                    "environment, locked dependencies, a formatter, a linter, a type checker "
                    "and a reproducible build. This lesson shows the modern stack "
                    "(2024-2026) and how to organize a new project from scratch — not the "
                    "2010 version with <code>setup.py</code>."
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
    Global["Python global do sistema"] --> Conflict["Deps conflitam entre projetos"]
    Venv["Ambiente virtual"] --> Isolated["Deps isoladas por projeto"]
    Isolated --> Repro["Reproduzível com lockfile"]
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Lint + format com ruff</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Tipos com mypy (gradual)</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Hooks no pre-commit e na CI</p></div>
  </div>
  <figcaption>Qualidade moderna: uma pipeline curta que o time consegue rodar localmente e no CI.</figcaption>
</figure>
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
<div class="mermaid">
flowchart LR
    Src["Código-fonte"] --> Pyproject["pyproject.toml"]
    Pyproject --> Build["uv build"]
    Build --> Wheel["wheel e sdist na pasta dist"]
    Wheel --> Publish["Publica no índice de pacotes"]
</div>
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
                "body_en": (
                """<h3>1. Virtual environments: why isolation is what prevents "works on my machine"</h3>
<pre><code>python -m venv .venv
source .venv/bin/activate         # Linux/Mac
.venv\\Scripts\\activate            # Windows
python -m pip install --upgrade pip
pip install requests pytest</code></pre>
<p>Installing packages into the system Python mixes project versions with OS
packages and other projects. A venv (or uv/poetry env) keeps dependencies
per project. Activate it before install/run; CI should create a fresh env every
job.</p>
<div class="mermaid">
flowchart LR
    Global["System-wide Python"] --> Conflict["Deps conflict across projects"]
    Venv["Virtual environment"] --> Isolated["Deps isolated per project"]
    Isolated --> Repro["Reproducible with a lockfile"]
</div>
<p><code>uv</code> resolves and installs dramatically faster than classic pip,
keeps a lockfile, and can manage Python versions. Day-to-day:
<code>uv init</code>, <code>uv add</code>, <code>uv sync</code>, <code>uv run</code>.</p>

<h3>2. `uv`: the same problem, solved without rewriting the resolver on every install</h3>
<pre><code>curl -LsSf https://astral.sh/uv/install.sh | sh

uv init meu-projeto && cd meu-projeto
uv add requests pydantic
uv add --dev pytest mypy ruff
uv run pytest                  # roda no env do projeto
uv lock                        # gera uv.lock determinístico
uv sync                        # restaura ambiente exato</code></pre>
<p><code>pyproject.toml</code> centralizes build metadata (PEP 621), dependencies,
and tool config (ruff, mypy, pytest). Prefer it over a scatter of
<code>setup.py</code>, <code>setup.cfg</code>, and ad-hoc ini files.</p>

<h3>3. `pyproject.toml`: one central file instead of three mismatched ones</h3>
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
<p>Putting the package under <code>src/</code> prevents tests from accidentally
importing the unfinished tree on <code>PYTHONPATH</code>. You install the project
editable (<code>uv sync</code> / <code>pip install -e .</code>) and test what you
will publish.</p>

<h3>4. `src/` layout: why one extra directory prevents an import bug</h3>
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
<p>ruff replaces a whole fleet (flake8, isort, pyupgrade, and can format like
black) in one Rust binary. Configure line length and rule sets in
<code>pyproject.toml</code>; run in CI and pre-commit.</p>

<h3>5. `ruff`: one Rust tool covering what used to be four in Python</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Lint + format with ruff</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Types with mypy (gradual)</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Hooks in pre-commit and CI</p></div>
  </div>
  <figcaption>Modern quality: a short pipeline the team can run locally and in CI.</figcaption>
</figure>
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
<p>mypy checks types without running code. <code>--strict</code> on a legacy
codebase explodes with errors — enable gradually per module. Type hints are a
contract for tools and readers, not a runtime guarantee.</p>

<h3>6. `mypy`: static type checking, and why starting `strict` stalls the team</h3>
<pre><code>mypy src/                   # checa types

# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true</code></pre>
<p><code>pre-commit install</code> hooks git so ruff/mypy/tests (as you configure)
run before a commit exists. That moves style debates out of PR review and keeps
main clean.</p>

<h3>7. Pre-commit hooks: moving the check to before the commit exists</h3>
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
<p>CI should repeat what developers run locally: sync deps, ruff, mypy, pytest.
Pin tool versions via the lockfile so "green locally, red in CI" is rare.</p>

<h3>8. Minimal CI: repeat remotely what will run locally</h3>
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
<p><code>uv build</code> produces wheel + sdist. Publish to PyPI or a private
index. Prefer wheels for install speed; keep sdist for source builds.</p>

<h3>9. Distribution: from a local wheel to a private registry</h3>
<div class="mermaid">
flowchart LR
    Src["Source code"] --> Pyproject["pyproject.toml"]
    Pyproject --> Build["uv build"]
    Build --> Wheel["wheel and sdist in dist/"]
    Wheel --> Publish["Publish to the package index"]
</div>
<pre><code>uv build                    # cria dist/*.whl e *.tar.gz
uv publish                  # publica no PyPI (requer token)

# para repositório privado (CodeArtifact, Artifactory, GCP AR)
uv publish --publish-url https://my-private/pypi/</code></pre>
<p>Recommended minimum stack (2026): uv for env/deps, src layout,
pyproject.toml, ruff + mypy, pytest, pre-commit, and a CI job that mirrors
local checks. That baseline scales from a personal CLI to a team-shared library.</p>

<h3>10. Summary: recommended minimum stack (2026)</h3>
<ul>
<li>uv + lockfile for reproducible installs</li>
<li>ruff for lint/format; mypy for types</li>
<li>pytest (+cov) for behavior</li>
<li>pre-commit + CI as the enforcement layer</li>
</ul>
"""
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
                "practical_en": (
                    "Create a new project with <code>uv init mytool</code> using the src "
                    "layout. Add: (1) dependencies <code>typer, requests</code>; (2) dev "
                    "deps <code>pytest, mypy, ruff</code>; (3) a <code>mytool</code> script "
                    "entrypoint; (4) configure ruff (line-length 100, rules E/F/I/B/UP) and "
                    "mypy strict in <code>pyproject.toml</code>; (5) a "
                    "<code>.pre-commit-config.yaml</code> running ruff and mypy; (6) make a "
                    "commit that deliberately breaks style and watch pre-commit block it."
                ),
            },
            "materials": [
                m("PEP 621, pyproject.toml metadata",
                  "https://peps.python.org/pep-0621/",
                  "docs", "Especificação oficial do pyproject.toml.",
                  title_en="PEP 621, pyproject.toml metadata",
                  description_en="Project metadata standard."),
                m("uv documentation",
                  "https://docs.astral.sh/uv/",
                  "docs", "Doc oficial do uv (Astral).",
                  title_en="uv documentation",
                  description_en="Fast Python package manager."),
                m("ruff documentation",
                  "https://docs.astral.sh/ruff/",
                  "docs", "Lint + format ultrarrápido.",
                  title_en="ruff documentation",
                  description_en="Extremely fast linter and formatter."),
                m("mypy, Type checking",
                  "https://mypy.readthedocs.io/",
                  "docs", "Verificador de tipos estático.",
                  title_en="mypy, Type checking",
                  description_en="Static type checker."),
                m("Hatch project",
                  "https://hatch.pypa.io/",
                  "docs", "Build backend moderno (hatchling).",
                  title_en="Hatch project",
                  description_en="Modern Python project manager."),
                m("pre-commit framework",
                  "https://pre-commit.com/",
                  "docs", "Hooks padronizados de Git.",
                  title_en="pre-commit framework",
                  description_en="Git hooks for code quality."),
            ],
            "questions": [
                q("Por que usar venv (ou similar) em vez de instalar deps globalmente?",
                  "Para isolar dependências por projeto e não afetar o Python do sistema.",
                  ["Reduz consideravelmente o uso de disco em comparação com instalar global.", "É uma convenção estética, sem diferença real de comportamento.", "Deixa a instalação de pacotes consideravelmente mais rápida."],
                  "Sem venv, projetos brigam por versões e você pode quebrar o pacote "
                  "do SO instalando lib global.",
                  statement_en="Why use venv (or similar) instead of installing deps globally?",
                  correct_en="To isolate dependencies per project and not affect the system Python.",
                  wrong_en=[
                            "It considerably reduces disk use compared with installing globally.",
                            "It's an aesthetic convention, with no real behavioral difference.",
                            "It makes package installation considerably faster.",
                        ],
                  explanation_en="Without venv, projects fight over versions and you can break an OS package by installing a lib globally."),
                q("O `pyproject.toml` substitui historicamente:",
                  "setup.py, setup.cfg e requirements.txt em muitos casos.",
                  ["Não substitui muito pouco de fato, funciona só como metadata extra.", "Substitui só o arquivo `requirements.txt` usado no projeto.", "Substitui só o `Makefile` usado para automatizar tarefas."],
                  "PEP 517/518/621 trouxeram pyproject.toml como arquivo de configuração "
                  "central de build, deps e ferramentas.",
                  statement_en="Historically, `pyproject.toml` replaces:",
                  correct_en="setup.py, setup.cfg and requirements.txt in many cases.",
                  wrong_en=[
                            "It doesn't really replace much; it only works as extra metadata.",
                            "It only replaces the project's `requirements.txt` file.",
                            "It only replaces the `Makefile` used to automate tasks.",
                        ],
                  explanation_en="PEP 517/518/621 made pyproject.toml the central config file for build, deps and tools."),
                q("`uv add requests` faz o quê?",
                  "Instala requests no ambiente do projeto e atualiza pyproject.toml/uv.lock.",
                  ["Instala o pacote de forma global no sistema, fora do ambiente do projeto atual.", "Cria um virtualenv inteiramente novo cada vez que o comando é chamado.", "Só baixa o tarball do pacote, sem de fato instalar coisa alguma."],
                  "Equivalente a `pip install requests + atualizar requirements`. "
                  "uv mantém lockfile determinístico.",
                  statement_en="What does `uv add requests` do?",
                  correct_en="Installs requests in the project environment and updates pyproject.toml/uv.lock.",
                  wrong_en=[
                            "Installs the package globally on the system, outside the current project environment.",
                            "Creates an entirely new virtualenv every time the command is called.",
                            "Only downloads the package tarball without actually installing anything.",
                        ],
                  explanation_en="Equivalent to `pip install requests + update requirements`. uv keeps a deterministic lockfile."),
                q("`ruff` substitui qual conjunto de ferramentas?",
                  "flake8, pylint, isort e black (lint + formatter).",
                  ["O framework de testes `pytest`, usado para rodar a suíte.", "Só o verificador de tipos estáticos `mypy`.", "As ferramentas de gestão de pacote `pip` e `venv`."],
                  "ruff é um único binário (Rust) que faz lint, ordenação de imports e "
                  "formatação. Não é type checker.",
                  statement_en="`ruff` replaces which set of tools?",
                  correct_en="flake8, pylint, isort and black (lint + formatter).",
                  wrong_en=[
                            "The `pytest` test framework used to run the suite.",
                            "Only the static type checker `mypy`.",
                            "The package-management tools `pip` and `venv`.",
                        ],
                  explanation_en="ruff is a single binary (Rust) that does linting, import sorting and formatting. It is not a type checker."),
                q("O 'src layout' (pacote em src/) tem qual vantagem prática?",
                  "Força instalar o pacote para testar, testes rodam no que será publicado.",
                  ["É uma exigência formal imposta diretamente pelo próprio índice oficial do PyPI.", "Deixa o `pip` consideravelmente mais rápido no momento de instalar o pacote.", "Permite manter múltiplos pacotes dentro de um mesmo repositório de código."],
                  "Sem src/, `import meu_pkg` pode pegar o código avulso do diretório "
                  "atual, não a versão instalada, bugs de empacotamento ficam ocultos.",
                  statement_en="What practical advantage does the 'src layout' (package under src/) have?",
                  correct_en="It forces installing the package to test; tests run against what will be published.",
                  wrong_en=[
                            "It's a formal requirement imposed directly by the official PyPI index.",
                            "It makes `pip` considerably faster when installing the package.",
                            "It lets you keep multiple packages inside the same code repository.",
                        ],
                  explanation_en="Without src/, `import my_pkg` can pick up loose code from the current directory, not the installed version — packaging bugs that only show up after publish."),
                q("`pre-commit install` configura o quê?",
                  "Hooks de Git que rodam linters/formatters antes de cada commit.",
                  ["É um apelido interno para `pip install -e .`, muito pouco mais.", "Instala o binário do pacote diretamente na pasta `/usr/bin`.", "Cria um novo virtualenv isolado dentro do projeto."],
                  "Os hooks impedem commit de código fora do padrão. Em time, "
                  "elimina discussão de estilo em PR.",
                  statement_en="What does `pre-commit install` configure?",
                  correct_en="Git hooks that run linters/formatters before each commit.",
                  wrong_en=[
                            "It's an internal alias for `pip install -e .`, little more than that.",
                            "It installs the package binary directly into `/usr/bin`.",
                            "It creates a new isolated virtualenv inside the project.",
                        ],
                  explanation_en="Hooks prevent committing code outside the standard. On a team, that eliminates style debates in PRs."),
                q("Para uma dependência usada apenas em desenvolvimento (ex: pytest), você usa:",
                  "[project.optional-dependencies] ou um grupo de dev no uv.",
                  ["Adicionar normalmente dentro da lista principal de `dependencies`.", "Instalar a dependência de forma global, direto no sistema.", "Compilar manualmente o pacote a partir do código-fonte."],
                  "Optional/dev deps não vão para o usuário final que instalar seu "
                  "pacote. Mantém o package final enxuto.",
                  statement_en="For a dependency used only in development (e.g. pytest), you use:",
                  correct_en="[project.optional-dependencies] or a uv dev group.",
                  wrong_en=[
                            "Adding it normally to the main `dependencies` list.",
                            "Installing the dependency globally, directly on the system.",
                            "Manually compiling the package from source.",
                        ],
                  explanation_en="Optional/dev deps don't go to the end user who installs your package. Keeps the final package lean."),
                q("`mypy --strict` em código legado costuma:",
                  "Gerar muitos erros de cara (type hints ausentes, Any implícito).",
                  ["Substituir por completo a necessidade de manter testes.", "Rodar de forma praticamente instantânea, sem apontar erro algum.", "Causar um segfault direto no processo do verificador de tipos."],
                  "Strict ativa todas as regras. Em legado, comece sem strict e "
                  "ative módulo por módulo.",
                  statement_en="`mypy --strict` on legacy code usually:",
                  correct_en="Produces many errors right away (missing type hints, implicit Any).",
                  wrong_en=[
                            "Completely replaces the need to keep tests.",
                            "Runs practically instantly without reporting any error.",
                            "Directly causes a segfault in the type-checker process.",
                        ],
                  explanation_en="Strict enables all rules. On legacy code, start without strict and enable it module by module."),
                q("`uv build` produz:",
                  "Um arquivo .whl (wheel) e um sdist .tar.gz na pasta dist/.",
                  ["Um `Dockerfile` pronto para buildar a imagem do projeto.", "Um binário já compilado diretamente na linguagem C.", "Só o tarball original do código-fonte, sem mais muito pouco."],
                  "Wheel é o formato binário moderno (rápido de instalar). sdist é o "
                  "código-fonte. Ambos vão para o PyPI.",
                  statement_en="`uv build` produces:",
                  correct_en="A .whl (wheel) file and an sdist .tar.gz in the dist/ folder.",
                  wrong_en=[
                            "A ready `Dockerfile` to build the project image.",
                            "A binary already compiled directly in the C language.",
                            "Only the original source-code tarball, little more than that.",
                        ],
                  explanation_en="Wheel is the modern binary format (fast to install). sdist is the source. Both go to PyPI."),
                q("Configuração centralizada no pyproject.toml ajuda a evitar:",
                  "Inconsistências entre dev e CI sobre versão de regras de lint, format e types.",
                  ["Conflitos de import entre módulos que compartilham o mesmo nome no projeto, decisão que funciona no papel, mas não sobrevive ao primeiro incidente real.", "Deadlocks que costumam acontecer só depois que o código já está em produção, prática que gera falso senso de segurança no time.", "Falhas relacionadas à resolução de nomes de DNS durante o pipeline de CI, atalho que troca segurança por conveniência de curto prazo."],
                  "Tudo em um único arquivo versionado: dev e CI usam exatamente as "
                  "mesmas regras.",
                  statement_en="Centralized config in pyproject.toml helps avoid:",
                  correct_en="Inconsistencies between dev and CI about lint, format and type-rule versions.",
                  wrong_en=[
                            "Import conflicts between modules that share the same name in the project — a decision that works on paper but doesn't survive the first real incident.",
                            "Deadlocks that usually happen only after the code is already in production — a practice that creates a false sense of security on the team.",
                            "Failures related to DNS name resolution during the CI pipeline — a shortcut that trades security for short-term convenience.",
                        ],
                  explanation_en="Everything in a single versioned file: dev and CI use exactly the same rules."),
            ],
        },
        # =====================================================================
        # 6.10 Python para DevSecOps na prática
        # =====================================================================
        {
            "title": "Python para DevSecOps na prática",
            "title_en": "Python for DevSecOps in Practice",
            "summary": "Automação de AWS (boto3), Kubernetes (kubernetes-client), métricas Prometheus e CI customizado.",
            "summary_en": "AWS automation (boto3), Kubernetes (kubernetes-client), Prometheus metrics and custom CI.",
            "lesson": {
                "intro": (
                    "Esta aula final amarra tudo: usando o Python que você aprendeu, "
                    "vamos ver como interagir com AWS, com a API do Kubernetes, expor "
                    "métricas Prometheus de uma ferramenta interna e construir um job "
                    "customizado de CI. São os casos que mais aparecem em times de "
                    "DevSecOps reais."
                ),
                "intro_en": (
                    "This final lesson ties it all together: using the Python you learned, "
                    "we'll see how to interact with AWS, with the Kubernetes API, expose "
                    "Prometheus metrics from an internal tool, and build a custom CI job. "
                    "These are the cases that show up most in real DevSecOps teams."
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
<div class="mermaid">
flowchart LR
    App["App Python"] --> Metrics["Counter / Histogram"]
    Metrics --> Expo["/metrics"]
    Expo --> Prom["Prometheus scrape"]
    Prom --> Alert["Alertas e dashboards"]
</div>
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
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Saída JSON para máquina, texto para humano</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Credenciais só via IAM/env — nunca no código</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Timeout, retries e códigos de saída explícitos</p></div>
  </div>
  <figcaption>Ferramenta que outros vão operar: previsível, auditável e sem segredo embutido.</figcaption>
</figure>
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
                "body_en": (
                """<h3>1. AWS with `boto3`: identity, pagination and credentials that never live in code</h3>
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
<p>On EC2/ECS/Lambda, prefer IAM roles — the SDK fetches credentials from the
instance/task metadata service. Locally, use profiles or short-lived SSO tokens.
Never hardcode access keys. List APIs are paginated: use
<code>get_paginator(...).paginate(...)</code> so you don't silently process only
the first page.</p>
<div class="mermaid">
flowchart LR
    EC2["EC2 instance"] --> Role["Attached IAM Role"]
    Role --> IMDS["Credentials via IMDS"]
    IMDS --> SDK["boto3 uses them automatically"]
</div>
<p>The official client can load in-cluster config when running inside the
cluster, or <code>kube_config</code> when running on a laptop. Try in-cluster
first and fall back — one tool, two environments.</p>

<h3>2. Kubernetes with the official client: one tool, two environments</h3>
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
<p>Watch streams events from the API server instead of polling every N seconds.
That reacts faster and wastes less quota. Always handle disconnects/reconnects
in long-running controllers.</p>

<h3>3. Watch: react to events instead of asking in a loop</h3>
<pre><code>from kubernetes import watch

w = watch.Watch()
for event in w.stream(v1.list_namespaced_pod, namespace="prod", timeout_seconds=0):
    pod = event["object"]
    if event["type"] in ("ADDED", "MODIFIED") and pod.status.phase == "Failed":
        notify_slack(f"Pod {pod.metadata.name} falhou")</code></pre>
<p>Instrument long-lived services with <code>prometheus_client</code>: counters,
histograms, gauges, and an HTTP <code>/metrics</code> endpoint for scraping.</p>

<h3>4. Prometheus metrics: instrumenting a service that stays up</h3>
<div class="mermaid">
flowchart LR
    App["Python app"] --> Metrics["Counter / Histogram"]
    Metrics --> Expo["/metrics"]
    Expo --> Prom["Prometheus scrape"]
    Prom --> Alert["Alerts and dashboards"]
</div>
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
<p>Batch jobs die before Prometheus scrapes them. Push metrics to Pushgateway
at the end of the job so the last run remains visible.</p>

<h3>5. Pushgateway: metrics from a job that's already dead when someone looks</h3>
<pre><code>from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

reg = CollectorRegistry()
g = Gauge("backup_last_success_unix", "Timestamp do último backup", registry=reg)
g.set_to_current_time()
push_to_gateway("pushgateway:9091", job="daily_backup", registry=reg)</code></pre>
<p>A custom CI gate can fail the pipeline before merge: license policy, image
tag denylist, required labels. Emit GitHub Actions annotations
(<code>::error::</code>) and non-zero exit codes so the UI surfaces the failure.</p>

<h3>6. Custom CI: a gate that blocks a forbidden license before merge</h3>
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
<p>Silent failure is worse than a loud one. Notify Slack/Teams/PagerDuty when
automation fails, including the command, exit code, and a link to logs.</p>

<h3>7. Notification: turning a silent failure into a visible alert</h3>
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
<p>kopf lets you write Kubernetes operators in Python: decorate handlers for
create/update/delete of custom resources. Use it when you need domain logic
beyond Helm templates, with care for retries and idempotency.</p>

<h3>8. Custom operators with `kopf`: native Kubernetes extensions</h3>
<pre><code># pip install kopf
import kopf

@kopf.on.create("example.com", "v1", "buckets")
def create_bucket(spec, name, **kwargs):
    boto3.client("s3").create_bucket(Bucket=spec["name"])
    return {"createdBucket": spec["name"]}

@kopf.on.delete("example.com", "v1", "buckets")
def delete_bucket(spec, **kwargs):
    boto3.client("s3").delete_bucket(Bucket=spec["name"])</code></pre>
<p>Checklist for DevSecOps tools others will run:</p>
<ul>
<li>Credentials from env/role/secret manager — never source.</li>
<li>Timeouts, retries with backoff, and clear exit codes.</li>
<li><code>--dry-run</code> for destructive actions.</li>
<li>Structured logs on stderr; machine-readable result on stdout (JSON flag).</li>
<li>Idempotent operations where possible.</li>
<li>Tests for the policy logic; integration tests for cloud/k8s boundaries.</li>
<li>Pinned dependencies and a minimal CI gate before merge.</li>
</ul>

<h3>9. Checklist for DevSecOps tools other people will run</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>JSON output for machines, text for humans</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Credentials only via IAM/env — never in code</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Explicit timeouts, retries and exit codes</p></div>
  </div>
  <figcaption>Tools others will operate: predictable, auditable, and with no embedded secrets.</figcaption>
</figure>
<p>The Python you practiced in this phase — packaging, HTTP, subprocess,
concurrency, tests — is the substrate. Production tools are those habits
applied with security and operability as first-class requirements.</p>
"""
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
                "practical_en": (
                    "Build <code>license_gate.py</code> that: (1) walks the project's "
                    "<code>uv.lock</code> or <code>pyproject.toml</code>; (2) queries the <a "
                    "href=\"https://pypi.org\">PyPI JSON</a> API for each lib "
                    "(<code>https://pypi.org/pypi/&lt;name&gt;/json</code>); (3) extracts "
                    "the license and blocks if it's on the denylist (<code>GPL-*</code>, "
                    "<code>AGPL-*</code>); (4) emits <code>::error::</code> in GitHub "
                    "Actions format and exit code 1 on violations; (5) has an "
                    "<code>--allow-list path</code> flag to override defaults."
                ),
            },
            "materials": [
                m("boto3 documentation",
                  "https://boto3.amazonaws.com/v1/documentation/api/latest/index.html",
                  "docs", "SDK oficial AWS para Python.",
                  title_en="boto3 documentation",
                  description_en="AWS SDK for Python."),
                m("kubernetes Python client",
                  "https://github.com/kubernetes-client/python",
                  "docs", "Cliente oficial do K8s para Python.",
                  title_en="kubernetes Python client",
                  description_en="Official Kubernetes Python client."),
                m("prometheus-client",
                  "https://github.com/prometheus/client_python",
                  "docs", "Lib para expor métricas Prometheus.",
                  title_en="prometheus-client",
                  description_en="Prometheus metrics instrumentation."),
                m("Pushgateway",
                  "https://github.com/prometheus/pushgateway",
                  "docs", "Coletor para batch jobs.",
                  title_en="Pushgateway",
                  description_en="Push metrics from short-lived jobs."),
                m("kopf, Kubernetes Operators in Python",
                  "https://kopf.readthedocs.io/",
                  "docs", "Framework para operadores K8s.",
                  title_en="kopf, Kubernetes Operators in Python",
                  description_en="Write K8s operators in Python."),
                m("AWS Well-Architected, Python on Lambda",
                  "https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html",
                  "docs", "Práticas de Python em Lambda.",
                  title_en="AWS Well-Architected, Python on Lambda",
                  description_en="Python on AWS Lambda guidance."),
            ],
            "questions": [
                q("Qual o jeito recomendado de autenticar boto3 em uma EC2 da própria AWS?",
                  "Anexar um IAM Role à instância, o SDK pega credenciais via IMDS automaticamente.",
                  ["Deixar as credenciais escritas diretamente dentro do arquivo `config.py`.", "Configurar um fluxo de OIDC integrado a um Vault externo, mesmo já dentro da AWS.", "Guardar as credenciais dentro de variáveis definidas em `/etc/environment`."],
                  "IAM Role + IMDSv2 é a forma segura. Sem credenciais persistidas, "
                  "sem rotação manual.",
                  statement_en="What's the recommended way to authenticate boto3 on an EC2 instance in AWS itself?",
                  correct_en="Attach an IAM Role to the instance; the SDK gets credentials via IMDS automatically.",
                  wrong_en=[
                            "Leave credentials written directly inside the `config.py` file.",
                            "Configure an OIDC flow integrated with an external Vault, even already inside AWS.",
                            "Store credentials in variables defined in `/etc/environment`.",
                        ],
                  explanation_en="IAM Role + IMDSv2 is the secure way. No persisted credentials, no manual rotation."),
                q("`config.load_incluster_config()` falha quando rodando localmente. Como tratar?",
                  "Tentar primeiro e cair para `load_kube_config()` em ConfigException.",
                  ["Usar só `load_kube_config()` em qualquer ambiente, sem tentar o outro.", "Forçar manualmente a variável de ambiente `KUBECONFIG`.", "Não existe outra forma, é preciso rodar dentro de um container."],
                  "Padrão clássico: tenta in-cluster (vê /var/run/secrets/...); "
                  "se não, usa kubeconfig local. Mesma ferramenta funciona em ambos "
                  "contextos.",
                  statement_en="`config.load_incluster_config()` fails when running locally. How do you handle it?",
                  correct_en="Try it first and fall back to `load_kube_config()` on ConfigException.",
                  wrong_en=[
                            "Only use `load_kube_config()` in any environment, without trying the other.",
                            "Manually force the `KUBECONFIG` environment variable.",
                            "There's no other way; you must run inside a container.",
                        ],
                  explanation_en="Classic pattern: try in-cluster (looks for /var/run/secrets/...); if not, use local kubeconfig. Same tool works in both places."),
                q("Para um job batch que termina, expor métricas Prometheus como?",
                  "Empurrar para Pushgateway com push_to_gateway.",
                  ["Simplesmente não é possível coletar métricas desse tipo de job.", "Salvar as métricas manualmente num arquivo `.prom` local.", "Iniciar um servidor HTTP que continua de pé mesmo após o job terminar."],
                  "Pushgateway armazena temporariamente as métricas para Prometheus "
                  "scrape. É o padrão para jobs efêmeros.",
                  statement_en="For a batch job that finishes, how do you expose Prometheus metrics?",
                  correct_en="Push them to Pushgateway with push_to_gateway.",
                  wrong_en=[
                            "It simply isn't possible to collect metrics from this kind of job.",
                            "Manually save the metrics in a local `.prom` file.",
                            "Start an HTTP server that stays up even after the job finishes.",
                        ],
                  explanation_en="Pushgateway temporarily stores metrics for Prometheus to scrape. It's the standard for ephemeral jobs."),
                q("Para listar todos os objetos de um bucket S3 grande:",
                  "client.get_paginator('list_objects_v2').paginate(Bucket=name)",
                  ["client.list_objects(Bucket=name, MaxKeys=1000, Prefix='', Marker='')", "boto3.list_all(Bucket=name, recursive=True, retry=3, timeout=30)", "ec2.objects.all(Bucket=name, filter=True, limit=None, sort='asc')"],
                  "list_objects_v2 retorna 1000 itens por página. Paginator itera "
                  "automaticamente todas as páginas.",
                  statement_en="To list all objects in a large S3 bucket:",
                  correct_en="client.get_paginator('list_objects_v2').paginate(Bucket=name)",
                  wrong_en=[
                            "client.list_objects(Bucket=name, MaxKeys=1000, Prefix='', Marker='')",
                            "boto3.list_all(Bucket=name, recursive=True, retry=3, timeout=30)",
                            "ec2.objects.all(Bucket=name, filter=True, limit=None, sort='asc')",
                        ],
                  explanation_en="list_objects_v2 returns 1000 items per page. Paginator automatically iterates all pages."),
                q("`subprocess.run([..., 'aws', 's3', 'cp', ...])` vs. boto3, qual a vantagem do boto3?",
                  "Type-safe, tratamento de erros pythonic, sem dependência do CLI instalado.",
                  ["Dispensa qualquer tipo de configuração prévia de credencial na máquina.", "É consideravelmente mais rápido de executar na prática do que usar o CLI.", "Continua funcionando normalmente mesmo sem qualquer conexão de rede disponível."],
                  "boto3 retorna dicts e levanta exceções tipadas. subprocess depende "
                  "do CLI estar no PATH e tem overhead de serialização JSON.",
                  statement_en="`subprocess.run([..., 'aws', 's3', 'cp', ...])` vs boto3 — what's boto3's advantage?",
                  correct_en="Type-safe, pythonic error handling, no dependency on the CLI being installed.",
                  wrong_en=[
                            "It removes any need for prior credential configuration on the machine.",
                            "It's considerably faster to run in practice than using the CLI.",
                            "It keeps working normally even without any network connection available.",
                        ],
                  explanation_en="boto3 returns dicts and raises typed exceptions. subprocess depends on the CLI being on PATH and has JSON serialization overhead."),
                q("Para reagir a eventos em tempo real no K8s, use:",
                  "kubernetes.watch.Watch().stream(...)",
                  ["ETag controlado manualmente a cada chamada", "polling com sleep(60) entre chamadas", "Só via CLI, sem qualquer suporte no SDK Python"],
                  "Watch usa long-polling do API Server: receberia eventos imediatos. "
                  "Polling é desperdício de quota e atrasa reação.",
                  statement_en="To react to real-time events in K8s, use:",
                  correct_en="kubernetes.watch.Watch().stream(...)",
                  wrong_en=[
                            "Manually controlled ETag on every call",
                            "polling with sleep(60) between calls",
                            "Only via CLI, with no support in the Python SDK",
                        ],
                  explanation_en="Watch uses API Server long-polling: you get immediate events. Polling wastes quota and delays reaction."),
                q("Em uma ferramenta de CI, a saída idealmente vai em JSON quando:",
                  "O consumidor é outra ferramenta (script, pipeline).",
                  ["A saída deveria ir em JSON em qualquer cenário, mesmo lida por humano.", "Só quando a ferramenta está rodando já em produção.", "Só quando a execução termina encontrando algum erro."],
                  "Humanos preferem texto formatado; máquinas preferem JSON. Idiomático: "
                  "flag --json para alternar.",
                  statement_en="In a CI tool, output ideally goes as JSON when:",
                  correct_en="The consumer is another tool (script, pipeline).",
                  wrong_en=[
                            "Output should be JSON in any scenario, even when read by a human.",
                            "Only when the tool is already running in production.",
                            "Only when execution ends with some error.",
                        ],
                  explanation_en="Humans prefer formatted text; machines prefer JSON. Idiomatic: a --json flag to switch."),
                q("`::error file=app.py,line=10::Erro X` em GitHub Actions...",
                  "Cria uma annotation no arquivo/linha indicado no PR.",
                  ["Faz a action inteira falhar automaticamente assim que aparece.", "É tratado como um comentário qualquer, sem efeito especial.", "É só um print colorido exibido no terminal do runner."],
                  "Workflow commands. ::error gera annotation; ::warning idem; "
                  "::set-output (deprecado em favor de $GITHUB_OUTPUT).",
                  statement_en="`::error file=app.py,line=10::Error X` in GitHub Actions...",
                  correct_en="Creates an annotation on the indicated file/line in the PR.",
                  wrong_en=[
                            "Makes the entire action fail automatically as soon as it appears.",
                            "Is treated as an ordinary comment, with no special effect.",
                            "Is just a colored print shown in the runner terminal.",
                        ],
                  explanation_en="Workflow commands. ::error creates an annotation; ::warning likewise; ::set-output (deprecated in favor of $GITHUB_OUTPUT)."),
                q("Boa prática para ferramentas destrutivas (delete, drop):",
                  "Implementar --dry-run que mostra o que faria sem executar.",
                  ["Fazer rollback automático depois de qualquer execução destrutiva.", "Só registrar logs quando a ferramenta roda em produção.", "Pedir uma senha extra em grande parte da execução da ferramenta."],
                  "Dry-run é o equivalente de `terraform plan`. Permite revisar antes "
                  "de aplicar; vital para evitar erros operacionais.",
                  statement_en="Good practice for destructive tools (delete, drop):",
                  correct_en="Implement --dry-run that shows what it would do without executing.",
                  wrong_en=[
                            "Do automatic rollback after any destructive execution.",
                            "Only write logs when the tool runs in production.",
                            "Ask for an extra password for a large part of the tool's execution.",
                        ],
                  explanation_en="Dry-run is the equivalent of `terraform plan`. Lets you review before applying; vital to avoid operational mistakes."),
                q("Idempotência em scripts DevOps significa:",
                  "Rodar o mesmo script várias vezes leva ao mesmo estado, sem efeitos colaterais extras.",
                  ["Significa que o script só pode ser executado uma única vez ao longo do tempo, abordagem que funciona bem até o primeiro pico de carga real.", "Significa que o script já vem com um mecanismo de retry embutido internamente, prática que gera falso senso de segurança no time.", "Significa que o script em questão não faz qualquer operação de I/O, comportamento que confunde quem está debugando meses depois."],
                  "Ex: 'criar bucket' deveria checar se existe primeiro. Idempotência "
                  "é base de Ansible, Terraform e bons pipelines de deploy.",
                  statement_en="Idempotency in DevOps scripts means:",
                  correct_en="Running the same script multiple times leads to the same state, without extra side effects.",
                  wrong_en=[
                            "It means the script can only be executed once over time — an approach that works fine until the first real load spike.",
                            "It means the script already comes with a built-in retry mechanism — a practice that creates a false sense of security on the team.",
                            "It means the script in question does no I/O at all — behavior that confuses whoever is debugging months later.",
                        ],
                  explanation_en="E.g. 'create bucket' should check if it exists first. Idempotency is the foundation of Ansible, Terraform and good deploy pipelines."),
            ],
        },
    ],
}
