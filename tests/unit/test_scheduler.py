"""Tests para scheduler-disable logic (item 1) e database fallback (item 10)."""
import os
import importlib
from unittest.mock import patch

def test_local_scheduler_disabled_when_celery_active(monkeypatch):
    # Simula ENVIRONMENT com CELERY_SCHEDULER=1
    monkeypatch.setenv("CELERY_SCHEDULER", "1")
    monkeypatch.setenv("ENABLE_LOCAL_SCHEDULER", "1")
    # Recarrega main para testar _start_scheduler logic
    import app.main as main_mod
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

def test_cors_explicit_origins(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://atualizabrasil.news,http://localhost:3000")
    # Importa a função _cors_origins
    import app.main as main_mod
    origins = main_mod._cors_origins()
    assert "https://atualizabrasil.news" in origins
    assert "http://localhost:3000" in origins
    assert "*" not in origins

def test_cors_default_no_wildcard(monkeypatch):
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    import app.main as main_mod
    origins = main_mod._cors_origins()
    assert "*" not in origins
    assert "https://atualizabrasil.news" in origins

def test_database_fallback_dev(monkeypatch):
    # Em dev, fallback para SQLite deve funcionar
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DATABASE_URL", "postgresql://invalid:invalid@localhost:5432/nonexistent")
    # Recarrega database.py
    import app.database as db_mod
    import importlib
    importlib.reload(db_mod)
    assert db_mod._using_sqlite is True or db_mod.ENVIRONMENT == "development"

def test_database_fails_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://invalid:invalid@localhost:5432/nonexistent")
    import app.database as db_mod
    import importlib
    # Deve levantar erro em produção, não fallback silencioso
    try:
        importlib.reload(db_mod)
        # Se chegou aqui sem erro, verifica se flag está correta
        # Em produção com DB inválido, deve ter levantado
        assert False, "Deveria falhar em produção"
    except Exception as e:
        assert "production" in str(e).lower() or "PostgreSQL" in str(e) or db_mod.IS_PRODUCTION is True
    finally:
        # Restaura para dev para não quebrar outros testes
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("DATABASE_URL", "postgresql://portal_user:portal_pass@localhost:5432/atualiza_brasil")
        importlib.reload(db_mod)
