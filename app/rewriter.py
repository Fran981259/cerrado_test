"""Agente Reescritor — Portal Cerrado."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from app.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReporterProfile:
    """Perfil de um repórter digital."""
    
    def __init__(self, config: Dict[str, Any]):
        self.slug = config['slug']
        self.display_name = config['display_name']
        self.role = config['role']
        self.specialties = config['specialties']
        self.voice_profile = config['voice_profile']
        self.prompt_system = config['prompt_system']
        self.attribution = config['attribution']
        
    def get_system_prompt(self) -> str:
        """Gera o prompt de sistema para o LLM."""
        base_prompt = self.prompt_system['role_description']
        
        # Adicionar regras
        rules_text = "\n".join([f"- {rule}" for rule in self.prompt_system['rules']])
        
        # Adicionar informações de voz
        voice_info = f"""
VOZ EDITORIAL:
- Tom: {self.voice_profile['tone']}
- Linguagem: {self.voice_profile['language']}
- Palavras-chave típicas: {', '.join(self.voice_profile['key_words'])}
- Gancho de abertura típico: {self.voice_profile['opening_hook']}
"""
        
        return f"""{base_prompt}

{voice_info}

REGRAS EDITORIAIS:
{rules_text}

ASSINATURA:
{self.attribution}"""


class ArticleRewriter:
    """Agente que reescreve artigos com a voz do repórter."""
    
    def __init__(self, reporter: ReporterProfile, llm_client: Optional[LLMClient] = None):
        self.reporter = reporter
        self.llm = llm_client or LLMClient()
        
    def rewrite(self, raw_article: Dict[str, Any]) -> Dict[str, Any]:
        """Reescreve um artigo usando a voz do repórter."""
        rewritten_content = self._generate_rewritten_content(raw_article)
        
        # Construir artigo final
        final_article = {
            'title': raw_article.get('title', ''),
            'content': rewritten_content,
            'source_urls': [raw_article.get('url', '')],
            'source_names': [self._extract_source_name(raw_article.get('url', ''))],
            'reporter_slug': self.reporter.slug,
            'reporter_name': self.reporter.display_name,
            'category': self.reporter.role,
            'attribution': self.reporter.attribution,
            'original_summary': raw_article.get('summary', ''),
            'rewritten_at': datetime.utcnow().isoformat(),
            'llm_provider': getattr(self.llm, 'provider', None),
            'llm_model': getattr(self.llm, 'model', None),
        }
        
        return final_article
    
    def _generate_rewritten_content(self, raw: Dict[str, Any]) -> str:
        """Reescreve com LLM; sem chave, não inventa texto local."""
        if not getattr(self.llm, 'api_key', None):
            title = raw.get('title', '')
            logger.warning(f"[REWRITER] sem LLM para '{title[:50]}' — conteúdo vazio por design")
            return ""

        title = raw.get('title', '')
        summary = raw.get('summary', '')
        body = raw.get('body', '')
        url = raw.get('url', '')
        source = raw.get('source', 'Portal de Notícias')

        prompt = f"""Reescreva esta notícia em Português Brasileiro com voz editorial humana, sem cara de IA.

TÍTULO: {title}
LEAD: {summary}
FONTE: {source}
URL: {url}
CORPO BRUTO:\n{body}

REQUISITOS:
- Abra com o fato principal e um dado concreto.
- Use parágrafos curtos e ritmo variado.
- Evite clichês, fórmulas repetidas e frases genéricas.
- Não use rótulos de seção, listas ou blocos de links.
- Não invente fatos.
- Escreva entre 700 e 900 palavras.
- Termine com a assinatura da redação.

REESCRITA:"""

        return self.llm.complete(
            prompt=prompt,
            system_prompt=self.reporter.get_system_prompt(),
            max_tokens=3000,
            temperature=0.65,
        )
    
    def _extract_source_name(self, url: str) -> str:
        """Extrai o nome do portal da URL."""
        if 'msnews.com.br' in url:
            return 'MS News'
        elif 'mstododia.com.br' in url:
            return 'MS Todo Dia'
        elif 'g1.globo.com' in url:
            return 'G1 MS'
        elif 'agenciadenoticias.ms.gov.br' in url:
            return 'Agência de Notícias MS'
        elif 'oestadoonline.com.br' in url:
            return 'O Estado Online'
        elif 'msnoticias.com.br' in url:
            return 'MS Notícias'
        elif 'msbigeconomico.com.br' in url:
            return 'MS Big Econômico'
        elif 'hoye.com.ms' in url:
            return 'Hoye'
        return 'Portal de Notícias'


# Carregamento de configuração dos repórteres
def load_reporters_config(path: str = "config/reporters.yml") -> Dict[str, ReporterProfile]:
    """Carrega a configuração de todos os repórteres."""
    import yaml
    
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    reporters = {}
    for slug, data in config['reporters'].items():
        # garante slug dentro do dict (yaml usa slug como chave, não como campo)
        data = dict(data)
        data['slug'] = slug
        if 'display_name' not in data and 'name' in data:
            data['display_name'] = data['name']
        reporters[slug] = ReporterProfile(data)
        
    return reporters


def get_reporter_for_category(category: str) -> Optional[ReporterProfile]:
    """Retorna o repórter adequado para uma categoria."""
    reporters = load_reporters_config()
    
    for reporter in reporters.values():
        if reporter.role == category:
            return reporter
            
    return None


def rewrite_for_category(category: str, raw_article: Dict[str, Any]) -> Dict[str, Any]:
    """Reescreve um artigo para uma categoria específica."""
    reporter = get_reporter_for_category(category)
    
    if not reporter:
        logger.warning(f"Nenhum repórter encontrado para categoria: {category}")
        return {}
        
    rewriter = ArticleRewriter(reporter)
    return rewriter.rewrite(raw_article)
