# DEPLOY — Portal Cerrado no VPS

Este guia ensina como colocar o portal no ar em um VPS.

---

## 1. ESCOLHA DO VPS

### Recomendado: Hetzner Cloud
- **Preço:** ~€4-6/mês (R$ 25-40)
- **Specs mínimas:**
  - 4 GB RAM
  - 2 vCPU
  - 80 GB SSD
- **Site:** https://hetzner.cloud
- **Região:** Frankfurt ou Nuremberg (mais perto do Brasil)

### Alternativa: DigitalOcean
- **Preço:** ~$6-20/mês
- **Specs mínimas:** mesmo acima
- **Site:** https://digitalocean.com

### Não recomendado
- Hosting compartilhado (não tem Docker/Celery)
- Servidores Windows (mais caro)

---

## 2. PROVISIONAR VPS

### Passo 1: Criar droplet/servidor

1. Acesse Hetzner Cloud Console
2. Clique "New Project"
3. Clique "Add Server"
4. Escolha:
   - **OS:** Ubuntu 22.04 LTS
   - **Type:** CX21 (4 GB RAM, 2 vCPU, 80 GB SSD)
   - **Location:** Frankfurt (ou Nürnberg)
   - **Networking:** IPv4 + IPv6
5. Crie com SSH key (recomendado) ou senha

### Passo 2: Acessar o servidor

```bash
ssh root@SEU_IP_DO_SERVIDOR
```

### Passo 3: Atualizar sistema

```bash
apt update && apt upgrade -y
```

### Passo 4: Criar usuário (não usar root)

```bash
adduser portal
usermod -aG sudo portal
su - portal
```

---

## 3. INSTALAR DOCKER

### Instalar Docker

```bash
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
```

### Verificar instalação

```bash
docker --version
docker-compose --version
```

---

## 4. CONFIGURAR DOMÍNIO (opcional mas recomendado)

### Registrar domínio
- Nome: `portalcerrado.com.br` (exemplo)
- Onde: Namecheap, Cloudflare, Registro.br

### Configurar DNS no Cloudflare
1. Crie conta em https://cloudflare.com
2. Adicione domínio
3. Configure DNS:
   ```
   Tipo    Nome    Conteúdo
   A       @       SEU_IP_DO_VPS
   A       www     SEU_IP_DO_VPS
   ```
4. Ative proteção DDoS gratuita
5. Obtenha SSL/TLS full

---

## 5. ENVIAR PROJETO PARA VPS

### No seu computador

```bash
cd /home/razuk/Documents/BotGram
rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' . portal@SEU_IP:/home/portal/atualiza-brasil/
```

### No VPS, organizar

```bash
cd /home/portal/atualiza-brasil/
mkdir -p data/postgres data/redis
chmod -R 777 data/
```

---

## 6. CONFIGURAR VARIÁVEIS DE AMBIENTE

### No VPS, criar .env

```bash
cd /home/portal/atualiza-brasil
nano .env
```

```env
# Groq (API KEY que você já tem)
GROQ_API_KEY=gsk_sua_key_aqui

# Database
DATABASE_URL=postgresql://portal_user:portal_pass@postgres:5432/atualiza_brasil
POSTGRES_USER=portal_user
POSTGRES_PASSWORD=portal_pass
POSTGRES_DB=atualiza_brasil

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Site
SITE_URL=https://portalcerrado.com.br
SITE_NAME=Portal Cerrado
DEFAULT_LOCALE=pt-BR
TIMEZONE=America/Sao_Paulo

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

---

## 7. SUBIR TUDO COM DOCKER

### Iniciar containers

```bash
cd /home/portal/atualiza-brasil
docker-compose up -d
```

### Verificar status

```bash
docker-compose ps
```

Deve mostrar:
```
NAME                STATUS
postgres            running
redis               running
api                 running
celery_worker       running
celery_beat         running
nginx               running
```

### Ver logs

```bash
# Todos
docker-compose logs -f

# Só API
docker-compose logs -f api

