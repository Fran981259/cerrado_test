"""
Cliente LLM do Portal Cerrado.
Suporta apenas Gemini e OpenAI.
"""

import logging
import os
from datetime import datetime
from typing import Dict, Optional

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS = {"gemini", "openai"}


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
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        return "gemini"

    def _resolve_api_key(self) -> Optional[str]:
        if self.provider == "gemini":
            return os.getenv("GEMINI_API_KEY")
        return os.getenv("OPENAI_API_KEY")

    def _resolve_model(self) -> str:
        if self.provider == "gemini":
            return os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def complete(self, prompt: str, system_prompt: str = "", max_tokens: int = 2000, temperature: float = 0.7) -> str:
        if not self.api_key:
            logger.error("LLM API key não configurada")
            return ""

        if self.provider == "gemini":
            return self._complete_gemini(prompt, system_prompt, max_tokens, temperature)
        return self._complete_openai(prompt, system_prompt, max_tokens, temperature)

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
            response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.HTTPError as e:
            logger.error("Erro OpenAI %s: %s", e.response.status_code, e.response.text[:200])
            return ""
        except Exception as e:
            logger.error("Erro ao chamar OpenAI: %s", e)
            return ""

    def _complete_gemini(self, prompt: str, system_prompt: str, max_tokens: int, temperature: float) -> str:
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                params={"key": self.api_key},
                json=payload,
                timeout=self.timeout,
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
            logger.error("Erro Gemini %s: %s", e.response.status_code, e.response.text[:200])
            return ""
        except Exception as e:
            logger.error("Erro ao chamar Gemini: %s", e)
            return ""

    def rewrite_article(self, article: Dict, reporter_prompt: str, attribution: str, related_sources: list = None) -> Dict:
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

        user_prompt = f"""Reescreva esta notícia em Português Brasileiro com padrão de jornal profissional.

TÍTULO ORIGINAL: {title}
LEAD (resumo): {summary}
FONTE PRINCIPAL: {source} — {source_url}
{body_text}
{related_text}

REQUISITOS EDITORIAIS:
1. Reescreva completamente, sem copiar frases da fonte.
2. Use o contexto factual para ampliar precisão e densidade.
3. Cruze com as fontes relacionadas quando existirem.
4. Escreva 700 a 900 palavras.
5. Abra com um fato concreto, sem lead genérico.
6. Use parágrafos curtos, 2 a 3 frases, com ritmo variado.
7. Alterne frases curtas e médias; corte repetições e lugares-comuns.
8. Evite linguagem engessada, clichês e aparência de texto gerado por IA.
9. Não invente fatos, não use listas, não use blocos de links, não use URLs no corpo.
10. Conclua com desdobramento concreto.
11. Termine com: {attribution}

REESCRITA:"""

        rewritten = self.complete(prompt=user_prompt, system_prompt=reporter_prompt, max_tokens=3000, temperature=0.65)
        return {**article, "rewritten_content": rewritten, "rewritten_at": datetime.utcnow().isoformat(), "llm_provider": self.provider, "llm_model": self.model}

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
    client = LLMClient(provider=provider)
    if not client.api_key:
        print(f"❌ API key não configurada para {client.provider}")
        return False

    response = client.complete(prompt="Responda em UMA frase: o que é jornalismo local?", system_prompt="Seja conciso.", max_tokens=100, temperature=0.3)
    if response:
        print(f"✅ {client.provider}: {response}")
        return True
    print(f"❌ Sem resposta de {client.provider}")
    return False
