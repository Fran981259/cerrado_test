# CRONOGRAMA EXECUTIVO ML - Portal Cerrado

## Objetivo
- Organizar a implantacao do modulo de machine learning em ordem de valor e risco.
- Prioridade: ganhar utilidade editorial cedo, sem criar complexidade desnecessaria.

## Visao Geral
- Fase 0 e 1: preparar dados.
- Fase 2 e 3: criar baseline util.
- Fase 4: validar contra criterio humano.
- Fase 5: integrar no portal.
- Fase 6: evoluir com uso real.

## Cronograma Executivo

### 1. Inventario E Instrumentacao
- Prioridade: alta
- Esforco: baixo a medio
- Dependencias: banco, eventos de leitura, labels basicos
- Impacto esperado: cria base real para aprendizado

### 2. Rotulacao Editorial
- Prioridade: alta
- Esforco: medio
- Dependencias: historico de publicacao e criterio editorial
- Impacto esperado: define o que o modelo deve aprender

### 3. Baseline ML
- Prioridade: alta
- Esforco: medio
- Dependencias: dados minimamente rotulados
- Impacto esperado: primeiro ranking de tema/prioridade/riscos

### 4. Validacao Editorial
- Prioridade: alta
- Esforco: medio
- Dependencias: baseline funcionando
- Impacto esperado: prova se o ML melhora a curadoria

### 5. Integracao No Portal
- Prioridade: media-alta
- Esforco: medio
- Dependencias: validacao positiva
- Impacto esperado: home e filtros mais inteligentes

### 6. Evolucao Continua
- Prioridade: media
- Esforco: medio a alto
- Dependencias: volume de uso e feedback real
- Impacto esperado: tendencia, agrupamento e ranking mais estaveis

## Sequencia Recomendada
1. Fazer dados.
2. Rotular.
3. Treinar baseline.
4. Medir ganho.
5. Integrar.
6. Evoluir.

## Decisao Pratica
- Se a fase nao melhora a curadoria, nao avanca para a seguinte.
- Se o ganho nao aparecer com dados reais, simplificar o escopo.
