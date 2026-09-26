# 🗺️ Portal Cerrado — Project Map

## Stack

- Frontend: Next.js 16, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Celery
- Database and queue: PostgreSQL/SQLite fallback, Redis
- Infra: Docker Compose, Caddy, GitHub Actions

## Delivery Gate

- Regra pétrea: nenhuma funcionalidade nova ou deploy antes de todos os gates de `documento/PLANO_ACAO.md` passarem com evidência atual.
- Exceção: apenas correções necessárias para fechar os gates, registradas com validação e risco residual.

## Folder Structure

- app/ → API, editorial pipeline, persistence and background tasks
- config/ → source, scheduler and reporter policies
- frontend/src/app/ → public Next.js routes
- frontend/src/components/ → reusable public UI components
- frontend/src/components/Icon.tsx → local lucide icon vocabulary
- frontend/src/components/article/ → reading guide, sharing actions and article sidebar
- frontend/src/lib/ → API client and shared frontend utilities
- tests/ → unit and pipeline tests
- scripts/ → operational and maintenance commands

## Routes / Pages

- GET / → public home
- GET /categoria/[slug] → public category feed
- GET /noticia/[slug] → public article
- GET /api/news → paginated local public feed
- GET /api/editorial/review → protected queue for local review and published articles
- GET /api/operations/status → publication freshness signal
- GET /news-sitemap.xml → recent article discovery for news indexers
- GET /admin/editorial → protected editorial review workspace

## Key Files

