"""
Atualiza os artigos reais do frontend a partir do scanner.
Uso: python scripts/update_frontend_articles.py
"""
import json, re, unicodedata, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.scanner import RealPortalScanner

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii','ignore').decode('ascii')
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')
    return text[:80].strip('-')

scanner = RealPortalScanner()
result = scanner.scan_all()
raw = result['articles']
print(f"Coletados: {len(raw)} | Portais OK: {result['summary']['success']}/{result['summary']['total']}")

seen=set()
out=[]
for a in raw:
    title = a['title'].strip()
    summary = a.get('summary','') or title
    if len(summary) > 300:
        summary = summary[:300].rsplit(' ',1)[0]+'...'
    base_slug = slugify(title)
    slug = base_slug
    i=2
    while slug in seen:
        slug = f"{base_slug}-{i}"
        i+=1
    seen.add(slug)
    out.append({
        "title": title,
        "slug": slug,
        "summary": summary[:240],
        "content": "",
        "category": a.get('category','general'),
        "reporter_slug": a.get('reporter_slug','enzo.bianchi'),
        "url": a.get('url'),
        "sources": [a.get('url')],
        "tags": [a.get('category','general')],
        "published_at": a.get('scraped_at'),
        "image_url": "",
        "source": a.get('source')
    })

os.makedirs('frontend/src/data', exist_ok=True)
os.makedirs('frontend/public', exist_ok=True)
with open('frontend/src/data/articles.json','w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
with open('frontend/public/articles.json','w',encoding='utf-8') as f:
    json.dump({"articles": out, "generated_at": out[0]['published_at'] if out else "", "total": len(out)}, f, ensure_ascii=False, indent=2)

print(f"✅ Salvos {len(out)} artigos em frontend/src/data/articles.json e frontend/public/articles.json")
from collections import Counter
print(Counter(a['category'] for a in out))
print(Counter(a['source'] for a in out))
