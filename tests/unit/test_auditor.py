"""Tests dedicados p/ app/auditor.py (HorusAuditor) — cobertura P1-P4.

Usa SQLite temporário (nunca o DATABASE_URL real). Padrão de fixture:
importar app.schema ANTES do create_all, senão nenhuma tabela é criada.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.auditor import HorusAuditor


@pytest.fixture()
def tdb(monkeypatch, tmp_path):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    import app.schema  # noqa: F401 — registra tabelas antes do create_all
    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path}/horus_test.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr("app.database.get_session", lambda: Session())
    return Session


def _reporter(Session, slug="enzo.bianchi", stage="established"):
    from app.schema import Reporter
    db = Session()
    rep = Reporter(slug=slug, display_name=slug.replace(".", " ").title(),
                   role="technology", personality_stage=stage,
                   email=f"{slug}@test.com")
    db.add(rep)
    db.commit()
    db.refresh(rep)
    rid = rep.id
    db.close()
    return rid


def _article(Session, reporter_id, title="Titulo de teste para auditoria",
             content="Conteudo original e distinto para teste de auditoria.",
             original="Texto fonte completamente diferente sem relacao.",
             published_at=None, status="published"):
    from app.schema import NewsArticle
    db = Session()
    art = NewsArticle(title=title, slug=f"slug-{title[:10]}-{reporter_id}-{abs(hash(title)) % 99999}",
                      summary="Resumo", content=content, reporter_id=reporter_id,
                      sources=[{"url": "https://ex.com/a", "name": "Ex"}],
                      original_text=original, status=status,
                      published_at=published_at or datetime.utcnow(),
                      category="technology", tags=["technology"])
    db.add(art)
    db.commit()
    aid = art.id
    db.close()
    return aid


# ---------------- _audit_agents ----------------

def test_audit_agents_real_counts(tdb):
    from app.schema import SourcePortal, ScrapingTask
    db = tdb()
    portal = SourcePortal(url="https://ex.com", name="ex")
    db.add(portal)
    db.commit()
    db.add(ScrapingTask(portal_id=portal.id, task_type="scan", status="ok"))
    db.commit()
    db.close()
    rid = _reporter(tdb)
    _article(tdb, rid)
    res = HorusAuditor()._audit_agents()
    assert res["scanner"]["status"] == "healthy"
    assert res["scanner"]["tasks_completed_today"] >= 1
    assert res["publisher"]["tasks_completed_today"] >= 1


def test_audit_agents_db_failure(tdb, monkeypatch):
    import app.database
    monkeypatch.setattr(app.database, "get_session", _boom)
    res = HorusAuditor()._audit_agents()
    assert all(v["status"] == "not_implemented" for v in res.values())


def _boom():
    raise RuntimeError("db down")


# ---------------- _audit_reporters ----------------

def test_audit_reporters_real_counts(tdb):
    rid = _reporter(tdb, slug="enzo.bianchi")
    _article(tdb, rid, title="Materia um de auditoria real")
    _article(tdb, rid, title="Materia dois de auditoria real")
    res = HorusAuditor()._audit_reporters()
    assert res["enzo.bianchi"]["articles_total"] == 2
    assert res["enzo.bianchi"]["status"] == "healthy"


def test_audit_reporters_not_found(tdb):
    res = HorusAuditor()._audit_reporters()
    assert res["enzo.bianchi"]["status"] == "not_found"


# ---------------- _audit_content_quality ----------------

def test_audit_content_quality_no_articles_today(tdb):
    res = HorusAuditor()._audit_content_quality()
    assert res["status"] == "not_implemented"
    assert res["articles_audited_today"] == 0


def test_audit_content_quality_average(tdb):
    rid = _reporter(tdb)
    _article(tdb, rid, title="Qualidade alta um")
    _article(tdb, rid, title="Qualidade alta dois")
    from app.filter import ContentFilter
    with patch.object(ContentFilter, "calculate_quality_score", return_value=8.0):
        res = HorusAuditor()._audit_content_quality()
    assert res["articles_audited_today"] == 2
    assert res["quality_score_avg"] == 8.0


# ---------------- _audit_compliance ----------------

def test_audit_compliance_flags_violation(tdb):
    rid = _reporter(tdb)
    same = "Texto identico repetido para teste de similaridade alta proposital."
    _article(tdb, rid, title="Copia quase literal", content=same, original=same)
    res = HorusAuditor()._audit_compliance()
    assert res["legal_compliance"] is False
    assert any("similarity" in i for i in res["issues"])


def test_audit_compliance_clean(tdb):
    rid = _reporter(tdb)
    _article(tdb, rid, title="Materia limpa e original",
             content=" ".join(["Jornalismo apurado com dados verificados"] * 20),
             original=" ".join(["Fonte bruta totalmente distinta"] * 20))
    res = HorusAuditor()._audit_compliance()
    assert res["legal_compliance"] is True


def test_audit_compliance_no_published(tdb):
    res = HorusAuditor()._audit_compliance()
    assert res["status"] == "not_implemented"


# ---------------- consolidate + overall ----------------

def _base_report():
    blank = {}
    return {"agents": blank, "reporters": blank, "content_quality": blank,
            "compliance": blank, "performance": blank, "alerts": []}


def test_consolidate_and_critical():
    h = HorusAuditor()
    rep = _base_report()
    rep["agents"] = {"scanner": {"status": "offline"}}
    rep["content_quality"] = {"quality_score_avg": 6.5}
    rep["performance"] = {"target_met": False, "daily_produced": 1, "daily_target": 50}
    alerts = h._consolidate_alerts(rep)
    kinds = {a["type"] for a in alerts}
    assert {"agent_offline", "quality_low", "target_not_met"} <= kinds
    rep["alerts"] = alerts
    assert h._determine_overall_status(rep) == "critical"


def test_overall_warning_and_healthy():
    h = HorusAuditor()
    warn = _base_report()
    warn["alerts"] = [{"severity": 3, "type": "x"}]
    assert h._determine_overall_status(warn) == "warning"
    ni = _base_report()
    ni["content_quality"] = {"status": "not_implemented"}
    assert h._determine_overall_status(ni) == "warning"  # nunca healthy
    ok = _base_report()
    assert h._determine_overall_status(ok) == "healthy"


# ---------------- watch_reporter_evolution ----------------

def test_watch_evolution_real_data(tdb):
    rid = _reporter(tdb, slug="maya.santos", stage="established")
    _article(tdb, rid, title="Saude um")
    _article(tdb, rid, title="Saude dois")
    _article(tdb, rid, title="Saude tres")
    res = HorusAuditor().watch_reporter_evolution("maya.santos")
    assert res["articles_published"] == 3
    assert res["evolution_stage"] == "established"
    assert isinstance(res["months_active"], int)
    assert res["status"] == "not_implemented"
    assert res["style_consistency"] is None


def test_watch_evolution_not_found(tdb):
    res = HorusAuditor().watch_reporter_evolution("fantasma.zero")
    assert res["status"] == "not_found"
