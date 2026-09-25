# MEMORIA - Portal Cerrado

## Canonico
- Nome do projeto: Portal Cerrado.
- Backend: FastAPI + Celery + Redis + PostgreSQL.
- Frontend: Next.js + Tailwind.
- Infra: Docker Swarm via Tailscale (100.95.111.24).

## Runtime Real
- Provider LLM: Groq (configurado como LLM_PROVIDER=gemini com GROQ_API_KEY).
- Classificador: heuristico com keywords PT-BR e EN, normalizado via contracts.category_name().
- Categorias canônicas: tech, culture, health, science, sports, politics, economy, security, agriculture, education, clima, world e general.
- Repórteres digitais são definidos em config/reporters.yml, inclusive cobertura internacional para world.
- O servidor ainda executa o Portal Cerrado legado por Docker Compose; a migração para Swarm é pendente.

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

## Migração Swarm Pendente
- O destino oficial é Docker Swarm, com stack `cerrado`; nenhuma nova configuração deve introduzir o nome `botgram`.
- O runtime legado confirmado em 2026-09-18 é Docker Compose, projeto `botgram`, em `/home/razuk/BotGram`, com rede bridge `botgram_portal_cerrado_net` e volumes `botgram_postgres_data` e `botgram_app_data`.
- Esse legado não pode ser parado, removido, renomeado ou alterado até haver aprovação explícita de cutover e encerramento da janela de rollback.
- AP2WEB ocupa a porta pública 8000 no Swarm. Portal Cerrado não deve publicar API nessa porta.
- A porta 443 está ocupada por Tailscale no host. Antes do corte público, definir a estratégia TLS/proxy: liberar 443, usar outro IP/host, ou usar Tailscale Serve/Funnel. Não assumir que Caddy pode bindar 443.
- Para validação em ambiente de teste, a abordagem recomendada é uma stack paralela `cerrado_test`: rede overlay isolada, PostgreSQL e Redis novos, sem reutilizar volumes `botgram_*`, Caddy exposto somente em porta temporária não conflitante (por exemplo 8081) e API/frontend internos.
- A stack Swarm final deve usar nomes de serviço `postgres`, `redis`, `api`, `worker`, `beat`, `frontend` e `caddy`; Caddy deve resolver `api:8000` e `frontend:3000` por DNS de serviço, nunca por `container_name`.
- Antes de qualquer rollout: concluir validações locais, gerar imagens imutáveis por SHA, validar migrations em banco novo e legado simulado, confirmar espaço em disco e documentar backup, rollback e verificação.
- Preflight remoto de 2026-09-18: Swarm manager ativo, cerca de 6,5 GB livres no host, nenhuma stack Swarm `cerrado` ativa e nenhum Caddy do Portal em execução.

## Separação Teste e Produção
- O repositório remoto de teste é `git@github.com:Fran981259/cerrado_test.git`; produção deve usar um repositório/branch definido explicitamente antes do cutover.
- A stack de teste usa `cerrado_test`, volumes `cerrado_test_*`, rede isolada e portas externas 8100 (API), 3100 (frontend), 8181 (HTTP) e 8843 (HTTPS).
- Produção deve trocar nome da stack, volumes, portas públicas, `SITE_URL`, `NEXT_PUBLIC_SITE_URL`, `NEXT_PUBLIC_API_URL` e `CORS_ALLOWED_ORIGINS` antes da aplicação.
- Imagens de produção devem ser publicadas no registry aprovado por digest SHA-256; nunca promover `latest` nem reutilizar imagens do teste.
- Secrets de produção (`PUBLISH_API_KEY`, banco, Redis, LLM, Flower e registry) devem ser recriados no gestor de segredos; não copiar `.env` de teste.
- O cutover exige backup/restore validado, janela de rollback, TLS/proxy confirmado e encerramento explícito dos containers standalone legados.
