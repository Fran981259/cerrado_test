# Portal Cerrado — Regras de Execução

Project Map: leia `portal-cerrado.md` na raiz antes de qualquer ação.

## Regra pétrea de entrega

Não implementar novas funcionalidades, não publicar imagens, não executar deploy,
não aplicar stack e não fazer corte de ambiente enquanto todos os gates definidos
em `documento/PLANO_ACAO.md` não estiverem aprovados por evidência atual.

Exceção única: correções estritamente necessárias para fazer os gates passarem.
Toda exceção deve registrar causa, arquivos afetados, validação e risco residual.

## Proteção do estado atual

Preserve alterações não relacionadas. Nunca descarte mudanças, dados ou volumes sem
autorização explícita do usuário e uma verificação prévia do alvo.
