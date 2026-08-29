# SPEC.md — Atualiza Brasil
## Especificação Técnica Completa

**Versão:** 1.0.0  
**Última atualização:** 2026-08-28  
**Status:** Em desenvolvimento

---

## 1. Visão Geral do Projeto

### 1.1 Descrição
Portal de notícias brasileiro 100% automatizado, com repórteres digitais por área temática. Piloto inicial no estado de Mato Grosso do Sul (MS), com expansão planejada para todo o Brasil.

### 1.2 Objetivos
- Produção automática de conteúdo jornalístico original
- Multiplicação de fontes com atribuição legal (Lei 9.610/98 Art. 46/47)
- 100% automatizado — sem intervenção humana na produção
- Compatibilidade total com Google AdSense
- Escalabilidade para cobertura nacional

### 1.3 Diferencial Competitivo
Cada matéria é assinada por um "repórter digital" com voz editorial própria, creando identidade e confiança. O leitor acompanha seus repórteres favoritos por área de interesse.

---

## 2. Arquitetura do Sistema

### 2.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORQUESTRADOR                             │
│              (Celery + Redis + Schedule)                         │
│   Coordena ciclos, detecta falhas, auto-recupera                │
└────────────────────┬────────────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┬───────────────┬────────────┐
     │               │               │               │            │
     ▼               ▼               ▼               ▼            ▼
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐  ┌─────────┐
│SCANNER  │   │FILTER    │   │REWRITER │   │QUALITY   │  │PUBLISHER│
│(Coleta) │──▶│(Filtro)  │──▶│(LLM)    │──▶│(Checagem)│──▶│(Publica)│
└─────────┘   └─────────┘   └─────────┘   └─────────┘  └─────────┘
     │                                                            │
     ▼                                                            ▼
┌─────────────┐                                          ┌─────────────┐
│PORTAIS FONT │                                          │  FRONTEND   │
│(MS e BR)    │                                          │(Next.js +    │
└─────────────┘                                          │SEO + ADS)   │
                                                         └─────────────┘
```

### 2.2 Stack Tecnológica

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| Backend API | FastAPI | 0.100+ |
| Task Queue | Celery | 5.3+ |
| Broker | Redis | 7+ |
| Database | PostgreSQL | 15+ |
| ORM | SQLAlchemy | 2.0+ |
| LLM | OpenRouter (multi-provider) | - |
| Frontend | Next.js 14 (App Router) | 14+ |
| Hosting | VPS/Dedicado | - |
| CDN | Cloudflare | - |
| Email | Resend/SendGrid | - |
| Monitoring | Sentry + Grafana | - |

---

## 3. Compatibilidade AdSense — Checklist Obrigatório

### 3.1 Páginas Estáticas Obrigatórias

| Página | URL | Descrição |
|--------|-----|-----------|
| **Home** | `/` | Listagem de notícias + ads |
| **Notícia** | `/[categoria]/[slug]` | Matéria completa |
| **Sobre** | `/sobre` | Quem somos, como funciona |
| **Política de Privacidade** | `/privacidade` | LGPD compliance |
| **Termos de Uso** | `/termos` | Regras do portal |
| **Contato** | `/contato` | Formulário + email |
| **Categorias** | `/[categoria]` | Listagem por área |
| **Repórteres** | `/reporters` | Equipe digital |
| **Sitemap** | `/sitemap.xml` | SEO |
| **Robots.txt** | `/robots.txt` | SEO |

### 3.2 Requisitos de Conteúdo AdSense

```
✅ Mínimo de 50-100 matérias publicadas ANTES de aplicar AdSense
✅ Conteúdo original e de qualidade
✅ Categorias bem definidas
✅ Navegação clara entre páginas
✅ Tempo de carregamento < 3 segundos
✅ Mobile-first (responsivo)
✅ SSL (HTTPS) obrigatório
✅ Domínio com +6 meses (recomendado)
✅ Sem conteúdo proibido (pirataria, ódio, etc.)
```

### 3.3 Configuração de Anúncios

| Posição | Formato | Dispositivo |
|---------|---------|-------------|
| Header | 728x90 ou 320x100 | Desktop/Mobile |
| Sidebar (desktop) | 300x250 | Desktop apenas |
| In-content | 300x250 ou 728x90 | Ambos |
| After-content | 300x250 ou 728x90 | Ambos |
| Sticky (mobile) | 320x100 | Mobile apenas |

---

## 4. Automação 100% — Fluxo Completo

### 4.1 Ciclo de Produção Automatizado

```
┌────────────────────────────────────────────────────────────────┐
│                    CICLO CONTÍNUO (24/7)                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  [00:00] ════════════════════════════════════════════ [23:59] │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────┐                                                   │
│  │SCANNER  │───▶ Coleta headlines de TODOS os portais MS       │
│  │ AUTOMÁT │     (a cada 15 minutos)                            │
│  └────┬────┘                                                   │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────┐                                                   │
│  │ FILTER   │───▶ Remove duplicados                            │
│  │         │───▶ Filtra por categoria                          │
│  │         │───▶ Remove conteúdo sensível                      │
│  └────┬────┘                                                   │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────┐                                                   │
│  │REWRITER │───▶ Cada matéria → repórter correto              │
│  │  (LLM)  │     (voz editorial única)                         │
│  └────┬────┘                                                   │
│       │                                                         │
│       ▼                                                         │
│  ┌────────────┐                                                │
│  │  QUALITY   │───▶ Verifica plágio                            │
│  │  CHECK    │───▶ Corrige erros                              │
│  │           │───▶ Adiciona meta tags                          │
│  └────┬───────┘                                                │
│       │                                                         │
│       ▼                                                         │
│  ┌────────────┐                                                │
│  │ PUBLISHER  │───▶ Publica automaticamente                    │
│  │            │───▶ Gera thumbnail                             │
│  │            │───▶ Atualiza sitemap                           │
│  │            │───▶ Notifica indexing                          │
│  └────────────┘                                                │
│       │                                                         │
│       ▼                                                         │
│  ┌────────────┐                                                │
│  │ MONITOR    │───▶ Logs de tudo                              │
│  │            │───▶ Alertas de erro                            │
│  │            │───▶ Métricas de produção                       │
│  └────────────┘                                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 4.2 Tarefas Celery (Auto-Schedule)

