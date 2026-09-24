"""Mistura controlada de curiosidades no fluxo editorial."""

import random
from typing import Dict, List

from app.curiosities import CuriosityGenerator


class CuriosityMixer:
    """Adiciona curiosidades em momentos estratégicos do dia."""

    def __init__(self):
        self.generator = CuriosityGenerator()

    def inject_curiosities(self, articles: List[Dict], daily_target: int = 50, curiosity_ratio: float = 0.15) -> List[Dict]:
        """Injeta curiosidades mantendo a proporção configurada."""
        target = max(3, int(daily_target * curiosity_ratio))
        generated = self.generator.generate_daily_curiosities()
        if len(generated) > target:
            random.shuffle(generated)
            generated = generated[:target]
        result, cursor = [], 0
        for index, article in enumerate(articles):
            result.append(article)
            if (index + 1) % 7 == 0 and cursor < len(generated):
                result.append(generated[cursor])
                cursor += 1
        result.extend(generated[cursor:])
        return result
