"""Categorias e padrões estáveis de detecção de curiosidades."""

from enum import Enum


class CuriosityCategory(Enum):
    """Categorias de curiosidade por segmento."""

    TECHNOLOGY = "technology"
    SPORTS = "sports"
    SECURITY = "security"
    POLITICS = "politics"
    HEALTH = "health"
    EDUCATION = "education"
    AGRICULTURE = "agriculture"
    CULTURE = "culture"
    ECONOMY = "economy"


class CuriosityPatterns:
    """Padrões usados para detectar curiosidades externas."""

    DETECTION_PATTERNS = {
        "did you know": "curiosity", "you may not know": "curiosity", "fun fact": "curiosity",
        "interesting fact": "curiosity", "little known": "curiosity", "rarely known": "curiosity",
        "surprising": "curiosity", "unbelievable": "curiosity", "amazing": "curiosity",
        "incredible": "curiosity", "strange but true": "curiosity", "você sabia": "curiosity",
        "sabia que": "curiosity", "curiosidade": "curiosity", "fato interessante": "curiosity",
        "poucos sabem": "curiosity", "raramente conhecido": "curiosity", "surpreendente": "curiosity",
        "incrível": "curiosity", "impressionante": "curiosity", "será que": "curiosity",
        "o número": "curiosity", "quantos": "curiosity", "quanto tempo": "curiosity",
        "a maior": "curiosity", "o menor": "curiosity", "o mais": "curiosity", "recorde": "curiosity",
        "nunca imaginou": "curiosity",
    }
    ENGAGEMENT_BOOST = 1.3
