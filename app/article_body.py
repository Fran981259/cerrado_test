"""Extração e limpeza do corpo textual de artigos."""

import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup


class ArticleBodyMixin:
    """Extrai corpo, fallback e limpeza textual de artigos."""

    _BOILERPLATE: re.Pattern

    # Corpo do texto
    # ----------------------------------------------------------
    def _extract_body(self, soup: BeautifulSoup, jsonld: Optional[Dict]) -> str:
        # 1) JSON-LD articleBody (fonte mais confiável)
        if jsonld and jsonld.get("articleBody"):
            body = self._clean_text(jsonld["articleBody"])
            if len(body.split()) >= 30:
                return body

        # 2) Heurística: container com mais texto (evita pegar <article> de relacionados)
        # Avalia candidatos específicos primeiro
        scored = []
        # id="single" é o container principal da Agência MS
        for sel in [
            "#single",
            "#content",
            "#post",
            ".post",
            ".entry-content",
            ".post-content",
            ".article-content",
            ".single-content",
            ".noticia-conteudo",
            ".conteudo",
            ".texto",
            "main",
            "[role=main]",
        ]:
            el = soup.select_one(sel)
            if el:
                txt = self._paragraphs_to_text(el)
                words = len(txt.split())
                if words >= 40:
                    scored.append((words, txt))
        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            return scored[0][1]

        # 3) Melhor <article> por volume de texto (não o primeiro)
        articles = soup.find_all("article")
        if articles:
            best = None
            best_words = 0
            for art in articles:
                txt = self._paragraphs_to_text(art)
                w = len(txt.split())
                if w > best_words:
                    best_words = w
                    best = txt
            if best and best_words >= 40:
                return best

        return ""

    def _paragraphs_to_text(self, container) -> str:
        parts = []
        for el in container.find_all(["p", "h2", "h3", "li"]):
            text = self._clean_text(el.get_text(" ", strip=True))
            if not text or len(text.split()) < 3:
                continue
            if self._BOILERPLATE.search(text) and len(text.split()) < 12:
                continue
            if text in parts:
                continue
            parts.append(text)
        return "\n\n".join(parts)

    def _paragraph_fallback(self, soup: BeautifulSoup) -> str:
        """Reconstrói parágrafos do documento inteiro quando faltam seletores."""
        parts = []
        for el in soup.find_all("p"):
            text = self._clean_text(el.get_text(" ", strip=True))
            if not text or len(text.split()) < 3:
                continue
            if self._BOILERPLATE.search(text) and len(text.split()) < 12:
                continue
            parts.append(text)
        # limita a não' duplicar parágrafos idênticos consecutivos
        deduped: List[str] = []
        for p in parts:
            if not deduped or p != deduped[-1]:
                deduped.append(p)
        return "\n\n".join(deduped)

    # ----------------------------------------------------------
    # Limpeza de texto
    # ----------------------------------------------------------
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
        # remove espaços duplicados, quebras e normaliza pontuação
        text = re.sub(r"[\r\n\t]+", " ", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = text.replace("\u00a0", " ").strip()
        # remove prefixos repetidos de categoria/nome do portal presos ao texto
        text = self._dedupe_title(text)
        return text

    def _dedupe_title(self, text: str) -> str:
        """Remove repetições anômalas como 'XXX' + 'XXX' (prefixo colado ao texto)."""
        if not text:
            return text
        # ex.: "Utilidade PúblicaMato Grosso..." -> "Mato Grosso..."
        text = re.sub(
            r"^(Utilidade Pública|Notícias|Geral|Política|Economia|Saúde|"
            r"Esporte|Cultura|Educação|Agronegócio|Segurança)("
            r"(?=[A-ZÁÉÍÓÚÂÊÔÀ]))",
            "",
            text,
            flags=re.IGNORECASE,
        )
        # remove sufixo de veículo grudado no título ("Notícia - O Estado Online")
        text = re.sub(
            r"\s*[-–—|/]\s*(O Estado Online|G1( MS)?|MS News|MS Todo Dia|"
            r"Agência( de Notícias)? MS|MS Notícias|Correio do Estado|"
            r"Campo Grande News|UOL)\s*$",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\b(\w{4,})\s+\1\b", r"\1", text, flags=re.IGNORECASE)
        return text.strip()

    def _is_dirty_lead(self, lead: str) -> bool:
        if not lead or len(lead.strip()) < 40:
            return True
        # concatenação sem espaço: minúscula seguida de maiúscula
        if re.search(r"[a-záéíóúâêôãç][A-ZÁÉÍÓÚÂÊÔÃÇ]", lead):
            return True
        if "Utilidade Pública" in lead and "Mato" in lead and "PúblicaMato" in lead.replace(" ", ""):
            return True
        # lead com prefixo de categoria colado ou repetição grosseira
        if lead.count("Utilidade Pública") >= 1 and len(lead.split()) > 30:
            return True
        return False

    def _is_generic_lead(self, lead: str) -> bool:
        if not lead:
            return True
        low = lead.lower()
        generics = [
            "veja notícias em campo grande",
            "últimas notícias de economia, política",
            "o estado online - últimas",
            "acompanhe as últimas notícias",
            "fique por dentro",
        ]
        return any(g in low for g in generics)

    def _pick_first(self, *values) -> str:
        for v in values:
            if v and str(v).strip():
                return str(v).strip()
        return ""
