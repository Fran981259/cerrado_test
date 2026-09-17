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
from urllib.parse import urlsplit, urlunsplit
import unicodedata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis TTL for dedup (7 dias)
DEDUP_TTL_SECONDS = int(os.getenv("DEDUP_TTL_SECONDS", "604800"))
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        raise RuntimeError("REDIS_URL obrigatorio em producao")
    REDIS_URL = "redis://localhost:6379/0"


def _redact_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
        netloc = parsed.hostname or ""
        if parsed.port:
            netloc += f":{parsed.port}"
        return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
    except Exception:
        return "<invalid-url>"

def _normalize_dedup_url(url: str) -> str:
    try:
        from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
        p = urlsplit((url or "").strip())
        scheme = (p.scheme or "https").lower()
        netloc = (p.hostname or "").lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        if p.port:
            netloc += f":{p.port}"
        path = p.path.rstrip("/") or ""
        # remove utm_* e fbclid
        qsl = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not k.lower().startswith("utm_") and k.lower() not in ("fbclid", "gclid")]
        query = urlencode(qsl, doseq=True)
        return urlunsplit((scheme, netloc, path, query, ""))
    except Exception:
        return (url or "").strip().rstrip("/").lower()

def _get_redis():
    try:
        import redis as redis_lib
        client = redis_lib.from_url(REDIS_URL, socket_connect_timeout=2, socket_timeout=2, decode_responses=True)
        client.ping()
        return client
    except Exception as e:
        logger.debug(f"[DEDUP] Redis não disponível ({_redact_url(REDIS_URL)}): {e} — usando memória")
        return None


class ContentFilter:
    """Filtro de qualidade e duplicatas — com persistência Redis (ou memória fallback)."""
    
    def __init__(self, similarity_threshold: float = 0.85, use_redis: bool = True):
        self.similarity_threshold = similarity_threshold
        self.seen_hashes: Set[str] = set()
        self.seen_titles: List[str] = []
        # Tenta Redis para persistência cross-run (sorted sets com expiração por item)
        self._redis = _get_redis() if use_redis else None
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
        
        # Filtro de palavras desativado: portal de notícias publica os fatos sem censura de termos.
        # Mantido vazio por determinação editorial — nenhum termo bloqueia publicação.
        self.blocked_keywords: List[str] = []
        self.low_quality_keywords: List[str] = []
    
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
        
        # Filtro de palavras desativado — nenhum termo rejeita artigo (portal publica fatos sem censura)
        # Verificação mantida apenas para compatibilidade, mas listas estão vazias.
        
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
        """Detecta se o artigo é duplicata — com persistência Redis (URL normalizada)."""
        url = _normalize_dedup_url(article.get('url', '') or '')
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

        # Similaridade de título — busca títulos do Redis se disponível (normalizado)
        title = re.sub(r"\s+", " ", (article.get('title', '') or "").strip().lower())
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
                norm_seen = re.sub(r"\s+", " ", (seen_title or "").strip().lower())
                similarity = SequenceMatcher(None, title, norm_seen).ratio()
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
        if similarity >= threshold:
            return True
            
        return DuplicateDetector.are_semantically_similar(title1, title2)
    
    @staticmethod
    def get_keywords(text: str) -> set:
        """Extrai o núcleo de palavras-chave do texto (ignora stopwords comuns)."""
        if not text:
            return set()
        stopwords = {"para", "como", "sobre", "pelo", "pela", "onde", "mais", "isso", "esse", "esta", "entre", "ainda"}
        # Normaliza e remove acentos
        n_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
        words = set(re.findall(r'\b[a-z]{4,}\b', n_text))
        return words - stopwords

    @staticmethod
    def are_semantically_similar(text1: str, text2: str) -> bool:
        """Verifica se dois textos partilham as mesmas palavras-chave fundamentais."""
        kw1 = DuplicateDetector.get_keywords(text1)
        kw2 = DuplicateDetector.get_keywords(text2)
        
        if not kw1 or not kw2:
            return False
            
        intersection = kw1.intersection(kw2)
        overlap_ratio = len(intersection) / min(len(kw1), len(kw2))
        
        # Se compartilham pelo menos 3 palavras chaves fortes e mais de 45% de sobreposição
        return len(intersection) >= 3 and overlap_ratio >= 0.45
    
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
    """Filtro de conteúdo sensível — desativado: portal publica fatos sem censura."""

    SENSITIVE_TOPICS: Dict[str, Dict] = {}

    @staticmethod
    def check(article: Dict) -> Dict:
        """Desativado: sempre retorna não sensível (nenhum termo filtra)."""
        return {"is_sensitive": False}
