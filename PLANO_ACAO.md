# PLANO DE AÇÃO — Portal Cerrado para 100% GO-LIVE

**Data:** 31/08/2026
**Status atual:** 75-80% real (Backend 85%, Frontend 90%, Infra 60%)
**Meta:** 100% operacional em produção com AdSense apto
**Esforço total:** ~15h divididas em 3 Sprints (3 dias)
**Dono:** Tech Lead + (opcional) apoio DevOps

---

## 1. VISÃO GERAL E MILESTONES

```
[HOJE] SPRINT 1 — QUALIDADE (4h) ──▶ SPRINT 2 — DEPLOY (6h) ──▶ SPRINT 3 — HOMOLOGAÇÃO + ADSENSE (5h) ──▶ GO-LIVE 🚀
         │                              │                              │
         ▼                              ▼                              ▼
   M1: Lixo zerado                M2: VPS no ar                  M3: 50+ matérias/dia + PageSpeed >80 + AdSense aplicado
   Critério: 0 títulos            Critério: https://              Critério: 100% das tasks reais
   genéricos em articles.json     portalcerrado.com.br             + 0 stubs + testes verdes
                                  com SSL + /health OK
```

### KPIs de Sucesso (pós GO-LIVE)

| Métrica | Alvo D+7 | Alvo D+30 | Como medir |
|---------|----------|-----------|------------|
| Matérias/dia | 30+ | 50+ | `SELECT count(*) FROM news_articles WHERE published_at::date = today` |
| Taxa erro scanner | <5% | <1% | `logs + celery flower` |
| Uptime | 99% | 99.5% | UptimeRobot |
| PageSpeed Mobile | >75 | >85 | PageSpeed Insights |
| Tempo pipeline scan→publish | <15min | <5min | `celery logs` |

---

## 2. BACKLOG PRIORIZADO (P0=Crítico, P1=Importante, P2=Desejável)

### SPRINT 1 — CORREÇÃO DE QUALIDADE [P0] — 4h — BLOQUEIA TUDO

**Objetivo:** Eliminar conteúdo genérico que reprova AdSense.

| ID | Tarefa | Arquivos | Tempo | Critério de Aceite (DoD) |
|----|--------|----------|-------|---------------------------|
| **1.1** | **Fix Filtro Scanner — bloquear lixo** | `app/scanner.py::_is_valid_article` `app/filter.py` | 45min | `articles.json` após `python scripts/update_frontend_articles.py` tem **0** títulos `"O Estado Online"` isolado, 0 `homepage-nova`, 0 `mercedita` placeholder. Regras: `len(title.split())>=5`, `title.lower()!=source.lower()`, `len(content)>200`, url não contém `/homepage`, `/search`, `/feed`. Teste: rodar `scan_all` 2x e validar `inserted` sem duplicata genérica. |
| **1.2** | **Fix Slug Publisher — colisão** | `app/publisher.py:_generate_slug` `app/tasks/scan_tasks.py:_make_draft_slug` | 30min | Re-publicar 3x mesmo título gera slugs únicos `titulo-abc123-1`, `-2` etc. Teste: inserir 3 artigos com mesmo título, verificar `slug` distintos no DB. |
| **1.3** | **Limpeza DB + Regerar Frontend** | `data/atualiza_brasil.db` + `frontend/src/data/articles.json` | 30min | Deletar ids 25,26,27,10 genéricos: `DELETE FROM news_articles WHERE title='O Estado Online'`; Rodar `export_frontend_articles_to_files(limit=100)`; `npm --prefix frontend run build -- --webpack` sem erro; `cat articles.json | jq '.[].title' | grep -c "O Estado Online"` == 0 para títulos genéricos. |
| **1.4** | **Segurança — Rotacionar GROQ key** | `.env`, `.env.example`, `config` | 30min | Gerar nova key em `console.groq.com` → atualizar `.env` local + não versionado; `.env.example` só com `gsk_XXX_PLACEHOLDER`; `git rm --cached .env` se versionado; `echo ".env" >> .gitignore`; `git log --all -- .env` não mostra key antiga. |
| **1.5** | **Mapear Repórter Fantasma** | `app/scanner.py:REPORTER_BY_CATEGORY` `config/reporters.yml` | 30min | `fernanda.lima→lucas.nakamura`, `pedro.mendes→leon.vaz`, `carlos.nunes→camila.rocha`. Teste: `python -c "from app.scanner import RealPortalScanner; print(RealPortalScanner.REPORTER_BY_CATEGORY)"` sem slugs inexistentes. |
| **1.6** | **Validação manual pipeline** | `app/tasks/scan_tasks.py:run_full_pipeline` | 60min | Executar **sem Celery** (local scheduler): `ENABLE_LOCAL_SCHEDULER=1 python -m app.main` ou `python -c "from app.tasks.scan_tasks import run_full_pipeline; run_full_pipeline()"` → logs mostram `Persistidos: inserted>=5`, `Classificados: classified>=5`, `Reescritos: rewritten>=3`, `Publicados: published>=3`, `Exportados: exported>=3`. Verificar `http://localhost:8000/api/news?limit=3` retorna 3 com `content` >500 palavras. |

