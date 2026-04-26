# Contribuindo com o Personal DevOps Trainer (PDT)

Obrigado pelo interesse em colaborar! Este projeto tem dois pilares
fortes: **qualidade técnica** e **qualidade educacional**. Para manter os
dois alinhados, pedimos que você siga as regras abaixo.

> Antes de qualquer coisa, leia o arquivo [LICENSE](./LICENSE). O uso do
> projeto é restrito; contribuições são aceitas, mas operação,
> redistribuição ou exploração comercial dependem de autorização explícita
> do mantenedor.

## 1. Tipos de contribuição bem-vindos

- Correção de bugs e issues abertas.
- Melhorias de UX/UI dentro do design existente.
- Novos materiais curados (com link público, estável e gratuito sempre que
  possível).
- Revisão e melhoria das aulas e bancos de questões já existentes.
- Tradução de textos e mensagens.
- Documentação, exemplos, scripts utilitários.
- Discussão de arquitetura por **issue** antes de abrir PRs grandes.

## 2. O que **não** aceitamos sem autorização prévia

- Renomeação ou rebranding do projeto.
- Mudança de licença ou remoção do aviso de copyright.
- Inclusão de SDKs proprietários, telemetria, anúncios, trackers, sistemas
  de login social fechados ou integrações pagas.
- Conteúdo educacional protegido por direitos autorais de terceiros sem
  permissão.
- Mudanças estruturais no modelo de pontuação, gamificação ou no teste de
  admissão sem discussão prévia.

## 3. Antes de abrir uma PR

1. Abra (ou comente em) uma **issue** descrevendo o problema/proposta. PRs
   sem issue podem ser fechadas.
2. Faça **fork** do repositório e crie uma branch a partir de `main` com o
   prefixo apropriado:
   - `feat/...`, funcionalidade nova
   - `fix/...`, correção de bug
   - `docs/...`, documentação
   - `content/...`, conteúdo educacional (aulas, materiais, questões)
   - `chore/...`, manutenção (deps, ci, refactor sem efeito visível)
3. Garanta que o ambiente está rodando via `docker compose up`.
4. Rode as checagens locais (ver seção 6).
5. Atualize testes/documentação relacionados.

## 4. Estilo de código

- **Python/Django**: PEP 8, nomes descritivos em `snake_case`, docstrings
  curtas em português. Nunca commit de credenciais.
- **Templates**: usar Tailwind classes existentes; preferir HTMX +
  Alpine.js a JavaScript pesado.
- **Modelos**: nunca remover campos sem migração de transição. Não
  reordenar valores de `choices` sem `data migration`.
- **Comentários**: explique o *porquê*. Não comente o óbvio.
- **Mensagens de commit**: imperativo, em português, no padrão
  Conventional Commits, ex.:
  - `feat(courses): adicionar trilha intermediária de Kubernetes`
  - `fix(presence): corrigir broadcast quando usuário desconecta`
  - `content(phase3): revisar materiais do tópico Terraform`

## 5. Adicionando novo conteúdo educacional

Conteúdo educacional vive em `pdt/apps/courses/seed_data/phaseN.py`. Para
contribuir:

- Use a função utilitária `q(...)` para questões e `m(...)` para
  materiais.
- Cada tópico precisa de **no mínimo 5 materiais** e **10 questões**.
- Verifique se os links são acessíveis sem login e preferencialmente
  gratuitos.
- Marque a alternativa correta com `is_correct=True` e escreva uma
  explicação curta (`explanation`).
- Mantenha o nível das questões coerente com a fase (1 = básico, 5 =
  avançado).
- Após editar o seed, rode:
  ```bash
  docker compose exec web python manage.py seed_topics --reset-questions
  ```
  para refletir as mudanças no banco local.

## 6. Checagens locais (antes de abrir a PR)

```bash
# Subir o ambiente
docker compose up -d

# Migrações
docker compose exec web python manage.py migrate --check

# Conteúdo carregado corretamente
docker compose exec web python manage.py seed_topics
docker compose exec web python manage.py seed_admission_test

# Smoke test mínimo (criar superuser e acessar /admin)
docker compose exec web python manage.py createsuperuser
```

Quando houver suíte de testes automatizada (em construção), também:
```bash
docker compose exec web python manage.py test
```

## 7. Revisão e merge

- PRs precisam de pelo menos uma aprovação do mantenedor.
- Squash merge é o padrão; mantenha o título da PR descritivo.
- Após o merge, sua contribuição passa a estar sob a licença do projeto
  (ver cláusula 4 da [LICENSE](./LICENSE)).

## 8. Código de conduta

Trate todo mundo com respeito. Comentários discriminatórios, ataques
pessoais ou conteúdo ofensivo levam à remoção imediata da PR/issue e
podem resultar em bloqueio do colaborador.

## 9. Dúvidas

Abra uma issue com a label `question` ou entre em contato pelo e-mail
informado no [README](./README.md).
