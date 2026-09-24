"""Modelos e sinais estáticos usados pelo ranking de tendências."""

from dataclasses import dataclass
from typing import Any, Dict, List

TOPIC_KEYWORDS = {
    "politics": {"governo", "prefeito", "governador", "câmara", "assembleia", "eleição", "política", "stf", "stj", "tre", "tse", "câmara dos vereadores", "assembleia legislativa"},
    "economy": {"economia", "mercado", "emprego", "juros", "inflação", "banco", "investimento", "arrecadação", "salário", "piso salarial"},
    "security": {"polícia", "crime", "prisão", "homicídio", "roubo", "furto", "investigação", "suspeito", "flagrante", "delegacia"},
    "health": {"saúde", "hospital", "vacina", "médico", "paciente", "uti", "sus", "dengue", "tratamento", "exame", "pronto-socorro"},
    "agriculture": {"agro", "agronegócio", "safra", "soja", "milho", "pecuária", "gado", "colheita", "plantio", "produtor rural"},
    "sports": {"futebol", "esporte", "jogo", "time", "gol", "campeonato", "atleta", "torcida", "vitória", "partida"},
    "tech": {"tecnologia", "ia", "inteligência artificial", "aprendizado de máquina", "app", "sistema", "software", "startup", "digital", "plataforma"},
}


@dataclass
class TrendItem:
    topic: str
    category: str
    score: int
    article_count: int
    evidence: List[Dict[str, Any]]
