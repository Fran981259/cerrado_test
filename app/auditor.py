"""
Agente Auditor HORUS — Portal Cerrado
======================================
O olho que tudo vê. Monitora todos os agentes e repórteres
para garantir qualidade, consistência e evolução.
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from app.auditor_agent_checks import AgentReporterAuditMixin
from app.auditor_compliance_checks import ComplianceAuditMixin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportSeverity(Enum):
    """Níveis de severidade dos relatórios."""

    CRITICAL = 5  # Ação imediata necessária
    HIGH = 4  # Problema sério
    MEDIUM = 3  # Atenção necessária
    LOW = 2  # Informativo
    INFO = 1  # Apenas notificação


class AgentStatus(Enum):
    """Status dos agentes monitorados."""

    HEALTHY = "healthy"  # Tudo funcionando
    WARNING = "warning"  # Atenção necessária
    CRITICAL = "critical"  # Problema sério
    OFFLINE = "offline"  # Não está respondendo
    EVOLVING = "evolving"  # Em fase de evolução


class HorusAuditor(AgentReporterAuditMixin, ComplianceAuditMixin):
    """
    O olho que tudo vê.

    HORUS (High-level Observer for Reporter Unification & Supervision)
    Monitora:
    - Todos os agentes (scanner, miner, classifier, rewriter, publisher)
    - Todos os 9 repórteres digitais
    - Qualidade de conteúdo
    - Compliance legal
    - Performance e saúde
    - Evolução de personalidade
    """

    def __init__(self):
        self.agents_monitored = ["scanner", "miner", "classifier", "rewriter", "publisher", "filter"]
        self.reporters_monitored = [
            "enzo.bianchi",
            "marcus.teixeira",
            "rafael.dumas",
            "luciana.freitas",
            "maya.santos",
            "lucas.nakamura",
            "bia.fernandes",
            "leon.vaz",
            "camila.rocha",
        ]
        self.audit_log = []

    def audit_all(self) -> Dict:
        """
        Executa auditoria completa do sistema.
        Retorna relatório consolidado.
        """
        logger.info("👁️ HORUS iniciando auditoria completa")

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "auditor": "HORUS",
            "agents": self._audit_agents(),
            "reporters": self._audit_reporters(),
            "content_quality": self._audit_content_quality(),
            "compliance": self._audit_compliance(),
            "performance": self._audit_performance(),
            "categories": self._audit_categories(),
            "alerts": [],
            "overall_status": "healthy",
        }

        # Consolida alertas
        report["alerts"] = self._consolidate_alerts(report)

        # Determina status geral
        report["overall_status"] = self._determine_overall_status(report)

        # Log de auditoria
        self.audit_log.append(report)

        logger.info(f"👁️ HORUS: Status geral = {report['overall_status']}")
        return report

    def _consolidate_alerts(self, report: Dict) -> List[Dict]:
        """Consolida alertas de todos os módulos auditados."""
        alerts = []

        # Verifica agentes offline
        for agent_name, status in report["agents"].items():
            if status["status"] == AgentStatus.OFFLINE.value:
                alerts.append(
                    {
                        "severity": ReportSeverity.CRITICAL.value,
                        "type": "agent_offline",
                        "message": f"Agente {agent_name} está offline",
                        "agent": agent_name,
                        "action": "reiniciar_agente",
                    }
                )

        # Verifica qualidade baixa
        cq = report.get("content_quality", {})
        if cq.get("status") != "not_implemented":
            quality_score = cq.get("quality_score_avg")
            if isinstance(quality_score, (int, float)) and quality_score < 7.0:
                alerts.append(
                    {
                        "severity": ReportSeverity.HIGH.value,
                        "type": "quality_low",
                        "message": f"Score de qualidade baixo: {quality_score}",
                        "action": "revisar_prompts",
                    }
                )

        # Verifica meta diária
        perf = report.get("performance", {})
        if perf.get("status") != "not_implemented" and "target_met" in perf:
            if not perf["target_met"]:
                alerts.append(
                    {
                        "severity": ReportSeverity.MEDIUM.value,
                        "type": "target_not_met",
                        "message": f"Meta diária não atingida: {perf.get('daily_produced')}/{perf.get('daily_target')}",
                        "action": "aumentar_coleta",
                    }
                )

        # Verifica categorias
        cats = report.get("categories", {})
        if cats.get("status") not in ("not_implemented", "no_data", "error"):
            if cats.get("invalid_count", 0) > 0:
                alerts.append(
                    {
                        "severity": ReportSeverity.HIGH.value,
                        "type": "invalid_categories",
                        "message": f"{cats['invalid_count']} artigos com categorias inválidas",
                        "action": "reclassificar_artigos",
                    }
                )
            if cats.get("general_ratio_warning"):
                alerts.append(
                    {
                        "severity": ReportSeverity.MEDIUM.value,
                        "type": "general_overflow",
                        "message": f"Categoria 'general' com {cats['general_ratio']:.0%} dos artigos (>30%)",
                        "action": "refinar_heuristica_classificacao",
                    }
                )

        return alerts

    def _determine_overall_status(self, report: Dict) -> str:
        """Determina status geral baseado nos alertas e not_implemented."""
        # Se qualquer seção está not_implemented, não pode ser healthy
        for key in ("agents", "content_quality", "compliance", "performance", "reporters"):
            sec = report.get(key)
            if isinstance(sec, dict) and sec.get("status") == "not_implemented":
                return AgentStatus.WARNING.value
        critical_count = sum(1 for a in report["alerts"] if a["severity"] >= 4)
        high_count = sum(1 for a in report["alerts"] if a["severity"] >= 3)

        if critical_count > 0:
            return AgentStatus.CRITICAL.value
        elif high_count > 0:
            return AgentStatus.WARNING.value
        else:
            return AgentStatus.HEALTHY.value

    def watch_reporter_evolution(self, reporter_slug: str) -> Dict:
        """
        Acompanha a evolução de um repórter específico com dados reais.
        Segue o mesmo padrão de _audit_reporters(): contagens do DB;
        métricas sem fonte de dados retornam None + not_implemented.
        """
        try:
            from app.database import get_session
            from app.schema import NewsArticle, Reporter

            db = get_session()
            try:
                rep = db.query(Reporter).filter(Reporter.slug == reporter_slug).first()
                if not rep:
                    return {
                        "reporter": reporter_slug,
                        "status": "not_found",
                        "articles_published": 0,
                        "note": "reporter not in DB",
                    }
                total = db.query(NewsArticle).filter(NewsArticle.reporter_id == rep.id).count()
                first = (
                    db.query(NewsArticle.published_at)
                    .filter(NewsArticle.reporter_id == rep.id, NewsArticle.published_at.isnot(None))
                    .order_by(NewsArticle.published_at.asc())
                    .first()
                )
                base_date = (first[0] if first and first[0] else None) or rep.birth_date or rep.created_at
                now = datetime.now(timezone.utc)
                if base_date:
                    months_active = max(0, (now.year - base_date.year) * 12 + (now.month - base_date.month))
                else:
                    months_active = 0
                return {
                    "reporter": reporter_slug,
                    "status": "not_implemented",
                    "reason": "no engagement/analytics table for style/audience metrics",
                    "articles_published": total,
                    "months_active": months_active,
                    "evolution_stage": rep.personality_stage if hasattr(rep, "personality_stage") else "unknown",
                    "style_consistency": None,
                    "voice_distinctiveness": None,
                    "audience_loyalty": None,
                    "engagement_growth": None,
                    "next_milestone": None,
                    "source": "DB Reporter+NewsArticle",
                }
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[HORUS] watch_reporter_evolution fallback: {e}")
            return {"reporter": reporter_slug, "status": "not_implemented", "reason": str(e)[:200]}
