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
                  ["Faz merge preservando cada commit exatamente como já estava no branch.",
                   "Apaga o branch inteiro junto com o histórico inteiro associado a ele.",
                   "Sincroniza o repositório local com o remoto, sem alterar commit."],
                  "Rebase gera novos hashes; não use em história já compartilhada."),
                q("Por que evitar force push em main?",
                  "Pode reescrever história compartilhada e quebrar o time.",
                  ["É mais lento que um push comum, mas funciona normalmente.",
                   "É ilegal em muitos contextos corporativos regulados por auditoria.",
                   "Não funciona em repositório hospedado especificamente no GitHub."],
                  "Qualquer dev com a história anterior fica desincronizado e pode perder commits."),
                q("Signed commits servem para:",
                  "Provar autoria via GPG/SSH.",
                  ["Acelerar o push para o repositório remoto configurado.",
                   "Substituir a necessidade de criar um branch separado.",
                   "Comprimir o tamanho de cada commit antes de enviar."],
                  "Evita spoofing, atacante consegue dizer 'commit do CTO' sem assinatura. Com GPG, GitHub mostra 'Verified'."),
                q("Em PR, o que é review obrigatório?",
                  "Regra que exige aprovação humana antes do merge.",
                  ["Bloqueia o repositório inteiro para qualquer nova alteração.",
                   "Conta automaticamente como um deploy feito em produção.",
                   "Pula a execução do CI configurado para aquele repositório."],
                  "Combinada com CODEOWNERS, garante que pessoas certas sejam ouvidas."),
                q("Diferença entre merge e rebase:",
                  "Merge preserva história; rebase a reescreve linearmente.",
                  ["Os dois comandos são idênticos, sem diferença real entre eles.",
                   "O rebase é mais lento de executar do que um merge comum.",
                   "O merge apaga o commit mais antigo do branch de origem."],
                  "Escolha conforme política do time. Misturar pode confundir o histórico."),
                q("`.gitignore` serve para:",
                  "Listar arquivos a não rastrear (ex.: .env).",
                  ["Apagar o histórico de commit já registrado no repositório inteiro.",
                   "Bloquear um push específico feito para o branch principal.",
                   "Substituir o arquivo LICENSE do projeto por outro modelo."],
                  "Para arquivos já rastreados, é preciso `git rm --cached` antes."),
                q("Trunk-based development prefere:",
                  "Branches curtas e merge frequente em main.",
                  ["Branch de vida longa, mantida aberta por semanas ou meses.",
                   "Usar só tag de versão, sem branch de trabalho intermediário.",
                   "Trabalhar sem um branch principal de referência compartilhado."],
                  "Reduz merge hell. Exige feature flags e suite de testes confiável."),
                q("`git stash` faz:",
                  "Salva mudanças locais pendentes para retomar depois.",
                  ["Envia o commit local direto para o repositório remoto configurado.",
                   "Apaga o commit mais recente feito no branch atual.",
                   "Cria um branch novo a partir do commit atual do repositório."],
                  "Stash empilha. Use `git stash pop` para retomar; aplique a branch correta."),
                q("Conventional Commits é:",
                  "Convenção de mensagens (feat:, fix:, chore:).",
                  ["Um substituto completo para o próprio Git como ferramenta.",
                   "O hash único gerado automaticamente para cada commit novo.",
                   "Um linter que verifica erro de sintaxe dentro do código-fonte."],
                  "Permite gerar changelog e versionamento automático (semver)."),
                q("Em LFS, arquivos grandes:",
                  "Ficam em storage separado, com pointer no repo.",
                  ["Apagam o histórico de commit anterior relacionado ao arquivo.",
                   "Simplesmente não funcionam dentro de um repositório Git comum.",
                   "Ficam compactados dentro de um arquivo zip anexado ao commit."],
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
                  ["Aplica a mudança direto no provedor, sem mostrar diff antes.",
                   "Apaga o arquivo de estado atual armazenado remotamente.",
                   "Cria uma cópia de backup do estado atual do Terraform."],
                  "Plan gera plano determinístico (que apply vai consumir). Ler atentamente evita surpresas."),
                q("Estado remoto serve para:",
                  "Compartilhar entre membros do time com lock.",
                  ["Substitui a necessidade de configurar IAM na conta.",
                   "Habilita o protocolo HTTPS nas chamadas feitas à API.",
                   "Acelera o tempo de execução do comando plan localmente."],
                  "Sem state remoto, devs apagam o trabalho um do outro. Com lock, só um apply roda por vez."),
                q("Por que NÃO commitar tfstate?",
                  "Pode conter segredos e gera conflito.",
                  ["Falha silenciosamente o comando git ao tentar versionar.",
                   "Não é uma prática permitida pela documentação oficial.",
                   "É um arquivo grande demais para caber no limite do GitHub."],
                  "State guarda valores reais (incluindo passwords). Em git público, vira manchete instantânea."),
                q("Módulo Terraform serve para:",
                  "Encapsular e reutilizar componentes de infra.",
                  ["Criar uma VPN entre duas redes distintas na nuvem.",
                   "Substituir o provider configurado no bloco terraform.",
                   "Gerar log detalhado de cada execução do comando apply."],
                  "Padroniza configurações da empresa. Versione com tags Git."),
                q("`terraform import` serve para:",
                  "Trazer recurso existente para o estado.",
                  ["Renomear um módulo já existente dentro do código.",
                   "Aplicar um plano previamente gerado pelo comando plan.",
                   "Apagar um recurso já gerenciado pelo estado atual."],
                  "Útil ao migrar de console-feito para IaC. TF 1.5+ tem `import` block declarativo."),
                q("OpenTofu é:",
                  "Fork open source do Terraform mantido pela Linux Foundation.",
                  ["Outro provider oficial mantido diretamente pela HashiCorp original.",
                   "Uma DSL completamente diferente, com pouca relação prévia com o HCL.",
                   "Uma extensão de IDE que só destaca a sintaxe do HCL no editor."],
                  "Criado após mudança de licença do Terraform para BSL. Compatível com módulos existentes."),
                q("Para evitar drift:",
                  "Faça plan/apply periodicamente e proíba mudanças manuais.",
                  ["Apague o arquivo de estado ao perceber qualquer divergência.",
                   "Use só o console para fazer qualquer mudança de infraestrutura.",
                   "Edite o tfstate manualmente quando precisar corrigir algo pontual."],
                  "Drift detection em CI noturno é boa prática. Combine com SCPs que bloqueiem mudanças manuais."),
                q("Variável sensível em Terraform:",
                  "Marque com sensitive = true.",
                  ["Coloque o valor dentro da description da própria variável.",
                   "Imprima o valor no output, para conferência manual posterior.",
                   "Coloque o valor dentro de um comentário no próprio arquivo."],
                  "Evita que o valor apareça em outputs/log. Combine com TFC/Vault para evitar plaintext no state."),
                q("Provider é:",
                  "Plugin que conecta Terraform a uma API (AWS, GCP, etc.).",
                  ["Um tipo específico de variável usado dentro do HCL.",
                   "O hash calculado a partir do plano gerado pelo Terraform.",
                   "O backend responsável por guardar o estado remotamente."],
                  "Existem providers oficiais e da comunidade (Cloudflare, GitHub, K8s, Datadog...)."),
                q("Lock em backend remoto evita:",
                  "Dois apply simultâneos corrompendo estado.",
                  ["Custo adicional cobrado pelo provedor de nuvem utilizado.",
                   "Backup automático do estado feito antes de cada apply.",
                   "Importação de um recurso já existente para dentro do estado."],
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
