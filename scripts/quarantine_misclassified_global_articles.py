#!/usr/bin/env python3
"""Move para revisão matérias globais que foram rotuladas como ``ms``.

Use primeiro sem argumentos para auditar. Só use ``--apply`` após revisar a
lista: a operação tira as matérias encontradas da área pública, sem apagá-las.
"""

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# O bootstrap de sys.path permite executar o script diretamente na raiz do projeto.
import yaml  # noqa: E402
from sqlalchemy.exc import OperationalError  # noqa: E402

from app.database import get_session  # noqa: E402
from app.schema import NewsArticle  # noqa: E402


def host(url: str) -> str:
    return (urlparse(url or "").hostname or "").lower().removeprefix("www.")


def configured_global_hosts() -> set[str]:
    hosts: set[str] = set()
    for file_name in ("portals_global.yml", "portals_us.yml"):
        config = yaml.safe_load((ROOT / "config" / file_name).read_text(encoding="utf-8")) or {}
        groups = config.get("global_miner", {}).get("portals", {}) if file_name == "portals_global.yml" else config.get("portals_us", {})
        for entries in groups.values():
            for entry in entries or []:
                value = host(entry.get("url", ""))
                if value:
                    hosts.add(value)
    capital_config = yaml.safe_load((ROOT / "config" / "portals_capital_ms.yml").read_text(encoding="utf-8")) or {}
    for entries in (capital_config.get("portals_ms") or {}).values():
        for entry in entries or []:
            city = str(entry.get("city") or "").strip().lower()
            if city in {"nacional", "fortaleza"}:
                value = host(str(entry.get("url", "")))
                if value:
                    hosts.add(value)
    return hosts


def article_source_hosts(article: NewsArticle) -> set[str]:
    return {
        value
        for source in article.sources or []
        if isinstance(source, dict)
        for value in [host(str(source.get("url", "")))]
        if value
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="tira as matérias encontradas da área pública")
    args = parser.parse_args()

    global_hosts = configured_global_hosts()
    db = get_session()
    try:
        candidates = []
        try:
            articles = db.query(NewsArticle).filter(NewsArticle.region == "ms", NewsArticle.status == "published").all()
        except OperationalError as exc:
            if "news_articles.region" in str(exc):
                print("Banco sem a coluna region. Execute 'alembic upgrade head' no ambiente alvo antes da auditoria.")
                return 2
            raise

        for article in articles:
            matched = article_source_hosts(article) & global_hosts
            if matched:
                candidates.append((article, sorted(matched)))

        for article, matched in candidates:
            print(f"{article.id}\t{article.slug}\t{', '.join(matched)}\t{article.title}")

        if args.apply and candidates:
            for article, _ in candidates:
                article.status = "review"
                article.visibility = "private"
            db.commit()
            print(f"\n{len(candidates)} matéria(s) movida(s) para revisão e removida(s) da área pública.")
        else:
            print(f"\n{len(candidates)} matéria(s) encontrada(s). {'Nenhuma alteração aplicada.' if not args.apply else ''}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
