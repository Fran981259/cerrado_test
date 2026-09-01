"""
Agente Publicador — Portal Cerrado
Publica as matérias no banco de dados REAL.
"""

import os
import re
import logging
from difflib import SequenceMatcher
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.database import get_session
from app.schema import NewsArticle, Reporter, PublicationLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Threshold de similaridade para Lei 9.610/98 Art. 46/47 (paráfrase)
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))


class ArticlePublisher:
    """Publica artigos no banco de dados REAL."""
    
    def __init__(self, db_session: Session = None):
        self._db_session = db_session
    
    @property
    def db(self) -> Session:
        if self._db_session is None:
            self._db_session = get_session()
        return self._db_session
    
    def publish_article(self, article_data: Dict) -> Dict:
        """Publica um artigo no banco de dados REAL."""
        
        logger.info(f"Publicando: {article_data.get('title', '')[:50]}...")
        
        # Valida campos obrigatórios
        required = ['title', 'content', 'reporter_slug', 'category']
        for field in required:
            if not article_data.get(field):
                raise ValueError(f"Campo obrigatório: {field}")

        # --- Lei 9.610/98 Art. 46/47: verifica paráfrase (similaridade) ---
        threshold = float(os.getenv("SIMILARITY_THRESHOLD", str(DEFAULT_SIMILARITY_THRESHOLD)))
        content = article_data.get('content', '') or ''
        original = article_data.get('original_text') or article_data.get('body') or ''
        # Só verifica se temos ambos e se não é curiosidade (is_curiosity pode ter original vazio)
        if content and original and not article_data.get('is_curiosity'):
            # compara até 4000 chars para performance, case-insensitive
            sim = SequenceMatcher(None, content[:4000].lower(), original[:4000].lower()).ratio()
            if sim > threshold:
                logger.warning(f"[COMPLIANCE] Similaridade {sim:.2%} > {threshold:.0%} para '{article_data.get('title','')[:60]}' — bloqueado (Art. 46/47)")
                raise ValueError(f"Conteúdo muito similar ao original ({sim:.1%} > {threshold:.0%} threshold) — reescreva com paráfrase própria")
            logger.info(f"[COMPLIANCE] Similaridade {sim:.1%} OK para '{article_data.get('title','')[:40]}'")
        
        # Busca repórter
        reporter = self._get_or_create_reporter(article_data['reporter_slug'])
        
        # Gera slug único
        slug = self._generate_slug(article_data['title'])
        
        # Cria artigo
        article = NewsArticle(
            title=article_data['title'],
            slug=slug,
            summary=article_data.get('summary', ''),
            content=article_data['content'],
            reporter_id=reporter.id,
            
            sources=article_data.get('sources', []),
            original_text=article_data.get('original_text', ''),
            compliance_hash=article_data.get('hash', ''),
            
            status='published',
            published_at=datetime.utcnow(),
            visibility='public',
            
            category=article_data['category'],
            tags=article_data.get('tags', []),
            
            importance_score=int(article_data.get('importance_score', 0) * 10),
            engagement_score=int(article_data.get('engagement_score', 0) * 10),
            final_score=int(article_data.get('final_score', 0) * 10),
            priority_tier=article_data.get('priority_tier', 'TIER_2'),
            is_curiosity=article_data.get('is_curiosity', False),
        )
        
        try:
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            
            # Log de auditoria
            self._log_publication(article, article_data)
            
            # Atualiza contador do repórter
            reporter.articles_published += 1
            self.db.commit()
            
            logger.info(f"Publicado com ID {article.id}: {slug}")
            
            return {
                'success': True,
                'article_id': article.id,
                'slug': slug,
                'published_at': article.published_at.isoformat(),
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao publicar: {e}")
            raise
    
    def _get_or_create_reporter(self, slug: str) -> Reporter:
        """Busca ou cria repórter."""
        reporter = self.db.query(Reporter).filter(Reporter.slug == slug).first()
        
        if not reporter:
            # Cria repórter com dados básicos
            reporter = Reporter(
                slug=slug,
                display_name=slug.replace('.', ' ').title(),
                role='general',
                email=f"{slug}@portalcerrado.com.br",
            )
            self.db.add(reporter)
            self.db.commit()
            self.db.refresh(reporter)
            logger.info(f"Criado repórter: {slug}")
        
        return reporter
    
    def _generate_slug(self, title: str) -> str:
        """Gera slug URL-friendly único (sem colisão)."""
        import unicodedata
        # normaliza acentos
        slug = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode("ascii")
        slug = slug.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug.strip('-')
        base_slug = (slug[:180].strip('-') or "artigo")
        
        # 1) tenta base sem sufixo
        if not self.db.query(NewsArticle).filter(NewsArticle.slug == base_slug).first():
            return base_slug
        # 2) base-2, base-3...
        counter = 2
        while True:
            candidate = f"{base_slug}-{counter}"
            exists = self.db.query(NewsArticle).filter(NewsArticle.slug == candidate).first()
            if not exists:
                return candidate
            counter += 1
    
    def _log_publication(self, article: NewsArticle, article_data: Dict):
        """Registra log de auditoria."""
        log = PublicationLog(
            article_id=article.id,
            action='published',
            reporter_id=article.reporter_id,
            details=f"Publicado: {article.title[:100]}",
        )
        self.db.add(log)
        self.db.commit()
    
    def publish_batch(self, articles: List[Dict]) -> List[Dict]:
        """Publica múltiplos artigos."""
        results = []
        for article in articles:
            try:
                result = self.publish_article(article)
                results.append(result)
            except Exception as e:
                logger.error(f"Erro: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'title': article.get('title', 'Sem título'),
                })
        return results
    
    def get_published_articles(self, limit: int = 20, 
                                category: str = None) -> List[Dict]:
        """Busca artigos publicados."""
        query = self.db.query(NewsArticle).filter(
            NewsArticle.status == 'published'
        )
        
        if category:
            query = query.filter(NewsArticle.category == category)
        
        articles = query.order_by(
            NewsArticle.published_at.desc()
        ).limit(limit).all()
        
        return [self._article_to_dict(a) for a in articles]
    
    def _article_to_dict(self, article: NewsArticle) -> Dict:
        """Converte artigo para dict."""
        return {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.summary,
            'content': article.content,
            'category': article.category,
            'reporter': article.reporter.display_name if article.reporter else None,
            'reporter_slug': article.reporter.slug if article.reporter else None,
            'author': article.author,
            'image_url': article.image_url,
            'sources': article.sources,
            'tags': article.tags,
            'published_at': article.published_at.isoformat() if article.published_at else None,
            'is_curiosity': article.is_curiosity,
        }
    
    def close(self):
        """Fecha sessão do banco."""
        if self._db_session:
            self._db_session.close()


# Função para usar com Celery
def publish_article_task(article_data: Dict) -> Dict:
    """Publica um artigo (para uso em tasks)."""
    publisher = ArticlePublisher()
    try:
        return publisher.publish_article(article_data)
    finally:
        publisher.close()
