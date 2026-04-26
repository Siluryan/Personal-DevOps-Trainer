"""Fase 3, Automação e Ciclo de Vida (DevOps & IaC)."""
from ._helpers import m, q

PHASE3 = {
    "name": "Fase 3: Automação e Ciclo de Vida (DevOps & IaC)",
    "description": "Parar de configurar as coisas manualmente e usar código.",
    "topics": [
        # =====================================================================
        # 3.1 Versionamento com Git
        # =====================================================================
        {
            "title": "Versionamento com Git",
            "summary": "Fluxos de trabalho seguros (Gitflow) e proteção de branches.",
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
                "body": (
                    "<h3>1. Modelo mental: o que Git realmente armazena</h3>"
                    "<p>A primeira coisa a entender: Git não armazena <em>diferenças</em> "
                    "(como SVN), ele armazena <em>snapshots</em>. Cada commit é um objeto "
                    "imutável que aponta para uma <em>tree</em> (estado de toda a árvore "
                    "de arquivos), o(s) commit(s) pai(s), autor, mensagem, timestamp. Tudo "
                    "isso é endereçado por um hash SHA-1 (ou SHA-256 em repos modernos). "
                    "Esse hash é determinístico: mesmo conteúdo + mesmo pai + mesmo autor "
                    "gera mesmo hash.</p>"
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
            },
            "materials": [
                m("Pro Git Book", "https://git-scm.com/book/en/v2", "book", "A referência."),
                m("Atlassian Gitflow", "https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow", "article", ""),
                m("GitHub Branch Protection", "https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches", "docs", ""),
                m("Trunk Based Development", "https://trunkbaseddevelopment.com/", "article", ""),
                m("Conventional Commits", "https://www.conventionalcommits.org/", "article", ""),
                m("Oh Shit, Git!?!", "https://ohshitgit.com/", "article",
                  "Receitas para sair de roubadas comuns."),
            ],
            "questions": [
                q("`git rebase` faz:",
                  "Reaplica commits sobre outra base reescrevendo histórico.",
                  ["Sincroniza com remoto.", "Apaga branch.", "Faz merge sem reescrever."],
                  "Rebase gera novos hashes; não use em história já compartilhada."),
                q("Por que evitar force push em main?",
                  "Pode reescrever história compartilhada e quebrar o time.",
                  ["É ilegal.", "É lento.", "Não funciona em GitHub."],
                  "Qualquer dev com a história anterior fica desincronizado e pode perder commits."),
                q("Signed commits servem para:",
                  "Provar autoria via GPG/SSH.",
                  ["Comprimir commits.", "Acelerar push.", "Substituir branch."],
                  "Evita spoofing, atacante consegue dizer 'commit do CTO' sem assinatura. Com GPG, GitHub mostra 'Verified'."),
                q("Em PR, o que é review obrigatório?",
                  "Regra que exige aprovação humana antes do merge.",
                  ["Bloqueia o repo.", "Pula CI.", "Conta como deploy."],
                  "Combinada com CODEOWNERS, garante que pessoas certas sejam ouvidas."),
                q("Diferença entre merge e rebase:",
                  "Merge preserva história; rebase a reescreve linearmente.",
                  ["São idênticos.", "Rebase é mais lento.", "Merge apaga commits."],
                  "Escolha conforme política do time. Misturar pode confundir o histórico."),
                q("`.gitignore` serve para:",
                  "Listar arquivos a não rastrear (ex.: .env).",
                  ["Bloquear push.", "Apagar histórico.", "Substituir LICENSE."],
                  "Para arquivos já rastreados, é preciso `git rm --cached` antes."),
                q("Trunk-based development prefere:",
                  "Branches curtas e merge frequente em main.",
                  ["Branches longas.", "Sem main.", "Apenas tags."],
                  "Reduz merge hell. Exige feature flags e suite de testes confiável."),
                q("`git stash` faz:",
                  "Salva mudanças locais pendentes para retomar depois.",
                  ["Apaga commits.", "Cria branch.", "Faz push."],
                  "Stash empilha. Use `git stash pop` para retomar; aplique a branch correta."),
                q("Conventional Commits é:",
                  "Convenção de mensagens (feat:, fix:, chore:).",
                  ["Linter de código.", "Substituto do git.", "Hash de commit."],
                  "Permite gerar changelog e versionamento automático (semver)."),
                q("Em LFS, arquivos grandes:",
                  "Ficam em storage separado, com pointer no repo.",
                  ["São compactados em zip.", "Não funcionam.", "Apagam o histórico."],
                  "Útil para mídia/binários. Repo principal continua leve; LFS é cobrado por banda."),
            ],
        },
        # =====================================================================
        # 3.2 Infraestrutura como Código (Terraform)
        # =====================================================================
        {
            "title": "Infraestrutura como Código (Terraform)",
            "summary": "Criar servidores usando arquivos de configuração versionáveis.",
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
                "body": (
                    "<h3>1. Por que IaC importa de verdade</h3>"
                    "<ul>"
                    "<li><strong>Reprodutibilidade</strong>: dev, staging, prod saem do mesmo "
                    "código. Não é 'igualzinho', é literalmente o mesmo. Bug em prod vira "
                    "reproduzível em staging em segundos.</li>"
                    "<li><strong>Revisão por PR</strong>: mudança em VPC passa pelo mesmo "
                    "fluxo de revisão de código de aplicação. Você lê o diff, comenta, "
                    "aprova.</li>"
                    "<li><strong>Rastreabilidade</strong>: <code>git blame</code> em "
                    "<code>main.tf</code> mostra quem mudou aquele bucket S3 e por quê. "
                    "Auditoria fica trivial.</li>"
                    "<li><strong>Disaster recovery</strong>: cluster inteiro destruído? "
                    "<code>terraform apply</code> reconstrói tudo. Empresas testam isso em "
                    "Game Days.</li>"
                    "<li><strong>Compliance</strong>: políticas como 'todo bucket deve ter "
                    "encryption' viram regra (Sentinel, OPA, tfsec).</li>"
                    "</ul>"

                    "<h3>2. Anatomia do Terraform</h3>"
                    "<p>Terraform usa HCL (HashiCorp Configuration Language), uma DSL "
                    "declarativa, JSON-like, mais legível.</p>"
                    "<pre><code># main.tf\n"
                    "terraform {\n"
                    "  required_version = \"&gt;= 1.6.0\"\n"
                    "  required_providers {\n"
                    "    aws = { source = \"hashicorp/aws\", version = \"~&gt; 5.40\" }\n"
                    "  }\n"
                    "  backend \"s3\" {\n"
                    "    bucket         = \"empresa-tfstate-prod\"\n"
                    "    key            = \"network/main.tfstate\"\n"
                    "    region         = \"us-east-1\"\n"
                    "    dynamodb_table = \"tfstate-lock\"\n"
                    "    encrypt        = true\n"
                    "  }\n"
                    "}\n"
                    "\n"
                    "provider \"aws\" {\n"
                    "  region = var.region\n"
                    "  default_tags {\n"
                    "    tags = {\n"
                    "      Owner       = \"platform-team\"\n"
                    "      Environment = var.env\n"
                    "      ManagedBy   = \"terraform\"\n"
                    "    }\n"
                    "  }\n"
                    "}\n"
                    "\n"
                    "variable \"env\"    { type = string }\n"
                    "variable \"region\" { type = string, default = \"us-east-1\" }\n"
                    "\n"
                    "resource \"aws_s3_bucket\" \"app_data\" {\n"
                    "  bucket = \"empresa-app-${var.env}-${random_id.suffix.hex}\"\n"
                    "}\n"
                    "\n"
                    "resource \"aws_s3_bucket_versioning\" \"app_data\" {\n"
                    "  bucket = aws_s3_bucket.app_data.id\n"
                    "  versioning_configuration { status = \"Enabled\" }\n"
                    "}\n"
                    "\n"
                    "resource \"aws_s3_bucket_server_side_encryption_configuration\" \"app_data\" {\n"
                    "  bucket = aws_s3_bucket.app_data.id\n"
                    "  rule {\n"
                    "    apply_server_side_encryption_by_default {\n"
                    "      sse_algorithm     = \"aws:kms\"\n"
                    "      kms_master_key_id = aws_kms_key.app.arn\n"
                    "    }\n"
                    "  }\n"
                    "}\n"
                    "\n"
                    "resource \"aws_s3_bucket_public_access_block\" \"app_data\" {\n"
                    "  bucket                  = aws_s3_bucket.app_data.id\n"
                    "  block_public_acls       = true\n"
                    "  block_public_policy     = true\n"
                    "  ignore_public_acls      = true\n"
                    "  restrict_public_buckets = true\n"
                    "}\n"
                    "\n"
                    "output \"bucket_name\" {\n"
                    "  value = aws_s3_bucket.app_data.id\n"
                    "}</code></pre>"
                    "<p>Conceitos:</p>"
                    "<ul>"
                    "<li><strong>Provider</strong>: plugin que conhece a API (aws, azurerm, "
                    "google, kubernetes, github, cloudflare, datadog...).</li>"
                    "<li><strong>Resource</strong>: 'eu quero um bucket S3 chamado X'. "
                    "Terraform vai criar, atualizar ou destruir conforme diferença com state.</li>"
                    "<li><strong>Data source</strong>: lê algo existente sem gerenciar "
                    "(<code>data \"aws_ami\" \"ubuntu\"</code>).</li>"
                    "<li><strong>Variable</strong>: parâmetro de entrada.</li>"
                    "<li><strong>Output</strong>: valor exposto após apply (útil para "
                    "remote_state em outro módulo).</li>"
                    "<li><strong>Locals</strong>: variáveis derivadas locais.</li>"
                    "</ul>"

                    "<h3>3. Workflow básico: init → plan → apply</h3>"
                    "<pre><code>$ terraform init      # baixa providers, configura backend\n"
                    "$ terraform validate  # checa sintaxe\n"
                    "$ terraform fmt -recursive  # formata\n"
                    "$ terraform plan -out=tfplan\n"
                    "Plan: 4 to add, 1 to change, 0 to destroy.\n"
                    "$ terraform apply tfplan</code></pre>"
                    "<p><strong>Plan</strong> é fundamental: gera diff explícito entre "
                    "estado atual e desejado. <em>Sempre</em> leia o plan antes de aplicar. "
                    "Em CI, faça plan no PR e exija comentário com o output (ferramenta "
                    "Atlantis automatiza).</p>"
                    "<p>Comandos úteis:</p>"
                    "<pre><code>terraform plan -target=aws_s3_bucket.app_data   # foco\n"
                    "terraform apply -refresh-only                    # só atualiza state\n"
                    "terraform destroy -target=aws_instance.test       # destruição cirúrgica\n"
                    "terraform state list\n"
                    "terraform state show aws_s3_bucket.app_data\n"
                    "terraform import aws_s3_bucket.legacy bucket-name\n"
                    "terraform graph | dot -Tpng &gt; deps.png\n"
                    "terraform console   # REPL para testar expressões</code></pre>"

                    "<h3>4. State é crítico, trate com paranoia</h3>"
                    "<p>O <code>terraform.tfstate</code> é um JSON com mapeamento "
                    "<em>resource → ID real</em>. Sem ele, Terraform 'esquece' o que gerencia. "
                    "Pior: state contém valores sensíveis em <strong>plaintext</strong> "
                    "(senhas RDS, keys IAM). Por isso:</p>"
                    "<ul>"
                    "<li><strong>NUNCA commite tfstate</strong> em Git. Coloque em .gitignore.</li>"
                    "<li><strong>Use backend remoto</strong>: S3+DynamoDB lock (AWS), GCS "
                    "(GCP), Azure Storage (Azure), Terraform Cloud, Spacelift, Atlantis, "
                    "GitLab Terraform state.</li>"
                    "<li><strong>Habilite encryption at rest</strong> no backend (KMS/CMEK).</li>"
                    "<li><strong>Habilite versionamento</strong> no bucket, você vai precisar "
                    "(quando state for corrompido).</li>"
                    "<li><strong>State lock</strong>: DynamoDB (AWS), Cloud Storage (GCP) ou "
                    "lock interno (TFC). Evita dois apply simultâneos corrompendo state.</li>"
                    "<li><strong>Não edite state à mão</strong>. Use comandos "
                    "<code>terraform state mv|rm|replace-provider</code> ou re-import.</li>"
                    "<li><strong>Restrição de acesso</strong>: state em prod só CI deve ler. "
                    "Devs leem com role de leitura.</li>"
                    "</ul>"
                    "<p>Backend exemplo S3+DynamoDB:</p>"
                    "<pre><code>terraform {\n"
                    "  backend \"s3\" {\n"
                    "    bucket         = \"empresa-tfstate\"\n"
                    "    key            = \"prod/network.tfstate\"\n"
                    "    region         = \"us-east-1\"\n"
                    "    dynamodb_table = \"tfstate-lock\"\n"
                    "    encrypt        = true\n"
                    "    kms_key_id     = \"arn:aws:kms:us-east-1:111:key/xxx\"\n"
                    "  }\n"
                    "}</code></pre>"

                    "<h3>5. Módulos: reuso sem copiar-colar</h3>"
                    "<p>Módulo é uma pasta com inputs (variables), recursos e outputs. "
                    "Use módulos para encapsular padrões da empresa:</p>"
                    "<pre><code>modules/\n"
                    "  rds-postgres/\n"
                    "    main.tf       # cria RDS com encryption + backup + parameter group\n"
                    "    variables.tf  # name, allocated_storage, instance_class, vpc_id...\n"
                    "    outputs.tf    # endpoint, port, secret_arn\n"
                    "    README.md     # como usar</code></pre>"
                    "<p>Uso em outro lugar:</p>"
                    "<pre><code>module \"app_db\" {\n"
                    "  source  = \"git::https://github.com/empresa/tf-modules.git//rds-postgres?ref=v1.4.0\"\n"
                    "  name    = \"app-prod\"\n"
                    "  vpc_id  = data.aws_vpc.main.id\n"
                    "  size    = \"db.r5.large\"\n"
                    "}\n"
                    "\n"
                    "output \"db_endpoint\" {\n"
                    "  value = module.app_db.endpoint\n"
                    "}</code></pre>"
                    "<p>Boas práticas para módulos:</p>"
                    "<ul>"
                    "<li>Versione com Git tags semver (<code>v1.0.0</code>, <code>v1.4.0</code>).</li>"
                    "<li>Mantenha módulo pequeno e composável (não 'megamódulo' que faz tudo).</li>"
                    "<li>README com exemplo de uso e tabela de inputs/outputs.</li>"
                    "<li><code>terraform-docs</code> gera documentação automática.</li>"
                    "<li>Teste com <code>terratest</code> ou <code>kitchen-terraform</code>.</li>"
                    "</ul>"

                    "<h3>6. Variáveis, locals e data sources</h3>"
                    "<pre><code>variable \"env\" {\n"
                    "  type        = string\n"
                    "  description = \"Ambiente (dev/staging/prod)\"\n"
                    "  validation {\n"
                    "    condition     = contains([\"dev\", \"staging\", \"prod\"], var.env)\n"
                    "    error_message = \"env deve ser dev, staging ou prod.\"\n"
                    "  }\n"
                    "}\n"
                    "\n"
                    "variable \"db_password\" {\n"
                    "  type      = string\n"
                    "  sensitive = true   # esconde de outputs/logs\n"
                    "}\n"
                    "\n"
                    "locals {\n"
                    "  is_prod   = var.env == \"prod\"\n"
                    "  instance  = local.is_prod ? \"db.r5.large\" : \"db.t3.medium\"\n"
                    "  multi_az  = local.is_prod\n"
                    "  tags = merge(\n"
                    "    var.tags,\n"
                    "    { Env = var.env, ManagedBy = \"terraform\" }\n"
                    "  )\n"
                    "}\n"
                    "\n"
                    "data \"aws_ami\" \"ubuntu\" {\n"
                    "  most_recent = true\n"
                    "  owners      = [\"099720109477\"]   # Canonical\n"
                    "  filter {\n"
                    "    name   = \"name\"\n"
                    "    values = [\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\"]\n"
                    "  }\n"
                    "}</code></pre>"

                    "<h3>7. Drift: realidade ≠ código</h3>"
                    "<p>Drift acontece quando alguém muda algo manualmente no console. "
                    "Detectar:</p>"
                    "<pre><code>$ terraform plan\n"
                    "# aws_security_group.web has been changed\n"
                    "  ~ ingress {\n"
                    "      - cidr_blocks = [\"10.0.0.0/8\"]   # removido manualmente!\n"
                    "      + cidr_blocks = [\"10.0.0.0/8\", \"0.0.0.0/0\"]\n"
                    "  }</code></pre>"
                    "<p>Estratégias:</p>"
                    "<ul>"
                    "<li>CI noturno rodando <code>terraform plan</code> e alertando se "
                    "houver drift.</li>"
                    "<li>SCP/Azure Policy bloqueando mudanças manuais (read-only para devs "
                    "em prod).</li>"
                    "<li>Driftctl, AWS Config rules.</li>"
                    "</ul>"
                    "<p>Para 'oficializar' recurso criado fora do TF, use import:</p>"
                    "<pre><code># Forma clássica (CLI)\n"
                    "terraform import aws_s3_bucket.legacy meu-bucket-existente\n"
                    "\n"
                    "# Terraform 1.5+: import block declarativo\n"
                    "import {\n"
                    "  to = aws_s3_bucket.legacy\n"
                    "  id = \"meu-bucket-existente\"\n"
                    "}</code></pre>"

                    "<h3>8. Boas práticas de produção</h3>"
                    "<ul>"
                    "<li><strong>Workspaces ou diretórios separados</strong> por ambiente. "
                    "Workspaces são mais frágeis em prod (mesmo backend, prefixo de key), "
                    "muitos times preferem diretórios separados (<code>envs/dev/</code>, "
                    "<code>envs/prod/</code>) ou Terragrunt.</li>"
                    "<li><strong>Lockfile</strong>: <code>.terraform.lock.hcl</code> deve "
                    "ser commitado, fixa hashes de providers.</li>"
                    "<li><strong>Lint e security scan</strong>: <code>tflint</code>, "
                    "<code>tfsec</code>, <code>checkov</code> em CI.</li>"
                    "<li><strong>Plan no PR</strong> obrigatório. Atlantis ou GitHub Actions "
                    "comentam o output. Apply só após review e approval.</li>"
                    "<li><strong>Apply automático apenas em main</strong>, e mesmo assim "
                    "com lock e human approval em prod.</li>"
                    "<li><strong>Tags obrigatórias</strong>: Owner, Environment, CostCenter, "
                    "ManagedBy. <code>default_tags</code> no provider + Sentinel/OPA para "
                    "garantir.</li>"
                    "<li><strong>Não use count para recursos críticos</strong>, "
                    "for_each é mais seguro (chaves estáveis).</li>"
                    "<li><strong>Targeted apply é exceção</strong>, não regra. Force "
                    "deriva.</li>"
                    "</ul>"

                    "<h3>9. Pipeline de Terraform com GitHub Actions</h3>"
                    "<pre><code>name: terraform\n"
                    "on:\n"
                    "  pull_request:\n"
                    "    paths: ['envs/**', 'modules/**']\n"
                    "  push:\n"
                    "    branches: [main]\n"
                    "permissions:\n"
                    "  id-token: write   # OIDC\n"
                    "  contents: read\n"
                    "  pull-requests: write\n"
                    "jobs:\n"
                    "  plan:\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - uses: aws-actions/configure-aws-credentials@v4\n"
                    "        with:\n"
                    "          role-to-assume: arn:aws:iam::111:role/gh-actions-tf\n"
                    "          aws-region: us-east-1\n"
                    "      - uses: hashicorp/setup-terraform@v3\n"
                    "        with: { terraform_version: 1.7.5 }\n"
                    "      - run: terraform fmt -check -recursive\n"
                    "      - run: terraform init\n"
                    "      - run: terraform validate\n"
                    "      - run: tflint --recursive\n"
                    "      - run: tfsec .\n"
                    "      - run: terraform plan -out=tfplan\n"
                    "      - uses: actions/upload-artifact@v4\n"
                    "        with: { name: tfplan, path: tfplan }\n"
                    "  apply:\n"
                    "    needs: plan\n"
                    "    if: github.ref == 'refs/heads/main'\n"
                    "    environment: production   # gate manual\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - uses: aws-actions/configure-aws-credentials@v4\n"
                    "        with: { role-to-assume: ..., aws-region: us-east-1 }\n"
                    "      - uses: hashicorp/setup-terraform@v3\n"
                    "      - run: terraform init\n"
                    "      - uses: actions/download-artifact@v4\n"
                    "        with: { name: tfplan }\n"
                    "      - run: terraform apply tfplan</code></pre>"

                    "<h3>10. OpenTofu, Pulumi, CDK: alternativas</h3>"
                    "<ul>"
                    "<li><strong>OpenTofu</strong>: fork open source do Terraform após "
                    "mudança para BSL pela HashiCorp em 2023. Compatível com módulos "
                    "existentes; mantido pela Linux Foundation. Para muitos times, virou "
                    "default.</li>"
                    "<li><strong>Pulumi</strong>: IaC em Python/TypeScript/Go/etc., código "
                    "real, com loops, condicionais, classes. Trade-off: mais poder, mas "
                    "menos restrição (pode virar bagunça se mal arquitetado).</li>"
                    "<li><strong>CDK (AWS/Terraform)</strong>: AWS CDK gera CloudFormation; "
                    "CDKTF gera HCL. Boa abstração, lock-in moderado.</li>"
                    "<li><strong>Crossplane</strong>: IaC declarado como Custom Resources "
                    "do Kubernetes, bom em times K8s-first.</li>"
                    "</ul>"

                    "<h3>11. Anti-patterns comuns</h3>"
                    "<ul>"
                    "<li><strong>tfstate no Git</strong>, vazamento de senhas garantido.</li>"
                    "<li><strong>Editar console + esquecer de importar</strong>, drift "
                    "cresce até virar incidente.</li>"
                    "<li><strong>Módulo gigante 'rules-them-all'</strong>, quase impossível "
                    "de testar e debugar.</li>"
                    "<li><strong>Apply local em prod</strong>, sem revisão, sem auditoria. "
                    "Force pipeline.</li>"
                    "<li><strong>Hardcode de regiões/contas</strong>, variáveis com defaults "
                    "claros.</li>"
                    "<li><strong>Esquecer <code>sensitive = true</code></strong> em senhas.</li>"
                    "<li><strong>Provider sem version constraint</strong>, break em "
                    "deploys aleatórios.</li>"
                    "</ul>"
                ),
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
            },
            "materials": [
                m("Terraform docs", "https://developer.hashicorp.com/terraform/docs", "docs", ""),
                m("Terraform Up & Running (livro)", "https://www.terraformupandrunning.com/", "book", ""),
                m("OpenTofu", "https://opentofu.org/", "tool", "Fork open source do Terraform."),
                m("Terragrunt", "https://terragrunt.gruntwork.io/", "tool", ""),
                m("tflint", "https://github.com/terraform-linters/tflint", "tool", ""),
                m("Atlantis (Terraform PR automation)", "https://www.runatlantis.io/", "tool", ""),
            ],
            "questions": [
                q("`terraform plan` faz:",
                  "Calcula diff entre estado e desejado, sem aplicar.",
                  ["Aplica diretamente.", "Apaga estado.", "Cria backup."],
                  "Plan gera plano determinístico (que apply vai consumir). Ler atentamente evita surpresas."),
                q("Estado remoto serve para:",
                  "Compartilhar entre membros do time com lock.",
                  ["Acelerar plan.", "Substituir IAM.", "Habilitar HTTPS."],
                  "Sem state remoto, devs apagam o trabalho um do outro. Com lock, só um apply roda por vez."),
                q("Por que NÃO commitar tfstate?",
                  "Pode conter segredos e gera conflito.",
                  ["É grande demais.", "Falha o git.", "Não é permitido."],
                  "State guarda valores reais (incluindo passwords). Em git público, vira manchete instantânea."),
                q("Módulo Terraform serve para:",
                  "Encapsular e reutilizar componentes de infra.",
                  ["Gerar logs.", "Substituir provider.", "Criar VPN."],
                  "Padroniza configurações da empresa. Versione com tags Git."),
                q("`terraform import` serve para:",
                  "Trazer recurso existente para o estado.",
                  ["Aplicar plan.", "Apagar recurso.", "Renomear módulo."],
                  "Útil ao migrar de console-feito para IaC. TF 1.5+ tem `import` block declarativo."),
                q("OpenTofu é:",
                  "Fork open source do Terraform mantido pela Linux Foundation.",
                  ["Outro provider.", "Extensão de IDE.", "DSL diferente."],
                  "Criado após mudança de licença do Terraform para BSL. Compatível com módulos existentes."),
                q("Para evitar drift:",
                  "Faça plan/apply periodicamente e proíba mudanças manuais.",
                  ["Edite tfstate.", "Use só console.", "Apague o state."],
                  "Drift detection em CI noturno é boa prática. Combine com SCPs que bloqueiem mudanças manuais."),
                q("Variável sensível em Terraform:",
                  "Marque com sensitive = true.",
                  ["Coloque em comments.", "Coloque em description.", "Imprima sempre."],
                  "Evita que o valor apareça em outputs/log. Combine com TFC/Vault para evitar plaintext no state."),
                q("Provider é:",
                  "Plugin que conecta Terraform a uma API (AWS, GCP, etc.).",
                  ["Tipo de variável.", "Backend de estado.", "Hash de plan."],
                  "Existem providers oficiais e da comunidade (Cloudflare, GitHub, K8s, Datadog...)."),
                q("Lock em backend remoto evita:",
                  "Dois apply simultâneos corrompendo estado.",
                  ["Backups.", "Custos.", "Importação."],
                  "S3+DynamoDB usa item lock; TFC usa lock interno. Sem isso, race condition no state."),
            ],
        },
        # =====================================================================
        # 3.3 Gestão de Configuração (Ansible)
        # =====================================================================
        {
            "title": "Gestão de Configuração (Ansible)",
            "summary": "Padronizar o que acontece dentro do servidor automaticamente.",
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
                "body": (
                    "<h3>1. Ansible vs alternativas</h3>"
                    "<table>"
                    "<tr><th>Ferramenta</th><th>Modelo</th><th>Linguagem</th><th>Notas</th></tr>"
                    "<tr><td>Ansible</td><td>Agentless (SSH/WinRM)</td><td>YAML</td><td>Padrão de fato hoje. Curva suave.</td></tr>"
                    "<tr><td>Chef</td><td>Agente</td><td>Ruby DSL</td><td>Poderoso, complexo. Mais raro hoje.</td></tr>"
                    "<tr><td>Puppet</td><td>Agente</td><td>DSL própria</td><td>Forte em ambientes regulados/grandes.</td></tr>"
                    "<tr><td>Salt</td><td>Agente ou agentless</td><td>YAML/Jinja</td><td>Bom em escala (event-driven).</td></tr>"
                    "</table>"
                    "<p>Ansible ganhou por: zero footprint no host, YAML legível, "
                    "comunidade gigante (Galaxy), integração com cloud nativa.</p>"

                    "<h3>2. Anatomia: inventário, playbooks, módulos, roles</h3>"
                    "<h4>2.1 Inventário</h4>"
                    "<p>Lista de hosts gerenciados. Estático ou dinâmico:</p>"
                    "<pre><code># inventory.ini\n"
                    "[web]\n"
                    "web1.example.com\n"
                    "web2.example.com\n"
                    "\n"
                    "[db]\n"
                    "db1.example.com ansible_user=admin\n"
                    "\n"
                    "[prod:children]\n"
                    "web\n"
                    "db\n"
                    "\n"
                    "[prod:vars]\n"
                    "env=production</code></pre>"
                    "<p>Inventário dinâmico (essencial em cloud): plugin que consulta AWS, "
                    "GCP, Azure, GCP, etc. Em vez de manter lista de IPs (que muda com "
                    "auto-scaling), o inventário é gerado em tempo real.</p>"
                    "<pre><code># aws_ec2.yml\n"
                    "plugin: amazon.aws.aws_ec2\n"
                    "regions: [us-east-1]\n"
                    "filters:\n"
                    "  tag:Environment: production\n"
                    "  instance-state-name: running\n"
                    "keyed_groups:\n"
                    "  - key: tags.Role\n"
                    "    prefix: role</code></pre>"
                    "<h4>2.2 Playbook</h4>"
                    "<p>YAML que descreve plays e tasks:</p>"
                    "<pre><code>---\n"
                    "- name: Provisionar servidor web\n"
                    "  hosts: web\n"
                    "  become: yes\n"
                    "  vars:\n"
                    "    nginx_port: 80\n"
                    "  tasks:\n"
                    "    - name: Atualiza apt cache\n"
                    "      ansible.builtin.apt:\n"
                    "        update_cache: yes\n"
                    "        cache_valid_time: 3600\n"
                    "\n"
                    "    - name: Instala nginx\n"
                    "      ansible.builtin.apt:\n"
                    "        name: nginx\n"
                    "        state: present\n"
                    "\n"
                    "    - name: Configura site\n"
                    "      ansible.builtin.template:\n"
                    "        src: nginx.conf.j2\n"
                    "        dest: /etc/nginx/sites-available/app\n"
                    "        owner: root\n"
                    "        group: root\n"
                    "        mode: '0644'\n"
                    "      notify: reload nginx\n"
                    "\n"
                    "    - name: Habilita site\n"
                    "      ansible.builtin.file:\n"
                    "        src: /etc/nginx/sites-available/app\n"
                    "        dest: /etc/nginx/sites-enabled/app\n"
                    "        state: link\n"
                    "      notify: reload nginx\n"
                    "\n"
                    "    - name: Garante nginx ativo\n"
                    "      ansible.builtin.systemd:\n"
                    "        name: nginx\n"
                    "        state: started\n"
                    "        enabled: yes\n"
                    "\n"
                    "  handlers:\n"
                    "    - name: reload nginx\n"
                    "      ansible.builtin.systemd:\n"
                    "        name: nginx\n"
                    "        state: reloaded</code></pre>"
                    "<p><code>notify</code> + <code>handlers</code>: padrão clássico para "
                    "'recarrega só se alguma coisa mudou'. Roda 1x ao final do play, "
                    "mesmo que vários tasks notifiquem.</p>"
                    "<h4>2.3 Módulos</h4>"
                    "<p>Cada task usa um <em>módulo</em>: <code>apt</code>, <code>yum</code>, "
                    "<code>copy</code>, <code>template</code>, <code>file</code>, "
                    "<code>lineinfile</code>, <code>blockinfile</code>, <code>systemd</code>, "
                    "<code>user</code>, <code>cron</code>, <code>uri</code>, "
                    "<code>postgresql_db</code>, <code>community.docker.docker_container</code>. "
                    "São idempotentes, chamadas repetidas convergem para o estado desejado.</p>"
                    "<h4>2.4 Roles</h4>"
                    "<p>Role é estrutura padrão para reuso:</p>"
                    "<pre><code>roles/\n"
                    "  webserver/\n"
                    "    tasks/main.yml\n"
                    "    handlers/main.yml\n"
                    "    templates/nginx.conf.j2\n"
                    "    files/index.html\n"
                    "    vars/main.yml\n"
                    "    defaults/main.yml   # valores padrão (override-friendly)\n"
                    "    meta/main.yml       # dependências, autor</code></pre>"
                    "<p>Uso:</p>"
                    "<pre><code>- hosts: web\n"
                    "  roles:\n"
                    "    - role: common\n"
                    "    - role: webserver\n"
                    "      vars:\n"
                    "        nginx_port: 8080</code></pre>"

                    "<h3>3. Idempotência: o coração do Ansible</h3>"
                    "<p>Idempotência = aplicar a mesma configuração N vezes resulta no mesmo "
                    "estado. Crítico para:</p>"
                    "<ul>"
                    "<li>Convergência: rode em servidor já configurado, nada quebra.</li>"
                    "<li>CI: dry-run repetido não causa drift.</li>"
                    "<li>Self-healing: agente periódico mantém estado.</li>"
                    "</ul>"
                    "<p>Módulos nativos do Ansible são geralmente idempotentes:</p>"
                    "<pre><code># 1ª vez: instala. Demais: 'ok' (não muda nada)\n"
                    "- ansible.builtin.apt:\n"
                    "    name: nginx\n"
                    "    state: present\n"
                    "\n"
                    "# Insere linha SE não existir; idempotente\n"
                    "- ansible.builtin.lineinfile:\n"
                    "    path: /etc/sysctl.conf\n"
                    "    line: 'net.ipv4.ip_forward = 1'\n"
                    "    regexp: '^net.ipv4.ip_forward'</code></pre>"
                    "<p>Quando precisar do <code>shell</code>/<code>command</code>, use "
                    "<code>creates</code>, <code>removes</code> ou <code>changed_when</code>:</p>"
                    "<pre><code>- ansible.builtin.shell: |\n"
                    "    /opt/setup.sh &amp;&amp; touch /var/lib/setup.done\n"
                    "  args:\n"
                    "    creates: /var/lib/setup.done   # só roda se arquivo não existir\n"
                    "\n"
                    "- ansible.builtin.command: my-tool status\n"
                    "  register: result\n"
                    "  changed_when: \"'CHANGED' in result.stdout\"\n"
                    "  failed_when: result.rc &gt; 1</code></pre>"

                    "<h3>4. Variáveis: precedência e secrets</h3>"
                    "<p>Ordem de precedência (parcial, do menor ao maior):</p>"
                    "<ol>"
                    "<li>role defaults (<code>defaults/main.yml</code>)</li>"
                    "<li>inventory vars (group_vars / host_vars)</li>"
                    "<li>play vars</li>"
                    "<li>task vars</li>"
                    "<li><code>--extra-vars</code> (CLI)</li>"
                    "</ol>"
                    "<p>Para segredos, há <strong>Ansible Vault</strong>:</p>"
                    "<pre><code>$ ansible-vault create group_vars/prod/secrets.yml\n"
                    "Vault password: ****\n"
                    "$ # editor abre, você escreve em texto, ele criptografa\n"
                    "$ cat group_vars/prod/secrets.yml\n"
                    "$ANSIBLE_VAULT;1.1;AES256\n"
                    "323435...\n"
                    "$ ansible-playbook site.yml --ask-vault-pass</code></pre>"
                    "<p>Em produção, prefira lookups para Vault/Secrets Manager:</p>"
                    "<pre><code>vars:\n"
                    "  db_password: \"{{ lookup('amazon.aws.aws_secret', 'prod/db/password') }}\"</code></pre>"

                    "<h3>5. Templates Jinja2</h3>"
                    "<pre><code># templates/nginx.conf.j2\n"
                    "server {\n"
                    "    listen {{ nginx_port }};\n"
                    "    server_name {{ ansible_fqdn }};\n"
                    "\n"
                    "    {% if env == 'production' %}\n"
                    "    ssl_certificate /etc/letsencrypt/live/{{ ansible_fqdn }}/fullchain.pem;\n"
                    "    ssl_certificate_key /etc/letsencrypt/live/{{ ansible_fqdn }}/privkey.pem;\n"
                    "    {% endif %}\n"
                    "\n"
                    "    {% for upstream in upstreams %}\n"
                    "    upstream {{ upstream.name }} {\n"
                    "        {% for srv in upstream.servers %}\n"
                    "        server {{ srv }};\n"
                    "        {% endfor %}\n"
                    "    }\n"
                    "    {% endfor %}\n"
                    "}</code></pre>"

                    "<h3>6. Operação em escala</h3>"
                    "<ul>"
                    "<li><code>--check</code>: dry-run (não aplica). <code>--diff</code> "
                    "mostra mudanças propostas em arquivos.</li>"
                    "<li><code>--limit web1.example.com</code>: roda só em um host.</li>"
                    "<li><code>--tags install</code> / <code>--skip-tags reboot</code>: "
                    "controle granular.</li>"
                    "<li><code>forks</code> (default 5): paralelismo.</li>"
                    "<li>Strategies: <code>linear</code> (espera todos antes de avançar, "
                    "padrão), <code>free</code> (cada host segue independente), "
                    "<code>host_pinned</code>.</li>"
                    "<li><code>serial: 25%</code>: rolling upgrade (25% por vez).</li>"
                    "</ul>"

                    "<h3>7. Testes: Molecule + ansible-lint</h3>"
                    "<p><code>molecule</code> roda role em container/VM, valida idempotência "
                    "e estado.</p>"
                    "<pre><code># molecule/default/molecule.yml\n"
                    "driver:\n"
                    "  name: docker\n"
                    "platforms:\n"
                    "  - name: ubuntu-22\n"
                    "    image: geerlingguy/docker-ubuntu2204-ansible\n"
                    "verifier:\n"
                    "  name: ansible</code></pre>"
                    "<pre><code>$ molecule test\n"
                    "# create container, converge (rodar a role), idempotence (rodar de novo,\n"
                    "# verificar que nenhuma task reportou changed=true), verify, destroy</code></pre>"
                    "<p><code>ansible-lint</code> pega anti-patterns comuns:</p>"
                    "<pre><code>$ ansible-lint roles/webserver\n"
                    "WARNING: name[missing] - All tasks should be named\n"
                    "ERROR: command-instead-of-shell - Use shell only when shell features needed</code></pre>"

                    "<h3>8. AWX/Tower e governance</h3>"
                    "<p>Em escala, rodar <code>ansible-playbook</code> manual vira problema: "
                    "quem rodou, quando, com que vars? AWX (open source) e Ansible Tower "
                    "(comercial) dão UI, RBAC, surveys, scheduling, audit log e secret "
                    "management integrado.</p>"

                    "<h3>9. Ansible vs Terraform: complementares, não substitutos</h3>"
                    "<p>Regra prática:</p>"
                    "<ul>"
                    "<li><strong>Terraform</strong>: provisão de recursos cloud (VMs, VPCs, "
                    "RDS, IAM). Mundo declarativo, state.</li>"
                    "<li><strong>Ansible</strong>: configuração interna de OS, deploy de app, "
                    "orquestração de comandos. Mundo procedural mas idempotente.</li>"
                    "</ul>"
                    "<p>Padrão comum: Terraform cria EC2 → output IPs → Ansible-pull ou "
                    "GitHub Actions roda playbooks. Ou: AMI base 'golden' construída com "
                    "Packer + Ansible, depois Terraform apenas instancia. Imagens "
                    "imutáveis vs mutáveis é decisão arquitetural importante.</p>"

                    "<h3>10. Anti-patterns comuns</h3>"
                    "<ul>"
                    "<li><strong>Tasks sem <code>name</code></strong>: log impossível "
                    "de ler.</li>"
                    "<li><strong>Abusar de <code>shell</code>/<code>command</code></strong>: "
                    "perde idempotência.</li>"
                    "<li><strong>Senha em playbook texto puro</strong>: use Vault.</li>"
                    "<li><strong>Roles sem defaults</strong>: usuários têm que adivinhar "
                    "todas as vars.</li>"
                    "<li><strong>Rodar como root sempre</strong>: use <code>become</code> "
                    "só onde necessário.</li>"
                    "<li><strong>Inventário gigante e estático em cloud</strong>: use "
                    "dinâmico.</li>"
                    "<li><strong>Sem testes (Molecule)</strong>: cada execução é incógnita.</li>"
                    "</ul>"
                ),
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
            },
            "materials": [
                m("Ansible docs", "https://docs.ansible.com/", "docs", ""),
                m("Ansible Galaxy", "https://galaxy.ansible.com/", "tool", ""),
                m("Ansible for DevOps (livro)", "https://www.ansiblefordevops.com/", "book", ""),
                m("ansible-lint", "https://ansible.readthedocs.io/projects/lint/", "tool", ""),
                m("Molecule (testes)", "https://ansible.readthedocs.io/projects/molecule/", "tool", ""),
                m("AWX (open source Tower)", "https://github.com/ansible/awx", "tool", ""),
            ],
            "questions": [
                q("Ansible exige agente nos hosts gerenciados?",
                  "Não, basta SSH e Python.",
                  ["Sim, daemon obrigatório.", "Sim, agente em C.", "Sim, kubelet."],
                  "Em hosts mínimos sem Python, há `raw` module para bootstrap. Em Windows, WinRM."),
                q("Idempotência significa:",
                  "Rodar a mesma tarefa N vezes resulta no mesmo estado.",
                  ["Falha em loops.", "Sempre cria recurso novo.", "Aleatório."],
                  "Permite rodar playbooks com confiança em sistemas já configurados (convergência)."),
                q("ansible-vault serve para:",
                  "Criptografar arquivos com segredos no repositório.",
                  ["Compactar logs.", "Substituir KMS.", "Comprimir playbooks."],
                  "Bom para projetos pequenos. Em escala, prefira lookups para Vault/Secrets Manager."),
                q("Inventário pode ser:",
                  "Estático (arquivo) ou dinâmico (script/plugin).",
                  ["Apenas estático.", "Apenas dinâmico.", "Apenas em INI."],
                  "Dinâmico é essencial em cloud com auto-scaling, onde IPs mudam."),
                q("Role em Ansible é:",
                  "Conjunto reutilizável de tasks, handlers, templates, etc.",
                  ["Política IAM.", "Tipo de host.", "Comando shell."],
                  "Estrutura padrão (tasks/, handlers/, defaults/, templates/) facilita compartilhamento."),
                q("Handlers são executados:",
                  "Apenas quando um task notifica e tem mudança.",
                  ["Sempre primeiro.", "Aleatoriamente.", "Apenas com erro."],
                  "Padrão clássico: copiar nginx.conf → notify 'restart nginx'. Restart só ocorre se houve mudança."),
                q("Diferença entre Ansible e Terraform:",
                  "Ansible foca em config interna; Terraform em provisão de infra.",
                  ["São idênticos.", "Ansible cria VMs; Terraform configura.", "Ambos só rodam local."],
                  "Não é regra rígida (Ansible cria recursos cloud, Terraform pode configurar). Mas a pegada é essa."),
                q("ansible-lint serve para:",
                  "Detectar más práticas em playbooks.",
                  ["Substituir o ansible.", "Compilar YAML.", "Subir ao Galaxy."],
                  "Pega coisas como 'task sem nome', 'shell sem creates', 'sudo redundante'."),
                q("Modo `--check` faz:",
                  "Dry-run, simulando sem aplicar.",
                  ["Aplica e ignora erros.", "Cria backup.", "Reinicia agentes."],
                  "Combine com `--diff` para ver o que mudaria. Útil em PR antes de aplicar."),
                q("Para 100+ hosts paralelos:",
                  "Ajuste forks e use estratégias (free, linear).",
                  ["Não há como.", "Use cron.", "Reduza a 1 host."],
                  "Default fork=5. Aumentar exige memória no controlador. Strategy 'free' não espera todos."),
            ],
        },
        # =====================================================================
        # 3.4 Secret Management
        # =====================================================================
        {
            "title": "Secret Management",
            "summary": "Onde guardar senhas que não seja no código (Vault e similares).",
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
                "body": (
                    "<h3>1. Tipos de segredos</h3>"
                    "<ul>"
                    "<li><strong>Estáticos</strong>: senha de banco, API key, token de "
                    "serviço. São criados manualmente e pouco mudam. Devem ir para o cofre "
                    "e ser rotacionados periodicamente.</li>"
                    "<li><strong>Dinâmicos</strong>: o cofre cria sob demanda com TTL. "
                    "Vault gera usuário Postgres temporário com senha aleatória válida por "
                    "1h, depois revoga. <em>Janela de exposição mínima</em>.</li>"
                    "<li><strong>Tokens efêmeros</strong>: JWT/STS/OIDC com TTL curto. "
                    "Sem armazenamento persistente em parte alguma. AssumeRole na AWS, "
                    "Workload Identity no GCP, Managed Identity na Azure.</li>"
                    "<li><strong>Certificados</strong>: TLS, mTLS, SSH CA. Geralmente curtos "
                    "(7-90 dias) e renovados via ACME ou ferramenta similar (Vault PKI, "
                    "smallstep, cert-manager).</li>"
                    "</ul>"

                    "<h3>2. Onde NUNCA guardar segredos</h3>"
                    "<ul>"
                    "<li><strong>Git</strong>, mesmo em repo privado. Forks, clones, "
                    "exports, histórico, uma vez lá, está lá para sempre.</li>"
                    "<li><strong>Slack/Teams/Discord</strong>: logs, integrations, exports "
                    "de discovery. Empresa pode reter mensagens por anos.</li>"
                    "<li><strong>Email</strong>: idem, e ainda passa por servidores externos.</li>"
                    "<li><strong>Dockerfile (ENV/ARG)</strong>: segredo vai parar em "
                    "<em>layers</em> da imagem. <code>docker history image</code> revela "
                    "para qualquer um com pull access.</li>"
                    "<li><strong>Logs</strong>: de aplicação ou de CI. SIEM e SaaS de log "
                    "guardam por 30+ dias.</li>"
                    "<li><strong>Variáveis de ambiente em CI sem mask</strong>: aparecem em "
                    "<code>echo $VAR</code> de algum step.</li>"
                    "<li><strong>Browser/extensão sincronizada</strong>: vão para a nuvem "
                    "do navegador.</li>"
                    "</ul>"

                    "<h3>3. Cofres modernos</h3>"
                    "<table>"
                    "<tr><th>Cofre</th><th>Pontos fortes</th></tr>"
                    "<tr><td>HashiCorp Vault</td><td>Multi-cloud, dynamic secrets, transit, PKI, OIDC. Self-hosted ou Cloud.</td></tr>"
                    "<tr><td>AWS Secrets Manager</td><td>Integração nativa AWS, rotação automática RDS, cross-region replication.</td></tr>"
                    "<tr><td>AWS Parameter Store</td><td>Mais barato, mais simples; bom para configs e segredos menos críticos.</td></tr>"
                    "<tr><td>Azure Key Vault</td><td>Integração Entra ID, HSM-backed.</td></tr>"
                    "<tr><td>GCP Secret Manager</td><td>Versionamento, replicação, IAM granular.</td></tr>"
                    "<tr><td>1Password / Bitwarden</td><td>Bom para humanos + secret automation (1Password Connect).</td></tr>"
                    "<tr><td>Doppler / Infisical</td><td>SaaS pequenos, focados em devex.</td></tr>"
                    "</table>"

                    "<h3>4. Padrão: nunca leia o cofre direto da app (se possível)</h3>"
                    "<p>App acessar cofre direto exige: cliente, retry, cache, autenticação, "
                    "tratamento de erro. E em incidente de cofre, app cai junto. Padrões "
                    "melhores:</p>"
                    "<h4>4.1 Sidecar/Init container injetor</h4>"
                    "<p>Outro container puxa do cofre e escreve em arquivo/volume "
                    "compartilhado. App lê do arquivo. Vault Agent é o exemplo clássico:</p>"
                    "<pre><code># Pod K8s\n"
                    "annotations:\n"
                    "  vault.hashicorp.com/agent-inject: 'true'\n"
                    "  vault.hashicorp.com/role: 'app'\n"
                    "  vault.hashicorp.com/agent-inject-secret-db: 'database/creds/app'</code></pre>"
                    "<h4>4.2 Operator no K8s</h4>"
                    "<p><strong>External Secrets Operator</strong> (ESO): você cria CR "
                    "<code>ExternalSecret</code> apontando para cofre; ESO popula um "
                    "<code>Secret</code> nativo no namespace. App consome como Secret normal:</p>"
                    "<pre><code>apiVersion: external-secrets.io/v1beta1\n"
                    "kind: ExternalSecret\n"
                    "metadata: { name: app-db }\n"
                    "spec:\n"
                    "  secretStoreRef: { name: aws-sm, kind: ClusterSecretStore }\n"
                    "  target: { name: app-db-secret }\n"
                    "  data:\n"
                    "    - secretKey: password\n"
                    "      remoteRef: { key: prod/app/db, property: password }</code></pre>"
                    "<h4>4.3 OIDC/Workload Identity</h4>"
                    "<p>Em CI/CD, o melhor é <em>nada armazenado</em>. GitHub Actions emite "
                    "JWT efêmero; AWS valida via OIDC e devolve credencial STS. Sem secret "
                    "no GitHub.</p>"
                    "<pre><code>permissions:\n"
                    "  id-token: write\n"
                    "  contents: read\n"
                    "jobs:\n"
                    "  deploy:\n"
                    "    steps:\n"
                    "      - uses: aws-actions/configure-aws-credentials@v4\n"
                    "        with:\n"
                    "          role-to-assume: arn:aws:iam::111111111111:role/gh-deployer\n"
                    "          aws-region: us-east-1\n"
                    "      - run: aws s3 sync ./build s3://app-prod   # sem keys!</code></pre>"

                    "<h3>5. Rotação</h3>"
                    "<p>Política comum:</p>"
                    "<ul>"
                    "<li>Credenciais humanas (senha, MFA reset): 90d.</li>"
                    "<li>Credenciais máquinas estáticas: 30-90d.</li>"
                    "<li>Credenciais críticas (root, master KMS): cuidado, mas idealmente 365d com auditoria.</li>"
                    "<li>Após qualquer suspeita: imediata.</li>"
                    "</ul>"
                    "<p>Vault dynamic secrets dão rotação 'natural' (TTL curto). Em "
                    "estáticos, automatize: AWS Secrets Manager rotaciona RDS sozinho "
                    "se você ativar; é uma Lambda que cria nova senha, atualiza RDS, "
                    "atualiza secret. App busca via cache com TTL, pega nova senha "
                    "automaticamente.</p>"

                    "<h3>6. Detecção em PR e em código</h3>"
                    "<p>Acidentes acontecem. Camadas defensivas:</p>"
                    "<ul>"
                    "<li><strong>Pre-commit hook</strong> (gitleaks, trufflehog, "
                    "detect-secrets): bloqueia push antes de sair do laptop.</li>"
                    "<li><strong>CI check</strong>: mesmo se pre-commit foi pulado, server "
                    "pega.</li>"
                    "<li><strong>GitHub Secret Scanning</strong>: ativo por padrão em "
                    "público; Advanced Security em privado. Detecta &gt;200 padrões e "
                    "notifica provider (AWS, Stripe, etc.) que pode revogar automaticamente.</li>"
                    "<li><strong>Auditoria periódica</strong> de repos antigos com "
                    "trufflehog/gitleaks-search.</li>"
                    "</ul>"
                    "<p>Exemplo gitleaks pre-commit:</p>"
                    "<pre><code># .pre-commit-config.yaml\n"
                    "repos:\n"
                    "  - repo: https://github.com/gitleaks/gitleaks\n"
                    "    rev: v8.18.0\n"
                    "    hooks:\n"
                    "      - id: gitleaks</code></pre>"

                    "<h3>7. SE um segredo vazou: o que fazer</h3>"
                    "<ol>"
                    "<li><strong>Rotacione imediatamente</strong>. Mesmo se vc 'só' deu "
                    "<code>git rm --cached</code>: o histórico ainda tem.</li>"
                    "<li><strong>Verifique uso</strong>: logs do provider (CloudTrail, "
                    "Stripe events, etc.). Talvez já está sendo abusado.</li>"
                    "<li>Considere remover do histórico (BFG, git filter-repo), mais para "
                    "limpar do que para 'esconder'. Forks/clones já têm.</li>"
                    "<li>Comunique ao time/security. Não esconda.</li>"
                    "<li>Postmortem: como vazou? Como impedir próxima vez?</li>"
                    "</ol>"

                    "<h3>8. K8s Secrets: cuidados</h3>"
                    "<p>K8s <code>Secret</code> nativo é apenas <strong>base64</strong>, "
                    "não criptografado. <code>kubectl get secret -o yaml</code> revela em "
                    "texto plano. Em multi-tenant ou cluster compartilhado, tratar com "
                    "cuidado:</p>"
                    "<ul>"
                    "<li>Habilite <strong>encryption-at-rest</strong> no etcd "
                    "(<code>EncryptionConfiguration</code> com KMS).</li>"
                    "<li>RBAC restritivo: só app namespace lê seus secrets.</li>"
                    "<li>SealedSecrets (Bitnami) para GitOps: secret cripto pode ser "
                    "commitado no Git, controller decripta no cluster.</li>"
                    "<li>SOPS + KMS: arquivos YAML/JSON criptografados commitáveis.</li>"
                    "<li>External Secrets Operator: padrão moderno para cofre externo.</li>"
                    "</ul>"

                    "<h3>9. Vault transit engine: criptografia como serviço</h3>"
                    "<p>Você tem dado sensível em DB (CPF, cartão, prontuário). Em vez de "
                    "guardar plaintext ou implementar cripto na app, use Vault transit:</p>"
                    "<pre><code># app envia plaintext, recebe ciphertext\n"
                    "POST /v1/transit/encrypt/customer-pii\n"
                    "{ \"plaintext\": \"MTIzNDU2Nzg5\" }   # base64\n"
                    "→ { \"ciphertext\": \"vault:v2:abc...\" }\n"
                    "\n"
                    "# DB armazena 'vault:v2:abc...'\n"
                    "# Para ler, app chama /decrypt</code></pre>"
                    "<p>Vantagens: chave nunca sai do Vault, rotação centralizada, "
                    "auditoria por chamada. Útil para PCI/LGPD/HIPAA.</p>"

                    "<h3>10. Caso real: codecov breach (2021)</h3>"
                    "<p>Atacantes injetaram código no script bash do Codecov "
                    "(<code>bash &lt;(curl ...)</code> em CIs do mundo todo). Esse script "
                    "exfiltrava variáveis de ambiente, incluindo secrets de CI. "
                    "Resultado: milhares de keys/tokens vazados de centenas de empresas.</p>"
                    "<p>Lição: secret em variável de ambiente de CI é vulnerável a "
                    "qualquer script suspeito. OIDC com tokens efêmeros teria limitado o "
                    "blast radius, mesmo capturando o token, ele expirava em minutos.</p>"
                ),
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
            },
            "materials": [
                m("HashiCorp Vault docs", "https://developer.hashicorp.com/vault/docs", "docs", ""),
                m("AWS Secrets Manager", "https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html", "docs", ""),
                m("Azure Key Vault", "https://learn.microsoft.com/azure/key-vault/general/overview", "docs", ""),
                m("GitHub OIDC", "https://docs.github.com/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect", "docs", ""),
                m("Mozilla SOPS", "https://github.com/getsops/sops", "tool", ""),
                m("External Secrets Operator (K8s)", "https://external-secrets.io/", "tool", ""),
            ],
            "questions": [
                q("Senha em código é:",
                  "Risco crítico, bastando um clone público para vazar.",
                  ["Boa prática.", "Imune a leaks.", "Encriptada por default."],
                  "Crawlers buscam por padrões como `AKIA...` em segundos após push público."),
                q("Vault dynamic secrets:",
                  "Geram credenciais temporárias por demanda.",
                  ["São arquivos cripto.", "São DNS.", "Substituem TLS."],
                  "Diminui janela de exposição, e revogação é trivial, basta TTL expirar."),
                q("OIDC em CI evita:",
                  "Armazenar chaves longas estáticas.",
                  ["Reduzir tempo de build.", "Atualizar dependências.", "Substituir Docker."],
                  "GitHub emite token JWT efêmero; AWS valida e devolve credencial STS, sem segredo persistente."),
                q("SOPS criptografa:",
                  "Arquivos YAML/JSON com chaves KMS.",
                  ["Apenas binários.", "Apenas senhas.", "Apenas hashes."],
                  "Permite commitar arquivo cripto no repo (GitOps friendly). Decryption só com permissão KMS."),
                q("Rotação automática reduz:",
                  "Janela de exposição se a senha vazar.",
                  ["Custo.", "Latência.", "Tamanho do arquivo."],
                  "Mesmo se um atacante captura, a credencial vira inválida em poucos dias."),
                q("Compartilhar segredo via Slack:",
                  "Risco de exposição persistente, preferir cofres.",
                  ["Boa prática.", "Auto-expira.", "Encriptado por padrão."],
                  "Mensagens permanecem em logs corporativos, integrações, exports. Use 1Password share / Vault link com TTL."),
                q("`.env.example` deve conter:",
                  "Apenas as chaves esperadas, sem valores reais.",
                  ["Senha de produção.", "Token KMS.", "Backup de banco."],
                  "Documenta variáveis necessárias, mas valores ficam fora do repo."),
                q("Pre-commit hook útil:",
                  "Detectar segredos com gitleaks ou trufflehog.",
                  ["Apagar histórico.", "Forçar push.", "Comprimir o repo."],
                  "Bloqueia push antes do segredo sair do laptop. Combine com checagem server-side."),
                q("Em K8s, segredos como Secret são:",
                  "Base64 encoded, NÃO criptografados por padrão.",
                  ["Sempre cripto.", "Hashes irreversíveis.", "Não podem ter binário."],
                  "Habilite encryption-at-rest no etcd e use ferramentas como SealedSecrets/External Secrets."),
                q("Vault transit engine serve para:",
                  "Criptografia como serviço (encrypt/decrypt) sem expor a chave.",
                  ["Backup de logs.", "Provisão de VMs.", "Auditoria de IAM."],
                  "App envia plaintext, recebe ciphertext. Chave nunca sai do Vault. Bom para campos sensíveis em DB."),
            ],
        },
        # =====================================================================
        # 3.5 CI/CD Básico
        # =====================================================================
        {
            "title": "CI/CD Básico",
            "summary": "Criar uma esteira simples que testa e move o código para o servidor.",
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
                "body": (
                    "<h3>1. CI vs CD vs CD: três conceitos, duas siglas</h3>"
                    "<p><strong>CI (Continuous Integration)</strong>: a cada commit, código "
                    "é mergeado e validado, build, lint, testes unitários, SAST, SCA. "
                    "Objetivo: encontrar problema em minutos, não dias. Se o build quebra, "
                    "<em>todo o time para</em> até consertar.</p>"
                    "<p><strong>CD (Continuous Delivery)</strong>: artefato sempre pronto "
                    "para deploy a qualquer momento, mas <em>humano aperta o botão</em>. "
                    "Comum em times que ainda querem aprovação humana.</p>"
                    "<p><strong>CD (Continuous Deployment)</strong>: cada commit que passa "
                    "no pipeline vai automaticamente para produção. Maturidade alta. "
                    "Requer testes e telemetria muito bons.</p>"

                    "<h3>2. Pipeline mínimo de qualidade</h3>"
                    "<pre><code>commit → lint → unit tests → build → security scans →\n"
                    "         push artefato → deploy dev → integration tests →\n"
                    "         deploy staging → smoke + e2e → [approval] → deploy prod</code></pre>"
                    "<p>Cada etapa deve <strong>falhar rápido</strong>: lint em segundos, "
                    "unit em &lt;5min, integration em &lt;15min. Pipeline lento é pipeline "
                    "ignorado.</p>"

                    "<h3>3. GitHub Actions: pipeline completo de exemplo</h3>"
                    "<pre><code>name: ci-cd\n"
                    "on:\n"
                    "  push: { branches: [main] }\n"
                    "  pull_request: {}\n"
                    "permissions:\n"
                    "  contents: read\n"
                    "  packages: write\n"
                    "  id-token: write\n"
                    "  security-events: write\n"
                    "concurrency:\n"
                    "  group: ${{ github.workflow }}-${{ github.ref }}\n"
                    "  cancel-in-progress: true\n"
                    "jobs:\n"
                    "  lint:\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - uses: actions/setup-python@v5\n"
                    "        with: { python-version: '3.12', cache: 'pip' }\n"
                    "      - run: pip install -r requirements-dev.txt\n"
                    "      - run: ruff check .\n"
                    "      - run: ruff format --check .\n"
                    "      - run: mypy app\n"
                    "  test:\n"
                    "    needs: lint\n"
                    "    runs-on: ubuntu-latest\n"
                    "    services:\n"
                    "      postgres:\n"
                    "        image: postgres:16\n"
                    "        env: { POSTGRES_PASSWORD: ci }\n"
                    "        options: --health-cmd pg_isready\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - uses: actions/setup-python@v5\n"
                    "        with: { python-version: '3.12' }\n"
                    "      - run: pip install -r requirements-dev.txt\n"
                    "      - run: pytest --cov=app --cov-report=xml\n"
                    "      - uses: codecov/codecov-action@v4\n"
                    "  security:\n"
                    "    needs: lint\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - uses: aquasecurity/trivy-action@master\n"
                    "        with:\n"
                    "          scan-type: fs\n"
                    "          severity: 'CRITICAL,HIGH'\n"
                    "          exit-code: '1'\n"
                    "      - uses: returntocorp/semgrep-action@v1\n"
                    "        with: { config: p/owasp-top-ten }\n"
                    "      - uses: gitleaks/gitleaks-action@v2\n"
                    "  build:\n"
                    "    needs: [test, security]\n"
                    "    runs-on: ubuntu-latest\n"
                    "    outputs:\n"
                    "      digest: ${{ steps.push.outputs.digest }}\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - uses: docker/setup-buildx-action@v3\n"
                    "      - uses: docker/login-action@v3\n"
                    "        with:\n"
                    "          registry: ghcr.io\n"
                    "          username: ${{ github.actor }}\n"
                    "          password: ${{ secrets.GITHUB_TOKEN }}\n"
                    "      - id: push\n"
                    "        uses: docker/build-push-action@v5\n"
                    "        with:\n"
                    "          push: true\n"
                    "          tags: |\n"
                    "            ghcr.io/empresa/app:${{ github.sha }}\n"
                    "            ghcr.io/empresa/app:latest\n"
                    "          cache-from: type=gha\n"
                    "          cache-to: type=gha,mode=max\n"
                    "      - uses: aquasecurity/trivy-action@master\n"
                    "        with:\n"
                    "          image-ref: ghcr.io/empresa/app:${{ github.sha }}\n"
                    "          severity: 'CRITICAL'\n"
                    "          exit-code: '1'\n"
                    "      - uses: sigstore/cosign-installer@v3\n"
                    "      - run: cosign sign --yes ghcr.io/empresa/app@${{ steps.push.outputs.digest }}\n"
                    "  deploy-staging:\n"
                    "    needs: build\n"
                    "    if: github.ref == 'refs/heads/main'\n"
                    "    environment: staging\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: aws-actions/configure-aws-credentials@v4\n"
                    "        with:\n"
                    "          role-to-assume: arn:aws:iam::111:role/deployer\n"
                    "          aws-region: us-east-1\n"
                    "      - run: ./scripts/deploy.sh staging ${{ github.sha }}\n"
                    "      - run: ./scripts/smoke-tests.sh https://staging.app\n"
                    "  deploy-prod:\n"
                    "    needs: deploy-staging\n"
                    "    environment: production   # gate manual\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - run: ./scripts/deploy.sh prod ${{ github.sha }}</code></pre>"
                    "<p>Pontos importantes:</p>"
                    "<ul>"
                    "<li><code>concurrency</code>: cancela runs antigos do mesmo branch.</li>"
                    "<li><code>permissions</code>: princípio do menor privilégio (write só "
                    "onde precisa).</li>"
                    "<li>OIDC para AWS sem armazenar keys.</li>"
                    "<li><code>environment: production</code>: gate manual; mais "
                    "secrets/wait timer/required reviewers configurados na UI.</li>"
                    "<li>Cosign assina imagem; admission controller K8s pode verificar.</li>"
                    "</ul>"

                    "<h3>4. Estratégias de deploy</h3>"
                    "<h4>4.1 Recriação (recreate)</h4>"
                    "<p>Para ambiente novo. Mata todos os pods antigos, sobe novos. Causa "
                    "downtime. Bom para dev/QA, ruim para prod.</p>"
                    "<h4>4.2 Rolling</h4>"
                    "<p>Substitui réplicas aos poucos. Padrão em K8s. Não tem downtime se "
                    "app suporta múltiplas versões coexistindo. Rollback é rolar de volta "
                    "(lento).</p>"
                    "<pre><code>spec:\n"
                    "  strategy:\n"
                    "    type: RollingUpdate\n"
                    "    rollingUpdate:\n"
                    "      maxSurge: 25%\n"
                    "      maxUnavailable: 0</code></pre>"
                    "<h4>4.3 Blue-Green</h4>"
                    "<p>Dois ambientes idênticos: blue (atual) e green (novo). Você "
                    "mantém os dois rodando, faz deploy no green, valida, troca o tráfego "
                    "do load balancer. Rollback é trocar de volta, segundos.</p>"
                    "<p>Custo: dobrado durante a transição. Bom para sistemas que toleram "
                    "duplicação de recursos por algumas horas.</p>"
                    "<h4>4.4 Canary</h4>"
                    "<p>Libera nova versão para X% dos usuários (ex.: 5%), monitora "
                    "métricas (errors, latency, business KPIs). Se ok, aumenta para 25%, "
                    "50%, 100%. Se ruim, rollback.</p>"
                    "<p>Origem: canários em mina de carvão, morriam antes dos humanos como "
                    "alarme. Aqui, % pequeno de tráfego sente o problema antes da maioria.</p>"
                    "<p>Argo Rollouts e Flagger automatizam canary com promoção baseada "
                    "em Prometheus/Datadog metrics.</p>"
                    "<h4>4.5 Feature flags</h4>"
                    "<p>Deploy desacoplado de release. Código vai para prod desligado, "
                    "ativa-se gradualmente por flag. LaunchDarkly, Unleash, OpenFeature, "
                    "ConfigCat. Permite A/B test, kill switch, rollback instantâneo "
                    "sem redeploy.</p>"
                    "<pre><code>if (flags.isEnabled('new-checkout-flow', user)) {\n"
                    "    return newCheckout(req);\n"
                    "}\n"
                    "return oldCheckout(req);</code></pre>"

                    "<h3>5. Artefatos imutáveis</h3>"
                    "<p>Princípio: o mesmo binário/imagem que passou em staging vai para "
                    "prod, identificado por hash/SHA. Nada de 'rebuild para prod', você "
                    "está testando outra coisa.</p>"
                    "<p>Isso significa:</p>"
                    "<ul>"
                    "<li>Tag por commit SHA (<code>app:abc1234</code>) ou versão semver "
                    "(<code>app:v1.4.2</code>).</li>"
                    "<li>Evite <code>latest</code> em produção, não é rastreável.</li>"
                    "<li>Build uma vez, promova entre ambientes.</li>"
                    "<li>Configurações injetadas via env vars / secrets externos, não no "
                    "build.</li>"
                    "<li>Assinatura (Cosign) garante integridade.</li>"
                    "</ul>"

                    "<h3>6. Pipeline-as-code</h3>"
                    "<p>O pipeline mora no repo: <code>.github/workflows/</code>, "
                    "<code>.gitlab-ci.yml</code>, <code>Jenkinsfile</code>, "
                    "<code>buildspec.yml</code>. Versionado, revisado em PR, auditável. "
                    "<em>Nunca</em> mais 'só admin sabe o que existe no Jenkins clássico'.</p>"

                    "<h3>7. Métricas DORA</h3>"
                    "<p>Pesquisa do Google (DORA) por anos correlacionou alta performance "
                    "de engenharia com 4 métricas:</p>"
                    "<ul>"
                    "<li><strong>Deployment Frequency</strong>: quantas vezes por dia/"
                    "semana/mês você deploya. Elite: várias por dia.</li>"
                    "<li><strong>Lead Time for Changes</strong>: do commit ao deploy em "
                    "prod. Elite: &lt;1h.</li>"
                    "<li><strong>Mean Time to Restore (MTTR)</strong>: tempo para "
                    "recuperar de incidente. Elite: &lt;1h.</li>"
                    "<li><strong>Change Failure Rate</strong>: % de deploys que causam "
                    "incidente. Elite: 0-15%.</li>"
                    "</ul>"
                    "<p>Times elite têm todas altas, não trade-off entre velocidade e "
                    "estabilidade. O que viabiliza: testes automatizados, deploy automatizado, "
                    "trunk-based, observabilidade.</p>"

                    "<h3>8. Cache, matrix e otimização</h3>"
                    "<ul>"
                    "<li><strong>Cache</strong> de dependências (Python pip, npm, Go modules, "
                    "Docker layers). Chave por lockfile hash, não por branch.</li>"
                    "<li><strong>Matrix builds</strong>: Python 3.10/3.11/3.12 × Linux/macOS, "
                    "paralelo. Roda em ~tempo de uma execução.</li>"
                    "<li><strong>Reusable workflows</strong> (GitHub) ou "
                    "<code>include</code> (GitLab): DRY entre repos.</li>"
                    "<li><strong>Self-hosted runners</strong>: para builds pesados ou "
                    "necessidade de hardware específico (GPU).</li>"
                    "</ul>"

                    "<h3>9. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Deploy manual em prod</strong>: erro humano frequente.</li>"
                    "<li><strong>Pipeline sem testes</strong>: 'deploy direto' = roleta russa.</li>"
                    "<li><strong>Test escape rate alto</strong>: bugs chegam em prod com CI verde, sinal de testes ruins.</li>"
                    "<li><strong>Pipeline lento (1h+)</strong>: ninguém espera, todos pulam.</li>"
                    "<li><strong>Flaky tests</strong>: testes intermitentes corroem confiança.</li>"
                    "<li><strong>Build em prod</strong>: 'só recompilei lá' = bug específico que ninguém reproduz.</li>"
                    "<li><strong>Apenas main testado</strong>: PRs sem CI = problemas só aparecem após merge.</li>"
                    "</ul>"

                    "<h3>10. GitOps</h3>"
                    "<p>Padrão: repo Git é a fonte da verdade do estado desejado do "
                    "cluster. Argo CD ou Flux observa o repo; quando muda, reconcilia. "
                    "Sem <code>kubectl apply</code> manual.</p>"
                    "<pre><code># cluster/applications/app.yaml\n"
                    "apiVersion: argoproj.io/v1alpha1\n"
                    "kind: Application\n"
                    "metadata: { name: app, namespace: argocd }\n"
                    "spec:\n"
                    "  source:\n"
                    "    repoURL: https://github.com/empresa/k8s-config\n"
                    "    path: apps/app/overlays/prod\n"
                    "  destination:\n"
                    "    server: https://kubernetes.default.svc\n"
                    "    namespace: prod\n"
                    "  syncPolicy:\n"
                    "    automated: { prune: true, selfHeal: true }</code></pre>"
                    "<p>Vantagens: rollback = revert no Git; auditoria = git log; "
                    "drift detection nativo.</p>"
                ),
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
            },
            "materials": [
                m("GitHub Actions docs", "https://docs.github.com/actions", "docs", ""),
                m("GitLab CI/CD", "https://docs.gitlab.com/ee/ci/", "docs", ""),
                m("Jenkins handbook", "https://www.jenkins.io/doc/book/", "docs", ""),
                m("Continuous Delivery (livro)", "https://continuousdelivery.com/", "book", ""),
                m("Argo CD", "https://argo-cd.readthedocs.io/", "tool", ""),
                m("DORA metrics", "https://dora.dev/", "article", "Pesquisa do Google sobre DevOps."),
            ],
            "questions": [
                q("CI difere de CD porque:",
                  "CI integra/testa código; CD entrega/deploy automaticamente.",
                  ["São idênticos.", "CD não testa.", "CI faz deploy."],
                  "CD pode ser delivery (manual aprovar) ou deployment (totalmente automático)."),
                q("Deploy canário:",
                  "Libera para uma fração de usuários antes do total.",
                  ["Roda apenas em dev.", "É um IDE.", "Substitui blue-green."],
                  "Origem: canário em mina de carvão. Métricas guiam quando avançar/reverter."),
                q("Pipeline as code é:",
                  "Definir o pipeline em arquivo versionado no repo.",
                  ["Rodar pipeline manualmente.", "Sem versionamento.", "Apenas script bash."],
                  "Mudanças no pipeline passam pelo mesmo PR review do código."),
                q("Falha de teste deve:",
                  "Bloquear o merge/deploy.",
                  ["Ser ignorada.", "Apenas warn.", "Acelerar release."],
                  "Sem 'pode pode' o pipeline morre. Triagem ágil para flaky tests é essencial."),
                q("Rollback rápido depende de:",
                  "Artefatos imutáveis e healthchecks.",
                  ["Apenas backup do disco.", "Sem versionamento.", "Build do zero."],
                  "Re-deploy do artefato anterior leva segundos; rebuild leva minutos."),
                q("Cache em CI serve para:",
                  "Acelerar builds reaproveitando dependências.",
                  ["Substituir testes.", "Compactar log.", "Trocar runner."],
                  "Cuide de invalidação correta (chave por lockfile, não por branch arbitrário)."),
                q("Matrix builds servem para:",
                  "Rodar a mesma pipeline com várias combinações (versões/SO).",
                  ["Reduzir testes.", "Aumentar cache.", "Trocar IDE."],
                  "Ex.: testar Python 3.10/3.11/3.12 × Linux/macOS em paralelo."),
                q("Trunk-based + CI/CD geralmente exige:",
                  "Feature flags e testes automatizados fortes.",
                  ["Branches longas.", "Deploy manual.", "Sem CI."],
                  "Sem flags, código incompleto não pode ir para main com segurança."),
                q("Artefato imutável significa:",
                  "Mesma versão (hash) é sempre a mesma, usado em todos os ambientes.",
                  ["Pode ser editado.", "Tem TTL.", "É só local."],
                  "Tag SHA + assinatura (Cosign) garante. 'latest' móvel é o oposto."),
                q("Argo CD aplica padrão:",
                  "GitOps, repo Git é a fonte da verdade.",
                  ["FTP-based.", "Cron-based.", "Manual."],
                  "Argo observa o repo; quando muda, reconcilia o cluster com o declarado."),
            ],
        },
        # =====================================================================
        # 3.6 Linting
        # =====================================================================
        {
            "title": "Linting de Código e IaC",
            "summary": "Ferramentas que avisam se você escreveu algo inseguro.",
            "lesson": {
                "intro": (
                    "Linter é a primeira linha de defesa contra bugs e más práticas. "
                    "Custa quase nada (segundos no editor + segundos no CI), pega ~80% do "
                    "que humano cansa de procurar em review, padroniza estilo (sem mais "
                    "discussões eternas sobre tabs vs spaces), e em alguns casos pega "
                    "anti-patterns de segurança óbvios. Ignorar linter é como dirigir sem "
                    "espelhos, possível, mas por quê?"
                ),
                "body": (
                    "<h3>1. O que linters fazem</h3>"
                    "<p>Linters fazem <strong>análise estática</strong>: leem o código sem "
                    "executá-lo e procuram padrões. Categorias:</p>"
                    "<ul>"
                    "<li><strong>Estilo</strong>: indentação, naming, comprimento de linha, "
                    "ordem de imports.</li>"
                    "<li><strong>Bugs simples</strong>: variável não usada, comparação errada "
                    "de tipo, função sem retorno em path.</li>"
                    "<li><strong>Anti-patterns</strong>: uso de <code>eval()</code>, "
                    "regex catastrófico, mutável default arg, hardcoded password.</li>"
                    "<li><strong>Performance</strong>: list comprehension preferida, evitar "
                    "concatenação em loop.</li>"
                    "<li><strong>Type checking</strong> (mypy, tsc): tipos coerentes em "
                    "linguagens com hint.</li>"
                    "</ul>"
                    "<p>Linters NÃO substituem SAST (mas a fronteira é borrada hoje, "
                    "Bandit/Semgrep cobrem ambos).</p>"

                    "<h3>2. Linters por linguagem</h3>"
                    "<h4>2.1 Python</h4>"
                    "<ul>"
                    "<li><strong>Ruff</strong>: novo padrão. Escrito em Rust. Substitui "
                    "<code>flake8</code>, <code>isort</code>, <code>pyupgrade</code>, "
                    "<code>autoflake</code>, <code>black</code>, em 1 ferramenta, 10-100x "
                    "mais rápido. Lint + format.</li>"
                    "<li><strong>mypy</strong> / <strong>pyright</strong>: type checking.</li>"
                    "<li><strong>Bandit</strong>: foco em segurança.</li>"
                    "</ul>"
                    "<pre><code># pyproject.toml\n"
                    "[tool.ruff]\n"
                    "line-length = 100\n"
                    "target-version = \"py312\"\n"
                    "[tool.ruff.lint]\n"
                    "select = [\n"
                    "  \"E\", \"W\",   # pycodestyle\n"
                    "  \"F\",         # pyflakes\n"
                    "  \"I\",         # isort\n"
                    "  \"N\",         # pep8-naming\n"
                    "  \"UP\",        # pyupgrade\n"
                    "  \"B\",         # bugbear\n"
                    "  \"S\",         # bandit\n"
                    "  \"SIM\",       # simplify\n"
                    "]\n"
                    "ignore = [\"E501\"]   # justifique cada um</code></pre>"
                    "<h4>2.2 JavaScript/TypeScript</h4>"
                    "<ul>"
                    "<li><strong>ESLint</strong>: o padrão; com plugins (typescript-eslint, "
                    "react, next, security).</li>"
                    "<li><strong>Prettier</strong>: formatação opinativa.</li>"
                    "<li><strong>tsc --noEmit</strong>: type check.</li>"
                    "<li><strong>Biome</strong>: alternativa em Rust (rápida, integra "
                    "lint+format).</li>"
                    "</ul>"
                    "<h4>2.3 Go</h4>"
                    "<ul>"
                    "<li><strong>golangci-lint</strong>: agrega 50+ linters (errcheck, "
                    "govet, ineffassign, gosec, staticcheck).</li>"
                    "<li><strong>gofmt</strong>/<strong>goimports</strong>: formatação "
                    "padrão.</li>"
                    "</ul>"
                    "<h4>2.4 Shell/Bash</h4>"
                    "<ul>"
                    "<li><strong>shellcheck</strong>: o padrão. Pega "
                    "<code>$var</code> não-quoted, <code>cd $dir &amp;&amp; rm</code>, "
                    "etc.</li>"
                    "<li><strong>shfmt</strong>: formatação.</li>"
                    "</ul>"
                    "<h4>2.5 Outros</h4>"
                    "<ul>"
                    "<li><strong>YAML</strong>: <code>yamllint</code>.</li>"
                    "<li><strong>Markdown</strong>: <code>markdownlint</code>.</li>"
                    "<li><strong>JSON</strong>: <code>jq</code> + schemas.</li>"
                    "<li><strong>SQL</strong>: <code>sqlfluff</code>.</li>"
                    "</ul>"

                    "<h3>3. Linters de IaC</h3>"
                    "<h4>3.1 Dockerfile</h4>"
                    "<p><strong>hadolint</strong>: pega anti-patterns Docker.</p>"
                    "<pre><code>$ hadolint Dockerfile\n"
                    "Dockerfile:5 DL3008 Pin versions in apt-get install. Instead of `apt install foo`,\n"
                    "use `apt install foo=1.2.3`.\n"
                    "Dockerfile:7 DL3009 Delete the apt-get lists after installing.\n"
                    "Dockerfile:10 DL3025 Use arguments JSON notation for CMD and ENTRYPOINT.</code></pre>"
                    "<h4>3.2 Terraform</h4>"
                    "<ul>"
                    "<li><strong>tflint</strong>: lint específico de Terraform; tem "
                    "rulesets por provider (aws-tflint detecta instance type inválido, "
                    "ami inexistente).</li>"
                    "<li><strong>tfsec</strong> / <strong>checkov</strong>: security "
                    "(bucket público, sg 0.0.0.0/0, encryption desabilitada).</li>"
                    "<li><strong>terraform fmt</strong>: formatação nativa.</li>"
                    "</ul>"
                    "<h4>3.3 Kubernetes</h4>"
                    "<ul>"
                    "<li><strong>kubeval</strong> / <strong>kubeconform</strong>: schema "
                    "validation.</li>"
                    "<li><strong>kube-linter</strong>: best practices "
                    "(securityContext, resource limits, liveness probe).</li>"
                    "<li><strong>polaris</strong>: similar.</li>"
                    "<li><strong>checkov</strong>: também cobre K8s manifests + Helm.</li>"
                    "</ul>"
                    "<h4>3.4 Ansible</h4>"
                    "<p><strong>ansible-lint</strong>: detecta tasks sem nome, "
                    "<code>shell</code> sem <code>creates</code>, <code>become</code> "
                    "redundante, etc.</p>"

                    "<h3>4. Pre-commit + CI: defesa em camadas</h3>"
                    "<p>Padrão moderno: rodar tudo localmente antes do commit "
                    "(<strong>pre-commit framework</strong>) e novamente no CI:</p>"
                    "<pre><code># .pre-commit-config.yaml\n"
                    "repos:\n"
                    "  - repo: https://github.com/astral-sh/ruff-pre-commit\n"
                    "    rev: v0.5.0\n"
                    "    hooks:\n"
                    "      - id: ruff       # lint\n"
                    "        args: [--fix]\n"
                    "      - id: ruff-format\n"
                    "  - repo: https://github.com/hadolint/hadolint\n"
                    "    rev: v2.13.0-beta\n"
                    "    hooks:\n"
                    "      - id: hadolint-docker\n"
                    "  - repo: https://github.com/koalaman/shellcheck-precommit\n"
                    "    rev: v0.10.0\n"
                    "    hooks:\n"
                    "      - id: shellcheck\n"
                    "  - repo: https://github.com/gitleaks/gitleaks\n"
                    "    rev: v8.18.0\n"
                    "    hooks:\n"
                    "      - id: gitleaks\n"
                    "  - repo: https://github.com/aquasecurity/tfsec\n"
                    "    rev: v1.28.0\n"
                    "    hooks:\n"
                    "      - id: tfsec</code></pre>"
                    "<pre><code>$ pre-commit install   # instala hook git\n"
                    "$ pre-commit run --all-files   # roda em todo repo\n"
                    "ruff..............................Passed\n"
                    "hadolint..........................Failed\n"
                    "  Dockerfile:7 DL3009 Delete apt lists after install</code></pre>"
                    "<p>No CI, repita: <code>pre-commit run --all-files</code>. "
                    "Devs podem pular pre-commit local com <code>--no-verify</code>; CI "
                    "não pula.</p>"

                    "<h3>5. Auto-fix</h3>"
                    "<p>Muitos linters têm <code>--fix</code>:</p>"
                    "<ul>"
                    "<li><code>ruff check --fix</code>: organiza imports, remove unused.</li>"
                    "<li><code>ruff format</code>: formata estilo black-like.</li>"
                    "<li><code>prettier --write</code>: formata JS/TS/CSS/JSON/MD.</li>"
                    "<li><code>terraform fmt -recursive</code>: formata HCL.</li>"
                    "</ul>"
                    "<p>Combine com bot no PR: lefthook, treefmt, ou um GitHub Action "
                    "que faz commit do fix.</p>"

                    "<h3>6. Falsos positivos: como lidar</h3>"
                    "<p>Suprimir é legítimo, mas <em>com motivo no comentário</em>:</p>"
                    "<pre><code>SQL = (\n"
                    "    \"SELECT * FROM users WHERE id IN (\" + ids_csv + \")\"  # noqa: S608 - ids_csv é validado em validate_ids() acima\n"
                    ")</code></pre>"
                    "<p><code># noqa</code> sem motivo vira ruído permanente. Audite "
                    "supressões periodicamente (<code>grep -r 'noqa' .</code>).</p>"

                    "<h3>7. Linter no editor</h3>"
                    "<p>Erro aparece enquanto você digita. Reduz mental "
                    "context-switch (não precisa rodar CI para descobrir typo). VS Code, "
                    "JetBrains, Vim/Neovim, Emacs, todos suportam LSP, ruff-lsp, ESLint, "
                    "tflint, etc.</p>"

                    "<h3>8. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Desativar todas as regras</strong>: linter inútil. "
                    "Migre legados ativando regras gradualmente, não desligando tudo.</li>"
                    "<li><strong>Suprimir sem comentar</strong>: lixo permanente.</li>"
                    "<li><strong>Linter só no CI</strong>: feedback de minutos. Adicione "
                    "pre-commit + editor.</li>"
                    "<li><strong>Discussão sobre estilo em review</strong>: deixe para "
                    "linter/formatter. Humano revisa lógica, segurança, design.</li>"
                    "<li><strong>Auto-fix sem revisar</strong>: cuidado com fixers "
                    "agressivos que mudam semântica.</li>"
                    "</ul>"
                ),
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
            },
            "materials": [
                m("pre-commit", "https://pre-commit.com/", "tool", ""),
                m("Ruff (Python)", "https://docs.astral.sh/ruff/", "tool", ""),
                m("hadolint (Dockerfile)", "https://github.com/hadolint/hadolint", "tool", ""),
                m("tflint", "https://github.com/terraform-linters/tflint", "tool", ""),
                m("Checkov (IaC security)", "https://www.checkov.io/", "tool", ""),
                m("ESLint", "https://eslint.org/docs/latest/", "docs", ""),
            ],
            "questions": [
                q("hadolint detecta:",
                  "Más práticas em Dockerfiles.",
                  ["Erros JS.", "Bugs de Java.", "DNS quebrado."],
                  "Pega coisas como `apt-get install` sem `--no-install-recommends`, falta de USER."),
                q("Linter difere de SAST porque:",
                  "Linter foca em estilo/erros simples; SAST em vulnerabilidades.",
                  ["São idênticos.", "Linter é para JS apenas.", "SAST não roda em CI."],
                  "Linha entre os dois é borrada hoje (Bandit, Semgrep cobrem ambos)."),
                q("pre-commit serve para:",
                  "Rodar verificações antes do commit.",
                  ["Substituir CI.", "Apagar branch.", "Compactar logs."],
                  "Feedback em segundos. CI ainda valida no servidor (defesa em camadas)."),
                q("Configurar linter no CI evita:",
                  "Que erros de estilo quebrem o build/peças posteriores.",
                  ["Custos.", "Latência.", "Backup automático."],
                  "Style guide automatizado é menos cansativo que review humano."),
                q("Falsos positivos podem ser:",
                  "Suprimidos com comentários # noqa, // eslint-disable, etc.",
                  ["Apenas ignorados em prod.", "Erros reais.", "Bugs do compilador."],
                  "Sempre justifique no comentário; supressão sem motivo vira lixo."),
                q("Por que não desativar todas as regras?",
                  "Reduz a utilidade do linter quase a zero.",
                  ["É rápido.", "Reduz custo.", "Faz o CI passar."],
                  "Time perde o feedback. Em legados, ative gradualmente em vez de desligar tudo."),
                q("ruff substitui:",
                  "Vários linters Python (flake8, isort, etc.) com performance maior.",
                  ["O Python.", "O pytest.", "O pip."],
                  "Escrito em Rust; lint + format. Reduz minutos de CI para segundos."),
                q("Lint em IaC importa porque:",
                  "Erros em IaC se traduzem em erros de produção.",
                  ["Acelera plan.", "Reduz custo.", "Bloqueia o IAM."],
                  "tfsec/checkov barram bucket público, role com '*' antes do plan."),
                q("Editor integration de linter:",
                  "Mostra problemas em tempo real, encurtando o feedback.",
                  ["É opcional para juniores.", "Apenas decora a IDE.", "Substitui CI."],
                  "Erros aparecem enquanto digita. Reduz tempo de mental context-switch."),
                q("Auto-fix em linters:",
                  "Aplica correções automaticamente quando seguro.",
                  ["Quebra commits.", "Apaga arquivos.", "Reverte código."],
                  "Bom para imports, formatação. Tenha cuidado com regras semânticas (ex.: cuidado com fixers que mudam comportamento)."),
            ],
        },
        # =====================================================================
        # 3.7 SAST
        # =====================================================================
        {
            "title": "SAST",
            "summary": "Análise estática de código no pipeline.",
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
                "body": (
                    "<h3>1. Como SAST funciona internamente</h3>"
                    "<p>Etapas típicas:</p>"
                    "<ol>"
                    "<li><strong>Parsing</strong>: código vira AST (Abstract Syntax Tree).</li>"
                    "<li><strong>Análise de fluxo de controle (CFG)</strong>: como execução "
                    "pula entre blocos.</li>"
                    "<li><strong>Análise de fluxo de dados (taint)</strong>: rastreia "
                    "valores 'sujos' (input do usuário) até pontos perigosos (SQL exec, "
                    "shell, eval). Se chegar sem sanitização, é vulnerabilidade.</li>"
                    "<li><strong>Aplicação de regras</strong>: padrões pré-definidos "
                    "(OWASP) ou custom.</li>"
                    "<li><strong>Reporte</strong>: SARIF, JSON, HTML.</li>"
                    "</ol>"
                    "<p>Exemplo conceitual de taint analysis:</p>"
                    "<pre><code>def view(request):\n"
                    "    user_id = request.GET.get('id')        # source: tainted\n"
                    "    query = f\"SELECT * FROM u WHERE id={user_id}\"   # propaga taint\n"
                    "    cursor.execute(query)                  # sink: SQL injection!</code></pre>"
                    "<p>Sanitização interrompe taint:</p>"
                    "<pre><code>user_id = int(request.GET.get('id'))  # cast → não tainted (escopo)\n"
                    "cursor.execute(\"SELECT * FROM u WHERE id=%s\", [user_id])  # parametrizado, ok</code></pre>"

                    "<h3>2. Tipos de regras</h3>"
                    "<ul>"
                    "<li><strong>Pattern simples</strong>: regex/AST básico (Bandit "
                    "<code>B102</code> = uso de <code>exec()</code>).</li>"
                    "<li><strong>Taint analysis</strong>: source → sanitizer → sink. "
                    "Mais preciso e mais caro computacionalmente.</li>"
                    "<li><strong>Symbolic execution</strong>: simula execução com "
                    "valores simbólicos. Encontra bugs profundos.</li>"
                    "<li><strong>Custom rules</strong>: você escreve para seu domínio "
                    "(ex.: 'log que contém variável <code>cpf</code> = bloqueia merge').</li>"
                    "</ul>"

                    "<h3>3. Ferramentas open source</h3>"
                    "<h4>3.1 Semgrep</h4>"
                    "<p>Padrão moderno. Sintaxe simples (YAML + pattern). Multi-linguagem. "
                    "Regras OWASP prontas, e custom é fácil:</p>"
                    "<pre><code># .semgrep/no-print-in-prod.yml\n"
                    "rules:\n"
                    "  - id: no-print\n"
                    "    languages: [python]\n"
                    "    severity: WARNING\n"
                    "    message: \"Use logging em vez de print()\"\n"
                    "    pattern: print(...)\n"
                    "    paths:\n"
                    "      include: ['app/**/*.py']\n"
                    "      exclude: ['tests/**', 'scripts/**']</code></pre>"
                    "<pre><code>$ semgrep --config p/owasp-top-ten\n"
                    "$ semgrep --config p/python --config .semgrep/\n"
                    "$ semgrep --config auto   # detecta linguagem e usa registry</code></pre>"
                    "<h4>3.2 Bandit (Python)</h4>"
                    "<pre><code>$ bandit -r app/\n"
                    "&gt;&gt; Issue: [B201:flask_debug_true] A Flask app appears to be run with debug=True\n"
                    "   Severity: High   Confidence: Medium\n"
                    "   Location: app.py:42</code></pre>"
                    "<h4>3.3 CodeQL (GitHub)</h4>"
                    "<p>Constrói banco de fatos sobre seu código; queries SQL-like buscam "
                    "padrões. Muito poderoso, free para repos públicos.</p>"
                    "<pre><code>// query CodeQL\n"
                    "import python\n"
                    "from FunctionDef f\n"
                    "where f.getName() = \"login\" and not exists(f.getBody().getAStmt())\n"
                    "select f, \"Função login sem corpo\"</code></pre>"
                    "<h4>3.4 Outros</h4>"
                    "<ul>"
                    "<li><strong>Brakeman</strong>: Ruby/Rails.</li>"
                    "<li><strong>gosec</strong>: Go.</li>"
                    "<li><strong>SpotBugs</strong>/Find-Sec-Bugs: Java.</li>"
                    "<li><strong>Sonarqube/SonarCloud</strong>: comercial com freemium; "
                    "engloba SAST + qualidade de código.</li>"
                    "</ul>"

                    "<h3>4. Integração no pipeline</h3>"
                    "<p>Idealmente como check obrigatório no PR:</p>"
                    "<pre><code># GitHub Actions\n"
                    "- name: Semgrep\n"
                    "  uses: returntocorp/semgrep-action@v1\n"
                    "  with:\n"
                    "    config: p/owasp-top-ten\n"
                    "    auditOn: push\n"
                    "    publishToken: ${{ secrets.SEMGREP_APP_TOKEN }}</code></pre>"
                    "<p>Para evitar 'mar de ruído' em legado, configure <strong>diff-only</strong>: "
                    "comente no PR apenas achados em <em>linhas tocadas neste PR</em>. Legado é tratado "
                    "em sprint de tech-debt, não bloqueia merge.</p>"
                    "<p>Regra de bloqueio:</p>"
                    "<ul>"
                    "<li><strong>Critical/High</strong>: bloqueia merge.</li>"
                    "<li><strong>Medium</strong>: vira issue automática, prazo sprint.</li>"
                    "<li><strong>Low/Info</strong>: backlog, não obriga.</li>"
                    "</ul>"

                    "<h3>5. Triagem de falsos positivos</h3>"
                    "<p>Falsos positivos são normais, alguns padrões precisam contexto. "
                    "Crie processo:</p>"
                    "<ol>"
                    "<li>Triagem semanal por security champion ou squad rotativo.</li>"
                    "<li>Confirma que é FP, suprime com justificativa <strong>no código</strong> "
                    "(<code># nosec - input validado em validate()</code>).</li>"
                    "<li>Ou em arquivo de baseline (<code>.semgrepignore</code>).</li>"
                    "<li>Sempre revisita supressões antigas (auditoria trimestral).</li>"
                    "</ol>"
                    "<p>Importante: nunca suprima 'em massa' sem analisar. Vira tapa-buraco "
                    "que esconde achados reais.</p>"

                    "<h3>6. SAST vs DAST vs IAST vs SCA, complementares</h3>"
                    "<table>"
                    "<tr><th>Tipo</th><th>O que olha</th><th>Quando</th><th>Exemplo</th></tr>"
                    "<tr><td>SAST</td><td>Código (white box)</td><td>Pré-deploy/PR</td><td>Semgrep, CodeQL</td></tr>"
                    "<tr><td>DAST</td><td>App rodando (black box)</td><td>Staging/QA</td><td>OWASP ZAP, Burp</td></tr>"
                    "<tr><td>IAST</td><td>Agente em runtime</td><td>QA com tráfego</td><td>Contrast, Seeker</td></tr>"
                    "<tr><td>SCA</td><td>Dependências</td><td>Pre-deploy/contínuo</td><td>Trivy, Dependabot</td></tr>"
                    "<tr><td>Pentest</td><td>App + infra (humano)</td><td>Periódico</td><td>Consultoria/red team</td></tr>"
                    "</table>"
                    "<p>Use vários, cada um pega coisas diferentes:</p>"
                    "<ul>"
                    "<li>SAST pega lógica que DAST nunca testará (path raro).</li>"
                    "<li>DAST pega misconfig de servidor/runtime que SAST não vê.</li>"
                    "<li>SCA pega CVE em deps que SAST/DAST ignoram.</li>"
                    "<li>Pentest combina criatividade humana + ferramentas + lógica de negócio.</li>"
                    "</ul>"

                    "<h3>7. Custom rules: o real diferencial</h3>"
                    "<p>Regras default cobrem OWASP top 10, bom, mas todo mundo tem. "
                    "Custom rules pegam padrões internos:</p>"
                    "<pre><code>rules:\n"
                    "  - id: no-direct-db-cursor\n"
                    "    pattern: connection.cursor()\n"
                    "    message: \"Use UnitOfWork em vez de cursor direto. Ver ADR-12.\"\n"
                    "    severity: ERROR\n"
                    "    languages: [python]\n"
                    "    paths: { include: ['app/**'], exclude: ['app/db/uow.py'] }\n"
                    "\n"
                    "  - id: log-sem-mascarar-cpf\n"
                    "    pattern-either:\n"
                    "      - pattern: logger.info(f\"...{$X.cpf}...\")\n"
                    "      - pattern: logger.info(f\"...{$X.email}...\")\n"
                    "    message: \"PII em log, use mask_pii()\"\n"
                    "    severity: ERROR\n"
                    "    languages: [python]</code></pre>"
                    "<p>Comece pequeno: 3-5 regras críticas para a empresa. Cresça com "
                    "tempo. Cada regra é menos um bug recorrente em review.</p>"

                    "<h3>8. Métricas úteis</h3>"
                    "<ul>"
                    "<li><strong>MTTR por severidade</strong>: tempo médio de remediação.</li>"
                    "<li><strong>Taxa de FP</strong>: % de achados que viram supressão "
                    "justificada. Se &gt;30%, regras precisam ajuste.</li>"
                    "<li><strong>Achados / KLOC novo</strong>: tendência da base.</li>"
                    "<li><strong>Tempo de análise no CI</strong>: SAST &gt;5min vira "
                    "fricção.</li>"
                    "</ul>"

                    "<h3>9. Limitações de SAST</h3>"
                    "<p>SAST não enxerga:</p>"
                    "<ul>"
                    "<li>Misconfig de servidor/runtime (debug=True via env var).</li>"
                    "<li>Falhas de auth/authz em runtime.</li>"
                    "<li>DoS, race conditions em produção.</li>"
                    "<li>Logic flaws complexas (preço negativo aceito).</li>"
                    "<li>Vulnerabilidade em serviço terceiro chamado por API.</li>"
                    "</ul>"
                    "<p>Por isso: combine com DAST, observabilidade, threat modeling, "
                    "pentest. Defesa em profundidade.</p>"

                    "<h3>10. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Comprar ferramenta cara, deixar gerar relatório de "
                    "1000 páginas, ninguém ler</strong>: integre no PR ou esqueça.</li>"
                    "<li><strong>Bloquear todos achados de uma vez em legado</strong>: "
                    "ninguém merge nada. Use baseline + diff-only.</li>"
                    "<li><strong>Suprimir todos os FP sem ler</strong>: vai esconder "
                    "achado real.</li>"
                    "<li><strong>Apenas regras default</strong>: pega o óbvio, perde "
                    "padrões internos.</li>"
                    "<li><strong>Não atualizar regras</strong>: novos patterns aparecem; "
                    "atualize semanalmente.</li>"
                    "</ul>"
                ),
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
            },
            "materials": [
                m("OWASP Source Code Analysis Tools", "https://owasp.org/www-community/Source_Code_Analysis_Tools", "docs", ""),
                m("Semgrep", "https://semgrep.dev/docs/", "tool", ""),
                m("Bandit (Python)", "https://bandit.readthedocs.io/", "tool", ""),
                m("CodeQL (GitHub)", "https://codeql.github.com/", "tool", ""),
                m("SonarQube", "https://www.sonarsource.com/products/sonarqube/", "tool", ""),
                m("OWASP Top 10", "https://owasp.org/www-project-top-ten/", "docs", "Categorias guia para SAST."),
            ],
            "questions": [
                q("SAST acrônimo significa:",
                  "Static Application Security Testing.",
                  ["System Audit Software Tool.", "Single Access Static Token.", "Server Application Security Test."],
                  "'Static' = sem rodar o app. Diferente de DAST (Dynamic) e IAST (Interactive)."),
                q("Diferença entre SAST e DAST:",
                  "SAST analisa o código sem rodar; DAST analisa app rodando.",
                  ["São idênticos.", "DAST analisa código apenas.", "SAST exige produção."],
                  "Use ambos: SAST no PR, DAST contra staging. Cada um pega coisas que o outro não vê."),
                q("Bandit detecta:",
                  "Padrões inseguros em Python.",
                  ["Apenas YAML.", "Apenas Java.", "DNS quebrado."],
                  "Eval, hardcoded password, uso de tempfile inseguro etc. Roda fácil em pre-commit."),
                q("Falso positivo em SAST:",
                  "Achado real do padrão, mas que não é vulnerabilidade no contexto.",
                  ["Bug do ferramenta.", "Sucesso garantido.", "Logs de info."],
                  "Ex.: SQL string concat onde input é constante interna. Suprima e documente."),
                q("Para trecho legado já mitigado:",
                  "Documente a exceção e suprima com comentário/regra.",
                  ["Reescreva todo o app.", "Ignore SAST.", "Use só DAST."],
                  "Comentário deve explicar a mitigação. Auditoria periódica re-avalia."),
                q("CodeQL roda:",
                  "Queries em representações de código (DBs).",
                  ["Apenas regex.", "Apenas no servidor SQL.", "Apenas em prod."],
                  "Constrói banco de fatos sobre o código; queries SQL-like buscam padrões. Free para repos públicos."),
                q("SAST no PR é eficaz porque:",
                  "Dá feedback antes do merge, com escopo pequeno.",
                  ["Apenas no fim.", "Apenas em prod.", "Não faz diferença."],
                  "Diff-only reduz ruído. Bloquear merge em High garante que não acumula dívida."),
                q("Limitação de SAST:",
                  "Não enxerga problemas runtime/configuração.",
                  ["Não detecta SQLi.", "Não roda em Java.", "Apenas YAML."],
                  "Misconfig de servidor, falhas de auth em runtime, DoS, fora do escopo."),
                q("Métrica útil para SAST:",
                  "MTTR (mean time to remediate) por severidade.",
                  ["Quantidade de linhas.", "Tamanho do PR.", "Número de devs."],
                  "Mostra se time está realmente endereçando ou só ignorando."),
                q("Custom rules em Semgrep:",
                  "Permitem capturar padrões específicos do seu domínio.",
                  ["Apenas SQL.", "Apenas YAML.", "Desabilitam o tool."],
                  "Sintaxe simples (YAML + pattern). Útil para exigir uso de função interna padrão."),
            ],
        },
        # =====================================================================
        # 3.8 SCA
        # =====================================================================
        {
            "title": "SCA",
            "summary": "Verificar se as bibliotecas que seu código usa têm vírus ou falhas.",
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
                "body": (
                    "<h3>1. SBOM (Software Bill of Materials)</h3>"
                    "<p>Lista de <em>todas</em> dependências (diretas e transitivas) com "
                    "versão e licença. É o ingrediente para qualquer análise. Em ambientes "
                    "regulados (governo dos EUA via Executive Order 14028, automotive, "
                    "médicos), SBOM é obrigação contratual.</p>"
                    "<p>Formatos:</p>"
                    "<ul>"
                    "<li><strong>CycloneDX</strong>: OWASP, mais focado em segurança.</li>"
                    "<li><strong>SPDX</strong>: Linux Foundation, mais focado em "
                    "compliance/licenças.</li>"
                    "</ul>"
                    "<p>Ferramentas: <code>syft</code> (Anchore), <code>cdxgen</code> "
                    "(OWASP), <code>trivy</code>:</p>"
                    "<pre><code>$ syft packages docker:nginx:latest -o cyclonedx-json &gt; sbom.json\n"
                    "$ syft dir:. -o spdx-json &gt; sbom.spdx.json</code></pre>"
                    "<p>SBOM atrelado ao artefato (referenciado no registry OCI) cria "
                    "trilha auditável: você sabe o que entregou.</p>"

                    "<h3>2. CVE, CVSS, EPSS, KEV</h3>"
                    "<ul>"
                    "<li><strong>CVE</strong> (Common Vulnerabilities and Exposures): "
                    "ID único. Ex.: <code>CVE-2024-1234</code>.</li>"
                    "<li><strong>CVSS</strong>: score 0-10 de severidade. Vetor "
                    "(<code>AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H</code>) + base score.</li>"
                    "<li><strong>EPSS</strong> (Exploit Prediction Scoring System): "
                    "probabilidade de ser explorado nos próximos 30 dias. Ajuda a priorizar.</li>"
                    "<li><strong>KEV</strong> (Known Exploited Vulnerabilities): catálogo "
                    "CISA de CVEs <em>já</em> exploradas em ataques reais. KEV = ação "
                    "imediata.</li>"
                    "</ul>"
                    "<p>Priorização moderna: CVSS &gt;= 7 + KEV ou EPSS alto = critical. "
                    "CVSS sozinho leva a fadiga (centenas de '7s' irrelevantes).</p>"

                    "<h3>3. Ferramentas</h3>"
                    "<table>"
                    "<tr><th>Ferramenta</th><th>Pontos fortes</th></tr>"
                    "<tr><td>Trivy</td><td>CLI grátis; escaneia FS, imagens, IaC, K8s. SBOM + CVEs. Bom em CI.</td></tr>"
                    "<tr><td>Grype</td><td>Pareado com Syft (mesmo dono). Foco em CVEs.</td></tr>"
                    "<tr><td>Dependabot (GitHub)</td><td>Nativo. PR de update automático. Limitado em config avançada.</td></tr>"
                    "<tr><td>Renovate</td><td>Mais configurável; agrupa updates, segue regras complexas.</td></tr>"
                    "<tr><td>Snyk</td><td>Comercial freemium; bom UX, sugere fix.</td></tr>"
                    "<tr><td>OSV-Scanner</td><td>Google; usa OSV.dev; rápido e gratuito.</td></tr>"
                    "<tr><td>npm audit / pip-audit</td><td>Nativos; básicos.</td></tr>"
                    "<tr><td>OWASP Dependency-Check</td><td>Java; bom para empresas legacy.</td></tr>"
                    "</table>"

                    "<h3>4. Trivy: ferramenta vital</h3>"
                    "<pre><code>$ trivy fs .                     # escaneia diretório\n"
                    "$ trivy image nginx:1.25.3        # escaneia imagem\n"
                    "$ trivy config terraform/         # IaC\n"
                    "$ trivy k8s --severity CRITICAL --all-namespaces\n"
                    "\n"
                    "# Falhar build em criticais\n"
                    "$ trivy image --severity CRITICAL --exit-code 1 myapp:dev\n"
                    "\n"
                    "# Gerar SBOM\n"
                    "$ trivy image --format cyclonedx --output sbom.json myapp:dev\n"
                    "\n"
                    "# Ignorar específicos (com motivo!)\n"
                    "# .trivyignore:\n"
                    "# CVE-2024-12345  # não-exploitable em nosso uso\n"
                    "</code></pre>"

                    "<h3>5. Política de remediação (SLA)</h3>"
                    "<p>Sem prazo, ninguém prioriza. Documente em SECURITY.md:</p>"
                    "<pre><code>| Severidade           | SLA Prod | SLA Staging |\n"
                    "|----------------------|----------|-------------|\n"
                    "| Critical em KEV      | 24-72h   | 7d          |\n"
                    "| Critical             | 7d       | 14d         |\n"
                    "| High + EPSS &gt;= 0.5    | 14d      | 30d         |\n"
                    "| High                 | 30d      | 60d         |\n"
                    "| Medium               | 90d      | 180d        |\n"
                    "| Low                  | 180d     | best-effort |</code></pre>"

                    "<h3>6. Lockfiles: a base de tudo</h3>"
                    "<p>Lockfile fixa versões exatas e hashes:</p>"
                    "<ul>"
                    "<li>Python: <code>poetry.lock</code>, <code>pdm.lock</code>, "
                    "<code>requirements.txt</code> com pinning + hashes.</li>"
                    "<li>JS: <code>package-lock.json</code>, <code>yarn.lock</code>, "
                    "<code>pnpm-lock.yaml</code>.</li>"
                    "<li>Go: <code>go.sum</code>.</li>"
                    "<li>Rust: <code>Cargo.lock</code>.</li>"
                    "<li>Ruby: <code>Gemfile.lock</code>.</li>"
                    "</ul>"
                    "<p><strong>SEMPRE commite o lockfile</strong>. Sem ele:</p>"
                    "<ul>"
                    "<li>Build não-reprodutível: dev e prod podem ter versões diferentes.</li>"
                    "<li>SCA confunde-se: relata CVE em versão que talvez não esteja "
                    "instalada.</li>"
                    "<li>Atacante pode swap silencioso por versão maliciosa em dependency "
                    "confusion.</li>"
                    "</ul>"
                    "<p>Use <code>--require-hashes</code> (pip) para validar integridade no "
                    "install, qualquer mudança de hash falha.</p>"

                    "<h3>7. Cadeia de suprimentos: além de CVE</h3>"
                    "<p>SCA pega 'biblioteca tem CVE conhecida'. Cadeia de suprimentos é mais "
                    "amplo:</p>"
                    "<ul>"
                    "<li><strong>Typosquatting</strong>: pacote malicioso com nome parecido "
                    "(<code>requests</code> vs <code>requets</code>). Defesa: revise deps "
                    "novas.</li>"
                    "<li><strong>Conta comprometida</strong>: mantenedor invadido publica "
                    "versão maliciosa. Famoso: <em>event-stream</em>, <em>colors.js</em>, "
                    "<em>node-ipc</em>. Defesa: pin por hash, mirror interno.</li>"
                    "<li><strong>Dependency confusion</strong>: package interno com mesmo "
                    "nome no público, pacote público é puxado. Defesa: scoping em registry "
                    "interno.</li>"
                    "<li><strong>Build infrastructure</strong>: comprometer pipeline para "
                    "injetar código (SolarWinds). Defesa: SLSA framework.</li>"
                    "<li><strong>Pacote 'protestware'</strong>: mantenedor sabota a própria "
                    "lib em protesto político. Defesa: pin de versão.</li>"
                    "</ul>"

                    "<h3>8. Dependabot configurado direito</h3>"
                    "<pre><code># .github/dependabot.yml\n"
                    "version: 2\n"
                    "updates:\n"
                    "  - package-ecosystem: pip\n"
                    "    directory: /\n"
                    "    schedule: { interval: weekly, day: monday }\n"
                    "    open-pull-requests-limit: 10\n"
                    "    groups:\n"
                    "      django:\n"
                    "        patterns: ['django*']\n"
                    "      dev-deps:\n"
                    "        dependency-type: development\n"
                    "    ignore:\n"
                    "      - dependency-name: 'numpy'\n"
                    "        versions: ['&gt;=2.0.0']  # major bump quebra; pin manual\n"
                    "  - package-ecosystem: docker\n"
                    "    directory: /\n"
                    "    schedule: { interval: weekly }\n"
                    "  - package-ecosystem: github-actions\n"
                    "    directory: /\n"
                    "    schedule: { interval: monthly }</code></pre>"
                    "<p>Sem <code>groups</code>, vc recebe 50 PRs por semana. Com, recebe "
                    "5, ainda atualiza tudo.</p>"

                    "<h3>9. CVEs em transitivas: o pesadelo do override</h3>"
                    "<p>Você usa <code>django</code>; <code>django</code> usa "
                    "<code>asgiref</code>; <code>asgiref</code> tem CVE. Ação?</p>"
                    "<ul>"
                    "<li>Avalie exploitabilidade no seu uso.</li>"
                    "<li>Tente atualizar pai (<code>django</code>), solução mais limpa.</li>"
                    "<li>Force versão da transitiva (npm <code>overrides</code>, pip "
                    "<code>--constraint</code>, Maven dependency management).</li>"
                    "<li>Aceite risco (com justificativa).</li>"
                    "<li>Substitua biblioteca pai (último recurso).</li>"
                    "</ul>"

                    "<h3>10. Resposta a CVE crítica em produção</h3>"
                    "<ol>"
                    "<li><strong>Inventário</strong>: SCA cruza SBOM com CVE. Quem usa? "
                    "Em quais ambientes?</li>"
                    "<li><strong>Avaliação</strong>: o caminho explorável existe na sua app? "
                    "(Log4Shell exigia logging de input não-sanitizado, mas era trivial.)</li>"
                    "<li><strong>Mitigação</strong>: WAF rule? Disable feature? Patch?</li>"
                    "<li><strong>Patch</strong>: bump da versão; testes; deploy.</li>"
                    "<li><strong>Detecção</strong>: logs/SIEM por exploração tentada.</li>"
                    "<li><strong>Comunicação</strong>: customers, regulator, status page.</li>"
                    "<li><strong>Postmortem</strong>: como descobrimos? Qual SLA atingido? "
                    "O que melhorar?</li>"
                    "</ol>"

                    "<h3>11. SLSA: framework de cadeia de suprimentos</h3>"
                    "<p>SLSA (Supply chain Levels for Software Artifacts) define níveis "
                    "1-4 de provenance:</p>"
                    "<ul>"
                    "<li>L1: build automatizado e documentado.</li>"
                    "<li>L2: source versionado, build serviço hospedado.</li>"
                    "<li>L3: build não-falsificável, isolamento.</li>"
                    "<li>L4: builds reproduzíveis, two-person review.</li>"
                    "</ul>"
                    "<p>Combine com Cosign + Rekor (Sigstore) para gerar atestados "
                    "verificáveis.</p>"
                ),
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
            },
            "materials": [
                m("OWASP Dependency-Check", "https://owasp.org/www-project-dependency-check/", "tool", ""),
                m("Trivy", "https://aquasecurity.github.io/trivy/", "tool", ""),
                m("GitHub Dependabot", "https://docs.github.com/code-security/dependabot", "docs", ""),
                m("Renovate", "https://docs.renovatebot.com/", "tool", ""),
                m("CVE database", "https://www.cve.org/", "docs", ""),
                m("OSV.dev", "https://osv.dev/", "docs", "Banco unificado de CVEs em open source."),
            ],
            "questions": [
                q("SCA significa:",
                  "Software Composition Analysis.",
                  ["Static Code Audit.", "System Check Authority.", "Secure Code Algo."],
                  "Foca em mapear e checar componentes (libs, frameworks)."),
                q("CVE é:",
                  "Identificador único para uma vulnerabilidade conhecida.",
                  ["Tipo de release.", "Comando shell.", "Parte do TLS."],
                  "Mantido por MITRE. Cada CVE tem descrição, refs, scoring CVSS."),
                q("Dependabot abre:",
                  "PRs automáticos de atualização de dependências.",
                  ["Tickets de suporte.", "Builds canário.", "Alertas DNS."],
                  "Configure agrupamento (group updates) para evitar 50 PRs por semana."),
                q("Trivy escaneia:",
                  "Imagens, IaC, e dependências em busca de CVEs e mis-configs.",
                  ["Apenas imagens.", "Apenas Python.", "Apenas YAML."],
                  "Multi-tool ótimo para CI: roda em segundos, fácil de integrar."),
                q("CVSS mede:",
                  "Severidade de vulnerabilidades (0-10).",
                  ["Latência de pacote.", "Tamanho do binário.", "Custo de cloud."],
                  "Vetor base inclui AV (vetor de ataque), C/I/A impactos. CVSS 9.0+ é Critical."),
                q("Lockfile (poetry.lock, package-lock):",
                  "Fixa versões exatas para reprodução.",
                  ["Apaga deps.", "Ignora deps.", "Substitui IAM."],
                  "Sem lockfile, atualizações silenciosas podem trazer bug, ou backdoor."),
                q("Política de patching deve definir:",
                  "Prazos de remediação por severidade.",
                  ["Apenas o time.", "Apenas custo.", "Apenas lint."],
                  "Sem SLA, nada vira prioridade. Documente no SECURITY.md."),
                q("Quando SCA aponta CVE em transitiva:",
                  "Avalie se há override possível ou alternativa.",
                  ["Ignore sempre.", "Apague o lockfile.", "Force-merge."],
                  "Em alguns ecossistemas você pode forçar versão (npm overrides, Maven dependencyManagement)."),
                q("OSV.dev é:",
                  "Banco aberto de vulnerabilidades de open source.",
                  ["Linter.", "Container registry.", "Cloud SQL."],
                  "Mantido pelo Google. APIs gratuitas; integra com Trivy, OSV-Scanner."),
                q("PR de update sem testes pode:",
                  "Quebrar produção mesmo com 'fix de segurança'.",
                  ["Sempre é seguro.", "Aumenta logs.", "Reduz custo."],
                  "Patch numa lib pode mudar API. Suite de testes razoável é pré-requisito."),
            ],
        },
        # =====================================================================
        # 3.9 Code Review
        # =====================================================================
        {
            "title": "Code Review",
            "summary": "O processo humano de revisar segurança antes do deploy.",
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
                "body": (
                    "<h3>1. Princípios de PR/MR de qualidade</h3>"
                    "<h4>1.1 Tamanho importa</h4>"
                    "<p>Estatística repetidamente confirmada (Google, Microsoft, Meta): "
                    "qualidade de review cai dramaticamente acima de ~200 linhas. PRs de "
                    "1000+ linhas recebem ~5% mais aprovação rapida e ~50% mais bugs em "
                    "produção comparado a 200-linha PRs.</p>"
                    "<p>Se vc tem PR grande, considere quebrar em:</p>"
                    "<ul>"
                    "<li>PR 1: refactor neutro (rename, mover arquivos).</li>"
                    "<li>PR 2: nova interface vazia.</li>"
                    "<li>PR 3: implementação.</li>"
                    "<li>PR 4: integração.</li>"
                    "</ul>"
                    "<h4>1.2 Contexto claro</h4>"
                    "<p>Reviewer não deveria adivinhar 'por que esta mudança'. Use template "
                    "de PR:</p>"
                    "<pre><code>## O que muda?\n"
                    "Adiciona rate limiting no endpoint /login.\n"
                    "\n"
                    "## Por quê?\n"
                    "Mitiga brute force. Issue: SEC-1234.\n"
                    "\n"
                    "## Como testar?\n"
                    "1. POST /login com 6 senhas erradas em &lt;15min\n"
                    "2. Próxima request deve retornar 429\n"
                    "\n"
                    "## Risco?\n"
                    "Usuário legítimo errando senha repetidamente. Mensagem clara orienta\n"
                    "esperar. WAF tem regra de bypass para IPs confiáveis.\n"
                    "\n"
                    "## Checklist\n"
                    "- [x] Testes adicionados\n"
                    "- [x] Logs sem PII\n"
                    "- [x] Documentação\n"
                    "- [ ] Verificar com SRE antes do deploy</code></pre>"
                    "<h4>1.3 Tom respeitoso</h4>"
                    "<p>'Aqui está confuso, talvez X?' &gt;&gt; 'Isso está errado'. "
                    "Conventional Comments dão estrutura:</p>"
                    "<pre><code>**suggestion**: poderia usar dataclass aqui, mais idiomático\n"
                    "**nitpick**: comma no final\n"
                    "**question**: por que não usar threadpool aqui?\n"
                    "**issue (blocking)**: SQL injection, use parametrização\n"
                    "**praise**: adorei essa abstração, simplifica muito</code></pre>"
                    "<p><em>Praise</em> é underrated. Reconheça boas decisões.</p>"
                    "<h4>1.4 Reviewer responde rápido</h4>"
                    "<p>PR parado é dinheiro queimando. SLA saudável: TTFR (Time to First "
                    "Review) &lt;4h em horário de trabalho. PRs urgentes &lt;1h. Cada hora "
                    "parado = autor perde contexto + ciclos.</p>"

                    "<h3>2. Checklist de segurança em PR</h3>"
                    "<p>Para PRs em código sensível (auth, dados, payment), valide "
                    "explicitamente:</p>"
                    "<ul>"
                    "<li><strong>Input validation</strong>: todo input do usuário é "
                    "validado/sanitizado antes de uso?</li>"
                    "<li><strong>Output encoding</strong>: HTML/SQL/shell escape onde "
                    "preciso?</li>"
                    "<li><strong>Authn/Authz</strong>: novo endpoint tem auth correto? "
                    "Authorization checa <em>recurso</em>, não só user logado?</li>"
                    "<li><strong>PII em logs</strong>: cpf, email, token não aparecem em "
                    "log? Use <code>mask_pii()</code>.</li>"
                    "<li><strong>Errors sem leak</strong>: stack trace não vai para "
                    "usuário; mensagem genérica para 500.</li>"
                    "<li><strong>Crypto correto</strong>: hash de senha com bcrypt/argon2 "
                    "(não md5); randomness com <code>secrets</code> (não <code>random</code>); "
                    "TLS verificado.</li>"
                    "<li><strong>Race condition</strong>: locks/transactions onde precisa.</li>"
                    "<li><strong>Dependências novas</strong>: SCA escaneou? Lib é mantida? "
                    "MIT/Apache, não GPL viral?</li>"
                    "<li><strong>Testes</strong>: caminhos novos cobertos? Edge cases? "
                    "Negativos?</li>"
                    "<li><strong>Backward compat</strong>: API existente não quebra? "
                    "Migração de DB tem rollback?</li>"
                    "</ul>"

                    "<h3>3. CODEOWNERS: quem revisa o quê</h3>"
                    "<pre><code># .github/CODEOWNERS\n"
                    "# Pessoas/equipes que reviewam por path\n"
                    "*                 @empresa/dev-platform\n"
                    "/security/        @empresa/sec-team\n"
                    "/payment/         @empresa/payments-squad @empresa/sec-team\n"
                    "/iac/terraform/   @empresa/sre @empresa/sec-team\n"
                    "*.md              @empresa/docs\n"
                    "**/migrations/    @empresa/dba</code></pre>"
                    "<p>Combinado com branch protection, GitHub <em>requer</em> aprovação "
                    "do dono do path. PR em <code>/payment/</code> não mergeia sem "
                    "<code>@empresa/payments-squad</code> + <code>@empresa/sec-team</code> "
                    "aprovarem. Garante olhar certo, sem precisar lembrar.</p>"

                    "<h3>4. Ferramentas no PR poupam tempo</h3>"
                    "<p>CI deve mostrar antes do reviewer humano olhar:</p>"
                    "<ul>"
                    "<li>Build passou?</li>"
                    "<li>Lint OK?</li>"
                    "<li>SAST/SCA sem high/critical?</li>"
                    "<li>Coverage não baixou? (codecov/coveralls)</li>"
                    "<li>Performance benchmarks ok? (Bencher)</li>"
                    "<li>Visual diff (Chromatic, Percy)?</li>"
                    "</ul>"
                    "<p>Reviewer humano pode focar em design e lógica, não em 'falta espaço "
                    "aqui'. Tempo economizado é gigante.</p>"

                    "<h3>5. Anti-patterns clássicos</h3>"
                    "<ul>"
                    "<li><strong>Rubber stamp</strong>: aprovar sem ler. Comum em PRs "
                    "do CTO ('quem sou eu para discordar?'). Métrica: % de PRs aprovados "
                    "com 0 comentários, se &gt;50%, suspeito.</li>"
                    "<li><strong>Bikeshedding</strong>: discutir cor do botão por dias, "
                    "ignorar SQL injection. Lei de Parkinson: tempo gasto em decisão é "
                    "inversamente proporcional à importância dela.</li>"
                    "<li><strong>PR de 3000 linhas</strong>: ninguém revisa de verdade. "
                    "Quebre.</li>"
                    "<li><strong>Reviewer único</strong> (gargalo): se só fulano revisa, "
                    "fulano vira ponto único de falha + queima.</li>"
                    "<li><strong>'Aprovar e pedir teste depois'</strong>: 'depois' não "
                    "vem.</li>"
                    "<li><strong>Comentários adversariais</strong>: 'isso é horrível'. "
                    "Tóxico, ineficaz.</li>"
                    "<li><strong>Re-write silencioso</strong>: reviewer reescreve em vez "
                    "de pedir mudança. Autor não aprende e fica ressentido.</li>"
                    "<li><strong>Aprovar sem CI verde</strong>: por quê o CI existe?</li>"
                    "<li><strong>Bloquear merge por preferência pessoal</strong>: blocking "
                    "deveria ser bug/segurança. Estilo é nitpick.</li>"
                    "</ul>"

                    "<h3>6. Métricas saudáveis</h3>"
                    "<ul>"
                    "<li><strong>TTFR (Time to First Review)</strong>: &lt;4h em PRs "
                    "normais.</li>"
                    "<li><strong>Time to Merge</strong>: &lt;24h em maioria.</li>"
                    "<li><strong>Comments por PR</strong>: 1-10 saudável; 0 = "
                    "rubber stamp; 50+ = PR muito grande ou autor desatento.</li>"
                    "<li><strong>Defect Escape Rate</strong>: bugs que passam review e "
                    "vão para prod. Se subindo, review está superficial.</li>"
                    "<li><strong>Review participation</strong>: Bus factor, só 1-2 "
                    "pessoas revisam? Distribua via round-robin.</li>"
                    "</ul>"
                    "<p>PRs &gt;3 dias parados degradam moral; mire em &lt;24h.</p>"

                    "<h3>7. Round-robin e ownership distribuído</h3>"
                    "<p>GitHub <em>auto-assignment</em> com round-robin previne fila "
                    "única. Em squad de 6 devs, todo PR aleatoriamente cai em alguém. "
                    "Combinado com CODEOWNERS para áreas críticas, distribui carga e "
                    "espalha conhecimento.</p>"

                    "<h3>8. Pair review e mob review</h3>"
                    "<p>Em mudanças muito críticas (auth, infra, migração), considere:</p>"
                    "<ul>"
                    "<li><strong>Pair review</strong>: reviewer e autor sentam juntos "
                    "(in-person ou call) e passam pelo PR. Discussão rica, decisões "
                    "rápidas.</li>"
                    "<li><strong>Mob review</strong>: 3-5 pessoas reviewam juntas. Para "
                    "decisão de design.</li>"
                    "<li><strong>Async + sync hybrid</strong>: async no GitHub, sync "
                    "rápido para resolver impasses.</li>"
                    "</ul>"

                    "<h3>9. Reviewer guia (cheat sheet do reviewer)</h3>"
                    "<ol>"
                    "<li>Leia descrição do PR antes do código.</li>"
                    "<li>Veja 'overview do diff' para entender escopo.</li>"
                    "<li>Identifique riscos: novo endpoint? nova lib? mudança em "
                    "auth?</li>"
                    "<li>Foque em: <em>design</em> &gt; <em>correção</em> &gt; "
                    "<em>manutenibilidade</em> &gt; <em>estilo</em>.</li>"
                    "<li>Comente perguntas, não comandos.</li>"
                    "<li>Aprove rápido se tudo ok. Não 'segure' por preciosismo.</li>"
                    "<li>Se grande demais para revisar bem, peça quebra.</li>"
                    "<li>Se discordar muito, agende sync, texto longo cria mal-entendido.</li>"
                    "</ol>"
                ),
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
            },
            "materials": [
                m("Google: Code Review Developer Guide", "https://google.github.io/eng-practices/review/", "article", ""),
                m("OWASP Code Review Guide", "https://owasp.org/www-project-code-review-guide/", "docs", ""),
                m("Conventional comments", "https://conventionalcomments.org/", "article", ""),
                m("PR template (GitHub)", "https://docs.github.com/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository", "docs", ""),
                m("ThoughtWorks: code review", "https://www.thoughtworks.com/insights/blog/code-review", "article", ""),
                m("CODEOWNERS docs", "https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners", "docs", ""),
            ],
            "questions": [
                q("PR pequeno é melhor porque:",
                  "Reduz tempo e probabilidade de bugs passarem.",
                  ["É mais difícil.", "Reduz qualidade.", "Aumenta merge conflicts."],
                  "Estudos mostram que diffs grandes recebem revisão superficial."),
                q("Checklist em PR ajuda a:",
                  "Não esquecer de validar pontos críticos.",
                  ["Substituir testes.", "Aumentar burocracia.", "Diminuir cobertura."],
                  "Bom em PRs sensíveis (auth, dados pessoais). Em PRs triviais, pode atrapalhar."),
                q("Reviewer deve:",
                  "Comentar com clareza, tom respeitoso e sugerir alternativa.",
                  ["Apenas aprovar.", "Apenas reprovar.", "Reescrever silenciosamente."],
                  "'Aqui está confuso, talvez X?' > 'errado'. Conventional comments dão estrutura."),
                q("Mudanças sensíveis precisam:",
                  "Revisão por alguém com perfil de segurança.",
                  ["Apenas IA.", "Auto-merge.", "Bypass de checks."],
                  "Use CODEOWNERS para garantir que sec-team é notificado."),
                q("Revisão sem testes é:",
                  "Risco, pode aprovar bug que CI pegaria.",
                  ["Eficiente.", "Mais rápido.", "Recomendado."],
                  "Coverage bot ajuda a barrar code novo sem teste."),
                q("Conventional comments:",
                  "Padroniza tipos de comentário (suggestion, nitpick, blocking).",
                  ["Forçam aprovação.", "Substituem CI.", "Apagam comentário."],
                  "Reviewer sinaliza intenção: 'nitpick' não bloqueia, 'blocking' bloqueia."),
                q("PR muito velho:",
                  "Junta merge conflicts e deveria ser refeito ou fragmentado.",
                  ["Vinho fica melhor.", "Sempre vai mergear.", "Substitui doc."],
                  "PRs > 1 semana parados raramente terminam bem. Quebre ou cancele."),
                q("Reviewer perceber dado sensível em log:",
                  "Pedir remoção/sanitização antes do merge.",
                  ["Aprovar e pedir depois.", "Ignorar.", "Adicionar mais."],
                  "Após log estar em produção, a chance de remover de SIEM/Datadog é zero."),
                q("Aprovação 'rubber stamp':",
                  "Aprovar sem ler, viola o propósito do review.",
                  ["É eficiente.", "É política.", "É lei."],
                  "Cria sensação de segurança falsa. Métricas (zero comments) podem revelar."),
                q("Métrica saudável:",
                  "Time-to-first-review baixo, sem fila eterna.",
                  ["Número de PRs aprovados sem ler.", "PRs gigantes.", "Reviews só do CTO."],
                  "TTFR < 4h para PRs urgentes; < 24h para o resto. Combine com round-robin."),
            ],
        },
        # =====================================================================
        # 3.10 Artifact Repositories
        # =====================================================================
        {
            "title": "Artifact Repositories",
            "summary": "Guardar suas versões de software em locais seguros.",
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
                "body": (
                    "<h3>1. Tipos de registries</h3>"
                    "<h4>1.1 Container registries</h4>"
                    "<ul>"
                    "<li><strong>AWS ECR</strong>: nativo AWS, IAM-based, scan integrado.</li>"
                    "<li><strong>GCP Artifact Registry (GAR)</strong>: substitui o GCR antigo. "
                    "Multi-formato (Docker, Maven, npm, etc.).</li>"
                    "<li><strong>Azure Container Registry (ACR)</strong>: nativo Azure.</li>"
                    "<li><strong>GitHub Container Registry (GHCR)</strong>: integrado a "
                    "GitHub Actions (token automático).</li>"
                    "<li><strong>Docker Hub</strong>: público, free com limites; pago para "
                    "ilimitado.</li>"
                    "<li><strong>Harbor</strong>: open source, self-hosted, RBAC, vuln scan, "
                    "replicação. Padrão em times K8s on-prem.</li>"
                    "<li><strong>Quay (Red Hat)</strong>: comercial; bom em ecossistema "
                    "OpenShift.</li>"
                    "</ul>"
                    "<h4>1.2 Generic / linguagens</h4>"
                    "<ul>"
                    "<li><strong>JFrog Artifactory</strong>: o veterano. Multi-formato "
                    "(Docker, Maven, npm, NuGet, PyPI, RPM, ...). Caro mas robusto.</li>"
                    "<li><strong>Sonatype Nexus</strong>: similar; OSS edition gratuita.</li>"
                    "<li><strong>GitHub Packages</strong>: integrado, multi-formato.</li>"
                    "<li><strong>GitLab Package Registry</strong>: idem.</li>"
                    "<li><strong>Cloudsmith</strong>: SaaS multi-formato.</li>"
                    "</ul>"
                    "<h4>1.3 Helm Charts</h4>"
                    "<p>Helm 3+ suporta OCI nativo, qualquer registry OCI (ECR, GHCR, "
                    "Harbor) guarda Helm chart. <code>ChartMuseum</code> ainda existe "
                    "para legacy.</p>"

                    "<h3>2. Padrões essenciais</h3>"
                    "<h4>2.1 Tags imutáveis</h4>"
                    "<p>Use <strong>SHA do commit</strong> ou <strong>versão semver</strong>. "
                    "<em>Nunca</em> em produção: <code>latest</code>, <code>main</code>, "
                    "<code>dev</code>, tags móveis.</p>"
                    "<pre><code># Bom\n"
                    "ghcr.io/empresa/app:v1.4.2\n"
                    "ghcr.io/empresa/app:abc1234   # commit SHA\n"
                    "ghcr.io/empresa/app@sha256:f0a1b2...   # digest absoluto\n"
                    "\n"
                    "# Ruim em prod\n"
                    "ghcr.io/empresa/app:latest\n"
                    "ghcr.io/empresa/app:dev</code></pre>"
                    "<p>Por digest é o ouro: <code>sha256:</code> é imutável e único, "
                    "mesmo se alguém republicar a tag.</p>"
                    "<p>Habilite <strong>tag immutability</strong> no registry "
                    "(ECR, Harbor, ACR), uma tag não pode ser sobrescrita.</p>"
                    "<h4>2.2 Assinatura com Cosign (Sigstore)</h4>"
                    "<p>Sem assinatura, atacante que comprometa o registry pode trocar "
                    "imagem. Com Cosign:</p>"
                    "<pre><code>$ cosign sign --yes ghcr.io/empresa/app:v1.4.2\n"
                    "Generating ephemeral keys... [OIDC: 'ci@empresa.com']\n"
                    "tlog entry written: rekor.sigstore.dev\n"
                    "\n"
                    "$ cosign verify ghcr.io/empresa/app:v1.4.2 \\\n"
                    "    --certificate-identity ci@empresa.com \\\n"
                    "    --certificate-oidc-issuer https://token.actions.githubusercontent.com\n"
                    "Verification for ghcr.io/empresa/app:v1.4.2 --\n"
                    "The following checks were performed on each of these signatures:\n"
                    "  - Signature was verified\n"
                    "  - Identity matched expectation</code></pre>"
                    "<p>Combine com admission controller K8s (<strong>Sigstore Policy "
                    "Controller</strong>, <strong>Kyverno</strong>) que rejeita imagens não "
                    "assinadas:</p>"
                    "<pre><code>apiVersion: kyverno.io/v1\n"
                    "kind: ClusterPolicy\n"
                    "metadata: { name: require-signed-images }\n"
                    "spec:\n"
                    "  validationFailureAction: Enforce\n"
                    "  rules:\n"
                    "    - name: check-signature\n"
                    "      match:\n"
                    "        any:\n"
                    "          - resources: { kinds: [Pod] }\n"
                    "      verifyImages:\n"
                    "        - imageReferences: ['ghcr.io/empresa/*']\n"
                    "          attestors:\n"
                    "            - keyless:\n"
                    "                subject: ci@empresa.com\n"
                    "                issuer: https://token.actions.githubusercontent.com</code></pre>"
                    "<h4>2.3 SBOM atrelado</h4>"
                    "<p>Anexe SBOM como referrer no registry OCI:</p>"
                    "<pre><code>$ syft ghcr.io/empresa/app:v1.4.2 -o cyclonedx-json &gt; sbom.json\n"
                    "$ cosign attach sbom --sbom sbom.json ghcr.io/empresa/app:v1.4.2\n"
                    "$ cosign attest --predicate sbom.json --type cyclonedx \\\n"
                    "    ghcr.io/empresa/app:v1.4.2</code></pre>"
                    "<p>Quando incident response precisar 'quem usa log4j 2.14?', você tem "
                    "SBOM por imagem.</p>"
                    "<h4>2.4 Provenance / SLSA</h4>"
                    "<p>Atestado de como foi construído. SLSA L3+ exige builder confiável. "
                    "GitHub Actions tem template oficial para gerar:</p>"
                    "<pre><code>- uses: slsa-framework/slsa-github-generator/.github/workflows/builder_container_slsa3.yml@v1.10.0</code></pre>"
                    "<p>Resultado: imagem vem com <code>provenance.intoto.jsonl</code> "
                    "verificável.</p>"

                    "<h3>3. RBAC e segregação</h3>"
                    "<ul>"
                    "<li><strong>Write apenas para CI</strong>: nenhum dev faz push direto. "
                    "Token de CI (OIDC, idealmente).</li>"
                    "<li><strong>Read scoped</strong>: por equipe/produto. Multi-tenant "
                    "usa namespaces.</li>"
                    "<li><strong>Pull em prod</strong>: pull-secret específico do cluster, "
                    "ao invés de credencial humana.</li>"
                    "<li><strong>Tokens curtos</strong>: OIDC com STS &gt; tokens "
                    "estáticos.</li>"
                    "<li><strong>Auditoria</strong>: registry log de quem puxou o quê e "
                    "quando. Útil em incidente.</li>"
                    "</ul>"

                    "<h3>4. Retenção e custo</h3>"
                    "<p>Sem política, registries acumulam GBs/TBs:</p>"
                    "<ul>"
                    "<li>Cada PR gera imagem (ABA-feature-test).</li>"
                    "<li>Builds antigos têm CVEs novos a cada semana.</li>"
                    "<li>Custo escala com storage.</li>"
                    "</ul>"
                    "<p>Política de retenção:</p>"
                    "<pre><code># Exemplo ECR lifecycle\n"
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
                    "<p>Reduz fatura e diminui superfície (atacante puxar imagem antiga "
                    "vulnerável).</p>"

                    "<h3>5. Pull-through cache</h3>"
                    "<p>Em vez de cada pipeline puxar do Docker Hub (rate limit gigante "
                    "no plano free), use registry interno como cache:</p>"
                    "<ul>"
                    "<li>Harbor proxy cache.</li>"
                    "<li>ECR pull-through (configurável para Docker Hub, Quay, GHCR).</li>"
                    "<li>Artifactory remote repository.</li>"
                    "</ul>"
                    "<p>Vantagens:</p>"
                    "<ul>"
                    "<li>Acelera builds (cache local).</li>"
                    "<li>Sobrevive a outage do upstream.</li>"
                    "<li>Auditoria de o que vem de fora.</li>"
                    "<li>Possibilidade de scan/quarentena antes de uso.</li>"
                    "</ul>"

                    "<h3>6. Vulnerability scanning contínuo</h3>"
                    "<p>Scan no push é útil, mas insuficiente, CVEs novos aparecem "
                    "depois. Configure:</p>"
                    "<ul>"
                    "<li>Re-scan periódico (Harbor schedule, Trivy operator no K8s, "
                    "ECR Enhanced Scanning).</li>"
                    "<li>Notificação quando imagem em produção fica vulnerável "
                    "(webhook → Slack).</li>"
                    "<li>Bloqueio de imagens com CVEs críticas em prod (admission policy).</li>"
                    "</ul>"

                    "<h3>7. Multi-arch images</h3>"
                    "<p>Hoje, ARM (Graviton, Apple Silicon) e AMD64 coexistem. "
                    "Build multi-arch:</p>"
                    "<pre><code>docker buildx build --platform linux/amd64,linux/arm64 \\\n"
                    "  --tag ghcr.io/empresa/app:v1.4.2 \\\n"
                    "  --push .</code></pre>"
                    "<p>Resultado: manifest list (multi-arch). Pull seleciona arch "
                    "automaticamente.</p>"

                    "<h3>8. Anti-patterns</h3>"
                    "<ul>"
                    "<li><strong>Apenas <code>latest</code> em prod</strong>: sem "
                    "rastreabilidade.</li>"
                    "<li><strong>Sem retenção</strong>: GBs/TBs acumulando.</li>"
                    "<li><strong>Push sem assinar</strong>: supply chain vulnerável.</li>"
                    "<li><strong>Token estático em registry</strong>: vaza, atacante puxa "
                    "tudo.</li>"
                    "<li><strong>Imagem em registry público</strong> sem scan/auditoria.</li>"
                    "<li><strong>Build em prod</strong>: 'só rebuildei lá' = artefato "
                    "diferente do testado.</li>"
                    "<li><strong>Não usar pull-through cache</strong>: rate limit em "
                    "horário de pico paralisa CI.</li>"
                    "</ul>"

                    "<h3>9. Caso real: SolarWinds (2020)</h3>"
                    "<p>Atacantes comprometeram o pipeline de build da SolarWinds, "
                    "injetando código no Orion antes de ser assinado. Centenas de "
                    "empresas (incluindo agências US) baixaram a imagem 'oficial' com "
                    "backdoor.</p>"
                    "<p>Lições: não basta assinar, o build precisa ser confiável "
                    "(SLSA L3+). Idealmente, builds reproducíveis (mesmo input gera mesma "
                    "saída) permitem que múltiplas partes verifiquem.</p>"
                ),
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
            },
            "materials": [
                m("Sigstore Cosign", "https://docs.sigstore.dev/cosign/overview/", "tool", ""),
                m("Harbor", "https://goharbor.io/docs/", "tool", ""),
                m("GitHub Container Registry", "https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry", "docs", ""),
                m("Artifactory docs", "https://jfrog.com/help/r/jfrog-artifactory-documentation", "docs", ""),
                m("OCI image spec", "https://github.com/opencontainers/image-spec", "docs", ""),
                m("SLSA framework", "https://slsa.dev/", "docs", "Níveis de provenance para supply chain."),
            ],
            "questions": [
                q("Por que usar registry privado?",
                  "Controle de acesso, rastreabilidade e independência de fornecedor público.",
                  ["É mais lento.", "É grátis sempre.", "Substitui IAM."],
                  "Também evita rate-limit (Docker Hub) e dá auditoria fina."),
                q("Tag mutável (latest) é problema porque:",
                  "Não há rastreabilidade, pode mudar a qualquer hora.",
                  ["É lenta.", "Aumenta custo.", "É só Linux."],
                  "Em rollback, você não consegue voltar para 'qual latest era ontem?'."),
                q("Cosign serve para:",
                  "Assinar e verificar artefatos OCI.",
                  ["Comprimir imagem.", "Substituir registry.", "Build de Java."],
                  "Combinado com policy controllers (Kyverno, Connaisseur), bloqueia imagens não assinadas."),
                q("Retenção de artefatos serve para:",
                  "Reduzir custos e poluição mantendo só o necessário.",
                  ["Aumentar redundância.", "Substituir backup.", "Melhorar lint."],
                  "Configure regras: 'manter últimas 50 tags + todas semver'."),
                q("OCI é:",
                  "Padrão aberto para imagens de container.",
                  ["Ferramenta de IAM.", "Backend de logs.", "Linguagem."],
                  "Open Container Initiative. Garante que imagem buildada pelo Docker roda no Podman, K8s etc."),
                q("Registry como pull-through cache:",
                  "Faz cache local de imagens públicas, evitando rate-limits.",
                  ["Acelera commits.", "Substitui CI.", "Cache de DNS."],
                  "Especialmente útil para imagens base (alpine, debian, python)."),
                q("RBAC em registry:",
                  "Controla quem pode ler/escrever em quais repositórios.",
                  ["Aumenta tamanho.", "Acelera scan.", "Substitui TLS."],
                  "Só CI faz push; devs leem; produção usa pull-secret específico."),
                q("Vulnerability scanning no registry:",
                  "Avisa quando uma imagem fica insegura mesmo após o push.",
                  ["Apenas no push.", "Substitui SCA.", "Substitui SAST."],
                  "Re-scan periódico cobre CVEs publicadas posteriormente."),
                q("Imagem 'untagged' é:",
                  "Geralmente lixo de builds antigos, limpar com retenção.",
                  ["Mais segura.", "Mais leve por default.", "Sempre last good."],
                  "Imagem perdeu a tag em rebuild; sem política, fica ocupando espaço."),
                q("Provenance (SLSA) é:",
                  "Atestado de como o artefato foi construído (origem, build).",
                  ["Tipo de tag.", "Backup.", "Apenas RBAC."],
                  "SLSA tem níveis 1-4. L3+ exige builder confiável (sem injeção do dev)."),
            ],
        },
    ],
}
