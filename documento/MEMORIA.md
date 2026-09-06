# MEMORIA - Portal Cerrado

## Canonico
- Nome do projeto: Portal Cerrado.
- Backend: FastAPI + Celery + Redis + PostgreSQL.
- Frontend: Next.js.
- O projeto tem modo de desenvolvimento com fallback local, mas o objetivo e usar dados reais no fluxo produtivo.
- Quando for para producao na VPS, a camada de LLM deve ser migrada para Gemini, se a decisao de deploy assim exigir.

## Regras Fixas
- Nao misturar docs de planejamento com docs de operacao.
- Nao tratar fallback de desenvolvimento como fluxo principal.
- Nao criar nomes ou marcas paralelas sem aprovacao.

## Identidade Editorial
- Os repórteres digitais sao os mesmos definidos em `config/reporters.yml`.
- A assinatura padrao deve continuar consistente com o projeto.

## Infraestrutura de Referencia
- O ambiente deve ser interpretado a partir do estado real do repositorio e da stack ativa.
- Quando houver conflito entre docs antigos e o estado atual, vale o estado atual confirmado.

## Observacao
- Esta memoria e para consistencia, nao para planejamento.