**Entregável Sprint 1:** Vídeo/print de `http://localhost:3000` sem cards genéricos + `articles.json` limpo + `git commit fix: qualidade scraper e slug`

### SPRINT 2 — DEPLOY VPS + INFRA REAL [P0] — 6h

**Objetivo:** Sair do localhost para produção.

| ID | Tarefa | Tempo | Passos & Comando de Validação |
|----|--------|-------|-------------------------------|
| **2.1** | **Provisionar VPS** | 45min | Hetzner CX21 (4GB/2vCPU/80GB) Ubuntu 22.04 Frankfurt. Criar SSH key, firewall `ufw allow 22,80,443`. Validação: `ssh portal@IP "docker --version"` |
| **2.2** | **Instalar Docker + Deps** | 30min | Seguir `DEPLOY.md#3`: `docker-ce + compose-plugin`. Validação: `docker compose version && docker ps` |
| **2.3** | **Enviar projeto + .env prod** | 30min | `rsync -avz --exclude .git --exclude __pycache__ --exclude .venv --exclude data/*.db . portal@IP:/home/portal/atualiza-brasil/` + criar `.env` prod (GROQ nova key, `ENVIRONMENT=production`, `DEBUG=false`, `NEXT_PUBLIC_SITE_URL=https://portalcerrado.com.br`, `DATABASE_URL=postgresql://...`). Validação: `ssh portal@IP "cat atualiza-brasil/.env \| grep GROQ"` |
| **2.4** | **Subir stack + Migrations** | 45min | `docker compose up -d --build` → 7 containers `running`. `docker compose exec atualiza_brasil python -c "from app.database import init_db; init_db(); print('ok')"` + verificar `psql -c "\dt"` com 5 tabelas. Validação: `curl http://localhost:8000/health` → `{"status":"healthy","articles_count":N}` |
| **2.5** | **Nginx + SSL + Domínio** | 60min | Cloudflare DNS `A @ → IP` + `A www → IP`. `certbot --nginx -d portalcerrado.com.br -d www.portalcerrado.com.br` ou Cloudflare Origin cert. Validação: `https://portalcerrado.com.br` com cadeado, `curl -I https://portalcerrado.com.br | grep 200`, `frontend` em `:3000` proxy. |
| **2.6** | **Ativar Workers Reais** | 30min | `docker compose logs celery_worker -f` mostra `[PIPELINE] Iniciando a cada 30min`; `docker compose exec celery_worker celery -A app.celery_app inspect active` responde. Desligar `LOCAL_SCHEDULER` em prod: `CELERY_SCHEDULER=1` ou `ENABLE_LOCAL_SCHEDULER=0`. Validação: aguardar 35min e ver `SELECT count(*) FROM news_articles WHERE created_at > now()-interval '1 hour'` aumentou. |
| **2.7** | **Implementar maintenance REAL** | 60min | Editar `app/tasks/maintenance.py`: `cleanup_old_content` → `DELETE FROM news_articles WHERE status='draft' AND created_at < now()-7d`; `update_sitemap` → gerar `frontend/public/sitemap.xml` real (iterar `published`); `report_metrics` → contar `articles_today/this_hour`; `system_health_check` → ping DB+Redis real. Teste: `docker compose exec atualiza_brasil python -c "from app.tasks.maintenance import cleanup_old_content; print(cleanup_old_content())"` retorna `cleaned>0` se houver lixo. |

