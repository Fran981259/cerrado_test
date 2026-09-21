---
name: desenvolvimento-backend
description: "Implemente, corrija ou revise serviços de backend, APIs, regras de negócio, persistência e integrações locais. Use para mudanças de comportamento no servidor; não use para decisões arquiteturais amplas sem diagnóstico ou para publicar serviços externos."
---

# Desenvolvimento Backend

Trabalhe em português e leia `../engenharia-base/SKILL.md` antes de atuar. Para uma mudança estrutural de alto impacto ou com escopo desconhecido, aplique primeiro `../analise-sistemas/SKILL.md` ou explique por que a inspeção atual é suficiente.

## Escopo

Use esta skill para código do lado servidor: handlers, APIs, serviços, regras de negócio, jobs, acesso a banco, filas, cache, autenticação/autorização e integrações. Diagnostique antes de editar; implemente somente o que o pedido autoriza.

Não faça deploy, publique dados, altere credenciais, chame sistemas de produção, rode migração irreversível ou modifique infraestrutura externa sem autorização específica e condições de rollback. Não substitua a arquitetura atual por um framework, ORM, banco ou fila apenas porque seriam sua preferência.

## Inspeção obrigatória

Antes de mudar comportamento:

1. Leia as instruções do repositório, a documentação e os comandos de teste relevantes.
2. Siga o fluxo afetado: entrada (rota, RPC, consumidor, CLI ou job) → autenticação/autorização → validação → regra de negócio → persistência/integração → saída e tratamento de falhas.
3. Identifique contratos existentes: métodos HTTP, schemas, códigos de status, formatos de erro, eventos, tabelas, migrações, variáveis de ambiente e consumidores conhecidos.
4. Localize testes existentes e alterações não relacionadas no diretório de trabalho. Preserve ambas quando não forem parte do pedido.

Se o comportamento desejado, o chamador, o modelo de autorização ou a compatibilidade esperada não estiverem claros e a escolha puder mudar dados, acesso ou API, pare antes de implementar e exponha a decisão necessária.

## Regras de implementação

- Preserve assinaturas e comportamento público existentes, salvo quando a ruptura for solicitada e documentada.
- Valide dados na fronteira usando os mecanismos já adotados pelo projeto. Erros de entrada devem seguir o formato e a semântica existentes, sem vazar detalhes internos.
- Mantenha regras de negócio independentes de HTTP, banco e SDKs externos quando o código existente permitir isso sem introduzir abstração artificial.
- Faça autorização no ponto onde o recurso é acessado. Não confunda autenticação com permissão e não confie em identificadores, papéis ou tenant enviados pelo cliente sem a validação prevista pelo sistema.
- Use as práticas de acesso a dados do próprio projeto. Não concatene dados externos em consultas, comandos ou caminhos; não desative proteções de validação para “fazer funcionar”.
- Em operações que escrevem mais de uma entidade ou produzem efeito externo, avalie atomicidade, idempotência, falha parcial, retries e consistência conforme a evidência do fluxo. Não alegue transacionalidade se a tecnologia ou o código não a garantirem.
- Não registre segredos, tokens, senhas, dados pessoais desnecessários ou payloads sensíveis. Siga as convenções existentes de configuração e observabilidade.
- Não adicione dependência, endpoint, tabela, campo, variável de ambiente ou feature flag sem necessidade demonstrada e sem registrar o impacto.

## Guardrails contra alucinação

- Trate contratos como observados somente quando encontrados em código, schema, teste, documentação confiável ou consumidor verificável. Se houver conflito, registre-o.
- Não invente campos, papéis, permissões, regras de negócio, estados de entidade, formatos de erro, tabelas, índices ou endpoints.
- Não declare que uma mudança é segura, compatível, idempotente, performática ou protegida contra injeção sem teste, mecanismo ou evidência correspondente.
- Não assuma que uma integração respondeu, que uma mensagem foi entregue ou que uma transação foi confirmada sem executar uma validação permitida e observar o resultado.
- Não use mocks como prova de integração real; descreva-os apenas como teste do contrato simulado.
- Não silencie exceções, retorne sucesso em falhas ou transforme toda falha em erro genérico para esconder comportamento desconhecido.

## Testes e validação

Para cada mudança de comportamento, cubra o caminho de sucesso, as falhas previsíveis e a regra de autorização ou integridade relevante. Use o nível adequado já existente no projeto: unitário para regra isolada, integração para persistência/handler, contrato para API ou consumidor.

Quando alterar banco de dados, valide compatibilidade entre código, schema e migração. Apresente plano de rollback; não aplique a migração fora de ambiente local sem autorização explícita.

Execute os testes, lint, type-check, build ou smoke test disponíveis e relevantes. Se não puder executar alguma validação, registre o motivo, o risco e a maneira de executá-la.

## Entrega

Informe objetivamente:

1. fluxo e contrato alterados;
2. regras de validação, autorização e persistência afetadas;
3. compatibilidade ou quebra introduzida;
4. testes e verificações executados, com resultado;
5. riscos, pré-requisitos e ações externas ainda necessárias.
