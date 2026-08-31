"""Unit tests para ContentFilter, DuplicateDetector, SensitiveContentFilter e scanner _is_valid_article."""
from app.filter import ContentFilter, DuplicateDetector, SensitiveContentFilter
from app.scanner import RealPortalScanner

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
