---
name: devops-entrega
description: "Projete, revise ou implemente configuração local de execução, Docker, CI/CD, deploy, observabilidade e segurança operacional. Use para tornar uma aplicação reproduzível e entregável; não use para aplicar mudanças em infraestrutura externa sem autorização explícita."
---

# Devops Entrega

Trabalhe em português e leia `../engenharia-base/SKILL.md` antes de atuar. Diferencie sempre entre criar/revisar artefatos de infraestrutura no repositório e aplicar uma alteração em ambiente externo: a segunda exige autorização específica.

## Escopo

Use esta skill para Dockerfiles, Compose, scripts de inicialização, dependências de runtime, CI/CD, configurações de ambiente, deploy, health checks, logging, métricas, alertas, secrets e práticas de segurança operacional. Inspecione a aplicação antes de criar configuração.

Não faça deploy, push de imagem, alteração de cloud, DNS, banco, segredo, pipeline remoto, registry, permissões, firewall ou qualquer recurso externo sem o usuário autorizar a ação exata, o ambiente-alvo e a estratégia de rollback. Uma configuração criada localmente não é evidência de que produção funciona.

## Descoberta obrigatória

1. Leia instruções do repositório, documentação, manifests existentes e comandos de build/teste.
2. Determine pelo código e pelos manifests: runtime, versão, gerenciador de dependências, comando de entrada, portas, arquivos necessários, build output, serviços dependentes, variáveis de ambiente, persistência e health checks existentes.
3. Identifique o ambiente-alvo somente se estiver documentado ou fornecido. Caso contrário, produza uma solução local/portável e marque decisões de deployment como pendentes.
4. Mapeie dados e credenciais que não podem entrar em imagem, logs, repositório ou artefatos de CI.
5. Preserve convenções já adotadas pelo projeto quando forem válidas; não troque plataforma, base image ou pipeline apenas por preferência.

## Regras de containerização e execução

- Use imagem base e versão compatíveis com o runtime observado. Fixe versões quando o projeto já adotar esse controle ou quando a reprodutibilidade exigir, sem inventar versões inexistentes.
- Inclua somente arquivos necessários no contexto de build e crie/atualize `.dockerignore` quando isso reduzir exposição ou tamanho sem excluir artefatos necessários.
- Separe build de runtime quando houver ganho concreto de tamanho, segurança ou dependências; não imponha multi-stage em aplicação trivial sem motivo.
- Execute como usuário não-root quando compatível com o processo e permissões de arquivos. Não quebre escrita necessária em volumes, cache ou diretórios temporários para cumprir a regra superficialmente.
- Não inclua segredos, `.env`, chaves, tokens, certificados privados ou credenciais em imagem, Dockerfile, argumentos de build, commit ou log.
- Use sinais, processo principal e health check conforme a aplicação realmente suporta. Não adicione endpoint de saúde fictício nem declare readiness sem validar dependências relevantes.
- Documente volumes, portas, permissões e variáveis obrigatórias. Nunca forneça valores reais de segredo como exemplo.

## Regras para CI/CD e operação

- CI deve validar o que é relevante: dependências reproduzíveis, testes, lint/type-check, build e artefatos. Não marque etapa como obrigatória se ela não existe nem finja que a pipeline cobre cenário não executado.
- Aplique menor privilégio a tokens e permissões. Não desative verificação TLS, assinatura, proteção de branch, scan ou aprovação para contornar falhas.
- Cache de dependências precisa ter chave relacionada à versão/lockfile e não pode vazar segredos ou artefatos não confiáveis entre contextos.
- Separe build, teste e deploy. Deploy deve ter ambiente, gatilho, aprovação quando aplicável, observabilidade e rollback definidos antes da aplicação externa.
- Defina logging, métricas, tracing e alertas apenas para sinais que a aplicação realmente emite ou que possam ser implementados. Não afirme SLO, cobertura de observabilidade ou monitoramento ativo sem evidência.
- Para migrações e alterações de configuração, descreva ordem de aplicação, compatibilidade, backup quando necessário, janela de risco e rollback. Nunca presuma que rollback de schema é seguro.

## Guardrails contra alucinação e quebra de regras

- Classifique afirmações como fato observado, proposta ou desconhecido. Cite manifests, código, comandos ou resultados para fatos materiais.
- Não invente plataforma de hospedagem, região, domínio, porta pública, limites de recursos, variável de ambiente, credencial, conta cloud, registry, política de rede ou mecanismo de autoscaling.
- Não alegue que uma imagem é segura, enxuta, reproduzível, deployada, saudável, observável, escalável ou pronta para produção sem comandos e resultados correspondentes.
- Não confunda build bem-sucedido com runtime funcional, nem teste local com acesso a serviços externos, permissões ou comportamento de produção.
- Não exponha segredo em relatório, diff ou comando. Se detectar possível segredo, não o repita; indique apenas caminho/forma segura de rotação e remoção conforme o escopo autorizado.
- Não use ações destrutivas, `--force`, limpeza de volumes/imagens/dados, recriação de recursos ou alteração de estado remoto para “resolver” uma falha sem alvo confirmado e autorização explícita.

## Validação e entrega

Quando permitido, valide artefatos localmente: parse/lint de manifests, build da imagem, execução com usuário configurado, smoke test do processo, health check e comando de teste do projeto. Se o ambiente não permitir build ou execução, informe o comando recomendado e o que permaneceu não verificado.

Entregue:

1. contexto de execução e dependências observadas;
2. arquivos de infraestrutura criados/alterados e justificativa;
3. configuração externa necessária, sem incluir segredos;
4. validações locais executadas e resultado;
5. riscos, decisões pendentes, etapas de deploy e rollback — claramente separados de ações já realizadas.
