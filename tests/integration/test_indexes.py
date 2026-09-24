from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from alembic import command

EXPECTED_INDEXES = {
    "ix_news_articles_reporter_id": ("news_articles", "reporter_id"),
    "ix_news_articles_visibility": ("news_articles", "visibility"),
    "ix_news_articles_updated_at": ("news_articles", "updated_at"),
    "ix_scraping_tasks_portal_id": ("scraping_tasks", "portal_id"),
    "ix_scraping_tasks_created_at": ("scraping_tasks", "created_at"),
    "ix_publication_logs_article_id": ("publication_logs", "article_id"),
    "ix_publication_logs_reporter_id": ("publication_logs", "reporter_id"),
    "ix_publication_logs_created_at": ("publication_logs", "created_at"),
    "ix_article_identities_article_id": ("article_identities", "article_id"),
}


def test_editorial_query_indexes_exist_and_are_used(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database_path = tmp_path / "indexes.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path}")
    database_inspector = inspect(engine)

    for index_name, (table, column) in EXPECTED_INDEXES.items():
        indexes = {item["name"]: item["column_names"] for item in database_inspector.get_indexes(table)}
        assert indexes.get(index_name) == [column]

    with engine.connect() as connection:
        plan = connection.execute(
            text(
                "EXPLAIN QUERY PLAN SELECT id FROM news_articles "
                "WHERE reporter_id = 1 AND visibility = 'public' "
                "ORDER BY updated_at DESC"
            )
        ).all()
    assert any("ix_news_articles_reporter_id" in str(row) for row in plan)
