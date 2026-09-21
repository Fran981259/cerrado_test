---
name: logica-algoritmos
description: "Investigue e corrija lógica computacional, cálculos, algoritmos, estruturas de dados, concorrência e desempenho mensurável. Use para bugs difíceis ou otimização com evidência; não use para mudanças cosméticas ou otimização especulativa."
---

# Logica Algoritmos

Trabalhe em português e leia `../engenharia-base/SKILL.md` antes de atuar. Use esta skill para raciocinar sobre corretude e custo computacional; não use complexidade assintótica como substituta para medir um sistema real.

## Escopo

Atue em erros de cálculo, condições de borda, regras determinísticas, parsing, ordenação, busca, agregação, estruturas de dados, uso de memória, paralelismo, concorrência, deadlocks, race conditions e gargalos comprováveis. Inspecione a implementação e seus chamadores antes de editar.

Quando o artefato principal for uma API, serviço, pipeline ou interface, use esta skill para provar a causa, invariantes ou ganho de desempenho e mantenha a skill de backend, dados ou frontend como proprietária da alteração de domínio.

Não altere resultado funcional para acelerar o código sem autorização explícita. Não troque precisão por aproximação, ordenação por não determinismo, processamento completo por amostragem ou consistência por eventualidade sem documentar a mudança de contrato e obter a aprovação necessária.

## Método de diagnóstico

1. Defina o problema em termos observáveis: entrada, saída esperada, estado inicial, efeitos colaterais, falha atual e condição de ocorrência.
2. Localize a implementação, seus chamadores, tipos, formatos de dados e testes. Identifique premissas explícitas e implícitas, como ordenação, unicidade, nulidade, limites, precisão e mutabilidade.
3. Para um bug, construa ou encontre um caso mínimo reproduzível antes de corrigir. Para uma regra complexa, escreva invariantes ou propriedades que devem permanecer verdadeiras.
4. Trace o fluxo somente até onde a evidência for necessária. Separe erro de implementação, requisito ambíguo, dado inválido, contrato quebrado e efeito de concorrência.
5. Para desempenho, estabeleça uma linha de base com workload, ambiente, métrica e método de medição. Use entradas representativas ou declare a limitação.

## Regras de corretude

- Preserve contratos de entrada, saída, ordem, determinismo, precisão e efeitos colaterais existentes, salvo mudança explicitamente solicitada.
- Trate limites, vazio, nulo, duplicidade, overflow, underflow, timezone, encoding e precisão numérica conforme a semântica real do domínio e da linguagem. Não use valores mágicos ou tolerâncias arbitrárias para esconder erro.
- Evite mutação compartilhada quando o fluxo pode ser reentrante ou concorrente. Se alterar concorrência, defina ownership, sincronização, cancelamento, ordem, timeout e propagação de erro com base nos mecanismos existentes.
- Não introduza paralelismo, cache ou batch sem analisar repetição, invalidação, consistência, limites de recurso e observabilidade.
- Ao modificar algoritmo, mantenha a implementação legível o suficiente para verificar seus invariantes. Um algoritmo teoricamente melhor que ninguém consegue manter pode aumentar o custo total do sistema.

## Análise de desempenho

Ao discutir complexidade, indique as variáveis de entrada e as operações dominantes. Diferencie:

- **complexidade assintótica** do trecho analisado;
- **custo real medido** no ambiente e workload disponíveis;
- **custo de I/O, alocação, serialização, banco ou rede**, que pode dominar o algoritmo.

Otimize somente depois de confirmar o gargalo ou atender requisito mensurável. Compare antes/depois com a mesma carga e verifique correção, memória e latência. Rejeite micro-otimizações cujo benefício não seja observado ou cujo custo de manutenção seja maior que o ganho.

## Guardrails contra alucinação e quebra de regras

- Classifique achados como fato observado, inferência ou hipótese de investigação. Não apresente uma hipótese de race condition ou gargalo como causa comprovada sem reprodução, trace, perfil ou evidência equivalente.
- Não alegue Big-O sem considerar chamadas internas relevantes, tamanho das coleções, comportamento de biblioteca e pré-condições. Se a complexidade depender de uma implementação externa não inspecionada, declare-a condicional.
- Não suponha distribuição de dados, ordenação, unicidade, imutabilidade, thread safety, cache hit, hardware, volume ou padrão de tráfego sem fonte verificável.
- Não use um único exemplo de sucesso como prova de corretude geral, nem um benchmark isolado como prova de ganho estável.
- Não remova verificações, validações ou tratamento de erro para melhorar número de benchmark. Isso muda o problema, não resolve desempenho.
- Não “corrija” resultado inesperado alterando teste, expected value ou requisito sem demonstrar por que o comportamento anterior estava incorreto e sem autorização quando a regra de negócio for ambígua.

## Testes e validação

Adicione ou atualize testes que cubram o caso mínimo, limites relevantes e invariantes. Quando apropriado, use testes parametrizados, propriedade/metamórficos ou comparação contra implementação de referência simples. Para concorrência, teste interleavings controláveis quando a stack permitir; não alegue cobertura completa de timing.

Em otimização, mantenha testes de comportamento e execute benchmark ou profiling antes/depois. Informe o comando, a métrica, a entrada e a variação observada. Se a medição não for reproduzível, trate o resultado como indicativo, não conclusivo.

## Entrega

Informe:

1. problema formalizado e evidência da causa;
2. invariantes, pré-condições e casos de borda relevantes;
3. alteração aplicada ou proposta e impacto no contrato;
4. complexidade e métricas, claramente separadas entre análise e medição;
5. testes/benchmarks executados, resultado e limitações restantes.
