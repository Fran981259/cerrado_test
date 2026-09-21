---
name: analise-sistemas
description: "Analise localmente um projeto de software para mapear arquitetura, fluxos, regras, integrações, riscos e prioridades. Use antes de planejar refatorações ou mudanças amplas; não use para implementar correções diretamente."
---

# Análise de Sistemas

Produza um diagnóstico técnico baseado no repositório, em português, sem modificar arquivos. Antes de começar, leia `../engenharia-base/SKILL.md` e aplique seu protocolo comum.

## Escopo

Use esta skill para entender um sistema existente, uma área do repositório, uma funcionalidade ou uma proposta de mudança. O objetivo é reduzir incerteza e orientar decisão; não é reescrever código, produzir uma arquitetura idealizada ou inventar requisitos.

Não edite, crie, remova, formate, instale dependências, execute migrações nem faça chamadas externas. Se o usuário também pediu implementação, entregue primeiro a análise e separe explicitamente o plano de execução da alteração.

## Coleta de evidências

1. Descubra a raiz do projeto e leia instruções aplicáveis (`AGENTS.md`, README, documentação de arquitetura e arquivos de configuração relevantes).
2. Faça um inventário proporcional ao escopo: linguagem, gerenciador de dependências, serviços, módulos, pontos de entrada, testes, dados persistidos, integrações e comandos de execução/validação que sejam observáveis.
3. Leia os arquivos que sustentam as conclusões. Para fluxos relevantes, siga o caminho da entrada ao efeito: interface ou job → camada de aplicação → regras → persistência, rede ou outro I/O.
4. Identifique contratos observáveis: APIs, schemas, eventos, arquivos, variáveis de ambiente, formatos de entrada/saída e interfaces entre módulos.
5. Quando faltarem evidências, registre a lacuna. Não expanda a investigação para todo o repositório se isso não responder à pergunta do usuário.

## Disciplina contra alucinação

Classifique todas as conclusões importantes como uma das categorias abaixo:

- **Fato observado:** sustentado por arquivo, configuração, teste, log ou comando consultado. Cite o caminho e, quando útil, o símbolo ou linha.
- **Inferência:** conclusão plausível derivada de fatos; explique a cadeia de raciocínio e use linguagem condicional.
- **Desconhecido:** informação que o repositório não confirma. Diga como validá-la, em vez de preenchê-la com suposição.

Regras obrigatórias:

- Não atribua intenção de negócio a código, nome de arquivo ou padrão de pastas sem fonte explícita.
- Não declare vulnerabilidade, gargalo, bug, incompatibilidade ou ausência de teste como certeza sem evidência reproduzível ou leitura suficiente.
- Não invente métricas, cobertura, complexidade, volume de dados, SLA, custo ou comportamento em produção.
- Não trate README, comentário ou configuração como verdade operacional quando o código ou os testes a contradisserem; registre a divergência.
- Não recomende frameworks, reescritas ou padrões arquiteturais por preferência. Cada recomendação deve atacar um problema observado, explicitar custo e ter critério de sucesso.
- Não esconda incerteza com linguagem confiante. Se o diagnóstico depende de ambiente, credenciais, tráfego, logs ou dados indisponíveis, isso limita a conclusão.

## Avaliação

Avalie somente dimensões pertinentes ao pedido:

- arquitetura e acoplamento;
- regras de negócio e fronteiras de I/O;
- fluxo de dados e consistência;
- integrações e contratos;
- confiabilidade, observabilidade, segurança ou desempenho;
- qualidade de testes e risco de regressão.

Para cada problema relevante, descreva: evidência, impacto provável, probabilidade ou condição de ocorrência, escopo afetado, alternativa de tratamento e validação necessária. Separe dívida técnica de defeito funcional e de decisão de produto pendente.

## Formato de entrega

Entregue nesta ordem:

1. **Escopo analisado:** o que foi inspecionado e o que ficou fora.
2. **Mapa do sistema:** componentes, responsabilidades, fluxos e dependências relevantes.
3. **Achados priorizados:** tabela com prioridade, classificação (fato/inferência/desconhecido), evidência, impacto e recomendação.
4. **Riscos e lacunas:** incertezas que impedem conclusão ou aumentam risco de mudança.
5. **Plano incremental:** próximas ações na menor ordem útil, com pré-condições e validação para cada uma.

Priorize por impacto e risco, não por quantidade de observações. Se não houver problema material, diga isso e descreva os limites da inspeção.