```python
TASKS = {
    # Scanner - a cada 15 minutos
    "scan_all_portals": "*/15 * * * *",
    
    # Limpeza - diariamente às 03:00
    "cleanup_old_content": "0 3 * * *",
    
    # Sitemap - diariamente às 04:00
    "update_sitemap": "0 4 * * *",
    
    # Health check - a cada 5 minutos
    "system_health": "*/5 * * * *",
    
    # Métricas - a cada hora
    "report_metrics": "0 * * * *",
    
    # Backup DB - diariamente às 02:00
    "backup_database": "0 2 * * *",
}
```

### 4.3 Auto-Recuperação (Self-Healing)

```python
FAILURE_HANDLERS = {
    "portal_unavailable": "retry_3x_with_backoff",
    "llm_timeout": "use_cache_or_skip",
    "db_connection_error": "restart_connection_pool",
    "rate_limited": "wait_1_hour_and_retry",
    "content_quality_low": "flag_for_review",
    "system_oom": "restart_worker",
}
```

---

## 5. Repórteres Digitais — Perfis Completos

### 5.1 Equipe Editorial

| Repórter | Área | Slug | Tom de Voz |
|----------|------|------|------------|
| **ENZO BIANCHI** | Tecnologia | `enzo.bianchi` | Técnico, futuro, dinâmico |
| **MARCUS TEIXEIRA** | Esportes | `marcus.teixeira` | Empolgado, narrativo, competitivo |
| **RAFAEL DUMAS** | Segurança | `rafael.dumas` | Sério, direto, investigativo |
| **LUCIANA FREITAS** | Política | `luciana.freitas` | Preciso, neutro, informado |
| **MAYA SANTOS** | Saúde | `maya.santos` | Científico, cauteloso, rigoroso |
| **LUCAS NAKAMURA** | Educação | `lucas.nakamura` | Didático, acessível, motivador |
| **BIA FERNANDES** | Agronegócio | `bia.fernandes` | Territorial, profissional, realista |
| **LEON VAZ** | Cultura | `leon.vaz` | Criativo, sensível, engajado |
| **CAMILA ROCHA** | Economia | `camila.rocha` | Analítico, pragmático, direto |

### 5.2 Estrutura do Prompt de Cada Repórter

