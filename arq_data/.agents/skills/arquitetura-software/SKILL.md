---
name: arquitetura-software
description: "Avalie decisões arquiteturais, dependências, fronteiras e planos de refatoração ou migração em projetos de software. Use após um diagnóstico ou quando uma mudança estrutural exige trade-offs; não use para reescrever código por preferência estética."
---

# Arquitetura Software

Avalie a arquitetura existente e proponha decisões executáveis, em português. Leia `../engenharia-base/SKILL.md` antes de agir. Quando houver diagnóstico existente, use-o como evidência; quando o escopo ainda for desconhecido, execute primeiro `../analise-sistemas/SKILL.md` ou declare claramente que a análise arquitetural é preliminar.

## Escopo e autorização

Esta skill serve para analisar modularidade, dependências, limites entre componentes, contratos, evolução de dados, integração entre serviços e estratégia de mudança. Por padrão, entregue diagnóstico e plano; não modifique código, configurações ou infraestrutura sem um pedido explícito de implementação.

Não transforme uma preferência de padrão em requisito. Clean Architecture, DDD, microserviços, CQRS, eventos, repositórios, ORMs, filas e camadas adicionais são meios, não objetivos. Só os recomende quando resolverem uma limitação observada e o custo for justificável.

## Evidência mínima

Antes de recomendar mudança estrutural:

1. Inspecione instruções do repositório, árvore de módulos, dependências, pontos de entrada, configurações de execução, testes e contratos relevantes.
2. Mapeie responsabilidades reais, fluxo de controle e fluxo de dados dos componentes envolvidos. Não deduza a arquitetura apenas por nomes de diretórios.
3. Identifique consumidores e produtores dos contratos afetados: APIs, eventos, schemas, banco de dados, arquivos, jobs, CLI, variáveis de ambiente e integrações externas.
4. Registre as restrições observadas: compatibilidade, prazo, equipe, custo operacional, volume, segurança, deployment e dados. Se não forem conhecidas, marque como desconhecidas.

## Regras de decisão

Para cada decisão arquitetural, apresente pelo menos:

- o problema concreto e sua evidência;
- o estado atual e os limites afetados;
- opções viáveis, incluindo manter a arquitetura atual quando apropriado;
- trade-offs: complexidade, custo de migração, risco operacional, manutenção, desempenho e reversibilidade;
- decisão recomendada e as condições que a tornam válida;
- critérios mensuráveis ou observáveis de sucesso;
- estratégia de implantação, compatibilidade e rollback quando houver mudança de contrato, dados ou infraestrutura.

Prefira evolução incremental e compatível. Uma reescrita total só é aceitável se houver evidência de que a migração gradual é inviável ou mais arriscada; declare explicitamente essa evidência e os riscos remanescentes.

## Guardrails contra alucinação e quebra de escopo

- Distinga **fato observado**, **inferência** e **decisão proposta**. Fatos devem apontar para arquivos, símbolos, testes ou configuração; inferências devem explicar seus limites.
- Não invente requisitos não funcionais, limites de escala, custos, SLAs, topologia de produção, volume de tráfego, regras de negócio ou dependências de terceiros.
- Não declare que um componente está “desacoplado”, “escalável”, “seguro”, “testável” ou “pronto para produção” sem critério e evidência verificável.
- Não classifique uma dependência como circular, um módulo como responsável demais ou uma interface como pública sem seguir as referências relevantes no código.
- Não proponha dividir em serviços, adicionar banco/fila/cache ou alterar modelo de dados sem explicar a operação futura: ownership, falhas, observabilidade, consistência e custo de manutenção.
- Não esconda impacto de compatibilidade. Se uma mudança alterar entrada, saída, persistência ou comportamento, identifique consumidores, dados históricos e plano de transição.
- Não aplique mudanças arquiteturais automaticamente. Pare e peça confirmação antes de ações irreversíveis, disruptivas ou externas, mesmo quando uma implementação tiver sido solicitada.

## Plano de execução

Quando o usuário autorizar implementação, transforme a decisão em etapas pequenas e verificáveis:

1. estabelecer testes de caracterização ou contratos antes da mudança;
2. introduzir a nova fronteira ou adaptação mantendo compatibilidade quando necessário;
3. migrar um fluxo por vez;
4. validar comportamento, dados e observabilidade em cada etapa;
5. remover o caminho legado somente após evidência de que não há consumidores e com autorização para a remoção.

Cada etapa deve listar arquivos/serviços afetados, pré-condições, risco, rollback e validação. Não escreva código nesta skill a menos que isso tenha sido explicitamente solicitado após a decisão.

## Formato de entrega

Entregue:

1. **Contexto e limites analisados** — escopo, fatos e lacunas.
2. **Mapa arquitetural atual** — componentes, responsabilidades, dependências e contratos relevantes.
3. **Problemas arquiteturais priorizados** — evidência, impacto, condição de ocorrência e risco de não agir.
4. **Decisões recomendadas** — opções, trade-offs, decisão e critério de sucesso.
5. **Plano de migração** — etapas incrementais, compatibilidade, validação e rollback.
6. **Decisões pendentes do usuário** — somente quando uma escolha de produto, custo ou risco não puder ser inferida com segurança.
