"""Shared boundary contracts; existing timestamps in the database represent UTC."""
from datetime import datetime, timezone
from urllib.parse import urlsplit

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator


def as_utc(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def iso_utc(value):
    return as_utc(value).isoformat() if value is not None else None


class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return as_utc(value).replace(tzinfo=None) if value is not None else None


ALIASES = {
    # Tecnologia e Ciência
    "technology": "tech", "tecnologia": "tech", "inovação": "tech", "informática": "tech",
    "science": "science", "ciência": "science", "ciências": "science", "espaço": "science", "astronomia": "science",
    
    # Cultura e Entretenimento
    "entertainment": "culture", "cultura": "culture", "cinema": "culture", "música": "culture", "arte": "culture",
    "famosos": "culture", "celebridades": "culture", "televisão": "culture", "tv": "culture", "shows": "culture",
    
    # Saúde
    "health": "health", "saúde": "health", "bem-estar": "health", "medicina": "health", "science_health": "health",
    
    # Esportes
    "sports": "sports", "esporte": "sports", "esportes": "sports", "futebol": "sports", "brasileirão": "sports", 
    "sports_global": "sports", "tênis": "sports", "vôlei": "sports", "basquete": "sports", "olimpíadas": "sports",
    
    # Política
    "politics": "politics", "política": "politics", "geopolitics": "politics", "poder": "politics", 
    "eleições": "politics", "governo": "politics", "legislativo": "politics", "executivo": "politics", "judiciário": "politics",
    
    # Economia
    "economy": "economy", "economia": "economy", "mercado": "economy", "negócios": "economy", "finanças": "economy",
    "dinheiro": "economy", "bolsa": "economy", "investimentos": "economy", "trabalho e renda": "economy",
    
    # Segurança
    "security": "security", "segurança": "security", "polícia": "security", "crime": "security", "investigação": "security",
    
    # Agronegócio
    "agriculture": "agriculture", "agronegócio": "agriculture", "agro": "agriculture", "rural": "agriculture", "campo": "agriculture",
    
    # Educação
    "education": "education", "educação": "education", "escola": "education", "faculdade": "education", 
    "enem": "education", "concursos": "education", "capacitação": "education",
    
    # Clima e Meio Ambiente
    "clima": "clima", "meio ambiente": "clima", "natureza": "clima", "sustentabilidade": "clima", "previsão do tempo": "clima",
}
CATEGORIES = {"tech", "culture", "health", "science", "sports", "politics", "economy",
              "security", "agriculture", "education", "clima", "general"}


def category_name(value):
    value = (value or "general").lower().strip()
    return ALIASES.get(value, value) if value in CATEGORIES or value in ALIASES else "general"


def category_values(value):
    canonical = category_name(value)
    return [canonical] + [alias for alias, target in ALIASES.items() if target == canonical]


def sources_list(value):
    result = []
    seen = set()
    for source in value if isinstance(value, list) else []:
        source = {"url": source} if isinstance(source, str) else source
        if not isinstance(source, dict) or not isinstance(source.get("url"), str):
            continue
        url = source["url"].strip()
        try:
            parsed = urlsplit(url)
            valid = parsed.scheme in {"https", "http"} and parsed.hostname and not parsed.username and not parsed.password
        except ValueError:
            valid = False
        if valid and url not in seen:
            seen.add(url)
            result.append({"url": url, "name": str(source.get("name") or ""), "title": str(source.get("title") or "")})
    return result