```yaml
enzo.bianchi:
  role: "technology"
  system_prompt: |
    Você é Enzo Bianchi, repórter tecnológico do Atualiza Brasil.
    
    CARACTERÍSTICAS:
    - Tom: Técnico mas acessível
    - Linguagem: Formal com toques modernos
    - Foco: Impacto tecnológico no cotidiano
    
    REGRAS:
    - Reescreva com SUA voz, nunca copie
    - Cite a fonte original com link
    - Use dados e estatísticas
    - Evite jargões excessivos
    - Max 800 palavras por matéria
    
    ASSINATURA: "Por Enzo Bianchi, do Atualiza Brasil"
```

### 5.3 Cronograma de Publicação

| Horário | Repórter | Área | Prioridade |
|---------|----------|------|------------|
| 05:00 | Enzo Bianchi | Tecnologia | Alta |
| 06:00 | Enzo Bianchi | Tecnologia | Alta |
| 07:00 | Marcus Teixeira | Esportes | Alta |
| 08:00 | Rafael Dumas | Segurança | Alta |
| 09:00 | Luciana Freitas | Política | Alta |
| 10:00 | Maya Santos | Saúde | Média |
| 12:00 | Lucas Nakamura | Educação | Média |
| 14:00 | Bia Fernandes | Agronegócio | Média |
| 16:00 | Leon Vaz | Cultura | Média |
| 18:00 | Camila Rocha | Economia | Alta |
| 20:00 | Marcus Teixeira | Esportes | Alta |
| 22:00 | Enzo Bianchi | Tecnologia | Média |

---

## 6. Portais de Origem (Piloto MS)

### 6.1 Fontes Primárias

| Portal | URL | Status | Prioridade |
|--------|-----|--------|------------|
| MS News | msnews.com.br | ✅ Ativo | Alta |
| MS Todo Dia | mstododia.com.br | ✅ Ativo | Alta |
| G1 MS | g1.globo.com/ms | ⚠️ parcial | Média |
| Agência MS | agenciadenoticias.ms.gov.br | ✅ Ativo | Alta |
| O Estado Online | oestadoonline.com.br | ✅ Ativo | Alta |
| MS Notícias | msnoticias.com.br | ✅ Ativo | Média |
| Correio do Estado | correiodoestado.com.br | ✅ Ativo | Alta |

### 6.2 Configuração de Rate Limiting

```python
PORTAL_CONFIG = {
    "msnews.com.br": {
        "requests_per_minute": 5,
        "respect_robots": True,
        "cache_ttl": 900,  # 15 min
    },
    "agenciadenoticias.ms.gov.br": {
        "requests_per_minute": 10,
        "respect_robots": True,
        "cache_ttl": 600,  # 10 min
    },
    # ...
}
```

---

## 7. Frontend — Requisitos AdSense + SEO

### 7.1 Meta Tags Obrigatórias

```html
<!-- Primary -->
<title>{TÍTULO} | Atualiza Brasil</title>
<meta name="description" content="{RESUMO_150-160}">
<link rel="canonical" href="{URL_CANÔNICA}">

<!-- Open Graph -->
<meta property="og:title" content="{TÍTULO}">
<meta property="og:description" content="{RESUMO}">
<meta property="og:image" content="{THUMBNAIL}">
<meta property="og:url" content="{URL}">
<meta property="og:type" content="article">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TÍTULO}">
<meta name="twitter:description" content="{RESUMO}">
<meta name="twitter:image" content="{THUMBNAIL}">

<!-- Article -->
<meta property="article:author" content="{REPORTER}">
<meta property="article:section" content="{CATEGORIA}">
<meta property="article:published_time" content="{DATA}">
```

### 7.2 Estrutura de Página de Notícia

```
┌─────────────────────────────────────────────────────────┐
│  HEADER (logo + nav + search)                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │            ANÚNCIO HEADER (728x90)              │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [CATEGORIA]                                            │
│  TÍTULO GRANDE DA MATÉRIA                               │
│  Resumo da matéria em 1-2 linhas                       │
│                                                         │
│  Por [REPORTER], do Atualiza Brasil                    │
│  [DATA] • [TEMPO DE LEITURA]                           │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐  ┌──────────────────┐    │
│  │                         │  │ SIDEBAR          │    │
│  │   CONTEÚDO PRINCIPAL    │  │                  │    │
│  │                         │  │ ┌──────────────┐ │    │
│  │   [Parágrafos...]       │  │ │ ANÚNCIO 300x │ │    │
│  │                         │  │ └──────────────┘ │    │
│  │                         │  │                  │    │
│  │   [ANÚNCIO IN-CONTENT] │  │ ┌──────────────┐ │    │
│  │                         │  │ │ ANÚNCIO 300x │ │    │
│  │   [Mais parágrafos...]  │  │ └──────────────┘ │    │
│  │                         │  │                  │    │
│  │                         │  │ + Links related  │    │
│  └─────────────────────────┘  └──────────────────┘    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  TAGS: [tag1] [tag2] [tag3]                            │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            ANÚNCIO FOOTER (728x90)              │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  FOOTER (links, políticas, copyright)                   │
└─────────────────────────────────────────────────────────┘
```

