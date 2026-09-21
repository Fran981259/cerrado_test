---
name: desenvolvimento-frontend
description: "Implemente, corrija ou revise interfaces web, componentes, estado, formulários, acessibilidade e integração com APIs. Use para mudanças no cliente; não use para inventar produto, identidade visual ou contratos de backend inexistentes."
---

# Desenvolvimento Frontend

Trabalhe em português e leia `../engenharia-base/SKILL.md` antes de atuar. Para escopo funcional ou fluxo desconhecido, aplique `../analise-sistemas/SKILL.md` antes de propor uma mudança ampla.

## Escopo

Use esta skill para rotas, páginas, componentes, estilos, design system existente, gerenciamento de estado, formulários, navegação, acessibilidade, internacionalização e consumo de APIs. Inspecione antes de editar e modifique apenas o necessário para o pedido autorizado.

Não invente telas, jornadas, copy, identidade visual, endpoints, campos de formulário, regras de autorização ou comportamento de negócio. Não redesenhe uma interface inteira para corrigir um detalhe, nem troque framework, biblioteca de componentes ou estratégia de estado por preferência.

## Inspeção obrigatória

1. Leia instruções do projeto, documentação, configuração do framework, rotas e comandos de execução/teste relevantes.
2. Localize a página ou componente afetado, seus chamadores, seu estado, estilos, dados de entrada e testes.
3. Identifique padrões existentes: tokens, componentes reutilizáveis, breakpoints, convenções de formulário, mensagens, loading/error/empty states, i18n e forma de consumir a API.
4. Siga o fluxo visível e o fluxo de dados: interação do usuário → atualização de estado → requisição/efeito → sucesso, falha, carregamento e navegação.
5. Quando a mudança depender de backend, confirme o contrato no código, schema, documentação ou teste. Se ele não existir, não fabrique uma integração.

## Regras de implementação

- Preserve a semântica e a consistência visual do projeto. Reutilize componentes e tokens existentes quando forem adequados; não copie componentes parecidos sem motivo.
- Modele explicitamente estados de carregamento, vazio, erro, sucesso e submissão quando o fluxo os exigir. Evite interface que pareça concluída enquanto uma operação ainda está pendente ou falhou.
- Em formulários, mantenha valores, validação, mensagens e prevenção de duplo envio coerentes com o padrão existente. Validação no cliente melhora experiência, mas nunca substitui validação do servidor.
- Use elementos HTML semânticos antes de adicionar ARIA. Quando ARIA for necessária, mantenha papel, nome acessível, estado e comportamento de teclado compatíveis.
- Preserve foco, navegação por teclado e retorno de foco em modais, menus e alterações de rota quando esses elementos forem afetados. Não capture foco ou atalhos globalmente sem necessidade.
- Respeite os breakpoints e o sistema de layout existentes. Não alegue responsividade sem verificar os tamanhos de viewport relevantes ou registrar que essa verificação não foi possível.
- Consuma dados pela camada e pelo padrão já adotados no projeto. Não exponha segredos no bundle, não armazene tokens sem base na estratégia existente e não trate verificações de rota no cliente como controle de segurança suficiente.
- Evite otimização especulativa. Memoização, virtualização, divisão de bundle e redução de renderizações só devem ser introduzidas com evidência de custo ou requisito observável.

## Guardrails contra alucinação e quebra de regras

- Diferencie fatos observados, inferências e decisões de UX propostas. Cite arquivos, componentes, testes ou especificações para fatos importantes.
- Não invente usuário, persona, prioridade de produto, conteúdo, requisito legal, métrica de conversão, navegador suportado ou critério de design.
- Não declare conformidade WCAG, compatibilidade em navegadores, boa performance, design aprovado ou acessibilidade completa sem teste ou evidência delimitada.
- Não presuma que uma resposta da API contém um campo, que uma ação foi persistida ou que uma feature flag está ativa sem contrato ou validação observável.
- Não remova validação, tratamento de erro, confirmação destrutiva, mecanismo de autorização ou teste para simplificar a implementação.
- Não manipule DOM, rota, storage ou estado global fora das convenções do framework/projeto sem explicar o motivo e o impacto.
- Não faça alterações em massa de CSS, formatação ou componentes não relacionados. Preserve alterações locais já existentes.

## Validação

Execute as verificações disponíveis e pertinentes: type-check, lint, testes de componente/e2e, build e, quando possível, inspeção visual da rota em viewports relevantes. Para mudanças de fluxo, valide ao menos o caminho principal e uma falha relevante.

Registre claramente o que foi validado em execução real, o que foi validado apenas por teste automatizado e o que não foi verificado. Não descreva uma inspeção estática como teste visual ou integração real.

## Entrega

Informe:

1. componentes, rotas e fluxo de usuário afetados;
2. contratos de dados usados ou preservados;
3. comportamento de estados, validação e acessibilidade alterado;
4. verificações executadas e resultado;
5. limitações, hipóteses e riscos restantes.
