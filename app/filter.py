# ============================================================
# Filtro de Qualidade — Portal Cerrado
# ============================================================
# Remove duplicatas, conteúdo de baixa qualidade,
# conteúdo sensível, etc.
# ============================================================

import hashlib
import logging
import os
import re
import time
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Set
from urllib.parse import urlsplit, urlunsplit

from app.duplicate_detection import DuplicateDetector, SensitiveContentFilter

__all__ = ["ContentFilter", "DuplicateDetector", "SensitiveContentFilter"]

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
        from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

        p = urlsplit((url or "").strip())
        scheme = (p.scheme or "https").lower()
        netloc = (p.hostname or "").lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        if p.port:
            netloc += f":{p.port}"
        path = p.path.rstrip("/") or ""
        # remove utm_* e fbclid
        qsl = [
            (k, v)
            for k, v in parse_qsl(p.query, keep_blank_values=True)
            if not k.lower().startswith("utm_") and k.lower() not in ("fbclid", "gclid")
        ]
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
        if not article.get("title"):
            logger.debug("Artigo rejeitado: sem título")
            return False

        if not article.get("summary") and not article.get("content"):
            logger.debug("Artigo rejeitado: sem conteúdo")
            return False

        if not article.get("image_url"):
            logger.debug("Artigo rejeitado: sem imagem original")
            return False

        title_lower = article["title"].lower()
        summary_lower = article.get("summary", "").lower()
        title_lower + " " + summary_lower

        # Filtro de palavras desativado — nenhum termo rejeita artigo (portal publica fatos sem censura)
        # Verificação mantida apenas para compatibilidade, mas listas estão vazias.

        # Verifica duplicatas
        if self._is_duplicate(article):
            logger.debug("Artigo rejeitado: duplicata")
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
        url = _normalize_dedup_url(article.get("url", "") or "")
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
        title = re.sub(r"\s+", " ", (article.get("title", "") or "").strip().lower())
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
        if article.get("image_url"):
            score += 1.0

        # Tem resumo substancial?
        summary_len = len(article.get("summary", ""))
        if summary_len > 500:
            score += 1.0
        elif summary_len < 100:
            score -= 1.0

        # Tem fonte identificada?
        if article.get("source"):
            score += 0.5

        # Tem URL válido?
        if article.get("url") and article["url"].startswith("http"):
            score += 0.5

        # Título tem tamanho razoável?
        title_len = len(article.get("title", ""))
        if 30 <= title_len <= 120:
            score += 1.0
        elif title_len > 200:
            score -= 1.0

        # Tem data de publicação?
        if article.get("published_at"):
            score += 0.5

        return max(0.0, min(10.0, score))
