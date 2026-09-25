# OPERACAO - Portal Cerrado

## Status Consolidado
- Validação local em 20/09/2026: 84 testes backend, Ruff e mypy aprovados; ESLint e build Next aprovados.
- A validação acima não confirma o estado do Docker Swarm, serviços externos, banco de produção ou provedor LLM.
- O pipeline mede e retorna a duração de scan, classificação, reescrita, publicação e total por execução.

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
| 6 - Validacao Final | local done | divergência entre ambiente local e produção | 84 testes; Ruff, mypy, ESLint e build Next aprovados em 20/09/2026 |

## Guia Operacional
1. Validar banco, API e frontend.
2. Validar pipeline de scan, classify, rewrite, publish.
3. Validar exportacao do frontend.
4. Validar healthchecks e logs.
5. Validar deploy pela stack oficial do ambiente.

## Backup e Restore do Banco

- O utilitário oficial é `venv/bin/python scripts/database_backup.py`.
- Backup local SQLite: `DATABASE_URL=sqlite:///data/portal_cerrado.db venv/bin/python scripts/database_backup.py backup --output /caminho/portal.db`.
- Backup PostgreSQL: `DATABASE_URL="$DATABASE_URL" venv/bin/python scripts/database_backup.py backup --output /caminho/portal.dump`.
- Restore exige confirmação explícita: `venv/bin/python scripts/database_backup.py restore --input /caminho/backup --confirm`.
- Antes de restaurar, interromper writers, confirmar o arquivo e registrar o SHA-256 do backup.
- Retenção operacional: manter backups diários por 30 dias; expurgar somente após confirmar um backup mais novo e um restore de teste.
- O restore de teste deve usar banco isolado; produção permanece bloqueada até o relatório de aceite.
- Evidência local: o round-trip SQLite foi executado em diretório temporário isolado,
  com remoção do banco-fonte, restauração confirmada e validação do registro restaurado.

## Rotação da Chave Editorial

1. Gerar uma nova chave com `openssl rand -hex 32` em um gestor seguro.
2. Definir `PUBLISH_API_KEY_PREVIOUS` com a chave atual e `PUBLISH_API_KEY` com a nova.
3. Reiniciar gradualmente a API e testar `POST /api/publish` com a nova chave.
4. Confirmar que todos os réplicas estão usando a nova configuração.
5. Remover `PUBLISH_API_KEY_PREVIOUS` e reiniciar novamente.
6. Invalidar a chave antiga no gestor de segredos e registrar horário/operador.

A chave nunca deve aparecer em logs, commits, tickets ou mensagens de operação.

## Checklist de Promoção para Produção

Antes de promover `cerrado_test` para produção:

1. Confirmar o repositório e branch oficiais de produção; o remote
   `git@github.com:Fran981259/cerrado_test.git` é exclusivo do teste.
2. Publicar novas imagens no registry aprovado e registrar os digests SHA-256 do
   backend e frontend; nunca reutilizar a tag `latest`.
3. Alterar nome da stack, portas públicas, URLs, CORS e domínios para os valores
   produtivos; manter `8100`, `3100`, `8181` e `8843` somente no teste.
4. Criar secrets de produção separadamente e validar força de `PUBLISH_API_KEY`;
   não copiar `.env.example` ou credenciais do teste como valores reais.
5. Executar backup, restore em banco isolado, migrations, smoke de API/frontend,
   healthchecks e validação de sitemap no candidato produtivo.
6. Definir janela de rollback por digest, preservar os containers standalone e só
   removê-los após aceite, observação e aprovação explícita do cutover.

## Regras de Parada
- Se uma fase falhar, nao avancar para a seguinte.
- Se o erro for de build, corrigir antes de publicar.
- Se o erro for de stack, corrigir antes de validar frontend.
- Se o erro for de runtime, atualizar o plano antes de improvisar.

## Stack de Teste Swarm

- O serviço Caddy usa o Docker Config `caddyfile` definido no manifesto; não depende de bind mount no diretório interno do Portainer.
- No teste, o Config aponta para `Caddyfile.test`: somente HTTP na porta publicada e sem emissão ACME para o domínio de produção.
- Docker Config é imutável no Swarm; ao alterar seu conteúdo, versionar o nome (`caddyfile_test_http_vN`) em vez de tentar atualizar o objeto existente.
- Após alterar o manifesto, atualizar o repositório Git da stack `cerrado_test` e executar redeploy pelo Portainer.
- A stack de teste é isolada por nomes de volumes, rede e portas; não remover os containers standalone existentes.
- As imagens GHCR são privadas e exigem um registry endpoint no Portainer com usuário GitHub e token de leitura `read:packages`; não colocar esse token no compose, `.env` ou Git.
- O redeploy só é considerado aprovado quando cada serviço de imagem SHA estiver `1/1`; falha `No such image` significa autenticação/pull pendente e bloqueia o aceite.

## Observabilidade e Resposta a Incidentes

- O contrato canônico está em `config/observability.yaml`; ele define métricas,
  campos mínimos de log, campos proibidos, alertas, retenção e rollback.
- Métricas mínimas: latência/erros HTTP, duração de cada etapa do pipeline,
  saúde de banco/Redis, heartbeat de worker/beat e ocupação de disco.
- `publication_stale` é acionado quando não há publicação pública de MS por 2h;
  investigar Beat, worker, fila, fontes e falhas do provedor LLM antes de repetir jobs.
- Em falha crítica, preservar logs e estado, interromper writers, restaurar a imagem
  anterior por SHA e confirmar `/health` antes de retomar escritores.
- Todo incidente deve registrar horário, operador, serviço, evidência, ação e resultado;
  nunca registrar tokens, chaves, senhas, autorização, e-mail ou IP.
- Produção exige aprovação explícita para rollback; ensaios devem usar banco isolado.
- O comando `scripts/rollback.sh <sha>` é dry-run por padrão. A execução exige
  simultaneamente `--confirm`, `ROLLBACK_APPROVED=yes`, Swarm ativo e SHA de 40–64
  caracteres; sem esses requisitos nenhuma chamada Docker é feita.
- Antes de qualquer ensaio real, executar `docker compose ... config` e `docker stack
  config`; nesta etapa ambos passaram com imagens de teste e nenhum daemon foi alterado.

## Referencia Rapida
- Se precisar saber o que mudar, use `PLANO_ACAO.md`.
- Se precisar saber o que e verdade canonica, use `MEMORIA.md`.
- Se precisar operar o sistema, use este arquivo.