- AGENTS.md → regra pétrea de entrega e proteção de alterações existentes
- app/main.py → FastAPI application and HTTP endpoints
- app/contracts.py → contratos de categoria, fontes e timestamps UTC/apresentação
- app/main.py → CORS fail-closed e endpoints FastAPI
- app/rate_limit.py → contador Redis compartilhado para endpoints públicos
- TRUSTED_PROXY_HOSTS → allowlist de proxies confiáveis para X-Forwarded-For
- app/security.py → autenticação por chave com política de força em produção
- app/editorial_routes.py → revisão editorial e registro de auditoria
- tests/unit/test_security.py → contrato de força da chave editorial
- tests/unit/test_env_contract.py → variáveis documentadas versus runtime
- tests/unit/test_operations_sitemap.py → filtro de artigos do news sitemap
- .env.example → contrato de ambiente sem chaves legadas
- SENTRY_TRACES_SAMPLE_RATE / SENTRY_PROFILES_SAMPLE_RATE → amostragem configurável do Sentry
- LLM_FALLBACK_CHAIN → ordem de failover dos provedores LLM
- .env.example → placeholders sem senha reutilizável para desenvolvimento
- documento/OPERACAO.md → procedimento de backup e rotação de chave editorial
- app/editorial_routes.py → fonte única das rotas editoriais protegidas
- app/analytics_routes.py → fonte única do tracking de primeira parte
- app/database.py → sessões FastAPI com rollback e fechamento garantidos
- app/tasks/scan_tasks.py → orquestração Celery do pipeline de coleta
- app/translation_glossary.py → glossário compartilhado de tradução LLM
- app/tasks/scan_persistence.py → persistência e deduplicação de rascunhos coletados
- alembic/versions/b3a8e4f7c2d1_add_news_title_fts_index.py → índice FTS PostgreSQL para fontes relacionadas
- app/personality.py → evolução temporal dos repórteres com datas normalizadas
- scripts/quarantine_misclassified_global_articles.py → auditoria segura de fontes globais
- app/duplicate_detection.py → regras compartilhadas de duplicação e conteúdo sensível
- app/trend_models.py → sinais e modelo de tendências editoriais
- app/curiosity_models.py → categorias e padrões de curiosidades
- app/curiosity_mixing.py → inserção de curiosidades no fluxo editorial
- app/scanner_catalog.py → agregador de dados editoriais do scanner
- app/scanner_keyword_core.py → palavras-chave principais do scanner
- app/scanner_keyword_extra.py → palavras-chave complementares do scanner
- app/scanner_parsing.py → coleta HTTP, parsing e validação de artigos
- app/classifier_patterns.py → padrões de importância e engajamento
- app/classifier_category.py → mixin de inferência de categoria
- app/classifier_category_keywords.py → agregador de palavras-chave do classificador
- app/classifier_category_core.py → palavras-chave principais de categoria
- app/classifier_category_extra.py → palavras-chave complementares de categoria
- app/auditor_agent_checks.py → checks de agentes e repórteres
- app/auditor_compliance_checks.py → checks de conteúdo, compliance, performance e categorias
- app/article_fetcher.py → orquestração HTTP da extração de artigos
- app/article_metadata.py → metadados, ruído e imagens de artigos
- app/article_body.py → corpo textual, fallback e limpeza de leads
- app/miner.py → fachada pública compatível do minerador
- app/miner_constants.py → constantes de volume e randomização
- app/miner_global.py → orquestração de coleta global
- app/miner_global_parsing.py → parsing RSS, Google News e relevância
- app/miner_volume.py → balanceamento de volume editorial
- app/miner_pipeline.py → classificação, tradução e roteamento
- app/publisher.py → publication and public feed rules
- app/local_news_policy.py → local editorial source gate
- frontend/src/lib/api.ts → frontend API client and home ranking
- frontend/src/lib/formatArticle.ts → article formatting and DOMPurify sanitization
- frontend/src/lib/electionCoverage.ts → deterministic election and politics selection for the home
- app/category_inference.py → conservative category inference for the publication pipeline
- tests/conftest.py → banco temporário e bloqueio de rede para testes unitários
- tests/integration/test_migrations.py → upgrade, downgrade e compatibilidade de migrations
- tests/unit/test_database_backup.py → round-trip e confirmação de restore
- tests/integration/test_indexes.py → índices de FK e consultas editoriais
- scripts/database_backup.py → backup/restore SQLite e PostgreSQL
- alembic/versions/a7c3d9e1f204_add_foreign_key_and_feed_indexes.py → índices de FKs e filtros editoriais
- frontend/src/lib/siteMetadata.ts → shared public social-preview metadata
- frontend/next.config.ts → allowlist explícita de hosts de imagem
- frontend/package.json → scripts oficiais de lint, TypeScript e build
- frontend/src/app/page.tsx → home dinâmica por depender de cotações no-store
- frontend/src/app/robots.ts → metadata de robots
- frontend/src/app/sitemap.ts → sitemap público
- frontend/src/app/news-sitemap.xml/route.ts → sitemap de notícias com fallback 503
- frontend/src/app/not-found.tsx → fallback editorial de rota inexistente
- frontend/src/app/noticia/[slug]/loading.tsx → skeleton da leitura de notícia
- documento/PRONTIDAO_CANDIDATO.md → gates finais e bloqueios para promoção
- Caddyfile → CSP, Permissions-Policy e headers HTTP de segurança
- tests/unit/test_security_headers.py → contrato estático dos headers do proxy
- docker-compose.local.yml → override local com bridge e portas temporárias
- docker-stack.swarm.yml → stack Swarm de teste com imagens por digest
- celery_monitoring → worker Celery dedicado à fila de healthcheck e métricas
- tests/unit/test_runtime_contract.py → serviços, healthchecks e isolamento Swarm
- tests/unit/test_ci_contract.py → promoção manual e tags imutáveis
- .github/workflows/deploy.yml → workflow manual por SHA e inventário de dependências
- scripts/update.sh → promoção local/Swarm com contrato explícito
- config/observability.yaml → métricas, alertas, retenção e rollback declarativos
- tests/unit/test_observability_contract.py → contrato offline de observabilidade
- tests/unit/test_failure_simulations.py → simulações offline de falhas críticas
- scripts/rollback.sh → rollback Swarm por SHA com dry-run obrigatório
- tests/unit/test_rollback_contract.py → contrato de confirmação e cobertura de serviços
- frontend/src/lib/editorialApi.ts → protected editorial queue client
- frontend/src/components/admin/ → editorial review dashboard UI
- config/scheduler.yaml → local publication policy
- documento/FONTES_RASPAGEM.md → catálogo de fontes, URLs e status de integração
- documento/EVIDENCIAS_VALIDACAO.md → evidências extensas de testes, CI e Swarm

## Database Tables

- news_articles · reporters · publication_logs · scraping_tasks · editorial_trend_signals

## Data Retention

- Backups operacionais: retenção de 30 dias; restore de teste obrigatório antes de expurgo.

## Last updated: 2026-09-24
