# Evidências de validação — Portal Cerrado

Registro detalhado extraído do plano operacional. O plano principal mantém apenas
decisões, gates e critérios; esta página guarda evidências extensas.

## CI, imagens e performance

- CI publicado com todos os jobs verdes; manifests GHCR consultados no host de teste e digests registrados no relatório de prontidão. Nenhuma stack foi aplicada.
- Auditoria local de performance/SEO: Lighthouse não está instalado; o build produziu 1,36 MB de assets estáticos e 2,06 MB de server bundle, não há tags `<img>` cruas no frontend, as três rotas de metadata existem e `npm audit` offline não encontrou vulnerabilidades altas.

## Higiene e testes

- A auditoria de higiene não encontrou `console.log` ou `debugger`; o `.env.example` teve senha reutilizável convertida para placeholder. Arquivos legados acima de 300 linhas permanecem dívida técnica registrada.
- A auditoria Ruff completa encontrou apenas o bootstrap intencional de `sys.path`; os quatro imports receberam justificativa `E402` localizada.
- A suíte de integração passou com 8 testes; a suíte unitária passou com 120/120 testes.

## Correção técnica de runtime Swarm — 25/09/2026

- Causa: o backend usava DBAPI incompatível com o driver instalado; o healthcheck do Caddy requisitava `/healthz`, ausente no frontend.
- Arquivos: `app/database.py`, `docker-stack.swarm.yml`, `docker-compose.yml`.
- Validação: os 8 serviços `cerrado_test` convergiram em `1/1`; API, frontend e Caddy responderam HTTP 200 com headers de segurança.
- Risco residual: baixo; fallback defensivo e drivers explícitos, sem impacto nos containers standalone de produção.
