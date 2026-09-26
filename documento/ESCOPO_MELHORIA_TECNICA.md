# Escopo de Melhoria Técnica — Portal Cerrado

**Versão:** 1.0
**Data da Auditoria:** 25/09/2026
**Metodologia:** Framework `arq_data/.agents/skills/` (9 domínios)
**Disciplina Epistêmica:** Cada item é classificado como **[FATO]**, **[INFERÊNCIA]** ou **[DESCONHECIDO]**

---

## 1. Resumo da Auditoria

### 1.1 Validações Automatizadas (Gate de Qualidade)

| Ferramenta | Resultado | Evidência |
|---|---|---|
| `ruff check app tests scripts` | ✅ 0 erros | `All checks passed!` |
| `mypy app` | ✅ 0 erros em 65 módulos | Cobertura completa de tipagem estática |
| `npm run lint` (ESLint + Next.js) | ✅ 0 erros | Lint clean |
| `npm run build` (Next.js 16) | ✅ 26 rotas compiladas | Build de produção aprovado |
| `pytest tests/unit` | ✅ 120/120 testes passaram | 27.61s |
| `pytest tests/integration` | ✅ 8/8 testes passaram | 3.86s |

### 1.2 Inventário do Projeto

| Domínio | Contagem |
|---|---|
| Módulos backend (`app/`) | 50 arquivos Python |
| Tarefas Celery (`app/tasks/`) | 7 módulos de tarefa |
| Componentes React (`frontend/src/components/`) | 9 componentes + 5 diretórios de UI |
| Rotas Next.js (`frontend/src/app/`) | 12 diretórios de rota + 8 arquivos |
| Libs frontend (`frontend/src/lib/`) | 12 módulos utilitários |
| Tabelas ORM | 7 modelos (`schema.py`) |
| Serviços Docker | 8 (postgres, redis, backend, worker, beat, flower, frontend, caddy) |

---

## 2. Diagnósticos de Auditoria — Backend

### 2.1 🔴 CRÍTICO — Rate Limiter Cego a IP Real

**Arquivos:** `app/analytics_routes.py:46-49`, `app/rate_limit.py:33-38`

**[FATO]** `_is_rate_limited` extrai IP exclusivamente de `request.client.host`. Em produção
atrás de Caddy, todos os visitantes compartilham o IP do proxy reverso. Com
`_MAX_REQUESTS = 30` em janela de 60s, bastam 30 pageviews globais para que **todos**
os clientes sejam bloqueados.

**[FATO]** `redis.Redis.from_url(...)` é instanciado a **cada invocação** — sem pool de
conexões reutilizável. Churn de sockets TCP a cada requisição HTTP.

**[FATO]** `incr` e `expire` são comandos separados sem pipeline atômico. Se a conexão
falhar entre os dois, a chave fica sem TTL (bloqueio permanente do IP afetado).

### 2.2 🔴 CRÍTICO — Gargalo de Memória e CPU no Painel Editorial

**Arquivo:** `app/editorial_routes.py:68-91`

**[FATO]** `list_articles_for_review` carrega até 2.000 artigos ORM completos (incluindo
corpo textual), e no serializer `_review_payload` (L129) executa
`review_natural_writing()` — que roda `SequenceMatcher` + regexes pesados — de forma
síncrona para **cada um dos 2.000 artigos** na mesma requisição GET, sem paginação.

**[INFERÊNCIA]** Em VPS com 1.8 GB de RAM livre, uma única chamada a essa rota pode
provocar OOM Killer ou travar o Uvicorn por mais de 30 segundos.

### 2.3 🔴 CRÍTICO — Acúmulo de Tarefas Health Check no Celery

**Arquivo:** `app/celery_app.py:88-91`

**[FATO]** `system_health_check` é agendado a cada 5 minutos na fila padrão `celery` (sem
`queue` dedicada). O worker opera com `-c 1`. Quando o pipeline pesado roda (15–25 min),
o Beat continua enfileirando health checks que não são consumidos. Isso gerou **1.469
tarefas acumuladas** no Redis documentadas em inspeção anterior da VPS.

### 2.4 🟡 ALTO — Ausência de Rollback em Analytics

