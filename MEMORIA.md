# MEMÓRIA — BotGram / Portal Cerrado
> Última atualização: 2026-08-31 23:12 (America/Sao_Paulo)
> Salvo para não esquecer a infra do projeto

## Infraestrutura Canônica (NÃO ESQUECER)

- **Projeto:** BotGram / Portal Cerrado — portal de notícias automatizado 9 repórteres, 50+ matérias/dia, compatível AdSense
- **Máquina servidor:** `Razuk` — Debian/Ubuntu local, **gerenciado via Portainer** (Stacks), NÃO é VPS externo
  - **IP Tailscale servidor:** `100.95.111.24` (`razuk.tailab4f1d.ts.net`)
  - **Portainer:** `http://100.95.111.24:9000` ou `:9443` → `Stacks` → Stack `atualiza-brasil`/`BotGram`
  - **Serviços docker-compose:** `postgres:15`, `redis:7-alpine`, `atualiza_brasil:8000`, `celery_worker`, `celery_beat`, `flower:5555`, `frontend:3000`
  - **Volumes:** `postgres_data` (prod), `data/atualiza_brasil.db` é só local dev (sqlite fallback)

- **Máquina cliente/dev:** `razuk-lenovo-ideapad-s145-15iwl`
  - **IP Tailscale cliente:** `100.87.26.29`
  - **Path projeto:** `/home/razuk/Documents/BotGram`
  - **SSH key:** `~/.ssh/id_ed25519` → pública `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOhZBSoMiHjS867EQgdCOKk07nLT2spmuZZOqZ7QCzMC ap2web@local` (essa é a que precisa autorizar no servidor se usar ssh direto; mas com Portainer não precisa)

- **Tailscale rede:** `tailab4f1d.ts.net`, relay `sao`, node `Razuk` online 2026-08-31

## Estado Atual (31/08/2026 23:09)

- **DB local (sqlite):** 51 `published`, 0 `draft`, success 100%, 13 nas últimas 2h, min 575 palavras max 1018
- **Frontend JSON:** `frontend/src/data/articles.json` = 51, `frontend/public/articles.json` wrapper = 51
- **Sitemap:** `frontend/public/sitemap.xml` = 56 urls (51 + 5 estáticas) com `https://portalcerrado.com.br` (prod) — regenerado após build que resetou para localhost
- **Testes:** `pytest tests/ -v` = 23 passed (fix `frontend_tasks.py` sources str/dict)
- **Build:** `npm --prefix frontend run build -- --webpack` OK 4.7s, 18 pages
- **Health:** `system_health_check` = healthy (DB ok 51, Redis fail tolerado local scheduler, Celery ok)
- **Servidor Portainer:** STALE 28 matérias de 28/08 com `Homepage Nova` genérico — precisa `Pull and redeploy` para 51

## Decisões Canônicas

- **Nunca usar VPS externo** — servidor é a máquina Debian local com Portainer
- **Deploy via Portainer Stack**, não via `docker compose` local
  - Se Stack via Git: `Pull and redeploy` no Portainer
  - Se via Web editor: colar `docker-compose.yml` novo + env vars
- **DB prod é postgres**, não sqlite — não fazer rsync de `data/*.db`, deixar pipeline recriar no servidor (scan + curiosities + Groq)
- **Sitemap deve ser prod** `https://portalcerrado.com.br` — `docker-compose.yml` já default para isso, e `frontend/Dockerfile` já `ENV NEXT_PUBLIC_SITE_URL=https://portalcerrado.com.br`

## Comandos de Validação Rápida

```bash
# local
pytest tests/ -q
python -c "from app.tasks.maintenance import system_health_check; print(system_health_check())"
grep -c "portalcerrado.com.br" frontend/public/sitemap.xml # 56
python3 -c "import json; print(len(json.load(open('frontend/src/data/articles.json'))))" # 51

# no Portainer console (atualiza_brasil_app)
python -c "from app.tasks.scan_tasks import run_full_pipeline; print(run_full_pipeline())"
python -c "from app.tasks.frontend_tasks import export_frontend_articles_to_files; print(export_frontend_articles_to_files(100))"
python -c "from app.tasks.maintenance import update_sitemap; print(update_sitemap())"
curl -s http://localhost:8000/health | jq
curl -s http://localhost:3000/sitemap.xml | grep -c "portalcerrado.com.br"
```

## Próximo Passo Pendente

- [ ] Portainer: `Stacks` → `Pull and redeploy` (ou Update editor) no `100.95.111.24`
- [ ] Rodar pipeline 1x no container para ir de 28 → 51 se necessário
- [ ] Validar `http://100.95.111.24:3000` e `http://100.95.111.24:8000/health`

## Env Vars Canônicas

```
SITE_URL=https://portalcerrado.com.br
NEXT_PUBLIC_SITE_URL=https://portalcerrado.com.br
NEXT_PUBLIC_API_URL=http://atualiza_brasil:8000
GROQ_API_KEY=gsk_... (em .env, não versionado)
GROQ_MODEL=qwen/qwen3-32b
DATABASE_URL=postgresql://portal_user:portal_pass@postgres:5432/atualiza_brasil
REDIS_URL=redis://redis:6379/0
```

---
*Este arquivo é a fonte da verdade da infra. Atualize sempre que mudar IP, Stack ou método de deploy.*
