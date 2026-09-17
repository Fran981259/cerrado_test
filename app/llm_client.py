"""
Cliente LLM do Portal Cerrado.
Suporta apenas Gemini e OpenAI.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, Optional

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS = {"gemini", "openai", "groq"}


class LLMClient:
    """Cliente para Gemini ou OpenAI via HTTP."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, provider: Optional[str] = None):
        self.provider = self._resolve_provider(provider)
        self.api_key = api_key or self._resolve_api_key()
        self.model = model or self._resolve_model()
        self.timeout = 120.0

        if not self.api_key:
            logger.warning("LLM API key não configurada para %s", self.provider)
        else:
            logger.info("LLM Client inicializado - provider=%s model=%s", self.provider, self.model)

    def _resolve_provider(self, provider: Optional[str]) -> str:
        value = (provider or os.getenv("LLM_PROVIDER") or "").strip().lower()
        if value in SUPPORTED_PROVIDERS:
            return value
        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        if os.getenv("GROQ_API_KEY"):
            return "groq"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        return "gemini"

    def _resolve_api_key(self) -> Optional[str]:
        if self.provider == "gemini":
            return os.getenv("GEMINI_API_KEY")
        if self.provider == "groq":
            return os.getenv("GROQ_API_KEY")
        return os.getenv("OPENAI_API_KEY")

    def _resolve_model(self) -> str:
        if self.provider == "gemini":
            return os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
        if self.provider == "groq":
            return os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def complete(self, prompt: str, system_prompt: str = "", max_tokens: int = 2000, temperature: float = 0.7) -> str:
        if not self.api_key:
            logger.error("LLM API key não configurada")
            return ""

        if self.provider == "gemini":
            return self._complete_gemini(prompt, system_prompt, max_tokens, temperature)
        return self._complete_openai(prompt, system_prompt, max_tokens, temperature)

    RETRYABLE_STATUS = {429, 500, 502, 503}
    MAX_ATTEMPTS = 6

    def _post_with_backoff(self, url: str, payload: Dict, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> requests.Response:
        """POST com retry e backoff exponencial rigoroso para erros transientes (429/5xx)."""
        import random
        import time

        last_exc = None
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                response = requests.post(url, json=payload, headers=headers, params=params, timeout=self.timeout)
                if response.status_code in self.RETRYABLE_STATUS and attempt < self.MAX_ATTEMPTS:
                    wait = 10 * (2 ** (attempt - 1)) + random.uniform(0, 3)
                    logger.warning("LLM HTTP %s (tentativa %d/%d). Aguardando %.1fs...", response.status_code, attempt, self.MAX_ATTEMPTS, wait)
                    time.sleep(wait)
                    continue
                return response
            except (requests.ConnectionError, requests.Timeout) as e:
                last_exc = e
                if attempt < self.MAX_ATTEMPTS:
                    wait = 10 * (2 ** (attempt - 1)) + random.uniform(0, 3)
                    logger.warning("LLM erro de rede %s (tentativa %d/%d). Aguardando %.1fs...", type(e).__name__, attempt, self.MAX_ATTEMPTS, wait)
                    time.sleep(wait)
                    continue
                raise
        raise last_exc if last_exc else requests.HTTPError("LLM sem resposta após retries")

    def _complete_openai(self, prompt: str, system_prompt: str, max_tokens: int, temperature: float) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        try:
            url = "https://api.groq.com/openai/v1/chat/completions" if self.provider == "groq" else "https://api.openai.com/v1/chat/completions"
            response = self._post_with_backoff(url, payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.HTTPError as e:
            logger.error("Erro OpenAI HTTP %s", e.response.status_code if e.response is not None else "?")
            return ""
        except Exception as e:
            logger.error("Erro ao chamar OpenAI (%s)", type(e).__name__)
            return ""

    def _complete_gemini(self, prompt: str, system_prompt: str, max_tokens: int, temperature: float) -> str:
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        try:
            response = self._post_with_backoff(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                payload,
                params={"key": self.api_key},
            )
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return ""
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts).strip()
            return text
        except requests.HTTPError as e:
            logger.error("Erro Gemini HTTP %s", e.response.status_code if e.response is not None else "?")
            return ""
        except Exception as e:
            logger.error("Erro ao chamar Gemini (%s)", type(e).__name__)
            return ""

    def rewrite_article(self, article: Dict, reporter_prompt: str, attribution: str, related_sources: list = None, **_: object) -> Dict:
        title = article.get("title_pt") or article.get("title", "")
        summary = article.get("summary_pt") or article.get("summary", "")
        source = article.get("source", "Portal de Notícias")
        source_url = article.get("url", "")
        body = article.get("body", "") or ""

        related_text = ""
        if related_sources:
            related_text = "\nOUTRAS FONTES SOBRE O MESMO FATO:\n"
            for i, rs in enumerate(related_sources[:3], 1):
                related_text += f"{i}. {rs.get('title','')} — {rs.get('source','')} ({rs.get('url','')})\n   Resumo: {rs.get('summary','')[:200]}\n"

        body_text = ""
        if body:
            paragraphs = [p for p in body.split("\n\n") if p.strip()][:12]
            body_text = "\n".join(f"- {p}" for p in paragraphs)
            body_text = f"\n\nCONTEXTO APURADO (use como base factual; reescreva do zero, sem copiar):\n{body_text}"

        user_prompt = f"""Reescreva esta notícia em Português Brasileiro com padrão de jornal profissional. IMPORTANTE: TRADUZA E ADAPTE O TÍTULO E O RESUMO PARA PT-BR!

TÍTULO ORIGINAL: {title}
LEAD (resumo): {summary}
FONTE PRINCIPAL: {source} — {source_url}
{body_text}
{related_text}

REQUISITOS EDITORIAIS:
1. Reescreva completamente, sem copiar frases da fonte. O idioma OBRIGATÓRIO é Português do Brasil.
2. Use o contexto factual para ampliar precisão e densidade.
3. Cruze com as fontes relacionadas quando existirem.
4. Escreva 700 a 900 palavras no corpo da notícia.
5. Abra com um fato concreto, sem lead genérico.
6. Use parágrafos curtos, 2 a 3 frases, com ritmo variado.
7. Alterne frases curtas e médias; corte repetições e lugares-comuns.
8. Evite linguagem engessada, clichês e aparência de texto gerado por IA.
9. Não invente fatos, não use listas, não use blocos de links, não use URLs no corpo.
10. Conclua com desdobramento concreto.
11. Termine com: {attribution}

A SUA RESPOSTA DEVE SEGUIR EXATAMENTE ESTE FORMATO:

TÍTULO: [Escreva aqui o título em português]
RESUMO: [Escreva aqui o lead/resumo em português]
CORPO:
[Escreva aqui o corpo da notícia reescrita em português]"""

        rewritten = self.complete(prompt=user_prompt, system_prompt=reporter_prompt, max_tokens=5000, temperature=0.65)
        
        # Extrair Título, Resumo e Corpo
        import re
        parsed_title = title
        parsed_summary = summary
        parsed_body = rewritten

        match = re.search(r"TÍTULO:\s*(.*?)\nRESUMO:\s*(.*?)\nCORPO:\s*(.*)", rewritten, re.IGNORECASE | re.DOTALL)
        if match:
            parsed_title = match.group(1).strip()
            parsed_summary = match.group(2).strip()
            parsed_body = match.group(3).strip()
        else:
            # Fallback se o LLM ignorar o formato
            # Tenta limpar as tags TÍTULO:, etc se ele gerou bagunçado
            parsed_body = re.sub(r"^(TÍTULO:|RESUMO:|CORPO:).*\n?", "", rewritten, flags=re.IGNORECASE | re.MULTILINE).strip()

        return {
            **article, 
            "rewritten_title": parsed_title,
            "rewritten_summary": parsed_summary,
            "rewritten_content": parsed_body, 
            "rewritten_at": datetime.now(timezone.utc).isoformat(), 
            "llm_provider": self.provider, 
            "llm_model": self.model
        }

    def translate_to_pt_br(self, text: str, source_lang: str = "en") -> str:
        system_prompt = f"Você é um tradutor especializado em jornalismo. Traduza de {source_lang} para Português Brasileiro (pt-BR) com fluidez natural e tom jornalístico."
        return self.complete(prompt=f"Traduza para pt-BR:\n\n{text}", system_prompt=system_prompt, max_tokens=2000, temperature=0.3)


class TranslationGlossary:
    """Glossário de tradução para garantir consistência."""

    TERMS = {
        "AI": "inteligência artificial",
        "ML": "machine learning",
        "startup": "startup",
        "IPO": "oferta pública inicial (IPO)",
        "CEO": "CEO",
        "layoffs": "demissões em massa",
        "Fed": "Federal Reserve (Banco Central dos EUA)",
        "interest rates": "taxas de juros",
        "inflation": "inflação",
        "GDP": "PIB",
        "recession": "recessão",
        "White House": "Casa Branca",
        "Congress": "Congresso",
        "NATO": "OTAN",
        "WHO": "OMS",
        "FDA": "FDA",
    }

    @classmethod
    def apply(cls, text: str) -> str:
        result = text
        for en, pt in cls.TERMS.items():
            import re

            pattern = re.compile(re.escape(en), re.IGNORECASE)
            result = pattern.sub(pt, result)
        return result


def test_llm_connection(provider: Optional[str] = None) -> bool:
    """Helper manual usado por scripts/test_llm.py; não é parte da suíte pytest."""
    client = LLMClient(provider=provider)
    if not client.api_key:
        return False
    text = client.complete("Responda apenas: ok", max_tokens=10, temperature=0)
    return bool(text.strip())
