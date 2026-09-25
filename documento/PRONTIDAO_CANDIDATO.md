# Prontidão do Candidato — Portal Cerrado

## Estado atual

- Data: 24/09/2026.
- Qualidade estática: Ruff e Mypy do backend aprovados.
- Testes: 120 unitários e 8 de integração aprovados.
- Frontend: lint, TypeScript, build e smoke full-stack local aprovados.
- Runtime: Compose e stack Swarm renderizados, sem deploy executado.
- Recuperação: backup/restore isolado e rollback dry-run aprovados.

## Auditoria da árvore

- Arquivos modificados: 50.
- Arquivos novos não rastreados: 52.
- Artefatos de build ou `node_modules` pendentes: nenhum detectado.
- `git diff --check`: aprovado.
- Commit candidato: `e9dbb16801d041af11ef5873d58882aae17f35d4`.
- Stack de teste: portas externas reservadas `8100`, `3100`, `8181` e `8843`.

## Imagens publicadas pelo CI

- Backend: `ghcr.io/fran981259/portal-cerrado-backend@sha256:6e8baac4f534e5452724c0d1c21764b6c502f111d7935ec744b073c1ee6ec42b`.
- Frontend: `ghcr.io/fran981259/portal-cerrado-frontend@sha256:191d7c39913742bd80ecaa8903306e3c73df73f44291680f4c77a652db02da05`.
- Tags de origem: `db42cc9ace37d9e15654732c5aff2100bc421970`.

## Mudanças obrigatórias antes da produção

- Trocar remote/branch de teste pelo repositório oficial de produção.
- Trocar nome da stack, portas, domínios, CORS, URLs e volumes.
- Publicar imagens novas por digest no registry produtivo.
- Recriar secrets de produção sem copiar valores de teste.
- Confirmar TLS, backup, rollback e encerramento dos containers standalone.

## Bloqueios

1. Revisar e agrupar as alterações em commits lógicos.
2. Criar commit candidato e registrar seu SHA.
3. Executar Lighthouse em navegador disponível.
4. Aprovar explicitamente o ensaio Docker/Swarm de teste.
5. Confirmar o endpoint correto: no nó `100.95.111.24` não existe stack `cerrado`;
   apenas `ap2web` e `n8n_2026_evo-go` foram observadas.

## Regra de promoção

Nenhuma imagem será publicada, stack aplicada ou rollback real executado enquanto
os bloqueios acima não forem resolvidos e o usuário não aprovar o candidato.
