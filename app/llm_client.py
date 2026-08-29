"""
Cliente LLM — Atualiza Brasil
Integração com OpenRouter (modelos FREE).
"""

import os
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# MODELOS FREE DISPONÍVEIS NO OPENROUTER (2026-08)
# ============================================================
FREE_MODELS = {
    "general": "inclusionai/ling-3.0-flash-fin:free",
    "fast": "dots-studio/dots-3-note-preview:free",
    "reasoning": "inclusionai/ling-3.0-flash-fin:free",
    "translation": "inclusionai/ling-3.0-flash-fin:free",
    "code": "inclusionai/ling-3.0-flash-fin:free",
    "creative": "dots-studio/dots-3-note-preview:free",
    "tech": "inclusionai/ling-3.0-flash-fin:free",
    "economy": "inclusionai/ling-3.0-flash-fin:free",
    "sports": "inclusionai/ling-3.0-flash-fin:free",
    "general_news": "inclusionai/ling-3.0-flash-fin:free",
}


class LLMClient:
    """Cliente para interação com LLMs via OpenRouter (FREE)."""
    
    def __init__(self, api_key: Optional[str] = None, 
                 model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("LLM_MODEL") or FREE_MODELS["general"]
        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout = 120.0
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY não configurada")
        else:
            logger.info(f"LLM Client inicializado - Modelo: {self.model}")
    
    def complete(self, prompt: str, system_prompt: str = "",
                 max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """Envia prompt ao LLM e retorna resposta."""
        if not self.api_key:
            logger.error("API key não configurada")
            return ""
        
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
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://atualizabrasil.news",
            "X-Title": "Atualiza Brasil",
        }
        
        try:
            with requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.timeout,
            ) as response:
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        
        except requests.HTTPError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e.response.text[:200]}")
            return ""
        except Exception as e:
            logger.error(f"Erro ao chamar LLM: {e}")
            return ""
    
    def rewrite_article(self, article: Dict, 
                        reporter_prompt: str,
                        attribution: str,
                        category: str = "general") -> Dict:
        """Reescreve artigo com a voz do repórter."""
        
        # Escolhe modelo baseado na categoria
        model = FREE_MODELS.get(category, FREE_MODELS["general_news"])
        
        title = article.get('title_pt') or article.get('title', '')
        summary = article.get('summary_pt') or article.get('summary', '')
        source = article.get('source', 'Portal de Notícias')
        source_url = article.get('url', '')
        
        user_prompt = f"""Reescreva a seguinte notícia em Português Brasileiro com sua voz editorial.

TÍTULO: {title}
CONTEÚDO: {summary}
FONTE: {source}
URL ORIGINAL: {source_url}

INSTRUÇÕES:
1. Reescreva completamente (paráfrase, NÃO cópia)
2. Mantenha os fatos principais
3. Adicione contexto para o público brasileiro
4. Use a voz editorial do repórter
5. Termine com: {attribution}
6. Limite: 400-600 palavras

REESCRITA:"""
        
        rewritten = self.complete(
            prompt=user_prompt,
            system_prompt=reporter_prompt,
            max_tokens=1500,
            temperature=0.7,
        )
        
        return {
            **article,
            'rewritten_content': rewritten,
            'rewritten_at': datetime.utcnow().isoformat(),
            'llm_model': model,
        }
    
    def translate_to_pt_br(self, text: str, source_lang: str = "en") -> str:
        """Traduz texto para Português Brasileiro."""
        system_prompt = f"""Você é um tradutor especializado em jornalismo internacional.
Traduza o texto de {source_lang} para Português Brasileiro (pt-BR).

REGRAS:
- Use linguagem natural e fluente
- Mantenha termos técnicos (IA, API, etc.)
- Preserve nomes próprios
- Adapte expressões idiomáticas
- Mantenha tom jornalístico"""
        
        return self.complete(
            prompt=f"Traduza para pt-BR:\n\n{text}",
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.3,
        )


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
    
    KEEP_ORIGINAL = [
        "OpenAI", "ChatGPT", "GPT-4", "GPT-5",
        "Microsoft", "Google", "Apple", "Amazon", "Meta", "Tesla",
        "iPhone", "Android",
        "NASDAQ", "Dow Jones", "S&P 500", "Wall Street",
        "Bitcoin", "Ethereum",
    ]
    
    @classmethod
    def apply(cls, text: str) -> str:
        """Aplica glossário ao texto traduzido."""
        result = text
        for en, pt in cls.TERMS.items():
            import re
            pattern = re.compile(re.escape(en), re.IGNORECASE)
            result = pattern.sub(pt, result)
        return result


def test_llm_connection():
    """Testa conexão com OpenRouter usando modelo FREE."""
    import os
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY não configurada")
        return False
    
    client = LLMClient()
    
    print(f"Testando modelo: {client.model}")
    print("Aguarde (modelos free podem demorar)...")
    
    response = client.complete(
        prompt="Responda em UMA frase: o que é OpenRouter?",
        system_prompt="Seja conciso.",
        max_tokens=100,
        temperature=0.5,
    )
    
    if response:
        print(f"✅ Resposta: {response}")
        return True
    else:
        print("❌ Sem resposta")
        return False
