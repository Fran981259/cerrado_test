# PLANO DE ACAO - Portal Cerrado

## Regra Pétrea de Entrega

- Este arquivo é a fonte única do plano de entrega e refatoração.
- Não implementar novas funcionalidades, não publicar imagem, não executar deploy, não aplicar stack e não cortar ambiente enquanto todos os gates abaixo não estiverem aprovados por evidência atual.
- A única exceção permitida é uma correção estritamente necessária para fazer um gate passar. Ela deve registrar causa, arquivos afetados, comando de validação e risco residual.
- Nenhum texto de documentação, status histórico ou build anterior substitui uma validação executada sobre o commit candidato atual.
- Não manter Compose e Swarm como dois runtimes produtivos concorrentes; Compose é local/teste e Swarm só existe após uma stack dedicada e validada.

## Estado de Referência em 24/09/2026

| Gate | Estado | Evidência atual |
| --- | --- | --- |
| Git limpo e commit candidato | aprovado | `2eac2448bb16c2fa8cbd2803464cdeb4c20770a7` local |
| Ruff backend | aprovado | `ruff check app tests scripts` sem violações |
| Mypy backend | aprovado | `mypy app` sem erros em 65 arquivos |
| Testes backend | aprovado | 120 unitários + 8 integração aprovados |
| Lint, tipos e build frontend | aprovado | Next.js gerou 27 páginas em 24/09/2026 |
| Dependências frontend | aprovado localmente | `npm audit --offline --omit=dev` sem vulnerabilidades altas |
| Contrato Swarm | aprovado localmente | Compose e stack dedicados renderizados com imagens por SHA |
| Deploy e rollback em teste | não iniciado | depende dos gates anteriores |

## Objetivo

Restaurar uma base reproduzível, testável e operável antes de qualquer evolução de produto ou deploy. O resultado deve ter um único contrato de runtime, pipeline editorial determinístico, frontend validado, imagens imutáveis e recuperação documentada.

## Definição de Pronto

- Árvore Git limpa, com commits lógicos e candidato identificado por SHA.
- Ruff, mypy, testes unitários e integração interna passam sem rede, LLM real ou dados externos.
- Frontend passa lint, tipos, build e auditoria de dependências sobre o mesmo commit.
- Cada rota HTTP tem uma única implementação, contrato validado e proteção proporcional.
- Compose local e stack Swarm têm arquivos separados, sem diretivas incompatíveis.
- Banco, fila, workers, frontend e proxy passam smoke test no ambiente de teste.
- Imagens usam tag SHA; rollback e restauração de banco foram exercitados.
- Observabilidade, alertas e documentação refletem a execução real.

## Plano Incremental de Refatoração

### Fase 0 — Congelamento e baseline

- Estado: concluída em 24/09/2026; manifesto registrado abaixo.
- Pré-condição: nenhuma implementação nova.
- Ações: inventariar diff, separar alterações por domínio, registrar versão de Python, Node, banco e imagens; classificar cada mudança como correção de gate ou adiar.
- Saída: `git status` conhecido, mapa atualizado e lista de commits planejados.
- Validação: `git diff --check`, inventário de arquivos e revisão humana do escopo.

#### Manifesto do baseline

| Grupo | Escopo identificado | Decisão nesta etapa |
|---|---|---|
| Governança | `AGENTS.md`, este plano e `portal-cerrado.md` | Manter: formalizam os gates e não alteram produto. |
| Classificação | `app/category_inference.py`, tarefas de classificação e teste unitário | Congelar até a Fase 1 definir e validar o contrato de categorização. |
| Sitemap de notícias | `app/operations_routes.py` | Adiar para a Fase 6: é entrega de SEO, não correção de gate atual. |
| Frontend editorial e SEO | Rotas, componentes e bibliotecas novas ou alteradas em `frontend/src/` | Adiar para a Fase 6: contém evolução de produto e apresentação. |
| Repositório remoto | `origin` ainda referencia o legado `BotGram` | Registrar para decisão controlada nas Fases 7 e 8; não alterar remoto agora. |
| Infraestrutura | Nenhum diff de infraestrutura nesta linha de base | Sem ação; a compatibilidade Compose/Swarm será tratada na Fase 7. |

### Fase 1 — Restaurar a verdade dos testes

