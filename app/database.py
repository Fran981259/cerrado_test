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
from sqlalchemy.pool import QueuePool, NullPool

# URL do banco
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///data/portal_cerrado.db"
)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"


def _connect_postgres(url: str):
    # Se URL é sqlite, não usa QueuePool
    if url.strip().startswith("sqlite"):
        return create_engine(
            url,
            poolclass=NullPool,
            connect_args={"check_same_thread": False},
            echo=False,
        )
    retries = int(os.getenv("DATABASE_CONNECT_RETRIES", "10"))
    delay = float(os.getenv("DATABASE_CONNECT_RETRY_DELAY", "1"))
    last_error = None
    engine = create_engine(
        url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_timeout=30,
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
            "Banco indisponivel em producao; sem fallback (%s)", type(e).__name__
        )
        raise
    # Fallback local (desenvolvimento sem Postgres): usa SQLite.
    import sqlite3
    _sqlite_file = os.path.join(os.path.dirname(__file__), "..", "data", "portal_cerrado.db")
    _sqlite_file = os.path.abspath(_sqlite_file)
    os.makedirs(os.path.dirname(_sqlite_file), exist_ok=True)
    engine = create_engine(
        f"sqlite:///{_sqlite_file}",
        poolclass=NullPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    _using_sqlite = True
    import logging
    logging.getLogger(__name__).warning(
        "Banco indisponivel; usando SQLite local (ENVIRONMENT=%s)", ENVIRONMENT
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para models
Base = declarative_base()


def init_db():
    """Inicializa o banco de dados (cria tabelas)."""
    from app.schema import NewsArticle, Reporter, SourcePortal, ScrapingTask, PublicationLog
    Base.metadata.create_all(bind=engine)


def get_session():
    """Retorna uma sessão nova (para uso fora do FastAPI)."""
    return SessionLocal()
