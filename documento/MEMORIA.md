# MEMORIA - Portal Cerrado

## Canonico
- Nome do projeto: Portal Cerrado.
- Backend: FastAPI + Celery + Redis + PostgreSQL.
- Frontend: Next.js + Tailwind.
- Infra: Docker Swarm via Tailscale (100.95.111.24).

## Runtime Real
- Provider LLM: Groq (configurado como LLM_PROVIDER=gemini com GROQ_API_KEY).
- Classificador: heuristico com keywords PT-BR e EN, normalizado via contracts.category_name().
- 11 categorias canonicas: technology, culture, health, sports, politics, economy, security, agriculture, education, clima, general.
- 9 reporeres digitais definidos em config/reporters.yml.
- Deploy via update.sh (docker stack deploy), nao CI/CD automatico.

## Regras Fixas
- Nao misturar docs de planejamento com docs de operacao.
- Nao tratar fallback de desenvolvimento como fluxo principal.
- Nao criar nomes ou marcas paralelas sem aprovacao.

## Identidade Editorial
- Os reporeres digitais sao os mesmos definidos em config/reporters.yml.
- A assinatura padrao deve continuar consistente com o projeto.
- Regras de escrita: 700-900 palavras, piramide invertida, 2-3 fontes cruzadas.

## Infraestrutura de Referencia
- O ambiente deve ser interpretado a partir do estado real do repositorio e da stack ativa.
- Quando houver conflito entre docs antigos e o estado atual, vale o estado atual confirmado.

## Observacao
- Esta memoria e para consistencia, nao para planejamento.
