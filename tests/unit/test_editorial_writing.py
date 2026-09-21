import pytest

from app.editorial import EditorialRejection, reject_blocked_writing, review_natural_writing


def test_writing_review_blocks_internal_placeholders():
    findings = review_natural_writing("A prefeitura informou: INSIRA AQUI o valor final.")
    assert any(f.code == "internal_placeholder" and f.severity == "block" for f in findings)
    with pytest.raises(EditorialRejection, match="placeholder"):
        reject_blocked_writing("A prefeitura informou: INSIRA AQUI o valor final.")
    assert any(f.code == "internal_placeholder" for f in review_natural_writing("[TODO] revisar o texto."))


def test_writing_review_routes_vague_attribution_to_editor():
    findings = review_natural_writing("Especialistas dizem que o mercado terá impacto.")
    assert any(f.code == "vague_attribution" and f.severity == "review" for f in findings)


def test_writing_review_allows_direct_factual_copy():
    findings = review_natural_writing("O governo publicou o decreto nesta terça-feira, segundo o Diário Oficial.")
    assert findings == []
