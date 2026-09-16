import logging
import re
from typing import List
from datetime import datetime, timezone
from app.database import get_session
from app.schema import NewsArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit_frankensteins")

def tokenize(text: str) -> set:
    if not text:
        return set()
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    # Stop words basicas
    stopwords = {'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão', 'você', 'tinha', 'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam', 'após', 'sobre', 'sob', 'ante'}
    return set(w for w in words if w not in stopwords and len(w) > 2)

def detect_mismatches():
    db = get_session()
    articles = db.query(NewsArticle).filter(NewsArticle.status.in_(['published', 'review', 'classified', 'draft'])).all()
    logger.info(f"Checking {len(articles)} articles...")
    
    mismatched = 0
    for a in articles:
        if not a.title or not a.original_text:
            continue
            
        title_tokens = tokenize(a.title)
        content_tokens = tokenize(a.original_text)
        
        if not title_tokens:
            continue
            
        intersection = title_tokens.intersection(content_tokens)
        overlap = len(intersection) / len(title_tokens)
        
        # Se menos de 10% das palavras-chave do título aparecem no texto, 
        # há grande chance de ser um Frankenstein.
        # Ajustamos o limite para 0.15 (15%) para pegar os flagrantes.
        if overlap < 0.15 and len(title_tokens) >= 3:
            logger.warning(f"FRANKENSTEIN DETECTADO! [overlap={overlap:.2f}]")
            logger.warning(f"Slug: {a.slug}")
            logger.warning(f"Title: {a.title}")
            logger.warning(f"Tokens in Title: {title_tokens}")
            logger.warning(f"Matched tokens: {intersection}")
            logger.warning("-" * 40)
            
            a.status = 'rejected'
            a.priority_tier = 'REJECT'
            a.rejection_reason = "Frankenstein Detectado (Overlap Título x Corpo muito baixo)"
            a.updated_at = datetime.now(timezone.utc)
            mismatched += 1
            
    if mismatched > 0:
        db.commit()
    db.close()
    logger.info(f"Auditoria finalizada. {mismatched} Frankensteins abatidos.")

if __name__ == "__main__":
    detect_mismatches()
