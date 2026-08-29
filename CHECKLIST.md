# CHECKLIST — O que falta para 100%

**Data:** 28/08/2026 18:55
**Status Atual:** 90% — Frontend online

---

## ✅ JÁ FEITO (75%)

### Backend (100%)
- [x] Scanner real de portais MS (26 artigos em 28/08)
- [x] Classificador com score e tiers
- [x] Filtro de duplicatas e sensível
- [x] Groq LLM (tradução + reescrita)
- [x] Sistema de curiosidades (90 templates)
- [x] Personalidade e evolução (XP)
- [x] Agente auditor HORUS
- [x] Pipeline completo testado

### Frontend (100% — 28/08 18:55)
- [x] Next.js 16.3.3 + Tailwind 4 + TypeScript + App Router
- [x] Node 20.20.2 via nvm + build --webpack OK + lint 0 erros
- [x] Páginas: Home (hero), /sobre, /privacidade, /termos, /contato, /noticia/[slug]
- [x] Componentes: Header, Footer, NewsCard (3 variantes), CategoryFilter, Ticker
- [x] SEO: metadata + OpenGraph + sitemap.ts + robots.ts
- [x] 26 artigos reais integrados (src/data/articles.json) + fallback automático
- [x] Online em http://localhost:3000 (nohup, HTTP 200 OK)
- [x] Docker: frontend/Dockerfile + docker-compose.yml atualizado
- [x] Script: scripts/update_frontend_articles.py

### Configuração (100%)
- [x] 9 repórteres com vozes
- [x] 25+ fontes globais RSS
- [x] Portal scanner (4 portais MS)
- [x] Glossário EN→PT
- [x] Docker Compose
- [x] .env configurado

### Testes (100%)
- [x] Teste Groq ✅
- [x] Teste scanner ✅
- [x] Teste classificador ✅
- [x] Teste filtro ✅
- [x] Teste pipeline completo ✅
- [x] Teste HORUS ✅

### Documentação (100%)
- [x] SPEC.md
- [x] README.md
- [x] andamento.md (atualizado)
- [x] DEPLOY.md (instruções VPS)
- [x] AUDITORIA.md

---

## 🔴 FALTA (10%)

### A) Frontend Next.js — ✅ CONCLUÍDO 28/08

#### Estrutura base
- [x] `npx create-next-app@latest frontend` — Next.js 16.3.3
- [x] Configurar TypeScript + Tailwind 4
- [x] Node 20.20.2 + build --webpack OK

#### Páginas
- [x] `src/app/page.tsx` — Home (hero + grid, ISR 60s)
- [x] `src/app/sobre/page.tsx`
- [x] `src/app/privacidade/page.tsx`
- [x] `src/app/termos/page.tsx`
- [x] `src/app/contato/page.tsx`
- [x] `src/app/sitemap.ts` — Sitemap dinâmico (26 URLs)
- [x] `src/app/robots.ts`

#### Componentes
- [x] `components/Header.tsx`
- [x] `components/NewsCard.tsx` (hero/compact/default)
- [x] `components/Footer.tsx`
- [x] `components/CategoryFilter.tsx`
- [x] `components/Ticker.tsx`
- [ ] `components/AdSense.tsx` — após aprovação

#### Integrações
- [x] `lib/api.ts` — fallback para 26 reais
- [x] Sitemap dinâmico via API
- [x] Meta tags SEO + OpenGraph
- [x] 26 artigos reais (src/data/articles.json)

#### Estilo
- [x] Responsivo mobile + Tailwind
- [x] Montserrat + tema Atualiza Brasil
- [ ] Loading skeletons (opcional)

#### AdSense
- [ ] Configurar após GO-LIVE

---

### B) Deploy VPS (~2h)

#### Preparação
- [ ] Escolher provedor (Hetzner/DO)
- [ ] Criar conta e configurar billing
- [ ] Provisionar servidor Ubuntu 22.04
- [ ] Configurar SSH keys
- [ ] Criar usuário não-root

#### Infraestrutura
- [ ] Instalar Docker + Docker Compose
- [ ] Configurar firewall (ufw)
- [ ] Configurar timezone (America/Sao_Paulo)

#### Deploy
- [ ] Enviar projeto via rsync/scp
- [ ] Configurar .env no servidor
- [ ] Iniciar containers (`docker-compose up -d`)
- [ ] Verificar todos os serviços rodando
- [ ] Testar API (`curl localhost:8000/health`)

#### Domínio
- [ ] Registrar domínio (se ainda não)
- [ ] Configurar DNS no Cloudflare
- [ ] Configurar SSL (Let's Encrypt)
- [ ] Pointar nginx para domínio

#### Validação E2E
- [ ] Acessar site pelo domínio
- [ ] Verificar SSL (cadeado verde)
- [ ] Testar navegação em todas as páginas
- [ ] Verificar se notícias aparecem
- [ ] Testar mobile (Chrome DevTools)
- [ ] Testar Speed (PageSpeed Insights > 80)

---

### C) Migrações e DB (~1h)

#### Alembic
- [ ] `alembic init alembic`
- [ ] Configurar `alembic.ini` para PostgreSQL
- [ ] Criar migração inicial (`init_schema`)
- [ ] Testar migração local
- [ ] Testar migração em produção

#### Dados de exemplo
- [ ] Seed com categorias
- [ ] Seed com repórteres
- [ ] Seed com notícias de teste (opcional)

---

### D) Monitoramento (~30min)

#### Logs
- [ ] Configurar logging centralizado
- [ ] Rotação de logs (logrotate)
- [ ] Alertas de erro (sentry.io gratuito)

#### Uptime
- [ ] Configurar UptimeRobot (gratuito)
- [ ] Configurar alertas por email
- [ ] Configurar alertas por Telegram

#### Performance
- [ ] Configurar Redis cache
- [ ] Configurar CDN (Cloudflare)
- [ ] Otimizar imagens (next/image)
- [ ] Lazy loading de componentes

---

## 📊 TIMELINE ESTIMADO

```
Dia 1 (4h):   Setup VPS + Deploy backend
Dia 1 (2h):   Configurar nginx + SSL + domínio
Dia 2 (6h):   Frontend base + componentes
Dia 2 (4h):   Páginas + integrações API
Dia 3 (2h):   AdSense + SEO
Dia 3 (1h):   Testes E2E + ajustes
Dia 3 (1h):   Monitoramento + GO-LIVE
```

**Total estimado: ~15 horas**

---

## 🎯 METAS DEPOIS DO GO-LIVE

- [ ] 50+ artigos/dia publicados
- [ ] 9 repórteres ativos
- [ ] 0 erros de scraping por 7 dias
- [ ] PageSpeed > 80
- [ ] Uptime > 99.5%
- [ ] AdSense aprovado
- [ ] 1000 visitantes/mês

---

## ❓ PERGUNTAS ANTES DE CONTINUAR

1. Você já tem domínio registrado?
2. Qual provedor VPS prefere? (Hetzner/DO/Outro)
3. Quer o frontend básico ou com design mais elaborado?
4. Quer incluir AdSense desde o início?
5. Tem tempo para dedicar 4-6h por dia esta semana?

---

## 🚀 PRÓXIMO PASSO

Escolha o que fazer primeiro:

**A)** Começar frontend Next.js (mais demorado, mas essencial)

**B)** Fazer deploy do backend agora (mais rápido, já funciona)

**C)** Ambos em paralelo (se tiver tempo)
