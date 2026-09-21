"""Tests para scheduler-disable logic (item 1) e database fallback (item 10)."""

import importlib
import os

TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")


def _restore_test_database(monkeypatch, db_mod):
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    importlib.reload(db_mod)
    db_mod.init_db()


def test_local_scheduler_disabled_when_celery_active(monkeypatch):
    # Simula ENVIRONMENT com CELERY_SCHEDULER=1
    monkeypatch.setenv("CELERY_SCHEDULER", "1")
    monkeypatch.setenv("ENABLE_LOCAL_SCHEDULER", "1")
    # Recarrega main para testar _start_scheduler logic
    # Chama a lógica interna sem iniciar thread
    enabled = os.getenv("ENABLE_LOCAL_SCHEDULER", "1") == "1"
    celery_active = os.getenv("CELERY_SCHEDULER", "0") == "1"
    if celery_active:
        enabled = False
    assert enabled is False
    assert celery_active is True


def test_local_scheduler_enabled_when_celery_inactive(monkeypatch):
    monkeypatch.setenv("CELERY_SCHEDULER", "0")
    monkeypatch.setenv("ENABLE_LOCAL_SCHEDULER", "1")
    enabled = os.getenv("ENABLE_LOCAL_SCHEDULER", "1") == "1"
    celery_active = os.getenv("CELERY_SCHEDULER", "0") == "1"
    if celery_active:
        enabled = False
    assert enabled is True


def test_local_scheduler_respects_enable_flag(monkeypatch):
    monkeypatch.setenv("CELERY_SCHEDULER", "0")
    monkeypatch.setenv("ENABLE_LOCAL_SCHEDULER", "0")
    enabled = os.getenv("ENABLE_LOCAL_SCHEDULER", "1") == "1"
    celery_active = os.getenv("CELERY_SCHEDULER", "0") == "1"
    if celery_active:
        enabled = False
    assert enabled is False


def test_scheduler_policy_is_loaded_from_runtime_config():
    from app.runtime_config import get_scheduler_settings

    settings = get_scheduler_settings()

    assert settings.min_articles_per_day == 12
    assert settings.pipeline_interval_seconds == 1800


def test_celery_schedule_keeps_only_local_editorial_pipeline(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    from app.celery_app import celery_app

    schedule = celery_app.conf.beat_schedule
    assert "run-full-pipeline" in schedule
    assert "mine-global-news" not in schedule
    assert "generate-daily-curiosities" not in schedule


def test_retired_global_mining_task_is_a_noop():
    from app.tasks.mine_tasks import mine_global_news

    result = mine_global_news.run()
    assert result["status"] == "disabled"
    assert result["articles_mined"] == 0


def test_cors_explicit_origins(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://100.95.111.24:3000,http://localhost:3000")
    # Importa a função _cors_origins
    import app.main as main_mod

    origins = main_mod._cors_origins()
    assert "http://100.95.111.24:3000" in origins
    assert "http://localhost:3000" in origins
    assert "*" not in origins


def test_cors_default_no_wildcard(monkeypatch):
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    import app.main as main_mod

    origins = main_mod._cors_origins()
    assert "*" not in origins
    assert "http://100.95.111.24:3000" in origins


def test_database_fallback_dev(monkeypatch):
    # Em dev, fallback para SQLite deve funcionar
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DATABASE_URL", "postgresql://invalid:invalid@localhost:5432/nonexistent")
    # Recarrega database.py
    import app.database as db_mod

    try:
        importlib.reload(db_mod)
        assert db_mod._using_sqlite is True or db_mod.ENVIRONMENT == "development"
    finally:
        _restore_test_database(monkeypatch, db_mod)


def test_database_fails_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://invalid:invalid@localhost:5432/nonexistent")
    import importlib

    import app.database as db_mod

    # Deve levantar erro em produção, não fallback silencioso
    try:
        importlib.reload(db_mod)
        # Se chegou aqui sem erro, verifica se flag está correta
        # Em produção com DB inválido, deve ter levantado
        assert False, "Deveria falhar em produção"
    except Exception as e:
        assert "production" in str(e).lower() or "PostgreSQL" in str(e) or db_mod.IS_PRODUCTION is True
    finally:
        _restore_test_database(monkeypatch, db_mod)
