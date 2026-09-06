"""Unit tests para ContentFilter, DuplicateDetector, SensitiveContentFilter e scanner _is_valid_article."""
import time
from app.filter import ContentFilter, DuplicateDetector, SensitiveContentFilter, DEDUP_TTL_SECONDS
from app.scanner import RealPortalScanner


class FakeRedis:
    """Sorted-set mínimo em memória p/ testar a dedup sem Redis real."""

    def __init__(self):
        self.data = {}

    def zadd(self, key, mapping):
        self.data.setdefault(key, {}).update(mapping)
        return len(mapping)

    def zremrangebyscore(self, key, min_v, max_v):
        cutoff = float(max_v)
        store = self.data.get(key, {})
        expired = [m for m, s in store.items() if float("-inf") <= float(s) <= cutoff] if min_v == "-inf" else []
        for m in expired:
            del store[m]
        return len(expired)

    def zscore(self, key, member):
        s = self.data.get(key, {}).get(member)
        return float(s) if s is not None else None

    def zrange(self, key, start, end):
        items = sorted(self.data.get(key, {}).items(), key=lambda kv: kv[1])
        members = [m for m, _ in items]
        return members[start:end + 1 if end >= 0 else len(members)]

    def zrevrange(self, key, start, end):
        items = sorted(self.data.get(key, {}).items(), key=lambda kv: kv[1], reverse=True)
        members = [m for m, _ in items]
        return members[start:end + 1 if end >= 0 else len(members)]


def _filter_with_fake_redis():
    f = ContentFilter(similarity_threshold=0.85)
    f._redis = FakeRedis()
    return f


def test_dedup_prunes_expired_entry():
    f = _filter_with_fake_redis()
    old = time.time() - DEDUP_TTL_SECONDS - 100
    url = "https://ex.com/velha"
    import hashlib
    h = hashlib.md5(url.encode()).hexdigest()
    f._redis.zadd(f._redis_hash_key, {h: old})
    f._redis.zadd(f._redis_titles_key, {"titulo bem diferente e antigo": old})
    art = {"title": "Manchete nova sem relação alguma com outra", "summary": "Texto", "url": url}
    f._prune_redis()
    assert f._redis.zscore(f._redis_hash_key, h) is None  # foi podada
    assert f._is_duplicate(art) is False  # expirada: não é duplicata


def test_dedup_keeps_recent_entry():
    f = _filter_with_fake_redis()
    url = "https://ex.com/recente"
    art = {"title": "Primeira manchete válida para dedup", "summary": "Texto", "url": url}
    assert f.is_valid(art) is True
    art2 = {"title": "Outra manchete totalmente distinta aqui", "summary": "Outro", "url": url}
    assert f.is_valid(art2) is False  # mesma url recente: duplicata

def test_content_filter_blocks_duplicate_url():
    f = ContentFilter(similarity_threshold=0.85)
    a1 = {"title": "Treze mil vagas abertas em Campo Grande", "summary": "Governo anuncia", "url": "https://ex.com/a"}
    a2 = {"title": "Outra manchete totalmente diferente", "summary": "Outro texto", "url": "https://ex.com/a"}
    assert f.is_valid(a1) is True
    assert f.is_valid(a2) is False  # mesma url

def test_content_filter_blocks_similar_title():
    f = ContentFilter(similarity_threshold=0.85)
    a1 = {"title": "Valor do combustível pode variar até 13,5% entre postos de Campo Grande", "summary": "Texto", "url": "https://ex.com/1"}
    a2 = {"title": "Valor do combustível pode variar até 13,5% entre postos de Campo Grande", "summary": "Outro", "url": "https://ex.com/2"}
    assert f.is_valid(a1) is True
    assert f.is_valid(a2) is False

def test_sensitive_filter_blocks_child_victim():
    art = {"title": "Child victim found after accident", "summary": ""}
    res = SensitiveContentFilter.check(art)
    assert res["is_sensitive"] is True
    assert res["action"] == "block"

def test_sensitive_filter_allows_normal():
    art = {"title": "Festival de Inverno de Bonito celebra cultura local", "summary": ""}
    assert SensitiveContentFilter.check(art)["is_sensitive"] is False

def test_duplicate_detector_are_duplicates():
    a1 = {"title": "Mato Grosso do Sul acumula 19 mil empregos"}
    a2 = {"title": "Mato Grosso do Sul acumula 19 mil empregos"}
    assert DuplicateDetector.are_duplicates(a1, a2) is True
    a3 = {"title": "UEMS realiza feira cultural Sabores do Cerrado"}
    assert DuplicateDetector.are_duplicates(a1, a3) is False

def test_scanner_blocks_generic_titles():
    s = RealPortalScanner()
    assert s._is_valid_article({"title": "O Estado Online", "url": "https://oestadoonline.com.br/"}) is False
    assert s._is_valid_article({"title": "O Estado Online", "url": "https://oestadoonline.com.br/homepage-nova-copy/"}) is False
    assert s._is_valid_article({"title": "Mercedita e serenatas - O Estado Online", "url": "https://oestadoonline.com.br/arte-e-lazer/mercedita-e-serenatas/"}) is False

def test_scanner_allows_real_article():
    s = RealPortalScanner()
    assert s._is_valid_article({"title": "TRE-MS retoma julgamento sobre mandato de Marquinhos Trad e analisa recurso", "url": "https://oestadoonline.com.br/politica/tre-ms-retoma-julgamento-sobre-mandato/"}) is True
    assert s._is_valid_article({"title": "Valor do combustível pode variar até 13,5% entre postos de Campo Grande hoje", "url": "https://agenciadenoticias.ms.gov.br/valor-do-combustivel-pode-variar/"}) is True

def test_scanner_blocks_homepage_root():
    s = RealPortalScanner()
    # homepage raiz sem slug profundo
    assert s._is_valid_article({"title": "Notícia muito longa com título válido para passar no tamanho", "url": "https://oestadoonline.com.br/"}) is False
    assert s._is_valid_article({"title": "Notícia muito longa com título válido para passar no tamanho", "url": "https://oestadoonline.com.br/a"}) is False

def test_quality_score():
    f = ContentFilter()
    art = {"title": "Título com tamanho ideal para engajamento e leitura", "summary": "x"*600, "source": "Agência MS", "url": "https://ex.com/a", "image_url": "https://ex.com/img.jpg", "published_at": "2026-08-31"}
    score = f.calculate_quality_score(art)
    assert 7 <= score <= 10
