# OPERACAO - Portal Cerrado

## Status Consolidado
- Backend funcional e operando em Docker Swarm via Tailscale.
- Frontend funcional consumindo API real.
- Pipeline de conteudo ativo: scan, classify, rewrite, publish.
- 125 artigos publicados, 0 categorias invalidas, 0 artigos em geral.
- 77 testes passando, lint e py_compile validados.

## Stack em Produção
- Backend: FastAPI + Celery + Redis + PostgreSQL
- Frontend: Next.js + Tailwind
- Infra: Docker Swarm via Tailscale (100.95.111.24)
- LLM: Groq (LLM_PROVIDER=gemini com GROQ_API_KEY)
- Deploy: via update.sh (docker stack deploy)

## Contrato de Runtime

### Backend Obrigatorio em Produção
- `DATABASE_URL` -> Postgres do stack.
- `REDIS_URL` -> Redis do stack.
- `LLM_PROVIDER` -> `gemini` (usa Groq API via SDK compatível).
- `GROQ_API_KEY` -> chave da API Groq (provider real).
- `GEMINI_API_KEY` -> fallback OpenRouter (opcional).
- `OPENAI_API_KEY` -> fallback OpenRouter (opcional).
- `PUBLISH_API_KEY` -> chave para endpoints de escrita.
- `SITE_URL` -> URL publica do site.
- `NEXT_PUBLIC_SITE_URL` -> mesma URL publica para o frontend.
- `NEXT_PUBLIC_API_URL` -> URL interna da API para o frontend.
- `CORS_ALLOWED_ORIGINS` -> origem publica do frontend e origem local de manutencao.
- `ENVIRONMENT` -> `production` no deploy real.
- `SIMILARITY_THRESHOLD` -> limiar de compliance (default: 0.35).

### Backend Opcional ou de Controle
- `CELERY_SCHEDULER` -> `1` quando beat assume.
- `ENABLE_LOCAL_SCHEDULER` -> `0` em producao com beat.
- `DATABASE_CONNECT_RETRIES` -> tentativas de conexao ao Postgres antes de falhar (default: 10).
- `DATABASE_CONNECT_RETRY_DELAY` -> intervalo entre tentativas (default: 1s).
- `ARCHIVE_DAYS_AFTER_PUBLISH` -> politica de retencao (default: 30 dias).
- `DEDUP_TTL_SECONDS` -> TTL de deduplicacao (default: 604800 = 7 dias).

### Frontend Obrigatorio em Produção
- `NEXT_PUBLIC_API_URL` -> destino dos rewrites e fetch.
- `NEXT_PUBLIC_SITE_URL` -> base do metadata, sitemap e robots.

### Regra de Contrato
- Qualquer variavel listada como obrigatoria deve existir no stack final.
- Variavel nao usada no runtime final deve ser removida do deploy ou documentada como legado.
- Nenhum valor de producao deve depender de default para host ou dominio antigo.

## Matriz de Execucao
| Fase | Status | Bloqueio Principal | Criterio de Aceite |
| --- | --- | --- | --- |
| 0 - Inventario | done | divergencia desconhecida | diff conhecido e registrado |
| 1 - Runtime | done | env/nome de servico incorreto | contrato de runtime fechado |
| 2 - Backend | done | import/db/DNS/crash loop | backend e workers sobem |
| 3 - Frontend | done | API/URL/metadata errados | frontend usa API real |
| 4 - Build e Registry | done | imagem nao publicada | build local funcional |
| 5 - Portainer/Swarm | done | stack fora do contrato | services 1/1 |
| 6 - Validacao Final | done | teste/lint/health falhando | 77 testes, 0 categorias invalidas |

## Guia Operacional
1. Validar banco, API e frontend.
2. Validar pipeline de scan, classify, rewrite, publish.
3. Validar exportacao do frontend.
4. Validar healthchecks e logs.
5. Validar deploy pela stack oficial do ambiente.

## Regras de Parada
- Se uma fase falhar, nao avancar para a seguinte.
- Se o erro for de build, corrigir antes de publicar.
- Se o erro for de stack, corrigir antes de validar frontend.
- Se o erro for de runtime, atualizar o plano antes de improvisar.

## Referencia Rapida
- Se precisar saber o que mudar, use `PLANO_ACAO.md`.
- Se precisar saber o que e verdade canonica, use `MEMORIA.md`.
- Se precisar operar o sistema, use este arquivo.
