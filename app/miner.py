"""Compatibilidade pública do minerador global.

As classes permanecem exportadas neste módulo enquanto a implementação fica
separada por responsabilidade.
"""

from app.miner_constants import ARTICLES_PER_CYCLE, MIN_ARTICLES_PER_DAY, RANDOM_CATEGORY_PROBABILITY
from app.miner_global import GlobalNewsMiner
from app.miner_pipeline import MinerPipeline
from app.miner_volume import VolumeManager

__all__ = [
    "ARTICLES_PER_CYCLE",
    "MIN_ARTICLES_PER_DAY",
    "RANDOM_CATEGORY_PROBABILITY",
    "GlobalNewsMiner",
    "MinerPipeline",
    "VolumeManager",
]
