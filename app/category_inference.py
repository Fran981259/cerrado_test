"""Conservative category inference for titles and leads collected by the pipeline."""

import re

_CATEGORY_SIGNALS = (
    ("politics", ("eleiç", "eleitoral", "candidato", "campanha", "tse", "tre", "urna", "debate presidencial", "congresso", "senado", "câmara dos deputados", "governo federal", "palácio do planalto", "deputado", "senador", "governador", "prefeito", "vereador")),
    ("sports", ("futebol", "campeonato", "partida", "torneio", "gol", "estádio", "torcida", "atleta", "brasileirão", "copa", "olímp", "time de", "sub-")),
    ("security", ("polícia", "homicídio", "prisão", "preso", "delegacia", "assalto", "roubo", "furto", "tráfico", "cocaína", "maconha", "apreensão")),
    ("health", ("hospital", "paciente", "vacina", "vacinação", "uti", "doença", "saúde pública", "cirurgia", "leito")),
    ("agriculture", ("agronegócio", "safra", "soja", "milho", "pecuária", "rebanho", "produtor rural", "lavoura", "colheita", "fertilizante")),
    ("economy", ("inflação", "juros", "emprego", "vagas de trabalho", "exportação", "arrecadação", "bolsa de valores", "mercado financeiro")),
    ("tech", ("tecnologia", "inteligência artificial", "software", "smartphone", "aplicativo", "ciberataque", "internet")),
)


def _matches(text: str, signal: str) -> bool:
    if signal.endswith("ç"):
        return signal in text
    return bool(re.search(rf"\b{re.escape(signal)}", text))


def infer_category(text: str) -> str:
    """Return a category only when specific editorial signals support it."""
    normalized = (text or "").lower()
    for category, signals in _CATEGORY_SIGNALS:
        if any(_matches(normalized, signal) for signal in signals):
            return category
    return "general"
