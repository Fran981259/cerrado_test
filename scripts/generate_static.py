"""
Gerador de HTML Estático — Atualiza Brasil
Design moderno estilo portal de notícias (tipo Campo Grande News).
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

CATEGORIES = {
    'tech': {'icon': '💻', 'color': '#e74c3c', 'name': 'Tecnologia'},
    'sports': {'icon': '⚽', 'color': '#27ae60', 'name': 'Esportes'},
    'politics': {'icon': '🏛️', 'color': '#2980b9', 'name': 'Política'},
    'economy': {'icon': '📈', 'color': '#f39c12', 'name': 'Economia'},
    'health': {'icon': '🏥', 'color': '#e91e63', 'name': 'Saúde'},
    'security': {'icon': '🔒', 'color': '#8e44ad', 'name': 'Segurança'},
    'science': {'icon': '🔬', 'color': '#00BCD4', 'name': 'Ciência'},
    'entertainment': {'icon': '🎬', 'color': '#FF5722', 'name': 'Entretenimento'},
    'general': {'icon': '📰', 'color': '#607d8b', 'name': 'Geral'},
    'agriculture': {'icon': '🌾', 'color': '#4CAF50', 'name': 'Agricultura'},
}

REPORTERS = {
    'enzo.bianchi': {'name': 'Enzo Bianchi', 'specialty': 'Tecnologia'},
    'marcus.teixeira': {'name': 'Marcus Teixeira', 'specialty': 'Esportes'},
    'luciana.freitas': {'name': 'Luciana Freitas', 'specialty': 'Política'},
    'bia.fernandes': {'name': 'Bia Fernandes', 'specialty': 'Agricultura'},
    'rafael.dumas': {'name': 'Rafael Dumas', 'specialty': 'Segurança'},
    'maya.santos': {'name': 'Maya Santos', 'specialty': 'Saúde'},
    'carlos.nunes': {'name': 'Carlos Nunes', 'specialty': 'Economia'},
    'fernanda.lima': {'name': 'Fernanda Lima', 'specialty': 'Educação'},
    'pedro.mendes': {'name': 'Pedro Mendes', 'specialty': 'Entretenimento'},
}

PATTERN_IMAGES = {
    'tech': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=400&fit=crop',
    'sports': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=600&h=400&fit=crop',
    'politics': 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=600&h=400&fit=crop',
    'economy': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&h=400&fit=crop',
    'health': 'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=600&h=400&fit=crop',
    'security': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&h=400&fit=crop',
    'science': 'https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=600&h=400&fit=crop',
    'entertainment': 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600&h=400&fit=crop',
    'agriculture': 'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=600&h=400&fit=crop',
    'general': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&h=400&fit=crop',
}


def fetch_articles():
    try:
        from app.scanner import RealPortalScanner
        scanner = RealPortalScanner()
        results = scanner.scan_all()
        return results.get('articles', [])
    except Exception as e:
        print(f"Erro scanner: {e}")
        return []


def generate_html(articles):
    featured = articles[0] if articles else None
    secondary = articles[1:5] if len(articles) > 1 else []
    remaining = articles[5:] if len(articles) > 5 else []
    
    def get_image(article):
        cat = article.get('category', 'general')
        return PATTERN_IMAGES.get(cat, PATTERN_IMAGES['general'])
    
    def format_date(d):
        if not d:
            return ''
        try:
            return datetime.fromisoformat(d).strftime('%d/%m/%Y %Hh%M')
        except:
            return d[:10]
    
    def news_card(article, size='normal'):
        cat = article.get('category', 'general')
        cat_info = CATEGORIES.get(cat, CATEGORIES['general'])
        reporter = REPORTERS.get(article.get('reporter_slug', ''), {'name': 'Redação'})
        
        img_class = 'card-img' if size == 'large' else 'card-img-sm'
        title_size = 'card-title-lg' if size == 'large' else 'card-title'
        
        return f'''
        <article class="news-card {size}">
            <a href="{article.get('url', '#')}" target="_blank" class="card-link">
                <div class="card-image">
                    <img src="{get_image(article)}" alt="{article.get('title', '')}" loading="lazy">
                    <span class="card-category" style="background:{cat_info['color']}">
                        {cat_info['icon']} {cat_info['name']}
                    </span>
                </div>
                <div class="card-body">
                    <h3 class="{title_size}">{article.get('title', '')}</h3>
                    <p class="card-summary">{article.get('summary', '')[:120]}...</p>
                    <div class="card-meta">
                        <span class="meta-reporter">✍️ {reporter['name']}</span>
                        <span class="meta-date">{format_date(article.get('scraped_at', ''))}</span>
                    </div>
                </div>
            </a>
        </article>'''
    
    def compact_card(article):
        cat = article.get('category', 'general')
        cat_info = CATEGORIES.get(cat, CATEGORIES['general'])
        reporter = REPORTERS.get(article.get('reporter_slug', ''), {'name': 'Redação'})
        
        return f'''
        <article class="compact-card">
            <a href="{article.get('url', '#')}" target="_blank" class="compact-link">
                <img src="{get_image(article)}" alt="" class="compact-img">
                <div class="compact-content">
                    <span class="compact-cat" style="color:{cat_info['color']}">{cat_info['icon']} {cat_info['name']}</span>
                    <h4 class="compact-title">{article.get('title', '')}</h4>
                    <span class="compact-meta">{reporter['name']} • {format_date(article.get('scraped_at', ''))}</span>
                </div>
            </a>
        </article>'''
    
    def sidebar_card(article):
        cat = article.get('category', 'general')
        cat_info = CATEGORIES.get(cat, CATEGORIES['general'])
        reporter = REPORTERS.get(article.get('reporter_slug', ''), {'name': 'Redação'})
        
        return f'''
        <article class="sidebar-card">
            <a href="{article.get('url', '#')}" target="_blank" class="sidebar-link">
                <span class="sidebar-cat" style="color:{cat_info['color']}">{cat_info['icon']} {cat_info['name']}</span>
                <h4 class="sidebar-title">{article.get('title', '')}</h4>
                <span class="sidebar-meta">{reporter['name']} • {format_date(article.get('scraped_at', ''))}</span>
            </a>
        </article>'''
    
    featured_html = news_card(featured, 'hero') if featured else ''
    
    secondary_html = ''
    for art in secondary:
        secondary_html += news_card(art, 'medium')
    
    remaining_html = ''
    for art in remaining:
        remaining_html += compact_card(art)
    
    sidebar_html = ''
    for art in articles[:6]:
        sidebar_html += sidebar_card(art)
    
    category_filters = ''
    for cat_id, cat_info in CATEGORIES.items():
        count = sum(1 for a in articles if a.get('category') == cat_id)
        if count > 0:
            category_filters += f'''<button class="cat-btn" data-category="{cat_id}" style="--cat-color:{cat_info['color']}">
                {cat_info['icon']} {cat_info['name']} <span class="cat-count">{count}</span>
            </button>'''
    
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atualiza Brasil — Últimas Notícias de Mato Grosso do Sul</title>
    <meta name="description" content="Portal de notícias de Mato Grosso do Sul. Informações atualizadas 24 horas sobre política, esportes, segurança, economia e mais.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        :root {{
            --primary: #e63946;
            --primary-dark: #c1121f;
            --dark: #1a1a2e;
            --dark-2: #16213e;
            --gray: #6c757d;
            --light: #f8f9fa;
            --white: #ffffff;
            --shadow: 0 2px 20px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 40px rgba(0,0,0,0.15);
        }}
        
        body {{
            font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--light);
            color: #333;
            line-height: 1.6;
        }}
        
        a {{ text-decoration: none; color: inherit; }}
        
        /* HEADER */
        .header-top {{
            background: var(--dark);
            color: white;
            padding: 0.5rem 0;
            font-size: 0.8rem;
        }}
        
        .header-top .container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header-main {{
            background: var(--white);
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        
        .header-main .container {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 0;
        }}
        
        .logo {{
            font-size: 2rem;
            font-weight: 900;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .logo span {{
            color: var(--dark);
        }}
        
        .nav-menu {{
            display: flex;
            gap: 0.25rem;
        }}
        
        .nav-link {{
            padding: 0.5rem 1rem;
            font-weight: 600;
            font-size: 0.85rem;
            border-radius: 4px;
            transition: all 0.2s;
        }}
        
        .nav-link:hover {{
            background: var(--primary);
            color: white;
        }}
        
        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 1.5rem;
        }}
        
        /* TICKER */
        .ticker {{
            background: var(--primary);
            color: white;
            padding: 0.5rem 0;
            overflow: hidden;
        }}
        
        .ticker-content {{
            display: flex;
            animation: ticker 30s linear infinite;
        }}
        
        .ticker-item {{
            white-space: nowrap;
            padding: 0 2rem;
            font-weight: 600;
        }}
        
        @keyframes ticker {{
            0% {{ transform: translateX(0); }}
            100% {{ transform: translateX(-50%); }}
        }}
        
        /* HERO SECTION */
        .hero-section {{
            padding: 2rem 0;
        }}
        
        .hero-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 1.5rem;
        }}
        
        @media (max-width: 900px) {{
            .hero-grid {{ grid-template-columns: 1fr; }}
        }}
        
        /* NEWS CARDS */
        .news-card {{
            background: var(--white);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow);
            transition: all 0.3s;
        }}
        
        .news-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }}
        
        .news-card.hero {{
            height: 100%;
        }}
        
        .news-card.medium .card-image img {{
            height: 200px;
        }}
        
        .card-link {{
            display: block;
            height: 100%;
        }}
        
        .card-image {{
            position: relative;
            overflow: hidden;
        }}
        
        .news-card.hero .card-image img {{
            height: 400px;
            transition: transform 0.5s;
        }}
        
        .news-card:hover .card-image img {{
            transform: scale(1.05);
        }}
        
        .card-category {{
            position: absolute;
            top: 1rem;
            left: 1rem;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        
        .card-body {{
            padding: 1.25rem;
        }}
        
        .card-title-lg {{
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--dark);
            margin-bottom: 0.75rem;
            line-height: 1.3;
        }}
        
        .card-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }}
        
        .card-summary {{
            color: var(--gray);
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}
        
        .card-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--gray);
            padding-top: 0.75rem;
            border-top: 1px solid #eee;
        }}
        
        .meta-reporter {{
            font-weight: 600;
            color: var(--primary);
        }}
        
        /* SECONDARY GRID */
        .secondary-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }}
        
        /* MAIN CONTENT */
        .main-content {{
            padding: 2rem 0;
        }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 2rem;
        }}
        
        @media (max-width: 1000px) {{
            .content-grid {{ grid-template-columns: 1fr; }}
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid var(--primary);
        }}
        
        .section-title {{
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--dark);
        }}
        
        .section-title::before {{
            content: '';
            display: inline-block;
            width: 6px;
            height: 24px;
            background: var(--primary);
            margin-right: 0.75rem;
            border-radius: 3px;
        }}
        
        /* COMPACT CARDS */
        .compact-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.25rem;
        }}
        
        .compact-card {{
            background: var(--white);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: var(--shadow);
            transition: all 0.3s;
        }}
        
        .compact-card:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg);
        }}
        
        .compact-link {{
            display: flex;
            gap: 1rem;
            padding: 1rem;
        }}
        
        .compact-img {{
            width: 100px;
            height: 80px;
            object-fit: cover;
            border-radius: 8px;
            flex-shrink: 0;
        }}
        
        .compact-content {{
            flex: 1;
            min-width: 0;
        }}
        
        .compact-cat {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        
        .compact-title {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--dark);
            margin: 0.25rem 0;
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .compact-meta {{
            font-size: 0.75rem;
            color: var(--gray);
        }}
        
        /* SIDEBAR */
        .sidebar {{
            position: sticky;
            top: 100px;
        }}
        
        .sidebar-card {{
            background: var(--white);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow);
            border-left: 4px solid var(--primary);
            transition: all 0.2s;
        }}
        
        .sidebar-card:hover {{
            transform: translateX(4px);
        }}
        
        .sidebar-link {{
            display: block;
        }}
        
        .sidebar-cat {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        
        .sidebar-title {{
            font-size: 1rem;
            font-weight: 700;
            color: var(--dark);
            margin: 0.25rem 0 0.5rem;
            line-height: 1.3;
        }}
        
        .sidebar-meta {{
            font-size: 0.75rem;
            color: var(--gray);
        }}
        
        /* CATEGORY FILTERS */
        .cat-filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 2rem;
            padding: 1rem;
            background: var(--white);
            border-radius: 10px;
            box-shadow: var(--shadow);
        }}
        
        .cat-btn {{
            padding: 0.5rem 1rem;
            border: 2px solid var(--cat-color, var(--gray));
            background: transparent;
            color: var(--cat-color, var(--gray));
            border-radius: 25px;
            font-weight: 600;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .cat-btn:hover, .cat-btn.active {{
            background: var(--cat-color, var(--gray));
            color: white;
        }}
        
        .cat-count {{
            background: rgba(255,255,255,0.3);
            padding: 0.1rem 0.4rem;
            border-radius: 10px;
            font-size: 0.7rem;
        }}
        
        /* FOOTER */
        .footer {{
            background: var(--dark);
            color: white;
            padding: 3rem 0 1rem;
            margin-top: 3rem;
        }}
        
        .footer-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .footer-col h4 {{
            color: var(--primary);
            margin-bottom: 1rem;
            font-size: 1rem;
        }}
        
        .footer-col ul {{
            list-style: none;
        }}
        
        .footer-col li {{
            margin-bottom: 0.5rem;
        }}
        
        .footer-col a {{
            color: #aaa;
            font-size: 0.9rem;
            transition: color 0.2s;
        }}
        
        .footer-col a:hover {{
            color: var(--primary);
        }}
        
        .footer-bottom {{
            text-align: center;
            padding-top: 2rem;
            border-top: 1px solid #333;
            color: #666;
            font-size: 0.85rem;
        }}
        
        /* MOBILE MENU */
        .mobile-toggle {{
            display: none;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
        }}
        
        @media (max-width: 768px) {{
            .nav-menu {{ display: none; }}
            .mobile-toggle {{ display: block; }}
            .secondary-grid {{ grid-template-columns: 1fr; }}
            .compact-grid {{ grid-template-columns: 1fr; }}
            .logo {{ font-size: 1.5rem; }}
        }}
        
        /* BREAKING BADGE */
        .breaking-badge {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: var(--primary);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 700;
            animation: pulse 1s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        /* STATS BAR */
        .stats-bar {{
            background: var(--dark-2);
            padding: 1rem 0;
            margin-bottom: 2rem;
        }}
        
        .stats-grid {{
            display: flex;
            justify-content: center;
            gap: 3rem;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            text-align: center;
            color: white;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 900;
            color: var(--primary);
        }}
        
        .stat-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            opacity: 0.8;
        }}
        
        .news-card[style*="display: none"] {{
            display: none !important;
        }}
    </style>
</head>
<body>
    <header class="header-top">
        <div class="container">
            <span>📍 Mato Grosso do Sul</span>
            <span>{datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        </div>
    </header>
    
    <div class="header-main">
        <div class="container">
            <a href="/" class="logo">📰 Atualiza <span>Brasil</span></a>
            <nav class="nav-menu">
                <a href="#" class="nav-link">Início</a>
                <a href="#" class="nav-link">Política</a>
                <a href="#" class="nav-link">Esportes</a>
                <a href="#" class="nav-link">Economia</a>
                <a href="#" class="nav-link">Polícia</a>
                <a href="#" class="nav-link">Cidades</a>
            </nav>
            <button class="mobile-toggle">☰</button>
        </div>
    </div>
    
    <div class="ticker">
        <div class="ticker-content">
            {''.join([f'<span class="ticker-item">🔥 {a.get("title", "")[:80]}</span>' for a in articles[:10] for _ in (None, None)])}
        </div>
    </div>
    
    <div class="stats-bar">
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">{len(articles)}</div>
                <div class="stat-label">Notícias</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">9</div>
                <div class="stat-label">Repórteres</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">4</div>
                <div class="stat-label">Fontes</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">24/7</div>
                <div class="stat-label">Atualização</div>
            </div>
        </div>
    </div>
    
    <section class="hero-section">
        <div class="container">
            <div class="hero-grid">
                <div class="hero-main">
                    {featured_html}
                </div>
                <div class="hero-secondary">
                    <div class="secondary-grid">
                        {secondary_html}
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <main class="main-content">
        <div class="container">
            <div class="cat-filters">
                <button class="cat-btn active" data-category="all">
                    📋 Todas <span class="cat-count">{len(articles)}</span>
                </button>
                {category_filters}
            </div>
            
            <div class="content-grid">
                <div class="news-list">
                    <div class="section-header">
                        <h2 class="section-title">Últimas Notícias</h2>
                    </div>
                    
                    <div class="compact-grid" id="news-grid">
                        {remaining_html}
                    </div>
                </div>
                
                <aside class="sidebar">
                    <div class="section-header">
                        <h2 class="section-title">Mais Lidas</h2>
                    </div>
                    {sidebar_html}
                </aside>
            </div>
        </div>
    </main>
    
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-col">
                    <h4>Sobre</h4>
                    <ul>
                        <li><a href="#">Quem Somos</a></li>
                        <li><a href="#">Nossa Equipe</a></li>
                        <li><a href="#">Contato</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Categorias</h4>
                    <ul>
                        <li><a href="#">Política</a></li>
                        <li><a href="#">Esportes</a></li>
                        <li><a href="#">Economia</a></li>
                        <li><a href="#">Segurança</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Legal</h4>
                    <ul>
                        <li><a href="#">Termos de Uso</a></li>
                        <li><a href="#">Política de Privacidade</a></li>
                        <li><a href="#">Disclaimer</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Contato</h4>
                    <ul>
                        <li><a href="#">contato@atualizabrasil.news</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© {datetime.now().year} Atualiza Brasil — Portal automatizado com IA</p>
                <p>Powered by Groq AI • Python • BeautifulSoup</p>
            </div>
        </div>
    </footer>
    
    <script>
        // Category filter
        const catBtns = document.querySelectorAll('.cat-btn');
        const newsCards = document.querySelectorAll('.news-card, .compact-card');
        const compactCards = document.querySelectorAll('.compact-card');
        const sidebarCards = document.querySelectorAll('.sidebar-card');
        
        catBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                catBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const cat = btn.dataset.category;
                let visibleCount = 0;
                
                compactCards.forEach(card => {{
                    const article = card.closest('article');
                    if (cat === 'all') {{
                        card.style.display = '';
                        visibleCount++;
                    }} else {{
                        const link = card.querySelector('a');
                        const title = card.querySelector('.compact-title').textContent.toLowerCase();
                        const cats = {{JSON.stringify(list(CATEGORIES.keys()))}};
                        const catKeywords = {{
                            'tech': ['tecnologia', 'software', 'app', 'google', 'apple'],
                            'sports': ['futebol', 'esporte', 'atleta', 'jogador'],
                            'politics': ['governo', 'política', 'deputado', 'vereador'],
                            'economy': ['economia', 'mercado', 'emprego', 'banco'],
                            'health': ['saúde', 'hospital', 'médico', 'vacina'],
                            'security': ['polícia', 'crime', 'suspeito', 'prisão'],
                            'agriculture': ['agro', 'safra', 'produtor', 'soja'],
                        }};
                        
                        const keywords = catKeywords[cat] || [];
                        const match = keywords.some(kw => title.includes(kw));
                        card.style.display = match ? '' : 'none';
                        if (match) visibleCount++;
                    }}
                }});
                
                // Update count
                const countEl = btn.querySelector('.cat-count');
                if (countEl) countEl.textContent = visibleCount;
            }});
        }});
        
        // Mobile menu toggle
        document.querySelector('.mobile-toggle')?.addEventListener('click', () => {{
            document.querySelector('.nav-menu').classList.toggle('show');
        }});
    </script>
</body>
</html>'''
    
    return html


def main():
    print("📰 Gerando portal Atualiza Brasil...\n")
    
    print("⏳ Buscando notícias...")
    articles = fetch_articles()
    print(f"✅ {len(articles)} artigos encontrados\n")
    
    html = generate_html(articles)
    
    output_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Portal gerado: {output_path}")
    print(f"📊 {len(articles)} notícias incluídas")
    print(f"\n🌐 Abra no navegador:")
    print(f"   file://{os.path.abspath(output_path)}")


if __name__ == '__main__':
    main()
