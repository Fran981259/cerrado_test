"""
Tradutor de Notícias — Atualiza Brasil
Tradução para Português Brasileiro usando LLM.
"""

from app.llm_client import LLMClient, TranslationGlossary
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsTranslator:
    """Tradutor de notícias para pt-BR."""
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
    
    def translate(self, article: Dict) -> Dict:
        """
        Traduz artigo para pt-BR.
        
        Args:
            article: Artigo com campos title, summary, source_lang
            
        Returns:
            Artigo com campos title_pt, summary_pt traduzidos
        """
        source_lang = article.get('source_lang', 'en')
        
        # Se já está em pt-BR, não traduz
        if source_lang == 'pt-BR':
            article['title_pt'] = article['title']
            article['summary_pt'] = article['summary']
            article['translation_method'] = 'none'
            return article
        
        # Traduz usando LLM
        try:
            return self._translate_with_llm(article)
        except Exception as e:
            logger.error(f"Erro na tradução: {e}")
            return self._translate_fallback(article)
    
    def _translate_with_llm(self, article: Dict) -> Dict:
        """Traduz usando LLM com prompt especializado."""
        
        system_prompt = """Você é tradutor especializado em jornalismo.
Traduza o texto para Português Brasileiro (pt-BR).

REGRAS:
1. Linguagem natural, não traduza literalmente
2. Mantenha termos técnicos universais (IA, API, etc.)
3. Preserve nomes próprios
4. Mantenha tom jornalístico
5. Preserve dados numéricos e datas
6. Use vírgulas e acentos corretamente"""

        # Traduz título
        title = article.get('title', '')
        title_pt = self.llm.complete(
            prompt=f"Traduza para pt-BR:\n\n{title}",
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.3,
        )
        
        # Traduz conteúdo
        summary = article.get('summary', '')
        summary_pt = self.llm.complete(
            prompt=f"Traduza para pt-BR:\n\n{summary}",
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.3,
        )
        
        # Aplica glossário
        title_pt = TranslationGlossary.apply(title_pt)
        summary_pt = TranslationGlossary.apply(summary_pt)
        
        return {
            **article,
            'title_pt': title_pt or title,
            'summary_pt': summary_pt or summary,
            'translated_at': article.get('translated_at') or __import__('datetime').datetime.utcnow().isoformat(),
            'translation_method': 'llm',
            'llm_model': self.llm.model,
        }
    
    def _translate_fallback(self, article: Dict) -> Dict:
        """Fallback quando LLM não disponível."""
        logger.warning("Usando tradução fallback (sem LLM)")
        return {
            **article,
            'title_pt': article['title'],
            'summary_pt': article['summary'],
            'translated_at': __import__('datetime').datetime.utcnow().isoformat(),
            'translation_method': 'fallback',
            'needs_review': True,
        }
