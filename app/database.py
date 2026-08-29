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

# Engine
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
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
