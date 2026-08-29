# Atualiza Brasil

> Portal de notícias brasileiro 100% automatizado, com repórteres digitais por área temática. Piloto no Mato Grosso do Sul, com expansão para cobertura nacional e global.

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-proprietary-blue.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()

---

## 📋 Sumário

1. [Sobre o Projeto](#-sobre-o-projeto)
2. [Arquitetura](#-arquitetura)
3. [Equipe de Repórteres Digitais](#-equipe-de-repórteres-digitais)
4. [Fontes de Notícias](#-fontes-de-notícias)
5. [Instalação](#-instalação)
6. [Configuração](#-configuração)
7. [Uso](#-uso)
8. [Deploy](#-deploy)
9. [Monitoramento](#-monitoramento)
10. [Compliance e Legal](#-compliance-e-legal)
11. [Roadmap](#-roadmap)
12. [Contribuição](#-contribuição)
13. [Licença](#-licença)

---

## 🎯 Sobre o Projeto

O **Atualiza Brasil** é um portal de notícias automatizado que combina inteligência artificial, curadoria editorial e jornalismo digital. O sistema coleta notícias de fontes nacionais e internacionais, reescreve com a voz única de repórteres digitais especializados, e publica em um portal compatível com Google AdSense.

### Objetivos

- **Produção automatizada** de conteúdo jornalístico original
- **Cobertura global**: minerar notícias internacionais que impactam o Brasil
- **Curiosidades engajantes**: fatos curiosos distribuídos por todos os segmentos
- **Identidade editorial**: repórteres digitais com voz própria
- **100% autônomo**: sem intervenção humana na produção diária
- **Compatível com AdSense**: monetização desde o primeiro dia
- **Compliance legal**: respeito integral à Lei 9.610/98 (Art. 46/47)

### Por que minerar portais internacionais?

Notícias de **geopolítica, tecnologia, ciência, mercados globais e saúde** frequentemente surgem primeiro no exterior. O Atualiza Brasil monitora fontes globais para trazer essas notícias em primeira mão para o público brasileiro, traduzindo contexto e impacto local.

```
Exemplo de fluxo:
Reuters (US) → Captura → Reescrita (Camila Rocha) → Publicação
"Fed raises interest rates" → "Banco Central dos EUA sobe juros — impacto no Brasil"
```

---

## 🏗️ Arquitetura

### Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ORQUESTRADOR                                │
│              (Celery + Redis + Beat Scheduler)                       │
│   Coordena ciclo de produção 24/7 com auto-recuperação              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┬──────────────┐
         │                 │                 │              │
         ▼                 ▼                 ▼              ▼
   ┌──────────┐      ┌──────────┐     ┌──────────┐  ┌──────────┐
   │ SCANNER  │      │ MINER    │     │ REWRITER │  │ QUALITY  │
   │ (Nacional│      │ (Global) │     │  (LLM)   │  │ CHECK    │
   │  + MS)   │      │          │     │          │  │          │
   └────┬─────┘      └────┬─────┘     └────┬─────┘  └────┬─────┘
        │                 │                │             │
        └─────────────────┼────────────────┘             │
                          ▼                              │
                  ┌──────────────┐                      │
                  │   DATABASE   │◀─────────────────────┘
                  │ (PostgreSQL) │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  PUBLISHER   │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   FRONTEND   │  ──▶  AdSense + Usuários
                  │  (Next.js)   │
                  └──────────────┘
```

### Stack Tecnológica

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| **API Backend** | FastAPI 0.100+ | Endpoints REST |
| **Task Queue** | Celery 5.3+ | Tarefas assíncronas |
| **Scheduler** | Celery Beat | Agendamento |
| **Broker** | Redis 7+ | Mensageria + cache |
| **Database** | PostgreSQL 15+ | Persistência |
| **ORM** | SQLAlchemy 2.0+ | Mapeamento objeto-relacional |
| **LLM** | OpenRouter (Claude/GPT) | Reescrita com IA |
| **Web Scraping** | BeautifulSoup + httpx | Coleta de conteúdo |
| **Frontend** | Next.js 14 (App Router) | Renderização + SEO |
| **Styling** | Tailwind CSS | Design responsivo |
| **CDN** | Cloudflare | Distribuição global |
| **Monitoring** | Sentry + Grafana | Observabilidade |
| **Email** | Resend | Notificações transacionais |

### Estrutura de Diretórios

```
atualiza-brasil/
├── app/                          # Backend Python
│   ├── __init__.py
│   ├── main.py                   # API FastAPI principal
│   ├── orchestrator.py           # Coordenador central
│   ├── scanner.py                # Coleta de portais nacionais/MS
│   ├── miner.py                  # Mineração de portais globais
│   ├── filter.py                 # Filtros de relevância e duplicatas
│   ├── rewriter.py               # Reescrita com LLM
│   ├── quality.py                # Verificação de qualidade
│   ├── publisher.py              # Publicação no banco
│   ├── schema.py                 # Modelos SQLAlchemy
│   ├── database.py               # Conexão com DB
│   ├── celery_app.py             # Configuração Celery
│   ├── tasks/                    # Tarefas Celery
│   │   ├── __init__.py
│   │   ├── scan_tasks.py
│   │   ├── mining_tasks.py
│   │   ├── rewrite_tasks.py
│   │   └── publish_tasks.py
│   ├── agents/                   # Agentes especializados
│   │   ├── __init__.py
│   │   └── reporter_agent.py
│   └── utils/                    # Utilitários
│       ├── __init__.py
│       ├── logger.py
│       ├── cache.py
│       └── helpers.py
│
├── frontend/                     # Next.js Frontend
│   ├── app/                      # App Router
│   │   ├── page.tsx              # Home
│   │   ├── [category]/           # Páginas por categoria
│   │   ├── [category]/[slug]/    # Páginas de notícia
│   │   ├── sobre/                # Sobre o portal
│   │   ├── privacidade/          # Política de privacidade
│   │   ├── termos/               # Termos de uso
│   │   ├── contato/              # Contato
│   │   └── api/                  # API routes
│   ├── components/               # Componentes React
│   ├── lib/                      # Utilities
│   ├── public/                   # Assets estáticos
│   └── styles/                   # Estilos globais
│
├── config/                       # Configurações YAML
│   ├── orchestrator.yaml         # Config geral
│   ├── reporters.yml             # Perfis dos repórteres
│   ├── portals_br.yml            # Portais nacionais/MS
│   ├── portals_global.yml        # Portais globais
│   └── prompts/                  # Prompts por repórter
│       ├── technology.md
│       ├── economy.md
│       └── ...
│
├── docker/                       # Configurações Docker
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── nginx.conf
│   └── postgres/
│       └── init.sql
│
├── scripts/                      # Scripts auxiliares
│   ├── setup.sh                  # Setup inicial
│   ├── backup.sh                 # Backup do DB
│   ├── deploy.sh                 # Deploy
│   └── health_check.sh           # Verificação
│
├── tests/                        # Testes automatizados
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── logs/                         # Logs do sistema
├── .github/                      # GitHub Actions
├── docker-compose.yml            # Orquestração Docker
├── requirements.txt              # Dependências Python
├── package.json                  # Dependências Node
├── tailwind.config.js            # Config Tailwind
├── .env.example                  # Variáveis de ambiente (template)
├── .gitignore
├── SPEC.md                       # Especificação técnica completa
└── README.md                     # Este arquivo
```

---

## 👥 Equipe de Repórteres Digitais

Cada repórter digital tem **voz editorial própria, especialidades definidas e personalidade consistente**.

| Repórter | Área | Slug | Tom de Voz |
|----------|------|------|------------|
| **ENZO BIANCHI** | Tecnologia & Inovação | `enzo.bianchi` | Técnico, futurista, dinâmico |
| **MARCUS TEIXEIRA** | Esportes & Lazer | `marcus.teixeira` | Empolgado, narrativo, competitivo |
| **RAFAEL DUMAS** | Polícia & Segurança | `rafael.dumas` | Sério, direto, investigativo |
| **LUCIANA FREITAS** | Política & Governo | `luciana.freitas` | Preciso, neutro, informado |
| **MAYA SANTOS** | Saúde & Ciência | `maya.santos` | Científico, cauteloso, rigoroso |
| **LUCAS NAKAMURA** | Educação & Concursos | `lucas.nakamura` | Didático, acessível, motivador |
| **BIA FERNANDES** | Agronegócio & Mercado | `bia.fernandes` | Territorial, profissional, realista |
| **LEON VAZ** | Cultura & Eventos | `leon.vaz` | Criativo, sensível, engajado |
| **CAMILA ROCHA** | Economia & Empregos | `camila.rocha` | Analítico, pragmático, direto |

### Cronograma de Publicação

| Horário | Repórter | Área | Frequência |
|---------|----------|------|------------|
| 05:00 | Enzo Bianchi | Tecnologia | Diária |
| 06:00 | Enzo Bianchi | Tecnologia | Diária |
| 07:00 | Marcus Teixeira | Esportes | Diária |
| 08:00 | Rafael Dumas | Segurança | Diária |
| 09:00 | Luciana Freitas | Política | Diária |
| 10:00 | Maya Santos | Saúde | Diária |
| 12:00 | Lucas Nakamura | Educação | Diária |
| 14:00 | Bia Fernandes | Agronegócio | Diária |
| 16:00 | Leon Vaz | Cultura | Diária |
| 18:00 | Camila Rocha | Economia | Diária |
| 20:00 | Marcus Teixeira | Esportes | Diária |
| 22:00 | Enzo Bianchi | Tecnologia | Diária |

### 🎯 Curiosidades (Engajamento Máximo)

Curiosidades são geradas automaticamente em **todos os segmentos** e distribuídas ao longo do dia. Cada repórter digital pode publicar fatos curiosos próprios ou detectados de fontes externas.

**Mecanismo:**
- ✅ Cada categoria tem 1-2 curiosidades próprias/dia
- ✅ Curiosidades detectadas em artigos externos recebem **+30% de boost de engajamento**
- ✅ Intercaladas entre artigos normais (1 a cada ~7 artigos)
- ✅ Marcadas visualmente como "Você sabia?"
- ✅ Atribuídas ao repórter do segmento

**Exemplos:**
- **Tecnologia (Enzo Bianchi)**: "Você sabia que o primeiro computador pesava 30 toneladas?"
- **Esportes (Marcus Teixeira)**: "A bola da primeira Copa pesava o dobro das atuais!"
- **Saúde (Maya Santos)**: "Seu corpo tem mais bactérias do que células!"
- **Cultura (Leon Vaz)**: "A palavra 'saudade' não tem tradução em nenhum idioma!"

**Por que funciona?**
Curiosidades têm **engajamento até 3x maior** que notícias normais porque:
- São compartilháveis em redes sociais
- Geram comentários ("eu não sabia!")
- Aumentam tempo de permanência na página
- Trazem público diversificado para o portal

---

## 🌍 Fontes de Notícias

### Minerador de Notícias Globais

O **Miner** é um agente especializado em coletar notícias de fontes internacionais de alta credibilidade. Essas notícias são **recontextualizadas para o público brasileiro** pelos repórteres digitais.

#### Por que minerar o exterior?

| Área | Origem Comum | Tempo até chegar no Brasil |
|------|--------------|---------------------------|
| **Tecnologia** | EUA (Vale do Silício), China, Japão | 1-3 dias |
| **Geopolítica** | Europa, Oriente Médio, Ásia | Imediato a 24h |
| **Mercados Globais** | NYSE, NASDAQ, Londres, Tóquio | Tempo real |
| **Ciência** | Nature, Science, MIT, NASA | 1-7 dias |
| **Saúde Global** | OMS, FDA, EMA | 1-3 dias |
| **Economia Internacional** | FMI, Banco Mundial, Fed | Tempo real |

#### Portais Globais Minerados

**Tecnologia & Inovação (Tier 1)**
- TechCrunch
- The Verge
- Wired
- Ars Technica
- MIT Technology Review
- Hacker News (Y Combinator)

**Geopolítica & Mundo (Tier 1)**
- Reuters World
- BBC World
- The Guardian International
- Al Jazeera
- Foreign Affairs
- The Economist

**Economia & Mercados (Tier 1)**
- Bloomberg
- Financial Times
- The Wall Street Journal
- Forbes
- Fortune

**Ciência & Saúde (Tier 1)**
- Nature
- Science
- The Lancet
- New England Journal of Medicine
- Scientific American

**Esportes Globais (Tier 2)**
- ESPN International
- BBC Sport
- Sky Sports

#### Configuração do Miner

```yaml
# config/portals_global.yml
global_miner:
  enabled: true
  check_interval_minutes: 30
  
  portals:
    technology:
      - name: "TechCrunch"
        url: "https://techcrunch.com"
        rss: "https://techcrunch.com/feed/"
        categories: ["AI", "startups", "tech"]
        priority: 1
        rate_limit: 10  # requests per minute
        
      - name: "The Verge"
        url: "https://www.theverge.com"
        rss: "https://www.theverge.com/rss/index.xml"
        categories: ["tech", "gadgets", "policy"]
        priority: 1
        rate_limit: 10

    geopolitics:
      - name: "Reuters World"
        url: "https://www.reuters.com/world"
        rss: "https://feeds.reuters.com/Reuters/worldNews"
        categories: ["world", "geopolitics"]
        priority: 1
        rate_limit: 15

    economy:
      - name: "Bloomberg"
        url: "https://www.bloomberg.com"
        rss: "https://feeds.bloomberg.com/markets/news.rss"
        categories: ["markets", "economy", "finance"]
        priority: 1
        rate_limit: 8

  # Tradução e contextualização
  processing:
    language_detection: true
    auto_translate_to: "pt-BR"
    brazil_context_required: true  # Adiciona contexto de impacto no Brasil
    fact_check: true
```

#### Fluxo do Miner

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO DO MINER                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Coleta (RSS/API)                                        │
│     └──▶ TechCrunch, Reuters, Bloomberg...                  │
│                                                             │
│  2. Filtragem por Relevância                                │
│     └──▶ Keywords: "Brazil", "BRICS", "Latin America"      │
│     └──▶ Keywords: "AI", "climate", "economy" (global)     │
│                                                             │
│  3. Tradução Automática                                     │
│     └──▶ en → pt-BR (com cuidado editorial)                │
│                                                             │
│  4. Contextualização para o Brasil                          │
│     └──▶ Adiciona contexto de impacto local                 │
│                                                             │
│  5. Roteamento para Repórter Adequado                       │
│     └──▶ Tecnologia → Enzo Bianchi                          │
│     └──▶ Economia Global → Camila Rocha                     │
│                                                             │
│  6. Reescrita com Voz Editorial                             │
│     └──▶ LLM com prompt específico                          │
│                                                             │
│  7. Publicação com Atribuição de Fonte Original             │
│     └──▶ "Traduzido e adaptado de TechCrunch"               │
│                                                             │
│  ⚠️ REGRA OBRIGATÓRIA:                                     │
│     O Atualiza Brasil NUNCA publica conteúdo em inglês.      │
│     Toda matéria do exterior é traduzida para pt-BR.        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Exemplo de Matéria Global Reescrita

**Original (TechCrunch):**
> "OpenAI announces GPT-5 with enhanced reasoning capabilities"

**Publicada (Enzo Bianchi):**
> **OpenAI anuncia GPT-5 com raciocínio avançado — o que muda para o Brasil**
>
> A OpenAI revelou nesta terça-feira (28) a nova geração do seu modelo de linguagem, o GPT-5. A grande novidade é a capacidade de raciocínio lógico aprimorada, que permite à IA resolver problemas complexos em áreas como medicina, direito e engenharia.
>
> A expectativa é que a novidade impacte diretamente o mercado brasileiro de tecnologia, especialmente startups que desenvolvem soluções baseadas em IA...
>
> Por **Enzo Bianchi**, do Atualiza Brasil
> *Traduzido e adaptado de TechCrunch*

### Portais Nacionais (Piloto MS)

```yaml
# config/portals_br.yml
brazil_sources:
  mato_grosso_do_sul:
    - name: "MS News"
      url: "https://www.msnews.com.br"
      priority: "high"
      
    - name: "MS Todo Dia"
      url: "https://www.mstododia.com.br"
      priority: "high"
      
    - name: "Agência de Notícias MS"
      url: "https://www.agenciadenoticias.ms.gov.br"
      priority: "high"
      type: "government"
      
    - name: "O Estado Online"
      url: "https://www.oestadoonline.com.br"
      priority: "high"
      
    - name: "G1 MS"
      url: "https://g1.globo.com/ms/"
      priority: "medium"
      
    - name: "Correio do Estado"
      url: "https://www.correiodoestado.com.br"
      priority: "high"
```

---

## 🚀 Instalação

### Pré-requisitos

- **Python** 3.11 ou superior
- **Node.js** 20+ e npm
- **Docker** 24+ e Docker Compose
- **Git** 2.30+
- **PostgreSQL** 15+ (via Docker)
- **Redis** 7+ (via Docker)

### Setup Rápido com Docker

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/atualiza-brasil.git
cd atualiza-brasil

# 2. Copie o arquivo de ambiente
cp .env.example .env

# 3. Edite as variáveis de ambiente
nano .env
# Configure: OPENROUTER_API_KEY, DATABASE_URL, etc.

# 4. Inicie os serviços
docker-compose up -d

# 5. Execute as migrations
docker-compose exec backend alembic upgrade head

# 6. Popule o banco com dados iniciais
docker-compose exec backend python scripts/seed.py

# 7. Acesse
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Flower (Celery): http://localhost:5555
```

### Setup Local (Sem Docker)

```bash
# Backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate (Windows)

pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm run dev

# Variáveis de ambiente
cp .env.example .env
# Edite conforme necessário
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# .env

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/atualiza_brasil
POSTGRES_USER=portal_user
POSTGRES_PASSWORD=portal_pass
POSTGRES_DB=atualiza_brasil

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# LLM (OpenRouter)
OPENROUTER_API_KEY=sk-or-v1-...
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Scraping
USER_AGENT=AtualizaBrasil/1.0
RESPECT_ROBOTS_TXT=true
RATE_LIMIT_DEFAULT=10

# Email
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=re_...
ADMIN_EMAIL=admin@atualizabrasil.news

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
GRAFANA_API_KEY=...

# AdSense (produção)
ADSENSE_CLIENT_ID=ca-pub-...
ADSENSE_ENABLED=true

# Site
SITE_URL=https://atualizabrasil.news
SITE_NAME=Atualiza Brasil
DEFAULT_LOCALE=pt-BR
TIMEZONE=America/Sao_Paulo
```

---

## 💻 Uso

### Comandos do Backend

```bash
# Iniciar API
python -m app.main

# Iniciar worker Celery
celery -A app.celery_app worker --loglevel=info

# Iniciar scheduler
celery -A app.celery_app beat --loglevel=info

# Iniciar Flower (monitoramento)
celery -A app.celery_app flower

# Executar testes
pytest tests/ -v

# Verificar lint
flake8 app/
black app/
```

### Comandos do Frontend

```bash
cd frontend

# Desenvolvimento
npm run dev

# Build de produção
npm run build

# Iniciar produção
npm start

# Lint
npm run lint

# Type check
npm run type-check
```

### Operações Comuns

```bash
# Forçar uma varredura manual
docker-compose exec backend python -c "from app.tasks import scan_all; scan_all()"

# Publicar uma matéria manualmente
docker-compose exec backend python -c "from app.tasks import publish; publish()"

# Ver logs em tempo real
docker-compose logs -f backend

# Backup do banco
./scripts/backup.sh

# Verificar saúde do sistema
./scripts/health_check.sh
```

---

## 🌐 Deploy

### Deploy em VPS (Digital Ocean, Hetzner, etc.)

```bash
# 1. Configurar servidor
ssh root@seu-servidor
apt update && apt install -y docker docker-compose nginx certbot python3-pip

# 2. Clonar projeto
git clone https://github.com/seu-usuario/atualiza-brasil.git
cd atualiza-brasil

# 3. Configurar SSL com Let's Encrypt
certbot certonly --standalone -d atualizabrasil.news -d www.atualizabrasil.news

# 4. Configurar nginx (proxy reverso)
cp docker/nginx.conf /etc/nginx/sites-available/atualiza-brasil
ln -s /etc/nginx/sites-available/atualiza-brasil /etc/nginx/sites-enabled/

# 5. Iniciar aplicação
docker-compose -f docker-compose.prod.yml up -d

# 6. Configurar auto-restart
systemctl enable docker
```

### Deploy com GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.4
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /app/atualiza-brasil
            git pull
            docker-compose up -d --build
```

---

## 📊 Monitoramento

### Flower (Celery Dashboard)

Acesse `http://localhost:5555` para ver:
- Tarefas em execução
- Histórico de tarefas
- Workers ativos
- Estatísticas de performance

### Health Check

```bash
# API
curl http://localhost:8000/api/health

# Database
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping
```

### Logs

```bash
# Backend
tail -f logs/atualiza_brasil.log

# Por componente
grep "scanner" logs/atualiza_brasil.log
grep "rewriter" logs/atualiza_brasil.log
grep "publisher" logs/atualiza_brasil.log

# Docker
docker-compose logs -f backend
```

### Métricas Chave

| Métrica | Target | Alerta |
|---------|--------|--------|
| Matérias/dia | 50+ | < 10 |
| Uptime | 99.9% | < 99% |
| Tempo de publicação | < 5 min | > 30 min |
| Taxa de erro | < 1% | > 5% |
| Latência LLM | < 10s | > 30s |

---

## ⚖️ Compliance e Legal

### Lei de Direitos Autorais (Lei 9.610/98)

O Atualiza Brasil opera em conformidade com:

- **Art. 46, I, "a"**: Citação de notícias em outros periódicos, com menção da fonte
- **Art. 47**: Paráfrases livres que não constituam reprodução
- **Art. 8, I**: Fatos não são protegíveis por direito autoral

**Cada matéria publicada:**
1. É **reescrita** (paráfrase) com voz editorial própria do repórter digital
2. **Cita a fonte original** com link direto
3. **Contextualiza** o conteúdo para o público brasileiro
4. **Não reproduz** integralmente o texto original

### LGPD (Lei Geral de Proteção de Dados)

- ✅ Política de Privacidade publicada
- ✅ Termos de Uso publicados
- ✅ Formulário de contato com consentimento
- ✅ Cookies com aviso (Google Analytics + AdSense)
- ✅ Direito de exclusão de dados (e-mail: privacidade@atualizabrasil.news)
- ✅ Logs de acesso (anonimizados após 90 dias)

### Google AdSense

Compatibilidade garantida com:
- ✅ Conteúdo original e de qualidade
- ✅ Páginas estáticas obrigatórias (Sobre, Privacidade, Termos, Contato)
- ✅ Navegação clara e categorias definidas
- ✅ Mobile responsivo
- ✅ Performance otimizada (Core Web Vitals)
- ✅ SSL/HTTPS obrigatório

---

## 🗺️ Roadmap

### ✅ Fase 1: Fundação (Concluído)
- [x] Arquitetura definida
- [x] Equipe de 9 repórteres digitais
- [x] Backend Python + Celery
- [x] Frontend Next.js
- [x] Sistema de compliance legal

### 🔄 Fase 2: Piloto MS (Em andamento)
- [ ] Scanner de portais MS
- [ ] Miner de portais globais
- [ ] Rewriter com LLM
- [ ] 100+ matérias publicadas
- [ ] Aplicação AdSense

### 📅 Fase 3: Validação (Q4 2026)
- [ ] 6 meses de operação contínua
- [ ] Aprovação AdSense
- [ ] Primeiras receitas
- [ ] 1000+ visitantes/dia

### 🚀 Fase 4: Expansão Nacional (2027)
- [ ] Cobertura de todos os estados
- [ ] Repórteres regionais
- [ ] App mobile
- [ ] Newsletter automática

### 🌎 Fase 5: Global (2028+)
- [ ] Versão em inglês
- [ ] Cobertura de outros países da América Latina
- [ ] Parcerias internacionais

---

## 🤝 Contribuição

Este é um projeto proprietário. Para colaborações:

📧 **contato@atualizabrasil.news**

---

## 📄 Licença

Copyright © 2026 Atualiza Brasil. Todos os direitos reservados.

Este software é propriedade exclusiva do Atualiza Brasil. Uso não autorizado é proibido.

---

## 📞 Contato

| Canal | Contato |
|-------|---------|
| **Email Geral** | contato@atualizabrasil.news |
| **Email Admin** | admin@atualizabrasil.news |
| **Privacidade/LGPD** | privacidade@atualizabrasil.news |
| **Imprensa** | imprensa@atualizabrasil.news |
| **Site** | https://atualizabrasil.news |

---

## 🎯 Equipe

- **Founder & Tech Lead**: [Seu nome]
- **AI Engineering**: Atualiza Brasil Team
- **Editorial**: 9 Repórteres Digitais
- **Legal**: Assessoria jurídica especializada

---

**Atualiza Brasil** — *O Brasil sempre atualizado, com a credibilidade de uma equipe editorial completa.*

📰 Tecnologia • 🌍 Geopolítica • 💼 Economia • 🏥 Saúde • 🎓 Educação • 🌾 Agronegócio • ⚽ Esportes • 🎭 Cultura • 🛡️ Segurança