**Arquivo:** `app/analytics_routes.py:39-43`

**[FATO]** O bloco `except` captura exceção mas não executa `db.rollback()`. No SQLAlchemy
com QueuePool, fechar sessão com transação abortada devolve conexão em estado
inconsistente. Além disso, `analytics_routes.py` usa `get_session()` diretamente (L32) em
vez de `Depends(get_db)`, quebrando o padrão do restante da aplicação.

### 2.5 🟡 ALTO — Backoff do LLM Descalibrado e Retorno Vazio Silencioso

**Arquivo:** `app/llm_client.py:68-108`

**[FATO]** O backoff do `LLMClient` tem fórmula `10 * 2^(attempt-1)` em 6 tentativas,
totalizando ~310s de bloqueio de thread. Se um lote inteiro esgotar retries, ultrapassa
facilmente o `soft_time_limit` de 1380s da Celery task.

**[FATO]** Ao falhar, `complete()` retorna string vazia `""` sem lançar exceção. O
`rewrite_tasks.py` (L167-178) já implementa validação defensiva (verifica
`len(candidate.split()) >= 350`), mas o LLM client mente ao caller sobre a natureza
do erro.

**[FATO]** O sistema possui adapters para `gemini`, `openai` e `groq`, mas NÃO implementa
failover automático entre eles em caso de cota esgotada (429).

### 2.6 🟡 ALTO — Busca de Fontes Relacionadas sem Índice

**Arquivo:** `app/tasks/rewrite_tasks.py:28-71`

**[FATO]** `_find_related_sources` carrega 300 artigos ORM completos (L40-45) e faz
matching por keywords em loop Python com complexidade O(N·K). À medida que a base
cresce, esta busca ficará progressivamente mais lenta — sem utilizar fulltext search
ou trgm do PostgreSQL.

### 2.7 🟢 MODERADO — Sentry com 100% de Sampling

**Arquivo:** `app/main.py:46-50`

**[FATO]** `traces_sample_rate=1.0` e `profiles_sample_rate=1.0` capturam 100% de traces
e perfis. Em tráfego crescente, isso gera overhead significativo de I/O e pode exceder
a cota gratuita do Sentry rapidamente.

### 2.8 🟢 MODERADO — Thread Scheduler no Lifespan

**Arquivo:** `app/main.py:64-72`

**[FATO]** `_local_scheduler` roda em `threading.Thread` com `time.sleep()` síncrono. Se
o pipeline lançar exceção não capturada por `_run_pipeline_once`, o `while True` do
scheduler continua rodando mas sem executar o pipeline. Além disso, `time.sleep()`
bloqueia a thread de forma rígida — sem possibilidade de cancelamento gracioso no
shutdown.

### 2.9 Pontos Positivos Observados

- **[FATO]** `app/security.py`: Usa `secrets.compare_digest` contra timing attacks,
  bloqueia chaves < 32 chars em produção, suporta rotação de chave com
  `PUBLISH_API_KEY_PREVIOUS`.
- **[FATO]** `app/main.py:108-117`: CORS fail-closed. Proíbe wildcard com credenciais,
  exige origens explícitas em produção.
- **[FATO]** `app/publisher.py:32-85`: Idempotência com ledger `ArticleIdentity` +
  `with_for_update()` protege contra publicação duplicada.
- **[FATO]** `database.py:36-46`: Fallback defensivo de driver `postgresql://` →
  `postgresql+psycopg2://` com retry loop.
- **[FATO]** `rewrite_tasks.py:101`: Usa `with_for_update(skip_locked=True)` para
  processar artigos sem lock contention entre workers.
- **[FATO]** `maintenance.py:77-87`: Job diário de expurgo de `PageView` com retenção de
  30 dias já implementado.

---

## 3. Diagnósticos de Auditoria — Frontend

### 3.1 🟡 ALTO — CDN Icons como Dependência Externa Bloqueante

**Arquivo:** `frontend/src/app/layout.tsx:42-43`

