"""Balanceamento de volume editorial."""

from typing import Any, Dict, List

from app.miner_constants import MIN_ARTICLES_PER_DAY


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
        "technology": 0.18,  # 9 matérias/dia
        "economy": 0.15,  # 7-8 matérias/dia
        "geopolitics": 0.15,  # 7-8 matérias/dia
        "sports": 0.12,  # 6 matérias/dia
        "security": 0.10,  # 5 matérias/dia
        "politics": 0.10,  # 5 matérias/dia
        "health": 0.08,  # 4 matérias/dia
        "culture": 0.05,  # 2-3 matérias/dia
        "education": 0.04,  # 2 matérias/dia
        "agriculture": 0.03,  # 1-2 matérias/dia
    }

    @staticmethod
    def get_target_count(category: str, total_target: int = MIN_ARTICLES_PER_DAY) -> int:
        """Retorna quantas matérias devem ser publicadas por categoria."""
        pct = VolumeManager.DISTRIBUTION_TARGET.get(category, 0.05)
        return max(1, int(total_target * pct))

    @staticmethod
    def balance_selection(articles: List[Dict], total_target: int = MIN_ARTICLES_PER_DAY) -> List[Dict]:
        """
        Balanceia seleção de artigos respeitando distribuição por categoria.
        """
        if not articles:
            return []

        # Agrupa por categoria
        by_category: Dict[str, List[Any]] = {}
        for article in articles:
            cat = article.get("classification", {}).get("category") or article.get("category")
            if cat is None:
                continue
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(article)

        # Ordena cada categoria por score
        for cat in by_category:
            by_category[cat].sort(key=lambda a: a.get("classification", {}).get("final_score", 0), reverse=True)

        # Seleciona respeitando targets
        selected = []
        for category, target_pct in VolumeManager.DISTRIBUTION_TARGET.items():
            target_count = max(1, int(total_target * target_pct))
            available = by_category.get(category, [])
            selected.extend(available[:target_count])

        # Completa com artigos restantes se necessário
        if len(selected) < total_target:
            remaining = [a for a in articles if a not in selected]
            remaining.sort(key=lambda a: a.get("classification", {}).get("final_score", 0), reverse=True)
            selected.extend(remaining[: total_target - len(selected)])

        return selected
