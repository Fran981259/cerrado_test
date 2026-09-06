# PLANO ML - Portal Cerrado

## Objetivo
- Criar um modulo de machine learning para apoiar decisao editorial.
- Prioridade: detectar temas em alta, ranquear pauta e melhorar consistencia do portal.
- Escopo: decisao editorial, nao geracao de texto.

## Referencia Externa
- Um projeto de classificacao de noticias curtas em portugues serve como referencia conceitual.
- A leitura comparativa esta registrada em `REFERENCIA_ML_NOTICIAS_CURTAS_PTB.md`.
- O valor principal dessa referencia e mostrar como NLP pode organizar temas, prioridade e ranking.

## O Que O ML Devera Fazer
- Identificar temas quentes por janela de tempo.
- Classificar relevancia de materias novas.
- Sinalizar risco de texto fraco, duplicado ou pouco util.
- Ajudar a ordenar home, categorias e destaques.
- Aprender com historico de performance editorial.

## O Que O ML Nao Devera Fazer
- Nao substituir Gemini/OpenAI na reescrita.
- Nao escrever noticia final.
- Nao rodar sem dados historicos minimamente confiaveis.
- Nao virar uma camada complexa antes do MVP provar valor.

## Problemas Que O ML Resolve Melhor
- Dependencia excessiva de palavra-chave.
- Prioridade editorial baseada apenas em regra fixa.
- Dificuldade para perceber assunto em ascensao.
- Ruido na selecao do que merece destaque.
- Duplicidade e baixa qualidade com pouca inteligencia adaptativa.

## Dados Necessarios

### Entrada Basica
- titulo
- resumo
- conteudo
- categoria
- fonte
- horario de coleta
- horario de publicacao
- reporter

### Sinais De Performance
- cliques
- tempo medio de leitura
- scroll depth
- rejeicao/saida rapida
- compartilhamentos
- comentario
- taxa de retorno

### Sinais Editoriais
- aprovado/rejeitado
- categoria final
- prioridade final
- duplicado ou nao
- precisa revisao humana

## MVP Recomendado
- Modelo leve com `scikit-learn`.
- Vetorizacao por TF-IDF.
- Classificador simples para:
  - tema em alta
  - prioridade editorial
  - risco de conteudo fraco
- Primeira versao focada em politica, economia, seguranca, saude e agro.

## Evolucao Pos-MVP
- Embeddings para agrupamento semantico.
- Clustering para detectar assunto recorrente.
- Ranking temporal por janela de 1h, 6h, 24h.
- Aprendizado com feedback editorial e desempenho real.

## Integracao No Pipeline

### `scanner.py`
- coleta os sinais brutos
- marca origem, categoria e horario

### `classifier.py`
- recebe score ML adicional
- combina regra atual + predicao do modelo

### `filter.py`
- usa risco previsto para barrar lixo com mais inteligencia

### `publisher.py`
- preserva validacao final
- registra feedback do conteudo publicado

### `frontend`
- usa ranking para ordenar home e blocos de destaque

## Modelo De Dados Sugerido
- `news_signals`
- `editorial_labels`
- `topic_trends`
- `publication_feedback`
- `article_performance`

## Metricas De Sucesso
- acuracia de classificacao editorial
- precision/recall para tema quente
- reducao de falso positivo
- aumento de CTR nos destaques
- maior estabilidade na curadoria da home

## Critérios De Aceite Do MVP
- consegue ranquear temas em alta melhor que heuristica pura
- usa historico real do portal
- melhora selecao editorial sem quebrar o fluxo atual
- nao interfere na reescrita Gemini/OpenAI

## Roadmap
1. Instrumentar dados.
2. Salvar historico editorial.
3. Treinar baseline simples.
4. Validar com metricas.
5. Integrar ao ranking do portal.
6. Evoluir para embeddings e tendencia temporal.

## Risco Principal
- Sem dados bons, o ML vira custo e nao vantagem.