**[FATO]** O `<head>` carrega dois CSS externos do `cdn-uicons.flaticon.com` como
`<link rel="stylesheet">`. Esses recursos são **render-blocking** — o browser pausa a
renderização até completar o download. Se o CDN ficar lento ou indisponível, o site
inteiro fica com tela branca.

**[INFERÊNCIA]** Impacto direto no LCP (Largest Contentful Paint) e na nota do Core Web
Vitals.

### 3.2 🟡 ALTO — `dangerouslySetInnerHTML` com Conteúdo LLM

**Arquivo:** `frontend/src/app/noticia/[slug]/page.tsx:232`

**[FATO]** O corpo do artigo é renderizado com
`dangerouslySetInnerHTML={{ __html: bodyHtml }}`. O conteúdo vem de
`formatArticleContent()`, que aplica `escapeHtml` antes de processar. Porém, o pipeline
inline de markdown reconverte para tags HTML (`<strong>`, `<em>`, `<h2>`, etc),
reintroduzindo possibilidade de XSS se o escape falhar em edge cases.

**[FATO POSITIVO]** O Caddyfile aplica CSP sem `unsafe-eval` com
`script-src 'self' 'unsafe-inline'`, mitigando a maioria dos vetores de XSS.

### 3.3 🟡 ALTO — Tipagem de `image_url` com Double Cast

**Arquivo:** `frontend/src/app/noticia/[slug]/page.tsx:77-80`

**[FATO]** `image_url` é acessada via `(article as unknown as { image_url?: string }).image_url`
— um double cast que ignora o tipo `Article` já definido em `api.ts` (que contém
`image_url?: string`). Isso indica desalinhamento entre o tipo e o uso.

### 3.4 🟢 MODERADO — Ausência de `not-found.tsx` Customizado

**[FATO]** Não existe arquivo `not-found.tsx` na raiz de `app/`. A chamada `notFound()` em
`noticia/[slug]/page.tsx:73` usa o fallback genérico do Next.js. Isso quebra a
experiência editorial do portal.

### 3.5 🟢 MODERADO — Home Carrega 80 Artigos por Requisição

**Arquivo:** `frontend/src/app/page.tsx:77`

**[FATO]** A home faz `fetchNewsResponse({ region: "ms", limit: 80, sortBy: "recent" })`.
Com 80 artigos completos (incluindo `content` com corpo de 700-900 palavras cada), o
payload JSON é pesado. Apenas ~10 artigos são exibidos no HeroGrid.

### 3.6 🟢 MODERADO — Sem Loading Skeleton para a Página de Artigo

**[FATO]** Existe `loading.tsx` na raiz, mas não existe `loading.tsx` dentro de
`noticia/[slug]/`, causando flash de tela branca durante navegação client-side para
artigos.

### 3.7 Pontos Positivos Observados

- **[FATO]** Error boundary com design editorial consistente em `error.tsx`.
- **[FATO]** SEO completo: metadata dinâmica por página, JSON-LD Organization+WebSite,
  OpenGraph, Twitter cards, sitemap dinâmico e news sitemap.
- **[FATO]** `Tracker.tsx` usa `useRef` para deduplicar tracking no StrictMode e
  `keepalive: true` para fire-and-forget.
- **[FATO]** `api.ts` valida rigorosamente o contrato da API com `articleFromJson()`,
  sanitiza URLs de fontes e aplica timeout de 10s com `AbortSignal.timeout`.
- **[FATO]** `formatArticle.ts` remove lixo de scraper (bylines, datas, CTAs de
  WhatsApp), detecta muros de texto e os quebra em parágrafos de ~55 palavras.
- **[FATO]** `globals.css` respeita `prefers-reduced-motion` desabilitando animações.
- **[FATO]** `rankHomepageArticles` usa timezone local de Campo Grande para priorizar
  reportagem do dia.

---

## 4. Escopo de Melhorias — Backend

### MEL-B01 | Corrigir Rate Limiter para Proxy Reverso

**Severidade:** 🔴 Crítica
**Impacto:** Rate limiting aplicado incorretamente a todos os usuários

**Ações:**
1. Adicionar `ProxyHeadersMiddleware` do Uvicorn ao FastAPI, configurando `trusted_hosts`
   com os IPs do Caddy
