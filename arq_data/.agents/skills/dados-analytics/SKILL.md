---
name: dados-analytics
description: "Analise, modele, valide ou implemente fluxos locais de dados, SQL, métricas, ETL e ciência de dados. Use para decisões sustentadas por dados e qualidade de pipelines; não use para inventar contexto de negócio, inferir causalidade ou manipular dados externos sem autorização."
---

# Dados Analytics

Trabalhe em português e leia `../engenharia-base/SKILL.md` antes de atuar. Ao trabalhar com arquivos de planilha, use a skill específica de planilhas disponível no ambiente quando ela se aplicar. Para escopo, regra de negócio ou origem de dados desconhecidos, aplique primeiro `../analise-sistemas/SKILL.md` ou declare a limitação.

## Escopo

Use esta skill para exploração de dados, métricas, SQL, modelagem relacional/dimensional, ETL/ELT, qualidade, observabilidade de pipelines, estatística aplicada e modelos preditivos locais. Separe claramente análise, proposta e implementação. Não altere fonte de dados, schema, banco, pipeline, permissões ou dados externos sem solicitação explícita e plano de reversão.

Esta skill é proprietária da semântica, qualidade e transformação dos dados. Para handlers, APIs, autorização ou regras de serviço que consomem esses dados, use `desenvolvimento-backend` como skill primária e trate esta como apoio quando necessário.

Não trate dados como neutros: origem, período, população, transformações, dados ausentes e regras de negócio determinam o significado da análise.

## Descoberta e proveniência

Antes de calcular, concluir ou transformar:

1. Identifique fonte, localização, formato, schema, granularidade, período de cobertura, timezone quando aplicável e atualização conhecida.
2. Verifique o significado documentado de cada campo, chaves, unidades, moeda, convenções de nulos, filtros e regras de deduplicação. Não deduza semântica apenas pelo nome de coluna.
3. Faça perfil proporcional dos dados: contagem, tipos, nulos, duplicidades, valores fora do domínio, intervalos, chaves e possíveis quebras de integridade.
4. Registre transformações aplicadas, filtros, joins, agregações e versões de fonte. A análise deve ser reproduzível a partir do input disponível.
5. Para métricas, defina numerador, denominador, população, janela temporal, timezone, filtros e regra para dados ausentes antes de comparar valores.

## Regras de análise e transformação

- Preserve dados brutos. Transformações devem ser explícitas, reversíveis quando possível e separadas da fonte original.
- Prefira queries e pipelines determinísticos, idempotentes e auditáveis. Em SQL, use o padrão de acesso do projeto, parâmetros para valores externos e operações de leitura por padrão.
- Não execute `UPDATE`, `DELETE`, `TRUNCATE`, `DROP`, alteração de schema ou backfill em fonte externa sem autorização explícita, alvo confirmado, backup/rollback e validação pós-operação.
- Valide joins quanto à cardinalidade. Não agregue ou some métricas após join sem verificar duplicação, fan-out e granularidade.
- Trate ausências, outliers e dados inválidos com regra documentada. Não os descarte silenciosamente, não substitua por zero sem semântica e não chame dado de erro sem critério de domínio.
- Em séries temporais, preserve a ordem, a timezone, a sazonalidade e o período incompleto. Não compare janelas diferentes como se fossem equivalentes.
- Ao implementar pipeline, inclua validações de schema, qualidade, falha explícita, logging útil e limite de reprocessamento conforme o projeto permitir.

## Estatística e ciência de dados

- Diferencie descrição, correlação, previsão e causalidade. Correlação observada não prova causa.
- Declare população, amostra, período, tamanho amostral, critérios de inclusão/exclusão e possíveis vieses antes de generalizar.
- Não reporte significância, intervalo de confiança, lift, acurácia, precisão, recall, AUC ou qualquer métrica sem método de cálculo, conjunto avaliado e limites claros.
- Em modelos preditivos, separe treino, validação e teste de forma compatível com tempo, entidades e risco de vazamento. Não use atributos que incorporam informação disponível apenas após o evento previsto.
- Compare com baseline simples e adequado. Não afirme que um modelo é útil sem métrica de validação, custo de erro e contexto operacional.
- Não use dados sensíveis ou pessoais além do necessário; não exponha identificadores, segredos ou amostras reidentificáveis no relatório.

## Guardrails contra alucinação e quebra de regras

- Classifique resultados como **fato calculado**, **interpretação**, **hipótese** ou **dado ausente**. Inclua fonte, período e transformação que sustentam fatos calculados.
- Não invente colunas, valores, tabelas, chaves, unidades, dicionário de dados, baseline, correlação, segmento, benchmark ou significado de métrica.
- Não extrapole uma amostra, período parcial ou dataset local para produção, mercado ou usuários que não estejam representados sem declarar a limitação.
- Não apresente gráfico, média ou percentual como evidência suficiente de impacto de negócio sem denominador, comparação válida e contexto.
- Não trate uma query que executa como correta. Valide schema, cardinalidade, filtro e resultado contra expectativas observáveis.
- Não modifique dados para fazer a hipótese “bater”, nem oculte linhas descartadas, critérios de limpeza ou falhas de pipeline.

## Validação e entrega

Valide resultados com checks de qualidade, amostras rastreáveis, reconciliação de totais, testes de transformação e, quando houver, testes automatizados do pipeline. Para alterações de schema ou query crítica, explique impacto, compatibilidade e rollback.

Entregue:

1. fonte, período, granularidade e limitações dos dados;
2. perfil de qualidade e transformações realizadas;
3. métricas/resultados com fórmula, filtros e evidência;
4. interpretações e hipóteses separadas dos fatos;
5. recomendações priorizadas, com risco e como validá-las;
6. validações executadas e pendências para reprodução ou produção.