# Só Celery
docker-compose logs -f celery_worker
```

---

## 8. INICIALIZAR BANCO DE DADOS

### Criar tabelas

```bash
docker-compose exec api python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(engine)
print('Tabelas criadas!')
"
```

### Verificar

```bash
docker-compose exec postgres psql -U portal_user -d atualiza_brasil -c "\dt"
```

---

## 9. CONFIGURAR NGINX + SSL

### Arquivo nginx.conf (já está no projeto)

O projeto já tem `nginx.conf`. Para usar SSL com Cloudflare:

### No Cloudflare
1. Vá em SSL/TLS → Overview
2. Escolha "Full" ou "Flexible"
3. Vá em SSL/TLS → Origin Server
4. Crie um certificado (gratuito)
5. Copie o certificado e private key

### No VPS

```bash
sudo apt install -y certbot
sudo certbot certonly --nginx -d portalcerrado.com.br -d www.portalcerrado.com.br
```

---

## 10. VERIFICAR TUDO

### Testar API

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{"status":"healthy","database":"connected","timestamp":"..."}
```

### Testar notícias

```bash
curl http://localhost:8000/api/news?limit=5
```

### Ver Celery

```bash
docker-compose exec celery_worker celery -A app.celery_app inspect active
```

---

## 11. MONITORAMENTO

### Ver uso de recursos

```bash
docker stats
```

### Logs centralizados

Adicione ao crontab:
```bash
crontab -e
```
```
0 * * * * docker-compose -f /home/portal/atualiza-brasil/docker-compose.yml logs --tail=100 >> /var/log/portal.log 2>&1
```

### Uptime monitoring (gratuito)

Use https://uptimerobot.com (gratuito):
1. Crie conta
2. Adicione monitor para https://portalcerrado.com.br
3. Alerta por email se cair

---

## 12. MANUTENÇÃO

### Backup do banco

```bash
docker-compose exec postgres pg_dump -U portal_user atualiza_brasil > backup_$(date +%Y%m%d).sql
```

### Restaurar backup

```bash
cat backup_20260828.sql | docker-compose exec -T postgres psql -U portal_user atualiza_brasil
```

### Update do projeto

```bash
cd /home/portal/atualiza-brasil
git pull  # se usar git
docker-compose down
docker-compose build
docker-compose up -d
```

### Limpar imagens antigas

```bash
docker system prune -af
```

---

## RESUMO DOS COMANDOS

```bash
# Primeira vez
ssh root@SEU_IP
apt update && apt upgrade -y
adduser portal && usermod -aG sudo portal
su - portal
sudo apt install -y docker-ce...
sudo usermod -aG docker portal
exit && exit
ssh portal@SEU_IP
rsync -avz ... /home/portal/atualiza-brasil/
cd /home/portal/atualiza-brasil
nano .env  # configurar
docker-compose up -d
docker-compose exec api python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(engine)"
curl http://localhost:8000/health

# Dia-a-dia
docker-compose logs -f
docker-compose restart
docker-compose exec api python scripts/...
docker system prune -af
```

---

## CUSTO ESTIMADO MENSAL

| Item | Custo |
|------|-------|
| VPS (Hetzner CX21) | R$ 25-40 |
| Domínio (.news) | R$ 30-50/ano |
| Cloudflare (free) | R$ 0 |
| **Total** | **~R$ 50-80/mês** |

---

## TROUBLESHOOTING

### "Connection refused" no postgres
```bash
docker-compose down
docker-compose rm -f
docker-compose up -d
```

### Celery não processa tarefas
```bash
docker-compose logs celery_worker
docker-compose restart celery_worker celery_beat
```

### SSL inválido
```bash
sudo certbot renew --force-renewal
docker-compose restart nginx
```

### Banco corrompido
```bash
docker-compose down
rm -rf data/postgres/*
docker-compose up -d
# Recriar tabelas
```

---

**Deploy finalizado?** Continue para `DEPLOY_CHECKLIST.md` e marque os itens conforme for fazendo.
