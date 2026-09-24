"""Add indexes for foreign keys and frequent editorial filters.

Revision ID: a7c3d9e1f204
Revises: 944b989187cf
"""

from alembic import op


revision = "a7c3d9e1f204"
down_revision = "944b989187cf"
branch_labels = None
depends_on = None


INDEXES = (
    ("ix_news_articles_reporter_id", "news_articles", ["reporter_id"]),
    ("ix_news_articles_visibility", "news_articles", ["visibility"]),
    ("ix_news_articles_updated_at", "news_articles", ["updated_at"]),
    ("ix_scraping_tasks_portal_id", "scraping_tasks", ["portal_id"]),
    ("ix_scraping_tasks_created_at", "scraping_tasks", ["created_at"]),
    ("ix_publication_logs_article_id", "publication_logs", ["article_id"]),
    ("ix_publication_logs_reporter_id", "publication_logs", ["reporter_id"]),
    ("ix_publication_logs_created_at", "publication_logs", ["created_at"]),
    ("ix_article_identities_article_id", "article_identities", ["article_id"]),
)


def upgrade() -> None:
    for name, table, columns in INDEXES:
        op.create_index(name, table, columns, unique=False)


def downgrade() -> None:
    for name, table, _columns in reversed(INDEXES):
        op.drop_index(name, table_name=table)
