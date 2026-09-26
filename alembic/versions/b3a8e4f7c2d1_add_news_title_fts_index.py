"""Add a PostgreSQL full-text index for related-source lookup."""

from alembic import op
from sqlalchemy import text


revision = "b3a8e4f7c2d1"
down_revision = "a7c3d9e1f204"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(text("CREATE INDEX IF NOT EXISTS ix_news_articles_title_fts ON news_articles USING GIN (to_tsvector('portuguese', title))"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(text("DROP INDEX IF EXISTS ix_news_articles_title_fts"))
