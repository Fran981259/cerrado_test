# PLANO DE ACAO ML - Portal Cerrado

## Objetivo
- Implantar um modulo de machine learning para melhorar decisao editorial.
- Foco: temas em alta, ranking de pauta e priorizacao de destaque.
- Escopo: apoio editorial, sem substituir Gemini/OpenAI na reescrita.

## Regra De Escopo
- Nao implementar antes de fechar dados e criterio de sucesso.
- Nao treinar modelo sem historico minimo confiavel.
- Nao misturar o objetivo do ML com o fluxo de escrita final.

## Definicao De Pronto
- Historico editorial guardado.
- Labels e sinais de performance persistidos.
- Baseline simples treinado.
- Ranking de tendencia validado contra heuristica atual.
- Integracao sem quebrar o fluxo principal.

## Fase 0 - Inventario De Dados
Objetivo: saber quais sinais existem hoje.

Entregaveis:
- lista de campos disponiveis em artigo
- lista de eventos de leitura e audiencia
- mapa de lacunas de dados

Gate de saida:
- ha entendimento claro do que sera coletado e do que falta.

## Fase 1 - Instrumentacao
Objetivo: registrar os sinais necessarios.

Entregaveis:
- persistencia de clicks
- persistencia de tempo de leitura
- persistencia de rejeicao/saida rapida
- persistencia de categoria final e revisao humana

Gate de saida:
- o portal passa a gerar dados para aprendizado.

## Fase 2 - Rotulacao Editorial
Objetivo: criar labels confiaveis para treino.

Entregaveis:
- rotulo de tema em alta
- rotulo de relevancia editorial
- rotulo de risco de texto fraco
- rotulo de duplicidade ou similaridade alta

Gate de saida:
- existe base suficiente para treino supervisionado simples.

## Fase 3 - Baseline ML
Objetivo: ter um primeiro modelo util.

Entregaveis:
- TF-IDF + classificador leve
- score de tendencia
- score de prioridade
- score de risco

Gate de saida:
- o modelo ja produz ranking melhor que a heuristica pura em teste interno.

## Fase 4 - Validacao Editorial
Objetivo: comparar modelo com criterio humano.

Entregaveis:
- comparacao de precisao/recall
- comparacao de ranking de temas
- analise de falso positivo
- revisao das classes mais instaveis

Gate de saida:
- o modelo melhora a curadoria sem degradar a qualidade.

## Fase 5 - Integracao No Portal
Objetivo: usar o ML no fluxo real.

Entregaveis:
- score ML no `classifier.py`
- uso do score no `filter.py`
- ranking editorial na home
- persistencia de feedback apos publicacao

Gate de saida:
- o portal passa a usar o ML sem impacto negativo no runtime.

## Fase 6 - Evolucao
Objetivo: melhorar a qualidade ao longo do tempo.

Entregaveis:
- embeddings para agrupamento semantico
- analise temporal por janela
- ajuste por tema e horario
- re-treino periodico

Gate de saida:
- o modulo evolui com o uso real do portal.

## Ordem Recomendada
1. Fase 0.
2. Fase 1.
3. Fase 2.
4. Fase 3.
5. Fase 4.
6. Fase 5.
7. Fase 6.

## Critérios De Sucesso
- mais temas quentes identificados corretamente
- melhor prioridade editorial
- menos ruido na home
- menos dependencia de palavra-chave
- mais consistencia entre curadoria e desempenho

## Riscos
- dados insuficientes
- labels ruins
- overfitting em historico pequeno
- custo de manutencao sem retorno claro
