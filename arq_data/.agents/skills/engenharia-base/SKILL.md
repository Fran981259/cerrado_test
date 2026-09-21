---
name: engenharia-base
description: "Aplique o protocolo comum de engenharia em tarefas de software sem uma skill especializada claramente aplicável; as skills especializadas devem consultá-lo como referência obrigatória. Não use para marketing, conteúdo ou administração sem relação com engenharia."
---

# Engenharia Base

Conduza o trabalho técnico em português claro, com conclusões sustentadas por evidência do projeto.

## Roteamento e precedência

Escolha uma skill primária pelo entregável principal; não carregue todas as skills por precaução.

- Use `analise-sistemas` quando a tarefa for entender ou priorizar antes de alterar.
- Use `arquitetura-software` quando a decisão envolver fronteiras, contratos, migração ou trade-offs estruturais.
- Use `desenvolvimento-backend` para comportamento no servidor, APIs, persistência e integrações; use `desenvolvimento-frontend` para comportamento no cliente e interface.
- Use `logica-algoritmos` quando a questão central for corretude formal, algoritmo, concorrência ou desempenho mensurável. Ela pode apoiar front, back ou dados, mas não substitui a skill proprietária do artefato alterado.
- Use `dados-analytics` quando a questão central for semântica, qualidade, transformação, métrica, análise ou pipeline de dados. Para uma API ou serviço que apenas consome esses dados, a skill primária é backend.
- Use `qa-confiabilidade` para estratégia, reprodução e implementação de testes; use `devops-entrega` para runtime, container, CI/CD e operação.

Em tarefas compostas, execute na ordem mínima que reduz risco: diagnóstico → decisão arquitetural quando necessária → implementação de domínio → validação → entrega operacional. Relate o limite entre etapas; não transforme essa sequência em autorização para executar todas elas.

## Antes de concluir ou alterar

1. Leia as instruções aplicáveis do repositório, incluindo `AGENTS.md`, e inspecione os arquivos, dependências e comandos de validação relevantes.
2. Diferencie fatos observados de hipóteses. Não presuma framework, requisito, contrato público, comportamento esperado ou ambiente de execução.
3. Delimite o escopo. Em pedidos de análise, revisão, explicação ou diagnóstico, não altere arquivos. Em pedidos de mudança, altere apenas o necessário para a solicitação.
4. Preserve alterações existentes que não pertencem à tarefa. Não descarte, reformate em massa ou reorganize código sem benefício verificável.

## Processo de engenharia

- Comece pelo comportamento e pelos contratos: pontos de entrada, interfaces públicas, dados persistidos, integrações e efeitos de I/O quando forem relevantes.
- Prefira a menor mudança que resolva o problema. Abstrações, camadas e refatorações precisam de um motivo concreto: reduzir acoplamento real, corrigir defeito, atender requisito ou tornar uma mudança necessária possível.
- Não otimize por intuição. Para trabalho de performance, obtenha ou proponha uma linha de base mensurável antes de mudar o algoritmo, o uso de memória ou o I/O.
- Para alterações de comportamento, crie ou atualize testes proporcionais ao risco. Se não for possível validar, declare exatamente o que ficou sem validação e por quê.
- Não afirme que algo está "pronto para produção" sem critérios explícitos e evidências correspondentes.

## Validação

Execute as verificações disponíveis e relevantes, como testes, lint, type-check, build, migrações seguras, benchmark ou smoke test. Não trate uma checagem ausente como aprovação.

Se uma ação exigir credenciais, acesso externo, publicação, migração destrutiva ou mudança de infraestrutura com impacto real, pare antes dessa ação e explique o que é necessário.

## Entrega

Ao finalizar, informe de forma objetiva:

1. diagnóstico ou alteração realizada;
2. arquivos e contratos afetados;
3. validações executadas e seus resultados;
4. riscos, suposições ou pendências restantes.

Skills especializadas deste repositório devem seguir este protocolo e acrescentar somente regras específicas do seu domínio.
