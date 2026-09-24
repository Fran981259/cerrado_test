"""Orquestração do minerador global."""

import logging
import random
from typing import Any, Dict, List

import httpx
import yaml

from app.classifier import NewsClassifier
from app.miner_constants import RANDOM_CATEGORY_PROBABILITY
from app.miner_global_parsing import GlobalNewsParsingMixin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GlobalNewsMiner(GlobalNewsParsingMixin):
    """
    Agente minerador de notícias globais COM RANDOMIZAÇÃO.

    - Cada execução escolhe aleatoriamente quais categorias minerar
    - Cada feed tem chance de ser amostrado ou pulado
    - Garante variedade na pauta diária
    """

    def __init__(self, config_path: str = "config/portals_global.yml"):
        self.config = self._load_config(config_path)
        self.classifier = NewsClassifier()
        self.session = httpx.Client(timeout=30.0, headers={"User-Agent": "PortalCerrado-Miner/1.0"})
        self._load_glossary()

    def _load_config(self, path: str) -> Dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_glossary(self):
        cfg_lang = self.config.get("global_miner", {}).get("language", {})
        self.glossary = cfg_lang.get("glossary", {})
        self.preserve_terms = cfg_lang.get("preserve_terms", [])

    def mine_randomized(self) -> List[Dict[str, Any]]:
        """
        Coleta randomizada de notícias.

        - Escolhe aleatoriamente quais portais minerar
        - Escolhe aleatoriamente quantos artigos pegar de cada portal
        - Varia a cada execução para evitar repetição
        """
        if not self.config.get("global_miner", {}).get("enabled", False):
            logger.info("Minerador global desativado pela política editorial.")
            return []

        all_news = []
        portals = self.config.get("global_miner", {}).get("portals", {})

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

        # Google News RSS (descoberta pt-BR) — sempre incluído, sem randomização
        try:
            all_news.extend(self.mine_google_news(limit=8))
        except Exception as e:
            logger.error(f"Erro no Google News: {e}")

        # Remove duplicatas por URL
        seen = set()
        unique_news = []
        for article in all_news:
            if article["url"] not in seen:
                seen.add(article["url"])
                unique_news.append(article)

        logger.info(f"Total único coletado: {len(unique_news)} artigos")
        return unique_news

    def mine_all(self) -> List[Dict[str, Any]]:
        """Coleta completa de todos os portais (sem randomização)."""
        if not self.config.get("global_miner", {}).get("enabled", False):
            logger.info("Minerador global desativado pela política editorial.")
            return []

        all_news = []
        portals = self.config.get("global_miner", {}).get("portals", {})

        for category, portal_list in portals.items():
            for portal in portal_list:
                try:
                    articles = self._mine_portal(portal, category, limit=15)
                    all_news.extend(articles)
                except Exception as e:
                    logger.error(f"Erro ao minerar {portal['name']}: {e}")

        try:
            all_news.extend(self.mine_google_news(limit=10))
        except Exception as e:
            logger.error(f"Erro no Google News: {e}")

        return all_news

    # ----------------------------------------------------------