- Estado: concluída em 24/09/2026.
- Escopo: `tests/unit`, `app/llm_client.py`, `app/rewriter.py`, `app/filter.py` e contratos de classificação.
- Ações:
  1. Definir para cada falha se o comportamento esperado mudou ou se o código regrediu.
  2. Mockar LLM, HTTP, Redis e relógio em testes unitários.
  3. Mover chamadas reais de provedor para testes de integração opt-in, sem execução no CI padrão.
  4. Corrigir expectativas obsoletas ou código divergente sem ampliar funcionalidade.
- Saída: testes unitários determinísticos, sem retry externo e sem depender de credenciais.
- Validação: `venv/bin/pytest tests/unit -q` duas vezes consecutivas com o mesmo resultado.
- Evidência: `89 passed` em 26,89 s e `89 passed` em 26,99 s, com bloqueio de socket
  ativo por teste, chaves LLM vazias no ambiente de teste, Redis falso nos testes de
  deduplicação e relógio fixado no caso de expiração.

### Fase 2 — Fechar qualidade estática e eliminar duplicação HTTP

- Estado: concluída em 24/09/2026.
- Escopo: `app/main.py`, `app/editorial_routes.py`, `app/analytics_routes.py`, `app/operations_routes.py`, imports e módulos de tarefa apontados pelo lint.
- Ações:
  1. Remover as versões duplicadas de publish, revisão e analytics de `app/main.py`.
  2. Manter cada endpoint exclusivamente no router especializado.
  3. Corrigir o tipo de conteúdo editorial antes de `review_natural_writing`.
  4. Organizar imports e remover símbolos não usados sem usar auto-fix cego.
  5. Adicionar teste que prova que cada caminho HTTP resolve para uma única rota.
- Saída: API sem rota sombra, Ruff e mypy verdes.
- Validação: `venv/bin/ruff check app tests`, `venv/bin/mypy app` e teste de rotas.
- Evidência: Ruff aprovou `app` e `tests`; mypy aprovou 41 módulos; 90 testes
  unitários passaram em 26,52 s. Os quatro contratos duplicados agora possuem
  uma única rota registrada, validada recursivamente para a versão atual do FastAPI.

### Fase 3 — Decomposição segura do núcleo backend

- Estado: concluída em 24/09/2026; decomposição estrutural do núcleo validada.
- Ordem: `app/main.py` → `app/tasks/scan_tasks.py` → `app/scanner.py` → `app/classifier.py` → `app/filter.py`.
- Ações:
  1. Extrair somente grupos coesos: schemas HTTP, dependências, consultas, regras editoriais e adaptadores externos.
  2. Preservar assinaturas públicas e criar testes de caracterização antes de mover cada grupo.
  3. Proibir mudança simultânea de regra de negócio e estrutura no mesmo commit.
- Saída: módulos de produção até 300 linhas, funções pequenas e dependências explícitas.
- Validação: testes existentes, type-check, diff de rotas e comparação de contratos JSON.
- Evidência parcial: a orquestração de scan foi reduzida de 450 para 144 linhas e a
  persistência foi isolada em `app/tasks/scan_persistence.py` (255 linhas). As regras
  auxiliares de deduplicação saíram de `app/filter.py`, que caiu de 333 para 252 linhas.
  O catálogo de tendências saiu para `app/trend_models.py`, reduzindo `ml_editorial.py`
  a 249 linhas. O catálogo e a mistura de curiosidades foram extraídos, reduzindo
  `curiosities.py` a 279 linhas. O catálogo do scanner foi dividido em três arquivos
  menores. Os métodos de coleta e validação foram extraídos para `scanner_parsing.py`,
  deixando `scanner.py` com 188 linhas. O classificador foi separado em núcleo,
  padrões e palavras-chave, todos abaixo de 300 linhas. O auditor foi separado em
  agregador e dois grupos de checks abaixo do teto. Ruff, mypy e os testes direcionados
  do auditor permanecem verdes (13 testes). Restam 2 módulos acima do teto:
  `article_fetcher.py` foi separado em orquestrador, metadados e corpo textual;
  `miner.py` foi separado em fachada, coleta, parsing, volume e pipeline. Todos os
  módulos da fase estão abaixo do teto, com Ruff, mypy e testes direcionados verdes.

### Fase 4 — Contratos de dados, tempo e persistência

- Estado: concluída em 24/09/2026; contratos, migrations, backup e índices validados.
- Escopo: SQLAlchemy, Alembic, `app/contracts.py`, `app/database.py`, `app/celery_app.py`.
- Ações:
  1. Padronizar runtime e apresentação em `America/Campo_Grande`.
  2. Documentar a fonte de verdade de categoria, região, status e timestamps.
  3. Revisar migrations contra banco de teste que represente dados legados.
  4. Criar procedimento de backup, restore e upgrade reversível quando suportado.
  5. Validar índices para filtros de publicação, região, status, slug e data.