2. Alterar `_is_rate_limited` para extrair IP de `X-Forwarded-For` com validação de proxy
   confiável
3. Substituir instanciação avulsa de `redis.Redis.from_url()` por um `ConnectionPool`
   compartilhado a nível de módulo
4. Substituir `incr` + `expire` separados por pipeline Redis atômico (ou Lua script)
5. Adicionar teste unitário que simula `X-Forwarded-For` com proxy reverso

**Arquivos afetados:** `app/rate_limit.py`, `app/analytics_routes.py`, `app/main.py`

### MEL-B02 | Paginar o Endpoint Editorial com Cálculo Assíncrono

**Severidade:** 🔴 Crítica
**Impacto:** OOM e travamento de thread em produção

**Ações:**
1. Substituir `.limit(2000)` por paginação com cursor (`limit=50`, `offset`)
2. Selecionar apenas campos necessários (sem `content` completo) via
   `.options(load_only(...))`
3. Mover cálculo de `review_natural_writing` para execução sob demanda (endpoint separado
   por slug) ou pré-cálculo em task Celery
4. Adicionar teste de carga que valide o tempo de resposta sob 1.000 artigos

**Arquivos afetados:** `app/editorial_routes.py`

### MEL-B03 | Isolar Health Check em Fila Dedicada

**Severidade:** 🔴 Crítica
**Impacto:** Desbloqueio imediato da fila principal do Celery

**Ações:**
1. Adicionar `"options": {"queue": "monitoring"}` ao beat_schedule de
   `system-health-check` e `report-metrics`
2. Subir um segundo worker com `-Q monitoring -c 1` (ou rota para fila existente)
3. Alternativa mínima: aumentar intervalo de health check para 15 min e adicionar
   `expires=270` para descartar tarefas obsoletas
4. Adicionar teste unitário que valide a configuração de fila no `beat_schedule`

**Arquivos afetados:** `app/celery_app.py`, `docker-compose.yml`, `docker-stack.swarm.yml`

### MEL-B04 | Adicionar Rollback e Migrar Analytics para Depends

**Severidade:** 🟡 Alta
**Impacto:** Prevenção de conexões corrompidas no pool

**Ações:**
1. Adicionar `db.rollback()` no bloco `except` de `track_pageview`
2. Substituir `db = get_session()` por `db: Session = Depends(get_db)` usando um context
   manager com rollback automático
3. Criar o dependency `get_db` como generator `yield`/`finally`

**Arquivos afetados:** `app/analytics_routes.py`, `app/database.py`

### MEL-B05 | Implementar Failover de Provedores LLM

**Severidade:** 🟡 Alta
**Impacto:** Resiliência do pipeline de reescrita

**Ações:**
1. Refatorar `LLMClient` para aceitar uma lista ordenada de provedores (`FALLBACK_CHAIN`)
2. Se o provedor principal retornar 429, tentar automaticamente o seguinte na cadeia
3. Reduzir backoff máximo (cap em 60s total, não 310s)
4. Substituir retorno `""` por `raise LLMUnavailableError` para forçar o caller a tratar
   o erro explicitamente
5. Adicionar métrica de contagem de fallbacks para observabilidade

**Arquivos afetados:** `app/llm_client.py`, `app/tasks/rewrite_tasks.py`

### MEL-B06 | Fulltext Search para Fontes Relacionadas

**Severidade:** 🟢 Moderada
**Impacto:** Performance de busca em base crescente

**Ações:**
1. Criar migration Alembic adicionando índice GIN `tsvector` na coluna `title` de
   `news_articles`
2. Substituir loop Python por query `ts_rank_cd` + `to_tsquery` do PostgreSQL
3. Eliminar o `.limit(300).all()` que carrega artigos completos na memória
4. Adicionar teste de integração que verifica a qualidade do match

**Arquivos afetados:** `app/tasks/rewrite_tasks.py`, nova migration Alembic

### MEL-B07 | Reduzir Sampling do Sentry

**Severidade:** 🟢 Moderada

**Ações:**
1. Alterar `traces_sample_rate` para `0.1` e `profiles_sample_rate` para `0.05`
2. Manter 100% apenas em produção se houver cota enterprise

