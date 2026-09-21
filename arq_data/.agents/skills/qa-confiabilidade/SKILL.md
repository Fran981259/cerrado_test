---
name: qa-confiabilidade
description: "Planeje, escreva ou revise testes e estratégias de confiabilidade para prevenir regressões e reproduzir defeitos. Use antes de refatorações ou após mudanças de comportamento; não use porcentagem de cobertura como substituta para risco e validação real."
---

# Qa Confiabilidade

Trabalhe em português e leia `../engenharia-base/SKILL.md` antes de atuar. A qualidade da validação depende do comportamento e dos contratos reais do projeto, não da quantidade de arquivos de teste criados.

## Escopo

Use esta skill para testes de caracterização, unitários, integração, contrato, end-to-end, regressão, propriedades, smoke tests e diagnóstico de falhas intermitentes. Em pedidos de análise, não modifique arquivos. Em pedidos de implementação de testes, altere testes e fixtures; altere código de produção somente se o usuário também tiver solicitado corrigir o comportamento ou aprovado explicitamente o ajuste mínimo de testabilidade.

Não use a skill para reescrever o sistema sob o pretexto de testabilidade, mascarar falhas, excluir testes inconvenientes ou aprovar publicação/deploy sem critérios explícitos.

## Descoberta e modelagem de risco

1. Leia instruções do repositório, comandos de teste, configuração de CI e testes existentes.
2. Identifique o comportamento em risco: entrada, estado, saída, efeitos externos, contratos, usuários/consumidores afetados e condição de falha.
3. Determine o nível mínimo de teste que pode detectar a regressão: unitário para regra isolada, integração para fronteira real, contrato para interface compartilhada, e2e para jornada crítica. Não escolha e2e por padrão.
4. Priorize por impacto, probabilidade, reversibilidade, dados envolvidos, exposição externa e histórico de falhas — não por cobertura superficial.
5. Antes de refatoração em código sem testes, crie testes de caracterização do comportamento observado. Diferencie comportamento intencional, bug conhecido e comportamento ainda não especificado.

## Regras para testes confiáveis

- Todo teste deve verificar um comportamento observável ou contrato. Evite testes acoplados a detalhes internos que podem mudar sem regressão funcional.
- Dê nomes que expressem cenário, ação e resultado esperado. Mantenha arrange/act/assert compreensível e com dados mínimos representativos.
- Cubra caminho principal, bordas relevantes, erro esperado e autorização/integridade quando fizerem parte do fluxo alterado.
- Use fixtures, factories e builders existentes. Não esconda dados importantes em setup global opaco nem compartilhe estado mutável entre testes.
- Controle relógio, aleatoriedade, rede, filesystem e concorrência quando forem fontes de não determinismo. Não use `sleep` arbitrário como solução para corrida ou eventual consistência.
- Mocks e stubs devem isolar dependências no nível adequado; eles não comprovam integração externa. Para contratos críticos, adicione teste de integração/contrato quando o ambiente permitir.
- Não acesse produção, não envie mensagens reais, não use credenciais reais e não destrua dados para testar sem autorização explícita e ambiente seguro.
- Não altere expectativa de teste apenas para aceitar a nova implementação. Mudança de expected exige evidência de mudança intencional de requisito ou correção confirmada.

## Diagnóstico de falhas

Ao investigar teste quebrado ou intermitente:

1. reproduza ou colete evidência antes de supor causa;
2. classifique o problema: defeito de produto, teste obsoleto, ambiente, dependência externa, dados, timing ou não determinismo;
3. reduza para caso mínimo quando possível;
4. corrija a causa, não apenas o sintoma;
5. execute novamente o conjunto relevante e registre o limite da reprodução.

Não desabilite, marque como skip, aumente timeout ou adicione retry como “correção” sem explicar a causa e sem autorização quando isso reduziria a detecção de regressão.

## Guardrails contra alucinação e quebra de regras

- Não declare que há cobertura, regressão, compatibilidade, ausência de bug ou confiabilidade total sem comando executado e resultado observado.
- Não invente regras de negócio, contratos, cenários de usuário, fixtures, dados de produção ou comportamento esperado. Quando o requisito for ambíguo, registre a decisão pendente.
- Não trate cobertura de linhas como prova de qualidade, nem um teste verde local como prova de que CI, produção ou uma integração externa funcionam.
- Não afirme que uma falha é flaky sem tentativas, logs, isolamento ou evidência equivalente. Não confunda falha não reproduzida com falha inexistente.
- Não remova assertions, tratamento de erro ou validações para fazer a suíte passar.
- Separe fatos observados, hipóteses de causa e lacunas de ambiente no relatório.

## Validação e entrega

Execute a menor suíte que detecta a mudança e amplie conforme risco: teste específico → módulo → integração/contrato → suíte relevante. Rode lint, type-check, build ou smoke test quando eles fizerem parte da confiança do projeto.

Entregue:

1. comportamento e risco cobertos;
2. estratégia e nível de cada teste;
3. cenários executados e resultado observável;
4. limitações: integrações simuladas, ambientes indisponíveis e casos não cobertos;
5. riscos residuais e a próxima validação recomendada.
