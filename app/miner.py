"""
Miner de Notícias Globais — Atualiza Brasil
============================================
Coleta notícias de fontes internacionais, classifica, traduz para pt-BR.

RECURSOS:
- Coleta randomizada (variação entre execuções)
- Classificação por importância e engajamento
- Volume mínimo garantido: 50 matérias/dia
- Atualização a cada 30 minutos
"""

import feedparser
import logging
import hashlib
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

import httpx
import yaml

from app.classifier import NewsClassifier, classify_articles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# CONSTANTES DE VOLUME
# ============================================================
MIN_ARTICLES_PER_DAY = 50  # Mínimo diário
ARTICLES_PER_CYCLE = 3     # ~3 a cada 30 min = 48/dia mínimo
                             # + ajustes = garantido 50+

# Randomização: cada categoria tem chance de ser amostrada
RANDOM_CATEGORY_PROBABILITY = 0.85  # 85% chance de pegar a categoria


class GlobalNewsMiner:
    """
    Agente minerador de notícias globais COM RANDOMIZAÇÃO.
    
    - Cada execução escolhe aleatoriamente quais categorias minerar
    - Cada feed tem chance de ser amostrado ou pulado
    - Garante variedade na pauta diária
    """
    
    def __init__(self, config_path: str = "config/portals_global.yml"):
        self.config = self._load_config(config_path)
        self.classifier = NewsClassifier()
        self.session = httpx.Client(
            timeout=30.0,
            headers={"User-Agent": "AtualizaBrasil-Miner/1.0"}
        )
        self._load_glossary()
    
    def _load_config(self, path: str) -> Dict:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_glossary(self):
        cfg_lang = self.config.get('global_miner', {}).get('language', {})
        self.glossary = cfg_lang.get('glossary', {})
        self.preserve_terms = cfg_lang.get('preserve_terms', [])
    
    def mine_randomized(self) -> List[Dict[str, Any]]:
        """
        Coleta randomizada de notícias.
        
        - Escolhe aleatoriamente quais portais minerar
        - Escolhe aleatoriamente quantos artigos pegar de cada portal
        - Varia a cada execução para evitar repetição
        """
        all_news = []
        portals = self.config.get('global_miner', {}).get('portals', {})
        
        # 1. Embaralha ordem das categorias
        categories = list(portals.keys())
        random.shuffle(categories)
        
        for category in categories:
            # 85% chance de minerar esta categoria nesta execução
            if random.random() > RANDOM_CATEGORY_PROBABILITY:
                logger.debug(f"Pulando categoria: {category}")
                continue
            
            portal_list = portals[category]
            
            # Embaralha portais dentro da categoria
            shuffled_portals = portal_list.copy()
            random.shuffle(shuffled_portals)
            
            # Pega 60-80% dos portais da categoria
            n_portals = max(1, int(len(shuffled_portals) * random.uniform(0.6, 0.8)))
            selected_portals = shuffled_portals[:n_portals]
            
            logger.info(f"[{category}] Minerando {n_portals}/{len(portal_list)} portais")
            
            for portal in selected_portals:
                try:
                    # Quantidade variável de artigos por portal (5-20)
                    n_articles = random.randint(5, 20)
                    articles = self._mine_portal(portal, category, limit=n_articles)
                    all_news.extend(articles)
                except Exception as e:
                    logger.error(f"Erro ao minerar {portal['name']}: {e}")
        
        # Embaralha resultado final
        random.shuffle(all_news)
        
        # Remove duplicatas por URL
        seen = set()
        unique_news = []
        for article in all_news:
            if article['url'] not in seen:
                seen.add(article['url'])
                unique_news.append(article)
        
        logger.info(f"Total único coletado: {len(unique_news)} artigos")
        return unique_news
    
    def mine_all(self) -> List[Dict[str, Any]]:
        """Coleta completa de todos os portais (sem randomização)."""
        all_news = []
        portals = self.config.get('global_miner', {}).get('portals', {})
        
        for category, portal_list in portals.items():
            for portal in portal_list:
                try:
                    articles = self._mine_portal(portal, category, limit=15)
                    all_news.extend(articles)
                except Exception as e:
                    logger.error(f"Erro ao minerar {portal['name']}: {e}")
        
        return all_news
    
    def _mine_portal(self, portal: Dict, category: str, 
                     limit: int = 10) -> List[Dict[str, Any]]:
        """Coleta artigos de um portal via RSS com limite variável."""
        articles = []
        rss_url = portal.get('rss')
        if not rss_url:
            return articles

        # Enforce robots.txt for RSS URL
        try:
            from app.robots import is_allowed
            if not is_allowed(rss_url):
                logger.warning(f"[ROBOTS] RSS bloqueado por robots.txt: {rss_url}")
                return articles
        except Exception as e:
            logger.debug(f"[ROBOTS] check falhou para {rss_url}: {e}")
        
        try:
            response = self.session.get(rss_url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            entries = feed.entries[:limit]
            
            for entry in entries:
                article = self._parse_entry(entry, portal, category)
                if article and self._is_relevant(article):
                    articles.append(article)
                    
        except Exception as e:
            logger.error(f"Erro ao coletar RSS de {portal['name']}: {e}")
        
        return articles
    
    def _parse_entry(self, entry, portal: Dict, category: str) -> Optional[Dict]:
        try:
            title = entry.get('title', '')
            link = entry.get('link', '')
            summary = entry.get('summary', entry.get('description', ''))
            published = entry.get('published', entry.get('updated', ''))
            
            summary = self._clean_html(summary)
            image_url = self._extract_image(entry)
            source_lang = self._detect_language(title + ' ' + summary)
            
            article = {
                'title': title,
                'url': link,
                'summary': summary[:1500],
                'source': portal['name'],
                'source_url': portal['url'],
                'source_lang': source_lang,
                'category': category,
                'image_url': image_url,
                'published_at': self._parse_date(published),
                'mined_at': datetime.utcnow().isoformat(),
                'hash': hashlib.md5(link.encode()).hexdigest(),
                'requires_translation': source_lang != 'pt-BR',
            }
            
            return article
            
        except Exception as e:
            logger.error(f"Erro ao parsear: {e}")
            return None
    
    def _clean_html(self, text: str) -> str:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_image(self, entry) -> Optional[str]:
        if hasattr(entry, 'media_content') and entry.media_content:
            return entry.media_content[0].get('url')
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image/'):
                    return enc.get('url')
        if hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    return link.get('href')
        return None
    
    def _detect_language(self, text: str) -> str:
        common_en = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'for']
        common_pt = ['o', 'a', 'e', 'é', 'de', 'do', 'da', 'que', 'para', 'com']
        
        text_lower = text.lower()
        en_count = sum(1 for w in common_en if f' {w} ' in f' {text_lower} ')
        pt_count = sum(1 for w in common_pt if f' {w} ' in f' {text_lower} ')
        
        return 'en' if en_count > pt_count else 'pt-BR'
    
    def _parse_date(self, date_str: str) -> str:
        if not date_str:
            return datetime.utcnow().isoformat()
        
        formats = [
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%a, %d %b %Y %H:%M:%S %z',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).isoformat()
            except ValueError:
                continue
        
        return datetime.utcnow().isoformat()
    
    def _is_relevant(self, article: Dict) -> bool:
        filters = self.config.get('global_miner', {}).get('relevance_filters', {})
        title_lower = article['title'].lower()
        summary_lower = article['summary'].lower()
        combined = title_lower + ' ' + summary_lower
        
        brazil_kw = filters.get('brazil_keywords', [])
        for kw in brazil_kw:
            if kw.lower() in combined:
                return True
        
        category = article['category']
        if category in ['technology', 'economy', 'geopolitics', 'health', 'science_health']:
            cat_kw = filters.get('global_keywords', {}).get(category, [])
            for kw_list in cat_kw:
                for kw in kw_list:
                    if kw.lower() in combined:
                        return True
        
        if category == 'sports_global':
            return True
        
        return False


class NewsTranslator:
    """Tradutor para pt-BR."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    def translate(self, article: Dict) -> Dict:
        if article.get('source_lang') == 'pt-BR':
            article['title_pt'] = article['title']
            article['summary_pt'] = article['summary']
            return article
        
        if self.llm_client:
            return self._translate_with_llm(article)
        return self._translate_simple(article)
    
    def _translate_with_llm(self, article: Dict) -> Dict:
        prompt = f"""Traduza para Português Brasileiro (pt-BR):

TÍTULO: {article['title']}
CONTEÚDO: {article['summary']}

Use linguagem natural brasileira, mantenha termos técnicos, preserve dados."""
        
        response = self.llm_client.complete(prompt)
        
        return {
            **article,
            'title_pt': response.get('title', article['title']),
            'summary_pt': response.get('summary', article['summary']),
            'translated_at': datetime.utcnow().isoformat(),
            'translation_method': 'llm',
        }
    
    def _translate_simple(self, article: Dict) -> Dict:
        logger.warning("Tradução simples (sem LLM). Configure OpenRouter para produção.")
        return {
            **article,
            'title_pt': article['title'],
            'summary_pt': article['summary'],
            'translated_at': datetime.utcnow().isoformat(),
            'translation_method': 'simple',
            'needs_review': True,
        }


class VolumeManager:
    """
    Gerenciador de Volume de Publicação.
    
    Garante mínimo de 50 matérias/dia com:
    - Distribuição por categoria
    - Mix entre fontes nacionais e globais
    - Priorização por tier
    """
    
    # Distribuição alvo por categoria (% das 50+ matérias)
    DISTRIBUTION_TARGET = {
        'technology': 0.18,     # 9 matérias/dia
        'economy': 0.15,        # 7-8 matérias/dia
        'geopolitics': 0.15,    # 7-8 matérias/dia
        'sports': 0.12,         # 6 matérias/dia
        'security': 0.10,       # 5 matérias/dia
        'politics': 0.10,       # 5 matérias/dia
        'health': 0.08,         # 4 matérias/dia
        'culture': 0.05,        # 2-3 matérias/dia
        'education': 0.04,      # 2 matérias/dia
        'agriculture': 0.03,    # 1-2 matérias/dia
    }
    
    @staticmethod
    def get_target_count(category: str, total_target: int = MIN_ARTICLES_PER_DAY) -> int:
        """Retorna quantas matérias devem ser publicadas por categoria."""
        pct = VolumeManager.DISTRIBUTION_TARGET.get(category, 0.05)
        return max(1, int(total_target * pct))
    
    @staticmethod
    def balance_selection(articles: List[Dict], 
                          total_target: int = MIN_ARTICLES_PER_DAY) -> List[Dict]:
        """
        Balanceia seleção de artigos respeitando distribuição por categoria.
        """
        if not articles:
            return []
        
        # Agrupa por categoria
        by_category = {}
        for article in articles:
            cat = article.get('classification', {}).get('category') or article.get('category')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(article)
        
        # Ordena cada categoria por score
        for cat in by_category:
            by_category[cat].sort(
                key=lambda a: a.get('classification', {}).get('final_score', 0),
                reverse=True
            )
        
        # Seleciona respeitando targets
        selected = []
        for category, target_pct in VolumeManager.DISTRIBUTION_TARGET.items():
            target_count = max(1, int(total_target * target_pct))
            available = by_category.get(category, [])
            selected.extend(available[:target_count])
        
        # Completa com artigos restantes se necessário
        if len(selected) < total_target:
            remaining = [a for a in articles if a not in selected]
            remaining.sort(
                key=lambda a: a.get('classification', {}).get('final_score', 0),
                reverse=True
            )
            selected.extend(remaining[:total_target - len(selected)])
        
        return selected


class MinerPipeline:
    """Pipeline completo do Miner."""
    
    def __init__(self):
        self.miner = GlobalNewsMiner()
        self.translator = NewsTranslator()
        self.volume = VolumeManager()
        self._load_routing()
    
    def _load_routing(self):
        with open("config/portals_global.yml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        routing = config.get('global_miner', {}).get('reporter_routing', {})
        self.reporter_map = {cat: info.get('reporter') for cat, info in routing.items()}
    
    def run(self, target_volume: int = MIN_ARTICLES_PER_DAY) -> List[Dict]:
        """Executa pipeline completo."""
        logger.info("=" * 50)
        logger.info("INICIANDO PIPELINE DO MINER")
        logger.info("=" * 50)
        
        # 1. Coleta randomizada
        articles = self.miner.mine_randomized()
        logger.info(f"Coletados: {len(articles)} artigos")
        
        # 2. Classificação (importância + engajamento)
        articles = classify_articles(articles)
        
        # 3. Filtra por prioridade mínima
        articles = self.miner.classifier.filter_by_priority(articles, min_tier="TIER_3")
        logger.info(f"Após filtro de prioridade: {len(articles)} artigos")
        
        # 4. Tradução para pt-BR
        translated = []
        for article in articles:
            article = self.translator.translate(article)
            translated.append(article)
        
        # 5. Roteamento para repórteres
        for article in translated:
            article = self._route_to_reporter(article)
        
        # 6. Balanceamento de volume
        final = self.volume.balance_selection(translated, total_target=target_volume)
        logger.info(f"Volume final balanceado: {len(final)} artigos")
        
        return final
    
    def _route_to_reporter(self, article: Dict) -> Dict:
        category = article.get('category', '')
        # Mapeia categoria minerada para categoria de repórter
        cat_map = {
            'technology': 'technology',
            'geopolitics': 'politics',
            'economy': 'economy',
            'science_health': 'health',
            'sports_global': 'sports',
            'agriculture': 'agriculture',
        }
        mapped = cat_map.get(category, 'general')
        article['reporter_slug'] = self.reporter_map.get(mapped, 'enzo.bianchi')
        article['routed_at'] = datetime.utcnow().isoformat()
        return article


# ============================================================
# SCHEDULER (executa a cada 30 min)
# ============================================================
def run_scheduled_mining():
    """Função chamada pelo scheduler a cada 30 minutos."""
    pipeline = MinerPipeline()
    articles = pipeline.run(target_volume=MIN_ARTICLES_PER_DAY)
    return articles


def mine_global_news() -> List[Dict]:
    """Função principal."""
    pipeline = MinerPipeline()
    return pipeline.run()


# ============================================================
# EXEMPLO DE USO
# ============================================================
if __name__ == "__main__":
    pipeline = MinerPipeline()
    articles = pipeline.run()
    
    print(f"\n{'='*50}")
    print(f"RESULTADO: {len(articles)} artigos prontos para publicação")
    print(f"{'='*50}\n")
    
    for i, article in enumerate(articles[:10], 1):
        c = article.get('classification', {})
        print(f"{i}. {article.get('title_pt', article['title'])[:60]}...")
        print(f"   Fonte: {article.get('source')}")
        print(f"   Score: {c.get('final_score', 0)} ({c.get('priority_tier')})")
        print(f"   Repórter: {article.get('reporter_slug')}")
        print()