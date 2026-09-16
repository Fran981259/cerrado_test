"""Publication checks are editorial safeguards, not a legal compliance verdict."""
import os
from difflib import SequenceMatcher

from app.contracts import sources_list, CATEGORIES, category_name


class EditorialRejection(ValueError):
    pass


def validate_publication(article):
    for key in ("title", "content", "category"):
        if not isinstance(article.get(key), str) or not article[key].strip():
            raise EditorialRejection(f"Campo obrigatorio: {key}")
    if len(article["title"]) > 500:
        raise EditorialRejection("Titulo excede 500 caracteres")
    cat = category_name(article["category"])
    if cat not in CATEGORIES:
        raise EditorialRejection(f"Categoria invalida: {article['category']} -> {cat}")
    article["category"] = cat
    if article.get("priority_tier") == "REJECT":
        raise EditorialRejection("Prioridade editorial rejeitada")
    original = article.get("original_text") or article.get("body") or ""
    content = article["content"]
    if original and not article.get("is_curiosity"):
        similarity = SequenceMatcher(None, content[:4000].lower(), original[:4000].lower()).ratio()
        if similarity > float(os.getenv("SIMILARITY_THRESHOLD", "0.35")):
            raise EditorialRejection("Conteudo muito similar ao original")
    if not sources_list(article.get("sources")):
        raise EditorialRejection("Fonte verificavel obrigatoria")
    # Filtros de palavras/sensibilidade desativados — portal publica fatos sem censura (decisão editorial).
    # Mantém apenas dedup e validações estruturais; não rejeita por termo.
