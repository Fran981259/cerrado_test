"""
Imagens 100% contextuais — Portal Cerrado.
Ordem de prioridade da capa:
1. Imagem ORIGINAL da matéria fonte (extraída pelo fetcher).
2. Imagem contextual por palavra-chave do título.
3. Imagem contextual da categoria.
NUNCA aleatória (picsum e afins são proibidos — geram criança em matéria de combustível).
"""
import logging
import re
from typing import Optional

import requests

logger = logging.getLogger(__name__)

U = "https://images.unsplash.com/{}?w=800&h=450&fit=crop"

CATEGORY_IMAGES = {
    "technology": U.format("photo-1518770660439-4636190af475"),
    "tech": U.format("photo-1518770660439-4636190af475"),
    "sports": U.format("photo-1579952363873-27f3bade9f55"),
    "politics": U.format("photo-1529107386315-e1a2ed48a620"),
    "economy": U.format("photo-1611974789855-9c2a0a7236a3"),
    "health": U.format("photo-1559757175-5700dde675bc"),
    "security": U.format("photo-1526374965328-7f61d4dc18c5"),
    "science": U.format("photo-1507413245164-6160d8298b31"),
    "entertainment": U.format("photo-1485846234645-a62644f84728"),
    "agriculture": U.format("photo-1500937386664-56d1dfef3854"),
    "education": U.format("photo-1503676260728-1c00da094a0b"),
    "culture": U.format("photo-1492684223066-81342ee5ff30"),
    "clima": U.format("photo-1504608524841-42fe6f032b4b"),
    "general": U.format("photo-1504711434969-e33886168f5c"),
}

# (palavras-chave no título, url candidata) — primeira que verificar vira capa.
# Palavras isoladas usam fronteira (evita "calor" em "calorias", "campo" em "Campo Grande").
KEYWORD_IMAGES = [
    (["combustível", "combustivel", "gasolina", "etanol", "posto de gasolina", "posto de combustível", "postos de"], U.format("photo-1527018601619-a508a2be00cd")),
    (["onda de calor", "recorde de calor", "temperatura", "calor"], U.format("photo-1504370805625-d32c54b16100")),
    (["chuva", "alagamento", "enchente", "tempestade", "defesa civil", "estiagem"], U.format("photo-1519692933481-e162a57d6721")),
    (["emprego", "empregos", "vaga", "concurso", "trabalho"], U.format("photo-1521737604893-d14cc237f11d")),
    (["casa própria", "casa propria", "moradia", "habitação", "habitacao"], U.format("photo-1560518883-ce09059eeffa")),
    (["empréstimo", "emprestimo", "dinheiro", "salário", "salario", "reajuste"], U.format("photo-1554224155-6726b3ff858f")),
    (["crédito", "credito", "empresa", "mercado", "negócio"], U.format("photo-1454165804606-c3d57bc86b40")),
    (["bitcoin", "cripto"], U.format("photo-1518546305927-5a555bb7020d")),
    (["teclado", "qwerty", "computador"], U.format("photo-1587829741301-dc798b83add3")),
    (["cachorro", "pet", "pitbull", "cão", "cao"], U.format("photo-1543466835-00a7907e9de1")),
    (["moto", "motociclista"], U.format("photo-1558981403-c5f9899a28bc")),
    (["carro", "volante", "trânsito", "transito", "acidente", "colisão", "colisao", "atropelamento"], U.format("photo-1449965408869-eaa3f722e40d")),
    (["documentário", "documentario", "cinema", "filme"], U.format("photo-1485846234645-a62644f84728")),
    (["blusinha", "importação", "importacao", "taxa"], U.format("photo-1494412574643-ff11b0a5c1c3")),
    (["tradução", "traducao", "idioma"], U.format("photo-1455390582262-044cdead277a")),
    (["unesco", "patrimônio", "patrimonio"], U.format("photo-1552832230-c0197dd311b5")),
    (["soja", "eucalipto", "safra", "lavoura"], U.format("photo-1500382017468-9049fed747ef")),
    (["onu", "eleição", "eleicao", "campanha", "governo"], U.format("photo-1529107386315-e1a2ed48a620")),
]

# Palavras que exigem fronteira estrita (nunca substring solta)
_STRICT = {"calor", "campo", "moto", "taxa", "posto", "casa", "mercado", "governo"}


def _hit(keyword: str, low: str) -> bool:
    if " " in keyword:
        return keyword in low  # frase: substring basta ("Campo Grande" não contém "campo " + ... )
    if keyword in _STRICT:
        if keyword == "campo":
            # "Campo Grande" é cidade, não lavoura
            return bool(re.search(r"\bcampos?\b(?! grande)", low))
        return bool(re.search(r"\b" + re.escape(keyword) + r"(s|es)?\b", low))
    return keyword in low


def verify_image(url: str, timeout: float = 8.0) -> bool:
    """Confere se a URL existe e é imagem (sem baixar tudo)."""
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True,
                          headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            return True
        # alguns CDNs bloqueiam HEAD — tenta GET parcial
        r = requests.get(url, timeout=timeout, stream=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        ok = r.status_code == 200 and "image" in r.headers.get("Content-Type", "")
        r.close()
        return ok
    except Exception:
        return False


def contextual_image(title: str, category: str, verify: bool = False) -> str:
    """Capa contextual determinística (verificada se verify=True)."""
    low = (title or "").lower()
    for keywords, url in KEYWORD_IMAGES:
        if any(_hit(k.lower(), low) for k in keywords):
            if not verify or verify_image(url):
                return url
    cat_url = CATEGORY_IMAGES.get(category or "", CATEGORY_IMAGES["general"])
    if verify and not verify_image(cat_url):
        return CATEGORY_IMAGES["general"]
    return cat_url