**Arquivos afetados:** `app/main.py`

### MEL-B08 | Dependency Injection Consistente para Sessões DB

**Severidade:** 🟢 Moderada
**Impacto:** Padronização e prevenção de leaks de conexão

**Ações:**
1. Criar um FastAPI dependency `get_db()` como generator: `yield SessionLocal()` →
   `finally: db.close()`
2. Migrar todas as rotas para usar `Depends(get_db)` em vez de `get_session()` manual
3. Eliminar blocos `try/finally` com `db.close()` redundantes nos handlers

**Arquivos afetados:** `app/database.py`, `app/main.py`, `app/analytics_routes.py`,
`app/editorial_routes.py`, `app/operations_routes.py`

---

## 5. Escopo de Melhorias — Frontend

### MEL-F01 | Internalizar Icons e Eliminar CDN Bloqueante

**Severidade:** 🟡 Alta
**Impacto:** Melhoria direta no LCP e eliminação de ponto de falha externo

**Ações:**
1. Substituir os dois `<link>` de `cdn-uicons.flaticon.com` por ícones SVG inline ou
   componente React (ex: `lucide-react` ou sprite SVG local)
2. Se os ícones do Flaticon forem imprescindíveis, fazer bundle no build (download +
   inclusão em `public/`)
3. Remover as duas entradas do CSP `style-src` e `font-src` do Caddyfile referentes ao
   `cdn-uicons.flaticon.com`

**Arquivos afetados:** `frontend/src/app/layout.tsx`, `frontend/src/components/Icon.tsx`,
`Caddyfile`

### MEL-F02 | Reduzir Payload da Home de 80 para ~20 Artigos

**Severidade:** 🟡 Alta
**Impacto:** Redução drástica do TTFB e consumo de memória do SSR

**Ações:**
1. Alterar `fetchNewsResponse({ limit: 80 })` para `limit: 20` na home
2. Criar endpoint backend `/api/news/headlines` que retorna apenas `title`, `slug`,
   `category`, `image_url`, `summary`, `published_at` (sem `content`)
3. Se o ranking de 80 artigos for necessário, implementar o ranking server-side na API

**Arquivos afetados:** `frontend/src/app/page.tsx`, potencialmente `app/main.py`

### MEL-F03 | Sanitização Reforçada do `dangerouslySetInnerHTML`

**Severidade:** 🟡 Alta
**Impacto:** Camada adicional de defesa contra XSS

**Ações:**
1. Instalar `isomorphic-dompurify` ou `sanitize-html`
2. Passar o output de `formatArticleContent()` pelo sanitizer antes de injetar no DOM
3. Whitelist apenas: `p`, `h2`, `strong`, `em`, `ul`, `li`, `blockquote`, `div` com
   classe `assinatura`

**Arquivos afetados:** `frontend/src/app/noticia/[slug]/page.tsx`,
`frontend/src/lib/formatArticle.ts`

### MEL-F04 | Criar `not-found.tsx` e `loading.tsx` para Artigos

**Severidade:** 🟢 Moderada
**Impacto:** UX consistente e editorial

**Ações:**
1. Criar `frontend/src/app/not-found.tsx` com design editorial (similar ao `error.tsx`)
2. Criar `frontend/src/app/noticia/[slug]/loading.tsx` com skeleton que imita o layout do
   artigo (hero, byline, corpo)

**Arquivos afetados:** Novos arquivos

### MEL-F05 | Corrigir Double Cast de `image_url`

**Severidade:** 🟢 Baixa

**Ações:**
1. Substituir `(article as unknown as { image_url?: string }).image_url` por
   `article.image_url` direto — o tipo `Article` já possui essa propriedade

**Arquivos afetados:** `frontend/src/app/noticia/[slug]/page.tsx:77-80`

### MEL-F06 | Implementar Acessibilidade ARIA Completa

**Severidade:** 🟢 Moderada
**Impacto:** Conformidade WCAG 2.1 AA