### 7.3 Performance (Core Web Vitals)

| Métrica | Target | Crítico |
|---------|--------|---------|
| LCP | < 2.5s | > 4.0s |
| FID | < 100ms | > 300ms |
| CLS | < 0.1 | > 0.25 |
| TTFB | < 800ms | > 1800ms |

### 7.4 Otimizações

```javascript
// Lazy load de imagens
<img loading="lazy" src="..." />

// Preload de recursos críticos
<link rel="preload" href="..." />

// Compression
assets: { compress: true }

// CDN para assets estáticos
cdn: "cloudflare"

// Cache headers
cache: {
  static: "1y",
  dynamic: "1h",
}
```

---

## 8. Compliance Legal e LGPD

### 8.1 Política de Privacidade (Obrigatória AdSense)

```markdown
# Política de Privacidade — Atualiza Brasil

Última atualização: [DATA]

## 1. Coleta de Dados
- Cookies de navegação (Google Analytics)
- Dados de formulário de contato
- Endereço IP (logs de acesso)

## 2. Uso dos Dados
- Melhorar experiência do usuário
- Análise de audiência (Google Analytics)
- Anúncios personalizados (Google AdSense)

## 3. Seus Direitos (LGPD)
- Solicitar acesso aos seus dados
- Solicitar correção de dados
- Solicitar exclusão de dados
- Contato: privacidade@atualizabrasil.news

## 4. Cookies de Terceiros
- Google Analytics
- Google AdSense
- Redes sociais (compartilhamento)
```

### 8.2 Termos de Uso

```markdown
# Termos de Uso — Atualiza Brasil

## 1. Objeto
Plataforma de notícias automatizada que agrega e reescreve 
conteúdo de fontes públicas.

## 2. Conteúdo
- Matérias assinadas por repórteres digitais
- Fontes sempre citadas conforme Lei 9.610/98 Art. 46/47
- Opiniões dos repórteres digitais não representam 
  posicionamento editorial do portal

## 3. Propriedade Intelectual
Todo conteúdo original é propriedade do Atualiza Brasil.
Texto original das fontes pertence aos respectivos veículos.

## 4. Conteúdo Gerado por Terceiros
Comentários e compartilhamentos são responsabilidade dos usuários.

## 5. Isenção de Responsabilidade
Não nos responsabilizamos por decisões tomadas com base 
nas notícias publicadas.
```

### 8.3 Disclaimer de Automação

```markdown
## Isenção de Responsabilidade — Conteúdo Automatizado

O Atualiza Brasil utiliza inteligência artificial para 
produzir conteúdo jornalístico de forma automatizada.

As opiniões expressas nas matérias são dos nossos repórteres 
digitais e não constituem aconselhamento profissional, 
médico, jurídico ou financeiro.

Sempre consulte fontes oficiais e profissionais especializados 
antes de tomar decisões.
```

---

## 9. Monitoramento e Alertas

### 9.1 Métricas de Saúde

```yaml
health_checks:
  - name: "API Response"
    endpoint: "/api/health"
    threshold: 200ms
  
  - name: "Database"
    check: "SELECT 1"
    threshold: 100ms
  
  - name: "LLM Availability"
    check: "openrouter_ping"
    threshold: 5000ms
  
  - name: "Portals Status"
    check: "scan_sample_portal"
    threshold: 10000ms
  
  - name: "Publication Rate"
    check: "articles_last_hour"
    threshold: 5 articles
```

### 9.2 Alertas

| Tipo | Severidade | Ação |
|------|------------|------|
| Scanner falhou | Warning | Retry automático |
| LLM indisponível | Critical | Usar cache + notificar |
| DB offline | Critical | Restart + notificar |
| Publicação parada | Critical | Investigar + notificar |
| Erro AdSense | Warning | Pausar anúncios + notificar |

