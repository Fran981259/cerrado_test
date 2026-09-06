# REFERENCIA ML - Noticias Curtas PTB

## Objetivo
- Registrar o valor conceitual de um projeto externo de classificacao de noticias curtas em portugues.
- Traduzir esse aprendizado para o Portal Cerrado sem copiar a estrutura de pesquisa.

## O Que O Projeto Externo Mostra
- Classificacao automatica de noticias curtas em portugues.
- Uso de embeddings e classificadores tradicionais.
- Pipeline orientado a NLP, nao a portal de producao.
- Avaliacao de modelo com metricas objetivas.

## O Que Isso Sugere Para O Portal Cerrado
- O portal pode ganhar um modulo de classificacao editorial mais inteligente.
- Temas em alta podem ser priorizados com base em historico e sinais de texto.
- A home pode ser ordenada por relevancia real, nao so por regra fixa.
- A curadoria pode ficar mais consistente entre scanner, filtro e destaque.

## O Que Pode Ser Aproveitado Conceitualmente
- classificacao por tema
- ranking editorial
- embeddings para agrupar noticias parecidas
- analise de desempenho por classe
- revisao com metricas de precisao e recall

## O Que Nao Pode Ser Copiado Direto
- dataset externo
- classes originais do estudo
- notebook como produto final
- dependencia de rotulacao academica fora do fluxo do portal
- modelos sem adaptacao ao contexto editorial do Portal Cerrado

## Diferenca Para O Portal Cerrado
- O Portal Cerrado precisa operar em producao.
- O ML do portal deve trabalhar com sinais editoriais e de audiencia.
- O ML nao substitui Gemini/OpenAI; ele apoia decisao.
- O resultado precisa alimentar pipeline, ranking e home.

## Aplicacao Pratica Recomendada
1. Coletar historico real de materias do portal.
2. Guardar labels editoriais e sinais de leitura.
3. Treinar um baseline simples de classificacao.
4. Medir se o ranking supera heuristica pura.
5. Evoluir para tendencia temporal e agrupamento semantico.

## Valor Para O Projeto
- Melhora a qualidade da curadoria.
- Ajuda a detectar temas em alta.
- Reduz dependencia de palavra-chave.
- Cria base de ML coerente com o negocio real.

## Conclusao
- O projeto externo e uma boa referencia de arquitetura conceitual.
- Para o Portal Cerrado, ele serve como ponto de partida para um ML editorial de producao.
