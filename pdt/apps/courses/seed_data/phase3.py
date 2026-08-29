"""Fase 3, Automação e Ciclo de Vida (DevOps & IaC)."""
from ._helpers import m, q

PHASE3 = {
    "name": "Fase 3: Automação e Ciclo de Vida (DevOps & IaC)",
    "name_en": "Phase 3: Automation and Lifecycle (DevOps & IaC)",
    "description": "Parar de configurar as coisas manualmente e usar código.",
    "description_en": "Stop configuring things manually and use code instead.",
    "topics": [
        # =====================================================================
        # 3.1 Versionamento com Git
        # =====================================================================
        {
            "title": "Versionamento com Git",
            "title_en": "Version Control with Git",
            "summary": "Fluxos de trabalho seguros (Gitflow) e proteção de branches.",
            "summary_en": "Safe workflows (Gitflow) and branch protection.",
            "lesson": {
                "intro": (
                    "Git é o sistema nervoso central de qualquer time moderno de software. "
                    "É praticamente impossível encontrar um pipeline DevOps que não comece "
                    "com 'um push para o repositório'. Mas existe uma diferença abismal entre "
                    "<em>usar</em> Git (commit, push, pull) e <em>entender</em> Git (commits "
                    "são snapshots imutáveis, branches são ponteiros, HEAD é a posição atual, "
                    "history é um DAG, Directed Acyclic Graph). Essa diferença é o que separa "
                    "quem 'sobrevive a Git' de quem 'domina o fluxo' em incidentes, quando "
                    "um colega rebase em produção e some o trabalho do time inteiro, ou "
                    "quando você precisa recuperar um commit que parecia perdido. Esta aula "
                    "vai do modelo mental até políticas de proteção de produção, passando "
                    "por workflows do mundo real."
                ),
                "intro_en": (
                    "Git is the central nervous system of any modern software team. "
                    "It's practically impossible to find a DevOps pipeline that doesn't start "
                    "with 'a push to the repository.' But there's an abysmal difference between "
                    "<em>using</em> Git (commit, push, pull) and <em>understanding</em> Git (commits "
                    "are immutable snapshots, branches are pointers, HEAD is the current position, "
                    "history is a DAG, a Directed Acyclic Graph). That difference is what separates "
                    "those who 'survive Git' from those who 'master the flow' during incidents, when "
                    "a colleague rebases in production and the whole team's work vanishes, or "
                    "when you need to recover a commit that seemed lost. This lesson goes from the "
                    "mental model to production protection policies, covering real-world "
                    "workflows along the way."
                ),
                "body": (
                    "<h3>1. Modelo mental: o que Git realmente armazena</h3>"
                    "<p>A primeira coisa a entender: Git não armazena <em>diferenças</em> "
                    "(como SVN), ele armazena <em>snapshots</em>. Cada commit é um objeto "
                    "imutável que aponta para uma <em>tree</em> (estado de toda a árvore "
                    "de arquivos), o(s) commit(s) pai(s), autor, mensagem, timestamp. Tudo "
                    "isso é endereçado por um hash SHA-1 (ou SHA-256 em repos modernos). "
                    "Esse hash é determinístico: mesmo conteúdo + mesmo pai + mesmo autor "
                    "gera mesmo hash.</p>"
                    """
<div class="mermaid">
flowchart TD
    Blob["blob: conteúdo do arquivo"] --> Tree["tree: diretório + nomes"]
    Tree --> Commit["commit: tree + pais + autor"]
    Commit --> Ref["ref: branch/tag aponta pro hash"]
    Ref --> Head["HEAD: onde você está agora"]
</div>
"""
                    "<p>Internamente, o <code>.git/objects/</code> contém quatro tipos:</p>"
                    "<ul>"
                    "<li><strong>blob</strong>: conteúdo de um arquivo.</li>"
                    "<li><strong>tree</strong>: diretório (lista de blobs/trees + nomes + perms).</li>"
                    "<li><strong>commit</strong>: aponta para uma tree raiz, pais, autor, mensagem.</li>"
                    "<li><strong>tag</strong>: anotação assinada para um commit.</li>"
                    "</ul>"
                    "<p>Branches e tags são apenas <em>refs</em>, arquivos texto em "
                    "<code>.git/refs/</code> contendo um hash. <code>HEAD</code> é o ref "
                    "que aponta para o branch atual (ou diretamente para um commit em "
                    "'detached HEAD').</p>"
                    "<p>Demonstre você mesmo:</p>"
                    "<pre><code>$ echo 'olá' > hello.txt\n"
                    "$ git add hello.txt\n"
                    "$ git commit -m 'first'\n"
                    "$ git cat-file -p HEAD\n"
                    "tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904\n"
                    "parent ...\n"
                    "author Você &lt;voce@ex.com&gt; ...\n"
                    "first\n"
                    "$ git cat-file -p 4b825...   # mostra a tree</code></pre>"
                    "<p>Esse modelo importa: quando você 'reseta', 'rebaseia' ou 'cherry-picka', "
                    "você está manipulando ponteiros e criando <em>novos</em> commits, "
                    "raramente apagando objetos. Isso é o que torna Git surpreendentemente "
                    "recuperável (via <code>reflog</code>) mesmo após operações 'destrutivas'.</p>"

                    "<h3>2. Workflows: escolha que casa com seu time</h3>"
                    "<p>Não existe workflow universalmente melhor, existe o que combina com "
                    "o nível de maturidade do time, o tipo do produto e a frequência de "
                    "deploy.</p>"
                    "<h4>2.1 Trunk-Based Development (TBD)</h4>"
                    "<ul>"
                    "<li>Todos commitam direto em <code>main</code> (ou abrem PRs <em>muito</em> "
                    "curtos, que vivem horas).</li>"
                    "<li>Código incompleto vai para <code>main</code> escondido atrás de "
                    "<strong>feature flags</strong>.</li>"
                    "<li>Build/teste/deploy roda a cada commit.</li>"
                    "<li>Times Google/Meta/Netflix usam variações.</li>"
                    "</ul>"
                    "<p>Vantagens: zero merge hell, integração contínua de verdade, deploys "
                    "frequentes (várias vezes por dia). Desvantagens: exige suite de testes "
                    "muito boa, feature flags maduras, cultura de 'never break trunk'.</p>"
                    "<h4>2.2 GitHub Flow</h4>"
                    "<ul>"
                    "<li><code>main</code> sempre deployable.</li>"
                    "<li>Cada feature em branch curto (<code>feat/algo</code>).</li>"
                    "<li>Abre PR cedo, conversa, revisa, mergeia.</li>"
                    "<li>Deploy direto da main.</li>"
                    "</ul>"
                    "<p>Simples, popular em SaaS modernos. É 'TBD com PRs como ritual de revisão'.</p>"
                    "<h4>2.3 Gitflow (Vincent Driessen, 2010)</h4>"
                    "<p>Era o padrão de mercado por muito tempo:</p>"
                    "<ul>"
                    "<li><code>main</code>: tags de release.</li>"
                    "<li><code>develop</code>: integração contínua.</li>"
                    "<li><code>feature/*</code>: features novas (saem de develop).</li>"
                    "<li><code>release/*</code>: estabilização para release.</li>"
                    "<li><code>hotfix/*</code>: correções urgentes em main.</li>"
                    "</ul>"
                    "<p>Cabe bem em produtos com release planejado (mobile com release "
                    "trimestral aprovado pela Apple, software embarcado, jogos). Em SaaS "
                    "moderno é geralmente burocrático demais e atrapalha entrega contínua. "
                    "Até o próprio autor publicou retratação dizendo que 'em SaaS, prefira "
                    "GitHub Flow'.</p>"
                    "<h4>2.4 Release branching (forks por versão)</h4>"
                    "<p>Comum em projetos de longa duração com múltiplas versões "
                    "suportadas em paralelo (Linux kernel, Postgres, Kubernetes). Cada "
                    "versão major mantém uma branch separada (<code>release-1.28</code>) "
                    "que recebe backports de fixes selecionados.</p>"

                    "<h3>3. Política de proteção de branches em produção</h3>"
                    "<p>Em <code>main</code> (ou equivalente), configure no GitHub/GitLab:</p>"
                    "<ul>"
                    "<li><strong>Pull Request obrigatório</strong> (sem push direto).</li>"
                    "<li><strong>Pelo menos 1 review aprovado</strong> (1-2 dependendo do "
                    "criticality; 2 para sensíveis em CODEOWNERS).</li>"
                    "<li><strong>Status checks obrigatórios verdes</strong> (CI build, lint, "
                    "tests, SAST, SCA, IaC scan, secret scan).</li>"
                    "<li><strong>Bloqueio de force-push</strong>.</li>"
                    "<li><strong>Linear history</strong> (sem merge commits, força rebase ou "
                    "squash).</li>"
                    "<li><strong>Signed commits</strong> obrigatórios (GPG ou SSH).</li>"
                    "<li><strong>Conversation resolution</strong>: comentários precisam ser "
                    "marcados como resolvidos.</li>"
                    "<li><strong>Restrict who can push</strong>: incluir maintainers, mas "
                    "<em>incluir admins na regra</em>. A frase 'eu sou admin, posso pular o "
                    "review' já causou tantos incidentes que GitHub e GitLab adicionaram "
                    "checkboxes só para isso.</li>"
                    "</ul>"
                    "<p>Em GitHub, configure também <strong>tag protection</strong> e "
                    "<strong>environment protection</strong> para deploy em produção exigir "
                    "aprovação manual e/ou wait timer.</p>"

                    "<h3>4. Boas práticas de commits</h3>"
                    "<h4>4.1 Atomicidade</h4>"
                    "<p>Um commit = uma mudança lógica. Misturar 'fix bug X' + 'refator "
                    "componente Y' + 'atualizar dependência Z' no mesmo commit dificulta "
                    "review, bisect, revert seletivo.</p>"
                    "<p>Use <code>git add -p</code> (patch) para stagear pedaços específicos "
                    "do diff, não o arquivo inteiro:</p>"
                    "<pre><code>$ git add -p src/auth.py\n"
                    "Stage this hunk [y,n,q,a,d,e,?]?</code></pre>"
                    "<h4>4.2 Mensagem com 'why', não só 'what'</h4>"
                    "<p>Ruim: <code>fix bug</code>, <code>update code</code>, <code>asdf</code>.</p>"
                    "<p>Bom:</p>"
                    "<pre><code>fix(auth): block login após 5 tentativas em 15min\n"
                    "\n"
                    "Antes, força bruta era teórica, sem rate limit no endpoint /login.\n"
                    "Implementa contador em Redis com TTL, retornando 429 após threshold.\n"
                    "\n"
                    "Refs: SEC-1234, OWASP A07:2021</code></pre>"
                    "<p>O 'what' o diff já mostra. O 'why' é o que reviewer (e você daqui a 6 "
                    "meses) precisa.</p>"
                    "<h4>4.3 Conventional Commits</h4>"
                    "<p>Padrão simples e popular:</p>"
                    "<pre><code>&lt;type&gt;(&lt;scope&gt;): &lt;descrição&gt;\n"
                    "\n"
                    "feat(api): adiciona endpoint /v2/users\n"
                    "fix(payment): corrige race condition em refund\n"
                    "chore(deps): atualiza django para 5.1.4\n"
                    "docs(readme): exemplo de docker compose\n"
                    "refactor(core): extrai service do view\n"
                    "test(api): cobre 401 em /admin\n"
                    "ci: roda trivy em pull request\n"
                    "perf(db): cria índice em users(email)\n"
                    "BREAKING CHANGE: removido campo deprecated 'name'</code></pre>"
                    "<p>Ferramentas como <code>commitlint</code>, <code>commitizen</code>, "
                    "<code>release-please</code>, <code>semantic-release</code> consomem essa "
                    "convenção para gerar changelog automático e bumpar versão semver, "
                    "<code>fix:</code> = patch (1.0.1), <code>feat:</code> = minor (1.1.0), "
                    "<code>BREAKING CHANGE:</code> = major (2.0.0).</p>"
                    "<h4>4.4 Signed commits</h4>"
                    "<p>Sem assinatura, qualquer um pode setar <code>user.email</code> para "
                    "<code>cto@empresa.com</code> e fazer commits com nome do CTO. GitHub/GitLab "
                    "exibem como autor sem questionar, não é spoofing 'sofisticado', é "
                    "comportamento normal do Git.</p>"
                    "<p>Configure GPG ou SSH signing:</p>"
                    "<pre><code># SSH (mais simples; funciona com mesma chave de auth)\n"
                    "git config --global user.signingkey ~/.ssh/id_ed25519.pub\n"
                    "git config --global gpg.format ssh\n"
                    "git config --global commit.gpgsign true\n"
                    "git config --global tag.gpgsign true</code></pre>"
                    "<p>No GitHub: Settings → SSH and GPG keys → New SSH key (Signing key). "
                    "Em branch protection, marque 'Require signed commits'. Quem não assina = "
                    "não mergeia.</p>"

                    "<h3>5. Merge, rebase e cherry-pick: quando usar cada um</h3>"
                    """
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Merge</strong><p>Preserva histórico do branch; cria commit com 2 pais. Ideal para manter contexto da feature.</p></div>
    <div class="lesson-viz-card"><strong>Rebase</strong><p>Reescreve commits em cima da base nova; histórico linear. Só em branches ainda não compartilhados.</p></div>
  </div>
  <figcaption>Merge vs rebase: escolha pelo contexto do time, não por dogma.</figcaption>
</figure>
"""

                    "<h4>5.1 Merge</h4>"
                    "<p>Cria um commit com 2+ pais. Preserva a história intocada.</p>"
                    "<pre><code>$ git checkout main\n"
                    "$ git merge feature/login\n"
                    "Merge made by the 'recursive' strategy.</code></pre>"
                    "<p>Ideal quando: você quer manter visível o contexto do branch ('estes "
                    "10 commits foram a feature X'). Mantém atribuição original. Não reescreve.</p>"
                    "<h4>5.2 Squash merge</h4>"
                    "<p>Junta todos os commits do PR em um único, com a mensagem do PR. "
                    "História de main fica linear e limpa, mas você perde granularidade "
                    "intermediária.</p>"
                    "<p>Bom para: PRs com 'wip', 'fix typo', 'fix lint' que polui histórico. "
                    "Ruim para: PRs grandes onde commits intermediários têm valor.</p>"
                    "<h4>5.3 Rebase</h4>"
                    "<p>Reaplica commits do branch atual <em>em cima</em> de outra base, "
                    "criando novos hashes (mesma mudança, novo commit).</p>"
                    "<pre><code>$ git checkout feature/login\n"
                    "$ git rebase main\n"
                    "Successfully rebased and updated refs/heads/feature/login.</code></pre>"
                    "<p>Resultado: branch <code>feature/login</code> agora 'parece' ter saído "
                    "da última versão de main. Histórico fica linear. Bom para 'limpar' o "
                    "PR antes do merge.</p>"
                    "<p><strong>REGRA DE OURO</strong>: nunca rebase história já compartilhada. "
                    "Se você rebaseou commits que outras pessoas já têm, na próxima vez que "
                    "elas fizerem pull, vão ter conflito (ou pior, vão re-introduzir os commits "
                    "antigos).</p>"
                    "<p>Rebase interativo é poderoso para 'reescrever' commits locais antes "
                    "do push:</p>"
                    "<pre><code>$ git rebase -i HEAD~5\n"
                    "pick a1b2c3 feat(api): novo endpoint\n"
                    "squash d4e5f6 fix typo\n"
                    "squash 7g8h9i wip\n"
                    "reword 0j1k2l adiciona testes\n"
                    "drop 3m4n5o commit acidental</code></pre>"
                    "<h4>5.4 Cherry-pick</h4>"
                    "<p>Aplica um commit específico em outro branch:</p>"
                    "<pre><code>$ git checkout release-1.28\n"
                    "$ git cherry-pick a1b2c3   # backport do fix\n"
                    "$ git push origin release-1.28</code></pre>"
                    "<p>Padrão clássico para backportar fix urgente em release branch antiga "
                    "sem trazer todas as features de main.</p>"

                    "<h3>6. Recuperação: como se salvar de quase tudo</h3>"
                    "<h4>6.1 reflog: a corda de segurança</h4>"
                    "<p><code>git reflog</code> guarda <em>localmente</em> toda movimentação "
                    "do <code>HEAD</code> (e de cada branch) por 90 dias por padrão. Mesmo "
                    "após <code>git reset --hard</code>, <code>git rebase</code>, deletar "
                    "branch, os commits ainda estão lá.</p>"
                    "<pre><code>$ git reflog\n"
                    "abc1234 HEAD@{0}: reset: moving to HEAD~3\n"
                    "def5678 HEAD@{1}: commit: feat: nova feature crítica\n"
                    "...\n"
                    "$ git reset --hard def5678   # voltei para o estado anterior</code></pre>"
                    "<h4>6.2 stash</h4>"
                    "<p>Arquiva mudanças não commitadas para retomar depois:</p>"
                    "<pre><code>$ git stash push -m 'wip do refactor'\n"
                    "$ git stash list\n"
                    "stash@{0}: On feature/x: wip do refactor\n"
                    "$ git stash pop   # retoma e remove da pilha\n"
                    "$ git stash apply stash@{0}   # aplica sem remover</code></pre>"
                    "<h4>6.3 revert: undo seguro em main</h4>"
                    "<p>Cria um <em>novo</em> commit que inverte o anterior. Não reescreve "
                    "história, pode usar em main sem afetar ninguém:</p>"
                    "<pre><code>$ git revert abc1234\n"
                    "[main 7g8h9i] Revert 'feat: feature ruim'</code></pre>"
                    "<h4>6.4 reset: cuidado em compartilhado</h4>"
                    "<p><code>git reset</code> tem 3 modos:</p>"
                    "<ul>"
                    "<li><code>--soft</code>: move HEAD, mantém index e working tree.</li>"
                    "<li><code>--mixed</code> (padrão): move HEAD, reseta index, mantém working tree.</li>"
                    "<li><code>--hard</code>: move HEAD, reseta index e working tree (perigoso!).</li>"
                    "</ul>"
                    "<p>Em branch local: ok. Em branch compartilhado: NUNCA combinado com "
                    "force-push, exceto em emergência (e com aviso ao time).</p>"
                    "<h4>6.5 bisect: caça ao bug por busca binária</h4>"
                    "<p>Quando bug apareceu 'em algum lugar nos últimos 200 commits', use:</p>"
                    "<pre><code>$ git bisect start\n"
                    "$ git bisect bad HEAD          # commit atual está quebrado\n"
                    "$ git bisect good v1.0         # esta tag estava ok\n"
                    "Bisecting: 100 revisions left to test\n"
                    "$ # roda teste; se passa: git bisect good; se falha: git bisect bad\n"
                    "$ git bisect run pytest test_login.py    # automatiza!</code></pre>"
                    "<p>Em ~7 passos você pega o commit em 200. Em projetos grandes (kernel "
                    "Linux), bisect é como mantenedores caçam regressões.</p>"

                    "<h3>7. Anti-patterns comuns (e como evitar)</h3>"
                    """
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Nunca force-push em main/protegida</p></div>
    <div class="lesson-viz-step"><span>2</span><p>PR pequeno e focado (não 3000 linhas)</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Assine commits e exija checks verdes</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Use reflog antes de panicar após reset</p></div>
  </div>
  <figcaption>Checklist anti-caos em Git de produção.</figcaption>
</figure>
"""

                    "<ul>"
                    "<li><strong>'PR de 3000 linhas'</strong>: ninguém revisa de verdade. "
                    "Quebre em PRs menores, ou aceite que será rubber stamp.</li>"
                    "<li><strong>'Force push em main para esconder erro'</strong>: log de "
                    "auditoria GitHub/GitLab guarda. Você só esconde para si mesmo. Faça "
                    "<code>revert</code>.</li>"
                    "<li><strong>'Commit massivo de 'inicial commit''</strong>: sem histórico = "
                    "sem bisect, sem blame útil. Faça commits pequenos desde o dia 0.</li>"
                    "<li><strong>'.gitignore depois de commitar segredo'</strong>: o segredo "
                    "está no histórico para sempre. Único fix: rotacione o segredo "
                    "imediatamente. Apagar do histórico (BFG, git filter-repo) é teatro, "
                    "forks/clones já existem.</li>"
                    "<li><strong>'Commit de arquivos gigantes'</strong>: repos enchem rápido. "
                    "Use Git LFS para mídia/binários (&gt;10MB).</li>"
                    "<li><strong>'Branches longas (semanas/meses)'</strong>: merge hell "
                    "garantido. Mergeie main de volta na branch frequentemente.</li>"
                    "</ul>"

                    "<h3>8. Caso real: o force-push de Domingo</h3>"
                    "<p>Empresa X. Domingo, 10h. Dev tira plantão, vê que merge accidental "
                    "trouxe código quebrado para main. Faz <code>git reset --hard HEAD~3</code> "
                    "e <code>git push --force origin main</code>. Resolveu? Não:</p>"
                    "<ul>"
                    "<li>Outros 30 devs na segunda começam a clonar/pull e ter conflitos "
                    "estranhos.</li>"
                    "<li>CI/CD que cacheia artefatos por SHA fica lost, SHA não existe mais.</li>"
                    "<li>Tags que apontavam para os commits sumiram da vista (mas estão no reflog).</li>"
                    "<li>Auditoria de compliance: '...você acabou de reescrever 3 commits "
                    "produtivos sem rastreabilidade.'</li>"
                    "</ul>"
                    "<p>Lição: <em>nunca</em> use force-push em main. Use revert. Configure "
                    "branch protection para tornar isso impossível, mesmo para admins.</p>"
                ),
                "body_en": """<h3>1. Mental model: what Git actually stores</h3>
<p>The first thing to understand: Git does not store <em>diffs</em>
(like SVN), it stores <em>snapshots</em>. Each commit is an immutable
object that points to a <em>tree</em> (the state of the entire file
tree), its parent commit(s), author, message, timestamp. All of this
is addressed by a SHA-1 hash (or SHA-256 in modern repos). That hash
is deterministic: same content + same parent + same author produces
the same hash.</p>
<div class="mermaid">
flowchart TD
    Blob["blob: file contents"] --> Tree["tree: directory + names"]
    Tree --> Commit["commit: tree + parents + author"]
    Commit --> Ref["ref: branch/tag points to hash"]
    Ref --> Head["HEAD: where you are now"]
</div>
<p>Internally, <code>.git/objects/</code> contains four types:</p>
<ul>
<li><strong>blob</strong>: the content of a file.</li>
<li><strong>tree</strong>: a directory (list of blobs/trees + names + perms).</li>
<li><strong>commit</strong>: points to a root tree, parents, author, message.</li>
<li><strong>tag</strong>: a signed annotation for a commit.</li>
</ul>
<p>Branches and tags are just <em>refs</em>, plain text files under
<code>.git/refs/</code> containing a hash. <code>HEAD</code> is the ref
that points to the current branch (or directly to a commit in
'detached HEAD').</p>
<p>Try it yourself:</p>
<pre><code>$ echo 'olá' > hello.txt
$ git add hello.txt
$ git commit -m 'first'
$ git cat-file -p HEAD
tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904
parent ...
author Você &lt;voce@ex.com&gt; ...
first
$ git cat-file -p 4b825...   # shows the tree</code></pre>
<p>This model matters: when you 'reset', 'rebase' or 'cherry-pick',
you are manipulating pointers and creating <em>new</em> commits,
rarely deleting objects. That's what makes Git surprisingly
recoverable (via <code>reflog</code>) even after 'destructive'
operations.</p>

<h3>2. Workflows: pick what matches your team</h3>
<p>There is no universally best workflow, only the one that matches
the team's maturity level, the type of product and the deploy
frequency.</p>
<h4>2.1 Trunk-Based Development (TBD)</h4>
<ul>
<li>Everyone commits directly to <code>main</code> (or opens <em>very</em>
short-lived PRs, living hours).</li>
<li>Incomplete code goes into <code>main</code> hidden behind
<strong>feature flags</strong>.</li>
<li>Build/test/deploy runs on every commit.</li>
<li>Google/Meta/Netflix teams use variations of this.</li>
</ul>
<p>Advantages: zero merge hell, real continuous integration, frequent
deploys (several times a day). Disadvantages: requires a very good
test suite, mature feature flags, a 'never break trunk' culture.</p>
<h4>2.2 GitHub Flow</h4>
<ul>
<li><code>main</code> is always deployable.</li>
<li>Each feature lives in a short branch (<code>feat/something</code>).</li>
<li>Open the PR early, discuss, review, merge.</li>
<li>Deploy directly from main.</li>
</ul>
<p>Simple, popular in modern SaaS. It's 'TBD with PRs as a review ritual'.</p>
<h4>2.3 Gitflow (Vincent Driessen, 2010)</h4>
<p>It was the market standard for a long time:</p>
<ul>
<li><code>main</code>: release tags.</li>
<li><code>develop</code>: continuous integration.</li>
<li><code>feature/*</code>: new features (branch off develop).</li>
<li><code>release/*</code>: stabilization for a release.</li>
<li><code>hotfix/*</code>: urgent fixes on main.</li>
</ul>
<p>Fits well in products with planned releases (mobile with a
quarterly release approved by Apple, embedded software, games). In
modern SaaS it's generally too bureaucratic and gets in the way of
continuous delivery. Even the original author published a retraction
saying that 'in SaaS, prefer GitHub Flow'.</p>
<h4>2.4 Release branching (per-version forks)</h4>
<p>Common in long-lived projects with multiple versions supported in
parallel (Linux kernel, Postgres, Kubernetes). Each major version
keeps a separate branch (<code>release-1.28</code>) that receives
backports of selected fixes.</p>

<h3>3. Branch protection policy in production</h3>
<p>On <code>main</code> (or equivalent), configure in GitHub/GitLab:</p>
<ul>
<li><strong>Required Pull Request</strong> (no direct push).</li>
<li><strong>At least 1 approved review</strong> (1-2 depending on
criticality; 2 for sensitive paths in CODEOWNERS).</li>
<li><strong>Required green status checks</strong> (CI build, lint,
tests, SAST, SCA, IaC scan, secret scan).</li>
<li><strong>Force-push blocking</strong>.</li>
<li><strong>Linear history</strong> (no merge commits, forces rebase or
squash).</li>
<li><strong>Signed commits</strong> required (GPG or SSH).</li>
<li><strong>Conversation resolution</strong>: comments need to be
marked resolved.</li>
<li><strong>Restrict who can push</strong>: include maintainers, but
<em>include admins in the rule</em>. The phrase 'I'm admin, I can skip
review' has already caused enough incidents that GitHub and GitLab
added checkboxes just for that.</li>
</ul>
<p>On GitHub, also configure <strong>tag protection</strong> and
<strong>environment protection</strong> so that deploying to
production requires manual approval and/or a wait timer.</p>

<h3>4. Commit best practices</h3>
<h4>4.1 Atomicity</h4>
<p>One commit = one logical change. Mixing 'fix bug X' + 'refactor
component Y' + 'update dependency Z' in the same commit makes
review, bisect, and selective revert harder.</p>
<p>Use <code>git add -p</code> (patch) to stage specific chunks of the
diff, not the whole file:</p>
<pre><code>$ git add -p src/auth.py
Stage this hunk [y,n,q,a,d,e,?]?</code></pre>
<h4>4.2 A message with 'why', not just 'what'</h4>
<p>Bad: <code>fix bug</code>, <code>update code</code>, <code>asdf</code>.</p>
<p>Good:</p>
<pre><code>fix(auth): block login após 5 tentativas em 15min

Antes, força bruta era teórica, sem rate limit no endpoint /login.
Implementa contador em Redis com TTL, retornando 429 após threshold.

Refs: SEC-1234, OWASP A07:2021</code></pre>
<p>The diff already shows the 'what'. The 'why' is what the reviewer
(and you, 6 months from now) needs.</p>
<h4>4.3 Conventional Commits</h4>
<p>A simple, popular convention:</p>
<pre><code>&lt;type&gt;(&lt;scope&gt;): &lt;description&gt;

feat(api): adiciona endpoint /v2/users
fix(payment): corrige race condition em refund
chore(deps): atualiza django para 5.1.4
docs(readme): exemplo de docker compose
refactor(core): extrai service do view
test(api): cobre 401 em /admin
ci: roda trivy em pull request
perf(db): cria índice em users(email)
BREAKING CHANGE: removido campo deprecated 'name'</code></pre>
<p>Tools like <code>commitlint</code>, <code>commitizen</code>,
<code>release-please</code>, <code>semantic-release</code> consume
this convention to generate an automatic changelog and bump the
semver version: <code>fix:</code> = patch (1.0.1), <code>feat:</code>
= minor (1.1.0), <code>BREAKING CHANGE:</code> = major (2.0.0).</p>
<h4>4.4 Signed commits</h4>
<p>Without signing, anyone can set <code>user.email</code> to
<code>cto@empresa.com</code> and make commits under the CTO's name.
GitHub/GitLab display it as the author without question — it isn't
'sophisticated' spoofing, it's normal Git behavior.</p>
<p>Configure GPG or SSH signing:</p>
<pre><code># SSH (simpler; works with the same auth key)
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global gpg.format ssh
git config --global commit.gpgsign true
git config --global tag.gpgsign true</code></pre>
<p>On GitHub: Settings → SSH and GPG keys → New SSH key (Signing key).
In branch protection, check 'Require signed commits'. Whoever doesn't
sign doesn't merge.</p>

<h3>5. Merge, rebase and cherry-pick: when to use each one</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Merge</strong><p>Keeps branch history; creates a commit with 2 parents. Ideal to preserve feature context.</p></div>
    <div class="lesson-viz-card"><strong>Rebase</strong><p>Replays commits on a new base; linear history. Only on branches not yet shared.</p></div>
  </div>
  <figcaption>Merge vs rebase: choose by team context, not dogma.</figcaption>
</figure>

<h4>5.1 Merge</h4>
<p>Creates a commit with 2+ parents. Preserves history untouched.</p>
<pre><code>$ git checkout main
$ git merge feature/login
Merge made by the 'recursive' strategy.</code></pre>
<p>Ideal when: you want to keep the branch's context visible ('these
10 commits were feature X'). Keeps original attribution. Doesn't
rewrite anything.</p>
<h4>5.2 Squash merge</h4>
<p>Combines every commit in the PR into a single one, using the PR's
message. Main's history stays linear and clean, but you lose
intermediate granularity.</p>
<p>Good for: PRs with 'wip', 'fix typo', 'fix lint' that pollute
history. Bad for: large PRs where intermediate commits have value.</p>
<h4>5.3 Rebase</h4>
<p>Reapplies commits from the current branch <em>on top of</em>
another base, creating new hashes (same change, new commit).</p>
<pre><code>$ git checkout feature/login
$ git rebase main
Successfully rebased and updated refs/heads/feature/login.</code></pre>
<p>Result: the <code>feature/login</code> branch now 'looks like' it
branched from the latest version of main. History becomes linear.
Good for 'cleaning up' the PR before merging.</p>
<p><strong>GOLDEN RULE</strong>: never rebase history that's already
shared. If you rebased commits that other people already have, the
next time they pull, they'll get a conflict (or worse, they'll
re-introduce the old commits).</p>
<p>Interactive rebase is powerful for 'rewriting' local commits before
the push:</p>
<pre><code>$ git rebase -i HEAD~5
pick a1b2c3 feat(api): novo endpoint
squash d4e5f6 fix typo
squash 7g8h9i wip
reword 0j1k2l adiciona testes
drop 3m4n5o commit acidental</code></pre>
<h4>5.4 Cherry-pick</h4>
<p>Applies a specific commit onto another branch:</p>
<pre><code>$ git checkout release-1.28
$ git cherry-pick a1b2c3   # backport do fix
$ git push origin release-1.28</code></pre>
<p>The classic pattern for backporting an urgent fix onto an old
release branch without bringing in all of main's features.</p>

<h3>6. Recovery: how to save yourself from almost anything</h3>
<h4>6.1 reflog: the safety rope</h4>
<p><code>git reflog</code> keeps a <em>local</em> record of every
movement of <code>HEAD</code> (and of each branch) for 90 days by
default. Even after <code>git reset --hard</code>, <code>git
rebase</code>, or deleting a branch, the commits are still there.</p>
<pre><code>$ git reflog
abc1234 HEAD@{0}: reset: moving to HEAD~3
def5678 HEAD@{1}: commit: feat: nova feature crítica
...
$ git reset --hard def5678   # voltei para o estado anterior</code></pre>
<h4>6.2 stash</h4>
<p>Archives uncommitted changes to resume later:</p>
<pre><code>$ git stash push -m 'wip do refactor'
$ git stash list
stash@{0}: On feature/x: wip do refactor
$ git stash pop   # retoma e remove da pilha
$ git stash apply stash@{0}   # aplica sem remover</code></pre>
<h4>6.3 revert: a safe undo on main</h4>
<p>Creates a <em>new</em> commit that reverses the previous one. It
doesn't rewrite history, so it can be used on main without affecting
anyone:</p>
<pre><code>$ git revert abc1234
[main 7g8h9i] Revert 'feat: feature ruim'</code></pre>
<h4>6.4 reset: be careful on shared branches</h4>
<p><code>git reset</code> has 3 modes:</p>
<ul>
<li><code>--soft</code>: moves HEAD, keeps index and working tree.</li>
<li><code>--mixed</code> (default): moves HEAD, resets index, keeps working tree.</li>
<li><code>--hard</code>: moves HEAD, resets index and working tree (dangerous!).</li>
</ul>
<p>On a local branch: fine. On a shared branch: NEVER combined with
force-push, except in an emergency (and with a heads-up to the team).</p>
<h4>6.5 bisect: bug hunting via binary search</h4>
<p>When a bug showed up 'somewhere in the last 200 commits', use:</p>
<pre><code>$ git bisect start
$ git bisect bad HEAD          # commit atual está quebrado
$ git bisect good v1.0         # esta tag estava ok
Bisecting: 100 revisions left to test
$ # roda teste; se passa: git bisect good; se falha: git bisect bad
$ git bisect run pytest test_login.py    # automatiza!</code></pre>
<p>In about 7 steps you land on the bad commit out of 200. In large
projects (the Linux kernel), bisect is how maintainers hunt down
regressions.</p>

<h3>7. Common anti-patterns (and how to avoid them)</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Never force-push to main/protected branches</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Keep PRs small and focused (not 3000 lines)</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Sign commits and require green checks</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Use reflog before panicking after a reset</p></div>
  </div>
  <figcaption>Anti-chaos checklist for production Git.</figcaption>
</figure>

<ul>
<li><strong>'The 3000-line PR'</strong>: nobody really reviews it.
Break it into smaller PRs, or accept that it will be a rubber stamp.</li>
<li><strong>'Force push to main to hide a mistake'</strong>: the
GitHub/GitLab audit log keeps it. You only hide it from yourself. Do a
<code>revert</code> instead.</li>
<li><strong>'One massive "initial commit"'</strong>: no history means
no bisect, no useful blame. Make small commits from day 0.</li>
<li><strong>'.gitignore after committing a secret'</strong>: the
secret stays in history forever. The only real fix is to rotate the
secret immediately. Removing it from history (BFG, git filter-repo)
is theater — forks/clones already exist.</li>
<li><strong>'Committing giant files'</strong>: repos fill up fast. Use
Git LFS for media/binaries (&gt;10MB).</li>
<li><strong>'Long-lived branches (weeks/months)'</strong>: guaranteed
merge hell. Merge main back into the branch frequently.</li>
</ul>

<h3>8. Real case: the Sunday force-push</h3>
<p>Company X. Sunday, 10am. A dev on call sees that an accidental
merge broke main. They run <code>git reset --hard HEAD~3</code>
and <code>git push --force origin main</code>. Did that solve it? No:</p>
<ul>
<li>The other 30 devs on Monday start pulling/cloning and hitting
strange conflicts.</li>
<li>The CI/CD that caches artifacts by SHA is left stranded, the SHA
no longer exists.</li>
<li>Tags that pointed to those commits disappeared from view (but
they're in the reflog).</li>
<li>Compliance audit: '...you just rewrote 3 production commits with
no traceability.'</li>
</ul>
<p>Lesson: <em>never</em> use force-push on main. Use revert.
Configure branch protection to make that impossible, even for
admins.</p>""",
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Configure SSH signing key local + GitHub. Verifique commits aparecem "
                    "como 'Verified'.</li>"
                    "<li>Em um repo pessoal, configure branch protection em <code>main</code>: "
                    "PR obrigatório, 1 review, status checks (CI básico), bloquear force-push, "
                    "linear history, signed commits.</li>"
                    "<li>Crie um PR com 5 commits: 'wip', 'fix typo', 'feat: real', 'wip 2', "
                    "'fix lint'. Faça <code>git rebase -i HEAD~5</code> para squashar/reordenar "
                    "tornando 1 ou 2 commits semânticos.</li>"
                    "<li>Push -force-with-lease no branch (não em main). Verifique que main "
                    "está protegida, tente <code>git push -f origin main</code> e veja a "
                    "rejeição.</li>"
                    "<li>Mergeie via squash. Confira histórico em main: "
                    "<code>git log --oneline --graph --all</code>.</li>"
                    "<li>Simule incidente: faça commit ruim em main local, depois recupere "
                    "via <code>reflog</code> sem perder dado.</li>"
                    "<li>Bonus: configure <code>commitlint</code> + Husky para validar "
                    "Conventional Commits localmente; <code>release-please</code> para "
                    "gerar changelog/versionamento automático no GitHub Actions.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Full hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>Configure a local SSH signing key + GitHub. Verify commits show up "
                    "as 'Verified'.</li>"
                    "<li>In a personal repo, configure branch protection on <code>main</code>: "
                    "required PR, 1 review, status checks (basic CI), block force-push, "
                    "linear history, signed commits.</li>"
                    "<li>Create a PR with 5 commits: 'wip', 'fix typo', 'feat: real', 'wip 2', "
                    "'fix lint'. Run <code>git rebase -i HEAD~5</code> to squash/reorder it "
                    "into 1 or 2 semantic commits.</li>"
                    "<li>Push force-with-lease on the branch (not on main). Verify main is "
                    "protected, try <code>git push -f origin main</code> and see the "
                    "rejection.</li>"
                    "<li>Merge via squash. Check main's history: "
                    "<code>git log --oneline --graph --all</code>.</li>"
                    "<li>Simulate an incident: make a bad commit on local main, then recover "
                    "via <code>reflog</code> without losing data.</li>"
                    "<li>Bonus: configure <code>commitlint</code> + Husky to validate "
                    "Conventional Commits locally; <code>release-please</code> to generate "
                    "an automatic changelog/version bump in GitHub Actions.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("Pro Git Book", "https://git-scm.com/book/en/v2", "book", "A referência.",
                  title_en="Pro Git Book", description_en="The reference."),
                m("Atlassian Gitflow", "https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow", "article", "",
                  title_en="Atlassian Gitflow", description_en=""),
                m("GitHub Branch Protection", "https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches", "docs", "",
                  title_en="GitHub Branch Protection", description_en=""),
                m("Trunk Based Development", "https://trunkbaseddevelopment.com/", "article", "",
                  title_en="Trunk Based Development", description_en=""),
                m("Conventional Commits", "https://www.conventionalcommits.org/", "article", "",
                  title_en="Conventional Commits", description_en=""),
                m("Oh Shit, Git!?!", "https://ohshitgit.com/", "article",
                  "Receitas para sair de roubadas comuns.",
                  title_en="Oh Shit, Git!?!", description_en="Recipes for getting out of common Git messes."),
            ],
            "questions": [
                q("`git rebase` faz:",
                  "Reaplica commits sobre outra base reescrevendo histórico.",
                  ["Faz merge preservando cada commit exatamente como já estava no branch.",
                   "Apaga o branch inteiro junto com o histórico inteiro associado a ele.",
                   "Sincroniza o repositório local com o remoto, sem alterar commit."],
                  "Rebase gera novos hashes; não use em história já compartilhada.",
                  statement_en="`git rebase` does:",
                  correct_en="Reapplies commits onto another base, rewriting history.",
                  wrong_en=["Merges while preserving each commit exactly as it was on the branch.",
                            "Deletes the entire branch along with its whole associated history.",
                            "Syncs the local repository with the remote one, without touching any commit."],
                  explanation_en="Rebase generates new hashes; don't use it on history that's already shared."),
                q("Por que evitar force push em main?",
                  "Pode reescrever história compartilhada e quebrar o time.",
                  ["É mais lento que um push comum, mas funciona normalmente.",
                   "É ilegal em muitos contextos corporativos regulados por auditoria.",
                   "Não funciona em repositório hospedado especificamente no GitHub."],
                  "Qualquer dev com a história anterior fica desincronizado e pode perder commits.",
                  statement_en="Why avoid force-pushing to main?",
                  correct_en="It can rewrite shared history and break the team's work.",
                  wrong_en=["It's slower than a regular push, but still works fine otherwise.",
                            "It's illegal in many corporate contexts regulated by audit rules.",
                            "It simply doesn't work on a repository hosted specifically on GitHub."],
                  explanation_en="Any dev with the previous history becomes out of sync and can lose commits."),
                q("Signed commits servem para:",
                  "Provar autoria via GPG/SSH.",
                  ["Acelerar o push para o repositório remoto configurado.",
                   "Substituir a necessidade de criar um branch separado.",
                   "Comprimir o tamanho de cada commit antes de enviar."],
                  "Evita spoofing, atacante consegue dizer 'commit do CTO' sem assinatura. Com GPG, GitHub mostra 'Verified'.",
                  statement_en="Signed commits are used to:",
                  correct_en="Prove authorship via GPG/SSH.",
                  wrong_en=["Speed up the push to the configured remote repository.",
                            "Replace the need to create a separate branch for the work.",
                            "Compress the size of each commit before sending it."],
                  explanation_en="Prevents spoofing — without a signature, an attacker can claim a commit is 'from the CTO'. With GPG, GitHub shows 'Verified'."),
                q("Em PR, o que é review obrigatório?",
                  "Regra que exige aprovação humana antes do merge.",
                  ["Bloqueia o repositório inteiro para qualquer nova alteração.",
                   "Conta automaticamente como um deploy feito em produção.",
                   "Pula a execução do CI configurado para aquele repositório."],
                  "Combinada com CODEOWNERS, garante que pessoas certas sejam ouvidas.",
                  statement_en="In a PR, what does a required review mean?",
                  correct_en="A rule requiring human approval before the merge happens.",
                  wrong_en=["It locks the entire repository against any new change.",
                            "It automatically counts as a deploy made to production.",
                            "It skips running the CI configured for that repository."],
                  explanation_en="Combined with CODEOWNERS, it guarantees the right people get heard."),
                q("Diferença entre merge e rebase:",
                  "Merge preserva história; rebase a reescreve linearmente.",
                  ["Os dois comandos são idênticos, sem diferença real entre eles.",
                   "O rebase é mais lento de executar do que um merge comum.",
                   "O merge apaga o commit mais antigo do branch de origem."],
                  "Escolha conforme política do time. Misturar pode confundir o histórico.",
                  statement_en="Difference between merge and rebase:",
                  correct_en="Merge preserves history; rebase rewrites it linearly.",
                  wrong_en=["The two commands are identical, with no real difference between them.",
                            "Rebase is slower to run than a regular merge operation.",
                            "Merge deletes the oldest commit from the source branch."],
                  explanation_en="Pick one based on team policy. Mixing them can confuse the history."),
                q("`.gitignore` serve para:",
                  "Listar arquivos a não rastrear (ex.: .env).",
                  ["Apagar o histórico de commit já registrado no repositório inteiro.",
                   "Bloquear um push específico feito para o branch principal.",
                   "Substituir o arquivo LICENSE do projeto por outro modelo."],
                  "Para arquivos já rastreados, é preciso `git rm --cached` antes.",
                  statement_en="`.gitignore` is used to:",
                  correct_en="List files that should not be tracked (e.g. .env).",
                  wrong_en=["Erase commit history already recorded across the entire repository.",
                            "Block a specific push made against the main branch.",
                            "Replace the project's LICENSE file with a different template."],
                  explanation_en="For files already tracked, you need `git rm --cached` first."),
                q("Trunk-based development prefere:",
                  "Branches curtas e merge frequente em main.",
                  ["Branch de vida longa, mantida aberta por semanas ou meses.",
                   "Usar só tag de versão, sem branch de trabalho intermediário.",
                   "Trabalhar sem um branch principal de referência compartilhado."],
                  "Reduz merge hell. Exige feature flags e suite de testes confiável.",
                  statement_en="Trunk-based development prefers:",
                  correct_en="Short-lived branches and frequent merges into main.",
                  wrong_en=["A long-lived branch, kept open for weeks or months at a time.",
                            "Using only version tags, with no intermediate working branch.",
                            "Working without any shared main reference branch at all."],
                  explanation_en="Reduces merge hell. Requires feature flags and a reliable test suite."),
                q("`git stash` faz:",
                  "Salva mudanças locais pendentes para retomar depois.",
                  ["Envia o commit local direto para o repositório remoto configurado.",
                   "Apaga o commit mais recente feito no branch atual.",
                   "Cria um branch novo a partir do commit atual do repositório."],
                  "Stash empilha. Use `git stash pop` para retomar; aplique a branch correta.",
                  statement_en="`git stash` does:",
                  correct_en="Saves pending local changes so you can resume them later.",
                  wrong_en=["Sends the local commit straight to the configured remote repository.",
                            "Deletes the most recent commit made on the current branch.",
                            "Creates a new branch starting from the repository's current commit."],
                  explanation_en="Stash stacks entries. Use `git stash pop` to resume; make sure you apply it to the right branch."),
                q("Conventional Commits é:",
                  "Convenção de mensagens (feat:, fix:, chore:).",
                  ["Um substituto completo para o próprio Git como ferramenta.",
                   "O hash único gerado automaticamente para cada commit novo.",
                   "Um linter que verifica erro de sintaxe dentro do código-fonte."],
                  "Permite gerar changelog e versionamento automático (semver).",
                  statement_en="Conventional Commits is:",
                  correct_en="A message convention (feat:, fix:, chore:).",
                  wrong_en=["A complete substitute for Git itself as a tool.",
                            "The unique hash automatically generated for every new commit.",
                            "A linter that checks for syntax errors inside the source code."],
                  explanation_en="Enables automatic changelog generation and version bumping (semver)."),
                q("Em LFS, arquivos grandes:",
                  "Ficam em storage separado, com pointer no repo.",
                  ["Apagam o histórico de commit anterior relacionado ao arquivo.",
                   "Simplesmente não funcionam dentro de um repositório Git comum.",
                   "Ficam compactados dentro de um arquivo zip anexado ao commit."],
                  "Útil para mídia/binários. Repo principal continua leve; LFS é cobrado por banda.",
                  statement_en="In LFS, large files:",
                  correct_en="Live in separate storage, with a pointer left in the repo.",
                  wrong_en=["Erase the previous commit history related to that file.",
                            "Simply don't work at all inside a regular Git repository.",
                            "Get compressed inside a zip file attached to the commit."],
                  explanation_en="Useful for media/binaries. The main repo stays lightweight; LFS storage is billed by bandwidth."),
            ],
        },
        # =====================================================================
        # 3.2 Infraestrutura como Código (Terraform)
        # =====================================================================
        {
            "title": "Infraestrutura como Código (Terraform)",
            "title_en": "Infrastructure as Code (Terraform)",
            "summary": "Criar servidores usando arquivos de configuração versionáveis.",
            "summary_en": "Creating servers using version-controllable configuration files.",
            "lesson": {
                "intro": (
                    "Antes do IaC, infraestrutura era um conjunto de cliques no console que "
                    "ninguém documentava. Quando o servidor caía, descobrir 'como ele tinha "
                    "sido configurado originalmente' era arqueologia. Quando o engenheiro que "
                    "tinha clicado saía da empresa, o conhecimento ia junto. IaC inverte isso: "
                    "infraestrutura é descrita em arquivos versionados no Git, revisada por "
                    "PR e aplicada via pipeline. Reproduzir um ambiente vira "
                    "<code>terraform apply</code>; documentar vira ler o repo. Esta aula "
                    "foca em Terraform, o padrão de fato para IaC multi-cloud, hoje com fork "
                    "open source (OpenTofu) após mudança de licença em 2023."
                ),
                "intro_en": (
                    "Before IaC, infrastructure was a bunch of console clicks nobody ever "
                    "documented. When the server went down, figuring out 'how it was originally "
                    "configured' was archaeology. When the engineer who clicked it into "
                    "existence left the company, the knowledge left with them. IaC flips this "
                    "around: infrastructure is described in files versioned in Git, reviewed via "
                    "PR and applied through a pipeline. Reproducing an environment becomes "
                    "<code>terraform apply</code>; documenting it becomes reading the repo. This "
                    "lesson focuses on Terraform, the de facto standard for multi-cloud IaC, "
                    "today with an open source fork (OpenTofu) after the 2023 license change."
                ),
                "body": (
                """<h3>1. Por que IaC importa de verdade</h3>
<p>Cinco ganhos concretos justificam trocar clique por código. O
primeiro é <strong>reprodutibilidade</strong>: dev, staging e prod saem
literalmente do mesmo código, não de um esforço manual para deixá-los
"parecidos" — um bug em produção vira reproduzível em staging em
segundos, porque o ambiente de staging É o mesmo `apply`. O segundo é
<strong>revisão por PR</strong>: uma mudança em VPC passa pelo mesmo
fluxo de revisão de código de aplicação, com diff explícito, comentário
e aprovação — em vez de alguém clicando direto no console de produção. O
terceiro é <strong>rastreabilidade</strong>: <code>git blame</code> em
<code>main.tf</code> mostra exatamente quem mudou aquele bucket S3 e
por quê, tornando auditoria trivial em vez de arqueologia. O quarto é
<strong>disaster recovery</strong>: se um cluster inteiro for destruído,
<code>terraform apply</code> reconstrói tudo a partir do código —
empresas maduras testam esse cenário deliberadamente em "Game Days". E o
quinto é <strong>compliance</strong>: uma política como "todo bucket deve
ter encryption" deixa de ser um lembrete em wiki e vira regra executável
(Sentinel, OPA, tfsec) que barra o `apply` se violada.</p>
<div class="mermaid">
flowchart LR
    Manual["Clique no console"] --> Drift["Ambientes divergem"]
    IaC["Código versionado"] --> Same["dev = staging = prod"]
    IaC --> PR["Mudança revisada em PR"]
    IaC --> Blame["git blame no recurso"]
</div>


<h3>2. Anatomia do Terraform</h3>
<p>Terraform usa HCL (HashiCorp Configuration Language), uma DSL
declarativa e JSON-like, mas pensada para ser legível por humano:</p>
<pre><code># main.tf
terraform {
  required_version = "&gt;= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~&gt; 5.40" }
  }
  backend "s3" {
    bucket         = "empresa-tfstate-prod"
    key            = "network/main.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Owner       = "platform-team"
      Environment = var.env
      ManagedBy   = "terraform"
    }
  }
}

variable "env"    { type = string }
variable "region" { type = string, default = "us-east-1" }

resource "aws_s3_bucket" "app_data" {
  bucket = "empresa-app-${var.env}-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_versioning" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.app.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket                  = aws_s3_bucket.app_data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "bucket_name" {
  value = aws_s3_bucket.app_data.id
}</code></pre>
<p>Seis conceitos sustentam qualquer arquivo Terraform. Um
<strong>provider</strong> é o plugin que sabe falar com a API de um
sistema específico — aws, azurerm, google, kubernetes, github,
cloudflare, datadog. Um <strong>resource</strong> declara intenção: "eu
quero um bucket S3 chamado X", e o Terraform decide sozinho se precisa
criar, atualizar ou destruir algo, comparando com o state atual. Um
<strong>data source</strong> só LÊ algo que já existe, sem gerenciar seu
ciclo de vida (<code>data "aws_ami" "ubuntu"</code>). Uma
<strong>variable</strong> é o parâmetro de entrada do módulo. Um
<strong>output</strong> expõe um valor depois do apply, para outro
módulo consumir via remote_state. E <strong>locals</strong> são
variáveis derivadas, calculadas dentro do próprio módulo.</p>

<h3>3. Workflow básico: init → plan → apply</h3>
<pre><code>$ terraform init      # baixa providers, configura backend
$ terraform validate  # checa sintaxe
$ terraform fmt -recursive  # formata
$ terraform plan -out=tfplan
Plan: 4 to add, 1 to change, 0 to destroy.
$ terraform apply tfplan</code></pre>
<p>O <strong>plan</strong> é o passo que mais importa nesse fluxo: ele
gera um diff explícito entre o estado atual e o desejado, ANTES de
qualquer mudança real acontecer. Leia esse diff sempre — em CI, o padrão
maduro é rodar plan automaticamente em cada PR e exigir que o output
apareça como comentário (a ferramenta Atlantis automatiza exatamente
isso), para que quem revisa o código também revise o efeito real dele na
infraestrutura antes de aprovar.</p>
<pre><code>terraform plan -target=aws_s3_bucket.app_data   # foco
terraform apply -refresh-only                    # só atualiza state
terraform destroy -target=aws_instance.test       # destruição cirúrgica
terraform state list
terraform state show aws_s3_bucket.app_data
terraform import aws_s3_bucket.legacy bucket-name
terraform graph | dot -Tpng &gt; deps.png
terraform console   # REPL para testar expressões</code></pre>

<h3>4. State é crítico, trate com paranoia</h3>
<div class="mermaid">
flowchart TD
    Plan["terraform plan"] --> Lock["State lock no backend"]
    Lock --> Apply["terraform apply"]
    Apply --> State["Atualiza state remoto"]
    State --> Next["Próximo plan parte do state"]
</div>

<p>O <code>terraform.tfstate</code> é um JSON que mapeia cada
<em>resource do código</em> ao <em>ID real</em> na nuvem. Sem ele, o
Terraform simplesmente "esquece" o que gerencia e não tem como calcular
diff nenhum. E o problema fica pior: esse mesmo arquivo guarda valores
sensíveis em <strong>texto puro</strong> — senha de RDS, chave de IAM —
porque o Terraform precisa desses valores para calcular o próximo plan.
Isso muda completamente como o state deve ser tratado: nunca deve ser
commitado no Git (vá direto para o <code>.gitignore</code>); deve viver
num backend remoto com lock — S3+DynamoDB no lado AWS, GCS no GCP, Azure
Storage no Azure, ou uma plataforma dedicada como Terraform Cloud,
Spacelift ou Atlantis; deve ter encryption at rest habilitada no próprio
backend via KMS/CMEK; deve ter versionamento habilitado no bucket, porque
mais cedo ou mais tarde um state vai corromper e a versão anterior é o
único caminho de volta; deve usar lock de verdade (DynamoDB na AWS, Cloud
Storage no GCP, lock interno no Terraform Cloud) para impedir que dois
`apply` simultâneos corrompam o mesmo arquivo; nunca deve ser editado à
mão — os comandos <code>terraform state mv|rm|replace-provider</code> ou
um re-import existem exatamente para isso; e deve ter acesso restrito em
produção, onde só o CI lê o state real e desenvolvedores usam, no
máximo, uma role de leitura.</p>
<pre><code>terraform {
  backend "s3" {
    bucket         = "empresa-tfstate"
    key            = "prod/network.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-lock"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:111:key/xxx"
  }
}</code></pre>

<h3>5. Módulos: reuso sem copiar-colar</h3>
<p>Um módulo é só uma pasta com inputs (variables), recursos e outputs
— e serve para encapsular um padrão que a empresa inteira reutiliza, em
vez de cada time reinventar a mesma configuração de RDS com pequenas
variações incompatíveis entre si:</p>
<pre><code>modules/
  rds-postgres/
    main.tf       # cria RDS com encryption + backup + parameter group
    variables.tf  # name, allocated_storage, instance_class, vpc_id...
    outputs.tf    # endpoint, port, secret_arn
    README.md     # como usar</code></pre>
<pre><code>module "app_db" {
  source  = "git::https://github.com/empresa/tf-modules.git//rds-postgres?ref=v1.4.0"
  name    = "app-prod"
  vpc_id  = data.aws_vpc.main.id
  size    = "db.r5.large"
}

output "db_endpoint" {
  value = module.app_db.endpoint
}</code></pre>
<p>Um módulo bem mantido versiona com tags semver do Git
(<code>v1.0.0</code>, <code>v1.4.0</code>), permanece pequeno e
composável em vez de virar um "megamódulo" que tenta fazer tudo, traz um
README com exemplo real de uso e tabela de inputs/outputs — gerada
automaticamente pelo <code>terraform-docs</code> — e tem testes de
verdade, com <code>terratest</code> ou <code>kitchen-terraform</code>,
em vez de confiar que "sempre funcionou até agora".</p>

<h3>6. Variáveis, locals e data sources</h3>
<pre><code>variable "env" {
  type        = string
  description = "Ambiente (dev/staging/prod)"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.env)
    error_message = "env deve ser dev, staging ou prod."
  }
}

variable "db_password" {
  type      = string
  sensitive = true   # esconde de outputs/logs
}

locals {
  is_prod   = var.env == "prod"
  instance  = local.is_prod ? "db.r5.large" : "db.t3.medium"
  multi_az  = local.is_prod
  tags = merge(
    var.tags,
    { Env = var.env, ManagedBy = "terraform" }
  )
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]   # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}</code></pre>
<p>O bloco <code>validation</code> na variável <code>env</code> é o que
transforma um typo ("prd" em vez de "prod") de um bug silencioso
descoberto só depois do apply em um erro imediato, ainda na fase de
plan. E marcar <code>db_password</code> como <code>sensitive = true</code>
não criptografa nada — só instrui o Terraform a mascarar aquele valor
em qualquer output de log ou console, evitando que ele vaze
acidentalmente num histórico de CI.</p>

<h3>7. Drift: realidade ≠ código</h3>
<p>Drift acontece quando alguém muda algo manualmente no console,
fazendo a infraestrutura real divergir silenciosamente do que o código
descreve. O próprio <code>terraform plan</code> detecta isso, porque ele
sempre compara o estado REAL (consultado via API) contra o desejado, não
apenas o state salvo:</p>
<pre><code>$ terraform plan
# aws_security_group.web has been changed
  ~ ingress {
      - cidr_blocks = ["10.0.0.0/8"]   # removido manualmente!
      + cidr_blocks = ["10.0.0.0/8", "0.0.0.0/0"]
  }</code></pre>
<p>Três estratégias mitigam drift antes que ele vire incidente: um job
noturno de CI rodando <code>terraform plan</code> e alertando se houver
qualquer diferença; uma SCP ou Azure Policy bloqueando mudança manual em
produção, deixando devs com acesso só de leitura; ou uma ferramenta
dedicada de detecção contínua, como Driftctl ou AWS Config rules. Quando
um recurso já existe fora do Terraform e precisa ser "oficializado", o
caminho é import — na forma clássica via CLI, ou de forma declarativa a
partir do Terraform 1.5+:</p>
<pre><code># Forma clássica (CLI)
terraform import aws_s3_bucket.legacy meu-bucket-existente

# Terraform 1.5+: import block declarativo
import {
  to = aws_s3_bucket.legacy
  id = "meu-bucket-existente"
}</code></pre>

<h3>8. Boas práticas de produção</h3>
<p>Ambientes separados evitam que um `apply` de dev afete produção por
engano — via workspaces (mesmo backend, prefixo de key diferente, mais
frágil em produção) ou, preferido por muitos times, diretórios
separados (<code>envs/dev/</code>, <code>envs/prod/</code>) ou
Terragrunt. O arquivo <code>.terraform.lock.hcl</code> deve sempre ser
commitado — ele fixa o hash exato de cada provider, evitando que um
`init` em outra máquina baixe uma versão ligeiramente diferente e
produza um plan inesperado. Lint e scan de segurança (tflint, tfsec,
checkov) rodando em CI pegam erro de configuração antes do plan, não
depois do incidente. Plan no PR deve ser obrigatório — Atlantis ou
GitHub Actions comentando o output automaticamente — com apply liberado
só após review humano e aprovação explícita. Apply automático deve
acontecer só a partir de main, e mesmo assim com lock e aprovação humana
extra em produção. Tags obrigatórias (Owner, Environment, CostCenter,
ManagedBy) via <code>default_tags</code> no provider, reforçadas por
Sentinel ou OPA, tornam rastreamento de custo e responsabilidade
possível em escala. Preferir <code>for_each</code> a <code>count</code>
em recursos críticos evita que remover um item do meio de uma lista
force a recriação de todos os itens seguintes — <code>for_each</code>
usa chaves estáveis, <code>count</code> usa índice posicional. E apply
com <code>-target</code> deve ser exceção, não rotina — usado fora de
contexto, ele tende a acumular drift em vez de resolver.</p>

<h3>9. Pipeline de Terraform com GitHub Actions</h3>
<pre><code>name: terraform
on:
  pull_request:
    paths: ['envs/**', 'modules/**']
  push:
    branches: [main]
permissions:
  id-token: write   # OIDC
  contents: read
  pull-requests: write
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111:role/gh-actions-tf
          aws-region: us-east-1
      - uses: hashicorp/setup-terraform@v3
        with: { terraform_version: 1.7.5 }
      - run: terraform fmt -check -recursive
      - run: terraform init
      - run: terraform validate
      - run: tflint --recursive
      - run: tfsec .
      - run: terraform plan -out=tfplan
      - uses: actions/upload-artifact@v4
        with: { name: tfplan, path: tfplan }
  apply:
    needs: plan
    if: github.ref == 'refs/heads/main'
    environment: production   # gate manual
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: ..., aws-region: us-east-1 }
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - uses: actions/download-artifact@v4
        with: { name: tfplan }
      - run: terraform apply tfplan</code></pre>
<p>Note o uso de <code>id-token: write</code> combinado com
<code>configure-aws-credentials</code>: isso é OIDC — o GitHub Actions
troca um token de curta duração diretamente com a AWS via federação,
sem nenhuma chave de acesso de longa duração armazenada em segredo do
repositório. E o gate <code>environment: production</code> no job de
apply é o que exige aprovação manual explícita antes de qualquer mudança
real em produção, mesmo depois do plan já ter passado.</p>

<h3>10. OpenTofu, Pulumi, CDK: alternativas</h3>
<p>Depois da HashiCorp mudar a licença do Terraform para BSL em 2023,
a comunidade fez um fork open source — <strong>OpenTofu</strong> —
compatível com os módulos já existentes e mantido pela Linux Foundation;
para muitos times, virou o default de facto. <strong>Pulumi</strong>
segue caminho diferente: IaC escrita em linguagem de programação real
(Python, TypeScript, Go), com loop, condicional e classe nativos — mais
poder de expressão, ao custo de menos restrição, o que pode virar
bagunça se mal arquitetado, já que HCL força um estilo mais declarativo
e limitado por design. <strong>CDK</strong> (tanto o AWS CDK quanto o
CDKTF) gera CloudFormation ou HCL a partir de código, oferecendo boa
abstração com lock-in moderado na ferramenta escolhida. E
<strong>Crossplane</strong> declara infraestrutura como Custom Resources
do próprio Kubernetes, encaixando bem em times que já são K8s-first e
preferem manter tudo dentro do mesmo control plane.</p>

<h3>11. Anti-patterns comuns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Evite</strong><p>State local, secrets no .tf, apply sem plan, módulos gigantes sem versão.</p></div>
    <div class="lesson-viz-card"><strong>Prefira</strong><p>Backend remoto + lock, variáveis sensíveis fora do código, plan no CI, módulos versionados.</p></div>
  </div>
  <figcaption>Anti-patterns de Terraform em produção.</figcaption>
</figure>

<ul>
<li><strong>tfstate no Git</strong>: vazamento de senha garantido, dado
que o state guarda segredo em texto puro (seção 4).</li>
<li><strong>Editar console e esquecer de importar</strong>: drift cresce
silenciosamente até virar incidente (seção 7).</li>
<li><strong>Módulo gigante "rules-them-all"</strong>: quase impossível
de testar e depurar, o oposto do módulo pequeno e composável da seção
5.</li>
<li><strong>Apply local em produção</strong>: sem revisão, sem
auditoria — force sempre pelo pipeline (seção 9).</li>
<li><strong>Hardcode de região ou conta</strong>: use variável com
default explícito em vez de valor fixo espalhado pelo código.</li>
<li><strong>Esquecer <code>sensitive = true</code></strong> em senha,
deixando-a vazar em log de CI ou output de plan.</li>
<li><strong>Provider sem version constraint</strong>: quebra em deploy
aleatório quando uma nova versão muda comportamento sem aviso.</li>
</ul>"""
                ),
                "body_en": """<h3>1. Why IaC really matters</h3>
<p>Five concrete gains justify swapping clicks for code. The first is
<strong>reproducibility</strong>: dev, staging and prod come
literally from the same code, not from a manual effort to make them
"look alike" — a production bug becomes reproducible in staging in
seconds, because the staging environment IS the same `apply`. The
second is <strong>PR review</strong>: a change to a VPC goes through
the same code review flow as application code, with an explicit diff,
comments and approval — instead of someone clicking directly in the
production console. The third is <strong>traceability</strong>:
<code>git blame</code> on <code>main.tf</code> shows exactly who
changed that S3 bucket and why, turning audit into something trivial
instead of archaeology. The fourth is <strong>disaster recovery</strong>:
if an entire cluster gets destroyed, <code>terraform apply</code>
rebuilds everything from code — mature companies deliberately test
this scenario in "Game Days". And the fifth is <strong>compliance</strong>:
a policy like "every bucket must have encryption" stops being a wiki
reminder and becomes an enforceable rule (Sentinel, OPA, tfsec) that
blocks the `apply` if violated.</p>
<div class="mermaid">
flowchart LR
    Manual["Click in the console"] --> Drift["Environments diverge"]
    IaC["Versioned code"] --> Same["dev = staging = prod"]
    IaC --> PR["Change reviewed in a PR"]
    IaC --> Blame["git blame on the resource"]
</div>


<h3>2. Anatomy of Terraform</h3>
<p>Terraform uses HCL (HashiCorp Configuration Language), a
declarative, JSON-like DSL, but designed to be human-readable:</p>
<pre><code># main.tf
terraform {
  required_version = "&gt;= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~&gt; 5.40" }
  }
  backend "s3" {
    bucket         = "empresa-tfstate-prod"
    key            = "network/main.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Owner       = "platform-team"
      Environment = var.env
      ManagedBy   = "terraform"
    }
  }
}

variable "env"    { type = string }
variable "region" { type = string, default = "us-east-1" }

resource "aws_s3_bucket" "app_data" {
  bucket = "empresa-app-${var.env}-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_versioning" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.app.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket                  = aws_s3_bucket.app_data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "bucket_name" {
  value = aws_s3_bucket.app_data.id
}</code></pre>
<p>Six concepts underpin any Terraform file. A
<strong>provider</strong> is the plugin that knows how to talk to a
specific system's API — aws, azurerm, google, kubernetes, github,
cloudflare, datadog. A <strong>resource</strong> declares intent: "I
want an S3 bucket called X", and Terraform decides on its own whether
it needs to create, update or destroy something, comparing against the
current state. A <strong>data source</strong> only READS something
that already exists, without managing its lifecycle (<code>data
"aws_ami" "ubuntu"</code>). A <strong>variable</strong> is the
module's input parameter. An <strong>output</strong> exposes a value
after apply, for another module to consume via remote_state. And
<strong>locals</strong> are derived variables, computed inside the
module itself.</p>

<h3>3. Basic workflow: init → plan → apply</h3>
<pre><code>$ terraform init      # baixa providers, configura backend
$ terraform validate  # checa sintaxe
$ terraform fmt -recursive  # formata
$ terraform plan -out=tfplan
Plan: 4 to add, 1 to change, 0 to destroy.
$ terraform apply tfplan</code></pre>
<p>The <strong>plan</strong> step matters most in this flow: it
generates an explicit diff between the current and desired state,
BEFORE any real change happens. Always read that diff — in CI, the
mature standard is running plan automatically on every PR and
requiring the output to appear as a comment (the Atlantis tool
automates exactly that), so that whoever reviews the code also
reviews its real effect on the infrastructure before approving.</p>
<pre><code>terraform plan -target=aws_s3_bucket.app_data   # foco
terraform apply -refresh-only                    # só atualiza state
terraform destroy -target=aws_instance.test       # destruição cirúrgica
terraform state list
terraform state show aws_s3_bucket.app_data
terraform import aws_s3_bucket.legacy bucket-name
terraform graph | dot -Tpng &gt; deps.png
terraform console   # REPL para testar expressões</code></pre>

<h3>4. State is critical, treat it with paranoia</h3>
<div class="mermaid">
flowchart TD
    Plan["terraform plan"] --> Lock["State lock in backend"]
    Lock --> Apply["terraform apply"]
    Apply --> State["Updates remote state"]
    State --> Next["Next plan starts from state"]
</div>

<p>The <code>terraform.tfstate</code> is a JSON file that maps each
<em>resource in the code</em> to its <em>real ID</em> in the cloud.
Without it, Terraform simply "forgets" what it manages and has no way
to compute any diff. And the problem gets worse: that same file stores
sensitive values in <strong>plain text</strong> — RDS password, IAM
key — because Terraform needs those values to compute the next plan.
This completely changes how state should be treated: it must never be
committed to Git (put it straight into <code>.gitignore</code>); it
must live in a remote backend with locking — S3+DynamoDB on the AWS
side, GCS on GCP, Azure Storage on Azure, or a dedicated platform like
Terraform Cloud, Spacelift or Atlantis; it must have encryption at
rest enabled on the backend itself via KMS/CMEK; it must have
versioning enabled on the bucket, because sooner or later a state will
get corrupted and the previous version is the only way back; it must
use real locking (DynamoDB on AWS, Cloud Storage on GCP, internal lock
on Terraform Cloud) to prevent two simultaneous `apply` runs from
corrupting the same file; it must never be edited by hand — the
commands <code>terraform state mv|rm|replace-provider</code> or a
re-import exist exactly for that; and it must have restricted access
in production, where only CI reads the real state and developers get,
at most, a read-only role.</p>
<pre><code>terraform {
  backend "s3" {
    bucket         = "empresa-tfstate"
    key            = "prod/network.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-lock"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:111:key/xxx"
  }
}</code></pre>

<h3>5. Modules: reuse without copy-paste</h3>
<p>A module is just a folder with inputs (variables), resources and
outputs — and it serves to encapsulate a pattern the whole company
reuses, instead of each team reinventing the same RDS configuration
with small, incompatible variations between them:</p>
<pre><code>modules/
  rds-postgres/
    main.tf       # cria RDS com encryption + backup + parameter group
    variables.tf  # name, allocated_storage, instance_class, vpc_id...
    outputs.tf    # endpoint, port, secret_arn
    README.md     # como usar</code></pre>
<pre><code>module "app_db" {
  source  = "git::https://github.com/empresa/tf-modules.git//rds-postgres?ref=v1.4.0"
  name    = "app-prod"
  vpc_id  = data.aws_vpc.main.id
  size    = "db.r5.large"
}

output "db_endpoint" {
  value = module.app_db.endpoint
}</code></pre>
<p>A well-maintained module versions with semver Git tags
(<code>v1.0.0</code>, <code>v1.4.0</code>), stays small and composable
instead of turning into a "megamodule" that tries to do everything,
carries a README with a real usage example and an inputs/outputs
table — auto-generated by <code>terraform-docs</code> — and has real
tests, with <code>terratest</code> or <code>kitchen-terraform</code>,
instead of trusting that "it's always worked so far".</p>

<h3>6. Variables, locals and data sources</h3>
<pre><code>variable "env" {
  type        = string
  description = "Ambiente (dev/staging/prod)"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.env)
    error_message = "env deve ser dev, staging ou prod."
  }
}

variable "db_password" {
  type      = string
  sensitive = true   # esconde de outputs/logs
}

locals {
  is_prod   = var.env == "prod"
  instance  = local.is_prod ? "db.r5.large" : "db.t3.medium"
  multi_az  = local.is_prod
  tags = merge(
    var.tags,
    { Env = var.env, ManagedBy = "terraform" }
  )
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]   # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}</code></pre>
<p>The <code>validation</code> block on the <code>env</code> variable
is what turns a typo ("prd" instead of "prod") from a silent bug
discovered only after apply into an immediate error, right at the
plan stage. And marking <code>db_password</code> as <code>sensitive =
true</code> doesn't encrypt anything — it only instructs Terraform to
mask that value in any log or console output, preventing it from
accidentally leaking into a CI history.</p>

<h3>7. Drift: reality ≠ code</h3>
<p>Drift happens when someone manually changes something in the
console, making real infrastructure silently diverge from what the
code describes. <code>terraform plan</code> itself detects this,
because it always compares the REAL state (queried via API) against
the desired one, not just the saved state:</p>
<pre><code>$ terraform plan
# aws_security_group.web has been changed
  ~ ingress {
      - cidr_blocks = ["10.0.0.0/8"]   # removido manualmente!
      + cidr_blocks = ["10.0.0.0/8", "0.0.0.0/0"]
  }</code></pre>
<p>Three strategies mitigate drift before it becomes an incident: a
nightly CI job running <code>terraform plan</code> and alerting on any
difference; an SCP or Azure Policy blocking manual changes in
production, leaving devs with read-only access; or a dedicated
continuous-detection tool, like Driftctl or AWS Config rules. When a
resource already exists outside of Terraform and needs to be
"officialized", the path is import — the classic way via CLI, or
declaratively from Terraform 1.5+:</p>
<pre><code># Forma clássica (CLI)
terraform import aws_s3_bucket.legacy meu-bucket-existente

# Terraform 1.5+: import block declarativo
import {
  to = aws_s3_bucket.legacy
  id = "meu-bucket-existente"
}</code></pre>

<h3>8. Production best practices</h3>
<p>Separate environments prevent a dev `apply` from accidentally
hitting production — via workspaces (same backend, different key
prefix, more fragile in production) or, preferred by many teams,
separate directories (<code>envs/dev/</code>, <code>envs/prod/</code>)
or Terragrunt. The <code>.terraform.lock.hcl</code> file must always be
committed — it pins the exact hash of each provider, preventing an
`init` on another machine from pulling a slightly different version
and producing an unexpected plan. Lint and security scanning (tflint,
tfsec, checkov) running in CI catch configuration errors before the
plan, not after the incident. Plan on the PR should be mandatory —
Atlantis or GitHub Actions commenting the output automatically — with
apply gated only after human review and explicit approval. Automatic
apply should only happen from main, and even then with locking and
extra human approval in production. Mandatory tags (Owner,
Environment, CostCenter, ManagedBy) via <code>default_tags</code> on
the provider, reinforced by Sentinel or OPA, make cost and
responsibility tracking possible at scale. Preferring <code>for_each</code>
over <code>count</code> on critical resources prevents removing an
item from the middle of a list from forcing the recreation of every
subsequent item — <code>for_each</code> uses stable keys,
<code>count</code> uses a positional index. And apply with
<code>-target</code> should be the exception, not routine — used out
of context, it tends to accumulate drift instead of resolving it.</p>

<h3>9. Terraform pipeline with GitHub Actions</h3>
<pre><code>name: terraform
on:
  pull_request:
    paths: ['envs/**', 'modules/**']
  push:
    branches: [main]
permissions:
  id-token: write   # OIDC
  contents: read
  pull-requests: write
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111:role/gh-actions-tf
          aws-region: us-east-1
      - uses: hashicorp/setup-terraform@v3
        with: { terraform_version: 1.7.5 }
      - run: terraform fmt -check -recursive
      - run: terraform init
      - run: terraform validate
      - run: tflint --recursive
      - run: tfsec .
      - run: terraform plan -out=tfplan
      - uses: actions/upload-artifact@v4
        with: { name: tfplan, path: tfplan }
  apply:
    needs: plan
    if: github.ref == 'refs/heads/main'
    environment: production   # gate manual
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: ..., aws-region: us-east-1 }
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - uses: actions/download-artifact@v4
        with: { name: tfplan }
      - run: terraform apply tfplan</code></pre>
<p>It's worth highlighting five details of this pipeline that aren't
accidental: <code>concurrency</code> cancels an old run of the same
branch when a new push arrives, avoiding wasted CI minutes on an
already-obsolete commit; <code>permissions</code> follows the
least-privilege principle, granting write only where actually
necessary; OIDC authenticates against AWS with no long-lived key
stored at all; <code>environment: production</code> implements the
manual gate — with an extra secret, wait timer or required reviewer
configurable directly in the GitHub UI; and the Cosign signature in
the build step lets a Kubernetes admission controller verify the
image's integrity before running it.</p>

<h3>10. OpenTofu, Pulumi, CDK: alternatives</h3>
<p>After HashiCorp changed Terraform's license to BSL in 2023, the
community forked an open source project — <strong>OpenTofu</strong> —
compatible with existing modules and maintained by the Linux
Foundation; for many teams, it became the de facto default.
<strong>Pulumi</strong> takes a different path: IaC written in a real
programming language (Python, TypeScript, Go), with native loops,
conditionals and classes — more expressive power, at the cost of less
restriction, which can turn into a mess if poorly architected, since
HCL forces a more declarative, deliberately limited style by design.
<strong>CDK</strong> (both AWS CDK and CDKTF) generates CloudFormation
or HCL from code, offering good abstraction with moderate lock-in to
the chosen tool. And <strong>Crossplane</strong> declares
infrastructure as Kubernetes' own Custom Resources, fitting well in
teams that are already Kubernetes-first and prefer to keep everything
inside the same control plane.</p>

<h3>11. Common anti-patterns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Avoid</strong><p>Local state, secrets in .tf, apply without plan, giant unversioned modules.</p></div>
    <div class="lesson-viz-card"><strong>Prefer</strong><p>Remote backend + lock, sensitive vars outside code, plan in CI, versioned modules.</p></div>
  </div>
  <figcaption>Terraform anti-patterns in production.</figcaption>
</figure>

<ul>
<li><strong>tfstate in Git</strong>: guaranteed password leak, given
that state stores secrets in plain text (section 4).</li>
<li><strong>Editing the console and forgetting to import</strong>:
drift grows silently until it becomes an incident (section 7).</li>
<li><strong>Giant "rules-them-all" module</strong>: nearly impossible
to test and debug, the opposite of the small, composable module from
section 5.</li>
<li><strong>Local apply in production</strong>: no review, no
audit — always force it through the pipeline (section 9).</li>
<li><strong>Hardcoding a region or account</strong>: use a variable
with an explicit default instead of a fixed value scattered through
the code.</li>
<li><strong>Forgetting <code>sensitive = true</code></strong> on a
password, letting it leak into a CI log or plan output.</li>
<li><strong>Provider without a version constraint</strong>: breaks on
a random deploy when a new version changes behavior without
warning.</li>
</ul>""",
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Configure backend remoto S3+DynamoDB com encryption, versionamento "
                    "e bucket policy negando deleção sem MFA.</li>"
                    "<li>Crie um módulo <code>s3-secure-bucket</code> com: versionamento, "
                    "encryption KMS, public access block, lifecycle (mover para IA após 30d).</li>"
                    "<li>Use o módulo em dois ambientes (<code>envs/dev</code> e "
                    "<code>envs/staging</code>) com tfvars diferentes.</li>"
                    "<li>Configure <code>tflint</code> + <code>tfsec</code> em pre-commit "
                    "e em CI (GitHub Actions com OIDC para AWS).</li>"
                    "<li>Faça plan, apply, depois mude algo no console manualmente. Rode "
                    "plan novamente e veja o drift. Use <code>terraform apply -refresh-only</code> "
                    "ou re-aplique para reconciliar.</li>"
                    "<li>Importe um recurso pré-existente usando <code>import</code> block.</li>"
                    "<li>Bonus: configure Atlantis (ou GitHub Actions) para postar plan no "
                    "comentário do PR e exigir 'apply' como comando manual.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Full hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>Configure a remote S3+DynamoDB backend with encryption, versioning "
                    "and a bucket policy denying deletion without MFA.</li>"
                    "<li>Create an <code>s3-secure-bucket</code> module with: versioning, "
                    "KMS encryption, public access block, lifecycle (move to IA after 30d).</li>"
                    "<li>Use the module in two environments (<code>envs/dev</code> and "
                    "<code>envs/staging</code>) with different tfvars.</li>"
                    "<li>Configure <code>tflint</code> + <code>tfsec</code> in pre-commit "
                    "and in CI (GitHub Actions with OIDC for AWS).</li>"
                    "<li>Run plan, apply, then change something manually in the console. Run "
                    "plan again and see the drift. Use <code>terraform apply -refresh-only</code> "
                    "or re-apply to reconcile.</li>"
                    "<li>Import a pre-existing resource using an <code>import</code> block.</li>"
                    "<li>Bonus: configure Atlantis (or GitHub Actions) to post the plan as a "
                    "PR comment and require 'apply' as a manual command.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("Terraform docs", "https://developer.hashicorp.com/terraform/docs", "docs", "",
                  title_en="Terraform docs", description_en=""),
                m("Terraform Up & Running (livro)", "https://www.terraformupandrunning.com/", "book", "",
                  title_en="Terraform Up & Running (book)", description_en=""),
                m("OpenTofu", "https://opentofu.org/", "tool", "Fork open source do Terraform.",
                  title_en="OpenTofu", description_en="Open source fork of Terraform."),
                m("Terragrunt", "https://terragrunt.gruntwork.io/", "tool", "",
                  title_en="Terragrunt", description_en=""),
                m("tflint", "https://github.com/terraform-linters/tflint", "tool", "",
                  title_en="tflint", description_en=""),
                m("Atlantis (Terraform PR automation)", "https://www.runatlantis.io/", "tool", "",
                  title_en="Atlantis (Terraform PR automation)", description_en=""),
            ],
            "questions": [
                q("`terraform plan` faz:",
                  "Calcula diff entre estado e desejado, sem aplicar.",
                  ["Aplica a mudança direto no provedor, sem mostrar diff antes.",
                   "Apaga o arquivo de estado atual armazenado remotamente.",
                   "Cria uma cópia de backup do estado atual do Terraform."],
                  "Plan gera plano determinístico (que apply vai consumir). Ler atentamente evita surpresas.",
                  statement_en="`terraform plan` does:",
                  correct_en="Calculates the diff between current and desired state, without applying it.",
                  wrong_en=["Applies the change directly to the provider, without showing a diff first.",
                            "Deletes the current state file stored remotely in the backend.",
                            "Creates a backup copy of Terraform's current state file."],
                  explanation_en="Plan generates a deterministic plan (which apply will consume). Reading it carefully avoids surprises."),
                q("Estado remoto serve para:",
                  "Compartilhar entre membros do time com lock.",
                  ["Substitui a necessidade de configurar IAM na conta.",
                   "Habilita o protocolo HTTPS nas chamadas feitas à API.",
                   "Acelera o tempo de execução do comando plan localmente."],
                  "Sem state remoto, devs apagam o trabalho um do outro. Com lock, só um apply roda por vez.",
                  statement_en="Remote state is used to:",
                  correct_en="Share state between team members with locking.",
                  wrong_en=["Replace the need to configure IAM on the account entirely.",
                            "Enable the HTTPS protocol on calls made to the API.",
                            "Speed up how long the plan command takes to run locally."],
                  explanation_en="Without remote state, devs overwrite each other's work. With locking, only one apply runs at a time."),
                q("Por que NÃO commitar tfstate?",
                  "Pode conter segredos e gera conflito.",
                  ["Falha silenciosamente o comando git ao tentar versionar.",
                   "Não é uma prática permitida pela documentação oficial.",
                   "É um arquivo grande demais para caber no limite do GitHub."],
                  "State guarda valores reais (incluindo passwords). Em git público, vira manchete instantânea.",
                  statement_en="Why should tfstate NOT be committed?",
                  correct_en="It can contain secrets and generates merge conflicts.",
                  wrong_en=["It silently fails the git command whenever you try to version it.",
                            "It's simply not a practice allowed by the official documentation.",
                            "It's a file too large to fit within GitHub's size limit."],
                  explanation_en="State stores real values (including passwords). In a public git repo, it instantly becomes a headline."),
                q("Módulo Terraform serve para:",
                  "Encapsular e reutilizar componentes de infra.",
                  ["Criar uma VPN entre duas redes distintas na nuvem.",
                   "Substituir o provider configurado no bloco terraform.",
                   "Gerar log detalhado de cada execução do comando apply."],
                  "Padroniza configurações da empresa. Versione com tags Git.",
                  statement_en="A Terraform module is used to:",
                  correct_en="Encapsulate and reuse infrastructure components.",
                  wrong_en=["Create a VPN between two distinct networks in the cloud.",
                            "Replace the provider configured in the terraform block.",
                            "Generate a detailed log of every apply command execution."],
                  explanation_en="Standardizes the company's configurations. Version it with Git tags."),
                q("`terraform import` serve para:",
                  "Trazer recurso existente para o estado.",
                  ["Renomear um módulo já existente dentro do código.",
                   "Aplicar um plano previamente gerado pelo comando plan.",
                   "Apagar um recurso já gerenciado pelo estado atual."],
                  "Útil ao migrar de console-feito para IaC. TF 1.5+ tem `import` block declarativo.",
                  statement_en="`terraform import` is used to:",
                  correct_en="Bring an existing resource into the managed state.",
                  wrong_en=["Rename a module that already exists within the code.",
                            "Apply a plan that was previously generated by the plan command.",
                            "Delete a resource that's already managed by the current state."],
                  explanation_en="Useful when migrating from console-made resources to IaC. TF 1.5+ has a declarative `import` block."),
                q("OpenTofu é:",
                  "Fork open source do Terraform mantido pela Linux Foundation.",
                  ["Outro provider oficial mantido diretamente pela HashiCorp original.",
                   "Uma DSL completamente diferente, com pouca relação prévia com o HCL.",
                   "Uma extensão de IDE que só destaca a sintaxe do HCL no editor."],
                  "Criado após mudança de licença do Terraform para BSL. Compatível com módulos existentes.",
                  statement_en="OpenTofu is:",
                  correct_en="An open source fork of Terraform maintained by the Linux Foundation.",
                  wrong_en=["Another official provider maintained directly by HashiCorp itself.",
                            "A completely different DSL, with little prior relation to HCL.",
                            "An IDE extension that only highlights HCL syntax in the editor."],
                  explanation_en="Created after Terraform's license changed to BSL. Compatible with existing modules."),
                q("Para evitar drift:",
                  "Faça plan/apply periodicamente e proíba mudanças manuais.",
                  ["Apague o arquivo de estado ao perceber qualquer divergência.",
                   "Use só o console para fazer qualquer mudança de infraestrutura.",
                   "Edite o tfstate manualmente quando precisar corrigir algo pontual."],
                  "Drift detection em CI noturno é boa prática. Combine com SCPs que bloqueiem mudanças manuais.",
                  statement_en="To avoid drift:",
                  correct_en="Run plan/apply periodically and forbid manual changes.",
                  wrong_en=["Delete the state file whenever you notice any divergence.",
                            "Use only the console to make any infrastructure change at all.",
                            "Edit the tfstate by hand whenever you need to fix something specific."],
                  explanation_en="Nightly drift detection in CI is good practice. Combine it with SCPs that block manual changes."),
                q("Variável sensível em Terraform:",
                  "Marque com sensitive = true.",
                  ["Coloque o valor dentro da description da própria variável.",
                   "Imprima o valor no output, para conferência manual posterior.",
                   "Coloque o valor dentro de um comentário no próprio arquivo."],
                  "Evita que o valor apareça em outputs/log. Combine com TFC/Vault para evitar plaintext no state.",
                  statement_en="A sensitive variable in Terraform:",
                  correct_en="Mark it with sensitive = true.",
                  wrong_en=["Put the value inside the variable's own description field.",
                            "Print the value in the output, for later manual verification.",
                            "Put the value inside a comment within the file itself."],
                  explanation_en="Prevents the value from appearing in outputs/logs. Combine with TFC/Vault to avoid plaintext in state."),
                q("Provider é:",
                  "Plugin que conecta Terraform a uma API (AWS, GCP, etc.).",
                  ["Um tipo específico de variável usado dentro do HCL.",
                   "O hash calculado a partir do plano gerado pelo Terraform.",
                   "O backend responsável por guardar o estado remotamente."],
                  "Existem providers oficiais e da comunidade (Cloudflare, GitHub, K8s, Datadog...).",
                  statement_en="A provider is:",
                  correct_en="The plugin that connects Terraform to an API (AWS, GCP, etc.).",
                  wrong_en=["A specific type of variable used within HCL syntax.",
                            "The hash calculated from the plan Terraform generated.",
                            "The backend responsible for storing state remotely."],
                  explanation_en="There are official and community providers (Cloudflare, GitHub, K8s, Datadog...)."),
                q("Lock em backend remoto evita:",
                  "Dois apply simultâneos corrompendo estado.",
                  ["Custo adicional cobrado pelo provedor de nuvem utilizado.",
                   "Backup automático do estado feito antes de cada apply.",
                   "Importação de um recurso já existente para dentro do estado."],
                  "S3+DynamoDB usa item lock; TFC usa lock interno. Sem isso, race condition no state.",
                  statement_en="Locking on a remote backend prevents:",
                  correct_en="Two simultaneous applies corrupting the state.",
                  wrong_en=["Extra cost charged by the cloud provider being used.",
                            "An automatic backup of state made before every apply.",
                            "Importing an already-existing resource into the state."],
                  explanation_en="S3+DynamoDB uses item locking; TFC uses an internal lock. Without it, race conditions hit the state."),
            ],
        },
        # =====================================================================
        # 3.3 Gestão de Configuração (Ansible)
        # =====================================================================
        {
            "title": "Gestão de Configuração (Ansible)",
            "title_en": "Configuration Management (Ansible)",
            "summary": "Padronizar o que acontece dentro do servidor automaticamente.",
            "summary_en": "Automatically standardizing what happens inside the server.",
            "lesson": {
                "intro": (
                    "Terraform criou o servidor. Agora, quem instala nginx? Quem configura "
                    "fail2ban? Quem aplica hardening de SSH? Quem garante que as 50 máquinas "
                    "todas usam o mesmo timezone? Antes, isso era 'documento no Confluence' "
                    "que ninguém seguia. Resultado: <em>snowflake servers</em>, cada servidor "
                    "único, irreproduzível, e ninguém lembra como configurou. Em incidente, "
                    "pesadelo. Gestão de configuração resolve: descreva o estado desejado, "
                    "uma ferramenta o aplica de forma idempotente. Ansible é o padrão de "
                    "fato hoje, especialmente por ser <em>agentless</em>: nada para instalar "
                    "no host gerenciado, só SSH e Python."
                ),
                "intro_en": (
                    "Terraform created the server. Now, who installs nginx? Who configures "
                    "fail2ban? Who applies SSH hardening? Who makes sure all 50 machines use "
                    "the same timezone? Before, this was 'a document in Confluence' that nobody "
                    "followed. Result: <em>snowflake servers</em>, each server unique, "
                    "irreproducible, and nobody remembers how it was configured. During an "
                    "incident, a nightmare. Configuration management solves this: describe the "
                    "desired state, a tool applies it idempotently. Ansible is the de facto "
                    "standard today, especially for being <em>agentless</em>: nothing to install "
                    "on the managed host, just SSH and Python."
                ),
                "body": (
                """<h3>1. Ansible vs alternativas</h3>
<table>
<tr><th>Ferramenta</th><th>Modelo</th><th>Linguagem</th><th>Notas</th></tr>
<tr><td>Ansible</td><td>Agentless (SSH/WinRM)</td><td>YAML</td><td>Padrão de fato hoje. Curva suave.</td></tr>
<tr><td>Chef</td><td>Agente</td><td>Ruby DSL</td><td>Poderoso, complexo. Mais raro hoje.</td></tr>
<tr><td>Puppet</td><td>Agente</td><td>DSL própria</td><td>Forte em ambientes regulados/grandes.</td></tr>
<tr><td>Salt</td><td>Agente ou agentless</td><td>YAML/Jinja</td><td>Bom em escala (event-driven).</td></tr>
</table>
<p>Ansible se consolidou como padrão por uma combinação simples de
fatores: zero footprint no host gerenciado (nada além de SSH e Python
precisa existir lá, ao contrário de Chef e Puppet que exigem um agente
rodando permanentemente), YAML legível mesmo por quem não escreve
Ansible no dia a dia, uma comunidade enorme via Galaxy, e integração
nativa com as principais nuvens.</p>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Ansible</strong><p>Agentless via SSH/WinRM. YAML. Push. Baixa fricção para começar.</p></div>
    <div class="lesson-viz-card"><strong>Puppet/Chef</strong><p>Agente no host. Modelo pull. Bom em fleets enormes já maduros.</p></div>
  </div>
  <figcaption>Ansible vs alternativas: escolha pelo modelo operacional, não pela moda.</figcaption>
</figure>


<h3>2. Anatomia: inventário, playbooks, módulos, roles</h3>
<h4>2.1 Inventário</h4>
<p>O inventário é a lista de hosts gerenciados, e pode ser estático ou
dinâmico:</p>
<pre><code># inventory.ini
[web]
web1.example.com
web2.example.com

[db]
db1.example.com ansible_user=admin

[prod:children]
web
db

[prod:vars]
env=production</code></pre>
<p>Em ambiente de nuvem, o inventário dinâmico deixa de ser opcional e
vira essencial: em vez de manter uma lista de IP fixa que muda a cada
evento de auto-scaling, um plugin consulta AWS, GCP ou Azure diretamente
e gera o inventário em tempo real, sempre refletindo o estado atual:</p>
<pre><code># aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions: [us-east-1]
filters:
  tag:Environment: production
  instance-state-name: running
keyed_groups:
  - key: tags.Role
    prefix: role</code></pre>
<h4>2.2 Playbook</h4>
<p>Um playbook é o YAML que descreve plays e tasks — o que fazer, em
qual host, em qual ordem:</p>
<pre><code>---
- name: Provisionar servidor web
  hosts: web
  become: yes
  vars:
    nginx_port: 80
  tasks:
    - name: Atualiza apt cache
      ansible.builtin.apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Instala nginx
      ansible.builtin.apt:
        name: nginx
        state: present

    - name: Configura site
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/sites-available/app
        owner: root
        group: root
        mode: '0644'
      notify: reload nginx

    - name: Habilita site
      ansible.builtin.file:
        src: /etc/nginx/sites-available/app
        dest: /etc/nginx/sites-enabled/app
        state: link
      notify: reload nginx

    - name: Garante nginx ativo
      ansible.builtin.systemd:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: reload nginx
      ansible.builtin.systemd:
        name: nginx
        state: reloaded</code></pre>
<p>O par <code>notify</code> + <code>handlers</code> resolve um problema
específico: "recarregue o nginx, mas só se alguma coisa realmente
mudou" — mesmo que várias tasks disparem o mesmo notify, o handler roda
uma única vez, ao final do play inteiro, evitando reload redundante.</p>
<h4>2.3 Módulos</h4>
<p>Cada task chama um <em>módulo</em> específico —
<code>apt</code>, <code>yum</code>, <code>copy</code>,
<code>template</code>, <code>file</code>, <code>lineinfile</code>,
<code>blockinfile</code>, <code>systemd</code>, <code>user</code>,
<code>cron</code>, <code>uri</code>, <code>postgresql_db</code>,
<code>community.docker.docker_container</code>. A propriedade que
diferencia esses módulos de um script shell equivalente é que eles são
idempotentes: chamar o mesmo módulo repetidamente sempre converge para
o mesmo estado, sem efeito colateral cumulativo (seção 3).</p>
<h4>2.4 Roles</h4>
<p>Uma role é a estrutura padrão para reuso de configuração entre
playbooks diferentes:</p>
<pre><code>roles/
  webserver/
    tasks/main.yml
    handlers/main.yml
    templates/nginx.conf.j2
    files/index.html
    vars/main.yml
    defaults/main.yml   # valores padrão (override-friendly)
    meta/main.yml       # dependências, autor</code></pre>
<pre><code>- hosts: web
  roles:
    - role: common
    - role: webserver
      vars:
        nginx_port: 8080</code></pre>

<h3>3. Idempotência: o coração do Ansible</h3>
<div class="mermaid">
flowchart LR
    Run1["Playbook 1ª vez"] --> Desired["Estado desejado"]
    Run2["Playbook 2ª vez"] --> Desired
    Desired --> Ok["Sem mudança se já ok"]
</div>

<p>Idempotência significa que aplicar a mesma configuração N vezes
produz sempre o mesmo estado final, não N efeitos acumulados — essa
propriedade é o que torna Ansible seguro de rodar repetidamente sem
medo, e sustenta três cenários distintos: convergência (rodar num
servidor já configurado não quebra nada, só confirma que já está
certo), CI (um dry-run repetido não causa drift acidental), e
self-healing (um agente periódico consegue manter o estado desejado
sozinho, corrigindo qualquer desvio). Módulos nativos do Ansible
respeitam isso por design:</p>
<pre><code># 1ª vez: instala. Demais: 'ok' (não muda nada)
- ansible.builtin.apt:
    name: nginx
    state: present

# Insere linha SE não existir; idempotente
- ansible.builtin.lineinfile:
    path: /etc/sysctl.conf
    line: 'net.ipv4.ip_forward = 1'
    regexp: '^net.ipv4.ip_forward'</code></pre>
<p>O problema aparece quando é preciso recorrer a
<code>shell</code>/<code>command</code>, que por natureza NÃO são
idempotentes — rodar dá o mesmo efeito toda vez, sem checagem prévia de
estado. A saída é usar <code>creates</code>, <code>removes</code> ou
<code>changed_when</code> para simular idempotência manualmente:</p>
<pre><code>- ansible.builtin.shell: |
    /opt/setup.sh &amp;&amp; touch /var/lib/setup.done
  args:
    creates: /var/lib/setup.done   # só roda se arquivo não existir

- ansible.builtin.command: my-tool status
  register: result
  changed_when: "'CHANGED' in result.stdout"
  failed_when: result.rc &gt; 1</code></pre>

<h3>4. Variáveis: precedência e secrets</h3>
<p>A ordem de precedência determina qual valor vence quando a mesma
variável é definida em mais de um lugar, do menor peso ao maior:
role defaults, depois inventory vars (group_vars/host_vars), depois play
vars, depois task vars, e por fim <code>--extra-vars</code> na linha de
comando, que sempre vence qualquer outro nível. Para segredo, o
<strong>Ansible Vault</strong> criptografa o arquivo inteiro em repouso:</p>
<pre><code>$ ansible-vault create group_vars/prod/secrets.yml
Vault password: ****
$ # editor abre, você escreve em texto, ele criptografa
$ cat group_vars/prod/secrets.yml
$ANSIBLE_VAULT;1.1;AES256
323435...
$ ansible-playbook site.yml --ask-vault-pass</code></pre>
<p>Em produção, o padrão mais maduro é evitar até o Vault e buscar o
segredo diretamente de um gerenciador dedicado no momento da execução,
via lookup:</p>
<pre><code>vars:
  db_password: "{{ lookup('amazon.aws.aws_secret', 'prod/db/password') }}"</code></pre>

<h3>5. Templates Jinja2</h3>
<pre><code># templates/nginx.conf.j2
server {
    listen {{ nginx_port }};
    server_name {{ ansible_fqdn }};

    {% if env == 'production' %}
    ssl_certificate /etc/letsencrypt/live/{{ ansible_fqdn }}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{{ ansible_fqdn }}/privkey.pem;
    {% endif %}

    {% for upstream in upstreams %}
    upstream {{ upstream.name }} {
        {% for srv in upstream.servers %}
        server {{ srv }};
        {% endfor %}
    }
    {% endfor %}
}</code></pre>
<p>Um template Jinja2 permite gerar arquivo de configuração diferente
por ambiente a partir de uma única fonte — o mesmo template produz
config sem SSL em dev e com SSL em produção, controlado inteiramente
pela variável <code>env</code>.</p>

<h3>6. Operação em escala</h3>
<p>Rodar Ansible contra dezenas ou centenas de hosts pede controle mais
fino que "rode em tudo, sempre". A flag <code>--check</code> faz
dry-run sem aplicar nada de fato, e <code>--diff</code> mostra
exatamente qual mudança seria feita em cada arquivo. <code>--limit
web1.example.com</code> restringe a execução a um único host, útil para
testar antes de aplicar em todos. <code>--tags install</code> ou
<code>--skip-tags reboot</code> dão controle granular sobre quais tasks
rodam. O parâmetro <code>forks</code> (padrão 5) controla quantos hosts
são processados em paralelo. A estratégia de execução importa também:
<code>linear</code> (o padrão) espera todos os hosts terminarem cada
task antes de avançar para a próxima, <code>free</code> deixa cada host
seguir seu próprio ritmo independente, e <code>host_pinned</code> fixa
cada host a um worker específico. E <code>serial: 25%</code> implementa
rolling upgrade — aplica em 25% dos hosts por vez, permitindo detectar
problema antes de afetar a frota inteira.</p>

<h3>7. Testes: Molecule + ansible-lint</h3>
<p>O <code>molecule</code> roda uma role dentro de container ou VM
isolada e valida tanto o resultado quanto a idempotência de verdade —
não basta a role "parecer" idempotente, o Molecule roda duas vezes e
confirma que a segunda execução não reporta nenhuma mudança:</p>
<pre><code># molecule/default/molecule.yml
driver:
  name: docker
platforms:
  - name: ubuntu-22
    image: geerlingguy/docker-ubuntu2204-ansible
verifier:
  name: ansible</code></pre>
<pre><code>$ molecule test
# create container, converge (rodar a role), idempotence (rodar de novo,
# verificar que nenhuma task reportou changed=true), verify, destroy</code></pre>
<p>O <code>ansible-lint</code> complementa isso pegando anti-pattern
comum antes mesmo de rodar:</p>
<pre><code>$ ansible-lint roles/webserver
WARNING: name[missing] - All tasks should be named
ERROR: command-instead-of-shell - Use shell only when shell features needed</code></pre>

<h3>8. AWX/Tower e governance</h3>
<p>Em escala, rodar <code>ansible-playbook</code> manualmente a partir
do laptop de alguém vira um problema de governança: quem rodou, quando,
com quais variáveis? AWX (a versão open source) e Ansible Tower (a
versão comercial) resolvem isso com UI centralizada, RBAC, surveys de
variável, agendamento, log de auditoria e integração de gerenciamento
de segredo — tudo rastreável, em vez de depender de disciplina
individual.</p>

<h3>9. Ansible vs Terraform: complementares, não substitutos</h3>
<p>A divisão de responsabilidade segue uma regra simples: Terraform
provisiona o RECURSO na nuvem — VM, VPC, RDS, IAM — num mundo
declarativo que mantém state (aula anterior); Ansible configura o
INTERIOR desse recurso já criado — instalar pacote, fazer deploy de
aplicação, orquestrar comando — num mundo procedural, mas que se
comporta de forma idempotente (seção 3). O padrão mais comum na prática
é Terraform criar a instância EC2, expor o IP como output, e então
Ansible-pull ou uma GitHub Action rodar os playbooks sobre aquele IP
recém-criado. Uma alternativa mais avançada constrói uma AMI "golden"
já pronta com Packer + Ansible, deixando o Terraform apenas instanciar
essa imagem pronta — a escolha entre imagem imutável e servidor mutável
configurado depois é uma decisão arquitetural com implicações reais em
velocidade de deploy e superfície de drift.</p>

<h3>10. Anti-patterns comuns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Não misture shell ad-hoc onde há módulo</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Separe inventário por ambiente</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Teste com Molecule + ansible-lint</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Segredos no Vault/ansible-vault, nunca plain</p></div>
  </div>
  <figcaption>Checklist para playbooks sustentáveis.</figcaption>
</figure>

<ul>
<li><strong>Task sem <code>name</code></strong>: o log da execução fica
impossível de interpretar depois.</li>
<li><strong>Abusar de <code>shell</code>/<code>command</code></strong>:
perde a idempotência que é o ponto central do Ansible (seção 3).</li>
<li><strong>Senha em playbook em texto puro</strong>: use Vault ou
lookup direto num secrets manager (seção 4).</li>
<li><strong>Role sem <code>defaults</code></strong>: obriga quem for
usar a role a adivinhar toda variável necessária, em vez de ter um
valor sensato pronto.</li>
<li><strong>Rodar sempre como root</strong>: use <code>become</code>
apenas nas tasks que realmente exigem privilégio elevado.</li>
<li><strong>Inventário estático gigante em ambiente de nuvem</strong>:
use inventário dinâmico (seção 2.1) para nunca ficar desatualizado.</li>
<li><strong>Nenhum teste automatizado (Molecule)</strong>: cada
execução vira uma incógnita sobre se a role ainda funciona como
esperado.</li>
</ul>"""
                ),
                "body_en": """<h3>1. Ansible vs alternatives</h3>
<table>
<tr><th>Tool</th><th>Model</th><th>Language</th><th>Notes</th></tr>
<tr><td>Ansible</td><td>Agentless (SSH/WinRM)</td><td>YAML</td><td>De facto standard today. Gentle learning curve.</td></tr>
<tr><td>Chef</td><td>Agent</td><td>Ruby DSL</td><td>Powerful, complex. Rarer today.</td></tr>
<tr><td>Puppet</td><td>Agent</td><td>Own DSL</td><td>Strong in regulated/large environments.</td></tr>
<tr><td>Salt</td><td>Agent or agentless</td><td>YAML/Jinja</td><td>Good at scale (event-driven).</td></tr>
</table>
<p>Ansible consolidated itself as the standard through a simple
combination of factors: zero footprint on the managed host (nothing
beyond SSH and Python needs to exist there, unlike Chef and Puppet
which require a permanently running agent), YAML readable even by
someone who doesn't write Ansible every day, a huge community via
Galaxy, and native integration with the major clouds.</p>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Ansible</strong><p>Agentless over SSH/WinRM. YAML. Push. Low friction to start.</p></div>
    <div class="lesson-viz-card"><strong>Puppet/Chef</strong><p>Agent on the host. Pull model. Good for huge mature fleets.</p></div>
  </div>
  <figcaption>Ansible vs alternatives: choose by operating model, not hype.</figcaption>
</figure>


<h3>2. Anatomy: inventory, playbooks, modules, roles</h3>
<h4>2.1 Inventory</h4>
<p>The inventory is the list of managed hosts, and it can be static or
dynamic:</p>
<pre><code># inventory.ini
[web]
web1.example.com
web2.example.com

[db]
db1.example.com ansible_user=admin

[prod:children]
web
db

[prod:vars]
env=production</code></pre>
<p>In a cloud environment, dynamic inventory stops being optional and
becomes essential: instead of maintaining a fixed IP list that changes
with every auto-scaling event, a plugin queries AWS, GCP or Azure
directly and generates the inventory in real time, always reflecting
the current state:</p>
<pre><code># aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions: [us-east-1]
filters:
  tag:Environment: production
  instance-state-name: running
keyed_groups:
  - key: tags.Role
    prefix: role</code></pre>
<h4>2.2 Playbook</h4>
<p>A playbook is the YAML that describes plays and tasks — what to do,
on which host, in what order:</p>
<pre><code>---
- name: Provisionar servidor web
  hosts: web
  become: yes
  vars:
    nginx_port: 80
  tasks:
    - name: Atualiza apt cache
      ansible.builtin.apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Instala nginx
      ansible.builtin.apt:
        name: nginx
        state: present

    - name: Configura site
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/sites-available/app
        owner: root
        group: root
        mode: '0644'
      notify: reload nginx

    - name: Habilita site
      ansible.builtin.file:
        src: /etc/nginx/sites-available/app
        dest: /etc/nginx/sites-enabled/app
        state: link
      notify: reload nginx

    - name: Garante nginx ativo
      ansible.builtin.systemd:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: reload nginx
      ansible.builtin.systemd:
        name: nginx
        state: reloaded</code></pre>
<p>The <code>notify</code> + <code>handlers</code> pair solves a
specific problem: "reload nginx, but only if something actually
changed" — even if several tasks trigger the same notify, the handler
runs only once, at the end of the whole play, avoiding a redundant
reload.</p>
<h4>2.3 Modules</h4>
<p>Each task calls a specific <em>module</em> —
<code>apt</code>, <code>yum</code>, <code>copy</code>,
<code>template</code>, <code>file</code>, <code>lineinfile</code>,
<code>blockinfile</code>, <code>systemd</code>, <code>user</code>,
<code>cron</code>, <code>uri</code>, <code>postgresql_db</code>,
<code>community.docker.docker_container</code>. The property that
distinguishes these modules from an equivalent shell script is that
they are idempotent: calling the same module repeatedly always
converges to the same state, with no cumulative side effect
(section 3).</p>
<h4>2.4 Roles</h4>
<p>A role is the standard structure for reusing configuration across
different playbooks:</p>
<pre><code>roles/
  webserver/
    tasks/main.yml
    handlers/main.yml
    templates/nginx.conf.j2
    files/index.html
    vars/main.yml
    defaults/main.yml   # valores padrão (override-friendly)
    meta/main.yml       # dependências, autor</code></pre>
<pre><code>- hosts: web
  roles:
    - role: common
    - role: webserver
      vars:
        nginx_port: 8080</code></pre>

<h3>3. Idempotency: the heart of Ansible</h3>
<div class="mermaid">
flowchart LR
    Run1["Playbook 1st run"] --> Desired["Desired state"]
    Run2["Playbook 2nd run"] --> Desired
    Desired --> Ok["No change if already ok"]
</div>

<p>Idempotency means applying the same configuration N times always
produces the same final state, not N accumulated effects — this
property is what makes Ansible safe to run repeatedly without fear,
and it underpins three distinct scenarios: convergence (running on an
already-configured server doesn't break anything, it just confirms
it's already correct), CI (a repeated dry-run doesn't cause accidental
drift), and self-healing (a periodic agent can keep the desired state
on its own, correcting any deviation). Ansible's native modules
respect this by design:</p>
<pre><code># 1ª vez: instala. Demais: 'ok' (não muda nada)
- ansible.builtin.apt:
    name: nginx
    state: present

# Insere linha SE não existir; idempotente
- ansible.builtin.lineinfile:
    path: /etc/sysctl.conf
    line: 'net.ipv4.ip_forward = 1'
    regexp: '^net.ipv4.ip_forward'</code></pre>
<p>The problem shows up when you need to resort to
<code>shell</code>/<code>command</code>, which by nature are NOT
idempotent — running them has the same effect every time, with no
prior state check. The way out is using <code>creates</code>,
<code>removes</code> or <code>changed_when</code> to simulate
idempotency manually:</p>
<pre><code>- ansible.builtin.shell: |
    /opt/setup.sh &amp;&amp; touch /var/lib/setup.done
  args:
    creates: /var/lib/setup.done   # só roda se arquivo não existir

- ansible.builtin.command: my-tool status
  register: result
  changed_when: "'CHANGED' in result.stdout"
  failed_when: result.rc &gt; 1</code></pre>

<h3>4. Variables: precedence and secrets</h3>
<p>The precedence order determines which value wins when the same
variable is defined in more than one place, from lowest to highest
weight: role defaults, then inventory vars (group_vars/host_vars),
then play vars, then task vars, and finally <code>--extra-vars</code>
on the command line, which always beats every other level. For
secrets, <strong>Ansible Vault</strong> encrypts the entire file at
rest:</p>
<pre><code>$ ansible-vault create group_vars/prod/secrets.yml
Vault password: ****
$ # editor abre, você escreve em texto, ele criptografa
$ cat group_vars/prod/secrets.yml
$ANSIBLE_VAULT;1.1;AES256
323435...
$ ansible-playbook site.yml --ask-vault-pass</code></pre>
<p>In production, the more mature standard is to avoid even Vault and
fetch the secret directly from a dedicated manager at execution time,
via lookup:</p>
<pre><code>vars:
  db_password: "{{ lookup('amazon.aws.aws_secret', 'prod/db/password') }}"</code></pre>

<h3>5. Jinja2 templates</h3>
<pre><code># templates/nginx.conf.j2
server {
    listen {{ nginx_port }};
    server_name {{ ansible_fqdn }};

    {% if env == 'production' %}
    ssl_certificate /etc/letsencrypt/live/{{ ansible_fqdn }}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{{ ansible_fqdn }}/privkey.pem;
    {% endif %}

    {% for upstream in upstreams %}
    upstream {{ upstream.name }} {
        {% for srv in upstream.servers %}
        server {{ srv }};
        {% endfor %}
    }
    {% endfor %}
}</code></pre>
<p>A Jinja2 template lets you generate a different configuration file
per environment from a single source — the same template produces a
config with no SSL in dev and with SSL in production, controlled
entirely by the <code>env</code> variable.</p>

<h3>6. Operating at scale</h3>
<p>Running Ansible against dozens or hundreds of hosts calls for finer
control than "run on everything, always". The <code>--check</code>
flag does a dry-run without actually applying anything, and
<code>--diff</code> shows exactly which change would be made to each
file. <code>--limit web1.example.com</code> restricts execution to a
single host, useful for testing before applying to everyone.
<code>--tags install</code> or <code>--skip-tags reboot</code> give
granular control over which tasks run. The <code>forks</code>
parameter (default 5) controls how many hosts are processed in
parallel. The execution strategy matters too: <code>linear</code> (the
default) waits for all hosts to finish each task before moving to the
next one, <code>free</code> lets each host proceed at its own
independent pace, and <code>host_pinned</code> pins each host to a
specific worker. And <code>serial: 25%</code> implements a rolling
upgrade — applying to 25% of hosts at a time, letting you detect a
problem before it affects the whole fleet.</p>

<h3>7. Testing: Molecule + ansible-lint</h3>
<p><code>molecule</code> runs a role inside an isolated container or VM
and validates both the result and actual idempotency — it's not enough
for the role to "seem" idempotent, Molecule runs it twice and confirms
that the second run reports no change at all:</p>
<pre><code># molecule/default/molecule.yml
driver:
  name: docker
platforms:
  - name: ubuntu-22
    image: geerlingguy/docker-ubuntu2204-ansible
verifier:
  name: ansible</code></pre>
<pre><code>$ molecule test
# create container, converge (rodar a role), idempotence (rodar de novo,
# verificar que nenhuma task reportou changed=true), verify, destroy</code></pre>
<p><code>ansible-lint</code> complements this by catching common
anti-patterns even before you run anything:</p>
<pre><code>$ ansible-lint roles/webserver
WARNING: name[missing] - All tasks should be named
ERROR: command-instead-of-shell - Use shell only when shell features needed</code></pre>

<h3>8. AWX/Tower and governance</h3>
<p>At scale, running <code>ansible-playbook</code> manually from
someone's laptop becomes a governance problem: who ran it, when, with
which variables? AWX (the open source version) and Ansible Tower (the
commercial version) solve this with a centralized UI, RBAC, variable
surveys, scheduling, audit logging and secret-management
integration — everything traceable, instead of relying on individual
discipline.</p>

<h3>9. Ansible vs Terraform: complementary, not substitutes</h3>
<p>The division of responsibility follows a simple rule: Terraform
provisions the RESOURCE in the cloud — VM, VPC, RDS, IAM — in a
declarative world that keeps state (previous lesson); Ansible
configures the INSIDE of that already-created resource — installing a
package, deploying an application, orchestrating a command — in a
procedural world, but one that behaves idempotently (section 3). The
most common pattern in practice is Terraform creating the EC2
instance, exposing the IP as an output, and then Ansible-pull or a
GitHub Action running the playbooks against that freshly created IP. A
more advanced alternative builds a "golden" AMI already ready with
Packer + Ansible, leaving Terraform to just instantiate that ready
image — the choice between an immutable image and a mutable server
configured afterward is an architectural decision with real
implications for deploy speed and drift surface.</p>

<h3>10. Common anti-patterns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Do not use ad-hoc shell where a module exists</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Split inventory by environment</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Test with Molecule + ansible-lint</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Secrets in Vault/ansible-vault, never plain</p></div>
  </div>
  <figcaption>Checklist for sustainable playbooks.</figcaption>
</figure>

<ul>
<li><strong>Task with no <code>name</code></strong>: makes the
execution log impossible to interpret afterward.</li>
<li><strong>Overusing <code>shell</code>/<code>command</code></strong>:
loses the idempotency that is Ansible's central point (section 3).</li>
<li><strong>Password in plain text in the playbook</strong>: use Vault
or a lookup directly against a secrets manager (section 4).</li>
<li><strong>Role with no <code>defaults</code></strong>: forces
whoever uses the role to guess every required variable, instead of
having a sensible value ready.</li>
<li><strong>Always running as root</strong>: use <code>become</code>
only on tasks that really require elevated privilege.</li>
<li><strong>Giant static inventory in a cloud environment</strong>:
use dynamic inventory (section 2.1) so it never goes stale.</li>
<li><strong>No automated testing (Molecule)</strong>: every run
becomes a question mark over whether the role still works as
expected.</li>
</ul>""",
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Crie role <code>webserver</code> com tasks/handlers/templates/defaults "
                    "que: instala nginx, copia config (template Jinja2), habilita systemd, "
                    "configura logrotate.</li>"
                    "<li>Adicione role <code>hardening</code>: SSH só com chave, fail2ban, "
                    "ufw básico, automatic security updates.</li>"
                    "<li>Use <code>ansible-vault</code> para senha do banco em "
                    "<code>group_vars/prod/secrets.yml</code>.</li>"
                    "<li>Configure inventário dinâmico AWS EC2 com filtros por tag.</li>"
                    "<li>Rode o playbook duas vezes; verifique <code>changed=0</code> na "
                    "segunda (idempotência).</li>"
                    "<li>Configure Molecule com Docker para testar a role em CI.</li>"
                    "<li>Adicione <code>ansible-lint</code> em pre-commit.</li>"
                    "<li>Bonus: AWX em Docker Compose para rodar o playbook por UI com "
                    "survey de variáveis.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Full hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>Create a <code>webserver</code> role with tasks/handlers/templates/defaults "
                    "that: installs nginx, copies config (Jinja2 template), enables systemd, "
                    "configures logrotate.</li>"
                    "<li>Add a <code>hardening</code> role: SSH key-only, fail2ban, "
                    "basic ufw, automatic security updates.</li>"
                    "<li>Use <code>ansible-vault</code> for the DB password in "
                    "<code>group_vars/prod/secrets.yml</code>.</li>"
                    "<li>Configure AWS EC2 dynamic inventory with tag filters.</li>"
                    "<li>Run the playbook twice; verify <code>changed=0</code> on the "
                    "second run (idempotency).</li>"
                    "<li>Configure Molecule with Docker to test the role in CI.</li>"
                    "<li>Add <code>ansible-lint</code> to pre-commit.</li>"
                    "<li>Bonus: AWX on Docker Compose to run the playbook via UI with "
                    "a variable survey.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("Ansible docs", "https://docs.ansible.com/", "docs", "",
                  title_en="Ansible docs", description_en=""),
                m("Ansible Galaxy", "https://galaxy.ansible.com/", "tool", "",
                  title_en="Ansible Galaxy", description_en=""),
                m("Ansible for DevOps (livro)", "https://www.ansiblefordevops.com/", "book", "",
                  title_en="Ansible for DevOps (book)", description_en=""),
                m("ansible-lint", "https://ansible.readthedocs.io/projects/lint/", "tool", "",
                  title_en="ansible-lint", description_en=""),
                m("Molecule (testes)", "https://ansible.readthedocs.io/projects/molecule/", "tool", "",
                  title_en="Molecule (testing)", description_en=""),
                m("AWX (open source Tower)", "https://github.com/ansible/awx", "tool", "",
                  title_en="AWX (open source Tower)", description_en=""),
            ],
            "questions": [
                q("Ansible exige agente nos hosts gerenciados?",
                  "Não, basta SSH e Python.",
                  ["Sim, daemon obrigatório.", "Sim, agente em C.", "Sim, kubelet."],
                  "Em hosts mínimos sem Python, há `raw` module para bootstrap. Em Windows, WinRM.",
                  statement_en="Does Ansible require an agent on managed hosts?",
                  correct_en="No — SSH and Python are enough.",
                  wrong_en=["Yes, a mandatory daemon.", "Yes, a C agent.", "Yes, kubelet."],
                  explanation_en="On minimal hosts without Python, the `raw` module can bootstrap. On Windows, WinRM."),
                q("Idempotência significa:",
                  "Rodar a mesma tarefa N vezes resulta no mesmo estado.",
                  ["Falha imediatamente ao encontrar qualquer laço de repetição.",
                   "Cria um recurso novo a cada execução, mesmo sem mudança real.",
                   "Produz resultado diferente a cada execução, de forma aleatória."],
                  "Permite rodar playbooks com confiança em sistemas já configurados (convergência).",
                  statement_en="Idempotency means:",
                  correct_en="Running the same task N times yields the same state.",
                  wrong_en=["It fails immediately if it finds any kind of loop.",
                            "It creates a new resource on every run, even with no real change.",
                            "It produces a different result every run, at random."],
                  explanation_en="It lets you run playbooks confidently on already-configured systems (convergence)."),
                q("ansible-vault serve para:",
                  "Criptografar arquivos com segredos no repositório.",
                  ["Substituir completamente a necessidade de usar um KMS externo.",
                   "Comprimir o tamanho do playbook antes de rodar no host.",
                   "Compactar log gerado durante a execução do playbook."],
                  "Bom para projetos pequenos. Em escala, prefira lookups para Vault/Secrets Manager.",
                  statement_en="ansible-vault is used to:",
                  correct_en="Encrypt files that hold secrets in the repository.",
                  wrong_en=["Fully replace the need to use an external KMS.",
                            "Shrink the playbook size before it runs on the host.",
                            "Compress logs produced while the playbook runs."],
                  explanation_en="Fine for small projects. At scale, prefer lookups into Vault/Secrets Manager."),
                q("Inventário pode ser:",
                  "Estático (arquivo) ou dinâmico (script/plugin).",
                  ["Só em formato INI, sem suporte a outro tipo de arquivo.",
                   "Só estático, sem possibilidade de gerar inventário dinâmico.",
                   "Só dinâmico, sem possibilidade de declarar host num arquivo."],
                  "Dinâmico é essencial em cloud com auto-scaling, onde IPs mudam.",
                  statement_en="Inventory can be:",
                  correct_en="Static (file) or dynamic (script/plugin).",
                  wrong_en=["INI format only, with no support for other file types.",
                            "Static only, with no way to generate a dynamic inventory.",
                            "Dynamic only, with no way to declare a host in a file."],
                  explanation_en="Dynamic inventory is essential in cloud with auto-scaling, where IPs change."),
                q("Role em Ansible é:",
                  "Conjunto reutilizável de tasks, handlers, templates, etc.",
                  ["Um comando de shell executado diretamente num host remoto.",
                   "Um tipo específico de host dentro do inventário do Ansible.",
                   "Uma política de acesso do IAM aplicada a uma conta na nuvem."],
                  "Estrutura padrão (tasks/, handlers/, defaults/, templates/) facilita compartilhamento.",
                  statement_en="An Ansible role is:",
                  correct_en="A reusable set of tasks, handlers, templates, and related files.",
                  wrong_en=["A shell command run directly on a remote host.",
                            "A specific host type inside the Ansible inventory.",
                            "An IAM access policy applied to a cloud account."],
                  explanation_en="The standard layout (tasks/, handlers/, defaults/, templates/) makes sharing easier."),
                q("Handlers são executados:",
                  "Apenas quando um task notifica e tem mudança.",
                  ["Logo no início, antes de qualquer outra task do playbook.",
                   "De forma aleatória, sem relação com o resultado da task.",
                   "Só quando alguma task anterior termina em erro explícito."],
                  "Padrão clássico: copiar nginx.conf → notify 'restart nginx'. Restart só ocorre se houve mudança.",
                  statement_en="Handlers run:",
                  correct_en="Only when a task notifies them and a change occurred.",
                  wrong_en=["Right at the start, before any other playbook task.",
                            "At random, unrelated to the task outcome.",
                            "Only when some earlier task ends with an explicit error."],
                  explanation_en="Classic pattern: copy nginx.conf → notify 'restart nginx'. Restart only if something changed."),
                q("Diferença entre Ansible e Terraform:",
                  "Ansible foca em config interna; Terraform em provisão de infra.",
                  ["Os dois rodam exclusivamente na máquina local do operador.",
                   "Fazem exatamente a mesma coisa, sem diferença real relevante entre eles.",
                   "Ansible cria a máquina virtual; Terraform configura o que roda dentro dela."],
                  "Não é regra rígida (Ansible cria recursos cloud, Terraform pode configurar). Mas a pegada é essa.",
                  statement_en="Difference between Ansible and Terraform:",
                  correct_en="Ansible focuses on internal config; Terraform on provisioning infra.",
                  wrong_en=["Both run exclusively on the operator's local machine.",
                            "They do exactly the same thing, with no real meaningful difference.",
                            "Ansible creates the VM; Terraform configures what runs inside it."],
                  explanation_en="Not a rigid rule (Ansible can create cloud resources; Terraform can configure). But that's the usual split."),
                q("ansible-lint serve para:",
                  "Detectar más práticas em playbooks.",
                  ["Substituir completamente o próprio Ansible como ferramenta.",
                   "Compilar o arquivo YAML antes de rodar o playbook.",
                   "Publicar a role diretamente no repositório do Galaxy."],
                  "Pega coisas como 'task sem nome', 'shell sem creates', 'sudo redundante'.",
                  statement_en="ansible-lint is used to:",
                  correct_en="Detect bad practices in playbooks.",
                  wrong_en=["Fully replace Ansible itself as a tool.",
                            "Compile the YAML file before running the playbook.",
                            "Publish the role straight to the Galaxy repository."],
                  explanation_en="It catches things like 'unnamed task', 'shell without creates', 'redundant sudo'."),
                q("Modo `--check` faz:",
                  "Dry-run, simulando sem aplicar.",
                  ["Cria uma cópia de backup do host antes de aplicar.",
                   "Reinicia o agente instalado no host gerenciado remotamente.",
                   "Aplica a mudança normalmente, ignorando qualquer erro encontrado."],
                  "Combine com `--diff` para ver o que mudaria. Útil em PR antes de aplicar.",
                  statement_en="`--check` mode does:",
                  correct_en="A dry-run, simulating without applying.",
                  wrong_en=["Create a backup copy of the host before applying.",
                            "Restart the agent installed on the remote managed host.",
                            "Apply the change normally, ignoring any error found."],
                  explanation_en="Combine with `--diff` to see what would change. Useful in a PR before applying."),
                q("Para 100+ hosts paralelos:",
                  "Ajuste forks e use estratégias (free, linear).",
                  ["Reduza a execução a um único host de cada vez.",
                   "Não há forma de paralelizar execução em larga escala.",
                   "Use o cron do sistema operacional para agendar a execução."],
                  "Default fork=5. Aumentar exige memória no controlador. Strategy 'free' não espera todos.",
                  statement_en="For 100+ hosts in parallel:",
                  correct_en="Tune forks and use strategies (free, linear).",
                  wrong_en=["Reduce execution to one host at a time.",
                            "There is no way to parallelize execution at large scale.",
                            "Use the OS cron to schedule the run."],
                  explanation_en="Default forks=5. Raising it needs controller memory. Strategy 'free' does not wait for everyone."),
            ],
        },
        # =====================================================================
        # 3.4 Secret Management
        # =====================================================================
        {
            "title": "Secret Management",
            "title_en": "Secret Management",
            "summary": "Onde guardar senhas que não seja no código (Vault e similares).",
            "summary_en": "Where to store passwords that aren't in code (Vault and similar).",
            "lesson": {
                "intro": (
                    "Em 2022, GitGuardian escaneou 1 bilhão+ commits e encontrou ~10 milhões "
                    "de segredos vazados no GitHub público. Token AWS, key Stripe, senha "
                    "Postgres, JWT secret. Em segundos após push público, bots clonam, "
                    "extraem credenciais e começam a minerar criptomoedas na sua conta. "
                    "Custo médio de incidente: USD 5-50k/dia até detectar. Esta aula é "
                    "sobre como evitar virar manchete: ferramentas, padrões e cultura para "
                    "lidar com segredos. Spoiler: 'colocar em variável de ambiente' não é "
                    "secret management."
                ),
                "intro_en": (
                    "In 2022, GitGuardian scanned 1 billion+ commits and found ~10 million "
                    "secrets leaked on public GitHub. AWS tokens, Stripe keys, Postgres "
                    "passwords, JWT secrets. Within seconds of a public push, bots clone, "
                    "extract credentials, and start mining crypto on your account. "
                    "Average incident cost: USD 5-50k/day until detection. This lesson is "
                    "about how not to become a headline: tools, patterns, and culture for "
                    "handling secrets. Spoiler: 'put it in an environment variable' is not "
                    "secret management."
                ),
                "body": (
                """<h3>1. Tipos de segredos</h3>
<p>Nem todo segredo deve ser tratado do mesmo jeito, e a categoria certa
determina a estratégia de proteção. Os <strong>estáticos</strong> —
senha de banco, API key, token de serviço — são criados manualmente e
mudam pouco; devem ir para um cofre e passar por rotação periódica
mesmo assim, porque "quase nunca muda" não é o mesmo que "nunca precisa
mudar". Os <strong>dinâmicos</strong> invertem o modelo: o próprio
cofre cria a credencial sob demanda, com TTL curto — o Vault, por
exemplo, gera um usuário Postgres temporário com senha aleatória válida
por uma hora e depois a revoga sozinho, minimizando a janela de
exposição a praticamente o tempo de uso real. Os <strong>tokens
efêmeros</strong> (JWT/STS/OIDC) vão além: têm TTL curto e nunca chegam
a existir como armazenamento persistente em lugar nenhum — AssumeRole na
AWS, Workload Identity no GCP, Managed Identity na Azure seguem esse
modelo. E os <strong>certificados</strong> (TLS, mTLS, SSH CA)
tipicamente vivem de 7 a 90 dias e são renovados automaticamente via
ACME ou ferramenta equivalente (Vault PKI, smallstep, cert-manager).</p>
<div class="mermaid">
flowchart TD
    S["Segredos"] --> Static["Estáticos: senha, API key"]
    S --> Dyn["Dinâmicos: gerados sob demanda"]
    S --> Eph["Efêmeros: TTL curto / one-shot"]
    Static --> Vault["Cofre + rotação"]
    Dyn --> Vault
    Eph --> Vault
</div>


<h3>2. Onde NUNCA guardar segredos</h3>
<p>Sete lugares parecem convenientes mas garantem vazamento mais cedo
ou mais tarde. O <strong>Git</strong> — mesmo em repositório privado —
nunca esquece: fork, clone, export e histórico preservam o segredo
indefinidamente, mesmo que o commit seja "revertido" depois. O
<strong>Slack/Teams/Discord</strong> arquiva mensagem em log,
integração e export de e-discovery, muitas vezes retido por anos pela
política de retenção da própria empresa. O <strong>e-mail</strong> tem o
mesmo problema, ainda passando por servidor externo no caminho. Um
<code>ENV</code> ou <code>ARG</code> no <strong>Dockerfile</strong>
grava o segredo direto numa LAYER da imagem — qualquer pessoa com
permissão de pull consegue extrair rodando
<code>docker history image</code>. <strong>Logs</strong> de aplicação ou
de CI acabam retidos por 30 dias ou mais em qualquer SIEM ou SaaS de
observabilidade padrão. Uma variável de ambiente de CI <strong>sem
mask</strong> configurado aparece em texto puro assim que algum step
rodar um <code>echo $VAR</code>, intencional ou não. E até uma extensão
de navegador com <strong>sincronização em nuvem</strong> ativada pode
levar o segredo para fora do controle da empresa sem que ninguém
perceba.</p>

<h3>3. Cofres modernos</h3>
<table>
<tr><th>Cofre</th><th>Pontos fortes</th></tr>
<tr><td>HashiCorp Vault</td><td>Multi-cloud, dynamic secrets, transit, PKI, OIDC. Self-hosted ou Cloud.</td></tr>
<tr><td>AWS Secrets Manager</td><td>Integração nativa AWS, rotação automática RDS, cross-region replication.</td></tr>
<tr><td>AWS Parameter Store</td><td>Mais barato, mais simples; bom para configs e segredos menos críticos.</td></tr>
<tr><td>Azure Key Vault</td><td>Integração Entra ID, HSM-backed.</td></tr>
<tr><td>GCP Secret Manager</td><td>Versionamento, replicação, IAM granular.</td></tr>
<tr><td>1Password / Bitwarden</td><td>Bom para humanos + secret automation (1Password Connect).</td></tr>
<tr><td>Doppler / Infisical</td><td>SaaS pequenos, focados em devex.</td></tr>
</table>

<h3>4. Padrão: nunca leia o cofre direto da app (se possível)</h3>
<div class="mermaid">
sequenceDiagram
    participant App
    participant Platform as Plataforma
    participant Vault as Cofre
    App->>Platform: Sobe com identidade
    Platform->>Vault: Busca segredo
    Vault-->>Platform: Segredo de curta duração
    Platform-->>App: Injeta em runtime
</div>

<p>Fazer a aplicação acessar o cofre diretamente parece simples, mas
exige cliente dedicado, retry, cache, autenticação própria e tratamento
de erro específico — e num incidente do próprio cofre, a aplicação cai
junto, criando um novo ponto único de falha exatamente onde não devia
existir um. Três padrões evitam esse acoplamento direto.</p>
<h4>4.1 Sidecar/Init container injetor</h4>
<p>Um container separado puxa o segredo do cofre e escreve num
arquivo ou volume compartilhado; a aplicação só lê o arquivo, sem
nenhuma lógica de cofre embutida nela mesma. O Vault Agent é o exemplo
clássico desse padrão:</p>
<pre><code># Pod K8s
annotations:
  vault.hashicorp.com/agent-inject: 'true'
  vault.hashicorp.com/role: 'app'
  vault.hashicorp.com/agent-inject-secret-db: 'database/creds/app'</code></pre>
<h4>4.2 Operator no K8s</h4>
<p>O <strong>External Secrets Operator</strong> (ESO) segue o mesmo
espírito, mas de forma nativa ao Kubernetes: você cria um Custom
Resource <code>ExternalSecret</code> apontando para o cofre, e o ESO
popula um <code>Secret</code> nativo no namespace, que a aplicação
consome exatamente como consumiria qualquer Secret comum, sem saber que
a fonte real é externa:</p>
<pre><code>apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: app-db }
spec:
  secretStoreRef: { name: aws-sm, kind: ClusterSecretStore }
  target: { name: app-db-secret }
  data:
    - secretKey: password
      remoteRef: { key: prod/app/db, property: password }</code></pre>
<h4>4.3 OIDC/Workload Identity</h4>
<p>Em pipeline de CI/CD, o ideal é não armazenar segredo NENHUM: o
GitHub Actions emite um JWT efêmero, a AWS valida esse token via OIDC e
devolve uma credencial STS de curta duração — nenhum secret de longa
duração jamais fica salvo no GitHub:</p>
<pre><code>permissions:
  id-token: write
  contents: read
jobs:
  deploy:
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111111111111:role/gh-deployer
          aws-region: us-east-1
      - run: aws s3 sync ./build s3://app-prod   # sem keys!</code></pre>

<h3>5. Rotação</h3>
<p>Uma política comum diferencia rotação por tipo de credencial:
credencial humana (senha, reset de MFA) a cada 90 dias; credencial de
máquina estática entre 30 e 90 dias; credencial crítica (root, chave
mestra de KMS) com cuidado redobrado, mas idealmente a cada 365 dias com
auditoria acompanhando; e qualquer suspeita de vazamento dispara rotação
IMEDIATA, sem esperar o ciclo programado. O Vault com dynamic secrets já
resolve isso "de graça" — o TTL curto É a rotação. Para segredo
estático, a automação é o caminho: o AWS Secrets Manager, uma vez
ativado, roda uma Lambda que cria a senha nova, atualiza o RDS e
atualiza o próprio secret — a aplicação busca via um cache com TTL e
recebe a senha nova automaticamente, sem nenhuma intervenção manual no
momento da troca.</p>

<h3>6. Detecção em PR e em código</h3>
<p>Acidente acontece mesmo com processo bem desenhado — a defesa real
está em ter várias camadas capturando o mesmo erro em pontos
diferentes. O <strong>pre-commit hook</strong> (gitleaks, trufflehog,
detect-secrets) bloqueia o push antes de sair do laptop do
desenvolvedor. O <strong>CI check</strong> pega o que passou pelo
pre-commit pulado — a camada que não tem <code>--no-verify</code>
disponível. O <strong>GitHub Secret Scanning</strong> já vem ativo por
padrão em repositório público (e via Advanced Security em privado),
detecta mais de 200 padrões conhecidos, e em muitos casos notifica o
próprio provedor (AWS, Stripe) que pode revogar a chave automaticamente
antes mesmo de alguém perceber o vazamento. E uma <strong>auditoria
periódica</strong> de repositório antigo com trufflehog ou
gitleaks-search pega o que ficou esquecido de anos atrás, antes dessas
camadas existirem:</p>
<pre><code># .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks</code></pre>

<h3>7. SE um segredo vazou: o que fazer</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Revogue o segredo imediatamente</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Rotacione tudo que compartilhava o mesmo material</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Audite logs de uso no período</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Bloqueie novos commits com secret scan</p></div>
  </div>
  <figcaption>Ordem de resposta quando um segredo vaza.</figcaption>
</figure>

<ol>
<li><strong>Rotacione imediatamente</strong>, mesmo que a resposta
tenha sido só um <code>git rm --cached</code> — o histórico ainda
carrega o valor original, então a única defesa real é trocar a
credencial.</li>
<li><strong>Verifique o uso</strong> nos logs do provedor (CloudTrail,
eventos do Stripe) — o segredo pode já estar sendo ativamente
explorado, não só teoricamente exposto.</li>
<li>Considere remover do histórico (BFG, git filter-repo) — isso limpa
o repositório principal, mas não desfaz o que forks e clones já
copiaram, então serve mais para higiene do que para conter o
vazamento.</li>
<li>Comunique ao time e à área de segurança — esconder o incidente só
atrasa a mitigação real.</li>
<li>Faça o postmortem: como o segredo vazou especificamente, e o que
muda no processo para que não se repita.</li>
</ol>

<h3>8. K8s Secrets: cuidados</h3>
<p>O <code>Secret</code> nativo do Kubernetes é apenas
<strong>base64</strong>, não criptografia — <code>kubectl get secret -o
yaml</code> revela o valor em texto plano para qualquer um com acesso
de leitura àquele objeto. Em cluster multi-tenant ou compartilhado,
quatro medidas fecham essa lacuna: habilitar
<strong>encryption-at-rest</strong> no próprio etcd via
<code>EncryptionConfiguration</code> com KMS; aplicar RBAC restritivo
para que só o namespace da aplicação leia seus próprios secrets;
adotar SealedSecrets (Bitnami) quando o fluxo é GitOps — o secret
CRIPTOGRAFADO pode ser commitado no Git com segurança, e só o controller
dentro do cluster consegue decriptar; ou usar SOPS combinado com KMS
para manter arquivo YAML/JSON criptografado e commitável. O External
Secrets Operator (seção 4.2) continua sendo o padrão mais moderno
quando a fonte de verdade é um cofre externo de verdade.</p>

<h3>9. Vault transit engine: criptografia como serviço</h3>
<p>Quando existe dado sensível para guardar num banco — CPF, cartão,
prontuário médico — a alternativa a implementar criptografia dentro da
própria aplicação (com risco real de errar a implementação) é delegar
isso ao Vault transit: a aplicação envia o texto puro e recebe de
volta um ciphertext pronto para armazenar, sem NUNCA manusear a chave
de criptografia diretamente:</p>
<pre><code># app envia plaintext, recebe ciphertext
POST /v1/transit/encrypt/customer-pii
{ "plaintext": "MTIzNDU2Nzg5" }   # base64
→ { "ciphertext": "vault:v2:abc..." }

# DB armazena 'vault:v2:abc...'
# Para ler, app chama /decrypt</code></pre>
<p>A chave nunca sai do Vault em nenhum momento desse fluxo, a rotação
fica centralizada num só lugar, e cada chamada de encrypt/decrypt gera
um registro de auditoria — um requisito direto de conformidade em
PCI, LGPD e HIPAA.</p>

<h3>10. Caso real: codecov breach (2021)</h3>
<p>Atacantes conseguiram injetar código no script bash distribuído
pelo Codecov (o padrão <code>bash &lt;(curl ...)</code>, rodado
diretamente em milhares de pipelines de CI ao redor do mundo). Esse
script comprometido exfiltrava as variáveis de ambiente do CI onde
rodava — incluindo qualquer segredo armazenado ali. O resultado foi
milhares de chaves e tokens vazados, espalhados por centenas de
empresas diferentes que nem sabiam estar expostas até o incidente ser
publicamente divulgado. A lição prática: segredo guardado como variável
de ambiente de CI fica vulnerável a QUALQUER script de terceiro que
rode naquele ambiente, mesmo um script aparentemente inofensivo de
cobertura de teste. Se o padrão fosse OIDC com token efêmero (seção
4.3), mesmo um atacante capturando o token teria uma janela de minutos
antes dele expirar sozinho — limitando drasticamente o blast radius do
mesmo incidente.</p>"""
                ),
                "body_en": """<h3>1. Types of secrets</h3>
<p>Not every secret should be treated the same way, and the right
category drives the protection strategy. <strong>Static</strong>
secrets — database passwords, API keys, service tokens — are created
manually and change rarely; they still belong in a vault and should
rotate periodically, because "almost never changes" is not the same as
"never needs to change". <strong>Dynamic</strong> secrets invert the
model: the vault itself creates the credential on demand, with a short
TTL — Vault, for example, generates a temporary Postgres user with a
random password valid for one hour and then revokes it on its own,
shrinking the exposure window to roughly the real usage time.
<strong>Ephemeral tokens</strong> (JWT/STS/OIDC) go further: short TTL
and they never exist as persistent storage anywhere — AssumeRole on
AWS, Workload Identity on GCP, and Managed Identity on Azure follow
this model. And <strong>certificates</strong> (TLS, mTLS, SSH CA)
typically live 7 to 90 days and renew automatically via ACME or an
equivalent tool (Vault PKI, smallstep, cert-manager).</p>
<div class="mermaid">
flowchart TD
    S["Secrets"] --> Static["Static: password, API key"]
    S --> Dyn["Dynamic: generated on demand"]
    S --> Eph["Ephemeral: short TTL / one-shot"]
    Static --> Vault["Vault + rotation"]
    Dyn --> Vault
    Eph --> Vault
</div>


<h3>2. Where NEVER to store secrets</h3>
<p>Seven places look convenient but guarantee a leak sooner or later.
<strong>Git</strong> — even in a private repo — never forgets: forks,
clones, exports, and history keep the secret indefinitely, even if the
commit is later "reverted". <strong>Slack/Teams/Discord</strong>
archives messages in logs, integrations, and e-discovery exports, often
retained for years by the company's own retention policy.
<strong>Email</strong> has the same problem, and also passes through
external servers along the way. An <code>ENV</code> or <code>ARG</code>
in a <strong>Dockerfile</strong> writes the secret straight into an
image LAYER — anyone with pull permission can extract it with
<code>docker history image</code>. Application or CI
<strong>logs</strong> end up retained for 30+ days in any typical SIEM
or observability SaaS. A CI environment variable <strong>without
masking</strong> appears in plaintext as soon as some step runs
<code>echo $VAR</code>, intentional or not. And even a browser
extension with <strong>cloud sync</strong> enabled can carry the secret
outside company control without anyone noticing.</p>

<h3>3. Modern vaults</h3>
<table>
<tr><th>Vault</th><th>Strengths</th></tr>
<tr><td>HashiCorp Vault</td><td>Multi-cloud, dynamic secrets, transit, PKI, OIDC. Self-hosted or Cloud.</td></tr>
<tr><td>AWS Secrets Manager</td><td>Native AWS integration, automatic RDS rotation, cross-region replication.</td></tr>
<tr><td>AWS Parameter Store</td><td>Cheaper, simpler; good for configs and less-critical secrets.</td></tr>
<tr><td>Azure Key Vault</td><td>Entra ID integration, HSM-backed.</td></tr>
<tr><td>GCP Secret Manager</td><td>Versioning, replication, granular IAM.</td></tr>
<tr><td>1Password / Bitwarden</td><td>Good for humans + secret automation (1Password Connect).</td></tr>
<tr><td>Doppler / Infisical</td><td>Small SaaS products focused on developer experience.</td></tr>
</table>

<h3>4. Pattern: never read the vault directly from the app (if possible)</h3>
<div class="mermaid">
sequenceDiagram
    participant App
    participant Platform as Platform
    participant Vault as Vault
    App->>Platform: Starts with identity
    Platform->>Vault: Fetches secret
    Vault-->>Platform: Short-lived secret
    Platform-->>App: Injects at runtime
</div>

<p>Having the application talk to the vault directly looks simple, but
it needs a dedicated client, retries, cache, its own auth, and specific
error handling — and if the vault itself has an incident, the app falls
with it, creating a new single point of failure exactly where you should
not have one. Three patterns avoid that direct coupling.</p>
<h4>4.1 Sidecar/Init container injector</h4>
<p>A separate container pulls the secret from the vault and writes it to
a shared file or volume; the application only reads the file, with no
vault logic embedded in it. Vault Agent is the classic example of this
pattern:</p>
<pre><code># Pod K8s
annotations:
  vault.hashicorp.com/agent-inject: 'true'
  vault.hashicorp.com/role: 'app'
  vault.hashicorp.com/agent-inject-secret-db: 'database/creds/app'</code></pre>
<h4>4.2 Operator on K8s</h4>
<p>The <strong>External Secrets Operator</strong> (ESO) follows the same
spirit, but natively for Kubernetes: you create an
<code>ExternalSecret</code> Custom Resource pointing at the vault, and
ESO populates a native <code>Secret</code> in the namespace, which the
application consumes exactly like any ordinary Secret, without knowing
the real source is external:</p>
<pre><code>apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: app-db }
spec:
  secretStoreRef: { name: aws-sm, kind: ClusterSecretStore }
  target: { name: app-db-secret }
  data:
    - secretKey: password
      remoteRef: { key: prod/app/db, property: password }</code></pre>
<h4>4.3 OIDC/Workload Identity</h4>
<p>In a CI/CD pipeline, the ideal is to store NO secret at all: GitHub
Actions issues an ephemeral JWT, AWS validates that token via OIDC and
returns short-lived STS credentials — no long-lived secret is ever
saved in GitHub:</p>
<pre><code>permissions:
  id-token: write
  contents: read
jobs:
  deploy:
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111111111111:role/gh-deployer
          aws-region: us-east-1
      - run: aws s3 sync ./build s3://app-prod   # sem keys!</code></pre>
<h3>5. Rotation</h3>
<p>A common policy differentiates rotation by credential type: human
credentials (password, MFA reset) every 90 days; static machine
credentials every 30 to 90 days; critical credentials (root, KMS master
key) with extra care, but ideally every 365 days with accompanying
audit; and any suspected leak triggers IMMEDIATE rotation, without
waiting for the scheduled cycle. Vault with dynamic secrets already
solves this "for free" — the short TTL IS the rotation. For static
secrets, automation is the path: once enabled, AWS Secrets Manager runs
a Lambda that creates the new password, updates RDS, and updates the
secret itself — the application fetches via a TTL cache and receives
the new password automatically, with no manual intervention at swap
time.</p>

<h3>6. Detection in PRs and in code</h3>
<p>Accidents happen even with a well-designed process — real defense is
having several layers catching the same mistake at different points. The
<strong>pre-commit hook</strong> (gitleaks, trufflehog, detect-secrets)
blocks the push before it leaves the developer's laptop. The
<strong>CI check</strong> catches what slipped past a skipped pre-commit
— the layer where <code>--no-verify</code> is not available.
<strong>GitHub Secret Scanning</strong> is on by default for public
repos (and via Advanced Security for private ones), detects 200+ known
patterns, and in many cases notifies the provider itself (AWS, Stripe)
which can revoke the key automatically before anyone notices the leak.
And a <strong>periodic audit</strong> of old repositories with
trufflehog or gitleaks-search catches what was forgotten years ago,
before these layers existed:</p>
<pre><code># .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks</code></pre>
<h3>7. IF a secret leaked: what to do</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Revoke the secret immediately</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Rotate anything that shared the same material</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Audit usage logs for the window</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Block new commits with secret scanning</p></div>
  </div>
  <figcaption>Response order when a secret leaks.</figcaption>
</figure>

<ol>
<li><strong>Rotate immediately</strong>, even if the first response was
only a <code>git rm --cached</code> — history still carries the original
value, so the only real defense is changing the credential.</li>
<li><strong>Check usage</strong> in provider logs (CloudTrail, Stripe
events) — the secret may already be actively exploited, not just
theoretically exposed.</li>
<li>Consider removing it from history (BFG, git filter-repo) — that
cleans the main repository, but does not undo what forks and clones
already copied, so it is more hygiene than containment.</li>
<li>Tell the team and security — hiding the incident only delays real
mitigation.</li>
<li>Do the postmortem: how the secret leaked specifically, and what
changes in the process so it does not happen again.</li>
</ol>

<h3>8. K8s Secrets: caveats</h3>
<p>The native Kubernetes <code>Secret</code> is only
<strong>base64</strong>, not encryption — <code>kubectl get secret -o
yaml</code> reveals the value in plaintext to anyone with read access
to that object. In a multi-tenant or shared cluster, four measures close
that gap: enable <strong>encryption-at-rest</strong> on etcd via
<code>EncryptionConfiguration</code> with KMS; apply restrictive RBAC so
only the application namespace reads its own secrets; adopt
SealedSecrets (Bitnami) for GitOps flows — the ENCRYPTED secret can be
committed to Git safely, and only the in-cluster controller can decrypt;
or use SOPS with KMS to keep an encrypted, commit-friendly YAML/JSON
file. External Secrets Operator (section 4.2) remains the more modern
pattern when the source of truth is a real external vault.</p>

<h3>9. Vault transit engine: encryption as a service</h3>
<p>When sensitive data must live in a database — tax IDs, cards,
medical records — the alternative to implementing encryption inside the
application itself (with real risk of getting it wrong) is to delegate
to Vault transit: the app sends plaintext and gets back ciphertext ready
to store, without EVER handling the encryption key directly:</p>
<pre><code># app envia plaintext, recebe ciphertext
POST /v1/transit/encrypt/customer-pii
{ "plaintext": "MTIzNDU2Nzg5" }   # base64
→ { "ciphertext": "vault:v2:abc..." }

# DB armazena 'vault:v2:abc...'
# Para ler, app chama /decrypt</code></pre>
<p>The key never leaves Vault at any point in this flow, rotation stays
centralized in one place, and every encrypt/decrypt call produces an
audit record — a direct compliance requirement under PCI, LGPD, and
HIPAA.</p>

<h3>10. Real case: Codecov breach (2021)</h3>
<p>Attackers injected code into the bash script distributed by Codecov
(the <code>bash &lt;(curl ...)</code> pattern, run directly in thousands
of CI pipelines worldwide). That compromised script exfiltrated
environment variables from the CI where it ran — including any secret
stored there. The result was thousands of keys and tokens leaked across
hundreds of companies that did not even know they were exposed until the
incident was publicly disclosed. The practical lesson: a secret stored
as a CI environment variable is vulnerable to ANY third-party script that
runs in that environment, even an apparently harmless test-coverage
script. If the pattern had been OIDC with an ephemeral token (section
4.3), even an attacker capturing the token would have only minutes
before it expired on its own — drastically limiting the blast radius of
the same incident.</p>""",
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Configure Vault em Docker. Habilite KV-v2 e crie segredos.</li>"
                    "<li>Configure GitHub Actions com OIDC para AWS, sem armazenar access "
                    "keys no GitHub. Job baixa secret do Secrets Manager e usa.</li>"
                    "<li>Em K8s local (kind/minikube), instale External Secrets Operator. "
                    "Crie ExternalSecret apontando para AWS Secrets Manager (ou Vault).</li>"
                    "<li>Configure gitleaks como pre-commit hook + GitHub Action. Faça commit "
                    "com fake AWS key e veja o bloqueio.</li>"
                    "<li>Habilite GitHub Secret Scanning no seu repo público.</li>"
                    "<li>Configure rotação automática de RDS via AWS Secrets Manager.</li>"
                    "<li>Bonus: SOPS + KMS, criptografe arquivo de config, commite, "
                    "decripte localmente para uso.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Full hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>Configure Vault in Docker. Enable KV-v2 and create secrets.</li>"
                    "<li>Configure GitHub Actions with OIDC for AWS, without storing access "
                    "keys in GitHub. The job pulls a secret from Secrets Manager and uses it.</li>"
                    "<li>On local K8s (kind/minikube), install External Secrets Operator. "
                    "Create an ExternalSecret pointing at AWS Secrets Manager (or Vault).</li>"
                    "<li>Configure gitleaks as a pre-commit hook + GitHub Action. Commit "
                    "a fake AWS key and watch the block.</li>"
                    "<li>Enable GitHub Secret Scanning on your public repo.</li>"
                    "<li>Configure automatic RDS rotation via AWS Secrets Manager.</li>"
                    "<li>Bonus: SOPS + KMS — encrypt a config file, commit it, "
                    "decrypt locally for use.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("HashiCorp Vault docs", "https://developer.hashicorp.com/vault/docs", "docs", "",
                  title_en="HashiCorp Vault docs", description_en=""),
                m("AWS Secrets Manager", "https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html", "docs", "",
                  title_en="AWS Secrets Manager", description_en=""),
                m("Azure Key Vault", "https://learn.microsoft.com/azure/key-vault/general/overview", "docs", "",
                  title_en="Azure Key Vault", description_en=""),
                m("GitHub OIDC", "https://docs.github.com/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect", "docs", "",
                  title_en="GitHub OIDC", description_en=""),
                m("Mozilla SOPS", "https://github.com/getsops/sops", "tool", "",
                  title_en="Mozilla SOPS", description_en=""),
                m("External Secrets Operator (K8s)", "https://external-secrets.io/", "tool", "",
                  title_en="External Secrets Operator (K8s)", description_en=""),
            ],
            "questions": [
                q("Senha em código é:",
                  "Risco crítico, bastando um clone público para vazar.",
                  ["Encriptada automaticamente por padrão em qualquer repositório git.",
                   "Uma boa prática amplamente recomendada por especialista em segurança.",
                   "Imune a vazamento mesmo com o repositório tornado público sem querer."],
                  "Crawlers buscam por padrões como `AKIA...` em segundos após push público.",
                  statement_en="A password in code is:",
                  correct_en="A critical risk — a public clone is enough to leak it.",
                  wrong_en=["Encrypted by default in any git repository.",
                            "A widely recommended practice among security specialists.",
                            "Immune to leaks even if the repo is made public by accident."],
                  explanation_en="Crawlers search for patterns like `AKIA...` within seconds of a public push."),
                q("Vault dynamic secrets:",
                  "Geram credenciais temporárias por demanda.",
                  ["Substituem completamente a necessidade de usar TLS na conexão.",
                   "Um registro de DNS apontando para o endereço do serviço.",
                   "Um arquivo criptografado guardado localmente no disco do usuário."],
                  "Diminui janela de exposição, e revogação é trivial, basta TTL expirar.",
                  statement_en="Vault dynamic secrets:",
                  correct_en="Generate temporary credentials on demand.",
                  wrong_en=["Fully replace the need to use TLS on the connection.",
                            "A DNS record pointing at the service address.",
                            "An encrypted file stored locally on the user's disk."],
                  explanation_en="They shrink the exposure window, and revocation is trivial — just wait for TTL to expire."),
                q("OIDC em CI evita:",
                  "Armazenar chaves longas estáticas.",
                  ["Substituir a necessidade de usar container Docker no pipeline.",
                   "Atualizar a dependência do projeto antes de cada deploy.",
                   "Reduzir o tempo total gasto durante a etapa de build."],
                  "GitHub emite token JWT efêmero; AWS valida e devolve credencial STS, sem segredo persistente.",
                  statement_en="OIDC in CI avoids:",
                  correct_en="Storing long-lived static keys.",
                  wrong_en=["Replacing the need to use Docker containers in the pipeline.",
                            "Updating project dependencies before every deploy.",
                            "Reducing total time spent in the build stage."],
                  explanation_en="GitHub issues an ephemeral JWT; AWS validates it and returns STS credentials — no persistent secret."),
                q("SOPS criptografa:",
                  "Arquivos YAML/JSON com chaves KMS.",
                  ["Só senha em texto puro, sem suporte a outro tipo de dado.",
                   "Só hash calculado a partir do conteúdo do arquivo original.",
                   "Só arquivo binário, sem suporte a formato de texto estruturado."],
                  "Permite commitar arquivo cripto no repo (GitOps friendly). Decryption só com permissão KMS.",
                  statement_en="SOPS encrypts:",
                  correct_en="YAML/JSON files with KMS keys.",
                  wrong_en=["Only plaintext passwords, with no support for other data types.",
                            "Only a hash computed from the original file contents.",
                            "Only binary files, with no support for structured text formats."],
                  explanation_en="Lets you commit encrypted files to the repo (GitOps-friendly). Decryption requires KMS permission."),
                q("Rotação automática reduz:",
                  "Janela de exposição se a senha vazar.",
                  ["A latência de rede entre o cliente e o cofre de segredo.",
                   "O custo mensal cobrado pelo serviço de gerenciamento de chave.",
                   "O tamanho em disco do arquivo onde a credencial fica salva."],
                  "Mesmo se um atacante captura, a credencial vira inválida em poucos dias.",
                  statement_en="Automatic rotation reduces:",
                  correct_en="The exposure window if the password leaks.",
                  wrong_en=["Network latency between the client and the secrets vault.",
                            "The monthly cost charged by the key-management service.",
                            "Disk size of the file where the credential is stored."],
                  explanation_en="Even if an attacker captures it, the credential becomes invalid within a few days."),
                q("Compartilhar segredo via Slack:",
                  "Risco de exposição persistente, preferir cofres.",
                  ["Auto-expira depois de um tempo configurado pela plataforma.",
                   "Uma boa prática amplamente aceita para troca rápida de informação.",
                   "Encriptado por padrão em qualquer canal de mensagem corporativo."],
                  "Mensagens permanecem em logs corporativos, integrações, exports. Use 1Password share / Vault link com TTL.",
                  statement_en="Sharing a secret via Slack:",
                  correct_en="Risks persistent exposure — prefer vaults.",
                  wrong_en=["Auto-expires after a time configured by the platform.",
                            "A widely accepted practice for quick information exchange.",
                            "Encrypted by default in any corporate messaging channel."],
                  explanation_en="Messages linger in corporate logs, integrations, and exports. Use 1Password share / Vault link with TTL."),
                q("`.env.example` deve conter:",
                  "Apenas as chaves esperadas, sem valores reais.",
                  ["Um backup completo do banco de dado de produção da empresa.",
                   "Um token de acesso direto ao serviço de KMS da conta.",
                   "A senha real usada no ambiente de produção da aplicação."],
                  "Documenta variáveis necessárias, mas valores ficam fora do repo.",
                  statement_en="`.env.example` should contain:",
                  correct_en="Only the expected keys, with no real values.",
                  wrong_en=["A full backup of the company's production database.",
                            "A direct access token to the account's KMS service.",
                            "The real password used in the application's production environment."],
                  explanation_en="It documents required variables, but values stay out of the repo."),
                q("Pre-commit hook útil:",
                  "Detectar segredos com gitleaks ou trufflehog.",
                  ["Forçar um push direto para o branch principal do repositório.",
                   "Apagar o histórico de commit relacionado ao segredo vazado.",
                   "Comprimir o tamanho total do repositório antes do commit."],
                  "Bloqueia push antes do segredo sair do laptop. Combine com checagem server-side.",
                  statement_en="A useful pre-commit hook:",
                  correct_en="Detect secrets with gitleaks or trufflehog.",
                  wrong_en=["Force a direct push to the repository's main branch.",
                            "Delete the commit history related to a leaked secret.",
                            "Compress the total repository size before the commit."],
                  explanation_en="Blocks the push before the secret leaves the laptop. Combine with server-side checks."),
                q("Em K8s, segredos como Secret são:",
                  "Base64 encoded, NÃO criptografados por padrão.",
                  ["Hash irreversível, sem caminho de volta até o valor original.",
                   "Criptografado automaticamente com uma chave gerenciada pelo cluster.",
                   "Incapaz de armazenar valor binário dentro do mesmo objeto."],
                  "Habilite encryption-at-rest no etcd e use ferramentas como SealedSecrets/External Secrets.",
                  statement_en="In K8s, Secret objects are:",
                  correct_en="Base64-encoded, NOT encrypted by default.",
                  wrong_en=["An irreversible hash, with no way back to the original value.",
                            "Automatically encrypted with a cluster-managed key.",
                            "Unable to store binary values in the same object."],
                  explanation_en="Enable encryption-at-rest on etcd and use tools like SealedSecrets/External Secrets."),
                q("Vault transit engine serve para:",
                  "Criptografia como serviço (encrypt/decrypt) sem expor a chave.",
                  ["Auditoria detalhada de permissão concedida a cada usuário do IAM da conta.",
                   "Provisionamento automático de máquina virtual sob demanda na infraestrutura.",
                   "Backup periódico do log gerado pela aplicação rodando em produção."],
                  "App envia plaintext, recebe ciphertext. Chave nunca sai do Vault. Bom para campos sensíveis em DB.",
                  statement_en="Vault transit engine is used for:",
                  correct_en="Encryption as a service (encrypt/decrypt) without exposing the key.",
                  wrong_en=["Detailed auditing of IAM permissions granted to each account user.",
                            "Automatic on-demand provisioning of virtual machines in the infrastructure.",
                            "Periodic backup of logs produced by the application running in production."],
                  explanation_en="The app sends plaintext and receives ciphertext. The key never leaves Vault. Good for sensitive DB fields."),
            ],
        },
        # =====================================================================
        # 3.5 CI/CD Básico
        # =====================================================================
        {
            "title": "CI/CD Básico",
            "title_en": 'Basic CI/CD',
            "summary": "Criar uma esteira simples que testa e move o código para o servidor.",
            "summary_en": 'Build a simple pipeline that tests and moves code to the server.',
            "lesson": {
                "intro": (
                    "Em times sem CI/CD, deploy é evento. Engenheiros se preparam por dias, "
                    "agendam janela noturna, fazem checklist no Confluence, e mesmo assim "
                    "alguma coisa quebra em produção. Em times com CI/CD maduros, deploy "
                    "é não-evento, várias vezes por dia, automaticamente, com rollback em "
                    "segundos. CI/CD não é luxo, é o que viabiliza entregar com frequência "
                    "<em>sem</em> aumentar risco. Esta aula cobre os princípios, padrões "
                    "(blue-green, canary, rolling), pipeline-as-code, e como medir saúde "
                    "do processo (DORA metrics)."
                ),
                "intro_en": (
                    "In teams without CI/CD, deploy is an event. Engineers prepare for days, "
                    "schedule a night window, follow a Confluence checklist, and something still "
                    "breaks in production. In teams with mature CI/CD, deploy is a non-event, "
                    "several times a day, automatically, with rollback in seconds. CI/CD is not "
                    "a luxury — it is what makes frequent delivery possible <em>without</em> "
                    "increasing risk. This lesson covers principles, patterns "
                    "(blue-green, canary, rolling), pipeline-as-code, and how to measure process "
                    "health (DORA metrics)."
                ),
                "body": (
                """<h3>1. CI vs CD vs CD: três conceitos, duas siglas</h3>
<p><strong>CI (Continuous Integration)</strong> significa que a cada
commit, o código é mergeado e validado imediatamente — build, lint,
teste unitário, SAST, SCA — com o objetivo de encontrar problema em
minutos, não dias depois quando já está enterrado sob outras mudanças.
A regra que sustenta isso é: se o build quebra, TODO o time para até
consertar, em vez de continuar empilhando trabalho em cima de uma base
quebrada. <strong>CD (Continuous Delivery)</strong> vai um passo além:
o artefato fica sempre pronto para deploy a qualquer momento, mas um
HUMANO ainda aperta o botão final — comum em times que preferem manter
essa aprovação explícita. E <strong>CD (Continuous Deployment)</strong>
remove até esse último passo manual: todo commit que passa pelo
pipeline inteiro vai automaticamente para produção, sem intervenção —
um nível de maturidade que exige teste e telemetria muito robustos antes
de fazer sentido.</p>
<div class="mermaid">
flowchart LR
    CI["CI: build + test a cada push"] --> CD1["CD: entrega contínua pronta"]
    CD1 --> CD2["CD: deploy contínuo automático"]
    CI --> Gate["Gate humano opcional"]
    Gate --> CD2
</div>


<h3>2. Pipeline mínimo de qualidade</h3>
<pre><code>commit → lint → unit tests → build → security scans →
         push artefato → deploy dev → integration tests →
         deploy staging → smoke + e2e → [approval] → deploy prod</code></pre>
<p>Cada etapa precisa <strong>falhar rápido</strong> — lint em
segundos, unit test em menos de 5 minutos, integration test em menos de
15 — porque um pipeline lento é um pipeline que o time aprende a
ignorar ou pular, na prática anulando todo o propósito de tê-lo.</p>

<h3>3. GitHub Actions: pipeline completo de exemplo</h3>
<pre><code>name: ci-cd
on:
  push: { branches: [main] }
  pull_request: {}
permissions:
  contents: read
  packages: write
  id-token: write
  security-events: write
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12', cache: 'pip' }
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy app
  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: ci }
        options: --health-cmd pg_isready
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v4
  security:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
      - uses: returntocorp/semgrep-action@v1
        with: { config: p/owasp-top-ten }
      - uses: gitleaks/gitleaks-action@v2
  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ghcr.io/empresa/app:${{ github.sha }}
            ghcr.io/empresa/app:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/empresa/app:${{ github.sha }}
          severity: 'CRITICAL'
          exit-code: '1'
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/empresa/app@${{ steps.push.outputs.digest }}
  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111:role/deployer
          aws-region: us-east-1
      - run: ./scripts/deploy.sh staging ${{ github.sha }}
      - run: ./scripts/smoke-tests.sh https://staging.app
  deploy-prod:
    needs: deploy-staging
    environment: production   # gate manual
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy.sh prod ${{ github.sha }}</code></pre>
<p>Vale destacar cinco detalhes desse pipeline que não são acidente:
<code>concurrency</code> cancela execução antiga do mesmo branch quando
um push novo chega, evitando gastar minuto de CI num commit já
obsoleto; <code>permissions</code> segue o princípio do menor
privilégio, concedendo write apenas onde realmente é necessário;
OIDC autentica na AWS sem nenhuma chave de longa duração armazenada;
<code>environment: production</code> implementa o gate manual — com
secret adicional, timer de espera ou reviewer obrigatório configurável
diretamente na UI do GitHub; e a assinatura via Cosign na etapa de
build permite que um admission controller no Kubernetes verifique a
integridade da imagem antes de rodá-la.</p>

<h3>4. Estratégias de deploy</h3>
<div class="mermaid">
flowchart TD
    Blue["Blue estável"] --> Switch{"Troca tráfego?"}
    Green["Green nova versão"] --> Switch
    Switch -- Sim --> Live["Green vira live"]
    Switch -- Rollback --> Blue
</div>

<h4>4.1 Recriação (recreate)</h4>
<p>A estratégia mais simples: mata todos os pods antigos e sobe os
novos em seguida. Causa downtime real durante a transição — aceitável
em dev/QA, praticamente inaceitável em produção.</p>
<h4>4.2 Rolling</h4>
<p>Substitui réplica por réplica gradualmente, o padrão default no
Kubernetes. Não causa downtime SE a aplicação suporta múltiplas versões
coexistindo ao mesmo tempo durante a transição — o rollback, porém, é
literalmente rolar o processo de volta, e por isso é relativamente
lento:</p>
<pre><code>spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0</code></pre>
<h4>4.3 Blue-Green</h4>
<p>Mantém dois ambientes idênticos rodando ao mesmo tempo — blue (a
versão atual) e green (a nova). O deploy acontece no green, é validado
isoladamente, e só então o load balancer troca o tráfego de um lado
para o outro de uma vez. Isso torna o rollback quase instantâneo — basta
trocar de volta — ao custo de manter recurso dobrado durante toda a
janela de transição, algo aceitável para sistema que tolera essa
duplicação por algumas horas.</p>
<h4>4.4 Canary</h4>
<p>Libera a versão nova para uma fração pequena dos usuários (5%, por
exemplo), monitora métrica real (erro, latência, KPI de negócio), e só
então aumenta gradualmente para 25%, 50%, 100% — ou reverte
imediatamente se algo sair errado. O nome vem do canário usado em minas
de carvão: o pássaro morria antes do gás afetar os mineiros, servindo
como alarme antecipado — aqui, a pequena fração de tráfego sente o
problema antes que ele afete a maioria dos usuários. Argo Rollouts e
Flagger automatizam esse processo, promovendo a versão automaticamente
com base em métrica do Prometheus ou Datadog.</p>
<h4>4.5 Feature flags</h4>
<p>Desacopla completamente deploy de release: o código chega em
produção já DESLIGADO, e é ativado gradualmente depois, controlado por
flag — não por um novo deploy. LaunchDarkly, Unleash, OpenFeature e
ConfigCat são as ferramentas dominantes desse padrão, que viabiliza A/B
test, kill switch instantâneo, e rollback sem precisar de nenhum
redeploy:</p>
<pre><code>if (flags.isEnabled('new-checkout-flow', user)) {
    return newCheckout(req);
}
return oldCheckout(req);</code></pre>

<h3>5. Artefatos imutáveis</h3>
<p>O princípio central: o MESMO binário ou imagem que passou em
staging é exatamente o que vai para produção, identificado por hash ou
SHA — nunca um "rebuild para produção", porque rebuildar significa
testar uma coisa e rodar outra ligeiramente diferente. Na prática isso
exige tag por commit SHA (<code>app:abc1234</code>) ou versão semver
(<code>app:v1.4.2</code>), nunca <code>latest</code> em produção — essa
tag não é rastreável a nenhum commit específico; build uma vez só,
promovendo o mesmo artefato entre ambientes em vez de reconstruir a
cada estágio; configuração injetada via variável de ambiente ou segredo
externo, nunca embutida durante o build; e assinatura via Cosign
garantindo que o artefato não foi adulterado entre a construção e a
execução.</p>

<h3>6. Pipeline-as-code</h3>
<p>O pipeline vive dentro do próprio repositório —
<code>.github/workflows/</code>, <code>.gitlab-ci.yml</code>,
<code>Jenkinsfile</code>, <code>buildspec.yml</code> — versionado,
revisado em PR como qualquer outro código, e totalmente auditável.
Isso elimina de vez o cenário clássico do Jenkins configurado
manualmente pela UI, onde só um administrador específico sabe o que
realmente existe configurado no servidor.</p>

<h3>7. Métricas DORA</h3>
<p>Uma pesquisa de longo prazo do Google (o time DORA) correlacionou
alta performance de engenharia com quatro métricas específicas, não com
intuição subjetiva de "esse time é rápido". O <strong>Deployment
Frequency</strong> mede quantas vezes por dia, semana ou mês a equipe
faz deploy — um time elite deploya várias vezes ao dia. O
<strong>Lead Time for Changes</strong> mede o tempo do commit até
chegar em produção — elite fica abaixo de uma hora. O
<strong>Mean Time to Restore</strong> (MTTR) mede quanto tempo leva
para recuperar de um incidente — elite também abaixo de uma hora. E o
<strong>Change Failure Rate</strong> mede a porcentagem de deploys que
causam incidente — elite fica entre 0% e 15%. O achado mais
contraintuitivo dessa pesquisa é que times elite têm as QUATRO métricas
altas ao mesmo tempo — não existe trade-off real entre velocidade e
estabilidade quando o processo é bom o suficiente. O que viabiliza isso
é justamente teste automatizado, deploy automatizado, trunk-based
development e observabilidade — as peças descritas nas seções
anteriores desta aula.</p>

<h3>8. Cache, matrix e otimização</h3>
<p>Cache de dependência (pip, npm, Go modules, camada de imagem
Docker) deve ter chave baseada no hash do lockfile, não no nome do
branch — assim o cache é reaproveitado entre branches diferentes que
compartilham as mesmas dependências, em vez de recriar tudo do zero a
cada PR novo. Matrix builds rodam múltiplas combinações em paralelo —
Python 3.10/3.11/3.12 cruzado com Linux/macOS, por exemplo — no
tempo aproximado de UMA única execução, não da soma de todas. Workflows
reutilizáveis (o recurso nativo do GitHub) ou <code>include</code> no
GitLab evitam duplicar a mesma configuração de pipeline entre múltiplos
repositórios. E runner self-hosted faz sentido especificamente para
build pesado ou que exige hardware específico, como GPU, que o runner
padrão hospedado não oferece.</p>

<h3>9. Anti-patterns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Anti-pattern</strong><p>Deploy manual fora do pipeline, artefato mutável, secrets no YAML do workflow.</p></div>
    <div class="lesson-viz-card"><strong>Saudável</strong><p>Pipeline-as-code, artefato imutável por digest, approvals em environment.</p></div>
  </div>
  <figcaption>Sinais de pipeline maduro vs frágil.</figcaption>
</figure>

<ul>
<li><strong>Deploy manual em produção</strong>: abre espaço para erro
humano recorrente, exatamente o que a automação existe para
eliminar.</li>
<li><strong>Pipeline sem teste real</strong>: "deploy direto" vira
roleta russa disfarçada de processo.</li>
<li><strong>Taxa alta de bug escapando com CI verde</strong>: sinal
direto de que os testes existentes não cobrem o que realmente
importa.</li>
<li><strong>Pipeline lento (1h ou mais)</strong>: ninguém espera de
verdade, e o time aprende a pular etapa (seção 2).</li>
<li><strong>Teste "flaky" (intermitente)</strong>: corrói a confiança
no próprio sinal do CI — depois de algumas falhas aleatórias, o time
para de confiar em falha real também.</li>
<li><strong>Build feito "manualmente" direto em produção</strong>: "só
recompilei lá" vira exatamente o tipo de bug específico que ninguém
mais consegue reproduzir depois.</li>
<li><strong>Só a branch main é testada</strong>: sem CI rodando em PR,
problema só aparece DEPOIS do merge, quando já é mais caro reverter.</li>
</ul>

<h3>10. GitOps</h3>
<p>O princípio do GitOps: o repositório Git é a fonte da verdade do
estado DESEJADO do cluster, não um histórico de comando aplicado
manualmente. O Argo CD ou o Flux observam continuamente o repositório
e reconciliam o cluster real contra o que está declarado — sem nenhum
<code>kubectl apply</code> manual no meio do caminho:</p>
<pre><code># cluster/applications/app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: app, namespace: argocd }
spec:
  source:
    repoURL: https://github.com/empresa/k8s-config
    path: apps/app/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: prod
  syncPolicy:
    automated: { prune: true, selfHeal: true }</code></pre>
<p>As vantagens seguem diretamente do modelo: rollback vira um simples
<code>git revert</code>, auditoria vira <code>git log</code>, e a
detecção de drift é nativa — qualquer mudança manual feita fora do
Git é automaticamente revertida pelo <code>selfHeal</code> na próxima
reconciliação.</p>"""
                ),
                "body_en": """<h3>1. CI vs CD vs CD: three concepts, two acronyms</h3>
<p><strong>CI (Continuous Integration)</strong> means that on every
commit, code is merged and validated immediately — build, lint,
unit tests, SAST, SCA — with the goal of finding problems in
minutes, not days later when they are buried under other changes.
The rule that sustains this: if the build breaks, the WHOLE team stops
until it is fixed, instead of stacking more work on a broken base.
<strong>CD (Continuous Delivery)</strong> goes one step further:
the artifact is always ready to deploy at any moment, but a
HUMAN still presses the final button — common in teams that prefer to
keep that explicit approval. And <strong>CD (Continuous Deployment)</strong>
removes even that last manual step: every commit that passes the
full pipeline goes to production automatically, with no intervention —
a maturity level that needs very robust tests and telemetry before
it makes sense.</p>
<div class="mermaid">
flowchart LR
    CI["CI: build + test on every push"] --> CD1["CD: continuous delivery ready"]
    CD1 --> CD2["CD: continuous deploy automatic"]
    CI --> Gate["Optional human gate"]
    Gate --> CD2
</div>


<h3>2. Minimum quality pipeline</h3>
<pre><code>commit → lint → unit tests → build → security scans →
         push artefato → deploy dev → integration tests →
         deploy staging → smoke + e2e → [approval] → deploy prod</code></pre>
<p>Each stage must <strong>fail fast</strong> — lint in
seconds, unit tests under 5 minutes, integration tests under
15 — because a slow pipeline is one the team learns to
ignore or skip, effectively nullifying the whole point of having it.</p>

<h3>3. GitHub Actions: complete sample pipeline</h3>
<pre><code>name: ci-cd
on:
  push: { branches: [main] }
  pull_request: {}
permissions:
  contents: read
  packages: write
  id-token: write
  security-events: write
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12', cache: 'pip' }
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy app
  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: ci }
        options: --health-cmd pg_isready
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v4
  security:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
      - uses: returntocorp/semgrep-action@v1
        with: { config: p/owasp-top-ten }
      - uses: gitleaks/gitleaks-action@v2
  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ghcr.io/empresa/app:${{ github.sha }}
            ghcr.io/empresa/app:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/empresa/app:${{ github.sha }}
          severity: 'CRITICAL'
          exit-code: '1'
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/empresa/app@${{ steps.push.outputs.digest }}
  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111:role/deployer
          aws-region: us-east-1
      - run: ./scripts/deploy.sh staging ${{ github.sha }}
      - run: ./scripts/smoke-tests.sh https://staging.app
  deploy-prod:
    needs: deploy-staging
    environment: production   # gate manual
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy.sh prod ${{ github.sha }}</code></pre>
<p>Five details of this pipeline are not accidental:
<code>concurrency</code> cancels an older run on the same branch when
a new push arrives, avoiding spending CI minutes on an already
obsolete commit; <code>permissions</code> follows least
privilege, granting write only where it is truly needed;
OIDC authenticates to AWS with no long-lived key stored;
<code>environment: production</code> implements the manual gate — with
extra secrets, wait timers, or required reviewers configurable
directly in the GitHub UI; and Cosign signing in the
build stage lets a Kubernetes admission controller verify
image integrity before running it.</p>

<h3>4. Deploy strategies</h3>
<div class="mermaid">
flowchart TD
    Blue["Blue stable"] --> Switch{"Shift traffic?"}
    Green["Green new version"] --> Switch
    Switch -- Yes --> Live["Green becomes live"]
    Switch -- Rollback --> Blue
</div>

<h4>4.1 Recreate</h4>
<p>The simplest strategy: kill all old pods and bring the
new ones up next. Causes real downtime during the transition — acceptable
in dev/QA, practically unacceptable in production.</p>
<h4>4.2 Rolling</h4>
<p>Replaces replicas one by one gradually — the Kubernetes
default. No downtime IF the application supports multiple versions
coexisting during the transition — rollback, however, is
literally rolling the process back, and therefore relatively
slow:</p>
<pre><code>spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0</code></pre>
<h4>4.3 Blue-Green</h4>
<p>Keeps two identical environments running at once — blue (the
current version) and green (the new one). Deploy happens on green, is
validated in isolation, and only then the load balancer flips traffic
from one side to the other in one shot. That makes rollback almost
instant — just flip back — at the cost of doubled resources for the
whole transition window, acceptable for systems that tolerate that
duplication for a few hours.</p>
<h4>4.4 Canary</h4>
<p>Releases the new version to a small fraction of users (5%, for
example), monitors real metrics (errors, latency, business KPIs), and only
then gradually increases to 25%, 50%, 100% — or rolls back
immediately if something goes wrong. The name comes from the canary used in
coal mines: the bird died before the gas affected miners, serving as
an early alarm — here, the small traffic fraction feels the
problem before it hits most users. Argo Rollouts and
Flagger automate this, promoting the version automatically
based on Prometheus or Datadog metrics.</p>
<h4>4.5 Feature flags</h4>
<p>Fully decouples deploy from release: code reaches
production already OFF, and is turned on gradually later, controlled by
flag — not by a new deploy. LaunchDarkly, Unleash, OpenFeature, and
ConfigCat dominate this pattern, enabling A/B
tests, instant kill switches, and rollback without any
redeploy:</p>
<pre><code>if (flags.isEnabled('new-checkout-flow', user)) {
    return newCheckout(req);
}
return oldCheckout(req);</code></pre>

<h3>5. Immutable artifacts</h3>
<p>The core principle: the SAME binary or image that passed
staging is exactly what goes to production, identified by hash or
SHA — never a "rebuild for production", because rebuilding means
testing one thing and running something slightly different. In practice that
requires tagging by commit SHA (<code>app:abc1234</code>) or semver
(<code>app:v1.4.2</code>), never <code>latest</code> in production — that
tag is not traceable to any specific commit; build once,
promoting the same artifact across environments instead of rebuilding at
each stage; configuration injected via environment variables or external
secrets, never baked in at build time; and Cosign
signing guaranteeing the artifact was not tampered with between build and
execution.</p>

<h3>6. Pipeline-as-code</h3>
<p>The pipeline lives inside the repository itself —
<code>.github/workflows/</code>, <code>.gitlab-ci.yml</code>,
<code>Jenkinsfile</code>, <code>buildspec.yml</code> — versioned,
reviewed in PRs like any other code, and fully auditable.
That ends the classic Jenkins-configured-by-hand-in-the-UI scenario,
where only one specific admin knows what is actually configured on the
server.</p>

<h3>7. DORA metrics</h3>
<p>Long-running Google research (the DORA team) correlated
high engineering performance with four specific metrics, not with
subjective intuition that "this team is fast". <strong>Deployment
Frequency</strong> measures how many times per day, week, or month the team
deploys — an elite team deploys several times a day.
<strong>Lead Time for Changes</strong> measures time from commit to
production — elite stays under one hour.
<strong>Mean Time to Restore</strong> (MTTR) measures how long it takes
to recover from an incident — elite also under one hour. And
<strong>Change Failure Rate</strong> measures the percentage of deploys that
cause incidents — elite sits between 0% and 15%. The most
counterintuitive finding is that elite teams have all FOUR metrics
high at once — there is no real trade-off between speed and
stability when the process is good enough. What enables that
is automated testing, automated deploy, trunk-based
development, and observability — the pieces described in earlier
sections of this lesson.</p>

<h3>8. Cache, matrix, and optimization</h3>
<p>Dependency cache (pip, npm, Go modules, Docker image
layers) should be keyed on the lockfile hash, not the
branch name — so the cache is reused across different branches that
share the same dependencies, instead of rebuilding from scratch on
every new PR. Matrix builds run multiple combinations in parallel —
Python 3.10/3.11/3.12 crossed with Linux/macOS, for example — in
roughly the time of ONE run, not the sum of all. Reusable workflows
(GitHub's native feature) or <code>include</code> in
GitLab avoid duplicating the same pipeline config across multiple
repositories. And self-hosted runners make sense specifically for
heavy builds or hardware-specific needs, like GPUs, that hosted
runners do not offer.</p>

<h3>9. Anti-patterns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Anti-pattern</strong><p>Manual deploy outside the pipeline, mutable artifact, secrets in workflow YAML.</p></div>
    <div class="lesson-viz-card"><strong>Healthy</strong><p>Pipeline-as-code, immutable artifact by digest, environment approvals.</p></div>
  </div>
  <figcaption>Signs of a mature vs fragile pipeline.</figcaption>
</figure>

<ul>
<li><strong>Manual production deploy</strong>: opens the door to recurring human
error — exactly what automation exists to
eliminate.</li>
<li><strong>Pipeline with no real tests</strong>: "deploy straight through" becomes
Russian roulette dressed up as process.</li>
<li><strong>High rate of bugs escaping with green CI</strong>: a direct signal
that existing tests do not cover what actually
matters.</li>
<li><strong>Slow pipeline (1h+)</strong>: nobody truly waits,
and the team learns to skip stages (section 2).</li>
<li><strong>Flaky (intermittent) tests</strong>: erode trust
in the CI signal itself — after a few random failures, the team
stops trusting real failures too.</li>
<li><strong>Build done "manually" straight in production</strong>: "I just
recompiled there" becomes exactly the kind of environment-specific bug nobody
can reproduce later.</li>
<li><strong>Only main is tested</strong>: without CI on PRs,
problems only appear AFTER merge, when they are more expensive to revert.</li>
</ul>

<h3>10. GitOps</h3>
<p>The GitOps principle: the Git repository is the source of truth for the
DESIRED cluster state, not a history of commands applied
manually. Argo CD or Flux continuously watch the repository
and reconcile the real cluster against what is declared — with no
manual <code>kubectl apply</code> in the middle:</p>
<pre><code># cluster/applications/app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: app, namespace: argocd }
spec:
  source:
    repoURL: https://github.com/empresa/k8s-config
    path: apps/app/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: prod
  syncPolicy:
    automated: { prune: true, selfHeal: true }</code></pre>
<p>The advantages follow directly from the model: rollback becomes a simple
<code>git revert</code>, audit becomes <code>git log</code>, and
drift detection is native — any manual change made outside
Git is automatically reverted by <code>selfHeal</code> on the next
reconciliation.</p>
""",
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Crie repo Python com app simples e suite de testes.</li>"
                    "<li>Adicione GitHub Actions: lint (ruff), test (pytest), security "
                    "(trivy + semgrep + gitleaks), build (Docker para GHCR), assina com "
                    "Cosign.</li>"
                    "<li>Configure tag por SHA + tag semver (release-please).</li>"
                    "<li>Adicione environment <code>production</code> com required reviewers + "
                    "wait timer 10min.</li>"
                    "<li>Implemente canary: deploy para 10% → smoke test → 50% → 100%, "
                    "com rollback automático em error rate.</li>"
                    "<li>Bonus: Argo CD em kind cluster apontando para repo de manifests; "
                    "demonstre GitOps (mude manifest, veja Argo aplicar).</li>"
                    "<li>Bonus 2: meça suas DORA metrics com Four Keys do Google.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Full hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>Create a Python repo with a simple app and a test suite.</li>"
                    "<li>Add GitHub Actions: lint (ruff), test (pytest), security "
                    "(trivy + semgrep + gitleaks), build (Docker to GHCR), sign with "
                    "Cosign.</li>"
                    "<li>Configure tagging by SHA + semver tag (release-please).</li>"
                    "<li>Add a <code>production</code> environment with required reviewers + "
                    "a 10-minute wait timer.</li>"
                    "<li>Implement canary: deploy to 10% → smoke test → 50% → 100%, "
                    "with automatic rollback on error rate.</li>"
                    "<li>Bonus: Argo CD on a kind cluster pointing at a manifests repo; "
                    "demonstrate GitOps (change a manifest, watch Argo apply it).</li>"
                    "<li>Bonus 2: measure your DORA metrics with Google's Four Keys.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("GitHub Actions docs", "https://docs.github.com/actions", "docs", "",
                  title_en="GitHub Actions docs", description_en=""),
                m("GitLab CI/CD", "https://docs.gitlab.com/ee/ci/", "docs", "",
                  title_en="GitLab CI/CD", description_en=""),
                m("Jenkins handbook", "https://www.jenkins.io/doc/book/", "docs", "",
                  title_en="Jenkins handbook", description_en=""),
                m("Continuous Delivery (livro)", "https://continuousdelivery.com/", "book", "",
                  title_en="Continuous Delivery (book)", description_en=""),
                m("Argo CD", "https://argo-cd.readthedocs.io/", "tool", "",
                  title_en="Argo CD", description_en=""),
                m("DORA metrics", "https://dora.dev/", "article", "Pesquisa do Google sobre DevOps.",
                  title_en="DORA metrics", description_en="Google research on DevOps."),
            ],
            "questions": [
                q("CI difere de CD porque:",
                  "CI integra/testa código; CD entrega/deploy automaticamente.",
                  ["CD pula a etapa de teste, indo direto para o deploy.",
                   "CI já inclui o deploy automático em produção, sem etapa a mais.",
                   "Os dois termos descrevem exatamente o mesmo processo, sem diferença."],
                  "CD pode ser delivery (manual aprovar) ou deployment (totalmente automático).",
                  statement_en="CI differs from CD because:",
                  correct_en="CI integrates/tests code; CD delivers/deploys automatically.",
                  wrong_en=["CD skips the test stage and goes straight to deploy.",
                            "CI already includes automatic production deploy, with no extra stage.",
                            "Both terms describe exactly the same process, with no difference."],
                  explanation_en="CD can mean delivery (manual approval) or deployment (fully automatic)."),
                q("Deploy canário:",
                  "Libera para uma fração de usuários antes do total.",
                  ["Uma ferramenta de edição de código, não uma estratégia de deploy.",
                   "Roda só em ambiente de desenvolvimento, fora de produção.",
                   "Substitui completamente a estratégia blue-green de deploy."],
                  "Origem: canário em mina de carvão. Métricas guiam quando avançar/reverter.",
                  statement_en="Canary deploy:",
                  correct_en="Releases to a fraction of users before everyone.",
                  wrong_en=["A code-editing tool, not a deploy strategy.",
                            "Runs only in a development environment, outside production.",
                            "Fully replaces the blue-green deploy strategy."],
                  explanation_en="Origin: canary in a coal mine. Metrics guide when to advance or roll back."),
                q("Pipeline as code é:",
                  "Definir o pipeline em arquivo versionado no repo.",
                  ["Deixar de vincular o pipeline a qualquer controle de versão.",
                   "Rodar o pipeline manualmente, disparado por alguém a cada vez.",
                   "Escrever o pipeline só em script bash, sem outro formato aceito."],
                  "Mudanças no pipeline passam pelo mesmo PR review do código.",
                  statement_en="Pipeline as code is:",
                  correct_en="Defining the pipeline in a versioned file in the repo.",
                  wrong_en=["Leaving the pipeline unbound from any version control.",
                            "Running the pipeline manually, triggered by someone each time.",
                            "Writing the pipeline only as a bash script, with no other accepted format."],
                  explanation_en="Pipeline changes go through the same PR review as application code."),
                q("Falha de teste deve:",
                  "Bloquear o merge/deploy.",
                  ["Ser ignorada, seguindo o pipeline até o final normalmente.",
                   "Acelerar o processo de release para compensar o atraso.",
                   "Gerar só um aviso (warning), sem impedir o merge."],
                  "Sem 'pode pode' o pipeline morre. Triagem ágil para flaky tests é essencial.",
                  statement_en="A test failure should:",
                  correct_en="Block the merge/deploy.",
                  wrong_en=["Be ignored, letting the pipeline finish normally.",
                            "Speed up the release process to make up for the delay.",
                            "Only emit a warning, without blocking the merge."],
                  explanation_en="Without a hard stop, the pipeline is dead. Agile triage for flaky tests is essential."),
                q("Rollback rápido depende de:",
                  "Artefatos imutáveis e healthchecks.",
                  ["Deixar de vincular o artefato a qualquer controle de versão.",
                   "Fazer só um backup do disco antes de cada deploy.",
                   "Reconstruir o artefato inteiro do zero a cada rollback necessário."],
                  "Re-deploy do artefato anterior leva segundos; rebuild leva minutos.",
                  statement_en="Fast rollback depends on:",
                  correct_en="Immutable artifacts and healthchecks.",
                  wrong_en=["Leaving the artifact unbound from any version control.",
                            "Only taking a disk backup before each deploy.",
                            "Rebuilding the entire artifact from scratch on every rollback."],
                  explanation_en="Re-deploying the previous artifact takes seconds; a rebuild takes minutes."),
                q("Cache em CI serve para:",
                  "Acelerar builds reaproveitando dependências.",
                  ["Compactar o log gerado durante a execução do pipeline.",
                   "Trocar o runner usado para executar o pipeline de CI.",
                   "Substituir a necessidade de rodar teste automatizado."],
                  "Cuide de invalidação correta (chave por lockfile, não por branch arbitrário).",
                  statement_en="CI cache is used to:",
                  correct_en="Speed up builds by reusing dependencies.",
                  wrong_en=["Compress logs produced while the pipeline runs.",
                            "Swap the runner used to execute the CI pipeline.",
                            "Replace the need to run automated tests."],
                  explanation_en="Mind correct invalidation (key by lockfile, not by an arbitrary branch)."),
                q("Matrix builds servem para:",
                  "Rodar a mesma pipeline com várias combinações (versões/SO).",
                  ["Reduzir o número de teste executado ao longo do pipeline de CI inteiro.",
                   "Aumentar o tamanho do cache usado durante o build da aplicação inteira.",
                   "Trocar a IDE usada pelo desenvolvedor durante o trabalho diário."],
                  "Ex.: testar Python 3.10/3.11/3.12 × Linux/macOS em paralelo.",
                  statement_en="Matrix builds are used to:",
                  correct_en="Run the same pipeline across several combinations (versions/OS).",
                  wrong_en=["Reduce the number of tests run across the whole CI pipeline.",
                            "Increase cache size used during the full application build.",
                            "Swap the IDE the developer uses for daily work."],
                  explanation_en="E.g. test Python 3.10/3.11/3.12 × Linux/macOS in parallel."),
                q("Trunk-based + CI/CD geralmente exige:",
                  "Feature flags e testes automatizados fortes.",
                  ["Rodar sem etapa de integração contínua configurada.",
                   "Fazer o deploy manualmente a cada nova versão lançada.",
                   "Manter branch de vida longa, aberta por semanas seguidas."],
                  "Sem flags, código incompleto não pode ir para main com segurança.",
                  statement_en="Trunk-based + CI/CD usually requires:",
                  correct_en="Feature flags and strong automated tests.",
                  wrong_en=["Running with no continuous integration stage configured.",
                            "Deploying manually for every new version released.",
                            "Keeping long-lived branches open for weeks."],
                  explanation_en="Without flags, incomplete code cannot safely land on main."),
                q("Artefato imutável significa:",
                  "Mesma versão (hash) é sempre a mesma, usado em todos os ambientes.",
                  ["Pode ser editado livremente depois de publicado, sem gerar nenhum hash novo.",
                   "Existe apenas localmente, na própria máquina que fez o build original.",
                   "Tem um TTL definido, expirando automaticamente depois de um tempo configurado."],
                  "Tag SHA + assinatura (Cosign) garante. 'latest' móvel é o oposto.",
                  statement_en="An immutable artifact means:",
                  correct_en="The same version (hash) is always identical, used across all environments.",
                  wrong_en=["It can be freely edited after publish without producing a new hash.",
                            "It exists only locally, on the machine that did the original build.",
                            "It has a defined TTL and expires automatically after a configured time."],
                  explanation_en="SHA tags + signing (Cosign) guarantee it. Movable 'latest' is the opposite."),
                q("Argo CD aplica padrão:",
                  "GitOps, repo Git é a fonte da verdade.",
                  ["Baseado em transferência de arquivo via FTP tradicional.",
                   "Aplicado manualmente por alguém direto no cluster.",
                   "Baseado em tarefa agendada (cron) rodando periodicamente."],
                  "Argo observa o repo; quando muda, reconcilia o cluster com o declarado.",
                  statement_en="Argo CD applies the pattern:",
                  correct_en="GitOps — the Git repo is the source of truth.",
                  wrong_en=["Based on traditional FTP file transfer.",
                            "Applied manually by someone directly on the cluster.",
                            "Based on a cron job running periodically."],
                  explanation_en="Argo watches the repo; when it changes, it reconciles the cluster to the declared state."),
            ],
        },
        # =====================================================================
        # 3.6 Linting
        # =====================================================================
        {
            "title": "Linting de Código e IaC",
            "title_en": 'Code and IaC Linting',
            "summary": "Ferramentas que avisam se você escreveu algo inseguro.",
            "summary_en": 'Tools that warn you when you wrote something insecure.',
            "lesson": {
                "intro": (
                    "Linter é a primeira linha de defesa contra bugs e más práticas. "
                    "Custa quase nada (segundos no editor + segundos no CI), pega ~80% do "
                    "que humano cansa de procurar em review, padroniza estilo (sem mais "
                    "discussões eternas sobre tabs vs spaces), e em alguns casos pega "
                    "anti-patterns de segurança óbvios. Ignorar linter é como dirigir sem "
                    "espelhos, possível, mas por quê?"
                ),
                "intro_en": (
                    "A linter is the first line of defense against bugs and bad practices. "
                    "It costs almost nothing (seconds in the editor + seconds in CI), catches ~80% of "
                    "what humans tire of hunting in review, standardizes style (no more endless "
                    "tabs-vs-spaces debates), and in some cases catches obvious security "
                    "anti-patterns. Ignoring a linter is like driving without mirrors — "
                    "possible, but why?"
                ),
                "body": (
                """<h3>1. O que linters fazem</h3>
<p>Um linter faz <strong>análise estática</strong>: lê o código sem
executá-lo e procura padrões, em cinco categorias amplas. A primeira é
<strong>estilo</strong> — indentação, naming, comprimento de linha, ordem
de imports — o tipo de coisa que consome minutos de review humano sem
agregar nada além de consistência visual. A segunda é <strong>bug
simples</strong>: variável nunca usada, comparação de tipo incorreta,
função que esquece de retornar em algum caminho. A terceira é
<strong>anti-pattern</strong> conhecido: uso de <code>eval()</code>,
regex catastrófico (que pode travar o processo com input adversarial),
argumento default mutável (armadilha clássica em Python), senha
hardcoded. A quarta é <strong>performance</strong>: sugerir list
comprehension em vez de loop equivalente, evitar concatenação de string
dentro de loop. E a quinta é <strong>type checking</strong> (mypy, tsc),
que verifica se os tipos declarados realmente batem entre si em
linguagens com type hint. Linter não substitui SAST — mas a fronteira
entre os dois ficou borrada: Bandit e Semgrep hoje cobrem os dois papéis
ao mesmo tempo.</p>
<div class="mermaid">
flowchart LR
    A["Código escrito"] --> B["Linter roda"]
    B --> C{"Viola regra?"}
    C -- Sim --> D["Bloqueia commit ou PR"]
    C -- Não --> E["Segue no CI"]
</div>


<h3>2. Linters por linguagem</h3>
<h4>2.1 Python</h4>
<p>O <strong>Ruff</strong> virou o novo padrão — escrito em Rust,
substitui <code>flake8</code>, <code>isort</code>,
<code>pyupgrade</code>, <code>autoflake</code> e <code>black</code> numa
única ferramenta, 10 a 100 vezes mais rápida, cobrindo lint e formatação
ao mesmo tempo. <strong>mypy</strong> e <strong>pyright</strong> cuidam
especificamente de type checking. E <strong>Bandit</strong> mantém foco
exclusivo em segurança, mesmo com Ruff já cobrindo boa parte disso via
plugin.</p>
<pre><code># pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"
[tool.ruff.lint]
select = [
  "E", "W",   # pycodestyle
  "F",         # pyflakes
  "I",         # isort
  "N",         # pep8-naming
  "UP",        # pyupgrade
  "B",         # bugbear
  "S",         # bandit
  "SIM",       # simplify
]
ignore = ["E501"]   # justifique cada um</code></pre>
<h4>2.2 JavaScript/TypeScript</h4>
<p><strong>ESLint</strong> continua sendo o padrão, extensível via
plugin (typescript-eslint, react, next, security). O
<strong>Prettier</strong> cuida só de formatação, deliberadamente
opinativo para eliminar debate de estilo. <code>tsc --noEmit</code> roda
o type checker do TypeScript sem gerar output. E o
<strong>Biome</strong>, escrito em Rust, é a alternativa mais recente que
integra lint e format numa ferramenta só, na mesma linha do Ruff para
Python.</p>
<h4>2.3 Go</h4>
<p><strong>golangci-lint</strong> agrega mais de 50 linters individuais
(errcheck, govet, ineffassign, gosec, staticcheck) sob uma configuração
única. <strong>gofmt</strong> e <strong>goimports</strong> cuidam da
formatação padrão da linguagem — Go é incomum em ter formatação oficial
imposta pela própria toolchain, eliminando de vez a discussão de
estilo.</p>
<h4>2.4 Shell/Bash</h4>
<p><strong>shellcheck</strong> é o padrão indiscutível — pega erro
sutil e comum como variável não citada (<code>$var</code> sem aspas,
que quebra com espaço no valor) ou um <code>cd $dir &amp;&amp; rm</code>
que apaga o diretório errado se o `cd` falhar silenciosamente.
<strong>shfmt</strong> cuida da formatação.</p>
<h4>2.5 Outros</h4>
<p>Cada formato de arquivo tende a ter seu linter dedicado:
<code>yamllint</code> para YAML, <code>markdownlint</code> para
Markdown, <code>jq</code> combinado com schema para JSON, e
<code>sqlfluff</code> para SQL.</p>

<h3>3. Linters de IaC</h3>
<h4>3.1 Dockerfile</h4>
<p><strong>hadolint</strong> pega anti-pattern específico de Docker —
coisas que só fazem sentido dentro do contexto de construção de
imagem:</p>
<pre><code>$ hadolint Dockerfile
Dockerfile:5 DL3008 Pin versions in apt-get install. Instead of `apt install foo`,
use `apt install foo=1.2.3`.
Dockerfile:7 DL3009 Delete the apt-get lists after installing.
Dockerfile:10 DL3025 Use arguments JSON notation for CMD and ENTRYPOINT.</code></pre>
<h4>3.2 Terraform</h4>
<p><strong>tflint</strong> é o lint específico do Terraform, com
rulesets por provider — a variante para AWS detecta instance type
inválido ou AMI inexistente antes mesmo de rodar plan.
<strong>tfsec</strong> e <strong>checkov</strong> focam em segurança:
bucket público, security group aberto para <code>0.0.0.0/0</code>,
encryption desabilitada. E <code>terraform fmt</code> cuida da
formatação nativa da linguagem.</p>
<h4>3.3 Kubernetes</h4>
<p><strong>kubeval</strong> e <strong>kubeconform</strong> validam o
manifesto contra o schema da versão do Kubernetes-alvo.
<strong>kube-linter</strong> e o similar <strong>polaris</strong> vão
além do schema e checam boas práticas de verdade — securityContext
definido, resource limits presentes, liveness probe configurada. E o
<strong>checkov</strong>, já citado para Terraform, também cobre
manifesto Kubernetes e chart Helm.</p>
<h4>3.4 Ansible</h4>
<p><strong>ansible-lint</strong> detecta task sem nome (dificulta
debugar output de playbook), uso de <code>shell</code> sem
<code>creates</code> (torna a task não-idempotente), e
<code>become</code> redundante onde já não é necessário.</p>

<h3>4. Pre-commit + CI: defesa em camadas</h3>
<div class="mermaid">
flowchart TD
    Local["Pre-commit no laptop"] --> PR["Checks no PR"]
    PR --> CI["Job de lint no CI"]
    CI --> Merge["Só então merge"]
</div>

<p>O padrão moderno é rodar tudo LOCALMENTE antes mesmo do commit — via
o framework <strong>pre-commit</strong> — e rodar de novo no CI como
segunda camada, porque nem todo desenvolvedor lembra de instalar o hook
local:</p>
<pre><code># .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff       # lint
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/hadolint/hadolint
    rev: v2.13.0-beta
    hooks:
      - id: hadolint-docker
  - repo: https://github.com/koalaman/shellcheck-precommit
    rev: v0.10.0
    hooks:
      - id: shellcheck
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
  - repo: https://github.com/aquasecurity/tfsec
    rev: v1.28.0
    hooks:
      - id: tfsec</code></pre>
<pre><code>$ pre-commit install   # instala hook git
$ pre-commit run --all-files   # roda em todo repo
ruff..............................Passed
hadolint..........................Failed
  Dockerfile:7 DL3009 Delete apt lists after install</code></pre>
<p>A razão de repetir tudo no CI (<code>pre-commit run --all-files</code>
de novo) é que um desenvolvedor pode pular o hook local com
<code>--no-verify</code> — o CI é a camada que não tem esse atalho de
saída.</p>

<h3>5. Auto-fix</h3>
<p>Boa parte dos linters modernos corrige o próprio problema que
encontra, quando a correção é mecânica e sem ambiguidade:
<code>ruff check --fix</code> organiza import e remove código morto,
<code>ruff format</code> formata no estilo black, <code>prettier
--write</code> cobre JS/TS/CSS/JSON/Markdown, e <code>terraform fmt
-recursive</code> formata HCL. Combinar isso com um bot no PR — lefthook,
treefmt, ou uma GitHub Action que commita a correção automaticamente —
elimina de vez o ciclo manual de "rodar, corrigir, commitar de novo".</p>

<h3>6. Falsos positivos: como lidar</h3>
<p>Suprimir um alerta de linter é legítimo, mas só quando vem
acompanhado do motivo explícito no próprio comentário — sem isso, a
supressão vira uma incógnita para quem ler o código depois:</p>
<pre><code>SQL = (
    "SELECT * FROM users WHERE id IN (" + ids_csv + ")"  # noqa: S608 - ids_csv é validado em validate_ids() acima
)</code></pre>
<p>Um <code># noqa</code> sem justificativa vira ruído permanente que
ninguém mais entende o porquê. Auditar supressões periodicamente
(<code>grep -r 'noqa' .</code>) é a forma de garantir que elas ainda
fazem sentido meses depois.</p>

<h3>7. Linter no editor</h3>
<p>Quando o erro aparece enquanto o código ainda está sendo digitado, o
custo de correção cai para quase zero — não é preciso esperar o CI
rodar minutos depois para descobrir um typo. VS Code, JetBrains,
Vim/Neovim e Emacs suportam isso nativamente via LSP, com integrações
específicas como ruff-lsp, ESLint e tflint.</p>

<h3>8. Anti-patterns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Evite</strong><p>Desligar regra globalmente, lint só local, configs divergentes por dev.</p></div>
    <div class="lesson-viz-card"><strong>Prefira</strong><p>Baseline versionada, auto-fix no CI, exceções locais documentadas.</p></div>
  </div>
  <figcaption>Anti-patterns de linting.</figcaption>
</figure>

<ul>
<li><strong>Desativar todas as regras</strong>: o linter deixa de ter
qualquer utilidade — em legado, migre ativando regra por regra
gradualmente, em vez de desligar tudo de uma vez.</li>
<li><strong>Suprimir sem comentar o motivo</strong>: vira lixo
permanente que ninguém mais entende (seção 6).</li>
<li><strong>Linter rodando só no CI</strong>: o feedback demora minutos
em vez de segundos — adicione pre-commit e integração no editor (seções
4 e 7).</li>
<li><strong>Discussão de estilo em code review</strong>: deixe isso para
o linter/formatter resolver automaticamente; humano deveria revisar
lógica, segurança e design, não indentação.</li>
<li><strong>Auto-fix aplicado sem revisar o diff</strong>: alguns
fixers são agressivos o suficiente para mudar semântica sem querer,
não só estilo.</li>
</ul>"""
                ),
                "body_en": """<h3>1. What linters do</h3>
<p>A linter performs <strong>static analysis</strong>: it reads code without
running it and looks for patterns, in five broad categories. The first is
<strong>style</strong> — indentation, naming, line length, import
order — the kind of thing that burns minutes of human review without
adding anything beyond visual consistency. The second is <strong>simple
bugs</strong>: unused variables, wrong type comparisons,
functions that forget to return on some path. The third is known
<strong>anti-patterns</strong>: use of <code>eval()</code>,
catastrophic regex (which can hang the process on adversarial input),
mutable default arguments (a classic Python trap), hardcoded
passwords. The fourth is <strong>performance</strong>: suggesting list
comprehensions instead of equivalent loops, avoiding string concatenation
inside loops. And the fifth is <strong>type checking</strong> (mypy, tsc),
which verifies that declared types actually agree in
languages with type hints. A linter does not replace SAST — but the line
between them has blurred: Bandit and Semgrep now cover both roles
at once.</p>
<div class="mermaid">
flowchart LR
    A["Code written"] --> B["Linter runs"]
    B --> C{"Rule violated?"}
    C -- Yes --> D["Blocks commit or PR"]
    C -- No --> E["Continues in CI"]
</div>


<h3>2. Linters by language</h3>
<h4>2.1 Python</h4>
<p><strong>Ruff</strong> became the new default — written in Rust,
it replaces <code>flake8</code>, <code>isort</code>,
<code>pyupgrade</code>, <code>autoflake</code>, and <code>black</code> in a
single tool, 10 to 100× faster, covering lint and formatting
at once. <strong>mypy</strong> and <strong>pyright</strong> handle
type checking specifically. And <strong>Bandit</strong> keeps an exclusive
focus on security, even with Ruff already covering much of that via
plugin.</p>
<pre><code># pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"
[tool.ruff.lint]
select = [
  "E", "W",   # pycodestyle
  "F",         # pyflakes
  "I",         # isort
  "N",         # pep8-naming
  "UP",        # pyupgrade
  "B",         # bugbear
  "S",         # bandit
  "SIM",       # simplify
]
ignore = ["E501"]   # justifique cada um</code></pre>
<h4>2.2 JavaScript/TypeScript</h4>
<p><strong>ESLint</strong> remains the standard, extensible via
plugins (typescript-eslint, react, next, security).
<strong>Prettier</strong> handles formatting only, deliberately
opinionated to kill style debates. <code>tsc --noEmit</code> runs
the TypeScript type checker without emitting output. And
<strong>Biome</strong>, written in Rust, is the newer alternative that
integrates lint and format in one tool, along the same lines as Ruff for
Python.</p>
<h4>2.3 Go</h4>
<p><strong>golangci-lint</strong> aggregates 50+ individual linters
(errcheck, govet, ineffassign, gosec, staticcheck) under one
configuration. <strong>gofmt</strong> and <strong>goimports</strong> handle the
language's standard formatting — Go is unusual in having official formatting
enforced by the toolchain itself, ending style debates for
good.</p>
<h4>2.4 Shell/Bash</h4>
<p><strong>shellcheck</strong> is the undisputed standard — it catches subtle,
common mistakes like unquoted variables (<code>$var</code> without quotes,
which breaks when the value has spaces) or a <code>cd $dir &amp;&amp; rm</code>
that deletes the wrong directory if `cd` fails silently.
<strong>shfmt</strong> handles formatting.</p>
<h4>2.5 Others</h4>
<p>Each file format tends to have its dedicated linter:
<code>yamllint</code> for YAML, <code>markdownlint</code> for
Markdown, <code>jq</code> plus schemas for JSON, and
<code>sqlfluff</code> for SQL.</p>

<h3>3. IaC linters</h3>
<h4>3.1 Dockerfile</h4>
<p><strong>hadolint</strong> catches Docker-specific anti-patterns —
things that only make sense in the context of building an
image:</p>
<pre><code>$ hadolint Dockerfile
Dockerfile:5 DL3008 Pin versions in apt-get install. Instead of `apt install foo`,
use `apt install foo=1.2.3`.
Dockerfile:7 DL3009 Delete the apt-get lists after installing.
Dockerfile:10 DL3025 Use arguments JSON notation for CMD and ENTRYPOINT.</code></pre>
<h4>3.2 Terraform</h4>
<p><strong>tflint</strong> is Terraform-specific linting, with
provider rulesets — the AWS variant detects invalid instance types
or nonexistent AMIs before plan even runs.
<strong>tfsec</strong> and <strong>checkov</strong> focus on security:
public buckets, security groups open to <code>0.0.0.0/0</code>,
disabled encryption. And <code>terraform fmt</code> handles the
language's native formatting.</p>
<h4>3.3 Kubernetes</h4>
<p><strong>kubeval</strong> and <strong>kubeconform</strong> validate
manifests against the target Kubernetes version schema.
<strong>kube-linter</strong> and similar <strong>polaris</strong> go
beyond the schema and check real best practices — securityContext
set, resource limits present, liveness probes configured. And
<strong>checkov</strong>, already mentioned for Terraform, also covers
Kubernetes manifests and Helm charts.</p>
<h4>3.4 Ansible</h4>
<p><strong>ansible-lint</strong> detects unnamed tasks (harder to
debug playbook output), <code>shell</code> without
<code>creates</code> (making the task non-idempotent), and
redundant <code>become</code> where it is no longer needed.</p>

<h3>4. Pre-commit + CI: defense in depth</h3>
<div class="mermaid">
flowchart TD
    Local["Pre-commit on laptop"] --> PR["Checks on PR"]
    PR --> CI["Lint job in CI"]
    CI --> Merge["Only then merge"]
</div>

<p>The modern pattern is to run everything LOCALLY before the commit — via
the <strong>pre-commit</strong> framework — and run again in CI as a
second layer, because not every developer remembers to install the local
hook:</p>
<pre><code># .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff       # lint
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/hadolint/hadolint
    rev: v2.13.0-beta
    hooks:
      - id: hadolint-docker
  - repo: https://github.com/koalaman/shellcheck-precommit
    rev: v0.10.0
    hooks:
      - id: shellcheck
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
  - repo: https://github.com/aquasecurity/tfsec
    rev: v1.28.0
    hooks:
      - id: tfsec</code></pre>
<pre><code>$ pre-commit install   # instala hook git
$ pre-commit run --all-files   # roda em todo repo
ruff..............................Passed
hadolint..........................Failed
  Dockerfile:7 DL3009 Delete apt lists after install</code></pre>
<p>The reason to repeat everything in CI (<code>pre-commit run --all-files</code>
again) is that a developer can skip the local hook with
<code>--no-verify</code> — CI is the layer that has no such escape
hatch.</p>

<h3>5. Auto-fix</h3>
<p>Most modern linters can fix the problems they
find when the fix is mechanical and unambiguous:
<code>ruff check --fix</code> organizes imports and removes dead code,
<code>ruff format</code> formats in black style, <code>prettier
--write</code> covers JS/TS/CSS/JSON/Markdown, and <code>terraform fmt
-recursive</code> formats HCL. Combining that with a PR bot — lefthook,
treefmt, or a GitHub Action that commits the fix automatically —
ends the manual cycle of "run, fix, commit again".</p>

<h3>6. False positives: how to handle them</h3>
<p>Suppressing a linter alert is legitimate, but only when it comes
with an explicit reason in the comment itself — without that, the
suppression becomes a mystery for whoever reads the code later:</p>
<pre><code>SQL = (
    "SELECT * FROM users WHERE id IN (" + ids_csv + ")"  # noqa: S608 - ids_csv é validado em validate_ids() acima
)</code></pre>
<p>A <code># noqa</code> without justification becomes permanent noise that
nobody understands anymore. Auditing suppressions periodically
(<code>grep -r 'noqa' .</code>) is how you ensure they still
make sense months later.</p>

<h3>7. Linters in the editor</h3>
<p>When the error appears while the code is still being typed, the
fix cost drops nearly to zero — no waiting for CI to
run minutes later to discover a typo. VS Code, JetBrains,
Vim/Neovim, and Emacs support this natively via LSP, with integrations
like ruff-lsp, ESLint, and tflint.</p>

<h3>8. Anti-patterns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Avoid</strong><p>Disabling a rule globally, lint only locally, configs diverge per developer.</p></div>
    <div class="lesson-viz-card"><strong>Prefer</strong><p>Versioned baseline, auto-fix in CI, documented local exceptions.</p></div>
  </div>
  <figcaption>Linting anti-patterns.</figcaption>
</figure>

<ul>
<li><strong>Disabling every rule</strong>: the linter stops being
useful at all — on legacy code, migrate by enabling rules
gradually instead of turning everything off at once.</li>
<li><strong>Suppressing without commenting why</strong>: becomes permanent
clutter nobody understands (section 6).</li>
<li><strong>Linter only in CI</strong>: feedback takes minutes
instead of seconds — add pre-commit and editor integration (sections
4 and 7).</li>
<li><strong>Style debates in code review</strong>: leave that to
the linter/formatter automatically; humans should review
logic, security, and design — not indentation.</li>
<li><strong>Auto-fix applied without reviewing the diff</strong>: some
fixers are aggressive enough to change semantics by accident,
not just style.</li>
</ul>""",
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Em projeto Python, configure <code>pyproject.toml</code> com "
                    "Ruff cobrindo: pycodestyle, pyflakes, isort, pyupgrade, bugbear, "
                    "bandit, simplify.</li>"
                    "<li>Adicione mypy ou pyright em modo strict para tipo.</li>"
                    "<li>Configure pre-commit com hooks: ruff, hadolint, shellcheck, "
                    "gitleaks, tflint (se houver TF), markdownlint, yamllint.</li>"
                    "<li>Adicione GitHub Action que roda <code>pre-commit run "
                    "--all-files</code>.</li>"
                    "<li>Configure VS Code para mostrar lint inline (extensions Ruff, "
                    "Pylance).</li>"
                    "<li>Rode em legado: arrume os fáceis com <code>--fix</code>, "
                    "documente os que precisam supressão consciente.</li>"
                    "<li>Bonus: bot de auto-format que comita correções no PR.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Full hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>In a Python project, configure <code>pyproject.toml</code> with "
                    "Ruff covering: pycodestyle, pyflakes, isort, pyupgrade, bugbear, "
                    "bandit, simplify.</li>"
                    "<li>Add mypy or pyright in strict mode for types.</li>"
                    "<li>Configure pre-commit with hooks: ruff, hadolint, shellcheck, "
                    "gitleaks, tflint (if you have TF), markdownlint, yamllint.</li>"
                    "<li>Add a GitHub Action that runs <code>pre-commit run "
                    "--all-files</code>.</li>"
                    "<li>Configure VS Code to show lint inline (Ruff, Pylance "
                    "extensions).</li>"
                    "<li>Run on legacy code: fix easy ones with <code>--fix</code>, "
                    "document those that need a conscious suppression.</li>"
                    "<li>Bonus: an auto-format bot that commits fixes on the PR.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("pre-commit", "https://pre-commit.com/", "tool", "",
                  title_en="pre-commit", description_en=""),
                m("Ruff (Python)", "https://docs.astral.sh/ruff/", "tool", "",
                  title_en="Ruff (Python)", description_en=""),
                m("hadolint (Dockerfile)", "https://github.com/hadolint/hadolint", "tool", "",
                  title_en="hadolint (Dockerfile)", description_en=""),
                m("tflint", "https://github.com/terraform-linters/tflint", "tool", "",
                  title_en="tflint", description_en=""),
                m("Checkov (IaC security)", "https://www.checkov.io/", "tool", "",
                  title_en="Checkov (IaC security)", description_en=""),
                m("ESLint", "https://eslint.org/docs/latest/", "docs", "",
                  title_en="ESLint", description_en=""),
            ],
            "questions": [
                q("hadolint detecta:",
                  "Más práticas em Dockerfiles.",
                  ["DNS quebrado, um problema de rede não relacionado a Dockerfile.",
                   "Erro de JavaScript, algo que hadolint não analisa nem entende.",
                   "Bug no código Java, fora do escopo de análise do hadolint."],
                  "Pega coisas como `apt-get install` sem `--no-install-recommends`, falta de USER.",
                  statement_en="hadolint detects:",
                  correct_en="Bad practices in Dockerfiles.",
                  wrong_en=["Broken DNS — a network issue unrelated to Dockerfiles.",
                            "JavaScript errors — something hadolint does not analyze.",
                            "Bugs in Java code — outside hadolint's analysis scope."],
                  explanation_en="Catches things like `apt-get install` without `--no-install-recommends`, missing USER."),
                q("Linter difere de SAST porque:",
                  "Linter foca em estilo/erros simples; SAST em vulnerabilidades.",
                  ["SAST não roda dentro de pipeline de CI moderno algum.",
                   "Linter serve só para código escrito em JavaScript ou TypeScript.",
                   "Os dois termos descrevem exatamente a mesma coisa, sem diferença."],
                  "Linha entre os dois é borrada hoje (Bandit, Semgrep cobrem ambos).",
                  statement_en="A linter differs from SAST because:",
                  correct_en="Linters focus on style/simple errors; SAST on vulnerabilities.",
                  wrong_en=["SAST never runs inside any modern CI pipeline.",
                            "Linters only work for JavaScript or TypeScript code.",
                            "Both terms describe exactly the same thing, with no difference."],
                  explanation_en="The line between them is blurred today (Bandit, Semgrep cover both)."),
                q("pre-commit serve para:",
                  "Rodar verificações antes do commit.",
                  ["Apagar um branch específico do repositório remoto.",
                   "Substituir completamente a necessidade de ter um CI configurado.",
                   "Compactar o log gerado durante a execução do commit."],
                  "Feedback em segundos. CI ainda valida no servidor (defesa em camadas).",
                  statement_en="pre-commit is used to:",
                  correct_en="Run checks before the commit.",
                  wrong_en=["Delete a specific branch from the remote repository.",
                            "Fully replace the need to have CI configured.",
                            "Compress logs produced during the commit."],
                  explanation_en="Feedback in seconds. CI still validates on the server (defense in depth)."),
                q("Configurar linter no CI evita:",
                  "Que erros de estilo quebrem o build/peças posteriores.",
                  ["Um backup automático do repositório antes de cada commit.",
                   "O custo mensal cobrado pela ferramenta de linter escolhida.",
                   "A latência de resposta percebida ao rodar o linter localmente."],
                  "Style guide automatizado é menos cansativo que review humano.",
                  statement_en="Configuring a linter in CI avoids:",
                  correct_en="Style errors breaking the build / later stages.",
                  wrong_en=["An automatic repository backup before each commit.",
                            "The monthly cost charged by the chosen linter tool.",
                            "Perceived response latency when running the linter locally."],
                  explanation_en="An automated style guide is less exhausting than human review."),
                q("Falsos positivos podem ser:",
                  "Suprimidos com comentários # noqa, // eslint-disable, etc.",
                  ["Um bug dentro do próprio compilador da linguagem utilizada.",
                   "Ignorados só em ambiente de produção, sem afetar outro estágio.",
                   "Erros reais que precisam ser corrigidos antes do próximo deploy."],
                  "Sempre justifique no comentário; supressão sem motivo vira lixo.",
                  statement_en="False positives can be:",
                  correct_en="Suppressed with comments like # noqa, // eslint-disable, etc.",
                  wrong_en=["A bug inside the language compiler itself.",
                            "Ignored only in production, without affecting other stages.",
                            "Real errors that must be fixed before the next deploy."],
                  explanation_en="Always justify in the comment; unexplained suppressions become clutter."),
                q("Por que não desativar todas as regras?",
                  "Reduz a utilidade do linter quase a zero.",
                  ["Torna a execução do linter mais rápida no editor.",
                   "Faz o pipeline de CI passar mesmo com problema real presente.",
                   "Reduz o custo mensal pago pela licença da ferramenta."],
                  "Time perde o feedback. Em legados, ative gradualmente em vez de desligar tudo.",
                  statement_en="Why not disable every rule?",
                  correct_en="It reduces the linter's usefulness almost to zero.",
                  wrong_en=["It makes the linter run faster in the editor.",
                            "It makes the CI pipeline pass even with a real problem present.",
                            "It reduces the monthly cost of the tool license."],
                  explanation_en="The team loses feedback. On legacy code, enable rules gradually instead of turning everything off."),
                q("ruff substitui:",
                  "Vários linters Python (flake8, isort, etc.) com performance maior.",
                  ["Substitui completamente a linguagem Python inteira, não só o linter.",
                   "Substitui o framework de teste pytest usado no projeto.",
                   "Substitui o gerenciador de pacote pip usado para instalar dependência."],
                  "Escrito em Rust; lint + format. Reduz minutos de CI para segundos.",
                  statement_en="ruff replaces:",
                  correct_en="Several Python linters (flake8, isort, etc.) with higher performance.",
                  wrong_en=["The entire Python language itself, not just the linter.",
                            "The pytest test framework used in the project.",
                            "The pip package manager used to install dependencies."],
                  explanation_en="Written in Rust; lint + format. Shrinks minutes of CI into seconds."),
                q("Lint em IaC importa porque:",
                  "Erros em IaC se traduzem em erros de produção.",
                  ["Reduz o custo mensal da infraestrutura provisionada pelo Terraform.",
                   "Bloqueia a criação de política nova dentro do IAM da conta.",
                   "Acelera a execução do comando plan do Terraform localmente."],
                  "tfsec/checkov barram bucket público, role com '*' antes do plan.",
                  statement_en="Linting IaC matters because:",
                  correct_en="IaC mistakes translate into production mistakes.",
                  wrong_en=["It reduces the monthly cost of infrastructure provisioned by Terraform.",
                            "It blocks creation of new policies inside the account IAM.",
                            "It speeds up Terraform plan locally."],
                  explanation_en="tfsec/checkov block public buckets and roles with '*' before plan."),
                q("Editor integration de linter:",
                  "Mostra problemas em tempo real, encurtando o feedback.",
                  ["Decora a interface do editor, sem trazer benefício funcional real.",
                   "É um recurso opcional, útil só para quem está começando agora.",
                   "Substitui completamente a necessidade de rodar o CI depois."],
                  "Erros aparecem enquanto digita. Reduz tempo de mental context-switch.",
                  statement_en="Editor integration for a linter:",
                  correct_en="Shows issues in real time, shortening feedback.",
                  wrong_en=["Decorates the editor UI without real functional benefit.",
                            "Is optional, useful only for beginners.",
                            "Fully replaces the need to run CI afterward."],
                  explanation_en="Errors appear as you type. Reduces mental context-switching time."),
                q("Auto-fix em linters:",
                  "Aplica correções automaticamente quando seguro.",
                  ["Reverte o código para uma versão anterior automaticamente.",
                   "Apaga arquivo considerado desnecessário pelo linter.",
                   "Quebra o commit em vários pedaços menores automaticamente."],
                  "Bom para imports, formatação. Tenha cuidado com regras semânticas (ex.: cuidado com fixers que mudam comportamento).",
                  statement_en="Auto-fix in linters:",
                  correct_en="Applies corrections automatically when it is safe.",
                  wrong_en=["Reverts code to a previous version automatically.",
                            "Deletes files the linter considers unnecessary.",
                            "Splits the commit into several smaller pieces automatically."],
                  explanation_en="Good for imports and formatting. Be careful with semantic rules (fixers that change behavior)."),
            ],
        },
        # =====================================================================
        # 3.7 SAST
        # =====================================================================
        {
            "title": "SAST",
            "title_en": 'SAST',
            "summary": "Análise estática de código no pipeline.",
            "summary_en": 'Static code analysis in the pipeline.',
            "lesson": {
                "intro": (
                    "SAST (Static Application Security Testing) é o 'antivírus do código': "
                    "lê seu source code sem executá-lo e procura padrões inseguros, SQL "
                    "injection, XSS, deserialização perigosa, path traversal, hardcoded "
                    "secrets. É a defesa mais barata contra vulnerabilidades clássicas, "
                    "acha em segundos o que humano em review não veria. Não é infalível "
                    "(não substitui DAST nem pentest), mas pega muito do baixo-pendurado. "
                    "Esta aula cobre como funciona, ferramentas, integração no PR, triagem "
                    "de falsos positivos e custom rules para padrões do seu domínio."
                ),
                "intro_en": (
                    "SAST (Static Application Security Testing) is the 'antivirus for code': "
                    "it reads your source without executing it and looks for insecure patterns — SQL "
                    "injection, XSS, dangerous deserialization, path traversal, hardcoded "
                    "secrets. It is the cheapest defense against classic vulnerabilities, "
                    "finding in seconds what a human in review would miss. It is not infallible "
                    "(it does not replace DAST or pentests), but it catches a lot of low-hanging fruit. "
                    "This lesson covers how it works, tools, PR integration, false-positive "
                    "triage, and custom rules for patterns in your domain."
                ),
                "body": (
                """<h3>1. Como SAST funciona internamente</h3>
<p>Cinco etapas transformam código-fonte em achado de vulnerabilidade.
Primeiro, <strong>parsing</strong> transforma o texto do código numa AST
(Abstract Syntax Tree) — uma estrutura de árvore que representa a
sintaxe sem ambiguidade. Depois, a <strong>análise de fluxo de
controle</strong> (CFG) mapeia como a execução pode pular entre blocos —
qual `if` leva a qual `return`, onde um loop pode terminar. A etapa mais
importante é a <strong>análise de fluxo de dados</strong> (taint
analysis): ela rastreia um valor "sujo" — tipicamente input vindo do
usuário — desde onde ele entra no sistema (a "source") até onde ele
chega a fazer algo perigoso (o "sink", como executar SQL, chamar shell,
rodar `eval`). Se esse valor sujo percorre esse caminho SEM passar por
nenhuma sanitização no meio, a ferramenta reporta vulnerabilidade —
mesmo sem nunca ter executado o código de verdade:</p>
<div class="mermaid">
flowchart LR
    A["Código-fonte"] --> B["SAST analisa sem executar"]
    B --> C{"Padrão vulnerável?"}
    C -- Sim --> D["Reporta linha e tipo"]
    C -- Não --> E["Aprova o build"]
</div>

<pre><code>def view(request):
    user_id = request.GET.get('id')        # source: tainted
    query = f"SELECT * FROM u WHERE id={user_id}"   # propaga taint
    cursor.execute(query)                  # sink: SQL injection!</code></pre>
<p>Uma sanitização de verdade interrompe essa cadeia — o taint para de
se propagar porque o valor deixou de ser o input bruto do usuário:</p>
<pre><code>user_id = int(request.GET.get('id'))  # cast → não tainted (escopo)
cursor.execute("SELECT * FROM u WHERE id=%s", [user_id])  # parametrizado, ok</code></pre>
<p>Depois disso vem a <strong>aplicação de regras</strong> — padrões
pré-definidos (cobrindo OWASP Top 10) ou custom, escritos para o domínio
específico da empresa — e por fim o <strong>reporte</strong>, tipicamente
em formato SARIF, JSON ou HTML, consumível tanto por humano quanto por
outra ferramenta no pipeline.</p>

<h3>2. Tipos de regras</h3>
<p>Nem toda regra de SAST funciona do mesmo jeito, e a escolha do tipo
afeta diretamente precisão e custo computacional. Um <strong>pattern
simples</strong> é regex ou AST básico procurando uma chamada específica
— Bandit <code>B102</code>, por exemplo, sinaliza qualquer uso de
<code>exec()</code>, sem entender contexto nenhum ao redor. A
<strong>taint analysis</strong> (seção 1) já rastreia o caminho completo
source → sanitizer → sink, muito mais precisa mas também muito mais
cara de computar, porque precisa simular fluxo de dados através de todo
o programa. A <strong>execução simbólica</strong> vai além: simula a
execução do programa com valores simbólicos (não valores concretos),
capaz de encontrar bugs profundos que dependem de combinações raras de
condição. E as <strong>custom rules</strong> são as que a própria empresa
escreve para seu domínio específico — por exemplo, "qualquer log que
inclua a variável <code>cpf</code> bloqueia o merge", um padrão que
nenhuma ferramenta genérica conheceria de antemão.</p>

<h3>3. Ferramentas open source</h3>
<h4>3.1 Semgrep</h4>
<p>Tornou-se o padrão moderno por combinar sintaxe simples (YAML mais
um pattern que lembra o próprio código) com suporte multi-linguagem e
regras OWASP já prontas para uso, além de facilitar escrever regra
custom sem precisar aprender uma DSL complexa:</p>
<pre><code># .semgrep/no-print-in-prod.yml
rules:
  - id: no-print
    languages: [python]
    severity: WARNING
    message: "Use logging em vez de print()"
    pattern: print(...)
    paths:
      include: ['app/**/*.py']
      exclude: ['tests/**', 'scripts/**']</code></pre>
<pre><code>$ semgrep --config p/owasp-top-ten
$ semgrep --config p/python --config .semgrep/
$ semgrep --config auto   # detecta linguagem e usa registry</code></pre>
<h4>3.2 Bandit (Python)</h4>
<pre><code>$ bandit -r app/
&gt;&gt; Issue: [B201:flask_debug_true] A Flask app appears to be run with debug=True
   Severity: High   Confidence: Medium
   Location: app.py:42</code></pre>
<h4>3.3 CodeQL (GitHub)</h4>
<p>Segue uma abordagem diferente: constrói um banco de fatos sobre todo
o código do repositório, e permite escrever queries no estilo SQL para
buscar padrões arbitrariamente complexos — muito mais poderoso que
regex, e gratuito para repositórios públicos:</p>
<pre><code>// query CodeQL
import python
from FunctionDef f
where f.getName() = "login" and not exists(f.getBody().getAStmt())
select f, "Função login sem corpo"</code></pre>
<h4>3.4 Outros</h4>
<p>Cada linguagem tende a ter sua ferramenta especializada dominante:
<strong>Brakeman</strong> para Ruby/Rails, <strong>gosec</strong> para
Go, <strong>SpotBugs</strong>/Find-Sec-Bugs para Java. E o
<strong>SonarQube</strong>/SonarCloud, comercial com camada gratuita,
combina SAST com métricas gerais de qualidade de código na mesma
ferramenta.</p>

<h3>4. Integração no pipeline</h3>
<div class="mermaid">
flowchart TD
    Push["Push / PR"] --> SAST["Job SAST"]
    SAST --> Gate{"Severidade alta?"}
    Gate -- Sim --> Block["Bloqueia merge"]
    Gate -- Não --> Ok["Segue pipeline"]
</div>

<p>O ponto ideal de integração é como check obrigatório no próprio PR,
não como relatório separado que alguém consulta depois:</p>
<pre><code># GitHub Actions
- name: Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: p/owasp-top-ten
    auditOn: push
    publishToken: ${{ secrets.SEMGREP_APP_TOKEN }}</code></pre>
<p>Rodar SAST pela primeira vez num código legado tipicamente produz
centenas de achados acumulados ao longo de anos — bloquear merge por
todos eles de uma vez paralisa o time inteiro. A saída é configurar
<strong>diff-only</strong>: comentar no PR apenas os achados nas linhas
que aquele PR especificamente tocou, deixando o legado para um esforço
dedicado de tech-debt, sem travar trabalho novo. A regra de bloqueio
então segue a severidade: Critical/High bloqueia o merge diretamente;
Medium vira issue automática com prazo dentro do sprint; Low/Info só
entra no backlog, sem obrigar ação imediata.</p>

<h3>5. Triagem de falsos positivos</h3>
<p>Falso positivo é normal — muitos padrões de vulnerabilidade dependem
de contexto que a ferramenta não tem como enxergar sozinha. O que evita
que isso vire caos é um processo estruturado: uma triagem semanal, feita
por um security champion ou squad rotativo; ao confirmar que é
realmente falso positivo, a supressão vai DIRETO no código com
justificativa explícita (<code># nosec - input validado em
validate()</code>), nunca silenciosa; alternativamente, um arquivo de
baseline (<code>.semgrepignore</code>) registra supressões em lote; e
uma auditoria trimestral revisita supressões antigas, porque o código ao
redor pode ter mudado desde que a supressão foi justificada. O erro
mais caro aqui é suprimir "em massa" sem analisar cada caso — isso vira
um tapa-buraco que esconde achado real junto com os falsos.</p>

<h3>6. SAST vs DAST vs IAST vs SCA, complementares</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>SAST</strong><p>Achados no código parado: injection, secrets hard-coded, APIs inseguras.</p></div>
    <div class="lesson-viz-card"><strong>DAST</strong><p>Achados em runtime: auth bypass, XSS refletido, misconfig exposta.</p></div>
  </div>
  <figcaption>SAST e DAST se complementam — um não substitui o outro.</figcaption>
</figure>

<table>
<tr><th>Tipo</th><th>O que olha</th><th>Quando</th><th>Exemplo</th></tr>
<tr><td>SAST</td><td>Código (white box)</td><td>Pré-deploy/PR</td><td>Semgrep, CodeQL</td></tr>
<tr><td>DAST</td><td>App rodando (black box)</td><td>Staging/QA</td><td>OWASP ZAP, Burp</td></tr>
<tr><td>IAST</td><td>Agente em runtime</td><td>QA com tráfego</td><td>Contrast, Seeker</td></tr>
<tr><td>SCA</td><td>Dependências</td><td>Pre-deploy/contínuo</td><td>Trivy, Dependabot</td></tr>
<tr><td>Pentest</td><td>App + infra (humano)</td><td>Periódico</td><td>Consultoria/red team</td></tr>
</table>
<p>Nenhum desses métodos sozinho cobre tudo, e cada um pega uma classe
diferente de problema: SAST alcança lógica interna que DAST jamais
testaria por acaso, como um caminho de código raro só atingido por uma
combinação específica de parâmetros; DAST, por sua vez, pega
misconfiguração de servidor ou runtime que simplesmente não existe no
código-fonte (é uma configuração de ambiente, não uma linha de Python);
SCA pega CVE conhecida em dependência de terceiro, algo que nem SAST nem
DAST enxergam porque o código vulnerável não foi escrito pelo próprio
time; e pentest combina criatividade humana, ferramenta automatizada e
entendimento de lógica de negócio — capaz de encadear falhas
individualmente pequenas em um comprometimento real, algo que nenhuma
ferramenta automatizada replica de forma confiável.</p>

<h3>7. Custom rules: o real diferencial</h3>
<p>Regras default cobrem o OWASP Top 10 — útil, mas é exatamente o mesmo
conjunto que toda outra empresa também roda. O que realmente diferencia
uma configuração de SAST madura são as custom rules, que capturam
padrão INTERNO específico daquele código:</p>
<pre><code>rules:
  - id: no-direct-db-cursor
    pattern: connection.cursor()
    message: "Use UnitOfWork em vez de cursor direto. Ver ADR-12."
    severity: ERROR
    languages: [python]
    paths: { include: ['app/**'], exclude: ['app/db/uow.py'] }

  - id: log-sem-mascarar-cpf
    pattern-either:
      - pattern: logger.info(f"...{$X.cpf}...")
      - pattern: logger.info(f"...{$X.email}...")
    message: "PII em log, use mask_pii()"
    severity: ERROR
    languages: [python]</code></pre>
<p>O caminho recomendado é começar pequeno — 3 a 5 regras que capturam
os erros mais recorrentes vistos em code review — e crescer com o
tempo. Cada regra nova elimina um tipo de bug que, de outra forma,
continuaria sendo pego manualmente review após review.</p>

<h3>8. Métricas úteis</h3>
<p>Quatro números indicam se o programa de SAST está funcionando de
verdade ou só gerando ruído. O <strong>MTTR por severidade</strong> mede
o tempo médio até um achado ser corrigido — se um Critical demora
semanas, a prioridade declarada não bate com a prática real. A
<strong>taxa de falso positivo</strong> — a fração de achados que vira
supressão justificada — sinaliza problema de calibração quando passa de
30%: nesse ponto as regras estão gerando mais ruído que sinal e
precisam de ajuste. <strong>Achados por mil linhas novas</strong> (KLOC)
mostra a tendência: se está subindo, o código novo está entrando pior
que o antigo. E o <strong>tempo de análise no CI</strong> importa porque
um SAST que leva mais de cinco minutos por PR vira fricção suficiente
para o time começar a ignorar ou pular a etapa.</p>

<h3>9. Limitações de SAST</h3>
<p>SAST simplesmente não enxerga uma categoria inteira de problema, por
definição — tudo que só existe em RUNTIME fica fora do alcance de uma
análise que nunca executa o código: misconfiguração de servidor
(<code>debug=True</code> vindo de variável de ambiente, não do
código-fonte), falha de autenticação ou autorização que só se manifesta
com dado real de sessão, condição de corrida (race condition) que só
aparece sob concorrência real, falha de lógica de negócio complexa (um
preço negativo sendo aceito pelo checkout), ou vulnerabilidade num
serviço de terceiro chamado via API, cujo código nunca passa pelo
scanner. É exatamente por essa lacuna que SAST precisa vir combinado com
DAST, observabilidade em produção, threat modeling e pentest periódico —
defesa em profundidade, não uma única camada tentando cobrir tudo.</p>

<h3>10. Anti-patterns</h3>
<ul>
<li><strong>Comprar ferramenta cara e deixar gerar relatório de mil
páginas que ninguém lê</strong>: sem integração direta no PR (seção 4),
o investimento não produz efeito real.</li>
<li><strong>Bloquear todos os achados de uma vez em legado</strong>:
ninguém consegue mais dar merge em nada — use baseline mais diff-only
(seção 4) em vez disso.</li>
<li><strong>Suprimir todo falso positivo sem ler caso a caso</strong>:
esconde achado real junto com o ruído (seção 5).</li>
<li><strong>Usar apenas regra default</strong>: pega o óbvio que todo
mundo já pega, mas perde exatamente o padrão interno que mais importa
para aquele código (seção 7).</li>
<li><strong>Nunca atualizar as regras</strong>: novo padrão de ataque
aparece constantemente; regra desatualizada para de pegar o que hoje já
é conhecido.</li>
</ul>"""
                ),
                "body_en": """<h3>1. How SAST works internally</h3>
<p>Five stages turn source code into a vulnerability finding.
First, <strong>parsing</strong> turns code text into an AST
(Abstract Syntax Tree) — a tree that represents
syntax without ambiguity. Next, <strong>control-flow
analysis</strong> (CFG) maps how execution can jump between blocks —
which `if` leads to which `return`, where a loop can end. The most
important stage is <strong>data-flow analysis</strong> (taint
analysis): it tracks a "dirty" value — typically user
input — from where it enters the system (the "source") to where it
does something dangerous (the "sink", such as running SQL, calling a shell,
or running `eval`). If that dirty value travels that path WITHOUT any
sanitization in between, the tool reports a vulnerability —
even without ever executing the real code:</p>
<div class="mermaid">
flowchart LR
    A["Source code"] --> B["SAST analyzes without running"]
    B --> C{"Vulnerable pattern?"}
    C -- Yes --> D["Reports line and type"]
    C -- No --> E["Approves the build"]
</div>

<pre><code>def view(request):
    user_id = request.GET.get('id')        # source: tainted
    query = f"SELECT * FROM u WHERE id={user_id}"   # propaga taint
    cursor.execute(query)                  # sink: SQL injection!</code></pre>
<p>Real sanitization breaks that chain — the taint stops
propagating because the value is no longer raw user input:</p>
<pre><code>user_id = int(request.GET.get('id'))  # cast → não tainted (escopo)
cursor.execute("SELECT * FROM u WHERE id=%s", [user_id])  # parametrizado, ok</code></pre>
<p>After that comes <strong>rule application</strong> — predefined
patterns (covering the OWASP Top 10) or custom ones written for the company's
specific domain — and finally <strong>reporting</strong>, typically
in SARIF, JSON, or HTML, consumable by both humans and other
pipeline tools.</p>

<h3>2. Rule types</h3>
<p>Not every SAST rule works the same way, and the type you choose
directly affects precision and compute cost. A <strong>simple
pattern</strong> is regex or a basic AST match looking for a specific call
— Bandit <code>B102</code>, for example, flags any use of
<code>exec()</code> without understanding surrounding context.
<strong>Taint analysis</strong> (section 1) tracks the full
source → sanitizer → sink path — much more precise but also much more
expensive, because it must simulate data flow through the whole
program. <strong>Symbolic execution</strong> goes further: it simulates
program execution with symbolic values (not concrete ones),
able to find deep bugs that depend on rare combinations of
conditions. And <strong>custom rules</strong> are what the company itself
writes for its domain — for example, "any log that
includes the <code>cpf</code> variable blocks the merge", a pattern
no generic tool would know in advance.</p>

<h3>3. Open-source tools</h3>
<h4>3.1 Semgrep</h4>
<p>It became the modern default by combining simple syntax (YAML plus
a pattern that looks like the code itself) with multi-language support and
ready-made OWASP rules, plus making custom rules easy
without learning a complex DSL:</p>
<pre><code># .semgrep/no-print-in-prod.yml
rules:
  - id: no-print
    languages: [python]
    severity: WARNING
    message: "Use logging em vez de print()"
    pattern: print(...)
    paths:
      include: ['app/**/*.py']
      exclude: ['tests/**', 'scripts/**']</code></pre>
<pre><code>$ semgrep --config p/owasp-top-ten
$ semgrep --config p/python --config .semgrep/
$ semgrep --config auto   # detecta linguagem e usa registry</code></pre>
<h4>3.2 Bandit (Python)</h4>
<pre><code>$ bandit -r app/
&gt;&gt; Issue: [B201:flask_debug_true] A Flask app appears to be run with debug=True
   Severity: High   Confidence: Medium
   Location: app.py:42</code></pre>
<h4>3.3 CodeQL (GitHub)</h4>
<p>Takes a different approach: it builds a fact database over the whole
repository and lets you write SQL-like queries to
find arbitrarily complex patterns — far more powerful than
regex, and free for public repositories:</p>
<pre><code>// query CodeQL
import python
from FunctionDef f
where f.getName() = "login" and not exists(f.getBody().getAStmt())
select f, "Função login sem corpo"</code></pre>
<h4>3.4 Others</h4>
<p>Each language tends to have a dominant specialized tool:
<strong>Brakeman</strong> for Ruby/Rails, <strong>gosec</strong> for
Go, <strong>SpotBugs</strong>/Find-Sec-Bugs for Java. And
<strong>SonarQube</strong>/SonarCloud, commercial with a free tier,
combines SAST with general code-quality metrics in the same
tool.</p>

<h3>4. Pipeline integration</h3>
<div class="mermaid">
flowchart TD
    Push["Push / PR"] --> SAST["SAST job"]
    SAST --> Gate{"High severity?"}
    Gate -- Yes --> Block["Blocks merge"]
    Gate -- No --> Ok["Pipeline continues"]
</div>

<p>The ideal integration point is as a required check on the PR itself,
not as a separate report someone consults later:</p>
<pre><code># GitHub Actions
- name: Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: p/owasp-top-ten
    auditOn: push
    publishToken: ${{ secrets.SEMGREP_APP_TOKEN }}</code></pre>
<p>Running SAST for the first time on legacy code typically produces
hundreds of findings accumulated over years — blocking merge on
all of them at once paralyzes the whole team. The way out is
<strong>diff-only</strong>: comment on the PR only findings on lines
that PR specifically touched, leaving legacy for a dedicated
tech-debt effort without blocking new work. The blocking rule
then follows severity: Critical/High blocks merge directly;
Medium becomes an automatic issue with a sprint deadline; Low/Info only
enters the backlog, without forcing immediate action.</p>

<h3>5. Triaging false positives</h3>
<p>False positives are normal — many vulnerability patterns depend on
context the tool cannot see alone. What prevents
chaos is a structured process: weekly triage by a
security champion or rotating squad; when confirming a true
false positive, suppression goes DIRECTLY in code with an
explicit justification (<code># nosec - input validated in
validate()</code>), never silent; alternatively, a baseline file
(<code>.semgrepignore</code>) records bulk suppressions; and a
quarterly audit revisits old suppressions, because surrounding code may
have changed since the suppression was justified. The most expensive
mistake here is suppressing "in bulk" without analyzing each case — that
becomes a cover-up that hides real findings along with the false ones.</p>

<h3>6. SAST vs DAST vs IAST vs SCA — complementary</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>SAST</strong><p>Findings in static code: injection, hard-coded secrets, unsafe APIs.</p></div>
    <div class="lesson-viz-card"><strong>DAST</strong><p>Findings at runtime: auth bypass, reflected XSS, exposed misconfig.</p></div>
  </div>
  <figcaption>SAST and DAST complement each other — neither replaces the other.</figcaption>
</figure>

<table>
<tr><th>Type</th><th>What it looks at</th><th>When</th><th>Example</th></tr>
<tr><td>SAST</td><td>Code (white box)</td><td>Pre-deploy/PR</td><td>Semgrep, CodeQL</td></tr>
<tr><td>DAST</td><td>Running app (black box)</td><td>Staging/QA</td><td>OWASP ZAP, Burp</td></tr>
<tr><td>IAST</td><td>Runtime agent</td><td>QA with traffic</td><td>Contrast, Seeker</td></tr>
<tr><td>SCA</td><td>Dependencies</td><td>Pre-deploy/continuous</td><td>Trivy, Dependabot</td></tr>
<tr><td>Pentest</td><td>App + infra (human)</td><td>Periodic</td><td>Consultancy/red team</td></tr>
</table>
<p>None of these methods alone covers everything, and each catches a different
class of problem: SAST reaches internal logic DAST would never
hit by chance, such as a rare code path only reached by a
specific parameter combination; DAST, in turn, catches
server or runtime misconfiguration that simply does not exist in
source code (it is environment config, not a line of Python);
SCA catches known CVEs in third-party dependencies — something neither SAST nor
DAST sees because the vulnerable code was not written by your
team; and pentests combine human creativity, automated tools, and
business-logic understanding — able to chain individually small
flaws into a real compromise no automated tool reliably
replicates.</p>

<h3>7. Custom rules: the real differentiator</h3>
<p>Default rules cover the OWASP Top 10 — useful, but exactly the same
set every other company also runs. What really differentiates a mature
SAST setup are custom rules that capture
INTERNAL patterns specific to that codebase:</p>
<pre><code>rules:
  - id: no-direct-db-cursor
    pattern: connection.cursor()
    message: "Use UnitOfWork em vez de cursor direto. Ver ADR-12."
    severity: ERROR
    languages: [python]
    paths: { include: ['app/**'], exclude: ['app/db/uow.py'] }

  - id: log-sem-mascarar-cpf
    pattern-either:
      - pattern: logger.info(f"...{$X.cpf}...")
      - pattern: logger.info(f"...{$X.email}...")
    message: "PII em log, use mask_pii()"
    severity: ERROR
    languages: [python]</code></pre>
<p>The recommended path is to start small — 3 to 5 rules that capture
the most recurring mistakes seen in code review — and grow over
time. Each new rule eliminates a bug type that would otherwise
keep being caught manually review after review.</p>

<h3>8. Useful metrics</h3>
<p>Four numbers show whether the SAST program is truly working
or just generating noise. <strong>MTTR by severity</strong> measures
average time until a finding is fixed — if a Critical takes
weeks, declared priority does not match real practice. The
<strong>false-positive rate</strong> — the fraction of findings that become
justified suppressions — signals calibration problems above
30%: at that point rules generate more noise than signal and
need tuning. <strong>Findings per thousand new lines</strong> (KLOC)
shows the trend: if it is rising, new code is entering worse
than the old. And <strong>CI analysis time</strong> matters because
SAST taking more than five minutes per PR creates enough friction
for the team to start ignoring or skipping the stage.</p>

<h3>9. SAST limitations</h3>
<p>SAST simply cannot see an entire category of problems by
definition — everything that only exists at RUNTIME is out of reach for
analysis that never executes the code: server misconfiguration
(<code>debug=True</code> from an environment variable, not from
source), auth/authz failures that only show up with real session
data, race conditions that only appear under real concurrency,
complex business-logic failures (a negative price accepted at checkout),
or vulnerabilities in a third-party service called via API whose code
never passes through the scanner. That gap is exactly why SAST must be
combined with DAST, production observability, threat modeling, and periodic
pentests — defense in depth, not one layer trying to cover everything.</p>

<h3>10. Anti-patterns</h3>
<ul>
<li><strong>Buying an expensive tool and letting it generate a thousand-page
report nobody reads</strong>: without direct PR integration (section 4),
the investment produces no real effect.</li>
<li><strong>Blocking every finding at once on legacy</strong>:
nobody can merge anything — use a baseline plus diff-only
(section 4) instead.</li>
<li><strong>Suppressing every false positive without reading each case</strong>:
hides real findings along with the noise (section 5).</li>
<li><strong>Using only default rules</strong>: catches the obvious everyone
already catches, but misses exactly the internal patterns that matter
most for that codebase (section 7).</li>
<li><strong>Never updating rules</strong>: new attack patterns appear
constantly; outdated rules stop catching what is already
known today.</li>
</ul>""",
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Rode <code>semgrep --config p/owasp-top-ten</code> no seu repo. "
                    "Triagem: para cada achado High, decida se é FP ou bug real.</li>"
                    "<li>Adicione Bandit (se Python) ou gosec (se Go) e configure no CI.</li>"
                    "<li>Habilite GitHub CodeQL no repo (gratuito para públicos).</li>"
                    "<li>Configure Semgrep como required check no PR, diff-only.</li>"
                    "<li>Escreva 2 custom rules: uma para anti-pattern do seu projeto "
                    "(ex.: <code>print()</code> em código de produção), outra para padrão "
                    "de PII em logs.</li>"
                    "<li>Documente processo de triagem no SECURITY.md.</li>"
                    "<li>Bonus: complemente com OWASP ZAP em DAST contra staging.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Full hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>Run <code>semgrep --config p/owasp-top-ten</code> on your repo. "
                    "Triage: for each High finding, decide if it is an FP or a real bug.</li>"
                    "<li>Add Bandit (if Python) or gosec (if Go) and configure it in CI.</li>"
                    "<li>Enable GitHub CodeQL on the repo (free for public repos).</li>"
                    "<li>Configure Semgrep as a required PR check, diff-only.</li>"
                    "<li>Write 2 custom rules: one for a project anti-pattern "
                    "(e.g. <code>print()</code> in production code), another for PII "
                    "patterns in logs.</li>"
                    "<li>Document the triage process in SECURITY.md.</li>"
                    "<li>Bonus: complement with OWASP ZAP as DAST against staging.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("OWASP Source Code Analysis Tools", "https://owasp.org/www-community/Source_Code_Analysis_Tools", "docs", "",
                  title_en="OWASP Source Code Analysis Tools", description_en=""),
                m("Semgrep", "https://semgrep.dev/docs/", "tool", "",
                  title_en="Semgrep", description_en=""),
                m("Bandit (Python)", "https://bandit.readthedocs.io/", "tool", "",
                  title_en="Bandit (Python)", description_en=""),
                m("CodeQL (GitHub)", "https://codeql.github.com/", "tool", "",
                  title_en="CodeQL (GitHub)", description_en=""),
                m("SonarQube", "https://www.sonarsource.com/products/sonarqube/", "tool", "",
                  title_en="SonarQube", description_en=""),
                m("OWASP Top 10", "https://owasp.org/www-project-top-ten/", "docs", "Categorias guia para SAST.",
                  title_en="OWASP Top 10", description_en="Guide categories for SAST."),
            ],
            "questions": [
                q("SAST acrônimo significa:",
                  "Static Application Security Testing.",
                  ["System Audit Software Tool, um nome plausível mas incorreto.",
                   "Single Access Static Token, termo usado em outro contexto de autenticação.",
                   "Server Application Security Test, ordem de palavra trocada da sigla real."],
                  "'Static' = sem rodar o app. Diferente de DAST (Dynamic) e IAST (Interactive).",
                  statement_en="The SAST acronym means:",
                  correct_en="Static Application Security Testing.",
                  wrong_en=["System Audit Software Tool — plausible but incorrect.",
                            "Single Access Static Token — a term from another auth context.",
                            "Server Application Security Test — words in the wrong order for the real acronym."],
                  explanation_en="'Static' = without running the app. Different from DAST (Dynamic) and IAST (Interactive)."),
                q("Diferença entre SAST e DAST:",
                  "SAST analisa o código sem rodar; DAST analisa app rodando.",
                  ["Os dois são exatamente a mesma coisa, só com nome diferente.",
                   "DAST analisa só o código-fonte, sem tocar na aplicação rodando.",
                   "SAST exige a aplicação já rodando em produção para funcionar."],
                  "Use ambos: SAST no PR, DAST contra staging. Cada um pega coisas que o outro não vê.",
                  statement_en="Difference between SAST and DAST:",
                  correct_en="SAST analyzes code without running it; DAST analyzes a running app.",
                  wrong_en=["Both are exactly the same thing under different names.",
                            "DAST analyzes only source code, without touching the running app.",
                            "SAST requires the app already running in production to work."],
                  explanation_en="Use both: SAST on the PR, DAST against staging. Each catches what the other misses."),
                q("Bandit detecta:",
                  "Padrões inseguros em Python.",
                  ["Só arquivo YAML, sem suporte a código Python de verdade.",
                   "Só código Java, sem suporte à linguagem Python.",
                   "Falha de resolução de DNS, algo fora do escopo do Bandit."],
                  "Eval, hardcoded password, uso de tempfile inseguro etc. Roda fácil em pre-commit.",
                  statement_en="Bandit detects:",
                  correct_en="Insecure patterns in Python.",
                  wrong_en=["Only YAML files, with no support for real Python code.",
                            "Only Java code, with no support for Python.",
                            "DNS resolution failures — outside Bandit's scope."],
                  explanation_en="Eval, hardcoded passwords, insecure tempfile use, etc. Easy to run in pre-commit."),
                q("Falso positivo em SAST:",
                  "Achado real do padrão, mas que não é vulnerabilidade no contexto.",
                  ["Um bug dentro da própria ferramenta que gerou o achado.",
                   "Uma garantia de que o achado será corrigido rapidamente sem falha.",
                   "Um simples log informativo, sem qualquer relação com vulnerabilidade."],
                  "Ex.: SQL string concat onde input é constante interna. Suprima e documente.",
                  statement_en="A false positive in SAST:",
                  correct_en="A real pattern match that is not a vulnerability in context.",
                  wrong_en=["A bug inside the tool that produced the finding.",
                            "A guarantee the finding will be fixed quickly without failure.",
                            "A simple info log, unrelated to any vulnerability."],
                  explanation_en="E.g. SQL string concat where input is an internal constant. Suppress and document."),
                q("Para trecho legado já mitigado:",
                  "Documente a exceção e suprima com comentário/regra.",
                  ["Reescreva a aplicação inteira só por causa desse achado pontual.",
                   "Ignore completamente o resultado do SAST daqui em diante.",
                   "Use só DAST, abandonando o SAST configurado até então."],
                  "Comentário deve explicar a mitigação. Auditoria periódica re-avalia.",
                  statement_en="For legacy code that is already mitigated:",
                  correct_en="Document the exception and suppress with a comment/rule.",
                  wrong_en=["Rewrite the entire application just because of that one finding.",
                            "Ignore all SAST results from now on.",
                            "Use only DAST and abandon the SAST already configured."],
                  explanation_en="The comment should explain the mitigation. Periodic audits re-evaluate."),
                q("CodeQL roda:",
                  "Queries em representações de código (DBs).",
                  ["Só expressão regular, sem entender a estrutura real do código.",
                   "Só dentro de um servidor SQL, sem relação com análise de código.",
                   "Só em ambiente de produção, fora do próprio pipeline de CI."],
                  "Constrói banco de fatos sobre o código; queries SQL-like buscam padrões. Free para repos públicos.",
                  statement_en="CodeQL runs:",
                  correct_en="Queries over code representations (databases).",
                  wrong_en=["Only regular expressions, without understanding real code structure.",
                            "Only inside a SQL server, unrelated to code analysis.",
                            "Only in production, outside the CI pipeline itself."],
                  explanation_en="Builds a fact database about the code; SQL-like queries find patterns. Free for public repos."),
                q("SAST no PR é eficaz porque:",
                  "Dá feedback antes do merge, com escopo pequeno.",
                  ["Só no final do pipeline, depois de tudo já ter sido feito.",
                   "Só quando já está em produção, tarde demais para corrigir fácil.",
                   "Não muda o resultado final do processo de forma alguma."],
                  "Diff-only reduz ruído. Bloquear merge em High garante que não acumula dívida.",
                  statement_en="SAST on the PR is effective because:",
                  correct_en="It gives feedback before merge, with a small scope.",
                  wrong_en=["Only at the end of the pipeline, after everything is already done.",
                            "Only once it is already in production — too late to fix easily.",
                            "It does not change the final outcome of the process at all."],
                  explanation_en="Diff-only reduces noise and focuses on what the author just changed."),
                q("Limitação de SAST:",
                  "Não enxerga problemas runtime/configuração.",
                  ["Não detecta SQL injection do jeito que o DAST detectaria.",
                   "Não roda em projeto escrito na linguagem Java.",
                   "Só analisa arquivo YAML, ignorando qualquer outra linguagem."],
                  "Misconfig de servidor, falhas de auth em runtime, DoS, fora do escopo.",
                  statement_en="A limitation of SAST:",
                  correct_en="It does not see runtime issues (auth, config, infra).",
                  wrong_en=["It never finds any vulnerability in any language.",
                            "It only works when the application is already in production.",
                            "It fully replaces the need for any other security testing."],
                  explanation_en="Complement with DAST, SCA, secrets scanning, and reviews."),
                q("Métrica útil para SAST:",
                  "MTTR (mean time to remediate) por severidade.",
                  ["A quantidade total de linha de código presente no projeto.",
                   "O tamanho em linha de cada PR aberto no repositório.",
                   "O número de desenvolvedor ativo contribuindo com o projeto."],
                  "Mostra se time está realmente endereçando ou só ignorando.",
                  statement_en="A useful SAST metric:",
                  correct_en="Time-to-triage and true-positive rate.",
                  wrong_en=["Number of lines of code alone, with no security context.",
                            "Monthly cost of the CI runner used in the pipeline.",
                            "Disk size of the repository clone on the developer laptop."],
                  explanation_en="If findings pile up unread, the tool becomes noise. Track closure."),
                q("Custom rules em Semgrep:",
                  "Permitem capturar padrões específicos do seu domínio.",
                  ["Só padrão relacionado a SQL, sem cobrir outro tipo de código.",
                   "Só arquivo YAML, sem capturar padrão de código de verdade.",
                   "Desabilitam completamente a ferramenta, impedindo qualquer execução."],
                  "Sintaxe simples (YAML + pattern). Útil para exigir uso de função interna padrão.",
                  statement_en="Custom rules in Semgrep:",
                  correct_en="Encode project-specific anti-patterns as searchable rules.",
                  wrong_en=["Replace the need to write any application code.",
                            "Only work for Java, with no other language support.",
                            "Disable every built-in rule automatically."],
                  explanation_en="Great for house rules (no print in prod, no PII in logs)."),
            ],
        },
        # =====================================================================
        # 3.8 SCA
        # =====================================================================
        {
            "title": "SCA",
            "title_en": 'SCA',
            "summary": "Verificar se as bibliotecas que seu código usa têm vírus ou falhas.",
            "summary_en": 'Check whether libraries your code uses have viruses or flaws.',
            "lesson": {
                "intro": (
                    "Em apps modernos, ~80% do código não é seu, vem de dependências. "
                    "React, Django, requests, lodash, openssl, glibc. Você é responsável "
                    "por todas. SCA (Software Composition Analysis) mapeia o que você "
                    "usa e cruza com bases de CVEs públicas. Caso real: Log4Shell "
                    "(CVE-2021-44228), uma string em log derrubava 30%+ da internet. "
                    "Empresas com SCA detectaram em horas e mitigaram. Sem SCA, "
                    "ficaram vulneráveis por dias/semanas até alguém perceber. Esta aula "
                    "cobre SBOM, CVE/CVSS, ferramentas e o que fazer quando aparece a "
                    "próxima Log4Shell."
                ),
                "intro_en": (
                    "In modern apps, ~80% of the code is not yours — it comes from dependencies. "
                    "React, Django, requests, lodash, openssl, glibc. You are responsible "
                    "for all of it. SCA (Software Composition Analysis) maps what you "
                    "use and cross-checks public CVE databases. Real case: Log4Shell "
                    "(CVE-2021-44228) — one string in a log took down 30%+ of the internet. "
                    "Companies with SCA detected it in hours and mitigated. Without SCA, "
                    "they stayed vulnerable for days/weeks until someone noticed. This lesson "
                    "covers SBOM, CVE/CVSS, tools, and what to do when the next "
                    "Log4Shell appears."
                ),
                "body": (
                """<h3>1. SBOM (Software Bill of Materials)</h3>
<p>Um SBOM é a lista de TODAS as dependências — diretas e transitivas —
com versão e licença de cada uma. É o ingrediente básico sem o qual
nenhuma análise de segurança de dependência funciona, porque não dá para
verificar CVE em algo que você nem sabe que está usando. Em ambientes
regulados (governo dos EUA via Executive Order 14028, setor automotivo,
dispositivo médico), SBOM já é obrigação contratual, não boa prática
opcional. Dois formatos dominam: <strong>CycloneDX</strong>, mantido
pela OWASP com foco mais voltado a segurança, e <strong>SPDX</strong>,
mantido pela Linux Foundation com foco mais voltado a compliance e
licenciamento. Ferramentas como <code>syft</code> (Anchore),
<code>cdxgen</code> (OWASP) e <code>trivy</code> geram esses formatos a
partir de código ou imagem:</p>
<div class="mermaid">
flowchart LR
    Manifest["package-lock / go.sum"] --> SBOM["Gera SBOM"]
    SBOM --> Inv["Inventário de componentes"]
    Inv --> Share["Compartilha com auditoria / clientes"]
</div>

<pre><code>$ syft packages docker:nginx:latest -o cyclonedx-json &gt; sbom.json
$ syft dir:. -o spdx-json &gt; sbom.spdx.json</code></pre>
<p>Atrelar o SBOM diretamente ao artefato — referenciado no próprio
registry OCI — cria uma trilha auditável: fica registrado exatamente o
que foi entregue em cada versão, não uma aproximação reconstruída
depois.</p>

<h3>2. CVE, CVSS, EPSS, KEV</h3>
<p>Quatro siglas organizam como o ecossistema de segurança fala sobre
vulnerabilidade. <strong>CVE</strong> (Common Vulnerabilities and
Exposures) é só um identificador único, como <code>CVE-2024-1234</code>
— um nome, não uma medida de gravidade. <strong>CVSS</strong> é o score
de 0 a 10 que mede severidade técnica, calculado a partir de um vetor
como <code>AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H</code>. Mas CVSS sozinho
mede só o dano POTENCIAL, não o risco real de exploração — daí o
<strong>EPSS</strong> (Exploit Prediction Scoring System), que estima a
probabilidade real de aquela CVE específica ser explorada nos próximos
30 dias, com base em dados observados de ataque. E o <strong>KEV</strong>
(Known Exploited Vulnerabilities) é o catálogo da CISA de CVEs que JÁ
foram exploradas em ataque real — entrar no KEV significa ação
imediata, não uma prioridade a mais na fila. A combinação madura de
priorização é CVSS ≥ 7 combinado com presença no KEV ou EPSS alto
classificado como crítico; usar CVSS isolado leva à fadiga de alerta,
com centenas de "7s" tecnicamente altos mas praticamente irrelevantes
competindo pela mesma atenção.</p>

<h3>3. Ferramentas</h3>
<table>
<tr><th>Ferramenta</th><th>Pontos fortes</th></tr>
<tr><td>Trivy</td><td>CLI grátis; escaneia FS, imagens, IaC, K8s. SBOM + CVEs. Bom em CI.</td></tr>
<tr><td>Grype</td><td>Pareado com Syft (mesmo dono). Foco em CVEs.</td></tr>
<tr><td>Dependabot (GitHub)</td><td>Nativo. PR de update automático. Limitado em config avançada.</td></tr>
<tr><td>Renovate</td><td>Mais configurável; agrupa updates, segue regras complexas.</td></tr>
<tr><td>Snyk</td><td>Comercial freemium; bom UX, sugere fix.</td></tr>
<tr><td>OSV-Scanner</td><td>Google; usa OSV.dev; rápido e gratuito.</td></tr>
<tr><td>npm audit / pip-audit</td><td>Nativos; básicos.</td></tr>
<tr><td>OWASP Dependency-Check</td><td>Java; bom para empresas legacy.</td></tr>
</table>

<h3>4. Trivy: ferramenta vital</h3>
<div class="mermaid">
flowchart TD
    Img["Imagem / FS / repo"] --> Trivy["Trivy scan"]
    Trivy --> CVE["CVEs + severidade"]
    CVE --> Policy{"Dentro do SLA?"}
    Policy -- Não --> Ticket["Abre remediação"]
    Policy -- Sim --> Pass["Aceito com prazo"]
</div>

<pre><code>$ trivy fs .                     # escaneia diretório
$ trivy image nginx:1.25.3        # escaneia imagem
$ trivy config terraform/         # IaC
$ trivy k8s --severity CRITICAL --all-namespaces

# Falhar build em criticais
$ trivy image --severity CRITICAL --exit-code 1 myapp:dev

# Gerar SBOM
$ trivy image --format cyclonedx --output sbom.json myapp:dev

# Ignorar específicos (com motivo!)
# .trivyignore:
# CVE-2024-12345  # não-exploitable em nosso uso
</code></pre>

<h3>5. Política de remediação (SLA)</h3>
<p>Sem um prazo explícito, achado de SCA vira mais um item numa lista
que ninguém prioriza de verdade. Documentar SLA por severidade no
SECURITY.md transforma "corrija quando der" em compromisso mensurável:</p>
<pre><code>| Severidade           | SLA Prod | SLA Staging |
|----------------------|----------|-------------|
| Critical em KEV      | 24-72h   | 7d          |
| Critical             | 7d       | 14d         |
| High + EPSS &gt;= 0.5    | 14d      | 30d         |
| High                 | 30d      | 60d         |
| Medium               | 90d      | 180d        |
| Low                  | 180d     | best-effort |</code></pre>

<h3>6. Lockfiles: a base de tudo</h3>
<p>Um lockfile fixa a versão exata (e o hash) de cada dependência
resolvida — Python usa <code>poetry.lock</code>, <code>pdm.lock</code>
ou <code>requirements.txt</code> com pinning e hash; JavaScript usa
<code>package-lock.json</code>, <code>yarn.lock</code> ou
<code>pnpm-lock.yaml</code>; Go usa <code>go.sum</code>; Rust usa
<code>Cargo.lock</code>; Ruby usa <code>Gemfile.lock</code>. Commitar
esse arquivo SEMPRE é inegociável, por três razões concretas: sem ele o
build deixa de ser reprodutível, e dev/prod podem acabar com versões
diferentes da mesma dependência declarada; o SCA fica confuso, relatando
CVE numa versão que talvez nem esteja de fato instalada; e um atacante
ganha uma janela para trocar silenciosamente uma dependência por uma
versão maliciosa — o ataque conhecido como dependency confusion. Usar
<code>--require-hashes</code> no pip valida a integridade no momento do
install: qualquer hash que não bata falha a instalação imediatamente, em
vez de instalar silenciosamente um pacote adulterado.</p>

<h3>7. Cadeia de suprimentos: além de CVE</h3>
<p>SCA tradicional resolve "esta biblioteca tem CVE conhecida" — mas
ataque de cadeia de suprimentos é uma categoria mais ampla, que muitas
vezes nem envolve CVE nenhuma. <strong>Typosquatting</strong> planta um
pacote malicioso com nome parecido ao real (<code>requests</code> vs
<code>requets</code>), na aposta de que alguém digite errado; a defesa é
revisar toda dependência nova antes de adicionar. <strong>Conta de
mantenedor comprometida</strong> permite publicar uma versão maliciosa
sob um nome já confiável e amplamente usado — os casos
<em>event-stream</em>, <em>colors.js</em> e <em>node-ipc</em> ficaram
famosos exatamente por isso; a defesa é pin por hash e um mirror interno
que não puxa versão nova automaticamente sem revisão.
<strong>Dependency confusion</strong> explora quando um pacote interno
tem o mesmo nome de um pacote público — se a configuração de resolução
não distinguir os dois corretamente, o pacote PÚBLICO acaba sendo
puxado no lugar do interno, potencialmente controlado por um atacante
que só precisou publicar algo com aquele nome; a defesa é escopo
explícito no registry interno. Comprometer a <strong>infraestrutura de
build</strong> em si para injetar código diretamente no pipeline — o
caso SolarWinds é o exemplo mais conhecido — pede defesa em outro nível,
via o framework SLSA (seção 11). E existe até o caso do
<strong>"protestware"</strong>, onde o próprio mantenedor sabota
deliberadamente sua biblioteca em protesto político; pin de versão
protege contra isso da mesma forma que protege contra qualquer update
inesperado.</p>

<h3>8. Dependabot configurado direito</h3>
<pre><code># .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule: { interval: weekly, day: monday }
    open-pull-requests-limit: 10
    groups:
      django:
        patterns: ['django*']
      dev-deps:
        dependency-type: development
    ignore:
      - dependency-name: 'numpy'
        versions: ['&gt;=2.0.0']  # major bump quebra; pin manual
  - package-ecosystem: docker
    directory: /
    schedule: { interval: weekly }
  - package-ecosystem: github-actions
    directory: /
    schedule: { interval: monthly }</code></pre>
<p>Sem o campo <code>groups</code>, o Dependabot abre um PR separado
para cada dependência que mudou — facilmente 50 PRs numa semana num
projeto com muitas libs. Com <code>groups</code>, PRs relacionados se
consolidam num só, reduzindo para 5 PRs que ainda cobrem exatamente as
mesmas atualizações.</p>

<h3>9. CVEs em transitivas: o pesadelo do override</h3>
<p>O cenário mais comum na prática: você depende de
<code>django</code>; <code>django</code> depende de
<code>asgiref</code>; e é <code>asgiref</code> que carrega a CVE — uma
dependência que você nunca declarou diretamente. A resposta segue uma
ordem de preferência: primeiro avalie se o caminho é realmente
explorável no seu uso específico; depois tente atualizar o PAI
(<code>django</code>), que normalmente já resolveu a transitiva numa
versão mais nova — a solução mais limpa por não introduzir override
manual; se isso não for possível ainda, force a versão da transitiva
diretamente (<code>overrides</code> no npm, <code>--constraint</code> no
pip, dependency management no Maven); só então considere aceitar o
risco com justificativa documentada; e substituir a biblioteca pai
inteira fica como último recurso, quando nada mais resolve.</p>

<h3>10. Resposta a CVE crítica em produção</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Confirme explotabilidade (KEV/EPSS)</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Atualize lockfile / imagem base</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Reconstrua e redeploy por digest</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Verifique scan limpo no registry</p></div>
  </div>
  <figcaption>Resposta a CVE crítica em produção.</figcaption>
</figure>

<p>Um incidente como o Log4Shell (CVE-2021-44228) — uma string
simplesmente logada derrubando mais de 30% da internet — segue um
roteiro que separa quem reage em horas de quem reage em semanas.
Primeiro, <strong>inventário</strong>: o SCA cruza o SBOM já existente
com a CVE anunciada, respondendo imediatamente "quem usa isso, e em
quais ambientes" — sem SBOM prévio, essa pergunta sozinha pode levar
dias. Depois, <strong>avaliação</strong>: o caminho realmente explorável
existe na sua aplicação específica? (No caso do Log4Shell, bastava
logar input não-sanitizado — um cenário trivialmente comum, o que
explicou o alcance do estrago.) Em seguida, <strong>mitigação</strong>
imediata via regra de WAF ou desabilitar a feature afetada, enquanto o
patch definitivo não sai. Depois o <strong>patch</strong> propriamente
dito: bump de versão, teste, deploy. Paralelamente, <strong>detecção</strong>
via log ou SIEM procurando tentativa de exploração já ocorrida antes do
patch. Depois, <strong>comunicação</strong> transparente com cliente,
regulador e status page, se aplicável. E por fim um
<strong>postmortem</strong> real: como a vulnerabilidade foi descoberta,
qual SLA foi de fato cumprido, e o que precisa melhorar para a próxima
— porque vai haver uma próxima.</p>

<h3>11. SLSA: framework de cadeia de suprimentos</h3>
<p>SLSA (Supply chain Levels for Software Artifacts) define quatro
níveis crescentes de garantia sobre a proveniência de um artefato — não
é binário "seguro ou não", é uma escala. O nível 1 exige apenas build
automatizado e documentado, algo que muitos times já têm sem saber
nomear. O nível 2 exige que o código-fonte seja versionado e o build
rode num serviço hospedado, não numa máquina de desenvolvedor
individual. O nível 3 exige que o build seja não-falsificável, com
isolamento real entre execuções. E o nível 4, o mais exigente, exige
build reproduzível byte a byte e revisão de duas pessoas antes de
qualquer release. Combinar isso com Cosign e Rekor (o ecossistema
Sigstore) permite gerar atestados verificáveis criptograficamente sobre
qual nível cada artefato de fato atingiu.</p>"""
                ),
                "body_en": """<h3>1. SBOM (Software Bill of Materials)</h3>
<p>An SBOM is the list of ALL dependencies — direct and transitive —
with version and license for each. It is the basic ingredient without which
no dependency security analysis works, because you cannot
check CVEs in something you do not even know you use. In regulated
environments (US government via Executive Order 14028, automotive,
medical devices), SBOM is already a contractual obligation, not an optional
best practice. Two formats dominate: <strong>CycloneDX</strong>, maintained
by OWASP with a security focus, and <strong>SPDX</strong>,
maintained by the Linux Foundation with more focus on compliance and
licensing. Tools like <code>syft</code> (Anchore),
<code>cdxgen</code> (OWASP), and <code>trivy</code> generate these formats from
code or images:</p>
<div class="mermaid">
flowchart LR
    Manifest["package-lock / go.sum"] --> SBOM["Generate SBOM"]
    SBOM --> Inv["Component inventory"]
    Inv --> Share["Share with audit / customers"]
</div>

<pre><code>$ syft packages docker:nginx:latest -o cyclonedx-json &gt; sbom.json
$ syft dir:. -o spdx-json &gt; sbom.spdx.json</code></pre>
<p>Attaching the SBOM directly to the artifact — referenced in the
OCI registry itself — creates an auditable trail: exactly what was
shipped in each version is recorded, not an approximation reconstructed
later.</p>

<h3>2. CVE, CVSS, EPSS, KEV</h3>
<p>Four acronyms organize how the security ecosystem talks about
vulnerabilities. <strong>CVE</strong> (Common Vulnerabilities and
Exposures) is only a unique identifier, like <code>CVE-2024-1234</code>
— a name, not a severity measure. <strong>CVSS</strong> is the 0–10 score
measuring technical severity, computed from a vector
like <code>AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H</code>. But CVSS alone
measures only POTENTIAL damage, not real exploitation risk — hence
<strong>EPSS</strong> (Exploit Prediction Scoring System), which estimates the
real probability that a specific CVE will be exploited in the next
30 days based on observed attack data. And <strong>KEV</strong>
(Known Exploited Vulnerabilities) is CISA's catalog of CVEs that HAVE
already been exploited in real attacks — landing on KEV means immediate
action, not just another priority in the queue. Mature prioritization
combines CVSS ≥ 7 with KEV presence or high EPSS classified as critical;
using CVSS alone leads to alert fatigue, with hundreds of technically
high "7s" that are practically irrelevant competing for the same
attention.</p>

<h3>3. Tools</h3>
<table>
<tr><th>Tool</th><th>Strengths</th></tr>
<tr><td>Trivy</td><td>Free CLI; scans FS, images, IaC, K8s. SBOM + CVEs. Good in CI.</td></tr>
<tr><td>Grype</td><td>Paired with Syft (same owner). CVE-focused.</td></tr>
<tr><td>Dependabot (GitHub)</td><td>Native. Automatic update PRs. Limited advanced config.</td></tr>
<tr><td>Renovate</td><td>More configurable; groups updates, follows complex rules.</td></tr>
<tr><td>Snyk</td><td>Commercial freemium; good UX, suggests fixes.</td></tr>
<tr><td>OSV-Scanner</td><td>Google; uses OSV.dev; fast and free.</td></tr>
<tr><td>npm audit / pip-audit</td><td>Native; basic.</td></tr>
<tr><td>OWASP Dependency-Check</td><td>Java; good for legacy enterprises.</td></tr>
</table>

<h3>4. Trivy: a vital tool</h3>
<div class="mermaid">
flowchart TD
    Img["Image / FS / repo"] --> Trivy["Trivy scan"]
    Trivy --> CVE["CVEs + severity"]
    CVE --> Policy{"Within SLA?"}
    Policy -- No --> Ticket["Open remediation"]
    Policy -- Yes --> Pass["Accepted with deadline"]
</div>

<pre><code>$ trivy fs .                     # escaneia diretório
$ trivy image nginx:1.25.3        # escaneia imagem
$ trivy config terraform/         # IaC
$ trivy k8s --severity CRITICAL --all-namespaces

# Falhar build em criticais
$ trivy image --severity CRITICAL --exit-code 1 myapp:dev

# Gerar SBOM
$ trivy image --format cyclonedx --output sbom.json myapp:dev

# Ignorar específicos (com motivo!)
# .trivyignore:
# CVE-2024-12345  # não-exploitable em nosso uso
</code></pre>

<h3>5. Remediation policy (SLA)</h3>
<p>Without an explicit deadline, SCA findings become another item on a list
nobody truly prioritizes. Documenting severity SLAs in
SECURITY.md turns "fix when you can" into a measurable commitment:</p>
<pre><code>| Severidade           | SLA Prod | SLA Staging |
|----------------------|----------|-------------|
| Critical em KEV      | 24-72h   | 7d          |
| Critical             | 7d       | 14d         |
| High + EPSS &gt;= 0.5    | 14d      | 30d         |
| High                 | 30d      | 60d         |
| Medium               | 90d      | 180d        |
| Low                  | 180d     | best-effort |</code></pre>

<h3>6. Lockfiles: the foundation of everything</h3>
<p>A lockfile pins the exact version (and hash) of every resolved
dependency — Python uses <code>poetry.lock</code>, <code>pdm.lock</code>,
or <code>requirements.txt</code> with pinning and hashes; JavaScript uses
<code>package-lock.json</code>, <code>yarn.lock</code>, or
<code>pnpm-lock.yaml</code>; Go uses <code>go.sum</code>; Rust uses
<code>Cargo.lock</code>; Ruby uses <code>Gemfile.lock</code>. Committing
that file ALWAYS is non-negotiable for three concrete reasons: without it,
builds stop being reproducible, and dev/prod can end up with different
versions of the same declared dependency; SCA gets confused, reporting
CVEs on versions that may not even be installed; and an attacker
gains a window to silently swap a dependency for a
malicious version — the known dependency-confusion attack. Using
<code>--require-hashes</code> in pip validates integrity at install time:
any mismatched hash fails installation immediately instead of silently
installing a tampered package.</p>

<h3>7. Supply chain: beyond CVEs</h3>
<p>Traditional SCA answers "does this library have a known CVE" — but
supply-chain attacks are a broader category that often involve no CVE
at all. <strong>Typosquatting</strong> plants a malicious package with a name
similar to the real one (<code>requests</code> vs <code>requets</code>), betting
someone will mistype; the defense is reviewing every new dependency before
adding it. A <strong>compromised maintainer account</strong> lets someone publish
a malicious version under an already trusted, widely used name — the
<em>event-stream</em>, <em>colors.js</em>, and <em>node-ipc</em> cases became
famous for exactly that; the defense is hash pinning and an internal
mirror that does not pull new versions automatically without review.
<strong>Dependency confusion</strong> exploits when an internal package
shares a name with a public one — if resolution config does not distinguish
them correctly, the PUBLIC package gets pulled instead of the internal one,
potentially controlled by an attacker who only needed to publish something
with that name; the defense is explicit scoping on the internal registry.
Compromising the <strong>build infrastructure</strong> itself to inject code
directly into the pipeline — SolarWinds is the best-known example —
requires defense at another level via the SLSA framework (section 11).
And there is even <strong>"protestware"</strong>, where the maintainer
deliberately sabotages their own library in political protest; version
pinning protects against that the same way it protects against any unexpected
update.</p>

<h3>8. Dependabot configured properly</h3>
<pre><code># .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule: { interval: weekly, day: monday }
    open-pull-requests-limit: 10
    groups:
      django:
        patterns: ['django*']
      dev-deps:
        dependency-type: development
    ignore:
      - dependency-name: 'numpy'
        versions: ['&gt;=2.0.0']  # major bump quebra; pin manual
  - package-ecosystem: docker
    directory: /
    schedule: { interval: weekly }
  - package-ecosystem: github-actions
    directory: /
    schedule: { interval: monthly }</code></pre>
<p>Without the <code>groups</code> field, Dependabot opens a separate PR
for every dependency that changed — easily 50 PRs in a week on a
project with many libs. With <code>groups</code>, related PRs
consolidate into one, reducing to ~5 PRs that still cover exactly the
same updates.</p>

<h3>9. CVEs in transitives: the override nightmare</h3>
<p>The most common real scenario: you depend on
<code>django</code>; <code>django</code> depends on
<code>asgiref</code>; and <code>asgiref</code> carries the CVE — a
dependency you never declared directly. The response follows a
preferred order: first evaluate whether the path is truly
exploitable in your specific usage; then try updating the PARENT
(<code>django</code>), which usually already resolved the transitive in a
newer version — the cleanest fix because it introduces no manual override;
if that is not yet possible, force the transitive version
directly (<code>overrides</code> in npm, <code>--constraint</code> in
pip, dependencyManagement in Maven); only then consider accepting the
risk with documented justification; and replacing the entire parent
library is the last resort when nothing else works.</p>

<h3>10. Responding to a critical CVE in production</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Confirm exploitability (KEV/EPSS)</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Update lockfile / base image</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Rebuild and redeploy by digest</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Verify clean scan in the registry</p></div>
  </div>
  <figcaption>Responding to a critical CVE in production.</figcaption>
</figure>

<p>An incident like Log4Shell (CVE-2021-44228) — a string
simply logged taking down more than 30% of the internet — follows a
playbook that separates who reacts in hours from who reacts in weeks.
First, <strong>inventory</strong>: SCA cross-checks the existing SBOM
with the announced CVE, immediately answering "who uses this, and in
which environments" — without a prior SBOM, that question alone can take
days. Next, <strong>assessment</strong>: does an exploitable path really
exist in your specific application? (In Log4Shell, logging unsanitized
input was enough — a trivially common scenario, which explained the blast
radius.) Then immediate <strong>mitigation</strong>
via WAF rules or disabling the affected feature while the
definitive patch is not out. Then the <strong>patch</strong> itself:
version bump, test, deploy. In parallel, <strong>detection</strong>
via logs or SIEM looking for exploitation attempts that already happened before
the patch. Then transparent <strong>communication</strong> with customers,
regulators, and the status page if applicable. And finally a real
<strong>postmortem</strong>: how the vulnerability was discovered,
which SLA was actually met, and what must improve for the next one —
because there will be a next one.</p>

<h3>11. SLSA: supply-chain framework</h3>
<p>SLSA (Supply chain Levels for Software Artifacts) defines four
increasing levels of assurance about an artifact's provenance — it is
not binary "secure or not", it is a scale. Level 1 only requires
automated, documented builds — something many teams already have without
naming it. Level 2 requires versioned source and builds on a hosted
service, not an individual developer machine. Level 3 requires
non-falsifiable builds with real isolation between runs. And level 4,
the most demanding, requires byte-for-byte reproducible builds and two-person
review before any release. Combining that with Cosign and Rekor (the
Sigstore ecosystem) lets you generate cryptographically verifiable attestations
about which level each artifact actually reached.</p>""",
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Configure Dependabot/Renovate no repo com groups.</li>"
                    "<li>Rode <code>trivy fs .</code> e <code>trivy image</code>; gere "
                    "SBOM com <code>syft</code>.</li>"
                    "<li>Falhe CI em CVEs criticais (<code>--exit-code 1</code>).</li>"
                    "<li>Documente SLA de remediação no SECURITY.md.</li>"
                    "<li>Configure pin por hash em <code>requirements.txt</code> "
                    "(pip-tools).</li>"
                    "<li>Simule: encontre CVE conhecido em uma versão antiga, faça PR de "
                    "update, verifique CI passa.</li>"
                    "<li>Bonus: gere atestado SLSA L3 com Sigstore.</li>"
                    "<li>Bonus 2: configure pull-through cache em registry interno para "
                    "imagens base.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Full hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>Configure Dependabot/Renovate on the repo with groups.</li>"
                    "<li>Run <code>trivy fs .</code> and <code>trivy image</code>; generate "
                    "an SBOM with <code>syft</code>.</li>"
                    "<li>Fail CI on critical CVEs (<code>--exit-code 1</code>).</li>"
                    "<li>Document remediation SLAs in SECURITY.md.</li>"
                    "<li>Configure hash pinning in <code>requirements.txt</code> "
                    "(pip-tools).</li>"
                    "<li>Simulate: find a known CVE in an old version, open an update PR, "
                    "verify CI passes.</li>"
                    "<li>Bonus: generate an SLSA L3 attestation with Sigstore.</li>"
                    "<li>Bonus 2: configure a pull-through cache in an internal registry for "
                    "base images.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("OWASP Dependency-Check", "https://owasp.org/www-project-dependency-check/", "tool", "",
                  title_en="OWASP Dependency-Check", description_en=""),
                m("Trivy", "https://aquasecurity.github.io/trivy/", "tool", "",
                  title_en="Trivy", description_en=""),
                m("GitHub Dependabot", "https://docs.github.com/code-security/dependabot", "docs", "",
                  title_en="GitHub Dependabot", description_en=""),
                m("Renovate", "https://docs.renovatebot.com/", "tool", "",
                  title_en="Renovate", description_en=""),
                m("CVE database", "https://www.cve.org/", "docs", "",
                  title_en="CVE database", description_en=""),
                m("OSV.dev", "https://osv.dev/", "docs", "Banco unificado de CVEs em open source.",
                  title_en="OSV.dev", description_en="Unified database of open-source CVEs."),
            ],
            "questions": [
                q("SCA significa:",
                  "Software Composition Analysis.",
                  ["System Check Authority, uma sigla parecida mas inventada.",
                   "Secure Code Algo, termo que não corresponde à sigla real.",
                   "Static Code Audit, quase certo mas não é o nome oficial."],
                  "Foca em mapear e checar componentes (libs, frameworks).",
                  statement_en="SCA means:",
                  correct_en="Software Composition Analysis.",
                  wrong_en=["System Configuration Audit — a plausible but wrong expansion.",
                            "Secure Code Automation — not what the acronym stands for.",
                            "Source Control Access — a different concept entirely."],
                  explanation_en="Maps dependencies and checks them against public CVE databases."),
                q("CVE é:",
                  "Identificador único para uma vulnerabilidade conhecida.",
                  ["Um tipo de versão de release usado em algumas empresas.",
                   "Um comando de shell usado para verificar dependência instalada.",
                   "Parte do protocolo TLS responsável pelo handshake inicial."],
                  "Mantido por MITRE. Cada CVE tem descrição, refs, scoring CVSS.",
                  statement_en="A CVE is:",
                  correct_en="A public identifier for a known vulnerability.",
                  wrong_en=["A private certificate used only inside the company.",
                            "A type of immutable container image tag.",
                            "A CI runner that executes security jobs."],
                  explanation_en="Common Vulnerabilities and Exposures. CVSS scores severity."),
                q("Dependabot abre:",
                  "PRs automáticos de atualização de dependências.",
                  ["Ticket de suporte aberto automaticamente para o time de infra.",
                   "Build canário rodando contra uma fração pequena de usuário.",
                   "Alerta de DNS disparado quando um domínio expira sem aviso."],
                  "Configure agrupamento (group updates) para evitar 50 PRs por semana.",
                  statement_en="Dependabot opens:",
                  correct_en="PRs that update vulnerable or outdated dependencies.",
                  wrong_en=["A shell on the production server for the user.",
                            "A DNS alert when a domain expires without notice.",
                            "A merge commit that skips all required checks."],
                  explanation_en="Configure grouping (group updates) to avoid 50 PRs per week."),
                q("Trivy escaneia:",
                  "Imagens, IaC, e dependências em busca de CVEs e mis-configs.",
                  ["Só imagem de container, sem cobrir arquivo de IaC nem dependência alguma.",
                   "Só código escrito em Python, sem suporte a outra linguagem ou formato.",
                   "Só arquivo YAML de configuração, sem escanear imagem nem dependência real."],
                  "Multi-tool ótimo para CI: roda em segundos, fácil de integrar.",
                  statement_en="Trivy scans:",
                  correct_en="Images, IaC, and dependencies for CVEs and misconfigs.",
                  wrong_en=["Only container images — no IaC files or dependencies.",
                            "Only Python code — no other language or format.",
                            "Only YAML config files — no images or real dependencies."],
                  explanation_en="A strong multi-tool for CI: runs in seconds, easy to integrate."),
                q("CVSS mede:",
                  "Severidade de vulnerabilidades (0-10).",
                  ["A latência medida ao baixar um pacote da internet.",
                   "O tamanho em byte do binário final compilado.",
                   "O custo mensal cobrado pela infraestrutura de nuvem usada."],
                  "Vetor base inclui AV (vetor de ataque), C/I/A impactos. CVSS 9.0+ é Critical.",
                  statement_en="CVSS measures:",
                  correct_en="Vulnerability severity (0–10).",
                  wrong_en=["Latency when downloading a package from the internet.",
                            "Byte size of the final compiled binary.",
                            "Monthly cost of the cloud infrastructure in use."],
                  explanation_en="Base vector includes AV (attack vector) and C/I/A impacts. CVSS 9.0+ is Critical."),
                q("Lockfile (poetry.lock, package-lock):",
                  "Fixa versões exatas para reprodução.",
                  ["Apaga a dependência inteira do projeto sem aviso prévio.",
                   "Substitui a política de IAM aplicada à conta de deploy.",
                   "Ignora a dependência declarada, sem resolver versão alguma."],
                  "Sem lockfile, atualizações silenciosas podem trazer bug, ou backdoor.",
                  statement_en="A lockfile (poetry.lock, package-lock):",
                  correct_en="Pins exact versions for reproducibility.",
                  wrong_en=["Deletes the entire dependency from the project without warning.",
                            "Replaces the IAM policy applied to the deploy account.",
                            "Ignores declared dependencies without resolving any version."],
                  explanation_en="Without a lockfile, silent updates can bring bugs — or a backdoor."),
                q("Política de patching deve definir:",
                  "Prazos de remediação por severidade.",
                  ["Só o nome do time responsável, sem prazo definido de fato.",
                   "Só o custo estimado da correção, sem prazo associado.",
                   "Só a regra de lint aplicada, sem relação com prazo de patch."],
                  "Sem SLA, nada vira prioridade. Documente no SECURITY.md.",
                  statement_en="A patching policy should define:",
                  correct_en="Remediation deadlines by severity.",
                  wrong_en=["Only the owning team's name, with no real deadline.",
                            "Only the estimated fix cost, with no associated deadline.",
                            "Only the lint rule applied, unrelated to patch deadlines."],
                  explanation_en="Without an SLA, nothing becomes a priority. Document it in SECURITY.md."),
                q("Quando SCA aponta CVE em transitiva:",
                  "Avalie se há override possível ou alternativa.",
                  ["Force o merge do PR, ignorando o alerta apresentado.",
                   "Ignore o alerta de forma automática, pulando qualquer avaliação.",
                   "Apague o lockfile inteiro, esperando que o problema suma sozinho."],
                  "Em alguns ecossistemas você pode forçar versão (npm overrides, Maven dependencyManagement).",
                  statement_en="When SCA flags a CVE in a transitive dependency:",
                  correct_en="Evaluate whether an override or alternative is possible.",
                  wrong_en=["Force-merge the PR, ignoring the alert shown.",
                            "Ignore the alert automatically, skipping any evaluation.",
                            "Delete the entire lockfile and hope the problem disappears."],
                  explanation_en="In some ecosystems you can force a version (npm overrides, Maven dependencyManagement)."),
                q("OSV.dev é:",
                  "Banco aberto de vulnerabilidades de open source.",
                  ["Um registro de container usado para guardar imagem Docker.",
                   "Um linter que verifica estilo de código antes do commit.",
                   "Um banco de dado relacional hospedado na nuvem do Google."],
                  "Mantido pelo Google. APIs gratuitas; integra com Trivy, OSV-Scanner.",
                  statement_en="OSV.dev is:",
                  correct_en="An open database of open-source vulnerabilities.",
                  wrong_en=["A container registry used to store Docker images.",
                            "A linter that checks code style before commit.",
                            "A relational database hosted on Google Cloud."],
                  explanation_en="Maintained by Google. Free APIs; integrates with Trivy and OSV-Scanner."),
                q("PR de update sem testes pode:",
                  "Quebrar produção mesmo com 'fix de segurança'.",
                  ["Aumenta o volume de log gerado pela aplicação em produção.",
                   "É seguro aplicar na maioria dos casos, sem risco associado.",
                   "Reduz o custo mensal pago pela licença da dependência."],
                  "Patch numa lib pode mudar API. Suite de testes razoável é pré-requisito.",
                  statement_en="An update PR without tests can:",
                  correct_en="Break production even as a 'security fix'.",
                  wrong_en=["Increase the volume of logs the app produces in production.",
                            "Be safe to apply in most cases, with no associated risk.",
                            "Reduce the monthly cost of the dependency license."],
                  explanation_en="A patch in a library can change APIs. A reasonable test suite is a prerequisite."),
            ],
        },
        # =====================================================================
        # 3.9 Code Review
        # =====================================================================
        {
            "title": "Code Review",
            "title_en": 'Code Review',
            "summary": "O processo humano de revisar segurança antes do deploy.",
            "summary_en": 'The human process of reviewing security before deploy.',
            "lesson": {
                "intro": (
                    "Tooling captura o óbvio, linter, SAST, SCA, testes. Humano captura o "
                    "sutil, lógica de negócio, design, edge cases, intent. Code review é "
                    "onde a segurança vira cultura, e onde o time aprende junto. Bem feito, "
                    "é um dos momentos mais valiosos do dia. Mal feito, é gargalo, "
                    "passivo-agressivo, ou rubber stamp. Esta aula cobre como tornar review "
                    "rápido, útil e respeitoso, e quais checklists / práticas separam times "
                    "de alta performance."
                ),
                "intro_en": (
                    "Tooling catches the obvious — linters, SAST, SCA, tests. Humans catch the "
                    "subtle — business logic, design, edge cases, intent. Code review is "
                    "where security becomes culture, and where the team learns together. Done well, "
                    "it is one of the most valuable moments of the day. Done poorly, it is a bottleneck, "
                    "passive-aggressive, or a rubber stamp. This lesson covers how to make review "
                    "fast, useful, and respectful, and which checklists / practices separate "
                    "high-performing teams."
                ),
                "body": (
                """<h3>1. Princípios de PR/MR de qualidade</h3>
<h4>1.1 Tamanho importa</h4>
<p>Uma estatística repetidamente confirmada por Google, Microsoft e
Meta: a qualidade do review cai dramaticamente acima de ~200 linhas de
diff. Isso acontece porque a capacidade de atenção humana não escala
linearmente com o tamanho do PR — a partir de certo ponto, o reviewer
passa a "aprovar de olho" em vez de rastrear cada mudança de fato. Na
prática, PRs de 1000+ linhas recebem cerca de 5% mais aprovação rápida
E cerca de 50% mais bugs chegando em produção, comparado a PRs de
200 linhas — o oposto do que a aprovação rápida sugeriria. A saída é
quebrar um PR grande em uma sequência menor e mais digerível: um PR de
refactor neutro (rename, mover arquivo), seguido de um PR com a nova
interface ainda vazia, depois um PR com a implementação em si, e por
fim um PR de integração — cada um pequeno o bastante para ser revisado
de verdade.</p>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>PR pequeno, uma intenção clara</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Descrição com contexto e risco</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Testes / evidência de que funciona</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Revisor foca em correção, não em ego</p></div>
  </div>
  <figcaption>Princípios de um PR que dá para revisar de verdade.</figcaption>
</figure>

<h4>1.2 Contexto claro</h4>
<p>Um reviewer não deveria precisar adivinhar "por que esta mudança
existe" — um template de PR força essa informação a aparecer sempre:</p>
<pre><code>## O que muda?
Adiciona rate limiting no endpoint /login.

## Por quê?
Mitiga brute force. Issue: SEC-1234.

## Como testar?
1. POST /login com 6 senhas erradas em &lt;15min
2. Próxima request deve retornar 429

## Risco?
Usuário legítimo errando senha repetidamente. Mensagem clara orienta
esperar. WAF tem regra de bypass para IPs confiáveis.

## Checklist
- [x] Testes adicionados
- [x] Logs sem PII
- [x] Documentação
- [ ] Verificar com SRE antes do deploy</code></pre>
<h4>1.3 Tom respeitoso</h4>
<p>A diferença entre "aqui está confuso, talvez X?" e "isso está
errado" não é só cortesia — muda se o autor lê o comentário com a
guarda baixa ou já na defensiva. Conventional Comments dão uma
estrutura que deixa a intenção explícita em vez de implícita:</p>
<pre><code>**suggestion**: poderia usar dataclass aqui, mais idiomático
**nitpick**: comma no final
**question**: por que não usar threadpool aqui?
**issue (blocking)**: SQL injection, use parametrização
**praise**: adorei essa abstração, simplifica muito</code></pre>
<p>O rótulo <em>praise</em> é subestimado na prática, mas reconhecer
uma boa decisão explicitamente ensina o time o que repetir, tão
importante quanto apontar o que evitar.</p>
<h4>1.4 Reviewer responde rápido</h4>
<p>Um PR parado é literalmente dinheiro queimando: o autor perde
contexto a cada hora de espera e precisa "recarregar" o problema na
cabeça quando finalmente chega feedback. Um SLA saudável de referência é
TTFR (Time to First Review) abaixo de 4h em horário de trabalho, caindo
para menos de 1h em PRs urgentes.</p>

<h3>2. Checklist de segurança em PR</h3>
<p>Para PRs tocando código sensível — autenticação, dado pessoal,
pagamento — vale validar explicitamente uma lista específica, porque
esses são exatamente os pontos onde um erro sutil vira incidente sério:
se todo input do usuário é validado ou sanitizado antes de uso; se
saída para HTML, SQL ou shell tem o escape correto aplicado onde
necessário; se um endpoint novo tem autenticação certa E se a
autorização checa o RECURSO específico sendo acessado, não só se o
usuário está logado (a diferença entre "você está autenticado" e "você
pode acessar ESTE registro"); se dado sensível — CPF, e-mail, token —
não está vazando em log, usando <code>mask_pii()</code> onde aplicável;
se mensagem de erro não vaza stack trace para o usuário final, com
mensagem genérica cobrindo erro 500; se a criptografia usada é a
correta (hash de senha com bcrypt ou argon2, nunca md5; geração de
número aleatório com <code>secrets</code>, nunca <code>random</code>;
TLS verificado, não desabilitado "temporariamente"); se existe race
condition não coberta por lock ou transação onde o cenário exige; se
dependência nova já passou pelo SCA e é de fato mantida ativamente, com
licença compatível (MIT/Apache, não GPL de efeito viral onde isso
importa); se os caminhos novos têm teste cobrindo edge case e cenário
negativo, não só o caminho feliz; e se a API existente continua
funcionando sem quebra, com qualquer migração de banco tendo caminho de
rollback definido.</p>

<h3>3. CODEOWNERS: quem revisa o quê</h3>
<div class="mermaid">
flowchart LR
    Path["path no CODEOWNERS"] --> Owners["Owners obrigatórios"]
    Owners --> Review["Review aprovado"]
    Review --> Merge["Merge liberado"]
</div>

<pre><code># .github/CODEOWNERS
# Pessoas/equipes que reviewam por path
*                 @empresa/dev-platform
/security/        @empresa/sec-team
/payment/         @empresa/payments-squad @empresa/sec-team
/iac/terraform/   @empresa/sre @empresa/sec-team
*.md              @empresa/docs
**/migrations/    @empresa/dba</code></pre>
<p>Combinado com branch protection, o GitHub passa a EXIGIR aprovação
do dono declarado daquele path — um PR em <code>/payment/</code>
simplesmente não mergeia sem aprovação de
<code>@empresa/payments-squad</code> E <code>@empresa/sec-team</code>.
Isso garante que a pessoa certa olhe a mudança certa, sem depender de
alguém lembrar de chamá-la manualmente.</p>

<h3>4. Ferramentas no PR poupam tempo</h3>
<p>Antes de qualquer reviewer humano abrir o diff, o CI já deveria ter
respondido um conjunto de perguntas mecânicas: o build passou? o lint
está limpo? SAST/SCA não encontrou nada high ou critical? a cobertura
de teste não caiu (codecov/coveralls)? os benchmarks de performance
continuam dentro do esperado (Bencher)? o diff visual não introduziu
regressão (Chromatic, Percy)? Delegar tudo isso para automação libera o
reviewer humano para focar exatamente onde ele agrega mais valor —
design e lógica — em vez de gastar atenção em "falta um espaço aqui".</p>

<h3>5. Anti-patterns clássicos</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Evite</strong><p>LGTM sem ler, bikeshedding de estilo, PR gigante de sexta à noite.</p></div>
    <div class="lesson-viz-card"><strong>Prefira</strong><p>Comentários acionáveis, checagem de segurança, SLA de review do time.</p></div>
  </div>
  <figcaption>Anti-patterns clássicos de code review.</figcaption>
</figure>

<ul>
<li><strong>Rubber stamp</strong>: aprovar sem realmente ler, comum
especialmente em PR de alguém sênior ("quem sou eu para discordar?"). A
métrica de alerta é a porcentagem de PRs aprovados com zero comentário —
acima de 50% já é suspeito.</li>
<li><strong>Bikeshedding</strong>: discutir a cor do botão por dias
enquanto uma SQL injection passa batido — a Lei de Parkinson descreve
exatamente isso: o tempo gasto discutindo uma decisão tende a ser
inversamente proporcional à real importância dela.</li>
<li><strong>PR de 3000 linhas</strong>: ninguém revisa isso de verdade
(seção 1.1) — a resposta certa é pedir para quebrar, não tentar revisar
mesmo assim.</li>
<li><strong>Reviewer único</strong>: se só uma pessoa revisa
determinada área, ela vira ponto único de falha — e queima, porque
carrega o peso sozinha indefinidamente.</li>
<li><strong>"Aprovar e pedir teste depois"</strong>: o "depois" quase
nunca chega, porque a pressão que motivava a correção já passou junto
com o merge.</li>
<li><strong>Comentário adversarial</strong> ("isso é horrível"): tóxico
e ineficaz — não muda o código mais rápido, só o clima do time.</li>
<li><strong>Reescrita silenciosa</strong>: o reviewer reescreve o
código em vez de pedir a mudança — o autor não aprende nada com isso e
fica ressentido pela decisão tomada sem ele.</li>
<li><strong>Aprovar sem CI verde</strong>: anula o propósito de o CI
existir (seção 4).</li>
<li><strong>Bloquear merge por preferência pessoal</strong>: bloqueio
deveria reservar-se a bug real ou risco de segurança — estilo é
nitpick, não motivo de travar o PR.</li>
</ul>

<h3>6. Métricas saudáveis</h3>
<p>Cinco números indicam se o processo de review está funcionando de
verdade. O <strong>TTFR</strong> (Time to First Review) abaixo de 4h em
PR normal mostra que ninguém fica esperando desnecessariamente. O
<strong>Time to Merge</strong> abaixo de 24h na maioria dos casos evita
que trabalho fique acumulando em limbo. O número de
<strong>comentários por PR</strong> entre 1 e 10 é o intervalo saudável
— zero sugere rubber stamp (seção 5), e mais de 50 sugere um PR grande
demais ou um autor que não revisou o próprio trabalho antes de abrir. A
<strong>taxa de defeito escapado</strong> mede quantos bugs passam pelo
review inteiro e chegam a produção — se está subindo, o review está
ficando superficial, mesmo que os números de velocidade pareçam bons. E
a <strong>participação em review</strong> revela bus factor: se só uma
ou duas pessoas revisam a maior parte do código, distribuir via
round-robin (seção 7) evita concentração de risco. Como referência
geral, PR parado por mais de 3 dias já degrada moral do time — a meta
deveria mirar bem abaixo de 24h.</p>

<h3>7. Round-robin e ownership distribuído</h3>
<p>O auto-assignment por round-robin do GitHub evita que todo PR caia
sempre na mesma pessoa disponível — numa squad de 6 desenvolvedores,
cada PR novo é distribuído aleatoriamente entre eles. Combinado com
CODEOWNERS (seção 3) para as áreas mais críticas, esse mecanismo
distribui carga de trabalho E espalha conhecimento do código pela
equipe, em vez de concentrar tudo numa só pessoa que "sempre revisa
aquela parte".</p>

<h3>8. Pair review e mob review</h3>
<p>Para mudanças especialmente críticas — autenticação, infraestrutura,
migração de dado — três formatos alternativos ao review assíncrono
padrão fazem sentido. <strong>Pair review</strong> senta reviewer e
autor juntos (presencial ou em call) passando pelo PR em tempo real,
produzindo discussão mais rica e decisão mais rápida do que trocar
comentários por horas. <strong>Mob review</strong> reúne de 3 a 5
pessoas revisando juntas, útil especificamente para decisão de design
que afeta muita gente. E um híbrido <strong>async + sync</strong> mantém
o fluxo normal assíncrono no GitHub, reservando uma sessão síncrona
rápida só para resolver um impasse específico que travou por texto.</p>

<h3>9. Reviewer guia (cheat sheet do reviewer)</h3>
<ol>
<li>Leia a descrição do PR antes do código — o contexto muda como você
lê o diff.</li>
<li>Veja o overview do diff inteiro antes de entrar linha por linha,
para entender o escopo real da mudança.</li>
<li>Identifique risco logo de saída: é endpoint novo? biblioteca nova?
mudança em autenticação?</li>
<li>Priorize nessa ordem: design, depois correção, depois
manutenibilidade, e só por último estilo.</li>
<li>Comente como pergunta, não como comando — abre espaço para o autor
explicar uma decisão que você não viu de imediato.</li>
<li>Aprove rápido quando está tudo certo — não "segure" o PR por
preciosismo.</li>
<li>Se o PR é grande demais para revisar de verdade, peça para quebrar
em partes menores (seção 1.1) em vez de aprovar sem ler tudo.</li>
<li>Se a discordância é grande, agende uma conversa síncrona — texto
longo tende a gerar mal-entendido que só piora por escrito.</li>
</ol>"""
                ),
                "body_en": """<h3>1. Principles of quality PRs/MRs</h3>
<h4>1.1 Size matters</h4>
<p>A statistic repeatedly confirmed by Google, Microsoft, and
Meta: review quality drops dramatically above ~200 lines of
diff. Human attention does not scale
linearly with PR size — past a point, the reviewer
starts "approving by eye" instead of tracking every real change. In
practice, 1000+ line PRs get about 5% more quick approvals
AND about 50% more bugs reaching production compared to 200-line
PRs — the opposite of what quick approval would suggest. The fix is
to split a large PR into a smaller, more digestible sequence: a neutral
refactor PR (rename, move files), then a PR with the new
still-empty interface, then a PR with the implementation itself, and
finally an integration PR — each small enough to review for
real.</p>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Small PR, one clear intent</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Description with context and risk</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Tests / evidence it works</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Reviewer focuses on correctness, not ego</p></div>
  </div>
  <figcaption>Principles of a PR that can actually be reviewed.</figcaption>
</figure>

<h4>1.2 Clear context</h4>
<p>A reviewer should not have to guess "why this change
exists" — a PR template forces that information to always appear:</p>
<pre><code>## O que muda?
Adiciona rate limiting no endpoint /login.

## Por quê?
Mitiga brute force. Issue: SEC-1234.

## Como testar?
1. POST /login com 6 senhas erradas em &lt;15min
2. Próxima request deve retornar 429

## Risco?
Usuário legítimo errando senha repetidamente. Mensagem clara orienta
esperar. WAF tem regra de bypass para IPs confiáveis.

## Checklist
- [x] Testes adicionados
- [x] Logs sem PII
- [x] Documentação
- [ ] Verificar com SRE antes do deploy</code></pre>
<h4>1.3 Respectful tone</h4>
<p>The difference between "this is confusing — maybe X?" and "this is
wrong" is not just courtesy — it changes whether the author reads the comment with
their guard down or already defensive. Conventional Comments give a
structure that makes intent explicit instead of implicit:</p>
<pre><code>**suggestion**: poderia usar dataclass aqui, mais idiomático
**nitpick**: comma no final
**question**: por que não usar threadpool aqui?
**issue (blocking)**: SQL injection, use parametrização
**praise**: adorei essa abstração, simplifica muito</code></pre>
<p>The <em>praise</em> label is underrated in practice, but recognizing
a good decision explicitly teaches the team what to repeat — as
important as pointing out what to avoid.</p>
<h4>1.4 Reviewers respond quickly</h4>
<p>A stalled PR is literally burning money: the author loses
context every hour of waiting and must "reload" the problem in their
head when feedback finally arrives. A healthy reference SLA is
TTFR (Time to First Review) under 4h during working hours, dropping
under 1h for urgent PRs.</p>

<h3>2. Security checklist on PRs</h3>
<p>For PRs touching sensitive code — authentication, personal data,
payments — explicitly validate a specific list, because
those are exactly where a subtle mistake becomes a serious incident:
whether every user input is validated or sanitized before use; whether
output to HTML, SQL, or shell has the correct escaping applied where
needed; whether a new endpoint has the right authentication AND whether
authorization checks the specific RESOURCE being accessed, not just whether the
user is logged in (the difference between "you are authenticated" and "you
may access THIS record"); whether sensitive data — tax IDs, email, tokens —
is not leaking in logs, using <code>mask_pii()</code> where applicable;
whether error messages do not leak stack traces to end users, with a
generic message covering 500 errors; whether the cryptography used is
correct (password hashing with bcrypt or argon2, never md5; random number
generation with <code>secrets</code>, never <code>random</code>;
TLS verified, not disabled "temporarily"); whether there is a race
condition uncovered by a lock or transaction where the scenario requires it; whether
a new dependency already passed SCA and is actually actively maintained, with a
compatible license (MIT/Apache, not viral GPL where that
matters); whether new paths have tests covering edge cases and negative
scenarios, not only the happy path; and whether the existing API still
works without breakage, with any database migration having a defined
rollback path.</p>

<h3>3. CODEOWNERS: who reviews what</h3>
<div class="mermaid">
flowchart LR
    Path["path in CODEOWNERS"] --> Owners["Required owners"]
    Owners --> Review["Approved review"]
    Review --> Merge["Merge allowed"]
</div>

<pre><code># .github/CODEOWNERS
# Pessoas/equipes que reviewam por path
*                 @empresa/dev-platform
/security/        @empresa/sec-team
/payment/         @empresa/payments-squad @empresa/sec-team
/iac/terraform/   @empresa/sre @empresa/sec-team
*.md              @empresa/docs
**/migrations/    @empresa/dba</code></pre>
<p>Combined with branch protection, GitHub starts REQUIRING approval
from the declared owner of that path — a PR under <code>/payment/</code>
simply will not merge without approval from
<code>@empresa/payments-squad</code> AND <code>@empresa/sec-team</code>.
That ensures the right person looks at the right change, without depending on
someone remembering to ping them manually.</p>

<h3>4. Tools on the PR save time</h3>
<p>Before any human reviewer opens the diff, CI should already have
answered a set of mechanical questions: did the build pass? is lint
clean? did SAST/SCA find nothing high or critical? did test coverage
not drop (codecov/coveralls)? are performance benchmarks still within
expectations (Bencher)? did the visual diff introduce no
regression (Chromatic, Percy)? Delegating all of that to automation frees the
human reviewer to focus exactly where they add the most value —
design and logic — instead of spending attention on "missing a space here".</p>

<h3>5. Classic anti-patterns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--compare">
    <div class="lesson-viz-card"><strong>Avoid</strong><p>LGTM without reading, style bikeshedding, giant Friday-night PRs.</p></div>
    <div class="lesson-viz-card"><strong>Prefer</strong><p>Actionable comments, security checks, team review SLA.</p></div>
  </div>
  <figcaption>Classic code-review anti-patterns.</figcaption>
</figure>

<ul>
<li><strong>Rubber stamp</strong>: approving without really reading, common
especially on a senior's PR ("who am I to disagree?"). The
alert metric is the percentage of PRs approved with zero comments —
above 50% is already suspicious.</li>
<li><strong>Bikeshedding</strong>: debating button color for days
while a SQL injection slips through — Parkinson's Law describes
exactly this: time spent debating a decision tends to be
inversely proportional to its real importance.</li>
<li><strong>3000-line PRs</strong>: nobody truly reviews that
(section 1.1) — the right response is to ask for a split, not try to review
anyway.</li>
<li><strong>Single reviewer</strong>: if only one person reviews
a given area, they become a single point of failure — and burn out, because
they carry the weight alone indefinitely.</li>
<li><strong>"Approve and ask for tests later"</strong>: "later" almost
never arrives, because the pressure that motivated the fix already passed with
the merge.</li>
<li><strong>Adversarial comments</strong> ("this is horrible"): toxic
and ineffective — they do not change the code faster, only the team climate.</li>
<li><strong>Silent rewrites</strong>: the reviewer rewrites the
code instead of asking for the change — the author learns nothing and
resents a decision made without them.</li>
<li><strong>Approving without green CI</strong>: nullifies the purpose of having
CI (section 4).</li>
<li><strong>Blocking merge over personal preference</strong>: blocking
should be reserved for real bugs or security risk — style is a
nitpick, not a reason to stall the PR.</li>
</ul>

<h3>6. Healthy metrics</h3>
<p>Five numbers show whether the review process is truly working.
<strong>TTFR</strong> (Time to First Review) under 4h on
normal PRs shows nobody is waiting unnecessarily.
<strong>Time to Merge</strong> under 24h in most cases avoids
work piling up in limbo. The number of
<strong>comments per PR</strong> between 1 and 10 is the healthy range
— zero suggests rubber stamp (section 5), and more than 50 suggests a PR that is too
large or an author who did not review their own work before opening.
<strong>Escaped defect rate</strong> measures how many bugs pass the
entire review and reach production — if it is rising, review is getting
shallow even if speed numbers look good. And
<strong>review participation</strong> reveals bus factor: if only one
or two people review most of the code, distribute via
round-robin (section 7) to avoid risk concentration. As a general
reference, a PR idle more than 3 days already degrades team morale — the goal
should aim well under 24h.</p>

<h3>7. Round-robin and distributed ownership</h3>
<p>GitHub's round-robin auto-assignment stops every PR from always landing
on the same available person — in a squad of 6 developers,
each new PR is distributed randomly among them. Combined with
CODEOWNERS (section 3) for the most critical areas, this mechanism
spreads workload AND spreads code knowledge across the
team, instead of concentrating everything on one person who "always reviews
that part".</p>

<h3>8. Pair review and mob review</h3>
<p>For especially critical changes — authentication, infrastructure,
data migration — three alternatives to standard async review
make sense. <strong>Pair review</strong> sits reviewer and
author together (in person or on a call) walking the PR in real time,
producing richer discussion and faster decisions than trading
comments for hours. <strong>Mob review</strong> gathers 3 to 5
people reviewing together, useful specifically for design decisions
that affect many people. And a hybrid <strong>async + sync</strong> keeps
the normal async GitHub flow, reserving a quick sync session
only to resolve a specific deadlock that got stuck in text.</p>

<h3>9. Reviewer guide (reviewer cheat sheet)</h3>
<ol>
<li>Read the PR description before the code — context changes how you
read the diff.</li>
<li>Look at the whole-diff overview before going line by line,
to understand the real scope of the change.</li>
<li>Identify risk early: new endpoint? new library?
auth change?</li>
<li>Prioritize in this order: design, then correctness, then
maintainability, and only last style.</li>
<li>Comment as a question, not a command — leaves room for the author
to explain a decision you did not see immediately.</li>
<li>Approve quickly when everything is fine — do not "hold" the PR over
pedantry.</li>
<li>If the PR is too large to review for real, ask to split
into smaller parts (section 1.1) instead of approving without reading it all.</li>
<li>If disagreement is large, schedule a sync conversation — long text
tends to create misunderstandings that only get worse in writing.</li>
</ol>""",
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Crie PR template em <code>.github/pull_request_template.md</code> "
                    "com checklist (auth, validação, log sem PII, testes, backward "
                    "compat).</li>"
                    "<li>Configure CODEOWNERS: <code>/security/</code> exige sec-team; "
                    "migrations exigem DBA; .md exige docs.</li>"
                    "<li>Configure branch protection com 1 review obrigatório + signed "
                    "commits + status checks.</li>"
                    "<li>Configure auto-assignment round-robin para distribuir.</li>"
                    "<li>Adicione codecov bot que comenta cobertura no PR.</li>"
                    "<li>Crie um PR de teste com 'mau-pattern' (SQL concat, log com PII) "
                    "e veja se SAST + reviewer pegam.</li>"
                    "<li>Bonus: configure GitHub Insights para acompanhar TTFR e "
                    "merge time.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Full hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>Create a PR template in <code>.github/pull_request_template.md</code> "
                    "with a checklist (auth, validation, logs without PII, tests, backward "
                    "compat).</li>"
                    "<li>Configure CODEOWNERS: <code>/security/</code> requires sec-team; "
                    "migrations require a DBA; .md requires docs.</li>"
                    "<li>Configure branch protection with 1 required review + signed "
                    "commits + status checks.</li>"
                    "<li>Configure round-robin auto-assignment to distribute load.</li>"
                    "<li>Add a codecov bot that comments coverage on the PR.</li>"
                    "<li>Create a test PR with a bad pattern (SQL concat, PII in logs) "
                    "and see if SAST + the reviewer catch it.</li>"
                    "<li>Bonus: configure GitHub Insights to track TTFR and "
                    "merge time.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("Google: Code Review Developer Guide", "https://google.github.io/eng-practices/review/", "article", "",
                  title_en="Google: Code Review Developer Guide", description_en=""),
                m("OWASP Code Review Guide", "https://owasp.org/www-project-code-review-guide/", "docs", "",
                  title_en="OWASP Code Review Guide", description_en=""),
                m("Conventional comments", "https://conventionalcomments.org/", "article", "",
                  title_en="Conventional comments", description_en=""),
                m("PR template (GitHub)", "https://docs.github.com/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository", "docs", "",
                  title_en="PR template (GitHub)", description_en=""),
                m("ThoughtWorks: code review", "https://www.thoughtworks.com/insights/blog/code-review", "article", "",
                  title_en="ThoughtWorks: code review", description_en=""),
                m("CODEOWNERS docs", "https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners", "docs", "",
                  title_en="CODEOWNERS docs", description_en=""),
            ],
            "questions": [
                q("PR pequeno é melhor porque:",
                  "Reduz tempo e probabilidade de bugs passarem.",
                  ["Passa despercebido em diffs grandes, o revisor lê por cima.",
                   "Cria a falsa impressão de qualidade mais alta no que foi entregue.",
                   "Costuma gerar mais conflito de merge entre branches diferentes."],
                  "Estudos mostram que diffs grandes recebem revisão superficial.",
                  statement_en="A small PR is better because:",
                  correct_en="It reduces time and the chance bugs slip through.",
                  wrong_en=["It goes unnoticed in large diffs where reviewers skim.",
                            "It creates a false impression of higher quality in what was shipped.",
                            "It usually causes more merge conflicts across branches."],
                  explanation_en="Studies show large diffs get shallow reviews."),
                q("Checklist em PR ajuda a:",
                  "Não esquecer de validar pontos críticos.",
                  ["Fica pronto rápido, mesmo sem rodar teste automatizado de verdade.",
                   "Torna o processo de aprovação mais lento e burocrático.",
                   "Reduz a cobertura de teste que aparece no relatório de CI."],
                  "Bom em PRs sensíveis (auth, dados pessoais). Em PRs triviais, pode atrapalhar.",
                  statement_en="A PR checklist helps to:",
                  correct_en="Avoid forgetting to validate critical points.",
                  wrong_en=["Ship fast even without running real automated tests.",
                            "Make the approval process slower and more bureaucratic.",
                            "Reduce the test coverage shown in the CI report."],
                  explanation_en="Good for sensitive PRs (auth, personal data). On trivial PRs it can get in the way."),
                q("Reviewer deve:",
                  "Comentar com clareza, tom respeitoso e sugerir alternativa.",
                  ["Só aprovar o PR direto, pulando qualquer comentário no processo.",
                   "Só reprovar sem explicar o motivo da reprovação ao autor.",
                   "Reescrever o código do autor sem avisar ou discutir a mudança."],
                  "'Aqui está confuso, talvez X?' > 'errado'. Conventional comments dão estrutura.",
                  statement_en="A reviewer should:",
                  correct_en="Comment clearly, respectfully, and suggest alternatives.",
                  wrong_en=["Only approve the PR outright, skipping any comments.",
                            "Only reject without explaining the reason to the author.",
                            "Rewrite the author's code without notice or discussion."],
                  explanation_en="'This is confusing — maybe X?' beats 'wrong'. Conventional comments give structure."),
                q("Mudanças sensíveis precisam:",
                  "Revisão por alguém com perfil de segurança.",
                  ["Só uma IA analisando, sem revisor humano no processo.",
                   "Mesclar automaticamente sem esperar qualquer aprovação humana.",
                   "Pular a verificação obrigatória configurada no repositório."],
                  "Use CODEOWNERS para garantir que sec-team é notificado.",
                  statement_en="Sensitive changes need:",
                  correct_en="Review by someone with a security profile.",
                  wrong_en=["Only an AI analyzing, with no human reviewer.",
                            "Automatic merge without waiting for any human approval.",
                            "Skipping the required checks configured on the repository."],
                  explanation_en="Use CODEOWNERS so the sec-team is notified."),
                q("Revisão sem testes é:",
                  "Risco, pode aprovar bug que CI pegaria.",
                  ["Rápido de concluir, mas às custas da qualidade real do código.",
                   "Recomendado só para PR pequeno e de baixo risco.",
                   "Uma forma eficiente de economizar o tempo do revisor."],
                  "Coverage bot ajuda a barrar code novo sem teste.",
                  statement_en="Review without tests is:",
                  correct_en="A risk — it can approve a bug CI would catch.",
                  wrong_en=["Quick to finish, but at the cost of real code quality.",
                            "Recommended only for small, low-risk PRs.",
                            "An efficient way to save the reviewer's time."],
                  explanation_en="A coverage bot helps block new code without tests."),
                q("Conventional comments:",
                  "Padroniza tipos de comentário (suggestion, nitpick, blocking).",
                  ["Apagam qualquer comentário deixado por outro revisor no mesmo PR.",
                   "Substituem por completo a necessidade de rodar CI antes do merge.",
                   "Forçam a aprovação automática do PR, não importa o conteúdo revisado."],
                  "Reviewer sinaliza intenção: 'nitpick' não bloqueia, 'blocking' bloqueia.",
                  statement_en="Conventional comments:",
                  correct_en="Standardize comment types (suggestion, nitpick, blocking).",
                  wrong_en=["Delete any comment left by another reviewer on the same PR.",
                            "Fully replace the need to run CI before merge.",
                            "Force automatic PR approval regardless of review content."],
                  explanation_en="The reviewer signals intent: 'nitpick' does not block; 'blocking' does."),
                q("PR muito velho:",
                  "Junta merge conflicts e deveria ser refeito ou fragmentado.",
                  ["Fica com gosto melhor quanto mais tempo passa parado.",
                   "Consegue mergear sem esforço extra, não importa o tempo parado.",
                   "Substitui a necessidade de manter documentação do projeto."],
                  "PRs > 1 semana parados raramente terminam bem. Quebre ou cancele.",
                  statement_en="A very old PR:",
                  correct_en="Accumulates merge conflicts and should be redone or split.",
                  wrong_en=["Gets better the longer it sits untouched.",
                            "Merges effortlessly no matter how long it sat.",
                            "Replaces the need to maintain project documentation."],
                  explanation_en="PRs idle for more than a week rarely end well. Split or cancel."),
                q("Reviewer perceber dado sensível em log:",
                  "Pedir remoção/sanitização antes do merge.",
                  ["Aprovar o PR e deixar a correção para depois, como tarefa futura.",
                   "Ignorar, já que log em produção raramente é lido por alguém.",
                   "Adicionar mais dado sensível ao mesmo log, para comparação."],
                  "Após log estar em produção, a chance de remover de SIEM/Datadog é zero.",
                  statement_en="If a reviewer spots sensitive data in a log:",
                  correct_en="Ask for removal/sanitization before merge.",
                  wrong_en=["Approve the PR and leave the fix for later as a future task.",
                            "Ignore it, since production logs are rarely read by anyone.",
                            "Add more sensitive data to the same log for comparison."],
                  explanation_en="Once the log is in production, chance of removing it from SIEM/Datadog is near zero."),
                q("Aprovação 'rubber stamp':",
                  "Aprovar sem ler, viola o propósito do review.",
                  ["Uma forma eficiente de economizar tempo do revisor no PR.",
                   "Uma prática aceitável quando o autor já tem muita experiência.",
                   "Um jeito rápido de manter o fluxo de entrega sem travar."],
                  "Cria sensação de segurança falsa. Métricas (zero comments) podem revelar.",
                  statement_en="'Rubber stamp' approval:",
                  correct_en="Approving without reading — it violates the purpose of review.",
                  wrong_en=["An efficient way to save the reviewer's time on the PR.",
                            "Acceptable when the author already has a lot of experience.",
                            "A quick way to keep delivery flowing without blocking."],
                  explanation_en="Creates a false sense of safety. Metrics (zero comments) can expose it."),
                q("Métrica saudável:",
                  "Time-to-first-review baixo, sem fila eterna.",
                  ["PR gigante acumulado, esperando revisão há semanas seguidas.",
                   "Grande volume de PR aprovado sem leitura de verdade pelo revisor.",
                   "Revisão feita só pelo CTO, sem outro revisor envolvido no time."],
                  "TTFR < 4h para PRs urgentes; < 24h para o resto. Combine com round-robin.",
                  statement_en="A healthy metric:",
                  correct_en="Low time-to-first-review, without an endless queue.",
                  wrong_en=["Giant PRs piled up, waiting weeks for review.",
                            "A high volume of PRs approved without a real read by the reviewer.",
                            "Review done only by the CTO, with no other reviewer on the team."],
                  explanation_en="TTFR < 4h for urgent PRs; < 24h for the rest. Combine with round-robin."),
            ],
        },
        # =====================================================================
        # 3.10 Artifact Repositories
        # =====================================================================
        {
            "title": "Artifact Repositories",
            "title_en": 'Artifact Repositories',
            "summary": "Guardar suas versões de software em locais seguros.",
            "summary_en": 'Store your software versions in safe places.',
            "lesson": {
                "intro": (
                    "Imagem Docker, jar, wheel, helm chart, binário Go, módulo Terraform. "
                    "Todo build gera artefatos. Onde guardar importa para reprodutibilidade "
                    "(rollback?), segurança (assinatura, vuln scan), governance (quem pode "
                    "puxar?), custo (Docker Hub rate limit, S3 egress) e supply chain (impedir "
                    "imagens não assinadas no cluster). Esta aula cobre tipos de registries, "
                    "padrões essenciais (tag imutável, assinatura, SBOM), e como integrar "
                    "tudo no pipeline."
                ),
                "intro_en": (
                    "Docker images, jars, wheels, Helm charts, Go binaries, Terraform modules. "
                    "Every build produces artifacts. Where you store them matters for reproducibility "
                    "(rollback?), security (signing, vuln scan), governance (who can "
                    "pull?), cost (Docker Hub rate limits, S3 egress), and supply chain (blocking "
                    "unsigned images in the cluster). This lesson covers registry types, "
                    "essential patterns (immutable tags, signing, SBOM), and how to integrate "
                    "it all into the pipeline."
                ),
                "body": (
                """<h3>1. Tipos de registries</h3>
<h4>1.1 Container registries</h4>
<p>Cada nuvem oferece seu registry nativo: <strong>AWS ECR</strong> com
controle de acesso via IAM e scan de vulnerabilidade integrado,
<strong>GCP Artifact Registry</strong> (que substituiu o GCR antigo,
com suporte multi-formato para Docker, Maven, npm), e <strong>Azure
Container Registry</strong>. O <strong>GitHub Container Registry</strong>
se destaca por integração automática com GitHub Actions — o token de
autenticação já vem pronto, sem configuração extra. O <strong>Docker
Hub</strong> continua público e gratuito com limite de taxa, pago para
uso ilimitado. O <strong>Harbor</strong>, open source e self-hosted, com
RBAC, scan de vulnerabilidade e replicação nativos, virou o padrão em
times que rodam Kubernetes on-premise. E o <strong>Quay</strong> (Red
Hat) é forte especificamente no ecossistema OpenShift.</p>
<div class="mermaid">
flowchart TD
    Reg["Registries"] --> Cont["Containers: ECR, GHCR, Harbor"]
    Reg --> Lang["Linguagem: npm, Maven, PyPI proxy"]
    Reg --> Helm["Charts / OCI generico"]
</div>

<h4>1.2 Generic / linguagens</h4>
<p>Para artefato que não é imagem de container, o <strong>JFrog
Artifactory</strong> é o veterano do mercado — multi-formato (Docker,
Maven, npm, NuGet, PyPI, RPM), caro mas robusto. O <strong>Sonatype
Nexus</strong> cobre um espaço similar, com edição open source
gratuita. <strong>GitHub Packages</strong> e o <strong>GitLab Package
Registry</strong> vêm integrados nativamente às respectivas
plataformas. E o <strong>Cloudsmith</strong> é uma opção SaaS
multi-formato dedicada.</p>
<h4>1.3 Helm Charts</h4>
<p>A partir do Helm 3, o suporte a OCI nativo significa que qualquer
registry OCI comum (ECR, GHCR, Harbor) já consegue guardar um Helm
chart diretamente, sem precisar de infraestrutura dedicada. O
<code>ChartMuseum</code> ainda existe para quem mantém setup legado.</p>

<h3>2. Padrões essenciais</h3>
<div class="mermaid">
flowchart LR
    Build["Build"] --> Sign["Assina cosign/notation"]
    Sign --> Push["Push por digest"]
    Push --> Pull["Deploy puxa digest"]
</div>

<h4>2.1 Tags imutáveis</h4>
<p>Use SHA do commit ou versão semver como tag — nunca
<code>latest</code>, <code>main</code>, <code>dev</code> ou qualquer
tag "móvel" que pode apontar para conteúdo diferente amanhã sem
aviso:</p>
<pre><code># Bom
ghcr.io/empresa/app:v1.4.2
ghcr.io/empresa/app:abc1234   # commit SHA
ghcr.io/empresa/app@sha256:f0a1b2...   # digest absoluto

# Ruim em prod
ghcr.io/empresa/app:latest
ghcr.io/empresa/app:dev</code></pre>
<p>Referenciar por digest (<code>sha256:...</code>) é o padrão-ouro:
esse identificador é imutável e único por definição, mesmo se alguém
republicar a MESMA tag com conteúdo diferente depois. Habilitar
<strong>tag immutability</strong> no registry (disponível em ECR,
Harbor, ACR) reforça isso estruturalmente — a tag simplesmente não pode
ser sobrescrita, mesmo por acidente.</p>
<h4>2.2 Assinatura com Cosign (Sigstore)</h4>
<p>Sem assinatura, um atacante que comprometa o registry pode trocar a
imagem por outra maliciosa sem que ninguém perceba — o nome e a tag
continuam os mesmos, só o conteúdo mudou. O Cosign fecha essa lacuna:</p>
<pre><code>$ cosign sign --yes ghcr.io/empresa/app:v1.4.2
Generating ephemeral keys... [OIDC: 'ci@empresa.com']
tlog entry written: rekor.sigstore.dev

$ cosign verify ghcr.io/empresa/app:v1.4.2 \\
    --certificate-identity ci@empresa.com \\
    --certificate-oidc-issuer https://token.actions.githubusercontent.com
Verification for ghcr.io/empresa/app:v1.4.2 --
The following checks were performed on each of these signatures:
  - Signature was verified
  - Identity matched expectation</code></pre>
<p>Combinar isso com um admission controller no Kubernetes (Sigstore
Policy Controller, Kyverno) fecha o ciclo completo: o cluster rejeita
qualquer imagem que não tenha assinatura válida, tornando a verificação
obrigatória, não opcional:</p>
<pre><code>apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-signed-images }
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-signature
      match:
        any:
          - resources: { kinds: [Pod] }
      verifyImages:
        - imageReferences: ['ghcr.io/empresa/*']
          attestors:
            - keyless:
                subject: ci@empresa.com
                issuer: https://token.actions.githubusercontent.com</code></pre>
<h4>2.3 SBOM atrelado</h4>
<p>Anexar o SBOM diretamente como referrer no próprio registry OCI
mantém a lista de dependências junto do artefato que ela descreve, em
vez de num documento separado que pode desatualizar:</p>
<pre><code>$ syft ghcr.io/empresa/app:v1.4.2 -o cyclonedx-json &gt; sbom.json
$ cosign attach sbom --sbom sbom.json ghcr.io/empresa/app:v1.4.2
$ cosign attest --predicate sbom.json --type cyclonedx \\
    ghcr.io/empresa/app:v1.4.2</code></pre>
<p>Quando um incidente exigir responder rapidamente "quem está usando
log4j 2.14?", ter o SBOM atrelado a cada imagem específica transforma
essa pergunta de investigação manual em uma consulta direta.</p>
<h4>2.4 Provenance / SLSA</h4>
<p>Um atestado de proveniência documenta COMO o artefato foi
construído, não só o que ele contém — o nível SLSA L3 ou superior exige
que esse atestado venha de um builder confiável, não de qualquer
máquina arbitrária. O GitHub Actions já tem um template oficial para
gerar isso automaticamente:</p>
<pre><code>- uses: slsa-framework/slsa-github-generator/.github/workflows/builder_container_slsa3.yml@v1.10.0</code></pre>
<p>O resultado é a imagem acompanhada de um
<code>provenance.intoto.jsonl</code> verificável, provando de onde
exatamente ela veio.</p>

<h3>3. RBAC e segregação</h3>
<p>Cinco práticas de controle de acesso separam um registry bem
governado de um em risco. Escrita (push) deve ficar restrita
exclusivamente ao CI — nenhum desenvolvedor faz push direto, usando
idealmente token OIDC de curta duração em vez de credencial estática.
Leitura deve ser escopada por equipe ou produto, com ambiente
multi-tenant usando namespace separado por time. Em produção, o pull
deve usar um pull-secret específico do próprio cluster, nunca uma
credencial humana reaproveitada. Tokens de curta duração via OIDC+STS
são preferíveis a token estático em qualquer cenário onde isso é
viável. E um log de auditoria do registry — quem puxou o quê e quando —
se torna essencial no meio de qualquer investigação de incidente.</p>

<h3>4. Retenção e custo</h3>
<p>Sem política de retenção, um registry acumula gigabyte após
gigabyte silenciosamente: cada PR gera sua própria imagem de teste, e
build antigo acumula CVE nova a cada semana que passa, mesmo sem
ninguém tocar nele — o custo de storage escala proporcionalmente a essa
acumulação:</p>
<pre><code># Exemplo ECR lifecycle
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
<p>Além de reduzir a fatura, essa limpeza reduz a superfície de
ataque: uma imagem antiga esquecida no registry, com vulnerabilidade
conhecida, é exatamente o tipo de alvo fácil que um atacante procura
antes de tentar algo mais sofisticado.</p>

<h3>5. Pull-through cache</h3>
<p>Fazer cada execução de pipeline puxar direto do Docker Hub esbarra
rápido no rate limit generoso, mas finito, do plano gratuito — a
alternativa é usar o registry interno como camada de cache
intermediária, via Harbor proxy cache, ECR pull-through (configurável
para Docker Hub, Quay, GHCR) ou um repositório remoto do Artifactory.
Isso acelera o build com cache local, mantém o pipeline funcionando
mesmo durante uma indisponibilidade do registry upstream, gera
auditoria do que efetivamente vem de fora, e abre espaço para
scan ou quarentena antes de qualquer imagem externa ser de fato
usada.</p>

<h3>6. Vulnerability scanning contínuo</h3>
<p>Escanear apenas no momento do push é insuficiente por natureza —
uma CVE nova pode ser descoberta semanas depois, numa imagem que já
estava limpa quando publicada. A resposta é configurar re-scan
periódico (agendamento no Harbor, Trivy Operator no Kubernetes, ECR
Enhanced Scanning), notificação automática quando uma imagem já em
produção passa a ser considerada vulnerável (webhook disparando para
Slack), e uma política de admissão que bloqueia ativamente qualquer
imagem com CVE crítica de rodar em produção, mesmo que já tenha sido
aprovada no passado.</p>

<h3>7. Multi-arch images</h3>
<p>Com ARM (Graviton na AWS, Apple Silicon localmente) coexistindo com
AMD64 no dia a dia, o build precisa produzir as duas arquiteturas de
uma vez:</p>
<pre><code>docker buildx build --platform linux/amd64,linux/arm64 \\
  --tag ghcr.io/empresa/app:v1.4.2 \\
  --push .</code></pre>
<p>O resultado é um manifest list — uma referência única que aponta
para as duas variantes de arquitetura ao mesmo tempo — e o pull
seleciona automaticamente a arquitetura correta para a máquina que está
puxando, sem nenhuma configuração adicional do lado do cliente.</p>

<h3>8. Anti-patterns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Imagens sempre por digest, não por tag mutável</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Assinatura + policy de admissão</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Scan contínuo no registry</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Segregação prod vs não-prod</p></div>
  </div>
  <figcaption>Lições do caso SolarWinds aplicadas a artifacts.</figcaption>
</figure>

<ul>
<li><strong>Usar apenas <code>latest</code> em produção</strong>: zero
rastreabilidade sobre qual código está de fato rodando (seção 2.1).</li>
<li><strong>Nenhuma política de retenção</strong>: gigabyte acumulando
sem controle (seção 4).</li>
<li><strong>Push sem assinar</strong>: deixa a cadeia de suprimentos
vulnerável a troca silenciosa de imagem (seção 2.2).</li>
<li><strong>Token estático no registry</strong>: se vazar, o atacante
consegue puxar tudo sem limite de tempo.</li>
<li><strong>Imagem publicada em registry público sem scan ou
auditoria</strong>: qualquer um pode puxar código não verificado.</li>
<li><strong>Rebuild direto em produção</strong>: "só recompilei lá"
produz um artefato literalmente diferente do que passou pelos
testes.</li>
<li><strong>Não usar pull-through cache</strong>: rate limit batendo em
horário de pico paralisa o CI inteiro sem aviso (seção 5).</li>
</ul>

<h3>9. Caso real: SolarWinds (2020)</h3>
<p>Atacantes comprometeram diretamente o pipeline de BUILD da
SolarWinds, injetando código malicioso no produto Orion ANTES da etapa
de assinatura acontecer — o que significa que a imagem "oficial"
assinada já saía comprometida de fábrica. Centenas de empresas,
incluindo agências do governo americano, baixaram essa versão
"oficial" com backdoor embutido, confiando exatamente na assinatura que
deveria garantir integridade. A lição central: assinar não basta se o
PROCESSO de build em si não é confiável — daí a exigência de SLSA nível
3 ou superior (seção 2.4), que valida a cadeia de build, não só o
artefato final. Idealmente, um build reprodutível (o mesmo input sempre
produz exatamente a mesma saída) permite que múltiplas partes
independentes verifiquem o resultado sem precisar confiar cegamente
numa única infraestrutura de build.</p>"""
                ),
                "body_en": """<h3>1. Registry types</h3>
<h4>1.1 Container registries</h4>
<p>Each cloud offers its native registry: <strong>AWS ECR</strong> with
IAM access control and integrated vulnerability scanning,
<strong>GCP Artifact Registry</strong> (which replaced old GCR,
with multi-format support for Docker, Maven, npm), and <strong>Azure
Container Registry</strong>. <strong>GitHub Container Registry</strong>
stands out for automatic GitHub Actions integration — the auth
token comes ready, with no extra configuration. <strong>Docker
Hub</strong> remains public and free with rate limits, paid for
unlimited use. <strong>Harbor</strong>, open source and self-hosted, with
native RBAC, vulnerability scanning, and replication, became the default in
teams running on-prem Kubernetes. And <strong>Quay</strong> (Red
Hat) is strong specifically in the OpenShift ecosystem.</p>
<div class="mermaid">
flowchart TD
    Reg["Registries"] --> Cont["Containers: ECR, GHCR, Harbor"]
    Reg --> Lang["Language: npm, Maven, PyPI proxy"]
    Reg --> Helm["Charts / generic OCI"]
</div>

<h4>1.2 Generic / language registries</h4>
<p>For artifacts that are not container images, <strong>JFrog
Artifactory</strong> is the market veteran — multi-format (Docker,
Maven, npm, NuGet, PyPI, RPM), expensive but robust. <strong>Sonatype
Nexus</strong> covers similar ground, with a free open-source
edition. <strong>GitHub Packages</strong> and <strong>GitLab Package
Registry</strong> come natively integrated into their respective
platforms. And <strong>Cloudsmith</strong> is a dedicated multi-format
SaaS option.</p>
<h4>1.3 Helm Charts</h4>
<p>Starting with Helm 3, native OCI support means any
common OCI registry (ECR, GHCR, Harbor) can already store a Helm
chart directly, without dedicated infrastructure.
<code>ChartMuseum</code> still exists for whoever keeps a legacy setup.</p>

<h3>2. Essential patterns</h3>
<div class="mermaid">
flowchart LR
    Build["Build"] --> Sign["Sign with cosign/notation"]
    Sign --> Push["Push by digest"]
    Push --> Pull["Deploy pulls digest"]
</div>

<h4>2.1 Immutable tags</h4>
<p>Use the commit SHA or a semver version as the tag — never
<code>latest</code>, <code>main</code>, <code>dev</code>, or any
"moving" tag that can point at different content tomorrow without
warning:</p>
<pre><code># Bom
ghcr.io/empresa/app:v1.4.2
ghcr.io/empresa/app:abc1234   # commit SHA
ghcr.io/empresa/app@sha256:f0a1b2...   # digest absoluto

# Ruim em prod
ghcr.io/empresa/app:latest
ghcr.io/empresa/app:dev</code></pre>
<p>Referencing by digest (<code>sha256:...</code>) is the gold standard:
that identifier is immutable and unique by definition, even if someone
republishes the SAME tag with different content later. Enabling
<strong>tag immutability</strong> on the registry (available in ECR,
Harbor, ACR) reinforces this structurally — the tag simply cannot
be overwritten, even by accident.</p>
<h4>2.2 Signing with Cosign (Sigstore)</h4>
<p>Without a signature, an attacker who compromises the registry can swap the
image for a malicious one without anyone noticing — name and tag
stay the same, only the content changed. Cosign closes that gap:</p>
<pre><code>$ cosign sign --yes ghcr.io/empresa/app:v1.4.2
Generating ephemeral keys... [OIDC: 'ci@empresa.com']
tlog entry written: rekor.sigstore.dev

$ cosign verify ghcr.io/empresa/app:v1.4.2 \\
    --certificate-identity ci@empresa.com \\
    --certificate-oidc-issuer https://token.actions.githubusercontent.com
Verification for ghcr.io/empresa/app:v1.4.2 --
The following checks were performed on each of these signatures:
  - Signature was verified
  - Identity matched expectation</code></pre>
<p>Combining that with a Kubernetes admission controller (Sigstore
Policy Controller, Kyverno) closes the full loop: the cluster rejects
any image without a valid signature, making verification
mandatory, not optional:</p>
<pre><code>apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-signed-images }
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-signature
      match:
        any:
          - resources: { kinds: [Pod] }
      verifyImages:
        - imageReferences: ['ghcr.io/empresa/*']
          attestors:
            - keyless:
                subject: ci@empresa.com
                issuer: https://token.actions.githubusercontent.com</code></pre>
<h4>2.3 Attached SBOM</h4>
<p>Attaching the SBOM directly as a referrer in the OCI registry itself
keeps the dependency list with the artifact it describes, instead of
in a separate document that can go stale:</p>
<pre><code>$ syft ghcr.io/empresa/app:v1.4.2 -o cyclonedx-json &gt; sbom.json
$ cosign attach sbom --sbom sbom.json ghcr.io/empresa/app:v1.4.2
$ cosign attest --predicate sbom.json --type cyclonedx \\
    ghcr.io/empresa/app:v1.4.2</code></pre>
<p>When an incident requires answering quickly "who is using
log4j 2.14?", having the SBOM attached to each specific image turns
that question from a manual investigation into a direct query.</p>
<h4>2.4 Provenance / SLSA</h4>
<p>A provenance attestation documents HOW the artifact was
built, not only what it contains — SLSA L3 or higher requires
that attestation to come from a trusted builder, not from any
arbitrary machine. GitHub Actions already has an official template to
generate this automatically:</p>
<pre><code>- uses: slsa-framework/slsa-github-generator/.github/workflows/builder_container_slsa3.yml@v1.10.0</code></pre>
<p>The result is the image accompanied by a verifiable
<code>provenance.intoto.jsonl</code>, proving exactly where
it came from.</p>

<h3>3. RBAC and segregation</h3>
<p>Five access-control practices separate a well-governed registry
from one at risk. Write (push) should be restricted
exclusively to CI — no developer pushes directly, ideally using
short-lived OIDC tokens instead of static credentials.
Read should be scoped by team or product, with multi-tenant
environments using a separate namespace per team. In production, pulls
should use a cluster-specific pull-secret, never a
reused human credential. Short-lived OIDC+STS tokens
are preferable to static tokens whenever feasible. And a registry audit
log — who pulled what and when — becomes essential in the middle of any
incident investigation.</p>

<h3>4. Retention and cost</h3>
<p>Without a retention policy, a registry silently accumulates gigabyte after
gigabyte: every PR generates its own test image, and
old builds accumulate new CVEs every week that passes, even with
nobody touching them — storage cost scales with that
accumulation:</p>
<pre><code># Exemplo ECR lifecycle
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
<p>Beyond cutting the bill, that cleanup reduces the attack
surface: an old image forgotten in the registry, with a known
vulnerability, is exactly the easy target an attacker looks for
before trying something more sophisticated.</p>

<h3>5. Pull-through cache</h3>
<p>Having every pipeline run pull straight from Docker Hub quickly hits
the generous-but-finite free-plan rate limit — the
alternative is using the internal registry as an intermediate cache
layer via Harbor proxy cache, ECR pull-through (configurable
for Docker Hub, Quay, GHCR), or an Artifactory remote repository.
That speeds builds with a local cache, keeps the pipeline working
even during upstream registry outages, produces
audit of what actually comes from outside, and opens room for
scanning or quarantine before any external image is actually
used.</p>

<h3>6. Continuous vulnerability scanning</h3>
<p>Scanning only at push time is inherently insufficient —
a new CVE can be discovered weeks later in an image that was already
clean when published. The answer is configuring periodic re-scan
(Harbor scheduling, Trivy Operator on Kubernetes, ECR
Enhanced Scanning), automatic notification when an image already in
production becomes considered vulnerable (webhook firing to
Slack), and an admission policy that actively blocks any
image with a critical CVE from running in production, even if it was
approved in the past.</p>

<h3>7. Multi-arch images</h3>
<p>With ARM (Graviton on AWS, Apple Silicon locally) coexisting with
AMD64 day to day, the build needs to produce both architectures at
once:</p>
<pre><code>docker buildx build --platform linux/amd64,linux/arm64 \\
  --tag ghcr.io/empresa/app:v1.4.2 \\
  --push .</code></pre>
<p>The result is a manifest list — a single reference that points
at both architecture variants at once — and the pull
automatically selects the correct architecture for the machine that is
pulling, with no extra client-side configuration.</p>

<h3>8. Anti-patterns</h3>
<figure class="lesson-figure">
  <div class="lesson-viz lesson-viz--steps">
    <div class="lesson-viz-step"><span>1</span><p>Images always by digest, not mutable tag</p></div>
    <div class="lesson-viz-step"><span>2</span><p>Signature + admission policy</p></div>
    <div class="lesson-viz-step"><span>3</span><p>Continuous scanning in the registry</p></div>
    <div class="lesson-viz-step"><span>4</span><p>Segregate prod vs non-prod</p></div>
  </div>
  <figcaption>SolarWinds lessons applied to artifacts.</figcaption>
</figure>

<ul>
<li><strong>Using only <code>latest</code> in production</strong>: zero
traceability of which code is actually running (section 2.1).</li>
<li><strong>No retention policy</strong>: gigabytes accumulating
uncontrolled (section 4).</li>
<li><strong>Push without signing</strong>: leaves the supply chain
vulnerable to silent image swaps (section 2.2).</li>
<li><strong>Static registry tokens</strong>: if leaked, the attacker
can pull everything with no time limit.</li>
<li><strong>Images published to a public registry without scan or
audit</strong>: anyone can pull unverified code.</li>
<li><strong>Rebuild straight in production</strong>: "I just recompiled there"
produces an artifact literally different from what passed
tests.</li>
<li><strong>Not using a pull-through cache</strong>: rate limits at
peak hours stall the entire CI without warning (section 5).</li>
</ul>

<h3>9. Real case: SolarWinds (2020)</h3>
<p>Attackers compromised SolarWinds' BUILD pipeline directly,
injecting malicious code into the Orion product BEFORE the
signing step happened — meaning the "official" signed
image already left the factory compromised. Hundreds of companies,
including US government agencies, downloaded that
"official" backdoored version, trusting exactly the signature that
should have guaranteed integrity. The central lesson: signing is not enough if the
build PROCESS itself is untrusted — hence the requirement for SLSA level
3 or higher (section 2.4), which validates the build chain, not only the
final artifact. Ideally, a reproducible build (the same input always
produces exactly the same output) lets multiple independent parties
verify the result without blindly trusting a single build
infrastructure.</p>""",
                "practical": (
                    "<p><strong>Exercício prático completo</strong>:</p>"
                    "<ol>"
                    "<li>Suba imagem para GHCR com tag por commit SHA + tag semver.</li>"
                    "<li>Habilite immutability nas tags.</li>"
                    "<li>Gere SBOM com <code>syft</code>; anexe como referrer com Cosign.</li>"
                    "<li>Assine imagem com <code>cosign sign</code> (keyless OIDC do GitHub).</li>"
                    "<li>Verifique com <code>cosign verify</code> contra OIDC issuer.</li>"
                    "<li>Configure Trivy operator (ou rescan periódico) no Harbor/ECR.</li>"
                    "<li>Configure retenção: manter 30 versões semver + apagar untagged "
                    "após 7d.</li>"
                    "<li>Em K8s local (kind), instale Sigstore Policy Controller que "
                    "rejeita imagens não assinadas.</li>"
                    "<li>Bonus: gere atestado SLSA L3 com <code>slsa-github-generator</code>.</li>"
                    "<li>Bonus 2: build multi-arch (amd64 + arm64) e teste em ambos.</li>"
                    "</ol>"
                ),
                "practical_en": (
                    "<p><strong>Full hands-on exercise</strong>:</p>"
                    "<ol>"
                    "<li>Push an image to GHCR with a commit-SHA tag + a semver tag.</li>"
                    "<li>Enable tag immutability.</li>"
                    "<li>Generate an SBOM with <code>syft</code>; attach it as a referrer with Cosign.</li>"
                    "<li>Sign the image with <code>cosign sign</code> (GitHub keyless OIDC).</li>"
                    "<li>Verify with <code>cosign verify</code> against the OIDC issuer.</li>"
                    "<li>Configure the Trivy operator (or periodic rescan) on Harbor/ECR.</li>"
                    "<li>Configure retention: keep 30 semver versions + delete untagged "
                    "after 7d.</li>"
                    "<li>On local K8s (kind), install Sigstore Policy Controller that "
                    "rejects unsigned images.</li>"
                    "<li>Bonus: generate an SLSA L3 attestation with <code>slsa-github-generator</code>.</li>"
                    "<li>Bonus 2: multi-arch build (amd64 + arm64) and test on both.</li>"
                    "</ol>"
                ),
            },
            "materials": [
                m("Sigstore Cosign", "https://docs.sigstore.dev/cosign/overview/", "tool", "",
                  title_en="Sigstore Cosign", description_en=""),
                m("Harbor", "https://goharbor.io/docs/", "tool", "",
                  title_en="Harbor", description_en=""),
                m("GitHub Container Registry", "https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry", "docs", "",
                  title_en="GitHub Container Registry", description_en=""),
                m("Artifactory docs", "https://jfrog.com/help/r/jfrog-artifactory-documentation", "docs", "",
                  title_en="Artifactory docs", description_en=""),
                m("OCI image spec", "https://github.com/opencontainers/image-spec", "docs", "",
                  title_en="OCI image spec", description_en=""),
                m("SLSA framework", "https://slsa.dev/", "docs", "Níveis de provenance para supply chain.",
                  title_en="SLSA framework", description_en="Provenance levels for the supply chain."),
            ],
            "questions": [
                q("Por que usar registry privado?",
                  "Controle de acesso, rastreabilidade e independência de fornecedor público.",
                  ["Costuma ficar bem mais lento para fazer o pull dentro do pipeline de CI, com frequência.",
                   "Sai de graça na grande maioria dos planos gratuitos disponíveis hoje em dia.",
                   "Faz basicamente o mesmo papel que o próprio IAM sozinho já deveria cobrir."],
                  "Também evita rate-limit (Docker Hub) e dá auditoria fina.",
                  statement_en="Why use a private registry?",
                  correct_en="Access control, traceability, and independence from public vendors.",
                  wrong_en=["It often makes pulls inside the CI pipeline much slower.",
                            "It is free on most free plans available today.",
                            "It basically does the same job IAM alone should already cover."],
                  explanation_en="Also avoids rate limits (Docker Hub) and gives fine-grained audit."),
                q("Tag mutável (latest) é problema porque:",
                  "Não há rastreabilidade, pode mudar a qualquer hora.",
                  ["Deixa o pull mais lento por causa do cache do registry.",
                   "Aumenta o custo de armazenamento guardado no registry.",
                   "Só funciona direito em ambiente rodando Linux."],
                  "Em rollback, você não consegue voltar para 'qual latest era ontem?'.",
                  statement_en="A mutable tag (latest) is a problem because:",
                  correct_en="There is no traceability — it can change at any time.",
                  wrong_en=["It makes pulls slower because of registry cache.",
                            "It increases storage cost in the registry.",
                            "It only works properly in Linux environments."],
                  explanation_en="On rollback, you cannot go back to 'which latest was yesterday?'."),
                q("Cosign serve para:",
                  "Assinar e verificar artefatos OCI.",
                  ["Comprimir o tamanho final da imagem antes do push.",
                   "Substituir por completo o registry usado no pipeline.",
                   "Compilar projeto Java dentro do processo de build."],
                  "Combinado com policy controllers (Kyverno, Connaisseur), bloqueia imagens não assinadas.",
                  statement_en="Cosign is used to:",
                  correct_en="Sign and verify OCI artifacts.",
                  wrong_en=["Compress the final image size before push.",
                            "Fully replace the registry used in the pipeline.",
                            "Compile a Java project inside the build process."],
                  explanation_en="Combined with policy controllers (Kyverno, Connaisseur), it blocks unsigned images."),
                q("Retenção de artefatos serve para:",
                  "Reduzir custos e poluição mantendo só o necessário.",
                  ["Aumentar a redundância de cópias guardadas do artefato.",
                   "Substituir o processo de backup usado pela equipe.",
                   "Melhorar o resultado do lint rodado no pipeline."],
                  "Configure regras: 'manter últimas 50 tags + todas semver'.",
                  statement_en="Artifact retention is used to:",
                  correct_en="Cut costs and clutter by keeping only what is needed.",
                  wrong_en=["Increase redundancy of stored artifact copies.",
                            "Replace the backup process used by the team.",
                            "Improve lint results run in the pipeline."],
                  explanation_en="Configure rules: 'keep last 50 tags + all semver'."),
                q("OCI é:",
                  "Padrão aberto para imagens de container.",
                  ["Uma ferramenta específica de gestão de IAM.",
                   "Um backend usado para centralizar logs da aplicação.",
                   "Uma linguagem de programação para escrever backend."],
                  "Open Container Initiative. Garante que imagem buildada pelo Docker roda no Podman, K8s etc.",
                  statement_en="OCI is:",
                  correct_en="An open standard for container images.",
                  wrong_en=["A specific IAM management tool.",
                            "A backend used to centralize application logs.",
                            "A programming language for writing backends."],
                  explanation_en="Open Container Initiative. Ensures an image built by Docker runs on Podman, K8s, etc."),
                q("Registry como pull-through cache:",
                  "Faz cache local de imagens públicas, evitando rate-limits.",
                  ["Acelera o tempo de commit feito diretamente no repositório de código.",
                   "Substitui inteiramente o pipeline de CI usado para buildar a imagem.",
                   "Funciona como cache de resolução de DNS usado pelo cluster."],
                  "Especialmente útil para imagens base (alpine, debian, python).",
                  statement_en="A registry as pull-through cache:",
                  correct_en="Caches public images locally, avoiding rate limits.",
                  wrong_en=["Speeds up commits made directly to the code repository.",
                            "Fully replaces the CI pipeline used to build the image.",
                            "Acts as a DNS resolution cache used by the cluster."],
                  explanation_en="Especially useful for base images (alpine, debian, python)."),
                q("RBAC em registry:",
                  "Controla quem pode ler/escrever em quais repositórios.",
                  ["Aumenta o tamanho final da imagem guardada no registry.",
                   "Acelera o scan de vulnerabilidade rodado no push.",
                   "Substitui a necessidade de usar TLS na conexão."],
                  "Só CI faz push; devs leem; produção usa pull-secret específico.",
                  statement_en="RBAC on a registry:",
                  correct_en="Controls who can read/write which repositories.",
                  wrong_en=["Increases the final size of the image stored in the registry.",
                            "Speeds up vulnerability scanning run on push.",
                            "Replaces the need to use TLS on the connection."],
                  explanation_en="Only CI pushes; developers read; production uses a specific pull-secret."),
                q("Vulnerability scanning no registry:",
                  "Avisa quando uma imagem fica insegura mesmo após o push.",
                  ["Só verifica vulnerabilidade no exato momento em que ocorre o push.",
                   "Substitui completamente a etapa de SCA rodada no pipeline.",
                   "Substitui completamente a etapa de SAST rodada no código."],
                  "Re-scan periódico cobre CVEs publicadas posteriormente.",
                  statement_en="Vulnerability scanning in the registry:",
                  correct_en="Warns when an image becomes unsafe even after push.",
                  wrong_en=["Only checks vulnerabilities at the exact moment of push.",
                            "Fully replaces the SCA stage run in the pipeline.",
                            "Fully replaces the SAST stage run on code."],
                  explanation_en="Periodic re-scan covers CVEs published later."),
                q("Imagem 'untagged' é:",
                  "Geralmente lixo de builds antigos, limpar com retenção.",
                  ["Pode parecer mais segura só por não ter tag visível.",
                   "Ocupa menos espaço por padrão no armazenamento do registry.",
                   "Não é garantia de ser a versão boa mais recente."],
                  "Imagem perdeu a tag em rebuild; sem política, fica ocupando espaço.",
                  statement_en="An 'untagged' image is:",
                  correct_en="Usually leftover from old builds — clean with retention.",
                  wrong_en=["Seemingly safer just because it has no visible tag.",
                            "Occupying less space by default in registry storage.",
                            "Not a guarantee it is the good latest version."],
                  explanation_en="The image lost its tag on rebuild; without a policy it keeps consuming space."),
                q("Provenance (SLSA) é:",
                  "Atestado de como o artefato foi construído (origem, build).",
                  ["Um tipo específico de tag usada só para marcar a versão do build.",
                   "Uma forma de backup guardada fora do registry principal, redundante.",
                   "Só mais uma camada de RBAC aplicada em cima do repositório."],
                  "SLSA tem níveis 1-4. L3+ exige builder confiável (sem injeção do dev).",
                  statement_en="Provenance (SLSA) is:",
                  correct_en="An attestation of how the artifact was built (origin, build).",
                  wrong_en=["A specific tag type used only to mark the build version.",
                            "A redundant backup stored outside the main registry.",
                            "Just another RBAC layer on top of the repository."],
                  explanation_en="SLSA has levels 1–4. L3+ requires a trusted builder (no developer injection)."),
            ],
        },
    ],
}