- Saída: migração segura, timezone único e contratos de dados testados.
- Validação: banco vazio, banco com legado, upgrade Alembic, rollback de teste e consultas de API.
- Evidência parcial: `app.contracts` agora é a fonte única para UTC persistido e
  apresentação em `America/Campo_Grande`; Celery e o manifesto do orquestrador usam
  o mesmo identificador. Três testes de contrato cobrem normalização, apresentação e
  timestamps ingênuos de banco; 21 testes direcionados passaram. O ensaio de
  migrations agora cobre upgrade completo, downgrade até a base e upgrade de um
  banco legado com artigo anterior à coluna `region` (2 testes aprovados).
  O utilitário `scripts/database_backup.py` cobre backup/restore SQLite e
  PostgreSQL, exige confirmação para restore e foi validado em round-trip local
  com 2 testes aprovados. A migration `a7c3d9e1f204` adiciona índices de FKs e
  filtros editoriais; inspeção de índices e `EXPLAIN QUERY PLAN` passaram (3 testes).

### Fase 5 — Segurança e administração editorial

- Estado: em andamento; CORS fail-closed em produção.
- Escopo: CORS, proxy, endpoint editorial, analytics, imagens externas e variáveis de ambiente.
- Ações:
  1. Exigir `CORS_ALLOWED_ORIGINS` em produção sem defaults locais.
  2. Trocar rate limit em memória por limite compartilhado ou aplicar limite no proxy.
  3. Restringir `next.config.ts` a hosts de imagem permitidos.
  4. Definir CSP, Permissions-Policy e política de headers no Caddy.
  5. Definir autenticação de operadores, rotação de chave e auditoria de ação editorial.
  6. Remover variáveis de ambiente legadas que não participam do runtime.
- Saída: superfície pública mínima e administração rastreável.
- Validação: testes de autorização, matriz CORS, scanner de configuração e smoke test de headers.
- Evidência parcial: `CORS_ALLOWED_ORIGINS` passou a ser obrigatório em produção no
  FastAPI e no Compose; wildcard é rejeitado quando há credenciais. Defaults ficam
  restritos a desenvolvimento/teste. A matriz CORS foi coberta por 12 testes do
  scheduler; o mypy global ainda possui um erro preexistente em
  `app/tasks/scan_persistence.py:45`. O rate limit de analytics foi movido para
  contador Redis atômico, com fallback local apenas fora de produção; 5 testes
  direcionados cobrem fallback, fail-closed e `INCR`/`EXPIRE`.
  O `frontend/next.config.ts` deixou de aceitar hostname wildcard para imagens e
  mantém apenas hosts editoriais/CDNs explicitamente listados; ESLint do frontend
  passou. O `Caddyfile` agora define CSP, Permissions-Policy e headers básicos
  de proteção; o contrato foi coberto por 1 teste estático. A validação nativa do
  Caddy permanece pendente porque o binário não está instalado neste ambiente.
  Em autenticação editorial, produção agora exige chave de pelo menos 32 caracteres
  e revisões manuais geram `PublicationLog` sem registrar segredos ou conteúdo;
  22 testes direcionados passaram. O `.env.example` foi alinhado ao runtime atual:
  removidos OpenRouter, `LLM_MODEL` e Grafana; adicionados provider/modelos atuais,
  `API_URL` e retenção de arquivamento. O contrato de ambiente passou em 2 testes.
  A autenticação suporta rotação sem downtime via `PUBLISH_API_KEY_PREVIOUS`, com
  remoção obrigatória após a janela de transição; a rotina foi coberta por 3 testes
  de segurança.

### Fase 6 — Consolidar frontend e SEO

- Estado: em andamento; contrato SEO validado no build atual.
- Escopo: App Router, sitemap, news sitemap, metadados, busca, admin e integração API.
- Ações:
  1. Confirmar que sitemaps só publicam artigos públicos de MS.
  2. Testar XML de news sitemap, escaping e janela de 48 horas.
  3. Testar JSON-LD, canonical, Open Graph e páginas sem imagem ou sem repórter.
  4. Adicionar testes de rota e contrato para busca, editorias e administração.
  5. Substituir o README padrão do Next por guia real de operação e desenvolvimento.
