"""Publication checks are editorial safeguards, not a legal compliance verdict."""

import os
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable

from app.contracts import CATEGORIES, category_name, sources_list
from app.local_news_policy import local_story_decision


class EditorialRejection(ValueError):
    pass


@dataclass(frozen=True)
class WritingFinding:
    """A deterministic signal for an editor; it is not a factuality verdict."""

    code: str
    severity: str  # "block" or "review"
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "severity": self.severity, "message": self.message}


_PLACEHOLDER_RE = re.compile(
    r"(?:\binsira(?:\s+(?:aqui|texto|url|link|data|nome))?\b|"
    r"\b(?:url|link|texto|data|nome)_(?:aqui|here)\b|\[\s*(?:todo|tbd)\s*\])",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"\bhttps?://\S+|\bwww\.\S+", re.IGNORECASE)
_VAGUE_ATTRIBUTION_RE = re.compile(
    r"\b(?:especialistas|analistas|estudos|pesquisas)\s+"
    r"(?:dizem|afirmam|apontam|mostram|indicam)|"
    r"\bé amplamente reconhecido\b",
    re.IGNORECASE,
)
_FORMULAIC_RE = re.compile(
    r"\b(?:em conclusão|em resumo|de modo geral|vale lembrar|diante disso|"
    r"nessa linha|não se trata apenas de|não é [^.]{1,80},? é)\b",
    re.IGNORECASE,
)
_EMPTY_ADJECTIVE_RE = re.compile(
    r"\b(?:crucial|notável|vibrante|robusto|inovador|revolucionário)\b",
    re.IGNORECASE,
)


def review_natural_writing(content: str) -> list[WritingFinding]:
    """Return observable style/provenance risks for human editorial review.

    This intentionally does not claim to verify facts or source support. Those
    require a person comparing the draft with the cited source material.
    """
    if not isinstance(content, str) or not content.strip():
        return [WritingFinding("empty_content", "block", "O texto reescrito está vazio.")]

    findings: list[WritingFinding] = []
    if _PLACEHOLDER_RE.search(content):
        findings.append(
            WritingFinding("internal_placeholder", "block", "O texto contém placeholder ou marcador interno.")
        )
    if _URL_RE.search(content):
        findings.append(WritingFinding("url_in_body", "review", "O corpo contém URL; confirme se ela é necessária."))
    if _VAGUE_ATTRIBUTION_RE.search(content):
        findings.append(
            WritingFinding(
                "vague_attribution",
                "review",
                "Há atribuição vaga. Confirme a fonte específica que sustenta a afirmação.",
            )
        )

    formulaic_count = len(_FORMULAIC_RE.findall(content))
    if formulaic_count:
        findings.append(
            WritingFinding(
                "formulaic_language",
                "review",
                "Há fórmula editorial previsível; revise se ela acrescenta informação.",
            )
        )
    adjective_count = len(_EMPTY_ADJECTIVE_RE.findall(content))
    if adjective_count >= 2:
        findings.append(
            WritingFinding(
                "empty_adjectives",
                "review",
                "Há adjetivação vaga repetida; substitua por informação verificável ou corte.",
            )
        )
    if content.count("—") > 3:
        findings.append(
            WritingFinding("excessive_dashes", "review", "O texto usa travessões em excesso."))
    return findings


def requires_human_writing_review(findings: Iterable[WritingFinding]) -> bool:
    return any(finding.severity == "review" for finding in findings)


def reject_blocked_writing(content: str) -> None:
    blocking = [finding for finding in review_natural_writing(content) if finding.severity == "block"]
    if blocking:
        raise EditorialRejection(blocking[0].message)


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
    reject_blocked_writing(content)
    if original and not article.get("is_curiosity"):
        similarity = SequenceMatcher(None, content[:4000].lower(), original[:4000].lower()).ratio()
        if similarity > float(os.getenv("SIMILARITY_THRESHOLD", "0.35")):
            raise EditorialRejection("Conteudo muito similar ao original")
    if not sources_list(article.get("sources")):
        raise EditorialRejection("Fonte verificavel obrigatoria")
    if article.get("region", "ms") != "ms":
        raise EditorialRejection("A publicação automática aceita apenas pauta local de Mato Grosso do Sul")
    source = sources_list(article.get("sources"))[0]
    locality = local_story_decision(
        source_url=source["url"],
        title=article["title"],
        summary=article.get("summary") or "",
        body=article.get("content") or "",
    )
    if locality == "reject":
        raise EditorialRejection("Fonte fora da política editorial local")
    if locality == "review":
        raise EditorialRejection("Relevância para Mato Grosso do Sul não comprovada; exige revisão humana")
    # Filtros de palavras/sensibilidade desativados — portal publica fatos sem censura (decisão editorial).
    # Mantém apenas dedup e validações estruturais; não rejeita por termo.
