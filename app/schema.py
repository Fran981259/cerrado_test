# Schema do Banco de Dados — Atualiza Brasil
# Define as tabelas e modelos para o sistema de notícias.

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class NewsArticle(Base):
    """Modelo para uma matéria de notícias publicada."""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)

    # Metadados
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    author = Column(String(200), nullable=True)
    image_url = Column(String(500), nullable=True)

    # Associação com repórter
    reporter_id = Column(Integer, ForeignKey("reporters.id"), nullable=False)

    # Fontes e atribuições
    sources = Column(JSON, nullable=True)
    original_text = Column(Text, nullable=True)
    compliance_hash = Column(String(64), nullable=True)

    # Status e publicação
    status = Column(String(20), default="draft")
    published_at = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    visibility = Column(String(20), default="public")

    # Categorias
    category = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True)

    # Classificação
    importance_score = Column(Integer, nullable=True)
    engagement_score = Column(Integer, nullable=True)
    final_score = Column(Integer, nullable=True)
    priority_tier = Column(String(20), nullable=True)
    is_curiosity = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamento
    reporter = relationship("Reporter", back_populates="articles")


class Reporter(Base):
    """Modelo para um repórter digital."""
    __tablename__ = "reporters"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True)
    display_name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=True)

    role = Column(String(50), nullable=False)
    specialties = Column(JSON, nullable=True)

    voice_profile = Column(JSON, nullable=True)
    prompt_system = Column(JSON, nullable=True)
    attribution = Column(String(200), nullable=True)

    # Evolução
    articles_published = Column(Integer, default=0)
    experience_points = Column(Integer, default=0)
    personality_stage = Column(String(20), default="newborn")
    birth_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    articles = relationship("NewsArticle", back_populates="reporter", cascade="all, delete-orphan")


class SourcePortal(Base):
    """Modelo para um portal de notícias de origem."""
    __tablename__ = "source_portals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    type = Column(String(50), default="general")

    enabled = Column(Boolean, default=True)
    rate_limit_seconds = Column(Integer, default=5)
    last_checked = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

    robots_txt_url = Column(String(500), nullable=True)
    robots_txt_last_fetched = Column(DateTime, nullable=True)
    robots_txt_allowed = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ScrapingTask(Base):
    """Modelo para uma tarefa de scraping realizada."""
    __tablename__ = "scraping_tasks"

    id = Column(Integer, primary_key=True, index=True)
    portal_id = Column(Integer, ForeignKey("source_portals.id"), nullable=False)
    task_type = Column(String(50), nullable=False)

    status = Column(String(20), default="pending")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    result_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PublicationLog(Base):
    """Registro de auditoria de publicações."""
    __tablename__ = "publication_logs"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False)
    action = Column(String(50), nullable=False)
    reporter_id = Column(Integer, ForeignKey("reporters.id"), nullable=True)
    details = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
