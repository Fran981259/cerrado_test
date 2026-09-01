# Portainer — Deploy 1-clique (Atualiza Brasil)

**Servidor:** Razuk `100.95.111.24` Debian/Ubuntu, Stack `botgram`

## Opção A — Git Auto-pull (recomendado, 0 manutenção)
1. Portainer → Stacks → Add stack → **Build method: Repository**
2. Repository URL: `https://github.com/Fran981259/BotGram.git`
3. Branch: `main`, Compose path: `docker-compose.yml`
4. **Enable automatic updates** → Polling interval `5m` → ON
5. Add stack → Pronto

Daqui pra frente: `git push` no Lenovo → 5min Portainer puxa sozinho e rebuilda.

## Opção B — 1 comando no host
No host Razuk:
```bash
cd ~/BotGram  # ou /home/razuk/BotGram
./scripts/update.sh
# ou: bash scripts/update.sh
```
Esse script faz: git pull → docker build backend → docker build frontend → docker stack deploy

## Validação
- http://100.95.111.24:3000 → 51 matérias
- http://100.95.111.24:8000/health → articles_count 51
- http://100.95.111.24:5555 → Flower Online

## Manutenção futura
- **Conteúdo:** automático via celery_beat (30min). Nada manual.
- **Deploy:** só git push. Não precisa mais entrar no Console para popular DB.
