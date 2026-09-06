# OPERACAO - Portal Cerrado

## Status Consolidado
- O sistema possui backend funcional, frontend funcional e pipeline de conteudo em camadas.
- Existem apenas artefatos de desenvolvimento e testes, sem uso no fluxo principal do frontend.
- A operacao precisa manter claro o que e real, o que e contingencia e o que e legado.

## Baseline Atual
- `origin/main` aponta para `be31c4a`.
- O working tree local tem divergencia grande do baseline: dezenas de arquivos alterados, varios removidos e novos artefatos de documento e frontend.
- Os maiores grupos de risco sao: deploy/Portainer, contrato de runtime, frontend com defaults de URL e backend com boot/import sensivel ao banco.
- A conclusao da Fase 0 depende apenas de registrar este baseline e separar o que vai para producao do que e so manutencao/teste.

## O que foi consolidado
- `andamento.md` virou historico de progresso.
- `CHECKLIST.md` virou lista de validacao resumida.
- `AUDITORIA.md` virou registro tecnico e de follow-up.
- `DEPLOY.md` e `PORTAINER.md` viraram guia operacional unificado.

## Guia Operacional
1. Validar banco, API e frontend.
2. Validar pipeline de scan, classify, rewrite, publish.
3. Validar exportacao do frontend.
4. Validar healthchecks e logs.
5. Validar deploy pela stack oficial do ambiente.

## Checklist Operacional Por Fase

## Contrato de Runtime

### Backend Obrigatorio em Produção
- `DATABASE_URL` -> Postgres do stack.
- `REDIS_URL` -> Redis do stack.
- `GROQ_API_KEY` -> chave do provider LLM usado em producao hoje.
- `GROQ_MODEL` -> modelo explicitamente definido.
- `PUBLISH_API_KEY` -> chave para endpoints de escrita.
- `SITE_URL` -> URL publica do site.
- `NEXT_PUBLIC_SITE_URL` -> mesma URL publica para o frontend.
- `NEXT_PUBLIC_API_URL` -> URL interna da API para o frontend.
- `CORS_ALLOWED_ORIGINS` -> origem publica do frontend e origem local de manutencao.
- `ENVIRONMENT` -> `production` no deploy real.
- `SIMILARITY_THRESHOLD` -> limiar de compliance.

### Backend Opcional ou de Controle
- `CELERY_SCHEDULER` -> `1` quando beat assume.
- `ENABLE_LOCAL_SCHEDULER` -> `0` em producao com beat.
- `LOCAL_SCHEDULER_INTERVAL` -> usado so em scheduler local.
- `DATABASE_CONNECT_RETRIES` -> tentativas de conexao ao Postgres antes de falhar.
- `DATABASE_CONNECT_RETRY_DELAY` -> intervalo entre tentativas.
- `ARCHIVE_DAYS_AFTER_PUBLISH` -> politica de retencao.
- `USER_AGENT` -> identidade de crawler.
- `RESPECT_ROBOTS_TXT` -> controle de crawler.
- `ROBOTS_TXT_CACHE_HOURS` -> cache do robots.
- `DEDUP_TTL_SECONDS` -> TTL de deduplicacao.

### Frontend Obrigatorio em Produção
- `NEXT_PUBLIC_API_URL` -> destino dos rewrites e fetch.
- `NEXT_PUBLIC_SITE_URL` -> base do metadata, sitemap e robots.

### LLM Alternativo/Futuro
- `OPENROUTER_API_KEY` -> fallback tecnico atualmente presente.
- `LLM_MODEL` -> modelo do OpenRouter.
- `OPENAI_API_KEY` -> legado/nao usado no caminho atual.

### Regra de Contrato
- Qualquer variavel listada como obrigatoria deve existir no stack final.
- Variavel nao usada no runtime final deve ser removida do deploy ou documentada como legado.
- Nenhum valor de producao deve depender de default para host ou dominio antigo.

