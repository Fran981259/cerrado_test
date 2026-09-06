# PLANO DE AÇÃO - Portal Cerrado

## Regra de Escopo
- Este arquivo e a fonte unica do plano.
- Toda mudanca deve manter alinhamento entre repositorio local, GitHub e deploy.
- Nao executar etapas fora da sequencia sem aprovacao.
- Nao manter dois caminhos concorrentes para o mesmo runtime.

## Objetivo
- Tornar o projeto reproduzivel, observavel e deployavel em Docker/Portainer sem dependencias ocultas.
- Garantir que local, GitHub e stack de producao apontem para o mesmo contrato tecnico.
- Eliminar fallback silencioso, mock funcional e artefato estatico no caminho produtivo.

## Definicao de Pronto
- O `git status` local fica limpo.
- O GitHub recebe o mesmo estado funcional do local.
- As imagens sao publicadas em registry com tag imutavel.
- O Portainer puxa as imagens corretas e sobe os servicos sem erro de DNS, banco ou import.
- `pytest` e lint passam.
- O frontend carrega dados reais da API ou exibe erro explicito.

## Metodo
1. Inventariar.
2. Corrigir.
3. Validar.
4. Publicar.
5. Conferir no Portainer.

## Fases Claras

### Fase 0 - Inventario e Baseline
Objetivo: saber exatamente o que existe hoje.
Entregaveis:
- lista dos arquivos alterados vs `origin/main`
- lista dos modulos `real`, `fallback`, `teste`, `demo`, `placeholder`
- mapa dos pontos de entrada do runtime
Gate de saida:
- nenhuma divergencia critica sem registro.

### Fase 1 - Contrato de Runtime
Objetivo: definir o que e obrigatorio para rodar.
Entregaveis:
- variaveis de ambiente finais
- nomes de servico e DNS do Swarm definidos
- URLs de frontend/API padronizadas
Gate de saida:
- nenhum componente depende de suposicao local invisivel.

### Fase 2 - Backend Real
Objetivo: fazer o backend subir e operar sem import quebrado.
Entregaveis:
- boot do FastAPI sem erro de banco ou import
- Celery worker/beat importando tasks sem falha
- Postgres e Redis resolvidos corretamente no stack
Gate de saida:
- `botgram_portal_cerrado`, `botgram_celery_worker`, `botgram_celery_beat` e `botgram_flower` sobem sem crash loop.

### Fase 3 - Frontend Real
Objetivo: garantir que o frontend consome a API real.
Entregaveis:
- rewrites corretos
- metadata/sitemap/robots coerentes com o ambiente
- erro visivel quando a API falhar
Gate de saida:
- sem JSON local como fonte principal.

### Fase 4 - Build e Registry
Objetivo: produzir artefatos implantaveis.
Entregaveis:
- imagem backend publicada em registry
- imagem frontend publicada em registry
- tags imutaveis definidas para release
Gate de saida:
- Portainer consegue puxar as imagens sem depender de build local.

### Fase 5 - Portainer/Swarm
Objetivo: subir tudo em ambiente real.
Entregaveis:
- stack validada no Portainer
- services com DNS, aliases e env corretos
- healthchecks e logs conferidos
Gate de saida:
- stack em estado estavel, sem servico em `0/1`.

### Fase 6 - Validacao Final
Objetivo: provar que o sistema esta pronto para producao.
Entregaveis:
- lint verde
- pytest verde
- healthcheck da API ok
- frontend carregando noticias reais
- logs limpos ou com warnings conhecidos documentados
Gate de saida:
- pronto para producao.

## Fase 0 - Baseline e Paridade
1. Congelar o estado atual do GitHub como referencia.
2. Comparar o working tree local com `origin/main`.
3. Listar diferencas por categoria: runtime, docs, testes, deploy, frontend, backend.
4. Identificar artefatos que nao devem entrar em producao: JSON estatico, demo, fallback silencioso, helpers legados.
5. Definir o caminho unico de deploy: imagem publicada -> Portainer -> Swarm.

