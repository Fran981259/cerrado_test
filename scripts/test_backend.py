"""
Script de Teste — Atualiza Brasil
Testa o pipeline completo: scan → classify → filter → rewrite → publish
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_imports():
    """Testa se todas as importações funcionam."""
    print("\n" + "="*60)
    print("TESTE 1: Importações")
    print("="*60)
    
    modules = [
        ("database", "Conexão PostgreSQL"),
        ("schema", "Modelos SQLAlchemy"),
        ("scanner", "Scanner de portais BR"),
        ("classifier", "Classificador de artigos"),
        ("filter", "Filtro de qualidade"),
        ("rewriter", "Reescritor"),
        ("publisher", "Publicador"),
        ("llm_client", "Cliente LLM"),
        ("translator", "Tradutor"),
        ("personality", "Evolução de personalidade"),
        ("curiosities", "Gerador de curiosidades"),
        ("auditor", "Auditor HORUS"),
    ]
    
    all_ok = True
    for module, desc in modules:
        try:
            exec(f"from app import {module}")
            print(f"✅ {module:15} - {desc}")
        except Exception as e:
            print(f"❌ {module:15} - ERRO: {e}")
            all_ok = False
    
    return all_ok


def test_database():
    """Testa conexão com banco de dados."""
    print("\n" + "="*60)
    print("TESTE 2: Banco de Dados")
    print("="*60)
    
    try:
        from app.database import engine, get_session, Base
        from app.schema import NewsArticle, Reporter
        
        # Testa engine
        print(f"✅ Engine criado: {engine.url}")
        
        # Cria tabelas
        print("Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas")
        
        # Testa sessão
        db = get_session()
        print(f"✅ Sessão criada: {db.bind.url.database}")
        
        # Conta tabelas
        articles = db.query(NewsArticle).count()
        reporters = db.query(Reporter).count()
        print(f"✅ Tabelas ok - Artigos: {articles}, Repórteres: {reporters}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("   (Banco não está rodando - isso é esperado se Docker não estiver ativo)")
        return False


def test_scanner():
    """Testa scanner de portais."""
    print("\n" + "="*60)
    print("TESTE 3: Scanner (Coleta de Portais BR)")
    print("="*60)
    
    try:
        from app.scanner import RealPortalScanner
        
        scanner = RealPortalScanner()
        
        print(f"Portais configurados: {len(scanner.PORTALS)}")
        for p in scanner.PORTALS:
            print(f"  - {p['name']} ({p['url']})")
        
        print("\nExecutando scan...")
        results = scanner.scan_all()
        
        print(f"\n✅ Scan concluído!")
        print(f"   Portais: {results['summary']}")
        print(f"   Artigos coletados: {len(results.get('articles', []))}")
        
        if results.get('articles'):
            print("\nPrimeiros 3 artigos:")
            for i, art in enumerate(results['articles'][:3], 1):
                print(f"  {i}. [{art['category']}] {art['title'][:60]}...")
                print(f"     Fonte: {art['source']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_classifier():
    """Testa classificador."""
    print("\n" + "="*60)
    print("TESTE 4: Classificador")
    print("="*60)
    
    try:
        from app.classifier import classify_articles
        
        test_articles = [
            {
                'title': 'OpenAI announces GPT-5 with advanced reasoning',
                'summary': 'The new AI model shows unprecedented capabilities...',
                'source': 'TechCrunch',
                'category': 'technology',
            },
            {
                'title': 'Fed raises interest rates again',
                'summary': 'The Federal Reserve announced another rate hike...',
                'source': 'Bloomberg',
                'category': 'economy',
            },
            {
                'title': 'Jogador marca gol aos 90 minutos',
                'summary': 'Nos últimos segundos da partida...',
                'source': 'MS News',
                'category': 'sports',
            },
        ]
        
        classified = classify_articles(test_articles)
        
        print(f"✅ Classificados: {len(classified)}")
        
        for art in classified:
            c = art['classification']
            print(f"\n  📰 {art['title'][:50]}...")
            print(f"     Importância: {c['importance_score']} ({c['importance_level']})")
            print(f"     Engajamento: {c['engagement_score']} ({c['engagement_level']})")
            print(f"     Score Final: {c['final_score']} → {c['priority_tier']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_filter():
    """Testa filtro."""
    print("\n" + "="*60)
    print("TESTE 5: Filtro de Qualidade")
    print("="*60)
    
    try:
        from app.filter import filter_articles, check_sensitive
        from app.classifier import classify_articles
        
        test_articles = [
            {
                'title': 'Jogador marca gol aos 90 minutos',
                'summary': 'Nos últimos segundos da partida...',
                'source': 'MS News',
                'category': 'sports',
            },
            {
                'title': 'Teste de clique aqui para ganhar dinheiro',
                'summary': 'Clique aqui agora...',
                'source': 'Spam Site',
                'category': 'general',
            },
        ]
        
        classified = classify_articles(test_articles)
        filtered = filter_articles(classified)
        
        print(f"✅ Filtrados: {len(filtered)}/{len(test_articles)}")
        
        for art in filtered:
            print(f"  ✅ {art['title'][:50]}...")
        
        # Testa sensível
        print("\nTestando filtro de conteúdo sensível...")
        sensitive_test = {
            'title': 'Notícia sobre criança',
            'summary': 'Vítima era menor de idade...',
        }
        result = check_sensitive(sensitive_test)
        print(f"   Resultado: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_publisher():
    """Testa publicador."""
    print("\n" + "="*60)
    print("TESTE 6: Publicador (Salvar no DB)")
    print("="*60)
    
    try:
        from app.publisher import ArticlePublisher
        
        publisher = ArticlePublisher()
        
        test_article = {
            'title': 'Teste: Jogador marca gol aos 90 minutos na final',
            'content': '''O clube saiu na frente aos 15 minutos do primeiro tempo, 
            mas sofreu o empate aos 80. Quando todos já esperavam a decisão nos pênaltis, 
            o atacante fez o gol da vitória aos 90+3.''',
            'summary': 'Gol nos acréscimos decidiu a partida',
            'reporter_slug': 'marcus.teixeira',
            'category': 'sports',
            'sources': ['https://example.com/news/123'],
            'importance_score': 3.5,
            'engagement_score': 4.0,
            'final_score': 3.7,
            'priority_tier': 'TIER_2',
        }
        
        print("Publicando artigo de teste...")
        result = publisher.publish_article(test_article)
        
        print(f"\n✅ Publicado com sucesso!")
        print(f"   ID: {result['article_id']}")
        print(f"   Slug: {result['slug']}")
        print(f"   Timestamp: {result['published_at']}")
        
        publisher.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_api():
    """Testa API."""
    print("\n" + "="*60)
    print("TESTE 7: API Endpoints")
    print("="*60)
    
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Testa root
        resp = client.get("/")
        print(f"✅ GET /: {resp.status_code}")
        
        # Testa health
        resp = client.get("/health")
        print(f"✅ GET /health: {resp.status_code}")
        if resp.status_code == 200:
            print(f"   Database: {resp.json().get('database')}")
            print(f"   Articles: {resp.json().get('articles_count', 'N/A')}")
        
        # Testa news
        resp = client.get("/api/news?limit=5")
        print(f"✅ GET /api/news: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   Total: {data.get('total', 0)}")
            print(f"   News: {len(data.get('news', []))}")
        
        # Testa reporters
        resp = client.get("/api/reporters")
        print(f"✅ GET /api/reporters: {resp.status_code}")
        if resp.status_code == 200:
            reporters = resp.json().get('reporters', [])
            print(f"   Repórteres: {len(reporters)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_curiosities():
    """Testa curiosidades."""
    print("\n" + "="*60)
    print("TESTE 8: Sistema de Curiosidades")
    print("="*60)
    
    try:
        from app.curiosities import generate_all_daily_curiosities
        
        curiosities = generate_all_daily_curiosities()
        
        print(f"✅ Geradas: {len(curiosities)} curiosidades")
        
        for c in curiosities[:3]:
            print(f"\n  🗂️ {c['category'].upper()}")
            print(f"  📰 {c['title']}")
            print(f"  ✍️  {c['reporter_slug']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("🔬 TESTE COMPLETO — ATUALIZA BRASIL")
    print("="*60)
    
    results = []
    
    results.append(("Importações", test_imports()))
    results.append(("Scanner", test_scanner()))
    results.append(("Classificador", test_classifier()))
    results.append(("Filtro", test_filter()))
    results.append(("Curiosidades", test_curiosities()))
    results.append(("Banco de Dados", test_database()))
    results.append(("Publicador", test_publisher()))
    results.append(("API", test_api()))
    
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("O backend está funcionando corretamente.")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falhou(aram).")
        print("Verifique os erros acima.")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