- Saída: frontend e SEO verificáveis, sem promessas falsas ou dados inventados.
- Validação: lint, tipos, build, testes de contrato, inspeção de XML/JSON-LD e Lighthouse manual no ambiente de teste.
- Evidência parcial: o frontend passou ESLint, TypeScript e build Next.js, gerando
  27 rotas. Canonical, Open Graph, Twitter, JSON-LD e janela de 48 horas do news
  sitemap estão implementados; inspeção manual de XML e Lighthouse permanecem
  pendentes para o ambiente de teste servido. O contrato backend do news sitemap
  foi coberto: somente artigos publicados, públicos, regionais e dentro de 48 horas
  entram no resultado (1 teste aprovado).
  O smoke test servido não pôde ser executado neste sandbox: `next start` recebeu
  `EPERM` ao abrir a porta local, embora o build tenha concluído com 27 rotas.

### Fase 7 — Separar runtime local e Swarm

- Estado: em andamento; contratos local e Swarm separados e validados sem deploy.
- Escopo: `docker-compose.local.yml`, Compose de teste, nova stack Swarm dedicada, Caddy e CI.
- Ações:
  1. Manter Compose somente para desenvolvimento e teste local.
  2. Criar arquivo Swarm próprio sem `container_name`, `build` e `depends_on.condition`.
  3. Usar serviços com nomes DNS de Swarm e rede overlay dedicada.
  4. Definir volumes novos para teste; nunca reutilizar volumes legados sem migração aprovada.
  5. Resolver previamente portas, TLS e proxy do host.
- Saída: um caminho local e um caminho Swarm, ambos explícitos e sem ambiguidade.
- Validação: `docker compose config`, `docker stack config`, deploy paralelo de teste e healthchecks 1/1.
- Evidência parcial: `docker-compose.local.yml` sobrescreve somente o ambiente local
  e usa rede bridge/portas temporárias; `docker-stack.swarm.yml` remove `build`,
  `container_name` e `depends_on.condition`, usa imagens obrigatórias por digest,
  volumes `cerrado_test_*` e rede overlay dedicada. `docker compose config` e
  `docker stack config` passaram com valores de teste; nenhum deploy foi executado.
  O contrato automático de runtime confirmou sete serviços obrigatórios, réplicas
  unitárias, healthchecks, placeholders que exigem digest e ausência de volumes
  legados; 3 testes passaram.

### Fase 8 — CI, imagens e promoção controlada

- Estado: em andamento; promoção manual e imagens imutáveis configuradas.
- Ações:
  1. Fazer CI executar exatamente os comandos aprovados localmente.
  2. Bloquear merge se backend, frontend ou auditoria de dependências falhar.
  3. Publicar somente tags SHA imutáveis; `latest` não é entrada de deploy.
  4. Gerar SBOM ou inventário de dependências e registrar artefato do build.
  5. Separar build/push de autorização de deploy.
- Saída: cada imagem é rastreável ao commit e só pode ser promovida após CI verde.
- Validação: PR de teste, artefatos de workflow, pull por SHA e reprodução local da imagem.
- Evidência parcial: o workflow de publicação agora exige `workflow_dispatch`, remove
  tags `latest` e publica somente `${{ github.sha }}`. O job
  `dependency-inventory` gera `pip freeze --all` e a árvore JSON de `npm ls`,
  anexando ambos como artefato versionado pelo SHA. `scripts/update.sh` usa o SHA
  completo, exige CORS e aponta para `docker-stack.swarm.yml`; o caminho local usa
  `docker-compose.local.yml`. O contrato passou em 3 testes; nenhuma imagem foi
  construída, publicada ou promovida.

### Fase 9 — Observabilidade e ensaio de operação

- Estado: em andamento; contrato declarativo e runbook adicionados, sem ensaio externo.
- Ações:
  1. Definir métricas de API, workers, fila, publicação e falha de fonte.
  2. Centralizar logs estruturados com correlação por pipeline e artigo.
  3. Criar alertas de fila parada, publicação stale, erro LLM, healthcheck e disco.
  4. Executar backup/restore, rollback de imagem e rollback operacional em teste.
  5. Atualizar `OPERACAO.md`, `MEMORIA.md` e mapa somente após evidência coletada.