## Fase 1 - Contrato de Runtime
1. Consolidar variaveis de ambiente obrigatorias e opcionais.
2. Padronizar nomes de servico que o Swarm realmente resolve.
3. Remover dependencia de `localhost` no caminho produtivo.
4. Eliminar `latest` como unica referencia de release.
5. Garantir que o backend e o frontend sejam configurados por env, nao por suposicao interna.

## Fase 2 - Backend
1. Postgres deve ser a fonte real em producao.
2. Redis deve ser o broker/beat real do Celery.
3. A inicializacao nao pode quebrar por conexao precoce em import.
4. A pipeline precisa falhar fechado quando a etapa anterior nao produzir saida valida.
5. Qualquer fallback de desenvolvimento deve estar explicitamente fora da rota de producao.

## Fase 3 - Frontend
1. O frontend deve consumir a API real como fonte primaria.
2. Rewrites e metadata devem usar `NEXT_PUBLIC_API_URL` e `NEXT_PUBLIC_SITE_URL` corretos.
3. Sitemap e robots devem refletir o host de deploy, nao o dominio antigo por default.
4. Sem JSON local como fonte principal.
5. Erro de backend deve aparecer como erro visivel, nao como tela vazia ou dado inventado.

## Fase 4 - Docker e Portainer
1. Buildar backend e frontend em imagens separadas e publicadas.
2. Tag de release deve ser especifica, nao apenas `latest`.
3. O stack do Portainer deve usar imagens publicadas do registry.
4. O stack deve declarar rede e aliases coerentes com o DNS interno do Swarm.
5. `docker-compose.yml` do repo deve representar o mesmo contrato que o Portainer usa.

## Fase 5 - CI/CD e GitHub
1. O workflow deve testar antes de buildar.
2. O workflow deve publicar imagens em registry.
3. O workflow deve usar tags previsiveis por commit ou release.
4. O GitHub deve passar a ser espelho funcional do local, nao so arquivo de codigo.
5. Nenhuma mudanca em runtime entra sem passar por teste automatizado.

## Fase 6 - Validacao Cientifica
1. Lint do frontend.
2. `py_compile` dos modulos alterados.
3. `pytest` da suite completa.
4. Build das imagens com contexto correto.
5. Push das imagens no registry.
6. Deploy no Portainer.
7. Healthcheck da API.
8. Resposta do frontend com dados reais.
9. Verificacao de logs do worker, beat e flower.

## Fase 7 - Operacao e Observabilidade
1. Centralizar logs de erro de API, worker e frontend.
2. Definir criterio de retry e timeout por etapa.
3. Tornar falha de banco, fila ou api publicamente detectavel no health.
4. Manter alerta para divergencia entre compose local e stack real.
5. Registrar rollback simples por tag anterior.

## Sequencia de Execucao
1. Igualar o codigo local ao contrato final.
2. Rodar lint e testes.
3. Buildar imagens.
4. Publicar no registry.
5. Atualizar stack no Portainer.
6. Validar status dos servicos.
7. Corrigir o que falhar e repetir apenas a fase afetada.

## Critérios de Aceite
- Backend sobe sem erro de import, banco ou DNS.
- Worker, beat e flower sobem e importam tasks sem SyntaxError.
- Frontend sobe e carrega a API real.
- Sitemap e robots saem com a URL correta do ambiente.
- Os testes passam localmente antes do push.
- O GitHub e o local ficam consistentes com o mesmo contrato de runtime.

## Itens Ja Confirmados
- Frontend lint passou.
- Suite Python passou com `68 passed` no ambiente de verificacao.
- O projeto precisa de tag de imagem explicita para evitar divergencia de `latest`.
- O stack precisa de aliases/dns coerentes para `postgres` e `redis` no Swarm.

## Riscos Conhecidos
- `init_db()` no import pode quebrar boot precoce.
- `latest` pode mascarar imagem antiga em Portainer.
- Fallback de URL antigo pode vazar para sitemap/metadata se env vier errada.
- Workflow sem push deixa GitHub sem artefato implantavel.

## Proxima Acao
- Executar a Fase 1 e a Fase 4 em conjunto, porque sao as que destravam o deploy real.
