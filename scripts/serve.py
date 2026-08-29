"""
Servidor HTTP Simples — Atualiza Brasil
Mostra as notícias coletadas em localhost sem precisar de DB.
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Load .env
env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Adiciona path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Articles cache
ARTICLES_CACHE = []
CACHE_TIME = None
CACHE_DURATION = 300  # 5 minutos

CATEGORIES = {
    'tech': {'icon': '💻', 'color': '#3b82f6', 'name': 'Tecnologia'},
    'sports': {'icon': '⚽', 'color': '#22c55e', 'name': 'Esportes'},
    'politics': {'icon': '🏛️', 'color': '#ef4444', 'name': 'Política'},
    'economy': {'icon': '📈', 'color': '#f59e0b', 'name': 'Economia'},
    'health': {'icon': '🏥', 'color': '#ec4899', 'name': 'Saúde'},
    'security': {'icon': '🔒', 'color': '#6366f1', 'name': 'Segurança'},
    'science': {'icon': '🔬', 'color': '#8b5cf6', 'name': 'Ciência'},
    'entertainment': {'icon': '🎬', 'color': '#f97316', 'name': 'Entretenimento'},
    'general': {'icon': '📰', 'color': '#64748b', 'name': 'Geral'},
}

REPORTERS = {
    'enzo.bianchi': {'name': 'Enzo Bianchi', 'specialty': 'Tecnologia'},
    'marcus.teixeira': {'name': 'Marcus Teixeira', 'specialty': 'Esportes'},
    'luciana.freitas': {'name': 'Luciana Freitas', 'specialty': 'Política'},
    'bia.fernandes': {'name': 'Bia Fernandes', 'specialty': 'Agricultura'},
    'rafael.dumas': {'name': 'Rafael Dumas', 'specialty': 'Segurança'},
    'maya.santos': {'name': 'Maya Santos', 'specialty': 'Saúde'},
    'carlos.nunes': {'name': 'Carlos Nunes', 'specialty': 'Economia'},
    'fernanda.lima': {'name': 'Fernanda Lima', 'specialty': 'Ciência'},
    'pedro.mendes': {'name': 'Pedro Mendes', 'specialty': 'Entretenimento'},
}


def get_category_info(cat):
    return CATEGORIES.get(cat, CATEGORIES['general'])


def get_reporter_info(slug):
    return REPORTERS.get(slug, {'name': slug, 'specialty': 'Geral'})


def fetch_articles():
    """Busca artigos do scanner."""
    global ARTICLES_CACHE, CACHE_TIME
    
    now = datetime.now()
    if CACHE_TIME and (now - CACHE_TIME).seconds < CACHE_DURATION and ARTICLES_CACHE:
        return ARTICLES_CACHE
    
    try:
        from app.scanner import RealPortalScanner
        scanner = RealPortalScanner()
        results = scanner.scan_all()
        ARTICLES_CACHE = results.get('articles', [])
        CACHE_TIME = now
        return ARTICLES_CACHE
    except Exception as e:
        print(f"Erro scanner: {e}")
        return []


def generate_html(articles):
    """Gera HTML completo da página."""
    
    reporter_html = ""
    for slug, info in REPORTERS.items():
        reporter_html += f"""
        <div class="reporter-card">
            <div class="reporter-name">{info['name']}</div>
            <div class="reporter-specialty">{info['specialty']}</div>
        </div>
        """
    
    articles_html = ""
    for art in articles[:30]:  # Limita a 30
        cat_info = get_category_info(art.get('category', 'general'))
        reporter_info = get_reporter_info(art.get('reporter_slug', ''))
        
        articles_html += f"""
        <article class="news-card">
            <div class="news-header">
                <span class="category-badge" style="background: {cat_info['color']}">
                    {cat_info['icon']} {cat_info['name']}
                </span>
                <span class="news-source">{art.get('source', 'Portal')}</span>
            </div>
            <h3 class="news-title">{art.get('title', 'Sem título')}</h3>
            <p class="news-summary">{art.get('summary', '')[:200]}...</p>
            <div class="news-footer">
                <span class="reporter-badge">✍️ {reporter_info['name']}</span>
                <span class="news-time">{art.get('scraped_at', '')[:10] if art.get('scraped_at') else ''}</span>
            </div>
        </article>
        """
    
    if not articles_html:
        articles_html = """
        <div class="empty-state">
            <p>Nenhuma notícia encontrada.</p>
            <p><a href="/?refresh=1">Atualizar</a></p>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atualiza Brasil — Portal de Notícias</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header p {{ opacity: 0.9; }}
        
        .stats {{
            background: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: center;
            gap: 3rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 2rem; font-weight: bold; color: #1e40af; }}
        .stat-label {{ font-size: 0.875rem; color: #64748b; }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #1e40af;
        }}
        
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        
        .news-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .news-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}
        
        .news-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .category-badge {{
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .news-source {{
            font-size: 0.75rem;
            color: #64748b;
        }}
        
        .news-title {{
            font-size: 1.125rem;
            margin-bottom: 0.75rem;
            color: #0f172a;
        }}
        
        .news-summary {{
            font-size: 0.875rem;
            color: #475569;
            margin-bottom: 1rem;
        }}
        
        .news-footer {{
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: #64748b;
        }}
        
        .reporter-badge {{
            background: #f1f5f9;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }}
        
        .reporters-section {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .reporters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
        }}
        
        .reporter-card {{
            background: #f8fafc;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        .reporter-name {{
            font-weight: 600;
            color: #1e40af;
        }}
        
        .reporter-specialty {{
            font-size: 0.75rem;
            color: #64748b;
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-size: 0.875rem;
        }}
        
        .refresh-btn {{
            display: inline-block;
            background: #1e40af;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            margin-top: 1rem;
        }}
        
        .refresh-btn:hover {{
            background: #1e3a8a;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 3rem;
            background: white;
            border-radius: 12px;
        }}
        
        @media (max-width: 768px) {{
            .news-grid {{ grid-template-columns: 1fr; }}
            .stats {{ flex-wrap: wrap; gap: 1rem; }}
            .header h1 {{ font-size: 1.75rem; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>📰 Atualiza Brasil</h1>
        <p>Portal de notícias automatizado com 9 repórteres de IA</p>
    </header>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value">{len(articles)}</div>
            <div class="stat-label">Notícias</div>
        </div>
        <div class="stat">
            <div class="stat-value">9</div>
            <div class="stat-label">Repórteres</div>
        </div>
        <div class="stat">
            <div class="stat-value">4</div>
            <div class="stat-label">Portais MS</div>
        </div>
        <div class="stat">
            <div class="stat-value">25+</div>
            <div class="stat-label">Fontes Globais</div>
        </div>
    </div>
    
    <div class="container">
        <section class="reporters-section">
            <h2 class="section-title">✍️ Nossa Equipe</h2>
            <div class="reporters-grid">
                {reporter_html}
            </div>
        </section>
        
        <h2 class="section-title">📋 Últimas Notícias</h2>
        <div class="news-grid">
            {articles_html}
        </div>
        
        <div style="text-align: center;">
            <a href="/?refresh=1" class="refresh-btn">🔄 Atualizar Notícias</a>
        </div>
    </div>
    
    <footer class="footer">
        <p>Atualiza Brasil — {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <p>Powered by AI • Groq • Python</p>
    </footer>
</body>
</html>"""
    
    return html


class Handler(BaseHTTPRequestHandler):
    """Handler para requisições HTTP."""
    
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            articles = fetch_articles()
            html = generate_html(articles)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/api/news':
            articles = fetch_articles()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'articles': articles,
                'total': len(articles),
                'timestamp': datetime.now().isoformat()
            }).encode('utf-8'))
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'healthy',
                'articles_cached': len(ARTICLES_CACHE),
                'timestamp': datetime.now().isoformat()
            }).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


def main():
    port = 8080
    server = HTTPServer(('0.0.0.0', port), Handler)
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           ATUALIZA BRASIL — SERVIDOR LOCAL               ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  🌐 Acesse: http://localhost:{port}                       ║
║  📱 Também: http://127.0.0.1:{port}                      ║
║                                                          ║
║  Endpoints:                                              ║
║    /          → Página principal (HTML)                  ║
║    /api/news  → API JSON                               ║
║    /health    → Status do servidor                     ║
║                                                          ║
║  Pressione Ctrl+C para parar                            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⛔ Servidor parado")
        server.shutdown()


if __name__ == '__main__':
    main()
