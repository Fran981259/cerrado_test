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
                       attribution: str,
                       related_sources: list = None) -> Dict:
        """Reescreve artigo com voz do repórter — versão PROFISSIONAL longa e cruzada."""
        
        title = article.get('title_pt') or article.get('title', '')
        summary = article.get('summary_pt') or article.get('summary', '')
        source = article.get('source', 'Portal de Notícias')
        source_url = article.get('url', '')
        body = article.get('body', '') or ''

        # Fontes relacionadas para cruzamento
        related_text = ""
        if related_sources:
            related_text = "\nOUTRAS FONTES SOBRE O MESMO FATO (cruze informações):\n"
            for i, rs in enumerate(related_sources[:3], 1):
                related_text += f"{i}. {rs.get('title','')} — {rs.get('source','')} ({rs.get('url','')})\n   Resumo: {rs.get('summary','')[:200]}\n"

        body_text = ""
        if body:
            paragraphs = [p for p in body.split("\n\n") if p.strip()][:12]
            body_text = "\n".join(f"- {p}" for p in paragraphs)
            body_text = f"\n\nCONTEXTO APURADO NO PORTAL (use como base factual; reescreva com APURAÇÃO PRÓPRIA, NÃO copie):\n{body_text}"

        user_prompt = f"""Reescreva esta notícia em Português Brasileiro com padrão PROFISSIONAL, COMPLETO e LONGO.

TÍTULO ORIGINAL: {title}
LEAD (resumo): {summary}
FONTE PRINCIPAL: {source} — {source_url}
{body_text}
{related_text}
INSTRUÇÕES OBRIGATÓRIAS (REGRA DO SISTEMA):
1. Reescreva completamente (paráfrase total, NÃO cópia) — apuração própria
2. Use o CONTEXTO APURADO acima para dar densidade, precisão e riqueza factual ao texto (fatos, números, citações)
3. PESQUISE E CRUZE as outras fontes listadas acima; confronte dados, confirme fatos e complemente lacunas
4. Escreva matéria LONGA e COMPLETA: 700-900 palavras (mínimo 700)
5. Estruture profissionalmente: LEAD forte (o que/quem/quando/onde/por quê) → CONTEXTO/HISTÓRICO → DESENVOLVIMENTO com dados/números → ANÁLISE/IMPACTO para Mato Grosso do Sul → FECHAMENTO com desdobramentos
6. Inclua dados, estatísticas, citações de autoridades ou especialistas (quando faltar, contextualize com base nas fontes)
7. Use sua voz editorial característica, linguagem clara e fluida
8. Cite todas as fontes consultadas ao longo do texto e no rodapé
9. Termine com: {attribution}
10. NÃO invente fatos — se faltar dado, diga "segundo apuração" ou "ainda não divulgado"

REESCRITA LONGA (700-900 palavras):"""
        
        rewritten = self.complete(
            prompt=user_prompt,
            system_prompt=reporter_prompt,
            max_tokens=3000,
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