### Fase 0 - Inventario
- Confirmar `git status --short` limpo ou listar divergencias intencionais.
- Confirmar `git remote -v` apontando para o repo certo.
- Confirmar branch de trabalho.
- Registrar o que esta alterado no local e o que ainda nao foi enviado.
- Gate: nenhuma divergencia desconhecida.

### Fase 1 - Runtime
- Conferir variaveis obrigatorias do backend.
- Conferir variaveis obrigatorias do frontend.
- Conferir nomes reais de servico no Swarm.
- Conferir que nao existe dependencia de `localhost` em producao.
- Gate: ambiente descrito exatamente como sera usado.

### Fase 2 - Backend
- Validar import e startup do FastAPI.
- Validar conexao com banco no ambiente correto.
- Validar Celery worker.
- Validar Celery beat.
- Validar Flower.
- Gate: nenhum servico em crash loop.

### Fase 3 - Frontend
- Validar build do frontend.
- Validar rewrites para a API.
- Validar metadata, sitemap e robots.
- Validar pagina de noticia com API real.
- Gate: frontend mostra noticia real ou erro explicito.

### Fase 4 - Build e Registry
- Buildar imagem backend com tag especifica.
- Buildar imagem frontend com tag especifica.
- Fazer push das duas imagens.
- Confirmar digest do registry.
- Gate: imagens publicadas e recuperaveis fora da maquina local.

### Fase 5 - Portainer/Swarm
- Atualizar stack com as imagens corretas.
- Conferir DNS interno e aliases.
- Conferir env vars aplicadas no stack.
- Conferir estado dos servicos.
- Gate: todos os servicos em `1/1`.

### Fase 6 - Validacao Final
- Rodar lint do frontend.
- Rodar testes Python.
- Conferir `/health`.
- Abrir frontend e confirmar conteudo real.
- Conferir logs sem erro recorrente.
- Gate: pronto para producao.

## Ordem de Execucao Recomendada
1. Fase 0.
2. Fase 1.
3. Fase 2.
4. Fase 3.
5. Fase 4.
6. Fase 5.
7. Fase 6.

## Matriz de Execucao
| Fase | Status | Bloqueio Principal | Critério de Aceite |
| --- | --- | --- | --- |
| 0 - Inventario | done | divergencia desconhecida | diff conhecido e registrado |
| 1 - Runtime | done | env/nome de servico incorreto | contrato de runtime fechado |
| 2 - Backend | in_progress | import/db/DNS/crash loop | backend e workers sobem |
| 3 - Frontend | pending | API/URL/metadata errados | frontend usa API real |
| 4 - Build e Registry | pending | imagem nao publicada | registry com tags validas |
| 5 - Portainer/Swarm | pending | stack fora do contrato | services 1/1 |
| 6 - Validacao Final | pending | teste/lint/health falhando | pronto para producao |

## Como Usar a Matriz
- Atualizar `Status` para `in_progress` apenas na fase em execucao.
- Marcar `blocked` quando houver erro que impeca avancar.
- Marcar `done` somente apos cumprir o criterio de aceite.
- Nao iniciar uma fase se a anterior nao estiver `done`.

## Regras de Parada
- Se uma fase falhar, nao avancar para a seguinte.
- Se o erro for de build, corrigir antes de publicar.
- Se o erro for de stack, corrigir antes de validar frontend.
- Se o erro for de runtime, atualizar o plano antes de improvisar.

## Critérios de Saida para Produção
- Sem simulacao silenciosa no caminho principal.
- Sem dados de exemplo no fluxo real.
- Sem documento duplicado com instrucoes conflitantes.
- Sem deploy manual fora do processo acordado.

## Itens que ainda merecem atencao
- Fallback local no frontend.
- Diferenca entre estado de desenvolvimento e estado de producao.
- Sincronia entre banco, exportador e site.

## Referencia Rapida
- Se precisar saber o que mudar, use `PLANO_ACAO.md`.
- Se precisar saber o que e verdade canonica, use `MEMORIA.md`.
- Se precisar operar o sistema, use este arquivo.