**Entregável Sprint 2:** URL pública `https://portalcerrado.com.br` no ar, 3 matérias novas em 1h via Celery, `flower` em `:5555` com tasks verdes.

### SPRINT 3 — HOMOLOGAÇÃO, TESTES E ADSENSE [P1] — 5h

| ID | Tarefa | Tempo | Critério |
|----|--------|-------|----------|
| **3.1** | **Testes automatizados** | 60min | Criar `tests/unit/test_filter.py` (duplicata, sensível), `test_classifier.py` (tier), `tests/integration/test_pipeline.py` (scan→classify→publish mock). `pip install pytest` + `pytest -v` 100% verde. Add `requirements.txt` e CI `github/workflows/test.yml`. |
| **3.2** | **Frontend gaps** | 60min | Criar `frontend/src/app/loading.tsx` (skeleton), `frontend/src/app/categoria/[slug]/page.tsx`, `components/AdSense.tsx` (placeholder), `next/image` para `image_url`, paginação real `?page=`. `npm run lint` 0 erros. |
| **3.3** | **SEO + Performance** | 45min | Verificar `sitemap.ts` dinâmico (via `getAllRealArticles` ou API), `robots.ts` `allow:/`, meta OG nos 3 layouts, `next.config.ts` `images.remotePatterns` já ok. Rodar `npx next build` < 6s, Lighthouse >80. |
| **3.4** | **Monitoramento** | 45min | Sentry gratuito (`SENTRY_DSN` no `.env`), UptimeRobot monitor `https://portalcerrado.com.br/health` a cada 5min + alerta email/Telegram, `docker stats` <70% RAM. |
| **3.5** | **Carga AdSense — 50 matérias** | 60min | Deixar pipeline rodar 24h OU forçar `for i in {1..3}; do docker compose exec atualiza_brasil python -c "from app.tasks.scan_tasks import run_full_pipeline; run_full_pipeline()"; sleep 1800; done` até `SELECT count(*) WHERE status='published'` >=50. Validar 0 genéricos, 9 repórteres com `articles_published>0`. |
| **3.6** | **Aplicação AdSense** | 30min | Criar conta AdSense, adicionar `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXX">` em `frontend/src/app/layout.tsx`, enviar domínio, aguardar 1-2 semanas. |

**Entregável Sprint 3:** `pytest 5 passed`, Lighthouse 85, 50+ matérias publicadas, AdSense em "Em análise".

---

## 3. CRONOGRAMA VISUAL (3 DIAS)

```
DIA 1 (4h) — SPRINT 1 QUALIDADE
09:00-09:45  1.1 Filtro scanner
09:45-10:15  1.2 Slug fix
10:15-10:45  1.3 Limpeza DB + rebuild
10:45-11:15  1.4 Rotacionar key
11:15-11:45  1.5 Repórter map
11:45-12:45  1.6 Pipeline manual E2E ✅ M1

DIA 2 (6h) — SPRINT 2 DEPLOY
09:00-09:45  2.1 VPS
09:45-10:15  2.2 Docker
10:15-10:45  2.3 rsync + env prod
10:45-11:30  2.4 Stack + DB
11:30-12:30  2.5 Nginx/SSL/DNS
12:30-13:00  2.6 Workers cel
13:00-14:00  2.7 Maintenance real ✅ M2

DIA 3 (5h) — SPRINT 3 HOMOLOGAÇÃO
09:00-10:00  3.1 Tests
10:00-11:00  3.2 Frontend gaps
11:00-11:45  3.3 SEO perf
11:45-12:30  3.4 Monitoramento
12:30-13:30  3.5 Carga 50 matérias
13:30-14:00  3.6 AdSense ✅ M3 → GO
```

