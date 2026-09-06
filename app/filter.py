# ============================================================
# Filtro de Qualidade — Portal Cerrado
# ============================================================
# Remove duplicatas, conteúdo de baixa qualidade,
# conteúdo sensível, etc.
# ============================================================

import os
import re
import time
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis TTL for dedup (7 dias)
DEDUP_TTL_SECONDS = int(os.getenv("DEDUP_TTL_SECONDS", "604800"))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

def _get_redis():
    try:
        import redis as redis_lib
        client = redis_lib.from_url(REDIS_URL, socket_connect_timeout=2, socket_timeout=2, decode_responses=True)
        client.ping()
        return client
    except Exception as e:
        logger.debug(f"[DEDUP] Redis não disponível ({REDIS_URL}): {e} — usando memória")
        return None


class ContentFilter:
    """Filtro de qualidade e duplicatas — com persistência Redis (ou memória fallback)."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.seen_hashes: Set[str] = set()
        self.seen_titles: List[str] = []
        # Tenta Redis para persistência cross-run (sorted sets com expiração por item)
        self._redis = _get_redis()
        self._redis_hash_key = "dedup:hashes"
        self._redis_titles_key = "dedup:titles"
        if self._redis:
            try:
                self._prune_redis()
                # Carrega hashes existentes (já podados)
                for h in self._redis.zrange(self._redis_hash_key, 0, -1) or []:
                    self.seen_hashes.add(h)
                for t in self._redis.zrange(self._redis_titles_key, 0, -1) or []:
                    self.seen_titles.append(t)
                logger.info(f"[DEDUP] Redis carregado: {len(self.seen_hashes)} hashes, {len(self.seen_titles)} títulos")
            except Exception as e:
                logger.debug(f"[DEDUP] falha ao carregar Redis: {e}")
                self._redis = None
        
        # Palavras sensíveis (não publicar)
        self.blocked_keywords = [
            # Violência extrema
            "execution", "execução", "torture", "tortura",
            "beheading", "decapitação", "massacre",
            
            # Conteúdo sexual explícito
            "pornography", "pornografia",
            
            # Discurso de ódio
            "racism", "racismo",
            "nazi", "fascist", "fascista",
            "hate crime",
            
            # Substâncias ilegais (em contexto de venda)
            "drug trafficking", "tráfico de drogas",
            
            # Desastres (com vítimas específicas - sensível)
            # Não bloquear completamente, mas filtrar com cuidado
        ]
        
        # Palavras que indicam baixa qualidade
        self.low_quality_keywords = [
            "click here", "clique aqui",
            "buy now", "compre agora",
            "limited time", "tempo limitado",
            "make money fast", "ganhe dinheiro rápido",
            "weight loss miracle", "emagrecimento milagroso",
        ]
    
    def is_valid(self, article: Dict) -> bool:
        """Verifica se o artigo é válido para publicação."""
        
        # Validações básicas
        if not article.get('title'):
            logger.debug("Artigo rejeitado: sem título")
            return False
        
        if not article.get('summary') and not article.get('content'):
            logger.debug("Artigo rejeitado: sem conteúdo")
            return False
        
        title_lower = article['title'].lower()
        summary_lower = article.get('summary', '').lower()
        combined = title_lower + ' ' + summary_lower
        
        # Verifica palavras sensíveis
        for keyword in self.blocked_keywords:
            if keyword in combined:
                logger.warning(f"Artigo rejeitado por palavra sensível: {keyword}")
                return False
        
        # Verifica baixa qualidade
        for keyword in self.low_quality_keywords:
            if keyword in combined:
                logger.warning(f"Artigo rejeitado por baixa qualidade: {keyword}")
                return False
        
        # Verifica duplicatas
        if self._is_duplicate(article):
            logger.debug(f"Artigo rejeitado: duplicata")
            return False
        
        return True
    
    def _prune_redis(self, now: Optional[float] = None) -> None:
        """Remove entradas mais antigas que DEDUP_TTL_SECONDS (expiração por item).

        Usa sorted set com score = timestamp de inserção: diferente do EXPIRE
        na chave (que reiniciava o relógio do SET inteiro a cada SADD), cada
        entrada expira de forma independente.
        """
        if not self._redis:
            return
        cutoff = (now if now is not None else time.time()) - DEDUP_TTL_SECONDS
        try:
            self._redis.zremrangebyscore(self._redis_hash_key, "-inf", cutoff)
            self._redis.zremrangebyscore(self._redis_titles_key, "-inf", cutoff)
        except Exception as e:
            logger.debug(f"[DEDUP] falha ao podar Redis: {e}")

    def _is_duplicate(self, article: Dict) -> bool:
        """Detecta se o artigo é duplicata — com persistência Redis."""
        url = article.get('url', '') or ''
        url_hash = hashlib.md5(url.encode()).hexdigest()
        # Poda antes de checar: entradas expiradas não são duplicatas
        if self._redis:
            self._prune_redis()
            try:
                if self._redis.zscore(self._redis_hash_key, url_hash) is not None:
                    return True
            except Exception:
                pass
        else:
            if url_hash in self.seen_hashes:
                return True

        # Similaridade de título — busca títulos do Redis se disponível
        title = article.get('title', '').lower()
        titles_to_check = self.seen_titles
        if self._redis:
            try:
                # Pega até 500 títulos mais recentes do Redis (já podados)
                redis_titles = self._redis.zrevrange(self._redis_titles_key, 0, 499) or []
                if redis_titles:
                    titles_to_check = list(redis_titles)
            except Exception:
                pass
        for seen_title in titles_to_check:
            try:
                similarity = SequenceMatcher(None, title, seen_title.lower()).ratio()
                if similarity >= self.similarity_threshold:
                    return True
            except Exception:
                continue

        # Não é duplicata: persiste (score = timestamp p/ expiração por item)
        self.seen_hashes.add(url_hash)
        self.seen_titles.append(title)
        if self._redis:
            try:
                now = time.time()
                self._redis.zadd(self._redis_hash_key, {url_hash: now})
                self._redis.zadd(self._redis_titles_key, {title: now})
            except Exception as e:
                logger.debug(f"[DEDUP] falha ao persistir no Redis: {e}")

        # Limita memória local
        if len(self.seen_titles) > 1000:
            self.seen_titles = self.seen_titles[-500:]

        return False
    
    def filter_batch(self, articles: List[Dict]) -> List[Dict]:
        """Filtra uma lista de artigos."""
        filtered = []
        for article in articles:
            if self.is_valid(article):
                filtered.append(article)
        
        logger.info(f"Filtragem: {len(articles)} → {len(filtered)} artigos")
        return filtered
    
    def calculate_quality_score(self, article: Dict) -> float:
        """Calcula score de qualidade (0-10)."""
        score = 5.0  # Base
        
        # Tem imagem?
        if article.get('image_url'):
            score += 1.0
        
        # Tem resumo substancial?
        summary_len = len(article.get('summary', ''))
        if summary_len > 500:
            score += 1.0
        elif summary_len < 100:
            score -= 1.0
        
        # Tem fonte identificada?
        if article.get('source'):
            score += 0.5
        
        # Tem URL válido?
        if article.get('url') and article['url'].startswith('http'):
            score += 0.5
        
        # Título tem tamanho razoável?
        title_len = len(article.get('title', ''))
        if 30 <= title_len <= 120:
            score += 1.0
        elif title_len > 200:
            score -= 1.0
        
        # Tem data de publicação?
        if article.get('published_at'):
            score += 0.5
        
        return max(0.0, min(10.0, score))


class DuplicateDetector:
    """Detector avançado de duplicatas."""
    
    @staticmethod
    def are_duplicates(article1: Dict, article2: Dict, 
                       threshold: float = 0.85) -> bool:
        """Verifica se dois artigos são duplicatas."""
        
        # Compara títulos
        title1 = article1.get('title', '').lower()
        title2 = article2.get('title', '').lower()
        
        if not title1 or not title2:
            return False
        
        similarity = SequenceMatcher(None, title1, title2).ratio()
        return similarity >= threshold
    
    @staticmethod
    def find_duplicates(articles: List[Dict], 
                        threshold: float = 0.85) -> List[List[Dict]]:
        """Encontra grupos de duplicatas."""
        groups = []
        used = set()
        
        for i, a1 in enumerate(articles):
            if i in used:
                continue
            
            group = [a1]
            used.add(i)
            
            for j, a2 in enumerate(articles[i+1:], i+1):
                if j in used:
                    continue
                
                if DuplicateDetector.are_duplicates(a1, a2, threshold):
                    group.append(a2)
                    used.add(j)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups


class SensitiveContentFilter:
    """Filtro de conteúdo sensível."""
    
    SENSITIVE_TOPICS = {
        'children': {
            'keywords': ['child victim', 'criança vítima', 'minor', 'menor'],
            'action': 'block',  # Bloquear por padrão — prioridade máxima
        },
        'violence': {
            'keywords': ['murder', 'assassinato', 'killing', 'homicídio'],
            'action': 'review',  # Revisar antes de publicar
        },
        'accidents': {
            'keywords': ['accident', 'acidente', 'crash', 'colisão'],
            'action': 'review',
        },
        'tragedy': {
            'keywords': ['tragedy', 'tragédia', 'disaster', 'desastre'],
            'action': 'review',
        },
    }
    
    @staticmethod
    def check(article: Dict) -> Dict:
        """Verifica conteúdo sensível."""
        combined = (
            article.get('title', '') + ' ' + 
            article.get('summary', '')
        ).lower()
        
        for topic, config in SensitiveContentFilter.SENSITIVE_TOPICS.items():
            for keyword in config['keywords']:
                if keyword in combined:
                    return {
                        'is_sensitive': True,
                        'topic': topic,
                        'action': config['action'],
                        'keyword_found': keyword,
                    }
        
        return {'is_sensitive': False}


# Funções de conveniência
def filter_articles(articles: List[Dict]) -> List[Dict]:
    """Filtra uma lista de artigos."""
    content_filter = ContentFilter()
    return content_filter.filter_batch(articles)


def calculate_quality(article: Dict) -> float:
    """Calcula qualidade de um artigo."""
    content_filter = ContentFilter()
    return content_filter.calculate_quality_score(article)


def check_sensitive(article: Dict) -> Dict:
    """Verifica conteúdo sensível."""
    return SensitiveContentFilter.check(article)
