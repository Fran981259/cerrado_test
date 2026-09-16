# PLANO DE ACAO - Portal Cerrado

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

## Fases

### Fase 0 - Inventario e Baseline
- Status: DONE
- Entregaveis: lista de arquivos, modulos, pontos de entrada.
- Gate: nenhuma divergencia critica sem registro.

### Fase 1 - Contrato de Runtime
- Status: DONE
- Entregaveis: variaveis de ambiente, nomes de servico, URLs padronizadas.
- Gate: nenhum componente depende de suposicao local invisivel.

### Fase 2 - Backend Real
- Status: DONE
- Servicos: cerrado_portal_cerrado, cerrado_celery_worker, cerrado_celery_beat, cerrado_flower.
- Gate: todos sobem sem crash loop, imports validados, 77 testes passando.

### Fase 3 - Frontend Real
- Status: DONE
- Entregaveis: rewrites corretos, metadata/sitemap/robots coerentes.
- Gate: frontend consome API real, 0 JSON local como fonte.

### Fase 4 - Build e Registry
- Status: DONE
- Entregaveis: imagens buildadas localmente, deploy via update.sh.
- Gate: imagens funcionais no stack.

### Fase 5 - Portainer/Swarm
- Status: DONE
- Entregaveis: stack validada, services 1/1, DNS interno resolvido.
- Gate: todos os servicos operacionais.

### Fase 6 - Validacao Final
- Status: DONE
- Entregaveis: 77 testes, lint verde, py_compile ok, 0 categorias invalidas.
- Gate: pronto para producao.

### Fase 7 - CI/CD e GitHub
- Status: PENDING
- Entregaveis: .github/workflows/deploy.yml, build+test+push automatico.
- Gate: mudancas entram via PR com teste automatizado.

### Fase 8 - Observabilidade
- Status: PENDING
- Entregaveis: healthchecks reais, logs centralizados, alertas.
- Gate: falhas detectaveis automaticamente.

## Itens Ja Confirmados
- Frontend lint passou.
- Suite Python passou com 77 testes.
- 125 artigos classificados, 0 em geral.
- Servicos nomes: cerrado_portal_cerrado, cerrado_celery_worker, cerrado_celery_beat, cerrado_flower, cerrado_frontend.

## Riscos Conhecidos
- CI/CD nao implementado (Fase 7 pendente).
- Healthchecks desabilitados no docker-compose (Fase 8 pendente).
- Provider LLM e Groq, nao Gemini/OpenAI (documentado em MEMORIA.md).

## Proxima Acao
- Implementar Fase 7 (CI/CD) e Fase 8 (healthchecks/observabilidade).
