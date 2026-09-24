"""Pipeline completo do minerador global."""

import logging
from datetime import datetime, timezone
from typing import Dict, List

import yaml

from app.miner_constants import MIN_ARTICLES_PER_DAY
from app.miner_global import GlobalNewsMiner
from app.miner_volume import VolumeManager

logger = logging.getLogger(__name__)


class MinerPipeline:
    """Pipeline completo do Miner."""

    def __init__(self):
        self.miner = GlobalNewsMiner()
        from app.translator import NewsTranslator as LLMTranslator

        self.translator = LLMTranslator()
        self.volume = VolumeManager()
        self._load_routing()

    def _load_routing(self):
        with open("config/portals_global.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        routing = config.get("global_miner", {}).get("reporter_routing", {})
        self.reporter_map = {cat: info.get("reporter") for cat, info in routing.items()}

    def run(self, target_volume: int = MIN_ARTICLES_PER_DAY) -> List[Dict]:
        """Executa pipeline completo."""
        logger.info("=" * 50)
        logger.info("INICIANDO PIPELINE DO MINER")
        logger.info("=" * 50)

        # 1. Coleta randomizada
        articles = self.miner.mine_randomized()
        logger.info(f"Coletados: {len(articles)} artigos")

        # 2. Classificação (importância + engajamento)
        for article in articles:
            self.miner.classifier.classify(article)

        # 3. Filtra por prioridade mínima
        articles = self.miner.classifier.filter_by_priority(articles, min_tier="TIER_3")
        logger.info(f"Após filtro de prioridade: {len(articles)} artigos")

        # 4. Tradução para pt-BR
        translated = []
        for article in articles:
            try:
                translated.append(self.translator.translate(article))
            except RuntimeError:
                translated.append({**article, "needs_review": True})

        # 5. Roteamento para repórteres
        for article in translated:
            article = self._route_to_reporter(article)

        # 6. Balanceamento de volume
        final = self.volume.balance_selection(translated, total_target=target_volume)
        logger.info(f"Volume final balanceado: {len(final)} artigos")

        return final

    def _route_to_reporter(self, article: Dict) -> Dict:
        category = article.get("category", "")
        # Mapeia categoria minerada para categoria de repórter
        cat_map = {
            "technology": "tech",
            "geopolitics": "politics",
            "economy": "economy",
            "science_health": "health",
            "sports_global": "sports",
            "agriculture": "agriculture",
        }
        mapped = cat_map.get(category, "general")
        article["reporter_slug"] = self.reporter_map.get(mapped, "enzo.bianchi")
        article["routed_at"] = datetime.now(timezone.utc).isoformat()
        return article
