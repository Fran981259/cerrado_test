# 🗺️ Portal Cerrado — Project Map

## Stack
- Frontend: Next.js 16, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Celery
- Database and queue: PostgreSQL/SQLite fallback, Redis
- Infra: Docker Compose, Caddy, GitHub Actions

## Folder Structure
- app/ → API, editorial pipeline, persistence and background tasks
- config/ → source, scheduler and reporter policies
- frontend/src/app/ → public Next.js routes
- frontend/src/components/ → reusable public UI components
- frontend/src/lib/ → API client and shared frontend utilities
- tests/ → unit and pipeline tests
- scripts/ → operational and maintenance commands

## Routes / Pages
- GET / → public home
- GET /categoria/[slug] → public category feed
- GET /noticia/[slug] → public article
- GET /api/news → paginated local public feed
- GET /api/editorial/review → protected queue for local review and published articles
- GET /api/operations/status → publication freshness signal
- GET /admin/editorial → protected editorial review workspace

## Key Files
- app/main.py → FastAPI application and HTTP endpoints
- app/publisher.py → publication and public feed rules
- app/local_news_policy.py → local editorial source gate
- frontend/src/lib/api.ts → frontend API client and home ranking
- frontend/src/lib/editorialApi.ts → protected editorial queue client
- frontend/src/components/admin/ → editorial review dashboard UI
- config/scheduler.yaml → local publication policy

## Database Tables
- news_articles · reporters · publication_logs · scraping_tasks · editorial_trend_signals

## Last updated: 2026-09-21
