"""
Conexão com Banco de Dados — Portal Cerrado
PostgreSQL via SQLAlchemy
"""

import os
import time
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

# URL do banco
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://portal_user:portal_pass@localhost:5432/portal_cerrado"
)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"


def _connect_postgres(url: str):
    retries = int(os.getenv("DATABASE_CONNECT_RETRIES", "3"))
    delay = float(os.getenv("DATABASE_CONNECT_RETRY_DELAY", "0.5"))
    last_error = None
    engine = create_engine(
        url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )

    for attempt in range(retries):
        try:
            with engine.connect() as _c:
                pass
            return engine
        except Exception as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(delay)

    if last_error:
        raise last_error
    return engine

try:
    # Tenta PostgreSQL (produção). Em caso de falha transitória, repete antes de cair.
    engine = _connect_postgres(DATABASE_URL)
    _using_sqlite = False
except Exception as e:
    if IS_PRODUCTION:
        import logging
        logging.getLogger(__name__).error(
            f"PostgreSQL indisponível em produção ({DATABASE_URL}): {e} — falhando (sem fallback SQLite)"
        )
        raise
    # Fallback local (desenvolvimento sem Postgres): usa SQLite.
    import sqlite3
    _sqlite_file = os.path.join(os.path.dirname(__file__), "..", "data", "portal_cerrado.db")
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
        f"PostgreSQL indisponível ({DATABASE_URL}); usando SQLite em {_sqlite_file} (ENVIRONMENT={ENVIRONMENT})"
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
