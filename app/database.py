"""
Conexão com Banco de Dados — Atualiza Brasil
PostgreSQL via SQLAlchemy
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

# URL do banco
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://portal_user:portal_pass@localhost:5432/atualiza_brasil"
)

try:
    # Tenta PostgreSQL (produção). create_engine é lazy, então checamos com connect.
    _engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )
    with _engine.connect() as _c:
        pass
    engine = _engine
    _using_sqlite = False
except Exception:
    # Fallback local (desenvolvimento sem Postgres): usa SQLite.
    import sqlite3
    _sqlite_file = os.path.join(os.path.dirname(__file__), "..", "data", "atualiza_brasil.db")
    _sqlite_file = os.path.abspath(_sqlite_file)
    os.makedirs(os.path.dirname(_sqlite_file), exist_ok=True)
    engine = create_engine(
        f"sqlite:///{_sqlite_file}",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    _using_sqlite = True
    import logging
    logging.getLogger(__name__).warning(
        f"PostgreSQL indisponível ({DATABASE_URL}); usando SQLite em {_sqlite_file}"
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para models
Base = declarative_base()


def get_db():
    """Dependency para FastAPI - retorna sessão do DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa o banco de dados (cria tabelas)."""
    from app.schema import NewsArticle, Reporter, SourcePortal, ScrapingTask, PublicationLog
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Remove todas as tabelas (USE COM CUIDADO)."""
    from app.schema import NewsArticle, Reporter, SourcePortal, ScrapingTask, PublicationLog
    Base.metadata.drop_all(bind=engine)


def get_session():
    """Retorna uma sessão nova (para uso fora do FastAPI)."""
    return SessionLocal()
