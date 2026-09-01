"""
Agente Reescritor — Atualiza Brasil
Responsável por reescrever notícias com a voz de cada repórter digital.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

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
    
    def __init__(self, reporter: ReporterProfile):
        self.reporter = reporter
        
    def rewrite(self, raw_article: Dict[str, Any]) -> Dict[str, Any]:
        """Reescreve um artigo usando a voz do repórter."""
        
        # Simulação da reescrita (em produção, usar LLM via API)
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
        }
        
        return final_article
    
    def _generate_rewritten_content(self, raw: Dict[str, Any]) -> str:
        """Gera conteúdo PROFISSIONAL longo (fallback quando LLM offline)."""

        title = raw.get('title', '')
        summary = raw.get('summary', '')
        source_url = raw.get('url', '')
        source_name = self._extract_source_name(source_url)
        related = raw.get('related_sources', [])
        body = raw.get('body', '') or ''

        # Usa os parágrafos reais apurados no portal como base factual
        paragraphs = [p for p in (body or "").split("\n\n") if p.strip()][:12]
        contexto_fatos = ""
        if paragraphs:
            contexto_fatos = "\n\nAPURAÇÃO — " + " ".join(paragraphs[:6])
        elif summary:
            contexto_fatos = f"\n\nAPURAÇÃO — {summary}"

        # Monta bloco de fontes cruzadas
        fontes_cruzadas = ""
        if related:
            fontes_cruzadas = "\n\nFontes cruzadas consultadas:\n"
            for rs in related[:3]:
                fontes_cruzadas += f"- {rs.get('title','')} — {rs.get('source','')} ({rs.get('url','')})\n"
        else:
            fontes_cruzadas = f"\n\nEm apuração complementar, nossa equipe cruzou dados com outros portais regionais para ampliar o contexto.\n"

        # Fallback sem LLM: usa APENAS conteúdo apurado, sem boilerplate genérico repetido.
        # Se não há corpo apurado suficiente, retorna vazio para retry (evita thin content AdSense)
        if not contexto_fatos and not summary:
            logger.warning(f"[REWRITER] Fallback sem LLM e sem corpo para '{title[:50]}' — abortando para retry")
            return ""
        if paragraphs and len(" ".join(paragraphs).split()) < 80 and not summary:
            logger.warning(f"[REWRITER] Corpo muito curto ({len(' '.join(paragraphs).split())} palavras) — abortando fallback")
            return ""

        # Monta fallback variado por artigo, usando apenas fatos apurados + lead
        # Não repete boilerplate verbatim; cada artigo tem lead + apuração + fontes cruzadas + assinatura
        partes = [title, "", f"LEAD — {summary}"]
        if contexto_fatos:
            partes.append(contexto_fatos)
        # Desenvolvimento com base no summary expandido, sem frase genérica fixa
        if summary:
            partes.append(f"APURAÇÃO — {summary}")
        if fontes_cruzadas and related:
            partes.append(fontes_cruzadas.strip())
        partes.append(f"Fontes consultadas: {source_name} ({source_url}){''.join([f', {r.get('source','')} ({r.get('url','')})' for r in related[:3]])}")
        partes.append(self.reporter.attribution)
        # Filtra vazios e junta
        content = "\n\n".join(p for p in partes if p and p.strip())
        # Se ainda ficou curto (<200 palavras), não publica — deixa para retry com LLM
        if len(content.split()) < 200:
            logger.warning(f"[REWRITER] Fallback gerou apenas {len(content.split())} palavras para '{title[:40]}' — considerado curto, abortando")
            return ""
        return content
        
        return content
    
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


# Exemplo de uso
if __name__ == "__main__":
    # Teste rápido
    sample_article = {
        'title': 'Nova tecnologia agrícola aumenta produtividade em 30%',
        'url': 'https://www.msnews.com.br/noticia/tecnologia-agricola',
        'summary': 'Pesquisadores de Campo Grande anunciam nova técnica'
    }
    
    reporters = load_reporters_config()
    tech_reporter = reporters['enzo.bianchi']
    rewriter = ArticleRewriter(tech_reporter)
    
    result = rewriter.rewrite(sample_article)
    print(json.dumps(result, indent=2, ensure_ascii=False))