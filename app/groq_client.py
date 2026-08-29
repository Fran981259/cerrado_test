"""
Cliente Groq — Atualiza Brasil
API gratuita com limites generosos.

Modelos disponíveis:
- qwen/qwen3.8-27b (disponível free)
- allam-2-7b

Limites FREE: 14 req/min, 5760 req/dia
"""

import os
import logging
import requests
from typing import Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqClient:
    """Cliente Groq para reescrita e tradução."""
    
    BASE_URL = "https://api.groq.com/openai/v1"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY não configurada")
        else:
            logger.info(f"Groq Client OK - Modelo: {self.model}")
    
    def complete(self, prompt: str, system_prompt: str = "",
                 max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """Envia prompt ao Groq e retorna resposta."""
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
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro Groq {e.response.status_code}: {e.response.text[:200]}")
            return ""
        except Exception as e:
            logger.error(f"Erro: {e}")
            return ""
    
    def rewrite_article(self, article: Dict, 
                       reporter_prompt: str,
                       attribution: str) -> Dict:
        """Reescreve artigo com voz do repórter."""
        
        title = article.get('title_pt') or article.get('title', '')
        summary = article.get('summary_pt') or article.get('summary', '')
        source = article.get('source', 'Portal de Notícias')
        source_url = article.get('url', '')
        
        user_prompt = f"""Reescreva esta notícia em Português Brasileiro com sua voz editorial.

TÍTULO ORIGINAL: {title}
CONTEÚDO: {summary}
FONTE: {source}
URL: {source_url}

INSTRUÇÕES:
1. Reescreva completamente (paráfrase, NÃO cópia)
2. Mantenha os fatos principais
3. Adicione contexto para o público brasileiro
4. Use sua voz editorial característica
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
            'llm_provider': 'groq',
            'llm_model': self.model,
        }
    
    def translate_to_pt_br(self, text: str, source_lang: str = "en") -> str:
        """Traduz texto para Português Brasileiro."""
        
        system_prompt = f"""Você é tradutor especializado em jornalismo.
Traduza o texto de {source_lang} para Português Brasileiro (pt-BR).

REGRAS:
- Linguagem natural e fluente
- Mantenha termos técnicos universais (IA, API, etc.)
- Preserve nomes próprios
- Adapte expressões idiomáticas
- Mantenha tom jornalístico"""
        
        return self.complete(
            prompt=f"Traduza para pt-BR:\n\n{text}",
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.3,
        )


# Instância global
groq_client = GroqClient()


def test_groq_connection() -> bool:
    """Testa conexão com Groq."""
    client = GroqClient()
    
    if not client.api_key:
        print("❌ GROQ_API_KEY não configurada")
        return False
    
    print(f"Testando Groq com modelo: {client.model}")
    print("Aguarde...")
    
    response = client.complete(
        prompt="Responda em UMA frase: o que é Groq?",
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