**Ações:**
1. Adicionar `aria-current="page"` na navegação ativa (`NavMenu.tsx`, `DesktopNav`)
2. Garantir que todos os botões interativos (share, mobile menu) tenham `aria-expanded`
3. Verificar contraste de cores no tema editorial (especialmente `text-muted` sobre
   `canvas`)
4. Adicionar `skip-to-content` link no layout

**Arquivos afetados:** `frontend/src/app/layout.tsx`,
`frontend/src/components/NavMenu.tsx`, `frontend/src/components/Header.tsx`

---

## 6. Matriz de Priorização

| # | Item | Sev. | Esforço | Risco se ignorar | Prioridade |
|---|---|---|---|---|---|
| MEL-B01 | Rate Limiter + Redis Pool | 🔴 | Médio | Todos os usuários bloqueados em prod | **P0** |
| MEL-B02 | Paginação Editorial | 🔴 | Médio | OOM / travamento do Uvicorn | **P0** |
| MEL-B03 | Fila Celery dedicada | 🔴 | Baixo | Fila congestionada, pipeline parado | **P0** |
| MEL-B04 | Rollback + Depends analytics | 🟡 | Baixo | Pool de conexões corrompido | **P1** |
| MEL-F01 | Internalizar ícones | 🟡 | Médio | CWV degradado, ponto de falha externo | **P1** |
| MEL-F02 | Reduzir payload home | 🟡 | Baixo | TTFB lento, desperdício de banda | **P1** |
| MEL-F03 | Sanitizer HTML | 🟡 | Baixo | Vetor XSS residual | **P1** |
| MEL-B05 | Failover LLM | 🟡 | Alto | Pipeline parado em cota esgotada | **P2** |
| MEL-B06 | Fulltext search | 🟢 | Médio | Degradação progressiva de performance | **P2** |
| MEL-F04 | not-found + loading | 🟢 | Baixo | UX inconsistente | **P2** |
| MEL-B07 | Sentry sampling | 🟢 | Baixo | Overhead e cota excedida | **P3** |
| MEL-B08 | DI consistente | 🟢 | Médio | Dívida técnica acumulada | **P3** |
| MEL-F05 | Fix double cast | 🟢 | Trivial | Confusão de tipagem | **P3** |
| MEL-F06 | Acessibilidade ARIA | 🟢 | Médio | Não-conformidade WCAG | **P3** |

---

## 7. Fases de Execução Sugeridas

### Fase A — Estabilização Crítica (P0)
> **Objetivo:** Eliminar os 3 riscos que podem derrubar produção
> **Estimativa:** 2-3 dias de desenvolvimento + testes
> **Escopo:** MEL-B01, MEL-B02, MEL-B03

### Fase B — Hardening (P1)
> **Objetivo:** Corrigir vulnerabilidades, performance e UX
> **Estimativa:** 2-3 dias
> **Escopo:** MEL-B04, MEL-F01, MEL-F02, MEL-F03

### Fase C — Evolução (P2)
> **Objetivo:** Resiliência avançada e refinamento
> **Estimativa:** 3-5 dias
> **Escopo:** MEL-B05, MEL-B06, MEL-F04

### Fase D — Dívida Técnica (P3)
> **Objetivo:** Padronização e polimento
> **Estimativa:** 2-3 dias
> **Escopo:** MEL-B07, MEL-B08, MEL-F05, MEL-F06

---

## 8. Desconhecidos Registrados

| # | Item | Impacto Potencial |
|---|---|---|
| U-01 | Volume real de tráfego diário em produção | Determina se MEL-B01 é urgência imediata ou preventiva |
| U-02 | Cota efetiva do provedor LLM em uso | Define se o backoff de 310s é atingido regularmente |
| U-03 | Frequência de uso do painel editorial por editores | Determina a urgência de MEL-B02 |
| U-04 | Métricas Lighthouse/CWV em produção | Confirma impacto real de MEL-F01 e MEL-F02 |
| U-05 | Existência de monitoramento externo (UptimeRobot, etc) | Pode tornar o `system_health_check` interno redundante |

---

> **Nota de conformidade:** Este documento é um escopo de melhoria técnica.
> Nenhuma implementação será iniciada antes da aprovação explícita do usuário,
> conforme regra pétrea do `AGENTS.md`.
