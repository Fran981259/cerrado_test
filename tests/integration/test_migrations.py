from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from alembic import command


def _alembic_config(database_path: Path) -> Config:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")
    return config


def _table_names(database_path: Path) -> set[str]:
    engine = create_engine(f"sqlite:///{database_path}")
    return set(inspect(engine).get_table_names())


def test_migrations_upgrade_and_downgrade_are_reversible(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database_path = tmp_path / "migrations.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    config = _alembic_config(database_path)

    command.upgrade(config, "head")
    tables = _table_names(database_path)
    assert {"news_articles", "page_views", "alembic_version"}.issubset(tables)

    command.downgrade(config, "base")
    assert _table_names(database_path) == {"alembic_version"}


def test_region_migration_preserves_legacy_articles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database_path = tmp_path / "legacy.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    config = _alembic_config(database_path)

    command.upgrade(config, "fd2de82e095a")
    engine = create_engine(f"sqlite:///{database_path}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO reporters "
                "(slug, display_name, role, birth_date, created_at, updated_at) "
                "VALUES ('legacy.reporter', 'Legacy Reporter', 'general', "
                "'2026-09-24 12:00:00', '2026-09-24 12:00:00', '2026-09-24 12:00:00')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO news_articles "
                "(title, content, reporter_id, created_at, updated_at) "
                "VALUES ('Legacy', 'Conteúdo legado', 1, "
                "'2026-09-24 12:00:00', '2026-09-24 12:00:00')"
            )
        )

    command.upgrade(config, "head")
    with engine.connect() as connection:
        row = connection.execute(text("SELECT region FROM news_articles")).one()
        assert row.region == "ms"
        columns = {column["name"] for column in inspect(engine).get_columns("page_views")}
        assert {"user_agent", "session_hash"}.isdisjoint(columns)
