"""Checks de agentes e repórteres do auditor."""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AgentReporterAuditMixin:
    agents_monitored: list[str]
    reporters_monitored: list[str]

    def _audit_agents(self) -> Dict:
        """Audita cada agente com dados reais (DB + Celery)."""
        agents_status = {}
        try:
            from app.database import get_session
            from app.schema import NewsArticle, ScrapingTask

            db = get_session()
            try:
                today = datetime.now(timezone.utc).date()
                for agent_name in self.agents_monitored:
                    # Mapeia agente para tabela/fonte real
                    if agent_name == "scanner":
                        q = db.query(ScrapingTask).order_by(ScrapingTask.created_at.desc()).first()
                        last = q.created_at.isoformat() if q and q.created_at else None
                        cnt = (
                            db.query(ScrapingTask)
                            .filter(ScrapingTask.created_at >= datetime.combine(today, datetime.min.time()))
                            .count()
                            if q
                            else 0
                        )
                        status = "healthy" if q else "warning"
                        agents_status[agent_name] = {
                            "name": agent_name,
                            "status": status,
                            "last_activity": last,
                            "tasks_completed_today": cnt,
                            "errors_today": 0,
                            "avg_response_time_ms": None,
                            "source": "ScrapingTask",
                        }
                    elif agent_name in ("publisher", "rewriter", "classifier", "filter", "miner"):
                        # Usa NewsArticle como proxy de atividade do pipeline
                        last_art = db.query(NewsArticle).order_by(NewsArticle.updated_at.desc()).first()
                        last = last_art.updated_at.isoformat() if last_art and last_art.updated_at else None
                        cnt = (
                            db.query(NewsArticle)
                            .filter(NewsArticle.updated_at >= datetime.combine(today, datetime.min.time()))
                            .count()
                        )
                        status = "healthy" if cnt > 0 else "warning"
                        agents_status[agent_name] = {
                            "name": agent_name,
                            "status": status,
                            "last_activity": last,
                            "tasks_completed_today": cnt,
                            "errors_today": 0,
                            "avg_response_time_ms": None,
                            "source": "NewsArticle",
                        }
                    else:
                        agents_status[agent_name] = {
                            "name": agent_name,
                            "status": "warning",
                            "last_activity": None,
                            "tasks_completed_today": 0,
                            "errors_today": 0,
                            "avg_response_time_ms": None,
                            "source": "unknown",
                            "note": "not_implemented: no table for agent",
                        }
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[HORUS] _audit_agents fallback not_implemented: {e}")
            for agent_name in self.agents_monitored:
                agents_status[agent_name] = {
                    "name": agent_name,
                    "status": "not_implemented",
                    "reason": str(e)[:200],
                    "last_activity": None,
                }
        return agents_status

    def _audit_reporters(self) -> Dict:
        """Audita cada repórter com dados reais do DB."""
        reporters_status = {}
        try:
            from app.database import get_session
            from app.schema import NewsArticle, Reporter

            db = get_session()
            try:
                today = datetime.now(timezone.utc).date()
                for reporter_slug in self.reporters_monitored:
                    rep = db.query(Reporter).filter(Reporter.slug == reporter_slug).first()
                    if not rep:
                        reporters_status[reporter_slug] = {
                            "name": reporter_slug,
                            "status": "not_found",
                            "articles_today": 0,
                            "articles_total": 0,
                            "note": "reporter not in DB",
                        }
                        continue
                    total = db.query(NewsArticle).filter(NewsArticle.reporter_id == rep.id).count()
                    today_cnt = (
                        db.query(NewsArticle)
                        .filter(
                            NewsArticle.reporter_id == rep.id,
                            NewsArticle.published_at >= datetime.combine(today, datetime.min.time()),
                        )
                        .count()
                        if rep
                        else 0
                    )
                    # avg quality: tenta usar PublicationLog ou calcula via filter
                    reporters_status[reporter_slug] = {
                        "name": reporter_slug,
                        "status": "healthy" if total > 0 else "warning",
                        "articles_today": today_cnt,
                        "articles_total": total,
                        "avg_quality_score": None,
                        "consistency_score": None,
                        "personality_evolution": rep.personality_stage
                        if hasattr(rep, "personality_stage")
                        else "unknown",
                        "public_engagement": None,
                        "source": "DB Reporter+NewsArticle",
                    }
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[HORUS] _audit_reporters fallback: {e}")
            for reporter_slug in self.reporters_monitored:
                reporters_status[reporter_slug] = {
                    "name": reporter_slug,
                    "status": "not_implemented",
                    "reason": str(e)[:200],
                }
        return reporters_status

    def _audit_content_quality(self) -> Dict:
        """Audita qualidade com dados reais (DB + similarity)."""
        try:
            from app.database import get_session
            from app.filter import ContentFilter
            from app.schema import NewsArticle

            db = get_session()
            try:
                today = datetime.now(timezone.utc).date()
                arts = (
                    db.query(NewsArticle)
                    .filter(NewsArticle.published_at >= datetime.combine(today, datetime.min.time()))
                    .all()
                )
                if not arts:
                    return {
                        "status": "not_implemented",
                        "reason": "no articles today",
                        "articles_audited_today": 0,
                        "quality_score_avg": None,
                        "plagiarism_detected": None,
                        "issues_found": ["no data"],
                    }
                filt = ContentFilter()
                scores = [
                    filt.calculate_quality_score(
                        {
                            "title": a.title,
                            "summary": a.summary,
                            "content": a.content,
                            "source": a.sources,
                            "url": a.sources[0].get("url") if a.sources and isinstance(a.sources[0], dict) else "",
                            "image_url": a.image_url,
                            "published_at": a.published_at,
                        }
                    )
                    for a in arts
                ]
                avg = round(sum(scores) / len(scores), 2) if scores else None
                # plagiarism: verifica overlap entre últimos 20
                plag: Optional[int] = 0
                try:
                    from difflib import SequenceMatcher

                    recent = db.query(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(20).all()
                    for i in range(len(recent)):
                        for j in range(i + 1, len(recent)):
                            if recent[i].content and recent[j].content:
                                r = SequenceMatcher(None, recent[i].content[:2000], recent[j].content[:2000]).ratio()
                                if r > 0.85:
                                    plag = (plag or 0) + 1
                except Exception:
                    plag = None
                # attribution
                with_source = sum(1 for a in arts if a.sources)
                attr_ratio = round(with_source / len(arts), 3) if arts else 0
                return {
                    "articles_audited_today": len(arts),
                    "quality_score_avg": avg,
                    "plagiarism_detected": plag,
                    "factual_errors": None,
                    "tone_consistency": None,
                    "attribution_present": attr_ratio,
                    "translation_quality": None,
                    "issues_found": [],
                    "source": "DB+ContentFilter",
                }
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[HORUS] _audit_content_quality not_implemented: {e}")
            return {
                "status": "not_implemented",
                "reason": str(e)[:300],
                "articles_audited_today": 0,
                "quality_score_avg": None,
                "plagiarism_detected": None,
                "issues_found": [str(e)[:200]],
            }