---

## 4. RISCOS E MITIGAÇÃO

| Risco | Prob. | Impacto | Mitigação | Plano B |
|-------|-------|---------|-----------|---------|
| VPS Hetzner sem estoque Frankfurt | Média | Atraso 1d | Usar Nuremberg ou DigitalOcean `s-2vcpu-4gb` | Vultr |
| Groq 429 (14 req/min) | Alta | Reescrita falha | `rewrite_pending_articles` já limita 50; adicionar `time.sleep(5)` por artigo se `groq.api_key` | Fallback local já existe |
| Cloudflare SSL Full Strict erro | Baixa | Site fora | Começar com `Flexible` + depois `Full` | Let's Encrypt direto |
| AdSense reprova por conteúdo fino | Média | Perda 2 semanas | Sprint 1 garante 0 genérico + 500+ palavras via `article_fetcher` | Reaplicar após ajuste |

---

## 5. DEFINIÇÃO DE PRONTO (DoD) PARA GO-LIVE

- [ ] `docker compose ps` mostra 7 containers `healthy/running` há 24h
- [ ] `curl https://portalcerrado.com.br/health` → `healthy` + `articles_count >=50`
- [ ] `curl https://portalcerrado.com.br/api/news?limit=5` retorna 5 com `content` >600 palavras
- [ ] `https://portalcerrado.com.br/sitemap.xml` tem >=50 `<url>` dinâmicos
- [ ] `https://portalcerrado.com.br/robots.txt` permite e aponta sitemap
- [ ] Lighthouse mobile `Performance >80, SEO >90`
- [ ] `pytest -v` 100% verde local e no VPS
- [ ] UptimeRobot 24h sem downtime + Flower sem `failed` >5%
- [ ] AdSense tag instalada e domínio verificado

---

## 6. COMANDOS DE VALIDAÇÃO RÁPIDA (colar no terminal)

```bash
# SPRINT 1 — validação local
python -c "from app.scanner import RealPortalScanner; s=RealPortalScanner(); r=s.scan_all(); print(r['summary'])"
python scripts/update_frontend_articles.py && cat frontend/src/data/articles.json | jq '.[].title' | grep -c "O Estado Online" # esperado 0 genérico isolado
python -c "from app.tasks.scan_tasks import run_full_pipeline; print(run_full_pipeline())"
curl -s http://localhost:8000/health | jq
curl -s "http://localhost:8000/api/news?limit=2" | jq '.news[0].title, .news[0].content | length'

# SPRINT 2 — validação prod
ssh portal@SEU_IP "docker compose -f ~/atualiza-brasil/docker-compose.yml ps"
ssh portal@SEU_IP "curl -s http://localhost:8000/health | jq"
ssh portal@SEU_IP "docker compose exec postgres psql -U portal_user -d atualiza_brasil -c 'SELECT status, count(*) FROM news_articles GROUP BY status;'"
curl -s https://portalcerrado.com.br/api/news?limit=1 | jq

# SPRINT 3 — qualidade
pytest -v
npm --prefix frontend run build -- --webpack
npx --prefix frontend next lint
```

---

## 7. PRÓXIMA AÇÃO IMEDIATA (15 min)

1. Decida: **Rodar Sprint 1 agora?** (recomendado sim — é local e desbloqueia tudo)
2. Me diga: **Hetzner ou DigitalOcean?** e se já tem domínio `portalcerrado.com.br` registrado
3. Eu já preparo o **patch 1.1+1.2** (scanner+publisher) e deixo o `articles.json` limpo — confirma?

---
**Arquivo gerado em:** `PLANO_ACAO.md` — pode compartilhar com time ou imprimir como checklist.
Pronto para executar. Qual Sprint quer começar?