### 9.3 Dashboard de Monitoramento

```
┌─────────────────────────────────────────────────────────┐
│  ATUALIZA BRASIL — DASHBOARD DE PRODUÇÃO              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ 247      │  │ 1.2K     │  │ 98.5%    │           │
│  │Matérias  │  │Visitantes│  │Uptime    │           │
│  │Hoje      │  │Mês       │  │30 dias   │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│                                                         │
│  Producao por Repórter (24h)                           │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Enzo ████████████████████░░░░░░ 45%             │  │
│  │ Marcus ████████████░░░░░░░░░░░░ 28%             │  │
│  │ Rafael ████████░░░░░░░░░░░░░░░ 18%             │  │
│  │ Outros ████░░░░░░░░░░░░░░░░░░░ 9%              │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Status dos Agentes                                    │
│  ┌─────────────────────────────────────────────────┐  │
│  │ ✅ Scanner    │ 🟡 Rewriter  │ ✅ Publisher     │  │
│  │ ✅ Filter     │ ✅ Quality   │ ✅ Monitor       │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Ultimas Publicacoes                                   │
│  ┌─────────────────────────────────────────────────┐  │
│  │ 14:32 │ Tecnologia │ Enzo Bianchi │ ✅         │  │
│  │ 14:15 │ Esportes   │ Marcus       │ ✅         │  │
│  │ 13:58 │ Seguranca  │ Rafael       │ ✅         │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 10. Checklist de Lançamento AdSense

### Fase 1 — Pré-Lançamento
- [ ] 100+ matérias publicadas
- [ ] Todas as páginas estáticas criadas
- [ ] SSL configurado
- [ ] Mobile responsivo
- [ ] Performance < 3s
- [ ] Privacy policy online
- [ ] Terms of service online
- [ ] Contato funcional
- [ ] About page completa

### Fase 2 — Validação
- [ ] 6 meses de domínio (recomendado)
- [ ] 0 conteúdo proibido
- [ ] 0 plágio (todas fontes citadas)
- [ ] Navegação funcionando
- [ ] Sitemap.xml gerado
- [ ] Robots.txt configurado

### Fase 3 — Aplicação
- [ ] Criar conta AdSense
- [ ] Adicionar código aosite
- [ ] Aguardar verificação (~1-2 semanas)
- [ ] Implementar anúncios

### Fase 4 — Pós-Aprovação
- [ ] Monitorar CTR (>1% ideal)
- [ ] Ajustar posicionamento
- [ ] Testar formatos
- [ ] Compliance contínuo

---

## 11. Roadmap de Expansão

### Fase 1: Piloto MS (Atual)
- [x] Arquitetura definida
- [ ] Scanner funcionando
- [ ] Rewriter com LLM
- [ ] Frontend básico
- [ ] 100+ matérias

### Fase 2: Expansão MS
- [ ] Mais fontes locais
- [ ] Todas as categorias ativas
- [ ] AdSense aprovado
- [ ] Monetização inicial

### Fase 3: Expansão Nacional
- [ ] Fontes de outros estados
- [ ] Repórteres por região
- [ ] Escalabilidade

### Fase 4: Brasil Completo
- [ ] Cobertura nacional
- [ ] Multi-idioma (futuro)
- [ ] App mobile

---

## 12. Contatos e Configurações

| Serviço | Configuração |
|---------|-------------|
| **Domínio** | atualizabrasil.news |
| **Email** | admin@atualizabrasil.news |
| **Sentry** | DSN em produção |
| **Cloudflare** | Zona configurada |
| **PostgreSQL** | localhost:5432 |
| **Redis** | localhost:6379 |
| **LLM** | OpenRouter API |

---

## 13. Glossário

| Termo | Definição |
|-------|-----------|
| **Scanner** | Agente que coleta headlines dos portais fonte |
| **Rewriter** | Agente que reescreve com a voz do repósito |
| **Publisher** | Agente que publica no site |
| **Repórter digital** | Pseudônimo com voz editorial própria |
| **Art. 46/47 LDA** | Lei de Direitos Autorais — citação e paráfrase |
| **AdSense** | Plataforma de anúncios do Google |
| **LLM** | Large Language Model (GPT, Claude, etc.) |
| **Celery** | Fila de tarefas assíncronas |

---

*Documento atualizado em: 2026-08-28*  
*Próxima revisão: 2026-09-28*