- Saída: falha detectável, diagnóstico possível e recuperação ensaiada.
- Validação: simulação controlada de falha de API, Redis, worker, LLM e proxy.
- Evidência parcial: `config/observability.yaml` define métricas, alertas, retenção,
  campos proibidos e ordem de rollback; `documento/OPERACAO.md` documenta resposta a
  incidentes. As simulações offline confirmam HTTP 503 para banco indisponível,
  degradação do healthcheck de manutenção e retries limitados do LLM; 5 testes de
  observabilidade/falha passaram. Redis, worker e proxy permanecem validações
  contratuais, pois nenhum serviço externo foi iniciado. A análise mypy transitiva
  ainda acusa erro preexistente em `app/tasks/scan_persistence.py:45`. O ensaio
  isolado SQLite backup → remoção → restore confirmou o conteúdo e gerou SHA-256;
  `tests/unit/test_database_backup.py` passou com 2 testes.
- O rollback controlado foi ensaiado em dry-run: `scripts/rollback.sh` rejeita SHA
  inválido, não chama Docker sem `--confirm` e exige `ROLLBACK_APPROVED=yes`; o
  contrato passou em 2 testes. A renderização de Compose local e stack Swarm passou
  com imagens de teste por SHA. O daemon Docker não está ativo nesta sessão, então a
  aplicação real do rollback e o ensaio com serviços permanecem bloqueados.
- O bloqueio Mypy de `app/tasks/scan_persistence.py:45` foi corrigido com guarda
  explícita para `datetime | None`; a validação estática do módulo passa.
- A execução Mypy sobre todo `app/` revelou dois usos equivalentes em
  `app/personality.py`; ambos foram centralizados em `_age_days` com tratamento
  explícito de data ausente.
- A validação frontend passou em `npm run lint`, TypeScript (`npx tsc --noEmit`) e
  `npm run build`; o Next.js compilou 27 rotas, incluindo `news-sitemap.xml`,
  `sitemap.xml` e `robots.txt`, sem iniciar servidor ou publicar artefato.
- O primeiro smoke servido revelou HTTP 503 na home por conflito estático/dinâmico
  causado pelas cotações `no-store`; `frontend/src/app/page.tsx` foi marcado como
  `force-dynamic` para alinhar o contrato de renderização. Após novo build, o smoke
  local confirmou home, `robots.txt` e `sitemap.xml` em HTTP 200; `news-sitemap.xml`
  retornou 503 controlado porque a API backend não estava ativa.
- Smoke full-stack concluído com API FastAPI em SQLite descartável e frontend servido:
  `/health` retornou `healthy`, `news-sitemap.xml` respondeu HTTP 200 com XML válido
  (167 bytes) e ambos os processos foram encerrados ao final.
- Auditoria de prontidão registrou 50 arquivos modificados e 52 novos não rastreados;
  não há artefatos de build pendentes. O candidato continua bloqueado até revisão,
  commits lógicos, Lighthouse e aprovação explícita do ensaio Docker/Swarm.
- Auditoria local de performance/SEO: Lighthouse não está instalado no ambiente;
  o build produziu 1,36 MB de assets estáticos e 2,06 MB de server bundle, não há
  tags `<img>` cruas no frontend, as três rotas de metadata existem e `npm audit`
  offline não encontrou vulnerabilidades altas.
- A auditoria de higiene não encontrou `console.log` ou `debugger`; o `.env.example`
  tinha `portal_pass` como senha reutilizável e foi convertido para placeholder
  `CHANGE_ME_LOCAL_PASSWORD`. Arquivos legados acima de 300 linhas permanecem sem
  alteração e foram registrados como dívida técnica para uma fase própria.
- A auditoria Ruff completa de `app`, `tests` e `scripts` encontrou apenas o
  bootstrap intencional de `sys.path`; os quatro imports receberam justificativa
  `E402` localizada e a auditoria foi aprovada.
- A suíte de integração passou com 8 testes em 3,47s. A suíte unitária foi
  executada por blocos equivalentes (incluindo publisher e robots): 120/120 testes
  passaram. A execução agregada excede o limite interativo de 30s desta sessão,
  mas a cobertura total foi executada e o gate unitário está aprovado por blocos.

### Fase 10 — Candidato de deploy

- Pré-condições: fases 0 a 9 aprovadas e `git status` limpo.
- Ações: criar tag de candidato, publicar imagens SHA, fazer deploy somente no ambiente de teste e executar smoke test completo.
- Saída: relatório de aceite com versões, resultados, risco residual e plano de rollback.
- Regra: produção continua bloqueada até aprovação explícita do usuário depois do relatório.
